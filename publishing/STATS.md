# Stats - what each posted video did (the numbers have the final word)

Filled by the `studio` skill at every session start: Claude asks the owner for the numbers of posted videos that
have no data yet (48 h and 7 days after posting), writes them here, then analyses them (see `STRATEGY.md`).
**Never invent or estimate a number.** Unknown = `?`. Copy numbers exactly as YouTube Studio / Instagram show them.

Where the owner finds the numbers (YouTube Studio app or studio.youtube.com -> the Short -> Analytics):
- **Viewed vs swiped away** (Engagement / Audience tab, Shorts only): % of people who stayed instead of swiping.
- **Average percentage viewed** and **average view duration** (Engagement). Can be > 100% (replays).
- **Views**, **likes**, **shares**, **subscribers gained**, (Instagram: **saves**, **shares**, **follows**).
- **Retention chart** -> the seconds where the line drops steeply (or the CSV: Advanced mode -> Export ->
  send the file; `tools/yt/retention.py` reads it).
- **Traffic source** (Shorts feed / search / channel page / external).
Per-1k numbers are computed here: `likes / views * 1000` (Claude does the maths).

## A. DNA of each posted video (posting order)
Codes: opening O1-O7 and ending E1-E5 (+L = loop tail into the hook) = rotation menu in `.claude/skills/explainer-from-idea/SKILL.md`.
| # | Slug | Release | Posted (date, RO time) | Where | Opening | Ending | First frame | Length | Fixes | Category | Experiment |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | card_tap | VID-002-v2 | 2026-11-20 20:22 | YT + IG | O1 | E1 | chip + wire loop appear on a blank card | 1:54 | 8 | payments / everyday tech | - (baseline) |
| 2 | elevator | VID-001-v5 | 2026-11-21 ~19:00 | YT + IG | O1 | E1 | box on a rope in a shaft, motor on top | 2:10 | 11 | transport / safety | - (baseline) |

## B. Numbers (one row per video x snapshot x platform)
Snapshot = hours after posting when the owner read the numbers. YT per-1k = per 1,000 views. "~" = read from a
chart by eye. Raw Studio export: `stats_raw/2026-11-22_yt_studio_table_until_2026-11-21.csv` (data until 2026-11-21).
| # | Slug | Snapshot | Platform | Views | Engaged views | Stayed to watch (vs swiped) | Avg % viewed | Avg view duration | Likes/1k | Shares/1k | Comments | Subs (follows)/1k | Retention curve | Traffic source | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | card_tap | ~45 h (11-22 17:16) | YT | 1,333 | ? (855 at ~28 h) | 65.7% | 59% | 1:08 | ? | ? | ? | 0.75 (1 sub) | 75.1% at 0:30; slow slide to ~45-50% at ~1:40; **cliff ~1:40-1:53 to ~10%** (steps 16-17: payoff + "congratulations" CTA) | ? | CSV until 11-21: 59.93% avg viewed, 26 thumbnail impressions |
| 2 | elevator | ~22 h (11-22 17:18) | YT | ~1,200 | 730 | 59.6% | ~61% (1:19 / 2:10) | 1:19 | ? | ? | ? | 3.3 (4 subs) | not ready (Studio: up to 2 days) | ? | CSV after a few hours: 69.42% avg viewed (347 views) |
| 3 | atm_notes | ~5 h (11-22 17:19) | YT | 329 | 171 | 55.7% | ~76% (1:23 / 1:49) | 1:23 | ? | ? | ? | 3.0 (1 sub) | not ready | ? | very early |
| 1 | card_tap | ~2 d (11-22 17:21) | IG | 362 | - | - | ? | ? | 27.6 (10) | 0 (0 sends) | 0 | ? | ? | ? | |
| 2 | elevator | ~21 h | IG | ~1,700 | - | - | ? | ? | ~42 (71) | 0 | 0 | ? | ? | ? | |
| 3 | atm_notes | ~5 h | IG | ~1,700 | - | - | ? | ? | ~31 (52) | 0 | 1 | ? | ? | ? | IG caption started "The ATM just pinched every..." |
| 4 | chatbot | ~16 h (11-23 12:48) | YT | 317 | 200 | 64.5% | ~41% (0:52 / 2:08) | 0:52 | ? | ? | ? | ~3 (1 sub?) | not ready | Shorts feed 9 / other YT 2 / other 1 (first 60 min) | views ~240 in the first ~4 h, then flat |
| 2 | elevator | ~42 h (11-23) | YT | ~1,200 | ? | (59.6% at 22 h) | ? | ? | ? | ? | ? | ? | not given | ? | "watched right now" list |
| 3 | atm_notes | ~24 h (11-23) | YT | 436 | ? | (55.7% at 5 h) | ? | ? | ? | ? | ? | ? | not given | ? | |
| - | CHANNEL | 28 days (11-23) | YT | 3.2K | - | - | - | - | - | - | - | 6 subs total | - | - | 41.8 watch hours; 100% new viewers; US 14.9% (top), Indonesia 3.3, Philippines 3.1, India 2.8, UK 2.2; 94.3% male; 25-34 = 43.1%, 18-24 17.5%, 35-44 19.9%, 13-17 10.5% |
| 1 | card_tap | 7 d | YT + IG | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | due 2026-11-27 |
| 2 | elevator | 48 h / 7 d | YT + IG | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | due 11-23 / 11-28 |
| 3 | atm_notes | 48 h / 7 d | YT + IG | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | ? | due 11-24 / 11-29 |

### Snapshot 2026-11-25 (YouTube Studio export, `stats_raw/2026-11-26_*`) - all 8 posted videos
| Video | Hook | Posted | Length | Views | Engaged | Stayed to watch | Avg % viewed | Avg view dur. | Likes | Shares | Subs + |
|---|---|---|---|---|---|---|---|---|---|---|---|
| microwave v4 | open loop (question) | 11-24 | 1:45 | 1,377 | 1,003 | **76.3%** | 54.7% | 0:57 | 40 | 3 | 2 |
| streaming v3 | open loop (claim) | 11-24 | 1:27 | 1,378 | 882 | 66.2% | **80.4%** | 1:09 | 22 | 0 | 0 |
| card_tap v2 | O1 | 11-20 | 1:54 | 1,343 | 866 | 65.9% | 60.0% | 1:08 | 31 | 1 | 2 |
| traffic_light v5 | open loop (claim) | 11-23 | 1:46 | 1,271 | 850 | 69.4% | 46.3% | 0:49 | 23 | 0 | 0 |
| elevator v5 | O1 | 11-21 | 2:10 | 1,256 | 754 | 59.9% | 60.9% | 1:19 | 40 | 0 | 5 |
| self_checkout v3 | open loop (claim) | 11-25 | 1:38 | 1,200 | 758 | 63.4% | 56.1% | 0:55 | 37 | 0 | ? (young) |
| chatbot v4 | open loop (claim) | 11-22 | 2:08 | 1,173 | 763 | 67.6% | 45.6% | 0:58 | 27 | 0 | 2 |
| atm_notes v2 | O1 | 11-22 | 1:49 | 1,085 | 688 | 64.3% | 71.2% | 1:17 | 26 | 0 | 1 |
| **Channel** | | | | **10,083** | 6,564 | 66.7% | 58.6% | 1:03 | 246 | 4 | 13 (-2) |
Daily engaged views: every video gets its burst within ~24 h, then almost nothing (traffic_light 793 -> 7 -> 50;
microwave 13 -> 967 -> 23; streaming 764 -> 118). Thumbnail impressions 978, CTR 0.72% (irrelevant for Shorts).
Instagram (owner, 11-26): ~1,700-1,800 views and 50-70 likes on most reels; 2 reels only ~300 views (which ones: ?).

## C. Queue - planned DNA (posting order, next first)
Opening/ending codes of videos not yet posted. `python tools/rotation.py` checks A + C for repeats.
Current codes are what the rendered files contain; "proposed" = new hook/ending suggested in `STRATEGY.md`
(needs a re-render; the owner decides).
| Order | Slug | Release | Opening | Ending | Proposed opening | Proposed ending | Length | Fixes | Category |
|---|---|---|---|---|---|---|---|---|---|
| 1 | chatbot | VID-003-v3 (open loop) | O2 | E3+L | O2 | E3+L | ~2:05 | 8 | AI |
| 2 | traffic_light | VID-005-v3 (open loop) | O6 | E2+L | O6 | E2+L | ~1:47 | 8 | city / transport |
| 3 | microwave | VID-006-v2 (open loop) | O2 | E3+L | O2 | E3+L | ~1:43 | 7 | kitchen |
| 4 | self_checkout | VID-007-v2 (open loop) | O6 | E1+L | O6 | E1+L | ~1:35 | 9 | shopping |
| 5 | undersea_cable | VID-008-v3 (open loop) | O2 | E2+L | O2 | E2+L | ~1:39 | 7 | internet |
| 6 | streaming | VID-009-v2 (open loop) | O5 | E3+L | O5 | E3+L | ~1:25 | 6 | internet / entertainment |
| 7 | toilet | VID-010-v1 (open loop) | O6 | E2+L | O6 | E2+L | ~1:40 | 7 | home |
| 8 | fridge | VID-011-v1 (open loop) | O5 | E3+L | O5 | E3+L | ~1:38 | 8 | kitchen |
