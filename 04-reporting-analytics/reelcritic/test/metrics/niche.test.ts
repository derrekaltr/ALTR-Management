import { describe, expect, it } from "vitest";
import { annotateReel, commercialRiskMatches, inMonthDayWindow, sentimentCounts } from "../../src/metrics/niche.js";
import { loadFixture } from "../../src/ingest/fixture.js";
import { ProfileSchema } from "../../src/rubric/profile.js";
import fs from "node:fs";
const testProfile = () => ProfileSchema.parse(JSON.parse(fs.readFileSync(new URL("../fixtures/test-profile.json", import.meta.url), "utf8")));

describe("niche annotations", () => {
  const profile = testProfile();
  it("month-day windows wrap the year boundary", () => {
    expect(inMonthDayWindow("12-25", "12-20", "01-10")).toBe(true);
    expect(inMonthDayWindow("01-05", "12-20", "01-10")).toBe(true);
    expect(inMonthDayWindow("06-01", "12-20", "01-10")).toBe(false);
    expect(inMonthDayWindow("08-30", "08-15", "09-15")).toBe(true);
  });
  it("commercial regexes and sentiment lexicon", () => {
    expect(commercialRiskMatches("Link in bio, use code SUMMER10", profile.commercial_risk_patterns).length).toBeGreaterThanOrEqual(2);
    expect(commercialRiskMatches("sunrise at the lake", profile.commercial_risk_patterns)).toEqual([]);
    const s = sentimentCounts([{ text: "So beautiful 😍" }, { text: "influencer energy" }, { text: "which camp?" }], profile.sentiment_lexicon)!;
    expect(s).toMatchObject({ admiring: 1, hostile: 1, neutral: 1, sampled: 3 });
    expect(sentimentCounts([], profile.sentiment_lexicon)).toBeNull();
  });
  it("fixture: r13 is event-driven, r08 is commercial risk, r14 is in season", () => {
    const ds = loadFixture();
    const by = (id: string) => annotateReel(ds.reels.find((r) => r.id === id)!, profile);
    expect(by("r13").event_driven).toBe(true);
    expect(by("r08").commercial_risk.hit).toBe(true);
    expect(by("r08").reminders.length).toBeGreaterThan(0);
    expect(by("r14").in_season).toBe(true);
    expect(by("r01").in_season).toBe(false);
    expect(by("r01").event_driven).toBe(false);
  });
});
