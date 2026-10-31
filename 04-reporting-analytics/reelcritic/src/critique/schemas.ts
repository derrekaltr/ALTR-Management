import { z } from "zod";
import { METRIC_KEYS } from "../metrics/packet.js";

export const MetricKeyEnum = z.enum(METRIC_KEYS);

export const EvidenceSchema = z.object({
  metric: MetricKeyEnum,
  value: z.number(),
  percentile: z.number().nullable(),
  reading: z.string().describe("One sentence: what this number means for this Reel."),
});
export type Evidence = z.infer<typeof EvidenceSchema>;

const SectionSchema = z.object({
  summary: z.string(),
  points: z.array(z.string()),
  evidence: z.array(EvidenceSchema),
});

const MetricShiftSchema = z.object({
  metric: MetricKeyEnum,
  direction: z.enum(["up", "down"]),
  rationale: z.string(),
});

const ChangeSchema = z.object({
  priority: z.number().int(),
  change: z.string(),
  metric_to_watch: MetricKeyEnum,
  hard_rule: z.string().nullable().describe("A hard-rule id from the packet, or null."),
  pattern_id: z.string().nullable().describe("An example-library pattern id, or null."),
});

const NicheFlagSchema = z.object({
  flag: z.string(),
  severity: z.enum(["info", "warn", "risk"]),
  reason: z.string(),
});

export const ReelCritiqueSchema = z.object({
  reel_id: z.string(),
  headline: z.string().describe("One blunt sentence."),
  value_type: z.enum(["entertaining", "useful", "provocative", "conversion", "unclear"]),
  retention_shape: z.enum(["cliff", "hump", "plateau_loop", "unknown"]),
  what_you_are_doing: SectionSchema,
  why_it_is_incorrect: SectionSchema,
  better_example: z.object({
    mechanism: z.string().describe("The structural mechanism, never a named creator."),
    hook: z.string().describe("The rewritten first 1-3 seconds, word for word / shot by shot."),
    structure: z.array(z.string()).describe("Beat-by-beat structure."),
    reward_or_loop: z.string(),
    caption: z.string().describe("The rewritten caption (may be empty string for no caption)."),
    on_screen_text: z.string().describe("Exact first-frame text block, line breaks as \\n."),
    comment_seed: z.string().describe("The pinned comment / first reply you would post, or empty string."),
    patterns_used: z.array(z.string()).describe("Example-library pattern ids this draws on (must exist in the library)."),
    expected_metric_shift: z.array(MetricShiftSchema),
  }),
  why_it_worked_vs_failed: z.object({
    worked: z.array(z.string()),
    failed: z.array(z.string()),
    evidence: z.array(EvidenceSchema),
  }),
  what_to_change_next: z.array(ChangeSchema),
  niche_flags: z.array(NicheFlagSchema),
  confidence: z.number(),
  data_gaps: z.array(z.string()),
});
export type ReelCritique = z.infer<typeof ReelCritiqueSchema>;

const ReelRefSchema = z.object({
  reel_id: z.string(),
  because: z.string(),
  evidence: z.array(EvidenceSchema),
});

export const AccountCritiqueSchema = z.object({
  account_id: z.string(),
  headline: z.string(),
  what_you_are_doing: SectionSchema,
  why_it_is_incorrect: SectionSchema,
  better_example: z.object({
    mechanism: z.string(),
    content_system: z.array(z.string()),
    cadence: z.string(),
    patterns_used: z.array(z.string()),
    expected_metric_shift: z.array(MetricShiftSchema),
  }),
  why_it_worked_vs_failed: z.object({
    top_reels: z.array(ReelRefSchema),
    bottom_reels: z.array(ReelRefSchema),
  }),
  what_to_change_next: z.array(ChangeSchema),
  niche_flags: z.array(NicheFlagSchema),
  confidence: z.number(),
  data_gaps: z.array(z.string()),
});
export type AccountCritique = z.infer<typeof AccountCritiqueSchema>;

export interface CritiqueRecord<T> {
  critique: T;
  validation: "ok" | "partial";
  validation_notes: string[];
  usage: { input_tokens: number; output_tokens: number; cache_read_input_tokens: number; cache_creation_input_tokens: number } | null;
  model: string;
  generated_at: string;
}
