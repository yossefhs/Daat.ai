# DAAT — Erreurs critiques (phase automatique)

> Aucune modification effectuée. Une « erreur critique » ici = un défaut pouvant induire un lecteur en erreur sur *quel* siman/contenu il étudie, ou une règle halakhique incorrecte.
> **La phase automatique n'a détecté AUCUNE erreur halakhique de contenu** (celles-ci ne peuvent être établies que par la revue rabbinique — en cours pour 3 simanim).

---

## C-01 — `<title>` erroné « Siman 242 » sur les simanim 243 et 246 (niveau 4, FR)

- **Fichiers :** `sources/shabbat/siman-243/niveau-4-daat-harav.html`, `sources/shabbat/siman-246/niveau-4-daat-harav.html`
- **Constat :** la balise `<title>` affiche `Siman 242 · Niveau 4 — Chitah de l'Admour HaZaken | Hilkhot Shabbat`.
- **Preuve que le contenu, lui, est correct :** `canonical = /oh/243/daat-harav` (resp. 246), `<h1>` = « …sur le Siman **רמ״ג** » (=243) / « **רמ״ו** » (=246), `og:title` correct, versions HE et EN correctes.
- **Nature :** copier-coller du `<title>` depuis le siman 242. **Aucune erreur de contenu halakhique** — seul l'intitulé d'onglet / le SEO est affecté.
- **Gravité réelle :** IMPORTANTE (pas CRITIQUE au sens halakhique).
- **Correction proposée :** remplacer `Siman 242` par `Siman 243` / `Siman 246` dans la seule balise `<title>`.
- **Certitude :** haute. **Validation du Rav nécessaire :** non.

---

## C-02 — `<title>` HE/EN non traduits sur les simanim 304 et 322

- **Fichiers :** `sources/shabbat/siman-304/index-en.html`, `.../index-he.html`, `sources/shabbat/siman-322/index-en.html`, `.../index-he.html`
- **Constat :** le `<title>` des variantes anglaise et hébraïque est resté **en français** (ex. HE : « Siman 304 — Le repos du serviteur et de l'esclave le | הלכות שבת »).
- **Contexte :** 304 et 322 sont les deux simanim « pont » (sans niveau 4). Le reste du corpus (1 142 triples testés) est correctement localisé.
- **Gravité :** IMPORTANTE (parité trilingue + SEO). Pas d'impact halakhique.
- **Correction proposée :** traduire les `<title>` EN et HE de ces deux pages index.
- **Certitude :** haute. **Validation du Rav nécessaire :** non (traduction éditoriale simple).

---

## Points NON critiques mais à trancher (voir rapport-global §5)

- **Yoreh Deah niveau Lamdan hébreu uniquement** (50 simanim) : choix éditorial à confirmer, pas une erreur.
- **108 alertes chronologie heuristiques** : très majoritairement des faux positifs ; l'exactitude fine des zmanim relève du Rav.

---

## Ce que la phase automatique ne peut PAS certifier

- Exactitude d'une règle halakhique.
- Exactitude d'une citation par rapport à sa source primaire.
- Exactitude/fidélité d'une traduction.
- Contradiction *de fond* entre niveaux d'étude.

→ Ces axes sont ouverts sur la revue sémantique (3 simanim échantillonnés en cours) et, pour toute conclusion, **« À vérifier par le Rav »**.
