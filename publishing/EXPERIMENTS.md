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

## EXP-001 - Length ~60 s (status: planned)
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
