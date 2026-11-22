# Video registry

One row per **rendered version** of a video. Never delete rows (history). To re-render any old
version exactly: skill `video-archive` with the index (`#`) or the release ID, or by hand:
`scripts/render_at_commit.sh <commit> <slug>`.

Release IDs: `VID-<index>-v<version>`. Since 2026-11-20 every approved video gets its own commit whose
message starts with `[VID-<index>-v<version>]` (find it with `git log --grep "VID-002-v2"`).
Older versions (before this rule) are pinned by commit hash only.

| # | Release ID | Slug | Title (YouTube) | Length | Fixes | Commit (render code) | Rendered | Status / notes |
|---|---|---|---|---|---|---|---|---|
| 1 | VID-001-v4 | elevator | Why Elevators Almost Never Fall | ~2:10 | 11 | `a5550e0` (Merge PR #1) | 2026-11 (earlier session) | delivered, 9.5/10. Was voiced at 1.3x; this commit renders at 1.2x. MP4 not kept. |
| 2 | VID-002-v1 | card_tap | Your Card Has No Battery. So How Does It Pay? | 1:54 | 8 | `a65ac39` (Explainer: card_tap video ...) | 2026-11-20 | delivered; liked. Text on objects not in perspective (fixed later in engine). |
| 3 | VID-003-v1 | chatbot | Why AI Chatbots Type One Word at a Time | 2:00 | 8 | `e5fb308` (Explainer: chatbot video ...) | 2026-11-20 | delivered; old text rendering, labels can be hidden. |
| 4 | VID-004-v1 | atm_notes | How an ATM Knows Two Notes Are Stuck Together | 1:47 | 9 | `81de026` (Callout labels always drawn above the scene ...) | 2026-11-20 | delivered; perspective text + on-top labels. |

Descriptions, captions and covers: `publishing/<slug>/post.md` and `cover.png` (always for the latest version).

## Versions since the release-commit rule

| # | Release ID | Slug | Title (YouTube) | Length | Fixes | Commit (render code) | Rendered | Status / notes |
|---|---|---|---|---|---|---|---|---|
| 1 | VID-001-v5 | elevator | Why Elevators Almost Never Fall | 2:09 | 11 | `aba98bc` [VID-001-v5] | 2026-11-20 | delivered; voice 1.2x, new CTA, cover frame at end |
| 2 | VID-002-v2 | card_tap | Your Card Has No Battery. So How Does It Pay? | 1:54 | 8 | `c224b85` [VID-002-v2] | 2026-11-20 | delivered; perspective text, on-top labels, new CTA, cover at end |
| 3 | VID-003-v2 | chatbot | Why AI Chatbots Type One Word at a Time | 2:00 | 8 | `d13c4a1` [VID-003-v2] | 2026-11-20 | delivered; same upgrades |
| 4 | VID-004-v2 | atm_notes | How an ATM Knows Two Notes Are Stuck Together | 1:48 | 9 | `0f66980` [VID-004-v2] | 2026-11-20 | delivered; new CTA, cover at end |
| 5 | VID-005-v1 | traffic_light | How the Traffic Light Knows You're Waiting | 1:42 | 8 | `cc47131` [VID-005-v1] | 2026-11-20 | delivered; idea #8 |
| 6 | VID-006-v1 | microwave | Why Forks Spark in the Microwave | 1:41 | 7 | `2cfd497` [VID-006-v1] | 2026-11-20 | delivered; idea #4 |
| 7 | VID-007-v1 | self_checkout | Who Is Judging You at Self-Checkout? | 1:32 | 9 | `9ab4ad0` [VID-007-v1] | 2026-11-20 | delivered; idea #3 |
| 8 | VID-008-v1 | undersea_cable | How Your Message Crosses the Ocean | 1:31 | 7 | `876fb6a` [VID-008-v1] | 2026-11-20 | delivered; idea #6 |
| 9 | VID-009-v1 | streaming | Why Movies Start Instantly Even Though the File Is Huge | 1:23 | 6 | `e5c300d` [VID-009-v1] | 2026-11-20 | delivered; idea #10 (shortest, could get 2-3 more steps) |
| 5 | VID-005-v2 | traffic_light | How the Traffic Light Knows You're Waiting | 1:42 | 8 | `bcf4216` [VID-005-v2] | 2026-11-20 | delivered; cars exit after their step, no drive-through (fixes v1) |
| 8 | VID-008-v2 | undersea_cable | How Your Message Crosses the Ocean | 1:31 | 7 | `7322c98` [VID-008-v2] | 2026-11-20 | delivered; cable ends connect into the stations (fixes v1) |
| 3 | VID-003-v3 | chatbot | Why AI Sounds Sure Even When It's Wrong | 2:06 | 8 | `2cdda5e` [VID-003-v3] | 2026-11-22 | superseded by v4 (wrong screen texts/animations: step numbers shifted by the hook) |
| 3 | VID-003-v4 | chatbot | Why AI Sounds Sure Even When It's Wrong | 2:07 | 8 | `440b753` [VID-003-v4] | 2026-11-22 | delivered; open loop: natural hook + teaser of the late answer, reminder, reveal, gapless loop ending, no end cover |
| 5 | VID-005-v4 | traffic_light | The One Vehicle That Turns Every Light Green | ~1:47 | 8 | `440b753` [VID-005-v4] | 2026-11-22 | delivered; open loop: natural hook + teaser of the late answer, reminder, reveal, gapless loop ending, no end cover |
| 6 | VID-006-v3 | microwave | Why Forks Spark in the Microwave | ~1:43 | 7 | `440b753` [VID-006-v3] | 2026-11-22 | delivered; open loop: natural hook + teaser of the late answer, reminder, reveal, gapless loop ending, no end cover; see-through top + varied camera |
| 7 | VID-007-v2 | self_checkout | Who Is Judging You at Self-Checkout? | ~1:35 | 9 | `440b753` [VID-007-v2] | 2026-11-22 | delivered; open loop: natural hook + teaser of the late answer, reminder, reveal, gapless loop ending, no end cover |
| 8 | VID-008-v3 | undersea_cable | Why a Ship Goes Fishing for the Internet | 1:34 | 7 | `440b753` [VID-008-v3] | 2026-11-22 | delivered; open loop: natural hook + teaser of the late answer, reminder, reveal, gapless loop ending, no end cover |
| 9 | VID-009-v2 | streaming | You Never Actually Download the Movie | 1:25 | 6 | `440b753` [VID-009-v2] | 2026-11-22 | delivered; open loop: natural hook + teaser of the late answer, reminder, reveal, gapless loop ending, no end cover |
