// /api/iap-webhook — Achats dans l'application mobile (App Store, Google Play).
//
// L'application vend ses formules par l'achat intégré des magasins ; RevenueCat
// vérifie les reçus auprès d'Apple et de Google et nous notifie ici chaque
// événement d'abonnement. Ce handler ne fait qu'une chose : traduire l'événement
// en plan DAAT et l'écrire par la porte commune (api/_plans.js), les mêmes clés
// que lit api/chat.js. Aucune donnée bancaire ne transite.
//
// Configuration (Vercel) :
//   REVENUECAT_WEBHOOK_SECRET  valeur de l'entête Authorization que RevenueCat
//                              enverra (à coller dans son tableau de bord) ; sans
//                              elle, le webhook refuse tout.
//   IAP_PRODUCTS               JSON { "identifiant_produit": "plan", … } ; sinon le
//                              plan est déduit du nom du produit (khavroutha,
//                              beit_midrash, beit_midrash_plus, yeshiva, lifetime).
//   IAP_GRACE_DAYS             jours ajoutés à l'échéance (défaut 3 : absorbe les
//                              relances de facturation avant l'EXPIRATION).
//   IAP_ALLOW_SANDBOX          '1' pour appliquer aussi les achats de test (SANDBOX) ;
//                              sinon ils sont journalisés sans toucher aux plans.
//
// Côté application : après la connexion par code e-mail, l'app appelle
// Purchases.logIn(<email>) — ou pose l'attribut $email — pour que l'événement
// porte l'adresse du compte DAAT. C'est elle qui relie l'achat au plan.
//
// Événements RevenueCat et décision :
//   INITIAL_PURCHASE, RENEWAL, UNCANCELLATION, NON_RENEWING_PURCHASE → poser/prolonger
//   PRODUCT_CHANGE   → journal seul (le changement prend effet au RENEWAL suivant)
//   CANCELLATION     → journal seul (l'accès court jusqu'à l'échéance)
//   EXPIRATION       → révoquer, uniquement si le plan vient de ce magasin
//   BILLING_ISSUE, SUBSCRIPTION_PAUSED, TRANSFER, TEST, autres → journal seul
//
// Réponse : 200 dès que l'événement est authentifié et traité, même sans effet
// (RevenueCat rejoue tout ce qui n'est pas 2xx). 401 si le secret ne correspond pas.

import crypto from 'node:crypto';
import { kv } from './_kv.js';
import { applyPaidPlan, revokePlan, msToISODate, normalizeEmail, SUBSCRIBER_PLANS } from './_plans.js';

const APPLY_EVENTS = new Set(['INITIAL_PURCHASE', 'RENEWAL', 'UNCANCELLATION', 'NON_RENEWING_PURCHASE']);
const REVOKE_EVENTS = new Set(['EXPIRATION']);
const LOG_ONLY_EVENTS = new Set(['PRODUCT_CHANGE', 'CANCELLATION', 'BILLING_ISSUE', 'SUBSCRIPTION_PAUSED', 'TRANSFER', 'TEST', 'TEMPORARY_ENTITLEMENT_GRANT', 'SUBSCRIBER_ALIAS', 'INVOICE_ISSUANCE', 'REFUND_REVERSED']);

const LOG_KEY = 'logs:iap';
const LOG_UNMATCHED_KEY = 'logs:iap-unmatched';
const DEDUP_TTL_S = 30 * 24 * 60 * 60;
const MAP_TTL_S = 400 * 24 * 60 * 60;
const DEFAULT_GRACE_DAYS = 3;
const PREPAID_FALLBACK_DAYS = 35;

function safeEqual(a, b) {
  const x = Buffer.from(String(a || ''));
  const y = Buffer.from(String(b || ''));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

function isAuthorized(req) {
  const secret = process.env.REVENUECAT_WEBHOOK_SECRET;
  if (!secret) return { ok: false, status: 503, error: 'REVENUECAT_WEBHOOK_SECRET non configuré' };
  const h = String(req.headers?.authorization || '');
  const bare = h.replace(/^\s*Bearer\s+/i, '').trim();
  if (safeEqual(h.trim(), secret) || safeEqual(bare, secret)) return { ok: true };
  return { ok: false, status: 401, error: 'Non autorisé' };
}

export function storeOf(event) {
  const s = String(event?.store || '').toUpperCase();
  if (s === 'APP_STORE' || s === 'MAC_APP_STORE') return 'apple';
  if (s === 'PLAY_STORE') return 'google';
  return null;
}

function looksLikeEmail(s) {
  return typeof s === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.trim()) && s.length <= 254;
}

// L'adresse du compte DAAT : attribut $email, sinon un app_user_id qui est une
// adresse, sinon un alias ; en dernier recours la correspondance mémorisée lors
// d'un événement précédent (iap:map:{app_user_id}).
export async function resolveEmail(event, store = kv) {
  const attr = event?.subscriber_attributes?.$email?.value;
  if (looksLikeEmail(attr)) return normalizeEmail(attr);
  const candidates = [event?.app_user_id, event?.original_app_user_id, ...(Array.isArray(event?.aliases) ? event.aliases : [])];
  for (const c of candidates) if (looksLikeEmail(c)) return normalizeEmail(c);
  for (const c of candidates) {
    if (typeof c !== 'string' || !c) continue;
    const mapped = await store.get(`iap:map:${c}`);
    if (looksLikeEmail(mapped)) return normalizeEmail(mapped);
  }
  return null;
}

function productMap() {
  try {
    const raw = process.env.IAP_PRODUCTS;
    if (!raw) return {};
    const obj = JSON.parse(raw);
    return obj && typeof obj === 'object' ? obj : {};
  } catch {
    console.warn('[iap-webhook] IAP_PRODUCTS illisible (JSON attendu) — repli sur le nom du produit');
    return {};
  }
}

// Produit (ou entitlement) → plan DAAT.
export function planForEvent(event, map = productMap()) {
  const productId = String(event?.product_id || '');
  if (productId && SUBSCRIBER_PLANS.has(map[productId])) return map[productId];
  const ents = Array.isArray(event?.entitlement_ids) ? event.entitlement_ids : (event?.entitlement_id ? [event.entitlement_id] : []);
  for (const e of ents) {
    if (SUBSCRIBER_PLANS.has(e)) return e;
    if (SUBSCRIBER_PLANS.has(map[e])) return map[e];
  }
  const s = productId.toLowerCase().replace(/[^a-z]+/g, '_');
  for (const name of ['beit_midrash_plus', 'beit_midrash', 'khavroutha', 'yeshiva', 'lifetime']) {
    if (s.includes(name)) return name;
  }
  return null;
}

function graceDays() {
  const n = parseInt(process.env.IAP_GRACE_DAYS ?? '', 10);
  return Number.isFinite(n) && n >= 0 ? n : DEFAULT_GRACE_DAYS;
}

// Échéance à écrire : la date d'expiration du magasin + grâce ; un achat non
// renouvelable sans date (lifetime) n'expire pas ; un prépayé sans date reçoit 35 j.
export function expiryForEvent(event, plan, grace = graceDays()) {
  if (plan === 'lifetime') return null;
  const fromStore = msToISODate(event?.expiration_at_ms, grace);
  if (fromStore) return fromStore;
  if (String(event?.type) === 'NON_RENEWING_PURCHASE') {
    return new Date(Date.now() + PREPAID_FALLBACK_DAYS * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  }
  return null;
}

async function journal(store, entry, key = LOG_KEY) {
  try {
    await store.lpush(key, JSON.stringify({ ts: new Date().toISOString(), ...entry }));
    await store.ltrim(key, 0, 499);
  } catch (err) {
    console.error('[iap-webhook] journal KV error:', err?.message || err);
  }
}

function mask(email) {
  return String(email || '').replace(/^(.).*?(@.*)$/, '$1***$2');
}

// `deps` permet d'injecter un KV en mémoire et des fonctions de plan factices dans
// les tests ; en production tout vient des modules partagés.
export async function handleWebhook(req, res, deps = {}) {
  const store = deps.kv || kv;
  const apply = deps.applyPaidPlan || ((args) => applyPaidPlan(args, store));
  const revoke = deps.revokePlan || ((args) => revokePlan(args, store));

  if (req.method === 'GET') {
    return res.status(200).json({ ok: true, configured: Boolean(process.env.REVENUECAT_WEBHOOK_SECRET) });
  }
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  const auth = isAuthorized(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { return res.status(400).json({ error: 'JSON invalide' }); }
  }
  const event = body?.event;
  if (!event || typeof event !== 'object') return res.status(400).json({ error: 'Corps attendu : { event: {…} }' });

  const type = String(event.type || 'UNKNOWN').toUpperCase();
  const eventId = String(event.id || '').trim();
  const canal = storeOf(event);
  const environment = String(event.environment || 'PRODUCTION').toUpperCase();
  const sandbox = environment === 'SANDBOX';
  const sandboxApplies = process.env.IAP_ALLOW_SANDBOX === '1';

  // Anti-rejeu : RevenueCat renvoie le même événement tant qu'il n'a pas reçu 2xx. Le
  // marqueur est posé AVANT le traitement, et libéré si le traitement échoue (y compris
  // la résolution de l'adresse) : un incident passager ne doit jamais faire passer un
  // achat réel pour un doublon déjà servi.
  let marked = false;
  if (eventId) {
    try {
      const fresh = await store.set(`iap:event:${eventId}`, 1, { nx: true, ex: DEDUP_TTL_S });
      if (fresh === null) return res.status(200).json({ ok: true, duplicate: true, id: eventId });
      marked = true;
    } catch (err) {
      console.error('[iap-webhook] dedup KV error (continue):', err?.message || err);
    }
  }
  const release = async () => {
    if (marked) await Promise.resolve(store.del(`iap:event:${eventId}`)).catch(() => null);
  };

  const plan = planForEvent(event);
  const base = {
    id: eventId || null, type, store: event.store || null, environment,
    app_user_id: event.app_user_id || null, product_id: event.product_id || null,
    period_type: event.period_type || null,
  };

  try {
    const email = await resolveEmail(event, store);
    base.email = email;

    if (!email) {
      await journal(store, { ...base, outcome: 'sans_email' }, LOG_UNMATCHED_KEY);
      console.warn(`[iap-webhook] ${type} sans adresse de compte (app_user_id=${event.app_user_id || '?'})`);
      return res.status(200).json({ ok: true, applied: false, reason: 'no_email' });
    }

    // Mémorise la correspondance identifiant RevenueCat → adresse, pour les événements
    // suivants qui n'auraient que l'identifiant (EXPIRATION d'un abonné déconnecté).
    const ids = [event.app_user_id, event.original_app_user_id, ...(Array.isArray(event.aliases) ? event.aliases : [])]
      .filter((v) => typeof v === 'string' && v && !looksLikeEmail(v));
    await Promise.all(ids.map((id) => Promise.resolve(store.set(`iap:map:${id}`, email, { ex: MAP_TTL_S })).catch(() => null)));

    if (sandbox && !sandboxApplies) {
      await journal(store, { ...base, plan, outcome: 'sandbox_ignore' });
      return res.status(200).json({ ok: true, applied: false, reason: 'sandbox' });
    }

    if (!canal && (APPLY_EVENTS.has(type) || REVOKE_EVENTS.has(type))) {
      await journal(store, { ...base, plan, outcome: 'magasin_inconnu' }, LOG_UNMATCHED_KEY);
      return res.status(200).json({ ok: true, applied: false, reason: 'unknown_store' });
    }

    let result = { applied: false };
    if (APPLY_EVENTS.has(type)) {
      if (!plan) {
        await journal(store, { ...base, outcome: 'produit_inconnu' }, LOG_UNMATCHED_KEY);
        console.warn(`[iap-webhook] produit sans plan : ${event.product_id}`);
        return res.status(200).json({ ok: true, applied: false, reason: 'unknown_product' });
      }
      const expiresAt = expiryForEvent(event, plan);
      const decision = await apply({ email, plan, expiresAt, source: canal });
      await store.set(`iap:user:${email}`, {
        store: canal, app_user_id: event.app_user_id || null, product_id: event.product_id || null,
        plan, expires: decision.channel?.expires ?? expiresAt, governs: decision.governs,
        lastEvent: type, lastEventId: eventId || null, updatedAt: new Date().toISOString(),
      });
      result = { applied: true, governs: decision.governs, plan, expires: decision.channel?.expires ?? expiresAt, effective: decision.effective };
      await journal(store, { ...base, plan, expires: result.expires, outcome: decision.governs ? 'applique' : 'enregistre:autre_canal_meilleur', effective: decision.effective });
      console.log(`[iap-webhook] ✓ ${type} ${mask(email)} ${canal} plan=${plan}${result.expires ? ' exp=' + result.expires : ''} → ${decision.governs ? 'effectif' : 'enregistré (' + (decision.effective?.source || '?') + ' reste effectif)'}`);
    } else if (REVOKE_EVENTS.has(type)) {
      const decision = await revoke({ email, source: canal });
      result = { applied: decision.revoked, revoked: decision.revoked, reason: decision.reason || null, effective: decision.effective };
      await journal(store, { ...base, plan, expiration_reason: event.expiration_reason || null, outcome: decision.revoked ? 'revoque' : `conserve:${decision.reason}`, effective: decision.effective });
      console.log(`[iap-webhook] ${type} ${mask(email)} ${canal} → ${decision.revoked ? 'droit retiré' : 'rien à retirer (' + decision.reason + ')'}${decision.effective ? ', reste ' + decision.effective.source + ':' + decision.effective.plan : ', plus de droit actif'}`);
    } else {
      await journal(store, { ...base, plan, cancel_reason: event.cancel_reason || null, new_product_id: event.new_product_id || null, outcome: LOG_ONLY_EVENTS.has(type) ? 'journal' : 'type_inconnu' });
      result = { applied: false, reason: 'log_only' };
    }

    return res.status(200).json({ ok: true, type, email, ...result });
  } catch (err) {
    console.error('[iap-webhook] erreur de traitement:', err?.message || err);
    await journal(store, { ...base, plan, outcome: 'erreur', error: String(err?.message || err) }, LOG_UNMATCHED_KEY);
    // 500 → RevenueCat rejouera ; le marqueur anti-rejeu est libéré pour que ce rejeu compte.
    await release();
    return res.status(500).json({ error: 'Erreur de traitement' });
  }
}

export default function handler(req, res) {
  return handleWebhook(req, res);
}
