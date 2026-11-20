"""Easing curves used for smooth, cartoony motion."""
from __future__ import annotations

import math


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def linear(t: float) -> float:
    return clamp(t)


def ease_in_quad(t: float) -> float:
    t = clamp(t)
    return t * t


def ease_out_quad(t: float) -> float:
    t = clamp(t)
    return 1 - (1 - t) * (1 - t)


def ease_in_out_sine(t: float) -> float:
    t = clamp(t)
    return -(math.cos(math.pi * t) - 1) / 2


def ease_in_cubic(t: float) -> float:
    t = clamp(t)
    return t * t * t


def ease_out_cubic(t: float) -> float:
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_back(t: float, s: float = 1.70158) -> float:
    t = clamp(t)
    c3 = s + 1
    return 1 + c3 * (t - 1) ** 3 + s * (t - 1) ** 2


def ease_out_elastic(t: float) -> float:
    t = clamp(t)
    if t in (0.0, 1.0):
        return t
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def ease_out_bounce(t: float) -> float:
    t = clamp(t)
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1:
        return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def pulse(t: float, freq: float) -> float:
    """Smooth 0..1 pulse."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * freq * t)


def smooth_noise(t: float, seed: int = 0) -> float:
    """Cheap deterministic smooth noise in [-1, 1]."""
    return (math.sin(t * 1.7 + seed * 12.9898) * 0.5
            + math.sin(t * 3.1 + seed * 78.233) * 0.3
            + math.sin(t * 5.3 + seed * 3.17) * 0.2)
