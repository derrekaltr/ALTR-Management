# Case Cards

Three generators share one ALTR design system:

- `generate.mjs` — client case flashcards (`cases/*.json` → `output/*.png` + `.pdf`)
- `offers.mjs` — marketplace offer cards (`offers/*.json` → `output/offers/*.png`); each offer shows the service, price (hero), and TAT, with optional `details`/`notes`; `platform` picks the YouTube/Instagram/TikTok/Snapchat look or `house` for cross-platform ALTR offers
- `avatars.mjs` — group-chat profile pictures (`output/avatars/*.png`), monogram + SERVICES, circle-crop safe

Branded PNG flashcards for client cases — built to be dropped straight into Telegram / WhatsApp / iMessage group chats instead of raw text.

## Usage

```bash
npm install && npx playwright install chromium   # one-time setup
node generate.mjs cases/my-case.json             # → output/my-case.png + .pdf
node generate.mjs cases/*.json                   # batch
```

Every case produces a PNG (paste straight into chat) and a matching PDF — same design, but any `link` on the card is clickable in the PDF.

## Case file format (`cases/<name>.json`)

```json
{
  "platform": "youtube | instagram | tiktok | snapchat",
  "category": "recovery | removal",
  "service": "Unban | Unappealed Unban | Restriction Removal | Custom Verification | ...",
  "caseType": "the specific ban/restriction/target being worked",
  "status": "In Progress",
  "client": "Client name",
  "handle": "@handle",
  "link": "https://... (page/channel URL — clickable in the PDF)",
  "details": { "Any Label": "Any value", "...": "shown as rows" },
  "credentials": { "Email": "...", "Password": "..." },
  "notes": "optional free text",
  "size": "portrait (optional — 1080x1350 instead of square)"
}
```

- `category: "removal"` switches the card to the red hazard treatment (takedown work).
- `status` auto-colors: done/recovered/removed → green, in progress → amber, submitted/pending → blue, issue/denied → red.
- `details` and `credentials` are free-form key/value — whatever the case needs.
- For YouTube cases, always include the ban type and appeal status ("Appeal": "Never filed / Denied once / …") — different bans and appeal states route differently, and notes should say which route applies.
- Cards auto-compact when content runs long; if the notes still wouldn't get at least 2 lines, the card automatically upgrades to 1080×1350 portrait (unless `size` is set explicitly).

## Branding

House brand lives in `cards/brand/config.json` with the real ALTR assets in `cards/brand/assets/` (trimmed wordmark + monogram in mint `#B6F2E5`, cream `#EBECDC`, and charcoal `#1D1D1B`). Dark cards use the mint marks; the light Snapchat card uses the charcoal ones. Platform looks live in `cards/templates/*.html` — one file per platform, shared chassis in `base.css`. Add a platform by copying a template and registering it in `generate.mjs` (`PLATFORMS`).
