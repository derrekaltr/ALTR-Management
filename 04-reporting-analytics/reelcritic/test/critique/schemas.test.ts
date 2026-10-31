import { describe, expect, it } from "vitest";
import { ReelCritiqueSchema, type ReelCritique } from "../../src/critique/schemas.js";
import { proseNumberWarnings, stripInvalidEvidence, validateReelEvidence } from "../../src/critique/validate-evidence.js";
import { buildReelPacket, buildRows } from "../../src/metrics/packet.js";
import { loadFixture } from "../../src/ingest/fixture.js";
import { loadProfile } from "../../src/rubric/profile.js";
import { buildSystemPrompt } from "../../src/rubric/system-prompt.js";
import { METRIC_KEYS } from "../../src/metrics/packet.js";
import { ProfileSchema } from "../../src/rubric/profile.js";
import fs from "node:fs";
const testProfile = () => ProfileSchema.parse(JSON.parse(fs.readFileSync(new URL("../fixtures/test-profile.json", import.meta.url), "utf8")));

const ds = loadFixture();
const profile = testProfile();
const rows = buildRows(ds, profile);
const packet = buildReelPacket(ds.reels.find((r) => r.id === "r02")!, ds, profile, rows);

function goodCritique(): ReelCritique {
  const m = packet.metrics;
  return {
    reel_id: "r02",
    headline: "A 48-second tutorial with a weak open and a bait CTA.",
    value_type: "useful",
    retention_shape: "unknown",
    what_you_are_doing: { summary: "s", points: ["p"], evidence: [{ metric: "send_rate", value: m.send_rate.value!, percentile: m.send_rate.percentile, reading: "low" }] },
    why_it_is_incorrect: { summary: "s", points: ["p"], evidence: [{ metric: "hold_rate", value: m.hold_rate.value!, percentile: m.hold_rate.percentile, reading: "low" }] },
    better_example: { mechanism: "m", hook: "h", structure: ["a"], reward_or_loop: "r", caption: "", on_screen_text: "t", comment_seed: "", patterns_used: ["hook.but_then_curiosity"], expected_metric_shift: [{ metric: "hold_rate", direction: "up", rationale: "x" }] },
    why_it_worked_vs_failed: { worked: [], failed: ["f"], evidence: [{ metric: "views", value: m.views.value!, percentile: m.views.percentile, reading: "r" }] },
    what_to_change_next: [{ priority: 1, change: "drop bait", metric_to_watch: "send_rate", hard_rule: "engagement_bait", pattern_id: "caption.in_character_line" }],
    niche_flags: [],
    confidence: 0.7,
    data_gaps: [],
  };
}

describe("critique schema + evidence validation", () => {
  it("schema parses a valid critique and rejects a missing section", () => {
    expect(ReelCritiqueSchema.safeParse(goodCritique()).success).toBe(true);
    const bad = goodCritique() as Partial<ReelCritique>;
    delete bad.why_it_is_incorrect;
    expect(ReelCritiqueSchema.safeParse(bad).success).toBe(false);
  });
  it("valid evidence passes", () => {
    expect(validateReelEvidence(goodCritique(), packet).ok).toBe(true);
  });
  it("catches wrong value, wrong percentile, null metric, bad hard rule, wrong shape", () => {
    const c = goodCritique();
    c.what_you_are_doing.evidence[0]!.value = 0.5;
    c.why_it_is_incorrect.evidence[0]!.percentile = 99;
    c.why_it_worked_vs_failed.evidence.push({ metric: "non_follower_share", value: 0.5, percentile: null, reading: "x" });
    c.what_to_change_next[0]!.hard_rule = "made_up";
    c.what_to_change_next[0]!.pattern_id = "hook.nope";
    c.better_example.patterns_used.push("text.nope");
    c.retention_shape = "cliff";
    const v = validateReelEvidence(c, packet);
    expect(v.ok).toBe(false);
    expect(v.mismatches.map((m) => m.path)).toEqual(expect.arrayContaining(["what_you_are_doing.evidence[0]", "why_it_is_incorrect.evidence[0]", "why_it_worked_vs_failed.evidence[1]", "what_to_change_next[0].hard_rule", "what_to_change_next[0].pattern_id", "better_example.patterns_used[1]", "retention_shape"]));
    const stripped = stripInvalidEvidence(c, v.mismatches);
    expect(stripped.what_you_are_doing.evidence).toHaveLength(0);
    expect(stripped.why_it_worked_vs_failed.evidence).toHaveLength(1);
    expect(stripped.what_to_change_next[0]!.hard_rule).toBeNull();
    expect(stripped.what_to_change_next[0]!.pattern_id).toBeNull();
    expect(stripped.better_example.patterns_used).toEqual(["hook.but_then_curiosity"]);
  });
  it("prose number warnings flag numbers absent from the packet", () => {
    const w = proseNumberWarnings(`Your send rate is ${(packet.metrics.send_rate.value! * 100).toFixed(1)}% but you need 47% and 12,345 views`, packet.metrics);
    expect(w.join(" ")).toMatch(/47%/);
    expect(w.join(" ")).toMatch(/12,345/);
  });
  it("system prompt is deterministic and names every metric", () => {
    const a = buildSystemPrompt(profile);
    expect(a).toBe(buildSystemPrompt(profile));
    for (const k of METRIC_KEYS) expect(a).toContain(k);
    expect(a).toContain("Niche profile: test-niche");
    expect(buildSystemPrompt(loadProfile("default"))).not.toContain("Niche profile");
  });
});
