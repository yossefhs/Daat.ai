// /api/push — Notifications Web Push « Daat Yomi » (quotidien).
//
// La PWA installée (Android, iOS ≥ 16.4) reçoit chaque matin le programme du
// jour : « דעת · Daat Yomi — jour N · Siman X, séifim a-b », qui ouvre /limoud/.
//
// Flux :
//   GET  ?action=key                 → clé publique VAPID (public, pour s'abonner)
//   POST {action:'subscribe', subscription, lang}    → enregistre l'abonnement
//   POST {action:'unsubscribe', endpoint}            → le retire
//   GET  (Authorization: Bearer CRON_SECRET)         → envoi du jour (cron 05:30 UTC)
//     &force=1  → ignorer l'anti-doublon du jour
//     &action=status → compteurs (Bearer requis)
//
// KV :
//   push:sub:<id>      → { subscription, lang, createdAt }   (id = sha256(endpoint))
//   push:subs:ids      → set des id
//   push:lastSentDate  → 'YYYY-MM-DD' anti-doublon
//
// Un abonnement mort (404/410 du service push) est purgé à l'envoi.
// Sans clés VAPID configurées, l'endpoint répond 503 sans casser le site.

import crypto from 'node:crypto';
import webpush from 'web-push';
import { kv } from './_kv.js';
import { getEntryForDate, loadPlan } from './_daily-limoud.js';

const env = (k) => (process.env[k] || '').trim();
const SITE = 'https://daattorah.com';

function vapidReady() {
  return !!(env('VAPID_PUBLIC_KEY') && env('VAPID_PRIVATE_KEY'));
}
function initVapid() {
  webpush.setVapidDetails(
    env('VAPID_SUBJECT') || 'mailto:contact@daattorah.com',
    env('VAPID_PUBLIC_KEY'),
    env('VAPID_PRIVATE_KEY'),
  );
}

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

const subId = (endpoint) => crypto.createHash('sha256').update(String(endpoint)).digest('hex').slice(0, 32);

function parisToday() {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Paris', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(new Date());
  const get = (t) => parts.find((p) => p.type === t)?.value;
  return `${get('year')}-${get('month')}-${get('day')}`;
}

// Messages par langue — contenu réel du plan, jamais inventé.
function buildPayloads(entry, totalDays) {
  const n = entry.siman?.num;
  const [a, b] = entry.seifRange || [];
  const url = `${SITE}/limoud/?utm_source=push`;
  const seifs = a === b ? `séif ${a}` : `séifim ${a}-${b}`;
  const seifsHe = a === b ? `סעיף ${a}` : `סעיפים ${a}-${b}`;
  const seifsEn = a === b ? `seif ${a}` : `seifim ${a}-${b}`;
  return {
    fr: { title: `דעת · Daat Yomi — jour ${entry.dayNumber}/${totalDays}`,
      body: `Siman ${n} · ${entry.siman?.title || ''} · ${seifs}`, url },
    he: { title: `דעת · דעת יומי — יום ${entry.dayNumber}/${totalDays}`,
      body: `סימן ${n} · ${entry.siman?.titleHe || entry.siman?.title || ''} · ${seifsHe}`, url: `${SITE}/limoud/index-he.html?utm_source=push` },
    en: { title: `דעת · Daat Yomi — day ${entry.dayNumber}/${totalDays}`,
      body: `Siman ${n} · ${entry.siman?.titleEn || entry.siman?.title || ''} · ${seifsEn}`, url: `${SITE}/limoud/index-en.html?utm_source=push` },
  };
}

async function sendDaily({ force = false } = {}) {
  const today = parisToday();
  const last = await kv.get('push:lastSentDate');
  if (!force && last === today) return { ok: true, skipped: 'deja-envoye', date: today };

  const entry = getEntryForDate(today);
  if (!entry) return { ok: true, skipped: 'pas-de-limoud-ce-jour', date: today };
  let totalDays = 194;
  try { totalDays = loadPlan()?.meta?.totalDays || 194; } catch { /* défaut */ }
  const payloads = buildPayloads(entry, totalDays);

  const ids = (await kv.smembers('push:subs:ids')) || [];
  let sent = 0, dead = 0, failed = 0;
  // envoi par paquets de 20 — la lambda a 60 s
  for (let i = 0; i < ids.length; i += 20) {
    const chunk = ids.slice(i, i + 20);
    await Promise.allSettled(chunk.map(async (id) => {
      const rec = await kv.get(`push:sub:${id}`);
      if (!rec?.subscription) { await kv.srem('push:subs:ids', id); return; }
      const lang = ['fr', 'he', 'en'].includes(rec.lang) ? rec.lang : 'fr';
      try {
        await webpush.sendNotification(rec.subscription, JSON.stringify(payloads[lang]), { TTL: 12 * 3600 });
        sent++;
      } catch (err) {
        const code = err?.statusCode;
        if (code === 404 || code === 410) {
          await kv.srem('push:subs:ids', id);
          await kv.del(`push:sub:${id}`);
          dead++;
        } else {
          failed++;
        }
      }
    }));
  }
  await kv.set('push:lastSentDate', today);
  return { ok: true, date: today, day: entry.dayNumber, siman: entry.siman?.num, subscribers: ids.length, sent, dead, failed };
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  if (!vapidReady()) {
    return res.status(503).json({ error: 'Push non configuré (VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY manquantes dans Vercel).' });
  }
  initVapid();

  try {
    // ---- POST : abonnement / désabonnement (public, depuis le site) ----
    if (req.method === 'POST') {
      const body = req.body || {};
      if (body.action === 'subscribe') {
        const sub = body.subscription;
        const endpoint = sub?.endpoint;
        if (!endpoint || !/^https:\/\//.test(endpoint) || !sub?.keys?.p256dh || !sub?.keys?.auth) {
          return res.status(400).json({ error: 'subscription invalide' });
        }
        const id = subId(endpoint);
        const lang = ['fr', 'he', 'en'].includes(body.lang) ? body.lang : 'fr';
        await kv.set(`push:sub:${id}`, { subscription: sub, lang, createdAt: new Date().toISOString() });
        await kv.sadd('push:subs:ids', id);
        return res.status(200).json({ ok: true, id });
      }
      if (body.action === 'unsubscribe') {
        if (!body.endpoint) return res.status(400).json({ error: 'endpoint requis' });
        const id = subId(body.endpoint);
        await kv.srem('push:subs:ids', id);
        await kv.del(`push:sub:${id}`);
        return res.status(200).json({ ok: true });
      }
      return res.status(400).json({ error: 'action inconnue' });
    }

    if (req.method !== 'GET') return res.status(405).json({ error: 'GET/POST uniquement' });

    // ---- GET public : la clé d'abonnement ----
    if (req.query?.action === 'key') {
      res.setHeader('Cache-Control', 's-maxage=3600');
      return res.status(200).json({ ok: true, publicKey: env('VAPID_PUBLIC_KEY') });
    }

    // ---- GET protégé (cron / admin) : envoi du jour, statut ----
    const bearer = (req.headers.authorization || '').replace(/^Bearer\s+/i, '').trim();
    const cronSecret = env('CRON_SECRET');
    if (!cronSecret || bearer !== cronSecret) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    if (req.query?.action === 'status') {
      const ids = (await kv.smembers('push:subs:ids')) || [];
      const last = await kv.get('push:lastSentDate');
      return res.status(200).json({ ok: true, subscribers: ids.length, lastSentDate: last || null });
    }
    return res.status(200).json(await sendDaily({ force: req.query?.force === '1' }));
  } catch (err) {
    console.error('[push] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
