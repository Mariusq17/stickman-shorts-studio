"""How does an ATM know it didn't give you two stuck notes? - built step by step."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

WIDE = ((1.5, 0.6, 1.25), 175)
INSIDE = ((0.75, 1.3, 0.9), 430)
ROLL = ((1.0, 1.3, 0.95), 640)
TOPCAM = ((0.95, 1.3, 1.3), 520)

STEPS = [
    dict(text="If you put a stack of cash in a box with a slot in the front, you've got the world's simplest ATM.",
         cam=((0.75, 0.8, 0.45), 520), pegs="neutral",
         cams=[("w:box", ((0.9, 0.8, 1.0), 300), 1.0), ("w:slot", ((1.3, 0.8, 1.3), 290), 0.7), ("w:simplest", WIDE, 1.4)],
         do=[("stack", 0.0, 1, 0.8, "out"), ("box", "w:box", 1, 0.9, "out"), ("slot", "w:slot", 1, 0.4, "back"),
             ("street", "w:simplest", 1, 1.3, "out")],
         keys=[("stack of cash", INK), ("box|in a box", INK), ("slot|+ a slot", INK), ("simplest ATM", BLUE)],
         sfx=[("w:box", "pop"), ("w:slot", "pop"), ("w:simplest", "whoosh")]),
    dict(text="Ask for sixty, and it pushes out three twenties. Easy.",
         cam=((1.6, 0.8, 1.2), 200), pegs="happy",
         do=[("scr", "w:sixty", 1, 0, "lin"), ("flow", "w:pushes", 3.0, "end-0.6", "lin")],
         keys=[("sixty|60", INK), ("three twenties|3 x 20", INK), ("easy", BLUE)],
         pops=[dict(kind="count", at="w:pushes", **{"from": 0, "to": 60}, anim=2.0, fmt="{}", sub="cash out",
                    pos="tr", until="end+0.2")],
         sfx=[("w:pushes", "cash")]),
    dict(text="But banknotes are paper, and paper sticks together. Grab one, and two come along.",
         cam=INSIDE, pegs="shocked",
         do=[("flow", "w:grab", 4.0, 1.4, "lin")],
         keys=[("sticks together", RED), ("two come along", RED)],
         pops=[dict(kind="warn", at="w:two", text="2 notes stuck", pos="bc", until="end+0.3")],
         sfx=[("w:two", "sting")]),
    dict(text="So a rubber roller spins against the top note and peels off just one at a time. That's the pick "
              "roller.",
         cam=((0.8, 1.3, 0.75), 540), pegs="happy",
         do=[("picker", "w:rubber", 1, 0.5, "back"), ("flow", "w:peels", 6.0, 2.4, "lin")],
         keys=[("rubber roller", INK), ("one at a time", BLUE), ("pick roller", INK)],
         fix="w:pick",
         pops=[dict(kind="arrow", at="w:spins", xyz=(0.92, 1.55, 0.72), text="pick roller", color=BLUE, off=(0.15, -0.12),
                    dur=2.4, sound=False)],
         sfx=[("w:rubber", "pop")]),
    dict(text="Mostly. Brand new notes can cling so tightly that two still slip through as one.",
         cam=INSIDE, pegs="worried",
         do=[("flow", "w:cling", 7.0, 1.6, "lin")],
         keys=[("brand new notes", INK), ("slip through|2 slip through", RED)]),
    dict(text="So every note squeezes between two rollers that measure its thickness. One note is about a tenth of a "
              "millimeter. Two stuck together are double.",
         cam=ROLL, pegs="neutral",
         do=[("sensor", "w:rollers", 1, 0.5, "back"), ("flow", "w:squeezes", 8.0, "w:double", "lin"),
             ("flow", "w:double", 9.0, 1.2, "lin"),
             ("thick", "w:tenth", 1.0, 0.2, "out"), ("thick", "w:double", 2.0, 0.2, "out")],
         keys=[("measure its thickness", INK), ("tenth of a millimeter|0.1 mm", INK), ("double|0.2 mm = double", RED)],
         fix="w:thickness",
         pops=[dict(kind="graph", at="w:tenth", title="THICKNESS", track="thick", window=5.0, color=BLUE, pos="bc",
                    until="end+0.4")],
         sfx=[("w:double", "sting")]),
    dict(text="It's like telling one sheet of paper from two just by pinching it, except it does it to every single note.",
         cam=ROLL, pegs="happy", pose="think",
         do=[("thick", 0.1, 1.0, 0.2, "out"), ("flow", "w:pinching", 11.0, "end", "lin")],
         keys=[("pinching it", INK), ("every single note", BLUE)]),
    dict(text="But it can't hand you eighty when you asked for sixty.",
         cam=((1.6, 0.8, 1.2), 210), pegs="worried",
         keys=[("eighty|80?!", RED), ("asked for sixty|asked for 60", INK)],
         pops=[dict(kind="bars", at="w:hand", title="CASH OUT", until="end+0.3", pos="bc",
                    items=[("asked", 0.6, GREEN), ("got", 0.8, RED)])]),
    dict(text="So a little flap flips, and the suspicious note drops into a locked box. That's the reject bin. Then it "
              "simply picks a fresh one.",
         cam=((0.75, 1.3, 1.0), 430), pegs="happy",
         do=[("divert", "w:flap", 1, 0.3, "out"), ("flow", "w:flips", 12.0, 1.8, "lin"),
             ("flow", "w:simply", 13.0, 1.4, "lin")],
         keys=[("little flap", INK), ("locked box", INK), ("reject bin", INK), ("fresh one", BLUE)],
         fix="w:reject",
         sfx=[("w:flips", "click")]),
    dict(text="Light beams across the path also count every note and check its length, so a torn or folded one gets "
              "rejected too.",
         cam=((0.95, 1.3, 1.05), 470), pegs="neutral",
         do=[("beams", "w:light", 1, 0.4, "out"), ("flow", "w:count", 15.0, "end-0.2", "lin")],
         keys=[("light beams", INK), ("count every note", INK), ("torn or folded", RED)],
         fix="w:light",
         sfx=[("w:light", "ding")]),
    dict(text="Now, firing notes out one by one would scatter them all over the street.",
         cam=((2.2, 0.6, 1.4), 170), pegs="shocked",
         do=[("flow", "w:firing", 17.0, 2.0, "lin")],
         keys=[("one by one", INK), ("scatter|scattered!", RED)],
         sfx=[("w:scatter", "whoosh")]),
    dict(text="So the notes pile up inside on a spinning wheel first, into one neat bundle. That's the stacker.",
         cam=TOPCAM, pegs="happy",
         do=[("stacker", "w:spinning", 1, 0.5, "back"), ("flow", "w:pile", 20.0, 2.6, "lin")],
         keys=[("spinning wheel", INK), ("neat bundle", BLUE), ("stacker", INK)],
         fix="w:stacker",
         sfx=[("w:spinning", "pop")]),
    dict(text="Then a shutter opens, and the whole bundle slides out at once.",
         cam=((1.8, 0.8, 1.3), 260), pegs="happy",
         do=[("shutter", "w:shutter", 1, 0.4, "out"), ("present", "w:slides", 1, 0.8, "out"), ("scr", "w:shutter", 2, 0, "lin")],
         keys=[("shutter", INK), ("whole bundle|whole bundle at once", BLUE)],
         sfx=[("w:shutter", "click"), ("w:slides", "cash")]),
    dict(text="But people get distracted. They grab their card, walk away, and leave the cash sticking out.",
         cam=WIDE, pegs="worried",
         do=[("walk", "w:walk", 1, 1.6, "io")],
         keys=[("distracted", RED), ("leave the cash|cash left behind", RED)],
         pops=[dict(kind="warn", at="w:leave", text="cash left behind", pos="bc", until="end+0.3")]),
    dict(text="So on many machines, if nobody takes it in time, the machine pulls it back inside. That's the retract.",
         cam=((1.6, 0.8, 1.3), 240), pegs="happy",
         do=[("present", "w:pulls", 0, 0.8, "io"), ("shutter", "w:inside", 0, 0.4, "io"), ("retracted", "w:retract", 1, 0.6, "out"),
             ("scr", "w:pulls", 3, 0, "lin")],
         keys=[("in time", INK), ("pulls it back|pulled back inside", BLUE), ("retract", INK)],
         fix="w:retract",
         pops=[dict(kind="meter", at="w:nobody", text="TIMER", **{"from": 1.0, "to": 0.0}, color=ORANGE, fmt="TIME UP",
                    anim=1.2, pos="bc", until="w:retract")],
         sfx=[("w:pulls", "whoosh")]),
    dict(text="Many machines also give your card back before the cash, because people almost never forget money, "
              "but they do forget cards.",
         cam=((1.7, 1.1, 1.75), 340), pegs="happy",
         do=[("cardout", "w:card", 1, 0.5, "out"), ("scr", "w:card", 4, 0, "lin"), ("cardout", "end-0.4", 0, 0.4, "in")],
         keys=[("card back before the cash|card first, then cash", BLUE), ("forget cards", RED)],
         fix="w:before",
         sfx=[("w:card", "click")]),
    dict(text="And the box is full of money, so of course someone will try to break in.",
         cam=WIDE, pegs="shocked",
         do=[("scr", 0.1, 0, 0, "lin"), ("walk", 0, 0, 0.01, "lin"), ("cust", 0.1, 0, 0.3, "in"), ("thief", "w:someone", 1, 0.5, "back"),
             ("pry", "w:break", 1, 0.3, "out")],
         keys=[("full of money", INK), ("break in", RED)],
         sfx=[("w:break", "slap")]),
    dict(text="So the cash sits inside a heavy steel safe, and only the screen and buttons live outside it.",
         cam=((0.75, 1.2, 0.8), 230), pegs="happy",
         do=[("safe", "w:heavy", 1, 0.8, "out")],
         keys=[("heavy steel safe", INK), ("screen and buttons|only the screen outside", BLUE)],
         fix="w:safe",
         sfx=[("w:steel", "thud")]),
    dict(text="And in many countries, forcing a cassette open sets off ink that stains every note, so stolen cash is "
              "worthless.",
         cam=((0.6, 1.2, 0.5), 280), pegs="happy",
         do=[("ink", "w:ink", 1, 0.8, "out"), ("thief_sad", "w:worthless", 1, 0.3, "out")],
         keys=[("forcing a cassette", RED), ("ink", INK), ("stains every note", INK), ("worthless", BLUE)],
         fix="w:ink",
         pops=[dict(kind="stamp", at="w:worthless", text="WORTHLESS", color=BLUE, pos="mr", until="end+0.3")],
         sfx=[("w:ink", "boing")]),
    dict(text="So next time you hear that whirring before your cash appears, you'll know every note was just peeled, "
              "pinched, measured and counted.",
         cam=((0.95, 1.2, 1.0), 360), pegs="happy",
         do=[("scr", 0.1, 0, 0, "lin"), ("ink", 0.1, 0, 0.5, "in"), ("thief", 0.1, 0, 0.4, "in"), ("cust", 0.2, 1, 0.4, "back"),
             ("flow", "w:whirring", 23.0, "end-0.3", "lin")],
         keys=[("whirring", INK), ("peeled|peeled, pinched, counted", BLUE)]),
    dict(text="And congratulations, you just built an ATM. Now you just need to remember your PIN. Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("present2", 0.4, 1, 0.8, "out")],
         keys=[("built an ATM|you built an ATM!", BLUE), ("remember your PIN", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(cardout=0, stack=0, box=0, slot=0, street=0, cust=1, scr=0, flow=0, picker=0, sensor=0, thick=1.0, divert=0,
               beams=0, stacker=0, shutter=0, present=0, walk=0, retracted=0, thief=0, pry=0, safe=0, ink=0,
               thief_sad=0, present2=0)

# fate of each note: (where it ends, kind)  kind: n = normal, d = double, t = torn
FATE = ([("hand", "n")] * 3 + [("hand", "d")] + [("hand", "n")] * 2 + [("hand", "d")] + [("hand", "n"), ("hand", "d")]
        + [("hand", "n")] * 2 + [("reject", "d"), ("hand", "n"), ("reject", "t"), ("hand", "n")]
        + [("scatter", "n")] * 2 + [("bundle", "n")] * 3 + [("bundle2", "n")] * 3)

BG_TOP, BG_BOT = (214, 230, 248), (250, 242, 230)
PAVE = (214, 214, 222)
INFLOOR = (196, 186, 176)
BRICK = (196, 122, 96)
HOUSING = (70, 110, 170)
NOTE = (132, 196, 132)
NOTE_INK = (90, 120, 230)
ATM_H = 2.7
Y0, Y1, YC = 0.0, 1.6, 1.3
SY = 1.12                      # slot centre (y) on the front panel

MAIN = [(0.88, YC, 0.62), (1.12, YC, 0.76), (1.12, YC, 1.12)]
UP = [(1.12, YC, 1.12), (1.12, YC, 1.38), (1.18, YC, 1.5)]
REJECT = [(1.12, YC, 1.12), (0.8, YC, 1.15), (0.5, YC, 1.07), (0.42, YC, 0.86)]
EXIT = [(1.18, YC, 1.5), (1.66, SY, 1.52), (2.25, SY, 1.2)]
SCATTER = [(1.18, YC, 1.5), (1.66, SY, 1.52), (2.4, SY - 0.4, 2.0), (3.4, SY - 1.6, 2.8), (4.4, SY - 2.8, 3.4)]
L_MAIN = sum(math.dist(a, b) for a, b in zip(MAIN, MAIN[1:]))


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class AtmScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, BG_TOP, BG_BOT, clouds=6)

    # -------------------------------------------------------------- main
    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        street = g("street")
        box = g("box")
        self._ground(cam, tr, t, street)
        if street > 0.01:
            self._facade(cam, tr, t, street)
        if box > 0.01:
            self._housing_back(cam, box)
        self._internals(cam, tr, t, box)
        if box > 0.01:
            self._housing_front(cam, tr, t, box)
        self._notes(cam, tr, t, outside=True)
        if street > 0.01:
            self._people(cam, tr, t, street)

    # -------------------------------------------------------------- environment
    def _ground(self, cam, tr, t, street):
        k = _sm(street)
        if k <= 0.01:
            return
        cam.poly([(-2.5, -3.5, 0), (1.3, -3.5, 0), (1.3, 3.5, 0), (-2.5, 3.5, 0)], INFLOOR)
        cam.poly([(1.3, -3.5, 0), (6.5, -3.5, 0), (6.5, 4.0, 0), (1.3, 4.0, 0)], PAVE)
        for i in range(1, 13):
            cam.line([(1.3 + i * 0.45, -3.5, 0), (1.3 + i * 0.45, 4.0, 0)], shade(PAVE, -0.07), 0.008, caps=False)
        for i in range(1, 17):
            cam.line([(1.3, -3.5 + i * 0.45, 0), (6.5, -3.5 + i * 0.45, 0)], shade(PAVE, -0.07), 0.008, caps=False)
        cam.box(5.2, -3.5, 0, 0.25, 7.5, 0.12, (170, 170, 180))      # kerb
        cam.poly([(5.45, -3.5, 0), (6.5, -3.5, 0), (6.5, 4.0, 0), (5.45, 4.0, 0)], (110, 114, 126))
        # interior back wall (bank lobby, behind the facade)
        h = 3.6 * k
        cam.poly([(-2.5, -3.5, 0), (1.3, -3.5, 0), (1.3, -3.5, h), (-2.5, -3.5, h)], (232, 224, 210), (180, 170, 160), 0.01)
        cam.poly([(-2.5, -3.5, 0), (-2.5, 3.5, 0), (-2.5, 3.5, h), (-2.5, -3.5, h)], (220, 212, 198), (180, 170, 160), 0.01)
        sh = ShadowLayer(cam)
        sh.ao_edge((-2.5, -3.5, 0), (1.3, -3.5, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
        sh.ao_edge((-2.5, -3.5, 0), (-2.5, 3.5, 0), (1, 0, 0), (0, 0, 1), 0.3, 140)
        sh.ao_edge((1.6, -3.5, 0), (1.6, 0.0, 0), (1, 0, 0), (0, 0, 1), 0.25, 120)
        sh.box_on_plane(1.3, -3.5, 0, 0.3, 5.1, 3.6 * k, "z", 0.0, 180)
        sh.apply(cam.img, 0.28, 2.6)

    def _facade(self, cam, tr, t, street):
        k = _sm(street)
        h = 3.6 * k
        cam.box(1.3, -3.5, 0, 0.3, 3.5, h, BRICK)
        for i in range(1, int(h / 0.22) + 1):
            z = i * 0.22
            cam.line([(1.601, -3.5, z), (1.601, 0.0, z)], shade(BRICK, -0.2), 0.006, caps=False)
            off = 0.0 if i % 2 else 0.25
            yy = -3.5 + off
            while yy < -0.05:
                cam.line([(1.601, yy, z - 0.22), (1.601, yy, z)], shade(BRICK, -0.2), 0.005, caps=False)
                yy += 0.5
        if k > 0.9:
            kit.plate(cam, "x", 1.605, -2.9, 2.5, -0.6, 3.2, (30, 60, 110), (10, 20, 40), 0.01)
            kit.plane_text(cam, "x", 1.61, -1.75, 2.85, "BANK", 0.42, (255, 220, 120))
            cam.box(1.3, 0.0, ATM_H, 0.3, Y1, h - ATM_H, BRICK)       # lintel above the ATM
            # cut face of the wall (cutaway)
            cam.poly([(1.3, Y1, ATM_H), (1.6, Y1, ATM_H), (1.6, Y1, h), (1.3, Y1, h)], (150, 90, 70))

    # -------------------------------------------------------------- housing
    def _housing_back(self, cam, box):
        k = _sm(box)
        h = ATM_H * k
        cam.poly([(0, Y0, 0), (1.6, Y0, 0), (1.6, Y0, h), (0, Y0, h)], (176, 186, 204))
        cam.poly([(0, Y0, 0), (0, Y1, 0), (0, Y1, h), (0, Y0, h)], (156, 166, 186))
        cam.poly([(0, Y0, 0.02), (1.6, Y0, 0.02), (1.6, Y1, 0.02), (0, Y1, 0.02)], (140, 150, 170))
        if k > 0.9:   # computer board in the upper part
            cam.box(0.15, 0.2, 1.75, 0.8, 0.9, 0.06, (40, 110, 70))
            for i in range(4):
                cam.box(0.22 + i * 0.18, 0.4, 1.81, 0.12, 0.3, 0.06, (30, 32, 40))
            parts.led(cam, (0.85, 1.1, 1.85), (90, 230, 140), True, 0.025)
            kit.label(cam, (0.55, 0.7, 2.25), "COMPUTER", 0.11, (255, 255, 255), (40, 110, 70))

    def _housing_front(self, cam, tr, t, box):
        g = lambda kk: tr.get(kk, t)
        k = _sm(box)
        h = ATM_H * k
        # front panel (x = 1.6) and top
        cam.poly([(1.6, Y0, 0), (1.6, Y1, 0), (1.6, Y1, h), (1.6, Y0, h)], HOUSING, shade(HOUSING, -0.45), 0.012)
        cam.poly([(0, Y0, h), (1.6, Y0, h), (1.6, Y1, h), (0, Y1, h)], shade(HOUSING, 0.2), shade(HOUSING, -0.4), 0.012)
        # cut edges of the open side
        for a, b in (((0, Y1, 0), (0, Y1, h)), ((0, Y1, h), (1.6, Y1, h)), ((1.6, Y1, 0), (1.6, Y1, h)),
                     ((0, Y1, 0.02), (1.6, Y1, 0.02))):
            cam.line([a, b], shade(HOUSING, -0.2), 0.05)
        if k < 0.9:
            return
        # slot
        sl = _sm(g("slot"))
        sh = g("shutter")
        if sl > 0.01:
            y0, y1 = SY - 0.36 * sl, SY + 0.36 * sl
            kit.plate(cam, "x", 1.602, y0 - 0.06, 1.4, y1 + 0.06, 1.64, (50, 54, 66))
            kit.plate(cam, "x", 1.604, y0, 1.46, y1, 1.58, mix((150, 156, 170), (12, 12, 16), max(sh, 0.0 if g("box") else 1)))
        if g("street") > 0.5:
            # screen + keypad ledge + card slot
            kit.plate(cam, "x", 1.602, 0.25, 1.95, 1.35, 2.5, (24, 26, 34))
            scr = int(round(g("scr")))
            col = {2: (60, 170, 110), 3: (220, 120, 40), 4: (60, 170, 110)}.get(scr, (60, 120, 210))
            kit.plate(cam, "x", 1.604, 0.31, 2.0, 1.29, 2.45, col)
            kit.plane_text(cam, "x", 1.606, 0.8, 2.22, {0: "HELLO", 1: "60", 2: "TAKE CASH", 3: "RETRACTED", 4: "TAKE CARD"}.get(scr, ""),
                           0.12 if scr != 1 else 0.2, (255, 255, 255), max_w=0.85)
            cam.box(1.6, 0.35, 1.7, 0.25, 0.75, 0.08, (60, 64, 78))
            for r in range(3):
                for c in range(3):
                    x, y = cam.p(1.64 + r * 0.065, 0.45 + c * 0.2, 1.785)
                    rr = 0.022 * cam.s
                    cam.d.ellipse((x - rr * 1.6, y - rr, x + rr * 1.6, y + rr), fill=(220, 222, 230))
            kit.plate(cam, "x", 1.603, 1.18, 1.86, 1.45, 1.92, (20, 20, 26))
            co = g("cardout")
            if co > 0.01:
                cam.box(1.6, 1.2, 1.87, 0.32 * co, 0.23, 0.025, (40, 96, 210))
                parts.led(cam, (1.605, 1.5, 1.89), (255, 200, 60), int(t * 6) % 2 == 0, 0.03)
            parts.led(cam, (1.605, 1.5, 1.89), (90, 230, 140), True, 0.02)
            kit.plane_text(cam, "x", 1.606, 0.8, 2.6, "ATM", 0.12, (255, 255, 255))
        # bundle sticking out of the slot
        pr = max(g("present"), g("present2"))
        if pr > 0.01:
            n = 3
            for i in range(n):
                z = 1.48 + i * 0.025
                x0 = 0.95 + 0.7 * pr
                cam.poly([(x0, SY - 0.22, z), (x0 + 0.45, SY - 0.22, z), (x0 + 0.45, SY + 0.22, z), (x0, SY + 0.22, z)],
                         NOTE, shade(NOTE, -0.4), 0.006)

    # -------------------------------------------------------------- internals
    def _internals(self, cam, tr, t, box):
        g = lambda k: tr.get(k, t)
        st = g("stack")
        safe = g("safe")
        ink = g("ink")
        if safe > 0.01:    # steel safe back + floor (inside)
            cam.poly([(0.04, 0.05, 0.04), (1.56, 0.05, 0.04), (1.56, 0.05, 1.28), (0.04, 0.05, 1.28)],
                     mix((176, 186, 204), (120, 124, 136), safe))
        # cassette
        bk = _sm(box)
        if bk > 0.3:
            cam.box(0.1, 0.75, 0.08, 0.95, 0.75, 0.04, (90, 94, 108))
            cam.poly([(0.1, 0.75, 0.08), (0.1, 1.5, 0.08), (0.1, 1.5, 0.66), (0.1, 0.75, 0.66)], (110, 114, 128))
            cam.poly([(0.1, 0.75, 0.08), (1.05, 0.75, 0.08), (1.05, 0.75, 0.66), (0.1, 0.75, 0.66)], (100, 104, 118))
        if st > 0.01:
            used = min(1.0, g("flow") / 26.0)
            n = int(16 * _sm(st) * (1 - used * 0.6))
            col = mix(NOTE, NOTE_INK, ink)
            for i in range(n):
                z = 0.14 + i * 0.026
                cam.poly([(0.2, 0.85, z), (0.95, 0.85, z), (0.95, 1.45, z), (0.2, 1.45, z)], col, shade(col, -0.4), 0.005)
            if ink > 0.3:
                for i in range(6):
                    x, y = cam.p(0.3 + i * 0.11, 1.15 + 0.2 * math.sin(i * 2.3), 0.14 + n * 0.026)
                    r = (0.05 + 0.03 * (i % 3)) * cam.s * ink
                    cam.d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(60, 80, 200))
        if bk > 0.3:
            cam.poly([(0.1, 1.5, 0.08), (1.05, 1.5, 0.08), (1.05, 1.5, 0.22), (0.1, 1.5, 0.22)], (120, 124, 138),
                     (70, 74, 88), 0.008)
            cam.poly([(1.05, 0.75, 0.08), (1.05, 1.5, 0.08), (1.05, 1.5, 0.22), (1.05, 0.75, 0.22)], (100, 104, 118))
            if bk > 0.9 and g("street") > 0.5:
                kit.label(cam, (0.55, 1.5, 0.3), "CASSETTE", 0.09, (255, 255, 255), (70, 74, 88))
        # pick roller
        pk = g("picker")
        flow = g("flow")
        if pk > 0.01:
            cam.wheel((0.93, YC, 0.72), 0.075 * _sm(pk), 0.25, (60, 60, 66), "y", -flow * 9, 4)
        # guides of the path
        if bk > 0.9:
            for pts in (MAIN, UP):
                cam.line([(x + 0.06, y - 0.2, z) for x, y, z in pts], (150, 156, 170), 0.012, caps=False)
        # thickness rollers + sensor
        se = g("sensor")
        if se > 0.01:
            r = 0.075 * _sm(se)
            for x in (1.03, 1.21):
                cam.wheel((x, YC, 0.92), r, 0.5, (150, 156, 170), "y", flow * 12 * (1 if x < 1.1 else -1), 4)
            dbl = self._double_at_sensor(tr, t)
            parts.led(cam, (1.25, 1.56, 1.02), RED if dbl else (90, 230, 140), True, 0.03)
            if se > 0.9:
                kit.label(cam, (0.6, 1.55, 0.98), "0.2 mm!" if dbl else "0.1 mm", 0.09, (255, 255, 255),
                          RED if dbl else BLUE)
        # reject bin
        dv = g("divert")
        if dv > 0.01:
            k = _sm(dv)
            cam.box(0.15, 0.95, 0.72, 0.6 * k, 0.55, 0.04, (80, 84, 96))
            cam.poly([(0.15, 0.95, 0.72), (0.15, 1.5, 0.72), (0.15, 1.5, 1.0), (0.15, 0.95, 1.0)], (90, 94, 108))
            nrej = sum(1 for i, (f, kd) in enumerate(FATE) if f == "reject" and flow - i >= 1)
            for i in range(nrej):
                z = 0.77 + i * 0.03
                c = NOTE if FATE[[j for j, f in enumerate(FATE) if f[0] == "reject"][i]][1] == "d" else (220, 170, 90)
                cam.poly([(0.2, 1.0, z), (0.7, 1.0, z), (0.7, 1.45, z), (0.2, 1.45, z)], c, shade(c, -0.4), 0.005)
            cam.poly([(0.15, 1.5, 0.72), (0.75, 1.5, 0.72), (0.75, 1.5, 0.9), (0.15, 1.5, 0.9)], (200, 70, 70),
                     (120, 40, 40), 0.008)
            kit.plane_text(cam, "y", 1.501, 0.45, 0.81, "REJECT", 0.075 * k, (255, 255, 255), max_w=0.5)
            # flap at the junction
            ang = -0.9 if self._divert_now(tr, t) else 0.6
            fx, fz = 1.12, 1.12
            cam.line([(fx, YC + 0.22, fz), (fx - 0.16 * math.cos(ang), YC + 0.22, fz + 0.16 * math.sin(ang))],
                     (230, 180, 60), 0.025)
        # light beams
        bm = g("beams")
        if bm > 0.01:
            for z in (1.0, 1.25):
                col = (255, 60, 60) if int(t * 10) % 3 else (255, 150, 150)
                cam.line([(1.12, 0.9, z), (1.12, 1.58, z)], col, 0.012 + 0.012 * bm, caps=False)
                parts.led(cam, (1.12, 1.59, z), (255, 60, 60), True, 0.025)
        # stacker wheel + bundle
        sk = g("stacker")
        if sk > 0.01:
            cam.wheel((0.9, YC, 1.47), 0.13 * _sm(sk), 0.4, (230, 180, 60), "y", t * 6, 6)
            nb = sum(1 for i, (f, kd) in enumerate(FATE) if f == "bundle" and flow - i >= 1)
            if g("present") < 0.01 and g("retracted") < 0.5:
                for i in range(nb):
                    z = 1.48 + i * 0.025
                    cam.poly([(0.95, SY - 0.02, z), (1.4, SY - 0.02, z), (1.4, SY + 0.38, z), (0.95, SY + 0.38, z)],
                             NOTE, shade(NOTE, -0.4), 0.006)
        self._notes(cam, tr, t, outside=False)
        # safe walls in front (cut view): a thick steel frame around the lower part
        if safe > 0.01:
            k = _sm(safe)
            th = 0.03 + 0.07 * k
            col = mix((120, 126, 140), (90, 96, 110), k)
            for (a, b) in (((0.04, 0.04), (1.56, 0.04 + th)), ((0.04, 1.28 - th), (1.56, 1.28)),
                           ((0.04, 0.04), (0.04 + th, 1.28)), ((1.56 - th, 0.04), (1.56, 1.28))):
                cam.poly([(a[0], Y1 + 0.01, a[1]), (b[0], Y1 + 0.01, a[1]), (b[0], Y1 + 0.01, b[1]), (a[0], Y1 + 0.01, b[1])],
                         col, shade(col, -0.4), 0.006)
            if k > 0.8:
                for x in (0.1, 1.5):
                    for z in (0.1, 1.22):
                        parts.bolt(cam, (x, Y1 + 0.012, z), 0.025)
                kit.label(cam, (0.8, Y1, 1.36), "STEEL SAFE", 0.1, (255, 255, 255), (70, 74, 88))
        elif bk > 0.9 and g("street") > 0.5:
            cam.line([(0.04, Y1 + 0.01, 1.28), (1.56, Y1 + 0.01, 1.28)], (140, 146, 160), 0.012, caps=False)

    def _divert_now(self, tr, t):
        flow = tr.get("flow", t)
        i = int(flow)
        if i >= len(FATE) or tr.get("divert", t) < 0.5:
            return False
        return FATE[i][0] == "reject"

    def _double_at_sensor(self, tr, t):
        flow = tr.get("flow", t)
        i = int(flow)
        if i >= len(FATE):
            return False
        p = flow - i
        return FATE[i][1] == "d" and 0.15 < p < 0.6

    def _notes(self, cam, tr, t, outside):
        g = lambda k: tr.get(k, t)
        flow = g("flow")
        i = int(flow)
        if flow <= 0.0 or i >= len(FATE):
            return
        p = flow - i
        fate, kind = FATE[i]
        ink = 0.0
        col = (220, 170, 90) if kind == "t" else NOTE
        # stage 1: along MAIN to the junction (0..0.45), stage 2: up / reject / exit
        if p < 0.45:
            if outside:
                return
            path, s = MAIN, p / 0.45
        else:
            q = (p - 0.45) / 0.55
            if fate == "reject":
                path, s = REJECT, q
                if outside:
                    return
            elif fate in ("bundle", "bundle2"):
                path, s = UP, q
                if outside:
                    return
            else:
                full = UP + (SCATTER if fate == "scatter" else EXIT)[1:]
                path, s = full, q
                pt, _ = kit.path_point(full, s)
                if (pt[0] > 1.6) != outside:
                    return
                if pt[0] > 2.2 and fate == "hand":
                    return
        kit.sheet(cam, path, s, 0.26, 0.4, col, double=0.035 if kind == "d" else 0.0,
                  crumple=1.0 if kind == "t" else 0.0)

    # -------------------------------------------------------------- people
    def _people(self, cam, tr, t, street):
        g = lambda k: tr.get(k, t)
        k = _sm(street)
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        th = g("thief")
        if th > 0.01:
            sad = g("thief_sad")
            col = mix((120, 120, 130), (80, 110, 220), sad)
            kit.peg(cam, (2.5, -0.5, 0), col, "angry" if sad > 0.5 else "smug", t, 2.8 * th, (-0.6, 0.3), seed=7,
                    pose="hold", floor=PAVE, hat=True)
            pry = g("pry")
            if pry > 0.01:
                wob = 0.04 * math.sin(t * 20) * pry
                cam.line([(2.2, -0.3, 1.0), (1.65, 0.1 + wob, 1.5)], (200, 50, 50), 0.035)
        cu = g("cust")
        if cu > 0.01:
            w = g("walk")
            x, y = 2.75 + 0.6 * w, -0.45 + 2.6 * w
            e = expr if th < 0.5 else "shocked"
            kit.peg(cam, (x, y, 0), PEG_COLORS[0], e, t, 2.8 * cu * k, (-0.7, 0.0 if w < 0.5 else 0.6), seed=1,
                    pose=tr.peg_pose(t) if w < 0.1 else "idle", react=react, floor=PAVE)
            nh = sum(1 for j, (f, kd) in enumerate(FATE) if f == "hand" and g("flow") - j >= 1)
            if 0 < nh and tr.step_at(t) < 10:
                hx, hz = x - 0.1, 0.55
                y = y + 0.42
                for j in range(min(nh, 6)):
                    z = hz + j * 0.02
                    cam.poly([(hx - 0.2, y - 0.15, z), (hx + 0.2, y - 0.15, z), (hx + 0.2, y + 0.15, z),
                              (hx - 0.2, y + 0.15, z)], NOTE, shade(NOTE, -0.4), 0.005)


VIDEO = dict(
    slug="atm_notes",
    title="How does an ATM know it didn't give you two stuck notes?",
    steps=STEPS, scene=AtmScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"),
)
