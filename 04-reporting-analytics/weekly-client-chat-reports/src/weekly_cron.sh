#!/bin/bash
# Runs the full weekly pipeline headlessly. Invoked by launchd every Friday.
#   1. /weekly-report      — client dashboard + employee reports, published to the team site
#   2. /cs-gap-analysis    — internal customer-success gap analysis (NOT published)
# Logs to data/cron.log.
set -uo pipefail
REPO="/Users/locklyjailbreak/conductor/workspaces/clientgroupchatreports/rio-de-janeiro"
export PATH="/Users/locklyjailbreak/.local/bin:/usr/local/bin:/usr/bin:/bin"
cd "$REPO"
{
  echo "=== weekly report run: $(date) ==="
  claude -p "/weekly-report" --permission-mode acceptEdits 2>&1
  echo "=== done: $(date) (exit $?) ==="
  echo "=== cs gap analysis run: $(date) ==="
  claude -p "/cs-gap-analysis" --permission-mode acceptEdits 2>&1
  echo "=== done: $(date) (exit $?) ==="
} >> data/cron.log
