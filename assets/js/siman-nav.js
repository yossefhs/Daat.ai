// Navigation entre simanim — bouton précédent / suivant
// Auto-détecte le siman courant depuis l'URL, calcule prev/next dans la liste
// des simanim disponibles, et injecte la nav avant <footer> (ou en fin de <body>).

(function () {
  'use strict';

  // Liste triée des simanim disponibles (124 simanim, 242 → 365 contigus).
  // À régénérer depuis data/simanim-disponibles.json si la liste change.
  const SIMANIM = [242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365];

  // Détecte siman + niveau depuis l'URL.
  // Routes possibles (cf. vercel.json) :
  //   /oh/242              → siman=242, level=""        (index)
  //   /oh/242/             → idem
  //   /oh/242/base         → niveau-1-base
  //   /oh/242/lamdan       → niveau-2-lamdan
  //   /oh/242/synthese     → niveau-3-synthese
  //   /oh/242/daat-harav   → niveau-4-daat-harav
  // Fallback (preview ou accès direct) :
  //   /sources/shabbat/siman-242/index.html
  //   /sources/shabbat/siman-242/niveau-1-base.html (etc.)
  function detect() {
    const p = location.pathname;
    let m = p.match(/^\/oh\/(\d+)(?:\/(base|lamdan|synthese|daat-harav))?\/?$/);
    if (m) return { siman: +m[1], level: m[2] || '' };
    m = p.match(/\/siman-(\d+)\/([^/]+)$/);
    if (m) {
      const n = +m[1];
      const f = m[2];
      if (f.startsWith('niveau-1')) return { siman: n, level: 'base' };
      if (f.startsWith('niveau-2')) return { siman: n, level: 'lamdan' };
      if (f.startsWith('niveau-3')) return { siman: n, level: 'synthese' };
      if (f.startsWith('niveau-4')) return { siman: n, level: 'daat-harav' };
      return { siman: n, level: '' };
    }
    return null;
  }

  const ctx = detect();
  if (!ctx) return;

  const idx = SIMANIM.indexOf(ctx.siman);
  if (idx === -1) return;

  const prev = idx > 0 ? SIMANIM[idx - 1] : null;
  const next = idx < SIMANIM.length - 1 ? SIMANIM[idx + 1] : null;

  const url = (n) => ctx.level ? `/oh/${n}/${ctx.level}` : `/oh/${n}/`;

  // Construction de la nav (styles inline pour éviter une dépendance CSS).
  const nav = document.createElement('nav');
  nav.setAttribute('aria-label', 'Navigation entre simanim');
  nav.style.cssText = [
    'display:flex',
    'justify-content:space-between',
    'align-items:center',
    'gap:16px',
    'max-width:1100px',
    'margin:48px auto 24px',
    'padding:20px 32px',
    'border-top:1px solid #e6dccb',
    'border-bottom:1px solid #e6dccb',
    'font-family:\'Inter\',sans-serif',
    'font-size:14px'
  ].join(';');

  const btnStyle = [
    'display:inline-flex',
    'align-items:center',
    'gap:8px',
    'padding:10px 18px',
    'background:#143C5C',
    'color:#fff',
    'text-decoration:none',
    'border-radius:2px',
    'font-weight:600',
    'letter-spacing:0.5px',
    'transition:background 0.2s'
  ].join(';');

  const emptyStyle = 'visibility:hidden;padding:10px 18px';

  function link(n, label) {
    const a = document.createElement('a');
    a.href = url(n);
    a.style.cssText = btnStyle;
    a.textContent = label;
    a.addEventListener('mouseenter', () => { a.style.background = '#C5A55A'; });
    a.addEventListener('mouseleave', () => { a.style.background = '#143C5C'; });
    return a;
  }

  function placeholder() {
    const s = document.createElement('span');
    s.style.cssText = emptyStyle;
    s.setAttribute('aria-hidden', 'true');
    s.textContent = ' ';
    return s;
  }

  nav.appendChild(prev ? link(prev, '← Siman ' + prev) : placeholder());

  const center = document.createElement('span');
  center.style.cssText = 'color:#7a6f5a;font-size:13px;letter-spacing:1px;text-transform:uppercase';
  center.textContent = 'Siman ' + ctx.siman + ' / ' + SIMANIM[SIMANIM.length - 1];
  nav.appendChild(center);

  nav.appendChild(next ? link(next, 'Siman ' + next + ' →') : placeholder());

  // Insertion : avant <footer> si présent, sinon en fin de <body>.
  const footer = document.querySelector('footer');
  if (footer && footer.parentNode) footer.parentNode.insertBefore(nav, footer);
  else document.body.appendChild(nav);
})();
