import type { Reel } from "../ingest/types.js";

export type HardRuleId =
  | "hashtags_gt_5"
  | "length_gt_3min"
  | "engagement_bait"
  | "other_platform_watermark"
  | "majority_text"
  | "low_res"
  | "bordered"
  | "muted"
  | "repost_originality";

export interface HardRuleHit {
  rule: HardRuleId;
  evidence: string;
  source: "caption" | "user_flag" | "duration" | "history";
  /** Primary source for the rule, for the report footnote. */
  citation: string;
}

export const HARD_RULE_CITATIONS: Record<HardRuleId, string> = {
  hashtags_gt_5: "Instagram @Creators, Dec 19 2025: up to 5 targeted hashtags improves performance",
  length_gt_3min: "Mosseri (Threads, late 2024): Reels up to 3 min; non-follower recommendation reach effectively capped at ~3 min",
  engagement_bait: "Instagram Recommendation Guidelines: clickbait / engagement bait / giveaways are deprioritized",
  other_platform_watermark: "Instagram Ranking Explained (2021/2023) + Mosseri Oct 23 2024: other-platform watermarks are not recommended; own logo is fine",
  majority_text: "Instagram Ranking Explained (2021/2023): majority-text Reels are not recommended",
  low_res: "Instagram Ranking Explained (2021/2023): low-resolution Reels are not recommended",
  bordered: "Instagram Ranking Explained (2021/2023): bordered Reels are not recommended",
  muted: "Instagram Ranking Explained (2021/2023): muted Reels are not recommended",
  repost_originality: "Instagram originality policy, Apr 30 2026: 10+ unmodified reposts in 30 days -> account not recommendable",
};

export const ENGAGEMENT_BAIT_PHRASES = [
  "tag a friend",
  "tag someone",
  "comment yes",
  "comment \"yes\"",
  "like if",
  "like for part",
  "follow for part",
  "share this with",
  "double tap if",
  "type yes",
  "drop a ",
  "giveaway",
  "like and share to win",
];

/** Count hashtags in a caption; ignores '#' inside URLs. */
export function countHashtags(caption: string): number {
  const noUrls = caption.replace(/https?:\/\/\S+/gi, " ");
  const matches = noUrls.match(/(^|\s)#[\p{L}\p{N}_]+/gu);
  return matches ? matches.length : 0;
}

export function findEngagementBait(caption: string): string | null {
  const lc = caption.toLowerCase();
  for (const phrase of ENGAGEMENT_BAIT_PHRASES) {
    if (lc.includes(phrase)) return phrase;
  }
  return null;
}

const WATERMARK_KEYWORDS = ["tiktok.com", "@tiktok", "capcut template", "#capcut", "#tiktok"];

export function countRecentReposts(reel: Reel, history: Reel[], windowDays = 30): number {
  const t = Date.parse(reel.timestamp);
  const lo = t - windowDays * 86_400_000;
  return history.filter((r) => {
    const rt = Date.parse(r.timestamp);
    return r.flags?.repost === true && rt <= t && rt >= lo;
  }).length;
}

export function checkHardRules(reel: Reel, history: Reel[]): HardRuleHit[] {
  const hits: HardRuleHit[] = [];
  const cap = reel.caption ?? "";
  const cite = (rule: HardRuleId) => HARD_RULE_CITATIONS[rule];

  const n = countHashtags(cap);
  if (n > 5) hits.push({ rule: "hashtags_gt_5", evidence: `${n} hashtags in caption`, source: "caption", citation: cite("hashtags_gt_5") });

  if (reel.duration_s != null && reel.duration_s > 180)
    hits.push({ rule: "length_gt_3min", evidence: `duration ${reel.duration_s}s > 180s`, source: "duration", citation: cite("length_gt_3min") });

  const bait = findEngagementBait(cap);
  if (bait) hits.push({ rule: "engagement_bait", evidence: `caption contains "${bait}"`, source: "caption", citation: cite("engagement_bait") });

  const f = reel.flags ?? {};
  const lc = cap.toLowerCase();
  const wmKeyword = WATERMARK_KEYWORDS.find((k) => lc.includes(k));
  if (f.other_platform_watermark) hits.push({ rule: "other_platform_watermark", evidence: "user flag", source: "user_flag", citation: cite("other_platform_watermark") });
  else if (wmKeyword) hits.push({ rule: "other_platform_watermark", evidence: `caption mentions "${wmKeyword}"`, source: "caption", citation: cite("other_platform_watermark") });

  if (f.majority_text) hits.push({ rule: "majority_text", evidence: "user flag", source: "user_flag", citation: cite("majority_text") });
  if (f.low_res) hits.push({ rule: "low_res", evidence: "user flag", source: "user_flag", citation: cite("low_res") });
  if (f.bordered) hits.push({ rule: "bordered", evidence: "user flag", source: "user_flag", citation: cite("bordered") });
  if (f.muted) hits.push({ rule: "muted", evidence: "user flag", source: "user_flag", citation: cite("muted") });

  if (f.repost) {
    const recent = countRecentReposts(reel, history);
    hits.push({
      rule: "repost_originality",
      evidence: recent >= 10 ? `flagged repost; ${recent} reposts in trailing 30 days (>=10: account not recommendable)` : `flagged repost; ${recent} in trailing 30 days`,
      source: "history",
      citation: cite("repost_originality"),
    });
  }
  return hits;
}
