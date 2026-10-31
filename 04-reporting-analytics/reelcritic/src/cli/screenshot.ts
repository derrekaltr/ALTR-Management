import path from "node:path";
import { Command } from "commander";
import { screenshotsDir } from "../config.js";
import { extractFromScreenshots } from "../ingest/screenshot-vision.js";
import { writeJson } from "../ingest/store.js";

export function registerScreenshot(program: Command): void {
  program
    .command("screenshot <reelId> <images...>")
    .description("Extract retention curve / views-by-source / follower split from in-app Insights screenshots (vision) → data/screenshots/<reelId>.json")
    .action(async (reelId: string, images: string[]) => {
      const out = await extractFromScreenshots(images);
      if (out.legibility === "unreadable") {
        console.error("Screenshots were unreadable — retake at full resolution with the chart fully visible.");
        process.exit(3);
      }
      const file = path.join(screenshotsDir(), `${reelId}.json`);
      writeJson(file, out);
      console.log(`Saved ${file}: ${out.retention_curve.length} curve points, skip rate ${out.skip_rate_pct ?? "—"}%, legibility ${out.legibility}${out.notes ? ` — ${out.notes}` : ""}`);
    });
}
