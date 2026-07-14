# DAAT — Guide de correction (dirigé)

> Comment procéder, dans l'ordre. Trois tranches, du plus sûr au plus délicat.
> Branche de travail : `claude/daattorah-site-audit-tyhabm`. Rien n'est en production tant que la branche n'est pas fusionnée.

---

## 🟢 TRANCHE 0 — Déjà fait, à vérifier puis fusionner (0 risque halakhique)

Ces corrections mécaniques sont **appliquées et vérifiées** (contenu 124/124 conforme). Votre seule action : les regarder et fusionner.

| # | Correction | Portée | Comment vérifier en 30 s |
|---|-----------|--------|--------------------------|
| 0.1 | Ordre du catalogue `/contenu` (OH 1→64 · YD · Nida · Shabbat) | 3 fichiers | Ouvrir `/contenu` : la 1ʳᵉ section doit être « Orah Haïm quotidien » (siman 1). |
| 0.2 | Meta/JSON-LD réparés (gershayim `"`→`״`) | ~1 700 fichiers | Partager n'importe quelle page siman sur WhatsApp/FB : le titre n'est plus coupé à « Siman רמ ». |
| 0.3 | Coquille שיחות (était סיכות) | 122 simanim | Sur un niveau 4, la section du Rabbi affiche « שיחות, מאמרים ואגרות ». |
| 0.4 | Compteur « 4 niveaux » (était 3) | 136 index | Un index de siman affiche « Les 4 niveaux d'étude ». |

**👉 Action recommandée : fusionner la Tranche 0 dès maintenant** — gain immédiat sur tout le site, aucun enjeu halakhique.

---

## 🟠 TRANCHE 1 — Corrections éditoriales sûres restantes (je peux les faire, sans le Rav)

Vérifiables par simple lecture, aucune décision halakhique. Je peux toutes les appliquer sur demande.

1. **Titre `<title>` « Siman 242 » sur les simanim 243 et 246** (niveau 4, FR) — dans le `<title>` **et** le `headline` JSON-LD. → Remplacer par 243 / 246. *(le contenu, lui, est correct)*
2. **Titres HE/EN non traduits sur 304 et 322** (restés en français). → Traduire les `<title>`.
3. **Meta au mauvais sujet — siman 255** : les pages HE/EN du niveau 4 annoncent « eau bouillante / boiling water » au lieu de « préparation du feu ». → Corriger le sujet.
4. **Meta EN cassée — siman 293** : guillemets droits autour de « Atah Chonantanu » + troncature. → Échapper / compléter.
5. **196 `<title>` tronqués** (coupés en plein mot). → **À régénérer côté générateur** (og:title n'est pas une source fiable) — je peux préparer le correctif du générateur.
6. **Coquilles hébraïques ponctuelles** : `חטמנא`→`הַטְמָנָה` (253), « Yarba »→`חבית` (258), `סיכות`(261) déjà couvert, `איו`→`אינו` (251), `בכסף`→formulation (251). → Corriger.
7. **Résidus de langue** : meta/titres N2 rédigés en français sur pages HE/EN (249, 253, 293) ; mot « séifim »/« Lamdan » latin resté sur pages EN/HE (244, 258). → Traduire.
8. **Liens de langue** : sur les pages FR de certains niveau 2, les liens « Soutenir/Communauté » pointent vers les pages **HE** (251, 293). → Corriger la cible selon la langue.
9. **Duplication `סימן (סימן)`** dans 13 titres HE. → Retirer.
10. **Placeholders vides** « Position classique : — » (257, 263, 293). → Compléter ou masquer.

**👉 Dites « fais la Tranche 1 » et je l'exécute** (dry-run puis application, comme la Tranche 0).

---

## 🔴 TRANCHE 2 — Réservé au Rav (fond halakhique — je ne corrige pas, je documente)

C'est le **cœur du problème** et il ne peut être tranché que par le Rav. Détail complet, avec extraits et n° de ligne, dans `erreurs-halakha.csv` (69 points « Validation_Rav = oui »).

### Le problème n°1, transversal : le Niveau 4 « Daat HaRav »
Sur **9 des 20 simanim revus**, l'appareil analytique du niveau 4 (tableau « force du psak », חידושים, conduite pratique) **ne correspond pas au texte du Choulhan Aroukh HaRav reproduit sur la même page** : renvois de seif faux, paraphrases présentées comme citations *verbatim*, sources anachroniques (machine à laver, Netflix, Pony Espress, « Mahadoura Batra » inexistante), et **parfois une conclusion halakhique inversée**.

**Comment le Rav devrait procéder, siman par siman :**
1. Lire la **section 1** du niveau 4 (le texte hébreu intégral du Rav) — c'est la référence.
2. Confronter chaque renvoi de seif du tableau/chidoushim à ce texte.
3. Trancher : réécrire l'analyse d'après le texte réel, ou la retirer.

### Points les plus urgents (conclusion pratique en jeu)
| Siman | Point à trancher | Réf. CSV |
|-------|------------------|----------|
| **261** | Niveau 4 : « allumer **même à bein hashmashot** » — contredit tous les autres niveaux et le texte de l'Admour. | H-261-01 |
| **257** | Niveau 4 : « sable froid = permis » — le texte classe le sable en מוסיף הבל (interdit). | H-257-01 |
| **249** | Niveau 4 : Mehaber « interdit de jeûner érev Shabbat » — le Mehaber dit l'inverse. | H-249-01 |
| **248** | Base FR+HE : « mercredi permis » — contredit tout le reste (interdit selon Magen Avraham). | H-248-01 |
| **246** | Prêter en érev Shabbat : *permis* (N1/N4) vs *interdit* (index/N2/N3). | H-246-01 |
| **293** | Attribution « אתה חוננתנו » au siman 293 (c'est le 294). | H-293-01 |
| **242** | Statut déoraïta vs dérabanan de l'Admour : contradiction interne au niveau 4. | H-242-01 |

### Puis, par siman, les autres points Rav
242 (8) · 243 (2) · 244 (5) · 245 (3) · 246 (3) · 247 (6) · 248 (4) · 249 (4) · 250 (1) · 251 (3) · 252 (3) · 253 (3) · 254 (3) · 255 (2) · 256 (1) · 257 (3) · 258 (2) · 261 (7) · 263 (3) · 293 (3).
→ Filtrer `erreurs-halakha.csv` sur la colonne `Siman` ; chaque ligne donne fichier, ligne, extrait, problème, source primaire suggérée et correction proposée.

---

## Ordre conseillé (résumé)

1. **Fusionner la Tranche 0** (fait, vérifié) — gain immédiat.
2. **Me laisser faire la Tranche 1** (éditorial sûr) — je livre en dry-run.
3. **Confier la Tranche 2 au Rav**, en commençant par les 7 points « conclusion pratique » ci-dessus.
4. En parallèle, je peux **poursuivre la revue profonde** des 104 simanim Shabbat restants + Orah Haïm / Yoreh Deah / Limoud / Blog, pour compléter la liste du Rav.

---

## Fichiers de référence
- `erreurs-halakha.csv` — 121 constats de contenu (fond + éditorial).
- `erreurs-techniques.csv` — défauts techniques/SEO + agrégats site-wide.
- `erreurs-recurrentes.md` — les 7 patterns récurrents expliqués.
- `erreurs-critiques.md` · `rapport-global.md` — vue d'ensemble.
- `artefacts-a-verifier.csv` — les 112 points que l'auteur a lui-même marqués « à vérifier ».
