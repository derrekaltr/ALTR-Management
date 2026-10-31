# ALTR Creator Audit System — Operator Handoff

This repo turns a client's social links into ALTR-branded audit PDFs. You paste
links, Claude does the browsing/scoring/writing, you send the PDF. This file is
everything a new operator needs.

---

## 1. What this produces

Two workflows, run as slash commands inside Claude Code in this repo:

| Command | Use when | Output |
|---|---|---|
| `/audit <instagram-url>` | Deep dive on one account (reach collapse, flags, "shadowban," monetization) | `reports/<handle>-<date>.md` + `.pdf` |
| `/onboard <client name> + all known links` | Every new client | `reports/<client>-onboarding-<date>.md` + `.pdf` with a platform grade matrix |

**Audit scope is exactly five platforms:** Instagram, TikTok, YouTube,
Snapchat (graded as *Snap Star review readiness*), Facebook (always includes
the *monetization-eligibility* lens). Anything else a client links
(Twitch/Kick/X/etc.) is noted as funnel risk only — never audited or graded.

Reports are dark ALTR-branded PDFs: grade tiles, charts built from the
account's own public numbers, evidence screenshots placed beside the finding
they prove, per-post fix tiers (adjust / rework / delete), an action plan, and
a "what we need from the client" list. The PDFs are designed to be readable on
a phone — send them as-is.

## 2. Setup (once per machine)

1. **Mac with Google Chrome installed** (the pipeline drives headless Chrome).
2. **Claude Code opened in this repo.**
3. `pandoc` installed (`brew install pandoc`) — PDF rendering needs it.
4. First run auto-creates `.venv/` for the screenshot tool; if Python errors
   mention `websocket`, run:
   `python3 -m venv .venv && .venv/bin/pip install websocket-client pillow`
5. The Claude-in-Chrome extension is OPTIONAL. Everything runs headless and
   logged-out by default; the extension only adds logged-in views (useful for
   Facebook Pages and private accounts).

## 3. Running an audit — what to expect

- Paste the command; Claude browses public pages headless, screenshots
  evidence, scores against `rubric/`, writes the markdown, renders the PDF,
  and verifies the pages visually. A single audit takes several minutes; an
  onboarding (5 platforms + discovery) takes longer.
- **Always read the final summary**, then skim the PDF before sending.
- Every report ends with a client-asks section (Account Status screenshots,
  insights, dashboard panels). Collect those — they confirm the diagnosis in
  the platform's own words and sharpen the 30-day re-audit.

## 4. Known limitations (tell clients honestly)

- Audits see what a logged-out visitor sees: no stories/highlights content, no
  DMs, no internal analytics, hidden like counts stay hidden. The Reels tab's
  public view counts are the main reach evidence.
- **Facebook Pages are login-walled logged-out.** Claude evidences the content
  mix from the brand's mirrors (same clips on TikTok/YouTube) and the client's
  Professional Dashboard pulls; or connect the Chrome extension for a
  logged-in view.
- Private accounts need the client to accept a follow or send screen
  recordings.
- Instagram exposes ~12 post permalinks logged-out; thumbnail↔post mapping is
  sometimes approximate (reports say so when it is).

## 5. The one hard rule

Every recommendation must make content **genuinely compliant** with the
platform's written policy. We never advise evasion — algospeak, misspellings
("gambaaling"), hidden funnels, "DM me" workarounds. Evasion converts a reach
problem into an account-loss problem, and platforms treat it as proof of
knowing violation. If a client's core format can't be made compliant (selling
peptides on IG, casino referral codes, hate-speech "jokes"), the report says so
plainly and prescribes the compliant pivot or the correct off-platform home.

## 6. Repo map

```
.claude/skills/audit/     /audit workflow (phases, evidence rules, components)
.claude/skills/onboard/   /onboard workflow (discovery, 5-platform collection)
rubric/00–04              Instagram (enforcement model, suggestive, regulated
                          goods, harassment-pattern, general reach-killers)
rubric/05                 YouTube + TikTok
rubric/06                 Snapchat (+ Twitch/Kick/X as funnel context only)
rubric/07                 Snap Star review readiness grading
rubric/08                 Facebook content monetization
templates/                report-template.md (single) · onboarding-template.md
brand/brand.css           ALL visual tokens (colors/type from altrmgmt.com)
brand/logo-mark.png       the real ALTR mark (from the site's headerLogo)
scripts/render_pdf.py     markdown → branded PDF (pandoc + headless Chrome)
scripts/igshot.py         clean screenshots (kills IG's signup modal via CDP)
reports/                  finished audits + assets/<client>/ evidence images
```

## 7. Maintenance

- **Rubrics are dated.** Policies shift several times a year; each rubric notes
  when it was grounded. If enforcement behavior seems off, ask Claude to
  re-verify that rubric against current published policy and update the file.
- **Brand changes:** edit tokens at the top of `brand/brand.css`; swap
  `brand/logo-mark.png`. Rules that must not regress: no gray/thin text —
  cream or sage only; ~20px body; nothing splits across pages.
- **Scope changes** (adding/removing platforms): update both SKILL.md files,
  both templates, the rubric headers, README, and this file.
- Re-render any report after edits: `python3 scripts/render_pdf.py reports/<file>.md`

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| "websocket" / "PIL" module errors | `.venv` missing — see Setup step 4 |
| Chrome extension won't connect | Don't fight it; everything falls back to headless automatically. (If you want it: chrome://extensions, remove duplicate Claude extensions, correct profile, same claude.ai account.) |
| A platform page times out headless | Claude retries with per-command timeouts; TikTok/Snap web are flaky — screenshots via `scripts/igshot.py` usually succeed where DOM dumps hang |
| PDF looks wrong | Check the markdown renders the components correctly (blank lines inside `<div class="txt">` blocks are required); re-render |
| Cover title wrong | It's pulled from the report's own `# H1` ("Title — Subject") |

## 9. Report history (examples to learn the voice from)

- `tsteezylive-2026-09-17` — gambling funnel, F-grade, the full visual system
- `thegabedias-2026-09-12` — hate-speech strikes, delete-only findings
- `farahjamay-2026-10-20` + `farah-jamay-onboarding-2026-10-20` — clean-conduct
  framing drift; the onboarding/grade-matrix format
- `trin_dacomic-2026-09-29` — format A/B story; cross-platform section
- `collegesportsonly-fb-monetization-2026-10-21` — Facebook monetization lens
