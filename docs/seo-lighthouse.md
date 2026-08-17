# Faz 6 — Lighthouse ve erişilebilirlik raporu

**Ölçüm koşulları:** Lighthouse 13.4.1, headless Chrome, yerel statik sunucu
(`python3 -m http.server`, sıkıştırma ve CDN yok — canlıda Vercel'in brotli'si
devrede, yani gerçek rakamlar buradakinden iyi). Mobil koşu Lighthouse'un
varsayılan kısıtlaması (Moto G Power benzeri CPU 4x yavaşlatma, yavaş 4G);
masaüstü koşu `--preset=desktop`. 18 Ağustos 2026.

## Sonuçlar

| Sayfa | Performans | Erişilebilirlik | En İyi Uygulamalar | SEO | LCP | CLS |
|---|---|---|---|---|---|---|
| `/en` (masaüstü) | 100 | 100 | 100 | 100 | 0,3 sn | 0 |
| `/en` (mobil) | 100 | 100 | 100 | 100 | 1,8 sn | 0 |
| `/tr` (mobil) | 99 | 100 | 100 | 100 | 2,1 sn | 0 |
| `/en/glp1-shot-tracker` | 100 | 100 | 100 | 100 | 1,1 sn | 0 |
| `/en/switch-glp1-tracker-app` | 100 | 100 | 100 | 100 | 1,1 sn | 0 |
| `/en/articles/what-is-glp1` | 100 | 100 | 100 | 100 | 1,1 sn | 0 |
| `/tr/makaleler/glp1-yan-etkileri` | 100 | 100 | 100 | 100 | 1,1 sn | 0 |
| `/en/support` · `/tr/destek` | 100 | 100 | 100 | 100 | 1,1 sn | 0 |
| `/en/why` · `/tr/kvkk` · `/en/editorial-policy` | 100 | 100 | 100 | 100 | 1,1 sn | 0 |

Dört kategoride hedef 90'dı; tek istisna Türkçe ana sayfanın 99 performansı ve
o da ölçüm gürültüsü aralığında (aynı sayfa İngilizcesiyle bayt bayt aynı
yapıda).

## Ölçüm sırasında bulunup düzeltilenler

| Sorun | Neydi | Ne yapıldı |
|---|---|---|
| `<html lang>` ziyaretçiye göre eziliyordu | `lang.js`, saat dilimine ve tarayıcı diline bakıp `documentElement.lang`'i değiştiriyordu. Diller ayrı URL'lere taşındıktan sonra bu, Türkiye'den `/en/…` okuyan birine `lang="tr"` yazmak demekti — ve sayfayı render eden tarayıcı da aynısını görüyordu | Script tamamen kaldırıldı; dili artık yalnızca URL belirliyor |
| Bağlantılar metinden yalnızca renkle ayrılıyordu | Gövde metnine karşı fark 1,15–1,38:1. Renk göremeyen okuyucu için bağlantı görünmez | Altı çizgi varsayılan hâle getirildi; menü, altbilgi, düğme ve kart gibi kendi başına duran bağlantılarda kapatıldı |
| Birincil düğme metni | Beyaz yazı `#0D9488` üstünde 3,74:1; 15px normal metin için eşik 4,5:1 | Zemin `--teal-700`'e alındı (5,47:1); hover bir ton daha koyu |
| Künye ve altbilgi metni | `--slate-400` (#94A3B8) beyaz üstünde 2,56:1 — üstelik künye, E-E-A-T için yeni eklenen satırdı | `--slate-500`'e alındı (4,76:1) |
| `.back-link` | 14px metin, teal-600, 3,74:1 | teal-700 |
| Başlık sırası | Altbilgi başlıkları `<h4>`, sayfadaki son başlık `<h2>` — seviye atlanıyordu | Altbilgi başlıkları `<h3>` |
| Odak görünürlüğü | Yalnızca ekran görüntüsü şeridinde odak halkası vardı | Global `:focus-visible` halkası |
| Azaltılmış hareket | Kart ve düğme geçişleri her koşulda çalışıyordu | `prefers-reduced-motion: reduce` bloğu |

## Görseller

- **Dil ayrımı:** Türkçe sayfa yalnızca `screenshots/tr/`, İngilizce sayfa
  yalnızca `screenshots/en/` yüklüyor. (Bu, dil ayrımıyla birlikte gelmişti;
  öncesinde her ziyaretçi iki dilin görsellerini de indirip birini görüyordu.)
- **LCP adayı tek:** Hero ekranı `fetchpriority="high"`, diğer bütün görseller
  `loading="lazy"`.
- **`srcset`:** Telefon çerçevesi 280–300 CSS piksel. 750w dosya 2x ekran için
  doğru, 1x için iki buçuk kat fazlaydı; her görselin 400w varyantı üretildi ve
  `sizes="(min-width: 900px) 300px, 72vw"` ile sunuluyor.
- **Dosya adları:** `01-home.webp` → `home-next-dose.webp`,
  `02-injection.webp` → `log-injection-site-map.webp` ve benzeri; sekiz
  görselin tamamı içeriğini söyleyen adlara geçti.
- **`width`/`height`:** Hepsinde duruyor — CLS her sayfada 0.
- **Alt metinleri:** 36 görselin tamamında var, hepsi ekranda ne olduğunu
  anlatıyor; anahtar kelime doldurulmadı.

## Yapılmayanlar

- **Font optimizasyonu gerekmedi:** site sistem font yığınını kullanıyor, tek
  bir web fontu indirilmiyor.
- **Kullanılmayan CSS/JS ayıklaması gerekmedi:** `lang.js` kaldırıldıktan sonra
  sitede hiç JavaScript kalmadı; CSS tek dosya ve 20 KB'ın altında.
- **Canlı ölçüm henüz yok:** Bu rakamlar yerel sunucudan. Search Console'un
  Core Web Vitals raporu gerçek kullanıcı verisiyle dolduğunda (28 günlük
  pencere) tekrar bakılmalı.
