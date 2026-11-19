"""StickmanRig: articulated 2D skeleton, forward/inverse kinematics and the
library of procedural, exaggerated comedy actions."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .easing import (clamp, lerp, ease_out_back, ease_out_cubic, ease_in_cubic,
                     ease_in_out_sine, ease_in_out_cubic, ease_out_bounce, smooth_noise)

# Bone lengths as a fraction of the character unit U (~ total height).
TORSO = 0.30
NECK = 0.035
HEAD_R = 0.095
UP_ARM = 0.17
LO_ARM = 0.16
THIGH = 0.22
SHIN = 0.22

POSE_KEYS = ("torso", "head", "nod", "look", "l_up", "l_lo", "r_up", "r_lo",
             "l_th", "l_sh", "r_th", "r_sh", "x", "y", "squash", "profile", "facing")

BASE = dict(torso=0.0, head=0.0, nod=0.0, look=0.0,
            l_up=8.0, l_lo=4.0, r_up=8.0, r_lo=4.0,
            l_th=7.0, l_sh=-3.0, r_th=7.0, r_sh=-3.0,
            x=0.0, y=0.0, squash=1.0, profile=0.0, facing=1.0)


def P(**kw) -> dict:
    p = dict(BASE)
    p.update(kw)
    return p


def lerp_pose(a: dict, b: dict, t: float) -> dict:
    return {k: a[k] + (b[k] - a[k]) * t for k in POSE_KEYS}


def mirror_pose(p: dict) -> dict:
    m = dict(p)
    for a, b in (("l_up", "r_up"), ("l_lo", "r_lo"), ("l_th", "r_th"), ("l_sh", "r_sh")):
        m[a], m[b] = p[b], p[a]
    m["torso"] = -p["torso"]
    m["head"] = -p["head"]
    m["look"] = -p["look"]
    m["x"] = -p["x"]
    m["facing"] = -p["facing"]
    return m


def vec(deg: float):
    a = math.radians(deg)
    return math.sin(a), math.cos(a)


def _wrap(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


def side_signs(p: dict):
    pr, f = clamp(p["profile"]), (1.0 if p["facing"] >= 0 else -1.0)
    s_r = lerp(1.0, f, pr)
    s_l = lerp(-1.0, f, pr)
    return s_l, s_r


def ik_arm(target, torso: float, s: float, elbow: float = 1.0):
    """2-bone IK. target = (dx, dy) in U relative to the shoulder (screen axes).
    Returns (up, lo) pose angles for a limb with side sign s."""
    dx, dy = target
    d = math.hypot(dx, dy)
    d = clamp(d, abs(UP_ARM - LO_ARM) + 1e-3, UP_ARM + LO_ARM - 1e-3)
    base = math.degrees(math.atan2(dx, dy))
    cos_off = (UP_ARM ** 2 + d ** 2 - LO_ARM ** 2) / (2 * UP_ARM * d)
    off = math.degrees(math.acos(clamp(cos_off, -1, 1)))
    sgn = 1.0 if s >= 0 else -1.0
    abs_up = base + sgn * off * elbow
    ex, ey = vec(abs_up)
    ex, ey = ex * UP_ARM, ey * UP_ARM
    abs_lo = math.degrees(math.atan2(dx - ex, dy - ey))
    s = s if abs(s) > 1e-3 else 1e-3
    up = (abs_up + torso) / s
    lo = _wrap(abs_lo - abs_up) / s
    return up, lo


@dataclass
class Skeleton:
    pts: dict
    head_c: tuple
    head_r: float
    head_angle: float
    pose: dict
    unit: float


class StickmanRig:
    """Forward kinematics + automatic grounding for one stickman."""

    def __init__(self, unit: float, base_x: float, floor_y: float):
        self.U = unit
        self.base_x = base_x
        self.floor_y = floor_y

    def solve(self, p: dict) -> Skeleton:
        U = self.U
        s_l, s_r = side_signs(p)
        tor = p["torso"]
        hip = (0.0, 0.0)
        up = (math.sin(math.radians(tor)), -math.cos(math.radians(tor)))
        neck = (hip[0] + up[0] * TORSO, hip[1] + up[1] * TORSO)
        hang = tor + p["head"]
        hd = (math.sin(math.radians(hang)), -math.cos(math.radians(hang)))
        head_c = (neck[0] + hd[0] * (NECK + HEAD_R), neck[1] + hd[1] * (NECK + HEAD_R))
        pts = {"hip": hip, "neck": neck}
        for side, s in (("l", s_l), ("r", s_r)):
            a_up = -tor + s * p[side + "_up"]
            a_lo = a_up + s * p[side + "_lo"]
            e = vec(a_up)
            elbow = (neck[0] + e[0] * UP_ARM, neck[1] + e[1] * UP_ARM)
            h = vec(a_lo)
            hand = (elbow[0] + h[0] * LO_ARM, elbow[1] + h[1] * LO_ARM)
            a_th = s * p[side + "_th"]
            a_sh = s * (p[side + "_th"] + p[side + "_sh"])
            k = vec(a_th)
            knee = (hip[0] + k[0] * THIGH, hip[1] + k[1] * THIGH)
            f = vec(a_sh)
            foot = (knee[0] + f[0] * SHIN, knee[1] + f[1] * SHIN)
            pts[side + "_elbow"] = elbow
            pts[side + "_hand"] = hand
            pts[side + "_knee"] = knee
            pts[side + "_foot"] = foot
        # ground: lowest of feet/knees/hip/head bottom touches the floor
        low = max(pts["l_foot"][1], pts["r_foot"][1], pts["l_knee"][1], pts["r_knee"][1],
                  hip[1], head_c[1] + HEAD_R)
        ox = self.base_x + p["x"] * U
        oy = self.floor_y - low * U - p["y"] * U
        sq = p["squash"]
        sx = 1.0 / math.sqrt(max(sq, 0.3))
        foot_y = self.floor_y - p["y"] * U

        def tf(pt):
            X = ox + pt[0] * U
            Y = oy + pt[1] * U
            return (ox + (X - ox) * sx, foot_y - (foot_y - Y) * sq)

        world = {k: tf(v) for k, v in pts.items()}
        hc = tf(head_c)
        return Skeleton(world, hc, HEAD_R * U * (0.5 * (sq + sx)), hang, p, U)


# ---------------------------------------------------------------------------
# Actions. Each returns (pose, fx). t = seconds into the shot, d = shot
# duration, e = energy multiplier (0.6 .. 1.6).
# ---------------------------------------------------------------------------
TAU = 2 * math.pi


def a_idle_breathing(t, d, e):
    b = math.sin(TAU * t / 2.8)
    return P(torso=1.5 * b, head=2.5 * math.sin(TAU * t / 4.1), y=0.004 * (b + 1),
             l_up=8 + 2 * b, r_up=8 + 2 * b, squash=1 + 0.01 * b), {}


def a_talk(t, d, e):
    g = math.sin(TAU * 0.8 * t)
    return P(torso=2 * g, head=3 * math.sin(TAU * 0.6 * t + 1), nod=0.12 * g,
             r_up=25 + 12 * g * e, r_lo=45 + 15 * g, l_up=10, l_lo=6), {}


def a_walk(t, d, e):
    ph = TAU * 1.7 * t
    s = math.sin(ph)
    p = P(profile=1.0, facing=1.0, torso=5.0,
          l_th=26 * s * e, r_th=-26 * s * e,
          l_sh=-12 - 38 * max(0.0, math.sin(ph + 1.4)),
          r_sh=-12 - 38 * max(0.0, math.sin(ph + math.pi + 1.4)),
          l_up=-24 * s * e, r_up=24 * s * e, l_lo=28, r_lo=28,
          y=0.014 * abs(math.sin(ph)), x=lerp(-0.22, 0.18, clamp(t / max(d, 0.1))))
    return p, {}


def a_run_panic(t, d, e):
    per = 1.7
    x = 0.30 * math.sin(TAU * t / per)
    facing = 1.0 if math.cos(TAU * t / per) >= 0 else -1.0
    ph = TAU * 3.6 * t
    s = math.sin(ph)
    p = P(profile=1.0, facing=facing, torso=13 * facing,
          l_th=42 * s * e, r_th=-42 * s * e,
          l_sh=-20 - 50 * max(0.0, math.sin(ph + 1.4)),
          r_sh=-20 - 50 * max(0.0, math.sin(ph + math.pi + 1.4)),
          l_up=150 + 30 * math.sin(ph * 1.3), r_up=150 + 30 * math.sin(ph * 1.3 + 2),
          l_lo=25 * math.sin(ph * 2), r_lo=25 * math.sin(ph * 2 + 1),
          y=0.03 * abs(s), x=x)
    return p, {"sweat": True, "speed_lines": True}


def a_explain_gestures(t, d, e):
    g = math.sin(TAU * 1.1 * t)
    g2 = math.sin(TAU * 0.9 * t + 1.0)
    return P(torso=3 * g, head=4 * g2, nod=0.15 * g,
             r_up=45 + 25 * g * e, r_lo=55 + 30 * g2,
             l_up=35 + 20 * g2 * e, l_lo=45 + 30 * g,
             y=0.006 * abs(g)), {}


def a_point_at(t, d, e):
    k = ease_out_back(t / 0.35)
    poke = max(0.0, math.sin(TAU * 1.4 * t)) ** 4
    return P(r_up=lerp(10, 95, k) + 5 * poke * e, r_lo=lerp(10, -4, k),
             l_up=45, l_lo=-115, torso=5 * k, head=6 * k, look=0.6 * k,
             l_th=9, r_th=9), {}


def a_panic_hands_up(t, d, e):
    w = TAU * 7.5 * t
    return P(l_up=160 + 12 * math.sin(w) * e, r_up=160 + 12 * math.sin(w + 1.5) * e,
             l_lo=18 * math.sin(w + 0.7), r_lo=18 * math.sin(w + 2.0),
             l_th=18, r_th=18, l_sh=-34, r_sh=-34,
             y=0.035 * abs(math.sin(TAU * 2.2 * t)) * e,
             x=0.012 * math.sin(TAU * 11 * t), torso=3 * math.sin(TAU * 5 * t),
             head=5 * math.sin(TAU * 6 * t)), {"sweat": True, "shake_lines": True}


def a_facepalm(t, d, e):
    k = ease_out_back(t / 0.4)
    head_shake = 5 * math.sin(TAU * 0.9 * t) * clamp((t - 0.4) * 3)
    up, lo = ik_arm((0.03, -(NECK + HEAD_R) + 0.01), 0.0, 1.0, elbow=1.0)
    p = P(r_up=lerp(8, up, k), r_lo=lerp(4, lo, k), l_up=4, l_lo=0,
          head=head_shake, nod=0.45 * k, squash=1 - 0.03 * k, torso=-2 * k)
    return p, {"palm": "r"}


def a_type_on_laptop(t, d, e):
    j = lambda ph: 0.014 * max(0.0, math.sin(TAU * 8.5 * t + ph)) * e
    ru, rl = ik_arm((0.10, 0.30 - j(0)), 0.0, 1.0)
    lu, ll = ik_arm((-0.10, 0.30 - j(1.9)), 0.0, -1.0)
    return P(r_up=ru, r_lo=rl, l_up=lu, l_lo=ll, nod=0.38,
             head=2 * math.sin(TAU * 0.5 * t)), {"needs": ["desk", "laptop"], "glow": True}


def a_celebrate_jump(t, d, e):
    per = 0.75
    ph = (t % per) / per
    h = 0.22 * e
    y = 4 * h * ph * (1 - ph)
    land = math.exp(-((min(ph, 1 - ph)) / 0.07) ** 2)
    air = math.sin(math.pi * ph)
    return P(y=y, squash=1 - 0.13 * land + 0.06 * air,
             l_up=148 + 14 * math.sin(TAU * 2.6 * t), r_up=148 + 14 * math.sin(TAU * 2.6 * t + 1),
             l_lo=12, r_lo=12, l_th=12 + 22 * air, r_th=12 + 22 * air,
             l_sh=-45 * air, r_sh=-45 * air, head=6 * math.sin(TAU * 1.3 * t)), {"confetti": True}


def a_think_chin(t, d, e):
    tap = 0.009 * math.sin(TAU * 2 * t)
    ru, rl = ik_arm((0.035, -NECK + 0.005 + tap), 0.0, 1.0, elbow=1.0)
    lu, ll = ik_arm((0.07, 0.15), 0.0, -1.0, elbow=-1.0)
    k = ease_out_cubic(t / 0.4)
    return P(r_up=lerp(8, ru, k), r_lo=lerp(4, rl, k), l_up=lerp(8, lu, k), l_lo=lerp(4, ll, k),
             head=8 + 3 * math.sin(TAU * 0.5 * t), nod=-0.35, look=0.3,
             torso=-2), {"thought": True}


def a_argue_wildly(t, d, e):
    g = math.sin(TAU * 2.2 * t)
    return P(r_up=95 + 55 * max(0.0, g) * e, r_lo=-20 + 70 * max(0.0, g),
             l_up=95 + 55 * max(0.0, -g) * e, l_lo=-20 + 70 * max(0.0, -g),
             torso=9 * g, head=8 * math.sin(TAU * 4.4 * t), y=0.025 * abs(g),
             x=0.02 * g, l_th=12, r_th=12), {"anger": True}


def a_fall_down_dramatic(t, d, e):
    t1, t2 = 0.45, 0.8
    if t < t1:
        w = math.sin(TAU * 3 * t)
        return P(torso=12 * w, l_up=120 + 40 * w, r_up=120 - 40 * w, l_lo=30, r_lo=-30,
                 l_th=10 + 8 * w, r_th=10 - 8 * w, head=10 * w), {"sweat": True}
    lying = P(torso=-88, head=-10, l_up=150, l_lo=20, r_up=40, r_lo=30,
              l_th=-82, l_sh=-8, r_th=96, r_sh=10)
    if t < t2:
        k = ease_in_cubic((t - t1) / (t2 - t1))
        start = P(torso=12, l_up=120, r_up=120, l_th=10, r_th=10)
        return lerp_pose(start, lying, k), {}
    b = t - t2
    lying["y"] = 0.07 * (1 - ease_out_bounce(b / 0.5)) if b < 0.5 else 0.0
    lying["r_sh"] = 10 + 25 * max(0.0, math.sin(TAU * 1.3 * b)) ** 8
    return lying, {"stars": True, "impact": b < 0.25}


def a_nod_yes(t, d, e):
    g = math.sin(TAU * 2.2 * t)
    return P(nod=0.5 * g * e, y=0.006 * (g + 1), head=2 * g,
             l_up=45, l_lo=-115, r_up=45, r_lo=-115), {}


def a_shake_head_no(t, d, e):
    g = math.sin(TAU * 3.0 * t)
    ru, rl = ik_arm((-0.07, 0.13), 0.0, 1.0, elbow=1.0)
    lu, ll = ik_arm((0.07, 0.15), 0.0, -1.0, elbow=1.0)
    return P(look=0.6 * g * e, head=7 * g, r_up=ru, r_lo=rl, l_up=lu, l_lo=ll), {}


def a_shock_freeze(t, d, e):
    k = ease_out_back(t / 0.25)
    hop = 0.09 * e * math.sin(math.pi * clamp(t / 0.32))
    trem = 0.005 * math.sin(TAU * 23 * t) * clamp((t - 0.3) * 4)
    return P(y=hop, x=trem, l_up=lerp(8, 75, k), r_up=lerp(8, 75, k),
             l_lo=lerp(4, 35, k), r_lo=lerp(4, 35, k), l_th=lerp(7, 17, k), r_th=lerp(7, 17, k),
             squash=1 + 0.08 * math.sin(math.pi * clamp(t / 0.3))), {"shock_lines": True}


MIC_RELEASE = 1.1


def a_mic_drop(t, d, e):
    t_rel = min(MIC_RELEASE, 0.45 * d)
    sway = 3 * math.sin(TAU * 0.8 * t)
    if t < t_rel:
        k = ease_out_back(t / 0.35)
        ru, rl = ik_arm((0.17, 0.0), 0.0, 1.0)
        return P(r_up=lerp(8, ru, k), r_lo=lerp(4, rl, k), torso=sway,
                 l_up=45, l_lo=-115, head=-4), {"hand_prop": {"r": "mic"}}
    k = ease_in_out_cubic((t - t_rel - 0.6) / 0.5)
    ru, rl = ik_arm((0.17, 0.0), 0.0, 1.0)
    cu, cl = ik_arm((-0.07, 0.13), 0.0, 1.0)
    lu, ll = ik_arm((0.07, 0.15), 0.0, -1.0)
    return P(r_up=lerp(ru, cu, k), r_lo=lerp(rl, cl, k), l_up=lerp(45, lu, k),
             l_lo=lerp(-115, ll, k), torso=sway * (1 - k), head=-6 * k), \
        {"drop": {"prop": "mic", "t0": t_rel, "side": "r"}}


def a_sip_coffee(t, d, e):
    cyc = 3.4
    ph = t % cyc
    rest, mouth = (0.13, 0.13), (0.075, -NECK - HEAD_R + 0.045)
    if ph < 1.0:
        k = ease_in_out_sine(ph / 1.0)
    elif ph < 1.8:
        k = 1.0
    elif ph < 2.6:
        k = 1 - ease_in_out_sine((ph - 1.8) / 0.8)
    else:
        k = 0.0
    tgt = (lerp(rest[0], mouth[0], k), lerp(rest[1], mouth[1], k))
    ru, rl = ik_arm(tgt, 0.0, 1.0, elbow=1.0)
    return P(r_up=ru, r_lo=rl, head=-7 * k, nod=-0.15 * k, l_up=6, l_lo=4), \
        {"hand_prop": {"r": "coffee"}, "sipping": k > 0.85}


def a_plot_evil(t, d, e):
    tap = 0.012 * math.sin(TAU * 4 * t)
    ru, rl = ik_arm((0.035 + tap, 0.12), 0.0, 1.0)
    lu, ll = ik_arm((-0.035 - tap, 0.12), 0.0, -1.0)
    laugh = abs(math.sin(TAU * 5 * t)) * (0.5 + 0.5 * math.sin(TAU * 0.4 * t))
    return P(r_up=ru, r_lo=rl, l_up=lu, l_lo=ll, squash=0.95 + 0.02 * laugh,
             nod=0.25, torso=2.5 * math.sin(TAU * 5 * t) * e, y=0.012 * laugh,
             head=4 * math.sin(TAU * 0.7 * t)), {"evil": True}



def a_cta_point(t, d, e):
    hop = 0.025 * abs(math.sin(TAU * 1.8 * t)) * e
    k = ease_out_back(t / 0.35)
    return P(r_up=lerp(10, 125, k) + 7 * math.sin(TAU * 2.5 * t), r_lo=lerp(4, -8, k),
             l_up=30 + 10 * math.sin(TAU * 1.8 * t), l_lo=60, y=hop, torso=4 * k,
             head=7 * k, look=0.6 * k), {}


def a_wave(t, d, e):
    return P(r_up=150, r_lo=25 * math.sin(TAU * 3 * t) * e, l_up=8,
             head=5 * math.sin(TAU * 1.0 * t), y=0.008 * abs(math.sin(TAU * 1.5 * t))), {}


def a_shrug(t, d, e):
    k = ease_in_out_sine(min(1.0, (t % 2.2) / 0.5)) * (1 - ease_in_out_sine(clamp(((t % 2.2) - 1.4) / 0.6)))
    return P(l_up=lerp(10, 38, k), r_up=lerp(10, 38, k), l_lo=lerp(4, 100, k), r_lo=lerp(4, 100, k),
             head=lerp(0, 10, k), squash=1 - 0.035 * k, nod=-0.1 * k), {}


ACTIONS = {
    "idle_breathing": a_idle_breathing,
    "walk": a_walk,
    "run_panic": a_run_panic,
    "explain_gestures": a_explain_gestures,
    "point_at": a_point_at,
    "panic_hands_up": a_panic_hands_up,
    "facepalm": a_facepalm,
    "type_on_laptop": a_type_on_laptop,
    "celebrate_jump": a_celebrate_jump,
    "think_chin": a_think_chin,
    "argue_wildly": a_argue_wildly,
    "fall_down_dramatic": a_fall_down_dramatic,
    "nod_yes": a_nod_yes,
    "shake_head_no": a_shake_head_no,
    "shock_freeze": a_shock_freeze,
    "mic_drop": a_mic_drop,
    "sip_coffee": a_sip_coffee,
    "plot_evil": a_plot_evil,
    # bonus actions
    "talk": a_talk,
    "cta_point": a_cta_point,
    "wave": a_wave,
    "shrug": a_shrug,
}

DEFAULT_EXPRESSION = {
    "idle_breathing": "neutral", "walk": "neutral", "run_panic": "shocked",
    "explain_gestures": "happy", "point_at": "smug", "panic_hands_up": "shocked",
    "facepalm": "deadpan", "type_on_laptop": "deadpan", "celebrate_jump": "happy",
    "think_chin": "neutral", "argue_wildly": "angry", "fall_down_dramatic": "shocked",
    "nod_yes": "happy", "shake_head_no": "deadpan", "shock_freeze": "shocked",
    "mic_drop": "smug", "sip_coffee": "smug", "plot_evil": "evil",
    "talk": "neutral", "cta_point": "happy", "wave": "happy", "shrug": "deadpan",
}

ACTION_SFX = {
    "celebrate_jump": "boing", "fall_down_dramatic": "thud", "shock_freeze": "sting",
    "mic_drop": "thud", "panic_hands_up": "whoosh", "run_panic": "whoosh",
    "facepalm": "slap", "plot_evil": "rumble", "cta_point": "pop", "point_at": "pop",
    "think_chin": "tick", "type_on_laptop": "click",
}


def action_pose(name: str, t: float, d: float, energy: float = 1.0):
    fn = ACTIONS.get(name, a_talk)
    pose, fx = fn(max(0.0, t), max(d, 0.1), energy)
    return pose, fx


def guest_reaction(main_action: str) -> str:
    return {
        "argue_wildly": "argue_wildly", "celebrate_jump": "celebrate_jump",
        "panic_hands_up": "panic_hands_up", "explain_gestures": "nod_yes",
        "point_at": "shock_freeze", "plot_evil": "shake_head_no",
        "fall_down_dramatic": "facepalm", "mic_drop": "shock_freeze",
        "shock_freeze": "shock_freeze", "facepalm": "shrug",
    }.get(main_action, "idle_breathing")
