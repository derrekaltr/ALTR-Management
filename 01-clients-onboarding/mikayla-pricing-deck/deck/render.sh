#!/bin/zsh
# Render a .pptx to PDF via Keynote, then to per-slide JPGs for visual QA.
# Run with sandbox disabled (needs Apple Events to Keynote).
set -e
setopt null_glob
DIR="$(cd "$(dirname "$0")" && pwd)"
PPTX="${1:-$DIR/ALTR-Media-Bundles-2026.pptx}"
PDF="$DIR/render/deck.pdf"
mkdir -p "$DIR/render"
rm -f "$DIR/render"/slide-*.jpg "$PDF"

osascript -e 'tell application "Keynote" to close every document saving no' >/dev/null 2>&1 || true
open -a Keynote "$PPTX"
sleep 8
osascript <<EOF
tell application "Keynote"
  set theDoc to front document
  export theDoc to POSIX file "$PDF" as PDF
  close theDoc saving no
end tell
EOF

pdftoppm -jpeg -r 110 "$PDF" "$DIR/render/slide"
ls "$DIR/render"
