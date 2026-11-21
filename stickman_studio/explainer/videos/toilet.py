"""How does a toilet flush without flooding the bathroom? - a gravity toilet built step by step, shown as a
cut-through section (tank, flapper, S-trap siphon, rim holes, fill valve, refill + overflow tubes)."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
WATER = (90, 170, 245)
STINK = (130, 170, 60)

WIDE = ((1.25, 0.9, 1.25), 255)
TANK = ((0.45, 0.9, 1.95), 330)
TRAP = ((1.0, 0.9, 0.55), 330)
BOWL = ((1.5, 0.9, 0.9), 300)

STEPS = [
    dict(text="The simplest toilet is a bucket of water dumped into a bowl with a hole. It's also terrible. "
              "Let's fix it.",
         cam=((1.5, 0.9, 1.0), 420), pegs="neutral",
         cams=[("w:bucket", ((1.5, 0.9, 1.3), 330), 1.0), ("w:terrible", WIDE, 1.3)],
         do=[("bowl", 0.0, 1, 0.7, "back"), ("drain", 0.3, 1, 0.6, "out"), ("bucket", "w:bucket", 1, 0.4, "back"),
             ("pour", "w:dumped", 1, 0.4, "out"), ("bowlw", "w:dumped", 0.6, 0.6, "out"),
             ("bowlw", "w:hole+0.2", 0, 0.8, "in"), ("pour", "w:terrible", 0, 0.3, "in"),
             ("bucket", "w:terrible", 0, 0.4, "in"), ("room", "w:terrible", 1, 1.0, "out")],
         keys=[("bucket of water", INK), ("bowl with a hole", INK), ("also terrible", RED), ("let's fix it", BLUE)],
         pops=[dict(kind="hook", at=0.0, until="w:dumped", text="A toilet has NO pump", hi=["no", "pump"])],
         sfx=[("w:bucket", "pop"), ("w:dumped", "whoosh"), ("w:terrible", "sting")]),
    dict(text="First, a straight hole lets the sewer smell come right back up. So you bend the pipe into an S, and "
              "water stays trapped in the bend. That's the trap, a plug made of water.",
         cam=TRAP, pegs="shocked",
         do=[("stink", "w:smell", 1, 0.6, "out"), ("bend", "w:bend", 1, 1.0, "io"), ("bowlw", "w:water", 1, 0.8, "out"),
             ("stink", "w:trapped", 0, 0.8, "in")],
         keys=[("sewer smell", RED), ("into an S|S-bend", INK), ("the trap", INK), ("plug made of water", BLUE)],
         fix="w:trap",
         pops=[dict(kind="check", at="w:plug", text="smell blocked", pos="tr", until="end+0.2")],
         sfx=[("w:smell", "sting"), ("w:bend", "whoosh")]),
    dict(text="Nobody wants to carry a bucket. So you put a tank of water above the bowl, ready to dump in one go.",
         cam=WIDE, pegs="happy",
         do=[("tank", "w:tank", 1, 0.8, "back"), ("tankw", "w:water", 1, 1.2, "out")],
         keys=[("carry a bucket", RED), ("tank of water", INK), ("in one go", BLUE)],
         fix="w:tank",
         sfx=[("w:tank", "thud")]),
    dict(text="Push the handle, a chain lifts a rubber plug at the bottom of the tank, and water rushes down. "
              "That's the flapper.",
         cam=TANK, pegs="neutral",
         do=[("handle", "w:push", 1, 0.3, "out"), ("chain", "w:chain", 1, 0.4, "out"), ("flap", "w:lifts", 1, 0.4, "out"),
             ("rush", "w:rushes", 1, 0.3, "out"), ("tankw", "w:rushes", 0.75, 1.6, "lin"), ("handle", "w:flapper", 0, 0.4, "io")],
         keys=[("push the handle", INK), ("rubber plug", INK), ("water rushes down", BLUE), ("flapper", INK)],
         fix="w:flapper",
         sfx=[("w:push", "click"), ("w:rushes", "whoosh")]),
    dict(text="The water floods the S-bend so fast that it fills completely, and gravity pulls the whole column "
              "down the drain, dragging everything with it. That's a siphon.",
         cam=TRAP, pegs="shocked",
         do=[("tankw", 0.0, 0.0, 2.6, "io"), ("siph", "w:fills", 1, 0.5, "out"), ("paper", 0.0, 1, 0.3, "out"),
             ("gone", "w:dragging", 1, 1.6, "in"), ("bowlw", "w:pulls", 0.1, 2.0, "io"), ("siph", "w:siphon+0.8", 0, 0.4, "in"),
             ("rush", "w:siphon", 0, 0.4, "in")],
         keys=[("fills completely", INK), ("gravity pulls|gravity pulls it all", BLUE), ("siphon", INK)],
         fix="w:siphon",
         pops=[dict(kind="graph", at="w:fills", title="BOWL WATER", track="bowlw", window=4.0, color=BLUE, pos="tr",
                    until="end+0.2")],
         sfx=[("w:pulls", "rumble"), ("w:siphon", "slap")]),
    dict(text="Pouring through the middle would splash, so the water enters through little holes under the rim and "
              "washes the sides on the way down.",
         cam=BOWL, pegs="happy",
         do=[("splash", "w:splash", 1, 0.3, "out"), ("splash", "w:holes", 0, 0.3, "in"), ("rim", "w:holes", 1, 0.5, "out"),
             ("rim", "end-0.3", 0, 0.3, "in")],
         keys=[("would splash", RED), ("little holes|rim holes", INK), ("washes the sides", BLUE)],
         fix="w:holes",
         pops=[dict(kind="arrow", at="w:holes", xyz=(1.9, 0.9, 1.2), text="rim holes", color=BLUE, off=(0.1, -0.12),
                    until="end", sound=False)]),
    dict(text="Now the tank is empty. A float drops with the water and opens a valve to refill it. As the water "
              "rises, the float rises too and shuts the valve off. That's the fill valve.",
         cam=TANK, pegs="neutral", pose="think",
         do=[("flap", 0.2, 0, 0.4, "in"), ("chain", 0.2, 0, 0.3, "in"), ("fillv", "w:float", 1, 0.5, "back"),
             ("supply", "w:opens", 1, 0.3, "out"), ("tankw", "w:refill", 1, "w:shuts", "io"), ("supply", "w:shuts", 0, 0.3, "in")],
         keys=[("float drops", INK), ("opens a valve", BLUE), ("float rises too", INK), ("fill valve", INK)],
         fix="w:fill",
         pops=[dict(kind="meter", at="w:refill", text="TANK", **{"from": 0.0, "to": 1.0}, color=BLUE, anim=3.0,
                    pos="tr", until="end+0.2")],
         sfx=[("w:opens", "click"), ("w:shuts", "click")]),
    dict(text="But the siphon left the bowl almost empty, and with no water in the bend, the smell is back. So a small "
              "tube tops up the bowl while the tank fills. That's the refill tube.",
         cam=WIDE, pegs="worried",
         do=[("stink", "w:smell", 0.8, 0.5, "out"), ("refill", "w:tube", 1, 0.6, "out"), ("topup", "w:tops", 1, 0.3, "out"),
             ("bowlw", "w:tops", 1, 1.8, "io"), ("stink", "w:tops+0.6", 0, 0.6, "in"), ("topup", "end-0.4", 0, 0.3, "in")],
         keys=[("smell is back", RED), ("tops up the bowl", BLUE), ("refill tube", INK)],
         fix="w:refill",
         sfx=[("w:smell", "sting")]),
    dict(text="And if the valve ever gets stuck open? A tall pipe in the tank catches the extra water and dumps it "
              "into the bowl, so the bathroom never floods. That's the overflow tube.",
         cam=TANK, pegs="shocked",
         do=[("over", "w:tall", 1, 0.6, "back"), ("supply", "w:stuck", 1, 0.3, "out"), ("high", "w:stuck", 1, 1.4, "out"),
             ("spill", "w:catches", 1, 0.4, "out"), ("high", "w:overflow", 0, 0.8, "io"), ("supply", "w:overflow", 0, 0.3, "in"),
             ("spill", "w:overflow+0.4", 0, 0.4, "in")],
         keys=[("stuck open", RED), ("tall pipe", INK), ("never floods", BLUE), ("overflow tube", INK)],
         fix="w:overflow",
         pops=[dict(kind="warn", at="w:stuck", text="valve stuck!", pos="tr", dur=1.8)],
         sfx=[("w:stuck", "sting"), ("w:catches", "whoosh")]),
    dict(text="So next time you hear that gurgle, that's a siphon finishing its job, with zero pumps and zero "
              "electricity.",
         cam=WIDE, pegs="happy", pose="point",
         do=[("siph", "w:gurgle", 1, 0.3, "out"), ("bowlw", "w:gurgle", 0.2, 1.0, "io"), ("bubbles", "w:gurgle+0.4", 1, 0.3, "out"),
             ("siph", "w:finishing+0.4", 0, 0.4, "in"), ("bowlw", "w:zero", 1, 1.4, "io"), ("bubbles", "w:zero", 0, 0.3, "in")],
         keys=[("gurgle", INK), ("siphon finishing|siphon ends with a gulp", BLUE), ("zero pumps|0 pumps, 0 power", BLUE)],
         sfx=[("w:gurgle", "slap")]),
    dict(text="Now you know more about toilets than ninety nine percent of people. Use it wisely. Follow for more.",
         cam=WIDE, pegs="happy", pose="cheer", min=8.4,
         do=[("done", "w:toilets", 1, 0.3, "out")],
         keys=[("more about toilets|toilet expert", BLUE), ("ninety nine percent|than 99% of people", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:toilets", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(bowl=0, drain=0, bucket=0, pour=0, bowlw=0, room=0, stink=0, bend=0, tank=0, tankw=0, handle=0, chain=0,
               flap=0, rush=0, siph=0, paper=0, gone=0, splash=0, rim=0, fillv=0, supply=0, refill=0, topup=0, over=0,
               high=0, spill=0, bubbles=0, done=0)

Y = 0.9                      # the cut plane (front)
PORC = (246, 247, 250)
CAV = (200, 210, 222)
FLOOR = (214, 208, 200)
BOWL_IN = [(1.0, 1.22), (2.25, 1.22), (2.1, 0.95), (1.8, 0.7), (1.5, 0.56), (1.32, 0.52), (1.18, 0.56), (1.05, 0.8)]
BOWL_OUT = [(0.92, 1.3), (2.36, 1.3), (2.28, 1.0), (2.0, 0.72), (1.6, 0.55), (1.5, 0.0), (0.45, 0.0), (0.5, 0.55),
            (0.92, 0.9)]
S_TRAP = [(1.25, 0.54), (1.22, 0.32), (1.05, 0.24), (0.9, 0.36), (0.86, 0.62), (0.8, 0.86), (0.7, 0.9), (0.62, 0.78),
          (0.62, 0.4), (0.62, 0.0)]
LEVEL = 0.8                  # normal water level (weir)
TANK_IN = (0.15, 0.85, 1.55, 2.45)
TANK_OUT = (0.05, 0.95, 1.45, 2.55)
TANK_Z0, TANK_Z1 = 1.56, 2.18


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _ls(cam):
    return max(0.1, 0.033 * cam.img.width / cam.s)


def P(u, v, y=Y):
    return (u, y, v)


def _resample(pts, n):
    return [kit.path_point([(a, 0.0, b) for a, b in pts], i / (n - 1))[0] for i in range(n)]


_ST = [(p[0], p[2]) for p in _resample(S_TRAP, 28)]
_STRAIGHT = [(1.25, 0.54 - 0.54 * i / 27) for i in range(28)]


def _clip_below(poly, z):
    """Part of a 2D polygon (u, v) below the horizontal line v = z."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina, inb = a[1] <= z, b[1] <= z
        if ina:
            out.append(a)
        if ina != inb:
            k = (z - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * k, z))
    return out


class ToiletScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (228, 238, 246), (248, 246, 240), clouds=0)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        if g("room") > 0.01:
            self._room(cam, g("room"))
        if g("bowl") > 0.01:
            self._bowl(cam, tr, t)
        if g("tank") > 0.01:
            self._tank(cam, tr, t)
        self._bucket(cam, tr, t)
        if g("room") > 0.5:
            self._pegs(cam, tr, t)

    # ------------------------------------------------------------- room
    def _room(self, cam, k):
        k = _sm(k)
        cam.poly([(-0.4, -0.6, 0), (4.5, -0.6, 0), (4.5, 4.5, 0), (-0.4, 4.5, 0)], FLOOR)
        for i in range(1, 9):
            cam.line([(-0.4 + i * 0.6, -0.6, 0), (-0.4 + i * 0.6, 4.5, 0)], shade(FLOOR, -0.07), 0.008, caps=False)
            cam.line([(-0.4, -0.6 + i * 0.6, 0), (4.5, -0.6 + i * 0.6, 0)], shade(FLOOR, -0.07), 0.008, caps=False)
        h = 3.4 * k
        cam.poly([(-0.4, -0.6, 0), (4.5, -0.6, 0), (4.5, -0.6, h), (-0.4, -0.6, h)], (222, 236, 238), (190, 204, 206), 0.01)
        cam.poly([(-0.4, -0.6, 0), (-0.4, 4.5, 0), (-0.4, 4.5, h), (-0.4, -0.6, h)], (210, 226, 230), (190, 204, 206), 0.01)
        for i in range(1, 6):
            z = i * 0.55
            if z < h:
                cam.line([(-0.4, -0.599, z), (4.5, -0.599, z)], (206, 222, 224), 0.008, caps=False)
                cam.line([(-0.399, -0.6, z), (-0.399, 4.5, z)], (196, 212, 216), 0.008, caps=False)
        sh = ShadowLayer(cam)
        sh.box_on_plane(0.45, 0.0, 0, 1.9, Y, 1.3, "z", 0.0, 170)
        sh.box_on_plane(0.05, 0.0, 1.45, 0.9, Y, 1.1, "x", -0.4, 120, ((-0.4, -0.4), (-0.6, 4.5), (0, 3.4)))
        sh.apply(cam.img, 0.24, 2.4)
        # toilet roll holder on the left wall + a plant for context
        cam.poly(cam.disc_pts((-0.38, 2.0, 1.0), 0.16, "x", 20), (250, 250, 250), (190, 190, 196), 0.008)
        cam.box(3.4, -0.5, 0, 0.4, 0.4, 0.45, (190, 120, 80))
        for j in range(5):
            a = j * 1.25
            cam.line([(3.6, -0.3, 0.45), (3.6 + 0.3 * math.cos(a), -0.3 + 0.3 * math.sin(a), 1.0 + 0.1 * j)],
                     (80, 160, 90), 0.05)

    # ------------------------------------------------------------- bowl + trap
    def _bowl(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("bowl"))
        sc = lambda pts: [(1.4 + (u - 1.4) * k, v * k) for u, v in pts]
        # depth: extrude the outline from the back (y = 0.05) to the cut plane, then the seat ring on top
        out = sc(BOWL_OUT)
        quads = []
        for a, b in zip(out, out[1:] + out[:1]):
            nz = (b[0] - a[0])                       # edge direction -> roughly "faces up" when it runs along +u at top
            quads.append(((a[1] + b[1]) / 2, a, b))
        for _, a, b in sorted(quads, key=lambda q: q[0]):
            up = abs(a[1] - b[1]) < 0.35 * (abs(a[0] - b[0]) + 1e-6) and (a[1] + b[1]) / 2 > 0.4
            col = shade(PORC, -0.04) if up else shade(PORC, -0.2)
            cam.poly([P(a[0], a[1], 0.05), P(b[0], b[1], 0.05), P(b[0], b[1]), P(a[0], a[1])], col, shade(PORC, -0.35), 0.006)
        if k > 0.95:
            seat = (236, 238, 244)
            for (x0, y0, x1, y1) in ((0.95, 0.05, 2.36, 0.2), (0.95, 0.05, 1.1, Y), (2.2, 0.05, 2.36, Y)):
                cam.box(x0, y0, 1.3, x1 - x0, y1 - y0, 0.05, seat)
        cam.poly([P(u, v) for u, v in sc(BOWL_IN)], CAV, shade(CAV, -0.3), 0.01)
        if k < 0.95:
            return
        # the drain: straight hole morphing into the S-trap
        bend = _sm(g("bend"))
        d = g("drain")
        path = [(a[0] + (b[0] - a[0]) * bend, a[1] + (b[1] - a[1]) * bend) for a, b in zip(_STRAIGHT, _ST)]
        path = path[: max(2, int(len(path) * min(1.0, d * 1.0)) )] if d < 1 else path
        cam.line([P(u, v) for u, v in path], shade(PORC, -0.3), 0.24)
        cam.line([P(u, v) for u, v in path], CAV, 0.17)
        lvl = 0.52 + (LEVEL - 0.52) * g("bowlw")
        siph = g("siph")
        # water in the trap: up to the bowl level (or the whole column during a siphon)
        if bend > 0.5:
            wet = []
            for u, v in path:
                if v > lvl + 0.02 and siph < 0.5:
                    break
                wet.append((u, v))
            if siph > 0.5:
                wet = path
            if len(wet) >= 2:
                cam.line([P(u, v) for u, v in wet], mix(WATER, shade(WATER, -0.2), siph), 0.15)
            if siph > 0.5:
                for i in range(6):
                    s = (t * 0.9 + i / 6) % 1.0
                    p, _ = kit.path_point([P(u, v) for u, v in path], s)
                    kit.glow_dot(cam, p, 0.03, (220, 240, 255))
        # bowl water
        if g("bowlw") > 0.01 or siph > 0.01:
            wpoly = _clip_below(BOWL_IN, lvl)
            if len(wpoly) >= 3:
                cam.poly([P(u, v, Y + 0.001) for u, v in wpoly], mix(WATER, (255, 255, 255), 0.15))
                xs = [u for u, v in wpoly if abs(v - lvl) < 1e-6]
                if len(xs) >= 2:
                    cam.line([P(min(xs), lvl, Y + 0.002), P(max(xs), lvl, Y + 0.002)], (220, 240, 255), 0.02, caps=False)
        # sewer smell through the open drain
        st = g("stink")
        if st > 0.01:
            src = (1.25, Y + 0.05, 0.1) if bend < 0.5 else (0.62, Y + 0.05, 0.1)
            top = 0.6 if bend > 0.5 and g("bowlw") > 0.6 else 1.6
            for i in range(4):
                f = (t * 0.5 + i / 4) % 1.0
                pts = []
                for j in range(8):
                    q = f + j * 0.04
                    pts.append((src[0] + (0.0 if bend < 0.5 else 0.6) * min(1, q * 1.2) + 0.06 * math.sin(q * 20 + i),
                                src[1] + 0.05, src[2] + q * top))
                cam.line(pts, mix(STINK, (255, 255, 255), f * 0.7), 0.03 * st, caps=False)
            if bend > 0.5 and g("bowlw") > 0.6:
                kit.label(cam, (0.75, Y, 1.0), "BLOCKED", _ls(cam), (255, 255, 255), GREEN)
            else:
                kit.label(cam, (1.3, Y, 1.55), "SEWER SMELL", _ls(cam), (255, 255, 255), STINK)
        if bend > 0.9 and g("stink") < 0.05 and g("tank") < 0.5:
            kit.label(cam, (0.75, Y, 1.05), "TRAP", _ls(cam), (255, 255, 255), BLUE)
        # toilet paper pulled down the trap
        pp = g("paper")
        if pp > 0.01:
            gone = g("gone")
            for i in range(3):
                if gone < 0.02:
                    p = P(1.45 + 0.18 * i, lvl + 0.02 + 0.01 * math.sin(t * 3 + i))
                else:
                    s = min(1.0, gone * 1.2 - i * 0.12)
                    if s >= 1.0:
                        continue
                    p, _ = kit.path_point([P(u, v) for u, v in path], max(0.0, s))
                x, yy = cam.p(*p)
                r = 0.06 * cam.s
                cam.d.rectangle((x - r, yy - r * 0.5, x + r, yy + r * 0.5), fill=(255, 255, 255), outline=(200, 200, 206))
        # rim channel + holes
        rim = g("rim")
        cam.line([P(1.02, 1.25), P(2.22, 1.25)], shade(CAV, -0.15), 0.05, caps=False)
        if rim > 0.01:
            for xx in (1.15, 1.45, 1.75, 2.05):
                f = (t * 1.8) % 1.0
                xin = xx + (0.12 if xx > 1.6 else 0.0)
                pts = [P(xin, 1.23), P(xin + (1.4 - xin) * 0.25 * f, 1.23 - 0.5 * f)]
                cam.line(pts, WATER, 0.03 * rim)
                cam.line([P(xx - 0.06, 1.2), P(xx + 0.06, 1.2)], (110, 120, 136), 0.02)
            kit.label(cam, (1.6, Y, 1.5), "WASHES THE SIDES", _ls(cam), (255, 255, 255), BLUE)
        sp = g("splash")
        if sp > 0.01:
            cam.line([P(1.45, 1.6), P(1.45, lvl)], WATER, 0.07 * sp)
            for i in range(6):
                a = math.pi * (0.15 + 0.7 * i / 5)
                f = (t * 1.5 + i / 6) % 1.0
                kit.glow_dot(cam, P(1.45 + math.cos(a) * 0.6 * f, lvl + math.sin(a) * 0.8 * f - 0.6 * f * f), 0.03 * sp,
                             WATER)
        bb = g("bubbles")
        if bb > 0.01:
            for i in range(5):
                f = (t * 1.3 + i / 5) % 1.0
                x, yy = cam.p(*P(1.25 + 0.05 * math.sin(i * 3), 0.55 + f * 0.3))
                r = (0.03 + 0.02 * i % 2) * cam.s * bb
                cam.d.ellipse((x - r, yy - r, x + r, yy + r), outline=(255, 255, 255), width=max(1, int(0.008 * cam.s)))

    # ------------------------------------------------------------- tank
    def _tank(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        si = tr.step_at(t)
        k = _sm(g("tank"))
        x0, x1, z0, z1 = TANK_OUT
        dz = (1 - k) * 0.8
        cam.box(x0, 0.0, z0 + dz, x1 - x0, Y, z1 - z0, PORC, faces="tr")              # lid + side for depth
        cam.poly([P(x0, z0 + dz), P(x1, z0 + dz), P(x1, z1 + dz), P(x0, z1 + dz)], PORC, shade(PORC, -0.35), 0.012)
        ix0, ix1, iz0, iz1 = TANK_IN
        cam.poly([P(ix0, iz0 + dz), P(ix1, iz0 + dz), P(ix1, iz1 + dz), P(ix0, iz1 + dz)], CAV, shade(CAV, -0.3), 0.008)
        if k < 0.95:
            return
        # outlet pipe tank -> rim
        rush = g("rush")
        cam.line([P(0.52, 1.47), P(0.52, 1.36), P(0.98, 1.26)], shade(CAV, -0.25), 0.1)
        if rush > 0.01:
            cam.line([P(0.52, 1.5), P(0.52, 1.36), P(0.98, 1.26), P(2.2, 1.25)], WATER, 0.06 * rush)
        # water
        hi = g("high")
        lv = TANK_Z0 + (TANK_Z1 - TANK_Z0) * g("tankw") + 0.12 * hi
        if lv > TANK_Z0 + 0.01:
            cam.poly([P(ix0, iz0, Y + 0.001), P(ix1, iz0, Y + 0.001), P(ix1, lv, Y + 0.001), P(ix0, lv, Y + 0.001)],
                     mix(WATER, (255, 255, 255), 0.2))
            cam.line([P(ix0, lv, Y + 0.002), P(ix1, lv, Y + 0.002)], (220, 240, 255), 0.02, caps=False)
        # flapper on its seat
        fl = g("flap")
        cam.line([P(0.4, 1.56), P(0.64, 1.56)], (120, 126, 140), 0.04, caps=False)
        a = fl * 1.1
        hx, hz = 0.64, 1.6
        cam.line([P(hx - 0.24 * math.cos(a), hz + 0.24 * math.sin(a)), P(hx, hz)], (200, 60, 60), 0.07)
        if si in (3, 4):
            kit.label(cam, (0.45, Y, 1.4), "FLAPPER", _ls(cam), (255, 255, 255), RED)
        # handle + chain
        hd = g("handle")
        arm_end = (0.48, 2.36 + 0.1 * hd)
        cam.line([P(-0.05, 2.38 - 0.06 * hd), P(0.12, 2.38), P(*arm_end)], (170, 176, 190), 0.035)
        ch = g("chain")
        if True:
            tip = (hx - 0.24 * math.cos(a), hz + 0.24 * math.sin(a))
            n = 10
            sag = 0.08 * (1 - ch)
            pts = [P(arm_end[0] + (tip[0] - arm_end[0]) * i / n + sag * math.sin(math.pi * i / n),
                     arm_end[1] + (tip[1] - arm_end[1]) * i / n) for i in range(n + 1)]
            cam.line(pts, (120, 126, 140), 0.012, caps=False)
        # fill valve + float
        fv = g("fillv")
        sup = g("supply")
        cam.line([P(0.22, 1.5), P(0.22, 0.95), P(-0.38, 0.95)], (170, 176, 190), 0.045)
        cam.box(-0.39, 0.82, 0.88, 0.06, 0.16, 0.14, (190, 196, 206))
        if sup > 0.01:
            for i in range(4):
                s = (t * 0.9 + i / 4) % 1.0
                p, _ = kit.path_point([P(-0.38, 0.95, Y + 0.01), P(0.22, 0.95, Y + 0.01), P(0.22, 2.1, Y + 0.01)], s)
                kit.glow_dot(cam, p, 0.025 * sup, WATER)
            cam.line([P(0.22, 2.12), P(0.22, lv)], WATER, 0.03 * sup)
        if fv > 0.01:
            fk = _sm(fv)
            cam.line([P(0.22, 1.56), P(0.22, 1.56 + 0.66 * fk)], (110, 116, 130), 0.05)
            fz = max(1.62, lv - 0.08)
            kit.plate(cam, "y", Y + 0.003, 0.15, fz - 0.07, 0.3, fz + 0.05, (90, 96, 110))
            if si == 6:
                kit.label(cam, (0.22, Y, 2.62), "FILL VALVE", _ls(cam), (255, 255, 255), INK)
            if si == 6:
                kit.label(cam, (-0.05, Y, fz), "FLOAT", _ls(cam) * 0.85, (255, 255, 255), (90, 96, 110))
        # refill tube
        rf = g("refill")
        if rf > 0.01:
            cam.line(kit.path_prefix([P(0.22, 2.22), P(0.32, 2.36), P(0.56, 2.38), P(0.7, 2.3)], _sm(rf)), (90, 96, 110),
                     0.025)
            if g("topup") > 0.01:
                for i in range(3):
                    s = (t * 1.0 + i / 3) % 1.0
                    p, _ = kit.path_point([P(0.22, 2.22, Y + 0.01), P(0.32, 2.36, Y + 0.01), P(0.56, 2.38, Y + 0.01),
                                           P(0.7, 2.3, Y + 0.01), P(0.7, 1.5, Y + 0.01), P(0.98, 1.27, Y + 0.01),
                                           P(1.3, 0.9, Y + 0.01)], s)
                    kit.glow_dot(cam, p, 0.03 * g("topup"), WATER)
            if si == 7:
                kit.label(cam, (0.5, Y, 2.6), "REFILL TUBE", _ls(cam), (255, 255, 255), BLUE)
        # overflow tube (always there once the refill tube needs it)
        ov = max(g("over"), 1.0 if rf > 0.01 else 0.0)
        if ov > 0.01:
            ok = _sm(ov)
            cam.line([P(0.7, 1.56), P(0.7, 1.56 + 0.72 * ok)], (150, 156, 170), 0.07)
            cam.line([P(0.7, 1.56), P(0.7, 1.56 + 0.72 * ok)], (220, 224, 232), 0.04)
            if si == 8:
                kit.label(cam, (0.82, Y, 2.62), "OVERFLOW TUBE", _ls(cam), (255, 255, 255), RED)
        spl = g("spill")
        if spl > 0.01:
            cam.line([P(0.7, 2.27), P(0.7, 1.45), P(0.98, 1.27), P(1.3, 1.0)], WATER, 0.035 * spl)
            for i in range(3):
                s = (t * 1.2 + i / 3) % 1.0
                p, _ = kit.path_point([P(0.62, lv, Y + 0.01), P(0.7, 2.27, Y + 0.01), P(0.7, 1.45, Y + 0.01)], s)
                kit.glow_dot(cam, p, 0.03 * spl, (220, 240, 255))

    def _bucket(self, cam, tr, t):
        b = tr.get("bucket", t)
        if b <= 0.01:
            return
        k = _sm(b)
        pr = tr.get("pour", t)
        ang = 1.25 * pr
        c = (1.75, 1.95)
        def R(u, v):
            u, v = u * k, v * k
            ca, sa = math.cos(ang), math.sin(ang)
            return P(c[0] + u * ca - v * sa, c[1] + u * sa + v * ca, Y + 0.3)
        cam.poly([R(-0.25, -0.3), R(0.25, -0.3), R(0.32, 0.3), R(-0.32, 0.3)], (120, 150, 200), (60, 80, 120), 0.012)
        cam.line([R(-0.32, 0.3), R(0.0, 0.55), R(0.32, 0.3)], (80, 86, 100), 0.02, caps=False)
        if pr > 0.3:
            lip = R(-0.32, 0.3)
            pts = [(lip[0] - 0.02 - 0.25 * q * q, Y + 0.3, lip[2] - (lip[2] - 0.8) * q) for q in [i / 8 for i in range(9)]]
            cam.line(pts, WATER, 0.1 * pr)

    def _pegs(self, cam, tr, t):
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (2.9, 1.9, 0), PEG_COLORS[3], expr, t, 1.45, (-0.6, -0.5), seed=3, pose=tr.peg_pose(t),
                react=react, floor=FLOOR)


VIDEO = dict(
    slug="toilet",
    title="How does a toilet flush without flooding the bathroom?",
    steps=STEPS, scene=ToiletScene, initial=INITIAL, tracker=dict(label="FIXES"),
)
