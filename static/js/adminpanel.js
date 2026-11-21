(function () {
  var shell = document.querySelector('.ap-shell');
  var btn = document.getElementById('apMenuBtn');
  var backdrop = document.getElementById('apBackdrop');
  if (!shell || !btn) return;

  function open() {
    shell.classList.add('is-open');
    if (backdrop) backdrop.hidden = false;
  }
  function close() {
    shell.classList.remove('is-open');
    if (backdrop) backdrop.hidden = true;
  }
  function toggle() {
    if (shell.classList.contains('is-open')) close();
    else open();
  }

  btn.addEventListener('click', toggle);
  if (backdrop) backdrop.addEventListener('click', close);
  window.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
  });
})();

/* confirm before publishing / restoring, and filter drop-downs that apply at once
   (kept here instead of inline onsubmit / onchange so the site can use a strict Content-Security-Policy) */
(function () {
  document.addEventListener('submit', function (e) {
    var msg = e.target.getAttribute && e.target.getAttribute('data-confirm');
    if (msg && !window.confirm(msg)) e.preventDefault();
  });
  document.addEventListener('change', function (e) {
    if (e.target.hasAttribute && e.target.hasAttribute('data-autosubmit') && e.target.form) e.target.form.submit();
  });
})();

/* Site Settings → colour scheme: show the three colour pickers only for "Custom colours",
   keep the custom card's swatches in step with the pickers, and point "Preview" at the chosen scheme */
(function () {
  var picker = document.querySelector('[data-scheme-picker]');
  if (!picker) return;
  var form = picker.closest('form');
  var names = ['primary', 'accent', 'dark'];
  var inputs = names.map(function (n) { return form.querySelector('[name="color_' + n + '"]'); });
  var custom = picker.querySelector('[data-scheme-custom]');
  var preview = form.querySelector('[data-scheme-preview]');

  function update() {
    var chosen = picker.querySelector('input:checked');
    var key = chosen ? chosen.value : '';
    var isCustom = key === 'custom';
    inputs.forEach(function (input, i) {
      if (!input) return;
      var box = input.closest('[data-field]');
      if (box) box.hidden = !isCustom;
      custom.style.setProperty('--c' + (i + 1), input.value);
    });
    var q = '?scheme=' + encodeURIComponent(key);
    if (isCustom) inputs.forEach(function (input, i) { if (input) q += '&' + names[i] + '=' + encodeURIComponent(input.value); });
    if (preview) preview.href = '/' + q;
  }
  picker.addEventListener('change', update);
  inputs.forEach(function (input) { if (input) input.addEventListener('input', update); });
  update();
})();

/* Copy buttons (dashboard: sitemap address). */
document.addEventListener('click', function (e) {
  var btn = e.target.closest('[data-copy]');
  if (!btn || !navigator.clipboard) return;
  navigator.clipboard.writeText(btn.getAttribute('data-copy')).then(function () {
    var label = btn.textContent;
    btn.textContent = 'Copied';
    setTimeout(function () { btn.textContent = label; }, 1500);
  });
});
