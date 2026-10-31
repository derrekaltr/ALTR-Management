import fs from "node:fs";
import path from "node:path";
import type { z } from "zod";
import { P } from "../config.js";
import { AccountSchema, DatasetSchema, ReelSchema, type Account, type Dataset, type Reel } from "./types.js";

export function readJson<T>(file: string, schema: z.ZodType<T>): T | null {
  if (!fs.existsSync(file)) return null;
  const raw = JSON.parse(fs.readFileSync(file, "utf8"));
  return schema.parse(raw);
}

/** Atomic write: tmp file + rename. */
export function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(value, null, 2) + "\n");
  fs.renameSync(tmp, file);
}

export function readDataset(): Dataset | null {
  const account = readJson(P().account, AccountSchema);
  const reels = readJson(P().reels, ReelSchema.array());
  if (!account || !reels) return null;
  return DatasetSchema.parse({ account, reels });
}

export function writeDataset(ds: Dataset): void {
  writeJson(P().account, ds.account satisfies Account);
  writeJson(P().reels, ds.reels satisfies Reel[]);
}

/** Merge incoming reels into existing by permalink (fallback id); incoming non-null fields win. */
export function mergeReels(existing: Reel[], incoming: Partial<Reel>[]): Reel[] {
  const key = (r: Partial<Reel>) => r.permalink ?? r.id ?? "";
  const byKey = new Map(existing.map((r) => [key(r), r] as const));
  for (const inc of incoming) {
    const k = key(inc);
    const prev = byKey.get(k);
    if (!prev) {
      const parsed = ReelSchema.safeParse(inc);
      if (parsed.success) byKey.set(k, parsed.data);
      continue;
    }
    const merged: Reel = {
      ...prev,
      ...stripNullish(inc),
      insights: { ...prev.insights, ...stripNullish(inc.insights ?? {}) },
    };
    byKey.set(k, ReelSchema.parse(merged));
  }
  return [...byKey.values()].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
}

function stripNullish<T extends object>(o: T): Partial<T> {
  const out: Partial<T> = {};
  for (const [k, v] of Object.entries(o)) {
    if (v !== null && v !== undefined) (out as Record<string, unknown>)[k] = v;
  }
  return out;
}
