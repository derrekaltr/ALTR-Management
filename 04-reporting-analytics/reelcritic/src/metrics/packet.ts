import type { Dataset, Reel } from "../ingest/types.js";
import type { Profile } from "../rubric/profile.js";
import { tierFor } from "../rubric/benchmarks.js";
import { computeRatios, safeDiv } from "./ratios.js";
import { percentileOf, median, round1 } from "./percentiles.js";
import { lengthBand, completionVsBand, type LengthBand } from "./length-band.js";
import { classifyCurve, type CurveResult } from "./curve.js";
import { checkHardRules, countHashtags, type HardRuleHit } from "./hard-rules.js";
import { annotateReel, annotateAccount, type NicheReelAnnotation, type NicheAccountAnnotation } from "./niche.js";
import { selectExamples, type FailureMode } from "../rubric/examples.js";

/** The ONLY metric names Claude may cite. Drives the Zod enum and evidence validation. */
export const METRIC_KEYS = [
  "views",
  "reach",
  "likes",
  "comments",
  "shares",
  "saved",
  "reposts",
  "total_interactions",
  "profile_visits",
  "avg_watch_time_s",
  "duration_s",
  "replay_ratio",
  "send_rate",
  "save_rate",
  "comment_rate",
  "like_rate",
  "engagement_rate",
  "hold_rate",
  "hook_rate",
  "completion_vs_band_delta",
  "non_follower_share",
  "views_vs_tier_ratio",
  "hashtag_count",
  "follow_conversion",
] as const;
export type MetricKey = (typeof METRIC_KEYS)[number];

export interface MetricCell {
  value: number | null;
  percentile: number | null; // vs. this creator's own history
  n: number; // population size used
}
export type MetricTable = Record<MetricKey, MetricCell>;

export interface ReelPacket {
  reel: {
    id: string;
    permalink: string;
    timestamp: string;
    caption: string;
    duration_s: number | null;
    duration_source: Reel["duration_source"];
    length_band: LengthBand;
    hashtag_count: number;
  };
  metrics: MetricTable;
  hard_rules: HardRuleHit[];
  curve: CurveResult | null;
  screenshot: {
    skip_rate_pct: number | null;
    views_by_source: NonNullable<Reel["screenshot"]>["views_by_source"] | null;
    follower_split: NonNullable<Reel["screenshot"]>["follower_split"] | null;
  } | null;
  niche: NicheReelAnnotation;
  benchmark: { tier: string; tier_avg_views: number; ratio_to_tier: number | null };
  comments_sample: string[];
  /** Deterministic failure-mode tags derived from hard rules, curve shape and own-history percentiles. */
  failure_modes: FailureMode[];
  /** Example-library pattern ids most relevant to this Reel (Claude must cite from these or the full library). */
  suggested_pattern_ids: string[];
  data_gaps: string[];
  percentile_population_note: string;
}

/** Derive failure-mode tags from the computed signals. Percentile thresholds are relative to the creator's own history. */
export function deriveFailureModes(table: MetricTable, hard: HardRuleHit[], curve: CurveResult | null, niche: NicheReelAnnotation, band: LengthBand, caption: string): FailureMode[] {
  const out = new Set<FailureMode>();
  const low = (k: MetricKey, p = 35) => table[k].percentile != null && table[k].percentile! <= p;
  for (const h of hard) {
    if (h.rule === "hashtags_gt_5") out.add("hashtag_stuffing");
    if (h.rule === "engagement_bait") out.add("engagement_bait");
    if (h.rule === "length_gt_3min") out.add("too_long");
    if (h.rule === "majority_text") out.add("muted_autoplay_unreadable");
  }
  if (curve?.shape === "cliff") out.add("cliff"), out.add("weak_hook");
  if (curve && curve.shape !== "cliff" && curve.mid_slope != null && curve.mid_slope < -0.5 && !curve.rewatch_bump) out.add("mid_sag");
  if (curve && !curve.rewatch_bump && curve.shape !== "plateau_loop") out.add("no_payoff");
  if (table.hook_rate.value != null && (low("hook_rate") || table.hook_rate.value < 0.5)) out.add("weak_hook");
  if (low("hold_rate")) out.add(band === "60+" || band === "over-3min" ? "too_long" : "mid_sag");
  if (table.replay_ratio.value != null && table.replay_ratio.value <= 1.05 && (band === "7-15" || band === "15-30")) out.add("no_loop");
  if (low("send_rate")) out.add("low_sends");
  if (low("save_rate")) out.add("low_saves");
  if (low("comment_rate")) out.add("low_comments"), out.add("no_conversation_seed");
  if (caption.trim().length === 0 || /#\w+/.test(caption) && caption.replace(/#\w+/g, "").trim().length < 10) out.add("caption_dead");
  if (niche.commercial_risk.hit) out.add("commercial_signal");
  const s = niche.comment_sentiment;
  if (s && s.sampled >= 3 && s.hostile >= s.admiring && s.hostile > 0) out.add("hostile_comments");
  if (out.size === 0 && table.views.percentile != null && table.views.percentile < 50) out.add("no_premise");
  return [...out];
}

export interface AccountReelRow {
  id: string;
  timestamp: string;
  caption_short: string;
  views: number;
  views_percentile: number | null;
  send_rate: number | null;
  save_rate: number | null;
  hold_rate: number | null;
  replay_ratio: number | null;
  hard_rules: string[];
  event_driven: boolean;
  commercial_risk: boolean;
  length_band: LengthBand;
}

export interface AccountPacket {
  account: { username: string; follower_count: number; tier: string; n_reels: number; first: string; last: string };
  metrics: MetricTable; // medians across reels (percentile null) + follow_conversion
  aggregates: {
    median_views: number | null;
    median_send_rate: number | null;
    median_save_rate: number | null;
    median_hold_rate: number | null;
    median_replay_ratio: number | null;
    non_follower_view_share: number | null; // account-level API breakdown
    reels_per_week: number | null;
    longest_gap_days: number | null;
  };
  reels: AccountReelRow[]; // sorted by views desc
  top_ids: string[];
  bottom_ids: string[];
  hard_rule_summary: Record<string, number>;
  niche: NicheAccountAnnotation;
  data_gaps: string[];
}

interface RawRow {
  reel: Reel;
  values: Record<MetricKey, number | null>;
  band: LengthBand;
  niche: NicheReelAnnotation;
}

function rawValues(reel: Reel, ds: Dataset): Record<MetricKey, number | null> {
  const r = computeRatios(reel);
  const band = lengthBand(reel.duration_s);
  const tier = tierFor(ds.account.follower_count);
  return {
    views: reel.insights.views,
    reach: reel.insights.reach,
    likes: reel.insights.likes,
    comments: reel.insights.comments,
    shares: reel.insights.shares,
    saved: reel.insights.saved,
    reposts: reel.insights.reposts,
    total_interactions: reel.insights.total_interactions,
    profile_visits: reel.insights.profile_visits,
    avg_watch_time_s: r.avg_watch_time_s,
    duration_s: reel.duration_s,
    replay_ratio: r.replay_ratio,
    send_rate: r.send_rate,
    save_rate: r.save_rate,
    comment_rate: r.comment_rate,
    like_rate: r.like_rate,
    engagement_rate: r.engagement_rate,
    hold_rate: r.hold_rate,
    hook_rate: r.hook_rate,
    completion_vs_band_delta: completionVsBand(r.hold_rate, band),
    non_follower_share: r.non_follower_share,
    views_vs_tier_ratio: tier.avg_views_per_reel > 0 ? reel.insights.views / tier.avg_views_per_reel : null,
    hashtag_count: countHashtags(reel.caption),
    follow_conversion: reel.insights.follows == null ? null : safeDiv(reel.insights.follows, reel.insights.reach),
  };
}

function round(v: number | null): number | null {
  if (v == null) return null;
  return Math.abs(v) >= 100 ? Math.round(v) : Math.round(v * 10000) / 10000;
}

export function buildRows(ds: Dataset, profile: Profile): RawRow[] {
  return ds.reels.map((reel) => ({
    reel,
    values: rawValues(reel, ds),
    band: lengthBand(reel.duration_s),
    niche: annotateReel(reel, profile),
  }));
}

/** Percentile population: all non-event-driven reels (the reel itself included, mid-rank). */
function metricTable(row: RawRow, rows: RawRow[]): { table: MetricTable; note: string } {
  const pop = rows.filter((r) => !r.niche.event_driven);
  const table = {} as MetricTable;
  for (const k of METRIC_KEYS) {
    const others = pop.map((r) => r.values[k]);
    const value = round(row.values[k]);
    const p = percentileOf(row.values[k], others);
    table[k] = { value, percentile: p.percentile, n: p.n };
  }
  const excluded = rows.length - pop.length;
  return {
    table,
    note: `Percentiles are mid-rank vs. this creator's own ${pop.length} non-event-driven Reels${excluded ? ` (${excluded} event-driven Reels excluded from the population)` : ""}; null when the population is < 5 or the metric is missing.`,
  };
}

export function buildReelPacket(reel: Reel, ds: Dataset, profile: Profile, rows: RawRow[] = buildRows(ds, profile)): ReelPacket {
  const row = rows.find((r) => r.reel.id === reel.id) ?? { reel, values: rawValues(reel, ds), band: lengthBand(reel.duration_s), niche: annotateReel(reel, profile) };
  const { table, note } = metricTable(row, rows);
  const tier = tierFor(ds.account.follower_count);
  const hard = checkHardRules(reel, ds.reels);
  const curve = reel.screenshot && reel.screenshot.retention_curve.length >= 3 ? classifyCurve(reel.screenshot.retention_curve) : null;

  const gaps: string[] = [];
  if (reel.duration_s == null) gaps.push("duration_s unknown → hold_rate and completion_vs_band_delta unavailable (add data/overrides.json or a screenshot)");
  if (reel.insights.ig_reels_avg_watch_time_ms == null) gaps.push("ig_reels_avg_watch_time missing from API");
  if (reel.insights.reels_skip_rate == null && reel.screenshot?.skip_rate_pct == null) gaps.push("skip rate / hook_rate unavailable (Meta marks reels_skip_rate 'in development'; upload an Insights screenshot)");
  if (!curve) gaps.push("no retention curve (in-app only; upload the Reel's retention chart screenshot)");
  if (!reel.screenshot?.follower_split) gaps.push("per-Reel follower vs non-follower split unavailable (in-app only)");
  if (!reel.comments_sample || reel.comments_sample.length === 0) gaps.push("no comment sample");
  for (const k of METRIC_KEYS) {
    const c = table[k];
    if (c.value != null && c.percentile == null && c.n < 5 && k !== "follow_conversion") {
      gaps.push(`percentiles unavailable: only ${c.n} comparable Reels in history (need >= 5)`);
      break;
    }
  }

  // hook_rate from screenshot if API skip rate absent
  if (table.hook_rate.value == null && reel.screenshot?.skip_rate_pct != null) {
    table.hook_rate = { value: round(1 - reel.screenshot.skip_rate_pct / 100), percentile: null, n: 0 };
  }

  const failureModes = deriveFailureModes(table, hard, curve, row.niche, row.band, reel.caption);
  const valueGuess = (() => {
    const p = (k: MetricKey) => table[k].percentile ?? -1;
    const best = (["send_rate", "save_rate", "comment_rate"] as MetricKey[]).sort((a, b) => p(b) - p(a))[0]!;
    if (p(best) < 50) return null;
    return best === "send_rate" ? "entertaining" : best === "save_rate" ? "useful" : "provocative";
  })();
  const suggested = selectExamples(failureModes, row.band, valueGuess).map((e) => e.id);

  return {
    reel: {
      id: reel.id,
      permalink: reel.permalink,
      timestamp: reel.timestamp,
      caption: reel.caption,
      duration_s: reel.duration_s,
      duration_source: reel.duration_source,
      length_band: row.band,
      hashtag_count: countHashtags(reel.caption),
    },
    metrics: table,
    hard_rules: hard,
    curve,
    screenshot: reel.screenshot
      ? { skip_rate_pct: reel.screenshot.skip_rate_pct, views_by_source: reel.screenshot.views_by_source, follower_split: reel.screenshot.follower_split }
      : null,
    niche: row.niche,
    benchmark: { tier: tier.key, tier_avg_views: tier.avg_views_per_reel, ratio_to_tier: round(table.views_vs_tier_ratio.value) },
    comments_sample: (reel.comments_sample ?? []).slice(0, 25).map((c) => c.text),
    failure_modes: failureModes,
    suggested_pattern_ids: suggested,
    data_gaps: gaps,
    percentile_population_note: note,
  };
}

export function buildAccountPacket(ds: Dataset, profile: Profile, rows: RawRow[] = buildRows(ds, profile)): AccountPacket {
  const tier = tierFor(ds.account.follower_count);
  const perReelNiche = new Map(rows.map((r) => [r.reel.id, r.niche] as const));
  const niche = annotateAccount(ds, profile, perReelNiche);
  const viewsPop = rows.filter((r) => !r.niche.event_driven).map((r) => r.values.views);

  const med = (k: MetricKey) => median(rows.map((r) => r.values[k]).filter((v): v is number => v != null));
  const table = {} as MetricTable;
  for (const k of METRIC_KEYS) table[k] = { value: round(med(k)), percentile: null, n: rows.filter((r) => r.values[k] != null).length };

  // account-level follow conversion: follows / total reach in window (own-baseline only)
  const fu = ds.account.follows_and_unfollows;
  if (fu) {
    const totalReach = rows.reduce((s, r) => s + r.reel.insights.reach, 0);
    table.follow_conversion = { value: round(totalReach > 0 ? fu.follows / totalReach : null), percentile: null, n: rows.length };
  }

  const vf = ds.account.views_by_follow_type;
  const nonFollowerShare = vf && vf.follower + vf.non_follower > 0 ? round(vf.non_follower / (vf.follower + vf.non_follower)) : null;
  table.non_follower_share = { value: nonFollowerShare, percentile: null, n: vf ? 1 : 0 };

  const sorted = [...rows].sort((a, b) => b.values.views! - a.values.views!);
  const times = rows.map((r) => Date.parse(r.reel.timestamp)).sort((a, b) => a - b);
  let longestGap: number | null = null;
  for (let i = 1; i < times.length; i++) longestGap = Math.max(longestGap ?? 0, (times[i]! - times[i - 1]!) / 86_400_000);
  const spanWeeks = times.length > 1 ? (times[times.length - 1]! - times[0]!) / (7 * 86_400_000) : null;

  const reelRows: AccountReelRow[] = sorted.map((r) => ({
    id: r.reel.id,
    timestamp: r.reel.timestamp,
    caption_short: r.reel.caption.slice(0, 80).replace(/\s+/g, " "),
    views: r.reel.insights.views,
    views_percentile: percentileOf(r.values.views, viewsPop).percentile,
    send_rate: round(r.values.send_rate),
    save_rate: round(r.values.save_rate),
    hold_rate: round(r.values.hold_rate),
    replay_ratio: round(r.values.replay_ratio),
    hard_rules: checkHardRules(r.reel, ds.reels).map((h) => h.rule),
    event_driven: r.niche.event_driven,
    commercial_risk: r.niche.commercial_risk.hit,
    length_band: r.band,
  }));

  const hardSummary: Record<string, number> = {};
  for (const rr of reelRows) for (const h of rr.hard_rules) hardSummary[h] = (hardSummary[h] ?? 0) + 1;

  const k = Math.max(1, Math.min(5, Math.floor(rows.length / 4)));
  const gaps: string[] = [];
  if (rows.length < 10) gaps.push(`only ${rows.length} Reels — account-level conclusions are weak; post more before changing strategy`);
  if (!vf) gaps.push("account-level follower/non-follower view split not pulled");
  if (!fu) gaps.push("follows/unfollows not pulled → follow_conversion unavailable");
  if (rows.every((r) => r.values.duration_s == null)) gaps.push("no durations known → hold_rate unavailable for every Reel");

  return {
    account: {
      username: ds.account.username,
      follower_count: ds.account.follower_count,
      tier: tier.key,
      n_reels: rows.length,
      first: rows.length ? new Date(times[0]!).toISOString().slice(0, 10) : "",
      last: rows.length ? new Date(times[times.length - 1]!).toISOString().slice(0, 10) : "",
    },
    metrics: table,
    aggregates: {
      median_views: med("views"),
      median_send_rate: round(med("send_rate")),
      median_save_rate: round(med("save_rate")),
      median_hold_rate: round(med("hold_rate")),
      median_replay_ratio: round(med("replay_ratio")),
      non_follower_view_share: nonFollowerShare,
      reels_per_week: spanWeeks && spanWeeks > 0 ? round1(rows.length / spanWeeks) : null,
      longest_gap_days: longestGap == null ? null : round1(longestGap),
    },
    reels: reelRows,
    top_ids: reelRows.slice(0, k).map((r) => r.id),
    bottom_ids: reelRows.slice(-k).map((r) => r.id),
    hard_rule_summary: hardSummary,
    niche,
    data_gaps: gaps,
  };
}
