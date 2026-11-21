"""How does an airbag inflate faster than you blink? - an airbag system built step by step in a cut-away
car: folded bag, gas generator, crash sensor, airbag computer, igniter, tear seam, vents, pretensioner,
seat occupancy sensor."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

HUB = (2.05, 0.75, 1.12)             # steering wheel centre (wheel faces -x, towards the driver)
SENSOR = (1.55, 0.95, 0.42)
ACU = (1.75, 0.95, 0.42)
SEAT = (0.55, 0.45, 0.35)            # driver seat min corner
CAR_BODY = (214, 60, 66)

WIDE = ((1.7, 0.8, 0.9), 175)
WHEEL = ((1.85, 0.75, 1.1), 360)
FLOOR = ((1.6, 0.95, 0.5), 330)

STEPS = [
    dict(text="Your airbag is a tiny explosion. Fold a nylon bag into the steering wheel, add something that makes "
              "gas really fast, and you've got the simplest airbag.",
         cam=WHEEL, pegs="shocked",
         cams=[("w:fold", ((1.8, 0.75, 1.05), 300), 1.0), ("w:simplest", WIDE, 1.4)],
         do=[("bag", 0.05, 1, 0.12, "out"), ("flash", 0.05, 1, 0.05, "lin"), ("flash", 0.3, 0, 0.4, "in"),
             ("bag", "w:fold", 0, 0.7, "io"), ("folded", "w:fold", 1, 0.5, "out"), ("gen", "w:gas", 1, 0.5, "back"),
             ("car", "w:simplest", 1, 1.2, "out")],
         keys=[("tiny explosion", RED), ("nylon bag", INK), ("makes gas really fast|gas generator", INK),
               ("simplest airbag", BLUE)],
         pops=[dict(kind="hook", at=0.0, until="w:fold", text="Your airbag is a tiny EXPLOSION", hi=["explosion"])],
         sfx=[(0.05, "slap"), ("w:gas", "pop"), ("w:simplest", "whoosh")]),
    dict(text="But it has to fire at exactly the right moment. So a crash sensor feels how fast the car is slowing "
              "down. That's an accelerometer.",
         cam=FLOOR, pegs="neutral", pose="think",
         do=[("drive", 0.0, 1, 1.0, "out"), ("sensor", "w:sensor", 1, 0.5, "back"), ("needle", "w:slowing", 1, 0.8, "io"),
             ("needle", "w:accelerometer", 0, 0.8, "io")],
         keys=[("right moment", INK), ("crash sensor", INK), ("slowing down", INK), ("accelerometer", INK)],
         fix="w:accelerometer",
         pops=[dict(kind="graph", at="w:feels", title="SLOWING DOWN", track="needle", window=4.0, color=ORANGE,
                    pos="tr", until="end+0.2")],
         sfx=[("w:sensor", "pop")]),
    dict(text="A pothole jolts the car too, so a little computer checks if it's a real crash, in just a few "
              "thousandths of a second.",
         cam=WIDE, pegs="worried",
         do=[("bump", "w:pothole", 1, 0.25, "out"), ("bump", "w:jolts", 0, 0.4, "in"), ("acu", "w:computer", 1, 0.5, "back"),
             ("verdict", "w:checks", 1, 0.3, "out")],
         keys=[("pothole", RED), ("little computer|airbag computer", INK), ("real crash|real crash?", INK),
               ("few thousandths|in milliseconds", BLUE)],
         fix="w:computer",
         pops=[dict(kind="check", at="w:real", text="pothole: no fire", pos="tr", until="end+0.2")],
         sfx=[("w:pothole", "thud"), ("w:computer", "click")]),
    dict(text="In a real crash, it fires an igniter. A pellet of chemicals burns and turns into a huge puff of "
              "nitrogen gas.",
         cam=WIDE, pegs="shocked",
         cams=[("w:igniter", WHEEL, 0.8)],
         do=[("verdict", 0.1, 0, 0.2, "in"), ("wall", 0.0, 1, 0.9, "in"), ("crash", 0.9, 1, 0.15, "out"),
             ("drive", 0.9, 0, 0.15, "out"), ("signal", "w:fires", 1, 0.4, "out"), ("ignite", "w:igniter", 1, 0.2, "out"),
             ("burn", "w:burns", 1, 0.5, "out"), ("gas", "w:nitrogen", 1, 0.5, "out")],
         keys=[("real crash", RED), ("igniter", INK), ("pellet of chemicals", INK), ("nitrogen gas", BLUE)],
         fix="w:igniter",
         pops=[dict(kind="stamp", at=0.95, text="CRASH!", color=RED, pos="tl", dur=1.2)],
         sfx=[(0.9, "slap"), ("w:igniter", "click"), ("w:burns", "rumble")]),
    dict(text="The bag rips through a seam in the cover and fills in about thirty milliseconds, several times faster "
              "than a blink.",
         cam=WHEEL, pegs="shocked",
         do=[("seam", "w:rips", 1, 0.15, "out"), ("folded", "w:rips", 0, 0.1, "lin"), ("ignite", "w:rips", 0, 0.2, "in"), ("bag", "w:fills", 1, 0.25, "out"),
             ("gas", "w:fills", 0, 0.4, "in"), ("burn", "w:fills", 0, 0.3, "in")],
         cams=[("w:fills", ((1.6, 0.75, 1.05), 260), 0.8)],
         keys=[("seam in the cover|tear seam", INK), ("thirty milliseconds|~30 ms", BLUE), ("faster than a blink", BLUE)],
         fix="w:seam",
         pops=[dict(kind="bars", at="w:thirty", title="TIME", pos="tr", until="end+0.2",
                    items=[("blink", 1.0, INK), ("airbag", 0.22, RED)])],
         sfx=[("w:rips", "slap")]),
    dict(text="But a rock hard bag would be like hitting a wall. So it has vent holes that let gas out as your head "
              "sinks in.",
         cam=((1.4, 0.75, 1.1), 280), pegs="worried",
         do=[("hard", "w:rock", 1, 0.3, "out"), ("hard", "w:vent", 0, 0.3, "in"), ("lurch", "w:sinks", 1, 1.0, "io"),
             ("vent", "w:vent", 1, 0.4, "out"), ("bag", "w:sinks", 0.75, 1.2, "io")],
         keys=[("like hitting a wall", RED), ("vent holes", INK), ("head sinks in|soft landing", BLUE)],
         fix="w:vent",
         sfx=[("w:wall", "thud"), ("w:vent", "whoosh")]),
    dict(text="That white smoke after a crash? It's mostly powder that keeps the folded bag from sticking.",
         cam=WIDE, pegs="neutral",
         do=[("smoke", "w:smoke", 1, 0.6, "out"), ("vent", "w:powder", 0, 0.4, "in")],
         keys=[("white smoke", INK), ("mostly powder|it's just powder", BLUE)],
         sfx=[("w:smoke", "whoosh")]),
    dict(text="And the bag can't do it alone. The same signal tightens your seatbelt, pulling you back before you fly "
              "forward. That's the pretensioner.",
         cam=((1.0, 0.6, 1.0), 260), pegs="happy",
         do=[("smoke", 0.2, 0, 1.0, "in"), ("bag", 0.2, 0, 0.8, "io"), ("lurch", 0.2, 0, 0.8, "io"),
             ("belt", "w:seatbelt", 1, 0.3, "out"), ("tight", "w:tightens", 1, 0.25, "out"), ("lurch", "w:fly", 0.3, 0.3, "out"),
             ("lurch", "w:forward", 0, 0.5, "io")],
         keys=[("can't do it alone", RED), ("tightens your seatbelt", BLUE), ("pretensioner", INK)],
         fix="w:pretensioner",
         sfx=[("w:tightens", "click")]),
    dict(text="Nobody in the passenger seat? A weight sensor in the seat switches that airbag off, so it isn't wasted.",
         cam=((1.0, 1.2, 0.8), 230), pegs="neutral",
         do=[("pseat", 0.1, 1, 0.6, "back"), ("weight", "w:weight", 1, 0.4, "out"), ("poff", "w:off", 1, 0.3, "out")],
         keys=[("passenger seat", INK), ("weight sensor", INK), ("airbag off|PASSENGER AIRBAG OFF", BLUE)],
         fix="w:weight",
         sfx=[("w:off", "click")]),
    dict(text="So next time you see SRS on your steering wheel, it means a sensor, a computer, and a tiny explosion "
              "are watching out for you.",
         cam=((1.95, 0.75, 1.1), 320), pegs="happy",
         do=[("pseat", 0.1, 0, 0.5, "in"), ("weight", 0.1, 0, 0.3, "in"), ("poff", 0.1, 0, 0.3, "in"), ("tight", 0.1, 0, 0.3, "in"),
             ("srs", "w:srs", 1, 0.4, "back"), ("folded", "w:srs", 1, 0.3, "out"), ("seam", "w:srs", 0, 0.3, "in")],
         keys=[("SRS|SRS = airbag inside", INK), ("sensor", INK), ("a computer|sensor + computer", INK),
               ("tiny explosion|+ a tiny explosion", RED)]),
    dict(text="Now you know more about airbags than ninety nine percent of drivers. Still, please don't test it. "
              "Follow for more.",
         cam=WIDE, pegs="happy", pose="cheer", min=8.4,
         do=[("wall", 0.2, 0, 1.0, "io"), ("crash", 0.2, 0, 1.0, "io"), ("drive", 0.4, 1, 1.0, "out"),
             ("done", "w:airbags", 1, 0.3, "out")],
         keys=[("more about airbags|airbag expert", BLUE), ("don't test it", RED)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:airbags", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(bag=0, flash=0, folded=0, gen=0, car=0, drive=0, sensor=0, needle=0, bump=0, acu=0, verdict=0, wall=0,
               crash=0, signal=0, ignite=0, burn=0, gas=0, seam=0, hard=0, lurch=0, vent=0, smoke=0, belt=0, tight=0,
               pseat=0, weight=0, poff=0, srs=0, done=0)

ROAD = (90, 96, 110)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _ls(cam):
    return max(0.09, 0.033 * cam.img.width / cam.s)


class AirbagScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (196, 222, 250), (250, 244, 232), clouds=5)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        car = _sm(g("car"))
        dz = 0.06 * math.sin(g("bump") * math.pi) + 0.012 * math.sin(t * 22) * g("drive")
        self.dz = dz
        if car > 0.01:
            self._road(cam, tr, t, car)
            self._car_back(cam, tr, t, car)
        self._driver(cam, tr, t)
        if car > 0.01:
            self._cabin_parts(cam, tr, t, car)
        self._wheel(cam, tr, t)
        self._bag(cam, tr, t)
        if car > 0.01:
            self._car_front(cam, tr, t, car)
            self._wall(cam, tr, t)

    def _wall(self, cam, tr, t):
        w = _sm(tr.get("wall", t))
        if w > 0.01:
            x0 = 3.75 + (1 - w) * 5.0
            cam.box(x0, -0.9, 0, 0.5, 3.4, 1.0, (200, 200, 206))
            for j in range(5):
                kit.plate(cam, "x", x0 - 0.001 + 0.5, -0.9 + j * 0.7, 0.4, -0.9 + j * 0.7 + 0.35, 0.8, (255, 200, 40))

    # ------------------------------------------------------------- road + car shell
    def _road(self, cam, tr, t, k):
        cam.poly([(-4, -1.2, 0), (9, -1.2, 0), (9, 2.8, 0), (-4, 2.8, 0)], ROAD)
        cam.poly([(-4, 2.8, 0), (9, 2.8, 0), (9, 5, 0), (-4, 5, 0)], (170, 200, 140))
        cam.poly([(-4, -3, 0), (9, -3, 0), (9, -1.2, 0), (-4, -1.2, 0)], (170, 200, 140))
        off = (t * 6.0 * tr.get("drive", t)) % 1.6
        for i in range(-3, 9):
            x = i * 1.6 - off
            cam.line([(x, 2.2, 0.002), (x + 0.8, 2.2, 0.002)], (250, 250, 250), 0.06, caps=False)
        sh = ShadowLayer(cam)
        sh.box_on_plane(-0.2, 0.0, 0, 3.9, 1.6, 1.2, "z", 0.0, 200)
        sh.apply(cam.img, 0.3, 2.4)

    def _car_back(self, cam, tr, t, k):
        dz = self.dz
        cr = _sm(tr.get("crash", t))
        nose = 3.7 - 0.35 * cr
        # wheels (far side) + floor pan + far door wall with window
        for x in (0.3, 3.0 - 0.2 * cr):
            cam.wheel((x, -0.02, 0.3), 0.3, 0.2, (40, 40, 46), axis="y", angle=-t * 8 * tr.get("drive", t))
        cam.box(-0.2, 0.0, 0.18 + dz, nose + 0.2, 1.6, 0.14, shade(CAR_BODY, -0.1))
        h = 1.0 * k
        cam.poly([(-0.2, 0.0, 0.32 + dz), (2.6, 0.0, 0.32 + dz), (2.6, 0.0, 0.32 + h + dz), (-0.2, 0.0, 0.32 + h + dz)],
                 shade(CAR_BODY, -0.05), shade(CAR_BODY, -0.4), 0.01)
        if k > 0.9:
            kit.plate(cam, "y", 0.001, 0.2, 0.95 + dz, 2.2, 1.27 + dz, (180, 214, 240), (120, 140, 160))
        # inner floor + carpet
        cam.poly([(-0.2, 0.0, 0.32 + dz), (2.6, 0.0, 0.32 + dz), (2.6, 1.6, 0.32 + dz), (-0.2, 1.6, 0.32 + dz)],
                 (70, 72, 82))

    def _car_front(self, cam, tr, t, k):
        dz = self.dz
        cr = _sm(tr.get("crash", t))
        nose = 3.7 - 0.35 * cr
        # dashboard + hood + windscreen frame + near wheels (the near door is cut away)
        cam.box(2.25, 0.0, 0.32 + dz, 0.5, 1.6, 0.68, (60, 62, 72), top_color=(80, 82, 94))
        hood_h = 0.62 + 0.1 * cr
        cam.box(2.75, 0.0, 0.32 + dz, nose - 2.75, 1.6, 0.3 * k, CAR_BODY)
        if cr > 0.05:
            for i in range(3):
                x = nose - 0.08 - i * 0.12
                cam.line([(x, 1.6, 0.4 + dz), (x - 0.05, 1.6, 0.55 + dz), (x, 1.6, 0.6 + dz)], shade(CAR_BODY, -0.4),
                         0.015)
        top = 0.32 + 1.0 * k + dz
        cam.line([(2.6, 0.0, 1.0 + dz), (2.0, 0.0, top), (-0.1, 0.0, top), (-0.2, 0.0, 0.9 + dz)], shade(CAR_BODY, -0.2),
                 0.06)
        cam.line([(2.6, 1.6, 1.0 + dz), (2.0, 1.6, top), (-0.1, 1.6, top), (-0.2, 1.6, 0.9 + dz)], CAR_BODY, 0.06)
        cam.line([(2.0, 0.0, top), (2.0, 1.6, top)], CAR_BODY, 0.05)
        cam.line([(-0.1, 0.0, top), (-0.1, 1.6, top)], CAR_BODY, 0.05)
        cam.poly([(2.6, 0.0, 1.0 + dz), (2.6, 1.6, 1.0 + dz), (2.0, 1.6, top), (2.0, 0.0, top)], None, (150, 180, 210), 0.01)
        cam.box(-0.2, 1.52, 0.18 + dz, 2.45, 0.08, 0.16, CAR_BODY)              # sill (door cut line)
        for x in (0.3, 3.0 - 0.2 * cr):
            cam.wheel((x, 1.62, 0.3), 0.3, 0.2, (40, 40, 46), axis="y", angle=-t * 8 * tr.get("drive", t))
        if k > 0.9 and tr.step_at(t) == 0:
            kit.label(cam, (1.5, 1.6, 1.75), "CUT-AWAY CAR", _ls(cam), (255, 255, 255), INK)

    def _cabin_parts(self, cam, tr, t, k):
        g = lambda kk: tr.get(kk, t)
        dz = self.dz
        si = tr.step_at(t)
        # crash sensor + airbag computer on the floor tunnel
        s = _sm(g("sensor"))
        if s > 0.01:
            x, y, z = SENSOR
            cam.box(x - 0.08, y - 0.08, z + dz, 0.16 * s, 0.16, 0.06, (40, 120, 70))
            # inner proof mass on springs
            nd = g("needle")
            m = (x + 0.04 * nd, y, z + 0.09 + dz)
            cam.line([(x - 0.07, y, z + 0.09 + dz), m], (200, 200, 210), 0.01)
            kit.glow_dot(cam, m, 0.025 * s, ORANGE)
            if si in (1,):
                kit.label(cam, (x, y, z + 0.32 + dz), "CRASH SENSOR", _ls(cam), (255, 255, 255), GREEN)
        a = _sm(g("acu"))
        if a > 0.01:
            x, y, z = ACU
            cam.box(x - 0.1, y - 0.12, z + dz, 0.2 * a, 0.24, 0.1, (50, 54, 66))
            parts.led(cam, (x + 0.1, y, z + 0.06 + dz), RED if g("crash") > 0.5 else GREEN, True, 0.02)
            if si in (2,):
                kit.label(cam, (x + 0.1, y, z + 0.4 + dz), "AIRBAG COMPUTER", _ls(cam), (255, 255, 255), INK)
        sg = g("signal")
        if sg > 0.01 and si in (3, 7):
            path = [(ACU[0] + 0.1, ACU[1], ACU[2] + 0.1 + dz), (2.25, 0.9, 0.5 + dz), (2.2, 0.85, 0.9 + dz),
                    (HUB[0], HUB[1], HUB[2] + dz)]
            kit.cable(cam, path, (60, 64, 76), 0.02, lit=sg)
            kit.packet(cam, path, (t * 1.5) % 1.0, (255, 210, 60), r=0.04)
        # passenger seat + weight sensor
        ps = _sm(g("pseat"))
        if ps > 0.01:
            self._seat(cam, 0.55, 1.05, dz, (90, 96, 120), ps)
            w = g("weight")
            if w > 0.01:
                kit.plate(cam, "z", 0.62 + dz, 0.6, 1.08, 1.0, 1.48, mix((90, 96, 120), (255, 200, 60), w))
                kit.label(cam, (0.8, 1.3, 0.95 + dz), "WEIGHT: 0 kg", _ls(cam), (255, 255, 255), INK)
            if g("poff") > 0.01:
                kit.label(cam, (2.4, 1.3, 1.25 + dz), "PASSENGER AIRBAG OFF", _ls(cam), (255, 255, 255), BLUE)

    def _seat(self, cam, x, y, dz, col, k):
        cam.box(x, y, 0.32 + dz, 0.5, 0.45, 0.3 * k, col)
        cam.box(x - 0.08, y, 0.32 + dz, 0.12, 0.45, 0.95 * k, shade(col, -0.05))
        cam.box(x - 0.06, y + 0.1, 0.32 + 0.95 * k + dz, 0.08, 0.25, 0.18 * k, shade(col, 0.05))

    def _driver(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        if g("car") < 0.5:
            return
        dz = self.dz
        self._seat(cam, SEAT[0], SEAT[1], dz, (60, 64, 84), 1.0)
        lean = g("lurch")
        expr = tr.peg_expr(t)
        react = max(0.0, 1.0 - tr.since_step(t) / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (SEAT[0] + 0.28 + 0.45 * lean, SEAT[1] + 0.23, 0.62 + dz), PEG_COLORS[0], expr, t, 1.15,
                (0.9, 0.0), seed=1, pose=tr.peg_pose(t), react=react)
        # seatbelt
        b = g("belt")
        tight = g("tight")
        if b > 0.01 or g("car") > 0.9:
            sx = SEAT[0] + 0.3 + 0.45 * lean * (1 - tight)
            pts = [(SEAT[0] - 0.05, SEAT[1] - 0.02, 1.25 + dz), (sx + 0.15 - 0.08 * tight, SEAT[1] + 0.3, 1.0 + dz),
                   (sx + 0.1 - 0.05 * tight, SEAT[1] + 0.45, 0.75 + dz), (SEAT[0] + 0.45, SEAT[1] + 0.47, 0.6 + dz)]
            cam.line(pts, mix((40, 40, 46), (255, 200, 60), tight), 0.035)
            if tight > 0.3 and tr.step_at(t) == 7:
                kit.label(cam, (SEAT[0] - 0.05, SEAT[1], 1.55 + dz), "PRETENSIONER: PULL!", _ls(cam), (255, 255, 255),
                          GREEN)
                kit.glow_dot(cam, (SEAT[0] - 0.05, SEAT[1] - 0.02, 1.25 + dz), 0.05, (255, 200, 60))

    # ------------------------------------------------------------- steering wheel + bag
    def _wheel(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        dz = self.dz if g("car") > 0.01 else 0.0
        c = (HUB[0], HUB[1], HUB[2] + dz)
        # column
        cam.line([(2.45, c[1], 0.85 + dz), c], (50, 52, 60), 0.08)
        rim = cam.disc_pts(c, 0.36, "x", 40)
        cam.poly(rim, None, (40, 42, 50), 0.07)
        for a in (0.0, 2.1, 4.2):
            p = cam.disc_pts(c, 0.34, "x", 1, a + math.pi / 2)[0]
            cam.line([c, p], (60, 62, 72), 0.05)
        # hub cover with the tear seam
        cover = (70, 72, 84)
        seam = g("seam")
        if seam < 0.5:
            cam.poly(cam.disc_pts((c[0] - 0.02, c[1], c[2]), 0.17, "x", 24), cover, (40, 42, 50), 0.01)
            if g("srs") > 0.01:
                cam.text((c[0] - 0.03, c[1], c[2] - 0.04), "SRS", 0.07 * _sm(g("srs")), (230, 230, 236))
                kit.label(cam, (c[0], c[1], c[2] + 0.45), "SUPPLEMENTAL RESTRAINT SYSTEM", _ls(cam), (255, 255, 255),
                          INK)
            cam.line([(c[0] - 0.025, c[1] - 0.14, c[2]), (c[0] - 0.025, c[1] + 0.14, c[2])], shade(cover, -0.3), 0.006,
                     caps=False)
        else:
            for s_ in (-1, 1):
                cam.poly([(c[0] - 0.02, c[1], c[2] - 0.15), (c[0] - 0.02 - 0.12, c[1] + s_ * 0.2, c[2] - 0.12),
                          (c[0] - 0.02 - 0.12, c[1] + s_ * 0.22, c[2] + 0.14), (c[0] - 0.02, c[1], c[2] + 0.15)], cover,
                         (40, 42, 50), 0.008)
            if tr.step_at(t) == 4:
                kit.label(cam, (c[0], c[1] + 0.4, c[2] + 0.5), "TEAR SEAM", _ls(cam), (255, 255, 255), INK)
        # cut-away module: gas generator + igniter + folded bag (seen while the bag is not out)
        gen = g("gen")
        if gen > 0.01 and g("bag") < 0.3:
            x = c[0] + 0.12
            cam.box(x - 0.06, c[1] - 0.11, c[2] - 0.11, 0.12, 0.22, 0.22 * _sm(gen), (150, 156, 170))
            bn = g("burn")
            if g("ignite") > 0.01:
                kit.glow_dot(cam, (x, c[1], c[2]), 0.05 * g("ignite"), (255, 230, 120))
            if bn > 0.01:
                for i in range(8):
                    a = i * 0.785 + t * 6
                    kit.glow_dot(cam, (x - 0.05, c[1] + 0.1 * math.cos(a) * bn, c[2] + 0.1 * math.sin(a) * bn), 0.03,
                                 (255, 140 + 40 * (i % 2), 40))
            si = tr.step_at(t)
            if si == 0 and gen > 0.5:
                kit.label(cam, (x, c[1] - 0.3, c[2] + 0.4), "GAS GENERATOR", _ls(cam), (255, 255, 255), ORANGE)
            if si == 3 and g("ignite") > 0.5:
                kit.label(cam, (x, c[1] - 0.3, c[2] + 0.4), "IGNITER", _ls(cam), (255, 255, 255), RED)
        if g("folded") > 0.01 and g("bag") < 0.3 and g("srs") < 0.01:
            for i in range(4):
                z = c[2] - 0.09 + i * 0.06
                cam.line([(c[0] - 0.05, c[1] - 0.1, z), (c[0] - 0.05, c[1] + 0.1, z)], (240, 240, 244), 0.03 * g("folded"),
                         caps=False)
            if tr.step_at(t) == 0:
                kit.label(cam, (c[0] - 0.1, c[1] + 0.35, c[2] - 0.35), "FOLDED NYLON BAG", _ls(cam), (255, 255, 255), BLUE)
        gs = g("gas")
        if gs > 0.01:
            for i in range(10):
                f = (t * 1.4 + i / 10) % 1.0
                a = i * 2.4
                p = (c[0] - 0.1 - f * 0.5, c[1] + 0.25 * f * math.cos(a), c[2] + 0.25 * f * math.sin(a))
                kit.glow_dot(cam, p, 0.03 * gs * (1 - f * 0.5), (180, 220, 255))
            if tr.step_at(t) == 3:
                kit.label(cam, (c[0] - 0.4, c[1] + 0.3, c[2] + 0.45), "N2 GAS", _ls(cam), (255, 255, 255), BLUE)

    def _bag(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        b = g("bag")
        fl = g("flash")
        dz = self.dz if g("car") > 0.01 else 0.0
        c = (HUB[0] - 0.04, HUB[1], HUB[2] + dz)
        if fl > 0.01:
            x, y = cam.p(*c)
            r = 0.7 * cam.s * fl
            cam.d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 200))
            for i in range(10):
                a = i * 0.628
                cam.d.line((x, y, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5), fill=(255, 200, 80),
                           width=max(2, int(0.03 * cam.s)))
        if b <= 0.01:
            return
        k = min(1.0, b)
        L = 0.55 * k                      # depth towards the driver (-x)
        R = 0.42 * k
        squash = 1.0 - 0.25 * g("lurch")
        hard = g("hard")
        col = mix((248, 248, 250), (255, 210, 210), hard)
        n = 7
        for i in range(n + 1):
            f = i / n
            r = R * math.sqrt(max(0.0, 1 - (2 * f - 1) ** 2)) * (1.05 if i else 0.9)
            r = max(r, 0.1 * k)
            p = (c[0] - L * f * squash, c[1], c[2] + 0.03 * f)
            cam.poly(cam.disc_pts(p, r, "x", 30), mix(col, (205, 210, 222), 0.4 - 0.4 * f), shade(col, -0.25), 0.006)
        # seams on the front face
        p = (c[0] - L * squash, c[1], c[2] + 0.03)
        cam.poly(cam.disc_pts(p, R * 0.45, "x", 24), None, (210, 214, 224), 0.008)
        if hard > 0.3:
            kit.label(cam, (p[0], p[1], p[2] + R + 0.2), "ROCK HARD", _ls(cam), (255, 255, 255), RED)
        v = g("vent")
        if v > 0.01:
            for s_ in (-1, 1):
                base = (c[0] - 0.15, c[1] + s_ * R * 0.9, c[2] + 0.1)
                for i in range(3):
                    f = (t * 1.3 + i / 3) % 1.0
                    q = (base[0] + 0.1 * f, base[1] + s_ * 0.5 * f, base[2] + 0.25 * f)
                    x, y = cam.p(*q)
                    r = (0.04 + 0.08 * f) * cam.s * v
                    cam.d.ellipse((x - r, y - r, x + r, y + r), fill=mix((235, 240, 248), (255, 255, 255), f))
            if tr.step_at(t) == 5:
                kit.label(cam, (c[0] - 0.1, c[1] + R + 0.2, c[2] + 0.45), "VENT HOLES", _ls(cam), (255, 255, 255), BLUE)
        sm = g("smoke")
        if sm > 0.01:
            for i in range(9):
                f = (t * 0.25 + i / 9) % 1.0
                q = (c[0] - 0.6 + 0.3 * math.cos(i * 2.1), c[1] + 0.5 * math.sin(i * 1.7), c[2] + 0.1 + f * 0.8)
                x, y = cam.p(*q)
                r = (0.12 + 0.18 * f) * cam.s * sm
                cam.d.ellipse((x - r, y - r, x + r, y + r), fill=mix((245, 245, 248), (255, 255, 255), f))
            if tr.step_at(t) == 6:
                kit.label(cam, (c[0] - 0.5, c[1], c[2] + 1.1), "CORNSTARCH / TALC", _ls(cam), INK, (255, 255, 255))


VIDEO = dict(
    slug="airbag",
    title="How does an airbag inflate faster than you blink?",
    steps=STEPS, scene=AirbagScene, initial=INITIAL, tracker=dict(label="FIXES"),
)
