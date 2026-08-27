# DAAT — Décisions

Format : décision · date · raison · preuve · conséquences.

## D1 — Tuiles des index de section : routes propres au lieu des chemins physiques
- **Date** : S1 (mode growth)
- **Décision** : `sources/{yoreh-deah,orah-haim,nida}/index*.html` (9 fichiers) : `a.href = '../../' + s.path` → mapping section → `/yd/N/`, `/oh-quotidien/N/` (+ suffixe `/he` `/en` par langue). Nida route vers `/yd/N/` (fichiers physiques sous yoreh-deah, aucune route `/nida/:n` n'existe).
- **Raison** : les visiteurs et crawlers atterrissaient sur `/sources/...` (URL non canonique, dupliquée, hors sitemap).
- **Preuve** : grep `a.href` l.154 ×9 ; vercel.json sans redirect `/sources/yoreh-deah/...`.
- **Conséquences** : + redirects 301 `/sources/{yoreh-deah,orah-haim}/siman-N…` → routes (rattrape les URLs déjà crawlées).

## D2 — `/aujourdhui` = redirect 302 vers `/limoud/`
- **Date** : S1
- **Décision** : redirect temporaire (302), pas une page.
- **Raison** : URL quotidienne mémorisable immédiatement utile ; la vraie page « Aujourd'hui » (P2) prendra la place sans casse (302 → remplaçable).
- **Conséquences** : quand la page dédiée existera, retirer le redirect.

## D3 — Compteurs homepage : périmètre nommé plutôt que chiffres fragiles
- **Date** : S1
- **Décision** : og/twitter/JSON-LD ne citent plus « 124 simanim / 3 niveaux » mais les sections réelles (Chabbat, Yoreh De'ah, Orah Haïm quotidien) + « 4 niveaux ». Les « 124 » restants sont scopés « de Chabbat » (exacts).
- **Raison** : le corpus grandit chaque semaine (371 dossiers siman au moment de l'audit) ; un chiffre hardcodé re-deviendrait faux. Interdiction du brief de hardcoder des chiffres périssables.
- **Conséquences** : de vrais compteurs auto-générés depuis `simanim-disponibles.json` restent souhaitables (P1) — après réconciliation du JSON (périmé : yd 32 vs 50 disque).

## D4 — CTA chat : bénéfice utilisateur, pas démo IA
- **Date** : S1
- **Décision** : « Tester l'IA Daat » → « Poser une question de Halakha » (FR/HE/EN, hero + bloc IA).
- **Raison** : exigence explicite du brief produit ; « tester » ne promet aucun bénéfice.
- **Conséquences** : expérience E1 à mesurer dès Web Analytics activé.

## D5 — Pas de régénération de `data/simanim-disponibles.json` cette session
- **Date** : S1
- **Décision** : ne PAS relancer `generate-simanim-index.js` malgré le JSON périmé.
- **Raison** : le build l'a volontairement retiré (commit `6843dcda8` « préserve l'index section-aware ») — le script courant écraserait l'index section-aware. Risque de casse > gain immédiat.
- **Conséquences** : P1 backlog — réconcilier le générateur, puis SSG des listings.

## D6 — vercel.json : point chaud de collision entre sessions
- **Date** : S8
- **Décision** : toute session qui modifie `vercel.json` doit (1) repartir de la version d'`origin/main` fraîchement fetchée, jamais de sa copie locale ; (2) après tout merge touchant ce fichier, vérifier que les règles récentes des autres sessions y sont encore (grep des sources ajoutées ces derniers jours) ; (3) re-tester les URLs clés en prod après déploiement.
- **Raison** : le merge de la session « restauration » (f1193d0e2) a silencieusement écrasé les rewrites `/partenaires` ajoutés 30 min plus tôt → 404 en prod signalé par le Rav. Réparé en 6d4a3e28e (base remote + ré-ajout).
- **Preuve** : `git show f1193d0e2:vercel.json | grep partenaires` → vide, alors que la page HTML était déployée.
- **Conséquences** : routes clés à re-tester après chaque gros merge : /aujourdhui, /partenaires, /oh-quotidien/:n/:page, /yd/:n, /nida/:n.
