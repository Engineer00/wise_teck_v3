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
