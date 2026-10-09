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
argument, « tout est conforme » sur zéro siman.

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
      l'édition qu'api/texts sert par défaut : voir `_recouper`) et la Torat Emet
      NUMÉROTÉE (357), elles SEULES. Freeware et Wikisource ne sont jamais une
      référence : la porte les ignore et les NOMME quand elles sont servies.
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
leçon admise, « KTIV » s'il ne s'en écarte que par les matres lectionis (refusé :
cette porte exige les consonnes), « OMISSION » s'il est la leçon de Torat Emet 357
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
    porte sa FORME : 2 depuis le tour 3, qui garde la preuve du recoupement
    (`recoupement`) ; un fichier d'une autre forme, ou dont la preuve ne
    s'accorde pas à son contenu, est relu sur Sefaria (`_recoupe`). Il garde
    toutes les éditions servies, ignorées comprises, pour pouvoir les nommer ;
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
« KTIV ». Le recoupement ne protège que de ce que Sefaria peut SERVIR : un fichier
de cache forgé à la main et cohérent avec lui-même (preuve de recoupement
comprise) est cru — `--rafraichir` l'ignore. Et il rend la porte dépendante
d'api/texts : api/texts injoignable ou en désaccord, le siman n'est pas conclu
(3), même quand api/v3 répond juste.
"""
import sys, re, json, unicodedata, os, html, difflib
import urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = os.path.join(ROOT, "sources", "yoreh-deah")
LIVRE = "Shulchan_Arukh,_Yoreh_De%27ah"
CACHE = os.path.join(ROOT, "scripts", ".cache-sefaria", "yd-editions")
FORME_CACHE = 2          # à incrémenter dès que la forme d'un fichier de cache change
# 2 (tour 3) : le fichier garde la preuve du RECOUPEMENT (`recoupement`, voir fetch) ;
# un fichier de forme 1, écrit sans recoupement, est relu sur Sefaria.
HE_CONS = re.compile(r'[א-ת]')
CHAPEAU = re.compile(r'^\s*<b>.*?</b>\s*(<br\s*/?>)?', re.S)
LANGS = [("FR", ""), ("HE", "-he"), ("EN", "-en")]
ANCRE = 24               # consonnes (squelette) qui reconnaissent le début d'un séif
NGRAMME = 5              # pour désigner l'édition la plus proche d'un séif divergent
SEUIL_ALIGNEMENT = 0.5   # R2 — mesuré : alignés ≥ 0,636, autre siman ≤ 0,258 (docstring)
# R2 — et le séif de même numéro doit battre STRICTEMENT tous les autres séifs du siman.
REFERENCE_ALT = re.compile(r'^Torat Emet \d+$')   # R1 — la Torat Emet NUMÉROTÉE
MARQUE = re.compile(r'[א-ת]["\'׳״]')    # guerech / guerchayim après une lettre
ANCRE_SEFARIA = re.compile(r'<i data-commentator[^>]*>\s*</i>')

COURT = {
    "Ashlei Ravrevei: Shulchan Aruch Yoreh Deah, Lemberg, 1888": "Ashlei Ravrevei",
    "Torat Emet 357": "Torat Emet 357",
    "Torat Emet Freeware Shulchan Aruch": "Torat Emet Freeware",
    "Wikisource Shulchan Aruch": "Wikisource",
}

RAISONS = {}


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
    """R1 : (édition par défaut, [Torat Emet numérotée], [éditions servies, avec
    du texte, et IGNORÉES])."""
    d = defaut_de(eds)
    alts = [e for e in eds if e is not d and REFERENCE_ALT.match((e["titre"] or "").strip())]
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


def fetch(n, rafraichir=False):
    """Les éditions hébraïques du siman N : {"ref", "editions": [{"titre",
    "priorite", "seifim": [html brut…]}]} triées par priorité décroissante — ou
    None, et RAISONS[n] dit pourquoi. Une réponse dont l'édition par défaut est
    vide ou indécidable n'est jamais mise en cache."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"YD-{n}.json")
    if not rafraichir and os.path.exists(f):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if (d.get("forme") == FORME_CACHE and str(d.get("ref", "")).endswith(f" {n}")
                    and _complet(d) and _recoupe(d)):
                return d
        except Exception:
            pass
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
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
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
    """Les mots d'un texte : [(clé, mot lisible, consonnes, début, fin)], début et
    fin en position du SQUELETTE de tout le texte (celle de `localiser`). La clé
    est le squelette — ou, pour un mot qui porte un guerech ou des guerchayim
    (abréviation, nombre), ses lettres et ses marques normalisées : « סי׳ »
    (siman) et « ס״י » (séif 10) ont les mêmes consonnes, et « י״א » le même
    squelette que « א׳ ». Un mot sans clé (« ו » seul) n'est pas aligné."""
    t = re.sub(r'<[^>]+>', ' ', ANCRE_SEFARIA.sub('', brut))
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


def _remplacement(A, B):
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
    qui leur sont substitués)."""
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
                if not _egal(A[i], B[j]):
                    pose(i + 1, j + 1, 1, 0.5, "leçon")
                for di, dj in _paires(A, i, B, j):
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


def statuts(A, B):
    """Le sort de chaque mot de A (l'édition par défaut) dans B :
      'porté'   — apparié à sa place (même mot, ktiv, une lettre, abréviation
                  développée ou contractée, scindé ou soudé), ou couvert par un
                  mot non apparié de B tout près (`_couvert`) ;
      'leçon'   — un mot de B lui est substitué (et, s'il y en a un, le seul mot
                  laissé sans contrepartie à côté de la substitution : la censure
                  deux-pour-un, « עובד כוכבים » / « גוי ») ;
      'déplacé' — sans contrepartie à sa place, mais tout son passage se lit d'un
                  seul tenant ailleurs dans le séif de B (`_deplace`) ;
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
            om, pris, subst, subst_b = _remplacement(A[i1:i2], B[j1:j2])
            libres.update(j1 + j for j in range(j2 - j1) if j not in pris)
            substitues.update(j1 + j for j in subst_b)
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
    """Les suites d'indices des mots de A (l'édition par défaut) OMIS dans B (R3)."""
    return _suites(i for i, x in enumerate(statuts(A, B)) if x == "omis")


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
        self.mots, self.omis, self.ratio, self.ecartees = [], [], [], []
        self.statut, self.dep = [], []
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
                    raw = CHAPEAU.sub('', raw)
            raws.append(raw)
        self.mots = [mots(r) for r in raws]
        for i, raw in enumerate(raws):
            c0 = consonants(raw)
            var, br, rat, om, stt, dep = {}, {}, {}, {}, {}, {}
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
                stt[nom] = statuts(self.mots[i], ma)
                om[nom] = _suites(j for j, x in enumerate(stt[nom]) if x == "omis")
                dep[nom] = _suites(j for j, x in enumerate(stt[nom]) if x == "déplacé")
            self.seifs.append(var)
            self.bruts.append(br)
            self.ratio.append(rat)
            self.omis.append(om)
            self.statut.append(stt)
            self.dep.append(dep)

    def lacunaire(self, i, labs):
        """La leçon (éditions `labs`) du séif i+1 perd-elle un passage de
        l'édition par défaut ? Jamais si l'édition par défaut la donne aussi."""
        return bool(labs) and self.D not in labs and bool(self.omis[i].get(labs[0]))

    SORTS = {"porté": "le porte", "omis": "absent aussi", "déplacé": "porté ailleurs dans le séif",
             "leçon": "autre leçon"}

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
                        + (" — absent en partie de " + nom + " aussi" if "omis" in c else ""))
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
                if om:
                    om["ktiv"] = ex is None
                    out.append((i + 1, "OMISSION", tuple(ex if ex is not None else labs), om))
                elif ex is not None:
                    out.append((i + 1, "RETENU", tuple(ex), None))
                else:
                    out.append((i + 1, "KTIV", tuple(labs),
                                {"page_mots": mots_autour(brut_page, pos)}))
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
            out.append((i + 1, "DIVERGENT", tuple(labs), {
                "proximite": sc, "autres": autres, "p": p,
                "page_mid": seg[p:len(seg) - s], "ed_mid": k[p:len(k) - s],
                "page_mots": mots_autour(brut_page, pos + p),
                "ed_mots": mots_autour(bruts[i].get(ed, ""), p),
                "omis": omis,
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
            continue
        ok = False
        for s_, st, labs, d in loc:
            cle = st
            if st == "RETENU":
                cle = "RETENU" if D in labs else "RETENU hors défaut"
                if cle == "RETENU hors défaut":
                    stats["div_hors_defaut"].append((n, lang, s_, labs[0]))
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
    print(f"  éditions de référence (séifs non vides) : {lues} — par défaut : {D}")
    if ref.ignorees:
        print("  servies et IGNORÉES (R1 — ni par défaut, ni Torat Emet numérotée) : " + " · ".join(
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
            continue
        print(f"  {lang}: {nb} blocs text-source | texte source : ❌ DIVERGENCE "
              f"(contre les éditions de référence)")
        ret = [(s, labs) for s, st, labs, _ in loc if st == "RETENU"]
        if ret:
            hors = [(s, labs) for s, labs in ret if D not in labs]
            print(f"      {len(ret)} séif(s) fidèle(s) à une édition de référence"
                  + (f", dont {len(hors)} à {'/'.join(ref.nom_alts) or 'une autre'} seulement : "
                     + " ".join(f"{s}={labs[0]}" for s, labs in hors) if hors else ""))
        for s, st, labs, d in loc:
            if st == "RETENU":
                continue
            if st == "SURPLUS":
                print(f"      SURPLUS : {d['long']} consonnes après le dernier séif — « {d['page_mots']} »")
            elif st == "CHAPEAU DIVERGENT":
                print(f"      CHAPEAU du siman récrit : page « {d['page_mid'][:40] or '∅'} » / "
                      f"« {d['ed_mid'][:40] or '∅'} » (squelette) — {d['page_mots']}")
            elif st == "KTIV":
                print(f"      séif {s} : KTIV — égal à {'+'.join(labs)} aux seules matres lectionis "
                      f"près (refusé : cette porte exige les consonnes) — {d['page_mots']}")
            elif st in ("NON RETROUVÉ", "SANS TEXTE"):
                print(f"      séif {s} : {st} — son début ne se lit nulle part après le séif "
                      f"précédent (absent, fondu, ou altéré dès ses premiers mots)")
            elif st == "OMISSION":
                print(f"      séif {s} : OMISSION (R3) — la page est {'+'.join(labs)} "
                      f"{'au ktiv près' if d.get('ktiv') else 'mot pour mot'}, mais {D} porte "
                      f"ce qu'elle n'a pas :")
                for t, L, m in d["runs"]:
                    print(f"          « {t} » ({L} mot{'s' if L > 1 else ''}) — {m}")
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
    if not parite:
        print("  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE")
    elif cons_par_langue:
        print("  parité FR/HE/EN du texte source : ✅ identique")
    return ok


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
             "div_hors_defaut": []}
    print(f"=== Texte source de Yoré Déa vs l'édition par défaut de Sefaria (et Torat Emet "
          f"numérotée pour les leçons) — {len(nums)} siman(im) · ROOT {ROOT} ===")
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
