#!/usr/bin/env node
// scripts/pack-du-jour.js — « Le pack du jour » de DAAT.
//
// Génère, en une commande, un lot de posts prêts à copier-coller pour la journée :
// une accroche du jour, LinkedIn, un fil X/Bluesky, une caption + script de carrousel
// Instagram, un message communauté (WhatsApp/Telegram), et un appel au soutien qui
// TOURNE (dédicace / don / mécénat / newsletter) pour ne jamais spammer la même chose.
//
// Le contenu est ANCRÉ dans la source (titre réel du siman, numéro hébreu, liens
// canoniques) — on ne crée pas de halakha. Tout cas pratique renvoie « consulte ton Rav ».
//
// Usage :
//   node scripts/pack-du-jour.js                 # siman 242, accroche du jour = aujourd'hui
//   node scripts/pack-du-jour.js --siman 253     # un siman précis
//   node scripts/pack-du-jour.js --siman 253 --day 3   # forcer l'angle du jour (0=dim … 6=sam)
//   node scripts/pack-du-jour.js --siman 253 --html pack.html   # + page HTML avec boutons « Copier »
//
// Le skill `daat-social` (mode « Pack du jour ») s'appuie sur ce script pour la partie
// déterministe, puis enrichit les concepts depuis niveau-1-base.html si besoin.

import { writeFileSync } from 'node:fs';
import { getSiman } from '../api/_newsletter-weekly.js';
import { buildSocialPosts } from '../api/_social-content.js';

const SITE = 'https://daattorah.com';
const WHATSAPP = 'https://chat.whatsapp.com/LQT3IMwjNiZEARC7lxqmv1';
const TELEGRAM = 'https://t.me/Daattorah_com';
const HELLOASSO = 'https://www.helloasso.com/associations/association-hessed/formulaires/9';
const SOUTENIR = `${SITE}/soutenir.html`;
const CHAT = `${SITE}/chat.html`;

// ---- args ----
function arg(name, def) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const num = Number(arg('siman', '242'));
const dayOverride = arg('day', null);
const htmlOut = arg('html', null);
const today = dayOverride != null ? Number(dayOverride) : new Date().getDay(); // 0=dim

// ---- 7 accroches / angles du jour (une par jour de la semaine) ----
// Chaque angle propose une manière DIFFÉRENTE de présenter le même siman, pour que
// poster tous les jours ne lasse jamais.
const ANGLES = [
  { key: 'question', label: 'La question concrète',
    hook: (s) => `On se l'est tous déjà demandé un vendredi après-midi…` },
  { key: 'concept', label: 'Le mot juste',
    hook: (s) => `Un mot de la halakha que peu de gens savent définir précisément.` },
  { key: 'histoire', label: 'D\'où ça vient',
    hook: (s) => `Du Talmud au Choulhan Aroukh : la chaîne d'une même halakha.` },
  { key: 'nuance', label: 'La nuance qui change tout',
    hook: (s) => `Deux cas qui se ressemblent, une différence décisive.` },
  { key: 'pratique', label: 'Cas pratique',
    hook: (s) => `Un cas réel du quotidien, éclairé par le siman.` },
  { key: 'quatre-niveaux', label: 'Les 4 niveaux',
    hook: (s) => `Du débutant au talmid hakham : le même siman, 4 profondeurs.` },
  { key: 'daat-harav', label: 'La chitah de l\'Admour HaZaken',
    hook: (s) => `Ce que le Choulhan Aroukh HaRav apporte de plus.` },
];
const angle = ANGLES[today % 7];

// ---- 5 appels au soutien qui TOURNENT (monétisation sans spam) ----
const CTAS = [
  { key: 'dedicace',
    text: `🕯️ Tu peux dédier l'étude de ce siman — à la mémoire d'un proche (לעילוי נשמת), pour une refoua chéléma ou une réussite. Le nom apparaît sur la page, étudiée chaque jour dans le monde.\n👉 ${SOUTENIR}` },
  { key: 'don-18',
    text: `📚 18 € offrent une semaine d'étude accessible à tous, gratuitement. Si DAAT t'apporte, tu peux soutenir en un geste :\n👉 ${HELLOASSO}` },
  { key: 'mecenat',
    text: `🤝 Le mécénat mensuel (36 €/mois) fait vivre la plateforme et l'IA d'étude, gratuite pour tous. Rejoins les soutiens de DAAT :\n👉 ${SOUTENIR}` },
  { key: 'chat',
    text: `💬 Une question de halakha ? Le Chat Da'at te répond à partir du corpus du Rav, sources à l'appui — et gratuitement.\n👉 ${CHAT}` },
  { key: 'newsletter',
    text: `✉️ Reçois « le siman du dimanche » : un siman par semaine, expliqué, dans ta boîte mail. Inscription en bas de ${SITE}` },
];
// rotation : décalée par le siman ET le jour → varie chaque jour
const cta = CTAS[(num + today) % CTAS.length];

// ---- construction ----
const s = getSiman(num);
if (!s) {
  console.error(`✗ Siman ${num} introuvable dans data/. Vérifie le numéro (242→365).`);
  process.exit(1);
}
const posts = buildSocialPosts(num);
const he = s.numHe ? `${s.numHe} · ` : '';
const study = `${SITE}/oh/${num}/base`;
const overview = `${SITE}/oh/${num}/`;

const DIS = 'Pour la pratique, consulte ton Rav.';

// Fil X / Bluesky (5 tweets) — angle du jour en ouverture
const thread = [
  `1/ ${angle.hook(s)}\nAujourd'hui : ${he}${s.title}. 🧵`,
  `2/ Le Choulhan Aroukh (Orah Haïm, siman ${num}) pose ici les fondements. On l'étudie du texte hébreu jusqu'à l'application moderne.`,
  `3/ Sur DAAT, ce siman existe en 4 niveaux : base (texte + traduction), lamdan (pilpoul Rishonim/Acharonim), synthèse, et Daat HaRav (l'Admour HaZaken).`,
  `4/ L'idée : ne pas se contenter d'une réponse, mais comprendre la sougya — pour étudier, pas seulement “savoir quoi faire”.`,
  `5/ 📖 Étudier le siman ${num} 👉 ${overview}\n${DIS}`,
];

// Carrousel Instagram (script slide par slide)
const carousel = [
  `SLIDE 1 — ${he}${s.title}`,
  `SLIDE 2 — ${angle.label} : ${angle.hook(s)}`,
  `SLIDE 3 — Le siman ${num} du Choulhan Aroukh, expliqué simplement (texte hébreu + traduction française).`,
  `SLIDE 4 — Pour aller plus loin : pilpoul des Rishonim & Acharonim, puis la chitah de l'Admour HaZaken.`,
  `SLIDE 5 — Étudie les 4 niveaux gratuitement sur daattorah.com (lien en bio). ${DIS}`,
];

// Message communauté (WhatsApp / Telegram)
const communaute =
  `🕯️ *Le siman du jour — ${he}${s.title}*\n` +
  `${angle.hook(s)}\n` +
  `📖 À étudier (4 niveaux) : ${overview}\n` +
  `${DIS}`;

// LinkedIn : on part du gabarit auto, on ajoute l'angle du jour en tête
const linkedin =
  `${angle.hook(s)}\n\n` + posts.linkedin;

// ---- rendu texte ----
const jours = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
const sep = '\n' + '─'.repeat(64) + '\n';

const out = [
  `\n╔══════════════════════════════════════════════════════════════╗`,
  `   דעת · PACK DU JOUR — ${jours[today]}`,
  `   Siman ${num} ${s.numHe ? '(' + s.numHe + ')' : ''} — ${s.title}`,
  `   Angle du jour : ${angle.label}`,
  `╚══════════════════════════════════════════════════════════════╝`,
  ``,
  `Liens : étude ${study} · vue ${overview}`,
  posts.blog ? `Article de blog : ${posts.blog}` : `(pas encore d'article de blog pour ce siman)`,
  posts.image ? `Visuel OG : ${posts.image}` : ``,
  sep,
  `① ACCROCHE DU JOUR (story / statut)\n`,
  `${angle.hook(s)}\n👉 ${overview}`,
  sep,
  `② LINKEDIN (mar–jeu 8h–10h)\n`,
  linkedin,
  sep,
  `③ FIL X / BLUESKY (thread)\n`,
  thread.join('\n\n'),
  sep,
  `④ INSTAGRAM — caption\n`,
  posts.instagram,
  `\n— script carrousel —\n`,
  carousel.join('\n'),
  sep,
  `⑤ FACEBOOK\n`,
  posts.facebook,
  sep,
  `⑥ COMMUNAUTÉ (WhatsApp / Telegram — ven. avant Shabbat)\n`,
  communaute,
  `\nGroupe WhatsApp : ${WHATSAPP}\nCanal Telegram : ${TELEGRAM}`,
  sep,
  `⑦ APPEL DU JOUR (soutien — rotation « ${cta.key} »)\n`,
  cta.text,
  sep,
  `Rappel : on ne tranche pas de halakha. Toujours « consulte ton Rav ».`,
  ``,
].filter((l) => l !== '').join('\n');

console.log(out);

// ---- sortie HTML optionnelle (boutons « Copier ») ----
if (htmlOut) {
  const blocks = [
    ['Accroche du jour', `${angle.hook(s)}\n👉 ${overview}`],
    ['LinkedIn', linkedin],
    ['Fil X / Bluesky', thread.join('\n\n')],
    ['Instagram — caption', posts.instagram],
    ['Instagram — carrousel', carousel.join('\n')],
    ['Facebook', posts.facebook],
    ['Communauté WhatsApp / Telegram', communaute],
    [`Appel au soutien (${cta.key})`, cta.text],
  ];
  const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const cards = blocks.map(([t, body], i) => `
    <section class="card">
      <div class="card-h"><h2>${esc(t)}</h2><button data-i="${i}">Copier</button></div>
      <pre id="b${i}">${esc(body)}</pre>
    </section>`).join('');
  const html = `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pack du jour — siman ${num}</title>
<style>
  :root{--navy:#1A1F3A;--or:#C5A55A;--creme:#FAF6EE;}
  *{box-sizing:border-box}body{margin:0;background:var(--creme);color:var(--navy);
    font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;line-height:1.55;padding:20px}
  header{max-width:760px;margin:0 auto 20px}h1{font-family:Georgia,serif;margin:.2em 0}
  .sub{color:#6a6f86;font-size:14px}
  .card{max-width:760px;margin:0 auto 16px;background:#fff;border:1px solid #e6dfcf;border-radius:12px;overflow:hidden}
  .card-h{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#fbf7ee;border-bottom:1px solid #e6dfcf}
  h2{margin:0;font-size:15px}
  button{background:var(--or);color:var(--navy);border:0;padding:8px 16px;border-radius:8px;font-weight:700;cursor:pointer}
  button.ok{background:#3f8f6b;color:#fff}
  pre{margin:0;padding:16px;white-space:pre-wrap;word-wrap:break-word;font-family:ui-monospace,Menlo,monospace;font-size:13px}
</style></head><body>
<header><h1>דעת · Pack du jour</h1>
<p class="sub">Siman ${num} — ${esc(s.title)} · angle : ${esc(angle.label)}</p>
<p class="sub">Clique « Copier », colle sur le réseau. On ne tranche pas de halakha — « consulte ton Rav ».</p></header>
${cards}
<script>
document.querySelectorAll('button[data-i]').forEach(b=>b.addEventListener('click',async()=>{
  const t=document.getElementById('b'+b.dataset.i).textContent;
  try{await navigator.clipboard.writeText(t);b.textContent='Copié ✓';b.classList.add('ok');
    setTimeout(()=>{b.textContent='Copier';b.classList.remove('ok')},1500);}catch(e){}
}));
</script></body></html>`;
  writeFileSync(htmlOut, html);
  console.log(`\n📄 Page HTML avec boutons « Copier » écrite : ${htmlOut}`);
}
