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
from .mascots import PEG_COLORS, draw_peg

RED, BLUE, INK = (226, 52, 64), (40, 110, 235), (25, 25, 32)

# ----------------------------------------------------------------- the script
# Each step: narration text, on-screen keyword (+ color), camera (focus xyz, zoom in px/unit at
# 1080 px width), passenger expression, minimum duration and timed actions on animation tracks:
#   (track, seconds_from_step_start, value, transition_seconds, ease)
WIDE = ((1.9, 1.3, 5.6), 112)
STEPS = [
    dict(text="If you put a box on a rope and hang it from a motor at the top of a shaft, "
              "you've got the world's simplest elevator.",
         label="the simplest elevator", color=INK, cam=WIDE, pegs="neutral",
         do=[("build", 0, 1, 2.2, "out"), ("car_show", 1.0, 1, 0.6, "back"), ("rope_show", 1.6, 1, 0.5, "out")],
         sfx=[(1.0, "pop")]),
    dict(text="Press the button, the motor winds up the rope, and your passengers ride to the third floor.",
         label="going up", color=BLUE, cam=((1.5, 1.0, 6.2), 130), pegs="happy",
         do=[("pegs_in", 0, 1, 0.4, "back"), ("car_z", 1.0, 7.0, 3.0, "io")], sfx=[(4.0, "ding")]),
    dict(text="But hauling the whole car plus everyone inside takes a monster of a motor.",
         label="a monster motor", color=RED, cam=((0.8, 1.2, 10.8), 290), pegs="worried",
         do=[("motor_glow", 0.2, 1, 0.5, "out")], sfx=[(0.2, "sting")]),
    dict(text="So you hang a heavy block on the other end of the rope. That's the counterweight.",
         label="counterweight", color=INK, cam=((0.9, 1.0, 6.2), 135), pegs="neutral",
         do=[("motor_glow", 0, 0, 0.5, "io"), ("cw_show", 0.3, 1, 0.9, "back")], sfx=[(0.4, "whoosh")]),
    dict(text="It weighs about as much as the empty car plus half a full load, so the motor only moves the "
              "difference. It's a seesaw where your friend is already sitting on the other side.",
         label="only the difference", color=BLUE, cam=((0.9, 1.0, 6.2), 135), pegs="happy",
         do=[("bubble", 3.2, 1, 0.5, "back"), ("bubble_kind", 0, 1, 0, "lin"), ("bubble", 99, 0, 0.3, "in")],
         bubble_off=True),
    dict(text="And instead of winding the rope, the motor just spins a grooved wheel, and friction drags "
              "the ropes along. That's the traction sheave.",
         label="traction sheave", color=INK, cam=((0.75, 1.0, 10.7), 280), pegs="neutral",
         do=[("car_z", 0.6, 4.0, 3.5, "io")]),
    dict(text="Smooth ride. Until the car starts swinging and scraping the walls.",
         label="scraping", color=RED, cam=((1.2, 1.0, 5.1), 190), pegs="shocked",
         do=[("swing", 0.9, 1, 0.3, "out")], sfx=[(0.9, "slap")]),
    dict(text="So you bolt steel rails up both sides of the shaft, and the car slides along them on guide shoes.",
         label="guide rails", color=INK, cam=((1.2, 1.0, 5.4), 150), pegs="happy",
         do=[("swing", 0.2, 0, 0.4, "out"), ("rails", 0.2, 1, 1.6, "out")], sfx=[(0.2, "whoosh")]),
    dict(text="Then someone in the car asks the obvious question. What if the rope snaps?",
         label="what if it snaps?", color=RED, cam=((1.2, 1.0, 7.8), 210), pegs="worried",
         do=[("strain", 1.5, 1, 0.3, "out")]),
    dict(text="So you don't use one rope. You use several, and each one is strong enough to hold the car by itself.",
         label="several ropes", color=INK, cam=((1.2, 1.0, 7.8), 210), pegs="happy",
         do=[("strain", 0, 0, 0.3, "out"), ("ropes", 0.4, 4, 1.4, "out")], sfx=[(0.4, "pop")]),
    dict(text="But what if the car starts falling anyway? In 1854, Elisha Otis stood on a platform high above "
              "a crowd in New York, and had the only rope cut.",
         label="1854", color=INK, cam=((1.7, 1.0, 3.2), 175), pegs="worried",
         do=[("flash", 2.1, 1, 0, "lin"), ("otis_cut", 99, 1, 0, "lin")], cut_at_end=True,
         sfx=[(2.1, "whoosh")]),
    dict(text="The platform dropped a few inches. And stopped.",
         label="it stopped", color=BLUE, cam=((1.4, 1.0, 3.4), 200), pegs="happy", min=3.0,
         do=[("otis_drop", 0.25, 1, 0.45, "in")], sfx=[(0.7, "thud")]),
    dict(text="Today's version works like this. A second rope runs from the car up to a small wheel at the top. "
              "That's the governor.",
         label="governor", color=INK, cam=((1.9, 1.6, 9.6), 220), pegs="neutral",
         do=[("flash", 0, 0, 0, "lin"), ("gov", 1.2, 1, 1.2, "out")], sfx=[(1.2, "pop")]),
    dict(text="If the car goes too fast, weights inside the governor swing outward and lock the wheel.",
         label="too fast", color=RED, cam=((1.5, 1.2, 5.6), 140), pegs="shocked",
         do=[("falling", 0.2, 1, 0, "lin"), ("car_z", 0.2, 2.6, 3.2, "in"), ("bubble_kind", 0, 2, 0, "lin"),
             ("bubble", 0.5, 1, 0.4, "back"), ("fly", 1.6, 1, 0.8, "out")], sfx=[(0.2, "whoosh")]),
    dict(text="The locked wheel grabs the rope, the rope yanks a lever on the car, and steel wedges clamp onto "
              "the rails. That's the safety brake.",
         label="safety brake", color=INK, cam=((1.2, 1.0, 3.7), 210), pegs="shocked",
         do=[("bubble", 0, 0, 0.3, "in"), ("brake", 1.6, 1, 0.25, "out"), ("falling", 1.6, 0, 0, "lin"),
             ("car_z", 1.6, 2.6, 0, "lin")], sfx=[(1.6, "thud")]),
    dict(text="It's like grabbing a fire pole with both hands while you're sliding down.",
         label="grab the pole", color=BLUE, cam=((1.2, 1.0, 3.7), 210), pegs="happy",
         do=[("bubble_kind", 0, 3, 0, "lin"), ("bubble", 0.1, 1, 0.4, "back"), ("bubble", 99, 0, 0.3, "in")],
         bubble_off=True),
    dict(text="And just in case, you put giant springs at the bottom of the pit. Those are the buffers.",
         label="buffers", color=INK, cam=((1.2, 1.0, 1.2), 210), pegs="neutral",
         do=[("brake", 0.5, 0, 0.3, "io"), ("car_z", 0.5, 4.0, 2.0, "io"), ("buffers", 0.6, 1, 1.0, "back")],
         sfx=[(0.6, "boing")]),
    dict(text="Now the car is safe. The doors aren't. Open a door on the wrong floor, and there's nothing "
              "behind it but an empty shaft.",
         label="empty shaft", color=RED, cam=((1.2, 0.5, 5.4), 175), pegs="neutral",
         do=[("car_z", 0.3, 7.0, 2.4, "io"), ("visitor", 1.0, 1, 0.5, "back"), ("door2", 2.4, 1, 0.8, "io"),
             ("visitor_x", 3.4, 1, 1.4, "io")], sfx=[(2.4, "sting")]),
    dict(text="So every landing door gets a lock that only releases when the car is right there. And the car "
              "won't move until every door is shut and locked.",
         label="door interlock", color=INK, cam=((1.2, 0.5, 5.4), 165), pegs="neutral",
         do=[("visitor_x", 0, 0, 0.6, "io"), ("door2", 0.3, 0, 0.7, "io"), ("locks", 0.9, 1, 0.6, "back")],
         sfx=[(0.9, "click")]),
    dict(text="Then the doors close on someone's backpack.",
         label="ouch", color=RED, cam=((1.2, 0.5, 5.0), 230), pegs="worried",
         do=[("car_z", 0, 4.0, 2.0, "io"), ("door2", 1.8, 1, 0.5, "io"), ("visitor", 0, 0, 0, "lin"),
             ("pegs_in", 0, 0, 0.4, "in"),
             ("rider", 1.8, 1, 0.3, "back"), ("squeeze", 2.4, 1, 0.25, "in")], sfx=[(2.6, "slap")], min=3.2),
    dict(text="So you shine a curtain of invisible infrared beams across the doorway. Break a beam, and the doors "
              "pop back open.",
         label="light curtain", color=INK, cam=((1.2, 0.5, 5.0), 230), pegs="happy",
         do=[("curtain", 0.4, 1, 0.5, "out"), ("squeeze", 2.6, 0, 0.3, "out")], sfx=[(2.6, "pop")]),
    dict(text="Last problem. The car stops two inches below the floor, and everyone trips on the step.",
         label="trip hazard", color=RED, cam=((1.2, 0.5, 4.8), 250), pegs="shocked",
         do=[("door2", 0, 0, 0.4, "io"), ("curtain", 0, 0, 0.3, "io"),
             ("car_z", 0.6, 3.72, 1.0, "io"), ("door2", 1.7, 1, 0.5, "io")], sfx=[(2.6, "thud")]),
    dict(text="So sensors on the rails tell the controller exactly where the car is, and it creeps the last bit "
              "to stop perfectly level.",
         label="leveling", color=INK, cam=((1.4, 0.7, 4.8), 240), pegs="happy",
         do=[("sensor", 0.4, 1, 0.5, "back"), ("door2", 0.4, 0, 0.4, "io"), ("car_z", 2.4, 4.0, 1.4, "io"),
             ("door2", 4.0, 1, 0.5, "io")], sfx=[(4.0, "ding")]),
    dict(text="So next time the doors bounce back open when your bag gets in the way, you'll know who saw it.",
         label="now you know", color=BLUE, cam=((1.2, 0.5, 5.0), 210), pegs="happy",
         do=[("curtain", 0.3, 1, 0.4, "out")]),
    dict(text="And congratulations, you just built an elevator. Now you just need to stop people from pressing "
              "every single button. Follow for more.",
         label="you built an elevator!", color=BLUE, cam=WIDE, pegs="happy",
         do=[("curtain", 0, 0, 0.4, "io"), ("door2", 0, 0, 0.4, "io"), ("cta", 4.0, 1, 0.5, "back"),
             ("pegs_in", 0, 1, 0.4, "back"), ("rider", 0, 0, 0.3, "in")],
         sfx=[(4.0, "pop")], min=6.0),
]

INITIAL = dict(build=0, car_show=0, rope_show=0, car_z=1.0, pegs_in=0, motor_glow=0, cw_show=0, bubble=0,
               bubble_kind=0, swing=0, rails=0, strain=0, ropes=1, flash=0, otis_cut=0, otis_drop=0, gov=0,
               falling=0, fly=0, brake=0, buffers=0, visitor=0, visitor_x=0, door2=0, locks=0, rider=0,
               squeeze=0, curtain=0, sensor=0, cta=0)

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
        # pit buffers
        bu = g("buffers")
        if bu > 0.01:
            for bx in (CX - 0.38, CX + 0.38):
                cam.spring((bx, 1.0, 0.0), 0.55 * bu, 0.12, (60, 60, 70), 6, 0.035)
                cam.box(bx - 0.16, 0.84, 0.55 * bu, 0.32, 0.32, 0.06, RED)
            cam.spring((0.14, 1.0, 0.0), 0.4 * bu, 0.07, (60, 60, 70), 5, 0.03)
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
                if cws > 0.01:
                    cam.line([(0.2, 1.0 + off, cw_z + 1.3), (0.2, 1.0 + off, TOP)], (60, 50, 45), 0.03)
        # front-right rail and governor rope
        if rails > 0.01:
            cam.box(2.03, 0.92, 0, 0.1, 0.16, TOP * rails, METAL)
        if gov > 0.01:
            zt = 0.3 + (TOP + 0.5 - 0.3) * gov
            for yy in (1.57, 1.93):
                cam.line([(2.12, yy, 0.3), (2.12, yy, zt)], (110, 80, 50), 0.022)
            cam.wheel((2.12, 1.75, 0.3), 0.18, 0.06, (120, 120, 130), "x", 0)
            cam.line([(1.95 + cx, 1.57, car_z + 1.3), (2.12, 1.57, car_z + 1.3)], (80, 80, 90), 0.035)
            cam.box(2.08, 1.53, car_z + 1.24, 0.08, 0.08, 0.12, RED)
        if build > 0.6:
            self._top(cam, tr, t, car_z, n_ropes, cws)
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
        # facade walls continuing the back walls of the shaft
        cam.poly([(2.2, 0, 0.7), (5.2, 0, 0.7), (5.2, 0, h), (2.2, 0, h)], FACADE, shade(FACADE, -0.2), 0.01)
        cam.poly([(0, 2.0, 0.7), (0, 4.6, 0.7), (0, 4.6, h), (0, 2.0, h)], shade(FACADE, -0.1), shade(FACADE, -0.25), 0.01)
        for fz in FLOORS:
            if fz + 1.0 > h:
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
            cam.text((CX, 0.02, fz + 2.45), str(i + 1), 0.3, (80, 86, 100))
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

    def _car(self, cam, tr, t, cx, z, cs, gov):
        g = lambda k: tr.get(k, t)
        x0, y0, w, d, h = 0.45 + cx, 0.3, 1.5, 1.4, 2.0
        zz = z + (1 - min(1.0, cs)) * 2.5
        door = g("door2") if abs(z - 4.0) < 0.5 else 0.0
        sq = g("squeeze")
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
                     1.9 * g("rider"), (0.0, 0.3), seed=9)
        # passengers
        if g("pegs_in") > 0.01:
            expr = tr.peg_expr(t)
            look = (0.3 * math.sin(t * 0.7), 0.1)
            spots = ((0.55, 1.15), (1.05, 1.35), (0.85, 0.75)) if g("rider") > 0.01 else \
                ((0.4, 0.75), (1.0, 0.85), (0.7, 1.3))
            for k, (px, py) in sorted(enumerate(spots), key=lambda e: e[1][0] + e[1][1]):
                draw_peg(cam, (x0 + px, y0 + py, zz), PEG_COLORS[k], expr, t, 1.9 * g("pegs_in"), look, seed=k)
        # thin front corner posts + roof
        cam.box(x0 + w - 0.06, y0 + d - 0.06, zz, 0.06, 0.06, h, CAR)
        cam.box(x0, y0 + d - 0.06, zz + h - 0.18, w, 0.06, 0.18, CAR)
        cam.box(x0 + w - 0.06, y0, zz + h - 0.18, 0.06, d, 0.18, CAR)
        cam.box(x0, y0, zz + h, w, d, 0.12, shade(CAR, -0.05))
        # guide shoes, safety brakes, sparks
        if g("rails") > 0.5:
            for gx in (x0 - 0.08, x0 + w):
                for gz in (zz + 0.05, zz + h - 0.2):
                    cam.box(gx, 0.9, gz, 0.08, 0.2, 0.15, (70, 74, 86))
        br = g("brake")
        if gov > 0.5 or br > 0.01:
            col = RED if br > 0.5 else (90, 90, 100)
            for gx in (x0 - 0.14, x0 + w + 0.04):
                cam.box(gx, 0.86, zz + 0.25, 0.1, 0.28, 0.25, col)
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
    draw_cta(img, tr.get("cta", t), t, W, H)


def main(argv=None):
    import argparse
    from .builder import build_explainer
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="output/elevator_explainer.mp4")
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--preview", default=None, help="save a contact sheet PNG instead of a video")
    a = ap.parse_args(argv)
    if a.preview:
        frames, starts, durs = build_explainer(STEPS, ElevatorScene, None, INITIAL, overlays, ss=a.ss,
                                               preview_frames=[(i, f) for i in range(len(STEPS)) for f in (0.3, 0.85)])
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
    build_explainer(STEPS, ElevatorScene, a.out, INITIAL, overlays, ss=a.ss)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
