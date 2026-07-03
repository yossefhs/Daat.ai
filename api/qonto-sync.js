// /api/qonto-sync — Synchronise les virements ENTRANTS Qonto vers l'admin Paiements.
//
// Récupère les transactions « credit » (argent reçu) du compte Qonto via l'API
// Business, dédoublonne, et les enregistre comme dons (source: 'qonto') dans le
// même stockage KV que l'admin lit (soutien:list). Elles apparaissent alors dans
// /admin/paiements.html avec la source « qonto ».
//
// Déclenchement :
//   - Manuel (bouton admin)  : GET /api/qonto-sync?secret=<ADMIN_PASSWORD>
//   - Cron Vercel (quotidien): Authorization: Bearer <CRON_SECRET>
//   - Test à blanc           : ?dry=1  (compte sans écrire)
//   - Fenêtre                : ?since=YYYY-MM-DD  (défaut : QONTO_SINCE ou 90 j)
//   - Lister les comptes     : ?accounts=1  (pour trouver l'IBAN de daattorah)
//   - Purger les imports     : ?reset=1     (retire tous les q-*, remet à zéro)
//   - Filtre ponctuel        : ?include=daat,don  (liste blanche à la volée)
//
// ➜ Pour n'importer QUE les paiements daattorah (compte Qonto partagé) :
//     • soit un compte dédié → mettre son IBAN dans QONTO_IBAN ;
//     • soit un compte unique → QONTO_INCLUDE (mots-clés obligatoires dans le virement).
//
// Variables d'environnement Vercel (à définir) :
//   QONTO_LOGIN            = login API Qonto      (Qonto → Paramètres → Intégrations → API)
//   QONTO_SECRET_KEY       = clé secrète API Qonto
//   QONTO_BANK_ACCOUNT_ID  = (optionnel) UUID du compte ; sinon déduit via /organization
//   QONTO_IBAN             = (optionnel) IBAN du compte daattorah — ne synchronise QUE lui
//   QONTO_INCLUDE          = (optionnel) mots-clés OBLIGATOIRES (libellé+référence+note),
//                            séparés par des virgules — n'importe QUE les virgules matchant
//                            (ex. "daat,don,tsedaka,soutien"). Idéal si un seul compte reçoit tout.
//   QONTO_EXCLUDE          = (optionnel) libellés à ignorer, séparés par des virgules
//                            (défaut : "helloasso,stripe,remboursement,refund" — évite de
//                             recompter les reversements HelloAsso déjà suivis par le webhook)
//   QONTO_SINCE            = (optionnel) date ISO plancher par défaut (ex. 2026-01-01)
//
// ⚠ N'écrit PAS sur le Mur public (vie privée des payeurs bancaires). Alimente en
//   revanche la barre de progression mensuelle (soutien:total), comme un don manuel.

import { kv } from './_kv.js';

const QONTO_BASE = 'https://thirdparty.qonto.com/v2';
const DEFAULT_EXCLUDE = ['helloasso', 'stripe', 'remboursement', 'refund'];
const PROCESSED_SET = 'qonto:processed';

function setCors(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Admin-Secret');
}

// Auth : admin (UI) OU cron Vercel.
function isAuthed(req) {
  const adminPwd = process.env.ADMIN_PASSWORD;
  const soutienSecret = process.env.SOUTIEN_ADMIN_SECRET;
  const cronSecret = process.env.CRON_SECRET;

  const bearer = (req.headers.authorization || '').replace(/^Bearer\s+/i, '');
  if (bearer && cronSecret && bearer === cronSecret) return true;
  if (bearer && soutienSecret && bearer === soutienSecret) return true;
  if (bearer && adminPwd && bearer === adminPwd) return true;

  const headerSecret = req.headers['x-admin-secret'];
  if (headerSecret && adminPwd && headerSecret === adminPwd) return true;

  const qsSecret = req.query?.secret;
  if (qsSecret && adminPwd && qsSecret === adminPwd) return true;

  return false;
}

async function qontoGet(path) {
  const login = process.env.QONTO_LOGIN;
  const key = process.env.QONTO_SECRET_KEY;
  if (!login || !key) {
    const e = new Error('QONTO_LOGIN / QONTO_SECRET_KEY non configurés sur Vercel');
    e.code = 'no_creds';
    throw e;
  }
  const r = await fetch(QONTO_BASE + path, {
    headers: { Authorization: `${login}:${key}`, Accept: 'application/json' },
  });
  if (!r.ok) {
    const body = (await r.text().catch(() => '')).slice(0, 300);
    throw new Error(`Qonto API ${r.status} sur ${path} — ${body}`);
  }
  return r.json();
}

async function resolveBankAccountId() {
  if (process.env.QONTO_BANK_ACCOUNT_ID) return process.env.QONTO_BANK_ACCOUNT_ID;
  const org = await qontoGet('/organization');
  const accounts = org?.organization?.bank_accounts || org?.bank_accounts || [];
  if (!accounts.length) throw new Error('Aucun compte bancaire dans /organization Qonto');
  const wantedIban = (process.env.QONTO_IBAN || '').replace(/\s/g, '');
  const match = wantedIban
    ? accounts.find((a) => String(a.iban || '').replace(/\s/g, '') === wantedIban)
    : null;
  return (match || accounts[0]).id;
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET only' });
  if (!isAuthed(req)) return res.status(401).json({ error: 'Unauthorized' });

  // ── Mode « lister les comptes » (?accounts=1) : pour identifier lequel est
  //    celui de daattorah (IBAN à mettre dans QONTO_IBAN). ──
  if (req.query.accounts === '1') {
    try {
      const org = await qontoGet('/organization');
      const accounts = (org?.organization?.bank_accounts || org?.bank_accounts || []).map((a) => ({
        id: a.id,
        name: a.name || a.slug || null,
        iban: a.iban || null,
        balance: a.balance != null ? a.balance
          : (a.balance_cents != null ? a.balance_cents / 100 : null),
        currency: a.currency || 'EUR',
      }));
      return res.status(200).json({ ok: true, accounts });
    } catch (err) {
      const status = err?.code === 'no_creds' ? 503 : 500;
      return res.status(status).json({ error: err?.message || 'Erreur serveur' });
    }
  }

  // ── Mode « purge » (?reset=1) : retire TOUS les imports Qonto déjà faits
  //    (id q-*), décrémente les compteurs, et vide le set de dédoublonnage
  //    pour permettre un ré-import filtré propre. ──
  if (req.query.reset === '1') {
    try {
      const ids = (await kv.lrange('soutien:list', 0, 9999)) || [];
      let removed = 0;
      for (const id of ids) {
        if (!String(id).startsWith('q-')) continue;
        const rec = await kv.get(`soutien:${id}`);
        if (rec && rec.amount > 0 && rec.createdAt) {
          const d = new Date(rec.createdAt);
          const mk = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
          await kv.incrby(`soutien:total:${mk}`, -Math.round(rec.amount * 100));
          await kv.incrby(`soutien:count:${mk}`, -1);
        }
        await kv.lrem('soutien:list', 0, id);
        await kv.del(`soutien:${id}`);
        removed++;
      }
      try { await kv.del(PROCESSED_SET); } catch (_) {}
      return res.status(200).json({ ok: true, reset: true, removed });
    } catch (err) {
      return res.status(500).json({ error: err?.message || 'Erreur serveur' });
    }
  }

  const dryRun = req.query.dry === '1';
  const excludes = (process.env.QONTO_EXCLUDE
    ? process.env.QONTO_EXCLUDE.split(',')
    : DEFAULT_EXCLUDE
  ).map((s) => s.trim().toLowerCase()).filter(Boolean);

  // Liste blanche (QONTO_INCLUDE ou ?include=…) : si définie, on n'importe QUE
  // les crédits dont le texte (libellé + référence + note) contient l'un de ces
  // mots (ex. "daat,don,tsedaka,soutien"). Idéal quand UN seul compte reçoit tout.
  const includes = (process.env.QONTO_INCLUDE || req.query.include || '')
    .split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);

  // Fenêtre plancher (évite d'importer des années de crédits au 1er passage)
  let since = req.query.since || process.env.QONTO_SINCE || '';
  if (!since) {
    const d = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
    since = d.toISOString().slice(0, 10);
  }
  const sinceIso = /^\d{4}-\d{2}-\d{2}/.test(since) ? new Date(since).toISOString() : since;

  try {
    const bankId = await resolveBankAccountId();

    // Récupère les crédits (argent reçu), réglés, depuis la date plancher, paginé.
    const all = [];
    let page = 1;
    let totalPages = 1;
    do {
      const qs = new URLSearchParams({
        bank_account_id: bankId,
        side: 'credit',
        'status[]': 'completed',
        per_page: '100',
        page: String(page),
        sort_by: 'settled_at:desc',
        settled_at_from: sinceIso,
      });
      const data = await qontoGet('/transactions?' + qs.toString());
      const txns = data?.transactions || [];
      all.push(...txns);
      totalPages = data?.meta?.total_pages || 1;
      page += 1;
    } while (page <= totalPages && page <= 10); // plafond de sécurité : 1000 txns

    let synced = 0;
    let skipped = 0;
    let excluded = 0;
    const added = [];

    for (const t of all) {
      if (t.side !== 'credit') continue;
      // Texte de matching : libellé (nom du payeur) + référence + note du virement.
      const text = [t.label, t.reference, t.note].map((v) => String(v || '')).join(' ').toLowerCase();
      if (excludes.some((x) => x && text.includes(x))) { excluded++; continue; }
      // Liste blanche : si active, tout ce qui NE matche PAS est ignoré.
      if (includes.length && !includes.some((x) => text.includes(x))) { excluded++; continue; }

      // Dédoublonnage par identifiant Qonto (sadd = 1 si nouveau, 0 sinon)
      const isNew = await kv.sadd(PROCESSED_SET, t.id);
      if (isNew === 0) { skipped++; continue; }
      if (dryRun) {
        // en test à blanc, on retire l'id du set pour ne pas fausser un run réel
        try { await kv.srem(PROCESSED_SET, t.id); } catch (_) {}
        synced++;
        added.push({ label: t.label, amount: Number(t.amount) || 0, at: t.settled_at });
        continue;
      }

      const amount = Number(t.amount) || Number(t.amount_cents || 0) / 100;
      const createdAt = t.settled_at || t.emitted_at || new Date().toISOString();
      const id = `q-${t.id}`;
      const record = {
        id,
        name: t.label || 'Virement Qonto',
        type: 'don',
        source: 'qonto',
        amount,
        dedicace: t.reference || t.note || null,
        anonymous: false,
        createdAt,
        qonto_operation: t.operation_type || null,
        qonto_txn: t.transaction_id || null,
      };
      await kv.set(`soutien:${id}`, record);
      await kv.lpush('soutien:list', id);
      await kv.ltrim('soutien:list', 0, 9999);
      // Compteurs mensuels (barre de progression) — symétrique avec la route DELETE
      // qui décrémente à la suppression. Un virement Qonto est un vrai don.
      if (amount > 0) {
        const d = new Date(createdAt);
        const mk = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
        await kv.incrby(`soutien:total:${mk}`, Math.round(amount * 100));
        await kv.incr(`soutien:count:${mk}`);
      }
      synced++;
      added.push({ label: t.label, amount, at: createdAt });
    }

    return res.status(200).json({
      ok: true,
      bank_account_id: bankId,
      since: sinceIso,
      fetched: all.length,
      synced,
      skipped,
      excluded,
      dryRun,
      filter: { excludes, includes },
      added: added.slice(0, 50),
    });
  } catch (err) {
    console.error('[qonto-sync]', err?.message || err);
    const status = err?.code === 'no_creds' ? 503 : 500;
    return res.status(status).json({ error: err?.message || 'Erreur serveur' });
  }
}
