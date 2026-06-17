// /api/my-plan — Lecture du plan personnel de l'utilisateur connecté.
//
// Pourquoi : le plan personnel est stocké en KV par email (custom-plan:{email})
// et utilisé par le cron pour envoyer le Daat Yomi quotidien. Mais la page
// d'accueil ne le détectait que via localStorage (par navigateur), d'où un
// décalage entre l'email (plan perso) et le site (plan universel) sur un
// appareil sans la clé localStorage. Cet endpoint donne au site une source de
// vérité commune : le plan tel que le cron l'utilise.
//
// Auth : cookie daat_session (JWT) → getUserFromRequest → { email }
// Stockage lu : custom-plan:{email} → { email, plan, savedAt } (écrit par /api/custom-plan)
//
// Endpoints :
//   GET /api/my-plan → { ok:true, plan: {...} | null }
//
// CORS credentialed (origine sur allow-list) — le cookie est SameSite=None.

import { kv } from './_kv.js';
import { getUserFromRequest, setCorsHeaders } from './_auth.js';

function planKey(email) {
  return `custom-plan:${email.toLowerCase().trim()}`;
}

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET uniquement' });

  const user = getUserFromRequest(req);
  // Pas connecté : on ne révèle rien, mais ce n'est pas une erreur côté client
  // (le site retombera simplement sur localStorage / plan universel).
  if (!user) return res.status(200).json({ ok: true, plan: null, authenticated: false });

  try {
    const raw = await kv.get(planKey(user.email));
    let record = null;
    if (raw) {
      try { record = typeof raw === 'string' ? JSON.parse(raw) : raw; }
      catch { record = null; }
    }
    const plan = record && record.plan ? record.plan : null;
    return res.status(200).json({ ok: true, plan, authenticated: true });
  } catch (err) {
    console.error('[my-plan] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
