# Post quotidien du Daat Yomi — validé d'un clic

Chaque jour d'étude (dimanche → jeudi), vers 6 h (heure de Paris), le site prépare le post du
jour et l'envoie par email pour validation. Rien n'est publié sans un clic.

Code : `api/daily-post.js` (routes), `api/_daily-post.js` (rédaction, vérification,
illustrations, email), `api/_daily-post-view.js` (page de validation), `api/_social-publish.js`
(publication). Cron : `/api/daily-post`, `0 4 * * 0-4` (UTC) dans `vercel.json`.

## Contrôles bloquants (mieux vaut ne rien envoyer qu'un Daat Yomi faux)

Avant toute rédaction (`api/_daily-post-checks.js`), le jour du plan est confronté :
- au **nombre réel de séifim** du siman, lu en direct sur Sefaria (et à `data/seifim-count.json`) ;
- aux **autres journées du même siman** : séifim 1..N couverts une fois et une seule, ≤ 5 par jour ;
- à la **page du calendrier publiée** (`/limoud/jour-NNN.html`) : même jour, siman, séifim ;
- à la **cohérence du plan** : total annoncé = journées réelles.

Un seul écart bloquant → aucun pack : un email « PACK NON PRÉPARÉ » explique ce qui n'a pas pu
être vérifié. Les écarts non bloquants (étiquette de partie fausse, siman étudié en rattrapage)
sont corrigés à l'affichage et signalés en tête de l'email et de la page.

Après rédaction : jour, total, siman, séifim et lien sont contrôlés mécaniquement dans chaque
texte ; chaque illustration est inspectée (texte, personnes, symbole religieux étranger, hors
sujet) et régénérée une fois si besoin, sinon remplacée par un fond sobre.

La date est celle de **Jérusalem**. L'email part à `DAILY_POST_EMAIL` (liste séparée par des
virgules), sinon à `ADMIN_EMAIL` et `daattorah.com@gmail.com` ; il n'est donné pour envoyé que
sur l'identifiant renvoyé par Resend (sinon « EMAIL NON ENVOYÉ » au journal).

## Ce qui se passe chaque matin

1. Le jour, le total, le siman et les séifim viennent de `data/limoud-plan.json`.
2. Claude rédige à partir du texte exact des séifim (Sefaria, Mehaber + Rama) et de la page
   d'étude du site : titre, une carte par séif, « À retenir », un texte par réseau.
3. Un second appel confronte chaque affirmation au texte source : vert, orange ou rouge.
4. OpenAI génère les illustrations (une grande, une par séif), **sans aucun texte**.
5. Un email part vers `DAILY_POST_EMAIL` (sinon `ADMIN_EMAIL`) avec le lien de validation.
6. Dans la page : relire, corriger si besoin (visuel et textes sont modifiables), puis
   **Publier partout**. Le bouton **Partager sur WhatsApp** ouvre le partage du téléphone
   avec l'image et le texte.

Coût estimé : 2 à 3 $ par mois de Claude, environ 2,5 $ par mois d'images (qualité
« medium » pour la grande, « low » pour les vignettes).

## Variables d'environnement (Vercel → Settings → Environment Variables)

| Variable | Rôle | Obligatoire |
|---|---|---|
| `ANTHROPIC_API_KEY`, `RESEND_API_KEY`, `CRON_SECRET`, KV | déjà en place | oui |
| `OPENAI_API_KEY` | illustrations (clé API OpenAI avec paiement activé) | pour les images |
| `DAILY_POST_EMAIL` | destinataires, séparés par des virgules (défaut : `ADMIN_EMAIL` + `daattorah.com@gmail.com`) | non |
| `DAILY_POST_MODEL` | modèle Claude (défaut `claude-sonnet-5-5`, repli `claude-sonnet-4-6`) | non |
| `OPENAI_IMAGE_MODEL`, `DAILY_POST_HERO_QUALITY`, `DAILY_POST_THUMB_QUALITY` | réglages des images | non |
| `FB_PAGE_ID`, `FB_PAGE_TOKEN` | Facebook (page) | par réseau |
| `IG_USER_ID` (+ `IG_ACCESS_TOKEN` facultatif) | Instagram (compte pro relié à la page) | par réseau |
| `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN` | LinkedIn (profil perso : `urn:li:person:…`) | par réseau |
| `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` | X (texte + lien) | par réseau |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Telegram (facultatif) | par réseau |
| `META_GRAPH_VERSION` | version de l'API Meta (défaut `v23.0`) | non |
| `SOCIAL_WEEKLY_ENABLED=1` | réactive l'ancien pilote du mardi (désactivé : il doublerait) | non |

Un réseau s'active dès que ses variables existent ; les autres continuent de fonctionner.
WhatsApp n'a pas d'API de publication pour les groupes : il reste un partage manuel.

## Administration

- Journal : `GET /api/daily-post?action=status` avec `Authorization: Bearer <CRON_SECRET>`.
- Refaire un jour : `GET /api/daily-post?date=AAAA-MM-JJ&force=1` (même en-tête).
- Le lien de l'email porte un jeton propre à la date, dérivé de `CRON_SECRET` : il n'ouvre
  que le post de ce jour-là et ne révèle pas le secret.
- Le jeton LinkedIn expire au bout d'environ 60 jours : le refaire à l'échéance.
