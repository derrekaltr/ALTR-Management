import { describe, expect, it } from "vitest";
import { canonicalizeReelUrl, looksLikeUrl, normalizeHookText } from "../normalize";
import { GenerationResultSchema, ReelAnalysisSchema } from "../llm/types";

describe("normalizeHookText", () => {
  it("folds case, smart quotes, punctuation and whitespace", () => {
    expect(normalizeHookText("My  Toxic Trait? This Outfit on a Tuesday!!")).toBe(
      normalizeHookText("my toxic trait: this outfit on a tuesday"),
    );
    expect(normalizeHookText("“smart quotes” shouldn’t break dedupe")).toBe(
      "smart quotes shouldn't break dedupe",
    );
  });

  it("strips emoji", () => {
    expect(normalizeHookText("main character energy 💅✨")).toBe("main character energy");
  });

  it("returns empty for punctuation-only input", () => {
    expect(normalizeHookText("!!! ???")).toBe("");
  });
});

describe("canonicalizeReelUrl", () => {
  it("strips share tokens and folds /reel/ variants", () => {
    const expected = "https://www.instagram.com/reel/DdX2vemzXMI/";
    expect(canonicalizeReelUrl("https://www.instagram.com/reel/DdX2vemzXMI/?stkn=djk4")).toBe(expected);
    expect(canonicalizeReelUrl("https://www.instagram.com/reels/DdX2vemzXMI//")).toBe(expected);
    expect(canonicalizeReelUrl("https://instagram.com/reel/DdX2vemzXMI")).toBe(expected);
  });

  it("handles /p/ post links", () => {
    expect(canonicalizeReelUrl("https://www.instagram.com/p/DYLdNXYJhxS")).toBe(
      "https://www.instagram.com/reel/DYLdNXYJhxS/",
    );
  });

  it("rejects junk", () => {
    expect(canonicalizeReelUrl("Reel")).toBeNull();
    expect(canonicalizeReelUrl("https://example.com/reel/abc")).toBeNull();
    expect(canonicalizeReelUrl("https://www.instagram.com/some.profile/")).toBeNull();
  });
});

describe("looksLikeUrl", () => {
  it("detects http(s) urls only", () => {
    expect(looksLikeUrl("https://www.instagram.com/reel/x")).toBe(true);
    expect(looksLikeUrl("Reel")).toBe(false);
    expect(looksLikeUrl("POV: hello")).toBe(false);
  });
});

describe("LLM schemas", () => {
  it("rejects malformed generation payloads", () => {
    expect(GenerationResultSchema.safeParse({ candidates: [] }).success).toBe(false);
    expect(GenerationResultSchema.safeParse({ candidates: [{ text: "" }] }).success).toBe(false);
    expect(GenerationResultSchema.safeParse({}).success).toBe(false);
  });

  it("accepts a valid generation payload", () => {
    const result = GenerationResultSchema.safeParse({
      candidates: [{ text: "POV: it worked", category: "goofy", rationale: "riff" }],
    });
    expect(result.success).toBe(true);
  });

  it("validates analysis payloads", () => {
    expect(
      ReelAnalysisSchema.safeParse({
        onScreenHookText: "hi",
        backgroundDescription: "girl in a car, barely moving",
        tags: { setting: "car", outfit: "casual", energy: "still" },
        whyItWorks: "text does the work",
        hookVisibleInFirst3s: true,
      }).success,
    ).toBe(true);
    expect(ReelAnalysisSchema.safeParse({ onScreenHookText: "hi" }).success).toBe(false);
  });
});
