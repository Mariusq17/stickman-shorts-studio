# Explainer library

Reusable pieces for "build it step by step" explainer videos (2.5D isometric, rendered in pure
Python, offline). Every new video should **reuse** what is here and **add** any new generic piece
back into `lib/`, so the library grows with each video.

```
explainer/
  builder.py      narration-driven planner + renderer (cues, tracks, camera, post, overlays, audio, MP4)
  iso.py          IsoCam: isometric projection + primitives (box, poly, line, wheel, spring, text)
  timeline.py     keyframe tracks + easing names ("io", "smooth", "out", "in", "back", "lin")
  elevator.py     example video (script + scene)          <- copy this structure for new videos
  videos/         card_tap (shop + bank network), chatbot (word machine + belts), atm_notes (cutaway machine),
                  traffic_light (crossroad + cars), microwave (see-through door + x-ray), self_checkout (store lane),
                  undersea_cable (diorama with translucent water), streaming (servers -> ISP -> living room TV)
  branding.py     channel avatar, banner, per-video covers (COVERS dict); cover = last 0.5 s of each video
  lib/
    palette.py    harmonised colours, mix/warm/cool helpers, PEG_COLORS
    camera.py     CameraPath: spring-damped follow, handheld drift, hard-cut detection, speed
    post.py       Post: grade, vignette, DOF edge blur, whip-pan smear, old-film look; average() for motion blur
    shadows.py    ShadowLayer: soft projected shadows (box_on_plane) + ambient occlusion (ao_edge)
    characters.py draw_peg(): 'Pegs' mascots v2 (expressions, poses, look, reaction, hat)
    widgets.py    keywords, progress tracker and all pop-ups (see below)
    parts.py      2.5D parts: bolt, panel_seams, led, button_panel, digital_display, gear, pipe, fan,
                  screen, crate, light_panel, phone, server_rack, bank_building, car, signal_head
    kit.py        scene helpers: gradient_bg, peg (mascot + contact shadow), label (billboard callout, always drawn on top of the scene),
                  path_point/sub_path, packet (glowing data dot on a path), cable, glow_dot, rings,
                  plate / plane_text (rectangles + perspective-correct text printed on a plane, auto-fit with max_w/max_h), strip, sheet (banknote/ticket
                  moving along a path, can be doubled or crumpled)
```

## Writing a new video

1. **Script first.** Follow the formula: hook that is already the first build step
   ("If you put X in Y, you've got the simplest Z") -> "but..." problem -> "so you..." fix ->
   term revealed after the need ("That's the ...") -> repeat every ~8-12 s -> payoff that ties to
   a real-life moment -> "Congratulations, you just built a ..." + joke + CTA.
2. **One step per sentence or two**, as dicts in `STEPS` (see `elevator.py`):
   - `text` narration, `cam` ((focus xyz), zoom), `pegs` expression, optional `pose`, `min` duration
   - `do`: `(track, cue, value, duration_or_cue, ease)` -> drives the scene
   - `keys`: `("spoken phrase|shown text", COLOR)` -> keyword shown exactly when spoken
     (RED = problem, INK = term, BLUE = result)
   - `pops`: widgets (below), `cams`: extra camera moves on cues, `sfx`: `(cue, name)`
   - `fix`: cue -> advances the "FIXES n/N" progress tracker
3. **Cues**: `1.2` seconds, `"w:word"` when the word is spoken, `"w:word+0.3"`, `"end-0.5"`.
4. **Scene class** with `bg`, `draw(img, cam, tr, t, step_i, step_t)` and optionally
   `film_amount(tr, t)` (old-film post effect, e.g. flashbacks). Read animation values with
   `tr.get("track", t)`. Use `ShadowLayer` right after drawing static walls/floors.
5. Preview cheaply with `preview_times=[...]` (see `elevator.py --preview`), render with `--ss 2`.

## Widgets (pops)

| kind | fields | use for |
|---|---|---|
| `note` / `warn` / `check` | `text, pos` | short 2-4 word messages, problems, confirmations |
| `stamp` | `text, color, pos` | big moment ("SAFE!", "SOLVED") |
| `meter` | `text, from, to, color, fmt, anim` | a quantity going up/down (effort, temperature) |
| `bars` | `title, items[(label, value, color)]` | before/after comparisons |
| `count` | `from, to, fmt, sub` | numbers, years, counters |
| `equation` | `parts[], colors[], step` | a formula assembling piece by piece |
| `graph` | `title, track, window, color` | live line graph of an animation track (speed, load) |
| `arrow` | `xyz, text, color, off` | label pointing at a 3D part |
| `card` | `title, sub, tap` | follow CTA with tap animation |

Positions: `tl tr ml mr bl br bc c`. Timing: `at` + `dur` or `until` (cues).

## Camera & post (automatic)

- Camera keyframes from `cam`/`cams` are followed by a spring (natural inertia, slight settle).
  A jump that happens in one frame (duration `0.01`) becomes a **whip-pan** with a whoosh.
- Motion blur kicks in automatically on fast camera moves; DOF edge blur on close-ups (zoom > ~190).
- Grade + vignette always on; film grain when the scene reports `film_amount`.

## Adding to the library

- A part that could appear in another video (fan, gear, server, battery, pipe...) -> `lib/parts.py`.
- A new kind of pop-up -> `lib/widgets.py` (`draw_pop` branch + table above).
- New mascot pose/expression -> `lib/characters.py` (`POSES`, expression branches).
- Keep things readable at phone size: minimum text ~0.045 x width, thick strokes, few colours.

## Layout lessons (2.5D)

- The camera looks from +x,+y. A **cutaway** (open +y face) only shows internals with x < y (roughly):
  anything near the +x front panel hides behind it. Put mechanisms on a plane close to the open face.
- Things that tell a "journey" (packets, notes, words) read best flowing from top-left to bottom-right
  (along +x), with buildings/stations spaced ~2.4 units and a wide camera at zoom ~90.
- Desks/props in front (+y) of the main object cover it in close-ups: put them further out or aside.

- Translucent volumes (water, glass): draw the inside first, then paste a tinted L-mask over it
  (see `undersea_cable._water`) - cheap and keeps everything behind visible.
- See-through fronts (microwave door, cutaway): an "x-ray" track that skips the front panel/top while a
  hidden part (magnetron) is explained.

## Scene QA (`explainer/qa.py`)
Checks a video **without rendering**: runs the scene's own draw() on a recording camera and the planned
timeline (`builder.plan_timeline`, Piper word times or a calibrated estimate). Errors: props lingering after
their steps, moving objects overlapping, cables/pipes not connecting their end objects. Warnings: static screen
> 2 s while talking, keywords readable < 0.9 s or spoken twice, labels cut by the frame, unreadable text on
objects. Per-video spec: `QA = dict(objects=..., links=..., static_ok=...)` in the video module (+ `qa=QA` in
VIDEO). Examples: `videos/traffic_light.py` (cars), `videos/undersea_cable.py` (cable with bridges).
`python -m stickman_studio.explainer.qa <slug> [--rev <commit>] [--srt out.srt] [--json]`, `--all` for every video.

## Story structure (`lib/story.py`)
`open_loop(STEPS, hook, answer_step, ending_text, teaser_frac=.., reminder=(i, text), reveal="Here's the answer.",
hook_keys=[..], hook_pops=[..], ending_keys=[..], ending_do=[..])` -> inserts a ~3 s question hook over a teaser of
the answer step (builder `teaser=dict(step, frac)`: the scene plays a later moment), whip-cut into the build,
mid reminder, reveal line, short loop ending (no end cover - set `end_cover=False` in VIDEO). QA specs: write them
with original step indices and use `qa.shift_spec(QA, 1)` in VIDEO.

## Camera angle, kinetic captions, bursts (2026-11-22)
- `IsoCam(..., yaw=45, pitch=35.26)`: default = classic iso (bit-identical). Tracks `cam_yaw` / `cam_pitch` in a step's
  `do` swing the view (yaw 0 = looking straight at the +y face). Example: `videos/microwave.py` (door glass).
- Pops `kind="kinetic"` (text = a phrase spoken in that step; words appear as spoken; `hl` = red words) and
  `kind="burst"` (`glyph` "99%"/"?!"/"bolt"/"star"/"eye"/"check"/"cross", `color`, `xy` as fractions of the frame).
  `open_loop(..., hook_hl, hook_bursts, ending_hl, ending_bursts)` adds them to the hook and the ending.
