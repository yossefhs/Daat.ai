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

import { kv } from './_kv.js';
import { randomBytes, createHash, timingSafeEqual } from 'node:crypto';
import {
  origineRefusee, refuserOrigine, corsAdmin, adminParJeton,
  freinage, echecAdmin, reussiteAdmin, refuser,
} from './_admin-gate.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Secret');
}

// Comparaison à temps constant : on compare les empreintes SHA-256, de longueur
// fixe, pour ne révéler par le temps de réponse ni le secret ni sa longueur.
function egal(a, b) {
  if (!a || !b) return false;
  const ha = createHash('sha256').update(String(a)).digest();
  const hb = createHash('sha256').update(String(b)).digest();
  return timingSafeEqual(ha, hb);
}

// Vérifie l'administrateur — trois voies :
//   - session du site (connexion par courriel, adresse dans ADMIN_EMAILS) ;
//   - Authorization: Bearer <SOUTIEN_ADMIN_SECRET ou ADMIN_PASSWORD>  (webhooks, page Paiements) ;
//   - X-Admin-Secret: <ADMIN_PASSWORD>                                (tableau de bord admin).
// ?secret= n'est PLUS accepté (1er octobre 2026) : dans une URL, le secret
// s'écrit dans les journaux d'accès, dans l'historique et part dans le Referer.
// Aucun appelant du dépôt ne s'en servait.
function isAuthed(req) {
  // L'administrateur connecté par courriel (JWT du site, adresse listée dans
  // ADMIN_EMAILS) — même voie que /api/admin/*. Le cookie de session étant
  // SameSite=None, il part aussi sur une requête déclenchée par une page tierce :
  // on ne l'accepte donc JAMAIS d'une origine étrangère. Sans variable définie,
  // adminParJeton rend null et rien ne change.
  if (!origineRefusee(req) && adminParJeton(req)) return true;

  const adminPwd = process.env.ADMIN_PASSWORD;
  const soutienSecret = process.env.SOUTIEN_ADMIN_SECRET;

  const bearer = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  if (egal(bearer, soutienSecret)) return true;
  if (egal(bearer, adminPwd)) return true;

  if (egal(req.headers['x-admin-secret'], adminPwd)) return true;

  return false;
}

// La porte des actions ADMIN — la même que /api/admin/* (api/_admin-gate.js),
// posée ici parce que ce point en était resté à l'état d'avant le 22 septembre
// 2026 : « Access-Control-Allow-Origin: * » sur les réponses admin, secret
// accepté dans l'URL, aucun freinage — c'est-à-dire un mot de passe que les
// navigateurs de visiteurs ordinaires pouvaient être employés à deviner.
// Dans l'ordre : refus d'une origine étrangère AVANT toute comparaison, puis
// freinage, puis vérification ; un échec est compté, un succès remet à zéro.
// Les actions PUBLIQUES (mur, statistiques du mois) n'y passent pas et gardent
// leur CORS ouvert : la page Soutenir les lit depuis daattorah.com.
async function porteAdmin(req, res) {
  res.removeHeader('Access-Control-Allow-Origin');
  corsAdmin(req, res, 'GET, POST, DELETE, OPTIONS', 'Content-Type, Authorization, X-Admin-Secret');
  if (origineRefusee(req)) { refuserOrigine(res); return false; }
  const frein = await freinage(req);
  if (frein.bloque) { refuser(res); return false; }
  if (!isAuthed(req)) {
    await echecAdmin(req);
    res.status(401).json({ error: 'Unauthorized' });
    return false;
  }
  await reussiteAdmin(req);
  return true;
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
      if (!(await porteAdmin(req, res))) return;
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

    // GET ?action=admin-all → consolidé manuels + HelloAsso (admin)
    //   ?since=YYYY-MM-DD (optionnel, par défaut 12 mois en arrière)
    //   ?source=manuel|helloasso (optionnel)
    if (req.query.action === 'admin-all') {
      if (!(await porteAdmin(req, res))) return;
      try {
        const sinceParam = req.query.since;
        const sourceFilter = req.query.source || 'all';
        const since = sinceParam
          ? new Date(sinceParam)
          : new Date(Date.now() - 365 * 24 * 60 * 60 * 1000);
        const sinceTs = since.getTime();

        const items = [];

        // 1. Dons manuels + virements Qonto via soutien:list (tagués par r.source)
        if (sourceFilter === 'all' || sourceFilter === 'manuel' || sourceFilter === 'qonto') {
          const ids = (await kv.lrange('soutien:list', 0, 9999)) || [];
          const recs = await Promise.all(
            ids.map(async (id) => {
              try { return await kv.get(`soutien:${id}`); } catch { return null; }
            })
          );
          for (const r of recs) {
            if (!r) continue;
            const src = r.source || 'manuel';
            // filtre explicite manuel|qonto : ne garder que la bonne source
            if (sourceFilter !== 'all' && src !== sourceFilter) continue;
            const ts = new Date(r.createdAt).getTime();
            if (ts < sinceTs) continue;
            items.push({
              source: src,
              ts: r.createdAt,
              email: null,
              name: r.anonymous ? '(anonyme)' : r.name,
              amount_eur: Number(r.amount) || 0,
              plan: r.type || '',
              recurring: false,
              dedicace: r.dedicace || '',
              orderId: r.id,
              eventType: '',
            });
          }
        }

        // 2. Paiements HelloAsso via logs:helloasso
        if (sourceFilter === 'all' || sourceFilter === 'helloasso') {
          const logs = (await kv.lrange('logs:helloasso', 0, 9999)) || [];
          for (const raw of logs) {
            let entry = raw;
            if (typeof raw === 'string') {
              try { entry = JSON.parse(raw); } catch { continue; }
            }
            if (!entry || !entry.ts) continue;
            const ts = new Date(entry.ts).getTime();
            if (ts < sinceTs) continue;
            items.push({
              source: 'helloasso',
              ts: entry.ts,
              email: entry.email || '',
              name: '',
              amount_eur: Number(entry.amount_eur) || 0,
              plan: entry.plan || '',
              recurring: !!entry.recurring,
              dedicace: '',
              orderId: entry.orderId || '',
              eventType: entry.eventType || '',
            });
          }
        }

        // Tri descendant par date
        items.sort((a, b) => new Date(b.ts) - new Date(a.ts));

        // Stats consolidées
        const stats = {
          total_count: items.length,
          total_eur: 0,
          by_source: { manuel: 0, helloasso: 0, qonto: 0 },
          by_plan: {},
          by_month: {},
          recurring_count: 0,
          unique_donors: new Set(),
        };
        for (const it of items) {
          stats.total_eur += it.amount_eur;
          stats.by_source[it.source] = (stats.by_source[it.source] || 0) + it.amount_eur;
          stats.by_plan[it.plan] = (stats.by_plan[it.plan] || 0) + it.amount_eur;
          const month = it.ts.slice(0, 7);
          stats.by_month[month] = (stats.by_month[month] || 0) + it.amount_eur;
          if (it.recurring) stats.recurring_count++;
          if (it.email) stats.unique_donors.add(it.email);
          if (it.name && it.name !== '(anonyme)') stats.unique_donors.add(it.name);
        }
        stats.unique_donors = stats.unique_donors.size;

        return res.status(200).json({
          ok: true,
          since: since.toISOString(),
          source_filter: sourceFilter,
          stats,
          items,
        });
      } catch (err) {
        console.error('[soutenir] admin-all error:', err);
        return res.status(500).json({ error: err?.message || 'Erreur serveur' });
      }
    }

    // GET ?action=stats → objectif mensuel + total collecté + URLs HelloAsso configurées
    if (req.query.action === 'stats') {
      try {
        const now = new Date();
        const monthKey = `${now.getUTCFullYear()}-${String(now.getUTCMonth() + 1).padStart(2, '0')}`;
        const totalCents = parseInt((await kv.get(`soutien:total:${monthKey}`)) || 0, 10);
        const count = parseInt((await kv.get(`soutien:count:${monthKey}`)) || 0, 10);
        const target = parseInt(process.env.SOUTIEN_MONTHLY_TARGET || '800', 10);

        // URLs HelloAsso configurables via env vars (Vercel Settings → Environment Variables)
        // Tant qu'une URL n'est pas configurée, on renvoie null → la card affichera un message
        // "à venir" et un fallback vers Qonto.
        const helloasso = {
          khavroutha:        process.env.HELLOASSO_FORM_KHAVROUTHA_URL        || null,
          beit_midrash:      process.env.HELLOASSO_FORM_BEIT_MIDRASH_URL      || null,
          beit_midrash_plus: process.env.HELLOASSO_FORM_BEIT_MIDRASH_PLUS_URL || null,
          yeshiva:           process.env.HELLOASSO_FORM_YESHIVA_URL           || null,
          lifetime:          process.env.HELLOASSO_FORM_LIFETIME_URL          || null,
        };

        // Cache CDN court (2 min) — la barre n'a pas besoin d'être temps réel
        res.setHeader('Cache-Control', 's-maxage=120, stale-while-revalidate=300');
        return res.status(200).json({
          ok: true,
          month: monthKey,
          month_total: totalCents / 100,
          month_count: count,
          target,
          currency: 'EUR',
          helloasso,
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
    if (!(await porteAdmin(req, res))) return;

    try {
      const body = req.body || {};
      const name = clean(body.name, 100);
      const type = clean(body.type, 32);
      const customTag = clean(body.tag, 80) || null;
      const dedicace = clean(body.dedicace, 200) || null;
      const amount = body.amount != null ? Number(body.amount) : null;
      const anonymous = !!body.anonymous;
      // Source optionnelle (manuel par défaut) + date optionnelle (sinon maintenant).
      const srcRaw = clean(body.source, 16).toLowerCase();
      const source = ['qonto', 'especes', 'manuel'].includes(srcRaw) ? srcRaw : null;
      const createdAt = body.date && /^\d{4}-\d{2}-\d{2}/.test(String(body.date))
        ? new Date(body.date).toISOString()
        : new Date().toISOString();

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
        source,
        anonymous,
        createdAt,
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
    if (!(await porteAdmin(req, res))) return;
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
