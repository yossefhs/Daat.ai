// /api/custom-plan — Plan personnel DAAT
//
// MVP placeholder pour l'envoi quotidien par email (à venir).
// Pour l'instant, on stocke simplement le plan dans Vercel KV pour pouvoir
// le retrouver côté serveur quand le cron d'envoi sera ajouté.
//
// Méthodes :
//   POST   { email, plan }          → enregistre / met à jour le plan
//   OPTIONS                          → préflight CORS
//
// Aucune authentification stricte côté client (single-opt-in). Le rate-limit
// par IP empêche le spam.
//
// Stockage Vercel KV :
//   - custom-plan:{email}    → { email, plan, savedAt, ip }
//   - custom-plan:list       → liste des emails (pour le cron futur)

import { kv } from './_kv.js';
import { getClientIp } from './_http.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function isValidEmail(s) {
  return typeof s === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) && s.length <= 254;
}

// Garde-fous : on n'accepte que des plans avec une forme attendue.
// On accepte un sous-ensemble — pas besoin de tout valider, c'est un MVP.
function validatePlanShape(p) {
  if (!p || typeof p !== 'object') return 'plan absent';
  const rate = parseInt(p.rate, 10);
  if (!isFinite(rate) || rate < 1 || rate > 50) return 'rate invalide';
  if (p.rateUnit !== 'seifim_per_day' && p.rateUnit !== 'siman_per_day') return 'rateUnit invalide';
  if (!Array.isArray(p.studyDays) || !p.studyDays.length) return 'studyDays vide';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(p.startDate || ''))) return 'startDate invalide';
  const startSiman = parseInt(p.startSiman, 10);
  if (!isFinite(startSiman) || startSiman < 242 || startSiman > 365) return 'startSiman hors range';
  return null;
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  try {
    const body = req.body || {};
    const email = String(body.email || '').trim().toLowerCase();
    const plan = body.plan;

    if (!isValidEmail(email)) {
      return res.status(400).json({ error: 'Adresse email invalide' });
    }
    const planErr = validatePlanShape(plan);
    if (planErr) {
      return res.status(400).json({ error: 'Plan invalide : ' + planErr });
    }

    // Rate-limit IP : 5 saves/heure max
    const ip = getClientIp(req);
    try {
      const rlKey = `custom-plan:rl:${ip}`;
      const n = (await kv.incr(rlKey)) || 1;
      if (n === 1) await kv.expire(rlKey, 3600);
      if (n > 5) {
        return res.status(429).json({ error: 'Trop de sauvegardes — réessaie dans 1h.' });
      }
    } catch (e) {
      // KV down : on continue quand même (best-effort)
      console.warn('[custom-plan] rate-limit KV failed:', e?.message);
    }

    const record = {
      email,
      plan: {
        rate: parseInt(plan.rate, 10),
        rateUnit: plan.rateUnit,
        studyDays: plan.studyDays.map((x) => parseInt(x, 10)).filter((x) => x >= 0 && x <= 6),
        startDate: plan.startDate,
        startSiman: parseInt(plan.startSiman, 10),
      },
      savedAt: new Date().toISOString(),
      ip,
    };

    try {
      await kv.set(`custom-plan:${email}`, record);
      await kv.lpush('custom-plan:list', email);
      await kv.ltrim('custom-plan:list', 0, 9999);
    } catch (e) {
      console.warn('[custom-plan] KV write failed:', e?.message);
      // Pas d'erreur 500 — le client a déjà localStorage, le MVP fonctionne sans KV.
    }

    return res.status(200).json({
      ok: true,
      notice: "Plan enregistré. L'envoi quotidien par email arrive bientôt — tu seras prévenu.",
    });
  } catch (err) {
    console.error('[custom-plan] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
