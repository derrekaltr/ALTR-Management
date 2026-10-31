import type { AccountPacket, MetricKey, ReelPacket } from "../metrics/packet.js";
import type { AccountCritique, Evidence, ReelCritique } from "./schemas.js";
import { exampleIds } from "../rubric/examples.js";

export interface Mismatch {
  path: string;
  metric?: MetricKey | string;
  problem: string;
}

const REL_TOL = 0.005;
const ABS_TOL = 1e-3;

function closeEnough(a: number, b: number): boolean {
  return Math.abs(a - b) <= Math.max(REL_TOL * Math.abs(b), ABS_TOL);
}

function checkEvidence(ev: Evidence, packetMetrics: ReelPacket["metrics"], path: string, out: Mismatch[]): boolean {
  const cell = packetMetrics[ev.metric];
  if (!cell) {
    out.push({ path, metric: ev.metric, problem: `metric "${ev.metric}" not in packet` });
    return false;
  }
  if (cell.value == null) {
    out.push({ path, metric: ev.metric, problem: `metric "${ev.metric}" is null in packet (cannot be cited; list it in data_gaps instead)` });
    return false;
  }
  if (!closeEnough(ev.value, cell.value)) {
    out.push({ path, metric: ev.metric, problem: `value ${ev.value} != packet ${cell.value}` });
    return false;
  }
  if (cell.percentile == null && ev.percentile != null) {
    out.push({ path, metric: ev.metric, problem: `percentile ${ev.percentile} given but packet percentile is null` });
    return false;
  }
  if (cell.percentile != null && (ev.percentile == null || Math.abs(ev.percentile - cell.percentile) > 1)) {
    out.push({ path, metric: ev.metric, problem: `percentile ${ev.percentile} != packet ${cell.percentile}` });
    return false;
  }
  return true;
}

export interface ValidationResult {
  ok: boolean;
  mismatches: Mismatch[];
}

export function validateReelEvidence(c: ReelCritique, packet: ReelPacket): ValidationResult {
  const out: Mismatch[] = [];
  if (c.reel_id !== packet.reel.id) out.push({ path: "reel_id", problem: `reel_id ${c.reel_id} != ${packet.reel.id}` });
  const expectedShape = packet.curve?.shape ?? "unknown";
  if (c.retention_shape !== expectedShape) out.push({ path: "retention_shape", problem: `retention_shape ${c.retention_shape} != classifier ${expectedShape}` });

  const sections: Array<[string, Evidence[]]> = [
    ["what_you_are_doing.evidence", c.what_you_are_doing.evidence],
    ["why_it_is_incorrect.evidence", c.why_it_is_incorrect.evidence],
    ["why_it_worked_vs_failed.evidence", c.why_it_worked_vs_failed.evidence],
  ];
  for (const [p, evs] of sections) evs.forEach((ev, i) => checkEvidence(ev, packet.metrics, `${p}[${i}]`, out));

  const ruleIds = new Set(packet.hard_rules.map((h) => h.rule as string));
  const patterns = exampleIds();
  c.what_to_change_next.forEach((ch, i) => {
    if (ch.hard_rule != null && !ruleIds.has(ch.hard_rule))
      out.push({ path: `what_to_change_next[${i}].hard_rule`, problem: `"${ch.hard_rule}" is not a hard-rule hit in the packet` });
    if (ch.pattern_id != null && !patterns.has(ch.pattern_id))
      out.push({ path: `what_to_change_next[${i}].pattern_id`, problem: `"${ch.pattern_id}" is not an example-library pattern id` });
  });
  c.better_example.patterns_used.forEach((id, i) => {
    if (!patterns.has(id)) out.push({ path: `better_example.patterns_used[${i}]`, problem: `"${id}" is not an example-library pattern id` });
  });
  return { ok: out.length === 0, mismatches: out };
}

export function validateAccountEvidence(c: AccountCritique, packet: AccountPacket, reelPackets: Map<string, ReelPacket>): ValidationResult {
  const out: Mismatch[] = [];
  const sections: Array<[string, Evidence[]]> = [
    ["what_you_are_doing.evidence", c.what_you_are_doing.evidence],
    ["why_it_is_incorrect.evidence", c.why_it_is_incorrect.evidence],
  ];
  for (const [p, evs] of sections) evs.forEach((ev, i) => checkEvidence(ev, packet.metrics, `${p}[${i}]`, out));

  const refs: Array<[string, AccountCritique["why_it_worked_vs_failed"]["top_reels"]]> = [
    ["why_it_worked_vs_failed.top_reels", c.why_it_worked_vs_failed.top_reels],
    ["why_it_worked_vs_failed.bottom_reels", c.why_it_worked_vs_failed.bottom_reels],
  ];
  for (const [p, list] of refs) {
    list.forEach((ref, i) => {
      const rp = reelPackets.get(ref.reel_id);
      if (!rp) {
        out.push({ path: `${p}[${i}].reel_id`, problem: `unknown reel_id ${ref.reel_id}` });
        return;
      }
      ref.evidence.forEach((ev, j) => checkEvidence(ev, rp.metrics, `${p}[${i}].evidence[${j}]`, out));
    });
  }
  const hardIds = new Set(Object.keys(packet.hard_rule_summary));
  const patterns = exampleIds();
  c.what_to_change_next.forEach((ch, i) => {
    if (ch.hard_rule != null && !hardIds.has(ch.hard_rule))
      out.push({ path: `what_to_change_next[${i}].hard_rule`, problem: `"${ch.hard_rule}" is not a hard-rule hit for this account` });
    if (ch.pattern_id != null && !patterns.has(ch.pattern_id))
      out.push({ path: `what_to_change_next[${i}].pattern_id`, problem: `"${ch.pattern_id}" is not an example-library pattern id` });
  });
  c.better_example.patterns_used.forEach((id, i) => {
    if (!patterns.has(id)) out.push({ path: `better_example.patterns_used[${i}]`, problem: `"${id}" is not an example-library pattern id` });
  });
  return { ok: out.length === 0, mismatches: out };
}

/** Remove evidence entries that failed validation (used after the repair retry also fails). */
export function stripInvalidEvidence<T extends ReelCritique | AccountCritique>(c: T, mismatches: Mismatch[]): T {
  const bad = new Set(mismatches.map((m) => m.path));
  const clone = structuredClone(c) as T;
  const filter = (path: string, evs: Evidence[]) => evs.filter((_, i) => !bad.has(`${path}[${i}]`));
  clone.what_you_are_doing.evidence = filter("what_you_are_doing.evidence", clone.what_you_are_doing.evidence);
  clone.why_it_is_incorrect.evidence = filter("why_it_is_incorrect.evidence", clone.why_it_is_incorrect.evidence);
  if ("reel_id" in clone) {
    const rc = clone as ReelCritique;
    rc.why_it_worked_vs_failed.evidence = filter("why_it_worked_vs_failed.evidence", rc.why_it_worked_vs_failed.evidence);
  } else {
    const ac = clone as AccountCritique;
    ac.why_it_worked_vs_failed.top_reels.forEach((ref, i) => {
      ref.evidence = filter(`why_it_worked_vs_failed.top_reels[${i}].evidence`, ref.evidence);
    });
    ac.why_it_worked_vs_failed.bottom_reels.forEach((ref, i) => {
      ref.evidence = filter(`why_it_worked_vs_failed.bottom_reels[${i}].evidence`, ref.evidence);
    });
  }
  clone.what_to_change_next = clone.what_to_change_next.map((ch, i) => ({
    ...ch,
    hard_rule: bad.has(`what_to_change_next[${i}].hard_rule`) ? null : ch.hard_rule,
    pattern_id: bad.has(`what_to_change_next[${i}].pattern_id`) ? null : ch.pattern_id,
  }));
  clone.better_example.patterns_used = clone.better_example.patterns_used.filter((_, i) => !bad.has(`better_example.patterns_used[${i}]`));
  return clone;
}

/** Warn-only: numbers in prose that don't appear in the packet. */
export function proseNumberWarnings(text: string, packetMetrics: ReelPacket["metrics"] | AccountPacket["metrics"]): string[] {
  const known = new Set<number>();
  for (const cell of Object.values(packetMetrics)) {
    if (cell.value != null) {
      known.add(cell.value);
      known.add(Math.round(cell.value * 100)); // percent form
      known.add(Math.round(cell.value * 1000) / 10);
    }
    if (cell.percentile != null) known.add(cell.percentile), known.add(Math.round(cell.percentile));
  }
  const warnings: string[] = [];
  const re = /(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(%|x|s)?(?![\w])/g;
  for (const m of text.matchAll(re)) {
    const n = Number(m[1]!.replace(/,/g, ""));
    if (!Number.isFinite(n) || n <= 5) continue; // ignore small ordinals / list numbers
    const hit = [...known].some((k) => closeEnough(n, k) || closeEnough(n, k * 100));
    if (!hit) warnings.push(`"${m[0]}" not found in packet`);
  }
  return [...new Set(warnings)].slice(0, 10);
}
