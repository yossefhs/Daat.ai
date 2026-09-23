// GET /api/admin/feedback — Liste les retours utilisateurs (auth: ADMIN_PASSWORD)
//
// Query params :
//   ?limit=100  (défaut 100, max 500)
//   ?rating=👍|👎  (filtre optionnel)
//
// Réponse :
//   {
//     ok: true,
//     stats: { total, positive, negative, satisfaction (0-100) },
//     entries: [...]
//   }
//
// DELETE /api/admin/feedback?id={id} — supprime un retour
//
// Auth : header Authorization: Bearer <ADMIN_PASSWORD>

import { kv } from '../_kv.js';
import { corsAdmin, origineRefusee, refuserOrigine, freinage, echecAdmin, reussiteAdmin, refuser } from '../_admin-gate.js';

function checkAuth(req) {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) {
    return { ok: false, status: 500, error: 'ADMIN_PASSWORD non configuré' };
  }
  const auth = req.headers['authorization'] || '';
  const provided = auth.startsWith('Bearer ') ? auth.slice(7) : '';
  if (provided !== expected) {
    return { ok: false, status: 401, error: 'Non autorisé' };
  }
  return { ok: true };
}

export default async function handler(req, res) {
  // L'origine est comparée à une liste : le 401 n'est plus lisible
  // par une page quelconque (voir ../_admin-gate.js).
  corsAdmin(req, res, 'GET, DELETE, OPTIONS', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();

  if (origineRefusee(req)) return refuserOrigine(res);
  const frein = await freinage(req);
  if (frein.bloque) return refuser(res);
  const auth = checkAuth(req);
  if (!auth.ok) {
    if (auth.status === 401) await echecAdmin(req);
    return res.status(auth.status).json({ error: auth.error });
  }
  await reussiteAdmin(req);

  try {
    if (req.method === 'GET') {
      const limit = Math.min(parseInt(req.query.limit || '100', 10) || 100, 500);
      const ratingFilter = req.query.rating || null;

      const ids = (await kv.lrange('feedback:list', 0, limit - 1)) || [];
      const entries = await Promise.all(ids.map(id => kv.get(`feedback:${id}`)));
      let valid = entries.filter(Boolean);
      if (ratingFilter) valid = valid.filter(e => e.rating === ratingFilter);

      // Stats sur les 100 derniers (toutes ratings)
      const allRecent = entries.filter(Boolean);
      const total = allRecent.length;
      const positive = allRecent.filter(e => e.rating === '👍').length;
      const negative = allRecent.filter(e => e.rating === '👎').length;
      const satisfaction = total > 0 ? Math.round((positive / total) * 100) : 0;

      return res.status(200).json({
        ok: true,
        stats: { total, positive, negative, satisfaction },
        entries: valid,
      });
    }

    if (req.method === 'DELETE') {
      const id = req.query.id;
      if (!id) return res.status(400).json({ error: 'id requis' });
      await kv.del(`feedback:${id}`);
      // On ne nettoie pas la liste — les ids morts seront filtrés par le GET
      return res.status(200).json({ ok: true, deleted: id });
    }

    return res.status(405).json({ error: 'Méthode non autorisée' });
  } catch (err) {
    console.error('[admin/feedback] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}
