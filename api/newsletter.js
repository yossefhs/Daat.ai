// POST /api/newsletter — Inscription à la newsletter DAAT
//
// Body JSON :
//   { email: string, source?: 'home' | 'siman' | ... }
//
// Stockage Vercel KV :
//   - newsletter:{email}      → { email, subscribedAt, source, confirmed: false, token }
//   - newsletter:list         → liste des emails (pour export)
//
// Envoie un email de bienvenue via Resend (si RESEND_API_KEY).
// Rate-limit : 3 inscriptions / IP / heure pour limiter le spam.

import { kv } from '@vercel/kv';
import { Resend } from 'resend';
import { randomBytes } from 'node:crypto';
import { getStepById } from './_email-sequence.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

function isValidEmail(s) {
  return typeof s === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) && s.length <= 254;
}

function getClientIp(req) {
  const fwd = req.headers['x-forwarded-for'];
  if (typeof fwd === 'string') return fwd.split(',')[0].trim();
  return req.socket?.remoteAddress || 'unknown';
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST uniquement' });
  }

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
      return res.status(429).json({ error: 'Trop d\'inscriptions depuis cette IP. Réessaie plus tard.' });
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
      sentSteps: [], // Sera mis à jour avec ['j0'] après envoi du welcome
    };

    await kv.set(`newsletter:${email}`, record);

    // Liste agrégée (limite douce : on append, pas de doublons puisque la clé email est unique)
    try {
      await kv.lpush('newsletter:list', email);
      await kv.ltrim('newsletter:list', 0, 9999);
    } catch (e) {
      console.warn('[newsletter] kv list push failed:', e?.message);
    }

    // Email de bienvenue (J0 — premier email de la séquence, best-effort)
    if (process.env.RESEND_API_KEY) {
      try {
        const resend = new Resend(process.env.RESEND_API_KEY);
        const fromEmail = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';
        const j0 = getStepById('j0').build();

        const result = await resend.emails.send({
          from: `DAAT <${fromEmail}>`,
          to: email,
          subject: j0.subject,
          html: j0.html,
          text: j0.text,
        });

        if (!result.error) {
          // Marque J0 comme envoyé pour que le cron ne le ré-envoie pas
          record.sentSteps = ['j0'];
          await kv.set(`newsletter:${email}`, record);
        }
      } catch (e) {
        console.warn('[newsletter] welcome email failed:', e?.message);
      }
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[newsletter] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
