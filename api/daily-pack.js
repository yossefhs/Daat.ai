// api/daily-pack.js — « Le pack du jour » en self-service (zéro token IA).
//
// Ouvre l'URL sur ton téléphone chaque matin : la page affiche les posts du jour
// (accroche, LinkedIn, fil X/Bluesky, Instagram + slides PNG, Facebook, communauté,
// appel au soutien) avec boutons « Copier » et partage direct (WhatsApp/Telegram/X).
// Par défaut, le pack suit le **Daat Yomi** du jour (programme quotidien) ; hors
// jours de programme, il retombe sur le siman de la semaine (curseur social).
// Le secret n'est saisi qu'une fois : la page le mémorise (localStorage).
//
// GET :
//   /api/daily-pack                        → écran de saisie du secret (mémorisé ensuite)
//   /api/daily-pack?secret=…               → pack du jour (Daat Yomi, sinon curseur)
//   /api/daily-pack?secret=…&siman=253     → un siman précis
//   /api/daily-pack?secret=…&day=5         → forcer l'angle (0=dim … 6=sam)
//   /api/daily-pack?secret=…&format=json   → le pack en JSON (intégrations)

import { kv } from './_kv.js';
import { nextValidSiman } from './_newsletter-weekly.js';
import { getEntryForDate, loadPlan } from './_daily-limoud.js';
import { buildPack, renderPackHtml } from './_pack.js';

const env = (k) => (process.env[k] || '').trim();
const FIRST_SIMAN = 242;

// Date et jour de semaine côté utilisateur (Europe/Paris).
function parisNow() {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short',
  }).formatToParts(new Date());
  const get = (t) => parts.find((p) => p.type === t)?.value;
  return {
    dateISO: `${get('year')}-${get('month')}-${get('day')}`,
    day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday')),
  };
}

// Écran de saisie du secret : mémorise en localStorage puis recharge avec ?secret=.
// Auto-redirige si un secret est déjà mémorisé (sauf s'il vient d'être refusé).
function loginHtml(invalid) {
  return `<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>DAAT · Pack du jour</title>
<style>body{margin:0;background:#FAF6EE;color:#1A1F3A;font-family:-apple-system,system-ui,sans-serif;
display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px}
.box{max-width:380px;width:100%;background:#fff;border:1px solid #e6dfcf;border-radius:14px;padding:28px;text-align:center}
h1{font-family:Georgia,serif;margin:0 0 4px}p{color:#6a6f86;font-size:14px}
input{width:100%;padding:12px;border:1px solid #e6dfcf;border-radius:9px;font-size:15px;margin:12px 0;text-align:center}
button{width:100%;background:#C5A55A;color:#1A1F3A;border:0;padding:12px;border-radius:9px;font-weight:700;font-size:15px;cursor:pointer}
.err{color:#b3413d;font-size:13.5px;font-weight:600}</style></head><body>
<div class="box"><h1>דעת · Pack du jour</h1>
<p>Entre ton code d'accès (CRON_SECRET). Il sera mémorisé sur cet appareil — tu ne le saisiras qu'une fois.</p>
${invalid ? '<p class="err">Code refusé — vérifie la valeur dans Vercel (Settings → Environment Variables).</p>' : ''}
<form id="f"><input id="s" type="password" autocomplete="current-password" placeholder="Code d'accès" required>
<button>Ouvrir le pack du jour</button></form></div>
<script>
(function(){
  var invalid=${invalid ? 'true' : 'false'};
  try{
    if(invalid){localStorage.removeItem('daat_pack_secret');}
    else{var s=localStorage.getItem('daat_pack_secret');
      if(s){location.replace('?secret='+encodeURIComponent(s));return;}}
  }catch(e){}
  document.getElementById('f').addEventListener('submit',function(ev){ev.preventDefault();
    var v=document.getElementById('s').value.trim();
    try{localStorage.setItem('daat_pack_secret',v);}catch(e){}
    location.replace('?secret='+encodeURIComponent(v));});
})();
</script></body></html>`;
}

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET uniquement' });

  const secret = env('CRON_SECRET');
  const auth = (req.headers.authorization || '').trim();
  const qSecret = String((req.query && req.query.secret) || '').trim();
  const authorized = !!secret && (auth === `Bearer ${secret}` || qSecret === secret);
  const wantsJson = (req.query?.format || '') === 'json';

  if (!authorized) {
    if (wantsJson) return res.status(401).json({ error: 'Unauthorized' });
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'no-store');
    return res.status(401).send(loginHtml(!!qSecret));
  }

  try {
    const now = parisNow();

    // Daat Yomi du jour (si le plan couvre la date) — sinon curseur social.
    let yomiEntry = null;
    try { yomiEntry = getEntryForDate(now.dateISO); } catch { /* plan indisponible */ }
    let totalDays = 194;
    try { totalDays = loadPlan()?.meta?.totalDays || 194; } catch { /* défaut */ }

    let num = Number(req.query?.siman) || 0;
    if (!num) {
      if (yomiEntry?.siman?.num) num = yomiEntry.siman.num;
      else {
        let cursor = FIRST_SIMAN;
        try { cursor = Number(await kv.get('social:weekly:cursor')) || FIRST_SIMAN; } catch { /* KV absent */ }
        num = nextValidSiman(cursor) || FIRST_SIMAN;
      }
    }

    const day = req.query?.day != null && req.query.day !== ''
      ? Number(req.query.day)
      : now.day;

    // Le badge Daat Yomi n'apparaît que si le pack porte bien le siman du jour.
    const yomi = yomiEntry && yomiEntry.siman?.num === num
      ? {
          dayNumber: yomiEntry.dayNumber,
          totalDays,
          seifRange: yomiEntry.seifRange,
          lotIndex: yomiEntry.lotIndex,
          lotTotal: yomiEntry.lotTotal,
        }
      : null;

    const pack = buildPack(num, day, { yomi });
    if (!pack) return res.status(404).json({ error: `Siman ${num} introuvable (242→365).` });

    if (wantsJson) return res.status(200).json({ ok: true, pack });
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'no-store');
    return res.status(200).send(renderPackHtml(pack));
  } catch (err) {
    console.error('[daily-pack] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
