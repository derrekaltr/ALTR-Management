"""Verification-readiness rubric: review prompts and readiness scoring.

Snapchat's public-profile guidelines require that everything on a public
profile (stories, Spotlight, bio, avatar) be appropriate for a broad audience
aged 13+. Verification ("gold star") review is stricter still: accounts with
sexually suggestive public content, adult-platform promotion, or paid-content
solicitation are routinely declined. This rubric flags anything that even
*hints* at that, so creators can clean up before applying.
"""

from __future__ import annotations

from typing import Any

from .models import CreatorReview, Severity

READINESS_LABELS = {
    "ready": "Ready",
    "nearly_ready": "Nearly ready",
    "needs_cleanup": "Needs cleanup",
    "major_cleanup": "Major cleanup",
}


def weighted_score(review: CreatorReview, scoring: dict[str, Any]) -> int:
    weights = scoring["weights"]
    total = 0
    for item in review.items:
        severity = item.review.severity
        if severity != Severity.CLEAN:
            total += int(weights.get(severity.value, 0))
    return total


def readiness_level(review: CreatorReview, scoring: dict[str, Any]) -> str:
    """Map a creator's flags to a readiness key (see READINESS_LABELS)."""
    if any(i.review.severity == Severity.CRITICAL for i in review.items):
        return "major_cleanup"
    score = weighted_score(review, scoring)
    thresholds = scoring["thresholds"]
    if score <= int(thresholds["ready"]):
        return "ready"
    if score <= int(thresholds["nearly_ready"]):
        return "nearly_ready"
    if score <= int(thresholds["needs_cleanup"]):
        return "needs_cleanup"
    return "major_cleanup"


_RUBRIC_CORE = """\
You are a brand-safety reviewer for ALTR, a talent management agency. ALTR's
creators are applying for Snapchat verification (the "gold star"). Snapchat
declines verification for accounts whose PUBLIC content is sexually suggestive
in any way, promotes adult platforms, or solicits paid adult content. Your job
is to flag anything on a creator's public profile that could jeopardize
verification, so the creator can remove it BEFORE applying. Many of these
creators also run adult platforms elsewhere, so their public Snapchat must be
squeaky clean; when in doubt, flag it (use `borderline: true` for judgment
calls).

Severity scale:
- critical: explicit content or unmistakable adult-platform promotion
  (nudity, implied nudity, direct OnlyFans/Fansly links or mentions, PPV
  menus). Verification is effectively impossible while this is public.
- high: strongly suggestive but not explicit (lingerie/underwear framing,
  overtly sexualized poses, "18+"/"spicy content" language, link hubs that
  lead to adult pages, cash-app/tip solicitation with suggestive framing).
- medium: mildly suggestive or ambiguous (swimwear shots framed to emphasize
  the body, suggestive emoji clusters, flirty captions with innuendo,
  revealing outfits beyond everyday attire).
- low: minor polish issues that reviewers may still hold against the account
  (third-party app watermarks, borderline caption wording, an off-brand
  username/display name that hints at adult content).
- clean: nothing that would concern a verification reviewer.

Categories (choose every one that applies): explicit_nudity, implied_nudity,
revealing_attire, suggestive_pose, suggestive_text, adult_platform_reference,
monetization_solicitation, identity_innuendo, third_party_watermark, other.

For every flagged item write:
- rationale: one or two sentences a creator will understand — what a Snapchat
  verification reviewer would object to. Be direct but professional.
- removal_action: the exact step to take in the Snapchat app, e.g. "Delete
  this Spotlight post: Profile -> Spotlight tab -> open the post -> ⋯ ->
  Delete", "Delete this Story snap: Profile -> My Story -> open the snap ->
  ⋯ -> Delete Snap", or "Edit your bio: Profile -> Edit Profile -> Bio" —
  matched to where the item lives.
For clean items, set rationale to why it is fine and removal_action to "".
"""

IMAGE_REVIEW_SYSTEM = (
    _RUBRIC_CORE
    + """
You will be shown ONE captured image from the creator's public Snapchat
(a profile screenshot, a Story snap, a Spotlight post, or their avatar).
Assess only what is visible. If the image is a full-profile screenshot,
judge the overall impression it gives a reviewer (avatar, imagery, visible
captions) and flag the worst element you can see.
"""
)

TEXT_REVIEW_SYSTEM = (
    _RUBRIC_CORE
    + """
You will be given ONE text field from the creator's public Snapchat profile
(username, display name, or bio). Judge innuendo, adult-platform references,
solicitation language, emoji signaling, and "link in bio"-style pointers that
commonly lead to adult link hubs.
"""
)
