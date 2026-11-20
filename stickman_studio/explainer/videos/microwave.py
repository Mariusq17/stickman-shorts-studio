"""Why does a fork spark in the microwave? - a microwave oven built step by step."""
from __future__ import annotations

import math

from PIL import ImageDraw

from ...painter import font
from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

WIDE = ((1.3, 0.6, 1.6), 190)
INSIDE = ((0.85, 0.35, 1.5), 420)
MAG = ((2.0, 0.3, 1.8), 330)

STEPS = [
    dict(text="If you put a radio transmitter that's way too powerful inside a metal box, you've got the world's "
              "simplest microwave oven.",
         cam=((2.0, 0.3, 1.7), 460), pegs="neutral",
         cams=[("w:metal", ((1.2, 0.3, 1.65), 300), 1.0), ("w:simplest", WIDE, 1.4)],
         do=[("mag", 0.0, 1, 0.7, "back"), ("glow", "w:powerful", 1, 0.4, "out"), ("box", "w:metal", 1, 1.0, "out"),
             ("kitchen", "w:simplest", 1, 1.3, "out"), ("xray", "w:simplest", 0, 1.0, "io")],
         keys=[("radio transmitter", INK), ("way too powerful", RED), ("metal box|inside a metal box", INK),
               ("simplest microwave oven", BLUE)],
         sfx=[("w:radio", "pop"), ("w:metal", "thud"), ("w:simplest", "whoosh")]),
    dict(text="That transmitter is called a magnetron. It pumps out microwaves, invisible waves that flip back and "
              "forth about two and a half billion times a second.",
         cam=MAG, pegs="neutral",
         do=[("xray", 0.1, 1, 0.6, "io"), ("waves", "w:pumps", 1, 0.6, "out")],
         keys=[("magnetron", INK), ("microwaves|invisible microwaves", INK), ("two and a half billion|2.45 billion / s", INK)],
         fix="w:magnetron",
         pops=[dict(kind="note", at="w:two", text="2,450,000,000 flips / s", pos="bc", until="end+0.2")],
         sfx=[("w:pumps", "whoosh")]),
    dict(text="Water molecules have a plus end and a minus end. Every flip, they twist around to line up, and all that "
              "jiggling turns into heat.",
         cam=INSIDE, pegs="happy", pose="think",
         do=[("food", 0.1, 1, 0.5, "back"), ("bubble", "w:water", 1, 0.4, "back"), ("heat", "w:heat", 1, 1.0, "out")],
         keys=[("plus end and a minus end|+ end and - end", INK), ("twist around", INK), ("jiggling|jiggling = heat", BLUE)],
         sfx=[("w:heat", "ding")]),
    dict(text="To get the waves from the magnetron to the food, a metal channel pipes them into the box. That's the "
              "waveguide.",
         cam=((1.6, 0.3, 2.0), 280), pegs="neutral",
         do=[("bubble", 0.1, 0, 0.3, "in"), ("guide", "w:channel", 1, 0.8, "out")],
         keys=[("metal channel", INK), ("waveguide", INK)],
         fix="w:waveguide",
         pops=[dict(kind="arrow", at="w:waveguide", xyz=(1.75, 0.3, 2.15), text="waveguide", color=BLUE,
                    off=(0.12, -0.12), until="end+0.3", sound=False)]),
    dict(text="The metal walls bounce the waves around so none escape. But bouncing waves pile up into hot spots and "
              "cold spots, so half your soup boils and half stays frozen.",
         cam=INSIDE, pegs="worried",
         do=[("xray", 0.1, 0, 0.6, "io"), ("bounce", "w:bounce", 1, 0.6, "out"), ("spots", "w:hot", 1, 0.6, "out")],
         keys=[("metal walls", INK), ("hot spots|hot spots + cold spots", RED), ("stays frozen", RED)],
         fix="w:walls",
         pops=[dict(kind="bars", at="w:half", title="SOUP", until="end+0.3", pos="bc",
                    items=[("boiling", 1.0, RED), ("frozen", 0.9, BLUE)])],
         sfx=[("w:frozen", "sting")]),
    dict(text="So the food sits on a turntable that keeps carrying every bit through the hot spots. Some ovens spin a "
              "little metal fan in the ceiling instead.",
         cam=INSIDE, pegs="happy",
         do=[("turn", "w:turntable", 1, 0.5, "out"), ("even", "w:carrying", 1, 2.5, "io")],
         keys=[("turntable", INK), ("through the hot spots", INK), ("metal fan|stirrer fan", INK)],
         fix="w:turntable",
         sfx=[("w:turntable", "click")]),
    dict(text="Next problem. You want to watch your popcorn, but a plain window would leak microwaves straight into "
              "your face.",
         cam=((1.0, 1.6, 1.4), 200), pegs="shocked",
         do=[("leak", "w:leak", 1, 0.5, "out")],
         keys=[("watch your popcorn", INK), ("leak microwaves|leaking waves", RED)],
         pops=[dict(kind="warn", at="w:leak", text="waves leaking!", pos="bc", until="end+0.3")],
         sfx=[("w:leak", "sting")]),
    dict(text="So the door glass has a metal mesh with holes much smaller than the waves. Microwaves are about twelve "
              "centimeters long and can't squeeze through. Light is way tinier, so it walks right out.",
         cam=((1.0, 1.0, 1.65), 330), pegs="happy",
         do=[("leak", 0.2, 0, 0.4, "in"), ("mesh", "w:mesh", 1, 0.8, "out")],
         keys=[("metal mesh", INK), ("twelve centimeters|wave = 12 cm", INK), ("can't squeeze through", BLUE),
               ("light is way tinier|light gets out", BLUE)],
         fix="w:mesh",
         pops=[dict(kind="bars", at="w:twelve", title="SIZE", until="end+0.3", pos="bc",
                    items=[("microwave", 1.0, RED), ("mesh hole", 0.1, INK), ("light", 0.01, ORANGE)])],
         sfx=[("w:mesh", "click")]),
    dict(text="And if someone opens the door while it's running, switches in the latch cut the magnetron instantly. "
              "That's the door interlock.",
         cam=((1.4, 0.8, 1.6), 230), pegs="shocked",
         do=[("door", "w:opens", 1, 0.6, "out"), ("glow", "w:cut", 0, 0.1, "lin"), ("waves", "w:cut", 0, 0.1, "lin"),
             ("door", "end-0.6", 0, 0.5, "io")],
         keys=[("opens the door", RED), ("cut the magnetron|magnetron OFF", BLUE), ("door interlock", INK)],
         fix="w:interlock",
         sfx=[("w:cut", "click")]),
    dict(text="Want half power? Many microwaves can't turn the magnetron down, so they just switch it on and off in "
              "cycles.",
         cam=MAG, pegs="neutral",
         do=[("xray", 0.1, 1, 0.5, "io"), ("cycle", "w:switch", 1, 0.2, "lin"), ("waves", 0.2, 1, 0.2, "lin")],
         keys=[("half power", INK), ("on and off|on - off - on - off", INK)],
         fix="w:cycles",
         pops=[dict(kind="graph", at="w:switch", title="MAGNETRON", track="glow", window=4.0, color=ORANGE, pos="bc",
                    until="end+0.3")]),
    dict(text="Now, the fork. Microwaves push electrons around in metal, and on a sharp point they crowd together so "
              "tightly that they jump through the air. That's arcing.",
         cam=INSIDE, pegs="shocked",
         do=[("cycle", 0.1, 0, 0, "lin"), ("glow", 0.1, 1, 0.2, "lin"), ("xray", 0.1, 0, 0.5, "io"),
             ("fork", "w:fork", 1, 0.4, "back"), ("arc", "w:jump", 1, 0.2, "out")],
         keys=[("the fork", INK), ("sharp point", RED), ("jump through the air", RED), ("arcing", INK)],
         pops=[dict(kind="arrow", at="w:sharp", xyz=(0.9, 0.75, 1.2), text="sharp tips", color=RED, off=(-0.15, -0.14),
                    dur=2.4)],
         sfx=[("w:jump", "slap"), ("w:arcing", "sting")]),
    dict(text="That's why some ovens even come with a metal rack. It's smooth, rounded, and kept away from the walls.",
         cam=INSIDE, pegs="happy",
         do=[("fork", 0.3, 0, 0.3, "in"), ("arc", 0.2, 0, 0.1, "in"), ("rack", "w:rack", 1, 0.5, "back")],
         keys=[("metal rack", INK), ("smooth, rounded|smooth + rounded = OK", BLUE)],
         pops=[dict(kind="check", at="w:smooth", text="no sharp points", pos="bc", until="end+0.3")]),
    dict(text="And no, it doesn't cook from the inside out. The waves only reach a couple of centimeters in, and the "
              "middle warms up as the heat spreads inward.",
         cam=((0.9, 0.4, 1.45), 380), pegs="neutral",
         do=[("rack", 0.2, 0, 0.3, "in"), ("cut", "w:inside", 1, 0.6, "out"), ("depth", "w:couple", 1, 2.5, "io")],
         keys=[("inside out|inside out? no", RED), ("couple of centimeters|only 1-3 cm deep", INK), ("spreads inward", BLUE)]),
    dict(text="So next time your fork lights up like a tiny thunderstorm, you'll know the microwaves just found a sharp "
              "point.",
         cam=INSIDE, pegs="happy",
         do=[("cut", 0.2, 0, 0.4, "in"), ("depth", 0.2, 0, 0.2, "in"), ("fork", 0.2, 1, 0.3, "back"), ("arc", "w:lights", 1, 0.2, "out")],
         keys=[("tiny thunderstorm", INK), ("sharp point|found a sharp point", BLUE)],
         sfx=[("w:lights", "slap")]),
    dict(text="And congratulations, you just built a microwave oven. Now you just need to stop putting forks in it. "
              "Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("fork", 0.2, 0, 0.3, "in"), ("arc", 0.1, 0, 0.1, "in"), ("done", "w:built", 1, 0.3, "out")],
         keys=[("built a microwave oven|you built a microwave!", BLUE), ("forks in it", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:built", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(mag=0, glow=0, box=0, kitchen=0, xray=1, waves=0, food=0, bubble=0, heat=0, guide=0, bounce=0, spots=0,
               turn=0, even=0, leak=0, mesh=0, door=0, cycle=0, fork=0, arc=0, rack=0, cut=0, depth=0, done=0)

# microwave body: x 0..2.4, y -0.4..1.0 (front face y = 1.0), z ZB..ZB+1.3 (sits on the counter)
ZB = 1.0
MX0, MX1, MY0, MY1, MH = 0.0, 2.4, -0.4, 1.0, 1.3
CH = (0.1, 1.7, -0.3, 0.95, ZB + 0.08, ZB + 1.2)      # cooking chamber x0,x1,y0,y1,z0,z1
TT = (0.9, 0.32, ZB + 0.14)                             # turntable centre
BODY = (236, 238, 244)
STEEL = (196, 202, 214)
COUNTER = (200, 160, 120)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class MicrowaveScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (238, 232, 222), (252, 246, 236), clouds=0)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        if g("kitchen") > 0.01:
            self._kitchen(cam, tr, t)
        box = g("box")
        if box > 0.01:
            self._chamber(cam, tr, t, box)
        self._magnetron(cam, tr, t)
        if box > 0.01:
            self._front(cam, tr, t, box)
        if g("kitchen") > 0.5:
            self._pegs(cam, tr, t)

    # ------------------------------------------------------------- kitchen
    def _kitchen(self, cam, tr, t):
        k = _sm(tr.get("kitchen", t))
        cam.poly([(-3, -1.2, 0), (5, -1.2, 0), (5, 4.5, 0), (-3, 4.5, 0)], (226, 214, 196))
        h = 3.4 * k
        cam.poly([(-3, -1.2, 0), (5, -1.2, 0), (5, -1.2, h), (-3, -1.2, h)], (244, 236, 222), (200, 190, 176), 0.01)
        cam.poly([(-3, -1.2, 0), (-3, 4.5, 0), (-3, 4.5, h), (-3, -1.2, h)], (232, 222, 206), (200, 190, 176), 0.01)
        for i in range(1, 9):     # wall tiles behind the counter
            z = ZB + i * 0.22
            if z < h:
                cam.line([(-3, -1.199, z), (5, -1.199, z)], (226, 216, 200), 0.008, caps=False)
        sh = ShadowLayer(cam)
        sh.ao_edge((-3, -1.2, 0), (5, -1.2, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
        sh.box_on_plane(MX0, MY0, ZB, MX1 - MX0, MY1 - MY0, MH, "y", -1.2, 160, ((-3, 5), (-1.2, -1.2), (ZB, 4)))
        sh.box_on_plane(-2.4, -1.2, 0, 7.0, 2.3, ZB, "z", 0.0, 200)
        sh.apply(cam.img, 0.28, 2.4)
        # counter + cabinets
        cam.box(-2.4, -1.2, 0, 7.0, 2.3, ZB, (240, 240, 244), top_color=(200, 196, 186))
        for i in range(5):
            x0 = -2.3 + i * 1.4
            kit.plate(cam, "y", 1.101, x0 + 0.05, 0.1, x0 + 1.3, 0.85, (232, 232, 238), (190, 190, 200))
            cam.line([(x0 + 0.55, 1.105, 0.75), (x0 + 0.8, 1.105, 0.75)], (120, 124, 136), 0.025)
        # kettle + jar for context
        cam.box(3.3, -0.6, ZB, 0.4, 0.4, 0.5, (220, 80, 70))
        cam.box(3.9, -0.4, ZB, 0.3, 0.3, 0.45, (120, 180, 220))

    # ------------------------------------------------------------- inside
    def _chamber(self, cam, tr, t, box):
        g = lambda k: tr.get(k, t)
        x0, x1, y0, y1, z0, z1 = CH
        k = _sm(box)
        if k < 0.5:
            return
        heat = g("heat")
        wall = mix((210, 214, 222), (255, 236, 200), 0.3 * g("waves"))
        cam.poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], shade(wall, -0.1))
        cam.poly([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], shade(wall, -0.2))
        cam.poly([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], shade(wall, -0.05))
        light = g("waves") > 0.5 or heat > 0.5
        if light:
            cam.poly([(x0, y0, z1 - 0.01), (x1, y0, z1 - 0.01), (x1, y1, z1 - 0.01), (x0, y1, z1 - 0.01)],
                     (255, 244, 200))
        # waveguide outlet (top right of the chamber)
        if g("guide") > 0.5 or g("mag") > 0.5:
            cam.poly([(x1 - 0.01, 0.1, z1 - 0.35), (x1 - 0.01, 0.55, z1 - 0.35), (x1 - 0.01, 0.55, z1 - 0.05),
                      (x1 - 0.01, 0.1, z1 - 0.05)], (150, 156, 170))
        # turntable + food
        spin = t * 1.2 * g("turn")
        if g("turn") > 0.01:
            cam.poly(cam.disc_pts(TT, 0.62, "z", 32), (226, 240, 246), (150, 180, 190), 0.008)
        fk = g("food")
        if fk > 0.01:
            self._food(cam, tr, t, fk, spin)
        if g("rack") > 0.01:
            r = _sm(g("rack"))
            for i in range(6):
                xx = 0.35 + i * 0.22
                cam.line([(xx, -0.15, z0 + 0.45 * r), (xx, 0.8, z0 + 0.45 * r)], (180, 186, 198), 0.02)
            cam.line([(0.3, -0.15, z0 + 0.45 * r), (1.5, -0.15, z0 + 0.45 * r), (1.5, 0.8, z0 + 0.45 * r),
                      (0.3, 0.8, z0 + 0.45 * r), (0.3, -0.15, z0 + 0.45 * r)], (160, 166, 178), 0.03)
        fo = g("fork")
        if fo > 0.01:
            self._fork(cam, tr, t, fo, spin)
        # waves bouncing inside
        wv = g("waves") * (1.0 if g("glow") > 0.5 else 0.0)
        if wv > 0.01:
            for j in range(3):
                pts = []
                bx = g("bounce")
                for i in range(40):
                    f = i / 39
                    x = x1 - 0.05 - f * (x1 - x0 - 0.1)
                    zz = z1 - 0.2 - j * 0.28 + 0.07 * math.sin(f * 30 - t * 18 + j)
                    if bx > 0.5:
                        zz = z0 + 0.1 + (z1 - z0 - 0.2) * abs(((f * 2.5 + j * 0.3 + t * 0.6) % 2) - 1) \
                            + 0.05 * math.sin(f * 30 - t * 18)
                    pts.append((x, 0.25 + j * 0.18, zz))
                cam.line(pts, mix((255, 200, 120), (255, 120, 60), j / 2), 0.012 * wv, caps=False)

    def _food(self, cam, tr, t, fk, spin):
        g = lambda k: tr.get(k, t)
        k = _sm(fk)
        cx, cy, cz = TT
        cam.poly(cam.disc_pts((cx, cy, cz + 0.02), 0.45 * k, "z", 28), (250, 250, 250), (190, 190, 200), 0.008)
        # bowl
        cam.poly(cam.disc_pts((cx, cy, cz + 0.05), 0.3 * k, "z", 28), (90, 140, 210))
        cam.poly(cam.disc_pts((cx, cy, cz + 0.22), 0.36 * k, "z", 28), (110, 160, 230), (60, 100, 170), 0.008)
        soup = mix((240, 170, 80), (255, 120, 60), g("heat"))
        cam.poly(cam.disc_pts((cx, cy, cz + 0.2), 0.31 * k, "z", 28), soup)
        sp = g("spots")
        if sp > 0.01:
            ev = g("even")
            for i in range(6):
                a = i * 1.047 + spin
                rr = 0.17
                px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
                hot = i % 2 == 0
                col = mix(RED if hot else (90, 170, 255), soup, ev * 0.85)
                cam.poly(cam.disc_pts((px, py, cz + 0.205), 0.08 * sp, "z", 14), col)
            if ev > 0.6:
                for i in range(3):       # steam
                    f = (t * 0.6 + i / 3) % 1.0
                    x, y = cam.p(cx - 0.1 + i * 0.1, cy, cz + 0.3 + f * 0.5)
                    r = (0.03 + 0.05 * f) * cam.s
                    cam.d.ellipse((x - r, y - r, x + r, y + r), fill=mix((255, 255, 255), (230, 230, 236), f))
        cu = g("cut")
        if cu > 0.01:
            # cut-away slice showing the heating depth
            d = g("depth")
            kit.label(cam, (cx, cy + 0.36, cz + 0.55), "HOT OUTSIDE  ->  WARM MIDDLE" if d > 0.5 else "WAVES: 1-3 cm",
                      0.07, (255, 255, 255), ORANGE)
            ring = 0.31 * (1 - 0.6 * d)
            cam.poly(cam.disc_pts((cx, cy, cz + 0.21), 0.31, "z", 28), None, RED, 0.03 * cu)
            cam.poly(cam.disc_pts((cx, cy, cz + 0.21), max(0.05, ring), "z", 28), None, (255, 170, 60), 0.02 * cu)
        if g("heat") > 0.3 and g("spots") < 0.01:
            for i in range(2):
                f = (t * 0.7 + i / 2) % 1.0
                x, y = cam.p(cx + 0.05 * i, cy, cz + 0.3 + f * 0.4)
                r = (0.03 + 0.04 * f) * cam.s
                cam.d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 250, 252))

    def _fork(self, cam, tr, t, fo, spin):
        g = lambda k: tr.get(k, t)
        cx, cy, cz = TT
        k = _sm(fo)
        a = spin + 1.2                                  # rides on the plate next to the bowl
        px, py = cx + math.cos(a) * 0.4, cy + math.sin(a) * 0.4
        z = cz + 0.05 + (1 - k) * 0.6
        ta = a + math.pi / 2                            # lies tangent to the plate rim
        ca, sa = math.cos(ta), math.sin(ta)
        base = (px + ca * 0.08, py + sa * 0.08, z)
        handle = (px - ca * 0.4, py - sa * 0.4, z + 0.02)
        cam.line([handle, base], (90, 96, 110), 0.06)
        cam.line([handle, base], (214, 220, 232), 0.042)
        tips = []
        for j in (-1.5, -0.5, 0.5, 1.5):
            ox, oy = -sa * j * 0.04, ca * j * 0.04
            tip = (base[0] + ca * 0.24 + ox, base[1] + sa * 0.24 + oy, z)
            cam.line([(base[0] + ox, base[1] + oy, z), tip], (90, 96, 110), 0.03)
            cam.line([(base[0] + ox, base[1] + oy, z), tip], (220, 226, 238), 0.018)
            tips.append(tip)
        ar = g("arc")
        if ar > 0.3 and (t * 24) % 3 < 2:
            for k2, tip in enumerate(tips):
                pts = [tip]
                p = tip
                for s_ in range(4):
                    seed = math.sin(t * 90 + k2 * 7 + s_ * 3)
                    p = (p[0] + 0.06 * ca + 0.04 * seed, p[1] + 0.06 * sa + 0.04 * math.cos(t * 70 + s_),
                         p[2] + 0.05 + 0.03 * seed)
                    pts.append(p)
                cam.line(pts, (60, 120, 255), 0.04)
                cam.line(pts, (235, 245, 255), 0.015)
                kit.glow_dot(cam, tip, 0.035, (120, 170, 255))

    # ------------------------------------------------------------- magnetron
    def _magnetron(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        m = g("mag")
        if m <= 0.01:
            return
        xr = g("xray")
        box = g("box")
        if box > 0.5 and xr < 0.05:
            return
        k = _sm(m)
        on = g("glow")
        if g("cycle") > 0.5:
            on = 1.0 if (t % 1.6) < 0.8 else 0.0
            tr_set = getattr(tr, "_glow_override", None)
        c = (1.95, 0.0, ZB + 0.45)
        cam.box(1.8, -0.2, ZB + 0.2, 0.42 * k, 0.6, 0.5 * k, mix((150, 156, 170), (255, 140, 60), 0.5 * on))
        for i in range(5):           # cooling fins
            z = ZB + 0.28 + i * 0.09
            cam.line([(1.78, -0.2, z), (1.78, 0.4, z)], (110, 116, 130), 0.012, caps=False)
            cam.box(1.79, 0.4, z - 0.01, 0.42 * k, 0.02, 0.02, (180, 186, 198))
        cam.box(1.95, 0.05, ZB + 0.7 * k, 0.12, 0.12, 0.18 * k, (230, 180, 60))     # antenna
        parts.led(cam, (2.1, 0.41, ZB + 0.6), (255, 120, 60) if on > 0.5 else (70, 74, 86), on > 0.5, 0.03)
        if g("guide") > 0.01 or box > 0.5:
            gk = _sm(g("guide")) if g("guide") > 0.01 else 1.0
            cam.box(1.7, 0.08, ZB + 0.85, 0.35 * gk, 0.5, 0.25, (176, 182, 196))
        if g("waves") > 0.01 and on > 0.5:
            for i in range(3):
                f = (t * 1.5 + i / 3) % 1.0
                pts = [(2.0 - f * 0.5 - j * 0.02, 0.33, ZB + 0.95 + 0.05 * math.sin(j * 1.2 - t * 20)) for j in range(10)]
                cam.line(pts, (255, 160, 60), 0.012, caps=False)
        if box < 0.5 or xr > 0.5:
            kit.label(cam, (2.0, 0.1, ZB + 1.25), "MAGNETRON", 0.1, (255, 255, 255), (200, 90, 40))

    # ------------------------------------------------------------- front
    def _front(self, cam, tr, t, box):
        g = lambda k: tr.get(k, t)
        k = _sm(box)
        h = MH * k
        xr = g("xray")
        # body shell: top + right side + front frame (the window shows the chamber)
        xr0 = g("xray")
        tx1 = MX1 if xr0 < 0.5 else 1.72          # x-ray: open the top + side over the magnetron bay
        cam.poly([(MX0, MY0, ZB + h), (tx1, MY0, ZB + h), (tx1, MY1, ZB + h), (MX0, MY1, ZB + h)], shade(BODY, 0.05),
                 shade(BODY, -0.35), 0.01)
        if xr0 < 0.5:
            cam.poly([(MX1, MY0, ZB), (MX1, MY1, ZB), (MX1, MY1, ZB + h), (MX1, MY0, ZB + h)], shade(BODY, -0.18),
                     shade(BODY, -0.35), 0.01)
        else:
            for a, b in (((MX1, MY0, ZB), (MX1, MY0, ZB + h)), ((MX1, MY1, ZB), (MX1, MY1, ZB + h)),
                         ((tx1, MY0, ZB + h), (MX1, MY0, ZB + h)), ((tx1, MY1, ZB + h), (MX1, MY1, ZB + h)),
                         ((MX1, MY0, ZB + h), (MX1, MY1, ZB + h))):
                cam.line([a, b], (150, 156, 170), 0.02, caps=False)
        if k < 0.9:
            return
        y = MY1
        door = g("door")
        # control panel (hidden in x-ray mode so the magnetron shows)
        if xr < 0.5:
            kit.plate(cam, "y", y, 1.72, ZB, MX1, ZB + MH, (60, 64, 76), (30, 32, 40))
            kit.plate(cam, "y", y + 0.002, 1.8, ZB + 1.02, 2.32, ZB + 1.2, (20, 24, 30))
            on = g("glow") > 0.5 and (g("cycle") < 0.5 or (t % 1.6) < 0.8)
            kit.plane_text(cam, "y", y + 0.004, 2.06, ZB + 1.11, "1:30" if g("waves") > 0.5 else "12:00", 0.08,
                           (90, 255, 140) if on else (60, 200, 110), max_w=0.45)
            for r in range(4):
                for c in range(3):
                    kit.plate(cam, "y", y + 0.002, 1.82 + c * 0.17, ZB + 0.25 + r * 0.17, 1.95 + c * 0.17,
                              ZB + 0.36 + r * 0.17, (200, 204, 214))
        else:
            cam.poly([(1.72, y, ZB), (MX1, y, ZB), (MX1, y, ZB + MH), (1.72, y, ZB + MH)], None, (90, 96, 110), 0.012)
        # door: frame around the window, mesh dots, handle; swings open around its left edge
        if door < 0.02:
            fr = (220, 224, 232)
            for (a0, b0, a1, b1) in ((MX0, ZB, 1.72, ZB + 0.08), (MX0, ZB + 1.2, 1.72, ZB + MH), (MX0, ZB, 0.1, ZB + MH),
                                     (1.62, ZB, 1.72, ZB + MH)):
                kit.plate(cam, "y", y, a0, b0, a1, b1, fr, shade(fr, -0.3))
            mesh = g("mesh")
            if mesh > 0.01:
                step = 0.1
                zz = ZB + 0.12
                while zz < ZB + 1.17:
                    xx = 0.14
                    while xx < 1.6:
                        px, py = cam.p(xx, y + 0.002, zz)
                        r = 0.006 * cam.s * mesh
                        cam.d.ellipse((px - r, py - r, px + r, py + r), fill=(110, 116, 130))
                        xx += step
                    zz += step
            cam.box(1.55, y, ZB + 0.25, 0.06, 0.06, 0.8, (180, 186, 198))
            lk = g("leak")
            if lk > 0.01:
                for i in range(4):
                    f = (t * 0.8 + i / 4) % 1.0
                    rr = 0.2 + f * 1.2
                    pts = [(0.9 + math.cos(a) * rr, y + 0.1 + f * 1.4, ZB + 0.65 + math.sin(a) * rr * 0.6)
                           for a in [math.pi * (0.1 + 0.8 * j / 12) for j in range(13)]]
                    cam.line(pts, mix((255, 120, 60), (255, 230, 210), f), 0.02 * lk, caps=False)
        else:
            ang = door * 1.6
            w = 1.72
            pts = [(MX0, y, ZB), (MX0 + w * math.cos(ang), y + w * math.sin(ang), ZB),
                   (MX0 + w * math.cos(ang), y + w * math.sin(ang), ZB + MH), (MX0, y, ZB + MH)]
            cam.poly(pts, (226, 230, 238), (150, 156, 170), 0.012)
            if door > 0.3:
                kit.label(cam, (1.75, y + 0.05, ZB + 1.45), "LATCH SWITCH: OFF", 0.08, (255, 255, 255), GREEN)

    def _pegs(self, cam, tr, t):
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (3.1, 1.0, ZB), PEG_COLORS[0], expr, t, 1.35, (-0.6, -0.4), seed=1, pose=tr.peg_pose(t),
                react=react, floor=(200, 196, 186))


def draw_bubble(img, tr, t, W, H):
    """Magnifier: water molecules flipping with the field."""
    k = tr.get("bubble", t)
    if k <= 0.01:
        return
    d = ImageDraw.Draw(img)
    cx, cy, R = W * 0.70, H * 0.33, W * 0.24 * k
    d.ellipse((cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), fill=(35, 35, 45))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255))
    u = R / 100.0
    field = 1 if math.sin(t * 9) > 0 else -1
    d.text((cx, cy - 72 * u), "+" if field > 0 else "-", font=font(int(30 * u)), fill=RED if field > 0 else BLUE,
           anchor="mm")
    d.text((cx, cy + 74 * u), "-" if field > 0 else "+", font=font(int(30 * u)), fill=BLUE if field > 0 else RED,
           anchor="mm")
    for i, (mx, my) in enumerate(((-40, -20), (35, -25), (-15, 30), (45, 35), (-50, 40))):
        a = (math.pi / 2 if field > 0 else -math.pi / 2) + 0.4 * math.sin(t * 20 + i)
        ox, oy = cx + mx * u, cy + my * u
        o = 13 * u
        for s in (-1, 1):
            hx = ox + math.cos(a + s * 0.95) * 20 * u
            hy = oy + math.sin(a + s * 0.95) * 20 * u
            d.line((ox, oy, hx, hy), fill=(80, 80, 90), width=max(2, int(3 * u)))
            d.ellipse((hx - 7 * u, hy - 7 * u, hx + 7 * u, hy + 7 * u), fill=(240, 240, 245), outline=(80, 80, 90),
                      width=max(1, int(2 * u)))
        d.ellipse((ox - o, oy - o, ox + o, oy + o), fill=(230, 70, 70), outline=(120, 30, 30), width=max(1, int(2 * u)))
    d.text((cx, cy + R * 0.55), "water", font=font(int(15 * u)), fill=INK, anchor="mm")


def overlays(img, tr, t, W, H):
    draw_bubble(img, tr, t, W, H)


VIDEO = dict(
    slug="microwave",
    title="Why does a fork spark in the microwave?",
    steps=STEPS, scene=MicrowaveScene, initial=INITIAL, overlays=overlays, tracker=dict(label="FIXES"),
)
