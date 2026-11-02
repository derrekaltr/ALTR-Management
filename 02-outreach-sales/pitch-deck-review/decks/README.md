# Deck Archive — ALTR 2026 Pitch Decks

The two decks the review in [`../README.md`](../README.md) covers, archived **byte-for-byte as
received**. Nothing here has been modified, compressed, re-rendered, or re-saved.

| File | Slides | Size | Created |
|---|---|---|---|
| `ALTR-Management.pdf` | 13 | 28,999,507 bytes (27.7 MB) | 2026-09-17 16:32 EDT |
| `ALTR-Media.pdf` | 13 | 26,072,680 bytes (24.9 MB) | 2026-09-17 16:32 EDT |

```
SHA-256
0198c2ac704b65ccc1cbcce6d9663c3e8a1f52911fa5b10056285e112d89646a  ALTR-Management.pdf
d8276f64ca8b8f0086202b069001207dcfa650b7c8a88021f11ed6f61a176d02  ALTR-Media.pdf
```

## Why they are committed

**These PDFs are the only copy that exists on this machine.** Both were generated 2026-09-17
from HTML via headless Chrome (`Skia/PDF m153`), and the HTML source is not in any workspace or
repo under `~/conductor` — grepped for distinctive slide copy, zero hits. Until that source is
recovered or rebuilt, losing these files means losing the decks.

They arrived as Conductor chat attachments under `.context/attachments/`, which is gitignored
and scoped to a single workspace. They would not have survived the workspace being cleaned up.

## Notes

- Committed at full size on purpose — these are the print/present masters. Do not compress in
  place. The review recommends generating separate `-email.pdf` copies instead
  (see [`../README.md`](../README.md) §3.1; the Management file is over Gmail's 25 MB cap).
- `ALTR-Media.pdf` is ALTR Media Group material. It is archived here rather than in a Media hub
  repo because that repo does not exist yet — see the open item in
  [`06-ops-admin/TASKS.md`](../../../06-ops-admin/TASKS.md).
- Roughly 53 MB of binaries. This repo has no git-lfs; if the archive grows, that is the first
  thing to set up.
