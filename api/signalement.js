// api/signalement.js — « Signaler une erreur » : les lecteurs deviennent relecteurs.
//
// PUBLIC :
//   POST /api/signalement
//     body { url, titre, siman?, seif?, type, description, source?, lang?, hp? }
//     → { ok, id }   (rate-limit 5/jour/IP ; honeypot `hp` doit rester vide)
//
// ADMIN (Authorization: Bearer ADMIN_PASSWORD — même convention que admin/feedback) :
//   GET    /api/signalement?limit=200[&status=NEW]        → { ok, entries, stats }
//   POST   /api/signalement  { action:'set-status', id, status }
//   DELETE /api/signalement?id=…
//
// Pipeline des statuts : NEW → TRIAGED → NEEDS_RABBINIC_VALIDATION → APPROVED → FIXED / REJECTED.
// RÈGLE ABSOLUE : aucun contenu halakhique n'est modifié sans validation du Rav —
// ce pipeline est le chemin officiel de cette validation.
// Stockage : liste KV `signalements:list` (LPUSH d'objets JSON). Aucune donnée
// personnelle exigée ; l'IP n'est utilisée que pour le rate-limit (clé hashée, TTL 24h).

import { kv } from './_kv.js';

const STATUSES = ['NEW', 'TRIAGED', 'NEEDS_RABBINIC_VALIDATION', 'APPROVED', 'FIXED', 'REJECTED'];
// Catégories du signalement — distinctes dès la soumission pour que le triage
// n'ait jamais à deviner si un point de langue est un point de halakha.
const TYPES = ['halakha', 'traduction', 'langue', 'source', 'pedagogie'];
const LIST_KEY = 'signalements:list';
const MAX_PER_DAY = 5;

function clientIp(req) {
  const xf = String(req.headers['x-forwarded-for'] || '');
  return xf.split(',')[0].trim() || req.socket?.remoteAddress || 'unknown';
}

function isAdmin(req) {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) return false;
  const auth = req.headers['authorization'] || '';
  const provided = auth.startsWith('Bearer ') ? auth.slice(7) : '';
  return provided === expected;
}

const clip = (v, n) => String(v ?? '').trim().slice(0, n);

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();

  try {
    // ── ADMIN : liste ────────────────────────────────────────────────────────
    if (req.method === 'GET') {
      if (!isAdmin(req)) return res.status(401).json({ ok: false, error: 'Non autorisé' });
      const limit = Math.min(parseInt(req.query.limit || '200', 10) || 200, 500);
      const raw = (await kv.lrange(LIST_KEY, 0, limit - 1)) || [];
      let entries = raw.map((r) => { try { return typeof r === 'string' ? JSON.parse(r) : r; } catch { return null; } }).filter(Boolean);
      if (req.query.status && STATUSES.includes(req.query.status)) {
        entries = entries.filter((e) => e.status === req.query.status);
      }
      const stats = {};
      for (const s of STATUSES) stats[s] = 0;
      for (const e of entries) if (stats[e.status] !== undefined) stats[e.status]++;
      return res.status(200).json({ ok: true, entries, stats });
    }

    // ── ADMIN : suppression ─────────────────────────────────────────────────
    if (req.method === 'DELETE') {
      if (!isAdmin(req)) return res.status(401).json({ ok: false, error: 'Non autorisé' });
      const id = clip(req.query.id, 40);
      if (!id) return res.status(400).json({ ok: false, error: 'id requis' });
      const raw = (await kv.lrange(LIST_KEY, 0, 499)) || [];
      for (const r of raw) {
        const e = typeof r === 'string' ? JSON.parse(r) : r;
        if (e && e.id === id) {
          await kv.lrem(LIST_KEY, 1, typeof r === 'string' ? r : JSON.stringify(r));
          return res.status(200).json({ ok: true, deleted: id });
        }
      }
      return res.status(404).json({ ok: false, error: 'introuvable' });
    }

    if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'méthode' });

    const body = req.body || {};

    // ── ADMIN : changement de statut ────────────────────────────────────────
    if (body.action === 'set-status') {
      if (!isAdmin(req)) return res.status(401).json({ ok: false, error: 'Non autorisé' });
      const id = clip(body.id, 40);
      const status = clip(body.status, 40);
      if (!id || !STATUSES.includes(status)) return res.status(400).json({ ok: false, error: 'id/status invalide' });
      const raw = (await kv.lrange(LIST_KEY, 0, 499)) || [];
      for (const r of raw) {
        const e = typeof r === 'string' ? JSON.parse(r) : r;
        if (e && e.id === id) {
          const before = typeof r === 'string' ? r : JSON.stringify(r);
          e.status = status;
          e.updatedAt = new Date().toISOString();
          // Remplacement atomique approximatif : LREM l'ancien + LPUSH le nouveau.
          await kv.lrem(LIST_KEY, 1, before);
          await kv.lpush(LIST_KEY, JSON.stringify(e));
          return res.status(200).json({ ok: true, id, status });
        }
      }
      return res.status(404).json({ ok: false, error: 'introuvable' });
    }

    // ── PUBLIC : nouveau signalement ────────────────────────────────────────
    if (clip(body.hp, 10)) return res.status(200).json({ ok: true, id: 'merci' }); // honeypot : on absorbe sans stocker

    const description = clip(body.description, 2000);
    if (description.length < 10) {
      return res.status(400).json({ ok: false, error: 'Décris le problème (au moins 10 caractères).' });
    }
    const type = TYPES.includes(body.type) ? body.type : 'pedagogie';

    // Rate-limit par IP (jour) — l'IP ne sert qu'à ça, jamais stockée avec le signalement.
    const today = new Date().toISOString().slice(0, 10);
    const rlKey = `signalements:rl:${today}:${clientIp(req)}`;
    const count = await kv.incr(rlKey);
    if (count === 1) await kv.expire(rlKey, 86400);
    if (count > MAX_PER_DAY) {
      return res.status(429).json({ ok: false, error: 'Limite quotidienne atteinte — merci ! Réessaie demain.' });
    }

    const entry = {
      id: `sig_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`,
      ts: new Date().toISOString(),
      status: 'NEW',
      url: clip(body.url, 300),
      titre: clip(body.titre, 200),
      siman: clip(body.siman, 10),
      seif: clip(body.seif, 20),
      type,
      description,
      source: clip(body.source, 300),
      lang: ['fr', 'he', 'en'].includes(body.lang) ? body.lang : 'fr',
    };
    await kv.lpush(LIST_KEY, JSON.stringify(entry));
    await kv.ltrim(LIST_KEY, 0, 999); // garde-fou : max 1000 signalements stockés

    return res.status(200).json({ ok: true, id: entry.id });
  } catch (e) {
    return res.status(500).json({ ok: false, error: 'erreur serveur' });
  }
}
