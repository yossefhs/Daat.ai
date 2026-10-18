# Corrections des signalements lecteurs — 7 octobre 2026

Demande : corriger les signalements joints et publier directement sur daattorah.com.
Base synchronisée avec origin/main avant modification : fdff23717 (150 commits récupérés).

## Les 11 points

| Point | Traitement |
|---|---|
| 252, vendredi 23 h | Remplacé dans les trois langues par vendredi peu avant l’entrée de Shabbat ; lien parasite retiré. |
| 299, de jour / nuit | Traduction de מבעוד יום précisée : de jour, avant le crépuscule ; משתחשך : dès qu’il fait nuit. Niveau 4 harmonisé. Encadré distinct sur les deux opinions du crépuscule (SA HaRav 299:2-3). |
| 301, longueur du pas | « lorsqu’on peut marcher avec un pas plus court » ; conservation de l’unité source, une ama, sans conversion non sourcée. |
| 292, Pirké Avot | Six chapitres au total, Kinyan Torah étant le sixième. Cycle de six semaines à un chapitre par semaine. Opposition Ashkenaz/Sepharad retirée du lamdan hébreu ; FR/EN étaient déjà corrigés. |
| 293, entrée de Shabbat | Avant la shkia, avec ajout du profane au saint selon l’usage du lieu, sans fourchette universelle de minutes. |
| 290, raisin | Déjà correctement indiqué ha-ets dans les trois langues : conservé. |
| Navigation | Navigation ajoutée à 372 pages de Chabbat. Toutes les 1488 pages de niveau disposent désormais de la barre ; 304 et 322 inclus (N4 = passerelle). Script idempotent corrigé, numéraux hébreux conformes. |
| 291, siha du Rabbi | Référence Likoutei Sikhot 21, Bechalah, siha 2 ajoutée dans sa rubrique avec un lien Chabad.org. Attribution de רעוא דרעוין au SA HaRav 291:6-8 retirée, ainsi que sa répétition pratique. Les résumés voisins ont été rectifiés : exception en cas d’impossibilité de manger, horaire référencé au séif 2. |
| 286, séif ד | Étiquette confirmée : zéro écart d’alignement ; aucune correction. |
| 284, parenthèse | Parenthèse isolée après ובכל יום retirée de six pages, sans changement consonantique. |
| 284, maftir et bénédictions | Le terme maftir était déjà correct. Introduction hébraïque corrigée : deux bénédictions sur la Torah, une avant la haftara, quatre après ; alignée sur FR/EN. |

## Défaut supplémentaire découvert par vérification

La page hébraïque du niveau 4 de 252 tronquait plusieurs textes sources. Les vingt blocs ont été harmonisés avec le texte intégral présent en FR et vérifié contre Sefaria. Les trois langues reproduisent maintenant intégralement le même texte source.

## Sources vérifiées

- Sefaria : Choulhan Aroukh OH 252:1, 299:1, 301:1, 292:2 ; Michna Beroura 284:2 ; Choulhan Aroukh HaRav 291 et 299.
- https://www.sefaria.org/Pirkei_Avot.6
- https://www.chabad.org/library/article_cdo/aid/3447081/jewish/Shulchan-Aruch-Chapter-291-Laws-Pertaining-to-Three-Shabbos-Meals.htm
- https://www.chabad.org/search/keyword_cdo/kid/26230/scope/591213/jewish/Likkutei-Sichot-Vol-21.htm

## Veilleur : bilan actualisé, pas validation automatique

Le rapport joint était périmé. Avant correction du détecteur : 313 candidats, dont 180 concepts absents de synthèse, 68 séifim non couverts et 65 formulations absolues (3 hautes, 7 moyennes, 55 basses).

Les 68 textes de séifim prétendument absents sont intégralement présents dans les blocs sources du niveau 1. Pour 269:1, seul le titre éditorial est absent, pas le séif. Le détecteur compare maintenant les textes consonantiques complets indépendamment des balises, du nikoud et des guillemets, et retire uniquement le chapeau éditorial optionnel. Trois tests vérifient la typographie, le chapeau et la conservation d’une vraie alerte d’absence.

Après correction : zéro candidat de séif absent, 245 autres candidats conservés. Ces 180 concepts et 65 formulations ne sont PAS déclarés corrigés ni rejetés en bloc ; une relecture de fond reste nécessaire. L’alerte 255 vise notamment une question (« une seule crainte dite deux fois ? »), pas une affirmation.

## Vérifications

- Texte source niveau 1 : neuf simanim, trois langues, aucune divergence ni erreur de découpe.
- Texte intégral niveau 4 : sept simanim modifiés sur le fond, trois langues, consonnes et dénombrement identiques à Sefaria. Extraction jusqu’à </p> : le vieux helper s’arrête trop tôt sur </small> au siman 301.
- Alignement : neuf simanim, zéro écart.
- Citations : sept simanim, aucune référence fausse ou introuvable. Quatre citations restent sans référence automatiquement exploitable, et deux variantes au 284 ; ces limites préexistantes ne sont pas une validation exhaustive de toutes les phrases du site.
- Langues, balises, classes et langue des liens : zéro défaut sur Chabbat.
- Liens internes : 144421 liens vérifiés, zéro cible absente.
- Audit structurel : 272/272 simanim conformes.
- Build réussi. Avertissements d’extraction préexistants : 188 pages partiellement extraites, six sans chunk (dont les deux passerelles 304/322).
- Intégrité contre origin/main : aucune régression après harmonisation des numéros de navigation.

## Registre administrateur

Les statuts du registre ne sont pas modifiés : accès administrateur indisponible dans cette session. Aucun candidat automatique n’a été marqué « Approuvé » ou « Corrigé » sans examen.
