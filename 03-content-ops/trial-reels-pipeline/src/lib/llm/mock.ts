import type {
  FrameInput,
  GenerateInput,
  HookCandidate,
  LLMProvider,
  ReelAnalysis,
} from "./types";

const TEMPLATES = [
  (s: string) => `POV: ${s.toLowerCase()} but it's somehow worse today`,
  (s: string) => `nobody warned me that ${s.toLowerCase()}`,
  (s: string) => `me pretending ${s.toLowerCase()} is totally normal`,
  (s: string) => `when he finds out ${s.toLowerCase()}`,
  (s: string) => `day 47 of ${s.toLowerCase()} and no regrets`,
  (s: string) => `tell me why ${s.toLowerCase()}`,
  (s: string) => `she said ${s.toLowerCase()} and I believed her`,
  (s: string) => `warning: ${s.toLowerCase()} ahead`,
  (s: string) => `it's giving ${s.toLowerCase()} energy`,
  (s: string) => `rating my ability to ${s.toLowerCase()}: 2/10`,
];

/**
 * Deterministic offline provider so the entire pipeline (generation, review,
 * analysis) is demoable and testable with zero credentials.
 */
export class MockProvider implements LLMProvider {
  readonly modelName = "mock";

  async generateHooks(input: GenerateInput): Promise<HookCandidate[]> {
    await new Promise((r) => setTimeout(r, 50));
    const candidates: HookCandidate[] = [];
    for (let i = 0; i < input.count; i++) {
      const seed = input.seeds[i % Math.max(input.seeds.length, 1)];
      const fragment = (seed?.text ?? "living my best life").split(" ").slice(0, 5).join(" ");
      candidates.push({
        text: TEMPLATES[i % TEMPLATES.length](fragment),
        category: seed?.category ?? "goofy",
        rationale: "mock candidate riffing on a seed hook",
      });
    }
    return candidates;
  }

  async analyzeReel(frames: FrameInput[], notes?: string): Promise<ReelAnalysis> {
    await new Promise((r) => setTimeout(r, 50));
    return {
      onScreenHookText: `mock extracted hook (${frames.length} frames${notes ? ", noted" : ""})`,
      backgroundDescription:
        "Creator stands mostly still in a plain room; minimal motion, the text carries the video.",
      tags: { setting: "bedroom", outfit: "casual", energy: "still pose" },
      whyItWorks:
        "Blank background keeps all attention on the overlay text, so the hook does the retention work.",
      hookVisibleInFirst3s: true,
    };
  }
}
