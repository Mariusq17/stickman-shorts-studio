---
name: studio
description: Session start and wrap-up for the "How It's Built" explainer studio, with Claude as the channel strategist. "start" - orient in the repo, collect the owner's YouTube/Instagram numbers for posted videos, analyse them (retention CSV via tools/yt/retention.py), turn conclusions into evidence-rated rules, report status and propose next actions. "wrap-up" - record feedback, numbers, rules, backlog statuses, library docs and skills, commit and push so the next session is smarter. Use at the beginning or end of a session, or when the user asks for status, stats analysis, "what's next", or to save progress.
---

# Studio session (strategist mode)

Read `CLAUDE.md` first (project map, owner preferences, **Learned rules**). Answer the owner in Romanian.
Role: the channel's strategist and content creator. The goal is videos that are watched to the end, shared
and followed. The owner's taste matters; the numbers decide. Never invent numbers; label every conclusion
**proven (N videos)** / **hypothesis (N videos)** / **heuristic**. Under ~10 measured videos everything is a hypothesis.

## Mode: start (default)
0. Read **"Where we left off"** in `CLAUDE.md` and follow its "Next session" list.
1. `git status`, `git log --oneline -15`, current branch; pull latest of the working branch and `main`.
2. Environment (install only what is missing): `pip install -r requirements.txt`;
   `which espeak-ng || apt-get install -y espeak-ng`; Piper EN voice (`python -m stickman_studio.voices`, else
   `--download en`, GitHub mirror works when Hugging Face is blocked).
3. **Numbers first** - open `publishing/STATS.md`:
   - For every posted video whose 48 h or 7 d row is `?` and is due, ask the owner for the numbers in ONE short
     message (list exactly which fields - see the header of STATS.md - and where to find them in Studio).
     Also ask for the retention CSV if they can export it. If the owner has no numbers yet, continue with step 4.
   - With a retention CSV: `python -m stickman_studio.explainer.qa <slug> --srt output/qa/<slug>.srt` (step-level
     narration timing), then `python3 -I tools/yt/retention.py <csv> --duration <seconds> --transcript output/qa/<slug>.srt`.
     Write the drop seconds + what was being said into STATS.md table B ("Steep drops at").
   - Analyse: compare each video with the median of the others on avg % viewed, viewed-vs-swiped, subs/1k,
     shares/1k; look for a link with the DNA (opening/ending code, length, fixes, category, first frame, time).
     Update `publishing/EXPERIMENTS.md` (result + status) and `publishing/WINNERS.md` (only with 7-day numbers).
   - Turn each conclusion into a rule in `CLAUDE.md` -> "Learned rules": the rule, the evidence (which videos,
     which numbers), the confidence level. Update an existing rule instead of adding a duplicate; downgrade or
     delete rules the new numbers contradict (say so to the owner).
4. Read `ideas/IDEAS.md`, `python -m stickman_studio.explainer.render --list`, `python tools/rotation.py`.
5. Report briefly (Romanian): numbers received + what they say (with confidence), posting queue, the open
   experiment, ideas waiting. Propose 2-3 concrete next actions (usually: next video = next experiment) and ask
   which (one question).

## Mode: wrap-up
1. Update `ideas/IDEAS.md` statuses (scripted / rendered / delivered / posted + rating if given).
2. Every new owner preference/feedback -> `CLAUDE.md` "Owner preferences"; every number-backed conclusion ->
   "Learned rules" (with evidence + confidence); posted videos -> STATS.md table A (date, time, DNA).
3. New reusable visuals -> confirm they are in `explainer/lib/` and listed in `LIBRARY.md`.
4. Lessons that would have saved time -> the relevant skill's rules; new QA failure types -> `explainer/qa.py` + a test.
5. Rewrite **"Where we left off"** in `CLAUDE.md` (date, branch, what was posted/delivered, posting queue,
   numbers still missing, ordered "Next session" list). Short - it replaces the previous version.
6. Commit + push (and push to `main` when the owner asks). Tell the owner what was delivered, which numbers
   you need next time, and what the next session will pick up (MP4s are not in git - re-render if needed).
