"""Drawing of the stickman figure: body, expressive face (with lip-sync) and
character-attached effects (sweat, anger, stars, thought bubbles...)."""
from __future__ import annotations

import math

from .easing import clamp, lerp
from .painter import Painter, rotate

EXPRESSIONS = ["neutral", "happy", "shocked", "angry", "sad", "smug", "deadpan",
               "mind_blown", "evil", "dizzy"]


def _blink(t: float, seed: float) -> float:
    """1 = eyes open, 0 = closed. Blink ~every 3.3 s."""
    ph = (t + seed) % 3.3
    if ph < 0.12:
        return abs(ph - 0.06) / 0.06
    return 1.0


def draw_face(p: Painter, c, r, expr, mouth_open, t, look=0.0, nod=0.0, ink=(0, 0, 0),
              accent=(255, 200, 0), bad=(230, 50, 60), angle=0.0, seed=0.0, lw=4.0,
              covered=False):
    """Draw facial features inside head of centre c, radius r (world px)."""
    cx, cy = c
    fx = cx + look * 0.32 * r
    fy = cy + nod * 0.28 * r
    rot = lambda x, y: rotate(x, y, cx, cy, angle)
    ex_off = 0.36 * r
    eye_y = fy - 0.10 * r
    blink = _blink(t, seed)
    flw = lw * 0.75
    mo = clamp(mouth_open)

    def eyes_dots(size=0.11, dy=0.0):
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y + dy * r)
            if blink < 0.5:
                p.line([(ex - size * r, ey), (ex + size * r, ey)], ink, flw)
            else:
                p.ellipse((ex, ey), size * r, size * r * blink, fill=ink)

    def brows(inner_dy, outer_dy, y0=-0.36, spread=0.20):
        for sx in (-1, 1):
            a = rot(fx + sx * (ex_off - spread * r), fy + (y0 + inner_dy) * r)
            b = rot(fx + sx * (ex_off + spread * r), fy + (y0 + outer_dy) * r)
            p.line([a, b], ink, flw)

    def mouth_talk(width=0.34, base_h=0.05, y=0.36, smile=0.0):
        mx, my = rot(fx, fy + y * r)
        h = (base_h + 0.32 * mo) * r
        if mo < 0.08 and smile == 0:
            p.line([(mx - width * r * 0.6, my), (mx + width * r * 0.6, my)], ink, flw)
        elif mo < 0.08:
            p.arc((mx, my - smile * r * 0.5), width * r * 0.8, 20 if smile > 0 else 200,
                  160 if smile > 0 else 340, ink, flw)
        else:
            p.ellipse((mx, my), width * r * 0.55, h * 0.6, fill=ink)
            if h > 0.15 * r:
                p.ellipse((mx, my + h * 0.3), width * r * 0.32, h * 0.22, fill=bad)

    if expr == "happy":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y)
            p.arc((ex, ey + 0.06 * r), 0.14 * r, 200, 340, ink, flw)
        mx, my = rot(fx, fy + 0.30 * r)
        w = 0.42 * r
        h = (0.16 + 0.22 * mo) * r
        p.polygon([(mx - w, my - 0.02 * r)] +
                  [(mx + w * math.cos(math.radians(a)), my + h * math.sin(math.radians(a)))
                   for a in range(0, 181, 15)],
                  fill=ink)
        p.ellipse((mx, my + h * 0.55), w * 0.45, h * 0.3, fill=bad)
        # blush
        for sx in (-1, 1):
            bx, by = rot(fx + sx * 0.62 * r, fy + 0.16 * r)
            p.ellipse((bx, by), 0.12 * r, 0.06 * r, fill=(255, 140, 150))
    elif expr == "shocked":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y - 0.04 * r)
            p.circle((ex, ey), 0.22 * r, fill=(255, 255, 255), outline=ink, width=flw * 0.8)
            p.circle((ex + look * 0.05 * r, ey), 0.07 * r, fill=ink)
        brows(-0.14, -0.20, y0=-0.42)
        mx, my = rot(fx, fy + 0.40 * r)
        p.ellipse((mx, my), (0.15 + 0.08 * mo) * r, (0.18 + 0.12 * mo) * r, fill=ink)
    elif expr == "angry":
        eyes_dots(0.11, 0.04)
        brows(0.12, -0.10, y0=-0.30, spread=0.22)
        mx, my = rot(fx, fy + 0.38 * r)
        w, h = 0.30 * r, (0.08 + 0.20 * mo) * r
        p.rect(mx - w, my - h, mx + w, my + h, fill=(255, 255, 255), outline=ink, width=flw * 0.8,
               radius=0.05 * r)
        p.line([(mx - w, my), (mx + w, my)], ink, flw * 0.5, caps=False)
        for i in (-1, 0, 1):
            p.line([(mx + i * w / 2, my - h), (mx + i * w / 2, my + h)], ink, flw * 0.4, caps=False)
    elif expr == "sad":
        eyes_dots(0.10, 0.06)
        brows(-0.14, 0.05, y0=-0.30)
        mx, my = rot(fx, fy + 0.46 * r)
        if mo > 0.1:
            p.ellipse((mx, my - 0.04 * r), 0.16 * r, (0.05 + 0.18 * mo) * r, fill=ink)
        else:
            p.arc((mx, my + 0.08 * r), 0.24 * r, 210, 330, ink, flw)
        tx, ty = rot(fx + ex_off + 0.05 * r, eye_y + (0.2 + (t * 0.6 % 0.6)) * r)
        p.polygon([(tx, ty - 0.1 * r), (tx - 0.06 * r, ty + 0.02 * r), (tx + 0.06 * r, ty + 0.02 * r)],
                  fill=(90, 170, 255))
        p.circle((tx, ty + 0.03 * r), 0.06 * r, fill=(90, 170, 255))
    elif expr == "smug":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y)
            p.ellipse((ex, ey + 0.03 * r), 0.12 * r, 0.06 * r, fill=ink)
            p.line([(ex - 0.16 * r, ey - 0.02 * r), (ex + 0.16 * r, ey - 0.02 * r)], ink, flw)
        a = rot(fx - ex_off - 0.18 * r, fy - 0.30 * r)
        b = rot(fx - ex_off + 0.15 * r, fy - 0.33 * r)
        p.line([a, b], ink, flw)
        a = rot(fx + ex_off - 0.15 * r, fy - 0.46 * r)
        b = rot(fx + ex_off + 0.18 * r, fy - 0.40 * r)
        p.line([a, b], ink, flw)
        mx, my = rot(fx + 0.06 * r, fy + 0.36 * r)
        if mo > 0.12:
            p.ellipse((mx, my), 0.22 * r, (0.04 + 0.2 * mo) * r, fill=ink)
        else:
            p.line([(mx - 0.25 * r, my + 0.02 * r), (mx + 0.05 * r, my + 0.03 * r),
                    (mx + 0.25 * r, my - 0.09 * r)], ink, flw)
    elif expr == "deadpan":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y)
            p.line([(ex - 0.15 * r, ey), (ex + 0.15 * r, ey)], ink, flw * 1.2)
            p.ellipse((ex, ey + 0.05 * r), 0.07 * r, 0.04 * r, fill=ink)
        mouth_talk(width=0.36, base_h=0.02, y=0.38)
    elif expr == "mind_blown":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y)
            pts = []
            for i in range(28):
                a = i * 0.55 + t * 9 * sx
                rr = 0.012 * r * i
                pts.append((ex + rr * math.cos(a), ey + rr * math.sin(a)))
            p.line(pts, ink, flw * 0.6)
        mx, my = rot(fx, fy + 0.42 * r)
        p.ellipse((mx, my), (0.2 + 0.05 * mo) * r, (0.2 + 0.1 * mo) * r, fill=ink)
    elif expr == "evil":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y + 0.03 * r)
            p.ellipse((ex, ey), 0.12 * r, 0.07 * r, fill=bad)
        brows(0.16, -0.12, y0=-0.30, spread=0.24)
        mx, my = rot(fx, fy + 0.30 * r)
        w = 0.46 * r
        h = (0.18 + 0.15 * mo) * r
        p.polygon([(mx - w, my - 0.06 * r), (mx + w, my - 0.06 * r), (mx, my + h)],
                  fill=(255, 255, 255), outline=ink, width=flw * 0.7)
        for i in (-2, -1, 0, 1, 2):
            p.line([(mx + i * w / 3, my - 0.06 * r),
                    (mx + i * w / 3 * 0.8, my + h * (1 - abs(i) / 3.2) * 0.8)], ink, flw * 0.4,
                   caps=False)
    elif expr == "dizzy":
        for sx in (-1, 1):
            ex, ey = rot(fx + sx * ex_off, eye_y)
            s = 0.12 * r
            p.line([(ex - s, ey - s), (ex + s, ey + s)], ink, flw)
            p.line([(ex - s, ey + s), (ex + s, ey - s)], ink, flw)
        mx, my = rot(fx, fy + 0.40 * r)
        p.line([(mx - 0.25 * r, my), (mx - 0.1 * r, my - 0.06 * r), (mx + 0.05 * r, my + 0.04 * r),
                (mx + 0.25 * r, my - 0.03 * r)], ink, flw)
    else:  # neutral
        eyes_dots(0.11)
        brows(0.0, 0.0, y0=-0.38)
        mouth_talk(width=0.34, base_h=0.04, y=0.36, smile=0.12)


def draw_stickman(p: Painter, sk, ink, face_fill, expression, mouth_open, t, fx=None,
                  theme=None, lw=None, seed=0.0, hand_props=None):
    fx = fx or {}
    U = sk.unit
    lw = lw or U * 0.028
    pts = sk.pts
    hc, hr = sk.head_c, sk.head_r
    pose = sk.pose
    prof = clamp(pose.get("profile", 0.0))
    facing = 1 if pose.get("facing", 1) >= 0 else -1

    def foot_tip(side):
        fx_, fy_ = pts[side + "_foot"]
        out = (-1 if side == "l" else 1) * (1 - prof) + facing * prof
        return (fx_ + out * U * 0.055, fy_ + U * 0.004)

    def skeleton(color, w, head_w):
        for side in ("l", "r"):
            p.line([pts["hip"], pts[side + "_knee"], pts[side + "_foot"], foot_tip(side)], color, w)
        p.line([pts["hip"], pts["neck"]], color, w)
        if head_w:
            p.circle(hc, hr + head_w / 2, fill=color)

    halo = getattr(theme, "bg", None)
    if halo is not None:      # thin background-colored outline: reads well over any decor
        skeleton(halo, lw * 1.9, lw * 1.0)
        for side in ("l", "r"):
            p.line([pts["neck"], pts[side + "_elbow"], pts[side + "_hand"]], halo, lw * 1.9)
    skeleton(ink, lw, 0)
    # head
    p.circle(hc, hr, fill=face_fill, outline=ink, width=lw * 0.85)
    expr = expression
    if fx.get("stars"):
        expr = "dizzy"
    accent = theme.accent if theme else (255, 200, 0)
    bad = theme.bad if theme else (230, 50, 60)
    if expression == "mind_blown":
        _mind_blown_fx(p, hc, hr, t, accent, bad, lw)
    draw_face(p, hc, hr, expr, mouth_open, t, look=sk.pose.get("look", 0.0) + 0.55 *
              sk.pose.get("profile", 0) * (1 if sk.pose.get("facing", 1) >= 0 else -1),
              nod=sk.pose.get("nod", 0.0), ink=ink, accent=accent, bad=bad,
              angle=sk.head_angle * 0.6, seed=seed, lw=lw)
    # arms (after head so hands can cover the face)
    for side in ("l", "r"):
        p.line([pts["neck"], pts[side + "_elbow"], pts[side + "_hand"]], ink, lw)
        hand_r = lw * (1.9 if fx.get("palm") == side else 0.9)
        p.circle(pts[side + "_hand"], hand_r, fill=ink)
    # character effects
    if fx.get("sweat"):
        for i in range(2):
            ph = (t * 1.6 + i * 0.5) % 1.0
            sx = hc[0] + (1 if i == 0 else -1) * hr * (1.05 + 0.25 * ph)
            sy = hc[1] - hr * 0.3 + hr * ph * 1.2
            p.polygon([(sx, sy - hr * 0.22), (sx - hr * 0.1, sy), (sx + hr * 0.1, sy)],
                      fill=(110, 190, 255))
            p.circle((sx, sy + hr * 0.02), hr * 0.1, fill=(110, 190, 255))
    if fx.get("anger"):
        ax, ay = hc[0] + hr * 0.75, hc[1] - hr * 0.85
        s = hr * 0.25 * (1 + 0.15 * math.sin(t * 20))
        for a in (45, 135, 225, 315):
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            p.line([(ax + dx * s * 0.3, ay + dy * s * 0.3), (ax + dx * s, ay + dy * s)], bad, lw * 0.8)
    if fx.get("stars"):
        for i in range(3):
            a = t * 4 + i * 2.09
            sx, sy = hc[0] + math.cos(a) * hr * 1.4, hc[1] - hr * 1.15 + math.sin(a) * hr * 0.35
            _star(p, sx, sy, hr * 0.22, accent)
    if fx.get("shock_lines") or fx.get("shake_lines"):
        k = 1.0 if fx.get("shake_lines") else clamp(1.4 - t)
        if k > 0:
            for i in range(7):
                a = math.radians(-160 + i * 23)
                r0, r1 = hr * 1.35, hr * (1.75 + 0.15 * math.sin(t * 25 + i))
                p.line([(hc[0] + math.cos(a) * r0, hc[1] + math.sin(a) * r0),
                        (hc[0] + math.cos(a) * r1, hc[1] + math.sin(a) * r1)], ink, lw * 0.6 * k + 1)
    if fx.get("thought"):
        for i in range(3):
            pulse = 0.5 + 0.5 * math.sin(t * 4 - i)
            p.circle((hc[0] + hr * (1.1 + i * 0.45), hc[1] - hr * (1.0 + i * 0.5)),
                     hr * (0.1 + 0.06 * i) * (0.8 + 0.3 * pulse), fill=face_fill, outline=ink,
                     width=lw * 0.5)
    if fx.get("speed_lines"):
        f = 1 if sk.pose.get("facing", 1) >= 0 else -1
        for i in range(4):
            y = pts["hip"][1] - U * 0.25 + i * U * 0.12
            x0 = pts["hip"][0] - f * U * (0.25 + 0.05 * i)
            ln = U * (0.12 + 0.05 * math.sin(t * 30 + i))
            p.line([(x0, y), (x0 - f * ln, y)], ink, lw * 0.45)
    # hand props
    for side, name in (hand_props or {}).items():
        draw_hand_prop(p, name, pts[side + "_hand"], U, t, theme, lw, side)


def _star(p, x, y, r, color):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    p.polygon(pts, fill=color)


def _mind_blown_fx(p, hc, hr, t, accent, bad, lw):
    k = (t * 1.5) % 1.0
    for i in range(12):
        a = math.radians(-180 + i * 15 + 7)
        r0 = hr * (1.1 + 0.9 * k)
        r1 = r0 + hr * 0.5
        col = accent if i % 2 else bad
        p.line([(hc[0] + math.cos(a) * r0, hc[1] + math.sin(a) * r0 * 1.2),
                (hc[0] + math.cos(a) * r1, hc[1] + math.sin(a) * r1 * 1.2)], col, lw * 0.9)
    p.circle((hc[0], hc[1] - hr * (1.3 + 0.8 * k)), hr * 0.25 * (1 - k) + 1, fill=accent)


def draw_hand_prop(p: Painter, name, hand, U, t, theme, lw, side="r"):
    ink = theme.ink if theme else (0, 0, 0)
    x, y = hand
    if name == "coffee":
        w, h = U * 0.075, U * 0.09
        cx = x + (w * 0.6 if side == "r" else -w * 0.6)
        p.rect(cx - w / 2, y - h * 0.6, cx + w / 2, y + h * 0.4,
               fill=theme.accent if theme else (255, 200, 0), outline=ink, width=lw * 0.6, radius=U * 0.01)
        p.arc((cx + w / 2, y - h * 0.1), w * 0.28, 270, 90, ink, lw * 0.5)
        for i in range(2):
            ph = (t * 0.8 + i * 0.5) % 1.0
            sx = cx - w * 0.15 + i * w * 0.3
            p.line([(sx + math.sin(ph * 6 + i) * w * 0.12, y - h * 0.7 - ph * h * 0.9),
                    (sx + math.sin(ph * 6 + 1 + i) * w * 0.12, y - h * 0.9 - ph * h * 0.9)],
                   ink, lw * 0.35)
    elif name == "mic":
        draw_mic(p, x, y, U, 0.0, ink, theme, lw)
    elif name == "phone":
        w, h = U * 0.06, U * 0.11
        p.rect(x - w / 2, y - h * 0.8, x + w / 2, y + h * 0.2, fill=(30, 30, 40), outline=ink,
               width=lw * 0.5, radius=U * 0.01)
        p.rect(x - w * 0.38, y - h * 0.72, x + w * 0.38, y + h * 0.1, fill=(120, 200, 255))


def draw_mic(p, x, y, U, angle, ink, theme, lw):
    L = U * 0.12
    ux, uy = math.sin(math.radians(angle)), -math.cos(math.radians(angle))
    top = (x + ux * L * 0.55, y + uy * L * 0.55)
    bot = (x - ux * L * 0.45, y - uy * L * 0.45)
    p.line([bot, top], (60, 60, 70), lw * 0.9)
    p.circle((top[0] + ux * U * 0.02, top[1] + uy * U * 0.02), U * 0.035,
             fill=(150, 150, 160), outline=ink, width=lw * 0.4)
