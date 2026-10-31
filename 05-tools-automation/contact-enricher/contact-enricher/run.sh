#!/bin/bash
# Full pipeline: extract new/changed conversations, analyze them, write contacts.
# Default is a dry run. Pass --apply to create contacts.
set -euo pipefail

cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"

APPLY=""
if [[ "${1:-}" == "--apply" ]]; then
  APPLY="--apply --yes"
fi

echo "=== $(date '+%Y-%m-%d %H:%M:%S') starting run ==="

echo "--- extract ---"
python3 extract.py

echo "--- analyze ---"
python3 analyze.py --parallel 4

echo "--- contacts ---"
# shellcheck disable=SC2086
python3 write_contacts.py $APPLY

echo "=== $(date '+%Y-%m-%d %H:%M:%S') run complete ==="
