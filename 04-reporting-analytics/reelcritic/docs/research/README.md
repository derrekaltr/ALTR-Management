# Research index (2026-08-25)

Deep market research for an Instagram Reels creator-analytics critique tool, run 2026-08-25 across four parallel web-research passes. Each report keeps every fact, number, date and citation from the raw research, flags what could not be verified, and ends with implications for the tool.

| File | One-line summary | Informs |
|---|---|---|
| [data-access.md](data-access.md) | What Reels data is actually obtainable: Graph API (dev-mode, no App Review) gives views/reach/likes/comments/shares/saves/avg-watch-time; the retention curve, views-by-source and per-Reel follower split are in-app only; Business Suite CSV is the structured fallback; DYI has no metrics; scraping is useless and risky. | `src/ingest/*` |
| [critique-frameworks.md](critique-frameworks.md) | Primary-sourced hard rules (watermark, majority-text, >5 hashtags, originality, engagement bait, ≤3 min), ratio signals whose public thresholds disagree 2–5× (so we score by the creator's own percentile), retention-curve shapes, Hook-Retain-Reward, benchmark tables, and the "describe the mechanism, never copy a creator" rule for better examples. | `src/rubric/*`, `src/metrics/*` |
| [competitor-landscape.md](competitor-landscape.md) | 40+ tools mapped: suites pull API metrics but never critique; upload-only analyzers predict but never see outcomes; Reelyze is the only fusion attempt (solo-founder, unvalidated); Meta's Edits AI assistant (Jun 2026 closed test) is the biggest strategic risk; the open gap is falsifiable, own-history-relative critique with a calibration loop. | positioning, `README.md` |
| [reference-creators.md](reference-creators.md) | What three user-nominated accounts actually do (public data, 2026-08-26): premise-as-first-frame-text skits with one-line in-character captions and no hashtags win at 30K–250K followers; a pinned binary question seeds comments; visual-only trend-timed content has a weak baseline and rare outliers. Seeds the example library. | `src/rubric/examples/*.json`, `src/rubric/examples.ts` |

## Verified-facts snapshot (2026-08-25)

Code comments reference these; re-verify before relying on them in a year.

- `views` replaced `plays`/`impressions` in the Graph API on **2025-04-21**; a view has **no minimum duration**. Skip rate (`reels_skip_rate`) is a separate, 3-second-window metric and is marked "in development" by Meta, as is `ig_reels_video_view_total_time`.
- Own-account insights need **no App Review**: Meta app in Development Mode, creator added as Instagram Tester, `instagram_basic` + `instagram_manage_insights`, Professional account linked to a Facebook Page. ~200 calls/hour.
- The per-Reel **retention chart** (in-app since 2025-08-24), **views by source**, per-Reel **follower/non-follower split** and **Trial Reels** results are not in the API. Only a screenshot → vision path recovers them.
- Video **duration is not an API field**; it must be probed from `media_url`, supplied by the user, or read from a screenshot.
- Instagram suppresses low-res, other-platform-watermarked, muted, bordered and majority-text Reels (Ranking Explained, 2021/2023); ≤5 hashtags (@Creators, 2025-12-19); 10+ unmodified reposts in 30 days makes an account non-recommendable (2026-04-30); engagement bait is deprioritized.
- Socialinsider 2025 (35M posts): average views/Reel ≈ 580 (1–5K followers), 1,000 (5–10K), 2,460 (10–50K), 6,095 (50–100K), 16,035 (100K–1M); Reels ER ≈ 0.5%.
- Public benchmarks for hook/hold/send/save/follow-conversion rates disagree by 2–5× across sources; follow-conversion figures contradict each other by 5–15×. The tool therefore scores ratios by **percentile against the creator's own history** and uses fixed numbers only as labelled soft references.
