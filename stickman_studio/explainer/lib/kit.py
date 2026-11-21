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


def label(cam, xyz, text, size, fg=INK, bg=(255, 255, 255), pad=0.35, outline=None, now=False):
    """Billboard text with a rounded plate, size in world units (scales with zoom).
    Labels are callouts: they are queued and drawn ON TOP of the whole scene (flush_labels, called by the
    builder after scene.draw), so no object can ever hide them. now=True draws immediately."""
    if not now:
        if not hasattr(cam, "_labels"):
            cam._labels = []
        cam._labels.append((xyz, text, size, fg, bg, pad, outline))
        return
    x, y = cam.p(*xyz)
    f = font(int(size * cam.s))
    tw = cam.d.textlength(text, font=f)
    h = size * cam.s
    p = h * pad
    cam.d.rounded_rectangle((x - tw / 2 - p * 1.4, y - h / 2 - p, x + tw / 2 + p * 1.4, y + h / 2 + p),
                            radius=h * 0.35, fill=bg, outline=outline or _shade(bg, -0.35),
                            width=max(1, int(0.01 * cam.s)))
    cam.d.text((x, y), text, font=f, fill=fg, anchor="mm")


def flush_labels(cam):
    """Draw every queued label above the scene (called by the builder after scene.draw)."""
    for xyz, text, size, fg, bg, pad, outline in getattr(cam, "_labels", []):
        label(cam, xyz, text, size, fg, bg, pad, outline, now=True)
    cam._labels = []


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


def _plane_pt(plane, c, u, v):
    return (u, c, v) if plane == "y" else ((c, u, v) if plane == "x" else (u, v, c))


def plane_text(cam, plane, c, u, v, text, size, color, max_w=None, max_h=None):
    """Text printed ON a surface: centred at plane point (u, v), cap height `size` in world units,
    warped with the surface's perspective (follows the iso skew like a real label/screen).
    max_w / max_h (world units) shrink the text so it always fits inside its object.
    Planes: 'y' (wall facing +y, u = x), 'x' (wall facing +x, u = y), 'z' (floor/top, u = x, v = y).
    On 'x' walls text runs towards -y so it reads left-to-right on screen."""
    if not text or size <= 0:
        return
    px_per_unit = cam.s
    fs = max(8, int(size * px_per_unit * 1.35))
    f = font(fs)
    bbox = f.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if tw <= 0 or th <= 0:
        return
    s = size / max(1, th)                       # world units per text pixel
    if max_w is not None and tw * s > max_w:
        s = max_w / tw
    if max_h is not None and th * s > max_h:
        s = max_h / th
    pad = 2
    layer = Image.new("L", (tw + 2 * pad, th + 2 * pad), 0)
    ImageDraw.Draw(layer).text((pad - bbox[0], pad - bbox[1]), text, font=f, fill=255)
    W_, H_ = layer.size
    du = -1.0 if plane == "x" else 1.0           # reading direction along u
    o = cam.p(*_plane_pt(plane, c, u, v))
    pu = cam.p(*_plane_pt(plane, c, u + du, v))
    pv = cam.p(*_plane_pt(plane, c, u, v + (1.0 if plane != "z" else -1.0)))
    eu = (pu[0] - o[0], pu[1] - o[1])
    ev = (pv[0] - o[0], pv[1] - o[1])
    # forward: screen = o + (i - W/2)*s*eu - (j - H/2)*s*ev
    a, b = eu[0] * s, -ev[0] * s
    cc, d = eu[1] * s, -ev[1] * s
    corners = []
    for i, j in ((0, 0), (W_, 0), (W_, H_), (0, H_)):
        corners.append((o[0] + a * (i - W_ / 2) + b * (j - H_ / 2), o[1] + cc * (i - W_ / 2) + d * (j - H_ / 2)))
    x0, y0 = int(min(p[0] for p in corners)) - 1, int(min(p[1] for p in corners)) - 1
    x1, y1 = int(max(p[0] for p in corners)) + 2, int(max(p[1] for p in corners)) + 2
    if x1 - x0 < 2 or y1 - y0 < 2 or x1 < 0 or y1 < 0 or x0 > cam.img.width or y0 > cam.img.height:
        return
    det = a * d - b * cc
    if abs(det) < 1e-9:
        return
    ia, ib, ic, id_ = d / det, -b / det, -cc / det, a / det
    # inverse: (i, j) = inv * (screen - o) + (W/2, H/2), with screen = (x0 + X, y0 + Y)
    ox, oy = x0 - o[0], y0 - o[1]
    coeffs = (ia, ib, ia * ox + ib * oy + W_ / 2, ic, id_, ic * ox + id_ * oy + H_ / 2)
    mask = layer.transform((x1 - x0, y1 - y0), Image.AFFINE, coeffs, resample=Image.BILINEAR)
    cam.img.paste(tuple(color), (x0, y0, x1, y1), mask)


def sheet(cam, pts, s, length, width, color, double=0.0, outline=None, crumple=0.0):
    """A flat sheet (banknote, ticket) lying along a polyline path at fraction s, `width` across the y axis.
    double > 0 draws a second sheet stuck under it (offset along the path normal); crumple bends it."""
    p, tan = path_point(pts, s)
    nx, nz = -tan[2], tan[0]                  # normal in the x-z plane
    hl = length / 2
    oc = outline or _shade(color, -0.45)
    layers = [(double, _shade(color, -0.12))] if double > 0 else []
    layers.append((0.0, color))
    for off, col in layers:
        c = (p[0] + nx * off, p[1], p[2] + nz * off)
        a = (c[0] - tan[0] * hl, c[1], c[2] - tan[2] * hl)
        b = (c[0] + tan[0] * hl, c[1], c[2] + tan[2] * hl)
        k = crumple * hl * 0.8
        quad = [(a[0], a[1] - width / 2, a[2] + k), (b[0], b[1] - width / 2, b[2]),
                (b[0], b[1] + width / 2, b[2] - k * 0.5), (a[0], a[1] + width / 2, a[2])]
        cam.poly(quad, col, oc, 0.006)
        m = (c[0], c[1] + width / 2 - 0.001, c[2])
        x, y = cam.p(*c)
        r = width * 0.18 * cam.s
        cam.d.ellipse((x - r, y - r * 0.5, x + r, y + r * 0.5), outline=_shade(col, -0.3),
                      width=max(1, int(0.006 * cam.s)))


def path_prefix(pts, s):
    """The first fraction s (0..1, by length) of a polyline, keeping its corners (for pipes/cables that
    'grow' along their route)."""
    if s >= 1.0:
        return list(pts)
    if s <= 0.0:
        return [pts[0], pts[0]]
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    d = s * (sum(seg) or 1.0)
    out = [pts[0]]
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if d <= L:
            k = d / L if L else 0.0
            out.append(tuple(a[i] + (b[i] - a[i]) * k for i in range(3)))
            return out
        out.append(b)
        d -= L
    return out


def heat_wisps(cam, base, t, color=(255, 120, 60), n=3, h=0.6, spread=0.3, amount=1.0, width=0.02, axis="z"):
    """Wavy rising lines (heat leaving a surface). axis = direction they travel ('z' up, 'x'/'y' sideways)."""
    if amount <= 0.01:
        return
    for i in range(n):
        f = (t * 0.7 + i / n) % 1.0
        pts = []
        for j in range(8):
            q = j / 7 * 0.35
            w = 0.04 * math.sin((f + q) * 14 + i)
            off = (i - (n - 1) / 2) * spread / max(1, n - 1)
            if axis == "z":
                pts.append((base[0] + off + w, base[1] + w, base[2] + (f + q) * h))
            elif axis == "x":
                pts.append((base[0] + (f + q) * h, base[1] + off + w, base[2] + w))
            else:
                pts.append((base[0] + off + w, base[1] + (f + q) * h, base[2] + w))
        cam.line(pts, mix(color, (255, 255, 255), f * 0.8), width * amount * (1 - f * 0.6), caps=False)


def flow_line(cam, pts, t, color, width, speed=0.8, dash=0.1, amount=1.0, base=True):
    """Liquid/gas flowing inside a pipe or channel: a solid core plus light dashes travelling along the path
    (direction = order of pts). amount scales the width (0 = nothing)."""
    if amount <= 0.01 or len(pts) < 2:
        return
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    L = sum(seg) or 1.0
    if base:
        cam.line(pts, color, width * amount, caps=False)
    hi = mix(color, (255, 255, 255), 0.55)
    step = 2.5 * dash / L
    off = ((t * speed) / L) % step
    s = off - step
    while s < 1.0:
        a, b = max(0.0, s), min(1.0, s + dash / L)
        if b > a:
            cam.line(sub_path(pts, a, b, 3), hi, width * amount * 0.45, caps=False)
        s += step
