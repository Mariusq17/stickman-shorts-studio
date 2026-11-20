"""Reusable 2.5D parts for IsoCam scenes. All sizes are world units.

Planes: 'x' = face with normal +x (a wall at x=c), 'y' = normal +y, 'z' = horizontal.
"""
from __future__ import annotations

import math

from ...painter import font
from .palette import INK, mix


def _shade(c, k):
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c)
    return tuple(int(v * (1 + k)) for v in c)


def _on_plane(plane, c, u, v):
    """Map plane coordinates (u, v) to a 3D point. For 'y'/'x' planes v is height (z)."""
    if plane == "y":
        return (u, c, v)
    if plane == "x":
        return (c, u, v)
    return (u, v, c)


def bolt(cam, xyz, r=0.03, color=(150, 156, 168)):
    x, y = cam.p(*xyz)
    rr = r * cam.s
    cam.d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=_shade(color, -0.25))
    cam.d.ellipse((x - rr * 0.6, y - rr * 0.75, x + rr * 0.5, y + rr * 0.3), fill=_shade(color, 0.25))


def panel_seams(cam, plane, c, u0, u1, v0, v1, spacing=0.6, color=(180, 186, 200), width=0.008, horizontal=False):
    u = u0 + spacing
    while u < u1 - 1e-6:
        cam.line([_on_plane(plane, c, u, v0), _on_plane(plane, c, u, v1)], color, width, caps=False)
        u += spacing
    if horizontal:
        v = v0 + spacing
        while v < v1 - 1e-6:
            cam.line([_on_plane(plane, c, u0, v), _on_plane(plane, c, u1, v)], color, width, caps=False)
            v += spacing


def led(cam, xyz, color=(80, 230, 120), on=True, r=0.03, glow=True):
    x, y = cam.p(*xyz)
    rr = r * cam.s
    if on and glow:
        for k, a in ((2.6, 0.18), (1.8, 0.35)):
            cam.d.ellipse((x - rr * k, y - rr * k, x + rr * k, y + rr * k), fill=mix((255, 255, 255), color, a))
    cam.d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color if on else (70, 74, 86))


def button_panel(cam, plane, c, u, v, n=3, lit=None, color=(70, 74, 86), btn=(230, 232, 238), glow=(255, 210, 80)):
    """Vertical strip of round buttons on a wall (u = horizontal position, v = bottom height)."""
    w, h = 0.14, 0.12 + n * 0.11
    pts = [_on_plane(plane, c, u, v), _on_plane(plane, c, u + w, v), _on_plane(plane, c, u + w, v + h),
           _on_plane(plane, c, u, v + h)]
    cam.poly(pts, color, _shade(color, -0.4), 0.008)
    for i in range(n):
        x, y = cam.p(*_on_plane(plane, c, u + w / 2, v + 0.1 + i * 0.11))
        r = 0.035 * cam.s
        cam.d.ellipse((x - r, y - r, x + r, y + r), fill=glow if lit == i else btn)


def digital_display(cam, plane, c, u, v, text, w=0.36, h=0.18, color=(255, 120, 60)):
    pts = [_on_plane(plane, c, u, v), _on_plane(plane, c, u + w, v), _on_plane(plane, c, u + w, v + h),
           _on_plane(plane, c, u, v + h)]
    cam.poly(pts, (24, 26, 34), (60, 64, 76), 0.01)
    x, y = cam.p(*_on_plane(plane, c, u + w / 2, v + h / 2))
    cam.d.text((x, y), text, font=font(int(h * 0.75 * cam.s)), fill=color, anchor="mm")


def gear(cam, center, r, teeth=12, axis="y", angle=0.0, color=(150, 156, 168)):
    pts = []
    n = teeth * 4
    for i in range(n):
        a = 2 * math.pi * i / n + angle
        rr = r * (1.0 if (i // 2) % 2 == 0 else 0.84)
        u, v = math.cos(a) * rr, math.sin(a) * rr
        if axis == "y":
            pts.append((center[0] + u, center[1], center[2] + v))
        elif axis == "x":
            pts.append((center[0], center[1] + u, center[2] + v))
        else:
            pts.append((center[0] + u, center[1] + v, center[2]))
    cam.poly(pts, color, _shade(color, -0.45), 0.012)
    cam.poly(cam.disc_pts(center, r * 0.35, axis, 18), _shade(color, -0.25))
    cam.poly(cam.disc_pts(center, r * 0.12, axis, 12), _shade(color, -0.5))


def pipe(cam, pts3, r=0.06, color=(120, 170, 220)):
    cam.line(pts3, _shade(color, -0.35), r * 2.2)
    cam.line(pts3, color, r * 1.8)
    hl = [(p[0], p[1], p[2] + r * 0.45) for p in pts3]
    cam.line(hl, _shade(color, 0.45), r * 0.5)


def fan(cam, center, r, axis="y", angle=0.0, color=(90, 96, 110)):
    cam.poly(cam.disc_pts(center, r, axis, 28), _shade(color, -0.3), _shade(color, -0.5), 0.01)
    for k in range(5):
        a = angle + 2 * math.pi * k / 5
        p1 = cam.disc_pts(center, r * 0.85, axis, 1, a)[0]
        p2 = cam.disc_pts(center, r * 0.85, axis, 1, a + 0.5)[0]
        cam.poly([center, p1, p2], _shade(color, 0.2))
    cam.poly(cam.disc_pts(center, r * 0.18, axis, 12), _shade(color, -0.5))


def screen(cam, plane, c, u, v, w, h, color=(60, 140, 255), t=0.0, lines=4):
    pts = [_on_plane(plane, c, u, v), _on_plane(plane, c, u + w, v), _on_plane(plane, c, u + w, v + h),
           _on_plane(plane, c, u, v + h)]
    cam.poly(pts, (24, 26, 34), (60, 64, 76), 0.012)
    m = 0.04
    cam.poly([_on_plane(plane, c, u + m, v + m), _on_plane(plane, c, u + w - m, v + m),
              _on_plane(plane, c, u + w - m, v + h - m), _on_plane(plane, c, u + m, v + h - m)], color)
    for i in range(lines):
        ln = (0.3 + 0.6 * abs(math.sin(i * 1.7 + int(t * 5) * 0.9))) * (w - 3 * m)
        vv = v + h - m * 2.2 - i * (h - 3 * m) / max(1, lines)
        cam.line([_on_plane(plane, c, u + m * 2, vv), _on_plane(plane, c, u + m * 2 + ln, vv)], (255, 255, 255),
                 0.012, caps=False)


def crate(cam, x, y, z, w, d, h, color=(196, 150, 96)):
    cam.box(x, y, z, w, d, h, color)
    for k in (1, 2):
        zz = z + h * k / 3
        cam.line([(x, y + d, zz), (x + w, y + d, zz)], _shade(color, -0.35), 0.01, caps=False)
        cam.line([(x + w, y, zz), (x + w, y + d, zz)], _shade(color, -0.45), 0.01, caps=False)


def light_panel(cam, x, y, z, w, d, color=(255, 248, 225)):
    """Ceiling light seen from below/above as a glowing quad."""
    cam.poly([(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)], color, mix(color, INK, 0.2), 0.006)
