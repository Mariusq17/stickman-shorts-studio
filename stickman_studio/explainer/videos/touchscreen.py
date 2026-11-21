"""How does your touchscreen know where your finger is? - a capacitive touchscreen built step by step:
see-through electrode grid, mutual capacitance, finger stealing the field, fast scan, blob centre,
multitouch, palm rejection, water, gloves."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE, CYAN, PURPLE = (240, 140, 40), (60, 200, 230), (150, 100, 230)
SKIN = (240, 190, 150)

SX, SY = 2.0, 3.6                 # screen size (x across, y along the phone)
NC, NR = 7, 12                    # columns (along y) and rows (along x)
COLS = [0.2 + i * (SX - 0.4) / (NC - 1) for i in range(NC)]
ROWS = [0.2 + j * (SY - 0.4) / (NR - 1) for j in range(NR)]
T1 = (COLS[3] + 0.12, ROWS[6] - 0.1)          # first touch (between wires on purpose)

WIDE = ((1.0, 1.8, 0.7), 205)
CLOSE = ((T1[0], T1[1], 0.6), 330)

STEPS = [
    dict(text="Your screen can't feel you press. Put a grid of invisible wires over a display, and you've got the "
              "simplest touchscreen.",
         cam=((T1[0], T1[1], 0.3), 380), pegs="neutral",
         cams=[("w:grid", ((1.0, 1.8, 0.6), 260), 1.2), ("w:simplest", WIDE, 1.2)],
         do=[("finger", 0.0, 1, 0.8, "out"), ("phone", 0.0, 1, 0.6, "out"), ("finger", "w:grid", 0, 0.5, "in"),
             ("explode", "w:grid", 1, 1.0, "io"), ("grid", "w:wires", 1, 1.0, "out"), ("desk", "w:simplest", 1, 1.0, "out")],
         keys=[("grid of invisible wires", INK), ("simplest touchscreen", BLUE)],
         pops=[dict(kind="hook", at=0.0, until="w:grid", text="Your screen CAN'T feel you press", hi=["can't", "press"])],
         sfx=[("w:grid", "whoosh"), ("w:simplest", "pop")]),
    dict(text="The wires are made of a see-through metal oxide, so the picture shines right through. Rows on one "
              "layer, columns on another.",
         cam=WIDE, pegs="happy",
         do=[("glowrows", "w:rows", 1, 0.4, "out"), ("glowcols", "w:columns", 1, 0.4, "out"), ("glowrows", "end-0.4", 0, 0.3, "in"),
             ("glowcols", "end-0.4", 0, 0.3, "in")],
         keys=[("see-through metal oxide|transparent metal oxide", INK), ("shines right through", BLUE),
               ("rows", INK), ("columns|rows + columns", INK)],
         fix="w:oxide",
         sfx=[("w:rows", "tick"), ("w:columns", "tick")]),
    dict(text="A chip sends a tiny electric pulse down each row, and every column picks a little of it up where they "
              "cross. That's mutual capacitance.",
         cam=((1.0, 1.8, 0.5), 240), pegs="neutral",
         do=[("chip", "w:chip", 1, 0.5, "back"), ("pulse", "w:pulse", 1, 0.4, "out"), ("couple", "w:cross", 1, 0.5, "out")],
         keys=[("tiny electric pulse", INK), ("where they cross|every crossing", INK), ("mutual capacitance", INK)],
         fix="w:mutual",
         sfx=[("w:pulse", "click")]),
    dict(text="Now your finger. Your body is salty water, so it conducts, and it steals some of that field at the "
              "crossing under it.",
         cam=CLOSE, pegs="happy", pose="point",
         do=[("finger", "w:finger", 1, 0.8, "io"), ("steal", "w:steals", 1, 0.5, "out")],
         keys=[("salty water", INK), ("it conducts", INK), ("steals some of that field|finger steals the field", RED)],
         sfx=[("w:steals", "whoosh")]),
    dict(text="The column hears a weaker signal, and the chip knows exactly which crossing you touched.",
         cam=((1.0, 1.8, 0.5), 240), pegs="happy",
         do=[("heat", "w:weaker", 1, 0.5, "out")],
         keys=[("weaker signal", RED), ("which crossing|touch found", BLUE)],
         fix="w:weaker",
         pops=[dict(kind="bars", at="w:weaker", title="SIGNAL", pos="tr", until="end+0.2",
                    items=[("normal crossing", 1.0, BLUE), ("under your finger", 0.45, RED)])],
         sfx=[("w:knows", "ding")]),
    dict(text="But a slow scan would feel laggy. So the chip checks every crossing over a hundred times a second.",
         cam=WIDE, pegs="neutral",
         do=[("scan", "w:scan", 1, 0.3, "out"), ("fast", "w:checks", 1, 0.6, "out")],
         keys=[("feel laggy", RED), ("over a hundred times|100+ scans/s", BLUE)],
         fix="w:checks",
         pops=[dict(kind="count", at="w:hundred", **{"from": 0, "to": 120}, fmt="{}", sub="scans per second", color=BLUE,
                    pos="tr", until="end+0.2")],
         sfx=[("w:laggy", "sting")]),
    dict(text="Your finger is wider than one crossing, so it dims a few at once. The chip finds the center of that "
              "blob, so it can place your touch between the wires.",
         cam=CLOSE, pegs="happy", pose="think",
         do=[("scan", 0.1, 0, 0.3, "in"), ("fast", 0.1, 0, 0.3, "in"), ("blob", "w:dims", 1, 0.6, "out"),
             ("center", "w:center", 1, 0.5, "back")],
         keys=[("dims a few", INK), ("center of that blob|blob centre", BLUE), ("between the wires", BLUE)],
         fix="w:center",
         sfx=[("w:center", "ding")]),
    dict(text="Two fingers make two blobs. That's multitouch, and it's how you pinch to zoom.",
         cam=WIDE, pegs="happy",
         do=[("center", 0.1, 0, 0.3, "in"), ("finger2", "w:two", 1, 0.6, "io"), ("pinch", "w:pinch", 1, 1.4, "io"),
             ("zoom", "w:pinch", 1, 1.4, "io")],
         keys=[("two blobs", INK), ("multitouch", INK), ("pinch to zoom", BLUE)],
         fix="w:multitouch",
         sfx=[("w:pinch", "whoosh")]),
    dict(text="Your palm resting on the edge makes a huge blob. So anything that big gets ignored. That's palm "
              "rejection.",
         cam=WIDE, pegs="worried",
         do=[("finger2", 0.1, 0, 0.4, "in"), ("pinch", 0.1, 0, 0.3, "in"), ("zoom", 0.1, 0, 0.5, "io"),
             ("palm", "w:palm", 1, 0.6, "out"), ("reject", "w:ignored", 1, 0.4, "out"), ("palm", "end-0.5", 0, 0.4, "in")],
         keys=[("huge blob", RED), ("gets ignored", BLUE), ("palm rejection", INK)],
         fix="w:rejection",
         sfx=[("w:ignored", "click")]),
    dict(text="Water conducts too, so raindrops can fake a touch. That's why wet screens go a little crazy.",
         cam=WIDE, pegs="shocked",
         do=[("reject", 0.1, 0, 0.3, "in"), ("finger", "w:water", 0, 0.5, "in"), ("drops", "w:raindrops", 1, 0.6, "out"),
             ("ghost", "w:fake", 1, 0.3, "out"), ("drops", "end-0.4", 0, 0.3, "in"), ("ghost", "end-0.4", 0, 0.3, "in")],
         keys=[("water conducts too", RED), ("fake a touch|ghost touches", RED)],
         pops=[dict(kind="warn", at="w:fake", text="ghost touches", pos="tr", until="end")],
         sfx=[("w:fake", "sting")]),
    dict(text="And regular gloves block the trick completely, unless they have conductive thread in the fingertips.",
         cam=CLOSE, pegs="neutral",
         do=[("glove", 0.05, 1, 0.01, "lin"), ("finger", "w:gloves", 1, 0.7, "io"), ("tip", "w:conductive", 1, 0.5, "out")],
         keys=[("regular gloves|gloves = no touch", RED), ("conductive thread", BLUE)],
         sfx=[("w:conductive", "ding")]),
    dict(text="So next time your phone ignores your gloved finger, it's not broken. It just can't feel your "
              "electricity.",
         cam=((1.0, 1.8, 0.6), 230), pegs="happy", pose="point",
         do=[("tip", 0.1, 0, 0.3, "in"), ("electric", "w:electricity", 1, 0.4, "out")],
         keys=[("not broken", BLUE), ("feel your electricity", INK)]),
    dict(text="And that's how you build a touchscreen. Please wipe it sometimes. Follow for more.",
         cam=WIDE, pegs="happy", pose="cheer", min=8.4,
         do=[("glove", 0.1, 0, 0.01, "lin"), ("finger", 0.1, 0, 0.4, "in"), ("electric", 0.1, 0, 0.3, "in"),
             ("explode", 0.2, 0, 1.2, "io"), ("done", "w:build", 1, 0.3, "out")],
         keys=[("build a touchscreen|you built a touchscreen!", BLUE), ("wipe it sometimes", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:build", "ding"), ("w:follow", "pop")]),
]

INITIAL = dict(finger=0, phone=0, explode=0, grid=0, desk=0, glowrows=0, glowcols=0, chip=0, pulse=0, couple=0, steal=0,
               heat=0, scan=0, fast=0, blob=0, center=0, finger2=0, pinch=0, zoom=0, palm=0, reject=0, drops=0, ghost=0,
               glove=0, tip=0, electric=0, done=0)

DESK = (196, 160, 120)
BODY = (40, 42, 52)
ZD = 0.14                                    # display surface


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _ls(cam):
    return max(0.1, 0.033 * cam.img.width / cam.s)


class TouchScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (238, 232, 246), (250, 246, 240), clouds=0)

    # touches: list of (x, y, strength, radius, kind)
    def _touches(self, tr, t):
        g = lambda k: tr.get(k, t)
        out = []
        f = g("finger") * (0.0 if g("glove") > 0.5 and g("tip") < 0.5 else 1.0)
        dn = _sm(g("finger"))
        if dn > 0.9 and f > 0.5:
            out.append((self._fpos(tr, t, 0)[0], self._fpos(tr, t, 0)[1], 1.0, 0.32, "finger"))
        if g("finger2") > 0.9:
            p = self._fpos(tr, t, 1)
            out.append((p[0], p[1], 1.0, 0.32, "finger"))
        if g("palm") > 0.5:
            out.append((1.75, 0.9, 1.0, 0.75, "palm"))
        if g("ghost") > 0.5:
            for (x, y) in ((0.6, 2.9), (1.4, 1.6)):
                out.append((x, y, 0.7, 0.22, "ghost"))
        return out

    def _fpos(self, tr, t, i):
        p = tr.get("pinch", t)
        if i == 0:
            f2 = _sm(tr.get("finger2", t))
            return (T1[0] - (0.25 + 0.35 * p) * f2, T1[1] - (0.35 + 0.45 * p) * f2)
        return (T1[0] + 0.25 + 0.35 * p, T1[1] + 0.35 + 0.45 * p)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        if g("desk") > 0.01:
            self._desk(cam, g("desk"))
        ph = _sm(g("phone"))
        if ph > 0.01:
            self._phone(cam, tr, t, ph)
        touches = self._touches(tr, t)
        ex = _sm(g("explode"))
        zg = ZD + 0.02 + 0.45 * ex                 # electrode layer
        if g("grid") > 0.01:
            self._grid(cam, tr, t, zg, touches)
        zc = ZD + 0.04 + 0.9 * ex                  # cover glass
        if ph > 0.5:
            cam.poly([(0, 0, zc), (SX, 0, zc), (SX, SY, zc), (0, SY, zc)], None, (200, 220, 240), 0.012)
            if ex > 0.5 and step_i <= 1:
                kit.label(cam, (SX + 0.1, SY, zc + 0.05), "COVER GLASS", _ls(cam), INK, (255, 255, 255))
                kit.label(cam, (SX + 0.1, SY, zg + 0.05), "WIRE GRID", _ls(cam), (255, 255, 255), CYAN)
                kit.label(cam, (SX + 0.1, SY, ZD + 0.02), "DISPLAY", _ls(cam), (255, 255, 255), INK)
        self._hands(cam, tr, t, zc)
        if g("desk") > 0.5 and cam.s / (cam.img.width / 1080) < 290:
            expr = tr.peg_expr(t)
            react = max(0.0, 1.0 - tr.since_step(t) / 0.5) if expr == "shocked" else 0.0
            kit.peg(cam, (3.4, 2.6, 0), PEG_COLORS[4], expr, t, 1.6, (-0.8, -0.3), seed=4, pose=tr.peg_pose(t),
                    react=react, floor=DESK)

    # ------------------------------------------------------------- scene parts
    def _desk(self, cam, k):
        k = _sm(k)
        R = 3.6 * k
        cam.poly([(1 - R, 1.8 - R * 1.3, 0), (1 + R * 1.2, 1.8 - R * 1.3, 0), (1 + R * 1.2, 1.8 + R, 0),
                  (1 - R, 1.8 + R, 0)], DESK, shade(DESK, -0.3), 0.02)
        if k < 0.9:
            return
        for i in range(8):
            y = -2.5 + i * 0.8
            cam.line([(-2.6, y, 0.001), (5.3, y + 0.15, 0.001)], shade(DESK, -0.06), 0.01, caps=False)
        sh = ShadowLayer(cam)
        sh.box_on_plane(0, 0, 0, SX, SY, 0.14, "z", 0.0, 200)
        sh.apply(cam.img, 0.3, 2.5)
        # a mug for scale
        cam.poly(cam.disc_pts((-1.2, 3.4, 0.0), 0.35, "z", 24), (230, 90, 80))
        cam.box(-1.5, 3.1, 0, 0.6, 0.6, 0.7, (230, 90, 80), top_color=(120, 70, 50))

    def _phone(self, cam, tr, t, k):
        g = lambda kk: tr.get(kk, t)
        cam.box(-0.12, -0.25, 0, SX + 0.24, SY + 0.5, ZD * k, BODY)
        zoom = g("zoom")
        # display: wallpaper + app icons (zoom scales the "map" picture)
        cam.poly([(0, 0, ZD), (SX, 0, ZD), (SX, SY, ZD), (0, SY, ZD)], (70, 110, 190))
        if zoom < 0.05:
            cols = [(255, 120, 90), (90, 200, 120), (255, 200, 70), (120, 150, 255), (240, 100, 180), (80, 200, 220)]
            for j in range(5):
                for i in range(4):
                    x0, y0 = 0.15 + i * 0.47, 0.35 + j * 0.62
                    kit.plate(cam, "z", ZD + 0.002, x0, y0, x0 + 0.32, y0 + 0.32, cols[(i + j * 3) % 6])
        else:
            s = 1 + 1.6 * zoom
            cx, cy = SX / 2, SY / 2
            for j in range(-3, 4):
                for i in range(-3, 4):
                    x0, y0 = cx + (i * 0.6 - 0.25) * s, cy + (j * 0.6 - 0.25) * s
                    x1, y1 = x0 + 0.5 * s, y0 + 0.5 * s
                    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(SX, x1), min(SY, y1)
                    if x1 > x0 and y1 > y0:
                        kit.plate(cam, "z", ZD + 0.002, x0, y0, x1, y1, (226, 232, 214) if (i + j) % 3 else (176, 214, 150))
            kit.plane_text(cam, "z", ZD + 0.004, cx, cy, "MAP", 0.25 * s, (60, 70, 90), max_w=SX * 0.8)
        if g("chip") > 0.01:
            c = _sm(g("chip"))
            cam.box(0.7, SY + 0.02, 0.02, 0.6 * c, 0.2, 0.1, (30, 32, 40))
            for q in range(6):
                cam.line([(0.75 + q * 0.09, SY + 0.02, 0.07), (0.75 + q * 0.09, SY - 0.02, 0.1)], (220, 190, 90), 0.012)
            if tr.step_at(t) in (2, 3, 4, 5):
                kit.label(cam, (2.3, SY + 0.3, 0.45), "CONTROLLER CHIP", _ls(cam), (255, 255, 255), INK)

    def _grid(self, cam, tr, t, zg, touches):
        g = lambda k: tr.get(k, t)
        k = _sm(g("grid"))
        gr, gc = g("glowrows"), g("glowcols")
        rowc = mix((150, 225, 240), (60, 200, 230), gr)
        colc = mix((150, 225, 240), (255, 170, 60), gc)
        for y in ROWS:
            cam.line([(0.05, y, zg), (0.05 + (SX - 0.1) * k, y, zg)], rowc, 0.018 + 0.015 * gr, caps=False)
        for x in COLS:
            cam.line([(x, 0.05, zg + 0.01), (x, 0.05 + (SY - 0.1) * k, zg + 0.01)], colc, 0.018 + 0.015 * gc, caps=False)
        if k < 0.9:
            return
        # wires leaving the edge towards the controller chip
        if g("chip") > 0.01:
            for x in COLS:
                cam.line([(x, SY - 0.05, zg + 0.01), (x, SY + 0.05, zg), (1.0, SY + 0.1, 0.1)], (120, 160, 180), 0.008,
                         caps=False)
        # pulses running along the rows (one row at a time, faster during "scan")
        pu = g("pulse")
        if pu > 0.01:
            rate = 2.0 + 10.0 * g("fast")
            j = int(t * rate) % NR
            f = (t * rate) % 1.0
            y = ROWS[j]
            cam.line([(0.05, y, zg + 0.005), (SX - 0.05, y, zg + 0.005)], (255, 240, 120), 0.04 * pu, caps=False)
            kit.glow_dot(cam, (0.05 + (SX - 0.1) * f, y, zg + 0.01), 0.05 * pu, (255, 220, 80))
            if g("scan") > 0.3:
                kit.label(cam, (SX + 0.3, y, zg + 0.1), "ROW %d" % (j + 1), _ls(cam) * 0.85, (255, 255, 255), ORANGE)
        # field at each crossing, dimmed by touches
        cp = g("couple")
        if cp > 0.01:
            st, ht, bl, rej = g("steal"), g("heat"), g("blob"), g("reject")
            for x in COLS:
                for y in ROWS:
                    drop, kind = 0.0, None
                    for (tx, ty, s, r, kd) in touches:
                        d = math.hypot(x - tx, y - ty)
                        v = s * math.exp(-(d / r) ** 2)
                        if v > drop:
                            drop, kind = v, kd
                    show = max(st, ht, bl)
                    drop *= show
                    if kind == "palm" and rej > 0.5:
                        col = mix((255, 222, 100), (150, 150, 160), min(1, drop * 1.5))
                    elif kind == "ghost":
                        col = mix((255, 222, 100), BLUE, min(1, drop * 1.6))
                    else:
                        col = mix((255, 222, 100), RED, min(1, drop * 1.6))
                    if drop < 0.12:
                        px, py = cam.p(x, y, zg + 0.02)
                        r = 0.028 * cam.s * cp
                        cam.d.ellipse((px - r, py - r, px + r, py + r), fill=col)
                    else:
                        kit.glow_dot(cam, (x, y, zg + 0.02), (0.03 + 0.05 * drop) * cp, col)
        # blob centre between the wires
        ce = g("center")
        if ce > 0.01 or g("finger2") > 0.5:
            for (tx, ty, s, r, kd) in touches:
                if kd != "finger":
                    continue
                c = (tx, ty, zg + 0.03)
                a = max(ce, g("finger2"))
                cam.poly(cam.disc_pts(c, 0.12 * a, "z", 20), None, GREEN, 0.03)
                cam.line([(tx - 0.16 * a, ty, c[2]), (tx + 0.16 * a, ty, c[2])], GREEN, 0.02, caps=False)
                cam.line([(tx, ty - 0.16 * a, c[2]), (tx, ty + 0.16 * a, c[2])], GREEN, 0.02, caps=False)
            if ce > 0.5 and g("finger2") < 0.01:
                kit.label(cam, (T1[0], T1[1], zg + 0.9), "TOUCH  x=412  y=1083", _ls(cam), (255, 255, 255), GREEN)
        if g("reject") > 0.5 and g("palm") > 0.1:
            kit.label(cam, (1.75, 0.9, zg + 0.9), "TOO BIG: IGNORED", _ls(cam), (255, 255, 255), INK)

    def _hands(self, cam, tr, t, zc):
        g = lambda k: tr.get(k, t)
        glove = g("glove") > 0.5
        for i, key in ((0, "finger"), (1, "finger2")):
            k = _sm(g(key))
            if k <= 0.01:
                continue
            fx, fy = self._fpos(tr, t, i)
            lift = (1 - k) * 2.2
            tip = (fx, fy, zc + 0.12 + lift)
            base = (fx + 0.9, fy + 1.0, zc + 1.9 + lift)
            col = (130, 90, 200) if glove else SKIN
            cam.line([base, tip], shade(col, -0.35), 0.34)
            cam.line([base, tip], col, 0.28)
            # knuckle crease + nail
            m = tuple(tip[q] + (base[q] - tip[q]) * 0.4 for q in range(3))
            cam.line([(m[0] - 0.1, m[1] + 0.08, m[2]), (m[0] + 0.08, m[1] - 0.1, m[2])], shade(col, -0.2), 0.02)
            if not glove:
                n = tuple(tip[q] + (base[q] - tip[q]) * 0.12 for q in range(3))
                cam.poly(cam.disc_pts((n[0], n[1], n[2] + 0.1), 0.08, "z", 14), (250, 220, 210), shade(SKIN, -0.3), 0.008)
            elif g("tip") > 0.01:
                cam.poly(cam.disc_pts((tip[0], tip[1], tip[2] + 0.02), 0.14, "z", 16), mix(col, (200, 200, 210), g("tip")),
                         (90, 90, 100), 0.01)
                kit.label(cam, (tip[0], tip[1], tip[2] + 0.9), "CONDUCTIVE TIP", _ls(cam), (255, 255, 255), GREEN)
            if glove and g("tip") < 0.5 and k > 0.9 and tr.step_at(t) == 10:
                kit.label(cam, (tip[0], tip[1], tip[2] + 0.9), "NOTHING HAPPENS", _ls(cam), (255, 255, 255), RED)
            # little field lines pulled into the finger
            if g("steal") > 0.01 and i == 0 and not glove and k > 0.9:
                for q in range(5):
                    a = q * 1.256 + t * 0.8
                    p0 = (fx + 0.35 * math.cos(a), fy + 0.35 * math.sin(a), zc - 0.3)
                    cam.line([p0, ((p0[0] + fx) / 2, (p0[1] + fy) / 2, zc - 0.05), (fx, fy, tip[2] - 0.05)],
                             mix((255, 220, 80), (255, 255, 255), 0.3), 0.012 * g("steal"), caps=False)
            if g("electric") > 0.01 and i == 0:
                kit.rings(cam, (fx, fy, zc + 0.02), "z", 0.1, 0.6, t, (255, 210, 80), n=3, speed=0.8, width=0.02,
                          bg=(210, 220, 240))
        pa = g("palm")
        if pa > 0.01:
            k = _sm(pa)
            c = (1.85, 0.8, zc + 0.15 + (1 - k) * 1.5)
            cam.poly(cam.disc_pts(c, 0.7, "z", 30), shade(SKIN, -0.1), shade(SKIN, -0.35), 0.012)
            cam.poly(cam.disc_pts((c[0] + 0.15, c[1] + 0.1, c[2] + 0.15), 0.6, "z", 30), SKIN)
        dr = g("drops")
        if dr > 0.01:
            for (x, y) in ((0.6, 2.9), (1.4, 1.6), (0.4, 1.0), (1.6, 3.1)):
                z = zc + 0.05 + (1 - _sm(dr)) * 1.2
                cam.poly(cam.disc_pts((x, y, z), 0.13, "z", 16), mix((170, 210, 250), (255, 255, 255), 0.3),
                         (90, 150, 220), 0.01)
                x2, y2 = cam.p(x - 0.03, y - 0.03, z + 0.02)
                r = 0.03 * cam.s
                cam.d.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=(255, 255, 255))


VIDEO = dict(
    slug="touchscreen",
    title="How does your touchscreen know where your finger is?",
    steps=STEPS, scene=TouchScene, initial=INITIAL, tracker=dict(label="FIXES"),
)
