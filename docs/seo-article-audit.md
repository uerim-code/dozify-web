# Faz 4.2 — sağlık makalesi denetimi

18 Ağustos 2026'da beş makalenin tamamı; her kaynak bağlantısı tek tek açıldı.
Tarihler sayfaların kendisinden, kaynak durumu canlı HTTP kontrolünden geliyor.

| URL | Son güncelleme | Ana sorgu | Kaynak durumu | Riskli iddia | Yapılan düzeltme |
|---|---|---|---|---|---|
| `/en/articles/what-is-glp1` · `/tr/makaleler/glp1-nedir` | 14 Ağu 2026 | what is glp-1 / glp1 nedir | 7 kaynak, hepsi 200 (MedlinePlus ×3, Cleveland Clinic, NIDDK, FDA) | Yok. Hormon ile ilaç sınıfı ilk paragrafta ayrılmış, doz veya sonuç iddiası yok | Yazar adı + üç tarih eklendi; CTA artık App Store'un yanında doz takibi sayfasına da gidiyor |
| `/en/articles/how-to-inject-glp1` · `/tr/makaleler/glp1-nasil-yapilir` | 29 Haz 2026 | how to inject glp-1 / glp1 iğnesi nasıl yapılır | Üretici talimatları + MedlinePlus deri altı enjeksiyon sayfası, hepsi 200 | Yok. Adımlar "üretici talimatına göre" çerçevesinde, iğne uzunluğu/açısı reçete gibi verilmiyor | Yazar adı + üç tarih; iğne takibi sayfasına bağlantı |
| `/en/articles/glp1-injection-sites` · `/tr/makaleler/glp1-enjeksiyon-bolgeleri` | 29 Haz 2026 | glp-1 injection sites / glp1 enjeksiyon bölgeleri | MedlinePlus, Cleveland Clinic, üretici talimatları — hepsi 200 | Onaylı bölge listesi mutlak ifade taşıyordu; kaynağı üretici talimatı olarak zaten adlandırılmış, iddia sınırlı | Yazar adı + üç tarih; bölge rotasyonu sayfasına bağlantı |
| `/en/articles/glp1-side-effects` · `/tr/makaleler/glp1-yan-etkileri` | 24 Haz 2026 | glp-1 side effects / glp1 yan etkileri | MedlinePlus ×3, Cleveland Clinic, NIDDK — hepsi 200 | **Acil yönlendirme yalnızca 112 veriyordu.** İngilizce sayfa dünya çapında okunuyor; okuyucunun arayacağı numara yazmıyordu | Acil numara yerelleştirildi: ABD/Kanada 911, BK 999 veya 112, AB ve Türkiye 112. Kutulu uyarı (MTC/MEN 2) zaten kaynaklıydı, dokunulmadı |
| `/en/articles/glp1-patches` · `/tr/makaleler/glp1-bantlari` | 14 Ağu 2026 | glp-1 patches / glp1 bantları | **Düzeltildi.** Önce GoodRx ve Drugs.com vardı — ticari siteler, düzenleyici bir olgu için | "FDA veya EMA onaylı bant yok" iddiası ticari kaynağa dayanıyordu | Kaynaklar Drugs@FDA, FDA'nın onaysız GLP-1 ürünleri bildirimi ve EMA ilaç kaydı ile değiştirildi; ikisi de artık 200 |

## Denetim ölçütleri ve sonuç

- **Ana soru ilk paragrafta cevaplanıyor mu?** Beşinde de evet; `article-lede`
  sorunun düz cevabını veriyor.
- **Tıbbi iddialar kaynakla eşleşiyor mu?** Patches makalesi hariç evet; o da
  düzeltildi.
- **Kaynaksız kesin ifade kaldı mı?** Hayır. Kalan mutlak ifadeler (onaylı
  bölgeler, kutulu uyarı) doğrudan üretici talimatına ve FDA'ya dayanıyor.
- **Marka isimleri bağlama uygun mu?** Ozempic® ve diğerleri yalnızca ilaç
  sınıfı anlatılırken, ® ve sahiplik uyarısıyla geçiyor.
- **Acil yönlendirme doğru mu?** Şimdi evet — yalnızca acil belirti anlatan
  makalede var, orada da okuyucunun bulunduğu yere göre.
- **Uygulama tıbbi çözüm gibi konumlanıyor mu?** Hayır; her makalenin altındaki
  uyarı "takip aracı, tıbbi cihaz değil" diyor ve CTA takip özelliğine gidiyor.
- **Takip özelliğine doğal CTA var mı?** Şimdi var: her makalenin CTA'sı hem
  App Store'a hem konusunun karşılığı olan ürün sayfasına bağlanıyor.
- **Okunabilirlik?** Kısa paragraf, açıklayıcı ara başlık ve liste kullanımı
  zaten yerindeydi; değiştirilmedi.

## Yapılmayan ve neden

- **Klinisyen incelemesi yok.** Yayın ilkeleri bunu açıkça yazıyor; "doctor
  reviewed" ya da benzeri bir ifade hiçbir sayfada yok ve schema'da
  `reviewedBy` bilerek boş bırakıldı. Gerçek bir hekim incelerse, incelediği
  makalede adıyla ve tarihiyle yazılacak.
- **Yeni tıbbi içerik yazılmadı.** Bu faz mevcut beş makalenin denetimiydi;
  yeni konular Faz 5.2'deki takvimde.
