# Aperçus du niveau 4 : relevé, échantillon jugé, règle (13 octobre 2026)

Chaque séif du niveau 4 (Orah Haïm, Hilkhot Chabbat) vit dans un `<details class="seif-details">`. Son titre porte « סעיף X » et un **aperçu** vocalisé (`summary > span.seif-preview`), dans la police du texte source, juste au-dessus de lui. **8 976 blocs sur 9 942 (90,3 %) sont fermés au chargement** (seuls 966 portent `open`) : c'est l'aperçu que le lecteur lit d'abord, et il le lit comme le début du séif.

Aucune porte ne le lisait. `verify-oh-source.py` le déclarait hors champ, et `verifier-citations.py` ne juge que le texte entre guillemets. Le relevé ci-dessous est celui de la porte écrite pour lui, `scripts/verifier-apercus.py`, sur les pages d'avant la correction. Le relevé complet, une entrée par aperçu distinct avec le début de son séif, est dans `audit/apercus-niveau4.txt`. **La correction A a été appliquée le même jour (section 5) : la porte sort désormais verte.**

## 1. Mesure

**Méthode.** Chaque aperçu est comparé au `.sa-he` **de son propre bloc**. La page est lue par le `Lecteur` de `verify-oh-source.py`, et les mots sont normalisés par sa fonction `mots()`, importée et non recopiée :

- comparaison sur les consonnes ; nikoud, ponctuation et guillemets ignorés ;
- maqaf traité comme une frontière de mot ;
- crochets éditoriaux de Kehot retirés : « יַחֲזִ[י]ר » = « יחזיר » ;
- « … » et « ... » reconnus.

Le texte de l'aperçu est tout le `<summary>`, sauf `span.seif-num`. La porte ne consulte pas Sefaria. L'aperçu n'est donc garanti conforme à la source que si `verify-oh-source.py` certifie le `.sa-he` de la même page.

**Recoupement avec l'arbitre du septième tour.** L'arbitre comptait 9 859 aperçus, dont 2 694 avec un mot absent du `.sa-he`. La mesure trouve 9 861 blocs qui portent un `span.seif-preview`, et 2 695 aperçus avec au moins un mot absent au sens strict. La porte en classe 2 591 dans « mot absent ». Les 104 autres ne s'écartent du séif que par leur dernier mot, coupé juste avant « … » (« בְּסִמ… », Chabbat 305 (ש״ה), 314 (שי״ד)…). Ce sont des débuts de séif coupés à longueur fixe : la règle les tient pour conformes.

### Répartition, 906 pages lues (les 189 pages-ponts n'ont aucun bloc)

| Classe de la porte | Classe de la demande | Blocs | FR · HE · EN | Aperçus distincts |
|---|---|---:|---|---:|
| INCIPIT — séif entier | préfixe exact | 107 | 37 · 35 · 35 | |
| INCIPIT — coupe finale déclarée | préfixe exact, « … » final | 5 554 | 1 938 · 1 807 · 1 809 | |
| COUPES DÉCLARÉES | troncature avec « … » | 214 | 72 · 69 · 73 | |
| **Conformes** | | **5 875** | | |
| SANS APERÇU (`<summary>` nu) | — | 41 | 1 · 40 · 0 | |
| TITRE SANS HÉBREU | — | 70 | 0 · 0 · 70 | |
| NOTE ENTRE CROCHETS (305 (ש״ה):33, séif vide chez Sefaria) | — | 1 | 0 · 1 · 0 | |
| **Admis, non confrontés** | | **112** | | |
| COUPE NON DÉCLARÉE | préfixe ou fenêtre, sans « … » | 316 | 102 · 104 · 110 | 113 |
| « … » SANS COUPE | troncature avec « … » | 21 | 7 · 7 · 7 | 7 |
| ABRÉGÉ | abrégé (mots présents, sautés) | 776 | 250 · 257 · 269 | 278 |
| REFORMULÉ | reformulé (mots présents, ordre changé) | 251 | 82 · 82 · 87 | 87 |
| MOT ABSENT | contenant un mot absent | 2 591 | 825 · 912 · 854 | 947 |
| **Non conformes** | | **3 955** | | **1 432** |

Précisions sur les classes non conformes :

- **Mot absent.** 1 544 aperçus contiennent au moins un mot étranger au séif. Dans les 1 047 autres, chaque mot absent n'est qu'une variante d'un mot du séif : yod/vav, préfixe, frontière de mot, sigle. Cela ne rend pas l'aperçu plus fidèle : une condensation faite de mots du séif reste une condensation.
- **Fenêtres hors tête.** Elles sont toutes dans la coupe non déclarée : aucun aperçu ne s'ouvre sur « … ». Le cas le plus fréquent est un premier mot omis, le plus souvent « אֲבָל » ou « וְכֵן ».
- **Drapeau ⚑.** 143 aperçus (53 distincts) contiennent un mot de décision absent du séif (מֻתָּר, אָסוּר, חַיָּב, פָּטוּר, צָרִיךְ, חוֹזֵר, מְבָרֵךְ…).

**Le défaut est concentré à Orah Haïm.**

| Section | Aperçus confrontés | Non conformes | Part | Simanim touchés |
|---|---:|---:|---:|---|
| Orah Haïm | 4 716 | 3 922 | 83 % | 175 sur 180 servis |
| Hilkhot Chabbat | 5 114 | 33 | 0,6 % | 6 : 252 (רנ״ב), 301 (ש״א), 330 (ש״ל), 355-357 (שנ״ה-שנ״ז) |

Au total, 1 362 séifs sur 3 314 portent au moins un aperçu non conforme : 1 266 dans les trois langues, 61 dans deux, 35 dans une seule. Pour 560 séifs, les trois langues n'ont pas les mêmes mots d'aperçu.

**Quatre populations, nées de quatre façons de produire :**

1. **Orah Haïm : des condensations en hébreu vocalisé, dans la langue de l'Admour HaZaken.** Un tiret sépare le cas de la décision, un point-virgule sépare les clauses. Exemple, 47 (מ״ז):3 : « הַכּוֹתֵב בְּדִבְרֵי תוֹרָה — מַחֲלֹקֶת ; לְעִנְיַן מַעֲשֶׂה יוֹצִיא בְּפִיו ». Rien ne les distingue du texte source : même nikoud, même police, même place. C'est la quasi-totalité des 3 922 aperçus non conformes de la section.
2. **Pages hébraïques de 128 (קכ״ח), 60 aperçus, et de 355-357 (שנ״ה-שנ״ז), 29 aperçus : des condensations ou titres non vocalisés.** Exemple : « שתי ספינות סמוכות — דין הטלטול והעירוב ». Les 89 aperçus sans nikoud sont tous non conformes, et aucun aperçu conforme n'est sans nikoud. Les pages françaises des mêmes séifs portent le début du séif.
3. **Pages anglaises de 305 (ש״ה), 321-324 (שכ״א-שכ״ד), 355-357 (שנ״ה-שנ״ז) : des titres anglais**, par exemple « Two ships side by side — carrying law and eruv ». La règle les admet : ils ne se donnent pas pour la source.
4. **Le reste de Chabbat : des débuts de séif coupés à longueur fixe** (« בְּסִמ… »). Conformes.

## 2. Échantillon jugé : paraphrase légitime ou erreur de sens

**Méthode.** J'ai lu deux échantillons, chaque aperçu contre son séif complet.

- **Un tirage au hasard** (graine 20261013) de 60 aperçus distincts parmi les non conformes : 30 « mot absent » avec un mot étranger, 10 « mot absent » faits de variantes seulement, 10 abrégés, 10 reformulés.
- **Les aperçus marqués ⚑**, lus en entier dans les deux versions du drapeau, soit 61 aperçus distincts.

Avec les recoupements, 117 aperçus distincts ont été lus.

**Trois verdicts :**

- **Fidèle** : la condensation dit ce que dit le séif. Elle n'est ni verbatim ni marquée.
- **Imprécis** : le sens pratique est conservé, mais une attribution est omise (« יֵשׁ מִי שֶׁאוֹמֵר », « יֵשׁ מְפָרְשִׁים » ou un « לִמּוּד זְכוּת » donnés comme la règle), ou un mot est ambigu.
- **Erreur de sens** : l'aperçu affirme ce que le séif ne dit pas. Cela recouvre un psak inversé, une condition omise qui renverse la règle pour un cas, ou un statut changé (minhag donné pour une règle, « אֵינוֹ רַשַּׁאי » donné pour « אֵינוֹ יוֹצֵא »).

| Tirage au hasard | Fidèle | Imprécis | Erreur de sens |
|---|---:|---:|---:|
| Mot absent, mot étranger (30) | 25 | 2 | 3 |
| Mot absent, variantes seules (10) | 7 | 1 | 2 |
| Abrégé (10) | 10 | 0 | 0 |
| Reformulé (10) | 7 | 3 | 0 |
| **Total (60)** | **49** | **6** | **5** |

**Ce qu'il en ressort :**

- **Le hasard donne 5 erreurs de sens sur 60**, soit 8 % (intervalle à 95 % : 4 à 18 %). Pondérées par strate, elles correspondent à **une centaine d'aperçus distincts** sur le site, peut-être 130. L'échantillon est petit : c'est un ordre de grandeur, pas un compte.
- **Le drapeau ⚑ ne fait guère mieux que le hasard** : 8 erreurs sur 61 aperçus marqués, soit 13 %. Il donne aussi deux faux positifs : « מִבָּרוּךְ שֶׁאָמַר » (51 (נ״א):4) et « מוֹתַר הָאָדָם » (115 (קט״ו):1). Il sert à ouvrir d'abord certains aperçus, il ne remplace pas la règle.
- **La plupart de ces condensations sont fidèles en substance.** Leur défaut tient à leur forme : elles occupent la place du texte et en prennent l'apparence, sans le dire.

### Les 12 erreurs de sens trouvées

Toutes figurent dans les trois langues. Elles sont à soumettre au Rav, ou à faire disparaître par la règle (voir 3).

| Séif | Ce que dit l'aperçu | Ce que dit le séif |
|---|---|---|
| **75 (ע״ה):7** | « עֶרְוַת גּוֹי וְקָטָן — אָסוּר (וְיֵשׁ מַתִּירִין בְּקָטָן) » | **Psak inversé.** Après l'avis strict, l'Admour HaZaken écrit « וְיֵשׁ מַתִּירִין כְּנֶגֶד עֶרְוַת קָטָן … וְכֵן עִקָּר » : il permet jusqu'à neuf ans et un jour, et en tire la conséquence pour la brit. L'aperçu donne pour règle l'avis qu'il écarte. |
| **186 (קפ״ו):4** | « הַיּוֹדֵעַ לְבָרֵךְ אֵינוֹ יוֹצֵא בִּשְׁמִיעָה » | « אֵינוֹ רַשַּׁאי לָצֵאת בִּשְׁמִיעָה … אֶלָּא עַל יְדֵי זִמּוּן בִּשְׁלֹשָׁה ». Le séif interdit a priori et prévoit une exception. L'aperçu en fait une absence d'acquittement, sans l'exception. |
| **76 (ע״ו):11** | « קָרָא וּמָצָא צוֹאָה — חוֹזֵר » | Il ne recommence que « בְּמָקוֹם שֶׁרָאוּי לְהִסְתַּפֵּק בּוֹ בְּצוֹאָה ». Sinon, « אֵין צָרִיךְ לַחֲזֹר ». |
| **192 (קצ״ב):6** | « טָעָה בַּעֲשָׂרָה וְלֹא הִזְכִּיר הַשֵּׁם — אֵינוֹ חוֹזֵר » | « אֲבָל אִם עֲדַיִן לֹא עָנוּ אַחֲרָיו … יַחֲזֹר הַמְבָרֵךְ וִיזַמֵּן בְּשֵׁם ». |
| **167 (קס״ז):10** | « הַמְסֻבִּין שֶׁשָּׂחוּ קֹדֶם שֶׁטָּעֲמוּ — חוֹזְרִים וּמְבָרְכִים » | Seulement « אִם שָׂח בְּדָבָר שֶׁאֵינוֹ מֵעִנְיַן צָרְכֵי סְעוּדָה ». Pour qui a parlé des besoins du repas, l'aperçu prescrit une bénédiction de trop. |
| **38 (ל״ח):7** | « כּוֹתְבֵי סְתָ"ם … — פְּטוּרִים » | « פְּטוּרִין מֵהֲנָחַת תְּפִלִּין כָּל הַיּוֹם, זוּלַת בִּשְׁעַת קְרִיאַת שְׁמַע וּתְפִלָּה ». L'exception a disparu. |
| **40 (מ׳):1** | « וּבְאַקְרַאי הָאוֹחֵז בְּיָדוֹ אֵין לְהַקְפִּיד » | Seulement quand ce sont les courroies qui pendent : « אֲבָל אִם הַתְּפִלִּין תְּלוּיִים — אָסוּר אֲפִלּוּ בְּאַקְרַאי ». |
| **53 (נ״ג):36** | « רָאוּי לְהִתְפַּלֵּל מִתּוֹךְ הַסִּדּוּר הַמְיֻחָד לַצִּבּוּר » | « יֵשׁ מִי שֶׁאוֹמֵר שֶׁרָאוּי לִשְׁלִיחַ צִבּוּר », puis « אֲבָל בְּהַנִּדְפָּסִין אֵין חִלּוּק ». L'aperçu fait d'un avis isolé une règle, étend au premier venu ce qui vise l'officiant, et omet la conclusion qui rend la règle sans objet aujourd'hui. |
| **25 (כ״ה):39** | « בְּיוֹם קְרִיאַת הַתּוֹרָה — אֵין לְחָלְצָן עַד … » | « וְהוּא מָקוֹם שֶׁמַּחֲזִירִין … — נוֹהֲגִין שֶׁלֹּא לְחָלְצָן ». L'aperçu donne pour règle un minhag local et omet la condition de lieu. |
| **162 (קס״ב):1** | « סֵדֶר נְטִילָה מֵרְבִיעִית — שְׁתֵּי שְׁפִיכוֹת עַל כָּל יָד » | Verser le revi'it d'un coup sur les deux mains suffit (« נִטְהֲרוּ יָדָיו »). Deux versements ne sont exigés que pour qui lave chaque main séparément avec un seul revi'it. |
| **69 (ס״ט):7** | « … בְּעַרְבִית — מֻתָּר » (interrompre entre גאולה et תפילה) | Permis à ‘arvit « לְהוֹצִיא אֲחֵרִים יְדֵי חוֹבָתָן בְּ״בָרְכוּ״ ». L'aperçu en fait une permission générale. |
| **174 (קע״ד):7** | « כּוֹס שֶׁל בִּרְכַּת הַמָּזוֹן פּוֹטֵר מַשְׁקִין שֶׁלְּפָנֶיהָ » | Si l'on a l'intention de dire le birkat hamazon sur une coupe, on est dispensé de la **bénédiction finale** (« בְּרָכָה אַחֲרוֹנָה ») sur les boissons d'avant le repas. L'aperçu ne dit ni quelle bénédiction ni à quelle condition. |

**Les aperçus imprécis :**

- **Attribution omise :**
  - 183 (קפ״ג):3, « יֵשׁ אוֹמְרִים » ;
  - 90 (צ׳):19, « יֵשׁ מְפָרְשִׁים » ;
  - 95 (צ״ה):2, « יֵשׁ מִי שֶׁאוֹמֵר » ;
  - 100 (ק׳):1, un « לִמּוּד זְכוּת » sur l'usage donné pour la règle.
- **Conditions omises sans renversement :** 25 (כ״ה):31, la reprise « מִיָּד » et l'intention de remettre aussitôt.
- **Mot ambigu ou objet manquant :**
  - 81 (פ״א):3 : « וְיַרְחִיקֶנָּה » pour « יֵלֵךְ לְפָנָיו כְּדֵי שֶׁיִּזְרְקֶנָּה מֵאַחֲרָיו » ;
  - 188 (קפ״ח):16 : « וְשָׁכְחוּ » sans complément.

## 3. La règle proposée

**R-APERÇU.** Un aperçu est fait de **mots du séif, verbatim, dans l'ordre, et toute coupe y est déclarée par « … »**. C'est la convention des citations du dépôt, appliquée au titre.

1. **Les segments.** Chaque segment entre deux « … » est une suite de mots consécutifs du `.sa-he` du bloc, et les segments se suivent dans l'ordre du séif.
2. **Les coupes.** Un aperçu qui ne commence pas au premier mot s'ouvre sur « … ». Un aperçu qui s'arrête avant la fin se ferme sur « … », et c'est là seulement qu'un mot peut être coupé. Pas de « … » là où rien n'est omis.
3. **Le chapeau.** Seul le chapeau du siman (« … וּבוֹ N סְעִיפִים: ») peut être omis sans « … », en tête du séif 1.
4. **Ce qui est admis sans confrontation :** un titre sans lettre hébraïque, une note entièrement entre crochets, l'absence d'aperçu, et une **condensation marquée** qui commence par « תַּמְצִית: ». C'est le marqueur des niveaux 4 hébreux, où il paraît 200 fois dans 30 pages sous la forme `<em>תמצית</em> :`. Dans le titre, il s'écrit sans `<em>` : `verify-oh-source.py` n'y admet que des `<span>`. Une condensation marquée n'est pas jugée verbatim, comme les cellules « résumé : » des tableaux.

**Deux façons de mettre les pages en règle, à décider (rien n'est appliqué) :**

- **A, recommandée : remplacer chaque aperçu non conforme par le début de son séif.**
  - On prend les premiers mots du `.sa-he` de la même page, avec son nikoud, coupés à la longueur des aperçus conformes (11 à 14 mots, médiane 13), suivis de « … ». C'est la forme que portent déjà 5 554 aperçus, dont 5 007 des 5 114 aperçus confrontés de Chabbat.
  - L'opération est mécanique : aucun jugement halakhique, aucun risque de fabrication. Les 12 erreurs ci-dessus disparaissent, et la parité des langues revient d'elle-même, puisque les trois `.sa-he` sont identiques.
  - Seul le texte de `span.seif-preview` change : ni CSS, ni `style=`, ni classe, ni balise. Aucune empreinte de `verify-oh-source.py` n'est touchée (CSS_ADMIS, STYLES_EN_LIGNE_ADMIS, CLASSES_ADMISES, TAGS_ADMIS).
  - Ce qu'on perd : la décision lisible d'un coup d'œil dans le titre. Elle reste dans la traduction et dans les explications de la page.
- **B : garder les condensations et les marquer « תַּמְצִית: ».** La porte les admet aussitôt. Mais il faudrait alors faire relire par le Rav 1 312 condensations distinctes (947 « mot absent », 278 abrégés, 87 reformulés) : 12 erreurs de sens sur 117 lues montrent que la marque seule ne suffit pas. Le marqueur hébreu apparaîtrait aussi dans les titres des pages FR et EN.

Dans les deux cas, les 113 coupes non déclarées et les 7 « … » sans coupe se corrigent mécaniquement : on ajoute ou on retire « … », ou on remet le premier mot omis.

## 4. La porte

```bash
python3 scripts/verifier-apercus.py                  # Orah Haïm et Chabbat, trois langues, ~6 s, hors réseau
python3 scripts/verifier-apercus.py 75 186 --lignes  # chaque aperçu non conforme, avec le début de son séif
python3 scripts/verifier-apercus.py --json FICHIER   # un enregistrement par bloc
```

- **Codes de sortie :**
  - 0 : tout aperçu est conforme ;
  - 1 : au moins un aperçu est non conforme. C'était le cas au premier balayage : 3 955 aperçus, 181 simanim ;
  - 3 : une page est illisible, ou aucun aperçu n'a été confronté.
- **Ce qu'elle ne couvre pas :**
  - la justesse d'une coupe déclarée : « A… B » verbatim peut sauter la condition qui retourne A. C'est la famille de `verifier-troncatures.py`, qui ne lit pas les aperçus ;
  - le sens d'une condensation marquée ;
  - l'étiquette « סעיף X », contrôlée par `verifier-alignement.py`.
- **Épreuves.** La porte a été éprouvée sur 18 témoins construits, tous classés comme attendu. On y trouve le témoin de l'arbitre (« כְּשֵׁרָה » pour « פְּסוּלָה »), des mots du séif permutés (« חַיָּב » à la place de « פָּטוּר »), et un mot ajouté hors de `span.seif-preview`, dans `span.seif-num`, dans un `<span>` imbriqué, dans un `<summary>` nu, derrière des lettres latines ou entre crochets. La note entre crochets n'est admise que sur un séif vide.
- **Depuis la correction (section 5),** elle sort verte, et doit le rester sur chaque nouveau lot.

## 5. La correction A, appliquée le 13 octobre 2026

`scripts/fix-apercus.py` remplace chaque aperçu non conforme par le début de son séif. Par défaut, il ne fait que simuler ; il n'écrit dans les pages qu'avec `--appliquer`. Il a été appliqué le 13 octobre 2026, à la demande de l'utilisateur, après simulation et contre-épreuve sur une copie du dépôt.

**La forme de l'aperçu** est celle du générateur du dépôt (`generate-niveau-4.py`, `_seif_preview`), qui a produit les aperçus de Chabbat : le texte du séif coupé à 110 caractères au plus, sur une frontière de mot, suivi de « … » quand le séif continue. Ce texte est pris dans le `.sa-he` de la page elle-même. Trois écarts, voulus :

- au séif 1, le chapeau du siman est sauté ;
- la coupe ne laisse ni virgule ni tiret avant « … » ;
- la coupe s'arrête avant une « … » de la source ou avant un dessin de lettre. Sans cela, l'aperçu de 36 (ל״ו):2 enjamberait les 27 dessins sans le dire ; il devient « זוֹ תְּמוּנַת הָאוֹתִיּוֹת… ».

**La parité.** Pour chaque séif dont une langue au moins porte un aperçu non conforme, l'aperçu est réécrit dans les trois langues. Seuls les titres anglais et les `<summary>` nus, admis, sont laissés tels quels.

**Ce qui a été réécrit :**

- **537 pages, 1 362 séifs, 4 029 aperçus réécrits** : les 3 955 non conformes, plus 74 aperçus conformes réécrits pour que les trois langues portent le même ;
- **les 1 362 séifs** reçoivent le même aperçu dans les trois langues. À 128 (קכ״ח) et 355 (שנ״ה), l'ordre des signes de nikoud diffère d'une page à l'autre, pas ce qui s'affiche ;
- longueur : 13 mots en médiane, de 3 (36:2) à 17.

Le relevé avant/après, un séif par entrée, est dans `audit/apercus-correction-A.txt`. Il garde le texte des condensations écrites à la main pour Orah Haïm, qui ne figurera plus que là.

**Vérifications faites par le script, page par page, avant toute écriture :**

- chaque aperçu réécrit est conforme ;
- les autres aperçus gardent leur classe ;
- la lecture de `verify-oh-source.py` est inchangée : mêmes blocs, même empreinte du `.sa-he`, même empreinte du CSS, mêmes fautes de forme ;
- le fichier ne change qu'à l'intérieur des `span.seif-preview` visés.

Aucune page n'est refusée.

**Contre-épreuve sur une copie du dépôt corrigée** (dans le scratchpad, pas dans `sources/`) :

| Porte | Résultat sur la copie |
|---|---|
| `verifier-apercus.py` | 0 non conforme sur 9 830 (code 0) |
| `verify-oh-source.py --tous`, contre Sefaria | 365 simanim conformes, 0 divergent |
| `verifier-balises.py` | même bilan que l'original : 0 défaut |
| `verifier-classes.py` | même bilan que l'original : 0 défaut |
| `verifier-langues.py` | même bilan que l'original |
| `verifier-alignement.py` | même bilan que l'original : 0 écart |
| `diff` copie / original | 537 fichiers changés, 0 ligne changée hors d'un `span.seif-preview` |

**Après application, sur les pages réelles :**

| Porte | Résultat |
|---|---|
| `verifier-apercus.py` | 0 non conforme sur 9 830 |
| `verify-oh-source.py --tous`, contre Sefaria | 365 simanim conformes, 0 divergent |
| `verifier-balises.py`, `verifier-classes.py`, `verifier-langues.py` | 0 défaut sur 7 707 pages |
| `verifier-integrite.py` | aucune régression face à `origin/main` |
| `audit-simanim.py` | 272 simanim conformes |
| `verifier-alignement.py` | 24 écarts, tous antérieurs : niveau 1 de Chabbat 248, 259, 263, 264 et de Yoré Déa 89, 90, 101, 183, 190, pages non touchées |

**Ce qui n'a pas été fait :**

- **le rendu Chromium (`--rendu`) des 181 simanim corrigés.** Il n'a été fait que sur 4 d'entre eux : 36 (ל״ו), avec ses dessins de lettres, 75 (ע״ה), 128 (קכ״ח), le plus long, et 355 (שנ״ה). Les quatre sont conformes, à cinq largeurs d'écran, sur la copie corrigée. Le rendu complet (environ 2 h) a été arrêté à la demande de l'utilisateur. Seul le titre des blocs change, le CSS est figé et le texte des séifs est intact, mais la clause de publication de CLAUDE.md exige ce rendu avant toute mise en ligne sur `main` ;
- **la parité des 454 séifs restants.** Les trois langues y portent des aperçus conformes mais différents. La correction n'y touche pas.
