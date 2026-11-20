"""Painter: a thin camera-aware wrapper around PIL.ImageDraw + font discovery."""
from __future__ import annotations

import math
import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

_BOLD_FONT_CANDIDATES = [
    # Windows
    "C:/Windows/Fonts/seguibl.ttf", "C:/Windows/Fonts/ariblk.ttf",
    "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    # macOS
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "DejaVuSans-Bold.ttf", "arialbd.ttf",
]


@lru_cache(maxsize=1)
def bold_font_path() -> str | None:
    here = os.path.join(os.path.dirname(__file__), "assets", "font.ttf")
    for cand in [here] + _BOLD_FONT_CANDIDATES:
        if os.path.isabs(cand) and os.path.exists(cand):
            return cand
    for cand in _BOLD_FONT_CANDIDATES:
        if not os.path.isabs(cand):
            try:
                ImageFont.truetype(cand, 10)
                return cand
            except OSError:
                pass
    windir = os.environ.get("WINDIR")
    if sys.platform.startswith("win") and windir:
        p = os.path.join(windir, "Fonts", "arialbd.ttf")
        if os.path.exists(p):
            return p
    return None


@lru_cache(maxsize=256)
def font(size: int) -> ImageFont.FreeTypeFont:
    size = max(6, int(size))
    path = bold_font_path()
    if path:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


class Painter:
    """Draws in *world* coordinates, mapped to screen by a simple camera.

    screen = (world - focus) * zoom + anchor + shake
    """

    def __init__(self, img: Image.Image, focus=(0.0, 0.0), zoom=1.0,
                 anchor=None, shake=(0.0, 0.0)):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.zoom = zoom
        self.fx, self.fy = focus
        if anchor is None:
            anchor = focus
        self.ax = anchor[0] + shake[0]
        self.ay = anchor[1] + shake[1]

    # -- coordinate helpers -------------------------------------------------
    def pt(self, x, y):
        return ((x - self.fx) * self.zoom + self.ax, (y - self.fy) * self.zoom + self.ay)

    def pts(self, seq):
        return [self.pt(x, y) for x, y in seq]

    def w(self, width):
        return max(1, int(round(width * self.zoom)))

    # -- primitives -----------------------------------------------------------
    def line(self, points, color, width, caps=True):
        sp = self.pts(points)
        wpx = self.w(width)
        if len(sp) >= 2:
            self.d.line(sp, fill=color, width=wpx, joint="curve")
        if caps:
            r = wpx / 2.0
            for (x, y) in (sp[0], sp[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def circle(self, c, r, fill=None, outline=None, width=1):
        x, y = self.pt(*c)
        rr = max(0.5, r * self.zoom)
        self.d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=fill, outline=outline,
                       width=self.w(width) if outline is not None else 0)

    def ellipse(self, c, rx, ry, fill=None, outline=None, width=1):
        x, y = self.pt(*c)
        rx, ry = max(0.5, rx * self.zoom), max(0.5, ry * self.zoom)
        self.d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=fill, outline=outline,
                       width=self.w(width) if outline is not None else 0)

    def polygon(self, points, fill=None, outline=None, width=1):
        sp = self.pts(points)
        self.d.polygon(sp, fill=fill, outline=outline,
                       width=self.w(width) if outline is not None else 0)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1, radius=0):
        a = self.pt(x0, y0)
        b = self.pt(x1, y1)
        box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
        if radius > 0:
            self.d.rounded_rectangle(box, radius=max(1, int(radius * self.zoom)), fill=fill,
                                     outline=outline,
                                     width=self.w(width) if outline is not None else 0)
        else:
            self.d.rectangle(box, fill=fill, outline=outline,
                             width=self.w(width) if outline is not None else 0)

    def arc(self, c, r, start, end, color, width):
        x, y = self.pt(*c)
        rr = max(1, r * self.zoom)
        self.d.arc((x - rr, y - rr, x + rr, y + rr), start, end, fill=color, width=self.w(width))

    def text(self, pos, s, size, fill, anchor="mm", stroke=0, stroke_fill=None):
        x, y = self.pt(*pos)
        f = font(int(size * self.zoom))
        self.d.text((x, y), s, font=f, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * self.zoom), stroke_fill=stroke_fill)


def rotate(px, py, cx, cy, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = px - cx, py - cy
    return cx + dx * ca - dy * sa, cy + dx * sa + dy * ca
