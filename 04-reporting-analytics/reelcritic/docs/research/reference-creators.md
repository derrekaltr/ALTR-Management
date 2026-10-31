---
title: "Reference creators: what three accounts the user rates as 'really good' actually do"
date: 2026-08-26
status: partial   # public data only (grid view counts, captions, thumbnails, comments); no private insights; video lengths not readable from the web player
informs: [src/rubric/examples/*.json, src/rubric/examples.ts, src/rubric/system-prompt.ts]
---

## Summary

- Three user-nominated reference accounts were read through a logged-in Chrome session on 2026-08-26: **@tak0bell** (240K followers, comedian), **@kenzinicolee.irl** (28.8K, fitness/lifestyle), **@sarah.h44** (1.4M, aesthetic/lifestyle). Only public signals were captured: view counts on the Reels grid, thumbnail (first-frame) text, captions, audio type, like counts, and the top comments.
- Two of the three run the **same mechanism**: a talking-head skit whose *entire hook is a premise stated as on-screen text on the first frame*, spoken to camera in character, with a **one-line in-character caption**, **no hashtags**, and **original audio**. The comments are the audience quoting the bit back or self-identifying — the content is built to be sent to a specific person ("why'd my boyfriend like this").
- The third (@sarah.h44) is a different format entirely: **no on-screen text, trending audio, two-word captions**, aesthetic/thirst-trap visuals, an international emoji-only comment section, and monetization through a bio link. It has one 48M outlier against a 50K–450K baseline — an outlier-driven account, not a system.
- The one creator who **replies to comments and pins a question** (@kenzinicolee.irl: "Okay but what's worse? Gym crush or work crush??") is the one converting a 28.8K following into 1.6M–1.9M-view Reels — the same premise format as tak0bell, plus a comment seed.
- These observations seed `src/rubric/examples/*.json`. They are described as **mechanisms**, not as "copy this creator"; the tool never tells a user to imitate a named account.

## @tak0bell — 240K followers · comedian · "Not PR trained yet sorry"

**Grid (top 24 Reels, views):** 3.1M, 5.3M, 3.3M (pinned) · 163K, 210K, 126K, 92.9K, 1M, 257K, 381K, 237K, 335K, 460K, 171K, 477K, 180K, 256K, 399K, 341K, 350K, 406K, 200K, 388K, 674K. Median of the non-pinned set ≈ 300K on 240K followers — roughly 1.2× followers per Reel, i.e. consistently reaching beyond the follower base.

**First-frame on-screen text (the hook is the whole premise):**
- "I am your husbands receptionist in 10 years" (3.1M)
- "The first girl you sleep with after losing the love of your life" (5.3M)
- "How your girlfriend starts acting after you decided you're breaking up with her" (3.3M)
- "This is where leaving your cheater boyfriend will get you. Never give up" (163K, walking b-roll, trending song, no caption)
- "What you overhear when your man and you split up for 2 minutes to talk to other people at the function" (210K)
- "Real G's move in silence like lasagna" (126K)
- "Your begging him to share his location. I bugged his car and house. We are not the same." (92.9K)
- "Me sitting down at the club absolutely vibing and couldn't be happier" (1M)
- "POV I'm your girlfriend" (257K)
- "Ofcourse my man can like other girls pictures. At the small price of burning his finger prints off" (381K)
- "The 'emergency' phone call you pick up from your girlfriend at work" (237K)
- "I'm your girlfriend who just went thru your phone but refuses to leave you" (335K)

**Captions:** one line, in character, no hashtags, no CTA — "Can I stay with you all day" (5.3M), "Are you coming next year?😇" (1M+), or **no caption at all** (163K).
**Audio:** original audio on the skits; a trending song on the b-roll walking clip.
**Comments (5.3M Reel, 188K likes):** audience quotes the bit ("Steak is too lobstery… juice is full of butter", 46K likes), self-identifies ("This my type and also not my type simultaneously", 3.5K), and tags partners. **The creator does not reply.** The content itself is the send trigger: "hello why'd my boyfriend like this" (6.6K likes).
**Mechanism:** premise-as-text hook → in-character monologue that escalates one specific, hyper-relatable relationship dynamic → ends on the sharpest line (no outro). Nothing is explained; the viewer supplies the context, which is what makes it sendable.

## @kenzinicolee.irl — 28.8K followers · fitness | lifestyle | alcohol-free · ATX

**Grid (top 24 Reels, views):** 1.6M, 1.9M (pinned), 4,739, 136K, 13.3K, 29.6K, 62.5K, 95.5K, 15.6K, 16.7K, 19.5K, 13.2K, 15.9K, 29.1K, 100K, 12.7K, 49.4K, 27.3K, 16.9K, 71K, 16.8K, 63.6K, 26.6K, 86.7K. Bimodal: most Reels land 13K–100K (0.5–3.5× followers); the two pinned ones did 55–65× followers.

**First-frame on-screen text:**
- "Girls 24/7 for no reason" (1.6M, 95.5K — she reposts the same premise; the repeat did 95.5K)
- "Me to my 🥺 when the 6'5", tatted, tan, gym rat walks into the gym" (1.9M)
- "What happens when a Virgo's intuition is wrong?" (4.7K — a question hook with no relatable image underperformed 400×)
- "'How many times a day do you need to be cracked to keep your attitude in check?'" (136K — a quoted line someone says *to* her)
- "No I would never bite someone's biceps. That's disgusting and unhealthy" (13.3K)
- "When they actually tease instead of going straight to it" (29.6K)
- "Me after spending the weekend with my man going round for round" (62.5K)
- "Bulgarian split squats or RDLs for glute growth?" (15.6K — a genuine fitness question; the audience is not there for that)
- "'You're the only girl I talk to'" (16.7K)
- "Some people think I'm crazy. Others think I'm a b*tch. As long as no one thinks I'm broke I'm good with both." (19.5K)
- "It's 7am on a fkn friday. Get tf up" (13.2K, treadmill POV)

**Captions:** "This is actually embarrassing 😭", "couldn't be me" — one line of in-character deflection. No hashtags.
**Comments:** she **pins her own first comment as a question** — "Okay but what's worse? Gym crush or work crush?? 😩" (71 likes, 14 replies) — and the top reply threads are debates she seeded ("0,0001% of men on the planet are 6'5", 43 replies). She replies inside threads.
**Mechanism:** identical premise-as-text skit format to tak0bell, at 1/8 the audience, plus a **conversation seed** in the pinned comment. The two blockbusters are the two most universal premises; the fitness-specific and astrology-specific ones die.

## @sarah.h44 — 1.4M followers · "Just a girl from Aus" · bio link sarahsworld.vip

**Grid (top 30 Reels, views):** 48M (pinned), 49.3K, 97.9K, 65.1K, 92.9K, 222K, 180K, 180K, 125K, 75.1K, 134K, 118K, 145K, 158K, 195K, 95K, 383K, 141K, 153K, 349K, 114K, 72.9K, 191K, 438K, 123K, 926K, 377K, 894K, 139K, 129K. Median ≈ 140K on 1.4M followers — **0.1× followers per Reel**, i.e. most Reels reach a tenth of the follower base; the account is carried by outliers (48M, 926K, 894K).

**First-frame text:** none. Thumbnails are the creator in outfits/swimwear; one text card ("ANA SW…", a brand shoot).
**Captions:** "Going up⬆️" (48M, 717K likes), "Home time" (49K). Two words, no hashtags.
**Audio:** trending tracks (Cardi B "I Like It" on the 48M) and original audio on the low ones.
**Comments:** emoji strings and "beautiful"/"linda" from a largely non-English male audience; zero creator replies; no conversation.
**Mechanism:** visual-first, audio-trend-timed, aesthetic content whose engagement is likes rather than sends or saves. It works for reach when a clip catches a trend wave and converts through the bio link, but the baseline is weak relative to audience size and the comment section has no community — the opposite of the other two.

## What this changes in the tool

1. The **hook library** leads with the *premise-as-first-frame-text* pattern and its sub-types (POV role, "how X acts when Y", "me when", a quoted line someone says to you, a deadpan absurd claim), each with the observed failure cases (a niche-specific question, an explanation instead of a premise).
2. The **caption library** treats the caption as a second punchline or a one-line in-character deflection — never a summary, never hashtags, and "no caption" is a legitimate option.
3. The **on-screen text library** specifies: one block, 1–3 lines, centred on the face or chest line, present from frame 0, plain white sans with shadow, no animation — the text *is* the hook, so it must be readable on the first frame of a muted autoplay.
4. The **comment library** encodes the *pinned question seed* and the *reply-inside-the-top-thread* pattern, and explicitly excludes engagement-bait phrasings.
5. The critique now cites the pattern ids it drew on (`better_example.patterns_used`), validated against the library so it cannot invent a pattern.

## Limits

Public data only: no watch time, retention, skip rate, or sends are visible, so the "why" for these creators is inferred from views-vs-followers, like counts, and comment behaviour. Video durations could not be read from the web player. All three accounts are in the same broad category (young women, relationship/lifestyle humour or aesthetics); the mechanisms are transferable, the topics are not.
