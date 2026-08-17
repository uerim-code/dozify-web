#!/bin/sh
# Everything that has to be true before this site is published.
#
#   ./check.sh          # local files only
#   ./check.sh --live   # also fetch every sitemap URL and every legal link
#
# Run it from the repo root. Exit 0 means publishable.
set -e

echo "→ sayfalar kaynaklardan yeniden üretiliyor"
python3 tools/build-languages.py > /dev/null

# A generated tree that differs from what is committed means someone edited a
# page under en/ or tr/ by hand, or edited a source and did not rebuild. Either
# way the thing about to be published is not the thing that was reviewed.
if ! git diff --quiet; then
  echo
  echo "KALDI — üretilen ağaç commit'lenmiş hâlden farklı:"
  git diff --stat
  echo
  echo "Kaynağı düzenleyip yeniden üret, sonra commit'le. en/ ve tr/ altındaki"
  echo "dosyaları elle düzenleme — bir sonraki üretim onları siler."
  exit 1
fi

python3 tools/seo-gate.py "$@"
