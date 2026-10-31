import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";

const MonthDay = z.string().regex(/^\d{2}-\d{2}$/, "MM-DD");
const IsoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "YYYY-MM-DD");

export const ProfileSchema = z.object({
  name: z.string(),
  description: z.string(),
  /** Recurring yearly windows, MM-DD (may wrap year end). */
  season_windows: z.array(z.object({ start: MonthDay, end: MonthDay, label: z.string() })).default([]),
  /** Specific dated events (disaster/celebrity spikes) — content in these windows is "event-driven". */
  event_windows: z.array(z.object({ start: IsoDate, end: IsoDate, label: z.string() })).default([]),
  event_keywords: z.array(z.string()).default([]),
  /** Regex sources (case-insensitive) that indicate commercial / sponsorship signals. */
  commercial_risk_patterns: z.array(z.string()).default([]),
  reminders: z.array(z.string()).default([]),
  sentiment_lexicon: z
    .object({ admiring: z.array(z.string()).default([]), hostile: z.array(z.string()).default([]) })
    .default({ admiring: [], hostile: [] }),
  extra_rubric_text: z.string().default(""),
});
export type Profile = z.infer<typeof ProfileSchema>;

const here = path.dirname(fileURLToPath(import.meta.url));
export const PROFILES_DIR = path.join(here, "profiles");

export function listProfiles(): string[] {
  return fs
    .readdirSync(PROFILES_DIR)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""));
}

export function loadProfile(name = "default"): Profile {
  const file = path.join(PROFILES_DIR, `${name}.json`);
  if (!fs.existsSync(file)) throw new Error(`Unknown profile "${name}". Available: ${listProfiles().join(", ")}`);
  return ProfileSchema.parse(JSON.parse(fs.readFileSync(file, "utf8")));
}
