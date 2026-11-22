"""Story structure helpers for explainer scripts.

open_loop(): turns a classic "build it step by step" script into an open-loop one (owner's request 2026-11-22):
  - a ~3-4 s HOOK step in front: a question (or claim) whose answer comes LATE, spoken over a teaser of that late
    moment (the scene plays the answer step early - builder "teaser" steps), a short pause (`hook_pad`) so it keeps
    the video's normal pace, then a quick smooth camera move (`transition` s) into the original build;
  - an optional REMINDER appended to a middle step ("Hold that thought."), so the question stays open;
  - an optional REVEAL prefix on the answer step ("Here's the answer."), the climax;
  - a short ENDING whose last words run straight into the hook when the Short replays (loop): no padding after
    the last word (`ending_min=0`), no cover frame at the end (it would break the loop).
Owner feedback 2026-11-22: hooks must sound natural - one flowing sentence, never a lone "Why?" tacked on.
Indices are the ORIGINAL step indices (before the hook is inserted).
"""
from __future__ import annotations


def open_loop(steps, hook, answer_step, ending_text, *, teaser_frac=0.7, hook_keys=(), hook_pops=(), hook_cam=None,
              hook_sfx=(("w:{first}", "whoosh"),), reminder=None, reveal=None, ending_keys=(), ending_min=0.0, hook_pad=0.7, transition=0.7,
              ending_cam=None, ending_do=None, pegs="shocked", kinetic=True, hook_hl=(), hook_bursts=(),
              ending_hl=(), ending_bursts=()):
    """kinetic=True (owner 2026-11-22): hook and ending are never 'blank video + voice' - word-by-word captions
    synced to the voice in the lower third, plus `bursts` = dict(at="w:word", glyph="?!"|"99%"|"bolt"|"star"|"eye"|
    "check"|"cross", color=(r,g,b), xy=(0.78, 0.34)) badges that slam in with rays."""
    steps = [dict(s) for s in steps]
    if reminder:
        i, extra = reminder
        steps[i]["text"] = steps[i]["text"].rstrip() + " " + extra
    if reveal:
        steps[answer_step]["text"] = reveal + " " + steps[answer_step]["text"]
    cam = hook_cam or steps[answer_step]["cam"]
    first = hook.split()[0].strip(".,?!").lower()
    hpops = list(hook_pops)
    if kinetic:
        hpops.append(dict(kind="kinetic", text=hook, hl=list(hook_hl), until="end+0.1", sound=False))
        hook_keys = ()                                 # the kinetic captions replace keywords here
    for b in hook_bursts:
        hpops.append(dict(dict(kind="burst", until="end"), **b))
    hook_step = dict(text=hook, cam=cam, pegs=pegs, teaser=dict(step=answer_step + 1, frac=teaser_frac), pad=hook_pad,
                     keys=list(hook_keys), pops=hpops,
                     sfx=[(c.replace("{first}", first), n) for c, n in hook_sfx])
    steps[0]["cam_dur"] = transition                   # quick but smooth camera move into the first build step
    last = steps[-1]
    last["text"] = ending_text
    last["keys"] = [] if kinetic else list(ending_keys)
    if kinetic:                                       # every sentence except the CTA one gets kinetic captions
        sents, cur = [], []
        for w in ending_text.split():
            cur.append(w)
            if w.endswith((".", "!", "?")):
                sents.append(" ".join(cur))
                cur = []
        if cur:
            sents.append(" ".join(cur))
        pops = [p for p in last.get("pops", []) if p.get("kind") != "kinetic"]
        body = [x for x in sents if "follow" not in x.lower()]
        for j, sent in enumerate(body):
            nxt = sents[sents.index(sent) + 1] if sents.index(sent) + 1 < len(sents) else None
            until = f"w:{nxt.split()[0].strip('.,?!')}-0.15" if nxt else "end+0.2"
            pops.append(dict(kind="kinetic", text=sent.rstrip(".,"), hl=list(ending_hl), until=until, sound=False))
        for b in ending_bursts:
            pops.append(dict(dict(kind="burst", until="end"), **b))
        last["pops"] = pops
    last["min"] = ending_min
    last["cam"] = ending_cam or cam                    # end on the hook's framing -> seamless replay
    last.pop("cams", None)
    if ending_do is not None:
        last["do"] = ending_do
    words = [w.strip(".,?!").lower() for w in ending_text.split()]

    def spoken(cue):                                   # drop sound cues on words the new ending no longer says
        if not isinstance(cue, str) or not cue.startswith("w:"):
            return True
        head = cue[2:].split("+")[0].split("-")[0].split()[0].lower()
        return any(w.startswith(head) for w in words)
    last["sfx"] = [x for x in last.get("sfx", []) if spoken(x[0])]
    return [hook_step] + steps
