/*
 * Ana sayfanın iki küçük davranışı. Betik yüklenmezse sayfa eksiksiz kalır:
 * galeri yana kayan şerit olarak durur, hiçbir içerik gizli başlamaz.
 *
 * 1. "Dozify'ı yakından görün": geniş ekranda ekran adlarına basınca telefondaki
 *    ekran değişir. Dar ekranda şerit olduğu gibi kalır.
 * 2. Görünüme giren bölümlerin parçaları sırayla yükselir. Hareket azaltma
 *    isteyen ziyaretçide hiç çalışmaz.
 */
(function () {
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function viewer() {
    var strip = document.querySelector('#screenshots .screenshot-strip');
    if (!strip) return;
    var heading = document.querySelector('#screenshots h2');
    var wide = window.matchMedia('(min-width: 960px)');
    var shots = [].slice.call(strip.querySelectorAll('.shot'));
    var live = document.createElement('p');
    live.className = 'sr-only';
    live.setAttribute('role', 'status');
    strip.parentNode.insertBefore(live, strip.nextSibling);

    var started = false;

    function load(shot) {
      var img = shot && shot.querySelector('img');
      if (img) img.loading = 'eager';
    }

    function show(index) {
      shots.forEach(function (shot, i) {
        shot.classList.toggle('is-active', i === index);
        var b = shot.querySelector('figcaption button');
        if (b) b.setAttribute('aria-pressed', i === index ? 'true' : 'false');
      });
      load(shots[index]);
      load(shots[index + 1]);
      var img = shots[index].querySelector('img');
      live.textContent = started && img ? img.alt : '';
      started = true;
    }

    function on() {
      strip.classList.add('is-viewer');
      strip.removeAttribute('tabindex');
      if (heading) {
        heading.id = heading.id || 'screenshots-title';
        strip.setAttribute('aria-labelledby', heading.id);
      }
      shots.forEach(function (shot, i) {
        var cap = shot.querySelector('figcaption');
        var b = document.createElement('button');
        b.type = 'button';
        while (cap.firstChild) b.appendChild(cap.firstChild);
        b.addEventListener('click', function () { show(i); });
        b.addEventListener('pointerenter', function () { load(shot); });
        cap.appendChild(b);
      });
      show(0);
    }

    function off() {
      strip.classList.remove('is-viewer');
      strip.setAttribute('tabindex', '0');
      strip.removeAttribute('aria-labelledby');
      shots.forEach(function (shot) {
        shot.classList.remove('is-active');
        var cap = shot.querySelector('figcaption');
        var b = cap.querySelector('button');
        if (!b) return;
        while (b.firstChild) cap.appendChild(b.firstChild);
        b.remove();
      });
    }

    if (wide.matches) on();
    wide.addEventListener('change', function (e) { if (e.matches) on(); else off(); });
  }

  function reveal() {
    if (calm || !('IntersectionObserver' in window)) return;
    var parts = document.querySelectorAll(
      '.section-title, .section-lede, .split-copy > *, .split-shot .device, ' +
      '#themes .shot, #ai-calories .shot, .step, .feature, .article-card, ' +
      '.faq-item, .privacy-card > *, .cta-copy > *, .cta-phone .device, .trademarks'
    );
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        entry.target.classList.add('rv-in');
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    [].forEach.call(parts, function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) return;
      var i = [].indexOf.call(el.parentNode.children, el);
      el.style.transitionDelay = Math.min(i, 4) * 70 + 'ms';
      el.classList.add('rv');
      io.observe(el);
    });
  }

  function drift() {
    if (calm) return;
    var hero = document.querySelector('.hero');
    var b = document.querySelector('.phone-b');
    var c = document.querySelector('.phone-c');
    if (!hero || !b || !c || !window.matchMedia('(min-width: 960px)').matches) return;
    var queued = false;
    window.addEventListener('scroll', function () {
      if (queued) return;
      queued = true;
      requestAnimationFrame(function () {
        queued = false;
        var y = Math.min(window.scrollY, hero.offsetHeight);
        b.style.translate = '0 ' + (y * -0.05).toFixed(1) + 'px';
        c.style.translate = '0 ' + (y * -0.1).toFixed(1) + 'px';
      });
    }, { passive: true });
  }

  viewer();
  reveal();
  drift();
})();
