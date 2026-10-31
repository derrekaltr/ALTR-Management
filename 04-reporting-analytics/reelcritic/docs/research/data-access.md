---
title: "Instagram Reels analytics: what data is actually obtainable"
date: 2026-08-25
status: partial   # verified against Meta docs where noted; flagged items unverified
informs: [src/ingest/graph-api.ts, src/ingest/screenshot-vision.ts, src/ingest/business-suite.ts, src/metrics/packet.ts]
---

## Summary

- The **Graph API** (or the newer "Instagram API with Instagram Login") is the richest structured source for per-Reel data: `views`, `reach`, `likes`, `comments`, `shares`, `saved`, `reposts`, `total_interactions`, `profile_visits`, `profile_activity`, and `ig_reels_avg_watch_time` are all live as of 2026-08-25.
- `views` fully replaced `plays` and `impressions` on **April 21, 2025**. It counts every play/replay start with **no minimum watch-time threshold**; the 3-second window only applied to the deprecated `video_views` and still applies to the separate `reels_skip_rate` metric.
- Two important fields, `reels_skip_rate` and `ig_reels_video_view_total_time`, are marked **"in development"** in Meta's own reference docs even though vendor guides list them as generally available. Treat them as best-effort until confirmed.
- The **retention curve** (added in-app Aug 24, 2025), **views by source**, **Trial Reels results**, standalone **replay counts**, and (very likely) the **per-Reel follower/non-follower split** are **in-app exclusives** with no confirmed API field. The only capture route is creator screenshots plus vision extraction.
- A creator pulling insights for their **own** account can run a self-owned Meta app in **Development Mode** indefinitely without App Review; rate limits (~200 calls/hour per account) are generous for that use case.
- **Meta Business Suite** offers an official **CSV/XLS** content-level export (column schema unverified); the **Edits** app and native "Export Insights" only produce **image/PDF** snapshots; the **Download Your Information** export contains no per-Reel metrics.
- Scraping is useless for private Insights data (retention, skip, source) and carries ToS/ban risk when logged in; public-data scraping is legally tolerated per *Meta v. Bright Data* but yields only public counts.
- Video duration is **not** an API field and must be derived from the media file, user input, or a screenshot.

## Findings

### 1. Instagram Graph API / Instagram API with Instagram Login — Reels Insights Metrics

#### Media-level (per-Reel) metrics

| Metric name | API field | Status (2026) | Notes |
|---|---|---|---|
| Views | `views` | Live, GA | Replaced both `plays` and `impressions` for media created ≥ Jul 2, 2024. Full cutover completed **April 21, 2025** after a 90-day notice given Jan 8, 2025. Counts every time the reel "starts to play or replay" — **no minimum watch-time threshold**. [Meta docs](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/), [Zoomph](https://help.zoomph.com/instagram-metric-deprecation-views-transition-april-2025), [Emplifi](https://docs.emplifi.io/platform/latest/home/instagram-insights-metrics-deprecation-april-2025) |
| Plays (legacy) | `plays` | **Deprecated** Apr 21, 2025 | Superseded by `views`. |
| Impressions | `impressions` | **Deprecated** — errors for media created on/after Jul 2, 2024; fully removed for all media Apr 21, 2025 | [Graph API v22.0 changelog](https://developers.facebook.com/docs/graph-api/changelog/version22.0/) |
| Reach | `reach` | Live | Unique accounts that saw the media. |
| Likes | `likes` | Live | |
| Comments | `comments` | Live | |
| Shares | `shares` | Live | |
| Saved | `saved` | Live | |
| Reposts | `reposts` | Live (newer field) | Count of reposts minus deletions. |
| Total interactions | `total_interactions` | Live | Sum of likes+comments+shares+saves. |
| Profile activity | `profile_activity` | Live | Supports `action_type` breakdown (bio link taps, etc.) |
| Profile visits | `profile_visits` | Live | |
| Avg watch time | `ig_reels_avg_watch_time` | Live, Reels-only | Returned in **milliseconds**; watch time ÷ initial views. [getphyllo](https://www.getphyllo.com/post/real-time-reels-analytics-using-instagram-reels-api-iv) |
| Total watch time | `ig_reels_video_view_total_time` | **Marked "in development"** by Meta's own docs | Total cumulative watch time incl. replays. Treat as beta/limited-availability — flag for re-verification. |
| Skip rate | `reels_skip_rate` | **Marked "in development" / estimated** in Meta's own docs, though several third-party vendor guides list it as generally available | Definition: % of views where viewer skipped within first 3 seconds. **This is the one place a 3-second window still matters** even though `views` itself has no such threshold. |
| Cross-posted views | `crossposted_views`, `facebook_views` | Live | For Reels cross-posted to Facebook. |
| Total views/likes/comments (cross-surface) | `total_views`, `total_likes`, `total_comments` | Live, requires Facebook Login product | Aggregates IG + FB + boosted placements. |

Source: direct fetch of [Meta's Instagram Media Insights reference doc](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/), 2026-08-25.

**Not available via API at all (as far as could be verified):** replays as a distinct count, "views by source" (Reels tab/Explore/Home/Profile/Audio page breakdown), a per-second retention curve, and Trial Reels-specific insight fields.

#### Account-level metrics

| Metric | Field | Notes |
|---|---|---|
| Accounts engaged | `accounts_engaged` | |
| Reach | `reach` | Supports `media_product_type` breakdown (AD/STORY/REEL/CAROUSEL_CONTAINER/POST) |
| Views | `views` | Supports **`follow_type` breakdown: FOLLOWER / NON_FOLLOWER / UNKNOWN** — the one place a followers-vs-non-followers split is officially documented as an API breakdown, at the **account** level (not confirmed at individual-media level — flagged as unverified). |
| Follower demographics | `follower_demographics` | Age, city, country, gender. Requires ≥100 followers. Privacy-limited to top 45 segments; up to 48h reporting delay. |
| Engaged audience demographics | `engaged_audience_demographics` | |
| Follows/unfollows | `follows_and_unfollows` | Supports `follow_type` breakdown. |
| Profile links taps | `profile_links_taps` | |
| Deprecated (Jan 8 & Apr 21, 2025) | `impressions`, `email_contacts`, `phone_call_clicks`, `text_message_clicks`, `get_directions_clicks`, `website_clicks`, `profile_views` | Replaced by `views`, `reach`, `follower_count`, `reposts` |

Source: [Meta Instagram User Insights reference](https://developers.facebook.com/docs/instagram-platform/api-reference/instagram-user/insights/), fetched 2026-08-25.

**"Online followers" metric:** No current documentation found confirming this still exists in the Graph API for 2025-2026; treat as **unverified/likely removed**.

#### Access requirements

- **Permissions:** `instagram_basic`, `instagram_manage_insights` (App Review required for insights beyond your own linked account), `instagram_content_publish` for posting. `business_management` is needed only if managing accounts via a Business Portfolio you don't personally own. [Chatwoot dev docs](https://developers.chatwoot.com/self-hosted/instagram-app-review), [Meta Insights docs](https://developers.facebook.com/docs/instagram-platform/insights/)
- **Self-serve without App Review:** **Confirmed viable.** If a creator only wants to pull insights for their *own* account, they can create a Meta developer app, add themselves as an "Instagram Tester" role, and the app stays in **Development Mode** indefinitely — App Review is only triggered when the app needs to access accounts the developer doesn't own/manage (Standard Access is the default; Advanced Access requires App Review + Business Verification). [singhamandeep.com](https://singhamandeep.com/instagram-api-advanced-access-approval/), [Outstand docs](https://www.outstand.so/docs/configurations/instagram)
- **Account type requirement:** Must be a Professional (Business or Creator) account linked to a Facebook Page; personal accounts are not supported by the Graph API. (A newer "Instagram API with Instagram Login" path exists that does not require a Facebook Page and uses `instagram_business_manage_insights`.)
- **Rate limits:** ~**200 API calls/hour per Instagram Business account** under the Business Use Case model (rolling 60-minute window; failed calls still count); Meta's overview page phrases it as 4,800 × account impressions per 24h. For a single creator's own account this is generous. [Meta Graph API rate limiting docs](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/), [getphyllo](https://www.getphyllo.com/post/instagram-api-rate-limits-explained----and-how-to-scale-beyond-them-2026)
- **Data retention:** ~90 days for user-level metrics (Meta insights guide), ~2 years for media-level metrics (per third-party synthesis; not independently confirmed — conflict flagged).
- **Minimum audience thresholds:** demographic data requires ≥100 followers; some metrics unavailable under 100 followers. Skip rate returns null below an unpublished minimum-view threshold ([Storrito](https://storrito.com/resources/how-instagrams-updated-marketing-api-metrics-work/)).
- **Data delay:** up to 48h.

### 2. In-app-only Reel insights (not in the API)

| Feature | In-app? | In API? | Notes |
|---|---|---|---|
| **Retention chart** (% still watching at each moment) | Yes — added **Aug 24, 2025** | **No** confirmed API field | "The flatter the line, the more engaged." [Social Media Today](https://www.socialmediatoday.com/news/instagram-adds-retention-insights-reels/758464/) |
| **Skip Rate** (% who skip within first 3 sec) | Yes — replaced "View Rate" starting Aug 24, 2025 | Field exists in Meta docs (`reels_skip_rate`) but marked "in development"/estimated — **not confirmed GA** | Contradiction: vendor blogs (getphyllo) list it as fully available; Meta's reference page hedges. Treat API access as **unreliable** until confirmed. |
| **Views by source** (Feed/Reels tab/Explore/Search/Profile/Stories shares) | Yes, in-app | **No** API field found | [inro.social](https://www.inro.social/blog/instagram-reels-insights) |
| **Views from followers vs non-followers** | Yes, in-app (Insights redesign into Overview/Engagement/Audience tabs, April 2026) | Partially — `follow_type` breakdown exists at **account** level; per-media **unverified** | |
| **Avg watch time** | Yes | Yes — `ig_reels_avg_watch_time` | |
| **Watch time (total, incl. replays)** | Yes | Field exists but "in development" | |
| **Replays** (distinct count) | Displayed historically | No standalone API field (legacy "reel replay count" deprecated in v22.0 per one source) | |
| **Trial Reels results** | Yes, in-app only | **No** API access found | |

**Bottom line:** the retention curve, views-by-surface breakdown, and (very likely) the per-reel follower/non-follower split are **in-app exclusives**. Skip rate and total watch time are a gray zone — present as field names, flagged "in development" by Meta.

### 3. Instagram Edits app (launched April 2025)

| Feature | Available in Edits? | Exportable? | Notes / Date |
|---|---|---|---|
| Insights tab (Views, Likes, Comments, Reposts, Saves, Skip Rate) | Yes | — | Update **Jan 12, 2026**: filterable by 7/14/30-day windows. [OnlineMarketing.de](https://onlinemarketing.de/social-media-marketing/instagram-edits-bekommt-insights-tab-update-reels-performance) |
| Per-reel export | Yes | **Yes — image/PDF** for pitches/media kits | Same source |
| Account-level insights export | Yes | **Yes — image or PDF** | Same source |
| Reel comparison tool | Yes | — | New Jan 2026 |
| AI comment summarization | Yes | — | New Jan 2026 |
| Ideas tab / Trending Audio tab | Yes | No | |
| Per-second retention inside Edits | **Not separately confirmed** — appears to surface the same metrics as the main app | — | Original hypothesis not substantiated. |
| "Best time to post" | Referenced in secondary sources; no explicit feature confirmed | — | Unverified. |
| AI "production assistant" | Announced **Jun 11, 2026**, closed test: uses views + retention insights to say "what's working and why" and suggest ideas ([TechCrunch](https://techcrunch.com/2026/06/11/metas-edits-app-is-getting-an-ai-assistant-and-a-desktop-version/), [Social Media Today](https://www.socialmediatoday.com/news/edits-is-getting-a-desktop-version-and-an-ai-production-assistant/822864/)) | — | Strategic risk. |

**Caveat:** Edits' export is an **image or PDF snapshot**, not structured data (no CSV/JSON confirmed) — unsuitable for programmatic ingestion without vision/OCR.

### 4. Meta's AI-driven creator guidance

| Item | Status | Notes |
|---|---|---|
| Meta AI recommendations in Professional Dashboard | Reported present (secondary synthesis: creatorflow.so, improvado.io) | **Not independently confirmed** against a Meta primary source. |
| Trial Reels | Confirmed, evolving | Launched Dec 2024 to test reels with non-followers first; expanded to all public creators with 1,000+ followers by mid-2025; **schedulable Feb 2026**. Meta's data: "40% of creators who try trial reels go on to post more Reels overall, and 80% of that group see increased reach with non-followers." [Social Media Today](https://www.socialmediatoday.com/news/instagram-allows-creators-to-schedule-trial-reels/816549/), [posteverywhere.ai](https://posteverywhere.ai/blog/what-are-instagram-trial-reels) |
| Facebook Creator Studio "AI Creator Assistant" relaunch | Confirmed but **Facebook-focused** | Shut down Jan 2023; relaunched with an AI chatbot for eligible US/Canada/India creators **June 3, 2026**. Unclear if it applies to Instagram. |
| Mosseri's Dec 31, 2025 "year-end memo" | Reported (creatorflow.so) | "The polished, perfect aesthetic is dead"; 2026 weights authenticity/provenance more. **Primary post not located** — reported-but-unconfirmed. |
| "Creator AI" / "AI-generated insights summaries" as a named product | **Not found** | Could not verify existence. |

### 5. Instagram "Download Your Information" (DYI) export

- **Formats:** JSON or HTML (some categories CSV). `instagram.com/dyi`. [Alibaba tech guide](https://lifetips.alibaba.com/tech-efficiency/whats-in-your-instagram-data-dump-and-how-to-get-it), [Zapier](https://zapier.com/blog/download-facebook-twitter-instagram/)
- **Includes:** posts, photos, videos, Stories, Highlights, Reels (the media itself), comments, likes, saved items, search history, DMs, login history.
- **Does NOT include:** per-Reel performance metrics. Confirmed via multiple independent sources.
- **Conclusion:** not a viable ingestion path for analytics.

### 6. Alternative ingestion routes

| Route | What it gives you | Format | Legality/Risk | Notes |
|---|---|---|---|---|
| **Meta Business Suite → Insights → Content → Export Data** | Post/Reel-level performance (reach, engagement, likes, comments, shares, saves, watch time per vendor claims) | **CSV or XLS** | Official, TOS-compliant | Best non-API structured export. Exact column schema not enumerated — live-test to confirm. [Graphed blog](https://www.graphed.com/blog/how-to-export-data-from-meta-business-suite) |
| **Graph API (self app, dev mode)** | Richest structured data | JSON | Official, compliant for own account | Most viable for a real product. |
| **Screenshots of in-app Insights + vision/OCR** | Retention curve, skip rate, views-by-source, follower split — everything API-inaccessible | Image | Compliant (own data) | The **only** way to capture retention curves; fragile to UI changes; the curve is a graphic, not text. |
| **Creator Studio** | Facebook-focused; Instagram largely superseded by Business Suite. Original shut down Jan 2023; 2026 relaunch is an AI assistant | — | — | **Not a reliable route** for Instagram Reels. |
| **Third-party scrapers (public data)** | Public-facing counts only — **not** private Insights | Varies | *Meta v. Bright Data*: Meta's Terms "do not bar logged-off scraping of public data" (Judge Edward Chen; Meta dropped claims Feb 2024). [Courthouse News](https://www.courthousenews.com/federal-judge-rules-against-meta-in-data-scraping-case/), [Zyte](https://www.zyte.com/blog/california-court-meta-ruling/). Logged-in scraping of private Insights is a different posture (ToS/ban risk). | Useless for retention/skip/source data since those aren't public. |
| **In-app native "Export Insights"** | Image/PDF account insights | Image/PDF | Official | Corroborates Edits export. |

### 7. Publicly stated ranking signals (Mosseri, 2025-2026)

| Signal | Weight/role | Source/date |
|---|---|---|
| **Watch time** (total seconds + replay rate) | #1 signal; a 15-sec reel watched 3× can outrank a 60-sec reel watched once | Mosseri Jan 2025, reiterated 2026 |
| **Sends per reach** (DM shares) | ~3-5× the weight of likes for **non-follower** reach (numeric multiplier **unverified**) | [Socialync](https://www.socialync.io/blog/adam-mosseri-shares-instagram-algorithm-2026) |
| **Likes per reach** | Slightly more than shares for **existing follower** reach | Same |
| **Originality** | Original content gets more distribution; accounts with 10+ reposts in 30 days excluded from recommendations (Apr 30, 2026 policy) | dataslayer.ai synthesis — the 40-60% figure is **unverified** |
| **"Views" as primary metric** | Finalized **April 21, 2025** | |
| **3-second view definition** | Resolved: `views` has **no** minimum duration; the 3-s rule applied only to the deprecated `video_views`. [SocialCrawl, Aug 2026 (425-post study)](https://www.socialcrawl.dev/blog/how-instagram-counts-views). Skip rate is a **separate** metric with a 3-s window. |
| **Trial Reels** | Distribution pipeline: non-followers first; surfaced to followers if it performs in 24h. Schedulable Feb 2026. | |
| **Reels length** | 3 min as of Jan 2025; technical ceiling reportedly 15–20 min for some accounts in 2026, but **non-follower recommendation reach effectively capped at ~3 min** ([Inrō](https://www.inro.social/blog/instagram-reels-can-now-be-20-minutes-long-new-time-limit-explained-2025)) | |
| **Authenticity/anti-AI-polish (2026)** | Reported Dec 31, 2025 memo; **primary not located** | |
| **UTIS survey model (Jan 2026)** | Meta ranks Reels partly on survey-reported interest, not just engagement ([Meta](https://about.fb.com/news/2026/01/2026-ai-drives-performance/)) | "Why" explanations may drift. |

## Implications for the tool

1. **Primary path — Graph API via self-owned app in Development Mode** (`src/ingest/graph-api.ts`). No App Review is required for a creator's own account. Pull `views`, `reach`, `likes`, `comments`, `shares`, `saved`, `reposts`, `total_interactions`, `profile_visits`, `ig_reels_avg_watch_time` as guaranteed fields; request `ig_reels_video_view_total_time` and `reels_skip_rate` on a best-effort basis and tolerate errors or nulls (skip rate is null below an unpublished minimum-view threshold). Remember `ig_reels_avg_watch_time` arrives in **milliseconds**. Budget for the ~200 calls/hour per-account rate limit and the up-to-48h data delay. Do not depend on `impressions`, `plays`, `profile_views`, or the other fields deprecated Jan 8 / Apr 21, 2025.
2. **Structured fallback — Business Suite CSV/XLS export** (`src/ingest/business-suite.ts`). Official and TOS-compliant, but the column schema is not enumerated anywhere; the parser must be built against a hands-on sample export and treated as brittle.
3. **Critical gap — retention curve, views-by-source, per-Reel follower split** (`src/ingest/screenshot-vision.ts`). These are in-app exclusives, so the only capture route is creator-supplied screenshots run through vision extraction. The retention chart is a **graphic**, so this needs curve-shape extraction rather than text OCR. This path is manual, creator-in-the-loop, not schedulable, and fragile to UI changes (note the April 2026 Insights redesign into Overview/Engagement/Audience tabs).
4. **Edits exports** (image/PDF, per-Reel and account-level) are a secondary vision target with the same limitations; they surface Views, Likes, Comments, Reposts, Saves and Skip Rate over 7/14/30-day windows.
5. **Avoid scraping.** Public-data scraping is legally tolerated but yields nothing private; logged-in scraping of Insights risks ToS violations and account bans.
6. **Video duration is not an API field.** Derive it by probing the media file, from user input, or from a screenshot. Duration matters because non-follower recommendation reach is effectively capped near ~3 min.
7. **Metric packet design** (`src/metrics/packet.ts`) should follow a tiered architecture: **Tier 1** automated GA metrics; **Tier 2** best-effort "in development" metrics (skip rate, total watch time) with explicit availability flags; **Tier 3** creator-in-the-loop screenshot-derived metrics (retention, source breakdown, follower split); **Tier 4** static ranking-signal rules (watch time first, sends-per-reach for non-follower reach, likes-per-reach for follower reach, originality) with the numeric multipliers marked unverified. Because Meta now ranks partly on UTIS survey-reported interest, any "why" explanations built on these rules should be presented as heuristics that may drift.
8. **Strategic watch item:** Meta's own Edits AI "production assistant" (closed test, Jun 11, 2026) uses views and retention insights to explain "what's working and why" — a direct overlap with this tool's value proposition.

## Open questions / items to re-verify

- GA status of `reels_skip_rate` and `ig_reels_video_view_total_time` (Meta docs say "in development"; vendors say available).
- Whether the `follow_type` breakdown (FOLLOWER / NON_FOLLOWER / UNKNOWN) is accepted on the *media* insights endpoint, or only at account level.
- Continued existence of the "online followers" metric.
- Existence of a named "Creator AI" / "AI-generated insights summaries" product.
- Whether Meta AI recommendations in the Professional Dashboard exist per a Meta primary source.
- Primary-source confirmation of Mosseri's Dec 31, 2025 memo and the 40-60% originality figure; the 3-5× sends-vs-likes multiplier is likewise unverified.
- Exact Business Suite CSV/XLS column schema (live-test).
- Whether the 2026 Facebook Creator Studio AI Assistant (relaunched June 3, 2026) covers Instagram Reels.
- Insights storage window: 90 days (Meta guide) vs 2 years for media-level metrics (third-party).
- Whether Edits exposes per-second retention or a "best time to post" feature.
- Whether `ig_reels_video_view_total_time` and the in-app "Watch time" figure share a definition (both claim to include replays).

## Sources

- https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/
- https://developers.facebook.com/docs/instagram-platform/api-reference/instagram-user/insights/
- https://developers.facebook.com/docs/graph-api/changelog/version22.0/
- https://developers.facebook.com/docs/instagram-platform/insights/
- https://developers.facebook.com/docs/instagram-platform/changelog
- https://developers.facebook.com/docs/instagram-platform/overview/
- https://developers.facebook.com/docs/graph-api/overview/rate-limiting/
- https://help.zoomph.com/instagram-metric-deprecation-views-transition-april-2025
- https://docs.emplifi.io/platform/latest/home/instagram-insights-metrics-deprecation-april-2025
- https://docs.emplifi.io/platform/latest/home/instagram-media-and-profile-insights-metrics-depre
- https://social-media-management-help.brandwatch.com/en/articles/12767947-deprecation-of-instagram-impressions-plays-and-video-views
- https://www.socialcrawl.dev/blog/how-instagram-counts-views
- https://www.socialmediatoday.com/news/instagram-adds-retention-insights-reels/758464/
- https://www.babbleboxx.com/post/instagram-adds-reels-retention-skip-rate-what-influencer-marketers-should-do-next
- https://www.inro.social/blog/instagram-reels-insights
- https://www.inro.social/blog/instagram-insights-update-2025
- https://onlinemarketing.de/social-media-marketing/instagram-edits-bekommt-insights-tab-update-reels-performance
- https://creators.instagram.com/blog/edits-video-creation-app
- https://metricool.com/instagram-edits/
- https://techcrunch.com/2026/06/11/metas-edits-app-is-getting-an-ai-assistant-and-a-desktop-version/
- https://www.socialmediatoday.com/news/edits-is-getting-a-desktop-version-and-an-ai-production-assistant/822864/
- https://www.socialmediatoday.com/news/instagram-allows-creators-to-schedule-trial-reels/816549/
- https://posteverywhere.ai/blog/what-are-instagram-trial-reels
- https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/
- https://about.fb.com/news/2026/01/2026-ai-drives-performance/
- https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers
- https://www.socialync.io/blog/adam-mosseri-shares-instagram-algorithm-2026
- https://www.inro.social/blog/instagram-reels-can-now-be-20-minutes-long-new-time-limit-explained-2025
- https://www.courthousenews.com/federal-judge-rules-against-meta-in-data-scraping-case/
- https://www.zyte.com/blog/california-court-meta-ruling/
- https://www.socialmediatoday.com/news/meta-brings-back-facebook-creator-studio/823716/
- https://singhamandeep.com/instagram-api-advanced-access-approval/
- https://www.outstand.so/docs/configurations/instagram
- https://www.getphyllo.com/post/instagram-api-rate-limits-explained----and-how-to-scale-beyond-them-2026
- https://www.getphyllo.com/post/real-time-reels-analytics-using-instagram-reels-api-iv
- https://www.graphed.com/blog/how-to-export-data-from-meta-business-suite
- https://lifetips.alibaba.com/tech-efficiency/whats-in-your-instagram-data-dump-and-how-to-get-it
- https://zapier.com/blog/download-facebook-twitter-instagram/
- https://storrito.com/resources/how-instagrams-updated-marketing-api-metrics-work/
- https://storrito.com/resources/instagram-api-2026/
- https://developers.chatwoot.com/self-hosted/instagram-app-review
