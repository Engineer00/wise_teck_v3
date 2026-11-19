/* Section form: show only the fields the chosen layout uses, relabel them in that layout's terms,
   and explain what the cards under the section are. Data: core/layouts.py (GUIDE). */
(function () {
  var el = document.getElementById('apLayoutGuide');
  var select = document.getElementById('id_layout');
  if (!el || !select) return;
  var guide = JSON.parse(el.textContent);
  var help = document.getElementById('apLayoutHelp');
  var itemsHelp = document.getElementById('apItemsHelp');
  var form = select.form;
  var original = {};

  function fieldsIn(root) { return [].slice.call(root.querySelectorAll('[data-field]')); }
  function labelOf(box) { return box.querySelector('.ap-label-text'); }
  fieldsIn(form).forEach(function (box) {
    var l = labelOf(box);
    if (l && !original[box.dataset.field]) original[box.dataset.field] = l.textContent;
  });

  function apply() {
    var g = guide.layouts[select.value];
    var main = [].slice.call(form.querySelectorAll('fieldset[data-group]'));
    main.forEach(function (fs) {
      var shown = 0;
      fieldsIn(fs).forEach(function (box) {
        var name = box.dataset.field, on = !g || guide.always.indexOf(name) > -1 || (name in g.fields);
        box.hidden = !on;
        var l = labelOf(box);
        if (l) l.textContent = (g && g.fields[name]) || original[name] || l.textContent;
        if (on) shown++;
      });
      fs.hidden = shown === 0;
    });
    if (help) { help.hidden = !g; help.textContent = g ? g.help : ''; }
    var inl = form.querySelector('.ap-inlines');
    if (inl) {
      var items = g ? g.items : {}, has = Object.keys(items).length > 0;
      inl.closest('fieldset').hidden = g ? !has : false;
      if (itemsHelp) itemsHelp.textContent = g ? (g.item_help || '') : '';
      fieldsIn(inl).forEach(function (box) {
        var name = box.dataset.field;
        if (name === 'order' || name === 'is_active') { box.hidden = false; return; }
        box.hidden = has && !(name in items);
        var l = labelOf(box);
        if (l) l.textContent = (has && items[name]) || original[name] || l.textContent;
      });
    }
  }
  select.addEventListener('change', apply);
  apply();
})();
