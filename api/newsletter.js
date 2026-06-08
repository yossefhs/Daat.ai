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

    // Email de bienvenue J0 (best-effort, le cron rattrape si échec)
    if (!process.env.RESEND_API_KEY) {
      console.warn('[newsletter] RESEND_API_KEY absent — J0 non envoyé, cron rattrapera');
    } else {
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

        if (result.error) {
          console.error('[newsletter] Resend a renvoyé une erreur sur J0:', {
            email,
            error: result.error?.message || result.error,
            name: result.error?.name,
          });
        } else {
          record.sentSteps = ['j0'];
          await kv.set(`newsletter:${email}`, record);
          console.log('[newsletter] J0 envoyé OK', { email, resendId: result.data?.id });
        }
      } catch (e) {
        console.error('[newsletter] exception lors de l\'envoi J0:', {
          email,
          message: e?.message,
          name: e?.name,
        });
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

    return res.status(200).json({
      ok: true,
      processed,
      sent,
      errors,
      log: log.slice(0, 50),
    });
  } catch (err) {
    console.error('[newsletter/cron] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur cron' });
  }
}

// ---------- GET ?action=stats : lecture admin (ADMIN_PASSWORD ou SOUTIEN_ADMIN_SECRET) ----------
async function handleStats(req, res) {
  const auth = req.headers.authorization || '';
  const expected = process.env.ADMIN_PASSWORD || process.env.SOUTIEN_ADMIN_SECRET;
  if (!expected) {
    return res.status(500).json({ error: 'ADMIN_PASSWORD non configuré' });
  }
  if (auth !== `Bearer ${expected}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const emails = (await kv.lrange('newsletter:list', 0, 9999)) || [];
    const uniqueEmails = [...new Set(emails)];

    const recent = [];
    let confirmed = 0;
    let sentJ0 = 0;
    let sentJ14 = 0;
    const stepCounts = { j0: 0, j3: 0, j7: 0, j10: 0, j14: 0 };

    for (const email of uniqueEmails) {
      const r = await kv.get(`newsletter:${email}`);
      if (!r) continue;
      if (r.confirmed) confirmed++;
      const steps = r.sentSteps || [];
      for (const s of steps) if (s in stepCounts) stepCounts[s]++;
      if (steps.includes('j0')) sentJ0++;
      if (steps.includes('j14')) sentJ14++;
      recent.push({
        email: email.replace(/^(.)(.*)(@.*)$/, (_, a, b, c) => a + '*'.repeat(b.length) + c),
        subscribedAt: r.subscribedAt,
        source: r.source,
        sentSteps: steps,
      });
    }

    recent.sort((a, b) => (b.subscribedAt || '').localeCompare(a.subscribedAt || ''));

    return res.status(200).json({
      ok: true,
      total: uniqueEmails.length,
      confirmed,
      sentJ0,
      sentJ14,
      stepCounts,
      recent: recent.slice(0, 20),
    });
  } catch (err) {
    console.error('[newsletter/stats] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur stats' });
  }
}

// ---------- dispatcher ----------
export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method === 'POST') return handleSignup(req, res);
  if (req.method === 'GET') {
    const url = new URL(req.url, 'http://x');
    if (url.searchParams.get('action') === 'stats') return handleStats(req, res);
    return handleCron(req, res);
  }
  return res.status(405).json({ error: 'GET ou POST uniquement' });
}
