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

### Revision after owner feedback (2026-11-26): the "10-item list" premise was illogical -> replaced
Owner: nobody announces "tick my list and I date you"; she is online, so leaving doesn't matter by itself. Wanted:
they chat, he asks her out, THEN she has to leave, but she keeps texting / posting stories daily so he feels pressure
to become good enough; and it must rest on a LIE that creates tension - "spicy", keeps you on edge.
Proposal v2 - **"He lied on his dating profile"**:
- Kevin's profile is all lies: 6'1", chef, owns a husky, speaks French, runs marathons, drives a sports car.
  Mia matches BECAUSE of the lies. They chat great, he asks her out, she says yes - "but I fly abroad tomorrow for
  a month for work. Day 30, 8 pm, it's a date - and you're cooking for me ;)".
- HUD: `DAYS LEFT 30` + `LIES LEFT 6` + a `SUSPICION` meter (rises when he dodges her questions).
- Daily pressure: her story or text pokes one lie ("send me a pic of your husky!", "say something in French").
- Vote: which lie he turns into truth next (or how he dodges today's test); losing option returns escalated.
- Spicy: a rival who likes every one of her stories; long-term twist: maybe Mia lied too (payoff late).

### v3 (owner 2026-11-26): he asks her out as a JOKE, not expecting a yes; "why would she swipe on him?" must be airtight
Logic chain (proposal):
1. Roommate Dan, sick of Kevin whining, makes him a dating profile as a prank/bet: Kevin's photos run through an
   AI "glow-up" app (jawline, abs) + a bio of lies (chef, owns a husky, fluent French, marathon runner).
2. Overnight: a match with Mia, way out of his league -> she swiped because the profile is literally perfect.
   She writes first: "a chef with a husky? 👀"
3. Kevin is sure it's a bot or Dan's prank -> answers sarcastically: "yes. dinner at mine, I cook, the husky judges
   you. 8 pm?" - expecting nothing.
4. She: "lol ok 😂 I'm a flight attendant, on rotation for a month. Day 30, 8 pm. Don't flake."
   -> she accepts BECAUSE he sounded confident and funny (he didn't care), and a date in 30 days costs her nothing.
5. Kevin realises: she has seen the AI photos and believes every lie. 30 days to make the profile true.
Why the delay is real: flight-attendant rotation -> daily stories from a different city (visual variety) + texts that
test one lie each day. Why he doesn't confess: he's tempted every episode (a possible vote option later).

### Ending (owner idea 2026-11-26, SECRET - never in titles/captions): Mia was Dan all along
Day 30: Kevin, now fully glowed-up, waits at the restaurant -> "Mia" is Dan (AI photos + AI-written texts).
Claude's take: not stupid - a planted twist is the strongest comment/share driver, IF it's fair:
- Plant clues from Day 1 that commenters can spot: Mia and Dan use the same odd emoji/typo; Dan is always on his phone
  when Mia texts; Mia never picks up a video call; her stories have tiny AI glitches (6 fingers, melting background
  sign); Mia "knows" things only Dan saw. Comment theories ("Dan is Mia!!") = engagement every episode.
- Dan's motive turns wholesome: started as a prank, kept going because Kevin finally got off the couch.
- Don't punish the audience that wanted the romance: plant a REAL girl from Day 1-2 (recurring side character, e.g.
  the barista / the girl from the dog shelter who sees his whole journey). Final beat: Dan's jaw drops at the giga-chad
  Kevin, Kevin walks out... and the real girl is there. Twist + happy ending.
- Option: let the audience vote the very last choice (forgive Dan? / ask her out?) to keep the comment engine to the end.

---
# SERIES BIBLE v1 (owner + Claude, 2026-11-26) - supersedes the dating-app drafts above
Working title: **"30 Days to Mia"** (episode titles: "Day N of 30: ..."). Language: English. All twists SECRET.

## Spine (season 1)
- **Kevin**: couch guy, funny, zero confidence. Does NOT know anything below.
- **Dan**, his roommate/best friend, secretly runs **"Mia"**: a small but believable account on a photo app (a few
  older posts, some followers, old comments). Explanation revealed only at the end: it's his cousin's old account
  (she moved abroad / left social media; she's in on it) - or "an old experiment". Mia's texts are written by Dan (with AI).
- **Kevin's own profile is REAL and visibly loser-ish** (few followers, old cringe gaming posts, a blurry selfie).
  That's why it's a WOW that she writes to him. No fake photos of Kevin anywhere.
- **Mia's profile = the wow**: stunning, flight attendant, bio "📍 <our city> | ✈️ + a row of country flags",
  posts from Dubai/Tokyo/Rio; local, so a date is realistic. Why him? "your old comment made me laugh" (Dan's line).
- Day 1: Mia likes an old post of Kevin and DMs him. Kevin, sure it's a bot, answers as a JOKE and invites her out
  ("dinner at mine, I cook, 8 pm? lol"). She says yes - but she's a flight attendant on rotation: "Day 30, 8 pm,
  the terrace at <cafe>. Don't flake." In the chat Kevin also bragged as a joke about things his profile can't show
  (chef, runs, speaks French); she: "a chef? your profile is 90% video games lol. prove it on Day 30" -> pressure.
- Days 2-29: Mia's texts and stories (Dan's training program in disguise: "I love guys who cook", "my ex never ran
  with me") -> Kevin improves one thing per episode; viewers vote WHICH (2 options, losing one returns escalated).
  HUD: `DAYS LEFT` + a visible progress meter (exact meter TBD).
- Clues that Mia = Dan, planted from Day 1 (same odd emoji/typo, Dan always on his phone when Mia writes, she never
  takes video calls, tiny AI glitches in her stories). Comment theories = engagement.
- **The waitress** (name TBD, e.g. Lena): appears early at the cafe Kevin passes daily; new at the job, works extra
  shifts for money (we don't know why yet). She sees his whole transformation; small moments between them.
- **Day 30 finale**: Kevin, now giga-chad, waits on the terrace. "Mia" = Dan. Dan's jaw drops: "look at you, bro".
  Kevin asks how the account was so believable -> the cousin/old-experiment explanation. Then the waitress serves his
  table... she steals his heart -> cliffhanger: "Season 2?" (comments decide).
## Season 2+ (improvised, driven by comments)
- The waitress has her own problems/challenges (why she needs the money). She may turn out to be a villain at some
  point: Kevin loses everything except the mindset he rebuilt in season 1, which gets him out of trouble at the end.
## Rules
- Votes choose the ORDER and the flavour of the improvements + side choices; they never break the spine.
- Fictional app/brand names in the video (no real Instagram/Facebook logos or UI).
- Each episode stands alone (stakes line + recap in the first 10 s) and rewards returning viewers (callbacks, clues).
- Measure every episode (STATS.md): stayed-to-watch, % viewed, comments/1K (the vote!), shares, follows.
  If the numbers are bad after ~5 episodes, compress the remaining days rather than drag.
