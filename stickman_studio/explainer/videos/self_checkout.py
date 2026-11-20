"""'Unexpected item in bagging area': who is judging you at self-checkout? - built step by step."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

WIDE = ((0.9, 0.4, 1.0), 165)
SCAN = ((0.6, 0.5, 1.15), 330)
BAG = ((1.9, 0.5, 1.15), 300)
SCREEN = ((1.35, 0.3, 1.6), 300)

STEPS = [
    dict(text="If you put a barcode scanner next to a cash box and let shoppers ring themselves up, you've got the "
              "world's simplest self checkout.",
         cam=((0.6, 0.5, 1.1), 430), pegs="neutral",
         cams=[("w:cash", ((0.9, 0.5, 1.1), 320), 0.9), ("w:simplest", WIDE, 1.4)],
         do=[("scanner", 0.0, 1, 0.7, "back"), ("laser", "w:scanner", 1, 0.3, "out"), ("cashbox", "w:cash", 1, 0.5, "back"),
             ("store", "w:simplest", 1, 1.3, "out"), ("shopper", "w:shoppers", 1, 0.5, "back")],
         keys=[("barcode scanner", INK), ("cash box|+ a cash box", INK), ("ring themselves up", INK),
               ("simplest self checkout", BLUE)],
         sfx=[("w:barcode", "pop"), ("w:cash", "cash"), ("w:simplest", "whoosh")]),
    dict(text="Beep. But the barcode doesn't hold the price. It's just a product number, like a name tag.",
         cam=SCAN, pegs="neutral",
         do=[("item", 0.0, 0, 0, "lin"), ("ip", 0.0, 0.5, 0.6, "io"), ("zoomcode", "w:barcode", 1, 0.4, "out")],
         keys=[("doesn't hold the price", RED), ("product number", INK), ("name tag", INK)],
         sfx=[(0.55, "ding")]),
    dict(text="The scanner turns the stripes into digits. The last digit is a check digit, calculated from all the "
              "others, so a misread barcode gets caught.",
         cam=SCAN, pegs="happy", pose="think",
         do=[("digits", "w:digits", 1, 0.8, "out"), ("checkd", "w:check", 1, 0.4, "out")],
         keys=[("stripes into digits", INK), ("check digit", INK), ("misread|misreads caught", BLUE)],
         fix="w:check",
         pops=[dict(kind="equation", at="w:calculated", parts=["5", "0", "1", "2", "3", "4", "...", "→", "7"],
                    colors=[INK] * 7 + [(120, 125, 140), GREEN], step=0.18, pos="bc", until="end+0.3")]),
    dict(text="Then it asks the store's database: what is this, and what does it cost?",
         cam=((-0.6, -0.6, 1.2), 150), pegs="neutral",
         do=[("zoomcode", 0.0, 0, 0.3, "in"), ("digits", 0.0, 0, 0.3, "in"), ("checkd", 0.0, 0, 0.3, "in"),
             ("db", "w:database", 1, 0.5, "back"), ("pk", "w:asks", 1, 1.2, "io"), ("pkb", "w:cost", 1, 1.0, "io"),
             ("scr", "w:cost+0.6", 1, 0, "lin")],
         keys=[("store's database", INK), ("what does it cost|name + price", BLUE)],
         fix="w:database",
         sfx=[("w:asks", "whoosh"), ("w:cost+0.6", "ding")]),
    dict(text="Easy. Until someone scans a cheap banana, and bags an expensive steak.",
         cam=WIDE, pegs="smug",
         do=[("ip", 0.0, 1.0, 0.6, "io"), ("bagn", 0.5, 1, 0, "lin"), ("item", "w:cheap", 1, 0, "lin"),
             ("ip", "w:cheap", 0.0, 0.01, "lin"), ("ip", "w:banana", 0.5, 0.7, "io"), ("scr", "w:banana", 2, 0, "lin"),
             ("ip", "w:bags", 1.0, 0.5, "io"), ("bagn", "w:bags+0.4", 2, 0, "lin"), ("steak", "w:expensive", 1, 0.8, "io")],
         keys=[("cheap banana", INK), ("expensive steak", RED)],
         sfx=[("w:banana", "ding"), ("w:steak", "sting")]),
    dict(text="So the bagging area sits on a scale. The database also knows what every product weighs, so the bag has "
              "to get heavier by just the right amount.",
         cam=BAG, pegs="neutral",
         do=[("steak", 0.0, 0, 0.01, "lin"), ("scale", "w:scale", 1, 0.5, "back"), ("expw", "w:weighs", 1, 0.3, "out")],
         keys=[("bagging area", INK), ("scale", INK), ("just the right amount|+ the right weight", BLUE)],
         fix="w:scale",
         pops=[dict(kind="equation", at="w:database", parts=["new weight", "=", "old", "+", "item"],
                    colors=[INK, (120, 125, 140), INK, (120, 125, 140), BLUE], step=0.3, pos="bc", until="end+0.3")],
         sfx=[("w:scale", "thud")]),
    dict(text="Sneak in something that wasn't scanned, and the weight doesn't add up. Unexpected item in the bagging "
              "area.",
         cam=BAG, pegs="shocked",
         do=[("steak", "w:sneak", 1, 0.8, "io"), ("alarm", "w:add", 1, 0, "lin"), ("scr", "w:unexpected", 3, 0, "lin")],
         keys=[("wasn't scanned", RED), ("doesn't add up", RED), ("unexpected item|UNEXPECTED ITEM!", RED)],
         pops=[dict(kind="warn", at="w:unexpected", text="+ 450 g  not scanned", pos="bc", until="end+0.3")],
         sfx=[("w:unexpected", "sting")]),
    dict(text="But no two apples weigh the same, and bags rustle. So the scale allows a little wiggle room. That's the "
              "tolerance.",
         cam=BAG, pegs="happy",
         do=[("steak", 0.0, 0, 0.6, "io"), ("alarm", 0.0, 0, 0, "lin"), ("scr", 0.0, 1, 0, "lin"),
             ("wobble", "w:apples", 1, 0.3, "out"), ("tol", "w:wiggle", 1, 0.5, "out"), ("wobble", "end-0.5", 0, 0.3, "in")],
         keys=[("no two apples", INK), ("wiggle room", INK), ("tolerance", INK)],
         fix="w:tolerance",
         pops=[dict(kind="meter", at="w:wiggle", text="WEIGHT CHECK", **{"from": 0.0, "to": 0.5}, color=GREEN,
                    fmt="WITHIN RANGE", pos="bc", until="end+0.3")]),
    dict(text="Loose fruit has no barcode at all. So the scanner glass is also a scale, and you type a short produce "
              "code to pay by weight.",
         cam=SCAN, pegs="neutral",
         do=[("tol", 0.2, 0, 0.3, "in"), ("item", 0.0, 2, 0, "lin"), ("ip", 0.0, 0.0, 0.01, "lin"),
             ("ip", "w:fruit", 0.5, 0.8, "io"), ("pscale", "w:glass", 1, 0.4, "out"), ("scr", "w:code", 4, 0, "lin")],
         keys=[("no barcode", RED), ("also a scale", INK), ("produce code|code 4011 = bananas", INK), ("pay by weight", BLUE)],
         fix="w:produce",
         sfx=[("w:code", "click")]),
    dict(text="Then someone scans a bottle of wine. The machine can't check ID, so it pauses and calls the attendant "
              "to check your age.",
         cam=((1.6, -0.4, 1.3), 170), pegs="worried",
         do=[("pscale", 0.2, 0, 0.3, "in"), ("ip", 0.0, 1.0, 0.5, "io"), ("item", "w:wine", 3, 0, "lin"),
             ("ip", "w:wine", 0.0, 0.01, "lin"), ("ip", "w:wine+0.1", 0.5, 0.6, "io"), ("scr", "w:pauses", 5, 0, "lin"),
             ("attendant", "w:attendant", 1, 0.5, "back"), ("light", "w:pauses", 1, 0.2, "out")],
         keys=[("bottle of wine", INK), ("can't check ID", RED), ("attendant", INK)],
         fix="w:attendant",
         sfx=[("w:pauses", "sting")]),
    dict(text="One attendant watches a whole row of machines from one screen, like air traffic control for groceries.",
         cam=((2.6, -1.2, 1.3), 120), pegs="happy",
         do=[("light", "w:watches", 0, 0.3, "in"), ("scr", "w:watches", 1, 0, "lin"), ("row", "w:row", 1, 1.0, "out")],
         keys=[("whole row of machines", INK), ("air traffic control", BLUE)]),
    dict(text="And some stores now add cameras above the scanner that spot items sliding past without a beep.",
         cam=((0.6, 0.5, 1.6), 230), pegs="shocked",
         do=[("camera", "w:cameras", 1, 0.5, "back"), ("item", 0.0, 4, 0, "lin"), ("ip", 0.0, 0.0, 0.01, "lin"),
             ("ip", "w:spot", 1.0, 1.2, "io"), ("spotted", "w:sliding", 1, 0.3, "out")],
         keys=[("cameras above the scanner", INK), ("without a beep", RED)],
         fix="w:cameras",
         pops=[dict(kind="stamp", at="w:beep", text="SPOTTED", color=RED, pos="mr", until="end+0.3")]),
    dict(text="Then you pay with cash. To catch fake notes, the slot shines light through every note and checks its "
              "size and its magnetic ink before accepting it.",
         cam=((-0.3, 0.6, 1.0), 300), pegs="neutral",
         do=[("spotted", 0.0, 0, 0.3, "in"), ("note", "w:pay", 1, "w:shines", "io"), ("uv", "w:shines", 1, 0.3, "out"),
             ("note", "w:accepting", 2, 0.6, "io"), ("uv", "end-0.3", 0, 0.2, "in")],
         keys=[("fake notes", RED), ("shines light through", INK), ("magnetic ink", INK)],
         fix="w:shines",
         pops=[dict(kind="check", at="w:accepting", text="real note", pos="bc", until="end+0.3")],
         sfx=[("w:accepting", "cash")]),
    dict(text="And in some stores, the exit gate only opens once you scan your receipt.",
         cam=((1.6, 2.6, 0.8), 190), pegs="happy",
         do=[("gate", 0.0, 1, 0.5, "back"), ("receipt", "w:scan", 1, 0.4, "out"), ("gate_open", "w:receipt", 1, 0.6, "io")],
         keys=[("exit gate", INK), ("scan your receipt|receipt = gate opens", BLUE)],
         fix="w:gate",
         sfx=[("w:receipt", "ding")]),
    dict(text="So next time the machine yells about an unexpected item, you'll know it's not judging you. It's just "
              "doing math with a scale.",
         cam=BAG, pegs="happy",
         do=[("gate_open", 0.2, 0, 0.4, "io"), ("camera", 0.0, 1, 0, "lin"), ("scr", "w:yells", 3, 0, "lin"),
             ("alarm", "w:yells", 1, 0, "lin"), ("alarm", "w:math", 0, 0, "lin"), ("scr", "w:math", 1, 0, "lin")],
         keys=[("not judging you", INK), ("math with a scale|it's just math", BLUE)]),
    dict(text="And congratulations, you just built a self checkout. Now you just need it to stop yelling at you. "
              "Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("scr", 0.2, 6, 0, "lin")],
         keys=[("built a self checkout|you built a self-checkout!", BLUE), ("stop yelling", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(scanner=0, laser=0, cashbox=0, store=0, shopper=0, item=0, ip=0, zoomcode=0, digits=0, checkd=0, db=0,
               pk=0, pkb=0, scr=0, bagn=0, steak=0, scale=0, expw=0, alarm=0, wobble=0, tol=0, pscale=0, attendant=0,
               light=0, row=0, camera=0, spotted=0, note=0, uv=0, gate=0, receipt=0, gate_open=0)

FLOOR = (222, 226, 232)
BODY = (60, 66, 84)
TOP = (226, 230, 238)
ZT = 0.95                      # counter top height
SCAN_C = (0.6, 0.5, ZT)        # centre of the scanner glass
BAG_C = (2.1, 0.5, ZT)
PATH = [(-1.2, 0.6, ZT + 0.05), (0.0, 0.5, ZT + 0.25), (0.6, 0.5, ZT + 0.12), (1.3, 0.5, ZT + 0.35),
        (2.1, 0.5, ZT + 0.12)]
SKIP = [(-1.2, 0.6, ZT + 0.05), (0.2, 0.9, ZT + 0.45), (1.3, 0.9, ZT + 0.5), (2.1, 0.5, ZT + 0.15)]
SCREENS = {0: ("SCAN ITEM", BLUE), 1: ("CEREAL  3.49", BLUE), 2: ("BANANA  0.25", BLUE),
           3: ("UNEXPECTED ITEM", RED), 4: ("CODE: 4011", BLUE), 5: ("WAIT FOR HELP", ORANGE),
           6: ("THANK YOU!", GREEN)}
DB_RACK = (-2.6, -2.4)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class CheckoutScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (232, 238, 246), (250, 248, 242), clouds=0)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        self._step = step_i
        st = g("store")
        if st > 0.01:
            self._store(cam, tr, t, st)
        if g("row") > 0.01:
            self._row(cam, tr, t)
        self._station(cam, tr, t)
        self._items(cam, tr, t)
        if st > 0.5:
            self._people(cam, tr, t)

    # ------------------------------------------------------------- store
    def _store(self, cam, tr, t, st):
        g = lambda k: tr.get(k, t)
        k = _sm(st)
        cam.poly([(-4, -3.2, 0), (6, -3.2, 0), (6, 4, 0), (-4, 4, 0)], FLOOR)
        for i in range(1, 17):
            cam.line([(-4 + i * 0.62, -3.2, 0), (-4 + i * 0.62, 4, 0)], shade(FLOOR, -0.05), 0.006, caps=False)
            cam.line([(-4, -3.2 + i * 0.45, 0), (6, -3.2 + i * 0.45, 0)], shade(FLOOR, -0.05), 0.006, caps=False)
        h = 3.6 * k
        cam.poly([(-4, -3.2, 0), (6, -3.2, 0), (6, -3.2, h), (-4, -3.2, h)], (240, 236, 228), (200, 196, 188), 0.01)
        cam.poly([(-4, -3.2, 0), (-4, 4, 0), (-4, 4, h), (-4, -3.2, h)], (228, 224, 216), (200, 196, 188), 0.01)
        if k > 0.9:
            for sx in (-1.6, 1.2, 4.0):          # shelves on the back wall
                cam.box(sx, -3.2, 0, 2.2, 0.5, 2.0, (200, 170, 130))
                for row, z in enumerate((0.4, 1.0, 1.6)):
                    for j in range(6):
                        c = PEG_COLORS[(j + row + int(sx)) % 5]
                        cam.box(sx + 0.1 + j * 0.35, -3.0, z, 0.25, 0.25, 0.32, mix(c, (255, 255, 255), 0.25))
            kit.plate(cam, "x", -3.99, -1.2, 2.6, 1.6, 3.3, (40, 140, 90), (20, 80, 50))
            kit.plane_text(cam, "x", -3.98, 0.2, 2.95, "SELF CHECKOUT", 0.3, (255, 255, 255), max_w=2.5)
        sh = ShadowLayer(cam)
        sh.ao_edge((-4, -3.2, 0), (6, -3.2, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
        sh.ao_edge((-4, -3.2, 0), (-4, 4, 0), (1, 0, 0), (0, 0, 1), 0.3, 140)
        sh.box_on_plane(-0.1, 0, 0, 3.0, 1.0, ZT, "z", 0.0, 200)
        sh.apply(cam.img, 0.26, 2.4)
        # store database (server rack in the back office corner)
        db = g("db")
        if db > 0.01:
            parts.server_rack(cam, DB_RACK[0], DB_RACK[1], 0, 0.7, 0.7, 2.2 * _sm(db), t, busy=0.6)
            if db > 0.8 and self._step == 3:
                kit.label(cam, (DB_RACK[0] + 0.35, DB_RACK[1] + 0.35, 2.6), "STORE DATABASE", 0.14, (255, 255, 255), BLUE)
        # attendant podium
        at = g("attendant")
        if at > 0.01 or g("row") > 0.01:
            kk = _sm(max(at, g("row")))
            cam.box(3.6, -1.6, 0, 0.7, 0.6, 1.1 * kk, (90, 96, 110))
            kit.plate(cam, "y", -0.999, 3.65, 0.6, 4.25, 1.0, (30, 34, 44)) if kk > 0.9 else None
            if kk > 0.9:
                for i in range(4):
                    on = g("light") > 0.5 and i == 0
                    kit.plate(cam, "y", -0.998, 3.7 + i * 0.13, 0.7, 3.8 + i * 0.13, 0.9,
                              ORANGE if on and int(t * 6) % 2 else (90, 200, 120))
                kit.peg(cam, (3.95, -0.6, 0), PEG_COLORS[2], "happy", t, 1.8 * kk, (-0.6, 0.5), seed=6,
                        pose="wave" if g("light") > 0.5 else "idle", floor=FLOOR)
                if self._step in (9, 10):
                    kit.label(cam, (3.95, -1.3, 1.6), "ATTENDANT", 0.12, (255, 255, 255), (90, 96, 110))

    def _row(self, cam, tr, t):
        k = _sm(tr.get("row", t))
        for i in range(1, 4):            # more lanes behind (same machine, simpler)
            y = 0.0 - i * 1.6
            if y < -3.0:
                break
            x0 = -0.1 + 0.0
            cam.box(x0, y, 0, 2.9, 1.0, ZT * k, BODY, top_color=TOP)
            cam.box(1.25, y + 0.05, ZT * k, 0.12, 0.12, 0.7 * k, (50, 54, 66))
            cam.box(1.0, y + 0.1, ZT + 0.6 * k, 0.6, 0.06, 0.4 * k, (30, 34, 44))

    # ------------------------------------------------------------- station
    def _station(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        sc = g("scanner")
        if sc <= 0.01:
            return
        k = _sm(sc)
        # scanner counter
        cam.box(0.0, 0.0, 0, 1.2, 1.0, ZT * k, BODY, top_color=TOP)
        if k < 0.9:
            return
        # vertical scanner window + glass bed
        cam.box(0.05, 0.0, ZT, 1.1, 0.16, 0.42, (70, 76, 92))
        kit.plate(cam, "y", 0.161, 0.2, ZT + 0.08, 1.0, ZT + 0.36, (40, 50, 60))
        glass = mix((50, 60, 72), (90, 200, 120), 0.6 * g("pscale"))
        cam.poly([(0.2, 0.25, ZT + 0.002), (1.0, 0.25, ZT + 0.002), (1.0, 0.85, ZT + 0.002), (0.2, 0.85, ZT + 0.002)],
                 glass, (30, 34, 44), 0.01)
        las = g("laser")
        if las > 0.01:
            near = abs(g("ip") - 0.5) < 0.12
            col = (255, 60, 60) if near else (200, 70, 70)
            for i in range(5):
                a = -0.6 + i * 0.3 + 0.05 * math.sin(t * 3)
                cam.line([(0.6, 0.55, ZT + 0.003), (0.6 + math.cos(a) * 0.38, 0.55 + math.sin(a) * 0.28, ZT + 0.003)],
                         col, 0.01, caps=False)
            if near:
                kit.glow_dot(cam, (0.6, 0.55, ZT + 0.12), 0.06, (255, 80, 80))
        if g("pscale") > 0.3:
            kit.label(cam, (0.6, 0.85, ZT + 0.1), "SCALE: 0.82 kg", 0.08, (255, 255, 255), GREEN)
        # cash box (simplest version) / payment unit
        cb = g("cashbox")
        if cb > 0.01:
            cam.box(-0.55, 0.2, ZT * 0.0 + 0.0, 0.5, 0.6, 1.25 * _sm(cb), (80, 86, 102))
            kit.plate(cam, "y", 0.801, -0.5, 0.75, -0.1, 0.9, (20, 20, 26))
            kit.plate(cam, "y", 0.801, -0.5, 1.0, -0.1, 1.08, (220, 200, 90))
            kit.plane_text(cam, "y", 0.802, -0.3, 0.6, "CASH", 0.06, (255, 255, 255), max_w=0.35)
            nt = g("note")
            if 0.01 < nt < 1.99:
                ins = min(1.0, nt) if nt <= 1 else 1.0 + 0.0
                gone = max(0.0, nt - 1.0)
                yy = 0.801 + 0.5 * (1 - ins) - 0.0
                h_ = 0.22 * (1 - gone)
                if h_ > 0.01:
                    cam.poly([(-0.48, yy + 0.01, 1.04), (-0.12, yy + 0.01, 1.04), (-0.12, yy + 0.01 + 0.0, 1.04 + h_),
                              (-0.48, yy + 0.01, 1.04 + h_)], (150, 205, 150), (80, 130, 80), 0.008)
                if g("uv") > 0.3:
                    zz = 1.05 + 0.18 * (0.5 + 0.5 * math.sin(t * 9))
                    cam.line([(-0.5, 0.83, zz), (-0.1, 0.83, zz)], (170, 90, 255), 0.03, caps=False)
                    kit.label(cam, (-0.3, 0.9, 1.55), "LIGHT + MAGNETIC INK CHECK", 0.07, (255, 255, 255), (130, 70, 220))
        # screen on a post
        cam.box(1.25, 0.05, ZT, 0.12, 0.12, 0.6, (50, 54, 66))
        cam.box(0.95, 0.1, ZT + 0.55, 0.75, 0.08, 0.5, (30, 34, 44))
        scr = int(round(g("scr")))
        text, col = SCREENS.get(scr, SCREENS[0])
        if g("alarm") > 0.5 and int(t * 4) % 2:
            col = (255, 90, 90)
        kit.plate(cam, "y", 0.181, 1.0, ZT + 0.6, 1.65, ZT + 1.0, col)
        kit.plane_text(cam, "y", 0.182, 1.325, ZT + 0.8, text, 0.09, (255, 255, 255), max_w=0.58)
        # bagging area: platform (scale), bag rack, bag
        cam.box(1.4, 0.0, 0, 1.5, 1.0, ZT - 0.05, shade(BODY, 0.05), top_color=TOP)
        s = g("scale")
        cam.box(1.5, 0.1, ZT - 0.05, 1.3, 0.8, 0.05 + 0.02 * s, mix((170, 176, 190), (90, 170, 255), 0.4 * s))
        cam.line([(1.55, 0.15, ZT), (1.55, 0.15, ZT + 0.8), (2.75, 0.15, ZT + 0.8), (2.75, 0.15, ZT)], (150, 156, 170),
                 0.03)
        # bag
        cam.box(1.75, 0.2, ZT, 0.75, 0.55, 0.55, (246, 246, 250))
        cam.line([(1.75, 0.75, ZT + 0.55), (2.1, 0.75, ZT + 0.8), (2.5, 0.75, ZT + 0.55)], (220, 220, 228), 0.02)
        if s > 0.01:
            bagn = int(round(g("bagn"))) + (1 if g("steak") > 0.9 else 0)
            w = {0: 0.0, 1: 0.50, 2: 0.62, 3: 1.07}.get(bagn, 0.62)
            if g("wobble") > 0.3:
                w += 0.008 * math.sin(t * 13)
            alarm = g("alarm") > 0.5
            px, py = 2.15, 0.9
            kit.plate(cam, "y", 0.901, 2.3, ZT - 0.45, 2.85, ZT - 0.15, (20, 22, 30))
            kit.plane_text(cam, "y", 0.902, 2.575, ZT - 0.3, f"{w:.3f} kg", 0.08, RED if alarm else (90, 255, 140),
                           max_w=0.5)
            if g("expw") > 0.5 and self._step in (5, 6, 7, 14):
                kit.label(cam, (2.1, 0.5, ZT + 1.15), "EXPECTED: 0.620 kg" if not alarm else "EXPECTED 0.620 / GOT 1.070",
                          0.08, (255, 255, 255), RED if alarm else BLUE)
            if g("tol") > 0.01 and self._step == 7:
                kit.label(cam, (2.1, 0.5, ZT + 1.38), "OK: 0.620 kg  +/- a few g", 0.08, (255, 255, 255), GREEN)
        # camera above
        cm = g("camera")
        if cm > 0.01:
            cam.line([(0.6, 0.5, 2.6), (0.6, 0.5, 2.2)], (90, 96, 110), 0.03)
            cam.box(0.45, 0.4, 2.05 + (1 - _sm(cm)) * 0.6, 0.3, 0.2, 0.16, (230, 232, 238))
            if cm > 0.8:
                for (ex, ey) in ((0.1, 0.1), (1.1, 0.1), (1.1, 0.9), (0.1, 0.9)):
                    cam.line([(0.6, 0.5, 2.05), (ex, ey, ZT)], (120, 200, 255), 0.008, caps=False)
                if self._step == 11:
                    kit.label(cam, (0.6, 0.5, 2.45), "CAMERA", 0.09, (255, 255, 255), BLUE)
        # packets to / from the database
        for key, rev, colr in (("pk", False, (60, 140, 255)), ("pkb", True, (60, 200, 110))):
            v = g(key)
            if 0.01 < v < 0.99:
                path = [(0.6, 0.15, ZT + 0.4), (0.0, -1.0, 2.2), (DB_RACK[0] + 0.35, DB_RACK[1] + 0.7, 1.6)]
                if rev:
                    path = list(reversed(path))
                kit.packet(cam, path, v, colr, 0.07)

    # ------------------------------------------------------------- items
    def _item_draw(self, cam, kind, p, t, scale=1.0):
        x, y, z = p
        if kind == 0:      # cereal box
            cam.box(x - 0.15, y - 0.08, z, 0.3, 0.16, 0.42, (250, 200, 70))
            kit.plate(cam, "y", y + 0.081, x - 0.1, z + 0.05, x + 0.1, z + 0.16, (255, 255, 255))
            for i in range(9):
                xx = x - 0.09 + i * 0.022
                cam.line([(xx, y + 0.082, z + 0.06), (xx, y + 0.082, z + 0.15)], INK, 0.006 + 0.004 * (i % 2), caps=False)
            kit.plane_text(cam, "y", y + 0.082, x, z + 0.3, "CEREAL", 0.045, (180, 60, 40), max_w=0.25)
        elif kind == 1 or kind == 2:   # banana
            pts = [(x - 0.22 + 0.44 * f, y, z + 0.04 + 0.12 * math.sin(f * math.pi)) for f in [i / 10 for i in range(11)]]
            cam.line(pts, (190, 150, 30), 0.1)
            cam.line(pts, (250, 214, 70), 0.075)
            if kind == 2:
                pts2 = [(px + 0.03, py + 0.08, pz + 0.03) for px, py, pz in pts]
                cam.line(pts2, (190, 150, 30), 0.1)
                cam.line(pts2, (250, 214, 70), 0.075)
        elif kind == 3:    # wine bottle
            cam.box(x - 0.08, y - 0.08, z, 0.16, 0.16, 0.4, (90, 30, 50))
            cam.box(x - 0.03, y - 0.03, z + 0.4, 0.06, 0.06, 0.18, (90, 30, 50))
            kit.plate(cam, "y", y + 0.081, x - 0.06, z + 0.12, x + 0.06, z + 0.26, (240, 230, 210))
        elif kind == 4:    # chocolate bar slid past
            cam.box(x - 0.2, y - 0.07, z, 0.4, 0.14, 0.06, (120, 70, 40))

    def _items(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        if g("scanner") < 0.9:
            return
        # bag contents
        n = int(round(g("bagn")))
        for i in range(min(n, 3)):
            cam.box(1.85 + i * 0.18, 0.3, ZT + 0.35, 0.16, 0.3, 0.25 + 0.05 * i, PEG_COLORS[(i + 1) % 5])
        st = g("steak")
        if st > 0.01:
            p, _ = kit.path_point(SKIP, st)
            cam.box(p[0] - 0.2, p[1] - 0.14, p[2], 0.4, 0.28, 0.1, (220, 70, 80))
            cam.box(p[0] - 0.16, p[1] - 0.1, p[2] + 0.1, 0.32, 0.2, 0.02, (250, 240, 240))
        ip = g("ip")
        kind = int(round(g("item")))
        if 0.0 <= ip < 0.995 and g("store") > 0.3:
            path = PATH if kind != 4 else SKIP
            p, _ = kit.path_point(path, ip)
            self._item_draw(cam, kind, p, t)
            if kind == 4 and g("spotted") > 0.5:
                kit.label(cam, (p[0], p[1], p[2] + 0.35), "NOT SCANNED", 0.08, (255, 255, 255), RED)
        if g("zoomcode") > 0.01 and kind == 0:
            k = _sm(g("zoomcode"))
            kit.label(cam, (0.6, 0.8, ZT + 0.8), "5 012345 678907" if g("digits") > 0.5 else "|| ||| | || ||| |",
                      0.12 * k, INK, (255, 255, 255))
            if g("checkd") > 0.5:
                kit.label(cam, (0.95, 0.8, ZT + 1.05), "CHECK DIGIT  7 OK", 0.09, (255, 255, 255), GREEN)

    def _people(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        sh = g("shopper")
        if sh <= 0.01:
            return
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (0.9, 1.75, 0), PEG_COLORS[0], expr, t, 2.0 * _sm(sh), (0.0, -0.8), seed=1, pose=tr.peg_pose(t),
                react=react, floor=FLOOR)
        # basket on the floor stand
        cam.box(-1.5, 0.35, 0, 0.5, 0.5, 0.75, (90, 96, 110))
        cam.box(-1.5, 0.35, 0.75, 0.5, 0.5, 0.25, (230, 60, 60))
        gt = g("gate")
        if gt > 0.01:                      # exit gate with receipt reader
            op = g("gate_open")
            k = _sm(gt)
            cam.box(0.6, 3.0, 0, 0.18, 0.5, 1.0 * k, (90, 96, 110))
            cam.box(2.6, 3.0, 0, 0.18, 0.5, 1.0 * k, (90, 96, 110))
            for side, x0 in ((1, 0.78), (-1, 2.6)):
                w = 0.9 * (1 - 0.85 * op)
                xa, xb = (x0, x0 + w) if side > 0 else (x0 - w, x0)
                cam.poly([(xa, 3.25, 0.3), (xb, 3.25, 0.3), (xb, 3.25, 0.9), (xa, 3.25, 0.9)], (200, 230, 250),
                         (90, 140, 180), 0.012)
            kit.plate(cam, "y", 3.501, 0.62, 0.7, 0.76, 0.85, (90, 230, 140) if op > 0.5 else (226, 52, 64))
            if g("receipt") > 0.01:
                rk = _sm(g("receipt"))
                kit.plate(cam, "y", 3.52, 0.55, 0.88, 0.75, 0.88 + 0.3 * rk, (255, 255, 255), (150, 150, 160))
            kit.label(cam, (1.7, 3.25, 1.3), "EXIT", 0.14, (255, 255, 255), GREEN if op > 0.5 else RED)


VIDEO = dict(
    slug="self_checkout",
    title="'Unexpected item in bagging area': who is judging you?",
    steps=STEPS, scene=CheckoutScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"),
)
