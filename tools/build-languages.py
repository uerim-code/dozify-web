#!/usr/bin/env python3
"""Generate the /en/ and /tr/ trees from the dual-language sources.

Each source page currently holds both languages and picks between them with
CSS. That gives Google two H1s per page, an <html lang> that is wrong for half
the visitors, and no URL the Turkish copy can rank on. This writes each page
twice — once per language — with:

  * only that language's markup (tools/split-languages.py does the cutting)
  * <html lang> set to it
  * a self-canonical on its own URL
  * reciprocal hreflang, plus x-default on the English side
  * internal links rewritten into the same language tree
  * a visible EN/TR switcher that links to the page's counterpart

Turkish slugs are the phrases Turkish users actually search, not transliterated
English ones: /tr/glp1-igne-takibi, not /tr/glp1-shot-tracker. That is the
whole point of giving the language its own URL.

Run from the repo root: python3 tools/build-languages.py
"""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from split_languages import split  # noqa: E402
from metadata import META  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://dozify.app"

# source file -> (english slug, turkish slug). "" is the tree's index.
PAGES: dict[str, tuple[str, str]] = {
    "index.html":                     ("", ""),
    "glp1-shot-tracker.html":         ("glp1-shot-tracker", "glp1-igne-takibi"),
    "injection-site-tracker.html":    ("injection-site-tracker", "enjeksiyon-bolgesi-takibi"),
    "glp1-weight-tracker.html":       ("glp1-weight-tracker", "glp1-kilo-takibi"),
    "glp1-side-effect-journal.html":  ("glp1-side-effect-journal", "yan-etki-gunlugu"),
    "glp1-vial-tracker.html":         ("glp1-vial-tracker", "flakon-takibi"),
    "private-glp1-tracker.html":      ("private-glp1-tracker", "gizli-glp1-takibi"),
    "glp1-appointment-report.html":   ("glp1-appointment-report", "doktor-raporu"),
    "switch-glp1-tracker-app.html":   ("switch-glp1-tracker-app", "baska-uygulamadan-gecis"),
    "why.html":                       ("why", "neden-dozify"),
    "support.html":                   ("support", "destek"),
    "privacy.html":                   ("privacy", "gizlilik"),
    "terms.html":                     ("terms", "kullanim-kosullari"),
    "kvkk.html":                      ("kvkk", "kvkk"),
    "articles/index.html":            ("articles", "makaleler"),
    "articles/what-is-glp1.html":     ("articles/what-is-glp1", "makaleler/glp1-nedir"),
    "articles/how-to-inject-glp1.html": ("articles/how-to-inject-glp1", "makaleler/glp1-nasil-yapilir"),
    "articles/glp1-injection-sites.html": ("articles/glp1-injection-sites", "makaleler/glp1-enjeksiyon-bolgeleri"),
    "articles/glp1-side-effects.html": ("articles/glp1-side-effects", "makaleler/glp1-yan-etkileri"),
    "articles/glp1-patches.html":     ("articles/glp1-patches", "makaleler/glp1-bantlari"),
}

SWITCHER = {
    "en": ('<a class="lang-switch" href="{other}" hreflang="tr" lang="tr" '
           'rel="alternate">Türkçe</a>'),
    "tr": ('<a class="lang-switch" href="{other}" hreflang="en" lang="en" '
           'rel="alternate">English</a>'),
}


def url_for(lang: str, slug: str) -> str:
    return f"{SITE}/{lang}/" if slug == "" else f"{SITE}/{lang}/{slug}"


def path_for(lang: str, slug: str) -> pathlib.Path:
    return ROOT / lang / ("index.html" if slug == "" else f"{slug}.html")


def rewrite_links(html: str, lang: str) -> str:
    """Point internal links at the same language tree."""
    # Longest first, so /articles/what-is-glp1 is not eaten by /articles.
    for src, (en, tr) in sorted(PAGES.items(), key=lambda kv: -len(kv[1][0])):
        old = "/" + PAGES[src][0]
        new = "/" + lang + "/" + (en if lang == "en" else tr)
        if PAGES[src][0] == "":
            continue  # the bare "/" is handled below
        html = html.replace(f'href="{old}"', f'href="{new}"')
    # Home last, and only as an exact href, or it matches every path.
    html = html.replace('href="/"', f'href="/{lang}/"')
    return html


def head_tags(lang: str, en_slug: str, tr_slug: str) -> str:
    en_url, tr_url = url_for("en", en_slug), url_for("tr", tr_slug)
    self_url = en_url if lang == "en" else tr_url
    return (
        f'\n  <link rel="canonical" href="{self_url}">'
        f'\n  <link rel="alternate" hreflang="en" href="{en_url}">'
        f'\n  <link rel="alternate" hreflang="tr" href="{tr_url}">'
        f'\n  <link rel="alternate" hreflang="x-default" href="{en_url}">'
    )


def build_page(src: str, lang: str, en_slug: str, tr_slug: str) -> str:
    raw = (ROOT / src).read_text(encoding="utf-8")
    html, _ = split(raw, lang)

    html = re.sub(r'<html\s+lang="[^"]*"', f'<html lang="{lang}"', html, count=1)

    # Title and description are written per language, not translated — 19 of
    # the 20 Turkish pages were otherwise inheriting the English title, which
    # is the line a Turkish user decides on in the results page.
    title, desc = META[en_slug][lang]
    # These land inside content="…" attributes. A quotation mark in the copy —
    # and the side-effect description quotes a patient saying "I had nausea" —
    # closes the attribute early and truncates the description to nothing.
    def attr(v: str) -> str:
        return v.replace("&", "&amp;").replace('"', "&quot;")
    title_a, desc_a = attr(title), attr(desc)
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    if re.search(r'<meta\s+name="description"', html):
        html = re.sub(r'(<meta\s+name="description"\s+content=")[^"]*(")',
                      lambda m: m.group(1) + desc_a + m.group(2), html, count=1)
    else:
        html = html.replace("</head>", f'  <meta name="description" content="{desc_a}">\n</head>', 1)
    # Open Graph must say the same thing as the page.
    for prop, val in (("og:title", title_a), ("og:description", desc_a)):
        if f'property="{prop}"' in html:
            html = re.sub(rf'(<meta\s+property="{prop}"\s+content=")[^"]*(")',
                          lambda m, v=val: m.group(1) + v + m.group(2), html, count=1)
        else:
            html = html.replace("</head>", f'  <meta property="{prop}" content="{val}">\n</head>', 1)
    if 'name="twitter:card"' not in html:
        html = html.replace("</head>", '  <meta name="twitter:card" content="summary_large_image">\n</head>', 1)
    # Drop the old canonical and any stray alternates, then add the real set.
    html = re.sub(r'\s*<link\s+rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\s*<link\s+rel="alternate"[^>]*>', "", html)
    html = html.replace("</head>", head_tags(lang, en_slug, tr_slug) + "\n</head>", 1)

    self_url = url_for(lang, en_slug if lang == "en" else tr_slug)
    html = re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*(")',
                  lambda m: m.group(1) + self_url + m.group(2), html)
    if 'property="og:locale"' not in html:
        loc = "en_US" if lang == "en" else "tr_TR"
        alt = "tr_TR" if lang == "en" else "en_US"
        html = html.replace("</head>",
                            f'  <meta property="og:locale" content="{loc}">\n'
                            f'  <meta property="og:locale:alternate" content="{alt}">\n</head>', 1)

    # Language-specific screenshots only — the other language's images were
    # being downloaded by every visitor and shown to none of them.
    other = "tr" if lang == "en" else "en"
    html = html.replace(f"screenshots/{other}/", f"screenshots/{lang}/")
    html = html.replace(f'src="screenshots/', f'src="/screenshots/')

    html = rewrite_links(html, lang)

    other_url = url_for("tr" if lang == "en" else "en",
                        tr_slug if lang == "en" else en_slug)
    switcher = SWITCHER[lang].format(other=other_url)
    html = re.sub(r"(</nav>)", switcher + r"\1", html, count=1)

    # Assets are referenced relative today; the trees are one level deeper.
    html = re.sub(r'(href|src)="(styles\.css|lang\.js|favicon\.svg|og-image\.png)"',
                  r'\1="/\2"', html)
    return html


def main() -> int:
    made = []
    for lang in ("en", "tr"):
        tree = ROOT / lang
        if tree.exists():
            shutil.rmtree(tree)
    for src, (en_slug, tr_slug) in PAGES.items():
        for lang in ("en", "tr"):
            slug = en_slug if lang == "en" else tr_slug
            out = path_for(lang, slug)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(build_page(src, lang, en_slug, tr_slug), encoding="utf-8")
            made.append(out.relative_to(ROOT).as_posix())
    print(f"{len(made)} sayfa üretildi")
    for m in made[:6]:
        print("  ", m)
    print("   …")
    return 0


if __name__ == "__main__":
    sys.exit(main())
