/**
 * Instagram API with Instagram Login — "Business Login for Instagram".
 * Creators authorize once on their own device; no Facebook Page, no shared passwords.
 *
 * Verified 2026-08-26 against Meta docs:
 *  - authorize:   https://www.instagram.com/oauth/authorize?client_id&redirect_uri&response_type=code&scope&state
 *  - exchange:    POST https://api.instagram.com/oauth/access_token  (form: client_id, client_secret, grant_type=authorization_code, redirect_uri, code)
 *                 → { data: [{ access_token, user_id, permissions }] }   (short-lived, 1 hour)
 *  - long-lived:  GET https://graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret&access_token → { access_token, token_type, expires_in }
 *  - refresh:     GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token   (token must be ≥ 24 h old and unexpired)
 *  - API base:    https://graph.instagram.com/v25.0/  ; /me?fields=user_id,username,followers_count,...
 */
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { z } from "zod";
import { dataDir, env } from "../config.js";

export const IG_API_BASE = "https://graph.instagram.com/v25.0";
export const DEFAULT_SCOPES = ["instagram_business_basic", "instagram_business_manage_insights"];

export const TokenSchema = z.object({
  access_token: z.string(),
  token_type: z.literal("bearer").default("bearer"),
  ig_user_id: z.string(),
  username: z.string().nullable().default(null),
  permissions: z.array(z.string()).default([]),
  obtained_at: z.string(), // ISO
  expires_at: z.string(), // ISO
  source: z.literal("instagram_login").default("instagram_login"),
});
export type Token = z.infer<typeof TokenSchema>;

export interface OAuthConfig {
  appId: string;
  appSecret: string;
  redirectUri: string;
  scopes?: string[];
}

export function oauthConfigFromEnv(overrides: Partial<OAuthConfig> = {}): OAuthConfig {
  const appId = overrides.appId ?? env("IG_APP_ID");
  const appSecret = overrides.appSecret ?? env("IG_APP_SECRET");
  const redirectUri = overrides.redirectUri ?? env("IG_REDIRECT_URI") ?? "http://localhost:3000/callback";
  if (!appId || !appSecret) throw new Error("IG_APP_ID and IG_APP_SECRET are required (Meta app → Instagram → API setup with Instagram business login). Put them in .env.");
  const scopesEnv = env("IG_SCOPES");
  return { appId, appSecret, redirectUri, scopes: overrides.scopes ?? (scopesEnv ? scopesEnv.split(",").map((s) => s.trim()) : DEFAULT_SCOPES) };
}

export function newState(account: string): string {
  return `${account}.${crypto.randomBytes(12).toString("base64url")}`;
}
export function accountFromState(state: string): string {
  return state.split(".")[0] ?? "";
}

export function buildAuthUrl(cfg: OAuthConfig, state: string, opts: { forceReauth?: boolean } = {}): string {
  const u = new URL("https://www.instagram.com/oauth/authorize");
  u.searchParams.set("client_id", cfg.appId);
  u.searchParams.set("redirect_uri", cfg.redirectUri);
  u.searchParams.set("response_type", "code");
  u.searchParams.set("scope", (cfg.scopes ?? DEFAULT_SCOPES).join(","));
  u.searchParams.set("state", state);
  u.searchParams.set("enable_fb_login", "0");
  if (opts.forceReauth) u.searchParams.set("force_reauth", "true");
  return u.toString();
}

/** Accepts a bare code or a full redirect URL (creators often paste the whole thing). Strips Meta's trailing "#_". */
export function parseCodeInput(input: string): { code: string; state: string | null } {
  const t = input.trim();
  if (/^https?:\/\//i.test(t)) {
    const u = new URL(t);
    const code = u.searchParams.get("code");
    if (!code) throw new Error("No ?code= in that URL");
    return { code: code.replace(/#_$/, ""), state: u.searchParams.get("state") };
  }
  return { code: t.replace(/#_$/, ""), state: null };
}

export class IgOAuthError extends Error {
  constructor(public status: number, public body: unknown) {
    super(`Instagram OAuth ${status}: ${JSON.stringify(body).slice(0, 300)}`);
  }
}

export interface IgOAuthDeps {
  fetchImpl?: typeof fetch;
  now?: () => number;
}

export async function exchangeCode(cfg: OAuthConfig, code: string, deps: IgOAuthDeps = {}): Promise<{ access_token: string; user_id: string; permissions: string[] }> {
  const f = deps.fetchImpl ?? fetch;
  const body = new URLSearchParams({ client_id: cfg.appId, client_secret: cfg.appSecret, grant_type: "authorization_code", redirect_uri: cfg.redirectUri, code });
  const res = await f("https://api.instagram.com/oauth/access_token", { method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" }, body });
  const json = (await res.json()) as { data?: Array<{ access_token: string; user_id: string | number; permissions?: string[] | string }>; access_token?: string; user_id?: string | number; permissions?: string[] | string };
  if (!res.ok) throw new IgOAuthError(res.status, json);
  const d = json.data?.[0] ?? json;
  if (!d.access_token) throw new IgOAuthError(res.status, json);
  const perms = Array.isArray(d.permissions) ? d.permissions : typeof d.permissions === "string" ? d.permissions.split(",") : [];
  return { access_token: d.access_token, user_id: String(d.user_id), permissions: perms };
}

export async function exchangeLongLived(cfg: OAuthConfig, shortToken: string, deps: IgOAuthDeps = {}): Promise<{ access_token: string; expires_in: number }> {
  const f = deps.fetchImpl ?? fetch;
  const u = new URL("https://graph.instagram.com/access_token");
  u.searchParams.set("grant_type", "ig_exchange_token");
  u.searchParams.set("client_secret", cfg.appSecret);
  u.searchParams.set("access_token", shortToken);
  const res = await f(u);
  const json = (await res.json()) as { access_token: string; expires_in: number };
  if (!res.ok) throw new IgOAuthError(res.status, json);
  return json;
}

export async function refreshLongLived(token: string, deps: IgOAuthDeps = {}): Promise<{ access_token: string; expires_in: number }> {
  const f = deps.fetchImpl ?? fetch;
  const u = new URL("https://graph.instagram.com/refresh_access_token");
  u.searchParams.set("grant_type", "ig_refresh_token");
  u.searchParams.set("access_token", token);
  const res = await f(u);
  const json = (await res.json()) as { access_token: string; expires_in: number };
  if (!res.ok) throw new IgOAuthError(res.status, json);
  return json;
}

export async function fetchMe(token: string, deps: IgOAuthDeps = {}): Promise<{ id: string; user_id: string; username: string; followers_count?: number; account_type?: string }> {
  const f = deps.fetchImpl ?? fetch;
  const u = new URL(`${IG_API_BASE}/me`);
  u.searchParams.set("fields", "id,user_id,username,account_type,followers_count");
  u.searchParams.set("access_token", token);
  const res = await f(u);
  const json = (await res.json()) as { id: string; user_id: string; username: string; followers_count?: number; account_type?: string };
  if (!res.ok) throw new IgOAuthError(res.status, json);
  return json;
}

/** Full flow: code → short-lived → long-lived → /me → Token. */
export async function completeAuthorization(cfg: OAuthConfig, code: string, deps: IgOAuthDeps = {}): Promise<Token> {
  const now = deps.now ?? Date.now;
  const short = await exchangeCode(cfg, code, deps);
  const long = await exchangeLongLived(cfg, short.access_token, deps);
  const me = await fetchMe(long.access_token, deps).catch(() => null);
  const t = now();
  return TokenSchema.parse({
    access_token: long.access_token,
    token_type: "bearer",
    ig_user_id: me?.user_id ?? short.user_id,
    username: me?.username ?? null,
    permissions: short.permissions,
    obtained_at: new Date(t).toISOString(),
    expires_at: new Date(t + long.expires_in * 1000).toISOString(),
    source: "instagram_login",
  });
}

// ---------- per-account token store ----------
export function tokenPath(account: string): string {
  return path.join(dataDir(account), "token.json");
}
export function readToken(account: string): Token | null {
  const f = tokenPath(account);
  if (!fs.existsSync(f)) return null;
  return TokenSchema.parse(JSON.parse(fs.readFileSync(f, "utf8")));
}
export function writeToken(account: string, token: Token): void {
  const f = tokenPath(account);
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, JSON.stringify(token, null, 2) + "\n", { mode: 0o600 });
}

export function tokenStatus(token: Token, now = Date.now()): { daysLeft: number; ageDays: number; expired: boolean; refreshable: boolean; shouldRefresh: boolean } {
  const exp = Date.parse(token.expires_at);
  const obt = Date.parse(token.obtained_at);
  const daysLeft = (exp - now) / 86_400_000;
  const ageDays = (now - obt) / 86_400_000;
  const expired = daysLeft <= 0;
  const refreshable = !expired && ageDays >= 1;
  return { daysLeft: Math.round(daysLeft * 10) / 10, ageDays: Math.round(ageDays * 10) / 10, expired, refreshable, shouldRefresh: refreshable && daysLeft < 10 };
}

/** Refresh if it is worth it; returns the (possibly new) token. Never throws on a failed refresh when the token is still valid. */
export async function ensureFreshToken(account: string, deps: IgOAuthDeps = {}): Promise<Token | null> {
  const t = readToken(account);
  if (!t) return null;
  const now = deps.now ?? Date.now;
  const st = tokenStatus(t, now());
  if (st.expired) throw new Error(`Token for account "${account}" expired on ${t.expires_at.slice(0, 10)}. Re-run: reelcritic -a ${account} connect`);
  if (!st.shouldRefresh) return t;
  try {
    const r = await refreshLongLived(t.access_token, deps);
    const nt: Token = { ...t, access_token: r.access_token, obtained_at: new Date(now()).toISOString(), expires_at: new Date(now() + r.expires_in * 1000).toISOString() };
    writeToken(account, nt);
    return nt;
  } catch {
    return t;
  }
}
