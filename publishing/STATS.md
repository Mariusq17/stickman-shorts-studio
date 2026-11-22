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
Codes: opening O1-O7 and ending E1-E5 = rotation menu in `.claude/skills/explainer-from-idea/SKILL.md`.
| # | Slug | Release | Posted (date, RO time) | Where | Opening | Ending | First frame | Length | Fixes | Category | Experiment |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | card_tap | VID-002-v2 | 2026-11-20 (? h) | YT + IG | O1 | E1 | chip + wire loop appear on a blank card | 1:54 | 8 | payments / everyday tech | - (baseline) |

## B. Numbers (one row per video x checkpoint x platform)
| # | Slug | Checkpoint | Platform | Views | Viewed vs swiped (% stayed) | Avg % viewed | Avg view duration | Likes/1k | Shares/1k | Saves/1k | Subs (follows)/1k | Steep drops at (s) | Main traffic source | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | card_tap | 48h | YT | ? | ? | ? | ? | ? | ? | - | ? | ? | ? | waiting for the owner |
| 1 | card_tap | 48h | IG | ? | - | ? | ? | ? | ? | ? | ? | ? | ? | waiting for the owner |
| 1 | card_tap | 7d | YT | ? | ? | ? | ? | ? | ? | - | ? | ? | ? | due 2026-11-27 |

## C. Queue - planned DNA (posting order, next first)
Opening/ending codes of videos not yet posted. `python tools/rotation.py` checks A + C for repeats.
Current codes are what the rendered files contain; "proposed" = new hook/ending suggested in `STRATEGY.md`
(needs a re-render; the owner decides).
| Order | Slug | Release | Opening | Ending | Proposed opening | Proposed ending | Length | Fixes | Category |
|---|---|---|---|---|---|---|---|---|---|
| 1 | elevator | VID-001-v5 | O1 | E1 | O2 | E2 | 2:09 | 11 | transport / safety |
| 2 | chatbot | VID-003-v2 | O1 | E1 | O6 | E3 | 2:00 | 8 | AI |
| 3 | atm_notes | VID-004-v2 | O1 | E1 | O3 | E2 | 1:48 | 9 | money |
| 4 | traffic_light | VID-005-v2 | O1 | E1 | O6 | E4 | 1:42 | 8 | city / transport |
| 5 | microwave | VID-006-v1 | O1 | E1 | O5 | E3 | 1:41 | 7 | kitchen |
| 6 | self_checkout | VID-007-v1 | O1 | E1 | O6 | E1 | 1:32 | 9 | shopping |
| 7 | undersea_cable | VID-008-v2 | O1 | E1 | O2 | E2 | 1:31 | 7 | internet |
| 8 | streaming | VID-009-v1 | O1 | E1 | O5 | E4 | 1:23 | 6 | internet / entertainment |
