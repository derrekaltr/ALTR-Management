#!/bin/zsh
# Render each model-week's pack.html to a branded PDF the team can hand to the creator.
# PDFs land in content/<model>/<week>/ (committed) and are copied into dist/ on the next build.
set -e
cd "$(dirname "$0")/.."

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Google Chrome not found at $CHROME"; exit 1; }

node site/build.js

made=0
for pack in dist/*/*/pack.html; do
  [ -e "$pack" ] || continue
  model=$(basename "$(dirname "$(dirname "$pack")")")
  week=$(basename "$(dirname "$pack")")
  out="content/$model/$week/ALTR-$model-$week.pdf"
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --run-all-compositor-stages-before-draw --virtual-time-budget=10000 \
    --print-to-pdf="$out" "file://$PWD/$pack" 2>/dev/null
  echo "→ $out"
  made=$((made + 1))
done

# rebuild so the PDFs are copied into dist/ and linked on the week pages
node site/build.js
echo "Rendered $made PDF(s). Deploy with: vercel deploy --prod --yes"
