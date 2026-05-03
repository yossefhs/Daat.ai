// POST /api/auth/logout
// Clear le cookie de session.

import { clearSessionCookie, setCorsHeaders } from '../_auth.js';

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  clearSessionCookie(res);
  return res.status(200).json({ ok: true });
}
