#!/bin/bash
# Publish weekly reports to a shareable Netlify link.
# Usage: ./src/publish.sh 2026-08-08
#
# One-time setup: `npx -y netlify-cli login` (browser approval), then the
# first run creates the site. NOTE: the link is PUBLIC — anyone with the URL
# can view the report. Pages are marked noindex and the site name is random.
set -euo pipefail
WEEK="${1:?usage: ./src/publish.sh <week, e.g. 2026-08-08>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$REPO_ROOT/reports"
SITE_FILE="$REPO_ROOT/config/netlify-site.txt"   # gitignored via config? stores site id
[ -f "$REPORT_DIR/$WEEK/index.html" ] || { echo "no report for $WEEK — run render.py first"; exit 1; }

# Keep robots off the whole site as well as per-page noindex
printf 'User-agent: *\nDisallow: /\n' > "$REPORT_DIR/robots.txt"

if [ ! -f "$SITE_FILE" ]; then
  SUFFIX="$(python3 -c 'import secrets; print(secrets.token_hex(5))')"
  npx -y netlify-cli sites:create --name "altr-reports-$SUFFIX" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' > "$SITE_FILE"
fi
SITE_ID="$(cat "$SITE_FILE")"

npx -y netlify-cli deploy --dir "$REPORT_DIR" --site "$SITE_ID" --prod --json \
  | python3 -c "
import json, sys
url = json.load(sys.stdin)['url']
print('Share this link with the team:')
print(f'  {url}/$WEEK/')
print(f'All weeks: {url}')
"
