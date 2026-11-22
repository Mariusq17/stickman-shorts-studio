# tools/yt - vendored YouTube heuristics (MIT)

Copied from https://github.com/Jakeschincariol/youtube-agent-skill (commit `a2feb21`, MIT, (c) 2026 Jake
Schincariol - full text in `LICENSE`). Code was read before copying; standard library only, no network.
Only these files were taken: `hooks.json` + `hookscore.py` (yt-script), `title.py` (yt-package),
`retention.py` (yt-retention), `swipe.py` (yt-viral). Not taken: yt-edit, yt-chapters, yt-shorts (long-form).

Local changes (marked in the files):
- every file: a one-line origin/licence comment under the shebang;
- `swipe.py`: reads `hooks.json` from this folder;
- `retention.py`: `--transcript` uses a local SRT reader instead of `yt-edit/deadair.py`.

| Tool | Use in this repo | Command |
|---|---|---|
| `hookscore.py` | score 5 candidate hooks per script (skill `explainer-from-idea`) | `python3 -I tools/yt/hookscore.py hooks.txt` |
| `hooks.json` | the 21 hook formulas (shape, example, failure mode) | read it; mapping for our format in `explainer-from-idea` |
| `title.py` | title + cover text as a pair (skill `publish-kit`) | `python3 -I tools/yt/title.py --title "..." --thumb "COVER WORDS"` |
| `retention.py` | audience-retention CSV from YouTube Studio (skill `studio`) | `python3 -I tools/yt/retention.py ret.csv --duration 104 --transcript output/qa/<slug>.srt` |
| `swipe.py` | outliers in the niche: views as a multiple of the channel's median (skill `explainer-ideas`) | `python3 -I tools/yt/swipe.py output/niche.json --min 2` |

## Honest limits (read before quoting a number)
- `hookscore.py`: its author measured it on 74 real hooks - it separates *bad* hooks from real ones, it barely
  separates a creator's hits from their misses. A low score = look again; a high score is not a promise.
  It was tuned on talking-head hooks; our hooks are narration over a build, so treat it as a lint.
- `title.py`: built for long-form YouTube (desktop/mobile truncation, thumbnail). For Shorts the feed autoplays,
  so the cover matters mostly on the channel grid, search and the Instagram grid.
- `retention.py`: its "HOOK LEAK" uses the first 30 s (long-form). For Shorts read the first 3 s and the
  "viewed vs swiped away" number from Studio instead; cliffs and slide are still useful.
  `--duration` is required when the CSV x-axis is a percentage. Get a step-level SRT of our narration with
  `python -m stickman_studio.explainer.qa <slug> --srt output/qa/<slug>.srt`.
- `swipe.py`: needs >= 4 videos per channel; the formula it prints is a label for the TITLE, not the reason
  the video worked. Input from `tools/collect_niche.py` (public listings via yt-dlp, no login).
