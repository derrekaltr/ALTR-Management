import fs from "node:fs";
import { parseCsv } from "./csv.js";
import type { Insights, Reel } from "./types.js";

/**
 * Meta Business Suite → Insights → Content → Export.
 * Column names are NOT documented by Meta and vary by locale/version; we map by alias and log what we could not map.
 */
export const HEADER_ALIASES: Record<string, string[]> = {
  id: ["Post ID", "Media ID", "ID", "Content ID"],
  permalink: ["Permalink", "Post link", "Link", "URL"],
  timestamp: ["Publish time", "Date", "Published", "Created", "Post time", "Publish Time", "Date published"],
  caption: ["Description", "Caption", "Title", "Text"],
  platform: ["Platform", "Account", "Channel"],
  media_product_type: ["Post type", "Content type", "Type", "Format", "Media type"],
  duration_s: ["Duration (sec)", "Duration", "Video length", "Length (s)"],
  views: ["Views", "Plays", "Video views", "Reel plays"],
  reach: ["Reach", "Accounts reached", "Viewers"],
  likes: ["Likes", "Reactions", "Likes and reactions"],
  comments: ["Comments"],
  shares: ["Shares", "Sends"],
  saved: ["Saves", "Saved"],
  reposts: ["Reposts"],
  total_interactions: ["Total interactions", "Interactions", "Engagement"],
  profile_visits: ["Profile visits", "Profile Visits"],
  ig_reels_avg_watch_time_ms: ["Average watch time (ms)", "Avg watch time (ms)"],
  avg_watch_time_s: ["Average watch time", "Avg watch time", "Average watch time (sec)", "Avg. watch time (s)", "Video average play time", "Average play time"],
  total_watch_time: ["Watch time", "Total watch time", "Video watch time"],
  follows: ["Follows", "New follows", "Follows from post"],
  reels_skip_rate: ["Skip rate", "Skip rate (%)"],
};

const norm = (s: string) => s.trim().toLowerCase().replace(/\s+/g, " ");

export function mapHeaders(headers: string[]): { index: Record<string, number>; unmapped: string[] } {
  const index: Record<string, number> = {};
  const used = new Set<number>();
  for (const [key, aliases] of Object.entries(HEADER_ALIASES)) {
    const wanted = aliases.map(norm);
    const i = headers.findIndex((h, idx) => !used.has(idx) && wanted.includes(norm(h)));
    if (i >= 0) {
      index[key] = i;
      used.add(i);
    }
  }
  const unmapped = headers.filter((_, i) => !used.has(i));
  return { index, unmapped };
}

function num(s: string | undefined): number | null {
  if (s == null) return null;
  const t = s.replace(/[,%\s]/g, "");
  if (t === "" || t === "-" || t === "—") return null;
  const n = Number(t);
  return Number.isFinite(n) ? n : null;
}

/** Durations may be "12.3", "0:12", "1:02:03", "12s", "1m 2s" → seconds. */
export function durationToSeconds(s: string | undefined): number | null {
  if (s == null) return null;
  const t = s.trim();
  if (t === "" || t === "-" || t === "—") return null;
  if (/^\d+(\.\d+)?$/.test(t)) return Number(t);
  const hms = t.match(/^(\d+):(\d{1,2})(?::(\d{1,2}))?$/);
  if (hms) return hms[3] != null ? Number(hms[1]) * 3600 + Number(hms[2]) * 60 + Number(hms[3]) : Number(hms[1]) * 60 + Number(hms[2]);
  let total = 0;
  let matched = false;
  for (const m of t.matchAll(/(\d+(?:\.\d+)?)\s*(h|m|s)\b/gi)) {
    matched = true;
    const v = Number(m[1]);
    total += m[2]!.toLowerCase() === "h" ? v * 3600 : m[2]!.toLowerCase() === "m" ? v * 60 : v;
  }
  return matched ? total : null;
}

function toIso(s: string | undefined): string | null {
  if (!s) return null;
  const t = Date.parse(s);
  return Number.isFinite(t) ? new Date(t).toISOString() : null;
}

export interface ImportResult {
  reels: Partial<Reel>[];
  unmapped_headers: string[];
  skipped_rows: number;
}

export function importBusinessSuiteCsv(file: string): ImportResult {
  const rows = parseCsv(fs.readFileSync(file, "utf8"));
  if (rows.length < 2) return { reels: [], unmapped_headers: rows[0] ?? [], skipped_rows: 0 };
  const headers = rows[0]!;
  const { index, unmapped } = mapHeaders(headers);
  const get = (r: string[], key: string) => (index[key] == null ? undefined : r[index[key]!]);

  const reels: Partial<Reel>[] = [];
  let skipped = 0;
  for (const r of rows.slice(1)) {
    const platform = get(r, "platform")?.toLowerCase() ?? "";
    if (platform && !/instagram|ig\b/.test(platform)) {
      skipped++;
      continue;
    }
    const type = get(r, "media_product_type")?.toLowerCase() ?? "";
    if (type && !/reel/.test(type)) {
      skipped++;
      continue;
    }
    const permalink = get(r, "permalink");
    const id = get(r, "id") ?? permalink;
    const ts = toIso(get(r, "timestamp"));
    if (!id || !ts) {
      skipped++;
      continue;
    }
    const views = num(get(r, "views"));
    const reach = num(get(r, "reach"));
    if (views == null || reach == null) {
      skipped++;
      continue;
    }
    const likes = num(get(r, "likes")) ?? 0;
    const comments = num(get(r, "comments")) ?? 0;
    const shares = num(get(r, "shares")) ?? 0;
    const saved = num(get(r, "saved")) ?? 0;
    const avgS = durationToSeconds(get(r, "avg_watch_time_s"));
    const avgMs = num(get(r, "ig_reels_avg_watch_time_ms")) ?? (avgS == null ? null : Math.round(avgS * 1000));
    const totalS = durationToSeconds(get(r, "total_watch_time"));
    const skipRaw = num(get(r, "reels_skip_rate"));
    const insights: Insights = {
      views,
      reach,
      likes,
      comments,
      shares,
      saved,
      reposts: num(get(r, "reposts")) ?? 0,
      total_interactions: num(get(r, "total_interactions")) ?? likes + comments + shares + saved,
      profile_visits: num(get(r, "profile_visits")) ?? 0,
      ig_reels_avg_watch_time_ms: avgMs,
      reels_skip_rate: skipRaw == null ? null : skipRaw > 1 ? skipRaw / 100 : skipRaw,
      ig_reels_video_view_total_time_ms: totalS == null ? null : Math.round(totalS * 1000),
      follows: num(get(r, "follows")),
    };
    const dur = num(get(r, "duration_s"));
    reels.push({
      id,
      permalink: permalink ?? `bs:${id}`,
      timestamp: ts,
      caption: get(r, "caption") ?? "",
      duration_s: dur,
      duration_source: dur == null ? "unknown" : "user",
      insights,
      source: "business-suite",
    });
  }
  return { reels, unmapped_headers: unmapped, skipped_rows: skipped };
}
