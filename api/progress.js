// Endpoint de synchronisation de la progression d'étude — par utilisateur.
//
// Auth : cookie daat_session (JWT signé) → getUserFromRequest → { email }
//
// Stockage : Vercel KV (Upstash Redis)
//   Clé `progress:{email}` → JSON { "242": ["base","lamdan"], "243": ["base"], ... }
//
// Endpoints :
//   GET  /api/progress       → { progress: {...} }
//   POST /api/progress       → merge avec le payload (jamais d'écrasement, juste union)
//                              body = { progress: { "242": ["base"], ... } }
//
// Philosophie : la progression est une UNION cumulative. Si le client envoie
// { 242: ['base'] } et que le serveur a déjà { 242: ['base','lamdan'] }, le
// résultat reste { 242: ['base','lamdan'] }. Aucune action ne peut « décocher »
// un niveau étudié — seul un DELETE explicite (non implémenté ici par sécurité)
// pourrait le faire. Cela évite de perdre du progrès en cas de localStorage
// corrompu sur un nouvel appareil.

import { kv } from './_kv.js';
import { getUserFromRequest, setCorsHeaders } from './_auth.js';

// Rate-limit par user pour les mutations.
// Le client écrit la progression à chaque ouverture de page niveau —
// donc beaucoup d'appels normaux. 600/h = 10/min suffit pour l'usage
// le plus intensif (révision rapide siman par siman).
const RL_WRITES_PER_HOUR = 600;

const VALID_LEVELS = new Set(['base', 'lamdan', 'synthese', 'daat-harav']);
const MAX_SIMAN = 365;
const MIN_SIMAN = 242;

async function isWriteRateLimited(email) {
  try {
    const key = `progress:rl:${email.toLowerCase()}`;
    const count = await kv.incr(key);
    if (count === 1) await kv.expire(key, 3600);
    return count > RL_WRITES_PER_HOUR;
  } catch (err) {
    console.error('[progress] rate-limit KV error (fail-open):', err?.message || err);
    return false;
  }
}

function progressKey(email) {
  return `progress:${email.toLowerCase().trim()}`;
}

// Nettoie un objet progress reçu du client.
// - Ne garde que les simanim numériques dans [242, 365]
// - Ne garde que les niveaux connus
// - Déduplique
function sanitize(payload) {
  if (!payload || typeof payload !== 'object') return {};
  const out = {};
  for (const [siman, levels] of Object.entries(payload)) {
    if (!/^\d+$/.test(siman)) continue;
    const n = parseInt(siman, 10);
    if (n < MIN_SIMAN || n > MAX_SIMAN) continue;
    if (!Array.isArray(levels)) continue;
    const clean = [...new Set(levels.filter(l => VALID_LEVELS.has(l)))];
    if (clean.length) out[siman] = clean;
  }
  return out;
}

// Union de deux progressions — jamais on perd un niveau étudié.
function merge(serverData, clientData) {
  const out = { ...serverData };
  for (const [siman, levels] of Object.entries(clientData)) {
    const existing = Array.isArray(out[siman]) ? out[siman] : [];
    out[siman] = [...new Set([...existing, ...levels])];
  }
  return out;
}

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const user = getUserFromRequest(req);
  if (!user) return res.status(401).json({ error: 'Non authentifié' });

  try {
    if (req.method === 'GET') {
      const raw = await kv.get(progressKey(user.email));
      let progress = {};
      if (raw) {
        try { progress = typeof raw === 'string' ? JSON.parse(raw) : raw; }
        catch { progress = {}; }
      }
      return res.status(200).json({ ok: true, progress });
    }

    if (req.method === 'POST') {
      if (await isWriteRateLimited(user.email)) {
        res.setHeader('Retry-After', '3600');
        return res.status(429).json({ error: 'Trop d\'écritures. Réessaie dans une heure.' });
      }

      const body = req.body || {};
      const clientProgress = sanitize(body.progress);
      if (!Object.keys(clientProgress).length) {
        return res.status(400).json({ error: 'Aucune progression valide dans le payload' });
      }

      // Lecture-merge-écriture (sans transaction — accepté car union pure)
      const raw = await kv.get(progressKey(user.email));
      let serverProgress = {};
      if (raw) {
        try { serverProgress = typeof raw === 'string' ? JSON.parse(raw) : raw; }
        catch { serverProgress = {}; }
      }
      const merged = merge(serverProgress, clientProgress);
      await kv.set(progressKey(user.email), JSON.stringify(merged));

      return res.status(200).json({ ok: true, progress: merged });
    }

    return res.status(405).json({ error: 'Méthode non autorisée — GET ou POST' });
  } catch (err) {
    console.error('[progress] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}
