"""Spring-damped camera path computed over the whole timeline.

The narration planner produces *target* camera keyframes; a slightly under-damped spring
follows them, giving natural inertia and a tiny settle/overshoot. Hard cuts (targets that
jump in one frame) are detected and snapped, and reported as whip-pan events."""
from __future__ import annotations

import math

import numpy as np


class CameraPath:
    def __init__(self, tr, total, fps=30, omega=7.5, zeta=0.78, handheld=0.0025, width=1080):
        n = int(math.ceil(total * fps)) + 2
        self.fps = fps
        tf = np.array([tr.get("cam_f", k / fps) for k in range(n)], np.float64)
        tz = np.log(np.array([tr.get("cam_z", k / fps) for k in range(n)], np.float64))
        f = np.zeros_like(tf)
        z = np.zeros_like(tz)
        p, v = tf[0].copy(), np.zeros(3)
        pz, vz = tz[0], 0.0
        dt = 1.0 / fps
        self.cuts = []
        for k in range(n):
            vis = width / math.exp(tz[k])                       # visible width in world units
            if k > 0 and (np.linalg.norm(tf[k] - tf[k - 1]) > 0.35 * vis or abs(tz[k] - tz[k - 1]) > 0.35):
                p, v, pz, vz = tf[k].copy(), np.zeros(3), tz[k], 0.0   # hard cut
                self.cuts.append(k / fps)
            for _ in range(4):
                h = dt / 4
                a = omega * omega * (tf[k] - p) - 2 * zeta * omega * v
                v += a * h
                p += v * h
                az = omega * omega * (tz[k] - pz) - 2 * zeta * omega * vz
                vz += az * h
                pz += vz * h
            f[k], z[k] = p, pz
        # handheld micro drift (smooth noise), proportional to the visible width
        tt = np.arange(n) / fps
        vis = width / np.exp(z)
        for ax, (a1, a2) in enumerate(((0.31, 0.73), (0.47, 0.91), (0.23, 0.61))):
            f[:, ax] += handheld * vis * (np.sin(tt * a1 * 2 * math.pi + ax) * 0.6 + np.sin(tt * a2 * 2 * math.pi) * 0.4)
        self.f, self.logz = f, z
        # screen-space speed (fraction of frame width per frame) for motion blur / DOF
        sp = np.zeros(n)
        sp[1:] = np.linalg.norm(np.diff(f, axis=0), axis=1) / vis[1:] + np.abs(np.diff(z)) * 0.6
        self.speed = sp

    def _idx(self, t):
        x = t * self.fps
        k = int(max(0, min(len(self.f) - 2, math.floor(x))))
        return k, x - k

    def at(self, t):
        k, a = self._idx(t)
        f = self.f[k] * (1 - a) + self.f[k + 1] * a
        z = math.exp(self.logz[k] * (1 - a) + self.logz[k + 1] * a)
        return tuple(f), z

    def speed_at(self, t):
        k, _ = self._idx(t)
        return float(self.speed[k])

    def whip_amount(self, t, half=0.14):
        best = 0.0
        for c in self.cuts:
            dd = abs(t - c)
            if dd < half:
                best = max(best, 1 - dd / half)
        return best
