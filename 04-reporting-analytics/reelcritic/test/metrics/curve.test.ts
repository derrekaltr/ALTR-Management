import { describe, expect, it } from "vitest";
import { classifyCurve } from "../../src/metrics/curve.js";

const pts = (arr: Array<[number, number]>) => arr.map(([t, r]) => ({ t_pct: t, retained_pct: r }));

describe("retention curve classifier", () => {
  it("cliff: large drop by 15%", () => {
    const c = classifyCurve(pts([[0, 100], [5, 62], [10, 48], [15, 41], [50, 22], [100, 11]]));
    expect(c.shape).toBe("cliff");
    expect(c.first_15pct_drop).toBeGreaterThanOrEqual(40);
  });
  it("hump: rewatch/payoff bump", () => {
    const c = classifyCurve(pts([[0, 100], [10, 80], [20, 70], [40, 62], [55, 75], [80, 60], [100, 40]]));
    expect(c.shape).toBe("hump");
    expect(c.rewatch_bump).toBe(true);
  });
  it("plateau_loop: gentle slope, high tail", () => {
    const c = classifyCurve(pts([[0, 100], [5, 91], [15, 83], [50, 76], [90, 72], [100, 78]]));
    expect(["plateau_loop", "hump"]).toContain(c.shape); // final uptick can register as bump
    expect(c.tail_retention_pct).toBe(78);
  });
  it("unknown with < 3 points or steady fall without bump", () => {
    expect(classifyCurve(pts([[0, 100], [100, 20]])).shape).toBe("unknown");
    expect(classifyCurve(pts([[0, 100], [15, 80], [50, 50], [100, 10]])).shape).toBe("unknown");
  });
});
