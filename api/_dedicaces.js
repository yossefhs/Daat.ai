// Helpers partagés pour le système de dédicaces HelloAsso.
//
// Stockage : Upstash Redis (Vercel KV étant « sunset »).
// On privilégie Redis.fromEnv() — qui lit UPSTASH_REDIS_REST_URL /
// UPSTASH_REDIS_REST_TOKEN — comme demandé. Si ces variables ne sont pas
// présentes, on retombe sur les variables KV_REST_API_* déjà utilisées par
// le reste du code (api/_kv.js), de sorte que les dédicaces et les autres
// données vivent dans la même base Upstash.
//
// Modèle de données Redis :
//   dedic:siman:{N}  → liste (LIFO) des dédicaces du siman N
//   dedic:all        → liste (LIFO) globale de toutes les dédicaces
//   dedic:orders     → set des order id HelloAsso déjà traités (anti-doublon)
import { Redis } from '@upstash/redis';

let _redis;

// Construction paresseuse : importer ce module ne lève jamais d'erreur même
// si les variables d'environnement sont absentes (utile en build / preview).
export function getRedis() {
  if (_redis) return _redis;
  if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    _redis = Redis.fromEnv();
  } else {
    _redis = new Redis({
      url: process.env.KV_REST_API_URL,
      token: process.env.KV_REST_API_TOKEN,
    });
  }
  return _redis;
}

// ── Clés Redis ──────────────────────────────────────────────────────────────
export const K_ALL = 'dedic:all';
export const K_ORDERS = 'dedic:orders';
export const kSiman = (n) => `dedic:siman:${n}`;

// Bornes de rétention pour ne pas faire grossir les listes indéfiniment.
const MAX_PER_SIMAN = 99; // 100 dédicaces max affichées par siman
const MAX_ALL = 999; // 1000 dédicaces max dans le flux global

// ── Types de dédicace → libellé hébreu ──────────────────────────────────────
export const DEDIC_TYPES = {
  ilui: { he: 'לעילוי נשמת', fr: 'Illoui Nichmat' }, // à la mémoire
  refoua: { he: 'לרפואה שלמה', fr: 'Refoua Chelema' }, // guérison
  hatzlacha: { he: 'להצלחה', fr: 'Hatzlacha' }, // réussite
};

// Normalise un libellé de type (FR/EN/HE, saisi librement côté HelloAsso ou
// admin) vers une des trois clés canoniques. Défaut : « ilui » (le cas le
// plus fréquent pour une dédicace d'étude).
export function normalizeType(raw) {
  const s = String(raw || '').toLowerCase().trim();
  if (!s) return 'ilui';
  if (/נשמת|עילוי|ilui|illoui|iloui|m[ée]moire|memory|nichmat|nechama|נפטר|נשמה/.test(s)) return 'ilui';
  if (/רפוא|refoua|refua|refoua|gu[ée]ris|heal|recover|רפו/.test(s)) return 'refoua';
  if (/הצלח|hatzlacha|hatslacha|hatzla|r[ée]ussit|success|succ[èe]s|parnassa|זיווג|shidoukh/.test(s)) return 'hatzlacha';
  return 'ilui';
}

// Construit un objet dédicace normalisé.
export function makeDedicace({ siman, nom, type, source, orderId }) {
  const t = normalizeType(type);
  // Tolère « 242 », 242, « Siman 242 », « סימן רמב » → on extrait les chiffres.
  const n = parseInt((String(siman).match(/\d+/) || [])[0], 10);
  return {
    id: 'ded-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7),
    siman: Number.isFinite(n) ? n : null,
    nom: String(nom || '').trim().slice(0, 120),
    type: t,
    typeHe: DEDIC_TYPES[t].he,
    source: source || 'manual',
    orderId: orderId != null ? String(orderId) : null,
    createdAt: Date.now(),
  };
}

// @upstash/redis (de)sérialise le JSON automatiquement. Selon le chemin, un
// élément de liste peut revenir soit en objet, soit en string : on gère les
// deux pour être robuste.
export function parseItem(x) {
  if (x == null) return null;
  if (typeof x === 'object') return x;
  try {
    return JSON.parse(x);
  } catch {
    return null;
  }
}

// Écrit une dédicace dans Redis (liste du siman + flux global).
export async function saveDedicace(redis, d) {
  const ops = [redis.lpush(K_ALL, d), redis.ltrim(K_ALL, 0, MAX_ALL)];
  if (d.siman != null) {
    ops.unshift(redis.lpush(kSiman(d.siman), d), redis.ltrim(kSiman(d.siman), 0, MAX_PER_SIMAN));
  }
  await Promise.all(ops);
}

// Lit les dédicaces d'un siman (les plus récentes d'abord).
export async function listSiman(redis, n, limit = 50) {
  const raw = await redis.lrange(kSiman(n), 0, limit - 1);
  return (raw || []).map(parseItem).filter(Boolean);
}

// Lit le flux global de dédicaces.
export async function listAll(redis, limit = 200) {
  const raw = await redis.lrange(K_ALL, 0, limit - 1);
  return (raw || []).map(parseItem).filter(Boolean);
}

// Réécrit une liste de bout en bout en préservant l'ordre (newest → oldest).
async function rewriteList(redis, key, items) {
  await redis.del(key);
  if (items.length) await redis.rpush(key, ...items);
}

// Supprime une dédicace par id (du flux global ET de la liste du siman).
// Renvoie true si trouvée et supprimée, false sinon.
export async function deleteDedicace(redis, id) {
  const all = await listAll(redis, 1000);
  const target = all.find((d) => d && d.id === id);
  if (!target) return false;
  await rewriteList(redis, K_ALL, all.filter((d) => d && d.id !== id));
  if (target.siman != null) {
    const sm = await listSiman(redis, target.siman, 1000);
    await rewriteList(redis, kSiman(target.siman), sm.filter((d) => d && d.id !== id));
  }
  return true;
}
