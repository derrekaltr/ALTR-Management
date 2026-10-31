# ig-audit

A repeatable Instagram account compliance audit system for content-creator clients
whose accounts keep getting flagged, restricted, or reach-limited.

## How to use

In a Claude Code session in this repo, with the Claude Chrome extension connected
and Chrome logged into Instagram:

```
/audit https://www.instagram.com/<handle>/     # single-account deep dive
/onboard <client name> + all known handles     # full multi-platform onboarding audit
```

`/onboard` audits the five core platforms as first-class accounts — Instagram,
TikTok, YouTube, Snapchat (graded for Snap Star review readiness per rubric
07), Facebook (incl. monetization eligibility per rubric 08) — each on its own
enforcement system, in one PDF led by a platform grade matrix. Other linked
platforms (Twitch/Kick/X) are noted in the funnel map only, not audited.

Claude will browse the profile (bio, link-in-bio one hop deep, pinned + ~12–20 recent
posts/reels), capture evidence screenshots, score everything against the policy
rubric, and produce two files in `reports/`: the working markdown report and an
**ALTR-branded client-ready PDF** (`<handle>-<date>.pdf`) — dark-theme cover page,
severity badges, embedded evidence screenshots per finding, per-post findings with
the exact policy each item trips, and three fix tiers per finding (adjust / rework /
delete), including concrete caption rewrites and recut instructions.

See `reports/chazcartii-2026-09-12.pdf` for a full real example.

### Branding
The visual system is the real ALTR brand, extracted from **altrmgmt.com**:
charcoal `#1D1D1B` pages, cream `#FFFFF0`/`#E8E8D9` text, sage `#586F69`
(legible tint `#9DB4AC`), heavy condensed uppercase display headlines, mono
labels, and the actual ALTR mark (`brand/logo-mark.png`, from the site's
headerLogo.png). All tokens live at the top of `brand/brand.css`; the brand name
string is `BRAND_NAME` in `scripts/render_pdf.py`. Layout rules: one section per
page, figures/quotes/rows never split across pages. Evidence screenshots
referenced with relative paths (`assets/<handle>/…`) are inlined into the PDF
automatically. Re-render any report with:

```
python3 scripts/render_pdf.py reports/<file>.md
```

## Repo layout

- `.claude/skills/audit/` — the `/audit` command (browse → score → report workflow)
- `.claude/skills/onboard/` — the `/onboard` multi-platform onboarding workflow
- `rubric/` — the scoring knowledge base:
  - `00` how Instagram enforcement actually works (strikes vs. silent reach demotion)
  - `01` sexually suggestive / adult-adjacent content
  - `02` peptides, GLP-1s, regulated goods
  - `03` POV smart-glasses / street-harassment-pattern content
  - `04` general reach-killers + recovery mechanics (every audit, every niche)
- `templates/report-template.md` — single-account report · `templates/onboarding-template.md` — multi-platform onboarding report
- `reports/` — finished audits (gitignored by default? no — kept in repo; add to
  .gitignore if client confidentiality requires)

## Keeping the rubric current

Meta updates the Community Standards and Recommendation Guidelines several times a
year. When enforcement behavior seems to shift, ask Claude to re-verify the rubric
against Meta's current published policies (Transparency Center) and update the files.
The rubric was last grounded: September 2026.

## Scope & limits

- Audits see what a logged-in viewer sees: no Account Status internals, DMs, stories,
  or Insights. The report tells the client exactly what to screenshot and send
  (Account Status, non-follower reach %) — a re-audit with those is much sharper.
- Private accounts: the client must accept a follow from the auditing account, or
  provide screen recordings.
- All recommendations target genuine policy compliance. This system deliberately does
  not produce classifier-evasion tactics (algospeak, hidden funnels, etc.) — those
  convert reach demotions into account bans.
