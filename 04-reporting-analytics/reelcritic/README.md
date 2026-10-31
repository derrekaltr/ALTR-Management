# reelcritic

Instagram Reels analytics critique, built on the creator's **real** numbers. For every Reel and for the account as a whole it answers, in order:

1. **What you're doing** — the concrete pattern (format, hook, length, caption, cadence)
2. **Why it's incorrect** — the mechanisms that suppressed reach or retention, each tied to a metric or a policy hard rule
3. **A better example** — the *mechanism* of a stronger version in the same length band (hook rewritten word-for-word, beat-by-beat structure, the reward or loop) — never "copy creator X"
4. **Why it worked vs. why it failed** — in the same metric vocabulary as the diagnosis, so it is falsifiable
5. **What to change next** — prioritized, each naming the one metric to watch

Every number in a critique is computed in code from your data and cited as `metric = value (pNN)`, where `pNN` is the percentile against **your own** Reels. Claude never sees raw media or invents thresholds; a validator rejects any cited number that does not match the computed packet.

The market research behind the design is in [`docs/research/`](docs/research/README.md).

## Setup

```bash
npm install
npm run typecheck && npm test        # no credentials needed
```

**Claude credential** (needed for `analyze` and `screenshot`): either `export ANTHROPIC_API_KEY=sk-ant-...` (or put it in `.env`, see `.env.example`), or install the `ant` CLI and run `ant auth login` — the SDK picks up the profile automatically.

## Try it without an Instagram token

```bash
npm run analyze -- --fixture                              # 20 synthetic Reels, ~$1–3 in Claude usage
open out/report.md
npm run analyze -- --fixture --dry-run                     # packets + report skeleton, no Claude calls
npm run analyze -- --fixture --reel r02 --effort medium    # one Reel
```

## Connect creator accounts (the scalable path)

Private insights are only readable with the creator's authorization — but that is a **one-time tap on their own phone**, not you logging in as them. This is the *Instagram API with Instagram Login* flow every agency tool uses; no Facebook Page linkage is needed.

**One-time Meta app setup (you, ~10 min):**
1. [developers.facebook.com/apps](https://developers.facebook.com/apps) → *Create App* → type **Business**. (Developer registration must be done from a device Meta already trusts for your account.)
2. In the app: **Instagram → API setup with Instagram business login**. Copy the **Instagram App ID** and **App Secret** into `.env` as `IG_APP_ID` / `IG_APP_SECRET`.
3. *Business login settings → Valid OAuth Redirect URIs*: add your callback, e.g. `https://xxxx.ngrok.app/callback`, and put the same value in `.env` as `IG_REDIRECT_URI`. (Creators tap Allow on their phones, so the callback must be reachable from the internet — `ngrok http 3000` or `cloudflared tunnel` in front of the local server is enough.)
4. While the app is in **Development Mode**, each creator must be added under *App Roles → Roles → Instagram Testers* and accept the invite in Instagram (*Settings → Apps and websites → Tester invites*). Fine for a handful of accounts. For any number of creators with no tester step, submit **App Review** for `instagram_business_basic` + `instagram_business_manage_insights` (Advanced Access; needs Business Verification; typically 1–3 weeks).

**Per creator (30 seconds):**
```bash
npx tsx src/cli/index.ts -a sarah connect          # prints a link + waits on the callback
# send the link; the creator opens it on their phone, logs in as themselves, taps Allow
npx tsx src/cli/index.ts -a sarah pull --comments  # → data/sarah/
npx tsx src/cli/index.ts -a sarah analyze          # → out/sarah/report.md
```
If the callback can't reach you, `connect --no-serve` prints the link only and `connect --code "<url they landed on>"` finishes it. Tokens live in `data/<slug>/token.json` (60 days) and refresh automatically on `pull`; `token --refresh` forces it; `accounts` shows expiry for every slug.

## Single account via Facebook Login (legacy)

If you only care about an Instagram professional account that is linked to a Facebook Page *you* manage, a user token from the Graph API Explorer works without the connect flow:

```bash
npx tsx src/cli/index.ts auth set-token <long-lived-token>
npx tsx src/cli/index.ts auth discover          # lists every Page you manage + its linked IG account
npx tsx src/cli/index.ts pull --username sarah.h44 --comments
```

### The data the API does not give you

The **retention curve**, **views by source** and **per-Reel follower vs non-follower split** exist only in the Instagram app. Screenshot the Reel's *View insights* screen and run:

```bash
npx tsx src/cli/index.ts screenshot <reelId> retention.png sources.png
```

Claude vision extracts the numbers and the curve into `data/screenshots/<reelId>.json`; the next `analyze` classifies the curve (cliff / hump / plateau-loop) and cites it.

### Other inputs

- `import <file.csv>` — Meta Business Suite → Insights → Content → *Export*. Column names vary; unmapped columns are printed so you can add aliases in `src/ingest/business-suite.ts`.
- `data/overrides.json` — `{ "<reelId>": { "duration_s": 27 } }` when a duration could not be probed.
- `data/flags.json` — `{ "<reelId>": { "repost": true, "other_platform_watermark": true, "majority_text": true } }` for hard rules that need a human eye.

## Example library (hooks · captions · on-screen text · comments)

`src/rubric/examples/*.json` holds pattern cards — each with a template, real examples, the mechanism, the anti-pattern, and which computed failure modes / length bands / value types it fits. They were seeded from three reference accounts the user rates highly (see [`docs/research/reference-creators.md`](docs/research/reference-creators.md)); the dominant mechanism there is a **premise stated as first-frame text** on a talking-head skit, a one-line in-character caption with no hashtags, and (on the fastest-growing account) a **pinned binary question** to seed comments.

The packet tags each Reel with `failure_modes` (computed) and `suggested_pattern_ids`; the critique's `better_example` returns the rewritten hook, the exact frame-0 `on_screen_text`, the `caption`, a `comment_seed`, and `patterns_used` — pattern ids are validated against the library so Claude cannot invent one. Add a card by appending to the JSON; `npm test` validates it.

## Niche profiles

`--profile default` has no niche rules. A profile is plain JSON in `src/rubric/profiles/` validated by `ProfileSchema`: recurring `season_windows`, dated `event_windows` + `event_keywords` (Reels inside them are tagged event-driven and excluded from your percentile baseline), `commercial_risk_patterns`, `reminders`, an admiring/hostile `sentiment_lexicon` for comment samples, and `extra_rubric_text` appended to the system prompt. See `test/fixtures/test-profile.json` for a complete example.

## How to read the report

- **Hard-rule summary** — deterministic policy violations with primary-source citations (>5 hashtags, >3 min, engagement bait, other-platform watermark, majority-text, low-res, bordered, muted, repost/originality). Fix these before anything else.
- **Percentiles** are against your own history; they are `—` when fewer than 5 comparable Reels exist. Event-driven Reels are excluded from the population so a viral disaster clip does not distort your baseline.
- **Partial validation banner** — Claude cited a number that did not match the computed packet; the bad evidence was removed and confidence capped at 0.4. Re-run that Reel.
- **Data gaps** — what could not be judged and how to supply it (screenshot, override, more Reels).

## Layout

```
src/ingest/    Instagram Login OAuth + token store, Graph/Instagram API client (rate-limited, cached), Business Suite CSV, mp4 duration probe, screenshot vision, JSON store
src/metrics/   pure functions: ratios, own-history percentiles, length bands, retention-curve classifier, hard rules, niche annotations, packet builder
src/rubric/    benchmarks (Socialinsider 2025), niche profiles, frozen system prompt (cached)
src/critique/  Claude calls (claude-opus-5, structured output via zodOutputFormat), Zod schemas, evidence validator + repair loop
src/report/    markdown + JSON renderers
src/cli/       connect · token · accounts · auth · pull · import · screenshot · analyze · report
docs/research/ the research reports (data access, frameworks, competitors, reference creators) + index
```

## Tests

```bash
npm test                     # unit tests (metrics, ingest, schemas, report) — no network
LIVE=1 npm run test:live     # one real Claude call; asserts schema, evidence validation and prompt-cache hit
```
