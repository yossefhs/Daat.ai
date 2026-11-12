// Module partagé des plans payants — une seule porte d'écriture, quel que soit le canal.
//
// Trois canaux peuvent poser un plan sur un compte : HelloAsso (site), les magasins
// d'applications (Apple App Store, Google Play — via api/iap-webhook.js) et l'admin.
// Un même compte peut tenir plusieurs droits à la fois (un don HelloAsso ET un abonnement
// Apple). On garde donc UN DROIT PAR CANAL, et l'on recalcule à chaque écriture le droit
// effectif que lit api/chat.js (identifyUser) :
//
//   user:plan_channels:{email} → { helloasso: {plan, expires}, apple: {…}, google: {…}, manual: {…} }
//   user:plan:{email}          → plan effectif (le meilleur droit actif)
//   user:plan_expires:{email}  → 'YYYY-MM-DD' de ce droit (absent pour lifetime) ; chat.js
//                                rétrograde en 'free' dès que la date est dépassée
//   user:plan_source:{email}   → canal du droit effectif
//
// Règles :
//   - le droit effectif est le meilleur droit ACTIF : rang le plus élevé, puis échéance la
//     plus lointaine (sans échéance = la plus lointaine) ;
//   - un renouvellement n'avance jamais l'échéance d'un même plan sur un même canal ;
//   - une révocation (expiration côté magasin) ne retire que le droit DE CE CANAL : si un
//     autre canal tient encore un droit actif, il devient effectif, sans perte ;
//   - les clés effectives écrites directement (ancien webhook HelloAsso, admin) font foi
//     pour le canal qu'indique plan_source ('helloasso' pour les plans antérieurs à ce
//     module) : elles sont relues et réintégrées à chaque passage.
//
// Les fonctions acceptent un client `kv` injectable pour les tests ; par défaut elles
// utilisent le client Redis partagé.

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

const K = {
  plan: (e) => `user:plan:${e}`,
  expires: (e) => `user:plan_expires:${e}`,
  source: (e) => `user:plan_source:${e}`,
  channels: (e) => `user:plan_channels:${e}`,
};

// Toutes les clés de plan d'un compte — pour la suppression de compte.
export function planKeys(email) {
  const e = normalizeEmail(email);
  return [K.plan(e), K.expires(e), K.source(e), K.channels(e)];
}

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

function normDate(d) {
  return d ? String(d).slice(0, 10) : null;
}

export function isActive({ plan, expires }, today = todayISO()) {
  if (!plan || !SUBSCRIBER_PLANS.has(plan)) return false;
  if (plan === 'lifetime' || !expires) return true;
  return today <= normDate(expires);
}

// Entre deux droits actifs, le meilleur : rang, puis échéance la plus lointaine.
function better(a, b) {
  if (!b) return a;
  if (!a) return b;
  const ra = rank(a.plan), rb = rank(b.plan);
  if (ra !== rb) return ra > rb ? a : b;
  if (!a.expires) return a;
  if (!b.expires) return b;
  return a.expires >= b.expires ? a : b;
}

// Le droit effectif d'un jeu de canaux : { plan, expires, source } ou null.
export function effectiveOf(channels, today = todayISO()) {
  let best = null;
  for (const [source, ent] of Object.entries(channels || {})) {
    if (!ent || !isActive(ent, today)) continue;
    best = better({ plan: ent.plan, expires: normDate(ent.expires), source }, best);
  }
  return best;
}

// Les clés effectives, telles que les lit chat.js.
export async function readPlan(email, kv = defaultKv) {
  const e = normalizeEmail(email);
  const [plan, expires, source] = await Promise.all([
    kv.get(K.plan(e)),
    kv.get(K.expires(e)),
    kv.get(K.source(e)),
  ]);
  const rec = {
    plan: plan || 'free',
    expires: normDate(expires),
    source: source || (plan && SUBSCRIBER_PLANS.has(plan) ? 'helloasso' : null),
  };
  rec.active = isActive(rec);
  return rec;
}

// Les droits par canal, réconciliés avec les clés effectives (qui font foi pour le canal
// qu'indique plan_source — c'est ainsi que les écritures directes sont réintégrées).
export async function readChannels(email, kv = defaultKv) {
  const e = normalizeEmail(email);
  const [raw, plan, expires, source] = await Promise.all([
    kv.get(K.channels(e)),
    kv.get(K.plan(e)),
    kv.get(K.expires(e)),
    kv.get(K.source(e)),
  ]);
  let channels = {};
  if (raw && typeof raw === 'object' && !Array.isArray(raw)) channels = { ...raw };
  else if (typeof raw === 'string') {
    try { channels = JSON.parse(raw) || {}; } catch { channels = {}; }
  }
  if (plan && SUBSCRIBER_PLANS.has(plan)) {
    const src = PLAN_SOURCES.has(source) ? source : 'helloasso';
    channels[src] = { plan, expires: normDate(expires) };
  }
  for (const [s, ent] of Object.entries(channels)) {
    if (!PLAN_SOURCES.has(s) || !ent || !SUBSCRIBER_PLANS.has(ent.plan)) delete channels[s];
  }
  return { channels, effective: effectiveOf(channels) };
}

// Écrit le jeu de canaux (droits actifs seulement) et les clés effectives qui en découlent.
async function writeEffective(e, channels, kv) {
  const today = todayISO();
  const kept = {};
  for (const [s, ent] of Object.entries(channels)) {
    if (ent && isActive(ent, today)) kept[s] = { plan: ent.plan, expires: normDate(ent.expires) };
  }
  const eff = effectiveOf(kept, today);
  const ops = [Object.keys(kept).length ? kv.set(K.channels(e), kept) : kv.del(K.channels(e))];
  if (eff) {
    ops.push(
      kv.set(K.plan(e), eff.plan),
      kv.set(K.source(e), eff.source),
      eff.expires ? kv.set(K.expires(e), eff.expires) : kv.del(K.expires(e)),
      kv.sadd('users:known', e),
    );
  } else {
    ops.push(kv.set(K.plan(e), 'free'), kv.del(K.expires(e)), kv.del(K.source(e)));
  }
  await Promise.all(ops);
  return eff;
}

// Pose (ou prolonge) le droit d'un canal, puis recalcule le droit effectif.
// Renvoie { applied, channel, effective, governs, previous } :
//   governs = le droit de CE canal est celui que l'utilisateur voit (sinon un autre canal
//   tient un droit meilleur — le sien est enregistré et prendra le relais le moment venu).
export async function applyPaidPlan({ email, plan, expiresAt = null, source }, kv = defaultKv) {
  const e = normalizeEmail(email);
  if (!e.includes('@')) throw new Error('applyPaidPlan: email requis');
  if (!SUBSCRIBER_PLANS.has(plan)) throw new Error(`applyPaidPlan: plan inconnu « ${plan} »`);
  if (!PLAN_SOURCES.has(source)) throw new Error(`applyPaidPlan: source inconnue « ${source} »`);

  const { channels, effective: previous } = await readChannels(e, kv);
  const prev = channels[source];
  let expires = plan === 'lifetime' ? null : normDate(expiresAt);
  if (prev && prev.plan === plan) expires = laterExpiry(prev.expires, expires);
  channels[source] = { plan, expires };

  const effective = await writeEffective(e, channels, kv);
  return {
    applied: true,
    channel: { plan, expires, source },
    effective,
    governs: Boolean(effective && effective.source === source),
    previous,
  };
}

// Retire le droit posé par `source` (expiration, remboursement), puis recalcule : si un
// autre canal tient encore un droit actif, il devient effectif — rien n'est perdu.
export async function revokePlan({ email, source }, kv = defaultKv) {
  const e = normalizeEmail(email);
  if (!e.includes('@')) throw new Error('revokePlan: email requis');
  if (!PLAN_SOURCES.has(source)) throw new Error(`revokePlan: source inconnue « ${source} »`);

  const { channels, effective: previous } = await readChannels(e, kv);
  if (!channels[source]) {
    return { revoked: false, reason: 'aucun_droit_de_ce_canal', effective: previous, previous };
  }
  delete channels[source];
  const effective = await writeEffective(e, channels, kv);
  return { revoked: true, effective, previous };
}
