# Migration Manifest

Every old Conductor project, its classification, and migration status.
Status: ✅ migrated (copied + checksum-verified + committed) · 🗑 source deleted · 🔗 indexed in ECOSYSTEM.md · ⏭ skipped (no artifacts) · ❓ awaiting owner decision

**Global copy exclusions** (regenerable/junk, never migrated): `.git`, `.context`, `.claude`, `.venv`, `venv`, `node_modules`, `__pycache__`, `.DS_Store`, `dist`, `.next`, `.vercel`, `skills-lock.json`, Conductor starter boilerplate.
**On disk but not in git** (gitignored, preserved in the destination folder only): `trial-reels-pipeline/.pgdata/` (local dev Postgres; production data is in Neon), `weekly-edit-story-planner/.data/` (local PGlite), `weekly-client-chat-reports/config/telegram.ini` and `model-social-monitor/config/*.session` (credentials), any `.env*` files.
**Security note:** an Apify API token quoted inside lead-checkup iMessage transcripts was redacted before pushing (GitHub push protection flagged it). The token itself was exposed in those texts — consider rotating it at apify.com.

## ALTR Management → migrated into this repo (source delete pending owner OK)

| Old project | Source | Destination | Status | Notes |
|---|---|---|---|---|
| altr-master-intake | ws `altr-master-intake` | `01-clients-onboarding/master-intake-forms/` | ✅ | |
| new-model-checkups | ws `new-model-checkups` | `01-clients-onboarding/altr-checkin/` | ✅ | |
| mikayla | repo `mikayla` @13c7a21a | `01-clients-onboarding/mikayla-pricing-deck/` | ✅ | |
| modelsniche | repo `modelsniche` (2 branches) | `02-outreach-sales/modelsniche/<branch>/` | ✅ | |
| operation-swapd | ws `operation-swapd` | `02-outreach-sales/swapd-listing-outreach/` | ✅ | |
| ofm-cook | ws `ofm-cook` | `02-outreach-sales/agency-growth-research/` | ✅ | |
| txt | ws `txt` | `02-outreach-sales/txtcom-messaging/` | ✅ | |
| creator-mutuals-heat-map-crm | ws `Starter project/chennai` | `02-outreach-sales/creator-mutuals-crm/` | ✅ | |
| content-scripts (OF script GPT) | ws `content-scripts/rome` | `03-content-ops/onlyfans-content-script-gpt/` | ✅ | |
| content-scripts (gdrive folders) | ws `content-scripts/tyler` | `03-content-ops/google-drive-folder-create/` | ✅ | |
| close-friends-schedule | ws `close-friends-schedule` | `03-content-ops/weekly-edit-story-planner/` | ✅ | deployed app (The Weekly Edit) |
| trial-reels-cook | ws `trial-reels-cook` | `03-content-ops/trial-reels-pipeline/` | ✅ | `.pgdata` kept on disk only |
| implied-script | ws `implied-script` | `03-content-ops/implied-script-outlines/` | ✅ | |
| content-drop-automation | ws `Starter project/delhi` | `03-content-ops/content-drop-automation/` | ✅ | |
| clientgroupchatreports | ws `clientgroupchatreports` | `04-reporting-analytics/weekly-client-chat-reports/` | ✅ | |
| telegram-groupchat-analysis | ws `telegram-groupchat-analysis` | `04-reporting-analytics/invoice-chat-audit/` | ✅ | |
| lead-check-up | ws `lead-check-up` | `04-reporting-analytics/lead-checkup-case-board/` | ✅ | excl. scratch DB snapshots (chat.db 2.1G, wa.sqlite, *.jsonl) — re-copyable from live Messages/WhatsApp |
| analyze-client-groupchat-data | ws `Starter project/nairobi` | `04-reporting-analytics/client-chat-analysis/` | ✅ | |
| creatorsteroids (reelcritic) | ws `creatorsteroids` | `04-reporting-analytics/reelcritic/` | ✅ | |
| sauce-the-brown-carpet-riders | ws `sauce-the-brown-carpet-riders` | `04-reporting-analytics/client-case-cards/` | ✅ | |
| research-alberto-riehl-scams | ws `Starter project/geneva` | `04-reporting-analytics/alberto-riehl-research/` | ✅ | |
| client-ig-scraper | ws `client-ig-scraper` | `05-tools-automation/ig-follower-lead-scraper/` | ✅ | excl. raw Apify dumps (`profiles_raw`/`followers_raw` jsonl, logs); final lead CSVs kept |
| conctact-list-creator (enricher) | ws `conctact-list-creator/santo-domingo` | `05-tools-automation/contact-enricher/` | ✅ | |
| model-ig-update | ws `model-ig-update` | `05-tools-automation/model-social-monitor/` | ✅ | |
| platform-review-and-tester | ws `platform-review-and-tester` | `06-ops-admin/wisfma-ux-audit/` | ✅ | |
| ig-audit | ws `ig-audit` | `04-reporting-analytics/creator-audit-system/` | ✅ | includes snapstar rubric + 10 client audit PDFs |
| pre-snapstar-account-review | ws `pre-snapstar-account-review` | `04-reporting-analytics/creator-audit-system/snapstar/` | ✅ | capture tool + client outputs; rubric already lived in ig-audit |

## ❓ Resolved by owner 2026-10-31

| Project | Decision | Outcome |
|---|---|---|
| ig-audit | ALTR Management | ✅ migrated → `04-reporting-analytics/creator-audit-system/` |
| pre-snapstar-account-review | Owner thought it was a copy of ig-audit — partially true: the rubric was folded into ig-audit (`rubric/07-snapstar-review.md`), but the Python capture/report tool + client outputs were unique | ✅ migrated → `04-reporting-analytics/creator-audit-system/snapstar/` |
| conctact-list-creator (vivek sheet, ws `brussels`) | ALTR Services | 🔗 indexed, left in place (workspace kept; only the contact-enricher worktree is deleted) |
| email-clean-up | Personal | ⏭ left alone |
| alex-camus-investigation | Personal | ⏭ left alone |
| ig-trending-sound-reports (+ `Starter/bordeaux`) | ALTR Media Group | 🔗 indexed, left in place |
| statly | Old — delete | 🗑 repo deleted, nothing migrated |
| find-password / finding-passwords / secure-passwords | Old — delete | 🗑 repos deleted, nothing migrated |

## 🔗 Sister companies — indexed in ECOSYSTEM.md, left in place

ALTR Services: services-intake, smm-panel-pricing, ig-rep-submissions (+daegu), legacy-verification (6,805 files in repo), mr-jones-online-cleanup. (ban-reason-lookup and don-resin have no file artifacts — chat-only.)
ALTR Media Group: phone-farm-operation, beatporttt, twitterreels, tweet-reels-extraction. (beatport, twitterupdated, social-media-influencer-audio-seeding, music-crowdfunding-chart-engine have no file artifacts.)

## ⏭ No artifacts anywhere (work was chat-delivered; repo trees are empty)

model-outreach-sop, model-outreach-warm-leads, model-folder-buildouts, isa-becomes-the-goat, altr-reporting, mayson-referral-audit, ban-reason-lookup, farah-website, okularity, kartik-fame, new-repo, new-repo-v1, ofm-platform-research-agent, don-resin-makes-it-into-heaven, beatport (repo), twitterupdated, social-media-influencer-audio-seeding, music-crowdfunding-chart-engine — plus Starter tabs: altr-google-drive-organize, paperclipai-onboard, valentina-salary-inquiry, odyssey-g9, thumb-drive, da-nang and unnamed city tabs.
*The outputs of these sessions (playbooks, reports) live in the old Conductor chat transcripts, not in files. Rebuild them as docs in this repo when needed.*

## ⏭ Personal / other ventures — untouched

my-gf-is-bitching-about-burning-man, derrek-jarvis-buildout (Jarvis), gosip (Go Sip), karen-bot, peptide-funnel, campus-phone-repair, monitors, conductor-playground (W-9), new-trick, Starter: stolen-car-type-lookup (+medan).
