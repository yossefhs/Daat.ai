# DAAT — Erreurs récurrentes (revue approfondie, lots 1-4 : 34 simanim)

> Basé sur la revue sémantique des simanim **242-274 (contigus) + 293** (222 constats dans `erreurs-halakha.csv`).
> Chaque pattern est **vérifiable par lecture croisée** (une page contredit une autre page, ou le texte reproduit sur la même page). La **résolution halakhique** reste « À vérifier par le Rav ».

---

## 🔴 PATTERN #1 (le plus grave) — Niveau 4 « Daat HaRav » : l'appareil analytique est décorrélé du texte-source reproduit sur la même page

**Où :** sections §2 (tableau « כח הפסק / Force du psak »), §3 (חידושים) et §5 (למעשה) des pages `niveau-4-daat-harav*`.
**Quoi :** ces sections citent des **numéros de seif faux**, présentent des **paraphrases entre guillemets comme des citations verbatim**, et attribuent au Mehaber/Rama/Admour HaZaken des textes qui **ne correspondent pas** au texte intégral reproduit en §1 de la **même page**.
**Observé sur :** 244-250, 261, 263 (lots 1-2) **et confirmé en masse au lot 4 : 268, 271, 272, 273, 274** — dans presque tous les N4 revus.
**Identique dans les 3 langues** → défaut de **contenu**, pas de traduction.

Cas les plus graves (inversions / fabrications) :
- **268** (grave, trilingue) : la section למעשה/חידוש greffe sur le siman 268 (**erreurs dans la tefilla** de Chabbat) la loi de l'oubli de **Retsé dans le Birkat Hamazon** (hiérarchie 1er/2e repas = reprise, seouda chlichit = non) — qui relève du **siman 188**, en contradiction avec le §1 de la même page et avec N1/N3.
- **270** (grave, trilingue) : N1/N2/N3 **fabriquent un « seif 2 = exceptions calendaires »** et **omettent le vrai seif 2** du Mehaber (Kiddouch en synagogue avant Bameh Madlikin), que seule la page N4/SAR reproduit correctement.
- **271** : « Vayekhulou » renvoyé à 271:14-18 alors qu'il est au **seif 19** ; obligation des femmes renvoyée à 271:19-23 alors qu'elle est aux **seifim 5-6** (les deux vérifiés contre le §1 reproduit).
- **273** : le critère de la « vue continue » renvoyé à 273:4-7 alors qu'il est au **seif 2** reproduit sur la même page ; découpage 1-3/4-7/8-10/11-12 des למעשה sans correspondance thématique.
- **274** : le **לחם משנה** renvoyé à 274:3-5 alors qu'il est au **seif 2** ; le choix du pain (dessous/dessus) renvoyé à 274:6-8 alors qu'il est aussi au **seif 2**.
- **249** : le tableau attribue au Mehaber « אָסוּר לְהִתְעַנּוֹת בְּעֶרֶב שַׁבָּת » (interdit de jeûner) — or le Mehaber 249:3 dit **l'inverse** (« דרך אנשי מעשה להתענות »). Cite aussi un **seif 5 du Mehaber inexistant** (le siman n'a que 4 seifim).
- **261** : le point ④ למעשה « allumer **même à bein hashmashot** » contredit N1/N3/blog **et** le texte de l'Admour sur la même page (melakha interdite midéoraïta à בין השמשות).
- **250** : « 3 repas / choix des plats poisson-viande-vin » plaqués sur des seifim qui traitent en réalité de l'aiguisage du couteau et du moment des achats ; Mehaber 250:2 fabriqué.
- **263** : « filles allument dès 3 ans (263:11-12) » alors que 263:11-12 = nuit de tevila et aveugle.
- **244** : les seifim ד et ו *étudiés* ne correspondent pas au texte *cité*.

➡️ **Recommandation : traiter le Niveau 4 comme la priorité de vérification rabbinique.** Réassigner chaque renvoi/chidoush au seif réel du Choulhan Aroukh HaRav et rétablir les verbatim exacts.

---

## 🔴 PATTERN #2 — Références fabriquées / anachroniques (Niveau 4)

- **Michna Beroura** citée avec des plages de seif-katan précises **et des exemples anachroniques** : « Western Union, Pony Express » (247), « chemins de fer XIXᵉ, Maharsham, bateaux à vapeur 1810-1820 » (248), « Netflix » (249).
- **« Mahadoura Batra »** invoquée pour des simanim qui n'en ont pas (247, 249).
- **Mivtza Neshek** (institué par le Rabbi en **1974**) attribué au Choulhan Aroukh de l'**Admour HaZaken** (mort en 1812) — anachronisme (263).

➡️ Risque de **source non attestée**. À sourcer ou retirer. « Je ne peux pas vérifier automatiquement — validation rabbinique nécessaire. »

---

## 🟠 PATTERN #3 — Contradictions inter-niveaux sur la conclusion pratique

Le takeaway d'un niveau contredit un autre niveau (souvent le Niveau 4 vs Base/Synthèse) :
- **248** : Base FR+HE « mercredi permis (majorité) » vs tableau/EN/N2/N3/Admour « mercredi interdit (Magen Avraham) » — statut **permis/interdit**.
- **246** : prêter (השאלה) en érev Shabbat *permis* (N1/N4/index.md) vs *interdit* (index/N2/N3).
- **247** : « permis בכל גוונא » (N1/N3) vs חומרא de l'Admour (N4).
- **242** : statut déoraïta (N4 §חידוש) vs dérabanan (index/N1/N3 + tableau du N4).
- **293** : tzeit « 35-45 min » (N1) vs « 15-30 min » (N3).
- **261** : « 22 min à Jérusalem » (Base) vs « 40 min » partout ailleurs.

---

## 🟠 PATTERN #4 (technique, systémique) — Meta / JSON-LD cassés par un gershayim ASCII

Le numéral hébraïque (`רמ״ב`…) est parfois écrit avec un guillemet **droit ASCII** `"` (au lieu du gershayim typographique `״`, U+05F4) **à l'intérieur d'attributs `content="…"` et de chaînes JSON-LD**, ce qui ferme l'attribut / invalide le JSON. **1 093 fichiers** (voir `T-META-GERSHAYIM`). Casse `description`, `og:title`, `twitter:*`, et parfois tout le bloc `@graph` (250, 249).

---

## 🟠 PATTERN #5 — Compteur « 3 niveaux » alors que 4 sont affichés

Le titre « Les 3 niveaux d'étude » (souvent FR seul ; parfois HE/EN aussi, ex. 263) surplombe 4 cartes. Vu sur 243, 245, 246, 247, 248, 249, 250, 261, 263, 293. Corrigeable mécaniquement.

---

## 🟡 PATTERN #6 — Troncatures (titres, sous-titres, JSON-LD headline)

`<title>` et sous-titres hero **coupés en plein mot**, souvent côté FR, alors que HE/EN sont complets (243, 247, 248, 249, 250, 261, 293). Parfois la troncature est aussi dans le `headline` JSON-LD (248).

---

## 🟡 PATTERN #7 — Artefacts éditoriaux en production

- **112 commentaires** `<!-- à vérifier / to verify -->` dans 45 pages Niveau 4 (25 simanim) — l'auteur a lui-même marqué ces points (voir `artefacts-a-verifier.csv`).
- Coquille hébraïque **« סיכות » au lieu de « שיחות »** dans le titre de section Niveau 4 (244, 249 — défaut de gabarit partagé FR+EN, HE correct).
- Placeholders vides « Position classique : — » (263, 293).

---

## Ce qui est SAIN (à souligner)

- **Parité FR/HE/EN globalement bonne** : la plupart des erreurs sont *inter-niveaux* ou *partagées dans les 3 langues*, pas des divergences de traduction. Exceptions notables où une langue est meilleure : 248 (mercredi : EN correct, FR/HE faux), 261 (nom d'Amora : EN correct, FR/HE faux), 249 (Base FR plus riche que HE/EN).
- **Numérotation des simanim** (gematria רמ״ב=242…) : correcte partout.
- **Niveaux 1-3** souvent fidèles et cohérents entre eux ; le point « allumage = kabbalat Shabbat » (263) est correctement présenté comme *mahloket* à tous les niveaux.
- **Le blog** est le support le plus rigoureux sur les zmanim (261).
- **Le bug « Siman 242 »** (title+JSON-LD) est **isolé** à 243 et 246 (pas universel).
