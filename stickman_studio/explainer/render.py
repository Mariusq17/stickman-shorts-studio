"""Render explainer videos - single, preview, or a resumable batch.

  python -m stickman_studio.explainer.render --list
  python -m stickman_studio.explainer.render elevator --preview 1,5,20,60      # contact sheet PNG
  python -m stickman_studio.explainer.render elevator                          # full MP4
  python -m stickman_studio.explainer.render --batch elevator vending solar --jobs 2

Batch mode keeps output/explainers/status.json; a video is skipped when its MP4 exists and its
source (video module + engine) has not changed since it was rendered - so an interrupted batch
simply continues where it stopped."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUTDIR = os.path.join(ROOT, "output", "explainers")
STATUS = os.path.join(OUTDIR, "status.json")


def _src_hash(slug):
    from .videos import module_file
    h = hashlib.sha1()
    files = [module_file(slug)]
    for base in (HERE, os.path.join(HERE, "lib")):
        files += [os.path.join(base, f) for f in sorted(os.listdir(base)) if f.endswith(".py")]
    for f in files:
        with open(f, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:16]


def _load_status():
    try:
        with open(STATUS) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_status(st):
    os.makedirs(OUTDIR, exist_ok=True)
    tmp = STATUS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=2)
    os.replace(tmp, STATUS)


def render_one(slug, out=None, ss=2, log=print):
    from .builder import build_explainer
    from .videos import load
    v = load(slug)
    out = out or os.path.join(OUTDIR, f"{slug}.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    kw = {}
    if v.get("dynamic"):
        kw["dynamic"] = kw["layout"] = True
    if v.get("voice_rate"):
        kw["voice_rate"] = v["voice_rate"]
    cover = os.path.join(ROOT, "publishing", slug, "cover.png")
    if os.path.exists(cover):          # last 0.5 s = cover (YouTube Shorts thumbnail frame picker)
        kw["end_cover"] = cover
    path, total, engine = build_explainer(v["steps"], v["scene"], out, v["initial"], v.get("overlays"), ss=ss,
                                          tracker=v.get("tracker"), log=log, **kw)
    return path, total, engine


def preview(slug, times, out_png, ss=1):
    from .builder import build_explainer
    from .videos import load
    from ..painter import font
    v = load(slug)
    frames, starts, durs, keys = build_explainer(v["steps"], v["scene"], None, v["initial"], v.get("overlays"), ss=ss,
                                                 preview_times=times, tracker=v.get("tracker"), log=lambda m: None,
                                                 dynamic=bool(v.get("dynamic")), layout=bool(v.get("dynamic")))
    w, h = frames[0].size
    sc = 0.3
    tw, th = int(w * sc), int(h * sc)
    cols = min(6, len(frames))
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), "white")
    d = ImageDraw.Draw(sheet)
    for k, (im, t) in enumerate(zip(frames, times)):
        x, y = (k % cols) * tw, (k // cols) * th
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 8, y + th - 30), f"{t:.1f}s", font=font(22), fill=(200, 0, 0))
    sheet.save(out_png)
    print("steps:", len(durs), "total:", round(sum(durs), 1), "s")
    print("step starts:", [round(s, 1) for s in starts])
    return out_png


def batch(slugs, jobs=2, ss=2):
    st = _load_status()
    todo = []
    for s in slugs:
        h = _src_hash(s)
        rec = st.get(s, {})
        if rec.get("state") == "done" and rec.get("hash") == h and os.path.exists(rec.get("path", "")):
            print(f"[skip] {s} already rendered -> {rec['path']}")
            continue
        todo.append((s, h))
    running = []
    while todo or running:
        while todo and len(running) < jobs:
            s, h = todo.pop(0)
            log = open(os.path.join(OUTDIR, f"{s}.log"), "w") if os.makedirs(OUTDIR, exist_ok=True) is None else None
            p = subprocess.Popen([sys.executable, "-m", "stickman_studio.explainer.render", s, "--ss", str(ss)],
                                 cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            st[s] = dict(state="rendering", hash=h, started=time.strftime("%Y-%m-%d %H:%M:%S"))
            _save_status(st)
            running.append((s, h, p, time.time()))
            print(f"[start] {s}")
        time.sleep(5)
        for item in list(running):
            s, h, p, t0 = item
            if p.poll() is None:
                continue
            running.remove(item)
            path = os.path.join(OUTDIR, f"{s}.mp4")
            ok = p.returncode == 0 and os.path.exists(path)
            st[s] = dict(state="done" if ok else "failed", hash=h, path=path if ok else "",
                         seconds=round(time.time() - t0), finished=time.strftime("%Y-%m-%d %H:%M:%S"))
            _save_status(st)
            print(f"[{'done' if ok else 'FAILED'}] {s} ({round(time.time() - t0)} s) -> {path if ok else 'see ' + s + '.log'}")
    return st


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--preview", default=None, help="comma separated times (s) -> contact sheet PNG")
    ap.add_argument("--batch", nargs="+", default=None)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args(argv)
    if a.list:
        from .videos import load, modules
        for s in sorted(modules()):
            print(f"{s:20s} {load(s).get('title', '')}")
        return 0
    if a.batch:
        st = batch(a.batch, a.jobs, a.ss)
        return 0 if all(st.get(s, {}).get("state") in ("done",) for s in a.batch) else 1
    if not a.slug:
        ap.error("give a video slug, --batch or --list")
    if a.preview:
        times = [float(x) for x in a.preview.split(",")]
        print(preview(a.slug, times, a.out or os.path.join(OUTDIR, f"{a.slug}_preview.png")))
        return 0
    render_one(a.slug, a.out, a.ss)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
