import type { Reel } from "../ingest/types.js";

export interface Ratios {
  avg_watch_time_s: number | null;
  replay_ratio: number | null; // views / reach (>1 => loops/replays)
  send_rate: number | null; // shares / reach
  save_rate: number | null; // saved / reach
  comment_rate: number | null; // comments / reach
  like_rate: number | null; // likes / reach
  engagement_rate: number | null; // total_interactions / reach
  hold_rate: number | null; // avg_watch_time / duration
  hook_rate: number | null; // 1 - skip_rate
  non_follower_share: number | null; // from screenshot follower split
}

export function safeDiv(num: number | null | undefined, den: number | null | undefined): number | null {
  if (num == null || den == null) return null;
  if (!Number.isFinite(num) || !Number.isFinite(den) || den <= 0) return null;
  return num / den;
}

export function computeRatios(reel: Reel): Ratios {
  const i = reel.insights;
  const avgWatch = i.ig_reels_avg_watch_time_ms == null ? null : i.ig_reels_avg_watch_time_ms / 1000;
  const skip = i.reels_skip_rate;
  const nonFollower = reel.screenshot?.follower_split?.non_followers_pct;
  return {
    avg_watch_time_s: avgWatch,
    replay_ratio: safeDiv(i.views, i.reach),
    send_rate: safeDiv(i.shares, i.reach),
    save_rate: safeDiv(i.saved, i.reach),
    comment_rate: safeDiv(i.comments, i.reach),
    like_rate: safeDiv(i.likes, i.reach),
    engagement_rate: safeDiv(i.total_interactions, i.reach),
    hold_rate: safeDiv(avgWatch, reel.duration_s),
    hook_rate: skip == null ? null : Math.max(0, Math.min(1, 1 - skip)),
    non_follower_share: nonFollower == null ? null : nonFollower / 100,
  };
}
