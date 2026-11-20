"""Vector props drawn 100% from code. Every prop is a function
    draw(p, x, y, s, t, th, lw, **kw)
where (x, y) is the anchor (centre, or bottom-centre for floor props), s is the
prop scale in world px (usually the character unit U), t is the local time
since the prop appeared and th is the Theme."""
from __future__ import annotations

import math
import random

from .easing import clamp, ease_out_back, ease_out_cubic, lerp
from .figure import draw_mic, _star


def _txt(p, pos, s, size, color, th, stroke=0.0):
    p.text(pos, s, size, color, anchor="mm", stroke=stroke, stroke_fill=th.ink if stroke else None)


def desk(p, x, y, s, t, th, lw, **kw):
    w, h = s * 0.62, s * 0.40
    top = y - h
    p.rect(x - w / 2, top, x + w / 2, top + s * 0.05, fill=th.bg2, outline=th.ink, width=lw * 0.8)
    for sx in (-1, 1):
        p.line([(x + sx * w * 0.42, top + s * 0.05), (x + sx * w * 0.42, y)], th.ink, lw * 0.8)
    p.rect(x + w * 0.05, top + s * 0.06, x + w * 0.38, top + s * 0.20, fill=th.prop_fill,
           outline=th.ink, width=lw * 0.6)


def laptop(p, x, y, s, t, th, lw, **kw):
    top = y - s * 0.45   # sits on the desk top
    bw = s * 0.30
    p.polygon([(x - bw / 2, top), (x + bw / 2, top), (x + bw * 0.55, top + s * 0.02),
               (x - bw * 0.55, top + s * 0.02)], fill=th.prop_fill, outline=th.ink, width=lw * 0.6)
    sw, sh = bw * 0.9, s * 0.17
    p.rect(x - sw / 2, top - sh, x + sw / 2, top, fill=th.ink, outline=th.ink, width=lw * 0.6,
           radius=s * 0.01)
    p.rect(x - sw / 2 + s * 0.012, top - sh + s * 0.012, x + sw / 2 - s * 0.012, top - s * 0.012,
           fill=th.accent2)
    # scrolling "code" lines
    for i in range(5):
        ly = top - sh + s * 0.03 + i * s * 0.025
        ln = (0.3 + 0.6 * abs(math.sin(i * 1.7 + int(t * 6) * 0.9))) * (sw - s * 0.05)
        p.line([(x - sw / 2 + s * 0.025, ly), (x - sw / 2 + s * 0.025 + ln, ly)],
               (255, 255, 255), max(1.0, lw * 0.25), caps=False)
    p.circle((x, top - sh + s * 0.006), s * 0.004, fill=th.bad)


def _chart(p, x, y, s, t, th, lw, up=True):
    w, h = s * 0.46, s * 0.36
    x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
    p.rect(x0, y0, x1, y1, fill=th.prop_fill, outline=th.ink, width=lw * 0.7, radius=s * 0.02)
    p.line([(x0 + s * 0.04, y0 + s * 0.03), (x0 + s * 0.04, y1 - s * 0.04), (x1 - s * 0.03, y1 - s * 0.04)],
           th.ink, lw * 0.5)
    vals = [0.15, 0.32, 0.25, 0.5, 0.42, 0.72, 0.62, 0.95] if up else \
        [0.9, 0.78, 0.84, 0.6, 0.66, 0.35, 0.42, 0.06]
    k = ease_out_cubic(t / 1.3)
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        fi = i / (n - 1)
        if fi > k:
            break
        pts.append((lerp(x0 + s * 0.07, x1 - s * 0.07, fi), lerp(y1 - s * 0.07, y0 + s * 0.06, v)))
    col = th.good if up else th.bad
    if len(pts) >= 2:
        p.line(pts, col, lw * 0.9)
        ax, ay = pts[-1]
        bx, by = pts[-2]
        ang = math.atan2(ay - by, ax - bx)
        a = s * 0.05
        p.polygon([(ax + math.cos(ang) * a * 0.6, ay + math.sin(ang) * a * 0.6),
                   (ax + math.cos(ang + 2.4) * a, ay + math.sin(ang + 2.4) * a),
                   (ax + math.cos(ang - 2.4) * a, ay + math.sin(ang - 2.4) * a)], fill=col)
    lbl = "$$$" if up else "-99%"
    _txt(p, (x1 - s * 0.11, y0 + s * 0.06), lbl, s * 0.05, col, th)


def chart_up(p, x, y, s, t, th, lw, **kw):
    _chart(p, x, y, s, t, th, lw, True)


def chart_down(p, x, y, s, t, th, lw, **kw):
    sh = s * 0.01 * math.sin(t * 40) * clamp(t - 1.0)
    _chart(p, x + sh, y, s, t, th, lw, False)


def clock(p, x, y, s, t, th, lw, **kw):
    r = s * 0.13
    p.circle((x, y), r, fill=th.prop_fill, outline=th.ink, width=lw * 0.8)
    for i in range(12):
        a = math.radians(i * 30)
        p.line([(x + math.sin(a) * r * 0.8, y - math.cos(a) * r * 0.8),
                (x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92)], th.ink, lw * 0.3, caps=False)
    am = math.radians(t * 720)
    ah = math.radians(t * 60)
    p.line([(x, y), (x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75)], th.bad, lw * 0.5)
    p.line([(x, y), (x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5)], th.ink, lw * 0.7)
    p.circle((x, y), lw * 0.6, fill=th.ink)
    # alarm bells wobble
    wob = 6 * math.sin(t * 30)
    for sx in (-1, 1):
        a = math.radians(sx * 40 + wob)
        p.circle((x + math.sin(a) * r * 1.05, y - math.cos(a) * r * 1.05), r * 0.25, fill=th.accent,
                 outline=th.ink, width=lw * 0.5)


def question(p, x, y, s, t, th, lw, **kw):
    bob = math.sin(t * 3) * s * 0.02
    rot_y = y + bob
    _txt(p, (x, rot_y), "?", s * 0.26, th.accent, th, stroke=s * 0.012)


def exclamation(p, x, y, s, t, th, lw, **kw):
    sh = math.sin(t * 35) * s * 0.008
    _txt(p, (x + sh, y), "!", s * 0.28, th.bad, th, stroke=s * 0.012)


def bulb(p, x, y, s, t, th, lw, **kw):
    on = 1.0 if t > 0.35 or (int(t * 20) % 2 == 0) else 0.0
    r = s * 0.085
    if on:
        for i in range(10):
            a = math.radians(i * 36 + t * 40)
            r0 = r * 1.35
            r1 = r * (1.8 + 0.2 * math.sin(t * 8 + i))
            p.line([(x + math.cos(a) * r0, y - r * 0.2 + math.sin(a) * r0),
                    (x + math.cos(a) * r1, y - r * 0.2 + math.sin(a) * r1)], th.accent, lw * 0.6)
    p.circle((x, y - r * 0.2), r, fill=th.accent if on else th.prop_fill, outline=th.ink, width=lw * 0.7)
    p.rect(x - r * 0.45, y + r * 0.7, x + r * 0.45, y + r * 1.25, fill=(150, 150, 160), outline=th.ink,
           width=lw * 0.5)
    p.line([(x - r * 0.3, y + r * 0.2), (x, y - r * 0.2), (x + r * 0.3, y + r * 0.2)], th.ink, lw * 0.35)


def _bill(p, x, y, s, ang, th, lw):
    w, h = s * 0.11, s * 0.055
    ca, sa = math.cos(ang), math.sin(ang)
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    pts = [(x + cx * ca - cy * sa, y + cx * sa + cy * ca) for cx, cy in corners]
    p.polygon(pts, fill=(110, 200, 120), outline=(20, 90, 40), width=lw * 0.3)
    p.text((x, y), "$", s * 0.04, (20, 90, 40), anchor="mm")


def money(p, x, y, s, t, th, lw, area=None, **kw):
    """Money rain over the given area (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = area or (x - s, y - s, x + s, y + s)
    rnd = random.Random(7)
    for i in range(18):
        sx = rnd.uniform(x0, x1)
        speed = rnd.uniform(0.25, 0.45) * (y1 - y0)
        yy = y0 + ((t * speed + rnd.uniform(0, y1 - y0)) % (y1 - y0))
        sway = math.sin(t * 2 + i) * s * 0.05
        if i % 3 == 0:
            p.circle((sx + sway, yy), s * 0.03, fill=th.accent, outline=th.ink, width=lw * 0.3)
        else:
            _bill(p, sx + sway, yy, s, math.sin(t * 3 + i) * 0.6, th, lw)


def coins(p, x, y, s, t, th, lw, **kw):
    base = y + s * 0.15
    for col in range(3):
        n = 3 + col * 2
        k = clamp(t * 4 - col)
        for i in range(int(n * k)):
            cy = base - i * s * 0.03
            cx = x + (col - 1) * s * 0.11
            p.ellipse((cx, cy), s * 0.05, s * 0.018, fill=th.accent, outline=th.ink, width=lw * 0.3)
    _txt(p, (x, y - s * 0.15), "$", s * 0.14, th.good, th, stroke=s * 0.008)


def _cursor(p, x, y, s, th, lw):
    pts = [(0, 0), (0, 0.07), (0.018, 0.053), (0.03, 0.08), (0.04, 0.076), (0.028, 0.05), (0.05, 0.05)]
    p.polygon([(x + a * s, y + b * s) for a, b in pts], fill=(255, 255, 255), outline=(0, 0, 0),
              width=lw * 0.35)


def subscribe(p, x, y, s, t, th, lw, label="SUBSCRIBE", done_label="SUBSCRIBED", **kw):
    click_t = 1.1
    pressed = t > click_t
    squish = 1 - 0.12 * math.exp(-((t - click_t) / 0.08) ** 2)
    w, h = s * 0.50 * squish, s * 0.13 * squish
    col = (120, 120, 128) if pressed else (230, 30, 40)
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=col, outline=th.ink, width=lw * 0.5,
           radius=s * 0.03)
    _txt(p, (x, y), done_label if pressed else label, s * 0.055, (255, 255, 255), th)
    # bell
    bx, by = x + w / 2 + s * 0.09, y
    wob = math.sin(t * 25) * 18 * clamp(1.5 - abs(t - click_t - 0.4))
    _bell(p, bx, by, s * 0.8, wob, th, lw)
    # cursor flying in and clicking
    k = ease_out_cubic(t / click_t)
    cx = lerp(x + s * 0.55, x + w * 0.2, k)
    cy = lerp(y + s * 0.45, y + h * 0.1, k)
    if t < click_t + 0.8:
        _cursor(p, cx, cy, s, th, lw)
    if pressed and t < click_t + 0.5:
        rr = (t - click_t) * s * 0.6
        p.circle((x + w * 0.2, y), rr, outline=(255, 255, 255), width=lw * 0.3)


def _bell(p, x, y, s, wob, th, lw):
    r = s * 0.07
    a = math.radians(wob)
    pts = []
    for i in range(0, 181, 20):
        ang = math.radians(180 + i)
        pts.append((r * math.cos(ang), r * math.sin(ang) * 1.1))
    pts += [(r * 1.25, r * 0.7), (-r * 1.25, r * 0.7)]
    rp = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
    p.polygon(rp, fill=th.accent, outline=th.ink, width=lw * 0.4)
    p.circle((x - math.sin(a) * r * 0.9, y + math.cos(a) * r * 0.95), r * 0.22, fill=th.ink)


def bell(p, x, y, s, t, th, lw, **kw):
    _bell(p, x, y, s * 1.6, math.sin(t * 22) * 20, th, lw)


def _heart(p, x, y, r, color, ink, lw):
    pts = []
    for i in range(0, 360, 12):
        a = math.radians(i)
        hx = 16 * math.sin(a) ** 3
        hy = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + hx * r / 16, y + hy * r / 16))
    p.polygon(pts, fill=color, outline=ink, width=lw)


def like(p, x, y, s, t, th, lw, label="LIKE", **kw):
    beat = 1 + 0.12 * max(0.0, math.sin(t * 7)) ** 6
    p.circle((x, y), s * 0.12 * beat, fill=th.prop_fill, outline=th.ink, width=lw * 0.6)
    _heart(p, x, y, s * 0.075 * beat, th.bad, th.ink, lw * 0.3)
    _txt(p, (x, y + s * 0.17), label, s * 0.05, th.ink, th)
    for i in range(3):
        ph = (t * 0.9 + i / 3) % 1
        _heart(p, x + s * (0.1 + 0.05 * i) * math.sin(i * 2 + ph * 3), y - s * (0.12 + ph * 0.3),
               s * 0.025 * (1 - ph), th.bad, th.bad, 0.1)


def comment(p, x, y, s, t, th, lw, label="COMMENT", **kw):
    w, h = s * 0.36, s * 0.20
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=th.prop_fill, outline=th.ink, width=lw * 0.6,
           radius=s * 0.05)
    p.polygon([(x - w * 0.2, y + h / 2 - 1), (x - w * 0.35, y + h * 0.85), (x - w * 0.02, y + h / 2 - 1)],
              fill=th.prop_fill, outline=th.ink, width=lw * 0.6)
    p.line([(x - w * 0.2 + 2, y + h / 2 - lw * 0.4), (x - w * 0.02 - 2, y + h / 2 - lw * 0.4)],
           th.prop_fill, lw * 0.7, caps=False)
    for i in range(3):
        k = max(0.0, math.sin(t * 6 - i * 0.9))
        p.circle((x + (i - 1) * w * 0.22, y - k * s * 0.015), s * 0.022, fill=th.ink)
    n = min(999, int(t * 180))
    _txt(p, (x, y - h / 2 - s * 0.05), f"{label} {n}+", s * 0.045, th.accent2, th)


def save(p, x, y, s, t, th, lw, label="SAVE", **kw):
    w, h = s * 0.14, s * 0.19
    k = ease_out_back(t / 0.5)
    fill = th.accent if t > 0.9 else th.prop_fill
    p.polygon([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2 * k),
               (x, y + h * 0.2 * k), (x - w / 2, y + h / 2 * k)], fill=fill, outline=th.ink, width=lw * 0.6)
    _txt(p, (x, y + h * 0.75), label, s * 0.05, th.ink, th)
    # share arrow
    ax = x + s * 0.2
    p.line([(ax - s * 0.05, y + s * 0.05), (ax - s * 0.05, y - s * 0.0), (ax + s * 0.05, y - s * 0.03)],
           th.accent2, lw * 0.7)
    p.polygon([(ax + s * 0.08, y - s * 0.035), (ax + s * 0.035, y - s * 0.07), (ax + s * 0.045, y + s * 0.01)],
              fill=th.accent2)


def coffee(p, x, y, s, t, th, lw, **kw):
    w, h = s * 0.16, s * 0.19
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=th.accent, outline=th.ink, width=lw * 0.7,
           radius=s * 0.02)
    p.arc((x + w / 2, y), h * 0.25, 270, 90, th.ink, lw * 0.6)
    _txt(p, (x, y), "$7", s * 0.05, th.ink, th)
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1.0
        sx = x - w * 0.3 + i * w * 0.3
        p.line([(sx + math.sin(ph * 7 + i) * w * 0.1, y - h / 2 - s * 0.02 - ph * h),
                (sx + math.sin(ph * 7 + i + 1) * w * 0.1, y - h / 2 - s * 0.07 - ph * h)], th.ink, lw * 0.35)


def wall_door(p, x, y, s, t, th, lw, **kw):
    w, h = s * 0.36, s * 0.78
    p.rect(x - w / 2, y - h, x + w / 2, y, fill=th.bg2, outline=th.ink, width=lw * 0.7)
    k = 0.5 + 0.5 * math.cos(min(t, 3.0) * 1.2)
    dw = w * (0.15 + 0.85 * k)
    p.rect(x - w / 2, y - h, x - w / 2 + dw, y, fill=th.prop_fill, outline=th.ink, width=lw * 0.6)
    p.circle((x - w / 2 + dw * 0.85, y - h * 0.48), s * 0.014, fill=th.ink)


def phone(p, x, y, s, t, th, lw, **kw):
    w, h = s * 0.20, s * 0.36
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=(30, 30, 38), outline=th.ink, width=lw * 0.6,
           radius=s * 0.03)
    p.rect(x - w * 0.42, y - h * 0.42, x + w * 0.42, y + h * 0.40, fill=(225, 238, 255))
    for i in range(min(4, int(t * 2.5) + 1)):
        ny = y - h * 0.35 + i * h * 0.17
        p.rect(x - w * 0.36, ny, x + w * 0.36, ny + h * 0.12, fill=(255, 255, 255), outline=(150, 150, 160),
               width=0.6, radius=s * 0.01)
        p.circle((x - w * 0.27, ny + h * 0.06), s * 0.012, fill=th.bad if i % 2 else th.accent2)
    badge = min(99, int(t * 37) + 1)
    p.circle((x + w / 2, y - h / 2), s * 0.035, fill=th.bad)
    p.text((x + w / 2, y - h / 2), str(badge), s * 0.03, (255, 255, 255), anchor="mm")


def fire(p, x, y, s, t, th, lw, **kw):
    for layer, (col, sc) in enumerate(((th.bad, 1.0), ((255, 150, 30), 0.72), (th.accent, 0.45))):
        pts = [(x - s * 0.18 * sc, y)]
        for i in range(7):
            fx = x - s * 0.18 * sc + (i + 0.5) * s * 0.36 * sc / 7
            fh = s * (0.25 + 0.12 * math.sin(t * 9 + i * 1.7 + layer)) * sc
            pts.append((fx, y - fh if i % 2 == 0 else y - fh * 0.55))
        pts.append((x + s * 0.18 * sc, y))
        p.polygon(pts, fill=col)


def mic(p, x, y, s, t, th, lw, **kw):
    p.line([(x, y), (x, y - s * 0.35)], th.ink, lw * 0.6)
    p.line([(x - s * 0.08, y), (x + s * 0.08, y)], th.ink, lw * 0.8)
    draw_mic(p, x, y - s * 0.40, s, 0, th.ink, th, lw)


def battery(p, x, y, s, t, th, lw, **kw):
    w, h = s * 0.34, s * 0.16
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=th.prop_fill, outline=th.ink, width=lw * 0.8,
           radius=s * 0.02)
    p.rect(x + w / 2, y - h * 0.22, x + w / 2 + s * 0.025, y + h * 0.22, fill=th.ink)
    level = max(0.01, 0.8 - t * 0.35)
    col = th.good if level > 0.4 else th.accent if level > 0.15 else th.bad
    if level > 0.05 or int(t * 4) % 2 == 0:
        p.rect(x - w / 2 + s * 0.015, y - h / 2 + s * 0.015, x - w / 2 + s * 0.015 + (w - s * 0.03) * level,
               y + h / 2 - s * 0.015, fill=col)
    _txt(p, (x, y + h), f"{int(level * 100)}%", s * 0.06, col, th, stroke=s * 0.004)


def calendar(p, x, y, s, t, th, lw, label="MONDAY", **kw):
    w, h = s * 0.30, s * 0.30
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, fill=th.prop_fill, outline=th.ink, width=lw * 0.7,
           radius=s * 0.02)
    p.rect(x - w / 2, y - h / 2, x + w / 2, y - h / 4, fill=th.bad, outline=th.ink, width=lw * 0.7)
    _txt(p, (x, y - h * 0.375), label, s * 0.045, (255, 255, 255), th)
    _txt(p, (x, y + h * 0.1), str(1 + int(t * 3) % 31), s * 0.11, th.ink, th)


def dumbbell(p, x, y, s, t, th, lw, **kw):
    lift = abs(math.sin(t * 2.5)) * s * 0.03
    yy = y - s * 0.05 - lift
    p.line([(x - s * 0.16, yy), (x + s * 0.16, yy)], th.ink, lw * 0.9)
    for sx in (-1, 1):
        p.rect(x + sx * s * 0.16 - s * 0.03, yy - s * 0.07, x + sx * s * 0.16 + s * 0.03, yy + s * 0.07,
               fill=th.ink, radius=s * 0.01)
    _txt(p, (x, yy - s * 0.12), "200kg", s * 0.05, th.bad, th)


def cart(p, x, y, s, t, th, lw, **kw):
    w, h = s * 0.32, s * 0.18
    top = y - s * 0.30
    p.line([(x - w * 0.75, top - s * 0.04), (x - w / 2, top)], th.ink, lw * 0.7)
    p.polygon([(x - w / 2, top), (x + w / 2, top), (x + w * 0.4, top + h), (x - w * 0.4, top + h)],
              fill=th.prop_fill, outline=th.ink, width=lw * 0.7)
    rnd = random.Random(3)
    for i in range(min(9, int(t * 5) + 2)):
        bx = x + rnd.uniform(-w * 0.35, w * 0.35)
        by = top - rnd.uniform(0, s * 0.12)
        col = rnd.choice([th.bad, th.accent, th.good, th.accent2])
        p.rect(bx - s * 0.025, by - s * 0.035, bx + s * 0.025, by + s * 0.035, fill=col, outline=th.ink,
               width=lw * 0.3)
    for sx in (-1, 1):
        p.circle((x + sx * w * 0.3, y - s * 0.04), s * 0.035, fill=th.ink)


PROPS = {
    "desk": (desk, "front"),
    "laptop": (laptop, "front"),
    "chart_up": (chart_up, "side"),
    "chart_down": (chart_down, "side"),
    "clock": (clock, "above_side"),
    "question": (question, "above"),
    "exclamation": (exclamation, "above"),
    "bulb": (bulb, "above"),
    "money": (money, "rain"),
    "coins": (coins, "side"),
    "subscribe": (subscribe, "cta"),
    "like": (like, "cta"),
    "comment": (comment, "cta"),
    "save": (save, "cta"),
    "bell": (bell, "above_side"),
    "coffee": (coffee, "side"),
    "wall_door": (wall_door, "back"),
    "phone": (phone, "side"),
    "fire": (fire, "side_floor"),
    "mic": (mic, "side_floor"),
    "battery": (battery, "side"),
    "calendar": (calendar, "above_side"),
    "dumbbell": (dumbbell, "side_floor"),
    "cart": (cart, "side_floor"),
}

PROP_NAMES = list(PROPS.keys())
