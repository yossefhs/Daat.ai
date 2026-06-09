/**
 * _custom-plan-engine.js — Daat Yomi PERSONNEL helpers for the cron newsletter.
 *
 * Charge le catalogue `data/limoud-simanim-catalog.json` (124 simanim, 242→365)
 * et calcule, pour un plan perso { rate, rateUnit, studyDays, startDate,
 * startSiman }, l'entry du jour à envoyer par email.
 *
 * Format du plan perso (cohérent avec assets/js/daat-custom-plan.js client) :
 *   {
 *     rate: 1 | 5 | 50 | number,        // séifim/jour OU 50 = siman/jour
 *     rateUnit: 'seifim_per_day' | 'siman_per_day',
 *     studyDays: [0,1,2,3,4],            // 0=dim, 6=sam
 *     startDate: 'YYYY-MM-DD',
 *     startSiman: 242,                    // siman de départ
 *     completedDays: [1, 2, 3, ...],     // optionnel
 *     createdAt: ISO
 *   }
 *
 * API publique :
 *   - loadCatalog()                                → { meta, simanim, byNum }   (cached)
 *   - getStudyDayNumber(planConfig, todayISO)      → number | null
 *   - getEntryForUser(planConfig, todayISO)        → entry | null
 *   - buildCustomDailyEmail(entry, planConfig, lang) → { subject, html, text }
 *
 * Aucun appel réseau ; uniquement filesystem (le catalogue est packagé dans le
 * bundle Lambda Vercel).
 */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SITE = 'https://daattorah.com';

// Cache mémoire — Vercel garde le lambda warm entre invocations.
let _catalogCache = null;

/**
 * Charge le catalogue depuis le filesystem et le met en cache.
 * Retourne { meta, simanim, byNum } où byNum est un index num → siman.
 */
export function loadCatalog() {
  if (_catalogCache) return _catalogCache;

  const here = dirname(fileURLToPath(import.meta.url));
  const catalogPath = join(here, '..', 'data', 'limoud-simanim-catalog.json');

  const raw = readFileSync(catalogPath, 'utf8');
  const json = JSON.parse(raw);

  const simanim = Array.isArray(json.simanim) ? json.simanim : [];
  const byNum = Object.create(null);
  for (const s of simanim) {
    if (s && typeof s.num === 'number') byNum[s.num] = s;
  }

  _catalogCache = {
    meta: json.meta || {},
    simanim,
    byNum,
  };
  return _catalogCache;
}

// ---------- Utilitaires dates (UTC) ----------
function parseISO(s) {
  if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
  const [y, m, d] = s.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  if (isNaN(dt.getTime())) return null;
  return dt;
}

function daysBetween(startDate, endDate) {
  const MS = 86400000;
  return Math.floor((endDate.getTime() - startDate.getTime()) / MS);
}

/**
 * Compte le nombre de jours d'étude entre startDate (inclus) et today (inclus)
 * selon le tableau studyDays du user. Retourne null si today < startDate ou si
 * today n'est pas un studyDay.
 *
 * Retourne le N-ième jour d'étude (1-based) : pour le 1er studyDay c'est 1.
 *
 * @param {{ studyDays: number[], startDate: string }} planConfig
 * @param {string} todayISO
 * @returns {number | null}
 */
export function getStudyDayNumber(planConfig, todayISO) {
  if (!planConfig || !Array.isArray(planConfig.studyDays) || !planConfig.studyDays.length) {
    return null;
  }
  const start = parseISO(planConfig.startDate);
  const today = parseISO(todayISO);
  if (!start || !today) return null;
  if (today.getTime() < start.getTime()) return null;

  const studySet = new Set(planConfig.studyDays.map((d) => parseInt(d, 10)));
  const todayDow = today.getUTCDay();
  if (!studySet.has(todayDow)) return null;

  // Compte les jours d'étude entre start (inclus) et today (inclus).
  const totalDays = daysBetween(start, today); // 0 si même jour
  let count = 0;
  for (let i = 0; i <= totalDays; i++) {
    const d = new Date(start.getTime() + i * 86400000);
    if (studySet.has(d.getUTCDay())) count++;
  }
  return count > 0 ? count : null;
}

function makeSimanPath(num) {
  return `sources/shabbat/siman-${num}/index.html`;
}

/**
 * Construit la liste des "lots" (entries) pour un plan donné, du startSiman
 * jusqu'à la fin du corpus. N'effectue pas l'assignation de dates.
 * Reproduit la logique côté client (assets/js/daat-custom-plan.js — buildLots).
 *
 * @returns {Array<{ simanNum, numHe, title, titleEn, titleHe,
 *   seifStart, seifEnd, lotIndex, lotTotal }>}
 */
function buildLots(planConfig, catalog) {
  const lots = [];
  const rate = parseInt(planConfig.rate, 10) || 1;
  const rateUnit = planConfig.rateUnit === 'siman_per_day' ? 'siman_per_day' : 'seifim_per_day';
  const startSiman = parseInt(planConfig.startSiman, 10) || 242;

  const simanList = catalog.simanim
    .filter((s) => s.num >= startSiman)
    .sort((a, b) => a.num - b.num);

  for (const siman of simanList) {
    const total = siman.totalSeifim;
    if (rateUnit === 'siman_per_day') {
      lots.push({
        simanNum: siman.num,
        numHe: siman.numHe,
        title: siman.title,
        titleEn: siman.titleEn,
        titleHe: siman.titleHe,
        seifStart: 1,
        seifEnd: total,
        lotIndex: 1,
        lotTotal: 1,
      });
      continue;
    }
    const lotTotal = Math.max(1, Math.ceil(total / rate));
    let seif = 1;
    let lotIdx = 1;
    while (seif <= total) {
      const end = Math.min(total, seif + rate - 1);
      lots.push({
        simanNum: siman.num,
        numHe: siman.numHe,
        title: siman.title,
        titleEn: siman.titleEn,
        titleHe: siman.titleHe,
        seifStart: seif,
        seifEnd: end,
        lotIndex: lotIdx,
        lotTotal,
      });
      seif = end + 1;
      lotIdx++;
    }
  }
  return lots;
}

/**
 * Retourne l'entry pour le jour courant du user, ou null si :
 *   - aujourd'hui n'est pas un studyDay du user
 *   - aujourd'hui < startDate
 *   - le plan a été épuisé (user a dépassé le dernier lot)
 *
 * @param {Object} planConfig
 * @param {string} todayISO  format "YYYY-MM-DD"
 * @returns {Object | null}
 */
export function getEntryForUser(planConfig, todayISO) {
  if (!planConfig || typeof planConfig !== 'object') return null;
  const dayNumber = getStudyDayNumber(planConfig, todayISO);
  if (dayNumber == null) return null;

  const catalog = loadCatalog();
  const lots = buildLots(planConfig, catalog);
  if (!lots.length) return null;

  // dayNumber est 1-based ; lots est 0-based.
  const idx = dayNumber - 1;
  if (idx >= lots.length) return null; // plan terminé

  const lot = lots[idx];
  const isLastDay = idx === lots.length - 1;

  return {
    dayNumber,
    date: todayISO,
    siman: {
      num: lot.simanNum,
      numHe: lot.numHe,
      title: lot.title,
      titleEn: lot.titleEn,
      titleHe: lot.titleHe,
      path: makeSimanPath(lot.simanNum),
    },
    seifRange: [lot.seifStart, lot.seifEnd],
    seifCount: lot.seifEnd - lot.seifStart + 1,
    lotIndex: lot.lotIndex,
    lotTotal: lot.lotTotal,
    isLastDay,
  };
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
    sigYou: 'Tu reçois cet email parce que tu as activé le Daat Yomi personnel.',
    unsub: 'Modifier mon plan',
    universal: 'Préférer le rythme universel ?',
    subjectPrefix: 'Mon plan · Jour',
    siman: 'Siman',
    dayOfPlan: 'de ton plan',
    bannerTitle: 'Daat Yomi PERSONNEL',
    lastDayLabel: '🎉 Dernier jour de ton plan — Bravo !',
  },
};

const FR_DOWS = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
const FR_MONTHS = [
  'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
];

function formatFrDate(dateISO) {
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
  if (entry.lotTotal === 1 && entry.lotIndex === 1) {
    return {
      subjectSuffix: `Siman ${entry.siman.num}`,
      todayLine: `${L.todayPrefix} : Siman ${entry.siman.num} (${L.fullySiman})`,
    };
  }
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
 * Construit l'email quotidien Daat Yomi PERSONNEL pour une entry custom-plan.
 * Réutilise le style de buildDailyEmail mais avec un subject "Mon plan",
 * une bannière "Daat Yomi PERSONNEL", et un footer pointant vers
 * /limoud/personnaliser.html (modifier le plan).
 *
 * @param {Object} entry — sortie de getEntryForUser()
 * @param {Object} planConfig — pour rappel du rythme dans le footer (optionnel)
 * @param {string} lang — 'fr' (défaut), 'en', 'he'
 * @param {Object} [ctx] — `{ email, optinToken }`. Si fourni, le lien
 *   "Désinscription" du footer pointe vers /api/newsletter?action=unsubscribe
 *   plutôt que vers un mailto.
 * @returns {{ subject: string, html: string, text: string }}
 */
export function buildCustomDailyEmail(entry, planConfig, lang = 'fr', ctx) {
  if (!entry || !entry.siman) {
    throw new Error('buildCustomDailyEmail: entry invalide');
  }
  const L = LABELS.fr; // MVP : libellés FR uniquement
  const title = pickTitle(entry, lang || 'fr');
  const titleHtml = escapeHtml(title);

  const { subjectSuffix, todayLine } = describeLot(entry, L);
  const subject = `${L.subjectPrefix} ${entry.dayNumber} — ${subjectSuffix}`;

  const dateLabel = formatFrDate(entry.date);
  // entry.siman.path = "sources/shabbat/siman-242/index.html"
  // → page du siman pour la version perso
  const simanBase = entry.siman.path.replace(/\/index\.html?$/, '');
  const simanHref = `${SITE}/${simanBase}/index.html`;
  const niveau1Href = `${SITE}/${simanBase}/niveau-1-base.html`;

  const customHref = `${SITE}/limoud/personnaliser.html`;
  const universalHref = `${SITE}/limoud/index.html`;
  // Lien 1-click si on a le ctx (email + token), sinon fallback mailto.
  const unsubHref = (ctx && ctx.email && ctx.optinToken)
    ? `${SITE}/api/newsletter?action=unsubscribe&email=${encodeURIComponent(ctx.email)}&token=${encodeURIComponent(ctx.optinToken)}`
    : 'mailto:noreply@daattorah.com?subject=' + encodeURIComponent('Désactiver Daat Yomi personnel');

  const rate = planConfig && parseInt(planConfig.rate, 10);
  const rateUnit = planConfig && planConfig.rateUnit;
  let rateLabel = '';
  if (rate && rateUnit === 'siman_per_day') {
    rateLabel = `${rate} siman/jour`;
  } else if (rate) {
    rateLabel = `${rate} ${L.seifim}/jour`;
  }

  const lastDayBlock = entry.isLastDay
    ? `<p style="background:#FAF6EE;border:1px solid #C5A55A;color:#1A1F3A;padding:12px 14px;border-radius:4px;margin:14px 0 0;font-size:14px;text-align:center;">${L.lastDayLabel}</p>`
    : '';

  const html = `<!DOCTYPE html>
<html lang="fr"><body style="font-family:Georgia,'Times New Roman',serif;background:#FAF6EE;margin:0;padding:24px;color:#1A1F3A;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E4DDD0;border-radius:8px;padding:32px;">
    <div style="display:flex;align-items:baseline;gap:12px;padding-bottom:16px;border-bottom:2px solid #C5A55A;margin-bottom:24px;">
      <span style="font-family:'Frank Ruhl Libre',serif;font-size:32px;font-weight:700;color:#C5A55A;">דעת</span>
      <span style="font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:600;color:#1A1F3A;letter-spacing:4px;">DAAT</span>
      <span style="font-family:'Inter',-apple-system,sans-serif;font-size:11px;color:#7A7F9A;letter-spacing:2px;margin-left:auto;">MON PLAN</span>
    </div>

    <div style="background:#1A1F3A;color:#FAF6EE;padding:14px 18px;border-radius:4px;border:1px solid #C5A55A;margin-bottom:22px;">
      <p style="font-family:'Inter',-apple-system,sans-serif;font-size:11px;letter-spacing:3px;color:#C5A55A;margin:0 0 4px;text-transform:uppercase;">📖 ${L.bannerTitle}</p>
      <p style="font-family:Georgia,serif;font-size:17px;margin:0;color:#FAF6EE;">Jour ${entry.dayNumber} ${L.dayOfPlan}${rateLabel ? ` · <span style="color:#C5A55A;">${rateLabel}</span>` : ''}</p>
    </div>

    <p style="color:#7A7F9A;font-size:13px;margin:0 0 6px;letter-spacing:.5px;">
      📅 ${escapeHtml(dateLabel)}
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
      <a href="${simanHref}" style="display:inline-block;background:#C5A55A;color:#1A1F3A;padding:14px 28px;text-decoration:none;font-family:'Inter',-apple-system,sans-serif;font-size:14px;font-weight:600;letter-spacing:1px;border-radius:3px;">
        ${L.ctaPrimary}
      </a>
    </div>

    <div style="text-align:center;margin:8px 0 24px;">
      <a href="${niveau1Href}" style="display:inline-block;border:1px solid #C5A55A;color:#1A1F3A;padding:10px 22px;text-decoration:none;font-family:'Inter',-apple-system,sans-serif;font-size:13px;font-weight:500;letter-spacing:.5px;border-radius:3px;background:#FAF6EE;">
        ${L.ctaSecondary}
      </a>
    </div>

    ${lastDayBlock}

    <p style="color:#aaa;font-size:11px;line-height:1.7;margin-top:32px;padding-top:16px;border-top:1px solid #E4DDD0;text-align:center;">
      ${L.sigYou}<br>
      <a href="${customHref}" style="color:#C5A55A;">${L.unsub}</a>
      &nbsp;·&nbsp;
      <a href="${universalHref}" style="color:#C5A55A;">${L.universal}</a>
      &nbsp;·&nbsp;
      <a href="${unsubHref}" style="color:#C5A55A;">Désinscription</a>
    </p>

    <p style="color:#bbb;font-size:10px;line-height:1.6;margin-top:12px;text-align:center;letter-spacing:1px;">
      דעת DAAT · <a href="${SITE}/" style="color:#C5A55A;">daattorah.com</a>
    </p>
  </div>
</body></html>`.trim();

  const text =
    `${dateLabel} · Jour ${entry.dayNumber} ${L.dayOfPlan}` +
    (rateLabel ? ` (${rateLabel})` : '') + `\n` +
    `${L.bannerTitle}\n\n` +
    `${todayLine}\n\n` +
    `${title}\n\n` +
    `Étudier maintenant (≈20 min) :\n` +
    `${simanHref}\n\n` +
    `Texte hébreu + traduction :\n` +
    `${niveau1Href}\n\n` +
    (entry.isLastDay ? `${L.lastDayLabel}\n\n` : '') +
    `—\n` +
    `${L.sigYou}\n` +
    `Modifier mon plan : ${customHref}\n` +
    `Préférer le rythme universel ? ${universalHref}\n` +
    `Désinscription : ${unsubHref}\n\n` +
    `— DAAT דעת`;

  return { subject, html, text };
}

// Export par défaut pour compat éventuelle.
export default { loadCatalog, getStudyDayNumber, getEntryForUser, buildCustomDailyEmail };
