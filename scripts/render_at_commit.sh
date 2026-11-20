#!/usr/bin/env bash
# Render a video exactly as it was at an old commit, without touching the current checkout.
#   scripts/render_at_commit.sh <commit> <slug> [output.mp4]
# Uses a temporary git worktree (shares voices/models with the main checkout), renders there,
# copies the MP4 out and removes the worktree. The current branch and files are never changed.
set -euo pipefail
COMMIT="$1"; SLUG="$2"
ROOT="$(git rev-parse --show-toplevel)"
SHORT="$(git -C "$ROOT" rev-parse --short "$COMMIT")"
OUT="${3:-$ROOT/output/archive/${SLUG}_${SHORT}.mp4}"
mkdir -p "$(dirname "$OUT")"
OUT="$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")"
WT="$(mktemp -d)/wt_${SLUG}_${SHORT}"
git -C "$ROOT" worktree add --detach "$WT" "$COMMIT" >/dev/null
trap 'git -C "$ROOT" worktree remove --force "$WT" >/dev/null 2>&1 || true' EXIT
mkdir -p "$WT/models"
[ -d "$ROOT/models/piper" ] && ln -s "$ROOT/models/piper" "$WT/models/piper"
cd "$WT"
echo "[render_at_commit] $SLUG @ $SHORT -> $OUT"
python -m stickman_studio.explainer.render "$SLUG" -o "$OUT"
echo "[render_at_commit] done: $OUT"
