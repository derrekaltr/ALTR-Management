import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { accountFromState, buildAuthUrl, completeAuthorization, ensureFreshToken, newState, parseCodeInput, readToken, tokenStatus, writeToken, type OAuthConfig, type Token } from "../../src/ingest/ig-login.js";
import { startCallbackServer } from "../../src/ingest/oauth-server.js";

const cfg: OAuthConfig = { appId: "123", appSecret: "sec", redirectUri: "http://localhost:0/callback", scopes: ["instagram_business_basic", "instagram_business_manage_insights"] };

function fakeFetch(): { f: typeof fetch; calls: string[] } {
  const calls: string[] = [];
  const f = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const u = new URL(String(input));
    calls.push(u.host + u.pathname);
    if (u.host === "api.instagram.com") {
      const body = String(init?.body);
      if (!/code=goodcode/.test(body)) return new Response(JSON.stringify({ error_message: "bad code" }), { status: 400 });
      return new Response(JSON.stringify({ data: [{ access_token: "short", user_id: 999, permissions: ["instagram_business_basic"] }] }), { status: 200 });
    }
    if (u.pathname === "/access_token") return new Response(JSON.stringify({ access_token: "long", token_type: "bearer", expires_in: 5184000 }), { status: 200 });
    if (u.pathname === "/refresh_access_token") return new Response(JSON.stringify({ access_token: "long2", token_type: "bearer", expires_in: 5184000 }), { status: 200 });
    if (u.pathname.endsWith("/me")) return new Response(JSON.stringify({ id: "999", user_id: "999", username: "sarah.h44", followers_count: 1400000 }), { status: 200 });
    return new Response("{}", { status: 404 });
  }) as typeof fetch;
  return { f, calls };
}

describe("instagram login oauth", () => {
  let cwd: string;
  beforeEach(() => {
    cwd = process.cwd();
    process.chdir(fs.mkdtempSync(path.join(os.tmpdir(), "iglogin-")));
  });
  afterEach(() => {
    process.chdir(cwd);
    delete process.env.REELCRITIC_ACCOUNT;
  });

  it("builds the authorize URL with the documented params and scopes", () => {
    const state = newState("sarah");
    const u = new URL(buildAuthUrl(cfg, state, { forceReauth: true }));
    expect(u.origin + u.pathname).toBe("https://www.instagram.com/oauth/authorize");
    expect(u.searchParams.get("client_id")).toBe("123");
    expect(u.searchParams.get("response_type")).toBe("code");
    expect(u.searchParams.get("scope")).toBe("instagram_business_basic,instagram_business_manage_insights");
    expect(u.searchParams.get("state")).toBe(state);
    expect(u.searchParams.get("force_reauth")).toBe("true");
    expect(accountFromState(state)).toBe("sarah");
  });

  it("parses a bare code or a pasted redirect URL and strips #_", () => {
    expect(parseCodeInput("abc#_")).toEqual({ code: "abc", state: null });
    expect(parseCodeInput("http://localhost:3000/callback?code=xyz&state=sarah.1#_")).toEqual({ code: "xyz", state: "sarah.1" });
  });

  it("completeAuthorization: code → short → long → /me, and persists per account", async () => {
    const { f, calls } = fakeFetch();
    const now = () => Date.parse("2026-08-26T00:00:00Z");
    const t = await completeAuthorization(cfg, "goodcode", { fetchImpl: f, now });
    expect(t.access_token).toBe("long");
    expect(t.username).toBe("sarah.h44");
    expect(t.expires_at).toBe("2026-10-25T00:00:00.000Z");
    expect(calls).toEqual(["api.instagram.com/oauth/access_token", "graph.instagram.com/access_token", "graph.instagram.com/v25.0/me"]);
    writeToken("sarah", t);
    expect(readToken("sarah")!.ig_user_id).toBe("999");
    expect(fs.existsSync(path.join(process.cwd(), "data", "sarah", "token.json"))).toBe(true);
  });

  it("rejects a bad code with the OAuth error body", async () => {
    const { f } = fakeFetch();
    await expect(completeAuthorization(cfg, "badcode", { fetchImpl: f })).rejects.toThrow(/Instagram OAuth 400/);
  });

  it("tokenStatus + ensureFreshToken refresh only when ≥24h old and <10 days left", async () => {
    const day = 86_400_000;
    const base = Date.parse("2026-08-26T00:00:00Z");
    const mk = (ageDays: number, leftDays: number): Token => ({ access_token: "long", token_type: "bearer", ig_user_id: "999", username: "s", permissions: [], obtained_at: new Date(base - ageDays * day).toISOString(), expires_at: new Date(base + leftDays * day).toISOString(), source: "instagram_login" });
    expect(tokenStatus(mk(0.5, 59), base)).toMatchObject({ refreshable: false, shouldRefresh: false });
    expect(tokenStatus(mk(30, 30), base)).toMatchObject({ refreshable: true, shouldRefresh: false });
    expect(tokenStatus(mk(55, 5), base)).toMatchObject({ refreshable: true, shouldRefresh: true });
    expect(tokenStatus(mk(70, -1), base).expired).toBe(true);
    const { f } = fakeFetch();
    writeToken("x", mk(55, 5));
    const nt = await ensureFreshToken("x", { fetchImpl: f, now: () => base });
    expect(nt!.access_token).toBe("long2");
    writeToken("y", mk(70, -1));
    await expect(ensureFreshToken("y", { fetchImpl: f, now: () => base })).rejects.toThrow(/expired/);
  });

  it("callback server: validates state, completes the flow, serves a friendly page", async () => {
    const { f } = fakeFetch();
    const state = newState("sarah");
    let got: Token | null = null;
    const server = await startCallbackServer({ cfg, port: 0, host: "127.0.0.1", expectedStates: new Set([state]), onToken: (_a, t) => (got = t), deps: { fetchImpl: f } });
    const port = (server.address() as { port: number }).port;
    const bad = await fetch(`http://127.0.0.1:${port}/callback?code=goodcode&state=nope`);
    expect(bad.status).toBe(400);
    const ok = await fetch(`http://127.0.0.1:${port}/callback?code=goodcode&state=${encodeURIComponent(state)}`);
    expect(ok.status).toBe(200);
    expect(await ok.text()).toContain("sarah.h44");
    expect(got!.username).toBe("sarah.h44");
    expect(readToken("sarah")!.access_token).toBe("long");
    server.close();
  });
});
