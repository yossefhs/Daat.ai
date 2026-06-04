// Helpers HTTP partagés par les fonctions serverless.

// Extrait l'IP cliente d'une requête derrière le proxy Vercel.
// ⚠️ Le 1er élément de x-forwarded-for est fourni par le client → falsifiable.
// On privilégie donc x-vercel-forwarded-for / x-real-ip, renseignés par la
// plateforme Vercel et non spoofables, avant de retomber sur x-forwarded-for.
export function getClientIp(req) {
  const vercel = req.headers['x-vercel-forwarded-for'];
  if (vercel) return String(vercel).split(',')[0].trim();
  const real = req.headers['x-real-ip'];
  if (real) return String(real).split(',')[0].trim();
  const xff = req.headers['x-forwarded-for'] || '';
  const first = xff.split(',')[0].trim();
  return first || req.socket?.remoteAddress || 'unknown';
}
