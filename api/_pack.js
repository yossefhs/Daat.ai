// api/_pack.js — « Pack du jour » DAAT : construction déterministe (zéro token IA).
//
// Un pack = 7 blocs prêts à copier-coller (accroche, LinkedIn, fil X/Bluesky,
// Instagram caption + carrousel, Facebook, message communauté, appel au soutien),
// pour UN siman, avec un angle qui tourne selon le jour et un appel au soutien
// en rotation (jamais deux fois le même d'affilée).
//
// L'enrichissement vient du corpus dérivé du site (data/corpus-shabbat.json) :
// sous-titre réel du siman + intitulés de sections → aucun contenu inventé.
// Consommé par api/daily-pack.js (page web) et scripts/pack-du-jour.js (CLI).

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { getSiman } from './_newsletter-weekly.js';
import { buildSocialPosts } from './_social-content.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

const SITE = 'https://daattorah.com';
export const LINKS = {
  whatsapp: 'https://chat.whatsapp.com/LQT3IMwjNiZEARC7lxqmv1',
  telegram: 'https://t.me/Daattorah_com',
  helloasso: 'https://www.helloasso.com/associations/association-hessed/formulaires/9',
  soutenir: `${SITE}/soutenir.html`,
  chat: `${SITE}/chat.html`,
};

const DIS = 'Pour la pratique, consulte ton Rav.';

// ---- enrichissement corpus (déterministe) ----
let _chunksBySiman = null;
function corpusFor(num) {
  if (!_chunksBySiman) {
    _chunksBySiman = new Map();
    try {
      const raw = readFileSync(join(__dirname, '..', 'data', 'corpus-shabbat.json'), 'utf-8');
      for (const c of JSON.parse(raw).chunks || []) {
        if (c.section !== 'orach-chaim') continue;
        const n = Number(c.siman);
        if (!_chunksBySiman.has(n)) _chunksBySiman.set(n, []);
        _chunksBySiman.get(n).push(c);
      }
    } catch (e) {
      console.warn('[pack] corpus indisponible :', e?.message);
    }
  }
  return _chunksBySiman.get(Number(num)) || [];
}

// Coupe proprement à la fin de phrase (ou au dernier mot avant `max`).
function firstSentence(text, max = 170) {
  const t = String(text || '').trim();
  if (!t) return '';
  const dot = t.indexOf('. ');
  if (dot > 20 && dot < max) return t.slice(0, dot + 1);
  if (t.length <= max) return /[.!?…]$/.test(t) ? t : '';
  const cut = t.slice(0, max);
  return cut.slice(0, cut.lastIndexOf(' ')) + '…';
}

// Sous-titre réel + intitulés de sections du siman (sans numérotation, sans génériques).
function enrichFor(num) {
  const chunks = corpusFor(num);
  const subtitle = firstSentence(chunks.find((c) => c.simanSubtitle)?.simanSubtitle);
  const seen = new Set();
  const concepts = [];
  for (const c of chunks) {
    const t = String(c.sectionTitle || '')
      .replace(/^\d+\.\s*/, '')
      .replace(/^concepts?-clés?\s*\d*\s*[—:–-]\s*/i, '')
      .trim();
    if (!t || seen.has(t)) continue;
    if (/^(introduction|le contexte général|conclusion|en bref|faq|sources?)$/i.test(t)) continue;
    if (/^le détail des?\b/i.test(t) || /^synthèse pratique\b/i.test(t)) continue;
    if (/^les concepts-clés\b/i.test(t) || /concepts?-clés? halakhiques?/i.test(t)) continue;
    seen.add(t);
    concepts.push(t);
    if (concepts.length >= 4) break;
  }
  return { subtitle, concepts };
}

// ---- 7 angles (un par jour de la semaine, 0 = dimanche) ----
export const ANGLES = [
  { key: 'question', label: 'La question concrète',
    hook: (e) => e.subtitle
      ? `Une question qu'on se pose vraiment : ${e.concepts[0] ? e.concepts[0].toLowerCase() : 'que faire en pratique ?'}`
      : `On se l'est tous déjà demandé un vendredi après-midi…` },
  { key: 'concept', label: 'Le mot juste',
    hook: (e) => e.concepts[0]
      ? `Un concept de la halakha à connaître précisément : « ${e.concepts[0]} ».`
      : `Un mot de la halakha que peu de gens savent définir précisément.` },
  { key: 'histoire', label: 'D\'où ça vient',
    hook: () => `Du Talmud au Choulhan Aroukh : la chaîne d'une même halakha.` },
  { key: 'nuance', label: 'La nuance qui change tout',
    hook: (e) => e.concepts[1]
      ? `Entre « ${e.concepts[0]} » et « ${e.concepts[1]} », une différence décisive.`
      : `Deux cas qui se ressemblent, une différence décisive.` },
  { key: 'pratique', label: 'Cas pratique',
    hook: (e) => e.subtitle || `Un cas réel du quotidien, éclairé par le siman.` },
  { key: 'quatre-niveaux', label: 'Les 4 niveaux',
    hook: () => `Du débutant au talmid hakham : le même siman, 4 profondeurs.` },
  { key: 'daat-harav', label: 'La chitah de l\'Admour HaZaken',
    hook: () => `Ce que le Choulhan Aroukh HaRav apporte de plus.` },
];

// ---- 5 appels au soutien en rotation (monétisation sans spam) ----
export const CTAS = [
  { key: 'dedicace',
    text: `🕯️ Tu peux dédier l'étude de ce siman — à la mémoire d'un proche (לעילוי נשמת), pour une refoua chéléma ou une réussite. Le nom apparaît sur la page, étudiée chaque jour dans le monde.\n👉 ${LINKS.soutenir}` },
  { key: 'don-18',
    text: `📚 18 € offrent une semaine d'étude accessible à tous, gratuitement. Si DAAT t'apporte, tu peux soutenir en un geste :\n👉 ${LINKS.helloasso}` },
  { key: 'mecenat',
    text: `🤝 Le mécénat mensuel (36 €/mois) fait vivre la plateforme et l'IA d'étude, gratuite pour tous. Rejoins les soutiens de DAAT :\n👉 ${LINKS.soutenir}` },
  { key: 'chat',
    text: `💬 Une question de halakha ? Le Chat Da'at te répond à partir du corpus du Rav, sources à l'appui — et gratuitement.\n👉 ${LINKS.chat}` },
  { key: 'newsletter',
    text: `✉️ Reçois « le siman du dimanche » : un siman par semaine, expliqué, dans ta boîte mail. Inscription en bas de ${SITE}` },
];

export const JOURS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];

// Construit le pack complet. `day` : 0 (dimanche) → 6 (samedi).
// `opts.yomi` (facultatif) : entrée Daat Yomi du jour {dayNumber, totalDays,
// seifRange, lotIndex, lotTotal} → les posts portent le programme quotidien.
export function buildPack(num, day, opts = {}) {
  const s = getSiman(num);
  if (!s) return null;
  const posts = buildSocialPosts(num);
  const e = enrichFor(num);
  const angle = ANGLES[((Number(day) % 7) + 7) % 7];
  const cta = CTAS[(Number(num) + Number(day)) % CTAS.length];
  const he = s.numHe ? `${s.numHe} · ` : '';
  const overview = `${SITE}/oh/${num}/`;
  const study = `${SITE}/oh/${num}/base`;
  const hook = angle.hook(e);

  const yomi = opts.yomi || null;
  const yomiLine = yomi
    ? `📅 Daat Yomi — jour ${yomi.dayNumber}/${yomi.totalDays} · séifim ${yomi.seifRange[0]}–${yomi.seifRange[1]}` +
      (yomi.lotTotal > 1 ? ` (${yomi.lotIndex}/${yomi.lotTotal})` : '') +
      ` · rejoindre : ${SITE}/#daat-yomi-banner`
    : '';

  const thread = [
    `1/ ${hook}\nAujourd'hui : ${he}${s.title}. 🧵`,
    e.concepts.length
      ? `2/ Au programme du siman ${num} (Orah Haïm) : ${e.concepts.slice(0, 3).join(' · ')}.`
      : `2/ Le Choulhan Aroukh (Orah Haïm, siman ${num}) pose ici les fondements. On l'étudie du texte hébreu jusqu'à l'application moderne.`,
    `3/ Sur DAAT, ce siman existe en 4 niveaux : base (texte + traduction), lamdan (pilpoul Rishonim/Acharonim), synthèse, et Daat HaRav (l'Admour HaZaken).`,
    `4/ L'idée : ne pas se contenter d'une réponse, mais comprendre la sougya — pour étudier, pas seulement “savoir quoi faire”.`,
    `5/ 📖 Étudier le siman ${num} 👉 ${overview}\n${DIS}`,
  ];

  const carousel = [
    `SLIDE 1 — ${he}${s.title}`,
    `SLIDE 2 — ${angle.label} : ${hook}`,
    ...(e.concepts.slice(0, 2).map((c, i) => `SLIDE ${3 + i} — ${c}`)),
    `SLIDE ${3 + Math.min(e.concepts.length, 2)} — Pour aller plus loin : pilpoul des Rishonim & Acharonim, puis la chitah de l'Admour HaZaken.`,
    `SLIDE ${4 + Math.min(e.concepts.length, 2)} — Étudie les 4 niveaux gratuitement sur daattorah.com (lien en bio). ${DIS}`,
  ];

  const communaute =
    `🕯️ *Le siman du jour — ${he}${s.title}*\n` +
    `${hook}\n` +
    (yomiLine ? `${yomiLine}\n` : '') +
    `📖 À étudier (4 niveaux) : ${overview}\n` +
    `${DIS}`;

  // Slides structurées pour le générateur d'images (canvas côté page).
  const slides = [
    { k: yomi ? `Daat Yomi · jour ${yomi.dayNumber}/${yomi.totalDays}` : `Siman ${num}${s.numHe ? ' · ' + s.numHe : ''}`,
      t: yomi ? `Siman ${num}${s.numHe ? ' · ' + s.numHe : ''} — ${s.title}` : s.title, cover: true },
    { k: angle.label, t: hook },
    ...e.concepts.slice(0, 2).map((c) => ({ k: 'Concept-clé', t: c })),
    ...(yomi ? [{ k: 'Le programme du jour', t: `Séifim ${yomi.seifRange[0]} à ${yomi.seifRange[1]} — 10 minutes par jour, 5 jours par semaine. Rejoins le Daat Yomi sur daattorah.com` }] : []),
    { k: 'Aller plus loin', t: 'Pilpoul des Rishonim & Acharonim, puis la chitah de l\'Admour HaZaken (Daat HaRav).' },
    { k: 'daattorah.com', t: `Étudie les 4 niveaux gratuitement. ${DIS}` },
  ];

  // Navigation vers les simanim voisins réellement disponibles.
  let prev = null;
  for (let n = Number(num) - 1; n >= 242 && !prev; n--) if (getSiman(n)) prev = n;
  let next = null;
  for (let n = Number(num) + 1; n <= 365 && !next; n++) if (getSiman(n)) next = n;

  return {
    nav: { prev, next },
    slides,
    yomi,
    num: Number(num),
    numHe: s.numHe || '',
    title: s.title,
    day: ((Number(day) % 7) + 7) % 7,
    jour: JOURS[((Number(day) % 7) + 7) % 7],
    angle: { key: angle.key, label: angle.label },
    subtitle: e.subtitle,
    concepts: e.concepts,
    links: { overview, study, blog: posts.blog, image: posts.image },
    blocks: [
      { id: 'accroche', title: 'Accroche du jour (story / statut)',
        text: `${hook}\n${yomiLine ? yomiLine + '\n' : ''}👉 ${overview}` },
      { id: 'linkedin', title: 'LinkedIn (mar–jeu 8h–10h)',
        text: `${hook}\n\n${yomiLine ? yomiLine + '\n\n' : ''}${posts.linkedin}` },
      { id: 'thread', title: 'Fil X / Bluesky', text: thread.join('\n\n') },
      { id: 'instagram', title: 'Instagram — caption', text: posts.instagram },
      { id: 'carrousel', title: 'Instagram — script carrousel', text: carousel.join('\n') },
      { id: 'facebook', title: 'Facebook', text: communauteFacebook(posts.facebook, yomiLine) },
      { id: 'communaute', title: 'Communauté WhatsApp / Telegram (ven. avant Shabbat)', text: communaute },
      { id: 'soutien', title: `Appel au soutien (rotation « ${cta.key} »)`, text: cta.text },
    ],
    cta: cta.key,
  };
}

// Insère la ligne Daat Yomi dans le post Facebook, avant le disclaimer final.
function communauteFacebook(fb, yomiLine) {
  if (!yomiLine) return fb;
  return fb.replace(`\n\n${DIS}`, `\n${yomiLine}\n\n${DIS}`);
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Studio mobile autonome (charte DAAT) : copier, partager (WhatsApp/Telegram/X/natif),
// onglets d'angle, navigation simanim, slides Instagram générées en PNG (canvas).
// Le secret est mémorisé côté navigateur (localStorage) — saisi une seule fois.
export function renderPackHtml(pack) {
  // Partages rapides pertinents par bloc (en plus de Copier + partage natif).
  const share = (b) => {
    const wa = `<a class="mini" data-share="wa" data-i="__I__" title="WhatsApp">WA</a>`;
    const tg = `<a class="mini" data-share="tg" data-i="__I__" title="Telegram">TG</a>`;
    const x = `<a class="mini" data-share="x" data-i="__I__" title="X">𝕏</a>`;
    if (b.id === 'communaute' || b.id === 'accroche' || b.id === 'soutien') return wa + tg;
    if (b.id === 'thread') return x;
    return '';
  };
  const cards = pack.blocks.map((b, i) => `
    <section class="card">
      <div class="card-h"><h2>${esc(b.title)}</h2>
        <div class="btns">${share(b).replaceAll('__I__', String(i))}
          <a class="mini" data-share="sys" data-i="${i}" title="Partager…">⤴</a>
          <button data-i="${i}">Copier</button></div></div>
      <pre id="b${i}">${esc(b.text)}</pre>
      ${b.id === 'carrousel' ? '<div id="slides" class="slides"></div>' : ''}
    </section>`).join('');

  const linksRow = [
    `<a href="${pack.links.overview}">Étude</a>`,
    pack.links.blog ? `<a href="${pack.links.blog}">Article</a>` : '',
    pack.links.image ? `<a href="${pack.links.image}">Visuel OG</a>` : '',
  ].filter(Boolean).join(' · ');

  const dayTabs = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
    .map((l, d) => `<a class="tab${d === pack.day ? ' on' : ''}" data-nav data-siman="${pack.num}" data-day="${d}">${l}</a>`)
    .join('');
  const nav =
    (pack.nav.prev ? `<a class="tab" data-nav data-siman="${pack.nav.prev}" data-day="${pack.day}">‹ ${pack.nav.prev}</a>` : '') +
    `<span class="cur">Siman ${pack.num}</span>` +
    (pack.nav.next ? `<a class="tab" data-nav data-siman="${pack.nav.next}" data-day="${pack.day}">${pack.nav.next} ›</a>` : '');

  const yomiBadge = pack.yomi
    ? `<p class="yomi">📅 Daat Yomi · jour ${pack.yomi.dayNumber}/${pack.yomi.totalDays} · séifim ${pack.yomi.seifRange[0]}–${pack.yomi.seifRange[1]}${pack.yomi.lotTotal > 1 ? ` (${pack.yomi.lotIndex}/${pack.yomi.lotTotal})` : ''}</p>`
    : '';

  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Pack du jour — siman ${pack.num}</title>
<style>
  :root{--navy:#1A1F3A;--or:#C5A55A;--or2:#a9863c;--creme:#FAF6EE;}
  *{box-sizing:border-box}body{margin:0;background:var(--creme);color:var(--navy);
    font-family:-apple-system,system-ui,'Segoe UI',Roboto,sans-serif;line-height:1.55;padding:16px}
  header{max-width:760px;margin:0 auto 14px}h1{font-family:Georgia,serif;margin:.2em 0;font-size:1.6rem}
  .sub{color:#6a6f86;font-size:13.5px;margin:.25em 0}.sub a{color:var(--or2)}
  .yomi{display:inline-block;background:var(--navy);color:var(--or);font-size:12.5px;font-weight:700;
    padding:5px 12px;border-radius:999px;margin:.35em 0}
  .row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:.5em 0}
  .tab{padding:6px 11px;border:1px solid #e6dfcf;border-radius:999px;background:#fff;color:var(--navy);
    text-decoration:none;font-size:12.5px;font-weight:600;cursor:pointer}
  .tab.on{background:var(--or);border-color:var(--or)}
  .cur{font-weight:700;font-size:13px;padding:0 4px}
  .card{max-width:760px;margin:0 auto 14px;background:#fff;border:1px solid #e6dfcf;border-radius:12px;overflow:hidden}
  .card-h{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:11px 14px;background:#fbf7ee;border-bottom:1px solid #e6dfcf;flex-wrap:wrap}
  h2{margin:0;font-size:14px;flex:1 1 auto}
  .btns{display:flex;gap:6px;align-items:center;flex:none}
  button{background:var(--or);color:var(--navy);border:0;padding:7px 14px;border-radius:8px;font-weight:700;cursor:pointer;flex:none}
  button.ok{background:#3f8f6b;color:#fff}
  .mini{display:inline-flex;align-items:center;justify-content:center;min-width:32px;height:30px;padding:0 8px;
    border:1px solid var(--or);border-radius:8px;color:var(--or2);font-size:12px;font-weight:800;cursor:pointer;text-decoration:none;background:#fff}
  pre{margin:0;padding:14px;white-space:pre-wrap;word-wrap:break-word;font-family:ui-monospace,Menlo,monospace;font-size:12.5px}
  .slides{display:flex;gap:10px;overflow-x:auto;padding:12px 14px;background:#fbf7ee;border-top:1px solid #e6dfcf}
  .slide-w{flex:none;text-align:center}
  .slide-w canvas{width:130px;height:162px;border-radius:8px;box-shadow:0 2px 8px rgba(26,31,58,.18);display:block}
  .slide-w a{display:inline-block;margin-top:6px;font-size:11.5px;font-weight:700;color:var(--or2);text-decoration:none}
  footer{max-width:760px;margin:18px auto 30px;color:#6a6f86;font-size:12px;text-align:center}
</style></head><body>
<header>
  <h1>דעת · Pack du jour</h1>
  ${yomiBadge}
  <p class="sub"><b>${esc(pack.jour)}</b> — siman ${pack.num}${pack.numHe ? ' (' + esc(pack.numHe) + ')' : ''} · ${esc(pack.title)}</p>
  <p class="sub">Angle : <b>${esc(pack.angle.label)}</b> · ${linksRow}</p>
  <div class="row">${nav}</div>
  <div class="row">${dayTabs}</div>
</header>
${cards}
<footer>Copier → coller, ou partager directement. On ne tranche pas de halakha — « consulte ton Rav ».<br>
Les vignettes du carrousel se téléchargent en PNG 1080×1350, prêtes pour Instagram.</footer>
<script>
(function(){
  var SLIDES=${JSON.stringify(pack.slides)};
  // — secret mémorisé une fois pour toutes —
  var qs=new URLSearchParams(location.search);
  var sec=qs.get('secret');
  if(sec){try{localStorage.setItem('daat_pack_secret',sec);}catch(e){}}
  else{try{sec=localStorage.getItem('daat_pack_secret');}catch(e){}}
  // — navigation (onglets jours + simanim) —
  document.querySelectorAll('[data-nav]').forEach(function(a){a.addEventListener('click',function(ev){
    ev.preventDefault();
    location.search='?secret='+encodeURIComponent(sec||'')+'&siman='+a.dataset.siman+'&day='+a.dataset.day;
  });});
  // — copier —
  document.querySelectorAll('button[data-i]').forEach(function(b){b.addEventListener('click',async function(){
    var t=document.getElementById('b'+b.dataset.i).textContent;
    try{await navigator.clipboard.writeText(t);b.textContent='Copié ✓';b.classList.add('ok');
      setTimeout(function(){b.textContent='Copier';b.classList.remove('ok')},1500);}catch(e){}
  });});
  // — partager —
  document.querySelectorAll('.mini[data-share]').forEach(function(a){a.addEventListener('click',function(ev){
    ev.preventDefault();
    var t=document.getElementById('b'+a.dataset.i).textContent;
    var m=a.dataset.share;
    if(m==='sys'&&navigator.share){navigator.share({text:t}).catch(function(){});return;}
    var u='';
    if(m==='wa')u='https://wa.me/?text='+encodeURIComponent(t);
    if(m==='tg')u='https://t.me/share/url?url='+encodeURIComponent('${pack.links.overview}')+'&text='+encodeURIComponent(t);
    if(m==='x'){var first=t.split('\\n\\n')[0];u='https://twitter.com/intent/tweet?text='+encodeURIComponent(first);}
    if(m==='sys'){u='https://wa.me/?text='+encodeURIComponent(t);}
    if(u)window.open(u,'_blank');
  });});
  // — slides Instagram en PNG (1080×1350, charte DAAT) —
  function wrap(ctx,text,max){var words=String(text).split(/\\s+/),lines=[],cur='';
    for(var i=0;i<words.length;i++){var test=cur?cur+' '+words[i]:words[i];
      if(ctx.measureText(test).width>max&&cur){lines.push(cur);cur=words[i];}else{cur=test;}}
    if(cur)lines.push(cur);return lines;}
  function draw(c,s){var x=c.getContext('2d'),W=1080,H=1350;
    x.fillStyle='#1A1F3A';x.fillRect(0,0,W,H);
    x.strokeStyle='#C5A55A';x.lineWidth=6;x.strokeRect(45,45,W-90,H-90);
    x.textAlign='center';
    x.fillStyle='#C5A55A';x.font='700 110px Georgia,serif';x.fillText('דעת',W/2,220);
    x.font='700 34px -apple-system,sans-serif';x.fillStyle='#FAF6EE';
    var k=String(s.k||'').toUpperCase();x.globalAlpha=.85;
    x.fillText(k.length>34?k.slice(0,34):k,W/2,330);x.globalAlpha=1;
    x.fillStyle='#C5A55A';x.fillRect(W/2-60,370,120,4);
    x.fillStyle='#FAF6EE';var size=s.cover?60:54;x.font=(s.cover?'700 ':'400 ')+size+'px Georgia,serif';
    var lines=wrap(x,s.t,W-220);if(lines.length>9){size=44;x.font='400 44px Georgia,serif';lines=wrap(x,s.t,W-200);}
    var y0=(H/2+40)-((lines.length-1)*(size+18))/2;
    lines.forEach(function(l,i){x.fillText(l,W/2,y0+i*(size+18));});
    x.fillStyle='#C5A55A';x.font='600 32px -apple-system,sans-serif';x.fillText('daattorah.com',W/2,H-110);}
  var box=document.getElementById('slides');
  if(box){SLIDES.forEach(function(s,i){
    var w=document.createElement('div');w.className='slide-w';
    var c=document.createElement('canvas');c.width=1080;c.height=1350;draw(c,s);
    var a=document.createElement('a');a.textContent='PNG '+(i+1);
    a.href='#';a.addEventListener('click',function(ev){ev.preventDefault();
      var d=document.createElement('a');d.download='daat-siman-${pack.num}-slide-'+(i+1)+'.png';
      d.href=c.toDataURL('image/png');d.click();});
    w.appendChild(c);w.appendChild(a);box.appendChild(w);});}
})();
</script></body></html>`;
}
