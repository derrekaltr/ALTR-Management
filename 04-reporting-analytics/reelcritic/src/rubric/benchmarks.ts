/**
 * Socialinsider Instagram Benchmarks (35M posts, 447,613 profiles, Jan–Dec 2025; report labelled 2026).
 * https://www.socialinsider.io/social-media-benchmarks/instagram
 * Reference only: the creator's own percentile is the scored signal.
 */
export interface FollowerTier {
  key: string;
  min: number;
  max: number; // exclusive
  avg_views_per_reel: number;
  avg_comments_per_reel: number;
  avg_saves_per_reel: number;
}

export const FOLLOWER_TIERS: FollowerTier[] = [
  { key: "<1K", min: 0, max: 1_000, avg_views_per_reel: 300, avg_comments_per_reel: 1, avg_saves_per_reel: 0 }, // extrapolated, not in source
  { key: "1K-5K", min: 1_000, max: 5_000, avg_views_per_reel: 580, avg_comments_per_reel: 3, avg_saves_per_reel: 1 },
  { key: "5K-10K", min: 5_000, max: 10_000, avg_views_per_reel: 1_000, avg_comments_per_reel: 6, avg_saves_per_reel: 2 },
  { key: "10K-50K", min: 10_000, max: 50_000, avg_views_per_reel: 2_460, avg_comments_per_reel: 12, avg_saves_per_reel: 7 },
  { key: "50K-100K", min: 50_000, max: 100_000, avg_views_per_reel: 6_095, avg_comments_per_reel: 22, avg_saves_per_reel: 22 },
  { key: "100K-1M", min: 100_000, max: 1_000_000, avg_views_per_reel: 16_035, avg_comments_per_reel: 60, avg_saves_per_reel: 96 },
  { key: "1M+", min: 1_000_000, max: Number.POSITIVE_INFINITY, avg_views_per_reel: 16_035, avg_comments_per_reel: 60, avg_saves_per_reel: 96 }, // source tops out at 100K-1M
];

/** Overall Reels engagement rate (reach-based), Socialinsider 2025: ~0.48–0.52%. */
export const REELS_ER_REFERENCE = 0.005;

export function tierFor(followerCount: number): FollowerTier {
  return FOLLOWER_TIERS.find((t) => followerCount >= t.min && followerCount < t.max) ?? FOLLOWER_TIERS[FOLLOWER_TIERS.length - 1]!;
}

export const BENCHMARK_TABLE_MD = `| Follower tier | Avg views/Reel | Avg comments/Reel | Avg saves/Reel |
|---|---|---|---|
| 1K-5K | 580 | 3 | 1 |
| 5K-10K | 1,000 | 6 | 2 |
| 10K-50K | 2,460 | 12 | 7 |
| 50K-100K | 6,095 | 22 | 22 |
| 100K-1M | 16,035 | 60 | 96 |
Overall Reels engagement rate (reach-based) ≈ 0.5%. Source: Socialinsider, 35M posts, 2025.`;
