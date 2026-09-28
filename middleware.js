// Edge Middleware Vercel — Protection /admin par Basic Auth
//
// Toutes les requêtes vers /admin (avec ou sans barre finale) sont interceptées
// AVANT d'atteindre le fichier/fonction cible. Sans identifiants valides : 401
// avec une fenêtre Basic Auth du navigateur.
//
// Compatible Edge Runtime (pas de Node.js, pas de Buffer/require) :
// utilise uniquement des API Web standard (crypto.subtle, TextEncoder, atob).
//
// Documentation : https://vercel.com/docs/functions/edge-middleware

export const config = {
  // Capture /admin et /admin/* (avec ou sans barre finale)
  matcher: ['/admin', '/admin/:path*'],
};

export async function middleware(req) {
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

  // Pas d'Authorization, ou mauvais secret : 401 avec fenêtre Basic Auth
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
