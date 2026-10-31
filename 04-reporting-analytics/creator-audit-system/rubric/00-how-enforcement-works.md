# How Instagram Enforcement Actually Works (read this first)

Every audit finding must be tagged with which enforcement layer it trips, because the fix and the urgency differ by layer.

## Layer 1 — Community Standards (removal + strikes)
Content that violates Community Standards gets removed and usually generates a **strike**.
Strikes accumulate into feature limits (can't comment, can't go Live, can't monetize),
account restriction, and eventually disablement. Strikes are visible to the client in
**Settings → Account Status → Removed content**. Old strikes age out, but only if new
ones stop coming.

Key categories for our client base:
- Adult Nudity and Sexual Activity
- Sexual Solicitation (offering/asking for sexual content or services, including
  directing users to paid adult content)
- Bullying and Harassment
- Restricted Goods and Services (pharmaceuticals, drugs — this is where peptides land)

## Layer 2 — Recommendation Guidelines (invisible reach collapse)
Content can be 100% allowed on the platform and still be **non-recommendable**: it will
never be shown in Explore, the Reels tab, suggested posts, or to non-followers. This is
the layer most clients don't understand — nothing gets removed, no notification fires
(except sometimes in Account Status → "What can't be recommended"), reach just dies.

Critical mechanic: **repeated non-recommendable posts make the entire ACCOUNT ineligible
for recommendation.** At that point even fully clean new posts get no non-follower
distribution. This is the "shadowban" clients describe. Recovery requires removing or
archiving the offending content, then sustained clean posting; eligibility is re-evaluated
on a rolling window (roughly 30–90 days of behavior).

Non-recommendable categories relevant to us:
- Sexually suggestive content (no nudity required — see 01)
- Content promoting or depicting regulated products, including pharmaceuticals and
  "wellness" compounds (see 02)
- Content that depicts people being harassed, mocked, or pranked without consent (see 03)
- Health claims / borderline health misinformation
- Engagement bait, watchbait, unoriginal/watermarked content (see 04)

## Layer 3 — Monetization & partnership eligibility
Stricter than both layers above. Any Layer 1 strike history or Layer 2 account-level
ineligibility usually kills bonuses, gifts, subscriptions, and branded-content tools.
Flag this in the report if the client monetizes on-platform.

## Layer 4 — Teen safety / 13+ content ratings (expanded globally April 2026)
Teen accounts now run a movie-style 13+ content rating globally. Beyond the
longstanding hide/no-recommend rules for sexually suggestive content and adult
products, the 2026 expansion also hides or refuses to recommend strong language,
risky stunts, and "potentially harmful behavior" content (e.g., marijuana
paraphernalia) from the entire under-18 audience — and adult-adjacent content is
weighted more harshly in recommendation scoring for everyone. If a client's content
style would not pass a 13+ rating bar, assume its recommendation ceiling is severely
capped regardless of appeals.

## Severity scale used in reports
- **CRITICAL** — likely Community Standards violation; strike/removal risk; act within 24h.
- **HIGH** — clearly non-recommendable; actively dragging the whole account's eligibility.
- **MEDIUM** — borderline; probably fine alone but contributes to account-level pattern.
- **LOW** — hygiene issue; fix opportunistically.

## The one rule for all recommendations
Every fix we recommend must make the content **actually compliant**, not just harder for
the classifier to detect. No algospeak, no misspelling banned terms, no "DM me 🤫"
workarounds, no burner link chains. Evasion tactics convert Layer 2 demotions into
Layer 1 strikes when caught (and they get caught — Meta classifies images, audio,
OCR'd text overlays, and linked destinations, not just captions). Durable reach comes
from content that passes review, not content that dodges it.
