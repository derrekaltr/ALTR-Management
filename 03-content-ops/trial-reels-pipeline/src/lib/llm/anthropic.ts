import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import {
  type FrameInput,
  type GenerateInput,
  GenerationResultSchema,
  type HookCandidate,
  LLMError,
  type LLMProvider,
  type ReelAnalysis,
  ReelAnalysisSchema,
} from "./types";

const GENERATION_SYSTEM = `You write hook captions for Instagram trial reels for lifestyle creators.
The background videos are deliberately blank and low-action (a creator posing or moving slightly);
the on-screen hook text is the entire retention mechanism. Captions overlay the first 3 seconds,
so they must be short (roughly 12 words or fewer), punchy, and curiosity-, humor-, or thirst-driven,
in the same voice as the provided examples: funny, flirty, goofy — suggestive at most, never explicit,
and always inside Instagram's community guidelines. Never number the captions, never add hashtags,
and only use emojis if the examples do. Never paraphrase an example — every caption must be new.`;

const ANALYSIS_SYSTEM = `You analyze Instagram trial reels for a creator agency.
These reels use deliberately blank, low-action background video (a creator posing or moving slightly)
with an on-screen text hook doing all the retention work. You receive frames sampled from one reel,
earliest first (the first frames are from the 0-3 second hook window).
Transcribe overlay text exactly as written. Describe the background plainly and note why the
hook + blank background combination holds attention.`;

function isRetryable(error: unknown): boolean {
  if (error instanceof Anthropic.RateLimitError) return true;
  if (error instanceof Anthropic.APIConnectionError) return true;
  if (error instanceof Anthropic.InternalServerError) return true;
  if (error instanceof Anthropic.APIError) {
    const status = (error as { status?: number }).status;
    return typeof status === "number" && status >= 500;
  }
  return false;
}

async function withOneRetry<T>(fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (!isRetryable(error)) throw error;
    await new Promise((r) => setTimeout(r, 1500));
    return fn();
  }
}

export class AnthropicProvider implements LLMProvider {
  readonly modelName: string;
  private client: Anthropic;

  constructor() {
    this.modelName = process.env.LLM_MODEL || "claude-sonnet-5";
    this.client = new Anthropic();
  }

  async generateHooks(input: GenerateInput): Promise<HookCandidate[]> {
    const seedLines = input.seeds
      .map((s) => {
        const bg = s.backgroundTags?.length ? ` (background: ${s.backgroundTags.join(", ")})` : "";
        return `- [${s.category ?? "uncategorized"}] ${s.text}${bg}`;
      })
      .join("\n");
    const avoid = input.rejectedExamples.slice(0, 30);
    const parts = [
      `<proven_examples>\n${seedLines}\n</proven_examples>`,
      avoid.length
        ? `<avoid>\nPreviously rejected — do not produce these or close variants:\n${avoid.map((t) => `- ${t}`).join("\n")}\n</avoid>`
        : "",
      input.toneGuidance ? `<tone_guidance>\n${input.toneGuidance}\n</tone_guidance>` : "",
      `Generate exactly ${input.count} new hook captions in the voice of the proven examples.`,
    ].filter(Boolean);

    const response = await withOneRetry(() =>
      this.client.messages.parse({
        model: this.modelName,
        max_tokens: 4000,
        system: GENERATION_SYSTEM,
        messages: [{ role: "user", content: parts.join("\n\n") }],
        output_config: { format: zodOutputFormat(GenerationResultSchema) },
      }),
    ).catch((error) => {
      throw toLLMError(error, "hook generation");
    });

    if (!response.parsed_output) {
      throw new LLMError("Model response did not match the expected schema", false);
    }
    return response.parsed_output.candidates;
  }

  async analyzeReel(frames: FrameInput[], notes?: string): Promise<ReelAnalysis> {
    const content: Anthropic.ContentBlockParam[] = frames.map((frame) => ({
      type: "image" as const,
      source: {
        type: "base64" as const,
        media_type: frame.mediaType,
        data: frame.data.toString("base64"),
      },
    }));
    content.push({
      type: "text",
      text:
        `Analyze this reel from ${frames.length} sampled frames (earliest first; the first three are from the 0-3s hook window).` +
        (notes ? `\nAgency notes: ${notes}` : ""),
    });

    const response = await withOneRetry(() =>
      this.client.messages.parse({
        model: this.modelName,
        max_tokens: 2000,
        system: ANALYSIS_SYSTEM,
        messages: [{ role: "user", content }],
        output_config: { format: zodOutputFormat(ReelAnalysisSchema) },
      }),
    ).catch((error) => {
      throw toLLMError(error, "reel analysis");
    });

    if (!response.parsed_output) {
      throw new LLMError("Model response did not match the expected schema", false);
    }
    return response.parsed_output;
  }
}

function toLLMError(error: unknown, context: string): LLMError {
  if (error instanceof LLMError) return error;
  const retryable = isRetryable(error);
  const message = error instanceof Error ? error.message : String(error);
  return new LLMError(`${context} failed: ${message}`, retryable);
}
