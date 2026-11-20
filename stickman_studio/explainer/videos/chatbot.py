"""How does an AI chatbot write its answer word by word? - built step by step."""
from __future__ import annotations

import math

from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

WIDE = ((0.2, 1.0, 1.4), 135)
BELT = ((-2.9, 0.9, 1.0), 150)
MACH = ((1.2, 1.4, 1.2), 190)

STEPS = [
    dict(text="If you build a machine that reads a sentence and guesses the next word, you've got the world's "
              "simplest AI chatbot.",
         cam=((1.2, 1.2, 1.1), 250), pegs="neutral",
         cams=[("w:reads", ((-1.4, 0.9, 1.0), 200), 1.0), ("w:guesses", ((2.6, 0.9, 1.0), 210), 0.9),
               ("w:simplest", WIDE, 1.4)],
         do=[("machine", 0.0, 1, 0.7, "back"), ("words", "w:reads", 1, 0.9, "out"), ("gen", "w:guesses", 0.3, 0.6, "out"),
             ("room", "w:simplest", 1, 1.3, "out")],
         keys=[("machine", INK), ("reads a sentence", INK), ("next word|guesses the next word", BLUE),
               ("simplest AI chatbot", BLUE)],
         sfx=[("w:machine", "pop"), ("w:guesses", "pop"), ("w:simplest", "whoosh")]),
    dict(text="Then you feed its own guess back in and ask again. And again. That's why chatbots type one word at a "
              "time.",
         cam=((1.0, 0.9, 1.9), 128), pegs="happy",
         do=[("loop", "w:feed", 1, 0.6, "out"), ("gen", "w:feed", 1.0, 1.2, "io"), ("gen", "w:again", 2.0, 1.2, "io"),
             ("gen", "w:why", 3.0, 1.2, "io")],
         keys=[("its own guess|feed it back in", INK), ("one word at a time", BLUE)],
         fix="w:feed",
         sfx=[("w:feed", "whoosh"), ("w:why", "pop")]),
    dict(text="But a brand new machine is clueless. Its guesses are pure garbage. Banana. Seven. Purple.",
         cam=((2.4, 1.0, 1.2), 175), pegs="shocked",
         do=[("junk", "w:banana", 1, 0, "lin"), ("junk", "w:seven", 2, 0, "lin"), ("junk", "w:purple", 3, 0, "lin"),
             ("smoke", "w:garbage", 1, 0.4, "out")],
         keys=[("brand new|brand new = clueless", INK), ("pure garbage", RED), ("banana|banana?", RED),
               ("seven|seven??", RED), ("purple|purple???", RED)],
         sfx=[("w:banana", "boing"), ("w:seven", "boing"), ("w:purple", "boing")]),
    dict(text="So you feed it a mountain of text from books and websites, hide the next word, and make it guess. Over "
              "and over, billions of times. That's training.",
         cam=((-1.6, 1.6, 1.3), 120), pegs="neutral",
         do=[("smoke", 0, 0, 0.3, "in"), ("books", "w:mountain", 1, 0.9, "back"), ("train", "w:hide", 1, 0.4, "out")],
         keys=[("mountain of text", INK), ("hide the next word", INK), ("billions of times", INK), ("training", INK)],
         fix="w:training",
         pops=[dict(kind="note", at="w:hide", text="guess the hidden word", pos="bc", until="w:over")],
         sfx=[("w:mountain", "whoosh")]),
    dict(text="Every wrong guess slightly turns every one of the tiny dials inside the machine. Those dials are the "
              "parameters, and big models have billions of them.",
         cam=((1.2, 1.8, 1.2), 230), pegs="neutral",
         do=[("dials", "w:turns", 1, "end", "lin"), ("loss", 0.2, 0.18, "end", "out")],
         keys=[("wrong guess", RED), ("tiny dials", INK), ("parameters", INK), ("billions of them", INK)],
         fix="w:parameters",
         pops=[dict(kind="graph", at=0.3, title="WRONG GUESSES", track="loss", window=7.0, color=RED, pos="bc",
                    until="end+0.3")]),
    dict(text="It's like learning to cook by tasting the soup and tweaking the recipe, a few trillion times.",
         cam=((1.2, 1.8, 1.2), 210), pegs="happy", pose="think",
         do=[("soup", "w:cook", 1, 0.4, "back"), ("soup", "end-0.3", 0, 0.3, "in"), ("dials", "end", 2, 0.01, "lin")],
         keys=[("tasting the soup", INK), ("tweaking the recipe", INK), ("few trillion times", BLUE)]),
    dict(text="Doing all that math on a normal computer would take forever. So it runs on thousands of graphics chips "
              "that each do trillions of multiplications every second.",
         cam=((1.0, -0.6, 1.8), 120), pegs="worried",
         do=[("gpus", "w:graphics", 1, 1.0, "out")],
         keys=[("take forever", RED), ("graphics chips", INK), ("trillions|trillions per second", BLUE)],
         fix="w:graphics",
         pops=[dict(kind="bars", at="w:normal", title="TIME TO TRAIN", until="end+0.2", pos="bc",
                    items=[("one computer", 1.0, RED), ("GPU farm", 0.05, GREEN)])],
         sfx=[("w:graphics", "whoosh")]),
    dict(text="Now it writes smooth sentences, until it reads this. The trophy didn't fit in the suitcase because it "
              "was too big. What was too big?",
         cam=BELT, pegs="worried", pose="think",
         keys=[("smooth sentences", BLUE), ("what was too big|what was too big?", RED)],
         sfx=[("w:what", "sting")]),
    dict(text="So before guessing, every word gets to look back at every other word and decide which ones matter. "
              "That's attention. The word it links straight to the trophy.",
         cam=BELT, pegs="happy",
         do=[("attn", "w:look", 1, 1.0, "out"), ("focus", "w:links", 1, 0.6, "out")],
         keys=[("look back", INK), ("which ones matter", INK), ("attention", INK), ("trophy|it = the trophy", BLUE)],
         fix="w:attention",
         sfx=[("w:attention", "ding")]),
    dict(text="But the machine can't actually read letters. It only does math on numbers.",
         cam=((-2.0, 0.9, 1.1), 200), pegs="worried",
         do=[("attn", 0, 0, 0.3, "in"), ("focus", 0, 0, 0.3, "in"), ("confused", "w:letters", 1, 0.3, "out")],
         keys=[("can't actually read|can't read letters", RED), ("numbers|only numbers", INK)]),
    dict(text="So text gets chopped into chunks, whole words or pieces of words, and each chunk gets a number. Those "
              "are tokens.",
         cam=((-2.0, 0.9, 1.1), 200), pegs="happy",
         do=[("confused", 0.2, 0, 0.3, "in"), ("split", "w:chopped", 1, 0.6, "back"), ("ids", "w:number", 1, 0.5, "out")],
         keys=[("chopped into chunks", INK), ("pieces of words", INK), ("tokens", INK)],
         fix="w:tokens",
         pops=[dict(kind="arrow", at="w:tokens", xyz=(-1.9, 1.17, 1.2), text="3 tokens", color=BLUE, off=(0.1, -0.13),
                    until="end+0.3", sound=False)],
         sfx=[("w:chopped", "slap")]),
    dict(text="Next problem. If it always picks the single most likely word, it gets boring and repetitive. Very, "
              "very, very boring.",
         cam=((2.6, 1.6, 1.3), 150), pegs="neutral", pose="idle",
         do=[("very", "w:boring", 1, 0, "lin"), ("very", "w:very", 2, 0, "lin"), ("very", "end-0.9", 3, 0, "lin")],
         keys=[("most likely word", INK), ("boring and repetitive", RED)]),
    dict(text="So it rolls weighted dice. Likely words win most of the time, but not always. A setting called "
              "temperature decides how wild it gets.",
         cam=MACH, pegs="happy",
         do=[("very", 0, 0, 0, "lin"), ("dice", "w:rolls", 1, 0.5, "back"), ("roll", "w:rolls", 1, 1.6, "out"),
             ("roll", "w:temperature", 2, 1.6, "out")],
         keys=[("weighted dice", INK), ("not always", INK), ("temperature", INK)],
         fix="w:dice",
         pops=[dict(kind="bars", at="w:likely", title="NEXT WORD", until="w:temperature-0.1", pos="bc",
                    items=[("mat", 0.62, GREEN), ("floor", 0.2, BLUE), ("moon", 0.04, RED)]),
               dict(kind="meter", at="w:temperature", text="TEMPERATURE", **{"from": 0.15, "to": 0.7}, color=ORANGE,
                    fmt="WILDER", pos="bc", until="end+0.3")],
         sfx=[("w:rolls", "click")]),
    dict(text="Then you ask it a question, and it just answers with more questions, like a random internet forum.",
         cam=((3.4, 2.2, 1.4), 150), pegs="worried",
         do=[("dice", 0, 0, 0.3, "in"), ("forum", "w:answers", 1, 0.4, "out")],
         keys=[("ask it a question", INK), ("more questions", RED), ("internet forum", RED)],
         pops=[dict(kind="warn", at="w:more", text="not an assistant", pos="bc", until="end+0.3")]),
    dict(text="So you train it again on example conversations, and people rate its answers. Good answers get "
              "rewarded. That's fine-tuning with human feedback.",
         cam=((3.0, 2.0, 1.4), 150), pegs="happy",
         do=[("forum", "w:train", 2, 0, "lin"), ("raters", "w:people", 1, 0.5, "back")],
         keys=[("example conversations", INK), ("rate its answers", INK), ("rewarded", BLUE), ("human feedback", INK)],
         fix="w:rate",
         sfx=[("w:rewarded", "ding")]),
    dict(text="But it can only look back so far. That limit is the context window. Paste in a whole book, and the "
              "beginning falls off the edge.",
         cam=((-2.0, 0.9, 1.0), 150), pegs="shocked",
         do=[("raters", 0, 0, 0.3, "in"), ("ctx", "w:limit", 1, 0.5, "out"), ("fall", "w:falls", 1, 1.0, "in")],
         keys=[("look back so far", INK), ("context window", INK), ("falls off|beginning falls off", RED)],
         sfx=[("w:falls", "whoosh")]),
    dict(text="And because it predicts what sounds right instead of checking facts, it can be wrong with total "
              "confidence. That's a hallucination.",
         cam=((2.2, 1.2, 1.1), 190), pegs="worried",
         do=[("ctx", 0, 0, 0.3, "in"), ("fall", 0, 0, 0.01, "lin"), ("halluc", "w:wrong", 1, 0.4, "back")],
         keys=[("sounds right", INK), ("total confidence", RED), ("hallucination", RED)],
         pops=[dict(kind="stamp", at="w:hallucination", text="CONFIDENTLY WRONG", color=RED, pos="mr",
                    until="end+0.3")],
         sfx=[("w:wrong", "sting")]),
    dict(text="So next time a chatbot types its answer word by word, you'll know each word is a fresh guess, built on "
              "every word before it.",
         cam=((1.0, 0.9, 1.9), 128), pegs="happy",
         do=[("halluc", 0, 0, 0.3, "in"), ("gen", "w:types", 4.0, 1.3, "io"), ("gen", "w:fresh", 5.0, 1.3, "io")],
         keys=[("word by word", INK), ("fresh guess", BLUE), ("every word before it", INK)]),
    dict(text="And congratulations, you just built an AI chatbot. Now you just need it to admit when it doesn't know. "
              "Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("gen", 1.0, 6.0, 2.5, "io")],
         keys=[("built an AI chatbot|you built an AI chatbot!", BLUE), ("doesn't know|\"I don't know\"", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(machine=0, words=0, gen=0, room=0, loop=0, junk=0, smoke=0, books=0, train=0, dials=0, loss=1.0,
               soup=0, gpus=0, attn=0, focus=0, confused=0, split=0, ids=0, very=0, dice=0, roll=0, forum=0,
               raters=0, ctx=0, fall=0, halluc=0)

BG_TOP, BG_BOT = (226, 232, 250), (248, 244, 252)
FLOOR = (226, 228, 240)
WALL = (238, 236, 248)
WALL2 = (224, 222, 238)
MCOL = (118, 96, 214)
BLOCK = (255, 250, 236)

MX0, MX1, MY0, MY1, MH = 0.0, 2.4, 0.0, 1.8, 2.2
BY0, BY1, BZ = 0.6, 1.2, 0.55           # belt band (y) and belt top height
IN_X0 = -5.9
OUT_X1 = 5.0
LOOP = [(4.6, 0.9, 1.1), (4.6, 0.9, 3.0), (-1.2, 0.9, 3.0), (-1.2, 0.9, 1.0)]

BASE = ["The", "cat", "sat", "on", "the"]
GEN = ["mat", "and", "it", "purred", "all", "day"]
TRAIN = [["Once", "upon", "a"], ["Paris", "is", "in"], ["Water", "boils", "at"]]
TRAIN_OUT = [("time", True), ("pizza", False), ("France", True), ("100", True)]
TROPHY = ["trophy", "didn't fit", "suitcase", "because", "it", "too big"]
LONG = ["Chapter", "one", "It", "was", "a", "dark", "and", "stormy", "night", "..."]
JUNK = ["banana", "seven", "purple"]


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def bw(word):
    return 0.16 + 0.095 * len(word)


class ChatScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, BG_TOP, BG_BOT, clouds=0)

    # ------------------------------------------------------------- content per step
    def _content(self, tr, t, step_i, step_t):
        """-> (input words, output word, output colour, extra flags)"""
        g = lambda k: tr.get(k, t)
        gen = g("gen")
        n = int(gen)
        if step_i in (0, 1, 17, 18):
            n = min(n, len(GEN))
            inp = BASE + GEN[:n]
            return inp[-7:], None, None
        if step_i == 2:
            j = int(round(g("junk")))
            return BASE, (JUNK[j - 1] if j else None), RED
        if step_i in (3, 4, 5, 6):
            k = int(step_t / 2.2) % 3
            if g("train") < 0.5:
                return BASE, None, None
            word, ok = TRAIN_OUT[(int(step_t / 1.1)) % 4]
            return TRAIN[k], word, GREEN if ok else RED
        if step_i in (7, 8):
            return TROPHY, None, None
        if step_i in (9, 10):
            return ["unbelievable"], None, None
        if step_i == 11:
            v = int(round(g("very")))
            return ["it", "was"] + ["very"] * v, "very", ORANGE
        if step_i == 12:
            return BASE, ("mat" if int(step_t * 1.3) % 3 else "floor"), BLUE
        if step_i in (13, 14):
            f = int(round(g("forum")))
            inp = ["How", "do", "I", "bake", "bread?"]
            if f == 1:
                return inp, "Why?", RED
            if f == 2:
                return inp, "Mix", GREEN
            return inp, None, None
        if step_i == 15:
            return LONG, None, None
        if step_i == 16:
            return ["first", "person", "on", "Mars", "was"], ("Neil" if g("halluc") > 0.3 else None), RED
        return BASE, None, None

    # ------------------------------------------------------------- main
    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        room = g("room")
        mach = g("machine")
        self._room(cam, tr, t, room)
        if g("gpus") > 0.01:
            self._gpus(cam, tr, t)
        if g("books") > 0.01:
            self._books(cam, t, g("books"), 3 <= step_i <= 6)
        inp, out, ocol = self._content(tr, t, step_i, step_t)
        self._belts(cam, tr, t, mach)
        self._input(cam, tr, t, step_i, step_t, inp, mach)
        if mach > 0.6:
            expr = tr.peg_expr(t)
            since = tr.since_step(t)
            react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
            kit.peg(cam, (-0.7, 2.4, 0), PEG_COLORS[0], expr, t, 1.9 * _sm((mach - 0.6) * 2.5), (0.5, -0.3), seed=1,
                    pose=tr.peg_pose(t), react=react, floor=FLOOR)
        if mach > 0.01:
            self._machine(cam, tr, t, mach)
        self._output(cam, tr, t, step_i, step_t, out, ocol)
        if g("loop") > 0.01:
            self._loop(cam, tr, t)
        if room > 0.01:
            self._desk(cam, tr, t, step_i, room)
        if g("raters") > 0.01:
            self._raters(cam, tr, t, g("raters"))

    # ------------------------------------------------------------- pieces
    def _room(self, cam, tr, t, room):
        a = _sm(room)
        cam.poly([(-6, -3.2, 0), (7, -3.2, 0), (7, 6.6, 0), (-6, 6.6, 0)], FLOOR)
        for k in range(1, 22):
            cam.line([(-6 + k * 0.62, -3.2, 0), (-6 + k * 0.62, 6.6, 0)], shade(FLOOR, -0.05), 0.006, caps=False)
        for k in range(1, 16):
            cam.line([(-6, -3.2 + k * 0.62, 0), (7, -3.2 + k * 0.62, 0)], shade(FLOOR, -0.05), 0.006, caps=False)
        h = 4.2 * a
        sh = ShadowLayer(cam)
        if h > 0.05:
            cam.poly([(-6, -3.2, 0), (7, -3.2, 0), (7, -3.2, h), (-6, -3.2, h)], WALL, shade(WALL, -0.25), 0.01)
            cam.poly([(-6, -3.2, 0), (-6, 6.6, 0), (-6, 6.6, h), (-6, -3.2, h)], WALL2, shade(WALL, -0.3), 0.01)
            if h > 3.5:
                kit.plate(cam, "y", -3.19, -4.6, 2.6, -1.4, 3.6, (60, 50, 120), shade((60, 50, 120), -0.4))
                kit.plane_text(cam, "y", -3.18, -3.0, 3.1, "WORD LAB", 0.38, (255, 255, 255))
            sh.ao_edge((-6, -3.2, 0), (7, -3.2, 0), (0, 1, 0), (0, 0, 1), 0.3, 140)
            sh.ao_edge((-6, -3.2, 0), (-6, 6.6, 0), (1, 0, 0), (0, 0, 1), 0.3, 140)
        m = _sm(tr.get("machine", t))
        if m > 0.05:
            sh.box_on_plane(MX0, MY0, 0, MX1 - MX0, MY1 - MY0, MH * m, "z", 0.0, 230)
            sh.box_on_plane(IN_X0, BY0 - 0.05, 0, -IN_X0, BY1 - BY0 + 0.1, BZ, "z", 0.0, 150)
            sh.box_on_plane(MX1, BY0 - 0.05, 0, OUT_X1 - MX1, BY1 - BY0 + 0.1, BZ, "z", 0.0, 150)
        sh.apply(cam.img, 0.28, 2.6)

    def _belts(self, cam, tr, t, mach):
        k = _sm(mach)
        if k <= 0.01:
            return
        for x0, x1 in ((IN_X0, -0.02), (MX1 + 0.02, OUT_X1)):
            xa = x1 - (x1 - x0) * k if x0 < 0 else x0
            xb = x1 if x0 < 0 else x0 + (x1 - x0) * k
            for lx in (xa + 0.2, xb - 0.3):
                cam.box(lx, BY0 + 0.05, 0, 0.1, 0.1, BZ - 0.15, (90, 94, 110))
                cam.box(lx, BY1 - 0.15, 0, 0.1, 0.1, BZ - 0.15, (90, 94, 110))
            cam.box(xa, BY0, BZ - 0.15, xb - xa, BY1 - BY0, 0.15, (64, 68, 84), top_color=(84, 88, 104))
            off = (t * 0.6) % 0.3
            xx = xa + off
            while xx < xb:
                cam.line([(xx, BY0, BZ + 0.001), (xx, BY1, BZ + 0.001)], (104, 108, 124), 0.012, caps=False)
                xx += 0.3

    def _block(self, cam, x, word, k=1.0, color=BLOCK, txt=INK, z=None, tilt=0.0, ids=None):
        if k <= 0.01:
            return
        w = bw(word)
        h = 0.42 * k
        z = BZ if z is None else z
        y0, d = BY0 + 0.05, (BY1 - BY0 - 0.1)
        cam.box(x, y0, z, w * k, d, h, color, top_color=shade(color, 0.05) if color != BLOCK else (246, 246, 252))
        if k > 0.6:
            kit.plane_text(cam, "y", y0 + d + 0.002, x + w * k / 2, z + h * 0.5, word, 0.15 * k, txt, max_w=bw(word) * k - 0.08)
        if ids is not None:
            kit.label(cam, (x + w / 2, y0 + d, z - 0.22), ids, 0.13, (255, 255, 255), BLUE)

    def _layout(self, words, end_x=-0.9, gap=0.1):
        xs = []
        x = end_x
        for wd in reversed(words):
            x -= bw(wd)
            xs.append(x)
            x -= gap
        return list(reversed(xs))

    def _input(self, cam, tr, t, step_i, step_t, words, mach):
        g = lambda k: tr.get(k, t)
        wk = g("words")
        if wk <= 0.01 or mach < 0.3:
            return
        pop = _sm(step_t / 0.4) if step_i not in (0, 1, 17, 18) else 1.0
        if step_i in (9, 10):
            sp = g("split")
            if sp < 0.5:
                xs = self._layout(words)
                self._block(cam, xs[0], words[0], pop * (1 - sp * 2) if sp > 0 else pop,
                            (255, 236, 236) if g("confused") > 0.5 else BLOCK)
                if g("confused") > 0.3:
                    for i in range(3):
                        kit.plane_text(cam, "y", 1.2, xs[0] + 0.4 + i * 0.35, 1.35 + 0.08 * math.sin(t * 5 + i), "?",
                                       0.3, RED)
            else:
                parts_ = ["un", "believ", "able"]
                ids = ["403", "8721", "481"]
                xs = self._layout(parts_, gap=0.25)
                kk = _sm((sp - 0.5) * 2)
                for i, (x, w) in enumerate(zip(xs, parts_)):
                    self._block(cam, x, w, kk, mix(BLOCK, PEG_COLORS[i], 0.35),
                                ids=ids[i] if g("ids") > 0.5 else None)
            return
        xs = self._layout(words)
        n_gen = int(g("gen")) if step_i in (0, 1, 17, 18) else 0
        for i, (x, w) in enumerate(zip(xs, words)):
            k = min(1.0, max(0.0, wk * len(words) - i)) * pop
            z = None
            color = BLOCK
            if step_i in (0, 1, 17, 18) and i >= len(words) - n_gen:
                color = (226, 240, 255)
            if step_i == 15:
                inside = i >= len(words) - 5
                if not inside:
                    f = g("fall")
                    x = x - 0.6 * f
                    z = BZ - 2.0 * f * f
                    if z < -0.4:
                        continue
                    color = (255, 226, 226)
            if step_i == 16 and w == "Mars":
                color = (255, 236, 220)
            if step_i in (7, 8) and g("focus") > 0.3 and w in ("trophy", "it"):
                color = mix(BLOCK, (255, 214, 90), g("focus"))
            self._block(cam, x, w, k, color, z=z)
        if step_i in (7, 8):
            self._attention(cam, tr, t, xs, words)
        if step_i == 15 and g("ctx") > 0.01:
            c = _sm(g("ctx"))
            x0 = xs[len(words) - 5] - 0.08
            x1 = -0.15
            z0, z1 = BZ - 0.05, BZ + 0.6
            y = BY1 + 0.02
            col = (255, 150, 40)
            pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1), (x0, y, z0)]
            cam.line(kit.sub_path(pts, 0, c, 20), col, 0.03)
            if c > 0.9:
                kit.label(cam, ((x0 + x1) / 2, y, z1 + 0.25), "CONTEXT WINDOW", 0.15, (255, 255, 255), col)

    def _attention(self, cam, tr, t, xs, words):
        g = lambda k: tr.get(k, t)
        a = g("attn")
        if a <= 0.01:
            return
        i_it = words.index("it")
        src = (xs[i_it] + bw("it") / 2, BY0 + 0.3, BZ + 0.45)
        focus = g("focus")
        for j, w in enumerate(words):
            if j == i_it:
                continue
            dst = (xs[j] + bw(w) / 2, BY0 + 0.3, BZ + 0.45)
            weight = {"trophy": 1.0, "too big": 0.55, "suitcase": 0.35}.get(w, 0.15)
            if focus > 0.3:
                weight = weight if w == "trophy" else weight * (1 - 0.7 * focus)
            hgt = 0.35 + 0.35 * abs(dst[0] - src[0])
            pts = []
            for k in range(17):
                f = k / 16
                pts.append((src[0] + (dst[0] - src[0]) * f, src[1], src[2] + math.sin(f * math.pi) * hgt))
            col = mix((150, 170, 210), (255, 150, 30), weight)
            cam.line(kit.sub_path(pts, 0, min(1.0, a * 1.3), 16), col, 0.012 + 0.035 * weight)
            if a > 0.9 and weight > 0.9:
                kit.glow_dot(cam, dst, 0.05, (255, 160, 40))

    def _machine(self, cam, tr, t, mach):
        g = lambda k: tr.get(k, t)
        k = _sm(mach)
        h = MH * k
        shake = 0.03 * math.sin(t * 40) if g("smoke") > 0.5 else 0.0
        x0 = MX0 + shake
        cam.box(x0, MY0, 0, MX1 - MX0, MY1 - MY0, 0.15, shade(MCOL, -0.35))
        cam.box(x0 + 0.05, MY0 + 0.05, 0.15, MX1 - MX0 - 0.1, MY1 - MY0 - 0.1, h - 0.15, MCOL)
        if k < 0.9:
            return
        # dial panel (the parameters)
        y = MY1 - 0.05 + 0.002
        kit.plate(cam, "y", y, 0.2, 0.35, 2.2, 1.95, shade(MCOL, -0.3), shade(MCOL, -0.5))
        dials = g("dials")
        for r in range(4):
            for c in range(6):
                cx, cz = 0.42 + c * 0.32, 0.55 + r * 0.38
                cam.poly(cam.disc_pts((cx, y + 0.003, cz), 0.12, "y", 20), (236, 232, 250), (60, 50, 110), 0.008)
                ang = 0.6 * math.sin(r * 2.1 + c * 1.3) + dials * (2.5 + ((r * 7 + c * 3) % 5)) * 0.9
                tip = (cx + math.cos(ang) * 0.09, y + 0.004, cz + math.sin(ang) * 0.09)
                cam.line([(cx, y + 0.004, cz), tip], (226, 52, 64), 0.014)
        # output slot on the right face + input slot glow
        kit.plate(cam, "x", MX1 - 0.05 + 0.002, BY0, BZ - 0.02, BY1, BZ + 0.6, (30, 28, 50))
        # top: name plate + lights
        kit.label(cam, ((MX0 + MX1) / 2, (MY0 + MY1) / 2, MH + 0.45), "NEXT-WORD MACHINE", 0.16, (255, 255, 255),
                  shade(MCOL, -0.35))
        for i in range(4):
            parts.led(cam, (0.35 + i * 0.5, MY1 - 0.04, 2.05), (90, 230, 140) if int(t * 3 + i) % 2 else (255, 200, 60),
                      True, 0.03)
        if g("smoke") > 0.01:
            for i in range(5):
                f = (t * 0.6 + i / 5) % 1.0
                p = (1.2 + 0.3 * math.sin(i * 2 + t), 0.9, MH + 0.2 + f * 1.4)
                x, yy = cam.p(*p)
                r = (0.12 + 0.25 * f) * cam.s * g("smoke")
                c = mix((120, 120, 130), (240, 240, 245), f)
                cam.d.ellipse((x - r, yy - r, x + r, yy + r), fill=c)
        d = g("dice")
        if d > 0.01:
            roll = g("roll")
            hop = abs(math.sin(roll * math.pi * 3)) * 0.5 * (1 if roll % 1 > 0.02 else 0)
            s = 0.42 * _sm(d)
            cam.box(1.0, 0.7, MH + hop, s, s, s, (255, 255, 255))
            face = 1 + int(roll * 7) % 6
            cx, cz = 1.0 + s / 2, MH + hop + s / 2
            for (du, dv) in {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
                             4: [(-1, -1), (1, 1), (-1, 1), (1, -1)], 5: [(-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)],
                             6: [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0)]}[face]:
                x, yy = cam.p(cx + du * s * 0.27, 0.7 + s + 0.003, cz + dv * s * 0.27)
                r = 0.035 * cam.s
                cam.d.ellipse((x - r, yy - r, x + r, yy + r), fill=(30, 30, 40))

    def _output(self, cam, tr, t, step_i, step_t, out, ocol):
        g = lambda k: tr.get(k, t)
        if step_i in (0, 1, 17, 18):
            gen = g("gen")
            n, f = int(gen), gen - int(gen)
            if gen <= 0.01 or n >= len(GEN):
                return
            word = GEN[n]
            if f < 0.45 and (n > 0 or f > 0.01):
                prog = _sm(f / 0.45) if n > 0 or step_i else _sm(f / 0.3)
                x = MX1 - 0.4 + prog * 1.6
                self._block(cam, x, word, 1.0, (226, 240, 255))
            return
        if out is None:
            return
        prog = _sm(step_t / 0.6)
        x = MX1 - 0.4 + prog * 1.4
        txt = (255, 255, 255) if ocol in (RED, GREEN, BLUE, ORANGE) else INK
        self._block(cam, x, out, 1.0, ocol, txt)
        if step_i in (3, 4, 5, 6) and prog > 0.9:
            ok = ocol == GREEN
            px, py = cam.p(x + bw(out) / 2, BY1, BZ + 0.85)
            r = 0.13 * cam.s
            cam.d.ellipse((px - r, py - r, px + r, py + r), fill=ocol, outline=(255, 255, 255), width=max(2, int(r * 0.15)))
            if ok:
                cam.d.line([(px - r * 0.45, py), (px - r * 0.1, py + r * 0.4), (px + r * 0.5, py - r * 0.4)],
                           fill=(255, 255, 255), width=max(2, int(r * 0.22)))
            else:
                for sgn in (-1, 1):
                    cam.d.line([(px - r * 0.4, py - sgn * r * 0.4), (px + r * 0.4, py + sgn * r * 0.4)],
                               fill=(255, 255, 255), width=max(2, int(r * 0.22)))

    def _loop(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("loop"))
        pts = kit.sub_path(LOOP, 0, k, 30)
        cam.line(pts, (170, 200, 240), 0.13)
        cam.line(pts, (225, 238, 255), 0.09)
        if k > 0.95:
            for i in range(5):     # flow arrows
                p, tan = kit.path_point(LOOP, (t * 0.25 + i / 5) % 1.0)
                q = tuple(p[j] - tan[j] * 0.12 for j in range(3))
                cam.line([q, p], (90, 140, 230), 0.035)
        gen = g("gen")
        n, f = int(gen), gen - int(gen)
        if 0.45 < f < 0.99 and n < len(GEN):
            p, _ = kit.path_point(LOOP, (f - 0.45) / 0.54)
            kit.label(cam, p, GEN[n], 0.15, BLUE, (226, 240, 255))

    def _desk(self, cam, tr, t, step_i, room):
        g = lambda k: tr.get(k, t)
        a = _sm(room * 1.4 - 0.3)
        if a <= 0.01:
            return
        x0, y0 = 2.4, 4.3
        cam.box(x0, y0, 0, 2.0, 0.9, 0.7 * a, (190, 150, 110))
        if a < 0.9:
            return
        cam.box(x0 + 0.5, y0 + 0.25, 0.7, 1.1, 0.12, 0.06, (40, 44, 56))
        cam.box(x0 + 0.95, y0 + 0.28, 0.76, 0.2, 0.06, 0.2, (40, 44, 56))
        sy = y0 + 0.33
        kit.plate(cam, "y", sy, x0 + 0.2, 0.95, x0 + 1.8, 1.85, (30, 32, 44), (10, 10, 14), 0.01)
        kit.plate(cam, "y", sy + 0.001, x0 + 0.27, 1.02, x0 + 1.73, 1.78, (246, 248, 255))
        # chat bubbles
        if step_i in (13, 14):
            lines = [("How do I bake bread?", (220, 232, 255))]
            if g("forum") > 0.5 and g("forum") < 1.5:
                lines.append(("Why bake? Who bakes?", (255, 226, 226)))
            elif g("forum") >= 1.5:
                lines.append(("Mix flour, water...", (220, 250, 228)))
        elif step_i == 11:
            lines = [("it was " + " ".join(["very"] * int(round(g("very")))), (255, 236, 210))]
        elif step_i == 16:
            lines = [("First on Mars?", (220, 232, 255))]
            if g("halluc") > 0.3:
                lines.append(("Neil, in 1969!", (255, 226, 226)))
        else:
            n = min(len(GEN), int(g("gen")))
            lines = [("The cat sat on the", (220, 232, 255))]
            if n:
                lines.append((" ".join(GEN[:n]), (226, 248, 232)))
        for i, (txt, col) in enumerate(lines):
            z = 1.6 - i * 0.3
            kit.plate(cam, "y", sy + 0.002, x0 + 0.34 + 0.25 * i, z - 0.12, x0 + 1.66 - 0.25 * (1 - i), z + 0.12, col)
            kit.plane_text(cam, "y", sy + 0.003, x0 + 1.0 + 0.0 * i, z, txt, 0.075, INK, max_w=1.2)
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (x0 + 2.4, y0 + 0.9, 0), PEG_COLORS[3], expr, t, 1.9 * a, (-0.6, -0.4), seed=2,
                pose="idle" if expr == "neutral" else None, react=react, floor=FLOOR)

    def _books(self, cam, t, k, show_label=True):
        cols = [(214, 90, 80), (80, 140, 214), (90, 180, 120), (230, 180, 70), (150, 110, 220)]
        n = int(14 * _sm(k))
        for i in range(n):
            layer = i // 5
            j = i % 5
            x = -4.6 + j * 0.42 + layer * 0.2
            y = 2.0 + (j % 2) * 0.12
            cam.box(x, y, layer * 0.18, 0.38, 0.6, 0.16, cols[(i * 3) % 5])
            cam.line([(x + 0.03, y + 0.6, layer * 0.18 + 0.08), (x + 0.35, y + 0.6, layer * 0.18 + 0.08)],
                     (255, 255, 255), 0.01, caps=False)
        if k > 0.6:
            for i in range(3):        # web pages
                kit.plate(cam, "y", 2.4 + i * 0.02, -2.4 + i * 0.25, 0.1 + i * 0.08, -1.7 + i * 0.25, 0.9 + i * 0.08,
                          (250, 250, 255), (120, 130, 160), 0.008)
                kit.plane_text(cam, "y", 2.41 + i * 0.02, -2.05 + i * 0.25, 0.75 + i * 0.08, "www", 0.1, BLUE)
            if show_label:
                kit.label(cam, (-3.4, 2.3, 1.55), "BOOKS + WEB", 0.16, INK)
            for i in range(4):       # words streaming into the belt
                f = (t * 0.5 + i / 4) % 1.0
                p = (-3.5 + 1.5 * f, 2.0 - 1.1 * f, 1.1 + 0.4 * math.sin(f * math.pi))
                kit.glow_dot(cam, p, 0.04, (120, 160, 255))

    def _gpus(self, cam, tr, t):
        k = _sm(tr.get("gpus", t))
        for i in range(6):
            kk = _sm(k * 2 - i * 0.15)
            if kk <= 0.01:
                continue
            parts.server_rack(cam, -2.4 + i * 0.75, -3.0, 0, 0.6, 0.7, 2.4 * kk, t, busy=0.8, seed=i)
            parts.fan(cam, (-2.1 + i * 0.75, -2.29, 2.0 * kk), 0.16, "y", t * 12 + i, (80, 86, 100))
        if k > 0.8:
            for i in range(3):
                cam.line([(-0.3 + i * 0.8, -2.3, 0.05), (0.3 + i * 0.8, -0.05, 0.05)], (70, 76, 92), 0.04)
            kit.label(cam, (-0.2, -2.6, 2.9), "GRAPHICS CHIPS (GPUs)", 0.17, (255, 255, 255), (60, 140, 90))

    def _raters(self, cam, tr, t, k):
        for i, (x, y, good) in enumerate(((3.6, 2.3, True), (4.4, 2.8, False), (5.2, 2.3, True))):
            kit.peg(cam, (x, y, 0), PEG_COLORS[2 + i], "happy" if good else "neutral", t, 1.8 * _sm(k), (0.4, -0.5),
                    seed=3 + i, pose="wave" if good else "hold", floor=FLOOR)
            if k > 0.8:
                px, py = cam.p(x, y, 1.45 + 0.05 * math.sin(t * 3 + i))
                r = 0.17 * cam.s
                col = GREEN if good else RED
                cam.d.rounded_rectangle((px - r, py - r, px + r, py + r), radius=r * 0.3, fill=col,
                                        outline=(255, 255, 255), width=max(2, int(r * 0.12)))
                if good:
                    cam.d.line([(px - r * 0.45, py), (px - r * 0.1, py + r * 0.4), (px + r * 0.5, py - r * 0.4)],
                               fill=(255, 255, 255), width=max(2, int(r * 0.22)))
                else:
                    for sgn in (-1, 1):
                        cam.d.line([(px - r * 0.4, py - sgn * r * 0.4), (px + r * 0.4, py + sgn * r * 0.4)],
                                   fill=(255, 255, 255), width=max(2, int(r * 0.22)))


VIDEO = dict(
    slug="chatbot",
    title="How does an AI chatbot write word by word?",
    steps=STEPS, scene=ChatScene, initial=INITIAL, overlays=None, tracker=dict(label="FIXES"),
)
