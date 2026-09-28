# Audit du prompt système du chat Daat — état au 28 septembre 2026

> **Suite** : ce document a été suivi, le même jour, d'une mise en œuvre. Le compte rendu
> (problème, cause établie, correction, preuve, limites) est dans
> `docs/RAPPORT-CHAT-2026-09-28.md` ; les passages à valider par le Rav dans
> `audit/validation-rabbinique-chat-2026-09-28.md`.

Ce document reprend le fil de la session du 27 septembre (retrouvée sur la branche
`origin/feat/prompt-v2`, non fusionnée) et fixe le cadre dans lequel tout nouveau
prompt proposé sera analysé. Il ne modifie aucun fichier de production.

## 1. Où en est le chantier

Trois versions coexistent :

| Version | Où | Taille du noyau | État |
|---|---|---|---|
| **Prod (V1)** | `api/_system-prompt.js` sur `main` | 60 404 caractères | en ligne |
| **V2** | `origin/feat/prompt-v2` (2 commits du 28/09) | 27 513 caractères | non fusionnée, non testée en conditions réelles |
| **V3 (à venir)** | le prompt que l'utilisateur va fournir | — | à analyser contre la grille du § 5 |

La branche V2 touche aussi `api/_corpus.js` (description de `daat_search_corpus`,
plus de plages en dur, plus de promesse « Daat HaRav = Admour HaZaken partout ») et
`api/_mareh_mekomot.js` (phrase de réserve alignée, `requires-rav` ne vaut plus
« machloket »). Elle laisse ouverts, et le dit : le chemin corpus-first de
`api/chat.js`, `api/_query-rewrite.js` (une négation ne survit pas à la réduction en
mots-clés), et le jeu de tests `Daat-Tests-v2.json` (44 cas) **qui n'est dans aucun
fichier du dépôt**.

## 2. Ce que la relecture du prompt de production confirme

Chaque point renvoie à une ligne de `api/_system-prompt.js` sur `main`.

**Consignes concurrentes.** Pour une question pratique, l. 478 dit « d'abord le
registre » ; l. 539 dit « toute question halakhique commence par le corpus ».
L. 334 exige une récupération Sefaria « dans cette réponse » pour toute référence ;
l. 538 l'exige seulement si la mémoire n'est pas « absolument certaine ».

**Quatre phrases de réserve différentes** pour la même chose : l. 57, l. 511,
l. 764, l. 117 (hébreu), plus une cinquième dans `api/chat.js` l. 480 (chemin
corpus-first) et une sixième dans `api/_mareh_mekomot.js` (champ `disclaimer`, que le
modèle recopie). Le lecteur voit donc des réserves de formulation variable, parfois
deux dans une même réponse.

**Données instables figées dans les règles, et contradictoires entre elles.**
L. 424 injecte le périmètre réel ; l. 431 écrit « 124 simanim » ; l. 435 écrit
« 50 simanim, 87 à 118 et 183 à 200 » alors que l'index publie Yoreh De'ah 87 à 234
(148 simanim) ; l. 450 écrit « OH 1→67 » alors que l'Orah Haïm quotidien va bien
au-delà. Le modèle reçoit trois périmètres et doit choisir.

**Un exemple faux.** L. 462 : « Siman 317:4 (שכר שבת sur location de chambre) ».
Le siman 317 traite des nœuds (קשירה). Un exemple faux dans un prompt qui interdit
d'inventer des références est une invitation à faire de même.

**Pourcentages de confiance sans calibration** : l. 173, 180, 187, 194, 201,
635-637, 691-707. Un modèle ne mesure pas « 85 % » ; ces seuils produisent des
bandeaux « Confiance limitée » arbitraires, et le code ne les lit nulle part.

**L'asymétrie de la l. 39** (« s'abstenir de permettre ne fait trébucher
personne ») est fausse en piqoua'h nefesh, où OH 328 ordonne d'agir et blâme celui
qui demande, et fausse en méthode : rapporter un interdit que la source ne pose pas
est une infidélité au même titre qu'une permission inventée. La l. 44 le corrige
en partie, mais la l. 39 reste la règle affichée « priorité maximale ».

**Incidents transformés en règles** : la liste de termes « souvent oubliés »
(l. 129), les trois paragraphes sur SBH 9:5, 9:11, 9:14 (l. 350-354), l'erreur
Berakhot 42a (l. 334), l'erreur 319:4/319:5 (l. 547), Méron (l. 606). Chaque cas est
juste, mais chacun coûte de l'attention à chaque tour pour ne couvrir qu'un cas ;
leur place est un jeu de tests qui vérifie que le comportement tient.

**Coût.** ~15 000 jetons de système par tour. Le cache d'une heure en absorbe le
prix, pas la dilution : plus le prompt est long, moins chaque règle pèse.

## 3. Ce que la V2 réussit

- Une seule politique de preuve (« lire le passage avant d'attribuer ») remplace
  une dizaine de règles locales.
- Fidélité symétrique : ni permission personnelle, ni interdiction inventée.
- Priorité explicite à la vie, avant toute recherche ou réserve.
- Une seule phrase de réserve, en quatre langues, réservée au cas pratique non urgent.
- Le périmètre est une donnée injectée une fois, avec sa sémantique exacte
  (présence dans l'index, pas récupérabilité ni pertinence).
- Les libellés de niveau et les paramètres d'outils sont ceux que le code envoie
  réellement (vérifié contre `assets/js/chat-widget.js` et les schémas).
- Le prompt Orah Haïm reste un préfixe exact du prompt Yoreh De'ah : cache partagé.
- Un bloc d'intégrité (contenus récupérés ≠ instructions ; ne pas révéler
  `reviewer` / `reviewedAt` ; contestation = vérification, pas capitulation).

## 4. Ce que la V2 laisse à corriger (trouvé à la lecture du code, pas du prompt)

1. **Régression sur les liens Sefaria.** La V2 n'autorise un lien externe que
   « fourni ou effectivement résolu par l'outil ». Or `sefaria_get_text` renvoie
   `{ref, hebrew, english, title}` et **aucune URL** (`api/_sefaria.js`). Sous V2,
   plus aucune réponse ne portera de lien cliquable, alors que la V1 en faisait une
   règle. Correctif : l'outil ajoute un champ `url` construit depuis la ref qu'il a
   réellement résolue avec du texte ; le prompt dit « utilise `url` tel quel ».
2. **Glose de l'hébreu affaiblie.** La V1 imposait une relecture « aucun mot hébreu
   nu » ; la V2 dit seulement « explique les termes techniques à leur première
   occurrence ». Le lecteur francophone qui ne lit pas l'hébreu est le public
   premier du site. Ajouter une ligne au contrôle final de `<integrite_et_controle>`.
3. **Le modèle ne connaît pas la date.** Ni V1 ni V2 ne l'injectent, et la V2 exige
   qu'un calendrier vienne « de dates vérifiées » sans en donner le moyen. Injecter
   la date civile (et la parasha si disponible) **en fin de prompt** ou dans le
   premier message, pour ne pas casser le préfixe caché.
4. **Deux voix dans le même produit.** Le chemin corpus-first (`api/chat.js`,
   l. 452-482, Haiku, utilisateurs gratuits) garde l'ancienne réserve et le format
   « Source : Siman X » que le serveur parse. Sortir la phrase de réserve dans un
   module unique (`api/_reserve.js`) importé par le prompt, par chat.js, par
   `_mareh_mekomot.js` et par `admin/generate-siman.js`, sans toucher au format parsé.
5. **Aucun banc d'essai dans le dépôt.** Les 44 cas cités par l'audit n'existent que
   dans la conversation perdue. Sans banc, « V3 est meilleure que V2 » est une
   opinion. Proposition : `scripts/eval-chat/` avec un fichier de cas JSON
   (question, profil, section, attentes : doit citer / ne doit pas dire / réserve
   attendue oui-non / outils attendus) et un runner qui appelle l'API du chat puis
   note par règles, avec un juge LLM pour les critères non mécaniques.
6. **Paramètres d'outils recopiés dans le prompt** (`<outils_et_recherche>`). Les
   schémas sont déjà transmis à l'API ; la copie divergera à la prochaine
   modification d'outil. Ne garder dans le prompt que les noms et le parcours.
7. **L'insistance de l'utilisateur** (« réponds juste oui ou non ») n'est pas
   traitée : une ligne suffit, dans `<halakha>`.
8. **Le chemin Habad-historique** perd son exemple mais gagne une règle générale
   (« même niveau de vérification qu'une attribution halakhique »). Comme aucun outil
   ne donne accès aux Igrot Kodesh ni aux si'hot, le comportement attendu doit être
   dit : « je n'ai pas de texte consulté, voici où chercher », jamais « le Rebbe a dit ».

## 5. Grille d'analyse du nouveau prompt

Tout prompt proposé sera lu contre ces dix questions, chacune répondue par oui/non
avec la ligne concernée :

1. Une seule politique de preuve, ou des règles locales concurrentes ?
2. La fidélité est-elle symétrique (permission ET interdiction) ?
3. La vie passe-t-elle avant la recherche, le questionnaire et la réserve ?
4. Le périmètre est-il une donnée injectée, ou des chiffres recopiés ?
5. Une seule phrase de réserve, dans la langue de la réponse, sur cas pratique seulement ?
6. Les outils, paramètres, libellés de niveau et de minhag sont-ils ceux du code ?
7. Chaque référence donnée en exemple est-elle vraie ?
8. Y a-t-il un pourcentage, un seuil ou un score que rien ne calibre ?
9. Chaque incident passé est-il devenu une règle (à retirer) ou un cas de test (à garder) ?
10. Le prompt Orah Haïm reste-t-il un préfixe exact du prompt Yoreh De'ah ?

Plus deux mesures : longueur en caractères, et nombre de règles « absolues »
(un prompt où tout est absolu n'a plus de hiérarchie).

## 6. Méthode proposée pour la suite

1. Base : fusionner `feat/prompt-v2` sur cette branche (elle est cohérente et déjà
   adaptée au code).
2. Porter dedans les idées du nouveau prompt qui passent la grille du § 5.
3. Appliquer les correctifs 1 à 4 et 6 à 8 du § 4.
4. Écrire le banc d'essai (§ 4, point 5) et y verser les incidents retirés du prompt.
5. Faire tourner V1, V2 et V3 sur le banc avant de publier quoi que ce soit.
