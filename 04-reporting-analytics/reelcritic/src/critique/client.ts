import Anthropic from "@anthropic-ai/sdk";
import { MODEL, loadEnv } from "../config.js";

let client: Anthropic | null = null;

/** Zero-arg client: resolves ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile. */
export function getClient(): Anthropic {
  loadEnv();
  if (!client) client = new Anthropic();
  return client;
}

export { MODEL };

export class CritiqueRefused extends Error {
  constructor(public details: unknown) {
    super("Claude declined to produce the critique (stop_reason=refusal)");
  }
}
export class CritiqueParseFailed extends Error {
  constructor(public raw: unknown) {
    super("Claude response did not parse against the schema");
  }
}

export interface Usage {
  input_tokens: number;
  output_tokens: number;
  cache_read_input_tokens: number;
  cache_creation_input_tokens: number;
}

export function usageOf(msg: { usage: Anthropic.Usage }): Usage {
  return {
    input_tokens: msg.usage.input_tokens,
    output_tokens: msg.usage.output_tokens,
    cache_read_input_tokens: msg.usage.cache_read_input_tokens ?? 0,
    cache_creation_input_tokens: msg.usage.cache_creation_input_tokens ?? 0,
  };
}

/** Retry on rate limits / connection errors with backoff; rethrow others. Most-specific-first. */
export async function withRetry<T>(fn: () => Promise<T>, attempts = 4): Promise<T> {
  let delay = 2000;
  for (let i = 0; ; i++) {
    try {
      return await fn();
    } catch (err) {
      const last = i >= attempts - 1;
      if (err instanceof Anthropic.AuthenticationError) {
        throw new Error("No valid Anthropic credential. Run `ant auth login` or set ANTHROPIC_API_KEY in .env");
      }
      if (err instanceof Anthropic.BadRequestError) throw err;
      if (err instanceof Anthropic.RateLimitError || err instanceof Anthropic.InternalServerError || err instanceof Anthropic.APIConnectionError) {
        if (last) throw err;
        await new Promise((r) => setTimeout(r, delay));
        delay *= 2;
        continue;
      }
      if (err instanceof Anthropic.APIError && err.status && err.status >= 500 && !last) {
        await new Promise((r) => setTimeout(r, delay));
        delay *= 2;
        continue;
      }
      throw err;
    }
  }
}
