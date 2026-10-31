import type { MetricCell, MetricTable, ReelPacket } from "../metrics/packet.js";
import type { Evidence } from "../critique/schemas.js";
import { HARD_RULE_CITATIONS, type HardRuleId } from "../metrics/hard-rules.js";
import { proseNumberWarnings } from "../critique/validate-evidence.js";
import type { ReportBundle } from "./json.js";

const fmt = (v: number | null | undefined, digits = 3): string => {
  if (v == null) return "—";
  if (Math.abs(v) >= 1000) return Math.round(v).toLocaleString("en-US");
  if (Number.isInteger(v)) return String(v);
  return v.toFixed(digits);
};
const pct = (v: number | null | undefined): string => (v == null ? "—" : `${(v * 100).toFixed(1)}%`);
const cell = (c: MetricCell, asPct = false): string => `${asPct ? pct(c.value) : fmt(c.value)}${c.percentile != null ? ` (p${Math.round(c.percentile)})` : ""}`;
const ev = (e: Evidence): string => `\`${e.metric} = ${fmt(e.value, 4)}${e.percentile != null ? ` (p${Math.round(e.percentile)})` : ""}\` — ${e.reading}`;
const bullets = (xs: string[]): string => (xs.length ? xs.map((x) => `- ${x}`).join("\n") : "- (none)");

function metricsTable(m: MetricTable): string {
  const rows: Array<[string, string]> = [
    ["views", cell(m.views)],
    ["reach", cell(m.reach)],
    ["replay_ratio (views/reach)", cell(m.replay_ratio)],
    ["send_rate (shares/reach)", cell(m.send_rate, true)],
    ["save_rate (saved/reach)", cell(m.save_rate, true)],
    ["comment_rate", cell(m.comment_rate, true)],
    ["like_rate", cell(m.like_rate, true)],
    ["engagement_rate", cell(m.engagement_rate, true)],
    ["avg_watch_time_s", cell(m.avg_watch_time_s)],
    ["duration_s", cell(m.duration_s)],
    ["hold_rate (watch/duration)", cell(m.hold_rate, true)],
    ["hook_rate (1−skip)", cell(m.hook_rate, true)],
    ["completion_vs_band_delta", cell(m.completion_vs_band_delta)],
    ["non_follower_share", cell(m.non_follower_share, true)],
    ["views_vs_tier_ratio", cell(m.views_vs_tier_ratio)],
    ["hashtag_count", cell(m.hashtag_count)],
  ];
  return `| metric | value (own-history percentile) |\n|---|---|\n${rows.map(([k, v]) => `| ${k} | ${v} |`).join("\n")}`;
}

function reelSection(entry: ReportBundle["reels"][number], idx: number): string {
  const p = entry.packet;
  const c = entry.critique;
  const head = `## ${idx + 1}. Reel ${p.reel.id} — ${p.reel.timestamp.slice(0, 10)} · ${p.reel.length_band === "unknown" ? "length unknown" : `${p.reel.length_band}s`}${p.niche.event_driven ? " · **EVENT-DRIVEN**" : ""}${p.niche.commercial_risk.hit ? " · **COMMERCIAL RISK**" : ""}`;
  const caption = p.reel.caption ? `> ${p.reel.caption.replace(/\n+/g, " ").slice(0, 240)}\n> [${p.reel.permalink}](${p.reel.permalink})` : `> [${p.reel.permalink}](${p.reel.permalink})`;
  const hard = p.hard_rules.length
    ? `**Hard-rule violations:**\n${p.hard_rules.map((h) => `- \`${h.rule}\` — ${h.evidence} _(${h.citation})_`).join("\n")}`
    : "**Hard-rule violations:** none";
  const curve = p.curve
    ? `**Retention curve:** shape = \`${p.curve.shape}\`, first-15% drop ${fmt(p.curve.first_15pct_drop, 1)} pts, tail ${fmt(p.curve.tail_retention_pct, 1)}%, rewatch bump: ${p.curve.rewatch_bump ? "yes" : "no"}`
    : "**Retention curve:** not supplied (in-app only — upload a screenshot)";
  const fm = p.failure_modes.length ? `**Failure modes (computed):** ${p.failure_modes.map((f) => `\`${f}\``).join(", ")}` : "**Failure modes (computed):** none flagged";
  const niche = [
    p.niche.season_label ? `season: ${p.niche.season_label}` : null,
    p.niche.event_driven ? `event-driven: ${p.niche.event_label}` : null,
    p.niche.commercial_risk.hit ? `commercial-risk matches: ${p.niche.commercial_risk.matches.join(", ")}` : null,
    p.niche.comment_sentiment ? `comments sampled ${p.niche.comment_sentiment.sampled}: admiring ${p.niche.comment_sentiment.admiring}, hostile ${p.niche.comment_sentiment.hostile}` : null,
  ].filter(Boolean) as string[];

  if (!c) {
    return `${head}\n\n${caption}\n\n${metricsTable(p.metrics)}\n\n${hard}\n\n${curve}\n\n_No critique generated (run \`analyze\`)._\n`;
  }
  const k = c.critique;
  const banner = c.validation === "partial" ? `> ⚠️ **Partial validation:** some cited evidence did not match the computed packet and was removed; confidence capped at 0.4.\n> ${c.validation_notes.join("; ")}\n\n` : "";
  const prose = [k.headline, k.what_you_are_doing.summary, ...k.what_you_are_doing.points, k.why_it_is_incorrect.summary, ...k.why_it_is_incorrect.points, ...k.why_it_worked_vs_failed.worked, ...k.why_it_worked_vs_failed.failed].join(" ");
  const warn = proseNumberWarnings(prose, p.metrics);

  return `${head}

${caption}

${banner}**${k.headline}**  
value type: \`${k.value_type}\` · retention shape: \`${k.retention_shape}\` · confidence: ${k.confidence.toFixed(2)}

${metricsTable(p.metrics)}

${hard}

${curve}

${fm}
${niche.length ? `\n**Niche:** ${niche.join(" · ")}` : ""}

### What you're doing
${k.what_you_are_doing.summary}
${bullets(k.what_you_are_doing.points)}
${k.what_you_are_doing.evidence.length ? `\nEvidence:\n${bullets(k.what_you_are_doing.evidence.map(ev))}` : ""}

### Why it's incorrect
${k.why_it_is_incorrect.summary}
${bullets(k.why_it_is_incorrect.points)}
${k.why_it_is_incorrect.evidence.length ? `\nEvidence:\n${bullets(k.why_it_is_incorrect.evidence.map(ev))}` : ""}

### A better version (mechanism, same length band)
**Mechanism:** ${k.better_example.mechanism}  
**Hook (first 1–3 s):** ${k.better_example.hook}  
**Structure:**
${bullets(k.better_example.structure)}
**Reward / loop:** ${k.better_example.reward_or_loop}  
**On-screen text (frame 0):**
\`\`\`
${k.better_example.on_screen_text}
\`\`\`
**Caption:** ${k.better_example.caption ? `"${k.better_example.caption}"` : "_(none)_"}  
**Comment seed:** ${k.better_example.comment_seed ? `"${k.better_example.comment_seed}"` : "_(none)_"}  
**Patterns used:** ${k.better_example.patterns_used.length ? k.better_example.patterns_used.map((p) => `\`${p}\``).join(", ") : "—"}  
**Expected metric shift:**
${bullets(k.better_example.expected_metric_shift.map((s) => `\`${s.metric}\` ${s.direction === "up" ? "↑" : "↓"} — ${s.rationale}`))}

### Why it worked vs. why it failed
**Worked:**
${bullets(k.why_it_worked_vs_failed.worked)}
**Failed:**
${bullets(k.why_it_worked_vs_failed.failed)}
${k.why_it_worked_vs_failed.evidence.length ? `\nEvidence:\n${bullets(k.why_it_worked_vs_failed.evidence.map(ev))}` : ""}

### What to change next
${k.what_to_change_next
  .sort((a, b) => a.priority - b.priority)
  .map((ch) => `${ch.priority}. ${ch.change} _(watch \`${ch.metric_to_watch}\`${ch.hard_rule ? `; fixes \`${ch.hard_rule}\`` : ""}${ch.pattern_id ? `; pattern \`${ch.pattern_id}\`` : ""})_`)
  .join("\n")}
${k.niche_flags.length ? `\n### Niche flags\n${bullets(k.niche_flags.map((f) => `**${f.severity.toUpperCase()}** ${f.flag} — ${f.reason}`))}` : ""}
${k.data_gaps.length ? `\n<details><summary>Data gaps</summary>\n\n${bullets(k.data_gaps)}\n\n</details>` : ""}
${warn.length ? `\n<sub>Prose-number check: ${warn.join("; ")}</sub>` : ""}
`;
}

export function renderReport(bundle: ReportBundle): string {
  const ap = bundle.account_packet;
  const ac = bundle.account_critique;
  const hardSummary = Object.entries(ap.hard_rule_summary);

  const accountBlock = ac
    ? `${ac.validation === "partial" ? `> ⚠️ **Partial validation:** ${ac.validation_notes.join("; ")}\n\n` : ""}**${ac.critique.headline}**  
confidence: ${ac.critique.confidence.toFixed(2)}

### What you're doing
${ac.critique.what_you_are_doing.summary}
${bullets(ac.critique.what_you_are_doing.points)}
${ac.critique.what_you_are_doing.evidence.length ? `\nEvidence:\n${bullets(ac.critique.what_you_are_doing.evidence.map(ev))}` : ""}

### Why it's incorrect
${ac.critique.why_it_is_incorrect.summary}
${bullets(ac.critique.why_it_is_incorrect.points)}
${ac.critique.why_it_is_incorrect.evidence.length ? `\nEvidence:\n${bullets(ac.critique.why_it_is_incorrect.evidence.map(ev))}` : ""}

### A better system
**Mechanism:** ${ac.critique.better_example.mechanism}  
**Content system:**
${bullets(ac.critique.better_example.content_system)}
**Cadence:** ${ac.critique.better_example.cadence}  
**Patterns used:** ${ac.critique.better_example.patterns_used.length ? ac.critique.better_example.patterns_used.map((p) => `\`${p}\``).join(", ") : "—"}  
**Expected metric shift:**
${bullets(ac.critique.better_example.expected_metric_shift.map((s) => `\`${s.metric}\` ${s.direction === "up" ? "↑" : "↓"} — ${s.rationale}`))}

### Why the top Reels worked
${bullets(ac.critique.why_it_worked_vs_failed.top_reels.map((r) => `**${r.reel_id}** — ${r.because}${r.evidence.length ? `\n  ${r.evidence.map((e) => `  - ${ev(e)}`).join("\n")}` : ""}`))}

### Why the bottom Reels failed
${bullets(ac.critique.why_it_worked_vs_failed.bottom_reels.map((r) => `**${r.reel_id}** — ${r.because}${r.evidence.length ? `\n  ${r.evidence.map((e) => `  - ${ev(e)}`).join("\n")}` : ""}`))}

### What to change next
${ac.critique.what_to_change_next
  .sort((a, b) => a.priority - b.priority)
  .map((ch) => `${ch.priority}. ${ch.change} _(watch \`${ch.metric_to_watch}\`${ch.hard_rule ? `; fixes \`${ch.hard_rule}\`` : ""})_`)
  .join("\n")}
${ac.critique.niche_flags.length ? `\n### Niche flags\n${bullets(ac.critique.niche_flags.map((f) => `**${f.severity.toUpperCase()}** ${f.flag} — ${f.reason}`))}` : ""}
${ac.critique.data_gaps.length ? `\n<details><summary>Data gaps</summary>\n\n${bullets(ac.critique.data_gaps)}\n\n</details>` : ""}`
    : "_No account critique generated._";

  const reelIndex = `| # | Reel | date | band | views | p(views) | send | save | hold | replay | hard rules | flags |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n${ap.reels
    .map((r, i) => `| ${i + 1} | ${r.id} | ${r.timestamp.slice(0, 10)} | ${r.length_band} | ${fmt(r.views)} | ${r.views_percentile == null ? "—" : `p${Math.round(r.views_percentile)}`} | ${pct(r.send_rate)} | ${pct(r.save_rate)} | ${pct(r.hold_rate)} | ${fmt(r.replay_ratio, 2)} | ${r.hard_rules.length ? r.hard_rules.join(", ") : "—"} | ${[r.event_driven ? "event" : null, r.commercial_risk ? "commercial" : null].filter(Boolean).join(", ") || "—"} |`)
    .join("\n")}`;

  const hardTable = hardSummary.length
    ? `| rule | Reels affected | source |\n|---|---|---|\n${hardSummary.map(([r, n]) => `| \`${r}\` | ${n} | ${HARD_RULE_CITATIONS[r as HardRuleId] ?? ""} |`).join("\n")}`
    : "_No hard-rule violations detected._";

  const byViews = [...bundle.reels].sort((a, b) => (b.packet.metrics.views.value ?? 0) - (a.packet.metrics.views.value ?? 0));

  return `# Reels critique — @${ap.account.username}

Generated ${bundle.generated_at.slice(0, 19).replace("T", " ")} UTC · profile \`${bundle.profile}\` · model \`${ac?.model ?? bundle.reels.find((r) => r.critique)?.critique?.model ?? "—"}\`

**Account:** ${ap.account.follower_count.toLocaleString("en-US")} followers (tier ${ap.account.tier}) · ${ap.account.n_reels} Reels from ${ap.account.first} to ${ap.account.last} · ${fmt(ap.aggregates.reels_per_week, 1)} Reels/week · longest gap ${fmt(ap.aggregates.longest_gap_days, 0)} days  
**Medians:** views ${fmt(ap.aggregates.median_views)} · send rate ${pct(ap.aggregates.median_send_rate)} · save rate ${pct(ap.aggregates.median_save_rate)} · hold rate ${pct(ap.aggregates.median_hold_rate)} · replay ratio ${fmt(ap.aggregates.median_replay_ratio, 2)} · non-follower view share ${pct(ap.aggregates.non_follower_view_share)}${ap.metrics.follow_conversion.value != null ? ` · follow conversion ${pct(ap.metrics.follow_conversion.value)}` : ""}  
**Niche (${ap.niche.profile}):** season median views ${fmt(ap.niche.season_median_views)} vs off-season ${fmt(ap.niche.off_season_median_views)} · event-driven Reels: ${ap.niche.event_driven_reel_ids.length ? ap.niche.event_driven_reel_ids.join(", ") : "none"} · commercial-risk Reels: ${ap.niche.commercial_risk_reel_ids.length ? ap.niche.commercial_risk_reel_ids.join(", ") : "none"} · hostile-comment-heavy: ${ap.niche.hostile_heavy_reel_ids.length ? ap.niche.hostile_heavy_reel_ids.join(", ") : "none"}

> How to read this: every number in a critique is computed in code from your own data and cited as \`metric = value (pNN)\`, where pNN is the percentile against **your own** Reels, not an industry average. Hard rules are policy violations with primary-source citations. Percentiles are null when fewer than 5 comparable Reels exist.

## Hard-rule summary
${hardTable}

## Account critique
${accountBlock}

## Reel index (by views)
${reelIndex}

---

${byViews.map((entry, i) => reelSection(entry, i)).join("\n---\n\n")}
${ap.data_gaps.length ? `\n## Account data gaps\n${bullets(ap.data_gaps)}\n` : ""}
<sub>Percentile note: ${bundle.reels[0]?.packet.percentile_population_note ?? ""}</sub>
`;
}
