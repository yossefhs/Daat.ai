// /api/dedicaces
//   GET  → flux global de toutes les dédicaces (lecture publique).
//   POST → ajout manuel d'une dédicace (admin-only via ADMIN_PASSWORD).
//
// Body POST JSON : { siman, nom, type }
//   siman : numéro du siman concerné (entier)
//   nom   : nom hébreu de la personne dédiée
//   type  : 'ilui' | 'refoua' | 'hatzlacha' (ou libellé libre normalisé)
//
// Auth POST — accepte (comme api/soutenir.js) :
//   - Authorization: Bearer <ADMIN_PASSWORD>
//   - x-admin-secret: <ADMIN_PASSWORD>
//   - ?secret=<ADMIN_PASSWORD>
import { getRedis, listAll, makeDedicace, saveDedicace } from './_dedicaces.js';

function isAuthed(req) {
  const adminPwd = process.env.ADMIN_PASSWORD;
  if (!adminPwd) return false;
  const bearer = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  if (bearer && bearer === adminPwd) return true;
  if (req.headers['x-admin-secret'] && req.headers['x-admin-secret'] === adminPwd) return true;
  if (req.query?.secret && req.query.secret === adminPwd) return true;
  return false;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Secret');
  if (req.method === 'OPTIONS') return res.status(200).end();

  let redis;
  try {
    redis = getRedis();
  } catch (err) {
    console.error('[dedicaces] KV init error:', err?.message || err);
    return res.status(500).json({ error: 'Erreur serveur' });
  }

  // ── GET : flux global ──────────────────────────────────────────────────────
  if (req.method === 'GET') {
    try {
      const limit = Math.min(parseInt(req.query?.limit, 10) || 200, 1000);
      const dedicaces = await listAll(redis, limit);
      res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=120, stale-while-revalidate=600');
      return res.status(200).json({ ok: true, count: dedicaces.length, dedicaces });
    } catch (err) {
      console.error('[dedicaces] GET error:', err?.message || err);
      return res.status(500).json({ error: 'Erreur serveur' });
    }
  }

  // ── POST : ajout manuel (admin) ────────────────────────────────────────────
  if (req.method === 'POST') {
    if (!isAuthed(req)) {
      return res.status(401).json({ error: 'Non autorisé' });
    }
    try {
      const body = req.body || {};
      const nom = String(body.nom || body.name || '').trim();
      if (!nom) return res.status(400).json({ error: 'nom requis' });

      const simanRaw = body.siman ?? body.simane ?? '';
      const siman = (String(simanRaw).match(/\d+/) || [])[0] || null;
      if (!siman) return res.status(400).json({ error: 'siman requis' });

      const dedic = makeDedicace({ siman, nom, type: body.type, source: 'manual' });
      await saveDedicace(redis, dedic);
      console.log(`[dedicaces] ajout manuel siman=${dedic.siman} type=${dedic.type}`);
      return res.status(200).json({ ok: true, saved: dedic });
    } catch (err) {
      console.error('[dedicaces] POST error:', err?.message || err);
      return res.status(500).json({ error: 'Erreur serveur' });
    }
  }

  return res.status(405).json({ error: 'Méthode non autorisée' });
}
