# HANDOFF — Snapchat Gold Star (Verification Readiness) Report Tool

For: ALTR platform-compliance reports workspace.
Purpose of this doc: everything another agent/workspace needs to reuse, extend,
or port this tool to other platforms' guideline audits. Last updated 2026-10-30.

## What this tool does

`snapstar` audits a creator's **public Snapchat presence** before they apply
for verification (the "gold star"), and produces an **ALTR-branded PDF** listing
every item that could block approval, with severity, plain-English rationale,
and the exact in-app removal step. One PDF per creator + an internal
roster-overview PDF that accumulates every audited creator.

Pipeline (three decoupled stages, each re-runnable):

```
capture (Playwright/Chromium)──▶ review (Claude vision) ──▶ report (Jinja2+Chromium PDF)
output/captures/<user>/          output/reviews/<user>.json  output/reports/*.pdf
  screenshots + manifest.json      structured findings
```

## Repo map

| Path | Role |
|---|---|
| `snapstar_review/capture.py` | Playwright capture of `snapchat.com/@user`: full-page screenshot, per-tile (Story/Spotlight) element screenshots, bio/display-name extraction, status classification (ok / not_found / private / bot_wall / error), polite rate limiting, one bot-wall retry. Also ingests team-provided screenshots from `captures/<user>/manual/`. |
| `snapstar_review/models.py` | Pydantic models — the data contract between all stages: `Manifest`, `CapturedImage`, `ItemReview` (the Claude output schema), `ReviewedItem`, `CreatorReview`, `Severity`, `Category`, `Surface`, `CaptureStatus`. |
| `snapstar_review/rubric.py` | **The platform-specific brain.** System prompts for image + text review, severity definitions, category list, and readiness scoring (weighted flags → Ready / Nearly ready / Needs cleanup / Major cleanup; any critical ⇒ Major cleanup). |
| `snapstar_review/review.py` | Claude calls: one vision call per image, one text call per text field (username / display name / bio), via `client.messages.parse(..., output_format=ItemReview)` → validated structured output. Skips already-reviewed creators unless `--force`. Model from `config.yaml` (default `claude-sonnet-5`; `claude-opus-5` for max judgment). |
| `snapstar_review/report.py` | Jinja2 → HTML → Chromium `page.pdf()`. Embeds screenshots + logos as data URIs. Footer via Playwright footer template. |
| `snapstar_review/templates/` | `styles.css` (ALTR theme), `creator_report.html.j2`, `roster_summary.html.j2`. |
| `snapstar_review/demo.py` | Fabricated captures/reviews + pure-Python PNG generator → test the PDF pipeline with zero Snapchat/API calls (`snapstar demo`). |
| `snapstar_review/cli.py` | `snapstar add <username>` (the everyday one-creator flow), `capture`/`review`/`report` stages, `run --roster csv`. |
| `assets/` | Official ALTR logos (transparent PNGs tinted cream/mint/charcoal from the exports in `assets/src/`), brand kit JPG. `altr-logo.svg/png` drop-in overrides the wordmark. |
| `config.yaml` | Model, capture pacing/timeouts/headless, severity weights + readiness thresholds, "prepared by"/contact lines. |
| `.env` | `ANTHROPIC_API_KEY` (gitignored). |

## Daily usage

```bash
source .venv/bin/activate            # Python 3.11 venv, deps in pyproject.toml
snapstar add <username>              # full audit for one creator
snapstar add <username> --force      # re-audit after cleanup
snapstar demo                        # exercise PDFs without API/Snapchat
pytest                               # 12 unit tests (scoring, parsing, roster/manifest handling)
```

Setup from scratch: `python3.11 -m venv .venv && pip install -e ".[dev]" && playwright install chromium`, put `ANTHROPIC_API_KEY` in `.env`.

## ALTR brand spec (reuse in every report tool)

- Charcoal `#232321`, cream `#eaebdd`, mint accent `#c8f2e6` (deep-mint `#2f8a70`
  for accents on light backgrounds). Severity colors are semantic and
  platform-agnostic: critical `#b3261e`, high `#c96a2b`, medium `#b08d3f`, low `#6b7280`.
- Mono/techno font stack for labels (`SF Mono, JetBrains Mono, Menlo, …`),
  Helvetica for body. Squared corners (2px), hairline borders, generous whitespace.
- Cover: charcoal full-bleed panel, cream wordmark top-left, mint "A" glyph +
  mono index top-right, emblem + report title + "Prepared for <name>" lower third.
- Report structure: Cover → "Where you stand" (readiness badge + severity
  scorecard + explainer) → "What to remove or edit" (one card per finding:
  screenshot thumbnail, severity pill, category chips, rationale, charcoal
  "HOW TO FIX" box) → pre-application checklist + disclaimer. Footer:
  "ALTR · Confidential" + page numbers.
- The gold star glyph on the cover is intentionally gold (`#e6c15c`) — it is
  Snapchat's emblem. For other platforms swap the emblem, keep the palette.

## Porting this to another platform (the intended reuse path)

The architecture is already platform-shaped; ~90% carries over:

1. **capture.py** — swap the profile URL pattern, tile selectors, and
   status markers. Everything else (manifest format, manual/ folder ingestion,
   rate limiting, retry, JPEG element screenshots) is platform-neutral.
2. **rubric.py** — rewrite `_RUBRIC_CORE` for the target platform's guidelines
   (e.g. Instagram Community Guidelines / TikTok Community Guidelines /
   X monetization standards). Keep the same severity ladder and
   `removal_action` convention ("exact in-app steps"), and adjust `Category`
   enum in models.py if the platform needs new ones (keep enum values
   stable — they're in saved review JSONs).
3. **models.py / review.py / report.py / templates** — unchanged except
   cover title, emblem, and checklist copy.
4. **Scoring** — thresholds in `config.yaml`; any-critical ⇒ worst tier is
   hardcoded in `rubric.readiness_level`.

Key design decisions worth keeping: structured output via
`messages.parse(output_format=<pydantic model>)` (no JSON-wrangling);
per-item calls rather than batched (isolates failures, keeps rationales
specific); stages communicate only through files (so stages can be re-run,
inspected, and hand-edited); already-reviewed skip guard (API spend safety
for drip-feed workflows); borderline flag for judgment calls.

## Operational gotchas (learned in production)

- **Share links** (`snapchat.com/t/…`) are aliases: resolve with
  `curl -sIL -o /dev/null -w '%{url_effective}'`, and note the redirect slug
  may STILL be an alias — the authoritative username is the one shown on the
  profile page / in tile hrefs (e.g. share slug `alarahriessee` → real handle
  `alarahxo`). Verify against the profile screenshot before filing.
- **Two profile shapes**: full public profiles (grid of Stories/Spotlight —
  rich audit) vs. bare "add me" cards (avatar + name only — thin audit; the
  report's checklist covers the gap). Private accounts surface as the
  add-card or not_found.
- **Tile capture is best-effort**: selectors are `a[href*="/spotlight/"]`,
  `a[href*="/story/"]`, plus class-pattern fallbacks; some grid posts don't
  yield individual element screenshots. The full-page screenshot is reviewed
  too, and Claude flags offending thumbnails visible in it — so nothing is
  missed, but some findings anchor to "Full public profile page" instead of
  an individual post.
- **Display names**: capture often returns og-title boilerplate ("x is on
  Snapchat!") as bio — that's the real public bio surface on the web profile.
  Creator display name for the PDF is set via `snapstar add --name`; when
  omitted it defaults to the username (we've been correcting it post-hoc by
  editing `creator_name` in the manifest + review JSON and re-running
  `snapstar report` — costless, no API calls).
- **not_found / bot_wall creators still get a PDF** saying "not audited —
  manual check needed" and appear in the roster overview with that status.
- **Cost**: ~1–3¢ per image on Sonnet; a rich profile ≈ 10–25¢, an add-card
  ≈ 2–4¢. Report regeneration is free (no API).
- **Snapchat markup changes**: every selector/extraction is try/except'd;
  worst case you get profile_full only. Check `TILE_SELECTORS` first if tile
  counts drop to zero across many profiles.
- `output/` is gitignored (creator captures/reports are sensitive);
  the roster overview rebuilds from whatever is in `output/reviews/`.

## State as of handoff (2026-10-30)

Audited so far (in `output/` on this machine, not in git):
real creators — Alarah (@alarahxo, Needs cleanup: 2 high), Sarah
(@sarahs_worldx, Major cleanup: 1 critical + 2 medium), Anllela Sagra
(@anllela_sagra, Major cleanup: 1 critical); plus 4 celebrity/system test
entries (Kylie Jenner, Loren Gray, Demi Rose=not_found, Snapchat Official)
that can be deleted by removing their files from `output/captures/` and
`output/reviews/`, then re-running `snapstar report`.

Verification snapshot: all 12 tests green; capture, review, and report all
validated live end-to-end (2026-09-29 onward).
