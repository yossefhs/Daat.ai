// api/admin/stats.js — Dashboard admin DAAT
// GET  /api/admin/stats?secret=XXX&days=7
// GET  /api/admin/stats?secret=XXX&action=users
// GET  /api/admin/stats?secret=XXX&action=logs&limit=50
// POST /api/admin/stats?secret=XXX  { action: 'set-plan', email, plan }
// POST /api/admin/stats?secret=XXX  { action: 'set-force-opus', email, value: true|false }
// POST /api/admin/stats?secret=XXX  { action: 'reset-limit', email }

import { kv } from '../_kv.js';

function today() { return new Date().toISOString().slice(0, 10); }
function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

export default async function handler(req, res) {
  // ── CORS (toujours en premier, AVANT toute auth) ─────────────────────────
  // Sinon le browser fait un preflight OPTIONS qui se prend un 401 et
  // n'envoie jamais la vraie requête (échec silencieux côté front).
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-admin-secret, Authorization');
  res.setHeader('Access-Control-Max-Age', '86400');
  if (req.method === 'OPTIONS') return res.status(204).end();

  // ── AUTH ADMIN ────────────────────────────────────────────────────────────
  const secret = req.query.secret || req.headers['x-admin-secret'];
  if (!secret || secret !== process.env.ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Non autorisé' });
  }

  // ── POST — actions admin ──────────────────────────────────────────────────
  if (req.method === 'POST') {
    const { action, email, plan, value } = req.body;

    if (action === 'set-plan' && email && plan) {
      await kv.set(`user:plan:${email}`, plan);
      // Date d'expiration optionnelle (pour les abonnements mensuels manuels Qonto)
      if (req.body.expires) {
        await kv.set(`user:plan_expires:${email}`, req.body.expires);
      } else if (req.body.expires === null || req.body.expires === '') {
        await kv.del(`user:plan_expires:${email}`);
      }
      return res.json({ success: true, message: `Plan de ${email} → ${plan}` });
    }

    if (action === 'set-force-opus' && email && typeof value === 'boolean') {
      if (value) {
        await kv.set(`user:force_opus:${email}`, '1');
      } else {
        await kv.del(`user:force_opus:${email}`);
      }
      return res.json({ success: true, message: `Forcer Opus pour ${email} : ${value ? 'ON' : 'OFF'}` });
    }

    if (action === 'reset-limit' && email) {
      const key = `rate:${email}:${today()}`;
      await kv.set(key, 0);
      return res.json({ success: true, message: `Limite de ${email} réinitialisée` });
    }

    if (action === 'reset-preview' && email) {
      await kv.del(`user:preview_used:${email}`);
      return res.json({ success: true, message: `Compteur Aperçu Premium de ${email} remis à 0 (3 questions Opus offertes restaurées)` });
    }

    return res.status(400).json({ error: 'Action inconnue' });
  }

  // ── GET — récupérer les stats ─────────────────────────────────────────────
  const action = req.query.action || 'overview';
  const days   = parseInt(req.query.days || '7', 10);

  // 1. OVERVIEW — stats des N derniers jours
  if (action === 'overview') {
    const dateRange = [];
    for (let i = days - 1; i >= 0; i--) dateRange.push(daysAgo(i));

    const results = await Promise.all(
      dateRange.map(async d => {
        const data = (await kv.get(`usage:global:${d}`)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        return { date: d, ...data };
      })
    );

    const totals = results.reduce((acc, r) => ({
      tokens_in:  acc.tokens_in  + r.tokens_in,
      tokens_out: acc.tokens_out + r.tokens_out,
      cost_usd:   +(acc.cost_usd  + r.cost_usd).toFixed(4),
      count:      acc.count + r.count
    }), { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 });

    return res.json({ days: results, totals });
  }

  // 2. USERS — liste des utilisateurs connus avec stats aujourd'hui
  if (action === 'users') {
    const knownIds = await kv.smembers('users:known') || [];
    const d = today();
    const includeGuests = req.query.guests !== 'false'; // par défaut on inclut

    const month = d.slice(0, 7);
    const all = await Promise.all(
      knownIds.map(async id => {
        const isGuest = id.startsWith('guest_');
        if (isGuest && !includeGuests) return null;
        const usage = (await kv.get(`usage:${id}:${d}`)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        const rateCount = parseInt((await kv.get(`rate:${id}:${d}`)) || 0, 10);
        const monthCount = parseInt((await kv.get(`rate-month:${id}:${month}`)) || 0, 10);
        const previewUsed = parseInt((await kv.get(`user:preview_used:${id}`)) || 0, 10);
        const plan = isGuest ? 'anonymous' : ((await kv.get(`user:plan:${id}`)) || 'free');
        const forceOpus = isGuest ? false : Boolean(await kv.get(`user:force_opus:${id}`));
        const planExpires = isGuest ? null : await kv.get(`user:plan_expires:${id}`);
        const label = isGuest ? `Anonyme #${id.slice(-8)}` : id;
        return { email: id, label, plan, plan_expires: planExpires, force_opus: forceOpus, preview_used: previewUsed, is_guest: isGuest, today_questions: rateCount, month_questions: monthCount, ...usage };
      })
    );

    const users = all.filter(Boolean);
    users.sort((a, b) => b.today_questions - a.today_questions);

    const stats = {
      total: users.length,
      guests: users.filter(u => u.is_guest).length,
      registered: users.filter(u => !u.is_guest).length,
    };
    return res.json({ users, total: users.length, stats, date: d });
  }

  // 3. LOGS — dernières requêtes
  if (action === 'logs') {
    const limit = Math.min(parseInt(req.query.limit || '50', 10), 200);
    const raw = await kv.lrange('logs:usage', 0, limit - 1);
    const logs = raw.map(r => {
      try { return typeof r === 'string' ? JSON.parse(r) : r; }
      catch (_) { return r; }
    });
    return res.json({ logs, total: logs.length });
  }

  // 3b. PAIEMENTS HELLOASSO — auto-upgrades reçus par webhook
  if (action === 'payments') {
    const limit = Math.min(parseInt(req.query.limit || '50', 10), 200);
    const [rawPayments, rawUnmatched] = await Promise.all([
      kv.lrange('logs:helloasso', 0, limit - 1),
      kv.lrange('logs:helloasso-unmatched', 0, Math.min(limit, 50) - 1),
    ]);
    const parse = (arr) => arr.map(r => {
      try { return typeof r === 'string' ? JSON.parse(r) : r; }
      catch (_) { return r; }
    });
    return res.json({
      payments: parse(rawPayments),
      unmatched: parse(rawUnmatched),
    });
  }

  // 4. USER DETAIL — stats sur 30 jours pour un utilisateur
  if (action === 'user-detail') {
    const email = req.query.email;
    if (!email) return res.status(400).json({ error: 'email requis' });

    const dateRange = [];
    for (let i = 29; i >= 0; i--) dateRange.push(daysAgo(i));

    const days30 = await Promise.all(
      dateRange.map(async d => {
        const data = (await kv.get(`usage:${email}:${d}`)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        return { date: d, ...data };
      })
    );

    const plan = (await kv.get(`user:plan:${email}`)) || 'free';
    const forceOpus = Boolean(await kv.get(`user:force_opus:${email}`));
    const todayRate = (await kv.get(`rate:${email}:${today()}`)) || 0;

    return res.json({ email, plan, force_opus: forceOpus, today_questions: todayRate, days: days30 });
  }

  return res.status(400).json({ error: 'action invalide' });
}
