// Client Redis partagé — remplace @vercel/kv (déprécié par Vercel).
//
// @vercel/kv n'était qu'une surcouche d'@upstash/redis ; on s'y connecte
// donc directement, en réutilisant les MÊMES variables d'environnement
// (KV_REST_API_URL / KV_REST_API_TOKEN) — aucun changement de configuration
// Vercel n'est nécessaire.
//
// Le client est construit paresseusement (à la première utilisation), comme
// le faisait @vercel/kv : importer ce module ne lève pas d'erreur même si
// les variables d'environnement sont absentes.
import { Redis } from '@upstash/redis';

let client;

function getClient() {
  if (!client) {
    client = new Redis({
      url: process.env.KV_REST_API_URL,
      token: process.env.KV_REST_API_TOKEN,
    });
  }
  return client;
}

export const kv = new Proxy(
  {},
  {
    get(_target, prop) {
      const value = getClient()[prop];
      return typeof value === 'function' ? value.bind(getClient()) : value;
    },
  },
);
