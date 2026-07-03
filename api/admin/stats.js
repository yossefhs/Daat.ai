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
    const { action, plan, value } = req.body;
    // NORMALISATION EMAIL : le JWT (chat) est toujours en minuscules+trim. Si l'admin
    // écrit une clé user:plan:{email} avec une autre casse, le chat ne la lira JAMAIS
    // → l'utilisateur reste 'free' malgré le plan. On normalise donc côté serveur.
    const email = String(req.body.email || '').trim().toLowerCase();

    if (action === 'set-plan' && email && plan) {
      await kv.set(`user:plan:${email}`, plan);
      await kv.sadd('users:known', email); // rendre visible dans l'admin même sans activité
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
      await kv.sadd('users:known', email);
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

    // Crédits Opus achetés (1 € = 1 question, permanents) — admin only
    if (action === 'add-credits' && email) {
      const delta = parseInt(req.body.amount, 10);
      if (!Number.isFinite(delta) || delta === 0) {
        return res.status(400).json({ error: 'amount requis (entier non nul, positif = ajouter, négatif = retirer)' });
      }
      const current = parseInt((await kv.get(`credits:${email}`)) || '0', 10);
      const newTotal = Math.max(0, current + delta);
      await kv.set(`credits:${email}`, newTotal);
      await kv.sadd('users:known', email); // rendre visible dans l'admin
      return res.json({
        success: true,
        email,
        credits: newTotal,
        added: delta,
        message: delta > 0
          ? `+${delta} crédits Opus pour ${email} (total : ${newTotal})`
          : `${delta} crédits Opus pour ${email} (total : ${newTotal})`,
      });
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
        const credits = isGuest ? 0 : parseInt((await kv.get(`credits:${id}`)) || '0', 10);
        const label = isGuest ? `Anonyme #${id.slice(-8)}` : id;
        return { email: id, label, plan, plan_expires: planExpires, force_opus: forceOpus, preview_used: previewUsed, credits, is_guest: isGuest, today_questions: rateCount, month_questions: monthCount, ...usage };
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

  // 4. USER DETAIL — recherche par email (fonctionne MÊME si l'email n'est pas
  // dans users:known). C'est l'outil pour vérifier "j'ai payé mais pas d'Opus".
  if (action === 'user-detail') {
    // Normaliser comme le JWT/webhook pour lire les bonnes clés
    const email = String(req.query.email || '').trim().toLowerCase();
    if (!email) return res.status(400).json({ error: 'email requis' });

    const dateRange = [];
    for (let i = 29; i >= 0; i--) dateRange.push(daysAgo(i));

    const days30 = await Promise.all(
      dateRange.map(async d => {
        const data = (await kv.get(`usage:${email}:${d}`)) || { tokens_in: 0, tokens_out: 0, cost_usd: 0, count: 0 };
        return { date: d, ...data };
      })
    );

    const d = today();
    const month = d.slice(0, 7);
    const [rawPlan, forceOpusRaw, planExpires, creditsRaw, previewRaw, accountRaw, todayRate, monthRate] = await Promise.all([
      kv.get(`user:plan:${email}`),
      kv.get(`user:force_opus:${email}`),
      kv.get(`user:plan_expires:${email}`),
      kv.get(`credits:${email}`),
      kv.get(`user:preview_used:${email}`),
      kv.get(`user:${email}`),
      kv.get(`rate:${email}:${d}`),
      kv.get(`rate-month:${email}:${month}`),
    ]);

    const plan = rawPlan || 'free';
    // L'utilisateur est-il "connu" (a un compte, un plan, des crédits, ou de l'activité) ?
    const exists = Boolean(accountRaw || rawPlan || (parseInt(creditsRaw || '0', 10) > 0) || parseInt(todayRate || '0', 10) > 0);
    // Le plan est-il expiré ? (même logique que le chat : comparaison de dates YYYY-MM-DD)
    let expired = false;
    if (plan !== 'lifetime' && plan !== 'free' && planExpires) {
      expired = d > String(planExpires).slice(0, 10);
    }

    return res.json({
      email,
      exists,
      plan,
      effective_plan: expired ? 'free' : plan,
      plan_expires: planExpires || null,
      expired,
      credits: parseInt(creditsRaw || '0', 10),
      force_opus: Boolean(forceOpusRaw),
      preview_used: parseInt(previewRaw || '0', 10),
      account: accountRaw || null,
      today_questions: parseInt(todayRate || '0', 10),
      month_questions: parseInt(monthRate || '0', 10),
      days: days30,
    });
  }

  return res.status(400).json({ error: 'action invalide' });
}
