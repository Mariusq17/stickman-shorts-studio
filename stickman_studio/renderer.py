"""Scene renderer: composes background, camera, props, stickmen, subtitles and
overlays into a frame for any global time t (stateless => random access)."""
from __future__ import annotations

import bisect
import math
import random
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw

from .camera import camera_state
from .config import RenderSettings
from .easing import clamp, ease_out_back, ease_out_cubic, lerp
from .figure import draw_stickman, draw_mic
from .painter import Painter, font
from .props import PROPS
from .rig import (StickmanRig, action_pose, lerp_pose, mirror_pose, guest_reaction,
                  DEFAULT_EXPRESSION, ACTIONS)
from .script_model import Script
from .subtitles import SubtitleRenderer, chunk_words

SIDE_SLOTS = ("side", "side_floor", "cta")
BLEND_T = 0.22


@dataclass
class ShotTiming:
    start: float
    duration: float
    words: list
    word_times: list                 # [(s, e)] seconds relative to shot start
    env: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=np.float32))
    env_rate: float = 100.0          # samples per second of env
    speech_end: float = 0.0

    def amp(self, t: float) -> float:
        if self.env is None or len(self.env) == 0:
            return 0.0
        i = int(t * self.env_rate)
        if i < 0 or i >= len(self.env):
            return 0.0
        return float(self.env[i])


def uniform_timeline(script: Script, wps: float = 2.45, pad: float = 0.35):
    """Timeline without audio (used for previews)."""
    tl, t0 = [], 0.0
    for sh in script.shots:
        words = sh.text.split()
        dur = max(1.4, len(words) / wps + pad)
        wt, cur = [], 0.1
        for w in words:
            wd = max(0.12, len(w) * 0.065)
            wt.append((cur, cur + wd))
            cur += wd * (dur - 0.1 - pad) / max(0.1, sum(max(0.12, len(x) * 0.065) for x in words))
            wt[-1] = (wt[-1][0], cur)
        env = np.array([0.5 + 0.5 * math.sin(i * 0.9) for i in range(int(dur * 100))], dtype=np.float32)
        tl.append(ShotTiming(t0, dur, words, wt, env, 100.0, dur - pad))
        t0 += dur
    return tl


class SceneRenderer:
    def __init__(self, script: Script, timeline: list, settings: RenderSettings):
        self.script = script
        self.tl = timeline
        self.st = settings
        self.W, self.H = settings.size
        self.th = settings.theme_obj
        self.fmt = settings.format
        self.energy = 0.6 + 0.2 * (clamp(settings.energy, 1, 5) - 1)   # 0.6 .. 1.4
        self.starts = [s.start for s in timeline]
        self.total = timeline[-1].start + timeline[-1].duration if timeline else 0.0
        W, H = self.W, self.H
        if self.fmt == "vertical":
            self.U = 0.68 * W
            self.floor = 0.615 * H
            self.stage_c = (0.5 * W, 0.40 * H)
            self.zoom_scale = 0.8
            self.x_solo, self.x_side, self.side_x = 0.5 * W, 0.33 * W, 0.76 * W
            self.cta_pos = (0.61 * W, self.floor - 0.98 * self.U)
            self.above_side = (0.68 * W, self.floor - 1.12 * self.U)
        else:
            self.U = 0.54 * H
            self.floor = 0.77 * H
            self.stage_c = (0.5 * W, 0.45 * H)
            self.zoom_scale = 0.8
            self.x_solo, self.x_side, self.side_x = 0.5 * W, 0.36 * W, 0.66 * W
            self.cta_pos = (0.66 * W, self.floor - 0.86 * self.U)
            self.above_side = (0.78 * W, self.floor - 0.98 * self.U)
        self.lw = self.U * 0.028
        self.margin = int(0.05 * max(W, H))
        self.bg = self._make_background()
        self.subs = SubtitleRenderer(W, H, self.fmt, self.th)
        self._chunks = [chunk_words(s.words, s.word_times) if s.words else [] for s in timeline]
        self._end_pose = {}
        self._vignette = None
        self.labels = _labels(script.language)

    # ------------------------------------------------------------------ setup
    def _make_background(self) -> Image.Image:
        m = self.margin
        W, H = self.W + 2 * m, self.H + 2 * m
        th = self.th
        img = Image.new("RGB", (W, H), th.bg)
        arr = np.asarray(img).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy = W * 0.5, H * 0.45
        dist = np.sqrt(((xx - cx) / W) ** 2 + ((yy - cy) / H) ** 2)
        k = np.clip(dist * 1.6, 0, 1)[..., None]
        bg2 = np.array(th.bg2, dtype=np.float32)
        arr = arr * (1 - k * 0.85) + bg2 * (k * 0.85)
        img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        if th.grid:
            step = int(min(W, H) / 14)
            for x in range(0, W, step):
                d.line([(x, 0), (x, H)], fill=th.grid, width=1 if (x // step) % 4 else 2)
            for y in range(0, H, step):
                d.line([(0, y), (W, y)], fill=th.grid, width=1 if (y // step) % 4 else 2)
        else:
            rnd = random.Random(11)
            dot = tuple(int(lerp(a, b, 0.5)) for a, b in zip(th.bg, th.bg2))
            for _ in range(70):
                x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.6)
                r = rnd.uniform(2, 6) * W / 1200
                d.ellipse((x - r, y - r, x + r, y + r), fill=dot)
        return img

    # --------------------------------------------------------------- helpers
    def shot_index(self, t: float) -> int:
        i = bisect.bisect_right(self.starts, t) - 1
        return int(clamp(i, 0, len(self.tl) - 1))

    def _layout(self, shot):
        props = [p for p in shot.props if p in PROPS]
        if "laptop" in props and "desk" not in props:
            props.append("desk")
        fxn = ACTIONS.get(shot.action)
        if shot.action == "type_on_laptop":
            for need in ("desk", "laptop"):
                if need not in props:
                    props.append(need)
        slots, used = [], set()
        for name in props:
            slot = PROPS[name][1]
            if slot in ("side", "side_floor") and (shot.guest or "side" in used or "side_floor" in used
                                                   or "cta" in used):
                slot = "above_side" if "above_side" not in used else "above"
            if slot == "cta" and ("cta" in used or shot.guest):
                slot = "above_side" if "above_side" not in used else "side"
            if slot in ("above", "above_side") and slot in used:
                slot = "above_side" if slot == "above" else "above"
            used.add(slot)
            slots.append((name, slot))
        busy_side = shot.guest or any(s in SIDE_SLOTS for _, s in slots)
        char_x = self.x_side if busy_side else self.x_solo
        return slots, char_x

    def _end_pose_of(self, i: int):
        if i not in self._end_pose:
            sh, tm = self.script.shots[i], self.tl[i]
            self._end_pose[i] = action_pose(sh.action, tm.duration, tm.duration, self.energy)[0]
        return self._end_pose[i]

    # ----------------------------------------------------------------- render
    def render(self, t: float) -> Image.Image:
        i = self.shot_index(t)
        shot, tm = self.script.shots[i], self.tl[i]
        lt = t - tm.start
        d = tm.duration
        th, U, W, H = self.th, self.U, self.W, self.H
        slots, char_x = self._layout(shot)

        pose, fx = action_pose(shot.action, lt, d, self.energy)
        if i > 0 and lt < BLEND_T:
            _, prev_x = self._layout(self.script.shots[i - 1])
            if abs(prev_x - char_x) < 1:
                pose = lerp_pose(self._end_pose_of(i - 1), pose, ease_out_cubic(lt / BLEND_T))
        amp = tm.amp(lt)
        speaking = lt <= tm.speech_end + 0.05
        mouth = clamp(amp * 1.4) if speaking else 0.0
        pose = dict(pose)
        pose["head"] += 3.0 * amp * math.sin(lt * 7.0)
        pose["y"] += 0.004 * amp

        rig = StickmanRig(U, char_x, self.floor)
        sk = rig.solve(pose)
        fxp = char_x
        if shot.guest:
            fxp = (char_x + self.side_x) / 2
        elif any(s_ == "cta" for _, s_ in slots):
            fxp = (char_x + self.cta_pos[0]) / 2
        elif any(s_ in ("side", "side_floor") for _, s_ in slots):
            fxp = (char_x + self.side_x) / 2
        focus_pt = (fxp, self.floor - 0.62 * U)
        zs = self.zoom_scale * (0.45 if any(s_ == "cta" for _, s_ in slots) else 1.0)
        focus, zoom, shake = camera_state(shot.camera, lt, d, W, H, focus_pt, self.energy,
                                          center=self.stage_c, zoom_scale=zs)

        # background with parallax + shake (screen space)
        m = self.margin
        sc = self.stage_c
        ox = int(clamp(m - (focus[0] - sc[0]) * 0.08 + shake[0] * 0.6, 0, 2 * m))
        oy = int(clamp(m - (focus[1] - sc[1]) * 0.08 + shake[1] * 0.6, 0, 2 * m))
        img = self.bg.crop((ox, oy, ox + W, oy + H))
        p = Painter(img, focus=focus, zoom=zoom, anchor=sc, shake=shake)

        # floor + shadow
        p.line([(-W, self.floor), (2 * W, self.floor)], th.floor, self.lw * 0.6, caps=False)
        hip = sk.pts["hip"]
        lift = clamp(1 - (self.floor - max(sk.pts["l_foot"][1], sk.pts["r_foot"][1])) / (0.5 * U))
        p.ellipse((hip[0], self.floor + U * 0.012), U * 0.16 * (0.5 + 0.5 * lift), U * 0.022,
                  fill=th.bg2)

        def prop_pos(slot, k):
            if slot == "side":
                return (self.side_x, self.floor - 0.42 * U)
            if slot == "side_floor":
                return (self.side_x, self.floor)
            if slot == "cta":
                return self.cta_pos
            if slot == "above_side":
                return self.above_side
            if slot == "above":
                return (sk.head_c[0] + U * 0.05, sk.head_c[1] - sk.head_r - U * 0.17)
            if slot == "back":
                bx = 0.14 * W if char_x >= self.x_solo - 1 or self.fmt == "horizontal" else 0.86 * W
                if char_x < self.x_solo - 1:
                    bx = 0.86 * W if not any(s in SIDE_SLOTS for _, s in slots) else 0.10 * W
                return (bx, self.floor)
            if slot == "front":
                return (char_x, self.floor)
            return (W / 2, H / 2)

        def draw_prop(name, slot, j):
            age = lt - 0.12 * j
            if age < 0:
                return
            k = ease_out_back(age / 0.35) if slot not in ("front", "back", "rain") else 1.0
            x, y = prop_pos(slot, k)
            fn = PROPS[name][0]
            kw = {}
            if name in ("subscribe",):
                kw = {"label": self.labels["subscribe"], "done_label": self.labels["subscribed"]}
            elif name in ("like", "comment", "save"):
                kw = {"label": self.labels[name]}
            elif name == "calendar":
                kw = {"label": self.labels["monday"]}
            if slot == "rain":
                kw["area"] = (-0.1 * W, -0.15 * H, 1.1 * W, self.floor + 0.05 * H)
            boost = 1.25 if slot in ("side", "cta", "side_floor", "above_side") else 1.0
            if slot == "cta" and self.fmt == "vertical":
                boost = 1.15
            s = U * max(0.05, k) * boost
            fn(p, x, y, s, age, th, self.lw * max(0.3, min(k, 1.0)), **kw)

        layer_back = [(n, s, j) for j, (n, s) in enumerate(slots) if s == "back"]
        layer_mid = [(n, s, j) for j, (n, s) in enumerate(slots) if s in SIDE_SLOTS + ("above_side",)]
        layer_front = [(n, s, j) for j, (n, s) in enumerate(slots) if s == "front"]
        layer_top = [(n, s, j) for j, (n, s) in enumerate(slots) if s in ("above", "rain")]
        for n, s_, j in layer_back + layer_mid:
            draw_prop(n, s_, j)

        # guest stickman
        if shot.guest:
            ga = guest_reaction(shot.action)
            gp, gfx = action_pose(ga, lt + 0.37, d, self.energy)
            gp = mirror_pose(gp)
            gx = self.side_x if self.fmt == "vertical" else self.side_x + 0.03 * W
            gsk = StickmanRig(U * 0.92, gx, self.floor).solve(gp)
            draw_stickman(p, gsk, th.guest_ink, th.face, DEFAULT_EXPRESSION.get(ga, "neutral"), 0.0,
                          lt + 1.3, gfx, th, self.lw, seed=1.7)

        # main character
        hand_props = dict(fx.get("hand_prop", {}))
        draw_stickman(p, sk, th.ink, th.face, shot.expression or DEFAULT_EXPRESSION.get(shot.action),
                      mouth if not fx.get("sipping") else 0.0, lt, fx, th, self.lw, seed=0.0,
                      hand_props=hand_props)
        if "drop" in fx:
            self._draw_drop(p, fx["drop"], lt, d, char_x)
        for n, s_, j in layer_front:
            draw_prop(n, s_, j)
        if fx.get("glow"):
            hx, hy = sk.head_c
            p.ellipse((hx, hy + sk.head_r * 0.1), sk.head_r * 1.25, sk.head_r * 1.1, outline=th.accent2,
                      width=self.lw * 0.25)
        for n, s_, j in layer_top:
            draw_prop(n, s_, j)
        if fx.get("confetti"):
            self._confetti(p, lt)
        if fx.get("impact"):
            for k in range(8):
                a = math.radians(180 + k * 25.7)
                cx, cy = sk.head_c[0], self.floor
                p.line([(cx + math.cos(a) * U * 0.25, cy + math.sin(a) * U * 0.1),
                        (cx + math.cos(a) * U * 0.42, cy + math.sin(a) * U * 0.2)], th.ink, self.lw * 0.5)

        # ---- screen-space overlays
        if fx.get("evil"):
            img = self._apply_vignette(img)
        if shot.camera in ("punch_in", "dramatic_camera_shake") or shot.action == "shock_freeze":
            if lt < 0.07:
                img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), 0.55)
        dr = ImageDraw.Draw(img)
        self._draw_header(dr, i, lt)
        if self.st.progress_bar and self.total > 0:
            bh = max(4, int(H * 0.006))
            dr.rectangle((0, 0, W, bh), fill=th.bg2)
            dr.rectangle((0, 0, int(W * clamp(t / self.total)), bh), fill=th.accent)
        if self.st.subtitles and tm.words:
            self.subs.draw(dr, tm.words, tm.word_times, lt, self._chunks[i])
        return img

    # ------------------------------------------------------------- overlays
    def _draw_header(self, dr, i, lt):
        title = (self.script.hook_text or self.script.title or "").strip()
        if not title:
            return
        W, H, th = self.W, self.H, self.th
        if self.fmt == "horizontal" and i > 0:
            return
        big = i == 0
        k = ease_out_back(lt / 0.4) if big else 1.0
        size = int((W * 0.068 if self.fmt == "vertical" else H * 0.06) * (1.0 if big else 0.72) * max(0.2, k))
        f = font(size)
        max_w = W * 0.84
        words, lines, cur = title.upper().split(), [], ""
        for w in words:
            cand = (cur + " " + w).strip()
            if dr.textlength(cand, font=f) > max_w and cur:
                lines.append(cur)
                cur = w
            else:
                cur = cand
        if cur:
            lines.append(cur)
        lines = lines[:3]
        lh = size * 1.18
        cy = H * (0.135 if self.fmt == "vertical" else 0.10)
        bw = max(dr.textlength(l, font=f) for l in lines) + size * 0.9
        bh = lh * len(lines) + size * 0.5
        box = (W / 2 - bw / 2, cy - bh / 2, W / 2 + bw / 2, cy + bh / 2)
        dr.rounded_rectangle(box, radius=int(size * 0.35), fill=th.accent if big else th.ink,
                             outline=th.sub_stroke, width=max(2, int(size * 0.08)))
        col = (15, 15, 20) if big else th.bg
        for li, l in enumerate(lines):
            dr.text((W / 2, cy - (len(lines) - 1) * lh / 2 + li * lh), l, font=f, fill=col, anchor="mm")

    def _apply_vignette(self, img):
        if self._vignette is None:
            W, H = self.W, self.H
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            dist = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
            a = np.clip((dist - 0.18) * 2.2, 0, 0.85)
            rgba = np.zeros((H, W, 4), dtype=np.uint8)
            rgba[..., 0] = 60
            rgba[..., 3] = (a * 255).astype(np.uint8)
            self._vignette = Image.fromarray(rgba, "RGBA")
        base = img.convert("RGBA")
        base.alpha_composite(self._vignette)
        return base.convert("RGB")

    def _confetti(self, p, lt):
        th = self.th
        rnd = random.Random(5)
        cols = [th.accent, th.bad, th.good, th.accent2]
        for k in range(40):
            x = rnd.uniform(0, self.W)
            sp = rnd.uniform(0.25, 0.5) * self.H
            y = -0.1 * self.H + ((lt * sp + rnd.uniform(0, self.H)) % (self.H * 0.9))
            a = lt * rnd.uniform(3, 8) + k
            s = self.U * 0.018
            ca, sa = math.cos(a), math.sin(a)
            pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca)
                   for dx, dy in ((-s, -s / 2), (s, -s / 2), (s, s / 2), (-s, s / 2))]
            p.polygon(pts, fill=cols[k % 4])

    def _draw_drop(self, p, info, lt, d, char_x):
        t0 = info["t0"]
        pose0, _ = action_pose("mic_drop", t0 - 1e-3, d, self.energy)
        sk0 = StickmanRig(self.U, char_x, self.floor).solve(pose0)
        x0, y0 = sk0.pts[info.get("side", "r") + "_hand"]
        tau = lt - t0
        g = 4.0 * self.U
        y = y0 + 0.5 * g * tau * tau
        ground = self.floor - self.U * 0.025
        ang = min(90.0, tau * 420)
        if y >= ground:
            y = ground
            ang = 90.0
        draw_mic(p, x0 + tau * self.U * 0.05, y, self.U, ang, self.th.ink, self.th, self.lw)


def mic_drop_hit_time(d: float) -> float:
    from .rig import MIC_RELEASE
    return min(MIC_RELEASE, 0.45 * d) + 0.32


def _labels(lang: str) -> dict:
    if lang == "ro":
        return {"subscribe": "ABONEAZĂ-TE", "subscribed": "ABONAT ✓".replace(" ✓", "!"),
                "like": "LIKE", "comment": "COMENTARII", "save": "SALVEAZĂ", "monday": "LUNI"}
    return {"subscribe": "SUBSCRIBE", "subscribed": "SUBSCRIBED", "like": "LIKE",
            "comment": "COMMENTS", "save": "SAVE", "monday": "MONDAY"}
