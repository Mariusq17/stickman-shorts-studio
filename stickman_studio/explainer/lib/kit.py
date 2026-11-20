"""Scene kit: small helpers shared by explainer scenes (backgrounds, mascot adapter, billboards,
moving packets along paths, glowing rings, flat sheets moving along a path).

    from .lib import kit
    self.bg = kit.gradient_bg(W, H, (228, 238, 250), (250, 246, 238), clouds=6)
    kit.peg(cam, (x, y, 0), PEG_COLORS[0], "happy", t, floor=FLOOR)
    kit.label(cam, (x, y, z), "YOUR BANK", 0.16, INK)
    kit.packet(cam, PATH, s, (60, 140, 255))            # glowing dot travelling along a polyline
    kit.strip(cam, PATH, s, 0.5, (120, 190, 120))       # a sheet (banknote, ticket) seen edge-on
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw

from ...painter import font
from .characters import draw_peg as _draw_peg
from .palette import INK, mix


def _shade(c, k):
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c)
    return tuple(int(v * (1 + k)) for v in c)


def gradient_bg(W, H, top, bot, clouds=0, seed=1, cloud_color=(255, 255, 255)):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = np.array(top, np.float32) * (1 - y) + np.array(bot, np.float32) * y
    img = Image.fromarray(np.broadcast_to(arr, (H, W, 3)).astype(np.uint8))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(clouds):
        cx, cy, r = rnd.uniform(0, W), rnd.uniform(0.05 * H, 0.5 * H), rnd.uniform(0.04, 0.08) * W
        for dx, rr in ((-1, 0.7), (0, 1.0), (1, 0.8)):
            d.ellipse((cx + dx * r - rr * r, cy - rr * r * 0.6, cx + dx * r + rr * r, cy + rr * r * 0.6),
                      fill=cloud_color)
    return img


def peg(cam, xyz, color, expr="neutral", t=0.0, scale=1.9, look=(0.0, 0.0), seed=0, pose=None, react=0.0,
        floor=None, hat=False):
    """Pegs mascot with a default pose per expression and an optional contact shadow."""
    if scale <= 0.02:
        return
    if pose is None:
        pose = {"shocked": "panic", "worried": "hold", "happy": "cheer" if seed % 2 else "wave",
                "angry": "hold", "smug": "idle"}.get(expr, "idle")
    if floor is not None:
        x, y = cam.p(*xyz)
        r = 0.30 * cam.s * scale * 0.62
        cam.d.ellipse((x - r, y - r * 0.24, x + r, y + r * 0.24), fill=_shade(floor, -0.22))
    _draw_peg(cam, xyz, color, expr, pose, t, scale, look, react, seed, hat)


def label(cam, xyz, text, size, fg=INK, bg=(255, 255, 255), pad=0.35, outline=None):
    """Billboard text with a rounded plate, size in world units (scales with zoom)."""
    x, y = cam.p(*xyz)
    f = font(int(size * cam.s))
    tw = cam.d.textlength(text, font=f)
    h = size * cam.s
    p = h * pad
    cam.d.rounded_rectangle((x - tw / 2 - p * 1.4, y - h / 2 - p, x + tw / 2 + p * 1.4, y + h / 2 + p),
                            radius=h * 0.35, fill=bg, outline=outline or _shade(bg, -0.35),
                            width=max(1, int(0.01 * cam.s)))
    cam.d.text((x, y), text, font=f, fill=fg, anchor="mm")


def path_point(pts, s):
    """Point at fraction s (0..1) of a 3D polyline (by length) + unit tangent."""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg) or 1.0
    d = min(max(s, 0.0), 1.0) * total
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if d <= L or L == seg[-1] and b == pts[-1]:
            k = d / L if L else 0.0
            tan = tuple((b[i] - a[i]) / (L or 1) for i in range(3))
            return tuple(a[i] + (b[i] - a[i]) * k for i in range(3)), tan
        d -= L
    a, b = pts[-2], pts[-1]
    L = seg[-1] or 1
    return pts[-1], tuple((b[i] - a[i]) / L for i in range(3))


def sub_path(pts, s0, s1, n=12):
    return [path_point(pts, s0 + (s1 - s0) * k / n)[0] for k in range(n + 1)]


def glow_dot(cam, xyz, r, color):
    x, y = cam.p(*xyz)
    rr = r * cam.s
    for k, a in ((2.4, 0.15), (1.7, 0.35)):
        cam.d.ellipse((x - rr * k, y - rr * k, x + rr * k, y + rr * k), fill=mix((255, 255, 255), color, a))
    cam.d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color, outline=_shade(color, -0.4),
                  width=max(1, int(0.008 * cam.s)))


def packet(cam, pts, s, color, r=0.09, trail=0.12):
    """Glowing data packet travelling along a polyline (s = 0..1), with a fading trail."""
    if s <= 0.0 or s >= 1.0:
        return
    tr = sub_path(pts, max(0.0, s - trail), s, 8)
    for k in range(len(tr) - 1):
        a = k / len(tr)
        cam.line([tr[k], tr[k + 1]], mix((255, 255, 255), color, 0.25 + 0.6 * a), r * (0.4 + 0.9 * a), caps=False)
    glow_dot(cam, path_point(pts, s)[0], r, color)


def cable(cam, pts, color=(70, 76, 92), width=0.035, lit=0.0, lit_color=(90, 170, 255)):
    cam.line(pts, _shade(color, -0.3), width * 1.3)
    cam.line(pts, mix(color, lit_color, lit), width)


def strip(cam, pts, s, length, color, width=0.035, double=0.0):
    """A thin sheet (banknote, ticket, card) seen edge-on, centred at fraction s of the path.
    double > 0 draws a second sheet stuck to it (offset perpendicular in z)."""
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg) or 1.0
    h = length / 2 / total
    p = sub_path(pts, s - h, s + h, 6)
    if double > 0:
        q = [(x, y, z + double) for x, y, z in p]
        cam.line(q, _shade(color, -0.45), width * 1.4, caps=False)
        cam.line(q, _shade(color, -0.05), width, caps=False)
    cam.line(p, _shade(color, -0.45), width * 1.4, caps=False)
    cam.line(p, color, width, caps=False)


def rings(cam, center, axis, r0, r1, t, color, n=4, speed=0.6, width=0.02, bg=(255, 255, 255), offset=None):
    """Expanding rings (radio/magnetic field) in the plane normal to `axis`.
    offset(f) -> (dx, dy, dz) lets the rings also travel (e.g. away from an antenna)."""
    for k in range(n):
        f = ((t * speed) + k / n) % 1.0
        r = r0 + (r1 - r0) * f
        c = center if offset is None else tuple(center[i] + offset(f)[i] for i in range(3))
        col = mix(color, bg, f * 0.85)
        cam.poly(cam.disc_pts(c, r, axis, 40), None, col, width * (1.2 - 0.6 * f))


def plate(cam, plane, c, u0, v0, u1, v1, color, outline=None, width=0.008):
    """Flat rectangle on a wall plane ('x', 'y') or floor ('z')."""
    def P(u, v):
        if plane == "y":
            return (u, c, v)
        if plane == "x":
            return (c, u, v)
        return (u, v, c)
    cam.poly([P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)], color, outline, width if outline else 0)


def plane_text(cam, plane, c, u, v, text, size, color):
    """Text centred on a wall point (screen-aligned, sized in world units)."""
    xyz = (u, c, v) if plane == "y" else ((c, u, v) if plane == "x" else (u, v, c))
    x, y = cam.p(*xyz)
    cam.d.text((x, y), text, font=font(int(size * cam.s)), fill=color, anchor="mm")
