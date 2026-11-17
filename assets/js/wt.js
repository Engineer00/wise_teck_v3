/* Wise-Teck v3 — site behaviour (vanilla JS, no dependencies) */
(function () {
  var html = document.documentElement;
  html.classList.add('js');

  /* ---- scroll reveal ---- */
  var els = [].slice.call(document.querySelectorAll('.reveal'));
  if (/[?&]static/.test(location.search)) { html.classList.add('static'); els.forEach(function (el) { el.classList.add('in'); }); }
  else if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  /* ---- mobile menu ---- */
  var burger = document.querySelector('.burger'), menu = document.getElementById('menu');
  if (burger && menu) burger.addEventListener('click', function () { menu.classList.toggle('open'); });

  /* ---- testimonial slider ---- */
  var slides = document.getElementById('stSlides');
  if (slides) {
    var dots = [].slice.call(document.querySelectorAll('#stDots button')), i = 0, n = dots.length;
    var go = function (k) { i = (k + n) % n; slides.style.transform = 'translateX(-' + (i * 100) + '%)'; dots.forEach(function (d, j) { d.classList.toggle('on', j === i); }); };
    dots.forEach(function (d, j) { d.addEventListener('click', function () { go(j); }); });
    [].forEach.call(document.querySelectorAll('[data-st]'), function (b) { b.addEventListener('click', function () { go(i + (+b.dataset.st)); }); });
    setInterval(function () { go(i + 1); }, 7000);
  }

  /* ---- reference overlay (home page): ?overlay in the URL or press O ----
     Every section carries data-ref-top / data-ref-h (page px of the reference at 1440 wide).
     The matching slice of the reference JPEG is laid over it, scaled to the section width. */
  var secs = [].slice.call(document.querySelectorAll('[data-ref-top]'));
  if (!secs.length) return;
  var ui = document.createElement('div');
  ui.className = 'ovl-ui';
  ui.innerHTML = '<b>Reference</b><button type="button">Show</button><input type="range" min="0" max="100" value="50" aria-label="Overlay opacity"><span>50%</span>';
  document.body.appendChild(ui);
  var btn = ui.querySelector('button'), rng = ui.querySelector('input'), lab = ui.querySelector('span');
  var REF = (document.body.getAttribute('data-ref') || 'assets/ref/reference.jpeg');
  function build() {
    [].forEach.call(document.querySelectorAll('.ovl'), function (o) { o.remove(); });
    secs.forEach(function (s) {
      var o = document.createElement('div'), w = s.clientWidth, k = w / 1440;
      o.className = 'ovl';
      o.style.top = (s.getBoundingClientRect().top + scrollY) + 'px';
      o.style.height = s.offsetHeight + 'px';
      o.style.backgroundImage = 'url("' + REF + '")';
      o.style.backgroundPosition = '0 ' + (-(+s.dataset.refTop) * k) + 'px';
      o.style.opacity = rng.value / 100;
      document.body.appendChild(o);
    });
  }
  function toggle() { html.classList.toggle('show-ovl'); btn.textContent = html.classList.contains('show-ovl') ? 'Hide' : 'Show'; build(); }
  document.body.style.position = 'relative';
  btn.addEventListener('click', toggle);
  rng.addEventListener('input', function () { lab.textContent = rng.value + '%'; [].forEach.call(document.querySelectorAll('.ovl'), function (o) { o.style.opacity = rng.value / 100; }); });
  addEventListener('keydown', function (e) { if ((e.key === 'o' || e.key === 'O') && !/input|textarea|select/i.test(e.target.tagName)) { html.classList.add('ovl-tool'); toggle(); } });
  addEventListener('resize', function () { if (html.classList.contains('show-ovl')) build(); });
  if (/[?&]overlay/.test(location.search)) { html.classList.add('ovl-tool'); toggle(); }
})();
