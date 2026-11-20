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
