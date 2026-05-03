// GET /api/auth/me
// Retourne l'utilisateur courant si connecté, sinon 401.

import { getUserFromRequest, setCorsHeaders } from '../_auth.js';

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ error: 'GET uniquement' });

  const user = getUserFromRequest(req);
  if (!user) return res.status(401).json({ error: 'Non authentifié' });
  return res.status(200).json({ user });
}
