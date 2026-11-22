---
name: explainer-from-idea
description: Turn the user's own idea, topic, rough notes or a video type/reference ("like the vending machine one", "how X works") into an approved step-by-step explainer script (STEPS with cues, keywords, pop-ups, camera, fixes) ready for production. Picks the hook from 5 scored candidates and rotates opening/ending formulas. Use when the user gives a specific topic or idea to make a video from, or asks to write/rewrite an explainer script.
---

# From idea to explainer script

Input can be: a topic ("how a dishwasher works"), a question, notes, a link/reference video type, or
an idea from `ideas/IDEAS.md`. Output: a script the user can read, then a `STEPS` list for
`stickman_studio/explainer/videos/<slug>.py` (structure: copy `stickman_studio/explainer/elevator.py`).

## 0. Read the evidence first (2 minutes, small files)
- `publishing/WINNERS.md` - the best scripts **by numbers**; copy their structure, not their words.
- `CLAUDE.md` -> "Learned rules" (with confidence levels) and the open experiment in `publishing/EXPERIMENTS.md`.
  The new script must apply the experiment's variable (e.g. target length) and keep everything else as usual.
- `python tools/rotation.py` - which opening/ending formulas are forbidden for the next slot in posting order.

## 1. Clarify only if needed
If the topic is ambiguous (which version of the system? which angle?), ask ONE question; otherwise
proceed. Video type defaults to "build it step by step"; other type seen in the reference channel:
"why is X almost impossible?" (question -> escalating obstacles with shocking numbers -> CTA).

## 2. Research the mechanism
List the real components in the order they would be *needed*, each with the problem it solves.
Use only well-established facts; if a number is not certain, drop it. 8-12 fixes (fewer when the
experiment asks for a short video: ~60 s = 5-6 fixes, ~170 words).

## 3. Hook: 5 candidates, scored, best one wins
The hook = the first 1-2 sentences (9-24 words). It must (a) say the title's promise/question out loud,
(b) open a question the viewer can't close, (c) be visually the **first build step** (frame 0 shows the object
starting to be built - never a title card, logo or static frame). Visual principle (also seen in stickman
directing guides): a readable state change in the first 3 s + 0.5 s of readable hold.

Write 5 hooks, each from a different formula in `tools/yt/hooks.json`. Formulas that fit our format:

| Code | Formula (hooks.json id) | Our shape | Example |
|---|---|---|---|
| O1 | build-step (ours) | "If you put X in Y, you've got the world's simplest Z." | elevator |
| O2 | the-question / the-impossible | paradox question, then the build | "Your card has no battery. So how does it pay?" |
| O3 | the-statistic ("Did you know") | one verified number + consequence | "Every second, 13 million flips of a magnetic field wake your card." |
| O4 | the-before-after ("simplest, also terrible") | "This is the simplest X. It's also terrible. Let's fix it." | |
| O5 | the-mistake / contrarian-flip | the wrong belief the viewer has | "Your microwave doesn't cook from the inside out." |
| O6 | the-insider / the-teardown | "Inside every X there's a Y nobody tells you about." | |
| O7 | the-warning / the-clock | a stake or a time bound | "If every rope on your elevator snapped, a trick from 1854 would still catch you." |

Not for us: someone-elses-result, i-tried-it, the-stack, the-deadline, the-receipt (need a person/creator).
Score them: write the 5 lines to `output/hooks_<slug>.txt` and run `python3 -I tools/yt/hookscore.py output/hooks_<slug>.txt`.
Pick the best score **among the formulas allowed by the rotation**; on a tie prefer the one whose first 3 s
can be shown best. Show the owner the 5 hooks with scores in one compact table. Hookscore is a lint, not a
prediction (see `tools/yt/README.md`): never say "this hook will perform better", say "it scores higher on X".

## 3b. Open loop - the owner's rule (2026-11-22): build anticipation, answer as LATE as possible
- The hook asks the question whose answer comes LAST (the climax at ~70-90% of the video, before the payoff),
  not something answered in step 1. Pick the most surprising late fact / moment of the chain.
- The hook is spoken over a **teaser** of that answer moment (builder `teaser` step: the scene plays the late
  step early, ~3 s), then a whip-cut into the first build step. Never reveal the answer in the teaser's words.
- Mini-answers keep coming (every fix), so nobody feels cheated; 1 reminder at ~50% ("Still not the reason
  it ... Hold that thought."); the answer step starts with a reveal line ("Here's the answer.").
- Implementation: `stickman_studio/explainer/lib/story.py` -> `open_loop(STEPS, hook, answer_step, ending_text, ...)`;
  examples: `videos/traffic_light.py`, `videos/microwave.py`; QA specs keep original indices + `shift_spec(QA, 1)`.
- The title must promise the SAME question (title.py pair check). Evidence level: hypothesis, 0 videos measured.

## 4. Write the script (English, ~3.2 words/s at voice 1.2x)
- Length = the open experiment's target, otherwise the current rule in CLAUDE.md "Learned rules"
  (default until numbers exist: ~1:30-2:00, ~300-420 words).
- Loop: "But/Until <problem>." -> "So you <fix>." -> "That's the <term>." (term AFTER the need)
- Every ~10 s something new breaks; escalate stakes. Short sentences, conversational, dry humour.
  Avoid steps with no problem in them (pure exposition) - merge them into a problem step.
- If the title/cover promises a specific moment (the fork, the ambulance), tease it in the first 10 s
  and pay it off; never let the promised thing first appear after ~60% of the video without a tease.
- 1-2 **exaggerated, concrete comparisons**; one comic beat (a pause + mascot reaction) every ~30 s.
- **Payoff**: "So next time <everyday moment>, you'll know <hidden mechanism>."
- **Ending** from the rotation menu below + one-line joke + "Follow for more." Keep the wind-down after
  the last fix <= ~12% of the runtime; the CTA step no longer than needed for the follow card (>= 8.4 s
  `min` only while the card animation needs it).

### Rotation menu (approved by the owner 2026-11-22)
Never the same opening code or the same ending code twice in a row **in posting order**
(`tools/rotation.py` checks `publishing/STATS.md` posted rows + the planned queue).
Endings:
| Code | Ending line |
|---|---|
| E1 | "And congratulations, you just built a <thing>." |
| E2 | "And that's how you build a <thing>." |
| E3 | "Now you know more about <thing> than 99% of people." |
| E4 | (retired 2026-11-22: the loop is now a tail on EVERY ending, written "+L") |
| E5 | question to the comments ("Which fix surprised you?") then "Follow for more." |
**Loop tail (+L), standard since 2026-11-22:** the ending phrase, then "Follow for more. Because remember," -
those words run straight into the hook line when the Short replays; the last frame uses the hook's camera; no
cover frame at the end (`end_cover=False`); CTA step `min` ~6 s. Rotation applies to the ending phrase code.
Record the codes in the video's planned row in `publishing/STATS.md` (queue table) when the script is approved.

## 5. Storyboard each step (show the user a compact table first)
step text | what is built/animated on which cue word | keywords (RED problem / INK term / BLUE result)
| pop-ups (meter, bars, count, equation, graph, warn/check, stamp, arrow) | camera (wide/close) |
mascot reaction | `fix` cue if it introduces a solution | **exit** of every prop that is not needed later.

## 6. Approval -> production
Ask the user to approve or tweak the script (unless they said to go ahead without asking), then
hand over to the `explainer-video` skill. Save the approved script text in `ideas/IDEAS.md` under
the idea (status `scripted`), add the planned row (DNA) in `publishing/STATS.md`, and commit.
