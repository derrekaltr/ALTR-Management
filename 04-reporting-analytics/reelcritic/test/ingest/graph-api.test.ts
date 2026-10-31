import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { GraphApiClient, RateLimiter } from "../../src/ingest/graph-api.js";

function fakeFetch(routes: Record<string, (u: URL) => unknown>): typeof fetch {
  return (async (input: RequestInfo | URL) => {
    const u = new URL(String(input));
    const key = Object.keys(routes).find((k) => u.pathname.endsWith(k) || u.href.includes(k));
    if (!key) return new Response(JSON.stringify({ error: { message: `no route ${u.pathname}` } }), { status: 404 });
    const body = routes[key]!(u);
    const status = (body as { __status?: number }).__status ?? 200;
    return new Response(JSON.stringify(body), { status });
  }) as typeof fetch;
}

describe("GraphApiClient", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "gapi-"));

  it("paginates media, filters REELS, respects since/limit", async () => {
    const page2 = "https://graph.facebook.com/v21.0/123/media?after=zzz";
    const f = fakeFetch({
      "/123/media": (u) =>
        u.searchParams.has("after")
          ? { data: [{ id: "3", media_product_type: "REELS", timestamp: "2025-01-01T00:00:00Z", permalink: "p3", media_type: "VIDEO" }] }
          : { data: [{ id: "1", media_product_type: "REELS", timestamp: "2025-03-01T00:00:00Z", permalink: "p1", media_type: "VIDEO" }, { id: "2", media_product_type: "FEED", timestamp: "2025-02-01T00:00:00Z", permalink: "p2", media_type: "IMAGE" }], paging: { next: page2 } },
    });
    const c = new GraphApiClient("tok", { fetchImpl: f, cacheDir: tmp });
    const all = [];
    for await (const m of c.listReels("123")) all.push(m.id);
    expect(all).toEqual(["1", "3"]);
    const since = [];
    for await (const m of c.listReels("123", { since: "2025-02-15" })) since.push(m.id);
    expect(since).toEqual(["1"]);
  });

  it("parses insights (values and total_value) and falls back without in-dev metrics on 400", async () => {
    let calls = 0;
    const f = fakeFetch({
      "/m1/insights": (u) => {
        calls++;
        if (u.searchParams.get("metric")!.includes("reels_skip_rate")) return { __status: 400, error: { message: "unsupported metric" } };
        return { data: [{ name: "views", values: [{ value: 1000 }] }, { name: "reach", total_value: { value: 800 } }, { name: "shares", values: [{ value: 12 }] }, { name: "ig_reels_avg_watch_time", values: [{ value: 9500 }] }] };
      },
    });
    const c = new GraphApiClient("tok", { fetchImpl: f, cacheDir: tmp });
    const i = await c.reelInsights("m1");
    expect(calls).toBe(2);
    expect(i.views).toBe(1000);
    expect(i.reach).toBe(800);
    expect(i.ig_reels_avg_watch_time_ms).toBe(9500);
    expect(i.reels_skip_rate).toBeNull();
    expect(i.total_interactions).toBe(12);
    // second call served from cache
    await c.reelInsights("m1");
    expect(calls).toBe(2);
  });

  it("account insights with follow_type breakdown", async () => {
    const f = fakeFetch({
      "/123/insights": (u) =>
        u.searchParams.get("metric") === "views"
          ? { data: [{ name: "views", total_value: { breakdowns: [{ results: [{ dimension_values: ["FOLLOWER"], value: 40 }, { dimension_values: ["NON_FOLLOWER"], value: 60 }] }] } }] }
          : { data: [{ name: "follows_and_unfollows", total_value: { value: 10, breakdowns: [{ results: [{ dimension_values: ["FOLLOWER"], value: 10 }, { dimension_values: ["UNFOLLOWER"], value: 3 }] }] } }] },
    });
    const c = new GraphApiClient("tok", { fetchImpl: f, cacheDir: tmp });
    const a = await c.accountInsights("123", 0, 86400 * 30);
    expect(a.views_by_follow_type).toEqual({ follower: 40, non_follower: 60 });
    expect(a.follows_and_unfollows).toEqual({ follows: 10, unfollows: 3, period_days: 30 });
  });

  it("rate limiter waits once the hourly budget is used", () => {
    let now = 1_000_000;
    const rl = new RateLimiter(path.join(tmp, "rl.json"), 3, () => now);
    expect(rl.reserve()).toBe(0);
    expect(rl.reserve()).toBe(0);
    expect(rl.reserve()).toBe(0);
    expect(rl.reserve()).toBeGreaterThan(0);
    now += 3_600_001 + 3_600_000;
    expect(rl.reserve()).toBe(0);
  });
});

describe("GraphApiClient multi-account discovery", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "gapi2-"));
  it("discoverAll paginates and resolveUsername matches case-insensitively", async () => {
    const f = fakeFetch({
      "/me/accounts": (u) =>
        u.searchParams.has("after")
          ? { data: [{ id: "p3", name: "Sarah H", instagram_business_account: { id: "ig3", username: "sarah.h44", followers_count: 1400000 } }] }
          : { data: [{ id: "p1", name: "Amber Haze", instagram_business_account: { id: "ig1", username: "amberhaze" } }, { id: "p2", name: "No IG" }], paging: { next: "https://graph.facebook.com/v21.0/me/accounts?after=x" } },
    });
    const c = new GraphApiClient("tok", { fetchImpl: f, cacheDir: tmp });
    const all = await c.discoverAll();
    expect(all.map((p) => p.page_name)).toEqual(["Amber Haze", "No IG", "Sarah H"]);
    expect(await c.resolveUsername("@Sarah.H44")).toEqual({ id: "ig3", username: "sarah.h44", page_name: "Sarah H" });
    expect(await c.resolveUsername("nobody")).toBeNull();
    expect((await c.discoverIgUserId())?.id).toBe("ig1");
  });
});

describe("GraphApiClient instagram-login mode", () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "gapi3-"));
  it("uses graph.instagram.com and /me for account + media", async () => {
    const seen: string[] = [];
    const f = (async (input: RequestInfo | URL) => {
      const u = new URL(String(input));
      seen.push(u.host + u.pathname);
      if (u.pathname.endsWith("/me")) return new Response(JSON.stringify({ id: "1", user_id: "17841400000000001", username: "sarah.h44", followers_count: 1400000 }));
      if (u.pathname.endsWith("/me/media")) return new Response(JSON.stringify({ data: [{ id: "m1", media_product_type: "REELS", timestamp: "2026-08-01T00:00:00Z", permalink: "p", media_type: "VIDEO" }] }));
      return new Response("{}", { status: 404 });
    }) as typeof fetch;
    const c = new GraphApiClient("tok", { fetchImpl: f, cacheDir: tmp, mode: "instagram" });
    const a = await c.account("ignored");
    expect(a).toEqual({ id: "17841400000000001", username: "sarah.h44", followers_count: 1400000 });
    const ids = [];
    for await (const m of c.listReels("ignored")) ids.push(m.id);
    expect(ids).toEqual(["m1"]);
    expect(seen[0]).toBe("graph.instagram.com/v25.0/me");
    expect(seen[1]).toBe("graph.instagram.com/v25.0/me/media");
  });
});
