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
from structured_data import build_graph, strip_jsonld  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://dozify.app"
APP_STORE_URL = "https://apps.apple.com/app/dozify/id6764325653"

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
    "editorial-policy.html":          ("editorial-policy", "yayin-ilkeleri"),
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
    "articles/missed-glp1-dose.html": ("articles/missed-glp1-dose", "makaleler/kacirilan-glp1-dozu"),
    "articles/storing-glp1-pens.html": ("articles/storing-glp1-pens", "makaleler/glp1-kalemi-saklama"),
    "articles/glp1-appointment-checklist.html": ("articles/glp1-appointment-checklist", "makaleler/randevu-kontrol-listesi"),
    "articles/injection-site-lumps.html": ("articles/injection-site-lumps", "makaleler/enjeksiyon-bolgesi-sertlesme"),
    "articles/glp1-reminders-that-work.html": ("articles/glp1-reminders-that-work", "makaleler/ise-yarayan-hatirlatici"),
    "articles/reading-a-weight-trend.html": ("articles/reading-a-weight-trend", "makaleler/kilo-trendini-okumak"),
}

# The share image is the same for every page, so its description is written
# once per language rather than faked per page.
OG_IMAGE_ALT = {
    "en": "Dozify — a private GLP-1 injection and weight tracker for iPhone",
    "tr": "Dozify — iPhone için gizli GLP-1 enjeksiyon ve kilo takip uygulaması",
}

BRAND = "#0D9488"

SWITCHER = {
    "en": ('<a class="lang-switch" href="{other}" hreflang="tr" lang="tr" '
           'rel="alternate">Türkçe</a>'),
    "tr": ('<a class="lang-switch" href="{other}" hreflang="en" lang="en" '
           'rel="alternate">English</a>'),
}


def url_for(lang: str, slug: str) -> str:
    # No trailing slash: vercel.json sets trailingSlash false, so /en/ 308s to
    # /en. A canonical pointing at a URL that redirects is a hop Google has to
    # follow to reach the page it was just told is canonical.
    return f"{SITE}/{lang}" if slug == "" else f"{SITE}/{lang}/{slug}"


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
    html = html.replace('href="/"', f'href="/{lang}"')
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
    # The rest of the share card. Half the pages carried none of this, so a
    # link to them previewed as a bare URL.
    alt = attr(OG_IMAGE_ALT[lang])
    og_type = "article" if en_slug.startswith("articles/") else "website"
    for tag, value in (
        ('<meta property="og:site_name" content="{}">', "Dozify"),
        ('<meta property="og:type" content="{}">', og_type),
        ('<meta property="og:image" content="{}">', f"{SITE}/og-image.png"),
        ('<meta property="og:image:width" content="{}">', "1200"),
        ('<meta property="og:image:height" content="{}">', "630"),
        ('<meta property="og:image:alt" content="{}">', alt),
        ('<meta name="twitter:title" content="{}">', title_a),
        ('<meta name="twitter:description" content="{}">', desc_a),
        ('<meta name="twitter:image" content="{}">', f"{SITE}/og-image.png"),
        ('<meta name="twitter:image:alt" content="{}">', alt),
        ('<meta name="theme-color" content="{}">', BRAND),
    ):
        key = re.search(r'(property|name)="([^"]+)"', tag).group(2)
        if f'"{key}"' in html:
            html = re.sub(rf'(<meta\s+(?:property|name)="{re.escape(key)}"\s+content=")[^"]*(")',
                          lambda m, v=value: m.group(1) + v + m.group(2), html, count=1)
        else:
            html = html.replace("</head>", "  " + tag.format(value) + "\n</head>", 1)
    if "apple-touch-icon" not in html:
        html = html.replace(
            "</head>",
            '  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n</head>', 1)
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

    # A phone frame is 280–300 CSS pixels wide. The 750w file is the right one
    # for a 2x screen and two and a half times too much for a 1x one, so both
    # widths are offered and the browser picks.
    def responsive(m: re.Match) -> str:
        tag, path = m.group(0), m.group(1)
        if "srcset=" in tag:
            return tag
        small = path.replace(".webp", "-400w.webp")
        return tag.replace(
            f'src="{path}"',
            f'src="{path}" srcset="{small} 400w, {path} 750w" '
            'sizes="(min-width: 900px) 300px, 72vw"',
        )

    html = re.sub(r'<img[^>]+src="(/screenshots/[^"]+\.webp)"[^>]*>', responsive, html)

    html = rewrite_links(html, lang)

    other_url = url_for("tr" if lang == "en" else "en",
                        tr_slug if lang == "en" else en_slug)
    switcher = SWITCHER[lang].format(other=other_url)
    html = re.sub(r"(</nav>)", switcher + r"\1", html, count=1)

    # Tag each page's App Store link with its own campaign token, so App
    # Analytics can say which page sent the install. It is a query parameter
    # Apple reads on its own side — no script on the page, nothing about the
    # visitor, and it works with the tracking permission denied.
    campaign = f"web-{en_slug.replace('/', '-') or 'home'}-{lang}"[:40]
    html = html.replace(APP_STORE_URL, f"{APP_STORE_URL}?ct={campaign}")

    # lang.js guessed the visitor's language from their time zone and wrote it
    # into <html lang>. That was right when both languages shared a document;
    # on a page whose URL already declares its language it overwrites the
    # declaration — a Turkish visitor reading /en/… was served lang="tr", and a
    # crawler rendering the page saw the same thing.
    html = re.sub(r'\s*<script src="/?lang\.js"[^>]*></script>', "", html)

    # Assets are referenced relative today; the trees are one level deeper.
    html = re.sub(r'(href|src)="(styles\.css|lang\.js|favicon\.svg|og-image\.png)"',
                  r'\1="/\2"', html)

    # The hand-written blocks described the English page and were copied into
    # the Turkish one unchanged. Read the shipped page instead.
    source_html = raw
    html = strip_jsonld(html)
    graph = build_graph(
        lang=lang,
        slug=en_slug if lang == "en" else tr_slug,
        en_slug=en_slug,
        url=self_url,
        page=html,
        source_html=source_html,
        title=title,
        description=desc,
        home_description=META[""][lang][1],
    )
    html = html.replace("</head>", "  " + graph.replace("\n", "\n  ") + "\n</head>", 1)
    return html


def write_sitemap(pages: list[tuple[str, str, str]]) -> int:
    """Write sitemap.xml from the pages that were just built.

    It was maintained by hand, which lasts exactly until someone adds a page and
    forgets. lastmod comes from the source file's last commit rather than from
    today's date: a sitemap that claims every page changed today is a sitemap
    Google stops believing.
    """
    import datetime
    import subprocess

    rows = []
    for src, en_slug, tr_slug in pages:
        try:
            stamp = subprocess.run(["git", "log", "-1", "--format=%cs", "--", src],
                                   cwd=ROOT, capture_output=True, text=True,
                                   check=True).stdout.strip()
            # A page edited but not yet committed has no commit date, or a stale
            # one. Using today's is both true and stable: committing it today
            # makes git agree, so the next build does not silently change the
            # file and fail the gate over a diff nobody made. Before this it
            # took two commits to add a page, the second one meaningless.
            dirty = subprocess.run(["git", "status", "--porcelain", "--", src],
                                   cwd=ROOT, capture_output=True, text=True,
                                   check=True).stdout.strip()
            if dirty or not stamp:
                stamp = datetime.date.today().isoformat()
        except Exception:
            stamp = ""
        en_url, tr_url = url_for("en", en_slug), url_for("tr", tr_slug)
        for self_url in (en_url, tr_url):
            rows.append(
                f"  <url>\n    <loc>{self_url}</loc>\n"
                + (f"    <lastmod>{stamp}</lastmod>\n" if stamp else "")
                + f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>\n'
                  f'    <xhtml:link rel="alternate" hreflang="tr" href="{tr_url}"/>\n'
                  f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en_url}"/>\n'
                  "  </url>"
            )
    body = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(sorted(rows)) + "\n</urlset>\n")
    (ROOT / "sitemap.xml").write_text(body, encoding="utf-8")
    return len(rows)


def write_vercelignore() -> int:
    """Keep the sources out of the deploy, from the same list the build reads.

    Hand-maintained, this file is one forgotten line away from publishing a
    page twice — once in its generated form and once in the old two-H1 source,
    with the source at the shorter URL.
    """
    lines = [
        "# Generated by tools/build-languages.py — edit PAGES there, not here.",
        "#",
        "# The dual-language sources the /en and /tr trees are built from. Kept in",
        "# git so the build is reproducible; not served, or every page would exist",
        "# twice, the second time in its old two-H1 shape.",
        "#",
        "# Leading slash matters: an unanchored pattern also matches the generated",
        "# en/ and tr/ copies and takes the whole tree down.",
    ]
    lines += sorted("/" + src for src in PAGES)
    lines += ["/tools/", "/docs/"]
    (ROOT / ".vercelignore").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(PAGES)


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
    write_vercelignore()
    n = write_sitemap([(src, en, tr) for src, (en, tr) in PAGES.items()])
    print(f"{len(made)} sayfa üretildi, sitemap {n} kayıt")
    for m in made[:6]:
        print("  ", m)
    print("   …")
    return 0


if __name__ == "__main__":
    sys.exit(main())
