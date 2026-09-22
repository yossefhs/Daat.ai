// Porte commune des points d'administration — freinage des tentatives et CORS fermé.
//
// POURQUOI. Toute la surface d'administration est gardée par un seul mot de passe
// partagé, et deux détails rendaient ce mot de passe devinable en pratique :
//
//   1. AUCUN FREINAGE. Mesuré le 22 septembre 2026 en production : dix requêtes
//      d'affilée avec un secret faux rendent dix 401, sans 429, sans Retry-After.
//      Rien ne comptait les échecs.
//   2. `Access-Control-Allow-Origin: *` était posé sur les six points AVANT le
//      contrôle d'authentification — le 401 lui-même revenait avec cet en-tête.
//      N'importe quelle page web pouvait donc essayer un mot de passe ET LIRE LA
//      RÉPONSE, c'est-à-dire faire chercher le secret par les navigateurs de
//      visiteurs ordinaires. C'est ce qui faisait passer l'attaque de théorique à
//      praticable, et c'est le plus grave des deux.
//
// Ce que coûte la chute de ce mot de passe, pour mémoire : `set-plan` (accorder
// n'importe quel plan, `lifetime` compris), `add-credits`, `reset-limit`,
// `set-force-opus`, la lecture de `users` / `payments` / `logs`, et deux points
// qui appellent des API d'IA payantes (`generate-siman`, `transcribe-photos`).
//
// CE QUI N'EST PAS FAIT ICI, et qui reste ouvert : la comparaison du secret n'est
// pas à temps constant, et le mot de passe partagé demeure. La solution de fond
// est de faire porter l'administration par le JWT et l'OTP que le site a déjà
// (`_auth.js`), ce qui supprimerait la cause au lieu de la protéger.

import { kv } from './_kv.js';

// Les pages d'administration appellent `/api/admin/*` en MÊME origine ; aucune
// requête légitime n'a donc besoin de CORS. La liste sert aux déploiements de
// prévisualisation et se complète par variable d'environnement, sans toucher au code.
const ORIGINES_PAR_DEFAUT = [
  'https://daattorah.com',
  'https://www.daattorah.com',
  'https://daatai.vercel.app',
];

export function originesAutorisees() {
  const sup = String(process.env.ADMIN_ALLOWED_ORIGINS || '')
    .split(',').map((s) => s.trim()).filter(Boolean);
  return [...ORIGINES_PAR_DEFAUT, ...sup];
}

export function corsAdmin(req, res, methodes = 'GET, POST, OPTIONS',
                          entetes = 'Content-Type, Authorization, X-Admin-Secret') {
  const origine = req.headers.origin;
  // `Vary: Origin` est indispensable : sans lui, un cache pourrait servir à un
  // site quelconque la réponse autorisée d'une origine légitime.
  res.setHeader('Vary', 'Origin');
  if (origine && originesAutorisees().includes(origine)) {
    res.setHeader('Access-Control-Allow-Origin', origine);
  }
  res.setHeader('Access-Control-Allow-Methods', methodes);
  res.setHeader('Access-Control-Allow-Headers', entetes);
  res.setHeader('Access-Control-Max-Age', '86400');
}

export const FENETRE = 15 * 60;   // secondes
const MAX_PAR_IP = 5;
const MAX_GLOBAL = 200;           // garde-fou contre une attaque répartie

function adresse(req) {
  const xff = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  return xff || req.socket?.remoteAddress || 'inconnue';
}

const cleIp = (req) => `admin:echecs:${adresse(req)}`;
const CLE_GLOBALE = 'admin:echecs:global';

/**
 * Le demandeur a-t-il déjà trop échoué ? À appeler AVANT de comparer le secret.
 *
 * En cas d'indisponibilité du KV on laisse passer : la porte exige de toute
 * façon le mot de passe, et fermer ici enfermerait dehors l'administrateur
 * légitime chaque fois qu'Upstash a un hoquet.
 */
export async function freinage(req) {
  try {
    const [parIp, global] = await Promise.all([
      kv.get(cleIp(req)),
      kv.get(CLE_GLOBALE),
    ]);
    if (Number(parIp) >= MAX_PAR_IP) return { bloque: true, portee: 'ip' };
    if (Number(global) >= MAX_GLOBAL) return { bloque: true, portee: 'global' };
  } catch {
    return { bloque: false };
  }
  return { bloque: false };
}

export async function echecAdmin(req) {
  try {
    for (const cle of [cleIp(req), CLE_GLOBALE]) {
      await kv.incr(cle);
      const ttl = await kv.ttl(cle);
      if (ttl === -1 || ttl === -2) await kv.expire(cle, FENETRE);
    }
    await kv.lpush('logs:admin', JSON.stringify({
      ts: new Date().toISOString(), ip: adresse(req),
      chemin: req.url ? String(req.url).split('?')[0] : null,
      origine: req.headers.origin || null,
    }));
    await kv.ltrim('logs:admin', 0, 499);
  } catch { /* le journal ne doit jamais faire échouer la requête */ }
}

export async function reussiteAdmin(req) {
  try { await kv.del(cleIp(req)); } catch { /* sans effet sur la requête */ }
}

export function refuser(res) {
  res.setHeader('Retry-After', String(FENETRE));
  return res.status(429).json({ error: 'Trop de tentatives — réessayez plus tard' });
}
