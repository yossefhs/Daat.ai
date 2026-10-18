// Edge Middleware Vercel — Protection de /admin
//
// Toutes les requêtes vers /admin (avec ou sans barre finale) sont interceptées
// AVANT d'atteindre le fichier/fonction cible. Deux portes, dans cet ordre :
//
//   1. la SESSION PAR COURRIEL — le cookie `daat_session` (JWT HS256 signé par
//      api/_auth.js) dont l'adresse figure dans ADMIN_EMAILS (ou ADMIN_EMAIL).
//      C'est la même règle que adminParJeton() dans api/_admin-gate.js ;
//   2. le MOT DE PASSE (Basic Auth, ADMIN_PASSWORD), comme avant.
//
// Sans l'un ni l'autre, une visite SANS identifiants est renvoyée vers la page
// de connexion par courriel (/connexion-admin.html), qui propose aussi le mot de
// passe : son lien ajoute `?motdepasse` et reçoit la fenêtre Basic Auth habituelle.
// Un mot de passe FAUX reçoit toujours le 401, pour que le navigateur redemande.
//
// Pourquoi : la fenêtre du navigateur n'expliquait pas quoi taper, et la
// connexion par courriel (déjà en place dans admin/index.html) restait derrière
// elle — il fallait le mot de passe partagé pour atteindre la connexion qui
// devait s'en passer. ADMIN_EMAILS non renseignée : rien ne change que la page
// de connexion, et le mot de passe fonctionne exactement comme avant.
//
// Compatible Edge Runtime (pas de Node.js, pas de Buffer/require) :
// utilise uniquement des API Web standard (crypto.subtle, TextEncoder, atob).
//
// Documentation : https://vercel.com/docs/functions/edge-middleware

export const config = {
  // Capture /admin et /admin/* (avec ou sans barre finale)
  matcher: ['/admin', '/admin/:path*'],
};

export default async function middleware(req) {
  // 1. Session par courriel d'une adresse administratrice : on laisse passer.
  if (await sessionAdmin(req)) return;

  const authHeader = req.headers.get('authorization');
  const expectedPassword = process.env.ADMIN_PASSWORD;

  // Fail closed : si la variable n'est pas configurée, on refuse l'accès.
  if (!expectedPassword) {
    return new Response('Configuration manquante', {
      status: 500,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }

  // Vérification Basic Auth avec comparaison en temps constant
  if (authHeader && authHeader.startsWith('Basic ')) {
    const base64Credentials = authHeader.slice(6);
    
    try {
      // Décoder les credentials (atob est disponible sur Edge Runtime)
      const credentials = atob(base64Credentials);
      const colonIndex = credentials.indexOf(':');
      
      if (colonIndex !== -1) {
        const providedPassword = credentials.slice(colonIndex + 1);
        
        // Comparaison en temps constant avec crypto.subtle (API Web)
        const isValid = await constantTimeEqual(providedPassword, expectedPassword);
        
        if (isValid) {
          // Authentification réussie : on laisse passer la requête
          return;
        }
      }
    } catch {
      // Erreur de décodage base64 ou autre : traiter comme échec d'auth
    }
  }

  // Aucune identification : la page de connexion par courriel, qui explique
  // quoi faire et propose aussi le mot de passe. `?motdepasse` demande la fenêtre.
  const url = new URL(req.url);
  if (!authHeader && !url.searchParams.has('motdepasse')) {
    const connexion = new URL('/connexion-admin.html', url);
    connexion.searchParams.set('retour', url.pathname + url.search);
    return Response.redirect(connexion, 302);
  }

  // Mauvais secret, ou mot de passe demandé : 401 avec fenêtre Basic Auth
  return new Response('Authentification requise', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="DAAT Admin", charset="UTF-8"',
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
}

/**
 * Comparaison en temps constant de deux chaînes via crypto.subtle.
 * Utilise SHA-256 puis XOR bit à bit pour éviter les attaques par timing.
 */
async function constantTimeEqual(a, b) {
  // Encoder les deux chaînes en Uint8Array
  const encoder = new TextEncoder();
  const bufferA = encoder.encode(a);
  const bufferB = encoder.encode(b);

  // Si les longueurs diffèrent, on calcule quand même les hash pour
  // éviter de révéler la longueur attendue par le temps de réponse
  const lengthMatch = bufferA.length === bufferB.length;

  // Calculer les hash SHA-256 des deux valeurs
  const [hashA, hashB] = await Promise.all([
    crypto.subtle.digest('SHA-256', bufferA),
    crypto.subtle.digest('SHA-256', bufferB),
  ]);

  // Convertir en Uint8Array pour comparaison
  const arrayA = new Uint8Array(hashA);
  const arrayB = new Uint8Array(hashB);

  // XOR bit à bit en temps constant
  let diff = 0;
  for (let i = 0; i < arrayA.length; i++) {
    diff |= arrayA[i] ^ arrayB[i];
  }

  // Retourner true seulement si longueurs égales ET hash identiques
  return lengthMatch && diff === 0;
}

// ── Session par courriel ─────────────────────────────────────────────────────
// Vérifie le cookie `daat_session` comme jsonwebtoken le signe (HS256, champ
// `exp`), sans la bibliothèque, absente de l'Edge Runtime. crypto.subtle.verify
// compare la signature en temps constant. Rend l'adresse, ou null.
const ADMIN_EMAILS = () => String(process.env.ADMIN_EMAILS || process.env.ADMIN_EMAIL || '')
  .split(',').map((s) => s.trim().toLowerCase()).filter(Boolean);

function octetsBase64url(s) {
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (s.length % 4)) % 4);
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
const jsonBase64url = (s) => JSON.parse(new TextDecoder().decode(octetsBase64url(s)));

export async function sessionAdmin(req) {
  const secret = process.env.JWT_SECRET;
  const liste = ADMIN_EMAILS();
  if (!secret || !liste.length) return null;
  const m = (req.headers.get('cookie') || '').match(/(?:^|;\s*)daat_session=([^;]+)/);
  if (!m) return null;
  try {
    const parties = decodeURIComponent(m[1]).split('.');
    if (parties.length !== 3) return null;
    const [h, p, sig] = parties;
    if (jsonBase64url(h).alg !== 'HS256') return null;
    const enc = new TextEncoder();
    const cle = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
    if (!(await crypto.subtle.verify('HMAC', cle, octetsBase64url(sig), enc.encode(h + '.' + p)))) return null;
    const charge = jsonBase64url(p);
    const maintenant = Math.floor(Date.now() / 1000);
    if (typeof charge.exp !== 'number' || charge.exp <= maintenant) return null;
    if (typeof charge.nbf === 'number' && charge.nbf > maintenant) return null;
    const email = String(charge.email || '').trim().toLowerCase();
    return liste.includes(email) ? email : null;
  } catch {
    return null;
  }
}
