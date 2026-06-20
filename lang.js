(function() {
  var KEY = 'dozify-lang';
  var SUPPORTED = ['en', 'tr'];

  // Best-effort, privacy-friendly geo check: a visitor whose device time zone
  // is Istanbul is treated as being in Turkey. No IP lookup, no network call.
  function isLikelyTurkey() {
    try {
      var tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || '');
      if (tz === 'Europe/Istanbul') return true;
    } catch (e) {}
    return false;
  }

  function detectInitialLang() {
    var saved = localStorage.getItem(KEY);
    if (SUPPORTED.indexOf(saved) > -1) return saved;
    // Default language by location, not browser language: only visitors in
    // Turkey see Turkish; everyone outside Turkey gets English. A manual
    // choice from the toggle (saved above) always wins.
    return isLikelyTurkey() ? 'tr' : 'en';
  }

  function applyLang(lang) {
    document.documentElement.lang = lang;
    var btns = document.querySelectorAll('[data-set-lang]');
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.toggle('is-active', btns[i].dataset.setLang === lang);
    }
  }

  // Apply ASAP to avoid flash
  applyLang(detectInitialLang());

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-set-lang]');
    if (!btn) return;
    var newLang = btn.dataset.setLang;
    if (SUPPORTED.indexOf(newLang) === -1) return;
    localStorage.setItem(KEY, newLang);
    applyLang(newLang);
  });
})();
