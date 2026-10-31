import { describe, expect, it } from "vitest";
import { completionVsBand, lengthBand } from "../../src/metrics/length-band.js";

describe("length band", () => {
  it("boundaries", () => {
    expect(lengthBand(null)).toBe("unknown");
    expect(lengthBand(0)).toBe("unknown");
    expect(lengthBand(7)).toBe("7-15");
    expect(lengthBand(15)).toBe("7-15");
    expect(lengthBand(15.1)).toBe("15-30");
    expect(lengthBand(30)).toBe("15-30");
    expect(lengthBand(60)).toBe("30-60");
    expect(lengthBand(61)).toBe("60+");
    expect(lengthBand(180)).toBe("60+");
    expect(lengthBand(181)).toBe("over-3min");
  });
  it("completion delta vs soft reference", () => {
    expect(completionVsBand(0.8, "7-15")).toBeCloseTo(0.06);
    expect(completionVsBand(null, "7-15")).toBeNull();
    expect(completionVsBand(0.5, "unknown")).toBeNull();
    expect(completionVsBand(0.5, "over-3min")).toBeCloseTo(0.04);
  });
});
