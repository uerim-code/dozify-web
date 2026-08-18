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
#
# Only the generated paths count. The first version diffed the whole tree, so
# an uncommitted note in docs/ was reported as "the generated tree is stale",
# which is both wrong and the kind of false alarm that gets a check ignored.
if ! git diff HEAD --quiet -- en tr sitemap.xml .vercelignore; then
  echo
  echo "KALDI — üretilen ağaç commit'lenmiş hâlden farklı:"
  git diff HEAD --stat -- en tr sitemap.xml .vercelignore
  echo
  echo "Kaynağı düzenleyip yeniden üret, sonra commit'le. en/ ve tr/ altındaki"
  echo "dosyaları elle düzenleme — bir sonraki üretim onları siler."
  exit 1
fi

python3 tools/seo-gate.py "$@"
