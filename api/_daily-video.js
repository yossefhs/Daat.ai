/**
 * _daily-video.js — pipeline de la vidéo quotidienne Daat Yomi.
 *
 * Chaîne : entrée du jour (_daily-limoud) → storyboard agnostique → rendu MP4
 * (json2video) → publication multi-plateforme (Ayrshare). Tout est env-gated :
 * sans clés, les fonctions de rendu/publication sont des no-op explicites.
 *
 * Env :
 *   JSON2VIDEO_API_KEY   → rendu MP4 (https://json2video.com)
 *   AYRSHARE_API_KEY     → publication YouTube/Instagram/Facebook/TikTok
 *   DAILY_VIDEO_PLATFORMS→ csv, ex "youtube,instagram,facebook" (def: youtube,instagram)
 *
 * Identité : Navy #1A1F3A · Or #C5A55A · Crème #FAF6EE · police héb. Frank Ruhl Libre.
 */
const NAVY = '#1A1F3A', GOLD = '#C5A55A', CREME = '#FAF6EE';
const SITE = 'https://daattorah.com';

/* ---------- 1. Storyboard agnostique (le « créatif », testable hors API) ---------- */

export function buildStoryboard(entry) {
  const s = entry.siman;
  const lot = entry.lotTotal > 1 ? ` · partie ${entry.lotIndex}/${entry.lotTotal}` : '';
  return [
    { dur: 3, he: 'דעת יומי', kicker: `JOUR ${entry.dayNumber}`,
      sub: 'Le limoud du jour · Hilkhot Shabbat' },
    { dur: 4, kicker: `SIMAN ${s.num}`, he: s.numHe, title: s.title },
    { dur: 4, kicker: `Séifim ${entry.seifRange[0]}–${entry.seifRange[1]}${lot}`,
      title: s.title, sub: '5 séifim/jour · du dimanche au jeudi' },
    { dur: 3, he: 'דעת', title: `Choulhan Aroukh · Siman ${s.num}`,
      cta: `Étudie maintenant → daattorah.com/oh/${s.num}` },
  ];
}

export function buildCaption(entry) {
  const s = entry.siman;
  return [
    `📖 Daat Yomi — Jour ${entry.dayNumber}`,
    `Aujourd'hui : Siman ${s.num} (${s.numHe}) — ${s.title}.`,
    `Séifim ${entry.seifRange[0]}–${entry.seifRange[1]}. Hilkhot Shabbat, en français.`,
    ``,
    `👉 ${SITE}/oh/${s.num}`,
    ``,
    `#halakha #choulhanaroukh #hilkhotshabbat #torah #daattorah #limoud #judaisme`,
  ].join('\n');
}

/* ---------- 2. Adaptateur json2video (seul morceau dépendant du fournisseur) ---------- */

const FONT = 'Frank Ruhl Libre';
const HE_FONT = 'Frank Ruhl Libre';

function sceneToJ2V(sc) {
  const els = [];
  if (sc.kicker) els.push({ type: 'text', text: sc.kicker, x: 0, y: 380, width: 1080,
    settings: { 'font-family': 'Inter', 'font-size': 44, color: GOLD, 'text-align': 'center', 'letter-spacing': 4 } });
  if (sc.he) els.push({ type: 'text', text: sc.he, x: 0, y: 700, width: 1080,
    settings: { 'font-family': HE_FONT, 'font-size': 160, 'font-weight': 700, color: CREME, 'text-align': 'center' } });
  if (sc.title) els.push({ type: 'text', text: sc.title, x: 90, y: 980, width: 900,
    settings: { 'font-family': FONT, 'font-size': 64, color: CREME, 'text-align': 'center' } });
  if (sc.sub) els.push({ type: 'text', text: sc.sub, x: 90, y: 1400, width: 900,
    settings: { 'font-family': 'Inter', 'font-size': 46, color: GOLD, 'text-align': 'center' } });
  if (sc.cta) els.push({ type: 'text', text: sc.cta, x: 90, y: 1700, width: 900,
    settings: { 'font-family': 'Inter', 'font-size': 42, 'font-weight': 600, color: CREME, 'text-align': 'center' } });
  return { duration: sc.dur, 'background-color': NAVY, transition: { style: 'fade', duration: 0.5 }, elements: els };
}

export function toJson2Video(storyboard) {
  return {
    resolution: 'custom', width: 1080, height: 1920, quality: 'high',
    scenes: storyboard.map(sceneToJ2V),
  };
}

/* ---------- 3. Rendu (json2video) — env-gated ---------- */

export async function renderVideo(movie) {
  const key = process.env.JSON2VIDEO_API_KEY;
  if (!key) return { skipped: 'JSON2VIDEO_API_KEY absent' };

  const start = await fetch('https://api.json2video.com/v2/movies', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': key },
    body: JSON.stringify(movie),
  }).then((r) => r.json());

  const project = start.project || start.id;
  if (!project) return { error: 'render-start-failed', raw: start };

  // Polling (le rendu prend quelques dizaines de secondes).
  for (let i = 0; i < 40; i++) {
    await new Promise((r) => setTimeout(r, 4000));
    const st = await fetch(`https://api.json2video.com/v2/movies?project=${project}`, {
      headers: { 'x-api-key': key },
    }).then((r) => r.json());
    const m = st.movie || st;
    if (m.status === 'done' && m.url) return { url: m.url };
    if (m.status === 'error') return { error: 'render-failed', raw: m };
  }
  return { error: 'render-timeout', project };
}

/* ---------- 4. Publication multi-plateforme (Ayrshare) — env-gated ---------- */

export async function postVideo(videoUrl, caption) {
  const key = process.env.AYRSHARE_API_KEY;
  if (!key) return { skipped: 'AYRSHARE_API_KEY absent' };
  const platforms = (process.env.DAILY_VIDEO_PLATFORMS || 'youtube,instagram')
    .split(',').map((s) => s.trim()).filter(Boolean);

  return fetch('https://api.ayrshare.com/api/post', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
    body: JSON.stringify({
      post: caption,
      platforms,
      mediaUrls: [videoUrl],
      isVideo: true,
    }),
  }).then((r) => r.json());
}
