# Pitch Deck Review — ALTR Management & ALTR Media (2026)

Review of the two 13-slide pitch decks, 2026-11-02. **Read-only review — neither PDF was
modified, compressed, or committed.** The decks live outside the repo; this document is the
only artifact.

---

## 1. What was reviewed

| | ALTR Management | ALTR Media |
|---|---|---|
| File | `ALTR-Management.pdf` | `ALTR-Media.pdf` |
| PDF title | `ALTR MANAGEMENT · Pitch Deck` | `ALTR MEDIA · Pitch Deck` |
| Slides | 13 | 13 |
| Size | 1440 × 810 pt (16:9) | 1440 × 810 pt (16:9) |
| File size | **28,999,507 bytes (27.7 MB)** | **26,072,680 bytes (24.9 MB)** |
| Created | 2026-09-17 16:32 EDT | 2026-09-17 16:32 EDT |
| Toolchain | HTML → HeadlessChrome 153 → Skia/PDF | same |

Every slide of both decks was inspected as a rendered image, not just as extracted text.

**There is no editable source.** Grepped every workspace and repo under `~/conductor` for
distinctive slide copy ("Stop renting attention", "Six pillars", "brand architects") — zero
hits. Only the PDFs exist. Every fix listed below currently requires rebuilding the slide from
scratch in whatever tool produced it. See §7.

---

## 2. Verdict

**These are good decks. Don't rewrite them — correct them.**

The design system is real and it holds across 26 slides without drifting: corner brackets,
numbered section eyebrows in mono (`03 / THE NETWORK ——`), the `ALTR | MEDIA · 04 / 13` footer,
the faint grid, the circled logo mark, the hatch marks bottom-right. The "window chrome" motif
(three dots, a header label, a right-aligned status chip) is used consistently for anything
that represents live data — the rented-vs-owned chart, the network console, the team panel, the
campaign report. That is a genuine visual argument: it makes the claims feel instrumented.

The palette is also *on-system* — the light slides use the same values as the existing ALTR
deck palette in `01-clients-onboarding/mikayla-pricing-deck/deck/build.js`
(`bg EBECDC`, `mint B6F2E5`, `ivory FFFFF0`, and the `purple 7C41F1` that shows up as the third
window-chrome dot). Whoever built these decks was working from the established brand, not
inventing a new one.

Specific things that work:

- **The VS slides (Management 11, Media 11) are the sharpest argument in either deck.** Old
  playbook in grey with × marks, the ALTR way in white with ✓ marks, a `VS` token between two
  cards. It does in one glance what the preceding five slides do in paragraphs.
- **Media 02 carries the whole thesis in one image** — the rented line peaking at `AD BUDGET
  ENDS` then decaying, the owned line crossing it and compounding. Nothing else in the deck
  needs to work as hard.
- **The positioning lines are real lines**, not filler: "Creators are brands. Not accounts.",
  "Agencies rent attention. We own it.", "The moat is ownership.", "Viral is a process, not
  luck.", "Losers die quietly in the lab."
- **The shared ecosystem slide (12 in both) is handled well.** Same three rows, but each deck
  highlights its own row in mint. Someone who receives both decks sees the family resemblance
  as intentional rather than lazy.
- **Light-slide rhythm breaks are well placed** — Management 03 (mint) and 10 (bone), Media 03
  (mint), 08 (ivory) and 10 (bone). They land exactly where the deck needs a breath.

---

## 3. Ship-stoppers

Fix these before the next send.

### 3.1 The Management PDF cannot be emailed — 27.7 MB over a 25 MB cap

Gmail, Outlook and most clients cap attachments at 25 MB. `ALTR-Management.pdf` is 27.7 MB and
will be rejected or silently converted to a Drive link. `ALTR-Media.pdf` at 24.9 MB clears it by
about 140 KB — that is not margin, that is luck.

The weight is raw full-resolution imagery: the chain hero render (used four times, see §6.1),
twelve celebrity headshots and eight brand logos on Management 09. None of it needs to be at
source resolution for a 1440 × 810 slide. Downsampling to 150 dpi should land both decks in the
3–6 MB range with no visible loss on screen or in a normal projector.

**Recommendation:** keep the current files as the print/present masters and produce a second
`-email.pdf` of each. Do not compress over the originals.

### 3.2 Both decks send prospects to the wrong brand's domain

Both close slides show the same CTA:

> `quote.altrservices.com ↗`

That is the **Services** domain. The Management deck has its own live domain — `altrmgmt.com`
resolves (Vercel) — and it isn't used anywhere in the deck. After twelve slides carefully
establishing that Media, Management and Services are three separate engines with *"separate
brands, separate contracts"* (Media 12), the final instruction sends everyone to the third one.

A Media prospect who wants to buy network distribution lands on a page branded for IG recovery
and verification. That is the single highest-cost error in either deck, because it sits on the
one slide where the prospect is deciding whether to act.

Checked live 2026-11-02: `quote.altrservices.com` resolves (Cloudflare), `altrmgmt.com`
resolves (Vercel), `altrholdings.com` is NXDOMAIN — so the umbrella domain chosen in
[domain-research](../../06-ops-admin/domain-research/README.md) is not yet registered and is not
an option for the CTA today.

### 3.3 The close slides have no contact details

Both closes carry a URL and nothing else. No name, no email, no phone, no Instagram handle,
no calendar link. If the deck is forwarded internally — which is exactly what happens to a good
deck — the recipient has no way to reach a person. Add a name and an email at minimum.

### 3.4 Management 07: the headline and the chart describe different time periods

The proof panel is chipped `FIVE CONSECUTIVE MONTHS` in its header, and under that header sits
both the stat stack and the chart:

| Stated in the panel | Readable in the chart |
|---|---|
| `GROSS ON-PLATFORM $5.97M` | M1 $95K → M2 $167K → M3 $217K → M4 $235K → M5 $238K |
| `NET $4.78M` | **five-month net total ≈ $952K** |
| `FAN MESSAGING $3.8M` | |
| `5-MO NET GROWTH +150%` | ✓ matches (95 → 238 = +150%) |

The internal ratios are clean and defensible — net is 80.1% of gross, which is exactly the
platform cut, and fan messaging is 79% of net. The growth figure matches the chart. **The
numbers are fine; the label is wrong.** $4.78M net against a five-month chart totalling ~$952K
means the stat stack is lifetime-to-date and the chart is the last five months, but the header
chip claims the whole panel is five months. Any prospect who adds the five bars reads the
headline as inflated roughly 5–6×, and once they think one number is inflated they discount all
of them.

Secondary: the panel mixes units. It is titled `GROSS ON-PLATFORM`, but the M5 tooltip reads
`$238K NET` and the growth row reads `5-MO NET GROWTH`. Pick gross or net for the chart and say
which.

**Fix:** label the stat stack `LIFETIME TO DATE` (or `SINCE ONBOARDING`) and the chart
`LAST 5 MONTHS · NET`. No number has to change.

### 3.5 Management 09: third-party names and marks used as endorsement

The roster slide shows twelve celebrity headshots under the header
`PAST & PRESENT CLIENTS · TALENT` — Floyd Mayweather, Diplo, Snoop Dogg, Wiz Khalifa, The
Chainsmokers, Tiësto, Big Sean, Polo G, Swae Lee, Paris Jackson, Lele Pons, Big Meech — plus
eight brand logos under `BRAND WORK`: Red Bull, Casamigos, Revolve, Sony Music, Universal Music
Group, Rolling Loud, Liquid Death, Walmart.

Two separate problems:

1. **Permission.** Names, likenesses and registered marks are being used in commercial
   collateral as implied endorsement. Right-of-publicity and trademark exposure here is real
   and it is cheap to reduce — confirm which of these are contractually citable, and drop or
   relabel the rest.
2. **Implication.** `20+ CREATORS UNDER ACTIVE EXCLUSIVE MANAGEMENT` is set in 96pt directly to
   the left of those twelve faces. The slide reads as *"these are the 20+."* If the actual
   relationship is event work, brand campaigns, or past one-off engagements, the slide is
   overclaiming by adjacency even though no single line is false.

**Fix:** split the row honestly — `EXCLUSIVE ROSTER` (the actual 20+, even if unnamed) separate
from `WORKED WITH · EVENTS & CAMPAIGNS` (the names), and keep only marks you can evidence.

---

## 4. Data integrity

Every hard number in both decks, and whether the two agree.

| Claim | Management | Media | Status |
|---|---|---|---|
| 20+ exclusive creators | 01, 09, 13 | — | consistent |
| $5.97M flagship gross | 01, 07, 13 | — | see §3.4 |
| $4.78M net | 07 | — | **conflicts with chart — §3.4** |
| $3.8M fan messaging | 07 | — | see §3.4 |
| +150% 5-mo net growth | 07 | — | ✓ matches chart |
| LA · MIA content houses | 01, 04 | — | consistent |
| 2,000+ owned pages | 04, 05, 09, 11, 12, 13 | 01, 02, 03, 04, 12, 13 | consistent |
| 580,339 accounts reached | 08 (as "580K") | 09 (full figure) | ✓ agree |
| 1,013,909 impressions | 08 (as "1M+") | 09 (full figure) | ✓ agree |
| +529% impressions | 08 | 01, 09, 13 | ✓ agree |
| 98.8% non-followers | 08 | 01, 09, 11, 13 | ✓ agree |
| 572K reach from reels | — | 09 | Media only |
| +718% non-follower growth | — | 09 | Media only |

Cross-deck numbers are clean — rounding is the only difference and it rounds honestly. The one
real defect is §3.4.

### 4.1 The evidence base is one account and one campaign

Both decks rest on the **same single 30-day creator case** (580,339 / 1,013,909 / 98.8%), and
the Management deck adds exactly one managed account. Anyone who receives both decks sees the
identical proof twice, which makes the evidence base look thinner than it probably is.

Two gaps follow from that:

- **Management never says anything about the other 19+ creators.** No average result, no
  retention rate, no median revenue lift, no "a typical creator does X in month three." One
  flagship account is being asked to prove a 20-creator agency.
- **Media never states the network's actual scale.** The entire thesis is owned distribution at
  scale, and the deck says "2,000+ pages" nine times without once stating how many people those
  pages reach. A buyer's first question is *"what's the combined monthly reach of the network?"*
  and the deck has no answer on any slide. One aggregate figure — total followers across the
  network, or monthly impressions network-wide — would do more for the Media deck than any other
  single addition.

### 4.2 Media 03/04: the network console is illustrative

The console lists 21 handles (`music.daily`, `luxe.life`, `street.style`, `court.side`,
`moto.scene`…) with `▶ PUSHING` status chips. These read as representative placeholders rather
than real page names. That is a reasonable design choice — you probably don't want to expose the
real network — but it invites *"can I see the pages?"*, and the deck has no prepared answer.
Either label the panel `ILLUSTRATIVE` or have a response ready. The slide itself is the best
visual in the Media deck, so this is a talk-track note, not a design change.

---

## 5. Narrative

### ALTR Management (creator-facing)

`01 cover → 02 problem → 03 who we are → 04 six pillars → 05 your team → 06 creator evolution →
07 proof: one account → 08 proof: marketing engine → 09 roster → 10 the deal → 11 why → 12
ecosystem → 13 close`

- **Proof arrives at slide 7 of 13.** Slides 02–06 are five consecutive promise slides before a
  single number lands. For a cold creator who doesn't know ALTR, that is a long way to read on
  trust. Moving slide 08 (580K / 1M+ / 98.8% — the cleanest, least ambiguous proof in either
  deck) to position 3 or 4 would fix this without restructuring anything.
- **Slide 06 "The Creator Evolution" is the weakest slide.** A seven-step roadmap where step 06
  is *"Global mobility — investment-based U.S. visa pathways."* That is the furthest thing from
  the core offer, it is the hardest claim in the deck to deliver on, and it sits on a slide
  where nothing else is substantiated either. Either cut to five steps or be ready to explain
  the visa claim in detail — a creator who asks about it and gets a vague answer discounts the
  other six steps retroactively.
- **Slide 10 "The Deal" never states the take.** "Performance-aligned revenue share," "the take
  scales with the growth we actually drive," "no big retainers, no upfront management fees" — no
  percentage, no range. Defensible if the number is always negotiated, but the slide is titled
  *The Deal* and doesn't contain one, which invites the question immediately.
- **Minor contradiction on the same slide:** "We only win when you win" (headline) vs
  "Transparent add-ons … scoped and billed as needed" (item 03). Add-ons bill regardless of
  performance. A one-clause acknowledgement — *"at cost, never marked up"* or similar — closes it.
- **Audience is slightly mixed.** Slides 02–06, 09–10 speak to "you" the creator; the `PITCH
  2026` label, the proof slides and the ecosystem slide have an investor flavour. It works as a
  creator-recruitment deck. If it is also being used with investors it needs a different proof
  slide — roster economics, retention, revenue per creator, agency-level revenue — not one
  flagship account.

### ALTR Media (client/brand-facing)

`01 cover → 02 thesis → 03 mission → 04 the network → 05 who rides the engine → 06 service lines
→ 07 how a campaign works → 08 the feedback loop → 09 proof → 10 commercial models → 11 why →
12 ecosystem → 13 close`

Structurally tighter than Management, and the thesis lands on slide 2 instead of slide 7.

- **Slide 08 "The feedback loop" is buried.** *"Hooks get validated across thousands of posts
  before a single dollar of your momentum is spent on them. Winners become strategy. Losers die
  quietly in the lab."* That is the most defensible differentiator in either deck — it is the
  one thing a competitor with an ad budget structurally cannot copy — and it arrives eighth,
  after five slides of setup. It belongs at 03 or 04, right behind the thesis.
- **Slide 03 "Mission" is the one skippable slide.** Control / Deploy / Own restates slide 02
  with less force. If anything gets cut to make room for a network-scale slide (§4.1), cut this.
- **Slide 10 "Commercial models" has no anchors.** Six ways to buy, no numbers — not even a
  "campaigns from $X." For a deck whose job is to produce an inbound quote request, one starting
  price would qualify leads before they reach the form.
- **Slides 06 and 07 are thin.** Both are a single row of text in the top half with the bottom
  40% empty. The restraint reads as confidence elsewhere in the deck; on these two it reads as
  a slide that didn't finish.

---

## 6. Cross-deck consistency

### 6.1 The hero image appears four times

The same abstract chain render is the cover of both decks *and* the close of both decks. Anyone
who receives both — which is the explicit plan, given the ecosystem slide and the "full-stack
bundle" model — sees it four times. Each deck should have its own hero. The chain reads as
"ALTR" generally; it says nothing specific about either management or distribution.

### 6.2 The third company has two names, two slides apart, in the same deck

- Media **10**, model 06: *"**Media, Signal, and Management** combined as one engagement."*
- Media **12**: the third row is labelled **`SERVICES`**.

`ECOSYSTEM.md` calls it "ALTR Services (Signal)", so both are defensible in isolation — but not
two slides apart in one deck. Pick the client-facing name and use it everywhere. Given the CTA
domain is `altrservices.com`, **Services** is the consistent choice.

### 6.3 Typographic orphans in the mono labels

Two slides break a mono label across lines in a way that reads as a bug:

- Management **04**: `MONETIZATION TO WELLNESS. ONE` / `TEAM.`
- Media **04**: `OWNED NICHE PAGES ACROSS INSTAGRAM & SHORT-` / `FORM`

The Media one is worse — breaking on the existing hyphen of "short-form" looks like a rendering
fault. Both need a narrower container or a manual break.

---

## 7. Production

No HTML/CSS source exists for either deck anywhere on disk. Every correction in this document —
including a two-word label change on Management 07 and a URL swap on both closes — currently
requires rebuilding the slide from nothing.

This is the most expensive problem in the review, because it is the one that makes every other
problem expensive. Recommend recovering the source if it still exists in the originating tool,
or recreating it in-repo. The precedent is already here:
`01-clients-onboarding/mikayla-pricing-deck/deck/` (pptxgenjs `build.js` + Keynote `render.sh`),
and its palette constants already match these decks.

Not scoped as work here — flagged for a decision.

---

## 8. Prioritized fix list

| # | Fix | Where | Why |
|---|---|---|---|
| 1 | Point the CTA at the right brand's domain | both, slide 13 | §3.2 — wrong brand on the one slide that asks for action |
| 2 | Label the stat stack lifetime, the chart last-5-months | Mgmt 07 | §3.4 — currently reads as ~5× inflated |
| 3 | Produce ~3–6 MB `-email.pdf` copies; keep originals as masters | both | §3.1 — Management can't be attached at all |
| 4 | Split roster into exclusive roster vs worked-with; keep only evidenced marks | Mgmt 09 | §3.5 — publicity/trademark exposure + overclaim by adjacency |
| 5 | Add a name and an email to both closes | both, slide 13 | §3.3 — forwarded decks currently dead-end |
| 6 | Add one network-scale figure (total followers or monthly impressions) | Media, new slide | §4.1 — the core thesis is never quantified |
| 7 | Settle Services vs Signal; apply everywhere | Media 10 & 12 | §6.2 — contradicts itself two slides apart |
| 8 | Give each deck its own hero image | both, 01 & 13 | §6.1 — same render four times |
| 9 | Move the cleanest proof earlier (Mgmt 08 → ~04; Media 08 → ~04) | both | §5 — best evidence arrives too late in both |
| 10 | Fix the two mono-label line breaks | Mgmt 04, Media 04 | §6.3 — reads as a rendering fault |
| 11 | Add roster-level results, not just the flagship account | Mgmt, new slide | §4.1 — one account proving a 20-creator agency |
| 12 | Add a price anchor | Media 10 | §5 — six models, no numbers |
| 13 | Recover or rebuild editable source | — | §7 — makes fixes 1–12 cheap instead of expensive |

---

## Notes

- The Media deck is **ALTR Media Group** material and sister-company projects don't live in this
  repo per `CLAUDE.md`. This review covers both decks because they are one coordinated pitch set
  and the Media hub repo doesn't exist yet (see the open item in
  [06-ops-admin/TASKS.md](../../06-ops-admin/TASKS.md)). The *assets* were deliberately not
  filed here — only this review.
- Deck stats were read from the PDFs as rendered. Nothing in this document was verified against
  source platform statements, bank records, or contracts; §3.4 is a labelling conflict found
  inside the deck, not an audit of the underlying figures.
