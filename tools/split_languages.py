#!/usr/bin/env python3
"""Split each dual-language page into an English one and a Turkish one.

Today every page carries both languages in one document and picks between them
with CSS driven by <html lang>, which JavaScript sets from the device time
zone. That gives Google two H1s, one <html lang> that is wrong for half the
visitors, and no way to rank the Turkish copy on its own URL.

This produces /en/<slug> and /tr/<slug> from the existing file, keeping only
the elements for that language.

Why a purpose-built parser: 356 of the 721 language pairs sit inside a
sentence rather than being whole blocks, so a regex over lines cuts words in
half. html.parser gives us the tag stream; we rebuild the document from it and
drop any element (with its whole subtree) whose data-lang is the other
language. Entities are left untouched — convert_charrefs=False — because
re-encoding them changes the Turkish text.
"""

from __future__ import annotations

import html.parser
import os
import re
import sys

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class LanguageFilter(html.parser.HTMLParser):
    """Rebuild the document, dropping elements of the unwanted language."""

    def __init__(self, keep: str):
        super().__init__(convert_charrefs=False)
        self.keep = keep
        self.out: list[str] = []
        # Depth counter for the subtree currently being dropped; 0 = emitting.
        self.skip_depth = 0
        self.dropped = 0

    # -- emission helpers ---------------------------------------------------
    def emit(self, text: str) -> None:
        if self.skip_depth == 0:
            self.out.append(text)

    @staticmethod
    def render(tag: str, attrs: list[tuple[str, str | None]], closing: str = "") -> str:
        parts = [tag]
        for k, v in attrs:
            parts.append(k if v is None else f'{k}="{v}"')
        return "<" + " ".join(parts) + closing + ">"

    # -- parser callbacks ---------------------------------------------------
    def handle_starttag(self, tag, attrs):
        lang = dict(attrs).get("data-lang")
        if self.skip_depth:
            if tag not in VOID:
                self.skip_depth += 1
            return
        if lang and lang != self.keep:
            self.dropped += 1
            if tag not in VOID:
                self.skip_depth = 1
            return
        # The attribute has done its job once the page is single-language.
        attrs = [(k, v) for k, v in attrs if k != "data-lang"]
        self.emit(self.render(tag, attrs))

    def handle_startendtag(self, tag, attrs):
        lang = dict(attrs).get("data-lang")
        if self.skip_depth:
            return
        if lang and lang != self.keep:
            self.dropped += 1
            return
        attrs = [(k, v) for k, v in attrs if k != "data-lang"]
        self.emit(self.render(tag, attrs, " /"))

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in VOID:
            return
        self.emit(f"</{tag}>")

    def handle_data(self, data):
        self.emit(data)

    def handle_entityref(self, name):
        self.emit(f"&{name};")

    def handle_charref(self, name):
        self.emit(f"&#{name};")

    def handle_comment(self, data):
        self.emit(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.emit(f"<!{decl}>")

    def handle_pi(self, data):
        self.emit(f"<?{data}>")


def split(src: str, keep: str) -> tuple[str, int]:
    f = LanguageFilter(keep)
    f.feed(src)
    f.close()
    return "".join(f.out), f.dropped


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    src = open(path, encoding="utf-8").read()
    for lang in ("en", "tr"):
        out, dropped = split(src, lang)
        h1 = len(re.findall(r"<h1\b", out))
        print(f"{lang}: {len(out)} bayt, {dropped} blok atıldı, H1 sayısı {h1}")
        open(f"/tmp/split-{lang}.html", "w", encoding="utf-8").write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
