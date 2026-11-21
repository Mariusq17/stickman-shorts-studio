"""Animated on-screen widgets (all drawn in screen space at render resolution).

Pop-up dicts (used in a step's "pops" list; "at"/"until" are narration cues):
  note    {text, pos}                       white chip with a dot
  warn    {text, pos}                       red warning chip that shakes in
  check   {text, pos}                       green check chip
  stamp   {text, color, pos}                rotated rubber stamp that slams in
  meter   {text, from, to, color, fmt, pos, anim}
  bars    {title, items:[(label, value 0..1, color)], pos, anim}
  count   {from, to, fmt, sub, color, pos, anim}
  equation{parts:[str...], colors:[...], step, pos}  pieces appear one after another
  graph   {title, track, ymax, color, pos, window}   live line graph of an animation track
  arrow   {xyz, text, color, off}                    label with a pointer to a 3D point
  card    {title, sub, tap}                          follow card CTA
  emoji   {emoji, text, no, xy|pos, size}            big emoji in a bubble with a caption; no=True -> red "NOT" slash
                                                     (use it to SHOW what is said: no motor / no battery / a fish tank...)
  hook    {text, hi, color}                          big opening headline (paradox question) for the first
                                                     1-3 s; words listed in `hi` get a coloured highlight
Positions: tl tr ml mr bl br bc c.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from ...easing import clamp, ease_in_cubic, ease_out_back, ease_out_cubic
from ...painter import font
from .palette import BLUE, GREEN, INK, RED

GREY = (110, 115, 128)


# ------------------------------------------------------------------ helpers
def fade(t, t0, t1, fin=0.2, fout=0.25):
    a = clamp((t - t0) / fin) if fin > 0 else 1.0
    b = 1.0 - clamp((t - t1) / fout) if fout > 0 else 1.0
    return min(a, b)


def paste(img, layer, x, y, alpha):
    if alpha <= 0.01:
        return
    if alpha < 0.999:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy()
        layer.putalpha(a)
    img.paste(layer, (int(x), int(y)), layer)


def card(w, h, radius, fill=(255, 255, 255, 255), shadow=0.10):
    """RGBA rounded card with a soft blurred drop shadow. Returns (layer, pad)."""
    pad = int(h * 0.35) + 4
    L = Image.new("RGBA", (int(w + 2 * pad), int(h + 2 * pad)), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle((pad, pad + h * 0.08, pad + w, pad + h * 1.08), radius=radius,
                        fill=(20, 24, 50, int(255 * shadow * 2.2)))
    L = L.filter(ImageFilter.GaussianBlur(max(2, h * 0.09)))
    ImageDraw.Draw(L).rounded_rectangle((pad, pad, pad + w, pad + h), radius=radius, fill=fill)
    return L, pad


def anchor(pos, w, h, W, H):
    m = W * 0.05
    return {
        "tl": (m, H * 0.20), "tr": (W - w - m, H * 0.20),
        "ml": (m, H * 0.40), "mr": (W - w - m, H * 0.40),
        "bl": (m, H * 0.74), "br": (W - w - m, H * 0.74),
        "bc": (W / 2 - w / 2, H * 0.79), "c": (W / 2 - w / 2, H * 0.45),
    }.get(pos, (W / 2 - w / 2, H * 0.79))


def icon(d, kind, cx, cy, r, color):
    lw = max(2, int(r * 0.24))
    if kind == "warn":
        d.polygon([(cx, cy - r), (cx + r * 1.1, cy + r * 0.85), (cx - r * 1.1, cy + r * 0.85)], fill=color)
        d.text((cx, cy + r * 0.15), "!", font=font(int(r * 1.3)), fill=(255, 255, 255), anchor="mm")
    elif kind == "check":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
        d.line([(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.55, cy - r * 0.4)],
               fill=(255, 255, 255), width=lw, joint="curve")
    else:
        d.ellipse((cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45), fill=color)


def _slide_x(x, k, W):
    return x + (1 - k) * (W * 0.15 if x > W / 2 else -W * 0.15)


# ------------------------------------------------------------------ keyword caption
def draw_key(img, k, t, W, H):
    """Keyword caption: pops in when spoken, glides up, fades out (k = [t0, t1, text, color, replaced])."""
    t0, t1, text, color, replaced = k
    a = fade(t, t0, t1, 0.18, 0.1 if replaced else 0.25)
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
    lh = int(size * 1.15 * len(lines) + size * 0.5)
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for j, ln in enumerate(lines):
        d.text((lw / 2 + size * 0.03, size * 0.80 + j * size * 1.15), ln, font=f, fill=(20, 24, 50, 70), anchor="mm",
               stroke_width=max(2, int(size * 0.12)), stroke_fill=(20, 24, 50, 70))
        d.text((lw / 2, size * 0.75 + j * size * 1.15), ln, font=f, fill=tuple(color) + (255,), anchor="mm",
               stroke_width=max(2, int(size * 0.12)), stroke_fill=(255, 255, 255, 255))
    y = H * 0.112 + (1 - pin) * H * 0.012 - pout * H * 0.01
    paste(img, layer, W / 2 - lw / 2, y, a)


# ------------------------------------------------------------------ progress tracker
def draw_tracker(img, t, events, total, label, t_show, t_hide, W, H, color=GREEN):
    """'FIXES 3/10' pill with segments; each event time fills the next segment with a pulse."""
    a = fade(t, t_show, t_hide, 0.4, 0.4)
    if a <= 0:
        return
    done = sum(1 for e in events if e <= t)
    last = max([e for e in events if e <= t], default=-9)
    pulse = math.exp(-((t - last) / 0.18) ** 2) if t >= last else 0.0
    size = int(W * 0.034)
    seg_w, gap = W * 0.030, W * 0.008
    lab = f"{label} {done}/{total}"
    tw = ImageDraw.Draw(img).textlength(f"{label} {total}/{total}", font=font(size))
    w = size * 0.6 + tw + size * 0.7 + total * (seg_w + gap) + size * 0.4
    h = size * 1.9
    L, pad = card(w, h, h * 0.5, (255, 255, 255, 235), 0.08)
    d = ImageDraw.Draw(L)
    d.text((pad + size * 0.6, pad + h / 2), lab, font=font(size), fill=INK, anchor="lm")
    x = pad + size * 0.6 + tw + size * 0.7
    for i in range(total):
        filled = i < done
        col = color if filled else (226, 229, 236)
        grow = 1.0 + (0.35 * pulse if filled and i == done - 1 else 0)
        sh = h * 0.30 * grow
        d.rounded_rectangle((x, pad + h / 2 - sh / 2, x + seg_w, pad + h / 2 + sh / 2), radius=sh / 2, fill=col)
        x += seg_w + gap
    s = 1.0 + 0.06 * pulse
    if s != 1.0:
        L = L.resize((int(L.width * s), int(L.height * s)))
    paste(img, L, W / 2 - L.width / 2, H * 0.035, a)


# ------------------------------------------------------------------ pop-ups
def draw_pop(img, cam, p, t, W, H, tr=None):
    kind = p["kind"]
    t0, t1 = p["t0"], p["t1"]
    a = fade(t, t0, t1, 0.2, 0.3)
    if a <= 0:
        return
    k = ease_out_back(clamp((t - t0) / 0.35))
    color = tuple(p.get("color", INK))
    if kind in ("note", "warn", "check"):
        text = p["text"]
        size = int(W * 0.058)
        f = font(size)
        tw = ImageDraw.Draw(img).textlength(text, font=f)
        w, h = tw + size * 2.4, size * 1.9
        L, pad = card(w, h, h * 0.5)
        d = ImageDraw.Draw(L)
        col = {"warn": RED, "check": GREEN}.get(kind, color)
        icon(d, kind if kind != "note" else "dot", pad + size * 1.05, pad + h / 2, size * 0.55, col)
        d.text((pad + size * 1.85, pad + h / 2), text, font=f, fill=col if kind != "note" else INK, anchor="lm")
        x, y = anchor(p.get("pos", "bc"), w, h, W, H)
        if kind == "warn":
            x += math.sin(t * 40) * W * 0.005 * clamp(1.2 - (t - t0))
        paste(img, L, _slide_x(x, k, W) - pad, y - pad, a)
    elif kind == "stamp":
        text = p["text"]
        size = int(W * 0.075)
        f = font(size)
        tw = ImageDraw.Draw(img).textlength(text, font=f)
        w, h = int(tw + size * 1.0), int(size * 1.6)
        L = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        col = tuple(p.get("color", GREEN))
        d.rounded_rectangle((10, 10, 10 + w, 10 + h), radius=size * 0.25, outline=col + (255,), width=max(4, size // 9))
        d.text((10 + w / 2, 10 + h / 2), text, font=f, fill=col + (255,), anchor="mm")
        slam = ease_out_cubic(clamp((t - t0) / 0.18))
        sc = 1.8 - 0.8 * slam
        L = L.rotate(-12, expand=True, resample=Image.BICUBIC)
        L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))))
        x, y = anchor(p.get("pos", "mr"), L.width, L.height, W, H)
        paste(img, L, x, y, a * (0.4 + 0.6 * slam))
    elif kind == "meter":
        w, h = W * 0.62, W * 0.20
        L, pad = card(w, h, W * 0.03)
        d = ImageDraw.Draw(L)
        v0, v1 = p.get("from", 0.0), p.get("to", 1.0)
        prog = ease_out_cubic(clamp((t - t0 - 0.25) / p.get("anim", 1.2)))
        v = v0 + (v1 - v0) * prog
        d.text((pad + w * 0.06, pad + h * 0.28), p["text"], font=font(int(h * 0.20)), fill=INK, anchor="lm")
        fmt = p.get("fmt", "{:.0%}")
        if fmt:
            d.text((pad + w * 0.94, pad + h * 0.28), fmt.format(v), font=font(int(h * 0.22)), fill=color, anchor="rm")
        bx0, by0, bx1, by1 = pad + w * 0.06, pad + h * 0.55, pad + w * 0.94, pad + h * 0.80
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=(by1 - by0) / 2, fill=(230, 232, 238))
        if v > 0.01:
            d.rounded_rectangle((bx0, by0, bx0 + (bx1 - bx0) * min(1, v), by1), radius=(by1 - by0) / 2, fill=color)
        x, y = anchor(p.get("pos", "bc"), w, h, W, H)
        paste(img, L, x - pad, y + (1 - k) * H * 0.04 - pad, a)
    elif kind == "bars":
        items = p["items"]
        w = W * 0.66
        rowh = W * 0.10
        h = W * 0.10 + rowh * len(items)
        L, pad = card(w, h, W * 0.03)
        d = ImageDraw.Draw(L)
        d.text((pad + w * 0.06, pad + W * 0.055), p.get("title", ""), font=font(int(W * 0.04)), fill=INK, anchor="lm")
        for j, (lab, val, col) in enumerate(items):
            prog = ease_out_cubic(clamp((t - t0 - 0.2 - j * p.get("stagger", 0.6)) / p.get("anim", 0.9)))
            y = pad + W * 0.09 + j * rowh
            d.text((pad + w * 0.06, y + rowh * 0.22), lab, font=font(int(W * 0.03)), fill=GREY, anchor="lm")
            x0 = pad + w * 0.06
            x1 = x0 + (w * 0.88) * val * prog
            d.rounded_rectangle((x0, y + rowh * 0.42, max(x0 + 2, x1), y + rowh * 0.82), radius=rowh * 0.2,
                                fill=tuple(col))
        x, y = anchor(p.get("pos", "bc"), w, h, W, H)
        paste(img, L, x - pad, y + (1 - k) * H * 0.04 - pad, a)
    elif kind == "count":
        n0, n1 = p["from"], p["to"]
        prog = ease_out_cubic(clamp((t - t0) / p.get("anim", 1.0)))
        big = p.get("fmt", "{}").format(int(round(n0 + (n1 - n0) * prog)))
        size = int(W * 0.14)
        sub = p.get("sub", "")
        dd = ImageDraw.Draw(img)
        tw = max(dd.textlength(big, font=font(size)), dd.textlength(sub, font=font(int(size * 0.3))))
        w, h = tw + size * 0.8, size * (1.55 if sub else 1.2)
        L, pad = card(w, h, size * 0.25)
        d = ImageDraw.Draw(L)
        d.text((pad + w / 2, pad + size * 0.62), big, font=font(size), fill=color, anchor="mm")
        if sub:
            d.text((pad + w / 2, pad + size * 1.25), sub, font=font(int(size * 0.3)), fill=GREY, anchor="mm")
        x, y = anchor(p.get("pos", "bc"), w, h, W, H)
        s = 0.7 + 0.3 * k
        L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))))
        paste(img, L, x - pad * s + (w * (1 - s)) / 2, y - pad * s + (h * (1 - s)) / 2, a)
    elif kind == "equation":
        parts = p["parts"]
        cols = p.get("colors", [INK] * len(parts))
        size = int(W * p.get("size", 0.050))
        f = font(size)
        dd = ImageDraw.Draw(img)
        gap = size * 0.35
        widths = [dd.textlength(x, font=f) for x in parts]
        w = sum(widths) + gap * (len(parts) - 1) + size * 1.2
        h = size * 1.9
        L, pad = card(w, h, h * 0.35)
        d = ImageDraw.Draw(L)
        x = pad + size * 0.6
        step = p.get("step", 0.35)
        for j, (txt, wd) in enumerate(zip(parts, widths)):
            kk = clamp((t - t0 - j * step) / 0.25)
            if kk > 0:
                c = tuple(cols[j])
                d.text((x + wd / 2, pad + h / 2 + (1 - kk) * size * 0.4), txt, font=f, fill=c, anchor="mm")
            x += wd + gap
        x0, y0 = anchor(p.get("pos", "bc"), w, h, W, H)
        paste(img, L, x0 - pad, y0 - pad, a)
    elif kind == "graph" and tr is not None:
        w, h = W * 0.62, W * 0.34
        L, pad = card(w, h, W * 0.03)
        d = ImageDraw.Draw(L)
        d.text((pad + w * 0.06, pad + h * 0.13), p.get("title", ""), font=font(int(W * 0.036)), fill=INK, anchor="lm")
        gx0, gy0, gx1, gy1 = pad + w * 0.08, pad + h * 0.26, pad + w * 0.94, pad + h * 0.88
        d.line((gx0, gy1, gx1, gy1), fill=(210, 213, 222), width=3)
        d.line((gx0, gy0, gx0, gy1), fill=(210, 213, 222), width=3)
        win = p.get("window", 8.0)
        ymax = p.get("ymax", 1.0)
        pts = []
        n = 60
        for j in range(n + 1):
            tt = t0 + win * j / n
            if tt > t:
                break
            v = clamp(tr.get(p["track"], tt) / ymax)
            pts.append((gx0 + (gx1 - gx0) * j / n, gy1 - (gy1 - gy0) * v))
        col = tuple(p.get("color", RED))
        if len(pts) >= 2:
            d.line(pts, fill=col, width=max(3, int(W * 0.006)), joint="curve")
            ex, ey = pts[-1]
            r = W * 0.01
            d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=col)
        x, y = anchor(p.get("pos", "bc"), w, h, W, H)
        paste(img, L, x - pad, y + (1 - k) * H * 0.04 - pad, a)
    elif kind == "arrow":
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
        L, pad = card(w, h, h * 0.3, color + (255,))
        ImageDraw.Draw(L).text((pad + w / 2, pad + h / 2), text, font=f, fill=(255, 255, 255), anchor="mm")
        s = 0.6 + 0.4 * k
        L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))))
        paste(img, L, bx - L.width / 2, by - L.height / 2, a)
    elif kind == "card":
        draw_follow_card(img, p, t, W, H, a)
    elif kind == "hook":
        draw_hook(img, p, t, W, H, a)
    elif kind == "emoji":
        draw_emoji(img, p, t, W, H, a, k)


_EMOJI_FONT = {}


def emoji_font(size=109):
    """Colour emoji font (Noto Color Emoji on Linux, Segoe UI Emoji on Windows). Bitmap fonts only render at 109."""
    if size in _EMOJI_FONT:
        return _EMOJI_FONT[size]
    from PIL import ImageFont
    import os
    for path, sz in (("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109),
                     ("C:/Windows/Fonts/seguiemj.ttf", size), ("/System/Library/Fonts/Apple Color Emoji.ttc", 160)):
        if os.path.exists(path):
            try:
                _EMOJI_FONT[size] = ImageFont.truetype(path, sz)
                return _EMOJI_FONT[size]
            except OSError:
                continue
    _EMOJI_FONT[size] = None
    return None


def emoji_image(ch, px):
    f = emoji_font(109)
    if f is None:
        return None
    L = Image.new("RGBA", (220, 160), (0, 0, 0, 0))
    ImageDraw.Draw(L).text((10, 10), ch, font=f, embedded_color=True)
    bb = L.getbbox()
    if not bb:
        return None
    L = L.crop(bb)
    sc = px / max(L.width, L.height)
    return L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.LANCZOS)


def draw_emoji(img, p, t, W, H, a, k):
    """Illustration bubble: big emoji + short caption; pops with a bounce, wobbles gently while visible."""
    px = int(W * p.get("size", 0.16))
    em = emoji_image(p["emoji"], px)
    text = p.get("text", "")
    f = font(int(W * 0.042))
    tw = ImageDraw.Draw(img).textlength(text, font=f) if text else 0
    w = max(px * 1.35, tw + W * 0.06)
    h = px * 1.3 + (W * 0.06 if text else 0)
    L, pad = card(w, h, W * 0.04)
    d = ImageDraw.Draw(L)
    if em is not None:
        L.paste(em, (int(pad + w / 2 - em.width / 2), int(pad + px * 0.15)), em)
    if p.get("no"):
        cx, cy, r = pad + w / 2, pad + px * 0.15 + px / 2, px * 0.62
        lw = max(4, int(px * 0.09))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED + (235,), width=lw)
        d.line((cx - r * 0.7, cy + r * 0.7, cx + r * 0.7, cy - r * 0.7), fill=RED + (235,), width=lw)
    if text:
        d.text((pad + w / 2, pad + h - W * 0.042), text, font=f, fill=RED if p.get("no") else INK, anchor="mm")
    sc = 0.4 + 0.6 * k
    rot = math.sin((t - p["t0"]) * 3.0) * 3.0
    L = L.rotate(rot, expand=True, resample=Image.BICUBIC)
    L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))))
    if "xy" in p:
        x, y = p["xy"][0] * W - L.width / 2, p["xy"][1] * H - L.height / 2
    else:
        x, y = anchor(p.get("pos", "tr"), L.width, L.height, W, H)
    paste(img, L, x, y, a)


def draw_hook(img, p, t, W, H, a):
    """Opening headline: heavy white text with dark outline, highlighted words on a tilted marker bar,
    punches in word-group by line (first line at t0, second ~0.25 s later). Sits at ~22% height."""
    t0 = p["t0"]
    hi = [w.lower() for w in p.get("hi", [])]
    col = tuple(p.get("color", (255, 200, 40)))
    size = int(W * p.get("size", 0.092))
    f = font(size)
    tmp = ImageDraw.Draw(img)
    lines, cur = [], ""
    for wd in p["text"].split():
        c = (cur + " " + wd).strip()
        if tmp.textlength(c, font=f) > W * 0.86 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = c
    lines.append(cur)
    y0 = H * p.get("y", 0.19)
    for j, ln in enumerate(lines):
        k = ease_out_back(clamp((t - t0 - 0.22 * j) / 0.32))
        if k <= 0:
            continue
        lw = int(tmp.textlength(ln, font=f)) + size
        lh = int(size * 1.45)
        L = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        d = ImageDraw.Draw(L)
        x = size * 0.5
        for wd in ln.split(" "):
            ww = d.textlength(wd, font=f)
            if wd.lower().strip(".,?!'\"") in hi:
                d.rounded_rectangle((x - size * 0.12, lh * 0.16, x + ww + size * 0.12, lh * 0.88),
                                    radius=size * 0.18, fill=col + (255,))
            x += ww + d.textlength(" ", font=f)
        x = size * 0.5
        for wd in ln.split(" "):
            ww = d.textlength(wd, font=f)
            isk = wd.lower().strip(".,?!'\"") in hi
            d.text((x, lh * 0.52), wd, font=f, fill=(25, 25, 32, 255) if isk else (255, 255, 255, 255), anchor="lm",
                   stroke_width=0 if isk else max(3, int(size * 0.13)), stroke_fill=(25, 25, 32, 255))
            x += ww + d.textlength(" ", font=f)
        L = L.rotate(-2.5 if j % 2 == 0 else 1.5, expand=True, resample=Image.BICUBIC)
        sc = 0.55 + 0.45 * k
        L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))))
        paste(img, L, W / 2 - L.width / 2, y0 + j * size * 1.3 - L.height / 2 + size * 0.6, a)


_AVATAR = {}
CHANNEL = dict(title="How It's Built", handle="@howitsbuiltshorts_official")


def _avatar(size):
    """Channel avatar (publishing/brand/avatar.png) cropped to a circle with a white + orange ring."""
    import os
    key = int(size)
    if key in _AVATAR:
        return _AVATAR[key]
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    path = os.path.join(root, "publishing", "brand", "avatar.png")
    S = key * 2
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse((0, 0, S - 1, S - 1), fill=(255, 150, 60, 255))
    d.ellipse((S * 0.05, S * 0.05, S * 0.95, S * 0.95), fill=(255, 255, 255, 255))
    inner = int(S * 0.84)
    if os.path.exists(path):
        src = Image.open(path).convert("RGB")
        c = int(src.width * 0.18)                    # zoom on the mascot so it reads at small size
        av = src.crop((c, int(c * 0.6), src.width - c, src.height - int(c * 1.4))).resize((inner, inner), Image.LANCZOS)
    else:
        av = Image.new("RGB", (inner, inner), (255, 170, 60))
    m = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(m).ellipse((0, 0, inner - 1, inner - 1), fill=255)
    out.paste(av, ((S - inner) // 2, (S - inner) // 2), m)
    out = out.resize((key, key), Image.LANCZOS)
    _AVATAR[key] = out
    return out


def _fit(draw, text, max_w, size):
    while size > 10 and draw.textlength(text, font=font(size)) > max_w:
        size -= 2
    return font(size)


def draw_follow_card(img, p, t, W, H, a=1.0):
    """CTA: channel card (real avatar, name, handle) - a hand taps Follow, it turns into Following."""
    t0 = p["t0"]
    k = ease_out_back(clamp((t - t0) / 0.45))
    w, h = W * 0.92, W * 0.26
    L, pad = card(w, h, h * 0.24, shadow=0.16)
    d = ImageDraw.Draw(L)
    av = _avatar(h * 0.74)
    L.paste(av, (int(pad + h * 0.13), int(pad + h / 2 - av.height / 2)), av)
    tx = pad + h * 0.98
    tap = t0 + p.get("tap", 1.3)
    pressed = t >= tap
    bw0, bh0 = h * 0.92, h * 0.38
    bx, by = pad + w - h * 0.12 - bw0 / 2, pad + h / 2
    text_w = (bx - bw0 / 2) - tx - h * 0.08
    d.text((tx, pad + h * 0.36), p.get("title", CHANNEL["title"]), font=_fit(d, p.get("title", CHANNEL["title"]), text_w,
                                                                                int(h * 0.17)), fill=INK, anchor="lm")
    d.text((tx, pad + h * 0.62), p.get("sub", CHANNEL["handle"]), font=_fit(d, p.get("sub", CHANNEL["handle"]), text_w,
                                                                            int(h * 0.12)), fill=GREY, anchor="lm")
    squish = 1 - 0.08 * math.exp(-((t - tap) / 0.07) ** 2)
    bw, bh = bw0 * squish, bh0 * squish
    if not pressed:
        d.rounded_rectangle((bx - bw / 2, by - bh / 2 + 5, bx + bw / 2, by + bh / 2 + 5), radius=bh / 2,
                            fill=(150, 20, 35))
        d.rounded_rectangle((bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), radius=bh / 2, fill=(232, 36, 52))
        d.rounded_rectangle((bx - bw / 2 + bh * 0.2, by - bh / 2 + bh * 0.1, bx + bw / 2 - bh * 0.2, by - bh * 0.05),
                            radius=bh / 3, fill=(242, 92, 104))
        d.text((bx, by), "+ Follow", font=font(int(h * 0.135)), fill=(255, 255, 255), anchor="mm")
    else:
        d.rounded_rectangle((bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2), radius=bh / 2, fill=(236, 238, 242),
                            outline=(210, 212, 220), width=3)
        d.text((bx, by), "Following", font=font(int(h * 0.115)), fill=INK, anchor="mm")
    if pressed and t - tap < 0.45:
        rr = (t - tap) * h * 1.6
        d.ellipse((bx - rr, by - rr, bx + rr, by + rr), outline=(232, 36, 52, int(200 * (1 - (t - tap) / 0.45))),
                  width=4)
    x, y = W / 2 - w / 2, H * 0.77 + (1 - k) * H * 0.08
    paste(img, L, x - pad, y - pad, a)
    dd = ImageDraw.Draw(img)
    if t0 + 0.5 < t < tap + 0.7:     # pointing hand (mascot orange glove)
        prog = ease_out_cubic(clamp((t - t0 - 0.5) / max(0.1, tap - t0 - 0.5)))
        fx = x + (bx - pad) + h * 0.05 + (1 - prog) * W * 0.12
        fy = y + (by - pad) + h * 0.06 + (1 - prog) * H * 0.06
        r = W * 0.03
        glove, edge = (255, 170, 60), (170, 100, 30)
        dd.rounded_rectangle((fx - r * 0.45, fy - r * 0.2, fx + r * 0.45, fy + r * 2.0), radius=r * 0.45, fill=glove,
                             outline=edge, width=3)
        dd.rounded_rectangle((fx - r * 0.5, fy + r * 1.3, fx + r * 1.9, fy + r * 3.4), radius=r * 0.8, fill=glove,
                             outline=edge, width=3)
        dd.rounded_rectangle((fx + r * 0.1, fy + r * 3.2, fx + r * 1.5, fy + r * 4.4), radius=r * 0.3,
                             fill=(255, 255, 255), outline=edge, width=3)
    if pressed:
        for j in range(4):
            ph = ((t - tap) * 0.8 + j * 0.25) % 1.0
            hx = x + w * 0.80 + math.sin(j * 2 + ph * 4) * W * 0.03
            hy = y - ph * H * 0.12
            r = W * 0.018 * (1 - ph)
            if r > 1:
                dd.ellipse((hx - r, hy - r, hx, hy), fill=(235, 60, 80))
                dd.ellipse((hx, hy - r, hx + r, hy), fill=(235, 60, 80))
                dd.polygon([(hx - r, hy - r * 0.5), (hx + r, hy - r * 0.5), (hx, hy + r)], fill=(235, 60, 80))
