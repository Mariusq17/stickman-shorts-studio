"""'Pegs' v2 - original mascots: rounded capsule bodies, big eyes, stubby arms.

draw_peg(cam, xyz, color, expr, pose, t, ...)
  expr : neutral | happy | shocked | worried | angry | smug | proud
  pose : idle | wave | cheer | panic | cover | point | think | hold | shrug
  look : (-1..1, -1..1) where the eyes look
  react: 0..1 reaction impulse (jump + stretch), e.g. right after something happens
Drawn as a billboard at the projected world position; works with any IsoCam-like camera
(needs .p(x,y,z), .s, .d)."""
from __future__ import annotations

import math

from .palette import INK


def _shade(c, k):
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c)
    return tuple(int(v * (1 + k)) for v in c)


POSES = {
    #        (left arm, right arm) angle from straight down, degrees (outward/up positive)
    "idle": (14, 14), "hold": (55, 55), "point": (14, 92), "wave": (14, 150), "cheer": (152, 152),
    "panic": (140, 140), "shrug": (100, 100), "cover": None, "think": None,
}


def draw_peg(cam, xyz, color, expr="neutral", pose="idle", t=0.0, scale=1.0, look=(0.0, 0.0), react=0.0,
             seed=0, hat=False, shadow=None, facing=1):
    d = cam.d
    s = cam.s * scale
    bx, by = cam.p(*xyz)
    lw = max(1, int(0.014 * s))
    outline = _shade(color, -0.42)
    # idle breathing, reaction jump + squash/stretch
    br = math.sin(t * 2.1 + seed * 1.7)
    jump = math.sin(min(1.0, react) * math.pi) * 0.12 * s if react > 0 else 0.0
    stretch = 1.0 + 0.10 * react - 0.02 * br * 0.5
    squash = 1.0 / math.sqrt(stretch)
    if expr in ("shocked",) and pose == "panic":
        bx += math.sin(t * 38 + seed) * 0.012 * s
    w, h = 0.30 * s * squash, 0.52 * s * stretch
    x0, x1 = bx - w / 2, bx + w / 2
    y1 = by - jump
    y0 = y1 - h
    if shadow is not None:
        k = 1.0 - 0.5 * (jump / (0.12 * s + 1e-6)) if jump else 1.0
        shadow.d.ellipse(((bx - w * 0.6 * k) / shadow.k, (by - w * 0.14) / shadow.k,
                          (bx + w * 0.6 * k) / shadow.k, (by + w * 0.14) / shadow.k), fill=200)
    # body
    d.rounded_rectangle((x0, y0, x1, y1), radius=w / 2, fill=color, outline=outline, width=lw)
    d.rounded_rectangle((x0 + w * 0.62, y0 + h * 0.14, x1 - w * 0.08, y1 - h * 0.10), radius=w * 0.16,
                        fill=_shade(color, -0.10))
    d.ellipse((x0 + w * 0.14, y0 + h * 0.08, x0 + w * 0.36, y0 + h * 0.20), fill=_shade(color, 0.5))
    # face
    ey = y0 + h * 0.34
    er = w * (0.19 if expr == "shocked" else 0.155)
    lx, ly = look
    blink = ((t * 1.0 + seed * 0.83) % 3.6) < 0.11 and expr != "shocked"
    lid = {"smug": 0.45, "angry": 0.25, "proud": 0.3}.get(expr, 0.0)
    for sx in (-1, 1):
        cx = bx + sx * w * 0.205
        if blink:
            d.arc((cx - er, ey - er * 0.6, cx + er, ey + er * 0.6), 20, 160, fill=INK, width=lw + 1)
            continue
        d.ellipse((cx - er, ey - er, cx + er, ey + er), fill=(255, 255, 255), outline=_shade(INK, 0.2), width=lw)
        pr = er * (0.34 if expr == "shocked" else 0.48)
        px, py = cx + lx * er * 0.42, ey + ly * er * 0.42
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(22, 24, 34))
        d.ellipse((px - pr * 0.25 + pr * 0.35, py - pr * 0.55, px + pr * 0.3 + pr * 0.35, py - pr * 0.05),
                  fill=(255, 255, 255))
        if lid > 0:
            d.chord((cx - er - 1, ey - er - 1, cx + er + 1, ey + er + 1), 180, 360, fill=color)
            d.line((cx - er, ey - er * (1 - 2 * lid) * 0.2, cx + er, ey - er * (1 - 2 * lid) * 0.2),
                   fill=outline, width=lw)
    # brows
    bwid = max(1, int(0.022 * s))
    tilt = {"worried": -0.55, "shocked": -0.25, "angry": 0.6, "smug": 0.15, "happy": -0.1}.get(expr, 0.0)
    lift = {"shocked": 1.6, "worried": 1.35, "happy": 1.35}.get(expr, 1.3)
    for sx in (-1, 1):
        cx = bx + sx * w * 0.205
        inner = (cx - sx * er * 0.85, ey - er * lift + tilt * er * 0.5)
        outer = (cx + sx * er * 0.85, ey - er * lift - tilt * er * 0.3)
        d.line((inner, outer), fill=(50, 34, 30), width=bwid)
    # mouth
    my = y0 + h * 0.60
    mw = w * 0.22
    mouth = (70, 24, 34)
    if expr == "shocked":
        d.ellipse((bx - mw * 0.45, my - mw * 0.35, bx + mw * 0.45, my + mw * 0.65), fill=mouth)
    elif expr in ("happy", "proud"):
        d.chord((bx - mw, my - mw * 0.55, bx + mw, my + mw * 0.95), 0, 180, fill=mouth)
        d.chord((bx - mw * 0.5, my + mw * 0.2, bx + mw * 0.5, my + mw * 0.9), 0, 180, fill=(235, 110, 120))
        for sx in (-1, 1):
            d.ellipse((bx + sx * w * 0.33 - w * 0.07, my - mw * 0.35, bx + sx * w * 0.33 + w * 0.07, my - mw * 0.05),
                      fill=_shade(color, -0.0) if False else (255, 150, 150))
    elif expr == "worried":
        pts = [(bx - mw * 0.7 + i * mw * 0.35, my + mw * 0.25 + (0.12 if i % 2 else -0.12) * mw) for i in range(5)]
        d.line(pts, fill=mouth, width=bwid, joint="curve")
    elif expr == "smug":
        d.arc((bx - mw * 0.4, my - mw * 0.4, bx + mw * 1.0, my + mw * 0.5), 20, 140, fill=mouth, width=bwid)
    elif expr == "angry":
        d.rounded_rectangle((bx - mw * 0.6, my, bx + mw * 0.6, my + mw * 0.35), radius=mw * 0.15, fill=mouth)
    else:
        d.arc((bx - mw * 0.5, my - mw * 0.3, bx + mw * 0.5, my + mw * 0.45), 30, 150, fill=mouth, width=bwid)
    # sweat drop
    if expr in ("worried",) or pose == "panic":
        ph = (t * 0.9 + seed * 0.3) % 1.0
        sx, sy = x1 - w * 0.02, y0 + h * (0.15 + 0.25 * ph)
        r = w * 0.07
        d.polygon([(sx, sy - r * 1.8), (sx - r, sy), (sx + r, sy)], fill=(120, 190, 255))
        d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(120, 190, 255))
    # arms
    arm_w = max(2, int(0.05 * s))
    hand_r = 0.052 * s
    sh_y = y0 + h * 0.56
    wav = math.sin(t * 9 + seed) * 22
    shake = math.sin(t * 30 + seed) * 12
    for side in (-1, 1):
        shx = bx + side * w * 0.47
        if pose == "cover":
            hx, hy = bx + side * w * 0.2, ey + er * 0.2
        elif pose == "think" and side == 1:
            hx, hy = bx + w * 0.15, my + mw * 0.6
        else:
            ang = (POSES.get(pose) or POSES["idle"])[0 if side < 0 else 1]
            if pose == "wave" and side == 1:
                ang += wav
            if pose == "panic":
                ang += shake * side
            if pose in ("idle", "hold"):
                ang += br * 3
            if pose == "point":
                side_dir = facing
                if side != side_dir:
                    ang = 14
            a = math.radians(ang)
            L = 0.22 * s
            hx = shx + side * math.sin(a) * L
            hy = sh_y + math.cos(a) * L
        mx_, my_ = (shx + hx) / 2 + side * 0.02 * s, (sh_y + hy) / 2 + 0.01 * s
        d.line([(shx, sh_y), (mx_, my_), (hx, hy)], fill=outline, width=arm_w + 2, joint="curve")
        d.line([(shx, sh_y), (mx_, my_), (hx, hy)], fill=color, width=arm_w, joint="curve")
        d.ellipse((hx - hand_r, hy - hand_r, hx + hand_r, hy + hand_r), fill=color, outline=outline, width=lw)
    if hat:
        hx0, hx1 = bx - w * 0.32, bx + w * 0.32
        d.rectangle((hx0, y0 - h * 0.30, hx1, y0 + h * 0.03), fill=(35, 35, 40))
        d.rectangle((bx - w * 0.52, y0 - h * 0.01, bx + w * 0.52, y0 + h * 0.05), fill=(35, 35, 40))
        d.rectangle((hx0, y0 - h * 0.07, hx1, y0 - h * 0.01), fill=(170, 40, 50))
    if expr == "shocked" and react > 0.2:
        d.text((bx + w * 0.55, y0 - h * 0.05), "!", fill=(232, 64, 72),
               font=__import__("stickman_studio.painter", fromlist=["font"]).font(int(0.22 * s)), anchor="mm")
