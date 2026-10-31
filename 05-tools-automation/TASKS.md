# Tools & Automation — Tasks

## Now

## Next
- [ ] Verify the contact-enricher launchd job still runs after old workspaces are deleted (`contact-enricher/com.altr.contact-enricher.plist` may point at the old path)
- [ ] Same check for altr-checkin install (`01-clients-onboarding/altr-checkin/install.sh`) and model-social-monitor (`model-social-monitor/`) — re-point any scheduled jobs to this repo
- [ ] ig-follower-lead-scraper: raw Apify dumps were not migrated; re-scrape if a client list needs rebuilding

## Done
- [x] 2026-10-31 — Migrated lead scraper, contact enricher, model social monitor
