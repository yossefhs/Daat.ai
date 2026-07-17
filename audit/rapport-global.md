# DAAT — Rapport d'audit global (daattorah.com)

> **Statut : audit EN COURS — phase automatique terminée ; revue approfondie = 111 simanim Shabbat sur 124 (lots 1-15, simanim 242-352 contigus), 1040 constats.**
> Ce rapport contient des constats **et** trace les corrections mécaniques déjà appliquées (voir §10). Aucune règle halakhique n'a été modifiée.

## 10. Corrections mécaniques appliquées (sûres, non-halakhiques)

Sur demande explicite (« fais au mieux pour améliorer le site »), après *dry-run* et vérifications :

1. **Ordre du catalogue `/contenu`** : sections réordonnées → Orah Haïm quotidien (1→64) · Yoreh Deah · Nida · Shabbat.
2. **Gershayim ASCII → typographique ״** (`audit/tools/fix_mechanical.py`, règle A) : 68 542 corrections / ~1699 fichiers. Répare **toutes** les meta/JSON-LD cassées (0 restante) ; citations préservées (`ה"שותף`, `ב"ברוך`…).
3. **Coquille סיכות → שיחות** (règle B) : 122 simanim (FR+EN) ; usages légitimes (épingles, siman 301) préservés.
4. **Compteur « 3 niveaux » → « 4 »** (règle C) : 136 index avec 4 cartes ; simanim-pont 304/322 (3 cartes) préservés.

Garde-fous : `audit-simanim.py` **124/124 conformes**, corpus régénéré, `simanim-disponibles.json` préservé (238 simanim — le générateur ne couvre que Shabbat).

**Non corrigé automatiquement (risque) :**
- **Titres `<title>` tronqués** (196 fichiers, `T-TITRES-TRONQUES`) : `og:title` a un format différent → reconstruction non fiable. À régénérer proprement côté générateur.
- **112 commentaires `<!-- à vérifier -->`** : laissés en place — ils constituent la liste de travail du Rav (catalogués dans `artefacts-a-verifier.csv`).
- **Tout le fond halakhique** (Niveau 4, citations, contradictions) : **réservé à la validation du Rav**.

---

*Note historique : la seule modification hors-audit initiale était l'ordre du catalogue `/contenu`.*
> Date de génération : 2026-07-13. Branche : `claude/daattorah-site-audit-tyhabm`.
>
> **Lots 1-15 terminés — simanim 242-352 (contigus, 111 simanim) → 1040 constats de contenu** dans `erreurs-halakha.csv`. Revue en cours vers 353+.
> Les patterns récurrents sont documentés dans **`erreurs-recurrentes.md`** (à lire en priorité). Constat n°1 : le **Niveau 4 « Daat HaRav »** a un appareil analytique (tableaux/chidoushim/למעשה) systématiquement décorrélé du texte-source reproduit sur la même page, avec parfois des **inversions halakhiques** (ex. 249 : jeûne érev Shabbat « interdit » vs « recommandé » ; 261 : allumage « même à bein hashmashot » + Amora erroné רב נחמן/ר' נחמיה).

---

## 0. Avertissement méthodologique (à lire avant tout)

Ce site contient **4 187 pages HTML** dont l'écrasante majorité est du **contenu halakhique trilingue** (Choulhan Aroukh, Orah Haïm). L'audit se décompose en deux natures de contrôles très différentes :

| Nature | Ce qu'on peut affirmer | Couverture actuelle |
|--------|------------------------|---------------------|
| **Automatique / structurel** (inventaire, liens, SEO, hreflang, numérotation de titre, cohérence des chiffres, parité de fichiers) | Fait **foi** : vérifiable mécaniquement, reproductible. | **100 % des pages** |
| **Sémantique / halakhique** (exactitude d'une règle, exactitude d'une citation vs source primaire, exactitude d'une traduction, contradiction entre niveaux) | **Ne peut PAS être tranché mécaniquement.** Un outil peut *signaler des candidats* mais **la confirmation exige la lecture des sources primaires et l'œil du Rav.** | **111 simanim Shabbat sur ~238** (revue approfondie en cours, lots 1-15, simanim 242-352) |

**Règle appliquée partout :** aucune règle halakhique n'est déclarée « fausse » sans source précise ; tout point douteux est marqué **« À vérifier par le Rav »**. Là où la vérification dépasse ce qui est mécaniquement prouvable, la mention explicite est : *« Je ne peux pas vérifier automatiquement — validation rabbinique nécessaire. »*

---

## 1. Inventaire — nombre de pages analysées

**Total : 4 187 pages HTML** (hors `node_modules`), inventoriées dans `audit/inventaire-pages.csv`.

### 1.1 Par langue
| Langue | Pages |
|--------|-------|
| Français (`X.html`, défaut) | 1 439 |
| Hébreu (`X-he.html`) | 1 374 |
| Anglais (`X-en.html`) | 1 374 |

L'écart FR (+65) s'explique par des pages FR sans équivalent HE/EN (voir §5 : Yoreh Deah niveau Lamdan, pages racine techniques).

### 1.2 Par section
| Section | Pages | Nature |
|---------|-------|--------|
| `sources/shabbat` | 1 863 | **Cœur du site** — 124 simanim × (index + 4 niveaux) × 3 langues |
| `sources/orah-haim` | 963 | 64 simanim (« Orah Haïm quotidien ») |
| `sources/yoreh-deah` | 653 | 50 simanim |
| `limoud` | 587 | 194 « jours » d'étude × 3 langues + index |
| `blog` | 72 | 21 articles × 3 langues + index + flux |
| `racine` | 29 | accueil, chat, about, faq, communauté, soutenir, 404… |
| `sources/nida` | 3 | index seul (section en amorce) |
| `auteur` | 3 | biographie du Rav × 3 langues |
| `admin`, `mockup`, `emails`, `autre` | 14 | non publiques / techniques |

### 1.3 Par niveau d'étude (simanim)
| Niveau | Pages |
|--------|-------|
| Index de siman | 736 |
| 1 — Base | 714 |
| 2 — Lamdan | 614 |
| 3 — Synthèse | 714 |
| 4 — Daat HaRav | 564 |

*(L'écart du niveau 2 — Lamdan tient au fait que Yoreh Deah n'a ce niveau qu'en hébreu ; voir §5.)*

### 1.4 Sitemap
- `sitemap.xml` : **4 163 URL**. `sitemap-llm.xml` : 125 URL. Les deux sont déclarés dans `robots.txt`.
- **24 pages hors sitemap**, toutes légitimement exclues : 8 racine techniques (404, offline, poc-corpus…), 8 pages `admin/`, 3 « autre », 1 `emails/`, 2 `mockup/`, 2 fragments `limoud`. **Aucune page de contenu halakhique n'est absente du sitemap.**

---

## 2. Résultats des contrôles automatiques

Détail complet : `audit/erreurs-techniques.csv` (277 lignes).

| Gravité | Nombre |
|---------|--------|
| CRITIQUE | 2 |
| IMPORTANTE | 50 |
| MOYENNE | 225 |

### 2.1 Ce qui est SAIN (résultats positifs notables)
- **Liens internes : 129 592 liens vérifiés, 4 cassés** (0,003 %) — et les 4 sont dans `admin/index.html` (page non publique). *Le maillage interne du site public est intact.*
- **hreflang : 0 incohérence** sur les pages `sources/` — chaque alternative FR/HE/EN pointe vers **le même siman et le même niveau** (test de l'étape 7 réussi).
- **Accessibilité images : 0 balise `<img>` sans `alt`** sur 4 187 pages.
- **Structure Hn : 0 page avec plusieurs `<h1>`** ; les 3 « sans H1 » sont des fragments de bannière (`data/.banner-snippets/`), pas des pages.
- **Numérotation des titres hébraïques : 0 erreur de gematria** après correction — les 124 simanim Shabbat passent le garde-fou `scripts/audit-simanim.py` (124/124 conformes).

### 2.2 Anomalies confirmées (automatiques)

**CRITIQUE (2) — mais impact limité au `<title>` (le contenu, lui, est correct) :**
- `sources/shabbat/siman-243/niveau-4-daat-harav.html` et `.../siman-246/...` : la balise `<title>` affiche **« Siman 242 »** alors que canonical, `<h1>` (רמ״ג / רמ״ו), `og:title` et les versions HE/EN sont corrects. → Copier-coller du titre. Reclassé **IMPORTANTE** en pratique (aucune erreur de contenu, seulement l'onglet du navigateur / SEO). *À corriger.*

**IMPORTANTE (50) — cluster unique : Yoreh Deah, niveau 2 (Lamdan) :** voir §5.1. Les 50 pages `lang="he"` sur une URL française relèvent du même choix structurel (niveau Lamdan de Yoreh Deah rédigé en hébreu uniquement).

**MOYENNE (225) :**
- **hreflang manquant (150)** = 50 pages Yoreh Deah Lamdan × 3 → même cause structurelle (§5.1).
- **Titres dupliqués (73)** : deux origines réelles — (a) le bug 242/243/246 ci-dessus ; (b) sur Yoreh Deah, `index.html` et `niveau-1-base.html` d'un même siman partagent parfois le même `<title>` (SEO : titres à différencier par niveau).
- **canonical absent (2)** : `offline.html`, `poc-corpus.html` (pages techniques).

**Titres non traduits (borné, IMPORTANTE) :**
- **Simanim 304 et 322** (les deux simanim « pont » sans niveau 4) : le `<title>` des pages **`index-en.html` et `index-he.html` est resté en français**. Détail dans `audit/titres-non-traduits.csv`. Le reste du site (1 142 autres triples testés) a des titres correctement localisés.

---

## 3. Chronologie, calculs et mesures (étape 5)

Scan complet dans `audit/chronologie-occurrences.csv` (6 311 phrases porteuses de zmanim) et `audit/chronologie-risques.csv` (108 alertes heuristiques).

**Conclusion de la passe automatique :** les 108 alertes heuristiques sont **très majoritairement des faux positifs** (ex. « interdite pour **toujours** » en Yoreh Deah capté comme « durée universelle » ; « בין השמשות » et « תוספת שבת » cités *ensemble* dans un tableau qui les distingue justement correctement).

**Point positif notable :** le traitement des zmanim de Shabbat (siman 261, blog « bougies ») distingue explicitement les shitot et précise que *« les 18 minutes proviennent du minhag ashkénaze codifié par les Aharonim, pas du Mehaber »* — ce qui est le bon niveau de nuance. **Aucune confusion grossière bein hashmashot / tosefet / shita détectée automatiquement.**

⚠️ **Réserve :** l'exactitude *fine* des valeurs (13,5 / 18 / 72 min, degrés) et leur bonne attribution (Guéonim vs Rabbénou Tam vs Admour HaZaken) **relève de la validation rabbinique** — l'échantillon approfondi (siman 293) est en cours.

---

## 4. Erreurs par gravité (synthèse provisoire)

| Gravité | Automatique (confirmé) | Sémantique (en cours) |
|---------|------------------------|------------------------|
| CRITIQUE | 0 erreur de contenu ; 2 titres erronés | à établir par la revue + le Rav |
| IMPORTANTE | 52 (cluster YD Lamdan + titres 304/322) | à établir |
| MOYENNE | ~223 (SEO/hreflang) | à établir |
| MINEURE | orthographe/ponctuation : non encore ratissé | à établir |

---

## 5. Constats structurels marquants

### 5.1 Yoreh Deah — niveau 2 (Lamdan) hébreu uniquement
Les 50 simanim de Yoreh Deah ont un niveau Lamdan **présent seulement en un fichier `niveau-2-lamdan.html` rédigé en hébreu** (`<html lang="he">`), **sans** variantes `-he`/`-en` ni balises hreflang. Conséquences mécaniques : 50 « lang incohérent », 150 « hreflang manquant », 52 « parité langue manquante ».
→ **Question au Rav / à l'auteur : est-ce un choix assumé** (le Lamdan de Yoreh Deah reste en hébreu) **ou un chantier de traduction inachevé ?** Impact SEO/accessibilité réel mais non halakhique. *À trancher, non une erreur en soi.*

### 5.2 Simanim 304 et 322 (« ponts », sans Daat HaRav)
Traités à part dans le repo (pas de niveau 4 car l'Admour HaZaken ne les a pas rédigés). C'est là que se logent les seules anomalies de titre non traduit. → Vérifier que ces deux simanim ont bien reçu le même soin de localisation que les autres.

---

## 6. Pages non analysées sémantiquement

`audit/pages-non-verifiees.csv` : le gros des pages de contenu n'a reçu que les contrôles automatiques. La revue halakhique/traduction/niveaux en profondeur couvre à ce stade **27 simanim de Shabbat (242-267 contigus + 293)**, lot 4 (268-274) en cours — analyse par agents dédiés, consignée dans `erreurs-halakha.csv` (151 constats).

---

## 7. Sources impossibles à vérifier automatiquement

**Par nature, toutes les affirmations halakhiques renvoyant à une source primaire** (Guemara, Rambam, Choulhan Aroukh, Rama, Choulhan Aroukh HaRav, Siddour de l'Admour HaZaken, Michna Beroura). Un script peut vérifier *qu'une référence est bien formée et que le siman cité existe*, **jamais** que *la source dit bien ce qu'on lui fait dire*. → **Validation rabbinique nécessaire** pour cet axe.

---

## 8. Recommandations (ordre conseillé des corrections)

1. **Corriger les 2 `<title>` « Siman 242 »** des simanim 243 et 246 (niveau 4, FR) — trivial, sans risque.
2. **Localiser les `<title>` HE/EN des simanim 304 et 322** — trivial.
3. **Trancher le statut de Yoreh Deah Lamdan** (traduire, ou assumer l'hébreu et ajouter les hreflang/`lang` cohérents). Décision éditoriale.
4. **Différencier les `<title>` par niveau** là où `index` et `base` partagent le même (Yoreh Deah surtout) — SEO.
5. **Ajouter canonical** à `offline.html` / `poc-corpus.html` (mineur).
6. **Lancer la revue sémantique approfondie** siman par siman (halakha, citations, traduction, cohérence des niveaux) — **par lots, avec validation du Rav** sur chaque point douteux. C'est le gros du travail restant et il ne peut être ni automatisé ni tranché sans le Rav.

---

## 9. Fichiers produits par l'audit

| Fichier | Contenu |
|---------|---------|
| `audit/inventaire-pages.csv` | Inventaire des 4 187 pages (étape 1) |
| `audit/erreurs-techniques.csv` | 277 anomalies techniques/SEO/numérotation |
| `audit/liens-casses.csv` | Liens internes cassés (4) |
| `audit/parite-langues-manquantes.csv` | Pages FR sans équivalent HE/EN (104) |
| `audit/hreflang-incoherences.csv` | Incohérences de cible hreflang (0) |
| `audit/chronologie-occurrences.csv` | 6 311 phrases avec termes de zmanim |
| `audit/chronologie-risques.csv` | 108 alertes heuristiques (à filtrer) |
| `audit/titres-non-traduits.csv` | Titres EN/HE non localisés (304, 322) |
| `audit/pages-non-verifiees.csv` | 4 096 pages non revues sémantiquement |
| `audit/erreurs-critiques.md` | Erreurs critiques isolées |
| `audit/erreurs-halakha.csv` · `erreurs-traduction.csv` · `divergences-langues.csv` | À remplir par la revue sémantique + le Rav |
| `audit/tools/*.py` | Scripts d'audit (lecture seule) reproductibles |
