(function() {
  var KEY = 'dozify-lang';
  var SUPPORTED = ['en', 'tr'];

  function detectInitialLang() {
    var saved = localStorage.getItem(KEY);
    if (SUPPORTED.indexOf(saved) > -1) return saved;
    var nav = (navigator.language || navigator.userLanguage || 'en').toLowerCase();
    return nav.indexOf('tr') === 0 ? 'tr' : 'en';
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
