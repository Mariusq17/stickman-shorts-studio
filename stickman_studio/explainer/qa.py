"""Scene QA for explainer videos - checks the scene-hygiene rules WITHOUT rendering a single pixel.

    python -m stickman_studio.explainer.qa <slug>                    # report, exit code 1 on ERROR
    python -m stickman_studio.explainer.qa <slug> --rev cc47131      # check an OLD version (video file at that commit)
    python -m stickman_studio.explainer.qa <slug> --srt out.srt      # step-level narration timing (for retention.py)
    python -m stickman_studio.explainer.qa --all                     # every video
    options: --timing auto|est|piper   --dt 0.25   --json

How: the narration timing is planned exactly like the renderer does (builder.plan_timeline), with Piper word
times when the voice is installed, otherwise an estimate calibrated on our 9 videos (+-4 s per video). The
scene's own draw() code runs on a *recording camera*: boxes, lines and labels are recorded in world space
instead of being painted. On that record we check:

  linger      an object from QA["objects"] is on screen during a step it does not belong to
  pass-through two objects overlap while one of them moves (cars through cars...)
  link        a cable/pipe (lines thicker than width_min) does not connect its two end objects
  label       a callout label (kit.label) is cut by the frame edge; text on an object shrunk to unreadable
  keyword     keyword on screen < 0.9 s, phrase spoken twice in the step, keyword too long (> 2 lines)
  static      > 2 s of narration with nothing moving (no track change, camera move or pop-up entering)
  info        DNA numbers for STATS.md: length, hook length, fixes, wind-down after the last fix

The per-video spec lives in the video module as QA = dict(...) (and VIDEO["qa"]):

    QA = dict(
        objects={"red car": dict(color=(226, 70, 70), steps="0-4,6-7,16-17")},  # boxes drawn in that colour
        links=[dict(name="cable", steps="10-15", width_min=0.03,
                    ends=[dict(color=(90, 110, 150), near=(-4.2, 1.35, 0.5)), dict(color=..., near=...)])],
        static_ok="13",          # steps where a still frame is intended (optional)
    )
Objects: color (or colors=[...]) = fill colour of the object's cam.box calls; optional near=(x,y,z) +
radius to pick one of several boxes of that colour; solid=False to skip pass-through checks; grace (s) for
the exit animation after its last step (default 2.5).
Links: lines thicker than width_min (optionally only `colors`) must chain from end 1 to end 2; `bridges` =
boxes where the cable is legitimately out of sight (buried trench, going into a cliff); `settle` = seconds
after the step start before checking (build animations); `when` = [(track, op, value), ...] all true
(e.g. ("broken", "<", 0.5) skips the moment the cable is broken on purpose).
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import types

from PIL import Image

from ..painter import font
from ..tts import _pause_after, _syllables, estimate_word_times, tokenize
from . import builder
from .iso import IsoCam
from .lib import kit

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SYL_S, PAUSE_K = 0.152, 1.0          # estimate calibrated on the 9 rendered videos (voice 1.2x)
STATIC_S = 2.0
KEY_MIN_READ = 0.9
SMALL_TEXT_PX = 0.018                # x width: text on objects smaller than ~19 px at 1080 is unreadable


# ------------------------------------------------------------------ timing
class EstClip:
    """Narration clip estimate (no audio): duration + word times from syllables and punctuation."""

    def __init__(self, text, rate=1.2):
        self.words = tokenize(text) or ["..."]
        k = 1.2 / max(0.5, rate)
        dur = (sum(_syllables(w) for w in self.words) * SYL_S + sum(_pause_after(w) for w in self.words[:-1]) * PAUSE_K) * k
        self.duration = dur
        self.word_times = estimate_word_times(self.words, dur)
        self.engine = "estimate"


def narration_clips(steps, timing="auto", rate=1.2):
    texts = [s["text"] for s in steps]
    if timing in ("auto", "piper"):
        try:
            from ..tts import PiperEngine, piper_ready
            if piper_ready("en", None):
                eng = PiperEngine("en", None, rate)
                return [eng.synth(t, i) for i, t in enumerate(texts)], "piper"
        except Exception:                       # noqa: BLE001 - fall back to the estimate
            pass
        if timing == "piper":
            raise RuntimeError("Piper voice not available (python -m stickman_studio.voices --download en)")
    return [EstClip(t, rate) for t in texts], "estimate"


# ------------------------------------------------------------------ recording camera
class RecCam(IsoCam):
    """IsoCam that records primitives in world space instead of painting them."""

    def __init__(self, img, focus, zoom, anchor):
        super().__init__(img, focus, zoom, anchor)
        self.rec = []

    def poly(self, pts3, fill=None, outline=None, width=0.0):
        self.rec.append(("poly", pts3, fill))

    def line(self, pts3, color, width, caps=True):
        self.rec.append(("line", [tuple(p) for p in pts3], color, width))

    def box(self, x, y, z, w, d, h, color, outline=True, faces="tlr", top_color=None):
        self.rec.append(("box", (x, y, z, x + w, y + d, z + h), tuple(color)))

    def text(self, xyz, s, size, fill, stroke=0.0, stroke_fill=(255, 255, 255), anchor="mm"):
        self.rec.append(("text", xyz, s, size))


_SMALL = []


def _plane_text_probe(cam, plane, c, u, v, text, size, color, max_w=None, max_h=None):
    """Replacement for kit.plane_text during QA: computes the final on-screen cap height, paints nothing."""
    if not text or size <= 0:
        return
    fs = max(8, int(size * cam.s * 1.35))
    bbox = font(fs).getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if tw <= 0 or th <= 0:
        return
    s = size / max(1, th)
    if max_w is not None and tw * s > max_w:
        s = max_w / tw
    if max_h is not None and th * s > max_h:
        s = max_h / th
    _SMALL.append((text, th * s * cam.s))


# ------------------------------------------------------------------ helpers
def parse_steps(spec, n):
    if spec is None:
        return set(range(n))
    if isinstance(spec, (list, tuple, set)):
        return set(spec)
    out = set()
    for part in str(spec).replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            out |= set(range(int(a), (int(b) if b else n - 1) + 1))
        else:
            out.add(int(part))
    return out


def _aabb_union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), min(b[2] for b in boxes),
            max(b[3] for b in boxes), max(b[4] for b in boxes), max(b[5] for b in boxes))


def _center(b):
    return ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)


def _overlap(a, b, m=0.04):
    return all(min(a[i + 3], b[i + 3]) - max(a[i], b[i]) > m for i in range(3))


def _pt_box_dist(p, b):
    d = [max(b[i] - p[i], 0.0, p[i] - b[i + 3]) for i in range(3)]
    return math.sqrt(sum(x * x for x in d))


def _pt_seg_dist(p, a, b):
    ab = [b[i] - a[i] for i in range(3)]
    ap = [p[i] - a[i] for i in range(3)]
    L = sum(x * x for x in ab)
    k = 0.0 if L <= 1e-12 else max(0.0, min(1.0, sum(ab[i] * ap[i] for i in range(3)) / L))
    q = [a[i] + ab[i] * k for i in range(3)]
    return math.sqrt(sum((p[i] - q[i]) ** 2 for i in range(3)))


def _screen_box(cam, b):
    pts = [cam.p(x, y, z) for x in (b[0], b[3]) for y in (b[1], b[4]) for z in (b[2], b[5])]
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def _on_screen(sb, W, H, frac=0.15):
    """At least `frac` of the object's screen box is inside the frame."""
    x0, y0, x1, y1 = sb
    area = max(1e-6, (x1 - x0) * (y1 - y0))
    ix = max(0.0, min(x1, W) - max(x0, 0)) * max(0.0, min(y1, H) - max(y0, 0))
    return ix / area >= frac


def _find_obj(rec, spec):
    cols = [tuple(c) for c in (spec.get("colors") or [spec["color"]])]
    boxes = [r[1] for r in rec if r[0] == "box" and r[2] in cols]
    if spec.get("near") is not None:
        rad = spec.get("radius", 0.8)
        boxes = [b for b in boxes if _pt_box_dist(spec["near"], b) <= rad]
    return _aabb_union(boxes) if boxes else None


def _cond(x, op, v):
    return {"<": x < v, ">": x > v, "<=": x <= v, ">=": x >= v}[op]


def _connected(lines, end_a, end_b, tol=0.08, bridges=()):
    """Is there a chain of lines from box end_a to box end_b? Lines touch when an endpoint of one lies
    within tol of the other's polyline. `bridges` are boxes the cable may pass through out of sight
    (buried in a trench, into a cliff): every line touching the same bridge counts as connected."""
    lines = [l for l in lines if len(l) >= 2]
    n = len(lines)
    if n == 0:
        return False
    segs = [list(zip(l[:-1], l[1:])) for l in lines]
    ends = [(l[0], l[-1]) for l in lines]

    def touch(i, j):
        for p in ends[i]:
            if any(_pt_seg_dist(p, a, b) <= tol for a, b in segs[j]):
                return True
        for p in ends[j]:
            if any(_pt_seg_dist(p, a, b) <= tol for a, b in segs[i]):
                return True
        return False

    def at_box(i, box):
        return any(_pt_box_dist(p, box) <= tol for p in lines[i])

    via = [{i for i in range(n) if at_box(i, b)} for b in bridges]

    start = [i for i in range(n) if at_box(i, end_a)]
    goal = {i for i in range(n) if at_box(i, end_b)}
    if not start or not goal:
        return False
    seen, stack = set(start), list(start)
    # spatial pre-filter: only compare lines whose bounding boxes are close
    bb = [_aabb_union([(p[0], p[1], p[2], p[0], p[1], p[2]) for p in l]) for l in lines]
    while stack:
        i = stack.pop()
        if i in goal:
            return True
        for group in via:
            if i in group:
                for j in group - seen:
                    seen.add(j)
                    stack.append(j)
        for j in range(n):
            if j in seen or not _overlap(bb[i], bb[j], -tol):
                continue
            if touch(i, j):
                seen.add(j)
                stack.append(j)
    return False


# ------------------------------------------------------------------ loading
def load_video(slug, rev=None):
    """VIDEO dict of the current video, or of the video file as it was at git revision `rev` (engine stays
    current - the scene-hygiene bugs live in the video files)."""
    from .videos import load, module_file
    if rev is None:
        return load(slug)
    path = os.path.relpath(module_file(slug), ROOT).replace(os.sep, "/")
    src = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    pkg = "stickman_studio.explainer.videos" if "/videos/" in path else "stickman_studio.explainer"
    name = f"{pkg}._qa_{slug}_{re.sub(r'[^0-9a-zA-Z]', '_', rev)}"
    mod = types.ModuleType(name)
    mod.__package__ = pkg
    mod.__file__ = os.path.join(ROOT, path)
    sys.modules[name] = mod
    exec(compile(src, f"{rev}:{path}", "exec"), mod.__dict__)
    return mod.VIDEO


def shift_spec(spec, n):
    """Same QA spec with every step index moved by n (e.g. +1 after open_loop() inserted a hook step)."""
    def mv(x):
        if x is None or x == "":
            return x
        out = []
        for part in str(x).replace(" ", "").split(","):
            if "-" in part:
                a, b = part.split("-")
                out.append(f"{int(a) + n}-{int(b) + n}" if b else f"{int(a) + n}-")
            else:
                out.append(str(int(part) + n))
        return ",".join(out)
    spec = dict(spec)
    spec["objects"] = {k: dict(o, steps=mv(o.get("steps"))) for k, o in spec.get("objects", {}).items()}
    spec["links"] = [dict(L, steps=mv(L.get("steps"))) for L in spec.get("links", [])]
    if spec.get("static_ok"):
        spec["static_ok"] = mv(spec["static_ok"])
    return spec


def spec_of(slug):
    from .videos import load
    v = load(slug)
    return v.get("qa") or {}


# ------------------------------------------------------------------ the checks
def run_qa(video, spec=None, timing="auto", dt=0.25, size=(1080, 1920), log=None):
    steps = video["steps"]
    spec = spec if spec is not None else (video.get("qa") or {})
    n = len(steps)
    clips, engine = narration_clips(steps, timing, video.get("voice_rate") or 1.2)
    P = builder.plan_timeline(steps, clips, video["initial"], size)
    W, H = P["W"], P["H"]
    tr, starts, durs, camp = P["tracks"], P["starts"], P["durs"], P["camp"]
    total = P["content_total"]
    issues = []

    def add(level, kind, msg, t=None, step=None):
        issues.append(dict(level=level, kind=kind, msg=msg, t=None if t is None else round(t, 2), step=step))

    # ---------------- keywords (synced to the spoken word by construction; check readability/ambiguity)
    for i, st in enumerate(steps):
        toks = [builder._norm(w) for w in tokenize(st["text"])]
        for phrase, _c in st.get("keys", []):
            spoken = phrase.split("|", 1)[0]
            ph = [builder._norm(w) for w in spoken.split()]
            hits = sum(1 for k in range(len(toks) - len(ph) + 1)
                       if all(toks[k + j].startswith(ph[j]) for j in range(len(ph))))
            if hits > 1:
                add("WARN", "keyword", f"step {i}: keyword '{spoken}' is spoken {hits}x - it pops on the FIRST one", step=i)
    f = font(int(W * 0.080))
    for k in P["keys"]:
        t0, t1, text = k[0], k[1], k[2]
        if t1 - t0 < KEY_MIN_READ:
            add("WARN", "keyword", f"keyword '{text}' readable only {t1 - t0:.2f} s (next one replaces it)", t0,
                tr.step_at(t0))
        words, lines, cur = text.split(), 1, ""
        for wd in words:
            c = (cur + " " + wd).strip()
            if f.getlength(c) > W * 0.84 and cur:
                lines += 1
                cur = wd
            else:
                cur = c
        if lines > 2 or f.getlength(max(words, key=len) if words else "") > W * 0.92:
            add("WARN", "keyword", f"keyword '{text}' too long ({lines} lines) - keep 1-3 short words", t0, tr.step_at(t0))

    # ---------------- static screen while talking (tracks, camera, pop-ups entering, fixes)
    static_ok = parse_steps(spec.get("static_ok", ""), n) if spec.get("static_ok") else set()
    names = [k for k in tr.keys if k not in ("cam_f", "cam_z")]
    pop_t = [(p["t0"], p["t1"] if p.get("kind") in ("card", "graph") else p["t0"] + max(0.5, float(p.get("anim", 0.6))))
             for p in P["pops"]]
    fix_t = [(x - 0.2, x + 0.6) for x in P["fixes"]]
    step_dt = 0.1
    t, prev, run0 = 0.0, None, None
    runs = []

    def moving(t):
        f0, z0 = camp.at(max(0.0, t - step_dt))
        f1, z1 = camp.at(t)
        if math.dist(f0, f1) * z1 > 1.5 or abs(z1 - z0) / max(1.0, z1) > 0.003:
            return True
        if any(a <= t <= b for a, b in pop_t) or any(a <= t <= b for a, b in fix_t):
            return True
        ts_ = builder.scene_time(P, t)[0]             # teaser steps show a later moment
        for nm in names:
            a, b = tr.get(nm, max(0.0, ts_ - step_dt)), tr.get(nm, ts_)
            if isinstance(a, tuple):
                if math.dist(a, b) > 1e-3:
                    return True
            elif abs(a - b) > 1e-3:
                return True
        return False

    while t < total:
        i = tr.step_at(t)
        s0 = starts[i] + builder.LEAD
        speaking = s0 <= t <= s0 + clips[i].duration
        still = speaking and i not in static_ok and not moving(t)
        if still and run0 is None:
            run0 = t
        if not still and run0 is not None:
            runs.append((run0, t))
            run0 = None
        t += step_dt
    if run0 is not None:
        runs.append((run0, total))
    merged = []
    for a, b in runs:                       # a blink of motion (< 0.3 s) does not break a static stretch
        if merged and a - merged[-1][1] < 0.3:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    for a, b in merged:
        if b - a > STATIC_S:
            i = tr.step_at(a)
            add("WARN", "static", f"{b - a:.1f} s with nothing moving while speaking (step {i}: "
                                  f"'{steps[i]['text'][:50]}...') - add a build/pop-up/camera beat", a, i)

    # ---------------- scene record: objects, pass-through, links, labels, text on objects
    objects = spec.get("objects", {})
    links = spec.get("links", [])
    scene = video["scene"](W, H)
    small = Image.new("RGB", (96, 160))
    orig_plane_text = kit.plane_text
    kit.plane_text = _plane_text_probe
    lingering, prev_pos, hits, link_bad, cut_labels, tiny, checked = {}, {}, {}, {}, {}, {}, {}
    seen_objects = set()
    try:
        t = 0.0
        while t < total:
            i = tr.step_at(t)
            f, z = camp.at(t)
            cam = RecCam(small.copy(), f, z, (W / 2, H * 0.56))
            del _SMALL[:]
            ts, si, st_ = builder.scene_time(P, t)
            scene.draw(cam.img, cam, P["scene_tracks"], ts, si, st_)
            i = tr.step_at(ts)         # teaser steps show a later step: judge the scene by the step it shows
            # objects
            pos = {}
            for name, o in objects.items():
                b = _find_obj(cam.rec, o)
                if b is None:
                    continue
                pos[name] = b
                seen_objects.add(name)
                if not _on_screen(_screen_box(cam, b), W, H):
                    continue
                own = parse_steps(o.get("steps"), n)
                if i in own:
                    continue
                last_own = max([s for s in own if s < i], default=None)
                next_own = min([s for s in own if s > i], default=None)
                if last_own is not None and ts - (starts[last_own] + durs[last_own]) <= o.get("grace", 2.5):
                    continue                                  # exit animation
                if next_own is not None and starts[next_own] - ts <= o.get("enter", 1.0):
                    continue                                  # entering for its next step
                lingering.setdefault(name, []).append((t, i))
            # pass-through: overlap while at least one of the two moves
            solid = [nm for nm in pos if objects[nm].get("solid", True)]
            for a_i, a in enumerate(solid):
                for b in solid[a_i + 1:]:
                    if not _overlap(pos[a], pos[b]):
                        continue
                    mv = any(nm in prev_pos and math.dist(_center(prev_pos[nm]), _center(pos[nm])) > 0.01 for nm in (a, b))
                    if mv:
                        hits.setdefault((a, b), []).append((t, i))
            prev_pos = pos
            # links (cables / pipes)
            for L in links:
                if i not in parse_steps(L.get("steps"), n):
                    continue
                if ts - starts[i] < L.get("settle", 1.2):       # let the build animation finish
                    continue
                if not all(_cond(tr.get(k, ts), op, v) for k, op, v in L.get("when", ())):
                    continue
                wmin = L.get("width_min", 0.03)
                cols = [tuple(c) for c in L["colors"]] if L.get("colors") else None
                lines = [r[1] for r in cam.rec if r[0] == "line" and r[3] >= wmin and (cols is None or tuple(r[2]) in cols)]
                ends = [_find_obj(cam.rec, e) for e in L["ends"]]
                checked[L["name"]] = checked.get(L["name"], 0) + 1
                if any(e is None for e in ends):
                    missing = [k for k, e in enumerate(ends) if e is None]
                    link_bad.setdefault(L["name"], []).append((t, i, f"end object #{missing[0] + 1} not in the scene"))
                elif not _connected(lines, ends[0], ends[1], L.get("tol", 0.08), L.get("bridges", ())):
                    link_bad.setdefault(L["name"], []).append((t, i, "does not reach both ends"))
            # callout labels cut by the frame
            for xyz, text, lsize, *_ in getattr(cam, "_labels", []):
                x, y = cam.p(*xyz)
                hpx = lsize * cam.s
                tw = font(max(6, int(hpx))).getlength(text)
                p = hpx * 0.35
                bx = (x - tw / 2 - p * 1.4, y - hpx / 2 - p, x + tw / 2 + p * 1.4, y + hpx / 2 + p)
                inside = bx[0] >= 0 and bx[1] >= 0 and bx[2] <= W and bx[3] <= H
                visible = bx[2] > 0 and bx[0] < W and bx[3] > 0 and bx[1] < H
                settled = camp.speed_at(t) < 0.004          # labels sliding out during a camera move are fine
                if visible and not inside and settled:
                    cut_labels.setdefault(text, []).append((t, i))
            for text, px in _SMALL:
                tiny.setdefault(text, []).append((t, i, px))
            t += dt
    finally:
        kit.plane_text = orig_plane_text
        del _SMALL[:]

    def spans(samples):
        out, cur = [], None
        for s in samples:
            t_, i_ = s[0], s[1]
            if cur and t_ - cur[1] <= dt * 1.5 and cur[2] == i_:
                cur[1] = t_
            else:
                if cur:
                    out.append(cur)
                cur = [t_, t_, i_]
        if cur:
            out.append(cur)
        return out

    for name, sm in lingering.items():
        for a, b, i in spans(sm):
            if b - a + dt >= 0.5:
                add("ERROR", "linger", f"'{name}' still on screen in step {i} ({a:.1f}-{b + dt:.1f} s) - not part of "
                                       f"its steps {objects[name].get('steps')}; make it exit", a, i)
    for (a_, b_), sm in hits.items():
        for a, b, i in spans(sm):
            add("ERROR", "pass-through", f"'{a_}' and '{b_}' overlap while moving (step {i}, {a:.1f}-{b + dt:.1f} s) - "
                                         f"clear the lane first", a, i)
    for name, sm in link_bad.items():
        reasons = {}
        for t_, i_, why in sm:
            reasons.setdefault((i_, why), []).append(t_)
        for (i_, why), ts in sorted(reasons.items()):
            add("ERROR", "link", f"'{name}' {why} in step {i_} ({min(ts):.1f}-{max(ts) + dt:.1f} s)", min(ts), i_)
    for text, sm in cut_labels.items():
        for a, b, i in spans(sm):
            if b - a + dt < 1.0:
                continue
            add("WARN", "label", f"label '{text}' cut by the frame edge in step {i} ({a:.1f}-{b + dt:.1f} s)", a, i)
    for text, sm in tiny.items():               # only text that is NEVER readable (even in close-ups)
        px = max(s[2] for s in sm)
        if px < SMALL_TEXT_PX * W:
            add("WARN", "label", f"text on object '{text}' is at most {px:.0f} px tall on screen (shrunk by max_w/max_h "
                                 f"or never shown close) - unreadable", sm[0][0], sm[0][1])

    # ---------------- DNA / strategy info
    fixes = sorted(P["fixes"])
    last_fix_step = max([i for i, s in enumerate(steps) if s.get("fix")], default=None)
    tail = total - (starts[last_fix_step] + durs[last_fix_step]) if last_fix_step is not None else None
    info = dict(slug=video.get("slug"), timing=engine, length_s=round(total, 1), steps=n, fixes=len(fixes),
                hook_s=round(durs[0], 1), first_fix_s=round(fixes[0], 1) if fixes else None,
                winddown_s=round(tail, 1) if tail is not None else None,
                winddown_pct=round(100 * tail / total) if tail is not None else None,
                words=sum(len(tokenize(s["text"])) for s in steps), link_samples=checked,
                objects_seen=sorted(seen_objects))
    if not objects and not links:
        add("INFO", "spec", "no QA spec (QA = dict(objects=..., links=...)) - linger/pass-through/link checks skipped")
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    issues.sort(key=lambda x: (order[x["level"]], x["t"] if x["t"] is not None else -1))
    return dict(info=info, issues=issues, starts=starts, durs=durs, clips=clips)


def to_srt(video, result):
    def ts(x):
        h, r = divmod(max(0.0, x), 3600)
        m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    out = []
    for i, (st, a, d) in enumerate(zip(video["steps"], result["starts"], result["durs"])):
        out.append(f"{i + 1}\n{ts(a)} --> {ts(a + d)}\n[step {i}] {st['text']}\n")
    return "\n".join(out)


def report(result, slug):
    info = result["info"]
    print(f"\n== QA {slug}  ({info['timing']} timing)  length {info['length_s']} s, {info['steps']} steps, "
          f"{info['fixes']} fixes, hook {info['hook_s']} s, wind-down after last fix {info['winddown_s']} s "
          f"({info['winddown_pct']}%)")
    if not result["issues"]:
        print("   all checks passed")
    for it in result["issues"]:
        print(f"   {it['level']:5s} {it['kind']:12s} {it['msg']}")
    n_err = sum(1 for it in result["issues"] if it["level"] == "ERROR")
    print(f"   -> {n_err} error(s), {sum(1 for it in result['issues'] if it['level'] == 'WARN')} warning(s)")
    return n_err


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d  # noqa: E731
    timing, rev, srt = opt("--timing", "auto"), opt("--rev"), opt("--srt")
    dt = float(opt("--dt", 0.25))
    vals = {opt(k) for k in ("--timing", "--rev", "--srt", "--dt")}
    slugs = [x for x in a if not x.startswith("--") and x not in vals]
    if "--all" in a:
        from .videos import modules
        slugs = sorted(modules())
    if not slugs:
        print(__doc__)
        return 2
    errors, out = 0, {}
    for slug in slugs:
        video = load_video(slug, rev)
        spec = spec_of(slug) if rev else None          # old versions are judged with today's spec
        res = run_qa(video, spec, timing=timing, dt=dt)
        if srt:
            os.makedirs(os.path.dirname(os.path.abspath(srt)), exist_ok=True)
            open(srt, "w", encoding="utf-8").write(to_srt(video, res))
        if "--json" in a:
            out[slug] = dict(info=res["info"], issues=res["issues"])
        else:
            errors += report(res, slug + (f" @ {rev}" if rev else ""))
    if "--json" in a:
        print(json.dumps(out, indent=1))
        errors = sum(1 for v in out.values() for it in v["issues"] if it["level"] == "ERROR")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
