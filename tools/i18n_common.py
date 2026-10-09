"""Shared by the page builders and the checks: which of the 20 extra
languages have a translated copy of which page.

English and Turkish are written by hand in the bilingual sources. The other
twenty are translations of the generated English page, stored as segment maps
in i18n/<lang>/<name>.json and rendered by tools/build-i18n.py. A page exists
in a language exactly when its translation file exists, so hreflang, the
sitemap and the checks can never disagree about what is published.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
I18N = ROOT / "i18n"

# folder -> hreflang code, og:locale
LANGS: dict[str, tuple[str, str]] = {
    "ar": ("ar", "ar_AR"), "cs": ("cs", "cs_CZ"), "da": ("da", "da_DK"),
    "de": ("de", "de_DE"), "el": ("el", "el_GR"), "es": ("es", "es_ES"),
    "fi": ("fi", "fi_FI"), "fr": ("fr", "fr_FR"), "hi": ("hi", "hi_IN"),
    "it": ("it", "it_IT"), "ja": ("ja", "ja_JP"), "ko": ("ko", "ko_KR"),
    "nb": ("nb", "nb_NO"), "nl": ("nl", "nl_NL"), "pl": ("pl", "pl_PL"),
    "pt": ("pt", "pt_PT"), "ru": ("ru", "ru_RU"), "sv": ("sv", "sv_SE"),
    "uk": ("uk", "uk_UA"), "zh": ("zh-Hans", "zh_CN"),
}
RTL = {"ar"}

# Legal pages have their own 20-language generator (build-legal.py).
NOT_TRANSLATED = {"privacy", "terms", "kvkk"}


def name_of(en_slug: str) -> str:
    return "home" if en_slug == "" else en_slug.replace("/", "__")


def has(lang: str, en_slug: str) -> bool:
    return lang in LANGS and (I18N / lang / f"{name_of(en_slug)}.json").exists()


def langs_for(en_slug: str) -> list[str]:
    return [l for l in LANGS if has(l, en_slug)]


def url_for(lang: str, slug: str, site: str = "https://dozify.app") -> str:
    return f"{site}/{lang}" if slug == "" else f"{site}/{lang}/{slug}"


def translated_files() -> list[str]:
    """Relative paths of every rendered translated page."""
    out = []
    for lang in LANGS:
        d = I18N / lang
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            if f.name.startswith("_"):
                continue
            slug = "" if f.stem == "home" else f.stem.replace("__", "/")
            rel = f"{lang}/" + ("index.html" if slug == "" else f"{slug}.html")
            if (ROOT / rel).exists():  # rendered by build-i18n (check.sh builds first)
                out.append(rel)
    return out


NATIVE = {
    "en": "English", "tr": "Türkçe", "ar": "العربية", "cs": "Čeština", "da": "Dansk",
    "de": "Deutsch", "el": "Ελληνικά", "es": "Español", "fi": "Suomi", "fr": "Français",
    "hi": "हिन्दी", "it": "Italiano", "ja": "日本語", "ko": "한국어", "nb": "Norsk",
    "nl": "Nederlands", "pl": "Polski", "pt": "Português", "ru": "Русский", "sv": "Svenska",
    "uk": "Українська", "zh": "简体中文",
}
LANG_LIST_START, LANG_LIST_END = "<!--langs-->", "<!--/langs-->"


def lang_list(en_slug: str, tr_slug: str, current: str) -> str:
    """Footer list of this page in every language it exists in.

    translate="no" keeps the names out of the translation segments: each
    language is written in its own script, so there is nothing to translate.
    """
    items = [("en", url_for("en", en_slug, site="")), ("tr", url_for("tr", tr_slug, site=""))]
    items += [(l, url_for(l, en_slug, site="")) for l in langs_for(en_slug)]
    if len(items) <= 2:
        return ""
    links = []
    for code, href in items:
        hl = LANGS[code][0] if code in LANGS else code
        cur = ' aria-current="page"' if code == current else ""
        links.append(f'<a href="{href}" hreflang="{hl}" lang="{hl}"{cur}>{NATIVE[code]}</a>')
    return (f'{LANG_LIST_START}<div class="container lang-list" translate="no">'
            + " · ".join(links) + f"</div>{LANG_LIST_END}")


def with_lang_list(html: str, en_slug: str, tr_slug: str, current: str) -> str:
    import re
    html = re.sub(re.escape(LANG_LIST_START) + ".*?" + re.escape(LANG_LIST_END), "", html, flags=re.S)
    block = lang_list(en_slug, tr_slug, current)
    return html.replace("</footer>", block + "</footer>", 1) if block else html
