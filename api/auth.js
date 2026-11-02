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
//   /api/auth/delete      → /api/auth?action=delete   (suppression du compte)
//
// On peut aussi appeler directement /api/auth?action=… si besoin.
//
// Application mobile : elle envoie `X-Daat-Client: app` sur verify-code et reçoit
// le jeton de session dans la réponse (le site, lui, ne le voit jamais : cookie
// HttpOnly). Elle le présente ensuite en `Authorization: Bearer <jeton>` — même
// JWT, même durée (voir _auth.js, getUserFromRequest).

import crypto from 'node:crypto';
import { kv } from './_kv.js';
import { Resend } from 'resend';
import { getClientIp } from './_http.js';
import { adminParJeton } from './_admin-gate.js';
import { K_ALL, K_POOL, kProfile } from './_khavroutha.js';
import {
  generateCode,
  isValidEmail,
  checkSendRateLimit,
  signSession,
  setSessionCookie,
  clearSessionCookie,
  getUserFromRequest,
  setCorsHeaders,
  SESSION_DAYS,
} from './_auth.js';

const MAX_VERIFY_ATTEMPTS = 5;
const GUEST_ID_RE = /^guest_[a-z0-9_]{6,48}$/;

// L'application mobile se déclare par entête (ou par le corps) ; c'est la seule
// cliente à qui l'on rend le jeton en clair.
function isAppClient(req) {
  const h = String(req.headers?.['x-daat-client'] || '').trim().toLowerCase();
  return h === 'app' || req.body?.client === 'app';
}

// Identifiant invité : cookie du site, ou entête X-Daat-Guest-Id de l'application.
function readGuestId(req) {
  const m = String(req.headers?.cookie || '').match(/(?:^|;\s*)daat_guest_id=([^;]+)/);
  if (m) {
    const v = decodeURIComponent(m[1]);
    if (v.startsWith('guest_')) return v;
  }
  const h = String(req.headers?.['x-daat-guest-id'] || '');
  return GUEST_ID_RE.test(h) ? h : null;
}

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

    // Anti-bombing : plafond par IP (toutes adresses confondues). Sans ça, le
    // throttle par email seul laisse envoyer des OTP vers une infinité d'adresses
    // (spam des victimes + coût Resend). 15 envois / heure / IP suffit largement.
    const ip = getClientIp(req);
    const ipKey = `auth:send-ip:${ip}`;
    const ipCount = await kv.incr(ipKey);
    if (ipCount === 1) await kv.expire(ipKey, 60 * 60);
    if (ipCount > 15) {
      return res.status(429).json({
        error: 'Trop de demandes depuis ce réseau. Réessaie plus tard.',
      });
    }

    const code = generateCode();
    await kv.set(`auth:code:${cleanEmail}`, { code, attempts: 0 }, { ex: 600 });

    const resend = new Resend(process.env.RESEND_API_KEY);
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';

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

    // Rendre le compte visible dans l'admin dès l'inscription, même sans avoir
    // encore chatté (sinon un compte inscrit/payant qui n'a jamais envoyé de
    // message n'apparaît nulle part — c'était la cause des "adresses manquantes").
    await kv.sadd('users:known', cleanEmail);

    // ── Migration du compteur Aperçu Premium guest → email (anti-gaming) ──
    // Si l'utilisateur a déjà épuisé son Aperçu en tant qu'anonyme, on garde
    // ce compteur sur son compte email. Évite : "anonyme épuise 3 → crée
    // compte → repart à 0". Le MAX préserve aussi le cas inverse improbable
    // où le user aurait un compteur email plus élevé qu'en anonyme.
    try {
      const guestId = readGuestId(req);
      if (guestId) {
        const [guestPreview, emailPreview] = await Promise.all([
          kv.get(`user:preview_used:${guestId}`),
          kv.get(`user:preview_used:${cleanEmail}`),
        ]);
        const merged = Math.max(parseInt(guestPreview || '0', 10), parseInt(emailPreview || '0', 10));
        if (merged > 0) {
          await kv.set(`user:preview_used:${cleanEmail}`, merged);
        }
      }
    } catch (err) {
      console.warn('[auth/verify] preview counter migration failed:', err?.message);
    }

    const token = signSession({ email: cleanEmail });
    setSessionCookie(res, token);

    const payload = { ok: true, user: { email: cleanEmail } };
    if (isAppClient(req)) {
      payload.token = token;
      payload.tokenExpiresInDays = SESSION_DAYS;
    }
    return res.status(200).json(payload);
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
  // `admin` : l'adresse figure-t-elle dans ADMIN_EMAILS ? Les pages /admin et
  // /connexion-admin.html le demandent ICI plutôt qu'à /api/admin/stats : là-bas,
  // une sonde sans identifiants compte comme un ÉCHEC de mot de passe (freinage :
  // 5 par IP en 15 min), et quelques visites suffisaient à bloquer l'adresse IP de
  // l'administrateur — mot de passe compris. Ne révèle que le statut de l'appelant.
  return res.status(200).json({ user, admin: Boolean(adminParJeton(req)) });
}

// ---------- logout ----------
async function handleLogout(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });
  clearSessionCookie(res);
  return res.status(200).json({ ok: true });
}

// ---------- delete (suppression du compte) ----------
// Exigée par les magasins d'applications (App Store, règle 5.1.1 v) et par le RGPD.
// Tout ce qui est rattaché à l'adresse disparaît : compte, plan, compteurs,
// conversations, progression, plan d'étude, lettre, profil khavroutha, et les
// entrées du journal d'usage qui la nomment. Restent : les écritures de dons
// (obligation comptable, logs:helloasso) et les compteurs techniques, qui expirent
// d'eux-mêmes. La page /confidentialite décrit exactement ce périmètre : la tenir
// à jour si cette liste change.
export async function effacerCompte(email) {
  const e = String(email || '').trim().toLowerCase();
  if (!e.includes('@')) throw new Error('effacerCompte: email requis');
  const report = { cles: 0, compteurs: 0, journal: 0, khavroutha: 0 };

  const fixes = [
    `user:${e}`, `user:plan:${e}`, `user:plan_expires:${e}`, `user:plan_source:${e}`,
    `user:force_opus:${e}`, `user:preview_used:${e}`, `credits:${e}`,
    `convs:${e}`, `convs:rl:${e}`, `progress:${e}`, `progress:rl:${e}`,
    `custom-plan:${e}`, `newsletter:${e}`, `auth:code:${e}`, `auth:send-rate:${e}`,
    `iap:user:${e}`,
  ];
  try {
    const iap = await kv.get(`iap:user:${e}`);
    if (iap?.app_user_id) fixes.push(`iap:map:${iap.app_user_id}`);
  } catch { /* fiche absente */ }
  report.cles = (await kv.del(...fixes)) || 0;

  // Compteurs datés (rate:, rate-month:, usage:) — balayage borné par motif.
  for (const pattern of [`rate:${e}:*`, `rate-month:${e}:*`, `usage:${e}:*`]) {
    let cursor = '0';
    for (let round = 0; round < 50; round++) {
      const [next, keys] = await kv.scan(cursor, { match: pattern, count: 200 });
      if (Array.isArray(keys) && keys.length) report.compteurs += (await kv.del(...keys)) || 0;
      cursor = String(next);
      if (cursor === '0') break;
    }
  }

  await Promise.all([
    kv.srem('users:known', e),
    kv.lrem('custom-plan:list', 0, e),
    kv.lrem('newsletter:list', 0, e),
  ]);

  // Journal d'usage : retire les entrées qui nomment l'adresse (liste bornée à 500).
  try {
    const entries = (await kv.lrange('logs:usage', 0, 999)) || [];
    for (const raw of entries) {
      const str = typeof raw === 'string' ? raw : JSON.stringify(raw);
      if (str.includes(`"${e}"`)) report.journal += (await kv.lrem('logs:usage', 0, raw)) || 0;
    }
  } catch (err) {
    console.warn('[auth/delete] journal d\'usage non nettoyé :', err?.message || err);
  }

  // Profils khavroutha portant cette adresse.
  try {
    const ids = (await kv.lrange(K_ALL, 0, 999)) || [];
    for (const id of ids) {
      const p = await kv.get(kProfile(id));
      if (p && String(p.email || '').trim().toLowerCase() === e) {
        await Promise.all([kv.del(kProfile(id)), kv.srem(K_POOL, id), kv.lrem(K_ALL, 0, id)]);
        report.khavroutha++;
      }
    }
  } catch (err) {
    console.warn('[auth/delete] profils khavroutha non nettoyés :', err?.message || err);
  }

  return report;
}

async function handleDelete(req, res) {
  if (req.method !== 'POST' && req.method !== 'DELETE') {
    return res.status(405).json({ error: 'POST ou DELETE uniquement' });
  }
  const user = getUserFromRequest(req);
  if (!user) return res.status(401).json({ error: 'Non authentifié' });
  const confirm = req.body?.confirm;
  if (confirm !== true && confirm !== 'true') {
    return res.status(400).json({ error: 'Confirmation requise : { "confirm": true }' });
  }
  try {
    const email = user.email.trim().toLowerCase();
    const report = await effacerCompte(email);
    clearSessionCookie(res);
    // Trace de l'opération sans l'adresse (empreinte tronquée) : compter, pas identifier.
    const empreinte = crypto.createHash('sha256').update(email).digest('hex').slice(0, 16);
    await kv.lpush('logs:comptes-supprimes', JSON.stringify({ ts: new Date().toISOString(), empreinte, ...report }));
    await kv.ltrim('logs:comptes-supprimes', 0, 499);
    console.log(`[auth/delete] compte supprimé (${empreinte}) :`, report);
    return res.status(200).json({ ok: true, deleted: true, ...report });
  } catch (err) {
    console.error('[auth/delete] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
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
    case 'delete':      return handleDelete(req, res);
    default:
      return res.status(400).json({
        error: 'Paramètre action requis (send-code, verify-code, me, logout, delete)',
      });
  }
}
