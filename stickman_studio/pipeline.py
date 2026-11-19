"""End-to-end pipeline: script -> offline TTS -> timing sync -> audio mix ->
frame rendering -> MP4 (H.264 + AAC) via imageio-ffmpeg."""
from __future__ import annotations

import math
import os
import tempfile
import time
from dataclasses import dataclass

import numpy as np

from .audio import SR, PROP_SFX, CAMERA_SFX, mix_tracks, music_bed, write_wav
from .config import RenderSettings, MAX_DURATION
from .renderer import SceneRenderer, ShotTiming, uniform_timeline, mic_drop_hit_time
from .rig import ACTION_SFX
from .script_gen import validate_script
from .script_model import Script
from .tts import synthesize_all

LEAD = 0.12      # silence before speech in each shot
TAIL = 0.30      # hold after speech (reaction beat)
MIN_SHOT = 1.5


@dataclass
class BuildResult:
    path: str
    duration: float
    frames: int
    fps: int
    size: tuple
    tts_engine: str
    shot_durations: list
    render_seconds: float


def _speech_total(clips):
    return sum(c.duration for c in clips) + len(clips) * (LEAD + TAIL)


def _shot_durations(script, clips):
    durs = []
    for sh, c in zip(script.shots, clips):
        d = LEAD + c.duration + TAIL
        if sh.kind == "cta":
            d += 1.0      # let the subscribe/like animation land
        if sh.action == "mic_drop":
            d = max(d, 2.2)
        if sh.action == "fall_down_dramatic":
            d = max(d, 1.9)
        durs.append(max(MIN_SHOT, d))
    return durs


def _trim_slack(durs, clips, excess):
    """Shorten the non-speech part of shots proportionally to remove `excess` seconds."""
    slack = [max(0.0, d - (LEAD + c.duration + 0.08)) for d, c in zip(durs, clips)]
    tot = sum(slack)
    if tot <= 0:
        return durs
    k = min(1.0, excess / tot)
    return [d - s_ * k for d, s_ in zip(durs, slack)]


def synthesize_timeline(script: Script, st: RenderSettings, log=None):
    texts = [s.text for s in script.shots]
    rate = st.voice_rate
    clips, engine = synthesize_all(texts, st.tts_engine, rate, st.voice_id, st.language,
                                   st.voice_pitch, seed=script.seed)
    target = min(float(st.target_duration or script.target_duration), MAX_DURATION - 0.1)
    if st.fit_to_target:
        total = _speech_total(clips)
        ratio = total / max(target, 1.0)
        # too long -> speak faster; too short -> slower (but never sluggish)
        if ratio > 1.06 or ratio < 0.85 or total > MAX_DURATION:
            new_rate = rate * max(0.8, min(1.4, ratio if ratio > 1 else max(ratio, 0.88)))
            if total > MAX_DURATION:
                new_rate = max(new_rate, rate * total / (MAX_DURATION - 1))
            if log:
                log(f"Ajustez viteza vocii {rate:.2f} -> {new_rate:.2f} pentru durata țintă")
            rate = new_rate
            clips, engine = synthesize_all(texts, st.tts_engine, new_rate, st.voice_id, st.language,
                                           st.voice_pitch, seed=script.seed)
    durs = _shot_durations(script, clips)
    for _ in range(2):  # hard cap: never exceed MAX_DURATION
        if sum(durs) <= MAX_DURATION:
            break
        durs = _trim_slack(durs, clips, sum(durs) - MAX_DURATION + 0.15)
        if sum(durs) > MAX_DURATION:
            rate = rate * (sum(durs) / MAX_DURATION) * 1.03
            if log:
                log(f"Accelerez vocea la {rate:.2f} pentru a rămâne sub {MAX_DURATION}s")
            clips, engine = synthesize_all(texts, st.tts_engine, rate, st.voice_id, st.language,
                                           st.voice_pitch, seed=script.seed)
            durs = _shot_durations(script, clips)
    total = sum(durs)
    if st.fit_to_target and total < target:
        extra = min(target - total, 0.9 * len(durs))
        per = extra / len(durs)
        durs = [d + per for d in durs]
    timeline, t0 = [], 0.0
    for sh, c, d in zip(script.shots, clips, durs):
        env = np.concatenate([np.zeros(int(LEAD * 100), dtype=np.float32), c.env])
        wt = [(s + LEAD, e + LEAD) for s, e in c.word_times]
        timeline.append(ShotTiming(t0, d, list(c.words), wt, env, 100.0, LEAD + c.duration))
        t0 += d
    return timeline, clips, engine


def build_audio(script: Script, timeline, clips, st: RenderSettings, path: str):
    total = timeline[-1].start + timeline[-1].duration
    voice = [(tm.start + LEAD, c.samples) for tm, c in zip(timeline, clips)]
    sfx = []
    if st.sfx:
        for i, (sh, tm) in enumerate(zip(script.shots, timeline)):
            n = 0
            name = ACTION_SFX.get(sh.action)
            if name:
                off = 0.0
                if sh.action == "mic_drop":
                    off = mic_drop_hit_time(tm.duration)
                elif sh.action == "fall_down_dramatic":
                    off = 0.8
                sfx.append((tm.start + off, name, 0.8))
                n += 1
            cam = CAMERA_SFX.get(sh.camera)
            if cam and n < 2:
                sfx.append((tm.start, cam, 0.6))
                n += 1
            for j, p in enumerate(sh.props):
                if n >= 2:
                    break
                if p in PROP_SFX:
                    sfx.append((tm.start + 0.12 * j + 0.05, PROP_SFX[p], 0.6))
                    n += 1
            if "subscribe" in sh.props:
                sfx.append((tm.start + 1.1, "pop", 0.9))
                sfx.append((tm.start + 1.25, "ding", 0.7))
    music = music_bed(total, st.energy, seed=script.seed) if st.music else None
    mix = mix_tracks(total, voice, sfx, music, st.music_volume)
    stereo = np.stack([mix, mix], axis=1)
    write_wav(path, stereo, SR)
    return total


def build_video(script: Script, settings: RenderSettings, out_path: str, progress=None,
                workdir: str | None = None, log=None) -> BuildResult:
    """progress(fraction: float, message: str) is called during rendering."""
    import imageio_ffmpeg

    t_start = time.time()
    script = validate_script(script)
    settings.language = script.language or settings.language
    wd = workdir or tempfile.mkdtemp(prefix="stickman_build_")
    os.makedirs(wd, exist_ok=True)
    say = log or (lambda m: None)
    report = progress or (lambda f, m: None)

    report(0.0, "Generez vocea offline (TTS)...")
    timeline, clips, engine = synthesize_timeline(script, settings, say)
    say(f"Motor TTS: {engine}")
    wav_path = os.path.join(wd, "mix.wav")
    report(0.03, "Mixez audio (voce + muzică + SFX)...")
    total = build_audio(script, timeline, clips, settings, wav_path)

    renderer = SceneRenderer(script, timeline, settings)
    fps = int(settings.fps)
    n_frames = int(math.ceil(total * fps))
    W, H = settings.size
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    out_params = ["-preset", settings.preset, "-crf", str(settings.crf), "-movflags", "+faststart",
                  "-b:a", "192k", "-shortest", "-profile:v", "high"]
    writer = imageio_ffmpeg.write_frames(
        out_path, (W, H), fps=fps, codec="libx264", pix_fmt_in="rgb24", pix_fmt_out="yuv420p",
        quality=None, macro_block_size=2, ffmpeg_log_level="error", output_params=out_params,
        audio_path=wav_path, audio_codec="aac")
    writer.send(None)
    n_shots = len(timeline)
    last_shot = -1
    try:
        for f in range(n_frames):
            t = f / fps
            si = renderer.shot_index(t)
            img = renderer.render(t)
            writer.send(img.tobytes())
            if si != last_shot or f % max(1, fps // 2) == 0:
                last_shot = si
                report(0.05 + 0.93 * (f + 1) / n_frames,
                       f"Randare shot {si + 1}/{n_shots} — cadru {f + 1}/{n_frames}")
    finally:
        writer.close()
    report(1.0, "Gata!")
    return BuildResult(out_path, total, n_frames, fps, (W, H), engine,
                       [round(tm.duration, 2) for tm in timeline], time.time() - t_start)


def render_preview_frame(script: Script, settings: RenderSettings, shot_index: int = 0,
                         t_in_shot: float = 1.0):
    """Fast still preview (no TTS) for the storyboard editor."""
    script = validate_script(script)
    tl = uniform_timeline(script)
    r = SceneRenderer(script, tl, settings)
    shot_index = max(0, min(shot_index, len(tl) - 1))
    tm = tl[shot_index]
    return r.render(tm.start + min(t_in_shot, tm.duration - 0.05))


def verify_video(path: str) -> dict:
    """Validates an exported MP4 with MoviePy: duration, resolution, fps, audio presence."""
    from moviepy import VideoFileClip

    clip = VideoFileClip(path)
    try:
        info = {
            "duration": float(clip.duration),
            "size": tuple(clip.size),
            "fps": float(clip.fps),
            "has_audio": clip.audio is not None,
        }
        frame = clip.get_frame(min(1.0, clip.duration / 2))
        info["frame_std"] = float(frame.std())
        if clip.audio is not None:
            info["audio_peak"] = float(clip.audio.max_volume())
        return info
    finally:
        clip.close()
