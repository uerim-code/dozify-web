#!/usr/bin/env python3
"""The internal link graph, counting only links inside the page's own content.

Header and footer links are on all forty pages; counting them would say every
page is well linked and no page is an orphan, which is the opposite of what
this is for. So only what is inside <main> counts.

  python3 tools/link-map.py            # report + fail on an orphan
  python3 tools/link-map.py --markdown # the table for docs/

Exit code 1 if a page inside a tree is unreachable from any other page's body.
"""

from __future__ import annotations

import glob
import html as html_mod
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metadata import INTENT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = ("en", "tr")


def _pages() -> dict[str, tuple[str, str]]:
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build-languages.py")
    spec = importlib.util.spec_from_file_location("build_languages", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PAGES


PAGES = _pages()
EN_FOR = {}
for en, tr in PAGES.values():
    EN_FOR[("en", en)] = en
    EN_FOR[("tr", tr)] = en


def url_of(path: str) -> str:
    rel = os.path.relpath(path, ROOT).removesuffix(".html")
    return "/" + (rel[: -len("/index")] if rel.endswith("/index") else rel)


def body(src: str) -> str:
    m = re.search(r"<main\b[^>]*>(.*?)</main>", src, re.S)
    return m.group(1) if m else ""


def purpose(src_slug: str, dst_slug: str) -> str:
    article = lambda s: s.startswith("articles")
    if article(src_slug) and not article(dst_slug):
        return "makaleden ürüne — okuyucuyu konunun karşılığı olan özelliğe götürür"
    if not article(src_slug) and article(dst_slug):
        return "üründen makaleye — iddiayı kaynaklı içerikle destekler"
    if article(src_slug) and article(dst_slug):
        return "makaleden makaleye — komşu niyeti karşılar, kanibalizasyonu önler"
    return "ürün sayfaları arası — bitişik özelliğe geçiş"


def main() -> int:
    out_links: dict[str, list[tuple[str, str]]] = defaultdict(list)
    in_links: dict[str, int] = defaultdict(int)
    all_urls: set[str] = set()

    for tree in TREES:
        for path in sorted(glob.glob(os.path.join(ROOT, tree, "**", "*.html"), recursive=True)):
            url = url_of(path)
            all_urls.add(url)
            src = open(path, encoding="utf-8").read()
            for m in re.finditer(r'<a[^>]+href="(/(?:en|tr)/?[^"#]*)"[^>]*>(.*?)</a>',
                                 body(src), re.S):
                target = m.group(1).rstrip("/")
                anchor = re.sub(r"\s+", " ", html_mod.unescape(
                    re.sub(r"<[^>]+>", "", m.group(2)))).strip()
                if target == url or not anchor:
                    continue
                out_links[url].append((target, anchor))

    for url, links in out_links.items():
        for target, _ in links:
            if target in all_urls:
                in_links[target] += 1

    orphans = sorted(u for u in all_urls if in_links[u] == 0)
    thin = sorted(u for u in all_urls if len(out_links[u]) == 0)

    if "--markdown" in sys.argv:
        print("# Faz 5.1 — iç bağlantı haritası\n")
        print("`tools/link-map.py` üretti. Yalnızca `<main>` içindeki bağlantılar; "
              "menü ve altbilgi sayılmıyor, çünkü onlar her sayfada var.\n")
        print("| Kaynak URL | Hedef URL | Anchor | Bağlantının amacı | Hedef sorgu |")
        print("|---|---|---|---|---|")
        for url in sorted(out_links):
            lang = url.split("/")[1]
            src_slug = EN_FOR.get((lang, url.split("/", 2)[2] if url.count("/") > 1 else ""), "")
            for target, anchor in out_links[url]:
                if target not in all_urls:
                    continue
                t_lang = target.split("/")[1]
                t_slug = EN_FOR.get((t_lang, target.split("/", 2)[2] if target.count("/") > 1 else ""), "")
                query = INTENT.get(t_slug, {}).get(t_lang, ("", ""))[1]
                print(f"| `{url}` | `{target}` | {anchor} | {purpose(src_slug, t_slug)} | {query} |")
        return 0

    print(f"{len(all_urls)} sayfa, gövde içi {sum(len(v) for v in out_links.values())} iç bağlantı")
    print(f"en çok bağlanan: " + ", ".join(
        f"{u} ({n})" for u, n in sorted(in_links.items(), key=lambda kv: -kv[1])[:5]))
    if thin:
        print(f"\ngövdesinden hiç iç bağlantı vermeyen {len(thin)} sayfa:")
        for u in thin:
            print("  " + u)
    if orphans:
        print(f"\n{len(orphans)} yetim sayfa (hiçbir sayfanın gövdesinden bağlantı almıyor):")
        for u in orphans:
            print("  " + u)
        return 1
    print("\nyetim sayfa yok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
