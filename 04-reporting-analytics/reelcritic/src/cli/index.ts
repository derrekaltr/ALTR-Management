#!/usr/bin/env node
import { Command } from "commander";
import { loadEnv, listAccounts, setCurrentAccount, currentAccount } from "../config.js";
import { registerAuth } from "./auth.js";
import { registerPull } from "./pull.js";
import { registerImport } from "./import.js";
import { registerScreenshot } from "./screenshot.js";
import { registerAnalyze } from "./analyze.js";
import { registerReport } from "./report.js";
import { registerConnect } from "./connect.js";
import { readToken, tokenStatus } from "../ingest/ig-login.js";

loadEnv();
const program = new Command()
  .name("reelcritic")
  .description("Instagram Reels analytics critique: what you're doing, why it's wrong, a better example, why it worked vs failed, what to change next.")
  .version("0.1.0")
  .option("-a, --account <slug>", "account slug: scopes data/<slug>/ and out/<slug>/ (mixed own + client accounts)")
  .hook("preAction", (cmd) => {
    const a = cmd.opts<{ account?: string }>().account;
    if (a) setCurrentAccount(a);
  });

program
  .command("accounts")
  .description("List account slugs that have pulled/imported data")
  .action(() => {
    const all = listAccounts();
    if (!all.length) return console.log("No accounts yet. Pull one: reelcritic --account <slug> pull --username <ig_username>");
    for (const a of all) {
      const t = readToken(a);
      const st = t ? tokenStatus(t) : null;
      console.log(`${a === currentAccount() ? "* " : "  "}${a.padEnd(16)} ${t ? `@${t.username ?? t.ig_user_id} · token ${st!.expired ? "EXPIRED" : `${st!.daysLeft}d left`}` : "(no Instagram Login token; uses IG_ACCESS_TOKEN)"}`);
    }
  });

registerAuth(program);
registerPull(program);
registerImport(program);
registerScreenshot(program);
registerAnalyze(program);
registerReport(program);
registerConnect(program);

program.parseAsync(process.argv).catch((err: unknown) => {
  console.error((err as Error).message ?? err);
  process.exit(1);
});
