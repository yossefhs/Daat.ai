// /api/helloasso-webhook — Auto-upgrade de plan après paiement HelloAsso.
//
// URL à configurer dans le dashboard HelloAsso :
//   https://daatai.vercel.app/api/helloasso-webhook?secret=XXX
//   (XXX = HELLOASSO_WEBHOOK_SECRET côté Vercel)
//
// Mapping des formulaires HelloAsso → plans DAAT, via variables d'environnement :
//   HELLOASSO_FORM_KHAVROUTHA   = identifiant ou slug du formulaire Khavroutha (8 €/mois)
//   HELLOASSO_FORM_BEIT_MIDRASH = identifiant ou slug du formulaire Beit Midrash (25 €/mois)
//   HELLOASSO_FORM_LIFETIME     = identifiant ou slug du formulaire Lifetime (500 € unique)
//
// Si aucun match par formulaire, on retombe sur un mapping par montant (failsafe).
//
// Sécurité : la requête doit passer ?secret=XXX qui matche HELLOASSO_WEBHOOK_SECRET.
// HelloAsso v5 ne signe pas en HMAC ; le secret query string est leur recommandation.

import { kv } from './_kv.js';

const SUBSCRIBER_PLANS = new Set(['khavroutha', 'beit_midrash', 'beit_midrash_plus', 'yeshiva', 'lifetime', 'premium']);

// Mapping forme → plan (lu au runtime pour permettre la maj env sans redéploiement)
function getFormMap() {
  return {
    [process.env.HELLOASSO_FORM_KHAVROUTHA || '__unset_khavroutha__']:   { plan: 'khavroutha',   recurring: true  },
    [process.env.HELLOASSO_FORM_BEIT_MIDRASH || '__unset_beit_midrash__']:{ plan: 'beit_midrash', recurring: true  },
    [process.env.HELLOASSO_FORM_LIFETIME || '__unset_lifetime__']:       { plan: 'lifetime',     recurring: false },
  };
}

// Failsafe : si le formulaire n'est pas mappé, on déduit du montant en centimes.
// Aligné sur les prix HelloAsso de l'Option A.
function planFromAmount(amountCents, isRecurring) {
  if (isRecurring) {
    if (amountCents >= 10000) return 'yeshiva';
    if (amountCents >= 5000)  return 'beit_midrash_plus';
    if (amountCents >= 2500)  return 'beit_midrash';      // 25 €/mois HelloAsso ou 36 €/mois Qonto
    if (amountCents >= 700)   return 'khavroutha';        // 8 €/mois HelloAsso ou 18 €/mois Qonto
    return null;
  }
  if (amountCents >= 50000) return 'lifetime';            // 500 € unique
  return null;
}

// Durée de validité d'un abonnement mensuel (35 jours = mois + marge).
// Le webhook du mois suivant prolongera la date.
const MONTHLY_GRACE_DAYS = 35;

export default async function handler(req, res) {
  // CORS : webhooks viennent du back HelloAsso, pas du navigateur, donc OPTIONS rare.
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST only' });
  }

  // ── Sécurité : secret partagé via query string ─────────────────────────────
  const expectedSecret = process.env.HELLOASSO_WEBHOOK_SECRET;
  if (!expectedSecret) {
    console.error('[helloasso-webhook] HELLOASSO_WEBHOOK_SECRET not configured in env');
    return res.status(503).json({ error: 'Webhook not configured' });
  }
  const providedSecret = req.query?.secret || req.headers['x-helloasso-secret'];
  if (providedSecret !== expectedSecret) {
    console.warn('[helloasso-webhook] invalid secret from', req.headers['x-forwarded-for'] || 'unknown');
    return res.status(401).json({ error: 'Invalid secret' });
  }

  // ── Parsing payload HelloAsso v5 ───────────────────────────────────────────
  const body = req.body || {};
  const eventType = body.eventType || body.event || '';
  const data = body.data || body;

  // Log toujours, même si on ignore — permet de débugger sans rejouer un paiement
  console.log('[helloasso-webhook] eventType=', eventType, 'data=', JSON.stringify(data).slice(0, 800));

  // On ne traite que les paiements validés (Order créé/payé, ou Payment confirmé)
  // HelloAsso envoie "Order" pour adhésion/don validé, "Payment" pour échéance récurrente
  const acceptedEvents = ['Order', 'Payment', 'Form'];
  if (eventType && !acceptedEvents.includes(eventType)) {
    return res.status(200).json({ ok: true, ignored: true, eventType });
  }

  // Extraction email payeur (plusieurs chemins possibles selon le type d'event)
  const email = String(
    data?.payer?.email ||
    data?.user?.email ||
    data?.email ||
    data?.order?.payer?.email ||
    ''
  ).toLowerCase().trim();

  if (!email || !email.includes('@')) {
    console.warn('[helloasso-webhook] no valid payer email in payload');
    return res.status(200).json({ ok: true, warning: 'no_email', eventType });
  }

  // Identifier le formulaire (slug ou id, selon ce que HelloAsso renvoie)
  // On combine plusieurs champs possibles en une string pour matcher facilement.
  const formIdentifier = [
    data?.formSlug,
    data?.form?.formSlug,
    data?.formId,
    data?.form?.id,
    data?.formName,
    data?.form?.name,
  ].filter(Boolean).map(String).join('|').toLowerCase();

  const amountCents = parseInt(data?.amount?.total || data?.amount || data?.totalAmount || 0, 10);

  // formType ou frequency peuvent indiquer un récurrent
  const formType = String(data?.formType || data?.form?.formType || '').toLowerCase();
  const frequency = String(data?.frequency || data?.recurrence || '').toLowerCase();
  const isRecurring = formType.includes('membership') || formType.includes('adhesion') ||
                      frequency.includes('monthly') || frequency.includes('mensuel') ||
                      eventType === 'Payment'; // les Payment events sont des échéances récurrentes

  // ── 1. Tenter le mapping par formulaire ──
  const formMap = getFormMap();
  let plan = null;
  let recurring = isRecurring;
  for (const [key, val] of Object.entries(formMap)) {
    if (!key || key.startsWith('__unset_')) continue;
    if (formIdentifier.includes(key.toLowerCase())) {
      plan = val.plan;
      recurring = val.recurring;
      break;
    }
  }

  // ── 2. Failsafe : déduire du montant ──
  if (!plan) {
    plan = planFromAmount(amountCents, isRecurring);
  }

  if (!plan) {
    console.warn('[helloasso-webhook] cannot map to plan:', { formIdentifier, amountCents, isRecurring });
    // Log quand même pour audit — un humain pourra investiguer dans l'admin
    await kv.lpush('logs:helloasso-unmatched', JSON.stringify({
      ts: new Date().toISOString(),
      email, eventType, formIdentifier, amountCents, isRecurring,
    }));
    await kv.ltrim('logs:helloasso-unmatched', 0, 99);
    return res.status(200).json({ ok: true, warning: 'no_plan_match', email, amount: amountCents });
  }

  // ── 3. Date d'expiration ──
  // Mensuel récurrent → 35j (le prochain Payment event prolongera)
  // Lifetime / one-time → pas d'expiration
  let expiresAt = null;
  if (recurring && plan !== 'lifetime') {
    const exp = new Date(Date.now() + MONTHLY_GRACE_DAYS * 24 * 60 * 60 * 1000);
    expiresAt = exp.toISOString().slice(0, 10);
  }

  // ── 4. Application de l'upgrade en KV ──
  const ops = [
    kv.set(`user:plan:${email}`, plan),
    kv.lpush('logs:helloasso', JSON.stringify({
      ts: new Date().toISOString(),
      email, plan, recurring,
      amount_eur: amountCents / 100,
      formIdentifier, eventType,
      orderId: data?.id || data?.orderId || null,
    })),
    kv.ltrim('logs:helloasso', 0, 199),
    kv.sadd('users:known', email), // au cas où c'est un nouveau compte payeur
  ];
  if (expiresAt) {
    ops.push(kv.set(`user:plan_expires:${email}`, expiresAt));
  } else {
    ops.push(kv.del(`user:plan_expires:${email}`));
  }
  await Promise.all(ops);

  console.log(`[helloasso-webhook] UPGRADED ${email} → ${plan}${expiresAt ? ' (expires ' + expiresAt + ')' : ' (lifetime)'} via ${eventType}`);

  return res.status(200).json({
    ok: true,
    upgraded: true,
    email,
    plan,
    expires: expiresAt,
    amount_eur: amountCents / 100,
  });
}
