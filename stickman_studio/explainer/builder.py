"""Generic builder for step-by-step explainers: narration-driven timing, animation
tracks, smooth camera, keyword captions, music/SFX mix and MP4 export."""
from __future__ import annotations

import bisect
import math
import os
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw

from ..audio import SR, mix_tracks, music_bed, write_wav
from ..easing import clamp, ease_out_back
from ..painter import font
from ..tts import synthesize_all
from .iso import IsoCam
from .timeline import Tracks

LEAD, TAIL = 0.06, 0.22


class StepTracks(Tracks):
    def __init__(self, starts, steps):
        super().__init__()
        self.starts, self.steps = starts, steps
        self.cut_time = 1e9

    def step_at(self, t):
        return max(0, bisect.bisect_right(self.starts, t) - 1)

    def peg_expr(self, t):
        return self.steps[self.step_at(t)].get("pegs", "neutral")


def build_explainer(steps, scene_cls, out_path, initial, draw_overlays=None, fps=30, size=(1080, 1920),
                    ss=2, voice_rate=1.25, music_volume=0.07, log=print, progress=None, preview_frames=None):
    t0 = time.time()
    texts = [s["text"] for s in steps]
    clips, engine = synthesize_all(texts, "auto", voice_rate, language="en", log=log)
    log(f"TTS: {engine}")
    durs = [max(s.get("min", 0.0), LEAD + c.duration + TAIL) for s, c in zip(steps, clips)]
    starts = list(np.cumsum([0.0] + durs[:-1]))
    total = float(sum(durs))
    tr = StepTracks(starts, steps)
    for k, v in initial.items():
        tr.set_initial(k, v)
    W, H = size
    base_zoom = W / 1080.0
    tr.set_initial("cam_f", steps[0]["cam"][0])
    tr.set_initial("cam_z", steps[0]["cam"][1] * base_zoom)
    for s0, d, st in zip(starts, durs, steps):
        tr.add("cam_f", s0, st["cam"][0], 0.9, "io")
        tr.add("cam_z", s0, st["cam"][1] * base_zoom, 0.9, "io")
        for name, off, val, td, ease in st.get("do", []):
            if off >= 90:
                off = max(0.0, d - (0.55 if name != "bubble" else 0.35))
            tr.add(name, s0 + off, val, td, ease)
            if name == "otis_cut":
                tr.cut_time = s0 + off
    # ---------------------------------------------------------- audio
    voice = [(s0 + LEAD, c.samples) for s0, c in zip(starts, clips)]
    sfx = [(s0 + off, name, 0.55) for s0, st in zip(starts, steps) for off, name in st.get("sfx", [])]
    sfx += [(s0, "whoosh", 0.25) for s0, st, prev in zip(starts[1:], steps[1:], steps[:-1])
            if st["cam"] != prev["cam"]]
    music = music_bed(total, 3, seed=7, style="lofi")
    mix = mix_tracks(total, voice, sfx, music, music_volume)
    wd = tempfile.mkdtemp(prefix="explainer_")
    wav = os.path.join(wd, "mix.wav")
    write_wav(wav, np.stack([mix, mix], axis=1))
    # ---------------------------------------------------------- render
    RW, RH = W * ss, H * ss
    scene = scene_cls(RW, RH)

    def render(t):
        i = tr.step_at(t)
        lt = t - starts[i]
        img = scene.bg.copy()
        f = tr.get("cam_f", t)
        z = tr.get("cam_z", t) * ss * (1.0 + 0.015 * math.sin(t * 0.35))
        cam = IsoCam(img, f, z, (RW / 2, RH * 0.57))
        scene.draw(img, cam, tr, t, i, lt)
        if draw_overlays:
            draw_overlays(img, tr, t, RW, RH)
        _caption(img, steps[i], lt, RW, RH)
        return img.reduce(ss) if ss > 1 else img

    if preview_frames is not None:
        return [render(min(total - 0.01, starts[i] + durs[i] * fr)) for i, fr in preview_frames], starts, durs

    import imageio_ffmpeg
    n = int(math.ceil(total * fps))
    w = imageio_ffmpeg.write_frames(out_path, (W, H), fps=fps, codec="libx264", quality=None,
                                    macro_block_size=2, ffmpeg_log_level="error", audio_path=wav,
                                    audio_codec="aac",
                                    output_params=["-preset", "veryfast", "-crf", "20", "-movflags", "+faststart",
                                                   "-b:a", "192k", "-shortest"])
    w.send(None)
    try:
        for k in range(n):
            w.send(render(k / fps).tobytes())
            if progress and k % fps == 0:
                progress(k / n)
    finally:
        w.close()
    log(f"OK {out_path}: {total:.1f}s, {n} frames, {time.time() - t0:.0f}s")
    return out_path, total, engine


def _caption(img, step, lt, W, H):
    text = step.get("label")
    if not text:
        return
    d = ImageDraw.Draw(img)
    k = ease_out_back(clamp(lt / 0.3))
    size = int(W * 0.082 * max(0.3, k))
    f = font(size)
    words, lines, cur = text.split(), [], ""
    for wd in words:
        cand = (cur + " " + wd).strip()
        if d.textlength(cand, font=f) > W * 0.86 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = cand
    lines.append(cur)
    y = H * 0.135
    for ln in lines:
        d.text((W / 2, y), ln, font=f, fill=step.get("color", (25, 25, 32)), anchor="mm",
               stroke_width=max(2, int(size * 0.1)), stroke_fill=(255, 255, 255))
        y += size * 1.1
