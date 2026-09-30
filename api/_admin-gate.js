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
import { getUserFromRequest } from './_auth.js';

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

/**
 * L'origine est-elle refusée ? À appeler APRÈS le préflight, AVANT tout le reste.
 *
 * La liste d'origines a d'abord été posée par le seul CORS, et cela NE SUFFIT PAS —
 * mesuré en production le 23 septembre 2026 : sur quatorze requêtes venues d'une
 * origine étrangère, DIX recevaient encore « Access-Control-Allow-Origin: * ».
 * `vercel.json` pose cet en-tête sur /api/ au niveau de la plateforme, et l'exclusion
 * de /api/admin/ par expression régulière n'est pas appliquée de façon fiable.
 *
 * Mais la vraie leçon n'est pas de syntaxe : **le CORS est un contrôle de navigateur**.
 * Il demande au navigateur de ne pas laisser LIRE la réponse ; il n'empêche jamais la
 * requête d'arriver, et il ne protège rien de ce qui n'est pas un navigateur. Faire
 * reposer une porte d'administration dessus, c'était la construction faible.
 *
 * On refuse donc côté SERVEUR. Une page hébergée ailleurs qui tente un mot de passe
 * reçoit 403 sans que la comparaison ait lieu : elle n'apprend rien, quel que soit
 * l'en-tête que la plateforme ajoute ensuite. Une requête sans `Origin` — même origine,
 * ou appel serveur à serveur — passe et retombe sur le mot de passe, comme avant.
 */
export function origineRefusee(req) {
  const origine = req.headers.origin;
  return Boolean(origine) && !originesAutorisees().includes(origine);
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

/**
 * L'administrateur est-il identifié par le JWT du site, plutôt que par le mot
 * de passe partagé ? Rend son adresse, ou null.
 *
 * PREMIÈRE ÉTAPE DU REMPLACEMENT DU MOT DE PASSE PARTAGÉ, et elle est purement
 * ADDITIVE : le mot de passe continue de fonctionner exactement comme avant, et
 * si `ADMIN_EMAILS` n'est pas définie, rien ne change du tout. Aucun risque
 * d'enfermer dehors l'administrateur légitime.
 *
 * Ce que cette voie apporte, et que le mot de passe ne peut pas donner : une
 * IDENTITÉ (on sait QUI a changé un plan), une EXPIRATION (le jeton vit ce que
 * dure la session), une RÉVOCATION individuelle (retirer une adresse de la
 * liste ne dérange personne d'autre), et plus aucun secret à se transmettre.
 *
 * ⚠️ Le cookie de session est `SameSite=None` — il le faut, l'API vit sur
 * daatai.vercel.app et le site sur daattorah.com. Il part donc AUSSI sur une
 * requête déclenchée par une page tierce. C'est exactement pourquoi le refus
 * d'origine ci-dessus doit rester, et pourquoi il devient PLUS important une
 * fois qu'un cookie peut authentifier : il est la seule défense contre une page
 * malveillante qui ferait agir le navigateur de l'administrateur à son insu.
 * L'en-tête `Origin` est posé par le navigateur sur toute requête d'origine
 * étrangère et ne peut pas être falsifié par du JavaScript.
 */
export function adminParJeton(req) {
  const liste = String(process.env.ADMIN_EMAILS || process.env.ADMIN_EMAIL || '')
    .split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);
  if (!liste.length) return null;
  const user = getUserFromRequest(req);
  if (!user?.email) return null;
  const email = String(user.email).trim().toLowerCase();
  return liste.includes(email) ? email : null;
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

export function refuserOrigine(res) {
  return res.status(403).json({ error: 'Origine non autorisée' });
}


export function refuser(res) {
  res.setHeader('Retry-After', String(FENETRE));
  return res.status(429).json({ error: 'Trop de tentatives — réessayez plus tard' });
}
