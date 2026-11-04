#!/usr/bin/env python3
"""Extra internal links that exist only on the Turkish pages.

Most Turkish guides are not indexed yet, so the pages Google does crawl point at
them. These live here rather than in the source pages on purpose: sitemap lastmod
comes from the source file's last commit, so editing a source page would claim
that the English page and all 20 translations changed too.
"""

import re

LINKS = {
    'articles/glp1-reminders-that-work': [
        ('/articles/glp1-dose-schedule', 'GLP-1 doz tablosu: her prospektüsün adımları'),
        ('/articles/wegovy-pill', 'Wegovy hap: günlük tablet nasıl alınır'),
    ],
    'articles/hydration-on-a-glp1': [
        ('/articles/protein-on-glp1', "GLP-1'de protein: ne kadar ve nasıl yetişir"),
        ('/articles/glp1-side-effects', 'Yaygın GLP-1 yan etkilerini yönetmek'),
        ('/articles/food-noise', 'Yemek gürültüsü (food noise) ve takibi'),
    ],
    'articles/injection-site-lumps': [
        ('/articles/how-to-inject-glp1', 'GLP-1 kalemi nasıl enjekte edilir: adım adım'),
        ('/articles/glp1-side-effects', 'Yaygın GLP-1 yan etkilerini yönetmek'),
    ],
    'private-glp1-tracker': [
        ('/glp1-medication-level', 'Tahmini ilaç seviyesi eğrisi'),
    ],
    'glp1-shot-tracker': [
        ('/articles/glp1-dose-schedule', 'GLP-1 doz tablosu: her prospektüsün adımları'),
        ('/articles/units-vs-milligrams', 'Birim mi, miligram mı? Tek bir dönüşüm yok'),
        ('/glp1-medication-level', 'Tahmini ilaç seviyesi eğrisi'),
        ('/articles/travelling-with-a-glp1-pen', 'GLP-1 kalemiyle uçmak: kurallar tam olarak ne diyor'),
    ],
    'glp1-vial-tracker': [
        ('/articles/units-vs-milligrams', 'Birim mi, miligram mı? Tek bir dönüşüm yok'),
    ],
    'glp1-appointment-report': [
        ('/articles/side-effect-diary-that-helps', 'Doktorunuzun gerçekten kullanabileceği bir yan etki günlüğü'),
        ('/articles/reading-a-weight-trend', 'Tartı durduğunda kilo trendini okumak'),
        ('/articles/measurements-vs-scale', 'Mezura kımıldarken tartı kımıldamadığında'),
    ],
    'glp1-side-effect-journal': [
        ('/articles/food-noise', 'Yemek gürültüsü (food noise) ve takibi'),
        ('/articles/glp1-appointment-checklist', 'GLP-1 kontrol randevusu için kontrol listesi'),
    ],
    'glp1-weight-tracker': [
        ('/articles/protein-on-glp1', "GLP-1'de protein: ne kadar ve nasıl yetişir"),
    ],
    'why': [
        ('/articles/what-is-glp1', 'GLP-1 nedir? Hormon, açılımı ve nasıl çalıştığı'),
        ('/articles/health-app-privacy', 'Bir sağlık uygulaması reçetenizi görmeden önce neye bakmalı'),
    ],
    'shotsy-alternative': [
        ('/glapp-alternative', 'Glapp alternatifi'),
    ],
    'glucopal-alternative': [
        ('/glapp-alternative', 'Glapp alternatifi'),
    ],
}

HOME_CARDS = [
    ('/articles/glp1-dose-schedule', 'GLP-1 doz tablosu: her prospektüsün adımları',
     'Semaglutid ve tirzepatid doz artış adımları ABD prospektüsünde yazdığı gibi, kaynağıyla. Plan değil; kararı hekiminiz verir.'),
    ('/articles/wegovy-pill', 'Wegovy hap: günlük tablet nasıl alınır',
     'Aç karnına, az suyla, yemekten önce bekleyerek — prospektüs ne diyor; kaçırılan doz, saklama ve kalemden geçiş.'),
    ('/articles/protein-on-glp1', "GLP-1'de protein: ne kadar ve nasıl yetişir",
     '1,2–1,6 g/kg rakamı nereden geliyor, hangi kiloyla hesaplanır ve iştah azken hedefe yiyecekle nasıl ulaşılır.'),
    ('/articles/food-noise', 'Yemek gürültüsü (food noise) ve takibi',
     'Araştırmacıların food noise ile kastettiği, bazı kişilerin hafta içinde fark ettiği değişim ve dozlarınızın yanında nasıl kaydedileceği.'),
]


def _list(items, indent):
    return "".join(f'\n{indent}<li><a href="{href}">{text}</a></li>' for href, text in items)


def add(html, en_slug):
    """Add this page's links to its Turkish HTML, before links are rewritten."""
    if en_slug == "":
        cards = "".join(
            f'          <a class="article-card" href="{href}">\n'
            f"            <h3>{title}</h3>\n            <p>{text}</p>\n          </a>\n"
            for href, title, text in HOME_CARDS)
        return html.replace('          <a class="article-card" href="/articles">',
                            cards + '          <a class="article-card" href="/articles">', 1)
    items = LINKS.get(en_slug)
    if not items:
        return html
    if en_slug.startswith("articles/"):
        block = '\n        <h2>İlgili yazılar</h2>\n        <ul>' + _list(items, " " * 10) + "\n        </ul>"
        return re.sub(r'(?=\s*</div>\s*<div class="article-cta">)', lambda _: block, html, count=1)
    links = ", ".join(f'<a href="{href}">{text}</a>' for href, text in items)
    para = f"    <p>Şunlara da bakın: {links}.</p>\n"
    # The first .meta sits under the page title; the one that matters closes the page.
    meta = html.rfind('    <p class="meta">')
    cta = html.rfind('    <p style="text-align:center')
    at = meta if meta > len(html) * 0.5 else cta
    if at > 0:
        return html[:at] + para + html[at:]
    raise SystemExit(f"tr_links: no place for links on {en_slug}")
