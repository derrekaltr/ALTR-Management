import { Command } from "commander";
import { P, env, currentAccount } from "../config.js";
import { GraphApiClient, rawMediaToReel } from "../ingest/graph-api.js";
import { ensureFreshToken } from "../ingest/ig-login.js";
import { fetchDurationSeconds, readOverrides, resolveDuration } from "../ingest/duration.js";
import { readJson, writeDataset, writeJson } from "../ingest/store.js";
import { ReelFlagsSchema, ReelSchema, type Account, type Reel } from "../ingest/types.js";
import { z } from "zod";

export function registerPull(program: Command): void {
  program
    .command("pull")
    .description("Pull your Reels + insights from the Instagram Graph API into data/")
    .option("--username <ig_username>", "Instagram username to pull (resolved via the Pages this token manages); overrides IG_USER_ID")
    .option("--since <YYYY-MM-DD>", "only Reels published on/after this date")
    .option("--limit <n>", "max Reels", (v) => parseInt(v, 10))
    .option("--comments", "also pull up to 50 comments per Reel", false)
    .option("--no-probe", "skip downloading media to probe duration")
    .action(async (opts: { username?: string; since?: string; limit?: number; comments: boolean; probe: boolean }) => {
      // 1) per-account Instagram Login token (creators who ran `connect`); 2) Facebook-Login user token from .env
      const igToken = await ensureFreshToken(currentAccount());
      const token = igToken?.access_token ?? env("IG_ACCESS_TOKEN");
      if (!token) {
        console.error(`No token for account "${currentAccount()}". Either \`reelcritic -a ${currentAccount()} connect\` (creator taps Allow) or set IG_ACCESS_TOKEN in .env.`);
        process.exit(2);
      }
      const client = new GraphApiClient(token, { mode: igToken ? "instagram" : "facebook" });
      let igId = igToken?.ig_user_id ?? env("IG_USER_ID");
      if (igToken && opts.username && opts.username.replace(/^@/, "").toLowerCase() !== (igToken.username ?? "").toLowerCase()) {
        console.error(`Account "${currentAccount()}" is connected as @${igToken.username}; --username ${opts.username} does not match.`);
        process.exit(2);
      }
      if (!igToken && opts.username) {
        const r = await client.resolveUsername(opts.username);
        if (!r) {
          console.error(`@${opts.username} is not linked to any Page this token manages. Run \`reelcritic auth discover\` to see what is.`);
          process.exit(2);
        }
        igId = r.id;
      }
      if (!igId) {
        console.error("Pass --username <ig_username> or set IG_USER_ID (`reelcritic auth discover --save <username>`).");
        process.exit(2);
      }
      const acct = await client.account(igId);
      console.log(`[account ${currentAccount()}] @${acct.username} — ${acct.followers_count.toLocaleString("en-US")} followers`);

      const existing = readJson(P().reels, ReelSchema.array()) ?? [];
      const byId = new Map(existing.map((r) => [r.id, r] as const));
      const overrides = readOverrides();
      const flags = readJson(P().flags, z.record(z.string(), ReelFlagsSchema)) ?? {};

      const reels: Reel[] = [];
      let n = 0;
      for await (const m of client.listReels(igId, { since: opts.since, limit: opts.limit })) {
        n++;
        const insights = await client.reelInsights(m.id);
        const prev = byId.get(m.id);
        let reel = rawMediaToReel(m, insights);
        if (prev) reel = { ...prev, ...reel, screenshot: prev.screenshot, comments_sample: prev.comments_sample, duration_s: prev.duration_s, duration_source: prev.duration_source };
        if (flags[m.id]) reel.flags = { ...(reel.flags ?? {}), ...flags[m.id] };
        if (opts.probe && reel.duration_s == null && m.media_url) {
          const d = await fetchDurationSeconds(m.media_url);
          if (d != null) {
            reel.duration_s = Math.round(d * 10) / 10;
            reel.duration_source = "probe";
          }
        }
        Object.assign(reel, resolveDuration(reel, overrides));
        if (opts.comments) reel.comments_sample = await client.comments(m.id);
        reels.push(reel);
        process.stdout.write(`\r  ${n} Reels pulled (${m.timestamp.slice(0, 10)})   `);
      }
      process.stdout.write("\n");

      // keep older reels we did not re-pull this run
      for (const r of existing) if (!reels.find((x) => x.id === r.id)) reels.push(r);
      reels.sort((a, b) => a.timestamp.localeCompare(b.timestamp));

      const first = reels[0]?.timestamp ?? new Date(Date.now() - 180 * 86_400_000).toISOString();
      const sinceUnix = Math.floor(Date.parse(first) / 1000);
      const untilUnix = Math.floor(Date.now() / 1000);
      const extra = await client.accountInsights(igId, sinceUnix, untilUnix);

      const account: Account = { ig_user_id: igId, username: acct.username, follower_count: acct.followers_count, ...extra, pulled_at: new Date().toISOString() };
      writeDataset({ account, reels });
      if (opts.comments) writeJson(P().comments, Object.fromEntries(reels.map((r) => [r.id, r.comments_sample ?? []])));
      const known = reels.filter((r) => r.duration_s != null).length;
      console.log(`Wrote ${reels.length} Reels to ${P().reels} (${known} with known duration) and ${P().account}`);
      if (!extra.views_by_follow_type) console.log("Note: account-level follower/non-follower view split unavailable for this account/token.");
    });
}
