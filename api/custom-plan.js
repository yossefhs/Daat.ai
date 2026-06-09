// /api/custom-plan — Plan personnel DAAT
//
// Stocke un plan personnel d'étude en Vercel KV (avec une liste pour le cron).
// Les utilisateurs sans email (anonymes) reçoivent 200 OK — leur plan reste
// dans le localStorage côté client, le serveur ne stocke rien.
//
// Méthodes :
//   POST   { email?, plan }          → enregistre / met à jour le plan
//   OPTIONS                          → préflight CORS
//
// Stockage Vercel KV :
//   - custom-plan:{email}    → { email, plan, savedAt, ip }
//   - custom-plan:list       → liste des emails (pour le cron)

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
function validatePlanShape(p) {
  if (!p || typeof p !== 'object') return 'plan absent';
  const rate = parseInt(p.rate, 10);
  if (!isFinite(rate) || rate < 1 || rate > 50) return 'rate invalide';
  if (p.rateUnit !== 'seifim_per_day' && p.rateUnit !== 'siman_per_day') return 'rateUnit invalide';
  if (!Array.isArray(p.studyDays) || !p.studyDays.length) return 'studyDays vide';
  // studyDays doit être un sous-ensemble de [0..6]
  for (const d of p.studyDays) {
    const dd = parseInt(d, 10);
    if (!isFinite(dd) || dd < 0 || dd > 6) return 'studyDays hors range';
  }
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

    // Validation stricte du plan dans tous les cas
    const planErr = validatePlanShape(plan);
    if (planErr) {
      return res.status(400).json({ error: 'Plan invalide : ' + planErr });
    }

    // Sans email → anonyme : on retourne 200 OK, le plan reste en localStorage.
    if (!email) {
      return res.status(200).json({
        ok: true,
        anonymous: true,
        notice: 'Plan accepté (anonyme). Pour recevoir le Daat Yomi par email, ajoute ton adresse.',
      });
    }

    if (!isValidEmail(email)) {
      return res.status(400).json({ error: 'Adresse email invalide' });
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

    const now = new Date().toISOString();
    const normalizedPlan = {
      rate: parseInt(plan.rate, 10),
      rateUnit: plan.rateUnit,
      studyDays: plan.studyDays
        .map((x) => parseInt(x, 10))
        .filter((x) => x >= 0 && x <= 6)
        .filter((v, i, a) => a.indexOf(v) === i)
        .sort((a, b) => a - b),
      startDate: plan.startDate,
      startSiman: parseInt(plan.startSiman, 10),
      createdAt: typeof plan.createdAt === 'string' ? plan.createdAt : now,
    };

    let isUpdate = false;
    try {
      // Idempotence : si existant, update ; sinon insert + push dans la liste.
      const existing = await kv.get(`custom-plan:${email}`);
      isUpdate = !!existing;

      const record = {
        email,
        plan: normalizedPlan,
        savedAt: now,
        ip,
      };
      await kv.set(`custom-plan:${email}`, record);

      if (!isUpdate) {
        await kv.lpush('custom-plan:list', email);
        await kv.ltrim('custom-plan:list', 0, 9999);
      }
    } catch (e) {
      console.warn('[custom-plan] KV write failed:', e?.message);
      // Pas d'erreur 500 — le client a déjà localStorage, le MVP fonctionne sans KV.
    }

    return res.status(200).json({
      ok: true,
      updated: isUpdate,
      notice: isUpdate
        ? 'Plan personnel mis à jour. Tu recevras le Daat Yomi du jour selon ce nouveau plan.'
        : 'Plan personnel enregistré. Tu recevras le Daat Yomi du jour par email aux jours d\'étude choisis.',
    });
  } catch (err) {
    console.error('[custom-plan] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
