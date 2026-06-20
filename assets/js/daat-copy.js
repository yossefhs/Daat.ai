/* ===================================================================
   DAAT — Copier-coller avec lien systématique vers le site
   -------------------------------------------------------------------
   1) Toute copie de texte (sélection) emporte automatiquement une ligne
      d'attribution + le lien canonique de la page (partage WhatsApp, etc.).
   2) Boutons « העתק » : tout élément portant la classe .daat-copy copie
      le bloc parent marqué [data-copy-block] (ou la cible data-copy-target),
      texte + attribution incluse.
   Drop-in : <script src="…/assets/js/daat-copy.js" defer></script>
   =================================================================== */
(function () {
  function siteRef() {
    var canon = document.querySelector('link[rel="canonical"]');
    var url = canon && canon.href ? canon.href : location.href;
    var title = (document.title || 'דעת תורה').split('·')[0].split('|')[0].trim();
    return { url: url, title: title };
  }
  function attribution() {
    var r = siteRef();
    return '\n\n— ' + r.title + ' · דעת תורה · DAAT\n' + r.url;
  }

  // 1) Append automatique du lien à chaque copie d'une sélection.
  document.addEventListener('copy', function (e) {
    try {
      // Ne pas interférer avec une copie programmatique depuis un champ
      // (ex. le textarea temporaire de share-text.js) — évite un double lien.
      var ae = document.activeElement;
      if (ae && /^(textarea|input)$/i.test(ae.tagName)) return;
      var sel = window.getSelection ? String(window.getSelection()) : '';
      if (!sel || sel.trim().length < 2) return;            // ignore copie triviale
      if (e.clipboardData) {
        e.clipboardData.setData('text/plain', sel + attribution());
        e.preventDefault();
      }
    } catch (err) { /* en cas d'échec, on laisse le copier natif */ }
  });

  // 2) Boutons de copie explicites.
  function textOf(el) { return (el.innerText || el.textContent || '').trim(); }
  function legacyCopy(t) {
    var ta = document.createElement('textarea');
    ta.value = t; ta.setAttribute('readonly', '');
    ta.style.position = 'absolute'; ta.style.left = '-9999px';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
  }
  function flash(btn) {
    if (!btn) return;
    var old = btn.textContent;
    btn.textContent = '✓ הועתק';
    btn.classList.add('is-copied');
    setTimeout(function () { btn.textContent = old; btn.classList.remove('is-copied'); }, 1600);
  }
  function doCopy(txt, btn) {
    var full = txt + attribution();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(full).then(function () { flash(btn); },
        function () { legacyCopy(full); flash(btn); });
    } else { legacyCopy(full); flash(btn); }
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.daat-copy') : null;
    if (!btn) return;
    e.preventDefault();
    var sel = btn.getAttribute('data-copy-target');
    var src = sel ? document.querySelector(sel)
                  : (btn.closest ? btn.closest('[data-copy-block]') : null);
    if (src) doCopy(textOf(src), btn);
  });

  // Style minimal injecté (auto-suffisant).
  var css = '.daat-copy{cursor:pointer;font-family:Inter,system-ui,sans-serif;font-size:11px;'
    + 'letter-spacing:.5px;color:#C5A55A;background:transparent;border:1px solid rgba(197,165,90,.5);'
    + 'border-radius:4px;padding:3px 10px;margin:0 0 0 6px;transition:all .2s;vertical-align:middle;}'
    + '.daat-copy:hover{background:#C5A55A;color:#1A1F3A;}'
    + '.daat-copy.is-copied{background:#2d7a3e;color:#fff;border-color:#2d7a3e;}'
    + '@media print{.daat-copy{display:none!important;}}';
  var style = document.createElement('style');
  style.appendChild(document.createTextNode(css));
  document.head.appendChild(style);
})();
