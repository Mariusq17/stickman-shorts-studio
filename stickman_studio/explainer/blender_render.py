"""Blender path: plan with the narration engine, render the 3D scene in Blender (Eevee),
then composite sky, keywords, pop-ups and bubbles in Python and mux the audio.

python -m stickman_studio.explainer.blender_render -o out.mp4 [--until 9] [--samples 16]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image

from .builder import build_explainer, draw_key, draw_pop
from .elevator import INITIAL, STEPS, ElevatorScene, draw_bubble

HERE = os.path.dirname(os.path.abspath(__file__))
TRACKS = ["build", "car_show", "rope_show", "top_show", "facade", "car_z", "pegs_in", "door2", "cw_show",
          "rails", "ropes", "gov", "brake", "buffers", "swing", "motor_glow"]
VIEW = np.array([0.62, 0.62, 0.48]) / np.linalg.norm([0.62, 0.62, 0.48])


class PerspCam:
    """Same projection as the Blender camera (for arrow pop-ups)."""

    def __init__(self, focus, zoom, W, H, lens=60.0, shift_y=0.06):
        self.W, self.H = W, H
        f = np.array(focus, float)
        dist = (1080.0 / zoom) * lens / 36.0
        self.pos = f + VIEW * dist
        fwd = -VIEW
        right = np.cross(fwd, [0, 0, 1.0])
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        self.R = (right, up, fwd)
        self.fpx = lens / 36.0 * W
        self.cy = H / 2 + shift_y * max(W, H)
        self.s = zoom * W / 1080.0

    def p(self, x, y, z):
        v = np.array([x, y, z], float) - self.pos
        r, u, f = self.R
        zc = max(1e-3, v @ f)
        return (self.W / 2 + self.fpx * (v @ r) / zc, self.cy - self.fpx * (v @ u) / zc)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="output/elevator_blender.mp4")
    ap.add_argument("--until", type=float, default=None, help="render only the first N seconds")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--blender", default=shutil.which("blender") or "blender")
    ap.add_argument("--keep", default=None, help="keep rendered frames in this folder")
    a = ap.parse_args(argv)
    W, H = 1080, 1920
    plan = build_explainer(STEPS, ElevatorScene, None, INITIAL, None, return_plan=True)
    tr, keys, pops, total = plan["tracks"], plan["keys"], plan["pops"], plan["total"]
    t_end = min(total, a.until) if a.until else total
    n = int(math.ceil(t_end * a.fps))
    states = []
    for k in range(n):
        t = k / a.fps
        st = {name: float(tr.get(name, t)) for name in TRACKS}
        st["cam_f"] = list(tr.get("cam_f", t))
        st["cam_z"] = float(tr.get("cam_z", t))
        states.append(st)
    work = a.keep or tempfile.mkdtemp(prefix="bl_elev_")
    os.makedirs(work, exist_ok=True)
    sp = os.path.join(work, "states.json")
    with open(sp, "w") as f:
        json.dump(states, f)
    frames_dir = os.path.join(work, "frames")
    cmd = [a.blender, "-b", "-noaudio", "--python", os.path.join(HERE, "bl_elevator_scene.py"), "--", sp,
           frames_dir, str(W), str(H), str(a.samples)]
    print("Blender:", " ".join(cmd))
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    # ------------------------------------------------ composite + encode
    import imageio_ffmpeg
    bg = ElevatorScene(W, H).bg
    wav = plan["wav"]
    if a.until:
        cut = os.path.join(work, "audio.wav")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", wav, "-t", f"{t_end:.3f}", cut],
                       check=True)
        wav = cut
    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
    wr = imageio_ffmpeg.write_frames(a.out, (W, H), fps=a.fps, codec="libx264", quality=None, macro_block_size=2,
                                     ffmpeg_log_level="error", audio_path=wav, audio_codec="aac",
                                     output_params=["-preset", "veryfast", "-crf", "19", "-movflags", "+faststart",
                                                    "-b:a", "192k", "-shortest"])
    wr.send(None)
    for k in range(n):
        t = k / a.fps
        img = bg.copy()
        fr = Image.open(os.path.join(frames_dir, f"f{k:05d}.png")).convert("RGBA")
        img.paste(fr, (0, 0), fr)
        cam = PerspCam(tr.get("cam_f", t), tr.get("cam_z", t), W, H)
        draw_bubble(img, int(round(tr.get("bubble_kind", t))), tr.get("bubble", t), t, tr, W, H)
        for p in pops:
            if p["t0"] - 0.01 <= t <= p["t1"] + 0.35:
                draw_pop(img, cam, p, t, W, H)
        for kk in keys:
            if kk[0] <= t <= kk[1] + (0.12 if kk[4] else 0.3):
                draw_key(img, kk, t, W, H)
        wr.send(img.convert("RGB").tobytes())
    wr.close()
    print("OK", a.out, f"{t_end:.1f}s")


if __name__ == "__main__":
    raise SystemExit(main())
