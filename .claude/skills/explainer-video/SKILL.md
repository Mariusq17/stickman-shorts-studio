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
3. **Preview, don't guess**: `python -m stickman_studio.explainer.render <slug> --preview t1,t2,...`
   then Read the PNG. Check every step at ~30% and ~85% of its duration, and the hook second by
   second (0.2, 0.7, 1.1 ... 5 s). Fix before rendering.
4. **Release commit + push before the long render**: `[VID-<idx>-v<ver>] <slug>: <title>` (see skill
   `video-archive`), then after the render add the row to `publishing/VIDEOS.md`.
5. **Render** (background): `python -m stickman_studio.explainer.render <slug>` (~20 min per 2 min
   video on 4 CPU cores). Verify with `stickman_studio.pipeline.verify_video`.
6. **Deliver immediately**: send the MP4 with SendUserFile as soon as it is verified - never wait
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
- Use `lib/kit.py` helpers (peg, label, packet, sheet, plate/plane_text) instead of re-writing them.
- Start rendering each video as soon as its previews pass (background `render <slug>`, max 2 at once)
  while writing the next scene - a 3-video batch then takes ~1.5 h of wall time instead of 2+.
- Full render with motion blur + shadows: ~20 min per 2 min video (4 cores); 2 jobs in parallel
  are fine. Rendering costs no tokens - the token cost is writing scene code and checking previews.

