#!/usr/bin/env python3
"""Render the 20 extra languages from the generated English pages.

    python3 tools/build-i18n.py extract   # i18n/_source/*.json from en/
    python3 tools/build-i18n.py build     # <lang>/<slug>.html from i18n/<lang>/*.json

A page is cut into "segments": the inner HTML of every leaf block (p, li, h2,
td, …) plus loose inline text (breadcrumb spans, buttons, tags) and the
text-bearing attributes (alt, aria-label). Strings that appear on three or
more pages go to _common.json so the nav, footer and disclaimers are
translated once. A translation file maps each English segment to its
translation, inline tags and hrefs kept as they are.

Rendering starts from the English page, so layout, scripts and screenshots
are identical; only the words, the language attributes, canonical/hreflang,
internal links, the App Store campaign token and the JSON-LD change.
"""
import html as htmllib
import importlib.util
import json
import pathlib
import re
import shutil
import sys
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from i18n_common import I18N, LANGS, NOT_TRANSLATED, RTL, ROOT, has, langs_for, name_of, url_for  # noqa: E402
import structured_data as sd  # noqa: E402

spec = importlib.util.spec_from_file_location("bl", ROOT / "tools" / "build-languages.py")
bl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bl)
SRC = I18N / "_source"

BLOCK = {"h1", "h2", "h3", "h4", "h5", "p", "li", "td", "th", "figcaption", "summary",
         "dt", "dd", "blockquote", "caption", "label", "button"}
INLINE = {"a", "span", "strong", "em", "small", "b", "i", "div", "time", "cite"}
SKIP = {"script", "style", "svg", "head", "noscript", "code"}
VOID = {"img", "br", "hr", "meta", "link", "input", "source", "wbr", "area", "base", "col", "embed", "track"}
TEXT_ATTRS = ("alt", "aria-label", "title", "placeholder")


class Node:
    __slots__ = ("tag", "start", "inner_start", "inner_end", "end", "children", "parent", "text")

    def __init__(self, tag, start, inner_start, parent):
        self.tag, self.start, self.inner_start, self.parent = tag, start, inner_start, parent
        self.inner_end = self.end = None
        self.children, self.text = [], ""


class Tree(HTMLParser):
    def __init__(self, src: str):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.lines = [0]
        for m in re.finditer("\n", src):
            self.lines.append(m.end())
        self.root = Node("#root", 0, 0, None)
        self.cur = self.root
        self.feed(src)
        self.close()

    def _off(self) -> int:
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self._off()
        end = start + len(self.get_starttag_text())
        node = Node(tag, start, end, self.cur)
        self.cur.children.append(node)
        if tag in VOID:
            node.inner_end = node.end = end
        else:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        start = self._off()
        node = Node(tag, start, start + len(self.get_starttag_text()), self.cur)
        node.inner_end = node.end = node.inner_start
        self.cur.children.append(node)

    def handle_endtag(self, tag):
        pos = self._off()
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is self.root:
            return
        close = self.src.index(">", pos) + 1
        # close every element left open inside n
        x = self.cur
        while x is not n:
            if x.inner_end is None:
                x.inner_end = x.end = pos
            x = x.parent
        n.inner_end, n.end = pos, close
        self.cur = n.parent

    def handle_data(self, data):
        self.cur.text += data


def _has_block(n: Node) -> bool:
    return any(c.tag in BLOCK or _has_block(c) for c in n.children)


def _visible(fragment: str) -> str:
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmllib.unescape(t)).strip()


def segments(page: str) -> list[tuple[int, int, str]]:
    """(inner_start, inner_end, inner_html) of each translatable element."""
    body_at = page.find("<body")
    tree = Tree(page)
    out: list[tuple[int, int, str]] = []

    def walk(n: Node):
        if n.tag in SKIP or (n.inner_end is None and n.tag != "#root"):
            return
        if n.start >= body_at and n.tag not in VOID:
            inner = page[n.inner_start:n.inner_end]
            if re.search(r"[A-Za-z]", _visible(inner)) and not _has_block(n):
                if n.tag in BLOCK or (n.tag in INLINE and n.text.strip()):
                    out.append((n.inner_start, n.inner_end, inner))
                    return
        for c in n.children:
            walk(c)

    walk(tree.root)
    return out


def attr_texts(page: str) -> list[str]:
    body = page[page.find("<body"):]
    found = []
    for a in TEXT_ATTRS:
        for m in re.finditer(rf'\s{a}="([^"]*)"', body):
            if re.search(r"[A-Za-z]{2}", m.group(1)):
                found.append(m.group(1))
    return found


def en_pages() -> list[tuple[str, str]]:
    """(en_slug, generated english html) for every page that gets translated."""
    out = []
    for src, (en_slug, _tr) in bl.PAGES.items():
        if en_slug in NOT_TRANSLATED:
            continue
        html = bl.path_for("en", en_slug).read_text(encoding="utf-8")
        out.append((en_slug, sd.strip_jsonld(html)))
    return out


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def extract() -> int:
    if SRC.exists():
        shutil.rmtree(SRC)
    SRC.mkdir(parents=True)
    per_page: dict[str, list[str]] = {}
    count: dict[str, int] = {}
    for en_slug, html in en_pages():
        seen: list[str] = []
        for _a, _b, inner in segments(html):
            k = norm(inner)
            if k not in seen:
                seen.append(k)
        for a in attr_texts(html):
            k = norm(a)
            if k not in seen:
                seen.append(k)
        per_page[en_slug] = seen
        for k in seen:
            count[k] = count.get(k, 0) + 1
    common = sorted(k for k, n in count.items() if n >= 3)
    cset = set(common)
    (SRC / "_common.json").write_text(json.dumps({
        "og_image_alt": bl.OG_IMAGE_ALT["en"],
        "strings": common,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    words = sum(len(_visible(k).split()) for k in common)
    for en_slug, keys in per_page.items():
        title, desc = bl.META[en_slug]["en"]
        own = [k for k in keys if k not in cset]
        words += sum(len(_visible(k).split()) for k in own)
        (SRC / f"{name_of(en_slug)}.json").write_text(json.dumps({
            "url": url_for("en", en_slug),
            "meta": {"title": title, "description": desc},
            "strings": own,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(per_page)} pages, {len(common)} common strings, ~{words} words to translate per language")
    return 0


def _attr(v: str) -> str:
    return v.replace("&", "&amp;").replace('"', "&quot;")


def render(lang: str, en_slug: str, html: str, page_t: dict, common_t: dict) -> str:
    table = {**common_t["t"], **page_t["t"]}

    def tr(s: str) -> str:
        return table.get(norm(s), s)

    segs = segments(html)
    for a, b, inner in reversed(segs):
        html = html[:a] + tr(inner) + html[b:]
    for attr in TEXT_ATTRS:
        html = re.sub(rf'(\s{attr}=")([^"]*)(")',
                      lambda m: m.group(1) + _attr(htmllib.unescape(tr(m.group(2)))) + m.group(3)
                      if norm(m.group(2)) in table else m.group(0), html)

    code, og_locale = LANGS[lang]
    title, desc = page_t["meta"]["title"], page_t["meta"]["description"]
    ta, da = _attr(title), _attr(desc)
    html = re.sub(r'<html\s+lang="[^"]*"', f'<html lang="{code}"' + (' dir="rtl"' if lang in RTL else ""), html, count=1)
    html = re.sub(r"<title>.*?</title>", f"<title>{htmllib.escape(title, quote=False)}</title>", html, count=1, flags=re.S)
    for pat, val in ((r'(<meta\s+name="description"\s+content=")[^"]*(")', da),
                     (r'(<meta\s+property="og:title"\s+content=")[^"]*(")', ta),
                     (r'(<meta\s+property="og:description"\s+content=")[^"]*(")', da),
                     (r'(<meta\s+name="twitter:title"\s+content=")[^"]*(")', ta),
                     (r'(<meta\s+name="twitter:description"\s+content=")[^"]*(")', da),
                     (r'(<meta\s+property="og:locale"\s+content=")[^"]*(")', og_locale),
                     (r'(<meta\s+property="og:image:alt"\s+content=")[^"]*(")', _attr(common_t.get("og_image_alt", ""))),
                     (r'(<meta\s+name="twitter:image:alt"\s+content=")[^"]*(")', _attr(common_t.get("og_image_alt", "")))):
        html = re.sub(pat, lambda m, v=val: m.group(1) + v + m.group(2), html, count=1)
    html = re.sub(r'\s*<meta\s+property="og:locale:alternate"[^>]*>', "", html)
    html = re.sub(r'\s*<meta\s+name="keywords"[^>]*>', "", html)

    self_url = url_for(lang, en_slug)
    html = re.sub(r'(<meta\s+property="og:url"\s+content=")[^"]*(")', lambda m: m.group(1) + self_url + m.group(2), html, count=1)
    html = re.sub(r'\s*<link\s+rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\s*<link\s+rel="alternate"\s+hreflang="[^"]*"[^>]*>', "", html)
    html = html.replace("</head>", alternates(en_slug, self_url) + "\n</head>", 1)

    # Internal links: same language when that page exists in it.
    def link(m):
        path = m.group(1)
        slug = path[len("/en"):].lstrip("/")
        if slug in ("privacy", "terms"):
            return f'href="/{lang}/{slug}"'
        if has(lang, slug):
            return f'href="/{lang}' + (f"/{slug}" if slug else "") + '"'
        return m.group(0)
    html = re.sub(r'href="(/en(?:/[^"#?]*)?)"', link, html)
    html = re.sub(r"(ct=web-[a-z0-9-]*-)en\b", rf"\g<1>{lang}", html)

    graph = sd.build_graph(lang=lang, slug=en_slug, en_slug=en_slug, url=self_url, page=html,
                           source_html=(ROOT / src_of(en_slug)).read_text(encoding="utf-8"),
                           title=title, description=desc,
                           home_description=home_desc(lang))
    return html.replace("</head>", "  " + graph.replace("\n", "\n  ") + "\n</head>", 1)


def alternates(en_slug: str, self_url: str) -> str:
    en_url = url_for("en", en_slug)
    tr_slug = next(tr for (en, tr) in bl.PAGES.values() if en == en_slug)
    links = [f'\n  <link rel="canonical" href="{self_url}">',
             f'\n  <link rel="alternate" hreflang="en" href="{en_url}">',
             f'\n  <link rel="alternate" hreflang="tr" href="{url_for("tr", tr_slug)}">']
    for l in langs_for(en_slug):
        links.append(f'\n  <link rel="alternate" hreflang="{LANGS[l][0]}" href="{url_for(l, en_slug)}">')
    links.append(f'\n  <link rel="alternate" hreflang="x-default" href="{en_url}">')
    return "".join(links)


def src_of(en_slug: str) -> str:
    return next(src for src, (en, _tr) in bl.PAGES.items() if en == en_slug)


def home_desc(lang: str) -> str:
    f = I18N / lang / "home.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))["meta"]["description"]
    return bl.META[""]["en"][1]


def build() -> int:
    made = 0
    pages = dict(en_pages())
    for lang in LANGS:
        d = I18N / lang
        out_dir = ROOT / lang
        # Remove previously rendered pages; legal pages (build-legal) stay.
        for en_slug in pages:
            p = out_dir / ("index.html" if en_slug == "" else f"{en_slug}.html")
            if p.exists():
                p.unlink()
        if not d.exists():
            continue
        cf = d / "_common.json"
        common_t = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {"t": {}}
        common_t["t"] = {norm(k): v for k, v in common_t.get("t", {}).items()}
        for en_slug, html in pages.items():
            if not has(lang, en_slug):
                continue
            page_t = json.loads((d / f"{name_of(en_slug)}.json").read_text(encoding="utf-8"))
            page_t["t"] = {norm(k): v for k, v in page_t.get("t", {}).items()}
            out = out_dir / ("index.html" if en_slug == "" else f"{en_slug}.html")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render(lang, en_slug, html, page_t, common_t), encoding="utf-8")
            made += 1
    print(f"{made} translated pages rendered")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    sys.exit(extract() if cmd == "extract" else build())
