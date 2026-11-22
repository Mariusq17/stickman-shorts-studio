"""Story structure helpers for explainer scripts.

open_loop(): turns a classic "build it step by step" script into an open-loop one (owner's request 2026-11-22):
  - a ~3 s HOOK step in front: a question whose answer comes LATE, spoken over a teaser of that late moment
    (the scene plays the answer step early - builder "teaser" steps), then a whip-cut into the original build;
  - an optional REMINDER appended to a middle step ("Hold that thought."), so the question stays open;
  - an optional REVEAL prefix on the answer step ("Here's the answer."), the climax;
  - a short ENDING whose last words run straight into the hook when the Short replays (loop), shorter CTA,
    no cover frame at the end (it would break the loop).
Indices are the ORIGINAL step indices (before the hook is inserted).
"""
from __future__ import annotations


def open_loop(steps, hook, answer_step, ending_text, *, teaser_frac=0.7, hook_keys=(), hook_pops=(), hook_cam=None,
              hook_sfx=(("w:{first}", "whoosh"),), reminder=None, reveal=None, ending_keys=(), ending_min=6.0,
              ending_cam=None, ending_do=None, pegs="shocked"):
    steps = [dict(s) for s in steps]
    if reminder:
        i, extra = reminder
        steps[i]["text"] = steps[i]["text"].rstrip() + " " + extra
    if reveal:
        steps[answer_step]["text"] = reveal + " " + steps[answer_step]["text"]
    cam = hook_cam or steps[answer_step]["cam"]
    first = hook.split()[0].strip(".,?!").lower()
    hook_step = dict(text=hook, cam=cam, pegs=pegs, teaser=dict(step=answer_step + 1, frac=teaser_frac),
                     keys=list(hook_keys), pops=list(hook_pops),
                     sfx=[(c.replace("{first}", first), n) for c, n in hook_sfx])
    steps[0]["cam_dur"] = 0.01                         # whip-cut from the teaser into the first build step
    last = steps[-1]
    last["text"] = ending_text
    last["keys"] = list(ending_keys)
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
