// Partage par section — ajoute un bouton 📤 sur chaque section d'étude
// (h2.section-title) d'une page de siman.
//
// Au clic : rassemble le texte de la section (titre + contenu jusqu'au
// prochain titre), puis le partage via l'API Web Share native (mobile) ou
// par copie dans le presse-papier (desktop). Le message inclut TOUJOURS le
// lien de la page + la signature du site, pour aider à la diffusion.
//
// Multilingue : la langue est déduite de <html lang>. Ne s'active que s'il y a
// des sections (sinon ne fait rien).
(function () {
  'use strict';

  var sections = document.querySelectorAll('h2.section-title');
  if (!sections.length) return;

  var SITE_URL = 'https://daattorah.com';
  var lang = (document.documentElement.lang || 'fr').slice(0, 2);
  var T = {
    fr: {
      title: 'Partager ce passage', aria: 'Partager ce passage',
      copied: 'Lien + texte copiés ✓', shared: 'Partagé ✓',
      fail: 'Copie échouée — sélectionne le texte manuellement',
      footer: '— Daat Torah · ' + SITE_URL + '\nÉtude halakhique en français · Choulhan Aroukh trilingue + assistant IA',
    },
    he: {
      title: 'שתף קטע זה', aria: 'שתף קטע זה',
      copied: 'הקישור והטקסט הועתקו ✓', shared: 'שותף ✓',
      fail: 'ההעתקה נכשלה — בחר את הטקסט ידנית',
      footer: '— דעת תורה · ' + SITE_URL + '\nלימוד הלכה רב-לשוני · שולחן ערוך עם עוזר בינה מלאכותית',
    },
    en: {
      title: 'Share this passage', aria: 'Share this passage',
      copied: 'Link + text copied ✓', shared: 'Shared ✓',
      fail: 'Copy failed — select the text manually',
      footer: '— Daat Torah · ' + SITE_URL + '\nMultilingual halacha study · Shulchan Aruch with AI assistant',
    },
  }[lang] || null;
  var i18n = T || {
    title: 'Partager', aria: 'Partager', copied: 'Copié ✓', shared: 'Partagé ✓',
    fail: 'Copie échouée', footer: '— Daat Torah · ' + SITE_URL,
  };

  // Éléments à ignorer dans le texte d'une section (navigation, boutons…).
  var SKIP = 'button, .daat-share-btn, .next-seif-nav, .seif-nav, .no-print, nav, script, style';

  function slugify(s, i) {
    var base = String(s || '').toLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-+|-+$/g, '').slice(0, 40);
    return 'sec-' + (base || i);
  }

  // Texte complet d'une section : titre + contenu jusqu'au prochain h2.section-title.
  function buildText(h2) {
    var titleClone = h2.cloneNode(true);
    titleClone.querySelectorAll('.daat-share-btn').forEach(function (b) { b.remove(); });
    var parts = [titleClone.textContent.trim().replace(/\s+/g, ' ')];
    var el = h2.nextElementSibling;
    while (el && !(el.matches && el.matches('h2.section-title'))) {
      if (!(el.matches && el.matches(SKIP))) {
        var t = (el.innerText || el.textContent || '').replace(/[ \t]+\n/g, '\n').trim();
        if (t) parts.push(t);
      }
      el = el.nextElementSibling;
    }
    return parts.join('\n\n');
  }

  // Petit toast de confirmation (réutilisé pour toutes les sections).
  var toast;
  function status(msg, ms) {
    if (!toast) {
      toast = document.createElement('div');
      toast.setAttribute('dir', lang === 'he' ? 'rtl' : 'ltr');
      toast.style.cssText = [
        'position:fixed', 'bottom:20px', 'left:50%', 'transform:translateX(-50%)',
        'background:#1a1a2e', 'color:#f5e9c8', 'border:1px solid #B8972A',
        'padding:10px 18px', 'border-radius:6px', 'font-size:0.95rem',
        'box-shadow:0 8px 30px rgba(0,0,0,0.25)', 'z-index:99999',
        'opacity:0', 'transition:opacity 0.2s', 'pointer-events:none', 'max-width:90vw',
      ].join(';');
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { toast.style.opacity = '0'; }, ms || 2500);
  }

  async function share(h2) {
    var url = location.origin + location.pathname + (h2.id ? '#' + h2.id : '');
    var body = buildText(h2);
    var text = body + '\n\n' + i18n.footer;

    if (navigator.share) {
      try {
        await navigator.share({ title: i18n.title, text: text, url: url });
        status(i18n.shared);
        return;
      } catch (err) {
        if (err && err.name === 'AbortError') return;
      }
    }
    // Pas de champ URL séparé pour le presse-papier : on inclut le lien dans le texte.
    var clip = body + '\n\n🔗 ' + url + '\n' + i18n.footer;
    try {
      await navigator.clipboard.writeText(clip);
      status(i18n.copied);
    } catch (err) {
      var ta = document.createElement('textarea');
      ta.value = clip;
      ta.style.cssText = 'position:fixed;opacity:0;';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); status(i18n.copied); }
      catch (e) { status(i18n.fail, 4000); }
      ta.remove();
    }
  }

  sections.forEach(function (h2, i) {
    if (!h2.id) h2.id = slugify(h2.textContent, i + 1);
    if (h2.querySelector('.daat-share-btn')) return; // idempotent

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'daat-share-btn';
    btn.setAttribute('aria-label', i18n.aria);
    btn.title = i18n.title;
    btn.textContent = '📤';
    btn.style.cssText = [
      'margin-inline-start:0.5em', 'border:1px solid rgba(184,151,42,0.5)',
      'background:transparent', 'color:#B8972A', 'cursor:pointer',
      'font-size:0.7em', 'line-height:1', 'padding:0.25em 0.45em',
      'border-radius:5px', 'vertical-align:middle', 'opacity:0.7',
      'transition:opacity 0.15s,background 0.15s',
    ].join(';');
    btn.addEventListener('mouseenter', function () { btn.style.opacity = '1'; btn.style.background = 'rgba(184,151,42,0.12)'; });
    btn.addEventListener('mouseleave', function () { btn.style.opacity = '0.7'; btn.style.background = 'transparent'; });
    btn.addEventListener('click', function (e) { e.preventDefault(); share(h2); });
    h2.appendChild(btn);
  });

  // Deep-link : si l'URL contient l'ancre d'une section (ajoutée ci-dessus),
  // on s'y rend en douceur après l'ajout des id.
  if (location.hash && location.hash.length > 1) {
    var target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (target) setTimeout(function () { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60);
  }
})();
