"""Dynamic retention-style subtitles: big bold words, 1-3 word chunks, active
word highlighted with a pop, placed inside the platform safe zone."""
from __future__ import annotations

import re

from .easing import clamp, ease_out_back
from .painter import font


def chunk_words(words: list, timings: list, max_words: int = 3, max_chars: int = 16):
    """Group words into short chunks. Returns list of (start, end, [idx...])."""
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        text_len = sum(len(words[j]) + 1 for j in cur)
        end_sentence = bool(re.search(r"[.!?…:]$", w))
        comma = w.endswith(",")
        if len(cur) >= max_words or text_len >= max_chars or end_sentence or comma:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for c in chunks:
        out.append((timings[c[0]][0], timings[c[-1]][1], c))
    # extend each chunk until the next one starts (no flicker)
    res = []
    for k, (s, e, c) in enumerate(out):
        nxt = out[k + 1][0] if k + 1 < len(out) else e + 0.35
        res.append((s, max(e, nxt), c))
    return res


class SubtitleRenderer:
    def __init__(self, W: int, H: int, fmt: str, theme):
        self.W, self.H, self.theme = W, H, theme
        if fmt == "vertical":
            self.cy = int(H * 0.745)      # above TikTok/Reels bottom UI, under the stage
            self.max_w = int(W * 0.80)    # keep away from right-side action buttons
            self.cx = int(W * 0.47)
            self.size = int(W * 0.095)
        else:
            self.cy = int(H * 0.885)
            self.max_w = int(W * 0.70)
            self.cx = W // 2
            self.size = int(H * 0.085)
        self.stroke = max(2, int(self.size * 0.12))

    def draw(self, draw, words, timings, t, chunks=None):
        if not words:
            return
        chunks = chunks or chunk_words(words, timings)
        active_chunk = None
        for s, e, idxs in chunks:
            if s - 0.02 <= t < e:
                active_chunk = (s, e, idxs)
                break
        if active_chunk is None:
            return
        s, e, idxs = active_chunk
        pop = ease_out_back(clamp((t - s) / 0.14))
        size = int(self.size * (0.82 + 0.18 * pop))
        f = font(size)
        toks = [words[i].upper() for i in idxs]
        space = draw.textlength(" ", font=f)
        widths = [draw.textlength(tk, font=f) for tk in toks]
        # wrap into lines
        lines, cur, cur_w = [], [], 0.0
        for k, wdt in zip(range(len(toks)), widths):
            add = wdt + (space if cur else 0)
            if cur and cur_w + add > self.max_w:
                lines.append((cur, cur_w))
                cur, cur_w = [], 0.0
                add = wdt
            cur.append(k)
            cur_w += add
        if cur:
            lines.append((cur, cur_w))
        line_h = size * 1.12
        y0 = self.cy - (len(lines) - 1) * line_h / 2
        th = self.theme
        for li, (ks, lw) in enumerate(lines):
            x = self.cx - lw / 2
            y = y0 + li * line_h
            for k in ks:
                wi = idxs[k]
                ws, we = timings[wi]
                active = ws - 0.02 <= t < max(we, ws + 0.12)
                fill = th.sub_highlight if active else th.sub_fill
                ff = f
                yy = y
                if active:
                    big = int(size * 1.08)
                    ff = font(big)
                    yy = y - (big - size) * 0.1
                draw.text((x, yy), toks[k], font=ff, fill=fill, anchor="lm",
                          stroke_width=self.stroke, stroke_fill=th.sub_stroke)
                x += (draw.textlength(toks[k], font=ff) if active else widths[k]) + space
