import { Command } from "commander";
import { P } from "../config.js";
import { importBusinessSuiteCsv } from "../ingest/business-suite.js";
import { mergeReels, readJson, writeJson } from "../ingest/store.js";
import { AccountSchema, ReelSchema } from "../ingest/types.js";

export function registerImport(program: Command): void {
  program
    .command("import <file.csv>")
    .description("Import a Meta Business Suite content-performance CSV export and merge into data/reels.json")
    .option("--username <name>", "Instagram username (only needed if data/account.json does not exist)")
    .option("--followers <n>", "follower count (only needed if data/account.json does not exist)", (v) => parseInt(v, 10))
    .action((file: string, opts: { username?: string; followers?: number }) => {
      const r = importBusinessSuiteCsv(file);
      if (r.unmapped_headers.length) console.log(`Unmapped columns (add aliases in src/ingest/business-suite.ts if useful): ${r.unmapped_headers.join(" | ")}`);
      if (r.skipped_rows) console.log(`Skipped ${r.skipped_rows} non-Reel / incomplete rows`);
      const existing = readJson(P().reels, ReelSchema.array()) ?? [];
      const merged = mergeReels(existing, r.reels);
      writeJson(P().reels, merged);
      if (!readJson(P().account, AccountSchema)) {
        if (!opts.username || !opts.followers) {
          console.error("data/account.json missing — pass --username and --followers so percentiles/benchmarks can be computed.");
          process.exit(2);
        }
        writeJson(P().account, { ig_user_id: "csv", username: opts.username, follower_count: opts.followers, pulled_at: new Date().toISOString() });
      }
      console.log(`Imported ${r.reels.length} Reels → data/reels.json now has ${merged.length}`);
    });
}
