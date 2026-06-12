/*
 * sw.js — Service worker de daattorah.com (PWA installable).
 *
 * Stratégie :
 *   - Navigations (pages HTML) : network-first → le contenu halakhique reste frais ;
 *     repli sur le cache puis sur /offline.html quand le réseau manque.
 *   - Assets statiques (css/js/images/polices) : stale-while-revalidate.
 *   - L'API ( /api/* et l'origine daatai.vercel.app ) n'est JAMAIS mise en cache.
 *
 * Bump VERSION pour invalider les anciens caches.
 */
const VERSION = 'v2';
const STATIC_CACHE = `daat-static-${VERSION}`;
const PAGE_CACHE = `daat-pages-${VERSION}`;
const OFFLINE_URL = '/offline.html';
const PRECACHE = [OFFLINE_URL, '/favicon.svg', '/assets/css/daat.css', '/icons/icon-192.png'];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(STATIC_CACHE);
    await cache.addAll(PRECACHE).catch(() => {});
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys.filter((k) => !k.endsWith(VERSION)).map((k) => caches.delete(k))
    );
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // Ne touche pas aux requêtes cross-origin (polices Google, API daatai.vercel.app…).
  if (url.origin !== self.location.origin) return;
  // Ne met jamais l'API en cache.
  if (url.pathname.startsWith('/api/')) return;

  if (req.mode === 'navigate') {
    event.respondWith(networkFirst(req));
    return;
  }
  if (/\.(?:css|js|mjs|png|jpg|jpeg|gif|svg|webp|ico|woff2?|ttf|otf)$/.test(url.pathname)) {
    event.respondWith(staleWhileRevalidate(req));
  }
});

async function networkFirst(req) {
  const cache = await caches.open(PAGE_CACHE);
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.status === 200) cache.put(req, fresh.clone());
    return fresh;
  } catch (err) {
    const cached = await cache.match(req);
    return cached || (await caches.match(OFFLINE_URL)) || Response.error();
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(req);
  const fetching = fetch(req)
    .then((res) => {
      if (res && res.status === 200) cache.put(req, res.clone());
      return res;
    })
    .catch(() => cached);
  return cached || fetching;
}
