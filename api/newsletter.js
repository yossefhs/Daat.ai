// /api/newsletter — Newsletter DAAT (signup public + cron + daily Daat Yomi)
//
// Modes selon la méthode HTTP et l'action :
//   POST /api/newsletter                       → inscription publique
//                                                body { email, source?, enableDaily? }
//   GET  /api/newsletter                       → cron (séquence J0-J14 + Daat Yomi quotidien)
//                                                (auth Bearer ${CRON_SECRET})
//   GET  /api/newsletter?action=stats          → stats admin (Bearer ${ADMIN_PASSWORD})
//   GET  /api/newsletter?action=test-daily&to=&date=
//                                              → envoi manuel d'un daily de test
//                                                (Bearer ${ADMIN_PASSWORD})
//   GET  /api/newsletter?action=test-custom-daily&to=&date=
//                                              → envoi manuel d'un daily PERSO
//                                                de test, en lisant le plan
//                                                stocké pour {to} (Bearer ${ADMIN_PASSWORD})
//   GET  /api/newsletter?action=enable-daily&email=&token=
//                                              → opt-in 1-click depuis email (HTML)
//   GET  /api/newsletter?action=disable-daily&email=&token=
//                                              → opt-out 1-click depuis email (HTML)
//
// Cette fusion permet de rester sous la limite de 12 fonctions Vercel
// Hobby tout en regroupant le système email dans un seul fichier (signup
// envoie J0, cron envoie J3 → J14 et le Daat Yomi quotidien).
//
// Stockage Vercel KV :
//   - newsletter:{email}      → {
//       email, subscribedAt, source, confirmed, token,
//       optinToken,               // secret 1-click pour enable/disable daily
//       sentSteps: ['j0', 'j3', ...],
//       dailyEnabled?: boolean,   // opt-in Daat Yomi quotidien (false par défaut)
//       dailyEnabledAt?: string,  // ISO de l'activation
//       dailyDisabledAt?: string, // ISO de la désactivation
//       lang?: 'fr'|'en'|'he',    // réserve future (libellés FR pour MVP)
//     }
//   - newsletter:list                         → liste des emails (pour le cron)
//   - newsletter:daily-sent:{date}:{email}    → marqueur idempotence (TTL 48h)
//
// Activation du daily :
//   - 1-click depuis email J7/J14 → ?action=enable-daily&email=&token=
//   - Lors de l'inscription → POST avec { enableDaily: true } (UI personnaliser)
//
// Cron Vercel : pointe vers /api/newsletter (le header Bearer fait le tri).

import { kv } from './_kv.js';
import { Resend } from 'resend';
import { randomBytes } from 'node:crypto';
import { getStepById, getDueSteps } from './_email-sequence.js';
import { getEntryForDate, buildDailyEmail } from './_daily-limoud.js';
import { getEntryForUser, buildCustomDailyEmail } from './_custom-plan-engine.js';
import { getClientIp } from './_http.js';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

function isValidEmail(s) {
  return typeof s === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s) && s.length <= 254;
}

// ---------- POST : inscription publique ----------
async function handleSignup(req, res) {
  try {
    const body = req.body || {};
    const email = String(body.email || '').trim().toLowerCase();
    const source = String(body.source || 'home').slice(0, 32);
    const enableDaily = body.enableDaily === true;

    if (!isValidEmail(email)) {
      return res.status(400).json({ error: 'Adresse email invalide' });
    }

    // Rate-limit par IP
    const ip = getClientIp(req);
    const ipKey = `newsletter:rl:${ip}`;
    const count = (await kv.incr(ipKey)) || 1;
    if (count === 1) await kv.expire(ipKey, 3600);
    if (count > 3) {
      return res.status(429).json({
        error: "Trop d'inscriptions depuis cette IP. Réessaie plus tard.",
      });
    }

    // Déjà inscrit ?
    const existing = await kv.get(`newsletter:${email}`);
    if (existing) {
      // Si l'utilisateur arrive depuis /limoud/personnaliser avec enableDaily=true,
      // on bascule son record existant en opt-in (idempotent).
      if (enableDaily && existing.confirmed && !existing.dailyEnabled) {
        const updated = {
          ...existing,
          // Génère un optinToken si absent (anciens records)
          optinToken: existing.optinToken || randomBytes(32).toString('hex'),
          dailyEnabled: true,
          dailyEnabledAt: new Date().toISOString(),
        };
        await kv.set(`newsletter:${email}`, updated);
        return res.status(200).json({
          ok: true,
          alreadySubscribed: true,
          dailyEnabled: true,
        });
      }
      return res.status(200).json({ ok: true, alreadySubscribed: true });
    }

    const token = randomBytes(16).toString('hex');
    const optinToken = randomBytes(32).toString('hex');
    const record = {
      email,
      source,
      subscribedAt: new Date().toISOString(),
      confirmed: true, // Single opt-in pour l'instant
      token,
      optinToken,
      sentSteps: [], // Mis à jour avec ['j0'] après envoi du welcome
      // Opt-in immédiat si demandé (case cochée sur /limoud/personnaliser)
      dailyEnabled: enableDaily,
      dailyEnabledAt: enableDaily ? new Date().toISOString() : null,
    };

    await kv.set(`newsletter:${email}`, record);

    try {
      await kv.lpush('newsletter:list', email);
      await kv.ltrim('newsletter:list', 0, 9999);
    } catch (e) {
      console.warn('[newsletter] kv list push failed:', e?.message);
    }

    // Email de bienvenue J0 (best-effort, le cron rattrape si échec)
    if (!process.env.RESEND_API_KEY) {
      console.warn('[newsletter] RESEND_API_KEY absent — J0 non envoyé, cron rattrapera');
    } else {
      try {
        const resend = new Resend(process.env.RESEND_API_KEY);
        const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';
        const j0 = getStepById('j0').build({ email, optinToken });

        const result = await resend.emails.send({
          from: `DAAT <${fromEmail}>`,
          to: email,
          subject: j0.subject,
          html: j0.html,
          text: j0.text,
        });

        if (result.error) {
          console.error('[newsletter] Resend a renvoyé une erreur sur J0:', {
            email,
            error: result.error?.message || result.error,
            name: result.error?.name,
          });
        } else {
          record.sentSteps = ['j0'];
          await kv.set(`newsletter:${email}`, record);
          console.log('[newsletter] J0 envoyé OK', { email, resendId: result.data?.id });
        }
      } catch (e) {
        console.error('[newsletter] exception lors de l\'envoi J0:', {
          email,
          message: e?.message,
          name: e?.name,
        });
      }
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[newsletter/signup] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}

// ---------- GET (Bearer) : cron de séquence ----------
async function handleCron(req, res) {
  // Auth — Vercel envoie ce header automatiquement sur les déclenchements de cron
  const auth = req.headers.authorization || '';
  const expectedSecret = process.env.CRON_SECRET;
  if (!expectedSecret) {
    return res.status(500).json({ error: 'CRON_SECRET non configuré côté serveur' });
  }
  if (auth !== `Bearer ${expectedSecret}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({ error: 'RESEND_API_KEY non configuré' });
  }

  const resend = new Resend(process.env.RESEND_API_KEY);
  const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';

  let processed = 0;
  let sent = 0;
  let errors = 0;
  const log = [];

  try {
    const emails = (await kv.lrange('newsletter:list', 0, 9999)) || [];
    const uniqueEmails = [...new Set(emails)];

    for (const email of uniqueEmails) {
      processed++;
      try {
        const record = await kv.get(`newsletter:${email}`);
        if (!record || !record.confirmed) continue;

        // Lazy: génère un optinToken pour les anciens inscrits sans token.
        // Doit être fait AVANT le build() pour que le CTA enable-daily fonctionne.
        if (!record.optinToken) {
          record.optinToken = randomBytes(32).toString('hex');
          await kv.set(`newsletter:${email}`, record);
        }

        const due = getDueSteps(record.subscribedAt, record.sentSteps || []);
        if (!due.length) continue;

        // Au plus 1 step par run (anti-spam si l'utilisateur s'inscrit puis
        // le cron tourne 14 jours plus tard)
        const step = due[0];
        const tpl = step.build({ email, optinToken: record.optinToken });

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

    const todayISO = new Date().toISOString().slice(0, 10);

    // ───── Phase 2 : Daat Yomi PERSONNEL ─────
    // Envoie le jour courant du plan perso aux users avec un plan en KV.
    // S'exécute AVANT le daily universel (phase 3) pour que le perso prime
    // — l'idempotence partagée (newsletter:daily-sent:{date}:{email}) bloque
    // le second envoi.
    const customEmails = (await kv.lrange('custom-plan:list', 0, 9999)) || [];
    const uniqueCustomEmails = [...new Set(customEmails)];

    let customSent = 0;
    let customSkipped = 0;
    let customErrors = 0;
    const customLog = [];

    for (const email of uniqueCustomEmails) {
      try {
        const customRecord = await kv.get(`custom-plan:${email}`);
        if (!customRecord || !customRecord.plan) continue;

        // Idempotence partagée avec le daily universel : 1 mail/jour/user max,
        // perso prime sur universel (puisqu'on tourne avant).
        const dailyKey = `newsletter:daily-sent:${todayISO}:${email}`;
        const already = await kv.get(dailyKey);
        if (already) {
          customSkipped++;
          continue;
        }

        const customEntry = getEntryForUser(customRecord.plan, todayISO);
        if (!customEntry) {
          // Pas un studyDay du user, ou plan terminé, ou date < startDate.
          customSkipped++;
          continue;
        }

        const { subject, html, text } = buildCustomDailyEmail(
          customEntry,
          customRecord.plan,
          'fr',
        );

        const result = await resend.emails.send({
          from: `DAAT <${fromEmail}>`,
          to: email,
          subject,
          html,
          text,
        });

        if (result.error) {
          customErrors++;
          customLog.push({ email, error: result.error.message });
          continue;
        }

        await kv.set(
          dailyKey,
          {
            resendId: result.data?.id,
            sentAt: new Date().toISOString(),
            source: 'custom',
            dayNumber: customEntry.dayNumber,
          },
          { ex: 172800 },
        );
        customSent++;
        customLog.push({ email, dayNumber: customEntry.dayNumber, ok: true });
      } catch (e) {
        customErrors++;
        customLog.push({ email, error: e?.message });
      }
    }

    // ───── Phase 3 : Daat Yomi UNIVERSEL ─────
    // En plus de la séquence J0-J14 (ci-dessus), envoyer chaque jour le lot
    // Daat Yomi à tous les inscrits qui ont opt-in (`record.dailyEnabled === true`).
    // Idempotence : un seul daily par jour par utilisateur (clé `newsletter:daily-sent:{date}:{email}`,
    // TTL 48h — recalculée à chaque run, pas besoin de garder éternellement).
    // Les users avec un plan perso ont déjà été servis ci-dessus → la clé existe
    // déjà et ils seront skippés ici.
    const entry = getEntryForDate(todayISO);

    let dailySent = 0;
    let dailySkipped = 0;
    let dailyErrors = 0;
    const dailyLog = [];

    if (!entry) {
      // Aujourd'hui = ven/sam, avant le plan, ou après le plan → on saute
      dailyLog.push({ reason: 'not_a_study_day', date: todayISO });
    } else {
      for (const email of uniqueEmails) {
        try {
          const record = await kv.get(`newsletter:${email}`);
          if (!record || !record.confirmed) continue;

          // Lazy: génère un optinToken pour les anciens inscrits sans token,
          // pour que les futurs liens manage (enable/disable-daily) fonctionnent
          // même si l'utilisateur n'a pas encore reçu de séquence.
          if (!record.optinToken) {
            record.optinToken = randomBytes(32).toString('hex');
            await kv.set(`newsletter:${email}`, record);
          }

          // Opt-in explicite requis (anti-spam + maîtrise volume Resend)
          if (!record.dailyEnabled) {
            dailySkipped++;
            continue;
          }

          // Idempotence : un seul daily par jour par utilisateur
          const dailyKey = `newsletter:daily-sent:${todayISO}:${email}`;
          const already = await kv.get(dailyKey);
          if (already) {
            dailySkipped++;
            continue;
          }

          const { subject, html, text } = buildDailyEmail(entry, record.lang || 'fr');

          const result = await resend.emails.send({
            from: `DAAT <${fromEmail}>`,
            to: email,
            subject,
            html,
            text,
          });

          if (result.error) {
            dailyErrors++;
            dailyLog.push({ email, error: result.error.message });
            continue;
          }

          // Mark sent — TTL 48h (on recalcule chaque jour, inutile de garder plus)
          await kv.set(
            dailyKey,
            { resendId: result.data?.id, sentAt: new Date().toISOString() },
            { ex: 172800 },
          );
          dailySent++;
          dailyLog.push({ email, dayNumber: entry.dayNumber, ok: true });
        } catch (e) {
          dailyErrors++;
          dailyLog.push({ email, error: e?.message });
        }
      }
    }

    return res.status(200).json({
      ok: true,
      // Séquence J0-J14
      processed,
      sent,
      errors,
      log: log.slice(0, 50),
      // Daat Yomi PERSONNEL (phase 2, prime sur le universel via idempotence partagée)
      custom: {
        date: todayISO,
        total: uniqueCustomEmails.length,
        sent: customSent,
        skipped: customSkipped,
        errors: customErrors,
        log: customLog.slice(0, 50),
      },
      // Daat Yomi UNIVERSEL (phase 3, ne touche pas les users avec un plan perso
      // déjà envoyé ci-dessus grâce à l'idempotence partagée)
      daily: {
        date: todayISO,
        entry: entry
          ? {
              dayNumber: entry.dayNumber,
              siman: entry.siman.num,
              seifRange: entry.seifRange,
              lotIndex: entry.lotIndex,
              lotTotal: entry.lotTotal,
            }
          : null,
        sent: dailySent,
        skipped: dailySkipped,
        errors: dailyErrors,
        log: dailyLog.slice(0, 50),
      },
    });
  } catch (err) {
    console.error('[newsletter/cron] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur cron' });
  }
}

// ---------- GET ?action=test-daily : envoi manuel d'un daily (Bearer ADMIN_PASSWORD) ----------
async function handleTestDaily(req, res) {
  const auth = req.headers.authorization || '';
  const expected = process.env.ADMIN_PASSWORD || process.env.SOUTIEN_ADMIN_SECRET;
  if (!expected) {
    return res.status(500).json({ error: 'ADMIN_PASSWORD non configuré' });
  }
  if (auth !== `Bearer ${expected}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const url = new URL(req.url, 'http://x');
  const date = url.searchParams.get('date') || new Date().toISOString().slice(0, 10);
  const to = url.searchParams.get('to');

  if (!to || !isValidEmail(to)) {
    return res.status(400).json({ error: 'param "to" requis (email valide)' });
  }

  const entry = getEntryForDate(date);
  if (!entry) {
    return res.status(200).json({
      ok: true,
      skipped: true,
      reason: 'not_a_study_day',
      date,
    });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({ error: 'RESEND_API_KEY non configuré' });
  }

  try {
    const { subject, html, text } = buildDailyEmail(entry, 'fr');
    const resend = new Resend(process.env.RESEND_API_KEY);
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';
    const result = await resend.emails.send({
      from: `DAAT <${fromEmail}>`,
      to,
      subject,
      html,
      text,
    });

    if (result.error) {
      return res.status(500).json({ error: result.error.message });
    }
    return res.status(200).json({
      ok: true,
      sent: true,
      to,
      date,
      entry: {
        dayNumber: entry.dayNumber,
        siman: entry.siman.num,
        seifRange: entry.seifRange,
        lotIndex: entry.lotIndex,
        lotTotal: entry.lotTotal,
      },
      subject,
      resendId: result.data?.id,
    });
  } catch (err) {
    console.error('[newsletter/test-daily] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur test-daily' });
  }
}

// ---------- GET ?action=test-custom-daily : envoi manuel du daily PERSO (Bearer ADMIN_PASSWORD) ----------
async function handleTestCustomDaily(req, res) {
  const auth = req.headers.authorization || '';
  const expected = process.env.ADMIN_PASSWORD || process.env.SOUTIEN_ADMIN_SECRET;
  if (!expected) {
    return res.status(500).json({ error: 'ADMIN_PASSWORD non configuré' });
  }
  if (auth !== `Bearer ${expected}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const url = new URL(req.url, 'http://x');
  const date = url.searchParams.get('date') || new Date().toISOString().slice(0, 10);
  const to = url.searchParams.get('to');

  if (!to || !isValidEmail(to)) {
    return res.status(400).json({ error: 'param "to" requis (email valide)' });
  }

  const customRecord = await kv.get(`custom-plan:${to.toLowerCase().trim()}`);
  if (!customRecord || !customRecord.plan) {
    return res.status(404).json({
      ok: false,
      error: 'Aucun plan personnel trouvé pour cet email',
      to,
    });
  }

  const entry = getEntryForUser(customRecord.plan, date);
  if (!entry) {
    return res.status(200).json({
      ok: true,
      skipped: true,
      reason: 'not_a_study_day_or_plan_finished',
      date,
      plan: customRecord.plan,
    });
  }

  if (!process.env.RESEND_API_KEY) {
    return res.status(500).json({ error: 'RESEND_API_KEY non configuré' });
  }

  try {
    const { subject, html, text } = buildCustomDailyEmail(entry, customRecord.plan, 'fr');
    const resend = new Resend(process.env.RESEND_API_KEY);
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'noreply@daattorah.com';
    const result = await resend.emails.send({
      from: `DAAT <${fromEmail}>`,
      to,
      subject,
      html,
      text,
    });

    if (result.error) {
      return res.status(500).json({ error: result.error.message });
    }
    return res.status(200).json({
      ok: true,
      sent: true,
      to,
      date,
      entry: {
        dayNumber: entry.dayNumber,
        siman: entry.siman.num,
        seifRange: entry.seifRange,
        lotIndex: entry.lotIndex,
        lotTotal: entry.lotTotal,
        isLastDay: entry.isLastDay,
      },
      subject,
      resendId: result.data?.id,
    });
  } catch (err) {
    console.error('[newsletter/test-custom-daily] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur test-custom-daily' });
  }
}

// ---------- GET ?action=enable-daily / disable-daily : 1-click depuis email ----------
//
// Liens cliqués depuis les emails J7/J14 : ne demande pas de password, mais
// vérifie un secret HMAC-like (`optinToken` aléatoire stocké dans le record).
// Réponses HTML pour affichage direct dans le navigateur.

const SITE_URL = 'https://daattorah.com';
const LOGO_URL = `${SITE_URL}/assets/img/og/og-default.svg`;

function escapeHtml(s) {
  return String(s || '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );
}

function htmlPage({ title, accent, icon, headline, message, email, primaryHref, primaryLabel, secondaryHref, secondaryLabel }) {
  const safeMsg = escapeHtml(message);
  const safeEmail = email ? escapeHtml(email) : '';
  const primary = primaryHref
    ? `<a href="${escapeHtml(primaryHref)}" style="display:inline-block;background:#c9a050;color:#0a1f3d;text-decoration:none;padding:14px 28px;font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:600;letter-spacing:2px;text-transform:uppercase;border-radius:3px;margin:6px 8px;">${escapeHtml(primaryLabel)}</a>`
    : '';
  const secondary = secondaryHref
    ? `<a href="${escapeHtml(secondaryHref)}" style="display:inline-block;background:transparent;color:#0a1f3d;text-decoration:none;padding:13px 26px;border:1px solid #c9a050;font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:600;letter-spacing:2px;text-transform:uppercase;border-radius:3px;margin:6px 8px;">${escapeHtml(secondaryLabel)}</a>`
    : '';
  return `<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>${escapeHtml(title)} — DAAT</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Frank+Ruhl+Libre:wght@400;500;700&family=Inter:wght@400;500;600&display=swap">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Cormorant Garamond',Georgia,serif;background:#fdf8f3;color:#0a1f3d;line-height:1.65;min-height:100vh;display:flex;flex-direction:column}
header{background:#0a1f3d;height:70px;display:flex;align-items:center;padding:0 40px;border-bottom:2px solid #c9a050}
.logo{display:flex;align-items:baseline;gap:12px;text-decoration:none}
.logo-hebrew{font-family:'Frank Ruhl Libre',serif;font-size:28px;font-weight:700;color:#c9a050;letter-spacing:2px}
.logo-latin{font-family:'Inter',sans-serif;font-size:13px;color:rgba(255,255,255,.85);letter-spacing:4px;text-transform:uppercase}
main{flex:1;display:flex;align-items:center;justify-content:center;padding:40px 24px}
.card{background:#fff;border:1px solid #e5dcc6;border-radius:6px;padding:48px 36px;max-width:520px;width:100%;text-align:center;box-shadow:0 2px 10px rgba(10,31,61,.06)}
.icon{font-size:48px;line-height:1;margin-bottom:18px;color:${accent}}
h1{font-family:'Cormorant Garamond',serif;font-size:30px;font-weight:600;color:#0a1f3d;margin-bottom:14px;line-height:1.25}
.msg{font-size:17px;color:#3D4266;margin-bottom:24px;line-height:1.6}
.email{font-family:'Inter',sans-serif;font-size:13px;color:#7A7F9A;letter-spacing:.5px;margin-bottom:32px;padding:10px 16px;background:#fdf8f3;border-radius:3px;display:inline-block}
.actions{display:flex;flex-wrap:wrap;justify-content:center;gap:6px}
footer{text-align:center;padding:24px;font-family:'Inter',sans-serif;font-size:11px;color:#7A7F9A;letter-spacing:2px;text-transform:uppercase}
footer a{color:#c9a050;text-decoration:none}
a:focus-visible{outline:3px solid #c9a050;outline-offset:2px}
@media(max-width:540px){header{padding:0 18px}.card{padding:36px 22px}h1{font-size:24px}.msg{font-size:15px}}
</style>
</head><body>
<header>
  <a class="logo" href="${SITE_URL}/">
    <span class="logo-hebrew">דעת</span>
    <span class="logo-latin">DAAT</span>
  </a>
</header>
<main>
  <div class="card">
    <div class="icon">${icon}</div>
    <h1>${escapeHtml(headline)}</h1>
    <p class="msg">${safeMsg}</p>
    ${safeEmail ? `<div class="email">${safeEmail}</div>` : ''}
    <div class="actions">${primary}${secondary}</div>
  </div>
</main>
<footer>© DAAT · <a href="${SITE_URL}/">daattorah.com</a></footer>
</body></html>`;
}

function htmlSuccess(message, email, { mode = 'enabled' } = {}) {
  if (mode === 'disabled') {
    return htmlPage({
      title: 'Rappels désactivés',
      accent: '#0a1f3d',
      icon: '✓',
      headline: 'Rappels désactivés',
      message,
      email,
      primaryHref: `${SITE_URL}/limoud/`,
      primaryLabel: 'Voir l’étude du jour',
      secondaryHref: null,
      secondaryLabel: null,
    });
  }
  // mode === 'enabled' (par défaut)
  const disableUrl = email
    ? `${SITE_URL}/api/newsletter?action=disable-daily&email=${encodeURIComponent(email)}&token=__TOKEN__`
    : null;
  return htmlPage({
    title: 'Rappels activés',
    accent: '#2E7D52',
    icon: '✓',
    headline: 'Rappels activés',
    message,
    email,
    primaryHref: `${SITE_URL}/limoud/`,
    primaryLabel: 'Voir l’étude du jour',
    secondaryHref: disableUrl,
    secondaryLabel: 'Désactiver les rappels',
  });
}

// Variante qui prend le token pour le bouton "Désactiver"
function htmlSuccessEnabled(message, email, token) {
  const disableUrl = `${SITE_URL}/api/newsletter?action=disable-daily&email=${encodeURIComponent(email)}&token=${encodeURIComponent(token)}`;
  return htmlPage({
    title: 'Rappels activés',
    accent: '#2E7D52',
    icon: '✓',
    headline: 'Rappels activés',
    message,
    email,
    primaryHref: `${SITE_URL}/limoud/`,
    primaryLabel: 'Voir l’étude du jour',
    secondaryHref: disableUrl,
    secondaryLabel: 'Désactiver les rappels',
  });
}

function htmlError(message) {
  return htmlPage({
    title: 'Lien invalide',
    accent: '#C04A3E',
    icon: '⚠',
    headline: 'Lien invalide',
    message,
    email: null,
    primaryHref: `${SITE_URL}/limoud/`,
    primaryLabel: 'Voir l’étude du jour',
    secondaryHref: null,
    secondaryLabel: null,
  });
}

async function handleEnableDaily(req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  try {
    const url = new URL(req.url, 'http://x');
    const email = String(url.searchParams.get('email') || '').toLowerCase().trim();
    const token = String(url.searchParams.get('token') || '');

    if (!email || !token || !isValidEmail(email)) {
      return res.status(400).send(htmlError('Le lien est incomplet ou mal formé.'));
    }

    const record = await kv.get(`newsletter:${email}`);
    if (!record) {
      return res.status(404).send(htmlError('Inscription introuvable. Le lien a peut-être expiré, ou tu n’es plus inscrit.'));
    }

    if (!record.optinToken || record.optinToken !== token) {
      return res.status(401).send(htmlError('Ce lien n’est plus valide. Demande un nouveau lien depuis ton dernier email DAAT.'));
    }

    // Idempotent : OK si déjà activé
    if (record.dailyEnabled) {
      return res.status(200).send(htmlSuccessEnabled(
        'Tu reçois déjà les rappels quotidiens. Aucune action supplémentaire n’est nécessaire.',
        email,
        record.optinToken,
      ));
    }

    const updated = {
      ...record,
      dailyEnabled: true,
      dailyEnabledAt: new Date().toISOString(),
    };
    await kv.set(`newsletter:${email}`, updated);

    return res.status(200).send(htmlSuccessEnabled(
      'Tu recevras désormais le Daat Yomi du jour, chaque jour d’étude (dim-jeu).',
      email,
      record.optinToken,
    ));
  } catch (err) {
    console.error('[newsletter/enable-daily] error:', err);
    return res.status(500).send(htmlError('Une erreur est survenue. Réessaie dans quelques minutes.'));
  }
}

async function handleDisableDaily(req, res) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  try {
    const url = new URL(req.url, 'http://x');
    const email = String(url.searchParams.get('email') || '').toLowerCase().trim();
    const token = String(url.searchParams.get('token') || '');

    if (!email || !token || !isValidEmail(email)) {
      return res.status(400).send(htmlError('Le lien est incomplet ou mal formé.'));
    }

    const record = await kv.get(`newsletter:${email}`);
    if (!record) {
      return res.status(404).send(htmlError('Inscription introuvable. Le lien a peut-être expiré.'));
    }

    if (!record.optinToken || record.optinToken !== token) {
      return res.status(401).send(htmlError('Ce lien n’est plus valide. Demande un nouveau lien depuis ton dernier email DAAT.'));
    }

    // Idempotent : OK si déjà désactivé
    if (!record.dailyEnabled) {
      return res.status(200).send(htmlSuccess(
        'Tu ne recevais déjà plus le Daat Yomi quotidien. Tu peux le réactiver à tout moment depuis ton plan personnel.',
        email,
        { mode: 'disabled' },
      ));
    }

    const updated = {
      ...record,
      dailyEnabled: false,
      dailyDisabledAt: new Date().toISOString(),
    };
    await kv.set(`newsletter:${email}`, updated);

    return res.status(200).send(htmlSuccess(
      'Tu ne recevras plus le Daat Yomi quotidien. Tu peux le réactiver à tout moment depuis ton plan personnel.',
      email,
      { mode: 'disabled' },
    ));
  } catch (err) {
    console.error('[newsletter/disable-daily] error:', err);
    return res.status(500).send(htmlError('Une erreur est survenue. Réessaie dans quelques minutes.'));
  }
}

// ---------- GET ?action=stats : lecture admin (ADMIN_PASSWORD ou SOUTIEN_ADMIN_SECRET) ----------
async function handleStats(req, res) {
  const auth = req.headers.authorization || '';
  const expected = process.env.ADMIN_PASSWORD || process.env.SOUTIEN_ADMIN_SECRET;
  if (!expected) {
    return res.status(500).json({ error: 'ADMIN_PASSWORD non configuré' });
  }
  if (auth !== `Bearer ${expected}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const emails = (await kv.lrange('newsletter:list', 0, 9999)) || [];
    const uniqueEmails = [...new Set(emails)];

    const recent = [];
    let confirmed = 0;
    let sentJ0 = 0;
    let sentJ14 = 0;
    const stepCounts = { j0: 0, j3: 0, j7: 0, j10: 0, j14: 0 };

    for (const email of uniqueEmails) {
      const r = await kv.get(`newsletter:${email}`);
      if (!r) continue;
      if (r.confirmed) confirmed++;
      const steps = r.sentSteps || [];
      for (const s of steps) if (s in stepCounts) stepCounts[s]++;
      if (steps.includes('j0')) sentJ0++;
      if (steps.includes('j14')) sentJ14++;
      recent.push({
        email: email.replace(/^(.)(.*)(@.*)$/, (_, a, b, c) => a + '*'.repeat(b.length) + c),
        subscribedAt: r.subscribedAt,
        source: r.source,
        sentSteps: steps,
      });
    }

    recent.sort((a, b) => (b.subscribedAt || '').localeCompare(a.subscribedAt || ''));

    // ─── Stats des plans personnels ───
    const customEmails = (await kv.lrange('custom-plan:list', 0, 9999)) || [];
    const uniqueCustomEmails = [...new Set(customEmails)];
    const customRecent = [];
    let customActive = 0;
    const todayISO = new Date().toISOString().slice(0, 10);
    for (const cemail of uniqueCustomEmails) {
      const cr = await kv.get(`custom-plan:${cemail}`);
      if (!cr || !cr.plan) continue;
      // "active" = aujourd'hui est un studyDay valide ET le plan n'est pas terminé.
      try {
        const entry = getEntryForUser(cr.plan, todayISO);
        if (entry) customActive++;
      } catch (_) { /* ignore */ }
      customRecent.push({
        email: cemail.replace(/^(.)(.*)(@.*)$/, (_, a, b, c) => a + '*'.repeat(b.length) + c),
        savedAt: cr.savedAt,
        rate: cr.plan.rate,
        rateUnit: cr.plan.rateUnit,
        startDate: cr.plan.startDate,
        startSiman: cr.plan.startSiman,
        studyDays: cr.plan.studyDays,
      });
    }
    customRecent.sort((a, b) => (b.savedAt || '').localeCompare(a.savedAt || ''));

    return res.status(200).json({
      ok: true,
      total: uniqueEmails.length,
      confirmed,
      sentJ0,
      sentJ14,
      stepCounts,
      recent: recent.slice(0, 20),
      customPlans: {
        total: uniqueCustomEmails.length,
        active: customActive,
        recent: customRecent.slice(0, 5),
      },
    });
  } catch (err) {
    console.error('[newsletter/stats] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur stats' });
  }
}

// ---------- dispatcher ----------
export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method === 'POST') return handleSignup(req, res);
  if (req.method === 'GET') {
    const url = new URL(req.url, 'http://x');
    const action = url.searchParams.get('action');
    if (action === 'stats') return handleStats(req, res);
    if (action === 'test-daily') return handleTestDaily(req, res);
    if (action === 'test-custom-daily') return handleTestCustomDaily(req, res);
    if (action === 'enable-daily') return handleEnableDaily(req, res);
    if (action === 'disable-daily') return handleDisableDaily(req, res);
    return handleCron(req, res);
  }
  return res.status(405).json({ error: 'GET ou POST uniquement' });
}
