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

  // Best upload size for a photo field in this layout: a badge next to the label (tooltip) + a help line.
  function showSize(box, hint) {
    [].forEach.call(box.querySelectorAll('[data-size-hint]'), function (n) { n.remove(); });
    var l = labelOf(box);
    if (!hint || !l) return;
    var badge = document.createElement('span');
    badge.className = 'ap-size';
    badge.setAttribute('data-size-hint', '');
    badge.title = hint.tip;
    badge.textContent = hint.size;
    l.parentNode.appendChild(badge);
    var line = document.createElement('p');
    line.className = 'ap-help';
    line.setAttribute('data-size-hint', '');
    line.textContent = hint.tip;
    box.appendChild(line);
  }
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
        showSize(box, g && on ? g.sizes[name] : null);
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
        showSize(box, has ? g.item_sizes[name] : null);
      });
    }
  }
  select.addEventListener('change', apply);
  apply();
})();
