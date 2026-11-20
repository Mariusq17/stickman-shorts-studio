---
name: video-archive
description: Keep the registry of every rendered video version (publishing/VIDEOS.md) and re-render any OLD version exactly as it was, from its pinned commit, without disturbing the current code. Use when the owner asks for an old video / an earlier version again ("rerender video 3", "give me the first ATM video", "VID-002-v1"), and after every new approved render to register it (release commit + registry row).
---

# Video archive (registry + re-render old versions)

Registry: `publishing/VIDEOS.md` - one row per rendered version: index `#`, release ID `VID-<index>-v<version>`,
slug, YouTube title, length, fixes, commit, date, status. Never delete rows.

## A. Register a new/approved video version (do this every time a video is final)
1. Make sure previews passed and the scene + engine changes are what was rendered.
2. Create the **release commit** BEFORE the final render (so the commit = the exact code that renders it):
   `git add -A <video file> stickman_studio/explainer publishing ideas`
   `git commit -m "[VID-<idx>-v<ver>] <slug>: <short title>"` (+ the attribution lines) and push.
   - index: the video's existing `#` in VIDEOS.md, or the next free number for a new video (3 digits).
   - version: previous version + 1 for that slug.
   - If nothing changed since the last commit, use `git commit --allow-empty` so the ID still exists.
3. Render from that commit (normal `render <slug>` in the current checkout).
4. Add the row to `publishing/VIDEOS.md` (commit = short hash of the release commit + its message),
   update `ideas/IDEAS.md` status, commit "registry: VID-<idx>-v<ver> rendered" and push.

## B. Re-render an old version (argument: `#` index, release ID, or slug [+ version])
1. Read `publishing/VIDEOS.md`, find the row. Index only -> take the **latest** version of that index unless
   the owner says otherwise; ask only if it is ambiguous.
2. Resolve the commit: the hash in the row, or `git log --all --grep "<release ID>" --format=%h -n1`.
   Fetch first if missing: `git fetch origin <branch>`.
3. Render it without touching the current checkout:
   `scripts/render_at_commit.sh <commit> <slug> output/archive/<slug>_<releaseID>.mp4` (run in background;
   ~20 min). It uses a temporary git worktree, links the Piper voices, renders, and deletes the worktree.
   If the script itself does not exist at that point in history, that is fine - it runs from the current
   checkout and only the worktree is old.
4. Verify (`stickman_studio.pipeline.verify_video`) and send it with SendUserFile.
5. The current branch was never switched; nothing to restore. Do not add a registry row for a pure
   re-render of an existing version (optionally note "re-rendered <date>" in its notes).

## Rules
- Old commits may render with older defaults (e.g. voice speed): mention it if the registry notes say so.
- Never `git checkout` an old commit in the main working tree (risk of losing uncommitted work) - always
  use the worktree script.
