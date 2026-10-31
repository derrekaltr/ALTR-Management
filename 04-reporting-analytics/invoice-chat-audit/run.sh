#!/bin/sh
# Run the full invoicing-audit pipeline against a Telegram Desktop HTML export.
# Usage: ./run.sh "/path/to/Telegram Export"
set -e
EXPORT_DIR="${1:?usage: ./run.sh <export_dir>}"
cd "$(dirname "$0")"
python3 scripts/parse_export.py "$EXPORT_DIR"
python3 scripts/extract_invoicing.py
python3 scripts/build_cycles.py
python3 scripts/verify.py "$EXPORT_DIR"
echo
echo "Done. Analysis inputs: data/invoicing/*.md + data/cycles/cycles.csv"
