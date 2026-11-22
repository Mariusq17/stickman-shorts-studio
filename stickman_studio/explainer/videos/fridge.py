"""How does a fridge make cold out of electricity? - built step by step (idea #11, open loop).

Dollhouse section cut at the plane y = 0: we look into the fridge from the side (door on the left, back with the
condenser coil on the right, facing the camera). The hook claims a fridge does not make cold; the answer (it moves
heat out of the box and dumps it out the back) comes near the end, with the camera swinging round to the back.
"""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer
from ..lib.story import open_loop
from ..qa import shift_spec

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)
SHELL = (238, 242, 246)
FOAM = (244, 222, 150)             # insulation in the cut
INNER = (214, 226, 236)
COMP = (52, 56, 66)                # compressor (QA end object)
EVAPBOX = (120, 170, 210)          # evaporator header (QA end object)
COLD, HOT = (80, 160, 255), (240, 90, 60)

X0, X1, YB, Z0, Z1 = 0.2, 1.0, -0.7, 0.1, 2.0       # cabinet
CX0, CX1, CZ0, CZ1 = 0.3, 0.9, 0.56, 1.9            # food compartment
EVAP = [(0.5, -0.66, 1.84), (0.86, -0.66, 1.84), (0.86, -0.66, 1.76), (0.5, -0.66, 1.76), (0.5, -0.66, 1.68),
        (0.86, -0.66, 1.68), (0.86, -0.66, 1.6)]
SUCTION = [(0.86, -0.66, 1.6), (0.96, -0.5, 1.6), (1.06, -0.45, 1.6), (1.06, -0.45, 0.4), (0.98, -0.4, 0.33)]
COND = [(1.0, -0.2, 0.42)] + [(1.06 if i % 2 == 0 else 1.06, -0.1 - (0.5 if i % 2 else 0.0), 0.5 + i * 0.12)
                              for i in range(12)]
CAPI = [COND[-1], (1.06, -0.62, 1.86), (0.94, -0.66, 1.86), (0.5, -0.66, 1.86), (0.5, -0.66, 1.84)]

WIDE = ((0.6, -0.35, 1.05), 255)
CAB = ((0.62, -0.3, 1.2), 330)
EVC = ((0.7, -0.5, 1.72), 470)
COMPC = ((0.9, -0.3, 0.45), 430)
DOORC = ((0.05, -0.2, 1.0), 270)
BACKC = ((1.15, -0.35, 1.1), 380)
ISO_P = 35.264

STEPS = [
    dict(text="If you put your food in a box with thick walls, you've got the world's simplest fridge.",
         cam=((0.6, -0.3, 1.2), 420), pegs="neutral",
         cams=[("w:walls", CAB, 1.0), ("w:simplest", WIDE, 1.4)],
         do=[("food", 0.0, 1, 0.6, "back"), ("cab", "w:box", 1, 0.9, "out"), ("room", "w:simplest", 1, 1.2, "out")],
         keys=[("your food", INK), ("thick walls", INK), ("simplest fridge", BLUE)],
         sfx=[("w:food", "pop"), ("w:box", "pop"), ("w:simplest", "whoosh")]),
    dict(text="But thick walls only slow heat down. Wait a day, and your milk is as warm as the kitchen.",
         cam=CAB, pegs="worried",
         do=[("heatin", "w:heat", 1, 0.6, "out"), ("temp", "w:wait", 0.9, 2.0, "io")],
         keys=[("only slow heat down", RED), ("as warm as the kitchen", RED)],
         pops=[dict(kind="graph", at="w:heat", title="MILK TEMPERATURE", track="temp", window=5.0, color=RED,
                    pos="tr", until="end+0.2")]),
    dict(text="So you run a pipe inside the box, filled with a liquid that boils far below freezing. Boiling soaks "
              "up heat, the same way sweat cools your skin. That's the evaporator.",
         cam=EVC, pegs="happy", pose="think",
         cams=[("w:soaks", CAB, 1.3)],
         do=[("evap", "w:pipe", 1, 1.0, "out"), ("boil", "w:boils", 1, 0.4, "out"), ("heatin", "w:soaks", 0, 0.5, "in"),
             ("toevap", "w:soaks", 1, 0.5, "out"), ("temp", "w:soaks", 0.25, 2.5, "io")],
         keys=[("boils far below freezing", INK), ("sweat cools your skin", INK), ("evaporator", BLUE)],
         pops=[dict(kind="meter", at="w:sweat", text="INSIDE", **{"from": 0.9, "to": 0.2}, color=BLUE, fmt="COLD",
                    anim=1.6, pos="bl", until="end+0.2")],
         fix="w:evaporator", sfx=[("w:boils", "pop"), ("w:evaporator", "ding")]),
    dict(text="But once all that liquid has boiled into gas, it can't soak up anything else.",
         cam=EVC, pegs="worried",
         do=[("boil", 0.0, 0, 0.6, "in"), ("gas", "w:gas", 1, 0.4, "out"), ("toevap", "w:can't", 0, 0.6, "in"),
             ("temp", "w:soak", 0.6, 1.6, "io")],
         keys=[("boiled into gas", RED), ("can't soak up", RED)]),
    dict(text="So a pump outside the box sucks the gas out and squeezes it hard. That's the compressor. And squeezed "
              "gas gets hot.",
         cam=COMPC, pegs="happy",
         cams=[("w:hot", ((0.95, -0.35, 0.8), 330), 1.2)],
         do=[("comp", "w:pump", 1, 0.6, "back"), ("suction", "w:sucks", 1, 0.8, "out"), ("compon", "w:squeezes", 1, 0.1, "lin"),
             ("gas", "w:squeezes", 0, 0.6, "in")],
         keys=[("pump outside the box", INK), ("squeezes it hard", INK), ("compressor", BLUE), ("gets hot", RED)],
         fix="w:compressor", sfx=[("w:pump", "slap"), ("w:compressor", "ding")]),
    dict(text="Then the hot gas runs through a long zigzag pipe outside the box. It gives its heat to the kitchen air "
              "and turns back into a liquid. That's the condenser.",
         cam=((1.08, -0.35, 1.1), 320), pegs="happy",
         do=[("cond", "w:zigzag", 1, 1.2, "out"), ("heatout", "w:gives", 1, 0.6, "out"),
             ("cam_yaw", "w:zigzag", 70.0, 1.8, "smooth"), ("cam_pitch", "w:zigzag", 22.0, 1.8, "smooth"),
             ("cam_yaw", "w:condenser", 45.0, 1.6, "smooth"), ("cam_pitch", "w:condenser", ISO_P, 1.6, "smooth"),
             ("heatout", "end-0.3", 0, 0.3, "in")],
         keys=[("long zigzag pipe", INK), ("gives its heat", INK), ("back into a liquid", INK), ("condenser", BLUE)],
         fix="w:condenser", sfx=[("w:zigzag", "whoosh"), ("w:condenser", "ding")]),
    dict(text="But that liquid is still squeezed. So it's forced through a tiny tube into the box, the pressure drops, "
              "and it turns ice cold, ready to boil again. That's the expansion valve.",
         cam=CAB, pegs="happy",
         cams=[("w:tiny", EVC, 1.2), ("w:expansion", CAB, 1.2)],
         do=[("capi", "w:tiny", 1, 0.9, "out"), ("boil", "w:ice", 1, 0.4, "out")],
         keys=[("tiny tube", INK), ("pressure drops", INK), ("ice cold", BLUE), ("expansion valve", INK)],
         fix="w:expansion", sfx=[("w:tiny", "pop"), ("w:expansion", "ding")]),
    dict(text="Round and round, the same liquid goes forever. That's the refrigeration cycle.",
         cam=WIDE, pegs="happy",
         cams=[("w:refrigeration", ((0.8, -0.4, 1.1), 300), 1.4)],
         do=[("flow", 0.0, 1, 0.4, "out"), ("toevap", 0.0, 1, 0.5, "out"), ("temp", 0.0, 0.2, 2.0, "io")],
         keys=[("round and round", INK), ("refrigeration cycle", BLUE)],
         pops=[dict(kind="equation", at="w:round", parts=["boil", "squeeze", "cool", "expand"],
                    colors=[BLUE, RED, ORANGE, BLUE], step=0.45, pos="tr", until="end+0.2")]),
    dict(text="But run it nonstop, and your lettuce freezes solid.",
         cam=CAB, pegs="shocked",
         do=[("frozen", "w:freezes", 1, 0.6, "out"), ("temp", "w:nonstop", 0.0, 1.2, "io")],
         keys=[("nonstop", RED), ("freezes solid", RED)],
         pops=[dict(kind="warn", at="w:freezes", text="frozen lettuce", pos="bl", until="end")],
         sfx=[("w:freezes", "sting")]),
    dict(text="So a thermostat watches the temperature and switches the compressor on and off. That's the hum that "
              "starts and stops.",
         cam=CAB, pegs="happy",
         cams=[("w:compressor", COMPC, 1.2), ("w:hum", WIDE, 1.2)],
         do=[("frozen", 0.0, 0, 0.8, "in"), ("thermo", "w:thermostat", 1, 0.5, "back"), ("cycle", "w:switches", 1, 0.1, "lin"),
             ("temp", "w:switches", 0.25, 1.4, "io")],
         keys=[("thermostat", BLUE), ("on and off", INK), ("hum|that hum!", INK)],
         fix="w:thermostat", sfx=[("w:thermostat", "pop"), ("w:hum", "ding")]),
    dict(text="Then someone opens the door, and the cold air spills out at their feet.",
         cam=DOORC, pegs="shocked",
         do=[("cycle", 0.0, 0, 0.1, "lin"), ("door", "w:opens", 1, 0.9, "io"), ("spill", "w:cold", 1, 0.6, "out")],
         keys=[("opens the door", INK), ("spills out|cold air spills out", RED)],
         sfx=[("w:opens", "whoosh")]),
    dict(text="So the rubber seal around the door has magnets inside. They pull it shut and close every gap.",
         cam=DOORC, pegs="happy",
         cams=[("w:magnets", ((0.1, -0.1, 1.0), 400), 1.2), ("w:gap", DOORC, 1.2)],
         do=[("spill", 0.0, 0, 0.6, "in"), ("mag", "w:magnets", 1, 0.4, "out"), ("door", "w:pull", 0, 0.7, "in")],
         keys=[("rubber seal", INK), ("magnets inside", BLUE), ("close every gap", INK)],
         fix="w:magnets", sfx=[("w:pull", "slap")]),
    dict(text="But every time the door opens, moist air gets in and freezes onto the cold pipe as frost.",
         cam=EVC, pegs="worried",
         do=[("mag", 0.0, 0, 0.4, "in"), ("frost", "w:moist", 1, 2.2, "io")],
         keys=[("moist air", INK), ("frost", RED)]),
    dict(text="So a small heater warms the pipe now and then, and the frost melts away. That's the defrost heater.",
         cam=EVC, pegs="happy",
         do=[("heater", "w:heater", 1, 0.3, "out"), ("frost", "w:melts", 0, 1.4, "io"), ("drip", "w:melts", 1, 0.3, "out"),
             ("heater", "w:defrost", 0, 0.4, "in"), ("drip", "end-0.3", 0, 0.3, "in")],
         keys=[("small heater", INK), ("frost melts away", BLUE), ("defrost heater", INK)],
         fix="w:defrost", sfx=[("w:heater", "pop"), ("w:defrost", "ding")]),
    dict(text="And a fan blows the cold air around, so the top shelf is as cold as the bottom.",
         cam=CAB, pegs="happy",
         do=[("fan", "w:fan", 1, 0.4, "back"), ("air", "w:blows", 1, 0.5, "out")],
         keys=[("fan", BLUE), ("top shelf", INK), ("as cold as the bottom", BLUE)],
         fix="w:fan", sfx=[("w:fan", "pop")]),
    dict(text="A fridge never makes cold. It pumps heat out of the box and dumps it out the back. That's why the back "
              "of your fridge is warm.",
         cam=BACKC, pegs="shocked",
         do=[("air", 0.0, 0, 0.4, "in"), ("flow", 0.0, 1, 0.1, "lin"), ("toevap", 0.0, 1, 0.4, "out"),
             ("heatout", "w:dumps", 1, 0.5, "out"), ("cam_yaw", 0.0, 72.0, 1.8, "smooth"),
             ("cam_pitch", 0.0, 20.0, 1.8, "smooth")],
         keys=[("never makes cold", RED), ("pumps heat out", INK), ("back of your fridge|warm back!", BLUE)],
         pops=[dict(kind="stamp", at="w:warm", text="HEAT OUT", color=ORANGE, pos="tr", until="end+0.2")],
         sfx=[("w:dumps", "whoosh")]),
    dict(text="So next time you feel warm air near your fridge, you'll know that's the heat from your food, thrown out "
              "into the kitchen.",
         cam=WIDE, pegs="happy",
         cams=[("w:heat", BACKC, 1.4)],
         do=[("cam_yaw", 0.0, 45.0, 1.6, "smooth"), ("cam_pitch", 0.0, ISO_P, 1.6, "smooth")],
         keys=[("warm air", INK), ("heat from your food", BLUE)]),
    dict(text="And congratulations, you just built a fridge. Follow for more.", cam=WIDE, pegs="happy", pose="cheer",
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(room=0, cab=0, food=0, heatin=0, temp=0.15, evap=0, boil=0, toevap=0, gas=0, comp=0, suction=0, compon=0,
               cond=0, heatout=0, capi=0, flow=0, frozen=0, thermo=0, cycle=0, door=0, spill=0, mag=0, frost=0,
               heater=0, drip=0, fan=0, air=0)

# Scene QA - ORIGINAL step indices (VIDEO uses shift_spec(QA, 1) after open_loop inserts the hook)
QA = dict(
    links=[dict(name="refrigerant loop compressor->evaporator", steps="6-17", width_min=0.02, tol=0.08, settle=2.0,
                ends=[dict(color=COMP), dict(color=EVAPBOX)])],
)

STEPS = open_loop(
    STEPS, "Your fridge doesn't make cold at all. It does something much stranger.", answer_step=15,
    teaser_frac=0.7, reminder=(6, "Still not the strangest part. Hold that thought."), reveal="Here's the answer.",
    hook_hl=["doesn't", "stranger"], hook_cam=BACKC,
    hook_bursts=[dict(at="w:cold", glyph="cross", color=(226, 52, 64), xy=(0.78, 0.30))],
    ending_text="Now you know more about fridges than 99% of people. Follow for more. Because remember,",
    ending_hl=["99%"], ending_bursts=[dict(at="w:99", glyph="99%", color=(40, 160, 90), xy=(0.78, 0.30))],
    ending_cam=BACKC, ending_do=[])


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _wave(cam, a, b, color, width, t, phase=0.0):
    """Wavy heat/cold arrow from a to b (3D)."""
    n = 14
    pts = []
    for i in range(n + 1):
        f = i / n
        x, y, z = (a[k] + (b[k] - a[k]) * f for k in range(3))
        pts.append((x, y, z + 0.035 * math.sin(f * 12 - t * 8 + phase)))
    cam.line(pts, color, width, caps=False)
    tip, prev = pts[-1], pts[-3]
    kit.glow_dot(cam, tip, width * 1.4, color)


class FridgeScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (220, 232, 246), (248, 244, 236), clouds=4)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        self._step = step_i
        if g("room") > 0.01:
            self._room(cam, tr, t)
            self._peg(cam, tr, t)
        if g("cab") > 0.01:
            self._door(cam, tr, t)
            self._cabinet(cam, tr, t)
            self._inside(cam, tr, t)
            self._section(cam, tr, t)
            self._machine(cam, tr, t)
        elif g("food") > 0.01:
            self._food(cam, tr, t)
        self._heat(cam, tr, t)

    # ------------------------------------------------------------- kitchen (cut at y = 0)
    def _room(self, cam, tr, t):
        k = _sm(tr.get("room", t))
        h = 2.8 * k
        cam.box(-0.9, -1.7, -0.3, 3.4, 1.7, 0.3, (186, 176, 164), top_color=(232, 222, 206))
        for i in range(1, 9):
            x = -0.9 + i * 0.4
            cam.line([(x, -1.7, 0.002), (x, 0.0, 0.002)], (218, 208, 192), 0.006, caps=False)
        cam.poly([(-0.9, -1.7, 0), (-0.9, 0.0, 0), (-0.9, 0.0, h), (-0.9, -1.7, h)], (238, 230, 218), (200, 190, 176), 0.01)
        cam.poly([(-0.9, -1.7, 0), (2.5, -1.7, 0), (2.5, -1.7, h), (-0.9, -1.7, h)], (246, 240, 230), (200, 190, 176), 0.01)
        sh = ShadowLayer(cam)
        sh.ao_edge((-0.9, -1.7, 0), (2.5, -1.7, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
        sh.ao_edge((-0.9, -1.7, 0), (-0.9, 0.0, 0), (1, 0, 0), (0, 0, 1), 0.3, 140)
        sh.box_on_plane(X0, YB, 0, X1 - X0, -YB, Z1, "z", 0.0, 160)
        sh.apply(cam.img, 0.26, 2.2)
        if k > 0.9 and self._step == 0:
            kit.label(cam, (1.8, -0.4, 0.05), "KITCHEN", 0.14, INK, (255, 255, 255))

    def _peg(self, cam, tr, t):
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (-0.45, -0.75, 0.0), PEG_COLORS[2], expr, t, 1.7, (0.8, 0.2), seed=5, pose=tr.peg_pose(t), react=react)

    # ------------------------------------------------------------- cabinet, door, insulation section
    def _door(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        a = _sm(g("door")) * 1.35
        hx, hy = X0 - 0.05, 0.0                         # hinge on the cut edge: the door swings out, face to camera
        ex, ey = hx - 0.72 * math.sin(a), hy - 0.72 * math.cos(a)
        kz = Z0 + (Z1 - Z0) * _sm(g("cab"))
        cam.poly([(hx, hy, Z0 + 0.02), (ex, ey, Z0 + 0.02), (ex, ey, kz), (hx, hy, kz)], (232, 236, 242), (170, 176, 188), 0.01)
        cam.poly([(hx, hy, kz), (ex, ey, kz), (ex + 0.05, ey, kz), (hx + 0.05, hy, kz)], SHELL)
        hxm, hym = hx + (ex - hx) * 0.8, hy + (ey - hy) * 0.8
        cam.line([(hxm, hym + 0.03, 1.0), (hxm, hym + 0.03, 1.5)], (160, 166, 178), 0.03)     # handle
        m = g("mag")
        if m > 0.01 or self._step in (10, 11):          # gasket with magnets along the door edge
            col = mix((60, 64, 72), RED, m)
            cam.line([(ex + 0.02, ey, Z0 + 0.06), (ex + 0.02, ey, kz - 0.04)], col, 0.035 * (1 + m))
            if m > 0.5 and self._step == 11:
                kit.label(cam, (ex + 0.05, ey + 0.1, 1.5), "MAGNETS", 0.11, (255, 255, 255), RED)

    def _cabinet(self, cam, tr, t):
        k = _sm(tr.get("cab", t))
        z1 = Z0 + (Z1 - Z0) * k
        cam.box(X0, YB, Z0, X1 - X0, -YB - 0.002, z1 - Z0, SHELL, faces="tr")
        if k < 0.95:
            return
        # inside of the back half: inner back wall, floor, inner front wall
        cam.poly([(CX0, YB + 0.08, CZ0), (CX1, YB + 0.08, CZ0), (CX1, YB + 0.08, CZ1), (CX0, YB + 0.08, CZ1)], INNER)
        cam.poly([(CX0, YB + 0.08, CZ0), (CX1, YB + 0.08, CZ0), (CX1, 0.0, CZ0), (CX0, 0.0, CZ0)], shade(INNER, 0.06))
        cam.poly([(CX0, YB + 0.08, CZ0), (CX0, 0.0, CZ0), (CX0, 0.0, CZ1), (CX0, YB + 0.08, CZ1)], shade(INNER, -0.06))
        # machine compartment under the back of the food compartment
        cam.poly([(0.62, YB + 0.05, Z0 + 0.02), (X1, YB + 0.05, Z0 + 0.02), (X1, YB + 0.05, 0.5), (0.62, YB + 0.05, 0.5)],
                 (120, 126, 140))

    def _food(self, cam, tr, t):
        k = _sm(tr.get("food", t))
        fr = tr.get("frozen", t)
        tint = lambda c: mix(c, (200, 230, 255), 0.6 * fr)
        cam.box(0.38, -0.5, CZ0, 0.16 * k, 0.16, 0.34 * k, tint((250, 250, 252)))       # milk
        cam.box(0.38, -0.5, CZ0 + 0.34 * k, 0.16 * k, 0.16, 0.06 * k, tint((70, 130, 220)))
        cam.box(0.62, -0.45, 1.18, 0.22 * k, 0.2, 0.12 * k, tint((120, 190, 90)))       # lettuce box
        px, py = cam.p(0.72, -0.25, CZ0 + 0.09)
        r = 0.09 * cam.s * k
        cam.d.ellipse((px - r, py - r, px + r, py + r), fill=tint((220, 60, 60)), outline=(150, 30, 30))   # apple
        if fr > 0.5 and self._step == 8:
            kit.label(cam, (0.73, -0.35, 1.5), "FROZEN", 0.1, (255, 255, 255), BLUE)

    def _inside(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        # shelf
        cam.box(CX0, YB + 0.08, 1.15, CX1 - CX0, -YB - 0.1, 0.03, (230, 240, 248))
        self._food(cam, tr, t)
        # evaporator coil on the inner back wall (+ frost, heater, header box)
        e = g("evap")
        if e > 0.01:
            pts = kit.sub_path(EVAP, 0, _sm(e)) if e < 0.99 else EVAP
            cam.box(0.44, -0.68, 1.62, 0.06, 0.06, 0.26, EVAPBOX)
            col = mix(COLD, (240, 250, 255), g("frost") * 0.8)
            cam.line(pts, shade(col, -0.3), 0.05)
            cam.line(pts, col, 0.036)
            fr = g("frost")
            if fr > 0.02:
                for i, p in enumerate(EVAP):
                    px, py = cam.p(*p)
                    r = (0.025 + 0.02 * (i % 3)) * fr * cam.s
                    cam.d.ellipse((px - r, py - r, px + r, py + r), fill=(250, 252, 255), outline=(200, 220, 240))
            if g("heater") > 0.05:
                cam.line([(0.5, -0.65, 1.58), (0.86, -0.65, 1.58)], mix((200, 80, 60), (255, 200, 80), 0.5 + 0.5 * math.sin(t * 9)), 0.03)
                if self._step == 13:
                    kit.label(cam, (0.68, -0.5, 1.45), "DEFROST HEATER", 0.1, (255, 255, 255), ORANGE)
            if g("drip") > 0.2:
                for j in range(3):
                    f = (t * 1.5 + j / 3) % 1.0
                    kit.glow_dot(cam, (0.6 + 0.1 * j, -0.62, 1.56 - 0.9 * f), 0.025, COLD)
            if g("boil") > 0.1:                         # bubbles in the coil = the liquid boiling
                for j in range(6):
                    s = (t * 0.6 + j / 6) % 1.0
                    p = kit.path_point(EVAP, s)[0]
                    px, py = cam.p(*p)
                    r = 0.02 * cam.s
                    cam.d.ellipse((px - r, py - r, px + r, py + r), outline=(255, 255, 255), width=max(2, int(0.006 * cam.s)))
            if self._step == 2 and e > 0.9:
                kit.label(cam, (0.68, -0.5, 1.98), "EVAPORATOR", 0.11, (255, 255, 255), BLUE)
        f = g("fan")
        if f > 0.01:
            parts.fan(cam, (0.38, -0.64, 1.7), 0.1 * _sm(f), "y", t * 14, (90, 96, 110))
            if g("air") > 0.1:
                loop = [(0.38, -0.3, 1.7), (0.85, -0.25, 1.75), (0.85, -0.2, 0.7), (0.4, -0.2, 0.65), (0.38, -0.3, 1.6)]
                for j in range(4):
                    kit.packet(cam, loop, (t * 0.35 + j / 4) % 1.0, (170, 215, 255), 0.04)
        th = g("thermo")
        if th > 0.01:
            cam.box(0.32, -0.3, 1.78, 0.08, 0.16 * _sm(th), 0.1, (60, 64, 76))
            on = g("cycle") > 0.5 and (t % 2.4) < 1.2
            parts.led(cam, (0.41, -0.22, 1.84), (90, 230, 140) if on or g("cycle") < 0.5 else (200, 70, 70), True, 0.022)
            if self._step == 9:
                kit.label(cam, (0.36, -0.22, 2.05), "THERMOSTAT", 0.1, (255, 255, 255), GREEN)
        sp = g("spill")
        if sp > 0.02:                                   # cold air pouring out of the open door, down to the floor
            for j in range(4):
                f = (t * 0.5 + j / 4) % 1.0
                _wave(cam, (CX0 + 0.05, -0.2 - 0.1 * j, 1.2 - 0.15 * j), (-0.3 - 0.2 * j, -0.1 - 0.1 * j, 0.05),
                      mix(COLD, (255, 255, 255), f), 0.025 * sp, t, j)

    def _section(self, cam, tr, t):
        """Cut face of the walls at y = 0 (insulation foam ring around the compartments)."""
        y = 0.0
        foam = [((X0, Z1 - 0.1), (X1, Z1)), ((X0, CZ0 - 0.06), (X1, CZ0)), ((X0, Z0), (CX0, Z1)), ((CX1, CZ0), (X1, Z1)),
                ((X0, Z0), (0.62, CZ0))]
        for (a0, b0), (a1, b1) in foam:
            cam.poly([(a0, y, b0), (a1, y, b0), (a1, y, b1), (a0, y, b1)], FOAM, shade(FOAM, -0.3), 0.006)
        cam.poly([(X0, y, Z0), (X1, y, Z0), (X1, y, Z1), (X0, y, Z1)], None, shade(SHELL, -0.4), 0.012)
        if self._step == 0 and tr.get("room", t) > 0.5:
            kit.label(cam, (X0 + 0.04, 0.05, 1.3), "THICK WALLS", 0.1, INK, FOAM)

    # ------------------------------------------------------------- compressor, pipes, condenser, refrigerant
    def _machine(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        c = g("comp")
        if c > 0.01:
            k = _sm(c)
            cam.box(0.7, -0.5, Z0 + 0.03, 0.26, 0.36, 0.3 * k, COMP)
            run = g("compon") > 0.5 and (g("cycle") < 0.5 or (t % 2.4) < 1.2)
            if run:
                for j in range(3):                      # hum lines
                    f = (t * 2 + j / 3) % 1.0
                    cam.line([(1.0 + 0.05 * f, -0.2, 0.25 + 0.06 * j), (1.06 + 0.05 * f, -0.2, 0.25 + 0.06 * j)],
                             (150, 156, 170), 0.012, caps=False)
            if self._step in (4, 9) and k > 0.9:
                kit.label(cam, (0.85, -0.2, 0.62), "COMPRESSOR", 0.1, (255, 255, 255), INK)
        if g("suction") > 0.01:
            path = [(0.86, -0.66, 1.6)] + SUCTION[1:] + [(0.96, -0.4, 0.33)]
            kit.cable(cam, kit.sub_path(path, 0, _sm(g("suction"))) if g("suction") < 0.99 else path, (120, 160, 200), 0.028)
        cd = g("cond")
        if cd > 0.01:
            pts = kit.sub_path(COND, 0, _sm(cd)) if cd < 0.99 else COND
            hot = mix((150, 156, 170), HOT, 0.6)
            cam.line(pts, shade(hot, -0.3), 0.042)
            cam.line(pts, hot, 0.03)
            if self._step in (5, 15) and cd > 0.9:
                kit.label(cam, (1.12, -0.35, 2.0), "CONDENSER", 0.11, (255, 255, 255), ORANGE)
        if g("capi") > 0.01:
            kit.cable(cam, kit.sub_path(CAPI, 0, _sm(g("capi"))) if g("capi") < 0.99 else CAPI, (110, 140, 190), 0.02)
            if self._step == 6:
                kit.label(cam, (1.0, -0.6, 2.05), "TINY TUBE", 0.1, (255, 255, 255), BLUE)
        fl = g("flow") + (g("gas") if self._step == 3 else 0)
        if fl > 0.05 and g("capi") > 0.9:
            loop = EVAP + SUCTION[1:] + COND[1:] + CAPI[1:]
            for j in range(10):
                s = (t * 0.12 + j / 10) % 1.0
                p, _ = kit.path_point(loop, s)
                hotness = 0.0 if s < 0.3 else (1.0 if s < 0.75 else max(0.0, 1.0 - (s - 0.75) * 6))
                kit.glow_dot(cam, p, 0.04, mix(COLD, HOT, hotness))

    def _heat(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        hi = g("heatin")
        if hi > 0.02:                                   # kitchen heat creeping in through the walls
            for j in range(4):
                _wave(cam, (X1 + 0.5, -0.3, 0.8 + 0.25 * j), (0.7, -0.35, 0.8 + 0.25 * j), mix(ORANGE, RED, 0.3), 0.025 * hi, t, j)
        te = g("toevap")
        if te > 0.02:                                   # heat from the food into the cold coil
            for j, start in enumerate(((0.46, -0.45, 0.98), (0.72, -0.35, 1.35), (0.72, -0.25, 0.7))):
                _wave(cam, start, (0.6 + 0.08 * j, -0.62, 1.66), ORANGE, 0.022 * te, t, j)
        ho = g("heatout")
        if ho > 0.02:                                   # heat thrown out of the condenser into the room
            for j in range(4):
                z = 0.7 + 0.3 * j
                _wave(cam, (1.1, -0.3, z), (1.7, -0.1, z + 0.25), mix(ORANGE, RED, 0.4), 0.03 * ho, t, j)


VIDEO = dict(
    slug="fridge",
    title="How does a fridge make cold out of electricity?",
    steps=STEPS, end_cover=False, scene=FridgeScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"),
    qa=shift_spec(QA, 1),
)
