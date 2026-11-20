"""How do you pay with a card in 1 second (with no battery in the card)? - built step by step."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)

WIDE = ((1.75, 1.0, 1.15), 150)
CARDCAM = ((2.35, 0.9, 1.55), 300)
NETWIDE = ((6.4, 0.4, 1.0), 88)

STEPS = [
    dict(text="If you put a tiny chip and a loop of wire inside a plastic card, you've got the world's simplest "
              "contactless card.",
         cam=((2.2, 1.4, 1.62), 900), pegs="neutral",
         cams=[("w:loop", ((2.3, 1.4, 1.58), 640), 0.9), ("w:plastic", ((2.35, 1.4, 1.55), 480), 0.8),
               ("w:simplest", WIDE, 1.4)],
         do=[("chip", 0.0, 1, 0.6, "back"), ("coil", "w:loop", 1, 1.1, "out"),
             ("body", "w:plastic", 1, 0.5, "back"), ("shop", "w:simplest", 1, 1.4, "out"),
             ("cust", "w:contactless", 1, 0.5, "back")],
         keys=[("tiny chip", INK), ("loop of wire|+ a loop of wire", INK), ("plastic card|inside a card", INK),
               ("simplest contactless card|simplest contactless card", BLUE)],
         sfx=[("w:chip", "pop"), ("w:plastic", "pop"), ("w:simplest", "whoosh")]),
    dict(text="Just one problem. There's no battery in there, so the chip is completely dead.",
         cam=((2.35, 1.3, 1.55), 330), pegs="worried",
         keys=[("one problem", INK), ("no battery", RED), ("completely dead", RED)],
         pops=[dict(kind="warn", at="w:battery", text="0% battery", pos="bc", until="end+0.2")],
         sfx=[("w:dead", "thud")]),
    dict(text="So the payment terminal makes a magnetic field that flips direction about thirteen million times "
              "every second.",
         cam=((2.35, 0.9, 1.6), 250), pegs="neutral",
         do=[("disp", "w:payment", 1, 0, "lin"), ("field", "w:magnetic", 1, 0.5, "out")],
         keys=[("payment terminal", INK), ("magnetic field", INK), ("thirteen million|13.56 million / s", INK)],
         fix="w:magnetic",
         pops=[dict(kind="count", at="w:thirteen", **{"from": 0, "to": 13}, anim=1.2, fmt="{} million",
                    sub="flips per second", pos="tr", until="end+0.3")],
         sfx=[("w:magnetic", "whoosh")]),
    dict(text="Bring the card close, and that field pushes a tiny current through the loop, enough to wake the chip. "
              "That's induction, the same trick as a wireless phone charger.",
         cam=CARDCAM, pegs="happy",
         do=[("gap", "w:close", 0.12, 0.8, "io"), ("power", "w:current", 1, 0.9, "out")],
         keys=[("tiny current", INK), ("wake the chip|chip wakes up", BLUE), ("induction", INK),
               ("wireless phone charger|like a wireless charger", INK)],
         fix="w:induction",
         pops=[dict(kind="meter", at="w:current", text="CHIP POWER", **{"from": 0.0, "to": 1.0}, color=GREEN,
                    fmt="ON", pos="bc", until="w:induction"),
               dict(kind="arrow", at="w:loop", xyz=(2.0, 0.53, 1.4), text="antenna loop", color=BLUE,
                    off=(-0.18, 0.12), dur=2.2, sound=False)],
         sfx=[("w:close", "whoosh"), ("w:wake", "ding")]),
    dict(text="But if that field reached across the shop, you could pay for someone else's groceries just by "
              "standing in line.",
         cam=((2.2, 2.0, 1.0), 150), pegs="shocked",
         do=[("queue", "w:field", 1, 0.5, "back"), ("frange", "w:reached", 3.4, 1.3, "out"),
             ("qcard", "w:pay", 1, 0.3, "out")],
         keys=[("across the shop", RED), ("someone else's groceries", RED)],
         pops=[dict(kind="warn", at="w:pay", text="you paid?!", pos="bc", until="end+0.3")],
         sfx=[("w:pay", "sting")]),
    dict(text="So the field is deliberately weak, and only works within a few centimeters. That's near field "
              "communication. NFC.",
         cam=((2.3, 1.5, 1.2), 190), pegs="happy",
         do=[("frange", "w:weak", 0.55, 0.9, "io"), ("qcard", "w:weak", 0, 0.3, "out")],
         keys=[("deliberately weak", INK), ("few centimeters|only a few cm", BLUE),
               ("near field communication|near field communication", INK), ("NFC", INK)],
         fix="w:near",
         pops=[dict(kind="bars", at="w:within", title="RANGE", until="end+0.2", pos="bc",
                    items=[("Wi-Fi", 1.0, RED), ("NFC", 0.06, GREEN)])]),
    dict(text="Now the chip is awake. It could just shout your card number, but anyone with a hidden reader could "
              "copy it and go shopping forever.",
         cam=((3.0, 1.6, 1.2), 185), pegs="worried",
         do=[("thief", "w:anyone", 1, 0.5, "back"), ("steal", "w:copy", 1, 0.4, "out")],
         keys=[("shout your card number", INK), ("hidden reader", RED), ("copy it|copied!", RED)],
         pops=[dict(kind="arrow", at="w:hidden", xyz=(3.55, 1.75, 0.95), text="hidden reader", color=RED,
                    off=(0.12, -0.14), dur=2.4)],
         sfx=[("w:copy", "sting")]),
    dict(text="So the chip keeps a secret key that never leaves it. For every payment, it mixes the amount, the "
              "date and a random number into a one time code. That's the cryptogram.",
         cam=CARDCAM, pegs="neutral",
         do=[("steal", 0, 0, 0.3, "in"), ("key", "w:secret", 1, 0.5, "back"), ("mixing", "w:mixes", 1, 0.4, "out"),
             ("mixing", "w:cryptogram", 0, 0.4, "out")],
         keys=[("secret key", INK), ("never leaves|never leaves the chip", BLUE), ("one time code", INK),
               ("cryptogram", INK)],
         fix="w:cryptogram",
         pops=[dict(kind="equation", at="w:amount", parts=["amount", "+", "date", "+", "random", "=", "code"],
                    colors=[INK, (120, 125, 140), INK, (120, 125, 140), INK, (120, 125, 140), BLUE], step=0.35,
                    pos="bc", until="end+0.3")],
         sfx=[("w:secret", "click")]),
    dict(text="Copy that code and try it again, and it's useless. It was only good for that one payment, like a "
              "ticket that tears itself up after the show.",
         cam=((2.9, 1.3, 1.3), 190), pegs="happy",
         do=[("replay", "w:try", 1, 0.9, "io"), ("disp", "w:useless", 4, 0, "lin"), ("thief_mad", "w:useless", 1, 0.3, "out")],
         keys=[("try it again", RED), ("useless", BLUE), ("tears itself up", INK)],
         pops=[dict(kind="stamp", at="w:useless", text="DECLINED", color=RED, pos="mr", until="w:ticket")],
         sfx=[("w:useless", "slap")]),
    dict(text="But the terminal can't check that code on its own. Only your bank knows the key, and your bank is "
              "miles away.",
         cam=((2.35, 0.9, 1.5), 240), pegs="worried",
         cams=[("w:miles", NETWIDE, 1.5)],
         do=[("thief", 0.2, 0, 0.4, "in"), ("disp", 0.2, 1, 0, "lin"), ("net", "w:only", 1, 1.4, "out")],
         keys=[("can't check", RED), ("only your bank|only YOUR bank knows", INK), ("miles away", RED)],
         sfx=[("w:miles", "whoosh")]),
    dict(text="So the terminal sends it to the shop's bank, which passes it through the card network, like Visa "
              "or Mastercard, to your bank.",
         cam=NETWIDE, pegs="neutral",
         do=[("pk1", "w:sends", 1, 1.0, "io"), ("b1", "w:shop's", 1, 0.3, "out"), ("pk2", "w:passes", 1, 1.0, "io"),
             ("b2", "w:network", 1, 0.3, "out"), ("pk3", "w:Visa", 1, 1.3, "io"), ("b3", "w:your", 1, 0.3, "out")],
         keys=[("shop's bank", INK), ("card network", INK), ("your bank", INK)],
         fix="w:network",
         sfx=[("w:sends", "whoosh"), ("w:passes", "whoosh"), ("w:your", "ding")]),
    dict(text="Your bank checks the code, your balance, and whether this purchase looks weird, like a coffee in "
              "Tokyo five minutes after one in London. That's fraud scoring.",
         cam=((10.9, 0.4, 1.5), 135), pegs="neutral",
         do=[("scan", "w:checks", 1, 0.4, "out")],
         keys=[("checks the code", INK), ("your balance", INK), ("looks weird", RED), ("fraud scoring", INK)],
         fix="w:fraud",
         pops=[dict(kind="check", at="w:code", text="code OK", pos="tl", until="w:balance-0.1"),
               dict(kind="check", at="w:balance", text="money OK", pos="tl", until="w:whether"),
               dict(kind="meter", at="w:weird", text="FRAUD RISK", **{"from": 0.0, "to": 0.12}, color=GREEN,
                    fmt="LOW", pos="bc", until="end+0.3")]),
    dict(text="Then the answer races all the way back. Approved. The whole round trip usually takes a second or two.",
         cam=NETWIDE, pegs="happy",
         cams=[("w:approved", ((2.35, 0.9, 1.6), 240), 0.9)],
         do=[("scan", 0, 0, 0.3, "in"), ("ret", "w:races", 1, "w:approved", "io"), ("disp", "w:approved", 3, 0, "lin")],
         keys=[("all the way back", INK), ("approved", BLUE), ("second or two|1-2 seconds", BLUE)],
         pops=[dict(kind="stamp", at="w:approved", text="APPROVED", color=GREEN, pos="mr", until="w:whole")],
         sfx=[("w:races", "whoosh"), ("w:approved", "ding")]),
    dict(text="Then someone taps a whole wallet with two cards inside. Which one pays?",
         cam=((2.35, 0.9, 1.55), 280), pegs="worried",
         do=[("disp", 0.1, 1, 0, "lin"), ("card2", "w:wallet", 1, 0.5, "back")],
         keys=[("whole wallet", INK), ("two cards", RED), ("which one pays|which one pays?", RED)],
         pops=[dict(kind="warn", at="w:two", text="two cards!", pos="bc", until="end+0.3")],
         sfx=[("w:wallet", "pop")]),
    dict(text="So the terminal talks to one card at a time. If two answer at once, it stops and asks for just one. "
              "That's anti-collision.",
         cam=((2.35, 0.9, 1.55), 280), pegs="happy",
         do=[("disp", "w:stops", 5, 0, "lin"), ("card2", "w:anti-collision", 0, 0.5, "in")],
         keys=[("one card at a time", INK), ("just one|just one, please", BLUE), ("anti-collision", INK)],
         fix="w:talks",
         sfx=[("w:stops", "click")]),
    dict(text="And when you pay with your phone, it doesn't even send your real card number. It sends a stand in "
              "number that only works on that phone. That's a token.",
         cam=CARDCAM, pegs="happy",
         do=[("disp", 0.1, 1, 0, "lin"), ("phone", "w:phone", 1, 0.6, "back")],
         keys=[("your phone", INK), ("real card number|real number: never sent", BLUE), ("stand in", INK),
               ("token", INK)],
         fix="w:token",
         pops=[dict(kind="arrow", at="w:token", xyz=(2.35, 0.53, 1.75), text="token", color=BLUE,
                    off=(0.22, -0.1), until="end+0.3")],
         sfx=[("w:phone", "pop")]),
    dict(text="So next time you tap and hear that beep, you'll know your card just woke up, did some math, and got "
              "three companies to agree in about a second.",
         cam=WIDE, pegs="happy",
         do=[("phone", 0.1, 0, 0.4, "in"), ("disp", "w:beep", 3, 0, "lin")],
         keys=[("hear that beep|beep!", INK), ("woke up", INK), ("did some math", INK),
               ("three companies|3 companies agreed", BLUE)],
         pops=[dict(kind="count", at="w:three", **{"from": 0, "to": 3}, anim=0.6, fmt="{}", sub="companies said yes",
                    pos="tr", until="end+0.2")],
         sfx=[("w:beep", "ding")]),
    dict(text="And congratulations, you just built a contactless card. Now you just need some money on it. "
              "Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         keys=[("built a contactless card|you built a contactless card!", BLUE), ("money on it", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(chip=0, coil=0, body=0, shop=0, cust=0, gap=1.0, field=0, frange=0.55, power=0, disp=0, queue=0,
               qcard=0, thief=0, steal=0, key=0, mixing=0, replay=0, thief_mad=0, net=0, pk1=0, pk2=0, pk3=0,
               b1=0, b2=0, b3=0, scan=0, ret=0, card2=0, phone=0)

BG_TOP, BG_BOT = (232, 240, 252), (252, 246, 236)
FLOOR = (236, 222, 204)
WALL = (246, 236, 220)
WALL2 = (232, 218, 200)
COUNTER = (178, 120, 78)
CARD = (40, 96, 210)
GOLD = (236, 190, 70)
COPPER = (214, 130, 70)
TERM = (52, 56, 70)

TX0, TX1, TY, TZ0, TZ1 = 2.0, 2.7, 0.4, 1.1, 2.22      # terminal: front face at y = TY
CX0, CX1, CZ0, CZ1 = 1.95, 2.75, 1.28, 1.80            # card on its face plane
FIELD_C = (2.35, TY, 1.55)
PATH1 = [(TX1, 0.3, 1.2), (3.45, 0.3, 1.2), (3.45, 0.3, 0.03), (5.2, 0.3, 0.03)]
PATH2 = [(6.8, 0.3, 0.03), (7.6, 0.3, 0.03)]
PATH3 = [(9.2, 0.3, 0.03), (10.0, 0.3, 0.03)]
BUILDINGS = ((5.2, "SHOP'S BANK"), (7.6, "CARD NETWORK"), (10.0, "YOUR BANK"))


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class CardScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, BG_TOP, BG_BOT, clouds=5)

    # ------------------------------------------------------------------ main
    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        shop = g("shop")
        net = g("net")
        if shop > 0.01:
            self._room(cam, tr, t, shop)
        if net > 0.01:
            self._network(cam, tr, t, net)
        card_y = TY + g("gap")
        # field rings behind the card
        fld = g("field") * _sm(shop * 2 - 0.6)
        if fld > 0.01:
            self._field(cam, t, fld, g("frange"), card_y, behind=True)
        if g("card2") > 0.01:
            self._card(cam, tr, t, card_y - 0.05, g("card2"), dx=0.16, dz=0.14, color=(226, 96, 60), simple=True)
        ph = g("phone")
        if ph < 0.5:
            self._card(cam, tr, t, card_y, 1.0 - _sm(ph * 2), dx=0.0, dz=0.0, color=CARD)
        else:
            k = _sm((ph - 0.5) * 2)
            w, h = 0.46 * k, 0.86 * k
            cx = (CX0 + CX1) / 2
            cam.box(cx - w / 2, card_y - 0.04, 1.12, w, 0.04, h, (30, 32, 40))
            parts.phone(cam, "y", card_y, cx - w / 2, 1.12, w, h, t, (40, 70, 140),
                        [("PAY", (255, 255, 255)), ("tok 5208", (150, 220, 255)), ("....7731", (180, 190, 210))])
        if fld > 0.01:
            self._field(cam, t, fld, g("frange"), card_y, behind=False)
        if shop > 0.01:
            self._people(cam, tr, t, shop)
        if net > 0.01:
            self._packets(cam, tr, t)

    # ------------------------------------------------------------------ pieces
    def _room(self, cam, tr, t, shop):
        g = lambda k: tr.get(k, t)
        a = _sm(shop * 1.6)
        hw = 3.6 * a
        cam.poly([(-1.6, -1.6, 0), (4.6, -1.6, 0), (4.6, 4.4, 0), (-1.6, 4.4, 0)], FLOOR)
        for k in range(1, 12):     # floor tiles
            cam.line([(-1.6 + k * 0.55, -1.6, 0), (-1.6 + k * 0.55, 4.4, 0)], shade(FLOOR, -0.06), 0.006, caps=False)
            cam.line([(-1.6, -1.6 + k * 0.55, 0), (4.6, -1.6 + k * 0.55, 0)], shade(FLOOR, -0.06), 0.006, caps=False)
        if hw > 0.05:
            cam.poly([(-1.6, -1.6, 0), (4.6, -1.6, 0), (4.6, -1.6, hw), (-1.6, -1.6, hw)], WALL, shade(WALL, -0.25), 0.01)
            cam.poly([(-1.6, -1.6, 0), (-1.6, 4.4, 0), (-1.6, 4.4, hw), (-1.6, -1.6, hw)], WALL2, shade(WALL, -0.3), 0.01)
            # shelves with products on the back wall
            for row, z in enumerate((0.9, 1.6, 2.3)):
                if z + 0.5 > hw:
                    continue
                cam.box(-1.2, -1.6, z, 2.6, 0.42, 0.05, (190, 150, 110))
                for k in range(7):
                    col = PEG_COLORS[(k + row * 2) % 5]
                    hh = 0.28 + 0.12 * ((k * 7 + row) % 3) / 2
                    cam.box(-1.1 + k * 0.36, -1.5, z + 0.05, 0.26, 0.24, hh, mix(col, (255, 255, 255), 0.2))
            # sign on the side wall
            if hw > 3.0:
                kit.plate(cam, "x", -1.59, 0.4, 2.55, 2.6, 3.2, (60, 150, 110), shade((60, 150, 110), -0.4))
                kit.plane_text(cam, "x", -1.58, 1.5, 2.88, "MARKET", 0.32, (255, 255, 255))
        sh = ShadowLayer(cam)
        if hw > 0.5:
            sh.ao_edge((-1.6, -1.6, 0), (4.6, -1.6, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
            sh.ao_edge((-1.6, -1.6, 0), (-1.6, 4.4, 0), (1, 0, 0), (0, 0, 1), 0.3, 140)
            sh.ao_edge((-1.6, -1.6, 0), (-1.6, -1.6, hw), (1, 0, 0), (0, 1, 0), 0.3, 140)
        c = _sm(shop * 1.6 - 0.4)
        if c > 0.05:
            sh.box_on_plane(0, -0.2, 0, 3.4, 1.2, 1.1 * c, "z", 0.0, 230)
        sh.apply(cam.img, 0.30, 2.6)
        # cashier behind the counter
        if c > 0.3:
            kit.peg(cam, (-0.4, -0.8, 0), PEG_COLORS[2], "happy" if g("disp") == 3 else "neutral", t, 2.0 * c,
                    (0.4, 0.4), seed=4, pose="idle")
        # counter + till + cable to the network
        if c > 0.01:
            hc = 1.1 * c
            cam.box(0, -0.2, 0, 3.4, 1.2, hc, COUNTER, top_color=(222, 214, 200))
            if g("net") > 0.01:
                kit.cable(cam, PATH1[1:], lit=0.0)
            cam.line([(0, 1.0, hc - 0.12), (3.4, 1.0, hc - 0.12)], shade(COUNTER, -0.3), 0.012, caps=False)
            cam.line([(3.4, -0.2, hc - 0.12), (3.4, 1.0, hc - 0.12)], shade(COUNTER, -0.4), 0.012, caps=False)
            if c > 0.9:
                cam.box(0.3, -0.05, 1.1, 0.8, 0.6, 0.35, (90, 96, 112))     # cash register
                cam.box(0.35, 0.0, 1.45, 0.5, 0.06, 0.32, (40, 44, 56))
                kit.plate(cam, "y", 0.065, 0.39, 1.5, 0.81, 1.72, (110, 220, 160))
                for k in range(3):                                         # groceries
                    cam.box(1.25 + k * 0.22, 0.2 + (k % 2) * 0.25, 1.1, 0.18, 0.18, 0.22 + 0.06 * k,
                            mix(PEG_COLORS[(k + 3) % 5], (255, 255, 255), 0.3))
        tz = _sm(shop * 1.6 - 0.75)
        if tz > 0.01:
            self._terminal(cam, tr, t, tz)

    def _terminal(self, cam, tr, t, k):
        g = lambda kk: tr.get(kk, t)
        drop = (1 - k) * 0.8
        z0, z1 = TZ0 + drop, TZ1 + drop
        cam.box(TX0 - 0.05, TY - 0.45, TZ0 + drop, TX1 - TX0 + 0.1, 0.5, 0.08, (40, 44, 56))
        cam.box(TX0, TY - 0.15, z0, TX1 - TX0, 0.15, z1 - z0, TERM)
        # screen
        disp = int(round(g("disp")))
        scr = {3: (60, 190, 110), 4: (226, 70, 80), 5: (250, 170, 60)}.get(disp, (70, 120, 200))
        kit.plate(cam, "y", TY + 0.002, TX0 + 0.06, z1 - 0.42, TX1 - 0.06, z1 - 0.08, (20, 22, 30))
        kit.plate(cam, "y", TY + 0.003, TX0 + 0.09, z1 - 0.39, TX1 - 0.09, z1 - 0.11, scr)
        text = {1: "4.50", 2: "...", 3: "APPROVED", 4: "DECLINED", 5: "ONE CARD"}.get(disp, "")
        if text:
            kit.plane_text(cam, "y", TY + 0.004, (TX0 + TX1) / 2, z1 - 0.25, text, 0.1 if len(text) > 5 else 0.14, max_w=TX1 - TX0 - 0.22, color=
                           (255, 255, 255))
        # contactless symbol
        cx, cz = (TX0 + TX1) / 2, z0 + 0.45
        on = g("field") > 0.5
        col = (120, 200, 255) if on else (150, 156, 170)
        for r in (0.07, 0.12, 0.17):
            pts = [(cx - 0.05 + math.cos(a) * r, TY + 0.004, cz + math.sin(a) * r)
                   for a in [(-0.8 + 1.6 * i / 10) for i in range(11)]]
            cam.line(pts, col, 0.018, caps=False)
        for j in range(3):
            parts.bolt(cam, (TX0 + 0.2 + j * 0.15, TY + 0.004, z0 + 0.1), 0.025, (120, 126, 140))
        parts.led(cam, (TX1 - 0.08, TY + 0.004, z1 - 0.03), (90, 230, 140) if disp == 3 else (255, 190, 60), True, 0.02)

    def _field(self, cam, t, k, rng, card_y, behind):
        col = (90, 160, 255)
        n = 6
        for i in range(n):
            f = ((t * 0.55) + i / n) % 1.0
            y = TY + 0.02 + rng * f
            if (y < card_y) != behind:
                continue
            r = (0.32 + 0.22 * f) * min(1.0, k)
            cc = mix(col, (255, 255, 255), 0.25 + 0.6 * f)
            cam.poly(cam.disc_pts((FIELD_C[0], y, FIELD_C[2]), r, "y", 40), None, cc, 0.022 * (1.2 - 0.7 * f))

    def _card(self, cam, tr, t, y, k, dx, dz, color, simple=False):
        g = lambda kk: tr.get(kk, t)
        if k <= 0.01:
            return
        chip, coil, body = (1, 1, 1) if simple else (g("chip"), g("coil"), g("body"))
        cx, cz = (CX0 + CX1) / 2 + dx, (CZ0 + CZ1) / 2 + dz
        w, h = (CX1 - CX0) * k, (CZ1 - CZ0) * k
        x0, x1, z0, z1 = cx - w / 2, cx + w / 2, cz - h / 2, cz + h / 2
        if body > 0.01:
            bw = w * _sm(body)
            cam.box(cx - bw / 2, y - 0.025, z0, bw, 0.025, h, color)
            kit.plate(cam, "y", y + 0.001, cx - bw / 2 + 0.02, z1 - 0.12, cx + bw / 2 - 0.02, z1 - 0.08,
                      shade(color, 0.25))
            if body > 0.9:
                kit.plane_text(cam, "y", y + 0.002, x0 + w * 0.3, z0 + h * 0.16, ".... 4821", 0.055 * k, max_w=w * 0.45, color=
                               (230, 236, 255))
                for r in (0.035, 0.06, 0.085):      # contactless mark
                    pts = [(x1 - 0.12 * k + math.cos(a) * r * k, y + 0.002, z1 - 0.2 * k + math.sin(a) * r * k)
                           for a in [(-0.8 + 1.6 * i / 8) for i in range(9)]]
                    cam.line(pts, (230, 236, 255), 0.01, caps=False)
        # antenna loop (drawn progressively around the card edge, 3 turns)
        power = g("power") if not simple else 0.0
        if coil > 0.01 and not simple:
            ccol = mix(COPPER, (255, 230, 90), power)
            for turn in range(3):
                m = (0.05 + 0.03 * turn) * k
                loop = [(x0 + m, y + 0.003, z0 + m), (x1 - m, y + 0.003, z0 + m), (x1 - m, y + 0.003, z1 - m),
                        (x0 + m, y + 0.003, z1 - m), (x0 + m, y + 0.003, z0 + m)]
                prog = min(1.0, max(0.0, coil * 3 - turn))
                if prog > 0.01:
                    cam.line(kit.sub_path(loop, 0.0, prog, 24), ccol, 0.014, caps=False)
            if power > 0.3:   # current flowing around the loop
                m = 0.08 * k
                loop = [(x0 + m, y + 0.004, z0 + m), (x1 - m, y + 0.004, z0 + m), (x1 - m, y + 0.004, z1 - m),
                        (x0 + m, y + 0.004, z1 - m), (x0 + m, y + 0.004, z0 + m)]
                for i in range(6):
                    p = kit.path_point(loop, (t * 0.5 + i / 6) % 1.0)[0]
                    kit.glow_dot(cam, p, 0.016, (255, 220, 80))
        if chip > 0.01:
            s = _sm(chip) * k
            ux, uz = x0 + 0.17 * k, z0 + h * 0.52
            cw, ch = 0.15 * s, 0.11 * s
            gcol = mix(GOLD, (255, 250, 200), 0.6 * power * (0.7 + 0.3 * math.sin(t * 9)))
            if power > 0.3:
                kit.glow_dot(cam, (ux, y + 0.004, uz), 0.09 * power, (255, 220, 90))
            kit.plate(cam, "y", y + 0.005, ux - cw / 2, uz - ch / 2, ux + cw / 2, uz + ch / 2, gcol,
                      shade(GOLD, -0.4), 0.008)
            cam.line([(ux - cw / 2, y + 0.006, uz), (ux + cw / 2, y + 0.006, uz)], shade(GOLD, -0.35), 0.006, caps=False)
            cam.line([(ux, y + 0.006, uz - ch / 2), (ux, y + 0.006, uz + ch / 2)], shade(GOLD, -0.35), 0.006, caps=False)
            if not simple and g("key") > 0.01:
                kk = _sm(g("key"))
                kx, kz = ux + 0.0, uz + 0.17
                px, py = cam.p(kx, y + 0.01, kz)
                r = 0.035 * cam.s * kk
                cam.d.ellipse((px - r, py - r, px + r, py + r), outline=(255, 200, 40), width=max(2, int(r * 0.45)))
                cam.d.line((px + r, py, px + r * 3.2, py), fill=(255, 200, 40), width=max(2, int(r * 0.45)))
                cam.d.line((px + r * 2.6, py, px + r * 2.6, py + r * 0.9), fill=(255, 200, 40), width=max(2, int(r * 0.4)))
            mixing = g("mixing") if not simple else 0.0
            if mixing > 0.05:     # digits swirling into the chip
                for i in range(5):
                    a = t * 4 + i * 1.256
                    rr = 0.2 * (1 - (t * 0.8 + i * 0.2) % 1.0)
                    p = (ux + math.cos(a) * rr, y + 0.01, uz + math.sin(a) * rr * 0.8)
                    kit.plane_text(cam, "y", y + 0.01, p[0], p[2], "0123456789"[(i * 3 + int(t * 6)) % 10],
                                   0.06 * mixing, (255, 210, 80))

    def _people(self, cam, tr, t, shop):
        g = lambda k: tr.get(k, t)
        expr = tr.peg_expr(t)
        pose = tr.peg_pose(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        th = g("thief")
        if th > 0.01:
            mad = g("thief_mad")
            kit.peg(cam, (3.95, 1.95, 0), (120, 120, 130), "angry" if mad > 0.5 else "smug", t, 1.9 * th, (-0.5, -0.3),
                    seed=7, pose="hold", floor=FLOOR, hat=True)
            cam.box(3.45, 1.6, 0.78, 0.22, 0.16, 0.3, (30, 32, 40))           # the hidden reader
            parts.led(cam, (3.56, 1.77, 1.0), (255, 70, 70), int(t * 4) % 2 == 0, 0.02)
            cam.line([(3.56, 1.68, 1.08), (3.6, 1.68, 1.32)], (30, 32, 40), 0.012)
            st = g("steal")
            if st > 0.01:
                src = (2.6, TY + g("gap"), 1.55)
                dst = (3.56, 1.68, 1.0)
                for i in range(4):
                    f = (t * 0.7 + i / 4) % 1.0
                    p = tuple(src[j] + (dst[j] - src[j]) * f for j in range(3))
                    x, y = cam.p(*p)
                    cam.d.text((x, y), "4821"[i], font=kit.font(int(0.11 * cam.s * st)), fill=RED, anchor="mm")
            rp = g("replay")
            if 0.01 < rp < 0.99:
                kit.packet(cam, [(3.56, 1.68, 1.05), (3.0, 1.2, 1.5), (2.5, TY + 0.05, 1.6)], rp, RED, 0.06)
        cu = g("cust")
        if cu > 0.01:
            kit.peg(cam, (2.3, 2.15, 0), PEG_COLORS[0], expr, t, 2.0 * cu, (0.0, -0.6), seed=1,
                    pose=pose if pose != "cheer" or since > 0.3 else "cheer", react=react, floor=FLOOR)
        q = g("queue")
        if q > 0.01:
            kit.peg(cam, (2.35, 3.7, 0), PEG_COLORS[3], "shocked" if g("qcard") > 0.5 else "neutral", t, 2.0 * q,
                    (0.0, -0.6), seed=2, floor=FLOOR)
            qc = g("qcard")
            x0, z0 = 2.62, 0.45
            kit.plate(cam, "y", 3.72, x0, z0, x0 + 0.3, z0 + 0.19, mix(CARD, (255, 230, 90), qc), shade(CARD, -0.4))
            if qc > 0.3:
                kit.glow_dot(cam, (x0 + 0.06, 3.73, z0 + 0.1), 0.03, (255, 220, 80))

    def _network(self, cam, tr, t, net):
        g = lambda k: tr.get(k, t)
        k = _sm(net)
        for i, (bx, name) in enumerate(BUILDINGS):
            kb = _sm(net * 1.6 - i * 0.3)
            if kb <= 0.01:
                continue
            cam.poly([(bx - 0.3, -0.7, 0), (bx + 1.9, -0.7, 0), (bx + 1.9, 1.5, 0), (bx - 0.3, 1.5, 0)],
                     (206, 228, 196), shade((206, 228, 196), -0.2), 0.01)
        cam.line([(3.45, 0.3, 0.0), (5.2, 0.3, 0.0)], (70, 76, 92), 0.035 * k)
        for p in (PATH2, PATH3):
            kit.cable(cam, p, lit=0.0, width=0.035 * k)
        for i, (bx, name) in enumerate(BUILDINGS):
            kb = _sm(net * 1.6 - i * 0.3)
            if kb <= 0.01:
                continue
            glow = g("b%d" % (i + 1))
            h = 2.3 * kb
            if i == 1:
                cam.box(bx, -0.4, 0, 1.6, 1.4, 0.12, (90, 96, 110))
                for j in range(3):
                    parts.server_rack(cam, bx + 0.15 + j * 0.48, -0.25, 0.12, 0.4, 0.6, 1.5 * kb, t, busy=0.3 + 0.6 * glow,
                                      seed=j)
                # globe
                gc = (bx + 0.8, 0.3, 0.12 + 1.5 * kb + 0.55)
                cam.poly(cam.disc_pts(gc, 0.42 * kb, "y", 36), mix((90, 150, 230), (140, 210, 255), glow),
                         (40, 70, 140), 0.012)
                cam.poly(cam.disc_pts(gc, 0.42 * kb, "x", 36), None, (230, 240, 255), 0.01)
                cam.line([(gc[0] - 0.42 * kb * 0.866, gc[1] + 0.21, gc[2]), (gc[0] + 0.42 * kb * 0.866, gc[1] - 0.21, gc[2])],
                         (230, 240, 255), 0.01)
            else:
                parts.bank_building(cam, bx, -0.4, 1.6, 1.4, h, (225, 228, 238) if i == 0 else (244, 230, 206),
                                    (120, 128, 150) if i == 0 else (180, 120, 80), t, glow)
            if kb > 0.8:
                kit.label(cam, (bx + 0.8, 0.3, 3.25), name, 0.3, INK if glow < 0.5 else (255, 255, 255),
                          (255, 255, 255) if glow < 0.5 else (60, 140, 230))
        sc = g("scan")
        if sc > 0.01:
            z = 0.4 + 1.4 * (0.5 + 0.5 * math.sin(t * 3))
            cam.poly([(9.95, -0.45, z), (11.65, -0.45, z), (11.65, 1.05, z), (9.95, 1.05, z)], None,
                     (90, 220, 140), 0.02 * sc)

    def _packets(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        for key, pts in (("pk1", PATH1), ("pk2", PATH2), ("pk3", PATH3)):
            kit.packet(cam, pts, g(key), (60, 140, 255), 0.09)
        r = g("ret")
        if 0.01 < r < 0.99:
            full = list(reversed(PATH3)) + list(reversed(PATH2)) + list(reversed(PATH1))
            p, _ = kit.path_point(full, r)
            inside = any(bx < p[0] < bx + 1.6 for bx, _n in BUILDINGS)
            if not inside:
                kit.packet(cam, full, r, (60, 200, 110), 0.1, 0.05)


VIDEO = dict(
    slug="card_tap",
    title="How does a card pay in 1 second with no battery?",
    steps=STEPS, scene=CardScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"),
)
