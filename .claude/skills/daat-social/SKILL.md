---
name: daat-social
description: Moteur de contenu social DAAT — donne en une commande le « pack du jour » (posts prêts à copier-coller pour tous les réseaux), pilote la publication automatique du site (api/social.js, cron autonome sans service tiers) et génère des kits sur-mesure (LinkedIn, Instagram, Facebook, X, Telegram, WhatsApp) dans la voix de DAAT à partir du corpus daattorah.com. Utiliser quand l'utilisateur veut « le pack du jour », « quoi poster aujourd'hui », « donne-moi des posts », « publier le siman de la semaine », « faire un post », « alimenter les réseaux », « mettre le blog en avant », « vérifier les envois sociaux », ou booster/monétiser la présence en ligne de DAAT.
---

# DAAT — Moteur de contenu social (v2, autonome)

Le site publie **tout seul** : `api/social.js` + cron Vercel (**mardi 09:10 UTC**)
postent le « siman de la semaine » (série 242 → 365, synchronisée avec la newsletter
du dimanche) **directement via les APIs officielles** (Facebook, Instagram, LinkedIn,
X, Telegram). Aucune session Claude ni service tiers requis.

Ce skill est le **copilote** de ce moteur : vérifier son état, prévisualiser/forcer un
envoi, et produire des **posts sur-mesure** (campagnes, fêtes, annonces) quand le
gabarit automatique ne suffit pas.

> **Principe fondateur inchangé** : on ne crée pas de halakha. On reformule du contenu
> déjà validé. Jamais de psak ; toujours « pour la pratique, consulte ton Rav ».

## ⚡ Mode « PACK DU JOUR » (le pilote quotidien — à privilégier)

Quand l'utilisateur veut « quoi poster aujourd'hui / le pack du jour / des posts »,
la voie **rapide et sans gaspiller de tokens** est le générateur déterministe.

**En production (self-service, zéro session Claude)** — l'URL à mettre en favori sur
son téléphone (remplacer SECRET par CRON_SECRET) :

```
https://daattorah.com/api/daily-pack?secret=SECRET            # siman de la semaine, angle du jour
https://daattorah.com/api/daily-pack?secret=SECRET&siman=253  # siman précis
…&day=5        # forcer l'angle (0=dim … 6=sam)   ·   …&format=json  # brut
```

**En local / session** (même moteur, `api/_pack.js`) :

```bash
node scripts/pack-du-jour.js --siman 253                 # pack texte, prêt à copier
node scripts/pack-du-jour.js --siman 253 --html pack.html # + page mobile, boutons « Copier »
```

Il produit **8 blocs** ancrés dans la source réelle (titre du siman, numéro hébreu,
sous-titre et concepts extraits du corpus `data/corpus-shabbat.json`, liens canoniques,
article de blog si présent) :
① accroche du jour · ② LinkedIn · ③ fil X/Bluesky · ④ Instagram (caption + carrousel) ·
⑤ Facebook · ⑥ message communauté WhatsApp/Telegram · ⑦ **appel au soutien qui tourne**
(dédicace / don 18 € / mécénat / chat / newsletter — jamais deux fois le même d'affilée).

L'**angle du jour** change chaque jour (7 angles) → poster tous les jours ne lasse pas.

L'enrichissement (sous-titre + concepts réels du siman) est **automatique** — extrait
du corpus, zéro invention. **Rôle du skill par-dessus le moteur :**
1. Lancer le script (ou donner l'URL prod) pour le siman voulu.
2. Aller **plus loin** si demandé : lire `sources/shabbat/siman-{N}/niveau-1-base.html`
   pour un post événementiel, une fête, une campagne (ne jamais inventer — citer la source).
3. Livrer prêt à copier-coller (ou envoyer le `--html` à l'utilisateur pour poster au doigt).

Détails, angles, rotation monétisation et calendrier : `references/pack-du-jour.md`.

## Architecture (qui fait quoi)
- **Automatique** : `api/social.js` (publication) + `api/_social-content.js` (textes
  par plateforme, générés depuis `data/simanim/…` + `BLOG_BY_SIMAN`). État en KV
  (`social:weekly:cursor`, `social:log`). Setup des jetons : `references/autopilot.md`
  (copie de `docs/social/autopilot.md`).
- **Sur-mesure (ce skill)** : kits artisanaux multi-plateformes, packs de lancement
  (`docs/social/launch-pack*.md` FR/HE/EN), posts événementiels.

## Opérations courantes (URLs admin — remplacer SECRET par CRON_SECRET)
- **Pack du jour (à poster soi-même)** : `https://daattorah.com/api/daily-pack?secret=SECRET`
- État / journal : `https://daattorah.com/api/social?action=status&secret=SECRET`
- Prévisualiser le prochain envoi : `…?action=preview&secret=SECRET`
- Publier maintenant : `…?action=force&secret=SECRET`
- Plateformes actives : `…?action=platforms&secret=SECRET`

Si l'utilisateur demande « est-ce que ça a été envoyé ? » → lui donner l'URL `status`
(le skill n'a pas accès au KV depuis une session).

## Workflow pour un post SUR-MESURE
1. **Choisir le sujet** : numéro de siman donné, ou lien avec le calendrier juif
   (paracha / fête) pour l'accroche.
2. **Lire la source** (ne PAS inventer) : `data/simanim/siman-{N}.json` (titleFr,
   numberHe) + `sources/shabbat/siman-{N}/niveau-1-base.html` (concepts, cas pratiques).
   Citer uniquement ce qui est dans la source.
3. **Générer une variante par plateforme** (jamais de copié-collé inter-réseaux) selon
   `references/platform-specs.md`. Toujours : lien `https://daattorah.com/oh/{N}/` ou
   l'article `/blog/…` s'il existe, visuel `assets/img/og/siman-{N}.png`, hashtags sobres.
4. **Garde-fous** (non négociables) : pas de psak tranché ; disclaimer « consulte ton
   Rav » sur tout cas pratique ; ton sérieux, pas de putaclic ; niveau 4 = chitah de
   l'Admour HaZaken, jamais présentée comme obligatoire pour tous.
5. **Validation humaine** avant toute publication ; puis au choix :
   - le donner à copier-coller,
   - ou l'injecter dans le moteur (modifier `api/_social-content.js` / déclencher `force`).

## Voix & charte DAAT
- Identité : דעת — דעת התורה לעומקה · initié par le **Rav Yossef Haim Samama**.
- Couleurs navy `#1A1F3A` · or `#C5A55A` · crème `#FAF6EE` ; Frank Ruhl Libre + Cormorant Garamond.
- Signature douce : renvoyer vers le chat IA Daat, la newsletter (« le siman du
  dimanche ») et le groupe WhatsApp `https://chat.whatsapp.com/LQT3IMwjNiZEARC7lxqmv1` —
  sans spammer.
- Langue : **français d'abord** ; HE/EN sur demande (corpus trilingue, packs
  `launch-pack-he.md` / `launch-pack-en.md`).

## Cas particuliers
- **WhatsApp** : pas d'API de groupe → fournir le texte prêt (vendredi avant Shabbat).
- **OmniSocials (optionnel, hérité)** : si son MCP est connecté dans la session, il
  peut servir pour de la programmation fine multi-créneaux — voir
  `references/omnisocials-setup.md`. Ce n'est **plus** le chemin par défaut.

## Références
- `references/pack-du-jour.md` — **playbook quotidien** : 7 angles, rotation monétisation, calendrier hebdo, boucle de croissance.
- `references/autopilot.md` — moteur autonome : jetons, URLs admin, sécurité.
- `references/platform-specs.md` — formats, tons, heures par plateforme.
- `references/omnisocials-setup.md` — option héritée.
