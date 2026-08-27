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

/* ===================================================================
   DAAT — Bouton flottant « Partager » (WhatsApp / partage natif)
   -------------------------------------------------------------------
   Présent sur toutes les pages de contenu (simanim, limoud, blog) via
   daat-copy.js. Bas-gauche (le chat occupe le bas-droit). Utilise le
   partage natif (navigator.share → feuille iOS/Android avec WhatsApp)
   avec repli wa.me sur desktop. Event analytics : share_clicked.
   =================================================================== */
(function () {
  function pageLang() {
    var l = (document.documentElement.lang || 'fr').slice(0, 2);
    return (l === 'he' || l === 'en') ? l : 'fr';
  }
  function shareContext() {
    var p = location.pathname;
    var m = p.match(/^\/(?:oh|yd|oh-quotidien)\/(\d+)/) || p.match(/\/siman-(\d+)/);
    if (m) return { type: 'siman', ref: m[1] };
    if (p === '/aujourdhui' || p.indexOf('/aujourdhui/') === 0 || p.indexOf('/aujourdhui.') === 0) return { type: 'aujourdhui', ref: 'today' };
    m = p.match(/\/limoud\/jour-(\d+)/);
    if (m) return { type: 'limoud', ref: m[1] };
    if (p.indexOf('/blog/') === 0 && p.length > 6) return { type: 'blog', ref: p.split('/').pop().replace(/\.html$/, '') };
    return null;
  }
  var ctx = shareContext();
  if (!ctx) return; // pas une page de contenu partageable

  var L = {
    fr: { label: 'Partager', title: "Partager cette étude sur WhatsApp" },
    he: { label: 'שתף', title: 'שתף את הלימוד בוואטסאפ' },
    en: { label: 'Share', title: 'Share this study on WhatsApp' },
  }[pageLang()];

  function track() {
    try {
      window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
      window.va('event', { name: 'share_clicked', data: { type: ctx.type, ref: ctx.ref } });
    } catch (_) {}
  }
  function shareText() {
    var canon = document.querySelector('link[rel="canonical"]');
    var url = canon && canon.href ? canon.href : location.href;
    var title = (document.title || 'DAAT').split('|')[0].trim();
    return { title: title, url: url, text: '📖 ' + title };
  }

  var btn = document.createElement('button');
  btn.id = 'daat-share-fab';
  btn.type = 'button';
  btn.title = L.title;
  btn.setAttribute('aria-label', L.title);
  btn.innerHTML = '<span aria-hidden="true" style="font-size:15px;">📤</span><span>' + L.label + '</span>';
  btn.addEventListener('click', function () {
    track();
    var s = shareText();
    if (navigator.share) {
      navigator.share({ title: s.title, text: s.text, url: s.url }).catch(function () {});
    } else {
      window.open('https://wa.me/?text=' + encodeURIComponent(s.text + '\n' + s.url), '_blank', 'noopener');
    }
  });

  var css = '#daat-share-fab{position:fixed;bottom:24px;left:24px;z-index:9990;'
    + 'display:inline-flex;align-items:center;gap:7px;padding:10px 16px;'
    + 'background:#1faa55;color:#fff;border:none;border-radius:24px;cursor:pointer;'
    + 'font-family:Inter,system-ui,sans-serif;font-size:13px;font-weight:600;letter-spacing:.3px;'
    + 'box-shadow:0 4px 14px rgba(0,0,0,.18);transition:transform .15s,box-shadow .15s;}'
    + '#daat-share-fab:hover{transform:translateY(-2px);box-shadow:0 7px 20px rgba(0,0,0,.25);}'
    + '@media (max-width:640px){#daat-share-fab{bottom:16px;left:16px;padding:9px 14px;font-size:12px;}}'
    + '@media print{#daat-share-fab{display:none!important;}}';
  var style = document.createElement('style');
  style.appendChild(document.createTextNode(css));

  function mount() {
    document.head.appendChild(style);
    document.body.appendChild(btn);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

/* ===================================================================
   DAAT — « Signaler une erreur » (participation des lecteurs)
   -------------------------------------------------------------------
   Lien discret sous le bouton Partager → modal (type, séif, description,
   source) → POST /api/signalement (rate-limité, honeypot). Le pipeline
   NEW → NEEDS_RABBINIC_VALIDATION → FIXED est géré dans l'admin ;
   aucune halakha n'est modifiée sans validation du Rav.
   =================================================================== */
(function () {
  function pageLang() {
    var l = (document.documentElement.lang || 'fr').slice(0, 2);
    return (l === 'he' || l === 'en') ? l : 'fr';
  }
  var p = location.pathname;
  var simanM = p.match(/^\/(?:oh|yd|oh-quotidien)\/(\d+)/) || p.match(/\/siman-(\d+)/);
  var isContent = simanM || /\/limoud\/jour-\d+/.test(p) || (p.indexOf('/blog/') === 0 && p.length > 6);
  if (!isContent) return;

  var L = {
    fr: { link: '⚑ Signaler une erreur', title: 'Signaler une erreur', intro: 'Merci de nous aider à fiabiliser l\'étude. Chaque signalement est examiné, et rien n\'est modifié sans validation rabbinique.',
          type: 'Type de problème', types: { halakha: '❌ Erreur halakhique', traduction: '📝 Traduction à améliorer', langue: '✍️ Faute de langue', source: '📚 Source / référence', pedagogie: '💡 Suggestion pédagogique' },
          seif: 'Sé\'if concerné (optionnel)', desc: 'Décris le problème *', src: 'Source correcte, si tu la connais (optionnel)',
          send: 'Envoyer', cancel: 'Annuler', ok: '✓ Merci ! Ton signalement a bien été transmis.', err: 'Envoi impossible : ' },
    he: { link: '⚑ דווח על טעות', title: 'דיווח על טעות', intro: 'תודה שאתה עוזר לדייק את הלימוד. כל דיווח נבדק, ודבר אינו משתנה ללא אישור רבני.',
          type: 'סוג הבעיה', types: { halakha: '❌ טעות הלכתית', traduction: '📝 תרגום לשיפור', langue: '✍️ טעות לשונית', source: '📚 מקור / ציון', pedagogie: '💡 הצעה פדגוגית' },
          seif: 'סעיף (לא חובה)', desc: 'תאר את הבעיה *', src: 'המקור הנכון, אם ידוע לך (לא חובה)',
          send: 'שלח', cancel: 'ביטול', ok: '✓ תודה! הדיווח נשלח.', err: 'השליחה נכשלה: ' },
    en: { link: '⚑ Report an error', title: 'Report an error', intro: 'Thank you for helping us make the study more reliable. Every report is reviewed; nothing changes without rabbinic validation.',
          type: 'Problem type', types: { halakha: '❌ Halachic error', traduction: '📝 Translation to improve', langue: '✍️ Language mistake', source: '📚 Source / reference', pedagogie: '💡 Teaching suggestion' },
          seif: 'Seif concerned (optional)', desc: 'Describe the problem *', src: 'Correct source, if you know it (optional)',
          send: 'Send', cancel: 'Cancel', ok: '✓ Thank you! Your report was sent.', err: 'Could not send: ' },
  }[pageLang()];
  var rtl = pageLang() === 'he';

  function track() {
    try {
      window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
      window.va('event', { name: 'correction_submitted', data: { siman: simanM ? simanM[1] : '' } });
    } catch (_) {}
  }

  var link = document.createElement('button');
  link.id = 'daat-report-link';
  link.type = 'button';
  link.textContent = L.link;

  var typesOpts = '';
  for (var k in L.types) typesOpts += '<option value="' + k + '">' + L.types[k] + '</option>';

  var overlay = document.createElement('div');
  overlay.id = 'daat-report-overlay';
  overlay.innerHTML =
    '<div id="daat-report-modal"' + (rtl ? ' dir="rtl"' : '') + '>' +
    '<h3>' + L.title + '</h3>' +
    '<p class="dr-intro">' + L.intro + '</p>' +
    '<label>' + L.type + '<select id="dr-type">' + typesOpts + '</select></label>' +
    '<label>' + L.seif + '<input id="dr-seif" type="text" maxlength="20"></label>' +
    '<label>' + L.desc + '<textarea id="dr-desc" rows="4" maxlength="2000"></textarea></label>' +
    '<label>' + L.src + '<input id="dr-src" type="text" maxlength="300"></label>' +
    '<input id="dr-hp" type="text" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;" aria-hidden="true">' +
    '<div class="dr-row"><button type="button" id="dr-cancel" class="dr-btn dr-ghost">' + L.cancel + '</button>' +
    '<button type="button" id="dr-send" class="dr-btn dr-gold">' + L.send + '</button></div>' +
    '<div id="dr-msg" role="status"></div>' +
    '</div>';

  function openModal() { document.body.appendChild(overlay); }
  function closeModal() { if (overlay.parentNode) overlay.parentNode.removeChild(overlay); }
  link.addEventListener('click', openModal);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });

  overlay.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'dr-cancel') closeModal();
    if (e.target && e.target.id === 'dr-send') {
      var msg = overlay.querySelector('#dr-msg');
      var desc = overlay.querySelector('#dr-desc').value.trim();
      if (desc.length < 10) { msg.textContent = L.desc.replace(' *', '') + ' (min. 10)'; msg.style.color = '#a33'; return; }
      var canon = document.querySelector('link[rel="canonical"]');
      var payload = {
        url: canon && canon.href ? canon.href : location.href,
        titre: (document.title || '').slice(0, 200),
        siman: simanM ? simanM[1] : '',
        seif: overlay.querySelector('#dr-seif').value,
        type: overlay.querySelector('#dr-type').value,
        description: desc,
        source: overlay.querySelector('#dr-src').value,
        lang: pageLang(),
        hp: overlay.querySelector('#dr-hp').value,
      };
      e.target.disabled = true;
      fetch('https://daatai.vercel.app/api/signalement', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (d && d.ok) { track(); msg.textContent = L.ok; msg.style.color = '#2d7a3e'; setTimeout(closeModal, 1800); }
        else { msg.textContent = L.err + (d && d.error || '?'); msg.style.color = '#a33'; e.target.disabled = false; }
      }).catch(function () { msg.textContent = L.err + 'réseau'; msg.style.color = '#a33'; e.target.disabled = false; });
    }
  });

  var css = '#daat-report-link{position:fixed;bottom:70px;left:24px;z-index:9989;background:rgba(255,255,255,.92);'
    + 'border:1px solid rgba(197,165,90,.55);color:#7a6428;font-family:Inter,system-ui,sans-serif;font-size:11px;'
    + 'letter-spacing:.4px;padding:5px 11px;border-radius:14px;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.08);}'
    + '#daat-report-link:hover{background:#fff;color:#1A1F3A;border-color:#C5A55A;}'
    + '#daat-report-overlay{position:fixed;inset:0;background:rgba(26,31,58,.55);z-index:10001;display:flex;align-items:center;justify-content:center;padding:16px;}'
    + '#daat-report-modal{background:#FAF6EE;max-width:430px;width:100%;padding:26px;border-top:3px solid #C5A55A;border-radius:4px;font-family:Inter,system-ui,sans-serif;max-height:92vh;overflow:auto;}'
    + '#daat-report-modal h3{font-family:"Cormorant Garamond",Georgia,serif;font-size:22px;color:#1A1F3A;margin:0 0 6px;}'
    + '#daat-report-modal .dr-intro{font-size:12.5px;color:#6a6a75;line-height:1.5;margin:0 0 14px;}'
    + '#daat-report-modal label{display:block;font-size:11px;letter-spacing:.5px;text-transform:uppercase;color:#8a8578;margin:10px 0 3px;}'
    + '#daat-report-modal select,#daat-report-modal input[type=text],#daat-report-modal textarea{width:100%;box-sizing:border-box;'
    + 'padding:9px 10px;border:1px solid #e7ddc9;border-radius:3px;background:#fff;font-family:inherit;font-size:14px;color:#1A1F3A;margin-top:3px;}'
    + '#daat-report-modal textarea{resize:vertical;}'
    + '#daat-report-modal .dr-row{display:flex;gap:10px;justify-content:flex-end;margin-top:16px;}'
    + '#daat-report-modal .dr-btn{padding:10px 20px;font-size:12px;font-weight:600;letter-spacing:1px;border-radius:3px;cursor:pointer;border:none;}'
    + '#daat-report-modal .dr-gold{background:#C5A55A;color:#1A1F3A;}'
    + '#daat-report-modal .dr-ghost{background:transparent;border:1px solid #cfc6b2;color:#6a6a75;}'
    + '#daat-report-modal #dr-msg{margin-top:10px;font-size:13px;}'
    + '@media (max-width:640px){#daat-report-link{bottom:62px;left:16px;font-size:10px;}}'
    + '@media print{#daat-report-link{display:none!important;}}';
  var style = document.createElement('style');
  style.appendChild(document.createTextNode(css));

  function mount() { document.head.appendChild(style); document.body.appendChild(link); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
