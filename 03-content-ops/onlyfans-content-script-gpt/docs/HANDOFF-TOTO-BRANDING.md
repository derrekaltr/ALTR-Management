# Handoff — ALTR Report Branding

**For:** Toto H
**From:** Derrek
**Purpose:** Everything needed to produce ALTR-branded reports (script outlines, weekly
content packs, quotes, any internal doc we hand to creators) that are indistinguishable
from the existing ones.

**Live references:** the content site https://altr-content-outlines.vercel.app and the
original quote doc style it's built from. **Start here:** copy
`design/altr-report-template.html` — a single self-contained file (logos embedded, all
components included) — and replace the placeholder content. Tokens live in
`design/altr-tokens.css`.

---

## 1. The brand in one paragraph

Dark editorial meets technical spec-sheet. Near-black pages, warm bone type, one mint
accent used like a highlighter — never as a background except the single mint panel per
page. Big headlines are heavy, wide, and uppercase; everything small is monospaced,
uppercase, and letter-spaced like a data label. Hairline dividers, film-grain texture,
"Confidential · Internal" framing. It should feel like a classified production document,
not a marketing page.

## 2. Color

| Token | Value | Role |
|---|---|---|
| `--ink` | `#1d1d1b` | Page background. Always. Never white, never gray. |
| `--ink-raise` | `#242422` | Raised cells: stat tiles, summary grids. |
| `--ink-line` | `rgba(235,236,220,0.14)` | Standard hairline dividers. |
| `--ink-line-soft` | `rgba(235,236,220,0.08)` | Secondary dividers. |
| `--bone` | `#ebecdc` | All text and display type. |
| `--bone-faint` | `rgba(235,236,220,0.9)` | Secondary text, labels, captions. |
| `--mint` | `#b6f2e5` | THE accent: kickers, section numbers, links, key data, highlight rows, the mint panel. |
| `--mint-wash` | `rgba(182,242,229,0.06)` | Background tint for highlighted rows/chips. |

Rules:
- Text on mint is always ink (`#1d1d1b`), never white.
- Mint is seasoning: if more than ~10% of a page is mint (excluding the one mint panel),
  it's too much.
- Solid `--bone` 1px border marks the TOP of every major table/list; internal dividers
  use `--ink-line`.

## 3. Typography

Google Fonts (one link, both families):
```
https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,62..125,100..900;1,62..125,100..900&family=Spline+Sans+Mono:wght@400;500&display=swap
```

**Archivo** (variable) — display + body:
- Headlines: weight 800, `font-stretch: 118%`, UPPERCASE, line-height 1.0,
  letter-spacing −0.015em. h1 `clamp(42px, 6.6vw, 76px)`; h2 `clamp(24px, 3vw, 33px)`;
  stat values 40px. The second half of a headline gets mint via `<span class="alt">`.
- Body: weight 400, 15–17px, line-height 1.6, bone or bone-faint.

**Spline Sans Mono** — every label, kicker, chip, table header, meta line, legal line:
- UPPERCASE, 10–13px, letter-spacing 0.12–0.3em (the smaller the type, the wider the
  tracking). Weight 400, 500 for emphasis.
- If a piece of text is metadata about the content rather than the content itself,
  it's mono.

## 4. Logo assets

In `site/assets/` (also embedded in the template):

| File | Use |
|---|---|
| `altr-logo.png` | Masthead (26px tall) and footer (16px tall, 90% opacity). |
| `altr-ghost.png` | Hero watermark: absolute right, ~560px wide, **opacity 0.045**. |
| `altr-mark-dark.png` | Watermark inside mint panels: bottom-right, bleeding off, **opacity 0.10**. |

Never place the logo at high opacity as decoration — it's either functional (masthead,
footer) or a barely-there watermark.

## 5. Signature components

All present in `design/altr-report-template.html` — copy, don't rebuild:

1. **Masthead** — logo left; mono dept line + pill "Confidential · Internal" badge right; hairline below.
2. **Hero** — mono mint kicker with a 44px rule before it → giant two-tone headline →
   optional "Doc №" meta block top-right → row of pill chips (first chip `.accent`).
3. **Numbered sections** — mint mono number (`01`) beside an uppercase h2, then a
   one-to-two-line `.sec-sub` intro. Vertical rhythm: 100px between sections.
4. **Beat sheet** — the signature table: 4 columns (big number / mono type-chip + meta /
   description / mono-labeled purpose). Highlight the key row with `.is-ppv` (mint wash
   + 3px mint left rule + filled type chip). One or two highlighted rows max.
5. **Summary grid** — 4 stat tiles on `--ink-raise`: mono label, 40px stat (mint
   `<small>` for units), support note.
6. **Folder/link rows** — mono item name + small descriptor, mint "Open ↗" on the right,
   hover mint wash.
7. **Mint panel** — the one solid-mint block per page: mono label with rule, editorial
   display copy in ink, dark watermark bottom-right. Use it for the single most
   important message (psychology, filming notes, verdict).
8. **Footer** — small logo left; right-aligned mono legal: "Prepared by ALTR Talent
   Development · Confidential · For assigned creator only · Not for distribution".

## 6. Texture & motion

- **Grain**: every page gets the fixed SVG-noise overlay on `body::before` (opacity 0.6
  over a 5%-opacity noise rect). It's what keeps the dark from feeling flat. Snippet in
  the template and `design/altr-tokens.css`.
- **Reveal**: `.rise` animation (22px translate + fade, 0.85s, `cubic-bezier(0.22,1,0.36,1)`)
  with stagger classes `.d1`–`.d4` on masthead/hero elements only. Disabled in print.

## 7. Layout & responsive

- Content column max 1060px, 48px side padding (26px ≤880px, 18px ≤560px).
- Beat sheet collapses to 2 columns on tablet (description/purpose full-width below);
  summary grid 4→2→1 columns; ghost mark and doc-№ hidden on small screens.

## 8. Print / PDF

- `@page { size: A4; margin: 0 }`, `print-color-adjust: exact` — the dark ink IS the
  printed page; never invert to a light theme.
- PDF pages: 210mm × min 297mm, padding 13mm 15mm 11mm, one idea/topic per page,
  `page-break-after: always`. Tables with 7+ rows use the dense scale (see `packPage()`
  in `site/build.js`). Cover page: masthead → mono kicker → two-tone title → TOC rows.
- Generation: headless Chrome via `scripts/make-pdfs.sh` (`--print-to-pdf`, no header/footer).

## 9. Do / Don't

- **Do** keep pages sparse — the brand is restraint. When unsure, remove.
- **Do** put every label in mono-uppercase-tracked; every headline in stretched-800-uppercase.
- **Don't** use white backgrounds, drop shadows, gradients, or rounded cards (only pills
  and the 4px mint panel are rounded).
- **Don't** introduce new colors. Two surfaces, one text color, one accent.
- **Don't** use mint for body text or large text blocks — accent lines and labels only.
- **Don't** skip the grain overlay or the "Confidential" framing on creator-facing docs.

## 10. Downloads (no repo access needed)

Everything is hosted — grab what you need from any device:

| Link | What |
|---|---|
| https://altr-content-outlines.vercel.app/brand/altr-brand-kit.zip | **Full kit** — template + tokens + logos + this guide |
| https://altr-content-outlines.vercel.app/brand/altr-report-template.html | Self-contained report template (logos embedded, has a downloads section inside too) |
| https://altr-content-outlines.vercel.app/brand/altr-tokens.css | Design tokens |
| https://altr-content-outlines.vercel.app/brand/altr-logo.png | Wordmark (masthead/footer) |
| https://altr-content-outlines.vercel.app/brand/altr-ghost.png | Ghost watermark (use at 4.5% opacity) |
| https://altr-content-outlines.vercel.app/brand/altr-mark-dark.png | Dark mark for mint panels (use at 10% opacity) |

## 11. File map (repo)

| Path | What |
|---|---|
| `design/altr-report-template.html` | Self-contained starter — copy this for any new report. |
| `design/altr-tokens.css` | Canonical tokens with usage notes. |
| `design/assets/altr-*.png` | Logo/watermark assets. |
| `site/assets/style.css` | Production stylesheet of the live content site. |
| `site/build.js` → `packPage()` | PDF page layout reference (A4 + dense mode). |
