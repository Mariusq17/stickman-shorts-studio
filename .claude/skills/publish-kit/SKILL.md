---
name: publish-kit
description: Prepare everything needed to post a finished "How It's Built" explainer - YouTube Shorts title, descriptions/captions for YouTube, Instagram and TikTok, and a vertical cover/thumbnail rendered from the video's own scene. Also (re)generates the channel avatar, banner and bios. Use when the owner wants to publish/post a video, asks for titles, descriptions, captions, thumbnails or covers, or after a video is delivered.
---

# Publish kit (titles, descriptions, covers)

Output lives in `publishing/` (committed to git): `channel.md` (bios), `brand/` (avatar, banner),
`<slug>/post.md` + `<slug>/cover.png` per video. Copy the format of an existing `publishing/<slug>/post.md`.
The owner talks Romanian; all posting text is **English** (like the videos).

## 1. Read the video first
Open `stickman_studio/explainer/videos/<slug>.py` (or `elevator.py`): the STEPS texts are the script.
Pull out: the hook question, the 1-2 most surprising facts, every fix term (FIXES tracker), the payoff.
Never invent facts or numbers that are not in the script.

## 2. Title (YouTube Shorts; also the first line on IG/TikTok)
- 40-60 characters, Title Case, no clickbait lies, no emoji, no hashtags.
- Formula options (pick the strongest for the topic):
  - the hidden mechanism: "Why Elevators Almost Never Fall", "How an ATM Knows Two Notes Are Stuck"
  - the paradox from the hook: "Your Card Has No Battery. So How Does It Pay?"
  - the everyday moment: "Why AI Chatbots Type One Word at a Time"
- Must contain the main search keyword (elevator, ATM, contactless card, AI chatbot...).

## 3. Descriptions (the algorithm now leans on descriptive text, not hashtags)
- **YouTube description:** 3-5 plain sentences. Say what we build and list the real component/term names
  in the order they appear (those are the search keywords). No keyword stuffing, no links.
  Then **max 2 hashtags** on the last line: one topic tag (#engineering / #technology / #ai / #science)
  + #howitworks.
- **Instagram / TikTok caption:** line 1 = hook question or surprising fact + 1 emoji that fits the object.
  Lines 2-3 = what we build and the 3-5 coolest fixes in plain words. Last line = the same 2 hashtags.
  Keep under ~300 characters so it is not cut off.
- Tone: curious, dry humour allowed, no "SMASH LIKE", no all-caps sentences.

## 4. Cover / thumbnail (`python -m stickman_studio.explainer.branding cover <slug>`)
- Add an entry to `COVERS` in `stickman_studio/explainer/branding.py`:
  `"<slug>": dict(t=<seconds>, cam=((focus_xyz), zoom) or None, lines=[(text, colour), ...])`.
- Pick `t` at the most visual moment: the main object fully built and recognisable, mechanism visible,
  a mascot reacting, no keyword/pop-up needed (covers render the clean scene only). Use `--preview` of the
  video to choose; `cam` overrides the video camera to frame the object (zoom ~160-360).
- Title lines: 2-3 lines, max ~18 characters each, ALL CAPS, the twist word(s) in YELLOW, the rest white
  (e.g. "THIS CARD HAS" / "NO BATTERY" / "SO HOW DOES IT PAY?"). It is a curiosity gap, not the YT title copied.
- Check the PNG: title readable at phone-grid size, inside the centre 3:4 area (Instagram crops the grid
  to 1080x1440), object not hidden by the title, no text cut at the edges. Fix `t`/`cam` and re-render.
- Instagram: upload `cover.png` as the Reel cover. YouTube Shorts: pick the frame in the app, or
  (preferred) add a 1-frame title card later if the owner wants the cover inside the video.

## 5. Channel brand (only when asked or when the name/handle changes)
`python -m stickman_studio.explainer.branding avatar|banner|all` -> `publishing/brand/`.
Avatar: Peg mascot with hard hat, readable in a small circle. Banner: everything important inside the
1546x423 centre safe area. Bios live in `publishing/channel.md` (IG <= 150 chars, TikTok <= 80 chars).
If the channel name changes, also change the follow card text in `lib/widgets.py` (needs re-render).

## 6. Deliver
Send the cover PNG(s) with SendUserFile, paste title + captions in the reply (ready to copy), commit
`publishing/` + `branding.py`. Mark the video in `ideas/IDEAS.md` as `posted` only when the owner says so.

## Rules learned
- Channel texts (bios, channel description, banner) must stay topic-agnostic: never name specific videos or
  topics there - the channel will cover many more subjects. Topic details belong only in per-video posts.
- Hashtags matter less and less: 2 max, relevant only. Descriptive, concrete text works better.
- Text inside the cover must fit and be readable; same rule as text in videos (see CLAUDE.md).
