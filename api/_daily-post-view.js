// api/_daily-post-view.js — Page de validation du post quotidien.
//
// Ouverte depuis l'email du matin. Montre le visuel composé (1080×1350, format
// Instagram), le verdict de vérification, les textes de chaque réseau (modifiables),
// et deux actions : « Publier partout » et « Partager sur WhatsApp ».
//
// Le visuel est composé EN HTML dans le navigateur, puis exporté en JPEG au clic :
// tous les mots (titres, hébreu, lien) sont posés par la page, les illustrations
// OpenAI ne portent aucun texte. Le navigateur gère l'hébreu et le sens de lecture
// correctement, ce qu'aucun moteur de rendu serveur léger ne garantit.

export function renderReviewPage(data) {
  const json = JSON.stringify(data).replace(/</g, '\\u003c');
  return `<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Daat Yomi · validation du ${data.info?.dateCourte || ''}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" crossorigin="anonymous" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Frank+Ruhl+Libre:wght@500;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap">
<style>${CSS}</style></head>
<body>
<main class="wrap">
  <header class="top">
    <p class="eyebrow">Daat Yomi · validation</p>
    <h1 id="h-title">Post du jour</h1>
    <p id="h-sub" class="muted"></p>
  </header>
  <section id="verdict" class="verdict pending"><strong>Vérification en cours…</strong></section>
  <div class="layout">
    <section class="col-visual">
      <div id="stage" class="stage"><div id="ig" class="ig"></div></div>
      <p class="muted small">Tu peux corriger un texte du visuel en cliquant dessus avant de publier.</p>
      <div class="actions">
        <button id="b-publish" class="btn primary" type="button">Publier partout</button>
        <button id="b-wa" class="btn" type="button">Partager sur WhatsApp</button>
      </div>
      <div class="actions small-actions">
        <button id="b-img" class="btn ghost" type="button">Refaire les illustrations</button>
        <button id="b-text" class="btn ghost" type="button">Refaire le texte</button>
      </div>
      <div id="results" class="results"></div>
    </section>
    <section class="col-texts">
      <h2>Textes par réseau</h2>
      <p class="muted small">Modifiables : c'est la version affichée ici qui sera publiée.</p>
      <div id="texts"></div>
    </section>
  </div>
</main>
<script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
<script>window.__DP__=${json};</script>
<script>(${clientMain.toString()})();</script>
</body></html>`;
}

const CSS = `
:root{--navy:#0E1633;--navy2:#1A1F3A;--gold:#C5A55A;--gold2:#E2C77F;--cream:#FAF6EE;--ink:#1A1F3A;--muted:#5B6078;--line:#E6DDC9;--ok:#2F6B45;--okbg:#E7F1EA;--warn:#8A5A12;--warnbg:#F8EEDB;--bad:#9B2F2F;--badbg:#F6E3E1}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);font:16px/1.55 'Source Sans 3',-apple-system,'Segoe UI',sans-serif}
.wrap{max-width:1240px;margin:0 auto;padding-inline:16px;padding-block:24px 60px}
.eyebrow{margin:0;font-size:.78rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:#A8883E}
h1{margin:4px 0 2px;font:700 2rem/1.15 'Cormorant Garamond',Georgia,serif}
h2{font:700 1.4rem 'Cormorant Garamond',Georgia,serif;margin:0 0 4px}
.muted{color:var(--muted)} .small{font-size:.88rem}
.verdict{margin:18px 0;padding:14px 16px;border-radius:10px;border:1px solid var(--line);background:#fff}
.verdict.vert{background:var(--okbg);color:var(--ok);border-color:transparent}
.verdict.orange{background:var(--warnbg);color:var(--warn);border-color:transparent}
.verdict.rouge{background:var(--badbg);color:var(--bad);border-color:transparent}
.verdict ul{margin:8px 0 0;padding-left:18px} .verdict li{margin-bottom:6px;color:var(--ink)}
.layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start}
@media (max-width:900px){.layout{grid-template-columns:1fr}}
.stage{width:100%;aspect-ratio:1080/1350;position:relative;overflow:hidden;border-radius:10px;box-shadow:0 6px 24px rgba(14,22,51,.25);background:var(--navy)}
.stage .ig{position:absolute;top:0;left:0;transform-origin:top left}
.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
.btn{font:700 1rem 'Source Sans 3',sans-serif;padding:12px 18px;border-radius:9px;border:1.5px solid var(--gold);background:#fff;color:var(--ink);cursor:pointer}
.btn.primary{background:var(--gold);color:var(--navy2)} .btn.ghost{font-size:.9rem;padding:8px 12px}
.btn:disabled{opacity:.55;cursor:wait} .btn:focus-visible{outline:2px solid var(--navy2);outline-offset:2px}
.results{margin-top:14px;display:grid;gap:6px}
.res{padding:8px 12px;border-radius:8px;font-size:.92rem}
.res.ok{background:var(--okbg);color:var(--ok)} .res.ko{background:var(--badbg);color:var(--bad)} .res.info{background:#fff;border:1px solid var(--line)}
.net{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-top:12px}
.net-h{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:6px}
.net-h strong{font:700 1.05rem 'Cormorant Garamond',Georgia,serif}
.net textarea{width:100%;min-height:150px;font:14.5px/1.5 'Source Sans 3',sans-serif;border:1px solid var(--line);border-radius:8px;padding:10px;resize:vertical;color:var(--ink);background:#FFFDF8}
.count{font-size:.8rem;color:var(--muted)}
/* ---- visuel 1080×1350 : navy profond, or en relief, cartes crème encadrées ---- */
.ig{font-variant-numeric:lining-nums;width:1080px;height:1350px;position:relative;color:var(--cream);font-family:'Source Sans 3',sans-serif;display:flex;flex-direction:column;overflow:hidden;
  background:radial-gradient(ellipse at 50% 38%,#1d2a63 0%,#101a3f 45%,#080d24 100%)}
.ig::before{content:'';position:absolute;inset:0;pointer-events:none;background:
  radial-gradient(circle at 0 100%,rgba(197,165,90,.16),transparent 30%),radial-gradient(circle at 100% 100%,rgba(197,165,90,.16),transparent 30%)}
.ig .frame{position:absolute;inset:12px;border:2px solid rgba(197,165,90,.55);border-radius:26px;pointer-events:none;z-index:3}
.ig .frame::after{content:'';position:absolute;inset:6px;border:1px solid rgba(197,165,90,.28);border-radius:20px}
.ig .hero{position:relative;height:462px;flex:none;background-size:cover;background-position:center 40%;background-color:#16204c}
.ig .hero::after{content:'';position:absolute;inset:0;background:
  linear-gradient(90deg,rgba(8,13,36,.94) 0%,rgba(8,13,36,.66) 36%,rgba(8,13,36,.05) 70%),
  linear-gradient(0deg,#101a3f 0%,rgba(16,26,63,.85) 22%,rgba(16,26,63,0) 52%),
  radial-gradient(ellipse at 72% 30%,rgba(255,196,110,.18),transparent 55%)}
.ig .hero>*{position:relative;z-index:2}
.ig .panel{position:absolute;top:40px;left:42px;display:flex;flex-direction:column;gap:12px}
.ig .datebox{display:flex;align-items:center;gap:14px;padding:10px 26px 10px 14px;border-radius:0 40px 40px 0;background:linear-gradient(90deg,#f3e6c4,#d9bf7e);color:var(--navy2);box-shadow:0 4px 18px rgba(0,0,0,.35)}
.ig .datebox svg{width:40px;height:40px;stroke:var(--navy2)}
.ig .datebox b{display:block;font:700 22px/1 'Source Sans 3',sans-serif;letter-spacing:.08em;text-transform:uppercase}
.ig .datebox span{display:block;font:700 34px/1.05 'Source Sans 3',sans-serif}
.ig .line{display:flex;align-items:center;gap:14px;font:700 25px 'Source Sans 3',sans-serif;letter-spacing:.04em;text-shadow:0 2px 8px rgba(0,0,0,.6);white-space:nowrap}
.ig .line svg{width:34px;height:34px;flex:none;stroke:var(--gold2)}
.ig .line .he{font-family:'Frank Ruhl Libre',serif;color:var(--gold2)}
.ig .brand{position:absolute;top:34px;right:46px;text-align:center}
.ig .brand svg{width:66px;height:44px;stroke:var(--gold2);display:block;margin:0 auto 2px}
.ig .brand b{font:700 54px/1 'Cormorant Garamond',Georgia,serif;color:#fff;text-shadow:0 2px 12px rgba(0,0,0,.6)} .ig .brand b em{font-style:normal;color:var(--gold2)}
.ig .brand small{display:block;font:600 19px 'Source Sans 3',sans-serif;color:#f5ecd6;margin-top:4px;text-shadow:0 2px 8px rgba(0,0,0,.7)}
.ig .title{position:absolute;left:30px;right:30px;bottom:14px;text-align:center}
.ig .title h2{margin:0;font:700 60px/1.02 'Cormorant Garamond',Georgia,serif;text-transform:uppercase;letter-spacing:.01em;
  background:linear-gradient(180deg,#fbe9b8 0%,#e2c77f 45%,#b58f3e 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 3px 6px rgba(0,0,0,.55))}
.ig .title p{margin:6px 0 0;font:700 38px/1.05 'Cormorant Garamond',Georgia,serif;color:#fff;text-transform:uppercase;text-shadow:0 3px 10px rgba(0,0,0,.6)}
.ig .orn{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:10px}
.ig .orn i{height:2px;width:230px;background:linear-gradient(90deg,transparent,var(--gold) 60%,var(--gold2))}
.ig .orn i:last-child{transform:scaleX(-1)} .ig .orn svg{width:46px;height:18px;fill:var(--gold2)}
.ig .cards{flex:1;min-height:0;display:flex;flex-direction:column;gap:10px;padding:6px 34px 0;position:relative;z-index:2}
.ig .card{flex:1;display:flex;min-height:0;border-radius:18px;padding:3px;background:linear-gradient(135deg,#f6e3a8,#b58f3e 40%,#f1d892 60%,#9c7a32);box-shadow:0 6px 16px rgba(0,0,0,.4)}
.ig .card-in{flex:1;display:flex;border-radius:15px;overflow:hidden;background:linear-gradient(180deg,#fffaf0,#f4ead3);color:var(--ink);min-width:0}
.ig .thumb{position:relative;width:215px;flex:none;background-size:cover;background-position:center;background-color:#cdbb92;box-shadow:inset -10px 0 14px -10px rgba(0,0,0,.45)}
.ig .num{position:absolute;top:8px;left:8px;width:64px;height:64px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at 35% 30%,#fff3c8 0%,#e2c77f 35%,#a8802f 100%);border:3px solid #fff7e0;box-shadow:0 3px 8px rgba(0,0,0,.45);
  font:700 36px 'Cormorant Garamond',Georgia,serif;color:var(--navy2)}
.ig .body{padding:8px 18px 8px 20px;display:flex;flex-direction:column;justify-content:center;min-width:0}
.ig .body h3{margin:0 0 4px;font:700 25px/1.05 'Cormorant Garamond',Georgia,serif;color:#1a2458;text-transform:uppercase;letter-spacing:.01em}
.ig .body ul{margin:0;padding-left:20px;font-size:18.5px;line-height:1.26;color:#232a45}
.ig.dense .body ul{font-size:17px} .ig.dense .body h3{font-size:23px} .ig.dense .num{width:56px;height:56px;font-size:31px}
.ig .body li{margin:1px 0} .ig .body li::marker{color:#b58f3e;font-size:1.2em} .ig .body strong{color:#101a3f}
.ig .retenir{position:relative;z-index:2;flex:none;margin:12px 34px 0;border-radius:20px;padding:3px;background:linear-gradient(135deg,#f6e3a8,#b58f3e 40%,#f1d892 60%,#9c7a32);box-shadow:0 6px 16px rgba(0,0,0,.4)}
.ig .retenir-in{display:flex;align-items:stretch;border-radius:17px;background:linear-gradient(180deg,#fffaf0,#f4ead3);color:var(--ink);min-height:100px}
.ig .retenir .lab{flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;width:175px;font:700 27px/1.05 'Cormorant Garamond',Georgia,serif;text-align:center;color:#1a2458;border-right:2px solid #c9a653;padding:0 10px}
.ig .retenir .lab svg{width:40px;height:40px;stroke:#b58f3e;margin-bottom:4px}
.ig .memo{flex:1;padding:8px 10px;border-left:1px solid rgba(181,143,62,.5);display:flex;align-items:center;gap:10px;font-size:17px;line-height:1.2;min-width:0}
.ig .memo:first-of-type{border-left:0} .ig .memo b{display:block;font-size:17.5px;color:#1a2458}
.ig .memo svg{width:38px;height:38px;flex:none;stroke:#b58f3e}
.ig .foot{position:relative;z-index:2;flex:none;display:flex;align-items:center;gap:18px;padding:12px 38px 24px}
.ig .foot .study{display:flex;align-items:center;gap:10px;font:700 18px 'Source Sans 3',sans-serif;letter-spacing:.1em}
.ig .foot .study svg{width:34px;height:34px;stroke:#f5ecd6}
.ig .foot .url{display:flex;align-items:center;gap:10px;background:linear-gradient(180deg,#f8e7b6,#d2b46c);color:var(--navy2);font:700 23px 'Source Sans 3',sans-serif;border-radius:14px;padding:10px 20px;box-shadow:0 3px 10px rgba(0,0,0,.4)}
.ig .foot .url svg{width:22px;height:22px;stroke:var(--navy2)}
.ig .foot .yh{margin-left:auto;text-align:center}
.ig .foot .yh b{display:inline-flex;align-items:center;justify-content:center;width:66px;height:66px;border-radius:50%;
  background:radial-gradient(circle at 35% 30%,#2a3570,#101a3f);border:3px solid var(--gold2);font:700 28px 'Cormorant Garamond',Georgia,serif;color:var(--gold2);box-shadow:0 0 14px rgba(226,199,127,.35)}
.ig .foot .yh small{display:block;font-size:13px;margin-top:3px;color:#f5ecd6}
.ig [contenteditable]:focus{outline:2px dashed var(--gold2);outline-offset:2px}
`;

// Code client, sérialisé dans la page (jamais exécuté côté serveur).
function clientMain() {
  const D = window.__DP__;
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const api = (action, extra) => `/api/daily-post?action=${action}&date=${D.date}&t=${D.token}${extra || ''}`;
  const imgs = {};
  const info = D.info; let post = D.post;

  $('h-title').textContent = post.titre;
  $('h-sub').textContent = `${info.dateFr} · Jour ${info.dayNumber}${info.totalDays ? '/' + info.totalDays : ''} · Siman ${info.siman.num} · séifim ${info.seifRange[0]}–${info.seifRange[1]}`;

  // Icônes au trait (dessinées ici : aucune dépendance, export fidèle).
  const P = {
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M7 14h2M11 14h2M15 14h2M7 17h2M11 17h2"/>',
    book: '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5M19 19v2H6"/>',
    scroll: '<path d="M6 4h11a3 3 0 0 1 0 6H9"/><path d="M6 4a3 3 0 0 0 0 6h3v8a3 3 0 0 1-3 3h11a3 3 0 0 0 3-3v-8"/>',
    list: '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    clock: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M5 4 3 6M19 4l2 2"/>',
    candle: '<path d="M12 3c1.5 2 1.5 3.5 0 5-1.5-1.5-1.5-3 0-5z"/><rect x="9" y="9" width="6" height="12" rx="1"/><path d="M6 21h12"/>',
    bread: '<path d="M5 11a4 4 0 0 1 4-6h6a4 4 0 0 1 4 6v8H5z"/><path d="M9 9l1 2M13 9l1 2"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9 7 7M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/>',
    wine: '<path d="M7 3h10l-1 6a4 4 0 0 1-8 0z"/><path d="M12 13v7M8 21h8"/>',
    water: '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/>',
    plate: '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="3.5"/>',
    alert: '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5v.5"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    bulb: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    link: '<path d="M14 4h6v6M20 4 10 14M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
  };
  const icon = (k) => `<svg viewBox="0 0 24 24" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${P[k] || P.check}</svg>`;
  // **mot** → gras (le reste est échappé)
  const rich = (t) => esc(t).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  function renderVisual() {
    const n = post.seifim.length;
    const lot = info.lotTotal > 1 ? ` (${info.lotIndex}/${info.lotTotal})` : '';
    const cards = post.seifim.map((s) => `
      <div class="card"><div class="card-in"><div class="thumb" style="${imgs['s' + s.n] ? `background-image:url('${imgs['s' + s.n]}')` : ''}"><div class="num">${s.n}</div></div>
      <div class="body"><h3 contenteditable="true">${esc(s.titre)}</h3><ul>${s.points.map((p) => `<li contenteditable="true">${rich(p)}</li>`).join('')}</ul></div></div></div>`).join('');
    const memos = (post.a_retenir || []).slice(0, 4).map((m) => `<div class="memo">${icon(m.icone)}<div><b contenteditable="true">${esc(m.label)}</b><span contenteditable="true">${esc(m.texte)}</span></div></div>`).join('');
    $('ig').className = 'ig' + (n >= 5 ? ' dense' : '');
    $('ig').innerHTML = `<div class="frame"></div>
      <div class="hero" style="${imgs.hero ? `background-image:url('${imgs.hero}')` : ''}">
        <div class="panel">
          <div class="datebox">${icon('calendar')}<div><b>${esc(info.jourSemaine)}</b><span>${esc(info.dateCourte)}</span></div></div>
          <div class="line">${icon('book')}SEMAINE ${info.semaine}</div>
          <div class="line">${icon('list')}JOUR ${info.dayNumber}${info.totalDays ? '/' + info.totalDays : ''}</div>
          <div class="line">${icon('scroll')}Siman ${info.siman.num} • <bdi class="he" dir="rtl">${esc(info.siman.numHe)}</bdi></div>
          <div class="line">${icon('list')}SÉ’IFIM ${info.seifRange[0]}–${info.seifRange[1]}${lot}</div>
        </div>
        <div class="brand">${icon('book')}<b>Daat<em>Torah</em></b><small>Étude et compréhension</small></div>
        <div class="title"><h2 contenteditable="true">${esc(post.titre)}</h2><p contenteditable="true">${esc(post.sous_titre)}</p>
          <div class="orn"><i></i><svg viewBox="0 0 46 18"><path d="M23 1 27 9 23 17 19 9zM4 9a3 3 0 1 0 6 0 3 3 0 1 0-6 0M36 9a3 3 0 1 0 6 0 3 3 0 1 0-6 0"/></svg><i></i></div></div>
      </div>
      <div class="cards" style="${n <= 3 ? 'gap:18px' : ''}">${cards}</div>
      <div class="retenir"><div class="retenir-in"><div class="lab">${icon('bulb')}À RETENIR</div>${memos}</div></div>
      <div class="foot"><span class="study">${icon('book')}ÉTUDE COMPLÈTE SUR DAATTORAH</span><span class="url">daattorah.com/oh/${info.siman.num}/base ${icon('link')}</span>
        <div class="yh"><b>YH</b><small>Tous droits réservés</small></div></div>`;
    fit();
  }
  function fit() { const st = $('stage'); $('ig').style.transform = `scale(${st.clientWidth / 1080})`; }
  window.addEventListener('resize', fit);

  function renderTexts() {
    const nets = [['whatsapp', 'WhatsApp'], ['facebook', 'Facebook'], ['instagram', 'Instagram'], ['linkedin', 'LinkedIn'], ['x', 'X']];
    $('texts').innerHTML = nets.map(([k, label]) => `
      <div class="net"><div class="net-h"><strong>${label}</strong><span><span class="count" id="c-${k}"></span>
      <button class="btn ghost" type="button" data-copy="${k}">Copier</button></span></div>
      <textarea id="t-${k}" aria-label="Texte ${label}">${esc(post.posts[k])}</textarea></div>`).join('') +
      `<div class="net"><div class="net-h"><strong>Hashtags</strong></div><textarea id="t-tags" style="min-height:60px">${esc((post.hashtags || []).join(' '))}</textarea></div>`;
    const count = (k) => { const el = $('c-' + k); if (el) el.textContent = $('t-' + k).value.length + ' car.'; };
    nets.forEach(([k]) => { count(k); $('t-' + k).addEventListener('input', () => count(k)); });
    document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', () => {
      const ta = $('t-' + b.dataset.copy);
      navigator.clipboard.writeText(ta.value).then(() => { b.textContent = 'Copié'; setTimeout(() => (b.textContent = 'Copier'), 1500); },
        () => { ta.select(); });
    }));
  }
  function editedPosts() {
    const p = {}; ['whatsapp', 'facebook', 'instagram', 'linkedin', 'x'].forEach((k) => (p[k] = $('t-' + k).value));
    return { posts: p, hashtags: $('t-tags').value.split(/\s+/).filter(Boolean) };
  }

  function renderVerdict(v) {
    const el = $('verdict');
    if (!v) { el.className = 'verdict pending'; el.innerHTML = '<strong>Vérification en cours…</strong>'; return; }
    el.className = 'verdict ' + v.global;
    const head = { vert: '✅ Vérifié contre le Choul’han Aroukh : rien à signaler.', orange: '⚠️ À relire : imprécisions relevées.', rouge: '⛔ Erreur de fond relevée : corrige avant de publier.' }[v.global];
    el.innerHTML = `<strong>${head}</strong>${v.nb_affirmations_verifiees ? ` <span class="small">(${v.nb_affirmations_verifiees} affirmations confrontées)</span>` : ''}` +
      (v.points && v.points.length ? `<ul>${v.points.map((p) => `<li><strong>${esc(p.ou)} · ${esc(p.statut)}</strong> — « ${esc(p.affirmation)} » : ${esc(p.explication)}</li>`).join('')}</ul>` : '');
  }

  function showResults(r) {
    $('results').innerHTML = Object.entries(r || {}).map(([k, v]) =>
      `<div class="res ${v.ok ? 'ok' : 'ko'}">${esc(k)} : ${v.ok ? 'publié' : 'échec — ' + esc(v.error)}</div>`).join('') ||
      (D.platforms.length ? '' : '<div class="res info">Aucun réseau n’est encore branché : la publication automatique s’activera dès que les connexions seront faites. Le partage WhatsApp fonctionne déjà.</div>');
  }

  async function loadImages(force) {
    if (!D.imagesEnabled) return;
    await Promise.all(D.slots.map(async (slot) => {
      try {
        const r = await fetch(api(force ? 'regen-img' : 'img', `&slot=${slot}`), { method: force ? 'POST' : 'GET' });
        const d = await r.json();
        if (d.dataUrl) { imgs[slot] = d.dataUrl; renderVisual(); }
      } catch (e) { /* le visuel garde son fond sobre */ }
    }));
  }

  // Polices intégrées en data: URL — sans elles, l'image exportée retombe sur des
  // polices de secours plus larges, et le texte déborde de ses cartes.
  let fontCss = null;
  async function embedFonts() {
    if (fontCss !== null) return fontCss;
    try {
      const link = document.querySelector('link[href*="fonts.googleapis.com/css2"]');
      let css = await (await fetch(link.href)).text();
      const urls = [...new Set(css.match(/https:[^)'"]+\.woff2/g) || [])];
      for (const u of urls) {
        const blob = await (await fetch(u)).blob();
        const data = await new Promise((ok) => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.readAsDataURL(blob); });
        css = css.split(u).join(data);
      }
      fontCss = css;
    } catch (e) { fontCss = ''; }
    return fontCss;
  }
  async function exportJpeg() {
    const node = $('ig');
    await document.fonts.ready;
    const fontEmbedCSS = await embedFonts();
    return window.htmlToImage.toJpeg(node, { quality: 0.9, width: 1080, height: 1350, pixelRatio: 1,
      style: { transform: 'none' }, cacheBust: true, ...(fontEmbedCSS ? { fontEmbedCSS } : {}) });
  }

  $('b-publish').addEventListener('click', async () => {
    const b = $('b-publish');
    if (D.verify && D.verify.global === 'rouge' &&
      !window.confirm('La vérification a relevé une erreur de fond. Publier quand même ?')) return;
    b.disabled = true; b.textContent = 'Publication…';
    try {
      const jpeg = await exportJpeg();
      const r = await fetch(api('publish'), { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jpeg: jpeg.split(',')[1], ...editedPosts() }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.error || 'HTTP ' + r.status);
      showResults(d.results);
      b.textContent = 'Publié';
    } catch (e) { $('results').innerHTML = `<div class="res ko">Échec : ${esc(e.message)}</div>`; b.disabled = false; b.textContent = 'Publier partout'; }
  });

  $('b-wa').addEventListener('click', async () => {
    const text = $('t-whatsapp').value;
    try {
      const jpeg = await exportJpeg();
      const blob = await (await fetch(jpeg)).blob();
      const file = new File([blob], `daat-yomi-${D.date}.jpg`, { type: 'image/jpeg' });
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({ files: [file], text });
        return;
      }
      const a = document.createElement('a'); a.href = jpeg; a.download = file.name; a.click();
      await navigator.clipboard.writeText(text).catch(() => {});
      $('results').innerHTML = '<div class="res info">Image téléchargée et texte copié : colle-les dans WhatsApp.</div>';
    } catch (e) { if (e.name !== 'AbortError') $('results').innerHTML = `<div class="res ko">${esc(e.message)}</div>`; }
  });

  $('b-img').addEventListener('click', async () => {
    const b = $('b-img'); b.disabled = true; b.textContent = 'Illustrations en cours…';
    await loadImages(true); b.disabled = false; b.textContent = 'Refaire les illustrations';
  });
  $('b-text').addEventListener('click', async () => {
    const b = $('b-text'); b.disabled = true; b.textContent = 'Rédaction en cours (≈1 min)…';
    try {
      const r = await fetch(api('regen-text'), { method: 'POST' }); const d = await r.json();
      if (!r.ok) throw new Error(d.error || 'HTTP ' + r.status);
      location.reload();
    } catch (e) { b.disabled = false; b.textContent = 'Refaire le texte'; $('results').innerHTML = `<div class="res ko">${esc(e.message)}</div>`; }
  });

  renderVisual(); renderTexts(); renderVerdict(D.verify); showResults(D.published);
  loadImages(false);
  if (!D.verify && !D.preview) {
    fetch(api('verify'), { method: 'POST' }).then((r) => r.json()).then((v) => { D.verify = v.verdict; renderVerdict(v.verdict); }).catch(() => {});
  }
}
