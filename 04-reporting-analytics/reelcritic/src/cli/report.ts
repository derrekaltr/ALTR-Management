import fs from "node:fs";
import path from "node:path";
import { Command } from "commander";
import { outDir } from "../config.js";
import { renderReport } from "../report/markdown.js";
import type { ReportBundle } from "../report/json.js";

export function registerReport(program: Command): void {
  program
    .command("report")
    .description("Re-render out/report.md from out/report.json without calling Claude")
    .option("--out <dir>", "output directory (default: out/ or out/<account>/)")
    .option("--format <fmt>", "md | json", "md")
    .action((opts: { out?: string; format: string }) => {
      const out = opts.out ?? outDir();
      const file = path.join(out, "report.json");
      if (!fs.existsSync(file)) {
        console.error(`${file} not found — run analyze first.`);
        process.exit(2);
      }
      const bundle = JSON.parse(fs.readFileSync(file, "utf8")) as ReportBundle;
      if (opts.format === "json") {
        process.stdout.write(JSON.stringify(bundle, null, 2));
        return;
      }
      const md = renderReport(bundle);
      fs.writeFileSync(path.join(out, "report.md"), md);
      console.log(`Re-rendered ${path.join(out, "report.md")}`);
    });
}
