# Niveau 4 de Chabbat — cinq simanim, dix-sept questions au Rav

Établie le 15 octobre 2026, sur main `f6bccca1` (les cinq simanim n'ont pas changé depuis le 9 octobre 2026).

**Aucune page n'a été modifiée.** Les cinq simanim ci-dessous (257, 261, 268, 278, 279) portent au niveau 4 — « Daat HaRav », la page qui présente la chitah de l'Admour HaZaken — des conduites pratiques que le Choul'han Aroukh HaRav ne dit pas, ou dont il dit le contraire, sur la page même qui reproduit son texte. Chacun touche une conduite (ce qu'on fait, ce qu'on ne fait pas), dans les trois langues.

D'où ils viennent : 257 et 261 sont deux des « points les plus urgents » de [`GUIDE-CORRECTIONS.md`](GUIDE-CORRECTIONS.md) (H-257-01, H-261-01) ; 268 et 278 sont relevés en 🔴 dans [`relecture-rav.md`](relecture-rav.md) (H-268-01 à 05, H-278-01 à 06) ; 279 a été trouvé lors de l'état des lieux du 15 octobre 2026. Les dossiers en ont retrouvé d'autres sur les mêmes pages : ils sont dans la partie « Autres constats » de chaque dossier complet, hors de cette décision.

## Comment chaque dossier a été établi

- Le texte source a été **retéléchargé de Sefaria le 15 octobre 2026** : Choul'han Aroukh HaRav dans l'édition vocalisée de Kehot (celle que recopient les pages), Choul'han Aroukh dans Maginei Eretz et Torat Emet 363, Michna Beroura, Guemara (William Davidson).
- Chaque dossier a été rédigé, puis contrôlé par **deux vérificateurs adverses** — l'un sur la fidélité à la source (la citation est-elle verbatim, à la bonne adresse ? le défaut est-il réel, ou la page dit-elle vrai sous une lecture que le dossier rate ?), l'autre sur les corrections et leur propagation dans tout le site —, puis **arbitré**, chaque objection revérifiée sur Sefaria. Les citations hébraïques des textes proposés sont des sous-chaînes exactes de la source ; pour 257, les textes ont en plus été appliqués à une copie du dépôt, portes vertes.
- Les options sont **rédigées dans les trois langues** et prêtes à appliquer ; elles ne disent rien de plus que la source, et quand une option ajoute un élément (un usage, une remarque), elle le dit.
- Ce que chaque dossier **n'a pas pu vérifier** est écrit sous la question (Siddour de l'Admour HaZaken, Notes de Kehot, etc.).

## Comment répondre

Pour chaque question : la lettre ou le numéro de l'option, ou « oui / non » quand la question est fermée. Une option peut être modifiée : dites-le, et le texte sera refait puis revérifié avant publication. Rien ne sera publié sur `main` sans ces réponses, ni avant que les portes de source (`verify-oh-source.py --rendu`, `verifier-citations.py --langues fr,he,en`, etc.) soient vertes sur le lot corrigé.

## Les dix-sept questions

| Q | Siman | Ce qui est faux | Recommandé |
|---|---|---|---|
| [Q1](#point-257-p1) | 257 | Niveau 4, section למעשה, puce ② : « sable froid = OK » contredit le séif 5 du Choul'han Aroukh HaRav reproduit sur la même page (H-257-01) | Option A, dans les trois langues, appliquée avec l'option A du 257-P2 (les deux ont été mesurées ensemble sur une copie : portes vertes, voir la description de l'option) |
| [Q2](#point-257-p2) | 257 | Niveau 4, tableau « La force du psak » : paraphrase donnée entre guillemets comme citation du Mehaber, parole du Mehaber attribuée au Rama, exemples et qualificatifs absents de la source (H-257-02) | Option A : elle donne au lecteur le texte même, corrige l'attribution en la montrant, et ses citations sortent conformes à la porte (mesure sur copie) |
| [Q3](#point-257-p3) | 257 | Papier aluminium : rangé parmi ce qui n'ajoute pas de chaleur dans tous les niveaux du siman 257 et le blog, sans source dans le siman (décision distincte du 257-P1) | Option A : elle garde l'information pratique sans la prêter au Rav, supprime le qualificatif « secs » que la source ne connaît pas, et laisse au niveau 2 son raisonnement rattaché à 257:2 / MB ס״ק יד |
| [Q4](#point-257-p4) | 257 | Métadonnées de l'index, data/simanim/siman-257.json et llms.txt : « matériaux permis (papier alu, torchon froid) vs interdits (couverture isolante chauffante) » | Option A, appliquée dans le même lot que 257-P1 et 257-P2 (index FR/HE/EN, data/simanim/siman-257 |
| [Q5](#point-261-n4-p4-allumage-bein-hachmachot) | 261 | Le point ④ du « למעשה » du niveau 4 permet à un Juif d'allumer à בין השמשות, « sans bracha si trop tard », et donne pour référence 261:5-6. Le Choul'han Aroukh HaRav dit le contraire | Option 1, ou l'option 4 si le Rav veut que le « למעשה » dise aussi comment éviter le retard |
| [Q6](#point-261-n4-18-minutes-et-adresses) | 261 | Le niveau 4 attribue au Choul'han Aroukh HaRav « 18 minutes » (261:3-4, 261:5-6), « 40 minutes » à Jérusalem et les fuseaux horaires (« רס״א chitah »). Il place la tossefet aux séifs 3-4, et la même attribution passe dans les index, data/simanim/siman-261.json, index.md et llms.txt | Option 2 |
| [Q7](#point-261-n2he-chitah-et-allumage-apres-chekia) | 261 | Le niveau 2 hébreu, qui n'a pas été réécrit comme les pages FR et EN, attribue à l'Admour HaZaken la « שיטת הגאונים » et admet, sans source, l'allumage après la chekia « במקרה דחוק » | Option 1 : c'est la seule qui rétablisse la parité, et la page FR a déjà été réécrite sur la source |
| [Q8](#point-268-a) | 268 | Niveau 4 : point ③ « Oubli de Retsé : retour aux 1er et 2e repas » et hidoush ב « hiérarchie des reprises ». Une loi du Birkat Hamazon (siman 188) est greffée sur la tefilla de Chabbat sous un renvoi רס״ח:9-13 qui ne la contient pas | Option A, avec la variante (i) pour le sous-titre |
| [Q9](#point-268-b) | 268 | Niveau 4 : hidoush א et point ① — « il faut le dire avec un autre Juif (témoignage à 2) » et « si oubli, retrouver un autre Juif pour le réciter ensemble », attribués à l'Admour HaZaken | Option A, et C si le Rav retient aussi l'option A de 268-A |
| [Q10](#point-268-c) | 268 | Niveau 4 : point ② « Confusion semaine/Shabbat dans Amida : reprendre dès qu'on s'aperçoit » — conduite inversée par rapport à SA HaRav 268:2, et renvoi רס״ח:4-8 inexact | Option A |
| [Q11](#point-268-d) | 268 | Niveau 4 : point ④ « Magen Avot à arvit : ne pas oublier dans la synagogue » — formule sans contenu dans la source, et renvoi רס״ח:14-18 qui ne traite pas de Magen Avot | Option A |
| [Q12](#point-278-a) | 278 | Niveau 4 : le « חידוש א » (« Le malade lève les שבותים ») et le למעשה qui en découle contredisent le SA HaRav 278:1 et 278:3 reproduits sur la même page ; la phrase « Application directe : שבות במקום חולה » se propage jusqu'au catalogue /oh/ | Option A2, appliquée d'un seul tenant dans les trois langues |
| [Q13](#point-278-b) | 278 | Niveau 3 (et explications du niveau 1) : phrase attribuée entre guillemets à la Michna Beroura ס״ק א, « פשוט הוא דלא רק מותר אלא חובה לכבות », qui n'existe pas ; explications des ס״ק א et ב qui ne correspondent pas à leur texte | Option B1 |
| [Q14](#point-278-c) | 278 | Niveau 2 (et tableau du niveau 3) : « אמר רב יהודה: מכבין את הנר מפני חולה כדי שיישן » (שבת ל׳ ע״א) — citation inexistante, sous une fausse adresse et un faux locuteur ; Rashi sous un dibbour inexistant | Option C1 |
| [Q15](#point-278-d) | 278 | Niveau 4, traduction du séif 1 (FR l.386, EN l.384) : parenthèse ajoutée et confuse en FR, « חֲשַׁשׁ » non rendu en EN — le seuil du heter est mal traduit | Option D1, en même temps que le point 278-a, pour que la traduction et le hidoush (ou son retrait) disent le même seuil |
| [Q16](#point-279-a) | 279 | Niveau 4 : « la bougie change de statut quand elle s'éteint naturellement » — généralisation fausse, dans les trois langues, contraire au séif 1 du Choul'han Aroukh HaRav | Option A |
| [Q17](#point-279-b) | 279 | Niveau 4, point ③ du למעשה : « le bougeoir suit le statut de la bougie », référencé 279:7-9 — référence fausse, énoncé incomplet | Option A, dans la même édition que 279-A, pour que la liste du למעשה ne garde aucune référence fausse |

## Siman 257

Dossier complet (texte source, analyse, propagation, textes FR/HE/EN de chaque option, autres constats) : [`niv4-chabbat-urgent/siman-257.md`](niv4-chabbat-urgent/siman-257.md).

<a id="point-257-p1"></a>

### Q1 — 257-P1

**Niveau 4, section למעשה, puce ② : « sable froid = OK » contredit le séif 5 du Choul'han Aroukh HaRav reproduit sur la même page (H-257-01)**

_Où :_ `sources/shabbat/siman-257/niveau-4-daat-harav.html` l. 639 · `sources/shabbat/siman-257/niveau-4-daat-harav-he.html` l. 532 · `sources/shabbat/siman-257/niveau-4-daat-harav-en.html` l. 551 · `sources/shabbat/siman-257/niveau-4-daat-harav.html` l. 429-430 · `sources/shabbat/siman-257/niveau-4-daat-harav.html` l. 573

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 257:5**

> אֵלּוּ הֵם דְּבָרִים הַמּוֹסִיפִים הֶבֶל, פְּסֹלֶת שֶׁל זֵיתִים וְשֶׁל שֻׁמְשְׁמִין לְאַחַר שֶׁהוֹצִיאוּ שַׁמְנָן, וְזֶבֶל, וּמֶלַח, וְסִיד, וְחוֹל, בֵּין שֶׁהֵם לַחִים בֵּין שֶׁהֵם יְבֵשִׁים, וְתֶבֶן, וְזָגִין דְּהַיְנוּ פְּסֹלֶת שֶׁל עֲנָבִים לְאַחַר שֶׁהוֹצִיאוּ יֵינָם, וּמוֹכִין (פֵּרוּשׁ כָּל דָּבָר רַךְ קָרוּי מוֹכִין, כְּגוֹן צֶמֶר גֶּפֶן וּתְלִישֵי צֶמֶר רַךְ שֶׁל בְּהֵמָה, וּגְרִידַת בְּגָדִים בְּלוּיִים), וַעֲשָׂבִים, בִּזְמַן שֶׁאַרְבַּעְתָּן לַחִים, אֲפִלּוּ הֵם לַחִים מֵחֲמַת מַיִם צוֹנְנִים שֶׁנָּפְלוּ עֲלֵיהֶם. <br>אֲבָל כָּל מִינֵי כְּסוּת, וּפֵרוֹת, וְנוֹצוֹת כָּל הָעוֹפוֹת, וּנְעֹרֶת שֶׁל פִּשְׁתָּן דַּקָּה, וּנְסֹרֶת שֶׁל חָרָשִׁים, וְעוֹרוֹת, בֵּין עֲבוּדִין בֵּין שֶׁאֵינָן עֲבוּדִין, וְגִזֵּי צֶמֶר — אֵינָן מוֹסִיפִים הֶבֶל בְּכָל עִנְיָן:

Voici les choses qui ajoutent de la chaleur : le résidu des olives et du sésame après qu'on en a extrait l'huile, le fumier, le sel, la chaux et le sable, qu'ils soient humides ou secs ; la paille, et les zaguin, c'est-à-dire le résidu des raisins après qu'on en a extrait le vin, et les moukhin (explication : toute chose molle est appelée moukhin, comme le coton, les touffes de laine douce d'animal et les raclures de vêtements usés), et les herbes, lorsque ces quatre sont humides, même s'ils sont humides à cause d'eau froide tombée sur eux. Mais toutes sortes de vêtements, les fruits, les plumes de tous les oiseaux, l'étoupe de lin fine, la sciure des charpentiers, les cuirs, tannés ou non, et les toisons de laine n'ajoutent de chaleur en aucun cas.

_(et 10 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Réécrire la puce d'après 257:5 avec ses limites (recommandée)** — Remplace la puce ② par ce que le Rav dit des deux matières qu'elle nomme, sans absolu (« pas », non « jamais »), chaque citation suivie de son adresse exacte. Le papier aluminium n'est plus nommé (sa place dans le reste du site est la décision 257-P3). Mesuré sur une COPIE du siman hors dépôt (avec l'option A du 257-P2) : verifier-citations --langues fr,he,en → 177 citations, 148 conformes, 0 variante, 0 référence fausse, 0 introuvable, 29 sans référence (29 avant : aucune citation nouvelle n'y part) ; verifier-etiquettes 257 → 0 anomalie ; verifier-langues → 0 ; verifier-troncatures → 0 trou, 4 coupures, les mêmes qu'avant (niveau 2, Taz et Beit Yossef).
- **B — Correction courte : corriger l'erreur et le renvoi, sans plus** — Rend la puce conforme au séif 5 (sable interdit, étoffe non), retire « froid » et le papier aluminium, sans absolu. Plus courte, mais ne dit pas les limites du tissu (Chabbat même, foyer à braises) : le lecteur peut lire « permis » sans condition. Aucune citation, rien à confronter.
- **C — Supprimer la puce ②** — Retirer la ligne dans les trois langues, la section 1 de la page (qui reproduit 257:5) parlant seule. Aucun risque d'affirmer ce que la source ne dit pas, mais la conduite pratique perd la seule puce qui nommait les matières. À combiner avec le sort des puces ①③④⑤ (autres constats).

**Recommandation.** Option A, dans les trois langues, appliquée avec l'option A du 257-P2 (les deux ont été mesurées ensemble sur une copie : portes vertes, voir la description de l'option). La métadonnée de l'index suit au 257-P4 ; le sort de l'aluminium dans le reste du site est la décision distincte 257-P3. Après application dans le dépôt : verify-oh-source.py 257 --rendu (non lancé : les textes ne touchent pas le .sa-he, mais la règle l'exige avant publication), verifier-citations.py --path sources/shabbat/siman-257 --langues fr,he,en, verifier-etiquettes.py 257, verifier-langues.py, verifier-troncatures.py --path sources/shabbat/siman-257.

**Question.** Validez-vous le remplacement de la puce ② du niveau 4 (FR l. 639, HE l. 532, EN l. 551) par le texte de l'option A — sable = מוסיף הבל, humide ou sec, on n'y enveloppe pas même un plat froid ni de jour ; étoffes permises avant Shabbat, avec les limites de 257:2-4, 9-10 (plat encore brûlant dans sa marmite d'origine, bein hachmachot, enveloppement complet, foyer à braises) — oui ou non ?

**Non vérifié.** (1) Assimiler un torchon ou une couverture à « כְּסוּת » est une application, non un mot de la source ; la Michna Beroura ס״ק כ étend « כסות » aux « כרים וכסתות וגיזי צמר », pas nommément au torchon : l'option A dit « étoffe/vêtements ». (2) Le texte n'écrit pas « jamais » ni « toujours interdit » : le Rav rapporte au séif 1 des avis indulgents (il n'empêche pas l'usage qui les suit, et retient le dernier « בְּדִיעֲבַד » seulement), permet au séif 7 les rochers, qui ajoutent de la chaleur, parce que l'usage en est rare, et au séif 12 l'enveloppement même au milieu des braises dans un four scellé d'argile. L'option A ne les mentionne pas, la puce ne portant que sur le sable et le tissu. (3) Le séif 8 (recouvrir Chabbat ce qui était déjà enveloppé à l'entrée de Chabbat) a été retiré du texte : la première version omettait sa condition (« וְהוּא שֶׁנִּתְבַּשְּׁלָה הַקְּדֵרָה כָּל צָרְכָּהּ » quand la marmite est sur un foyer à braises). (4) « l'interdit vise l'enveloppement complet » repose sur le Kountress Aharon 257, 2 (« לכולי עלמא לא מיתסר אלא כשמטמין כולו ») et sur la parenthèse du séif 4 ; le corps du séif 2 ne le dit pas en propres termes. (5) La Michna Beroura n'existe sur Sefaria que dans l'édition « On Your Way » ; sa citation (apostrophes ASCII comprises) n'est pas destinée à la page. Son ס״ק יט rapporte que plusieurs aharonim limitent l'interdit des matières humides à celles qui le sont d'elles-mêmes, quand le Rav écrit « אֲפִלּוּ הֵם לַחִים מֵחֲמַת מַיִם צוֹנְנִים » : cela concerne les quatre matières humides, pas le sable, et l'option n'en dit rien. (6) Les portes ont été passées sur une copie hors dépôt, non sur le dépôt ; verify-oh-source --rendu n'a pas été lancé.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-257-p2"></a>

### Q2 — 257-P2

**Niveau 4, tableau « La force du psak » : paraphrase donnée entre guillemets comme citation du Mehaber, parole du Mehaber attribuée au Rama, exemples et qualificatifs absents de la source (H-257-02)**

_Où :_ `sources/shabbat/siman-257/niveau-4-daat-harav.html` l. 570 · `sources/shabbat/siman-257/niveau-4-daat-harav.html` l. 571 · `sources/shabbat/siman-257/niveau-4-daat-harav.html` l. 573 · `sources/shabbat/siman-257/niveau-4-daat-harav-he.html` l. 465, 466, 468 · `sources/shabbat/siman-257/niveau-4-daat-harav-en.html` l. 482, 483, 485 · `(porte, état actuel)` l. -

_Source principale :_ **Shulchan Arukh, Orach Chayim 257:1 (Mehaber)**

> אין טומנין בשבת אפילו בדבר שאינו מוסיף הבל אבל בספק חשיכה טומנין בו ואין טומנין בדבר המוסיף הבל אפי' מבעוד יום ואם הטמין בדבר המוסיף הבל התבשיל אסור אפילו בדיעבד ודוקא בצונן שנתחמם או שנצטמק ויפה לו אבל בעומד בחמימותו כשעה ראשונה מותר:

On n'enveloppe pas Chabbat, même dans une chose qui n'ajoute pas de chaleur ; mais au doute de l'obscurité, on y enveloppe. Et on n'enveloppe pas dans une chose qui ajoute de la chaleur, même de jour ; et si l'on a enveloppé dans une chose qui ajoute de la chaleur, le plat est interdit même a posteriori — seulement s'il était froid et s'est réchauffé, ou s'il a réduit et que cela lui est bon ; mais s'il est resté à sa chaleur première, c'est permis.

_(et 3 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Citer verbatim, adresse collée, et rendre au Rama ses gloses (recommandée)** — Les cellules Mehaber et Rama citent le texte réel de l'édition Maginei Eretz (gershayim ״ et geresh ׳ à la place des guillemets et apostrophes ASCII de Sefaria), chaque citation suivie de son adresse ; la cellule du Rav devient une condensation introduite par <em>résumé</em>, avec les limites des séifs 1, 2, 9 et 10, sans exemples inventés. Mesuré sur une copie avec l'option A du 257-P1 : toutes les citations nouvelles sortent CONFORMES ; les trois VARIANTES de la pseudo-citation disparaissent (voir 257-P1). La cellule Mishna Beroura est traitée à part (autres constats).
- **B — Condensations sans guillemets** — Garder la structure du tableau mais remplacer les pseudo-citations par des condensations introduites par <em>résumé</em> / <em>תמצית</em> / <em>summary</em>, sans les qualificatifs inventés. Moins d'information que A, aucune citation à confronter. Cellule du Rav : comme en option A.

**Recommandation.** Option A : elle donne au lecteur le texte même, corrige l'attribution en la montrant, et ses citations sortent conformes à la porte (mesure sur copie). L'appliquer avec l'option A du 257-P1, puis passer, dans le dépôt, verifier-citations.py --path sources/shabbat/siman-257 --langues fr,he,en et verifier-etiquettes.py 257.

**Question.** Validez-vous le remplacement des TROIS cellules du tableau du niveau 4 (FR l. 570, 571, 573 ; HE l. 465, 466, 468 ; EN l. 482, 483, 485) par le texte de l'option A : (a) colonne Mehaber : la pseudo-citation et les qualificatifs « chaux fraîche, fumier en fermentation, sel non vieilli » sont remplacés par le texte réel de 257:1 et 257:3 ; (b) colonne Rama : ses gloses réelles sur 257:1 (shogeg ; pour le lendemain, a posteriori) et 257:3 (rochers), l'interdit de Chabbat même étant rendu au Mehaber ; (c) colonne du Rav : résumé de 257:1-10 avec ses limites, sans « couverture chauffante » ni « torchon froid » — oui ou non (éventuellement cellule par cellule) ?

**Non vérifié.** Le Mehaber écrit « ששלשתן » (trois) là où le SAHaRav écrit « שֶׁאַרְבַּעְתָּן » (quatre) : divergence de compte que la Michna Beroura ס״ק יח explique (« חשיב לתבן וזגין כחדא ») ; aucune option ne la tranche. « ne s'oppose pas à l'usage qui les suit » rend « וּבְמָקוֹם שֶׁנָּהֲגוּ לְהָקֵל … אֵין לִמְחוֹת בְּיָדָם », qui ne vise que le premier avis indulgent ; le second n'est retenu que « בְּדִיעֲבַד » — le résumé dit « des avis indulgents » sans les distinguer. Les portes ont été passées sur une copie hors dépôt.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-257-p3"></a>

### Q3 — 257-P3

**Papier aluminium : rangé parmi ce qui n'ajoute pas de chaleur dans tous les niveaux du siman 257 et le blog, sans source dans le siman (décision distincte du 257-P1)**

_Où :_ `sources/shabbat/siman-257/niveau-1-base.html (+ -he, -en)` l. FR 580 ; HE 477 ; EN 477 · `sources/shabbat/siman-257/niveau-1-base.html (+ -he, -en)` l. FR 616, 697-704, 773, 790 ; HE 478, 513, 519, 594-601, 670, 687 ; EN 513, 594-599, 670, 687 · `sources/shabbat/siman-257/niveau-2-lamdan.html (+ -he, -en)` l. FR 582 ; HE 534 ; EN 582 · `sources/shabbat/siman-257/niveau-3-synthese.html (+ -he, -en)` l. FR 344, 357, 375, 431, 452, 454, 461, 464 ; HE et EN 345, 358, 376, 432, 453, 455, 462, 465 · `blog/hatmana-envelopper-plats-chauds-shabbat.html (+ -he, -en)` l. FR 308 ; HE 307 ; EN 307 · `sources/shabbat/siman-257/niveau-4-daat-harav.html (+ -he, -en)` l. FR 639 ; HE 532 ; EN 551

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 257:5 (seconde moitié)**

> אֲבָל כָּל מִינֵי כְּסוּת, וּפֵרוֹת, וְנוֹצוֹת כָּל הָעוֹפוֹת, וּנְעֹרֶת שֶׁל פִּשְׁתָּן דַּקָּה, וּנְסֹרֶת שֶׁל חָרָשִׁים, וְעוֹרוֹת, בֵּין עֲבוּדִין בֵּין שֶׁאֵינָן עֲבוּדִין, וְגִזֵּי צֶמֶר — אֵינָן מוֹסִיפִים הֶבֶל בְּכָל עִנְיָן:

Mais toutes sortes de vêtements, les fruits, les plumes de tous les oiseaux, l'étoupe de lin fine, la sciure des charpentiers, les cuirs, tannés ou non, et les toisons de laine n'ajoutent de chaleur en aucun cas.

_(et 2 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Ne plus attribuer l'aluminium à la source ; le présenter comme application du site là où il reste (recommandée)** — La liste du niveau 1 reprend les matières de 257:5 et signale à part l'application aux isolants modernes, sans l'attribuer au Rav. Le niveau 2 (déjà raisonné) peut rester. Les autres mentions (N1, N3, blog) sont relues une à une selon le même principe. Texte fermé donné pour la ligne de liste du niveau 1 ; aucune citation.
- **B — Retirer l'aluminium partout** — Supprimer toutes les mentions de l'aluminium (et des isolants modernes) des niveaux 1-4 et du blog du siman 257, dans les trois langues. Aucun risque d'attribution, mais le site perd une question pratique que le lecteur se pose, et le raisonnement du niveau 2 (couvercle / enveloppement) disparaît.
- **C — Le Rav fournit la source** — Si le Rav tient l'aluminium pour une chose qui n'ajoute pas de chaleur selon un poseq qu'il désigne, la mention reste partout, avec cette source exacte ajoutée. Rien n'est écrit tant que la source n'est pas donnée.

**Recommandation.** Option A : elle garde l'information pratique sans la prêter au Rav, supprime le qualificatif « secs » que la source ne connaît pas, et laisse au niveau 2 son raisonnement rattaché à 257:2 / MB ס״ק יד. Les autres mentions (N1, N3, blog : relevé du constat) sont à relire une à une après la décision : un remplacement automatique ne convient pas, certaines étant des cas (couvercle) et non des listes.

**Question.** Pour le papier aluminium dans le siman 257 (niveaux 1, 2, 3 et blog, trois langues) : (A) le garder comme application déclarée du site, non attribuée au Rav, (B) le retirer partout, ou (C) le garder avec une source que vous indiquez — laquelle ?

**Non vérifié.** Le relevé des lignes vient d'un grep (« alu », « aluminum », « נייר כסף », « אלומיניום ») ; quelques lignes peuvent être des ancres internes (href) et non du texte. Des décisionnaires contemporains traitent certainement de l'aluminium ; je ne les ai ni lus ni vérifiés et n'en cite aucun. Le niveau 1 l. 579 (« מוסיף הבל : tout matériau qui peut fermenter, accumuler ou générer de la chaleur (paille fraîche, compost, certains tissus humides) ») porte un critère que la source ne pose pas et range des tissus parmi ce qui ajoute de la chaleur, contre « כָּל מִינֵי כְּסוּת … בְּכָל עִנְיָן » : versé aux autres constats, non traité ici.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-257-p4"></a>

### Q4 — 257-P4

**Métadonnées de l'index, data/simanim/siman-257.json et llms.txt : « matériaux permis (papier alu, torchon froid) vs interdits (couverture isolante chauffante) »**

_Où :_ `sources/shabbat/siman-257/index.html` l. 20, 27, 42 · `sources/shabbat/siman-257/index-he.html` l. 8, 20, 27, 42 · `sources/shabbat/siman-257/index-en.html` l. 20, 27, 42 · `data/simanim/siman-257.json` l. 7 · `llms.txt` l. 141

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 257:5**

> וּמֶלַח, וְסִיד, וְחוֹל, בֵּין שֶׁהֵם לַחִים בֵּין שֶׁהֵם יְבֵשִׁים — אֲבָל כָּל מִינֵי כְּסוּת, וּפֵרוֹת, וְנוֹצוֹת כָּל הָעוֹפוֹת

(Deux extraits séparés par —.) le sel, la chaux et le sable, qu'ils soient humides ou secs — mais toutes sortes de vêtements, les fruits, les plumes de tous les oiseaux [n'ajoutent pas de chaleur].

**Options**

- **A — Texte fermé tiré du séif 5 (recommandée)** — Remplacer, dans chaque champ cité, le seul passage entre « matériaux permis » et « interdits (…) » ; le reste de la description est inchangé. Indépendant de la décision 257-P3 (l'aluminium n'y figure pas).

**Recommandation.** Option A, appliquée dans le même lot que 257-P1 et 257-P2 (index FR/HE/EN, data/simanim/siman-257.json, llms.txt), puis verifier-langues.py (troisième échelle : entête) et npm run build pour régénérer le catalogue.

**Question.** Validez-vous, dans les métadonnées du siman 257 (index FR/HE/EN, data/simanim/siman-257.json, llms.txt), le remplacement de « matériaux permis (papier alu, torchon froid) vs interdits (couverture isolante chauffante) » par « matières qui n'ajoutent pas de chaleur (vêtements, plumes) et matières qui en ajoutent (sable, sel, chaux) », et son équivalent en hébreu et en anglais — oui ou non ?

**Non vérifié.** Le reste des descriptions (« application au cholent moderne », « 13 seifim et 3 entrées de Kountress Aharon ») n'a pas été jugé ici ; le compte 13 séifim / 3 entrées est conforme à Sefaria. La meta description FR et EN l. 8 est tronquée (« … ») avant le passage et n'est pas modifiée.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

## Siman 261

Dossier complet (texte source, analyse, propagation, textes FR/HE/EN de chaque option, autres constats) : [`niv4-chabbat-urgent/siman-261.md`](niv4-chabbat-urgent/siman-261.md).

<a id="point-261-n4-p4-allumage-bein-hachmachot"></a>

### Q5 — 261-N4-P4-allumage-bein-hachmachot

**Le point ④ du « למעשה » du niveau 4 permet à un Juif d'allumer à בין השמשות, « sans bracha si trop tard », et donne pour référence 261:5-6. Le Choul'han Aroukh HaRav dit le contraire**

_Où :_ `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 589 · `sources/shabbat/siman-261/niveau-4-daat-harav-en.html` l. 589 · `sources/shabbat/siman-261/niveau-4-daat-harav-he.html` l. 441

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 261:1**

> סָפֵק חֲשֵׁכָה סָפֵק אֵינָהּ חֲשֵׁכָה, וְזֶהוּ נִקְרָא בֵּין הַשְּׁמָשׁוֹת בְּכָל מָקוֹם, וְהוּא כְּדֵי מַהֲלַךְ ג' רְבִיעֵי מִיל (וְעוֹד מ"ט אַמּוֹת) קֹדֶם צֵאת ג' כּוֹכָבִים בֵּינוֹנִים — אָסוּר לַעֲשׂוֹת בּוֹ מְלָאכָה מִן הַתּוֹרָה, כֵּיוָן שֶׁהוּא סְפֵק לַיְלָה. וְאִם עָשָׂה — חַיָּב אָשָׁם תָּלוּי.

Le doute d'obscurité, quand on ne sait pas si l'obscurité est venue ou non, est ce qu'on appelle partout בין השמשות. Il dure le temps de marcher trois quarts de mil (et encore 49 coudées) avant la sortie de trois étoiles moyennes. Il est interdit d'y faire une mélakha, et c'est un interdit de la Torah, puisque c'est un doute de nuit. Si on l'a faite, on doit un אשם תלוי.

_(et 13 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **Option 1 — Réécrire ④ sur 261:1-2, sans fixer l'heure (recommandée)** — ④ dit ce que disent les séifs 1 et 2 : à בין השמשות on n'allume plus soi-même, et l'on peut dire à un non-Juif d'allumer. La bénédiction et « mieux vaut tard que jamais » sont supprimées. Le point ne dit pas l'heure de בין השמשות : c'est la question (2) au Rav. En HE, les citations sont entre « … », que verifier-citations.py lit (il ne lit pas ״…״). On les recopie du JSON de Sefaria, en écrivant ׳ et ״ là où Sefaria écrit ' et ".
- **Option 2 — Option 1, plus l'endroit où le Rav place בין השמשות et l'avis qu'il rapporte** — Même texte que l'option 1, avec en plus ce que le Choul'han Aroukh HaRav dit de l'heure : בין השמשות, ce sont les trois quarts de mil qui précèdent la sortie des étoiles (261:1). Le temps qui va du début de la chekia jusque-là est celui de la tossefet (261:5). Il rapporte aussi l'avis selon lequel la nuit est complète dès la chekia, puis il conclut que le principal est le premier avis (261:5). Cette option expose le SA HaRav tel qu'il est écrit. Elle s'écarte des niveaux 1 et 3, qui font commencer בין השמשות à la שקיעה. À retenir seulement si le Rav répond (b) à la question (2).
- **Option 3 — Supprimer ④** — On retire la ligne dans les trois langues et on renumérote ⑤ en ④. Le cas du retard reste traité aux niveaux 1 et 3, et le niveau 4 n'en dit plus rien.
- **Option 4 — Option 1, plus la consigne de 261:6** — Même texte que l'option 1, avec en plus la consigne du séif 6 pour celui qui ne connaît pas la mesure. On ne cite que la partie du séif hors parenthèses (« יַדְלִיק הַנֵּרוֹת … »). Le passage entre parenthèses (« צָרִיךְ לְהִסְתַּלֵּק … וְלָכֵן ») est ainsi dans les deux éditions Kehot, et je n'ai pas vérifié ce que signifient ces parenthèses dans cette édition. L'option ne dit pas l'heure de בין השמשות.

**Recommandation.** Option 1, ou l'option 4 si le Rav veut que le « למעשה » dise aussi comment éviter le retard. Le défaut est grave : le point permet, au nom du Rav et comme halakha lema'asse, une mélakha que le Rav interdit de la Torah, et il renvoie à des séifs qui disent le contraire. L'option 1 le corrige avec le texte même du Rav, sans rien y ajouter. Elle ne fixe pas l'heure de בין השמשות : cela relève de la question (2). Si le Rav répond (b), on passe à l'option 2 ; s'il répond (c), il faut d'abord la référence exacte du Siddour. Application : les trois langues dans le même commit. Puis, sans --cache : verifier-citations.py --langues fr,he,en --path sources/shabbat/siman-261 (les citations HE sont entre « … » pour qu'il les lise ; vérifier qu'il les compte bien parmi les citations confrontées), verify-oh-source.py 261 --rendu, verifier-langues.py --path sources/shabbat/siman-261, verifier-balises.py --path sources/shabbat/siman-261 et npm run build.

**Question.** (1) Pour le point ④ du niveau 4 (FR/HE/EN), qui permet aujourd'hui d'« allumer même bein hashemashot, sans bracha si trop tard », retenez-vous l'option 1 (à בין השמשות on n'allume plus soi-même, et l'on peut demander à un non-Juif, 261:1-2), l'option 2 (la même chose, plus la place que le Rav donne à בין השמשות en 261:1 et 261:5), l'option 3 (supprimer) ou l'option 4 (l'option 1, plus 261:6) ? (2) Sur la page du niveau 4, l'heure où commence בין השמשות doit-elle (a) ne pas être dite, (b) être celle du Choul'han Aroukh HaRav 261:1 et 261:5 (trois quarts de mil avant la sortie des étoiles, et la tossefet entre la chekia et ce moment), avec l'avis qu'il rapporte, ou (c) être « à partir de la שקיעה », comme aux niveaux 1 et 3 ? Pour (c), il faudrait la référence exacte du Siddour de l'Admour HaZaken, que ce dossier n'a pas pu vérifier.

**Non vérifié.** (a) Le Siddour de l'Admour HaZaken, auquel les niveaux 1 et 3 attribuent le début de בין השמשות à la שקיעה, n'est pas vérifiable par l'API consultée. Sefaria sert « Siddur Tehilat Hashem », dont l'index ne contient que les prières, sans section de lois sur l'entrée du Chabbat. Je n'en cite donc rien. (b) Je n'ai trouvé aucun poseq qui permette à un Juif d'allumer lui-même à בין השמשות « sans bénédiction » ; je n'en cite aucun. (c) Les « Notes » de l'édition Kehot (ancres <i data-commentator="Notes"> dans le texte) n'ont pas été consultées, ni le sens des parenthèses de 261:6 dans cette édition. (d) L'édition Kehot non vocalisée a été contrôlée pour ברכה et דקות (absents) et pour la parenthèse de 261:6 (présente). Elle n'a pas été confrontée mot à mot. (e) Le cas du siman 263 n'a pas été confronté à sa source.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-261-n4-18-minutes-et-adresses"></a>

### Q6 — 261-N4-18-minutes-et-adresses

**Le niveau 4 attribue au Choul'han Aroukh HaRav « 18 minutes » (261:3-4, 261:5-6), « 40 minutes » à Jérusalem et les fuseaux horaires (« רס״א chitah »). Il place la tossefet aux séifs 3-4, et la même attribution passe dans les index, data/simanim/siman-261.json, index.md et llms.txt**

_Où :_ `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 355 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 513 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 514 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 520 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 521 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 543-547 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 550-556 · `sources/shabbat/siman-261/niveau-4-daat-harav.html` l. 586-588 · `sources/shabbat/siman-261/niveau-4-daat-harav-en.html` l. 355, 513, 514, 520, 521, 543-547, 550-556, 586-588 · `sources/shabbat/siman-261/niveau-4-daat-harav-he.html` l. 222, 368, 369, 375, 376, 397, 401, 404-410, 438-440

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 261:4**

> יֵשׁ אוֹמְרִים שֶׁמִצְוַת עֲשֵׂה מִן הַתּוֹרָה לְהוֹסִיף מֵחֹל עַל הַקֹּדֶשׁ בְּאִסּוּר עֲשִׂיַּת מְלָאכָה בִּכְנִיסַת שַׁבָּתוֹת וְיָמִים טוֹבִים וּבִיצִיאָתָם

Certains disent que c'est une mitsva positive de la Torah d'ajouter du profane au sacré, en s'interdisant la mélakha, à l'entrée des Chabbatot et des fêtes et à leur sortie.

_(et 13 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **Option 1 — Garder 18 et 40 minutes comme usages non attribués au Rav, corriger les adresses** — Les chiffres restent, mais ils sortent de la colonne et des références du Rav. Les adresses deviennent 261:4-5. Le chidouch ב est supprimé (rien dans le siman). ② et ③ sont donnés comme conseil ou usage non écrits. Les cellules MB 513 et 520 reçoivent les ס״ק qui traitent réellement du sujet. Les index et fichiers dérivés retirent l'attribution. Ces usages sont énoncés sans source, sur la seule autorité du Rav du site : il faut son aval.
- **Option 2 — Ne garder que la source : retirer 18 et 40 minutes du niveau 4 (recommandée)** — Le niveau 4 ne dit que ce que dit le Rav, et les usages chiffrés restent aux niveaux 1, 2 et 3. Mêmes corrections que l'option 1 pour l.355, 513, 514, 520, 543-544, 547, pour la suppression du chidouch ב et pour les index et fichiers dérivés. Différences : la dernière phrase de la cellule l.521 disparaît, ① est réécrit sur 261:6, ② et ③ sont supprimés, et ④ et ⑤ deviennent ② et ③. La phrase de ① sur l'heure et quart temporelle (261:5) est entre crochets : on la garde ou on la retire selon la réponse du Rav à la question (3).

**Recommandation.** Option 2. Le niveau 4 a pour objet la chitah du Rav, et les usages chiffrés sont déjà traités comme usages aux niveaux 1, 2 et 3 (niveau 2 FR l.393). Si le Rav tient à ce que le « למעשה » donne un horaire, prendre l'option 1, qui le marque comme usage non écrit dans le SA HaRav. Dans les deux options, corriger data/simanim/siman-261.json en même temps que les trois index.html, ou régénérer ceux-ci avec generate-siman.js --siman 261 --force après avoir relu le diff. Puis lancer : verify-oh-source.py 261 --rendu, verifier-citations.py --langues fr,he,en --path sources/shabbat/siman-261, verifier-etiquettes.py 261 (les cellules MB changent d'adresse), verifier-langues.py, verifier-balises.py, verifier-liens.py (les ancres du chidouch ב disparaissent) et npm run build.

**Question.** (1) Sur le niveau 4 du siman 261, les « 18 minutes » et les « 40 minutes à Jérusalem » doivent-elles être retirées (option 2), ou maintenues comme usages explicitement non attribués au Choul'han Aroukh HaRav (option 1) ? (2) Validez-vous, dans les deux cas, la suppression du chidouch ב (fuseaux horaires, luah, Jérusalem, présentés comme « hidoush du Rav »), le remplacement des cellules MB 261:7-12 et 261:13-15 par MB 261:19-25 et 261:22-23, et la même correction dans les trois index, data/simanim/siman-261.json, index.md et llms.txt ? (3) La consigne de 261:5, « on ne se hâte pas d'allumer avant l'heure et quart temporelle qui précède la sortie des étoiles », doit-elle figurer dans le « למעשה » du niveau 4 (passage entre crochets de l'option 2), compte tenu du calcul exposé à l'analyse (5) ?

**Non vérifié.** (a) Je n'ai trouvé de source vérifiable ni pour l'usage d'allumer 18 minutes avant, ni pour celui des 40 minutes à Jérusalem ; je n'en cite aucune. Les chiffres en minutes de la Michna Beroura 261:22-23 sont cités, et ils ne fondent pas ces usages. (b) La conversion de « שליש שעה פחות חלק ל' » en minutes, et la position de l'heure et quart temporelle par rapport à la chekia (analyse (5)), sont des calculs qui dépendent de conventions (durée du mil, compte des heures temporelles). Je ne les présente pas comme des affirmations de la source. (c) Le passage de 261:1 du Choul'han Aroukh entre parenthèses, en petits caractères et sans « הגה », n'est attribué ici ni au Mehaber ni au Rama. Le crochet [ושיעור מיל…] est une couche de plus, que je n'ai pas identifiée. (d) Je n'ai pas vérifié si generate-siman.js --force régénère d'autres parties d'index.html que celles qui sont citées.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-261-n2he-chitah-et-allumage-apres-chekia"></a>

### Q7 — 261-N2HE-chitah-et-allumage-apres-chekia

**Le niveau 2 hébreu, qui n'a pas été réécrit comme les pages FR et EN, attribue à l'Admour HaZaken la « שיטת הגאונים » et admet, sans source, l'allumage après la chekia « במקרה דחוק »**

_Où :_ `sources/shabbat/siman-261/niveau-2-lamdan-he.html` l. 365 · `sources/shabbat/siman-261/niveau-2-lamdan-he.html` l. 366 · `sources/shabbat/siman-261/niveau-2-lamdan-he.html` l. 367 · `sources/shabbat/siman-261/niveau-2-lamdan-he.html` l. 518

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 261:5**

> שֶׁמִּתְּחִלַּת הַשְּׁקִיעָה עַד צֵאת ג' כּוֹכָבִים הוּא מַהֲלַךְ ד' מִילִין

Du début de la chekia à la sortie de trois étoiles, il y a le temps de marcher quatre mil.

_(et 4 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **Option 1 — Retraduire en hébreu la page FR actuelle du niveau 2 (recommandée)** — La page HE est remplacée par la traduction de la page FR réécrite (les citations hébraïques en restent inchangées), comme l'exige la parité trilingue. Les l.365-367 et 512-520 disparaissent avec le reste de l'ancienne version.
- **Option 2 — Correction minimale des quatre lignes** — On garde la page HE, et on corrige ou supprime seulement les quatre lignes sans source. La parité reste rompue pour le reste de la page.

**Recommandation.** Option 1 : c'est la seule qui rétablisse la parité, et la page FR a déjà été réécrite sur la source. L'option 2 peut servir de mesure d'urgence si la retraduction doit attendre. Dans les deux cas, lancer ensuite verifier-citations.py --langues he --path sources/shabbat/siman-261, verifier-url-langue.py --path sources/shabbat/siman-261 --details et verifier-troncatures.py --path sources/shabbat/siman-261.

**Question.** La page hébraïque du niveau 2 du siman 261 doit-elle être remplacée par une traduction de la page française actuelle (option 1), ce qui retire notamment « אדמו״ר הזקן : מקבל שיטת הגאונים » et la permission d'allumer après la chekia « במקרה דחוק » (l.518), ou seulement corrigée sur ces quatre lignes (option 2) ?

**Non vérifié.** Le Beit Yossef 261 n'a pas été ouvert. Je ne dis donc pas ce qu'il tranche, mais seulement que la page ne l'adresse pas, et que le Mehaber 261:2 compte comme Rabbenou Tam. Le Siddour de l'Admour HaZaken n'a pas pu être vérifié. Les autres « cas » des l.512-520 ne sont pas confrontés.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

## Siman 268

Dossier complet (texte source, analyse, propagation, textes FR/HE/EN de chaque option, autres constats) : [`niv4-chabbat-urgent/siman-268.md`](niv4-chabbat-urgent/siman-268.md).

<a id="point-268-a"></a>

### Q8 — 268-A

**Niveau 4 : point ③ « Oubli de Retsé : retour aux 1er et 2e repas » et hidoush ב « hiérarchie des reprises ». Une loi du Birkat Hamazon (siman 188) est greffée sur la tefilla de Chabbat sous un renvoi רס״ח:9-13 qui ne la contient pas**

_Où :_ `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 663 · `sources/shabbat/siman-268/niveau-4-daat-harav-he.html` l. 624 · `sources/shabbat/siman-268/niveau-4-daat-harav-en.html` l. 646 · `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 624-630 · `sources/shabbat/siman-268/niveau-4-daat-harav-he.html` l. 586-591 · `sources/shabbat/siman-268/niveau-4-daat-harav-en.html` l. 607-613 · `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 355 · `sources/shabbat/siman-268/niveau-4-daat-harav-he.html` l. 340 · `sources/shabbat/siman-268/niveau-4-daat-harav-en.html` l. 340

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 268:10**

> הַטּוֹעֶה בִּבְרָכָה אֶמְצָעִית שֶׁל תְּפִלּוֹת הַשַּׁבָּת וְהֶחֱלִיף שֶׁל תְּפִלָּה זוֹ בְּשֶׁל תְּפִלָּה הָאַחֶרֶת שֶׁל שַׁבָּת, אִם נִזְכַּר קֹדֶם שֶׁסִּיֵּם בְּרָכָה זוֹ שֶׁל תְּפִלָּה הָאַחֶרֶת — צָרִיךְ לִפְסוֹק וְלַחֲזוֹר לְרֹאשׁ בְּרָכָה זוֹ מִתְּפִלָּה שֶׁל עַכְשָׁו. וְאִם סִיֵּם בְּרָכָה זוֹ — אֵינוֹ חוֹזֵר, לְפִי שֶׁעִקַּר בְּרָכָה הָאֶמְצָעִית הוּא "רְצֵה נָא בִמְנוּחָתֵנוּ", שֶׁהוּא שָׁוֶה בְּכָל הַתְּפִלּוֹת:

Celui qui se trompe dans la berakha intermédiaire des tefillot de Chabbat et remplace celle de cette tefilla par celle de l'autre tefilla de Chabbat : s'il s'en souvient avant d'avoir achevé cette berakha de l'autre tefilla, il doit s'interrompre et revenir au début de cette berakha, [celle] de la tefilla du moment. S'il a achevé cette berakha, il ne revient pas, car l'essentiel de la berakha intermédiaire est « Retsé na bimnouhaténou », qui est identique dans toutes les tefillot.

_(et 9 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Remplacer ③ par la vraie loi de 268:10-11, supprimer le hidoush ב, corriger sous-titres, métadonnées et cartes du catalogue (recommandée)** — Le point ③ devient la loi de l'échange des tefillot de Chabbat (le seul « Retsé » du siman). On supprime le bloc du hidoush ב (FR l.624-630, HE l.586-591, EN l.607-613) : aucune ancre n'y renvoie. Dans les sous-titres, métadonnées et cartes, « oubli de Retsé » est remplacé par la formule que le Rav choisit : (i) « échange d'une tefilla de Chabbat contre une autre » (268:10-11, recommandée, parce que « confusion semaine/Shabbat » couvre déjà 268:2-9), ou (ii) « omission de la mention du Chabbat » (268:7-9). Dans index.html (l.147), index.md (l.14) et data/simanim/siman-268.json (l.6-7), on complète la troncature « Cadre conce » par « Cadre conceptuel complet. », sur le modèle de l'EN « A comprehensive conceptual framework » et du HE « מסגרת מושגית מקיפה ».
- **B — Comme A, mais le hidoush ב est remplacé par une « précision » sourcée sur 268:10-11 au lieu d'être supprimé** — Garde deux blocs dans la section 2 de la page. Le mot « hidoush » est retiré, parce que la Michna Beroura (268 ס״ק יד-טו) lit la même distinction dans le Mehaber : ce n'est pas une originalité de l'Admour HaZaken contre les autres poskim. Les ids h3 sont conservés. La ligne sa-he reçoit un titre hébreu, et le titre français ou anglais passe dans la ligne sa-fr ou sa-en, ce qui corrige le défaut de forme relevé en autres_constats (7). Le Mehaber est cité EN ENTIER, avec son « וי״א ».
- **C — Supprimer ③ et le hidoush ב, et mettre à la place un renvoi exact vers le siman 188** — À retenir si le Rav juge utile que le lecteur qui cherche « oubli de Retsé » soit orienté. La loi y est donnée sous sa vraie adresse, sans « (selon Habad) », sans « importance des moments », et avec la raison complète de 188:15. Les sous-titres et les cartes sont corrigés comme dans l'option A.

**Recommandation.** Option A, avec la variante (i) pour le sous-titre. Elle rend au siman ce qu'il dit (268:10-11), retire une attribution au Rav sans fondement dans ce siman, et n'ajoute rien que la source ne dise pas. On prend B si le Rav veut garder un second bloc dans la section 2, sous l'étiquette « עיון / Précision » et non « hidoush », en citant le Mehaber en entier. On ajoute C seulement si le Rav souhaite un renvoi vers le siman 188. Dans tous les cas, il faut corriger en parité FR/HE/EN les sous-titres et métadonnées des 7 fichiers du siman, data/simanim/siman-268.json (avant toute régénération) et les trois cartes du catalogue (sources/shabbat/index{,-he,-en}.html l.1152). Il faut ensuite relancer npm run build, verify-oh-source.py 268 --rendu et verifier-citations.py --path sources/shabbat/siman-268 --langues fr,he,en.

**Question.** (1) Validez-vous l'option A : remplacer le point ③ par la loi de 268:10-11 (échange d'une tefilla de Chabbat contre une autre ; à Moussaf, l'échange n'acquitte pas) et supprimer le hidoush ב sur les repas — oui ou non ? Si non : B (bloc « Précision » sur 268:10-11), C (renvoi au siman 188), ou ni l'un ni l'autre ? (2) Pour le sous-titre, les métadonnées et les cartes du catalogue, quelle formule remplace « oubli de Retsé » : (i) « échange d'une tefilla de Chabbat contre une autre » ou (ii) « omission de la mention du Chabbat » ? (3) Faut-il compléter au passage la troncature « Cadre conce » de l'index FR par « Cadre conceptuel complet. » — oui ou non ?

**Non vérifié.** (1) Je n'ai pas cherché qui, chez les poskim ultérieurs, aurait décrit la règle des repas comme une conduite propre à Habad. Le Mehaber 188:8 et la Michna Beroura ס״ק לא disent la même chose que le SA HaRav 188:15, ce qui exclut une spécificité Habad sur ce point. (2) Le relevé de juillet (audit/relecture-rav.md l.5190) renvoie à « Rama 188:10 / Michna Beroura 188:26-27 ». Dans l'édition Sefaria de la Michna Beroura (On Your Way), le ס״ק sur la troisième seouda est le ס״ק לא ; le Mehaber 188 compte 10 séifim, et le séif 10 n'a pas de glose du Rama sur ce point. (3) 268:11 « לֹא יָצָא » ne dit pas où reprendre (la Michna Beroura 268 ס״ק טז-יז le précise) ; les options n'en disent rien. (4) Le SA HaRav sur Sefaria (deux éditions Kehot) compte 18 séifim au siman 268 et 17 au siman 188 ; les numéros cités suivent cette numérotation. (5) Les options ne changent que du texte à l'intérieur d'éléments existants ou suppriment des blocs entiers. Mais verify-oh-source.py fige les empreintes CSS et les style= : il faut relancer le rendu pour s'assurer que la suppression d'un sa-block ne fait pas sortir la page de la forme admise. (6) Les cartes du catalogue sont écrites à la main (aucun script du dépôt ne produit div.siman-desc) : leur correction est manuelle.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-268-b"></a>

### Q9 — 268-B

**Niveau 4 : hidoush א et point ① — « il faut le dire avec un autre Juif (témoignage à 2) » et « si oubli, retrouver un autre Juif pour le réciter ensemble », attribués à l'Admour HaZaken**

_Où :_ `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 612-621 · `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 661 · `sources/shabbat/siman-268/niveau-4-daat-harav-he.html` l. 576, 580-583, 622 · `sources/shabbat/siman-268/niveau-4-daat-harav-en.html` l. 596, 600-604, 644

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 268:1**

> צָרִיךְ לוֹמַר פָּרָשַׁת "וַיְכֻלּוּ" בִּתְפִלַּת עַרְבִית. וְכָל הַמִּתְפַּלֵּל וְאוֹמֵר "וַיְכֻלּוּ" — מַעֲלֶה עָלָיו הַכָּתוּב כְּאִלּוּ נַעֲשָׂה שׁוּתָּף לְהַקָּדוֹשׁ בָּרוּךְ הוּא בְּמַעֲשֵׂה בְרֵאשִׁית, שֶׁנֶּאֱמַר "וַיְכֻלּוּ", אַל תִּקְרֵי "וַיְכֻלּוּ", אֶלָּא "וַיְכַלּוּ", כְּלוֹמַר הַקָּדוֹשׁ בָּרוּךְ הוּא וָהוּא:

Il faut dire la parasha « Vaykhoulou » dans la tefilla d'Arvit. Quiconque prie et dit « Vaykhoulou », le verset le lui compte comme s'il était devenu associé du Saint béni soit-Il dans l'œuvre de la Création, ainsi qu'il est dit « Vaykhoulou » : ne lis pas « vaykhoulou » mais « vaykhalou » (« et ils achevèrent »), c'est-à-dire le Saint béni soit-Il et lui.

_(et 6 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Réécrire le hidoush א et le point ① sur 268:1, 268:12 et le Kountress Aharon ב, titre h3 compris (recommandée)** — On garde les blocs et les ids h3, puisque le sous-titre y renvoie. On corrige le texte visible du h3 (témoignage sur l'œuvre de la Création, et non sur le « repos divin »), on retire le « binôme », on rend la conduite de l'oubli selon 268:12 avec son degré (« il est bon »), et on corrige les renvois. La ligne sa-he reçoit un titre entièrement hébreu, et le titre français ou anglais reste dans la ligne sa-fr ou sa-en. L'étiquette « חידוש א » est provisoirement gardée : son maintien est soumis au Rav (voir option C).
- **B — Comme A, en ajoutant la nuance de la Michna Beroura, nommément attribuée** — À retenir si le Rav tient à garder l'idée du « deux » sur la page, mais sous sa vraie source et sans en faire un remède à l'oubli. La phrase s'ajoute à la fin du paragraphe FR l.620, HE l.582 et EN l.603 de l'option A. Les guillemets ne sont pas imbriqués.
- **C — En plus de A : retirer l'étiquette « חידוש » de ce bloc et récrire, sur ce siman seulement, le chapeau de la section 2** — Si A est retenue (et A de 268-A, qui supprime le hidoush ב), la section 2 ne contient plus qu'un bloc. Son contenu se trouve déjà chez le Mehaber 268:7, le Magen Avraham et la Michna Beroura ; le Kountress Aharon suit le Mateh Moché et le Magen Avraham. Garder « חידוש » et « Originalités qui distinguent l'Admour HaZaken » affirmerait une originalité que la source ne montre pas. On garde le section-num et les h2 avec leurs ids (gabarit commun aux pages N4), et on change l'étiquette du bloc et le paragraphe du chapeau.

**Recommandation.** Option A, et C si le Rav retient aussi l'option A de 268-A. A supprime une conduite que la page attribue au Rav alors qu'elle contredit 268:12, reproduit sur la même page. Elle corrige le titre h3, qui faisait du témoignage un témoignage sur le « repos divin », et elle rend chaque conduite avec le degré que lui donne la source (צריך / נוהגין / טוב). B s'ajoute seulement si le Rav veut mentionner la Michna Beroura. Changer le chapeau de la section 2 sur les 119 pages N4 qui le partagent est une autre décision, hors de ce dossier.

**Question.** (1) Validez-vous que la « conséquence pratique » du hidoush א et le point ① disent, selon 268:12, « si on l'a oublié à la synagogue, il est bon de le dire au Kiddouch, debout », à la place de « retrouver un autre Juif pour le réciter ensemble », et que le titre devienne « Vaykhulu, témoignage sur l'œuvre de la Création » — oui ou non ? (2) Faut-il garder l'étiquette « חידוש א » et le chapeau « Originalités qui distinguent l'Admour HaZaken » sur ce siman, ou les remplacer selon l'option C ? (3) Faut-il ajouter la nuance de la Michna Beroura (option B) — oui ou non ?

**Non vérifié.** Je n'ai pas vérifié si une source Habad ultérieure (Siddour de l'Admour HaZaken, Sefer HaMinhagim, Ketsot HaChoulhan, Chaarei Halakha OuMinhag) recommande de dire Vaykhulu à deux en cas d'oubli. Si le Rav en connaît une, elle doit être citée avec sa référence exacte, ou ne pas être dite. Le texte du Taz cité est un extrait : son début (« וסיים הטור ואומרים אותו ביחיד ») porte sur Sefaria « ביחיד », là où le Magen Avraham cite le Tour avec « ביחד » ; je n'ai pas tranché cette leçon, et aucune option ne la cite. Les nouvelles chaînes en sa-he (« חידוש א — ויכולו כעדות … ») sont hors des blocs seif-details que contrôle verify-oh-source.py, mais il faut relancer le rendu.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-268-c"></a>

### Q10 — 268-C

**Niveau 4 : point ② « Confusion semaine/Shabbat dans Amida : reprendre dès qu'on s'aperçoit » — conduite inversée par rapport à SA HaRav 268:2, et renvoi רס״ח:4-8 inexact**

_Où :_ `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 662 · `sources/shabbat/siman-268/niveau-4-daat-harav-he.html` l. 623 · `sources/shabbat/siman-268/niveau-4-daat-harav-en.html` l. 645

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 268:2 (début)**

> אִם טָעָה וְהִתְחִיל בְּרָכוֹת אֶמְצָעִיּוֹת שֶׁל חֹל, אִם נִזְכַּר בְּאֶמְצַע בְּרָכָה — צָרִיךְ לִגְמוֹר כָּל אוֹתָהּ בְּרָכָה, וְאַחַר כָּךְ מַתְחִיל בְּרָכָה אֶמְצָעִית שֶׁל שַׁבָּת, בֵּין שֶׁנִּזְכַּר בִּבְרָכָה רִאשׁוֹנָה שֶׁל אֶמְצָעִיּוֹת שֶׁל חֹל שֶׁהִיא אַתָּה "חוֹנֵן", וּבֵין שֶׁנִּזְכַּר בִּשְׁאָר בְּרָכוֹת אֶמְצָעִיּוֹת שֶׁל חֹל, וְכֵן בְּיוֹם טוֹב …

S'il s'est trompé et a commencé les berakhot intermédiaires de semaine, s'il s'en souvient au milieu d'une berakha, il doit achever toute cette berakha, puis il commence la berakha intermédiaire de Chabbat ; qu'il s'en souvienne à la première des berakhot intermédiaires de semaine, « Ata honen », ou dans les autres berakhot intermédiaires de semaine ; et de même à Yom Tov…

_(et 4 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Réécrire ② sur 268:2-4 et 7-8, avec la réserve de 268:3 (recommandée)** — Le point ② donne la règle de base, l'exception de Moussaf avec sa réserve verbatim, un renvoi au séif 4 pour le cas du mot « אַתָּה », et la règle de la tefilla de semaine dite en entier. Le renvoi devient רס״ח:2-4, 7-8.
- **B — Réécriture courte de ②** — Si le Rav préfère une liste למעשה brève : seule la règle de base est donnée, avec un renvoi aux séifim pour les cas particuliers.

**Recommandation.** Option A. Elle rétablit la règle de 268:2, que le point ② actuel inverse, et garde la réserve de 268:3 sans l'interpréter. B si le Rav veut une ligne brève.

**Question.** Validez-vous que le point ② dise, selon 268:2-4 et 7-8, qu'à Arvit, Cha'harit et Min'ha on achève la berakha de semaine commencée avant de passer à celle de Chabbat, et qu'on ne s'interrompt qu'à Moussaf (avec la mention, verbatim, de « וְיֵשׁ חוֹלְקִין … וּסְפֵק בְּרָכוֹת לְהָקֵל »), à la place de « reprendre dès qu'on s'aperçoit » — oui ou non ? Si oui : version longue (A) ou courte (B) ?

**Non vérifié.** (1) Je ne traduis pas « וּסְפֵק בְּרָכוֹת לְהָקֵל » par une conduite. La Michna Beroura (268 ס״ק ה) lit dans le cas de Moussaf une interruption tranchée « משום ספק ברכה לבטלה », ce qui va dans le sens de l'interruption, mais c'est au Rav de dire s'il veut l'écrire. (2) Le séif 9 (doute) n'est pas repris dans ②. Le Rav peut l'ajouter ; voir autres_constats sur l'écart entre 268:9 et la Michna Beroura ס״ק ט. (3) Je n'ai pas consulté le Siddour de l'Admour HaZaken sur ces cas.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-268-d"></a>

### Q11 — 268-D

**Niveau 4 : point ④ « Magen Avot à arvit : ne pas oublier dans la synagogue » — formule sans contenu dans la source, et renvoi רס״ח:14-18 qui ne traite pas de Magen Avot**

_Où :_ `sources/shabbat/siman-268/niveau-4-daat-harav.html` l. 664 · `sources/shabbat/siman-268/niveau-4-daat-harav-he.html` l. 625 · `sources/shabbat/siman-268/niveau-4-daat-harav-en.html` l. 647

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 268:13 (début et fin)**

> תִּקְּנוּ חֲכָמִים שֶׁאַחַר תְּפִלַּת לַחַשׁ יֹאמַר הַשְּׁלִיחַ צִבּוּר בְּרָכָה אַחַת מֵעֵין שֶׁבַע. … לְפִיכָךְ, לֹא תִקְּנוּהָ אֶלָּא עַל הַשְּׁלִיחַ צִבּוּר בִּלְבָד. וְאִם יִרְצוּ הַצִּבּוּר לְאָמְרָהּ עִם הַשְּׁלִיחַ צִבּוּר — צָרִיךְ שֶׁיֹּאמְרוּ בְּלֹא פְתִיחָה וּבְלֹא חֲתִימָה, כְּדֵי שֶׁלֹּא יְבָרְכוּ לְבַטָּלָה. וְכֵן הַמִּנְהָג בִּמְדִינוֹת אֵלּוּ לוֹמַר עִם הַשְּׁלִיחַ צִבּוּר "מָגֵן אָבוֹת" עַד "זֵכֶר לְמַעֲשֵׂה בְרֵאשִׁית". וְאַף הַמִּתְפַּלֵּל בְּיָחִיד שֶׁרוֹצֶה לוֹמַר כֵּן — הָרְשׁוּת בְּיָדוֹ:

Les Sages ont institué qu'après la tefilla à voix basse, le chalia'h tsibour dise une berakha unique « me'ein cheva »… C'est pourquoi ils ne l'ont instituée que pour le seul chalia'h tsibour. Si la communauté veut la dire avec le chalia'h tsibour, elle doit la dire sans ouverture ni conclusion, pour ne pas bénir en vain. Et tel est l'usage dans ces pays : dire avec le chalia'h tsibour de « Maguen avot » jusqu'à « zékher lema'assé véréchit ». Et même celui qui prie seul et veut le dire en a la permission.

_(et 2 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Réécrire ④ sur 268:13, 15 et 17 (recommandée)** — Le point ④ dit ce qu'est la berakha me'ein cheva, ce que fait la communauté, où on la dit, et l'avertissement de ne pas parler. Le renvoi devient רס״ח:13, 15, 17.
- **B — Supprimer ④** — Si le Rav juge que la liste למעשה n'a pas à traiter de me'ein cheva, on supprime la ligne dans les trois langues (FR l.664, HE l.625, EN l.647).

**Recommandation.** Option A. Elle remplace une formule sans fondement par ce que disent 268:13, 15 et 17, et corrige le renvoi.

**Question.** Validez-vous que le point ④ soit réécrit sur 268:13, 15 et 17 (me'ein cheva instituée pour le chalia'h tsibour, dite par la communauté de « מָגֵן אָבוֹת » à « זֵכֶר לְמַעֲשֵׂה בְרֵאשִׁית » sans ouverture ni conclusion, seulement dans un minyan fixe, sans parler pendant ce temps), à la place de « ne pas oublier dans la synagogue » — oui ou non ? Sinon : supprimer ④ (B) ?

**Non vérifié.** Le séif 15 contient d'autres précisions (minyan temporaire dans les foires, lieux où l'on a l'usage de la dire même dans un minyan occasionnel : « אֵין לִמְחוֹת בְּיָדָם ») qui ne sont pas reprises ; le Rav peut les ajouter. Je n'ai pas vérifié l'usage Habad actuel sur me'ein cheva au-delà du texte de 268:13.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

## Siman 278

Dossier complet (texte source, analyse, propagation, textes FR/HE/EN de chaque option, autres constats) : [`niv4-chabbat-urgent/siman-278.md`](niv4-chabbat-urgent/siman-278.md).

<a id="point-278-a"></a>

### Q12 — 278-a

**Niveau 4 : le « חידוש א » (« Le malade lève les שבותים ») et le למעשה qui en découle contredisent le SA HaRav 278:1 et 278:3 reproduits sur la même page ; la phrase « Application directe : שבות במקום חולה » se propage jusqu'au catalogue /oh/**

_Où :_ `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 453-454 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 455 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 456 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 457 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 489 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 490 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 355 · `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 447-449 · `sources/shabbat/siman-278/niveau-4-daat-harav-he.html` l. 447-451 · `sources/shabbat/siman-278/niveau-4-daat-harav-he.html` l. 483-484 · `sources/shabbat/siman-278/niveau-4-daat-harav-he.html` l. 353 · `sources/shabbat/siman-278/niveau-4-daat-harav-en.html` l. 451-455 · `sources/shabbat/siman-278/niveau-4-daat-harav-en.html` l. 487-488 · `sources/shabbat/siman-278/niveau-4-daat-harav-en.html` l. 353

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 278:1**

> מֻתָּר לְכַבּוֹת אֶת הַנֵּר בִּשְׁבִיל הַחוֹלֶה שֶׁיִּישַׁן, אִם הוּא חוֹלֶה שֶׁיֵּשׁ בּוֹ חֲשַׁשׁ סַכָּנָה אִם לֹא יִישַׁן

Il est permis d'éteindre la lampe pour le malade, afin qu'il dorme, s'il est un malade en qui il y a crainte de danger s'il ne dort pas.

_(et 14 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A1 — Réécrire le « חידוש א » sur la seule différence de rédaction vérifiable (« חֲשַׁשׁ סַכָּנָה אִם לֹא יִישַׁן ») et sur l'interdit, sous les deux avis ; corriger hero, למעשה, index, meta, JSON, catalogue** — Garde l'étiquette « חידוש » : à ne retenir que si le Rav juge que la rédaction de 278:1 en est un (voir analyse, point a). Remplace le contenu du <div class="sa-block"> du hidoush (FR l.453-457, HE l.446-451, EN l.451-455), en gardant les attributs style= existants. Change l'id du h3 et l'ancre du hero (FR l.355, EN l.353). Remplace les items du למעשה ; l'item ③ est facultatif (voir la question). Remplace la phrase « Application directe… » partout (index, meta, JSON-LD, JSON, catalogue). Régénère index.md. Aucune formule courte ne cite « מדברי סופרים » hors de son cadre, aucune ne renvoie au « Rav » sur l'index (« l'Admour HaZaken »), aucune ne renvoie le lecteur à « ton Rav » pour juger d'un danger (SA HaRav 328:2 : « וְהַשּׁוֹאֵל — הֲרֵי זֶה שׁוֹפֵךְ דָּמִים »).
- **A2 — Retirer le « חידוש א » (aucun hidoush vérifié), avec le même למעשה, le même hero et le même index que A1** — Sur le modèle de l'encadré « Aucune référence vérifiée à ce jour » des דברי הרבי de la même page, dont le style= est repris à l'identique (déjà admis par verify-oh-source.py ; border-right en HE). Le <div class="sa-block"> du hidoush (FR l.452-458, HE l.446-452, EN l.450-456) devient un avertissement. Le paragraphe d'introduction « Originalités qui distinguent… Chaque hidoush suit la structure… » (FR l.447-449 et équivalents HE/EN) est supprimé : il annoncerait un hidoush que la page n'a plus. Le hero garde la phrase de remplacement, mais sans lien intra-ref. Le למעשה ①②(③), l'index, les meta, le JSON-LD, le JSON, index.md et le catalogue sont traités comme en A1.
- **A3 — Niveau 1, « Concept 3 » (l.399, FR/HE/EN) : remplacer les deux phrases qui suivent « catégorie distincte. »** — Complément indépendant de A1/A2. Le niveau 1 expose le Mehaber : la correction s'appuie sur la Michna Beroura et renvoie au siman 328 pour le non-Juif, au lieu d'effacer ce qu'en dit la page. Les deux phrases « Pour ce malade, on permet seulement les mélakhot dérabaniques ou par non-juif. La mélakha déorayta (comme מכבה) n'est levée qu'en cas de sakana. » sont REMPLACÉES, et non complétées : le dossier initial ne disait pas où placer son texte. Correction du dossier initial : la raison tirée du Biour Halakha (« לא רצו להקל בה ») est abandonnée, parce qu'elle y justifie la rigueur quand il existe une autre solution. La raison donnée est celle de la MB ס״ק ג elle-même. Les gershayim ASCII de Sefaria sont rendus par ״, selon la convention du site ; les consonnes sont inchangées.

**Recommandation.** Option A2, appliquée d'un seul tenant dans les trois langues. A2 retire l'affirmation fausse sans en poser une autre que la source n'établit pas : le texte du Rav est déjà reproduit en entier à la section 1, et la seule particularité possible, la rédaction « אִם לֹא יִישַׁן », est une question d'interprétation que le Biour Halakha discute. Si le Rav juge que cette rédaction est un hidoush, prendre A1. Dans les deux cas, corriger le hero, le למעשה ①②, l'index (hero, meta, JSON-LD), data/simanim/siman-278.json, puis régénérer index.md (scripts/generate-siman-markdown.py --siman 278). Corriger aussi le catalogue sources/shabbat/index*.html l.1292. Ajouter A3 au niveau 1. Ensuite relancer : verify-oh-source.py 278 --rendu (sans --cache) ; verifier-citations.py --path sources/shabbat/siman-278 --langues fr,he,en ; verifier-langues.py ; verifier-liens-langue.py ; verifier-balises.py ; contrôle des ancres intra-ref renommées ; npm run build (corpus du chat).

**Question.** Pour le « חידוש א » du niveau 4 de 278, dans les trois langues, avec ses reprises (hero, למעשה ① ②, index, meta, JSON-LD, data/simanim/siman-278.json, index.md, catalogue /oh/), quelle option choisissez-vous ? (A1) Le réécrire sur la rédaction « אִם הוּא חוֹלֶה שֶׁיֵּשׁ בּוֹ חֲשַׁשׁ סַכָּנָה אִם לֹא יִישַׁן » et l'interdit pour le malade sans danger, en gardant l'étiquette « חידוש ». (A2) Le retirer (« Aucun hidoush vérifié à ce jour »). (Z) Ne rien changer. Et séparément : (i) ajouter au למעשה l'item ③, non-Juif pour le malade alité, SA HaRav 328:19 — oui ou non ? (ii) remplacer au niveau 1 les deux phrases du « Concept 3 » selon A3 — oui ou non ?

**Non vérifié.** (1) Le Biour Halakha (ד״ה בשביל שיישן) rapporte d'un auteur la lecture « la permission dépend du danger né du manque de sommeil » et la rejette pour le Choulhan Aroukh. Il permet en revanche, même pour un malade sans danger, si le médecin dit que le manque de sommeil peut mener au danger. La rédaction du Rav en 278:1 correspond à la lecture rapportée ; en 278:3, il reprend la formule simple. J'ignore si l'auteur visé est l'Admour HaZaken, et aucune option ne le dit. (2) La MB ס״ק א (d'après le Rambam) et le Biour Halakha (« לדינא נראה להחמיר לכו״ע היכא דיש לו עצה אחרת ») demandent d'abord de cacher la lumière ou de sortir le malade. La MB ס״ק ב demande de passer par le non-Juif s'il est là sans retard (renvoi au Rama 328:12). Le SA HaRav 278 n'en parle pas, et A1 et A2 n'en disent rien. Pour le Rav, c'est une nuance d'un poseq ultérieur, non la shitah du Rav. (3) Le SA HaRav 328:19 permet par un Israélite, « עַל יְדֵי שִׁנּוּי », « אֲפִלּוּ מְלָאכָה גְמוּרָה » pour le malade alité. 278 n'en dit rien pour l'extinction, et le Biour Halakha traite l'extinction à part des « שאר שבותים » : aucune option ne tranche. (4) Le « fondement » initial décrivait mal la réserve du bas du למעשה : la page dit en général « Pour toute question concrète : consulter ton Rav ». Elle ne demande pas de faire juger par le Rav l'état d'un malade. Les options ne renvoient pas au Rav pour un danger (SA HaRav 328:2 : « וְהַשּׁוֹאֵל — הֲרֵי זֶה שׁוֹפֵךְ דָּמִים » ; « אוֹ עַל פִּי מֻמְחֶה »). Le bandeau général, commun aux pages, n'est pas traité ici. (5) Dans le niveau 4, verifier-citations.py rapporte par défaut toute citation au SA HaRav 278 (ref_du_siman). La citation du Mehaber « מותר לכבות הנר בשביל שישן החולה שיש בו סכנה » (« Position classique » de A1) pourrait donc être confrontée au SA HaRav 278:3, qui porte « שֶׁיִּישַׁן ». À vérifier après application. Si elle sort VARIANTE, la passer en <em>résumé</em>. (6) Recopier les citations depuis le JSON de Sefaria, ou depuis le .sa-he de la page, et non depuis ce dossier : l'ordre des diacritiques peut différer avant normalisation NFC.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-278-b"></a>

### Q13 — 278-b

**Niveau 3 (et explications du niveau 1) : phrase attribuée entre guillemets à la Michna Beroura ס״ק א, « פשוט הוא דלא רק מותר אלא חובה לכבות », qui n'existe pas ; explications des ס״ק א et ב qui ne correspondent pas à leur texte**

_Où :_ `sources/shabbat/siman-278/niveau-3-synthese.html` l. 380 · `sources/shabbat/siman-278/niveau-3-synthese.html` l. 414 · `sources/shabbat/siman-278/niveau-3-synthese-he.html` l. 380, 414 · `sources/shabbat/siman-278/niveau-3-synthese-en.html` l. 380, 414 · `sources/shabbat/siman-278/niveau-1-base.html (+ -he, -en)` l. 430 · `sources/shabbat/siman-278/niveau-1-base.html (+ -he, -en)` l. 434 · `sources/shabbat/siman-278/niveau-1-base.html (+ -he, -en)` l. 477

_Source principale :_ **Mishnah Berurah 278:1 (ס״ק א), texte intégral**

> (א) מותר וכו' - עיין ברמב"ם בפירוש המשנה שכתב דדוקא בשא"א להוציא החולה למקום אחר או להסתיר האור ממנו ור"ל ע"י כפיית כלי על גביו וכדלעיל בסוף הסימן עי"ש או ע"י הוצאה לחדר אחר דאל"ה בודאי יותר טוב לטלטל מוקצה מלעבור על איסור כביה ועיין בבה"ל:

« Il est permis, etc. » — voir le Rambam dans son commentaire de la Michna, qui écrit que c'est seulement lorsqu'il est impossible de sortir le malade vers un autre endroit ou de lui cacher la lumière ; c'est-à-dire [précision de la MB] en retournant un récipient dessus, comme plus haut à la fin du siman, voir là, ou en la sortant dans une autre pièce ; car sinon, il vaut certainement mieux déplacer un objet muktsé que transgresser l'interdit d'éteindre ; et voir le Biour Halakha.

_(et 4 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **B1 — Rattacher l'obligation à sa vraie source (או״ח שכ״ח:ב) et rendre aux ס״ק א et ב leur contenu** — Au N3, l.380 et l.414 (3 langues), la phrase inventée et son attribution sont remplacées par le Mehaber 328:2, cité mot pour mot (Maginei Eretz). Au N1, les explications l.430 et l.434 décrivent ce que disent réellement les ס״ק א et ב, en distinguant ce que la MB rapporte du Rambam de ce qu'elle précise elle-même. La question l.477 porte sur le vrai contenu du ס״ק א.
- **B2 — Retrait sans remplacement au N3 ; N1 corrigé comme en B1** — Au N3 l.380, supprimer la phrase « Le Mishna Beroura (s.k.1) tranche : « … » — il est évident que ce n'est pas seulement permis mais obligatoire d'éteindre. » et garder le reste. Au N3 l.413-415, supprimer l'encadré « Piège 4 » entier. Au N1, l.430, l.434 et l.477 sont corrigés comme en B1 : c'est indispensable dans les deux options, puisque ces explications ne correspondent pas au texte qu'elles suivent.

**Recommandation.** Option B1. Elle garde l'enseignement de la page (« permis » ne veut pas dire « facultatif ») en le rattachant à un texte qui le dit vraiment, et elle répare les deux explications du niveau 1, qui commentent aujourd'hui un texte disparu. Relancer ensuite verifier-citations.py --path sources/shabbat/siman-278 --langues fr,he,en, pour s'assurer que « (או״ח שכ״ח:ב) » est bien confronté au Mehaber 328:2.

**Question.** Pour la citation « פשוט הוא דלא רק מותר אלא חובה לכבות », attribuée à la Michna Beroura ס״ק א (N3 l.380 et l.414, trois langues), quelle option choisissez-vous ? (B1) La remplacer par le Choulhan Aroukh או״ח שכ״ח:ב (« מצוה לחלל עליו את השבת… »). (B2) La retirer sans la remplacer. (Z) Ne rien changer. Validez-vous aussi, dans les deux cas, la réécriture des explications des ס״ק א et ב et de la question l.477 au niveau 1, d'après leur texte réel — oui ou non ?

**Non vérifié.** (1) La recherche plein-texte de Sefaria peut manquer une source hors de son corpus. Ce qui est sûr, c'est que la phrase n'est pas dans la Michna Beroura 278 que la page cite. (2) Sefaria sert la MB avec des guillemets ASCII dans les abréviations (בשא"א, ע"י…), et le niveau 1 les recopie tels quels l.428 et l.432 ; la conversion en ״ n'est pas traitée ici. (3) Dans le ס״ק א, « הוצאה לחדר אחר » peut se lire comme la sortie de la lampe, ce que suggère « לטלטל מוקצה », ou comme celle du malade. La traduction proposée suit la première lecture (« la sortir »), et le Rav peut préférer l'autre. Que « דאל״ה בודאי יותר טוב… » appartienne au Rambam ou à la MB est ambigu : B1 l'attribue à la MB, ce qui ne prête au Rambam rien qu'il n'ait écrit.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-278-c"></a>

### Q14 — 278-c

**Niveau 2 (et tableau du niveau 3) : « אמר רב יהודה: מכבין את הנר מפני חולה כדי שיישן » (שבת ל׳ ע״א) — citation inexistante, sous une fausse adresse et un faux locuteur ; Rashi sous un dibbour inexistant**

_Où :_ `sources/shabbat/siman-278/niveau-2-lamdan.html (+ -he, -en, corps hébreu)` l. 360 · `sources/shabbat/siman-278/niveau-2-lamdan.html (+ -he, -en ; ligne identique dans les 3 fichiers)` l. 362 · `sources/shabbat/siman-278/niveau-2-lamdan.html et -en.html (identiques) ; -he.html (un lien de plus)` l. 365 · `sources/shabbat/siman-278/niveau-2-lamdan.html (+ -he, -en)` l. 339, 358 · `sources/shabbat/siman-278/niveau-2-lamdan.html (+ -he, -en)` l. 387 · `sources/shabbat/siman-278/niveau-3-synthese.html / -he / -en` l. 435

_Source principale :_ **Michna, Shabbat 29b (Mishnah Shabbat 2:5)**

> הַמְכַבֶּה אֶת הַנֵּר מִפְּנֵי שֶׁהוּא מִתְיָרֵא מִפְּנֵי גּוֹיִם וּמִפְּנֵי לִיסְטִים, מִפְּנֵי רוּחַ רָעָה, מִפְּנֵי הַחוֹלֶה שֶׁיִּישַׁן — פָּטוּר

Celui qui éteint la lampe parce qu'il a peur des gentils, des brigands, d'un mauvais esprit, ou pour que le malade dorme : il est exempt.

_(et 7 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **C1 — Remplacer la fausse citation par la Michna (29b) et la Guemara (30a), mot pour mot ; corriger le Rashi et la référence à Yoma** — Le corps du niveau 2 est en hébreu dans les trois fichiers. Les lignes 339, 358, 360, 362 et 387 reçoivent le même texte dans les trois. La ligne 365 diffère : le fichier -he garde son lien de plus vers la section 4. Le nouvel id du h2 (l.358) et son lien du sommaire (l.339) changent ensemble ; aucune autre page ne pointe vers l'ancien id. Le dibbour de Rashi est corrigé (l.387). La ligne du tableau N3 (l.435) est corrigée dans chaque langue.
- **C2 — Retirer la citation, garder la seule référence** — Supprimer le blockquote l.362, réécrire l.360 et l.365 sans aucun texte entre guillemets, et garder les liens existants (dont celui du fichier -he). Les lignes l.339, 358 et 387 et le tableau N3 l.435 sont corrigés comme en C1. L'option est moins riche pour un niveau lamdan, mais n'expose à aucune recopie.

**Recommandation.** Option C1. Au niveau lamdan, la Michna et la Guemara sont le cœur de la sougya. La Guemara de 30a donne mot pour mot la distinction entre malade en danger et malade sans danger (« פָּטוּר אֲבָל אָסוּר »), qui fonde aussi le point 278-a. Le lien vers la section 4 (fichier -he) est conservé tel quel ; mais cette section repose sur une citation du Rambam non vérifiée (voir autres_constats), et elle devra être revue.

**Question.** Pour la citation « אמר רב יהודה: מכבין את הנר מפני חולה כדי שיישן » (שבת ל׳ ע״א), au niveau 2 (trois fichiers) et dans le tableau du niveau 3, quelle option choisissez-vous ? (C1) La remplacer par la Michna de שבת כ״ט ע״ב et la Guemara de ל׳ ע״א citées mot pour mot, et renvoyer Rashi aux dibburim « ש״מ ר׳ יהודה היא » et « ור׳ שמעון היא ». (C2) Retirer la citation et garder les seuls renvois. (Z) Ne rien changer.

**Non vérifié.** (1) L'origine de la phrase est une hypothèse : mélange avec Yoma 85b, avec le « רבי יהודה » de 30a, ou avec la question à Rabbi Tan'houm. (2) La Michna est citée dans la vocalisation de la William Davidson Edition ; la Torat Emet de la Mishnah Shabbat 2:5 porte une autre leçon (« וְאִם בִּשְׁבִיל הַחוֹלֶה שֶׁיִּישַׁן »). (3) verifier-citations.py --path sources/shabbat/siman-278 n'examinait que 5 citations, sans confronter celle-ci : il est vert sur ce défaut. (4) La suite de l.387 (« מבאר שכיבוי … (אלא רק כדי שהחולה ישן) ») applique au malade ce que Rashi dit en ד״ה ור׳ שמעון היא ; elle n'est pas modifiée.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-278-d"></a>

### Q15 — 278-d

**Niveau 4, traduction du séif 1 (FR l.386, EN l.384) : parenthèse ajoutée et confuse en FR, « חֲשַׁשׁ » non rendu en EN — le seuil du heter est mal traduit**

_Où :_ `sources/shabbat/siman-278/niveau-4-daat-harav.html` l. 386 · `sources/shabbat/siman-278/niveau-4-daat-harav-en.html` l. 384

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 278:1**

> מֻתָּר לְכַבּוֹת אֶת הַנֵּר בִּשְׁבִיל הַחוֹלֶה שֶׁיִּישַׁן, אִם הוּא חוֹלֶה שֶׁיֵּשׁ בּוֹ חֲשַׁשׁ סַכָּנָה אִם לֹא יִישַׁן

Il est permis d'éteindre la lampe pour le malade, afin qu'il dorme, s'il est un malade en qui il y a crainte de danger s'il ne dort pas.

**Options**

- **D1 — Corriger la seule proposition fautive dans chaque traduction** — Remplace, dans le <p class="sa-fr"> (FR l.386) et le <p class="sa-en"> (EN l.384), le segment cité, sans toucher au .sa-he. La page hébraïque n'a pas de traduction.
- **D2 — Ne rien changer** — La traduction reste en l'état ; le texte hébreu reproduit au-dessus fait foi.

**Recommandation.** Option D1, en même temps que le point 278-a, pour que la traduction et le hidoush (ou son retrait) disent le même seuil.

**Question.** Validez-vous la correction de la traduction du séif 1 au niveau 4 : « s'il s'agit d'un malade en qui il y a crainte de danger s'il ne dort pas » (FR), « if he is a sick person in whom there is a concern of danger if he does not sleep » (EN) — option D1, oui ou non ?

**Non vérifié.** Le passage par Chromium de verify-oh-source.py (--rendu) n'a pas été lancé par l'arbitre. Une modification du .sa-fr ou du .sa-en ne touche ni au .sa-he ni au CSS, mais le passage est à refaire avant publication, selon la règle du dépôt.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

## Siman 279

Dossier complet (texte source, analyse, propagation, textes FR/HE/EN de chaque option, autres constats) : [`niv4-chabbat-urgent/siman-279.md`](niv4-chabbat-urgent/siman-279.md).

<a id="point-279-a"></a>

### Q16 — 279-A

**Niveau 4 : « la bougie change de statut quand elle s'éteint naturellement » — généralisation fausse, dans les trois langues, contraire au séif 1 du Choul'han Aroukh HaRav**

_Où :_ `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 502-508 · `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 512-513 · `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 514 · `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 515 · `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 516 · `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 548 · `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 549 · `sources/shabbat/siman-279/niveau-4-daat-harav-he.html` l. 413-419 · `sources/shabbat/siman-279/niveau-4-daat-harav-he.html` l. 423-426 · `sources/shabbat/siman-279/niveau-4-daat-harav-he.html` l. 458-459 · `sources/shabbat/siman-279/niveau-4-daat-harav-en.html` l. 424-429 · `sources/shabbat/siman-279/niveau-4-daat-harav-en.html` l. 433-437 · `sources/shabbat/siman-279/niveau-4-daat-harav-en.html` l. 469-470

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 279:1 (début)**

> נֵר שֶׁהִדְלִיקוּ בּוֹ מִבְּעוֹד יוֹם וְדָלַק עַד לְאַחַר שֶׁחָשֵׁכָה אַף עַל פִּי שֶׁכָּבָה אַחַר כָּךְ אָסוּר לְטַלְטְלוֹ כָּל הַשַּׁבָּת כֻּלָּהּ אֲפִלּוּ לְצֹרֶךְ גּוּפוֹ אוֹ לְצֹרֶךְ מְקוֹמוֹ

Une lampe qu'on a allumée de jour et qui a brûlé jusqu'après la tombée de la nuit, même si elle s'est éteinte ensuite, il est interdit de la déplacer durant tout le Chabbat, même pour le besoin de son corps ou de sa place.

_(et 13 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Rétablir la règle des séifim 1-2 et ses exceptions ouvertes (3, 5, 6), retirer l'étiquette « hidoush »** — Dans les trois langues, au niveau 4 : remplacer la phrase-cadre de la rubrique (FR:507-508, HE:418-419, EN:428-429), le titre du bloc (p.sa-he, et p.sa-fr / p.sa-en là où ils existent), son h3, ses deux paragraphes, et les points ① et ② du למעשה. Les identifiants d'ancre restent tels quels (les liens du hero y pointent). Le hero se corrige dans la même édition, partout où il figure : N4 FR:355, HE:278 (avec « בט׳ »), EN:278 ; data/simanim/siman-279.json:6-7 ; index.html (régénéré par generate-siman.js --force, diff relu, ou à la main), index-he.html:148, index-en.html:147 à la main ; cartes du catalogue sources/shabbat/index*.html:1306 à la main ; index.md (generate-siman-markdown.py) ; image OG (generate-og-image.js, SVG et PNG). Nouvelle formule du hero : FR « muktsé selon ce qu'elle était à bein ha-shemashot, distinction du chandelier » (« déplacement du plateau » est retiré, aucun séif ne le porte) ; HE « מוקצה לפי מה שהיה בבין השמשות, חילוק המנורה » (N4) et « מוקצה לפי מה שהיה בבין השמשות, דין המנורה והפמוט » (index ; « וטלטול הטס » retiré) ; EN « muktzeh according to what it was at bein hashemashos, distinction of the candelabra » (« moving the tray » retiré). Les citations hébraïques vocalisées sont à recopier du JSON brut de Sefaria ou de final_sefaria.json (dagesh avant sheva, comme le reste de la page), non d'une forme normalisée.
- **B — Option A, plus une remarque comparative sur le séif 6, sans étiquette « hidoush »** — Tout le texte de l'option A, et un paragraphe de plus, après « Conséquence pratique », qui expose l'écart textuel réel entre le Mehaber 279:5 et l'Admour HaZaken 279:6 en disant d'où vient la lecture « même délibérément ». L'étiquette « hidoush » n'est PAS gardée : le Magen Avraham 279, 11 (qui renvoie au Beit Yossef) et la Michna Beroura 279 ס״ק יח écrivent déjà que l'allumage délibéré est permis. L'ancienne option B du dossier, qui présentait cet écart comme l'originalité du Rav et disait que le Mehaber « ne nomme que l'allumage par inadvertance », est retirée : elle était fausse sur les deux points.
- **C — Retrait sobre** — Supprimer le bloc du hidoush (FR:511-517, HE:422-427, EN:432-438) et la phrase-cadre, remplacés par une ligne d'attente. Retirer le lien intra-ref du hero (FR:355, EN:278), qui pointerait vers une ancre disparue, en gardant le mot nu ; corriger dans la même édition la formule du hero partout où elle figure, comme dans l'option A. Réécrire ① et ② au plus court.

**Recommandation.** Option A. Elle redresse l'erreur avec les seuls mots de la source, garde la condition du séif 1 (la bougie qui brûlait encore à la tombée de la nuit), donne les exceptions des séifim 3, 5 et 6 sous une forme OUVERTE, avec la restriction du séif 6 (pour le besoin de son corps ou de sa place), et retire l'étiquette « hidoush », qu'aucune source n'autorise ici : même l'écart réel du séif 6 avec le Mehaber est déjà chez le Magen Avraham et la Michna Beroura. L'option B n'ajoute qu'une remarque d'étude ; l'option C est la plus sûre si le Rav préfère ne rien exposer. Appliquer dans les trois langues à la fois, avec le hero partout où il figure (N4, data/simanim/siman-279.json, index FR/HE/EN, cartes du catalogue, index.md, image OG SVG et PNG) et la phrase-cadre de la rubrique, puis lancer npm run build et redéployer (le corpus du chat porte la formule du hero). Relancer ensuite verifier-citations.py --langues fr,he,en --path sources/shabbat/siman-279, verify-oh-source.py 279 --rendu (le bloc garde les classes sa-block / sa-he / sa-fr déjà admises), verifier-langues.py, verifier-balises.py et veilleur.py sur le siman.

**Question.** Pour le niveau 4 du siman 279, en FR, HE et EN, répondez oui ou non à chaque point : (1) remplacez-vous le bloc « hidoush א » et les points ① et ② du למעשה par le texte de l'option A (règle 279:1-2 ; exceptions, non limitatives, aux séifim 3, 5 et 6) — et sinon, préférez-vous l'option B (A plus la remarque comparative) ou l'option C (retrait sobre) ? (2) Retirez-vous, pour ce siman, la phrase-cadre « Originalités qui distinguent l'Admour HaZaken… », remplacée par « Aucun hidoush n'est présenté pour ce siman à ce jour… » ? (3) Validez-vous la nouvelle formule du hero (« muktsé selon ce qu'elle était à bein ha-shemashot », et le retrait de « déplacement du plateau / טלטול הקנה / טלטול הטס / moving the tray ») partout où elle figure ? (4) Faut-il mentionner sur la page la Michna Beroura 279 ס״ק א (crainte des non-juifs liée à la lampe ; crainte d'être frappé ou d'une perte d'argent d'après le Pri Megadim) et ס״ק יד (la lampe destinée à brûler toute la journée, par exemple de yahrzeit, que le Pri Megadim hésite à faire déplacer même par un non-juif) ?

**Non vérifié.** (1) Décisionnaires ultérieurs, rapportés sans être mis dans les options. Michna Beroura 279 ס״ק א, sur le Mehaber : s'il y a une crainte des non-juifs à cause de la lampe elle-même (« ע"י הנר »), il est permis de la déplacer après extinction, d'après le Shiltei Guiborim et le Tosefet Shabbat, contre le Magen Avraham (« ודלא כמ"א ») ; et d'après le Pri Megadim, s'il craint d'être frappé ou une autre perte d'argent, c'est permis selon tous. Le Magen Avraham 279, 1, rapporte le Shiltei Guiborim puis lit chez Rachi une restriction au cas de danger. Michna Beroura 279 ס״ק יד : pour la lampe destinée à brûler toute la journée (« כמו יא"צ וכדומה »), le Pri Megadim hésite à la faire déplacer même par un non-juif quand c'est pour qu'elle ne soit pas volée, et le permet pour le besoin de son corps ou de sa place. Rien de cela n'est le texte du Rav. (2) Michna Beroura 279 ס״ק ז, sur la glose du Rama : l'istnis ne peut sortir la lampe que de l'endroit où il est assis, non la déplacer d'un endroit quelconque à un autre. Le texte du Rav écrit « לְהוֹצִיאוֹ מֵעָלָיו לְמָקוֹם אַחֵר » ; l'option A suit le Rav (« d'auprès de lui ») sans trancher la portée. (3) « במדינות אלו » : l'option A rapporte l'usage tel que l'écrit l'Admour HaZaken, sans dire si c'est l'usage Habad d'aujourd'hui ; aucune source n'a été trouvée pour le dire. La rubrique s'intitule pourtant « La conduite Habad pratique » / « הלכה למעשה — מנהג חב״ד ». (4) L'origine de l'ajout, au séif 6, du non-juif qui allume pour des enfants ou un malade sans danger n'a pas été recherchée (le Magen Avraham 279, 10 renvoie au siman 265 séif 3). (5) Les portes officielles n'ont pas été lancées (dépôt en lecture seule) ; la conformité des 9 blocs .sa-he vient d'un contrôle manuel des consonnes contre l'édition Kehot vocalisée. L'édition non vocalisée « Kehot Publication Society » n'a pas été confrontée aux citations proposées, ce qui n'est pas bloquant : les pages recopient l'édition vocalisée. (6) Le hidoush, le למעשה et le hero ont l'allure d'un gabarit généré (« outil pratique : … », références par paquets de trois séifim) : voir le point 279-B.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

<a id="point-279-b"></a>

### Q17 — 279-B

**Niveau 4, point ③ du למעשה : « le bougeoir suit le statut de la bougie », référencé 279:7-9 — référence fausse, énoncé incomplet**

_Où :_ `sources/shabbat/siman-279/niveau-4-daat-harav.html` l. 550 · `sources/shabbat/siman-279/niveau-4-daat-harav-he.html` l. 460 · `sources/shabbat/siman-279/niveau-4-daat-harav-en.html` l. 471

_Source principale :_ **Shulchan Arukh HaRav, Orach Chayim 279:1 (fin)**

> וַאֲפִלּוּ מְנוֹרָה גְדוֹלָה שֶׁדָּלַק עָלֶיהָ נֵר אֶחָד מִבְּעוֹד יוֹם נַעֲשֵׂית כֻּלָּהּ בָּסִיס לוֹ וְנֶאֶסְרָה בְּטִלְטוּל לְכָל הַשַּׁבָּת אֲפִלּוּ לְאַחַר שֶׁכָּבָה הַנֵּר (אֲפִלּוּ אִם אֵינָהּ שֶׁל פְּרָקִים)

Et même un grand chandelier sur lequel une seule lampe a brûlé de jour devient tout entier sa base, et il est interdit au déplacement pour tout le Chabbat, même après que la lampe s'est éteinte (même s'il n'est pas démontable).

_(et 3 autre(s) passage(s) cité(s) dans le dossier complet)_

**Options**

- **A — Réécrire ③ avec les séifim qui portent la règle** — Remplacer le point ③ dans les trois langues, avec la référence juste (279:1, 4, 8-9).
- **B — Supprimer le point ③** — Retirer la ligne ③ dans les trois langues ; la liste du למעשה garde ① et ② corrigés (point 279-A).

**Recommandation.** Option A, dans la même édition que 279-A, pour que la liste du למעשה ne garde aucune référence fausse.

**Question.** Remplacez-vous, en FR, HE et EN, le point ③ du למעשה du niveau 4 du siman 279 (« le bougeoir suit le statut de la bougie », 279:7-9) par le texte de l'option A (279:1, 4, 8-9) — oui ou non ? Sur un non, faut-il supprimer ce point (option B) ?

**Non vérifié.** Le séif 9 ne dit pas expressément si le chandelier à pièces lâches sur lequel une bougie a brûlé ce Chabbat reste soumis à 279:1 ; l'option A ne présente 279:9 que comme une limite de l'interdit du séif 8 (« à moins que »), sans rien affirmer de plus.

**Décision du Rav :** _à remplir_ — option : ______ · remarque : ______

---

## Après la décision

1. Appliquer les options retenues dans les trois langues, avec leur propagation (index, `data/simanim/siman-N.json`, `index.md`, `llms.txt`, catalogue), d'après `niv4-chabbat-urgent/dossiers.json`.
2. Rejouer sans `--cache` : `verify-oh-source.py N --rendu`, `verifier-citations.py --langues fr,he,en --path sources/shabbat/siman-N`, `verifier-etiquettes.py N`, `verifier-troncatures.py`, `verifier-langues.py`, `verifier-alignement.py`, `verifier-balises.py`, `audit-simanim.py`, puis `npm run build`.
3. Fusionner `origin/main`, `verifier-integrite.py` à 0, et ne publier qu'avec l'accord explicite.
