"""How does the traffic light know you're waiting? - built step by step."""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.story import open_loop
from ..qa import shift_spec
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

WIDE = ((-0.6, 0.6, 0.6), 118)
LOOPCAM = ((-2.4, 0.6, 0.4), 230)
SIGCAM = ((1.2, -1.0, 1.7), 280)
AVENUE = ((5.0, 0.5, 0.6), 86)

STEPS = [
    dict(text="If you put a red and a green lamp on a pole and switch them with a timer, you've got the world's "
              "simplest traffic light.",
         cam=((1.45, -1.3, 1.6), 420), pegs="neutral",
         cams=[("w:timer", ((1.45, -1.3, 1.7), 330), 1.0), ("w:simplest", WIDE, 1.4)],
         do=[("pole", 0.0, 1, 0.7, "out"), ("lamp_r", "w:red", 1, 0.4, "back"), ("lamp_g", "w:green", 1, 0.4, "back"),
             ("timer", "w:timer", 1, 0.4, "back"), ("world", "w:simplest", 1, 1.3, "out"),
             ("ms", "w:timer", 2, 0, "lin"), ("ms", "w:switch+1.6", 0, 0, "lin"), ("ms", "w:simplest", 2, 0, "lin")],
         keys=[("red|red lamp", INK), ("green lamp|+ green lamp", INK), ("timer|+ a timer", INK),
               ("simplest traffic light", BLUE)],
         sfx=[("w:red", "pop"), ("w:green", "pop"), ("w:simplest", "whoosh")]),
    dict(text="It works. Until it's three in the morning, the roads are empty, and you're stuck at a red light for a "
              "full minute.",
         cam=((-2.0, 0.6, 0.6), 190), pegs="worried",
         do=[("ms", 0.3, 0, 0, "lin"), ("ss", 0.3, 2, 0, "lin"), ("night", "w:three", 1, 0.8, "io"),
             ("car_x", "w:stuck", -2.4, 1.0, "out")],
         keys=[("three in the morning|3 AM", INK), ("roads are empty", INK), ("full minute", RED)],
         pops=[dict(kind="count", at="w:stuck", **{"from": 60, "to": 0}, anim=3.0, fmt="{} s", sub="of waiting",
                    pos="tr", until="end+0.2", color=RED)]),
    dict(text="So you cut a loop of wire into the road, just before the stop line. That's an inductive loop.",
         cam=LOOPCAM, pegs="neutral",
         do=[("loop", "w:cut", 1, 1.2, "out")],
         keys=[("loop of wire", INK), ("stop line", INK), ("inductive loop", INK)],
         fix="w:inductive",
         pops=[dict(kind="arrow", at="w:inductive", xyz=(-2.6, 0.85, 0.02), text="loop in the road", color=BLUE,
                    off=(-0.15, 0.12), until="end+0.3", sound=False)],
         sfx=[("w:cut", "slap")]),
    dict(text="Current in the wire makes a magnetic field. When a big lump of metal like a car sits on top, the field "
              "changes, and the controller in the box by the road knows someone is waiting.",
         cam=((-2.6, -0.2, 0.6), 190), pegs="happy",
         do=[("field", "w:magnetic", 1, 0.5, "out"), ("sense", "w:changes", 1, 0.3, "out"),
             ("cabinet", "w:controller", 1, 0.5, "back"), ("wire_lit", "w:knows", 1, 0.5, "out"),
             ("ms", "end-0.8", 2, 0, "lin"), ("ss", "end-1.6", 1, 0, "lin"), ("ss", "end-1.0", 0, 0, "lin"),
             ("night", "end-0.8", 0, 0.8, "io")],
         keys=[("magnetic field", INK), ("lump of metal", INK), ("field changes", INK), ("controller", INK)],
         pops=[dict(kind="graph", at="w:lump", title="LOOP SIGNAL", track="sense", window=5.0, color=BLUE, pos="bc",
                    until="w:controller")],
         sfx=[("w:changes", "ding")]),
    dict(text="But a bicycle has so little metal that the loop barely notices it.",
         cam=LOOPCAM, pegs="worried",
         do=[("car_x", 0.2, 14.5, 2.2, "in"), ("sense", 0.2, 0, 0.4, "in"), ("ms", 0.3, 0, 0, "lin"),
             ("bike", "w:bicycle", 1, 0.4, "back"), ("bike_x", "w:bicycle", -2.5, 1.0, "out")],
         keys=[("so little metal", RED), ("barely notices|barely noticed", RED)],
         pops=[dict(kind="meter", at="w:little", text="DETECTION", **{"from": 0.0, "to": 0.08}, color=RED, fmt="WEAK",
                    pos="bc", until="end+0.3")]),
    dict(text="So many intersections add cameras or radar that spot anything that moves, and some loops are tuned "
              "to feel bikes too.",
         cam=((-2.0, -0.4, 1.2), 200), pegs="happy",
         do=[("cam_on", "w:cameras", 1, 0.5, "back"), ("ms", "end-0.6", 2, 0, "lin"), ("bike_x", "end-0.4", 6.0, 2.5, "in")],
         keys=[("cameras or radar", INK), ("anything that moves", BLUE)],
         fix="w:cameras",
         sfx=[("w:cameras", "click")]),
    dict(text="Next problem. The light jumps straight from green to red, and nobody can stop in time.",
         cam=WIDE, pegs="shocked",
         do=[("bike", 0.2, 0, 0.3, "in"), ("car_x", 0.0, -6.0, 0.01, "lin"), ("car_x", "w:light", -1.2, 1.8, "in"),
             ("ms", "w:red", 0, 0, "lin"), ("skid", "w:nobody", 1, 0.3, "out")],
         keys=[("green to red", RED), ("stop in time", RED)],
         sfx=[("w:nobody", "slap")]),
    dict(text="So you add a yellow light, timed for how fast cars drive on that road. Faster road, longer yellow.",
         cam=SIGCAM, pegs="happy",
         do=[("skid", 0, 0, 0.3, "in"), ("car_x", 0.0, -2.5, 0.01, "lin"), ("yel", "w:yellow", 1, 0.4, "back"),
             ("ms", "end-1.5", 2, 0, "lin"), ("car_x", "end-1.3", 14.5, 1.3, "in"),
             ("ms", "w:yellow", 1, 0, "lin")],
         keys=[("yellow light", INK), ("how fast|timed by speed", INK), ("longer yellow", BLUE)],
         fix="w:yellow",
         pops=[dict(kind="bars", at="w:faster", title="YELLOW TIME", until="end+0.3", pos="bc",
                    items=[("slow street", 0.45, ORANGE), ("fast road", 0.9, ORANGE)])],
         sfx=[("w:yellow", "pop")]),
    dict(text="Some drivers still squeeze through on yellow. So for a second or two, every direction is red at the "
              "same time. That's the all red clearance.",
         cam=WIDE, pegs="neutral",
         do=[("ms", 0.2, 1, 0, "lin"), ("run_x", "w:squeeze", 14.5, 2.6, "lin"), ("ms", "w:every", 0, 0, "lin"),
             ("ss", "w:every", 0, 0, "lin"), ("ss", "end-0.6", 2, 0, "lin"), ("side_y", "end-0.6", 9.0, 3.0, "in")],
         keys=[("squeeze through", RED), ("every direction is red|all directions red", INK), ("all red clearance", INK)],
         fix="w:all",
         pops=[dict(kind="note", at="w:every", text="ALL RED: 1-2 s", pos="tr", until="end")]),
    dict(text="But what if a fault turns both directions green at once?",
         cam=WIDE, pegs="shocked",
         do=[("ms", "w:fault", 2, 0, "lin"), ("ss", "w:fault", 2, 0, "lin"), ("cabinet_alarm", "w:both", 1, 0, "lin")],
         keys=[("fault", RED), ("both directions green|both green?!", RED)],
         pops=[dict(kind="warn", at="w:both", text="crash risk!", pos="bc", until="end+0.3")],
         sfx=[("w:both", "sting")]),
    dict(text="A separate safety box called the conflict monitor watches every lamp. If it ever sees two greens that "
              "could crash, it switches the whole intersection to flashing red.",
         cam=((-2.3, -0.6, 0.9), 180), pegs="happy",
         do=[("monitor", "w:separate", 1, 0.4, "back"), ("flash", "w:flashing", 1, 0, "lin"),
             ("cabinet_alarm", "w:flashing", 0, 0, "lin")],
         keys=[("conflict monitor", INK), ("two greens", RED), ("flashing red", BLUE)],
         fix="w:conflict",
         sfx=[("w:flashing", "click")]),
    dict(text="Then a pedestrian shows up. So you add a push button that asks the controller for a walk signal.",
         cam=((1.4, 1.2, 0.9), 230), pegs="neutral",
         do=[("flash", 0.2, 0, 0, "lin"), ("ms", 0.2, 2, 0, "lin"), ("ss", 0.2, 0, 0, "lin"),
             ("ped", "w:pedestrian", 1, 0.4, "back"), ("button", "w:push", 1, 0.4, "back"), ("press", "w:asks", 1, 0.2, "out"),
             ("ms", "w:walk", 1, 0, "lin"), ("ms", "end-0.3", 0, 0, "lin")],
         keys=[("pedestrian", INK), ("push button", INK), ("walk signal", BLUE)],
         fix="w:push",
         sfx=[("w:asks", "click")]),
    dict(text="Fun fact. In some cities, lots of those buttons quietly do nothing, and the lights just run on a "
              "timer.",
         cam=((1.4, 1.2, 0.9), 230), pegs="worried", pose="shrug",
         do=[("walk", 0.3, 1, 0, "lin"), ("ped_x", 0.4, 1, 2.6, "io"), ("press", "w:nothing", 0, 0.2, "in")],
         keys=[("do nothing|placebo button", RED), ("run on a timer", INK)]),
    dict(text="Now drive down a long avenue, and you hit a red at every single block.",
         cam=AVENUE, pegs="worried",
         do=[("walk", 0, 0, 0, "lin"), ("ped", 0.2, 0, 0.3, "in"), ("ms", 0.1, 2, 0, "lin"), ("ss", 0.1, 0, 0, "lin"),
             ("avenue", 0.0, 1, 1.0, "out"), ("wave_x", "w:drive", 4.2, 1.6, "io"), ("w1", "w:drive", 0, 0, "lin"),
             ("w2", 0.0, 0, 0, "lin")],
         keys=[("long avenue", INK), ("every single block", RED)]),
    dict(text="So the controllers along the road are synced, and each light turns green just as cars driving the "
              "speed limit arrive. That's a green wave.",
         cam=AVENUE, pegs="happy",
         do=[("wave_x", 0.0, -3.0, 0.01, "lin"), ("w1", 0.0, 0, 0, "lin"), ("w2", 0.0, 0, 0, "lin"),
             ("wave_x", "w:synced", 14.5, "end-0.2", "lin"), ("w1", "w:turns", 2, 0, "lin"), ("w2", "w:speed", 2, 0, "lin"),
             ("sync", "w:synced", 1, 0.5, "out")],
         keys=[("synced", INK), ("speed limit", INK), ("green wave", BLUE)],
         fix="w:wave",
         sfx=[("w:wave", "ding")]),
    dict(text="And when an ambulance comes, a sensor on the light picks up a signal from the vehicle and gives it "
              "green all the way. That's preemption.",
         cam=((-1.0, 0.6, 0.8), 140), pegs="shocked",
         do=[("sync", 0.0, 0, 0.3, "in"), ("ms", 0.1, 0, 0, "lin"), ("amb_x", "w:ambulance", -3.0, 1.2, "out"),
             ("beam", "w:signal", 1, 0.3, "out"), ("ms", "w:green", 2, 0, "lin"), ("amb_x", "w:green", 14.5, 2.4, "in")],
         keys=[("ambulance", INK), ("signal from the vehicle", INK), ("green all the way", BLUE), ("preemption", INK)],
         fix="w:preemption",
         sfx=[("w:ambulance", "sting"), ("w:green", "ding")]),
    dict(text="So next time a red light flips green the moment you roll up at night, you'll know the road just felt "
              "your car.",
         cam=((-2.2, 0.8, 0.6), 170), pegs="happy",
         do=[("beam", 0, 0, 0.3, "in"), ("ms", 0.1, 0, 0, "lin"), ("night", 0.1, 1, 0.6, "io"), ("car_x", 0.1, -6.0, 0.01, "lin"),
             ("car_x", "w:roll", -2.4, 1.2, "out"), ("sense", "w:roll+0.8", 1, 0.3, "out"), ("ms", "w:night", 2, 0, "lin")],
         keys=[("flips green", BLUE), ("felt your car|the road felt your car", BLUE)]),
    dict(text="And congratulations, you just built a traffic light. Now you just need people to stop honking the "
              "second it turns green. Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("night", 0.1, 0, 0.8, "io"), ("sense", 0.2, 0, 0.3, "in"), ("car_x", 0.4, 14.5, 3.0, "in")],
         keys=[("built a traffic light|you built a traffic light!", BLUE), ("stop honking", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

# Scene QA (stickman_studio/explainer/qa.py) - ORIGINAL step indices (VIDEO uses shift_spec(QA, 1) after open_loop inserted the hook). Which steps each moving prop belongs to. Outside them it must
# drive away; while moving it must never overlap another car.
QA = dict(
    objects={
        "red car": dict(color=(226, 70, 70), steps="1-4,6-7,16-17"),
        "yellow car (runs the yellow)": dict(color=(250, 196, 70), steps="8"),
        "blue side car": dict(color=(90, 140, 220), steps="8"),
        "green wave car": dict(color=(120, 200, 140), steps="13-14"),
        "ambulance": dict(color=(250, 250, 250), steps="15"),
    },
)

INITIAL = dict(pole=0, lamp_r=0, lamp_g=0, timer=0, world=0, yel=0, ms=0, ss=0, night=0, car_x=-9.0, loop=0, field=0,
               sense=0, cabinet=0, wire_lit=0, bike=0, bike_x=-6.0, cam_on=0, skid=0, run_x=-6.0, side_y=-6.0,
               cabinet_alarm=0, monitor=0, flash=0, ped=0, button=0, press=0, walk=0, ped_x=0, avenue=0, wave_x=-9.0,
               w1=0, w2=0, sync=0, amb_x=-12.0, beam=0)

GRASS = (196, 222, 176)
ASPH = (78, 82, 94)
WALK = (214, 214, 220)
POLE = (70, 74, 86)
SIG_MAIN = (1.45, -1.3)        # main-road signal on the far corner (lamps face +y, towards the camera)
SIG_SIDE = (-1.45, -1.5)       # side-road signal pole (lamps face +x)
LOOP = (-3.4, -1.8, 0.15, 0.85)
WAVE_X = (5.2, 10.2)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _lamps(state, flash, t):
    if flash > 0.5:
        on = 1.0 if int(t * 2.2) % 2 == 0 else 0.15
        return (on, 0.0, 0.0)
    s = int(round(state))
    return (1.0 if s == 0 else 0.0, 1.0 if s == 1 else 0.0, 1.0 if s == 2 else 0.0)


class TrafficScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (200, 224, 250), (250, 244, 232), clouds=6)

    def film_amount(self, tr, t):
        return 0.0

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        world = g("world")
        if world > 0.01:
            self._ground(cam, tr, t, world)
        if g("avenue") > 0.01 or world > 0.9:
            self._avenue_signals(cam, tr, t)
        if world > 0.5:
            self._cars(cam, tr, t, behind=True)
        self._main_signal(cam, tr, t)
        if world > 0.5:
            self._cars(cam, tr, t, behind=False)
            self._people(cam, tr, t)
        n = g("night")
        if n > 0.01:
            arr = np.asarray(img).astype(np.float32)
            dark = arr * (1 - 0.55 * n) + np.array([10, 16, 50], np.float32) * 0.55 * n
            img.paste(Image.fromarray(np.clip(dark, 0, 255).astype(np.uint8)))
            # lamps glow through the night
            self._main_signal(cam, tr, t, heads_only=True)

    # ------------------------------------------------------------- ground
    def _ground(self, cam, tr, t, world):
        g = lambda k: tr.get(k, t)
        k = _sm(world)
        R = 3 + 11 * k
        cam.poly([(-R, -R, 0), (R + 4, -R, 0), (R + 4, R, 0), (-R, R, 0)], GRASS)
        cam.poly([(-R, -1.0, 0), (R + 4, -1.0, 0), (R + 4, 1.0, 0), (-R, 1.0, 0)], ASPH)
        cam.poly([(-1.0, -R, 0), (1.0, -R, 0), (1.0, R, 0), (-1.0, R, 0)], ASPH)
        for sgn in (-1, 1):   # sidewalks
            cam.poly([(-R, sgn * 1.0, 0), (R + 4, sgn * 1.0, 0), (R + 4, sgn * 1.55, 0), (-R, sgn * 1.55, 0)], WALK)
            cam.poly([(sgn * 1.0, -R, 0), (sgn * 1.55, -R, 0), (sgn * 1.55, R, 0), (sgn * 1.0, R, 0)], WALK)
        cam.poly([(-1.0, -1.0, 0.001), (1.0, -1.0, 0.001), (1.0, 1.0, 0.001), (-1.0, 1.0, 0.001)], ASPH)
        x = -R
        while x < R + 4:           # lane dashes
            if not -1.6 < x < 1.6:
                cam.line([(x, 0, 0.002), (x + 0.5, 0, 0.002)], (240, 220, 120), 0.03, caps=False)
            x += 1.0
        y = -R
        while y < R:
            if not -1.6 < y < 1.6:
                cam.line([(0, y, 0.002), (0, y + 0.5, 0.002)], (240, 220, 120), 0.03, caps=False)
            y += 1.0
        cam.line([(-1.3, 0.02, 0.003), (-1.3, 0.98, 0.003)], (250, 250, 250), 0.06, caps=False)
        cam.line([(-0.98, -1.3, 0.003), (-0.02, -1.3, 0.003)], (250, 250, 250), 0.06, caps=False)
        for i in range(6):         # zebra crossing east of the junction
            yy = -0.9 + i * 0.33
            cam.poly([(1.35, yy, 0.003), (2.05, yy, 0.003), (2.05, yy + 0.18, 0.003), (1.35, yy + 0.18, 0.003)],
                     (245, 245, 245))
        # loop saw-cut
        lp = g("loop")
        if lp > 0.01:
            x0, x1, y0, y1 = LOOP
            pts = [(x0, y0, 0.004), (x1, y0, 0.004), (x1, y1, 0.004), (x0, y1, 0.004), (x0, y0, 0.004)]
            col = mix((30, 30, 36), (90, 170, 255), g("wire_lit") * (0.6 + 0.4 * math.sin(t * 6)))
            cam.line(kit.sub_path(pts, 0, lp, 20), col, 0.035)
            if lp > 0.95:
                cam.line([(x1, y0, 0.004), (x1 + 0.2, -1.0, 0.004), (-2.65, -1.2, 0.004)], col, 0.025)
        # houses + trees for context
        if k > 0.6:
            for (hx, hy, c) in ((-5.5, -4.5, (236, 210, 180)), (-3.2, -4.8, (210, 222, 236)), (2.4, -4.6, (240, 200, 196)),
                                (-5.2, -2.6, (226, 230, 210))):
                hk = _sm((k - 0.6) / 0.4)
                cam.box(hx, hy, 0, 1.6, 1.4, 1.3 * hk, c)
                cam.box(hx - 0.05, hy - 0.05, 1.3 * hk, 1.7, 1.5, 0.15, shade(c, -0.35))
            for (tx, ty) in ((-4.0, 2.6), (4.6, 3.4), (-6.0, 2.4), (4.4, -2.4)):
                cam.box(tx - 0.06, ty - 0.06, 0, 0.12, 0.12, 0.5, (130, 96, 70))
                for r, z in ((0.5, 0.75), (0.36, 1.1)):
                    x, y = cam.p(tx, ty, z)
                    rr = r * cam.s
                    cam.d.ellipse((x - rr, y - rr * 0.9, x + rr, y + rr * 0.9), fill=(96, 170, 96), outline=(60, 120, 60),
                                  width=max(1, int(0.01 * cam.s)))
        sh = ShadowLayer(cam)
        if g("cabinet") > 0.3:
            sh.box_on_plane(-3.0, -1.55, 0, 0.6, 0.35, 1.0, "z", 0.0, 200)
        sh.apply(cam.img, 0.28, 2.0)
        # field rings above the loop
        fl = g("field")
        if fl > 0.01:
            sense = g("sense")
            for i in range(4):
                f = (t * 0.5 + i / 4) % 1.0
                x0, x1, y0, y1 = LOOP
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                rx = (0.9 + 0.3 * f) * (1 - 0.25 * sense)
                pts = [(cx + math.cos(a) * rx, cy + math.sin(a) * 0.45, 0.05 + f * 0.7) for a in
                       [2 * math.pi * j / 30 for j in range(31)]]
                cam.line(pts, mix((90, 160, 255), (230, 236, 250), f * 0.8), 0.018 * fl, caps=False)
        # roadside controller cabinet
        cb = g("cabinet")
        if cb > 0.01:
            kk = _sm(cb)
            cam.box(-3.0, -1.55, 0, 0.6, 0.35, 1.0 * kk, (150, 160, 150))
            if kk > 0.9:
                kit.plate(cam, "y", -1.199, -2.92, 0.15, -2.48, 0.85, (60, 70, 64))
                for i in range(3):
                    parts.led(cam, (-2.82 + i * 0.12, -1.195, 0.72),
                              (255, 60, 60) if g("cabinet_alarm") > 0.5 and int(t * 8) % 2 else (90, 230, 140), True,
                              0.025)
                if g("monitor") > 0.01:
                    kit.plate(cam, "y", -1.197, -2.88, 0.25, -2.52, 0.55, (40, 90, 160), (20, 40, 80))
                    kit.plane_text(cam, "y", -1.195, -2.7, 0.4, "MONITOR", 0.05, (255, 255, 255), max_w=0.32)
                kit.label(cam, (-2.7, -1.37, 1.3), "CONTROLLER", 0.12, (255, 255, 255), (70, 90, 70))

    # ------------------------------------------------------------- signals
    def _main_signal(self, cam, tr, t, heads_only=False):
        g = lambda k: tr.get(k, t)
        pole = g("pole")
        if pole <= 0.01:
            return
        x, y = SIG_MAIN
        h = 2.3 * _sm(pole)
        flash = g("flash")
        st = _lamps(g("ms"), flash, t)
        lamps = 3 if g("yel") > 0.5 else 2
        rk, gk = _sm(g("lamp_r")), _sm(g("lamp_g"))
        states = (st[0] * rk, st[1], st[2] * gk)
        if not heads_only:
            cam.box(x - 0.05, y - 0.05, 0, 0.1, 0.1, h, POLE)
            cam.box(x - 0.18, y - 0.18, 0, 0.36, 0.36, 0.08, POLE)
            # side-road signal on the far corner
            if g("world") > 0.6:
                sx, sy = SIG_SIDE
                cam.box(sx - 0.05, sy - 0.05, 0, 0.1, 0.1, 2.3, POLE)
                parts.signal_head(cam, sx + 0.17, sy, 1.55, "x", _lamps(g("ss"), flash, t), 3, 0.17, t)
        if h > 1.4:
            parts.signal_head(cam, x, y + 0.13, h - 0.85, "y", states, lamps, 0.2, t)
            if g("timer") > 0.01 and not heads_only and g("world") < 0.5:
                cx, cz = x + 0.55, h - 0.4
                px, py = cam.p(cx, y, cz)
                r = 0.18 * cam.s * _sm(g("timer"))
                cam.d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 255, 255), outline=INK, width=max(2, int(r * 0.12)))
                a = t * 4
                cam.d.line((px, py, px + math.sin(a) * r * 0.75, py - math.cos(a) * r * 0.75), fill=RED,
                           width=max(2, int(r * 0.12)))
        if heads_only:
            return
        cm = g("cam_on")
        if cm > 0.01:   # detection camera on an arm over the lane
            px_, py_ = SIG_SIDE
            cam.line([(px_, py_, 2.2), (px_ - 0.3, py_ + 0.7, 2.2)], POLE, 0.05)
            cam.box(px_ - 0.45, py_ + 0.6, 2.05, 0.3, 0.18, 0.16, (230, 232, 238))
            if cm > 0.5:
                tip = (px_ - 0.45, py_ + 0.7, 2.1)
                for (ex, ey) in ((-3.2, 0.2), (-3.2, 0.9), (-1.8, 0.9)):
                    cam.line([tip, (ex, ey, 0.02)], (120, 200, 255), 0.01, caps=False)
                kit.label(cam, (SIG_SIDE[0] - 0.3, SIG_SIDE[1] + 0.7, 2.6), "CAMERA", 0.1, (255, 255, 255), BLUE)
        if g("beam") > 0.01:
            ax = g("amb_x")
            for i in range(5):
                f = (t * 1.5 + i / 5) % 1.0
                p = (ax + 0.6 + (x - ax - 0.6) * f, 0.5 + (y - 0.5) * f, 0.6 + (h - 0.5 - 0.6) * f)
                kit.glow_dot(cam, p, 0.035, (255, 120, 120))

    def _avenue_signals(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        a = g("avenue")
        if a <= 0.01:
            return
        for wx, key in zip(WAVE_X, ("w1", "w2")):
            cam.line([(wx - 0.2, 0.02, 0.003), (wx - 0.2, 0.98, 0.003)], (250, 250, 250), 0.06, caps=False)
            cam.box(wx - 0.05, 1.4, 0, 0.1, 0.1, 2.3 * _sm(a), POLE)
            if a > 0.8:
                parts.signal_head(cam, wx, 1.58, 1.45, "y", _lamps(g(key), 0, t), 3, 0.2, t)
        if g("sync") > 0.5:
            for i, wx in enumerate((-1.5,) + WAVE_X):
                kit.label(cam, (wx, 1.5, 2.75), "SYNC", 0.16, (255, 255, 255), GREEN)

    # ------------------------------------------------------------- traffic
    def _cars(self, cam, tr, t, behind):
        g = lambda k: tr.get(k, t)
        if behind:
            sy = g("side_y")
            if -6 < sy < 6:
                parts.car(cam, -0.5, sy, 0, "y", (90, 140, 220))
            rx = g("run_x")
            if -6 < rx < 14:
                parts.car(cam, rx, 0.5, 0, "x", (250, 196, 70))
            return
        cx = g("car_x")
        sk = g("skid")
        if -8 < cx < 14:
            jit = 0.03 * math.sin(t * 50) * sk
            parts.car(cam, cx + jit, 0.5, 0, "x", (226, 70, 70), lights=g("night") > 0.3)
            if sk > 0.3:
                for i in range(3):
                    cam.line([(cx - 0.6 - i * 0.4, 0.3, 0.01), (cx - 0.9 - i * 0.4, 0.3, 0.01)], (30, 30, 30), 0.05)
                    cam.line([(cx - 0.6 - i * 0.4, 0.7, 0.01), (cx - 0.9 - i * 0.4, 0.7, 0.01)], (30, 30, 30), 0.05)
            # driver mascot peeking out of the roof (who is waiting)
            expr = tr.peg_expr(t)
            kit.peg(cam, (cx + 0.05, 0.5, 0.48), PEG_COLORS[0], expr, t, 0.9, (0.6, 0.3), seed=1,
                    pose=tr.peg_pose(t))
        if g("bike") > 0.01:
            bx = g("bike_x")
            k = _sm(g("bike"))
            for wx in (bx - 0.28, bx + 0.28):
                cam.poly(cam.disc_pts((wx, 0.5, 0.18), 0.18 * k, "y", 16), None, (30, 30, 36), 0.02)
            cam.line([(bx - 0.28, 0.5, 0.18), (bx, 0.5, 0.4), (bx + 0.28, 0.5, 0.18)], (230, 80, 60), 0.025)
            kit.peg(cam, (bx, 0.5, 0.35), PEG_COLORS[2], "worried" if tr.step_at(t) == 4 else "happy", t, 1.1 * k,
                    (0.6, 0.2), seed=4)
        wx = g("wave_x")
        if g("avenue") > 0.01 and -6 < wx < 14:
            parts.car(cam, wx, 0.5, 0, "x", (120, 200, 140))
            kit.peg(cam, (wx + 0.05, 0.5, 0.48), PEG_COLORS[0], tr.peg_expr(t), t, 0.9, (0.6, 0.3), seed=1)
        ax = g("amb_x")
        if -10 < ax < 14:
            parts.car(cam, ax, 0.5, 0, "x", (250, 250, 250), length=1.7)
            cam.line([(ax - 0.8, 0.82, 0.25), (ax + 0.8, 0.82, 0.25)], RED, 0.06, caps=False)
            on = int(t * 8) % 2
            parts.led(cam, (ax - 0.1, 0.4, 0.58), (255, 60, 60) if on else (60, 120, 255), True, 0.06)
            parts.led(cam, (ax + 0.2, 0.6, 0.58), (60, 120, 255) if on else (255, 60, 60), True, 0.06)

    def _people(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        bt = g("button")
        if bt > 0.01:
            cam.box(1.25, 1.2, 0, 0.08, 0.08, 1.1 * _sm(bt), POLE)
            cam.box(1.2, 1.28, 0.75, 0.18, 0.06, 0.26, (250, 210, 60))
            pr = g("press")
            x, y = cam.p(1.29, 1.345, 0.88)
            r = 0.05 * cam.s
            cam.d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 80, 60) if pr > 0.5 else (60, 60, 70))
            # walk signal head
            wk = g("walk")
            cam.box(1.17, 1.2, 1.15, 0.24, 0.12, 0.3, (40, 42, 50))
            kit.plane_text(cam, "y", 1.321, 1.29, 1.3, "WALK" if wk > 0.5 else "WAIT", 0.07,
                           (255, 255, 255) if wk > 0.5 else (255, 140, 60), max_w=0.2)
        pd = g("ped")
        if pd > 0.01:
            px = g("ped_x")
            kit.peg(cam, (1.7, 1.45 - 2.6 * px, 0), PEG_COLORS[3], tr.peg_expr(t), t, 1.6 * _sm(pd), (0.2, -0.6),
                    seed=3, pose=tr.peg_pose(t), floor=WALK)


# open-loop structure (2026-11-22): question hook + teaser, reminder, late answer, loop ending
STEPS = open_loop(
    STEPS, "There's one vehicle that can turn every traffic light on your street green.", answer_step=15,
    teaser_frac=0.6, reminder=(8, "Still not the vehicle that turns everything green. Hold on."),
    reveal="Here's the answer.",
    hook_keys=[("one vehicle", INK), ("every traffic light|every light → green", BLUE)],
    ending_text="And that's how you build a traffic light. Follow for more. Because remember,",
    ending_keys=[("build a traffic light|how you build it", BLUE)])  # O6 hook, E2 ending + loop

VIDEO = dict(
    slug="traffic_light",
    title="How does the traffic light know you're waiting?",
    steps=STEPS, end_cover=False, scene=TrafficScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"), qa=shift_spec(QA, 1),
)
