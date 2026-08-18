# Faz 7.1 — ölçüm planı

Kural, her şeyden önce: **sağlık verisi ölçüme girmez.** URL'de, olay adında,
olay parametresinde ya da herhangi bir analytics yükünde ilaç adı, belirti,
kilo, doz ya da enjeksiyon tarihi bulunmaz. Bu, uygulamanın gizlilik vaadinin
uzantısı; siteye analytics eklemenin kendisi de bu vaade uymak zorunda.

## Ne kurulu, ne kurulacak

| Araç | Durum | Not |
|---|---|---|
| Google Search Console | **kurulu** — `dozify.app` domain property (sc-domain), Google doğrulama TXT kaydı Namecheap'te duruyor | Vercel'e taşınırken TXT'ye dokunulmadı |
| Sitemap gönderimi | **yapılacak** — yeni `sitemap.xml` 42 URL, eskisi 20 | Domain property'de "sitemap.xml" reddediliyor; tam URL gerekiyor: `https://dozify.app/sitemap.xml` |
| URL denetimi ile yeniden indeksleme | **yapılacak** — yayından sonra | Ardışık hızlı gönderim geçici "Bir sorun oluştu" veriyor; ~20-30 sn arayla |
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
3. ⚠️ **Elle indeksleme kotası doldu.** Üçü geçti: `/en`, `/tr`,
   `/en/editorial-policy`. Dördüncüde GSC "Kota Aşıldı — yarın tekrar deneyin"
   dedi. **Günlük kota sayfa başına değil hesap başına ve düşük**; anlaşılan
   günde bir avuç istek.

   Sırada bekleyenler (öncelik sırasıyla, yarından itibaren birkaç güne
   yayılarak): `/tr/yayin-ilkeleri`, `/en/switch-glp1-tracker-app`,
   `/tr/baska-uygulamadan-gecis`, `/en/glp1-shot-tracker`,
   `/tr/glp1-igne-takibi`, sonra kalan landing page'ler.

   Bu bir engel değil: sitemap okundu ve 42 URL keşfedildi, Google kendi
   sırasında tarayacak. Elle istek yalnızca sırayı öne alıyor.
4. ⬜ Bing Webmaster Tools'a GSC'den içe aktarma — henüz yapılmadı.
