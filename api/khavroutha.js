// /api/khavroutha — Mise en relation khavroutha avec APPARIEMENT AUTOMATIQUE
//
//   POST   (public)  → inscription ; apparie en temps réel un partenaire
//                      compatible du vivier, sinon met en attente.
//   GET    (admin)   → ?action=pool|matches|all  (auth ADMIN_PASSWORD)
//   DELETE (admin)   → ?id=...  retire un profil du vivier
//
// Connexion entre partenaires : lien WhatsApp 1-à-1 (wa.me) pré-rempli.
// Seuls le prénom + le lien WhatsApp sont partagés entre partenaires.

import { kv } from './_kv.js';
import { Resend } from 'resend';
import { randomBytes } from 'node:crypto';
import { getClientIp } from './_http.js';
import {
  K_POOL, K_MATCHES, K_ALL, kProfile,
  NIVEAUX, GENRES, LANGUES, JOURS, MOMENTS, FORMATS,
  normalizePhone, waLink, findBestMatch, introMessage,
} from './_khavroutha.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Secret');
}

function clean(s, max = 200) { return String(s || '').trim().slice(0, max); }
function cleanList(arr, allowed, max = 12) {
  if (!Array.isArray(arr)) return [];
  return [...new Set(arr.map((x) => String(x).trim().toLowerCase()))].filter((x) => allowed.has(x)).slice(0, max);
}
function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function isAdmin(req) {
  const pwd = process.env.ADMIN_PASSWORD;
  if (!pwd) return false;
  const bearer = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  if (bearer && bearer === pwd) return true;
  if (req.headers['x-admin-secret'] && req.headers['x-admin-secret'] === pwd) return true;
  if (req.query?.secret && req.query.secret === pwd) return true;
  return false;
}

// ── Emails (best-effort) ─────────────────────────────────────────────────────
function resendClient() {
  if (!process.env.RESEND_API_KEY) return null;
  return new Resend(process.env.RESEND_API_KEY);
}
const FROM = () => `DAAT Khavroutha <${process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com'}>`;
const RAV = () => process.env.KHAVROUTHA_NOTIFY_EMAIL || process.env.ADMIN_EMAIL || 'yossefhs@gmail.com';

const L = {
  fr: { subj: 'Ton binôme de khavroutha est trouvé 🎉', hi: 'Bonjour', intro: 'Bonne nouvelle — on t\'a trouvé un partenaire d\'étude compatible :', cta: 'Écrire à', start: 'Pour démarrer, ouvre un siman ensemble', wait: 'Tu es bien inscrit. Dès qu\'un partenaire compatible s\'inscrit, on vous met en relation par WhatsApp.' },
  he: { subj: 'נמצא לך בן זוג לחברותא 🎉', hi: 'שלום', intro: 'בשורה טובה — מצאנו לך שותף לימוד מתאים:', cta: 'לכתוב אל', start: 'כדי להתחיל, פתחו סימן יחד', wait: 'נרשמת בהצלחה. ברגע שיירשם שותף מתאים, נחבר ביניכם בוואטסאפ.' },
  en: { subj: 'Your chavruta partner is matched 🎉', hi: 'Hello', intro: 'Good news — we found you a compatible study partner:', cta: 'Message', start: 'To begin, open a siman together', wait: 'You\'re registered. As soon as a compatible partner signs up, we\'ll connect you on WhatsApp.' },
};

async function emailMatch(resend, lang, to, selfName, partnerName, waHref) {
  if (!resend || !to || !to.includes('@')) return;
  const t = L[lang] || L.fr;
  const html = `<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;background:#FAF6EE;padding:24px;">
  <div style="max-width:520px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:28px;">
    <div style="font-family:'Frank Ruhl Libre',Georgia,serif;font-size:26px;color:#C5A55A;font-weight:700;border-bottom:2px solid #C5A55A;padding-bottom:12px;margin-bottom:18px;">דעת</div>
    <p style="color:#1A1F3A;font-size:16px;">${esc(t.hi)} ${esc(selfName)},</p>
    <p style="color:#3D4266;font-size:15px;line-height:1.6;">${esc(t.intro)}</p>
    <p style="font-size:20px;color:#1A1F3A;font-weight:600;margin:8px 0 18px;">${esc(partnerName)}</p>
    <a href="${esc(waHref)}" style="display:inline-block;background:#25D366;color:#fff;text-decoration:none;padding:13px 26px;border-radius:6px;font-weight:600;font-size:15px;">💬 ${esc(t.cta)} ${esc(partnerName)}</a>
    <p style="color:#7A7F9A;font-size:13px;line-height:1.6;margin-top:20px;">${esc(t.start)} — <a href="https://daattorah.com/oh/242/" style="color:#8C6F1E;">Siman 242</a>.</p>
  </div></div>`;
  try {
    await resend.emails.send({ from: FROM(), to, subject: t.subj, html, text: `${t.hi} ${selfName},\n\n${t.intro} ${partnerName}\n\n${t.cta} : ${waHref}\n\n${t.start} : https://daattorah.com/oh/242/` });
  } catch (e) { console.warn('[khavroutha] email match failed:', e?.message); }
}

async function emailWaiting(resend, lang, to, selfName) {
  if (!resend || !to || !to.includes('@')) return;
  const t = L[lang] || L.fr;
  try {
    await resend.emails.send({ from: FROM(), to, subject: 'DAAT Khavroutha', text: `${t.hi} ${selfName},\n\n${t.wait}` });
  } catch (e) { console.warn('[khavroutha] email waiting failed:', e?.message); }
}

async function notifyRav(resend, subject, lines) {
  if (!resend) return;
  try { await resend.emails.send({ from: FROM(), to: RAV(), subject, text: lines.join('\n') }); }
  catch (e) { console.warn('[khavroutha] notify rav failed:', e?.message); }
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  // ── GET admin ──────────────────────────────────────────────────────────────
  if (req.method === 'GET') {
    if (!isAdmin(req)) return res.status(401).json({ error: 'Non autorisé' });
    const action = req.query.action || 'all';
    if (action === 'matches') {
      const raw = await kv.lrange(K_MATCHES, 0, 199);
      return res.json({ ok: true, matches: raw.map((r) => (typeof r === 'string' ? JSON.parse(r) : r)) });
    }
    const poolIds = (await kv.smembers(K_POOL)) || [];
    const allIds = action === 'pool' ? poolIds : (await kv.lrange(K_ALL, 0, 499)) || [];
    const profiles = [];
    for (const id of allIds) {
      const p = await kv.get(kProfile(id));
      if (p) profiles.push(p);
    }
    return res.json({ ok: true, count: profiles.length, waiting: poolIds.length, profiles });
  }

  // ── DELETE admin ─────────────────────────────────────────────────────────────
  if (req.method === 'DELETE') {
    if (!isAdmin(req)) return res.status(401).json({ error: 'Non autorisé' });
    const id = clean(req.query.id, 60);
    if (!id) return res.status(400).json({ error: 'id requis' });
    await Promise.all([kv.del(kProfile(id)), kv.srem(K_POOL, id)]);
    return res.json({ ok: true, deleted: id });
  }

  if (req.method !== 'POST') return res.status(405).json({ error: 'Méthode non autorisée' });

  // ── POST : inscription + appariement ─────────────────────────────────────────
  try {
    const body = req.body || {};
    const nom = clean(body.nom, 80);
    const genre = clean(body.genre, 1).toLowerCase();
    const langue = clean(body.langue, 2).toLowerCase() || 'fr';
    const niveau = clean(body.niveau, 16).toLowerCase();
    const jours = cleanList(body.jours, JOURS);
    const moments = cleanList(body.moments, MOMENTS);
    const format = clean(body.format, 16).toLowerCase();
    const ville = clean(body.ville, 80);
    const email = clean(body.email, 160);
    const whatsapp = normalizePhone(body.whatsapp || body.contact);

    if (!nom || !GENRES.has(genre) || !NIVEAUX.has(niveau) || !jours.length || !moments.length) {
      return res.status(400).json({ error: 'Champs requis manquants (prénom, genre, niveau, jours, moments).' });
    }
    if (!LANGUES.has(langue)) return res.status(400).json({ error: 'Langue invalide' });
    if (whatsapp.length < 8) return res.status(400).json({ error: 'Numéro WhatsApp invalide (format international, ex. 33612345678).' });
    if (!email.includes('@')) return res.status(400).json({ error: 'Email requis pour la notification.' });

    // Rate-limit IP
    const ip = getClientIp(req);
    const rlKey = `kh:rl:${ip}`;
    const count = (await kv.incr(rlKey)) || 1;
    if (count === 1) await kv.expire(rlKey, 3600);
    if (count > 3) return res.status(429).json({ error: 'Trop de demandes. Réessaie dans une heure.' });

    const id = `kh-${Date.now()}-${randomBytes(4).toString('hex')}`;
    const profile = {
      id, nom, genre, langue, niveau, jours, moments,
      format: FORMATS.has(format) ? format : 'peu-importe',
      ville, email, whatsapp,
      status: 'waiting', createdAt: new Date().toISOString(), ip,
    };
    await kv.set(kProfile(id), profile);
    await kv.lpush(K_ALL, id);
    await kv.ltrim(K_ALL, 0, 999);

    const resend = resendClient();
    const match = await findBestMatch(profile);

    if (match) {
      const now = new Date().toISOString();
      profile.status = 'matched'; profile.matchedWith = match.id; profile.matchedAt = now;
      match.status = 'matched'; match.matchedWith = id; match.matchedAt = now;
      await Promise.all([
        kv.set(kProfile(id), profile),
        kv.set(kProfile(match.id), match),
        kv.srem(K_POOL, match.id),
        kv.lpush(K_MATCHES, JSON.stringify({
          at: now, langue, niveau,
          a: { id, nom }, b: { id: match.id, nom: match.nom },
        })),
        kv.ltrim(K_MATCHES, 0, 499),
      ]);

      // Liens WhatsApp croisés
      const linkNewToPartner = waLink(match.whatsapp, introMessage(langue, match.nom, nom, niveau));
      const linkPartnerToNew = waLink(profile.whatsapp, introMessage(langue, nom, match.nom, niveau));

      // Le partenaire qui attendait est notifié par email ; le nouveau voit le lien dans la réponse.
      await emailMatch(resend, match.langue || langue, match.email, match.nom, nom, linkPartnerToNew);
      await emailMatch(resend, langue, email, nom, match.nom, linkNewToPartner);
      await notifyRav(resend, `[DAAT] Khavroutha APPARIÉE — ${nom} ↔ ${match.nom}`, [
        `${nom} (${niveau}/${genre}/${langue}) ↔ ${match.nom}`,
        `WhatsApp: ${profile.whatsapp} ↔ ${match.whatsapp}`,
        `Jours communs: ${jours.filter((j) => match.jours.includes(j)).join(', ')}`,
      ]);

      return res.json({
        ok: true, matched: true,
        partner: { nom: match.nom },
        whatsapp_link: linkNewToPartner,
      });
    }

    // Pas de partenaire pour l'instant → vivier
    await kv.sadd(K_POOL, id);
    await emailWaiting(resend, langue, email, nom);
    await notifyRav(resend, `[DAAT] Khavroutha — nouvelle inscription ${nom}`, [
      `${nom} (${niveau}/${genre}/${langue}) — en attente`,
      `Jours: ${jours.join(', ')} | Moments: ${moments.join(', ')}`,
      `WhatsApp: ${whatsapp} | Email: ${email}`,
    ]);

    return res.json({ ok: true, matched: false });
  } catch (err) {
    console.error('[khavroutha] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
