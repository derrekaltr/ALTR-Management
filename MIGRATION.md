# Migration Manifest

Every old Conductor project, its classification, and migration status.
Status: ⬜ pending · ✅ migrated (copied + verified + committed) · 🗑 source deleted · 🔗 indexed in ECOSYSTEM.md · ⏭ skipped (no artifacts) · ❓ awaiting owner decision

**Global copy exclusions** (regenerable/junk, never migrated): `.git`, `.context`, `.claude`, `.venv`, `venv`, `node_modules`, `__pycache__`, `.DS_Store`, `dist`, `.vercel`, `skills-lock.json`, Conductor starter boilerplate.

## ALTR Management → migrate into this repo, then delete source

| Old project | Source | Destination | Status | Notes |
|---|---|---|---|---|
| altr-master-intake | ws `altr-master-intake/roseau` | `01-clients-onboarding/master-intake-forms/` | ⬜ | |
| new-model-checkups | ws `new-model-checkups/phoenix` | `01-clients-onboarding/altr-checkin/` | ⬜ | |
| model-folder-buildouts | repo branch `client-call-folder-structure` | `01-clients-onboarding/client-folder-structure/` | ⬜ | |
| isa-becomes-the-goat | repo branch `download-analyze-of-courses` | `01-clients-onboarding/isa-course-analysis/` | ⬜ | |
| mikayla | repo branch `bundle-pricing-15pct-branding-deck` | `01-clients-onboarding/mikayla-pricing-deck/` | ⬜ | |
| model-outreach-sop | repo branch `altr-ig-outreach-sales-playbook` | `02-outreach-sales/ig-outreach-sales-playbook/` | ⬜ | |
| model-outreach-warm-leads | repo branch `monday-leads-imessage-outreach` | `02-outreach-sales/monday-warm-leads-imessage/` | ⬜ | |
| modelsniche | repo branches `onlyfans-creator-instagram-niches`, `prospect-run` | `02-outreach-sales/modelsniche/<branch>/` | ⬜ | two branches exported |
| operation-swapd | ws `operation-swapd/stuttgart` | `02-outreach-sales/swapd-listing-outreach/` | ⬜ | |
| ofm-cook | ws `ofm-cook/newport-beach` | `02-outreach-sales/agency-growth-research/` | ⬜ | |
| txt | ws `txt/tokyo` | `02-outreach-sales/txtcom-messaging/` | ⬜ | |
| creator-mutuals-heat-map-crm | ws `Starter project/chennai` | `02-outreach-sales/creator-mutuals-crm/` | ⬜ | |
| content-scripts (OF script GPT) | ws `content-scripts/rome` | `03-content-ops/onlyfans-content-script-gpt/` | ⬜ | excl. `.vercel`, `dist`, `.env.local` kept? NO — env excluded |
| content-scripts (gdrive folders) | ws `content-scripts/tyler` | `03-content-ops/google-drive-folder-create/` | ⬜ | |
| close-friends-schedule | ws `close-friends-schedule/lima` | `03-content-ops/weekly-edit-story-planner/` | ⬜ | deployed app — node_modules excluded |
| trial-reels-cook | ws `trial-reels-cook/tehran` | `03-content-ops/trial-reels-pipeline/` | ⬜ | |
| implied-script | ws `implied-script/sun-valley` | `03-content-ops/implied-script-outlines/` | ⬜ | |
| content-drop-automation | ws `Starter project/delhi` | `03-content-ops/content-drop-automation/` | ⬜ | |
| altr-reporting | repo branch `derrekaltr/altr-reports-gpt-overview` | `04-reporting-analytics/altr-reports-gpt-overview/` | ⬜ | |
| clientgroupchatreports | ws `clientgroupchatreports/rio-de-janeiro` | `04-reporting-analytics/weekly-client-chat-reports/` | ⬜ | |
| telegram-groupchat-analysis | ws `telegram-groupchat-analysis/las-vegas` | `04-reporting-analytics/invoice-chat-audit/` | ⬜ | |
| lead-check-up | ws `lead-check-up/dakar` | `04-reporting-analytics/lead-checkup-case-board/` | ⬜ | excl. scratch DB snapshots (chat.db 2.1G, wa.sqlite, *.jsonl) — regenerable from live Messages/WhatsApp |
| mayson-referral-audit | repo branch `telegram-referral-invoice-totals` | `04-reporting-analytics/mayson-referral-audit/` | ⬜ | |
| analyze-client-groupchat-data | ws `Starter project/nairobi` | `04-reporting-analytics/client-chat-analysis/` | ⬜ | |
| creatorsteroids (reelcritic) | ws `creatorsteroids/valencia` | `04-reporting-analytics/reelcritic/` | ⬜ | |
| sauce-the-brown-carpet-riders | ws `sauce-the-brown-carpet-riders/chiang-mai` | `04-reporting-analytics/client-case-cards/` | ⬜ | |
| research-alberto-riehl-scams | ws `Starter project/geneva` | `04-reporting-analytics/alberto-riehl-research/` | ⬜ | |
| client-ig-scraper | ws `client-ig-scraper/boise` | `05-tools-automation/ig-follower-lead-scraper/` | ⬜ | excl. `data/*/profiles_raw.jsonl` + logs (raw Apify dumps); final lead CSVs kept |
| conctact-list-creator (enricher) | ws `conctact-list-creator/santo-domingo` | `05-tools-automation/contact-enricher/` | ⬜ | |
| model-ig-update | ws `model-ig-update/jakarta` | `05-tools-automation/model-social-monitor/` | ⬜ | |
| platform-review-and-tester | ws `platform-review-and-tester/bangui` | `06-ops-admin/wisfma-ux-audit/` | ⬜ | |

## ❓ Awaiting owner decision (not touched until answered)

| Project | Content | Question |
|---|---|---|
| ig-audit | ALTR Creator Audit system (IG compliance PDFs for creator clients) | Management (client reports) or Services (IG compliance/recovery)? |
| pre-snapstar-account-review | Snapchat gold-star verification-readiness audit | Management or Services? |
| conctact-list-creator/brussels | Vivek update sheet + pending IG-unban case tracking | Management reporting or Services (unbans)? |
| email-clean-up | gmail-triage: auto-labels 3 Gmail accounts, feeds Jarvis dashboard | Company ops or personal infra (leave)? |
| alex-camus-investigation | Finance investigation reports (Emanay, personal account defense) | ALTR business or personal? |
| ig-trending-sound-reports (+ `Starter/bordeaux`) | Reels trending-audio analytics reports | Management content ops or Media Group (music promo)? |
| statly | Reverse-engineering of Statly app | Management tooling research or skip? |
| farah-website | Shopify theme build handoff | Client work or personal? |
| okularity | Copyright response | Which company / personal? |
| find-password / finding-passwords / secure-passwords | Login/credential extraction utilities | Left alone by default (sensitive). Migrate to 06-ops-admin or leave? |

## 🔗 Sister companies — indexed in ECOSYSTEM.md, left in place

ALTR Services: services-intake, ban-reason-lookup, smm-panel-pricing, ig-rep-submissions (+daegu), legacy-verification, mr-jones-online-cleanup, don-resin-makes-it-into-heaven.
ALTR Media Group: phone-farm-operation, beatport, beatporttt, twitterreels, twitterupdated, tweet-reels-extraction, social-media-influencer-audio-seeding, music-crowdfunding-chart-engine.

## ⏭ Personal / other ventures / no artifacts — untouched

| Project | Reason |
|---|---|
| my-gf-is-bitching-about-burning-man | personal |
| derrek-jarvis-buildout | personal (Jarvis hub) |
| gosip | separate venture (Go Sip coffee membership) |
| karen-bot | separate venture (consumer app plan) |
| peptide-funnel | separate venture (peptide brand) |
| campus-phone-repair | separate/old business |
| monitors | personal (triple-monitor setup) |
| conductor-playground | personal (W-9 form) |
| new-trick | personal (uber lookup) |
| Starter: stolen-car-type-lookup (+medan), odyssey-g9, thumb-drive, valentina-salary-inquiry, paperclipai-onboard, altr-google-drive-organize, da-nang + city tabs | no unique artifacts (work was chat-only) |
| kartik-fame, new-repo, new-repo-v1, ofm-platform-research-agent | empty (1 commit, no content) |
