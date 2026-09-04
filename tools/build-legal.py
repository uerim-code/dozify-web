#!/usr/bin/env python3
"""Yalnız hukuki sayfaları, sitenin çevrilmemiş dilleri için üretir.

NEDEN AYRI BİR ÜRETEÇ

`build-languages.py` sitenin tamamını iki dilde kuruyor: kaynak sayfalar iki
dilli yazılıyor, slug haritası her sayfanın Türkçe karşılığını tutuyor ve
üreteç `en/` ile `tr/` ağaçlarını sıfırdan yazıyor. O yolu beş dile açmak, her
pazarlama sayfasının da o dile çevrilmesi demek.

Oysa zorunlu olan pazarlama değil: uygulama içindeki abonelik akışı Gizlilik
Politikası ve Kullanım Koşulları linklerini göstermek zorunda, ve etiket
Almancaysa sayfanın da Almanca açılması gerekiyor. Bu araç yalnız o iki
belgeyi üretiyor.

Sayfalar bilerek kendi kendine yetiyor: sitenin gezinme çubuğu ve alt bilgisi
İngilizce pazarlama sayfalarına bağlanıyor ve o sayfalar bu dillerde yok. Yarı
çevrilmiş bir menü, çevrilmemiş bir menüden kötüdür.

`build-languages.py` yalnız `en/` ve `tr/` dizinlerini siliyor, bu yüzden
burada üretilenler onun çalışmasından etkilenmiyor.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://dozify.app"

# Belgelerin İngilizce ve Türkçe karşılıkları zaten sitede; hreflang bunları da
# göstersin ki arama motoru sayfaları birbirinin çevirisi olarak eşlesin.
# Arapça sağdan sola yazılıyor. <html dir> olmadan tarayıcı sayfayı soldan
# sağa diziyor: paragraflar sola dayanıyor, noktalama satır sonunda yanlış
# tarafa düşüyor, madde işaretleri solda kalıyor. Metnin kendisi doğru olsa
# bile sayfa Arapça bir okura bozuk görünüyor.
RTL = {"ar", "he", "fa", "ur"}

CANONICAL = {
    "privacy": {"en": "/en/privacy", "tr": "/tr/gizlilik"},
    "terms": {"en": "/en/terms", "tr": "/tr/kullanim-kosullari"},
}

PAGE_CSS = """
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, "Helvetica Neue", Arial, sans-serif;
           color: #0F172A; background: #fff; line-height: 1.65; }
    .wrap { max-width: 760px; margin: 0 auto; padding: 24px 20px 72px; }
    header.bar { border-bottom: 1px solid #E2E8F0; }
    header.bar .wrap { padding: 16px 20px; display: flex; align-items: center; gap: 10px; }
    .brand { display: flex; align-items: center; gap: 10px; text-decoration: none; color: #0F172A; font-weight: 700; }
    h1 { font-size: 30px; line-height: 1.25; margin: 28px 0 8px; }
    h2 { font-size: 19px; margin: 34px 0 10px; }
    p, li { font-size: 16px; color: #1E293B; }
    ul { padding-inline-start: 22px; }
    a { color: #0F766E; }
    .meta { color: #64748B; font-size: 14px; margin: 0 0 8px; }
    .note { background: #F1F5F9; border-radius: 12px; padding: 14px 16px; font-size: 15px; }
    footer.bar { border-top: 1px solid #E2E8F0; margin-top: 48px; }
    footer.bar .wrap { padding: 20px; color: #64748B; font-size: 14px; }
"""


def render(lang: str, doc: str, content: dict) -> str:
    """Bir belgeyi tek bir dilde HTML'e döker."""
    slug = "privacy" if doc == "privacy" else "terms"
    self_url = f"{SITE}/{lang}/{slug}"
    alts = "".join(
        f'\n  <link rel="alternate" hreflang="{code}" href="{SITE}{path}">'
        for code, path in CANONICAL[doc].items()
    )
    body = []
    for block in content["blocks"]:
        kind = block["t"]
        if kind == "h2":
            body.append(f'      <h2>{block["v"]}</h2>')
        elif kind == "p":
            body.append(f'      <p>{block["v"]}</p>')
        elif kind == "note":
            body.append(f'      <p class="note">{block["v"]}</p>')
        elif kind == "ul":
            items = "".join(f"\n        <li>{i}</li>" for i in block["v"])
            body.append(f"      <ul>{items}\n      </ul>")
        else:
            raise SystemExit(f"bilinmeyen blok türü: {kind}")

    direction = ' dir="rtl"' if lang in RTL else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}"{direction}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{content["title"]} — Dozify</title>
  <meta name="description" content="{content["description"]}">
  <link rel="canonical" href="{self_url}">
  <link rel="alternate" hreflang="{lang}" href="{self_url}">{alts}
  <link rel="alternate" hreflang="x-default" href="{SITE}{CANONICAL[doc]["en"]}">
  <meta name="robots" content="index, follow">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>{PAGE_CSS}  </style>
</head>
<body>
  <header class="bar">
    <div class="wrap">
      <a class="brand" href="{SITE}/en">
        <svg width="26" height="26" viewBox="0 0 32 32" fill="none" aria-hidden="true">
          <rect width="32" height="32" rx="8" fill="#0D9488" />
          <path fill="#fff" fill-rule="evenodd" d="M8.5 6.5 H16 A9.5 9.5 0 0 1 16 25.5 H8.5 Z M13.5 11.5 H16 A4.5 4.5 0 0 1 16 20.5 H13.5 Z" />
          <path fill="#fff" d="M16.2 11.8 C 17.6 14, 18.6 15.4, 18.6 17.2 A 2.4 2.4 0 1 1 13.8 17.2 C 13.8 15.4, 14.8 14, 16.2 11.8 Z" />
        </svg>
        <span>Dozify</span>
      </a>
    </div>
  </header>

  <main class="wrap">
      <h1>{content["title"]}</h1>
      <p class="meta">{content["updated"]}</p>
{chr(10).join(body)}
  </main>

  <footer class="bar">
    <div class="wrap">
      <p>© 2026 Erimworks · <a href="mailto:privacy@dozify.app">privacy@dozify.app</a> · <a href="mailto:support@dozify.app">support@dozify.app</a></p>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    src = json.loads((ROOT / "tools" / "legal-content.json").read_text(encoding="utf-8"))
    written = []
    for lang, docs in src.items():
        for doc, content in docs.items():
            slug = "privacy" if doc == "privacy" else "terms"
            out = ROOT / lang / f"{slug}.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render(lang, doc, content), encoding="utf-8")
            written.append(f"{lang}/{slug}.html")
    print(f"{len(written)} hukuki sayfa üretildi")
    for w in written:
        print(f"  {w}")


if __name__ == "__main__":
    sys.exit(main())
