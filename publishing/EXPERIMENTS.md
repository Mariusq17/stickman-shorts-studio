# Experiments - one variable per video

Rules
- Each new video tests **one** variable (length, hook formula, ending, cover, posting time...). Everything else
  stays at the current default. Write the hypothesis and the decision rule **before** posting.
- Caveat we accept: the opening/ending rotation changes the hook formula on every video, so hook effects are
  learned across many videos (codes are logged in `STATS.md`), not from one A/B pair.
- One video is an anecdote. A result counts as a **hypothesis** after 1-2 videos, **likely** after 3-4 in the
  same direction, and only becomes a rule in CLAUDE.md "Learned rules" with its evidence level.
- Shorts numbers are noisy (the first test audience is small and random): compare against the baseline
  median, not against the single best video.
- Status: planned -> running (posted) -> measured (48h/7d in) -> concluded.

## Baseline (2026-11-22): card_tap, elevator, atm_notes - all O1 hook + E1 ending, 1:49-2:10
YT stayed-to-watch 55.7-65.7%, avg % viewed ~59-76% (early, different ages), subs/1k 0.75-3.3; card_tap curve:
cliff in the last ~13 s (payoff + CTA). Details: `STATS.md` table B. The 6 queued videos (also O1/E1) extend this
baseline if posted as they are.

## Priority after the first numbers (2026-11-22, hypothesis, 1-3 videos)
1. EXP-003 short ending / loop - the only measured cliff so far (card_tap, last ~13 s).
2. EXP-002 question hook - 34-44% swipe away at the start on all three.
3. EXP-001 ~60 s - elevator (2:10) did not do worse on % viewed than card_tap (1:54), so length looks less urgent.
The owner decides the order; EXP-001 was the owner's first pick.

**Decision 2026-11-22 (owner):** keep the long format. EXP-002 (hook) + EXP-003 (ending) run TOGETHER on the next
video, length unchanged: they are read on different metrics (hook -> "stayed to watch"; ending -> retention in the
last ~15 s / end cliff), so their effects stay separable. Targets (unverified heuristic): stayed >= 70%, avg % viewed
>= 70%. EXP-001 (~60 s) postponed: run it only if, after hook + ending fixes, avg % viewed stays under ~70%.

## EXP-001 - Length ~60 s (status: postponed 2026-11-22)
- **Variable:** duration ~55-65 s (5-6 fixes, ~170-190 words) instead of our usual 1:30-2:10 (7-11 fixes).
- **Why first:** biggest expected effect on "average % viewed", zero engine work, easy to read in Studio.
  Proposed by the owner and ranked #1 in the diagnostic (`STRATEGY.md`).
- **Hypothesis:** average % viewed goes up by >= 15 percentage points vs the baseline median of the long
  videos; viewed-vs-swiped stays about the same (it depends on the first seconds, not the length).
  Risk: fewer fixes -> less "aha", fewer shares/follows per 1k.
- **Baseline:** median of the first 3-4 posted long videos (card_tap, elevator, chatbot, atm_notes) at 7 days.
- **Test video:** the next NEW video (recommended idea #13 toilet or #11 fridge) written at ~60 s; hook and
  ending follow the rotation; same style, voice 1.2x, music, CTA. Optionally later: a 60 s cut of `streaming`
  (needs a re-render - ask the owner).
- **Measure:** 48 h and 7 d: avg % viewed (primary), viewed vs swiped, views, shares/1k, subs/1k, drop seconds.
- **Decision rule:** if avg % viewed >= baseline + 15 pp AND subs/1k not lower -> make 60-75 s the default for
  the next 2 videos (to confirm). If % viewed rises but subs/1k fall -> test ~90 s next. If nothing changes ->
  length is not our bottleneck; next experiment = hook (EXP-002).
- **Result:** -

## Queue of next experiments (pick after EXP-001 concludes)
- EXP-002 Question hook (O2) vs build-step hook (O1) - viewed vs swiped away.
- EXP-003 Short wind-down: CTA <= 4 s and loop ending (E4) - avg % viewed > 100% (replays) and end drop.
- EXP-004 Cover words different from the title (title.py "duplicate" fixed) - impressions CTR on channel page/IG grid.
- EXP-005 Posting time (18:00 vs 21:00 RO) - views at 48 h.
