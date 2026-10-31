import type Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import type { ReelPacket } from "../metrics/packet.js";
import type { Profile } from "../rubric/profile.js";
import { buildSystemPrompt } from "../rubric/system-prompt.js";
import { CritiqueParseFailed, CritiqueRefused, MODEL, getClient, usageOf, withRetry } from "./client.js";
import { ReelCritiqueSchema, type CritiqueRecord, type ReelCritique } from "./schemas.js";
import { stripInvalidEvidence, validateReelEvidence, type Mismatch } from "./validate-evidence.js";

export interface CritiqueOptions {
  effort?: "low" | "medium" | "high" | "xhigh" | "max";
  log?: (msg: string) => void;
}

function systemBlocks(profile: Profile): Anthropic.TextBlockParam[] {
  return [{ type: "text", text: buildSystemPrompt(profile), cache_control: { type: "ephemeral" } }];
}

function repairMessage(mismatches: Mismatch[]): string {
  return `Evidence validation failed. Correct ONLY these entries using the exact values from the packet (or drop the entry and mention the gap in data_gaps). Keep everything else identical.\n${mismatches
    .map((m) => `- ${m.path}: ${m.problem}`)
    .join("\n")}`;
}

export async function critiqueReel(packet: ReelPacket, profile: Profile, opts: CritiqueOptions = {}): Promise<CritiqueRecord<ReelCritique>> {
  const client = getClient();
  const log = opts.log ?? (() => {});
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: `Critique this Reel. Packet:\n${JSON.stringify(packet)}` },
  ];

  const call = () =>
    withRetry(() =>
      client.messages.parse({
        model: MODEL,
        max_tokens: 16000,
        system: systemBlocks(profile),
        messages,
        output_config: { effort: opts.effort ?? "high", format: zodOutputFormat(ReelCritiqueSchema) },
      }),
    );

  let res = await call();
  if (res.stop_reason === "refusal") throw new CritiqueRefused(res.stop_details);
  if (!res.parsed_output) throw new CritiqueParseFailed(res);
  let critique = res.parsed_output;
  let usage = usageOf(res);
  log(`  reel ${packet.reel.id}: ${usage.output_tokens} out, cache read ${usage.cache_read_input_tokens}`);

  let v = validateReelEvidence(critique, packet);
  const notes: string[] = [];
  if (!v.ok) {
    log(`  reel ${packet.reel.id}: ${v.mismatches.length} evidence mismatch(es) → repair retry`);
    messages.push({ role: "assistant", content: JSON.stringify(critique) });
    messages.push({ role: "user", content: repairMessage(v.mismatches) });
    res = await call();
    if (res.stop_reason === "refusal") throw new CritiqueRefused(res.stop_details);
    if (!res.parsed_output) throw new CritiqueParseFailed(res);
    critique = res.parsed_output;
    const u2 = usageOf(res);
    usage = {
      input_tokens: usage.input_tokens + u2.input_tokens,
      output_tokens: usage.output_tokens + u2.output_tokens,
      cache_read_input_tokens: usage.cache_read_input_tokens + u2.cache_read_input_tokens,
      cache_creation_input_tokens: usage.cache_creation_input_tokens + u2.cache_creation_input_tokens,
    };
    v = validateReelEvidence(critique, packet);
  }

  let validation: "ok" | "partial" = "ok";
  if (!v.ok) {
    validation = "partial";
    notes.push(...v.mismatches.map((m) => `${m.path}: ${m.problem}`));
    critique = stripInvalidEvidence(critique, v.mismatches);
    critique.confidence = Math.min(critique.confidence, 0.4);
    if (critique.retention_shape !== (packet.curve?.shape ?? "unknown")) critique.retention_shape = packet.curve?.shape ?? "unknown";
  }

  return { critique, validation, validation_notes: notes, usage, model: MODEL, generated_at: new Date().toISOString() };
}
