# Trial Reels Hook & Example Pipeline

Internal tool for the trial-reels method: creators film **one blank, low-action base video per day**, and the **on-screen hook text does the retention work**. Each base video becomes 5–10 posted variants via the Edits app → **versions** (new hook text, new audio, optional speed change) — and a proven hook can be reused over a new background video. This app manages the two interchangeable libraries (hooks + example reels) and the daily version plans.

**What it deliberately does NOT do:** render or edit video (Edits needs the creator's original file for versions to count as trial reels), scrape Instagram, or auto-post.

## The loop

1. **Import** (`/admin/import`) — upload the reel-link sheet (one column of IG links → example stubs) or a hook table CSV (`text,category,tags,notes` → library hooks). Formats are auto-detected; share tokens and junk rows are cleaned up.
2. **Examples** (`/admin/examples`) — save a reel to your device, upload it to its stub (or direct-upload without a link). Frames are captured in the browser; the AI extracts the on-screen hook (→ review queue) and describes the blank background (setting / outfit / energy / why it works).
3. **Generate** (`/admin/generate`) — pick proven hooks as seeds, add tone guidance, get ~10 new candidates. Rejected hooks are remembered and fed back as "avoid these".
4. **Review** (`/admin/review`) — approve / reject / edit-then-approve, per candidate or per batch. Approved hooks join the library; everything is deduped on normalized wording.
5. **Plan** (`/admin/creators/…`) — one plan per creator per day: base-video concept + ordered versions (hook, "new audio" / "speed change" flags, optional reference clip). Hooks used in the last 14 days for that creator are excluded.
6. **Creator link** (`/c/<token>`) — mobile page per creator: today's versions, tap-to-copy hook text, the 3-second-hook reminder, mark-posted tracking, yesterday's leftovers. "Copy creator link" in admin; "Rotate link" kills the old one instantly.

## Running locally

```bash
cp .env.example .env         # set ADMIN_PASSWORD + SESSION_SECRET
npm install
npm run db:start             # embedded Postgres on :5502 (keep this terminal open)
                             # (or: docker compose up -d)
npm run db:migrate
npm run db:seed              # demo hooks + creators; prints creator links
npm run dev
```

Log in at http://localhost:3000 with `ADMIN_PASSWORD`.

**Mock mode:** with `ANTHROPIC_API_KEY` empty (or `LLM_MOCK=1`), generation and reel analysis use a deterministic offline mock — the entire app works with zero credentials. Set a real key (and optionally `LLM_MODEL`, default `claude-sonnet-5`) for real output.

**Local uploads** are stored under `public/uploads/` (gitignored). With `BLOB_READ_WRITE_TOKEN` set, files go to Vercel Blob via client uploads instead.

## Tests

```bash
npm test        # unit: normalization, URL canonicalization, LLM schemas
npm run build   # type-checks everything
```

E2E happy path (login → import → generate → review → plan → creator view → mark posted) is covered by a Playwright script kept outside the repo; the mock provider makes it runnable without credentials.

## Deploying (Vercel + Neon)

1. Create a Neon Postgres DB; set `DATABASE_URL`.
2. Set env vars on Vercel: `ADMIN_PASSWORD`, `SESSION_SECRET` (long random), `ANTHROPIC_API_KEY`, `BLOB_READ_WRITE_TOKEN` (create a Blob store).
3. Build command: `prisma generate && prisma migrate deploy && next build`.
4. After the first deploy, run the seed only if you want demo data.

Notes:
- `/c/*` and everything else are `noindex`; robots.txt disallows all. Creator tokens are the credential — share links privately, rotate on any leak.
- Generation/analysis run inside server actions with `maxDuration = 60`.
- Reel videos exceed Vercel's request-body limit, which is why prod uploads must use Blob client uploads (automatic when the token is set).

## Architecture crib sheet

- `prisma/schema.prisma` — ExampleReel, Hook (unique `normalizedText` = dedupe backbone), GenerationBatch, Creator (token auth), DayPlan (`@@unique(creatorId, date)`), Version.
- `src/lib/normalize.ts` — single source of truth for hook dedupe + IG URL canonicalization.
- `src/lib/llm/` — provider interface; `mock.ts` (offline) and `anthropic.ts` (structured outputs via `messages.parse` + zod).
- `src/lib/dates.ts` — "today" is computed in each creator's timezone, never server UTC.
- `src/actions/*` — every admin action re-verifies the session itself (middleware alone doesn't cover server actions). The only tokenless mutation is `markVersionPosted`, authorized by the creator token owning the version.
- `src/lib/storage.ts` — Vercel Blob when configured, `public/uploads/` otherwise.
