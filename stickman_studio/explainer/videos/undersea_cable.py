"""How does a message reach America through the bottom of the ocean? - an undersea cable built step by step."""
from __future__ import annotations

import math

from PIL import ImageDraw

from ...painter import font
from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.story import open_loop
from ..qa import shift_spec
from ..lib.palette import PEG_COLORS

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

X0, X1 = -3.0, 5.0              # shore lines
DEPTH = 3.2
YC = 1.4                        # cable line (y)
D = 2.4                         # diorama depth (y)
REPEATERS = (-1.0, 1.0, 3.0)

WIDE = ((1.2, 1.2, -0.8), 72)
LEFT = ((-2.9, 1.2, -0.3), 190)
DEEP = ((1.0, 1.4, -2.5), 250)


def sea_z(x):
    if x <= X0 or x >= X1:
        return -0.35
    f = (x - X0) / (X1 - X0)
    return -0.35 - 2.4 * math.sin(math.pi * f) ** 0.7


STEPS = [
    dict(text="If you lay a long glass thread across the bottom of the ocean and shine a laser into one end, you've "
              "got the world's simplest internet cable.",
         cam=((-2.6, 1.4, -0.4), 330), pegs="neutral",
         cams=[("w:bottom", ((-0.5, 1.4, -1.6), 170), 1.2), ("w:laser", ((-3.1, 1.4, -0.3), 230), 0.9),
               ("w:simplest", WIDE, 1.4)],
         do=[("thread", 0.0, 1, "w:laser", "lin"), ("ocean", "w:ocean", 1, 1.0, "out"), ("laser", "w:laser", 1, 0.3, "out"),
             ("pulse", "w:shine", 1, 0.3, "out"), ("land", "w:simplest", 1, 1.0, "out")],
         keys=[("glass thread", INK), ("bottom of the ocean", INK), ("laser|+ a laser", INK),
               ("simplest internet cable", BLUE)],
         sfx=[("w:laser", "pop"), ("w:simplest", "whoosh")]),
    dict(text="Light zips through the glass by bouncing off its walls, so it follows the fiber even when it bends. "
              "That's an optical fiber.",
         cam=WIDE, pegs="happy",
         do=[("bubble_kind", 0, 1, 0, "lin"), ("bubble", "w:bouncing", 1, 0.4, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("bouncing off its walls", INK), ("even when it bends", BLUE), ("optical fiber", INK)],
         fix="w:optical"),
    dict(text="But after about a hundred kilometers, even in the clearest glass, almost all the light is gone.",
         cam=((0.5, 1.4, -1.8), 140), pegs="worried",
         do=[("fade", "w:hundred", 1, 1.0, "out")],
         keys=[("hundred kilometers|~100 km", INK), ("light is gone|light fades out", RED)],
         pops=[dict(kind="meter", at="w:clearest", text="SIGNAL", **{"from": 1.0, "to": 0.02}, color=RED, fmt="LOST",
                    anim=2.0, pos="bc", until="end+0.3")]),
    dict(text="So every fifty to a hundred kilometers, you drop a repeater on the seabed that boosts the light back "
              "up.",
         cam=DEEP, pegs="happy",
         do=[("rep", "w:repeater", 1, 0.8, "back"), ("fade", "w:boosts", 0, 0.5, "out")],
         keys=[("fifty to a hundred|every 50-100 km", INK), ("repeater", INK), ("boosts the light", BLUE)],
         fix="w:repeater",
         pops=[dict(kind="arrow", at="w:repeater", xyz=(1.0, YC, sea_z(1.0) + 0.2), text="repeater", color=BLUE,
                    off=(0.1, -0.14), until="end+0.3", sound=False)],
         sfx=[("w:drop", "thud")]),
    dict(text="But a box at the bottom of the ocean has no power socket.",
         cam=DEEP, pegs="worried",
         do=[("nopower", "w:power", 1, 0.3, "out")],
         keys=[("no power socket", RED)],
         pops=[dict(kind="warn", at="w:power", text="no power!", pos="bc", until="end+0.3")]),
    dict(text="So the cable also carries electricity. Thousands of volts get pushed in from the shore and travel along "
              "a copper layer to power every repeater.",
         cam=WIDE, pegs="happy",
         do=[("nopower", 0.2, 0, 0.3, "in"), ("power", "w:electricity", 1, 1.2, "out"),
             ("bubble_kind", "w:copper", 2, 0, "lin"), ("bubble", "w:copper", 1, 0.4, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("carries electricity", INK), ("thousands of volts", INK), ("copper layer", INK)],
         fix="w:electricity",
         sfx=[("w:electricity", "ding")]),
    dict(text="In the deep ocean, the cable is barely thicker than a garden hose, because nothing much down there can "
              "hurt it.",
         cam=DEEP, pegs="neutral",
         do=[("bubble_kind", 0.1, 2, 0, "lin"), ("bubble", "w:garden", 1, 0.4, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("deep ocean", INK), ("garden hose", BLUE)]),
    dict(text="Near the coast it's a different story. Ship anchors and fishing nets drag along the bottom and snag it.",
         cam=LEFT, pegs="shocked",
         do=[("anchor", "w:anchors", 1, 2.2, "io"), ("snag", "w:snag", 1, 0.3, "out")],
         keys=[("near the coast", INK), ("ship anchors", RED), ("snag it", RED)],
         sfx=[("w:snag", "slap")]),
    dict(text="So close to shore, the cable gets wrapped in thick steel wire armor and buried under the seabed.",
         cam=LEFT, pegs="happy",
         do=[("snag", 0.2, 0, 0.3, "in"), ("anchor", 0.2, 0, 0.6, "io"), ("armor", "w:armor", 1, 0.8, "out"),
             ("bury", "w:buried", 1, 0.8, "out"),
             ("bubble_kind", "w:armor", 3, 0, "lin"), ("bubble", "w:armor", 1, 0.4, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("steel wire armor", INK), ("buried under the seabed", BLUE)],
         fix="w:armor",
         sfx=[("w:armor", "thud")]),
    dict(text="One beam of light isn't enough for a whole continent. So each fiber carries dozens of colors of light "
              "at once, and each color is its own channel.",
         cam=((-0.8, 1.4, -1.6), 170), pegs="happy",
         do=[("colors", "w:colors", 1, 0.8, "out"),
             ("bubble_kind", "w:colors", 4, 0, "lin"), ("bubble", "w:colors", 1, 0.4, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("whole continent", RED), ("dozens of colors", INK), ("its own channel|1 color = 1 channel", BLUE)],
         fix="w:colors"),
    dict(text="On each shore, the cable comes up into a landing station that plugs it into the rest of the internet.",
         cam=((6.2, 1.2, 0.3), 180), pegs="neutral",
         do=[("station", "w:landing", 1, 0.6, "back"), ("netlines", "w:plugs", 1, 0.8, "out")],
         keys=[("landing station", INK), ("rest of the internet", BLUE)],
         fix="w:landing"),
    dict(text="Still, every so often a cable breaks.",
         cam=((2.0, 1.4, -2.3), 190), pegs="shocked", min=2.8,
         do=[("broken", "w:breaks", 1, 0.2, "out")],
         keys=[("cable breaks", RED)],
         sfx=[("w:breaks", "slap")]),
    dict(text="So there are always several cables between continents. Traffic instantly reroutes around the broken one, "
              "while a repair ship hooks it up from the bottom and splices it back together.",
         cam=WIDE, pegs="happy",
         do=[("second", "w:several", 1, 0.8, "out"), ("reroute", "w:reroutes", 1, 0.4, "out"),
             ("ship", "w:repair", 1, 0.6, "back"), ("hook", "w:hooks", 1, 1.4, "io"), ("broken", "w:splices", 0, 0.4, "io"),
             ("hook", "end-0.4", 0, 0.4, "io")],
         keys=[("several cables", INK), ("reroutes", BLUE), ("repair ship", INK), ("splices it", BLUE)],
         fix="w:several",
         sfx=[("w:reroutes", "whoosh")]),
    dict(text="That's how almost all the data between continents travels. Not through satellites, but along the bottom "
              "of the ocean.",
         cam=WIDE, pegs="shocked",
         do=[("reroute", 0.2, 0, 0.3, "in"), ("ship", 0.2, 0, 0.5, "in"), ("sat", "w:satellites", 1, 0.4, "back"),
             ("sat_x", "w:satellites", 1, 0.3, "out")],
         keys=[("almost all the data|~99% of it", BLUE), ("not through satellites", RED)],
         pops=[dict(kind="bars", at="w:almost", title="DATA BETWEEN CONTINENTS", until="end+0.3", pos="bc",
                    items=[("undersea cables", 0.99, GREEN), ("satellites", 0.02, RED)])]),
    dict(text="So next time a video from the other side of the world loads instantly, you'll know it just flashed "
              "along the ocean floor as light.",
         cam=WIDE, pegs="happy",
         do=[("sat", 0.2, 0, 0.3, "in"), ("pulse", 0.0, 1, 0, "lin"), ("fast", "w:loads", 1, 0.3, "out")],
         keys=[("other side of the world", INK), ("loads instantly", BLUE), ("as light|it travelled as light", BLUE)]),
    dict(text="And congratulations, you just built an undersea internet cable. Now you just need the sharks to leave "
              "it alone. Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("shark", "w:sharks", 1, 0.5, "out")],
         keys=[("built an undersea internet cable|you built an undersea cable!", BLUE), ("sharks", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

# Scene QA (stickman_studio/explainer/qa.py) - ORIGINAL step indices (VIDEO uses shift_spec(QA, 1) after open_loop inserted the hook). The cable must visibly connect its two ends - laser -> receiver
# before the landing stations exist, station -> station after. Bridges = where it is legitimately out of
# sight: buried in the trench near the left shore, and going into the right cliff.
_TRENCH = (X0 - 0.6, YC - 0.12, -2.5, X0 + 2.25, YC + 0.12, -0.2)
_RIGHT_CLIFF = (X1 + 0.6, 0.0, -DEPTH, X1 + 3.0, D, 0.37)
QA = dict(
    links=[
        dict(name="cable laser->receiver", steps="1-15", width_min=0.03, tol=0.12,
             when=[("station", "<", 0.5), ("broken", "<", 0.5), ("land", ">", 0.95)],
             ends=[dict(color=(60, 64, 76), near=(X0 - 0.7, YC, 0.05), radius=0.5),
                   dict(color=(60, 64, 76), near=(X1 + 1.15, YC, 0.5), radius=0.6)],
             bridges=[_TRENCH, _RIGHT_CLIFF]),
        dict(name="cable station->station", steps="10-15", width_min=0.03, tol=0.12,
             when=[("station", ">", 0.9), ("broken", "<", 0.5)],
             ends=[dict(color=(90, 110, 150), near=(X0 - 1.2, 1.35, 0.6), radius=0.6),
                   dict(color=(90, 110, 150), near=(X1 + 1.2, 1.35, 0.6), radius=0.6)],
             bridges=[_TRENCH, _RIGHT_CLIFF]),
    ],
)

INITIAL = dict(thread=0, ocean=0, laser=0, pulse=0, land=0, bubble=0, bubble_kind=0, fade=0, rep=0, nopower=0, power=0,
               anchor=0, snag=0, armor=0, bury=0, colors=0, station=0, netlines=0, broken=0, second=0, reroute=0, ship=0,
               hook=0, sat=0, sat_x=0, fast=0, shark=0)

SAND = (226, 206, 160)
ROCK = (150, 120, 90)
WATER = (70, 130, 205)
GRASS = (150, 196, 120)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class CableScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (190, 220, 250), (240, 246, 252), clouds=6)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        oc = g("ocean")
        if oc > 0.01:
            self._ocean_back(cam, tr, t, oc)
        self._seabed(cam, tr, t, oc)
        if g("second") > 0.01:
            self._cable(cam, tr, t, y=0.6, second=True)
        self._cable(cam, tr, t, y=YC)
        if oc > 0.01:
            self._water(cam, oc)
            self._front(cam, tr, t, oc)
        if g("land") > 0.01:
            self._land(cam, tr, t)
            self._cable_ends(cam, tr, t)
        self._surface(cam, tr, t)

    # ------------------------------------------------------------- environment
    def _xs(self, n=60):
        return [X0 - 0.6 + (X1 - X0 + 1.2) * i / n for i in range(n + 1)]

    def _ocean_back(self, cam, tr, t, oc):
        k = _sm(oc)
        xs = self._xs()
        pts = [(x, 0.0, 0.0) for x in xs] + [(x, 0.0, sea_z(x) * k) for x in reversed(xs)]
        cam.poly(pts, mix(WATER, (40, 80, 160), 0.3))
        for j in range(3):          # light rays in the water
            x = X0 + 1 + j * 2.4 + 0.3 * math.sin(t * 0.5 + j)
            cam.poly([(x, 0.01, 0.0), (x + 0.5, 0.01, 0.0), (x + 1.2, 0.01, -2.2 * k), (x + 0.9, 0.01, -2.2 * k)],
                     mix(WATER, (130, 190, 240), 0.35))

    def _seabed(self, cam, tr, t, oc):
        k = max(0.25, _sm(oc))
        xs = self._xs()
        for a, b in zip(xs, xs[1:]):
            za, zb = sea_z(a) * k, sea_z(b) * k
            cam.poly([(a, 0, za), (b, 0, zb), (b, D, zb), (a, D, za)], mix(SAND, (200, 180, 140), 0.3 * ((a * 3) % 1)))
        bury = tr.get("bury", t)
        if bury > 0.01:      # trench near the left shore
            for a, b in zip(xs, xs[1:]):
                if a < X0 + 2.2:
                    cam.poly([(a, YC - 0.1, sea_z(a) * k + 0.003), (b, YC - 0.1, sea_z(b) * k + 0.003),
                              (b, YC + 0.1, sea_z(b) * k + 0.003), (a, YC + 0.1, sea_z(a) * k + 0.003)],
                             mix(SAND, (160, 130, 90), 0.6 * bury))
        # rocks + seaweed for life
        for i, x in enumerate((-2.2, -0.3, 1.6, 2.6, 4.0)):
            z = sea_z(x) * k
            cam.box(x, 0.3 + (i % 2) * 1.5, z, 0.3, 0.25, 0.18, (140, 130, 120))
            for j in range(3):
                sway = 0.06 * math.sin(t * 1.5 + i + j)
                cam.line([(x + 0.5 + j * 0.1, 0.4, z), (x + 0.5 + j * 0.1 + sway, 0.4, z + 0.35 + 0.1 * j)],
                         (60, 150, 90), 0.025)

    def _water(self, cam, oc):
        """Translucent water: tinted top surface + front face (the scene stays visible through it)."""
        from PIL import Image, ImageDraw as _D
        k = _sm(oc)
        xs = self._xs()
        m = Image.new("L", cam.img.size, 0)
        d = _D.Draw(m)
        front = [cam.p(x, D, 0.0) for x in xs] + [cam.p(x, D, sea_z(x) * k) for x in reversed(xs)]
        top = [cam.p(xs[0], 0, 0), cam.p(xs[-1], 0, 0), cam.p(xs[-1], D, 0), cam.p(xs[0], D, 0)]
        d.polygon(top, fill=int(60 * k))
        d.polygon(front, fill=int(110 * k))
        cam.img.paste((60, 140, 220), (0, 0, cam.img.width, cam.img.height), m)

    def _front(self, cam, tr, t, oc):
        k = _sm(oc)
        xs = self._xs()
        pts = [(x, D, sea_z(x) * k) for x in xs] + [(xs[-1], D, -DEPTH), (xs[0], D, -DEPTH)]
        cam.poly(pts, shade(SAND, -0.3), shade(SAND, -0.5), 0.01)
        for j in range(1, 4):
            cam.line([(x, D + 0.001, sea_z(x) * k - j * 0.5) for x in xs if sea_z(x) * k - j * 0.5 > -DEPTH],
                     shade(SAND, -0.38), 0.01, caps=False)
        # water edge outline (glass tank look)
        cam.line([(xs[0], D, 0), (xs[-1], D, 0)], (150, 200, 245), 0.02, caps=False)
        # the fish
        for i in range(4):
            x = X0 + ((t * 0.4 + i * 3.1) % (X1 - X0))
            z = -0.8 - 0.4 * i
            if z > sea_z(x) + 0.2:
                px, py = cam.p(x, 1.9 - 0.3 * i, z)
                r = 0.08 * cam.s
                cam.d.ellipse((px - r * 1.6, py - r, px + r * 1.6, py + r), fill=(255, 170, 70))
                cam.d.polygon([(px - r * 1.5, py), (px - r * 2.4, py - r), (px - r * 2.4, py + r)], fill=(255, 140, 60))
        sh = tr.get("shark", t)
        if sh > 0.01:
            x = 1.0 + 1.2 * math.sin(t * 0.8)
            px, py = cam.p(x, 1.8, -1.7)
            r = 0.22 * cam.s * sh
            cam.d.ellipse((px - r * 2.2, py - r * 0.7, px + r * 2.2, py + r * 0.7), fill=(120, 130, 150))
            cam.d.polygon([(px - r * 0.2, py - r * 0.5), (px + r * 0.5, py - r * 1.6), (px + r * 0.9, py - r * 0.5)],
                          fill=(110, 120, 140))
            cam.d.polygon([(px + r * 2.0, py), (px + r * 3.0, py - r), (px + r * 3.0, py + r)], fill=(110, 120, 140))
            cam.d.ellipse((px - r * 1.6, py - r * 0.3, px - r * 1.3, py), fill=(20, 20, 30))

    def _land(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("land"))
        for xa, xb, name in ((X0 - 3.0, X0 - 0.6, "EUROPE"), (X1 + 0.6, X1 + 3.0, "AMERICA")):
            h = 0.35 * k
            cam.box(xa, 0, -DEPTH, xb - xa, D, DEPTH + h, ROCK, top_color=GRASS)
            if k > 0.9:
                kit.label(cam, ((xa + xb) / 2, 0.2, 1.6), name, 0.36, (255, 255, 255), INK)
                # landing station
                st = g("station")
                for i in range(2):
                    cam.box(xa + 0.4 + i * 1.1, 0.3, h, 0.6, 0.6, 0.3 + 0.3 * i, (226, 230, 240))
                if st > 0.01:
                    sx = xb - 1.0 if name == "EUROPE" else xa + 0.2
                    cam.box(sx, 0.9, h, 0.8, 0.9, 0.7 * _sm(st), (90, 110, 150))
                    parts.led(cam, (sx + 0.4, 1.81, h + 0.5), (90, 230, 140), True, 0.04)
                    if st > 0.9 and tr.step_at(t) == 10:
                        kit.label(cam, (sx + 0.4, 1.3, h + 1.2), "LANDING STATION", 0.18, (255, 255, 255), BLUE)
                    nl = g("netlines")
                    if nl > 0.01:
                        for j in range(3):
                            ex = sx + 0.4 + (-1.5 if name == "EUROPE" else 1.5) * (0.5 + j * 0.3)
                            p0, p1 = (sx + 0.4, 1.35, h + 0.7), (ex, 0.3 + j * 0.8, h + 1.0)
                            cam.line([p0, p1], (90, 170, 255), 0.02)
                            kit.packet(cam, [p0, p1], (t * 0.8 + j * 0.3) % 1.0, (90, 170, 255), 0.05)
        if k > 0.9:     # Pegs on both shores (sender + receiver)
            expr = tr.peg_expr(t)
            since = tr.since_step(t)
            react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
            kit.peg(cam, (X0 - 1.9, 1.9, 0.35), PEG_COLORS[0], expr, t, 2.0, (0.6, -0.4), seed=1,
                    pose=tr.peg_pose(t), react=react, floor=GRASS)
            kit.peg(cam, (X1 + 1.6, 1.9, 0.35), PEG_COLORS[1], "happy" if g("pulse") > 0.5 else "neutral", t, 2.0,
                    (-0.6, -0.4), seed=2, pose="wave" if g("fast") > 0.5 else None, floor=GRASS)
        # laser box on the left shore
        if g("laser") > 0.01:
            cam.box(X0 - 0.9, YC - 0.2, -0.1, 0.4, 0.4, 0.3, (60, 64, 76))
            parts.led(cam, (X0 - 0.5, YC, 0.05), (255, 60, 60), True, 0.04)

    def _surface(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        if g("ocean") < 0.5:
            return
        xs = self._xs(80)
        for y in (0.0, D):
            pts = [(x, y, 0.04 * math.sin(x * 3 + t * 2)) for x in xs]
            cam.line(pts, (210, 235, 255), 0.03, caps=False)
        an = g("anchor")
        if an > 0.01:       # fishing boat dragging an anchor near the left shore
            bx = X0 + 1.7 - 0.8 * an
            self._boat(cam, bx, 1.2, (220, 90, 70))
            z_b = sea_z(bx - 0.7)
            cam.line([(bx, 1.2, 0.05), (bx - 0.7, YC, z_b + 0.1)], (60, 60, 70), 0.02)
            ax, az = bx - 0.7, z_b + 0.08
            cam.line([(ax - 0.12, YC, az), (ax + 0.12, YC, az)], (60, 60, 70), 0.05)
            if g("snag") > 0.5 and int(t * 10) % 2:
                kit.glow_dot(cam, (ax, YC, az + 0.1), 0.06, RED)
        sh = g("ship")
        if sh > 0.01:
            bx = 2.1
            self._boat(cam, bx, 1.2, (240, 240, 245), big=True)
            if sh > 0.5:
                kit.label(cam, (bx, 1.2, 1.2), "REPAIR SHIP", 0.2, (255, 255, 255), ORANGE)
            hk = g("hook")
            if hk > 0.01:
                zb = sea_z(2.0)
                hz = zb + 0.1 + (0 - zb) * max(0.0, hk - 0.5) * 2 if hk > 0.5 else 0.0 + (zb + 0.1) * hk * 2
                cam.line([(bx, 1.2, 0.3), (2.0, YC, hz)], (60, 60, 70), 0.02)
        sa = g("sat")
        if sa > 0.01:
            px, py = cam.p(1.0, 1.2, 3.4)
            r = 0.3 * cam.s * sa
            cam.d.rectangle((px - r * 0.4, py - r * 0.4, px + r * 0.4, py + r * 0.4), fill=(200, 205, 215))
            cam.d.rectangle((px - r * 2.0, py - r * 0.25, px - r * 0.5, py + r * 0.25), fill=(60, 100, 200))
            cam.d.rectangle((px + r * 0.5, py - r * 0.25, px + r * 2.0, py + r * 0.25), fill=(60, 100, 200))
            if g("sat_x") > 0.5:
                cam.d.line((px - r * 2.2, py - r * 1.2, px + r * 2.2, py + r * 1.2), fill=RED, width=max(3, int(r * 0.2)))
                cam.d.line((px - r * 2.2, py + r * 1.2, px + r * 2.2, py - r * 1.2), fill=RED, width=max(3, int(r * 0.2)))

    def _boat(self, cam, x, y, color, big=False):
        L = 1.6 if big else 1.0
        cam.box(x - L / 2, y - 0.3, -0.05, L, 0.6, 0.25, color)
        cam.box(x - L * 0.15, y - 0.2, 0.2, L * 0.35, 0.4, 0.3, (250, 250, 252))
        if big:
            cam.line([(x + L * 0.3, y, 0.2), (x + L * 0.3, y, 0.9), (x + L * 0.5, y, 0.7)], (60, 60, 70), 0.03)

    # ------------------------------------------------------------- the cable
    def _cable_pts(self, y, a=None, b=None):
        a = X0 - 0.5 if a is None else a
        b = X1 + 0.5 if b is None else b
        n = 80
        out = []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            out.append((x, y, sea_z(x) + 0.05))
        return out

    def _cable_ends(self, cam, tr, t):
        """Shore ends of the cable: up the left cliff into the laser / landing station, and from the right
        cliff edge across the grass into the receiver / landing station (drawn after the land blocks)."""
        g = lambda k: tr.get(k, t)
        top = 0.35 * _sm(g("land")) + 0.012
        st = g("station") > 0.5
        armor = g("armor")
        col = mix((220, 236, 245), (90, 96, 110), 0.8 * armor)
        w = 0.035 + 0.035 * armor
        for y, key in ((YC, "thread"), (0.6, "second")):
            if g(key) < 0.95:
                continue
            ys = YC if y == YC else 1.05            # second cable also lands inside the station
            if st:
                left = [(X0 - 0.85, ys, top + 0.15), (X0 - 0.6, ys, top), (X0 - 0.6, y, top),
                        (X0 - 0.59, y, sea_z(X0) + 0.05), (X0 - 0.5, y, sea_z(X0) + 0.05)]
                right = [(X1 + 0.6, y, top), (X1 + 0.6, ys, top), (X1 + 0.8, ys, top + 0.15)]
            else:
                if y != YC:
                    continue
                left = [(X0 - 0.5, YC, 0.05), (X0 - 0.59, YC, 0.02), (X0 - 0.59, YC, sea_z(X0) + 0.05),
                        (X0 - 0.5, YC, sea_z(X0) + 0.05)]
                right = [(X1 + 0.6, YC, top), (X1 + 0.95, YC, top)]
            for pts in (left, right):
                cam.line(pts, shade(col, -0.35), w * 1.4)
                cam.line(pts, col, w)
            if not st and y == YC:      # receiver box on the right shore
                cam.box(X1 + 0.95, YC - 0.2, top - 0.01, 0.4, 0.4, 0.3, (60, 64, 76))
                parts.led(cam, (X1 + 1.15, YC + 0.21, top + 0.18), (90, 230, 140) if g("pulse") > 0.5 else (70, 74, 86),
                          g("pulse") > 0.5, 0.04)

    def _cable(self, cam, tr, t, y, second=False):
        g = lambda k: tr.get(k, t)
        th = g("thread") if not second else g("second")
        if th <= 0.01:
            return
        pts = self._cable_pts(y)
        n = max(2, int(len(pts) * min(1.0, th)))
        pts = pts[:n]
        armor = g("armor")
        power = g("power")
        col = mix((220, 236, 245), (200, 140, 80), 0.5 * power)
        for i in range(len(pts) - 1):
            x = pts[i][0]
            shore = x < X0 + 2.2 or x > X1 - 2.0
            w = 0.035 + (0.035 * armor if shore else 0.0)
            c = mix(col, (90, 96, 110), 0.8 * armor) if shore else col
            buried = g("bury") > 0.5 and x < X0 + 2.2 and not second
            if buried:
                continue
            cam.line([pts[i], pts[i + 1]], shade(c, -0.35), w * 1.4, caps=False)
            cam.line([pts[i], pts[i + 1]], c, w, caps=False)
        if second:
            return
        # repeaters
        rp = g("rep")
        if rp > 0.01:
            for rx in REPEATERS:
                z = sea_z(rx) + 0.05 + (1 - _sm(rp)) * 1.5
                cam.box(rx - 0.22, y - 0.12, z - 0.05, 0.44, 0.24, 0.2, (90, 96, 110))
                on = g("nopower") < 0.5 or power > 0.5
                parts.led(cam, (rx, y + 0.13, z + 0.08), (90, 230, 140) if on else (255, 70, 70), True, 0.03)
        # broken section
        if g("broken") > 0.5:
            bx = 2.0
            z = sea_z(bx) + 0.06
            kit.glow_dot(cam, (bx, y, z + 0.05), 0.08, RED)
        # light pulses
        if g("pulse") > 0.5 and th > 0.9:
            fade = g("fade")
            cols = [(255, 80, 80)] if g("colors") < 0.5 else [(255, 80, 80), (80, 220, 120), (90, 150, 255), (255, 200, 60)]
            speed = 0.18 if g("fast") < 0.5 else 0.5
            full = self._cable_pts(y)
            for i in range(10):
                f = (t * speed + i / 10) % 1.0
                p, _ = kit.path_point(full, f)
                if g("broken") > 0.5 and p[0] > 2.0:
                    continue
                # brightness: decays with distance from the last boost point
                last = X0 - 0.5
                if g("rep") > 0.5 and fade < 0.5:
                    for rx in REPEATERS:
                        if rx < p[0]:
                            last = rx
                dist = p[0] - last
                b = math.exp(-dist * (0.35 if g("rep") > 0.5 and fade < 0.5 else 0.12 + 0.6 * fade))
                if b < 0.08:
                    continue
                c = cols[i % len(cols)]
                kit.glow_dot(cam, (p[0], p[1], p[2] + 0.05), 0.05 * (0.4 + 0.6 * b), mix((240, 240, 250), c, b))
        if power > 0.5:
            for i in range(6):
                f = (t * 0.3 + i / 6) % 1.0
                p, _ = kit.path_point(self._cable_pts(y), f)
                kit.glow_dot(cam, (p[0], p[1] - 0.12, p[2] + 0.02), 0.03, (255, 190, 60))
        if g("reroute") > 0.5:
            alt = self._cable_pts(0.6)
            for i in range(8):
                f = (t * 0.3 + i / 8) % 1.0
                p, _ = kit.path_point(alt, f)
                kit.glow_dot(cam, (p[0], p[1], p[2] + 0.05), 0.05, (90, 230, 140))


def draw_bubble(img, tr, t, W, H):
    k = tr.get("bubble", t)
    kind = int(round(tr.get("bubble_kind", t)))
    if k <= 0.01 or kind == 0:
        return
    d = ImageDraw.Draw(img)
    cx, cy, R = W * 0.70, H * 0.33, W * 0.24 * k
    d.ellipse((cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), fill=(35, 35, 45))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255))
    u = R / 100.0
    lw = max(2, int(3 * u))
    if kind == 1:      # light bouncing inside a bent fiber
        pts = []
        for i in range(60):
            f = i / 59
            pts.append((cx - 80 * u + 160 * u * f, cy + 25 * u * math.sin(f * 3)))
        top = [(x, y - 14 * u) for x, y in pts]
        bot = [(x, y + 14 * u) for x, y in pts]
        d.line(top, fill=(120, 170, 220), width=lw)
        d.line(bot, fill=(120, 170, 220), width=lw)
        ray = []
        for i in range(13):
            x, y = pts[min(59, i * 5)]
            ray.append((x, y + (-11 if i % 2 else 11) * u))
        d.line(ray, fill=RED, width=lw)
        d.text((cx, cy + 62 * u), "light bounces off the walls", font=font(int(12 * u)), fill=INK, anchor="mm")
    elif kind in (2, 3):   # cable cross-section
        layers = [(16, (250, 250, 255), "fibers"), (22, (200, 140, 80), "copper (power)"), (34, (60, 60, 70), "insulation")]
        if kind == 3:
            layers.append((50, (150, 156, 170), "steel armor"))
            layers.append((58, (40, 40, 48), ""))
        for r, c, _ in reversed(layers):
            d.ellipse((cx - r * u, cy - 10 * u - r * u, cx + r * u, cy - 10 * u + r * u), fill=c, outline=(30, 30, 40),
                      width=max(1, int(1.5 * u)))
        for j in range(6):
            a = j * 1.047
            px, py = cx + math.cos(a) * 8 * u, cy - 10 * u + math.sin(a) * 8 * u
            d.ellipse((px - 3 * u, py - 3 * u, px + 3 * u, py + 3 * u), fill=(255, 220, 80))
        d.text((cx, cy + 62 * u), "deep sea: ~ garden hose" if kind == 2 else "near shore: armored", font=font(int(12 * u)),
               fill=INK, anchor="mm")
    elif kind == 4:    # several colours of light in one fiber
        cols = [(255, 80, 80), (255, 170, 60), (240, 220, 60), (80, 220, 120), (90, 150, 255), (170, 110, 255)]
        d.rectangle((cx - 85 * u, cy - 22 * u, cx + 85 * u, cy + 22 * u), outline=(120, 170, 220), width=lw)
        for j, c in enumerate(cols):
            y = cy - 15 * u + j * 6 * u
            off = (t * 60 + j * 13) % 30
            x = cx - 80 * u - off * u
            while x < cx + 80 * u:
                d.line((max(cx - 82 * u, x), y, min(cx + 82 * u, x + 14 * u), y), fill=c, width=lw)
                x += 30 * u
        d.text((cx, cy + 52 * u), "each colour = its own channel", font=font(int(12 * u)), fill=INK, anchor="mm")


def overlays(img, tr, t, W, H):
    draw_bubble(img, tr, t, W, H)


# open-loop structure (2026-11-22): question hook + teaser, reminder, late answer, loop ending
STEPS = open_loop(
    STEPS, "Why is there a ship fishing for the internet at the bottom of the ocean?", answer_step=12,
    teaser_frac=0.7, reminder=(7, "And that fishing ship? It's coming."), reveal="Here's where the ship comes in.",
    hook_keys=[("fishing for the internet", RED), ("bottom of the ocean", INK)],
    ending_text="And that's how you build an undersea internet cable. Follow for more. And next time someone asks you,",
    ending_keys=[("undersea internet cable|how you build it", BLUE)], ending_do=[])  # O2 hook, E2 ending + loop

VIDEO = dict(
    slug="undersea_cable",
    title="How does a message cross the ocean?",
    steps=STEPS, end_cover=False, scene=CableScene, initial=INITIAL, overlays=overlays, tracker=dict(label="FIXES"), qa=shift_spec(QA, 1),
)
