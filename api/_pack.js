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
export function buildPack(num, day) {
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
    `📖 À étudier (4 niveaux) : ${overview}\n` +
    `${DIS}`;

  return {
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
      { id: 'accroche', title: 'Accroche du jour (story / statut)', text: `${hook}\n👉 ${overview}` },
      { id: 'linkedin', title: 'LinkedIn (mar–jeu 8h–10h)', text: `${hook}\n\n${posts.linkedin}` },
      { id: 'thread', title: 'Fil X / Bluesky', text: thread.join('\n\n') },
      { id: 'instagram', title: 'Instagram — caption', text: posts.instagram },
      { id: 'carrousel', title: 'Instagram — script carrousel', text: carousel.join('\n') },
      { id: 'facebook', title: 'Facebook', text: posts.facebook },
      { id: 'communaute', title: 'Communauté WhatsApp / Telegram (ven. avant Shabbat)', text: communaute },
      { id: 'soutien', title: `Appel au soutien (rotation « ${cta.key} »)`, text: cta.text },
    ],
    cta: cta.key,
  };
}

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// Page mobile autonome avec boutons « Copier » (charte DAAT).
export function renderPackHtml(pack) {
  const cards = pack.blocks.map((b, i) => `
    <section class="card">
      <div class="card-h"><h2>${esc(b.title)}</h2><button data-i="${i}">Copier</button></div>
      <pre id="b${i}">${esc(b.text)}</pre>
    </section>`).join('');
  const linksRow = [
    `<a href="${pack.links.overview}">Étude</a>`,
    pack.links.blog ? `<a href="${pack.links.blog}">Article</a>` : '',
    pack.links.image ? `<a href="${pack.links.image}">Visuel OG</a>` : '',
  ].filter(Boolean).join(' · ');
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Pack du jour — siman ${pack.num}</title>
<style>
  :root{--navy:#1A1F3A;--or:#C5A55A;--creme:#FAF6EE;}
  *{box-sizing:border-box}body{margin:0;background:var(--creme);color:var(--navy);
    font-family:-apple-system,system-ui,'Segoe UI',Roboto,sans-serif;line-height:1.55;padding:20px}
  header{max-width:760px;margin:0 auto 20px}h1{font-family:Georgia,serif;margin:.2em 0}
  .sub{color:#6a6f86;font-size:14px}.sub a{color:#a9863c}
  .card{max-width:760px;margin:0 auto 16px;background:#fff;border:1px solid #e6dfcf;border-radius:12px;overflow:hidden}
  .card-h{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 16px;background:#fbf7ee;border-bottom:1px solid #e6dfcf}
  h2{margin:0;font-size:15px}
  button{background:var(--or);color:var(--navy);border:0;padding:8px 16px;border-radius:8px;font-weight:700;cursor:pointer;flex:none}
  button.ok{background:#3f8f6b;color:#fff}
  pre{margin:0;padding:16px;white-space:pre-wrap;word-wrap:break-word;font-family:ui-monospace,Menlo,monospace;font-size:13px}
</style></head><body>
<header><h1>דעת · Pack du jour</h1>
<p class="sub">${esc(pack.jour)} — siman ${pack.num}${pack.numHe ? ' (' + esc(pack.numHe) + ')' : ''} · ${esc(pack.title)}</p>
<p class="sub">Angle : ${esc(pack.angle.label)} · ${linksRow}</p>
<p class="sub">Clique « Copier », colle sur le réseau. On ne tranche pas de halakha — « consulte ton Rav ».</p></header>
${cards}
<script>
document.querySelectorAll('button[data-i]').forEach(function(b){b.addEventListener('click',async function(){
  var t=document.getElementById('b'+b.dataset.i).textContent;
  try{await navigator.clipboard.writeText(t);b.textContent='Copié ✓';b.classList.add('ok');
    setTimeout(function(){b.textContent='Copier';b.classList.remove('ok')},1500);}catch(e){}
});});
</script></body></html>`;
}
