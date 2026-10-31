import { Command } from "commander";
import { currentAccount } from "../config.js";
import { buildAuthUrl, completeAuthorization, newState, oauthConfigFromEnv, parseCodeInput, readToken, tokenStatus, writeToken, ensureFreshToken } from "../ingest/ig-login.js";
import { startCallbackServer } from "../ingest/oauth-server.js";

export function registerConnect(program: Command): void {
  program
    .command("connect")
    .description("Connect a creator's Instagram account via Instagram Login (they tap Allow on their own phone; no passwords shared). Use with -a <slug>.")
    .option("--redirect-uri <url>", "must match a Valid OAuth Redirect URI in the Meta app (default: IG_REDIRECT_URI or http://localhost:3000/callback)")
    .option("--port <n>", "local callback port", (v) => parseInt(v, 10), 3000)
    .option("--no-serve", "print the link only; complete later with --code")
    .option("--code <code-or-url>", "finish manually: the ?code= value or the whole redirect URL the creator sent back")
    .option("--timeout <min>", "minutes to wait for the creator to tap Allow", (v) => parseInt(v, 10), 30)
    .option("--force-reauth", "force the creator to re-enter credentials")
    .action(async (opts: { redirectUri?: string; port: number; serve: boolean; code?: string; timeout: number; forceReauth?: boolean }) => {
      const account = currentAccount();
      if (account === "default") {
        console.error("Pick a slug for this creator: reelcritic -a <slug> connect   (e.g. -a sarah)");
        process.exit(2);
      }
      const cfg = oauthConfigFromEnv(opts.redirectUri ? { redirectUri: opts.redirectUri } : {});

      if (opts.code) {
        const { code } = parseCodeInput(opts.code);
        const token = await completeAuthorization(cfg, code);
        writeToken(account, token);
        console.log(`Connected @${token.username ?? token.ig_user_id} → data/${account}/token.json (expires ${token.expires_at.slice(0, 10)})`);
        return;
      }

      const existing = readToken(account);
      if (existing) {
        const st = tokenStatus(existing);
        console.log(`Account "${account}" already has a token for @${existing.username ?? existing.ig_user_id} (${st.expired ? "EXPIRED" : `${st.daysLeft} days left`}). Continuing will replace it.`);
      }

      const state = newState(account);
      const url = buildAuthUrl(cfg, state, { forceReauth: !!opts.forceReauth });
      console.log(`\nSend this link to the creator (${account}). They open it on their phone, log in as themselves, tap Allow:\n\n${url}\n`);

      if (!opts.serve) {
        console.log(`When they send back the URL they landed on, run:\n  reelcritic -a ${account} connect --code "<that url>"`);
        return;
      }

      const expected = new Set([state]);
      let done = false;
      const server = await startCallbackServer({
        cfg,
        port: opts.port,
        expectedStates: expected,
        log: (m) => console.log(m),
        onToken: (acct, token) => {
          done = true;
          console.log(`\nConnected @${token.username ?? token.ig_user_id} → data/${acct}/token.json (expires ${token.expires_at.slice(0, 10)})`);
          console.log(`Next: reelcritic -a ${acct} pull --comments && reelcritic -a ${acct} analyze`);
          server.close();
        },
        onError: (e) => console.error(`callback error: ${e.message}`),
      });
      const local = new URL(cfg.redirectUri);
      if (!/localhost|127\.0\.0\.1/.test(local.hostname)) console.log(`Redirect URI is ${cfg.redirectUri} — make sure that hostname tunnels to this machine's port ${opts.port} (e.g. ngrok http ${opts.port}).`);
      console.log(`Waiting up to ${opts.timeout} min for the creator to tap Allow… (Ctrl-C to stop; you can finish later with --code)`);
      setTimeout(() => {
        if (!done) {
          console.log("Timed out waiting. The link is still valid until you run connect again; finish with --code when they send the redirect URL.");
          server.close();
        }
      }, opts.timeout * 60_000).unref();
    });

  program
    .command("token")
    .description("Show / refresh the connected Instagram token for -a <slug>")
    .option("--refresh", "refresh now if eligible (token ≥ 24 h old and not expired)")
    .action(async (opts: { refresh?: boolean }) => {
      const account = currentAccount();
      const t = readToken(account);
      if (!t) {
        console.log(`No Instagram Login token for account "${account}". Run: reelcritic -a ${account} connect`);
        return;
      }
      const st = tokenStatus(t);
      console.log(`@${t.username ?? t.ig_user_id} (ig_user_id ${t.ig_user_id}) · obtained ${t.obtained_at.slice(0, 10)} · expires ${t.expires_at.slice(0, 10)} · ${st.expired ? "EXPIRED" : `${st.daysLeft} days left`} · permissions: ${t.permissions.join(", ") || "?"}`);
      if (opts.refresh) {
        const nt = await ensureFreshToken(account);
        if (nt && nt.access_token !== t.access_token) console.log(`Refreshed → expires ${nt.expires_at.slice(0, 10)}`);
        else console.log(st.refreshable ? "Refresh not needed yet (>10 days left)." : "Not refreshable yet (must be ≥ 24 h old).");
      }
    });
}
