import fs from "node:fs";
import path from "node:path";
import type Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { ScreenshotExtractionSchema, type ScreenshotExtraction } from "./types.js";
import { CritiqueParseFailed, CritiqueRefused, MODEL, getClient, withRetry } from "../critique/client.js";

const SCREENSHOT_SYSTEM = `You extract numbers from Instagram Reel Insights screenshots (the in-app "View insights" screen or the Edits app insights export). Report ONLY what is visible. Use null for anything not shown.
- retention_curve: if a retention chart (% of viewers still watching over time) is visible, sample it as points {t_pct, retained_pct} at t = 0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100 (percent of video length). Read the y-axis carefully; retention at t=0 is typically 100. If no chart, return [].
- skip_rate_pct: the "Skip rate" percentage if shown.
- views_by_source: counts (or percentages if counts absent) for Reels tab / Explore / Home(feed) / Profile / other.
- follower_split: followers vs non-followers percentages.
- overview: views, reach, average watch time (seconds), video length (seconds) if shown.
- reel_hint: any caption/date text that identifies which Reel this is.
- legibility: clear / partial / unreadable.`;

const MIME: Record<string, "image/png" | "image/jpeg" | "image/webp" | "image/gif"> = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
};

export async function extractFromScreenshots(files: string[]): Promise<ScreenshotExtraction> {
  const client = getClient();
  const images: Anthropic.ImageBlockParam[] = files.map((f) => {
    const mt = MIME[path.extname(f).toLowerCase()];
    if (!mt) throw new Error(`Unsupported image type: ${f}`);
    return { type: "image", source: { type: "base64", media_type: mt, data: fs.readFileSync(f).toString("base64") } };
  });
  const res = await withRetry(() =>
    client.messages.parse({
      model: MODEL,
      max_tokens: 4000,
      system: [{ type: "text", text: SCREENSHOT_SYSTEM, cache_control: { type: "ephemeral" } }],
      messages: [{ role: "user", content: [...images, { type: "text", text: "Extract every number visible from these Insights screenshots." }] }],
      output_config: { effort: "low", format: zodOutputFormat(ScreenshotExtractionSchema) },
    }),
  );
  if (res.stop_reason === "refusal") throw new CritiqueRefused(res.stop_details);
  if (!res.parsed_output) throw new CritiqueParseFailed(res);
  return res.parsed_output;
}
