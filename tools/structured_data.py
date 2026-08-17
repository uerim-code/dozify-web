"""Build every page's JSON-LD from the page that is actually being shipped.

The site used to carry hand-written JSON-LD next to the markup. Two problems
came out of that. The FAQ schema on the homepage listed ten English questions
and was copied verbatim into the Turkish page, where none of those sentences
appear — schema describing content the visitor cannot see. And the schema drifts:
the answer text was edited in the markup and not in the block below it.

So the blocks are generated here, from the split HTML, after the language cut.
The questions in the schema are the questions on the page because they are read
off the page. Nothing is asserted that the markup does not show.

Facts that are language-independent and cannot be read off the page — an
article's publication date, its citation list — are lifted from the source's
old block, which is where they were recorded.

Entity @ids are shared across all forty pages, so the eight landing pages
describe one application rather than eight, and Organization/WebSite resolve to
a single node.
"""

from __future__ import annotations

import html as html_mod
import json
import re

SITE = "https://dozify.app"
ORG_ID = f"{SITE}/#organization"
SITE_ID = f"{SITE}/#website"
APP_ID = f"{SITE}/#app"

APP_STORE_URL = "https://apps.apple.com/app/dozify/id6764325653"
AUTHOR_ID = f"{SITE}/#author"
AUTHOR_NAME = "Ümit Can Erim"
OG_IMAGE = f"{SITE}/og-image.png"

# Slugs whose subject is the app itself rather than a topic.
LANDING = {
    "glp1-shot-tracker",
    "injection-site-tracker",
    "glp1-weight-tracker",
    "glp1-side-effect-journal",
    "glp1-vial-tracker",
    "private-glp1-tracker",
    "glp1-appointment-report",
    "switch-glp1-tracker-app",
    "why",
}

LABEL = {
    "home": {"en": "Home", "tr": "Ana sayfa"},
    "articles": {"en": "Articles", "tr": "Makaleler"},
}

LOCALE = {"en": "en", "tr": "tr"}


def _text(fragment: str) -> str:
    """Visible text of an HTML fragment, entities resolved, spacing collapsed."""
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_mod.unescape(fragment)).strip()


def visible_faqs(page: str) -> list[tuple[str, str]]:
    """Question/answer pairs a visitor can read on this page.

    Two shapes are in use: `.faq-item` blocks (h3 + paragraphs) on the homepage
    and the articles, and `<details><summary>` on the support page.
    """
    pairs: list[tuple[str, str]] = []

    for block in re.findall(r'<div class="faq-item">(.*?)</div>', page, re.S):
        q = re.search(r"<h3[^>]*>(.*?)</h3>", block, re.S)
        answers = re.findall(r"<p[^>]*>(.*?)</p>", block, re.S)
        if q and answers:
            pairs.append((_text(q.group(1)), " ".join(_text(a) for a in answers)))

    for block in re.findall(r"<details[^>]*>(.*?)</details>", page, re.S):
        q = re.search(r"<summary[^>]*>(.*?)</summary>", block, re.S)
        answers = re.findall(r"<p[^>]*>(.*?)</p>", block, re.S)
        if q and answers:
            pairs.append((_text(q.group(1)), " ".join(_text(a) for a in answers)))

    return [(q, a) for q, a in pairs if q and a]


def heading(page: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    return _text(m.group(1)) if m else ""


def visible_breadcrumb(page: str, url: str) -> list[tuple[str, str]] | None:
    """The trail the visitor can see, if the page draws one.

    Where a page shows a breadcrumb, that is what BreadcrumbList should say.
    Deriving it from the H1 instead put "GLP-1 nedir? Hormon, açılımı ve nasıl
    çalıştığı" in the schema next to a crumb reading "GLP-1 nedir?".
    """
    m = re.search(r'<(?:div|nav) class="breadcrumb"[^>]*>(.*?)</(?:div|nav)>', page, re.S)
    if not m:
        return None
    trail: list[tuple[str, str]] = []
    for tag in re.finditer(r'<(a|span)([^>]*)>(.*?)</\1>', m.group(1), re.S):
        attrs, name = tag.group(2), _text(tag.group(3))
        if not name or name in {"/", "›", "»", ">"} or "aria-hidden" in attrs:
            continue
        href = re.search(r'href="([^"]*)"', attrs)
        trail.append((name, SITE + href.group(1) if href else url))
    return trail or None


def source_facts(source_html: str) -> dict:
    """Dates and citations recorded in the source's own block."""
    facts: dict = {}
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source_html, re.S):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for node in data.get("@graph", [data]):
            if not isinstance(node, dict):
                continue
            for key in ("datePublished", "dateModified", "lastReviewed", "citation"):
                if key in node and key not in facts:
                    facts[key] = node[key]
    return facts


def strip_jsonld(page: str) -> str:
    return re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", page, flags=re.S)


def _author(lang: str) -> dict:
    """A named person, and what they are not.

    E-E-A-T asks who wrote this. The honest answer here is one developer who
    reads the primary sources — so the byline names him and the description
    says he is not a clinician, which is also why no page claims a medical
    review. The editorial policy page is where that is spelled out.
    """
    return {
        "@type": "Person",
        "@id": AUTHOR_ID,
        "name": AUTHOR_NAME,
        "url": f"{SITE}/{lang}/" + ("editorial-policy" if lang == "en" else "yayin-ilkeleri"),
        "description": (
            "Developer of Dozify. Writes these guides from primary sources; not a clinician."
            if lang == "en" else
            "Dozify'ın geliştiricisi. Bu rehberleri birincil kaynaklardan yazıyor; hekim değil."
        ),
    }


def _organization() -> dict:
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": "Dozify",
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": OG_IMAGE, "width": 1200, "height": 630},
    }


def _website(lang: str) -> dict:
    return {
        "@type": "WebSite",
        "@id": SITE_ID,
        "name": "Dozify",
        "url": f"{SITE}/{lang}",
        "publisher": {"@id": ORG_ID},
        "inLanguage": LOCALE[lang],
    }


def _application(lang: str, description: str) -> dict:
    # Every field here is checkable on the App Store listing: it is an iOS-only
    # health app, free to download, with the subscription sold inside it. No
    # rating, no install count, no award — none of that is ours to state.
    return {
        "@type": "MobileApplication",
        "@id": APP_ID,
        "name": "Dozify",
        "operatingSystem": "iOS",
        "applicationCategory": "HealthApplication",
        "url": f"{SITE}/{lang}",
        "downloadUrl": APP_STORE_URL,
        "installUrl": APP_STORE_URL,
        "description": description,
        "publisher": {"@id": ORG_ID},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "inLanguage": LOCALE[lang],
    }


def _breadcrumb(url: str, lang: str, trail: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "@id": f"{url}#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": item}
            for i, (name, item) in enumerate(trail, start=1)
        ],
    }


def build_graph(
    *,
    lang: str,
    slug: str,
    en_slug: str,
    url: str,
    page: str,
    source_html: str,
    title: str,
    description: str,
    home_description: str,
) -> str:
    """The whole page's JSON-LD, as one @graph script tag."""
    is_home = en_slug == ""
    is_article = en_slug.startswith("articles/")
    is_article_index = en_slug == "articles"
    is_landing = en_slug in LANDING

    home_url = f"{SITE}/{lang}"
    name = heading(page) or title
    trail = visible_breadcrumb(page, url)
    if trail is None:
        trail = [(LABEL["home"][lang], home_url)]
        if is_article:
            articles_slug = slug.rsplit("/", 1)[0]
            trail.append((LABEL["articles"][lang], f"{SITE}/{lang}/{articles_slug}"))
        if not is_home:
            trail.append((name, url))

    if is_article:
        page_type: list[str] = ["MedicalWebPage"]
    elif is_article_index:
        page_type = ["CollectionPage"]
    else:
        page_type = ["WebPage"]

    faqs = visible_faqs(page)
    if faqs:
        page_type.append("FAQPage")

    node: dict = {
        "@type": page_type[0] if len(page_type) == 1 else page_type,
        "@id": f"{url}#webpage",
        "url": url,
        "name": title,
        "description": description,
        "isPartOf": {"@id": SITE_ID},
        "inLanguage": LOCALE[lang],
    }
    if len(trail) > 1:
        node["breadcrumb"] = {"@id": f"{url}#breadcrumb"}
    if faqs:
        node["mainEntity"] = [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ]
    elif is_home or is_landing:
        node["mainEntity"] = {"@id": APP_ID}

    if is_article:
        facts = source_facts(source_html)
        node["headline"] = name or title
        node["author"] = {"@id": AUTHOR_ID}
        node["publisher"] = {"@id": ORG_ID}
        node["image"] = OG_IMAGE
        if "datePublished" in facts:
            node["datePublished"] = facts["datePublished"]
            node["dateModified"] = facts.get("dateModified", facts["datePublished"])
        if "lastReviewed" in facts:
            # The date the reference list was last opened and checked. Not a
            # clinical review: nobody has reviewed this content clinically, so
            # reviewedBy stays absent rather than being filled with the author.
            node["lastReviewed"] = facts["lastReviewed"]
        if "citation" in facts:
            node["citation"] = facts["citation"]

    graph: list[dict] = [_organization(), _website(lang)]
    if is_article:
        graph.append(_author(lang))
    if is_home or is_landing:
        graph.append(_application(lang, home_description))
    graph.append(node)
    if len(trail) > 1:
        graph.append(_breadcrumb(url, lang, trail))

    body = json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, indent=2)
    return '<script type="application/ld+json">\n' + body + "\n</script>"
