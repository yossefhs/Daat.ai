// Helpers du système de mise en relation khavroutha (appariement automatique).
//
// Modèle Redis :
//   kh:profile:{id}  → profil complet d'un inscrit
//   kh:pool          → set des id en attente d'appariement (status = 'waiting')
//   kh:matches       → liste (LIFO) des appariements réalisés
//   kh:all           → liste (LIFO) de tous les id (pour l'admin)
import { kv } from './_kv.js';

export const K_POOL = 'kh:pool';
export const K_MATCHES = 'kh:matches';
export const K_ALL = 'kh:all';
export const kProfile = (id) => `kh:profile:${id}`;

export const NIVEAUX = new Set(['base', 'lamdan', 'synthese', 'mixte']);
export const GENRES = new Set(['h', 'f']);
export const LANGUES = new Set(['fr', 'he', 'en']);
export const JOURS = new Set(['dim', 'lun', 'mar', 'mer', 'jeu', 'ven']);
export const MOMENTS = new Set(['matin', 'aprem', 'soir', 'nuit']);
export const FORMATS = new Set(['visio', 'tel', 'presentiel', 'peu-importe']);

// Numéro → chiffres internationaux pour wa.me (sans +, ni espaces).
export function normalizePhone(raw) {
  const s = String(raw || '').replace(/[^\d]/g, '');
  return s;
}

export function waLink(phoneDigits, text) {
  if (!phoneDigits) return null;
  return 'https://wa.me/' + phoneDigits + (text ? '?text=' + encodeURIComponent(text) : '');
}

function sharedCount(a, b) {
  if (!Array.isArray(a) || !Array.isArray(b)) return 0;
  return a.filter((x) => b.includes(x)).length;
}

// Contrainte dure : même genre, même langue, niveau compatible (mixte = joker),
// au moins un jour ET un moment en commun.
export function isHardCompatible(a, b) {
  if (!a || !b || a.id === b.id) return false;
  if (a.genre !== b.genre) return false;
  if (a.langue !== b.langue) return false;
  if (a.niveau !== 'mixte' && b.niveau !== 'mixte' && a.niveau !== b.niveau) return false;
  if (sharedCount(a.jours, b.jours) < 1) return false;
  if (sharedCount(a.moments, b.moments) < 1) return false;
  return true;
}

// Score de compatibilité (plus haut = meilleur appariement).
export function score(a, b) {
  let s = sharedCount(a.jours, b.jours) * 3 + sharedCount(a.moments, b.moments) * 3;
  if (a.niveau === b.niveau) s += 5;
  if (a.format && b.format && a.format === b.format && a.format !== 'peu-importe') s += 3;
  if (a.ville && b.ville && a.ville.toLowerCase().trim() === b.ville.toLowerCase().trim()) s += 4;
  return s;
}

// Cherche dans le vivier le meilleur partenaire pour `profile`.
// Nettoie au passage les entrées orphelines/non-waiting.
export async function findBestMatch(profile) {
  const ids = (await kv.smembers(K_POOL)) || [];
  const candidates = [];
  for (const cid of ids) {
    if (cid === profile.id) continue;
    const c = await kv.get(kProfile(cid));
    if (!c || c.status !== 'waiting') {
      await kv.srem(K_POOL, cid);
      continue;
    }
    if (isHardCompatible(profile, c)) candidates.push(c);
  }
  if (!candidates.length) return null;
  candidates.sort((x, y) => {
    const d = score(profile, y) - score(profile, x);
    if (d !== 0) return d;
    return String(x.createdAt).localeCompare(String(y.createdAt)); // le plus ancien d'abord
  });
  return candidates[0];
}

// Message d'intro pré-rempli (dans la langue partagée), pour le lien wa.me.
const NIVEAU_LABEL = {
  fr: { base: 'Base', lamdan: 'Lamdan', synthese: 'Synthèse', mixte: 'tous niveaux' },
  he: { base: 'בסיס', lamdan: 'למדן', synthese: 'סיכום', mixte: 'כל הרמות' },
  en: { base: 'Base', lamdan: 'Lamdan', synthese: 'Summary', mixte: 'all levels' },
};

export function introMessage(lang, toName, fromName, niveau) {
  const lvl = (NIVEAU_LABEL[lang] || NIVEAU_LABEL.fr)[niveau] || '';
  if (lang === 'he') {
    return `שלום ${toName}! 👋 הופנינו זה לזה דרך דעת ללימוד בחברותא (${lvl}). מתי נוח לך להתחיל סימן ביחד? — daattorah.com`;
  }
  if (lang === 'en') {
    return `Hi ${toName}! 👋 We were matched through Daat for a chavruta (${lvl}). When works for you to start a siman together? — daattorah.com`;
  }
  return `Shalom ${toName} ! 👋 On a été mis en relation par Daat pour une khavroutha (${lvl}). Quand veux-tu qu'on commence un siman ensemble ? — daattorah.com`;
}
