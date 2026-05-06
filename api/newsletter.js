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
    };

    await kv.set(`newsletter:${email}`, record);

    // Liste agrégée (limite douce : on append, pas de doublons puisque la clé email est unique)
    try {
      await kv.lpush('newsletter:list', email);
      await kv.ltrim('newsletter:list', 0, 9999);
    } catch (e) {
      console.warn('[newsletter] kv list push failed:', e?.message);
    }

    // Email de bienvenue (best-effort)
    if (process.env.RESEND_API_KEY) {
      try {
        const resend = new Resend(process.env.RESEND_API_KEY);
        const fromEmail = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';
        const html = `
<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background:#FAF6EE;margin:0;padding:24px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:32px;">
    <div style="display:flex;align-items:baseline;gap:12px;padding-bottom:16px;border-bottom:2px solid #C5A55A;margin-bottom:24px;">
      <span style="font-family:'Frank Ruhl Libre',Georgia,serif;font-size:32px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-size:14px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT</span>
    </div>
    <h1 style="font-family:Georgia,serif;color:#1A1F3A;font-size:24px;margin:0 0 16px;">Barukh haba dans la communauté Daat</h1>
    <p style="color:#3D4266;font-size:15px;line-height:1.7;">Tu recevras chaque dimanche un siman du Choulhan Aroukh — texte hébreu, traduction, sources des Rishonim et Acharonim.</p>
    <p style="color:#3D4266;font-size:15px;line-height:1.7;">Le premier envoi : <strong>Siman 242 — Kavod et Oneg Shabbat</strong>.</p>
    <div style="background:#FAF6EE;border-left:3px solid #C5A55A;padding:16px 20px;margin:24px 0;color:#3D4266;font-style:italic;line-height:1.6;">
      Pour toute question halakhique, l'IA Daat est disponible : <a href="https://daattorah.com/chat.html" style="color:#C5A55A;font-weight:600;">daattorah.com/chat.html</a>
    </div>
    <p style="color:#3D4266;font-size:14px;line-height:1.7;">Pour soutenir l'étude : <a href="https://daattorah.com/soutenir.html" style="color:#C5A55A;font-weight:600;">don libre, dédicace, ou Tomeh Adaat</a>.</p>
    <p style="color:#aaa;font-size:11px;line-height:1.6;margin-top:32px;padding-top:16px;border-top:1px solid #E4DDD0;text-align:center;">דעת DAAT · daattorah.com — initié par le Rav Yossef Haim Samama</p>
  </div>
</body>
</html>`.trim();

        const text = `Barukh haba dans la communauté Daat.\n\nTu recevras chaque dimanche un siman du Choulhan Aroukh — texte hébreu, traduction, sources.\n\nLe premier envoi : Siman 242 — Kavod et Oneg Shabbat.\n\nIA Daat : https://daattorah.com/chat.html\nSoutenir : https://daattorah.com/soutenir.html\n\n— DAAT דעת · daattorah.com`;

        await resend.emails.send({
          from: `DAAT <${fromEmail}>`,
          to: email,
          subject: 'Bienvenue dans la newsletter Daat',
          html,
          text,
        });
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
