#!/bin/zsh
# Installs the ALTR check-in automation: copies the script to
# ~/Library/Application Support/altr-checkin and loads a LaunchAgent
# that runs it daily at 10:00 AM.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$HOME/Library/Application Support/altr-checkin"
PLIST="$HOME/Library/LaunchAgents/com.altr.checkin.plist"

mkdir -p "$APP_DIR" "$HOME/Library/LaunchAgents"
cp "$SRC_DIR/checkin.py" "$APP_DIR/checkin.py"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.altr.checkin</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Library/Developer/CommandLineTools/usr/bin/python3</string>
        <string>$APP_DIR/checkin.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$APP_DIR/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$APP_DIR/launchd.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

# First run creates the baseline (marks already-past-due clients as skipped).
/usr/bin/python3 "$APP_DIR/checkin.py"

echo "Installed. Agent status:"
launchctl list | grep com.altr.checkin || true
