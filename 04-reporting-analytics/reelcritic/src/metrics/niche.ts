import type { Dataset, Reel } from "../ingest/types.js";
import type { Profile } from "../rubric/profile.js";
import { median } from "./percentiles.js";

export interface NicheReelAnnotation {
  in_season: boolean;
  season_label: string | null;
  event_driven: boolean;
  event_label: string | null;
  commercial_risk: { hit: boolean; matches: string[] };
  comment_sentiment: { admiring: number; hostile: number; neutral: number; sampled: number } | null;
  reminders: string[];
}

export interface NicheAccountAnnotation {
  profile: string;
  season_median_views: number | null;
  off_season_median_views: number | null;
  event_driven_reel_ids: string[];
  commercial_risk_reel_ids: string[];
  hostile_heavy_reel_ids: string[];
}

function monthDay(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
}

/** MM-DD window test; supports windows wrapping the year end (e.g. 12-20 → 01-10). */
export function inMonthDayWindow(md: string, start: string, end: string): boolean {
  if (start <= end) return md >= start && md <= end;
  return md >= start || md <= end;
}

export function inDateWindow(iso: string, start: string, end: string): boolean {
  const t = Date.parse(iso);
  return t >= Date.parse(`${start}T00:00:00Z`) && t <= Date.parse(`${end}T23:59:59Z`);
}

export function commercialRiskMatches(caption: string, patterns: string[]): string[] {
  const out: string[] = [];
  for (const p of patterns) {
    try {
      if (new RegExp(p, "i").test(caption)) out.push(p);
    } catch {
      if (caption.toLowerCase().includes(p.toLowerCase())) out.push(p);
    }
  }
  return out;
}

export function sentimentCounts(
  comments: Array<{ text: string }> | undefined,
  lexicon: Profile["sentiment_lexicon"],
): NicheReelAnnotation["comment_sentiment"] {
  if (!comments || comments.length === 0) return null;
  let admiring = 0;
  let hostile = 0;
  for (const c of comments) {
    const lc = c.text.toLowerCase();
    const a = lexicon.admiring.some((w) => lc.includes(w.toLowerCase()));
    const h = lexicon.hostile.some((w) => lc.includes(w.toLowerCase()));
    if (h) hostile++;
    else if (a) admiring++;
  }
  return { admiring, hostile, neutral: comments.length - admiring - hostile, sampled: comments.length };
}

export function annotateReel(reel: Reel, profile: Profile): NicheReelAnnotation {
  const md = monthDay(reel.timestamp);
  const season = profile.season_windows.find((w) => inMonthDayWindow(md, w.start, w.end));
  const eventWin = profile.event_windows.find((w) => inDateWindow(reel.timestamp, w.start, w.end));
  const lc = reel.caption.toLowerCase();
  const kw = profile.event_keywords.find((k) => lc.includes(k.toLowerCase()));
  const matches = commercialRiskMatches(reel.caption, profile.commercial_risk_patterns);
  return {
    in_season: !!season,
    season_label: season?.label ?? null,
    event_driven: !!eventWin || !!kw,
    event_label: eventWin?.label ?? (kw ? `keyword: "${kw}"` : null),
    commercial_risk: { hit: matches.length > 0, matches },
    comment_sentiment: sentimentCounts(reel.comments_sample, profile.sentiment_lexicon),
    reminders: matches.length > 0 ? profile.reminders : [],
  };
}

export function annotateAccount(ds: Dataset, profile: Profile, perReel: Map<string, NicheReelAnnotation>): NicheAccountAnnotation {
  const inSeason: number[] = [];
  const offSeason: number[] = [];
  const eventIds: string[] = [];
  const commercialIds: string[] = [];
  const hostileIds: string[] = [];
  for (const r of ds.reels) {
    const a = perReel.get(r.id)!;
    (a.in_season ? inSeason : offSeason).push(r.insights.views);
    if (a.event_driven) eventIds.push(r.id);
    if (a.commercial_risk.hit) commercialIds.push(r.id);
    const s = a.comment_sentiment;
    if (s && s.sampled >= 3 && s.hostile >= s.admiring && s.hostile > 0) hostileIds.push(r.id);
  }
  return {
    profile: profile.name,
    season_median_views: median(inSeason),
    off_season_median_views: median(offSeason),
    event_driven_reel_ids: eventIds,
    commercial_risk_reel_ids: commercialIds,
    hostile_heavy_reel_ids: hostileIds,
  };
}
