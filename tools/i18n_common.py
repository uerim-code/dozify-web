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
            out.append(f"{lang}/" + ("index.html" if slug == "" else f"{slug}.html"))
    return out
