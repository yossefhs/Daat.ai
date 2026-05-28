// Module partagé d'authentification — JWT + cookies + helpers
// Auth flow : OTP par email (code à 6 chiffres envoyé via Resend)
//
// Variables d'environnement requises (Vercel) :
//   - JWT_SECRET       : chaîne aléatoire ≥ 32 caractères (signe les sessions)
//   - RESEND_API_KEY   : clé API Resend (envoi des emails)
//   - RESEND_FROM_EMAIL: optionnel — adresse expéditeur (défaut : noreply@daattorah.com)

import jwt from 'jsonwebtoken';
import { kv } from './_kv.js';

const COOKIE_NAME = 'daat_session';
const SESSION_DAYS = 30;

// === JWT ===

export function signSession(payload) {
  if (!process.env.JWT_SECRET) throw new Error('JWT_SECRET non configuré');
  return jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: `${SESSION_DAYS}d` });
}

export function verifySession(token) {
  if (!process.env.JWT_SECRET) return null;
  try {
    return jwt.verify(token, process.env.JWT_SECRET);
  } catch {
    return null;
  }
}

// === COOKIES ===

function parseCookies(req) {
  const header = req.headers.cookie || '';
  return header.split(';').reduce((acc, pair) => {
    const idx = pair.indexOf('=');
    if (idx < 0) return acc;
    const k = pair.slice(0, idx).trim();
    const v = pair.slice(idx + 1).trim();
    if (k) acc[k] = decodeURIComponent(v || '');
    return acc;
  }, {});
}

export function getUserFromRequest(req) {
  const cookies = parseCookies(req);
  const token = cookies[COOKIE_NAME];
  if (!token) return null;
  const payload = verifySession(token);
  if (!payload || !payload.email) return null;
  return { email: payload.email };
}

export function setSessionCookie(res, token) {
  const maxAge = SESSION_DAYS * 24 * 60 * 60; // seconds
  // SameSite=None requis : le cookie est posé par daatai.vercel.app mais consommé
  // depuis daattorah.com (cross-site). Lax bloquerait l'envoi sur les fetch().
  res.setHeader('Set-Cookie', [
    `${COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=${maxAge}`,
  ]);
}

export function clearSessionCookie(res) {
  res.setHeader('Set-Cookie', [
    `${COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=None; Max-Age=0`,
  ]);
}

// === HELPERS ===

export function generateCode() {
  // Code numérique à 6 chiffres
  return String(Math.floor(100000 + Math.random() * 900000));
}

export function isValidEmail(email) {
  return (
    typeof email === 'string' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) &&
    email.length <= 100
  );
}

// Rate limiting : max 3 codes par email par 15 min
export async function checkSendRateLimit(email) {
  const key = `auth:send-rate:${email}`;
  const count = await kv.incr(key);
  if (count === 1) await kv.expire(key, 15 * 60);
  return count <= 3;
}

// === CORS HELPERS ===

export function setCorsHeaders(req, res) {
  const origin = req.headers.origin || '*';
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}
