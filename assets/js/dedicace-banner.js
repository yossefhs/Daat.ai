// Bandeau de dédicaces — affiché en haut de chaque page de siman.
//
// Déduit le numéro de siman depuis l'URL (motif « siman-(\d+) »), interroge
// /api/dedicace/{N} et insère un bandeau hébreu (RTL) en tête du <body>.
// Le bandeau reste masqué (rien n'est inséré) s'il n'y a aucune dédicace,
// ou si l'API est injoignable — l'étude n'est jamais bloquée.
//
// Style : fond #1a1a2e, bordure or #B8972A, texte hébreu לעילוי נשמת /
// רפואה שלמה / להצלחה.
(function () {
  'use strict';

  // Déduit N depuis l'URL. Deux formes possibles :
  //   - canonique servie par les rewrites vercel.json : /oh/242, /oh/242/, /oh/242/base…
  //   - accès direct au fichier : /sources/shabbat/siman-242/index.html
  var path = location.pathname || '';
  var m = path.match(/siman-(\d+)/) || path.match(/\/oh\/(\d+)/);
  if (!m) return;
  var siman = m[1];
  var API = 'https://daatai.vercel.app/api/dedicace/' + siman;

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function build(dedicaces) {
    if (!dedicaces || !dedicaces.length) return; // masqué si aucune dédicace
    if (document.getElementById('dedicace-banner')) return; // idempotent

    var banner = document.createElement('div');
    banner.id = 'dedicace-banner';
    banner.setAttribute('dir', 'rtl');
    banner.setAttribute('lang', 'he');
    banner.setAttribute('role', 'note');
    banner.style.cssText = [
      'background:#1a1a2e',
      'color:#f5e9c8',
      'border-bottom:2px solid #B8972A',
      'padding:0.55rem 1rem',
      'text-align:center',
      'direction:rtl',
      'line-height:1.7',
      'font-family:"Frank Ruhl Libre","Times New Roman",serif',
      'font-size:1.05rem',
      'letter-spacing:0.01em'
    ].join(';');

    var items = dedicaces.slice(0, 6).map(function (d) {
      return '<span style="display:inline-block;margin:0 0.5rem;white-space:nowrap;">' +
               '<span style="color:#B8972A;font-weight:600;">' + esc(d.typeHe || '') + '</span> ' +
               '<span>' + esc(d.nom || '') + '</span>' +
             '</span>';
    }).join('<span style="color:#B8972A;opacity:.45;">·</span>');

    banner.innerHTML = items;

    var body = document.body;
    if (!body) return;
    if (body.firstChild) body.insertBefore(banner, body.firstChild);
    else body.appendChild(banner);
  }

  function load() {
    fetch(API, { headers: { 'Accept': 'application/json' } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (data && data.ok && Array.isArray(data.dedicaces)) build(data.dedicaces);
      })
      .catch(function () { /* silencieux */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
})();
