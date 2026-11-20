"""Soft projected shadows + ambient occlusion for the isometric renderer.

Shadows are drawn into a low-resolution mask, blurred and then used to tint the frame
with a cool shadow colour - cheap and very soft (no hard aliasing)."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from .palette import SHADOW

LIGHT = (-0.42, -0.30, -0.86)    # direction the light travels (from front-right-top)


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


class ShadowLayer:
    def __init__(self, cam, scale=4, light=LIGHT):
        self.cam = cam
        self.k = scale
        W, H = cam.img.size
        self.mask = Image.new("L", (W // scale, H // scale), 0)
        self.d = ImageDraw.Draw(self.mask)
        self.L = light

    def _scr(self, p):
        x, y = self.cam.p(*p)
        return (x / self.k, y / self.k)

    def poly(self, pts3, value=255):
        self.d.polygon([self._scr(p) for p in pts3], fill=value)

    def box_on_plane(self, x, y, z, w, d, h, axis, c, value=255, clip=None):
        """Shadow of a box projected along the light onto plane axis=c ('x','y' or 'z')."""
        ai = "xyz".index(axis)
        L = self.L
        if abs(L[ai]) < 1e-6:
            return
        out = []
        for cx in (x, x + w):
            for cy in (y, y + d):
                for cz in (z, z + h):
                    p = [cx, cy, cz]
                    s = (c - p[ai]) / L[ai]
                    if s < 0:
                        s = 0
                    q = [p[0] + s * L[0], p[1] + s * L[1], p[2] + s * L[2]]
                    if clip:
                        q = [min(max(q[j], clip[j][0]), clip[j][1]) for j in range(3)]
                    out.append(self._scr(q))
        hull = _hull(out)
        if len(hull) >= 3:
            self.d.polygon(hull, fill=value)

    def ao_edge(self, a, b, normal_a, normal_b, width=0.35, value=120):
        """Ambient occlusion along an inside corner from a to b (two faces meeting)."""
        for n in (normal_a, normal_b):
            pts = [a, b, tuple(b[i] + n[i] * width for i in range(3)), tuple(a[i] + n[i] * width for i in range(3))]
            self.poly(pts, value)

    def apply(self, img, opacity=0.32, blur=3.0, color=SHADOW):
        m = self.mask.filter(ImageFilter.GaussianBlur(blur))
        m = m.resize(img.size, Image.BILINEAR).point(lambda v: int(v * opacity))
        img.paste(color, (0, 0, img.width, img.height), m)
