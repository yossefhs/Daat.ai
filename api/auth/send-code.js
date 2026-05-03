// POST /api/auth/send-code
// Body : { email }
// Génère un code à 6 chiffres, le stocke en KV (TTL 10 min), l'envoie par email via Resend.

import { kv } from '@vercel/kv';
import { Resend } from 'resend';
import {
  generateCode,
  isValidEmail,
  checkSendRateLimit,
  setCorsHeaders,
} from '../_auth.js';

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();
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

    // Rate limit : max 3 codes / email / 15 min
    const ok = await checkSendRateLimit(cleanEmail);
    if (!ok) {
      return res
        .status(429)
        .json({ error: 'Trop de codes demandés. Réessaie dans 15 minutes.' });
    }

    const code = generateCode();
    // Stockage 10 min, attempts = 0
    await kv.set(`auth:code:${cleanEmail}`, { code, attempts: 0 }, { ex: 600 });

    const resend = new Resend(process.env.RESEND_API_KEY);
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';

    const html = `
<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; background: #FAF6EE; margin: 0; padding: 24px;">
  <div style="max-width: 480px; margin: 0 auto; background: #fff; border: 1px solid #E4DDD0; border-radius: 8px; padding: 32px;">
    <div style="display: flex; align-items: baseline; gap: 12px; padding-bottom: 16px; border-bottom: 2px solid #C5A55A; margin-bottom: 24px;">
      <span style="font-family: 'Frank Ruhl Libre', Georgia, serif; font-size: 32px; font-weight: 700; color: #C5A55A;">דעת</span>
      <span style="font-size: 14px; font-weight: 600; color: #1A1F3A; letter-spacing: 4px;">DAAT</span>
    </div>
    <p style="color: #1A1F3A; font-size: 16px; line-height: 1.6;">Bonjour,</p>
    <p style="color: #3D4266; font-size: 15px; line-height: 1.6;">Voici ton code de connexion à <strong style="color: #1A1F3A;">DAAT</strong> :</p>
    <div style="font-family: 'Menlo', 'Courier New', monospace; font-size: 38px; font-weight: 700; letter-spacing: 12px; background: #FAF6EE; color: #1A1F3A; padding: 24px; text-align: center; border-radius: 6px; margin: 24px 0; border: 1px solid #C5A55A;">
      ${code}
    </div>
    <p style="color: #3D4266; font-size: 14px; line-height: 1.6;">Ce code expire dans <strong>10 minutes</strong>. Saisis-le dans la fenêtre de connexion ouverte sur le site.</p>
    <p style="color: #888; font-size: 12px; line-height: 1.6; margin-top: 32px; padding-top: 16px; border-top: 1px solid #E4DDD0;">Si tu n'as pas demandé cette connexion, ignore cet email. Personne ne pourra accéder à ton compte sans ce code.</p>
    <p style="color: #aaa; font-size: 11px; line-height: 1.6; margin-top: 24px; text-align: center;">דעת DAAT · daattorah.com</p>
  </div>
</body>
</html>
    `.trim();

    const result = await resend.emails.send({
      from: `DAAT <${fromEmail}>`,
      to: cleanEmail,
      subject: `Ton code DAAT : ${code}`,
      html,
      text: `Ton code de connexion à DAAT : ${code}\n\nCe code expire dans 10 minutes.\n\nSi tu n'as pas demandé cette connexion, ignore cet email.\n\n— DAAT דעת · daattorah.com`,
    });

    if (result.error) {
      console.error('[auth/send-code] Resend error:', result.error);
      return res
        .status(500)
        .json({ error: "Impossible d'envoyer l'email. Vérifie l'adresse." });
    }

    return res.status(200).json({ ok: true, sentTo: cleanEmail });
  } catch (err) {
    console.error('[auth/send-code] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}
