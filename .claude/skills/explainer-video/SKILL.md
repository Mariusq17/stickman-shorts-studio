---
name: explainer-video
description: Produce premium "build it step by step" explainer videos (2.5D isometric, pure Python, offline render) from a chosen idea - script, scene code, previews, full render, delivery - including batches of several videos with resume across sessions. Use when the user asks to make/render/produce one or more explainer videos, continue an unfinished batch, or improve an existing explainer.
---

# Explainer video production

Engine: `stickman_studio/explainer/` (read `stickman_studio/explainer/LIBRARY.md` first - it lists
every reusable piece). Reference video: `stickman_studio/explainer/elevator.py` (rated 9.5/10 by the
user) - copy its structure. Language: **English**. Format: 1080x1920, 30 fps, 2-2.5 min.

## Pipeline per video

1. **Script** (if not already approved): use the `explainer-from-idea` skill. Facts must be real and
   well established; no invented numbers.
2. **Scene file** `stickman_studio/explainer/videos/<slug>.py` exposing
   `VIDEO = dict(slug, title, steps, scene, initial, overlays, tracker=dict(label="FIXES"))`.
   - Reuse `lib/` (parts, characters, widgets, shadows). Anything generic you build -> add it to
     `lib/` and to the table in `LIBRARY.md` (the library must grow with every video).
   - Visual bar = elevator v4: room/backdrop context, soft shadows (`ShadowLayer` after static
     geometry), moderate detail (bolts, seams, LEDs, displays), moving indicators that show motion,
     Pegs mascots reacting (expr + pose), 1-3 widgets per explanation-heavy step.
3. **Scene QA (no rendering, ~1 s)**: give the scene file a `QA = dict(objects=..., links=..., static_ok=...)`
   spec (format in the docstring of `stickman_studio/explainer/qa.py`): every moving/temporary prop with the
   fill colour of its boxes and the steps it belongs to; every cable/pipe with its two end objects. Then
   `python -m stickman_studio.explainer.qa <slug>`. **All ERRORs must be fixed before any preview or render**
   (linger, pass-through, link). WARNs (static > 2 s while talking, keyword < 0.9 s, label cut by the frame,
   unreadable text on objects) are fixed when cheap, otherwise listed to the owner. The report also prints the
   DNA numbers for `publishing/STATS.md` (length, hook seconds, fixes, wind-down %).
4. **Preview, don't guess**: `python -m stickman_studio.explainer.render <slug> --preview t1,t2,...`
   then Read the PNG. Check every step at ~30% and ~85% of its duration, and the hook second by
   second (0.2, 0.7, 1.1 ... 5 s). Fix before rendering.
5. **Release commit + push before the long render**: `[VID-<idx>-v<ver>] <slug>: <title>` (see skill
   `video-archive`), then after the render add the row to `publishing/VIDEOS.md`.
6. **Render** (background): `python -m stickman_studio.explainer.render <slug>` (~20 min per 2 min
   video on 4 CPU cores). Verify with `stickman_studio.pipeline.verify_video`.
7. **Deliver immediately**: send the MP4 with SendUserFile as soon as it is verified - never wait
   for the rest of a batch.

## Batch of several videos

- Write + preview + commit ALL scene files first, then start one batch in the background:
  `python -m stickman_studio.explainer.render --batch slugA slugB slugC --jobs 2`
  (`output/explainers/status.json` tracks progress; finished videos are skipped on re-run).
- Poll the status file; send each MP4 the moment it is `done`.
- Running out of budget/session: make sure everything is committed and pushed, tell the user which
  videos were delivered and which remain, and that the next session continues with the same
  `--batch` command (it skips finished ones; MP4s are not in git, so deliver before the session ends).
- Update `ideas/IDEAS.md` status (scripted / rendered / delivered) and commit.

## Hard-won rules (do not relearn them)

- Narration drives everything: use cues `"w:word"` so visuals appear exactly when spoken. Every cue
  word must exist in that step's text (the planner raises KeyError otherwise).
- Hook: screen must not be static - build the object piece by piece on the hook's own words, camera
  starts close and pulls out as it grows.
- Keywords: 1-3 words, RED = problem, INK = term, BLUE = result; consecutive keywords replace
  each other (builder handles timing). Never full subtitles.
- Voice: Piper at `voice_rate=1.2` (user preference; ~3.2 words/s). Music lofi at 0.07.
- Draw order matters in 2.5D: anything behind a wall/face must be drawn before it; place doors and
  landings on back walls so they never cover the main object.
- Give animation-heavy steps a `min` duration; last CTA step `min` >= 8.4 s so the follow-card tap
  is visible. CTA = `card` pop on "Follow".
- Text on screen >= 0.045 x width; keep pops away from the subject (positions tl/tr/bc...).
- Mascots are our own "Pegs" - never copy other channels' characters, names or visuals.
- Tracker `fix` cue on every step that introduces a solution (target 8-12 fixes per video).
- Cue matching is case-insensitive on word prefixes ("w:open" matches "Open"); pick a word that
  appears once in the step, or the first occurrence is used.
- A camera jump in `cams` with duration `0.01` becomes an automatic whip-pan + whoosh (used for
  flashbacks); scenes can return `film_amount(tr, t)` for an old-film look.
- Mascot behaviour per step: `pegs="<expr>"` and optional `pose="<pose>"` (see lib/characters.py).
- Romanian Piper voice (ro_RO-mihai) needs Hugging Face; untested from the container. Videos are
  English by default.
- Cutaway machines: internals must sit near the open (+y) face or they hide behind the front panel; check
  the first preview specifically for "is the mechanism visible?".
- Text on any surface: `kit.plane_text(cam, plane, c, u, v, text, size, color, max_w=..)` - it is warped
  into the plane's perspective and shrunk to fit. Never `cam.d.text` on a 3D surface (only billboards/labels).
- Callouts: `kit.label(...)` is automatically drawn above the whole scene; use it for part names.
  Use `now=True` only for text that should be occluded on purpose.
- `qa.py` is the first line of defence for the WHOLE timeline (it caught traffic_light v1 and undersea_cable v1,
  which needed v2 renders); a new kind of visual bug the owner reports -> add a check to `qa.py` + a test in
  `tests/test_explainer_qa.py`, so it is never relearned.
- Check the WHOLE timeline, not only each step: a final contact sheet every ~4 s from start to end, looking
  for props that linger after their step, objects driving through each other, and cables/pipes that stop
  short of their endpoints. The second half of a video gets the same care as the hook.
- Every prop gets an exit: when its step is over, animate it away (or hide it) unless the payoff reuses it.
- Use `lib/kit.py` helpers (peg, label, packet, sheet, plate/plane_text) instead of re-writing them.
- Before the final render: add the video to `COVERS` in `branding.py` and run `branding cover <slug>` - the
  cover is appended as the last 0.5 s of the MP4 (YouTube Shorts thumbnail picker).
- One render process uses ~1 core; the container has 4 -> run up to 4 renders at once (`--jobs 4`).
- `sfx` cues: a number (0.55) or a string cue ("w:word", "end-0.3") - never a number inside quotes.
- Start rendering each video as soon as its previews pass (background `render <slug>`)
  while writing the next scene - a 3-video batch then takes ~1.5 h of wall time instead of 2+.
- Full render with motion blur + shadows: ~20 min per 2 min video (4 cores); 2 jobs in parallel
  are fine. Rendering costs no tokens - the token cost is writing scene code and checking previews.
- Scene code that tests step numbers (`if step_i == 2`, `tr.step_at(t) == 10`) keeps working after `open_loop()`
  only because the builder hands scenes `SceneTracks` + ORIGINAL step numbers (hook steps not counted). Never pass
  the raw tracks to a scene. Lesson 2026-11-22: chatbot v3 showed the wrong screen texts and skipped the
  "Banana. Seven. Purple." boxes because the hook shifted every step by 1 -> fixed in v4; covered by a test.
- After restructuring a script (hook inserted, steps moved), preview the steps with step-specific content
  (screens, special props), not only the hook - QA cannot see "the right text on the right step".
- Camera variety (owner, 2026-11-22, microwave): never hold one framing for long stretches - change framing every
  ~5-8 s with smooth moves (`cams` with 0.9-1.4 s): push in close for what happens inside, pull back wide when the
  explanation is done, try other vantage points. The iso angle is fixed, so variety = focus + zoom + reframing.
  No instant cuts unless it is a deliberate whip (flashback).
- Big plain surfaces (an oven top, a cabinet side) must not fill half the frame for long: make covers see-through
  (outline + glass glints, hide the inner ceiling) when the action is inside - example `videos/microwave.py` `ghost`.
