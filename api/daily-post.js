// /api/daily-post — Le post quotidien du Daat Yomi, validé d'un clic.
//
// Cron (Vercel, dimanche → jeudi, avant l'aube) — auth Bearer CRON_SECRET :
//   GET /api/daily-post                 → rédige, vérifie, illustre, envoie l'email
//   GET /api/daily-post?date=YYYY-MM-DD&force=1&secret=…  → (re)fait un jour précis
//   GET /api/daily-post?action=status&secret=…            → journal
//
// Lien de l'email (jeton propre à la date, dérivé de CRON_SECRET) :
//   GET  ?action=review&date&t          → page de validation
//   GET  ?action=img&date&t&slot        → une illustration (générée si absente)
//   POST ?action=regen-img&date&t&slot  → refait une illustration
//   POST ?action=verify&date&t          → (re)vérifie contre le Choul'han Aroukh
//   POST ?action=regen-text&date&t      → réécrit le post, puis le vérifie
//   POST ?action=publish&date&t         → { jpeg, posts, hashtags } → publie
//
// Public (c'est l'image publiée, les réseaux doivent pouvoir la télécharger) :
//   GET  ?action=final&date             → visuel publié, JPEG

import { kv } from './_kv.js';
import {
  parisToday, dayInfo, tokenOk, tokenFor, writePost, verifyPost, generateImage,
  generateAllImages, imageSlots, sendReviewEmail, sendBlockedEmail, BlockedError, logEvent, SITE,
} from './_daily-post.js';
import { renderReviewPage } from './_daily-post-view.js';
import { configuredPlatforms, publishAll } from './_social-publish.js';

const TTL = 10 * 24 * 3600;
const env = (k) => (process.env[k] || '').trim();

function cronAuthorized(req) {
  const secret = env('CRON_SECRET');
  const auth = (req.headers.authorization || '').trim();
  const q = String(req.query?.secret || '').trim();
  return !!secret && (auth === `Bearer ${secret}` || q === secret);
}

async function readJson(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch { return {}; } }
  return {};
}

async function deliveryStatus(ids) {
  const key = env('RESEND_API_KEY');
  if (!key || !ids) return null;
  return Promise.all(String(ids).split(',').map(async (id) => {
    try {
      const r = await fetch(`https://api.resend.com/emails/${id}`, { headers: { Authorization: `Bearer ${key}` } });
      const d = await r.json();
      return { id, to: d.to, last_event: d.last_event || d.message || `HTTP ${r.status}` };
    } catch (e) { return { id, error: e.message }; }
  }));
}

// Idempotent : le cron repasse plusieurs fois dans la matinée (vercel.json).
// Tant qu'aucun email n'est CONFIRMÉ par Resend pour ce jour, il reprend là où
// le passage précédent s'est arrêté ; une fois confirmé, il ne fait plus rien.
async function runDay(date, { force = false } = {}) {
  if (!dayInfo(date)) return { ok: true, date, skipped: 'pas d\'étude Daat Yomi ce jour' };
  const [existing, emailed] = await Promise.all([
    kv.get(`dailypost:${date}`), kv.get(`dailypost:${date}:emailed:du pack`),
  ]);
  if (existing && emailed && !force) {
    // Accepté par Resend ne veut pas dire livré : on relève le dernier état connu.
    const livraison = await deliveryStatus(emailed.id);
    await logEvent({ date, event: 'état de livraison du pack', id: emailed.id, livraison });
    return { ok: true, date, skipped: 'déjà préparé et envoyé', emailed, livraison };
  }
  let rec = existing;
  if (!existing || force) {
    try {
      rec = await writePost(date);
    } catch (e) {
      // Mieux vaut ne rien envoyer qu'un Daat Yomi faux : on explique pourquoi.
      const reasons = e instanceof BlockedError ? e.reasons : [`Rédaction impossible : ${e.message}`];
      await logEvent({ date, event: 'pack bloqué', error: reasons.join(' · ') });
      // Un seul email de blocage par jour et par motif, même si le cron repasse.
      const cle = `dailypost:${date}:blockedmail`;
      const deja = await kv.get(cle);
      const email = deja === reasons.join(' · ') && !force ? { ok: true, skipped: 'déjà signalé' } : await sendBlockedEmail(date, reasons);
      if (email.ok && !email.skipped) await kv.set(cle, reasons.join(' · '), { ex: 10 * 24 * 3600 });
      return { ok: false, date, bloque: reasons, email };
    }
  }
  const [verify, images] = await Promise.allSettled([
    existing && !force ? kv.get(`dailypost:${date}:verify`).then((v) => v || verifyPost(date)) : verifyPost(date),
    generateAllImages(date),
  ]);
  const email = await sendReviewEmail(date);
  return {
    ok: email.ok, date, titre: rec.post.titre, reprise: !!existing && !force,
    verify: verify.status === 'fulfilled' ? verify.value?.global : `échec : ${verify.reason?.message}`,
    images: images.status === 'fulfilled' ? images.value : `échec : ${images.reason?.message}`,
    email,
  };
}

export default async function handler(req, res) {
  const action = String(req.query?.action || '');
  const date = /^\d{4}-\d{2}-\d{2}$/.test(String(req.query?.date || '')) ? req.query.date : null;

  try {
    // ---- image publiée : publique ----
    if (action === 'final') {
      const b64 = date && (await kv.get(`dailypost:${date}:final`));
      if (!b64) return res.status(404).json({ error: 'aucun visuel publié pour cette date' });
      res.setHeader('Content-Type', 'image/jpeg');
      res.setHeader('Cache-Control', 'public, max-age=86400, immutable');
      return res.status(200).send(Buffer.from(b64, 'base64'));
    }

    // ---- cron et administration ----
    if (!action || action === 'status') {
      if (!cronAuthorized(req)) return res.status(401).json({ error: 'Unauthorized' });
      if (action === 'status') {
        const log = await kv.lrange('dailypost:log', 0, 29);
        return res.status(200).json({ ok: true, platforms: configuredPlatforms(), images: !!env('OPENAI_API_KEY'),
          log: (log || []).map((s) => { try { return typeof s === 'string' ? JSON.parse(s) : s; } catch { return s; } }) });
      }
      const d = date || parisToday(); // date civile à Jérusalem
      const out = await runDay(d, { force: req.query?.force === '1' });
      console.log('[daily-post] cron', JSON.stringify({ ...out, images: undefined }).slice(0, 1500));
      if (!out.skipped) out.review = `${SITE}/api/daily-post?action=review&date=${d}&t=${tokenFor(d)}`;
      // Email non confirmé → 500 : l'échec se voit dans les logs et le tableau des crons Vercel.
      return res.status(out.email && !out.email.ok ? 500 : 200).json(out);
    }

    // ---- actions de la page de validation : jeton du jour ----
    if (!date || !tokenOk(date, String(req.query?.t || ''))) {
      return res.status(401).json({ error: 'Lien invalide ou expiré' });
    }
    const rec = await kv.get(`dailypost:${date}`);
    if (!rec) return res.status(404).json({ error: 'Aucun post préparé pour cette date' });

    if (action === 'review' && req.method === 'GET') {
      const [verify, published] = await Promise.all([
        kv.get(`dailypost:${date}:verify`), kv.get(`dailypost:${date}:published`),
      ]);
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.setHeader('Cache-Control', 'no-store');
      return res.status(200).send(renderReviewPage({
        date, token: req.query.t, info: rec.info, post: rec.post, verify, published, anomalies: rec.anomalies || [],
        platforms: configuredPlatforms(), imagesEnabled: !!env('OPENAI_API_KEY'),
        slots: imageSlots(rec).map((s) => s.slot),
      }));
    }

    if (action === 'img' || action === 'regen-img') {
      const slot = String(req.query?.slot || '');
      const dataUrl = await generateImage(date, slot, { force: action === 'regen-img' });
      return res.status(200).json({ ok: true, slot, dataUrl });
    }

    if (action === 'verify' && req.method === 'POST') {
      const verdict = await verifyPost(date);
      return res.status(200).json({ ok: true, verdict });
    }

    if (action === 'regen-text' && req.method === 'POST') {
      await writePost(date);
      const verdict = await verifyPost(date);
      return res.status(200).json({ ok: true, verdict });
    }

    if (action === 'publish' && req.method === 'POST') {
      const body = await readJson(req);
      if (!body.jpeg || body.jpeg.length < 1000) return res.status(400).json({ error: 'visuel manquant' });
      // La version publiée est celle éventuellement corrigée dans la page.
      const post = { ...rec.post, posts: { ...rec.post.posts, ...(body.posts || {}) } };
      if (Array.isArray(body.hashtags) && body.hashtags.length) post.hashtags = body.hashtags;
      await kv.set(`dailypost:${date}`, { ...rec, post }, { ex: TTL });
      await kv.set(`dailypost:${date}:final`, body.jpeg, { ex: TTL });
      const imageUrl = `${SITE}/api/daily-post?action=final&date=${date}`;
      const already = (await kv.get(`dailypost:${date}:published`)) || {};
      const results = await publishAll({ post, imageUrl, imageBytes: Buffer.from(body.jpeg, 'base64'), already });
      await kv.set(`dailypost:${date}:published`, results, { ex: TTL });
      await logEvent({ date, event: 'publication', results });
      return res.status(200).json({ ok: true, results, imageUrl });
    }

    return res.status(400).json({ error: `action inconnue : ${action}` });
  } catch (err) {
    console.error('[daily-post]', action, err);
    await logEvent({ date, event: `erreur ${action || 'cron'}`, error: String(err?.message || err).slice(0, 300) });
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
