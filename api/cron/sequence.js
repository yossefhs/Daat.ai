// GET /api/cron/sequence — exécution quotidienne (cron Vercel)
//
// Parcourt la liste des inscrits newsletter et envoie les emails de la
// séquence de bienvenue (J3, J7, J10, J14) à ceux qui sont dus.
//
// Vercel ajoute automatiquement l'header `Authorization: Bearer ${CRON_SECRET}`
// quand il déclenche un cron — on vérifie que la requête vient bien de là
// pour éviter les déclenchements externes.
//
// Idempotence : chaque inscrit a un tableau `sentSteps` ; un step déjà
// envoyé ne sera jamais renvoyé. Re-run safe.

import { kv } from '@vercel/kv';
import { Resend } from 'resend';
import { getDueSteps } from '../_email-sequence.js';

export default async function handler(req, res) {
  // Auth — Vercel envoie ce header sur les déclenchements de cron
  const auth = req.headers.authorization || '';
  const expectedSecret = process.env.CRON_SECRET;
  if (expectedSecret && auth !== `Bearer ${expectedSecret}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({ error: 'RESEND_API_KEY non configuré' });
  }

  const resend = new Resend(process.env.RESEND_API_KEY);
  const fromEmail = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';

  let processed = 0;
  let sent = 0;
  let errors = 0;
  const log = [];

  try {
    // Récupère la liste des emails inscrits (jusqu'à 10000)
    const emails = (await kv.lrange('newsletter:list', 0, 9999)) || [];
    // Dédoublonne (sécurité — kv.lpush peut avoir laissé des doublons)
    const uniqueEmails = [...new Set(emails)];

    for (const email of uniqueEmails) {
      processed++;
      try {
        const record = await kv.get(`newsletter:${email}`);
        if (!record || !record.confirmed) continue;

        const due = getDueSteps(record.subscribedAt, record.sentSteps || []);
        if (!due.length) continue;

        // On envoie au plus 1 step par run pour ne pas spammer si
        // quelqu'un s'inscrit puis le cron tourne 14 jours plus tard
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

        // Marquer comme envoyé (idempotent)
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
      log: log.slice(0, 50), // tronque pour ne pas saturer la response
    });
  } catch (err) {
    console.error('[cron/sequence] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur cron' });
  }
}
