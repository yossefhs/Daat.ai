// Module partagé des plans payants — une seule porte d'écriture, quel que soit le canal.
//
// Trois canaux peuvent poser un plan sur un compte : HelloAsso (site), les magasins
// d'applications (Apple App Store, Google Play — via api/iap-webhook.js) et l'admin.
// Tous écrivent les MÊMES clés, lues par api/chat.js (identifyUser) :
//
//   user:plan:{email}          → nom du plan (khavroutha, beit_midrash, …, lifetime)
//   user:plan_expires:{email}  → 'YYYY-MM-DD' (absent pour lifetime) ; chat.js rétrograde
//                                en 'free' dès que la date est dépassée (comparaison de
//                                chaînes, inclusive du jour stocké)
//   user:plan_source:{email}   → 'helloasso' | 'apple' | 'google' | 'manual'
//
// Règle de cohabitation (un même compte peut avoir donné sur le site ET s'être
// abonné dans l'app) : on ne RACCOURCIT jamais un droit acquis.
//   - un plan `lifetime` actif n'est jamais remplacé ;
//   - un plan actif de rang supérieur venant d'un AUTRE canal est conservé ;
//   - à plan égal, l'échéance la plus lointaine gagne (null = sans échéance, gagne) ;
//   - une révocation (expiration côté magasin) ne touche que le plan posé par CE canal.
//
// Les fonctions acceptent un client `kv` injectable pour les tests ; par défaut
// elles utilisent le client Redis partagé.

import { kv as defaultKv } from './_kv.js';

export const SUBSCRIBER_PLANS = new Set([
  'khavroutha', 'beit_midrash', 'beit_midrash_plus', 'yeshiva', 'lifetime', 'premium',
]);

// Rang de générosité — sert uniquement à arbitrer entre deux canaux.
export const PLAN_RANK = {
  free: 0,
  khavroutha: 1,
  beit_midrash: 2,
  beit_midrash_plus: 3,
  yeshiva: 4,
  premium: 4,
  lifetime: 5,
};

export const PLAN_SOURCES = new Set(['helloasso', 'apple', 'google', 'manual']);

export function normalizeEmail(email) {
  return String(email || '').trim().toLowerCase();
}

export function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

// Millisecondes epoch → 'YYYY-MM-DD', avec un délai de grâce en jours (absorbe les
// relances de facturation : le magasin réessaie quelques jours avant d'expirer).
export function msToISODate(ms, graceDays = 0) {
  const n = Number(ms);
  if (!Number.isFinite(n) || n <= 0) return null;
  return new Date(n + Math.max(0, graceDays) * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
}

function rank(plan) {
  return PLAN_RANK[plan] ?? 0;
}

// L'échéance la plus lointaine ; null (sans échéance) l'emporte toujours.
function laterExpiry(a, b) {
  if (!a || !b) return null;
  return a >= b ? a : b;
}

export function isActive({ plan, expires }, today = todayISO()) {
  if (!plan || !SUBSCRIBER_PLANS.has(plan)) return false;
  if (plan === 'lifetime' || !expires) return true;
  return today <= String(expires).slice(0, 10);
}

export async function readPlan(email, kv = defaultKv) {
  const e = normalizeEmail(email);
  const [plan, expires, source] = await Promise.all([
    kv.get(`user:plan:${e}`),
    kv.get(`user:plan_expires:${e}`),
    kv.get(`user:plan_source:${e}`),
  ]);
  const rec = {
    plan: plan || 'free',
    expires: expires ? String(expires).slice(0, 10) : null,
    // Les plans posés avant l'existence de plan_source viennent tous de HelloAsso.
    source: source || (plan && SUBSCRIBER_PLANS.has(plan) ? 'helloasso' : null),
  };
  rec.active = isActive(rec);
  return rec;
}

// Pose (ou prolonge) un plan payant. Renvoie ce qui a été décidé, pour le journal.
export async function applyPaidPlan({ email, plan, expiresAt = null, source }, kv = defaultKv) {
  const e = normalizeEmail(email);
  if (!e.includes('@')) throw new Error('applyPaidPlan: email requis');
  if (!SUBSCRIBER_PLANS.has(plan)) throw new Error(`applyPaidPlan: plan inconnu « ${plan} »`);
  if (!PLAN_SOURCES.has(source)) throw new Error(`applyPaidPlan: source inconnue « ${source} »`);
  const wanted = { plan, expires: plan === 'lifetime' ? null : (expiresAt ? String(expiresAt).slice(0, 10) : null) };

  const current = await readPlan(e, kv);
  let decision;

  if (current.active && current.plan === 'lifetime') {
    decision = { applied: false, kept: current, reason: 'lifetime_actif' };
  } else if (current.active && current.source !== source && rank(current.plan) > rank(plan)) {
    decision = { applied: false, kept: current, reason: 'plan_superieur_autre_canal' };
  } else {
    let expires = wanted.expires;
    if (current.active && current.plan === plan) expires = laterExpiry(current.expires, wanted.expires);
    const ops = [
      kv.set(`user:plan:${e}`, plan),
      kv.set(`user:plan_source:${e}`, source),
      expires ? kv.set(`user:plan_expires:${e}`, expires) : kv.del(`user:plan_expires:${e}`),
      kv.sadd('users:known', e),
    ];
    await Promise.all(ops);
    decision = { applied: true, plan, expires, source, previous: current };
  }
  return decision;
}

// Retire le plan posé par `source` (expiration, remboursement). Ne touche jamais au
// plan d'un autre canal : un abonnement Apple qui expire ne doit pas éteindre un don
// HelloAsso toujours valide.
export async function revokePlan({ email, source }, kv = defaultKv) {
  const e = normalizeEmail(email);
  if (!e.includes('@')) throw new Error('revokePlan: email requis');
  const current = await readPlan(e, kv);
  if (!SUBSCRIBER_PLANS.has(current.plan)) return { revoked: false, reason: 'aucun_plan_payant', current };
  if (current.source !== source) return { revoked: false, reason: 'plan_d_un_autre_canal', current };
  await Promise.all([
    kv.set(`user:plan:${e}`, 'free'),
    kv.del(`user:plan_expires:${e}`),
    kv.del(`user:plan_source:${e}`),
  ]);
  return { revoked: true, previous: current };
}
