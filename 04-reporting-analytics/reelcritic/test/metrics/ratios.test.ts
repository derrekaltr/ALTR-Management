import { describe, expect, it } from "vitest";
import { computeRatios, safeDiv } from "../../src/metrics/ratios.js";
import type { Reel } from "../../src/ingest/types.js";

const base: Reel = {
  id: "x", permalink: "p", timestamp: "2025-01-01T00:00:00Z", caption: "", duration_s: 20, duration_source: "user",
  insights: { views: 1500, reach: 1000, likes: 100, comments: 10, shares: 20, saved: 30, reposts: 1, total_interactions: 160, profile_visits: 5, ig_reels_avg_watch_time_ms: 12000, reels_skip_rate: 0.3, ig_reels_video_view_total_time_ms: null },
  source: "fixture",
};

describe("ratios", () => {
  it("computes every ratio", () => {
    const r = computeRatios(base);
    expect(r.replay_ratio).toBeCloseTo(1.5);
    expect(r.send_rate).toBeCloseTo(0.02);
    expect(r.save_rate).toBeCloseTo(0.03);
    expect(r.comment_rate).toBeCloseTo(0.01);
    expect(r.like_rate).toBeCloseTo(0.1);
    expect(r.engagement_rate).toBeCloseTo(0.16);
    expect(r.avg_watch_time_s).toBe(12);
    expect(r.hold_rate).toBeCloseTo(0.6);
    expect(r.hook_rate).toBeCloseTo(0.7);
    expect(r.non_follower_share).toBeNull();
  });
  it("zero reach and unknown duration give null, never Infinity", () => {
    const r = computeRatios({ ...base, duration_s: null, insights: { ...base.insights, reach: 0 } });
    expect(r.replay_ratio).toBeNull();
    expect(r.send_rate).toBeNull();
    expect(r.hold_rate).toBeNull();
    expect(safeDiv(1, 0)).toBeNull();
    expect(safeDiv(null, 5)).toBeNull();
  });
  it("hook_rate null without skip rate; non_follower_share from screenshot", () => {
    const r = computeRatios({ ...base, insights: { ...base.insights, reels_skip_rate: null }, screenshot: { screenshot_kind: ["follower_split"], reel_hint: null, retention_curve: [], skip_rate_pct: null, views_by_source: null, follower_split: { followers_pct: 30, non_followers_pct: 70 }, overview: null, legibility: "clear", notes: "" } });
    expect(r.hook_rate).toBeNull();
    expect(r.non_follower_share).toBeCloseTo(0.7);
  });
});
