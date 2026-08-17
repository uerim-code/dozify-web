#!/usr/bin/env python3
"""One command that has to pass before the site is published.

Everything checked here has been wrong on this site at least once, and each
time it was invisible until someone looked at the live page: an ignore pattern
that hid every English page, a canonical pointing at a URL that redirected, a
description truncated to eight characters by a quotation mark, a script
rewriting <html lang> to the visitor's time zone.

  python3 tools/seo-gate.py           # local files, fast, no network
  python3 tools/seo-gate.py --live    # also fetch every sitemap and legal URL

Prints one row per finding — URL, check, expected, found, fix — and exits 1 if
there is any. Exit 0 means the tree on disk is publishable.
"""

from __future__ import annotations

import glob
import html as html_mod
import json
import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
TREES = ("en", "tr")
SITE = "https://dozify.app"

# In the app's own paywall and in App Store Connect. If one of these stops
# resolving, Apple's 3.1.2(c) rejection is the next thing that happens.
LEGAL_URLS = [
    f"{SITE}/privacy",
    f"{SITE}/terms",
    f"{SITE}/kvkk",
    f"{SITE}/support",
    f"{SITE}/privacy.html",  # the form recorded in App Store Connect
    "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/",
]

Finding = tuple[str, str, str, str, str]  # url, check, expected, found, fix


def pages() -> list[str]:
    out = []
    for tree in TREES:
        out += glob.glob(os.path.join(ROOT, tree, "**", "*.html"), recursive=True)
    return sorted(os.path.relpath(p, ROOT) for p in out)


def url_of(rel: str) -> str:
    path = rel.removesuffix(".html")
    return "/" + (path[: -len("/index")] if path.endswith("/index") else path)


def run_tool(name: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, os.path.join(TOOLS, name)],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def check_broken_links(findings: list[Finding]) -> None:
    """Every internal href has to land on a file that exists."""
    existing = {url_of(rel) for rel in pages()}
    for rel in pages():
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        for href in re.findall(r'href="(/[^"]*)"', src):
            target = href.split("#")[0].split("?")[0].rstrip("/")
            if not target or target.startswith("//"):
                continue
            if re.search(r"\.(css|js|png|webp|svg|xml|ico|txt)$", target):
                if not os.path.exists(os.path.join(ROOT, target.lstrip("/"))):
                    findings.append((url_of(rel), "kırık varlık bağlantısı",
                                     "dosya var", f"{target} yok",
                                     "yolu düzelt ya da dosyayı ekle"))
                continue
            if target not in existing:
                findings.append((url_of(rel), "kırık iç bağlantı",
                                 "üretilmiş bir sayfa", f"{target} yok",
                                 "PAGES'e ekle ya da bağlantıyı düzelt"))


def check_alt_text(findings: list[Finding]) -> None:
    for rel in pages():
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        for tag in re.findall(r"<img[^>]*>", src):
            if 'aria-hidden="true"' in tag:
                continue
            m = re.search(r'alt="([^"]*)"', tag)
            if not m:
                findings.append((url_of(rel), "alt metni yok", "açıklayıcı alt",
                                 tag[:60], "görselin ne gösterdiğini yaz"))
            elif not m.group(1).strip():
                findings.append((url_of(rel), "alt metni boş",
                                 "açıklayıcı alt veya aria-hidden", 'alt=""',
                                 "anlamlıysa yaz, dekoratifse aria-hidden ekle"))


def check_jsonld(findings: list[Finding]) -> None:
    for rel in pages():
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S)
        if not blocks:
            findings.append((url_of(rel), "JSON-LD yok", "en az bir blok", "yok",
                             "build-languages.py'yi çalıştır"))
        for raw in blocks:
            try:
                json.loads(raw)
            except json.JSONDecodeError as e:
                findings.append((url_of(rel), "geçersiz JSON-LD", "ayrıştırılabilir",
                                 str(e)[:50], "üreticideki kaçış hatasını düzelt"))


def check_live(findings: list[Finding]) -> None:
    import urllib.error
    import urllib.request

    def status(url: str) -> object:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "dozify-seo-gate"})
        try:
            return urllib.request.urlopen(req, timeout=20).status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception as e:  # noqa: BLE001 — network shape varies
            return type(e).__name__

    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    for url in re.findall(r"<loc>(.*?)</loc>", sm):
        code = status(url)
        if code != 200:
            findings.append((url, "sitemap URL canlı değil", "200", str(code),
                             "yayınla ya da sitemap'ten çıkar"))
    for url in LEGAL_URLS:
        code = status(url)
        if code != 200:
            findings.append((url, "hukuki bağlantı canlı değil", "200", str(code),
                             "SAYFAYI DÜZELTMEDEN MAĞAZAYA GÖNDERME"))


def main() -> int:
    findings: list[Finding] = []

    # The existing checkers already cover title, description, canonical,
    # hreflang, html lang, single H1, sitemap coverage and banned claims. Run
    # them rather than restating their rules here in a second, drifting copy.
    for tool, label in (("check-seo.py", "yapısal SEO"),
                        ("check-claims.py", "ürün iddiaları"),
                        ("link-map.py", "yetim sayfa")):
        code, out = run_tool(tool)
        if code != 0:
            for line in out.splitlines():
                line = line.strip()
                if not line or line.endswith("bulgu:") or line[0].isdigit():
                    continue
                findings.append(("—", label, "temiz", line[:110],
                                 f"python3 tools/{tool} çıktısına bak"))

    check_broken_links(findings)
    check_alt_text(findings)
    check_jsonld(findings)
    if "--live" in sys.argv:
        check_live(findings)

    n = len(pages())
    print(f"SEO kalite kapısı — {n} sayfa" + (" + canlı kontrol" if "--live" in sys.argv else ""))
    if not findings:
        print("\nGEÇTİ — yayınlanabilir.")
        return 0

    print(f"\nKALDI — {len(findings)} bulgu\n")
    head = ("URL", "Kontrol", "Beklenen", "Bulunan", "Önerilen düzeltme")
    rows = [head] + [tuple(str(c)[:60] for c in f) for f in findings]
    widths = [max(len(r[i]) for r in rows) for i in range(5)]
    for i, row in enumerate(rows):
        print("  " + " | ".join(c.ljust(widths[j]) for j, c in enumerate(row)))
        if i == 0:
            print("  " + "-+-".join("-" * w for w in widths))
    return 1


if __name__ == "__main__":
    sys.exit(main())
