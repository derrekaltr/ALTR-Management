import { z } from "zod";

export const HookCandidateSchema = z.object({
  text: z.string().min(1).max(300),
  category: z.string().min(1).max(60),
  rationale: z.string().max(500).optional(),
});

export const GenerationResultSchema = z.object({
  candidates: z.array(HookCandidateSchema).min(1),
});

export type HookCandidate = z.infer<typeof HookCandidateSchema>;

export const ReelAnalysisSchema = z.object({
  onScreenHookText: z
    .string()
    .describe("The exact overlay text visible on the video, verbatim. Empty string if none."),
  backgroundDescription: z
    .string()
    .describe("1-2 sentences on what's happening in the background video."),
  tags: z.object({
    setting: z.string().describe("Where it's filmed, e.g. bedroom, car, gym, beach"),
    outfit: z.string().describe("Outfit vibe in a few words"),
    energy: z.string().describe("Pace/energy, e.g. still pose, slow pan, walking, dancing"),
  }),
  whyItWorks: z
    .string()
    .describe("1-2 sentences on why this hook + blank background combo retains viewers."),
  hookVisibleInFirst3s: z
    .boolean()
    .describe("Whether the hook text appears within the first 3 seconds"),
});

export type ReelAnalysis = z.infer<typeof ReelAnalysisSchema>;

export interface SeedHook {
  text: string;
  category: string | null;
  backgroundTags?: string[];
}

export interface GenerateInput {
  seeds: SeedHook[];
  rejectedExamples: string[];
  toneGuidance?: string;
  count: number;
}

export interface FrameInput {
  /** JPEG bytes of frames captured from the video (hook window first). */
  data: Buffer;
  mediaType: "image/jpeg" | "image/png";
}

export interface LLMProvider {
  readonly modelName: string;
  generateHooks(input: GenerateInput): Promise<HookCandidate[]>;
  analyzeReel(frames: FrameInput[], notes?: string): Promise<ReelAnalysis>;
}

/** Thrown for non-retryable provider failures (bad request, parse failure). */
export class LLMError extends Error {
  constructor(
    message: string,
    public readonly retryable: boolean,
  ) {
    super(message);
    this.name = "LLMError";
  }
}
