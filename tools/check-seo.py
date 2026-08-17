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
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ("chembiocalc",)

# Google truncates well before these; past them the tail is wasted.
TITLE_MAX = 65
DESC_MIN, DESC_MAX = 70, 165


def pages() -> list[str]:
    out = []
    for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(p, ROOT)
        if rel.split(os.sep)[0] in SKIP_DIRS:
            continue
        out.append(rel)
    return sorted(out)


def field(src: str, pattern: str) -> str | None:
    m = re.search(pattern, src, re.I | re.S)
    return m.group(1).strip() if m else None


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

        # Deliberately NOT asserting a single H1 yet: both languages live in one
        # document, so every page legitimately carries two until the /tr/ + /en/
        # split lands. Turn this on with that change, not before — a check that
        # is known-failing teaches people to ignore the report.
        if not re.search(r'property="og:title"', src):
            findings.append(f"{rel}: Open Graph başlığı yok")

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
