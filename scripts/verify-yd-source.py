#!/usr/bin/env python3
"""Confronte le texte source (Mehaber + Rama) des simanim Yoré Déa aux sources
Sefaria — verbatim, consonnes identiques — à l'édition hébraïque PAR DÉFAUT de
Sefaria, et à elle seule pour ce qui est des OMISSIONS ; une seconde édition,
Torat Emet 357, peut seulement EXPLIQUER une leçon (voir R1-R4 plus bas).

Usage : python3 scripts/verify-yd-source.py 119 120 121
        python3 scripts/verify-yd-source.py --tous            # les 148 du dépôt
        python3 scripts/verify-yd-source.py --tous --bref     # une ligne par siman
        python3 scripts/verify-yd-source.py 95 --rafraichir   # ignore le cache

Codes de sortie : 0 aucune divergence · 1 une divergence au moins (texte source
contre les éditions de référence — une OMISSION d'un passage de l'édition par
défaut en est une, même quand Torat Emet 357 l'omet aussi —, fichier absent à
côté d'une page présente, ou parité FR/HE/EN) · 2 usage · 3 rien n'a été
confronté, ou un siman n'a pas été atteint (Sefaria injoignable, erreur servie en
HTTP 200, ref servi faux, édition par défaut vide, indécidable ou NON RECOUPÉE —
api/texts n'en sert pas la même, ou api/v3 ne sert pas une édition qu'il annonce —,
lacune annoncée par une API et démentie par l'autre), ou un siman demandé n'a aucune page sous
ROOT — la porte ne conclut pas, elle ne sort pas verte. Une divergence trouvée
ailleurs l'emporte : 1. La version d'avant octobre 2026 sortait en 0 sans
argument, « tout est conforme » sur zéro siman. Un cache de plus de
AGE_MAX_JOURS (30) jours n'est PAS un code : la porte le dit en tête et en pied
(tour 4, « âge du cache »).

Invariant vérifié, pour chaque siman N :
  - la CONCATÉNATION des <blockquote class="text-source"> de niveau-1-base
    reproduit EXACTEMENT la suite des seifim du Choul'han Aroukh Yoré Déa sur
    Sefaria, chaque séif pris dans l'une des deux éditions de RÉFÉRENCE
    (comparaison sur les seules consonnes hébraïques : nikud, ponctuation,
    balises et espaces sont ignorés ; le ktiv haser/malé n'est PAS toléré) ;
  - un séif pris dans Torat Emet 357 ne doit perdre AUCUN passage que porte
    l'édition par défaut (R3) ;
  - le titre-chapeau de Sefaria (« דין … ובו י״ג סעיפים ») est facultatif :
    il est retiré du texte de référence s'il n'est pas repris par la page ;
  - parité FR/HE/EN du texte source.
Le nombre de blocs est imprimé, il n'est pas jugé (il ne l'a jamais été ici : au
siman 100, six blocs pour quatre séifs, et le texte est celui de la source).

Rappel : le Choul'han Aroukh HaRav ne couvre pas Yoré Déa. Le niveau-4 des pages
Yoré Déa est `niveau-4-halakha` (psika pratique), pas `niveau-4-daat-harav` ;
c'est le niveau-1 qui porte le texte source, et c'est donc lui qu'on confronte.

LES ÉDITIONS. Sefaria sert le Choul'han Aroukh Yoré Déa en QUATRE éditions
hébraïques (`api/v3/texts/…?version=hebrew|all`, mesure du 8 octobre 2026 sur les
simanim 87-234 du dépôt) :
  · « Ashlei Ravrevei: Shulchan Aruch Yoreh Deah, Lemberg, 1888 » — priorité 2,
    non vocalisée, SEULE à porter le chapeau ; c'est elle qu'`api/texts` sert par
    défaut. 147/147 ;
  · « Torat Emet 357 » — priorité 1, VOCALISÉE, développe une partie des
    abréviations, a son ktiv, porte le texte CENSURÉ par endroits (« גוי » pour
    « עובד כוכבים », « עבודת כוכבים » pour « אלילים ») et n'a pas les notes de
    censeur entre crochets (228:8, 228:25, 228:35, 230:1, 232:12). 147/147, même
    nombre de séifs que l'édition par défaut partout ;
  · « Torat Emet Freeware Shulchan Aruch » — 113 simanim (113-234) ;
  · « Wikisource Shulchan Aruch » — 51 simanim, PARTIELLE.

LA RÈGLE COMMUNE aux trois portes de source (verify-chabbat-source,
verify-oh-niveau1-source, celle-ci), et ce qu'elle a donné ici :
  R1. Éditions de référence : l'édition PAR DÉFAUT (la priorité Sefaria
      strictement la plus haute — Ashlei Ravrevei, 147/147 —, RECOUPÉE avec
      l'édition qu'api/texts sert par défaut : voir `_recouper`) et « Torat Emet
      357 », ÉPINGLÉE PAR SON NOM (tour 4 : `^Torat Emet \d+$` admettait toute
      Torat Emet numérotée ; une autre serait ignorée et nommée), elles SEULES.
      Freeware et Wikisource ne sont jamais une référence : la porte les ignore
      et les NOMME quand elles sont servies.
      Pourquoi, mesuré par l'arbitre du premier tour : Freeware « 139 » est le
      texte du 138 ; Freeware 190:35 n'a pas « הגה: וכן עיקר », la DÉCISION du
      Rama ; Wikisource 114:10 omet « אע״פ ששאר עובדי כוכבים דרכן לערב בו יין » ;
      Wikisource et Freeware 123:1 n'ont pas la glose du Rama, et toutes deux
      ajoutent des « הערה » qui ne sont pas le livre. Le premier tour, qui les
      admettait sous deux gardes (ressemblance au siman ≥ 0,5 ; longueur de la
      leçon dans [0,6 ; 1,5]), certifiait IDENTIQUE, code 0, une page dont le
      séif 190:35 recopiait Freeware : le rapport de longueur y est 0,92. Ces
      deux gardes ad hoc ont disparu avec les éditions qu'elles filtraient.
      Coût : aucun verdict de siman n'en dépendait (voir la mesure plus bas).
  R2. Torat Emet 357 n'est admise pour un séif que si elle est ALIGNÉE sur le
      séif de même numéro de l'édition par défaut. Mesure : ratio de difflib sur
      les MOTS (clé de chaque mot : son squelette, ou ses lettres et ses marques
      s'il porte un guerech — même clé que pour R3). Au même séif, Torat Emet 357
      va de 0,636 (228:8, qui perd la note de censeur) à 1, 1 452 séifs ; contre
      le séif de même numéro du siman PRÉCÉDENT, jamais plus de 0,258 ; mais
      contre un AUTRE séif du même siman, jusqu'à 0,727 pour un voisin (234:45-47 ;
      0,625 aux 217:43-44 — des formules de vœux presque identiques d'un séif à
      l'autre), au-dessus du 0,636 d'un séif aligné, et jusqu'à 0,5 pour un séif
      distant de trois ou plus (234:45/48 ; 30 330 paires). Aucun seuil
      fixe ne sépare ces dernières populations, et les deux autres mesures
      essayées non plus (5-grammes de consonnes, la garde du premier tour : 0,255
      au 228:8 aligné ; ratio de caractères : 0,597 au 228:8, 0,787 entre deux
      voisins du 217). D'où une règle à deux conditions : ressemblance au séif de
      même numéro ≥ SEUIL_ALIGNEMENT = 0,5, ET strictement plus grande qu'à TOUT
      autre séif du siman dans l'édition par défaut. Une première version de ce
      tour ne regardait que i±1 et i±2 ; mais un séif distant de trois ou plus
      atteint 0,5, le seuil même (234:45/48) : la condition porte sur tout le
      siman, pour moins de 2 s de plus sur les 148. Le témoin construit pour ce cas
      (plus bas, 234:48) est écarté par les deux versions — son voisin 47 battait
      déjà le séif 48 — : l'extension ferme un cas limite mesuré, qu'aucun témoin
      n'a encore montré. Marge la plus faible mesurée :
      0,264 (217:44). Résultat : 1 452 séifs alignés sur 1 452 ; un séif écarté
      est imprimé, avec le séif qui lui ressemble davantage.
  R3. UNE AUTRE ÉDITION EXPLIQUE UNE LEÇON, JAMAIS UNE OMISSION. Un mot changé, un
      ktiv, une abréviation développée ou contractée, un mot censuré (« גוי »
      pour « עובד כוכבים »), un ajout que porte Torat Emet 357 : excusés, si le
      séif ENTIER de la page est cette leçon. Mais un passage que porte l'édition
      PAR DÉFAUT et qui manque à la page — suite de mots, glose du Rama,
      parenthèse de source, note entre crochets — reste SIGNALÉ, même si Torat
      Emet 357 l'omet aussi, avec la mention « absent aussi de Torat Emet 357 ».
      Le chapeau n'est jamais un écart.
      L'omission se lit par un alignement MOT À MOT. La mécanique vient de
      `verify-chabbat-source.py` (`mots`, `_remplacement`, `omissions`,
      `_couvert`, `_egal`) : une SUPPRESSION de difflib est une omission ; un
      REMPLACEMENT est une leçon, sauf pour les mots qu'un alignement fin y laisse
      sans contrepartie ; un mot sans contrepartie n'est retenu que si aucun mot
      non apparié de l'autre texte, tout près, n'en est la forme déplacée,
      développée (« ב״י » / « בית יוסף »), contractée, scindée ou à une lettre
      près. Le piège de l'abréviation est tenu : « בי״ד » face à « ביורה דעה »
      n'est pas une omission.
      Le tour 2 l'avait reprise « telle quelle » ; son arbitre a fait certifier,
      code 0, deux pages qui recopiaient Torat Emet 357 là où celle-ci PERD un
      passage de l'édition par défaut : au 141:1 la parenthèse de source
      « (לשון המחבר) » (vérifiée sur l'api/v3 en direct), au 201:50 l'attribution
      « ור״ש » de « (טור בשם י״א ור״ש וב״י בשם המרדכי) ». Deux défauts du code
      COMMUN — verify-chabbat-source.py les porte encore : sa fonction
      `omissions` rend [] sur ces deux passages —, corrigés ici :
        a. une substitution coûtait 0,5 et une omission 1 : face à « אלא אם כן »,
           trois LEÇONS (1,5) battaient « אא״כ » développé plus deux mots omis (2),
           et « (לשון המחבר) » disparaissait sans un mot. L'alignement est
           désormais LEXICOGRAPHIQUE : d'abord le plus grand nombre de mots
           APPARIÉS, ensuite le moindre coût (`_remplacement`) ;
        b. l'abréviation se lisait par simple sous-suite : « בשי״א » (בשא)
           absorbait « בשם י״א ור״ש » (בשםארש). Désormais CHAQUE MOT y a sa part,
           un groupe de lettres qui commence par sa première lettre (`_abrege`) :
           « בשי״א » note « בשם י״א », et « ור״ש » reste sans contrepartie.
      Trois autres écarts au code commun :
        c. les ancres de commentateurs que Sefaria pose DANS le texte
           (<i data-commentator…></i>) sont ôtées avant le découpage en mots ;
        d. un remplacement où un mot est SUBSTITUÉ et où DEUX mots ou plus restent
           sans contrepartie est une omission (Chabbat le lit comme une leçon
           entière). Au 158:2, Torat Emet 357 écrit « מצוה להרגם » là où Ashlei
           Ravrevei écrit « היו נוהגין בזמן הבית להרגם » : la page qui la
           recopierait perdrait « au temps du Temple », et le code de Chabbat
           taisait ce passage ; au 156:3 (« הכהנים » pour « כהני עבודת כוכבים ») et
           au 158:1 (« גלולים » pour « עבודת כוכבים מז׳ עממין »), il certifiait la
           page. Le passage cité est tout ce que le remplacement n'APPARIE pas,
           substitués compris (le tour 2 y mettait aussi les mots appariés : au
           113:13 d'une page, « מותרין » était donné pour absent à côté de son
           « מתרים ») ;
        e. un passage sans contrepartie à sa place, mais qui se lit D'UN SEUL
           TENANT ailleurs dans le séif de l'autre texte (`_deplace` : appariement
           strict, jamais « à une lettre près » ; deux mots au moins de l'autre
           texte ; MIN_DEPLACE = 4 consonnes de squelette au moins) est DÉPLACÉ, non
           omis : le texte le porte. Le tour 2 le comptait pour omission au-delà
           de la fenêtre de `_couvert`, et la porte écrivait « absent aussi de
           Torat Emet 357 » quand Torat Emet 357 le porte : au 94:5 « (ארוך כלל
           ל״ז) » (Torat Emet 357 l'a plus haut dans le séif ; l'arbitre du tour 2
           l'a relevé), au 190:34 « (ב״י » (« (בית יוסף) » en fin de séif), au
           157:1 « בשם רש״י » (Torat Emet 357 décale ses trois parenthèses d'une
           proposition). Lus mot à mot, ces trois séifs de Torat Emet 357 portent
           TOUS les mots de l'édition par défaut : une page qui les recopie passe,
           séif imprimé avec son édition (R4). Un mot SEUL retrouvé ailleurs
           reste une omission.
      La mention se lit MOT PAR MOT (`statuts`) : « Torat Emet 357 le porte »,
      « absent aussi de Torat Emet 357 », « … le porte ailleurs dans le séif
      (déplacé) », « … y a une autre leçon », ou le décompte s'ils diffèrent. Le
      tour 2 n'avait que « le porte » et « absent » : une page sans « (לשון
      המחבר) » au 141:1 lisait « Torat Emet 357 le porte », ce qui était faux.
      Mesure du 8 octobre 2026, Ashlei Ravrevei → Torat Emet 357, 1 452 séifs,
      tour 2 → tour 3 : séifs de Torat Emet 357 qui perdent au moins un passage
      de l'édition par défaut 62 → 61 ; passages 72 → 71, dont 31 → 30 portant une
      parenthèse ou un crochet et 14 → 13 de trois mots ou plus. Exactement cinq
      mouvements : +141:1 « (לשון המחבר) » (a), +201:50 « ור״ש » (b) ; −94:5,
      −157:1, −190:34, reconnus déplacés (e). Rien d'autre ne bouge sur Torat Emet
      357 : les 65 remplacements où une substitution laisse un seul mot sans
      contrepartie sont les MÊMES aux deux tours (le tour 2 en annonçait 64), et
      ce sont tous des leçons — la censure (« עובד כוכבים » / « גוי » et ses
      formes, « עבודת כוכבים » / « ע״ז » ou « אלילים », « צורת חמה » / « צלם »,
      « עבד כנעני » / « כותי ») et des contractions (« שהיו מלקין » / « שמלקין »,
      « ארבעה ועשרים » / « כ״ד »). Restent : les cinq notes de censeur entre
      crochets (228:8, 228:25, 228:35, 230:1, 232:12), des parenthèses de sources
      (141:1, 176:2 « (לשון רמב״ם פ״ח מה״מ די״א) », 217:11 « (רמב״ם פ״ט מה״נ
      ד״ח) », 187:1, 234:59), 98:8 « עיין ס״ק כ״ז », les trois remplacements de
      (d), et des passages d'un ou deux mots (« לו », « או », « (טור) », « ור״ש »,
      « בזמן הסנהדרין » aux 205:2 et 220:23…). Une page qui recopie Torat Emet 357
      à l'un de ces 61 séifs sort en 1, « absent aussi de Torat Emet 357 ». Au
      228:8, la leçon de Torat Emet 357 est celle du livre sans la note de
      censeur : une page qui la recopierait est signalée (le premier tour
      l'écartait par sa longueur, ×0,43 ; celle-ci l'admet comme alignée et NOMME
      le passage perdu). Aucune page ne le fait : les trois langues du 228
      recopient Ashlei Ravrevei.
      Contrôle indépendant — le détecteur de l'arbitre du tour 2, rejoué tel
      quel : suppressions de consonnes (deux au moins, au squelette) entre Ashlei
      Ravrevei et Torat Emet 357 que la porte ne signale pas. 41 séifs au tour 2
      (le compte de l'arbitre, reproduit), 41 au tour 3 : 141:1 et 201:50 en
      sortent, désormais signalés ; 94:5 et 157:1 y entrent, la suppression y est
      réelle à sa place et le passage se lit ailleurs dans le séif (e) ; les 39
      autres, communs aux deux tours, sont ceux que l'arbitre a lus un à un —
      contractions, développements, déplacements, censure.
      Tour 4, deux ajouts à R3 (détail et mesure plus bas, « TOUR 4 ») :
        f. la DITTOGRAPHIE est une omission, non une leçon (`_dittographie`) :
           l'esprit de R3 l'emporte sur sa lettre. Au 234:37, Torat Emet 357 écrit
           « מחול לך, או שרוי לך, או שרוי לך » pour « מחול ליך או מותר ליך או שרוי
           ליך » : « מותר ליך » disparaissait derrière une répétition, et une page qui
           la recopiait sortait IDENTIQUE, code 0. Le mot ainsi perdu est « répété »
           (`statuts`), compté avec les omissions, et la mention dit « DITTOGRAPHIE ».
           Tour 5 : la copie d'un voisin est cherchée aussi derrière un mot apparié
           « à une lettre près » (217:44, « בכהנים » pour « מכהנים »), à un mot
           d'écart (« X או X ») et, quand la lettre changée est l'initiale, jusqu'à
           six mots (ASSIMILATION, 173:16) — voir « TOUR 5 » ;
        g. les LEÇONS D'ATTRIBUTION sont NOMMÉES (`attributions`) : au 157:1 et au
           94:5 Torat Emet 357 rattache une parenthèse de source à une autre
           proposition, au 185:3 elle en réordonne les noms. Aucun mot n'est perdu ;
           R3 les excuse, le verdict reste 0 — décision de ce tour —, mais toute page
           qui recopie ces séifs lit « source attribuée autrement (Torat Emet 357) ».
  R4. Chaque séif retenu hors de l'édition par défaut est imprimé avec son
      édition, et chaque édition servie mais ignorée est nommée.
Une page qui prend un séif dans une édition de référence et le suivant dans
l'autre passe (R3 sauf) ; une page qui mêle les deux À L'INTÉRIEUR d'un séif ne
passe pas. Quand aucune ne convient, l'écart est rapporté à l'édition LA PLUS
PROCHE de ce séif, et les mots de l'édition par défaut qui n'ont pas de
contrepartie dans la page sont listés (R3), avec la mention de Torat Emet 357.

Localiser un écart (page divergente) : le parcours suit les séifs AU SQUELETTE
(un écart de ktiv en tête de séif ne doit pas empêcher de le reconnaître), puis
chaque séif reconnu est rejugé AUX CONSONNES : « RETENU » s'il est exactement une
leçon admise ; s'il ne s'en écarte que par des yod/vav, la GARDE KTIV (tour 4)
le dit « KTIV » quand ils sont seulement AJOUTÉS ou ôtés à l'intérieur des mots,
« MOT CHANGÉ » quand un yod/vav est ÉCHANGÉ (« כוס » / « כיס ») ou touche
l'initiale ou la finale (« ואם » / « אם ») — refusés l'un et l'autre (cette porte
exige les consonnes), CHAQUE MOT EN CAUSE IMPRIMÉ, avec l'autre édition qui
l'écrit ainsi s'il y en a une (deux éditions mêlées dans le séif) ; le chapeau
reconnu au squelette y passe aussi ; « OMISSION » s'il est la leçon de Torat Emet 357
et que celle-ci perd un passage de l'édition par défaut. Un séif n'est retenu
que si le suivant commence juste après lui (une leçon plus courte peut n'être
qu'un PRÉFIXE de la page). Un chapeau récrit est rapporté à part. Les séifs
« NON RETROUVÉ » sont ceux dont le début ne se lit nulle part : absents, fondus,
ou altérés dès leurs premiers mots.

CE QUE LA MESURE A DONNÉ (8 octobre 2026, sur un instantané FIGÉ des pages —
`git archive` de HEAD 7d4504d6 —, cache Sefaria du 8 octobre, contenu identique
au retéléchargement à froid du tour 3, 147 fichiers ; trois versions de la porte
lancées côte à côte : celle de HEAD, le tour 2, celle-ci) :
  · 148 simanim, 1 452 séifim, 444 pages. Verdicts IDENTIQUES siman par siman avec
    les trois versions : 115 conformes — chaque séif, trois langues, est celui
    d'Ashlei Ravrevei (3 702 séifs × page, 0 hors d'elle) —, 1 page-passerelle
    (169, lacune de Sefaria) et 32 divergents, 87-118, les trois langues. Le
    constat de CLAUDE.md (« les 50 simanim antérieurs échouent tous : leur niveau
    1 développe les abréviations… ») TIENT pour ces 32 et n'est PAS un artefact
    d'édition : ils divergent des deux éditions de référence, même mêlées séif
    par séif. (Les « 50 » étaient, au commit a5be5448, 87-118 et 183-200 ; les
    183-200 ont été refaits depuis et passent.)
  · Séif par séif dans les pages divergentes (× page), identique au tour 2 :
    fidèles à l'édition par défaut 27 ; fidèles à Torat Emet 357 seulement,
    leçon excusée, 18 (91:8, 94:4, 95:1, 95:4, 113:14, 114:3 — aucun ne perd de
    passage) ; OMISSION (R3) 3 (94:9, la page est Torat Emet 357 au ktiv près,
    sans « (ד״ע) ») ; au ktiv près 30 ; divergents 306 ; non retrouvés 270 ;
    surplus 12.
  · R3 dans les séifs divergents, tour 2 → tour 3 : passages (× page) d'Ashlei
    Ravrevei sans contrepartie dans la page 948 → 960, dont 510 → 519 de trois
    mots ou plus ; « absents aussi de Torat Emet 357 » 6 → 3 (117:1 « (ל׳
    המחבר) », trois langues ; le 94:5 « (ארוך כלל ל״ז) » est désormais « Torat
    Emet 357 le porte ailleurs dans le séif »). Les mouvements, lus : des
    parenthèses de sources que l'abréviation lâche absorbait ou coupait sont
    rendues entières (96:2 « (הגהת ש״ד והגהת או״ה שם) » au lieu de « או״ה שם) »,
    114:4 « (מרדכי בשם ראבי״ה) », 102:1 « הרא״ש ור׳ ירוחם והגהות ») ; des mots
    appariés ne sont plus cités comme absents (113:13). Ces listes sont un
    relevé : le verdict d'un séif divergent ne dépend pas d'elles.
  · Témoins (pages du siman remplacées, trois langues, réseau COUPÉ ; code de
    sortie HEAD / tour 2 / tour 3) — ceux de l'arbitre du tour 2, rejoués sur ses
    propres pages :
      141:1 ← Torat Emet 357, sans « (לשון המחבר) » ................... 1 / 0 / 1
        (OMISSION, « absent aussi de Torat Emet 357 ») ;
      201:50 ← Torat Emet 357, sans « ור״ש » ........................... 1 / 0 / 1 ;
      141:1 ← Ashlei Ravrevei sans « (לשון המחבר) » ................... 1 / 1 / 1
        (mention « absent aussi de Torat Emet 357 » ; le tour 2 écrivait
        « Torat Emet 357 le porte ») ;
      176 entier ← Torat Emet 357 ; 176:2 réduit à « (רמב״ם) » ; 139:2 ← Ashlei
        Ravrevei 138:2 ; Torat Emet 357 aux 217:11, 205:2, 119:18, 202:4, 228:14,
        156:3, 201:24, 176:2 ........................................ 1 / 1 / 1 ;
      124:4 ← Torat Emet 357, censuré ; 119:10 ← Torat Emet 357 ......... 1 / 0 / 0 ;
    ceux de l'arbitre du premier tour, rejoués sur ses pages : 190:35 ← Freeware,
    sans « הגה וכן עיקר » 1 / 1 / 1 ; 119:10 ← Torat Emet 357 1 / 0 / 0 ; 139:2 ←
    Freeware ; 123:1 ← Wikisource, sans la glose du Rama ; 119:10 mêlant deux
    éditions ; 119:10 omis : 1 / 1 / 1 ; ceux du tour 2, reconstruits sur
    l'instantané : Torat Emet 357 aux 228:8, 158:2, 176:2, 156:3 1 / 1 / 1, aux
    119:10 et 124:4 1 / 0 / 0 ; cache saboté, le 217:43 de Torat Emet 357 porte le
    texte de son 217:44 (R2) 1 / 1 / 1 ; le 234:48 porte celui du 234:45 1 / 1 / 1 ;
    et ceux de ce tour :
      157:1 ← Torat Emet 357 (« בשם רש״י » déplacé) .................... 1 / 1 / 0
        (séif imprimé « 1=Torat Emet 357 » ; le tour 2 accusait « absent aussi
        de Torat Emet 357 », ce qui était faux) ;
      190:34 ← Torat Emet 357 (« (ב״י » déplacé en fin de séif) .......... 1 / 1 / 0 ;
      201:50 ← Ashlei Ravrevei sans « ור״ש » ............................ 1 / 1 / 1
        (« absent aussi de Torat Emet 357 »).
  · Réseau saboté (cache vide, réponses RÉELLES d'api/v3 et d'api/texts du 8
    octobre, un seul côté saboté ; page : le 176 entier recopié de Torat Emet
    357, qui perd la parenthèse du 176:2 — tour 2 / tour 3) :
      api/v3 sans la version Ashlei Ravrevei ..... 0, Torat Emet 357 gravée en
        cache comme édition par défaut / 3, rien en cache (« annonce et ne sert
        pas : Ashlei Ravrevei ») ;
      la même, retirée AUSSI d'available_versions . 0, gravée / 3, rien en cache
        (« api/texts sert par défaut Ashlei Ravrevei, les priorités d'api/v3
        désignent Torat Emet 357 ») ;
      Torat Emet 357 à la priorité 3 ............. 0, gravée / 3, rien en cache ;
      api/v3 sans available_versions ............. 1, en cache / 3, rien en cache ;
      Ashlei Ravrevei tronquée à un séif ; api/texts sans heVersionTitle, au texte
        vide ou amputé d'un séif, au ref du livre entier, en erreur HTTP 200 ou
        500, ou coupée ............................... 1, en cache / 3, rien ;
      connexion coupée ; édition par défaut vide ; sans priorités .. 3 / 3, rien ;
      réponses réelles ........................ 1 / 1, cache de forme 1 / 2.
    Cache empoisonné d'avance (forme 1 sans Ashlei Ravrevei ; forme 2 sans
    Ashlei Ravrevei, ou Torat Emet 357 à la priorité 3, ou sans preuve de
    recoupement) : relu sur Sefaria, verdict juste (1), fichier réécrit ; réseau
    coupé : 3, sans que le fichier empoisonné soit lu.
  · Pages absentes : siman sans aucune page (dossier absent ou vide) : NON
    CONFRONTÉ et code 3, sans aller sur Sefaria ; une seule langue absente : 1,
    FICHIER ABSENT.

TOUR 4 (9 octobre 2026) — cinq corrections demandées par l'arbitre du tour 3 et
par la règle commune aux trois portes (garde ktiv), mesurées sur un instantané FIGÉ
(`git archive` de HEAD 56151b14, sources/ et scripts/), cache RETÉLÉCHARGÉ le 9
octobre en forme 3 — contenu identique, fichier par fichier, au cache du 8 octobre
(147 fichiers, 0 différence d'édition, de priorité, de texte ou de recoupement) —,
la porte de HEAD lancée à côté sur son propre cache de forme 2.
  1. LA GARDE KTIV (`nature_ktiv`, `garde_ktiv`, `garde_seif`). Voir plus haut
     « Localiser un écart ». COÛT MESURÉ sur les 444 pages réelles : aucun verdict
     ne change, par construction — un séif qui ne passe que le squelette était déjà
     refusé — ; les lignes --bref des 148 simanim sont identiques à l'octet. Les 30
     séifs (× page) « KTIV » restent KTIV, 0 devient MOT CHANGÉ : leurs 63 mots sont
     tous du ktiv intérieur (« אסור » / « איסור », « לאכל » / « לאכול », « טיפה » /
     « טפה »…), et la porte dit désormais pour chacun l'édition qui l'écrit ainsi —
     ces dix séifs mêlent Ashlei Ravrevei et Torat Emet 357 à l'intérieur du séif,
     ce que l'étiquette « aux seules matres lectionis près » taisait. Relevé neuf,
     sans effet sur le verdict : dans les séifs DIVERGENTS des 32 simanim 87-118,
     147 mots (× page, 75 séifs × page) appariés à l'édition la plus proche ont un
     yod/vav changé — 132 en tête ou en fin de mot (« כל » / « כלי », « עובד » /
     « עובדי », « אם » / « ואם »…), 12 échanges (« אסור » / « אוסר », « שהיא » /
     « שהוא », « יכול » / « יוכל », « ביתו » / « ובית », trois langues), 3 au-delà de
     la liste de huit ; aucun n'était imprimé. CORRIGÉ au tour 5 (son arbitre) : deux
     de ces quatre couples ne sont PAS des variantes — 87:6 « אסור » / « אוסר » et 112:1
     « ביתו » / « ובית » sont des appariements de difflib entre deux phrases sans
     rapport ; la liste sépare désormais les mots ANCRÉS des appariements ISOLÉS. Entre les deux éditions de
     référence, 8 017 mots ne diffèrent qu'au squelette près : 7 808 ktiv intérieur,
     75 mots de deux lettres (« רוב » / « רב » 32 fois, « ליה » / « לה » 27), 96 en
     tête ou en fin de mot (« עובד » / « עובדי » 32), 38 échanges (« הוא » / « היא »
     et « שהוא » / « שהיא » 9, « אסור » / « אוסר » 3, « לו » / « לי », « כמו » /
     « כמי »…). Une page qui en prendrait UN dans un séif de l'autre édition sortait
     déjà en 1 ; elle lit désormais « KTIV » pour 7 883 de ces mots, « MOT CHANGÉ »
     pour 134 — que Torat Emet 357 porte, et qu'une page recopiant son séif ENTIER
     garde, séif imprimé avec son édition (R4).
  2. DITTOGRAPHIE (R3 f). La règle demandée — un mot substitué qui répète un mot
     voisin, le mot remplacé n'existant nulle part ailleurs — prend 47 des 516
     substitutions un-pour-un de Torat Emet 357, dans 34 séifs ; lues, toutes sauf
     234:37 sont la censure (« אלילים » / « עבודת כוכבים », le mot « כוכבים »
     revenant dans « של עובד כוכבים ») ou des leçons (« בלי » / « בלא », « הנאד » /
     « הנוד »). La répétition CONTIGUË, la copie présente dans l'édition par défaut,
     l'édition par défaut sans répétition au même endroit, le mot remplacé absent :
     un seul séif, 234:37. R3 : 61 → 62 séifs, 71 → 72 passages de Torat Emet 357.
     MESURE INCOMPLÈTE, corrigée au tour 5 : elle ne portait que sur les
     SUBSTITUTIONS ; les 287 mots appariés « à une lettre près » n'avaient pas été
     examinés, et 217:44 y était (« une seule substitution retenue » restait vrai ;
     « un seul séif » ne l'était pas).
     Aucune page réelle n'en dépend (les trois pages du 234 recopient Ashlei
     Ravrevei). CONTRÔLE EXHAUSTIF, en mémoire : pour chacun des 1 381 séifs où
     Torat Emet 357 diffère d'Ashlei Ravrevei, une page = Ashlei Ravrevei avec CE
     SEUL séif pris dans Torat Emet 357, jugée par `juger` : DIVERGENCE 61 → 62
     (234:37 en plus), IDENTIQUE 1 320 → 1 319, chaque verdict égal à
     `Ref.lacunaire` ; l'attribution est nommée sur 94:5, 157:1, 185:3, et nulle
     part ailleurs.
  3. R1 épinglée : « Torat Emet 357 » au lieu de `^Torat Emet \d+$`. Sans effet sur
     les pages réelles (Sefaria ne sert pas d'autre Torat Emet numérotée en Yoré
     Déa) ; témoin P1 ci-dessous.
  4. LEÇONS D'ATTRIBUTION (R3 g) : 5 parenthèses dans 3 séifs de Torat Emet 357 —
     94:5 « (ארוך כלל ל״ז) » (14 mots franchis), 157:1 « (משנה פ׳ ח׳ דתרומות…) »
     (8), « (ב״י בשם רש״י ור״ן) » (15), « (רמב״ם פ׳ הנזכר) » (19), 185:3 « (ר״ן
     בשם הרמב״ן ורבינו ירוחם) » (noms réordonnés). Le poids d'une parenthèse dans
     l'alignement (POIDS_PARENTHESE = 1,5 mot) a été éprouvé : de 1,5 à 2,5, la
     même liste ; à 0,9, deux de plus — 160:14 (« (טור סי׳ קס״ט) » de part et
     d'autre du seul « לו ») et un artefact au 228:12 (difflib appariait le
     « שכיח » de la glose au « שכיח » de la phrase suivante). Trois essais l'ont
     précédée : ancrage aux mots voisins (9 parenthèses, dont une glose sans source
     écrite hors parenthèses par Torat Emet 357), symboles alignés par difflib avec
     une réponse « à une lettre près » (24 — « (וכן נוהגין) » répondait à « ור״ן) »,
     « (ב״י) » à une parenthèse de six mots), puis réponse stricte (7 : les deux
     ci-dessus en plus).
     Aucune page réelle n'en dépend (0 séif × page retenu dans Torat Emet 357 avec
     une attribution).
  5. ÂGE DU CACHE (`lire_cache`, `dire_cache`) : forme 3, date imprimée, et
     au-delà de 30 jours un AVERTISSEMENT en tête et en pied, sans code.
  Coût en temps : --tous, cache plein, ≈ 8 s → ≈ 15 s (l'alignement pondéré des
  parenthèses et la garde ktiv).
  · Témoins (pages du siman remplacées, trois langues, réseau COUPÉ ; code HEAD /
    tour 4) :
      K1 123:18 « כוס » → « כיס » et 123:5 « מים » → « מום » (analogue du N4b de
         l'arbitre d'Orah Haïm) ....... 1 / 1 ; HEAD : « KTIV — égal … aux seules
         matres lectionis près » et les premiers mots du séif, le mot changé jamais
         désigné ; tour 4 : « MOT CHANGÉ : « כיס » pour « כוס » (échange) » ;
      K2 122:9 « יום » → « ים » (analogue du N4a) .. 1 / 1, KTIV, « (mot de deux
         lettres) » listé ;
      K3 119:1 « הוא » → « היא » ; K4 120:2 « ואם » → « אם » .... 1 / 1, MOT CHANGÉ ;
      K5b 119:2 « מותר » → « מתר » ... 1 / 1, KTIV, « c'est la graphie de Torat Emet
         357 : deux éditions mêlées dans le séif » ; K5a, le même au 122:1, où le
         séif entier devient alors Torat Emet 357 ... 0 / 0 (leçon, R4) ;
      K6 122:2 « לכתחלה » → « לכתחילה » ... 1 / 1, KTIV ; K7 contrôle 123 ... 0 / 0 ;
      K8 145, chapeau repris avec « אלילים » → « אלולים » ... 1 / 1 — HEAD sortait
         DIVERGENCE avec « 9 séif(s) fidèle(s) » et pas une ligne pour dire où ; le
         tour 4 : « chapeau : MOT CHANGÉ » ; K9 chapeau intact ... 0 / 0 ;
      D1 234:37 ← Torat Emet 357 ......... 0 / 1 (« absent aussi de Torat Emet 357,
         … DITTOGRAPHIE ») ; D2 la même dittographie dans Ashlei Ravrevei ... 1 / 1 ;
         D3 contrôle 201:19 ← Torat Emet 357 (« לזו … ולזו ») ... 0 / 0 ;
      A 157:1, 185:3, 94:5 ← Torat Emet 357 .. 0 / 0, « source attribuée
         autrement » ; contrôles 160:14 et 190:34 ← Torat Emet 357 ... 0 / 0, sans
         mention ;
      P1 cache forgé où la Torat Emet s'appelle « 358 », 119:10 ← elle .... 0 / 1 ;
      C1 cache du 145 daté de 45 jours ... 0, avertissement en tête et en pied (C7 :
         aussi sous --bref) ; C6 29 jours ... 0, sans ; C2 sans date, C3 daté du
         futur, C4 de forme 2, C5 --rafraichir : relus sur Sefaria, réseau coupé ... 3.
    Ceux de l'arbitre du tour 3 (ARB-YD-T3/W, 37 témoins, leurs pages, ce cache) :
    tous au code attendu, te-234-37 compris (0 → 1) ; te-157-1 et te-185-3 restent
    à 0 et nomment l'attribution. Ses douze sabotages réseau (connexion coupée,
    Ashlei Ravrevei vide ou retirée, Torat Emet 357 en priorité 3, erreur HTTP 200,
    ref du livre entier sur l'une ou l'autre API, api/texts sans heVersionTitle,
    Ashlei Ravrevei amputée sur api/v3, lacune du 169 démentie) : 3, rien en cache ;
    réponses réelles : cache de forme 3, daté.

TOUR 5 (9 octobre 2026) — l'arbitre du tour 4 a bloqué sur un point et en a relevé
deux autres. Mesures sur un instantané FIGÉ (`git archive` de HEAD 7991a335, sources/
et scripts/ — pages de Yoré Déa identiques à 56151b14), cache du 9 octobre (forme 3,
147 fichiers), la porte du tour 4 lancée à côté sur le même cache.
  1. BLOQUANT — DITTOGRAPHIE À UNE LETTRE PRÈS. Au 217:44, Torat Emet 357 écrit
     « אסור בכהנים ולויים. בכהנים ולויים, מתר בישראל » pour « אסור בכהנים ולוים
     מכהנים ולוים מותר בישראל » : « מכהנים » disparaît derrière la répétition, et une
     page qui recopiait ce séif sortait IDENTIQUE, code 0, trois langues (témoin X1
     de l'arbitre). Cause : `_egal` apparie « מכהנים » et « בכהנים » à une lettre près ;
     le mot n'était ni substitué ni omis, et `_dittographie` n'était pas consultée.
     Correctif : `_remplacement(une_lettre=…)` rend ces couples, et `statuts` les lui
     soumet. Sur les 287 couples à une lettre près de Torat Emet 357, la forme
     contiguë en prend UN : 217:44 — le compte de l'arbitre (233 couples, par son
     propre alignement) trouve le même. `_couvert`, qui déclare porté un mot sans
     contrepartie à sa place quand un mot NON apparié tout près en diffère d'une
     lettre, a été examiné aussi : un seul cas sur Torat Emet 357 (157:1, « ור״ן) »
     couvert par « כן »), et ce n'est pas une copie — « ור״ן » est dans la
     parenthèse que Torat Emet 357 déplace.
  2. ASSIMILATION (173:16), que l'arbitre laissait « à trancher, ou au moins à
     déclarer » : tranchée ici, dans le sens STRICT, par une règle étroite. Torat
     Emet 357 écrit « מצוים בפרות. הגה: ויש מתירין בפרות » pour « מצויים כפירות: הגה
     ויש מתירין בפירות » — « aussi courants que les fruits » devient « courants dans
     les fruits », par assimilation au « בפרות » de la glose, quatre mots plus loin.
     La copie n'est pas contiguë : la règle du tour 4 ne pouvait pas la voir. Règle
     retenue (`_initiale_changee`, FENETRE_ASSIMILATION = 6) : un mot apparié à une
     lettre près dont la lettre changée est l'INITIALE — la préposition — et qui a
     les consonnes exactes d'un mot de B à six mots au plus, dont le modèle se lit
     dans A à sa place, le mot de A étant absent de B. Coût : 35 des 287 couples
     changent l'initiale ; la règle en prend un, 173:16. Sans la condition sur
     l'initiale elle prendrait aussi 112:15, 114:10, 138:8 et 215:1 — des
     désinences (« נותנין » / « נותנים »), des leçons.
  3. COPIE À UN MOT D'ÉCART (« לאשתו או לאשתו » pour « לאשתו או לבתו », témoin ND2
     de l'arbitre, que le tour 4 déclarait comme limite) : admise pour tout mot
     (PORTEE_COPIE = 2), substitué ou apparié à une lettre près. Coût sur Torat Emet
     357 : 0 — aucune substitution, aucun couple de plus.
     Effet des trois : R3, séifs de Torat Emet 357 qui perdent un passage de
     l'édition par défaut, 62 → 64 (173:16, 217:44), passages 72 → 74. CONTRÔLE
     EXHAUSTIF en mémoire (une page = Ashlei Ravrevei avec UN séif pris dans Torat
     Emet 357, 1 381 séifs, `juger`) : DIVERGENCE 62 → 64, exactement 173:16 et
     217:44 en plus, IDENTIQUE 1 319 → 1 317, chaque verdict égal à
     `Ref.lacunaire`. Pages réelles : les 148 lignes --bref sont identiques à
     l'octet ; 115 conformes / 1 passerelle / 32 divergents ; pages 345 IDENTIQUE,
     96 DIVERGENCE, 3 PASSERELLE ; le relevé des séifs divergents (960 passages,
     519 de trois mots ou plus) est inchangé ligne à ligne.
  4. LA LISTE « yod/vav changé » DES SÉIFS DIVERGENTS donnait pour des variantes
     des appariements de difflib entre phrases sans rapport (arbitre : 87:6
     « אסור » / « אוסר », 112:1 « ביתו » / « ובית »). Les 49 couples distincts (147
     mots × page) ont été lus un à un, contexte de la page et de l'édition sous les
     yeux : 5 sont sans rapport (87:6 trois fois, 101:1, 112:1), 44 sont de vrais
     changements. Les 5 sont tous dans un bloc égal de difflib d'un ou deux mots ;
     aucun mot d'un bloc de trois ou plus n'en est un — mais 14 vrais changements
     sont aussi isolés (« וכיוצא בה » / « כיוצא בה » au 103:1, « כל » / « כלו » au
     106:1, mots réordonnés au 108:1). Règle : ANCRAGE_MIN = 3 — un mot n'est donné
     pour une variante que dans un passage commun de trois mots ; isolé, il est
     listé à part, « À CONTRÔLER », avec la ressemblance du séif. Résultat : 90 mots
     ancrés (51 séifs × page), 57 isolés (33 séifs × page) ; les échanges ancrés
     sont 90:3 « שהיא » / « שהוא » et 104:1 « יכול » / « יוכל ». Un seuil de
     RESSEMBLANCE du séif, essayé d'abord (0,5, celui de R2), ne sépare pas : un séif
     de la page fondu avec les suivants ressemble peu à son séif (113:5, 0,30 ;
     111:1, 0,31 ; 112:14, 0,28) et porte des variantes réelles ancrées dans neuf à
     seize mots communs ; il en aurait caché sept séifs (× 3 langues) pour trois.
  Coût en temps : --tous, cache plein, ≈ 15 s, comme le tour 4.
  · Témoins (réseau COUPÉ ; code tour 4 / tour 5) :
      E1 217:44 ← Torat Emet 357 (le X1 de l'arbitre) ................. 0 / 1
         (« absent aussi de Torat Emet 357, qui écrit à sa place une suite
         voisine deux fois (DITTOGRAPHIE : « בכהנים ולויים. בכהנים ולויים, ») ») ;
      E2 173:16 ← Torat Emet 357 (le X2) ............................... 0 / 1
         (« … un mot voisin recopié (ASSIMILATION : « בפרות. » copie « בפרות, »,
         4 mots plus loin) ») ;
      E3 217:44 d'Ashlei Ravrevei avec « בכהנים » ; E4 173:16 d'Ashlei Ravrevei avec
         « בפירות » ........ 1 / 1, la mention nomme désormais la copie ;
      E5 contrôles ← Torat Emet 357 : 215:1, 138:8, 114:10, 112:15 (désinences
         assimilées à distance), 125:9 (« הנוד » pour « הנאד ») ......... 0 / 0 ;
      E6 234:37 d'Ashlei Ravrevei avec « לאשתו או לאשתו » .............. 1 / 1 ;
      E7 pages réelles 87, 90, 112 ...... 1 / 1, 87:6 et 112:1 « ISOLÉS — À
         CONTRÔLER », 90:3 ancré.
    Ceux de l'arbitre du tour 4 (ARB-YD-T4/W, 13, leur cache) : tous au code
    attendu, X1, X2 et ND2 passant de 0 à 1 ; NC1-NC3 (date illisible, sans
    fuseau, sans recoupement) 3 ; NC4 (30,5 jours) 0 avec l'avertissement ; NC5
    (Torat Emet 357 vide en cache) 0. Ceux de l'arbitre du tour 3 (37), du tour 1
    (6) et du tour 4 (26 ; le K5 d'origine doublait K5a) : tous au code attendu. Ses seize sabotages réseau
    (ARB-YD-T4/tools/sab4.py) : mêmes codes, rien en cache sur un 3.

Pièges tenus :
  · Sefaria rend HTTP 200 et le LIVRE ENTIER sur un ref mal formé : le `ref` servi
    doit finir par le numéro demandé — sur api/v3 comme sur api/texts —, sinon
    NON ATTEINT, avec sa raison ;
  · un siman que Sefaria n'a pas (169) : `api/v3` répond 404 « We have no text »,
    `api/texts` répond le BON ref et un texte vide. Les deux doivent le dire pour
    que la lacune soit admise ; sinon NON ATTEINT. La page doit alors ne citer
    aucun séif (page-passerelle). Une réponse où d'AUTRES éditions ont du texte
    mais pas l'édition par défaut n'est pas une lacune : NON ATTEINT. La lacune
    n'est jamais mise en cache : réseau coupé, le 169 est NON ATTEINT ;
  · l'édition par défaut est RECOUPÉE (`_recouper`) avant toute écriture en
    cache : api/v3 doit servir chaque édition hébraïque qu'il annonce, et api/texts
    doit servir par défaut la même édition, aux mêmes consonnes. Mesuré à froid le
    8 octobre : 147 simanim sur 147 recoupés (Ashlei Ravrevei partout ; éditions
    annoncées : Ashlei Ravrevei et Torat Emet 357 partout, plus Freeware 113 fois
    et Wikisource 51 fois, toutes servies) ;
  · le cache (`scripts/.cache-sefaria/yd-editions/`) ne persiste JAMAIS un
    résultat dont l'édition par défaut est vide, indécidable ou non recoupée, et
    porte sa FORME : 3 depuis le tour 4, qui garde la preuve du recoupement
    (`recoupement`, forme 2) et la DATE du téléchargement (`telecharge`, UTC) ; un
    fichier d'une autre forme, sans date ou daté du futur, ou dont la preuve ne
    s'accorde pas à son contenu, est relu sur Sefaria (`lire_cache`). Il garde
    toutes les éditions servies, ignorées comprises, pour pouvoir les nommer ;
    la porte imprime de quand date le texte confronté, en tête, en pied et par
    siman, et avertit au-delà de AGE_MAX_JOURS ;
  · ROOT se déduit de `__file__` : une copie lancée hors du dépôt ne trouve aucune
    page — par `--tous` comme par numéro — et sort en 3 sans aller sur Sefaria ;
  · une page ABSENTE n'est pas une divergence quand rien n'a été confronté : un
    siman sans aucune des trois pages est « NON CONFRONTÉ » (code 3) ; une page
    absente à côté d'une page présente est un FICHIER ABSENT (code 1) ;
  · le résumé « Pages par verdict » compte les pages-passerelles et imprime son
    total.
Ce que la porte ne fait pas : un remplacement où un mot est changé et UN seul
autre omis (« A B » pour « C ») est lu comme une leçon — c'est le prix de la
censure deux-pour-un ; un mot SEUL déplacé au-delà de la fenêtre de `_couvert`
est compté pour omission, et un passage n'est reconnu déplacé que d'un seul
tenant (s'il est en partie déplacé et en partie omis, il est omis tout entier) ;
dans un séif DIVERGENT, la liste des mots absents a les mêmes limites, et un
séif remplacé en entier sort avec la liste de tout le séif ; un chapeau RÉCRIT
reste un écart (seule son ABSENCE est permise) ; le ktiv haser/malé n'est jamais
toléré (pas de verdict ÉQUIVALENT ici, contrairement à Chabbat) : il est rapporté
« KTIV », ou « MOT CHANGÉ », mots listés. L'alignement de R3 garde le squelette pour
clé : un mot dont un yod/vav est échangé y reste APPARIÉ — c'est une leçon, jamais
une omission, et le compter pour leçon ferait passer pour censure deux-pour-un le
mot omis qui le jouxte (voir `statuts`). La garde ktiv n'étiquette donc que ce que la
porte REFUSE déjà ; elle ne change aucun verdict. Une copie de voisin
(`_dittographie`) n'est reconnue que CONTIGUË (de toute longueur), aux mêmes consonnes — une
copie dont le premier mot prend un ו de conjonction (témoin D2) n'en est pas une, ni une copie qui
remplace un mot ayant un homonyme EXACT ailleurs dans le séif (35,9 % des mots : la page sort « leçon
excusée ») —, à UN mot d'écart pour un
mot seul (« X או X »), ou, pour un mot apparié à une lettre près dont l'INITIALE
change, jusqu'à six mots (ASSIMILATION) : une substitution qui recopie un mot plus
loin (la censure « עבודת כוכבים … של עובד כוכבים ») et une désinence assimilée à un
mot distant (215:1 « המצוה » pour « המצות », à cinq mots) restent des leçons. Dans un
séif DIVERGENT, un mot à yod/vav changé n'est donné pour une variante que dans un
passage commun de trois mots (`ANCRAGE_MIN`) ; isolé, il est listé « à contrôler »
— et un vrai changement isolé (« כל » / « כלו » au 106:1) y reste mêlé aux
appariements sans rapport (87:6). Une attribution n'est vue que par des
parenthèses ou des crochets (`attributions`) : une source rattachée autrement SANS
parenthèses ne l'est pas, et
une parenthèse décalée d'un seul mot est tenue pour à sa place. Le recoupement ne
protège que de ce que Sefaria peut SERVIR : un fichier de cache forgé à la main et
cohérent avec lui-même (preuve de recoupement et date comprises) est cru —
`--rafraichir` l'ignore. Et il rend la porte dépendante d'api/texts : api/texts
injoignable ou en désaccord, le siman n'est pas conclu (3), même quand api/v3
répond juste.
"""
import sys, re, json, unicodedata, os, html, difflib
from datetime import datetime, timedelta, timezone
import urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = os.path.join(ROOT, "sources", "yoreh-deah")
LIVRE = "Shulchan_Arukh,_Yoreh_De%27ah"
CACHE = os.path.join(ROOT, "scripts", ".cache-sefaria", "yd-editions")
FORME_CACHE = 3          # à incrémenter dès que la forme d'un fichier de cache change
# 2 (tour 3) : le fichier garde la preuve du RECOUPEMENT (`recoupement`, voir fetch) ;
# un fichier de forme 1, écrit sans recoupement, est relu sur Sefaria.
# 3 (tour 4) : le fichier porte sa DATE de téléchargement (`telecharge`, UTC) ; un
# fichier de forme 2, qui ne la porte pas, est relu sur Sefaria.
AGE_MAX_JOURS = 30       # au-delà, la porte avertit qu'elle compare à un instantané (pas un code)
HE_CONS = re.compile(r'[א-ת]')
CHAPEAU = re.compile(r'^\s*<b>.*?</b>\s*(<br\s*/?>)?', re.S)
LANGS = [("FR", ""), ("HE", "-he"), ("EN", "-en")]
ANCRE = 24               # consonnes (squelette) qui reconnaissent le début d'un séif
NGRAMME = 5              # pour désigner l'édition la plus proche d'un séif divergent
SEUIL_ALIGNEMENT = 0.5   # R2 — mesuré : alignés ≥ 0,636, autre siman ≤ 0,258 (docstring)
ANCRAGE_MIN = 3          # tour 5 — un mot à yod/vav changé d'un séif DIVERGENT n'est donné
                         # pour une variante que dans un passage commun de 3 mots (docstring)
# R2 — et le séif de même numéro doit battre STRICTEMENT tous les autres séifs du siman.
REFERENCE_ALT = "Torat Emet 357"   # R1 — ÉPINGLÉE par son nom (tour 4) : toute autre
# Torat Emet numérotée que Sefaria servirait un jour est IGNORÉE et nommée, comme Freeware.
MARQUE = re.compile(r'[א-ת]["\'׳״]')    # guerech / guerchayim après une lettre
ANCRE_SEFARIA = re.compile(r'<i data-commentator[^>]*>\s*</i>')

COURT = {
    "Ashlei Ravrevei: Shulchan Aruch Yoreh Deah, Lemberg, 1888": "Ashlei Ravrevei",
    "Torat Emet 357": "Torat Emet 357",
    "Torat Emet Freeware Shulchan Aruch": "Torat Emet Freeware",
    "Wikisource Shulchan Aruch": "Wikisource",
}

RAISONS = {}
DATES = {}               # n -> (date UTC du téléchargement, "cache" | "téléchargé" | …) — tour 4


def court(titre):
    titre = (titre or "?").strip()
    return COURT.get(titre, titre[:28])


# ------------------------------------------------------------- normalisation

def consonants(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = unicodedata.normalize('NFC', s)
    return "".join(HE_CONS.findall(s))


def squelette(s):
    """Sans matres lectionis. Sert à LOCALISER un écart, à aligner les mots et à
    mesurer la ressemblance, jamais au verdict : cette porte exige les consonnes
    exactes."""
    return re.sub(r"[יו]", "", s)


def _ngrammes(s):
    return {s[i:i + NGRAMME] for i in range(max(1, len(s) - NGRAMME + 1))}


def proximite(a, b):
    A, B = _ngrammes(a), _ngrammes(b)
    return len(A & B) / max(1, len(A | B))


def mots_autour(brut, k, avant=6, apres=6):
    """Les mots du texte BRUT (balises et nikoud ôtés) autour de la k-ième
    consonne du squelette."""
    t = re.sub(r'<[^>]+>', ' ', brut)
    t = unicodedata.normalize('NFKD', t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    mots_ = t.split()
    cum = 0
    for i, m in enumerate(mots_):
        cum += len(squelette(consonants(m)))
        if cum > k:
            return (" ".join(mots_[max(0, i - avant):i]) + " ⟦" + mots_[i] + "⟧ "
                    + " ".join(mots_[i + 1:i + 1 + apres]))
    return " ".join(mots_[-avant:]) + " ⟦fin⟧"


# --------------------------------------------------------------------- source

def _texte_plat(t):
    if isinstance(t, list):
        return [x if isinstance(x, str) else " ".join(_texte_plat(x)) for x in t]
    return [t] if isinstance(t, str) and t else []


def _lire(u):
    """(code HTTP, JSON) — une erreur HTTP rend son corps, s'il est du JSON."""
    try:
        return 200, json.load(urllib.request.urlopen(u, timeout=60))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, None


def defaut_de(eds):
    """R1 — l'édition PAR DÉFAUT : la priorité Sefaria strictement la plus haute
    (Ashlei Ravrevei, 2.0, sur les 147 simanim servis). None si indécidable."""
    if not eds:
        return None
    top = max(e["priorite"] for e in eds)
    tops = [e for e in eds if e["priorite"] == top]
    return tops[0] if len(tops) == 1 and top > 0 else None


def _complet(d):
    e = defaut_de(d.get("editions") or [])
    return e is not None and bool(consonants("".join(e["seifim"])))


def _recoupe(d):
    """Le fichier de cache porte-t-il la preuve, cohérente avec son contenu, du
    recoupement fait à l'écriture : l'édition qu'api/texts sert par défaut est
    celle que désignent les priorités, et toutes les éditions hébraïques
    annoncées par api/v3 sont là ?"""
    r = d.get("recoupement")
    e = defaut_de(d.get("editions") or [])
    if not isinstance(r, dict) or e is None:
        return False
    titres = {x["titre"] for x in d["editions"]}
    return (r.get("api_texts_defaut") == e["titre"] and isinstance(r.get("annoncees_he"), list)
            and bool(r["annoncees_he"]) and all(t in titres for t in r["annoncees_he"]))


def references(eds):
    """R1 : (édition par défaut, [Torat Emet 357], [éditions servies, avec du
    texte, et IGNORÉES])."""
    d = defaut_de(eds)
    alts = [e for e in eds if e is not d and (e["titre"] or "").strip() == REFERENCE_ALT]
    ign = [e for e in eds if e is not d and e not in alts and consonants("".join(e["seifim"]))]
    return d, alts, ign


def _confirmer_lacune(n, motif):
    """api/v3 dit « pas de texte » : api/texts doit le dire aussi, avec le BON
    ref. Sinon on ne sait pas, et on ne conclut pas."""
    u = f"https://www.sefaria.org/api/texts/{LIVRE}.{n}?context=0&pad=0"
    try:
        code, d = _lire(u)
    except Exception as e:
        RAISONS[n] = f"{motif} ; api/texts injoignable pour confirmer : {type(e).__name__} {e}"[:200]
        return None
    if code != 200 or not d or d.get("error"):
        RAISONS[n] = f"{motif} ; api/texts : HTTP {code} {(d or {}).get('error')!r}"[:200]
        return None
    if not str(d.get("ref", "")).rstrip().endswith(f" {n}"):
        RAISONS[n] = f"{motif} ; api/texts sert le ref {d.get('ref')!r}"[:200]
        return None
    if consonants(" ".join(_texte_plat(d.get("he")))):
        RAISONS[n] = f"{motif} ; mais api/texts SERT du texte : les deux API se contredisent"[:200]
        return None
    DATES[n] = (_maintenant(), "téléchargé (lacune : jamais mise en cache)")
    return {"forme": FORME_CACHE, "ref": d["ref"], "editions": [], "lacune": True}


def _recouper(n, d, eds):
    """L'édition PAR DÉFAUT ne se prend pas sur la seule foi des priorités d'une
    réponse api/v3. L'arbitre du tour 2 l'a montré en sabotant cette réponse :
    sans la version Ashlei Ravrevei, ou avec Torat Emet 357 à une priorité plus
    haute, Torat Emet 357 devenait silencieusement « l'édition par défaut », la
    réponse était GRAVÉE en cache, et une page toute Torat Emet sans la
    parenthèse du 176:2 sortait en 0 — puis encore en 0, cache relu. Deux
    recoupements, et le cache n'est écrit qu'après eux :
      1. `available_versions` d'api/v3 annonce les éditions du siman : chaque
         édition HÉBRAÏQUE annoncée doit être SERVIE dans `versions`. Une réponse
         sans `available_versions` ne permet pas de le vérifier : NON ATTEINT.
      2. api/texts, interrogé SANS paramètre de version, sert l'édition par
         défaut de Sefaria et la nomme (`heVersionTitle`) : ce doit être celle
         que les priorités désignent, et son texte doit avoir les mêmes consonnes
         que celui d'api/v3. Deux points d'entrée distincts doivent dire la même
         chose ; sinon NON ATTEINT, avec la raison.
    Rend la preuve à garder dans le cache, ou None (RAISONS[n] dit pourquoi)."""
    av = d.get("available_versions")
    if not isinstance(av, list):
        RAISONS[n] = ("api/v3 ne liste pas available_versions : impossible de vérifier que toutes "
                      "les éditions hébraïques sont servies")
        return None
    annoncees = sorted({(v.get("versionTitle") or "?").strip() for v in av if isinstance(v, dict)
                        and (v.get("actualLanguage") or v.get("language")) == "he"})
    servies = {(e["titre"] or "").strip() for e in eds}
    manquent = [t for t in annoncees if t not in servies]
    if not annoncees or manquent:
        RAISONS[n] = (f"api/v3 annonce {len(annoncees)} édition(s) hébraïque(s) et ne sert pas : "
                      + (" · ".join(court(t) for t in manquent) or "(aucune annoncée)"))[:200]
        return None
    dft = defaut_de(eds)
    u = f"https://www.sefaria.org/api/texts/{LIVRE}.{n}?context=0&pad=0"
    try:
        code, t = _lire(u)
    except Exception as e:
        RAISONS[n] = f"api/texts injoignable pour recouper l'édition par défaut : {type(e).__name__} {e}"[:200]
        return None
    if code != 200 or not isinstance(t, dict) or t.get("error"):
        err = t.get("error") if isinstance(t, dict) else None
        RAISONS[n] = f"api/texts (recoupement) : HTTP {code} {err!r}"[:200]
        return None
    if not str(t.get("ref", "")).rstrip().endswith(f" {n}"):
        RAISONS[n] = f"api/texts (recoupement) sert le ref {t.get('ref')!r} ≠ siman {n}"[:200]
        return None
    titre = (t.get("heVersionTitle") or "").strip()
    if titre != (dft["titre"] or "").strip():
        RAISONS[n] = (f"api/texts sert par défaut « {court(titre) if titre else '∅'} », les priorités "
                      f"d'api/v3 désignent « {court(dft['titre'])} » : édition par défaut non recoupée")[:200]
        return None
    if consonants(" ".join(_texte_plat(t.get("he")))) != consonants(" ".join(dft["seifim"])):
        RAISONS[n] = (f"le texte par défaut d'api/texts ({court(titre)}) n'a pas les consonnes de celui "
                      "d'api/v3 : réponse non recoupée")[:200]
        return None
    return {"api_texts_defaut": dft["titre"], "annoncees_he": annoncees}


# ------------------------------------------------------------ âge du cache
# Tour 4. Le cache recoupé était cru SANS LIMITE DE DURÉE : si Sefaria corrige son
# texte, la porte compare à un instantané périmé — le piège que CLAUDE.md relève pour
# verifier-troncatures (balayage à froid du 8 octobre : 23 simanim avaient divergé du
# cache en une semaine, coquilles d'OCR corrigées). Chaque fichier porte désormais sa
# date de téléchargement ; la porte l'imprime, et au-delà de AGE_MAX_JOURS elle avertit,
# en tête et en pied, qu'il faut --rafraichir avant publication. Ce n'est pas un code
# d'erreur : le verdict reste celui de la comparaison faite.

def _maintenant():
    return datetime.now(timezone.utc)


def _date_de(d):
    """La date de téléchargement d'un fichier de cache, ou None si elle manque, est
    illisible, sans fuseau, ou dans le futur (fichier forgé ou horloge fausse)."""
    try:
        t = datetime.fromisoformat(str(d.get("telecharge")))
    except (TypeError, ValueError):
        return None
    if t.tzinfo is None or t > _maintenant() + timedelta(days=1):
        return None
    return t


def age_jours(t):
    return (_maintenant() - t).total_seconds() / 86400


def _cache_valide(d, n):
    return (d.get("forme") == FORME_CACHE and str(d.get("ref", "")).endswith(f" {n}")
            and _complet(d) and _recoupe(d) and _date_de(d) is not None)


def lire_cache(n):
    """Le fichier de cache du siman N s'il est valide (forme, ref, édition par défaut
    non vide, preuve de recoupement, date), sinon None."""
    f = os.path.join(CACHE, f"YD-{n}.json")
    if not os.path.exists(f):
        return None
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        return None
    return d if isinstance(d, dict) and _cache_valide(d, n) else None


def fetch(n, rafraichir=False):
    """Les éditions hébraïques du siman N : {"ref", "editions": [{"titre",
    "priorite", "seifim": [html brut…]}]} triées par priorité décroissante — ou
    None, et RAISONS[n] dit pourquoi. Une réponse dont l'édition par défaut est
    vide ou indécidable n'est jamais mise en cache. DATES[n] dit de quand date le
    texte confronté."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"YD-{n}.json")
    if not rafraichir:
        d = lire_cache(n)
        if d is not None:
            DATES[n] = (_date_de(d), "cache")
            return d
    u = (f"https://www.sefaria.org/api/v3/texts/{LIVRE}.{n}?version="
         + urllib.parse.quote("hebrew|all"))
    try:
        code, d = _lire(u)
    except Exception as e:
        RAISONS[n] = f"api/v3/texts injoignable : {type(e).__name__} {e}"[:160]
        return None
    err = str((d or {}).get("error") or "")
    if code == 404 and err.startswith("We have no text for") and err.rstrip(". ").endswith(f" {n}"):
        return _confirmer_lacune(n, f"api/v3 : {err!r}")
    if code != 200 or d is None:
        RAISONS[n] = f"api/v3/texts : HTTP {code} {err!r}"[:200]
        return None
    ref = str(d.get("ref") or "").rstrip()
    if err:
        RAISONS[n] = f"Sefaria répond une erreur (HTTP 200) : {err!r}, ref {d.get('ref')!r}"[:200]
        return None
    if not ref.endswith(f" {n}"):
        RAISONS[n] = f"ref servi {d.get('ref')!r} ≠ siman {n} demandé"[:200]
        return None
    eds = []
    for v in d.get("versions") or []:
        if (v.get("actualLanguage") or v.get("language")) != "he":
            continue
        eds.append({"titre": v.get("versionTitle") or "?",
                    "priorite": v.get("priority") if isinstance(v.get("priority"), (int, float)) else 0,
                    "seifim": _texte_plat(v.get("text"))})
    # La plus prioritaire d'abord : c'est l'édition par défaut d'api/texts.
    eds.sort(key=lambda e: -e["priorite"])
    out = {"forme": FORME_CACHE, "ref": ref, "editions": eds}
    if not _complet(out):
        avec = [e for e in eds if consonants("".join(e["seifim"]))]
        if not avec:
            return _confirmer_lacune(n, "api/v3 : aucune édition n'a de texte")
        dft = defaut_de(eds)
        RAISONS[n] = (("édition par défaut indécidable (aucune priorité strictement plus haute) : "
                       if dft is None else f"l'édition par défaut ({court(dft['titre'])}) est VIDE, "
                       "quand d'autres ont du texte : ")
                      + " · ".join(f"{court(e['titre'])} {e['priorite']}" for e in eds))[:200]
        return None
    rec = _recouper(n, d, eds)
    if rec is None:
        return None
    out["recoupement"] = rec
    t = _maintenant()
    out["telecharge"] = t.isoformat(timespec="seconds")
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    DATES[n] = (t, "téléchargé")
    return out


# ------------------------------------------------------------ R3 : omissions
# Mécanique de verify-chabbat-source.py (tour 2) — `mots`, `_remplacement`,
# `omissions`, `_couvert`, `_egal` —, reprise puis CORRIGÉE après l'arbitrage du
# tour 2, qui a fait certifier deux omissions réelles de Torat Emet 357 (141:1,
# 201:50 ; voir la docstring, R3, points a à e). Les défauts a et b sont dans le
# code COMMUN : verify-chabbat-source.py les porte encore (sa fonction `omissions`
# rend [] sur ces deux passages ; non corrigé ici, ce n'est pas le fichier de
# cette porte). verify-oh-niveau1-source.py a une autre mécanique, non mesurée.

FINALES = str.maketrans("ךםןףץ", "כמנפצ")
MIN_DEPLACE = 4          # consonnes de squelette d'un passage reconnu DÉPLACÉ (R3)


def mots(brut):
    """Les mots d'un texte : [(clé, mot lisible, consonnes, début, fin, groupe)],
    début et fin en position du SQUELETTE de tout le texte (celle de `localiser`).
    La clé est le squelette — ou, pour un mot qui porte un guerech ou des
    guerchayim (abréviation, nombre), ses lettres et ses marques normalisées :
    « סי׳ » (siman) et « ס״י » (séif 10) ont les mêmes consonnes, et « י״א » le
    même squelette que « א׳ ». Un mot sans clé (« ו » seul) n'est pas aligné.
    `groupe` (tour 4) : le numéro de la parenthèse « (…) » ou du crochet « […] » la
    plus INTÉRIEURE ouverte à la première lettre du mot, -1 hors de toute
    parenthèse — ce que lit `attributions`. Les marques se lisent caractère par
    caractère sur TOUS les jetons, ceux sans consonne compris (« ( » isolé), et
    repartent de zéro à chaque texte. La plus intérieure, parce que Torat Emet 357
    laisse des parenthèses ouvertes : au 185:3, « (אמרה: פלוני חכם… וטמאה היא.
    (בית יוסף ר״ן…) » ; au premier niveau, la source y était fondue dans la glose."""
    t = re.sub(r'<[^>]+>', ' ', ANCRE_SEFARIA.sub('', brut))
    out, cum, pile, ngrp = [], 0, [], 0
    for w in re.split(r'[\s־]+', t):
        grp = None
        for ch in w:
            if ch in "([":
                pile.append(ngrp)
                ngrp += 1
            elif ch in ")]":
                if pile:
                    pile.pop()
            elif grp is None and HE_CONS.match(ch):
                grp = pile[-1] if pile else -1
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
            out.append((k, lis, c, cum, cum + L, grp))
        cum += L
    return out


def _sous_suite(a, b):
    it = iter(b)
    return all(ch in it for ch in a)


def _formes(c):
    """Les consonnes d'un mot, et sans son « ו » de conjonction s'il en a un."""
    return [c] + ([c[1:]] if c[:1] == "ו" and len(c) > 1 else [])


def _abrev(w):
    """Le mot porte-t-il un guerech ou des guerchayim collés à une lettre ?"""
    return bool(re.search(r'[א-ת]["\'׳״]|["\'׳״][א-ת]', w))


def _parts(a, ws):
    """Les lettres `a` se partagent-elles, dans l'ordre, en un groupe NON VIDE par
    mot de `ws`, chaque groupe commençant par la PREMIÈRE lettre de son mot et se
    lisant, pour le reste, dans la suite du mot (au squelette) ?"""
    if not ws:
        return not a
    w = ws[0]
    if not a or not w or a[0] != w[0]:
        return False
    for k in range(len(a) - (len(ws) - 1), 0, -1):
        if _sous_suite(squelette(a[1:k]), squelette(w[1:])) and _parts(a[k:], ws[1:]):
            return True
    return False


def _abrege(abr, ws):
    """L'abréviation (ses consonnes) note-t-elle la suite de mots `ws` (leurs
    consonnes) ? CHAQUE MOT Y A SA PART : « אא״כ » note « אלא אם כן » (א|א|כ),
    « בשי״א » note « בשם י״א » (בש|יא) — et NON « בשם י״א ור״ש », où « ור״ש »
    n'a aucune lettre. Le simple test de sous-suite, celui du code commun,
    acceptait ce dernier et taisait la perte de « ור״ש » au 201:50. Le « ו » de
    conjonction peut manquer d'un côté ou de l'autre ; les finales comptent pour
    leur lettre."""
    if not ws:
        return False
    ws = [w.translate(FINALES) for w in ws]
    for a in _formes(abr.translate(FINALES)):
        for w0 in _formes(ws[0]):
            if _parts(a, [w0] + ws[1:]):
                return True
    return False


def _couvert(t, reserve, suite):
    """Un mot de l'édition par défaut, sans contrepartie à sa place, a-t-il sa
    forme ailleurs dans les mots NON appariés de l'autre texte, tout près ?"""
    k, w, c = t[0], t[1], t[2]
    if any(x[0] == k for x in reserve):
        return "déplacé"
    abr = bool(MARQUE.search(w))
    for s in range(len(reserve)):
        for n in range(1, min(4, len(reserve) - s) + 1):
            if abr and _abrege(c, [x[2] for x in reserve[s:s + n]]):
                return "développé"
            if n >= 2 and squelette("".join(x[2] for x in reserve[s:s + n])) == squelette(c):
                return "scindé"
    sq_c = squelette(c)
    for x in reserve:
        if MARQUE.search(x[1]) and any(_abrege(x[2], [c] + [y[2] for y in suite[:q]])
                                       for q in range(0, 4)):
            return "contracté"
        sq_x = squelette(x[2])
        if len(sq_c) >= 2 and len(sq_x) == len(sq_c) and sum(p != q for p, q in zip(sq_c, sq_x)) == 1:
            return "à une lettre près"
    return None


def _egal(a, b, stricte=False):
    """Un mot de l'édition par défaut et un mot de l'autre texte se répondent-ils
    1 pour 1 — même clé, même squelette, à une lettre près (sauf `stricte`), ou
    l'un est l'abréviation de l'autre ?"""
    sa, sb = squelette(a[2]), squelette(b[2])
    if a[0] == b[0] or sa == sb:
        return True
    if (not stricte and len(sa) >= 2 and len(sa) == len(sb)
            and sum(p != q for p, q in zip(sa, sb)) == 1):
        return True
    for x, y in ((a, b), (b, a)):
        if _abrev(x[1]) and not _abrev(y[1]) and _abrege(x[2], [y[2]]):
            return True
    return False


def _paires(A, i, B, j, stricte=False):
    """Les APPARIEMENTS possibles à partir du mot i de A et du mot j de B, en
    (mots de A, mots de B) : 1 pour 1 (`_egal`), un mot pour k mots (abréviation
    développée, mot scindé), k mots pour un (abréviation contractée, mots
    soudés), k ≤ 4."""
    m, n = len(A), len(B)
    if _egal(A[i], B[j], stricte):
        yield 1, 1
    for k in range(2, 5):
        if j + k <= n:          # un mot de A pour k mots de B
            ws = B[j:j + k]
            if (squelette("".join(x[2] for x in ws)) == squelette(A[i][2]) or
                    (_abrev(A[i][1]) and _abrege(A[i][2], [x[2] for x in ws]))):
                yield 1, k
        if i + k <= m:          # k mots de A pour un mot de B
            ws = A[i:i + k]
            if (squelette("".join(x[2] for x in ws)) == squelette(B[j][2]) or
                    (_abrev(B[j][1]) and _abrege(B[j][2], [x[2] for x in ws]))):
                yield k, 1


def _remplacement(A, B, stricte=False, une_lettre=None):
    """Un REMPLACEMENT de difflib peut cacher une omission (« לעשות בו מלאכ׳ בשבת »
    contre « לעשות מלאכה בשבת » : « בו » n'a aucune contrepartie). Petit
    alignement LEXICOGRAPHIQUE : d'abord le plus grand nombre de mots de A
    APPARIÉS (même mot, ktiv, une lettre, abréviation développée ou contractée —
    chaque mot y ayant sa part, voir `_abrege` —, mot scindé ou soudé), ensuite le
    moindre coût du reste : un mot de A substitué par un mot quelconque de B (une
    leçon) 0,5, laissé sans contrepartie 1 ; un mot de B en plus ne coûte rien.
    Le code commun n'avait que le coût : trois substitutions (1,5) y battaient une
    abréviation développée et deux omissions (2), et au 141:1 « (לשון המחבר)
    אא״כ » face à « אלא אם כן » rendait trois LEÇONS et aucune omission — la
    parenthèse de source disparaissait sans un mot. Rend (indices de A sans
    contrepartie, indices de B employés, indices de A SUBSTITUÉS, indices de B
    qui leur sont substitués). Si `une_lettre` est une liste, elle reçoit (tour 5)
    les couples (i de A, j de B) appariés 1 pour 1 SEULEMENT « à une lettre près » —
    ceux que `statuts` doit encore soumettre à `_dittographie` : au 217:44, « בכהנים »
    de Torat Emet 357 était apparié à « מכהנים » à une lettre près, si bien qu'il
    n'était ni substitué ni omis, et la dittographie passait."""
    m, n = len(A), len(B)
    INF = (float("inf"), float("inf"))
    best = [[(INF, None)] * (n + 1) for _ in range(m + 1)]
    best[0][0] = ((0, 0.0), None)
    for i in range(m + 1):
        for j in range(n + 1):
            c = best[i][j][0]
            if c == INF:
                continue

            def pose(i2, j2, non_apparies, cout, quoi):
                c2 = (c[0] + non_apparies, c[1] + cout)
                if c2 < best[i2][j2][0]:
                    best[i2][j2] = (c2, (i, j, quoi))
            if i < m:
                pose(i + 1, j, 1, 1.0, "omis")
            if j < n:
                pose(i, j + 1, 0, 0.0, "ajout")
            if i < m and j < n:
                if not _egal(A[i], B[j], stricte):
                    pose(i + 1, j + 1, 1, 0.5, "leçon")
                for di, dj in _paires(A, i, B, j, stricte):
                    pose(i + di, j + dj, 0, 0.0, "paire")
    omis, pris, subst, subst_b, i, j = [], set(), [], set(), m, n
    while (i, j) != (0, 0):
        pi, pj, quoi = best[i][j][1]
        if quoi == "omis":
            omis.append(pi)
        elif quoi in ("paire", "leçon"):
            pris.update(range(pj, j))
            if quoi == "leçon":
                subst.append(pi)
                subst_b.add(pj)
            elif (une_lettre is not None and i - pi == 1 and j - pj == 1
                  and not _egal(A[pi], B[pj], stricte=True)):
                une_lettre.append((pi, pj))
        i, j = pi, pj
    return sorted(omis), pris, sorted(subst), subst_b


def _suites(idx):
    """Les suites d'indices consécutifs."""
    out = []
    for i in sorted(idx):
        if out and i == out[-1][-1] + 1:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def _deplace(seq, B, libres):
    """Le passage `seq` (mots de A) se lit-il D'UN SEUL TENANT parmi les mots NON
    APPARIÉS de B (`libres` : ni égaux ni abréviation d'un mot de A — un mot de B
    seulement SUBSTITUÉ à un mot de A en est), n'importe où dans le séif —
    chaque mot apparié STRICTEMENT (même clé ou même squelette, abréviation où
    chaque mot a sa part, mot scindé ou soudé ; jamais « à une lettre près »,
    qui à l'échelle d'un séif apparie « מהרי״ו » à « מהן » et « ואוסרין » à
    « אסורה »), aucun substitué, aucun omis, aucun mot de B en plus, sur DEUX
    MOTS de B au moins et MIN_DEPLACE consonnes de squelette ? Un mot seul qui
    se retrouve ailleurs n'est jamais un déplacement : il reste une omission.
    Au 94:5, Torat Emet 357 porte « (ארך כלל ל״ז) » quatre mots plus haut que
    l'édition par défaut : la fenêtre de `_couvert` ne le voyait pas, et la porte
    l'annonçait « absent aussi de Torat Emet 357 » dans les trois langues."""
    m = len(seq)
    for j in sorted(libres):
        ws = []
        while j + len(ws) in libres and len(ws) < 4 * m + 3:
            ws.append(B[j + len(ws)])
        # Parcours des seuls appariements : atteints[i] = longueurs de ws lues
        # quand les i premiers mots de seq sont appariés.
        atteints = [set() for _ in range(m + 1)]
        atteints[0].add(0)
        for i in range(m):
            for jj in atteints[i]:
                if jj < len(ws):
                    for di, dj in _paires(seq, i, ws, jj, stricte=True):
                        atteints[i + di].add(jj + dj)
        if any(jj >= 2 and len(squelette("".join(x[2] for x in ws[:jj]))) >= MIN_DEPLACE
               for jj in atteints[m]):
            return True
    return False


PORTEE_COPIE = 2           # mots : copie d'un seul mot à UN mot d'écart (« X או X »), tour 5
FENETRE_ASSIMILATION = 6   # mots : portée de l'ASSIMILATION non contiguë (tour 5)


def _initiale_changee(a, b):
    """Deux mots appariés « à une lettre près » (squelettes de même longueur, une
    lettre différente) diffèrent-ils par leur PREMIÈRE lettre — la préposition
    (« כפירות » / « בפרות », « מכהנים » / « בכהנים ») ?"""
    sa, sb = squelette(a[2]).translate(FINALES), squelette(b[2]).translate(FINALES)
    return bool(sa) and bool(sb) and sa[0] != sb[0]


# PAS DE BORNE sur la longueur de la suite répétée (tour 6). Le tour 4 la bornait à 4 mots,
# sans mesure : l'arbitre du tour 5 a fait certifier conforme, code 0, une copie de CINQ mots
# écrite deux fois à la place d'un passage de l'édition par défaut (témoins D4 et D6). Portée
# à 12, son arbitre a fait passer de même une copie de TREIZE mots (X13x1, N13) : une borne
# fixe ne fait que déplacer le trou. La suite va donc jusqu'à la moitié du séif (len(B)//2,
# au-delà elle ne peut pas être écrite deux fois). Mesuré sur les 148 simanim : sortie
# complète identique à l'octet à celle de la borne 4, 12 ou 200 ; coût mesuré par l'arbitre du
# tour 7 : environ 5,6 s (15,2 → 20,9 s pour --tous --bref).
# Reste, déclaré : la condition 4 (le mot remplacé ne se lit nulle part ailleurs dans le séif)
# est jugée sur les consonnes exactes depuis le tour 6 ; un homonyme EXACT ailleurs dans le
# séif désactive encore la détection, quelle que soit la longueur de la copie — et ce n'est pas
# marginal : 35,9 % des mots de l'édition par défaut ont un homonyme exact dans leur séif (mesure de
# l'arbitre du tour 7). Voir « Ce que la porte ne fait pas ».


def _dittographie(A, ia, B, jb, assimilation=False):
    """DITTOGRAPHIE (tour 4) — le mot B[jb], SUBSTITUÉ au mot A[ia] (ou, depuis le
    tour 5, apparié à lui « à une lettre près »), est-il la copie d'un mot voisin
    plutôt qu'une leçon ? Au 234:37, Torat Emet 357 écrit « מחול לך,
    או שרוי לך, או שרוי לך » pour « מחול ליך או מותר ליך או שרוי ליך » : « שרוי »
    est substitué à « מותר », et la formule « מותר ליך » disparaît derrière une
    répétition. R3 excuse une leçon, jamais une omission ; une dittographie est une
    omission. Quatre conditions, toutes requises :
      1. B[jb] appartient à une suite de L mots (1 ≤ L ≤ len(B)/2) que B écrit DEUX FOIS DE
         SUITE, aux mêmes consonnes (« או שרוי לך » · « או שרוי לך » ; pas « ספק
         ספקו », deux mots de même squelette) ;
      2. l'AUTRE copie se lit telle quelle dans A, tout près (à 2L+2 mots) : c'est le
         texte qu'on a recopié une fois de trop (« או שרוי ליך »). Sans elle, une
         page DIVERGENTE du 110:10 qui écrit « בין הטלאים, הטלאים מתרים » pour
         « בכבשים ערבוביא הכבשים מותרים » passait pour une dittographie ;
      3. A, au même endroit, ne se répète PAS (au 201:19, « לזה לג ומחצה ולזה לג
         ומחצה » est répété dans l'édition par défaut elle-même, et Torat Emet 357 y
         écrit « לזו » : une leçon) ;
      4. le mot remplacé (« מותר ») ne se lit NULLE PART dans B, aux consonnes exactes. LIMITE :
         s'il a un homonyme exact ailleurs dans le séif (35,9 % des mots de l'édition par défaut),
         la copie n'est pas reconnue, quelle que soit sa longueur, et la page sort « leçon excusée ».
    La règle demandée (« un mot substitué qui répète un mot voisin du même séif, le
    mot remplacé n'existant nulle part ailleurs ») est plus large : sur les 519
    substitutions un-pour-un de Torat Emet 357 (516 au compte du tour 4, qui ne
    retirait pas le chapeau de Torat Emet), elle en prend 47 (34 séifs), et à la
    lecture tout sauf 234:37 est la censure (« אלילים » / « עבודת כוכבים » : le mot
    « כוכבים » revient trois mots plus loin dans « של עובד כוכבים ») ou une leçon
    (« בלי » / « בלא », « הנאד » / « הנוד », « ובית » / « ובבית »). La répétition
    CONTIGUË (condition 1) est la signature de la dittographie.
    TOUR 5, ce que le tour 4 ne voyait pas. Sa mesure (« une seule substitution
    retenue, 234:37 ») ne portait que sur les SUBSTITUTIONS. Or un mot apparié
    « à une lettre près » (`_egal`) n'est ni substitué ni omis : au 217:44, Torat
    Emet 357 écrit « אסור בכהנים ולויים. בכהנים ולויים, מתר בישראל » pour « אסור
    בכהנים ולוים מכהנים ולוים מותר בישראל » — la condition « (celui qui a fait vœu)
    à l'égard des kohanim » disparaît derrière la répétition, et une page qui la
    recopiait sortait IDENTIQUE (témoin de l'arbitre X1). `statuts` soumet donc
    aussi à cette fonction les 287 couples appariés à une lettre près : les quatre
    conditions en prennent UN, 217:44. Et, pour ces couples seulement, quand la
    lettre changée est l'INITIALE (`_initiale_changee` — la préposition : « כ »
    comme, « ב » dans, « מ » de, « ל » à), une forme NON CONTIGUË
    (`assimilation`) : B[jb] a les consonnes exactes d'un mot de B à au plus
    FENETRE_ASSIMILATION mots, dont la contrepartie se lit dans A à sa place (±2),
    et le mot de A est absent de B. Au 173:16, Torat Emet 357 écrit « מצוים בפרות.
    הגה: ויש מתירין בפרות » pour « מצויים כפירות: הגה ויש מתירין בפירות » : « aussi
    courants que les fruits » devient « courants dans les fruits », par
    assimilation au « בפרות » de la glose (témoin de l'arbitre X2). Sur les 287
    couples, 35 changent l'initiale (« כשהיה » / « בשהיה »…), et la forme non
    contiguë n'en prend qu'un, 173:16. Sans la condition sur l'initiale, elle
    prendrait quatre couples de plus — 112:15 « תשובה » / « תשובת », 114:10
    « נותנין » / « נותנים », 138:8 « בהם » / « בהן », 215:1 « המצות » / « המצוה » —,
    des désinences : des leçons d'un même mot, non une omission. Sur les
    SUBSTITUTIONS, et sur les couples dont l'initiale ne change pas, la forme non
    contiguë ne va pas au-delà d'UN mot d'écart (PORTEE_COPIE = 2 : « לאשתו או
    לאשתו » pour « לאשתו או לבתו », témoin ND2 de l'arbitre, que le tour 4 donnait
    pour limite déclarée) : à six mots elle prendrait 25 substitutions (22 séifs),
    la censure (« אלילים » / « עבודת כוכבים » devant « של עובד כוכבים ») et des
    leçons ; à un mot d'écart, AUCUNE de plus sur Torat Emet 357. Mesure du 9
    octobre, 1 452 séifs, règle de la porte : 519 substitutions → 1 (234:37) ; 287
    couples à une lettre près → 2 (217:44, 173:16).
    Rend (nature, texte) — nature « DITTOGRAPHIE » (texte : la suite répétée, deux
    fois) ou « ASSIMILATION » (texte : « mot de B » … « son modèle ») —, ou None."""
    KA, KB = [x[0] for x in A], [x[0] for x in B]
    CB = [x[2].translate(FINALES) for x in B]
    # condition 4 sur les CONSONNES EXACTES (tour 6) : jugée sur le squelette, un homonyme de
    # squelette n'importe où dans le séif désactivait la détection, quelle que soit la longueur de
    # la copie (arbitre du tour 6). Sortie des 148 simanim identique dans les deux cas.
    if A[ia][2].translate(FINALES) in CB:
        return None
    for L in range(1, len(B) // 2 + 1):
        for s0 in range(jb, jb - L, -1):
            for t in (s0 - L, s0 + L):
                if s0 < 0 or t < 0 or max(s0, t) + L > len(KB) or CB[s0:s0 + L] != CB[t:t + L]:
                    continue
                sa, ta = ia - (jb - s0), ia - (jb - s0) + (t - s0)
                if (min(sa, ta) >= 0 and max(sa, ta) + L <= len(KA)
                        and KA[sa:sa + L] == KA[ta:ta + L]):
                    continue
                if not any(KA[u:u + L] == KB[t:t + L]
                           for u in range(max(0, ia - 2 * L - 2), min(len(KA) - L, ia + 2 * L + 2) + 1)):
                    continue
                return ("DITTOGRAPHIE", " ".join(B[k][1] for k in range(min(s0, t), min(s0, t) + 2 * L)))
    # Forme NON CONTIGUË d'un seul mot (tour 5) : B[jb] a les consonnes exactes d'un mot
    # de B à d mots (2 ≤ |d| ≤ portée), dont la contrepartie se lit dans A à sa place
    # (±2) — le modèle qu'on a recopié. |d| = 1 relève de la forme contiguë ci-dessus.
    portee = FENETRE_ASSIMILATION if assimilation else PORTEE_COPIE
    for d in sorted(range(-portee, portee + 1), key=abs):
        t = jb + d
        if abs(d) < 2 or not 0 <= t < len(B) or CB[t] != CB[jb]:
            continue
        if any(0 <= u < len(KA) and KA[u] == KB[t] for u in range(ia + d - 2, ia + d + 3)):
            if abs(d) <= PORTEE_COPIE:
                return ("DITTOGRAPHIE", " ".join(B[k][1] for k in range(min(jb, t), max(jb, t) + 1)))
            return ("ASSIMILATION", f"« {B[jb][1]} » copie « {B[t][1]} », {abs(d)} mots plus "
                    f"{'loin' if d > 0 else 'haut'}")
    return None


OMIS = ("omis", "répété")   # les sorts qui sont une OMISSION (R3)


def dire_copie(note):
    """Ce que dit la sortie d'une copie de voisin (`_dittographie`) : (nature, texte)."""
    nature, texte = note
    if nature == "ASSIMILATION":
        return f"un mot voisin recopié (ASSIMILATION : {texte})"
    return f"une suite voisine deux fois (DITTOGRAPHIE : « {texte} »)"


def statuts(A, B, notes=None):
    """Le sort de chaque mot de A (l'édition par défaut) dans B :
      'porté'   — apparié à sa place (même mot, ktiv, une lettre, abréviation
                  développée ou contractée, scindé ou soudé), ou couvert par un
                  mot non apparié de B tout près (`_couvert`) ;
      'leçon'   — un mot de B lui est substitué (et, s'il y en a un, le seul mot
                  laissé sans contrepartie à côté de la substitution : la censure
                  deux-pour-un, « עובד כוכבים » / « גוי ») ;
      'déplacé' — sans contrepartie à sa place, mais tout son passage se lit d'un
                  seul tenant ailleurs dans le séif de B (`_deplace`) ;
      'répété'  — un mot de B lui est substitué, ou apparié à une lettre près
                  (tour 5), mais ce mot est la COPIE d'une suite voisine
                  (`_dittographie`, tour 4) : une OMISSION (R3) ; `notes`, s'il est
                  donné, reçoit {indice : (nature, texte)} ;
      'omis'    — rien de cela : une OMISSION (R3).
    Une SUPPRESSION de difflib est candidate à l'omission ; un REMPLACEMENT l'est
    pour les mots que son alignement fin (`_remplacement`) laisse sans
    contrepartie quand aucun mot n'y est substitué — et, quand un mot l'est, s'il
    en laisse DEUX ou plus : tout le passage remplacé est alors candidat."""
    st = ["porté"] * len(A)
    if not A:
        return st
    sm = difflib.SequenceMatcher(None, [x[0] for x in A], [x[0] for x in B], autojunk=False)
    libres, substitues, cand = set(), set(), []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "insert":
            libres.update(range(j1, j2))
        elif op == "delete":
            cand.append((list(range(i1, i2)), i1, i2, j1, j2))
        elif op == "replace":
            ul = []
            om, pris, subst, subst_b = _remplacement(A[i1:i2], B[j1:j2], une_lettre=ul)
            libres.update(j1 + j for j in range(j2 - j1) if j not in pris)
            substitues.update(j1 + j for j in subst_b)
            # Tour 5 — un mot apparié « à une lettre près » peut être la copie d'un
            # voisin (217:44, « בכהנים » pour « מכהנים ») : il n'est ni substitué ni
            # omis, et le tour 4 ne le soumettait pas à `_dittographie`. Forme
            # non contiguë admise si la lettre changée est l'initiale (173:16).
            for ia, jb in ul:
                rep_ = _dittographie(A, i1 + ia, B, j1 + jb,
                                     assimilation=_initiale_changee(A[i1 + ia], B[j1 + jb]))
                if rep_:
                    st[i1 + ia] = "répété"
                    if notes is not None:
                        notes[i1 + ia] = rep_
            # ÉCART AU CODE COMMUN : verify-chabbat-source.py ne retient rien d'un
            # remplacement où un mot est substitué. Ici, DEUX mots ou plus laissés
            # sans contrepartie sont une omission même à côté d'une substitution —
            # au 158:2, « היו נוהגין בזמן הבית » pour « מצוה » perd « au temps du
            # Temple ». Une substitution de deux mots par un (« עובד כוכבים » /
            # « גוי », la censure) n'en laisse qu'un : leçon. Le passage cité est
            # alors tout ce que le remplacement n'APPARIE pas, substitués compris :
            # lequel des mots non appariés l'alignement donne au mot substitué est
            # arbitraire (au 156:3, il désignait « כהני עבודת » quand c'est
            # « עבודת כוכבים » qui manque). Le tour 2 y mettait tout le passage
            # remplacé, mots APPARIÉS compris : au 113:13 d'une page, « מותרין »
            # était donné pour absent à côté de son « מתרים ».
            if om and not subst:
                cand.append(([i1 + i for i in om], i1, i2, j1, j2))
            elif len(om) >= 2:
                cand.append((sorted(i1 + i for i in om + subst), i1, i2, j1, j2))
            else:
                for i in subst + om:
                    st[i1 + i] = "leçon"
                # Tour 4 — une substitution qui n'est que la copie d'une suite voisine
                # (dittographie) est une OMISSION. L'alignement est monotone : les
                # indices substitués de A et de B se répondent dans l'ordre.
                ditto = False
                for ia, jb in zip(subst, sorted(subst_b)):
                    rep_ = _dittographie(A, i1 + ia, B, j1 + jb)
                    if rep_:
                        ditto = True
                        st[i1 + ia] = "répété"
                        if notes is not None:
                            notes[i1 + ia] = rep_
                # Le mot laissé seul à côté d'une substitution n'était excusé que comme
                # la moitié d'une censure deux-pour-un ; sans leçon, il est candidat.
                if ditto and om:
                    cand.append(([i1 + i for i in om], i1, i2, j1, j2))
    for idx, i1, i2, j1, j2 in cand:
        K = (i2 - i1) + 6
        reserve = [B[j] for j in range(max(0, j1 - K), min(len(B), j2 + K)) if j in libres]
        for i in idx:
            if _couvert(A[i], reserve, A[i + 1:]) is None:
                st[i] = "omis"
    for run in _suites(i for i, x in enumerate(st) if x == "omis"):
        if _deplace([A[i] for i in run], B, libres | substitues):
            for i in run:
                st[i] = "déplacé"
    return st


def omissions(A, B):
    """Les suites d'indices des mots de A (l'édition par défaut) OMIS dans B (R3) —
    dittographies comprises."""
    return _suites(i for i, x in enumerate(statuts(A, B)) if x in OMIS)


def texte_de(A, run):
    """Les mots d'une suite, pour l'affichage : un passage de plus de 24 mots
    (une glose du Rama entière) est montré par ses bouts ; son nombre de mots est
    toujours imprimé à côté."""
    m = [A[i][1] for i in run]
    return " ".join(m) if len(m) <= 24 else " ".join(m[:14]) + " … " + " ".join(m[-6:])


def ressemblance(A, B):
    """R2 — ratio de difflib sur les CLÉS des mots de deux textes."""
    return difflib.SequenceMatcher(None, [x[0] for x in A], [x[0] for x in B],
                                   autojunk=False).ratio()


def _groupes(W):
    """{n° de parenthèse : [indices de ses mots]} (le 6e champ de `mots`)."""
    g = {}
    for k, x in enumerate(W):
        if x[5] >= 0:
            g.setdefault(x[5], []).append(k)
    return g


def _repond(Ag, Bh):
    """La parenthèse Bh (de l'autre texte) RÉPOND-elle à la parenthèse Ag (de
    l'édition par défaut) — est-ce la même source ? L'alignement fin
    (`_remplacement`, STRICT : jamais « à une lettre près », qui appariait « (וכן »
    à « ור״ן) ») apparie le PREMIER mot de Ag — le nom de la source, d'ordinaire —,
    ou ce mot se lit dans Bh ; et la moitié au moins des mots de Ag ET de Bh sont
    appariés ou se lisent dans l'autre (les noms d'une attribution réordonnée ne
    sont pas appariés par un alignement monotone : 185:3). Sans la condition sur
    Bh, « (ב״י) » répondait à « (בית יוסף בשם הרא״ש ורבינו ירוחם) » (185:1).
    Rend (oui ?, mots de Ag sans contrepartie à leur place, mots de Bh non
    employés)."""
    om, pris, subst, sb = _remplacement(Ag, Bh, stricte=True)
    seuls_a = set(om) | set(subst)
    libres_b = [j for j in range(len(Bh)) if j not in pris or j in sb]
    ka, kb = {x[0] for x in Ag}, {x[0] for x in Bh}
    cov_a = sum(1 for i in range(len(Ag)) if i not in seuls_a or Ag[i][0] in kb)
    cov_b = sum(1 for j in range(len(Bh)) if j not in libres_b or Bh[j][0] in ka)
    premier = 0 not in seuls_a or Ag[0][0] in kb
    return premier and 2 * cov_a >= len(Ag) and 2 * cov_b >= len(Bh), sorted(seuls_a), libres_b


POIDS_PARENTHESE = 1.5  # attributions : une parenthèse pèse 1,5 mot dans l'alignement pondéré


def _aligne_pondere(ka, kb, poids):
    """Plus longue sous-suite commune PONDÉRÉE (programmation dynamique) : {position
    dans ka : position dans kb}. Remplace difflib pour `attributions` : difflib prend
    le premier plus long bloc, et au 228:12 il appariait le « שכיח » de la glose du
    Rama au « שכיח » de la phrase suivante de Torat Emet 357 — la parenthèse « (ב״י
    בשם הגמרא…) », pourtant à sa place, sortait déplacée."""
    n, m = len(ka), len(kb)
    dp = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai, row, prev = ka[i - 1], dp[i], dp[i - 1]
        w = poids(ai)
        for j in range(1, m + 1):
            v = row[j - 1] if row[j - 1] > prev[j] else prev[j]
            if ai == kb[j - 1] and prev[j - 1] + w > v:
                v = prev[j - 1] + w
            row[j] = v
    image, i, j = {}, n, m
    while i and j:
        if ka[i - 1] == kb[j - 1] and dp[i][j] == dp[i - 1][j - 1] + poids(ka[i - 1]):
            image[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif dp[i][j] == dp[i - 1][j]:
            i -= 1
        else:
            j -= 1
    return image


def attributions(A, B):
    """LEÇONS D'ATTRIBUTION (tour 4). Les parenthèses de source de A (l'édition par
    défaut) que B place AILLEURS, ou dont B RÉORDONNE les noms : [(indices des mots
    de A, nature, mots franchis)]. R3 les excuse — aucun mot n'est perdu —, mais la
    règle de CLAUDE.md (« le Choul'han Aroukh est le repère, ordre compris ») veut
    qu'elles soient NOMMÉES : une page qui recopie Torat Emet 357 au 157:1 rattache
    « (ב״י בשם רש״י ור״ן) » à la proposition suivante, et sortait verte sans un mot.
    Décision de ce tour : le verdict reste 0, la sortie dit « source attribuée
    autrement (Torat Emet 357) », avec le nombre de mots que la parenthèse franchit.
    Mécanique. Chaque parenthèse (ou crochet) devient UN symbole ; deux parenthèses
    qui se répondent (`_repond`) ont le même. Les deux textes, mots hors parenthèses
    (leur clé) et symboles mêlés, sont alignés (`_aligne_pondere`) : une parenthèse
    de A appariée à son symbole dans B est À SA PLACE. Une parenthèse de A que
    l'alignement laisse seule, et dont le symbole se lit dans B sur une parenthèse
    qu'aucune autre parenthèse de A n'a prise à sa place, est PLACÉE AILLEURS ; les
    mots franchis sont ceux de B (hors parenthèses) entre elle et l'endroit où B
    porte les voisins de A. Au 157:1, les trois parenthèses de la fin du séif sont
    décalées d'une proposition (8, 15 et 19 mots franchis) ; au 94:5, « (ארוך כלל
    ל״ז) » passe de la coutume (« ונוהגין להחמיר… ») au din qui la précède (14). Une
    première version ancrait chaque parenthèse aux mots appariés qui l'entourent :
    elle laissait passer celle que la PROPOSITION enjambe (« (משנה פ׳ ח׳ דתרומות…) »
    au 157:1 : c'est « אלא א״כ יחדוהו… פלוני » qui change de côté) ; un alignement de
    la suite entière ne s'y trompe pas. Une parenthèse à sa place dont un nom, sans
    contrepartie à sa place, se lit parmi les mots non employés de sa parenthèse
    dans B a ses noms dans un AUTRE ORDRE
    (185:3 : « (ר״ן בשם הרמב״ן ורבינו ירוחם) » / « (בית יוסף ר״ן ורבינו ירוחם בשם
    הרמב״ן) » — ce qui est dit « au nom du Ramban » n'est plus la même chose). Une
    parenthèse sans réponse n'est pas une attribution : omise (R3 le dit), ou
    écrite sans parenthèses (185:3, « (אם הוא לאחר כדי דבור) »)."""
    ga, gb = _groupes(A), _groupes(B)
    if not ga or not gb:
        return []
    classe = {("A", g): ("A", g) for g in ga}
    classe.update({("B", h): ("B", h) for h in gb})

    def racine(x):
        while classe[x] != x:
            x = classe[x]
        return x
    detail = {}
    for g, idx in ga.items():
        for h, jdx in gb.items():
            ok, seuls_a, libres_b = _repond([A[i] for i in idx], [B[j] for j in jdx])
            if ok:
                detail[(g, h)] = (seuls_a, libres_b)
                ra, rb = racine(("A", g)), racine(("B", h))
                if ra != rb:
                    classe[rb] = ra

    def suite(W, cote):
        out, vu = [], set()
        for k, x in enumerate(W):
            if x[5] < 0:
                out.append((x[0], k))
            elif x[5] not in vu:
                vu.add(x[5])
                out.append((("§",) + racine((cote, x[5])), k))
        return out
    sa, sb_ = suite(A, "A"), suite(B, "B")
    pos_a = {A[x[1]][5]: p for p, x in enumerate(sa) if isinstance(x[0], tuple)}
    pos_b = {B[x[1]][5]: p for p, x in enumerate(sb_) if isinstance(x[0], tuple)}
    classes_b = {racine(("B", h)) for h in gb}
    if not any(racine(("A", g)) in classes_b for g in ga):
        return []
    # L'alignement est PONDÉRÉ (une parenthèse pèse POIDS_PARENTHESE mots) : une
    # parenthèse n'est déplacée que si la garder à sa place coûtait plus d'un mot.
    # Décalée d'UN mot dans la même proposition (160:14, « (טור סי׳ קס״ט) » de part et
    # d'autre de « לו »), elle reste à sa place ; dès deux mots franchis, elle est
    # NOMMÉE. difflib, qui prend le premier plus long bloc, ne convenait pas (voir
    # `_aligne_pondere`) ; l'alignement pondéré coûte 1 s sur les 1 452 séifs.
    image = _aligne_pondere([x[0] for x in sa], [x[0] for x in sb_],
                            lambda k: POIDS_PARENTHESE if isinstance(k, tuple) else 1.0)
    en_place = {g: B[sb_[image[p]][1]][5] for g, p in pos_a.items() if p in image}
    prises = set(en_place.values())
    out = []
    for g, idx in ga.items():
        if g in en_place:
            seuls_a, libres_b = detail.get((g, en_place[g]), ([], []))
            jdx = gb[en_place[g]]
            kb_libres = {B[jdx[j]][0] for j in libres_b}
            if any(A[idx[i]][0] in kb_libres for i in seuls_a):
                out.append((idx, "noms de la parenthèse dans un autre ordre", 0))
            continue
        hs = [h for h in gb if h not in prises and racine(("B", h)) == racine(("A", g))]
        if not hs:
            continue
        p = pos_a[g]
        av = [image[q] for q in range(p) if q in image]
        ap = [image[q] for q in range(p + 1, len(sa)) if q in image]
        lo, hi = (max(av) if av else -1), (min(ap) if ap else len(sb_))

        def franchis(h):
            ph = pos_b[h]
            if ph < lo:
                rng = range(ph + 1, lo + 1)
            elif ph > hi:
                rng = range(hi, ph)
            else:
                return 0
            return sum(1 for q in rng if not isinstance(sb_[q][0], tuple))
        h = min(hs, key=lambda h: (franchis(h), pos_b[h]))
        f = franchis(h)
        if f:
            out.append((idx, "placée ailleurs", f))
    return out


# ------------------------------------------------------------- garde ktiv
# Tour 4. Le squelette ôte TOUT yod et tout vav : « כוס » (coupe) et « כיס » (poche),
# « מים » (eau) et « מום » (défaut), « יום » et « ים », « לו » et « לי », « הוא » et
# « היא » y ont la même clé. Cette porte n'a pas de verdict ÉQUIVALENT — un séif qui
# ne passe que le squelette est refusé (code 1) —, mais elle l'appelait « KTIV —
# égal … aux seules matres lectionis près » et n'imprimait que les premiers mots du
# séif : une page qui changeait « כוס » en « כיס » y était décrite comme une affaire
# d'orthographe, sans que le mot fût nommé. RÈGLE COMMUNE aux trois portes : deux mots
# ne sont égaux au ktiv près que si l'un s'obtient de l'autre en AJOUTANT des yod/vav
# (sous-suite, finales normalisées) ; un yod/vav ÉCHANGÉ au même endroit est un mot
# changé. Comme verify-chabbat-source.py, cette porte va un pas plus loin, puisque
# l'étiquette ne coûte aucun verdict : l'ajout doit être INTÉRIEUR au mot — en tête,
# c'est le ו de conjonction (« ועקרבים » / « עקרבים ») ; en fin, la personne ou le
# nombre (« עליו » / « עלי ») — et un mot de deux lettres que l'ajout allonge
# (« ים » / « יום ») est rendu à part, « à contrôler ». Chaque mot est IMPRIMÉ.


def _par_ajout(court, long_, interieur):
    """`long_` s'obtient-il de `court` en AJOUTANT seulement des yod et des vav — et,
    si `interieur`, ni en première ni en dernière lettre de `long_` ? (Programmation
    dynamique : un yod de `long_` peut être lu ou sauté, et le choix glouton n'est
    pas toujours le bon.)"""
    n, m, ok = len(court), len(long_), {0}
    for j, ch in enumerate(long_):
        nouv = set()
        for i in ok:
            if ch in "יו" and (not interieur or 0 < j < m - 1):
                nouv.add(i)
            if i < n and court[i] == ch:
                nouv.add(i + 1)
        ok = nouv
        if not ok:
            return False
    return n in ok


def nature_ktiv(a, b):
    """Deux mots (consonnes) de même squelette : None s'ils sont égaux, finales
    normalisées ; sinon « ktiv » (yod/vav ajoutés à l'intérieur du mot : « מתר » /
    « מותר ») ; « mot de deux lettres » (l'ajout allonge un mot de deux lettres :
    « ים » / « יום », « לך » / « ליך » — à contrôler) ; « en tête ou en fin de mot »
    (« ועקרבים » / « עקרבים », « עליו » / « עלי ») ; « échange » (ni l'un ni l'autre ne
    s'obtient par ajout : « כוס » / « כיס », « הוא » / « היא », et le vav qui change
    de place, « יוכל » / « יכול »)."""
    a, b = a.translate(FINALES), b.translate(FINALES)
    if a == b:
        return None
    c, l = (a, b) if len(a) <= len(b) else (b, a)
    if len(c) < len(l):
        if _par_ajout(c, l, True):
            return "mot de deux lettres" if len(c) <= 2 else "ktiv"
        if _par_ajout(c, l, False):
            return "en tête ou en fin de mot"
    # Un ו de conjonction d'un côté, du ktiv pour le reste (« ואפלו » / « אפילו ») : le
    # mot changé est en tête, ce n'est pas un échange.
    for x, y in ((a, b), (b, a)):
        if x[:1] == "ו" and len(x) > 2 and nature_ktiv(x[1:], y) in (None, "ktiv", "mot de deux lettres"):
            return "en tête ou en fin de mot"
    return "échange"


KTIV_SEUL = ("ktiv", "mot de deux lettres")   # natures qui laissent le séif « KTIV »


def garde_ktiv(Wp, We, egaux_seuls=False, blocs=None):
    """Les mots de la page (Wp) et d'une édition (We) qui ne sont égaux qu'au
    squelette près : [(mot de la page, mot de l'édition, nature, indice dans Wp)].
    Alignement par clé (difflib) : dans un bloc égal, mot à mot ; dans un
    remplacement de même nombre de mots, mot à mot aussi ; sinon le passage entier,
    nature « découpage des mots différent » s'il a le même squelette — ignoré si
    `egaux_seuls` (séif DIVERGENT : seuls les mots appariés y sont jugés). Si
    `blocs` est un dict, il reçoit (tour 5) {indice dans Wp : nombre de mots du bloc
    égal qui le contient} — ce qui sépare un mot ANCRÉ dans un passage commun d'un
    appariement ISOLÉ de difflib (`ANCRAGE_MIN`)."""
    sm = difflib.SequenceMatcher(None, [x[0] for x in Wp], [x[0] for x in We], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1 and not egaux_seuls):
            for k in range(i2 - i1):
                p, e = Wp[i1 + k], We[j1 + k]
                if p[2] != e[2] and squelette(p[2]) == squelette(e[2]):
                    nat = nature_ktiv(p[2], e[2])
                    if nat:
                        out.append((p[1], e[1], nat, i1 + k))
                        if blocs is not None:
                            blocs[i1 + k] = (i2 - i1) if op == "equal" else 0
        elif not egaux_seuls and op != "equal":
            cp = "".join(x[2] for x in Wp[i1:i2])
            ce = "".join(x[2] for x in We[j1:j2])
            if cp.translate(FINALES) != ce.translate(FINALES) and squelette(cp) == squelette(ce):
                out.append((" ".join(x[1] for x in Wp[i1:i2]) or "∅", " ".join(x[1] for x in We[j1:j2]) or "∅",
                            "découpage des mots différent", i1))
    return out


def _mots_egaux(Wp, We):
    """Les indices des mots de Wp que l'alignement par clé apparie à un mot de We
    AUX MÊMES CONSONNES (finales normalisées)."""
    sm = difflib.SequenceMatcher(None, [x[0] for x in Wp], [x[0] for x in We], autojunk=False)
    return {i1 + k for op, i1, i2, j1, j2 in sm.get_opcodes() if op == "equal" for k in range(i2 - i1)
            if Wp[i1 + k][2].translate(FINALES) == We[j1 + k][2].translate(FINALES)}


def garde_seif(ref, i, Wp, labs):
    """La garde ktiv sur un séif de la page (mots Wp) dont le squelette est celui
    d'une leçon de référence (éditions `labs`) : l'édition dont la page s'écarte le
    moins (mots changés, puis tous les écarts ; l'édition par défaut d'abord), ses
    écarts, et pour chacun les AUTRES éditions de référence du séif qui écrivent ce
    mot exactement comme la page (deux éditions mêlées dans le séif : « מתר » de
    Torat Emet 357 dans un séif d'Ashlei Ravrevei). Rend {"ed", "changes", "ktiv"}."""
    res = {}
    for ed in labs:
        if ref.bruts[i].get(ed) is not None:
            res[ed] = garde_ktiv(Wp, mots(ref.bruts[i][ed]))
    if not res:
        return {"ed": labs[0] if labs else "?", "changes": [], "ktiv": []}
    ed = min(res, key=lambda e: (sum(1 for x in res[e] if x[2] not in KTIV_SEUL), len(res[e]),
                                 e != ref.D))
    autres = {e: _mots_egaux(Wp, mots(b)) for e, b in ref.bruts[i].items() if e != ed}
    lis = [x + (tuple(e for e, idx in autres.items() if x[3] in idx),) for x in res[ed]]
    return {"ed": ed, "changes": [x for x in lis if x[2] not in KTIV_SEUL],
            "ktiv": [x for x in lis if x[2] in KTIV_SEUL]}


def dire_ecarts(l, n=8):
    """« X » pour « Y » (nature, leçon de …) · …"""
    out = []
    for p, e, nat, _, *mel in l[:n]:
        m = mel[0] if mel else ()
        out.append(f"« {p} » pour « {e} » ({nat}"
                   + (f" ; c'est la graphie de {'/'.join(m)} : deux éditions mêlées dans le séif" if m else "")
                   + ")")
    return " · ".join(out) + (f" · … et {len(l) - n} autre(s)" if len(l) > n else "")


# --------------------------------------------------------------------- unités

class Ref:
    """Les éditions de référence d'un siman, séif par séif (R1, R2, R3).
      seifs[i]  : {consonnes : [éditions qui donnent cette leçon]}
      mots[i]   : les mots du séif i+1 de l'édition par défaut
      statut[i] : {édition admise : [sort de chaque mot de mots[i] dans elle]} (`statuts`)
      omis[i]   : {édition admise : [suites d'indices de mots[i] qu'elle OMET]}
      dep[i]    : {édition admise : [suites qu'elle porte DÉPLACÉES dans le séif]}
      ratio[i]  : {édition : (ressemblance au séif, (séif voisin, ressemblance) | None)}
      ecartees  : [(séif, édition, ressemblance, voisin)] — R2"""

    def __init__(self, eds):
        self.defaut, self.alts, self.ignorees = references(eds)
        D = self.D = court(self.defaut["titre"]) if self.defaut else None
        self.nom_alts = [court(e["titre"]) for e in self.alts]
        self.chap, self.seifs, self.bruts = {"": []}, [], []
        self.chap_brut = {}      # consonnes du chapeau -> son html (garde ktiv, tour 4)
        self.mots, self.omis, self.ratio, self.ecartees = [], [], [], []
        self.statut, self.dep, self.ditto, self.attrib = [], [], [], []
        if not self.defaut:
            return
        sd = self.defaut["seifim"]
        nseifs = max([i + 1 for i, s in enumerate(sd) if consonants(s)] or [0])
        raws = []
        for i in range(nseifs):
            raw = sd[i]
            if i == 0:
                m = CHAPEAU.match(raw)
                if m:
                    self.chap[consonants(m.group(0))] = [D]
                    self.chap_brut[consonants(m.group(0))] = m.group(0)
                    raw = CHAPEAU.sub('', raw)
            raws.append(raw)
        self.mots = [mots(r) for r in raws]
        for i, raw in enumerate(raws):
            c0 = consonants(raw)
            var, br, rat, om, stt, dep, dit, att = {}, {}, {}, {}, {}, {}, {}, {}
            if c0:
                var[c0] = [D]
                br[D] = raw
            for e in self.alts:
                if i >= len(e["seifim"]) or not consonants(e["seifim"][i]):
                    continue
                r = CHAPEAU.sub('', e["seifim"][i]) if i == 0 else e["seifim"][i]
                c = consonants(r)
                nom = court(e["titre"])
                ma = mots(r)
                ici = ressemblance(self.mots[i], ma) if c0 else 0.0
                vois = [(j + 1, ressemblance(self.mots[j], ma))
                        for j in range(nseifs) if j != i and self.mots[j]]
                v = max(vois, key=lambda x: x[1]) if vois else None
                rat[nom] = (ici, v)
                if ici < SEUIL_ALIGNEMENT or (v is not None and v[1] >= ici):
                    self.ecartees.append((i + 1, nom, ici, v))
                    continue
                var.setdefault(c, []).append(nom)
                br[nom] = r
                dit[nom] = {}
                stt[nom] = statuts(self.mots[i], ma, dit[nom])
                om[nom] = _suites(j for j, x in enumerate(stt[nom]) if x in OMIS)
                dep[nom] = _suites(j for j, x in enumerate(stt[nom]) if x == "déplacé")
                att[nom] = attributions(self.mots[i], ma)
            self.seifs.append(var)
            self.bruts.append(br)
            self.ratio.append(rat)
            self.omis.append(om)
            self.statut.append(stt)
            self.dep.append(dep)
            self.ditto.append(dit)
            self.attrib.append(att)

    def lacunaire(self, i, labs):
        """La leçon (éditions `labs`) du séif i+1 perd-elle un passage de
        l'édition par défaut ? Jamais si l'édition par défaut la donne aussi."""
        return bool(labs) and self.D not in labs and bool(self.omis[i].get(labs[0]))

    SORTS = {"porté": "le porte", "omis": "absent aussi", "déplacé": "porté ailleurs dans le séif",
             "leçon": "autre leçon", "répété": "absent aussi (copie d'un voisin : dittographie ou assimilation)"}

    def mention(self, i, run):
        """Ce que Torat Emet 357 fait des mots `run` du séif i+1 de l'édition par
        défaut, mot par mot (`statuts`) : « absent aussi de Torat Emet 357 »,
        « Torat Emet 357 le porte », « … le porte ailleurs dans le séif
        (déplacé) », « … y a une autre leçon », ou le décompte s'ils diffèrent.
        Le tour 2 n'avait que « le porte » et « absent » : un mot SUBSTITUÉ y
        devenait « porté », et un passage DÉPLACÉ « absent »."""
        out = []
        for nom in self.nom_alts:
            if nom not in self.ratio[i]:
                out.append(f"{nom} n'a pas ce séif")
            elif nom not in self.statut[i]:
                out.append(f"{nom} non alignée sur ce séif ({self.ratio[i][nom][0]:.2f})")
            else:
                st = [self.statut[i][nom][j] for j in run]
                if all(x == "omis" for x in st):
                    out.append(f"absent aussi de {nom}")
                elif all(x == "répété" for x in st):
                    reps = sorted({self.ditto[i][nom][j] for j in run if j in self.ditto[i][nom]})
                    out.append(f"absent aussi de {nom}, qui écrit à sa place "
                               + " ; ".join(dire_copie(r) for r in reps))
                elif all(x == "porté" for x in st):
                    out.append(f"{nom} le porte")
                elif all(x == "déplacé" for x in st):
                    out.append(f"{nom} le porte ailleurs dans le séif (déplacé)")
                elif all(x == "leçon" for x in st):
                    out.append(f"{nom} y a une autre leçon")
                else:
                    c = {}
                    for x in st:
                        c[x] = c.get(x, 0) + 1
                    out.append(f"{nom}, mot par mot : " + ", ".join(
                        f"{v} {self.SORTS[k]}" for k, v in c.items())
                        + (" — absent en partie de " + nom + " aussi"
                           if "omis" in c or "répété" in c else ""))
        return " · ".join(out) or "aucune autre édition de référence"


def apparier(P, unites_, ref):
    """Programmation dynamique : la page P (consonnes) est-elle EXACTEMENT la
    suite des unités, chaque unité prise dans l'une quelconque de ses leçons ?
    Rend, par unité, (éditions retenues, début, fin) — ou None. À position égale,
    le chemin qui prend le MOINS de leçons lacunaires (R3), puis le moins de séifs
    hors de l'édition par défaut, l'emporte. L'unité 0 est le chapeau."""
    etats = {0: ((0, 0), ())}
    for iu, u in enumerate(unites_):
        if not u:
            # Un séif sans texte dans aucune édition de référence (jamais mesuré) :
            # rien n'y est exigé de la page.
            etats = {pos: (cout, chem + (((), pos, pos),)) for pos, (cout, chem) in etats.items()}
            continue
        nouv = {}
        for pos, (cout, chem) in etats.items():
            for k, labs in u.items():
                if P.startswith(k, pos):
                    np_ = pos + len(k)
                    lac = iu > 0 and ref.lacunaire(iu - 1, labs)
                    hors = bool(labs) and ref.D not in labs
                    c2 = (cout[0] + lac, cout[1] + hors)
                    if np_ not in nouv or c2 < nouv[np_][0]:
                        nouv[np_] = (c2, chem + ((tuple(labs), pos, np_),))
        etats = nouv
        if not etats:
            return None
    r = etats.get(len(P))
    return r[1] if r else None


def _omission_retenue(ref, i, labs):
    """R3 — un séif retenu hors de l'édition par défaut : rend None, ou le détail
    de ce que l'édition par défaut porte et que la page (= labs[0]) n'a pas."""
    if not ref.lacunaire(i, labs):
        return None
    return {"runs": [(texte_de(ref.mots[i], r), len(r), ref.mention(i, r))
                     for r in ref.omis[i][labs[0]]]}


def localiser(P, ref, brut_page):
    """La page diverge : où, et de quelle édition est-elle la plus proche ?
    Rend une liste de (séif, statut, éditions, détail)."""
    chap, seifs, bruts = ref.chap, ref.seifs, ref.bruts
    SP = squelette(P)
    smap = [i for i, c in enumerate(P) if c not in "יו"]   # squelette → consonnes
    pm = mots(brut_page)

    def exact(i, deb, fin, k):
        lo = smap[deb - 1] + 1 if deb > 0 else 0
        hi = smap[deb] if deb < len(SP) else len(P)
        flo = smap[fin - 1] + 1 if fin > 0 else 0
        fhi = smap[fin] if fin < len(SP) else len(P)
        for c, labs in sorted(seifs[i].items(), key=lambda x: ref.D not in x[1]):
            if squelette(c) != k:
                continue
            for s in range(lo, hi + 1):
                if P.startswith(c, s) and flo <= s + len(c) <= fhi:
                    return labs
        return None

    sq_seifs = []
    for u in seifs:
        d = {}
        for c, labs in u.items():
            d.setdefault(squelette(c), [])
            d[squelette(c)] += [l for l in labs if l not in d[squelette(c)]]
        sq_seifs.append(d)
    pos, out = 0, []
    chaps = sorted((squelette(c) for c in chap if c), key=len, reverse=True)
    for k in chaps:
        if SP.startswith(k, 0):
            pos = len(k)
            # Garde ktiv (tour 4) : le chapeau reconnu AU SQUELETTE doit l'être aux
            # consonnes. Sinon la page sortait DIVERGENTE sans qu'une ligne dise où.
            if not any(squelette(c) == k and P.startswith(c) for c in chap if c):
                Wp = [m for m in pm if m[3] < pos]
                for c, b in ref.chap_brut.items():
                    if squelette(c) == k:
                        lk = garde_ktiv(Wp, mots(b))
                        gk = {"ed": ref.D, "changes": [x + ((),) for x in lk if x[2] not in KTIV_SEUL],
                              "ktiv": [x + ((),) for x in lk if x[2] in KTIV_SEUL],
                              "page_mots": mots_autour(brut_page, 0)}
                        out.append((0, "MOT CHANGÉ" if gk["changes"] or not gk["ktiv"] else "KTIV",
                                    (ref.D,), gk))
                        break
            break
    else:
        # Un chapeau RÉCRIT : rapporté à part, non fondu dans le séif א.
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
        if not u:          # séif sans texte dans aucune édition de référence
            i += 1
            continue

        def suit(k):
            np_ = pos + len(k)
            if i + 1 >= N:
                return np_ == len(SP)
            return any(SP.startswith(k2, np_) for k2 in sq_seifs[i + 1])
        ok = [(k, labs) for k, labs in u.items() if k and SP.startswith(k, pos)]
        if ok:
            bons = [x for x in ok if suit(x[0])]
            # À longueur égale, l'édition par défaut d'abord (R3).
            k, labs = max(bons or ok, key=lambda x: (len(x[0]), ref.D in x[1]))
            # Une leçon plus COURTE peut n'être qu'un PRÉFIXE de la page : si le
            # début du séif suivant se lit plus loin et qu'une autre leçon de ce
            # séif est plus proche du passage entier, l'excédent appartient à ce
            # séif, qui diverge.
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
                ex = exact(i, pos, pos + len(k), k)
                om = _omission_retenue(ref, i, tuple(ex if ex is not None else labs))
                Wp = [m for m in pm if pos <= m[3] < pos + len(k)]
                if om:
                    om["ktiv"] = ex is None
                    if ex is None:
                        om["garde"] = garde_seif(ref, i, Wp, list(labs))
                    out.append((i + 1, "OMISSION", tuple(ex if ex is not None else labs), om))
                elif ex is not None:
                    out.append((i + 1, "RETENU", tuple(ex), None))
                else:
                    # LA GARDE KTIV (tour 4) : le squelette est celui d'une leçon, les
                    # consonnes non. Chaque mot en cause est nommé, et un yod/vav ÉCHANGÉ
                    # (« כוס » / « כיס ») n'est pas appelé du ktiv.
                    gk = garde_seif(ref, i, Wp, list(labs))
                    gk["page_mots"] = mots_autour(brut_page, pos)
                    out.append((i + 1, "MOT CHANGÉ" if gk["changes"] or not gk["ktiv"] else "KTIV",
                                (gk["ed"],), gk))
                pos += len(k)
                i += 1
                continue
        fin, j = len(SP), N
        for jj in range(i + 1, N):
            q = [SP.find(k2[:ANCRE], pos) for k2 in sq_seifs[jj] if k2]
            q = [x for x in q if x >= 0]
            if q:
                fin, j = min(q), jj
                break
        seg = SP[pos:fin]
        cands = sorted(((proximite(seg, k), k, labs) for k, labs in u.items()),
                       key=lambda x: (-x[0], ref.D not in x[2]))
        if not seg:
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
            omis = [(texte_de(ref.mots[i], r), len(r), ref.mention(i, r))
                    for r in omissions(ref.mots[i], seg_mots)]
            # Garde ktiv (tour 4) : les mots appariés à l'édition la plus proche dont un
            # yod/vav est CHANGÉ — invisibles au squelette, donc à « 1re divergence ».
            # Tour 5 : un mot n'est donné pour une VARIANTE que s'il est ANCRÉ, au sein
            # d'un bloc égal de difflib d'ANCRAGE_MIN mots ou plus ; un appariement
            # ISOLÉ (bloc de 1 ou 2 mots) est listé à part, « à contrôler ». Entre deux
            # textes sans rapport, difflib apparie des mots isolés : au 87:6 « אסור »
            # d'une phrase répondait à « אוסר » d'une autre, au 112:1 « ביתו » de « לבני
            # ביתו » à « ובית » de « ובית יוסף », et la porte les donnait pour des
            # variantes. Un seuil de RESSEMBLANCE du séif ne sépare pas : un séif fondu
            # avec les suivants ressemble peu (113:5, 0,30) et porte des variantes
            # réelles, ancrées dans seize mots communs (« אפלו » / « ואפילו »).
            ed_m = mots(bruts[i].get(ed, ""))
            r_mots = ressemblance(seg_mots, ed_m)
            blocs = {}
            chg = [x for x in garde_ktiv(seg_mots, ed_m, egaux_seuls=True, blocs=blocs)
                   if x[2] not in KTIV_SEUL]
            isoles = [x for x in chg if blocs.get(x[3], 0) < ANCRAGE_MIN]
            chg = [x for x in chg if blocs.get(x[3], 0) >= ANCRAGE_MIN]
            out.append((i + 1, "DIVERGENT", tuple(labs), {
                "proximite": sc, "autres": autres, "p": p,
                "page_mid": seg[p:len(seg) - s], "ed_mid": k[p:len(k) - s],
                "page_mots": mots_autour(brut_page, pos + p),
                "ed_mots": mots_autour(bruts[i].get(ed, ""), p),
                "omis": omis, "changes": chg, "isoles": isoles, "r_mots": r_mots,
            }))
        for jj in range(i + 1, j):
            if sq_seifs[jj]:
                out.append((jj + 1, "NON RETROUVÉ", (), None))
        pos, i = fin, j
    if pos < len(SP):
        out.append((None, "SURPLUS", (), {"long": len(SP) - pos,
                                          "page_mots": mots_autour(brut_page, pos)}))
    return out


def retenue(chemin_, D):
    """L'édition retenue pour chaque séif, et son résumé. Si une même édition
    donne TOUS les séifs, c'est elle (l'édition par défaut si elle en est) ;
    sinon chaque séif prend l'édition par défaut s'il la donne, l'autre sinon."""
    seifs = [list(l) for l in chemin_ if l]
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

def page_source(path):
    html_ = open(path, encoding="utf-8").read()
    b = re.findall(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>', html_, re.S)
    brut = " ".join(b)
    return len(b), consonants(brut), brut


def chemin(n, suf):
    return os.path.join(SECTION, f"siman-{n}", f"niveau-1-base{suf}.html")


def juger(cons, brut, ref):
    """(verdict, éditions retenues par séif, rapport de localisation). Une page
    qui est, séif par séif, la copie EXACTE d'une leçon de référence passe — sauf
    si un séif pris hors de l'édition par défaut y perd un passage que celle-ci
    porte (R3) : la page est alors DIVERGENTE et le rapport nomme l'omission."""
    ch = apparier(cons, [ref.chap] + ref.seifs, ref)
    if ch is not None:
        ch = ch[1:]
        loc, omis = [], False
        for i, (labs, a, b) in enumerate(ch):
            om = _omission_retenue(ref, i, labs)
            omis = omis or bool(om)
            loc.append((i + 1, "OMISSION", labs, om) if om else (i + 1, "RETENU", labs, None))
        if not omis:
            return "IDENTIQUE", [x[0] for x in ch], None
        return "DIVERGENCE", None, loc
    return "DIVERGENCE", None, localiser(cons, ref, brut)


def notes_attribution(ref, i, ed):
    """Tour 4 — ce que dit la sortie d'un séif (i, base 0) retenu dans l'édition `ed`
    quand celle-ci attribue une source autrement que l'édition par défaut."""
    out = []
    for idx, nat, f in ref.attrib[i].get(ed, []):
        t = texte_de(ref.mots[i], idx)
        if f:
            out.append(f"source attribuée autrement ({ed}) : « {t} » y est rattachée à une autre "
                       f"proposition ({f} mot{'s' if f > 1 else ''} franchi{'s' if f > 1 else ''} "
                       f"par rapport à {ref.D})")
        else:
            out.append(f"source attribuée autrement ({ed}) : « {t} » — {ed} en écrit les noms dans "
                       f"un autre ordre")
    return out


def un_siman(n, bref, rafraichir, stats):
    """Rend True (conforme) / False (divergent) — ou None si rien n'a été
    confronté (aucune page, ou siman non atteint)."""
    presentes = [(lang, suf) for lang, suf in LANGS if os.path.exists(chemin(n, suf))]
    if not presentes:
        # Rien à confronter, et ce n'est ni « conforme » ni « divergent » : une
        # copie lancée hors du dépôt, ou un siman qui n'existe pas. On ne va pas
        # sur Sefaria.
        r = f"aucune page niveau-1-base sous {os.path.join(SECTION, f'siman-{n}')}"
        print(f"  siman {n:3d} : NON CONFRONTÉ — {r}")
        stats["sans_page"].append((n, r))
        return None
    src = fetch(n, rafraichir)
    if src is None:
        print(f"  siman {n:3d} : NON ATTEINT — {RAISONS.get(n)}")
        stats["non_atteints"].append((n, RAISONS.get(n)))
        return None
    if src.get("lacune"):
        # Les deux API disent que Sefaria n'a pas ce siman. Au 169, l'édition
        # par défaut fond le texte dans le 168 (son chapeau s'intitule
        # « קסח-קסט »). La page doit être une passerelle : AUCUN bloc text-source.
        stats["simanim"] += 1
        if not bref:
            print(f"\n=== Siman {n} — aucun séif sur Sefaria, dans aucune édition "
                  f"(lacune confirmée par api/v3 et api/texts ; page-passerelle attendue) ===")
        ok, nbs = True, []
        for lang, suf in LANGS:
            p = chemin(n, suf)
            if not os.path.exists(p):
                print(f"  {lang}: FICHIER ABSENT {p}")
                stats["fichiers_absents"].append((n, lang))
                ok = False
                continue
            nb, _, _ = page_source(p)
            stats["pages"] += 1
            bon = (nb == 0)
            nbs.append(str(nb))
            v = "PASSERELLE" if bon else "PASSERELLE FAUSSE"
            stats["pages_verdict"][v] = stats["pages_verdict"].get(v, 0) + 1
            if not bref:
                print(f"  {lang}: {nb} blocs text-source | "
                      f"{'✅ aucun séif prétendu' if bon else '❌ la page cite un séif que la source ne donne pas'}")
            ok = ok and bon
        if bref:
            print(f"  siman {n:3d} : lacune de Sefaria · blocs {'/'.join(nbs):>8s} · "
                  f"{'✅ page-passerelle' if ok else '❌ la page cite un séif que la source ne donne pas'}")
        stats["verdict"].setdefault("PASSERELLE" if ok else "DIVERGENCE", []).append(n)
        return ok

    ref = Ref(src["editions"])
    if ref.defaut is None:
        RAISONS[n] = ("édition par défaut indécidable : " + " · ".join(
            f"{court(e['titre'])} {e['priorite']}" for e in src["editions"]))[:200]
        print(f"  siman {n:3d} : NON ATTEINT — {RAISONS[n]}")
        stats["non_atteints"].append((n, RAISONS[n]))
        return None
    D = ref.D
    nseifs = sum(1 for u in ref.seifs if u)
    stats["simanim"] += 1
    stats["seifim"] += nseifs
    stats["defaut"][D] = stats["defaut"].get(D, 0) + 1
    for e in [ref.defaut] + ref.alts:
        if consonants("".join(e["seifim"])):
            k = court(e["titre"])
            stats["editions_lues"][k] = stats["editions_lues"].get(k, 0) + 1
    for e in ref.ignorees:
        k = court(e["titre"])
        stats["ignorees"][k] = stats["ignorees"].get(k, 0) + 1
    for i, rat in enumerate(ref.ratio):
        for nom, (r, v) in rat.items():
            st = stats["alignement"].setdefault(nom, [0, 0, 1.0, 9.9])
            st[0] += 1
            if nom in ref.omis[i]:
                st[1] += 1
                st[2] = min(st[2], r)
                st[3] = min(st[3], r - v[1] if v else r)
            if ref.omis[i].get(nom):
                stats["lacunes_alt"].append((n, i + 1, nom, [len(x) for x in ref.omis[i][nom]]))
            if ref.dep[i].get(nom):
                stats["deplaces_alt"].append((n, i + 1, nom))
            if ref.attrib[i].get(nom):
                stats["attrib_alt"].append((n, i + 1, nom, ref.attrib[i][nom]))
            for j, rep_ in ref.ditto[i].get(nom, {}).items():
                stats["ditto_alt"].append((n, i + 1, nom, ref.mots[i][j][1], rep_))
    for s_, nom, r, v in ref.ecartees:
        stats["ecartees"].append((n, s_, nom, r, v))

    ok = True
    cons_par_langue, nb_par_langue, res = {}, {}, {}
    for lang, suf in LANGS:
        p = chemin(n, suf)
        if not os.path.exists(p):
            stats["fichiers_absents"].append((n, lang))
            ok = False
            continue
        nb, cons, brut = page_source(p)
        stats["pages"] += 1
        cons_par_langue[lang], nb_par_langue[lang] = cons, nb
        verdict, ch, loc = juger(cons, brut, ref)
        res[lang] = (verdict, ch, loc)
        stats["pages_verdict"][verdict] = stats["pages_verdict"].get(verdict, 0) + 1
        if verdict == "IDENTIQUE":
            for l in retenue(ch, D)[1]:
                stats["seifs_par_edition"][l] = stats["seifs_par_edition"].get(l, 0) + 1
            for i, labs in enumerate(ch, 1):
                if labs and D not in labs:
                    stats["seifs_hors_defaut"].append((n, lang, i, labs[0]))
                    if ref.attrib[i - 1].get(labs[0]):
                        stats["attrib_pages"].append((n, lang, i, labs[0]))
            continue
        ok = False
        for s_, st, labs, d in loc:
            cle = st
            if st == "RETENU":
                cle = "RETENU" if D in labs else "RETENU hors défaut"
                if cle == "RETENU hors défaut":
                    stats["div_hors_defaut"].append((n, lang, s_, labs[0]))
                    if ref.attrib[s_ - 1].get(labs[0]):
                        stats["attrib_pages"].append((n, lang, s_, labs[0]))
            if st in ("KTIV", "MOT CHANGÉ"):
                stats["garde"].append((n, lang, s_, st, d["ed"], d["changes"], d["ktiv"]))
            if st == "DIVERGENT" and d.get("changes"):
                stats["garde_div"].append((n, lang, s_, d["changes"]))
            if st == "DIVERGENT" and d.get("isoles"):
                stats["garde_div_iso"].append((n, lang, s_, d["isoles"], d["r_mots"]))
            stats["div_seifs"][cle] = stats["div_seifs"].get(cle, 0) + 1
            if st == "DIVERGENT":
                stats["div_proches"][labs[0]] = stats["div_proches"].get(labs[0], 0) + 1
                for t, L, m in d["omis"]:
                    stats["omis_div"].append((n, lang, s_, L, "absent aussi de " in m))
            if st == "OMISSION":
                stats["omissions"].append((n, lang, s_, labs[0], [t for t, _, _ in d["runs"]]))
    parite = len(set(cons_par_langue.values())) <= 1
    if not parite:
        ok = False
    stats["verdict"].setdefault("CONFORME" if ok else "DIVERGENCE", []).append(n)

    if bref:
        blocs = "/".join(str(nb_par_langue.get(l, "—")) for l, _ in LANGS)
        eds_txt = sorted({retenue(v[1], D)[0] for v in res.values() if v[1] is not None})
        extra = f" · {' / '.join(eds_txt)}" if eds_txt else ""
        hors = sorted({f"{i}={c}" for v in res.values() if v[1] is not None
                       for i, c in enumerate(retenue(v[1], D)[1], 1) if c != D})
        if hors:
            extra += f" (hors {D} : {' '.join(hors)})"
        divs = sorted({s for v in res.values() if v[2] for s, st, _, _ in v[2]
                       if st != "RETENU" and s is not None})
        if divs:
            proches = sorted({labs[0] for v in res.values() if v[2]
                              for _, st, labs, _ in v[2] if st == "DIVERGENT" and labs})
            extra += (f" · séifs en écart : {','.join(str(x) if x else 'chapeau' for x in divs)} — plus proche : "
                      f"{' / '.join(proches) or '—'}")
            hors = sorted({f"{s}={labs[0]}" for v in res.values() if v[2]
                           for s, st, labs, _ in v[2] if st == "RETENU" and D not in labs})
            if hors:
                extra += f" · fidèles à une autre édition : {' '.join(hors)}"
        omis = sorted({s for v in res.values() if v[2] for s, st, _, _ in v[2] if st == "OMISSION"})
        if omis:
            extra += f" · OMISSION (R3) au séif {','.join(map(str, omis))}"
        chg = sorted({s for v in res.values() if v[2] for s, st, _, _ in v[2] if st == "MOT CHANGÉ"})
        if chg:
            extra += f" · MOT CHANGÉ (yod/vav) : {','.join(str(x) if x else 'chapeau' for x in chg)}"
        att = sorted({f"{i}={c}" for v in res.values() if v[1] is not None
                      for i, c in enumerate(retenue(v[1], D)[1], 1) if c != D and ref.attrib[i - 1].get(c)}
                     | {f"{s}={labs[0]}" for v in res.values() if v[2] for s, st, labs, _ in v[2]
                        if st == "RETENU" and D not in labs and ref.attrib[s - 1].get(labs[0])})
        if att:
            extra += f" · source attribuée autrement : {' '.join(att)}"
        if ref.ecartees:
            extra += " · non alignée (R2) : " + " ".join(f"{s}={nom}" for s, nom, _, _ in ref.ecartees)
        absents = [l for l, suf in LANGS if not os.path.exists(chemin(n, suf))]
        if absents:
            extra += f" · FICHIER ABSENT : {'/'.join(absents)}"
        print(f"  siman {n:3d} : {nseifs:2d} séifim · blocs {blocs:>8s} · "
              f"texte {'✅' if res and all(v[0] == 'IDENTIQUE' for v in res.values()) else '❌'}"
              f"{'' if parite else ' ⚠️ parité'}{extra}")
        return ok

    lues = " · ".join(f"{court(e['titre'])} ({sum(1 for s in e['seifim'] if consonants(s))})"
                      for e in [ref.defaut] + ref.alts)
    print(f"\n=== Siman {n} — Yoré Déa : {nseifs} séifim dans l'édition par défaut ===")
    t, src = DATES.get(n, (None, "?"))
    print(f"  éditions de référence (séifs non vides) : {lues} — par défaut : {D} — texte Sefaria "
          + (f"{'lu dans le cache, téléchargé' if src == 'cache' else 'téléchargé pendant ce passage'}"
             f" le {t:%Y-%m-%d %H:%M} UTC ({age_jours(t):.1f} j)" if t else src))
    if ref.ignorees:
        print(f"  servies et IGNORÉES (R1 — ni par défaut, ni {REFERENCE_ALT}) : " + " · ".join(
            f"{court(e['titre'])} ({sum(1 for s in e['seifim'] if consonants(s))})" for e in ref.ignorees))
    for s_, nom, r, v in ref.ecartees:
        print(f"  ⚠️  R2 : {nom} séif {s_} NON ALIGNÉE sur {D} (ressemblance {r:.2f}"
              + (f", séif {v[0]} : {v[1]:.2f}" if v else "")
              + f" ; il faut ≥ {SEUIL_ALIGNEMENT} et plus qu'à tout autre séif du siman) — écartée pour ce séif")
    for lang, suf in LANGS:
        if lang not in res:
            print(f"  {lang}: FICHIER ABSENT {chemin(n, suf)}")
            continue
        verdict, ch, loc = res[lang]
        nb = nb_par_langue[lang]
        if verdict == "IDENTIQUE":
            r, choix = retenue(ch, D)
            print(f"  {lang}: {nb} blocs text-source | texte source : ✅ IDENTIQUE à {r}")
            hors = [(i, c) for i, c in enumerate(choix, 1) if c != D]
            if hors:
                print(f"      séifs pris HORS de l'édition par défaut ({D}), et l'édition retenue : "
                      + " ".join(f"{i}={c}" for i, c in hors))
            for i, c in hors:
                for t in notes_attribution(ref, i - 1, c):
                    print(f"      séif {i} : {t}")
            continue
        print(f"  {lang}: {nb} blocs text-source | texte source : ❌ DIVERGENCE "
              f"(contre les éditions de référence)")
        ret = [(s, labs) for s, st, labs, _ in loc if st == "RETENU"]
        if ret:
            hors = [(s, labs) for s, labs in ret if D not in labs]
            print(f"      {len(ret)} séif(s) fidèle(s) à une édition de référence"
                  + (f", dont {len(hors)} à {'/'.join(ref.nom_alts) or 'une autre'} seulement : "
                     + " ".join(f"{s}={labs[0]}" for s, labs in hors) if hors else ""))
            for s, labs in hors:
                for t in notes_attribution(ref, s - 1, labs[0]):
                    print(f"      séif {s} : {t}")
        for s, st, labs, d in loc:
            if st == "RETENU":
                continue
            if st == "SURPLUS":
                print(f"      SURPLUS : {d['long']} consonnes après le dernier séif — « {d['page_mots']} »")
            elif st == "CHAPEAU DIVERGENT":
                print(f"      CHAPEAU du siman récrit : page « {d['page_mid'][:40] or '∅'} » / "
                      f"« {d['ed_mid'][:40] or '∅'} » (squelette) — {d['page_mots']}")
            elif st == "KTIV":
                print(f"      {'chapeau' if s == 0 else f'séif {s}'} : KTIV — égal à {d['ed']} à des yod/vav AJOUTÉS ou ôtés à "
                      f"l'intérieur des mots près (refusé : cette porte exige les consonnes) ; "
                      f"page / {d['ed']} : {dire_ecarts(d['ktiv'])}")
            elif st == "MOT CHANGÉ":
                print(f"      {'chapeau' if s == 0 else f'séif {s}'} : MOT CHANGÉ — le squelette est celui de {d['ed']}, mais un "
                      f"yod/vav y change un mot (pas du ktiv) ; page / {d['ed']} : "
                      + (dire_ecarts(d["changes"]) or f"écart non localisé mot à mot — {d['page_mots']}"))
                if d["ktiv"]:
                    print(f"          et au ktiv près : {dire_ecarts(d['ktiv'])}")
            elif st in ("NON RETROUVÉ", "SANS TEXTE"):
                print(f"      séif {s} : {st} — son début ne se lit nulle part après le séif "
                      f"précédent (absent, fondu, ou altéré dès ses premiers mots)")
            elif st == "OMISSION":
                g_ = d.get("garde") or {}
                print(f"      séif {s} : OMISSION (R3) — la page est {'+'.join(labs)} "
                      f"{('à un yod/vav changé près' if g_.get('changes') else 'au ktiv près') if d.get('ktiv') else 'mot pour mot'}"
                      f", mais {D} porte ce qu'elle n'a pas :")
                for t, L, m in d["runs"]:
                    print(f"          « {t} » ({L} mot{'s' if L > 1 else ''}) — {m}")
                if g_.get("changes") or g_.get("ktiv"):
                    print(f"          écarts de yod/vav, page / {g_['ed']} : "
                          f"{dire_ecarts(g_['changes'] + g_['ktiv'])}")
            else:
                print(f"      séif {s} : DIVERGENT — édition la plus proche : {'+'.join(labs)} "
                      f"(ressemblance {d['proximite']:.2f}{'; ' + d['autres'] if d['autres'] else ''})")
                if len(d["page_mid"]) <= 40 and len(d["ed_mid"]) <= 40:
                    print(f"          écart (squelette) : page « {d['page_mid'] or '∅'} » / "
                          f"{labs[0]} « {d['ed_mid'] or '∅'} »")
                else:
                    print(f"          1re divergence @{d['p']} du séif ; écart de "
                          f"{len(d['page_mid'])} (page) / {len(d['ed_mid'])} ({labs[0]}) consonnes")
                print(f"          page   : {d['page_mots']}")
                print(f"          {labs[0][:15]:15s}: {d['ed_mots']}")
                for t, L, m in d["omis"][:8]:
                    print(f"          mots de {D} sans contrepartie dans la page : « {t} » "
                          f"({L} mot{'s' if L > 1 else ''}) — {m}")
                if len(d["omis"]) > 8:
                    print(f"          … et {len(d['omis']) - 8} autre(s) passage(s) sans contrepartie")
                if d.get("changes"):
                    print(f"          mots dont un yod/vav est changé (pas du ktiv), ancrés dans un passage commun "
                          f"de {ANCRAGE_MIN} mots ou plus, page / {labs[0]} : {dire_ecarts(d['changes'])}")
                if d.get("isoles"):
                    print(f"          appariements ISOLÉS à un yod/vav près (moins de {ANCRAGE_MIN} mots appariés de "
                          f"suite ; ressemblance mot à mot du séif {d['r_mots']:.2f}) — À CONTRÔLER, difflib apparie "
                          f"aussi des mots sans rapport : {dire_ecarts(d['isoles'])}")
    if not parite:
        print("  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE")
    elif cons_par_langue:
        print("  parité FR/HE/EN du texte source : ✅ identique")
    return ok


def dire_cache(dates, ou):
    """Imprime de quand date le texte de Sefaria confronté (tour 4), et avertit au-delà
    de AGE_MAX_JOURS. `dates` : {siman: date UTC}."""
    if not dates:
        return
    vmin, vmax = min(dates.values()), max(dates.values())
    amax = age_jours(vmin)
    print(f"Cache Sefaria ({ou}) : {len(dates)} siman(im) lus dans le cache, téléchargés du "
          f"{vmin:%Y-%m-%d %H:%M} au {vmax:%Y-%m-%d %H:%M} UTC — âge maximal {amax:.1f} jour(s) "
          f"(limite {AGE_MAX_JOURS})")
    if amax > AGE_MAX_JOURS:
        vieux = sorted(n for n, t in dates.items() if age_jours(t) > AGE_MAX_JOURS)
        print(f"⚠️  AVERTISSEMENT — CACHE DE PLUS DE {AGE_MAX_JOURS} JOURS ({len(vieux)} siman(im) : "
              f"{' '.join(map(str, vieux[:20]))}{' …' if len(vieux) > 20 else ''}) : la porte compare "
              f"les pages à un INSTANTANÉ de Sefaria vieux de {amax:.0f} jours, et Sefaria corrige son "
              f"texte. Relancer avec --rafraichir avant toute publication (avertissement, pas un code "
              f"d'erreur).")


def main(argv):
    bref = "--bref" in argv
    rafraichir = "--rafraichir" in argv
    nums = [int(a) for a in argv if a.isdigit()]
    if "--tous" in argv:
        nums = (sorted(int(d.split("-")[1]) for d in os.listdir(SECTION)
                       if d.startswith("siman-") and d.split("-")[1].isdigit())
                if os.path.isdir(SECTION) else [])
    elif not nums:
        print(__doc__.split("\n\n")[0] + "\n\n" + __doc__.split("\n\n")[1]); return 2
    stats = {"simanim": 0, "seifim": 0, "pages": 0, "non_atteints": [], "sans_page": [],
             "verdict": {}, "pages_verdict": {}, "seifs_par_edition": {},
             "seifs_hors_defaut": [], "editions_lues": {}, "ignorees": {}, "defaut": {},
             "alignement": {}, "ecartees": [], "lacunes_alt": [], "deplaces_alt": [], "omissions": [],
             "omis_div": [], "fichiers_absents": [], "div_seifs": {}, "div_proches": {},
             "div_hors_defaut": [], "attrib_alt": [], "ditto_alt": [], "attrib_pages": [],
             "garde": [], "garde_div": [], "garde_div_iso": []}
    print(f"=== Texte source de Yoré Déa vs l'édition par défaut de Sefaria (et {REFERENCE_ALT} "
          f"pour les leçons) — {len(nums)} siman(im) · ROOT {ROOT} ===")
    if rafraichir:
        print("Cache Sefaria ignoré (--rafraichir) : chaque siman est retéléchargé.")
    else:
        avant = {}
        for n in nums:
            if any(os.path.exists(chemin(n, suf)) for _, suf in LANGS):
                d = lire_cache(n)
                if d is not None:
                    avant[n] = _date_de(d)
        dire_cache(avant, "en tête, avant lecture")
    faux = []
    for n in nums:
        r = un_siman(n, bref, rafraichir, stats)
        if r is False:
            faux.append(n)

    print(f"\nCONFRONTÉ : {stats['simanim']} siman(im) · {stats['seifim']} séifim · "
          f"{stats['pages']} pages")
    if stats["defaut"]:
        print("Édition par défaut : " + " · ".join(f"{k} ({v} simanim)" for k, v in stats["defaut"].items()))
    if stats["editions_lues"]:
        print("Éditions de référence lues (simanim où elles ont du texte) : " + " · ".join(
            f"{k} {v}" for k, v in sorted(stats["editions_lues"].items(), key=lambda x: -x[1])))
    if stats["ignorees"]:
        print("Éditions servies et IGNORÉES (R1, jamais une référence) : " + " · ".join(
            f"{k} ({v} simanim)" for k, v in sorted(stats["ignorees"].items(), key=lambda x: -x[1])))
    for nom, (tot, ok_, mn, marge) in stats["alignement"].items():
        ec = [x for x in stats["ecartees"] if x[2] == nom]
        print(f"R2 — {nom} alignée sur {ok_} séif(s) sur {tot} (ressemblance min des alignés "
              f"{mn:.3f}, seuil {SEUIL_ALIGNEMENT} ; marge min sur les autres séifs du siman "
              f"{marge:.3f})" + (" ; écartés : " + " ".join(
                  f"{n}:{s} ({r:.2f}{f' < séif {v[0]} {v[1]:.2f}' if v and v[1] >= r else ''})"
                  for n, s, _, r, v in ec) if ec else ""))
    la = stats["lacunes_alt"]
    if la:
        par_ed = {}
        for n, s, nom, Ls in la:
            par_ed.setdefault(nom, []).append((n, s, Ls))
        for nom, l in par_ed.items():
            mots_ = [L for *_, Ls in l for L in Ls]
            print(f"R3 — leçons de {nom} qui perdent un passage de l'édition par défaut : "
                  f"{len(l)} séif(s), {len(mots_)} passage(s) ({sum(1 for L in mots_ if L >= 3)} de "
                  f"3 mots ou plus) — une page qui les recopie sort en 1")
    if stats["deplaces_alt"]:
        par_ed = {}
        for n, s, nom in stats["deplaces_alt"]:
            par_ed.setdefault(nom, []).append(f"{n}:{s}")
        for nom, l in par_ed.items():
            print(f"R3 — séifs où {nom} porte un passage de l'édition par défaut DÉPLACÉ dans le "
                  f"séif (leçon d'ordre, excusée) : {len(l)} — {' '.join(l)}")
    if stats["ditto_alt"]:
        print(f"R3 — COPIES D'UN VOISIN dans {REFERENCE_ALT} (dittographie ou assimilation, à la place d'un "
              f"mot de l'édition par défaut : une OMISSION, comptée ci-dessus) : {len(stats['ditto_alt'])} — "
              + " · ".join(f"{n}:{s} « {w} » ({r[0]} : {r[1] if r[0] == 'ASSIMILATION' else '« ' + r[1] + ' »'})"
                           for n, s, nom, w, r in stats["ditto_alt"]))
    if stats["attrib_alt"]:
        print(f"R3 — séifs où {REFERENCE_ALT} attribue une source AUTREMENT (leçon d'attribution : "
              f"excusée, NOMMÉE sur toute page qui la recopie) : {len(stats['attrib_alt'])} séif(s), "
              f"{sum(len(l) for *_, l in stats['attrib_alt'])} parenthèse(s) — "
              + " ".join(f"{n}:{s}" for n, s, *_ in stats["attrib_alt"]))
    if stats["pages_verdict"]:
        print("Pages par verdict : " + " · ".join(
            f"{k} {v}" for k, v in stats["pages_verdict"].items())
              + f" (total {sum(stats['pages_verdict'].values())} = {stats['pages']} pages lues)")
    if stats["seifs_par_edition"]:
        print("Séifs (× page) des pages conformes, par édition retenue : " + " · ".join(
            f"{k} {v}" for k, v in sorted(stats["seifs_par_edition"].items(), key=lambda x: -x[1])))
    h = stats["seifs_hors_defaut"]
    print(f"Séifs (× page) de pages conformes que SEULE Torat Emet donne, sans omission (leçon "
          f"excusée, R3) : {len(h)}" + ("" if not h else " — " + " ".join(
              f"{n}{g}:{i}" for n, g, i, e in h)))
    ap = stats["attrib_pages"]
    print(f"Séifs (× page) retenus dans {REFERENCE_ALT} où la source est attribuée autrement (nommés, "
          f"verdict inchangé) : {len(ap)}" + ("" if not ap else " — " + " ".join(
              f"{n}{g}:{i}" for n, g, i, e in ap)))
    o = stats["omissions"]
    print(f"OMISSIONS (R3) — séifs copiés de Torat Emet qui perdent un passage de l'édition par "
          f"défaut : {len(o)} (× page)" + ("" if not o else " — " + " ".join(
              f"{n}{g}:{s}" for n, g, s, *_ in o)))
    if stats["div_seifs"]:
        d = stats["div_seifs"]
        print(f"Dans les pages DIVERGENTES, séif par séif (× page) : "
              f"{d.get('RETENU', 0)} fidèles à l'édition par défaut · "
              f"{d.get('RETENU hors défaut', 0)} fidèles à Torat Emet seulement "
              f"(leçon, plus signalée) · "
              f"{d.get('OMISSION', 0)} copiés de Torat Emet avec omission (R3) · "
              f"{d.get('KTIV', 0)} au ktiv près · "
              f"{d.get('MOT CHANGÉ', 0)} à un yod/vav changé près (MOT CHANGÉ) · "
              f"{d.get('DIVERGENT', 0)} divergents des éditions de référence · "
              f"{d.get('NON RETROUVÉ', 0) + d.get('SANS TEXTE', 0)} non retrouvés · "
              f"{d.get('CHAPEAU DIVERGENT', 0)} chapeaux récrits · "
              f"{d.get('SURPLUS', 0)} surplus")
        if stats["div_hors_defaut"]:
            print("   fidèles à Torat Emet seulement : " + " ".join(
                f"{n}{g}:{s}" for n, g, s, e in stats["div_hors_defaut"]))
        if stats["div_proches"]:
            print("   séifs divergents par édition la plus proche : " + " · ".join(
                f"{k} {v}" for k, v in sorted(stats["div_proches"].items(), key=lambda x: -x[1])))
        od = stats["omis_div"]
        if od:
            print(f"   R3 dans les séifs divergents — passages de l'édition par défaut sans "
                  f"contrepartie dans la page : {len(od)} (× page), dont "
                  f"{sum(1 for *_, L, a in od if L >= 3)} de 3 mots ou plus ; "
                  f"{sum(1 for *_, a in od if a)} absents aussi de Torat Emet")
    if stats["garde"] or stats["garde_div"] or stats["garde_div_iso"]:
        ga = stats["garde"]
        nat = {}
        for *_, ch, kt in ga:
            for x in ch + kt:
                nat[x[2]] = nat.get(x[2], 0) + 1
        print(f"Garde ktiv — séifs (× page) égaux à une leçon au squelette près seulement : {len(ga)} = "
              f"{sum(1 for x in ga if x[3] == 'KTIV')} KTIV + {sum(1 for x in ga if x[3] == 'MOT CHANGÉ')} "
              f"MOT CHANGÉ (refusés l'un et l'autre, mots listés) ; mots en cause par nature : "
              + (" · ".join(f"{k} {v}" for k, v in sorted(nat.items(), key=lambda x: -x[1])) or "—"))
        gd = stats["garde_div"]
        if gd:
            print(f"   dans les séifs DIVERGENTS, mots dont un yod/vav est changé (pas du ktiv), ANCRÉS dans un "
                  f"passage commun de {ANCRAGE_MIN} mots ou plus : {sum(len(x[3]) for x in gd)} (× page), dans "
                  f"{len(gd)} séif(s) (× page)")
        gt = stats["garde_div_iso"]
        if gt:
            print(f"   appariements ISOLÉS (moins de {ANCRAGE_MIN} mots de suite), listés « à contrôler » : "
                  f"{sum(len(x[3]) for x in gt)} (× page), dans {len(gt)} séif(s) (× page)")
    if stats["fichiers_absents"]:
        print(f"FICHIERS ABSENTS ({len(stats['fichiers_absents'])}) : "
              + " ".join(f"{n}{g}" for n, g in stats["fichiers_absents"]))
    for k in ("CONFORME", "PASSERELLE", "DIVERGENCE"):
        if stats["verdict"].get(k):
            l = stats["verdict"][k]
            print(f"→ {k} : {len(l)} siman(im)" + (f" — {' '.join(map(str, l))}"
                                                  if k != "CONFORME" else ""))
    if stats["non_atteints"]:
        print(f"\nNON ATTEINTS ({len(stats['non_atteints'])}) — rien n'est conclu sur eux :")
        for n, r in stats["non_atteints"]:
            print(f"  siman {n} : {r}")
    if stats["sans_page"]:
        print(f"\nNON CONFRONTÉS faute de page ({len(stats['sans_page'])}) — rien n'est conclu sur eux :")
        for n, r in stats["sans_page"]:
            print(f"  siman {n} : {r}")
    lus = {n: t for n, (t, src) in DATES.items() if src == "cache"}
    tel = sorted(n for n, (t, src) in DATES.items() if src != "cache")
    if tel:
        print(f"Sefaria : {len(tel)} siman(im) téléchargé(s) pendant ce passage"
              + (f" ({' '.join(map(str, tel[:20]))}{' …' if len(tel) > 20 else ''})"))
    dire_cache(lus, "en pied")
    if stats["pages"] == 0:
        # Zéro page lue n'est ni conforme ni divergent : une copie de la porte
        # lancée hors du dépôt (ROOT se déduit de __file__) ne lit aucune page.
        print("❌ RIEN N'A ÉTÉ CONFRONTÉ — la porte ne conclut pas (code 3)."
              + ("" if os.path.isdir(SECTION) and nums else
                 f" Aucune page sous {SECTION} : copie lancée hors du dépôt ?"))
        return 3
    if faux:
        print("❌ VÉRIFICATION SOURCE : divergence(s) détectée(s) — NE PAS PUBLIER")
        return 1
    if stats["non_atteints"] or stats["sans_page"]:
        print("⚠️  conforme sur ce qui a été lu, mais des simanim n'ont pas été confrontés (code 3)")
        return 3
    print("✅ VÉRIFICATION SOURCE : tout est conforme")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
