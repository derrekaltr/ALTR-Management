import { describe, expect, it } from "vitest";
import { renderReport } from "../../src/report/markdown.js";
import type { ReportBundle } from "../../src/report/json.js";
import { buildAccountPacket, buildReelPacket, buildRows } from "../../src/metrics/packet.js";
import { loadFixture } from "../../src/ingest/fixture.js";
import type { CritiqueRecord, ReelCritique } from "../../src/critique/schemas.js";
import { ProfileSchema } from "../../src/rubric/profile.js";
import fs from "node:fs";
const testProfile = () => ProfileSchema.parse(JSON.parse(fs.readFileSync(new URL("../fixtures/test-profile.json", import.meta.url), "utf8")));

describe("markdown report", () => {
  it("renders skeleton without critiques and full sections with one", () => {
    const ds = loadFixture();
    const profile = testProfile();
    const rows = buildRows(ds, profile);
    const packets = ds.reels.map((r) => buildReelPacket(r, ds, profile, rows));
    const p13 = packets.find((p) => p.reel.id === "r13")!;
    const critique: CritiqueRecord<ReelCritique> = {
      critique: {
        reel_id: "r13", headline: "Disaster reach, not craft.", value_type: "entertaining", retention_shape: "unknown",
        what_you_are_doing: { summary: "S1", points: ["P1"], evidence: [{ metric: "views", value: p13.metrics.views.value!, percentile: p13.metrics.views.percentile, reading: "top" }] },
        why_it_is_incorrect: { summary: "S2", points: [], evidence: [] },
        better_example: { mechanism: "M", hook: "H", structure: ["B1", "B2"], reward_or_loop: "L", caption: "cap", on_screen_text: "line1\nline2", comment_seed: "seed?", patterns_used: ["hook.premise_text.role"], expected_metric_shift: [{ metric: "send_rate", direction: "up", rationale: "R" }] },
        why_it_worked_vs_failed: { worked: ["W"], failed: ["F"], evidence: [] },
        what_to_change_next: [{ priority: 2, change: "second", metric_to_watch: "save_rate", hard_rule: null, pattern_id: null }, { priority: 1, change: "first", metric_to_watch: "send_rate", hard_rule: null, pattern_id: "comment.pinned_binary_question" }],
        niche_flags: [{ flag: "event-driven", severity: "warn", reason: "dust storm" }],
        confidence: 0.55, data_gaps: ["no curve"],
      },
      validation: "ok", validation_notes: [], usage: null, model: "claude-opus-5", generated_at: "2025-11-20T00:00:00Z",
    };
    const bundle: ReportBundle = {
      generated_at: "2025-11-20T00:00:00Z", profile: "test-niche", account: ds.account,
      account_packet: buildAccountPacket(ds, profile, rows), account_critique: null,
      reels: packets.map((packet) => ({ packet, critique: packet.reel.id === "r13" ? critique : null })),
    };
    const md = renderReport(bundle);
    expect(md).toContain("# Reels critique — @samplecreator");
    expect(md).toContain("## Hard-rule summary");
    expect(md).toContain("`hashtags_gt_5`");
    expect(md).toContain("EVENT-DRIVEN");
    expect(md).toContain("COMMERCIAL RISK");
    expect(md).toContain("### What you're doing");
    expect(md).toContain("### Why it's incorrect");
    expect(md).toContain("### A better version");
    expect(md).toContain("### Why it worked vs. why it failed");
    expect(md).toContain("### What to change next\n1. first");
    expect(md).toContain("`views = 38,000 (p100)`");
    expect(md).toContain("_No critique generated");
    expect(md).toContain("shape = `cliff`");
    expect(md).toContain("**Failure modes (computed):**");
    expect(md).toContain("`hook.premise_text.role`");
    expect(md).toContain("pattern `comment.pinned_binary_question`");
  });
});
