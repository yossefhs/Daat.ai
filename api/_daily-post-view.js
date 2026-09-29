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
/* ---- visuel 1080×1350 ---- */
.ig{font-variant-numeric:lining-nums;width:1080px;height:1350px;background:radial-gradient(circle at 80% 0%,#243066 0%,var(--navy) 55%);color:var(--cream);font-family:'Source Sans 3',sans-serif;display:flex;flex-direction:column;overflow:hidden}
.ig .hero{position:relative;height:452px;flex:none;background-size:cover;background-position:center;background-color:#1b2450}
.ig .hero::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(14,22,51,.96) 0%,rgba(14,22,51,.72) 42%,rgba(14,22,51,.15) 78%),linear-gradient(0deg,var(--navy) 0%,rgba(14,22,51,0) 38%)}
.ig .hero>*{position:relative;z-index:1}
.ig .panel{position:absolute;top:34px;left:38px;border:2px solid var(--gold);border-radius:20px;padding:16px 22px;background:rgba(14,22,51,.72);min-width:420px}
.ig .date{font:700 34px/1.1 'Cormorant Garamond',Georgia,serif;color:var(--gold2);letter-spacing:.02em;text-transform:uppercase}
.ig .meta{display:flex;gap:16px;align-items:center;font:700 21px 'Source Sans 3',sans-serif;letter-spacing:.06em;margin-top:8px;white-space:nowrap}
.ig .meta i{width:2px;height:22px;background:var(--gold);display:inline-block}
.ig .pill{margin-top:12px;background:var(--cream);color:var(--navy2);border-radius:12px;padding:8px 16px;text-align:center}
.ig .pill b{display:block;font:700 31px 'Cormorant Garamond',Georgia,serif;white-space:nowrap}
.ig .pill .he{font-family:'Frank Ruhl Libre',serif;font-weight:700}
.ig .pill .sf{display:block;font:700 17px 'Source Sans 3',sans-serif;letter-spacing:.1em;margin-top:2px}
.ig .brand{position:absolute;top:30px;right:40px;text-align:right}
.ig .brand b{font:700 50px/1 'Cormorant Garamond',Georgia,serif;color:var(--cream)} .ig .brand b em{font-style:normal;color:var(--gold2)}
.ig .brand small{display:block;font:italic 19px 'Cormorant Garamond',Georgia,serif;color:var(--cream);margin-top:4px}
.ig .title{position:absolute;left:38px;right:38px;bottom:18px}
.ig .title h2{margin:0;font:700 56px/1.02 'Cormorant Garamond',Georgia,serif;color:var(--gold2);text-transform:uppercase;letter-spacing:.01em}
.ig .title p{margin:6px 0 0;font:700 36px/1.05 'Cormorant Garamond',Georgia,serif;color:var(--cream);text-transform:uppercase}
.ig .cards{flex:1;display:flex;flex-direction:column;gap:11px;padding:6px 30px 0}
.ig .card{flex:1;display:flex;background:var(--cream);border:2px solid var(--gold);border-radius:18px;overflow:hidden;color:var(--ink);min-height:0}
.ig .thumb{position:relative;width:210px;flex:none;background-size:cover;background-position:center;background-color:#d9ccb0}
.ig .num{position:absolute;top:10px;left:10px;width:58px;height:58px;border-radius:50%;background:linear-gradient(145deg,#E2C77F,#A8883E);border:3px solid var(--cream);display:flex;align-items:center;justify-content:center;font:700 32px 'Cormorant Garamond',Georgia,serif;color:var(--navy2)}
.ig .body{padding:12px 18px 10px;display:flex;flex-direction:column;justify-content:center;min-width:0}
.ig .body h3{margin:0 0 5px;font:700 25px/1.1 'Cormorant Garamond',Georgia,serif;color:var(--navy2);text-transform:uppercase}
.ig .body ul{margin:0;padding-left:20px;font-size:18.5px;line-height:1.3}
.ig .body li{margin:2px 0} .ig .body li::marker{color:var(--gold)}
.ig .retenir{margin:12px 30px 0;display:flex;align-items:stretch;background:var(--cream);color:var(--ink);border:2px solid var(--gold);border-radius:18px;min-height:112px}
.ig .retenir .lab{flex:none;display:flex;align-items:center;justify-content:center;width:170px;font:700 26px/1.05 'Cormorant Garamond',Georgia,serif;text-align:center;color:var(--navy2);border-right:2px solid var(--gold);padding:0 10px}
.ig .memo{flex:1;padding:12px 14px;border-left:1px solid rgba(197,165,90,.6);display:flex;flex-direction:column;justify-content:center;font-size:17px;line-height:1.2}
.ig .memo:first-of-type{border-left:0} .ig .memo b{font-size:17.5px;color:var(--navy2)}
.ig .foot{display:flex;align-items:center;gap:18px;padding:14px 30px 20px}
.ig .foot .study{font:700 17px 'Source Sans 3',sans-serif;letter-spacing:.1em}
.ig .foot .url{background:linear-gradient(145deg,#E2C77F,#C5A55A);color:var(--navy2);font:700 22px 'Source Sans 3',sans-serif;border-radius:12px;padding:9px 18px}
.ig .foot .yh{margin-left:auto;text-align:center}
.ig .foot .yh b{display:inline-flex;align-items:center;justify-content:center;width:62px;height:62px;border-radius:50%;border:3px solid var(--gold);font:700 26px 'Cormorant Garamond',Georgia,serif;color:var(--gold2)}
.ig .foot .yh small{display:block;font-size:13px;margin-top:3px}
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

  function renderVisual() {
    const n = post.seifim.length;
    const lot = info.lotTotal > 1 ? ` (${info.lotIndex}/${info.lotTotal})` : '';
    const cards = post.seifim.map((s) => `
      <div class="card"><div class="thumb" style="${imgs['s' + s.n] ? `background-image:url('${imgs['s' + s.n]}')` : ''}"><div class="num">${s.n}</div></div>
      <div class="body"><h3 contenteditable="true">${esc(s.titre)}</h3><ul>${s.points.map((p) => `<li contenteditable="true">${esc(p)}</li>`).join('')}</ul></div></div>`).join('');
    const memos = (post.a_retenir || []).slice(0, 4).map((m) => `<div class="memo"><b contenteditable="true">${esc(m.label)}</b><span contenteditable="true">${esc(m.texte)}</span></div>`).join('');
    $('ig').innerHTML = `
      <div class="hero" style="${imgs.hero ? `background-image:url('${imgs.hero}')` : ''}">
        <div class="panel"><div class="date">${esc(info.jourSemaine)} ${esc(info.dateCourte)}</div>
          <div class="meta"><span>SEMAINE ${info.semaine}</span><i></i><span>JOUR ${info.dayNumber}${info.totalDays ? '/' + info.totalDays : ''}</span></div>
          <div class="pill"><b>Siman ${info.siman.num} • <bdi class="he" dir="rtl">${esc(info.siman.numHe)}</bdi></b><span class="sf">SÉ’IFIM ${info.seifRange[0]}–${info.seifRange[1]}${lot}</span></div></div>
        <div class="brand"><b>Daat<em>Torah</em></b><small>Étude et compréhension</small></div>
        <div class="title"><h2 contenteditable="true">${esc(post.titre)}</h2><p contenteditable="true">${esc(post.sous_titre)}</p></div>
      </div>
      <div class="cards" style="${n <= 3 ? 'gap:16px' : ''}">${cards}</div>
      <div class="retenir"><div class="lab">À RETENIR</div>${memos}</div>
      <div class="foot"><span class="study">ÉTUDE COMPLÈTE SUR DAATTORAH</span><span class="url">daattorah.com/oh/${info.siman.num}/base</span>
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
