import { describe, expect, it } from "vitest";
import { METRIC_KEYS, buildAccountPacket, buildReelPacket, buildRows } from "../../src/metrics/packet.js";
import { loadFixture } from "../../src/ingest/fixture.js";
import { DatasetSchema } from "../../src/ingest/types.js";
import { ProfileSchema } from "../../src/rubric/profile.js";
import fs from "node:fs";
const testProfile = () => ProfileSchema.parse(JSON.parse(fs.readFileSync(new URL("../fixtures/test-profile.json", import.meta.url), "utf8")));

describe("packet", () => {
  const ds = loadFixture();
  const profile = testProfile();
  const rows = buildRows(ds, profile);

  it("fixture validates and has 20 reels", () => {
    expect(DatasetSchema.parse(ds).reels).toHaveLength(20);
  });
  it("every METRIC_KEY is present with value/percentile/n", () => {
    const p = buildReelPacket(ds.reels[0]!, ds, profile, rows);
    for (const k of METRIC_KEYS) {
      expect(p.metrics[k]).toBeDefined();
      expect("value" in p.metrics[k] && "percentile" in p.metrics[k] && "n" in p.metrics[k]).toBe(true);
    }
  });
  it("event-driven reels are excluded from the percentile population", () => {
    const p = buildReelPacket(ds.reels.find((r) => r.id === "r13")!, ds, profile, rows);
    expect(p.niche.event_driven).toBe(true);
    expect(p.metrics.views.n).toBe(19);
    expect(p.metrics.views.percentile).toBe(100); // above every non-event reel
  });
  it("hard rules and curve are attached; data gaps list nulls", () => {
    const r02 = buildReelPacket(ds.reels.find((r) => r.id === "r02")!, ds, profile, rows);
    expect(r02.hard_rules.map((h) => h.rule)).toEqual(expect.arrayContaining(["hashtags_gt_5", "engagement_bait"]));
    const r18 = buildReelPacket(ds.reels.find((r) => r.id === "r18")!, ds, profile, rows);
    expect(r18.curve?.shape).toBe("cliff");
    const r11 = buildReelPacket(ds.reels.find((r) => r.id === "r11")!, ds, profile, rows);
    expect(r11.metrics.hold_rate.value).toBeNull();
    expect(r11.data_gaps.join(" ")).toMatch(/duration_s unknown/);
  });
  it("account packet aggregates", () => {
    const a = buildAccountPacket(ds, profile, rows);
    expect(a.account.n_reels).toBe(20);
    expect(a.account.tier).toBe("5K-10K");
    expect(a.reels[0]!.id).toBe("r13");
    expect(a.top_ids.length).toBeGreaterThan(0);
    expect(a.hard_rule_summary.hashtags_gt_5).toBeGreaterThanOrEqual(2);
    expect(a.niche.event_driven_reel_ids).toContain("r13");
    expect(a.niche.commercial_risk_reel_ids).toContain("r08");
    expect(a.metrics.follow_conversion.value).toBeGreaterThan(0);
    expect(a.aggregates.non_follower_view_share).toBeCloseTo(52000 / 93000, 3);
  });
});
