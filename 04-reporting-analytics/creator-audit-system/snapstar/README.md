# snapstar-review

ALTR's Snapchat **verification-readiness audit**. Before a creator applies for the
gold star, this tool captures everything the public can see on their Snapchat,
flags anything explicit or even slightly suggestive (plus adult-platform links,
paid-content solicitation, watermarks, bio innuendo), and produces an
**ALTR-branded PDF report** the creator can follow to clean up their account —
one report per creator, plus an internal roster overview for the team.

## Pipeline

```
roster.csv ──▶ capture ──▶ review ──▶ report
              (Playwright   (Claude     (branded PDFs in
               screenshots   vision      output/reports/)
               of the public rubric)
               web profile)
```

1. **capture** — drives a real Chromium browser to `snapchat.com/@username`,
   screenshots the profile, public Stories, and Spotlight tiles, and extracts
   the bio/display name into `output/captures/<username>/manifest.json`.
2. **review** — sends every image and text field to Claude with a
   verification rubric; each item gets a severity
   (`critical/high/medium/low/clean`), categories, a plain-English rationale,
   and the exact in-app removal step. Results land in `output/reviews/`.
3. **report** — renders per-creator PDFs (cover, readiness badge, itemized
   findings with screenshots, pre-application checklist) and an internal
   roster summary PDF into `output/reports/`.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium

# API key for the review stage
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

## Usage

```bash
# audit ONE creator end-to-end (the usual flow)
snapstar add janedoe --name "Jane Doe"
# re-audit after they clean up:
snapstar add janedoe --name "Jane Doe" --force

# or a whole roster at once
snapstar run --roster roster.csv

# or stage by stage
snapstar capture --roster roster.csv
snapstar review                 # skips already-reviewed creators; --only/--force to control
snapstar report

# see the report design without touching Snapchat or the API
snapstar demo
```

Each audit adds the creator to the internal roster-overview PDF, which
accumulates into a running status tracker. `roster.csv` columns:
`creator_name,snap_username,notes` (see `roster.example.csv`).

## Branding

Reports use the ALTR brand kit (`assets/`): charcoal `#232321`, cream
`#eaebdd`, mint accent `#c8f2e6`, the cropped wordmark + mint "A" glyph, and
techno-mono labels. Drop `assets/altr-logo.svg`/`.png` to override the
wordmark (e.g. with a vector master). Colors/typography live in
`snapstar_review/templates/styles.css`; report copy in the two `.html.j2`
templates. `config.yaml` sets the review model, capture pacing, severity
weights, and the "prepared by"/contact lines.

## What the audit can and can't see

- ✅ Everything Snapchat exposes publicly on the web: bio, display name,
  avatar, public Stories, Spotlight posts.
- ❌ Private accounts, friends-only stories, in-app-only surfaces (Snap Map,
  etc.). Each report says this and ends with a manual in-app checklist.
- Extra screenshots can be added per creator in
  `output/captures/<username>/manual/` before running `review` — they're
  included automatically.

## Notes

- Capture paces itself (`capture.delay_seconds`) and retries once on a bot
  wall; profiles that still fail are marked **"not audited — manual check
  needed"** in the reports instead of failing the run.
- Claude's review is a first pass: borderline items are labeled as judgment
  calls, and the guidance to creators is "when unsure, remove."
- `output/` is gitignored — it contains creator captures and reports.

## Tests

```bash
pytest
```
