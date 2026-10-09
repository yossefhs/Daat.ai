#!/usr/bin/env python3
"""Confronte le texte source (Mehaber + Rama) des simanim de Hilkhot Chabbat aux
sources Sefaria — verbatim, consonnes identiques — à l'édition hébraïque PAR
DÉFAUT, Maginei Eretz, épinglée par son NOM, et à elle seule pour ce qui est des
OMISSIONS ; une seconde édition, Torat Emet 363, peut seulement EXPLIQUER une
leçon (voir R1-R4, puis TOUR 3, plus bas).

Usage : python3 scripts/verify-chabbat-source.py 292 301 308
        python3 scripts/verify-chabbat-source.py --tous          # les 124
        python3 scripts/verify-chabbat-source.py --tous --bref   # une ligne par siman
        python3 scripts/verify-chabbat-source.py 252 --rafraichir   # ignore le cache

Codes de sortie : 0 aucune divergence de texte · 1 une divergence au moins
(au-delà du ktiv haser/malé, contre les éditions de référence ; une OMISSION
d'un passage de l'édition par défaut en est une, même quand Torat Emet l'omet
aussi ; un yod/vav ÉCHANGÉ, déplacé, ou ajouté en tête ou en fin de mot aussi —
garde ktiv) · 2 usage · 3 rien n'a été confronté, ou un siman n'a pas été atteint
(Sefaria injoignable, erreur servie en HTTP 200, ref servi faux ; Maginei Eretz
absente, déclarée dans une autre langue, servie deux fois, vide — le Mehaber n'a
pas de lacune connue en Hilkhot Chabbat —, trouée, ou TRONQUÉE : autre nombre de
séifs que Torat Emet 363 ou que son propre chapeau ; Torat Emet 363 absente ; ou
aucune page sous ROOT pour un siman demandé) — la porte ne conclut pas, elle ne
sort pas verte, et rien n'est mis en cache. Une divergence trouvée ailleurs
l'emporte : 1.

C'est l'équivalent, pour Hilkhot Chabbat, de `verify-yd-source.py` (Yoré Déa) et
de `verify-oh-source.py` (Orah Haïm quotidien). Il manquait : `CLAUDE.md` le
notait — « Hilkhot Shabbat n'en a pas encore » — et c'est le plus gros
compartiment du site, 124 simanim.

Ce qu'aucune des trois portes historiques ne voit et que celle-ci voit :
`verifier-citations.py` juge les CITATIONS (ce que la page met entre guillemets),
pas la RECOPIE du texte de base ; `verifier-alignement.py` juge la correspondance
entre l'étiquette de séif annoncée et le contenu du bloc, mais ne confronte pas
ce contenu à Sefaria ; `audit-simanim.py` est structurel. Une page peut donc
passer les trois en développant les abréviations du Choul'han Aroukh, en laissant
tomber une parenthèse de source, en fondant deux séifim en un bloc ou en n'en
publiant que six sur dix.

Deux invariants, pour chaque siman N :

  1. **Le texte.** La CONCATÉNATION des `<blockquote class="text-source">` de
     `niveau-1-base` reproduit exactement la suite des séifim que Sefaria donne
     pour `Shulchan_Arukh, Orach_Chayim N` — consonnes hébraïques seules,
     nikoud, ponctuation, balises et espaces ignorés. Le titre-chapeau de Sefaria
     (« דין … ובו נ״א סעיפים ») est facultatif : il est retiré du texte de
     référence si la page ne le reprend pas.

  2. **La découpe.** Le NOMBRE de blocs source est comparé au nombre de séifim.
     C'est la règle absolue posée après le siman 243 : la découpe entre séifim
     fait partie de ce qui doit être exactement comme dans le Choul'han Aroukh.
     Une page qui fragmente un séif en trois, ou qui n'en publie que six sur dix,
     reproduit peut-être un texte juste mais ne donne pas la source telle qu'elle
     est. L'écart est signalé comme AVERTISSEMENT et non comme erreur, parce que
     le texte peut être intégralement exact malgré une découpe différente — les
     deux faits sont distincts et se lisent séparément.

Plus la parité FR/HE/EN du texte source : une même source doit être donnée au
lecteur français, hébreu et anglais sous la même forme.

Une étiquette que le bloc se donne lui-même — « <strong>סעיף ח:</strong> » en
hébreu, « <strong>Seif ח:</strong> » en anglais — n'est pas du texte du Choul'han
Aroukh et est retirée avant comparaison ; sans quoi toute page qui numérote ses
blocs serait déclarée divergente, et toute page qui les numérote en hébreu le
serait sans que l'anglaise le soit.

PLUSIEURS ÉDITIONS (octobre 2026). Sefaria sert le Choul'han Aroukh Orah Haïm en
plusieurs éditions hébraïques (`api/v3/texts/…?version=hebrew|all`), et elles ne
disent pas toujours les mêmes mots :
  · « Maginei Eretz: Shulchan Aruch Orach Chaim, Lemberg, 1893 » — non vocalisée,
    seule à porter le chapeau du siman ; priorité Sefaria 2.0, c'est l'édition
    PAR DÉFAUT d'`api/texts`. La porte la reconnaissait à sa priorité ; depuis le
    tour 3 elle l'ÉPINGLE PAR SON NOM (voir TOUR 3), et DIT si Sefaria en sert une
    autre par défaut ;
  · « Torat Emet 363 » — vocalisée, développe certaines abréviations, a son ktiv ;
  · « Torat Emet Freeware Shulchan Aruch » — servie sur 105 des 124 simanim ;
  · au siman 264, « שלחן ערוך מטור ארוח חיים », un séif.
Le premier tour de la réparation (8 octobre) retenait, pour chaque séif, l'édition
quelconque dont la page était la copie. Son arbitre l'a dit TROP INDULGENT, témoins
construits à l'appui : Freeware est DÉSALIGNÉE par endroits (son 344:1 est le texte
du 343:1 — une page publiant le mauvais séif était certifiée IDENTIQUE, code 0) et
LACUNAIRE (252:2 omet « מלאכתו בשבת אם היה עושה », saut du même au même ; 316:7
« ועקרבים » ; 320:18 « להסירו ») — une page qui recopiait ces lacunes sortait
IDENTIQUE, code 0, là où l'ancienne porte sortait en 1. D'où la règle, commune aux
trois portes de source :

  R1. Éditions de RÉFÉRENCE : l'édition par défaut et la Torat Emet NUMÉROTÉE
      (« Torat Emet 363 » pour Orah Haïm et Chabbat), et elles seules. Freeware,
      Wikisource et toute autre édition servie sont IGNORÉES — la porte le dit dans
      sa sortie. Coût mesuré : aucun verdict de l'état actuel n'en dépendait.
  R2. Torat Emet n'est admise pour un séif que si elle est ALIGNÉE sur le séif de
      même numéro de l'édition par défaut : ressemblance ≥ SEUIL_ALIGNEMENT (0,70),
      ratio de `difflib.SequenceMatcher` sur les squelettes, chapeau retiré.
      Mesure du 8 octobre 2026 sur les 124 simanim : les 1 053 séifs de Torat
      Emet 363 vont de 0,864 à 1 contre leur séif de Maginei Eretz ; un séif
      contre un séif VOISIN (i±1, i±2, 3 500 paires) ne dépasse jamais 0,556 ;
      Freeware 344:1 contre Maginei Eretz 344:1 : 0,144. Le seuil est dans le vide
      entre les deux populations. (La ressemblance par 5-grammes, celle qui désigne
      l'édition la plus proche d'un séif divergent, ne séparait pas : 0,30 pour
      le 345:8 de Torat Emet, pourtant aligné.)
  R3. UNE AUTRE ÉDITION EXPLIQUE UNE LEÇON, JAMAIS UNE OMISSION. Un mot changé, un
      ktiv, une abréviation développée ou contractée, un ajout que porte Torat
      Emet : excusés. Mais un passage que porte l'édition PAR DÉFAUT et qui manque
      à la page — suite de mots, glose du Rama, parenthèse de source — reste
      SIGNALÉ, même si Torat Emet l'omet aussi, avec la mention « absent aussi de
      Torat Emet 363 ». Le chapeau n'est jamais un écart.
      L'omission se lit par un alignement MOT À MOT (difflib sur les mots : un
      mot porte son squelette, ou, s'il porte un guerech ou des guerchayim, ses
      lettres et ses marques — sans quoi « סי׳ » (siman) et « ס״י » (séif 10), ou
      « י״א » et « א׳ », se confondaient). Une SUPPRESSION y est une omission. Un
      REMPLACEMENT est une leçon, sauf pour les mots qu'un alignement fin à coût
      (`_remplacement`) y laisse sans contrepartie quand AUCUN mot n'y est changé :
      au 244:1, « לעשות בו מלאכ׳ בשבת » / « לעשות מלאכה בשבת » est un remplacement
      de deux mots par un, et « בו » y manque ; mais « פרק במה טומנין » / « פרק
      כירה » (257:8) ou « פ׳ ה׳ » / « פכ״ה » (308:1) changent un mot, et l'on ne
      sait plus lequel de ses voisins il remplace : leçons. Un mot sans
      contrepartie n'est retenu que si aucun mot non apparié de l'autre texte, à
      proximité, n'en est la forme DÉPLACÉE (243:1, « עושה בו מלאכה » / « עושה
      מלאכה בו »), DÉVELOPPÉE (« ר״ה » / « רשות הרבים »), CONTRACTÉE, SCINDÉE
      (« וכלבו » / « וכל בו ») ou à UNE LETTRE près (« הן » / « הם ») — un mot
      apparié ne couvre rien d'autre (308:13 : le premier « אצבעות » de Torat
      Emet ne couvre pas le second « אצבעו׳ », qu'elle n'a pas).
      Mesure du 8 octobre 2026, Maginei Eretz → Torat Emet 363, 1 053 séifs :
      25 suppressions mot à mot, dont 4 déplacements ou développements (243:1 ;
      243:2, « וכן עיקר » placé AVANT la parenthèse ; 307:19 ; 345:8) ; 87
      remplacements où Torat Emet a moins de mots (abréviations, pour presque
      tous), dont un seul cache une omission, le 244:1. Restent 22 vraies lacunes
      de Torat Emet 363 — 242:1 « את », 244:1 « בו », 246:5 « ישראל » et « בו »,
      253:1 « או » (Torat Emet écrit « וגבבא » : leçon, mais tenue pour omission
      par prudence), 256:1 « שעה », 257:3 « הגה » (la marque de la glose du
      Rama), 268:9 « ברכת », 275:5 « כאחד », 288:2 « לו », 301:38 « בה », 303:20
      « הם », 305:17 « כדי », 306:1 « בו », 306:3 « לו », 306:4 « עמו », 307:2
      « בשבת », 308:13 « אצבעו׳ », 330:5 « להכיר », 358:2 « וארבע רוחב », 360:3
      « אם », 363:26 « הכל ». Une page qui recopie Torat Emet à l'un de ces séifs
      sort en 1. Contrôle de rappel, Maginei Eretz → Freeware (édition ignorée,
      mesurée pour éprouver l'alignement) : les lacunes que l'arbitre a trouvées à
      la main sortent toutes — 252:2 « מלאכתו בשבת אם היה עושה », 262:1 la
      parenthèse de sources, 292:2 « זוהר תרומה ע׳ רע״ט », 316:7 « ועקרבים »,
      320:18 « להסירו ».
  R4. Chaque séif retenu hors de l'édition par défaut est imprimé avec son
      édition, et chaque édition servie mais ignorée est nommée.
Une page qui prend un séif dans une édition de référence et le suivant dans
l'autre passe (R3 sauf) ; une page qui mêle les deux À L'INTÉRIEUR d'un séif ne
passe pas — décision du premier tour, maintenue. Quand aucune ne convient,
l'écart est rapporté à l'édition LA PLUS PROCHE de ce séif — sans quoi un séif
recopié de Torat Emet avec un mot changé serait accusé, contre Maginei Eretz, de
toutes les abréviations que Torat Emet développe — ET les mots de l'édition par
défaut qui n'ont pas de contrepartie dans la page sont listés (R3), avec la mention
de Torat Emet. Le nombre de séifim est celui de l'édition par défaut.

Localiser un écart (page divergente) : le parcours suit les séifs ; un séif est
RETENU quand une édition s'y lit telle quelle ET que le séif suivant commence
juste après. Une édition plus courte peut n'être qu'un PRÉFIXE de la page : si le
début du séif suivant se lit plus loin et qu'une autre édition du séif est plus
proche du passage entier, l'excédent appartient à ce séif, qui diverge (au 262
du 14 septembre, Freeware, sans la parenthèse de sources, se lisait en tête d'une
page qui la porte). Un chapeau récrit est rapporté à part, non fondu dans le
séif א. Les séifs « NON RETROUVÉ » sont ceux dont le début ne se lit nulle part :
absents, fondus, ou altérés dès leurs premiers mots.

CE QUE LA MESURE A DONNÉ (8 octobre 2026, sur des instantanés FIGÉS des pages —
`git archive` de HEAD 7d4504d6 et de cbd2ad85 —, cache Sefaria du 8 octobre ;
trois versions de la porte : celle de HEAD, le premier tour, celle-ci) :
  · état actuel — 124 simanim, 1 053 séifim, 372 pages (366 IDENTIQUE, 6
    ÉQUIVALENT) : les trois langues recopient Maginei Eretz, et elle seule —
    3 159 séifs × page retenus dans l'édition par défaut, 0 hors d'elle, 0
    omission. Verdicts identiques siman par siman avec les trois versions : 0
    divergence, 2 avertissements de découpe (242, 243). R1-R3 n'y changent rien.
  · état du 14 septembre (cbd2ad85), celui des « 44 » : 44 simanim divergents et
    19 en découpe ou parité, identiques siman par siman avec les trois versions.
    Au séif (page française) : le premier tour comptait 31 séifs, dans 19
    simanim, fidèles seulement à une autre édition que Maginei Eretz — sa
    docstring disait 32 dans 20, chiffre périmé. Avec R1-R3, ce sont les MÊMES
    31 séifs dans les mêmes 19 simanim : tous sont fidèles à Torat Emet 363 (12
    l'étaient aussi à Freeware, AUCUN à Freeware seule) et aucun ne perd un
    passage de Maginei Eretz — leçons excusées, R3 n'en retient aucun. Séifs
    divergents : 112 → 110, parce que 254:ח et 272:ט, dont le début ne se lisait
    que dans Freeware, passent en NON RETROUVÉ (toujours signalés). Dans les
    séifs divergents, R3 nomme 35 passages de Maginei Eretz absents de la page
    (27 séifs, 17 simanim : parenthèses de sources, « תרגום בערתי הקדש פליתי »
    au 275:א, la clause du 271:יא…) ; Torat Emet 363 les porte tous — aucune de
    ces pages ne recopiait une lacune de Torat Emet.
  · Témoins (instantané de HEAD dont UN bloc est retouché, trois langues ; code
    de sortie porte de HEAD / premier tour / celle-ci) : 316:7 sans « ועקרבים »
    (= Freeware) 1/0/1 et 292:2 dont « (טור זוהר תרומה ע׳ רע״ט) » est réduite à
    « (טור) » (= Freeware) 1/0/1 — l'omission est nommée, « Torat Emet 363 le
    porte » ; 344:1 remplacé par le 344:1 de Freeware (= le 343:1) 1/0/1 —
    DIVERGENT, ressemblance 0,00 ; cache saboté où le 344:1 de Torat Emet 363 est
    son 343:1, page égale à ce texte : premier tour 0, celle-ci 1, « R2 : … NON
    ALIGNÉE (0,15) » ; 268:9 et 307:2
    recopiés de Torat Emet 363 (sans « ברכת », sans « בשבת ») 1/0/1, « absent
    aussi de Torat Emet 363 » ; 244:1 recopié de Torat Emet 363 (« בו » perdu
    dans un remplacement) 1/0/1 ; 291:2 recopié de Torat Emet 363, qui CONTRACTE
    « הגהות מרדכי » en « הגמ״ר » 1/0/0, séif imprimé « ב=Torat Emet 363 » (le
    piège de l'abréviation) ; 279:א, fidèle à Torat Emet 363 (« אף על פי » pour
    « אע״פ ») 1/0/0 ; 271:יא, qui omet « והיינו דוקא כשיש לו כוס אחר להבדלה… ולא
    יהא לו יין להבדלה » présent dans les deux éditions, 1/1/1 — la clause est
    listée parmi les mots de Maginei Eretz absents de la page ; 292:1 recopié de
    Torat Emet 363 (1 séif sur 2 hors de l'édition par défaut, égalité) : la
    ligne MÉLANGE du premier tour nommait, selon PYTHONHASHSEED, « א=Torat Emet
    363 » ou « ב=Maginei Eretz » ; celle-ci nomme toujours le séif pris HORS de
    l'édition par défaut.

TOUR 3 (9 octobre 2026) — quatre corrections demandées par l'arbitre du tour 2 et
par celui d'Orah Haïm, mesurées sur des instantanés FIGÉS (`git archive` de HEAD
56151b14 et de cbd2ad85, le 14 septembre), cache Sefaria du 8 octobre, inchangé.

  1. LA GARDE KTIV (`garde_ktiv`). Le squelette ôte tout yod et tout vav : « כוס »
     et « כיס », « מים » et « מום », « לו » et « לי », « הוא » et « היא » y avaient la
     même clé, et une page qui changeait l'un en l'autre sortait ÉQUIVALENT, code 0,
     sans un mot imprimé. RÈGLE : deux mots ne sont égaux au ktiv près que si l'un
     s'obtient de l'autre en AJOUTANT des yod/vav (sous-suite ; finales normalisées
     — sans objet ici, yod et vav n'ont pas de finale) ; un yod/vav ÉCHANGÉ au même
     endroit est un mot changé. La porte va un pas plus loin que la règle commune,
     mesure à l'appui : l'ajout doit être INTÉRIEUR au mot (ni l'initiale, le ו de
     conjonction — « ועקרבים » / « עקרבים », le témoin N7 de l'arbitre, sortait 0 —,
     ni la finale, « עליו » / « עלי »), et d'un seul côté (« יוכל » / « יכול » ajoute
     un vav de chaque côté : déplacé). Mise en œuvre : entre deux mêmes consonnes du
     squelette, les yod/vav de la page et de la source sont comparés (`_trou`), chaque
     lettre portant sa place dans son mot (`lettres`). Un séif qui ne passe que le
     squelette est un « MOT CHANGÉ » (code 1) et ses mots sont imprimés, avec, quand
     c'est le cas, « à cette place, « X » est le mot de Torat Emet 363 : deux éditions
     mêlées dans le séif ». La garde court aussi sur le chapeau, et sur les séifs
     retrouvés d'une page déjà divergente. Sous ÉQUIVALENT, la porte LISTE les mots
     égaux au ktiv près seulement, pour que le lecteur les contrôle.
     COÛT MESURÉ, sur les pages réelles :
       · HEAD — 124 simanim, 372 pages : verdicts inchangés, 366 IDENTIQUE · 6
         ÉQUIVALENT · code 0. Les 6 pages ÉQUIVALENT (278 et 280, trois langues)
         listent 4 mots, tous du ktiv véritable : « מתר » / « מותר », « שיישן » /
         « שישן », « לכתחילה » / « לכתחלה ». 0 faux positif.
       · 14 septembre — 44 simanim divergents, comme avant ; 5 séifs (× 3 langues)
         passent de « retenu » à MOT CHANGÉ, tous dans des pages déjà divergentes :
         248:ד « היא » pour « הוא », 271:יד « יש » pour « ויש », 279:א « להסתפק »
         pour « ולהסתפק » — les trois, le mot de Maginei Eretz dans le texte de Torat
         Emet, deux éditions mêlées — ; 264:י, le marqueur « [י] » collé au séif, que
         le squelette effaçait ; et 273:ו « שנתכוון » pour « שנתכוין », le SEUL faux
         positif : le même mot, une autre graphie de la consonne vav.
       · contrôle exhaustif croisé : dans chacun des 1 053 séifs, une page = Maginei
         Eretz dont tous les mots que Torat Emet 363 écrit autrement AU KTIV PRÈS
         prennent sa graphie (961 séifs concernés) : 0 DIVERGENCE. Puis chacun des 157
         mots que Torat Emet écrit avec un yod/vav ÉCHANGÉ, déplacé, ou en tête ou en
         fin de mot, substitué SEUL : 141 DIVERGENCE ; les 16 autres sont des séifs où
         la page devient Torat Emet 363 au ktiv près, retenus comme tels (leçon que
         Torat Emet porte, R3) et imprimés « hors de l'édition par défaut » (R4).
     LIMITE DÉCLARÉE : « ים » / « יום » est un AJOUT intérieur — la règle le tient pour
     du ktiv, la page sort ÉQUIVALENT et le mot est LISTÉ. On ne peut pas mieux sans
     dictionnaire : Torat Emet 363 elle-même écrit « חל », « רב », « רק », « לה »,
     « כף » là où Maginei Eretz écrit « חול », « רוב », « רוק », « ליה », « כוף » (30
     occurrences, sur 4 442 mots que les deux éditions écrivent au ktiv près
     autrement) ; une règle des mots de deux lettres accuserait du vrai ktiv. Entre
     les deux éditions, la garde classe encore 157 mots comme CHANGÉS (45 échanges,
     dont « היא » / « הוא », préfixés ou non, 26 fois ; 100 en tête ou en fin de
     mot ; 12 déplacés) : ce sont leurs leçons, et le contrôle croisé ci-dessus les
     a tous éprouvés.

  2. L'ÉDITION PAR DÉFAUT EST ÉPINGLÉE PAR SON NOM (`DEFAUT`, `valider`). Elle était
     déduite de la priorité Sefaria : Maginei Eretz servie tronquée, absente ou
     déclarée « en » faisait de Torat Emet 363 l'édition par défaut, et le résultat
     était mis en cache (sabotages S10, S12 de l'arbitre : code 1, cache écrit). Le
     siman est désormais NON ATTEINT (code 3) et RIEN n'est mis en cache si Maginei
     Eretz est absente (en hébreu), déclarée dans une autre langue, servie deux fois,
     vide, trouée (un séif vide avant son dernier), ou tronquée — un autre nombre de
     séifs que Torat Emet 363, ou que son propre chapeau n'en annonce (« ובו ז
     סעיפים », « ובו סעיף אחד » ; les 124 chapeaux en annoncent un, égal partout
     au nombre servi). Torat Emet 363 absente : NON ATTEINT aussi, la complétude ne
     pouvant plus être contrôlée. Le même `valider` juge un fichier de cache avant
     de le relire. Sabotages (urlopen remplacé, cache vide, siman 252) : quinze
     réponses ; les treize anomalies sortent en 3 sans écrire le cache — la porte
     du tour 2 en sortait sept en 0 ou en 1, cache écrit — ; la réponse fidèle et
     celle où Sefaria donne la priorité à Torat Emet sortent en 0 (la porte reste
     épinglée et le dit ; celle du tour 2 jugeait alors la page contre Torat Emet,
     code 1). Un fichier de cache tronqué n'est plus relu : réseau coupé,
     code 3 ; réseau rendu, le fichier est réécrit entier. Les 124 fichiers du
     8 octobre passent `valider` ; la FORME du cache reste 1 (son contenu n'a pas
     changé de forme, seul le critère de relecture s'est resserré).

  3. LE DÉVELOPPEMENT PARTIEL (`_partiel`, dans `_remplacement`). Une abréviation
     de plusieurs mots appariée au seul premier mot qu'elle développe (« ב״י » avec
     « בית ») faisait du mot suivant une « leçon », et le mot réellement omis sortait
     de la liste. Témoin N3 : 315:1 de Torat Emet dont « (בית יוסף וכל בו) » est
     réduite à « (בית יוסף) » — avant, DIVERGENT sans aucune ligne ; désormais « mots
     de Maginei Eretz sans contrepartie dans la page : « וכלבו) » — Torat Emet 363 le
     porte ». Effet sur le reste, mesuré : les 22 lacunes de Torat Emet 363 sont les
     mêmes, le contrôle exhaustif de l'arbitre (chacun des 1 009 séifs où Torat Emet
     diffère, substitué seul) rend les mêmes 21 séifs DIVERGENTS, et les 105 lignes
     « sans contrepartie » du 14 septembre sont identiques.

  4. 303:26 — Torat Emet 363 écrit « יכולה לח שערה » où Maginei Eretz a « לחלוק » :
     une COQUILLE, un mot tronqué. Pour la porte c'est une leçon (un mot qui diffère),
     EXCUSÉE : une page qui recopierait ce séif de Torat Emet sortirait IDENTIQUE,
     code 0, le séif imprimé « כו=Torat Emet 363 » (témoin vérifié). Les trois pages
     du dépôt portent « לחלוק ».

  Témoins du tour 3 (instantané de HEAD, UN bloc retouché dans les trois langues ;
  code porte du tour 2 / celle-ci) : 271:ו « כוס » → « כיס » 0/1 ; 252:ה « מים » →
  « מום » 0/1 ; 244:ו « הוא » → « היא » 0/1 ; 243:ג « לו » → « לי » 0/1 ; 316:ז
  « ועקרבים » → « עקרבים » 0/1 ; 245:א « עליו » → « עלי » 0/1 ; 301:לג « יוכל » →
  « יכול » 0/1 ; 244:ה « ויש » → « יש » 0/1 ; chapeau du 252 recopié avec « ובי »
  pour « ובו » 0/1 (recopié exact : 0/0) ; 331:ו « היא » → « הוא », le mot de Torat
  Emet à cette place 0/1, « deux éditions mêlées » ; 245:א « יום » → « ים » 0/0, LISTÉ ;
  243:א « מותר » → « מתר » 0/0, listé (contrôle). Les 8 témoins de l'arbitre du tour 1
  et les 18 de celui du tour 2, rejoués : mêmes codes, sauf N7 (316:ז sans
  « ועקרבים »), 0 → 1.

Pièges tenus :
  · Sefaria rend HTTP 200 et le LIVRE ENTIER sur un ref mal formé : le `ref` servi
    doit finir par le numéro demandé, sinon le siman est NON ATTEINT, avec sa
    raison, et jamais compté conforme ;
  · une réponse injoignable n'est pas un siman vide : NON ATTEINT ;
  · le cache (`scripts/.cache-sefaria/chabbat-editions/`) ne persiste JAMAIS un
    résultat que `valider` refuse (voir TOUR 3, 2), et porte sa FORME : un cache
    d'une autre forme, ou qui ne passe plus `valider`, est relu sur Sefaria. Il
    garde toutes les éditions servies, ignorées comprises, pour pouvoir les nommer ;
    sa FORME est restée 1, R1-R3 et le tour 3 changeant ce qu'on en lit et non ce
    qu'il contient — seul le critère de complétude s'est resserré, et les 124
    fichiers du 8 octobre le remplissent ;
  · ROOT se déduit de `__file__` : une copie lancée hors du dépôt ne trouve aucune
    page — par `--tous` comme par numéro — et sort en 3, elle ne passe pas pour
    verte ; elle ne va même pas sur Sefaria. La porte imprime ce qu'elle a confronté.
Ce que la porte ne fait pas : un remplacement où un mot est CHANGÉ et un autre
omis (« A B » pour « C ») est lu comme une leçon, entière ; dans un séif
DIVERGENT, la liste des mots absents a la même limite, et un séif remplacé en
entier (le 344:1 ci-dessus) sort DIVERGENT, ressemblance 0,00, sans liste ; un
chapeau RÉCRIT reste un écart (seule son ABSENCE est permise). Le « ו » de
conjonction perdu (« וכן » / « כן »), que le squelette ne voyait pas, est vu
depuis le tour 3 (garde ktiv) — SAUF quand Torat Emet 363 porte elle-même la
forme de la page à tout le séif : c'est alors sa leçon, excusée (R3) et imprimée.
Restent : « ים » pour « יום », ajout intérieur, LISTÉ et non bloquant ; une
coquille de Torat Emet (303:26 « לח ») excusée comme leçon ; et la garde ktiv
juge les yod/vav entre deux mêmes consonnes, elle ne juge pas le sens — une
autre graphie d'un même mot (« שנתכוון » / « שנתכוין ») y est un mot changé.
"""
import sys, re, json, unicodedata, os, html, difflib, itertools, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = os.path.join(ROOT, "sources", "shabbat")
LIVRE = "Shulchan_Arukh,_Orach_Chayim"
CACHE = os.path.join(ROOT, "scripts", ".cache-sefaria", "chabbat-editions")
FORME_CACHE = 1          # à incrémenter dès que la forme d'un fichier de cache change
HE_CONS = re.compile(r'[א-ת]')
CHAPEAU = re.compile(r'^\s*<b>.*?</b>\s*(<br\s*/?>)?', re.S)
ETIQ = re.compile(r'^\s*<strong>\s*(?:סעיפים|סעיף|Seifim|Seif)\b[^<]*</strong>\s*')
LANGS = [("FR", ""), ("HE", "-he"), ("EN", "-en")]
ANCRE = 24               # consonnes (squelette) qui reconnaissent le début d'un séif
NGRAMME = 5              # pour désigner l'édition la plus proche d'un séif divergent
SEUIL_ALIGNEMENT = 0.70  # R2 — mesuré : alignés ≥ 0,864, voisins ≤ 0,556 (voir docstring)
# R1 — les deux éditions de référence, ÉPINGLÉES PAR LEUR NOM (tour 3) : l'édition par
# défaut n'est plus déduite de la priorité Sefaria.
DEFAUT = "Maginei Eretz: Shulchan Aruch Orach Chaim, Lemberg, 1893"
ALTERNATIVE = "Torat Emet 363"
MARQUE = re.compile(r'[א-ת]["\'׳״]')    # guerech / guerchayim après une lettre
GERSHAYIM = re.compile(r'[א-ת]["״][א-ת]')   # abréviation de plusieurs mots (« ב״י »)
YV = "יו"
# Balises qui séparent deux mots ; toute autre balise (<strong>, <b>, <small>…) peut
# tomber au milieu d'un mot — « ו<strong>בדאג״ה</strong> » (état du 14 septembre).
BLOC = re.compile(r'<\s*/?\s*(?:br|p|div|li|ul|ol|tr|td|th|blockquote|h\d)\b[^>]*>', re.I)

COURT = {
    DEFAUT: "Maginei Eretz",
    ALTERNATIVE: "Torat Emet 363",
    "Torat Emet Freeware Shulchan Aruch": "Torat Emet Freeware",
}

RAISONS = {}


def court(titre):
    titre = (titre or "?").strip()
    return COURT.get(titre, titre[:28])


def lettre(i):
    """Le numéro de séif en lettres (1 → א, 15 → טו) : la page et le livre
    numérotent ainsi, et un lecteur qui cherche « séif 12 » le cherche sous יב."""
    val = [(400, "ת"), (300, "ש"), (200, "ר"), (100, "ק"), (90, "צ"), (80, "פ"),
           (70, "ע"), (60, "ס"), (50, "נ"), (40, "מ"), (30, "ל"), (20, "כ"), (10, "י"),
           (9, "ט"), (8, "ח"), (7, "ז"), (6, "ו"), (5, "ה"), (4, "ד"), (3, "ג"),
           (2, "ב"), (1, "א")]
    out = ""
    for v, l in val:
        while i >= v:
            out += l
            i -= v
    return out.replace("יה", "טו").replace("יו", "טז")


# --------------------------------------------------------------------- source

def _texte_plat(t):
    if isinstance(t, list):
        return [x if isinstance(x, str) else " ".join(_texte_plat(x)) for x in t]
    return [t] if isinstance(t, str) and t else []


def _titre(e):
    return (e.get("titre") or "").strip()


def defaut_de(eds):
    """L'édition PAR DÉFAUT, épinglée par son NOM : Maginei Eretz, et elle seule.
    None si elle n'est pas servie, en hébreu, une fois et une seule."""
    me = [e for e in eds or [] if _titre(e) == DEFAUT]
    return me[0] if len(me) == 1 else None


def _nombre_seifs(seifim):
    """(nombre de séifs jusqu'au dernier non vide, [séifs vides avant lui])."""
    der = max([i + 1 for i, s in enumerate(seifim) if consonants(s)] or [0])
    return der, [i + 1 for i in range(der) if not consonants(seifim[i])]


GEMATRIE = dict(zip("אבגדהוזחטיכלמנסעפצקרשתךםןףץ",
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                     200, 300, 400, 20, 40, 50, 80, 90]))


def annonce_chapeau(premier):
    """Le nombre de séifs que le chapeau de Maginei Eretz annonce — « ובו י״ז
    סעיפים », « ובו סעיף אחד » —, ou None s'il n'en annonce pas."""
    m = CHAPEAU.match(premier or "")
    if not m:
        return None
    t = re.sub(r'<[^>]+>', ' ', m.group(0))
    if re.search(r'ובו\s+סעיף\s+אחד', t):
        return 1
    m = re.search(r'ובו\s+([א-ת"\'׳״]+)\s+סעיפים', t)
    return sum(GEMATRIE.get(c, 0) for c in m.group(1)) if m else None


def valider(d):
    """None si la réponse est complète, sinon la raison du refus. L'édition par
    défaut doit être là, par son nom, en hébreu, non vide, sans séif vide avant son
    dernier séif, avec AUTANT de séifs que Torat Emet 363 et que son propre chapeau
    en annonce. Le même contrôle juge une réponse de Sefaria avant de la mettre en
    cache et un fichier de cache avant de le relire."""
    eds = d.get("editions") or []
    me = [e for e in eds if _titre(e) == DEFAUT]
    if not me:
        return f"édition par défaut {court(DEFAUT)} absente de la réponse (en hébreu)"
    if len(me) > 1:
        return f"{court(DEFAUT)} servie {len(me)} fois"
    nme, trous = _nombre_seifs(me[0]["seifim"])
    if not nme:
        return (f"{court(DEFAUT)} servie VIDE — le Mehaber n'a pas de lacune connue en "
                f"Hilkhot Chabbat")
    if trous:
        return f"{court(DEFAUT)} a des séifs VIDES avant son dernier : {trous[:8]}"
    te = [e for e in eds if _titre(e) == ALTERNATIVE]
    nte = _nombre_seifs(te[0]["seifim"])[0] if len(te) == 1 else 0
    if not nte:
        return (f"{ALTERNATIVE} absente ou vide : la complétude de {court(DEFAUT)} ne peut "
                f"pas être contrôlée")
    if nte != nme:
        return (f"{nme} séifs dans {court(DEFAUT)}, {nte} dans {ALTERNATIVE} — l'une des "
                f"deux est tronquée")
    ann = annonce_chapeau(me[0]["seifim"][0])
    if ann is not None and ann != nme:
        return f"le chapeau de {court(DEFAUT)} annonce {ann} séifs, elle en sert {nme}"
    return None


def fetch(n, rafraichir=False):
    """Les éditions hébraïques du siman N : {"ref", "editions": [{"titre",
    "priorite", "seifim": [html brut…]}]}, ou None — et alors RAISONS[n] dit
    pourquoi. Une réponse que `valider` refuse (édition par défaut absente,
    déclarée dans une autre langue, vide, tronquée) n'est jamais mise en cache, et
    le siman est NON ATTEINT."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"OH-{n}.json")
    if not rafraichir and os.path.exists(f):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if (d.get("forme") == FORME_CACHE and str(d.get("ref", "")).endswith(f" {n}")
                    and valider(d) is None):
                return d
        except Exception:
            pass
    u = (f"https://www.sefaria.org/api/v3/texts/{LIVRE}.{n}?version="
         + urllib.parse.quote("hebrew|all"))
    try:
        d = json.load(urllib.request.urlopen(u, timeout=60))
    except Exception as e:
        RAISONS[n] = f"api/v3/texts injoignable : {type(e).__name__} {e}"[:160]
        return None
    if not isinstance(d, dict):
        RAISONS[n] = f"réponse de Sefaria inattendue : {type(d).__name__}"
        return None
    ref = str(d.get("ref") or "").rstrip()
    if d.get("error"):
        RAISONS[n] = f"Sefaria répond une erreur (HTTP 200) : {d.get('error')!r}, ref {d.get('ref')!r}"[:200]
        return None
    if not ref.endswith(f" {n}"):
        RAISONS[n] = f"ref servi {d.get('ref')!r} ≠ siman {n} demandé"[:200]
        return None
    eds, ailleurs = [], []
    for v in d.get("versions") or []:
        langue = v.get("actualLanguage") or v.get("language")
        if langue != "he":
            if (v.get("versionTitle") or "").strip() in (DEFAUT, ALTERNATIVE):
                ailleurs.append(f"{court(v.get('versionTitle'))} déclarée « {langue} »")
            continue
        eds.append({"titre": v.get("versionTitle") or "?",
                    "priorite": v.get("priority") if isinstance(v.get("priority"), (int, float)) else 0,
                    "seifim": _texte_plat(v.get("text"))})
    eds.sort(key=lambda e: -e["priorite"])
    out = {"forme": FORME_CACHE, "ref": ref, "editions": eds}
    raison = valider(out)
    if raison:
        RAISONS[n] = (raison + (f" ({' · '.join(ailleurs)})" if ailleurs else ""))[:240]
        return None
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    return out


def references(eds):
    """R1 : (édition par défaut, [Torat Emet 363], [éditions servies, avec du
    texte, et IGNORÉES]) — les deux premières par leur NOM."""
    d = defaut_de(eds)
    alts = [e for e in eds if e is not d and _titre(e) == ALTERNATIVE][:1]
    ign = [e for e in eds if e is not d and e not in alts and consonants("".join(e["seifim"]))]
    return d, alts, ign


def defaut_sefaria(eds):
    """L'édition que Sefaria sert par défaut (priorité strictement la plus haute),
    pour le DIRE si ce n'est plus Maginei Eretz — la porte, elle, reste épinglée."""
    if not eds:
        return None
    top = max(e["priorite"] for e in eds)
    tops = [e for e in eds if e["priorite"] == top]
    return _titre(tops[0]) if len(tops) == 1 else None


# ------------------------------------------------------------- normalisation

def consonants(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = unicodedata.normalize('NFC', s)
    return "".join(HE_CONS.findall(s))


def squelette(s):
    """Le texte privé de ses matres lectionis — même normalisation que
    `verifier-alignement.py`.

    Sans elle, ce garde-fou serait illisible : le siman 271 écrit « כשיבוא »
    là où Sefaria écrit « כשיבא », le 252 « המתרים » pour « המותרים ». C'est du
    ktiv haser/malé, le faux positif dominant du dépôt, et il ne dit rien de la
    fidélité au Choul'han Aroukh. Deux verdicts sont donc rendus, et ils ne se
    valent pas : IDENTIQUE (consonnes strictement égales) et ÉQUIVALENT (égal
    aux matres lectionis près). Un écart qui SURVIT au squelette est un écart de
    texte — un mot remplacé, une abréviation développée, une parenthèse de source
    perdue, un séif tronqué. Celui qui ne lui survit pas passe encore la GARDE
    KTIV (tour 3, `garde_ktiv`) : le squelette égalait « כוס » et « כיס ».
    """
    return re.sub(r"[יו]", "", s)


def ressemblance(a, b):
    """R2 — ratio de difflib sur deux squelettes."""
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def mots_autour(brut, k, avant=6, apres=6):
    """Les mots du texte BRUT (balises ôtées, nikoud ôté) autour de la k-ième
    consonne du squelette : un extrait lisible, là où l'ancien rapport montrait
    une suite de consonnes sans yod ni vav."""
    t = re.sub(r'<[^>]+>', ' ', brut)
    t = unicodedata.normalize('NFKD', t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    mots = t.split()
    cum = 0
    for i, m in enumerate(mots):
        cum += len(squelette(consonants(m)))
        if cum > k:
            return " ".join(mots[max(0, i - avant):i]) + " ⟦" + mots[i] + "⟧ " + \
                " ".join(mots[i + 1:i + 1 + apres])
    return " ".join(mots[-avant:]) + " ⟦fin⟧"


# ------------------------------------------------------------- garde ktiv

def lettres(brut):
    """Les consonnes d'un texte avec leur place : ([(lettre, n° de mot, intérieure)],
    [mot lisible]). La suite des lettres est exactement `consonants(brut)` ; un mot
    est coupé aux espaces, au maqaf, à la ponctuation et aux balises de bloc —
    jamais au nikoud, au guerech, aux guerchayim, ni à une balise de texte
    (« ו<strong>בדאג״ה</strong> » est un mot). Une lettre est INTÉRIEURE quand elle
    n'est ni la première ni la dernière de son mot."""
    t = BLOC.sub(" ", brut)
    t = re.sub(r'<[^>]+>', '', t)
    t = unicodedata.normalize('NFC', t)
    L, lis_mots, cur, lis = [], [], [], []

    def fin_mot():
        if cur:
            w = len(lis_mots)
            L.extend((ch, w, 0 < k < len(cur) - 1) for k, ch in enumerate(cur))
            lis_mots.append("".join(lis))
        cur.clear()
        lis.clear()
    for ch in t:
        if HE_CONS.match(ch):
            cur.append(ch)
            lis.append(ch)
        elif unicodedata.combining(ch):
            continue
        elif ch in "\"'׳״":
            if cur:
                lis.append(ch)
        else:
            fin_mot()
    fin_mot()
    return L, lis_mots


def _trou(rp, rs):
    """Les yod/vav que la page (rp) et la source (rs) placent entre deux MÊMES
    consonnes du squelette. Rend None (mêmes lettres), ou (nature, lettres de rp
    en cause, lettres de rs en cause) : « ktiv » quand l'un s'obtient de l'autre en
    AJOUTANT des yod/vav à l'intérieur d'un mot (« כשיבא » / « כשיבוא », « ים » /
    « יום ») ; « en tête ou en fin de mot » quand l'ajout touche l'initiale ou la
    finale (« ועקרבים » / « עקרבים », « עליו » / « עלי ») ; « échange » sinon
    (« כוס » / « כיס », « מים » / « מום », « הוא » / « היא »). Un trou ne voit pas
    le mot entier : `garde_ktiv` juge ensuite le vav qui CHANGE DE PLACE
    (« יוכל » / « יכול », un ajout de chaque côté)."""
    cp, cs = "".join(x[0] for x in rp), "".join(x[0] for x in rs)
    if cp == cs:
        return None
    if len(cp) == len(cs):
        k = next(t for t in range(len(cp)) if cp[t] != cs[t])
        return "échange", [rp[k]], [rs[k]]
    page_longue = len(cp) > len(cs)
    lo, co = (rp, rs) if page_longue else (rs, rp)
    cc = "".join(x[0] for x in co)
    bord = None
    for comb in itertools.combinations(range(len(lo)), len(co)):
        if any(lo[k][0] != cc[t] for t, k in enumerate(comb)):
            continue
        extra = [lo[k] for k in range(len(lo)) if k not in comb]
        if all(x[2] for x in extra):
            return ("ktiv", extra, []) if page_longue else ("ktiv", [], extra)
        bord = bord or extra
    if bord:
        return ("en tête ou en fin de mot", bord, []) if page_longue else \
            ("en tête ou en fin de mot", [], bord)
    return "échange", rp[:1], rs[:1]


def _en_regard(g, L, b, Lo, bo, en_cause):
    """Le n° du mot de L qui répond, au trou g, au mot de l'autre texte (Lo) où se
    trouve la lettre en cause : celui de la consonne voisine que Lo rattache au même
    mot. None si la lettre est un mot à elle seule (« [י] »)."""
    w = en_cause[0][1]
    if bo[g] >= 0 and Lo[bo[g]][1] == w and b[g] >= 0:
        return L[b[g]][1]
    if bo[g + 1] < len(Lo) and Lo[bo[g + 1]][1] == w and b[g + 1] < len(L):
        return L[b[g + 1]][1]
    return None


def garde_ktiv(Lp, mots_p, Ls, mots_s):
    """LA GARDE KTIV (tour 3). Le squelette ôte TOUT yod et tout vav, si bien que
    « כוס » et « כיס », « מים » et « מום », « לו » et « לי », « הוא » et « היא » y ont
    la même clé : une page qui changeait l'un en l'autre sortait ÉQUIVALENT, code 0,
    sans qu'un mot fût imprimé. Deux mots ne sont égaux au ktiv près que si l'un
    s'obtient de l'autre en AJOUTANT des yod/vav à l'INTÉRIEUR du mot ; un yod/vav
    ÉCHANGÉ au même endroit, ou ajouté en tête (le ו de conjonction) ou en fin de
    mot (« עליו » / « עלי »), ou déplacé dans le mot (« יוכל » / « יכול »), est un
    mot changé.

    Lp et Ls (page, source, sorties de `lettres`) ont le même squelette. Rend
    (changés, ktiv) : deux listes de (mot de la page, mot de la source, nature,
    n° du mot de la page ou None)."""
    sp = [k for k, x in enumerate(Lp) if x[0] not in YV]
    ss = [k for k, x in enumerate(Ls) if x[0] not in YV]
    if [Lp[k][0] for k in sp] != [Ls[k][0] for k in ss]:
        return [("?", "?", "squelettes inégaux", None)], []
    bp, bs = [-1] + sp + [len(Lp)], [-1] + ss + [len(Ls)]
    changes, ktiv, sens = [], [], {}
    for g in range(len(sp) + 1):
        r = _trou(Lp[bp[g] + 1:bp[g + 1]], Ls[bs[g] + 1:bs[g + 1]])
        if r is None:
            continue
        nature, ep, es = r
        wp = ep[0][1] if ep else _en_regard(g, Lp, bp, Ls, bs, es)
        ws = es[0][1] if es else _en_regard(g, Ls, bs, Lp, bp, ep)
        mp = "∅" if wp is None else mots_p[wp]
        ms = "∅" if ws is None else mots_s[ws]
        (ktiv if nature == "ktiv" else changes).append((mp, ms, nature, wp))
        if nature == "ktiv":
            sens.setdefault((wp, ws), set()).add("page" if ep else "source")
    # Un mot n'est égal à l'autre au ktiv près que si l'AJOUT est d'un seul côté :
    # « יכול » / « יוכל » ajoute un vav de chaque côté, en deux trous — le vav a
    # CHANGÉ DE PLACE, ce n'est pas du ktiv (ni l'un ni l'autre n'est sous-suite).
    deplaces = {(mots_p[wp] if wp is not None else "∅", mots_s[ws] if ws is not None else "∅")
                for (wp, ws), v in sens.items() if len(v) > 1}
    changes += [x[:2] + ("déplacé dans le mot",) + x[3:] for x in ktiv if x[:2] in deplaces]
    ktiv = [x for x in ktiv if x[:2] not in deplaces]
    uniques = lambda l: list({x[:3]: x for x in l}.values())
    return uniques(changes), uniques(ktiv)


# ------------------------------------------------------------ R3 : omissions

def mots(brut):
    """Les mots d'un texte : [(clé, mot lisible, consonnes, début, fin)], début et
    fin en position du SQUELETTE de tout le texte (celle de `localiser`). La clé
    est le squelette — ou, pour un mot qui porte un guerech ou des guerchayim
    (abréviation, nombre), ses lettres et ses marques normalisées : « סי׳ »
    (siman) et « ס״י » (séif 10) ont les mêmes consonnes, et « י״א » le même
    squelette que « א׳ » ; les confondre déplaçait l'alignement et inventait des
    omissions. Un mot sans clé (« ו » seul) n'est pas aligné."""
    t = re.sub(r'<[^>]+>', ' ', brut)
    out, cum = [], 0
    for w in re.split(r'[\s־]+', t):
        c = consonants(w)
        if not c:
            continue
        lis = "".join(ch for ch in unicodedata.normalize('NFKD', html.unescape(w))
                      if not unicodedata.combining(ch))
        if MARQUE.search(lis):
            k = re.sub(r'[^א-ת"\']', '', lis.replace('״', '"').replace('׳', "'")
                       ).lstrip('"\'').replace("'", "׳").replace('"', "״")
        else:
            k = squelette(c)
        L = len(squelette(c))
        if k:
            out.append((k, lis, c, cum, cum + L))
        cum += L
    return out


def _sous_suite(a, b):
    it = iter(b)
    return all(ch in it for ch in a)


def _couvert(t, reserve, suite):
    """Un mot de l'édition par défaut, sans contrepartie à sa place, a-t-il sa
    forme ailleurs dans les mots NON appariés de l'autre texte, tout près ?"""
    k, w, c = t[0], t[1], t[2]
    if any(x[0] == k for x in reserve):
        return "déplacé"
    abr = bool(MARQUE.search(w))
    formes = _formes(c) if abr else [c]
    for s in range(len(reserve)):
        for n in range(1, min(4, len(reserve) - s) + 1):
            cc = "".join(x[2] for x in reserve[s:s + n])
            if abr and any(cc[0] == f[0] and n <= len(f) and _sous_suite(squelette(f), squelette(cc))
                           for f in formes):
                return "développé"
            if n >= 2 and squelette(cc) == squelette(c):
                return "scindé"
    sq_c = squelette(c)
    for x in reserve:
        if (MARQUE.search(x[1]) and x[2][0] == c[0]
                and _sous_suite(squelette(x[2]), squelette(c + "".join(y[2] for y in suite[:3])))):
            return "contracté"
        sq_x = squelette(x[2])
        if len(sq_c) >= 2 and len(sq_x) == len(sq_c) and sum(p != q for p, q in zip(sq_c, sq_x)) == 1:
            return "à une lettre près"
    return None


def _abrev(w):
    """Le mot porte-t-il un guerech ou des guerchayim collés à une lettre, d'un
    côté ou de l'autre (« ג״פ », mais aussi « "ג » d'une abréviation coupée) ?"""
    return bool(re.search(r'[א-ת]["\'׳״]|["\'׳״][א-ת]', w))


def _egal(a, b):
    """Un mot de l'édition par défaut et un mot de l'autre texte se répondent-ils
    1 pour 1 — même clé, même squelette, à une lettre près, ou l'un est
    l'abréviation de l'autre ?"""
    sa, sb = squelette(a[2]), squelette(b[2])
    if a[0] == b[0] or sa == sb:
        return True
    if len(sa) >= 2 and len(sa) == len(sb) and sum(p != q for p, q in zip(sa, sb)) == 1:
        return True
    for x, y in ((a, b), (b, a)):
        # x abrège y : y est un mot PLEIN (« פ׳ » ne répond pas à « פכ״ה »).
        if _abrev(x[1]) and not _abrev(y[1]):
            for f in _formes(x[2]):
                if f[0] == y[2][0] and _sous_suite(squelette(f), squelette(y[2])):
                    return True
    return False


def _formes(c):
    """Les consonnes d'un mot, et sans son « ו » de conjonction s'il en a un."""
    return [c] + ([c[1:]] if c[:1] == "ו" and len(c) > 1 else [])


def _developpe(x, ws):
    """Le mot x répond-il à la suite de mots ws — soudé (même squelette) ou
    abréviation qui la développe (« ר״ה » / « רשות הרבים ») ?"""
    cc = "".join(y[2] for y in ws)
    return (squelette(cc) == squelette(x[2]) or
            (_abrev(x[1]) and any(f[0] == g[0] and _sous_suite(squelette(f), squelette(g))
                                  for f in _formes(x[2]) for g in _formes(cc))))


def _partiel(a, b, suite_a, suite_b):
    """La paire 1 pour 1 (a, b) n'est-elle qu'un DÉVELOPPEMENT PARTIEL — une
    abréviation de plusieurs mots (guerchayim : « ב״י ») appariée au seul PREMIER
    des mots qu'elle développe (« בית »), quand elle se lit en entier sur les
    suivants (« בית יוסף ») ? `suite_a`, `suite_b` : les mots qui commencent à a, b."""
    for x, y, ws in ((a, b, suite_b), (b, a, suite_a)):
        if (GERSHAYIM.search(x[1]) and not _abrev(y[1]) and x[0] != y[0]
                and squelette(x[2]) != squelette(y[2])
                and any(_developpe(x, ws[:k]) for k in range(2, min(4, len(ws)) + 1))):
            return True
    return False


def _remplacement(A, B):
    """Un REMPLACEMENT de difflib (des mots de A à la place desquels B en a
    d'autres) peut cacher une omission : au 244:1, « לעשות בו מלאכ׳ בשבת » contre
    « לעשות מלאכה בשבת » — « בו מלאכ׳ » pour « מלאכה », un remplacement de deux
    mots par un, dont « בו » n'a aucune contrepartie. Petit alignement à coût : un
    mot de A apparié (même mot, ktiv, une lettre, abréviation développée ou
    contractée, mot scindé ou soudé) coûte 0, substitué par un mot quelconque de B
    (une leçon) 0,5, laissé sans contrepartie 1 ; un mot de B en plus ne coûte
    rien (un ajout est excusé). Rend (indices de A sans contrepartie, indices de
    B employés, nombre de mots SUBSTITUÉS). `omissions` ne retient les mots sans
    contrepartie que si aucun mot n'y est substitué : là où l'autre texte CHANGE
    un mot, on ne sait plus lequel de ses voisins il remplace — « פרק במה טומנין »
    / « פרק כירה » (257:8), « פ׳ ה׳ » / « פכ״ה » (308:1) sont des leçons.

    TOUR 3 — le DÉVELOPPEMENT PARTIEL. Une abréviation de plusieurs mots
    s'appariait à un seul des mots qu'elle développe : au 315:1, une page qui
    réduit « (ב״י וכלבו) » à « (בית יוסף) » était lue « ב״י » = « בית » (paire,
    0) et « וכלבו » → « יוסף » (leçon, 0,5) — et, une leçon dans le bloc, le mot
    réellement omis, « וכלבו », disparaissait de la liste (verdict 1 tout de même).
    Une telle paire, quand l'abréviation se lit en entier sur les mots suivants
    (`_partiel`), ne vaut plus qu'une leçon (0,5) ; et à coût égal, l'alignement qui
    substitue le MOINS de mots l'emporte : « ב״י » = « בית יוסף » (0) et « וכלבו »
    omis (1) battent deux leçons (0,5 + 0,5)."""
    m, n = len(A), len(B)
    INF = (float("inf"), 0)
    best = [[(INF, None)] * (n + 1) for _ in range(m + 1)]
    best[0][0] = ((0.0, 0), None)
    for i in range(m + 1):
        for j in range(n + 1):
            c, nl = best[i][j][0]
            if c == INF[0]:
                continue

            def pose(i2, j2, cout, quoi):
                v = (c + cout, nl + (quoi == "leçon"))
                if v < best[i2][j2][0]:
                    best[i2][j2] = (v, (i, j, quoi))
            if i < m:
                pose(i + 1, j, 1.0, "omis")
            if j < n:
                pose(i, j + 1, 0.0, "ajout")
            if i < m and j < n:
                if _egal(A[i], B[j]) and not _partiel(A[i], B[j], A[i:], B[j:]):
                    pose(i + 1, j + 1, 0.0, "paire")
                else:
                    pose(i + 1, j + 1, 0.5, "leçon")
                for k in range(2, 5):
                    if j + k <= n and _developpe(A[i], B[j:j + k]):    # un mot de A pour k de B
                        pose(i + 1, j + k, 0.0, "paire")
                    if i + k <= m and _developpe(B[j], A[i:i + k]):    # k mots de A pour un de B
                        pose(i + k, j + 1, 0.0, "paire")
    omis, pris, lecons, i, j = [], set(), 0, m, n
    while (i, j) != (0, 0):
        pi, pj, quoi = best[i][j][1]
        if quoi == "omis":
            omis.append(pi)
        elif quoi in ("paire", "leçon"):
            pris.update(range(pj, j))
            lecons += quoi == "leçon"
        i, j = pi, pj
    return sorted(omis), pris, lecons


def omissions(A, B):
    """Les mots de A (l'édition par défaut) qu'un alignement mot à mot laisse sans
    contrepartie dans B, et qu'aucun mot non apparié de B, à proximité, ne couvre.
    Rend une liste de suites d'indices de A. Une SUPPRESSION de difflib est une
    omission ; un REMPLACEMENT est une leçon, sauf pour les mots de A que son
    alignement fin (`_remplacement`) laisse sans contrepartie. Les mots de B qui
    peuvent encore couvrir une omission — un mot DÉPLACÉ, développé, scindé… —
    sont ceux des insertions et ceux qu'un remplacement n'a pas employés : un mot
    apparié a déjà sa contrepartie (308:13 : le premier « אצבעות » de Torat Emet
    ne couvre pas le second « אצבעו׳ » de Maginei Eretz, qu'elle n'a pas)."""
    if not A:
        return []
    sm = difflib.SequenceMatcher(None, [x[0] for x in A], [x[0] for x in B], autojunk=False)
    ops = sm.get_opcodes()
    libres, cand = set(), []
    for op, i1, i2, j1, j2 in ops:
        if op == "insert":
            libres.update(range(j1, j2))
        elif op == "delete":
            cand.append((list(range(i1, i2)), i1, i2, j1, j2))
        elif op == "replace":
            om, pris, lecons = _remplacement(A[i1:i2], B[j1:j2])
            libres.update(j1 + j for j in range(j2 - j1) if j not in pris)
            if om and not lecons:
                cand.append(([i1 + i for i in om], i1, i2, j1, j2))
    out = []
    for idx, i1, i2, j1, j2 in cand:
        K = (i2 - i1) + 6
        reserve = [B[j] for j in range(max(0, j1 - K), min(len(B), j2 + K)) if j in libres]
        run = []
        for i in (i for i in idx if _couvert(A[i], reserve, A[i + 1:]) is None):
            if run and i != run[-1] + 1:
                out.append(run)
                run = []
            run.append(i)
        if run:
            out.append(run)
    return out


def texte_de(A, run):
    return " ".join(A[i][1] for i in run)


# --------------------------------------------------------------------- unités

class Ref:
    """Les éditions de référence d'un siman, séif par séif (R1, R2, R3)."""

    def __init__(self, eds):
        self.defaut, self.alts, self.ignorees = references(eds)
        D = self.D = court(self.defaut["titre"]) if self.defaut else None
        self.nom_alts = [court(e["titre"]) for e in self.alts]
        self.chap, self.seifs, self.bruts = {"": []}, [], []
        self.mots, self.omis, self.ratio, self.ecartees = [], [], [], []
        self.chap_brut, self._lettres = "", {}
        self.defaut_sefaria = defaut_sefaria(eds)
        if not self.defaut:
            return
        sd = self.defaut["seifim"]
        nseifs = max([i + 1 for i, s in enumerate(sd) if consonants(s)] or [0])
        for i in range(nseifs):
            raw = sd[i]
            if i == 0:
                m = CHAPEAU.match(raw)
                if m:
                    self.chap[consonants(m.group(0))] = [D]
                    self.chap_brut = m.group(0)
                    raw = CHAPEAU.sub('', raw)
            c0 = consonants(raw)
            var, br, rat, om = {}, {}, {}, {}
            md = mots(raw)
            if c0:
                var[c0] = [D]
                br[D] = raw
            for e in self.alts:
                if i >= len(e["seifim"]) or not consonants(e["seifim"][i]):
                    continue
                r = e["seifim"][i]
                c = consonants(r)
                nom = court(e["titre"])
                rat[nom] = ressemblance(squelette(c0), squelette(c)) if c0 else 0.0
                if rat[nom] < SEUIL_ALIGNEMENT:
                    self.ecartees.append((i + 1, nom, rat[nom]))
                    continue
                var.setdefault(c, []).append(nom)
                br[nom] = r
                om[nom] = omissions(md, mots(r))
            self.seifs.append(var)
            self.bruts.append(br)
            self.ratio.append(rat)
            self.omis.append(om)
            self.mots.append(md)

    def lettres_de(self, i, nom):
        """`lettres` du séif i+1 dans l'édition `nom` (i = "chapeau" : le chapeau)."""
        if (i, nom) not in self._lettres:
            self._lettres[(i, nom)] = lettres(self.chap_brut if i == "chapeau" else
                                              self.bruts[i].get(nom, ""))
        return self._lettres[(i, nom)]

    def garde(self, i, labs, Lp, mots_p):
        """La garde ktiv sur un passage de la page dont le squelette est celui du
        séif i+1 dans les éditions `labs`. Rend (éditions où la page ne s'écarte
        qu'au ktiv près — l'édition par défaut d'abord —, mots changés si AUCUNE ne
        passe — rapportés à l'édition par défaut si elle est de `labs` —, mots égaux
        au ktiv près seulement dans la première retenue)."""
        retenues, changes, ktiv, rapporte = [], None, None, None
        for nom in sorted(labs, key=lambda l: l != self.D):
            Ls, ms = self.lettres_de(i, nom)
            ch, kt = garde_ktiv(Lp, mots_p, Ls, ms)
            if not ch:
                retenues.append(nom)
                ktiv = kt if ktiv is None else ktiv
            elif changes is None:
                changes, rapporte = ch, nom
        if retenues or not changes:
            return tuple(retenues), [], ktiv or []
        # Le mot de la page est-il, À SA PLACE, celui de l'AUTRE édition de référence ?
        # La page mêle alors deux éditions à l'intérieur du séif — ce qui ne passe pas.
        # La place se lit par un alignement mot à mot (squelettes) de la page et de
        # l'autre édition : un mot seulement présent ailleurs dans le séif ne compte pas.
        ids = list(dict.fromkeys(x[1] for x in Lp))
        cles_p = [squelette(consonants(mots_p[w])) for w in ids]
        lecon = {}
        for nom in ([] if i == "chapeau" else [x for x in self.bruts[i] if x != rapporte]):
            mo = [consonants(w) for w in self.lettres_de(i, nom)[1]]
            sm = difflib.SequenceMatcher(None, cles_p, [squelette(w) for w in mo], autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                    for d in range(i2 - i1):
                        if consonants(mots_p[ids[i1 + d]]) == mo[j1 + d]:
                            lecon.setdefault(ids[i1 + d], []).append(nom)
        out = []
        for mp, ms, nat, wp in changes:
            chez = lecon.get(wp, [])
            out.append((mp, ms, nat + (f" ; à cette place, « {mp} » est le mot de "
                                       f"{' / '.join(chez)} : deux éditions mêlées dans le séif"
                                       if chez else "")))
        return (), out, []

    def omis_par(self, i, nom):
        """Indices des mots du séif i+1 de l'édition par défaut que `nom` n'a pas."""
        return {j for run in self.omis[i].get(nom, []) for j in run}

    def mention(self, i, run):
        """« absent aussi de Torat Emet 363 », « Torat Emet 363 le porte »…"""
        out = []
        for nom in self.nom_alts:
            if nom not in self.ratio[i]:
                out.append(f"{nom} n'a pas ce séif")
            elif nom not in self.omis[i]:
                out.append(f"{nom} non alignée sur ce séif ({self.ratio[i][nom]:.2f})")
            else:
                s = self.omis_par(i, nom)
                if set(run) <= s:
                    out.append(f"absent aussi de {nom}")
                elif set(run) & s:
                    out.append(f"absent en partie de {nom} aussi")
                else:
                    out.append(f"{nom} le porte")
        return " · ".join(out)


def apparier(P, unites_, cle, D):
    """Programmation dynamique : la page P est-elle EXACTEMENT la suite des
    unités, chaque unité prise dans l'une quelconque de ses éditions ? Rend, par
    unité, (éditions retenues, début, fin) — ou None. À position égale, le chemin
    qui prend le MOINS de séifs hors de l'édition par défaut l'emporte. `cle` est
    l'identité (verdict IDENTIQUE) ou le squelette (verdict ÉQUIVALENT)."""
    etats = {0: (0, ())}
    for u in unites_:
        uk = {}
        for c, labs in u.items():
            uk.setdefault(cle(c), [])
            uk[cle(c)] += [l for l in labs if l not in uk[cle(c)]]
        nouv = {}
        for pos, (cout, chemin) in etats.items():
            for k, labs in uk.items():
                if P.startswith(k, pos):
                    np_ = pos + len(k)
                    c2 = cout + (0 if (not labs or D in labs) else 1)
                    if np_ not in nouv or c2 < nouv[np_][0]:
                        nouv[np_] = (c2, chemin + ((tuple(labs), pos, np_),))
        etats = nouv
        if not etats:
            return None
    r = etats.get(len(P))
    return r[1] if r else None


def _ngrammes(s):
    return {s[i:i + NGRAMME] for i in range(max(1, len(s) - NGRAMME + 1))}


def proximite(a, b):
    A, B = _ngrammes(a), _ngrammes(b)
    return len(A & B) / max(1, len(A | B))


def _omission_retenue(ref, i, labs, deb, fin):
    """R3 — un séif retenu hors de l'édition par défaut : rend None, ou le détail
    de ce que l'édition par défaut porte et que la page (= labs[0]) n'a pas."""
    if not labs or ref.D in labs:
        return None
    runs = ref.omis[i].get(labs[0], [])
    if not runs:
        return None
    return {"deb": deb, "fin": fin, "runs": [(texte_de(ref.mots[i], r), ref.mention(i, r))
                                             for r in runs]}


def localiser(page, ref):
    """La page diverge : où, et de quelle édition est-elle la plus proche ?
    Parcours séif par séif, au squelette. Un séif retrouvé tel quel dans l'une
    des éditions est « retenu » (ou, s'il ne l'est que hors de l'édition par
    défaut et que celle-ci porte un passage qu'il n'a pas, en « OMISSION ») ;
    sinon on cherche le début d'un séif suivant pour borner le passage de la page
    qui lui correspond, et l'écart est rapporté à l'édition la plus proche DE CE
    SÉIF — plus la liste des mots de l'édition par défaut absents de la page.
    Un séif retrouvé au squelette passe encore la garde ktiv : un yod/vav échangé
    en fait un « MOT CHANGÉ ».
    Rend une liste de (séif, statut, éditions, détail)."""
    chap, seifs, bruts = ref.chap, ref.seifs, ref.bruts
    SP, brut_page = squelette(page.cons), page.brut
    pm = mots(brut_page)
    sq_seifs = []
    for u in seifs:
        d = {}
        for c, labs in u.items():
            d.setdefault(squelette(c), [])
            d[squelette(c)] += [l for l in labs if l not in d[squelette(c)]]
        sq_seifs.append(d)
    pos, out = 0, []
    suite = None                 # lettre où commence un séif qui suit un séif retenu
    chaps = sorted((squelette(c) for c in chap if c), key=len, reverse=True)
    for k in chaps:
        if SP.startswith(k, 0):
            pos = len(k)
            suite, _, chg, _ = _garde_unite(ref, "chapeau", [ref.D], page, 0, pos)
            if chg:
                out.append((0, "MOT CHANGÉ", (ref.D,), {"deb": 0, "fin": pos, "mots": chg}))
            break
    else:
        # Un chapeau RÉCRIT (au siman 252, « בע"ש » développé en « בערב שבת ») :
        # sans ce cas, il était compté dans le séif א, et le séif א — que Torat
        # Emet donne sans chapeau — paraissait plus proche de Maginei Eretz qu'il
        # ne l'est. Le chapeau est rapporté à part, et le séif א commence là où
        # son propre début se lit.
        if chaps and sq_seifs:
            fenetre = len(chaps[0]) * 2 + 40
            q = [SP.find(k2[:ANCRE], 1, fenetre) for k2 in sq_seifs[0] if k2]
            q = [x for x in q if x > 0]
            if q:
                pos = min(q)
                k = chaps[0]
                p = len(os.path.commonprefix([SP[:pos], k]))
                out.append((0, "CHAPEAU DIVERGENT", tuple(chap[c] for c in chap if c)[0],
                            {"page_mid": SP[p:pos], "ed_mid": k[p:],
                             "page_mots": mots_autour(brut_page, p)}))
    i, N = 0, len(sq_seifs)
    while i < N:
        u = sq_seifs[i]

        def suit(k):
            np_ = pos + len(k)
            if i + 1 >= N:
                return np_ == len(SP)
            return any(SP.startswith(k2, np_) for k2 in sq_seifs[i + 1])
        ok = [(k, labs) for k, labs in u.items() if SP.startswith(k, pos)]
        if ok:
            bons = [x for x in ok if suit(x[0])]
            # À longueur égale, l'édition par défaut d'abord (R3).
            k, labs = max(bons or ok, key=lambda x: (len(x[0]), ref.D in x[1]))
            # Une édition plus COURTE peut être un PRÉFIXE de la page sans être
            # son texte : au siman 262 (état du 14 septembre), le séif א de Torat
            # Emet Freeware, qui n'a pas la parenthèse de sources, se lisait en
            # tête d'une page qui la porte — le séif א était « retenu » et la
            # parenthèse passait au compte du séif ב. Un séif n'est donc retenu
            # que si le suivant commence juste après lui ; si le début du suivant
            # se lit PLUS LOIN, ce qui est entre les deux appartient à ce séif-ci,
            # qui diverge — à une condition : qu'une AUTRE édition de ce séif soit
            # plus proche du passage entier que celle qui s'y lit en préfixe (au
            # 262, les deux autres portent la parenthèse). Sinon l'excédent n'est
            # le texte d'aucune édition de ce séif — au 264, le marqueur « [ט] »
            # posé en tête du séif suivant — et il reste au compte du suivant.
            # (Si le début du suivant ne se lit nulle part, rien ne permet
            # d'attribuer la suite : le séif est retenu.)
            plus_loin = []
            if not bons and i + 1 < N:
                q = [x for x in (SP.find(k2[:ANCRE], pos) for k2 in sq_seifs[i + 1] if k2)
                     if x > pos + len(k)]
                if q:
                    seg = SP[pos:min(q)]
                    autres = [kk for kk in u if kk != k]
                    if autres and max(proximite(seg, kk) for kk in autres) > proximite(seg, k):
                        plus_loin = q
            if not plus_loin:
                debut = suite if suite is not None else page._bout(pos)
                suite, ret, chg, _ = _garde_unite(ref, i, labs, page, debut, pos + len(k))
                om = ret and _omission_retenue(ref, i, ret, pos, pos + len(k))
                if not ret:
                    out.append((i + 1, "MOT CHANGÉ", labs,
                                {"deb": pos, "fin": pos + len(k), "mots": chg}))
                elif om:
                    out.append((i + 1, "OMISSION", ret, om))
                else:
                    out.append((i + 1, "RETENU", ret, {"deb": pos, "fin": pos + len(k)}))
                pos += len(k)
                i += 1
                continue
        # Borner le passage : le premier séif suivant dont le début se retrouve.
        suite = None
        fin, j = len(SP), N
        for jj in range(i + 1, N):
            q = [SP.find(k2[:ANCRE], pos) for k2 in sq_seifs[jj] if k2]
            q = [x for x in q if x >= 0]
            if q:
                fin, j = min(q), jj
                break
        seg = SP[pos:fin]
        cands = sorted(((proximite(seg, k), k, labs) for k, labs in u.items()),
                       key=lambda x: -x[0])
        if not seg:
            # Le séif suivant commence là où celui-ci devrait : il est ABSENT de
            # la page, et non « divergent » contre un passage vide.
            out.append((i + 1, "NON RETROUVÉ", (), None))
        elif not cands:
            out.append((i + 1, "SANS TEXTE", (), None))
        else:
            sc, k, labs = cands[0]
            p = len(os.path.commonprefix([seg, k]))
            s = len(os.path.commonprefix([seg[p:][::-1], k[p:][::-1]]))
            autres = " · ".join(f"{'+'.join(l)} {x:.2f}" for x, _, l in cands[1:])
            ed = labs[0]
            # R3 — les mots de l'édition par défaut sans contrepartie dans la page.
            seg_mots = [m for m in pm if pos <= m[3] < fin]
            omis = [(texte_de(ref.mots[i], r), ref.mention(i, r))
                    for r in omissions(ref.mots[i], seg_mots)]
            detail = {
                "proximite": sc, "autres": autres, "deb": pos, "fin": fin,
                "page_long": len(seg), "ed_long": len(k), "p": p, "s": s,
                "page_mid": seg[p:len(seg) - s], "ed_mid": k[p:len(k) - s],
                "page_mots": mots_autour(brut_page, pos + p),
                "ed_mots": mots_autour(bruts[i].get(ed, ""), p),
                "omis": omis,
            }
            out.append((i + 1, "DIVERGENT", labs, detail))
        for jj in range(i + 1, j):
            out.append((jj + 1, "NON RETROUVÉ", (), None))
        pos, i = fin, j
    if pos < len(SP):
        out.append((None, "SURPLUS", (), {"long": len(SP) - pos,
                                          "page_mots": mots_autour(brut_page, pos)}))
    return out


def retenue(chemin, D):
    """L'édition retenue pour chaque séif, et son résumé. Si une même édition
    donne TOUS les séifs, c'est elle (l'édition par défaut si elle en est) ;
    sinon chaque séif prend l'édition par défaut s'il la donne, l'autre sinon.
    Rend (résumé, [édition par séif])."""
    seifs = [list(l) for l in chemin if l]
    if not seifs:
        return "—", []
    communes = set.intersection(*(set(l) for l in seifs))
    if communes:
        l0 = D if D in communes else next(l for l in seifs[0] if l in communes)
        return l0, [l0] * len(seifs)
    choix = [D if D in l else l[0] for l in seifs]
    comptes = {}
    for c in choix:
        comptes[c] = comptes.get(c, 0) + 1
    return ("MÉLANGE — " + " · ".join(f"{l} {c} séif{'s' if c > 1 else ''}" for l, c in
                                      sorted(comptes.items(), key=lambda x: (x[0] != D, -x[1]))),
            choix)


# ----------------------------------------------------------------------- page

class Page:
    """Le texte source d'une page : ses consonnes, ses lettres placées dans leurs
    mots (`lettres`), et la position de chaque consonne du squelette."""

    def __init__(self, brut):
        self.brut, self.cons = brut, consonants(brut)
        self.L, self.mots = lettres(brut)
        self.sk = [k for k, x in enumerate(self.L) if x[0] not in YV]
        # `lettres` lit exactement les consonnes de `consonants` ; si ce n'était pas le
        # cas, la garde ne saurait où sont les mots : elle ne passe rien (MOT CHANGÉ).
        self.lisible = "".join(x[0] for x in self.L) == self.cons

    def _bout(self, b):
        """L'indice de lettre qui suit la consonne b-1 du squelette et les yod/vav
        de SON mot : les yod/vav suivants appartiennent au mot (au séif) suivant."""
        if b <= 0:
            return 0
        if b >= len(self.sk):
            return len(self.L)
        k, w = self.sk[b - 1] + 1, self.L[self.sk[b - 1]][1]
        while k < len(self.L) and self.L[k][0] in YV and self.L[k][1] == w:
            k += 1
        return k

    def fins(self, b):
        """Les fins possibles, en indice de lettre, d'un passage dont le squelette
        s'achève à la consonne b-1 : après le mot de cette consonne, puis après
        chacun des mots faits de yod/vav SEULS qui le suivent avant le mot de la
        consonne b (« ו׳ » qui clôt 346:1) — un tel mot ne dit pas de lui-même à quel
        séif il appartient ; `_garde_unite` essaie chaque coupure."""
        if b >= len(self.sk):
            return [len(self.L)]
        k = self._bout(b)
        out, w_suiv = [k], self.L[self.sk[b]][1]
        while k < self.sk[b] and self.L[k][1] != w_suiv:
            w = self.L[k][1]
            while k < self.sk[b] and self.L[k][1] == w:
                k += 1
            out.append(k)
        return out


def _garde_unite(ref, i, labs, page, debut, b):
    """La garde ktiv sur une unité de la page (séif i+1, ou i = "chapeau") qui
    commence à la lettre `debut` et dont le squelette s'achève à la consonne b-1 :
    (fin, éditions retenues, mots changés, mots égaux au ktiv près). La première
    coupure (`Page.fins`) où une édition passe l'emporte ; si aucune ne passe, le
    rapport est celui de la coupure la plus courte."""
    if not page.lisible:
        return (len(page.L), (), [("?", "?", "lettres de la page illisibles par la garde")], [])
    premier = None
    for fin in page.fins(b):
        ret, chg, kt = ref.garde(i, labs, page.L[debut:fin], page.mots)
        if ret:
            return fin, ret, chg, kt
        premier = premier or (fin, ret, chg, kt)
    return premier


def page_source(path):
    html_ = open(path, encoding="utf-8").read()
    b = re.findall(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>',
                   html_, re.S)
    brut = " ".join(ETIQ.sub("", x) for x in b)
    return len(b), consonants(brut), brut


def chemin(n, suf):
    return os.path.join(SECTION, f"siman-{n}", f"niveau-1-base{suf}.html")


def juger(cons, brut, ref):
    """(verdict, éditions retenues par séif, rapport de localisation, mots égaux au
    ktiv près seulement). Une page qui est, séif par séif, la copie d'une édition
    de référence passe — sauf si un séif pris hors de l'édition par défaut y perd un
    passage que celle-ci porte (R3), ou si, au squelette près seulement, un yod/vav
    y est ÉCHANGÉ ou ajouté en tête ou en fin de mot (garde ktiv) : la page est
    alors DIVERGENTE et le rapport nomme l'omission ou le mot changé."""
    page = Page(brut)
    with_chap = [ref.chap] + ref.seifs
    premier = None
    for verdict, cle, P in (("IDENTIQUE", lambda c: c, cons),
                            ("ÉQUIVALENT", squelette, squelette(cons))):
        ch = apparier(P, with_chap, cle, ref.D)
        if ch is None:
            continue
        (labs0, a0, b0), ch = ch[0], ch[1:]
        loc, defaut_, retenus, ktiv, debut = [], False, [], [], 0
        if verdict == "ÉQUIVALENT" and b0 > a0:
            debut, _, chg, _ = _garde_unite(ref, "chapeau", labs0, page, 0, b0)
            if chg:
                loc.append((0, "MOT CHANGÉ", labs0, {"deb": a0, "fin": b0, "mots": chg}))
                defaut_ = True
        for i, (labs, a, b) in enumerate(ch):
            if verdict == "ÉQUIVALENT":
                debut, ret, chg, kt = _garde_unite(ref, i, labs, page, debut, b)
                if not ret:
                    loc.append((i + 1, "MOT CHANGÉ", labs, {"deb": a, "fin": b, "mots": chg}))
                    retenus.append(labs)
                    defaut_ = True
                    continue
                labs = ret
                ktiv += [(i + 1, mp, ms, labs[0]) for mp, ms, *_ in kt]
            om = _omission_retenue(ref, i, labs, a, b)
            defaut_ = defaut_ or bool(om)
            loc.append((i + 1, "OMISSION", labs, om) if om else
                       (i + 1, "RETENU", labs, {"deb": a, "fin": b}))
            retenus.append(labs)
        if not defaut_:
            return verdict, retenus, None, ktiv
        premier = premier or loc
    if premier:
        return "DIVERGENCE", None, premier, []
    return "DIVERGENCE", None, localiser(page, ref), []


def un_siman(n, bref, rafraichir, stats):
    """Renvoie (texte_ok, decoupe_ok) — ou None si le siman n'a pas été confronté."""
    presentes = [(lang, suf) for lang, suf in LANGS if os.path.exists(chemin(n, suf))]
    if not presentes:
        # Rien à confronter, et ce n'est pas « conforme » : une copie lancée hors
        # du dépôt, ou un siman qui n'existe pas. On ne va pas sur Sefaria.
        r = f"aucune page niveau-1-base sous {os.path.join(SECTION, f'siman-{n}')}"
        print(f"  siman {n:3d} : NON CONFRONTÉ — {r}")
        stats["sans_page"].append((n, r))
        return None
    src = fetch(n, rafraichir)
    if src is None:
        print(f"  siman {n:3d} : NON ATTEINT — {RAISONS.get(n)}")
        stats["non_atteints"].append((n, RAISONS.get(n)))
        return None
    eds = src["editions"]
    ref = Ref(eds)
    D = ref.D
    seifs = ref.seifs
    if ref.defaut is None or not seifs:
        # `fetch` ne rend que des réponses que `valider` accepte : ce cas ne se
        # présente pas. Il reste gardé — la porte ne conclut pas sur une référence
        # vide (le Mehaber n'a aucune lacune connue en Hilkhot Chabbat).
        RAISONS[n] = f"édition par défaut {court(DEFAUT)} introuvable ou vide après lecture"
        print(f"  siman {n:3d} : NON ATTEINT — {RAISONS[n]}")
        stats["non_atteints"].append((n, RAISONS[n]))
        return None

    stats["simanim"] += 1
    stats["defaut"][D] = stats["defaut"].get(D, 0) + 1
    for e in [ref.defaut] + ref.alts:
        if consonants("".join(e["seifim"])):
            stats["editions_lues"][court(e["titre"])] = stats["editions_lues"].get(court(e["titre"]), 0) + 1
    for e in ref.ignorees:
        stats["ignorees"][court(e["titre"])] = stats["ignorees"].get(court(e["titre"]), 0) + 1
    for i, rat in enumerate(ref.ratio):
        for nom, r in rat.items():
            st = stats["alignement"].setdefault(nom, [0, 0, 1.0])
            st[0] += 1
            if r >= SEUIL_ALIGNEMENT:
                st[1] += 1
                st[2] = min(st[2], r)
    for s_, nom, r in ref.ecartees:
        stats["ecartees"].append((n, s_, nom, r))
    nseifs = len(seifs)
    stats["seifim"] += nseifs
    texte_ok, decoupe_ok = True, True
    cons_par_langue, nb_par_langue, res = {}, {}, {}
    for lang, suf in LANGS:
        p = chemin(n, suf)
        if not os.path.exists(p):
            if not bref:
                print(f"  {lang}: FICHIER ABSENT {p}")
            stats["fichiers_absents"].append((n, lang))
            texte_ok = False
            continue
        nb, cons, brut = page_source(p)
        stats["pages"] += 1
        cons_par_langue[lang], nb_par_langue[lang] = cons, nb
        verdict, ch, loc, kt = juger(cons, brut, ref)
        res[lang] = (verdict, ch, loc, kt)
        if kt:
            stats["ktiv"].append((n, lang, kt))
        stats["pages_verdict"][verdict] = stats["pages_verdict"].get(verdict, 0) + 1
        if verdict == "DIVERGENCE":
            texte_ok = False
            for s_, st, labs, d in loc:
                cle = st if st != "RETENU" else ("RETENU" if D in labs else "RETENU hors défaut")
                stats["div_seifs"][cle] = stats["div_seifs"].get(cle, 0) + 1
                if st == "RETENU" and D not in labs:
                    stats["seifs_hors_defaut"].add((n, lang, s_, labs[0], "page divergente"))
                if st == "DIVERGENT":
                    stats["div_proches"][labs[0]] = stats["div_proches"].get(labs[0], 0) + 1
                if st == "OMISSION":
                    stats["omissions"].append((n, lang, s_, labs[0], [t for t, _ in d["runs"]]))
                if st == "MOT CHANGÉ":
                    stats["mots_changes"].append((n, lang, s_, d["mots"]))
        else:
            for l in retenue(ch, D)[1]:
                stats["seifs_par_edition"][l] = stats["seifs_par_edition"].get(l, 0) + 1
            for i, labs in enumerate(ch, 1):
                if labs and D not in labs:
                    stats["seifs_hors_defaut"].add((n, lang, i, labs[0], "page conforme"))
        if nb != nseifs:
            decoupe_ok = False
    parite = len(set(cons_par_langue.values())) <= 1

    pire = ("DIVERGENCE" if any(v[0] == "DIVERGENCE" for v in res.values()) else
            "ÉQUIVALENT" if any(v[0] == "ÉQUIVALENT" for v in res.values()) else
            "IDENTIQUE" if res else "PAGE ABSENTE")
    stats["verdict"].setdefault(pire, []).append(n)

    if bref:
        blocs = "/".join(str(nb_par_langue.get(l, "—")) for l, _ in LANGS)
        etat = "❌" if not texte_ok else ("≈ " if pire == "ÉQUIVALENT" else "✅")
        eds_txt = sorted({retenue(v[1], D)[0] for v in res.values() if v[1] is not None})
        div = sorted({s for v in res.values() if v[2] for s, st, _, _ in v[2]
                      if st in ("DIVERGENT", "NON RETROUVÉ", "SANS TEXTE", "CHAPEAU DIVERGENT",
                                "OMISSION", "MOT CHANGÉ")
                      and s is not None})
        proches = sorted({labs[0] for v in res.values() if v[2] for _, st, labs, _ in v[2]
                          if st == "DIVERGENT" and labs})
        omis = sorted({s for v in res.values() if v[2] for s, st, _, _ in v[2] if st == "OMISSION"})
        changes = sorted({(s, mp, ms) for v in res.values() if v[2] for s, st, _, d in v[2]
                          if st == "MOT CHANGÉ" for mp, ms, _ in d["mots"]})
        ktiv = sorted({(s, mp, ms) for v in res.values() for s, mp, ms, _ in v[3]})
        hors = sorted({f"{lettre(i)}={c}" for v in res.values() if v[1] is not None
                       for i, c in enumerate(retenue(v[1], D)[1], 1) if c != D})
        extra = (f" · édition {' / '.join(eds_txt)}" if eds_txt else "")
        if hors:
            extra += f" (hors {D} : {' '.join(hors)})"
        if div:
            extra += (f" · séifs {','.join(lettre(s) if s else 'chapeau' for s in div)} — plus proche : "
                      f"{' / '.join(proches) or '—'}")
        if omis:
            extra += f" · OMISSION (R3) au séif {','.join(lettre(s) for s in omis)}"
        if changes:
            extra += " · MOT CHANGÉ (garde ktiv) : " + " ".join(
                f"{lettre(s) if s else 'chapeau'} «{mp}»/«{ms}»" for s, mp, ms in changes)
        if ktiv:
            extra += " · au ktiv près seulement : " + " ".join(
                f"{lettre(s)} «{mp}»/«{ms}»" for s, mp, ms in ktiv)
        if ref.defaut_sefaria not in (None, DEFAUT):
            extra += f" · Sefaria sert {court(ref.defaut_sefaria)} par défaut"
        if ref.ecartees:
            extra += f" · non alignée (R2) : {' '.join(f'{lettre(s)}={nom}' for s, nom, _ in ref.ecartees)}"
        print(f"  siman {n:3d} : {nseifs:2d} séifim · blocs {blocs:>8s} · "
              f"texte {etat} · découpe {'✅' if decoupe_ok else '⚠️ '}"
              f"{'' if parite else ' ⚠️ parité'}{extra}")
        return texte_ok, decoupe_ok and parite

    lues = " · ".join(f"{court(e['titre'])} ({sum(1 for s in e['seifim'] if consonants(s))})"
                      for e in [ref.defaut] + ref.alts)
    print(f"\n=== Siman {n} — Hilkhot Chabbat : {nseifs} séifim dans l'édition par défaut ===")
    print(f"  éditions de référence (séifs non vides) : {lues} — par défaut : {D}")
    if ref.defaut_sefaria not in (None, DEFAUT):
        print(f"  ⚠️  Sefaria sert désormais {court(ref.defaut_sefaria)} par défaut ; la porte "
              f"reste épinglée sur {D}")
    if ref.ignorees:
        print(f"  servies et IGNORÉES (R1 — ni {D}, ni {ALTERNATIVE}) : " + " · ".join(
            f"{court(e['titre'])} ({sum(1 for s in e['seifim'] if consonants(s))})" for e in ref.ignorees))
    for s_, nom, r in ref.ecartees:
        print(f"  ⚠️  R2 : {nom} séif {lettre(s_)} ({s_}) NON ALIGNÉE sur {D} (ressemblance {r:.2f} "
              f"< {SEUIL_ALIGNEMENT:.2f}) — écartée pour ce séif")
    for lang, suf in LANGS:
        if lang not in res:
            if not os.path.exists(chemin(n, suf)):
                print(f"  {lang}: FICHIER ABSENT {chemin(n, suf)}")
            continue
        nb = nb_par_langue[lang]
        verdict, ch, loc, kt = res[lang]
        dec = "✅" if nb == nseifs else f"⚠️  {nb} blocs pour {nseifs} séifim"
        if verdict == "IDENTIQUE":
            v = f"✅ IDENTIQUE à {retenue(ch, D)[0]}"
        elif verdict == "ÉQUIVALENT":
            v = f"≈ ÉQUIVALENT à {retenue(ch, D)[0]} (ktiv haser/malé seulement)"
        else:
            v = "❌ DIVERGENCE"
        print(f"  {lang}: {nb} blocs | texte : {v} | découpe : {dec}")
        if kt:
            print(f"      mots égaux au ktiv près SEULEMENT (yod/vav ajouté à l'intérieur du mot ; "
                  f"à contrôler) : " + " · ".join(f"séif {lettre(s)} page « {mp} » / {e} « {ms} »"
                                                 for s, mp, ms, e in kt))
        if ch is not None:
            choix = retenue(ch, D)[1]
            hors = [(i, c) for i, c in enumerate(choix, 1) if c != D]
            if hors:
                print(f"      séifs pris HORS de l'édition par défaut ({D}), et l'édition retenue : "
                      + " ".join(f"{lettre(i)}={c}" for i, c in hors))
        if loc:
            ret = [s for s, st, _, _ in loc if st == "RETENU"]
            if ret:
                print(f"      {len(ret)} séif(s) retrouvé(s) tels quels (au ktiv près) "
                      f"dans une édition de référence")
            hors = [(s, labs[0]) for s, st, labs, _ in loc if st == "RETENU" and D not in labs]
            if hors:
                print(f"      dont pris HORS de {D} : " + " ".join(f"{lettre(s)}={c}" for s, c in hors))
            for s, st, labs, d in loc:
                if st == "RETENU":
                    continue
                if st == "SURPLUS":
                    print(f"      SURPLUS : {d['long']} consonnes après le dernier séif — "
                          f"« {d['page_mots']} »")
                    continue
                if st == "CHAPEAU DIVERGENT":
                    print(f"      CHAPEAU du siman récrit (seul {'+'.join(labs)} en porte un) : "
                          f"page « {d['page_mid'][:40] or '∅'} » / « {d['ed_mid'][:40] or '∅'} » "
                          f"(squelette) — {d['page_mots']}")
                    continue
                if st in ("NON RETROUVÉ", "SANS TEXTE"):
                    print(f"      séif {lettre(s)} ({s}) : {st} — son début ne se lit nulle part "
                          f"après le séif précédent (absent, fondu, ou altéré dès ses premiers mots)")
                    continue
                if st == "MOT CHANGÉ":
                    nom_s = f"séif {lettre(s)} ({s})" if s else "chapeau"
                    ed = D if D in labs else labs[0]
                    print(f"      {nom_s} : MOT CHANGÉ (garde ktiv) — égal à {'+'.join(labs)} au "
                          f"squelette seulement :")
                    for mp, ms, nat in d["mots"]:
                        print(f"          page « {mp} » / {ed} « {ms} » — yod/vav {nat}")
                    continue
                if st == "OMISSION":
                    print(f"      séif {lettre(s)} ({s}) : OMISSION (R3) — la page est {'+'.join(labs)} "
                          f"mot pour mot, mais {D} porte ce qu'elle n'a pas :")
                    for t, m in d["runs"]:
                        print(f"          « {t} » — {m}")
                    continue
                print(f"      séif {lettre(s)} ({s}) : DIVERGENT — édition la plus proche : "
                      f"{'+'.join(labs)} (ressemblance {d['proximite']:.2f}"
                      f"{'; ' + d['autres'] if d['autres'] else ''})")
                if len(d["page_mid"]) <= 40 and len(d["ed_mid"]) <= 40:
                    print(f"          écart (squelette) : page « {d['page_mid'] or '∅'} » / "
                          f"{labs[0]} « {d['ed_mid'] or '∅'} »")
                else:
                    print(f"          1re divergence @{d['p']} du séif ; écart de "
                          f"{len(d['page_mid'])} (page) / {len(d['ed_mid'])} ({labs[0]}) consonnes")
                print(f"          page   : {d['page_mots']}")
                print(f"          {labs[0]:6s} : {d['ed_mots']}")
                for t, m in d["omis"]:
                    print(f"          mots de {D} sans contrepartie dans la page : « {t} » — {m}")

    if not parite:
        print("  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE")
    elif cons_par_langue:
        print("  parité FR/HE/EN du texte source : ✅ identique")
    return texte_ok, decoupe_ok and parite


def main(argv):
    bref = "--bref" in argv
    rafraichir = "--rafraichir" in argv
    nums = [int(a) for a in argv if a.isdigit()]
    if "--tous" in argv:
        nums = (sorted(int(d.split("-")[1]) for d in os.listdir(SECTION)
                       if d.startswith("siman-")) if os.path.isdir(SECTION) else [])
    elif not nums:
        print(__doc__); return 2
    stats = {"simanim": 0, "seifim": 0, "pages": 0, "non_atteints": [], "sans_page": [],
             "verdict": {}, "pages_verdict": {}, "seifs_par_edition": {},
             "seifs_hors_defaut": set(), "editions_lues": {}, "ignorees": {}, "defaut": {},
             "alignement": {}, "ecartees": [], "omissions": [], "fichiers_absents": [],
             "div_seifs": {}, "div_proches": {}, "ktiv": [], "mots_changes": []}
    print(f"=== Texte source de Hilkhot Chabbat vs {court(DEFAUT)}, l'édition par défaut (et "
          f"{ALTERNATIVE} pour les leçons) — {len(nums)} siman(im) · ROOT {ROOT} ===")
    faux_texte, faux_decoupe = [], []
    for n in nums:
        r = un_siman(n, bref, rafraichir, stats)
        if r is None:
            continue
        t, d = r
        if not t: faux_texte.append(n)
        if not d: faux_decoupe.append(n)

    print(f"\nCONFRONTÉ : {stats['simanim']} siman(im) · {stats['seifim']} séifim · "
          f"{stats['pages']} pages")
    if stats["defaut"]:
        print("Édition par défaut : " + " · ".join(f"{k} ({v} simanim)" for k, v in stats["defaut"].items()))
    if stats["editions_lues"]:
        print("Éditions de référence lues (simanim où elles ont du texte) : " + " · ".join(
            f"{k} {v}" for k, v in sorted(stats["editions_lues"].items(), key=lambda x: -x[1])))
    if stats["ignorees"]:
        print("Éditions servies et IGNORÉES (R1) : " + " · ".join(
            f"{k} ({v} simanim)" for k, v in sorted(stats["ignorees"].items(), key=lambda x: -x[1])))
    for nom, (tot, ok, mn) in stats["alignement"].items():
        print(f"R2 — {nom} alignée sur {ok} séif(s) sur {tot} (ressemblance min des alignés "
              f"{mn:.3f}, seuil {SEUIL_ALIGNEMENT:.2f})"
              + (" ; écartés : " + " ".join(f"{n}:{lettre(s)} ({r:.2f})" for n, s, nm, r in stats["ecartees"]
                                           if nm == nom) if ok < tot else ""))
    if stats["pages_verdict"]:
        print("Pages par verdict : " + " · ".join(
            f"{k} {v}" for k, v in stats["pages_verdict"].items()))
    if stats["seifs_par_edition"]:
        print("Séifs (× page) des pages conformes, par édition retenue : " + " · ".join(
            f"{k} {v}" for k, v in sorted(stats["seifs_par_edition"].items(),
                                          key=lambda x: -x[1])))
    if stats["seifs_hors_defaut"]:
        l = sorted(stats["seifs_hors_defaut"])
        pg = sorted({(n, g) for n, g, *_ in l})
        print(f"Séifs que SEULE Torat Emet donne tels quels, sans omission (leçon excusée, R3) : "
              f"{len(l)} (× page), dans {len(pg)} pages — "
              + " ".join(f"{n}{g}:{lettre(s)}" for n, g, s, *_ in l))
    else:
        print("Séifs que seule Torat Emet donne tels quels : 0")
    if stats["omissions"]:
        print(f"OMISSIONS (R3) — séifs copiés d'une autre édition qui perdent un passage de "
              f"l'édition par défaut : {len(stats['omissions'])} (× page) — "
              + " ".join(f"{n}{g}:{lettre(s)}" for n, g, s, *_ in stats["omissions"]))
    else:
        print("OMISSIONS (R3) sur des séifs copiés d'une autre édition : 0")
    nk = sum(len(k) for _, _, k in stats["ktiv"])
    print(f"GARDE KTIV — mots égaux au ktiv près SEULEMENT (yod/vav ajouté à l'intérieur du mot), "
          f"dans les pages ÉQUIVALENT : {nk}"
          + (" — " + " ".join(f"{n}{g}:{lettre(s)} «{mp}»/«{ms}»" for n, g, k in stats["ktiv"]
                             for s, mp, ms, _ in k) if nk else ""))
    if stats["mots_changes"]:
        print(f"GARDE KTIV — séifs égaux au squelette seulement, un yod/vav ÉCHANGÉ, déplacé, ou "
              f"ajouté en tête ou en fin de mot (MOT CHANGÉ) : {len(stats['mots_changes'])} (× page) — "
              + " ".join(f"{n}{g}:{lettre(s) if s else 'chapeau'} " + ",".join(
                  f"«{mp}»/«{ms}»" for mp, ms, _ in m) for n, g, s, m in stats["mots_changes"]))
    else:
        print("GARDE KTIV — séifs où un yod/vav est ÉCHANGÉ, déplacé, ou ajouté en tête ou en fin "
              "de mot (MOT CHANGÉ) : 0")
    if stats["div_seifs"]:
        d = stats["div_seifs"]
        print(f"Dans les pages DIVERGENTES, séif par séif (× page) : "
              f"{d.get('RETENU', 0)} retrouvés tels quels dans l'édition par défaut · "
              f"{d.get('RETENU hors défaut', 0)} retrouvés tels quels dans Torat Emet seulement "
              f"(leçon, plus signalée) · "
              f"{d.get('OMISSION', 0)} copiés de Torat Emet avec omission (R3) · "
              f"{d.get('MOT CHANGÉ', 0)} égaux au squelette seulement (garde ktiv) · "
              f"{d.get('DIVERGENT', 0)} divergents des éditions de référence · "
              f"{d.get('NON RETROUVÉ', 0) + d.get('SANS TEXTE', 0)} non retrouvés · "
              f"{d.get('CHAPEAU DIVERGENT', 0)} chapeaux récrits · "
              f"{d.get('SURPLUS', 0)} surplus après le dernier séif")
        if stats["div_proches"]:
            print("   séifs divergents par édition la plus proche (celle à qui l'écart est rapporté) : "
                  + " · ".join(f"{k} {v}" for k, v in sorted(stats["div_proches"].items(),
                                                              key=lambda x: -x[1])))
    if stats["fichiers_absents"]:
        print(f"FICHIERS ABSENTS ({len(stats['fichiers_absents'])}) : "
              + " ".join(f"{n}{g}" for n, g in stats["fichiers_absents"]))
    print(f"→ {len(faux_texte)} dont le texte source diverge des éditions de référence "
          f"au-delà du ktiv haser/malé (omission R3 et fichier absent compris)")
    if faux_texte: print("   " + " ".join(map(str, faux_texte)))
    print(f"→ {len(faux_decoupe)} dont la découpe ou la parité s'écarte de la source")
    if faux_decoupe: print("   " + " ".join(map(str, faux_decoupe)))
    if stats["non_atteints"]:
        print(f"\nNON ATTEINTS ({len(stats['non_atteints'])}) — rien n'est conclu sur eux :")
        for n, r in stats["non_atteints"]:
            print(f"  siman {n} : {r}")
    if stats["sans_page"]:
        print(f"\nNON CONFRONTÉS faute de page ({len(stats['sans_page'])}) — rien n'est conclu sur eux :")
        for n, r in stats["sans_page"]:
            print(f"  siman {n} : {r}")
    if stats["pages"] == 0:
        print("❌ RIEN N'A ÉTÉ CONFRONTÉ — la porte ne conclut pas (code 3)."
              + ("" if os.path.isdir(SECTION) and nums else
                 f" Aucune page sous {SECTION} : copie lancée hors du dépôt ?"))
        return 3
    if faux_texte:
        return 1
    if stats["non_atteints"] or stats["sans_page"]:
        print("⚠️  conforme sur ce qui a été lu, mais des simanim n'ont pas été confrontés (code 3)")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
