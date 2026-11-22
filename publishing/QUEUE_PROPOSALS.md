# Proposals for the 8 queued (not yet posted) videos - 2026-11-22

Status: **proposal, waiting for the owner's decision** (nothing re-rendered). All 8 rendered files open with O1
("If you put...") and end with E1 ("congratulations") - posted as they are, the rotation rule is broken 8 times
in a row. Codes and rotation: `.claude/skills/explainer-from-idea/SKILL.md`; check: `python tools/rotation.py --proposed` (passes).

Evidence level: **heuristic only** (hookscore / title.py lints; 0 videos with numbers). The new hooks score
40-53 vs 38-43 today - a modest lint gain, still mostly "WEAK" by the tool's own scale (it was tuned on
talking-head hooks). The title+cover pairs gain more (48-66 -> 94-98), mostly by removing duplicated words
between title and cover. None of this is a prediction of views.

## How a new hook would be built (if approved)
A new **step 0 of ~3 s**: the hook line over a visual teaser of the finished machine/payoff moment (e.g. the
fork sparking, the safety brake clamping), reusing the existing scene states - a readable change in the first
3 s, no static frame. Then the current step 0 ("If you put...") stays as the first build step. Ending = the last
step's first sentence changed; the joke and "Follow for more" stay. Cost: ~10-20 min of scene work per video
+ `qa.py` + a targeted contact sheet + ~20 min render each (no tokens while rendering). Each becomes a new
release `[VID-xxx-v(n+1)]`.

| Order | Video | New hook (formula, hookscore) | New ending | Title (title.py) | Cover (title.py pair) |
|---|---|---|---|---|---|
| 1 | elevator | O2 "What stops your elevator from falling if the rope snaps? A trick from 1854." (52) | E2 "And that's how you build an elevator." | Why Elevators Almost Never Fall (keep) | WHAT IF / IT SNAPS? (62 -> 94) |
| 2 | chatbot | O6 "Your chatbot never knows its next word until it types it. Let's build one." (53) | E3 "Now you know more about AI chatbots than 99% of people." | Why AI Chatbots Type One Word at a Time (keep) | IT'S JUST / GUESSING (62 -> 94) |
| 3 | atm_notes | O3 "One banknote is a tenth of a millimeter thick, and your ATM measures every single one before it pays you." (51) | E2 "And that's how you build an ATM." | How an ATM Catches Two Stuck Notes (new, fits the 40-char mobile cut) | 0.1 MM / DECIDES (52 -> 98) |
| 4 | traffic_light | O6 "There's a loop of wire cut into the road under your car, and it's why your light turns green." (40) | E4 loop: "...Follow for more. And remember, it all starts with..." -> replays into the hook | How Traffic Lights Know You're Waiting (new, shorter) | WIRE UNDER / YOUR CAR (48 -> 94) |
| 5 | microwave | O5 "Your microwave doesn't cook from the inside out. And that fork? We'll get to it." (41) - also fixes the title promise (fork) being first shown at ~70% | E3 "Now you know more about microwaves than 99% of people." | Why Forks Spark in the Microwave (keep) | SHARP POINTS / = LIGHTNING (62 -> 94) |
| 6 | self_checkout | O6 "The self checkout isn't watching you. It's weighing every item you put in your bag." (43) | E1 (keep "congratulations") | Who Is Judging You at Self-Checkout? (keep) | IT'S WEIGHING / YOUR BAG (66 -> 98) |
| 7 | undersea_cable | O2 "How does your message cross the ocean in a blink? Not by satellite. Along the ocean floor." (43) | E2 "And that's how you build an undersea internet cable." | How Your Message Crosses the Ocean (keep) | NOT / SATELLITES (62 -> 94) |
| 8 | streaming | O5 "You never actually download the movie you're watching. Not even close." (52) | E4 loop: "...Follow for more. And remember, that's why..." -> replays into "You never actually download..." | Why Netflix Starts in One Second (new; Netflix and "in a second" are in the script) | NEVER THE / WHOLE MOVIE (48 -> 94) |

All facts in these lines come from the existing scripts (1854 Otis demo, 0.1 mm note, 2.5 billion flips per
second, loop of wire before the stop line, "doesn't cook from the inside out", data along the ocean floor).

## Options for the owner (choose one)
- **A. Re-render all 8** with new hook + ending (+ new titles/covers): rotation respected from post #2. ~3 h of
  background rendering, about 1 session of work.
- **B. Re-render only the next 2-3 in the queue** (elevator, chatbot, atm_notes) and post the rest as they are,
  alternating with new videos (the rotation is then checked from the new ones on).
- **C. Post the queue as it is** (titles/covers can still change - those need no re-render, only a new cover PNG)
  and apply the new formulas only to new videos (EXP-001 first). Cheapest; the queue then measures the O1/E1
  baseline cleanly, which is useful for comparing later.
My recommendation: **C + the new titles/covers now**: the queue becomes a clean baseline (same hook and
ending on 9 videos = the length, topic and cover are the only differences), and every new video tests one
variable. Covers/titles change nothing in the video and fix the clearest measurable lint.
Cover note: Instagram takes `cover.png` as the Reel cover directly. On YouTube the cover is the last 0.5 s frame
inside the MP4: swapping it needs no full render - `ffmpeg` can replace the last 0.5 s of the existing MP4 in
seconds (Claude can script it if the owner wants; MP4s are not in git).
