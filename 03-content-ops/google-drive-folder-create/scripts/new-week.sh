#!/bin/zsh
# Scaffold this week's folders for every model: content/<model>/<monday>/<level>/
set -e
cd "$(dirname "$0")/.."

# Monday of the current week (macOS date)
dow=$(date +%u)                       # 1 = Monday
monday=$(date -v-$((dow - 1))d +%Y-%m-%d)

for model in content/*/; do
  for level in level-1-implied level-2-topless level-3-full-nude; do
    mkdir -p "${model}${monday}/${level}"
  done
  [ -f "${model}${monday}/drive-folder.txt" ] || echo "TBD" > "${model}${monday}/drive-folder.txt"
done
echo "Created week folders for $(ls -d content/*/ | wc -l | tr -d ' ') models → week of ${monday}"
echo "Drop GPTease outputs in as idea-1.md / idea-2.md / idea-3.md, then run: node site/build.js"
echo "Then: create the week's Google Drive folders (model → week → one per idea),"
echo "paste the week root URL into drive-folder.txt and each idea URL into its"
echo "idea file's '**Drive folder:**' line. TBD = link hidden on site/PDF."
