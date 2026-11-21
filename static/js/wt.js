/* Wise-Teck v3 — site behaviour (vanilla JS, no dependencies) */
(function () {
  var html = document.documentElement;
  html.classList.add('js');

  /* ---- scroll reveal ---- */
  var els = [].slice.call(document.querySelectorAll('.reveal'));
  if (/[?&]static/.test(location.search)) { html.classList.add('static'); els.forEach(function (el) { el.classList.add('in'); }); }
  else if ('IntersectionObserver' in window) {
    // Whatever is already on the first screen shows at once (no flash, no late Largest Contentful Paint);
    // only content further down fades in as it scrolls into view.
    els = els.filter(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) { el.classList.add('in'); return false; }
      return true;
    });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  /* ---- mobile menu ---- */
  var burger = document.querySelector('.burger'), menu = document.getElementById('menu');
  if (burger && menu) {
    burger.setAttribute('aria-controls', 'menu'); burger.setAttribute('aria-expanded', 'false');
    burger.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    /* mobile menu: submenus are an accordion (one open at a time), so the list stays short
       and the Apply Now button at the bottom stays in reach */
    var mobile = window.matchMedia('(max-width: 1199px)');
    [].forEach.call(menu.querySelectorAll('.dd > button'), function (b) {
      b.setAttribute('aria-expanded', 'false');
      b.addEventListener('click', function () {
        if (!mobile.matches) return;
        var dd = b.parentNode, open = !dd.classList.contains('open');
        [].forEach.call(menu.querySelectorAll('.dd.open'), function (o) { o.classList.remove('open'); o.firstElementChild.setAttribute('aria-expanded', 'false'); });
        dd.classList.toggle('open', open); b.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });
  }

  /* ---- testimonial slider: autoplay pauses on hover / keyboard focus and is off for reduced motion ---- */
  var slides = document.getElementById('stSlides');
  if (slides) {
    var dots = [].slice.call(document.querySelectorAll('#stDots button')), i = 0, n = dots.length, paused = false;
    var go = function (k) { i = (k + n) % n; slides.style.transform = 'translateX(-' + (i * 100) + '%)'; dots.forEach(function (d, j) { d.classList.toggle('on', j === i); }); };
    dots.forEach(function (d, j) { d.addEventListener('click', function () { go(j); }); });
    [].forEach.call(document.querySelectorAll('[data-st]'), function (b) { b.addEventListener('click', function () { go(i + (+b.dataset.st)); }); });
    var box = slides.closest('.stories') || slides;
    ['mouseenter', 'focusin'].forEach(function (e) { box.addEventListener(e, function () { paused = true; }); });
    ['mouseleave', 'focusout'].forEach(function (e) { box.addEventListener(e, function () { paused = false; }); });
    var still = /[?&]static/.test(location.search) || (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
    if (n > 1 && !still) setInterval(function () { if (!paused && !document.hidden) go(i + 1); }, 7000);
  }
})();
