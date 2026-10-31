import { AnthropicProvider } from "./anthropic";
import { MockProvider } from "./mock";
import type { LLMProvider } from "./types";

export function getProvider(): LLMProvider {
  if (process.env.LLM_MOCK === "1" || !process.env.ANTHROPIC_API_KEY) {
    return new MockProvider();
  }
  return new AnthropicProvider();
}

export * from "./types";
