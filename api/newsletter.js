// /api/newsletter — Newsletter DAAT (signup public + cron de séquence)
//
// Deux modes selon la méthode HTTP :
//   POST /api/newsletter        → inscription publique (body { email, source? })
//   GET  /api/newsletter        → exécution du cron de séquence
//                                 (auth via header Authorization: Bearer ${CRON_SECRET})
//
// Cette fusion permet de rester sous la limite de 12 fonctions Vercel
// Hobby tout en regroupant le système de séquence email dans un seul
// fichier (signup envoie J0, cron envoie J3 → J14).
//
// Stockage Vercel KV :
//   - newsletter:{email}      → { email, subscribedAt, source, confirmed, sentSteps[] }
//   - newsletter:list         → liste des emails (pour le cron)
//
// Cron Vercel : pointe vers /api/newsletter (le header Bearer fait le tri).

import { kv } from './_kv.js';
import { Resend } from 'resend';
import { randomBytes } from 'node:crypto';
import { getStepById, getDueSteps } from './_email-sequence.js';
import { getClientIp } from './_http.js';
import { buildWeeklyEmail, getSiman, nextValidSiman, WEEKLY_DEFAULTS } from './_newsletter-weekly.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

function isValidEmail(s) {
  return typeof s === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) && s.length <= 254;
}

// ---------- POST : inscription publique ----------
async function handleSignup(req, res) {
  try {
    const body = req.body || {};
    const email = String(body.email || '').trim().toLowerCase();
    const source = String(body.source || 'home').slice(0, 32);

    if (!isValidEmail(email)) {
      return res.status(400).json({ error: 'Adresse email invalide' });
    }

    // Rate-limit par IP
    const ip = getClientIp(req);
    const ipKey = `newsletter:rl:${ip}`;
    const count = (await kv.incr(ipKey)) || 1;
    if (count === 1) await kv.expire(ipKey, 3600);
    if (count > 3) {
      return res.status(429).json({
        error: "Trop d'inscriptions depuis cette IP. Réessaie plus tard.",
      });
    }

    // Déjà inscrit ?
    const existing = await kv.get(`newsletter:${email}`);
    if (existing) {
      return res.status(200).json({ ok: true, alreadySubscribed: true });
    }

    const token = randomBytes(16).toString('hex');
    const record = {
      email,
      source,
      subscribedAt: new Date().toISOString(),
      confirmed: true, // Single opt-in pour l'instant
      token,
      sentSteps: [], // Mis à jour avec ['j0'] après envoi du welcome
    };

    await kv.set(`newsletter:${email}`, record);

    try {
      await kv.lpush('newsletter:list', email);
      await kv.ltrim('newsletter:list', 0, 9999);
    } catch (e) {
      console.warn('[newsletter] kv list push failed:', e?.message);
    }

    // Email de bienvenue J0 (best-effort)
    if (process.env.RESEND_API_KEY) {
      try {
        const resend = new Resend(process.env.RESEND_API_KEY);
        const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';
        const j0 = getStepById('j0').build();

        const result = await resend.emails.send({
          from: `DAAT <${fromEmail}>`,
          to: email,
          subject: j0.subject,
          html: j0.html,
          text: j0.text,
        });

        if (!result.error) {
          record.sentSteps = ['j0'];
          await kv.set(`newsletter:${email}`, record);
        }
      } catch (e) {
        console.warn('[newsletter] welcome email failed:', e?.message);
      }
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[newsletter/signup] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}

// ---------- GET (Bearer) : cron de séquence ----------
async function handleCron(req, res) {
  // Auth — Vercel envoie ce header automatiquement sur les déclenchements de cron
  const auth = req.headers.authorization || '';
  const expectedSecret = process.env.CRON_SECRET;
  if (!expectedSecret) {
    return res.status(500).json({ error: 'CRON_SECRET non configuré côté serveur' });
  }
  if (auth !== `Bearer ${expectedSecret}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({ error: 'RESEND_API_KEY non configuré' });
  }

  const resend = new Resend(process.env.RESEND_API_KEY);
  const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';

  let processed = 0;
  let sent = 0;
  let errors = 0;
  const log = [];

  try {
    const emails = (await kv.lrange('newsletter:list', 0, 9999)) || [];
    const uniqueEmails = [...new Set(emails)];

    for (const email of uniqueEmails) {
      processed++;
      try {
        const record = await kv.get(`newsletter:${email}`);
        if (!record || !record.confirmed) continue;

        const due = getDueSteps(record.subscribedAt, record.sentSteps || []);
        if (!due.length) continue;

        // Au plus 1 step par run (anti-spam si l'utilisateur s'inscrit puis
        // le cron tourne 14 jours plus tard)
        const step = due[0];
        const tpl = step.build();

        const result = await resend.emails.send({
          from: `DAAT <${fromEmail}>`,
          to: email,
          subject: tpl.subject,
          html: tpl.html,
          text: tpl.text,
        });

        if (result.error) {
          errors++;
          log.push({ email, step: step.id, error: result.error.message });
          continue;
        }

        const updated = {
          ...record,
          sentSteps: [...(record.sentSteps || []), step.id],
        };
        await kv.set(`newsletter:${email}`, updated);

        sent++;
        log.push({ email, step: step.id, ok: true });
      } catch (e) {
        errors++;
        log.push({ email, error: e?.message });
      }
    }

    // Dimanche : on envoie en plus le « siman du dimanche » à tous les abonnés.
    let weekly = null;
    if (new Date().getUTCDay() === 0) {
      try {
        weekly = await runWeeklyBroadcast(resend, fromEmail, { mode: 'auto' });
      } catch (e) {
        weekly = { error: e?.message };
      }
    }

    return res.status(200).json({
      ok: true,
      processed,
      sent,
      errors,
      weekly,
      log: log.slice(0, 50),
    });
  } catch (err) {
    console.error('[newsletter/cron] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur cron' });
  }
}

// ---------- broadcast hebdomadaire (« siman du dimanche ») ----------
function todayStr() {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD (UTC)
}

async function getConfirmedEmails() {
  const emails = (await kv.lrange('newsletter:list', 0, 9999)) || [];
  const out = [];
  for (const email of [...new Set(emails)]) {
    const rec = await kv.get(`newsletter:${email}`);
    if (rec && rec.confirmed) out.push(email);
  }
  return out;
}

// mode: 'auto' (cron dimanche) · 'force' · 'test' · 'preview'
async function runWeeklyBroadcast(resend, fromEmail, { mode = 'auto', testTo = null } = {}) {
  const cursor = Number(await kv.get('newsletter:weekly:cursor')) || WEEKLY_DEFAULTS.FIRST_SIMAN;
  const num = nextValidSiman(cursor);
  if (!num) return { ok: true, done: true, message: 'Série terminée (siman 365 atteint).' };

  const mail = buildWeeklyEmail(getSiman(num));
  if (mode === 'preview') {
    return { ok: true, preview: true, siman: num, subject: mail.subject, html: mail.html };
  }

  // Anti-doublon : un seul envoi par jour calendaire (sauf force / test).
  if (mode === 'auto') {
    const last = await kv.get('newsletter:weekly:lastSentDate');
    if (last === todayStr()) return { ok: true, skipped: 'already-sent-today', siman: num };
  }

  const recipients = mode === 'test' ? (testTo ? [testTo] : []) : await getConfirmedEmails();
  if (!recipients.length) return { ok: true, siman: num, sent: 0, message: 'Aucun destinataire.' };

  let sent = 0, errors = 0;
  const log = [];
  for (const email of recipients) {
    try {
      const r = await resend.emails.send({
        from: `DAAT <${fromEmail}>`,
        to: email,
        subject: mail.subject,
        html: mail.html,
        text: mail.text,
      });
      if (r.error) { errors++; log.push({ email, error: r.error.message }); }
      else sent++;
    } catch (e) { errors++; log.push({ email, error: e?.message }); }
  }

  // En test : on n'avance ni le curseur ni la date.
  if (mode !== 'test') {
    await kv.set('newsletter:weekly:lastSentDate', todayStr());
    const next = nextValidSiman(num + 1);
    await kv.set('newsletter:weekly:cursor', next || (WEEKLY_DEFAULTS.LAST_SIMAN + 1));
  }

  return { ok: true, mode, siman: num, recipients: recipients.length, sent, errors, log: log.slice(0, 20) };
}

// ---------- GET : cron quotidien + actions admin du broadcast ----------
async function handleGet(req, res) {
  const expectedSecret = process.env.CRON_SECRET;
  const auth = req.headers.authorization || '';
  const qSecret = (req.query && req.query.secret) || '';
  const authorized = !!expectedSecret && (auth === `Bearer ${expectedSecret}` || qSecret === expectedSecret);

  const weekly = req.query && req.query.weekly;
  if (weekly) {
    if (!authorized) return res.status(401).json({ error: 'Unauthorized' });
    if (!process.env.RESEND_API_KEY) return res.status(500).json({ error: 'RESEND_API_KEY non configuré' });
    const resend = new Resend(process.env.RESEND_API_KEY);
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';

    if (weekly === 'preview') {
      const r = await runWeeklyBroadcast(resend, fromEmail, { mode: 'preview' });
      if (r.html) { res.setHeader('Content-Type', 'text/html; charset=utf-8'); return res.status(200).send(r.html); }
      return res.status(200).json(r);
    }
    if (weekly === 'test') {
      const to = req.query && req.query.to;
      if (!to) return res.status(400).json({ error: 'Paramètre ?to=email requis' });
      return res.status(200).json(await runWeeklyBroadcast(resend, fromEmail, { mode: 'test', testTo: String(to) }));
    }
    if (weekly === 'force') {
      return res.status(200).json(await runWeeklyBroadcast(resend, fromEmail, { mode: 'force' }));
    }
    return res.status(400).json({ error: 'weekly invalide (preview | test | force)' });
  }

  // Sinon : exécution normale du cron (séquence + dimanche → broadcast).
  return handleCron(req, res);
}

// ---------- dispatcher ----------
export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method === 'POST') return handleSignup(req, res);
  if (req.method === 'GET')  return handleGet(req, res);
  return res.status(405).json({ error: 'GET ou POST uniquement' });
}
