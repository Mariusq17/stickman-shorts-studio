"""Isometric 2.5D drawing primitives: shaded boxes, discs, ropes, springs, billboards."""
from __future__ import annotations

import math

from PIL import ImageDraw

from ..painter import font

C30 = math.cos(math.radians(30))
S30 = 0.5


def shade(c, k):
    """k>0 lighten, k<0 darken."""
    if k >= 0:
        return tuple(int(v + (255 - v) * k) for v in c)
    return tuple(int(v * (1 + k)) for v in c)


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


ISO_YAW, ISO_PITCH = 45.0, math.degrees(math.atan(1 / math.sqrt(2)))     # classic isometric view
ISO_K = 1.0 / math.cos(math.radians(ISO_PITCH))                          # keeps the historical scale


class IsoCam:
    """Orthographic camera. Default yaw/pitch = the classic isometric view used by every video (identical
    output). yaw 45 -> 0 swings the camera round to look straight at the +y face (e.g. through a door);
    pitch lowers/raises the eye. Scenes draw the top, +y and +x faces, so keep yaw in [0, 90] and
    pitch in [5, 60] for the painter's order to stay right."""

    def __init__(self, img, focus=(0, 0, 0), zoom=100.0, anchor=(0, 0), yaw=ISO_YAW, pitch=ISO_PITCH):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.f = focus
        self.s = zoom
        self.a = anchor
        self.yaw, self.pitch = yaw, pitch
        if abs(yaw - ISO_YAW) < 1e-6 and abs(pitch - ISO_PITCH) < 1e-6:
            self._m = None
        else:
            ps, pc = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
            es, ec = math.sin(math.radians(pitch)), math.cos(math.radians(pitch))
            k = ISO_K
            # right = (cos yaw, -sin yaw, 0); up = (-sin(p) sin(yaw), -sin(p) cos(yaw), cos(p))
            self._m = (pc * k, -ps * k, es * ps * k, es * pc * k, ec * k)

    # world -> screen
    def p(self, x, y, z):
        x, y, z = x - self.f[0], y - self.f[1], z - self.f[2]
        if self._m is None:
            return (self.a[0] + (x - y) * C30 * self.s, self.a[1] + ((x + y) * S30 - z) * self.s)
        a, b, c, d, e = self._m
        return (self.a[0] + (a * x + b * y) * self.s, self.a[1] + (c * x + d * y - e * z) * self.s)

    def w(self, width):
        return max(1, int(round(width * self.s)))

    # -------------------------------------------------------------- shapes
    def poly(self, pts3, fill=None, outline=None, width=0.0):
        pts = [self.p(*q) for q in pts3]
        self.d.polygon(pts, fill=fill, outline=outline, width=self.w(width) if outline else 0)

    def line(self, pts3, color, width, caps=True):
        pts = [self.p(*q) for q in pts3]
        wp = self.w(width)
        self.d.line(pts, fill=color, width=wp, joint="curve")
        if caps and wp > 2:
            r = wp / 2
            for x, y in (pts[0], pts[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def box(self, x, y, z, w, d, h, color, outline=True, faces="tlr", top_color=None):
        """Axis-aligned box from min corner. Visible faces: top, left (max y), right (max x)."""
        x1, y1, z1 = x + w, y + d, z + h
        oc = shade(color, -0.45) if outline else None
        ow = 0.012 if outline else 0
        if "l" in faces:   # face at y = y1
            self.poly([(x, y1, z), (x1, y1, z), (x1, y1, z1), (x, y1, z1)], shade(color, -0.05), oc, ow)
        if "r" in faces:   # face at x = x1
            self.poly([(x1, y, z), (x1, y1, z), (x1, y1, z1), (x1, y, z1)], shade(color, -0.22), oc, ow)
        if "t" in faces:
            self.poly([(x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1)], top_color or shade(color, 0.18), oc, ow)

    def disc_pts(self, c, r, axis="x", n=36, rot=0.0):
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n + rot
            u, v = math.cos(a) * r, math.sin(a) * r
            if axis == "x":
                pts.append((c[0], c[1] + u, c[2] + v))
            elif axis == "y":
                pts.append((c[0] + u, c[1], c[2] + v))
            else:
                pts.append((c[0] + u, c[1] + v, c[2]))
        return pts

    def wheel(self, c, r, thick, color, axis="x", angle=0.0, spokes=5, groove=None):
        off = {"x": (thick, 0, 0), "y": (0, thick, 0), "z": (0, 0, thick)}[axis]
        back = (c[0] - off[0] / 2, c[1] - off[1] / 2, c[2] - off[2] / 2)
        front = (c[0] + off[0] / 2, c[1] + off[1] / 2, c[2] + off[2] / 2)
        self.poly(self.disc_pts(back, r, axis), shade(color, -0.35), shade(color, -0.55), 0.01)
        # rim band
        pb, pf = self.disc_pts(back, r, axis, 24), self.disc_pts(front, r, axis, 24)
        for i in range(24):
            j = (i + 1) % 24
            self.poly([pb[i], pb[j], pf[j], pf[i]], shade(color, -0.25))
        self.poly(self.disc_pts(front, r, axis), color, shade(color, -0.5), 0.012)
        if groove:
            self.poly(self.disc_pts(front, r * 0.86, axis), groove)
            self.poly(self.disc_pts(front, r * 0.74, axis), color)
        for k in range(spokes):
            a = angle + 2 * math.pi * k / spokes
            tip = self.disc_pts(front, r * 0.68, axis, 1, a)[0]
            self.line([front, tip], shade(color, -0.4), r * 0.12)
        self.poly(self.disc_pts(front, r * 0.18, axis, 16), shade(color, -0.45))

    def spring(self, base, h, r, color, coils=6, width=0.03):
        pts = []
        n = coils * 12
        for i in range(n + 1):
            a = 2 * math.pi * i / 12
            pts.append((base[0] + math.cos(a) * r, base[1] + math.sin(a) * r, base[2] + h * i / n))
        self.line(pts, color, width)

    def text(self, xyz, s, size, fill, stroke=0.0, stroke_fill=(255, 255, 255), anchor="mm"):
        x, y = self.p(*xyz)
        self.d.text((x, y), s, font=font(int(size * self.s)), fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.s), stroke_fill=stroke_fill)
