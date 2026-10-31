import { z } from "zod";

export const InsightsSchema = z.object({
  views: z.number(),
  reach: z.number(),
  likes: z.number(),
  comments: z.number(),
  shares: z.number(),
  saved: z.number(),
  reposts: z.number().default(0),
  total_interactions: z.number(),
  profile_visits: z.number().default(0),
  ig_reels_avg_watch_time_ms: z.number().nullable().default(null),
  reels_skip_rate: z.number().nullable().default(null), // 0..1
  ig_reels_video_view_total_time_ms: z.number().nullable().default(null),
  /** New follows attributed to this Reel — only from Business Suite export ("Follows" column). */
  follows: z.number().nullable().default(null),
});
export type Insights = z.infer<typeof InsightsSchema>;

export const ReelFlagsSchema = z.object({
  other_platform_watermark: z.boolean().optional(),
  bordered: z.boolean().optional(),
  low_res: z.boolean().optional(),
  majority_text: z.boolean().optional(),
  muted: z.boolean().optional(),
  repost: z.boolean().optional(),
});
export type ReelFlags = z.infer<typeof ReelFlagsSchema>;

export const RetentionPointSchema = z.object({
  t_pct: z.number().min(0).max(100),
  retained_pct: z.number().min(0).max(100),
});
export type RetentionPoint = z.infer<typeof RetentionPointSchema>;

/** Output of the screenshot vision extractor (also embeddable in fixtures). */
export const ScreenshotExtractionSchema = z.object({
  screenshot_kind: z.array(
    z.enum(["retention", "views_by_source", "follower_split", "overview", "unknown"]),
  ),
  reel_hint: z.string().nullable(),
  retention_curve: z.array(RetentionPointSchema),
  skip_rate_pct: z.number().min(0).max(100).nullable(),
  views_by_source: z
    .object({
      reels_tab: z.number().nullable(),
      explore: z.number().nullable(),
      home: z.number().nullable(),
      profile: z.number().nullable(),
      other: z.number().nullable(),
    })
    .nullable(),
  follower_split: z
    .object({
      followers_pct: z.number().nullable(),
      non_followers_pct: z.number().nullable(),
    })
    .nullable(),
  overview: z
    .object({
      views: z.number().nullable(),
      reach: z.number().nullable(),
      avg_watch_time_s: z.number().nullable(),
      duration_s: z.number().nullable(),
    })
    .nullable(),
  legibility: z.enum(["clear", "partial", "unreadable"]),
  notes: z.string(),
});
export type ScreenshotExtraction = z.infer<typeof ScreenshotExtractionSchema>;

export const CommentSchema = z.object({ text: z.string(), timestamp: z.string() });

export const ReelSchema = z.object({
  id: z.string(),
  permalink: z.string(),
  timestamp: z.string(), // ISO 8601
  caption: z.string().default(""),
  media_url: z.string().optional(),
  thumbnail_url: z.string().optional(),
  duration_s: z.number().nullable().default(null),
  duration_source: z.enum(["probe", "user", "screenshot", "unknown"]).default("unknown"),
  insights: InsightsSchema,
  screenshot: ScreenshotExtractionSchema.optional(),
  flags: ReelFlagsSchema.optional(),
  comments_sample: z.array(CommentSchema).optional(),
  source: z.enum(["graph-api", "business-suite", "fixture"]),
});
export type Reel = z.infer<typeof ReelSchema>;

export const AccountSchema = z.object({
  ig_user_id: z.string(),
  username: z.string(),
  follower_count: z.number(),
  views_by_follow_type: z
    .object({ follower: z.number(), non_follower: z.number() })
    .optional(),
  follows_and_unfollows: z
    .object({ follows: z.number(), unfollows: z.number(), period_days: z.number() })
    .optional(),
  pulled_at: z.string(),
});
export type Account = z.infer<typeof AccountSchema>;

export const DatasetSchema = z.object({
  account: AccountSchema,
  reels: z.array(ReelSchema),
});
export type Dataset = z.infer<typeof DatasetSchema>;
