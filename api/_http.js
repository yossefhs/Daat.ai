// Helpers HTTP partagés par les fonctions serverless.

// Extrait l'IP cliente d'une requête derrière le proxy Vercel.
// x-forwarded-for peut contenir une liste « client, proxy1, proxy2 » : on prend
// le premier élément (le client réel). Fallback x-real-ip puis socket.
export function getClientIp(req) {
  const xff = req.headers['x-forwarded-for'] || '';
  const first = xff.split(',')[0].trim();
  return first || req.headers['x-real-ip'] || req.socket?.remoteAddress || 'unknown';
}
