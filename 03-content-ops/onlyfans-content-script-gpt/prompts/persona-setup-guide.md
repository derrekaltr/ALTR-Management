# GPTease Persona Setup Guide (for account managers)

Each model gets one GPTease persona so weekly outlines come out in her voice and match
her brand. **The account manager / chatter team fills this out** — not the model.

Plan note: the current Pro plan allows **3 personas**. All 5 models need the **Power**
plan (10 personas). Until upgraded, run the two extra models by pasting their profile
block (below) at the top of the chat instead of selecting a persona.

## Creating the persona (gptease.ai → Personas → New Persona → Advanced Customization)

1. **Persona Name** — the model's stage name + handle, e.g. `Valerie Bragg (@valeraexo)`.
2. **Description** — 2–4 sentences: her vibe/archetype (pick from GPTease's style
   families: Flirty & Playful, Dominant & Bold, Sweet & Caring, Calm & Sensual,
   Luxury & Elegant, High Energy), her niche, and how she talks.
3. **Voice training** — paste 5–10 real writing samples (her captions, DMs). More
   samples = better voice match.

## Per-model profile block

Fill this out in `content/<model-slug>/profile.md`. It is internal only (never
published to the site) and is the source of truth when prompting GPTease.

```markdown
# <Stage name> (@handle)

- **Content level (floor):** Level 1 / 2 / 3
- **Archetype / vibe:** e.g. Sweet & Caring girl-next-door
- **Niche & themes that work:** e.g. gym, cozy homebody, luxury travel
- **Hard boundaries / do-not list:** anything she will not film, regardless of level
- **Filming setup:** locations available, props, lighting, solo or BG content
- **Comfortable video length:** e.g. up to 10 min
- **Voice notes:** yes/no, comfortable style (teasing, GFE, dominant)
- **Persona status in GPTease:** created? trained on writing samples? (date)
```

## Weekly use

1. Open a chat, select the model's persona.
2. Run the saved Prompt Library prompt (`prompts/weekly-outline-prompt.md`) once per
   content level, filling in the level block and this week's theme direction.
3. Keep one long-running chat per model — GPTease's contextual memory reduces
   repeated ideas week to week.
