// api/aujourdhui.js — L'étude du jour (Daat Yomi) en JSON public.
//
// Alimente la page /aujourdhui (bloc « Daat Yomi aujourd'hui ») sans que le
// client télécharge les 280 Ko de data/limoud-plan.json. Aucun secret, aucun
// appel IA, aucune écriture KV — lecture du plan + cache edge jusqu'à minuit
// (Europe/Paris), donc quasi toujours servi depuis le CDN.
//
// GET /api/aujourdhui             → { ok, date, isStudyDay, entry|null, next|null }
// GET /api/aujourdhui?date=ISO    → même chose pour une date donnée (debug)
// GET /api/aujourdhui?semaine=1   → { ok, weekStart, days: [entries dim→jeu de la
//                                    semaine courante] } — alimente /partenaires
//                                    (kit hebdo des communautés, zéro maintenance)

import { getEntryForDate, loadPlan } from './_daily-limoud.js';

function parisToday() {
  // Date côté utilisateur francophone (Europe/Paris), pas la TZ du lambda.
  const now = new Date();
  const paris = new Intl.DateTimeFormat('fr-CA', {
    timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit',
  }).format(now); // fr-CA → YYYY-MM-DD
  return paris;
}

function secondsUntilParisMidnight() {
  const now = new Date();
  const parisNow = new Date(now.toLocaleString('en-US', { timeZone: 'Europe/Paris' }));
  const midnight = new Date(parisNow);
  midnight.setHours(24, 0, 0, 0);
  return Math.max(60, Math.floor((midnight - parisNow) / 1000));
}

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'GET') return res.status(405).json({ ok: false, error: 'GET only' });

  try {
    const qDate = typeof req.query.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(req.query.date)
      ? req.query.date : null;
    const date = qDate || parisToday();

    // Mode « semaine » : les entrées du dimanche au jeudi de la semaine courante.
    if (req.query.semaine) {
      const [y, m, d] = date.split('-').map(Number);
      const ref = new Date(Date.UTC(y, m - 1, d));
      const sunday = new Date(ref);
      sunday.setUTCDate(ref.getUTCDate() - ref.getUTCDay()); // dimanche de la semaine
      const days = [];
      for (let i = 0; i < 5; i++) { // dim → jeu
        const dt = new Date(sunday);
        dt.setUTCDate(sunday.getUTCDate() + i);
        const iso = dt.toISOString().slice(0, 10);
        const e = getEntryForDate(iso);
        if (e) days.push(e);
      }
      const ttlW = Math.min(secondsUntilParisMidnight(), 21600);
      res.setHeader('Cache-Control', `public, s-maxage=${ttlW}, stale-while-revalidate=300`);
      return res.status(200).json({ ok: true, weekStart: sunday.toISOString().slice(0, 10), days });
    }

    const entry = getEntryForDate(date);

    // Jour sans étude (vendredi/shabbat/hors plan) → prochaine entrée pour le CTA.
    let next = null;
    if (!entry) {
      const plan = loadPlan();
      const upcoming = (plan.entries || []).find((e) => e.date > date);
      if (upcoming) {
        next = { date: upcoming.date, dayNumber: upcoming.dayNumber, siman: upcoming.siman };
      }
    }

    // Cache CDN jusqu'à minuit Paris (mais jamais plus de 6h, garde-fou).
    const ttl = Math.min(secondsUntilParisMidnight(), 21600);
    res.setHeader('Cache-Control', `public, s-maxage=${ttl}, stale-while-revalidate=300`);

    return res.status(200).json({ ok: true, date, isStudyDay: !!entry, entry, next });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'plan indisponible' });
  }
}
