import { describe, expect, it } from "vitest";
import { checkHardRules, countHashtags, countRecentReposts, findEngagementBait } from "../../src/metrics/hard-rules.js";
import type { Reel } from "../../src/ingest/types.js";

const mk = (over: Partial<Reel>): Reel => ({
  id: "a", permalink: "p", timestamp: "2025-08-01T00:00:00Z", caption: "", duration_s: 20, duration_source: "user",
  insights: { views: 1, reach: 1, likes: 0, comments: 0, shares: 0, saved: 0, reposts: 0, total_interactions: 0, profile_visits: 0, ig_reels_avg_watch_time_ms: null, reels_skip_rate: null, ig_reels_video_view_total_time_ms: null },
  source: "fixture", ...over,
});

describe("hard rules", () => {
  it("counts hashtags, ignoring '#' inside URLs", () => {
    expect(countHashtags("a #one #two https://x.com/#frag #three")).toBe(3);
    expect(countHashtags("#a#b")).toBe(1);
    expect(countHashtags("no tags")).toBe(0);
  });
  it("detects engagement bait case-insensitively", () => {
    expect(findEngagementBait("Follow For Part 2!")).toBe("follow for part");
    expect(findEngagementBait("just a caption")).toBeNull();
  });
  it("flags >5 hashtags, >3min, bait, watermark keyword, user flags", () => {
    const hits = checkHardRules(mk({ caption: "#1 #2 #3 #4 #5 #6 tag a friend #tiktok", duration_s: 200, flags: { majority_text: true, muted: true } }), []).map((h) => h.rule);
    expect(hits).toEqual(expect.arrayContaining(["hashtags_gt_5", "length_gt_3min", "engagement_bait", "other_platform_watermark", "majority_text", "muted"]));
    expect(checkHardRules(mk({ caption: "#one #two" }), [])).toHaveLength(0);
  });
  it("repost window counts trailing 30 days only", () => {
    const hist = [
      mk({ id: "r1", timestamp: "2025-07-10T00:00:00Z", flags: { repost: true } }),
      mk({ id: "r2", timestamp: "2025-06-01T00:00:00Z", flags: { repost: true } }),
      mk({ id: "r3", timestamp: "2025-07-20T00:00:00Z" }),
    ];
    const me = mk({ id: "me", timestamp: "2025-08-01T00:00:00Z", flags: { repost: true } });
    expect(countRecentReposts(me, [...hist, me])).toBe(2);
    const hit = checkHardRules(me, [...hist, me]).find((h) => h.rule === "repost_originality");
    expect(hit?.evidence).toContain("2 in trailing 30 days");
  });
});
