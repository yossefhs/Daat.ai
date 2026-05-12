// /api/soutenir
//
// GET                  → renvoie le « Mur des Bâtisseurs » public (50 derniers)
// GET ?action=stats    → renvoie le total collecté du mois courant + objectif
// POST                 → ajoute un nouveau soutien (admin-only via SOUTIEN_ADMIN_SECRET)
//                        ou via webhook HelloAsso/Stripe/PayPal (à brancher plus tard)
//
// Stockage Vercel KV :
//   - soutien:wall              → liste JSON-stringified des records publics
//                                 (anonymisés au besoin), 100 derniers
//   - soutien:list              → liste de tous les IDs (audit interne)
//   - soutien:{id}              → record complet (pour audit interne)
//   - soutien:total:YYYY-MM     → total cumulé du mois (en centimes)
//   - soutien:count:YYYY-MM     → nombre de soutiens du mois

import { kv } from '@vercel/kv';
import { randomBytes } from 'node:crypto';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Secret');
}

// Vérifie le secret admin — accepte 3 formats :
//   - Authorization: Bearer <SOUTIEN_ADMIN_SECRET>  (historique, webhooks)
//   - x-admin-secret: <ADMIN_PASSWORD>              (header, admin UI)
//   - ?secret=<ADMIN_PASSWORD>                       (query, admin UI simple)
function isAuthed(req) {
  const adminPwd = process.env.ADMIN_PASSWORD;
  const soutienSecret = process.env.SOUTIEN_ADMIN_SECRET;

  const bearer = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  if (bearer && soutienSecret && bearer === soutienSecret) return true;
  if (bearer && adminPwd && bearer === adminPwd) return true;

  const headerSecret = req.headers['x-admin-secret'];
  if (headerSecret && adminPwd && headerSecret === adminPwd) return true;

  const qsSecret = req.query?.secret;
  if (qsSecret && adminPwd && qsSecret === adminPwd) return true;

  return false;
}

function clean(s, max = 200) {
  return String(s || '').trim().slice(0, max);
}

// Tags affichés sur le mur selon le type de soutien
const TYPE_TAGS = {
  don: 'Don ponctuel',
  'don-petit': 'Don ponctuel · 36 €',
  'don-moyen': 'Don ponctuel · 180 €',
  'don-grand': 'Don ponctuel · 360 €',
  'don-libre': 'Don libre',
  dedicace: 'Dédicace d\'étude',
  'dedicace-page': 'Dédicace · une page',
  'dedicace-siman': 'Dédicace · un siman',
  'dedicace-mois': 'Dédicace · un mois',
  'illoui-nichmat': 'לעילוי נשמת',
  'refoua-cheléma': 'לרפואה שלמה',
  hatslakha: 'להצלחה',
  tomeh: 'Tomeh Adaat',
  'tomeh-18': 'Tomeh Adaat · 18 €/mois',
  'tomeh-36': 'Tomeh Adaat · 36 €/mois',
  'tomeh-100': 'Tomeh Adaat · 100 €/mois',
};

function buildPublicRecord({ id, name, type, customTag, anonymous, createdAt }) {
  const displayName = anonymous ? 'Anonyme' : name;
  const tag = customTag || TYPE_TAGS[type] || 'Bâtisseur';
  return { id, name: displayName, tag, type, createdAt, anonymous: !!anonymous };
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  // ---- GET : mur public OU stats du mois OU liste admin ----
  if (req.method === 'GET') {
    // GET ?action=recent → liste des derniers dons (admin only, données complètes)
    if (req.query.action === 'recent') {
      if (!isAuthed(req)) return res.status(401).json({ error: 'Unauthorized' });
      try {
        const limit = Math.min(parseInt(req.query.limit || '50', 10), 200);
        const ids = (await kv.lrange('soutien:list', 0, limit - 1)) || [];
        const records = await Promise.all(
          ids.map(async (id) => {
            const r = await kv.get(`soutien:${id}`);
            return r || null;
          })
        );
        return res.status(200).json({ ok: true, records: records.filter(Boolean) });
      } catch (err) {
        console.error('[soutenir] recent error:', err);
        return res.status(500).json({ error: err?.message || 'Erreur serveur' });
      }
    }

    // GET ?action=stats → objectif mensuel + total collecté
    if (req.query.action === 'stats') {
      try {
        const now = new Date();
        const monthKey = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, '0')}`;
        const totalCents = parseInt((await kv.get(`soutien:total:${monthKey}`)) || 0, 10);
        const count = parseInt((await kv.get(`soutien:count:${monthKey}`)) || 0, 10);
        const target = parseInt(process.env.SOUTIEN_MONTHLY_TARGET || '800', 10);

        // Cache CDN court (2 min) — la barre n'a pas besoin d'être temps réel
        res.setHeader('Cache-Control', 's-maxage=120, stale-while-revalidate=300');
        return res.status(200).json({
          ok: true,
          month: monthKey,
          month_total: totalCents / 100,
          month_count: count,
          target,
          currency: 'EUR',
        });
      } catch (err) {
        console.error('[soutenir] stats error:', err);
        return res.status(500).json({ error: err?.message || 'Erreur serveur' });
      }
    }

    // GET (par défaut) → mur public
    try {
      const raw = (await kv.lrange('soutien:wall', 0, 49)) || [];
      const wall = raw
        .map((s) => {
          if (typeof s === 'string') {
            try { return JSON.parse(s); } catch { return null; }
          }
          return s; // déjà désérialisé par certains clients KV
        })
        .filter(Boolean);
      // Cache CDN court (5 min)
      res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=600');
      return res.status(200).json({ ok: true, wall, count: wall.length });
    } catch (err) {
      console.error('[soutenir] GET error:', err);
      return res.status(500).json({ error: err?.message || 'Erreur serveur' });
    }
  }

  // ---- POST : ajout d'un soutien (admin-only) ----
  if (req.method === 'POST') {
    if (!isAuthed(req)) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    try {
      const body = req.body || {};
      const name = clean(body.name, 100);
      const type = clean(body.type, 32);
      const customTag = clean(body.tag, 80) || null;
      const dedicace = clean(body.dedicace, 200) || null;
      const amount = body.amount != null ? Number(body.amount) : null;
      const anonymous = !!body.anonymous;

      if (!name && !anonymous) {
        return res.status(400).json({ error: 'name requis (ou anonymous: true)' });
      }
      if (!type) {
        return res.status(400).json({ error: 'type requis' });
      }

      const id = `s-${Date.now()}-${randomBytes(4).toString('hex')}`;
      const record = {
        id,
        name,
        type,
        customTag,
        amount,
        dedicace,
        anonymous,
        createdAt: new Date().toISOString(),
      };

      // Audit interne complet
      await kv.set(`soutien:${id}`, record);
      await kv.lpush('soutien:list', id);
      await kv.ltrim('soutien:list', 0, 9999);

      // Mur public (avec anonymisation)
      const publicRecord = buildPublicRecord(record);
      await kv.lpush('soutien:wall', JSON.stringify(publicRecord));
      await kv.ltrim('soutien:wall', 0, 99);

      // Compteurs mensuels pour la barre de progression
      if (amount && amount > 0) {
        const monthKey = `${new Date().getUTCFullYear()}-${String(new Date().getUTCMonth() + 1).padStart(2, '0')}`;
        await kv.incrby(`soutien:total:${monthKey}`, Math.round(amount * 100));
        await kv.incr(`soutien:count:${monthKey}`);
      }

      return res.status(200).json({ ok: true, id, public: publicRecord });
    } catch (err) {
      console.error('[soutenir] POST error:', err);
      return res.status(500).json({ error: err?.message || 'Erreur serveur' });
    }
  }

  // ---- DELETE : supprimer un soutien (admin-only) ----
  if (req.method === 'DELETE') {
    if (!isAuthed(req)) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    const id = clean(req.query.id, 64);
    if (!id) {
      return res.status(400).json({ error: 'id requis (?id=s-xxx)' });
    }

    try {
      const record = await kv.get(`soutien:${id}`);
      if (!record) {
        return res.status(404).json({ error: 'Don introuvable' });
      }

      // 1. Décrémenter les compteurs du mois où le don a été enregistré
      if (record.amount && record.amount > 0 && record.createdAt) {
        const d = new Date(record.createdAt);
        const monthKey = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
        const cents = Math.round(record.amount * 100);
        // incrby avec valeur négative = decrement
        await kv.incrby(`soutien:total:${monthKey}`, -cents);
        await kv.incrby(`soutien:count:${monthKey}`, -1);
      }

      // 2. Retirer du mur public (LREM avec le publicRecord JSON-stringified exact)
      const publicRecord = buildPublicRecord(record);
      try { await kv.lrem('soutien:wall', 0, JSON.stringify(publicRecord)); } catch (_) {}

      // 3. Retirer l'id de la liste d'audit
      try { await kv.lrem('soutien:list', 0, id); } catch (_) {}

      // 4. Supprimer le record détaillé
      await kv.del(`soutien:${id}`);

      return res.status(200).json({ ok: true, id, deleted: record });
    } catch (err) {
      console.error('[soutenir] DELETE error:', err);
      return res.status(500).json({ error: err?.message || 'Erreur serveur' });
    }
  }

  return res.status(405).json({ error: 'GET, POST ou DELETE uniquement' });
}
