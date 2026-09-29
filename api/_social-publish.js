// api/_social-publish.js — Publication du post quotidien AVEC son visuel, via les
// APIs officielles (gratuites) de chaque réseau. Une plateforme est active dès
// que ses variables d'environnement existent dans Vercel :
//
//   Facebook  : FB_PAGE_ID + FB_PAGE_TOKEN                       (Graph /photos)
//   Instagram : IG_USER_ID + (IG_ACCESS_TOKEN | FB_PAGE_TOKEN)   (container + publish)
//   LinkedIn  : LINKEDIN_ACCESS_TOKEN + LINKEDIN_AUTHOR_URN      (upload image + /posts)
//   X         : X_API_KEY + X_API_SECRET + X_ACCESS_TOKEN + X_ACCESS_SECRET (texte + lien)
//   Telegram  : TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID           (sendPhoto)
//
// WhatsApp n'a pas d'API de publication dans un groupe ou une chaîne : il reste
// un partage manuel depuis la page de validation.

import { createHmac, randomBytes } from 'node:crypto';

const env = (k) => (process.env[k] || '').trim();
const GRAPH = `https://graph.facebook.com/${env('META_GRAPH_VERSION') || 'v23.0'}`;

export function configuredPlatforms() {
  const p = [];
  if (env('FB_PAGE_ID') && env('FB_PAGE_TOKEN')) p.push('facebook');
  if (env('IG_USER_ID') && (env('IG_ACCESS_TOKEN') || env('FB_PAGE_TOKEN'))) p.push('instagram');
  if (env('LINKEDIN_ACCESS_TOKEN') && env('LINKEDIN_AUTHOR_URN')) p.push('linkedin');
  if (env('X_API_KEY') && env('X_API_SECRET') && env('X_ACCESS_TOKEN') && env('X_ACCESS_SECRET')) p.push('x');
  if (env('TELEGRAM_BOT_TOKEN') && env('TELEGRAM_CHAT_ID')) p.push('telegram');
  return p;
}

async function graphPost(path, params) {
  const r = await fetch(`${GRAPH}/${path}`, { method: 'POST', body: new URLSearchParams(params) });
  const d = await r.json().catch(() => ({}));
  if (!r.ok || d.error) throw new Error(d.error?.message || `HTTP ${r.status}`);
  return d;
}

async function facebook({ text, imageUrl }) {
  const d = await graphPost(`${env('FB_PAGE_ID')}/photos`, {
    url: imageUrl, caption: text, access_token: env('FB_PAGE_TOKEN'),
  });
  return d.post_id || d.id;
}

async function instagram({ text, imageUrl }) {
  const token = env('IG_ACCESS_TOKEN') || env('FB_PAGE_TOKEN');
  const c = await graphPost(`${env('IG_USER_ID')}/media`, { image_url: imageUrl, caption: text.slice(0, 2200), access_token: token });
  // Instagram traite l'image de façon asynchrone : on attend qu'elle soit prête.
  for (let i = 0; i < 10; i++) {
    const s = await fetch(`${GRAPH}/${c.id}?fields=status_code&access_token=${encodeURIComponent(token)}`).then((r) => r.json()).catch(() => ({}));
    if (s.status_code === 'FINISHED') break;
    if (s.status_code === 'ERROR') throw new Error('Instagram a refusé l\'image');
    await new Promise((res) => setTimeout(res, 2000));
  }
  const p = await graphPost(`${env('IG_USER_ID')}/media_publish`, { creation_id: c.id, access_token: token });
  return p.id;
}

async function linkedin({ text, imageBytes }) {
  const headers = {
    Authorization: `Bearer ${env('LINKEDIN_ACCESS_TOKEN')}`,
    'LinkedIn-Version': env('LINKEDIN_VERSION') || '202509',
    'X-Restli-Protocol-Version': '2.0.0',
    'Content-Type': 'application/json',
  };
  const author = env('LINKEDIN_AUTHOR_URN');
  let init = await fetch('https://api.linkedin.com/rest/images?action=initializeUpload', {
    method: 'POST', headers, body: JSON.stringify({ initializeUploadRequest: { owner: author } }),
  });
  const id = await init.json().catch(() => ({}));
  if (!init.ok) throw new Error(id.message || `initializeUpload HTTP ${init.status}`);
  const { uploadUrl, image } = id.value || {};
  const up = await fetch(uploadUrl, { method: 'PUT', headers: { Authorization: headers.Authorization }, body: imageBytes });
  if (!up.ok) throw new Error(`upload image HTTP ${up.status}`);
  const r = await fetch('https://api.linkedin.com/rest/posts', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      author,
      commentary: text.slice(0, 2900),
      visibility: 'PUBLIC',
      distribution: { feedDistribution: 'MAIN_FEED', targetEntities: [], thirdPartyDistributionChannels: [] },
      content: { media: { id: image, altText: 'Daat Yomi — infographie du jour' } },
      lifecycleState: 'PUBLISHED',
      isReshareDisabledByAuthor: false,
    }),
  });
  if (r.status === 201) return r.headers.get('x-restli-id') || 'created';
  const d = await r.json().catch(() => ({}));
  throw new Error(d.message || `HTTP ${r.status}`);
}

function oauth1Header(method, url) {
  const enc = (s) => encodeURIComponent(s).replace(/[!'()*]/g, (c) => '%' + c.charCodeAt(0).toString(16).toUpperCase());
  const o = {
    oauth_consumer_key: env('X_API_KEY'),
    oauth_nonce: randomBytes(16).toString('hex'),
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: String(Math.floor(Date.now() / 1000)),
    oauth_token: env('X_ACCESS_TOKEN'),
    oauth_version: '1.0',
  };
  const params = Object.keys(o).sort().map((k) => `${enc(k)}=${enc(o[k])}`).join('&');
  const base = [method, enc(url), enc(params)].join('&');
  o.oauth_signature = createHmac('sha1', `${enc(env('X_API_SECRET'))}&${enc(env('X_ACCESS_SECRET'))}`).update(base).digest('base64');
  return 'OAuth ' + Object.keys(o).sort().map((k) => `${enc(k)}="${enc(o[k])}"`).join(', ');
}

async function x({ text }) {
  const url = 'https://api.x.com/2/tweets';
  const r = await fetch(url, {
    method: 'POST',
    headers: { Authorization: oauth1Header('POST', url), 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text.slice(0, 280) }),
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.detail || d.title || `HTTP ${r.status}`);
  return d.data?.id || 'created';
}

async function telegram({ text, imageUrl }) {
  const r = await fetch(`https://api.telegram.org/bot${env('TELEGRAM_BOT_TOKEN')}/sendPhoto`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: env('TELEGRAM_CHAT_ID'), photo: imageUrl, caption: text.slice(0, 1024) }),
  });
  const d = await r.json().catch(() => ({}));
  if (!d.ok) throw new Error(d.description || 'telegram error');
  return String(d.result?.message_id || 'sent');
}

const PUBLISHERS = { facebook, instagram, linkedin, x, telegram };

// Texte adressé à chaque réseau : Telegram reprend la version WhatsApp.
export function textFor(platform, post) {
  const tags = (post.hashtags || []).map((h) => (h.startsWith('#') ? h : '#' + h)).join(' ');
  const p = post.posts || {};
  switch (platform) {
    case 'facebook': return p.facebook;
    case 'instagram': return `${p.instagram}\n\n${tags}`.trim();
    case 'linkedin': return p.linkedin;
    case 'x': return p.x;
    case 'telegram': return p.whatsapp;
    default: return '';
  }
}

// Publie sur chaque réseau configuré ; ne republie jamais un réseau déjà réussi.
export async function publishAll({ post, imageUrl, imageBytes, already = {} }) {
  const results = { ...already };
  for (const platform of configuredPlatforms()) {
    if (results[platform]?.ok) continue;
    try {
      const id = await PUBLISHERS[platform]({ text: textFor(platform, post), imageUrl, imageBytes });
      results[platform] = { ok: true, id, at: new Date().toISOString() };
    } catch (e) {
      results[platform] = { ok: false, error: String(e?.message || e).slice(0, 300), at: new Date().toISOString() };
    }
  }
  return results;
}
