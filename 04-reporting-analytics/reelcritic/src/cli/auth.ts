import { Command } from "commander";
import { env } from "../config.js";
import { GraphApiClient } from "../ingest/graph-api.js";
import { upsertEnv } from "./env-file.js";

export function registerAuth(program: Command): void {
  const auth = program.command("auth").description("Instagram Graph API token management (own account, Meta app in Development Mode)");

  auth
    .command("set-token <token>")
    .description("Store a long-lived user access token in .env (IG_ACCESS_TOKEN)")
    .action((token: string) => {
      upsertEnv({ IG_ACCESS_TOKEN: token.trim() });
      console.log("Saved IG_ACCESS_TOKEN to .env");
    });

  auth
    .command("status")
    .description("Verify the stored token and show the linked account")
    .action(async () => {
      const token = env("IG_ACCESS_TOKEN");
      if (!token) return fail("No IG_ACCESS_TOKEN. Run: reelcritic auth set-token <token>");
      const client = new GraphApiClient(token);
      const me = await client.me();
      console.log(`Token OK for Facebook user ${me.name ?? me.id}`);
      const igId = env("IG_USER_ID");
      if (igId) {
        const acct = await client.account(igId);
        console.log(`Instagram: @${acct.username} (${acct.followers_count.toLocaleString("en-US")} followers, id ${acct.id})`);
      } else console.log("IG_USER_ID not set — run: reelcritic auth discover");
    });

  auth
    .command("discover")
    .description("List every Facebook Page this token manages and its linked Instagram professional account")
    .option("--save <username>", "also save that account's id as IG_USER_ID (single-account default)")
    .action(async (opts: { save?: string }) => {
      const token = env("IG_ACCESS_TOKEN");
      if (!token) return fail("No IG_ACCESS_TOKEN. Run: reelcritic auth set-token <token>");
      const client = new GraphApiClient(token);
      const all = await client.discoverAll();
      if (all.length === 0) return fail("This token can see no Pages. Grant pages_show_list (and pages_read_engagement) when generating it.");
      console.log(`${all.length} Page(s):`);
      for (const p of all) {
        console.log(p.ig ? `  ${p.page_name.padEnd(32)} → @${p.ig.username}  (ig_user_id ${p.ig.id}${p.ig.followers_count != null ? `, ${p.ig.followers_count.toLocaleString("en-US")} followers` : ""})` : `  ${p.page_name.padEnd(32)} → (no Instagram professional account linked)`);
      }
      const linked = all.filter((p) => p.ig);
      if (linked.length === 0) return fail("No Page has an Instagram professional account linked. In Instagram: Settings → Business tools → Connect a Facebook Page.");
      console.log(`\nNext: reelcritic --account <slug> pull --username <ig_username>`);
      if (opts.save) {
        const hit = linked.find((p) => p.ig!.username.toLowerCase() === opts.save!.replace(/^@/, "").toLowerCase());
        if (!hit) return fail(`@${opts.save} is not linked to any Page this token manages.`);
        upsertEnv({ IG_USER_ID: hit.ig!.id });
        console.log(`Saved IG_USER_ID=${hit.ig!.id} (@${hit.ig!.username})`);
      }
    });

  auth
    .command("refresh")
    .description("Exchange the current token for a fresh 60-day long-lived token (needs IG_APP_ID and IG_APP_SECRET)")
    .action(async () => {
      const token = env("IG_ACCESS_TOKEN");
      const appId = env("IG_APP_ID");
      const secret = env("IG_APP_SECRET");
      if (!token || !appId || !secret) return fail("Need IG_ACCESS_TOKEN, IG_APP_ID and IG_APP_SECRET in .env");
      const r = await GraphApiClient.refreshLongLivedToken(appId, secret, token);
      upsertEnv({ IG_ACCESS_TOKEN: r.access_token });
      console.log(`Refreshed token${r.expires_in ? ` (expires in ${Math.round(r.expires_in / 86400)} days)` : ""}`);
    });
}

function fail(msg: string): never {
  console.error(msg);
  process.exit(2);
}
