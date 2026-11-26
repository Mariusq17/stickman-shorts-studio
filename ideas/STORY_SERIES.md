# Idea (owner, 2026-11-26): interactive story series - "the viewers decide"

Status: idea, NOT started. Owner will send 2 reference videos in a NEW chat (another creator: ~4M + 1.3M Instagram
views in 3 days on a brand-new account). Watch them, extract the mechanics, then design OUR OWN story.

## The format (as the owner described the reference)
- A serialized story about a very "loser" character trying his luck. Reference premise: a "Discord-mod" type gets a
  message from a former high-school classmate inviting him to the reunion ball; she likes how he "looks" because he
  lied (rich, handsome, athletic); he has one month to fix himself, ONE thing per episode.
- Every episode ends with 2 options for what happens next; viewers vote in the comments; the next episode follows
  the winning option. Comments = the engine (the algorithm push the owner wants).
- The storytelling must stay gripping for the whole video (hook, escalation, cliffhanger, vote).

## Rules for us
- Same MECHANIC, our own characters, premise, art and jokes - never a recreation of the reference story/character.
- Engagement asks built in naturally: the vote = comments; "like if you'd do the same" style lines; follow at the end.
- Measure it like everything else (STATS.md): stayed-to-watch, % viewed, comments/1K, shares, follows.

## Brand question (Claude's recommendation, to confirm with the owner)
- "How It's Built" = engineering explainers; a comedy story series is a different promise and a different audience.
- Recommended: a SEPARATE YouTube channel + Instagram account for the story series (clean test, separate numbers,
  no mixed signals). The current channel is tiny (13 subs), so little would be lost either way.
- Names/handles CAN be changed later on YouTube and Instagram (both allow it, with frequency limits - check the
  current limits in the app settings), so the choice is reversible.
- Tools: the repo's original Stickman Video Studio (`app.py`, `stickman_studio/`) already makes stickman story
  shorts - starting point for the visuals; the 2.5D explainer engine is NOT needed for stories.

## Reference analysis (2026-11-26, Claude) - 2 episodes received (Day 1 = 1:38, Day 2 = 1:53, 720x1280)
Transcript reconstructed from the burned-in captions (no speech-to-text available in the container: Hugging Face
blocked). Mechanics only - we do NOT reuse the character, premise, gags or art.

### Format DNA
- **Persistent HUD** top-left on every frame: `DAYS LEFT 30` + `GLOW-UP 0%` meter. Countdown = stakes, meter = progress
  the viewer wants to see move (still 0% on Day 2 -> slow burn, people come back to see it rise).
- **Captions**: 1-3 words at a time, huge white bold, key word coloured (names pink, choices blue/green, failures red).
  Every ~0.5 s new caption -> constant motion even when the art is static.
- **Art**: flat 2D cartoon, one front-facing character, simple full-screen backgrounds that change every 5-10 s
  (bedroom, bathroom, kitchen, street, shop, park, phone screen). Cheap to produce; the WRITING carries it.
- **Phone-text screens** (iMessage-style) are a recurring beat: the crush's messages, him typing/deleting/sending.

### Episode structure (both episodes follow it)
| Time | Beat | Day 1 | Day 2 |
|---|---|---|---|
| 0-4 s | Countdown + stakes in the first sentence | "Thirty days. That's how long James has until his high school reunion." | "Twenty-nine days..." same line |
| 4-10 s | Recap of the VOTE (viewer agency) | - (Day 1: roast intro instead: "Look at him. James is a chud. Headset on, Cheeto dust up to the elbow, hasn't seen sunlight since the last patch update.") | "Yesterday YOU picked his teeth. So today James is going to brush them properly." |
| 13-25 s | Inciting text / the open question | "Then Sarah texts. Not a Sarah. THE Sarah. Prom Sarah." -> "Thirty days to fix everything. Where do we even start?" | obstacle: "He's never owned one" (toothbrush) |
| 25-75 s | 6-8 locations x 5-8 s, each one gag (rule of 3, exaggerated personification) | mirror fogs up "out of embarrassment", fridge note says NO, sun hits him "like a jumpscare", dog files a complaint, shop employee walks him to the deodorant "personally", puddle reflection looks away "hmph" | callbacks: same employee, "NOT TODAY" -> "EXTRA FIRM" toothbrush; brushing gags ("the bristles bend", "seen things", "respect"); small win: first person ever smiles at him; dog = "just a warning"; puddle doesn't look away "for about one second" |
| 75-85 s | Crush beat = cringe button | types a long reply, deletes, sends "k". "And that's his opening move." | Sarah: "haha you haven't changed at all" - he reads it x4, deletes, sends a smiley |
| last ~12 s | **The vote**: split screen 2 options, each with a funny one-line subtitle, "COMMENT ONE WORD", VOTE NOW button | TEETH ("brush them. properly.") vs SHEETS ("wash them. first time since 2019.") - "One of them changes his life today. Vote now. Day two starts with your choice." | the LOSING option comes back escalated: SHEETS ("they have eyes now") vs TOENAILS ("they click on the floor") - "Day three starts with your choice." |

### Why it works (hypotheses, from 2 episodes + the reported 4M / 1.3M views)
1. Stakes + deadline in sentence 1, and the countdown never leaves the screen.
2. Viewer agency: "YOU picked" -> the commenter feels ownership -> comes back for the next episode (and comments again).
3. Voting costs ONE word -> lowest-effort comment possible -> huge comment volume -> algorithm push.
4. Running callbacks (employee, dog, puddle, crush texts) reward returning viewers; each episode stands alone too.
5. Small wins + new humiliation in every episode; the main payoff (the reunion / the meter at 100%) is 30 episodes away.
6. Losing option recycled and escalated -> the "other" voters get a second chance, tension builds.
7. Gag density: one joke every ~5-8 s, mostly personification of objects (mirror, fridge, sun, dog, puddle).

### Rules for OUR series (from this analysis)
- Same skeleton: HUD (countdown + meter), stakes line first, recap "Yesterday you picked X", 6-8 gag locations,
  a recurring "pressure" beat (texts/calls), vote with 2 one-word options + joke subtitles, losing option returns.
- Length 1:30-1:55 is fine for this format (the gags reset attention every few seconds).
- Own character, own premise, own deadline event, own gags; our visual style (not the reference's chubby cartoon).
- Produce episode N+1 within ~24 h of episode N (vote window ~20 h): the pipeline must be templated (scenes,
  HUD, phone screen, vote card) so one episode = writing + one render.

## Owner's direction (2026-11-26): a dating-app premise ("a super hot girl's profile", modern setting)
Claude's proposal (to confirm) - made different enough from the reference (no reunion, no lie about looks, no glow-up meter):
- **"Day 1 of 30: Kevin matched with HER."** Kevin swipes right on everyone (thousands of swipes, zero matches).
  One night: a match. Mia, impossibly perfect profile. Her bio = a list of 10 requirements (cooks, dances, owns a car,
  has a dog, can swim, reads books, has a real job, ...). She texts: "I'm abroad for 30 days. Tick all 10 and we have a
  date the day I land."
- HUD: `DAYS LEFT 30` + `MIA'S LIST 0/10` (a checklist instead of a %, every tick = visible progress).
- Vote = which item from HER list Kevin attacks next; the losing item returns escalated.
- Recurring beats: Mia's texts/travel selfies ("progress?"); a rival match; Kevin's over-confidence (he is a
  confident try-hard, not a passive slob - our own character comedy).
- Long-term mystery: Mia's photos are a bit TOO perfect - is she even real? (comment theories = engagement; payoff late).
- Fictional app name and logo (never the real Tinder name/logo/UI in the video); titles say "dating app".
- Tasteful: Mia is attractive in a cartoon way, nothing sexualised.
