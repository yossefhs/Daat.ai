# DAAT — Pilote automatique réseaux sociaux (sans service tiers)

Le site publie **tout seul**, chaque **mardi 09:10 UTC**, le « siman de la semaine »
(242 → 365, même série que la newsletter du dimanche) sur les réseaux configurés —
directement via les **APIs officielles**, sans OmniSocials ni abonnement.

- Moteur : `api/social.js` + `api/_social-content.js` (cron dans `vercel.json`).
- Une plateforme est **activée dès que ses variables d'environnement existent** dans
  Vercel. Aucune variable → le cron ne fait rien (sans erreur).
- Curseur KV `social:weekly:cursor` (défaut 242), anti-doublon quotidien, journal
  `social:log` (30 derniers runs).
- Si le siman a un article de blog, le post pointe vers l'article ; sinon vers `/oh/N/`.

## Activer les plateformes (une fois, ~15 min chacune)

### Facebook (page DAAT)
1. https://developers.facebook.com → créer une app (type Business).
2. Outil **Graph API Explorer** → générer un **Page Access Token** avec
   `pages_manage_posts` + `pages_read_engagement`, puis l'échanger en **long-lived**
   (60 j) via `/oauth/access_token?grant_type=fb_exchange_token`. Un token de page
   issu d'un token utilisateur long-lived **n'expire pas**.
3. Vercel → `FB_PAGE_ID` (id numérique de la page) + `FB_PAGE_TOKEN`.

### Instagram (compte pro relié à la page FB)
1. Le compte IG doit être **Professionnel** et relié à la page Facebook.
2. Même app Meta ; le token page suffit avec `instagram_basic` + `instagram_content_publish`.
3. Vercel → `IG_USER_ID` (IG Business Account ID, via `GET /{page-id}?fields=instagram_business_account`).
   `IG_ACCESS_TOKEN` optionnel (sinon `FB_PAGE_TOKEN` est utilisé).
   L'image publiée = `assets/img/og/siman-N.png` (déjà généré pour les 124 simanim).

### LinkedIn (page DAAT)
1. https://developer.linkedin.com → créer une app rattachée à la page DAAT →
   demander le produit **Community Management API** (posting).
2. OAuth : obtenir un access token avec `w_organization_social` (admin de la page).
3. Vercel → `LINKEDIN_ACCESS_TOKEN` + `LINKEDIN_AUTHOR_URN`
   (`urn:li:organization:<id>` — l'id est dans l'URL admin de la page).
   ⚠️ Token LinkedIn : validité ~60 j → à régénérer périodiquement.

### X (Twitter)
1. https://developer.x.com → projet + app (le plan **Free** permet de poster, quota limité).
2. App permissions : **Read and write** → générer les 4 clés OAuth 1.0a.
3. Vercel → `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`.

### Telegram (canal DAAT) — le plus simple, 3 min
1. @BotFather → `/newbot` → récupérer le token.
2. Créer un canal, ajouter le bot comme **administrateur**.
3. Vercel → `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (`@nom_du_canal` ou id `-100…`).

### WhatsApp
Pas d'API officielle pour poster dans un groupe → reste **manuel**
(texte prêt chaque semaine via `?action=preview`).

## Piloter / vérifier (remplace SECRET par `CRON_SECRET`)
- Plateformes actives : `https://daattorah.com/api/social?action=platforms&secret=SECRET`
- **Prévisualiser** les posts du prochain siman (rien n'est publié) :
  `https://daattorah.com/api/social?action=preview&secret=SECRET`
- **Publier maintenant** (avance le curseur) :
  `https://daattorah.com/api/social?action=force&secret=SECRET`
- État (curseur, dernier envoi, journal) :
  `https://daattorah.com/api/social?action=status&secret=SECRET`
- **Le pack du jour** (posts à copier-coller soi-même — angle tournant, appel au
  soutien en rotation ; à mettre en favori sur le téléphone) :
  `https://daattorah.com/api/daily-pack?secret=SECRET` (`&siman=N`, `&day=0..6`, `&format=json`)

## Sécurité & garde-fous
- Contenu 100 % dérivé du corpus (titre du siman + liens) — **aucun psak généré**,
  disclaimer « consulte ton Rav » dans chaque post.
- Un envoi max par jour ; le curseur n'avance que si au moins une plateforme a publié.
- Échec d'une plateforme = loggé, n'empêche pas les autres.
- Rotation des tokens : LinkedIn ~60 j ; Meta long-lived page token sans expiration ;
  X/Telegram stables.
