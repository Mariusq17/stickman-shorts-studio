"""Why does a streaming movie start instantly if the file is gigabytes? - built step by step."""
from __future__ import annotations

import math

from PIL import ImageDraw

from ...painter import font
from ..iso import IsoCam, mix, shade
from ..lib import kit, parts
from ..lib.story import open_loop
from ..lib.palette import PEG_COLORS
from ..lib.shadows import ShadowLayer

RED, BLUE, INK, GREEN = (226, 52, 64), (40, 110, 235), (25, 25, 32), (40, 160, 90)
ORANGE = (240, 140, 40)

WIDE = ((0.4, 0.3, 0.7), 122)
ROOM = ((3.8, 2.4, 1.2), 190)
TV = ((4.0, 1.6, 1.5), 300)
DC = ((-3.4, -1.6, 1.0), 170)

DC_P = (-3.0, -1.0, 0.25)
ISP_P = (0.9, -0.2, 0.25)
TV_P = (4.0, 1.75, 1.3)
FAR = [DC_P, (-1.0, -1.0, 0.1), (0.9, -0.6, 0.1), (2.2, 1.0, 0.1), (3.4, 1.0, 0.1), (3.4, 1.75, 0.9), TV_P]
NEAR = [ISP_P, (0.9, -0.6, 0.1), (2.2, 1.0, 0.1), (3.4, 1.0, 0.1), (3.4, 1.75, 0.9), TV_P]

STEPS = [
    dict(text="If you download a whole movie file and then press play, you've got the world's simplest streaming "
              "service.",
         cam=((-3.0, -1.0, 1.0), 260), pegs="neutral",
         cams=[("w:then", ((3.6, 2.2, 1.2), 200), 1.2), ("w:simplest", WIDE, 1.4)],
         do=[("file", 0.0, 1, 0.6, "back"), ("dc", 0.0, 1, 0.8, "out"), ("file_p", "w:download", 0.25, 2.5, "io"),
             ("home", "w:movie", 1, 0.8, "out"), ("world", "w:simplest", 1, 1.2, "out")],
         keys=[("whole movie file", INK), ("press play", INK), ("simplest streaming service", BLUE)],
         sfx=[("w:download", "whoosh"), ("w:simplest", "whoosh")]),
    dict(text="Except a raw movie is enormous, and you'd wait hours before the first frame.",
         cam=WIDE, pegs="worried",
         do=[("file_p", 0.0, 0.45, "end", "lin"), ("wait", "w:wait", 1, 0.3, "out")],
         keys=[("raw movie is enormous|raw movie = huge", RED), ("wait hours", RED)],
         pops=[dict(kind="meter", at="w:wait", text="DOWNLOAD", **{"from": 0.0, "to": 0.04}, color=RED, fmt="4%",
                    anim=2.0, pos="bc", until="end+0.3")]),
    dict(text="So first you compress it. Most frames barely change from the one before, so instead of storing every "
              "pixel again, you store only what moved.",
         cam=DC, pegs="happy", pose="think",
         do=[("wait", 0.0, 0, 0.3, "in"), ("file_p", 0.0, 0.0, 0.01, "lin"), ("squash", "w:compress", 1, 1.4, "io"),
             ("bubble_kind", 0, 1, 0, "lin"), ("bubble", "w:frames", 1, 0.4, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("compress it", INK), ("barely change", INK), ("only what moved", BLUE)],
         fix="w:compress",
         sfx=[("w:compress", "slap")]),
    dict(text="The program that does this is a codec, and it makes the file hundreds of times smaller.",
         cam=DC, pegs="happy",
         keys=[("codec", INK), ("hundreds of times smaller", BLUE)],
         pops=[dict(kind="bars", at="w:hundreds", title="FILE SIZE", until="end+0.3", pos="bc",
                    items=[("raw", 1.0, RED), ("compressed", 0.02, GREEN)])]),
    dict(text="But even a compressed movie takes a while to download completely.",
         cam=WIDE, pegs="worried",
         do=[("file_p", 0.0, 0.3, "end", "lin")],
         keys=[("takes a while", RED)]),
    dict(text="So you chop it into small chunks, a few seconds each. Your TV grabs the first chunk, starts playing, "
              "and fetches the next ones while you watch.",
         cam=WIDE, pegs="happy",
         do=[("file_p", 0.0, 0.0, 0.01, "lin"), ("chunks", "w:chop", 1, 0.6, "out"), ("flow", "w:grabs", 3.0, "end", "lin"),
             ("play", "w:playing", 1, 0.2, "out")],
         keys=[("small chunks", INK), ("few seconds each", INK), ("starts playing", BLUE)],
         fix="w:chop",
         sfx=[("w:chop", "slap"), ("w:playing", "ding")]),
    dict(text="Then your Wi-Fi gets slower, and the movie freezes.",
         cam=TV, pegs="shocked",
         do=[("bw", "w:slower", 0.15, 0.6, "out"), ("freeze", "w:freezes", 1, 0, "lin"), ("flow", 0.0, 3.4, "end", "lin")],
         keys=[("Wi-Fi gets slower", RED), ("freezes|frozen!", RED)],
         sfx=[("w:freezes", "sting")]),
    dict(text="So every chunk is stored at several qualities. When your connection slows down, the player quietly "
              "switches to a smaller version. That's adaptive streaming.",
         cam=WIDE, pegs="happy",
         do=[("freeze", 0.2, 0, 0, "lin"), ("ladder", "w:several", 1, 0.6, "out"), ("q", "w:switches", 0, 0, "lin"),
             ("flow", 0.2, 7.0, "end", "lin"), ("bw", "w:adaptive", 1.0, 1.0, "io"), ("q", "w:adaptive+0.8", 2, 0, "lin")],
         keys=[("several qualities", INK), ("smaller version", BLUE), ("adaptive streaming", INK)],
         fix="w:adaptive",
         pops=[dict(kind="graph", at="w:connection", title="CONNECTION SPEED", track="bw", window=5.0, color=BLUE,
                    pos="bc", until="end+0.3")],
         sfx=[("w:switches", "click")]),
    dict(text="That's why videos sometimes start a little blurry, then snap sharp a few seconds later.",
         cam=TV, pegs="happy",
         do=[("q", 0.0, 0, 0, "lin"), ("q", "w:snap", 2, 0, "lin"), ("flow", 0.0, 9.0, "end", "lin")],
         keys=[("little blurry", INK), ("snap sharp", BLUE)],
         sfx=[("w:snap", "ding")]),
    dict(text="And to survive hiccups, the player always keeps a few chunks ready ahead of time. That's the buffer.",
         cam=TV, pegs="neutral",
         do=[("buffer", "w:ready", 1, 0.8, "out"), ("flow", 0.0, 11.0, "end", "lin")],
         keys=[("hiccups", RED), ("chunks ready ahead", INK), ("buffer", INK)],
         fix="w:buffer"),
    dict(text="But the main servers might be in another country, and every request crawls across the planet.",
         cam=WIDE, pegs="worried",
         do=[("slowpath", "w:crawls", 1, 0.4, "out"), ("flow", 0.0, 11.6, "end", "lin")],
         keys=[("another country", INK), ("crawls across the planet", RED)],
         pops=[dict(kind="meter", at="w:request", text="DISTANCE", **{"from": 0.0, "to": 1.0}, color=RED, fmt="FAR",
                    pos="bc", until="end+0.3")]),
    dict(text="So Netflix puts copies of popular shows on its own servers inside your internet provider's network, "
              "just a few miles from you.",
         cam=((1.6, 0.4, 0.8), 140), pegs="happy",
         do=[("slowpath", 0.0, 0, 0.3, "in"), ("isp", "w:copies", 1, 0.8, "back"), ("near", "w:inside", 1, 0.5, "out"),
             ("flow", 0.0, 15.0, "end", "lin")],
         keys=[("copies of popular shows", INK), ("internet provider's network|inside your provider", INK),
               ("few miles from you", BLUE)],
         fix="w:copies",
         sfx=[("w:copies", "pop")]),
    dict(text="It even tunes the qualities for each show. A simple cartoon needs far fewer bits than an explosion "
              "packed action movie.",
         cam=TV, pegs="happy",
         do=[("cartoon", "w:cartoon", 1, 0.3, "out"), ("cartoon", "w:explosion", 2, 0, "lin"), ("flow", 0.0, 17.0, "end", "lin")],
         keys=[("each show", INK), ("simple cartoon", BLUE), ("far fewer bits", BLUE)],
         fix="w:tunes",
         pops=[dict(kind="bars", at="w:fewer", title="BITS NEEDED", until="end+0.3", pos="bc",
                    items=[("cartoon", 0.3, GREEN), ("action movie", 1.0, ORANGE)])]),
    dict(text="So next time a movie starts in a second, you'll know you're not getting the movie. You're getting the "
              "next few seconds of it, over and over.",
         cam=ROOM, pegs="happy",
         do=[("cartoon", 0.2, 0, 0, "lin"), ("flow", 0.0, 21.0, "end", "lin")],
         keys=[("starts in a second", BLUE), ("next few seconds|the next few seconds", INK), ("over and over", INK)]),
    dict(text="And congratulations, you just built a streaming service. Now you just need to decide what to watch. "
              "Follow for more.",
         cam=WIDE, pegs="happy", min=8.4, pose="cheer",
         do=[("flow", 0.0, 25.0, "end", "lin")],
         keys=[("built a streaming service|you built a streaming service!", BLUE), ("what to watch", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(file=0, dc=0, file_p=0, home=0, world=0, wait=0, squash=0, bubble=0, bubble_kind=0, chunks=0, flow=0,
               play=0, bw=1.0, freeze=0, ladder=0, q=2, buffer=0, slowpath=0, isp=0, near=0, cartoon=0)

FLOOR = (214, 226, 206)
ROOMF = (232, 214, 190)
WALLC = (244, 236, 226)


def _sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


class StreamScene:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = kit.gradient_bg(W, H, (210, 226, 250), (248, 244, 238), clouds=5)

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        self._step = step_i
        if g("world") > 0.01:
            self._ground(cam, tr, t)
        if g("dc") > 0.01:
            self._datacenter(cam, tr, t)
        if g("isp") > 0.01:
            self._isp(cam, tr, t)
        if g("world") > 0.3 or g("chunks") > 0.01:
            self._cables(cam, tr, t)
        if g("home") > 0.01:
            self._room(cam, tr, t)
        self._file(cam, tr, t)
        self._chunks(cam, tr, t)

    # ------------------------------------------------------------- places
    def _ground(self, cam, tr, t):
        k = _sm(tr.get("world", t))
        R = 2 + 5 * k
        cam.poly([(-R - 1, -R, 0), (R + 1, -R, 0), (R + 1, R, 0), (-R - 1, R, 0)], FLOOR)
        for (x, y) in ((-1.5, 2.5), (1.6, 3.6), (-4.6, 1.2), (5.8, -1.0)):
            cam.box(x - 0.06, y - 0.06, 0, 0.12, 0.12, 0.5, (130, 96, 70))
            px, py = cam.p(x, y, 0.85)
            r = 0.4 * cam.s
            cam.d.ellipse((px - r, py - r * 0.9, px + r, py + r * 0.9), fill=(110, 180, 100), outline=(70, 130, 70),
                          width=max(1, int(0.01 * cam.s)))

    def _datacenter(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("dc"))
        cam.box(-4.6, -2.6, 0, 2.6, 1.8, 0.1, (150, 156, 170))
        for i in range(4):
            parts.server_rack(cam, -4.4 + i * 0.62, -2.5, 0.1, 0.5, 0.6, 1.8 * k, t, busy=0.7, seed=i)
        if k > 0.9 and self._step in (0, 1, 10):
            kit.label(cam, (-3.3, -1.7, 2.5), "STREAMING SERVERS", 0.2, (255, 255, 255), (200, 40, 50))
            if g("slowpath") > 0.5:
                kit.label(cam, (-3.3, -1.7, 2.1), "FAR AWAY", 0.15, (255, 255, 255), RED)

    def _isp(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("isp"))
        cam.box(0.2, -1.2, 0, 1.4, 1.0, 1.1 * k, (210, 214, 226))
        cam.box(0.15, -1.25, 1.1 * k, 1.5, 1.1, 0.12, (120, 128, 150))
        if k > 0.9:
            parts.server_rack(cam, 0.55, -0.6, 0.0, 0.4, 0.38, 0.9, t, busy=0.9, color=(200, 40, 50))
            if self._step == 11:
                kit.label(cam, (0.9, -0.7, 1.75), "COPY NEAR YOU", 0.17, (255, 255, 255), GREEN)
            kit.label(cam, (0.9, -0.7, 1.45), "INTERNET PROVIDER", 0.12, INK, (255, 255, 255))

    def _cables(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        near = g("near")
        kit.cable(cam, FAR[:5], lit=0.0)
        if g("slowpath") > 0.5:
            for i in range(2):
                f = (t * 0.08 + i / 2) % 1.0
                kit.packet(cam, FAR, f, (220, 80, 80), 0.07)

    def _room(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        k = _sm(g("home"))
        x0, x1, y0, y1 = 2.6, 5.6, 1.5, 4.2
        cam.poly([(x0, y0, 0.02), (x1, y0, 0.02), (x1, y1, 0.02), (x0, y1, 0.02)], ROOMF)
        h = 2.2 * k
        cam.poly([(x0, y0, 0), (x1, y0, 0), (x1, y0, h), (x0, y0, h)], WALLC, shade(WALLC, -0.3), 0.01)
        cam.poly([(x0, y0, 0), (x0, y1, 0), (x0, y1, h), (x0, y0, h)], shade(WALLC, -0.08), shade(WALLC, -0.3), 0.01)
        sh = ShadowLayer(cam)
        sh.ao_edge((x0, y0, 0), (x1, y0, 0), (0, 1, 0), (0, 0, 1), 0.25, 140)
        sh.ao_edge((x0, y0, 0), (x0, y1, 0), (1, 0, 0), (0, 0, 1), 0.25, 140)
        sh.apply(cam.img, 0.25, 2.0)
        if k < 0.9:
            return
        # TV on the back wall + stand
        cam.box(3.2, y0, 0, 1.6, 0.45, 0.5, (150, 110, 80))
        cam.box(3.1, y0, 0.85, 1.8, 0.06, 1.05, (24, 26, 32))
        self._screen(cam, tr, t, 3.18, y0 + 0.061, 4.82, 0.92, 1.83)
        # router on the stand
        cam.box(4.4, y0 + 0.1, 0.5, 0.3, 0.2, 0.06, (240, 240, 245))
        parts.led(cam, (4.55, y0 + 0.31, 0.53), (90, 230, 140) if g("bw") > 0.5 else (255, 150, 60), True, 0.02)
        # couch + Peg
        cam.box(3.0, 3.4, 0, 2.0, 0.7, 0.4, (90, 120, 180))
        cam.box(3.0, 3.9, 0.4, 2.0, 0.2, 0.45, (80, 108, 166))
        expr = tr.peg_expr(t)
        since = tr.since_step(t)
        react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" else 0.0
        kit.peg(cam, (4.0, 3.65, 0.4), PEG_COLORS[0], expr, t, 1.8, (0.0, -0.8), seed=1, pose=tr.peg_pose(t),
                react=react)
        kit.peg(cam, (3.4, 3.7, 0.4), PEG_COLORS[3], "happy" if expr != "shocked" else "worried", t, 1.6, (0.2, -0.8),
                seed=4, pose="idle")

    def _screen(self, cam, tr, t, x0, y, x1, z0, z1):
        g = lambda k: tr.get(k, t)
        playing = g("play") > 0.5 or self._step >= 12
        frozen = g("freeze") > 0.5
        q = int(round(g("q")))
        cart = int(round(g("cartoon")))
        tt = 0 if frozen else t
        kit.plate(cam, "y", y, x0, z0, x1, z1, (20, 22, 30))
        if not playing and self._step < 5:
            kit.plane_text(cam, "y", y + 0.001, (x0 + x1) / 2, (z0 + z1) / 2,
                           "DOWNLOADING..." if self._step >= 0 and g("file_p") > 0.01 else "", 0.1, (200, 200, 210),
                           max_w=x1 - x0 - 0.2)
            return
        # the "movie": sky, hills, sun, a little car driving
        sky = (120, 180, 240) if cart != 2 else (60, 40, 60)
        kit.plate(cam, "y", y + 0.001, x0 + 0.04, z0 + 0.04, x1 - 0.04, z1 - 0.04, sky)
        kit.plate(cam, "y", y + 0.002, x0 + 0.04, z0 + 0.04, x1 - 0.04, z0 + 0.3, (90, 170, 90) if cart != 2 else (80, 60, 50))
        sx = x0 + 0.3 + ((tt * 0.25) % 1.0) * (x1 - x0 - 0.6)
        sz = z0 + 0.38
        if cart == 2:     # explosions: lots of detail
            for i in range(6):
                a = tt * 3 + i
                cam.poly(cam.disc_pts((x0 + 0.4 + i * 0.22, y + 0.003, z0 + 0.55 + 0.1 * math.sin(a)), 0.09 + 0.03 * math.sin(a * 2),
                                      "y", 10), (255, 160 - i * 10, 40))
        else:
            cam.poly(cam.disc_pts((x1 - 0.35, y + 0.003, z1 - 0.25), 0.11, "y", 14), (255, 220, 80))
            kit.plate(cam, "y", y + 0.003, sx - 0.12, sz - 0.06, sx + 0.12, sz + 0.04, (230, 70, 70))
        if q == 0 and not frozen:       # blurry: coarse blocks over the picture
            for i in range(8):
                for j in range(4):
                    if (i + j) % 2:
                        u0 = x0 + 0.04 + i * (x1 - x0 - 0.08) / 8
                        v0 = z0 + 0.04 + j * (z1 - z0 - 0.08) / 4
                        kit.plate(cam, "y", y + 0.004, u0, v0, u0 + (x1 - x0 - 0.08) / 8, v0 + (z1 - z0 - 0.08) / 4,
                                  mix(sky, (200, 210, 220), 0.35))
        if frozen:
            cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
            for i in range(8):
                a = t * 6 + i * 0.785
                cam.poly(cam.disc_pts((cx + math.cos(a) * 0.16, y + 0.005, cz + math.sin(a) * 0.16), 0.03, "y", 8),
                         mix((255, 255, 255), (90, 90, 100), i / 8))
        # quality badge + progress bar (played / buffered)
        badge = {0: "480p", 1: "720p", 2: "4K"}.get(q, "4K")
        kit.plate(cam, "y", y + 0.005, x1 - 0.42, z1 - 0.2, x1 - 0.08, z1 - 0.06, (20, 20, 26))
        kit.plane_text(cam, "y", y + 0.006, x1 - 0.25, z1 - 0.13, badge, 0.07, (255, 255, 255), max_w=0.3)
        kit.plate(cam, "y", y + 0.005, x0 + 0.1, z0 + 0.08, x1 - 0.1, z0 + 0.12, (90, 90, 100))
        prog = min(1.0, g("flow") / 26.0)
        buf = min(1.0, prog + (0.18 if g("buffer") > 0.5 else 0.04))
        w = x1 - x0 - 0.2
        kit.plate(cam, "y", y + 0.006, x0 + 0.1, z0 + 0.08, x0 + 0.1 + w * buf, z0 + 0.12, (200, 200, 210))
        kit.plate(cam, "y", y + 0.007, x0 + 0.1, z0 + 0.08, x0 + 0.1 + w * prog, z0 + 0.12, (230, 40, 50))

    # ------------------------------------------------------------- the data
    def _file(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        f = g("file")
        if f <= 0.01 or g("chunks") > 0.5:
            return
        sq = g("squash")
        s = _sm(f) * (1 - 0.82 * sq)
        p, _ = kit.path_point(FAR, g("file_p"))
        w, d, h = 1.4 * s, 1.0 * s, 0.9 * s
        x, y, z = p[0] - w / 2, p[1] - d / 2, p[2]
        cam.box(x, y, z, w, d, h, (60, 64, 80))
        for i in range(6):     # film strip holes
            cam.box(x + 0.05 * s + i * w / 6, y + d, z + h - 0.12 * s, w / 10, 0.01, 0.07 * s, (230, 230, 240))
        label = "MOVIE RAW: 1,000+ GB" if sq < 0.5 else "MOVIE: ~5 GB"
        kit.label(cam, (p[0], p[1], z + h + 0.35), label, 0.16, (255, 255, 255), RED if sq < 0.5 else GREEN)

    def _chunks(self, cam, tr, t):
        g = lambda k: tr.get(k, t)
        ch = g("chunks")
        if ch <= 0.01:
            return
        near = g("near") > 0.5
        path = NEAR if near else FAR
        src = ISP_P if near else DC_P
        q = int(round(g("q")))
        flow = g("flow")
        cols = {0: (230, 170, 60), 1: (120, 190, 240), 2: (90, 210, 120)}
        frozen = g("freeze") > 0.5
        # stacks of chunks at the source: 3 quality rows
        rows = 3 if g("ladder") > 0.5 else 1
        for r in range(rows):
            for i in range(6):
                sz = 0.16 + 0.06 * (2 - r if rows == 3 else 2)
                cam.box(src[0] - 0.6 + i * 0.22, src[1] + 0.5 + r * 0.32, src[2] + 0.4 * 0 + 0.0, 0.18, 0.18 * 0 + sz,
                        0.18, cols[(2 - r) if rows == 3 else 2])
        if g("ladder") > 0.5 and self._step == 7:
            kit.label(cam, (src[0], src[1] + 1.6, 0.8), "4K / 720p / 480p", 0.14, (255, 255, 255), BLUE)
        # chunks travelling: one per unit of flow, travel time 0.8 units (faster when near)
        travel = 0.45 if near else 0.9
        for i in range(int(flow) + 1):
            a = (flow - i) / travel
            if 0.0 < a < 1.0:
                if frozen and a > 0.3:
                    a = 0.3 + 0.02 * math.sin(t * 4)
                p, _ = kit.path_point(path, a)
                size = {0: 0.13, 1: 0.17, 2: 0.22}[q]
                cam.box(p[0] - size / 2, p[1] - size / 2, p[2], size, size, size, cols[q])
        if g("play") > 0.5 and self._step in (5,):
            kit.label(cam, (TV_P[0] - 0.4, TV_P[1], TV_P[2] + 1.0), "CHUNK 1: PLAYING", 0.13, (255, 255, 255), GREEN)


def draw_bubble(img, tr, t, W, H):
    k = tr.get("bubble", t)
    if k <= 0.01:
        return
    d = ImageDraw.Draw(img)
    cx, cy, R = W * 0.70, H * 0.33, W * 0.24 * k
    d.ellipse((cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), fill=(35, 35, 45))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255))
    u = R / 100.0
    # two frames: only the ball moved -> only that patch is stored
    for j, ox in enumerate((-42, 42)):
        x0, y0 = cx + ox * u - 34 * u, cy - 30 * u
        d.rectangle((x0, y0, x0 + 68 * u, y0 + 50 * u), fill=(140, 195, 245), outline=INK, width=max(1, int(2 * u)))
        d.rectangle((x0, y0 + 36 * u, x0 + 68 * u, y0 + 50 * u), fill=(90, 170, 90))
        bx = x0 + (18 + 26 * j) * u
        d.ellipse((bx - 7 * u, y0 + 20 * u, bx + 7 * u, y0 + 34 * u), fill=(230, 70, 70))
        if j == 1:
            d.rectangle((x0 + 4 * u, y0 + 16 * u, x0 + 56 * u, y0 + 38 * u), outline=(255, 150, 30), width=max(2, int(3 * u)))
    d.text((cx, cy + 40 * u), "store only the change", font=font(int(13 * u)), fill=INK, anchor="mm")


def overlays(img, tr, t, W, H):
    draw_bubble(img, tr, t, W, H)


# open-loop structure (2026-11-22): question hook + teaser, reminder, late answer, loop ending
STEPS = open_loop(
    STEPS, "You never actually download the movie you're watching, not even close.", answer_step=13,
    teaser_frac=0.5, reminder=(5, "But that's still not the real trick."), reveal="Here's the real trick.",
    hook_keys=[("never actually download", RED), ("not even close", RED)],
    ending_text="Now you know more about streaming than 99% of people. Follow for more. Because remember,",
    ending_keys=[("99% of people|smarter than 99%", BLUE)])  # O5 hook, E3 ending + loop

VIDEO = dict(
    slug="streaming",
    title="Why does a movie start instantly if the file is gigabytes?",
    steps=STEPS, end_cover=False, scene=StreamScene, initial=INITIAL, overlays=overlays, tracker=dict(label="FIXES"),
)
