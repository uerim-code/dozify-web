# Faz 7.1 — ölçüm planı

Kural, her şeyden önce: **sağlık verisi ölçüme girmez.** URL'de, olay adında,
olay parametresinde ya da herhangi bir analytics yükünde ilaç adı, belirti,
kilo, doz ya da enjeksiyon tarihi bulunmaz. Bu, uygulamanın gizlilik vaadinin
uzantısı; siteye analytics eklemenin kendisi de bu vaade uymak zorunda.

## Ne kurulu, ne kurulacak

| Araç | Durum | Not |
|---|---|---|
| Google Search Console | **kurulu** — `dozify.app` domain property (sc-domain), Google doğrulama TXT kaydı Namecheap'te duruyor | Vercel'e taşınırken TXT'ye dokunulmadı |
| Sitemap gönderimi | **yapıldı** (18 Ağu 2026) — 42 URL, GSC aynı gün okudu | Domain property'de "sitemap.xml" reddediliyor; tam URL gerekiyor: `https://dozify.app/sitemap.xml` |
| URL denetimi ile yeniden indeksleme | **kısmen** — 3 URL geçti, gerisi günlük kotaya takıldı | Aşağıdaki listeye bak; kota hesap başına ve günlük |
| Bing Webmaster Tools | **kurulacak** | GSC'den içe aktarma ile; ayrı doğrulama gerekmez |
| Core Web Vitals | GSC'nin kendi raporu | Gerçek kullanıcı verisi 28 günlük pencerede birikir; laboratuvar ölçümü `docs/seo-lighthouse.md`'de |
| App Store tıklaması | **kurulu** — Apple kampanya jetonu | Aşağıda |

## App Store tıklamasını sayfa bazında ölçmek

Sitedeki her App Store bağlantısı kendi kampanya jetonunu taşıyor:
`…/id6764325653?ct=web-<sayfa>-<dil>`. Örnekler:

- `web-home-en`, `web-home-tr`
- `web-glp1-shot-tracker-en`, `web-glp1-igne-takibi` yerine `web-glp1-shot-tracker-tr`
  (jeton İngilizce slug + dil; iki dilin aynı sayfası tek satırda karşılaştırılabilsin)
- `web-switch-glp1-tracker-app-en` — veri aktarımı sayfasından gelen kurulumlar
- `web-articles-glp1-injection-sites-en` — makaleden gelen kurulumlar

Bunlar **App Store Connect → App Analytics → Kaynaklar → Kampanyalar** altında
görünür. Sayfada hiçbir script çalışmıyor, ziyaretçiye dair hiçbir şey
gönderilmiyor, takip izni reddedilmişken de çalışıyor — sayım Apple tarafında,
kampanya jetonuna göre yapılıyor.

Bu, "organik ziyaret → App Store tıklaması" oranını da verir: GSC'nin sayfa
bazlı tıklaması bölünen, ASC'nin kampanya bazlı ürün sayfası görüntülemesi
bölen.

## Site tarafında analytics

Şu an sitede **hiç JavaScript yok** (`lang.js` Faz 6'da kaldırıldı). Ölçüm
ihtiyacı GSC + ASC kampanya jetonlarıyla karşılanıyor ve bu ikisi hiçbir
ziyaretçi verisi toplamıyor.

Sayfa içi olay ölçümü (dil değiştirme tıklaması, makale okuma derinliği) gerçekten
gerekirse, uyulacak koşullar:

- Çerezsiz ve parmak izi çıkarmayan bir sağlayıcı (Vercel Web Analytics ya da
  Plausible tarzı), ziyaretçi başına kalıcı kimlik üretmeyen.
- Olay adları sabit ve genel: `lang_switch`, `store_click`. Parametre olarak
  yalnızca sayfa yolu ve dil.
- Sayfa yolu zaten sağlık verisi taşımıyor — URL'lerde ilaç adı yok, kişiye
  özel bir tanımlayıcı yok. Bu bilerek böyle; yeni sayfa açarken de böyle
  kalmalı.
- Eklenirse gizlilik politikasına yazılır. Politika neyin toplandığını
  sayıyor; sayfaya sessizce script eklemek o metni yanlış hâle getirir.

## Haftalık rapor

GSC + ASC'den, her pazartesi:

| Gösterge | Kaynak | Neye bakılıyor |
|---|---|---|
| Gösterim, tıklama, CTR, ortalama konum | GSC → Performans | Toplam ve dil kırılımında (`/en/*` ve `/tr/*` ayrı filtre) |
| Ülke ve cihaz kırılımı | GSC → Performans | Türkçe sayfaların Türkiye dışından ne kadar gösterim aldığı hreflang'ın işleyip işlemediğini söyler |
| En hızlı yükselen/düşen sorgular | GSC → Performans, 28 gün karşılaştırma | Enjeksiyon-bölgesi kümesi hâlâ ana marka-dışı kaynak |
| İndeksleme hataları | GSC → Sayfalar | Keşfedilen ama indekslenmeyen sayısı; 42 URL'nin kaçı dizinde |
| Core Web Vitals | GSC → Deneyim | Alan verisi; laboratuvar rakamı değil |
| Sayfa bazında App Store tıklaması | ASC → App Analytics → Kampanyalar | Hangi landing page kurulum getiriyor |
| Organik → App Store oranı | GSC tıklama ÷ ASC ürün sayfası görüntülemesi | Sayfa bazında |

## Yayın sonrası — 18 Ağustos 2026'da yapılanlar

1. ✅ `https://dozify.app/sitemap.xml` gönderildi. GSC aynı gün okudu:
   **42 keşfedilen sayfa** (önceki gönderim 5 sayfa görüyordu).
2. ✅ `python3 tools/seo-gate.py --live` temiz — 42 sitemap URL'si ve bütün
   hukuki bağlantılar 200.
3. **19 Ağu 2026 — yedi URL daha elle indekslemeye verildi**, kota bugün
   dolmadı: `/tr/yayin-ilkeleri`, `/en/articles/missed-glp1-dose`,
   `/tr/makaleler/kacirilan-glp1-dozu`, `/en/articles/storing-glp1-pens`,
   `/tr/makaleler/glp1-kalemi-saklama`, `/en/articles/injection-site-lumps`,
   `/tr/makaleler/enjeksiyon-bolgesi-sertlesme`. Kota günlük ve değişken
   görünüyor — 18 Ağu'da dördüncüde durmuştu (o gün sitemap de gönderilmişti),
   19 Ağu'da yedisi de geçti.

   Hâlâ bekleyen: `/en/articles/glp1-appointment-checklist` +
   `/tr/makaleler/randevu-kontrol-listesi` ve sekiz landing page'in iki dili.
   GSC "Genel Bakış" 19 Ağu'da 9 sayfa dizinde / 6 sayfa dizin dışı diyor;
   50 URL'nin tamamı sitemap üzerinden keşfedilmiş durumda.

4. ⚠️ **18 Ağu'daki kota notu (referans için):** Üçü geçti: `/en`, `/tr`,
   `/en/editorial-policy`. Dördüncüde GSC "Kota Aşıldı — yarın tekrar deneyin"
   dedi. **Günlük kota sayfa başına değil hesap başına ve düşük**; anlaşılan
   günde bir avuç istek.

   Sırada bekleyenler (öncelik sırasıyla, yarından itibaren birkaç güne
   yayılarak): `/tr/yayin-ilkeleri`, `/en/switch-glp1-tracker-app`,
   `/tr/baska-uygulamadan-gecis`, `/en/glp1-shot-tracker`,
   `/tr/glp1-igne-takibi`, sonra kalan landing page'ler.

   Bu bir engel değil: sitemap okundu ve 42 URL keşfedildi, Google kendi
   sırasında tarayacak. Elle istek yalnızca sırayı öne alıyor.
5. **20 Ağu 2026 — altı URL daha**, kota yine dolmadı:
   `/en/articles/glp1-appointment-checklist`, `/en/articles/health-app-privacy`,
   `/en/articles/measurements-vs-scale`, `/en/switch-glp1-tracker-app`,
   `/tr/baska-uygulamadan-gecis`, `/en/glp1-shot-tracker`, `/tr/glp1-igne-takibi`.

   **İyi haber, elle istekten bağımsız:** denetim sırasında üç sayfa zaten
   **"URL Google'da mevcut / Sayfa dizine eklendi"** çıktı —
   `/en/articles/glp1-appointment-checklist`, `/en/switch-glp1-tracker-app`,
   `/en/glp1-shot-tracker`. Yani Google yeni sitemap'i kendi tarıyor ve yeni
   makaleler elle istek olmadan da diziniyor. Elle istek sırayı öne alıyor,
   şart değil.

6. **21 Ağu 2026 — asıl işi site haritası yaptı, elle istek değil.**

   Bir Türkçe makaleyi denetlerken GSC "URL Google tarafından bilinmiyor" ve
   **"Yönlendiren site haritası algılanmadı"** dedi. Sayfa canlıydı (HTTP 200)
   ve canlı `sitemap.xml` içinde vardı — yani sorun sitede değildi: GSC
   haritayı en son 20 Ağu'da okumuştu ve o okumada **54 URL** vardı. Sonradan
   yayımlanan 11. ve 12. hafta makaleleri ile ikinci dil kopyaları o listeye
   hiç girmemişti.

   `https://dozify.app/sitemap.xml` yeniden gönderildi. Google **aynı anda**
   okudu: **64 keşfedilen sayfa** — sitenin tamamı. Tek bir işlem, kota
   harcamadan 10 yeni URL'yi keşfettirdi.

   **Buradan çıkan kural: yeni sayfa yayımlandıktan sonra site haritasını
   yeniden gönder.** Elle URL isteği kotaya takılıyor ve günde bir avuç
   sayfa ilerliyor; harita yeniden gönderimi kotasız ve toplu.

   Elle istek: `/tr/makaleler/randevu-kontrol-listesi` ve
   `/tr/makaleler/saglik-uygulamasi-gizliligi` sıraya girdi. Üçüncüde
   "Kota Aşıldı" geldi — bugünkü kota dün ve evvelsi günden düşüktü.

   Bir istek de boşa gitti: bir önceki isteğin onay bildirimi arama kutusunu
   kapattığı için yazılan yeni URL kutuya girmemiş ve **aynı sayfa ikinci kez**
   istenmiş. GSC arayüzünde her istekten sonra bildirimi kapatıp kutuya
   yazılanın gerçekten değiştiğini görmek gerekiyor.

7. ⬜ Bing Webmaster Tools'a GSC'den içe aktarma — henüz yapılmadı. Bing'e
   giriş Ümit'in hesabıyla yapılacak bir işlem; ben oturum açamam.

## Kalan elle indeksleme ihtiyacı — düşük öncelik

64 URL'nin tamamı artık site haritasından keşfedilmiş durumda ve 20 Ağu'da
üç sayfanın elle istek olmadan dizine girdiği görüldü. Yani kalan sayfalar
için her gün kota kovalamanın getirisi düşük; Google kendi sırasında
tarıyor. Elle istek yalnızca yeni yayımlanan ve hızlı görünmesi istenen bir
sayfa için anlamlı.
