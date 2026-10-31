import fs from "node:fs";
import path from "node:path";
import { cacheDir, GRAPH_API_VERSION } from "../config.js";
import type { Account, Insights, Reel } from "./types.js";

const FB_BASE = `https://graph.facebook.com/${GRAPH_API_VERSION}`;
const IG_BASE = "https://graph.instagram.com/v25.0";

export interface RawMedia {
  id: string;
  caption?: string;
  media_type: string;
  media_product_type?: string;
  timestamp: string;
  permalink: string;
  thumbnail_url?: string;
  media_url?: string;
  like_count?: number;
  comments_count?: number;
}

export class GraphApiError extends Error {
  constructor(public status: number, public body: unknown) {
    super(`Graph API ${status}: ${JSON.stringify(body).slice(0, 300)}`);
  }
}

interface RateState {
  calls: number[];
}

/** Persisted sliding-window limiter (default 180 calls/hour; Meta allows ~200/hour per IG account). */
export class RateLimiter {
  constructor(private file: string, private maxPerHour = 180, private now: () => number = Date.now) {}
  private load(): RateState {
    try {
      return JSON.parse(fs.readFileSync(this.file, "utf8")) as RateState;
    } catch {
      return { calls: [] };
    }
  }
  private save(s: RateState) {
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    fs.writeFileSync(this.file, JSON.stringify(s));
  }
  /** Returns ms to wait before the next call (0 if allowed now) and records the call. */
  reserve(): number {
    const t = this.now();
    const s = this.load();
    s.calls = s.calls.filter((c) => t - c < 3_600_000);
    let wait = 0;
    if (s.calls.length >= this.maxPerHour) wait = s.calls[0]! + 3_600_000 - t;
    s.calls.push(t + wait);
    this.save(s);
    return wait;
  }
}

export interface GraphApiClientOptions {
  /** "facebook" = Graph API via Facebook Login (Pages); "instagram" = Instagram API with Instagram Login (creator tokens). */
  mode?: "facebook" | "instagram";
  fetchImpl?: typeof fetch;
  cacheDir?: string;
  cacheTtlMs?: number;
  maxPerHour?: number;
  sleep?: (ms: number) => Promise<void>;
}

const REEL_INSIGHT_METRICS = ["views", "reach", "likes", "comments", "shares", "saved", "reposts", "total_interactions", "profile_visits", "ig_reels_avg_watch_time"];
const REEL_INSIGHT_METRICS_DEV = ["ig_reels_video_view_total_time", "reels_skip_rate"];

export class GraphApiClient {
  private fetchImpl: typeof fetch;
  private cacheDir: string;
  private cacheTtl: number;
  private limiter: RateLimiter;
  private sleep: (ms: number) => Promise<void>;
  readonly mode: "facebook" | "instagram";
  private base: string;
  /** Set after Meta rejects the "in development" metrics once; later calls skip them. */
  private devMetricsUnsupported = false;

  constructor(private token: string, opts: GraphApiClientOptions = {}) {
    this.mode = opts.mode ?? "facebook";
    this.base = this.mode === "instagram" ? IG_BASE : FB_BASE;
    this.fetchImpl = opts.fetchImpl ?? fetch;
    this.cacheDir = opts.cacheDir ?? cacheDir();
    this.cacheTtl = opts.cacheTtlMs ?? 24 * 3_600_000;
    this.limiter = new RateLimiter(path.join(this.cacheDir, "ratelimit.json"), opts.maxPerHour ?? 180);
    this.sleep = opts.sleep ?? ((ms) => new Promise((r) => setTimeout(r, ms)));
  }

  async get<T = unknown>(pathname: string, params: Record<string, string | number | undefined> = {}, cacheKey?: string): Promise<T> {
    if (cacheKey) {
      const c = this.readCache<T>(cacheKey);
      if (c) return c;
    }
    const url = new URL(pathname.startsWith("http") ? pathname : `${this.base}${pathname}`);
    for (const [k, v] of Object.entries(params)) if (v !== undefined) url.searchParams.set(k, String(v));
    url.searchParams.set("access_token", this.token);
    const wait = this.limiter.reserve();
    if (wait > 0) await this.sleep(wait);
    const res = await this.fetchImpl(url);
    const body = (await res.json()) as T;
    if (!res.ok) throw new GraphApiError(res.status, body);
    if (cacheKey) this.writeCache(cacheKey, body);
    return body;
  }

  private cachePath(key: string) {
    return path.join(this.cacheDir, "media", `${key.replace(/[^a-zA-Z0-9_-]/g, "_")}.json`);
  }
  private readCache<T>(key: string): T | null {
    const f = this.cachePath(key);
    if (!fs.existsSync(f)) return null;
    try {
      const { fetched_at, body } = JSON.parse(fs.readFileSync(f, "utf8")) as { fetched_at: number; body: T };
      if (Date.now() - fetched_at > this.cacheTtl) return null;
      return body;
    } catch {
      return null;
    }
  }
  private writeCache(key: string, body: unknown) {
    const f = this.cachePath(key);
    fs.mkdirSync(path.dirname(f), { recursive: true });
    fs.writeFileSync(f, JSON.stringify({ fetched_at: Date.now(), body }));
  }

  async me(): Promise<{ id: string; name?: string }> {
    return this.get("/me", { fields: "id,name" });
  }

  /** Every Facebook Page this token manages, with its linked Instagram professional account (if any). Paginates. */
  async discoverAll(): Promise<Array<{ page_id: string; page_name: string; ig?: { id: string; username: string; followers_count?: number } }>> {
    const out: Array<{ page_id: string; page_name: string; ig?: { id: string; username: string; followers_count?: number } }> = [];
    let next: string | undefined;
    do {
      const res: { data: Array<{ id: string; name: string; instagram_business_account?: { id: string; username: string; followers_count?: number } }>; paging?: { next?: string } } = next
        ? await this.get(next)
        : await this.get("/me/accounts", { fields: "id,name,instagram_business_account{id,username,followers_count}", limit: 100 });
      for (const p of res.data) out.push({ page_id: p.id, page_name: p.name, ig: p.instagram_business_account });
      next = res.paging?.next;
    } while (next);
    return out;
  }

  /** First linked Instagram professional account (single-account convenience). */
  async discoverIgUserId(): Promise<{ id: string; username: string } | null> {
    const all = await this.discoverAll();
    return all.find((p) => p.ig)?.ig ?? null;
  }

  /** Resolve an Instagram username to its ig_user_id via the Pages this token manages. */
  async resolveUsername(username: string): Promise<{ id: string; username: string; page_name: string } | null> {
    const want = username.replace(/^@/, "").toLowerCase();
    const all = await this.discoverAll();
    const hit = all.find((p) => p.ig && p.ig.username.toLowerCase() === want);
    return hit?.ig ? { id: hit.ig.id, username: hit.ig.username, page_name: hit.page_name } : null;
  }

  async account(igUserId: string): Promise<{ id: string; username: string; followers_count: number }> {
    if (this.mode === "instagram") {
      const me = await this.get<{ id: string; user_id?: string; username: string; followers_count?: number }>("/me", { fields: "id,user_id,username,followers_count" });
      return { id: me.user_id ?? me.id, username: me.username, followers_count: me.followers_count ?? 0 };
    }
    return this.get(`/${igUserId}`, { fields: "id,username,followers_count" });
  }

  async *listReels(igUserId: string, opts: { since?: string; limit?: number } = {}): AsyncGenerator<RawMedia> {
    let next: string | undefined;
    let count = 0;
    const sinceT = opts.since ? Date.parse(opts.since) : null;
    do {
      const res: { data: RawMedia[]; paging?: { next?: string } } = next
        ? await this.get(next)
        : await this.get(`/${this.mode === "instagram" ? "me" : igUserId}/media`, {
            fields: "id,caption,media_type,media_product_type,timestamp,permalink,thumbnail_url,media_url,like_count,comments_count",
            limit: 50,
          });
      for (const m of res.data) {
        if (sinceT != null && Date.parse(m.timestamp) < sinceT) return;
        if (m.media_product_type !== "REELS") continue;
        yield m;
        if (opts.limit && ++count >= opts.limit) return;
      }
      next = res.paging?.next;
    } while (next);
  }

  /** Per-Reel insights; retries without the "in development" metrics if Meta rejects them. */
  async reelInsights(mediaId: string): Promise<Insights> {
    const parse = (body: { data: Array<{ name: string; values?: Array<{ value: number }>; total_value?: { value: number } }> }) => {
      const m: Record<string, number> = {};
      for (const d of body.data) m[d.name] = d.total_value?.value ?? d.values?.[0]?.value ?? 0;
      return m;
    };
    let m: Record<string, number>;
    const cachedFull = this.readCache<Parameters<typeof parse>[0]>(`insights_${mediaId}`);
    const cachedBase = this.readCache<Parameters<typeof parse>[0]>(`insights_base_${mediaId}`);
    if (cachedFull) m = parse(cachedFull);
    else if (cachedBase) m = parse(cachedBase);
    else if (this.devMetricsUnsupported) {
      m = parse(await this.get(`/${mediaId}/insights`, { metric: REEL_INSIGHT_METRICS.join(",") }, `insights_base_${mediaId}`));
    } else {
      try {
        m = parse(await this.get(`/${mediaId}/insights`, { metric: [...REEL_INSIGHT_METRICS, ...REEL_INSIGHT_METRICS_DEV].join(",") }, `insights_${mediaId}`));
      } catch (e) {
        if (!(e instanceof GraphApiError) || e.status !== 400) throw e;
        this.devMetricsUnsupported = true;
        m = parse(await this.get(`/${mediaId}/insights`, { metric: REEL_INSIGHT_METRICS.join(",") }, `insights_base_${mediaId}`));
      }
    }
    const skip = m.reels_skip_rate;
    return {
      views: m.views ?? 0,
      reach: m.reach ?? 0,
      likes: m.likes ?? 0,
      comments: m.comments ?? 0,
      shares: m.shares ?? 0,
      saved: m.saved ?? 0,
      reposts: m.reposts ?? 0,
      total_interactions: m.total_interactions ?? (m.likes ?? 0) + (m.comments ?? 0) + (m.shares ?? 0) + (m.saved ?? 0),
      profile_visits: m.profile_visits ?? 0,
      ig_reels_avg_watch_time_ms: m.ig_reels_avg_watch_time ?? null,
      reels_skip_rate: skip == null ? null : skip > 1 ? skip / 100 : skip,
      ig_reels_video_view_total_time_ms: m.ig_reels_video_view_total_time ?? null,
      follows: null, // not a per-media API metric; Business Suite export supplies it
    };
  }

  async comments(mediaId: string, limit = 50): Promise<Array<{ text: string; timestamp: string }>> {
    const res = await this.get<{ data: Array<{ text: string; timestamp: string }> }>(`/${mediaId}/comments`, { fields: "text,timestamp", limit }, `comments_${mediaId}`);
    return res.data ?? [];
  }

  /** Account-level: views by follow_type and follows/unfollows over [since, until]. */
  async accountInsights(igUserId: string, sinceUnix: number, untilUnix: number): Promise<Pick<Account, "views_by_follow_type" | "follows_and_unfollows">> {
    const out: Pick<Account, "views_by_follow_type" | "follows_and_unfollows"> = {};
    if (this.mode === "instagram") igUserId = "me";
    try {
      const v = await this.get<{ data: Array<{ name: string; total_value?: { breakdowns?: Array<{ results: Array<{ dimension_values: string[]; value: number }> }> } }> }>(`/${igUserId}/insights`, {
        metric: "views",
        period: "day",
        metric_type: "total_value",
        breakdown: "follow_type",
        since: sinceUnix,
        until: untilUnix,
      });
      const results = v.data[0]?.total_value?.breakdowns?.[0]?.results ?? [];
      let follower = 0;
      let non = 0;
      for (const r of results) {
        const dim = r.dimension_values[0]?.toUpperCase();
        if (dim === "FOLLOWER") follower += r.value;
        else if (dim === "NON_FOLLOWER") non += r.value;
      }
      if (results.length) out.views_by_follow_type = { follower, non_follower: non };
    } catch {
      /* optional */
    }
    try {
      const f = await this.get<{ data: Array<{ name: string; total_value?: { value: number; breakdowns?: Array<{ results: Array<{ dimension_values: string[]; value: number }> }> } }> }>(`/${igUserId}/insights`, {
        metric: "follows_and_unfollows",
        period: "day",
        metric_type: "total_value",
        breakdown: "follow_type",
        since: sinceUnix,
        until: untilUnix,
      });
      const results = f.data[0]?.total_value?.breakdowns?.[0]?.results ?? [];
      let follows = 0;
      let unfollows = 0;
      for (const r of results) {
        const dim = r.dimension_values[0]?.toUpperCase() ?? "";
        if (dim.includes("UNFOLLOW")) unfollows += r.value;
        else follows += r.value;
      }
      const total = f.data[0]?.total_value?.value;
      if (results.length || total != null) out.follows_and_unfollows = { follows: results.length ? follows : (total ?? 0), unfollows, period_days: Math.round((untilUnix - sinceUnix) / 86_400) };
    } catch {
      /* optional */
    }
    return out;
  }

  static async refreshLongLivedToken(appId: string, appSecret: string, token: string, fetchImpl: typeof fetch = fetch): Promise<{ access_token: string; expires_in?: number }> {
    const url = new URL(`${FB_BASE}/oauth/access_token`);
    url.searchParams.set("grant_type", "fb_exchange_token");
    url.searchParams.set("client_id", appId);
    url.searchParams.set("client_secret", appSecret);
    url.searchParams.set("fb_exchange_token", token);
    const res = await fetchImpl(url);
    const body = (await res.json()) as { access_token: string; expires_in?: number };
    if (!res.ok) throw new GraphApiError(res.status, body);
    return body;
  }
}

export function rawMediaToReel(m: RawMedia, insights: Insights): Reel {
  return {
    id: m.id,
    permalink: m.permalink,
    timestamp: m.timestamp,
    caption: m.caption ?? "",
    media_url: m.media_url,
    thumbnail_url: m.thumbnail_url,
    duration_s: null,
    duration_source: "unknown",
    insights,
    source: "graph-api",
  };
}
