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


# ------------------------------------------------------------------ build
def build_explainer(steps, scene_cls, out_path, initial, draw_overlays=None, fps=30, size=(1080, 1920),
                    ss=2, voice_rate=1.3, music_volume=0.07, log=print, progress=None, preview_frames=None,
                    preview_times=None, return_plan=False):
    t0 = time.time()
    texts = [s["text"] for s in steps]
    clips, engine = synthesize_all(texts, "auto", voice_rate, language="en", log=log)
    log(f"TTS: {engine}")
    durs = [max(s.get("min", 0.0), LEAD + c.duration + TAIL) for s, c in zip(steps, clips)]
    starts = list(np.cumsum([0.0] + durs[:-1]))
    total = float(sum(durs))
    tm = Timing(steps, clips, starts, durs)
    tr = StepTracks(starts, steps)
    for k, v in initial.items():
        tr.set_initial(k, v)
    W, H = size
    bz = W / 1080.0
    tr.set_initial("cam_f", steps[0]["cam"][0])
    tr.set_initial("cam_z", steps[0]["cam"][1] * bz)
    keys, pops, sfx = [], [], []
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

    def render(t):
        i = tr.step_at(t)
        img = scene.bg.copy()
        f = tr.get("cam_f", t)
        z = tr.get("cam_z", t) * ss * (1.0 + 0.012 * math.sin(t * 0.35))
        cam = IsoCam(img, f, z, (RW / 2, RH * 0.56))
        scene.draw(img, cam, tr, t, i, t - starts[i])
        if draw_overlays:
            draw_overlays(img, tr, t, RW, RH)
        for p in pops:
            if p["t0"] - 0.01 <= t <= p["t1"] + 0.35:
                draw_pop(img, cam, p, t, RW, RH)
        for k in keys:
            if k[0] <= t <= k[1] + (0.12 if k[4] else 0.3):
                draw_key(img, k, t, RW, RH)
        return img.reduce(ss) if ss > 1 else img

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
            w.send(render(k / fps).tobytes())
            if progress and k % fps == 0:
                progress(k / n)
    finally:
        w.close()
    log(f"OK {out_path}: {total:.1f}s, {n} frames, {time.time() - t0:.0f}s")
    return out_path, total, engine


# ------------------------------------------------------------- overlays
def _fade(t, t0, t1, fin=0.2, fout=0.25):
    a = clamp((t - t0) / fin) if fin > 0 else 1.0
    b = 1.0 - clamp((t - t1) / fout) if fout > 0 else 1.0
    return min(a, b)


def _paste(img, layer, x, y, alpha):
    if alpha <= 0.01:
        return
    if alpha < 0.999:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    img.paste(layer, (int(x), int(y)), layer)


def _shadowed_box(w, h, radius, fill, shadow=0.10, outline=None, ow=0):
    """RGBA layer with a soft drop shadow (blurred)."""
    pad = int(h * 0.35) + 4
    L = Image.new("RGBA", (int(w + 2 * pad), int(h + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle((pad, pad + h * 0.08, pad + w, pad + h * 1.08), radius=radius,
                        fill=(0, 0, 0, int(255 * shadow * 2.2)))
    L = L.filter(ImageFilter.GaussianBlur(max(2, h * 0.09)))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle((pad, pad, pad + w, pad + h), radius=radius, fill=fill, outline=outline,
                        width=ow)
    return L, pad


def draw_key(img, k, t, W, H):
    """Keyword caption: pops in when spoken, glides up, fades out."""
    t0, t1, text, color, replaced = k
    a = _fade(t, t0, t1, 0.18, 0.1 if replaced else 0.25)
    if a <= 0:
        return
    pin = ease_out_back(clamp((t - t0) / 0.28))
    pout = 0.0 if replaced else ease_in_cubic(clamp((t - t1) / 0.25))
    size = int(W * 0.080 * (0.88 + 0.12 * pin))
    f = font(size)
    tmp = ImageDraw.Draw(img)
    lines, cur = [], ""
    for wd in text.split():
        c = (cur + " " + wd).strip()
        if tmp.textlength(c, font=f) > W * 0.84 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = c
    lines.append(cur)
    lw = int(max(tmp.textlength(l, font=f) for l in lines)) + size
    lh = int(size * 1.15 * len(lines) + size * 0.4)
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for j, ln in enumerate(lines):
        d.text((lw / 2, size * 0.75 + j * size * 1.15), ln, font=f, fill=color + (255,), anchor="mm",
               stroke_width=max(2, int(size * 0.12)), stroke_fill=(255, 255, 255, 255))
    y = H * 0.115 + (1 - pin) * H * 0.012 - pout * H * 0.01
    _paste(img, layer, W / 2 - lw / 2, y, a)


def _anchor(pos, w, h, W, H):
    m = W * 0.05
    return {
        "tl": (m, H * 0.22), "tr": (W - w - m, H * 0.22),
        "ml": (m, H * 0.40), "mr": (W - w - m, H * 0.40),
        "bl": (m, H * 0.74), "br": (W - w - m, H * 0.74),
        "bc": (W / 2 - w / 2, H * 0.80), "c": (W / 2 - w / 2, H * 0.45),
    }.get(pos, (W / 2 - w / 2, H * 0.80))


def _icon(d, kind, cx, cy, r, color):
    lw = max(2, int(r * 0.22))
    if kind == "warn":
        d.polygon([(cx, cy - r), (cx + r * 1.1, cy + r * 0.85), (cx - r * 1.1, cy + r * 0.85)], fill=color)
        d.text((cx, cy + r * 0.15), "!", font=font(int(r * 1.3)), fill=(255, 255, 255), anchor="mm")
    elif kind == "check":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
        d.line([(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.55, cy - r * 0.4)],
               fill=(255, 255, 255), width=lw, joint="curve")
    else:
        d.ellipse((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), fill=color)


def draw_pop(img, cam, p, t, W, H):
    kind = p["kind"]
    t0, t1 = p["t0"], p["t1"]
    a = _fade(t, t0, t1, 0.2, 0.3)
    if a <= 0:
        return
    k = ease_out_back(clamp((t - t0) / 0.35))
    color = p.get("color", INK)
    if kind in ("note", "warn", "check"):
        text = p["text"]
        size = int(W * 0.060)
        f = font(size)
        tw = ImageDraw.Draw(img).textlength(text, font=f)
        icon = kind if kind != "note" else "dot"
        w, h = tw + size * 2.4, size * 1.9
        L, pad = _shadowed_box(w, h, h * 0.5, (255, 255, 255, 255))
        d = ImageDraw.Draw(L)
        col = {"warn": RED, "check": GREEN}.get(kind, color)
        _icon(d, icon, pad + size * 1.05, pad + h / 2, size * 0.55, col)
        d.text((pad + size * 1.85, pad + h / 2), text, font=f, fill=col if kind != "note" else INK, anchor="lm")
        x, y = _anchor(p.get("pos", "bc"), w, h, W, H)
        if kind == "warn":
            x += math.sin(t * 40) * W * 0.004 * clamp(1.2 - (t - t0))
        x += (1 - k) * (W * 0.15 if x > W / 2 else -W * 0.15)
        _paste(img, L, x - pad, y - pad, a)
    elif kind == "meter":
        w, h = W * 0.62, W * 0.20
        L, pad = _shadowed_box(w, h, W * 0.03, (255, 255, 255, 255))
        d = ImageDraw.Draw(L)
        v0, v1 = p.get("from", 0.0), p.get("to", 1.0)
        prog = ease_out_cubic(clamp((t - t0 - 0.25) / p.get("anim", 1.2)))
        v = v0 + (v1 - v0) * prog
        d.text((pad + w * 0.06, pad + h * 0.28), p["text"], font=font(int(h * 0.20)), fill=INK, anchor="lm")
        d.text((pad + w * 0.94, pad + h * 0.28), p.get("fmt", "{:.0%}").format(v), font=font(int(h * 0.22)),
               fill=color, anchor="rm")
        bx0, by0, bx1, by1 = pad + w * 0.06, pad + h * 0.55, pad + w * 0.94, pad + h * 0.80
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=(by1 - by0) / 2, fill=(230, 232, 238))
        if v > 0.01:
            d.rounded_rectangle((bx0, by0, bx0 + (bx1 - bx0) * min(1, v), by1), radius=(by1 - by0) / 2, fill=color)
        x, y = _anchor(p.get("pos", "bc"), w, h, W, H)
        y += (1 - k) * H * 0.04
        _paste(img, L, x - pad, y - pad, a)
    elif kind == "count":
        n0, n1 = p["from"], p["to"]
        prog = ease_out_cubic(clamp((t - t0) / p.get("anim", 1.0)))
        val = int(round(n0 + (n1 - n0) * prog))
        big = p.get("fmt", "{}").format(val)
        size = int(W * 0.14)
        sub = p.get("sub", "")
        tw = max(ImageDraw.Draw(img).textlength(big, font=font(size)),
                 ImageDraw.Draw(img).textlength(sub, font=font(int(size * 0.3))))
        w, h = tw + size * 0.8, size * (1.55 if sub else 1.2)
        L, pad = _shadowed_box(w, h, size * 0.25, (255, 255, 255, 255))
        d = ImageDraw.Draw(L)
        d.text((pad + w / 2, pad + size * 0.62), big, font=font(size), fill=color, anchor="mm")
        if sub:
            d.text((pad + w / 2, pad + size * 1.25), sub, font=font(int(size * 0.3)), fill=(90, 95, 110), anchor="mm")
        x, y = _anchor(p.get("pos", "bc"), w, h, W, H)
        s = 0.7 + 0.3 * k
        L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))))
        _paste(img, L, x - pad * s + (w * (1 - s)) / 2, y - pad * s + (h * (1 - s)) / 2, a)
    elif kind == "arrow":
        # label card with a pointer line to a world-space point
        tx, ty = cam.p(*p["xyz"])
        text = p["text"]
        size = int(W * 0.056)
        f = font(size)
        tw = ImageDraw.Draw(img).textlength(text, font=f)
        w, h = tw + size * 1.2, size * 1.7
        dx, dy = p.get("off", (0.22, -0.10))
        bx, by = tx + dx * W, ty + dy * H
        bx = min(max(bx, W * 0.03 + w / 2), W * 0.97 - w / 2)
        d = ImageDraw.Draw(img)
        prog = ease_out_cubic(clamp((t - t0) / 0.35))
        ex, ey = bx + (tx - bx) * prog, by + (ty - by) * prog
        if a > 0.5:
            d.line((bx, by, ex, ey), fill=color, width=max(3, int(W * 0.005)))
            r = W * 0.012
            d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=color)
        L, pad = _shadowed_box(w, h, h * 0.3, color + (255,))
        ImageDraw.Draw(L).text((pad + w / 2, pad + h / 2), text, font=f, fill=(255, 255, 255), anchor="mm")
        s = 0.6 + 0.4 * k
        L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))))
        _paste(img, L, bx - L.width / 2, by - L.height / 2, a)
    elif kind == "card":
        draw_follow_card(img, p, t, W, H, a)


def draw_follow_card(img, p, t, W, H, a=1.0):
    """CTA: clean follow card; a finger taps the button, it turns into 'Following'."""
    t0 = p["t0"]
    k = ease_out_back(clamp((t - t0) / 0.45))
    w, h = W * 0.90, W * 0.25
    L, pad = _shadowed_box(w, h, h * 0.22, (255, 255, 255, 255), shadow=0.14)
    d = ImageDraw.Draw(L)
    # avatar: a peg face
    ar = h * 0.30
    ax, ay = pad + h * 0.48, pad + h / 2
    d.ellipse((ax - ar, ay - ar, ax + ar, ay + ar), fill=(255, 170, 60), outline=(200, 120, 30), width=3)
    for sx in (-1, 1):
        ex = ax + sx * ar * 0.36
        d.ellipse((ex - ar * 0.24, ay - ar * 0.38, ex + ar * 0.24, ay + ar * 0.10), fill=(255, 255, 255),
                  outline=(40, 40, 50), width=2)
        d.ellipse((ex - ar * 0.1, ay - ar * 0.22, ex + ar * 0.1, ay - ar * 0.02), fill=(25, 25, 35))
    d.chord((ax - ar * 0.35, ay + ar * 0.05, ax + ar * 0.35, ay + ar * 0.55), 0, 180, fill=(60, 20, 30))
    d.text((pad + h * 0.92, pad + h * 0.38), p.get("title", "How It's Built"), font=font(int(h * 0.15)), fill=INK,
           anchor="lm")
    d.text((pad + h * 0.92, pad + h * 0.63), p.get("sub", "step by step"),
           font=font(int(h * 0.10)), fill=(110, 115, 128), anchor="lm")
    # button
    tap = t0 + p.get("tap", 1.3)
    pressed = t >= tap
    squish = 1 - 0.08 * math.exp(-((t - tap) / 0.07) ** 2)
    bw, bh = h * 0.95 * squish, h * 0.36 * squish
    bx = pad + w - h * 0.62
    by = pad + h / 2
    col = (235, 236, 240) if pressed else (230, 30, 45)
    d.rounded_rectangle((bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), radius=bh / 2, fill=col)
    d.text((bx, by), "Following" if pressed else "Follow", font=font(int(h * 0.12 * (0.85 if pressed else 1))),
           fill=INK if pressed else (255, 255, 255), anchor="mm")
    if pressed and t - tap < 0.45:
        rr = (t - tap) * h * 1.6
        d.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=(230, 30, 45, int(200 * (1 - (t - tap) / 0.45))),
                  width=4)
    x, y = W / 2 - w / 2, H * 0.78 + (1 - k) * H * 0.08
    _paste(img, L, x - pad, y - pad, a)
    # tapping finger
    if t0 + 0.5 < t < tap + 0.7:
        prog = ease_out_cubic(clamp((t - t0 - 0.5) / (tap - t0 - 0.5)))
        fx = x + (bx - pad) + (1 - prog) * W * 0.12
        fy = y + (by - pad) + h * 0.20 + (1 - prog) * H * 0.06
        dd = ImageDraw.Draw(img)
        r = W * 0.035
        dd.ellipse((fx - r, fy - r, fx + r, fy + r), fill=(255, 220, 190), outline=(120, 80, 60), width=3)
        dd.rounded_rectangle((fx - r * 0.9, fy, fx + r * 0.9, fy + r * 3), radius=r * 0.8, fill=(255, 220, 190),
                             outline=(120, 80, 60), width=3)
    # floating hearts after the tap
    if pressed:
        dd = ImageDraw.Draw(img)
        for j in range(4):
            ph = ((t - tap) * 0.8 + j * 0.25) % 1.0
            hx = x + w * 0.80 + math.sin(j * 2 + ph * 4) * W * 0.03
            hy = y - ph * H * 0.12
            r = W * 0.018 * (1 - ph)
            if r > 1:
                dd.ellipse((hx - r, hy - r, hx, hy), fill=(235, 60, 80))
                dd.ellipse((hx, hy - r, hx + r, hy), fill=(235, 60, 80))
                dd.polygon([(hx - r, hy - r * 0.5), (hx + r, hy - r * 0.5), (hx, hy + r)], fill=(235, 60, 80))
