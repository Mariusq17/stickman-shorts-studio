"""Channel branding + per-video covers for "How It's Built", rendered with the explainer engine.

  python -m stickman_studio.explainer.branding avatar               # publishing/brand/avatar.png
  python -m stickman_studio.explainer.branding banner               # publishing/brand/banner.png
  python -m stickman_studio.explainer.branding cover <slug>         # publishing/<slug>/cover.png

Covers use COVERS[slug] (time, optional camera override, title lines). Add an entry for every new video
(see the `publish-kit` skill)."""
from __future__ import annotations

import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ..painter import font
from .iso import IsoCam
from .lib import kit, parts
from .lib.palette import PEG_COLORS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PUB = os.path.join(ROOT, "publishing")

BRAND = "HOW IT'S BUILT"
TAGLINE = "How things really work, built step by step"
ORANGE = PEG_COLORS[0]
INK = (28, 30, 40)
YELLOW = (255, 206, 70)

# slug -> dict(t=seconds, cam=((focus), zoom) or None, lines=[(text, colour)...])
COVERS = {
    "elevator": dict(t=79.0, cam=None, lines=[("WHY ELEVATORS", (255, 255, 255)), ("ALMOST NEVER FALL", YELLOW)]),
    "card_tap": dict(t=19.0, cam=((2.35, 0.9, 1.5), 260),
                     lines=[("THIS CARD HAS", (255, 255, 255)), ("NO BATTERY", YELLOW), ("SO HOW DOES IT PAY?", (255, 255, 255))]),
    "chatbot": dict(t=55.5, cam=((-2.6, 0.9, 1.0), 165),
                    lines=[("HOW AI WRITES", (255, 255, 255)), ("ONE WORD", YELLOW), ("AT A TIME", YELLOW)]),
    "traffic_light": dict(t=20.0, cam=((-2.4, 0.4, 0.5), 200),
                          lines=[("HOW THE LIGHT", (255, 255, 255)), ("KNOWS YOU'RE", YELLOW), ("WAITING", YELLOW)]),
    "microwave": dict(t=74.0, cam=((0.85, 0.35, 1.45), 380),
                      lines=[("WHY FORKS", (255, 255, 255)), ("SPARK", YELLOW), ("IN MICROWAVES", (255, 255, 255))]),
    "self_checkout": dict(t=38.5, cam=((1.9, 0.5, 1.15), 280),
                          lines=[("WHO'S JUDGING YOU", (255, 255, 255)), ("AT SELF-CHECKOUT?", YELLOW)]),
    "undersea_cable": dict(t=27.0, cam=((1.0, 1.2, -1.2), 100),
                           lines=[("HOW YOUR MESSAGE", (255, 255, 255)), ("CROSSES THE OCEAN", YELLOW)]),
    "streaming": dict(t=42.0, cam=((4.0, 1.6, 1.4), 260),
                      lines=[("WHY MOVIES START", (255, 255, 255)), ("INSTANTLY", YELLOW)]),
    "atm_notes": dict(t=44.5, cam=((0.75, 1.3, 0.95), 360),
                      lines=[("HOW AN ATM KNOWS", (255, 255, 255)), ("2 NOTES ARE STUCK", YELLOW)]),
    "fridge": dict(t=40.5, cam=((0.9, 0.8, 1.7), 215),
                   lines=[("YOUR FRIDGE", (255, 255, 255)), ("CAN'T MAKE COLD", YELLOW)]),
    "toilet": dict(t=57.0, cam=((1.1, 0.9, 0.9), 250),
                   lines=[("A TOILET HAS", (255, 255, 255)), ("NO PUMP", YELLOW), ("SO HOW DOES IT FLUSH?", (255, 255, 255))]),
    "gps": dict(t=44.0, cam=((0.3, 0.4, 2.2), 105),
                lines=[("YOUR PHONE NEVER", (255, 255, 255)), ("TALKS TO GPS", YELLOW)]),
    "touchscreen": dict(t=39.0, cam=((1.0, 1.9, 0.7), 260),
                        lines=[("YOUR SCREEN", (255, 255, 255)), ("CAN'T FEEL", YELLOW), ("YOU PRESS", YELLOW)]),
    "airbag": dict(t=31.0, cam=((1.6, 0.75, 1.0), 250),
                   lines=[("YOUR AIRBAG IS A", (255, 255, 255)), ("TINY EXPLOSION", YELLOW)]),
}


def _gradient(W, H, top, bot):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = np.array(top, np.float32) * (1 - y) + np.array(bot, np.float32) * y
    return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).astype(np.uint8))


def _fit_font(draw, text, max_w, size):
    while size > 20:
        f = font(size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return font(size)


def title_block(img, lines, y0, max_w_frac=0.9, size_frac=0.115, gap=0.12):
    """Big stacked cover title: bold, thick dark stroke, auto-fit to width. Returns bottom y."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    y = y0
    for text, col in lines:
        f = _fit_font(d, text, W * max_w_frac, int(W * size_frac))
        sw = max(4, int(f.size * 0.11))
        d.text((W / 2, y), text, font=f, fill=col, anchor="mt", stroke_width=sw, stroke_fill=INK)
        y += f.size * (1 + gap)
    return y


# ------------------------------------------------------------------ avatar
def avatar(out=None, size=1080):
    out = out or os.path.join(PUB, "brand", "avatar.png")
    ss = 2
    S = size * ss
    img = _gradient(S, S, (255, 214, 120), (255, 150, 70))
    d = ImageDraw.Draw(img)
    # soft rings (blueprint feel), centre stays clean for the circular crop
    for k, r in enumerate((0.47, 0.40)):
        d.ellipse((S / 2 - S * r, S / 2 - S * r, S / 2 + S * r, S / 2 + S * r), outline=(255, 236, 190),
                  width=int(S * 0.008))
    cam = IsoCam(img, (0, 0, 0), S / 1080 * 260, (S * 0.5, S * 0.78))
    parts.gear(cam, (-0.55, -0.6, 1.25), 0.55, 12, "y", 0.3, (90, 110, 150))
    parts.gear(cam, (0.75, -0.9, 1.75), 0.35, 10, "y", 0.0, (60, 140, 220))
    cam.box(-0.75, -0.2, 0, 1.5, 0.9, 0.18, (70, 78, 100))
    kit.peg(cam, (0.0, 0.25, 0.18), ORANGE, "happy", 0.35, 3.0, (0.0, -0.2), seed=1, pose="wave")
    # tiny hard hat
    hx, hy = cam.p(0.0, 0.25, 0.18 + 0.52 * 3.0 * 0.86)
    r = 0.30 * 3.0 * cam.s * 0.5
    d.chord((hx - r * 1.05, hy - r * 0.95, hx + r * 1.05, hy + r * 0.75), 180, 360, fill=YELLOW, outline=INK,
            width=int(S * 0.006))
    d.rectangle((hx - r * 1.25, hy - r * 0.12, hx + r * 1.25, hy + r * 0.02), fill=YELLOW, outline=INK,
                width=int(S * 0.006))
    img = img.resize((size, size), Image.LANCZOS)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    return out


# ------------------------------------------------------------------ banner
def banner(out=None):
    """YouTube banner 2560x1440; everything important inside the 1546x423 safe area (centre)."""
    out = out or os.path.join(PUB, "brand", "banner.png")
    W, H = 2560, 1440
    img = _gradient(W, H, (40, 52, 90), (28, 34, 60))
    d = ImageDraw.Draw(img)
    # blueprint grid
    for x in range(0, W, 64):
        d.line((x, 0, x, H), fill=(52, 66, 110), width=2)
    for y in range(0, H, 64):
        d.line((0, y, W, y), fill=(52, 66, 110), width=2)
    sx0, sx1 = (W - 1546) / 2, (W + 1546) / 2
    sy0, sy1 = (H - 423) / 2, (H + 423) / 2
    # side machines: inside the desktop band (full width, 423 px high), outside the all-devices area
    cam = IsoCam(img, (0, 0, 0), 95, ((sx0) / 2 + 20, sy1 - 30))
    parts.server_rack(cam, -0.9, -0.4, 0, 0.6, 0.7, 2.6, 1.0, busy=0.7)
    parts.server_rack(cam, -0.1, -0.4, 0, 0.6, 0.7, 3.0, 2.0, busy=0.7, seed=2)
    cam = IsoCam(img, (0, 0, 0), 95, ((sx1 + W) / 2 - 10, sy1 - 40))
    parts.bank_building(cam, -0.8, -0.7, 1.6, 1.4, 2.3, (225, 228, 238), (120, 128, 150), 0.0, 0.6)
    parts.gear(cam, (1.3, -0.5, 2.9), 0.45, 12, "y", 0.2, (255, 180, 70))
    # all-devices safe area (1546 x 423): mascot + title, with margins
    m = 40
    peg_h = 423 - 2 * m
    scale = 2.3
    zoom = peg_h / (0.52 * scale * 1.15)
    cam = IsoCam(img, (0, 0, 0), zoom, (sx0 + m + 0.22 * zoom * scale, sy1 - m - 0.02 * zoom))
    kit.peg(cam, (0, 0, 0), ORANGE, "happy", 0.4, scale, (0.4, -0.2), seed=1, pose="wave")
    tx = sx0 + m + 0.62 * zoom * scale
    max_w = sx1 - m - tx
    ft = _fit_font(d, BRAND, max_w, 150)
    fs = _fit_font(d, TAGLINE, max_w, 64)
    block = ft.size + 24 + fs.size
    ty = (sy0 + sy1) / 2 - block / 2
    d.text((tx, ty), BRAND, font=ft, fill=(255, 255, 255), stroke_width=max(4, ft.size // 15), stroke_fill=INK)
    d.text((tx, ty + ft.size + 24), TAGLINE, font=fs, fill=YELLOW)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    return out


# ------------------------------------------------------------------ covers
def cover(slug, out=None, spec=None, ss=2):
    """Vertical 1080x1920 cover: a clean scene frame (no keywords/pop-ups) + a big title.
    Title sits inside the centre 3:4 area so it survives the Instagram grid crop."""
    from .builder import build_explainer
    from .lib.camera import CameraPath
    from .lib.kit import flush_labels
    from .lib.post import Post
    from .videos import load
    v = load(slug)
    spec = spec or COVERS[slug]
    plan = build_explainer(v["steps"], v["scene"], None, v["initial"], v.get("overlays"), ss=1, return_plan=True,
                           log=lambda m: None)
    tr, total, starts = plan["tracks"], plan["total"], plan["starts"]
    W, H = 1080, 1920
    t = min(total - 0.05, spec["t"])
    f, z = spec["cam"] if spec.get("cam") else CameraPath(tr, total, 30, width=W).at(t)
    scene = v["scene"](W * ss, H * ss)
    img = scene.bg.copy()
    cam = IsoCam(img, f, z * ss, (W * ss / 2, H * ss * 0.60))
    i = tr.step_at(t)
    scene.draw(img, cam, tr, t, i, t - starts[i])
    flush_labels(cam)
    if v.get("overlays"):
        v["overlays"](img, tr, t, W * ss, H * ss)
    img = img.reduce(ss)
    img = Post(W, H).grade(img)
    # darken the top for the title
    shade = Image.new("L", (1, H))
    for y in range(H):
        shade.putpixel((0, y), int(170 * max(0.0, 1 - y / (H * 0.52)) ** 1.4))
    img.paste((20, 22, 34), (0, 0, W, H), shade.resize((W, H)))
    title_block(img, spec["lines"], int(H * 0.17))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((W * 0.31, H * 0.105, W * 0.69, H * 0.105 + 64), radius=32, fill=ORANGE)
    d.text((W / 2, H * 0.105 + 32), BRAND, font=font(36), fill=(255, 255, 255), anchor="mm")
    out = out or os.path.join(PUB, slug, "cover.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["avatar", "banner", "cover", "all"])
    ap.add_argument("slugs", nargs="*")
    a = ap.parse_args(argv)
    if a.what in ("avatar", "all"):
        print(avatar())
    if a.what in ("banner", "all"):
        print(banner())
    if a.what in ("cover", "all"):
        for s in (a.slugs or list(COVERS)):
            print(cover(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
