#!/bin/bash
# Install the daily launchd job (runs run.sh --apply at 4:30am).
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_NAME="com.altr.contact-enricher.plist"
TARGET="$HOME/Library/LaunchAgents/$PLIST_NAME"

mkdir -p "$HOME/Library/LaunchAgents" "$BASE_DIR/data/logs"
sed "s|__BASE_DIR__|$BASE_DIR|g" "$BASE_DIR/$PLIST_NAME" > "$TARGET"

launchctl unload "$TARGET" 2>/dev/null || true
launchctl load "$TARGET"

echo "installed: $TARGET"
echo "run now with:  launchctl start com.altr.contact-enricher"
echo "logs:          $BASE_DIR/data/logs/launchd.out.log"
echo "uninstall:     launchctl unload $TARGET && rm $TARGET"
