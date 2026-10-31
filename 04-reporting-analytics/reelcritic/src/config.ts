import fs from "node:fs";
import path from "node:path";

export const MODEL = "claude-opus-5";
export const GRAPH_API_VERSION = "v21.0";

/** Resolved at call time so tests (and `cd`) can relocate the project root. */
export function root(): string {
  return process.env.REELCRITIC_ROOT ?? process.cwd();
}
export const FIXTURES_DIR = path.join(process.cwd(), "fixtures");
export const FIXTURE_FILE = path.join(FIXTURES_DIR, "sample-account.json");
export const ENV_FILE = path.join(process.cwd(), ".env");

/**
 * Multi-account: every data/out path is scoped by the active account slug
 * (`--account <slug>` on the CLI, or REELCRITIC_ACCOUNT). Unset = "default".
 */
export function currentAccount(): string {
  const a = (process.env.REELCRITIC_ACCOUNT ?? "default").trim().toLowerCase().replace(/[^a-z0-9._-]+/g, "-");
  return a || "default";
}
export function setCurrentAccount(slug: string): void {
  process.env.REELCRITIC_ACCOUNT = slug;
}

export function dataDir(account = currentAccount()): string {
  return account === "default" ? path.join(root(), "data") : path.join(root(), "data", account);
}
export function outDir(account = currentAccount()): string {
  return account === "default" ? path.join(root(), "out") : path.join(root(), "out", account);
}
export function cacheDir(): string {
  return path.join(root(), "data", "cache"); // shared across accounts (keyed by media id)
}
export function screenshotsDir(account = currentAccount()): string {
  return path.join(dataDir(account), "screenshots");
}

export interface Paths {
  reels: string;
  account: string;
  comments: string;
  flags: string;
  overrides: string;
  critiques: string;
  reportMd: string;
  reportJson: string;
  env: string;
  fixture: string;
}
/** Paths for the active account. Call at use time, not import time. */
export function P(account = currentAccount()): Paths {
  const d = dataDir(account);
  const o = outDir(account);
  return {
    reels: path.join(d, "reels.json"),
    account: path.join(d, "account.json"),
    comments: path.join(d, "comments.json"),
    flags: path.join(d, "flags.json"),
    overrides: path.join(d, "overrides.json"),
    critiques: path.join(o, "critiques.json"),
    reportMd: path.join(o, "report.md"),
    reportJson: path.join(o, "report.json"),
    env: ENV_FILE,
    fixture: FIXTURE_FILE,
  };
}

/** Account slugs that have data on disk. */
export function listAccounts(): string[] {
  const rootDir = root;
  const rootData = path.join(rootDir(), "data");
  if (!fs.existsSync(rootData)) return [];
  const out: string[] = [];
  if (fs.existsSync(path.join(rootData, "account.json"))) out.push("default");
  for (const e of fs.readdirSync(rootData, { withFileTypes: true })) {
    if (e.isDirectory() && e.name !== "cache" && e.name !== "screenshots" && (fs.existsSync(path.join(rootData, e.name, "account.json")) || fs.existsSync(path.join(rootData, e.name, "token.json")))) out.push(e.name);
  }
  return out;
}

let envLoaded = false;
/** Load `.env` once if present. Node 22 built-in; no dotenv dependency. */
export function loadEnv(): void {
  if (envLoaded) return;
  envLoaded = true;
  if (fs.existsSync(ENV_FILE)) {
    try {
      process.loadEnvFile(ENV_FILE);
    } catch {
      /* ignore malformed .env */
    }
  }
}

export function env(name: string): string | undefined {
  loadEnv();
  const v = process.env[name];
  return v && v.length > 0 ? v : undefined;
}
