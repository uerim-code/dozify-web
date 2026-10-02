#!/usr/bin/env python3
"""2026-10-02: the app no longer requests App Tracking Transparency and never
collects IDFA (see dozify repo, store/ios/privacy-labels.md). This rewrites the
two places the policy promised an ATT prompt — the "data we do not collect"
bullet and the Meta SDK paragraph — in privacy.html (EN/TR) and in
tools/legal-content.json (20 languages), and bumps the policy dates.
One-off; kept for the record. Run from the repo root, then tools/build-legal.py."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "privacy.html"
JSON = ROOT / "tools" / "legal-content.json"

META_LINK = '<a href="https://www.facebook.com/privacy/policy" rel="nofollow noopener" target="_blank">{}</a>'

EN_BULLET = ("Advertising identifiers (IDFA): the App never collects them and never shows Apple's App Tracking "
             "Transparency prompt, because it does not track you")
TR_BULLET = ("Reklam tanımlayıcıları (IDFA): Uygulama bunları hiç toplamaz ve Apple'ın İzleme Şeffaflığı "
             "(App Tracking Transparency) ekranını hiç göstermez, çünkü sizi takip etmez")
EN_P = ("The App uses the <strong>Meta (Facebook) SDK</strong> for one purpose: measuring, in aggregate, whether app "
        "installs came from one of our ads. The App does <strong>not track you</strong>: it never collects your "
        "device's advertising identifier (IDFA), never shows Apple's App Tracking Transparency prompt, and advertiser "
        "tracking inside the SDK is permanently switched off. Meta receives only Apple's privacy-preserving aggregate "
        "SKAdNetwork signal and an anonymous “app opened” event. Your health data (medications, doses, "
        "injections, weight, blood glucose, side effects, notes) is <strong>never</strong> sent to Meta. See "
        + META_LINK.format("Meta's Privacy Policy") + " for details.")
TR_P = ("Uygulama, <strong>Meta (Facebook) SDK</strong>'sını tek bir amaçla kullanır: uygulama kurulumlarının bizim "
        "reklamlarımızdan gelip gelmediğini toplu olarak ölçmek. Uygulama <strong>sizi takip etmez</strong>: "
        "cihazınızın reklam tanımlayıcısını (IDFA) hiç toplamaz, Apple'ın İzleme Şeffaflığı (App Tracking "
        "Transparency) ekranını hiç göstermez ve SDK içindeki reklamveren takibi kalıcı olarak kapalıdır. Meta "
        "yalnızca Apple'ın gizliliği koruyan toplu SKAdNetwork sinyalini ve anonim bir “uygulama açıldı” "
        "olayını alır. Sağlık verileriniz (ilaçlar, dozlar, enjeksiyonlar, kilo, kan şekeri, yan etkiler, notlar) "
        "Meta'ya <strong>asla</strong> gönderilmez. Detaylar için "
        + META_LINK.format("Meta Gizlilik Politikası") + "'na bakın.")

# Plain-text versions for the 20 generated languages (legal-content.json holds no markup).
B = {
"de": "Werbekennungen (IDFA): Die App erhebt sie nie und zeigt Apples Abfrage zur App-Tracking-Transparenz nie an, weil sie dich nicht trackt",
"fr": "Identifiants publicitaires (IDFA) : l'App ne les collecte jamais et n'affiche jamais la demande d'App Tracking Transparency d'Apple, car elle ne te suit pas",
"es": "Identificadores publicitarios (IDFA): la App nunca los recopila y nunca muestra la solicitud de App Tracking Transparency de Apple, porque no te rastrea",
"it": "Identificatori pubblicitari (IDFA): l'App non li raccoglie mai e non mostra mai la richiesta di App Tracking Transparency di Apple, perché non ti traccia",
"pt": "Identificadores de publicidade (IDFA): o App nunca os recolhe e nunca mostra o pedido de App Tracking Transparency da Apple, porque não te rastreia",
"nl": "Advertentie-id's (IDFA): de App verzamelt ze nooit en toont nooit Apples App Tracking Transparency-verzoek, omdat ze je niet volgt",
"pl": "Identyfikatory reklamowe (IDFA): Aplikacja nigdy ich nie zbiera i nigdy nie wyświetla prośby App Tracking Transparency firmy Apple, ponieważ Cię nie śledzi",
"sv": "Reklam-id (IDFA): appen samlar aldrig in dem och visar aldrig Apples App Tracking Transparency-fråga, eftersom den inte spårar dig",
"da": "Reklame-id'er (IDFA): appen indsamler dem aldrig og viser aldrig Apples App Tracking Transparency-anmodning, fordi den ikke sporer dig",
"nb": "Reklame-ID-er (IDFA): appen samler dem aldri inn og viser aldri Apples App Tracking Transparency-forespørsel, fordi den ikke sporer deg",
"fi": "Mainostunnisteet (IDFA): sovellus ei koskaan kerää niitä eikä koskaan näytä Applen App Tracking Transparency -kyselyä, koska se ei seuraa sinua",
"el": "Διαφημιστικά αναγνωριστικά (IDFA): η Εφαρμογή δεν τα συλλέγει ποτέ και δεν εμφανίζει ποτέ το αίτημα App Tracking Transparency της Apple, επειδή δεν σε παρακολουθεί",
"ru": "Рекламные идентификаторы (IDFA): приложение никогда их не собирает и никогда не показывает запрос App Tracking Transparency от Apple, потому что не отслеживает вас",
"uk": "Рекламні ідентифікатори (IDFA): застосунок ніколи їх не збирає і ніколи не показує запит App Tracking Transparency від Apple, бо не відстежує вас",
"cs": "Reklamní identifikátory (IDFA): aplikace je nikdy nesbírá a nikdy nezobrazuje výzvu App Tracking Transparency od Applu, protože tě nesleduje",
"ja": "広告識別子（IDFA）：アプリはこれを一切収集せず、Appleのアプリトラッキング透明性（ATT）の許可画面も表示しません。あなたを追跡しないためです",
"ko": "광고 식별자(IDFA): 앱은 이를 절대 수집하지 않으며 Apple의 앱 추적 투명성(ATT) 요청도 표시하지 않습니다. 사용자를 추적하지 않기 때문입니다",
"zh": "广告标识符（IDFA）：应用从不收集它，也从不显示 Apple 的应用跟踪透明度（ATT）请求，因为应用不会跟踪你",
"ar": "معرّفات الإعلانات (IDFA): لا يجمعها التطبيق أبدًا ولا يعرض أبدًا طلب شفافية تتبع التطبيقات من Apple، لأنه لا يتتبعك",
"hi": "विज्ञापन पहचानकर्ता (IDFA): ऐप इन्हें कभी एकत्र नहीं करता और Apple का App Tracking Transparency अनुरोध कभी नहीं दिखाता, क्योंकि यह आपको ट्रैक नहीं करता",
}
P = {
"de": "Die App nutzt das SDK von Meta (Facebook) zu genau einem Zweck: um aggregiert zu messen, ob App-Installationen aus einer unserer Anzeigen stammen. Die App trackt dich nicht: Sie erhebt nie die Werbekennung deines Geräts (IDFA), zeigt nie Apples Abfrage zur App-Tracking-Transparenz an, und das Werbetracking im SDK ist dauerhaft abgeschaltet. Meta erhält nur Apples datenschutzfreundliches, aggregiertes SKAdNetwork-Signal und ein anonymes Ereignis „App geöffnet“. Deine Gesundheitsdaten (Medikamente, Dosen, Injektionen, Gewicht, Blutzucker, Nebenwirkungen, Notizen) werden nie an Meta gesendet.",
"fr": "L'App utilise le SDK de Meta (Facebook) dans un seul but : mesurer, de façon agrégée, si les installations proviennent de l'une de nos publicités. L'App ne te suit pas : elle ne collecte jamais l'identifiant publicitaire de ton appareil (IDFA), n'affiche jamais la demande d'App Tracking Transparency d'Apple, et le suivi publicitaire du SDK est désactivé en permanence. Meta ne reçoit que le signal agrégé SKAdNetwork d'Apple, respectueux de la vie privée, et un événement anonyme « application ouverte ». Tes données de santé (médicaments, doses, injections, poids, glycémie, effets secondaires, notes) ne sont jamais envoyées à Meta.",
"es": "La App usa el SDK de Meta (Facebook) con un único fin: medir, de forma agregada, si las instalaciones proceden de alguno de nuestros anuncios. La App no te rastrea: nunca recopila el identificador publicitario de tu dispositivo (IDFA), nunca muestra la solicitud de App Tracking Transparency de Apple y el seguimiento publicitario del SDK está desactivado de forma permanente. Meta solo recibe la señal agregada SKAdNetwork de Apple, que protege la privacidad, y un evento anónimo de «app abierta». Tus datos de salud (medicamentos, dosis, inyecciones, peso, glucosa, efectos secundarios, notas) nunca se envían a Meta.",
"it": "L'App usa l'SDK di Meta (Facebook) per un solo scopo: misurare, in forma aggregata, se le installazioni provengono da una delle nostre inserzioni. L'App non ti traccia: non raccoglie mai l'identificatore pubblicitario del dispositivo (IDFA), non mostra mai la richiesta di App Tracking Transparency di Apple e il tracciamento pubblicitario dell'SDK è disattivato in modo permanente. Meta riceve solo il segnale aggregato SKAdNetwork di Apple, rispettoso della privacy, e un evento anonimo di «app aperta». I tuoi dati sanitari (farmaci, dosi, iniezioni, peso, glicemia, effetti collaterali, note) non vengono mai inviati a Meta.",
"pt": "O App usa o SDK da Meta (Facebook) com um único objetivo: medir, de forma agregada, se as instalações vieram de um dos nossos anúncios. O App não te rastreia: nunca recolhe o identificador de publicidade do teu dispositivo (IDFA), nunca mostra o pedido de App Tracking Transparency da Apple e o rastreio publicitário do SDK está permanentemente desligado. A Meta recebe apenas o sinal agregado SKAdNetwork da Apple, que preserva a privacidade, e um evento anónimo de «app aberta». Os teus dados de saúde (medicamentos, doses, injeções, peso, glicemia, efeitos secundários, notas) nunca são enviados à Meta.",
"nl": "De App gebruikt de Meta (Facebook) SDK voor één doel: geaggregeerd meten of installaties uit een van onze advertenties komen. De App volgt je niet: ze verzamelt nooit de advertentie-id van je toestel (IDFA), toont nooit Apples App Tracking Transparency-verzoek, en adverteerderstracking in de SDK staat permanent uit. Meta ontvangt alleen Apples privacyvriendelijke, geaggregeerde SKAdNetwork-signaal en een anonieme 'app geopend'-gebeurtenis. Je gezondheidsgegevens (medicatie, doses, injecties, gewicht, bloedglucose, bijwerkingen, notities) worden nooit naar Meta gestuurd.",
"pl": "Aplikacja używa SDK Meta (Facebook) w jednym celu: aby zbiorczo mierzyć, czy instalacje pochodzą z naszych reklam. Aplikacja Cię nie śledzi: nigdy nie zbiera identyfikatora reklamowego urządzenia (IDFA), nigdy nie wyświetla prośby App Tracking Transparency firmy Apple, a śledzenie reklamowe w SDK jest na stałe wyłączone. Meta otrzymuje wyłącznie zbiorczy, chroniący prywatność sygnał SKAdNetwork od Apple oraz anonimowe zdarzenie „aplikacja otwarta”. Twoje dane zdrowotne (leki, dawki, zastrzyki, waga, glukoza, skutki uboczne, notatki) nigdy nie są wysyłane do Meta.",
"sv": "Appen använder Metas (Facebooks) SDK i ett enda syfte: att aggregerat mäta om installationer kom från någon av våra annonser. Appen spårar dig inte: den samlar aldrig in enhetens reklam-id (IDFA), visar aldrig Apples App Tracking Transparency-fråga, och annonsörsspårningen i SDK:n är permanent avstängd. Meta får bara Apples integritetsskyddande, aggregerade SKAdNetwork-signal och en anonym händelse ”appen öppnades”. Dina hälsodata (läkemedel, doser, injektioner, vikt, blodsocker, biverkningar, anteckningar) skickas aldrig till Meta.",
"da": "Appen bruger Metas (Facebooks) SDK til ét formål: at måle samlet, om installationer kom fra en af vores annoncer. Appen sporer dig ikke: den indsamler aldrig enhedens reklame-id (IDFA), viser aldrig Apples App Tracking Transparency-anmodning, og annoncørsporing i SDK'et er permanent slået fra. Meta modtager kun Apples privatlivsbeskyttende, samlede SKAdNetwork-signal og en anonym hændelse »app åbnet«. Dine sundhedsdata (medicin, doser, injektioner, vægt, blodsukker, bivirkninger, noter) sendes aldrig til Meta.",
"nb": "Appen bruker Metas (Facebooks) SDK til ett formål: å måle samlet om installasjoner kom fra en av annonsene våre. Appen sporer deg ikke: den samler aldri inn enhetens reklame-ID (IDFA), viser aldri Apples App Tracking Transparency-forespørsel, og annonsørsporing i SDK-et er permanent slått av. Meta mottar bare Apples personvernvennlige, aggregerte SKAdNetwork-signal og en anonym «app åpnet»-hendelse. Helsedataene dine (legemidler, doser, injeksjoner, vekt, blodsukker, bivirkninger, notater) sendes aldri til Meta.",
"fi": "Sovellus käyttää Metan (Facebookin) SDK:ta yhteen tarkoitukseen: mittaamaan koostetusti, tulivatko asennukset mainoksistamme. Sovellus ei seuraa sinua: se ei koskaan kerää laitteen mainostunnistetta (IDFA), ei koskaan näytä Applen App Tracking Transparency -kyselyä, ja SDK:n mainostajaseuranta on pysyvästi pois päältä. Meta saa vain Applen yksityisyyttä suojaavan, koostetun SKAdNetwork-signaalin ja anonyymin ”sovellus avattu” -tapahtuman. Terveystietojasi (lääkkeet, annokset, pistokset, paino, verensokeri, haittavaikutukset, muistiinpanot) ei koskaan lähetetä Metalle.",
"el": "Η Εφαρμογή χρησιμοποιεί το SDK της Meta (Facebook) για έναν μόνο σκοπό: να μετρά συγκεντρωτικά αν οι εγκαταστάσεις προήλθαν από κάποια διαφήμισή μας. Η Εφαρμογή δεν σε παρακολουθεί: δεν συλλέγει ποτέ το διαφημιστικό αναγνωριστικό της συσκευής σου (IDFA), δεν εμφανίζει ποτέ το αίτημα App Tracking Transparency της Apple, και η διαφημιστική παρακολούθηση στο SDK είναι μόνιμα απενεργοποιημένη. Η Meta λαμβάνει μόνο το συγκεντρωτικό σήμα SKAdNetwork της Apple που προστατεύει το απόρρητο και ένα ανώνυμο συμβάν «άνοιγμα εφαρμογής». Τα δεδομένα υγείας σου (φάρμακα, δόσεις, ενέσεις, βάρος, γλυκόζη, παρενέργειες, σημειώσεις) δεν αποστέλλονται ποτέ στη Meta.",
"ru": "Приложение использует SDK Meta (Facebook) с одной целью: агрегированно измерять, пришли ли установки из нашей рекламы. Приложение не отслеживает вас: оно никогда не собирает рекламный идентификатор устройства (IDFA), никогда не показывает запрос App Tracking Transparency от Apple, а рекламное отслеживание в SDK отключено навсегда. Meta получает только агрегированный, защищающий конфиденциальность сигнал SKAdNetwork от Apple и анонимное событие «приложение открыто». Ваши данные о здоровье (препараты, дозы, инъекции, вес, глюкоза, побочные эффекты, заметки) никогда не передаются Meta.",
"uk": "Застосунок використовує SDK Meta (Facebook) з однією метою: агреговано вимірювати, чи прийшли встановлення з нашої реклами. Застосунок не відстежує вас: він ніколи не збирає рекламний ідентифікатор пристрою (IDFA), ніколи не показує запит App Tracking Transparency від Apple, а рекламне відстеження в SDK вимкнено назавжди. Meta отримує лише агрегований сигнал SKAdNetwork від Apple, що захищає приватність, і анонімну подію «застосунок відкрито». Ваші дані про здоров'я (препарати, дози, ін'єкції, вага, глюкоза, побічні ефекти, нотатки) ніколи не надсилаються Meta.",
"cs": "Aplikace používá SDK Meta (Facebook) k jedinému účelu: souhrnně měřit, zda instalace přišly z některé z našich reklam. Aplikace tě nesleduje: nikdy nesbírá reklamní identifikátor zařízení (IDFA), nikdy nezobrazuje výzvu App Tracking Transparency od Applu a reklamní sledování v SDK je trvale vypnuté. Meta dostává pouze souhrnný signál SKAdNetwork od Applu, který chrání soukromí, a anonymní událost „aplikace otevřena“. Tvoje zdravotní údaje (léky, dávky, injekce, váha, glykemie, nežádoucí účinky, poznámky) se do Meta nikdy neposílají.",
"ja": "アプリは Meta（Facebook）SDK を一つの目的のためだけに使用します。アプリのインストールが当社の広告経由かどうかを集計レベルで測定することです。アプリはあなたを追跡しません。端末の広告識別子（IDFA）を一切収集せず、Apple のアプリトラッキング透明性（ATT）の許可画面も表示せず、SDK 内の広告主トラッキングは常にオフです。Meta が受け取るのは、Apple のプライバシー保護型の集計シグナル SKAdNetwork と匿名の「アプリ起動」イベントのみです。あなたの健康データ（薬、投与量、注射、体重、血糖値、副作用、メモ）が Meta に送られることはありません。",
"ko": "앱은 Meta(Facebook) SDK를 한 가지 목적으로만 사용합니다. 앱 설치가 당사 광고에서 비롯되었는지를 집계 수준에서 측정하는 것입니다. 앱은 사용자를 추적하지 않습니다. 기기의 광고 식별자(IDFA)를 절대 수집하지 않고, Apple의 앱 추적 투명성(ATT) 요청을 표시하지 않으며, SDK의 광고주 추적은 영구적으로 꺼져 있습니다. Meta는 Apple의 개인정보 보호형 집계 신호인 SKAdNetwork와 익명의 '앱 열림' 이벤트만 받습니다. 사용자의 건강 데이터(약물, 투여량, 주사, 체중, 혈당, 부작용, 메모)는 Meta로 절대 전송되지 않습니다.",
"zh": "应用仅出于一个目的使用 Meta（Facebook）SDK：以汇总方式衡量应用安装是否来自我们的广告。应用不会跟踪你：从不收集设备的广告标识符（IDFA），从不显示 Apple 的应用跟踪透明度（ATT）请求，SDK 中的广告主跟踪已永久关闭。Meta 只会收到 Apple 保护隐私的汇总信号 SKAdNetwork 以及一个匿名的“应用已打开”事件。你的健康数据（药物、剂量、注射、体重、血糖、副作用、笔记）绝不会发送给 Meta。",
"ar": "يستخدم التطبيق حزمة تطوير Meta (Facebook) لغرض واحد: القياس بشكل مجمّع ما إذا كانت عمليات التثبيت جاءت من أحد إعلاناتنا. التطبيق لا يتتبعك: لا يجمع أبدًا معرّف الإعلانات لجهازك (IDFA)، ولا يعرض أبدًا طلب شفافية تتبع التطبيقات من Apple، وتتبع المعلنين داخل الحزمة مُعطّل بشكل دائم. تتلقى Meta فقط إشارة SKAdNetwork المجمّعة من Apple التي تحمي الخصوصية، وحدثًا مجهول الهوية بعنوان «تم فتح التطبيق». بياناتك الصحية (الأدوية والجرعات والحقن والوزن وسكر الدم والآثار الجانبية والملاحظات) لا تُرسل أبدًا إلى Meta.",
"hi": "ऐप Meta (Facebook) SDK का उपयोग केवल एक उद्देश्य से करता है: समग्र रूप से यह मापना कि इंस्टॉल हमारे किसी विज्ञापन से आए या नहीं। ऐप आपको ट्रैक नहीं करता: यह आपके डिवाइस का विज्ञापन पहचानकर्ता (IDFA) कभी एकत्र नहीं करता, Apple का App Tracking Transparency अनुरोध कभी नहीं दिखाता, और SDK में विज्ञापनदाता ट्रैकिंग स्थायी रूप से बंद है। Meta को केवल Apple का गोपनीयता-रक्षक समग्र SKAdNetwork संकेत और एक गुमनाम \"ऐप खोला गया\" इवेंट मिलता है। आपका स्वास्थ्य डेटा (दवाएँ, खुराक, इंजेक्शन, वज़न, रक्त शर्करा, दुष्प्रभाव, नोट्स) कभी Meta को नहीं भेजा जाता।",
}
UPDATED = {
"de": "Zuletzt aktualisiert: 2. Oktober 2026 · Gültig ab: 2. Oktober 2026",
"fr": "Dernière mise à jour : 2 octobre 2026 · En vigueur depuis le 2 octobre 2026",
"es": "Última actualización: 2 de octubre de 2026 · En vigor desde el 2 de octubre de 2026",
"it": "Ultimo aggiornamento: 2 ottobre 2026 · In vigore dal 2 ottobre 2026",
"pt": "Última atualização: 2 de outubro de 2026 · Em vigor desde 2 de outubro de 2026",
"nl": "Laatst bijgewerkt: 2 oktober 2026 · Van kracht sinds 2 oktober 2026",
"pl": "Ostatnia aktualizacja: 2 października 2026 · Obowiązuje od 2 października 2026",
"sv": "Senast uppdaterad: 2 oktober 2026 · Gäller från 2 oktober 2026",
"da": "Senest opdateret: 2. oktober 2026 · Gælder fra 2. oktober 2026",
"nb": "Sist oppdatert: 2. oktober 2026 · Gjelder fra 2. oktober 2026",
"fi": "Viimeksi päivitetty: 2. lokakuuta 2026 · Voimassa 2.10.2026 alkaen",
"el": "Τελευταία ενημέρωση: 2 Οκτωβρίου 2026 · Σε ισχύ από 2 Οκτωβρίου 2026",
"ru": "Последнее обновление: 2 октября 2026 г. · Действует с 2 октября 2026 г.",
"uk": "Останнє оновлення: 2 жовтня 2026 р. · Чинна з 2 жовтня 2026 р.",
"cs": "Poslední aktualizace: 2. října 2026 · Účinnost: 2. října 2026",
"ja": "最終更新日：2026年10月2日 ・ 施行日：2026年10月2日",
"ko": "최종 업데이트: 2026년 10월 2일 · 시행: 2026년 10월 2일",
"zh": "最后更新：2026 年 10 月 2 日 · 生效：2026 年 10 月 2 日",
"ar": "آخر تحديث: 2 أكتوبر 2026 · سريان: 2 أكتوبر 2026",
"hi": "आख़िरी अपडेट: 2 अक्टूबर 2026 · प्रभावी: 2 अक्टूबर 2026",
}
ATT_RE = re.compile(r"Tracking.Transparen|IDFA|透明性|추적 투명성|跟踪透明度|شفافية تتبع|Werbekennung|publicit|pubblicit|advert|reklam|mainos|διαφημ|реклам|реклам|विज्ञापन|広告|광고|广告|إعلان", re.I)

# ---- privacy.html (EN + TR) ----
html = HTML.read_text(encoding="utf-8")
n = 0
HTML_DONE = EN_P in html
def sub_li(old_pat, new, s):
    global n
    s2, k = re.subn(r"<li>[^<]*" + old_pat + r"[^<]*</li>", "<li>" + new + "</li>", s, count=1)
    n += k
    return s2
html = sub_li(r"App Tracking Transparency prompt: see the ad measurement", EN_BULLET, html)
html = sub_li(r"Reklam tanımlayıcıları[^<]*İzleme Şeffaflığı", TR_BULLET, html)
html, k = re.subn(r"<p>The App uses the <strong>Meta \(Facebook\) SDK</strong>.*?</p>", "<p>" + EN_P + "</p>", html, count=1, flags=re.S); n += k
html, k = re.subn(r"<p>Uygulama, <strong>Meta \(Facebook\) SDK</strong>.*?</p>", "<p>" + TR_P + "</p>", html, count=1, flags=re.S); n += k
html, k = re.subn(r"Last updated: September 30, 2026 · Effective: September 30, 2026", "Last updated: October 2, 2026 · Effective: October 2, 2026", html); n += k
html, k = re.subn(r"Son güncelleme: 30 Eylül 2026 · Yürürlük: 30 Eylül 2026", "Son güncelleme: 2 Ekim 2026 · Yürürlük: 2 Ekim 2026", html); n += k
if not HTML_DONE:
    assert n == 6, f"privacy.html: expected 6 replacements, made {n}"
    HTML.write_text(html, encoding="utf-8")
else:
    print("privacy.html already updated")

# ---- legal-content.json (20 languages) ----
data = json.loads(JSON.read_text(encoding="utf-8"))
for lang, doc in data.items():
    priv = doc["privacy"]
    blocks = priv["blocks"]
    hits = 0
    for blk in blocks:
        if blk["t"] == "ul":
            for i, item in enumerate(blk["v"]):
                if ATT_RE.search(item):
                    blk["v"][i] = B[lang]; hits += 1
        elif blk["t"] == "p" and "Meta" in blk["v"] and ATT_RE.search(blk["v"]):
            blk["v"] = P[lang]; hits += 1
    assert hits == 2, f"{lang}: expected bullet+paragraph, replaced {hits}"
    priv["updated"] = UPDATED[lang]
JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("privacy.html: 6 replacements; legal-content.json: 20 languages x (bullet, paragraph, date)")
