/*
 * Mağaza indirme düğmesi tıklamalarını ölçer.
 *
 * Neden delege dinleyici: siteye yeni indirme bağlantısı eklendiğinde kimsenin
 * ölçüm kodunu hatırlaması gerekmesin diye tek bir document dinleyicisi kullanılır;
 * App Store / Google Play'e giden HER bağlantı otomatik kapsanır.
 *
 * Ne gönderilir: hangi mağaza, hangi sayfa. Kişisel veri yok, form içeriği yok.
 * gtag yüklenmemişse (etiket engellenmiş, script hata vermiş) sessizce hiçbir şey
 * yapmaz — tıklama her hâlükârda mağazaya gider, ölçüm asla akışı bozmaz.
 */
(function () {
  var STORES = [
    { host: 'apps.apple.com', store: 'app_store' },
    { host: 'play.google.com', store: 'google_play' }
  ];

  document.addEventListener('click', function (e) {
    var link = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!link) return;

    var href = link.getAttribute('href') || '';
    var hit = null;
    for (var i = 0; i < STORES.length; i++) {
      if (href.indexOf(STORES[i].host) !== -1) { hit = STORES[i]; break; }
    }
    if (!hit) return;
    if (typeof window.gtag !== 'function') return;

    window.gtag('event', 'download_click', {
      store: hit.store,
      page_path: location.pathname
    });
  }, true);
})();
