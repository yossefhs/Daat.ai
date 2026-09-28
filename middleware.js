// Edge Middleware Vercel — Protection /admin par Basic Auth
//
// Toutes les requêtes vers /admin (pages HTML + API) sont interceptées AVANT
// d'atteindre le fichier/fonction cible. Sans identifiants valides : 401
// avec une fenêtre Basic Auth du navigateur. Avec le bon ADMIN_PASSWORD : passe.
//
// Ne touche RIEN en dehors de /admin : les pages publiques, /chat, /oh/,
// /api/chat, etc. continuent à fonctionner exactement comme avant.
//
// Documentation Vercel : https://vercel.com/docs/functions/edge-middleware
// (compatible avec un projet non-Next comme celui-ci, sans aucune dépendance)

import { NextResponse } from 'next/server';

export const config = {
  matcher: '/admin/:path*',
};

export function middleware(req) {
  const authHeader = req.headers.get('authorization');
  const expectedPassword = process.env.ADMIN_PASSWORD;

  // Fail closed : si la variable n'est pas configurée, on refuse l'accès.
  if (!expectedPassword) {
    return new NextResponse('Configuration manquante', {
      status: 500,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }

  // Comparaison en temps constant (crypto.timingSafeEqual) pour éviter
  // les attaques par timing. Basic Auth : "Authorization: Basic <base64>"
  // où base64 encode "username:password" — on accepte n'importe quel
  // username, seul le mot de passe compte.
  if (authHeader && authHeader.startsWith('Basic ')) {
    const base64Credentials = authHeader.slice(6);
    
    try {
      const credentials = Buffer.from(base64Credentials, 'base64').toString('utf8');
      const [, providedPassword] = credentials.split(':', 2);

      // Comparaison en temps constant : les deux buffers doivent avoir
      // exactement la même longueur, sinon timingSafeEqual lève une erreur.
      const expectedBuf = Buffer.from(expectedPassword, 'utf8');
      const providedBuf = Buffer.from(providedPassword || '', 'utf8');

      if (expectedBuf.length === providedBuf.length) {
        const crypto = require('crypto');
        const isValid = crypto.timingSafeEqual(expectedBuf, providedBuf);
        
        if (isValid) {
          // Authentification réussie : on laisse passer la requête.
          return NextResponse.next();
        }
      }
    } catch {
      // Erreur de décodage base64 ou autre : on traite comme échec d'auth.
    }
  }

  // Pas d'Authorization, ou mauvais secret : 401 avec fenêtre Basic Auth.
  return new NextResponse('Authentification requise', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="DAAT Admin", charset="UTF-8"',
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
}
