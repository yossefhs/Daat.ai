// /api/indexnow — IndexNow notifier
//
// Notifie Bing, Yandex, Naver, Seznam et IndexNow.org en temps réel
// quand des URLs sont créées/modifiées. Cela accélère l'indexation
// dans Bing, Brave Search, Kagi, DuckDuckGo (qui se basent sur Bing).
//
// Standard IndexNow : https://www.indexnow.org/documentation
//
// Modes :
//   GET  /api/indexnow                    → ping rapide d'un échantillon
//                                          (Bearer ${INDEXNOW_SECRET})
//   POST /api/indexnow  body: { urls:[..] }
//                                          → notifier des URLs spécifiques
//   GET  /api/indexnow?action=ping-all     → notifier toutes les URLs
//                                          canoniques du sitemap (limite 10000)
//
// La clé IndexNow elle-même est servie en clair depuis la racine
// (fichier {KEY}.txt à la racine du repo, déjà créé).
//
// Variables env requises (Vercel) :
//   - INDEXNOW_KEY       = la clé hex 32 chars (= nom du fichier .txt)
//   - INDEXNOW_SECRET    = bearer pour les actions admin
//   - VERCEL_URL ou HOST = host du site (défaut : daattorah.com)

const HOST = "daattorah.com";

// Endpoints IndexNow officiels (un seul ping suffit, ils se synchronisent
// entre eux selon le standard, mais pinger les principaux est plus rapide)
const ENDPOINTS = [
  "https://api.indexnow.org/IndexNow",
  "https://www.bing.com/IndexNow",
  "https://yandex.com/indexnow",
];

function ok(res, data) {
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.status(200).send(JSON.stringify(data, null, 2));
}

function fail(res, status, error) {
  res.status(status).json({ error });
}

async function notify(urls, key, keyLocation) {
  if (!urls.length) return { sent: 0 };
  const payload = {
    host: HOST,
    key,
    keyLocation,
    urlList: urls,
  };
  const results = [];
  for (const endpoint of ENDPOINTS) {
    try {
      const r = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(payload),
      });
      results.push({
        endpoint,
        status: r.status,
        ok: r.ok || r.status === 202,
      });
    } catch (e) {
      results.push({ endpoint, error: e?.message || String(e) });
    }
  }
  return { sent: urls.length, endpoints: results };
}

export default async function handler(req, res) {
  const key = process.env.INDEXNOW_KEY;
  const secret = process.env.INDEXNOW_SECRET;
  if (!key) {
    return fail(res, 500, "INDEXNOW_KEY non configurée");
  }
  const keyLocation = `https://${HOST}/${key}.txt`;

  // Auth pour les actions sensibles
  const auth = req.headers.authorization || "";
  const expectedAuth = `Bearer ${secret}`;
  const authenticated = secret && auth === expectedAuth;

  try {
    const url = new URL(req.url, `https://${HOST}`);
    const action = url.searchParams.get("action") || "";

    if (req.method === "POST") {
      if (!authenticated) return fail(res, 401, "Bearer requis");
      const body = req.body || {};
      const urls = Array.isArray(body.urls) ? body.urls.slice(0, 10000) : [];
      if (!urls.length) return fail(res, 400, "body.urls vide");
      const result = await notify(urls, key, keyLocation);
      return ok(res, { mode: "post", ...result });
    }

    if (action === "ping-all") {
      if (!authenticated) return fail(res, 401, "Bearer requis");
      // Charge le sitemap canonique pour extraire les URLs /oh/...
      const r = await fetch(`https://${HOST}/sitemap.xml`);
      if (!r.ok) return fail(res, 500, "sitemap indisponible");
      const xml = await r.text();
      const matches = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)];
      const urls = matches.map((m) => m[1]).filter((u) => u.startsWith(`https://${HOST}`));
      const result = await notify(urls.slice(0, 10000), key, keyLocation);
      return ok(res, { mode: "ping-all", urls_total: urls.length, ...result });
    }

    // Mode défaut : ping d'un échantillon (homepage + 2 pages clés)
    if (!authenticated) return fail(res, 401, "Bearer requis pour les pings");
    const sample = [
      `https://${HOST}/`,
      `https://${HOST}/limoud/`,
      `https://${HOST}/about`,
    ];
    const result = await notify(sample, key, keyLocation);
    return ok(res, { mode: "sample", ...result });
  } catch (e) {
    console.error("[indexnow]", e);
    return fail(res, 500, e?.message || "erreur serveur");
  }
}
