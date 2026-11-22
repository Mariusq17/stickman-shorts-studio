#!/usr/bin/env python3
"""Opening/ending rotation check: never the same opening code (O1-O7) or ending code (E1-E5) twice in a row
in posting order. Reads publishing/STATS.md: table A (posted, in order) then table C (queue, in order).

    python tools/rotation.py              # uses the current codes of the queue
    python tools/rotation.py --proposed   # uses the "Proposed opening/ending" columns of the queue
Exit code 1 when a repeat is found (usable in tests / scripts).
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = os.path.join(ROOT, "publishing", "STATS.md")
OPENINGS = [f"O{i}" for i in range(1, 8)]
ENDINGS = ["E1", "E2", "E3", "E5"]          # E4 retired: the loop is a "+L" tail on every ending


def _table(md: str, heading_prefix: str):
    """Rows (list of dicts) of the first markdown table under the heading that starts with heading_prefix."""
    lines = md.splitlines()
    rows, header, inside = [], None, False
    for line in lines:
        if line.startswith("## "):
            inside = line[3:].startswith(heading_prefix)
            header = None
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif not all(re.fullmatch(r":?-+:?", c) for c in cells):
            rows.append(dict(zip(header, cells)))
    return rows


def sequence(md: str, proposed: bool = False):
    seq = []
    for r in _table(md, "A."):
        seq.append((r.get("Slug", "?"), "posted", r.get("Opening", "?"), r.get("Ending", "?")))
    for r in _table(md, "C."):
        o = r.get("Proposed opening") if proposed and r.get("Proposed opening") else r.get("Opening", "?")
        e = r.get("Proposed ending") if proposed and r.get("Proposed ending") else r.get("Ending", "?")
        seq.append((r.get("Slug", "?"), "queue", o, e))
    return seq


def repeats(seq):
    bad = []
    for (s0, k0, o0, e0), (s1, k1, o1, e1) in zip(seq, seq[1:]):
        if k0 == k1 == "posted":           # already published: history, not something we can still fix
            continue
        e0, e1 = e0.split("+")[0], e1.split("+")[0]   # "+L" (loop tail) is not part of the ending code
        if o0 == o1:
            bad.append(f"opening {o1} twice in a row: {s0} -> {s1}")
        if e0 == e1:
            bad.append(f"ending {e1} twice in a row: {s0} -> {s1}")
    return bad


def allowed_next(seq):
    last_o, last_e = (seq[-1][2], seq[-1][3].split("+")[0]) if seq else (None, None)
    return [o for o in OPENINGS if o != last_o], [e for e in ENDINGS if e != last_e]


def main(argv):
    md = open(STATS, encoding="utf-8").read()
    seq = sequence(md, "--proposed" in argv)
    for slug, kind, o, e in seq:
        print(f"  {kind:6s} {slug:16s} {o:3s} {e}")
    bad = repeats(seq)
    for b in bad:
        print("  REPEAT:", b)
    o, e = allowed_next(seq)
    print(f"\n  next video may open with {', '.join(o)} and end with {', '.join(e)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
