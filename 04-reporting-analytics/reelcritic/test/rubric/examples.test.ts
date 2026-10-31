import { describe, expect, it } from "vitest";
import { EXAMPLE_KINDS, FAILURE_MODES, loadExamples, renderLibraryMarkdown, selectExamples } from "../../src/rubric/examples.js";
import { buildReelPacket, buildRows } from "../../src/metrics/packet.js";
import { loadFixture } from "../../src/ingest/fixture.js";
import { ProfileSchema } from "../../src/rubric/profile.js";
import fs from "node:fs";
const testProfile = () => ProfileSchema.parse(JSON.parse(fs.readFileSync(new URL("../fixtures/test-profile.json", import.meta.url), "utf8")));

describe("example library", () => {
  it("loads, validates, has unique ids across all four kinds", () => {
    const all = loadExamples();
    expect(all.length).toBeGreaterThanOrEqual(16);
    const kinds = new Set(all.map((e) => e.id.split(".")[0]));
    expect(kinds).toEqual(new Set(["hook", "caption", "text", "comment"]));
    expect(EXAMPLE_KINDS).toHaveLength(4);
    for (const e of all) for (const f of e.when.failure_modes) expect(FAILURE_MODES).toContain(f);
  });
  it("selects by failure mode first, then band and value type", () => {
    const picks = selectExamples(["weak_hook", "cliff"], "15-30", "entertaining");
    expect(picks[0]!.id).toMatch(/^(hook|text)\./);
    expect(picks.every((e) => e.when.failure_modes.some((f) => f === "weak_hook" || f === "cliff") || e.when.length_bands.includes("15-30"))).toBe(true);
    expect(selectExamples([], "unknown", null)).toHaveLength(0);
  });
  it("renders deterministic markdown containing every id", () => {
    const md = renderLibraryMarkdown();
    expect(md).toBe(renderLibraryMarkdown());
    for (const e of loadExamples()) expect(md).toContain(e.id);
  });
  it("packet derives failure modes and suggested patterns from the fixture", () => {
    const ds = loadFixture();
    const profile = testProfile();
    const rows = buildRows(ds, profile);
    const r02 = buildReelPacket(ds.reels.find((r) => r.id === "r02")!, ds, profile, rows);
    expect(r02.failure_modes).toEqual(expect.arrayContaining(["hashtag_stuffing", "engagement_bait"]));
    expect(r02.suggested_pattern_ids.length).toBeGreaterThan(0);
    const r18 = buildReelPacket(ds.reels.find((r) => r.id === "r18")!, ds, profile, rows);
    expect(r18.failure_modes).toEqual(expect.arrayContaining(["cliff", "weak_hook"]));
    expect(r18.suggested_pattern_ids.some((id) => id.startsWith("hook.") || id.startsWith("text."))).toBe(true);
    expect(r18.suggested_pattern_ids).toContain("text.frame0_premise_block");
    const r08 = buildReelPacket(ds.reels.find((r) => r.id === "r08")!, ds, profile, rows);
    expect(r08.failure_modes).toContain("commercial_signal");
    expect(r08.failure_modes).toContain("hostile_comments");
  });
});
