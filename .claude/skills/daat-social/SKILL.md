---
name: daat-social
description: Moteur de contenu social DAAT — transforme un siman du corpus daattorah.com en kit de publication multi-plateforme (LinkedIn, Instagram, Facebook, X…) dans la voix de DAAT, puis le planifie/publie via OmniSocials (MCP). Utiliser quand l'utilisateur veut « publier le siman de la semaine », « faire un post », « alimenter les réseaux », « le contenu social », ou booster la présence en ligne de DAAT.
---

# DAAT — Moteur de contenu social

Transforme **un siman déjà rédigé** (corpus `daattorah.com`, 124 simanim × 4 niveaux ×
3 langues) en un **kit de publication multi-plateforme** prêt à programmer, dans la
voix de DAAT, puis le **publie/planifie via OmniSocials**.

> **Principe fondateur** : on ne *crée* pas de nouveau contenu halakhique. On
> **reformate** du contenu déjà validé. Claude n'invente **jamais** de psak.

## Quand utiliser ce skill
- « Publie le siman de la semaine », « fais un post sur le siman 247 »
- « Alimente les réseaux », « prépare le contenu social », « planifie la semaine »
- Toute demande de booster la présence sociale de DAAT.

## Pré-requis : OmniSocials connecté à Claude
La publication passe par **OmniSocials** (10 $/mo, 10 plateformes, OAuth). Voir
`references/omnisocials-setup.md`. Si le MCP OmniSocials n'est **pas** disponible
dans la session, **générer quand même le kit complet** et le présenter pour copier-
coller manuel + indiquer comment connecter OmniSocials.

## Workflow (toujours dans cet ordre)

### 1. Choisir le siman
- Numéro donné → l'utiliser. Sinon « siman de la semaine » → demander, ou prendre
  le prochain non encore publié (tenir une trace dans `data/social-log.json` si présent).
- Lier au **calendrier juif** si pertinent (paracha / fête à venir) pour l'accroche.

### 2. Lire la source (NE PAS inventer)
- `data/simanim/siman-{N}.json` → titre, sous-titre, keywords, descriptions des 4 niveaux, URLs.
- `sources/shabbat/siman-{N}/niveau-1-base.html` → le contenu accessible (traduction,
  concepts-clés, cas pratiques modernes). C'est la **matière première** des posts.
- Citer uniquement ce qui est dans la source.

### 3. Générer le kit (français d'abord — voir §Langue)
Produire **une variante adaptée par plateforme** (jamais le même texte copié-collé —
best practice 2026). Respecter les formats de `references/platform-specs.md`.
Toujours inclure :
- Un **lien** vers la page du siman : `https://daattorah.com/oh/{N}/base` (ou `/lamdan`,
  `/synthese`, `/daat-harav`, ou `/oh/{N}/` pour la vue d'ensemble).
- Le **visuel** : `assets/img/og/siman-{N}.svg` (le générer via
  `node scripts/generate-og-image.js --siman {N}` s'il manque).
- Un **hashtag set** sobre et pertinent (voir specs).

### 4. Garde-fous halakhiques (NON négociables)
- **Jamais de psak / décision pratique tranchée.** Toujours présenter « ce que dit la
  source » et renvoyer à un Rav pour le `lemaasseh`.
- Inclure, quand un cas pratique est mentionné, une formule du type :
  *« Pour la pratique, consulte ton Rav. »*
- Ton : sérieux, respectueux, pédagogique. Pas de putaclic, pas d'émoji à outrance.
- Translittération cohérente (Shabbat, halakha, Choulhan Aroukh, Admour HaZaken…).
- Le niveau 4 (Daat HaRav / Habad) : le présenter comme la chitah de l'Admour HaZaken,
  sans présenter le minhag Habad comme obligatoire pour tous.

### 5. Validation humaine (par défaut)
Présenter le kit complet à l'utilisateur **avant toute publication**. Attendre un « OK »
explicite. Ne publier directement (full-auto) **que** si l'utilisateur l'a demandé.

### 6. Publier / planifier via OmniSocials
Une fois validé, utiliser les outils MCP OmniSocials pour **programmer** (pas forcément
publier dans l'instant) sur les plateformes choisies, aux **heures optimales** (voir
specs). Proposer d'étaler sur la semaine (1 plateforme/jour) plutôt que tout d'un coup.
Après programmation, **journaliser** dans `data/social-log.json` (siman, date, plateformes).

## Voix & charte DAAT
- **Identité** : דעת — דעת התורה לעומקה. Initiée par le **Rav Yossef Haim Samama**.
- **Mission** : rendre l'étude rigoureuse de la halakha accessible en français,
  du débutant au Talmid Chakham. Choulhan Aroukh par siman, 4 niveaux.
- **Couleurs** : navy `#1A1F3A`, or `#C5A55A`, crème `#FAF6EE`.
- **Polices** : Frank Ruhl Libre + Cormorant Garamond.
- **Signature douce** : renvoyer vers le chat IA Daat et la newsletter (« un siman
  chaque dimanche ») quand c'est naturel — sans spammer.

## Langue
- **Français d'abord** (public principal). Rôder le pipeline en FR.
- HE / EN uniquement si l'utilisateur le demande (le corpus existe en 3 langues :
  `niveau-1-base-he.html`, `niveau-1-base-en.html`).

## Au-delà des réseaux (proposer, ne pas imposer)
Le même kit nourrit d'autres canaux — le mentionner si pertinent :
- **Newsletter** (déjà en prod : Resend, `api/newsletter.js`, « un siman/dimanche »).
- **Blog** `/blog/` (en prod — 13 articles AEO × 3 langues, voir `docs/STRATEGIE-CROISSANCE.md`) :
  l'article long AEO dont les posts sociaux sont des extraits. C'est le plus gros levier SEO.

## Références
- `references/platform-specs.md` — formats, longueurs, ton et heures par plateforme.
- `references/omnisocials-setup.md` — connecter OmniSocials à Claude (MCP / Agent Skill).
