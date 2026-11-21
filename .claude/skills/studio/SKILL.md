---
name: studio
description: Session start and wrap-up for the Stickman/Explainer video studio. "start" - orient in the repo, set up the environment, report status (videos done, in progress, idea backlog) and propose next actions. "wrap-up" - record feedback/preferences, update backlog statuses, library docs and skills, commit and push so the next session continues seamlessly. Use at the beginning or end of a session, or when the user asks for status, "what's next", or to save progress.
---

# Studio session

Read `CLAUDE.md` first (project map + owner preferences). Answer the owner in Romanian.

## Mode: start (default)
0. Read the section **"Where we left off"** in `CLAUDE.md` - it is the hand-over from the last session
   (what was posted, what is queued, the ordered to-do list). Follow its "Next session" list.
1. `git status`, `git log --oneline -15`, current branch; pull latest of the working branch (and `main`,
   which holds the last merged session).
2. Environment check (install only what is missing):
   `pip install -r requirements.txt`; `which espeak-ng || apt-get install -y espeak-ng`;
   Piper EN voice present? (`python -m stickman_studio.voices`) - else
   `python -m stickman_studio.voices --download en` (GitHub mirror works when Hugging Face is blocked).
3. Read `ideas/IDEAS.md` and `python -m stickman_studio.explainer.render --list`.
4. Report briefly: delivered videos, scripted-but-not-rendered, ideas waiting, last feedback from
   `CLAUDE.md`. Then propose 2-3 concrete next actions, e.g. "render ideas #3 and #8 as a batch",
   "generate 10 new ideas", "script your idea". Ask which (one question).

## Mode: wrap-up
1. Update `ideas/IDEAS.md` statuses (scripted / rendered / delivered + rating if given).
2. Put every new owner preference/feedback into `CLAUDE.md` -> "Owner preferences".
3. New reusable visuals -> confirm they are in `explainer/lib/` and listed in `LIBRARY.md`.
4. Lessons that would have saved time -> add to the relevant skill's "rules" section.
5. Rewrite the **"Where we left off"** section in `CLAUDE.md` (date, branch, what was posted/delivered, the
   posting queue, the ordered "Next session" list). Keep it short - it replaces the previous version.
6. Commit + push (and push to `main` when the owner asks). Tell the owner what was delivered and what the next session will pick up
   (videos not yet delivered must be re-rendered next time: MP4s are not stored in git).
