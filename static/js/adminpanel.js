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
