import fs from "node:fs";
import { P } from "../config.js";
import type { Reel } from "./types.js";

/** Parse an MP4/MOV buffer for moov/mvhd and return duration in seconds (v0 and v1 headers). */
export function probeMp4DurationSeconds(buf: Uint8Array): number | null {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const u32 = (o: number) => dv.getUint32(o);
  const u64 = (o: number) => Number((BigInt(dv.getUint32(o)) << 32n) | BigInt(dv.getUint32(o + 4)));
  const type = (o: number) => String.fromCharCode(buf[o]!, buf[o + 1]!, buf[o + 2]!, buf[o + 3]!);

  function walk(start: number, end: number): number | null {
    let o = start;
    while (o + 8 <= end) {
      let size = u32(o);
      const t = type(o + 4);
      let header = 8;
      if (size === 1) {
        if (o + 16 > end) return null;
        size = u64(o + 8);
        header = 16;
      } else if (size === 0) size = end - o;
      if (size < header) return null;
      if (t === "moov") {
        const r = walk(o + header, Math.min(o + size, end));
        if (r != null) return r;
      } else if (t === "mvhd") {
        const version = buf[o + header]!;
        if (version === 1) {
          if (o + header + 4 + 8 + 8 + 4 + 8 > end) return null;
          const timescale = u32(o + header + 4 + 16);
          const duration = u64(o + header + 4 + 20);
          return timescale > 0 ? duration / timescale : null;
        }
        if (o + header + 4 + 4 + 4 + 4 + 4 > end) return null;
        const timescale = u32(o + header + 4 + 8);
        const duration = u32(o + header + 4 + 12);
        return timescale > 0 ? duration / timescale : null;
      }
      o += size;
    }
    return null;
  }
  try {
    return walk(0, buf.byteLength);
  } catch {
    return null;
  }
}

/** Fetch the head (and, if needed, the tail) of a video via Range requests and probe its duration. */
export async function fetchDurationSeconds(url: string, chunkBytes = 2 * 1024 * 1024): Promise<number | null> {
  try {
    const head = await fetch(url, { headers: { Range: `bytes=0-${chunkBytes - 1}` } });
    if (!head.ok && head.status !== 206) return null;
    const headBuf = new Uint8Array(await head.arrayBuffer());
    const d = probeMp4DurationSeconds(headBuf);
    if (d != null) return d;
    const total = Number(head.headers.get("content-range")?.split("/")[1] ?? head.headers.get("content-length") ?? 0);
    if (!total || total <= chunkBytes) return null;
    const tail = await fetch(url, { headers: { Range: `bytes=${Math.max(0, total - chunkBytes)}-${total - 1}` } });
    if (!tail.ok && tail.status !== 206) return null;
    return probeMp4DurationSeconds(new Uint8Array(await tail.arrayBuffer()));
  } catch {
    return null;
  }
}

export type Overrides = Record<string, { duration_s?: number }>;

export function readOverrides(): Overrides {
  if (!fs.existsSync(P().overrides)) return {};
  return JSON.parse(fs.readFileSync(P().overrides, "utf8")) as Overrides;
}

/** Order: user override > existing probed value > screenshot > null. Never estimate from watch time. */
export function resolveDuration(reel: Reel, overrides: Overrides): Pick<Reel, "duration_s" | "duration_source"> {
  const ov = overrides[reel.id]?.duration_s;
  if (ov != null && ov > 0) return { duration_s: ov, duration_source: "user" };
  if (reel.duration_s != null && reel.duration_source === "probe") return { duration_s: reel.duration_s, duration_source: "probe" };
  if (reel.duration_s != null && reel.duration_source === "user") return { duration_s: reel.duration_s, duration_source: "user" };
  const ss = reel.screenshot?.overview?.duration_s;
  if (ss != null && ss > 0) return { duration_s: ss, duration_source: "screenshot" };
  if (reel.duration_s != null) return { duration_s: reel.duration_s, duration_source: reel.duration_source };
  return { duration_s: null, duration_source: "unknown" };
}
