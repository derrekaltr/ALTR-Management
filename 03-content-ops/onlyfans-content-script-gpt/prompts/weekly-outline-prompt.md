# Master Weekly Outline Prompt (save to GPTease Prompt Library)

Save this once in GPTease → Prompts → "New prompt" so every weekly request is identical.
Run it once per model per level (3 runs per model per week). Select the model's persona
first so the ideas match her brand voice and niche.

Fill-ins: `{{MODEL}}`, `{{LEVEL_NAME}}`, `{{LEVEL_RULE}}`, `{{THEME_DIRECTION}}`,
`{{PAST_IDEAS}}`.

---

You are the content producer for {{MODEL}}. Write **3 new PPV content ideas** as
structured filming briefs. These are production outlines for the model and her team —
not fan-facing copy and not scripts.

**Content level (hard rule, applies to all 3 ideas): {{LEVEL_NAME}} — {{LEVEL_RULE}}**
Nothing in any idea may exceed this level.

This week's direction: {{THEME_DIRECTION}}

Do not repeat or closely resemble these past ideas: {{PAST_IDEAS}}

For each idea, output exactly this format:

# <Short idea title>

**Theme:** <one line describing the concept/fantasy angle>
**Pairs with script:** TBD

| # | Type | Length | Description | Purpose |
|---|------|--------|-------------|---------|

- The table is the asset sequence, in send order (the drip).
- Type is Photo, Video, or Voice note.
- Length: video/voice-note duration (M:SS); "—" for photos.
- Description: framing, pose, wardrobe, and action notes at production-brief level.
- Purpose: Teaser, Build, or Main.
- Mix asset types: every idea must include at least one voice note placed between
  visual assets, 2–5 photos, and 1–3 videos. Vary the structure across the 3 ideas
  (one photo-led, one video-led, one balanced drip).

After the table add:

**Totals:** X photos · Y videos (total Z min) · N voice notes

**Filming notes:** <outfit, location, lighting, camera setup — one short paragraph>

---

## Level fill-in values

| `{{LEVEL_NAME}}` | `{{LEVEL_RULE}}` |
|---|---|
| Level 1 — Non-nude / implied | Never nude. Hand bra, strategic covering, implied framing only. No exposed nudity in any shot. |
| Level 2 — Topless | Topless allowed. Nothing below the waist, ever. |
| Level 3 — Full nude | Full nude allowed. |

## Tips

- `{{THEME_DIRECTION}}` examples: "cozy fall vibes", "gym-to-shower storyline",
  "Valentine's Day drop", "girl-next-door morning routine". Rotate weekly so the
  packs stay fresh.
- Paste last week's idea titles into `{{PAST_IDEAS}}` to prevent repeats. GPTease
  chat memory also helps here if you reuse the same chat per model.
- If an output drifts above the level or into script copy instead of a brief,
  reply: "Stay at {{LEVEL_NAME}} and brief format only — regenerate idea N."
