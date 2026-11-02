# IG Trending Sound Promo — One-Pagers

Two Letter one-pagers for the ALTR Media trending-sound product, one per audience:

| File | Audience | Top 20 | Top 10 | Top 5 |
|---|---|---|---|---|
| `ALTR-Trending-Sound-Promo-Wholesale.pdf` | Wholesale · Resellers | $2,000 | $3,000 | $4,000 |
| `ALTR-Trending-Sound-Promo-Artists.pdf` | Artists · Labels | $3,000 | $4,000 | $5,500 |

Deliverables are identical across both audiences — only the price column changes. Both sheets
are generated from one spec in `build.js` so they cannot drift apart.

## Rebuild

```
node build.js
```

pandoc is not used here; `build.js` writes the HTML directly and prints it through headless
Chrome — the same HTML → Chrome → Skia route the 2026 pitch decks were rendered with. Typeset
in the deck fonts (Bricolage Grotesque, Space Mono) on the palette from
`01-clients-onboarding/mikayla-pricing-deck/deck/build.js`.

The build **fails loudly if a sheet no longer fits on one page.** Chrome silently shrink-to-fits
overflowing content, which is how the first draft ended up rendering at ~79% scale. It also
reports slack above the footer so the layout can be tuned back up:

```
wrote ALTR-Trending-Sound-Promo-Wholesale.pdf (217 KB) — 0px slack above the footer
both sheets fit one page at 1:1
```

Decorative orbits live inside a clipped `.bg` layer for the same reason — bleeding them past
the page edge counts as overflow.

## Editing

- **Prices** — `SHEETS` in `build.js`.
- **Deliverables** — `SPEC`. Shared by both sheets by design.
- **Contact** — `CONTACT`, one place, both sheets follow.
- **Copy** — `RUN` (the 5-day timeline) and `KNOW` (expectation-setting).

## Open items

- **Contact block is a placeholder.** Currently `derrek@altrmgmt.com` + `quote.altrservices.com`.
  The URL is the *Services* domain on an ALTR **Media** sheet — the same cross-brand problem
  flagged in [pitch-deck-review](../pitch-deck-review/README.md) §3.2. Worth settling once and
  applying to the decks and these sheets together.
- **The theme-page example is deliberately generic.** The source note named a specific large
  comedy page in the network; these sheets say "a comedy page where the joke has to land"
  instead, since the wholesale sheet goes to resellers. Put the name back in `KNOW` if the
  credibility is worth more than the disclosure.
- **"2,000+ owned pages"** matches the Media deck. The source note said "thousands" — if the
  real figure has moved, change it in both places.
- **Dark only.** A light/print variant would be a palette swap in `style.css` if one is needed
  for physical leave-behinds.
