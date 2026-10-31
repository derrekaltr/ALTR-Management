import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import type { LengthBand } from "../metrics/length-band.js";

/** Failure-mode vocabulary shared by the packet (metrics/hard rules) and the example library. */
export const FAILURE_MODES = [
  "weak_hook",
  "cliff",
  "mid_sag",
  "no_payoff",
  "no_loop",
  "no_premise",
  "static_talking_head",
  "caption_dead",
  "hashtag_stuffing",
  "engagement_bait",
  "low_sends",
  "low_saves",
  "low_comments",
  "no_conversation_seed",
  "too_long",
  "muted_autoplay_unreadable",
  "hostile_comments",
  "commercial_signal",
] as const;
export type FailureMode = (typeof FAILURE_MODES)[number];

export const ExampleSchema = z.object({
  id: z.string().regex(/^(hook|caption|text|comment)\.[a-z0-9_]+(\.[a-z0-9_]+)*$/),
  name: z.string(),
  when: z.object({
    failure_modes: z.array(z.enum(FAILURE_MODES)),
    length_bands: z.array(z.enum(["7-15", "15-30", "30-60", "60+"])),
    value_types: z.array(z.enum(["entertaining", "useful", "provocative", "conversion"])),
  }),
  template: z.string(),
  examples: z.array(z.string()),
  mechanism: z.string(),
  anti_pattern: z.string(),
  observed: z.array(z.string()),
});
export type Example = z.infer<typeof ExampleSchema>;

export type ExampleKind = "hooks" | "captions" | "on-screen-text" | "comments";
export const EXAMPLE_KINDS: ExampleKind[] = ["hooks", "captions", "on-screen-text", "comments"];

const here = path.dirname(fileURLToPath(import.meta.url));
export const EXAMPLES_DIR = path.join(here, "examples");

let cache: Example[] | null = null;
export function loadExamples(): Example[] {
  if (cache) return cache;
  const all: Example[] = [];
  for (const kind of EXAMPLE_KINDS) {
    const file = path.join(EXAMPLES_DIR, `${kind}.json`);
    const raw = JSON.parse(fs.readFileSync(file, "utf8")) as unknown[];
    for (const item of raw) all.push(ExampleSchema.parse(item));
  }
  const ids = new Set<string>();
  for (const e of all) {
    if (ids.has(e.id)) throw new Error(`duplicate example id ${e.id}`);
    ids.add(e.id);
  }
  cache = all;
  return all;
}

export function exampleIds(): Set<string> {
  return new Set(loadExamples().map((e) => e.id));
}

/** Rank examples by overlap with the packet's failure modes, then band, then value type. */
export function selectExamples(
  failureModes: FailureMode[],
  band: LengthBand,
  valueType: Example["when"]["value_types"][number] | "unclear" | null,
  limit = 10,
): Example[] {
  const fm = new Set(failureModes);
  const scored = loadExamples().map((e) => {
    let s = 0;
    for (const f of e.when.failure_modes) if (fm.has(f)) s += 3;
    if (band !== "unknown" && band !== "over-3min" && e.when.length_bands.includes(band)) s += 1;
    if (band === "over-3min" && e.when.length_bands.includes("60+")) s += 1;
    if (valueType && valueType !== "unclear" && e.when.value_types.includes(valueType)) s += 1;
    return { e, s };
  });
  return scored
    .filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s || a.e.id.localeCompare(b.e.id))
    .slice(0, limit)
    .map((x) => x.e);
}

/** Deterministic markdown rendering of the whole library for the (cached) system prompt. */
export function renderLibraryMarkdown(): string {
  const byKind: Record<ExampleKind, Example[]> = { hooks: [], captions: [], "on-screen-text": [], comments: [] };
  for (const e of loadExamples()) {
    const kind: ExampleKind = e.id.startsWith("hook.") ? "hooks" : e.id.startsWith("caption.") ? "captions" : e.id.startsWith("text.") ? "on-screen-text" : "comments";
    byKind[kind].push(e);
  }
  const block = (e: Example) =>
    `- **${e.id}** — ${e.name}\n  - use for: ${e.when.failure_modes.join(", ")} · bands ${e.when.length_bands.join("/")} · value ${e.when.value_types.join("/")}\n  - template: ${e.template}\n  - examples: ${e.examples.map((x) => `"${x}"`).join(" · ")}\n  - why it works: ${e.mechanism}\n  - not this: ${e.anti_pattern}`;
  return EXAMPLE_KINDS.map((k) => `### ${k}\n${byKind[k].map(block).join("\n")}`).join("\n\n");
}
