"""How does a fridge make cold out of electricity? - a refrigerator built step by step (cutaway cabinet,
refrigerant loop: evaporator -> compressor -> condenser -> capillary tube)."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE, ICE = (240, 140, 40), (120, 190, 255)

WIDE = ((1.0, 0.9, 1.75), 190)
EVAP = ((0.1, 0.85, 2.55), 360)
COMP = ((1.6, 0.7, 0.9), 270)
COND = ((1.3, 0.8, 1.6), 230)
INSIDE = ((0.5, 0.8, 1.6), 260)

STEPS = [
    dict(text="Your fridge can't make cold. It steals heat. Bend a pipe inside a box, fill it with a liquid that "
              "boils at minus twenty six degrees, and you've got the simplest fridge.",
         cam=((0.2, 0.75, 2.7), 520), pegs="neutral",
         cams=[("w:box", ((0.5, 0.8, 2.2), 300), 1.0), ("w:simplest", WIDE, 1.4)],
         do=[("evap", 0.0, 1, 1.6, "out"), ("box", "w:box", 1, 0.9, "out"), ("food", "w:box+0.3", 1, 0.6, "back"),
             ("liquid", "w:liquid", 1, 0.8, "out"), ("boil", "w:boils", 1, 0.5, "out"),
             ("kitchen", "w:simplest", 1, 1.2, "out")],
         keys=[("steals heat", BLUE), ("pipe|pipe + box", INK), ("minus twenty six|boils at -26°C", INK),
               ("simplest fridge", BLUE)],
         pops=[dict(kind="hook", at=0.0, until="w:bend", text="Your fridge CAN'T make cold", hi=["can't", "cold"])],
         sfx=[("w:pipe", "pop"), ("w:box", "thud"), ("w:simplest", "whoosh")]),
    dict(text="Boiling eats energy, so as the liquid turns to gas, it soaks heat out of your food. That pipe is the "
              "evaporator.",
         cam=INSIDE, pegs="happy", pose="think",
         do=[("heatflow", "w:soaks", 1, 0.6, "out"), ("frost", "w:gas", 1, 1.5, "out")],
         keys=[("boiling eats energy", INK), ("soaks heat out|heat -> pipe", BLUE), ("evaporator", INK)],
         fix="w:evaporator",
         pops=[dict(kind="meter", at="w:soaks", text="FOOD TEMP", **{"from": 1.0, "to": 0.2}, fmt="", color=BLUE,
                    anim=2.0, pos="bc", until="end+0.2")],
         sfx=[("w:soaks", "whoosh")]),
    dict(text="But soon the pipe is full of warm gas, packed with stolen heat, and the cooling stops.",
         cam=EVAP, pegs="worried",
         do=[("full", "w:full", 1, 1.0, "out"), ("heatflow", "w:stops", 0, 0.5, "in"), ("frost", "w:stops", 0, 0.8, "in")],
         keys=[("full of warm gas", RED), ("cooling stops", RED)],
         pops=[dict(kind="warn", at="w:stops", text="cooling stopped", pos="bc", until="end+0.2")],
         sfx=[("w:stops", "sting")]),
    dict(text="So a pump squeezes that gas hard. Squeezed gas gets hot, way hotter than your kitchen. "
              "That's the compressor.",
         cam=COMP, pegs="happy",
         do=[("comp", "w:pump", 1, 0.5, "back"), ("suction", "w:pump", 1, 1.0, "out"), ("run", "w:squeezes", 1, 0.2, "lin"),
             ("hot", "w:hot", 1, 0.8, "out"), ("full", "w:squeezes", 0, 1.0, "io")],
         keys=[("squeezes that gas|squeeze the gas", INK), ("way hotter|hotter than the kitchen", RED),
               ("compressor", INK)],
         fix="w:compressor",
         pops=[dict(kind="meter", at="w:hot", text="GAS TEMP", **{"from": 0.2, "to": 0.95}, fmt="", color=RED,
                    anim=1.2, pos="tl", until="end+0.2")],
         sfx=[("w:pump", "pop"), ("w:squeezes", "rumble")]),
    dict(text="Now the hot gas flows through a grid of pipes outside the box, dumps its heat into the room, and "
              "turns back into a liquid. That's the condenser.",
         cam=COND, pegs="neutral",
         do=[("cond", "w:grid", 1, 1.4, "out"), ("dump", "w:dumps", 1, 0.6, "out")],
         keys=[("grid of pipes", INK), ("dumps its heat|heat -> your kitchen", RED), ("back into a liquid", BLUE),
               ("condenser", INK)],
         fix="w:condenser",
         pops=[dict(kind="arrow", at="w:dumps", xyz=(1.6, 1.4, 2.2), text="heat out", color=RED, off=(0.18, -0.1),
                    until="end+0.2", sound=False)],
         sfx=[("w:grid", "whoosh")]),
    dict(text="Finally, the liquid squeezes through a tiny tube, the pressure drops, and it's ready to boil cold "
              "again. That's the capillary tube.",
         cam=((0.9, 0.5, 2.9), 260), pegs="happy",
         do=[("cap", "w:tiny", 1, 1.2, "out"), ("frost", "w:cold", 1, 0.8, "out"), ("heatflow", "w:cold", 1, 0.6, "out")],
         keys=[("tiny tube", INK), ("pressure drops|pressure drops = cold", BLUE), ("capillary tube", INK)],
         fix="w:capillary",
         sfx=[("w:tiny", "click")]),
    dict(text="Loop it forever, and heat keeps flowing out of the box and into your kitchen.",
         cam=WIDE, pegs="happy",
         do=[("flow", "w:loop", 1, 0.8, "out")],
         keys=[("loop it forever", INK), ("out of the box|inside -> kitchen", BLUE)],
         pops=[dict(kind="equation", at="w:loop", parts=["boil", "->", "squeeze", "->", "cool", "->", "expand"],
                    colors=[BLUE, INK, RED, INK, ORANGE, INK, BLUE], pos="bc", until="end+0.2", step=0.3)]),
    dict(text="But nonstop cooling would freeze your milk solid. So a thermostat switches the compressor on and off "
              "to hold about four degrees.",
         cam=((0.9, 0.9, 1.4), 220), pegs="shocked",
         do=[("frozen", "w:freeze", 1, 0.5, "out"), ("thermo", "w:thermostat", 1, 0.5, "back"),
             ("frozen", "w:thermostat", 0, 0.8, "io"),
             ("cyc", "w:switches", 1, 0.01, "lin"), ("cyc", "w:on+0.9", 0, 0.01, "lin"),
             ("cyc", "w:on+1.9", 1, 0.01, "lin"), ("cyc", "w:on+2.9", 0, 0.01, "lin"), ("cyc", "w:on+3.9", 1, 0.01, "lin"),
             ("tin", "w:switches", 0.3, 0.9, "io"), ("tin", "w:on+0.9", 0.7, 1.0, "io"), ("tin", "w:on+1.9", 0.3, 1.0, "io"),
             ("tin", "w:on+2.9", 0.7, 1.0, "io"), ("tin", "w:on+3.9", 0.3, 1.0, "io")],
         keys=[("freeze your milk solid", RED), ("thermostat", INK), ("on and off", INK), ("four degrees|~4°C", BLUE)],
         fix="w:thermostat",
         pops=[dict(kind="graph", at="w:switches", title="FRIDGE TEMP", track="tin", window=5.0, color=BLUE, pos="tl",
                    until="end+0.2")],
         sfx=[("w:freeze", "sting"), ("w:thermostat", "click")]),
    dict(text="Cold air sinks and pools at the bottom, so a small fan pushes it across the coils and around every "
              "shelf.",
         cam=INSIDE, pegs="neutral",
         do=[("cyc", 0.1, 0, 0.01, "lin"), ("pool", "w:sinks", 1, 0.8, "out"), ("fan", "w:fan", 1, 0.5, "back"),
             ("pool", "w:pushes", 0, 1.0, "io"), ("air", "w:pushes", 1, 0.6, "out")],
         keys=[("cold air sinks", RED), ("small fan", INK), ("around every shelf", BLUE)],
         fix="w:fan",
         sfx=[("w:fan", "whoosh")]),
    dict(text="The cold coils also pull water out of the air, and it freezes into a block of ice. So every few hours, "
              "a little heater melts it off. That's auto defrost.",
         cam=EVAP, pegs="worried",
         do=[("air", 0.2, 0, 0.5, "in"), ("ice", "w:water", 1, 1.6, "out"), ("heater", "w:heater", 1, 0.3, "out"),
             ("ice", "w:melts", 0, 1.6, "io"), ("heater", "end-0.5", 0, 0.4, "in")],
         keys=[("block of ice", RED), ("little heater", INK), ("auto defrost", INK)],
         fix="w:heater",
         sfx=[("w:ice", "sting"), ("w:heater", "click")]),
    dict(text="And every time you open the door, the cold air pours out like water. So the rubber seal hides a "
              "magnet that snaps it shut.",
         cam=((0.9, 1.6, 1.6), 190), pegs="shocked",
         do=[("doorvis", 0.05, 1, 0.3, "out"), ("door", "w:open", 1, 0.6, "out"), ("spill", "w:pours", 1, 0.5, "out"),
             ("seal", "w:magnet", 1, 0.4, "out"), ("spill", "w:snaps", 0, 0.4, "in"), ("door", "w:snaps", 0, 0.35, "in")],
         keys=[("cold air pours out", RED), ("rubber seal", INK), ("magnet|magnet strip", INK), ("snaps it shut", BLUE)],
         fix="w:magnet",
         sfx=[("w:pours", "whoosh"), ("w:snaps", "thud")]),
    dict(text="So next time you feel warm air around your fridge, that's the heat it just pulled out of your food.",
         cam=((1.2, 1.0, 1.8), 175), pegs="happy", pose="point",
         do=[("doorvis", 0.1, 0, 0.3, "in"), ("dump", "w:warm", 1, 0.3, "out"), ("glowfood", "w:food", 1, 0.4, "out")],
         keys=[("warm air|warm air = food heat", RED), ("pulled out of your food", BLUE)],
         sfx=[("w:warm", "whoosh")]),
    dict(text="And that's how you build a fridge. Technically, it's a heater for your kitchen. Follow for more.",
         cam=WIDE, pegs="happy", pose="cheer", min=8.4,
         do=[("done", "w:build", 1, 0.3, "out"), ("glowfood", 0.2, 0, 0.3, "in")],
         keys=[("build a fridge|you built a fridge!", BLUE), ("heater for your kitchen", RED)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:build", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(evap=0, box=0, food=0, liquid=0, boil=0, kitchen=0, heatflow=0, frost=0, full=0, comp=0, suction=0,
               run=0, hot=0, cond=0, dump=0, cap=0, flow=0, frozen=0, thermo=0, cyc=1, tin=0.3, pool=0, fan=0, air=0,
               ice=0, heater=0, doorvis=0, door=0, spill=0, seal=0, glowfood=0, done=0)

# cabinet: x 0..1.4, y 0..1.5 (front y = 1.5 is the open cutaway), inner floor z = 0.5, top z = 3.2
X1, Y1, ZF, ZT = 1.4, 1.5, 0.5, 3.2
ZD = 2.2                    # freezer divider
CAB = (240, 242, 246)
INNER = (226, 236, 244)
FLOOR = (214, 204, 190)

EVAP_PATH = [(0.07, 0.25, 2.95), (0.07, 1.3, 2.95), (0.07, 1.3, 2.8), (0.07, 0.25, 2.8), (0.07, 0.25, 2.65),
             (0.07, 1.3, 2.65), (0.07, 1.3, 2.5), (0.07, 0.25, 2.5)]
SUCTION = [(0.07, 0.25, 2.5), (0.07, 0.06, 2.5), (0.07, 0.06, 3.32), (1.62, 0.06, 3.32), (1.62, 0.06, 0.45),
           (1.62, 0.45, 0.45)]
COMP_C = (1.9, 0.65)
DISCH = [(1.9, 0.65, 0.62), (1.9, 0.65, 0.75), (1.55, 1.38, 0.75)]
COND_PATH = [(1.55, 1.38, 0.75)]
for _i in range(10):
    _z = 0.75 + 0.2 * _i
    _ya, _yb = (1.38, 0.22) if _i % 2 == 0 else (0.22, 1.38)
    if _i:
        COND_PATH.append((1.55, _ya, _z))
    COND_PATH.append((1.55, _yb, _z))
CAP_PATH = [COND_PATH[-1], (1.55, 1.38, 3.42), (1.55, 0.25, 3.42), (0.07, 0.25, 3.42), (0.07, 0.25, 2.95)]
LOOP = EVAP_PATH + SUCTION[1:] + DISCH + COND_PATH[1:] + CAP_PATH[1:]


def _ls(cam):
    """Callout size: 0.11 world units, but never smaller than ~3.3% of the frame width."""
    return max(0.11, 0.033 * cam.img.width / cam.s)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _seglen(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


_L_EVAP, _L_SUC, _L_DIS, _L_COND = (_seglen(EVAP_PATH), _seglen(SUCTION), _seglen(DISCH), _seglen(COND_PATH))
_L_TOT = _seglen(LOOP)


def _loop_color(s):
    """Refrigerant colour along the loop: cold blue -> warm gas -> hot red -> cooling -> blue."""
    d = s * _L_TOT
    if d < _L_EVAP:
        return ICE
    d -= _L_EVAP
    if d < _L_SUC:
        return mix(ICE, (170, 200, 230), d / _L_SUC)
    d -= _L_SUC
    if d < _L_DIS:
        return RED
    d -= _L_DIS
    if d < _L_COND:
        return mix(RED, (250, 190, 120), d / _L_COND)
    return mix((250, 190, 120), ICE, 0.7)


class FridgeScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (232, 238, 246), (250, 246, 238), clouds=0)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        if g("kitchen") > 0.01:
            self._kitchen(cam, g("kitchen"))
        box = g("box")
        if box > 0.01:
            self._cabinet_back(cam, tr, t, _sm(box))
        self._evaporator(cam, tr, t)
        if box > 0.01:
            self._inside(cam, tr, t)
            self._cabinet_front(cam, tr, t, _sm(box))
        self._machine(cam, tr, t)
        if g("doorvis") > 0.01:
            self._door(cam, tr, t)
        if g("kitchen") > 0.5:
            self._pegs(cam, tr, t)

    # ------------------------------------------------------------- room
    def _kitchen(self, cam, k):
        k = _sm(k)
        cam.poly([(-3, -0.6, 0), (5, -0.6, 0), (5, 5, 0), (-3, 5, 0)], FLOOR)
        h = 4.2 * k
        cam.poly([(-3, -0.6, 0), (5, -0.6, 0), (5, -0.6, h), (-3, -0.6, h)], (236, 230, 218), (200, 192, 178), 0.01)
        cam.poly([(-3, -0.6, 0), (-3, 5, 0), (-3, 5, h), (-3, -0.6, h)], (226, 220, 206), (200, 192, 178), 0.01)
        for i in range(1, 12):
            x = -3 + i * 0.7
            cam.line([(x, -0.6, 0), (x, 5, 0)], shade(FLOOR, -0.06), 0.008, caps=False)
        sh = ShadowLayer(cam)
        sh.ao_edge((-3, -0.6, 0), (5, -0.6, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
        sh.box_on_plane(0, 0, 0, X1, Y1, ZT, "y", -0.6, 150, ((-3, 5), (-0.6, -0.6), (0, 4.2)))
        sh.box_on_plane(0, 0, 0, 2.2, Y1, ZT, "z", 0.0, 170)
        sh.apply(cam.img, 0.26, 2.4)
        # counter on the left wall for context
        cam.box(-3, 1.6, 0, 1.2, 2.4, 1.0, (236, 236, 240), top_color=(200, 190, 176))
        cam.box(-2.7, 2.2, 1.0, 0.35, 0.35, 0.45, (220, 80, 70))

    # ------------------------------------------------------------- cabinet
    def _cabinet_back(self, cam, tr, t, k):
        zt = ZF + (ZT - ZF) * k
        cam.box(0, 0, 0, X1, Y1, ZF, (200, 204, 214), top_color=INNER)          # plinth / machine bay cover
        kit.plate(cam, "y", Y1, 0.1, 0.12, X1 - 0.1, 0.38, (60, 64, 76))       # vent grille
        for i in range(6):
            x = 0.2 + i * 0.2
            cam.line([(x, Y1 + 0.002, 0.15), (x, Y1 + 0.002, 0.35)], (110, 116, 130), 0.012, caps=False)
        cam.poly([(0, 0, ZF), (X1, 0, ZF), (X1, 0, zt), (0, 0, zt)], shade(INNER, -0.06))
        cam.poly([(0, 0, ZF), (0, Y1, ZF), (0, Y1, zt), (0, 0, zt)], shade(INNER, -0.14))
        if k > 0.9:
            # freezer divider + shelves (glass)
            cam.poly([(0, 0, ZD), (X1, 0, ZD), (X1, Y1, ZD), (0, Y1, ZD)], (236, 242, 248), (180, 190, 204), 0.008)
            for z in (1.0, 1.6):
                cam.poly([(0, 0, z), (X1, 0, z), (X1, Y1 - 0.05, z), (0, Y1 - 0.05, z)], (210, 232, 244), (160, 186, 204),
                         0.008)
            fr = tr.get("frost", t)
            if fr > 0.01:
                cam.poly([(0.005, 0.2, 2.38), (0.005, 1.35, 2.38), (0.005, 1.35, 3.05), (0.005, 0.2, 3.05)],
                         mix(INNER, (245, 250, 255), fr))

    def _cabinet_front(self, cam, tr, t, k):
        zt = ZF + (ZT - ZF) * k
        # right wall (solid, white outside) + cut edges of the cutaway
        cam.box(X1 - 0.08, 0, ZF, 0.08, Y1, zt - ZF, CAB, top_color=shade(CAB, 0.1))
        cam.box(-0.08, 0, ZF, 0.08, Y1, zt - ZF, CAB, faces="tl")

    def _inside(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        fk = _sm(g("food"))
        if fk > 0.01:
            fz = g("frozen")
            hot = g("glowfood")
            # milk carton, apple, cheese, bottle, cake
            milk = mix((250, 250, 252), (200, 230, 255), fz)
            cam.box(0.35, 0.9, 1.0, 0.22, 0.22, 0.42 * fk, milk)
            cam.poly([(0.35, 1.12, 1.0 + 0.42 * fk), (0.57, 1.12, 1.0 + 0.42 * fk), (0.57, 1.01, 1.0 + 0.52 * fk),
                      (0.35, 1.01, 1.0 + 0.52 * fk)], shade(milk, -0.05), (160, 160, 170), 0.006)
            kit.plane_text(cam, "y", 1.121, 0.46, 1.18, "MILK", 0.07, BLUE, max_w=0.19)
            if fz > 0.3:
                kit.label(cam, (0.46, 1.0, 1.65), "FROZEN!", 0.08, (255, 255, 255), BLUE)
            cam.poly(cam.disc_pts((0.85, 1.1, 1.08), 0.1 * fk, "y", 16), (220, 60, 60), (150, 30, 30), 0.006)
            cam.box(0.25, 0.45, 1.6, 0.4, 0.3, 0.16 * fk, (250, 210, 80))
            cam.box(0.8, 0.8, 1.6, 0.35, 0.35, 0.22 * fk, (240, 170, 190))
            cam.box(0.75, 0.35, 0.5, 0.18, 0.18, 0.45 * fk, (90, 170, 110))
            cam.box(0.3, 0.5, 0.5, 0.35, 0.3, 0.25 * fk, (230, 200, 150))
            cam.box(0.4, 0.6, ZD, 0.5, 0.45, 0.2 * fk, (200, 220, 240))        # freezer tub
            if hot > 0.01:
                for c in ((0.46, 1.0, 1.5), (0.95, 1.0, 1.85), (0.45, 0.6, 1.8)):
                    kit.heat_wisps(cam, c, t, RED, 2, 0.35, 0.12, hot, 0.02)
        # heat flowing from the food into the evaporator
        hf = g("heatflow")
        if hf > 0.01 and fk > 0.5:
            srcs = [(0.46, 1.0, 1.45), (0.95, 0.95, 1.85), (0.6, 0.6, 2.42)]
            for j, s0 in enumerate(srcs):
                for i in range(3):
                    f = (t * 0.45 + i / 3 + j * 0.21) % 1.0
                    p = (s0[0] + (0.1 - s0[0]) * f, s0[1] + (0.75 - s0[1]) * f, s0[2] + (2.7 - s0[2]) * f)
                    kit.glow_dot(cam, p, 0.035 * hf * (1 - 0.4 * f), mix(RED, ORANGE, f))
        # thermostat dial on the left wall
        th = g("thermo")
        if th > 0.01:
            kit.plate(cam, "x", 0.01, 1.05, 1.75, 1.4, 2.05, (250, 250, 252), (150, 156, 170))
            kit.plane_text(cam, "x", 0.012, 1.22, 1.9, "4°C", 0.13 * _sm(th), BLUE, max_w=0.3)
            parts.led(cam, (0.02, 1.36, 2.0), GREEN if g("cyc") > 0.5 else (90, 96, 110), g("cyc") > 0.5, 0.025)
            kit.label(cam, (0.02, 1.22, 2.25), "THERMOSTAT", _ls(cam), (255, 255, 255), BLUE)
        # cold air pooling + fan + circulation
        pool = g("pool")
        if pool > 0.01:
            for i in range(4):
                f = (t * 0.35 + i / 4) % 1.0
                z = 1.9 - f * 1.3
                cam.line([(0.15, 0.3 + 0.25 * i, z), (1.2, 0.3 + 0.25 * i, z)], mix(ICE, (255, 255, 255), 0.4 + 0.4 * f),
                         0.02 * pool, caps=False)
            cam.poly([(0.02, 0.02, 0.52), (1.3, 0.02, 0.52), (1.3, 1.45, 0.52), (0.02, 1.45, 0.52)],
                     mix(INNER, ICE, 0.45 * pool))
        fan = g("fan")
        if fan > 0.01:
            r = 0.2 * _sm(fan)
            kit.plate(cam, "y", 0.01, 0.42, 1.78, 0.98, 2.15, (200, 206, 218), (150, 156, 170))
            parts.fan(cam, (0.7, 0.03, 1.96), r, "y", t * 14 * g("air") + t * 2, (110, 116, 130))
            kit.label(cam, (0.7, 0.05, 2.33), "FAN", _ls(cam), (255, 255, 255), INK)
        air = g("air")
        if air > 0.01:
            path = [(0.7, 0.15, 1.95), (0.7, 1.25, 1.9), (0.55, 1.35, 1.3), (0.5, 1.35, 0.7), (0.4, 0.3, 0.62),
                    (0.2, 0.2, 1.2), (0.12, 0.6, 2.6)]
            for i in range(7):
                kit.packet(cam, path, (t * 0.28 + i / 7) % 1.0, ICE, r=0.035 * air, trail=0.06)

    # ------------------------------------------------------------- refrigerant loop
    def _evaporator(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        e = g("evap")
        if e <= 0.01:
            return
        full = g("full")
        col = mix(mix((176, 184, 198), ICE, g("liquid")), ORANGE, full * 0.8)
        pts = kit.path_prefix(EVAP_PATH, _sm(e))
        parts.pipe(cam, pts, 0.035, col)
        lq = g("liquid")
        if lq > 0.01 and g("boil") > 0.01 and full < 0.5:
            for i in range(10):
                f = (t * 0.5 + i / 10) % 1.0
                p, _ = kit.path_point(EVAP_PATH, f)
                x, y = cam.p(p[0], p[1], p[2] + 0.03 * math.sin(t * 9 + i))
                r = 0.018 * cam.s * g("boil")
                cam.d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255), width=max(1, int(0.006 * cam.s)))
        if full > 0.01:
            for i in range(12):
                p, _ = kit.path_point(EVAP_PATH, (i + 0.5) / 12)
                kit.glow_dot(cam, (p[0] + 0.02, p[1], p[2] + 0.01 * math.sin(t * 7 + i)), 0.03 * full, RED)
        ice = g("ice")
        if ice > 0.01:
            k = _sm(ice)
            cam.box(0.02, 0.18, 2.42, 0.14 * k + 0.02, 1.2, 0.6 * k, (214, 236, 252), top_color=(236, 246, 255))
            kit.label(cam, (0.1, 0.8, 2.6 + 0.6 * k), "ICE", 0.09, (255, 255, 255), BLUE)
        ht = g("heater")
        if ht > 0.01:
            cam.line([(0.1, 0.2, 2.42), (0.1, 1.35, 2.42)], mix((120, 60, 50), (255, 90, 40), ht), 0.035)
            kit.label(cam, (0.12, 1.2, 2.25), "HEATER", _ls(cam), (255, 255, 255), RED)
            if ice > 0.05:
                for i in range(4):
                    f = (t * 1.2 + i / 4) % 1.0
                    x, y = cam.p(0.12, 0.35 + 0.28 * i, 2.4 - f * 0.4)
                    r = 0.02 * cam.s
                    cam.d.ellipse((x - r, y - r, x + r, y + r * 1.4), fill=ICE)
        if e > 0.9 and g("heatflow") > 0.3 and g("comp") < 0.5:
            kit.label(cam, (0.08, 0.8, 3.1), "EVAPORATOR", _ls(cam), (255, 255, 255), BLUE)

    def _machine(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        su = g("suction")
        if su > 0.01:
            parts.pipe(cam, kit.path_prefix(SUCTION, _sm(su)), 0.03, mix((150, 170, 200), ICE, 0.4))
        c = g("comp")
        if c > 0.01:
            k = _sm(c)
            run = g("run") * (g("cyc") if g("thermo") > 0.01 else 1.0)
            sh = 0.012 * run * math.sin(t * 60)
            cx, cy = COMP_C
            body = mix((50, 54, 64), (170, 60, 50), 0.6 * g("hot") * (0.4 + 0.6 * run))
            cam.box(cx - 0.32, cy - 0.28, 0, 0.64, 0.56, 0.06, (90, 96, 110))
            cam.box(cx - 0.26 + sh, cy - 0.24, 0.06, 0.52, 0.48, 0.38 * k, body)
            cam.poly(cam.disc_pts((cx + sh, cy, 0.06 + 0.38 * k), 0.22 * k, "z", 24), shade(body, 0.2),
                     shade(body, -0.4), 0.008)
            if run > 0.5:
                parts.led(cam, (cx + 0.27, cy + 0.1, 0.3), GREEN, True, 0.03)
            if c > 0.6:
                kit.label(cam, (cx, cy + 0.1, 0.85), "COMPRESSOR", _ls(cam), (255, 255, 255), INK)
            if g("hot") > 0.01:
                parts.pipe(cam, DISCH, 0.03, RED)
        cd = g("cond")
        if cd > 0.01:
            pts = kit.path_prefix(COND_PATH, _sm(cd))
            # fins/wires of the grid
            for j in range(6):
                y = 0.3 + j * 0.2
                cam.line([(1.56, y, 0.72), (1.56, y, 0.72 + 1.86 * _sm(cd))], (60, 64, 76), 0.008, caps=False)
            n = max(1, len(COND_PATH) - 1)
            for j, (a, b) in enumerate(zip(pts, pts[1:])):
                parts.pipe(cam, [a, b], 0.028, mix(RED, (250, 190, 120), j / n))
            if cd > 0.6:
                kit.label(cam, (1.6, 0.8, 2.8), "CONDENSER", _ls(cam), (255, 255, 255), RED)
        dp = g("dump")
        if dp > 0.01:
            for z in (1.0, 1.6, 2.2):
                kit.heat_wisps(cam, (1.75, 0.8, z), t, RED, 3, 0.7, 0.8, dp, 0.025, axis="x")
        cp = g("cap")
        if cp > 0.01:
            pts = kit.path_prefix(CAP_PATH, _sm(cp))
            cam.line(pts, (150, 100, 60), 0.022)
            cam.line(pts, (220, 150, 90), 0.014)
            if cp > 0.6 and g("flow") < 0.5:
                kit.label(cam, (0.8, 0.25, 3.6), "CAPILLARY TUBE", _ls(cam), (255, 255, 255), (180, 110, 60))
        fl = g("flow")
        if fl > 0.01:
            spd = 0.07 * (g("cyc") if g("thermo") > 0.01 else 1.0)
            for i in range(16):
                s = (t * 0.07 + i / 16) % 1.0
                if g("thermo") > 0.01 and g("cyc") < 0.5:
                    s = (i / 16 + 0.03) % 1.0
                p, _ = kit.path_point(LOOP, s)
                kit.glow_dot(cam, p, 0.04 * fl, _loop_color(s))

    # ------------------------------------------------------------- door
    def _door(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        vis = _sm(g("doorvis"))
        a = g("door") * 1.75
        w = X1
        z0, z1 = ZF - 0.02, ZT
        ex, ey = w * math.cos(a), Y1 + w * math.sin(a)
        col = mix((245, 246, 250), (255, 255, 255), 0.5)
        pts = [(0, Y1, z0), (ex, ey, z0), (ex, ey, z1), (0, Y1, z1)]
        if vis < 0.99:
            pts = [(0, Y1, z0), (ex * vis, Y1 + (ey - Y1) * vis, z0), (ex * vis, Y1 + (ey - Y1) * vis, z1), (0, Y1, z1)]
        cam.poly(pts, shade(col, -0.04 if a < 0.8 else -0.12), (150, 156, 170), 0.012)
        if a < 0.1:
            cam.box(1.15, Y1, 1.6, 0.06, 0.06, 0.8, (190, 196, 206))
            kit.plate(cam, "y", Y1 + 0.003, 0.0, ZD - 0.01, X1, ZD + 0.01, (180, 186, 198))
        seal = g("seal")
        if seal > 0.01:
            edge = [(0, Y1 + 0.01, z0), (ex, ey + 0.01, z0), (ex, ey + 0.01, z1), (0, Y1 + 0.01, z1), (0, Y1 + 0.01, z0)]
            cam.line(edge, mix((200, 200, 210), (60, 64, 76), seal), 0.04 * seal)
            kit.label(cam, (ex, ey + 0.1, 2.6), "MAGNET SEAL", _ls(cam), (255, 255, 255), INK)
        sp = g("spill")
        if sp > 0.01:
            for i in range(5):
                f = (t * 0.6 + i / 5) % 1.0
                pts = []
                for j in range(9):
                    q = j / 8
                    pts.append((0.2 + 0.25 * i + 0.05 * math.sin(t * 3 + j), Y1 + 0.1 + (f * 1.6) * q,
                                max(0.03, 1.2 - 1.2 * (f * q) ** 0.7 - 0.3 * q)))
                cam.line(pts, mix(ICE, (255, 255, 255), f), 0.035 * sp * (1 - f * 0.5), caps=False)

    def _pegs(self, cam, tr, t):
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (2.35, 1.95, 0), PEG_COLORS[1], expr, t, 1.5, (-0.6, -0.5), seed=2, pose=tr.peg_pose(t),
                react=react, floor=FLOOR)


VIDEO = dict(
    slug="fridge",
    title="How does a fridge make cold out of electricity?",
    steps=STEPS, scene=FridgeScene, initial=INITIAL, tracker=dict(label="FIXES"),
)
