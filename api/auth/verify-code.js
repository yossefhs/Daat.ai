// POST /api/auth/verify-code
// Body : { email, code }
// Vérifie le code, crée la session JWT, set le cookie httpOnly.

import { kv } from '@vercel/kv';
import {
  isValidEmail,
  signSession,
  setSessionCookie,
  setCorsHeaders,
} from '../_auth.js';

const MAX_ATTEMPTS = 5;

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  if (!process.env.JWT_SECRET) {
    return res.status(500).json({ error: 'JWT_SECRET non configuré côté serveur' });
  }

  try {
    const { email, code } = req.body || {};
    const cleanEmail = (email || '').trim().toLowerCase();
    const cleanCode = String(code || '').trim();

    if (!isValidEmail(cleanEmail)) {
      return res.status(400).json({ error: 'Adresse email invalide' });
    }
    if (!/^\d{6}$/.test(cleanCode)) {
      return res.status(400).json({ error: 'Le code doit faire 6 chiffres' });
    }

    const stored = await kv.get(`auth:code:${cleanEmail}`);
    if (!stored) {
      return res
        .status(400)
        .json({ error: 'Code expiré ou inexistant. Demande un nouveau code.' });
    }

    if (stored.attempts >= MAX_ATTEMPTS) {
      await kv.del(`auth:code:${cleanEmail}`);
      return res
        .status(429)
        .json({ error: 'Trop de tentatives échouées. Demande un nouveau code.' });
    }

    if (stored.code !== cleanCode) {
      stored.attempts += 1;
      await kv.set(`auth:code:${cleanEmail}`, stored, { ex: 600 });
      const remaining = MAX_ATTEMPTS - stored.attempts;
      return res.status(401).json({
        error: `Code incorrect. ${remaining} tentative(s) restante(s).`,
      });
    }

    // Code OK — supprime le code (one-shot)
    await kv.del(`auth:code:${cleanEmail}`);

    // Crée ou met à jour le user record
    const userKey = `user:${cleanEmail}`;
    const existing = await kv.get(userKey);
    const user = {
      email: cleanEmail,
      createdAt: existing?.createdAt || Date.now(),
      lastLoginAt: Date.now(),
    };
    await kv.set(userKey, user);

    // Génère et installe la session
    const token = signSession({ email: cleanEmail });
    setSessionCookie(res, token);

    return res.status(200).json({ ok: true, user: { email: cleanEmail } });
  } catch (err) {
    console.error('[auth/verify-code] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}
