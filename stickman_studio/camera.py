"""Dynamic camera moves: zoom_in, zoom_out, pan_left/right, dramatic shake,
punch_in. Returned values are interpreted by the Painter transform."""
from __future__ import annotations

import math

from .easing import clamp, ease_in_out_cubic, ease_out_back, ease_out_cubic, smooth_noise

CAMERA_MOVES = ["static", "zoom_in", "zoom_out", "pan_left", "pan_right",
                "dramatic_camera_shake", "punch_in"]


def camera_state(move: str, t: float, d: float, W: int, H: int, focus_pt, energy: float = 1.0,
                 center=None, zoom_scale: float = 1.0):
    """Returns (focus, zoom, shake) where focus is the world point that should
    appear at the default anchor (screen centre-ish)."""
    d = max(d, 0.1)
    p = clamp(t / d)
    fx, fy = focus_pt           # interesting point (character chest/head)
    cx, cy = center if center else (W / 2, H / 2)
    zoom, shake = 1.0, (0.0, 0.0)
    tx, ty = cx, cy
    if move == "zoom_in":
        k = ease_in_out_cubic(p)
        zoom = 1.0 + 0.32 * k
        tx, ty = cx + (fx - cx) * k * 0.9, cy + (fy - cy) * k * 0.9
    elif move == "zoom_out":
        k = ease_out_cubic(p)
        zoom = 1.35 - 0.35 * k
        tx, ty = cx + (fx - cx) * (1 - k) * 0.9, cy + (fy - cy) * (1 - k) * 0.9
    elif move in ("pan_left", "pan_right"):
        k = ease_in_out_cubic(p)
        sgn = -1 if move == "pan_left" else 1
        zoom = 1.12
        tx = cx + (fx - cx) * 0.5 + sgn * (k - 0.5) * W * 0.12
        ty = cy + (fy - cy) * 0.3
    elif move == "dramatic_camera_shake":
        decay = math.exp(-2.2 * t) * 0.85 + 0.15
        amp = W * 0.018 * energy * decay
        shake = (amp * smooth_noise(t * 9, 1), amp * smooth_noise(t * 9, 2))
        zoom = 1.0 + 0.18 * ease_out_back(t / 0.25) * (0.75 + 0.25 * decay)
        tx, ty = cx + (fx - cx) * 0.6, cy + (fy - cy) * 0.6
    elif move == "punch_in":
        k = ease_out_back(t / 0.22)
        zoom = 1.0 + 0.28 * k
        tx, ty = cx + (fx - cx) * 0.85 * clamp(k), cy + (fy - cy) * 0.85 * clamp(k)
    else:  # static: subtle Ken-Burns drift keeps the frame alive
        zoom = 1.0 + 0.035 * p
        tx, ty = cx + (fx - cx) * 0.1 * p, cy + (fy - cy) * 0.1 * p
    zoom = 1.0 + (zoom - 1.0) * zoom_scale
    return (tx, ty), zoom, shake
