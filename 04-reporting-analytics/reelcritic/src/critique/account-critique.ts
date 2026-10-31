import type Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import type { AccountPacket, ReelPacket } from "../metrics/packet.js";
import type { Profile } from "../rubric/profile.js";
import { buildSystemPrompt } from "../rubric/system-prompt.js";
import { CritiqueParseFailed, CritiqueRefused, MODEL, getClient, usageOf, withRetry } from "./client.js";
import { AccountCritiqueSchema, type AccountCritique, type CritiqueRecord, type ReelCritique } from "./schemas.js";
import { stripInvalidEvidence, validateAccountEvidence } from "./validate-evidence.js";
import type { CritiqueOptions } from "./reel-critique.js";

export async function critiqueAccount(
  packet: AccountPacket,
  reelPackets: Map<string, ReelPacket>,
  reelCritiques: CritiqueRecord<ReelCritique>[],
  profile: Profile,
  opts: CritiqueOptions = {},
): Promise<CritiqueRecord<AccountCritique>> {
  const client = getClient();
  const log = opts.log ?? (() => {});
  const headlines = reelCritiques.map((r) => ({ reel_id: r.critique.reel_id, headline: r.critique.headline, value_type: r.critique.value_type, retention_shape: r.critique.retention_shape }));
  const perReelMetrics = Object.fromEntries([...reelPackets.entries()].map(([id, p]) => [id, p.metrics]));

  const messages: Anthropic.MessageParam[] = [
    {
      role: "user",
      content:
        `Critique this ACCOUNT as a whole (patterns across Reels, cadence, what to double down on and what to stop). ` +
        `When citing evidence for a specific Reel in top_reels/bottom_reels, use that Reel's own metrics from per_reel_metrics (exact value and percentile). ` +
        `For account-level evidence use account packet.metrics (medians; percentile null).\n` +
        `Account packet:\n${JSON.stringify(packet)}\n\nPer-Reel headlines from the individual critiques:\n${JSON.stringify(headlines)}\n\nper_reel_metrics:\n${JSON.stringify(perReelMetrics)}`,
    },
  ];

  const call = async () =>
    withRetry(async () => {
      const stream = client.messages.stream({
        model: MODEL,
        max_tokens: 32000,
        system: [{ type: "text", text: buildSystemPrompt(profile), cache_control: { type: "ephemeral" } }],
        messages,
        output_config: { effort: opts.effort ?? "high", format: zodOutputFormat(AccountCritiqueSchema) },
      });
      return stream.finalMessage();
    });

  const parseText = (msg: Anthropic.Message): AccountCritique => {
    const text = msg.content.filter((b): b is Anthropic.TextBlock => b.type === "text").map((b) => b.text).join("");
    try {
      return AccountCritiqueSchema.parse(JSON.parse(text));
    } catch (e) {
      throw new CritiqueParseFailed({ text, error: String(e) });
    }
  };

  let msg = await call();
  if (msg.stop_reason === "refusal") throw new CritiqueRefused(msg.stop_details);
  let critique = parseText(msg);
  let usage = usageOf(msg);
  log(`  account: ${usage.output_tokens} out, cache read ${usage.cache_read_input_tokens}`);

  let v = validateAccountEvidence(critique, packet, reelPackets);
  const notes: string[] = [];
  if (!v.ok) {
    log(`  account: ${v.mismatches.length} evidence mismatch(es) → repair retry`);
    messages.push({ role: "assistant", content: JSON.stringify(critique) });
    messages.push({
      role: "user",
      content: `Evidence validation failed. Correct ONLY these entries using exact packet values (or drop them and note the gap). Keep everything else identical.\n${v.mismatches.map((m) => `- ${m.path}: ${m.problem}`).join("\n")}`,
    });
    msg = await call();
    if (msg.stop_reason === "refusal") throw new CritiqueRefused(msg.stop_details);
    critique = parseText(msg);
    const u2 = usageOf(msg);
    usage = {
      input_tokens: usage.input_tokens + u2.input_tokens,
      output_tokens: usage.output_tokens + u2.output_tokens,
      cache_read_input_tokens: usage.cache_read_input_tokens + u2.cache_read_input_tokens,
      cache_creation_input_tokens: usage.cache_creation_input_tokens + u2.cache_creation_input_tokens,
    };
    v = validateAccountEvidence(critique, packet, reelPackets);
  }

  let validation: "ok" | "partial" = "ok";
  if (!v.ok) {
    validation = "partial";
    notes.push(...v.mismatches.map((m) => `${m.path}: ${m.problem}`));
    critique = stripInvalidEvidence(critique, v.mismatches);
    critique.confidence = Math.min(critique.confidence, 0.4);
  }
  return { critique, validation, validation_notes: notes, usage, model: MODEL, generated_at: new Date().toISOString() };
}
