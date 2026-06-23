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

  // 3) Bouton flottant « Imprimer / PDF » — injecté automatiquement.
  //    Évite le doublon si la page possède déjà un contrôle d'impression
  //    (bouton .print-btn ou tout onclick=window.print()).
  function hasExistingPrintControl() {
    if (document.querySelector('.print-btn, [data-print]')) return true;
    var els = document.querySelectorAll('[onclick]');
    for (var i = 0; i < els.length; i++) {
      var oc = els[i].getAttribute('onclick') || '';
      if (/window\.print\s*\(/.test(oc)) return true;
    }
    return false;
  }
  function injectPrintButton() {
    if (document.getElementById('daat-print-fab')) return;
    if (hasExistingPrintControl()) return;     // ne pas doubler un bouton existant
    var rtl = (document.documentElement.getAttribute('dir') === 'rtl');
    var lang = (document.documentElement.getAttribute('lang') || 'fr').slice(0, 2);
    var label = lang === 'he' ? '🖨 הדפסה / PDF'
              : lang === 'en' ? '🖨 Print / PDF'
              : '🖨 Imprimer / PDF';
    var btn = document.createElement('button');
    btn.id = 'daat-print-fab';
    btn.type = 'button';
    btn.textContent = label;
    btn.setAttribute('aria-label', label);
    btn.style.cssText = 'position:fixed;bottom:18px;' + (rtl ? 'left:18px;' : 'right:18px;')
      + 'z-index:9990;font-family:Inter,system-ui,sans-serif;font-size:12px;font-weight:600;'
      + 'letter-spacing:.5px;background:#1A1F3A;color:#C5A55A;padding:9px 16px;'
      + 'border:1px solid #C5A55A;border-radius:24px;cursor:pointer;'
      + 'box-shadow:0 2px 10px rgba(26,31,58,.25);opacity:.92;transition:opacity .2s,transform .2s;';
    btn.onmouseenter = function () { btn.style.opacity = '1'; btn.style.transform = 'translateY(-1px)'; };
    btn.onmouseleave = function () { btn.style.opacity = '.92'; btn.style.transform = 'none'; };
    btn.onclick = function () { window.print(); };
    document.body.appendChild(btn);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectPrintButton);
  } else {
    injectPrintButton();
  }

  // Style minimal injecté (auto-suffisant).
  var css = '.daat-copy{cursor:pointer;font-family:Inter,system-ui,sans-serif;font-size:11px;'
    + 'letter-spacing:.5px;color:#C5A55A;background:transparent;border:1px solid rgba(197,165,90,.5);'
    + 'border-radius:4px;padding:3px 10px;margin:0 0 0 6px;transition:all .2s;vertical-align:middle;}'
    + '.daat-copy:hover{background:#C5A55A;color:#1A1F3A;}'
    + '.daat-copy.is-copied{background:#2d7a3e;color:#fff;border-color:#2d7a3e;}'
    + '@media print{.daat-copy,#daat-print-fab{display:none!important;}}';
  var style = document.createElement('style');
  style.appendChild(document.createTextNode(css));
  document.head.appendChild(style);
})();
