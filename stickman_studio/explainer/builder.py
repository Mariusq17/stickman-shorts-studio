"""Generic builder for step-by-step explainers.

Everything is driven by the narration: any timing in a step can be a *cue*:
    1.2            seconds from the step start
    "w:rope"       the moment the word/phrase "rope" is spoken (first match in the step)
    "w:rope+0.3"   ... plus an offset
    "end-0.5"      relative to the end of the step
Supports: animation tracks, camera moves on cues, keyword captions that appear exactly
when spoken, animated pop-ups (notes, meters, counters, warnings, checks, arrows) and an
animated follow card for the CTA.
"""
from __future__ import annotations

import bisect
import math
import os
import re
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ..audio import SR, mix_tracks, music_bed, write_wav
from ..easing import clamp, ease_in_cubic, ease_out_back, ease_out_cubic
from ..painter import font
from ..tts import synthesize_all
from .iso import IsoCam
from .lib.camera import CameraPath
from .lib.kit import flush_labels
from .lib.post import Post, average
from .lib.widgets import draw_key, draw_pop, draw_tracker  # noqa: F401  (re-exported)
from .timeline import Tracks

LEAD, TAIL = 0.05, 0.16
WORD_BIAS = -0.08          # aligner is ~0.1 s late on average
KEY_HOLD = 1.05            # keyword stays at least this long after its word ends
KEY_MIN = 1.5

INK, RED, BLUE, GREEN = (25, 25, 32), (226, 52, 64), (40, 110, 235), (40, 160, 90)


def _norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


class StepTracks(Tracks):
    def __init__(self, starts, steps):
        super().__init__()
        self.starts, self.steps = starts, steps
        self.cut_time = 1e9

    def step_at(self, t):
        return max(0, bisect.bisect_right(self.starts, t) - 1)

    def peg_expr(self, t):
        return self.steps[self.step_at(t)].get("pegs", "neutral")

    def peg_pose(self, t):
        st = self.steps[self.step_at(t)]
        return st.get("pose", {"shocked": "panic", "worried": "hold", "happy": "cheer"}.get(st.get("pegs"), "idle"))

    def since_step(self, t):
        return t - self.starts[self.step_at(t)]


class Timing:
    """Resolves cues against the synthesized narration."""

    def __init__(self, steps, clips, starts, durs):
        self.steps, self.clips, self.starts, self.durs = steps, clips, starts, durs

    def word_span(self, i, phrase):
        clip = self.clips[i]
        toks = [_norm(w) for w in clip.words]
        ph = [_norm(w) for w in phrase.split()]
        for k in range(len(toks) - len(ph) + 1):
            if all(toks[k + j].startswith(ph[j]) for j in range(len(ph))):
                s = clip.word_times[k][0]
                e = clip.word_times[k + len(ph) - 1][1]
                return s + LEAD + WORD_BIAS, e + LEAD
        raise KeyError(f"cue '{phrase}' not found in step {i}: {self.steps[i]['text'][:60]}")

    def rel(self, i, cue):
        if isinstance(cue, (int, float)):
            return float(cue)
        m = re.match(r"^w:(.+?)([+-]\d+(?:\.\d+)?)?$", cue)
        if m:
            return max(0.0, self.word_span(i, m.group(1))[0] + float(m.group(2) or 0))
        m = re.match(r"^end([+-]\d+(?:\.\d+)?)?$", cue)
        if m:
            return self.durs[i] + float(m.group(1) or 0)
        raise ValueError(cue)

    def abs(self, i, cue):
        return self.starts[i] + self.rel(i, cue)


# ------------------------------------------------------------------ plan (no audio, no pixels)
def plan_timeline(steps, clips, initial, size=(1080, 1920), fps=30, extra_end=0.0):
    """Resolve every cue of the script against the narration clips: step starts/durations, animation
    tracks, camera path, keywords, pop-ups, sfx and FIXES times. Used by build_explainer and by qa.py
    (which checks a video without rendering it)."""
    durs = [max(s.get("min", 0.0), LEAD + c.duration + TAIL) for s, c in zip(steps, clips)]
    starts = list(np.cumsum([0.0] + durs[:-1]))
    total = float(sum(durs))
    content_total = total
    if extra_end:                                   # e.g. the cover frame appended at the very end
        total += extra_end
    tm = Timing(steps, clips, starts, durs)
    tr = StepTracks(starts, steps)
    for k, v in initial.items():
        tr.set_initial(k, v)
    W, H = size
    bz = W / 1080.0
    tr.set_initial("cam_f", steps[0]["cam"][0])
    tr.set_initial("cam_z", steps[0]["cam"][1] * bz)
    keys, pops, sfx, fixes = [], [], [], []
    for i, st in enumerate(steps):
        s0 = starts[i]
        lead = 0.3 if i > 0 else 0.0
        tr.add("cam_f", s0 - lead, st["cam"][0], st.get("cam_dur", 1.3), "smooth")
        tr.add("cam_z", s0 - lead, st["cam"][1] * bz, st.get("cam_dur", 1.3), "smooth")
        for cue, (f, z), *rest in st.get("cams", []):
            d = rest[0] if rest else 1.0
            tr.add("cam_f", tm.abs(i, cue), f, d, "smooth")
            tr.add("cam_z", tm.abs(i, cue), z * bz, d, "smooth")
        for name, cue, val, td, ease in st.get("do", []):
            ta = tm.abs(i, cue)
            if isinstance(td, str):          # duration given as a cue: animate until that moment
                td = max(0.05, tm.abs(i, td) - ta)
            tr.add(name, ta, val, td, ease)
            if name == "otis_cut":
                tr.cut_time = ta
        for phrase, color in st.get("keys", []):
            text = phrase
            if "|" in phrase:                      # "spoken words|shown text"
                phrase, text = phrase.split("|", 1)
            a, b = tm.word_span(i, phrase)
            keys.append([s0 + a, s0 + b, text, color])
        for p in st.get("pops", []):
            p = dict(p)
            p["t0"] = tm.abs(i, p["at"])
            p["t1"] = p["t0"] + p.get("dur", 2.2) if "until" not in p else tm.abs(i, p["until"])
            pops.append(p)
        for cue, name in st.get("sfx", []):
            sfx.append((tm.abs(i, cue), name, 0.5))
        if "fix" in st:
            fixes.append(tm.abs(i, st["fix"]))
    # keyword windows: appear when spoken, stay readable, never overlap the next one
    keys.sort(key=lambda k: k[0])
    for j, k in enumerate(keys):
        end = max(k[1] + KEY_HOLD, k[0] + KEY_MIN)
        replaced = False
        if j + 1 < len(keys) and keys[j + 1][0] - 0.12 < end:
            end = keys[j + 1][0] - 0.12
            replaced = True
        k[1] = max(k[0] + 0.3, end)
        k.append(replaced)
    camp = CameraPath(tr, total, fps, width=W)
    sfx += [(c - 0.12, "whoosh", 0.55) for c in camp.cuts if c > 0.2]
    # teaser steps (visual hook): the scene plays a LATER moment of the video while the hook line is spoken
    teasers = {}
    for i, st in enumerate(steps):
        tz = st.get("teaser")
        if tz:
            k = tz["step"]
            teasers[i] = starts[k] + durs[k] * tz.get("frac", 0.3)
    off = hook_offset(steps)
    return dict(durs=durs, starts=starts, total=total, content_total=content_total, tm=tm, tracks=tr,
                keys=keys, pops=pops, sfx=sfx, fixes=fixes, camp=camp, W=W, H=H, bz=bz, teasers=teasers,
                offset=off, scene_tracks=SceneTracks(tr, off))


class SceneTracks:
    """What the scene sees: same tracks, but step numbers WITHOUT the hook steps inserted in front
    (open_loop), so scene code written as `if step_i == 2` keeps meaning the original step 2."""

    def __init__(self, tr, offset):
        self._tr, self.offset = tr, offset

    def step_at(self, t):
        return max(0, self._tr.step_at(t) - self.offset)

    def __getattr__(self, name):
        return getattr(self._tr, name)


def hook_offset(steps):
    n = 0
    while n < len(steps) and steps[n].get("teaser"):
        n += 1
    return n


def scene_time(P, t):
    """(time, step, time in step) the scene is drawn at - shifted forward inside a teaser step. The step
    index is in ORIGINAL numbering (hook steps not counted) - see SceneTracks."""
    tr, starts = P["tracks"], P["starts"]
    off = P.get("offset", 0)
    i = tr.step_at(t)
    if i in P.get("teasers", {}):
        te = P["teasers"][i] + (t - starts[i])
        j = tr.step_at(te)
        return te, max(0, j - off), te - starts[j]
    return t, max(0, i - off), t - starts[i]


# ------------------------------------------------------------------ build
def build_explainer(steps, scene_cls, out_path, initial, draw_overlays=None, fps=30, size=(1080, 1920),
                    ss=2, voice_rate=1.2, music_volume=0.07, log=print, progress=None, preview_frames=None,
                    preview_times=None, return_plan=False, tracker=None, motion_blur=True, end_cover=None,
                    cover_dur=0.5):
    t0 = time.time()
    texts = [s["text"] for s in steps]
    clips, engine = synthesize_all(texts, "auto", voice_rate, language="en", log=log)
    log(f"TTS: {engine}")
    cover_img = None
    extra = 0.0
    if end_cover and os.path.exists(end_cover):     # cover frame at the very end: pickable as Shorts thumbnail
        cover_img = Image.open(end_cover).convert("RGB").resize(size, Image.LANCZOS)
        extra = cover_dur
    P = plan_timeline(steps, clips, initial, size, fps, extra)
    durs, starts, total, content_total = P["durs"], P["starts"], P["total"], P["content_total"]
    tr, keys, pops, sfx, fixes, camp = P["tracks"], P["keys"], P["pops"], P["sfx"], P["fixes"], P["camp"]
    W, H = size
    bz = P["bz"]
    # ---------------------------------------------------------- audio
    voice = [(s0 + LEAD, c.samples) for s0, c in zip(starts, clips)]
    sfx += [(p["t0"], {"warn": "sting", "check": "ding", "count": "tick", "card": "pop"}.get(p["kind"], "pop"), 0.3)
            for p in pops if p.get("sound", True)]
    music = music_bed(total, 3, seed=7, style="lofi")
    mix = mix_tracks(total, voice, sfx, music, music_volume)
    wd = tempfile.mkdtemp(prefix="explainer_")
    wav = os.path.join(wd, "mix.wav")
    write_wav(wav, np.stack([mix, mix], axis=1))
    if return_plan:
        return dict(tracks=tr, keys=keys, pops=pops, starts=starts, durs=durs, total=total, wav=wav,
                    engine=engine)
    # ---------------------------------------------------------- render
    RW, RH = W * ss, H * ss
    scene = scene_cls(RW, RH)
    post = Post(W, H)
    t_track0 = starts[1] if len(starts) > 1 else 0.0
    t_track1 = starts[-1] - 0.2

    def frame(t):
        i = tr.step_at(t)
        img = scene.bg.copy()
        f, z = camp.at(t)
        cam = IsoCam(img, f, z * ss, (RW / 2, RH * 0.56))
        ts, si, st_ = scene_time(P, t)
        scene.draw(img, cam, P["scene_tracks"], ts, si, st_)
        flush_labels(cam)          # callout labels always on top of every object
        if draw_overlays:
            draw_overlays(img, P["scene_tracks"], t, RW, RH)
        return img.reduce(ss) if ss > 1 else img, (f, z)

    def render(t, blur=False):
        if cover_img is not None and t >= content_total:
            return cover_img
        sp = camp.speed_at(t)
        if blur and motion_blur and sp > 0.010:
            subs = [frame(t + dt / fps)[0] for dt in (-0.33, 0.0, 0.33)]
            img = average(subs)
        else:
            img = frame(t)[0]
        f, z = camp.at(t)
        film = getattr(scene, "film_amount", lambda tr_, t_: 0.0)(tr, t)
        img = post.grade(img)
        if film > 0:
            img = post.film(img, t, film)
        img = post.dof(img, clamp((z / bz - 190) / 140) * 0.9)
        img = post.whip(img, camp.whip_amount(t))
        cam = IsoCam(img, f, z, (W / 2, H * 0.56))
        for p in pops:
            if p["t0"] - 0.01 <= t <= p["t1"] + 0.35:
                draw_pop(img, cam, p, t, W, H, tr)
        if tracker and fixes:
            draw_tracker(img, t, fixes, len(fixes), tracker.get("label", "FIXES"), t_track0, t_track1, W, H)
        for k in keys:
            if k[0] <= t <= k[1] + (0.12 if k[4] else 0.3):
                draw_key(img, k, t, W, H)
        return img

    if preview_times is not None:
        return [render(min(total - 0.01, x)) for x in preview_times], starts, durs, keys
    if preview_frames is not None:
        return [render(min(total - 0.01, starts[i] + durs[i] * fr)) for i, fr in preview_frames], starts, durs, keys

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
            w.send(render(k / fps, blur=True).tobytes())
            if progress and k % fps == 0:
                progress(k / n)
    finally:
        w.close()
    log(f"OK {out_path}: {total:.1f}s, {n} frames, {time.time() - t0:.0f}s")
    return out_path, total, engine


