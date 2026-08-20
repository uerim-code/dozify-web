"""Per-language title and description for every page.

Written per language rather than translated. A Turkish user searching for
"glp1 iğne takibi" does not type the words a translation of the English title
would produce, and the title is the line they decide on in the results page.

Lengths are aimed at what a result actually shows: roughly 45–60 for a title
and 140–160 for a description. Longer is not more information, it is a
sentence cut off mid-word.
"""

# What each page is for, and the query it is written to answer. This is here
# rather than in a document because it is what keeps two pages from being
# written against the same query: "glp1 shot tracker" and "glp1 injection sites"
# look similar and are not, and the moment two pages chase one query they split
# their own signal. INTENT[slug][lang] = (intent, primary query).
INTENT: dict[str, dict[str, tuple[str, str]]] = {
    "":                             {"en": ("app search", "glp-1 tracker app"),
                                     "tr": ("uygulama arayışı", "glp1 takip uygulaması")},
    "glp1-shot-tracker":            {"en": ("app search", "glp-1 shot tracker"),
                                     "tr": ("uygulama arayışı", "glp1 iğne takip uygulaması")},
    "injection-site-tracker":       {"en": ("app search", "injection site tracker app"),
                                     "tr": ("uygulama arayışı", "enjeksiyon bölgesi takibi")},
    "glp1-weight-tracker":          {"en": ("app search", "glp-1 weight tracker"),
                                     "tr": ("uygulama arayışı", "glp1 kilo takibi")},
    "glp1-side-effect-journal":     {"en": ("app search", "glp-1 side effect tracker"),
                                     "tr": ("uygulama arayışı", "glp1 yan etki günlüğü")},
    "glp1-vial-tracker":            {"en": ("app search", "glp-1 vial tracker"),
                                     "tr": ("uygulama arayışı", "glp1 flakon takibi")},
    "private-glp1-tracker":         {"en": ("app search", "private glp-1 tracker no account"),
                                     "tr": ("uygulama arayışı", "gizli glp1 takip uygulaması")},
    "glp1-appointment-report":      {"en": ("app search", "glp-1 doctor report pdf"),
                                     "tr": ("uygulama arayışı", "glp1 doktor raporu pdf")},
    "switch-glp1-tracker-app":      {"en": ("switching", "shotsy alternative import data"),
                                     "tr": ("uygulama değiştirme", "shotsy yerine glp1 uygulaması")},
    "why":                          {"en": ("evaluation", "why dozify"),
                                     "tr": ("değerlendirme", "neden dozify")},
    "editorial-policy":             {"en": ("trust", "who writes dozify health content"),
                                     "tr": ("güven", "dozify sağlık içeriklerini kim yazıyor")},
    "support":                      {"en": ("support", "dozify support"),
                                     "tr": ("destek", "dozify destek")},
    "privacy":                      {"en": ("legal", "dozify privacy policy"),
                                     "tr": ("hukuki", "dozify gizlilik politikası")},
    "terms":                        {"en": ("legal", "dozify terms of service"),
                                     "tr": ("hukuki", "dozify kullanım koşulları")},
    "kvkk":                         {"en": ("legal", "dozify kvkk notice"),
                                     "tr": ("hukuki", "dozify kvkk aydınlatma metni")},
    "articles":                     {"en": ("information hub", "glp-1 guides"),
                                     "tr": ("bilgi merkezi", "glp1 rehberleri")},
    "articles/what-is-glp1":        {"en": ("information", "what is glp-1"),
                                     "tr": ("bilgi", "glp1 nedir")},
    "articles/how-to-inject-glp1":  {"en": ("information", "how to inject glp-1"),
                                     "tr": ("bilgi", "glp1 iğnesi nasıl yapılır")},
    "articles/glp1-injection-sites": {"en": ("information", "glp-1 injection sites"),
                                     "tr": ("bilgi", "glp1 enjeksiyon bölgeleri")},
    "articles/glp1-side-effects":   {"en": ("information", "glp-1 side effects"),
                                     "tr": ("bilgi", "glp1 yan etkileri")},
    "articles/glp1-patches":        {"en": ("information", "glp-1 patches"),
                                     "tr": ("bilgi", "glp1 bantları")},
    "articles/missed-glp1-dose":    {"en": ("information, urgent", "missed glp-1 dose what to do"),
                                     "tr": ("bilgi, acil", "glp1 dozunu kaçırdım ne yapmalıyım")},
    "articles/storing-glp1-pens":   {"en": ("information", "how to store ozempic pen fridge"),
                                     "tr": ("bilgi", "ozempic kalemi nasıl saklanır")},
    "articles/glp1-appointment-checklist": {"en": ("preparation", "what to ask doctor glp-1 follow up"),
                                     "tr": ("hazırlık", "glp1 kontrol randevusunda ne sorulur")},
    "articles/injection-site-lumps": {"en": ("information, concern", "lump at glp-1 injection site"),
                                     "tr": ("bilgi, endişe", "enjeksiyon yerinde sertlik")},
    "articles/glp1-reminders-that-work": {"en": ("troubleshooting", "change glp-1 injection day reminder"),
                                     "tr": ("sorun giderme", "glp1 iğne günü değiştirme hatırlatıcı")},
    "articles/reading-a-weight-trend": {"en": ("information", "glp-1 weight loss plateau trend"),
                                     "tr": ("bilgi", "glp1 kilo vermeme dönemi trend")},
    "articles/side-effect-diary-that-helps": {"en": ("information", "how to track glp-1 side effects for doctor"),
                                     "tr": ("bilgi", "yan etkileri doktora nasıl anlatmalı")},
}

# slug (english) -> {lang: (title, description)}
META: dict[str, dict[str, tuple[str, str]]] = {
    "": {
        "en": ("GLP-1 Tracker for Shots, Weight & Side Effects",
               "Track GLP-1 injections, rotate sites, log weight and side effects, and export a PDF for your doctor. No account, works offline, iPhone."),
        "tr": ("GLP-1 Takip Uygulaması — İğne, Kilo, Yan Etki",
               "GLP-1 iğnelerini kaydet, bölge değiştir, kilo ve yan etki tut, doktorun için PDF rapor çıkar. Hesap yok, çevrimdışı çalışır, iPhone."),
    },
    "glp1-shot-tracker": {
        "en": ("GLP-1 Shot Tracker — Never Miss Injection Day",
               "A weekly shot needs a weekly reminder. Dozify shows the next dose on the first screen, logs each one, and keeps the history you can look back at."),
        "tr": ("GLP-1 İğne Takibi — Doz Gününü Bir Daha Kaçırma",
               "Haftalık ilaç, haftalık hatırlatma ister. Dozify sıradaki dozu ilk ekranda gösterir, her iğneyi kaydeder ve geriye dönüp bakabileceğin bir geçmiş tutar."),
    },
    "injection-site-tracker": {
        "en": ("Injection Site Tracker — Rotate Without Notes",
               "The body map remembers which site is next, so you do not keep notes. Log where each GLP-1 injection went and see the rotation at a glance."),
        "tr": ("Enjeksiyon Bölgesi Takibi — Not Tutmadan Rotasyon",
               "Sıradaki bölgeyi vücut haritası hatırlar, sen not tutmazsın. Her GLP-1 enjeksiyonunun nereye yapıldığını kaydet, rotasyonu tek bakışta gör."),
    },
    "glp1-weight-tracker": {
        "en": ("GLP-1 Weight Tracker — Weight and Dose Together",
               "Your weight trend next to the doses that produced it, on one timeline. Log weight in seconds and see the shape of months, not single numbers."),
        "tr": ("GLP-1 Kilo Takibi — Kilo ve Doz Aynı Çizgide",
               "Kilo trendin, onu oluşturan dozların yanında, tek bir zaman çizelgesinde. Kiloyu saniyeler içinde gir, tek sayıları değil ayların şeklini gör."),
    },
    "glp1-side-effect-journal": {
        "en": ("GLP-1 Side-Effect Journal — See When They Happen",
               "Telling your doctor \"I had nausea\" is not the same as \"15 hours after the dose\". Log symptoms with severity and see them against your injections."),
        "tr": ("GLP-1 Yan Etki Günlüğü — Ne Zaman Olduğunu Gör",
               "Doktora \"bulantı vardı\" demekle \"dozdan 15 saat sonra\" demek aynı şey değil. Belirtileri şiddetiyle kaydet, enjeksiyonlarınla birlikte gör."),
    },
    "glp1-vial-tracker": {
        "en": ("GLP-1 Vial Tracker — Know Before It Runs Out",
               "Doses left, days since opening and the expiry date on one card. Both ways a vial ends are predictable weeks ahead; Dozify counts them for you."),
        "tr": ("GLP-1 Flakon Takibi — Bitmeden Haberin Olsun",
               "Kalan doz, açılıştan bu yana geçen gün ve son kullanma tarihi tek kartta. Flakonun bitişi haftalar öncesinden bellidir; Dozify senin yerine sayar."),
    },
    "private-glp1-tracker": {
        "en": ("Private GLP-1 Tracker — No Account, No Cloud",
               "Your doses, weight and symptoms stay on your phone. No sign-up, no sync, no in-app ads. Delete the app and the records go with it."),
        "tr": ("Gizli GLP-1 Takibi — Hesap Yok, Bulut Yok",
               "Dozların, kilon ve belirtilerin telefonunda kalır. Kayıt yok, senkron yok, uygulama içinde reklam yok. Uygulamayı silersen kayıtlar da gider."),
    },
    "glp1-appointment-report": {
        "en": ("GLP-1 Doctor Report — Walk In With a Summary",
               "Ten minutes to explain three months. Pick a date range and what to include, and Dozify builds a clean PDF of doses, weight and side effects."),
        "tr": ("GLP-1 Doktor Raporu — Randevuya Özetle Git",
               "Üç ayı anlatmak için on dakika. Tarih aralığını ve içeriği seç; Dozify dozları, kiloyu ve yan etkileri temiz bir PDF hâline getirsin."),
    },
    "switch-glp1-tracker-app": {
        "en": ("Switch to Dozify — Import Your GLP-1 History",
               "Import from Shotsy, Glapp, GLPzy, GlucoPal or a plain CSV. You see exactly what will be written before anything is, and it costs nothing."),
        "tr": ("Dozify'a Geç — GLP-1 Geçmişini Yanında Getir",
               "Shotsy, Glapp, GLPzy, GlucoPal ya da düz bir CSV dosyasından aktar. Hiçbir şey yazılmadan önce ne yazılacağını görürsün, üstelik ücretsiz."),
    },
    "why": {
        "en": ("Why Dozify — What It Does and What It Refuses To",
               "Built for people already prescribed a GLP-1. It records what you and your doctor decide; it does not suggest doses or interpret results."),
        "tr": ("Neden Dozify — Ne Yapar, Neyi Yapmayı Reddeder",
               "GLP-1 reçete edilmiş kişiler için yazıldı. Senin ve doktorunun kararını kaydeder; doz önermez, sonuç yorumlamaz, yerine geçmez. Ne yaptığı burada."),
    },
    "editorial-policy": {
        "en": ("Editorial Policy — Who Writes These Guides",
               "Who writes the guides on this site, which sources are allowed, what each date on an article means, and how to report something that is wrong."),
        "tr": ("Yayın İlkeleri — Bu Rehberleri Kim Yazıyor",
               "Bu sitedeki rehberleri kim yazıyor, hangi kaynaklara izin var, makaledeki her tarih ne anlama geliyor ve yanlış bir şeyi nasıl bildirirsiniz."),
    },
    "support": {
        "en": ("Dozify Support — Help, Contact and Subscriptions",
               "Answers about reminders, imports, backups, premium and cancelling a subscription — plus how to reach a person when the answer is not here."),
        "tr": ("Dozify Destek — Yardım, İletişim ve Abonelik",
               "Hatırlatıcılar, içe aktarma, yedekleme, premium ve abonelik iptali hakkında cevaplar — ve cevap burada yoksa bir insana nasıl ulaşacağın."),
    },
    "privacy": {
        "en": ("Dozify Privacy Policy — What Stays on Your Phone",
               "What Dozify stores on your device, the anonymous statistics it collects, what it never collects, and how to delete everything at once."),
        "tr": ("Dozify Gizlilik Politikası — Telefonunda Ne Kalır",
               "Dozify'ın cihazında ne sakladığı, topladığı anonim istatistikler, asla toplamadıkları ve tüm kayıtlarını tek seferde nasıl sileceğin."),
    },
    "terms": {
        "en": ("Dozify Terms of Service — Subscription and Use",
               "The terms for using Dozify, including the auto-renewable Premium subscription, cancellation, and the limits of what a tracking tool is."),
        "tr": ("Dozify Kullanım Koşulları — Abonelik ve Kullanım",
               "Dozify'ı kullanma koşulları: otomatik yenilenen Premium aboneliği, ücretlendirme, iptal ve bir takip aracının sınırlarının ne olduğu."),
    },
    "kvkk": {
        "en": ("Dozify KVKK Notice — Your Data Rights in Turkey",
               "The Turkish personal data protection notice for Dozify: what is processed, on what legal basis, and the rights you hold under KVKK."),
        "tr": ("Dozify KVKK Aydınlatma Metni — Haklarınız",
               "Dozify için kişisel verilerin korunması aydınlatma metni: hangi verinin işlendiği, hangi hukuki sebeple ve KVKK kapsamında haklarınızın neler olduğu."),
    },
    "articles": {
        "en": ("GLP-1 Guides — Sourced Articles for People on GLP-1s",
               "Plain guides to injection technique, side effects, storage and what the medications do, each one citing where the information came from."),
        "tr": ("GLP-1 Rehberleri — Kaynak Gösterilmiş Yazılar",
               "Enjeksiyon tekniği, yan etkiler, saklama ve ilaçların ne yaptığı üzerine sade rehberler; her biri bilginin nereden geldiğini yazıyor."),
    },
    "articles/what-is-glp1": {
        "en": ("What Is GLP-1? The Hormone and How It Works",
               "GLP-1 is a hormone your gut releases after eating. What it does, what the medications copy, and why appetite changes — with sources."),
        "tr": ("GLP-1 Nedir? Hormonun Görevi ve Nasıl Çalıştığı",
               "GLP-1, bağırsağın yemekten sonra saldığı bir hormondur. Ne yaptığı, ilaçların neyi taklit ettiği ve iştahın neden değiştiği — kaynaklarıyla."),
    },
    "articles/how-to-inject-glp1": {
        "en": ("How to Inject a GLP-1 Pen: A Step-by-Step Guide",
               "Preparing the pen, choosing a site, the injection itself and what to do afterwards — following the manufacturer instructions, with sources."),
        "tr": ("GLP-1 Kalemi Nasıl Yapılır? Adım Adım Anlatım",
               "Kalemi hazırlamak, bölge seçmek, enjeksiyonun kendisi ve sonrasında ne yapılacağı — üretici talimatlarına dayanarak, kaynaklarıyla."),
    },
    "articles/glp1-injection-sites": {
        "en": ("GLP-1 Injection Sites: Where to Inject and Rotate",
               "Abdomen, thigh and upper arm are the approved sites. Which to choose, why the exact spot must change each time, and what to avoid."),
        "tr": ("GLP-1 Enjeksiyon Bölgeleri: Nereye ve Nasıl Rotasyon",
               "Karın, uyluk ve üst kol onaylı bölgelerdir. Hangisini seçmeli, tam noktanın neden her seferinde değişmesi gerektiği ve nelerden kaçınmalı."),
    },
    "articles/glp1-side-effects": {
        "en": ("Managing Common GLP-1 Side Effects: What Helps",
               "Nausea, constipation and fatigue are the common ones. What tends to help, how long they usually last, and the signs that need a doctor."),
        "tr": ("Yaygın GLP-1 Yan Etkileri: Ne İşe Yarıyor?",
               "Bulantı, kabızlık ve yorgunluk en yaygın olanlar. Neyin yardımcı olduğu, genelde ne kadar sürdüğü ve doktor gerektiren belirtiler."),
    },
    "articles/glp1-patches": {
        "en": ("GLP-1 Patches: Do They Exist and Do They Work?",
               "No GLP-1 patch is approved by the FDA or EMA. What is sold under that name, what the evidence says, and why the question comes up."),
        "tr": ("GLP-1 Bantları: Var mı, İşe Yarıyor mu? Kanıtlar",
               "FDA veya EMA onaylı bir GLP-1 bandı yok. Bu adla satılanlar neler, kanıtlar ne diyor, bu soru neden sık soruluyor — kaynaklarıyla anlatılıyor."),
    },
    "articles/missed-glp1-dose": {
        "en": ("Missed a GLP-1 Dose? What Each Leaflet Says",
               "Five days for one product, four for another, two for a third — and for one, skip it. What each GLP-1's own instructions say about a late dose, quoted."),
        "tr": ("GLP-1 Dozunu Kaçırdım: Prospektüs Ne Diyor?",
               "Bir üründe beş gün, birinde dört, birinde iki — birinde ise atla. Her GLP-1'in geciken doz için kendi talimatının ne dediği, alıntılarıyla."),
    },
    "articles/storing-glp1-pens": {
        "en": ("Storing a GLP-1 Pen: Fridge, Counter and Days",
               "Fifty-six days for one pen and twenty-eight for another of the same medicine, and one that must never go back in the fridge. Each label, quoted."),
        "tr": ("GLP-1 Kalemi Nasıl Saklanır: Dolap ve Gün",
               "Aynı ilacın bir kaleminde 56 gün, ötekinde 28; birinde ise buzdolabına geri dönüş yok. Her etiket, alıntısıyla ve kaynağıyla."),
    },
    "articles/glp1-appointment-checklist": {
        "en": ("GLP-1 Follow-Up Appointment: A Checklist",
               "Ten minutes to cover three months. What to have ready, the questions the NIH's own patient pages suggest asking, and what a checklist cannot decide."),
        "tr": ("GLP-1 Kontrol Randevusu İçin Kontrol Listesi",
               "Üç ayı anlatmak için on dakika. Neler hazır olmalı, NIH'in hasta sayfalarının önerdiği sorular ve bir listenin karar veremeyeceği şeyler."),
    },
    "articles/injection-site-lumps": {
        "en": ("A Lump at the Injection Site: What Labels Report",
               "Injection site reactions are listed for these medicines, and 1% of the placebo group reported them too. What the labels say, and when to show someone."),
        "tr": ("Enjeksiyon Yerinde Sertlik: Etiketler Ne Diyor",
               "Bölge reaksiyonları bu ilaçların etiketinde yazılı; plasebo grubunun %1'i de bildirmiş. Etiketler ne diyor ve ne zaman birine gösterilmeli."),
    },
    "articles/glp1-reminders-that-work": {
        "en": ("Moving Your Shot Day, and Reminders That Arrive",
               "The labels answer \"can I change the day?\" in one conditional line. And a reminder that never appeared is almost always a phone setting, not the app."),
        "tr": ("İğne Gününü Kaydırmak ve Gelen Hatırlatıcılar",
               "\"Günü değiştirebilir miyim?\" sorusunu etiketler tek koşullu cümleyle cevaplıyor. Gelmeyen hatırlatıcı ise neredeyse hep telefon ayarıdır."),
    },
    "articles/reading-a-weight-trend": {
        "en": ("Reading a Weight Trend When the Scale Stalls",
               "Weight peaks early in the week and bottoms out around Friday — that is published, not anecdote. What a trend line answers, and what it deliberately cannot."),
        "tr": ("Tartı Durduğunda Kilo Trendini Okumak",
               "Kilo hafta başında en yüksek, cuma civarında en düşük — bu yayımlanmış bir bulgu. Trend çizgisi neyi cevaplar, neyi bilerek cevaplamaz."),
    },
    "articles/side-effect-diary-that-helps": {
        "en": ("A Side-Effect Diary Your Doctor Can Actually Use",
               "The NIH lists six things a doctor asks about a symptom. Most diaries record one. What to write instead, plus the field that only matters on a weekly injection."),
        "tr": ("Doktorun Kullanabileceği Bir Yan Etki Günlüğü",
               "NIH, doktorun belirti hakkında sorduğu altı şeyi sayıyor. Çoğu günlük birini kaydeder. Onun yerine ne yazılmalı ve haftalık iğneye özel alan."),
    },
}
