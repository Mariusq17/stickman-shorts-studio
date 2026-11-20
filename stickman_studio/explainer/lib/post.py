"""Post-processing at output resolution: grade, vignette, DOF edge blur, motion blur,
whip-pan transitions and a vintage film look."""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageChops, ImageFilter


def _curve(x, contrast=0.12, lift=4, gain=1.0):
    x = x / 255.0
    s = x + contrast * (x - 0.5) * (1 - abs(2 * x - 1))      # gentle S-curve
    return max(0, min(255, int(lift + s * (255 - lift) * gain)))


class Post:
    def __init__(self, W, H, warmth=0.03, contrast=0.12, vignette=0.16):
        self.W, self.H = W, H
        lr = [_curve(i, contrast, 6, 1.0 + warmth) for i in range(256)]
        lg = [_curve(i, contrast, 5, 1.0 + warmth * 0.4) for i in range(256)]
        lb = [_curve(i, contrast, 8, 1.0 - warmth * 0.5) for i in range(256)]
        self.lut = lr + lg + lb
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.52) / (H * 0.62)) ** 2)
        v = 1.0 - vignette * np.clip(d - 0.35, 0, 1) ** 1.6 / 0.42
        self.vig = Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)).convert("RGB")
        edge = np.clip((d - 0.30) / 0.55, 0, 1) ** 1.3
        self.edge = Image.fromarray((edge * 255).astype(np.uint8))
        rnd = np.random.default_rng(3)
        self.grain = [Image.fromarray(rnd.normal(128, 18, (H // 2, W // 2)).clip(0, 255).astype(np.uint8))
                      .resize((W, H)) for _ in range(4)]

    def grade(self, img):
        return ImageChops.multiply(img.point(self.lut), self.vig)

    def dof(self, img, strength):
        """Blur the frame edges (shallow depth of field feel for close-ups)."""
        if strength <= 0.02:
            return img
        W, H = self.W, self.H
        small = img.resize((W // 6, H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2))
        blur = small.resize((W, H), Image.BILINEAR)
        mask = self.edge.point(lambda v: int(v * min(1.0, strength)))
        return Image.composite(blur, img, mask)

    def whip(self, img, k, direction=1):
        """Directional smear for whip-pan cuts. k in 0..1."""
        if k <= 0.02:
            return img
        W, H = self.W, self.H
        f = max(2, int(4 + 60 * k))
        smear = img.resize((max(8, W // f), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
        out = Image.blend(img, smear, min(1.0, k * 1.15))
        if k > 0.75:
            out = Image.blend(out, Image.new("RGB", out.size, (255, 255, 255)), (k - 0.75) * 1.4)
        return out

    def film(self, img, t, amount=1.0):
        """Old-film look: grain, flicker, scratches."""
        g = self.grain[int(t * 24) % 4]
        out = ImageChops.overlay(img, Image.merge("RGB", (g, g, g))) if amount > 0 else img
        out = Image.blend(img, out, 0.55 * amount)
        flick = 1.0 + 0.05 * math.sin(t * 47) * amount
        out = out.point(lambda v: min(255, int(v * flick)))
        rnd = random.Random(int(t * 12))
        from PIL import ImageDraw
        d = ImageDraw.Draw(out)
        for _ in range(2):
            x = rnd.uniform(0, self.W)
            d.line((x, 0, x + rnd.uniform(-8, 8), self.H), fill=(235, 225, 200), width=1)
        return out


def average(images):
    """Motion blur: average several sub-frame renders."""
    acc = np.zeros((images[0].height, images[0].width, 3), np.float32)
    for im in images:
        acc += np.asarray(im, np.float32)
    return Image.fromarray((acc / len(images)).astype(np.uint8))
