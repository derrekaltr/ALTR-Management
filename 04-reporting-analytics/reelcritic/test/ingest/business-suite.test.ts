import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { durationToSeconds, importBusinessSuiteCsv, mapHeaders } from "../../src/ingest/business-suite.js";
import { mergeReels } from "../../src/ingest/store.js";
import type { Reel } from "../../src/ingest/types.js";

describe("business suite import", () => {
  it("maps aliases and reports unmapped headers", () => {
    const { index, unmapped } = mapHeaders(["Post ID", "Publish time", "Post type", "Views", "Reach", "Likes", "Mystery"]);
    expect(index.id).toBe(0);
    expect(index.timestamp).toBe(1);
    expect(index.views).toBe(3);
    expect(unmapped).toEqual(["Mystery"]);
  });
  it("imports reels only and merges by permalink", () => {
    const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "bs-")), "x.csv");
    fs.writeFileSync(f, ["Post ID,Permalink,Publish time,Post type,Description,Views,Reach,Likes,Comments,Shares,Saves,Average watch time,Skip rate", "1,https://ig/reel/A,2025-05-01 10:00,Reel,hello #a,\"1,200\",900,50,4,6,7,8.5,35%", "2,https://ig/p/B,2025-05-02 10:00,Image,static,300,250,10,1,0,0,,", "3,https://ig/reel/C,2025-05-03 10:00,Reel,another,500,400,20,2,1,3,,"].join("\n"));
    const r = importBusinessSuiteCsv(f);
    expect(r.reels).toHaveLength(2);
    expect(r.skipped_rows).toBe(1);
    expect(r.reels[0]!.insights!.views).toBe(1200);
    expect(r.reels[0]!.insights!.ig_reels_avg_watch_time_ms).toBe(8500);
    expect(r.reels[0]!.insights!.reels_skip_rate).toBeCloseTo(0.35);
    const existing: Reel[] = [{ id: "old", permalink: "https://ig/reel/A", timestamp: "2025-05-01T10:00:00.000Z", caption: "", duration_s: 21, duration_source: "user", insights: { views: 1, reach: 1, likes: 0, comments: 0, shares: 0, saved: 0, reposts: 0, total_interactions: 0, profile_visits: 0, ig_reels_avg_watch_time_ms: null, reels_skip_rate: null, ig_reels_video_view_total_time_ms: null }, source: "graph-api" }];
    const merged = mergeReels(existing, r.reels);
    expect(merged).toHaveLength(2);
    const a = merged.find((m) => m.permalink === "https://ig/reel/A")!;
    expect(a.duration_s).toBe(21); // preserved
    expect(a.insights.views).toBe(1200); // updated
  });
  it("parses Business Suite 2026 headers: Viewers, Date published, Media type, Follows, Video average play time", () => {
    const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "bs2-")), "y.csv");
    fs.writeFileSync(f, ["Title,Date published,Media type,Views,Viewers,Interactions,Likes and reactions,Comments,Shares,Saves,Follows,Watch time,Video average play time,Permalink", "hello,2026-08-01 10:00,Reel,\"10,000\",8000,500,400,50,30,20,12,1:23:20,0:07,https://ig/reel/Z"].join("\n"));
    const r = importBusinessSuiteCsv(f);
    expect(r.reels).toHaveLength(1);
    const i = r.reels[0]!.insights!;
    expect(i.reach).toBe(8000);
    expect(i.follows).toBe(12);
    expect(i.ig_reels_avg_watch_time_ms).toBe(7000);
    expect(i.ig_reels_video_view_total_time_ms).toBe(5000 * 1000);
    expect(durationToSeconds("1m 2s")).toBe(62);
    expect(durationToSeconds("12.5")).toBe(12.5);
  });
});
