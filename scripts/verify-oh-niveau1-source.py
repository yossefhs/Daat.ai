#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garde-fou de recopie du NIVEAU 1 d'Orah Haïm — le texte source donné au
lecteur est-il le Choul'han Aroukh, tout le Choul'han Aroukh, et rien d'autre ?

  python3 scripts/verify-oh-niveau1-source.py 8 32 128
  python3 scripts/verify-oh-niveau1-source.py --tous            # les 241
  python3 scripts/verify-oh-niveau1-source.py --tous --bref     # une ligne par siman
  python3 scripts/verify-oh-niveau1-source.py --tous --rafraichir   # ignore le cache
  python3 scripts/verify-oh-niveau1-source.py 3 --edition ME   # DIAGNOSTIC : une seule édition

Codes de sortie : 0 conforme · 1 divergence au-delà du ktiv · 3 RIEN n'a pu être
confronté, ou une partie des simanim demandés n'a pas été atteinte — ou seulement
confrontée à une réponse INCOMPLÈTE de Sefaria (siman PARTIEL, tour 3) — alors que le
reste est conforme (la porte ne conclut pas sur ce qu'elle n'a pas lu en entier), ou un
diagnostic ``--edition TE`` qui serait « conforme » (R3 n'y est pas appliquée) · 2 usage.

CE QUE DIT CHAQUE LIGNE DE DÉFAUT — pour qui corrige une page avec cette porte :
  séif 4 (ד) [ME] : ALTÉRATION (parenthèse) — passage entre parenthèses omis :
                    « פי' מיאני » — absent aussi de Torat Emet 363 (…)
  · [ME] / [TE] : l'ÉDITION DE RÉFÉRENCE à ouvrir pour ce séif (ME, l'édition par
    défaut ; TE, Torat Emet 363 quand la page la suit) ;
  · la famille (ABSENT, TRONCATURE, DÉPLACÉ, ALTÉRATION, AJOUT, REPRISE), et pour une
    ALTÉRATION sa NATURE entre parenthèses : (renvoi), (parenthèse), (omission) —
    des mots de la source qui manquent — ou (leçon) — des mots changés, une
    abréviation développée, une lettre, un mot ajouté ;
  · entre « » le TEXTE de la source qui manque, ou « source » → « page » ;
  · « — absent aussi de Torat Emet 363 » : le passage est de l'édition par défaut,
    l'autre édition l'omet aussi, et il reste à rétablir (règle R3 ci-dessous) —
    quelle que soit sa longueur, un mot compris (tour 3) ;
  · « À SA PLACE, N mot(s) qui ne sont pas ce séif : « … » » : ce que la page donne à
    l'endroit d'un séif ABSENT ou réduit (tour 3 — un séif d'un autre siman, par exemple).
  · « LEÇON EXCUSÉE (R3) — … c'est la leçon de Torat Emet 363, au même endroit du séif » :
    une INFORMATION, pas un écart (tour 4) — la page écrit là ce qu'écrit l'autre édition ;
  · sous les lignes de langue, « ktiv FR/HE/EN : N mot(s) égaux à l'édition retenue AU KTIV PRÈS … » :
    chaque mot que la page n'égale à l'édition qu'en ajoutant ou ôtant des yod/vav, à contrôler,
    « * » quand aucune des deux éditions ne l'écrit ainsi à cet endroit (tour 4).

POURQUOI UN NOUVEAU SCRIPT, ET NON UN MODE DE ``verify-oh-source.py``
--------------------------------------------------------------------
``verify-oh-source.py N`` est invoqué par la clause de vérification du dépôt avant
chaque publication ; son usage et ses codes de sortie doivent rester STRICTEMENT
identiques. Or il lit chaque argument par ``int(x)`` — un drapeau ``--niveau1`` y
lèverait une exception —, il ne connaît pas de code 3, et une source injoignable
l'arrête sur une trace Python. Lui greffer un mode, c'était toucher à son analyse
d'arguments et à ses chemins d'échec, c'est-à-dire à ce qui ne doit pas bouger.
Les deux portes ne lisent d'ailleurs ni le même ouvrage (Choul'han Aroukh HaRav
contre Mehaber + Rama), ni le même bloc (``seif-details`` du niveau 4 contre
``blockquote.text-source`` du niveau 1), ni ne rendent les mêmes verdicts.

CE QUE LES DEUX PORTES SŒURS SAVENT DÉJÀ, ET QUE CELLE-CI REPREND
-----------------------------------------------------------------
De ``verify-chabbat-source.py`` et ``verify-yd-source.py`` : la concaténation des
``<blockquote class="text-source">`` de ``niveau-1-base`` confrontée à la
concaténation des séifim de ``Shulchan_Arukh,_Orach_Chayim.N``, sur les CONSONNES :
nikoud, ponctuation, balises et ancres ``<i data-commentator>`` retirés ; le
chapeau du siman (« דין … ובו ט סעיפים ») facultatif ; deux verdicts, IDENTIQUE et
ÉQUIVALENT (égal aux matres lectionis près, le ktiv haser/malé étant le faux
positif dominant) ; la parité FR/HE/EN du texte source.

DEUX ÉDITIONS HÉBRAÏQUES — ET LA PORTE N'EN CONNAISSAIT QU'UNE (réparé le 8 octobre 2026)
---------------------------------------------------------------------------------------
Sefaria sert, pour chacun des 241 simanim, DEUX éditions hébraïques du Choul'han
Aroukh, au même nombre de séifim (vérifié sur les 241) :
  ME  « Maginei Eretz: Shulchan Aruch Orach Chaim, Lemberg, 1893 » — non vocalisée,
      abréviations de l'imprimé (לבה״כ, וי״א, ש״ז), chapeau du siman en <b> ; c'est
      la version que ``api/texts`` sert PAR DÉFAUT, et la seule que lisait la porte ;
  TE  « Torat Emet 363 » — VOCALISÉE, abréviations le plus souvent DÉVELOPPÉES
      (לבית הכסא, שכבת זרע), son propre ktiv, pas de chapeau, et des mots qui
      diffèrent par endroits (מורה נבוכים ח״ג פ׳ נ״ב / פ׳ כ״ב ; בית יוסף / ב״י).
Beaucoup de pages de niveau 1 ont recopié TE (leur hébreu est vocalisé), d'autres ME,
et beaucoup mêlent les deux. La porte les confrontait à ME seule : elle rangeait parmi
les « altérations par abréviation » des séifim que la page recopie FIDÈLEMENT d'une
édition réelle. MESURE (machinerie de la porte inchangée, ME puis TE seule, les trois
pages réunies) : des 655 séifim que ME mettait en ALTÉRATION, 138 sont CONFORMES à TE ;
1 des 219 TRONCATURES (67:1, le chapeau, voir plus bas) ; aucun des 139 ABSENTS ni des
19 DÉPLACÉS. Mais TE seule n'est pas la réponse : des 609 séifim conformes à ME, elle
en rend 332 non conformes — d'où le choix séif par séif. Le livre a quatre éditions hébraïques
sur Sefaria ; sur les simanim 1 à 241, ``api/v3`` n'en sert que ces deux (« Torat Emet
Freeware Shulchan Aruch » n'est servie qu'ailleurs — au siman 500, pas aux 1, 3, 100,
241, 300 —, et « שלחן ערוך מטור ארוח חיים » sur aucun des simanim sondés).

COMMENT LA PORTE CHOISIT, ET LES QUATRE GARDES QU'IL A FALLU
- Elle lit TOUTES les éditions hébraïques que ``api/v3/texts`` sert pour le siman
  (``version=hebrew|all``). Chaque édition est alignée SEULE sur toute la page et
  analysée. Puis, séif par séif, elle retient l'édition la PLUS PROCHE de la page —
  le moins de mots non appariés des deux côtés (mots de l'édition absents ou
  remplacés + mots de la page qui les remplacent ou s'y ajoutent), puis le moins
  d'écarts de ktiv, puis ME, l'édition par défaut — et rapporte le verdict que CET
  alignement-là donne du séif. Chaque ligne de défaut porte le sigle de l'édition à
  ouvrir : [ME] ou [TE]. Un séif qui ne correspond à AUCUNE édition au-delà du ktiv est
  compté comme tel, par siman et au total.
- GARDE 1, LE LIEU. On ne réaligne jamais une source composée : mêler les éditions
  déplaçait des mots d'un séif à l'autre sur une page qui réordonne la source (siman
  32 : le séif טז vidé au profit du séif טו). Et TE n'est retenue pour un séif que si
  elle le lit AU MÊME ENDROIT de la page que ME — au siman 32, TE « retrouvait » le séif
  טו dans le bloc qui donne le séif טז (tous deux finissent par « כשר ואם לאו פסול »),
  à deux mots de moins que ME, qui le tenait pour absent.
- GARDE 2, L'ORDRE. Qu'un séif soit DÉPLACÉ se juge par rapport à ses voisins, que
  chaque alignement place à sa façon : le séif est DÉPLACÉ si une édition qui le lit au
  même endroit le trouve hors de l'ordre de la source (32:19, vu par ME, pas par TE).
- GARDE 3, LES PARENTHÈSES. « Passage entre parenthèses omis » (une ALTÉRATION, jamais
  une troncature du din) ne vaut plus que pour un passage que TOUTES les éditions
  mettent entre parenthèses. Chacune en met où l'autre n'en met pas, et ni l'une ni
  l'autre n'y range que des renvois : ME imprime entre parenthèses la glose entière du
  Rama au 175:2 (« הגה ואין חילוק בין שניהם חדשים … », 55 mots) et au 6:2 (« ועכ״פ לא
  יברך ב׳ פעמים … »), TE l'explication de soixante mots du 97:2. La porte AVANT, qui ne
  lisait que ME, disait de ces omissions « passage entre parenthèses omis ». La ligne
  dit maintenant où sont les parenthèses (« — entre parenthèses dans ME, hors
  parenthèses dans TE ») : ce peut être un simple renvoi (« ועיין לקמן סימן רל״ג »,
  92:4), à juger, pas à taire. La glose du Rama de même : un mot est du Rama si une
  édition le dit.
- GARDE 4, LE MÉLANGE. Une page mêle souvent les éditions DANS un séif (« אע״פ » →
  « אף על פי », la leçon de TE, au 10:12, séif où elle suit ME pour le reste). L'écart reste un écart à l'édition
  retenue — aucune ne donne ce séif tel quel —, mais la ligne ajoute « — la page suit
  ici TE » quand la forme de la page est celle de l'autre édition au même séif. Pour le
  tri : aucun mot n'y est inventé.
- Le CHAPEAU (« הנהגת בית הכסא. ובו יז סעיפים: », propre à ME) n'est plus un mot de la
  source. La page qui le recopie en tête, en tout ou en partie, même abrégé autrement
  (« בניין בית הכנסת ושיהיה גבוה », siman 150), le voit retiré avant l'analyse ;
  ailleurs il n'est rien. Il n'est donc jamais un écart, et il ne capte plus les
  premiers mots du séif א : quand il les répète (« דין ספק אם קרא קריאת שמע », 67 ;
  « שלא יגהק ולא יפהק », 97), l'alignement leur appariait les mots de la page et le
  séif א sortait « TRONCATURE début » à tort.
- Le cache change de forme (toutes les éditions) : version 3 depuis le tour 2, fichiers
  ``OH-N.v3.json`` (voir ``fetch``). ``--edition ME`` (ou TE) confronte à une seule
  édition : un DIAGNOSTIC, pas la porte.

TOUR 2 (8 octobre 2026) — LA RÈGLE COMMUNE AUX TROIS PORTES DE SOURCE
--------------------------------------------------------------------
Les arbitres du tour 1 ont trouvé la confrontation à « l'édition la plus proche » TROP
INDULGENTE, témoins construits à l'appui : sur Chabbat et Yoré Déa, l'édition Freeware
est désalignée par endroits (son Orah Haïm 344:1 est le texte du 343:1) et lacunaire
(252:2 saute « מלאכתו בשבת אם היה עושה », Yoré Déa 190:35 n'a pas la décision du Rama) ;
une page qui recopiait ces lacunes était certifiée IDENTIQUE. Ici :
  R1  Éditions de référence : l'édition par défaut (ME) et Torat Emet 363 (TE), elles
      SEULES (``REFERENCES``). Toute autre édition servie est ignorée, et la sortie le
      dit. Sur les 241 simanim, Sefaria ne sert que ces deux : coût nul aujourd'hui.
  R2  TE n'est admise pour un séif que si elle est ALIGNÉE sur le séif de même numéro
      de ME (``SEUIL_ALIGNE`` = 0,72, mesuré : voir la constante). 0 séif non admis sur
      1 453 ; la plus faible ressemblance est 0,787 (222:2).
  R3  UNE AUTRE ÉDITION EXPLIQUE UNE LEÇON, JAMAIS UNE OMISSION (``confronter``). Un
      passage de ME qui manque à la page reste signalé même si TE l'omet aussi, avec
      « absent aussi de Torat Emet 363 ». MESURE : TE omet un passage de ME (trois mots
      ou plus, ou entre parenthèses, ou un renvoi ; abréviations, réordonnancements et
      leçons d'un mot à la même place exclus) dans 8 séifs sur 1 453 — 39:4 « (פי׳
      מיאני) », 100:1 « וכ״כ תניא בשם ר״א », 128:9 « [רש״י ותוספות ור״ן כתבו … וכ״כ
      הב״י] » (treize mots), 150:1 « סכ״ב », 153:14 « פ׳ », 160:7 « [חם] », 168:12
      « (מרדכי) », 206:6 « ואגור » ; et d'un ou deux mots hors parenthèses dans 23
      autres (« ממנו », « את » ; « אליך ויחנך » 128:45, « חשוב או » 211:5 et « בכלי
      תוך » 40:3, une leçon de place, pour deux mots). La porte du tour 1 certifiait
      CONFORMES, grâce à une telle omission de TE, 3 séifs × page (39:4, les trois
      langues), et taisait l'omission dans 6 autres (150:1, 168:12 ×3) ; les 9 sont
      désormais signalés. Témoin adverse construit : une page qui recopie TE aux
      simanim 128, 100 et 39 sortait IDENTIQUE, code 0 ; elle sort ALTÉRATION, code 1.
      (Le tour 2 EXCUSAIT encore les 23 omissions d'un ou deux mots comme « leçon de TE » :
      c'était faux, voir TOUR 3.)
Et les quatre points laissés par l'arbitre du tour 1 :
- LE CACHE (``fetch``) : une édition servie vide n'était pas manquante si elle était
  absente d'``available_versions``, et une réponse sans ``available_versions`` était
  gravée ME seule — éprouvé en sabotant la réponse. Réparé ; version 3.
- LES RENVOIS (``nature_par``) : TE imprime « ועיין ביורה דעה סי׳ שמ״א » dans un
  <small> sans parenthèses, la marque du Rama — la porte disait « la glose du Rama »
  et comptait le renvoi parmi les troncatures « portant sur le Rama ». Un renvoi est
  désormais une ALTÉRATION (renvoi), comme avant le tour 1 : jamais une troncature du
  din, toujours signalé. 20 séifs ; « troncatures portant sur le Rama » 191 → 176
  (14 renvois et une explication, 148:1 « פי׳ רש״י … », sortis). Un « mot(s) omis »
  porte aussi la mention des parenthèses (8:5 « פרוש בפעם אחת », entre parenthèses
  dans ME, dans un <small> nu dans TE).
- LES COMPTEURS QUI BOUGENT PAR RECLASSEMENT sont dits dans l'en-tête du relevé.
- LA FINALE DU MOT (``cle_de``) : le yod et le vav finaux sont gardés dans la clé.
  (Affirmé au tour 2 sans être vrai partout : la branche « coupé autrement » d'``aligner``
  la perdait encore — voir TOUR 3.)

TOUR 3 (8 octobre 2026) — CE QUE L'ARBITRE DU TOUR 2 A TROUVÉ, ET CE QUI A ÉTÉ FAIT
------------------------------------------------------------------------------------
L'arbitre a dit NON : quatre témoins adverses de R3 certifiés IDENTIQUE, code 0, sur
les vraies données de Sefaria, un cinquième par sabotage, un changement de finale et
une réponse incomplète gravée dans le cache. Chaque point, et sa réparation :
- R3 NE CONNAÎT PAS DE LONGUEUR (``r3_courte``). Le tour 2 excusait toute omission d'un
  ou deux mots hors parenthèses que TE omet aussi : « חשוב או » dans la glose du Rama
  (211:5), « מיד » (175:3), « וקורא » (135:8), « ופסק » (140:2) ; une TE sabotée privée de
  la décision du Rama « והעיקר להטות » (131:1) certifiée de même. Les 23 séifs que le tour
  2 excusait ont été ouverts un à un contre les deux éditions : 22 sont des SUPPRESSIONS
  dans TE ; le 23e (40:3, ME « אפילו בכלי תוך כלי », TE « אפלו כלי בתוך כלי ») est une
  particule passée d'un mot à l'autre — ``_prefixe_deplace`` le reconnaît. Toute omission
  est désormais signalée ; les courtes sont seulement comptées à part, et une omission
  dans la glose du Rama le dit (« mot(s) omis de la glose du Rama »).
- LA FINALE, AUSSI QUAND LE TEXTE EST COUPÉ AUTREMENT (``coupe_autrement``). La branche
  « même texte, coupé autrement en mots » d'``aligner`` comparait des squelettes privés
  de TOUS les yod et vav : un remplacement d'un mot par un mot (« יאכל » / « יאכלו »)
  redevenait du ktiv — ME 170 recopiée avec « יאכלו » sortait ÉQUIVALENT, code 0, et au
  séif א du siman 3 le « יאמר » de la page (ME) face au « יאמרו » de TE (retenue) ne donnait
  pas une ligne. Mot pour mot, seules des lettres identiques passent ; coupé autrement, la
  différence ne peut être qu'un yod ou un vav intérieur. Coût sur les pages réelles : deux
  séifs CONFORMES → ALTÉRATION, 3:1 (« יאמרו » → « יאמר », la page suit ici ME) et 4:8
  (TE « על גבי », ME « ע״ג », la page « על גב ») — vérifiés à la main, réels, et dans les trois
  langues. Aucun verdict de siman ne change.
- LA RÉPONSE INCOMPLÈTE (``lacunes``, ``attendu``). ME servie tronquée (4 séifim sur 6)
  et TE entière : TE était écartée, la réponse gravée, la page amputée des séifim 5 et 6
  certifiée, code 0 ; ME et TE tronquées toutes deux, rien ne le voyait. Le nombre de
  séifim attendu vient de data/seifim-count.json (égal à ME sur les 241 simanim), à défaut
  du chapeau (qui dit 9 au siman 219, qui en a 10) ; chaque séif des deux éditions doit
  être non vide. Une lacune de ME rend le siman NON ATTEINT ; une lacune de TE (non servie,
  vide, un séif vide, découpée autrement) ou une réponse sans available_versions le rend
  PARTIEL : rien n'est gravé, jamais certifié conforme (code 3), et il ne fait sortir en 1
  que par un défaut que TE ne pouvait pas excuser (``SURES`` : une omission ou un séif
  déplacé). L'arbitre laissait « à trancher » le code 0/1 du tour 2 sur ces sabotages :
  c'est tranché ainsi.
- CE QUI EST À LA PLACE D'UN SÉIF ABSENT. 39:5 remplacé par 38:5 : le séif était dit
  ABSENT, les onze mots étrangers n'étaient nommés nulle part ; la ligne dit désormais
  « À SA PLACE, … ». En TE, la ligne disait « séif réduit à 2 mots, réécrit autour » : ME
  lisait comme le séif ה les deux premiers mots du séif ו, que TE lisait à bon droit — GARDE
  5 (``double_lecture``) : deux séifs lus dans deux éditions ne lisent jamais les mêmes
  mots de la page.
- UN NUMÉRAL ENTRE CROCHETS DANS UNE PARENTHÈSE n'est pas un marqueur de séif de la page
  (TE 53:19 « (… ומהרי״ק שרש (מ״ד) [ל׳]) ») : sur des pages qui recopient TE, la porte les
  blanchissait et accusait la page de les avoir omis (53, 55, 78, 143). Faux positifs,
  dans le sens strict ; aucun sur les pages réelles.

TOUR 4 (9 octobre 2026) — CE QUE L'ARBITRE DU TOUR 3 A TROUVÉ, ET CE QUI A ÉTÉ FAIT
-----------------------------------------------------------------------------------
L'arbitre a dit NON pour un seul défaut — la garde ktiv, qui vaut pour les trois portes de
source — et laissé trois points à corriger (l'omission cachée, la limite de R2, les étiquettes) :
- LA GARDE KTIV (``ktiv_seul``, appliquée dans ``aligner`` et ``coupe_autrement``). La clé de
  comparaison ôte yod et vav à l'intérieur du mot ; « כוס » (coupe) et « כיס » (poche), « מים »
  et « מום », « הוא » et « היא » y ont la même clé, et une page qui changeait l'un en l'autre
  sortait ÉQUIVALENT, code 0, sans un mot imprimé (témoin N4b, siman 182). Désormais deux mots
  de même clé ne sont égaux « au ktiv près » que si l'un s'obtient de l'autre en AJOUTANT
  seulement des yod/vav (sous-suite, finales normalisées) ; un ÉCHANGE est un mot changé, que
  la ligne nomme « yod/vav ÉCHANGÉ, un autre mot ». La règle de l'ajout seul ne suffisait pas
  au second témoin de l'arbitre (N4a, « שלשים יום » → « ים » : « ים » + vav = « יום ») : un mot de
  DEUX lettres n'a pas de ktiv — une mater y fait presque toujours un autre mot (« ים » / « יום »,
  « סף » / « סוף », « קל » / « קול ») ; il est rendu comme un mot changé, et excusé (R3, ci-
  dessous) quand l'autre édition l'écrit ainsi au même endroit (« חל » / « חול », « גב » / « גוב »,
  « על » / « עול », « רב » / « רוב » : les cinq séifs des pages réelles où cela arrive, 65:1, 65:2,
  70:1, 85:2, 108:10, le sont tous). COÛT MESURÉ
  sur les 723 pages réelles (instantané HEAD 56151b14) : trois mots deviennent des écarts, ceux
  que l'arbitre avait comptés, tous de vraies variantes absentes des deux éditions — 27:6
  « חשובה » pour « חשיבה », 55:2 « עבירה היא » pour « הוא », 124:2 « יכול » pour « יוכל » ; aucun
  verdict de séif ne change (ces trois séifs avaient déjà d'autres écarts). Sous ÉQUIVALENT, la
  porte LISTE les mots qui ne sont égaux qu'au ktiv près (869 sur les pages réelles, 2 882
  × page), et marque « * » les 229 dont la forme n'est à cet endroit celle d'aucune des deux
  éditions — c'est là qu'il faut lire d'abord : « ציציות » pour « ציצית », « ברכות » pour « ברכת »,
  « יוצא » pour « יצא », « וילבישנו » pour « וילבשנו » sont des ajouts de mater qui changent le
  nombre, le temps ou le binyan, et la règle de l'ajout seul ne peut pas les voir. LIMITE DITE.
  (« שהוא » / « שיהא », que l'arbitre notait encore égaux par la clé, ne le sont plus : aucun ne
  s'obtient de l'autre par ajout.) Un passage COUPÉ AUTREMENT (``coupe_autrement``) suit la même
  règle — des yod/vav ajoutés d'un SEUL côté — et ses finales sont normalisées (collés, « לכוון
  מלה » font « לכווןמלה », nun final au milieu) ; coût sur les pages réelles : nul (112 remplacements
  reconnus comme recoupés, alignements de toutes éditions et pages confondus, chacun jugé comme
  au tour 3).
- R3, L'OMISSION CACHÉE DANS UN REMPLACEMENT (``_contreparties``). Un remplacement n'était une
  omission que si l'autre côté avait moins de la moitié des mots (``nj * 2 < ni``) : « ואלהי
  אבותינו כו׳ » (ME 128:10) / « ואלהי וכו׳ » (TE), recopié par la page, sortait « abréviation
  développée ou changée », et « אבותינו » n'était signalé nulle part. Chaque mot du remplacement
  cherche désormais sa contrepartie en face : le même mot à la souplesse près, une abréviation
  et son développement (« בה״כ » / « בית הכנסת », « וי״א » / « ויש אומרים », « פרק רביעי » /
  « פ״ד », « שמונה עשרה » / « י״ח »), le même texte coupé autrement (« של אחר » / « שלאחר »), une
  particule passée au mot voisin, puis un mot libre en face pour un mot changé ; ce qui reste
  est une OMISSION. Appliqué des deux côtés : entre ME et TE (``marquer_absences`` : 17
  remplacements candidats sur les 1 453 séifs, 4 portent désormais un mot absent de TE —
  131:8 « אם », 139:7 « את », 206:5 « ואח״כ », et 224:8 « אומות » (ME « אומות העולם עכו״ם », TE
  « עובדי כוכבים » : la substitution du censeur, LIMITE — le mot est de ME, il manque à TE, mais
  c'est une leçon plus qu'une omission) ; 128:10 était une suppression, déjà vue ; 220:1 « ליה »,
  que l'arbitre comptait, est DÉPLACÉ chez TE après la parenthèse, non omis), et entre la page
  et l'édition (``classer_trou`` : « mot(s) omis … — dans un remplacement : « … » → « … » »). Sur
  la page qui recopie TE lettre pour lettre (témoin Wte de l'arbitre) : 128:10, 131:8, 139:7,
  206:5, 224:8, plus 82:2 « הגה », 124:2 « ברכ׳ », 197:3 « פת » (« כזית פת » / « כזית »), tous
  « absent aussi de Torat Emet 363 ». Sur les pages réelles : 14 séifs gagnent une ligne
  d'omission cachée (153:13 « לא ימכרם לדבר מצוה » → « אין מוכרים », 11:4 « החוטים השמנה » →
  « החוטין »…), tous déjà en ALTÉRATION.
- LES OMISSIONS SE JUGENT CONTRE ME (``_rejuger_contre_me``). L'omission cachée faisait sortir
  « omission » dans des séifs retenus dans TE où la page suit ME (34:2 : TE « ואם (ויש אומרים) »,
  ME « (וי״א שאם) », la page « ויש אומרים שאם »). Une omission relevée contre TE n'en est une que
  si la page omet aussi ce que ME porte à cet endroit : contrepartie vide dans ME (TE seule
  porte ces mots : « [שתולה] » 42:1, « זה » 128:3, « בכלי » 171:4…) ou portée par la
  page → LEÇON EXCUSÉE ; contrepartie que la page rend autrement → une leçon (33:2) ; sinon
  l'omission reste. Le tour 3 ne le faisait pas non plus pour une simple suppression d'un mot
  que TE seule porte. Pages réelles : 7 séifs excusés (34:2, 42:1, 94:1, 128:3, 131:8, 149:1,
  171:4), 1 rendu leçon (33:2) ; aucune omission que ME porte n'a été excusée (témoin X2b : une
  page qui omet, dans un séif retenu dans TE, un mot des deux éditions, sort en 1).
- R3, LE VERSANT LEÇON (``_porte_au_meme_endroit``). Une page qui écrit la leçon de l'AUTRE
  édition au milieu d'un séif retenu dans une édition (« אע״פ » → « אף על פי » au 10:12 ; témoin
  C-A4 de l'arbitre au 271:2) sortait ALTÉRATION « la page suit ici TE » : plus sévère que R3, qui excuse
  les leçons. Elle est désormais LEÇON EXCUSÉE — une information, pas un écart — si l'autre
  édition porte cette forme AU MÊME ENDROIT : les mots de la page y sont appariés à ses mots, ce
  sont la contrepartie des mots remplacés, et la page porte toute cette contrepartie (« A B' B
  C » dans TE, « A B C » dans ME, « A B' C » sur la page : B manque, rien n'est excusé). Le tour 3
  disait « la page suit ici TE » quand la forme se trouvait N'IMPORTE OÙ dans le séif. MESURE sur
  les pages réelles : 176 séifs portent une leçon excusée ; 49 séifs que le tour 3 comptait en
  ALTÉRATION sont désormais conformes (3:1, le « יאמר » de ME dans un séif retenu dans TE, en
  est un), et quatre simanim passent d'ALTÉRATION à ÉQUIVALENT (23, 41, 44, 60).
- LES ÉTIQUETTES. Une interversion (« הולכים ואוכלי׳ » → « אוכלים והולכים », témoin N2b ; un mot
  « omis » ici et « ajouté » là dans le même séif) est « mots intervertis » / « mot(s) déplacé(s)
  dans le séif », non « abréviation développée ou changée » ni une omission (69:1 sur les pages
  réelles). Un siman PARTIEL n'affiche plus « IDENTIQUE » sur sa ligne de langue (témoin TE
  vidée, siman 224) ni dans le tableau des verdicts (``PARTIEL``).
- R2 NE VOIT PAS UN SÉIF PARALLÈLE, LIMITE ÉCRITE (``SEUIL_ALIGNE``). La ressemblance avec le séif
  de même numéro de ME écarte un séif voisin ou déplacé (Freeware 344:1 = 343:1, 0,00), pas un
  séif PARALLÈLE d'un autre siman qui dit presque la même chose : TE 185:2 remplacé par TE 62:3
  est admis à 0,945, et la page qui le recopie sort IDENTIQUE, code 0 (témoin N18 de
  l'arbitre) — « שישמיע » → « להשמיע », « בשפתיו » → « בפיו » y passent pour des leçons de TE. La
  vraie TE est alignée sur les 1 453 séifs (chaque séif de TE plus proche du séif ME de même
  numéro que de tout autre séif du siman ; minimum 0,787, 222:2) : la limite ne touche
  aujourd'hui aucun verdict, mais une TE corrompue ainsi passerait.
- LES TROIS LISTES D'UN SÉIF (familles, lignes, info) restent parallèles : une REPRISE dont des
  mots ne sont pas la source ajoutait une famille sans ligne, et décalait les lectures par
  indice des tours suivants ; c'était une ligne MUETTE (tour 5 : chaque écart d'une reprise a
  désormais sa ligne visible).

TOUR 5 (9 octobre 2026) — CE QUE L'ARBITRE DU TOUR 4 A TROUVÉ, ET CE QUI A ÉTÉ FAIT
-----------------------------------------------------------------------------------
L'arbitre a dit NON : sur les données réelles de Sefaria, sans sabotage, un témoin du bloquant du
tour 4 était encore certifié — la garde ktiv ne passait pas par le chemin de la REPRISE. Deux
bloquants, deux points à corriger :
- LA REPRISE CONFRONTÉE MOT À MOT (``juger_reprise``, les deux bloquants). La branche REPRISE
  d'``analyser`` ne comparait que des CLÉS, et excusait tout mot dont la clé figurait N'IMPORTE OÙ
  dans une édition. Au siman 5, « שֶׁהוּא תַּקִּיף » → « שֶׁהִיא » dans la seule reprise (témoin Y2), et
  au siman 22, « וְאִם לֹא בֵּרַךְ » → « וְאִם בֵּרַךְ » dans la reprise de la glose du Rama — le din
  inversé (Y1) : « cités une seconde fois, fidèlement (au ktiv près) », ÉQUIVALENT, code 0. Les mots
  de la source qui manquaient à la reprise n'étaient jamais regardés. Désormais chaque BLOC de la
  reprise est aligné mot à mot, dans chaque édition de référence, sur le passage qu'il cite :
  chaque paire passe la garde ktiv ; un mot de la page est conforme s'il est le mot d'une édition
  de référence À CET ENDROIT (R3, versant leçon), jamais parce que sa clé est ailleurs (l'excuse
  globale ``cles_eds`` est retirée) ; un mot de ME qui manque entre deux mots cités — ou entre deux
  blocs consécutifs de la reprise, qui ne peut pas sauter ce qu'un seul bloc ne peut pas sauter —
  est une OMISSION (« ALTÉRATION (reprise) … OMIS … NON déclaré(s) »), sauf « … » à cet endroit : la
  convention du dépôt (« A… B » : A et B chacun mot pour mot) ; la coupure déclarée est dite sur la
  ligne REPRISE. Les bords sont libres. Les mots égaux au ktiv près seulement sont listés sur la
  ligne REPRISE. COÛT sur les pages réelles : nul — les quatre reprises (5, 16, 22, 48) sont
  lettre pour lettre la source (la porte du tour 4 disait « au ktiv près » de toute reprise).
- UN MOT TRONQUÉ N'ABRÈGE QU'UN MOT (``_tronque``, ``_abrege``). « אפי׳ » couvrait « אפילו יש » (le yod
  lu comme initiale du mot suivant) : l'omission de « יש » passait pour une abréviation développée,
  et le séif sortait conforme quand l'autre édition portait la même abréviation (Z7a, Z7b, 128:31).
  Coût : un séif, 171:4, passe d'ALTÉRATION à CONFORME — « שאינ׳ » de ME ne couvre plus « שאינם
  נמאסים » de TE, et le « נמאסין » de la page y est reconnu pour la leçon de ME au même endroit.
- L'ÉTIQUETTE DE POSITION (``glisser``). Au 53:13 (pages d'avant les finitions), la page omet le
  crochet « [עבדי ישעיה ערום תרגם עבדי ישעיה פחח] » : son « פוחח » était apparié au « פחח » qui FERME
  le crochet (même clé, un vav ajouté), et la ligne disait « TRONCATURE début … « פוחח עבדי ישעיה
  … » », quand la page a bien « פוחח » et que l'omission est INTÉRIEURE. Un trou qui peut glisser
  préfère désormais la position où les mots appariés sont identiques lettre pour lettre, puis
  passent la garde ktiv, avant la frontière de séif : « ALTÉRATION (parenthèse) — passage entre
  parenthèses omis : « עבדי ישעיה ערום תרגם עבדי ישעיה פחח » » (les deux éditions le mettent entre
  crochets ou parenthèses). Coût sur les pages de HEAD 7991a335 : nul. Le même glissement vaut
  pour l'alignement de ME sur TE qui dit ce que TE omet (``_glisser_suppression``, R3) : ME 160:13
  « מחצי לוג לג׳ ולד׳ », TE « מחצי לג׳ ולד׳ » — TE n'a pas « לוג », non « לג׳ » (les deux mots ont la même
  clé). Sans lui, une fois la page glissée, la ligne [ME] « absent aussi de Torat Emet 363 » d'une page
  qui recopie TE disparaissait (témoin Wte de l'arbitre du tour 2 : 37 → 36 séifs). Mesuré : c'est la
  seule suppression des 1 453 séifs, dans les deux sens, qui glisse.
LIMITES DITES : l'alignement de ME et TE qui sert aux EXCUSES (``ops_ij``, ``_region``) n'est pas glissé —
le seul cas du livre est 160:13, et il ne touche aucun verdict des pages réelles ; un mot
de la page reconnu pour le CHAPEAU (``retirer_chapeau``) est retiré sans être confronté — le
chapeau n'est pas un mot de la source. TOUR 7 — UNE SEULE RÈGLE, STRICTE (``_chapeau_lu``, ``retirer_chapeau``) : le
chapeau est lu mot à mot, depuis son PREMIER mot et dans l'ordre ; chaque mot de la page doit
être le mot suivant du chapeau (même clé, ou au ktiv près : « באיזהו » pour « באיזה »), son
développement s'il est abrégé (« ב״ה » → « בית הכנסת », siman 150), la lettre-nombre écrite en
toutes lettres (« ובו ה סעיפים » → « חמשה סעיפים »), ou l'abréviation de mots du chapeau ; la
lecture s'arrête au premier mot qui ne suit pas, et il en faut deux au moins ; devant une
abréviation, le développement le plus court ; une lecture partielle n'est retirée que si elle
s'arrête à la fin du titre, juste avant « ובו » (tour 8 : « עכו״ם » avalait « מותר » au 14,
« בהמ״ז » avalait « זה » au 182, et « ושלא », mot suivant du chapeau, ouvrait le séif), et jamais
quand elle finit sur le développement d'une abréviation du chapeau (tour 9 : « בקריאת שאינו
אסור… », 83, se lisait « בק״ש » et le séif était conforme ; de même 64, 70, 76, 149, 187). Elle remplace
l'absorption par ressemblance des tours 3 à 6, qui, réglée trois fois, avalait chaque fois un
mot inséré en tête du séif א, et la page sortait IDENTIQUE, le din inversé : « אינו קורא על
מטתו » (239:1, témoins B1, B2 de l'arbitre du tour 5), « לא » devant 66:1 (W07, W10a, W11,
W12, W13 du tour 6), « לא אחד » au 88 et « לא » AVANT le chapeau au 24 (Z01, Z04b, Z05, Z10 du
tour 7, N07, N12, N14 du tour 8, V01-V05, V14 du tour 9). Rejoué sur tous ces témoins : chaque
insertion sort signalée.
Coût nul sur les 241 pages réelles : sortie complète identique à l'octet. Ce qu'elle laisse, et
qui est une ALERTE, jamais un vert : un chapeau interrompu par un mot inséré, REFORMULÉ
(« דיני החליצה של התפלין » pour « דיני חליצת התפילין », témoin B0 ; « להטיל מים » pour
« להשתין », W09c) ou tronqué ailleurs qu'à la fin du titre (Z03tc) n'est pas retiré, et sa tête
sort en AJOUT, comme dans la porte commitée avant ces tours. LIMITE : une abréviation du chapeau
se lit par ses initiales (« בק״ש » écrit « בלא קריאת שמע ») ; une reprise d'un bloc pris AILLEURS dans le séif est bien
signalée, mais son étiquette dit « dans la reprise du séif 0 () » ; quand l'édition retenue
écrit haser et que l'autre porte une forme malé au même endroit, une mater ÉCHANGÉE par
rapport à cette forme malé reste « égale au ktiv près » à l'édition haser (listée « * », non
signalée) ; deux blocs d'une reprise donnés dans un AUTRE ordre que la source ne sont pas jugés sur
ce qu'ils sautent ; un bloc d'un ou deux mots s'apparie où il se trouve dans l'édition.

DEUX DÉFAUTS QUE LA MÉMOÏSATION CACHAIT (réparés le même jour)
-------------------------------------------------------------
L'analyse était mémorisée par MOTS de page : trois pages aux mêmes mots recevaient le
résultat calculé sur la première, la française. Or l'analyse lit aussi ce qui est
propre à chaque page — la déclaration de sélection, les titres des blocs. Deux erreurs
s'y compensaient : le motif de déclaration ne lisait pas « טקסט מייצג » (siman 32, page
hébraïque) — le résultat français la couvrait ; et il lisait « נציג » / « representative »
dans « הנציג של הציבור » (siman 53, pages hébraïque et anglaise), qui ne déclarent rien —
le résultat français le taisait. L'analyse est désormais faite page par page (seul
l'alignement, qui ne dépend que des mots et des blocs, est mémorisé), et le motif ne
lit plus que les formules de déclaration.

CE QU'ELLES NE SAVENT PAS FAIRE, ET QUI EST LE CŒUR DE CELLE-CI
--------------------------------------------------------------
Les portes sœurs disent « divergence » et montrent la première. Elles ne disent pas
CE QUI diverge, ni OÙ, ni combien de fois. Or quatre défauts ne se valent pas :

  ABSENT DÉCLARÉ      le séif n'est pas reproduit, et la page le dit — elle annonce
                      une sélection (« Texte représentatif »), ou marque « … » à sa
                      place ;
  ABSENT NON DÉCLARÉ  le séif manque sans que rien ne le dise. Sous-cas aggravé :
                      le titre du bloc l'ANNONCE (« Texte original (séifim 12-16) »)
                      et le bloc ne le porte pas ;
  TRONCATURE          le séif est là, mais un passage d'au moins quatre mots
                      consécutifs manque — à la fin (la famille d'Orah Haïm 8 séif
                      10 : « או כשילבש טלית אחר … של ראשון » coupé dans les trois
                      langues), au début, ou à l'intérieur ; « déclarée » si la
                      page écrit « … » à l'endroit de la coupure ; la glose du Rama
                      est nommée quand c'est elle qui tombe ;
  ALTÉRATION          des mots changés : abréviation développée ou contractée PAR
                      RAPPORT À L'ÉDITION RETENUE (וי״א → ויש אומרים, הקב״ה → הקדוש
                      ברוך הוא — c'est ce qui a fait échouer les 50 premiers simanim
                      de Yoré Déa ; mais « לבה״כ » → « לבית הכסא » est la leçon de
                      TE, et n'est plus un écart quand la page suit TE), parenthèse de
                      source omise (« (טור) »), renvoi omis (« (וע״ל ס״ס נ״ד) »), mot
                      omis, mot remplacé. Sa nature est écrite sur la ligne : (leçon),
                      (parenthèse), (renvoi), (omission).

Et trois qui ne sont dans aucune des quatre, mais que la confrontation fait voir :

  DÉPLACÉ             le séif est reproduit, mais pas à sa place : la page
                      réordonne la source (règle « le Choul'han Aroukh est le
                      repère — ordre compris ») — au siman 90, le séif ד après les
                      séifim ה-ו ; au siman 61, la page regroupe par familles ;
  AJOUT               quatre mots ou plus dans un bloc source qui ne sont pas du
                      siman ;
  REPRISE             (information) un passage déjà donné, cité une seconde fois
                      pour l'analyser — au siman 22, la glose du Rama isolée sous
                      « Le din du Rama ». Ce n'est pas une infidélité et cela ne
                      fait pas diverger le siman ; la reprise est pourtant
                      confrontée MOT À MOT à son tour (tour 5, ``juger_reprise``) :
                      un mot changé, un yod/vav échangé, un mot de la source omis
                      sans « … » y sont une ALTÉRATION (reprise).

COMMENT : un alignement au MOT, non au caractère. Les deux textes sont découpés en
mots ; chaque mot est comparé par son squelette (consonnes sans yod ni vav, SAUF
l'initiale — le ktiv ne touche jamais la première lettre, le vav de conjonction
si — et SAUF le yod ou le vav final, grammatical, depuis le tour 2) ; un alignement
monotone (difflib) apparie la page à la source — et chaque paire que la clé apparie sans
être égale lettre pour lettre doit passer la garde ktiv (``ktiv_seul``, tour 4 ; dans les
REPRISES aussi depuis le tour 5) ; puis une
seconde passe cherche, bloc par bloc, les séifim que la première tient pour
absents : c'est ce qui sépare un séif ABSENT d'un séif DÉPLACÉ.

CE QUE L'ALIGNEMENT BRUT FAISAIT DIRE À TORT, ET QUI A ÉTÉ CORRIGÉ
-----------------------------------------------------------------
Chacun de ces faux verdicts a été vu en ouvrant la page et Sefaria côte à côte ;
chacun aurait suffi à rendre le relevé illisible.
- « ואם » valait « אם » quand le squelette ôtait TOUS les vav : le séif יד du
  siman 8 perdait son premier mot au profit du séif יג (d'où l'initiale gardée) ;
- un trou MORDAIT sur le séif suivant quand son dernier mot est aussi celui qui
  le précède : on le fait glisser, à texte égal, sur la frontière de séif ;
- l'îlot de deux mots « כשנפנה בשדה… » (siman 3, séif ח) était pris pour du
  bruit : un îlot n'en est un que si, DANS LA PAGE, il est lui-même entouré de
  mots que la source n'a pas ;
- le séif יד du siman 8 — 9 mots sur 43, « ואם פשט טליתו אפילו היה דעתו
  לחזור... » — était ABSENT au seul taux de mots : il est TRONQUÉ. Un séif n'est
  absent que si rien ne subsiste de lui : ni la moitié de ses mots, ni une suite
  de mots consécutifs (quatre, ou le tiers d'un séif court, deux au moins) ;
- les séifim ז du siman 53 et יא du siman 8, que la page place APRÈS un autre,
  passaient pour le remplacement d'un passage voisin ; le séif יט du siman 32
  était apparié à la fin du séif ח, qui dit aussi « לשם קדושת תפילין ». La
  seconde passe reprend ces mots — jamais à une suite d'au moins trois mots
  appariés de son propre séif (le séif י du siman 3, « לא יקנח ביד ימין », avait
  été vidé au profit du séif יא, « לא יקנח בחרס »), et pour un gain net ;
- les mots qu'une apostrophe abrège dans l'imprimé et que la page écrit en
  entier (« וכששפשפ׳ נטמא׳ חברת׳ », siman 162) gonflaient la troncature qui
  les suit : ils sont détachés aux bords d'un remplacement ;
- « דוראיתם » / « ד וראיתם » : le même texte, coupé autrement en mots ;
- un renvoi de source entre parenthèses n'est jamais une TRONCATURE du din ; ni un
  renvoi que TE imprime sans parenthèses (tour 2).

MESURE DU 8 OCTOBRE 2026 — les 241 simanim, 1 453 séifim, 723 pages
------------------------------------------------------------------
AVANT (ME seule) : 73 simanim IDENTIQUES, 7 ÉQUIVALENTS, 161 divergents (le pire des
trois pages : 14 ABSENT NON DÉCLARÉ, 1 ABSENT DÉCLARÉ, 56 TRONCATURE, 90 ALTÉRATION).
Par séif, chacun compté une fois sous son pire défaut : 609 conformes au ktiv près, 98
absents non déclarés (dont 66 ANNONCÉS par le titre de leur bloc), 41 absents déclarés
(le seul siman 32), 201 tronqués, 13 déplacés, 491 altérés.
APRÈS (l'édition la plus proche, séif par séif) : 78 IDENTIQUES, 12 ÉQUIVALENTS, 151
divergents (14 ABSENT NON DÉCLARÉ, 1 ABSENT DÉCLARÉ, 65 TRONCATURE, 71 ALTÉRATION). Par
séif : 751 conformes, 98 absents non déclarés, 40 absents déclarés, 233 tronqués, 13
déplacés, 318 altérés. Édition retenue : ME 804 séifs, TE 464, égalité 178 (les deux
exactement aussi proches), selon la langue de la page 7. Les mouvements, séif par séif :
141 ALTÉRATION → conformes (l'édition) ; 1 TRONCATURE → conforme (67:1, le chapeau) ;
2 TRONCATURE → ALTÉRATION (97:1, le chapeau ; 17:3, « ק״ש » absorbé dans la coupure) ;
1 ABSENT DÉCLARÉ → TRONCATURE (32:8 : « וצריך שיהא הקלף מעבד לשמו » est TE, « שיהי׳ »
chez ME) ; 34 ALTÉRATION → TRONCATURE (la garde des parenthèses : un passage que ME
seule met entre parenthèses — glose du Rama 175:2, 6:2, 159:20…, ou renvoi 71:1, 92:4…).
Les ABSENTS ne bougent pas : aucun n'était un effet d'édition.
Parité FR/HE/EN rompue dans 5 simanim (8, 10, 98, 128, 162) ; au siman 10, la page
FRANÇAISE seule omet la condition du séif ו, « אא״כ תפרה כולה ואפי׳ מרוח אחת ». Les
simanim 185 à 241 sont tous identiques ou équivalents.
TOUR 2 (R1-R3, renvois, finale du mot), sur le même instantané HEAD 7d4504d6 :
78 IDENTIQUES, 12 ÉQUIVALENTS, 151 divergents (14 ABSENT NON DÉCLARÉ, 1 ABSENT DÉCLARÉ,
59 TRONCATURE, 77 ALTÉRATION) — six simanim passent de TRONCATURE à ALTÉRATION (47 71 81
92 144 173 : leur seule troncature était un renvoi). Par séif : 750 conformes, 98
absents non déclarés, 40 absents déclarés, 219 tronqués, 13 déplacés, 333 altérés.
Mouvements depuis le tour 1 : 14 TRONCATURE → ALTÉRATION (13 renvois ; 61:21, une
troncature fictive de quatre mots née de « אותו » apparié à « את », que la finale
gardée défait) ; 1 CONFORME → ALTÉRATION (39:4, R3).
TOUR 3, même instantané : verdicts de siman INCHANGÉS (78 · 12 · 14 · 1 · 59 · 77). Par
séif : 748 conformes, 98, 40, 219, 13, 335 altérés — 2 CONFORME → ALTÉRATION (3:1, 4:8, la
finale). R3 : lignes [ME] ajoutées 3 séifs (9 × page), lignes annotées « absent aussi de
Torat Emet 363 » 4 → 9 séifs (12 → 25 × page), dont 6 séifs (16 × page) d'un ou deux mots
que le tour 2 aurait excusés si leur séif avait suivi TE (128:28, 128:39, 128:45, 160:7,
160:13, 160:15). GARDE 5 : deux séifs relus dans une autre édition, famille inchangée
(32:7 dans TE, une TRONCATURE fin de 89 mots au lieu de trois coupures nées de deux mots
égarés ; 160:9 dans ME, une TRONCATURE fin de 25 mots, ce que la page fait). « À SA
PLACE » : 2 lignes (32:14, 153:7). Pages qui recopient TE sur les 241 simanim : 23
simanim divergents, 29 séifs, tous par une omission que TE partage (22 séifs d'un ou deux
mots et les 8 du tour 2, 160:7 dans les deux), 0 autre ligne ; pages qui recopient ME :
241 IDENTIQUES, code 0.
TOUR 4 (9 octobre 2026), sur l'instantané HEAD 56151b14 — APRÈS les six lots qui ont restauré
le niveau 1 de 14 simanim (39d7d567..42140f53) ; relevé : audit/orah-haim-recopie-niveau1.txt.
Simanim (le pire des trois pages), porte de 7dd843b9 → tour 3 → tour 4 : IDENTIQUE 73 → 78 →
78 · ÉQUIVALENT 7 → 12 → 16 · ABSENT DÉCLARÉ 1 → 1 → 1 · TRONCATURE 62 → 65 → 65 · ALTÉRATION
98 → 85 → 81 · ABSENT NON DÉCLARÉ 0 partout (les lots les ont tous fermés). Séifs : conformes
719 → 867 → 916, absents déclarés 41 → 40 → 40, tronqués 136 → 148 → 148, déplacés 12, altérés
545 → 386 → 337. Du tour 3 au tour 4 : 49 séifs ALTÉRATION → CONFORME (leçons excusées), aucun
autre mouvement de verdict de séif ; 4 simanim ALTÉRATION → ÉQUIVALENT (23, 41, 44, 60).
TOUR 5 (9 octobre 2026), sur l'instantané HEAD 7991a335 — APRÈS les finitions des 14 simanim
(368bb709..b433e894) ; relevé : audit/orah-haim-recopie-niveau1.txt (sortie identique, au ROOT près,
sur 222c7197, dont les commits ne touchent aucun bloc text-source). Simanim, porte de 7dd843b9 →
tour 3 → tour 4 → tour 5 : IDENTIQUE 79 → 88 → 88 → 88 · ÉQUIVALENT 7 → 16 → 20 → 20 · ABSENT
DÉCLARÉ 1 partout · TRONCATURE 56 → 59 → 59 → 59 · ALTÉRATION 98 → 77 → 73 → 73 ; divergents 155 →
137 → 133 → 133. Séifs : conformes 814 → 968 → 1 004 → 1 005, absents déclarés 41 → 40, tronqués
124 → 136, déplacés 8, altérés 466 → 301 → 265 → 264. Du tour 4 au tour 5 : un seul séif bouge,
171:4 ALTÉRATION → CONFORME (le mot tronqué) ; les quatre reprises sont confrontées mot à mot,
sans écart. Les 14 simanim des lots : 261 séifs sur 261 CONFORMES (10 IDENTIQUES, 4 ÉQUIVALENTS :
55, 79, 90, 153 — leurs mots au ktiv près sont listés).

CE QUE DEVIENT LE COMPTE DE ``verifier-couverture-encadres.py``
--------------------------------------------------------------
Il annonçait 26 simanim d'Orah Haïm dont le niveau 1 ne reproduit qu'une partie,
264 séifim absents, 25 sans le déclarer. Il compte des BLOCS (séifim − blocs),
non des séifim. Sur la page française, ces 264 se répartissent en 133 séifim
réellement absents, dans 15 simanim — tous dans sa liste, aucun siman hors de sa
liste n'en a — et 131 séifim PRÉSENTS, regroupés à plusieurs dans un bloc
(« [יג] … [יד] … [טו] » au siman 4 : dix « absents », zéro en réalité). Onze de
ses 26 simanim n'ont aucun séif absent : 4, 27, 39, 40, 43, 46, 47, 61, 63, 150,
219 — dont le 61, que la page réordonne par familles (neuf séifim DÉPLACÉS). Des
15 restants, 14 omettent sans le dire ; le 32 seul l'annonce. Les trois pages
réunies, le siman 128 (11/8/16 blocs selon la langue) porte six absents de plus :
139 au lieu de 133. Après la réparation des éditions : 132 sur la page française et
138 les trois réunies — le séif ח du siman 32, réduit à cinq mots de TE, est une
TRONCATURE et non une absence.

PIÈGES TENUS
------------
- les marqueurs de séif que la page insère dans le bloc — « [ז] », « [י״א] » —
  sont des lettres hébraïques : lus comme texte, ils faisaient de la page de
  l'Orah Haïm 8 une divergence dès le séif 7. Ne sont retirés que les numéraux
  CANONIQUES entre crochets (« [לא] » oui, « (לא) » de Sefaria non, « [טור] » non) ;
- les ancres ``<i data-commentator>`` de Sefaria, le ``<b>`` du chapeau, le
  ``<small>`` du Rama : lus comme structure, jamais comme texte ;
- une étiquette « <strong>סעיף ח:</strong> » en tête de bloc n'est pas du texte ;
- Sefaria rend 200 et le livre entier sur un ref mal formé : le ``ref`` servi doit
  finir par le numéro demandé, sinon le siman est NON ATTEINT — avec sa raison — et
  jamais compté conforme ;
- ROOT se déduit de ``__file__`` : une copie lancée hors du dépôt lit « 0 page » et
  sort en 3, elle ne passe pas pour verte ;
- ``api/v3/texts`` rend des 504 passagers (un sur 241 au premier téléchargement) :
  trois essais, puis NON ATTEINT avec la raison — jamais un siman vide compté conforme.
"""
import argparse, difflib, html, importlib.util, json, os, re, sys, time, unicodedata
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = os.path.join(ROOT, "sources", "orah-haim")
CACHE = os.path.join(ROOT, "scripts", ".cache-sefaria", "recopie-oh-niveau1")
# v1 : une seule édition (api/texts, « he » par défaut), fichiers OH-N.json — périmés.
# v2 : toutes les éditions hébraïques servies (api/v3/texts, version=hebrew|all).
# v3 : + « listees » (available_versions) et « vides » — un v2 pouvait avoir été gravé
#      sans que rien ne prouve qu'il était complet (voir ``fetch``).
CACHE_VERSION = 3
LIVRE = "Shulchan_Arukh,_Orach_Chayim"
LANGS = [("FR", ""), ("HE", "-he"), ("EN", "-en")]
ED_DEFAUT = "Maginei Eretz: Shulchan Aruch Orach Chaim, Lemberg, 1893"
ED_TE = "Torat Emet 363"
SIGLES = {ED_DEFAUT: "ME", ED_TE: "TE"}
# R1 — les SEULES éditions de référence : l'édition par défaut et la Torat Emet numérotée.
# « Torat Emet Freeware » et « Wikisource » ne le sont jamais : désalignées par endroits
# (Freeware 344:1 est le texte du 343:1) et lacunaires (Freeware 252:2 saute « מלאכתו
# בשבת אם היה עושה »). Servies, elles sont ignorées, et la sortie le dit.
REFERENCES = (ED_DEFAUT, ED_TE)
# R2 — une édition alternative n'est admise pour un séif que si elle est ALIGNÉE sur le
# séif de même numéro de l'édition par défaut : ratio difflib des squelettes
# consonantiques (sans yod ni vav) des deux séifs. Mesuré le 8 octobre 2026 sur les
# 1 453 séifim : TE/ME au même séif, minimum 0,787 (222:2), 1 % sous 0,862 ; TE au séif
# s contre ME au séif s±1 (la forme exacte du désalignement de Freeware), maximum 0,651
# (39:6/39:5), médiane 0,222. Le seuil est pris dans le trou, à 0,72.
# LIMITE (tour 4, l'arbitre du tour 3) : un séif PARALLÈLE d'un autre siman, qui dit presque la même
# chose, passe ce seuil — TE 62:3 mis à la place de TE 185:2 est admis à 0,945 (témoin N18), et ses
# mots différents passent pour des leçons. La vraie TE est alignée sur les 1 453 séifs ; voir la
# docstring, TOUR 4.
SEUIL_ALIGNE = 0.72


def sigle(titre):
    """Le sigle imprimé dans les lignes de défaut ; une édition inconnue reçoit ses
    initiales (et le titre complet est imprimé en tête de siman)."""
    if titre in SIGLES:
        return SIGLES[titre]
    ini = "".join(w[0] for w in re.findall(r"[A-Za-z]+", titre)[:3]).upper()
    return ini or titre[:6]

TRONC_MIN = 4          # mots consécutifs absents au-delà desquels on parle de troncature
DEPLACE_SEUIL = 0.5    # part du séif retrouvée hors de sa place pour le dire DÉPLACÉ
ILOT_MAX = 2           # un îlot de 1-2 mots appariés au milieu d'un trou est du bruit

# Une page qui dit au lecteur qu'elle ne donne qu'une partie du siman. Le motif
# français est celui de verifier-couverture-encadres.py. L'hébreu et l'anglais n'y
# lisaient que des MOTS : « נציג » trouvait « הנציג של הציבור » (le chaliah tsibour,
# siman 53) et ratait la vraie formule, « טקסט מייצג » (siman 32) ; « representative »
# trouvait « the community's representative » (siman 53). On lit les FORMULES.
RE_DECL = re.compile(r'repr[ée]sentatif|s[ée]lection|extraits choisis'
                     r'|טקסט (?:מנוקד )?מייצג|representative (?:text|of each)', re.I)
RE_CHAPEAU = re.compile(r'^\s*<b>(.*?)</b>\s*(?:<br\s*/?>)?', re.S)
RE_TS = re.compile(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>', re.S)
RE_ETIQ = re.compile(r'^\s*<strong>\s*(?:סעיפים|סעיף|Seifim|Seif)\b[^<]*</strong>\s*')
RE_ANCRE = re.compile(r'<i\b[^>]*data-commentator[^>]*>\s*</i>', re.S)
RE_NOTE = re.compile(r'<sup[^>]*class="footnote-marker"[^>]*>.*?</sup>\s*'
                     r'<i[^>]*class="footnote"[^>]*>.*?</i>', re.S)
RE_TITRE = re.compile(r'<h([1-6])[^>]*>(.*?)</h\1>', re.S)
RE_BALISE = re.compile(r'<[^>]+>')
RE_BLOC_HTML = re.compile(r'</?(?:p|div|br|li|ul|ol|blockquote|h[1-6])\b[^>]*>', re.I)
QUOTES = "\"'״׳"
RE_MOT = re.compile(r'[א-ת]+(?:[' + QUOTES + r'][א-ת]+)*[' + QUOTES + r']?')
RE_MARQUEUR = re.compile(r'\[\s*([א-ת](?:[' + QUOTES + r']?[א-ת])?)[' + QUOTES + r']?\s*\]')
RE_ELLIPSE = re.compile(r'…|\.\s*\.\s*\.')

VAL = {"א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
       "י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60, "ע": 70, "פ": 80,
       "צ": 90, "ק": 100, "ר": 200, "ש": 300, "ת": 400}


def numeral(v):
    """L'écriture canonique d'un nombre en lettres : 15 → טו, 31 → לא."""
    out = ""
    for val, l in sorted(((v_, k) for k, v_ in VAL.items()), reverse=True):
        while v >= val:
            out += l
            v -= val
    return out.replace("יה", "טו").replace("יו", "טז")


def est_numeral(lettres):
    if not lettres or any(c not in VAL for c in lettres):
        return False
    return numeral(sum(VAL[c] for c in lettres)) == lettres


# ---------------------------------------------------------------- normalisation

def sans_nikoud(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def squelette(s):
    return re.sub(r"[יו]", "", s)


def cle_de(L):
    """La clé de comparaison d'un mot : l'initiale, puis les consonnes sans yod ni vav,
    puis le yod ou le vav FINAL s'il y en a un.

    L'initiale : le ktiv haser/malé ne la touche jamais ; le vav de conjonction, si.
    Sans cette réserve « ואם » valait « אם », et l'alignement appariait le « וְאִם » du
    séif יד du siman 8 à un « אם » du séif יג.

    La finale (réparé le 8 octobre 2026, tour 2) : ôter TOUT yod et tout vav rendait
    « יאמר » (ME 3:1) et « יאמרו » (TE) identiques, « ביד » et « בידו » (« ביד הראשון »
    → « בידו », 153:22), « חשיבו » et « חשיבי » — le nombre, la personne, un mot de plus,
    passaient pour du ktiv ; et « אותו » valait « את » (61:21 : une troncature FICTIVE de
    quatre mots). (Tour 4 : deux mots de même clé ne sont encore égaux au ktiv que s'ils
    passent ``ktiv_seul`` — un ÉCHANGE yod/vav, « כוס » / « כיס », n'en est pas.)
    Le ktiv haser/malé est une affaire de MATRES LECTIONIS intérieures ;
    la finale est grammaticale. Coût mesuré sur les 241 simanim, porte du tour 1
    inchangée par ailleurs : 19 lignes de défaut disparaissent et 21 apparaissent, sur
    1 568 ; aucun verdict de siman ne change, un verdict de séif (61:21, TRONCATURE →
    ALTÉRATION). Les 21 lues une à une : des alignements redressés et des mentions « la
    page suit ici … » ; aucun faux positif de ktiv (« עליו » / « עלו » et « ידיו » /
    « ידו » gardent la même clé)."""
    if not L:
        return "·"
    if len(L) > 1 and L[-1] in "יו":
        return L[0] + squelette(L[1:-1]) + L[-1]
    return L[0] + squelette(L[1:])


def cle_souple(L):
    """Pour retrouver un passage RÉORDONNÉ d'une édition à l'autre : squelette entier,
    sans vav de conjonction (« וסי׳ קס״ד » / « סי׳ קס״ד », 4:21)."""
    return squelette(L[1:] if L.startswith("ו") and len(L) > 2 else L)


FINALES = str.maketrans("ךםןףץ", "כמנפצ")


def ktiv_seul(a, b):
    """LA GARDE KTIV (tour 4). Deux mots de même clé (``cle_de``) ne sont égaux « au ktiv
    près » que si l'un s'obtient de l'autre en AJOUTANT seulement des yod et des vav — l'un
    est une sous-suite de l'autre, finales normalisées, et toutes les lettres en trop sont
    des yod ou des vav. Un ÉCHANGE yod/vav au même endroit est un AUTRE MOT : « כוס » (coupe)
    et « כיס » (poche), « מים » (eau) et « מום » (défaut), « יום » et « ים », « הוא » et
    « היא » ont la même clé, et aucun ne s'obtient de l'autre par ajout.

    Pourquoi la clé seule ne suffit pas : elle ôte yod et vav à l'intérieur du mot sans
    distinguer celui qu'on AJOUTE (le ktiv malé, « כל » / « כול ») de celui qu'on ÉCHANGE.
    L'arbitre l'a éprouvé (témoin N4b, siman 182 : « כוס פגום » → « כיס פגום », « מים » →
    « מום », dans les trois langues) : la porte certifiait ÉQUIVALENT, code 0, « CONFORME (au
    ktiv près) 7 », sans imprimer un seul des mots changés. Une relation « par ajout » n'est
    pas transitive — « כוס » et « כיס » sont tous deux un ajout à « כס » — : elle ne se met pas
    dans une clé ; on la vérifie sur chaque paire que la clé a appariée (``aligner``)."""
    a, b = a.translate(FINALES), b.translate(FINALES)
    if a == b:
        return True
    if len(a) > len(b):
        a, b = b, a
    # UN MOT DE DEUX LETTRES N'A PAS DE KTIV (garde ajoutée pour le témoin N4a de l'arbitre, « בתוך
    # שלשים יום » → « ים »). « ים » s'obtient de « יום » par ajout d'un vav : la règle de l'ajout seul
    # l'admettait. Mais ajouter une mater à un mot de deux lettres fait presque toujours un AUTRE mot
    # — « ים » / « יום », « סף » / « סוף », « קל » / « קול ». Le mot est donc rendu comme un mot
    # changé ; si l'AUTRE édition l'écrit ainsi au même endroit (« חל » de TE / « חול » de ME, « גב » /
    # « גוב », « על » / « עול », « רב » / « רוב »), la leçon est excusée par R3 (``excuser``).
    if len(a) <= 2:
        return False
    return _par_ajout(a, b)


def _par_ajout(a, b):
    """``b`` s'obtient-il de ``a`` (ou l'inverse) en AJOUTANT seulement des yod et des vav ?"""
    a, b = a.translate(FINALES), b.translate(FINALES)
    if len(a) > len(b):
        a, b = b, a
    # sous-suite, les lettres de b non lues toutes yod ou vav (programmation dynamique :
    # un yod de b peut être lu ou sauté, et le choix glouton n'est pas toujours le bon)
    n, m = len(a), len(b)
    ok = [False] * (n + 1)
    ok[0] = True
    for j in range(m):
        nouv = [False] * (n + 1)
        for i in range(n + 1):
            if not ok[i]:
                continue
            if b[j] in "יו":
                nouv[i] = True
            if i < n and a[i] == b[j]:
                nouv[i + 1] = True
        ok = nouv
    return ok[n]


class Mot:
    __slots__ = ("lettres", "cle", "abrev", "rama", "chapeau", "ref", "seif",
                 "bloc", "deb", "fin", "brut", "ed", "ailleurs", "paren", "absent_de")

    def __init__(self, brut, **kw):
        self.brut = brut
        self.lettres = re.sub(r"[^א-ת]", "", brut)
        self.cle = cle_de(self.lettres)      # voir cle_de : initiale et finale gardées
        self.abrev = any(q in brut for q in QUOTES)
        self.rama = kw.get("rama", False)
        self.chapeau = kw.get("chapeau", False)
        self.ref = kw.get("ref", False)
        self.paren = self.ref       # entre parenthèses dans SON édition (``ref`` peut être levé)
        self.seif = kw.get("seif", 0)
        self.bloc = kw.get("bloc", 0)
        self.deb = kw.get("deb", 0)
        self.fin = kw.get("fin", 0)
        self.ed = kw.get("ed", 0)
        # sigle d'une AUTRE édition → le mot y correspondant y est-il entre
        # parenthèses ? (rempli par ``marquer_ailleurs``)
        self.ailleurs = {}
        # R3 — sigles des éditions où ce mot (de l'édition par défaut) n'a AUCUN
        # correspondant : ni apparié, ni remplacé par un équivalent, ni déplacé
        # (rempli par ``marquer_absences``)
        self.absent_de = set()


def _mots_html(raw, seif=0, ed=0, chapeau=False):
    """Les mots d'un fragment de Sefaria, chacun avec ce qu'il est : Rama, renvoi
    de source entre parenthèses ou crochets.

    Le Rama est dans un ``<small>``. Mais un ``<small>`` porte aussi des renvois et
    des gloses ENTRE PARENTHÈSES, du Mehaber comme du Rama : ME écrit « <small>
    (פי' מקום שיכולים…)</small> » au milieu d'un séif du Mehaber (3:7), TE met tous
    ses renvois dans « <small><small>(טור)</small></small> ». Un mot entre parenthèses
    dans un ``<small>`` est donc du Rama si, et seulement si, le dernier mot hors
    parenthèses qui le précède l'est."""
    out = []
    small, prof, ctx_rama = 0, 0, False
    for piece in re.split(r"(<[^>]+>)", raw):
        if piece.startswith("<"):
            p = piece.lower()
            if p.startswith("<small"):
                small += 1
            elif p.startswith("</small"):
                small = max(0, small - 1)
            continue
        t = sans_nikoud(html.unescape(piece))
        for m in re.finditer(r"[\[(]|[\])]|" + RE_MOT.pattern, t):
            g = m.group(0)
            if g in "([":
                prof += 1
                continue
            if g in ")]":
                prof = max(0, prof - 1)
                continue
            if prof > 0:
                rama = small > 0 and ctx_rama
            else:
                rama = ctx_rama = small > 0
            out.append(Mot(g, rama=rama, chapeau=chapeau, ref=prof > 0, seif=seif, ed=ed))
    return out


def mots_source(seifim, ed=0):
    """Les mots d'une édition, chacun avec son séif et son édition. Le chapeau du
    siman (le premier ``<b>`` du séif א) n'en fait PAS partie : voir ``chapeau``."""
    out = []
    for i, raw in enumerate(seifim, 1):
        raw = RE_NOTE.sub(" ", RE_ANCRE.sub("", raw))
        if i == 1:
            raw = RE_CHAPEAU.sub(" ", raw, count=1)
        out += _mots_html(raw, seif=i, ed=ed)
    return out


def chapeau(seif1):
    """Les mots du chapeau du siman (« הנהגת בית הכסא. ובו יז סעיפים: »), ou []."""
    m = RE_CHAPEAU.match(RE_NOTE.sub(" ", RE_ANCRE.sub("", seif1)))
    return _mots_html(m.group(1), seif=1, chapeau=True) if m else []


def texte_bloc(raw):
    """Le texte lisible d'un bloc de la page, marqueurs de séif blanchis."""
    raw = RE_ETIQ.sub("", raw)
    raw = RE_NOTE.sub(" ", RE_ANCRE.sub("", raw))
    raw = RE_BLOC_HTML.sub(" ", raw)
    raw = RE_BALISE.sub("", raw)
    t = sans_nikoud(html.unescape(raw))
    marqueurs = []
    # Un numéral entre crochets À L'INTÉRIEUR d'une parenthèse n'est pas un marqueur de
    # séif de la page : c'est un renvoi de la source (TE 53:19 « (מהר״ם פדואה סי׳ ס״ד
    # ומהרי״ק שרש (מ״ד) [ל׳]) »). Le blanchir faisait accuser la page recopiant TE d'avoir
    # omis « ל׳ » (tour 3 : 53:19, 53:23, 55:21, 78:1, 143:2 sur des pages qui recopient TE).
    prof, dedans = 0, []
    for c in t:
        dedans.append(prof > 0)
        prof = prof + 1 if c == "(" else max(0, prof - 1) if c == ")" else prof

    def blanchir(m):
        lettres = re.sub(r"[^א-ת]", "", m.group(1))
        if dedans[m.start()]:
            return m.group(0)
        if est_numeral(lettres) and VAL.get(lettres[0], 999) <= 100:
            marqueurs.append(lettres)
            return " " * len(m.group(0))
        return m.group(0)

    return RE_MARQUEUR.sub(blanchir, t), marqueurs


def titre_avant(page, pos):
    t = None
    for m in RE_TITRE.finditer(page, 0, pos):
        t = m
    return re.sub(r"\s+", " ", RE_BALISE.sub("", t.group(2))).strip() if t else ""


# --------------------------------------------------------------------- source

RAISONS = {}
NON_GRAVES = {}     # siman → pourquoi la réponse n'a pas été gravée dans le cache


def _hebreu(v):
    return (v.get("actualLanguage") or v.get("language")) == "he"


def _non_vide(t):
    return any(re.sub(r"<[^>]+>", "", x).strip() for x in t)


# TOUR 3 — LE NOMBRE DE SÉIFIM ATTENDU. Le tour 2 prenait pour nombre de séifim celui
# de l'édition par défaut TELLE QUE SERVIE. L'arbitre a servi ME 211 tronquée (4 séifim
# sur 6) et TE entière : la porte écartait TE (« découpe différente »), gravait la
# réponse dans le cache et certifiait, code 0, une page à laquelle manquaient les séifim
# 5 et 6 ; ME et TE tronquées toutes deux, aucune garde ne voyait rien. Le nombre attendu
# vient désormais de data/seifim-count.json (tiré de Sefaria par generer-seifim-count.py,
# égal à ME sur les 241 simanim, mesuré le 8 octobre 2026), à défaut du chapeau du siman
# (« ובו ו סעיפים ») — moins sûr : il dit 9 au siman 219, qui en a 10.
_ATTENDUS = []
NOMBRES = {"אחד": 1, "שנים": 2, "שני": 2, "שלשה": 3, "שלושה": 3, "ארבעה": 4, "חמשה": 5,
           "חמישה": 5, "ששה": 6, "שבעה": 7, "שמנה": 8, "שמונה": 8, "תשעה": 9, "עשרה": 10}


def attendus():
    """{siman: séifim} de data/seifim-count.json, ou None (et la raison est imprimée)."""
    if not _ATTENDUS:
        p = os.path.join(ROOT, "data", "seifim-count.json")
        try:
            d = json.load(open(p, encoding="utf-8"))["orach-chayim"]
            _ATTENDUS.append({int(k): int(v) for k, v in d.items()})
        except Exception as e:
            print(f"  ⚠️  {p} illisible ({type(e).__name__}) : le nombre de séifim attendu sera lu "
                  "dans le chapeau du siman, moins sûr")
            _ATTENDUS.append(None)
    return _ATTENDUS[0]


def seifs_du_chapeau(seif1):
    """Le nombre de séifim que le chapeau de ME annonce (« ובו יז סעיפים », « ובו סעיף
    אחד », « ובו שלשה סעיפים »), ou None."""
    m = RE_CHAPEAU.match(RE_NOTE.sub(" ", RE_ANCRE.sub("", seif1 or "")))
    if not m:
        return None
    t = sans_nikoud(html.unescape(RE_BALISE.sub("", m.group(1))))
    if re.search(r"ובו\s+סעיף\s+אחד", t):
        return 1
    m = re.search(r"ובו\s+(\S+)\s+סעיפ", t)
    if not m:
        return None
    w = re.sub(r"[^א-ת]", "", m.group(1))
    if w in NOMBRES:
        return NOMBRES[w]
    v = sum(VAL.get(c, 0) for c in w)
    return v if w and all(c in VAL for c in w) else None


def attendu(n, me):
    """(nombre de séifim attendu, d'où il vient) — ou (None, None)."""
    a = attendus()
    if a and n in a:
        return a[n], "data/seifim-count.json"
    c = seifs_du_chapeau(me[0] if me else "")
    return (c, "le chapeau du siman") if c else (None, None)


def _seif_vide(x):
    return not re.sub(r"<[^>]+>", "", x or "").strip()


def lacunes(d, n):
    """Ce qui manque à une réponse pour être COMPLÈTE — liste vide : complète. Elle ne se
    grave, et ne se relit, que complète : le bon siman, ``available_versions`` connue,
    chaque édition servie non vide, les DEUX éditions de référence servies (Sefaria les
    sert toutes deux sur les 241 simanim), CHACUN de leurs séifs non vide (tour 3 : TE
    211:2 servi vide était gravé), au même nombre de séifim, et ce nombre celui qu'on
    attend (``attendu``). Les lacunes de l'édition par défaut rendent le siman NON ATTEINT
    (``fetch``) ; celles de TE, un siman confronté PARTIELLEMENT (``un_siman``)."""
    out = []
    if d.get("version") != CACHE_VERSION:
        out.append(f"version de cache {d.get('version')} ≠ {CACHE_VERSION}")
    if not str(d.get("ref", "")).rstrip().endswith(f" {n}"):
        out.append(f"ref {d.get('ref')!r} ≠ siman {n}")
    if not isinstance(d.get("listees"), list):
        out.append("available_versions absent de la réponse")
    eds = {e.get("titre"): e.get("he") for e in d.get("editions") or []}
    for t, he in eds.items():
        if not (he and _non_vide(he)):
            out.append(f"« {t} » servie vide")
    for t in d.get("manquantes") or []:
        if t in REFERENCES:
            out.append(f"« {t} » listée par Sefaria, non servie ou vide")
    me = eds.get(ED_DEFAUT)
    if not (me and _non_vide(me)):
        out.append(f"l'édition par défaut « {ED_DEFAUT} » non servie")
        return out
    for t in REFERENCES:
        he = eds.get(t)
        if t != ED_DEFAUT and not (he and _non_vide(he)):
            if f"« {t} » listée par Sefaria, non servie ou vide" not in out:
                out.append(f"« {t} » non servie")
            continue
        v = [i for i, x in enumerate(he, 1) if _seif_vide(x)]
        if v:
            out.append(f"{SIGLES.get(t, t)} : séif(s) {plages(v)} servi(s) VIDE(S)")
        if t != ED_DEFAUT and len(he) != len(me):
            out.append(f"{SIGLES.get(t, t)} a {len(he)} séifim, l'édition par défaut {len(me)}")
    att, d_ou = attendu(n, me)
    if att is not None and len(me) != att:
        out.append(f"l'édition par défaut sert {len(me)} séifim, {d_ou} en attend {att}")
    return out


def lacunes_me(lac):
    """Celles des lacunes qui touchent l'édition par défaut : le siman est alors NON ATTEINT."""
    return [x for x in lac if x.startswith("l'édition par défaut") or x.startswith("ME ")
            or ED_DEFAUT in x or x.startswith("ref ") or x.startswith("version ")]


def _complet(d, n):
    return not lacunes(d, n)


def fetch(n, rafraichir=False):
    """Les éditions hébraïques du siman, l'édition par défaut (ME) d'abord :
    ``{"ref", "editions": [{"titre", "he": [séifim bruts, avec balises]}], "listees":
    [titres hébreux d'available_versions], "vides": [servies vides], "manquantes":
    [listées ou servies, mais vides ou absentes]}`` — ou None, et alors RAISONS[n] dit
    pourquoi. Jamais de liste vide confondue avec un succès.

    LE CACHE NE GRAVE QU'UNE RÉPONSE COMPLÈTE (réparé au tour 2 — l'arbitre l'a
    éprouvé en sabotant la réponse) : une édition servie VIDE et absente
    d'``available_versions`` n'était pas comptée parmi les manquantes, et une réponse SANS
    ``available_versions`` passait pour complète — TE vidée et la liste ôtée, la porte
    gravait ME seule, et tous les passages suivants confrontaient à ME seule sans un mot.
    Désormais toute édition servie vide est manquante, et une réponse sans
    ``available_versions`` est lue mais jamais gravée (``NON_GRAVES``, imprimé).
    TOUR 3 : la complétude se juge aussi SÉIF PAR SÉIF et au NOMBRE de séifim attendu
    (``lacunes``) ; une lacune de l'édition par défaut rend le siman NON ATTEINT, une
    lacune de TE le rend PARTIEL (``un_siman`` : jamais certifié conforme, code 3)."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"OH-{n}.v{CACHE_VERSION}.json")
    if not rafraichir and os.path.exists(f):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if _complet(d, n):
                return d
        except Exception:
            pass
    u = f"https://www.sefaria.org/api/v3/texts/{LIVRE}.{n}?version=hebrew%7Call"
    d, err = None, None
    for essai in range(3):
        try:
            d = json.load(urllib.request.urlopen(u, timeout=60))
            break
        except urllib.error.HTTPError as e:
            err = e
            if e.code < 500:          # 4xx : redemander ne changera rien
                break
        except Exception as e:        # délai, coupure, 5xx déguisé : on réessaie
            err = e
        time.sleep(2 * (essai + 1))
    if d is None:
        RAISONS[n] = f"api/v3/texts injoignable : {type(err).__name__} {err}"[:160]
        return None
    ref = str(d.get("ref") or "")
    if d.get("error") or not ref.rstrip().endswith(f" {n}"):
        RAISONS[n] = f"ref servi {d.get('ref')!r} ≠ siman {n} demandé, error {d.get('error')!r}"
        return None
    editions, vides = [], []
    for v in d.get("versions") or []:
        if not _hebreu(v):
            continue
        t = v.get("text")
        t = t if isinstance(t, list) else ([t] if t else [])
        t = [x if isinstance(x, str) else " ".join(map(str, x)) for x in t]
        if _non_vide(t):
            editions.append({"titre": v.get("versionTitle") or "?", "he": t})
        else:
            vides.append(v.get("versionTitle") or "?")
    av = d.get("available_versions")
    listees = ([a.get("versionTitle") for a in av if _hebreu(a) and a.get("versionTitle")]
               if isinstance(av, list) else None)
    if not editions:
        RAISONS[n] = ("ref juste mais AUCUNE édition hébraïque non vide"
                      + (f" ({', '.join(vides)} vides)" if vides else "")
                      + " — le Mehaber n'a pas de lacune connue en Orah Haïm")
        return None
    editions.sort(key=lambda e: e["titre"] != ED_DEFAUT)
    servies = {e["titre"] for e in editions}
    manquantes = sorted(set(vides) | {t for t in listees or [] if t not in servies})
    out = {"version": CACHE_VERSION, "ref": ref, "editions": editions, "listees": listees,
           "vides": vides, "manquantes": manquantes}
    if ED_DEFAUT not in servies:
        # R3 se juge contre l'édition par défaut : sans elle, rien ne peut être conclu
        RAISONS[n] = (f"l'édition par défaut « {ED_DEFAUT} » n'est pas servie"
                      + (" (servie VIDE)" if ED_DEFAUT in vides else "")
                      + f" — servies : {', '.join(sorted(servies))}")
        return None
    lac = lacunes(out, n)
    lme = lacunes_me(lac)
    if lme:
        # ME tronquée, un séif de ME vide, ou un nombre de séifim qui n'est pas celui
        # qu'on attend : la page serait confrontée à un Choul'han Aroukh amputé
        RAISONS[n] = ("réponse INCOMPLÈTE de Sefaria — " + " ; ".join(lme) + " — rien n'est conclu"
                      + ("; si Sefaria a réellement redécoupé le siman, régénérer "
                         "data/seifim-count.json (scripts/generer-seifim-count.py)"
                         if any("en attend" in x for x in lme) else ""))
        return None
    if not lac:
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False)
    else:
        NON_GRAVES[n] = " ; ".join(lac)
    return out


# ----------------------------------------------------------------------- page

def chemin(n, suf):
    return os.path.join(SECTION, f"siman-{n}", f"niveau-1-base{suf}.html")


def lire_page(path):
    page = open(path, encoding="utf-8").read()
    mots, textes, titres, marqueurs = [], [], [], []
    for b, m in enumerate(RE_TS.finditer(page)):
        t, mk = texte_bloc(m.group(1))
        textes.append(t)
        marqueurs += mk
        titres.append(titre_avant(page, m.start()))
        for w in RE_MOT.finditer(t):
            mots.append(Mot(w.group(0), bloc=b, deb=w.start(), fin=w.end()))
    return {"html": page, "mots": mots, "textes": textes, "titres": titres,
            "marqueurs": marqueurs, "declare": RE_DECL.search(page), "chapeau": []}


def _chapeau_lu(chap, pm):
    """Combien de mots du chapeau, et combien de mots de la page, la page recopie-t-elle EN TÊTE,
    dans l'ordre, à partir du PREMIER mot du chapeau ? Chaque mot de la page doit être le mot
    suivant du chapeau (même clé), ou le développement d'une abréviation du chapeau (« ב״ה » →
    « בית הכנסת », siman 150 ; « י׳ » → « עשרה »), ou l'abréviation de mots du chapeau (« בק״ש »).
    La lecture s'arrête au premier mot qui ne suit pas. Rend (mots du chapeau, mots de la page,
    la dernière unité lue est-elle le DÉVELOPPEMENT d'une abréviation du chapeau ?)."""
    i = j = 0
    dev = False
    while i < len(chap) and j < len(pm):
        c, p = chap[i], pm[j]
        if c.cle == p.cle or ktiv_seul(c.lettres, p.lettres):     # « באיזהו » pour « באיזה » (66)
            i, j, dev = i + 1, j + 1, False
            continue
        pas = None
        # une lettre-nombre du chapeau, avec ou sans geresh (« ובו ה סעיפים »), écrite en toutes
        # lettres par la page (« ובו חמשה סעיפים », 97 ; « עשרה », 66)
        if len(c.lettres) <= 3 and est_numeral(c.lettres):
            v = sum(VAL[x] for x in c.lettres.translate(FINALES))
            for k in (2, 1):
                if j + k <= len(pm) and _valeur_mots([w.lettres for w in pm[j:j + k]]) == v:
                    pas = (1, k, False)
                    break
        # le développement le PLUS COURT (tour 8) : le plus long avalait un mot inséré dont
        # l'initiale prolongeait l'abréviation — « עכו״ם » → « עובדי כוכבים ומזלות מותר » (14),
        # « בהמ״ז » → « ברכת המזון זה » (182), les squelettes ignorant le vav
        if pas is None and c.abrev:
            for k in range(1, min(ABREV_MAX, len(pm) - j) + 1):
                if _abrege(c.lettres, [w.lettres for w in pm[j:j + k]],
                           gershayim=_gershayim(c), tronque=_tronque(c)):
                    pas = (1, k, True)
                    break
        if pas is None and p.abrev:
            for k in range(1, min(ABREV_MAX, len(chap) - i) + 1):
                if _abrege(p.lettres, [w.lettres for w in chap[i:i + k]],
                           gershayim=_gershayim(p), tronque=_tronque(p)):
                    pas = (k, 1, False)
                    break
        if pas is None:
            break
        i, j, dev = i + pas[0], j + pas[1], pas[2]
    return i, j, dev


def retirer_chapeau(pg, chap, sources):
    """La page recopie-t-elle le chapeau du siman en tête de son premier bloc — en
    entier, ou son début (« הַנְהָגַת בֵּית הַכִּסֵּא. כְּשֶׁיִּכָּנֵס… », siman 3) ? Ces
    mots-là sont retirés avant l'alignement : le chapeau n'est jamais un écart.

    Deux mots au moins. Et jamais quand le séif א d'une édition commence par les
    mêmes mots aussi loin : la page donnerait alors le séif, pas le chapeau.

    TOUR 7 — UNE SEULE RÈGLE, STRICTE (``_chapeau_lu``) : le chapeau est lu mot à mot, depuis
    son premier mot et dans l'ordre, au ktiv et aux abréviations près ; rien d'autre n'est du
    chapeau. Elle remplace le préfixe exact d'ici ET l'absorption par ressemblance qui suivait
    dans ``aligner_memo`` (tours 3 à 6) : celle-ci, réglée trois fois, avalait chaque fois un mot
    inséré en tête du séif א (« אינו קורא על מטתו », 239:1 ; « לא » devant 66:1 ; « לא אחד » au
    88 ; « לא » AVANT le chapeau au 24), et la page sortait IDENTIQUE, le din inversé.
    TOUR 8 (arbitre du tour 8) : devant une abréviation, le développement le PLUS COURT — le plus
    long avalait un mot inséré dont l'initiale prolongeait l'abréviation (« עכו״ם » → « עובדי
    כוכבים ומזלות מותר », 14 ; « בהמ״ז » → « ברכת המזון זה », 182) ; et une lecture PARTIELLE
    n'est retirée que si elle s'arrête à la fin du TITRE, juste avant « ובו » : ailleurs, le mot
    qui l'arrête peut être un mot inséré, y compris le mot SUIVANT du chapeau (« דיני כוס ברכת
    המזון ושלא יש אומרים… », 182). Sur les 241 pages réelles, toutes les lectures partielles qui
    retirent des mots s'arrêtent là (3, 13, 19, 21, 23) : coût nul, sortie identique à l'octet.
    CE QUI RESTE, et c'est une ALERTE, jamais un vert : un chapeau reformulé, un chapeau tronqué
    ailleurs qu'à la fin du titre, ou interrompu par un mot inséré, n'est pas retiré, et sa tête
    sort en AJOUT (témoins B0, W09c, Z03tc). LIMITE : une abréviation du chapeau se lit par ses
    initiales — « בק״ש » écrit « בלא קריאת שמע » se lit comme son développement."""
    pm = pg["mots"]
    nc, L, dev = _chapeau_lu(chap, pm)
    if nc < 2:
        return
    # une lecture PARTIELLE n'est un chapeau que si elle s'arrête à la fin du TITRE, juste avant
    # « ובו … סעיפים » (tour 8, règle de l'arbitre : sur les 241 pages réelles, toutes les lectures
    # partielles qui retirent des mots s'arrêtent là — 3, 13, 19, 21, 23). Ailleurs, le mot qui
    # arrête la lecture peut être un mot inséré (« דיני כוס ברכת המזון ושלא יש אומרים… », 182 :
    # « ושלא », mot SUIVANT du chapeau, ouvrait le séif) : rien n'est retiré, et la tête de la page
    # est confrontée — une alerte, jamais un vert.
    if nc < len(chap) and chap[nc].lettres != "ובו":
        return
    # et jamais sur le DÉVELOPPEMENT d'une abréviation du chapeau (tour 9, arbitre) : quand la page
    # ne recopie que le début du développement de la dernière abréviation du titre, un mot inséré
    # dont l'initiale est la lettre qui manque en devient la fin — « דיני בית הכסא בקריאת שאינו
    # אסור… » (83), « בקריאת » + « שאינו » lus comme « בק״ש », le din inversé et la page conforme ;
    # de même « ברכת המזמן » pour « בהמ״ז » (187), « ספר תמיד » pour « ס״ת » (149). Sur les 241
    # pages réelles, les seuls retraits avec développement sont des lectures COMPLÈTES (150, 239).
    if nc < len(chap) and dev:
        return
    cles = [w.cle for w in pm]
    for src in sources:
        s1 = [w.cle for w in src if w.seif == 1]
        M = 0
        while M < len(s1) and M < len(cles) and cles[M] == s1[M]:
            M += 1
        if M >= L:
            return
    pg["chapeau"], pg["mots"] = pm[:L], pm[L:]


# ------------------------------------------------------------------ alignement

def ellipse_a(pg, k):
    """La page marque-t-elle « … » entre son mot k-1 et son mot k ?"""
    mots, textes = pg["mots"], pg["textes"]
    morceaux = []
    if not mots:
        return any(RE_ELLIPSE.search(t) for t in textes)
    if k > 0:
        a = mots[k - 1]
        if k < len(mots) and mots[k].bloc == a.bloc:
            morceaux.append(textes[a.bloc][a.fin:mots[k].deb])
        else:
            morceaux.append(textes[a.bloc][a.fin:])
            if k < len(mots):
                morceaux.append(textes[mots[k].bloc][:mots[k].deb])
    else:
        morceaux.append(textes[mots[0].bloc][:mots[0].deb])
    return any(RE_ELLIPSE.search(x) for x in morceaux)


def glisser(src, pm, st, part, op_de):
    """Recale chaque suppression sur les frontières de séif quand c'est possible.

    Un alignement n'est pas unique : quand le mot qui précède un trou est aussi
    son dernier mot, le trou peut glisser d'un cran sans rien changer au compte.
    Au siman 8, la page coupe la fin du séif יג (« ואם מתפלל בתוך ביתו … ») et
    ouvre le séif יד par « ואם פשט טליתו » : l'alignement brut appariait le
    « ואם » de la page à celui du séif יג et rendait un trou qui MORDAIT sur le
    séif יד — « mot omis : ואם » au séif יד, troncature décalée d'un mot au séif
    יג. On fait glisser le trou, à texte égal, vers la position qui épouse le
    mieux les frontières de séif.
    """
    n = len(src)
    i = 0
    while i < n:
        if st[i] != "del":
            i += 1
            continue
        j = i
        while j < n and st[j] == "del" and op_de[j] == op_de[i]:
            j += 1
        cands = [(i, j)]
        a, b = i, j
        while a > 0 and st[a - 1] in ("eq", "ktiv") and src[b - 1].cle == src[a - 1].cle:
            a, b = a - 1, b - 1
            cands.append((a, b))
        a, b = i, j
        while b < n and st[b] in ("eq", "ktiv") and src[a].cle == src[b].cle:
            a, b = a + 1, b + 1
            cands.append((a, b))

        u0, u1 = min(c[0] for c in cands), max(c[1] for c in cands)
        partenaires = [part[x] for x in range(u0, u1) if not (i <= x < j)]

        def exacts(c):
            # TOUR 5 (l'arbitre du tour 4) : le nombre de mots appariés LETTRE POUR LETTRE dans la
            # fenêtre, si le trou est posé en c. Au siman 53 (séif יג), la page omet le crochet
            # « [עבדי ישעיה ערום תרגם עבדי ישעיה פחח] » qui suit « פוחח » : le « פוחח » de la page était
            # apparié au « פחח » qui FERME le crochet (même clé, un vav ajouté), et le trou posé au
            # DÉBUT du séif — « TRONCATURE début … « פוחח עבדי ישעיה … » », quand la page a bien « פוחח »
            # et que l'omission est INTÉRIEURE. À la frontière de séif, on préfère d'abord le mot
            # identique.
            # Puis le nombre de paires qui passent la garde ktiv (``ktiv_seul``) : un trou ne glisse
            # pas vers une position où il fabriquerait un yod/vav échangé.
            x, y = c
            ks = iter(partenaires)
            paires = [(src[z].lettres, pm[k].lettres) for z in range(u0, u1) if not (x <= z < y)
                      for k in [next(ks)] if k is not None]
            return (sum(1 for a_, b_ in paires if a_ == b_), sum(1 for a_, b_ in paires if ktiv_seul(a_, b_)))

        def score(c):
            x, y = c
            return exacts(c) + ((x == 0 or src[x - 1].seif != src[x].seif)
                                + (y == n or src[y].seif != src[y - 1].seif), c == (i, j))

        a, b = max(cands, key=score) if len(cands) > 1 else (i, j)
        if (a, b) != (i, j):
            op = op_de[i]
            for x in range(u0, u1):
                if a <= x < b:
                    st[x], op_de[x] = "del", op
                else:
                    k = partenaires.pop(0)
                    part[x], op_de[x] = k, None
                    st[x] = "eq" if src[x].lettres == pm[k].lettres else "ktiv"
            apres = next((part[x] for x in range(b, u1)), None)
            if apres is None:
                avant = next((part[x] for x in range(a - 1, u0 - 1, -1)), None)
                apres = None if avant is None else avant + 1
            for x in range(a, b):
                part[x] = apres
        i = max(j, b)


def complete(a, b):
    """b (page) écrit en entier le mot que a (source) abrège d'une apostrophe."""
    return (a.brut[-1] in QUOTES and len(a.lettres) >= 2 and len(b.lettres) > len(a.lettres)
            and b.lettres.startswith(a.lettres))


def coupe_autrement(a, b):
    """Les mots ``a`` (source) et ``b`` (page) sont-ils le même texte coupé autrement en
    mots (« דוראיתם » / « ד וראיתם ») ? Rend « eq » (mêmes lettres), « ktiv » (au ktiv
    près) ou None.

    TOUR 3 (l'arbitre du tour 2) : cette branche comparait les squelettes privés de TOUS
    les yod et vav, finale comprise — la finale gardée par ``cle_de`` y était perdue, et un
    remplacement d'UN mot par UN mot (« יאכלו » / « יאכל », « יאמרו » / « יאמר » : le nombre,
    la personne) redevenait du ktiv. Témoin : une page qui recopie ME 170 avec « שמא יאכל »
    sortait ÉQUIVALENT, code 0 ; et au séif א du siman 3, où la page suit TE, son « יאמר »
    (la leçon de ME) face au « יאמרו » de TE ne donnait pas une ligne. Désormais : mot pour
    mot (autant de mots des deux côtés), seules des lettres identiques passent — les clés
    en ont déjà jugé ; coupé autrement, la différence ne peut être qu'un yod ou un vav
    INTÉRIEUR à un mot, des deux côtés (ni initiale, ni finale)."""
    # finales normalisées (tour 4) : collés, « לכוון מלה » donne « לכווןמלה », dont le nun final est
    # au milieu — sans quoi aucun mot terminé par une finale ne se recolle jamais
    la = "".join(w.lettres for w in a).translate(FINALES)
    lb = "".join(w.lettres for w in b).translate(FINALES)
    if la == lb:
        return "eq" if len(a) != len(b) or all(x.lettres == y.lettres for x, y in zip(a, b)) else None
    if len(a) == len(b):
        return None

    def interieures(ws):
        f = []
        for w in ws:
            f += [0 < i < len(w.lettres) - 1 for i in range(len(w.lettres))]
        return f
    fa, fb = interieures(a), interieures(b)
    sens = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete" and all(la[i] in "יו" and fa[i] for i in range(i1, i2)):
            sens.add("source")
            continue
        if tag == "insert" and all(lb[j] in "יו" and fb[j] for j in range(j1, j2)):
            sens.add("page")
            continue
        return None
    # LA GARDE KTIV (tour 4, ``ktiv_seul``) : des yod/vav AJOUTÉS d'un seul côté. Un yod ôté
    # ici et un vav ajouté là, c'est un ÉCHANGE (« יוכל » / « יכול ») — un autre mot.
    if len(sens) > 1:
        return None
    return "ktiv"


def a_sa_place(src, st, part, s, premier, dernier):
    """Les mots de page [premier, dernier] sont-ils entre ceux des séifim qui
    précèdent s et ceux des séifim qui le suivent ?"""
    avant = [part[y] for y in range(len(src)) if src[y].seif < s and not src[y].chapeau
             and st[y] in ("eq", "ktiv") and part[y] is not None]
    apres = [part[y] for y in range(len(src)) if src[y].seif > s
             and st[y] in ("eq", "ktiv") and part[y] is not None]
    return (not avant or max(avant) < premier) and (not apres or min(apres) > dernier)


def aligner(src, pg, nseifs):
    """Apparie les mots de la page à ceux de la source.

    Rend ``st`` (pour chaque mot de source : 'eq', 'ktiv', 'del' ou 'rep'),
    ``op_de`` (l'opcode qui l'a rendu non apparié), ``part`` (la position de page
    où il se trouve, ou devrait se trouver), ``rep_page`` (opcode → mots de page
    qui le remplacent), ``deplace`` (séif → bloc où il a été retrouvé hors de
    sa place), ``ajouts`` (suites de mots de page qui ne sont à rien) et
    ``par_seif`` (séif → indices de ses mots, chapeau exclu).
    """
    pm = pg["mots"]
    A = [w.cle for w in src]
    B = [w.cle for w in pm]
    st = [None] * len(src)
    op_de = [None] * len(src)
    part = [None] * len(src)
    rep_page = {}                 # opcode -> [indices de page]
    apparie = [False] * len(pm)   # le mot de page est apparié à un mot de source
    rep_de = [None] * len(pm)     # le mot de page remplace un passage (opcode)
    pris = [False] * len(pm)      # repris par un séif déplacé
    ops = difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes()
    for o, (tag, i1, i2, j1, j2) in enumerate(ops):
        if tag == "equal":
            for d in range(i2 - i1):
                st[i1 + d] = "eq" if src[i1 + d].lettres == pm[j1 + d].lettres else "ktiv"
                part[i1 + d] = j1 + d
                apparie[j1 + d] = True
        elif tag == "replace" and coupe_autrement(src[i1:i2], pm[j1:j2]):
            # même texte, coupé autrement en mots : « דוראיתם » / « ד וראיתם »
            same = coupe_autrement(src[i1:i2], pm[j1:j2]) == "eq"
            for i in range(i1, i2):
                st[i] = "eq" if same else "ktiv"
                part[i] = j1
                # tour 4 : on garde la trace du passage recoupé, pour lister ses mots
                # sous ÉQUIVALENT (``paires_ktiv``) et ne pas les rejuger mot à mot
                op_de[i] = ("recoupe", i1, i2, j1, j2)
            for j in range(j1, j2):
                apparie[j] = True
        elif tag in ("replace", "delete"):
            if tag == "replace":
                # Les mots tronqués de l'imprimé (« וכששפשפ׳ נטמא׳ חברת׳ ») que la
                # page écrit en entier sont aux BORDS d'un remplacement : on les
                # détache, un par un, pour qu'ils soient dits « abréviation
                # développée » et ne gonflent pas le passage vraiment absent.
                while i1 < i2 and j1 < j2 and complete(src[i1], pm[j1]):
                    st[i1], op_de[i1], part[i1] = "rep", ("bord", o, i1), j1
                    rep_page[("bord", o, i1)] = [j1]
                    rep_de[j1] = ("bord", o, i1)
                    i1, j1 = i1 + 1, j1 + 1
                while i1 < i2 and j1 < j2 and complete(src[i2 - 1], pm[j2 - 1]):
                    st[i2 - 1], op_de[i2 - 1], part[i2 - 1] = "rep", ("bord", o, i2 - 1), j2 - 1
                    rep_page[("bord", o, i2 - 1)] = [j2 - 1]
                    rep_de[j2 - 1] = ("bord", o, i2 - 1)
                    i2, j2 = i2 - 1, j2 - 1
                if j1 == j2:
                    tag = "delete"
            for i in range(i1, i2):
                st[i] = "rep" if tag == "replace" else "del"
                op_de[i] = o
                part[i] = j1
            if tag == "replace":
                rep_page[o] = list(range(j1, j2))
                for j in range(j1, j2):
                    rep_de[j] = o
        # insert : la page a des mots que la source n'a pas — vus plus bas

    glisser(src, pm, st, part, op_de)

    # Îlots : 1-2 mots appariés au milieu de deux trous d'au moins TRONC_MIN mots
    # sont du bruit (« אם », « לא ») et ne sauvent pas le passage.
    i = 0
    while i < len(src):
        if st[i] in ("eq", "ktiv"):
            j = i
            while j < len(src) and st[j] in ("eq", "ktiv"):
                j += 1
            if j - i <= ILOT_MAX:
                g = i - 1
                while g >= 0 and st[g] in ("del", "rep"):
                    g -= 1
                d = j
                while d < len(src) and st[d] in ("del", "rep"):
                    d += 1
                # ... et seulement si, DANS LA PAGE, l'îlot est lui-même entouré
                # de mots que la source n'a pas : c'est la signature d'une
                # rencontre fortuite au milieu d'un texte étranger. Au siman 3, le
                # « כשנפנה בשדה... בבקעה » de la page est un îlot de deux mots entre
                # deux trous de la source — mais la page l'enchaîne à « הקדש », qui
                # est apparié : c'est le séif ח, coupé, et non du bruit.
                voisins = [k for k in (part[i] - 1, part[j - 1] + 1)
                           if part[i] is not None and part[j - 1] is not None and 0 <= k < len(pm)]
                isole = all(not apparie[k] for k in voisins)
                if (i - 1 - g) >= TRONC_MIN and (d - j) >= TRONC_MIN and isole:
                    for x in range(i, j):
                        if part[x] is not None:
                            apparie[part[x]] = False
                        st[x] = "del"
                        op_de[x] = ("ilot", i)
            i = j
        else:
            i += 1

    # Seconde passe : un séif que la première passe tient pour absent est-il
    # ailleurs dans la page ? On le cherche BLOC PAR BLOC, et l'on accepte de
    # reprendre des mots que la première passe avait appariés à un autre séif ou
    # pris pour le remplacement d'un autre passage — à condition que le gain soit
    # net. Deux cas l'ont imposé. Au siman 8, le séif יא suit le séif ו dans le
    # même bloc, et la première passe le lisait comme la paraphrase de la
    # parenthèse de source du séif ו. Au siman 32, le séif יט (« בתחלת הכתיבה
    # יאמר בפיו אני כותב לשם קדושת תפלין ») était apparié mot à mot à la fin du
    # séif ח, qui parle aussi de « לשם קדושת תפילין » : la page passait pour
    # altérer le séif ח et omettre le séif יט, quand elle donne le séif יט.
    deplace = {}
    par_seif = {}
    for x, w in enumerate(src):
        if not w.chapeau:
            par_seif.setdefault(w.seif, []).append(x)
    def en_place(s, premier, dernier):
        return a_sa_place(src, st, part, s, premier, dernier)

    blocs_page = {}
    for k, w in enumerate(pm):
        blocs_page.setdefault(w.bloc, [k, k + 1])[1] = k + 1
    for s in range(1, nseifs + 1):
        idx = par_seif.get(s, [])
        if not idx:
            continue
        cov = sum(1 for x in idx if st[x] in ("eq", "ktiv")) / len(idx)
        if cov >= DEPLACE_SEUIL:
            continue
        source_de = {part[y]: y for y in range(len(src))
                     if st[y] in ("eq", "ktiv") and part[y] is not None}
        dedans = set(idx)

        def solide(y):
            if y is None:
                return False
            g = d = y
            while g - 1 >= 0 and st[g - 1] in ("eq", "ktiv") and src[g - 1].seif == src[y].seif:
                g -= 1
            while d + 1 < len(src) and st[d + 1] in ("eq", "ktiv") and src[d + 1].seif == src[y].seif:
                d += 1
            return d - g + 1 >= 3
        cles_seif = [src[x].cle for x in idx]
        best = None
        for (k1, k2) in blocs_page.values():
            ops2 = difflib.SequenceMatcher(None, cles_seif, [pm[k].cle for k in range(k1, k2)],
                                           autojunk=False).get_opcodes()
            ancres = [i for i, o in enumerate(ops2)
                      if o[0] == "equal" and (o[2] - o[1] >= 2 or len(idx) <= 3)]
            if not ancres:
                continue
            o1, o2 = ancres[0], ancres[-1]

            def petit(o):
                return o[0] in ("replace", "equal") and o[2] - o[1] <= 3 and o[4] - o[3] <= 3

            # les bords du séif : « אם » → « ואם », « קדוש׳ וקדיש » → « קדושה וקדיש »
            # sont le séif, même si aucun n'est une ancre de deux mots
            for _ in range(2):
                if o1 > 0 and petit(ops2[o1 - 1]):
                    o1 -= 1
                if o2 < len(ops2) - 1 and petit(ops2[o2 + 1]):
                    o2 += 1
            m = sum(ops2[i][2] - ops2[i][1] for i in ancres)
            suite = max(ops2[i][2] - ops2[i][1] for i in ancres)
            pris_ici = [k1 + j for o in ops2[o1:o2 + 1] if o[0] in ("equal", "replace")
                        for j in range(o[3], o[4])]
            perte = sum(1 for k in pris_ici if apparie[k] and source_de.get(k) not in dedans)
            # On ne reprend jamais un mot qui tient à une suite d'au moins trois
            # mots appariés de son propre séif : c'est une reproduction, pas un
            # îlot. Au siman 3, le séif יא (« לא יקנח בחרס … ») venait reprendre
            # « לא יקנח » au séif י (« לא יקנח ביד ימין », reproduit en entier),
            # qui passait alors pour absent.
            if any(apparie[k] and source_de.get(k) not in dedans and solide(source_de.get(k))
                   for k in pris_ici):
                continue
            gain = m - perte
            if best is None or gain > best[0]:
                best = (gain, m, k1, ops2, o1, o2, perte, suite)
        if not best:
            continue
        gain, m, k1, ops2, o1, o2, perte, suite = best
        # Présent là-bas : la moitié du séif, ou une suite de mots consécutifs
        # (même critère que pour dire un séif absent — un séif à la fois déplacé
        # et tronqué, comme le séif יט du siman 32, n'en a pas la moitié). Et un
        # gain NET : ce que le séif y retrouve vaut au moins le double de ce qu'il
        # reprend à d'autres. Deux séifim de formulation voisine ne s'arrachent
        # donc pas leurs mots : l'un ne gagnerait que ce que l'autre perd.
        besoin = max(2, min(TRONC_MIN, -(-len(idx) // 3)))
        if not ((m / len(idx) >= DEPLACE_SEUIL or suite >= besoin) and m > cov * len(idx)
                and m >= 2 * perte and gain >= 2):
            continue
        for x in idx:
            if part[x] is not None and st[x] in ("eq", "ktiv"):
                apparie[part[x]] = False
            st[x], op_de[x], part[x] = "del", ("deplace", s), None

        def voler(k):
            # le mot de page était apparié ailleurs : il revient au séif retrouvé,
            # et son ancien partenaire redevient un trou
            y = source_de.get(k)
            if apparie[k] and y is not None and y not in dedans:
                st[y], op_de[y] = "del", ("vole", s)
                apparie[k] = False

        premier = dernier = None
        for o_i in range(o1, o2 + 1):
            tag, i1, i2, j1, j2 = ops2[o_i]
            if tag == "equal":
                for d in range(i2 - i1):
                    x, k = idx[i1 + d], k1 + j1 + d
                    voler(k)
                    st[x] = "eq" if src[x].lettres == pm[k].lettres else "ktiv"
                    part[x], op_de[x] = k, None
                    apparie[k] = True
                    premier = k if premier is None else min(premier, k)
                    dernier = k if dernier is None else max(dernier, k)
            elif tag in ("replace", "delete"):
                cle = ("deplace", s, o_i)
                for d in range(i2 - i1):
                    x = idx[i1 + d]
                    st[x] = "rep" if tag == "replace" else "del"
                    op_de[x], part[x] = cle, k1 + j1
                if tag == "replace":
                    for k in range(k1 + j1, k1 + j2):
                        voler(k)
                        pris[k] = True
                    rep_page[cle] = list(range(k1 + j1, k1 + j2))
        # Retrouvé À SA PLACE (entre le séif qui le précède et celui qui le suit
        # dans la page) : c'était un défaut d'alignement, pas un déplacement.
        # On garde le numéro du bloc, pas son titre : l'alignement est mémorisé
        # par mots et par blocs, et le titre est propre à la langue de la page.
        if not en_place(s, premier, dernier):
            deplace[s] = pm[premier].bloc

    # LA GARDE KTIV (tour 4, ``ktiv_seul``). La clé a apparié des mots que seul un yod ou un
    # vav intérieur sépare ; ceux qui ne s'obtiennent pas l'un de l'autre par AJOUT (« כוס » /
    # « כיס ») ne sont pas le même mot : chacun devient un remplacement d'un mot par un mot,
    # que ``classer_trou`` nomme « yod/vav échangé ». Un passage recoupé (``coupe_autrement``)
    # a été jugé en bloc, avec la même règle.
    for x in range(len(src)):
        if st[x] != "ktiv" or part[x] is None:
            continue
        o = op_de[x]
        if isinstance(o, tuple) and o[0] == "recoupe":
            continue
        k = part[x]
        if not ktiv_seul(src[x].lettres, pm[k].lettres):
            cle = ("ktiv", x)
            st[x], op_de[x] = "rep", cle
            rep_page[cle] = [k]
            apparie[k] = False

    # Les remplacements de la première passe ne gardent que les mots de page
    # restés libres : ni appariés, ni repris par un séif déplacé.
    for o in list(rep_page):
        if not (isinstance(o, tuple) and o[0] == "deplace"):
            rep_page[o] = [k for k in rep_page[o] if not apparie[k] and not pris[k]]
    dans_rep = {k for v in rep_page.values() for k in v}
    # Les mots de la page qui ne sont à rien : ajouts.
    ajouts, k = [], 0
    libre = [not apparie[k] and k not in dans_rep for k in range(len(pm))]
    while k < len(pm):
        if libre[k]:
            k2 = k
            while k2 < len(pm) and libre[k2]:
                k2 += 1
            ajouts.append((k, k2))
            k = k2
        else:
            k += 1
    return st, op_de, part, rep_page, deplace, ajouts, par_seif


def une_lettre(a, b):
    """a et b diffèrent d'une seule lettre (ajoutée, retirée ou changée)."""
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def extrait(mots, n=7):
    b = [w.brut for w in mots]
    if len(b) <= 2 * n:
        return " ".join(b)
    return " ".join(b[:n]) + " … " + " ".join(b[-3:])


def _nouveau():
    return {"familles": [], "lignes": [], "info": [], "ktiv": False}


def _ligne(d, fam, texte, **info):
    """Une ligne de défaut et ce qu'elle est, sans relire son texte : ``nature`` (absent,
    troncature, renvoi, parenthèse, omission, leçon, ordre, ajout, reprise), ``run`` (les
    mots de l'édition qui manquent à la page, pour R3), ``rama``, ``abrev``, ``suit``,
    ``pos``, ``decl``, ``sig`` (l'édition de la ligne quand ce n'est pas celle du séif).
    Les compteurs lisent ces champs : lire le texte (« "Rama" in ligne ») comptait un
    RENVOI parmi les troncatures « portant sur le Rama »."""
    d["familles"].append(fam)
    d["lignes"].append(texte)
    d["info"].append(info)


# Un RENVOI : « ועיין ביו״ד סי׳ שמ״א », « וע״ל ס״ס נ״ד », « (הגה ועיין לעיל סי׳ קע״ח) ».
# ME l'imprime entre parenthèses ou crochets ; TE souvent dans un <small> SANS
# parenthèses — et un <small> hors parenthèses est la marque du Rama : la porte du tour 1
# appelait « la glose du Rama » le renvoi « ועין ביורה דעה סי׳ שמ״א » (71:1). Un renvoi
# est un passage qu'une édition au moins met entre parenthèses, et qui s'ouvre (« הגה »
# éventuel passé) sur la formule « voir » — en toutes lettres, ou abrégée AVEC son signe
# d'abréviation (« ועל » sans guillemet est « et sur »).
VOIR = {"עיין", "ועיין", "עין", "ועין"}
VOIR_ABREV = {"על", "ועל", "עי", "ועי", "ע", "וע", "עיי", "ועיי", "עש", "ועש"}
EXPLIQUE = {"פירוש", "פרוש", "ופירוש", "ופרוש"}
EXPLIQUE_ABREV = {"פי", "ופי"}     # « פ׳ » seul est aussi « פרק » (153:14 « (מרדכי ריש פ׳ בני העיר) »)
RENVOI_MAX = 16      # mots ; au-delà, « עיין … » ouvre une glose, pas un renvoi
REF_MOTS = {"סימן", "סי", "סעיף", "סעיפים", "לעיל", "לקמן", "ריש", "סוף", "ובסוף", "וסוף",
            "ביורה", "דעה", "בחשן", "בחושן", "משפט", "באבן", "העזר", "שם", "בפנים", "ובסימן",
            "וסימן", "וסי", "בסימן", "בסי"}


def _entre_par_une(w):
    return w.paren or any(w.ailleurs.values())


def _marque_ref(w):
    """Un mot de renvoi : « סי׳ », « סעיף », « לעיל », un numéral (« קע״ח », « צ׳ »),
    « בי״ד » — ou un mot qu'une édition met entre parenthèses (la source qui suit)."""
    return (w.lettres in REF_MOTS or _entre_par_une(w)
            or (w.abrev and len(w.lettres) <= 4))


def nature_par(run):
    """« renvoi », « explication » (« (פי׳ מיאני) », « (פירוש בפעם אחת) ») ou None.

    Un renvoi s'ouvre (« הגה » passé) sur la formule « voir », et c'est ou bien un
    passage qu'une édition au moins met entre parenthèses (« (וע״ל סי׳ נ״ה סכ״ב אם כופין
    זה את זה לשכור להם מנין) », 150:1), ou bien la formule suivie de SEULES marques de
    référence (« וע״ל סי׳ צ׳ סעיף י׳ [מהרי״ל וד״ע] », 68:1, que les deux éditions donnent
    sans parenthèses dans la glose du Rama). « עיין בי״ד סי׳ ר״א ס״ל יש מי … » (quatre-
    vingt-cinq mots, 160:12) n'est ni l'un ni l'autre : c'est une glose."""
    if not run:
        return None
    mots = run[1:] if run[0].lettres == "הגה" and len(run) > 1 else run
    t = mots[0]
    voir = t.lettres in VOIR or (t.abrev and t.lettres in VOIR_ABREV)
    if voir and len(run) <= RENVOI_MAX and (all(_entre_par_une(w) for w in run)
                                            or all(_marque_ref(w) for w in mots[1:])):
        return "renvoi"
    if not all(_entre_par_une(w) for w in run):
        return None
    if t.lettres in EXPLIQUE or (t.abrev and t.lettres in EXPLIQUE_ABREV):
        return "explication"
    return None


def classer_trou(run, page_rep, k, pg, pos, s, autres=(), sig_ed=("ME",), reprise_rep=None):
    """Le nom d'un passage de l'édition qui manque à la page, ou que la page remplace.
    Rend (famille, texte, info). ``k`` : la position de page où il devrait être."""
    n = len(run)
    tout_rama = all(w.rama for w in run)
    un_rama = any(w.rama for w in run)
    tout_ref = all(w.ref for w in run)
    np_ = nature_par(run)
    dans_par = " (entre parenthèses)" if tout_ref else ""
    court = not page_rep or len(page_rep) * 2 < n
    rep = (f" (à sa place : « {extrait(page_rep)} »)" if page_rep else "")
    if np_ == "renvoi" and court:
        # un renvoi n'est jamais une troncature du DIN, ni la glose du Rama
        return ("ALTÉRATION", f"ALTÉRATION (renvoi) — renvoi omis : « {extrait(run)} »{rep}"
                + _ailleurs(run, sig_ed), dict(nature="renvoi", run=run, k=k))
    if tout_ref and court:
        # un passage que TOUTES les éditions mettent entre parenthèses
        return ("ALTÉRATION", f"ALTÉRATION (parenthèse) — passage entre parenthèses omis : "
                f"« {extrait(run)} »{rep}", dict(nature="parenthèse", run=run, k=k))
    if page_rep and not (n >= TRONC_MIN and len(page_rep) * 2 < n):
        # TOUR 4 — L'OMISSION CACHÉE DANS UN REMPLACEMENT. Un remplacement n'était une omission
        # que si la page y avait moins de la moitié des mots ; « ואלהי אבותינו כו׳ » → « ואלהי
        # וכו׳ » (128:10) sortait « abréviation développée ou changée », et un mot de la source
        # sans AUCUNE contrepartie en face était excusé avec ses voisins. Chaque mot de la source
        # cherche sa contrepartie (``_contreparties``) ; ceux qui n'en ont pas sont une omission,
        # nommée comme toute omission (mot omis, parenthèse, renvoi, troncature), le remplacement
        # rappelé à la suite.
        sans, paires, _t = _contreparties(run, page_rep)
        if sans:
            fam, t, info = classer_trou(sans, [], k, pg, pos, s, autres, sig_ed)
            info["cache"] = True
            return fam, (t + f" — dans un remplacement : « {extrait(run)} » → « {extrait(page_rep)} »"), info
        att = _suit(run, page_rep, s, autres)
        info = dict(nature="leçon", suit=bool(att), src_run=run)
        if _interverti(run, page_rep, paires):
            # tour 4 : une interversion n'est pas une « abréviation développée ou changée »
            # (« הולכים ואוכלי׳ » → « אוכלים והולכים », témoin N2b de l'arbitre)
            info["interverti"] = True
            t = (f"ALTÉRATION (leçon) — mots intervertis{dans_par} : "
                 f"« {extrait(run)} » → « {extrait(page_rep)} »{att}")
        elif any(w.abrev for w in run) or any(w.abrev for w in page_rep):
            info["abrev"] = True
            t = (f"ALTÉRATION (leçon) — abréviation développée ou changée{dans_par} : "
                 f"« {extrait(run)} » → « {extrait(page_rep)} »{att}")
        elif n == 1 and len(page_rep) == 1 and run[0].cle == page_rep[0].cle:
            # tour 4, la garde ktiv : même clé, mais ni l'un ni l'autre ne s'obtient par ajout
            # de yod/vav — « כוס » / « כיס », « מים » / « מום » ; ou un mot de deux lettres
            # (« ים » / « יום ») : voir ``ktiv_seul``
            info["yodvav"] = True
            if _par_ajout(run[0].lettres, page_rep[0].lettres):
                quoi = "mot de deux lettres, une mater ajoutée ou ôtée en fait un autre mot (pas du ktiv)"
            else:
                quoi = "yod/vav ÉCHANGÉ, un autre mot (pas du ktiv haser/malé)"
            t = (f"ALTÉRATION (leçon) — {quoi}{dans_par} : "
                 f"« {run[0].brut} » → « {page_rep[0].brut} »{att}")
        elif n == 1 and len(page_rep) == 1 and une_lettre(run[0].lettres, page_rep[0].lettres):
            t = f"ALTÉRATION (leçon) — une lettre{dans_par} : « {run[0].brut} » → « {page_rep[0].brut} »{att}"
        else:
            t = f"ALTÉRATION (leçon) — mots changés{dans_par} : « {extrait(run)} » → « {extrait(page_rep)} »{att}"
        return "ALTÉRATION", t, info
    if n >= TRONC_MIN:
        rama = (tout_rama or un_rama) and np_ is None
        decl = k is not None and ellipse_a(pg, k)
        if np_ == "explication":
            quoi = "une explication entre parenthèses"
        elif rama:
            quoi = "la glose du Rama" if tout_rama else "dont la glose du Rama"
        else:
            quoi = ""
        r = f", remplacés par « {extrait(list(page_rep), 4)} »" if page_rep else ""
        t = (f"TRONCATURE {pos} — {n} mots consécutifs non reproduits"
             f"{' (' + quoi + ')' if quoi else ''}{r}, "
             f"{'déclarée par « … »' if decl else 'NON déclarée'} : « {extrait(run)} »"
             + _ailleurs(run, sig_ed))
        return "TRONCATURE", t, dict(nature="troncature", run=run, k=k, rama=rama, pos=pos, decl=decl)
    decl = " (déclaré par « … »)" if (not page_rep and k is not None and ellipse_a(pg, k)) else ""
    quoi = ("mot « הגה » omis (l'étiquette de la glose)"
            if [w.lettres for w in run] == ["הגה"] and not page_rep else "mot(s) omis")
    # tour 3 : un mot omis de la glose du Rama est dit tel (« חשוב או », 211:5)
    if un_rama and np_ is None and quoi == "mot(s) omis":
        quoi += " de la glose du Rama"
    t = (f"ALTÉRATION (omission) — {quoi}{decl} : « {extrait(run)} »"
         + (f" → « {extrait(page_rep)} »{_suit(run, page_rep, s, autres)}" if page_rep else "")
         # la parenthèse se dit aussi d'un mot omis (8:5 « פרוש בפעם אחת », entre
         # parenthèses dans ME, dans un <small> nu dans TE)
         + _ailleurs(run, sig_ed))
    return "ALTÉRATION", t, dict(nature="omission", run=run, k=k)


def analyser(src, pg, nseifs, al=None, sig_me=None, sig_ed=("ME",), autres=(), propre=None):
    st, op_de, part, rep_page, deplace, ajouts, par_seif = al or aligner(src, pg, nseifs)
    pm = pg["mots"]
    kof = {id(w): k for k, w in enumerate(pm)}
    titres = pg["titres"]
    annonces = {}
    va = _va()
    if va:
        for b, t in enumerate(titres):
            try:
                nums = va.numeros(t) or []
            except Exception:
                nums = []
            for s in nums:
                annonces.setdefault(s, t)
    taille_op, seif_de_op = {}, {}
    for x, o in enumerate(op_de):
        if o is not None:
            taille_op[o] = taille_op.get(o, 0) + 1
            seif_de_op.setdefault(o, set()).add(src[x].seif)
    res = {}
    for s in range(1, nseifs + 1):
        idx = par_seif.get(s, [])
        d = _nouveau()
        if not idx:
            res[s] = d
            continue
        ok = [x for x in idx if st[x] in ("eq", "ktiv")]
        d["ktiv"] = any(st[x] == "ktiv" for x in idx)
        cov = len(ok) / len(idx)
        # Un séif n'est ABSENT que si rien de lui ne subsiste : ni la moitié de ses
        # mots, ni une seule suite de TRONC_MIN mots consécutifs. Le seul taux de
        # mots appariés déclarait absent le séif יד du siman 8, que la page donne
        # bel et bien — « ואם פשט טליתו אפילו היה דעתו לחזור... צריך לברך
        # כשיחזור » —, amputé de la glose du Rama : 9 mots sur 43. C'est une
        # TRONCATURE, et la page ne ment pas sur le même point qu'un séif absent.
        # Un mot remplacé par son développement (אפי׳ → אפילו) ou par un mot
        # voisin est À SA PLACE dans la page : il ne rompt pas la suite. Un grand
        # remplacement, lui, n'est pas une présence — c'est autre chose à la place.
        suite = plus = 0
        for x in idx:
            present = st[x] in ("eq", "ktiv") or (
                st[x] == "rep" and rep_page.get(op_de[x]) and
                (src[x].abrev or taille_op.get(op_de[x], 0) <= 3))
            suite = suite + 1 if present else 0
            plus = max(plus, suite)
        # La suite exigée se proportionne au séif : quatre mots dans un séif long,
        # trois dans un séif de sept — « מותר לסייע בבצים » est le séif טו du
        # siman 3, amputé de « אפי׳ מי שאינו נשוי » derrière un « … » — deux dans
        # un séif de trois à cinq mots.
        # Ce que la page donne À LA PLACE du séif (tour 3, l'arbitre du tour 2) : un séif
        # remplacé par celui d'un AUTRE siman (39:5 remplacé par 38:5) n'était dit
        # qu'ABSENT — les onze mots étrangers n'étaient nommés nulle part, ni comme AJOUT
        # (l'alignement les tient pour le remplacement du séif), ni sur la ligne.
        # On ne nomme que le remplacement PROPRE au séif — un remplacement qui couvre
        # plusieurs séifs absents (siman 90 : un mot de la page « בעשרה » face à dix
        # séifim) ne dit rien de l'un d'eux.
        place, vus_o = [], set()
        for x in idx:
            o = op_de[x]
            if st[x] == "rep" and o in rep_page and o not in vus_o:
                vus_o.add(o)
                if seif_de_op.get(o) == {s}:
                    place += [k for k in rep_page[o] if k not in place]
        place = [pm[k] for k in sorted(place)]
        a_sa_place_txt = (f" ; À SA PLACE, {len(place)} mot(s) qui ne sont pas ce séif : « {extrait(place)} »"
                          if place else "")
        if cov < 0.5 and plus < max(2, min(TRONC_MIN, -(-len(idx) // 3))):
            # Réduit, pas absent : la page garde quelques mots pleins du séif, à
            # sa place, réécrits autour. Au siman 32 le séif ח (29 mots) n'est
            # plus que « וצריך שיהא הקלף מעבד לשמו » : le dire ABSENT surestime
            # l'écart, le taire le sous-estime ; c'est une TRONCATURE, et la ligne
            # dit ce qui en reste.
            propres = [x for x in idx if st[x] in ("eq", "ktiv") and len(src[x].lettres) >= 3]
            # ... à SA place : deux mots d'un autre séif que l'alignement a laissés
            # libres (« והיה … שמע » du séif א, au siman 32) ne font pas le séif יד
            # Trois mots pleins au moins (deux dans un séif court) : « נושא כפיו »
            # revient dans dix séifim du siman 128 et n'en signe aucun.
            if (len(propres) >= 3 or (len(propres) >= 2 and len(idx) <= 12)) and a_sa_place(src, st, part, s, min(part[x] for x in propres),
                                                max(part[x] for x in propres)):
                restes = [pm[part[x]] for x in propres]
                _ligne(d, "TRONCATURE",
                       f"TRONCATURE — séif réduit à {len(propres)} mot(s) sur {len(idx)}, "
                       f"réécrit autour : « {extrait(restes)} » ; source : « {extrait([src[x] for x in idx])} »"
                       + a_sa_place_txt,
                       nature="troncature", reduit=True, pos="réduit", place=len(place),
                       run=[src[x] for x in idx if st[x] not in ("eq", "ktiv")], k=part[propres[0]])
                res[s] = d
                continue
            k = part[idx[0]] if part[idx[0]] is not None else 0
            if pg["declare"]:
                quoi, decl = "ABSENT DÉCLARÉ", f"la page annonce une sélection (« {pg['declare'].group(0)} »)"
            elif ellipse_a(pg, k):
                quoi, decl = "ABSENT DÉCLARÉ", "« … » à sa place"
            else:
                quoi, decl = "ABSENT NON DÉCLARÉ", "rien ne le dit au lecteur"
            if quoi == "ABSENT NON DÉCLARÉ" and s in annonces:
                decl = f"ANNONCÉ par le titre « {annonces[s][:70]} » et absent du bloc"
            _ligne(d, quoi, f"{quoi} — {len(idx)} mots, {decl} : « {extrait([src[x] for x in idx])} »"
                   + a_sa_place_txt,
                   nature="absent", run=[src[x] for x in idx], k=k, annonce="ANNONCÉ par le titre" in decl,
                   place=len(place))
            res[s] = d
            continue
        if s in deplace:
            b = deplace[s]
            t = titres[b]
            _ligne(d, "DÉPLACÉ", f"DÉPLACÉ — reproduit hors de l'ordre de la source, au bloc {b + 1}"
                   + (f" (« {t[:60]} »)" if t else ""), nature="ordre")
        # trous : suites contiguës de mots non appariés. Les SUPPRESSIONS
        # contiguës forment un seul passage, même venues de deux opcodes (un îlot
        # retiré entre elles) ; un REMPLACEMENT reste à part, sans quoi
        # « וכששפשפ׳ נטמא׳ חברת׳ » → « וכששפשפה נטמאת חברתה » (siman 162,
        # abréviations développées, mots PRÉSENTS) gonflait de trois mots la
        # troncature de 124 mots qui le suit.
        x = 0
        while x < len(idx):
            if st[idx[x]] in ("eq", "ktiv"):
                x += 1
                continue
            y = x + 1
            if st[idx[x]] == "del":
                while y < len(idx) and st[idx[y]] == "del":
                    y += 1
            else:
                while (y < len(idx) and st[idx[y]] == "rep"
                       and op_de[idx[y]] == op_de[idx[x]]):
                    y += 1
            run = [src[idx[z]] for z in range(x, y)]
            page_rep, vus = [], set()
            for z in range(x, y):
                o = op_de[idx[z]]
                if st[idx[z]] == "rep" and o in rep_page and o not in vus:
                    vus.add(o)
                    page_rep += [pm[k] for k in rep_page[o]]
            fin_seif = all(st[idx[z]] not in ("eq", "ktiv") for z in range(y, len(idx)))
            deb_seif = all(st[idx[z]] not in ("eq", "ktiv") for z in range(0, x))
            pos = ("fin" if fin_seif else "début" if deb_seif else "intérieure")
            fam, texte, info = classer_trou(run, page_rep, part[idx[x]], pg, pos, s, autres, sig_ed)
            if info.get("nature") == "leçon":
                # tour 4 : les positions de page de la leçon, pour juger si une AUTRE édition
                # la porte au même endroit (``excuser``, R3)
                info["pk"] = [kof[id(w)] for w in page_rep]
            _ligne(d, fam, texte, **info)
            x = y
        res[s] = d

    # Ajouts : rattachés au séif qui précède le point d'insertion.
    src_de_page = {}
    for x, k in enumerate(part):
        if k is not None and st[x] in ("eq", "ktiv"):
            src_de_page.setdefault(k, x)
    toutes = [w.cle for w in src]
    for (k1, k2) in ajouts:
        prec = None
        for k in range(k1 - 1, -1, -1):
            if k in src_de_page:
                prec = src[src_de_page[k]].seif
                break
        s = prec or 1
        mots = pm[k1:k2]
        if len(mots) >= TRONC_MIN:
            # Une REPRISE n'est pas un ajout : la page cite une seconde fois, pour
            # l'analyser, un passage qu'elle a déjà donné — au siman 5, le séif
            # unique en entier puis découpé en trois « composantes » ; au siman 22,
            # la glose du Rama isolée sous « Le din du Rama ». La concaténation des
            # blocs n'est alors plus le siman, et les portes sœurs le déclarent
            # divergent ; ce n'est pourtant pas une infidélité à la source. Elle
            # est nommée, comptée à part, et confrontée à son tour : une reprise
            # dont les mots ne sont pas ceux de la source est une ALTÉRATION.
            sm = difflib.SequenceMatcher(None, toutes, [w.cle for w in mots], autojunk=False)
            blocs = [b for b in sm.get_matching_blocks() if b.size >= 2]
            couverts = sum(b.size for b in blocs)
            if couverts / len(mots) >= 0.6:
                seifs = sorted({src[b.a + d].seif for b in blocs for d in range(b.size)})
                cible = seifs[0]
                # TOUR 5 (l'arbitre du tour 4) : la reprise est confrontée MOT À MOT à la source
                # (``juger_reprise``) — garde ktiv sur chaque paire, omissions intérieures signalées,
                # et plus d'excuse globale « la clé du mot est quelque part dans une édition ».
                jr = juger_reprise(list(range(k1, k2)), pg, src, propre, autres, sig_ed, sig_me)
                ecarts = jr["lignes"]
                # par construction, aucune édition n'écrit à cet endroit la forme de la page (sinon le mot
                # serait égal lettre pour lettre) : ces mots sont tous à lire (le « * » de la ligne ktiv)
                ktiv_r = "".join(f" · « {w.brut} » / « {p.brut} * »" for w, p in jr["ktiv"])
                ligne = (f"REPRISE — {len(mots)} mots du séif "
                         f"{', '.join(f'{q} ({numeral(q)})' for q in seifs)} cités une seconde fois"
                         + ((", fidèlement" if not jr["ktiv"] else
                             f", fidèlement au ktiv près — à contrôler :{ktiv_r[2:]}") if not ecarts else
                            f", avec {len(ecarts)} écart(s) à la source (lignes suivantes)"
                            + (f" ; au ktiv près, à contrôler :{ktiv_r[2:]}" if jr["ktiv"] else ""))
                         + (f" ; coupée par « … » à {jr['coupures']} endroit(s) (déclaré : chaque "
                            "morceau est cité mot pour mot)" if jr["coupures"] else ""))
                res.setdefault(cible, _nouveau())
                _ligne(res[cible], "REPRISE", ligne, nature="reprise", ecarts=bool(ecarts),
                       ktiv_reprise=list(jr["ktiv"]))
                for s_e, texte, inf in ecarts:
                    res.setdefault(s_e or cible, _nouveau())
                    _ligne(res[s_e or cible], "ALTÉRATION", texte, nature="reprise", ecarts=True, **inf)
                continue
            res.setdefault(s, _nouveau())
            _ligne(res[s], "AJOUT", f"AJOUT — {len(mots)} mots qui ne sont pas du siman : « {extrait(mots)} »",
                   nature="ajout", pk=list(range(k1, k2)))
        else:
            quoi = ("mot « הגה » ajouté (l'étiquette de la glose)"
                    if [w.lettres for w in mots] == ["הגה"] else "mot(s) ajouté(s)")
            att = _suit((), mots, s, autres, propre)
            res.setdefault(s, _nouveau())
            _ligne(res[s], "ALTÉRATION", f"ALTÉRATION (leçon) — {quoi} : « {extrait(mots)} »" + att,
                   nature="leçon", suit=bool(att), pk=list(range(k1, k2)))
    # tour 4 : un mot « omis » ici et « ajouté » là, dans le même séif, est un mot DÉPLACÉ — une
    # interversion (« ולא ירדו » → « ירדו ולא ») ; la dire omission la comptait parmi ce qu'aucune
    # autre édition ne peut excuser
    for s, d in res.items():
        omis = [q for q, i in enumerate(d["info"]) if i.get("nature") == "omission" and i.get("run")
                and len(i["run"]) <= 3 and not i.get("cache")]
        ajoutes = [q for q, i in enumerate(d["info"]) if i.get("nature") == "leçon" and i.get("pk")
                   and not i.get("src_run") and len(i["pk"]) <= 3]
        retirer = set()
        for q in omis:
            run = d["info"][q]["run"]
            for a in ajoutes:
                if a in retirer:
                    continue
                if [cle_souple(w.lettres) for w in run] == [cle_souple(pm[k].lettres) for k in d["info"][a]["pk"]]:
                    pk = d["info"][a]["pk"]
                    d["lignes"][q] = (f"ALTÉRATION (leçon) — mot(s) déplacé(s) dans le séif (interversion) : "
                                      f"« {extrait(run)} »")
                    d["info"][q] = dict(nature="leçon", interverti=True, src_run=run, pk=pk)
                    retirer.add(a)
                    break
        for a in sorted(retirer, reverse=True):
            del d["familles"][a], d["lignes"][a], d["info"][a]
    return res


def _a_plat(seq):
    return [w for s in sorted(seq) for w in seq[s]]


def _aligner_reprise(W, P, coupe):
    """Aligne un morceau de reprise ``P`` (mots de page, un seul bloc) sur l'édition ``W`` (mots, à
    plat) : le passage de ``W`` que le morceau cite, puis l'alignement mot à mot. Rend (a0, ops), ops
    relatifs à W[a0:…] et à P, ou None si le morceau ne partage aucune suite de deux mots avec ``W``.
    Un bloc apparié COURT au bord du morceau, séparé du suivant par un saut de source bien plus grand
    que le saut de page, est une rencontre fortuite (« אם לא » ailleurs dans le siman) : on l'écarte —
    sauf si la page coupe là sa citation (« … »), auquel cas le saut est déclaré."""
    A = [w.cle for w in W]
    B = [w.cle for w in P]
    blocs = [b for b in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks()
             if b.size >= min(2, len(P))]
    if not blocs:
        return None

    def egare(b, c):
        return ((c.a - b.a - b.size) - (c.b - b.b - b.size) > max(8, 2 * len(P))
                and not coupe(c.b))
    while len(blocs) > 1 and blocs[0].size < 4 and egare(blocs[0], blocs[1]):
        blocs.pop(0)
    while len(blocs) > 1 and blocs[-1].size < 4 and egare(blocs[-2], blocs[-1]):
        blocs.pop()
    a0 = max(0, blocs[0].a - blocs[0].b)
    a1 = min(len(W), blocs[-1].a + blocs[-1].size + len(P) - blocs[-1].b - blocs[-1].size)
    return a0, difflib.SequenceMatcher(None, A[a0:a1], B, autojunk=False).get_opcodes()


def _juger_morceau(W, P, coupe):
    """Un morceau de reprise confronté mot à mot à UNE édition. Rend un dict :
      ok     position de P → « eq » (mêmes lettres) ou « ktiv » (``ktiv_seul``) ;
      ktiv   position de P → le mot de l'édition qu'elle n'égale qu'au ktiv près ;
      page   position de P → (genre, mots de l'édition en face) pour un mot qui n'est PAS le mot de
             l'édition à cet endroit : « yodvav » (même clé, ni l'un ni l'autre par ajout de yod/vav —
             « שהוא » / « שהיא »), « leçon » (dans un remplacement), « ajout » (rien en face, entre
             deux mots cités), « étranger » (au bord, ou morceau introuvable) ;
      omis   [(mots de l'édition, position de P, déclaré)] — les mots de l'édition qui manquent
             À L'INTÉRIEUR du passage cité : entre deux mots cités, suppression, ou mot d'un
             remplacement sans contrepartie (``_contreparties``) ; « déclaré » si la page coupe là
             (« … », ou un autre bloc) ;
      seif   position de P → le séif du mot d'en face (ou du voisin) ;
      bornes (premier, dernier) : indices dans ``W`` du premier et du dernier mot cités, ou None."""
    r = {"ok": {}, "ktiv": {}, "page": {}, "omis": [], "seif": {}, "bornes": None}
    al = _aligner_reprise(W, P, coupe)
    if al is None:
        rien = []
        for j in range(len(P)):
            r["page"][j] = ("étranger", rien)
        return r
    a0, ops = al
    eqj = [j1 + d for tag, i1, i2, j1, j2 in ops if tag == "equal" for d in range(j2 - j1)]
    jmin, jmax = (min(eqj), max(eqj)) if eqj else (len(P), -1)
    eqi = [a0 + i1 + d for tag, i1, i2, j1, j2 in ops if tag == "equal" for d in range(i2 - i1)]
    if eqi:
        r["bornes"] = (min(eqi), max(eqi))
    for tag, i1, i2, j1, j2 in ops:
        mots_w = W[a0 + i1:a0 + i2]
        voisin = W[min(len(W) - 1, a0 + i1)] if W else None
        for j in range(j1, j2):
            r["seif"][j] = (mots_w[j - j1].seif if tag == "equal" else
                            mots_w[0].seif if mots_w else voisin.seif if voisin else 0)
        if tag == "equal":
            for d in range(i2 - i1):
                w, p = mots_w[d], P[j1 + d]
                if w.lettres == p.lettres:
                    r["ok"][j1 + d] = "eq"
                elif ktiv_seul(w.lettres, p.lettres):
                    r["ok"][j1 + d] = "ktiv"
                    r["ktiv"][j1 + d] = w
                else:
                    r["page"][j1 + d] = ("yodvav", [w])
            continue
        # à l'intérieur du passage cité : des mots cités de part et d'autre
        dedans = jmin < j1 and j2 <= jmax if tag == "replace" else jmin < j1 <= jmax
        if tag == "replace" and coupe_autrement(mots_w, P[j1:j2]):
            # le même texte, coupé autrement en mots (TE « ה " א » / la page « ה"א », 5:1) : la
            # garde ktiv de ``coupe_autrement`` (des yod/vav ajoutés d'un seul côté) y a déjà jugé
            eq = coupe_autrement(mots_w, P[j1:j2]) == "eq"
            for j in range(j1, j2):
                r["ok"][j] = "eq"
            if not eq:
                # au ktiv près : listé une fois, le passage de l'édition en entier
                r["ok"][j1] = "ktiv"
                r["ktiv"][j1] = Mot(" ".join(w.brut for w in mots_w))
            continue
        if tag == "replace":
            sans, _p, _t = _contreparties(mots_w, P[j1:j2])
            for j in range(j1, j2):
                r["page"][j] = ("leçon" if dedans else "étranger", mots_w)
            if sans and dedans:
                r["omis"].append((sans, j1, any(coupe(j) for j in range(j1, j2 + 1))))
        elif tag == "delete":
            if dedans:
                r["omis"].append((mots_w, j1, coupe(j1)))
        elif tag == "insert":
            rien = []
            for j in range(j1, j2):
                r["page"][j] = ("ajout" if jmin < j1 and j2 <= jmax else "étranger", rien)
    return r


def juger_reprise(ks, pg, src, propre, autres, sig_ed, sig_me):
    """TOUR 5 — LA REPRISE CONFRONTÉE MOT À MOT (l'arbitre du tour 4).

    Une REPRISE (un passage déjà donné, cité une seconde fois pour l'analyser) était confrontée à
    la source par les seules CLÉS, et tout mot dont la clé figurait N'IMPORTE OÙ dans une édition
    était excusé. Deux défauts, deux témoins sur les données réelles de Sefaria, certifiés
    ÉQUIVALENT, code 0, « cités une seconde fois, fidèlement (au ktiv près) » :
      · la garde ktiv n'y passait pas — au siman 5, « שֶׁהוּא תַּקִּיף » → « שֶׁהִיא » dans la reprise
        (témoin Y2) ; c'est le défaut du témoin N4b, sur un chemin que le tour 4 n'avait pas couvert ;
      · une reprise qui OMET des mots de la source n'était jamais signalée — on ne comptait que les
        mots de la page sans correspondant : au siman 22, « וְאִם לֹא בֵּרַךְ » → « וְאִם בֵּרַךְ » dans la
        reprise de la glose du Rama (témoin Y1), le din inversé.
    Désormais chaque BLOC de la reprise (une citation) est aligné mot à mot, dans chaque édition de
    référence, sur le passage qu'il cite (``_juger_morceau``) :
      · chaque paire appariée passe la garde ktiv ; un ÉCHANGE yod/vav est un mot changé ;
      · un mot de la page est conforme s'il est le mot d'UNE édition de référence À CET ENDROIT du
        passage (R3, versant leçon : la leçon de l'autre édition au même endroit) — jamais parce que
        sa clé se trouve ailleurs ;
      · une OMISSION se juge contre l'édition par défaut seule (R3) : un mot de ME qui manque entre
        deux mots cités est un écart, que TE l'ait ou non (« absent aussi de Torat Emet 363 ») —
        SAUF si la page coupe là sa citation (« … », la convention du dépôt : « A… B » veut dire A et
        B chacun mot pour mot), ce qui est dit sur la ligne REPRISE, sans faire diverger le siman ;
      · les bords sont libres : une reprise cite le passage qu'elle veut.
    Rend {"lignes": [(séif, texte, info)], "ktiv": [(mot source, mot page)], "coupures": n}."""
    pm = pg["mots"]
    eds = [(sig_ed[src[0].ed] if src else "?", _a_plat(propre) if propre is not None else
            [w for w in src])] + [(sg, _a_plat(seq)) for sg, seq in autres]
    me = next((e for e in eds if e[0] == sig_me), eds[0])
    autres_sig = [sg for sg, _ in eds if sg != me[0]]
    out = {"lignes": [], "ktiv": [], "coupures": 0}
    morceaux = []
    for k in ks:
        if morceaux and pm[morceaux[-1][-1]].bloc == pm[k].bloc:
            morceaux[-1].append(k)
        else:
            morceaux.append([k])
    bornes_prec = None
    for kp in morceaux:
        P = [pm[k] for k in kp]

        def coupe(j, kp=kp):
            return 0 < j < len(kp) and ellipse_a(pg, kp[j])
        par_ed = {sg: _juger_morceau(W, P, coupe) for sg, W in eds}
        rm = par_ed[me[0]]
        # les mots de la page : conformes si une édition de référence les porte à cet endroit
        ecart = []
        for j in range(len(P)):
            etats = [r["ok"].get(j) for r in par_ed.values()]
            if "eq" in etats:
                continue
            if "ktiv" in etats:
                w = next(r["ktiv"][j] for r in par_ed.values() if r["ok"].get(j) == "ktiv")
                out["ktiv"].append((w, P[j]))
                continue
            ecart.append(j)
        # groupés : des positions consécutives de même genre, vues par ME
        g = 0
        while g < len(ecart):
            j = ecart[g]
            genre, en_face = rm["page"].get(j, ("étranger", []))
            h = g + 1
            while (h < len(ecart) and ecart[h] == ecart[h - 1] + 1
                   and rm["page"].get(ecart[h], ("étranger", []))[0] == genre
                   and rm["page"].get(ecart[h], ("", []))[1] is en_face):
                h += 1
            mots_p = [P[ecart[q]] for q in range(g, h)]
            s_e = rm["seif"].get(j, 0)
            if genre == "yodvav":
                quoi = "yod/vav ÉCHANGÉ, un autre mot (pas du ktiv haser/malé)"
                if _par_ajout(en_face[0].lettres, mots_p[0].lettres):
                    quoi = "mot de deux lettres, une mater ajoutée ou ôtée en fait un autre mot (pas du ktiv)"
                t = f"« {en_face[0].brut} » → « {mots_p[0].brut} »"
            elif genre == "leçon":
                quoi = "mots changés"
                t = f"« {extrait(en_face)} » → « {extrait(mots_p)} »"
            elif genre == "ajout":
                quoi = "mot(s) ajouté(s) entre deux mots cités"
                t = f"« {extrait(mots_p)} »"
            else:
                quoi = "mot(s) qui ne sont pas la source à cet endroit"
                t = f"« {extrait(mots_p)} »"
            out["lignes"].append((s_e, f"ALTÉRATION (reprise) — dans la reprise du séif {s_e} ({numeral(s_e)}), "
                                       f"{quoi} : {t} — ni {me[0]} ni "
                                       f"{', '.join(autres_sig) or 'une autre édition'} ne l'écrit ainsi à cet endroit",
                                  dict(reprise=genre, yodvav=genre == "yodvav")))
            g = h
        # ENTRE DEUX BLOCS de la reprise : le bloc suivant reprend la source plus loin que là où le
        # précédent s'est arrêté — les mots sautés sont une omission, sauf « … » à la jointure. Une
        # reprise découpée en blocs (« composantes ») ne peut pas sauter, sans le dire, ce qu'un seul
        # bloc ne pourrait pas sauter (le « לא » de 22:1 posé entre deux blocs). Des blocs dans un
        # AUTRE ordre que la source ne sautent rien : ils ne sont pas jugés ici.
        omis = list(rm["omis"])
        if bornes_prec and rm["bornes"] and rm["bornes"][0] > bornes_prec[1] + 1:
            saut = me[1][bornes_prec[1] + 1:rm["bornes"][0]]
            # « … » en fin du bloc précédent ou en tête de celui-ci (``ellipse_a`` lit les deux)
            omis.append((saut, 0, ellipse_a(pg, kp[0])))
        bornes_prec = rm["bornes"] or bornes_prec
        # les omissions : contre l'édition par défaut seule (R3)
        for mots_w, j, declare in omis:
            if declare:
                out["coupures"] += 1
                continue
            aussi = [sg for sg in autres_sig if all(sg in w.absent_de for w in mots_w)]
            rama = " de la glose du Rama" if any(w.rama for w in mots_w) else ""
            par = " (entre parenthèses)" if all(w.ref for w in mots_w) else ""
            avant = P[j - 1].brut if j > 0 else (pm[kp[0] - 1].brut + " (bloc précédent)" if kp[0] > 0 else "")
            apres = P[j].brut if j < len(P) else ""
            s_e = mots_w[0].seif
            out["lignes"].append((s_e, f"ALTÉRATION (reprise) — dans la reprise du séif {s_e} ({numeral(s_e)}), "
                                       f"{len(mots_w)} mot(s){rama}{par} de la source OMIS entre « {avant} » et "
                                       f"« {apres} », NON déclaré(s) par « … » : « {extrait(mots_w)} »"
                                       + (f" — absent aussi de {', '.join(aussi)}" if aussi else ""),
                                  dict(reprise="omission", sure=True, run=list(mots_w), sig=me[0])))
    return out


def _contient(seq, sub):
    n = len(sub)
    return n > 0 and any(seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def _suit(run, page_rep, s, autres, propre=None):
    """La forme que la page donne à la place est-elle celle d'une AUTRE édition, au
    même séif ? Sur 529 lignes « abréviation / une lettre / mots changés » du premier
    balayage à deux éditions, 182 l'étaient : « אע״פ » → « אף על פי » (10:12, la page
    suit TE dans un séif où elle suit ME), « גויה » → « עכו״ם » (21:3, l'inverse). La
    page mêle alors les éditions à l'intérieur d'un séif : l'écart reste un écart à
    l'édition retenue — aucune ne donne ce séif tel quel —, mais aucun mot n'y est
    inventé. On le dit, pour le tri."""
    rep = [w.cle for w in page_rep]
    src = [w.cle for w in run]
    if sum(len(w.lettres) for w in page_rep) < 3:     # « כך », « כן » : partout, ne prouvent rien
        return ""
    # tour 4 : ``seq`` donne les MOTS de chaque séif. Un yod/vav échangé (« הוא » → « היא »)
    # a la même clé des deux côtés : on compare alors les lettres
    lettres = src == rep
    if lettres:
        rep, src = [w.lettres for w in page_rep], [w.lettres for w in run]

    def suite(seq):
        return [w.lettres if lettres else w.cle for w in seq.get(s, [])]
    # un mot AJOUTÉ (run vide) n'est « de l'autre édition » que si l'édition retenue
    # ne l'a nulle part dans ce séif : « הקלף » (32:8) est aux deux
    if not src and propre is not None and _contient(suite(propre), rep):
        return ""
    eds = [e for e, seq in autres if _contient(suite(seq), rep)
           and not (src and _contient(suite(seq), src))]
    return f" — la page suit ici {', '.join(eds)}" if eds else ""


def _ailleurs(run, sig_ed):
    """Un passage omis qu'UNE édition met entre parenthèses et l'autre non est
    compté en TRONCATURE (voir ``marquer_ailleurs``). On dit au lecteur où sont les
    parenthèses : ce peut être un simple renvoi (« ועיין לקמן סימן רל״ג », 92:4), ou
    une glose du Rama que ME imprime entre parenthèses (« הגה ואין חילוק בין שניהם
    חדשים … », 175:2, cinquante-cinq mots) — à juger, pas à taire."""
    if not run:
        return ""
    compte, vus = {}, {}
    for w in run:
        propre = sig_ed[w.ed]
        vus[propre] = vus.get(propre, 0) + 1
        if w.paren:
            compte[propre] = compte.get(propre, 0) + 1
        for e, r in w.ailleurs.items():
            vus[e] = vus.get(e, 0) + 1
            if r:
                compte[e] = compte.get(e, 0) + 1
    tout = [e for e in sig_ed if compte.get(e, 0) == len(run)]
    part = [e for e in sig_ed if e not in tout and 2 * compte.get(e, 0) >= len(run)]
    if not tout and not part:
        return ""
    # « hors parenthèses » ne se dit que d'une édition où le passage a un
    # correspondant pour la moitié de ses mots au moins
    hors = [e for e in sig_ed if e not in tout and e not in part and 2 * vus.get(e, 0) >= len(run)]
    morceaux = ([f"entre parenthèses dans {', '.join(tout)}"] if tout else []) \
        + ([f"en partie entre parenthèses dans {', '.join(part)}"] if part else []) \
        + ([f"hors parenthèses dans {', '.join(hors)}"] if hors else [])
    return " — " + ", ".join(morceaux)


_VA = []


def _va():
    """``numeros()`` de verifier-alignement.py lit les séifim qu'un titre ANNONCE."""
    if not _VA:
        p = os.path.join(ROOT, "scripts", "verifier-alignement.py")
        try:
            spec = importlib.util.spec_from_file_location("va", p)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            _VA.append(m)
        except Exception as e:
            print(f"  ⚠️  titres des blocs NON lus ({p} : {type(e).__name__}) — "
                  "le sous-cas « annoncé et absent » ne sera pas distingué")
            _VA.append(None)
    return _VA[0]


# -------------------------------------------------------------------- éditions

_ALIGN = {}


def aligner_memo(cle_src, src, pg, nseifs):
    """L'alignement ne dépend que de la source, des mots de la page et de leurs
    blocs : trois pages aux mêmes mots le partagent. L'ANALYSE, elle, lit ce qui est
    propre à chaque page (déclaration de sélection, titres des blocs, « … ») et
    n'est jamais partagée — la mémoriser par mots donnait à la page hébraïque le
    verdict de la française (voir la docstring).

    Rend l'alignement. Il rendait aussi, aux tours 3 à 6, le nombre de mots de tête
    « absorbés » comme chapeau par ressemblance ; depuis le tour 7, le chapeau n'est reconnu
    que par ``retirer_chapeau`` (lecture stricte, ``_chapeau_lu``), avant l'alignement."""
    # tour 4 : la clé de mémoïsation porte les LETTRES des mots, non leur seule clé — la
    # garde ktiv (``ktiv_seul``) les lit, et deux pages de mêmes clés (« כוס » dans l'une,
    # « כיס » dans l'autre) ne partagent plus un alignement
    k = (cle_src, tuple((w.lettres, w.bloc) for w in pg["mots"]))
    if k not in _ALIGN:
        al = aligner(src, pg, nseifs)
        st, op_de, part, rep_page, deplace, ajouts, par_seif = al
        _ALIGN[k] = al
    return _ALIGN[k]


def couts(src, al, nseifs):
    """Distance de la page à une édition, séif par séif : (mots non appariés des
    DEUX côtés — mots de l'édition absents ou remplacés, mots de la page qui les
    remplacent ou s'ajoutent après ce séif —, écarts de ktiv) ; et l'ÉTENDUE de
    chaque séif dans la page (positions des mots appariés ou qui le remplacent)."""
    st, op_de, part, rep_page, _deplace, ajouts, par_seif = al
    cout = dict.fromkeys(range(1, nseifs + 1), 0)
    ktiv = dict.fromkeys(range(1, nseifs + 1), 0)
    etendue = {s: set() for s in range(1, nseifs + 1)}
    for s, idx in par_seif.items():
        vus = set()
        for x in idx:
            if st[x] in ("eq", "ktiv"):
                etendue[s].add(part[x])
                if st[x] == "ktiv":
                    ktiv[s] += 1
                continue
            cout[s] += 1
            o = op_de[x]
            if st[x] == "rep" and o in rep_page and o not in vus:
                vus.add(o)
                cout[s] += len(rep_page[o])
                etendue[s].update(rep_page[o])
    seif_de_page = {}
    for x, k in enumerate(part):
        if k is not None and st[x] in ("eq", "ktiv"):
            seif_de_page.setdefault(k, src[x].seif)
    for k1, k2 in ajouts:
        s = next((seif_de_page[k] for k in range(k1 - 1, -1, -1) if k in seif_de_page), 1)
        cout[s] = cout.get(s, 0) + (k2 - k1)
    return cout, ktiv, etendue


def choisir(mesures, nseifs, admis=None):
    """Séif par séif, l'édition la plus proche de la page : le moins de mots non
    appariés, puis le moins d'écarts de ktiv, puis l'ordre des éditions (ME, celle
    que Sefaria sert par défaut, d'abord). ``mesures[i]`` = (coûts, ktiv, étendues,
    séifs DÉPLACÉS) de l'alignement de l'édition i sur toute la page.

    UNE GARDE. Un alignement n'est pas qu'une comparaison de mots : il décide aussi
    OÙ est chaque séif. Sur une page qui réordonne la source, deux éditions peuvent en
    décider autrement — au siman 32, TE « retrouvait » le séif טו dans le bloc qui
    donne le séif טז (les deux finissent par « כשר ואם לאו פסול »), à deux mots de
    moins que ME, qui le tenait pour absent ; l'en croire, c'était lire deux fois les
    mêmes mots de la page. Une autre édition que ME n'est donc retenue pour un séif que
    si elle le lit AU MÊME ENDROIT de la page que ME (leurs étendues se recoupent),
    ou, ME ne l'y lisant nulle part, si elle le lit à sa place (non DÉPLACÉ).

    R2 : une édition alternative n'est candidate qu'aux séifs où elle est ALIGNÉE sur
    l'édition par défaut (``admis[i]``, voir ``SEUIL_ALIGNE``).

    Rend ``choix`` (séif → indice de l'édition) et ``egal`` (séifs où toutes les
    éditions admises sont exactement aussi proches : le texte de la page n'y départage rien)."""
    choix, egal = {}, set()
    for s in range(1, nseifs + 1):
        cand = [i for i in range(len(mesures)) if i == 0 or admis is None or s in admis.get(i, ())]
        notes = sorted((mesures[i][0].get(s, 0), mesures[i][1].get(s, 0), i) for i in cand)
        e0 = mesures[0][2][s]
        for c, k, i in notes:
            ei, dep_i = mesures[i][2][s], mesures[i][3]
            if i == 0 or (e0 & ei) or (not e0 and s not in dep_i):
                choix[s] = i
                break
        if len(cand) > 1 and len({nt[:2] for nt in notes}) == 1:
            egal.add(s)
    return choix, egal


OMISSIONS = ("absent", "troncature", "renvoi", "parenthèse", "omission")
SURES = OMISSIONS + ("ordre",)   # ce qu'aucune autre édition ne peut excuser (siman PARTIEL)
R3_COURT = 2   # mots : une omission R3 « courte » (comptée à part, pour information — signalée)


def _sous_suites(run, sig):
    """Les suites de mots CONSÉCUTIFS (dans l'édition) de ``run`` qui n'ont aucun
    correspondant dans l'édition ``sig``."""
    out, cur = [], []
    for w in run:
        if sig in w.absent_de and (not cur or w is _suivant(cur[-1])):
            cur.append(w)
        else:
            if cur:
                out.append(cur)
            cur = [w] if sig in w.absent_de else []
    if cur:
        out.append(cur)
    return out


_SUIVANT = {}


def _suivant(w):
    return _SUIVANT.get(id(w))


def r3_courte(sous):
    """Une omission R3 d'un ou deux mots hors parenthèses (« מיד », « חשוב או »).

    TOUR 3 (l'arbitre du tour 2). Le tour 2 les EXCUSAIT comme « la leçon de TE » : seule
    une suite d'au moins trois mots, un passage entre parenthèses ou un renvoi était
    signalé. C'était juger l'omission à sa LONGUEUR, et R3 n'en connaît pas : « tout
    passage que porte l'édition par défaut et qui manque à la page — suite de mots, glose
    du Rama, parenthèse de source — reste signalé ». Ce qui sépare une LEÇON d'une
    OMISSION, c'est l'alignement des deux éditions, pas le nombre de mots : un mot de ME
    que TE REMPLACE (« ממנה » pour « ממנו », « בבית הכנסת » pour « בב״ה ») n'est jamais
    ``absent_de`` TE (``marquer_absences``) ; un mot que TE n'a PAS DU TOUT l'est. Les 23
    séifs que le tour 2 excusait, ouverts un à un contre les deux éditions, sont TOUS des
    suppressions dans TE, aucun un remplacement — et plusieurs portent le din : ME 211:5,
    dans la glose du Rama, « שהדבר השני חשוב או חביב עליו », TE « שהדבר השני חביב עליו » ;
    40:3 « אפילו בכלי תוך כלי », TE « אפילו כלי » ; 39:1 « מומר לע״א », TE « מומר » ; 175:3
    « יברך מיד » ; 135:8 « מברך שנית וקורא במקום לוי » ; 128:45 « אליך ויחנך ». Témoin de
    l'arbitre : des pages qui recopient TE aux simanim 211, 175, 135, 140 sortaient
    IDENTIQUE, code 0 ; et une TE sabotée, privée de la décision du Rama « והעיקר להטות »
    (131:1), recopiée par la page, de même. Elles sont désormais toutes signalées ; ces
    omissions courtes ne sont plus que COMPTÉES à part, pour l'information du relecteur."""
    return len(sous) <= R3_COURT and not all(w.paren for w in sous) and nature_par(sous) != "renvoi"


def _texte_aussi(sous, run, titre):
    if sum(len(x) for x in sous) == len(run):
        return f" — absent aussi de {titre}"
    return " — dont " + " ; ".join(f"« {extrait(x, 5)} »" for x in sous) + f" absent aussi de {titre}"


def confronter(n, srcs, cles_src, pg, nseifs, chap, sig_ed, admis=None, i_me=0, titres=()):
    """Chaque édition est alignée seule sur toute la page et analysée ; puis, séif
    par séif, on garde l'édition la plus proche (``choisir``) et le verdict que CET
    alignement-là donne du séif. On ne réaligne JAMAIS une source composée : mêler
    les éditions déplaçait des mots d'un séif à l'autre sur les pages réordonnées
    (siman 32), et le verdict d'un séif doit être celui qu'une édition réelle donne.

    R3 — UNE AUTRE ÉDITION EXPLIQUE UNE LEÇON, JAMAIS UNE OMISSION (tour 2). L'édition
    la plus proche excuse une différence de mots, de ktiv, une abréviation développée,
    un ajout. Mais elle était aussi la plus INDULGENTE pour les omissions : quand TE
    n'a pas un passage de ME et que la page ne l'a pas non plus, TE était la plus proche
    et le séif sortait conforme — 39:4, « (פי׳ מיאני) » de ME, absent de TE et des trois
    pages : 0 ligne. Désormais l'alignement sur l'édition par défaut (``i_me``) est
    TOUJOURS lu pour les omissions : un passage de ME qui manque à la page reste signalé
    même si TE l'omet aussi, avec la mention « absent aussi de Torat Emet 363 » — sur la
    ligne même quand ME est retenue pour le séif, sur une ligne [ME] ajoutée quand c'est
    TE. Toute omission, QUELLE QUE SOIT SA LONGUEUR (tour 3 : le tour 2 excusait un ou deux
    mots hors parenthèses comme « la leçon de TE » — voir ``r3_courte``) ; les omissions
    d'un ou deux mots sont seulement comptées à part (``r3_courtes``), pour information.
    Un séif ABSENT pour l'édition retenue ET pour ME est donné dans le texte de ME : rien
    de la page n'y départage les éditions, et la plus courte n'est pas la plus fidèle
    (128:9 : TE, sans le crochet de treize mots de ME, était « la plus proche » d'un
    séif que la page n'a pas).

    Rend (choix, egal, res, r3) — ``res`` à None si la page est identique, lettre pour
    lettre, aux séifs des éditions retenues et qu'aucune omission ne reste ; ``r3`` :
    {"ajoutees": [(s, ligne)], "annotees": [(s, ligne)], "courtes": [(s, mots)]}."""
    runs = [aligner_memo((n, cles_src[i]), src, pg, nseifs) for i, src in enumerate(srcs)]
    mesures = [couts(src, al, nseifs) + (al[4],) for src, al in zip(srcs, runs)]
    choix, egal = choisir(mesures, nseifs, admis)
    double_lecture(runs, choix, egal, nseifs, admis, n)
    seq = [{} for _ in srcs]
    for i, src in enumerate(srcs):
        for w in src:
            if admis is None or i == i_me or w.seif in admis.get(i, ()):
                seq[i].setdefault(w.seif, []).append(w)
    par_ed = {i: analyser(srcs[i], pg, nseifs, runs[i], sig_ed[i_me] if i_me is not None else None, sig_ed,
                          [(sig_ed[j], seq[j]) for j in range(len(srcs)) if j != i], seq[i])
              for i in range(len(srcs))}
    vide = {"familles": [], "lignes": [], "info": [], "ktiv": False}
    r3 = {"ajoutees": [], "annotees": [], "courtes": []}
    res = {}
    # pour R3, versant leçon : les mots de chaque édition que la page porte (``apparies`` :
    # position de page → mot), et l'alignement de deux éditions sur un séif (``ops_ij``)
    apparies = []
    for j, al in enumerate(runs):
        st_j, _o, part_j = al[0], al[1], al[2]
        apparies.append({part_j[x]: srcs[j][x] for x in range(len(srcs[j]))
                         if st_j[x] in ("eq", "ktiv") and part_j[x] is not None})
    _ops = {}

    def ops_ij(i, j, s):
        if (i, j, s) not in _ops:
            _ops[(i, j, s)] = difflib.SequenceMatcher(
                None, [w.cle for w in seq[i].get(s, [])], [w.cle for w in seq[j].get(s, [])],
                autojunk=False).get_opcodes()
        return _ops[(i, j, s)]
    for s in range(1, nseifs + 1):
        i = choix[s]
        if (i_me is not None and i != i_me
                and any(f.startswith("ABSENT") for f in par_ed[i].get(s, vide)["familles"])
                and any(f.startswith("ABSENT") for f in par_ed[i_me].get(s, vide)["familles"])):
            i = choix[s] = i_me
            egal.discard(s)
        d0 = par_ed[i].get(s, vide)
        d = {"familles": list(d0["familles"]), "lignes": list(d0["lignes"]),
             "info": [dict(x) for x in d0["info"]], "ktiv": d0["ktiv"]}
        # L'ORDRE n'est pas une affaire d'édition. Qu'un séif soit DÉPLACÉ se juge
        # par rapport aux séifs voisins, que chaque alignement place à sa façon : au
        # siman 32, ME voit le séif יט hors de l'ordre et TE, qui place autrement ses
        # voisins, ne le voit pas. Le séif est dit DÉPLACÉ si une édition qui le lit
        # au même endroit de la page le trouve hors de l'ordre de la source.
        if "DÉPLACÉ" not in d["familles"]:
            for j in range(len(srcs)):
                dj = par_ed[j].get(s, vide)
                q = next((x for x, l in enumerate(dj["lignes"]) if l.startswith("DÉPLACÉ")), None)
                if j != i and q is not None and mesures[j][2][s] & mesures[i][2][s]:
                    d["familles"].insert(0, "DÉPLACÉ")
                    d["lignes"].insert(0, dj["lignes"][q])
                    d["info"].insert(0, dict(dj["info"][q]))
                    break
        # R3, LES OMISSIONS SE JUGENT CONTRE ME (tour 4) : dans un séif retenu dans TE, une
        # « omission » relevée contre TE n'en est une que si la page omet aussi ce que ME porte
        # à cet endroit (``_rejuger_contre_me``).
        if i_me is not None and i != i_me:
            _rejuger_contre_me(i, i_me, s, d, srcs, seq, runs, par_ed, ops_ij, titres, sig_ed, apparies)
        # R3, LE VERSANT LEÇON (tour 4) : une leçon que porte une AUTRE édition de référence,
        # AU MÊME ENDROIT du séif, est excusée — « אע״פ » → « אף על פי » au milieu d'un séif
        # retenu dans ME, quand TE écrit « אף על פי » là. Le tour 3 la laissait en ALTÉRATION
        # avec « la page suit ici TE » : plus sévère que R3, qui excuse les leçons. Jamais une
        # omission (``OMISSIONS`` : elles ne passent pas ici).
        for q, info in enumerate(d["info"]):
            if info.get("nature") not in ("leçon", "ajout") or not info.get("pk"):
                continue
            for j in range(len(srcs)):
                if j == i or not (admis is None or j == i_me or s in admis.get(j, ())):
                    continue
                if _porte_au_meme_endroit(i, j, s, info, srcs, seq, apparies, ops_ij):
                    texte = re.sub(r"^(ALTÉRATION \(leçon\)|AJOUT) — ", "", d["lignes"][q])
                    texte = re.sub(r" — la page suit ici [^—]*$", "", texte)
                    d["familles"][q] = EXCUSEE
                    d["lignes"][q] = (f"{EXCUSEE} (R3) — {texte} — c'est la leçon de "
                                      f"{titres[j] if titres else sig_ed[j]}, au même endroit du séif")
                    info["excusee"] = sig_ed[j]
                    break
        # R3
        if i_me is not None:
            alt = [j for j in range(len(srcs)) if j != i_me and (admis is None or s in admis.get(j, ()))]
            if i == i_me:
                for q, info in enumerate(d["info"]):
                    if info.get("nature") in OMISSIONS and info.get("run"):
                        for j in alt:
                            sous = _sous_suites(info["run"], sig_ed[j])
                            r3["courtes"] += [(s, " ".join(w.brut for w in x)) for x in sous if r3_courte(x)]
                            if sous:
                                d["lignes"][q] += _texte_aussi(sous, info["run"], titres[j] if titres else sig_ed[j])
                                info.setdefault("aussi", []).append(sig_ed[j])
                                r3["annotees"].append((s, d["lignes"][q]))
            else:
                dm = par_ed[i_me].get(s, vide)
                for info in dm["info"]:
                    if info.get("nature") not in OMISSIONS or not info.get("run"):
                        continue
                    for sous in _sous_suites(info["run"], sig_ed[i]):
                        # TOUTE omission, quelle que soit sa longueur (``r3_courte``)
                        pos = info.get("pos") if info.get("nature") == "troncature" else "intérieure"
                        fam, texte, inf = classer_trou(sous, [], info.get("k"), pg, pos or "intérieure",
                                                       s, (), sig_ed)
                        texte += (f" — absent aussi de {titres[i] if titres else sig_ed[i]}"
                                  f" (l'édition la plus proche pour le reste du séif)")
                        inf.update(sig=sig_ed[i_me], aussi=[sig_ed[i]], r3=True)
                        d["familles"].append(fam)
                        d["lignes"].append(texte)
                        d["info"].append(inf)
                        r3["ajoutees"].append((s, texte))
                        if r3_courte(sous):
                            r3["courtes"].append((s, " ".join(w.brut for w in sous)))
        res[s] = d
    # tour 4 : les mots que la page n'égale à l'édition retenue qu'AU KTIV PRÈS (yod/vav
    # ajoutés d'un côté, ``ktiv_seul``) — listés sous ÉQUIVALENT, pour que le lecteur les
    # contrôle : la porte n'imprimait aucun d'eux, et c'est ainsi que « כיס » pour « כוס »
    # passait sans un mot
    pm = pg["mots"]
    ktiv = []
    for s in range(1, nseifs + 1):
        i = choix[s]
        st, op_de, part = runs[i][0], runs[i][1], runs[i][2]
        vus = set()
        for x, w in enumerate(srcs[i]):
            if w.seif != s or w.chapeau or st[x] != "ktiv" or part[x] is None:
                continue
            o = op_de[x]
            if isinstance(o, tuple) and o[0] == "recoupe":
                if o in vus:
                    continue
                vus.add(o)
                _r, i1, i2, j1, j2 = o
                ktiv.append((s, sig_ed[i], " ".join(v.brut for v in srcs[i][i1:i2]),
                             " ".join(v.brut for v in pm[j1:j2])))
            else:
                # « * » : la forme de la page n'est, à cet endroit, celle d'AUCUNE des éditions de
                # référence — c'est la page qui écrit ainsi (« ציציות » pour « ציצית », « יוצא »
                # pour « יצא » : un nombre, un temps, que le ktiv ne départage pas) : à lire d'abord
                k = part[x]
                atteste = any(apparies[j].get(k) is not None and apparies[j][k].lettres == pm[k].lettres
                              for j in range(len(srcs)) if j != i)
                ktiv.append((s, sig_ed[i], w.brut, pm[k].brut + ("" if atteste else " *")))
    src_c = composite(srcs, choix, nseifs)
    if ("".join(w.lettres for w in pg["mots"]) == "".join(w.lettres for w in src_c)
            and not any(x["lignes"] for x in res.values())):
        return choix, egal, None, r3, ktiv
    return choix, egal, res, r3, ktiv


EXCUSEE = "LEÇON EXCUSÉE"


def _region(ops, a_mots, b_mots, R):
    """Les positions de l'édition b qui répondent aux positions ``R`` de l'édition a, dans
    l'alignement ``ops`` (a, b) d'un séif : la contrepartie exacte dans un passage égal ; dans un
    remplacement, la contrepartie MOT À MOT (``_contreparties`` — « ויש אומרים » / « וי״א »,
    « ואם » / « שאם », « פרק רביעי » / « פ״ד ») ; rien pour un mot que b n'a pas. Les mots que b
    seule porte n'y sont jamais : ils ne répondent à rien de a."""
    region = set()
    for tag, i1, i2, j1, j2 in ops:
        dedans = {r for r in R if i1 <= r < i2}
        if not dedans:
            continue
        if tag == "equal":
            region.update(j1 + r - i1 for r in dedans)
        elif tag == "replace":
            _sans, _p, toutes = _contreparties(a_mots[i1:i2], b_mots[j1:j2])
            region.update(j1 + bb for aa, bb in toutes if i1 + aa in dedans)
    return region


def _rejuger_contre_me(i, i_me, s, d, srcs, seq, runs, par_ed, ops_ij, titres, sig_ed, apparies):
    """R3 (tour 4) : UNE OMISSION SE JUGE CONTRE L'ÉDITION PAR DÉFAUT. Dans un séif retenu dans
    TE, l'analyse de TE relève des omissions — des mots de TE que la page n'a pas. Ce n'en est
    une que si ME porte ces mots et que la page ne les a pas davantage sous la forme de ME.
    La contrepartie dans ME des mots omis se lit dans l'alignement des deux éditions sur le
    séif, mot à mot (``_contreparties`` dans un remplacement : « ויש אומרים » / « וי״א », « ואם »
    / « שאם », « פ״ד » / « פרק רביעי »). Puis, dans l'alignement de la page sur ME :
      · contrepartie VIDE (TE seule porte ces mots — « ביום זה », 128:3) ou entièrement
        portée par la page (« שאם » de ME, 34:2) : la page se lit ici comme ME — LEÇON EXCUSÉE ;
      · la page omet aussi la contrepartie de ME — un mot que l'analyse de ME dit omis, ou que
        l'alignement sur ME ne « remplace » que par des mots de la page que TE lit ailleurs
        (101:2 : « (טור) » de ME face au début du séif suivant) : l'omission reste, telle quelle ;
      · sinon, ME porte une contrepartie que la page rend autrement : une LEÇON, non une omission
        (33:2, TE « סברות כן נראה לי », ME « סברות כנ״ל », la page « הסברות כנזכר לעיל » : deux
        développements de la même abréviation de ME).
    Né de la garde de l'omission cachée (``_contreparties``) : un remplacement que l'analyse de
    TE disait leçon et qui devient omission ne doit pas l'être quand la page suit ME. Le tour 3
    ne le faisait pas non plus pour les simples suppressions : une page qui suivait ME, dans
    un séif retenu dans TE, sans un mot que TE seule porte, sortait ALTÉRATION."""
    st_me, op_me, rep_me = runs[i_me][0], runs[i_me][1], runs[i_me][3]
    x_me = {id(w): x for x, w in enumerate(srcs[i_me])}
    omis_me = {id(w) for info in par_ed[i_me].get(s, {}).get("info", [])
               if info.get("nature") in OMISSIONS for w in info.get("run") or []}
    te, me = seq[i].get(s, []), seq[i_me].get(s, [])
    pos_i = {id(w): q for q, w in enumerate(te)}
    for q, info in enumerate(d["info"]):
        if info.get("nature") not in OMISSIONS or info.get("nature") == "absent" or not info.get("run"):
            continue
        if info.get("sig") or info.get("r3"):
            continue                       # une ligne [ME] : déjà jugée contre ME
        run = info["run"]
        if any(id(w) not in pos_i for w in run):
            continue
        region = _region(ops_ij(i, i_me, s), te, me, {pos_i[id(w)] for w in run})
        mots = [me[r] for r in sorted(region)]

        def omis(w):
            x = x_me[id(w)]
            if id(w) in omis_me or st_me[x] == "del":
                return True
            # « remplacé » par des mots de la page que TE lit ailleurs : un artefact
            # d'alignement, le mot de ME n'est pas sur la page
            return st_me[x] == "rep" and any(k in apparies[i] for k in rep_me.get(op_me[x], []))
        if any(omis(w) for w in mots):
            continue
        lab, _, reste = d["lignes"][q].partition(" — ")
        if all(st_me[x_me[id(w)]] in ("eq", "ktiv") for w in mots):
            quoi = ("ME n'a pas ces mots" if not mots else
                    f"la page porte ici ME « {extrait(mots, 5)} »")
            d["familles"][q] = EXCUSEE
            d["lignes"][q] = (f"{EXCUSEE} (R3) — {lab} contre TE, {reste} — n'est pas une omission : "
                              f"{quoi}, {titres[i_me] if titres else sig_ed[i_me]}, l'édition par défaut")
            info["excusee"] = sig_ed[i_me]
        else:
            d["familles"][q] = "ALTÉRATION"
            d["lignes"][q] = (f"ALTÉRATION (leçon) — {lab} contre TE, {reste} — une LEÇON, non une "
                              f"omission : ME porte ici « {extrait(mots, 5)} », que la page rend autrement")
            info["nature"] = "leçon"
            info["rejugee"] = True


def _porte_au_meme_endroit(i, j, s, info, srcs, seq, apparies, ops_ij):
    """R3, versant leçon (tour 4) : la leçon d'une ligne de l'édition ``i`` — les mots de page
    ``info["pk"]``, à la place des mots ``info["src_run"]`` de ``i`` (aucun pour un ajout) — est-
    elle celle de l'édition ``j`` AU MÊME ENDROIT du séif ``s`` ?

    Trois conditions. (1) Chaque mot de page de la leçon est apparié, dans l'alignement de la
    page sur ``j``, à un mot du séif ``s`` de ``j``. (2) Ces mots de ``j`` sont la contrepartie
    des mots de ``i`` remplacés — la région de ``j`` qui leur répond dans l'alignement de ``i`` et
    de ``j`` sur le séif —, ou, pour un ajout, des mots que ``j`` porte et que ``i`` n'a pas. (3) Tous
    les mots de cette région de ``j`` sont portés par la page : si ``j`` a là un mot de plus que
    la page n'a pas, la page ne suit pas ``j``, elle omet (« A B' B C » dans ``j``, « A B C » dans
    ``i``, « A B' C » dans la page : B manque, et rien n'est excusé).

    Le tour 3 disait « la page suit ici TE » quand la forme de la page se trouvait N'IMPORTE OÙ
    dans le séif de TE (``_suit``) : assez pour le tri, pas pour excuser."""
    pk = info.get("pk") or []
    if not pk or s not in seq[j]:
        return False
    mj = apparies[j]
    if any(k not in mj or mj[k].seif != s for k in pk):
        return False
    a_mots, b_mots = seq[i].get(s, []), seq[j][s]
    pos_j = {id(w): q for q, w in enumerate(b_mots)}
    if any(id(mj[k]) not in pos_j for k in pk):
        return False
    jq = {pos_j[id(mj[k])] for k in pk}
    ops = ops_ij(i, j, s)
    run = info.get("src_run") or []
    # les mots de j qui ne répondent à RIEN de i (j seule les porte : « הגה » de ME au 82:2)
    seuls_j = set(range(len(b_mots))) - _region(ops, a_mots, b_mots, set(range(len(a_mots))))
    if not run:
        # un ajout : des mots que j seule porte — ou dont la contrepartie dans i n'est pas sur
        # la page (« שאם » de ME, 34:2, pour « ואם » de TE, que la page n'a pas)
        if jq <= seuls_j:
            return True
        en_face = _region(ops_ij(j, i, s), b_mots, a_mots, jq - seuls_j)
        portes_i = {id(w) for w in apparies[i].values()}
        return bool(en_face) and not any(id(a_mots[q]) in portes_i for q in en_face)
    pos_i = {id(w): q for q, w in enumerate(a_mots)}
    if any(id(w) not in pos_i for w in run):
        return False
    region = _region(ops, a_mots, b_mots, {pos_i[id(w)] for w in run})
    if not region or not jq <= region | seuls_j:
        return False
    portes = {id(w) for w in mj.values()}
    return all(id(b_mots[q]) in portes for q in region)


DOUBLES = []    # (siman, séif, édition écartée, édition retenue, séif qui tient les mots)


def double_lecture(runs, choix, egal, nseifs, admis, n=0):
    """GARDE 5 (tour 3) : deux séifs, lus dans deux éditions différentes, ne lisent
    jamais les MÊMES mots de la page. Chaque alignement est monotone — il n'emploie pas
    deux fois un mot de page —, mais le choix séif par séif mêle deux alignements. Témoin
    de l'arbitre du tour 2 (39:5 remplacé par 38:5, page en TE) : TE lisait le séif ו
    entier dans son bloc ; ME, qui l'alignait autrement, lisait dans ce même bloc les deux
    premiers mots du séif ו, « נמצאו ביד », comme le séif ה « réduit à 2 mots, réécrit
    autour » — et le séif ה, remplacé par un texte étranger, n'était pas dit ABSENT.
    Le mot disputé reste à la lecture où il appartient à la plus longue SUITE de mots
    appariés, consécutifs dans la source et dans la page ; l'autre séif est relu dans
    l'édition qui l'a emporté. À égalité, rien ne bouge. (Le taux de mots appariés ne
    départage pas : au siman 32, ME prête au séif ז deux mots égarés de la page,
    « שיהא הקלף », que TE lit à bon droit comme les restes du séif ח.) Mesuré sur les
    241 simanim : un seul cas, 160:9, où TE prenait au séif י le mot « ידים » — le séif ט
    y était « TRONCATURE intérieure … remplacés par « נוטלים » », il est relu dans ME,
    « TRONCATURE fin — 25 mots », ce que la page fait en effet."""
    infos = []
    for al in runs:
        st, _op, part, _rp, _dep, _aj, par_seif = al
        pos, suite = {}, {}
        for s in range(1, nseifs + 1):
            idx = [x for x in par_seif.get(s, []) if st[x] in ("eq", "ktiv") and part[x] is not None]
            pos[s] = {part[x] for x in idx}
            # longueur de la suite (source ET page consécutives) qui porte chaque mot de page
            groupe = []
            for x in idx:
                if groupe and x == groupe[-1] + 1 and part[x] == part[groupe[-1]] + 1:
                    groupe.append(x)
                else:
                    for y in groupe:
                        suite[(s, part[y])] = len(groupe)
                    groupe = [x]
            for y in groupe:
                suite[(s, part[y])] = len(groupe)
        infos.append((pos, suite))
    for _ in range(nseifs):
        change = False
        for s in range(1, nseifs + 1):
            i = choix[s]
            for s2 in range(1, nseifs + 1):
                j = choix[s2]
                if s2 == s or j == i:
                    continue
                commun = infos[i][0][s] & infos[j][0][s2]
                if not commun:
                    continue
                ri = max(infos[i][1][(s, k)] for k in commun)
                rj = max(infos[j][1][(s2, k)] for k in commun)
                if ri < rj and (admis is None or j == 0 or s in admis.get(j, ())):
                    DOUBLES.append((n, s, i, j, s2))
                    choix[s] = j
                    egal.discard(s)
                    change = True
                    break
        if not change:
            break


def ressemblance(a, b):
    """R2 : ratio difflib des squelettes consonantiques (sans yod ni vav) de deux séifs."""
    ca = "".join(squelette(w.lettres) for w in a)
    cb = "".join(squelette(w.lettres) for w in b)
    if not ca and not cb:
        return 1.0
    return difflib.SequenceMatcher(None, ca, cb, autojunk=False).ratio()


def _initiales(w, seq):
    """L'abréviation ``w`` (« וס״ס ») est-elle écrite en toutes lettres dans ``seq``
    (« וסוף סימן ») : ses lettres, vav de conjonction ôté, sont les initiales de mots
    consécutifs ? ``seq`` est le séif ENTIER de l'autre édition : le développement peut
    avoir été apparié ailleurs (190:1, « סימן » de TE apparié au « סימן » qui précède)."""
    if not w.abrev:
        return False
    L = w.lettres[1:] if w.lettres.startswith("ו") and len(w.lettres) > 2 else w.lettres
    if len(L) < 2:
        return False
    ini = [(x.lettres[1:] if x.lettres.startswith("ו") and len(x.lettres) > 2 else x.lettres)[:1] for x in seq]
    return any("".join(ini[y:y + len(L)]) == L for y in range(len(ini) - len(L) + 1))


def _proche(w, x):
    a, b = cle_souple(w.lettres), cle_souple(x.lettres)
    return a == b or (len(a) >= 3 and len(b) >= 3 and (a in b or b in a))


PREFIXES = "בהולכמש"


def _gershayim(w):
    """Le mot porte-t-il des GERSHAYIM à l'intérieur (« וי״א », « בה״כ ») — une abréviation de
    plusieurs mots — et non un geresh final (« אפי׳ », un mot tronqué) ?"""
    return any(q in w.brut[:-1] for q in '"״')


def _tronque(w):
    """Un mot TRONQUÉ de l'imprimé : un geresh final (« אפי׳ », « סי׳ », « וכו׳ »), sans gershayim à
    l'intérieur. Il abrège UN mot (tour 5), jamais une suite."""
    return w.abrev and w.brut[-1] in QUOTES and not _gershayim(w)


def _prefixe_deplace(c, libres):
    """La particule a changé de mot : ME « אפילו בכלי תוך כלי », TE « אפלו כלי בתוך כלי »
    (40:3) — « בכלי » et « תוך » de ME ont pour correspondants « כלי » et « בתוך » de TE, à
    une lettre-préfixe près. Le tour 3, en signalant toute omission R3 quelle que soit sa
    longueur, en faisait une omission « absente aussi de TE » sur une page qui recopie TE
    lettre pour lettre (le seul faux positif des 23 séifs ouverts un à un). Deux lettres au
    moins après le préfixe ôté, et parmi les seuls mots non appariés de l'autre édition,
    dans le même séif."""
    if len(c) >= 3 and c[0] in PREFIXES and c[1:] in libres:
        return True
    return any(len(x) >= 3 and x[0] in PREFIXES and x[1:] == c for x in libres if len(c) >= 2)


ABREV_MAX = 6    # mots qu'une abréviation peut couvrir (« עכו״ם » : trois)
# un nombre écrit en toutes lettres, qu'une abréviation rend par sa lettre-nombre : « פרק רביעי »
# (ME 183:9) / « פ״ד » (TE)
NOMBRES_MOTS = {"ראשון": 1, "ראשונה": 1, "שני": 2, "שנייה": 2, "שניה": 2, "שלישי": 3, "שלישית": 3,
                "רביעי": 4, "רביעית": 4, "חמישי": 5, "חמישית": 5, "ששי": 6, "שישי": 6, "שביעי": 7,
                "שמיני": 8, "תשיעי": 9, "עשירי": 10}


def _valeur_mots(mots):
    """La valeur d'un nombre écrit en un ou deux mots (« רביעי », « שמונה עשרה »), ou None."""
    if len(mots) == 1:
        return NOMBRES_MOTS.get(mots[0]) or NOMBRES.get(mots[0])
    if len(mots) == 2 and mots[1] in ("עשר", "עשרה") and NOMBRES.get(mots[0]):
        return 10 + NOMBRES[mots[0]]
    return None


def _abrege(abr, mots, gershayim=False, tronque=False):
    """Les lettres ``abr`` d'un mot ABRÉGÉ se découpent-elles en préfixes non vides des mots
    consécutifs ``mots``, un par mot et dans l'ordre ? « בה״כ » / « בית הכנסת » (ב + הכ),
    « וי״א » / « ויש אומרים », « עכו״ם » / « עובדי כוכבים ומזלות », « פ״ד » / « פרק ד׳ »,
    « סי׳ » / « סימן ». Chaque préfixe garde l'initiale du mot ; au-delà, squelettes comparés
    (« אפי׳ » / « אפלו », TE écrivant haser). Une abréviation à GERSHAYIM (« וי״א ») abrège
    plusieurs mots : lue sur un seul, le squelette lui faisait abréger « ואם » (« ו » + « יא » ≈
    « אם », 34:2).

    TOUR 5 (l'arbitre du tour 4) — UN MOT TRONQUÉ N'ABRÈGE QU'UN MOT (``tronque``). Les lettres de
    l'abréviation sont lues sur des squelettes privés de yod et de vav : le yod de « אפי׳ » servait
    d'initiale au mot suivant, et « אפי׳ » « couvrait » « אפילו יש ». Comme ``_contreparties`` préfère la
    couverture la plus large, le mot « יש » trouvait une contrepartie qui n'en est pas une : une page
    qui écrit « אפי׳ בפניו » pour « אפילו יש בפניו » (128:31) sortait « abréviation développée ou
    changée », l'omission de « יש » tue ; et si l'autre édition portait la même abréviation, le séif
    sortait CONFORME (témoins Z7a, Z7b). Un geresh final marque un mot tronqué, et un seul ; les
    gershayim (« וי״א ») abrègent une suite. Seul un nombre fait exception (« שמונה עשרה »)."""
    L = abr.translate(FINALES)
    W = [w.translate(FINALES) for w in mots]
    if not L or not W or len(W) > ABREV_MAX or not all(W):
        return False
    # un nombre : « י״ח » / « שמונה עשרה » (110:2)
    if est_numeral(L) and _valeur_mots(mots) == sum(VAL[c] for c in L):
        return True
    if gershayim and len(W) < 2:
        return False
    if tronque and len(W) > 1:
        return False
    memo = {}

    def f(i, j):
        if j == len(W):
            return i == len(L)
        if (i, j) not in memo:
            w, r = W[j], False
            v = NOMBRES_MOTS.get(mots[j]) or NOMBRES.get(mots[j])
            if v and L[i:].startswith(numeral(v)) and f(i + len(numeral(v)), j + 1):
                r = True
            elif i < len(L) and L[i] == w[0]:
                for t in range(i + 1, len(L) + 1):
                    if squelette(w[1:]).startswith(squelette(L[i + 1:t])) and f(t, j + 1):
                        r = True
                        break
            memo[(i, j)] = r
        return memo[(i, j)]
    return f(0, 0)


def _contreparties(run, rep):
    """TOUR 4 — ce qu'il y a, en face, de chaque mot de ``run`` (une édition) dans ``rep`` (ce
    qui est à sa place : la page, ou l'autre édition). Rend (``sans``, ``paires``) : les mots de
    ``run`` qui n'ont AUCUNE contrepartie, et les paires (i, j) établies par la ressemblance.

    Un mot a une contrepartie s'il est le même à la souplesse près (``_proche`` : « כו׳ » /
    « וכו׳ », « ממנו » / « ממנה »), si c'est une abréviation que ``rep`` développe ou s'il est
    pris dans le développement d'une abréviation de ``rep`` (``_abrege``), si sa particule a
    passé au mot voisin (``_prefixe_deplace``) — et, pour le reste, s'il reste en face un mot
    LIBRE pour le remplacer (un mot changé pour un autre est une leçon). Ce qui reste quand les
    mots libres d'en face sont épuisés est une OMISSION : « ואלהי אבותינו כו׳ » (ME 128:10) /
    « ואלהי וכו׳ » (TE) — « כו׳ » a « וכו׳ », « אבותינו » n'a rien. Le mot laissé sans
    contrepartie est, parmi les candidats, le moins semblable aux mots libres d'en face."""
    cv, pr, paires, toutes = [False] * len(run), [False] * len(rep), [], []
    # le même texte, coupé autrement : « של אחר » / « שלאחר » (104:2), « של אחריהם » / « שלאחריהם »
    def colle(a_seq, b_seq, cv_a, cv_b, inverse):
        for b, x in enumerate(b_seq):
            for a1 in range(len(a_seq)):
                for a2 in range(a1 + 2, min(len(a_seq), a1 + 3) + 1):
                    if any(cv_a[a] for a in range(a1, a2)):
                        continue
                    if (squelette("".join(w.lettres for w in a_seq[a1:a2]).translate(FINALES))
                            == squelette(x.lettres.translate(FINALES))):
                        for a in range(a1, a2):
                            cv_a[a] = True
                            toutes.append((b, a) if inverse else (a, b))
                        cv_b[b] = True
                        break
    colle(run, rep, cv, pr, False)
    colle(rep, run, pr, cv, True)
    for a, w in enumerate(run):
        if cv[a]:
            continue
        for b, x in enumerate(rep):
            if not pr[b] and _proche(w, x):
                cv[a] = pr[b] = True
                paires.append((a, b))
                break
    # abréviations : pour chacune, la couverture la PLUS LARGE, puis la plus proche de sa place
    # (« ב״י » couvre « בית יוסף », et non « בית » seul, le yod lu au squelette s'y perdant)
    def couverture(x, seq, pos, libres_seq):
        best = None
        for c1 in range(len(seq)):
            for c2 in range(min(len(seq), c1 + ABREV_MAX), c1, -1):
                if not all(libres_seq[c] for c in range(c1, c2)):
                    continue
                if _abrege(x.lettres, [y.lettres for y in seq[c1:c2]], _gershayim(x), _tronque(x)):
                    k = (c2 - c1, -abs(c1 - pos))
                    if best is None or k > best[0]:
                        best = (k, c1, c2)
                    break
        return best and best[1:]
    for a, w in enumerate(run):
        if cv[a] or not w.abrev:
            continue
        c = couverture(w, rep, a, [True] * len(rep))
        if c:
            cv[a] = True
            for b in range(*c):
                pr[b] = True
                toutes.append((a, b))
            paires.append((a, c[0]))
    for b, x in enumerate(rep):
        if not x.abrev:
            continue
        c = couverture(x, run, b, [True] * len(run))
        if c:
            for a in range(*c):
                cv[a] = True
                toutes.append((a, b))
            pr[b] = True
            paires.append((c[0], b))
    for a, w in enumerate(run):
        if cv[a]:
            continue
        c = cle_souple(w.lettres)
        b = next((b for b, x in enumerate(rep) if _prefixe_deplace(c, {cle_souple(x.lettres)})), None)
        if b is not None:
            # la particule a passé d'un mot à l'autre (« ואם » / « שאם », « בכלי תוך » / « כלי בתוך »)
            cv[a] = pr[b] = True
            toutes.append((a, b))
    reste = [a for a in range(len(run)) if not cv[a]]
    libre = [b for b in range(len(rep)) if not pr[b]]
    while reste and libre:
        _r, _d, a, b = max((difflib.SequenceMatcher(None, cle_souple(run[a].lettres),
                                                    cle_souple(rep[b].lettres)).ratio(),
                            -abs(a - b), a, b) for a in reste for b in libre)
        reste.remove(a)
        libre.remove(b)
        toutes.append((a, b))
    return [run[a] for a in reste], paires, toutes + paires


def _interverti(run, rep, paires):
    """Les mots sont-ils les mêmes, dans un autre ORDRE ? Chaque mot de ``run`` a sa
    contrepartie par ressemblance, une à une, et l'ordre n'est pas gardé."""
    if len(run) < 2 or len(run) != len(rep) or len(paires) != len(run):
        return False
    if len({a for a, _ in paires}) != len(run) or len({b for _, b in paires}) != len(rep):
        return False
    js = [b for _, b in sorted(paires)]
    return js != sorted(js)


def _glisser_suppression(a, b, i1, i2, pa):
    """La suppression a[i1:i2] d'un alignement de clés de ``a`` sur ``b`` (``pa`` : paires égales,
    indice de ``a`` → indice de ``b``) peut glisser, à clés égales, sur ses voisins appariés ; rend la
    position (x, y) où le plus de mots appariés sont identiques LETTRE POUR LETTRE, puis passent la
    garde ktiv, et la position d'origine à égalité (même critère que ``glisser``, tour 5)."""
    cands = [(i1, i2)]
    x, y = i1, i2
    while x > 0 and (x - 1) in pa and a[y - 1].cle == a[x - 1].cle:
        x, y = x - 1, y - 1
        cands.append((x, y))
    x, y = i1, i2
    while y < len(a) and y in pa and a[x].cle == a[y].cle:
        x, y = x + 1, y + 1
        cands.append((x, y))
    if len(cands) == 1:
        return i1, i2
    u0, u1 = min(c[0] for c in cands), max(c[1] for c in cands)
    partenaires = [pa[z] for z in range(u0, u1) if not (i1 <= z < i2)]

    def score(c):
        ks = iter(partenaires)
        paires = [(a[z].lettres, b[next(ks)].lettres) for z in range(u0, u1) if not (c[0] <= z < c[1])]
        return (sum(1 for p, q in paires if p == q), sum(1 for p, q in paires if ktiv_seul(p, q)),
                c == (i1, i2))
    return max(cands, key=score)


def marquer_absences(srcs, sig, admis=None, i_me=0):
    """R3 : pour chaque mot de l'édition par défaut, les éditions où il n'a AUCUN
    correspondant (``Mot.absent_de``). Alignement des clés, séif par séif ; un mot est
    absent d'une autre édition s'il est dans une SUPPRESSION, ou dans un remplacement où
    l'autre édition a moins de la moitié des mots (128:9 : « [רש״י ותוספות ור״ן כתבו …
    וכ״כ הב״י] כהנים » / « הכהנים », treize mots absents) — sauf les mots dont l'autre
    côté du remplacement porte la forme (« כהנים » dans « הכהנים »). Une abréviation et
    son développement sont un remplacement de UN mot par plusieurs (« בי״ד » / « ביורה
    דעה ») : jamais une absence. Un passage RÉORDONNÉ n'est pas absent : TE place
    « שלא עשני עבד שלא עשני אשה » après la glose du Rama (46:4) ; il est retrouvé, d'un
    seul tenant, ailleurs dans le séif de l'autre édition — à un mot près pour quatre
    mots et plus (54:3 : « וע״ל סוף סי׳ נ״ו » de ME est chez TE « וע״ל סוף סי׳ נ״ז »,
    déplacé : une leçon, pas une omission). Un ou deux mots sont présents s'ils sont
    parmi les mots non appariés de l'autre édition, ou si leurs initiales y sont
    (190:1 : « קפ״ב וס״ס » / « קפ״ב וסוף סימן », l'abréviation développée et déplacée)."""
    _SUIVANT.clear()
    if i_me is None:
        return
    par = [{} for _ in srcs]
    for i, src in enumerate(srcs):
        for w in src:
            par[i].setdefault(w.seif, []).append(w)
    for s, a in par[i_me].items():
        for x in range(len(a) - 1):
            _SUIVANT[id(a[x])] = a[x + 1]
    for j in range(len(srcs)):
        if j == i_me:
            continue
        for s, a in par[i_me].items():
            if admis is not None and s not in admis.get(j, ()):
                continue
            b = par[j].get(s, [])
            kb = [w.cle for w in b]
            sb = [cle_souple(w.lettres) for w in b]
            ops = difflib.SequenceMatcher(None, [w.cle for w in a], kb, autojunk=False).get_opcodes()
            libres = {sb[y] for tag, i1, i2, j1, j2 in ops if tag in ("insert", "replace") for y in range(j1, j2)}
            pa = {i1 + d: j1 + d for tag, i1, i2, j1, j2 in ops if tag == "equal" for d in range(i2 - i1)}
            for tag, i1, i2, j1, j2 in ops:
                if tag not in ("delete", "replace"):
                    continue
                run = a[i1:i2]
                if tag == "delete":
                    # tour 5 : la suppression glisse, à clés égales, vers les paires identiques lettre
                    # pour lettre — comme ``glisser`` dans l'alignement de la page. ME 160:13 « מחצי לוג
                    # לג׳ ולד׳ », TE « מחצי לג׳ ולד׳ » : les clés de « לוג » et de « לג׳ » sont égales ; TE
                    # n'a pas « לוג », non « לג׳ ». Sans ce glissement, la page qui recopie TE perdait
                    # « לוג » face à ME, et R3 cherchait « absent aussi de TE » sur l'autre mot : la
                    # ligne [ME] disparaissait quand l'alignement de la page, lui, glissait.
                    x, y = _glisser_suppression(a, b, i1, i2, pa)
                    run = a[x:y]
                if tag == "replace":
                    # tour 4 : TOUT remplacement, et mot par mot (``_contreparties``) — le tour 3
                    # n'y voyait une absence que si l'autre édition avait moins de la moitié des
                    # mots (``nj * 2 < ni``), et excusait « אבותינו » dans « ואלהי אבותינו כו׳ » /
                    # « ואלהי וכו׳ » (128:10), « אם » dans « אפי׳ אם » / « אפלו » (131:8)
                    run, _p, _t = _contreparties(run, b[j1:j2])
                if not run:
                    continue
                cs = [cle_souple(w.lettres) for w in run]
                L = len(run)
                if L >= 2 and _contient(sb, cs):
                    continue                       # réordonné
                if L >= 4 and any(sum(sb[y + q] == cs[q] for q in range(L)) >= L - 1
                                  for y in range(len(sb) - L + 1)):
                    continue                       # réordonné, à une leçon près
                for w, c in zip(run, cs):
                    if L <= 2 and (c in libres or _initiales(w, b) or _prefixe_deplace(c, libres)):
                        continue                   # déplacé, ou développé et déplacé
                    w.absent_de.add(sig[j])


def composite(srcs, choix, nseifs):
    """La source confrontée : chaque séif pris dans l'édition retenue pour lui."""
    par = [{} for _ in srcs]
    for i, src in enumerate(srcs):
        for w in src:
            par[i].setdefault(w.seif, []).append(w)
    return [w for s in range(1, nseifs + 1) for w in par[choix[s]].get(s, [])]


def _morceaux(mots):
    """Les suites de mots de même statut (entre parenthèses ou non)."""
    out = []
    for w in mots:
        if out and out[-1][0].ref == w.ref:
            out[-1].append(w)
        else:
            out.append([w])
    return out


def marquer_ailleurs(srcs, sig, admis=None):
    """Pour chaque mot de chaque édition : le mot qui lui correspond dans les autres
    éditions (même séif, alignement des squelettes) est-il entre parenthèses ? Une
    abréviation et son développement ne s'apparient pas mot à mot (« עיין בי״ד » /
    « ועין ביורה דעה ») : un REMPLACEMENT court (six mots au plus de chaque côté)
    donne pour correspondant à chacun de ses mots le passage d'en face entier."""
    par = [{} for _ in srcs]
    rama_ailleurs = set()
    for i, src in enumerate(srcs):
        for w in src:
            par[i].setdefault(w.seif, []).append(w)
    for i in range(len(srcs)):
        for j in range(len(srcs)):
            if i == j:
                continue
            for s, mots_i in par[i].items():
                if admis is not None and not (s in admis.get(i, ()) and s in admis.get(j, ())):
                    continue          # R2 : une édition non alignée sur ce séif ne dit rien de lui
                mots_j = par[j].get(s, [])
                sm = difflib.SequenceMatcher(None, [w.cle for w in mots_i], [w.cle for w in mots_j],
                                             autojunk=False)
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    if tag == "equal":
                        for d in range(i2 - i1):
                            mots_i[i1 + d].ailleurs[sig[j]] = mots_j[j1 + d].ref
                            if mots_j[j1 + d].rama and not mots_j[j1 + d].ref:
                                rama_ailleurs.add(id(mots_i[i1 + d]))
                    elif tag == "replace" and i2 - i1 <= 6 and j2 - j1 <= 6:
                        # découpé aux bords des parenthèses, des deux côtés : « אחר כך
                        # (בית יוסף » / « אח״כ (ב״י » s'apparient en deux morceaux, et
                        # « בית יוסף » a pour correspondant « ב״י », pas « אח״כ ב״י »
                        mi, mj = _morceaux(mots_i[i1:i2]), _morceaux(mots_j[j1:j2])
                        if len(mi) != len(mj):
                            continue
                        for a, en_face in zip(mi, mj):
                            for w in a:
                                w.ailleurs[sig[j]] = en_face[0].ref
                                if any(x.rama and not x.ref for x in en_face):
                                    rama_ailleurs.add(id(w))
    # Un RENVOI (« passage entre parenthèses omis », jamais une troncature du din)
    # est un passage que TOUTES les éditions mettent entre parenthèses. Chacune en
    # met là où l'autre n'en met pas, et ni l'une ni l'autre n'y range que des
    # renvois : ME met entre parenthèses la glose entière du Rama au 6:2 (« ועכ״פ לא
    # יברך ב׳ פעמים … »), TE l'explication de soixante mots du 97:2 (« והא דלקמן בריש
    # סי׳ קכ״ג … »). Lire la parenthèse d'une seule édition rendait la famille d'un
    # même passage omis dépendante de l'édition retenue — et la plus clémente.
    # La glose du Rama de même : ME l'imprime parfois entre parenthèses sans
    # <small> (« (הגה ואין חילוק … », 175:2), TE dans un <small>. Un mot est du Rama
    # si une édition le dit.
    for src in srcs:
        for w in src:
            if w.ref and not all(w.ailleurs.values()):
                w.ref = False
            if id(w) in rama_ailleurs:
                w.rama = True


def plages(nums):
    """[1, 2, 3, 5, 7, 8] → « 1-3, 5, 7-8 »."""
    out, nums = [], sorted(nums)
    i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        out.append(str(nums[i]) if i == j else f"{nums[i]}-{nums[j]}")
        i = j + 1
    return ", ".join(out)


# -------------------------------------------------------------------- verdicts

ORDRE = ["ABSENT NON DÉCLARÉ", "ABSENT DÉCLARÉ", "TRONCATURE", "DÉPLACÉ", "ALTÉRATION", "AJOUT"]
PARTIEL = "PARTIEL (non certifié)"
EGAL = "égalité"
MIXTE = "selon la page"


def principal(fams):
    for f in ORDRE:
        if f in fams:
            return f
    return None


def un_siman(n, args, stats):
    d = fetch(n, args.rafraichir)
    if n in NON_GRAVES:
        stats["non_graves"].append((n, NON_GRAVES[n]))
    if d is None:
        stats["non_atteints"].append((n, RAISONS.get(n, "?")))
        print(f"\n=== Siman {n} — NON ATTEINT : {RAISONS.get(n)}")
        return
    # R1 : l'édition par défaut et la Torat Emet numérotée, et elles SEULES
    ignorees = [e["titre"] for e in d["editions"] if e["titre"] not in REFERENCES]
    for t in ignorees:
        stats["ignorees"].append((n, t))
    eds = sorted((e for e in d["editions"] if e["titre"] in REFERENCES),
                 key=lambda e: e["titre"] != ED_DEFAUT)
    nseifs = len(eds[0]["he"])
    # Une édition découpée autrement ne se confronte pas séif par séif : elle est
    # écartée, et le relevé le dit. (Mesuré le 8 octobre 2026 : aucun cas sur 241.)
    # Depuis le tour 3 le nombre de séifim de ME est celui qu'on attend (``lacunes``) :
    # l'édition écartée est TE, et le siman est PARTIEL.
    retenues = [e for e in eds if len(e["he"]) == nseifs]
    for e in eds:
        if len(e["he"]) != nseifs:
            stats["ecartees"].append((n, e["titre"], len(e["he"]), nseifs))
    # PARTIEL (tour 3) : la réponse de Sefaria n'est pas complète (``lacunes``) — TE non
    # servie, vide, découpée autrement, un séif de TE vide, ou pas d'available_versions.
    # La confrontation à ME seule y est plus STRICTE, jamais plus indulgente (R3 juge
    # toujours les omissions contre ME) ; mais une LEÇON que TE aurait expliquée peut y
    # sortir en écart. D'où : un siman partiel n'est jamais certifié conforme (code 3) ;
    # il ne fait sortir la porte en 1 que par un défaut que TE ne pouvait pas excuser —
    # une omission (absent, troncature, renvoi, parenthèse, mot omis) ou un séif déplacé
    # Toute la page, et non les seuls séifs touchés : un séif de TE servi vide dérange
    # l'alignement de TE sur ses voisins (siman 3, TE 3:2 vidé : les mots de la page du
    # séif ב deviennent des ajouts au séif א, et le séif א passe à ME — une leçon de TE y
    # sortait en écart, code 1, sur une page qui recopie TE lettre pour lettre).
    partiel = NON_GRAVES.get(n)
    if args.edition:
        retenues = [e for e in retenues if args.edition in (sigle(e["titre"]), e["titre"])]
        if not retenues:
            r = (f"édition « {args.edition} » non servie pour ce siman (servies : "
                 + ", ".join(sigle(e["titre"]) for e in eds) + ")")
            stats["non_atteints"].append((n, r))
            print(f"\n=== Siman {n} — NON ATTEINT : {r}")
            return
    manq_ref = [t for t in d.get("manquantes") or [] if t in REFERENCES]
    for t in manq_ref:
        stats["manquantes"].append((n, t))
    for e in eds:
        stats["editions"][e["titre"]] = stats["editions"].get(e["titre"], 0) + 1
    sig = [sigle(e["titre"]) for e in retenues]
    titres_ed = [e["titre"] for e in retenues]
    srcs = [mots_source(e["he"], ed=i) for i, e in enumerate(retenues)]
    i_me = next((i for i, e in enumerate(retenues) if e["titre"] == ED_DEFAUT), None)
    # R2 : l'édition alternative n'est admise qu'aux séifs où elle est alignée sur ME
    admis, non_admis = {}, []
    for i in range(len(srcs)):
        if i == i_me or i_me is None:
            admis[i] = set(range(1, nseifs + 1))
            continue
        admis[i] = set()
        for s in range(1, nseifs + 1):
            r = ressemblance([w for w in srcs[i_me] if w.seif == s], [w for w in srcs[i] if w.seif == s])
            stats["r2_n"] = stats.get("r2_n", 0) + 1
            if stats.get("r2_min") is None or r < stats["r2_min"][0]:
                stats["r2_min"] = (r, f"{n}:{s} {sig[i]}")
            if r >= SEUIL_ALIGNE:
                admis[i].add(s)
            else:
                non_admis.append((s, sig[i], r))
                stats["non_admis"].append((n, s, sig[i], r))
    marquer_ailleurs(srcs, sig, admis)
    marquer_absences(srcs, sig, admis, i_me)
    cles_src = [e["titre"] for e in retenues]
    chap = next((c for c in (chapeau(e["he"][0]) for e in eds) if c), [])
    pages, absentes = {}, []
    for lang, suf in LANGS:
        p = chemin(n, suf)
        if os.path.exists(p):
            pages[lang] = lire_page(p)
        else:
            absentes.append(lang)
    if not pages:
        stats["non_atteints"].append((n, "aucune page niveau-1-base sous " + SECTION))
        print(f"\n=== Siman {n} — NON ATTEINT : aucune page niveau-1-base lue")
        return
    stats["simanim"] += 1
    stats["seifim"] += nseifs
    stats["mots_src"] += sum(len(s) for s in srcs)
    stats["pages"] += len(pages)
    parite = len({tuple(w.lettres for w in pg["mots"]) for pg in pages.values()}) == 1 and not absentes
    resultats, verdict_lang, choix_lang, egal_lang, ktiv_lang = {}, {}, {}, {}, {}
    for lang, pg in pages.items():
        retirer_chapeau(pg, chap, srcs)
        choix, egal, r, r3, kt = confronter(n, srcs, cles_src, pg, nseifs, chap, sig,
                                            admis, i_me, titres_ed)
        ktiv_lang[lang] = kt
        stats["ktiv"] += len(kt)
        stats["ktiv_distincts"].update((n,) + x for x in kt)
        stats["mots_page"] += len(pg["mots"])
        for s, l in r3["ajoutees"]:
            stats["r3_ajoutees"].add((n, s, lang, l))
        for s, l in r3["annotees"]:
            stats["r3_annotees"].add((n, s, lang, l))
        for s, m in r3["courtes"]:
            stats["r3_courtes"].add((n, s, lang, m))
        choix_lang[lang], egal_lang[lang] = choix, egal
        if r is None:
            verdict_lang[lang] = "IDENTIQUE"
            resultats[lang] = {}
            continue
        resultats[lang] = r
        fams = {f for x in r.values() for f in x["familles"]}
        verdict_lang[lang] = principal(fams) or "ÉQUIVALENT"

    # l'édition de référence de chaque séif, les trois pages réunies
    ref_seif = {}
    for s in range(1, nseifs + 1):
        strict = {sig[choix_lang[l][s]] for l in choix_lang if s not in egal_lang[l]}
        ref_seif[s] = EGAL if not strict else (strict.pop() if len(strict) == 1 else MIXTE)
        stats["ref"][ref_seif[s]] = stats["ref"].get(ref_seif[s], 0) + 1

    # comptes : un séif compte dans une famille si l'une des trois pages l'y met
    fam_seif = {}
    for lang, r in resultats.items():
        for s, x in r.items():
            for f in x["familles"]:
                fam_seif.setdefault((s, f), set()).add(lang)
    for (s, f), ls in fam_seif.items():
        stats["seifs_fam"].setdefault(f, set()).add((n, s))
    hors = []
    for s in range(1, nseifs + 1):
        infos = [(l, i) for r in resultats.values() for l, i in zip(r.get(s, {}).get("lignes", []),
                                                                   r.get(s, {}).get("info", []))
                 if i.get("nature") != "reprise" or i.get("ecarts")]
        if infos and all(i.get("excusee") for _, i in infos):
            stats["seuls_excuses"].add((n, s))
        infos = [(l, i) for l, i in infos if not i.get("excusee")]
        if infos and all(i.get("nature") == "leçon" and i.get("suit") for _, i in infos):
            stats["mixtes"].add((n, s))
        p = principal({f for (q, f) in fam_seif if q == s})
        stats["seifs_principal"][p or "CONFORME (au ktiv près)"] = \
            stats["seifs_principal"].get(p or "CONFORME (au ktiv près)", 0) + 1
        if p:
            hors.append(s)
            stats["hors"][ref_seif[s]] = stats["hors"].get(ref_seif[s], 0) + 1
    for lang, r in resultats.items():
        for s, x in r.items():
            for ligne, info in zip(x["lignes"], x["info"]):
                nat = info.get("nature")
                if info.get("muette"):
                    continue
                if info.get("excusee"):
                    stats["excusees"].add((n, s, lang))
                    continue                 # une leçon excusée (R3) n'est pas un écart
                if nat == "troncature" and info.get("pos") in ("fin", "début", "intérieure"):
                    stats["tronc"].add((n, s, info["pos"], bool(info.get("rama")), bool(info.get("decl"))))
                if nat == "leçon" and info.get("abrev"):
                    stats["abrev"].add((n, s))
                if nat == "parenthèse":
                    stats["paren"].add((n, s))
                if nat == "renvoi":
                    stats["renvois"].add((n, s))
                if nat == "troncature" and "entre parenthèses dans" in ligne:
                    stats["tronc_par"].add((n, s))
                if nat in ("omission",) or (nat == "leçon" and not info.get("abrev")):
                    stats["autres_alt"].add((n, s))
                if info.get("reduit"):
                    stats["reduits"].add((n, s))
                if info.get("annonce"):
                    stats["annonce"].add((n, s))
                if info.get("suit"):
                    stats["suit"].add((n, s))
                if info.get("cache"):
                    stats["caches"].add((n, s))
                if info.get("interverti"):
                    stats["intervertis"].add((n, s))
                if info.get("yodvav"):
                    stats["yodvav"].add((n, s))
                if nat == "reprise" and info.get("reprise"):
                    stats["reprises_ecarts"].add((n, s, info["reprise"]))
                for w, p in info.get("ktiv_reprise") or ():
                    stats["reprises_ktiv"].add((n, s, w.lettres, p.lettres))
                stats["natures"].setdefault(nat, set()).add((n, s))
    pires = [verdict_lang[l] for l in verdict_lang]
    pire = (principal(set(pires)) or ("ÉQUIVALENT" if "ÉQUIVALENT" in pires else "IDENTIQUE"))
    if absentes:
        pire = principal(set(pires)) or "PAGE ABSENTE"
        stats["pages_absentes"].append((n, absentes))
    if not parite:
        stats["parite"].append(n)
    sur = True
    # tour 4 : un siman PARTIEL n'affiche jamais « IDENTIQUE » ni « ÉQUIVALENT » — ni dans le
    # tableau des verdicts, ni sur la ligne de langue, ni en --bref (témoin de l'arbitre, TE
    # vidée au siman 224 : « FR: 346 mots confrontés · IDENTIQUE » sous « siman PARTIEL :
    # jamais certifié conforme »). Le code de sortie, lui, était déjà juste (3).
    pire_aff, partiel_txt = pire, ""
    if partiel and not args.edition:
        stats["partiels"].append((n, partiel))
        sur = any(i.get("nature") in SURES or i.get("sure") for r in resultats.values() for x in r.values()
                  for i in x["info"])
        partiel_txt = " à la réponse INCOMPLÈTE de Sefaria — NON CERTIFIÉ (siman PARTIEL)"
        if pire in ("IDENTIQUE", "ÉQUIVALENT"):
            pire_aff = f"PARTIEL ({pire.lower()} à ce qui a été servi, NON CERTIFIÉ)"
    stats["verdict"].setdefault(PARTIEL if pire_aff != pire else pire, []).append(n)
    if pire not in ("IDENTIQUE", "ÉQUIVALENT"):
        if sur:
            stats["divergents"].append(n)
        else:
            stats["a_confirmer"].append(n)
    blocs = "/".join(str(len(pages[l]["textes"])) if l in pages else "—" for l, _ in LANGS)
    cats = [c for c in sig + [EGAL, MIXTE] if any(v == c for v in ref_seif.values())]
    cats = list(dict.fromkeys(cats))

    if args.bref:
        fams = sorted({f for (s, f) in fam_seif}, key=(ORDRE + ["REPRISE", EXCUSEE]).index)
        detail = ", ".join(f"{f.lower()} {len({s for (s, g) in fam_seif if g == f})}" for f in fams)
        refs = " ".join(f"{'=' if c == EGAL else '≠' if c == MIXTE else c} {sum(1 for v in ref_seif.values() if v == c)}"
                        for c in cats)
        aussi = len({s for (m, s, _l, _t) in stats["r3_ajoutees"] if m == n})
        print(f"  siman {n:3d} : {nseifs:2d} séifim · blocs {blocs:>8s} · réf. {refs:<14s} · {pire_aff}"
              f"{' — ' + detail if detail else ''}"
              f"{' · hors édition ' + str(len(hors)) if hors else ''}"
              f"{' · R3 ' + str(aussi) + ' séif(s) absents aussi de TE' if aussi else ''}"
              f"{'' if parite else ' · ⚠️ parité'}")
        return

    print(f"\n=== Siman {n} — {nseifs} séifim sur Sefaria · éditions de référence "
          + ", ".join(sigle(e["titre"]) for e in eds)
          + f" · blocs FR/HE/EN {blocs} ===")
    for t in ignorees:
        print(f"  ⓘ  édition servie et IGNORÉE (R1 — ni l'édition par défaut ni Torat Emet 363) : « {t} »")
    for (_, t, a, b) in [x for x in stats["ecartees"] if x[0] == n]:
        print(f"  ⚠️  édition ÉCARTÉE : « {t} » a {a} séifim, l'édition par défaut {b}")
    for t in manq_ref:
        print(f"  ⚠️  édition de référence listée par Sefaria pour ce siman mais NON SERVIE ou vide : « {t} »"
              " — confrontation à l'édition par défaut seule (plus stricte, jamais plus indulgente)")
    if n in NON_GRAVES:
        print(f"  ⚠️  réponse de Sefaria INCOMPLÈTE, NON gravée dans le cache : {NON_GRAVES[n]}"
              + (" — siman PARTIEL : jamais certifié conforme"
                 + ("" if pire in ("IDENTIQUE", "ÉQUIVALENT") else
                    " ; ses écarts comptent" if sur else
                    " ; ses écarts sont des leçons que TE aurait pu expliquer : À CONFIRMER")
                 if not args.edition else ""))
    for s, sg, r in non_admis:
        print(f"  ⚠️  R2 : {sg} NON ADMISE au séif {s} — ressemblance {r:.3f} avec ME, sous le seuil "
              f"{SEUIL_ALIGNE} : ce n'est pas le même séif ; le séif est confronté à ME seule")
    print("  référence, séif par séif (l'édition la plus proche de la page) : " + " · ".join(
        f"{'égalité' if c == EGAL else c} {plages([s for s, v in ref_seif.items() if v == c])}"
        for c in cats))
    for s in [s for s, v in ref_seif.items() if v == MIXTE]:
        print(f"    séif {s} : " + " · ".join(
            f"{l} {'=' if s in egal_lang[l] else sig[choix_lang[l][s]]}" for l in choix_lang))
    for lang, _ in LANGS:
        if lang in absentes:
            print(f"  {lang}: FICHIER ABSENT {chemin(n, dict(LANGS)[lang])}")
        else:
            v = verdict_lang[lang]
            print(f"  {lang}: {len(pages[lang]['mots'])} mots confrontés · "
                  + (f"{v.lower()}{partiel_txt}" if partiel_txt and v in ("IDENTIQUE", "ÉQUIVALENT") else v)
                  + (f" · chapeau du siman recopié ({len(pages[lang]['chapeau'])} mots, non confronté)"
                     if pages[lang]["chapeau"] else ""))
    # tour 4 : sous ÉQUIVALENT, les mots qui ne sont égaux qu'AU KTIV PRÈS, imprimés pour être
    # contrôlés (une fois si les pages disent la même chose)
    kgroupes = {}
    for lang in [l for l, _ in LANGS if l in ktiv_lang]:
        kgroupes.setdefault(tuple(ktiv_lang[lang]), []).append(lang)
    for kt, ls in kgroupes.items():
        if kt:
            print(f"  ktiv {'/'.join(ls)} : {len(kt)} mot(s) égaux à l'édition retenue AU KTIV PRÈS seulement "
                  "(yod/vav ajoutés d'un côté, ``ktiv_seul`` ; « * » : forme de la page qu'aucune édition "
                  "n'écrit à cet endroit) — à contrôler : " + " · ".join(
                      f"{q}:{numeral(q)} [{e}] « {a} » / « {b} »" for q, e, a, b in kt))
    print("  parité FR/HE/EN du texte source : " + ("✅ identique" if parite else "⚠️  DIVERGENTE"))
    if not parite and "FR" in pages:
        ref = [w.lettres for w in pages["FR"]["mots"]]
        for lang in ("HE", "EN"):
            if lang not in pages:
                continue
            autre = [w.lettres for w in pages[lang]["mots"]]
            if autre == ref:
                continue
            ecarts = [o for o in difflib.SequenceMatcher(None, ref, autre, autojunk=False).get_opcodes()
                      if o[0] != "equal"]
            print(f"    {lang} ≠ FR en {len(ecarts)} endroit(s), dont : " + " · ".join(
                f"« {extrait(pages['FR']['mots'][i1:i2], 4) or '∅'} » → "
                f"« {extrait(pages[lang]['mots'][j1:j2], 4) or '∅'} »"
                for _, i1, i2, j1, j2 in ecarts[:3]))
    if hors:
        print(f"  séifs qui ne correspondent à AUCUNE édition au-delà du ktiv : {len(hors)} — {plages(hors)}")
    # Les lignes de défaut : une fois si les pages disent la même chose, sinon
    # langue par langue. Le sigle entre crochets est l'édition à ouvrir : celle du
    # séif, ou celle de la ligne quand elle diffère (R3 : [ME] dans un séif suivi en TE).
    groupes = {}
    for lang in [l for l, _ in LANGS if l in resultats]:
        r = resultats[lang]
        cle = (tuple(w.lettres for w in pages[lang]["mots"]),
               tuple((s, tuple(r[s]["familles"])) for s in sorted(r)),
               tuple(choix_lang[lang][s] for s in range(1, nseifs + 1)))
        groupes.setdefault(cle, []).append(lang)
    for cle, ls in groupes.items():
        r = resultats[ls[0]]
        lignes = [(s, l, i) for s in sorted(r) for l, i in zip(r[s]["lignes"], r[s]["info"])
                  if not i.get("muette")]
        if not lignes:
            continue
        if len(groupes) > 1:
            print(f"  — {'/'.join(ls)} :")
        for s, l, i in lignes:
            print(f"    séif {s:2d} ({numeral(s)}) [{i.get('sig') or sig[choix_lang[ls[0]][s]]}] : {l}")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("simanim", nargs="*", type=int)
    ap.add_argument("--tous", action="store_true")
    ap.add_argument("--bref", action="store_true")
    ap.add_argument("--rafraichir", action="store_true", help="ignore le cache Sefaria")
    ap.add_argument("--edition", metavar="SIGLE",
                    help="DIAGNOSTIC : confronter à cette seule édition (ME, TE, ou le titre "
                         "complet) au lieu de la plus proche séif par séif")
    args = ap.parse_args(argv)
    if args.tous:
        nums = (sorted(int(x.split("-")[1]) for x in os.listdir(SECTION) if x.startswith("siman-"))
                if os.path.isdir(SECTION) else [])
    else:
        nums = args.simanim
    if not nums and not args.tous:
        ap.print_usage()
        return 2
    stats = {"simanim": 0, "seifim": 0, "mots_src": 0, "mots_page": 0, "pages": 0,
             "non_atteints": [], "verdict": {}, "seifs_fam": {}, "parite": [],
             "divergents": [], "tronc": set(), "abrev": set(), "paren": set(),
             "annonce": set(), "pages_absentes": [], "autres_alt": set(), "reduits": set(),
             "seifs_principal": {}, "ref": {}, "hors": {}, "editions": {}, "ecartees": [],
             "manquantes": [], "suit": set(), "mixtes": set(), "renvois": set(), "tronc_par": set(),
             "natures": {}, "ignorees": [], "non_admis": [], "non_graves": [],
             "r3_ajoutees": set(), "r3_annotees": set(), "r3_courtes": set(),
             "partiels": [], "a_confirmer": [], "ktiv": 0, "ktiv_distincts": set(), "excusees": set(), "seuls_excuses": set(),
             "caches": set(), "intervertis": set(), "yodvav": set(), "reprises_ecarts": set(),
             "reprises_ktiv": set()}
    print(f"=== Recopie du niveau 1 d'Orah Haïm vs Shulchan_Arukh,_Orach_Chayim (Sefaria, "
          + (f"édition IMPOSÉE : {args.edition}" if args.edition else
             "éditions de référence ME et TE 363, la plus proche séif par séif ; "
             "les omissions toujours jugées contre ME")
          + f") — {len(nums)} siman(im) demandé(s) · ROOT {ROOT} ===")
    for n in nums:
        un_siman(n, args, stats)

    print("\n" + "=" * 78)
    print(f"CONFRONTÉ : {stats['simanim']} simanim · {stats['seifim']} séifim · "
          f"{stats['mots_src']} mots de source (toutes éditions lues) · {stats['pages']} pages · "
          f"{stats['mots_page']} mots de page")
    if stats["simanim"] == 0:
        print("❌ RIEN N'A ÉTÉ CONFRONTÉ — la porte ne conclut pas (code 3).")
        if not nums:
            print(f"   aucune page sous {SECTION} : copie lancée hors du dépôt ?")
    if stats["editions"]:
        print("\nÉditions de référence servies par Sefaria (api/v3/texts, version=hebrew|all) :")
        for t, c in sorted(stats["editions"].items(), key=lambda x: x[0] != ED_DEFAUT):
            print(f"  {sigle(t):3s} « {t} » — {c} simanim"
                  + ("  (servie PAR DÉFAUT par api/texts)" if t == ED_DEFAUT else ""))
    ign = {}
    for n, t in stats["ignorees"]:
        ign.setdefault(t, []).append(n)
    print("R1 — éditions servies et IGNORÉES (ni l'édition par défaut ni Torat Emet 363) : "
          + ("; ".join(f"« {t} » sur {len(l)} siman(im) ({plages(l)})" for t, l in ign.items())
             if ign else "aucune"))
    if stats.get("r2_n"):
        print(f"R2 — {stats['r2_n']} séifs d'édition alternative confrontés à ME : "
              f"{len(stats['non_admis'])} NON ADMIS (ressemblance < {SEUIL_ALIGNE})"
              f" · plus faible ressemblance admise ou non : {stats['r2_min'][0]:.3f} ({stats['r2_min'][1]})")
        for n, s, sg, r in stats["non_admis"]:
            print(f"    {n}:{s} {sg} {r:.3f}")
    if stats["non_graves"]:
        print("Réponses de Sefaria INCOMPLÈTES, lues mais NON gravées dans le cache : " + "; ".join(
            f"{n} ({r})" for n, r in stats["non_graves"]))
    if stats["ref"]:
        tot = sum(stats["ref"].values())
        print("\nÉdition de référence, séif par séif (la plus proche de la page, les trois pages réunies) :")
        for c in sorted(stats["ref"], key=lambda c: (c in (EGAL, MIXTE), c)):
            quoi = {EGAL: "égalité — éditions exactement aussi proches (ME retenue)",
                    MIXTE: "selon la page — les trois langues ne retiennent pas la même"}.get(c, c)
            print(f"  {quoi:58s} {stats['ref'][c]:5d} séifs · dont hors édition {stats['hors'].get(c, 0):4d}")
        print(f"  {'TOTAL':58s} {tot:5d}")
        print(f"Séifs qui ne correspondent à AUCUNE édition au-delà du ktiv : "
              f"{sum(stats['hors'].values())} sur {tot}")
    if stats["ecartees"]:
        print("Éditions ÉCARTÉES (découpe en séifim différente) : " + "; ".join(
            f"{n} {sigle(t)} {a} séifim ≠ {b}" for n, t, a, b in stats["ecartees"]))
    if stats["manquantes"]:
        print("Éditions listées mais NON SERVIES (confrontation partielle) : " + "; ".join(
            f"{n} « {t} »" for n, t in stats["manquantes"]))
    print("\nSimanim par verdict (le pire des trois pages) :")
    for v in ["IDENTIQUE", "ÉQUIVALENT", PARTIEL] + ORDRE + ["PAGE ABSENTE"]:
        if v in stats["verdict"]:
            l = stats["verdict"][v]
            print(f"  {v:20s} {len(l):4d}" + ("" if v in ("IDENTIQUE", "ÉQUIVALENT") else
                                               "   " + " ".join(map(str, l))))
    print("\nSéifs par verdict principal (chacun compté UNE fois, sous son pire défaut, "
          "les trois pages réunies) :")
    for v in ["CONFORME (au ktiv près)"] + ORDRE:
        if v in stats["seifs_principal"]:
            print(f"  {v:24s} {stats['seifs_principal'][v]:5d}")
    print("\nSéifs par famille (un séif compte dans chaque famille où l'une des trois pages le met) :")
    for f in ORDRE + ["REPRISE", EXCUSEE]:
        e = stats["seifs_fam"].get(f, set())
        print(f"  {f:20s} {len(e):4d} séifs dans {len({n for n, _ in e}):3d} simanim"
              + ("   (information : un passage déjà donné, cité une seconde fois — "
                 "ne fait pas à lui seul diverger le siman)" if f == "REPRISE" else
                 "   (information, R3 : la leçon d'une AUTRE édition de référence, au même endroit "
                 "du séif — n'est pas un écart)" if f == EXCUSEE else ""))
    tr = stats["tronc"]
    if tr:
        print(f"  dont troncatures : fin {sum(1 for t in tr if t[2] == 'fin')} · "
              f"début {sum(1 for t in tr if t[2] == 'début')} · "
              f"intérieure {sum(1 for t in tr if t[2] == 'intérieure')} · "
              f"portant sur le Rama {sum(1 for t in tr if t[3])} · "
              f"déclarées par « … » {sum(1 for t in tr if t[4])} (occurrences séif × position)")
    if stats["tronc_par"]:
        print(f"  dont troncatures d'un passage qu'une édition SEULE met entre parenthèses : "
              f"{len(stats['tronc_par'])} séifim")
    if stats["annonce"]:
        print(f"  dont absents ANNONCÉS par le titre de leur bloc : {len(stats['annonce'])} séifim")
    if stats["abrev"]:
        print(f"  dont altérations par abréviation : {len(stats['abrev'])} séifim")
    if stats["suit"]:
        print(f"  dont altérations où la page suit L'AUTRE édition (« la page suit ici … ») : "
              f"{len(stats['suit'])} séifim — dont {len(stats['mixtes'])} séifim dont c'est le SEUL écart "
              "(éditions mêlées dans le séif, aucun mot inventé)")
    if stats["paren"]:
        print(f"  dont passages que TOUTES les éditions mettent entre parenthèses, omis : {len(stats['paren'])} séifim")
    if stats["renvois"]:
        print(f"  dont RENVOIS omis (« ועיין … סי׳ … », jamais une troncature du din ni la glose du Rama) : "
              f"{len(stats['renvois'])} séifim")
    if stats["autres_alt"]:
        print(f"  dont autres altérations (mots changés, omis, ajoutés, une lettre) : "
              f"{len(stats['autres_alt'])} séifim")
    if stats["reduits"]:
        print(f"  dont séifim réduits à quelques mots réécrits (comptés en TRONCATURE) : "
              f"{len(stats['reduits'])}")
    if stats["caches"]:
        print(f"  dont omissions CACHÉES dans un remplacement (tour 4 : un mot sans contrepartie en face) : "
              f"{len(stats['caches'])} séifim")
    if stats["intervertis"]:
        print(f"  dont mots intervertis : {len(stats['intervertis'])} séifim")
    if stats["yodvav"]:
        print(f"  dont yod/vav ÉCHANGÉS, ou mater sur un mot de deux lettres (un autre mot, pas du ktiv — "
              f"tour 4) : {len(stats['yodvav'])} séifim")
    # tour 5 : la reprise confrontée mot à mot (``juger_reprise``) — imprimé même à zéro : une
    # porte qui ne dit pas qu'elle a regardé ne prouve pas qu'elle a regardé
    rs = stats["seifs_fam"].get("REPRISE", set())
    re_ = stats["reprises_ecarts"]
    print(f"  REPRISES confrontées mot à mot (tour 5) : {len(rs)} séif(s) ; écarts dans une reprise : "
          f"{len({(a, b) for a, b, _g in re_})} séif(s)"
          + (" — " + ", ".join(f"{g} {sum(1 for x in re_ if x[2] == g)}"
                               for g in sorted({x[2] for x in re_})) if re_ else "")
          + f" ; mots d'une reprise égaux au ktiv près seulement (listés sur la ligne REPRISE) : "
            f"{len(stats['reprises_ktiv'])}")
    nat = stats["natures"]
    if nat:
        print("\nSéifs par NATURE d'écart (un séif dans chaque nature où l'une des pages le met) :\n  " + " · ".join(
            f"{k} {len(nat[k])}" for k in ("absent", "troncature", "renvoi", "parenthèse", "omission",
                                          "leçon", "ordre", "ajout", "reprise") if k in nat))
    if stats["parite"]:
        print(f"\nParité FR/HE/EN du texte source DIVERGENTE : {len(stats['parite'])} simanim — "
              + " ".join(map(str, stats["parite"])))
    if stats["simanim"]:
        etoiles = {x for x in stats["ktiv_distincts"] if x[-1].endswith(" *")}
        print(f"\nGARDE KTIV (tour 4) : {len(stats['ktiv_distincts'])} mot(s) ({stats['ktiv']} mot(s) × page) égaux à "
              "l'édition retenue au ktiv près seulement (yod/vav ajoutés d'un côté) — listés siman par siman, "
              f"à contrôler, dont {len(etoiles)} (« * ») dont la forme n'est à cet endroit celle d'aucune "
              f"édition ; un yod/vav ÉCHANGÉ, ou une mater sur un mot de deux lettres, est un autre mot : "
              f"{len(stats['yodvav'])} séif(s)")
    a3, n3, l3 = stats["r3_ajoutees"], stats["r3_annotees"], stats["r3_courtes"]
    if stats["simanim"]:
        print(f"\nR3 — UNE AUTRE ÉDITION EXPLIQUE UNE LEÇON, JAMAIS UNE OMISSION (omissions jugées contre ME) :")
        print(f"  passages de ME absents de la page ET de TE, dans un séif où TE est l'édition la plus proche "
              f"(lignes [ME] ajoutées) : {len({(n, s) for n, s, _l, _t in a3})} séifs · "
              f"{len({(n, s, l) for n, s, l, _t in a3})} séifs × page")
        for (n, s) in sorted({(n, s) for n, s, _l, _t in a3}):
            ls = sorted({l for m, q, l, _t in a3 if (m, q) == (n, s)})
            t = next(t for m, q, _l, t in sorted(a3) if (m, q) == (n, s))
            print(f"    {n}:{s} [{'/'.join(ls)}] {t[:150]}")
        print(f"  lignes d'omission annotées « absent aussi de Torat Emet 363 » (ME retenue) : "
              f"{len({(n, s) for n, s, _l, _t in n3})} séifs · {len({(n, s, l) for n, s, l, _t in n3})} séifs × page")
        ex = stats["excusees"]
        print(f"  LEÇONS EXCUSÉES (tour 4) — la page écrit, au milieu d'un séif retenu dans une édition, la "
              f"leçon de l'AUTRE au même endroit : {len({(n, s) for n, s, _l in ex})} séifs · "
              f"{len(ex)} séifs × page ; séifs dont TOUTES les lignes sont des leçons excusées (donc conformes) : "
              f"{len(stats['seuls_excuses'])}")
        print(f"  dont omissions d'UN OU DEUX mots hors parenthèses (le tour 2 les excusait comme « leçon de TE » ; "
              f"SIGNALÉES depuis le tour 3) : {len({(n, s) for n, s, _l, _m in l3})} séifs · "
              f"{len({(n, s, l) for n, s, l, _m in l3})} séifs × page"
              + (" — " + " · ".join(sorted({f"{n}:{s} « {m} »" for n, s, _l, m in l3},
                                           key=lambda x: tuple(map(int, x.split(" ")[0].split(":")))))
                 if l3 else ""))
    if stats["pages_absentes"]:
        print("Pages absentes : " + "; ".join(f"{n} {'/'.join(l)}" for n, l in stats["pages_absentes"]))
    if stats["non_atteints"]:
        print(f"\nNON ATTEINTS ({len(stats['non_atteints'])}) — rien n'est conclu sur eux :")
        for n, r in stats["non_atteints"]:
            print(f"  siman {n} : {r}")
    if stats["partiels"]:
        print(f"\nPARTIELS ({len(stats['partiels'])}) — confrontés à une réponse INCOMPLÈTE de Sefaria, "
              "jamais certifiés conformes :")
        for n, r in stats["partiels"]:
            etat = ("divergent (un défaut que TE ne pouvait pas excuser)" if n in stats["divergents"] else
                    "À CONFIRMER (des leçons que TE aurait pu expliquer)" if n in stats["a_confirmer"] else
                    "conforme à ce qui a été servi")
            print(f"  siman {n} : {etat} — {r}")
    if stats["simanim"] == 0:
        return 3
    if stats["divergents"]:
        print(f"\n❌ {len(stats['divergents'])} siman(im) dont le texte source diverge, au-delà du ktiv "
              "haser/malé, de TOUTES les éditions hébraïques de Sefaria — NE PAS PUBLIER sans relecture")
        return 1
    if stats["non_atteints"] or stats["partiels"]:
        print("\n⚠️  conforme sur ce qui a été lu, mais des simanim n'ont pas été atteints, ou seulement "
              "en partie (code 3) — la porte ne certifie pas ce qu'elle n'a pas lu en entier")
        return 3
    if args.edition and args.edition not in ("ME", ED_DEFAUT):
        print(f"\n⚠️  DIAGNOSTIC à une seule édition ({args.edition}) : conforme à elle, mais R3 n'y est pas "
              "appliquée — une omission que cette édition partage avec la page n'y est pas vue. "
              "Ce n'est pas la porte (code 3).")
        return 3
    print("\n✅ RECOPIE DU NIVEAU 1 : conforme, séif par séif, à une édition de Sefaria (au ktiv près)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
