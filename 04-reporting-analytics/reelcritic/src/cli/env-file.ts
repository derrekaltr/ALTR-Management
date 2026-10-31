import fs from "node:fs";
import { ENV_FILE } from "../config.js";

/** Upsert KEY=value lines in .env without touching other keys. */
export function upsertEnv(values: Record<string, string>): void {
  const existing = fs.existsSync(ENV_FILE) ? fs.readFileSync(ENV_FILE, "utf8") : "";
  const lines = existing.split(/\r?\n/);
  const seen = new Set<string>();
  const out = lines.map((line) => {
    const m = /^([A-Z0-9_]+)=/.exec(line);
    if (m && values[m[1]!] != null) {
      seen.add(m[1]!);
      return `${m[1]}=${values[m[1]!]}`;
    }
    return line;
  });
  for (const [k, v] of Object.entries(values)) if (!seen.has(k)) out.push(`${k}=${v}`);
  fs.writeFileSync(ENV_FILE, out.filter((l, i, a) => !(l === "" && i === a.length - 1)).join("\n") + "\n");
  for (const [k, v] of Object.entries(values)) process.env[k] = v;
}
