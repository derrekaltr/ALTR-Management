import { describe, expect, it } from "vitest";
import { median, percentileOf, percentileRank } from "../../src/metrics/percentiles.js";

describe("percentiles", () => {
  it("mid-rank handles ties", () => {
    expect(percentileRank(5, [1, 2, 5, 5, 9])).toBeCloseTo(60); // (2 + 0.5*2)/5
    expect(percentileRank(10, [1, 2, 3])).toBe(100);
    expect(percentileRank(0, [1, 2, 3])).toBe(0);
  });
  it("returns null with insufficient history or null value", () => {
    expect(percentileOf(3, [1, 2, 3, 4])).toEqual({ percentile: null, n: 4, reason: "insufficient_history" });
    expect(percentileOf(null, [1, 2, 3, 4, 5])).toEqual({ percentile: null, n: 5, reason: "metric_null" });
    expect(percentileOf(3, [1, 2, null, 3, 4, 5]).percentile).toBeCloseTo(50);
  });
  it("median", () => {
    expect(median([])).toBeNull();
    expect(median([3, 1, 2])).toBe(2);
    expect(median([4, 1, 2, 3])).toBe(2.5);
  });
});
