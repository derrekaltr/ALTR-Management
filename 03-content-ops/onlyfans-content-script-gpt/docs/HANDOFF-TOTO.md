# Handoff — GPTease Personas for the Weekly Content-Outline System

**For:** Toto H
**From:** Derrek
**Date:** August 20, 2026
**Ask:** Build one GPTease persona per creator — same five girls as your ChatGPT IG-DM GPTs — so our weekly content packs come out in each girl's actual voice.

---

## 1. What we're doing and why

Our content briefs to creators have been bland: "film a 5-minute video, send 3 photos."
We've replaced that with a weekly pipeline that produces **structured PPV filming briefs**
— the full asset drip in send order (photos, videos with durations, voice notes placed
between visuals), plus framing/wardrobe/lighting notes. The chat team pairs these with
the sexting scripts separately; the briefs are what the girls actually film from.

The pipeline:

1. **GPTease** (gptease.ai) generates the ideas. It's an uncensored AI built for adult
   creators — no refusals on our content, unlike ChatGPT. Derrek's account is already
   set up and the workflow is proven (first live week for Valerie is done).
2. Every week, each girl gets **9 new ideas: 3 per content level** (levels below).
3. Ideas land in a branded site the team shares + a per-girl PDF pack we hand her:
   - Site: https://altr-content-outlines.vercel.app
   - Example PDF: https://altr-content-outlines.vercel.app/valerie-bragg/2026-08-17/ALTR-valerie-bragg-2026-08-17.pdf
   Look at the Valerie pack first — it shows exactly what the personas will be producing.

**Why personas matter:** the pilot week ran on the default persona. Structure was great,
but the voice-note lines are generic. With a trained persona per girl, the spoken/voice
content comes out sounding like *her* — same reason you trained the IG-DM GPTs on each
girl's real messages.

## 2. The three content levels (hard rules)

Every idea is generated *at* one level and must never exceed it. Each girl has an
assigned comfort floor; she only films ideas at or above her floor.

| Level | Name | Rule |
|---|---|---|
| 1 | Non-Nude / Implied | Never nude. Hand bra, strategic covering, implied framing only. |
| 2 | Topless | Topless allowed. Nothing below the waist, ever. |
| 3 | Full Nude | Full nude allowed. |

## 3. The five personas to build

Same five as your ChatGPT GPTs — mirror the same voice/personality work you already did
there. If you still have the writing samples and instruction blocks from the GPT builds,
reuse them; that's most of the work already done.

| Creator | Handle | Existing GPT to mirror |
|---|---|---|
| Alex Paige Moore | @alexpaigemoore | "Alex Paige Moore" (IG DMs) |
| Shayna Holt | @shaynaholt | "Shayna Holt" (IG DMs) |
| Sarah Henderson | @Sarah.h44 | "Sarah Henderson" (IG DMs) |
| Anllela Sagra | @anllela_sagra | "Anllela Sagra" (IG DMs, EN/ES) |
| Valerie Bragg | @valeraexo | "Valerie Bragg" (IG DMs) |

**Plan limit:** the account is on Pro (3 persona slots, 500 requests/mo). All five need
**Power** ($10/wk, 10 slots, 3,000 requests/mo) — Derrek to approve the upgrade, or
start with the top 3 girls and paste profile blocks into chat for the other two.

## 4. How to build a persona in GPTease

gptease.ai → log in → **Personas** (left sidebar) → **New Persona**.

Two routes:
- **Advanced Customization** (preferred): name → description → voice details.
- Or write a one-line generation prompt and let it draft, then edit.

Per persona:
1. **Name:** stage name + handle, e.g. `Valerie Bragg (@valeraexo)`.
2. **Description:** 2–4 sentences — archetype (GPTease's style families: Flirty & Playful,
   Dominant & Bold, Sweet & Caring, Calm & Sensual, Luxury & Elegant, High Energy),
   her niche, how she talks. Same personality definition as her GPT.
3. **Voice training:** paste 5–10 of her real captions/DMs — the same samples you used
   for the GPTs. This is what makes voice notes sound like her.

Note: GPTease personas are a single description + writing samples — simpler than the GPT
builder. Don't port the GPT's operational instructions (draft-review rules etc.); just
port the personality and voice. The outline *format* is enforced by our saved prompt,
not the persona.

## 5. Fill out her profile file (the other half of the "personality")

The repo (`content-scripts`) has one folder per girl with a `profile.md` — currently all
TBD. This is the production side the persona doesn't cover, and the weekly runs read
from it. For each girl fill in:

- **Content level (floor):** 1, 2, or 3 — get this confirmed by her manager, not guessed
- **Archetype / vibe** (should match the persona description)
- **Niche & themes that work** (gym, luxury, girl-next-door, etc.)
- **Hard boundaries / do-not list** — anything she won't film regardless of level
- **Filming setup:** locations she has access to, props, lighting, solo/BG
- **Comfortable video length** and **voice-note comfort**

Full template: `prompts/persona-setup-guide.md` in the repo.

## 6. What happens after you're done

Weekly (automated from Derrek's machine): the saved prompt runs once per girl per level
in GPTease with her persona selected → 9 briefs each → branded site + PDF pack update
automatically. Master prompt lives at `prompts/weekly-outline-prompt.md` and is saved in
the GPTease Prompt Library.

**Definition of done per girl:** persona created and trained on her samples ✅ +
`profile.md` filled in ✅. Ping Derrek as each one is ready — the girl gets added to the
next weekly run.

Questions → Derrek. For what "good output" looks like, the Valerie pack above is the bar.
