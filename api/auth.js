// /api/auth — dispatcher unique pour les 4 actions d'authentification.
//
// Consolidation de api/auth/{send-code, verify-code, me, logout}.js en
// un seul handler pour respecter la limite de 12 fonctions Vercel Hobby.
//
// URLs publiques préservées via rewrites dans vercel.json :
//   /api/auth/send-code   → /api/auth?action=send-code
//   /api/auth/verify-code → /api/auth?action=verify-code
//   /api/auth/me          → /api/auth?action=me
//   /api/auth/logout      → /api/auth?action=logout
//
// On peut aussi appeler directement /api/auth?action=… si besoin.

import { kv } from '@vercel/kv';
import { Resend } from 'resend';
import {
  generateCode,
  isValidEmail,
  checkSendRateLimit,
  signSession,
  setSessionCookie,
  clearSessionCookie,
  getUserFromRequest,
  setCorsHeaders,
} from './_auth.js';

const MAX_VERIFY_ATTEMPTS = 5;

// ---------- send-code ----------
async function handleSendCode(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({ error: 'RESEND_API_KEY non configuré côté serveur' });
  }
  if (!process.env.JWT_SECRET) {
    return res.status(500).json({ error: 'JWT_SECRET non configuré côté serveur' });
  }

  try {
    const { email } = req.body || {};
    const cleanEmail = (email || '').trim().toLowerCase();

    if (!isValidEmail(cleanEmail)) {
      return res.status(400).json({ error: 'Adresse email invalide' });
    }

    const ok = await checkSendRateLimit(cleanEmail);
    if (!ok) {
      return res.status(429).json({
        error: 'Trop de codes demandés. Réessaie dans 15 minutes.',
      });
    }

    const code = generateCode();
    await kv.set(`auth:code:${cleanEmail}`, { code, attempts: 0 }, { ex: 600 });

    const resend = new Resend(process.env.RESEND_API_KEY);
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';

    const html = `<!DOCTYPE html>
<html><body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background:#FAF6EE;margin:0;padding:24px;">
  <div style="max-width:480px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:32px;">
    <div style="display:flex;align-items:baseline;gap:12px;padding-bottom:16px;border-bottom:2px solid #C5A55A;margin-bottom:24px;">
      <span style="font-family:'Frank Ruhl Libre',Georgia,serif;font-size:32px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-size:14px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT</span>
    </div>
    <p style="color:#1A1F3A;font-size:16px;line-height:1.6;">Bonjour,</p>
    <p style="color:#3D4266;font-size:15px;line-height:1.6;">Voici ton code de connexion à <strong style="color:#1A1F3A;">DAAT</strong> :</p>
    <div style="font-family:'Menlo','Courier New',monospace;font-size:38px;font-weight:700;letter-spacing:12px;background:#FAF6EE;color:#1A1F3A;padding:24px;text-align:center;border-radius:6px;margin:24px 0;border:1px solid #C5A55A;">${code}</div>
    <p style="color:#3D4266;font-size:14px;line-height:1.6;">Ce code expire dans <strong>10 minutes</strong>. Saisis-le dans la fenêtre de connexion ouverte sur le site.</p>
    <p style="color:#888;font-size:12px;line-height:1.6;margin-top:32px;padding-top:16px;border-top:1px solid #E4DDD0;">Si tu n'as pas demandé cette connexion, ignore cet email. Personne ne pourra accéder à ton compte sans ce code.</p>
    <p style="color:#aaa;font-size:11px;line-height:1.6;margin-top:24px;text-align:center;">דעת DAAT · daattorah.com</p>
  </div>
</body></html>`;

    const result = await resend.emails.send({
      from: `DAAT <${fromEmail}>`,
      to: cleanEmail,
      subject: `Ton code DAAT : ${code}`,
      html,
      text: `Ton code de connexion à DAAT : ${code}\n\nCe code expire dans 10 minutes.\n\nSi tu n'as pas demandé cette connexion, ignore cet email.\n\n— DAAT דעת · daattorah.com`,
    });

    if (result.error) {
      console.error('[auth/send-code] Resend error:', result.error);
      return res.status(500).json({ error: "Impossible d'envoyer l'email. Vérifie l'adresse." });
    }

    return res.status(200).json({ ok: true, sentTo: cleanEmail });
  } catch (err) {
    console.error('[auth/send-code] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}

// ---------- verify-code ----------
async function handleVerifyCode(req, res) {
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
      return res.status(400).json({
        error: 'Code expiré ou inexistant. Demande un nouveau code.',
      });
    }

    if (stored.attempts >= MAX_VERIFY_ATTEMPTS) {
      await kv.del(`auth:code:${cleanEmail}`);
      return res.status(429).json({
        error: 'Trop de tentatives échouées. Demande un nouveau code.',
      });
    }

    if (stored.code !== cleanCode) {
      stored.attempts += 1;
      await kv.set(`auth:code:${cleanEmail}`, stored, { ex: 600 });
      const remaining = MAX_VERIFY_ATTEMPTS - stored.attempts;
      return res.status(401).json({
        error: `Code incorrect. ${remaining} tentative(s) restante(s).`,
      });
    }

    await kv.del(`auth:code:${cleanEmail}`);

    const userKey = `user:${cleanEmail}`;
    const existing = await kv.get(userKey);
    const user = {
      email: cleanEmail,
      createdAt: existing?.createdAt || Date.now(),
      lastLoginAt: Date.now(),
    };
    await kv.set(userKey, user);

    const token = signSession({ email: cleanEmail });
    setSessionCookie(res, token);

    return res.status(200).json({ ok: true, user: { email: cleanEmail } });
  } catch (err) {
    console.error('[auth/verify-code] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}

// ---------- me ----------
async function handleMe(req, res) {
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET uniquement' });
  const user = getUserFromRequest(req);
  if (!user) return res.status(401).json({ error: 'Non authentifié' });
  return res.status(200).json({ user });
}

// ---------- logout ----------
async function handleLogout(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });
  clearSessionCookie(res);
  return res.status(200).json({ ok: true });
}

// ---------- dispatcher ----------
export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  // Vercel parse query string dans req.query, mais on supporte aussi le path
  // au cas où le rewrite ne s'active pas (sur GitHub Pages par exemple).
  const action = (req.query?.action || '').toString();

  switch (action) {
    case 'send-code':   return handleSendCode(req, res);
    case 'verify-code': return handleVerifyCode(req, res);
    case 'me':          return handleMe(req, res);
    case 'logout':      return handleLogout(req, res);
    default:
      return res.status(400).json({
        error: 'Paramètre action requis (send-code, verify-code, me, logout)',
      });
  }
}
