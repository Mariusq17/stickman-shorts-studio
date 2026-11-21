"""How does GPS know where you are? - GPS built step by step: satellites shouting the time, delay = distance,
circles on the map, trilateration, atomic clocks, the 4th satellite for the clock, relativity, ground control."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE, PURPLE = (240, 140, 40), (150, 100, 230)

PH = (0.6, 0.8, 0.0)                       # the phone on the map
SATS = [(-3.2, -1.0, 5.5), (3.0, -2.6, 6.0), (-1.6, 3.6, 5.8), (3.4, 2.6, 6.4)]
SCOL = [ORANGE, BLUE, GREEN, PURPLE]
STATION = (-3.4, 2.2, 0.0)

WIDE = ((0.3, 0.3, 3.0), 90)
MAP = ((0.4, 0.6, 0.0), 150)
SAT1 = ((-3.2, -1.0, 5.4), 260)

STEPS = [
    dict(text="Did you know your phone never talks to GPS satellites? It only listens. Put one satellite in the sky "
              "shouting the time, and you've got the start of GPS.",
         cam=((-3.2, -1.0, 5.4), 330), pegs="neutral",
         cams=[("w:listens", ((-1.5, 0.0, 3.0), 170), 1.4), ("w:shouting", WIDE, 1.6)],
         do=[("sat1", 0.0, 1, 0.7, "back"), ("spin", 0.0, 1, 3.0, "lin"), ("map", "w:listens", 1, 1.2, "out"),
             ("phone", "w:listens", 1, 0.5, "back"), ("sig1", "w:shouting", 1, 0.4, "out")],
         keys=[("only listens", BLUE), ("one satellite", INK), ("shouting the time", INK)],
         pops=[dict(kind="hook", at=0.0, until="w:listens", text="Your phone NEVER talks to GPS", hi=["never", "talks"])],
         sfx=[("w:satellite", "pop"), ("w:shouting", "whoosh")]),
    dict(text="Each signal says: I'm here, and it's exactly this time. Your phone checks when it arrived. The delay "
              "tells the distance, because the signal moves at the speed of light.",
         cam=((-1.2, 0.0, 3.5), 125), pegs="neutral", pose="think",
         do=[("stamp", "w:here", 1, 0.4, "back"), ("arrive", "w:arrived", 1, 0.4, "out"), ("delay", "w:delay", 1, 0.8, "out")],
         keys=[("I'm here|position + exact time", INK), ("the delay|delay = distance", BLUE), ("speed of light", INK)],
         fix="w:delay",
         pops=[dict(kind="equation", at="w:speed", parts=["distance", "=", "delay", "x", "light speed"],
                    colors=[BLUE, INK, ORANGE, INK, INK], pos="bc", until="end+0.2", step=0.25)],
         sfx=[("w:arrived", "ding")]),
    dict(text="But one distance only puts you somewhere on a giant circle around that satellite.",
         cam=MAP, pegs="worried", pose="shrug",
         do=[("stamp", 0.1, 0, 0.3, "in"), ("delay", 0.1, 0, 0.4, "in"), ("ring1", "w:giant", 1, 1.0, "out")],
         keys=[("one distance", INK), ("giant circle|you're somewhere here", RED)],
         pops=[dict(kind="warn", at="w:circle", text="where exactly?", pos="tr", until="end+0.2")],
         sfx=[("w:circle", "sting")]),
    dict(text="So add a second satellite. Two circles only cross in two places.",
         cam=((0.3, 0.2, 1.8), 120), pegs="neutral",
         do=[("sat2", "w:second", 1, 0.6, "back"), ("sig2", "w:second+0.4", 1, 0.4, "out"), ("ring2", "w:circles", 1, 0.9, "out"),
             ("cross", "w:cross", 1, 0.4, "back")],
         keys=[("second satellite", INK), ("two places|2 possible spots", RED)],
         fix="w:second",
         sfx=[("w:second", "pop"), ("w:cross", "tick")]),
    dict(text="A third satellite picks the right one. That's trilateration.",
         cam=MAP, pegs="happy",
         do=[("sat3", "w:third", 1, 0.6, "back"), ("sig3", "w:third+0.4", 1, 0.4, "out"), ("ring3", "w:picks", 1, 0.8, "out"),
             ("cross", "w:trilateration", 0, 0.3, "in"), ("found", "w:trilateration", 1, 0.4, "back")],
         keys=[("third satellite", INK), ("trilateration", INK)],
         fix="w:trilateration",
         pops=[dict(kind="stamp", at="w:trilateration+0.3", text="FOUND YOU", color=GREEN, pos="tr", dur=2.0)],
         sfx=[("w:third", "pop"), ("w:trilateration", "ding")]),
    dict(text="But light is fast. Thirty centimeters every billionth of a second. Your phone's clock is a cheap "
              "crystal, and being off by just one millionth of a second puts you three hundred meters away.",
         cam=MAP, pegs="shocked",
         do=[("err", "w:millionth", 1, 0.8, "out")],
         keys=[("thirty centimeters|30 cm per nanosecond", INK), ("cheap crystal", RED),
               ("three hundred meters|300 m off!", RED)],
         pops=[dict(kind="count", at="w:three", **{"from": 0, "to": 300}, fmt="{} m", sub="off by 1 microsecond",
                    color=RED, pos="tr", until="end+0.2")],
         sfx=[("w:cheap", "sting"), ("w:three", "sting")]),
    dict(text="So the satellites carry atomic clocks, accurate to a few billionths of a second.",
         cam=((-0.2, 0.2, 5.2), 120), pegs="happy",
         do=[("atomic", "w:atomic", 1, 0.5, "out")],
         keys=[("atomic clocks", INK), ("few billionths|accurate to nanoseconds", BLUE)],
         fix="w:atomic",
         sfx=[("w:atomic", "ding")]),
    dict(text="And a fourth satellite fixes your phone's clock. With four distances, it solves where you are and what "
              "time it is, at once.",
         cam=WIDE, pegs="happy",
         do=[("sat4", "w:fourth", 1, 0.6, "back"), ("sig4", "w:fourth+0.4", 1, 0.4, "out"), ("err", "w:fixes", 0, 1.0, "io"),
             ("solve", "w:solves", 1, 0.4, "out")],
         keys=[("fourth satellite", INK), ("fixes your phone's clock|phone clock fixed", BLUE),
               ("where you are|where + when", BLUE)],
         fix="w:fourth",
         pops=[dict(kind="equation", at="w:four", parts=["4 satellites", "->", "x, y, z", "+", "time"],
                    colors=[INK, INK, BLUE, INK, ORANGE], pos="bc", until="end+0.2", step=0.3)],
         sfx=[("w:fourth", "pop")]),
    dict(text="There's a twist. Up there, gravity is weaker and the satellites are fast, so their clocks drift by "
              "thirty eight microseconds a day. Ignore that, and your map is off by about ten kilometers by tomorrow.",
         cam=WIDE, pegs="shocked",
         do=[("solve", 0.1, 0, 0.3, "in"), ("drift", "w:drift", 1, 0.6, "out"), ("wander", "w:ignore", 1, 2.5, "io")],
         keys=[("gravity is weaker", INK), ("thirty eight microseconds|+38 µs a day", RED),
               ("ten kilometers|10 km off per day", RED)],
         pops=[dict(kind="note", at="w:twist", text="Einstein was right", pos="tl", until="w:fast+0.6")],
         sfx=[("w:drift", "sting"), ("w:ten", "sting")]),
    dict(text="So engineers tune the clocks to tick slightly slow before launch. That's Einstein, in your pocket.",
         cam=((-0.2, 0.2, 5.2), 120), pegs="happy",
         do=[("tune", "w:tune", 1, 0.6, "out"), ("drift", "w:tune", 0, 0.8, "io"), ("wander", "w:tune", 0, 1.4, "io")],
         keys=[("tick slightly slow|clocks pre-tuned", BLUE), ("Einstein, in your pocket|relativity in your pocket", INK)],
         fix="w:tune",
         sfx=[("w:tune", "click"), ("w:einstein", "ding")]),
    dict(text="Satellites also drift in orbit, so ground stations track them and upload fresh orbit data every day.",
         cam=((-1.0, 1.4, 2.6), 115), pegs="neutral",
         do=[("tune", 0.2, 0, 0.3, "in"), ("orbit", "w:drift", 1, 0.8, "io"), ("station", "w:ground", 1, 0.6, "back"),
             ("upload", "w:upload", 1, 0.4, "out"), ("orbit", "w:fresh", 0, 1.0, "io")],
         keys=[("drift in orbit", RED), ("ground stations", INK), ("fresh orbit data|daily orbit update", BLUE)],
         fix="w:ground",
         sfx=[("w:upload", "whoosh")]),
    dict(text="So next time the blue dot finds you in the middle of nowhere with no signal bars, it's just listening "
              "to clocks in space.",
         cam=((0.6, 0.8, 0.5), 230), pegs="happy", pose="point",
         do=[("upload", 0.1, 0, 0.3, "in"), ("bars", "w:signal", 1, 0.3, "out"), ("pulse", "w:listening", 1, 0.4, "out")],
         keys=[("blue dot", BLUE), ("no signal bars|0 bars, still works", INK), ("clocks in space", BLUE)]),
    dict(text="Congratulations, you just built GPS. Now please stop recalculating. Follow for more.",
         cam=WIDE, pegs="happy", pose="cheer", min=8.4,
         do=[("done", "w:built", 1, 0.3, "out")],
         keys=[("built GPS|you built GPS!", BLUE), ("stop recalculating", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:built", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(sat1=0, spin=0, map=0, phone=0, sig1=0, stamp=0, arrive=0, delay=0, ring1=0, sat2=0, sig2=0, ring2=0,
               cross=0, sat3=0, sig3=0, ring3=0, found=0, err=0, atomic=0, sat4=0, sig4=0, solve=0, drift=0,
               wander=0, tune=0, orbit=0, station=0, upload=0, bars=0, pulse=0, done=0)

GROUND = (226, 232, 214)
ROAD = (250, 250, 248)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _ls(cam):
    return max(0.12, 0.033 * cam.img.width / cam.s)


def _r(i):
    s = SATS[i]
    return math.hypot(s[0] - PH[0], s[1] - PH[1])


def _other_cross():
    """Second intersection of the circles of satellites 0 and 1 (the wrong candidate)."""
    (x0, y0, _), (x1, y1, _) = SATS[0], SATS[1]
    r0, r1 = _r(0), _r(1)
    d = math.hypot(x1 - x0, y1 - y0)
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r0 * r0 - a * a))
    mx, my = x0 + a * (x1 - x0) / d, y0 + a * (y1 - y0) / d
    c1 = (mx + h * (y1 - y0) / d, my - h * (x1 - x0) / d)
    c2 = (mx - h * (y1 - y0) / d, my + h * (x1 - x0) / d)
    return c1 if math.hypot(c1[0] - PH[0], c1[1] - PH[1]) > 0.3 else c2


OTHER = _other_cross()


class GpsScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (24, 34, 70), (120, 160, 220), clouds=0)
        import random
        from PIL import ImageDraw
        d = ImageDraw.Draw(self.bg)
        rnd = random.Random(4)
        for _ in range(140):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.55)
            r = rnd.uniform(0.6, 2.0) * W / 1080
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255))

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        if g("map") > 0.01:
            self._map(cam, tr, t)
        self._rings(cam, tr, t)
        if g("station") > 0.01:
            self._station(cam, tr, t)
        self._phone(cam, tr, t)
        self._signals(cam, tr, t)
        for i in range(4):
            k = g("sat%d" % (i + 1))
            if k > 0.01:
                self._sat(cam, tr, t, i, k)
        if g("map") > 0.5:
            expr = tr.peg_expr(t)
            react = max(0.0, 1.0 - tr.since_step(t) / 0.5) if expr == "shocked" else 0.0
            kit.peg(cam, (PH[0] + 0.55, PH[1] + 0.35, 0), PEG_COLORS[0], expr, t, 2.0, (-0.6, -0.8), seed=1,
                    pose=tr.peg_pose(t), react=react, floor=GROUND)

    # ------------------------------------------------------------- map
    def _map(self, cam, tr, t):
        k = _sm(tr.get("map", t))
        R = 5.5 * k
        cam.poly([(-R, -R, 0), (R, -R, 0), (R, R, 0), (-R, R, 0)], GROUND, shade(GROUND, -0.3), 0.02)
        if k < 0.9:
            return
        # river, park, roads, blocks
        cam.poly([(-5.5, 4.2, 0), (-1.0, 4.6, 0), (2.0, 3.9, 0), (5.5, 4.4, 0), (5.5, 5.2, 0), (2.0, 4.6, 0),
                  (-1.0, 5.3, 0), (-5.5, 5.0, 0)], (150, 196, 240))
        cam.poly([(1.8, -1.6, 0), (3.6, -1.6, 0), (3.6, 0.2, 0), (1.8, 0.2, 0)], (176, 214, 150))
        for v in (-3.0, -0.4, 2.2):
            cam.line([(-5.5, v, 0), (5.5, v, 0)], ROAD, 0.16, caps=False)
            cam.line([(v + 0.6, -5.5, 0), (v + 0.6, 4.1, 0)], ROAD, 0.16, caps=False)
        import random
        rnd = random.Random(7)
        for bx in (-4.8, -2.2, 0.8, 3.6):
            for by in (-5.0, -2.4, 0.2):
                if abs(bx - 0.8) < 0.1 and abs(by - 0.2) < 0.1:
                    continue
                if bx > 3 and by < -1:
                    continue
                for j in range(2):
                    h = rnd.uniform(0.2, 0.7)
                    col = rnd.choice([(236, 226, 210), (214, 222, 236), (240, 214, 200)])
                    cam.box(bx + j * 0.9, by + 0.3, 0, 0.7, 1.4, h, col)

    def _rings(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        err = g("err") * (1 - g("solve"))
        for i in range(4):
            k = g("ring%d" % (i + 1)) if i < 3 else g("sat4") * g("solve")
            if k <= 0.01:
                continue
            s = SATS[i]
            r = _r(i) * _sm(k)
            col = SCOL[i]
            cam.poly(cam.disc_pts((s[0], s[1], 0.02), r, "z", 90), None, col, 0.05)
            if err > 0.01 and i < 3:
                cam.poly(cam.disc_pts((s[0], s[1], 0.02), r + 0.55 * err, "z", 90), None, mix(col, (255, 255, 255), 0.5),
                         0.03)
            cam.line([(s[0], s[1], 0.02), (s[0], s[1], s[2])], mix(col, (255, 255, 255), 0.4), 0.012, caps=False)
        cr = g("cross")
        if cr > 0.01:
            for p, lab in ((PH, "?"), ((OTHER[0], OTHER[1], 0), "?")):
                kit.glow_dot(cam, (p[0], p[1], 0.05), 0.12 * cr, RED)
                kit.label(cam, (p[0], p[1], 0.55), lab, _ls(cam) * 1.3, (255, 255, 255), RED)

    def _phone(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        ph = g("phone")
        if ph <= 0.01:
            return
        k = _sm(ph)
        wander = g("wander")
        err = g("err") * (1 - g("solve"))
        dx = 0.55 * err + 2.2 * wander
        dy = -0.3 * err + 1.2 * wander
        fd = g("found")
        # blue location dot (pulsing)
        dot = (PH[0] + dx, PH[1] + dy, 0.03)
        if fd > 0.01 or wander > 0.01 or err > 0.01 or g("pulse") > 0.01 or g("done") > 0.01:
            pr = 0.18 + 0.08 * math.sin(t * 5)
            cam.poly(cam.disc_pts(dot, pr * 1.8, "z", 30), mix((150, 190, 255), GROUND, 0.4))
            cam.poly(cam.disc_pts(dot, pr, "z", 30), BLUE, (255, 255, 255), 0.03)
            if err > 0.3 and wander < 0.1:
                kit.label(cam, (dot[0], dot[1], 0.6), "300 m OFF", _ls(cam), (255, 255, 255), RED)
            if wander > 0.3:
                kit.label(cam, (dot[0], dot[1], 0.6), "10 km OFF", _ls(cam), (255, 255, 255), RED)
                cam.line([(PH[0], PH[1], 0.04), dot], RED, 0.03)
        # the phone itself, held up next to the mascot
        x, y = PH[0] + 0.15, PH[1] + 0.05
        parts.phone(cam, "y", y, x - 0.2 * k, 0.9, 0.4 * k, 0.75 * k, t,
                    lines=[("GPS", (255, 255, 255)), ("listening...", (160, 200, 255))])
        if g("bars") > 0.01:
            kit.label(cam, (x, y, 1.95), "NO SIGNAL  x", _ls(cam), (255, 255, 255), INK)
        if g("arrive") > 0.01 and g("delay") < 0.5 and tr.step_at(t) == 1:
            kit.label(cam, (x, y, 1.95), "ARRIVED 0.067 s LATER", _ls(cam), (255, 255, 255), ORANGE)

    def _signals(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        for i in range(4):
            k = g("sig%d" % (i + 1))
            if k <= 0.01:
                continue
            s = SATS[i]
            tgt = (PH[0] + 0.15, PH[1] + 0.05, 1.4)
            pts = [(s[0], s[1], s[2] - 0.3), tgt]
            n = 3
            for j in range(n):
                f = (t * 0.45 + j / n + i * 0.17) % 1.0
                kit.packet(cam, pts, f, SCOL[i], r=0.09 * k, trail=0.15)
            if g("pulse") > 0.01 or (i == 0 and g("delay") > 0.01):
                cam.line(pts, mix(SCOL[i], (255, 255, 255), 0.5), 0.015, caps=False)
        if g("delay") > 0.01:
            s = SATS[0]
            m = ((s[0] + PH[0]) / 2, (s[1] + PH[1]) / 2, (s[2] + 1.4) / 2)
            kit.label(cam, m, "20,000 km", _ls(cam) * 1.1, (255, 255, 255), ORANGE)

    def _sat(self, cam, tr, t, i, k):
        g = lambda kk: tr.get(kk, t)
        x, y, z = SATS[i]
        ob = g("orbit")
        if i == 1 and ob > 0.01:
            x, y, z = x + 0.5 * ob, y - 0.3 * ob, z + 0.2 * ob
        s = 0.55 * _sm(k)
        z += (1 - _sm(k)) * 1.5 + 0.06 * math.sin(t * 1.6 + i)
        # solar panels
        for side in (-1, 1):
            x0 = x + side * s * 0.6
            x1 = x + side * s * 1.9
            cam.poly([(x0, y - s * 0.35, z), (x1, y - s * 0.35, z), (x1, y + s * 0.35, z), (x0, y + s * 0.35, z)],
                     (40, 70, 150), (180, 200, 240), 0.01)
            for q in range(1, 4):
                xx = x0 + (x1 - x0) * q / 4
                cam.line([(xx, y - s * 0.35, z), (xx, y + s * 0.35, z)], (120, 150, 210), 0.006, caps=False)
        cam.box(x - s * 0.5, y - s * 0.5, z - s * 0.5, s, s, s, (230, 200, 90))
        cam.line([(x, y, z - s * 0.5), (x, y, z - s * 0.9)], (200, 204, 214), 0.03)
        cam.poly(cam.disc_pts((x, y, z - s * 0.95), s * 0.3, "z", 16), (220, 224, 232), (120, 126, 140), 0.008)
        col = SCOL[i]
        parts.led(cam, (x + s * 0.5, y, z), col, (t * 2 + i) % 1 < 0.5, 0.05)
        if g("stamp") > 0.01 and i == 0 and tr.step_at(t) == 1:
            kit.label(cam, (x, y, z + 0.9), "I'M HERE  12:00:00.000000", _ls(cam), (255, 255, 255), col)
        if g("atomic") > 0.01 and tr.step_at(t) in (6, 8, 9):
            dr = g("drift") * (1 - g("tune"))
            txt = "ATOMIC CLOCK" if dr < 0.3 else "+38 µs / day"
            if g("tune") > 0.3:
                txt = "TUNED SLOW"
            kit.label(cam, (x, y, z + 0.8), txt, _ls(cam), (255, 255, 255),
                      RED if dr >= 0.3 else (GREEN if g("tune") > 0.3 else INK))
        if i == 0 and g("map") < 0.6:
            kit.rings(cam, (x, y, z - s * 1.0), "z", 0.15, 1.4, t, col, n=3, speed=0.9, width=0.03,
                      bg=(70, 100, 160))
        if i == 0 and k > 0.5 and g("map") < 0.5:
            kit.label(cam, (x, y, z + 0.8), "GPS SATELLITE", _ls(cam), (255, 255, 255), col)
        if g("upload") > 0.01:
            pts = [(STATION[0], STATION[1], 0.9), (x, y, z - 0.3)]
            for j in range(2):
                f = (t * 0.6 + j / 2 + i * 0.13) % 1.0
                kit.packet(cam, pts, f, (255, 230, 120), r=0.07 * g("upload"), trail=0.12)

    def _station(self, cam, tr, t):
        k = _sm(tr.get("station", t))
        x, y, _ = STATION
        cam.box(x - 0.4, y - 0.4, 0, 0.8, 0.8, 0.45 * k, (236, 236, 240))
        cam.line([(x, y, 0.45 * k), (x, y, 0.75 * k)], (150, 156, 170), 0.05)
        c = (x, y, 0.85 * k)
        cam.poly(cam.disc_pts(c, 0.42 * k, "y", 24), (246, 246, 250), (150, 156, 170), 0.012)
        cam.line([c, (x + 0.15, y + 0.2, 1.15 * k)], (150, 156, 170), 0.02)
        if k > 0.8:
            kit.label(cam, (x, y, 1.6), "GROUND STATION", _ls(cam), (255, 255, 255), INK)


VIDEO = dict(
    slug="gps",
    title="How does GPS know where you are?",
    steps=STEPS, scene=GpsScene, initial=INITIAL, tracker=dict(label="FIXES"),
)
