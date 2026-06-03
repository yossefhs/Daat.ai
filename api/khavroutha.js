// POST /api/khavroutha — Demande de mise en relation Khavroutha
//
// Body JSON :
//   { nom, niveau, disponibilite, contact }
//
// - Stocke la demande en KV : khavroutha:{id} + khavroutha:list
// - Envoie un email récapitulatif à KHAVROUTHA_NOTIFY_EMAIL (par défaut yossefhs@gmail.com)
// - Rate-limit : 3 demandes / IP / heure

import { kv } from './_kv.js';
import { Resend } from 'resend';
import { randomBytes } from 'node:crypto';
import { getClientIp } from './_http.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

const ALLOWED_NIVEAUX = new Set(['base', 'lamdan', 'synthese', 'mixte']);

function clean(s, max = 200) {
  return String(s || '').trim().slice(0, max);
}

function esc(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST uniquement' });
  }

  try {
    const body = req.body || {};
    const nom = clean(body.nom, 80);
    const niveau = clean(body.niveau, 16);
    const disponibilite = clean(body.disponibilite, 200);
    const contact = clean(body.contact, 160);

    if (!nom || !niveau || !disponibilite || !contact) {
      return res.status(400).json({ error: 'Tous les champs sont requis' });
    }
    if (!ALLOWED_NIVEAUX.has(niveau)) {
      return res.status(400).json({ error: 'Niveau invalide' });
    }

    // Rate-limit par IP
    const ip = getClientIp(req);
    const ipKey = `khavroutha:rl:${ip}`;
    const count = (await kv.incr(ipKey)) || 1;
    if (count === 1) await kv.expire(ipKey, 3600);
    if (count > 3) {
      return res.status(429).json({ error: 'Trop de demandes. Réessaie dans une heure.' });
    }

    const id = `kh-${Date.now()}-${randomBytes(4).toString('hex')}`;
    const record = {
      id,
      nom,
      niveau,
      disponibilite,
      contact,
      createdAt: new Date().toISOString(),
      ip,
    };

    await kv.set(`khavroutha:${id}`, record);
    try {
      await kv.lpush('khavroutha:list', id);
      await kv.ltrim('khavroutha:list', 0, 999);
    } catch (e) {
      console.warn('[khavroutha] list push failed:', e?.message);
    }

    // Notification au Rav (best-effort)
    const notifyTo =
      process.env.KHAVROUTHA_NOTIFY_EMAIL ||
      process.env.ADMIN_EMAIL ||
      'yossefhs@gmail.com';

    if (process.env.RESEND_API_KEY) {
      try {
        const resend = new Resend(process.env.RESEND_API_KEY);
        const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';
        const niveauLabel = {
          base: 'Base — débutant / intermédiaire',
          lamdan: 'Lamdan — pilpoul, sources',
          synthese: 'Synthèse — révision, mémorisation',
          mixte: 'Mixte (plusieurs niveaux)',
        }[niveau];

        const html = `
<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;background:#FAF6EE;margin:0;padding:24px;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:28px;">
    <div style="display:flex;align-items:baseline;gap:10px;padding-bottom:14px;border-bottom:2px solid #C5A55A;margin-bottom:20px;">
      <span style="font-family:'Frank Ruhl Libre',Georgia,serif;font-size:26px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-size:13px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT</span>
    </div>
    <h2 style="font-family:Georgia,serif;color:#1A1F3A;font-size:20px;margin:0 0 16px;">Nouvelle demande de Khavroutha</h2>
    <table style="width:100%;border-collapse:collapse;font-size:14px;color:#3D4266;">
      <tr><td style="padding:8px 0;color:#7A7F9A;width:140px;">Nom</td><td style="padding:8px 0;color:#1A1F3A;font-weight:600;">${esc(nom)}</td></tr>
      <tr><td style="padding:8px 0;color:#7A7F9A;border-top:1px solid #E4DDD0;">Niveau souhaité</td><td style="padding:8px 0;color:#1A1F3A;border-top:1px solid #E4DDD0;">${esc(niveauLabel)}</td></tr>
      <tr><td style="padding:8px 0;color:#7A7F9A;border-top:1px solid #E4DDD0;">Disponibilité</td><td style="padding:8px 0;color:#1A1F3A;border-top:1px solid #E4DDD0;">${esc(disponibilite)}</td></tr>
      <tr><td style="padding:8px 0;color:#7A7F9A;border-top:1px solid #E4DDD0;">Contact</td><td style="padding:8px 0;color:#1A1F3A;font-weight:600;border-top:1px solid #E4DDD0;">${esc(contact)}</td></tr>
    </table>
    <p style="color:#7A7F9A;font-size:12px;margin-top:24px;padding-top:14px;border-top:1px solid #E4DDD0;">ID interne : ${esc(id)}<br>Reçu : ${esc(record.createdAt)}<br>IP : ${esc(ip)}</p>
  </div>
</body>
</html>`.trim();

        const text = `Nouvelle demande de Khavroutha — DAAT\n\nNom : ${nom}\nNiveau : ${niveauLabel}\nDisponibilité : ${disponibilite}\nContact : ${contact}\n\nID : ${id}\nReçu : ${record.createdAt}`;

        await resend.emails.send({
          from: `DAAT Khavroutha <${fromEmail}>`,
          to: notifyTo,
          replyTo: contact.includes('@') ? contact : undefined,
          subject: `[DAAT] Khavroutha — ${nom} (${niveau})`,
          html,
          text,
        });
      } catch (e) {
        console.warn('[khavroutha] notify email failed:', e?.message);
      }
    }

    return res.status(200).json({ ok: true, id });
  } catch (err) {
    console.error('[khavroutha] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
