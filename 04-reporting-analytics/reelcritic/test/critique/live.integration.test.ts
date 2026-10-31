import { describe, expect, it } from "vitest";
import { critiqueReel } from "../../src/critique/reel-critique.js";
import { validateReelEvidence } from "../../src/critique/validate-evidence.js";
import { buildReelPacket, buildRows } from "../../src/metrics/packet.js";
import { loadFixture } from "../../src/ingest/fixture.js";
import { ProfileSchema } from "../../src/rubric/profile.js";
import fs from "node:fs";
const testProfile = () => ProfileSchema.parse(JSON.parse(fs.readFileSync(new URL("../fixtures/test-profile.json", import.meta.url), "utf8")));

// Runs only with LIVE=1 and a Claude credential (ANTHROPIC_API_KEY or `ant auth login`).
describe.skipIf(!process.env.LIVE)("live: critiqueReel against Claude", () => {
  it("returns a schema-valid, evidence-consistent critique and hits the prompt cache on the second call", async () => {
    const ds = loadFixture();
    const profile = testProfile();
    const rows = buildRows(ds, profile);
    const packet = buildReelPacket(ds.reels.find((r) => r.id === "r02")!, ds, profile, rows);
    const first = await critiqueReel(packet, profile, { effort: "medium" });
    expect(first.critique.reel_id).toBe("r02");
    expect(first.critique.confidence).toBeGreaterThanOrEqual(0);
    expect(first.critique.confidence).toBeLessThanOrEqual(1);
    expect(first.critique.what_to_change_next.length).toBeGreaterThan(0);
    expect(validateReelEvidence(first.critique, packet).ok || first.validation === "partial").toBe(true);
    const second = await critiqueReel(buildReelPacket(ds.reels.find((r) => r.id === "r03")!, ds, profile, rows), profile, { effort: "medium" });
    expect(second.usage!.cache_read_input_tokens).toBeGreaterThan(0);
  }, 600_000);
});
