/**
 * _daily-limoud.js — Daat Yomi (daily Limoud) helpers for the cron newsletter.
 *
 * Charge le plan universel `data/limoud-plan.json` (v2.0) et expose les
 * helpers nécessaires pour envoyer un email quotidien à tous les inscrits
 * confirmés ayant opt-in (`record.dailyEnabled === true`).
 *
 * Format d'une entry (cf. data/limoud-plan.json) :
 *   {
 *     dayNumber: number,            // 1..194
 *     date: "YYYY-MM-DD",           // ex "2026-06-08"
 *     dow: 0..4,                    // 0=dim, 1=lun, ..., 4=jeu
 *     siman: {
 *       num: number,                // ex 242
 *       numHe: string,              // ex "רמ״ב"
 *       title: string,              // FR
 *       titleEn: string,            // EN
 *       titleHe: string,            // HE
 *       path: string,               // ex "sources/shabbat/siman-242/index.html"
 *     },
 *     seifRange: [start, end],      // ex [1, 5]
 *     seifCount: number,
 *     lotIndex: number,             // 1..lotTotal
 *     lotTotal: number,             // 1 si le siman tient en un lot
 *     levels: { n1, n2, n3, n4 },
 *     status: "complet" | ...
 *   }
 *
 * API publique :
 *   - loadPlan()                  → { meta, entries, byDate }   (cached)
 *   - getEntryForDate(dateISO)    → entry | null
 *   - buildDailyEmail(entry, lang)→ { subject, html, text }
 *
 * Le module n'effectue aucun appel réseau et ne dépend que du filesystem
 * (les fichiers du repo sont packagés dans le bundle Lambda Vercel).
 */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SITE = 'https://daattorah.com';

// Cache mémoire — Vercel garde le lambda warm entre invocations.
let _planCache = null;

/**
 * Charge le plan depuis le filesystem et le met en cache.
 * Retourne { meta, entries, byDate } où byDate est un index "YYYY-MM-DD" -> entry.
 */
export function loadPlan() {
  if (_planCache) return _planCache;

  // __dirname équivalent ESM
  const here = dirname(fileURLToPath(import.meta.url));
  // api/ → racine du repo → data/limoud-plan.json
  const planPath = join(here, '..', 'data', 'limoud-plan.json');

  const raw = readFileSync(planPath, 'utf8');
  const json = JSON.parse(raw);

  const entries = Array.isArray(json.entries) ? json.entries : [];
  const byDate = Object.create(null);
  for (const entry of entries) {
    if (entry && typeof entry.date === 'string') {
      byDate[entry.date] = entry;
    }
  }

  _planCache = {
    meta: json.meta || {},
    entries,
    byDate,
  };
  return _planCache;
}

/**
 * Retourne l'entry du plan pour la date donnée (format "YYYY-MM-DD", UTC),
 * ou null si :
 *   - la date n'est pas un jour d'étude (ven/sam),
 *   - la date est avant `meta.startDate` ou après `meta.endDate`,
 *   - la date est inconnue du plan.
 */
export function getEntryForDate(dateISO) {
  if (typeof dateISO !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(dateISO)) {
    return null;
  }
  const plan = loadPlan();
  const entry = plan.byDate[dateISO];
  return entry || null;
}

// ---------- Localisation ----------
const LABELS = {
  fr: {
    todayPrefix: "Aujourd'hui",
    fullySiman: 'entièrement',
    seifim: 'séifim',
    lotOf: 'lot {i} sur {n}',
    studyNow: 'ÉTUDIER MAINTENANT (≈20 min)',
    ctaPrimary: 'Voir la page du jour →',
    ctaSecondary: 'Texte hébreu + traduction',
    sigYou: 'Tu reçois cet email parce que tu es inscrit·e à Daat Yomi.',
    unsub: 'Se désinscrire',
    custom: 'Préférer un rythme personnel ?',
    subjectPrefix: 'Daat Yomi · Jour',
    siman: 'Siman',
    dayOfPlan: 'du plan',
  },
};

const FR_DOWS = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
const FR_MONTHS = [
  'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
];

function formatFrDate(dateISO) {
  // dateISO = "YYYY-MM-DD" — on l'interprète comme UTC pour éviter les
  // décalages dus à la timezone du Lambda.
  const [y, m, d] = dateISO.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  const dow = FR_DOWS[dt.getUTCDay()];
  const day = dt.getUTCDate();
  const month = FR_MONTHS[dt.getUTCMonth()];
  const year = dt.getUTCFullYear();
  return `${dow} ${day} ${month} ${year}`;
}

function pickTitle(entry, lang) {
  if (lang === 'en') return entry.siman.titleEn || entry.siman.title;
  if (lang === 'he') return entry.siman.titleHe || entry.siman.title;
  return entry.siman.title;
}

function describeLot(entry, L) {
  const [start, end] = entry.seifRange || [];
  if (entry.lotTotal === 1 && entry.seifCount >= entry.siman.num /* dummy */) {
    // Pas utilisé : on garde la logique simple ci-dessous.
  }
  if (entry.lotTotal === 1 && entry.lotIndex === 1) {
    // Siman entier en un seul lot
    return {
      subjectSuffix: `Siman ${entry.siman.num}`,
      todayLine: `${L.todayPrefix} : Siman ${entry.siman.num} (${L.fullySiman})`,
    };
  }
  // Lot K/N
  const lotOf = L.lotOf.replace('{i}', entry.lotIndex).replace('{n}', entry.lotTotal);
  return {
    subjectSuffix: `Siman ${entry.siman.num} · séifim ${start}-${end} (${entry.lotIndex}/${entry.lotTotal})`,
    todayLine: `${L.todayPrefix} : Siman ${entry.siman.num} · ${L.seifim} ${start}-${end} (${lotOf})`,
  };
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Construit l'email quotidien Daat Yomi pour une entry.
 * `lang` peut être 'fr' (défaut), 'en' ou 'he'. Pour le MVP les libellés
 * restent en FR (lang est une réserve future).
 *
 * `ctx` (optionnel) : `{ email, optinToken }`. Si fourni, le footer affiche
 * un lien 1-click /api/newsletter?action=unsubscribe au lieu d'un mailto.
 * Si absent (anciens appels), fallback mailto pour ne pas casser.
 *
 * @returns {{ subject: string, html: string, text: string }}
 */
export function buildDailyEmail(entry, lang = 'fr', ctx) {
  if (!entry || !entry.siman) {
    throw new Error('buildDailyEmail: entry invalide');
  }
  const L = LABELS.fr; // MVP : libellés FR uniquement
  const title = pickTitle(entry, lang || 'fr');
  const titleHtml = escapeHtml(title);

  const { subjectSuffix, todayLine } = describeLot(entry, L);
  const subject = `${L.subjectPrefix} ${entry.dayNumber} — ${subjectSuffix}`;

  const dateLabel = formatFrDate(entry.date);
  // entry.siman.path = "sources/shabbat/siman-242/index.html"
  // → page du jour = /limoud/jour-NNN.html
  const dayPaddedNNN = String(entry.dayNumber).padStart(3, '0');
  const dayPageHref = `${SITE}/limoud/jour-${dayPaddedNNN}.html`;
  // Page Niveau 1 base = /sources/shabbat/siman-NNN/niveau-1-base.html
  const simanBase = entry.siman.path.replace(/\/index\.html?$/, '');
  const niveau1Href = `${SITE}/${simanBase}/niveau-1-base.html`;

  // Lien 1-click si on a le ctx (email + token), sinon fallback mailto
  // pour ne pas casser les anciens appels (tests, scripts admin).
  const unsubHref = (ctx && ctx.email && ctx.optinToken)
    ? `${SITE}/api/newsletter?action=unsubscribe&email=${encodeURIComponent(ctx.email)}&token=${encodeURIComponent(ctx.optinToken)}`
    : 'mailto:noreply@daattorah.com?subject=' + encodeURIComponent('Désinscription Daat Yomi');
  const customHref = `${SITE}/limoud/personnaliser.html`;

  const html = `<!DOCTYPE html>
<html lang="fr"><body style="font-family:Georgia,'Times New Roman',serif;background:#FAF6EE;margin:0;padding:24px;color:#1A1F3A;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:32px;">
    <div style="display:flex;align-items:baseline;gap:12px;padding-bottom:16px;border-bottom:2px solid #C5A55A;margin-bottom:24px;">
      <span style="font-family:'Frank Ruhl Libre',serif;font-size:32px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT</span>
      <span style="font-family:'Inter',-apple-system,sans-serif;font-size:11px;color:#7A7F9A;letter-spacing:2px;margin-left:auto;">DAAT YOMI</span>
    </div>

    <p style="color:#7A7F9A;font-size:13px;margin:0 0 6px;letter-spacing:.5px;">
      📅 ${escapeHtml(dateLabel)} · Jour ${entry.dayNumber} ${L.dayOfPlan}
    </p>

    <p style="color:#1A1F3A;font-size:15px;margin:6px 0 18px;line-height:1.5;">
      ${escapeHtml(todayLine)}
    </p>

    <h1 style="font-family:Georgia,serif;color:#1A1F3A;font-size:22px;margin:0 0 18px;line-height:1.3;">
      ${titleHtml}
    </h1>

    <p style="color:#3D4266;font-size:14px;margin:18px 0 4px;letter-spacing:1px;">
      📖 ${L.studyNow}
    </p>

    <div style="text-align:center;margin:18px 0 12px;">
      <a href="${dayPageHref}" style="display:inline-block;background:#C5A55A;color:#1A1F3A;padding:14px 28px;text-decoration:none;font-family:'Inter',-apple-system,sans-serif;font-size:14px;font-weight:600;letter-spacing:1px;border-radius:3px;">
        ${L.ctaPrimary}
      </a>
    </div>

    <div style="text-align:center;margin:8px 0 24px;">
      <a href="${niveau1Href}" style="display:inline-block;border:1px solid #C5A55A;color:#1A1F3A;padding:10px 22px;text-decoration:none;font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:500;letter-spacing:.5px;border-radius:3px;background:#FAF6EE;">
        ${L.ctaSecondary}
      </a>
    </div>

    <p style="color:#aaa;font-size:11px;line-height:1.7;margin-top:32px;padding-top:16px;border-top:1px solid #E4DDD0;text-align:center;">
      ${L.sigYou}<br>
      <a href="${unsubHref}" style="color:#C5A55A;">${L.unsub}</a>
      &nbsp;·&nbsp;
      <a href="${customHref}" style="color:#C5A55A;">${L.custom}</a>
    </p>

    <p style="color:#bbb;font-size:10px;line-height:1.6;margin-top:12px;text-align:center;letter-spacing:1px;">
      דעת DAAT · <a href="${SITE}/" style="color:#C5A55A;">daattorah.com</a>
    </p>
  </div>
</body></html>`.trim();

  const text =
    `${dateLabel} · Jour ${entry.dayNumber} du plan\n` +
    `${todayLine}\n\n` +
    `${title}\n\n` +
    `Étudier maintenant (≈20 min) :\n` +
    `${dayPageHref}\n\n` +
    `Texte hébreu + traduction :\n` +
    `${niveau1Href}\n\n` +
    `—\n` +
    `${L.sigYou}\n` +
    `Se désinscrire : ${unsubHref}\n` +
    `Préférer un rythme personnel ? ${customHref}\n\n` +
    `— DAAT דעת`;

  return { subject, html, text };
}

// Export par défaut pour compat éventuelle.
export default { loadPlan, getEntryForDate, buildDailyEmail };
