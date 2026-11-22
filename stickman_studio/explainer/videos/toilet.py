"""How does a toilet flush without flooding the bathroom? - built step by step (idea #13, open loop).

Side cutaway: the toilet is cut in half along its middle (plane y = 0), so the tank internals, the bowl and the
S-shaped trapway are visible like a diagram; water is translucent. The hook asks about the gurgle at the end of
every flush; the answer (the siphon breaking) comes near the end.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer
from ..lib.story import open_loop
from ..qa import shift_spec

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)
WATER = (70, 150, 230)
CERAMIC = (246, 248, 252)
SECTION = (214, 222, 232)          # cut face of the ceramic
CAVITY = (188, 198, 212)           # inside of the back half
PIPE = (150, 156, 170)
FLANGE = (120, 126, 140)           # floor flange under the outlet (QA end object)
SEWER = (110, 96, 84)              # sewer box below the floor (QA end object)
ROOFCAP = (96, 100, 112)           # vent cap on the roof (QA end object)
CUP = (236, 120, 70)               # the cup used in the "pour slowly" step (QA object)

WIDE = ((0.9, 0.2, 1.0), 175)
TANK = ((0.33, 0.0, 1.3), 330)
TRAP = ((0.8, 0.0, 0.45), 330)
DRAIN = ((0.4, -0.2, 0.0), 210)
ROOF = ((-0.1, -0.2, 3.3), 210)
ISO_P = 35.264

Y0, Y1 = -0.42, 0.0               # back half of the toilet: y from Y0 to the cut plane Y1
TANK_X0, TANK_X1, TANK_Z0, TANK_Z1 = 0.05, 0.62, 0.85, 1.75
TZ_EMPTY, TZ_FULL = 0.9, 1.52     # water surface in the tank: empty / full
OVER_TOP = 1.6                    # top of the overflow tube
REST = 0.58                       # bowl water at rest = height of the weir in the trapway
STACK_X, STACK_Y = -0.12, -0.08   # soil / vent stack, in the section plane

# trapway: straight drop (no trap) and the S-bend (same number of points so they can morph)
STRAIGHT = [(1.06, 0.3), (1.06, 0.25), (1.06, 0.2), (1.06, 0.15), (1.06, 0.1), (1.06, 0.06), (1.06, 0.03), (1.06, 0.0)]
SBEND = [(1.06, 0.3), (0.92, 0.24), (0.8, 0.34), (0.74, 0.6), (0.64, 0.62), (0.55, 0.48), (0.48, 0.2), (0.45, 0.0)]

STEPS = [
    dict(text="If you put a tank of water above a bowl, with a pipe out the bottom, you've got the world's simplest "
              "toilet.",
         cam=((0.35, 0.0, 1.3), 330), pegs="neutral",
         cams=[("w:bowl", ((0.9, 0.0, 0.6), 260), 1.1), ("w:simplest", WIDE, 1.4)],
         do=[("tank", 0.0, 1, 0.7, "back"), ("tank_w", "w:water", 1.0, 1.0, "out"), ("bowl", "w:bowl", 1, 0.8, "back"),
             ("pipe", "w:pipe", 1, 0.6, "out"), ("room", "w:simplest", 1, 1.2, "out")],
         keys=[("tank of water", INK), ("bowl", INK), ("pipe out the bottom", INK), ("simplest toilet", BLUE)],
         sfx=[("w:tank", "pop"), ("w:bowl", "pop"), ("w:simplest", "whoosh")]),
    dict(text="But that pipe runs straight to the sewer, and the sewer stinks. A lot.",
         cam=((0.9, 0.0, 0.4), 230), pegs="shocked", pose="cover",
         do=[("smell", "w:sewer", 1, 0.8, "out")],
         keys=[("straight to the sewer", RED), ("stinks|stinks!", RED)],
         pops=[dict(kind="meter", at="w:stinks", text="SMELL", **{"from": 0.0, "to": 1.0}, color=RED, fmt="MAX",
                    anim=1.0, pos="tr", until="end+0.2")],
         sfx=[("w:stinks", "sting")]),
    dict(text="So you bend the pipe into an S. Some water always stays stuck in the bend and blocks the smell. That's "
              "the trap seal.",
         cam=TRAP, pegs="happy",
         do=[("sbend", "w:bend", 1, 1.3, "io"), ("seal", "w:water", 1, 0.8, "out"), ("smell", "w:blocks", 0, 0.6, "in"),
             ("cam_yaw", "w:bend", 14.0, 1.7, "smooth"), ("cam_pitch", "w:bend", 18.0, 1.7, "smooth")],
         keys=[("bend the pipe", INK), ("stays stuck", INK), ("blocks the smell", BLUE), ("trap seal", INK)],
         fix="w:bend", sfx=[("w:bend", "slap"), ("w:trap", "ding")]),
    dict(text="Now pour in a cup of water, and it just dribbles over the bend. The bowl barely empties.",
         cam=((0.9, 0.0, 0.7), 260), pegs="worried",
         do=[("cup", "w:cup", 1, 0.5, "back"), ("pour", "w:pour", 1, 0.3, "out"), ("dribble", "w:dribbles", 1, 0.3, "out"),
             ("pour", "end-1.0", 0, 0.3, "in"), ("cup", "end-0.9", 0, 0.7, "in"), ("dribble", "end-0.4", 0, 0.3, "in")],
         keys=[("cup of water", INK), ("dribbles over", RED), ("barely empties", RED)]),
    dict(text="So you dump the whole tank in at once. The bend fills completely, and the falling water drags "
              "everything behind it, like sucking through a straw. That's a siphon.",
         cam=TRAP, pegs="happy",
         do=[("rim", "w:dump", 1, 0.2, "out"), ("tank_w", "w:dump", 0.0, 1.6, "in"), ("bowl_lvl", "w:dump", 0.74, 1.2, "out"),
             ("rim", "w:fills", 0, 0.3, "in"), ("siphon", "w:fills", 1, 0.3, "out"), ("bowl_lvl", "w:drags", 0.3, 2.2, "io"),
             ("siphon", "w:siphon", 0, 0.6, "in")],
         keys=[("whole tank", INK), ("fills completely", INK), ("sucking through a straw", INK), ("siphon", BLUE)],
         pops=[dict(kind="graph", at="w:dump", title="WATER IN THE BOWL", track="bowl_lvl", window=6.0, color=BLUE, ymax=0.8,
                    pos="tr", until="end")],
         fix="w:siphon", sfx=[("w:dump", "whoosh"), ("w:siphon", "ding")]),
    dict(text="But you can't lift a heavy tank and tip it over every time. You need a plug that opens fast.",
         cam=WIDE, pegs="worried", pose="shrug", cams=[("w:plug", ((0.3, 0.0, 0.95), 300), 1.2)],
         do=[("cam_yaw", 0.0, 45.0, 1.6, "smooth"), ("cam_pitch", 0.0, ISO_P, 1.6, "smooth"),
             ("tank_w", 0.3, 1.0, 1.4, "io"), ("bowl_lvl", 0.3, REST, 1.4, "io")],
         keys=[("heavy tank", RED), ("plug that opens fast", RED)]),
    dict(text="So the handle pulls a chain, and the chain lifts a rubber plug at the bottom of the tank. That's the "
              "flapper. It stays open until the tank is empty, then drops back down.",
         cam=TANK, pegs="happy",
         cams=[("w:empty", WIDE, 1.3)],
         do=[("handle", "w:handle", 1, 0.4, "out"), ("flap", "w:lifts", 1, 0.5, "out"), ("rim", "w:lifts", 1, 0.2, "out"),
             ("tank_w", "w:lifts", 0.0, 2.6, "in"), ("bowl_lvl", "w:lifts", 0.74, 1.4, "out"), ("handle", "w:flapper", 0, 0.4, "io"),
             ("siphon", "w:empty", 1, 0.3, "out"), ("bowl_lvl", "w:empty", 0.3, 1.8, "io"), ("flap", "w:drops", 0, 0.4, "in"),
             ("rim", "w:drops", 0, 0.3, "in"), ("siphon", "end-0.3", 0, 0.3, "in")],
         keys=[("handle pulls a chain", INK), ("rubber plug", INK), ("flapper", BLUE), ("drops back down", INK)],
         fix="w:flapper", sfx=[("w:handle", "slap"), ("w:lifts", "whoosh"), ("w:drops", "pop")]),
    dict(text="Now the tank is empty. Something has to fill it back up, and know when to stop.",
         cam=TANK, pegs="worried", cams=[("w:something", ((0.33, 0.0, 1.05), 420), 1.2), ("w:stop", ((0.4, 0.0, 1.3), 300), 1.0)],
         pops=[dict(kind="warn", at="w:empty", text="empty tank", pos="tr", until="end")],
         keys=[("tank is empty", RED), ("when to stop", RED)]),
    dict(text="So a float rides on the water. When the level drops, the float drops and opens a valve. As the water "
              "rises, the float rises and shuts it off. That's the fill valve.",
         cam=TANK, pegs="happy",
         cams=[("w:rises", ((0.35, 0.0, 1.35), 280), 1.2)],
         do=[("fill", "w:opens", 1, 0.2, "out"), ("tank_w", "w:rises", 1.0, 3.0, "io"), ("fill", "w:shuts", 0, 0.3, "in")],
         keys=[("rides on the water|float", INK), ("opens a valve", INK), ("shuts it off", INK), ("fill valve", BLUE)],
         pops=[dict(kind="graph", at="w:level", title="WATER IN THE TANK", track="tank_w", window=7.0, color=BLUE,
                    pos="tr", until="end")],
         fix="w:fill", sfx=[("w:opens", "pop"), ("w:shuts", "ding")]),
    dict(text="But if that valve ever gets stuck open, the tank overflows onto your bathroom floor.",
         cam=WIDE, pegs="shocked",
         do=[("fill", "w:stuck", 1, 0.2, "out"), ("tank_w", "w:stuck", 1.16, 1.6, "lin"), ("spillout", "w:overflows", 1, 0.3, "out"),
             ("flood", "w:overflows", 1, 1.6, "out")],
         keys=[("stuck open", RED), ("bathroom floor|flooded floor!", RED)],
         pops=[dict(kind="warn", at="w:overflows", text="flood!", pos="bl", until="end+0.2")],
         sfx=[("w:overflows", "sting")]),
    dict(text="So a tall tube stands inside the tank. Extra water spills into it and drains into the bowl instead. "
              "That's the overflow tube.",
         cam=TANK, pegs="happy",
         do=[("flood", 0.0, 0, 0.8, "in"), ("spillout", 0.0, 0, 0.3, "in"), ("tank_w", 0.1, 1.1, 0.6, "io"),
             ("tube", "w:tall", 1, 0.6, "back"), ("over", "w:spills", 1, 0.3, "out"), ("over", "end-0.4", 0, 0.3, "in"),
             ("fill", "end-0.4", 0, 0.2, "in"), ("tank_w", "end-0.4", 1.0, 0.4, "io")],
         keys=[("tall tube", INK), ("spills into it", INK), ("overflow tube", BLUE)],
         fix="w:overflow", sfx=[("w:spills", "pop")]),
    dict(text="A thin hose also tops up the bowl, so the trap seal is back before you even leave.",
         cam=((0.6, 0.0, 0.9), 230), pegs="happy",
         do=[("hose", "w:hose", 1, 0.5, "out"), ("refill", "w:tops", 1, 0.2, "out"), ("bowl_lvl", 0.0, 0.3, 0.01, "lin"),
             ("bowl_lvl", "w:tops", REST, 2.0, "io"), ("refill", "end-0.3", 0, 0.3, "in")],
         keys=[("thin hose", INK), ("trap seal is back", BLUE)],
         fix="w:hose", sfx=[("w:hose", "pop")]),
    dict(text="But a big rush of water down the drain needs air behind it, or it can suck the water right out of the "
              "traps.",
         cam=DRAIN, pegs="worried", cams=[("w:air", ((0.6, -0.1, 0.3), 260), 1.2)],
         do=[("drainflow", "w:rush", 1, 0.3, "out"), ("suck", "w:suck", 1, 1.0, "io"), ("drainflow", "end-0.3", 0, 0.3, "in")],
         keys=[("big rush of water", INK), ("needs air", RED), ("out of the traps", RED)],
         pops=[dict(kind="meter", at="w:suck", text="TRAP WATER", **{"from": 1.0, "to": 0.2}, color=RED, fmt="LOW",
                    anim=1.2, pos="tr", until="end+0.2")]),
    dict(text="So a vent pipe runs up through your roof and lets air in. Yes, your toilet breathes through the roof.",
         cam=((-0.1, -0.2, 1.8), 170), pegs="happy",
         cams=[("w:roof", ROOF, 1.6), ("w:yes", ((0.2, -0.1, 2.0), 150), 1.6)],
         do=[("suck", 0.0, 0, 0.8, "io"), ("vent", "w:vent", 1, 1.5, "out"), ("air", "w:air", 1, 0.5, "out")],
         keys=[("vent pipe", INK), ("through your roof", INK), ("breathes through the roof", BLUE)],
         fix="w:vent", sfx=[("w:vent", "whoosh"), ("w:air", "pop")]),
    dict(text="When the bowl is almost empty, air sneaks into the bend and breaks the siphon. That's the gurgle.",
         cam=TRAP, pegs="shocked",
         do=[("air", 0.0, 0, 0.4, "in"), ("cam_yaw", 0.0, 14.0, 1.6, "smooth"), ("cam_pitch", 0.0, 18.0, 1.6, "smooth"),
             ("bowl_lvl", 0.2, 0.74, 0.8, "out"), ("siphon", 0.6, 1, 0.3, "out"), ("bowl_lvl", 1.0, 0.36, "w:sneaks", "io"),
             ("gurgle", "w:sneaks", 1, 0.3, "out"), ("siphon", "w:breaks", 0, 0.3, "in"), ("gurgle", "end-0.2", 0, 0.2, "in")],
         keys=[("almost empty", INK), ("air sneaks", INK), ("breaks the siphon", RED), ("gurgle|GURGLE!", BLUE)],
         pops=[dict(kind="stamp", at="w:gurgle", text="GURGLE", color=BLUE, pos="mr", until="end+0.2")],
         sfx=[("w:breaks", "boing")]),
    dict(text="So next time you hear that gurgle, you'll know the siphon just let go, and the water in the bend is "
              "already blocking the smell again.",
         cam=WIDE, pegs="happy", cams=[("w:siphon", TRAP, 1.4), ("w:blocking", WIDE, 1.4)],
         do=[("cam_yaw", 0.0, 45.0, 1.6, "smooth"), ("cam_pitch", 0.0, ISO_P, 1.6, "smooth"),
             ("bowl_lvl", 0.3, REST, 2.0, "io"), ("refill", 0.3, 1, 0.2, "out"), ("refill", "end-0.5", 0, 0.3, "in")],
         keys=[("siphon just let go", INK), ("blocking the smell", BLUE)]),
    dict(text="And that's how you build a toilet. Follow for more.", cam=WIDE, pegs="happy", pose="cheer",
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(room=0, tank=0, tank_w=0.0, bowl=0, pipe=0, sbend=0, smell=0, seal=0, cup=0, pour=0, dribble=0, rim=0,
               bowl_lvl=0.3, siphon=0, handle=0, flap=0, fill=0, spillout=0, flood=0, tube=0, over=0, hose=0, refill=0,
               drainflow=0, suck=0, vent=0, air=0, gurgle=0)

# Scene QA - ORIGINAL step indices (VIDEO uses shift_spec(QA, 1) after open_loop inserts the hook)
QA = dict(
    objects={"cup": dict(color=CUP, steps="3", grace=1.5)},
    links=[
        dict(name="drain toilet->sewer", steps="1-16", width_min=0.05, tol=0.1,
             ends=[dict(color=FLANGE), dict(color=SEWER)]),
        dict(name="vent drain->roof", steps="13-16", width_min=0.05, tol=0.1, settle=2.5,
             ends=[dict(color=FLANGE), dict(color=ROOFCAP)]),
    ],
)

STEPS = open_loop(
    STEPS, "Every flush ends with the same gurgle, and that sound is the whole trick.", answer_step=14,
    teaser_frac=0.62, reminder=(6, "Remember that gurgle? Hold that thought."), reveal="Here's the answer.",
    hook_hl=["gurgle", "trick"], hook_cam=TRAP,
    hook_bursts=[dict(at="w:gurgle", glyph="?!", color=(40, 110, 235), xy=(0.78, 0.30))],
    ending_text="And that's how you build a toilet. Follow for more. Because remember,",
    ending_bursts=[dict(at="w:build", glyph="check", color=(40, 160, 90), xy=(0.78, 0.30))],
    ending_cam=TRAP, ending_do=[])


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _lerp_path(a, b, k):
    return [(p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k) for p, q in zip(a, b)]


def _clip_below(poly, zl):
    """Part of an (x, z) polygon below the level z = zl (Sutherland-Hodgman, one half-plane)."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina, inb = a[1] <= zl, b[1] <= zl
        if ina:
            out.append(a)
        if ina != inb:
            k = (zl - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * k, zl))
    return out


def _xz(pts, y=Y1):
    return [(x, y, z) for x, z in pts]


# outer silhouette of the toilet body (x, z) and the inner bowl cavity
BODY = [(0.3, 0.0), (1.1, 0.0), (1.14, 0.22), (1.05, 0.42), (1.48, 0.58), (1.6, 0.74), (1.58, 0.84), (0.6, 0.84),
        (0.52, 0.8), (0.3, 0.8)]
BOWL_IN = [(0.66, 0.79), (1.52, 0.79), (1.44, 0.62), (1.2, 0.46), (1.1, 0.33), (0.98, 0.3), (0.84, 0.5), (0.72, 0.66)]


class ToiletScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (214, 230, 246), (246, 242, 236), clouds=4)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        self._step = step_i
        self._water = []                        # translucent water polygons, composited once at the end
        room = g("room")
        if room > 0.01:
            self._room(cam, tr, t, room)
        if g("pipe") > 0.01:
            self._drain(cam, tr, t)
        if g("bowl") > 0.01:
            self._body(cam, tr, t)
        if g("tank") > 0.01:
            self._tank(cam, tr, t)
        self._composite_water(cam)
        if g("bowl") > 0.5:
            self._effects(cam, tr, t)
        if room > 0.5:
            self._peg(cam, tr, t)

    # ------------------------------------------------------------- room + pipes in the wall / under the floor
    def _room(self, cam, tr, t, room):
        """Dollhouse section: the whole room is cut at the plane y = 0 (same cut as the toilet), so the floor shows
        its cut face and the pipes inside it are seen in that face - nothing floats over the floor."""
        k = _sm(room)
        h = 3.2 * k
        cam.box(-0.3, -1.3, -1.45, 3.6, 1.3, 1.45, (176, 168, 158), top_color=(236, 232, 226))   # floor block, cut at y=0
        for i in range(1, 9):                       # floor tiles
            x = -0.3 + i * 0.4
            cam.line([(x, -1.3, 0.002), (x, 0.0, 0.002)], (222, 216, 208), 0.006, caps=False)
        cam.line([(-0.3, 0.0, -0.02), (3.3, 0.0, -0.02)], (150, 142, 132), 0.03, caps=False)   # floor screed line
        cam.poly([(-0.3, -1.3, 0), (-0.3, 0.0, 0), (-0.3, 0.0, h), (-0.3, -1.3, h)], (226, 234, 240), (190, 200, 210), 0.01)
        cam.poly([(-0.3, -1.3, 0), (3.3, -1.3, 0), (3.3, -1.3, h), (-0.3, -1.3, h)], (236, 240, 244), (190, 200, 210), 0.01)
        for i in range(1, 6):                       # wall tiles
            z = i * 0.3
            cam.line([(-0.299, -1.3, z), (-0.299, 0.0, z)], (210, 220, 228), 0.006, caps=False)
            cam.line([(-0.3, -1.299, z), (3.3, -1.299, z)], (220, 226, 232), 0.006, caps=False)
        sh = ShadowLayer(cam)
        sh.ao_edge((-0.3, -1.3, 0), (3.3, -1.3, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
        sh.ao_edge((-0.3, -1.3, 0), (-0.3, 0.0, 0), (1, 0, 0), (0, 0, 1), 0.3, 140)
        sh.box_on_plane(0.3, Y0, 0, 1.3, -Y0, 0.84, "z", 0.0, 150)
        sh.apply(cam.img, 0.26, 2.2)
        if k > 0.9 and self._step == 0:
            kit.label(cam, (1.0, 0.0, -0.7), "UNDER THE FLOOR", 0.12, INK, (255, 255, 255))

    def _outlet(self, tr, t):
        k = _sm(tr.get("sbend", t))
        x = 1.06 + (0.45 - 1.06) * k
        return x

    def _drain(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        ox = self._outlet(tr, t)
        kp = _sm(g("pipe"))
        # flange under the outlet + drain pipe running to the stack, stack down to the sewer
        cam.box(ox - 0.1, -0.16, -0.06, 0.2, 0.16, 0.06, FLANGE)
        route = [(ox, -0.08, -0.04), (ox, -0.08, -0.55), (STACK_X, STACK_Y, -0.55)]
        down = [(STACK_X, STACK_Y, -0.55), (STACK_X, STACK_Y, -0.95)]
        parts.pipe(cam, route, 0.07 * kp, PIPE)
        parts.pipe(cam, down, 0.08 * kp, PIPE)
        cam.box(STACK_X - 0.2, -0.16, -1.25, 0.4, 0.16, 0.3, SEWER)
        if kp > 0.9 and self._step in (0, 1):
            kit.label(cam, (STACK_X + 0.5, STACK_Y, -1.1), "TO THE SEWER", 0.12, (255, 255, 255), (130, 100, 70))
        fl = g("drainflow") + g("siphon")
        if fl > 0.05:
            for j in range(4):
                s = (t * 0.9 + j / 4) % 1.0
                kit.packet(cam, route + down[1:], s, WATER, 0.05)
        v = g("vent")
        if v > 0.01:                                 # the stack continues up inside the wall and out of the roof
            top = -0.55 + (3.75 + 0.55) * _sm(v)
            parts.pipe(cam, [(STACK_X, STACK_Y, -0.55), (STACK_X, STACK_Y, top)], 0.08, PIPE)
            if v > 0.97:
                cam.box(-0.5, -1.3, 3.2, 1.2, 1.4, 0.12, (170, 110, 90))      # piece of the roof
                cam.box(STACK_X - 0.12, STACK_Y - 0.12, 3.75, 0.24, 0.24, 0.1, ROOFCAP)
                if self._step in (13, 14):
                    kit.label(cam, (STACK_X, STACK_Y + 0.2, 4.1), "VENT PIPE", 0.14, (255, 255, 255), GREEN)
            a = g("air")
            if a > 0.05:
                for j in range(3):
                    s = (t * 0.5 + j / 3) % 1.0
                    kit.packet(cam, [(STACK_X, STACK_Y, 3.9), (STACK_X, STACK_Y, -0.5)], s, (200, 230, 255), 0.05)

    # ------------------------------------------------------------- toilet body (back half + cut face)
    def _body(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("bowl"))
        body = [(x, z * k) for x, z in BODY]
        # back half: back face, visible sides (normals towards +x / +z), then the cut face
        cam.poly(_xz(body, Y0), shade(CERAMIC, -0.12))
        n = len(body)
        for i in range(n):
            a, b = body[i], body[(i + 1) % n]
            nx, nz = (b[1] - a[1]), -(b[0] - a[0])       # outward normal for a counter-clockwise outline
            if nx + nz < 0:
                continue
            cam.poly([(a[0], Y0, a[1]), (b[0], Y0, b[1]), (b[0], Y1, b[1]), (a[0], Y1, a[1])],
                     shade(CERAMIC, -0.05 if nz > abs(nx) else -0.16), shade(CERAMIC, -0.3), 0.006)
        cam.poly(_xz(body), SECTION, shade(SECTION, -0.3), 0.008)
        if k < 0.95:
            return
        cam.poly(_xz(BOWL_IN), CAVITY, shade(CAVITY, -0.25), 0.008)
        # the trapway (straight drop morphing into the S-bend)
        path = _lerp_path(STRAIGHT, SBEND, _sm(g("sbend")))
        cam.line(_xz(path), CAVITY, 0.15)
        # rim channel from the tank outlet
        cam.line(_xz([(0.3, 0.84), (0.42, 0.8), (1.42, 0.8)]), CAVITY, 0.05)
        # water in the bowl (below the level) + in the trap
        lvl = g("bowl_lvl")
        if g("suck") > 0.01:
            lvl -= 0.2 * g("suck")
        wpoly = _clip_below(BOWL_IN, lvl)
        if len(wpoly) >= 3:
            self._water.append(_xz(wpoly, Y1 + 0.001))
        seal = g("seal") * _sm(g("sbend"))
        sip = g("siphon")
        if seal > 0.01 or sip > 0.01:
            pts = []
            for (x, z) in path:
                if sip > 0.5 or z <= min(lvl, REST) + 0.01 or x > 0.74:
                    pts.append((x, Y1 + 0.001, z))
            if len(pts) >= 2:
                self._water.append(("line", pts, 0.12))
        if g("rim") > 0.05:                             # water rushing along the rim channel and down the bowl
            for j in range(5):
                s = (t * 1.3 + j / 5) % 1.0
                kit.packet(cam, _xz([(0.3, 0.84), (0.42, 0.8), (1.42, 0.8)], Y1 + 0.01), s, WATER, 0.035)
            for xx in (0.8, 1.05, 1.3):
                f = (t * 2.2 + xx) % 1.0
                cam.line([(xx, Y1 + 0.01, 0.78), (xx - 0.03, Y1 + 0.01, 0.78 - 0.25 * f)], WATER, 0.02)
        if sip > 0.05:                                  # flow through the bend
            for j in range(6):
                s = (t * 1.1 + j / 6) % 1.0
                kit.packet(cam, _xz(path, Y1 + 0.01), s, (40, 110, 220), 0.045)
            if self._step in (4, 14):
                kit.label(cam, (0.7, 0.2, 0.85), "SIPHON", 0.13, (255, 255, 255), BLUE)
        if seal > 0.9 and self._step in (2, 11):
            kit.label(cam, (0.75, 0.2, 0.15), "TRAP SEAL", 0.13, (255, 255, 255), GREEN)
        if k > 0.95 and self._step == 0:
            kit.label(cam, (1.1, 0.2, 0.95), "BOWL", 0.12, INK, (255, 255, 255))

    # ------------------------------------------------------------- tank + its internals
    def _tank(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("tank"))
        x0, x1, z0, z1 = TANK_X0, TANK_X1, TANK_Z0, TANK_Z0 + (TANK_Z1 - TANK_Z0) * k
        cam.box(x0, Y0, z0, x1 - x0, Y1 - Y0 - 0.001, z1 - z0, CERAMIC, faces="tr")
        cam.poly([(x0, Y1, z0), (x1, Y1, z0), (x1, Y1, z1), (x0, Y1, z1)], SECTION, shade(SECTION, -0.3), 0.008)
        cam.poly([(x0 + 0.05, Y1, z0 + 0.05), (x1 - 0.05, Y1, z0 + 0.05), (x1 - 0.05, Y1, z1 - 0.03),
                  (x0 + 0.05, Y1, z1 - 0.03)], CAVITY)
        if k < 0.95:
            return
        cam.box(x0 - 0.03, Y0, z1, x1 - x0 + 0.06, Y1 - Y0, 0.06, CERAMIC)                         # lid
        tz = TZ_EMPTY + (TZ_FULL - TZ_EMPTY) * g("tank_w")
        yi = Y1 - 0.18                                   # internals stand in the middle of the tank
        # flapper on the outlet hole
        fa = g("flap") * 1.0
        hx, hz = 0.18, z0 + 0.07
        tip = (hx + 0.26 * math.cos(fa), yi, hz + 0.26 * math.sin(fa))
        cam.line([(hx, yi, hz), tip], (170, 40, 50), 0.05)
        # handle + lever + chain
        ha = g("handle") * 0.5
        piv = (x1 - 0.06, yi, z1 - 0.12)
        lev = (piv[0] - 0.32 * math.cos(ha), yi, piv[2] + 0.32 * math.sin(ha))
        cam.line([piv, lev], (150, 156, 168), 0.03)
        cam.box(x1, yi - 0.05, z1 - 0.16, 0.1 * (1 + ha), 0.1, 0.06, (190, 196, 206))
        cam.line([lev, tip], (110, 116, 128), 0.012)
        # overflow tube (+ water spilling in) and fill valve with its float cup
        cam.line([(0.13, yi, z0 + 0.06), (0.13, yi, OVER_TOP)], (120, 170, 120), 0.045)
        cam.line([(0.48, yi, z0 + 0.06), (0.48, yi, 1.5)], (130, 136, 150), 0.04)
        fz = max(z0 + 0.15, tz - 0.06)
        cam.box(0.43, yi - 0.05, fz, 0.1, 0.1, 0.1, (90, 96, 110))
        if g("fill") > 0.3:
            for j in range(3):
                f = (t * 3 + j / 3) % 1.0
                cam.line([(0.48, yi + 0.02, 1.5), (0.48 + 0.08 * f, yi + 0.02, 1.5 - 0.5 * f)], WATER, 0.02)
        if g("hose") > 0.01:
            hp = [(0.48, yi, 1.5), (0.4, yi, 1.62), (0.2, yi, 1.66), (0.14, yi, OVER_TOP + 0.02)]
            if g("hose") > 0.03:
                cam.line(kit.sub_path(hp, 0, _sm(g("hose"))), (40, 40, 48), 0.018)
            if g("refill") > 0.3:
                for j in range(3):
                    kit.packet(cam, hp + [(0.13, yi, z0)], (t * 0.9 + j / 3) % 1.0, WATER, 0.03)
        if g("over") > 0.3:
            for j in range(3):
                kit.packet(cam, [(0.13, yi + 0.02, OVER_TOP + 0.02), (0.13, yi + 0.02, z0)], (t * 1.2 + j / 3) % 1.0, WATER, 0.035)
        # water in the tank (translucent) + spilling over the top when the valve is stuck
        if tz > TZ_EMPTY + 0.005:
            self._water.append([(x0 + 0.05, Y1 + 0.001, z0 + 0.05), (x1 - 0.05, Y1 + 0.001, z0 + 0.05),
                                (x1 - 0.05, Y1 + 0.001, min(tz, z1 - 0.03)), (x0 + 0.05, Y1 + 0.001, min(tz, z1 - 0.03))])
        if g("spillout") > 0.2:
            for j in range(3):
                kit.packet(cam, [(x1, Y1, z1 - 0.05), (x1 + 0.15, -0.3, 0.6), (x1 + 0.3, -0.6, 0.02)],
                           (t * 1.0 + j / 3) % 1.0, WATER, 0.04)
        labels = {6: ("FLAPPER", (0.25, yi + 0.3, z0 + 0.35)), 8: ("FLOAT", (0.48, yi + 0.3, fz + 0.3)),
                  10: ("OVERFLOW TUBE", (0.13, yi + 0.3, OVER_TOP + 0.2)), 11: ("REFILL HOSE", (0.3, yi + 0.3, 1.85))}
        if self._step in labels and (self._step != 10 or g("tube") > 0.5):
            txt, xyz = labels[self._step]
            kit.label(cam, xyz, txt, 0.1, (255, 255, 255), BLUE)

    # ------------------------------------------------------------- water, smell, cup, puddle, gurgle
    def _composite_water(self, cam):
        if not self._water:
            return
        m = Image.new("L", cam.img.size, 0)
        d = ImageDraw.Draw(m)
        for w in self._water:
            if isinstance(w, tuple) and w and w[0] == "line":
                _, pts, width = w
                d.line([cam.p(*q) for q in pts], fill=150, width=max(2, int(width * cam.s)), joint="curve")
            else:
                d.polygon([cam.p(*q) for q in w], fill=140)
        cam.img.paste(WATER, (0, 0, cam.img.width, cam.img.height), m)

    def _effects(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        sm = g("smell")
        if sm > 0.02:                                   # green stink rising from the open pipe
            ox = self._outlet(tr, t)
            for j in range(4):
                f = (t * 0.4 + j / 4) % 1.0
                pts = [(1.0 + 0.08 * math.sin(i * 0.9 + t * 3 + j), 0.1 + 0.05 * j, 0.45 + f * 0.9 + i * 0.06) for i in range(8)]
                cam.line(pts, mix((120, 200, 90), (255, 255, 255), f), 0.03 * sm, caps=False)
        cu = g("cup")
        if cu > 0.01:                                   # a cup pouring slowly (slides in from the right)
            cx = 1.35 + 1.4 * (1 - _sm(cu))
            cam.box(cx - 0.08, -0.08, 1.1, 0.16, 0.16, 0.22, CUP)
            if g("pour") > 0.3:
                cam.line([(cx - 0.08, 0.0, 1.25), (cx - 0.12, 0.0, 0.62)], WATER, 0.025)
        if g("dribble") > 0.3:                          # a few drops creeping over the weir
            path = _lerp_path(STRAIGHT, SBEND, _sm(g("sbend")))
            s = 0.55 + 0.45 * ((t * 0.25) % 1.0)
            kit.packet(cam, _xz(path, Y1 + 0.01), s, WATER, 0.03)
        fl = g("flood")
        if fl > 0.01:                                   # puddle spreading on the floor
            px, py = cam.p(TANK_X1 + 0.7, -0.6, 0.005)
            r = 0.7 * _sm(fl) * cam.s
            cam.d.ellipse((px - r, py - r * 0.5, px + r, py + r * 0.5), fill=(150, 196, 236), outline=(100, 160, 220),
                          width=max(1, int(0.01 * cam.s)))
        gu = g("gurgle")
        if gu > 0.05:                                   # air bubbles breaking into the bend
            for j in range(5):
                f = (t * 1.6 + j / 5) % 1.0
                x, z = 0.74 - 0.05 * j, 0.62 - 0.3 * f
                px, py = cam.p(x, Y1 + 0.02, z)
                r = (0.02 + 0.015 * (j % 2)) * cam.s
                cam.d.ellipse((px - r, py - r, px + r, py + r), outline=(255, 255, 255), width=max(2, int(0.008 * cam.s)))

    def _peg(self, cam, tr, t):
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (2.2, -0.65, 0.0), PEG_COLORS[1], expr, t, 1.7, (-0.8, 0.2), seed=3, pose=tr.peg_pose(t), react=react)


def overlays(img, tr, t, W, H):
    return None


VIDEO = dict(
    slug="toilet",
    title="How does a toilet flush without flooding the bathroom?",
    steps=STEPS, end_cover=False, scene=ToiletScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"),
    qa=shift_spec(QA, 1),
)
