---
name: explainer-from-idea
description: Turn the user's own idea, topic, rough notes or a video type/reference ("like the vending machine one", "how X works") into an approved step-by-step explainer script (STEPS with cues, keywords, pop-ups, camera, fixes) ready for production. Use when the user gives a specific topic or idea to make a video from, or asks to write/rewrite an explainer script.
---

# From idea to explainer script

Input can be: a topic ("how a dishwasher works"), a question, notes, a link/reference video type, or
an idea from `ideas/IDEAS.md`. Output: a script the user can read, then a `STEPS` list for
`stickman_studio/explainer/videos/<slug>.py` (structure: copy `stickman_studio/explainer/elevator.py`).

## 1. Clarify only if needed
If the topic is ambiguous (which version of the system? which angle?), ask ONE question; otherwise
proceed. Video type defaults to "build it step by step"; other type seen in the reference channel:
"why is X almost impossible?" (question -> escalating obstacles with shocking numbers -> CTA).

## 2. Research the mechanism
List the real components in the order they would be *needed*, each with the problem it solves.
Use only well-established facts; if a number is not certain, drop it. 8-12 fixes.

## 3. Write the script (English, ~3.2 words/s -> ~400-450 words for 2-2.5 min)
- **Hook = first build step**, opened with a paradox line that is ALSO shown on screen from frame 0
  (`pops=[dict(kind="hook", at=0.0, until="w:<word ~2.5 s in>", text="Your fridge CAN'T make cold",
  hi=["can't","cold"])]`) and something already moving/exploding in the first 0.3 s (stats 2026-11-21:
  34% swiped away in the first second on card_tap).
- **Opening/closing rotation (owner approved 2026-11-21)** - never the same one twice in a row in posting order:
  openings: (a) paradox "Your X can't/never..." (b) "Did you know..." (c) "The simplest X is ... It's also
  terrible. Let's fix it." (d) classic "If you put <simplest version>, you've got the world's simplest <thing>."
  endings: (1) "And that's how you build a X." (2) "Now you know more about X than 99% of people."
  (3) "Congratulations, you just built a X." - each + one-line joke + "Follow for more."
  Batch 2026-11-21: fridge a/1, toilet c/2, gps b/3, touchscreen a/1, airbag a/2 -> next video: b or c / 3.
- **Length 1:20-1:40** (~260-300 words, 11-13 steps, 7-9 fixes).
- Loop: "But/Until <problem>." -> "So you <fix>." -> "That's the <term>." (term AFTER the need)
- Every ~10 s something new breaks; escalate stakes. Short sentences, conversational, dry humour.
- 1-2 **exaggerated, concrete comparisons** ("like a seesaw where your friend already sits on the
  other side", "a 3D city", "like tasting a dish and writing the recipe").
- **Payoff**: "So next time <everyday moment>, you'll know <hidden mechanism>."
- **Ending**: "And congratulations, you just built a <thing>." + one-line joke + "Follow for more."

## 4. Storyboard each step (show the user a compact table first)
step text | what is built/animated on which cue word | keywords (RED problem / INK term / BLUE result)
| pop-ups (meter, bars, count, equation, graph, warn/check, stamp, arrow) | camera (wide/close) |
mascot reaction | `fix` cue if it introduces a solution.

## 5. Approval -> production
Ask the user to approve or tweak the script (unless they said to go ahead without asking), then
hand over to the `explainer-video` skill. Save the approved script text in `ideas/IDEAS.md` under
the idea (status `scripted`) and commit.
