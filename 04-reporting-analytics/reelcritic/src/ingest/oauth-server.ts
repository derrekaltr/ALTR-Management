import http from "node:http";
import { accountFromState, completeAuthorization, writeToken, type IgOAuthDeps, type OAuthConfig, type Token } from "./ig-login.js";

export interface CallbackServerOptions {
  cfg: OAuthConfig;
  port: number;
  host?: string;
  /** Only accept callbacks whose state was issued by us. */
  expectedStates: Set<string>;
  onToken: (account: string, token: Token) => void;
  onError?: (err: Error) => void;
  deps?: IgOAuthDeps;
  log?: (msg: string) => void;
}

const page = (title: string, body: string) =>
  `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><body style="font:16px/1.5 -apple-system,system-ui,sans-serif;max-width:32rem;margin:4rem auto;padding:0 1rem;color:#111"><h1 style="font-size:1.4rem">${title}</h1><p>${body}</p></body>`;

/** Local HTTP callback server for the Instagram Login redirect. Bind 0.0.0.0 and tunnel it (ngrok/cloudflared) so creators' phones can reach it. */
export function startCallbackServer(opts: CallbackServerOptions): Promise<http.Server> {
  const log = opts.log ?? (() => {});
  const pathOf = new URL(opts.cfg.redirectUri).pathname || "/callback";
  const server = http.createServer(async (req, res) => {
    const u = new URL(req.url ?? "/", "http://localhost");
    if (u.pathname !== pathOf) {
      res.writeHead(404, { "content-type": "text/html" }).end(page("Not found", "Nothing here."));
      return;
    }
    const code = u.searchParams.get("code");
    const state = u.searchParams.get("state") ?? "";
    const err = u.searchParams.get("error_description") ?? u.searchParams.get("error");
    if (err) {
      res.writeHead(400, { "content-type": "text/html" }).end(page("Not connected", `Instagram said: ${err}. You can close this tab.`));
      opts.onError?.(new Error(`OAuth error: ${err}`));
      return;
    }
    if (!code || !opts.expectedStates.has(state)) {
      res.writeHead(400, { "content-type": "text/html" }).end(page("Invalid link", "This connect link is expired or was not issued by this tool. Ask for a new one."));
      return;
    }
    try {
      const account = accountFromState(state);
      const token = await completeAuthorization(opts.cfg, code.replace(/#_$/, ""), opts.deps);
      writeToken(account, token);
      opts.expectedStates.delete(state);
      opts.onToken(account, token);
      res.writeHead(200, { "content-type": "text/html" }).end(page("Connected ✓", `@${token.username ?? token.ig_user_id} is connected for analytics. You can close this tab.`));
    } catch (e) {
      opts.onError?.(e as Error);
      res.writeHead(500, { "content-type": "text/html" }).end(page("Something went wrong", "The connection could not be completed. Ask for a new link."));
    }
  });
  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(opts.port, opts.host ?? "0.0.0.0", () => {
      log(`callback server listening on http://${opts.host ?? "0.0.0.0"}:${opts.port}${pathOf}`);
      resolve(server);
    });
  });
}
