(function() {
  // Automatic, privacy-friendly language detection — no manual toggle, no IP
  // lookup, no network call. Turkish for visitors in Turkey (by device time
  // zone) or with a Turkish system language; English for everyone else.
  function isLikelyTurkish() {
    try {
      var tz = (Intl.DateTimeFormat().resolvedOptions().timeZone || '');
      if (tz === 'Europe/Istanbul') return true;
    } catch (e) {}
    var langs = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < langs.length; i++) {
      if (String(langs[i]).toLowerCase().indexOf('tr') === 0) return true;
    }
    return false;
  }

  // Apply ASAP to avoid flash
  document.documentElement.lang = isLikelyTurkish() ? 'tr' : 'en';
})();
