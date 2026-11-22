# Channel strategy - "How It's Built"

The strategist's notebook. Goal: videos that get **watched to the end, shared and followed**, not videos the
owner or Claude like. YouTube Studio numbers have the final word. Evidence levels used everywhere:
- **proven (N videos)** - seen in our own numbers on N videos (needs N >= ~10 to be called "confirmed").
- **hypothesis (N videos)** - plausible, seen in fewer than ~10 of our videos or only in a heuristic tool.
- **heuristic** - comes from a tool or general Shorts know-how; it is a reason to look again, never a prediction.

Until ~10 posted videos have numbers in `STATS.md`, **everything here is a hypothesis**.

Files of the learning loop: `STATS.md` (numbers + DNA per posted video) -> `EXPERIMENTS.md` (one variable per
video) -> rules in `CLAUDE.md` ("Learned rules") -> `WINNERS.md` (best scripts by numbers, read before scripting).

---

## Diagnostic 2026-11-22 (Phase 0, before any numbers exist)

Material: 9 scripts (`stickman_studio/explainer/videos/*.py` + `elevator.py`), titles in `publishing/*/post.md`,
covers in `branding.py` `COVERS`. Tools: `tools/yt/hookscore.py` and `tools/yt/title.py` (MIT, see
`tools/yt/README.md`). No audience data yet (card_tap posted 2026-11-20, numbers not given yet) -> every point
below is a **hypothesis or heuristic**, ordered by the estimated impact on retention.

### Already very good - keep it
1. **Visual style** (elevator 9.5/10): 2.5D isometric build, spring camera, motion blur, shadows, Pegs, pop-ups,
   FIXES tracker. The FIXES counter is a built-in progress bar -> a reason to stay ("how many fixes left?").
2. **Problem -> fix -> term loop every ~6-10 s**: every script has 6-11 fixes, a new problem every 2-3 steps.
   This is the engine of the "one more" feeling. Keep it.
3. **Narration-synced visuals and keywords** (built on the spoken word): rare on faceless channels.
4. **Concrete exaggerated comparisons** ("coffee in Tokyo five minutes after one in London", "air traffic
   control for groceries") - shareable lines.
5. **First frame is the object being built**, not a logo or a title card (hook = first build step).

### Risky - ordered by estimated impact on retention
1. **HIGH - the hook is a statement, not a question, and it is the same in 9/9 videos.**
   "If you put X..., you've got the world's simplest Y" names the topic only at the END of a ~6-8 s sentence
   (first 20-24 words). In the Shorts feed the decision viewed/swiped is made in ~1-2 s. hookscore: 9/9 hooks
   WEAK (38-43/100): curiosity 24, stakes 22 - nothing is at stake and no question is open in the first line.
   The title's question (the reason someone would stay) is never said out loud in the first sentence.
   *heuristic (hookscore; its own docs say it separates bad hooks from good ones, not hits from misses).*
2. **HIGH - title promise vs. first 3 seconds mismatch** in microwave ("Why Forks Spark" -> the fork appears at
   ~70% of the video, the first 3 s show a radio transmitter). If the cover/title promises a fork, the first 3 s should show the fork (or tease it:
   "...and by the end you'll know why a fork turns into a thunderstorm"). chatbot, card_tap, traffic_light answer
   their title early and keep the rest as bonus fixes - fine. *hypothesis.*
3. **MEDIUM-HIGH - long wind-down.** After the last fix there are 13-33% of the runtime with no new problem
   (payoff + "congratulations" + joke + CTA with `min=8.4 s`): microwave ~33%, chatbot ~23%, undersea ~21%.
   Shorts retention charts usually show the steepest drop exactly where the tension ends. The CTA card is 8.4 s
   long. The end also does not **loop** back into the first frame (a replay-friendly ending). *hypothesis.*
4. **MEDIUM - length 1:23-2:10 for a cold channel.** Average % viewed falls with length; at 0 subscribers
   the algorithm tests each Short on a small audience first, and % viewed / swiped-away are the signals it reads.
   A 60 s version of the same idea is the cheapest test with the biggest expected effect (Experiment 1).
   *hypothesis, 0 videos.*
5. **MEDIUM - identical ending formula 9/9** ("And congratulations, you just built a..."): fine for brand
   recognition, but regular viewers will start swiping at the familiar line. Rotation menu now approved
   (see `explainer-from-idea`). *hypothesis.*
6. **LOW-MEDIUM - covers repeat the title.** title.py on 9 title+cover pairs: 9/9 "duplicate" (the cover says the
   same words as the title), 8/9 "thumb-length" (cover > 4 words), 4/9 titles lose their subject in a 40-char
   mobile cut. For Shorts the cover matters less in the feed (autoplay) but matters on the channel grid, search
   and the Instagram grid. *heuristic (title.py is built for long-form YouTube).*
7. **LOW - steps without a problem** (pure exposition): microwave steps 1-2 and 10-12, chatbot 15-16,
   undersea 6 and 13. Facts are good; but a step without "but..." is where a scroll happens. *hypothesis.*

### What I would test first (one variable per video, see `EXPERIMENTS.md`)
1. **Duration ~60 s** vs. our usual ~1:45 (the owner's proposal - also my first pick: biggest expected effect,
   no engine work, easy to measure with "average % viewed" and "viewed vs swiped away").
2. **Question hook in the first sentence** (paradox / "Did you know") vs. "If you put...".
3. **Short ending** (payoff + 1-line ending, CTA <= 4 s, last frame = first frame for the loop).
4. Cover with different words than the title (curiosity gap), only after 1-3 have data.
