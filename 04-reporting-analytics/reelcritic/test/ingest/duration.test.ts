import { describe, expect, it } from "vitest";
import { probeMp4DurationSeconds, resolveDuration } from "../../src/ingest/duration.js";
import type { Reel } from "../../src/ingest/types.js";

function atom(type: string, payload: Uint8Array): Uint8Array {
  const out = new Uint8Array(8 + payload.length);
  new DataView(out.buffer).setUint32(0, out.length);
  out.set(new TextEncoder().encode(type), 4);
  out.set(payload, 8);
  return out;
}
function mvhdV0(timescale: number, duration: number): Uint8Array {
  const p = new Uint8Array(100);
  const dv = new DataView(p.buffer);
  dv.setUint8(0, 0); // version
  dv.setUint32(12, timescale);
  dv.setUint32(16, duration);
  return atom("mvhd", p);
}
function mvhdV1(timescale: number, duration: bigint): Uint8Array {
  const p = new Uint8Array(112);
  const dv = new DataView(p.buffer);
  dv.setUint8(0, 1);
  dv.setUint32(20, timescale);
  dv.setBigUint64(24, duration);
  return atom("mvhd", p);
}
const concat = (...xs: Uint8Array[]) => {
  const out = new Uint8Array(xs.reduce((s, x) => s + x.length, 0));
  let o = 0;
  for (const x of xs) {
    out.set(x, o);
    o += x.length;
  }
  return out;
};

describe("mp4 duration probe", () => {
  it("parses mvhd v0 inside moov after ftyp", () => {
    const buf = concat(atom("ftyp", new Uint8Array(8)), atom("moov", mvhdV0(1000, 24500)));
    expect(probeMp4DurationSeconds(buf)).toBeCloseTo(24.5);
  });
  it("parses mvhd v1", () => {
    const buf = concat(atom("moov", mvhdV1(90000, 90000n * 61n)));
    expect(probeMp4DurationSeconds(buf)).toBeCloseTo(61);
  });
  it("returns null for garbage", () => {
    expect(probeMp4DurationSeconds(new Uint8Array([1, 2, 3]))).toBeNull();
  });
  it("resolveDuration precedence: override > probe > screenshot", () => {
    const base = { id: "x", permalink: "", timestamp: "", caption: "", duration_s: null, duration_source: "unknown", insights: {} as Reel["insights"], source: "fixture" } as Reel;
    expect(resolveDuration({ ...base, screenshot: { overview: { duration_s: 30, views: null, reach: null, avg_watch_time_s: null } } as Reel["screenshot"] }, {})).toEqual({ duration_s: 30, duration_source: "screenshot" });
    expect(resolveDuration({ ...base, duration_s: 12, duration_source: "probe" }, { x: { duration_s: 15 } })).toEqual({ duration_s: 15, duration_source: "user" });
    expect(resolveDuration(base, {})).toEqual({ duration_s: null, duration_source: "unknown" });
  });
});
