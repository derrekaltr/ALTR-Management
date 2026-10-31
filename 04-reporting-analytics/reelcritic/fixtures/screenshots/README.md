# Insights screenshots

Instagram only exposes three things **in the app**, never in the API:

1. **Retention chart** — Reel → *View insights* → scroll to the line chart ("the flatter the line, the more engaged"). Added Aug 24 2025.
2. **Views by source** — Reels tab / Explore / Home / Profile / other.
3. **Followers vs non-followers** — share of views from people who don't follow you.

Capture them as PNG/JPG and run:

```bash
npx tsx src/cli/index.ts screenshot <reelId> path/to/retention.png path/to/sources.png
```

The extraction is stored in `data/screenshots/<reelId>.json` and merged into the Reel on the next `analyze`.
Filename convention (optional): `<reelId>-retention.png`, `<reelId>-sources.png`.

No real screenshots are committed here (privacy). Tests use the extraction objects embedded in `fixtures/sample-account.json` (`r14` plateau/loop, `r18` cliff).
