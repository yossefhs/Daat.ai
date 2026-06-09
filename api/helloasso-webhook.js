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
import crypto from 'node:crypto';
import { getRedis, K_ORDERS, makeDedicace, saveDedicace } from './_dedicaces.js';

// Comparaison à temps constant — évite les attaques temporelles sur le secret.
function safeEqual(a, b) {
  const x = Buffer.from(String(a || ''));
  const y = Buffer.from(String(b || ''));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

// Cherche une réponse de champ personnalisé HelloAsso par nom (fuzzy).
// HelloAsso renvoie les customFields sous forme [{ name, answer }, ...],
// au niveau de l'order et/ou de chaque item.
function collectCustomFields(data) {
  const fields = [];
  const push = (arr) => {
    if (Array.isArray(arr)) for (const f of arr) if (f) fields.push(f);
  };
  push(data?.customFields);
  push(data?.order?.customFields);
  if (Array.isArray(data?.items)) for (const it of data.items) push(it?.customFields);
  return fields;
}

function findField(fields, regex) {
  for (const f of fields) {
    const name = String(f?.name || f?.label || '').toLowerCase();
    if (regex.test(name)) {
      const v = f?.answer ?? f?.value ?? f?.values;
      if (v != null && String(v).trim()) return String(Array.isArray(v) ? v.join(' ') : v).trim();
    }
  }
  return '';
}

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
  if (!safeEqual(providedSecret, expectedSecret)) {
    console.warn('[helloasso-webhook] invalid secret from', req.headers['x-forwarded-for'] || 'unknown');
    return res.status(401).json({ error: 'Invalid secret' });
  }

  // ── Parsing payload HelloAsso v5 ───────────────────────────────────────────
  const body = req.body || {};
  const eventType = body.eventType || body.event || '';
  const data = body.data || body;

  // Log non-PII : eventType + metadata du formulaire/montant uniquement.
  // L'email et autres données personnelles ne sont JAMAIS écrits dans les logs Vercel ;
  // l'audit trail complet (email, plan, montant) est stocké dans KV `logs:helloasso`
  // accessible via l'admin pour les opérations légitimes.
  const safeMeta = {
    formSlug: data?.formSlug || data?.form?.formSlug,
    formType: data?.formType || data?.form?.formType,
    amount: data?.amount?.total || data?.amount || data?.totalAmount,
    orderId: data?.id || data?.orderId,
  };
  console.log('[helloasso-webhook] eventType=', eventType, 'meta=', JSON.stringify(safeMeta));

  // On ne traite que les paiements validés (Order créé/payé, ou Payment confirmé)
  // HelloAsso envoie "Order" pour adhésion/don validé, "Payment" pour échéance récurrente
  const acceptedEvents = ['Order', 'Payment', 'Form'];
  if (eventType && !acceptedEvents.includes(eventType)) {
    return res.status(200).json({ ok: true, ignored: true, eventType });
  }

  // ── Branche DÉDICACE ────────────────────────────────────────────────────────
  // Si le formulaire est un formulaire de dédicace (formSlug contient « dedicace »),
  // on lit les champs personnalisés (Nom hébreu, Type, Siman concerné) et on
  // enregistre la/les dédicace(s). Ces formulaires sont des dons ponctuels : on
  // ne déclenche pas d'upgrade de plan.
  const formSlugRaw = String(
    data?.formSlug || data?.form?.formSlug || data?.formName || data?.form?.name || '',
  ).toLowerCase();
  if (formSlugRaw.includes('dedicace') || formSlugRaw.includes('dédicace') || formSlugRaw.includes('dedication')) {
    // Anti-doublon : un order id ne doit être traité qu'une seule fois.
    const orderId = String(data?.id || data?.orderId || data?.order?.id || '').trim();
    if (orderId) {
      let redis;
      try {
        redis = getRedis();
        const isNew = await redis.sadd(K_ORDERS, orderId);
        if (isNew === 0) {
          return res.status(200).json({ ok: true, dedicace: true, duplicate: true, orderId });
        }
      } catch (err) {
        console.error('[helloasso-webhook] dedicace KV error:', err?.message || err);
        return res.status(500).json({ error: 'KV error' });
      }

      const fields = collectCustomFields(data);
      const nom = findField(fields, /nom|name|h[ée]breu|hebrew|שם|niftar|d[ée]di/);
      const type = findField(fields, /type|cat[ée]gorie|category|nature|כוונה|לעילוי|רפואה|הצלחה/);
      const simanRaw = findField(fields, /siman|simane|chapitre|chapter|סימן|page/);
      const siman = (String(simanRaw).match(/\d+/) || [])[0] || null;

      if (!nom) {
        console.warn('[helloasso-webhook] dedicace sans nom, orderId=', orderId);
        return res.status(200).json({ ok: true, dedicace: true, warning: 'no_name', orderId });
      }

      const dedic = makeDedicace({ siman, nom, type, source: 'helloasso', orderId });
      await saveDedicace(redis, dedic);
      console.log(`[helloasso-webhook] DEDICACE enregistrée siman=${dedic.siman} type=${dedic.type} order=${orderId}`);
      return res.status(200).json({ ok: true, dedicace: true, saved: dedic });
    }
    // Pas d'order id exploitable : on log et on s'arrête (pas d'anti-doublon possible).
    console.warn('[helloasso-webhook] dedicace sans orderId exploitable');
    return res.status(200).json({ ok: true, dedicace: true, warning: 'no_order_id' });
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

  // ── 3bis. Anti-rejeu : un même paiement ne doit upgrader qu'une fois ──
  // HelloAsso peut renvoyer le même event (retries). On réutilise le set K_ORDERS
  // (déjà utilisé par la branche dédicace) pour garantir l'idempotence. Les
  // échéances récurrentes ont un orderId distinct chaque mois → renouvellements
  // non bloqués ; seul un VRAI doublon (même id rejoué) est ignoré.
  const upgradeOrderId = String(data?.id || data?.orderId || data?.order?.id || '').trim();
  if (upgradeOrderId) {
    try {
      const isNew = await getRedis().sadd(K_ORDERS, upgradeOrderId);
      if (isNew === 0) {
        console.log('[helloasso-webhook] duplicate plan event ignored, orderId=', upgradeOrderId);
        return res.status(200).json({ ok: true, duplicate: true, orderId: upgradeOrderId });
      }
    } catch (err) {
      // Fail-open : mieux vaut un éventuel double upgrade qu'un vrai paiement bloqué.
      console.error('[helloasso-webhook] dedup KV error (continue):', err?.message || err);
    }
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

  // Email masqué dans les logs (audit trail complet en KV)
  const maskedEmail = email.replace(/^(.).*?(@.*)$/, '$1***$2');
  console.log(`[helloasso-webhook] UPGRADED ${maskedEmail} → ${plan}${expiresAt ? ' (expires ' + expiresAt + ')' : ' (lifetime)'} via ${eventType}`);

  return res.status(200).json({
    ok: true,
    upgraded: true,
    email,
    plan,
    expires: expiresAt,
    amount_eur: amountCents / 100,
  });
}
