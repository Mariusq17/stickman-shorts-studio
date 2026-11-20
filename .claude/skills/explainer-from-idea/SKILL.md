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
- **Hook = first build step**: "If you put <simplest version>, you've got the world's simplest <thing>."
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
