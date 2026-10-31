import fs from "node:fs";
import path from "node:path";
import { Command } from "commander";
import { z } from "zod";
import { outDir, P, screenshotsDir, currentAccount } from "../config.js";
import { loadFixture } from "../ingest/fixture.js";
import { readDataset, readJson, writeJson } from "../ingest/store.js";
import { ReelFlagsSchema, ScreenshotExtractionSchema, type Dataset } from "../ingest/types.js";
import { readOverrides, resolveDuration } from "../ingest/duration.js";
import { buildAccountPacket, buildReelPacket, buildRows, type ReelPacket } from "../metrics/packet.js";
import { loadProfile } from "../rubric/profile.js";
import { critiqueReel } from "../critique/reel-critique.js";
import { critiqueAccount } from "../critique/account-critique.js";
import type { AccountCritique, CritiqueRecord, ReelCritique } from "../critique/schemas.js";
import { renderReport } from "../report/markdown.js";
import { renderJson, type ReportBundle } from "../report/json.js";

interface AnalyzeOpts {
  fixture?: boolean;
  profile: string;
  reel?: string;
  limit?: number;
  out?: string;
  account: boolean;
  effort: "low" | "medium" | "high" | "xhigh" | "max";
  dryRun?: boolean;
  concurrency: number;
}

/** Merge data/screenshots/*.json, data/flags.json and data/overrides.json into the dataset. */
export function enrichDataset(ds: Dataset): Dataset {
  const overrides = readOverrides();
  const flags = readJson(P().flags, z.record(z.string(), ReelFlagsSchema)) ?? {};
  const reels = ds.reels.map((r) => {
    const reel = { ...r };
    const ssFile = path.join(screenshotsDir(), `${r.id}.json`);
    if (fs.existsSync(ssFile)) reel.screenshot = ScreenshotExtractionSchema.parse(JSON.parse(fs.readFileSync(ssFile, "utf8")));
    if (flags[r.id]) reel.flags = { ...(reel.flags ?? {}), ...flags[r.id] };
    Object.assign(reel, resolveDuration(reel, overrides));
    return reel;
  });
  return { ...ds, reels };
}

export function registerAnalyze(program: Command): void {
  program
    .command("analyze")
    .description("Compute metrics, ask Claude for the 5-section critique per Reel and per account, write out/report.md + out/report.json")
    .option("--fixture", "use fixtures/sample-account.json instead of data/")
    .option("--profile <name>", "niche profile from src/rubric/profiles/", "default")
    .option("--reel <id>", "only this Reel")
    .option("--limit <n>", "only the N most recent Reels", (v) => parseInt(v, 10))
    .option("--out <dir>", "output directory (default: out/ or out/<account>/)")
    .option("--no-account", "skip the account-level critique")
    .option("--effort <level>", "Claude effort: low|medium|high|xhigh|max", "high")
    .option("--dry-run", "build packets and the report skeleton without calling Claude")
    .option("--concurrency <n>", "parallel Claude calls", (v) => parseInt(v, 10), 3)
    .action(async (opts: AnalyzeOpts) => {
      opts.out = opts.out ?? outDir();
      const profile = loadProfile(opts.profile);
      let ds = opts.fixture ? loadFixture() : readDataset();
      if (!ds) {
        console.error(`No reels.json + account.json for account "${currentAccount()}". Run \`reelcritic pull --username <ig_username>\`, \`reelcritic import <csv>\`, or use --fixture.`);
        process.exit(2);
      }
      ds = enrichDataset(ds);
      if (ds.reels.length === 0) {
        console.error("Dataset has no Reels.");
        process.exit(2);
      }

      const rows = buildRows(ds, profile);
      let targets = [...ds.reels].sort((a, b) => b.timestamp.localeCompare(a.timestamp));
      if (opts.reel) targets = targets.filter((r) => r.id === opts.reel);
      if (opts.limit) targets = targets.slice(0, opts.limit);
      if (targets.length === 0) {
        console.error(`No Reels matched${opts.reel ? ` id ${opts.reel}` : ""}.`);
        process.exit(2);
      }

      const packets = new Map<string, ReelPacket>(ds.reels.map((r) => [r.id, buildReelPacket(r, ds, profile, rows)]));
      const accountPacket = buildAccountPacket(ds, profile, rows);
      console.log(`[account ${currentAccount()}] @${ds.account.username}: ${ds.reels.length} Reels, profile "${profile.name}", ${targets.length} to critique${opts.dryRun ? " (dry run)" : ""}`);

      const outD = opts.out;
      const previous = readJson(path.join(outD, "critiques.json"), z.object({ reels: z.array(z.any()), account: z.any().nullable() })) as
        | { reels: CritiqueRecord<ReelCritique>[]; account: CritiqueRecord<AccountCritique> | null }
        | null;
      const critiques = new Map<string, CritiqueRecord<ReelCritique>>((previous?.reels ?? []).map((c) => [c.critique.reel_id, c]));

      let totalUsage = { input: 0, output: 0, cacheRead: 0 };
      if (!opts.dryRun) {
        const log = (m: string) => console.log(m);
        const queue = [...targets];
        const workers = Array.from({ length: Math.max(1, opts.concurrency) }, async () => {
          while (queue.length) {
            const reel = queue.shift()!;
            const packet = packets.get(reel.id)!;
            try {
              const rec = await critiqueReel(packet, profile, { effort: opts.effort, log });
              critiques.set(reel.id, rec);
              if (rec.usage) {
                totalUsage.input += rec.usage.input_tokens;
                totalUsage.output += rec.usage.output_tokens;
                totalUsage.cacheRead += rec.usage.cache_read_input_tokens;
              }
              writeJson(path.join(outD, "critiques.json"), { reels: [...critiques.values()], account: previous?.account ?? null });
            } catch (e) {
              console.error(`  reel ${reel.id}: FAILED — ${(e as Error).message}`);
            }
          }
        });
        await Promise.all(workers);
      }

      let accountCritique: CritiqueRecord<AccountCritique> | null = previous?.account ?? null;
      if (!opts.dryRun && opts.account && !opts.reel) {
        try {
          accountCritique = await critiqueAccount(accountPacket, packets, [...critiques.values()], profile, { effort: opts.effort, log: (m) => console.log(m) });
          if (accountCritique.usage) {
            totalUsage.input += accountCritique.usage.input_tokens;
            totalUsage.output += accountCritique.usage.output_tokens;
            totalUsage.cacheRead += accountCritique.usage.cache_read_input_tokens;
          }
        } catch (e) {
          console.error(`  account: FAILED — ${(e as Error).message}`);
        }
      }

      const bundle: ReportBundle = {
        generated_at: new Date().toISOString(),
        profile: profile.name,
        account: ds.account,
        account_packet: accountPacket,
        account_critique: accountCritique,
        reels: ds.reels.map((r) => ({ packet: packets.get(r.id)!, critique: critiques.get(r.id) ?? null })),
      };
      fs.mkdirSync(outD, { recursive: true });
      writeJson(path.join(outD, "critiques.json"), { reels: [...critiques.values()], account: accountCritique });
      fs.writeFileSync(path.join(outD, "report.json"), renderJson(bundle));
      fs.writeFileSync(path.join(outD, "report.md"), renderReport(bundle));
      const partial = [...critiques.values()].filter((c) => c.validation === "partial").length;
      console.log(`Wrote ${path.join(outD, "report.md")} (${critiques.size} Reel critiques${accountCritique ? " + account" : ""}${partial ? `, ${partial} partial-validation` : ""})`);
      if (!opts.dryRun) console.log(`Tokens: ${totalUsage.input.toLocaleString("en-US")} in / ${totalUsage.output.toLocaleString("en-US")} out / ${totalUsage.cacheRead.toLocaleString("en-US")} cache-read`);
    });
}
