// api/daily-pack.js — « Le pack du jour » en self-service (zéro token IA).
//
// Ouvre l'URL sur ton téléphone chaque matin : la page affiche les posts du jour
// (accroche, LinkedIn, fil X/Bluesky, Instagram, Facebook, communauté, appel au
// soutien) avec un bouton « Copier » par bloc. L'angle tourne selon le jour
// (Europe/Paris), l'appel au soutien tourne aussi — rien à décider, tout à coller.
//
// GET (auth ?secret=CRON_SECRET ou Bearer) :
//   /api/daily-pack?secret=…              → pack du siman en cours (curseur social)
//   /api/daily-pack?secret=…&siman=253    → un siman précis
//   /api/daily-pack?secret=…&day=5        → forcer l'angle (0=dim … 6=sam)
//   /api/daily-pack?secret=…&format=json  → le pack en JSON (intégrations)

import { kv } from './_kv.js';
import { nextValidSiman } from './_newsletter-weekly.js';
import { buildPack, renderPackHtml } from './_pack.js';

const env = (k) => (process.env[k] || '').trim();
const FIRST_SIMAN = 242;

// Jour de la semaine côté utilisateur (Europe/Paris), 0 = dimanche.
function parisDay() {
  const name = new Intl.DateTimeFormat('en-US', { timeZone: 'Europe/Paris', weekday: 'short' })
    .format(new Date());
  return ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(name);
}

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET uniquement' });

  const secret = env('CRON_SECRET');
  const auth = (req.headers.authorization || '').trim();
  const qSecret = String((req.query && req.query.secret) || '').trim();
  const authorized = !!secret && (auth === `Bearer ${secret}` || qSecret === secret);
  if (!authorized) return res.status(401).json({ error: 'Unauthorized' });

  try {
    let num = Number(req.query?.siman) || 0;
    if (!num) {
      // Par défaut : le siman de la semaine (même curseur que l'autopilot social).
      let cursor = FIRST_SIMAN;
      try { cursor = Number(await kv.get('social:weekly:cursor')) || FIRST_SIMAN; } catch { /* KV absent → 242 */ }
      num = nextValidSiman(cursor) || FIRST_SIMAN;
    }

    const day = req.query?.day != null && req.query.day !== ''
      ? Number(req.query.day)
      : parisDay();

    const pack = buildPack(num, day);
    if (!pack) return res.status(404).json({ error: `Siman ${num} introuvable (242→365).` });

    if ((req.query?.format || '') === 'json') {
      return res.status(200).json({ ok: true, pack });
    }
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'no-store');
    return res.status(200).send(renderPackHtml(pack));
  } catch (err) {
    console.error('[daily-pack] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
