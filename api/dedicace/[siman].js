// GET /api/dedicace/{N} — Liste des dédicaces du siman N.
//
// Réponse : { ok: true, siman: N, count: <n>, dedicaces: [ { nom, type, typeHe, ... } ] }
// Endpoint public (lecture seule) appelé par le bandeau en haut de chaque
// page de siman. CORS ouvert (géré globalement par vercel.json).
import { getRedis, listSiman } from '../_dedicaces.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'GET uniquement' });
  }

  const n = parseInt(req.query?.siman, 10);
  if (!Number.isFinite(n) || n <= 0) {
    return res.status(400).json({ error: 'siman invalide' });
  }

  try {
    const redis = getRedis();
    const dedicaces = await listSiman(redis, n, 50);
    // Cache CDN court : les dédicaces changent rarement, mais on veut une mise
    // à jour sous quelques minutes après un paiement.
    res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=120, stale-while-revalidate=600');
    return res.status(200).json({ ok: true, siman: n, count: dedicaces.length, dedicaces });
  } catch (err) {
    console.error('[dedicace] error:', err?.message || err);
    return res.status(500).json({ error: 'Erreur serveur' });
  }
}
