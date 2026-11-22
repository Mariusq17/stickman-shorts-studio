#!/usr/bin/env python3
"""Collect PUBLIC Shorts listings of niche channels for tools/yt/swipe.py (no login, no cookies).

    python tools/collect_niche.py                     # channels from tools/niche_channels.txt -> output/niche.json
    python tools/collect_niche.py @SomeChannel --n 40
    python3 -I tools/yt/swipe.py output/niche.json --min 2

Uses `yt-dlp --flat-playlist -J` on https://www.youtube.com/<handle>/shorts (pip install yt-dlp).
Needs network access to www.youtube.com (blocked in some cloud containers: run it on the laptop then).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def channels(argv):
    hs = [a for a in argv if a.startswith("@")]
    if hs:
        return hs
    path = os.path.join(HERE, "niche_channels.txt")
    return [l.split("#")[0].strip() for l in open(path, encoding="utf-8") if l.split("#")[0].strip()]


def collect(handle, n):
    url = f"https://www.youtube.com/{handle}/shorts"
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", str(n), url],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"  ! {handle}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'failed'}", file=sys.stderr)
        return []
    data = json.loads(r.stdout)
    name = data.get("channel") or data.get("uploader") or handle
    out = []
    for e in data.get("entries") or []:
        if e.get("view_count") is None:
            continue
        out.append({"channel": name, "title": e.get("title", ""), "views": e["view_count"],
                    "url": e.get("url") or f"https://www.youtube.com/shorts/{e.get('id')}",
                    "duration": e.get("duration")})
    print(f"  {handle}: {len(out)} shorts", file=sys.stderr)
    return out


def main():
    a = sys.argv[1:]
    n = int(a[a.index("--n") + 1]) if "--n" in a else 40
    out_path = a[a.index("--out") + 1] if "--out" in a else os.path.join("output", "niche.json")
    rows = []
    for h in channels(a):
        rows += collect(h, n)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    json.dump(rows, open(out_path, "w"), indent=1)
    print(f"{len(rows)} videos -> {out_path}")


if __name__ == "__main__":
    main()
