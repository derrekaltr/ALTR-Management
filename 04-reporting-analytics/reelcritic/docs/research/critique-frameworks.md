---
title: "Frameworks and benchmarks for explaining why a Reel worked or failed"
date: 2026-08-25
status: partial   # primary Meta sources verified; many numeric benchmarks are aggregator-sourced and flagged
informs: [src/rubric/system-prompt.ts, src/rubric/benchmarks.ts, src/metrics/hard-rules.ts, src/metrics/ratios.ts, src/metrics/curve.ts]
---

# Frameworks and benchmarks for explaining why a Reel worked or failed

Research date: 2026-08-25. Compiled from a verbatim research pass over Meta/Instagram primary sources, named benchmark reports with disclosed methodology, and on-the-record practitioner frameworks. Numeric claims that could not be traced to a primary source are flagged inline.

## Summary

- The single most load-bearing primary source is Instagram's **Ranking Explained** blog (June 2021, updated May 2023): the top Reels predictions are reshare likelihood, watch-through likelihood, like likelihood, and audio-page visits. Everything else is a dateable but secondary-sourced elaboration.
- Meta has stated, on the record, a short list of things it tries **not** to recommend: low-resolution, watermarked (other platform), muted, bordered, majority-text, and (as of April 2026) unmodified reposted content. These are the only signals solid enough to hard-code.
- Ratio metrics (hook rate, hold rate, completion-by-length, shares/reach, saves/reach, non-follower share) have directionally sound logic but their numeric cutoffs come from aggregators (CreatorHouse, Dash Social, SocialPilot) without disclosed samples. They should be scored as percentiles within a creator's own history, not against fixed thresholds.
- The best-documented benchmark set is Socialinsider's 2025 study (35M posts, 447,613 profiles), which puts overall Reels engagement rate at 0.48–0.52%. Rival IQ's 2025 median across all formats is 0.36%. Aggregator tier-based ER figures (5–6% nano, etc.) do not reconcile with these and should be treated as secondary.
- Three contradictions were found and are preserved verbatim: follow-conversion benchmarks (differ 5–15x), overall Reels ER (0.36% vs 0.48–0.52% vs 1.23%), and hashtags ("don't help" vs "use up to 5").
- A large share of "2026" search results are SEO/AI content-mill sites (dataslayer.ai, socialync.io, creatorflow.so, posteverywhere.ai, aipowereddahlia.com, orangemonke.com, aibrify.com) producing suspiciously precise claims ("3–5x weight," "1.4 ratio," "500K views + 50K shares = viral") with no verifiable primary source. These are flagged **[UNVERIFIED — content-mill]** throughout.
- Practitioner frameworks (Kane's Hook Point, Galloway's Cliff/Hump/Plateau, Hoyos's "but/then," MrBeast's production doc) supply a shared vocabulary for narrative critique but are not measurable; they belong in the LLM's explanatory layer, not the scoring layer.
- Recommended tiering: hard rules (primary-sourced), percentile-scored ratios (creator-relative), and narrative vocabulary (frameworks only).

## Official Meta / Mosseri guidance (quotes, dates, links)

Only claims traceable to Meta/Instagram official channels, named reports with disclosed methodology (Socialinsider, Rival IQ, Emplifi, Metricool, Hootsuite's own experiment), or on-the-record practitioner statements are treated as reasonably solid.

| Date | Source | Quote |
|---|---|---|
| June 8, 2021 (updated May 31, 2023) | [Instagram Ranking Explained](https://about.instagram.com/blog/announcements/instagram-ranking-explained) | "The most important predictions we make are how likely you are to reshare a reel, watch a reel all the way through, like it, and go to the audio page." Ranking inputs in order: (1) your activity — "which reels you've liked, saved, reshared, commented on, and engaged with recently"; (2) history with creator; (3) reel information — "signals about the content within the video such as the audio track or visuals in the video, as well as popularity"; (4) creator information — "popularity signals such as number of followers or level of engagement." |
| June 8, 2021 | [Shedding Light on How Instagram Works](https://about.instagram.com/blog/announcements/shedding-more-light-on-how-instagram-works) | Instagram tries not to recommend "low-resolution or watermarked reels, reels that are muted or contain borders, reels that are majority text, or reels that [focus on political issues]." |
| Dec 10, 2024 | [Meta Newsroom — Trial Reels](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/) | Trial Reels let creators "try out content and see what performs best by sharing reels with people who don't follow you." "40% of creators who try Trial Reels go on to post more Reels — and 80% of those see increased reach with non-followers." |
| ~Late 2024 (Threads, @mosseri) | [Threads.com/@mosseri/DE-efFqyStv](https://www.threads.com/@mosseri/post/DE-efFqyStv) | "We're now supporting reels up to three minutes long on Instagram. We still are focused on short form video over long form, but hopefully this gives creators a bit more room to be creative." |
| Oct 23, 2024 | [Social Media Today — logos](https://www.socialmediatoday.com/news/instagram-clarifies-including-your-own-logo-on-a-reel-is-ok/730852/) | Mosseri: Instagram does **not** penalize content edited in third-party apps (CapCut etc.); including **your own** logo does not hurt reach — but Instagram tries not to recommend Reels carrying **another platform's** watermark. |
| Aug 2024 → Jan 2025 → Apr 21, 2025 | [SocialPilot](https://www.socialpilot.co/instagram-marketing/instagram-views-metrics-changes), [Social Media Today](https://www.socialmediatoday.com/news/instagram-updates-metrics-to-focus-creators-on-views/723645/) | Mosseri: "We want to evolve this so it's easier to understand how your content is doing regardless of the format." "Views" replaced "Plays"/"Impressions" as the primary metric; API switch completed April 21, 2025. |
| Dec 19, 2025 | [Social Media Today — hashtag limit](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/) | Instagram @Creators: "Instagram will gradually update the number of hashtags that you can include in a caption for a reel or post to five. We find that using fewer (up to 5) more targeted hashtags, rather than many generic ones, can improve both your content's performance and people's experience on Instagram." (Earlier Mosseri reportedly said hashtags "do not improve your reach", ~May 2025 — **[secondhand — moderate confidence]**.) |
| ~April 30, 2026 | [Tubefilter](https://www.tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator/), [PetaPixel](https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/), [Planoly](https://www.planoly.com/blog/instagram-updates-its-original-content-policy) | Mosseri: "If most of what you post to Instagram is someone else's content, your account is no longer going to be recommendable." When duplicate content is detected, "we will only recommend the original one." Reposting 10+ pieces of others' unmodified content within 30 days makes an account ineligible for recommendations. Meaningful transformation (commentary, voiceover, unique editing, humor) required; changing playback speed or adding a screenshot credit is explicitly **not** sufficient. Extends a Reels-only rule to the whole platform. **Caveat:** underlying Meta post not directly reached; three converging outlets same week. |
| Jan 2025 (secondary only) | dataslayer.ai, socialync.io **[content-mill]** | Claim that Mosseri named "watch time, likes per reach, and sends per reach" as top three Reels ranking signals. Consistent with the 2021/2023 primary source, but the "3–5x weight for shares vs likes" multiplier is **[UNVERIFIED numeric claim]**. |
| Undated | [Buffer's Threads post](https://www.threads.com/@buffer/post/DadeFZxiT5S/) quoting Instagram's Recommendation Guidelines | "content that users broadly tell us they dislike, including clickbait, engagement bait, or which promotes a contest or giveaway" is deprioritized. |

**Bottom line:** the single most load-bearing primary source is the Instagram Ranking Explained blog (2021, updated 2023). Everything else is a dateable but secondary-sourced elaboration. Treat any specific numeric multiplier as directionally true but numerically unverified.

## Scoring rubric: metric-derived signals

Each signal below is a ratio the tool can compute from Insights/API fields. The **Confidence** column reflects how well the numeric threshold is sourced, not whether the underlying logic is sound. Directional interpretations (e.g., "shares signal worth someone else's time") are well supported by the 2021/2023 primary source; the cutoffs mostly are not.

| Signal | Formula | Threshold / Benchmark | What it implies | Confidence |
|---|---|---|---|---|
| **Hook rate ("3-sec hold")** | 3-sec views ÷ reach | ~50%+ healthy; 70%+ comedy/entertainment; 50-60% education/finance; below ~30-40% = weak hook | Whether the opening 1-3 sec earns the scroll-stop. Tied to Meta's "view rate past 3 seconds"/skip rate. | Medium — bands aggregator-sourced ([CreatorHouse, Apr 30 2026](https://creatorhouse.app/blog/instagram-reel-hook-rate-hold-rate-completion-rate-benchmarks); [Dash Social](https://www.dashsocial.com/blog/instagram-reels-performance-benchmarks)) |
| **Views ÷ Reach ("replay ratio")** | views ÷ reach | ~1.0 = no rewatch; >1.4 cited as "healthy" for sub-30s **[UNVERIFIED exact cutoff]** | >1 = replaying/looping (strong). Near 1 with high reach but low likes = "junk-food reach". | Low-Medium on 1.4; underlying logic sound ([SocialPilot](https://www.socialpilot.co/instagram-marketing/instagram-views-metrics-changes)) |
| **Hold rate** | avg watch time ÷ Reel length | Sub-15s: 50%+; 30s+: 30%+ **[CreatorHouse]** | Completion depth. Low hold + high hook = strong open, weak middle. | Medium |
| **Completion rate by length band** | plays reaching end ÷ total plays | 7-15s: avg 74%, target 65%+; 15-30s: 60%/50%+; 30-60s: 49%/40%+; 60s+: 46%/35%+ | Judge against length-matched band. | Medium — Dash Social + Socialinsider + Metricool, no per-band sample disclosed |
| **Shares ÷ Reach ("send rate")** | shares ÷ reach | 1-2% strong; 3%+ "going viral through DMs" **[UNVERIFIED cutoffs]** | Instagram's clearest "worth someone else's time" signal; weighted more than likes for non-follower distribution. | Low-Medium numeric; High directional |
| **Saves ÷ Reach ("save rate")** | saves ÷ reach | >2% = high-value/reference **[aggregator]** | Utility signal vs entertainment (shares). | Low-Medium |
| **Comments ÷ Reach** | comments ÷ reach | No solid numeric benchmark found | Conversation/debate; caption CTA/question correlates. | Low |
| **Follows ÷ non-follower reach** | new follows ÷ non-follower reach | Conflicting: 1-3% target vs 0.18-0.35% median (10K-100K) | Late-funnel conversion; not per-post in API. | **Low — CONTRADICTION** |
| **Non-follower reach share** | non-follower reach ÷ total reach | ~55% average cited for Reels | High = algorithmic distribution; low = followers-only. | Medium |
| **Engagement rate (reach-based)** | (likes+comments+saves+shares) ÷ reach | ~0.48-3.3% depending on source; nano 5-6%, micro 3-6%, mid 1.5-3%, 500K+ 1-2% | Coarse; decompose into components. | Medium |

### Rubric assembly logic

The signals are read in sequence so each diagnosis narrows the next:

1. **Hook diagnosis** → hook rate vs niche-adjusted band.
2. **Retention shape** → hold rate + completion-by-band → classify as **Cliff** (early drop), **Hump** (mid-payoff, ending weak), or **Plateau-Loop** (views ≫ reach, rewatch).
3. **Distribution** → non-follower share + views/reach → "algorithm pushed it" vs "only followers saw it".
4. **Value-type** → shares high = entertaining/relatable; saves high = useful/reference; comments high = provocative; follows high = conversion.
5. **Anti-pattern check** → watermark, aspect ratio, hashtags >5, resolution, majority-text, repost risk, engagement bait.

## Benchmark tables

### Table 1 — Socialinsider 2025-26 Reels averages by follower tier

Source: [Socialinsider Instagram Benchmarks](https://www.socialinsider.io/social-media-benchmarks/instagram). Methodology: 35M posts, 447,613 profiles, Jan–Dec 2025. This is the only benchmark set in this report with a disclosed sample, and it should serve as the primary anchor.

| Follower tier | Avg comments/Reel | Avg saves/Reel | Avg views/Reel |
|---|---|---|---|
| 1K-5K | 3 | 1 | 580 |
| 5K-10K | 6 | 2 | 1,000 |
| 10K-50K | 12 | 7 | 2,460 |
| 50K-100K | 22 | 22 | 6,095 |
| 100K-1M | 60 | 96 | 16,035 |
| All tiers overall ER | 0.48-0.52% (Reels), vs 0.33% images, 0.50% carousels | | |

### Table 2 — Engagement rate by follower tier (aggregator consensus, no disclosed methodology)

| Tier | ER range |
|---|---|
| Nano (1K-10K) | 5-6% |
| Micro (10K-100K) | 3-6% |
| Mid (100K-500K) | 1.5-3% |
| Macro/Mega (500K+) | 1-2% |

Contradiction: Table 1's raw numbers imply rates that don't match Table 2 — different denominators/populations. Use Table 1 as primary anchor.

### Table 3 — Length-adjusted completion bands

Source: [CreatorHouse synthesis](https://creatorhouse.app/blog/instagram-reel-hook-rate-hold-rate-completion-rate-benchmarks). No per-band sample disclosed.

| Reel length | Avg completion | Healthy target |
|---|---|---|
| 7-15s | 74% | 65%+ |
| 15-30s | 60% | 50%+ |
| 30-60s | 49% | 40%+ |
| 60s+ | 46% | 35%+ |

### Table 4 — Rival IQ 2025

Source: [Rival IQ Social Media Industry Benchmark Report](https://www.rivaliq.com/blog/social-media-industry-benchmark-report/).

| Finding | Value |
|---|---|
| Reels vs static images | Reels generate 2-3× the engagement rate of static images across most industries |
| Overall median ER, all industries/formats (2025) | **0.36%**, down YoY |
| Fashion and Travel | Reels edge out carousels for the 3rd consecutive year |

Metricool 2025→2026: average watch time rose to only 8.5s even as total watch time grew ([press release](https://metricool.com/press-release-instagram-study-2026/)). This is the strongest available argument against padding Reels to 60s+.

## Contradictions

All three preserved verbatim from the research pass.

```
CONTRADICTION 1: Follow-conversion rate benchmark
  Claim A [content-mill]: "1-3% of non-follower reach should convert to follows"
  Claim B [content-mill]: "median follow conversion 0.18-0.35% for 10K-100K accounts"
  Assessment: no disclosed sample; figures differ 5-15x. Neither is ground truth.
  Recommendation: do NOT hard-code. Compute the creator's OWN historical distribution; flag outliers by percentile.
```

```
CONTRADICTION 2: Overall Reels engagement rate
  Socialinsider 2026: 0.48-0.52% | colorlib aggregator: 1.23% | Rival IQ 2025: 0.36% median all formats
  Assessment: different denominators (reach vs views vs impressions) and populations; Socialinsider discloses methodology.
  Recommendation: trust Socialinsider as anchor; treat 1.23% as uncorroborated.
```

```
CONTRADICTION 3: "Hashtags don't help" vs "use exactly 5"
  Claim A: Mosseri reportedly said hashtags "do not improve your reach" (~May 2025, secondhand)
  Claim B: @Creators (Dec 19, 2025): "using fewer (up to 5) more targeted hashtags... can improve both your content's performance and people's experience"
  Assessment: reconcilable — hashtags are not a discovery lever, but >5 generic ones is an active penalty.
  Recommendation: weight the dated on-platform quote; frame as "near-zero upside, real downside above 5".
```

## Failure-mode taxonomy → fixes

Each row pairs a diagnosable failure with its evidence base and the corrective the tool should recommend. Evidence quality varies widely; rows sourced to the 2021 primary source or dated Mosseri statements are strong, rows sourced to aggregators are soft.

| Failure mode | Evidence | Fix |
|---|---|---|
| Weak/absent hook (no pattern interrupt in first 1-3s) | Meta's "view rate past 3 seconds"/skip rate; Jenny Hoyos: "I really do think you have one second to hook someone"; Brendan Kane's Hook Point: "less than three seconds to capture attention"; up to 50% drop-off in first 3s cited | Script the first line word-for-word; open on the payoff, not setup; Hoyos "but/then" curiosity loop in the opening sentence. |
| Static talking head, no visual/audio pattern interrupts | Editing-technique sources: cadence every 3-15s (wide range) | Cuts, zooms, b-roll, text pop-ins; flag a continuous static shot > ~12-15s. |
| Cliff-curve retention | Galloway: Cliff = "opening 2-3 seconds do not earn the swipe"; triggers = intro cards, logo animations, "hey guys", wide establishing shots | Cut preamble; start mid-action; delay branding. |
| No mid-video payoff (flat Hump) | Galloway: Hump "holds above 60% through the middle... signature of a strong mid-piece payoff that produces the highest share rates" | Land a reveal/twist in the middle third. |
| No loop/rewatch design | "A Reel with 40% of viewers watching twice can reach 10x more audience than one with 5% re-watch" [aggregator, unverified multiplier] | Match final frame/line to opening; reverse-effect loops for 7-15s. |
| Watermarked / cross-posted-with-badge | Mosseri Oct 23, 2024; 2021 Ranking Explained | Export clean; never use TikTok's native "Share to Instagram". |
| Recycled/repost content | Mosseri Apr 30, 2026: 10+ unmodified reposts in 30 days = not recommendable | Flag unedited reposts; speed-ramp/credit screenshot insufficient. |
| Majority-text Reels | 2021 primary source | Cap on-screen text; prefer visual demonstration. |
| Low resolution / muted / bordered | 2021 primary source | 1080×1920, native audio, no borders. |
| Wrong aspect ratio | Aggregator A/B claims **[UNVERIFIED mechanism]** | Full 9:16 regardless. |
| Hashtag stuffing (>5) | @Creators Dec 19, 2025 | Cap at 5, specific. |
| Engagement bait | Instagram Recommendation Guidelines via Buffer | Flag "comment YES", "like for part 2", "tag a friend" as penalty risk. |
| Posting cadence collapse | Mosseri: posting more doesn't cost reach; each post ranked independently; 2-4 Reels/week commonly cited [secondary] | Consistent 2-4×/week; frame as momentum, not penalty. |
| Length mismatch (padding to 60s+) | Table 3; Metricool avg watch time 8.5s | If the idea completes in <30s, don't pad; judge vs length band. |
| Trend-audio misuse | Weak evidence — inferred | **[Gap]** soft heuristic only. |

## The "good example" library approach

When the critique points to a comparison Reel, the selection and description rules below keep the example useful, falsifiable, and clear of the April 2026 originality policy.

1. **Match on structural failure mode, not topic/niche.** A Cliff-curve Reel should be shown a Hump or Plateau-Loop mechanism, regardless of subject matter.
2. **Match on length band.** A 60s+ Reel should not be compared to a 7-15s loop; the completion targets differ by roughly 30 points (Table 3).
3. **Describe the mechanism, not the content.** This is coaching, not "copy this creator"; it also sidesteps originality-policy concerns.
4. **Anchor to the specific weak signal.** High hook, low hold → show a mid-video interrupt example, not a better opener.
5. **Explain "why it worked" in the same ratio vocabulary** (views/reach, shares/reach, saves/reach) so the explanation is falsifiable against the creator's own numbers.
6. **Prefer creator-agnostic structural composites over named creators.**

## Practitioner frameworks

These supply vocabulary for narrative critique. None is measurable from Insights data and none should feed a numeric score.

| Framework | Source | Rubric items | Evidence |
|---|---|---|---|
| Hook Point (Disrupt-Engage-Educate) | Brendan Kane, [Hook Point](https://hookpoint.com/hook-point-book/) | Disrupt pattern in <3-5s; engage emotionally; deliver value to earn the next 3s | Thesis/consulting-based |
| Hook-Retain-Reward + retention-curve taxonomy | Paddy Galloway via [Aibrify](https://aibrify.com/blog/youtube-shorts-retention-curve-playbook) | Best Shorts retain 70-90% through first 1-2s; Cliff / Hump / Plateau | Galloway's analysis of Shorts; YouTube-specific but transferable |
| "But/Then" hook + power words | Jenny Hoyos via [Marketing Examined](https://www.marketingexamined.com/blog/jenny-hoyos-short-form-video-playbook) | "but" (problem) + "then" (curiosity loop) inside first sentence; power words; target 90%+ retention | Self-reported single-creator |
| Stop-Hook-Payoff | Colin & Samir / Ernesto Perez, [Playbook](https://www.colinandsamir.com/playbook) | 5 hook principles; 3 levels of scripting | Coaching program |
| MrBeast production doc | [Tubefilter](https://www.tubefilter.com/2024/09/17/mrbeast-internal-production-guide-leaked-key-points/amp/), Aug 2024 | First minute wins retention; front-load; "crazy progression"; "no dull moments" | Internal standard |
| Creator Wheel | Jon Youshaei | Preparation → Production → Monetization; no per-Reel rubric located | **Gap** |
| Pattern interrupts | CapCut, joyspace.ai, edicionvideopro.com | Cadence 3-5s to 10-15s (inconsistent); claimed 20-35% watch-time lift **[UNVERIFIED]** | Soft heuristic only |

Note that the Galloway retention-curve taxonomy is sourced via aibrify.com, which is itself on the content-mill list; the Cliff/Hump/Plateau vocabulary is attributed to Galloway's Shorts analysis, but the specific quoted thresholds ("holds above 60% through the middle") should be treated with the same caution as other aggregator numbers.

## Gaps flagged

1. No primary Meta source for the Jan 2025 "watch time, likes/reach, sends/reach" restatement; only content-mill sites carry it.
2. No publication-grade worked case study with real Insights screenshots. Hootsuite's hashtag experiment (Oct 30, 2023, [link](https://blog.hootsuite.com/experiment-reels-hashtags/)) is n=6, too small.
3. Jon Youshaei per-Reel rubric not located.
4. Trending-audio penalty — no direct Meta statement; the "trend-audio misuse" failure mode is inferred.
5. Follow-conversion ground truth contradictory (Contradiction 1).
6. "3-5×" sends-vs-likes weight untraceable to any primary source.

## How the tool applies this

The evidence quality above maps directly onto three tiers of enforcement. The rule is: only primary-sourced, binary checks become hard rules; anything with an aggregator-sourced numeric cutoff is scored relative to the creator's own history; anything that is a practitioner heuristic stays in the narrative.

### Tier 1 — Hard rules (primary-sourced, binary)

Informs `src/metrics/hard-rules.ts`. Each of these traces to a Meta statement and can be checked deterministically from the media file or caption:

- Other-platform watermark present (2021 primary source; Mosseri Oct 23, 2024)
- Resolution below 1080×1920 (2021 primary source)
- Hashtags > 5 (@Creators Dec 19, 2025)
- Majority-text frame content (2021 primary source)
- Duplicate/repost without meaningful transformation (Mosseri ~Apr 30, 2026; 10+ in 30 days threshold)
- Aspect ratio not 9:16 (mechanism unverified, but the fix is costless)
- Length > 3 minutes (Mosseri, late 2024 Threads post)

Hard rules produce a pass/fail flag with the dated citation attached. They do not contribute to a percentile score.

### Tier 2 — Soft signals (percentile within the creator's own history)

Informs `src/metrics/ratios.ts`, `src/metrics/curve.ts`, and `src/rubric/benchmarks.ts`. These are the ratios from the scoring rubric whose logic is sound but whose published cutoffs are unverified:

- Hook rate (3-sec views ÷ reach)
- Hold rate (avg watch time ÷ length)
- Completion rate, judged against the Table 3 length band
- Shares ÷ reach
- Saves ÷ reach
- Non-follower reach share

For each, the tool computes the creator's own distribution across their Reel history and reports the current Reel's percentile. The published benchmarks (Tables 1–3) are shown as context ("industry reference") but never as the score itself. This directly follows the Contradiction 1 recommendation: do not hard-code, compute the creator's own distribution, flag outliers by percentile. Follow-conversion is excluded from scoring entirely because it is not available per-post in the API and its benchmarks contradict by 5–15x.

### Tier 3 — Narrative vocabulary only

Informs `src/rubric/system-prompt.ts`. These frameworks give the LLM critique a consistent language but have no numeric weight:

- Loop/rewatch design (final frame matches opening)
- Pattern-interrupt cadence (3-15s range; flag static shots > ~12-15s as a suggestion, not a score)
- "But/then" hook construction (Hoyos)
- Retention-curve classification: Cliff / Hump / Plateau-Loop (Galloway), derived from Tier 2 hold and completion data but described qualitatively

The system prompt should require the LLM to (a) name the curve shape, (b) cite the Tier 2 percentile that justifies it, (c) recommend a fix from the failure-mode table, and (d) when offering a "good example," follow the six library rules above so the explanation stays in ratio vocabulary and creator-agnostic.

### Confidence labelling in output

Every benchmark surfaced to the user carries its confidence label from the rubric table (High / Medium / Low-Medium / Low) and, where applicable, the **[UNVERIFIED]** or **[content-mill]** flag. Contradiction 2 means the tool should never display a single "average Reels ER" without stating the denominator and the source (Socialinsider 0.48–0.52% is the anchor).

## Sources

Primary (Meta / Instagram / Mosseri):

- https://about.instagram.com/blog/announcements/instagram-ranking-explained
- https://about.instagram.com/blog/announcements/shedding-more-light-on-how-instagram-works
- https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/
- https://www.threads.com/@mosseri/post/DE-efFqyStv

Reported Meta statements (secondary press):

- https://www.socialmediatoday.com/news/instagram-clarifies-including-your-own-logo-on-a-reel-is-ok/730852/
- https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/
- https://www.socialpilot.co/instagram-marketing/instagram-views-metrics-changes
- https://www.socialmediatoday.com/news/instagram-updates-metrics-to-focus-creators-on-views/723645/
- https://www.tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator/
- https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/
- https://www.planoly.com/blog/instagram-updates-its-original-content-policy
- https://www.threads.com/@buffer/post/DadeFZxiT5S/

Benchmark reports with disclosed or partially disclosed methodology:

- https://www.socialinsider.io/social-media-benchmarks/instagram
- https://www.rivaliq.com/blog/social-media-industry-benchmark-report/
- https://metricool.com/press-release-instagram-study-2026/
- https://blog.hootsuite.com/experiment-reels-hashtags/

Aggregator benchmark syntheses (no disclosed sample):

- https://creatorhouse.app/blog/instagram-reel-hook-rate-hold-rate-completion-rate-benchmarks
- https://www.dashsocial.com/blog/instagram-reels-performance-benchmarks

Practitioner frameworks:

- https://hookpoint.com/hook-point-book/
- https://aibrify.com/blog/youtube-shorts-retention-curve-playbook
- https://www.marketingexamined.com/blog/jenny-hoyos-short-form-video-playbook
- https://www.colinandsamir.com/playbook
- https://www.tubefilter.com/2024/09/17/mrbeast-internal-production-guide-leaked-key-points/amp/

Content-mill sites referenced only to flag unverified claims (not cited as evidence): dataslayer.ai, socialync.io, creatorflow.so, posteverywhere.ai, aipowereddahlia.com, orangemonke.com, aibrify.com, colorlib.

---

*Compiled by the research report generator on 2026-08-25 from a single verbatim research pass. Status is partial: primary Meta sources verified; numeric benchmarks remain aggregator-sourced and flagged pending better data.*
