#!/usr/bin/env python3
"""Print what each shipped page actually claims about itself.

Read off the generated files, not the plan — the point is to see what is on
disk about to be served. Two tables: the search-result appearance of every URL,
and the schema types each one declares.

  python3 tools/seo-report.py > docs/seo-metadata.md
"""

from __future__ import annotations

import glob
import html as html_mod
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metadata import INTENT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dozify.app"

# The English slug is the identity of a page; the Turkish one is a translation
# of the URL, not of the page.
EN_FOR_TR = {
    "": "", "glp1-igne-takibi": "glp1-shot-tracker",
    "enjeksiyon-bolgesi-takibi": "injection-site-tracker",
    "glp1-kilo-takibi": "glp1-weight-tracker",
    "yan-etki-gunlugu": "glp1-side-effect-journal",
    "flakon-takibi": "glp1-vial-tracker",
    "gizli-glp1-takibi": "private-glp1-tracker",
    "doktor-raporu": "glp1-appointment-report",
    "baska-uygulamadan-gecis": "switch-glp1-tracker-app",
    "neden-dozify": "why", "destek": "support", "gizlilik": "privacy",
    "kullanim-kosullari": "terms", "kvkk": "kvkk", "makaleler": "articles",
    "makaleler/glp1-nedir": "articles/what-is-glp1",
    "makaleler/glp1-nasil-yapilir": "articles/how-to-inject-glp1",
    "makaleler/glp1-enjeksiyon-bolgeleri": "articles/glp1-injection-sites",
    "makaleler/glp1-yan-etkileri": "articles/glp1-side-effects",
    "makaleler/glp1-bantlari": "articles/glp1-patches",
}


def field(src: str, pattern: str) -> str:
    m = re.search(pattern, src, re.I | re.S)
    return html_mod.unescape(m.group(1).strip()) if m else ""


def rows():
    for lang in ("en", "tr"):
        for path in sorted(glob.glob(os.path.join(ROOT, lang, "**", "*.html"), recursive=True)):
            rel = os.path.relpath(path, ROOT)
            slug = rel[len(lang) + 1:].removesuffix(".html").removesuffix("index").strip("/")
            en_slug = slug if lang == "en" else EN_FOR_TR[slug]
            yield lang, en_slug, rel, open(path, encoding="utf-8").read()


def main() -> int:
    print("# Faz 2 — yayınlanan sayfaların arama görünümü\n")
    print("`tools/seo-report.py` üretti; kaynağı diskteki sayfaların kendisi.\n")
    print("| URL | Dil | Arama niyeti | Ana sorgu | Title | Uzunluk | Description | Uzunluk |")
    print("|---|---|---|---|---|---|---|---|")
    schema_rows = []
    for lang, en_slug, rel, src in rows():
        title = field(src, r"<title>(.*?)</title>")
        desc = field(src, r'<meta\s+name="description"\s+content="(.*?)"')
        canon = field(src, r'<link\s+rel="canonical"\s+href="(.*?)"')
        intent, query = INTENT[en_slug][lang]
        url = canon.replace(SITE, "") or "/"
        print(f"| `{url}` | {lang} | {intent} | {query} | {title} | {len(title)} "
              f"| {desc} | {len(desc)} |")

        types = []
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
            for node in json.loads(raw).get("@graph", []):
                t = node.get("@type")
                types.extend(t if isinstance(t, list) else [t])
        schema_rows.append((url, lang, types))

    print("\n# Faz 2 — URL başına structured data\n")
    print("| URL | Dil | Schema türleri |")
    print("|---|---|---|")
    for url, lang, types in schema_rows:
        print(f"| `{url}` | {lang} | {', '.join(types)} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
