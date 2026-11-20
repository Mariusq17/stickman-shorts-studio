"""'Pegs' - original mascot characters: rounded capsules with big googly eyes.
Drawn as billboards at a projected world position so they live inside the 2.5D scene."""
from __future__ import annotations

import math

from .iso import shade

PEG_COLORS = [(255, 170, 60), (90, 170, 255), (120, 210, 130), (240, 110, 140), (180, 140, 255)]


def draw_peg(cam, xyz, color, expr="neutral", t=0.0, scale=1.0, look=(0.0, 0.0), hat=False, seed=0):
    d = cam.d
    s = cam.s * scale
    bx, by = cam.p(*xyz)                    # feet position
    bob = math.sin(t * 2.2 + seed) * 0.012 * s
    if expr in ("shocked", "panic"):
        bob += math.sin(t * 40 + seed) * 0.01 * s
    w, h = 0.30 * s, 0.50 * s
    x0, y0, x1, y1 = bx - w / 2, by - h + bob, bx + w / 2, by + bob
    r = w * 0.5
    # shadow
    d.ellipse((bx - w * 0.55, by - w * 0.12, bx + w * 0.55, by + w * 0.12), fill=(0, 0, 0, 60) if False else
              shade(color, -0.75))
    d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=color, outline=shade(color, -0.45),
                        width=max(1, int(0.012 * s)))
    d.rounded_rectangle((x1 - w * 0.28, y0 + h * 0.12, x1 - w * 0.06, y1 - h * 0.12), radius=w * 0.1,
                        fill=shade(color, -0.12))
    d.ellipse((x0 + w * 0.12, y0 + h * 0.10, x0 + w * 0.32, y0 + h * 0.22), fill=shade(color, 0.45))
    # eyes
    ey = y0 + h * 0.36
    er = w * (0.20 if expr in ("shocked", "panic") else 0.16)
    lx, ly = look
    blink = ((t + seed * 0.7) % 3.4) < 0.1 and expr not in ("shocked", "panic")
    for sx in (-1, 1):
        cx = bx + sx * w * 0.2
        if blink:
            d.line((cx - er, ey, cx + er, ey), fill=(30, 30, 40), width=max(1, int(0.02 * s)))
            continue
        d.ellipse((cx - er, ey - er, cx + er, ey + er), fill=(255, 255, 255), outline=(40, 40, 50),
                  width=max(1, int(0.01 * s)))
        pr = er * (0.32 if expr in ("shocked", "panic") else 0.45)
        px, py = cx + lx * er * 0.4, ey + ly * er * 0.4
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(25, 25, 35))
    # brows
    bw = max(1, int(0.016 * s))
    if expr in ("worried", "shocked", "panic"):
        for sx in (-1, 1):
            cx = bx + sx * w * 0.2
            d.line((cx - er * sx * -0.9, ey - er * 1.25, cx + er * sx * 0.9, ey - er * 1.55), fill=(40, 30, 30), width=bw)
    elif expr == "angry":
        for sx in (-1, 1):
            cx = bx + sx * w * 0.2
            d.line((cx - er * sx * 0.9, ey - er * 1.5, cx + er * sx * 0.9, ey - er * 1.1), fill=(40, 30, 30), width=bw)
    # mouth
    my = y0 + h * 0.62
    mw = w * 0.22
    if expr in ("shocked", "panic"):
        d.ellipse((bx - mw * 0.45, my - mw * 0.3, bx + mw * 0.45, my + mw * 0.6), fill=(60, 20, 30))
    elif expr == "happy":
        d.chord((bx - mw, my - mw * 0.6, bx + mw, my + mw * 0.9), 0, 180, fill=(60, 20, 30))
    elif expr == "worried":
        d.arc((bx - mw * 0.7, my, bx + mw * 0.7, my + mw), 200, 340, fill=(60, 20, 30), width=bw)
    else:
        d.line((bx - mw * 0.5, my + mw * 0.2, bx + mw * 0.5, my + mw * 0.2), fill=(60, 20, 30), width=bw)
    if hat:
        hx0, hx1 = bx - w * 0.32, bx + w * 0.32
        d.rectangle((hx0, y0 - h * 0.30, hx1, y0 + h * 0.02), fill=(35, 35, 40))
        d.rectangle((bx - w * 0.5, y0 - h * 0.02, bx + w * 0.5, y0 + h * 0.04), fill=(35, 35, 40))
        d.rectangle((hx0, y0 - h * 0.08, hx1, y0 - h * 0.02), fill=(170, 40, 50))
