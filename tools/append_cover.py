#!/usr/bin/env python3
"""Append the cover (publishing/<slug>/cover.png) as the last 0.5 s of an already rendered MP4 - the frame the owner
picks as thumbnail in YouTube / Instagram. No re-render.

    python tools/append_cover.py chatbot [traffic_light ...]  [--dur 0.5]
Writes output/explainers/<slug>_cover.mp4 next to the original (the original is kept).
"""
import os
import subprocess
import sys

import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def append(slug, dur=0.5):
    src = os.path.join(ROOT, "output", "explainers", f"{slug}.mp4")
    cover = os.path.join(ROOT, "publishing", slug, "cover.png")
    out = os.path.join(ROOT, "output", "explainers", f"{slug}_cover.mp4")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-i", src, "-loop", "1", "-t", str(dur), "-i", cover,
           "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-filter_complex",
           "[0:v]fps=30,format=yuv420p,setsar=1[a];[1:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[c];"
           "[0:a]aresample=44100,aformat=channel_layouts=stereo[x];[2:a]aformat=channel_layouts=stereo[y];"
           "[a][x][c][y]concat=n=2:v=1:a=1[v][au]",
           "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    d = float(a[a.index("--dur") + 1]) if "--dur" in a else 0.5
    for s in [x for x in a if not x.startswith("--") and x != str(d)]:
        print(append(s, d))
