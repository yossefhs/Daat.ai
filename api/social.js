// /api/social — Pilote automatique réseaux sociaux DAAT (sans service tiers).
//
// Chaque semaine (cron Vercel, mardi 09:00 UTC), publie le « siman de la semaine »
// directement via les APIs officielles des plateformes configurées. Une plateforme
// est active dès que ses variables d'environnement sont présentes :
//
//   Facebook Page : FB_PAGE_ID + FB_PAGE_TOKEN            (Graph API /feed)
//   Instagram     : IG_USER_ID + (IG_ACCESS_TOKEN|FB_PAGE_TOKEN)  (container + publish, image PNG)
//   LinkedIn      : LINKEDIN_ACCESS_TOKEN + LINKEDIN_AUTHOR_URN   (REST /posts)
//   X (Twitter)   : X_API_KEY + X_API_SECRET + X_ACCESS_TOKEN + X_ACCESS_SECRET  (OAuth 1.0a, /2/tweets)
//   Telegram      : TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID  (sendMessage)
//
// GET (auth Bearer ${CRON_SECRET} ou ?secret=) :
//   /api/social                      → run cron (mardi : publie ; autre jour : no-op)
//   /api/social?action=preview       → JSON des posts du prochain siman (aucune publication)
//   /api/social?action=platforms     → liste des plateformes configurées
//   /api/social?action=force         → publie maintenant + avance le curseur
//   /api/social?action=status        → curseur, dernier envoi, derniers logs
//
// KV : social:weekly:cursor · social:weekly:lastSentDate · social:log (30 derniers runs)

import { createHmac, randomBytes } from 'node:crypto';
import { kv } from './_kv.js';
import { nextValidSiman, WEEKLY_DEFAULTS } from './_newsletter-weekly.js';
import { buildSocialPosts } from './_social-content.js';

const GRAPH = 'https://graph.facebook.com/v21.0';

// Valeur d'env nettoyée (les espaces/retours à la ligne collés dans Vercel
// produisent des URLs invalides → « Not Found » côté Telegram/Meta).
const env = (k) => (process.env[k] || '').trim();

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

// ---------- plateformes ----------

function configuredPlatforms() {
  const p = [];
  if (env('FB_PAGE_ID') && env('FB_PAGE_TOKEN')) p.push('facebook');
  if (env('IG_USER_ID') && (env('IG_ACCESS_TOKEN') || env('FB_PAGE_TOKEN'))) p.push('instagram');
  if (env('LINKEDIN_ACCESS_TOKEN') && env('LINKEDIN_AUTHOR_URN')) p.push('linkedin');
  if (env('X_API_KEY') && env('X_API_SECRET') && env('X_ACCESS_TOKEN') && env('X_ACCESS_SECRET')) p.push('x');
  if (env('TELEGRAM_BOT_TOKEN') && env('TELEGRAM_CHAT_ID')) p.push('telegram');
  return p;
}

async function postFacebook(posts) {
  const url = `${GRAPH}/${env('FB_PAGE_ID')}/feed`;
  const body = new URLSearchParams({
    message: posts.facebook,
    link: posts.link,
    access_token: env('FB_PAGE_TOKEN'),
  });
  const r = await fetch(url, { method: 'POST', body });
  const d = await r.json();
  if (!r.ok || d.error) throw new Error(d.error?.message || `HTTP ${r.status}`);
  return d.id;
}

async function postInstagram(posts) {
  const token = env('IG_ACCESS_TOKEN') || env('FB_PAGE_TOKEN');
  const igUser = env('IG_USER_ID');
  // 1) container image + caption
  let r = await fetch(`${GRAPH}/${igUser}/media`, {
    method: 'POST',
    body: new URLSearchParams({ image_url: posts.image, caption: posts.instagram, access_token: token }),
  });
  let d = await r.json();
  if (!r.ok || d.error) throw new Error(d.error?.message || `container HTTP ${r.status}`);
  // 2) publish
  r = await fetch(`${GRAPH}/${igUser}/media_publish`, {
    method: 'POST',
    body: new URLSearchParams({ creation_id: d.id, access_token: token }),
  });
  d = await r.json();
  if (!r.ok || d.error) throw new Error(d.error?.message || `publish HTTP ${r.status}`);
  return d.id;
}

async function postLinkedIn(posts) {
  const r = await fetch('https://api.linkedin.com/rest/posts', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env('LINKEDIN_ACCESS_TOKEN')}`,
      'Content-Type': 'application/json',
      'X-Restli-Protocol-Version': '2.0.0',
      'LinkedIn-Version': env('LINKEDIN_VERSION') || '202406',
    },
    body: JSON.stringify({
      author: env('LINKEDIN_AUTHOR_URN'),
      commentary: posts.linkedin,
      visibility: 'PUBLIC',
      distribution: { feedDistribution: 'MAIN_FEED', targetEntities: [], thirdPartyDistributionChannels: [] },
      lifecycleState: 'PUBLISHED',
      isReshareDisabledByAuthor: false,
    }),
  });
  if (r.status === 201) return r.headers.get('x-restli-id') || 'created';
  const d = await r.json().catch(() => ({}));
  throw new Error(d.message || `HTTP ${r.status}`);
}

// OAuth 1.0a (X API v2 /tweets) — signature HMAC-SHA1, sans dépendance.
function oauth1Header(method, url) {
  const enc = (s) => encodeURIComponent(s).replace(/[!'()*]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase());
  const oauth = {
    oauth_consumer_key: env('X_API_KEY'),
    oauth_nonce: randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: String(Math.floor(Date.now() / 1000)),
    oauth_token: env('X_ACCESS_TOKEN'),
    oauth_version: '1.0',
  };
  // Corps JSON → seuls les paramètres oauth entrent dans la base de signature.
  const paramStr = Object.keys(oauth).sort().map((k) => `${enc(k)}=${enc(oauth[k])}`).join('&');
  const base = [method.toUpperCase(), enc(url), enc(paramStr)].join('&');
  const key = `${enc(env('X_API_SECRET'))}&${enc(env('X_ACCESS_SECRET'))}`;
  oauth.oauth_signature = createHmac('sha1', key).update(base).digest('base64');
  return 'OAuth ' + Object.keys(oauth).sort().map((k) => `${enc(k)}="${enc(oauth[k])}"`).join(', ');
}

async function postX(posts) {
  const url = 'https://api.x.com/2/tweets';
  const r = await fetch(url, {
    method: 'POST',
    headers: { Authorization: oauth1Header('POST', url), 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: posts.x }),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.detail || d.title || `HTTP ${r.status}`);
  return d.data?.id || 'created';
}

async function postTelegram(posts) {
  const r = await fetch(`https://api.telegram.org/bot${env('TELEGRAM_BOT_TOKEN')}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: env('TELEGRAM_CHAT_ID'), text: posts.telegram }),
  });
  const d = await r.json();
  if (!d.ok) throw new Error(d.description || 'telegram error');
  return String(d.result?.message_id || 'sent');
}

const PUBLISHERS = {
  facebook: postFacebook,
  instagram: postInstagram,
  linkedin: postLinkedIn,
  x: postX,
  telegram: postTelegram,
};

// ---------- run ----------

async function runBroadcast({ force = false } = {}) {
  const platforms = configuredPlatforms();
  if (!platforms.length) return { ok: true, skipped: 'no-platform-configured' };

  // Anti-doublon (un envoi par jour calendaire, sauf force)
  if (!force) {
    const last = await kv.get('social:weekly:lastSentDate');
    if (last === todayStr()) return { ok: true, skipped: 'already-sent-today' };
  }

  const cursor = Number(await kv.get('social:weekly:cursor')) || WEEKLY_DEFAULTS.FIRST_SIMAN;
  const num = nextValidSiman(cursor);
  if (!num) return { ok: true, done: true, message: 'Série terminée (365 atteint).' };

  const posts = buildSocialPosts(num);
  const results = {};
  let okCount = 0;
  for (const p of platforms) {
    try {
      results[p] = { ok: true, id: await PUBLISHERS[p](posts) };
      okCount++;
    } catch (e) {
      results[p] = { ok: false, error: String(e?.message || e).slice(0, 300) };
    }
  }

  // On avance le curseur dès qu'au moins une plateforme a publié.
  if (okCount > 0) {
    await kv.set('social:weekly:lastSentDate', todayStr());
    const next = nextValidSiman(num + 1);
    await kv.set('social:weekly:cursor', next || WEEKLY_DEFAULTS.LAST_SIMAN + 1);
  }

  const entry = { at: new Date().toISOString(), siman: num, platforms, results, okCount };
  try {
    await kv.lpush('social:log', JSON.stringify(entry));
    await kv.ltrim('social:log', 0, 29);
  } catch { /* best effort */ }

  return { ok: true, siman: num, ...entry };
}

// ---------- handler ----------

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET uniquement' });

  const secret = process.env.CRON_SECRET;
  const auth = req.headers.authorization || '';
  const authorized = !!secret && (auth === `Bearer ${secret}` || (req.query && req.query.secret) === secret);
  if (!authorized) return res.status(401).json({ error: 'Unauthorized' });

  const action = (req.query && req.query.action) || '';
  try {
    if (action === 'platforms') {
      return res.status(200).json({ ok: true, platforms: configuredPlatforms() });
    }
    if (action === 'preview') {
      const cursor = Number(await kv.get('social:weekly:cursor')) || WEEKLY_DEFAULTS.FIRST_SIMAN;
      const num = nextValidSiman(cursor);
      return res.status(200).json({ ok: true, siman: num, platforms: configuredPlatforms(), posts: num ? buildSocialPosts(num) : null });
    }
    if (action === 'status') {
      const [cursor, last, log] = await Promise.all([
        kv.get('social:weekly:cursor'),
        kv.get('social:weekly:lastSentDate'),
        kv.lrange('social:log', 0, 9),
      ]);
      return res.status(200).json({
        ok: true,
        cursor: Number(cursor) || WEEKLY_DEFAULTS.FIRST_SIMAN,
        lastSentDate: last || null,
        platforms: configuredPlatforms(),
        log: (log || []).map((s) => { try { return JSON.parse(s); } catch { return s; } }),
      });
    }
    if (action === 'force') {
      return res.status(200).json(await runBroadcast({ force: true }));
    }
    // Cron : ne publie que le mardi (UTC) — les autres jours, no-op.
    if (new Date().getUTCDay() !== 2) {
      return res.status(200).json({ ok: true, skipped: 'not-broadcast-day' });
    }
    return res.status(200).json(await runBroadcast());
  } catch (err) {
    console.error('[social] error:', err);
    return res.status(500).json({ error: err?.message || 'Erreur serveur' });
  }
}
