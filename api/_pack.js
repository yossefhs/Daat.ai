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

// Matière de l'infographie « Daat Yomi » : intro, points essentiels (concepts
// nommés du siman), message — tout extrait du corpus, rien d'inventé.
function infographicFor(num) {
  const chunks = corpusFor(num);
  // Intro : la question fondamentale (contexte général), sinon le sous-titre.
  const ctx = chunks.find((c) => /contexte général/i.test(c.sectionTitle || '') && c.type === 'definition');
  const intro = firstSentence(ctx?.text, 300) || firstSentence(chunks.find((c) => c.simanSubtitle)?.simanSubtitle, 300);
  // Points : « Concept N — nom : définition » (niveau 1), max 5.
  const points = [];
  for (const c of chunks) {
    const m = /^Concept\s*\d+\s*[—:-]\s*([^:]{2,140}?)\s*:\s*(.+)$/s.exec(String(c.text || '').trim());
    if (m) {
      const text = firstSentence(m[2].replace(/\s+/g, ' '), 150);
      if (text) points.push({ title: m[1].replace(/\s+/g, ' ').trim(), text });
    }
    if (points.length >= 5) break;
  }
  // Complément si moins de 3 points : premières phrases de sections FR distinctes.
  if (points.length < 3) {
    const seen = new Set(points.map((p) => p.title));
    for (const c of chunks) {
      const t = String(c.sectionTitle || '').replace(/^\d+\.\s*/, '').trim();
      if (!t || seen.has(t) || /[֐-׿]/.test(t)) continue;
      if (/contexte général|concepts-clés|introduction|conclusion|faq|sources?|axiome|synthèse|hiérarchie/i.test(t)) continue;
      const text = firstSentence(String(c.text || '').replace(/\s+/g, ' '), 150);
      if (!text) continue;
      seen.add(t);
      points.push({ title: t, text });
      if (points.length >= 4) break;
    }
  }
  // Message : « le siman en une phrase » (axiome central de la synthèse).
  const ax = chunks.find((c) => /axiome central/i.test(c.sectionTitle || ''));
  const message = firstSentence(String(ax?.text || '').replace(/^.*?en une phrase\.?\s*/is, '').replace(/\s+/g, ' '), 240)
    || 'Un siman, quatre niveaux : comprendre la sougya avant de « savoir quoi faire ».';
  return { intro, points, message };
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
    info: infographicFor(num),
    meta: opts.meta || null,
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

// Infographie « Daat Yomi » 1080×1350 — gabarit issu du Design System DAAT
// (variante « typographique parchemin » validée dans Claude Design) : filigrane
// דעת, cadre or fin, badge JOUR, titre Daat Yomi serif, bandeau siman navy,
// points essentiels en chiffres romains (hébreu vocalisé + translitération +
// définition), message du siman, pied URL. Styles 100 % inline pour l'export
// PNG côté client (SVG foreignObject → canvas).
function infographicHtml(pack) {
  const NAVY = '#1A1F3A', GOLD = '#C5A55A', CREME = '#FAF6EE', INK = '#3D4266';
  const serif = "'Cormorant Garamond',Georgia,serif";
  const hebfont = "'Frank Ruhl Libre',Georgia,serif";
  const p = pack;
  const semaine = p.yomi ? Math.ceil(p.yomi.dayNumber / 5) : null;
  const ROMANS = ['I', 'II', 'III', 'IV', 'V'];
  const points = (p.info.points || []).slice(0, 4);

  // « עָקַר רַגְלָיו (Akar Raglav) » → hébreu + translitération séparés.
  const splitTitle = (t) => {
    const m = /^([\u0590-\u05FF\u05B0-\u05C7\s"'״׳]+?)\s*\(([^)]+)\)\s*$/.exec(String(t).trim());
    return m ? { he: m[1].trim(), lat: m[2].trim() } : { he: '', lat: String(t).trim() };
  };

  const pts = points.map((pt, i) => {
    const s = splitTitle(pt.title);
    const last = i === points.length - 1;
    return `
      <div style="display:flex;gap:20px;align-items:baseline;padding:12px 0;${last ? '' : `border-bottom:1px solid rgba(197,165,90,.35);`}">
        <div style="flex:0 0 auto;font-family:${serif};font-size:34px;font-weight:600;color:${GOLD};width:40px;text-align:right">${ROMANS[i] || i + 1}</div>
        <div>
          ${s.he ? `<span style="font-family:${hebfont};font-size:26px;color:${NAVY};direction:rtl">${esc(s.he)}</span>` : ''}
          <span style="font-family:${serif};font-style:italic;font-size:20px;color:${INK};${s.he ? 'margin-left:12px' : ''}">${esc(s.lat)}</span>
          <div style="font-size:17px;line-height:1.45;color:${INK};margin-top:2px">${esc(pt.text)}</div>
        </div>
      </div>`;
  }).join('');

  const badge = `<div style="background:${NAVY};border-radius:14px;padding:18px 24px">
      <div style="font-family:${serif};font-size:36px;font-weight:600;color:${GOLD};line-height:1">${p.yomi ? `JOUR ${p.yomi.dayNumber}` : `SIMAN ${p.num}`}</div>
      ${p.meta?.dateFr ? `<div style="font-size:14px;color:${CREME};margin-top:6px;text-transform:capitalize">${esc(p.meta.dateFr)}</div>` : ''}
      ${semaine ? `<div style="font-size:11px;color:rgba(197,165,90,.9);margin-top:6px;letter-spacing:.22em">SEMAINE ${semaine}</div>` : ''}
    </div>`;

  return `<div id="ig-root" style="width:1080px;height:1350px;position:relative;display:flex;flex-direction:column;overflow:hidden;box-sizing:border-box;background:radial-gradient(circle at 22% 10%,rgba(197,165,90,.14),transparent 44%),radial-gradient(circle at 80% 88%,rgba(197,165,90,.1),transparent 50%),${CREME};font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif">
    <div style="position:absolute;right:-40px;bottom:60px;font-family:${hebfont};font-weight:700;font-size:460px;line-height:.8;color:rgba(197,165,90,.09);pointer-events:none">דעת</div>
    <div style="position:absolute;inset:28px;border:1px solid rgba(197,165,90,.55);pointer-events:none"></div>

    <div style="position:relative;padding:58px 62px 0;display:flex;justify-content:space-between;align-items:flex-start;flex:0 0 auto">
      ${badge}
      <div style="text-align:right;padding-top:6px">
        <div style="font-family:${hebfont};font-weight:700;font-size:44px;color:${GOLD};line-height:1">דעת</div>
        <div style="font-size:11px;letter-spacing:.2em;color:${INK};margin-top:6px">DAATTORAH</div>
      </div>
    </div>

    <div style="position:relative;padding:32px 62px 0;text-align:center;flex:0 0 auto">
      <div style="font-family:${serif};font-size:76px;font-weight:700;letter-spacing:.04em;color:${NAVY};line-height:1">Daat Yomi</div>
      <div style="width:110px;height:1px;background:${GOLD};margin:20px auto"></div>
      <div style="font-size:18px;letter-spacing:.18em;text-transform:uppercase;color:${INK}">Étude quotidienne des lois de Chabbat</div>
    </div>

    <div style="position:relative;margin:34px 62px 0;background:${NAVY};padding:24px 30px;text-align:center;flex:0 0 auto">
      <div style="display:flex;align-items:baseline;justify-content:center;gap:16px;flex-wrap:wrap">
        <span style="font-family:${serif};font-size:32px;font-weight:600;color:${GOLD}">SIMAN ${p.num}</span>
        ${p.numHe ? `<span style="color:rgba(197,165,90,.5)">·</span>
        <span style="font-family:${hebfont};font-size:30px;color:${GOLD};direction:rtl">${esc(p.numHe)}</span>` : ''}
        ${p.yomi ? `<span style="color:rgba(197,165,90,.5)">·</span>
        <span style="font-size:14px;letter-spacing:.14em;color:rgba(250,246,238,.9)">SÉ'IFIM ${p.yomi.seifRange[0]} À ${p.yomi.seifRange[1]}</span>` : ''}
      </div>
      <div style="font-family:${serif};font-style:italic;font-size:22px;color:${CREME};margin-top:10px">${esc(p.title)}</div>
    </div>

    ${p.info.intro ? `<div style="position:relative;margin:28px 62px 0;background:#fff;border:1.5px solid ${GOLD};padding:22px 26px;display:flex;gap:16px;align-items:flex-start;flex:0 0 auto">
      <div style="font-size:28px;line-height:1.1">📖</div>
      <div style="font-size:18px;line-height:1.5;color:${INK}">${esc(p.info.intro)}</div>
    </div>` : ''}

    <div style="position:relative;padding:20px 62px 0;flex:1 1 0;min-height:0">
      <div style="text-align:center;font-size:13px;letter-spacing:.26em;color:${GOLD}">LES POINTS ESSENTIELS</div>
      <div style="display:flex;flex-direction:column;margin-top:14px">${pts}</div>
    </div>

    <div style="position:relative;margin:0 62px;background:${NAVY};padding:24px 28px;text-align:center;flex:0 0 auto">
      <div style="font-size:12px;letter-spacing:.26em;color:${GOLD}">LE MESSAGE DU SIMAN</div>
      <div style="font-family:${serif};font-style:italic;font-size:25px;line-height:1.4;color:${CREME};margin-top:10px">${esc(p.info.message)}</div>
    </div>

    <div style="position:relative;padding:20px 62px 32px;display:flex;align-items:center;justify-content:space-between;gap:20px;flex:0 0 auto">
      <div style="font:15px ui-monospace,Menlo,monospace;color:${GOLD}">daattorah.com/oh/${p.num}/base</div>
      <div style="font-size:14px;color:rgba(61,66,102,.8);font-style:italic">Pour la pratique, consulte ton Rav.</div>
    </div>
  </div>`;
}

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

  const igCard = `
    <section class="card">
      <div class="card-h"><h2>Infographie du jour (PNG 1080×1350 — Instagram / WhatsApp)</h2>
        <div class="btns"><button id="ig-dl">Télécharger PNG</button></div></div>
      <div class="ig-wrap"><div class="ig-scale">${infographicHtml(pack)}</div></div>
    </section>`;

  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>Pack du jour — siman ${pack.num}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400&family=Frank+Ruhl+Libre:wght@700&display=swap" rel="stylesheet">
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
  .ig-wrap{padding:14px;background:#fbf7ee;display:flex;justify-content:center;overflow:hidden}
  .ig-scale{width:324px;height:405px;overflow:hidden}
  .ig-scale > div{transform:scale(0.3);transform-origin:top left}
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
${igCard}
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
  // — infographie : export PNG (SVG foreignObject → canvas) —
  var igBtn=document.getElementById('ig-dl');
  if(igBtn){igBtn.addEventListener('click',function(){
    var node=document.getElementById('ig-root');if(!node)return;
    var clone=node.cloneNode(true);
    clone.style.transform='none';
    var xml=new XMLSerializer().serializeToString(clone);
    var svg='<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350">'+
      '<foreignObject width="100%" height="100%">'+xml+'</foreignObject></svg>';
    var img=new Image();
    img.onload=function(){
      var c=document.createElement('canvas');c.width=1080;c.height=1350;
      var x=c.getContext('2d');x.fillStyle='#FAF6EE';x.fillRect(0,0,1080,1350);
      x.drawImage(img,0,0);
      try{var a=document.createElement('a');
        a.download='daat-yomi-siman-${pack.num}.png';
        a.href=c.toDataURL('image/png');a.click();
        igBtn.textContent='Téléchargé ✓';igBtn.classList.add('ok');
        setTimeout(function(){igBtn.textContent='Télécharger PNG';igBtn.classList.remove('ok')},2000);
      }catch(e){alert('Export impossible sur ce navigateur — fais une capture de l\\'aperçu.');}
    };
    img.onerror=function(){alert('Export impossible — fais une capture de l\\'aperçu.');};
    img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);
  });}
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
