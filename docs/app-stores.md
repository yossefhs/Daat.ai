# Publier DAAT sur le Play Store et l'App Store

État au 25 octobre 2026 : **la PWA est prête et en production** — manifest complet
(`manifest.webmanifest`, icônes 192/512 + maskable, raccourcis Catalogue/Assistant),
service worker network-first avec page hors-ligne (`sw.js`, enregistré par
`assets/js/pwa.js`), thème navy/crème. Daattorah.com est déjà installable depuis le
navigateur (Android : « Installer l'application » ; iPhone : Partager → « Sur l'écran
d'accueil »). Les apps stores ci-dessous **emballent cette PWA** : tout le contenu et
le chat restent servis par le site — pas de second code à maintenir.

## Voie recommandée : PWABuilder (gratuit, sans Mac pour Android)

[pwabuilder.com](https://www.pwabuilder.com) est l'outil de Microsoft qui transforme
une PWA en paquets stores. Entrer `https://daattorah.com` → il audite le manifest
(déjà conforme) → boutons « Package for stores ».

### Play Store (Android) — ~1 h, 25 $ une seule fois

1. Créer le compte développeur : [play.google.com/console](https://play.google.com/console) (25 $, une fois).
2. Sur PWABuilder : **Android** → renseigner
   - Package ID : `com.daattorah.app` (déjà inscrit dans `.well-known/assetlinks.json`)
   - App name : `Daat Torah` · Theme : `#1A1F3A` · Background : `#FAF6EE`
   - Signing key : « Create new » (télécharger et **conserver précieusement** le zip du keystore)
   → télécharger le `.aab`.
3. Play Console → Créer l'application → importer le `.aab` (test interne d'abord).
4. Play Console → Configuration → **Signature des applications** → copier
   l'**empreinte SHA-256** du certificat → la donner à Claude (ou remplacer soi-même
   `REMPLACER_PAR_EMPREINTE_SHA256_PLAY_APP_SIGNING` dans `.well-known/assetlinks.json`
   et fusionner) : c'est ce qui fait ouvrir l'app en plein écran, sans barre de navigateur.
5. Remplir la fiche (textes prêts ci-dessous), captures d'écran (le studio
   `/api/daily-pack` et les pages de siman font d'excellentes captures), classification
   contenu, politique de confidentialité : `https://daattorah.com/confidentialite.html`
   (à créer si absente — demander à Claude).
6. Envoyer en examen (quelques jours).

### App Store (iOS) — 99 $/an + un Mac (ou un service cloud)

Apple exige un compte [developer.apple.com](https://developer.apple.com) (99 $/an) et
une compilation Xcode (Mac physique, ou Mac cloud type MacStadium/Codemagic).

1. PWABuilder : **iOS** → télécharger le projet Xcode.
2. Sur Mac : ouvrir le projet, signer avec le compte développeur, archiver, envoyer
   via App Store Connect.
3. ⚠️ **Règle Apple 4.2** : Apple refuse les simples sites emballés. L'argument à
   mettre dans la note de révision ET dans l'app : notifications quotidiennes
   **Daat Yomi** (programme d'étude du jour), mode hors-ligne du siman en cours,
   raccourcis natifs. Si la v1 est refusée, la v2 avec notifications push passe
   (voir ci-dessous).

### Prochaine étape qui change tout : les notifications push Daat Yomi

Le Web Push fonctionne dans la PWA installée (Android, et iPhone depuis iOS 16.4).
À construire côté site (Claude peut le faire entièrement) :
- bouton « M'abonner au Daat Yomi » → abonnement push stocké en KV ;
- le cron quotidien envoie « 📅 Jour N — Siman X, séifim a-b » avec le lien ;
- c'est AUSSI l'argument décisif pour Apple (valeur native réelle) et le meilleur
  moteur de rétention de l'app.

## Textes de fiche store (prêts à coller)

**Nom** : Daat Torah — Halakha en français
**Sous-titre / courte (80 car.)** : Le Choulhan Aroukh étudié par siman, en 4 niveaux, du débutant au talmid hakham.
**Description longue** :
> Daat Torah (daattorah.com) est la plateforme d'étude du Choulhan Aroukh en
> français, initiée par le Rav Yossef Haim Samama.
>
> • Plus de 500 simanim étudiés : Orah Haïm (dont les lois de Chabbat et Érouvin)
>   et Yoré Déa — texte hébreu, traduction française fidèle, explications.
> • 4 niveaux pour chaque siman : Base (texte + traduction), Lamdan (pilpoul des
>   Richonim et Aharonim), Synthèse (révision structurée), Daat HaRav (la chitah
>   de l'Admour HaZaken).
> • Daat Yomi : le programme d'étude quotidien — quelques séifim par jour,
>   5 jours par semaine.
> • L'assistant d'étude Daat : posez votre question, il répond à partir des
>   sources, avec les références.
> • Trilingue : français, hébreu, anglais.
>
> L'étude ne remplace pas la consultation d'un Rav pour la pratique.

**Mots-clés** : halakha, choulhan aroukh, torah, chabbat, étude juive, daf yomi, judaïsme
**Catégorie** : Éducation (secondaire : Livres/Références)
**Confidentialité** : l'app n'exige pas de compte ; le chat utilise un identifiant
de session ; e-mail uniquement si l'utilisateur s'inscrit (OTP). Pas de publicité.

## Répartition des rôles

| Étape | Qui |
|-------|-----|
| PWA (manifest, SW, icônes, offline) | ✅ fait, en production |
| `assetlinks.json` (structure) | ✅ fait — empreinte à coller après création Play |
| Paquet Android `.aab` | Toi via PWABuilder (10 min) |
| Comptes stores (25 $ / 99 $ an) | Toi (paiement) |
| Fiches stores, captures | Textes ✅ ci-dessus ; captures : demander à Claude |
| Empreinte SHA-256 dans assetlinks | Claude (me coller l'empreinte) |
| Notifications push Daat Yomi | Claude (sur demande — recommandé avant l'App Store) |
| Projet iOS + soumission | Toi (Mac/compte) avec le paquet PWABuilder |
