#!/usr/bin/env python3
"""Structural SEO checks that can fail a release.

Everything here is something that was actually wrong on this site at some
point, or that would silently break if a page were added without its
metadata. Nothing here is a style opinion.

  python3 tools/check-seo.py           # local files only, fast
  python3 tools/check-seo.py --live    # also fetch every sitemap URL

Exit code 1 on any finding.
"""

from __future__ import annotations

import glob
import html as html_mod
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Only the generated trees are served and indexable. The dual-language files at
# the repo root are the sources the builder reads; .vercelignore keeps them off
# the site, so holding them to metadata rules would report findings nobody can
# act on and nobody should.
TREES = ("en", "tr")

# Google truncates well before these; past them the tail is wasted.
TITLE_MAX = 65
DESC_MIN, DESC_MAX = 70, 165


def pages() -> list[str]:
    out = []
    for tree in TREES:
        for p in glob.glob(os.path.join(ROOT, tree, "**", "*.html"), recursive=True):
            out.append(os.path.relpath(p, ROOT))
    return sorted(out)


def field(src: str, pattern: str) -> str | None:
    m = re.search(pattern, src, re.I | re.S)
    return m.group(1).strip() if m else None


def visible_text(src: str) -> str:
    """What a reader sees — scripts, styles and markup removed."""
    src = re.sub(r"<(script|style)\b.*?</\1>", " ", src, flags=re.S | re.I)
    src = re.sub(r"<[^>]+>", " ", src)
    return re.sub(r"\s+", " ", html_mod.unescape(src))


def main() -> int:
    findings: list[str] = []
    canonicals: dict[str, str] = {}
    titles: Counter[str] = Counter()
    descs: Counter[str] = Counter()

    for rel in pages():
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()

        title = field(src, r"<title>(.*?)</title>")
        desc = field(src, r'<meta\s+name="description"\s+content="(.*?)"')
        canon = field(src, r'<link\s+rel="canonical"\s+href="(.*?)"')

        if not title:
            findings.append(f"{rel}: <title> yok")
        else:
            titles[title] += 1
            if len(title) > TITLE_MAX:
                findings.append(f"{rel}: title {len(title)} karakter (üst sınır {TITLE_MAX})")

        if not desc:
            findings.append(f"{rel}: meta description yok")
        else:
            descs[desc] += 1
            if not (DESC_MIN <= len(desc) <= DESC_MAX):
                findings.append(f"{rel}: description {len(desc)} karakter (hedef {DESC_MIN}–{DESC_MAX})")

        if not canon:
            findings.append(f"{rel}: canonical yok")
        else:
            if canon in canonicals:
                findings.append(f"{rel}: canonical çakışması — {canon} zaten {canonicals[canon]}")
            canonicals[canon] = rel
            if not canon.startswith("https://dozify.app/"):
                findings.append(f"{rel}: canonical mutlak https://dozify.app/ ile başlamıyor: {canon}")
            if canon.endswith(".html"):
                findings.append(f"{rel}: canonical .html ile bitiyor; uzantısız biçim kullanılıyor")

        # One H1 per page. This was two per page while both languages shared a
        # document; the split is what made the check meaningful, so it is on.
        h1s = re.findall(r"<h1\b", src)
        if len(h1s) != 1:
            findings.append(f"{rel}: {len(h1s)} adet H1 (tam olarak 1 olmalı)")

        lang = rel.split(os.sep)[0]
        declared = field(src, r'<html\s+lang="(.*?)"')
        if declared != lang:
            findings.append(f"{rel}: <html lang=\"{declared}\"> ama sayfa /{lang}/ altında")

        # The share card. Half these tags were missing before Faz 2, so a link
        # to the page previewed as a bare URL.
        required = {
            "og:title": r'property="og:title"',
            "og:description": r'property="og:description"',
            "og:url": r'property="og:url"',
            "og:image": r'property="og:image"',
            "og:locale": r'property="og:locale"',
            "og:type": r'property="og:type"',
            "twitter:card": r'name="twitter:card"',
            "twitter:image": r'name="twitter:image"',
            "theme-color": r'name="theme-color"',
            "apple-touch-icon": r'rel="apple-touch-icon"',
        }
        for label, pattern in required.items():
            if not re.search(pattern, src):
                findings.append(f"{rel}: {label} yok")

        og_url = field(src, r'<meta\s+property="og:url"\s+content="(.*?)"')
        if canon and og_url and og_url != canon:
            findings.append(f"{rel}: og:url ({og_url}) canonical ({canon}) ile aynı değil")
        og_image = field(src, r'<meta\s+property="og:image"\s+content="(.*?)"')
        if og_image and not og_image.startswith("https://"):
            findings.append(f"{rel}: og:image mutlak URL değil: {og_image}")

        # hreflang has to point both ways and name this page as one of the
        # alternates, or Google treats the pair as unrelated duplicates.
        alts = dict(re.findall(r'<link\s+rel="alternate"\s+hreflang="(.*?)"\s+href="(.*?)"', src))
        for code in ("en", "tr", "x-default"):
            if code not in alts:
                findings.append(f"{rel}: hreflang {code} yok")
        if canon and canon not in alts.values():
            findings.append(f"{rel}: kendi canonical'ı hreflang kümesinde yok")

        # Structured data: it must parse, and it must not describe content the
        # visitor cannot see. The FAQ schema used to list ten English questions
        # on the Turkish page.
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
        if not blocks:
            findings.append(f"{rel}: JSON-LD yok")
        shown = visible_text(src)
        for raw in blocks:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                findings.append(f"{rel}: JSON-LD ayrıştırılamadı ({e})")
                continue
            for node in data.get("@graph", [data]):
                types = node.get("@type", "")
                types = types if isinstance(types, list) else [types]
                if "FAQPage" not in types:
                    continue
                for q in node.get("mainEntity", []):
                    name = re.sub(r"\s+", " ", q.get("name", ""))
                    if name and name not in shown:
                        findings.append(f"{rel}: FAQ şeması sayfada olmayan soruyu içeriyor — “{name[:50]}”")

    for t, n in titles.items():
        if n > 1:
            findings.append(f"yinelenen title ({n} sayfa): {t[:60]}")
    for d, n in descs.items():
        if n > 1:
            findings.append(f"yinelenen description ({n} sayfa): {d[:60]}")

    # Sitemap must be exactly the set of canonicals — no more, no less.
    sm_path = os.path.join(ROOT, "sitemap.xml")
    sm = open(sm_path, encoding="utf-8").read()
    locs = re.findall(r"<loc>(.*?)</loc>", sm)
    dupes = [u for u, n in Counter(locs).items() if n > 1]
    for u in dupes:
        findings.append(f"sitemap: mükerrer URL {u}")
    missing = set(canonicals) - set(locs)
    extra = set(locs) - set(canonicals)
    for u in sorted(missing):
        findings.append(f"sitemap: eksik {u} ({canonicals[u]})")
    for u in sorted(extra):
        findings.append(f"sitemap: karşılığı olmayan URL {u}")
    if re.search(r"<changefreq>|<priority>", sm):
        findings.append("sitemap: uydurma changefreq/priority değerleri var")

    if "--live" in sys.argv:
        import urllib.request
        import urllib.error
        print(f"canlı kontrol: {len(locs)} URL")
        for u in locs:
            req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "dozify-seo-check"})
            try:
                code = urllib.request.urlopen(req, timeout=15).status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception as e:  # noqa: BLE001 — network shape varies
                findings.append(f"sitemap: {u} istek başarısız ({e})")
                continue
            if code != 200:
                findings.append(f"sitemap: {u} HTTP {code}")

    print(f"{len(pages())} sayfa, {len(locs)} sitemap kaydı")
    if not findings:
        print("temiz")
        return 0
    print(f"\n{len(findings)} bulgu:\n")
    for f in findings:
        print("  " + f)
    return 1


if __name__ == "__main__":
    sys.exit(main())
