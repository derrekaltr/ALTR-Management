# ALTR Management HQ

This repo is the single organized home for ALTR Management (talent/creator management agency).
Derrek also runs two sister companies — ALTR Services (IG recovery/verification) and ALTR Media
Group (phone farm, meme pages, music promo). Their projects are indexed in `ECOSYSTEM.md` and do
NOT live in this repo.

## Layout

Six section folders, each containing one subfolder per project and a `TASKS.md` board:

- `01-clients-onboarding/` — intake forms, client checkups, client-specific decks
- `02-outreach-sales/` — outreach playbooks, prospecting, swapd, growth research
- `03-content-ops/` — content scripts, reels methods, The Weekly Edit, content automation
- `04-reporting-analytics/` — client chat reports, creator audits, case boards, investigations
- `05-tools-automation/` — scrapers, contact enrichment, social monitors
- `06-ops-admin/` — internal admin, platform audits, company infrastructure

`MIGRATION.md` records where every pre-consolidation Conductor project ended up.

## Conventions

- **Work in the section folder that matches the task.** Workspaces are typically named after a
  section (clients-onboarding, content-ops, …); stay inside that section's folder so parallel
  workspaces never conflict on merge.
- **Task tracking**: read the section's `TASKS.md` before starting; move items between
  `## Now / ## Next / ## Done` as you work; add new tasks there. Keep `## Done` entries dated.
- **New project** = new subfolder in the right section with its own README.
- **Merge to main** when work is worth keeping (`git push origin HEAD:main` after a clean
  fast-forward, or open a PR for bigger changes) so other workspaces inherit it.
- **Secrets stay out of git**: `.env*`, Telegram `.session`, `telegram.ini`, and local DBs
  (`.pgdata/`, `.data/`) are gitignored on purpose; they exist on disk only. Never force-add them.
- Some old projects' playbooks were chat-only and have no files — check the "rebuild as doc"
  tasks in section boards before assuming something is missing.
