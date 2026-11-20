"""Keyframe tracks resolved against narration-driven step timings."""
from __future__ import annotations

from ..easing import ease_in_out_cubic, ease_out_back, ease_out_cubic, ease_in_cubic, clamp

def _smootherstep(t):
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


EASES = {"io": ease_in_out_cubic, "smooth": _smootherstep, "out": ease_out_cubic, "in": ease_in_cubic, "back": ease_out_back,
         "lin": lambda t: clamp(t)}


class Tracks:
    """keys[name] = list of (abs_time, value, duration, ease). Value transitions start at abs_time."""

    def __init__(self):
        self.keys = {}
        self.init = {}

    def set_initial(self, name, value):
        self.init[name] = value

    def add(self, name, t, value, dur=0.6, ease="io"):
        self.keys.setdefault(name, []).append((t, value, dur, ease))

    def get(self, name, t, default=0.0):
        v = self.init.get(name, default)
        for (t0, val, dur, ease) in sorted(self.keys.get(name, []), key=lambda k: k[0]):
            if t < t0:
                break
            k = 1.0 if dur <= 0 else EASES[ease]((t - t0) / dur)
            if isinstance(v, tuple):
                v = tuple(a + (b - a) * k for a, b in zip(v, val))
            else:
                v = v + (val - v) * k
        return v
