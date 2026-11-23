/* Wise-Teck v3 — site behaviour (vanilla JS, no dependencies) */
(function () {
  var html = document.documentElement;
  html.classList.add('js');

  /* ---- scroll reveal ---- */
  var els = [].slice.call(document.querySelectorAll('.reveal'));
  // .shown = the fade-in is over: the element's own hover effects and transitions take over (see .reveal in the CSS)
  var showNow = function (el) { el.classList.add('in', 'shown'); };
  var fadeIn = function (el) { el.classList.add('in'); setTimeout(function () { el.classList.add('shown'); }, 1200); };
  if (/[?&]static/.test(location.search)) { html.classList.add('static'); els.forEach(showNow); }
  else if ('IntersectionObserver' in window) {
    // Whatever is already on the first screen shows at once (no flash, no late Largest Contentful Paint);
    // only content further down fades in as it scrolls into view.
    els = els.filter(function (el) {
      if (el.getBoundingClientRect().top < window.innerHeight) { showNow(el); return false; }
      return true;
    });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { fadeIn(e.target); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(showNow); }

  /* ---- mobile menu ---- */
  var burger = document.querySelector('.burger'), menu = document.getElementById('menu');
  if (burger && menu) {
    burger.setAttribute('aria-controls', 'menu'); burger.setAttribute('aria-expanded', 'false');
    var setOpen = function (open) {
      menu.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    burger.addEventListener('click', function () {
      var open = !menu.classList.contains('open');
      setOpen(open);
      burger.classList.toggle('just-closed', !open);   // show the resting (uneven) lines at once, not the hover look
    });
    burger.addEventListener('pointerleave', function () { burger.classList.remove('just-closed'); });
    document.addEventListener('click', function (e) {          // a tap on the dimmed page closes the menu
      if (menu.classList.contains('open') && !menu.contains(e.target) && !burger.contains(e.target)) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('open')) { setOpen(false); burger.focus(); }
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
