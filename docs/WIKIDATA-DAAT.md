# 🌐 Brouillon Wikidata — entité « DAAT »

> Document de travail à utiliser pour créer la fiche Wikidata de **daattorah.com**.
> Une fois créée et acceptée, elle sera lue par Google (Knowledge Graph), Siri,
> Alexa, ChatGPT, Claude et Perplexity → **knowledge panel** possible.
>
> Temps estimé : **20-30 minutes**, navigateur uniquement.
> Pas besoin d'autorisation préalable — la création est ouverte (compte gratuit sur wikidata.org).

---

## 🎯 Avant de commencer

1. **Crée un compte** sur https://www.wikidata.org → bouton « Create account » en haut à droite. Email + mot de passe, c'est tout.
2. **Active la langue française** dans tes préférences (icône utilisateur → Preferences → Internationalisation → ajouter "fr" + "he" en plus de "en"). Wikidata est multilingue, ça aide.
3. **Garde ce document ouvert** dans un onglet à côté.

---

## 📝 Étape 1 — Créer l'item

URL : https://www.wikidata.org/wiki/Special:NewItem

Remplis le formulaire :

| Champ | Valeur |
|---|---|
| **Language** | English (par défaut) |
| **Label** | `DAAT` |
| **Description** | `online study platform of the Shulchan Aruch (Hilchot Shabbat), in French, Hebrew, and English` |
| **Aliases** | `Daat Torah` · `daattorah` · `daattorah.com` |

Clique **Create**. L'item reçoit un identifiant `Q123456789` (Wikidata te donne un numéro neuf). **Note-le.**

### Ajoute les versions française et hébraïque

Une fois l'item créé, dans l'encadré « Language » en haut :

**Français** (clique « add label » sous fr) :
- Label : `DAAT`
- Description : `plateforme en ligne d'étude du Choulhan Aroukh (Hilkhot Shabbat), en français, hébreu et anglais`
- Aliases : `Daat Torah` · `Daat (plateforme)` · `daattorah` · `דעת תורה`

**עברית** (clique « add label » sous he) :
- Label : `דעת`
- Description : `פלטפורמת לימוד מקוונת של שולחן ערוך, הלכות שבת — בצרפתית, עברית ואנגלית`
- Aliases : `דעת תורה` · `DAAT` · `daattorah`

---

## 📐 Étape 2 — Ajouter les statements (propriétés)

Sur la page de ton item, à droite, clique « **+ add statement** ». Pour chaque ligne ci-dessous, cherche la propriété (P) par son nom anglais dans le champ de recherche.

### A — Identité fondamentale

| # | Propriété | Valeur | Comment chercher |
|---|---|---|---|
| 1 | **instance of** (P31) | `website` | tape `website`, choisis Q35127 |
| 2 | **instance of** (P31) | `educational organization` | tape `educational organization`, choisis Q2385804 |
| 3 | **instance of** (P31) | `Internet encyclopedia` ou `educational website` | optionnel |

> 💡 Mettre 2-3 *instance of* est normal : c'est à la fois un site, une organisation, et un projet éducatif.

### B — Thème et contenu

| # | Propriété | Valeur |
|---|---|---|
| 4 | **main subject** (P921) | `Shulchan Aruch` (Q620890) |
| 5 | **main subject** (P921) | `halakha` (Q177856) |
| 6 | **main subject** (P921) | `Shabbat` (Q9326) |
| 7 | **main subject** (P921) | `Orach Chayim` (Q3320348) |
| 8 | **genre** (P136) | `religious text` ou `Jewish religious literature` |
| 9 | **part of** (P361) | `Judaism` (Q9268) |

### C — Langues

| # | Propriété | Valeur |
|---|---|---|
| 10 | **language of work or name** (P407) | `French` (Q150) |
| 11 | **language of work or name** (P407) | `Hebrew` (Q9288) |
| 12 | **language of work or name** (P407) | `English` (Q1860) |

### D — Personnes / organisation

| # | Propriété | Valeur |
|---|---|---|
| 13 | **founder** (P112) | `Yossef Haim Samama` — **laisser vide pour l'instant**, mettre en commentaire `Yossef Haim Samama (no Wikidata item yet)` |
| 14 | **founded by** ou **author** (P50) | idem, laisser un texte si pas d'item |

> 📌 Pour le founder, deux options :
> - **Option A (rapide)** : laisser vide pour l'instant. À renseigner quand la fiche du Rav sera créée plus tard.
> - **Option B (mieux pour SEO)** : créer dans la foulée une fiche minimaliste pour `Yossef Haim Samama` (juste : *instance of: human*, *occupation: rabbi*, *country of citizenship: France*, *language of expression: French/Hebrew*) avec **uniquement les infos publiques sourçables** (= ce qui est déjà sur le site about.html : « rabbin, posek, fondateur de Daat Torah »). Pas besoin de bio détaillée.

### E — Dates et lieux

| # | Propriété | Valeur |
|---|---|---|
| 15 | **inception** (P571) | `2026` (ou la date précise de mise en ligne) |
| 16 | **country** (P17) | `France` (Q142) |
| 17 | **country** (P17) | `Israel` (Q801) |

### F — URL et identifiants externes

| # | Propriété | Valeur |
|---|---|---|
| 18 | **official website** (P856) | `https://daattorah.com/` |
| 19 | **LinkedIn organization ID** (P4264) | `daat-torah` (ou le slug exact de ta page LinkedIn) |
| 20 | **Twitter username** (P2002) | si tu as un compte X |
| 21 | **Instagram username** (P2003) | si tu en as un |
| 22 | **Facebook ID** (P2013) | si tu en as un |
| 23 | **YouTube channel ID** (P2397) | si tu en as un |

### G — Caractéristiques

| # | Propriété | Valeur |
|---|---|---|
| 24 | **copyright license** (P275) | (vérifier la licence du site) — laisser vide si pas sûr |
| 25 | **target audience** (P2360) | `Jewish people` (Q7325) ou plus précis |

---

## 🔗 Étape 3 — Sources (CRITIQUE)

**Chaque statement DOIT avoir une source**, sinon il sera supprimé par un éditeur dans les semaines suivantes.

Pour chaque statement, clique « **+ add reference** » puis utilise une de ces 3 patterns :

### Pattern 1 — Site officiel

| Champ | Valeur |
|---|---|
| **reference URL** (P854) | `https://daattorah.com/about` (ou la page pertinente) |
| **retrieved** (P813) | aujourd'hui |
| **title** (P1476) | `À propos de DAAT` |
| **language of work** (P407) | French |

**Utilise ça pour** : items 18 (official website), 4-9 (sujet/contenu), 10-12 (langues), 1-3 (instance of), 15-17 (dates/pays).

### Pattern 2 — LinkedIn officiel

| Champ | Valeur |
|---|---|
| **reference URL** (P854) | `https://www.linkedin.com/company/daat-torah/` (URL exacte de ta page LinkedIn) |
| **retrieved** (P813) | aujourd'hui |
| **publisher** | LinkedIn |

**Utilise ça pour** : items 19 (LinkedIn ID), 13-14 (founder), 16-17 (country).

### Pattern 3 — Article de presse (si tu en obtiens)

| Champ | Valeur |
|---|---|
| **reference URL** (P854) | URL de l'article |
| **publication date** (P577) | date de l'article |
| **title** (P1476) | titre exact |
| **author** (P50) | si crédité |

**Si tu n'as pas encore de presse**, c'est OK — les sources 1 et 2 suffisent au démarrage. Tu enrichiras quand l'action 10 (digital PR) aboutira.

---

## 📚 Étape 4 — Catégoriser

Sur la même page, en bas, section **Identifiers** :
- Si tu as un identifiant **VIAF** (Virtual International Authority File) — peu probable au début
- **Open Library work ID** — non applicable
- **Crossref funder ID** — non applicable

C'est OK de ne rien mettre ici au début. Wikidata est itératif.

---

## 🚀 Étape 5 — Publier et vérifier

1. Tout est sauvegardé automatiquement à chaque clic. Pas de bouton « publish ».
2. **Vérifie ton brouillon** : la page item doit ressembler à https://www.wikidata.org/wiki/Q1865 (exemple de Wikipédia) — colonne label en haut, statements groupés par section au milieu, identifiers en bas.
3. **Attends 24-72 h** : Google met ce délai pour indexer une nouvelle entité Wikidata.
4. **Teste après 1 semaine** : tape « daattorah » dans Google. Si tu vois un knowledge panel à droite avec un encadré DAAT → c'est gagné.

---

## ⚠️ Pièges à éviter

| Erreur | Conséquence |
|---|---|
| Pas de source sur les statements | Suppression par éditeurs sous 2-4 semaines |
| Auto-promo dans la description | Avertissement de la communauté Wikidata |
| Créer deux items en doublon | Confusion Google, fusion manuelle requise |
| Linker vers un compte LinkedIn perso au lieu de la page entreprise | Pas un identifiant officiel |
| Dater inception en 2027 (futur) | Refusé |

---

## ✅ Checklist finale (à cocher mentalement)

- [ ] Item créé avec Q-id noté
- [ ] Labels FR/HE/EN renseignés
- [ ] Description claire dans chaque langue
- [ ] 3+ aliases par langue
- [ ] Au moins **15 statements** avec sources
- [ ] Source = `daattorah.com/about` au minimum sur chaque statement
- [ ] URL `daattorah.com` dans **official website** (P856)
- [ ] **Pas de claim sans source**
- [ ] Capture d'écran de l'item finalisé pour archives

---

## 🔮 Ce qui se passe après

1. **Sous 24-72 h** : Google indexe l'entité. Tu peux la voir dans https://www.google.com/search/about/help/knowledge-graph
2. **Sous 1-2 semaines** : knowledge panel possible quand on tape « daattorah » ou « daat halakha »
3. **Permanent** : les LLM (ChatGPT, Claude, Perplexity) commencent à citer DAAT avec une autorité de source vérifiée
4. **Bonus** : ajoute le `sameAs` Wikidata dans le JSON-LD `EducationalOrganization` du site (je peux le faire dès que tu as le Q-id)

---

## 🛟 Si tu bloques

Wikidata a une page d'aide francophone : https://www.wikidata.org/wiki/Wikidata:Tours_guides/fr (tutoriel pas-à-pas). Et la **communauté est très réactive** sur la page Wikidata:Project chat.

Bonne création ! 🌟
