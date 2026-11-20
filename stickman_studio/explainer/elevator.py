"""TEST: 'How does an elevator not fall?' - built step by step in 2.5D isometric.

python -m stickman_studio.explainer.elevator -o elevator.mp4
"""
from __future__ import annotations

import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw

from ..painter import font
from .iso import IsoCam, mix, shade
from .lib import parts
from .lib.characters import draw_peg as _draw_peg2
from .lib.palette import PEG_COLORS
from .lib.shadows import ShadowLayer


def draw_peg(cam, xyz, color, expr="neutral", t=0.0, scale=1.0, look=(0.0, 0.0), seed=0, hat=False, pose=None,
             react=0.0, floor=None):
    """Adapter to the v2 mascots (+ a contact shadow on the given floor colour)."""
    if pose is None:
        pose = {"shocked": "panic", "worried": "hold", "happy": "cheer" if seed % 2 else "wave"}.get(expr, "idle")
    if floor is not None:
        x, y = cam.p(*xyz)
        r = 0.30 * cam.s * scale * 0.62
        cam.d.ellipse((x - r, y - r * 0.24, x + r, y + r * 0.24), fill=shade(floor, -0.22))
    _draw_peg2(cam, xyz, color, expr, pose, t, scale, look, react, seed, hat)

RED, BLUE, INK = (226, 52, 64), (40, 110, 235), (25, 25, 32)

# ----------------------------------------------------------------- the script
# Every timing is a cue on the narration ("w:word" = when that word is spoken).
#   do   : (track, cue, value, duration_or_cue, ease)
#   keys : ("spoken phrase|shown text", color) - keyword shown exactly when it is said
#   pops : animated pop-ups (note / warn / check / meter / count / arrow / card)
#   cams : (cue, (focus_xyz, zoom), duration) extra camera moves inside a step
GREEN = (40, 160, 90)
WIDE = ((1.9, 1.3, 5.6), 112)
STEPS = [
    dict(text="If you put a box on a rope and hang it from a motor at the top of a shaft, "
              "you've got the world's simplest elevator.",
         cam=((1.2, 1.0, 2.2), 250), pegs="neutral",
         cams=[("w:rope", ((1.2, 1.0, 5.0), 160), 0.9), ("w:motor", ((1.0, 1.0, 8.6), 165), 0.8),
               ("w:shaft", WIDE, 1.3)],
         do=[("car_show", "w:box", 1, 0.5, "back"), ("rope_show", "w:rope", 1, 0.9, "out"),
             ("top_show", "w:motor", 1, 0.6, "back"), ("build", "w:shaft", 1, 1.1, "out"),
             ("facade", "w:simplest", 1, 1.0, "out")],
         keys=[("box", INK), ("rope|box + rope", INK), ("motor|box + rope + motor", INK),
               ("simplest elevator", BLUE)],
         sfx=[("w:box", "pop"), ("w:motor", "pop"), ("w:shaft", "whoosh")]),
    dict(text="Press the button, the motor winds up the rope, and your passengers ride to the third floor.",
         cam=((1.4, 1.0, 3.2), 150), pegs="happy",
         cams=[("w:ride", ((1.4, 1.0, 7.4), 140), 2.6)],
         do=[("pegs_in", "w:passengers", 1, 0.4, "back"), ("car_z", "w:ride", 7.0, 2.6, "io")],
         keys=[("passengers", INK), ("third floor|going up", BLUE)],
         pops=[dict(kind="count", at="w:ride", **{"from": 1, "to": 3}, anim=2.4, fmt="FLOOR {}", pos="tr", dur=2.8)],
         sfx=[("end-0.2", "ding")]),
    dict(text="But hauling the whole car plus everyone inside takes a monster of a motor.",
         cam=((0.8, 1.2, 10.8), 290), pegs="worried",
         do=[("motor_glow", "w:hauling", 1, 0.5, "out")],
         keys=[("monster|monster motor", RED)],
         pops=[dict(kind="meter", at="w:hauling", text="MOTOR EFFORT", **{"from": 0.0, "to": 1.0}, color=RED,
                    fmt="MAX", pos="bc", until="end+0.4"),
               dict(kind="arrow", at="w:whole", xyz=(0.72, 1.6, 11.1), text="lifts EVERYTHING", color=RED,
                    off=(-0.05, -0.16), dur=2.6)]),
    dict(text="So you hang a heavy block on the other end of the rope. That's the counterweight.",
         cam=((0.9, 1.0, 6.2), 135), pegs="neutral",
         do=[("motor_glow", 0, 0, 0.5, "io"), ("cw_show", "w:heavy", 1, 0.9, "back")],
         keys=[("heavy block", INK), ("counterweight", INK)], fix="w:counterweight",
         pops=[dict(kind="arrow", at="w:counterweight", xyz=(0.14, 1.0, 2.3), text="counterweight", color=BLUE,
                    off=(-0.02, 0.12), dur=2.0, sound=False)],
         sfx=[("w:heavy", "whoosh")]),
    dict(text="It weighs about as much as the empty car plus half a full load, so the motor only moves the "
              "difference. It's a seesaw where your friend is already sitting on the other side.",
         cam=((0.9, 1.0, 6.2), 135), pegs="happy",
         do=[("bubble_kind", 0, 1, 0, "lin"), ("bubble", "w:seesaw", 1, 0.45, "back"), ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("empty car|car + half a load", INK), ("only moves the difference|only the difference", BLUE),
               ("seesaw", INK)],
         pops=[dict(kind="equation", at="w:weighs", parts=["counterweight", "≈", "car", "+", "½ load"],
                    colors=[INK, (120, 125, 140), INK, (120, 125, 140), BLUE], step=0.32, pos="bc",
                    until="w:only"),
               dict(kind="bars", at="w:only", title="MOTOR WORK", until="end+0.2",
                    items=[("no counterweight", 1.0, RED), ("with counterweight", 0.3, GREEN)], pos="bc")]),
    dict(text="And instead of winding the rope, the motor just spins a grooved wheel, and friction drags "
              "the ropes along. That's the traction sheave.",
         cam=((0.75, 1.0, 10.7), 280), pegs="neutral",
         do=[("car_z", "w:friction", 4.0, 3.0, "io")],
         keys=[("grooved wheel", INK), ("traction sheave", INK)], fix="w:traction",
         pops=[dict(kind="arrow", at="w:friction", xyz=(1.2, 1.0, 11.25), text="friction grip", color=BLUE,
                    off=(0.12, -0.12), dur=2.4)]),
    dict(text="Smooth ride. Until the car starts swinging and scraping the walls.",
         cam=((1.2, 1.0, 5.1), 190), pegs="shocked",
         do=[("swing", "w:swinging", 1, 0.3, "out")],
         keys=[("smooth ride", BLUE), ("scraping|scraping the walls", RED)],
         sfx=[("w:scraping", "slap")]),
    dict(text="So you bolt steel rails up both sides of the shaft, and the car slides along them on guide shoes.",
         cam=((1.2, 1.0, 5.4), 150), pegs="happy",
         do=[("swing", "w:rails", 0, 0.4, "out"), ("rails", "w:steel", 1, 1.4, "out")],
         keys=[("steel rails|guide rails", INK), ("guide shoes", INK)], fix="w:steel",
         pops=[dict(kind="check", at="w:slides", text="no more swinging", pos="bc", dur=2.2)],
         sfx=[("w:steel", "whoosh")]),
    dict(text="Then someone in the car asks the obvious question. What if the rope snaps?",
         cam=((1.2, 1.0, 7.8), 210), pegs="worried",
         do=[("strain", "w:snaps", 1, 0.3, "out")],
         keys=[("obvious question", INK), ("what if the rope snaps|what if it snaps?", RED)],
         pops=[dict(kind="warn", at="w:snaps", text="only ONE rope", pos="bc", until="end+0.3")]),
    dict(text="So you don't use one rope. You use several, and each one is strong enough to hold the car by itself.",
         cam=((1.2, 1.0, 7.8), 210), pegs="happy",
         do=[("strain", 0, 0, 0.3, "out"), ("ropes", "w:several", 4, 1.2, "out")],
         keys=[("several|several ropes", INK), ("by itself|each one holds it", BLUE)], fix="w:several",
         pops=[dict(kind="check", at="w:strong", text="any one can hold the car", pos="bc", until="end+0.3")],
         sfx=[("w:several", "pop")]),
    dict(text="But what if the car starts falling anyway? In 1854, Elisha Otis stood on a platform high above "
              "a crowd in New York, and had the only rope cut.",
         cam=((1.2, 1.0, 4.4), 170), pegs="worried",
         cams=[("w:1854", ((1.7, 1.0, 3.2), 175), 0.01)],
         do=[("flash", "w:1854", 1, 0, "lin"), ("otis_cut", "w:cut", 1, 0, "lin")],
         keys=[("falling anyway", RED), ("1854", INK), ("Elisha Otis", INK), ("cut|rope cut", RED)],
         pops=[dict(kind="count", at="w:1854", **{"from": 2025, "to": 1854}, anim=0.9, sub="New York", pos="tr",
                    dur=2.6)],
         sfx=[("w:1854", "whoosh"), ("w:cut", "slap")]),
    dict(text="The platform dropped a few inches. And stopped.",
         cam=((1.4, 1.0, 3.4), 200), pegs="happy", min=2.6,
         do=[("otis_drop", "w:dropped", 1, 0.45, "in")],
         keys=[("few inches|a few inches", INK), ("stopped", BLUE)],
         pops=[dict(kind="stamp", at="w:stopped", text="SAFE!", color=GREEN, pos="mr", until="end+0.3")],
         sfx=[("w:stopped", "thud")]),
    dict(text="Today's version works like this. A second rope runs from the car up to a small wheel at the top. "
              "That's the governor.",
         cam=((1.6, 1.3, 6.0), 150), pegs="neutral",
         cams=[("w:wheel", ((1.9, 1.6, 9.6), 220), 1.2)],
         do=[("flash", 0, 0, 0, "lin"), ("gov", "w:second", 1, 1.2, "out")],
         keys=[("second rope", INK), ("governor", INK)], fix="w:governor",
         sfx=[("w:second", "whoosh")]),
    dict(text="If the car goes too fast, weights inside the governor swing outward and lock the wheel.",
         cam=((1.5, 1.2, 5.6), 140), pegs="shocked",
         do=[("falling", 0, 1, 0, "lin"), ("car_z", 0.1, 3.0, "end", "lin"), ("bubble_kind", 0, 2, 0, "lin"),
             ("speed", 0.1, 1.0, "end", "in"),
             ("bubble", "w:weights", 1, 0.4, "back"), ("fly", "w:outward", 1, 0.6, "out")],
         keys=[("too fast", RED), ("swing outward", INK), ("lock|lock the wheel", INK)],
         pops=[dict(kind="graph", at=0.2, title="CAR SPEED", track="speed", window=9.5, color=RED, pos="bc",
                    dur=10.5)]),
    dict(text="The locked wheel grabs the rope, the rope yanks a lever on the car, and steel wedges clamp onto "
              "the rails. That's the safety brake.",
         cam=((1.2, 1.0, 3.7), 210), pegs="shocked",
         do=[("bubble", 0, 0, 0.3, "in"), ("car_z", 0, 2.4, "w:clamp", "lin"), ("brake", "w:clamp", 1, 0.25, "out"),
             ("speed", "w:clamp", 0.0, 0.35, "out"),
             ("falling", "w:clamp", 0, 0, "lin")],
         keys=[("grabs the rope", INK), ("steel wedges", INK), ("safety brake", INK)], fix="w:safety",
         pose="cover",
         sfx=[("w:clamp", "thud")]),
    dict(pose="cheer", text="It's like grabbing a fire pole with both hands while you're sliding down.",
         cam=((1.2, 1.0, 3.7), 210), pegs="happy",
         do=[("bubble_kind", 0, 3, 0, "lin"), ("bubble", "w:grabbing", 1, 0.4, "back"),
             ("bubble", "end-0.3", 0, 0.3, "in")],
         keys=[("fire pole", BLUE)]),
    dict(text="And just in case, you put giant springs at the bottom of the pit. Those are the buffers.",
         cam=((1.2, 1.0, 1.4), 210), pegs="neutral",
         do=[("brake", 0.3, 0, 0.3, "io"), ("car_z", 0.3, 4.0, 2.0, "io"), ("buffers", "w:springs", 1, 1.0, "back")],
         keys=[("just in case", INK), ("giant springs", INK), ("buffers", INK)], fix="w:buffers",
         sfx=[("w:springs", "boing")]),
    dict(text="Now the car is safe. The doors aren't. Open a door on the wrong floor, and there's nothing "
              "behind it but an empty shaft.",
         cam=((1.2, 0.5, 5.4), 175), pegs="neutral",
         do=[("car_z", 0.2, 7.0, 2.0, "io"), ("visitor", "w:doors", 1, 0.5, "back"), ("door2", "w:open", 1, 0.8, "io"),
             ("visitor_x", "w:nothing", 1, 1.2, "io")],
         keys=[("car is safe", BLUE), ("doors aren't", RED), ("empty shaft", RED)],
         pops=[dict(kind="warn", at="w:empty", text="nothing there!", pos="bc", until="end+0.3")],
         sfx=[("w:open", "sting")]),
    dict(text="So every landing door gets a lock that only releases when the car is right there. And the car "
              "won't move until every door is shut and locked.",
         cam=((1.2, 0.5, 5.4), 165), pegs="neutral",
         do=[("visitor_x", 0, 0, 0.6, "io"), ("door2", "w:lock", 0, 0.7, "io"), ("locks", "w:lock", 1, 0.6, "back")],
         keys=[("lock|door lock", INK), ("shut and locked", INK)], fix="w:lock",
         pops=[dict(kind="check", at="w:right", text="opens only if the car is here", pos="bc", dur=2.6)],
         sfx=[("w:lock", "click")]),
    dict(text="Then the doors close on someone's backpack.",
         cam=((1.2, 0.5, 5.0), 230), pegs="worried", min=3.0,
         do=[("car_z", 0, 4.0, 1.2, "io"), ("pegs_in", 0, 0, 0.3, "in"), ("rider", 0.4, 1, 0.3, "back"),
             ("door2", 0.2, 1, 0.3, "io"), ("door2", "w:close", 0, 0.5, "io"), ("squeeze", "w:backpack", 1, 0.2, "in")],
         keys=[("backpack", RED)],
         sfx=[("w:backpack", "slap")]),
    dict(text="So you shine a curtain of invisible infrared beams across the doorway. Break a beam, and the doors "
              "pop back open.",
         cam=((1.2, 0.5, 5.0), 230), pegs="happy",
         do=[("curtain", "w:curtain", 1, 0.5, "out"), ("door2", "w:pop", 1, 0.4, "out"), ("squeeze", "w:pop", 0, 0.2, "out")],
         keys=[("infrared beams", INK), ("pop back open", BLUE)], fix="w:infrared",
         sfx=[("w:pop", "pop")]),
    dict(text="Last problem. The car stops two inches below the floor, and everyone trips on the step.",
         cam=((1.2, 0.5, 4.8), 250), pegs="shocked",
         do=[("rider", 0, 0, 0.3, "in"), ("pegs_in", 0, 1, 0.3, "back"), ("door2", 0, 0, 0.4, "io"),
             ("curtain", 0, 0, 0.3, "io"), ("car_z", "w:stops", 3.72, 0.8, "io"), ("door2", "w:below", 1, 0.5, "io")],
         keys=[("last problem", INK), ("two inches", RED), ("trips", RED)],
         pops=[dict(kind="arrow", at="w:two", xyz=(1.2, 0.0, 4.0), text="2-inch step", color=RED,
                    off=(0.2, 0.12), until="end+0.3")],
         sfx=[("w:trips", "thud")]),
    dict(text="So sensors on the rails tell the controller exactly where the car is, and it creeps the last bit "
              "to stop perfectly level.",
         cam=((1.4, 0.7, 4.8), 240), pegs="happy",
         do=[("sensor", "w:sensors", 1, 0.5, "back"), ("door2", "w:sensors", 0, 0.4, "io"),
             ("car_z", "w:creeps", 4.0, 1.2, "io"), ("door2", "w:level", 1, 0.5, "io")],
         keys=[("sensors", INK), ("perfectly level", BLUE)], fix="w:sensors",
         sfx=[("w:level", "ding")]),
    dict(text="So next time the doors bounce back open when your bag gets in the way, you'll know who saw it.",
         cam=((1.2, 0.5, 5.0), 210), pegs="happy",
         do=[("curtain", "w:bounce", 1, 0.4, "out")],
         keys=[("bounce back|doors bounce back?", INK), ("you'll know|now you know", BLUE)]),
    dict(text="And congratulations, you just built an elevator. Now you just need to stop people from pressing "
              "every single button. Follow for more.",
         cam=WIDE, pegs="happy", min=8.4,
         do=[("curtain", 0, 0, 0.4, "io"), ("door2", 0, 0, 0.4, "io"), ("pegs_in", 0, 1, 0.4, "back")],
         keys=[("built an elevator|you built an elevator!", BLUE), ("every single button", INK)],
         pops=[dict(kind="card", at="w:follow-0.6", until="end+1", tap=1.4)],
         sfx=[("w:follow", "pop")]),
]

INITIAL = dict(build=0, car_show=0, rope_show=0, top_show=0, facade=0, car_z=1.0, pegs_in=0, motor_glow=0,
               cw_show=0, bubble=0, bubble_kind=0, swing=0, rails=0, strain=0, ropes=1, flash=0, otis_cut=0,
               otis_drop=0, gov=0, falling=0, fly=0, brake=0, buffers=0, visitor=0, visitor_x=0, door2=0, locks=0,
               rider=0, squeeze=0, curtain=0, sensor=0, speed=0)

FLOORS = (1.0, 4.0, 7.0)
TOP = 10.0
BG_TOP, BG_BOT = (228, 238, 250), (250, 246, 238)
WALL = (205, 212, 224)          # shaft concrete
FACADE = (238, 228, 212)        # building around the shaft
CAR = (250, 196, 70)
METAL = (150, 158, 170)
CORRIDOR = (255, 236, 196)
CX = 1.2                         # car centre x
DOOR_X0, DOOR_X1 = 0.75, 1.65    # door opening on the back wall (y = 0)
SHEAVE = (0.72, 1.0, TOP + 0.8)
SR = 0.48


class ElevatorScene:
    @staticmethod
    def film_amount(tr, t):
        return 1.0 if tr.get("flash", t) >= 0.5 else 0.0

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.bg = self._bg()

    def _bg(self):
        W, H = self.W, self.H
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        arr = np.array(BG_TOP, np.float32) * (1 - y) + np.array(BG_BOT, np.float32) * y
        img = Image.fromarray(np.broadcast_to(arr, (H, W, 3)).astype(np.uint8))
        d = ImageDraw.Draw(img)
        rnd = random.Random(1)
        for _ in range(7):
            cx, cy, r = rnd.uniform(0, W), rnd.uniform(0.05 * H, 0.5 * H), rnd.uniform(0.04, 0.08) * W
            for dx, rr in ((-1, 0.7), (0, 1.0), (1, 0.8)):
                d.ellipse((cx + dx * r - rr * r, cy - rr * r * 0.6, cx + dx * r + rr * r, cy + rr * r * 0.6),
                          fill=(255, 255, 255))
        return img

    def draw(self, img, cam: IsoCam, tr, t, step_i, step_t):
        g = lambda k: tr.get(k, t)
        if g("flash") >= 0.5:
            self._otis(cam, tr, t)
            arr = np.asarray(img).astype(np.float32)
            sep = arr @ np.array([[0.393, 0.349, 0.272], [0.769, 0.686, 0.534], [0.189, 0.168, 0.131]],
                                 dtype=np.float32)
            img.paste(Image.fromarray(np.clip(sep * 0.9 + 14, 0, 255).astype(np.uint8)))
            return
        build = g("build")
        car_z = g("car_z")
        cx = g("swing") * 0.10 * math.sin(t * 11)
        cw_z = 8.6 - car_z
        cws = g("cw_show")
        self._building(cam, tr, t, build, car_z)
        # soft projected shadows + ambient occlusion (drawn under everything that moves)
        sh = ShadowLayer(cam)
        hb = TOP * min(1.0, build * 1.2)
        if hb > 0.5:
            for a, b in (((0, 0, 0), (0, 0, hb)),):
                sh.ao_edge(a, b, (1, 0, 0), (0, 1, 0), 0.30, 150)
            sh.ao_edge((0, 0, 0), (2.2, 0, 0), (0, 1, 0), (0, 0, 1), 0.25, 140)
            sh.ao_edge((0, 0, 0), (0, 2.0, 0), (1, 0, 0), (0, 0, 1), 0.25, 140)
            sh.ao_edge((0, 0, hb), (2.2, 0, hb), (0, 1, 0), (0, 0, -1), 0.2, 90)
        cs0 = g("car_show")
        if cs0 > 0.5 and hb > 2:
            zz = car_z
            clip_y = ((0, 2.2), (0, 0), (0, hb))
            clip_x = ((0, 0), (0, 2.0), (0, hb))
            sh.box_on_plane(0.45 + cx, 0.3, zz - 0.12, 1.5, 1.4, 2.27, "y", 0.0, 230, clip_y)
            sh.box_on_plane(0.45 + cx, 0.3, zz - 0.12, 1.5, 1.4, 2.27, "x", 0.0, 200, clip_x)
            if car_z < 2.8:
                sh.box_on_plane(0.45 + cx, 0.3, zz - 0.12, 1.5, 1.4, 2.27, "z", 0.0, int(250 - 60 * (car_z - 1)),
                                ((0, 2.2), (0, 2.0), (0, 0)))
        if cws > 0.5 and hb > 2:
            sh.box_on_plane(0.04, 0.45, cw_z, 0.2, 1.1, 1.3, "y", 0.0, 200, ((0, 2.2), (0, 0), (0, hb)))
        sh.apply(img, 0.30, 2.6)
        # pit buffers
        bu = g("buffers")
        if bu > 0.01:
            for bx in (CX - 0.38, CX + 0.38):
                cam.spring((bx, 1.0, 0.0), 0.55 * bu, 0.12, (60, 60, 70), 6, 0.035)
                cam.box(bx - 0.16, 0.84, 0.55 * bu, 0.32, 0.32, 0.06, RED)
            cam.spring((0.14, 1.0, 0.0), 0.4 * bu, 0.07, (60, 60, 70), 5, 0.03)
            cam.box(0.02, 0.88, 0.4 * bu, 0.24, 0.24, 0.05, RED)
        # counterweight on the left wall
        if cws > 0.01:
            drop = (1 - min(1.0, cws)) * 3.0
            cam.box(0.04, 0.45, cw_z + drop, 0.2, 1.1, 1.3, (95, 100, 115))
            for k in range(4):
                zz = cw_z + drop + 0.3 * k + 0.2
                cam.line([(0.24, 0.45, zz), (0.24, 1.55, zz)], (70, 74, 86), 0.012, caps=False)
        rails = g("rails")
        if rails > 0.01:
            cam.box(0.27, 0.92, 0, 0.1, 0.16, TOP * rails, METAL)
            for bz in np.arange(0.8, TOP * rails, 1.6):
                cam.box(0.0, 0.88, bz, 0.3, 0.24, 0.1, (120, 126, 140))
                parts.bolt(cam, (0.3, 1.0, bz + 0.05), 0.025)
        cs = g("car_show")
        gov = g("gov")
        if cs > 0.01:
            self._car(cam, tr, t, cx, car_z, cs, gov)
        # ropes
        rs = g("rope_show")
        n_ropes = int(round(g("ropes")))
        strain = g("strain")
        if rs > 0.01 and cs > 0.5:
            for k in range(n_ropes):
                off = (k - (n_ropes - 1) / 2) * 0.09
                z1 = car_z + 2.15 + (TOP - car_z - 2.15) * rs
                col = (60, 50, 45) if strain < 0.5 or int(t * 10) % 2 else RED
                cam.line([(CX + cx, 1.0 + off, car_z + 2.15), (CX, 1.0 + off, z1)], col, 0.03)
                for m in np.arange(car_z + 2.35, z1 - 0.05, 0.7):
                    cam.line([(CX, 1.0 + off, m), (CX, 1.0 + off, m + 0.12)], (190, 170, 140), 0.03, caps=False)
                if cws > 0.01:
                    cam.line([(0.2, 1.0 + off, cw_z + 1.3), (0.2, 1.0 + off, TOP)], (60, 50, 45), 0.03)
                    for m in np.arange(cw_z + 1.5, TOP - 0.05, 0.7):
                        cam.line([(0.2, 1.0 + off, m), (0.2, 1.0 + off, m + 0.12)], (190, 170, 140), 0.03,
                                 caps=False)
        # front-right rail and governor rope
        if rails > 0.01:
            cam.box(2.03, 0.92, 0, 0.1, 0.16, TOP * rails, METAL)
            for bz in np.arange(0.8, TOP * rails, 1.6):
                parts.bolt(cam, (2.13, 1.0, bz + 0.05), 0.025)
        if gov > 0.01:
            zt = 0.3 + (TOP + 0.5 - 0.3) * gov
            for yy in (1.57, 1.93):
                cam.line([(2.12, yy, 0.3), (2.12, yy, zt)], (110, 80, 50), 0.022)
            cam.wheel((2.12, 1.75, 0.3), 0.18, 0.06, (120, 120, 130), "x", 0)
            cam.line([(1.95 + cx, 1.57, car_z + 1.3), (2.12, 1.57, car_z + 1.3)], (80, 80, 90), 0.035)
            cam.box(2.08, 1.53, car_z + 1.24, 0.08, 0.08, 0.12, RED)
        ts = g("top_show")
        if ts > 0.01:
            f0 = cam.f
            cam.f = (f0[0], f0[1], f0[2] - (1 - min(1.0, ts)) * 2.5)
            self._top(cam, tr, t, car_z, n_ropes, cws)
            cam.f = f0
        sen = g("sensor")
        if sen > 0.01:
            for fz in FLOORS:
                cam.box(2.03, 1.08, fz - 0.12, 0.1, 0.1, 0.26 * sen, BLUE)
            pz = car_z + 0.1
            cam.line([(2.0, 1.12, pz), (2.0, 1.12, pz + 0.35)], (110, 200, 255), 0.04)

    # -------------------------------------------------------------- pieces
    def _building(self, cam, tr, t, build, car_z):
        g = lambda k: tr.get(k, t)
        h = TOP * min(1.0, build * 1.2)
        # lawn
        cam.poly([(-4, -4, 0.7), (7, -4, 0.7), (7, 7, 0.7), (-4, 7, 0.7)], (214, 230, 200))
        # facade walls continuing the back walls of the shaft (rise in at the end of the hook)
        hf = 0.7 + (TOP - 0.7) * g("facade")
        if hf > 0.75:
            cam.poly([(2.2, 0, 0.7), (5.2, 0, 0.7), (5.2, 0, hf), (2.2, 0, hf)], FACADE, shade(FACADE, -0.2), 0.01)
            cam.poly([(0, 2.0, 0.7), (0, 4.6, 0.7), (0, 4.6, hf), (0, 2.0, hf)], shade(FACADE, -0.1),
                     shade(FACADE, -0.25), 0.01)
        for fz in FLOORS:
            if fz + 1.9 > hf:
                continue
            for wx in (2.9, 4.1):
                cam.poly([(wx, 0.01, fz + 0.7), (wx + 0.7, 0.01, fz + 0.7), (wx + 0.7, 0.01, fz + 1.8),
                          (wx, 0.01, fz + 1.8)], (170, 205, 235), shade(FACADE, -0.4), 0.015)
            for wy in (2.7, 3.7):
                cam.poly([(0.01, wy, fz + 0.7), (0.01, wy + 0.6, fz + 0.7), (0.01, wy + 0.6, fz + 1.8),
                          (0.01, wy, fz + 1.8)], (150, 185, 215), shade(FACADE, -0.4), 0.015)
            cam.line([(2.2, 0.01, fz - 0.15), (5.2, 0.01, fz - 0.15)], shade(FACADE, -0.25), 0.03, caps=False)
            cam.line([(0.01, 2.0, fz - 0.15), (0.01, 4.6, fz - 0.15)], shade(FACADE, -0.3), 0.03, caps=False)
        # shaft walls
        cam.poly([(0, 0, 0), (0, 2.0, 0), (0, 2.0, h), (0, 0, h)], shade(WALL, -0.08), shade(WALL, -0.3), 0.012)
        cam.poly([(0, 0, 0), (2.2, 0, 0), (2.2, 0, h), (0, 0, h)], WALL, shade(WALL, -0.3), 0.012)
        cam.poly([(0, 0, 0), (2.2, 0, 0), (2.2, 2.0, 0), (0, 2.0, 0)], shade(WALL, -0.2))
        parts.panel_seams(cam, "x", 0.005, 0.0, 2.0, 0.0, h, 0.5, shade(WALL, -0.12), 0.006)
        for fz in FLOORS:
            if fz < h:
                cam.line([(0.005, 0, fz - 0.15), (0.005, 2.0, fz - 0.15)], shade(WALL, -0.18), 0.012, caps=False)
                cam.line([(0, 0.005, fz - 0.15), (2.2, 0.005, fz - 0.15)], shade(WALL, -0.18), 0.012, caps=False)
        # landing doors in the back wall
        locks = g("locks")
        for i, fz in enumerate(FLOORS):
            if fz + 2.2 > h:
                continue
            here = abs(car_z - fz) < 0.5
            op = g("door2") if i == 1 else 0.0
            x0, x1 = DOOR_X0, DOOR_X1
            if op > 0.01:
                cam.poly([(x0, 0.0, fz), (x1, 0.0, fz), (x1, 0.0, fz + 2.1), (x0, 0.0, fz + 2.1)], CORRIDOR)
                cam.poly([(x0, 0.0, fz), (x1, 0.0, fz), (x1, -0.6, fz), (x0, -0.6, fz)], (230, 200, 160))
                vis = g("visitor")
                if vis > 0.01 and not here:
                    vy = -0.45 + 0.5 * g("visitor_x")
                    draw_peg(cam, (CX, vy, fz), PEG_COLORS[4], "shocked" if g("visitor_x") > 0.3 else "neutral",
                             t, 1.9 * vis, (0.2, 0.5), seed=5)
            pw = (x1 - x0) / 2 * (1 - op)
            if pw > 0.005:
                cam.box(x0, 0.0, fz, pw, 0.04, 2.08, (196, 202, 214), faces="tl")
                cam.box(x1 - pw, 0.0, fz, pw, 0.04, 2.08, (186, 192, 205), faces="tl")
            # frame + sill
            cam.box(x0 - 0.08, 0.0, fz, 0.08, 0.06, 2.18, (120, 126, 138))
            cam.box(x1, 0.0, fz, 0.08, 0.06, 2.18, (120, 126, 138))
            cam.box(x0 - 0.08, 0.0, fz + 2.1, x1 - x0 + 0.16, 0.06, 0.08, (120, 126, 138))
            cam.box(x0 - 0.08, 0.0, fz - 0.04, x1 - x0 + 0.16, 0.18, 0.04, (150, 150, 160))
            cur = int(round((car_z - 1.0) / 3.0)) + 1
            parts.digital_display(cam, "y", 0.02, CX - 0.2, fz + 2.3, f"{max(1, min(3, cur))}", 0.4, 0.22,
                                  (255, 140, 60) if here else (255, 190, 120))
            # call button + lock
            bx, by = cam.p(x1 + 0.25, 0.02, fz + 1.1)
            r = 0.05 * cam.s
            cam.d.rounded_rectangle((bx - r * 1.4, by - r * 2.4, bx + r * 1.4, by + r * 2.4), radius=r * 0.5,
                                    fill=(70, 74, 86))
            cam.d.ellipse((bx - r, by - r, bx + r, by + r), fill=(255, 210, 80) if here else (235, 235, 235))
            if locks > 0.01:
                lx, ly = cam.p(x0 - 0.35, 0.02, fz + 1.5)
                s2 = 0.12 * cam.s * locks
                ok = here
                cam.d.arc((lx - s2 * 0.6, ly - s2 * 1.0, lx + s2 * 0.6, ly + s2 * 0.3), 180, 360,
                          fill=(60, 60, 70), width=max(1, int(s2 * 0.25)))
                cam.d.rounded_rectangle((lx - s2, ly - s2 * 0.3, lx + s2, ly + s2 * 1.1), radius=s2 * 0.25,
                                        fill=(60, 170, 90) if ok else (226, 52, 64))

    def _side_parts(self, cam, tr, t, shoe_x, brake_x, zz, h, gov):
        if tr.get("rails", t) > 0.5:
            for gz in (zz + 0.05, zz + h - 0.2):
                cam.box(shoe_x, 0.9, gz, 0.08, 0.2, 0.15, (70, 74, 86))
        br = tr.get("brake", t)
        if gov > 0.5 or br > 0.01:
            cam.box(brake_x, 0.86, zz + 0.25, 0.1, 0.28, 0.25, RED if br > 0.5 else (90, 90, 100))

    def _car(self, cam, tr, t, cx, z, cs, gov):
        g = lambda k: tr.get(k, t)
        x0, y0, w, d, h = 0.45 + cx, 0.3, 1.5, 1.4, 2.0
        zz = z + (1 - min(1.0, cs)) * 2.5
        door = g("door2") if abs(z - 4.0) < 0.5 else 0.0
        sq = g("squeeze")
        # left-side guide shoes + safety brake sit behind the left wall: draw them first
        self._side_parts(cam, tr, t, x0 - 0.08, x0 - 0.14, zz, h, gov)
        # left inner wall + floor; back face is the door side
        cam.poly([(x0, y0, zz), (x0, y0 + d, zz), (x0, y0 + d, zz + h), (x0, y0, zz + h)], shade(CAR, -0.22))
        # door opening in the back face
        dx0, dx1 = DOOR_X0 + cx, DOOR_X1 + cx
        cam.poly([(x0, y0, zz), (dx0, y0, zz), (dx0, y0, zz + h), (x0, y0, zz + h)], shade(CAR, -0.1))
        cam.poly([(dx1, y0, zz), (x0 + w, y0, zz), (x0 + w, y0, zz + h), (dx1, y0, zz + h)], shade(CAR, -0.1))
        cam.poly([(dx0, y0, zz + 2.1 if False else zz + 1.95), (dx1, y0, zz + 1.95), (dx1, y0, zz + h),
                  (dx0, y0, zz + h)], shade(CAR, -0.1))
        pw = (dx1 - dx0) / 2 * (1 - door)
        stop = 0.18 if sq > 0.3 else 0.0
        pw = max(0.0, min(pw, (dx1 - dx0) / 2 - stop)) if door > 0 or sq > 0.3 else pw
        if pw > 0.005:
            cam.poly([(dx0, y0 + 0.01, zz), (dx0 + pw, y0 + 0.01, zz), (dx0 + pw, y0 + 0.01, zz + 1.95),
                      (dx0, y0 + 0.01, zz + 1.95)], (205, 210, 220), (130, 136, 150), 0.01)
            cam.poly([(dx1 - pw, y0 + 0.01, zz), (dx1, y0 + 0.01, zz), (dx1, y0 + 0.01, zz + 1.95),
                      (dx1 - pw, y0 + 0.01, zz + 1.95)], (195, 200, 212), (130, 136, 150), 0.01)
        cam.box(x0, y0, zz - 0.12, w, d, 0.12, shade(CAR, -0.3), top_color=(212, 196, 165))
        cam.line([(x0 + 0.05, y0 + 0.08, zz + 0.95), (x0 + 0.05, y0 + d - 0.05, zz + 0.95)], (200, 200, 210), 0.03)
        parts.button_panel(cam, "y", y0 + 0.07, dx1 + 0.06, zz + 0.75, 3,
                           lit=int(round((g("car_z") - 1) / 3)) if abs((g("car_z") - 1) % 3) < 0.2 else None)
        cam.poly([(x0 + 0.08, y0 + 0.07, zz + 1.86), (x0 + w - 0.1, y0 + 0.07, zz + 1.86),
                  (x0 + w - 0.1, y0 + 0.07, zz + 1.92), (x0 + 0.08, y0 + 0.07, zz + 1.92)], (255, 250, 228))
        # light curtain across the door
        cur = g("curtain")
        if cur > 0.01:
            for k in range(9):
                bz = zz + 0.15 + k * 0.2
                col = (255, 60, 60) if int(t * 8 + k) % 3 == 0 else (255, 140, 140)
                cam.line([(dx0, y0 + 0.03, bz), (dx1, y0 + 0.03, bz)], col, 0.03 * cur + 0.006, caps=False)
        # rider with a backpack in the doorway
        if g("rider") > 0.01:
            bx, by = cam.p(CX + cx, y0 + 0.05, zz + 0.6)
            r = 0.15 * cam.s
            cam.d.rounded_rectangle((bx - r, by - r * 1.3, bx + r, by + r * 1.3), radius=r * 0.4,
                                    fill=(90, 150, 90), outline=(40, 70, 40), width=max(1, int(0.01 * cam.s)))
            draw_peg(cam, (CX + cx, y0 + 0.35, zz), PEG_COLORS[3], "worried" if sq > 0.3 else "happy", t,
                     1.9 * g("rider"), (0.0, 0.3), seed=9, pose="cover" if sq > 0.3 else "wave",
                     floor=(212, 196, 165))
        # passengers
        if g("pegs_in") > 0.01:
            expr = tr.peg_expr(t)
            look = (0.3 * math.sin(t * 0.7), 0.1)
            spots = ((0.55, 1.15), (1.05, 1.35), (0.85, 0.75)) if g("rider") > 0.01 else \
                ((0.4, 0.75), (1.0, 0.85), (0.7, 1.3))
            for k, (px, py) in sorted(enumerate(spots), key=lambda e: e[1][0] + e[1][1]):
                pose = tr.peg_pose(t)
                if pose == "wave" and k != 1:
                    pose = "idle"
                since = tr.since_step(t) - 0.15 * k
                react = max(0.0, 1.0 - since / 0.5) if expr == "shocked" and since > 0 else 0.0
                draw_peg(cam, (x0 + px, y0 + py, zz), PEG_COLORS[k], expr, t, 1.9 * g("pegs_in"), look, seed=k,
                         pose=pose, react=react, floor=(212, 196, 165))
        # thin front corner posts + roof
        cam.box(x0 + w - 0.06, y0 + d - 0.06, zz, 0.06, 0.06, h, CAR)
        cam.box(x0, y0 + d - 0.06, zz + h - 0.18, w, 0.06, 0.18, CAR)
        cam.box(x0 + w - 0.06, y0, zz + h - 0.18, 0.06, d, 0.18, CAR)
        cam.box(x0, y0, zz + h, w, d, 0.12, shade(CAR, -0.05))
        # right-side guide shoes + safety brake (in front of the car); left side drawn earlier
        self._side_parts(cam, tr, t, x0 + w, x0 + w + 0.04, zz, h, gov)
        br = g("brake")
        if gov > 0.5 or br > 0.01:
            if br > 0.5 and (t * 20) % 2 < 1.2:
                rnd = random.Random(int(t * 30))
                for _ in range(10):
                    sx = rnd.choice((x0 - 0.12, x0 + w + 0.08))
                    sp = (sx, 1.0, zz + 0.3)
                    ep = (sx + rnd.uniform(-0.3, 0.3), 1.0 + rnd.uniform(-0.3, 0.3), zz + 0.3 + rnd.uniform(0.1, 0.5))
                    cam.line([sp, ep], (255, 190, 40), 0.018)
        if g("falling") > 0.5:
            for k in range(6):
                lz = zz + h + 0.3 + ((t * 9 + k * 0.6) % 3.0)
                lx = x0 + 0.2 + k * 0.22
                cam.line([(lx, y0 + d, lz), (lx, y0 + d, lz + 0.6)], (120, 130, 150), 0.02)
        if g("swing") > 0.5 and math.sin(t * 11) > 0.7:
            for k in range(6):
                rnd = random.Random(int(t * 20) + k)
                sp = (x0, y0 + rnd.uniform(0.2, d), zz + rnd.uniform(0.2, h))
                cam.line([sp, (sp[0] - 0.3, sp[1] + rnd.uniform(-0.2, 0.2), sp[2] + rnd.uniform(-0.2, 0.3))],
                         (255, 180, 40), 0.02)

    def _top(self, cam, tr, t, car_z, n_ropes, cws):
        g = lambda k: tr.get(k, t)
        cam.box(0, 0, TOP, 2.2, 2.0, 0.3, (200, 205, 215))
        glow = g("motor_glow")
        jit = 0.02 * glow * math.sin(t * 60)
        for k in range(n_ropes):
            off = (k - (n_ropes - 1) / 2) * 0.09
            cam.line([(CX, 1.0 + off, TOP + 0.3), (CX, 1.0 + off, SHEAVE[2])], (60, 50, 45), 0.03)
            if cws > 0.01:
                cam.line([(0.24, 1.0 + off, TOP + 0.3), (0.24, 1.0 + off, SHEAVE[2])], (60, 50, 45), 0.03)
        cam.wheel(SHEAVE, SR, 0.3, (110, 116, 130), "y", -car_z / SR, 5, groove=(60, 50, 45))
        mcol = mix((70, 120, 200), RED, glow)
        cam.box(0.42, 1.25, TOP + 0.3, 0.6, 0.7, 0.8, mcol)
        for k in range(5):
            fz = TOP + 0.42 + k * 0.13
            cam.line([(1.02, 1.3, fz), (1.02, 1.9, fz)], shade(mcol, -0.3), 0.015, caps=False)
            cam.line([(0.46, 1.95, fz), (0.98, 1.95, fz)], shade(mcol, -0.2), 0.015, caps=False)
        parts.led(cam, (0.9, 1.96, TOP + 0.98), (255, 70, 70) if glow > 0.5 else (90, 230, 120), True, 0.03)
        cam.box(0.64, 1.12, TOP + 0.72, 0.14, 0.14, 0.14, (90, 90, 100))
        if glow > 0.3:
            for k in range(3):
                ph = (t * 1.2 + k / 3) % 1.0
                bx = 0.55 + k * 0.18
                cam.line([(bx, 1.6, TOP + 1.15 + ph * 0.5), (bx + 0.05 * math.sin(ph * 9), 1.6, TOP + 1.35 + ph * 0.5)],
                         (255, 120, 60), 0.03)
        gov = g("gov")
        if gov > 0.01:
            spin = (car_z / 0.2) if g("fly") < 0.5 else 2.6 / 0.2
            cam.box(1.9, 1.5, TOP + 0.3, 0.4, 0.5, 0.15, (80, 84, 96))
            cam.wheel((2.12, 1.75, TOP + 0.5), 0.2 * min(1.0, gov * 1.4), 0.08, (230, 180, 60), "x", spin, 4)

    def _otis(self, cam, tr, t):
        """1854 flashback: Otis on an open platform, rope gets cut, safety catches."""
        g = lambda k: tr.get(k, t)
        wood = (150, 110, 70)
        cam.poly([(-4, -4, 0), (7, -4, 0), (7, 7, 0), (-4, 7, 0)], (200, 190, 170))
        cam.poly([(-1, -1, 0), (5, -1, 0), (5, -1, 6), (-1, -1, 6)], (215, 205, 185))   # exhibition hall wall
        for px in (0.0, 2.2):
            cam.box(px, 0.9, 0, 0.18, 0.2, 6.4, wood)
            for k in range(1, 6):   # ratchet teeth on the guide posts
                cam.line([(px + (0.18 if px == 0 else 0), 1.0, k), (px + (0.18 if px == 0 else 0), 1.0, k + 0.15)],
                         (90, 70, 50), 0.03)
        cam.box(-0.1, 0.85, 6.4, 2.5, 0.3, 0.25, wood)
        drop = 0.35 * g("otis_drop")
        pz = 3.0 - drop
        cut = g("otis_cut")
        if cut < 0.5:
            cam.line([(1.1, 1.0, pz + 1.6), (1.1, 1.0, 6.4)], (80, 60, 40), 0.045)
        else:
            cam.line([(1.1, 1.0, 5.6), (1.1, 1.0, 6.4)], (80, 60, 40), 0.045)
            cam.line([(1.1, 1.0, pz + 1.6), (1.1, 1.0, pz + 2.2)], (80, 60, 40), 0.045)
        cam.box(0.18, 0.4, pz, 2.02, 1.2, 0.15, (175, 135, 90))
        cam.line([(0.25, 1.0, pz + 0.15), (1.1, 1.0, pz + 1.6), (1.95, 1.0, pz + 0.15)], (80, 60, 40), 0.035)
        draw_peg(cam, (1.0, 0.9, pz + 0.15), (220, 200, 170), "happy" if drop > 0.3 else "neutral", t, 2.2,
                 (0.4, 0.3), hat=True, seed=3)
        if drop > 0.3:
            for sx in (0.12, 2.25):
                for k in range(5):
                    cam.line([(sx, 1.0, pz + 0.1), (sx + (k - 2) * 0.08, 1.2, pz + 0.3 + k * 0.05)], (255, 200, 80), 0.025)
        for k in range(8):
            draw_peg(cam, (2.5 + (k % 4) * 0.5, 0.2 + (k // 4) * 0.7 + (k % 2) * 0.15, 0), PEG_COLORS[k % 5],
                     "shocked" if cut > 0.5 and drop < 0.3 else ("happy" if drop > 0.3 else "neutral"),
                     t, 2.0, (-0.5, -0.8), seed=k)
        if 0 < t - tr.cut_time < 0.6 or (cut < 0.5 and 0 < tr.cut_time - t < 0.8):
            sx, sy = cam.p(1.1, 1.0, 5.6)
            r = 0.25 * cam.s
            cam.d.line((sx - r, sy - r, sx + r, sy + r), fill=(60, 60, 70), width=int(0.05 * cam.s))
            cam.d.line((sx - r, sy + r, sx + r, sy - r), fill=(60, 60, 70), width=int(0.05 * cam.s))


def draw_bubble(img, kind, k, t, tr, W, H):
    """Magnifier bubble with a schematic close-up / comparison."""
    if k <= 0.01:
        return
    d = ImageDraw.Draw(img)
    cx, cy, R = W * 0.70, H * 0.33, W * 0.24 * k
    d.ellipse((cx - R - 8, cy - R - 8, cx + R + 8, cy + R + 8), fill=(35, 35, 45))
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 255))
    u = R / 100.0
    lw = max(2, int(4 * u))
    if kind == 1:   # seesaw
        ang = math.radians(4 * math.sin(t * 2))
        d.polygon([(cx - 12 * u, cy + 40 * u), (cx + 12 * u, cy + 40 * u), (cx, cy + 15 * u)], fill=(90, 90, 100))
        ca, sa = math.cos(ang), math.sin(ang)
        p1 = (cx - 70 * u * ca, cy + 15 * u - 70 * u * sa)
        p2 = (cx + 70 * u * ca, cy + 15 * u + 70 * u * sa)
        d.line((p1, p2), fill=(120, 90, 60), width=int(8 * u))
        d.rectangle((p1[0] - 4 * u, p1[1] - 50 * u, p1[0] + 36 * u, p1[1] - 4 * u), fill=CAR, outline=(60, 50, 30),
                    width=lw)
        d.rectangle((p2[0] - 30 * u, p2[1] - 40 * u, p2[0] + 4 * u, p2[1] - 4 * u), fill=(95, 100, 115))
        d.text((cx, cy - 62 * u), "car  ≈  weight", font=font(int(16 * u)), fill=(30, 30, 40), anchor="mm")
    elif kind == 2:   # governor flyweights
        fly = tr.get("fly", t)
        spin = t * (14 if tr.get("falling", t) > 0.5 else 2)
        d.ellipse((cx - 70 * u, cy - 70 * u, cx + 70 * u, cy + 70 * u), outline=(60, 60, 70), width=lw)
        for k2 in range(16):   # ratchet teeth on the rim
            a = 2 * math.pi * k2 / 16
            d.line((cx + 70 * u * math.cos(a), cy + 70 * u * math.sin(a),
                    cx + 82 * u * math.cos(a + 0.15), cy + 82 * u * math.sin(a + 0.15)), fill=(60, 60, 70), width=lw)
        for sgn in (-1, 1):
            a = spin + (0 if sgn > 0 else math.pi)
            r = (25 + 32 * fly) * u
            px, py = cx + r * math.cos(a), cy + r * math.sin(a)
            d.line((cx, cy, px, py), fill=(90, 90, 100), width=lw)
            d.ellipse((px - 14 * u, py - 14 * u, px + 14 * u, py + 14 * u), fill=RED if fly > 0.6 else (230, 180, 60))
        d.ellipse((cx - 8 * u, cy - 8 * u, cx + 8 * u, cy + 8 * u), fill=(40, 40, 50))
        d.text((cx, cy + 92 * u), "flyweights", font=font(int(15 * u)), fill=(30, 30, 40), anchor="mm")
    elif kind == 3:   # fire pole
        d.rectangle((cx - 6 * u, cy - 85 * u, cx + 6 * u, cy + 85 * u), fill=(190, 190, 200))
        sq = 0.5 + 0.5 * math.sin(t * 6)
        for sgn in (-1, 1):
            hx = cx + sgn * (14 + 8 * (1 - sq)) * u
            d.rounded_rectangle((hx - 14 * u, cy - 20 * u, hx + 14 * u, cy + 20 * u), radius=8 * u,
                                fill=(255, 190, 150), outline=(120, 70, 50), width=lw)
        for k2 in range(4):
            d.line((cx - 40 * u, cy + (30 + k2 * 12) * u, cx - 30 * u, cy + (40 + k2 * 12) * u), fill=(255, 170, 40),
                   width=lw)


def draw_cta(img, k, t, W, H):
    if k <= 0.01:
        return
    d = ImageDraw.Draw(img)
    w, h = W * 0.5 * k, W * 0.12 * k
    cx, cy = W * 0.5, H * 0.80
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h * 0.5, fill=(230, 30, 40),
                        outline=(30, 30, 40), width=max(2, int(W * 0.004)))
    d.text((cx, cy), "FOLLOW FOR MORE", font=font(int(W * 0.045 * k)), fill=(255, 255, 255), anchor="mm")


def overlays(img, tr, t, W, H):
    draw_bubble(img, int(round(tr.get("bubble_kind", t))), tr.get("bubble", t), t, tr, W, H)


VIDEO = dict(
    slug="elevator",
    title="How does an elevator not fall?",
    steps=STEPS, scene=ElevatorScene, initial=INITIAL, overlays=overlays, tracker=dict(label="FIXES"),
)


def main(argv=None):
    import argparse
    from .builder import build_explainer
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="output/elevator_explainer.mp4")
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--preview", default=None, help="save a contact sheet PNG instead of a video")
    a = ap.parse_args(argv)
    if a.preview:
        frames, starts, durs, keys = build_explainer(STEPS, ElevatorScene, None, INITIAL, overlays, ss=a.ss,
                                                     preview_frames=[(i, f) for i in range(len(STEPS))
                                                                     for f in (0.3, 0.85)])
        w, h = frames[0].size
        sc = 0.25
        tw, th = int(w * sc), int(h * sc)
        cols = 10
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * th), "white")
        for k, im in enumerate(frames):
            sheet.paste(im.resize((tw, th), Image.LANCZOS), ((k % cols) * tw, (k // cols) * th))
        sheet.save(a.preview)
        print("durations", [round(x, 1) for x in durs], "total", round(sum(durs), 1))
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    build_explainer(STEPS, ElevatorScene, a.out, INITIAL, overlays, ss=a.ss, tracker=dict(label="FIXES"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
