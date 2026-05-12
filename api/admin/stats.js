// api/admin/stats.js — Dashboard admin DAAT
// GET  /api/admin/stats?secret=XXX&days=7
// GET  /api/admin/stats?secret=XXX&action=users
// GET  /api/admin/stats?secret=XXX&action=logs&limit=50
// POST /api/admin/stats?secret=XXX  { action: 'set-plan', email, plan }
// POST /api/admin/stats?secret=XXX  { action: 'reset-limit', email }

import { kv } from '@vercel/kv';

function today() { return new Date().toISOString().slice(0, 10); }
function daysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

export default async function handler(req, res) {
  // ── AUTH ADMIN ────────────────────────────────────────────────────────────
  const secret = req.query.secret || req.headers['x-admin-secret'];
  if (!secret || secret !== process.env.ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Non autorisé' });
  }

  res.setHeader('Access-Control-Allow-Origin', '*');

  // ── POST — actions admin ──────────────────────────────────────────────────
  if (req.method === 'POST') {
    const { action, email, plan } = req.body;

    if (action === 'set-plan' && email && plan) {
      await kv.set(`user:plan:${email}`, plan);
      return res.json({ success: true, message: `Plan de ${email} → ${plan}` });
    }

    if (action === 'reset-limit' && email) {
      const key = `rate:${email}:${today()}`;
      await kv.set(key, 0);
      return res.json({ success: true, message: `Limite de ${email} réinitialisée` });
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

    const all = await Promise.all(
      knownIds.map(async id => {
        const isGuest = id.startsWith('guest_');
        if (isGuest && !includeGuests) return null;
        const usage = (await kv.get(`usage:${id}:${d}`)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        const rateCount = parseInt((await kv.get(`rate:${id}:${d}`)) || 0, 10);
        const plan = isGuest ? 'anonymous' : ((await kv.get(`user:plan:${id}`)) || 'free');
        // Label lisible : email tel quel, ou "Anonyme #abc12345" pour les guests
        const label = isGuest ? `Anonyme #${id.slice(-8)}` : id;
        return { email: id, label, plan, is_guest: isGuest, today_questions: rateCount, ...usage };
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
    const todayRate = (await kv.get(`rate:${email}:${today()}`)) || 0;

    return res.json({ email, plan, today_questions: todayRate, days: days30 });
  }

  return res.status(400).json({ error: 'action invalide' });
}
