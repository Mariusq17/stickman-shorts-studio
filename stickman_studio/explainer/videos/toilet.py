"""How does a toilet flush without a pump? - a gravity toilet built step by step as a true cut-through section
(v3). Water only ever moves inside the porcelain channels: tank -> flush passage -> rim channel -> rim holes ->
bowl -> S-trap -> drain pipe under the floor. One flush is shown in slow motion across three steps."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
WATER = (90, 168, 240)
STINK = (120, 165, 50)

WIDE = ((1.4, 0.9, 0.85), 215)
TRAP = ((0.95, 0.9, 0.35), 320)
TANK = ((0.5, 0.9, 1.85), 340)
BOWL = ((1.55, 0.9, 1.0), 300)


def R(cue, text):
    """Checkpoint: the newly built part slams in big (with a ding in sfx)."""
    return dict(kind="stamp", at=cue, text=text, color=BLUE, pos="tr", dur=2.0)


def E(cue, emoji, text="", no=False, xy=(0.8, 0.72), until=None, dur=2.2):
    p = dict(kind="emoji", at=cue, emoji=emoji, text=text, no=no, xy=xy)
    if until:
        p["until"] = until
    else:
        p["dur"] = dur
    return p


STEPS = [
    dict(text="Your toilet has no pump. No motor, no battery, not even a plug. And yet it makes everything vanish in "
              "seconds. So let's build one from scratch. Step one: a bowl with a hole, and a bucket of water. Dump it "
              "in, and it works! It's also disgusting.",
         cam=((1.55, 0.9, 1.05), 400), pegs="neutral",
         cams=[("w:scratch", ((1.4, 0.9, 1.1), 300), 1.0), ("w:disgusting", WIDE, 1.3)],
         do=[("bowl", 0.0, 1, 0.7, "back"), ("drain", 0.2, 1, 0.6, "out"), ("bucket", "w:bucket", 1, 0.4, "back"),
             ("pour", "w:dump", 1, 0.4, "out"), ("bowlw", "w:dump", 0.5, 0.6, "out"),
             ("bowlw", "w:works", 0, 0.9, "in"), ("pour", "w:works+0.4", 0, 0.3, "in"),
             ("bucket", "w:disgusting", 0, 0.4, "in"), ("room", "w:disgusting", 1, 1.0, "out"),
             ("stink", "w:disgusting", 1, 0.5, "out")],
         keys=[("vanish in seconds", BLUE), ("bowl with a hole|bowl + hole + bucket", INK), ("it works|it works!", BLUE),
               ("also disgusting", RED)],
         pops=[dict(kind="hook", at=0.0, until="w:vanish", text="A toilet has NO pump", hi=["no", "pump"]),
               E("w:motor", "⚙️", "no motor", True, (0.2, 0.8), until="w:vanish"),
               E("w:battery", "🔋", "no battery", True, (0.5, 0.8), until="w:vanish"),
               E("w:plug", "🔌", "no plug", True, (0.8, 0.8), until="w:vanish"),
               E("w:disgusting", "🤢", xy=(0.8, 0.72), dur=2.0)],
         sfx=[("w:bucket", "pop"), ("w:dump", "whoosh")]),
    dict(text="Because the sewer is right under your floor, and that hole is an open window for the smell. Fix: bend "
              "the pipe into an S. Water gets stuck in the bend and plugs it, like a cork made of water. Say hello to "
              "the trap!",
         cam=TRAP, pegs="shocked", pause=0.8,
         do=[("bend", "w:bend", 1, 1.2, "io"), ("bowlw", "w:stuck", 1, 0.9, "out")],
         keys=[("open window for the smell|open window for the smell", RED), ("into an S|S-bend", INK),
               ("cork made of water", BLUE)],
         fix="w:trap",
         pops=[E("w:sewer", "👃", "sewer smell", xy=(0.2, 0.72), dur=2.4), E("w:cork", "🍾", "water cork", xy=(0.8, 0.72)),
               R("w:trap", "THE TRAP!")],
         sfx=[("w:bend", "whoosh"), ("w:trap", "ding")]),
    dict(text="Next problem: nobody wants to haul a bucket every time nature calls. So we park the water right above "
              "the bowl, ready to go. Upgrade: a tank!",
         cam=WIDE, pegs="happy", pause=0.8,
         do=[("tank", "w:park", 1, 0.9, "back"), ("tankw", "w:ready", 1, 1.4, "out"), ("stink", "w:park", 0, 0.5, "in")],
         keys=[("haul a bucket", RED), ("right above the bowl", INK)],
         fix="w:tank",
         pops=[E("w:haul", "🪣", "every time?", xy=(0.2, 0.72)), R("w:tank", "A TANK!")],
         sfx=[("w:park", "thud"), ("w:tank", "ding")]),
    dict(text="To release it, there's a rubber plug at the bottom, tied to the handle with a little chain. Push the "
              "handle, the plug lifts, and the tank starts to empty. That plug is the flapper!",
         cam=TANK, pegs="neutral", pause=0.7,
         do=[("flapper", "w:plug", 1, 0.5, "back"), ("chain", "w:chain", 1, 0.5, "out"), ("handle", "w:push", 1, 0.3, "out"),
             ("flap", "w:lifts", 1, 0.4, "out"), ("rush", "w:lifts+0.2", 1, 0.3, "out"), ("slowmo", "w:lifts", 1, 0.3, "out"),
             ("tankw", "w:lifts+0.2", 0.72, "end", "lin"), ("handle", "w:flapper", 0, 0.4, "io"),
             ("bowlw", "w:lifts+0.8", 1.12, "end", "io")],
         keys=[("rubber plug", INK), ("little chain", INK), ("push the handle", INK)],
         fix="w:flapper",
         pops=[R("w:flapper", "FLAPPER!"), dict(kind="note", at="w:lifts", text="slow motion", pos="bl", until="end+0.3")],
         sfx=[("w:push", "click"), ("w:lifts", "whoosh"), ("w:flapper", "ding")]),
    dict(text="But dumping all that water in the middle would splash you. So it sneaks out through tiny holes hidden "
              "under the rim, and washes the walls on the way down. Rim holes!",
         cam=BOWL, pegs="happy", pause=0.7,
         do=[("tankw", 0.0, 0.42, "end", "lin"), ("bowlw", 0.0, 1.3, "end", "io"), ("rim", "w:sneaks", 1, 0.5, "out")],
         keys=[("splash you", RED), ("hidden under the rim", INK), ("washes the walls", BLUE)],
         fix="w:rim",
         pops=[E("w:splash", "💦", "splash!", xy=(0.8, 0.45)), R("w:holes", "RIM HOLES!"),
               dict(kind="note", at=0.0, text="slow motion", pos="bl", until="end+0.3")],
         sfx=[("w:holes", "ding")]),
    dict(text="Now the magic trick. The water pours in so fast that it fills the entire S bend. And the moment that "
              "bend is full, gravity pulls the whole column down the drain, and drags everything in the bowl along. "
              "That's a siphon! Same trick as emptying a fish tank with a hose.",
         cam=TRAP, pegs="shocked", pause=0.6,
         cams=[("w:drags", ((1.0, 0.9, 0.5), 260), 1.0)],
         do=[("paper", 0.0, 1, 0.4, "out"), ("tankw", 0.0, 0.0, "w:drags", "lin"), ("siph", "w:fills", 1, 0.6, "out"),
             ("bowlw", "w:gravity", 0.05, "w:siphon", "io"), ("gone", "w:drags", 1, 2.2, "in"),
             ("flap", "w:siphon", 0, 0.5, "in"), ("rush", "w:siphon", 0, 0.5, "in"), ("rim", "w:siphon", 0, 0.4, "in"),
             ("bubbles", "w:fish-0.6", 1, 0.3, "out"), ("siph", "w:fish", 0, 0.6, "in"), ("bubbles", "end-0.3", 0, 0.3, "in"),
             ("slowmo", "end-0.4", 0, 0.3, "in")],
         keys=[("magic trick", INK), ("fills the entire|fills the whole bend", INK), ("gravity pulls|gravity pulls it all", BLUE)],
         fix="w:siphon",
         pops=[R("w:siphon", "SIPHON!"), E("w:fish", "🐠", "fish tank + hose", xy=(0.8, 0.45), dur=2.6),
               dict(kind="note", at=0.0, text="slow motion", pos="bl", until="w:siphon")],
         sfx=[("w:gravity", "rumble"), ("w:siphon", "ding")]),
    dict(text="Now the tank is empty, and nobody is refilling it by hand. So a float rides on the water. Float goes "
              "down, valve opens. Water comes up, float rises, valve shuts. No chip, no sensor, just a float. That's "
              "the fill valve!",
         cam=TANK, pegs="neutral", pose="think", pause=0.7,
         do=[("fillv", "w:float", 1, 0.6, "back"), ("supply", "w:opens", 1, 0.3, "out"),
             ("tankw", "w:opens", 1, "w:shuts", "io"), ("supply", "w:shuts", 0, 0.3, "in")],
         keys=[("by hand", RED), ("valve opens", BLUE), ("valve shuts", INK), ("just a float", BLUE)],
         fix="w:fill",
         pops=[E("w:chip", "💾", "no chip", True, (0.2, 0.72), dur=2.0), R("w:fill", "FILL VALVE!")],
         sfx=[("w:opens", "click"), ("w:shuts", "click"), ("w:fill", "ding")]),
    dict(text="One catch: the siphon sucked the bowl nearly dry, and with no water in the bend, the smell is back. So a "
              "tiny tube sneaks some water into the bowl while the tank refills. Refill tube!",
         cam=WIDE, pegs="worried", pause=0.7,
         do=[("stink", "w:smell", 1, 0.5, "out"), ("over", "w:tiny", 1, 0.6, "out"), ("refill", "w:tiny", 1, 0.6, "out"),
             ("topup", "w:sneaks", 1, 0.3, "out"), ("bowlw", "w:sneaks", 1, 2.0, "io"), ("topup", "w:refill", 0, 0.4, "in")],
         keys=[("nearly dry", RED), ("smell is back", RED), ("sneaks some water|tops up the bowl", BLUE)],
         fix="w:refill",
         pops=[E("w:smell", "🤢", "it's back", xy=(0.2, 0.72)), R("w:refill", "REFILL TUBE!")],
         sfx=[("w:smell", "sting"), ("w:refill", "ding")]),
    dict(text="And if that valve ever gets stuck open? A tall pipe in the tank swallows the extra water and sends it "
              "into the bowl, so your bathroom never becomes a swimming pool. Overflow tube!",
         cam=TANK, pegs="shocked", pause=0.7,
         do=[("stink", 0.0, 0, 0.5, "in"), ("supply", "w:stuck", 1, 0.3, "out"), ("high", "w:stuck", 1, "w:swallows", "io"),
             ("spill", "w:swallows", 1, 0.4, "out"), ("high", "w:overflow", 0, 0.9, "io"), ("supply", "w:overflow", 0, 0.3, "in"),
             ("spill", "w:overflow+0.5", 0, 0.4, "in")],
         keys=[("stuck open", RED), ("tall pipe", INK), ("never becomes a swimming pool|no swimming pool", BLUE)],
         fix="w:overflow",
         pops=[E("w:pool", "🏊", "bathroom pool", True, (0.2, 0.72)), R("w:overflow", "OVERFLOW TUBE!")],
         sfx=[("w:stuck", "sting"), ("w:overflow", "ding")]),
    dict(text="So that loud gurgle at the end of every flush? That's the siphon running out of water and gulping air. "
              "No pumps, no electricity. Just gravity, doing the dirty work.",
         cam=WIDE, pegs="happy", pose="point",
         do=[("handle", 0.0, 1, 0.2, "out"), ("handle", 0.5, 0, 0.3, "io"), ("flap", 0.1, 1, 0.3, "out"), ("rush", 0.2, 1, 0.3, "out"),
             ("tankw", 0.2, 0.0, "w:gurgle", "lin"), ("bowlw", 0.2, 1.3, 0.9, "io"), ("rim", 0.2, 1, 0.3, "out"),
             ("siph", 1.0, 1, 0.3, "out"), ("bowlw", 1.2, 0.05, "w:gulping", "io"),
             ("flap", "w:gurgle", 0, 0.4, "in"), ("rush", "w:gurgle", 0, 0.4, "in"), ("rim", "w:gurgle", 0, 0.4, "in"),
             ("bubbles", "w:gurgle", 1, 0.3, "out"), ("siph", "w:air", 0, 0.5, "in"), ("bubbles", "w:pumps", 0, 0.3, "in"),
             ("supply", "w:pumps", 1, 0.3, "out"), ("tankw", "w:pumps", 1, "end", "io"), ("topup", "w:pumps", 1, 0.3, "out"),
             ("bowlw", "w:pumps", 1, "end", "io"), ("supply", "end-0.2", 0, 0.2, "in"), ("topup", "end-0.2", 0, 0.2, "in")],
         keys=[("loud gurgle", INK), ("gulping air|the siphon gulps air", BLUE), ("dirty work|gravity does the dirty work", BLUE)],
         pops=[E("w:gurgle", "🔊", "gurgle!", xy=(0.2, 0.72)), E("w:gravity", "🌍", "just gravity", xy=(0.8, 0.72))],
         sfx=[("w:gurgle", "slap")]),
    dict(text="Now you know more about toilets than ninety nine percent of people. Use this power wisely. And wash "
              "your hands. Follow for more.",
         cam=WIDE, pegs="happy", pose="cheer", min=8.4,
         do=[("done", "w:toilets", 1, 0.3, "out")],
         keys=[("more about toilets|toilet expert", BLUE), ("wash your hands", INK)],
         pops=[E("w:wash", "🧼", "wash your hands", xy=(0.2, 0.72), dur=2.0),
               dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:toilets", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(bowl=0, drain=0, bucket=0, pour=0, bowlw=0, room=0, stink=0, bend=0, tank=0, tankw=0, flapper=0, chain=0,
               handle=0, flap=0, rush=0, slowmo=0, rim=0, siph=0, paper=0, gone=0, bubbles=0, fillv=0, supply=0, over=0,
               refill=0, topup=0, high=0, spill=0, done=0)

# ---------------------------------------------------------------- geometry (u = x along the toilet, v = height)
Y = 0.9                                   # the cut plane; the toilet body spans y = 0 .. Y
PORC = (247, 248, 251)
CUT = (236, 238, 244)                     # porcelain cut face
CAV = (196, 206, 220)                     # inside surfaces
FLOOR = (214, 206, 196)
CONCRETE = (186, 182, 176)
EARTH = (150, 128, 104)

BODY = [(0.05, 1.38), (2.28, 1.38), (2.3, 1.25), (2.15, 0.98), (1.85, 0.72), (1.55, 0.6), (1.5, 0.0), (0.5, 0.0),
        (0.5, 0.6), (0.4, 1.0), (0.3, 1.2), (0.05, 1.3)]
TANK_OUT = [(0.05, 1.38), (0.95, 1.38), (0.95, 2.45), (0.05, 2.45)]
TANK_IN = (0.13, 0.87, 1.45, 2.38)
BOWL_IN = [(1.0, 1.38), (2.24, 1.38), (2.2, 1.2), (2.08, 1.05), (1.85, 0.82), (1.55, 0.68), (1.38, 0.6), (1.22, 0.6),
           (1.12, 0.78), (1.05, 1.05), (1.0, 1.2)]
BACK_WALL = [(1.06, 1.2), (1.05, 1.05), (1.12, 0.78), (1.24, 0.62)]
FRONT_WALL = [(2.16, 1.2), (2.08, 1.05), (1.85, 0.82), (1.55, 0.68), (1.36, 0.62)]
S_TRAP = [(1.3, 0.62), (1.28, 0.47), (1.15, 0.38), (0.98, 0.4), (0.88, 0.52), (0.84, 0.7), (0.8, 0.84), (0.72, 0.9),
          (0.64, 0.84), (0.6, 0.7), (0.6, 0.3), (0.6, -0.02)]
FLUSH = [(0.56, 1.45), (0.56, 1.33), (0.8, 1.29), (1.04, 1.28)]
L0 = 0.83                                 # normal bowl level = bottom of the weir
LV_SUMP = 0.62
TANK_LO, TANK_HI = 1.5, 2.05
HINGE = (0.66, 1.5)
OVER_X, OVER_TOP = 0.69, 2.22
FILL_X = 0.24
TRAP_W = 0.14


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _ls(cam):
    return max(0.09, 0.033 * cam.img.width / cam.s)


def P(u, v, y=Y):
    return (u, y, v)


def PL(pts, y=Y):
    return [P(u, v, y) for u, v in pts]


def _resample(pts, n):
    q = [(a, 0.0, b) for a, b in pts]
    return [(p[0], p[2]) for p in (kit.path_point(q, i / (n - 1))[0] for i in range(n))]


_ST = _resample(S_TRAP, 32)
_STRAIGHT = [(1.3, 0.62 - 0.64 * i / 31) for i in range(32)]


def _clip_below(poly, z):
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


def _bowl_level(bw):
    """bowlw: 0 = empty sump, 1 = normal (weir), up to 1.3 = rising during a flush."""
    if bw <= 1.0:
        return LV_SUMP + (L0 - LV_SUMP) * bw
    return L0 + (bw - 1.0) * 0.55


def _extrude(cam, poly, col, y0=0.0, y1=Y):
    """Side walls of a prism with the cut face at y1 (drawn bottom-up so top faces end up on top)."""
    edges = list(zip(poly, poly[1:] + poly[:1]))
    for a, b in sorted(edges, key=lambda e: (e[0][1] + e[1][1])):
        flat = abs(a[1] - b[1]) < 0.4 * abs(a[0] - b[0]) + 1e-6
        c = shade(col, -0.03) if flat and (a[1] + b[1]) / 2 > 0.3 else shade(col, -0.2)
        cam.poly([P(a[0], a[1], y0), P(b[0], b[1], y0), P(b[0], b[1], y1), P(a[0], a[1], y1)], c, shade(col, -0.38),
                 0.005)


class ToiletScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (226, 236, 244), (246, 244, 238), clouds=0)
        self.path = list(_STRAIGHT)
        self.drain_pipe = [(1.3, 0.0), (1.3, -0.55), (1.15, -0.72), (-0.5, -0.78)]
        self.lvl = LV_SUMP

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        self.si = step_i
        room = g("room")
        self._room(cam, tr, t, room)
        if g("bowl") > 0.01:
            self._body(cam, tr, t)
        if g("tank") > 0.01:
            self._tank(cam, tr, t)
        self._bucket(cam, tr, t)
        self._smell(cam, tr, t)
        if room > 0.5 and cam.s / (cam.img.width / 1080) < 290:
            expr = tr.peg_expr(t)
            react = max(0.0, 1.0 - tr.since_step(t) / 0.5) if expr == "shocked" else 0.0
            kit.peg(cam, (2.7, 0.25, 0), PEG_COLORS[3], expr, t, 1.45, (-0.7, 0.2), seed=3, pose=tr.peg_pose(t),
                    react=react, floor=FLOOR)

    # ------------------------------------------------------------- room (sliced at the cut plane)
    def _room(self, cam, tr, t, room):
        k = _sm(room)
        bend = _sm(tr.get("bend", t))
        if k > 0.01:
            h = 3.0 * k
            cam.poly([(-0.5, -0.6, 0), (4.2, -0.6, 0), (4.2, -0.6, h), (-0.5, -0.6, h)], (222, 236, 238),
                     (190, 204, 206), 0.01)
            cam.poly([(-0.5, -0.6, 0), (-0.5, Y, 0), (-0.5, Y, h), (-0.5, -0.6, h)], (210, 226, 230), (190, 204, 206),
                     0.01)
            for i in range(1, 6):
                z = i * 0.5
                if z < h:
                    cam.line([(-0.5, -0.599, z), (4.2, -0.599, z)], (206, 222, 224), 0.006, caps=False)
            cam.poly([(-0.5, -0.6, 0), (4.2, -0.6, 0), (4.2, Y, 0), (-0.5, Y, 0)], FLOOR)
            for i in range(1, 8):
                cam.line([(-0.5 + i * 0.6, -0.6, 0.001), (-0.5 + i * 0.6, Y, 0.001)], shade(FLOOR, -0.07), 0.006,
                         caps=False)
            sh = ShadowLayer(cam)
            sh.box_on_plane(0.5, 0.0, 0, 1.0, Y, 1.3, "z", 0.0, 170)
            sh.apply(cam.img, 0.22, 2.4)
        # cut face of the floor slab and the ground below, with the drain pipe to the sewer
        x0 = 1.3 + (0.6 - 1.3) * bend
        u0, u1 = -0.5, 4.2
        cam.poly(PL([(u0, 0.0), (u1, 0.0), (u1, -0.22), (u0, -0.22)]), CONCRETE, shade(CONCRETE, -0.3), 0.006)
        cam.poly(PL([(u0, -0.22), (u1, -0.22), (u1, -1.05), (u0, -1.05)]), EARTH, shade(EARTH, -0.3), 0.006)
        pipe = [(x0, 0.0), (x0, -0.55), (x0 - 0.15, -0.72), (-0.5, -0.78)]
        cam.line(PL(pipe), (120, 124, 136), 0.2, caps=False)
        cam.line(PL(pipe), (60, 64, 76), 0.15, caps=False)
        if k > 0.5 and self.si in (0, 1):
            kit.label(cam, P(-0.1, -0.55), "SEWER", _ls(cam), (255, 255, 255), (110, 90, 60))
        self.drain_pipe = pipe

    # ------------------------------------------------------------- porcelain body + water
    def _body(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("bowl"))
        body = [(1.3 + (u - 1.3) * k, v * k) for u, v in BODY]
        _extrude(cam, body, PORC)
        cam.poly(PL(body), CUT, shade(PORC, -0.35), 0.01)
        if k < 0.97:
            return
        for (a0, b0, a1, b1) in ((0.98, 0.05, 2.3, 0.2), (0.98, 0.05, 1.12, Y), (2.16, 0.05, 2.3, Y)):
            cam.box(a0, b0, 1.38, a1 - a0, b1 - b0, 0.05, (238, 240, 246))
        cam.poly(PL(BOWL_IN), CAV, shade(CAV, -0.3), 0.008)
        bend = _sm(g("bend"))
        d = g("drain")
        path = [(a[0] + (b[0] - a[0]) * bend, a[1] + (b[1] - a[1]) * bend) for a, b in zip(_STRAIGHT, _ST)]
        if d < 1:
            path = path[:max(2, int(len(path) * d))]
        cam.line(PL(path), shade(CAV, -0.3), TRAP_W + 0.03)
        cam.line(PL(path), CAV, TRAP_W)
        self.path = path
        bw = g("bowlw")
        lvl = _bowl_level(bw)
        siph = g("siph")
        # trap water: communicating vessels - water up to the bowl level, unless the siphon runs
        if bend > 0.5 and siph < 0.5:
            wet = []
            for p in path:
                if p[1] > lvl + 0.03:
                    break
                wet.append(p)
            if len(wet) >= 2:
                cam.line(PL(wet), WATER, TRAP_W * 0.82, caps=False)
        if bend < 0.5 and g("pour") > 0.5:
            kit.flow_line(cam, PL(path) + PL(self.drain_pipe[1:]), t, WATER, 0.1, speed=1.6)
        if siph > 0.01:
            kit.flow_line(cam, PL(path) + PL(self.drain_pipe[1:]), t, WATER, TRAP_W * 0.82, speed=1.4, amount=siph)
        # bowl water
        if lvl > LV_SUMP + 0.005:
            wpoly = _clip_below(BOWL_IN, lvl)
            if len(wpoly) >= 3:
                cam.poly(PL(wpoly, Y + 0.001), mix(WATER, (255, 255, 255), 0.12))
                xs = [u for u, v in wpoly if abs(v - lvl) < 1e-6]
                if len(xs) >= 2:
                    cam.line([P(min(xs), lvl, Y + 0.002), P(max(xs), lvl, Y + 0.002)], (215, 236, 255), 0.018,
                             caps=False)
        self.lvl = lvl
        # rim lip with its hollow channel (front + back) and the holes underneath
        for cx in (1.08, 2.18):
            cam.poly(PL([(cx - 0.1, 1.38), (cx + 0.1, 1.38), (cx + 0.1, 1.22), (cx - 0.1, 1.22)]), CUT,
                     shade(PORC, -0.35), 0.006)
            cam.poly(PL([(cx - 0.05, 1.33), (cx + 0.05, 1.33), (cx + 0.05, 1.26), (cx - 0.05, 1.26)]), CAV)
        if g("tank") > 0.5:
            cam.line(PL(FLUSH), shade(CAV, -0.3), 0.12, caps=False)
            cam.line(PL(FLUSH), CAV, 0.09, caps=False)
            cam.poly(PL([(0.47, 1.45), (0.75, 1.45), (0.75, 1.39), (0.47, 1.39)]), CAV)
        rush = g("rush")
        if rush > 0.01:
            kit.flow_line(cam, PL(FLUSH + [(1.08, 1.3), (2.18, 1.3)]), t, WATER, 0.07, speed=1.2, amount=rush)
        rim = max(g("rim"), rush if rush > 0.5 else 0.0)
        if rim > 0.01:
            for wall in (BACK_WALL, FRONT_WALL):
                pts = [(u + (0.03 if wall is BACK_WALL else -0.03), v) for u, v in wall]
                pts = [p for p in pts if p[1] > lvl - 0.01] or pts[-1:]
                if len(pts) >= 2:
                    kit.flow_line(cam, PL(pts, Y + 0.003), t, WATER, 0.04, speed=1.0, amount=rim)
            if g("rim") > 0.5 and self.si == 4:
                kit.label(cam, P(1.25, 1.75), "WATER RUNS DOWN THE WALLS", _ls(cam), (255, 255, 255), BLUE)
        # toilet paper carried off by the siphon
        pp = g("paper")
        if pp > 0.01:
            gone = g("gone")
            full = list(path) + self.drain_pipe[1:]
            for i in range(3):
                if gone < 0.02:
                    c = (1.45 + 0.17 * i, lvl + 0.01)
                else:
                    s = gone * 1.15 - i * 0.12
                    if s >= 1.0:
                        continue
                    p, _ = kit.path_point([(u, 0.0, v) for u, v in full], max(0.0, s))
                    c = (p[0], p[2])
                x, yy = cam.p(*P(c[0], c[1], Y + 0.004))
                r = 0.05 * cam.s
                pts = [(x + r * (0.8 + 0.25 * math.sin(j * 2.3 + i)) * math.cos(j * 0.785),
                        yy + r * 0.6 * (0.8 + 0.25 * math.cos(j * 1.7 + i)) * math.sin(j * 0.785)) for j in range(8)]
                cam.d.polygon(pts, fill=(255, 255, 255), outline=(190, 190, 198))
        bb = g("bubbles")
        if bb > 0.01:
            for i in range(6):
                f = (t * 0.9 + i / 6) % 1.0
                p, _ = kit.path_point([(u, 0.0, v) for u, v in path], f)
                x, yy = cam.p(*P(p[0], p[2], Y + 0.005))
                r = (0.025 + 0.012 * (i % 3)) * cam.s * bb
                cam.d.ellipse((x - r, yy - r, x + r, yy + r), fill=(240, 248, 255), outline=(120, 160, 210),
                              width=max(1, int(0.006 * cam.s)))

    # ------------------------------------------------------------- tank + internals
    def _tank(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("tank"))
        dz = (1 - k) * 0.9
        out = [(u, v + dz) for u, v in TANK_OUT]
        _extrude(cam, out, PORC)
        cam.box(0.0, -0.02, 2.45 + dz, 1.0, Y + 0.04, 0.07, PORC)
        cam.poly(PL(out), CUT, shade(PORC, -0.35), 0.01)
        ix0, ix1, iz0, iz1 = TANK_IN
        cam.poly(PL([(ix0, iz0 + dz), (ix1, iz0 + dz), (ix1, iz1 + dz), (ix0, iz1 + dz)]), CAV, shade(CAV, -0.3), 0.008)
        if k < 0.97:
            return
        lv = TANK_LO + (TANK_HI - TANK_LO) * g("tankw") + (OVER_TOP + 0.025 - TANK_HI) * _sm(g("high"))
        lv = max(iz0, lv)
        if lv > iz0 + 0.01:
            cam.poly(PL([(ix0, iz0), (ix1, iz0), (ix1, lv), (ix0, lv)], Y + 0.001), mix(WATER, (255, 255, 255), 0.18))
            cam.line([P(ix0, lv, Y + 0.002), P(ix1, lv, Y + 0.002)], (215, 236, 255), 0.018, caps=False)
        si = self.si
        yy = Y + 0.003
        # overflow tube (hollow), the flapper hinge sits on it
        ov = _sm(g("over"))
        top = max(1.6, 1.45 + (OVER_TOP - 1.45) * ov)
        cam.poly(PL([(OVER_X - 0.035, 1.42), (OVER_X + 0.035, 1.42), (OVER_X + 0.035, top), (OVER_X - 0.035, top)], yy),
                 (238, 242, 248), (110, 116, 130), 0.008)
        if si == 8:
            kit.label(cam, P(OVER_X + 0.3, OVER_TOP + 0.25), "OVERFLOW TUBE", _ls(cam), (255, 255, 255), RED)
        # flapper on its seat
        a = g("flap") * 1.15
        tip = (HINGE[0] - 0.2 * math.cos(a), HINGE[1] - 0.03 + 0.2 * math.sin(a))
        cam.line([P(0.45, 1.46, yy), P(0.6, 1.46, yy)], (110, 116, 130), 0.025, caps=False)
        if g("flapper") > 0.01 or si >= 3:
            cam.line([P(*tip, yy), P(*HINGE, yy)], (200, 56, 60), 0.06)
        if si == 3:
            kit.label(cam, P(0.4, 1.2), "FLAPPER", _ls(cam), (255, 255, 255), RED)
        # handle outside the tank front + lever arm inside + chain
        hd = g("handle")
        if g("chain") > 0.01 or si >= 3:
            cam.line([P(0.95, 2.26, yy), P(1.14, 2.26 - 0.1 * hd, yy)], (170, 176, 190), 0.04)
            arm = (0.47, 2.27 + 0.13 * hd)
            cam.line([P(0.9, 2.27, yy), P(*arm, yy)], (150, 156, 170), 0.025)
            n = 10
            dist = math.dist(arm, tip)
            sag = max(0.0, 0.62 - dist) * 0.5
            pts = [P(arm[0] + (tip[0] - arm[0]) * i / n + sag * math.sin(math.pi * i / n),
                     arm[1] + (tip[1] - arm[1]) * i / n, yy) for i in range(n + 1)]
            cam.line(pts, (110, 116, 130), 0.01, caps=False)
            if si == 3 and hd > 0.3:
                kit.label(cam, P(1.25, 2.5), "HANDLE", _ls(cam), (255, 255, 255), INK)
        # fill valve + float + supply line from the wall
        fv = _sm(g("fillv"))
        sup = g("supply")
        supply = [(-0.5, 0.5), (-0.3, 0.5), (0.1, 0.5), (FILL_X, 0.66), (FILL_X, 1.38)]
        if fv > 0.01:
            cam.line(PL(supply, yy), (150, 156, 170), 0.045)
            cam.box(-0.36, Y - 0.06, 0.44, 0.1, 0.1, 0.12, (190, 196, 206))
            if sup > 0.01:
                kit.flow_line(cam, PL(supply + [(FILL_X, 2.12)], yy + 0.001), t, WATER, 0.028, speed=1.0, amount=sup)
            cam.line([P(FILL_X, 1.45, yy), P(FILL_X, 1.45 + 0.7 * fv, yy)], (100, 106, 120), 0.05)
            cam.poly(PL([(FILL_X - 0.06, 2.12), (FILL_X + 0.06, 2.12), (FILL_X + 0.06, 2.22), (FILL_X - 0.06, 2.22)], yy),
                     (80, 86, 100))
            if sup > 0.01:
                cam.line([P(FILL_X - 0.08, 2.12, yy), P(FILL_X - 0.09, max(lv, iz0) + 0.01, yy)], WATER, 0.03 * sup)
            fz = min(2.0, max(1.52, lv - 0.04))
            cam.poly(PL([(FILL_X - 0.09, fz - 0.06), (FILL_X + 0.09, fz - 0.06), (FILL_X + 0.09, fz + 0.06),
                         (FILL_X - 0.09, fz + 0.06)], yy + 0.001), (70, 74, 88), (40, 42, 50), 0.006)
            if si == 6:
                kit.label(cam, P(FILL_X - 0.1, 2.62), "FILL VALVE", _ls(cam), (255, 255, 255), INK)
                kit.label(cam, P(-0.2, fz), "FLOAT", _ls(cam), (255, 255, 255), (70, 74, 88))
                kit.label(cam, P(FILL_X + 0.35, 2.45), "OPEN" if sup > 0.5 else "SHUT", _ls(cam), (255, 255, 255),
                          GREEN if sup > 0.5 else RED)
        # refill tube: valve head -> into the top of the overflow tube -> down into the bowl
        rf = _sm(g("refill"))
        if rf > 0.01:
            hose = [(FILL_X + 0.06, 2.2), (0.42, 2.33), (OVER_X, 2.33), (OVER_X, OVER_TOP + 0.02)]
            cam.line(kit.path_prefix(PL(hose, yy + 0.002), rf), (60, 64, 76), 0.022)
            if si == 7:
                kit.label(cam, P(0.42, 2.62), "REFILL TUBE", _ls(cam), (255, 255, 255), BLUE)
        tu = g("topup")
        sp = g("spill")
        down = [(OVER_X, OVER_TOP), (OVER_X, 1.42), (0.56, 1.36)] + FLUSH[1:] + [(1.08, 1.3)]
        if tu > 0.01 and rf > 0.5:
            kit.flow_line(cam, PL([(FILL_X + 0.06, 2.2), (0.42, 2.33), (OVER_X, 2.33)] + down, yy + 0.004), t, WATER,
                          0.02, speed=1.0, amount=tu)
        if sp > 0.01:
            cam.line([P(OVER_X - 0.12, lv, yy + 0.004), P(OVER_X - 0.03, OVER_TOP, yy + 0.004)], WATER, 0.03 * sp)
            kit.flow_line(cam, PL(down, yy + 0.004), t, WATER, 0.04, speed=1.3, amount=sp)

    def _bucket(self, cam, tr, t):
        b = tr.get("bucket", t)
        if b <= 0.01:
            return
        k = _sm(b)
        pr = _sm(tr.get("pour", t))
        a = -1.15 * pr                                    # tilt towards -x (over the bowl)
        d = (math.sin(a), 0.0, math.cos(a))
        e1 = (math.cos(a), 0.0, -math.sin(a))
        base = (1.95, Y * 0.5, 1.75 + (1 - k) * 0.6)
        hgt, r0, r1 = 0.42 * k, 0.2 * k, 0.27 * k

        def ring(c, r, n=24):
            return [(c[0] + r * math.cos(q) * e1[0], c[1] + r * math.sin(q), c[2] + r * math.cos(q) * e1[2])
                    for q in [2 * math.pi * i / n for i in range(n)]]
        top_c = (base[0] + d[0] * hgt, base[1], base[2] + d[2] * hgt)
        bot, topr = ring(base, r0), ring(top_c, r1)
        pts = sorted(cam.p(*p) for p in bot + topr)
        hull = []
        for half in (pts, pts[::-1]):
            h = []
            for p in half:
                while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                    h.pop()
                h.append(p)
            hull += h[:-1]
        cam.d.polygon(hull, fill=(110, 150, 210), outline=(50, 70, 110))
        cam.poly(topr, (60, 90, 140), (40, 60, 100), 0.01)
        if pr < 0.6:
            cam.poly(ring(top_c, r1 * 0.9), WATER)
        hp = [(top_c[0] + r1 * e1[0] * math.cos(q) + d[0] * 0.25 * math.sin(q), top_c[1],
               top_c[2] + r1 * e1[2] * math.cos(q) + d[2] * 0.25 * math.sin(q)) for q in [math.pi * i / 10 for i in range(11)]]
        cam.line(hp, (70, 76, 90), 0.015, caps=False)
        if pr > 0.4:
            lip = (top_c[0] - r1 * e1[0], top_c[1], top_c[2] - r1 * e1[2])
            stream = []
            for i in range(14):
                s = i / 13
                z = lip[2] - 1.6 * s * s - 0.1 * s
                stream.append((lip[0] - 0.35 * s, lip[1], max(0.66, z)))
                if z < 0.66:
                    break
            kit.flow_line(cam, stream, t, WATER, 0.08, speed=2.0, amount=min(1.0, (pr - 0.4) * 2.5))

    def _smell(self, cam, tr, t):
        st = tr.get("stink", t)
        if st <= 0.01:
            return
        bend = _sm(tr.get("bend", t))
        route = list(self.drain_pipe[::-1]) + list(self.path[::-1])
        blocked = bend > 0.5 and self.lvl > L0 - 0.05
        if blocked:                                   # the gas stops at the water plug in the trap
            cut = []
            for p in route:
                cut.append(p)
                if p[1] > 0.6 and p[0] < 0.75:
                    break
            route = cut
        else:
            route = route + [(1.5, 1.2), (1.6, 1.9), (1.7, 2.6)]
        q = [(u, Y + 0.006, v) for u, v in route]
        for i in range(4):
            f = (t * 0.35 + i / 4) % 1.0
            seg = kit.sub_path(q, max(0.0, f - 0.12), f, 6)
            seg = [(x + 0.03 * math.sin(t * 6 + j + i), y, z) for j, (x, y, z) in enumerate(seg)]
            cam.line(seg, mix(STINK, (255, 255, 255), 0.25), 0.035 * st, caps=False)
        if blocked and self.si in (1, 7):
            end = route[-1]
            kit.label(cam, P(end[0] - 0.25, end[1] + 0.05), "BLOCKED", _ls(cam), (255, 255, 255), GREEN)


VIDEO = dict(
    slug="toilet",
    title="How does a toilet flush without flooding the bathroom?",
    steps=STEPS, scene=ToiletScene, initial=INITIAL, tracker=dict(label="FIXES"),
)
