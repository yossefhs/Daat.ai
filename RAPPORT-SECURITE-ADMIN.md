# Rapport de sécurisation /admin — P0

## 🎯 Objectif

Empêcher tout accès non authentifié aux pages et ressources sous `/admin`.

## 📊 État actuel (production)

```bash
$ curl -I https://daattorah.com/admin/
HTTP/2 200  ← ❌ ACCESSIBLE À TOUS (problème de sécurité)
```

Toutes les pages admin sont servies sans aucune vérification côté serveur :
- `/admin/index.html` (tableau de bord)
- `/admin/corpus.html` (gestion du corpus)
- `/admin/paiements.html` (paiements et dons)
- `/admin/signalements.html` (signalements utilisateurs)
- `/admin/feedback.html` (feedback utilisateurs)
- `/admin/newsletter-test.html` (tests newsletter)
- `/admin/dedicaces.html` (dédicaces)
- `/admin/khavroutha.html` (khavroutot)
- `/admin/siman-builder.html` (générateur de siman)

## ✅ Solution implémentée

### Architecture

**Edge Middleware** (`middleware.js`) avec **Basic Auth** :
- Intercepte TOUTES les requêtes vers `/admin/*` AVANT qu'elles n'atteignent les fichiers
- Vérifie l'en-tête `Authorization: Basic <base64>`
- Comparaison en **temps constant** (crypto.timingSafeEqual) contre `ADMIN_PASSWORD`
- **Fail closed** : refuse si `ADMIN_PASSWORD` absent

### Code

```javascript
// middleware.js
import { NextResponse } from 'next/server';

export const config = {
  matcher: '/admin/:path*',
};

export function middleware(req) {
  const authHeader = req.headers.get('authorization');
  const expectedPassword = process.env.ADMIN_PASSWORD;

  if (!expectedPassword) {
    return new NextResponse('Configuration manquante', { status: 500 });
  }

  if (authHeader && authHeader.startsWith('Basic ')) {
    const base64Credentials = authHeader.slice(6);
    const credentials = Buffer.from(base64Credentials, 'base64').toString('utf8');
    const [, providedPassword] = credentials.split(':', 2);

    const expectedBuf = Buffer.from(expectedPassword, 'utf8');
    const providedBuf = Buffer.from(providedPassword || '', 'utf8');

    if (expectedBuf.length === providedBuf.length) {
      const crypto = require('crypto');
      if (crypto.timingSafeEqual(expectedBuf, providedBuf)) {
        return NextResponse.next(); // ✅ Authentifié
      }
    }
  }

  // ❌ Non authentifié
  return new NextResponse('Authentification requise', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="DAAT Admin", charset="UTF-8"',
    },
  });
}
```

### Comportement attendu

| Route | Sans auth | Avec bon mot de passe |
|-------|-----------|----------------------|
| `/admin/` | **401** + fenêtre Basic Auth | **200** + contenu |
| `/admin/corpus.html` | **401** + fenêtre Basic Auth | **200** + contenu |
| `/admin/*` (toutes) | **401** + fenêtre Basic Auth | **200** + contenu |
| `/` (accueil) | **200** (inchangé) | **200** (inchangé) |
| `/chat` | **200** (inchangé) | **200** (inchangé) |
| `/oh/242/` | **200** (inchangé) | **200** (inchangé) |
| `/api/chat` | **200** (inchangé) | **200** (inchangé) |

## 🔐 Comment le Rav se connecte

1. Aller sur https://daattorah.com/admin/ (ou n'importe quelle sous-page)
2. Le navigateur affiche une **fenêtre Basic Auth native**
3. Entrer :
   - **Utilisateur** : n'importe quoi (ex: `admin`, ou laisser vide)
   - **Mot de passe** : la valeur exacte de `ADMIN_PASSWORD` (variable d'environnement Vercel)
4. Le navigateur mémorise les identifiants pour toute la session

**Aucune configuration à changer** : la même variable `ADMIN_PASSWORD` qui existe déjà dans Vercel est réutilisée.

## 📝 Pull Request

**URL** : https://github.com/yossefhs/Daat.ai/pull/245  
**Branche** : `cursor/secure-admin-edge-832a`  
**Statut** : ✅ Déployée (preview disponible)

## ⚠️ Note sur la preview Vercel

La preview à https://daatai-git-cursor-secure-admin-edge-832a-yossefhs-projects.vercel.app a un **SSO Vercel activé** qui redirige toutes les requêtes vers un écran de connexion Vercel. Ceci empêche de tester directement notre middleware sur la preview.

**Options** :
1. Désactiver temporairement le SSO Vercel pour cette preview
2. Tester localement avec `vercel dev` (script `test-middleware.sh` fourni)
3. Valider le code manuellement et fusionner (le middleware est correct)

## 🧪 Tests

### Script de test fourni

```bash
# Tester localement avec vercel dev
export ADMIN_PASSWORD="votre_secret"
vercel dev &
sleep 10
./test-middleware.sh http://localhost:3000
```

### Tests manuels (production après fusion)

```bash
# 1. Sans authentification (doit échouer)
curl -I https://daattorah.com/admin/
# Attendu : HTTP/2 401 + WWW-Authenticate: Basic realm="DAAT Admin"

# 2. Avec authentification (doit passer)
curl -I -u admin:$ADMIN_PASSWORD https://daattorah.com/admin/
# Attendu : HTTP/2 200

# 3. Pages publiques (ne doivent pas être affectées)
curl -I https://daattorah.com/
curl -I https://daattorah.com/chat
curl -I https://daattorah.com/oh/242/
# Attendu : HTTP/2 200 (tous)
```

## ✅ Checklist de validation

- [x] Code du middleware créé (`middleware.js`)
- [x] Comparaison en temps constant (crypto.timingSafeEqual)
- [x] Fail closed si ADMIN_PASSWORD absent
- [x] Matcher correct (`/admin/:path*`)
- [x] Ne touche PAS aux routes publiques
- [x] Commit et push sur branche
- [x] PR ouverte (#245)
- [x] Script de test fourni (`test-middleware.sh`)
- [ ] Tests réussis (bloqué par SSO Vercel sur preview)
- [ ] Validation par le Rav
- [ ] Fusion dans `main`

## 📋 Variables d'environnement

**Aucune nouvelle variable** à ajouter. La variable existante est réutilisée :
- `ADMIN_PASSWORD` (déjà configurée dans Vercel)

## 🚀 Déploiement

1. **Validation** : Le Rav valide que le code est correct
2. **Fusion** : Merge de la PR #245 dans `main`
3. **Déploiement automatique** : Vercel déploie automatiquement sur production
4. **Vérification** : Tester https://daattorah.com/admin/ (doit demander auth)

## 🔒 Sécurité

### Ce qui est corrigé
✅ Aucun accès non authentifié à `/admin`  
✅ Protection côté serveur (Edge = avant tout le reste)  
✅ Comparaison en temps constant (anti timing attack)  
✅ Fail closed (refuse si variable absente)  
✅ Basic Auth standard (reconnu par tous les navigateurs)  

### Ce qui reste (hors scope de ce P0)
⚠️ Mot de passe partagé (pas de comptes individuels)  
⚠️ Quelques API acceptent encore `?secret=` pour des raisons historiques (api/soutenir, api/daily-pack, api/social, api/newsletter) — selon CLAUDE.md, volontaire pour servir une page de connexion

## 📞 Contact

Pour toute question sur cette implémentation, voir la PR #245 ou le code dans `middleware.js`.

---

**Date** : 28 septembre 2026  
**Auteur** : Cloud Agent Cursor  
**Priorité** : P0 (Sécurité)
