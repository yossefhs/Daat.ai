#!/usr/bin/env python3
"""L'entrée d'appareil est-elle rattachée au bon séif ?

Une page qui écrit « le psak du Taz ס״ק י״ח (seif 7) » promet au lecteur qu'en
ouvrant le séif 7 il y trouvera ce ס״ק. Aucune des dix autres portes ne vérifie
cette promesse : `verifier-citations.py` confronte le VERBATIM à la source et le
trouve exact — le ס״ק י״ח existe, il dit bien ce que la page lui fait dire — mais
il ne regarde pas où il est posé. Trouvé au siman 119 de Yoré Déa : le Taz ס״ק י״ח
est ancré au séif 19 (son lemme est `וכל זה אינו נוהג בחשוד`, et il traite du
ḥachoud envoyé acheter du fromage) ; la page le donne au séif 7.

La source de vérité est l'ancre que Sefaria pose DANS le texte du Choul'han Aroukh :
    <i data-commentator="Turei Zahav" data-order="18"></i>
`data-order` est le numéro du ס״ק dans le siman, et le séif où l'ancre se trouve est
le séif auquel il se rattache. Vérifié : les ordres croissent avec les séifim, et le
total par commentateur coïncide exactement avec le nombre d'entrées que Sefaria sert
pour ce commentateur (siman 234 : 93 ש״ך, 66 ט״ז, 62 באר היטב).

Ce contrôle rend des CANDIDATS, jamais des verdicts, et sort toujours en 0 : une page
peut légitimement citer un ס״ק d'un autre séif quand il éclaire le sien. Ce qu'il faut
lire dans sa sortie, c'est (a) un écart isolé — à vérifier à la main — et (b) un écart
SYSTÉMATIQUE, tout un siman décalé d'un cran, qui est le piège de la règle 22-bis :
le décompte aplati de Sefaria décale toute la numérotation.

Usage :
  python3 scripts/verifier-ancrage.py                       # tout Yoré Déa
  python3 scripts/verifier-ancrage.py --path sources/yoreh-deah/siman-119
  python3 scripts/verifier-ancrage.py 119 120 234
"""
import sys, os, re, json, glob, subprocess, bisect

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# v2 : le format stocké change (on garde aussi le compte d'ancres et d'ancres sans
# numéro), donc NOUVEAU fichier — relire un cache v1 rendrait une carte amputée des
# ancres que cette version sait justement lire, et la porte reviendrait muette.
# v3 : l'entree porte en plus `ns`, le NOMBRE DE SEIFIM que Sefaria sert pour ce
# siman. Sans lui la porte acceptait un seif annonce plus grand que le siman n'en
# compte — YD 193 sert UN seif et la page annonce le 11, YD 222 un seul et la page
# annonce le 2. Relire un cache v2 rendrait ce controle muet faute du champ, donc
# NOUVEAU fichier, comme au passage v1 → v2.
CACHE = os.path.join(ROOT, ".cache-ancrage-v3.json")

GEM = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'כ':20,'ל':30,
       'מ':40,'נ':50,'ס':60,'ע':70,'פ':80,'צ':90,'ק':100,'ר':200,'ש':300,'ת':400}

def gem(s):
    s = re.sub(r'["״\'׳]', '', s or '')
    return sum(GEM[c] for c in s) if s and all(c in GEM for c in s) else None

def numero_attribut(v):
    """Le numéro de ס״ק porté par un `data-label` de Sefaria, ou None.

    Un `data-label` n'est PAS de la prose : c'est un champ contrôlé qui porte le
    numéro tel qu'il est imprimé, et Sefaria l'écrit SANS gershayim — mesuré :
    « טו », « יא », « קכג ». L'exigence du gershayim, qui protège la lecture d'un
    texte suivi contre la guématrie de tout mot court, n'a donc pas lieu ici et
    rendrait la lecture muette. Ce qui la remplace : au plus trois lettres, et une
    valeur dans l'étendue d'un ס״ק réel. Mesuré sur Orah Haïm 301, le plus long ס״ק
    de Michna Beroura rencontré est קכג = 123.

    Tout ce qui n'est pas un numéral rend None, et l'ancre est alors comptée comme
    NON CONFRONTABLE au lieu d'être jetée en silence : les labels non numériques
    existent — mesuré, « ♦ » (Ateret Zekenim), « • » et « (°) » (Be'er HaGolah),
    « ♯ » (Nekudot HaKesef).
    """
    v = (v or '').strip()
    if not re.fullmatch(r'[א-ת]{1,3}["״\'׳]?[א-ת]?', v):
        return None
    n = gem(v)
    return n if n and 1 <= n <= 400 else None

# Les libellés de `data-commentator` sont des translittérations ANGLAISES ; les pages
# citent en hébreu, en français et en anglais. Tout nom absent de cette table rend la
# lecture des ancres inutile pour l'ouvrage concerné — c'est ce qui s'est produit :
#
#  · LA MICHNA BEROURA N'Y ÉTAIT PAS, et c'est l'ouvrage le plus cité du dépôt. Aucune
#    de ses citations n'était confrontée à quoi que ce soit dans Orah Haïm ni Chabbat.
#  · « פת״ש » y était mappé sur « Pitchei Teshuva », quand Sefaria écrit « Pithei
#    Teshuva » — mesuré sur huit simanim de Yoré Déa et onze d'Orah Haïm : 125 ancres
#    portent « Pithei Teshuva », ZÉRO porte « Pitchei Teshuva ». La clé était morte.
#
# Les valeurs de droite sont celles que Sefaria sert réellement, relevées et non
# supposées ; la forme avec ה d'article (« הש״ך », « המ״ב ») est courante dans les pages.
NOMS = {
    # ---- Yoré Déa ----
    'ש״ך': 'Siftei Kohen', 'ש"ך': 'Siftei Kohen', 'הש״ך': 'Siftei Kohen',
    'שפתי כהן': 'Siftei Kohen', 'Chakh': 'Siftei Kohen', 'Shakh': 'Siftei Kohen',
    'Shach': 'Siftei Kohen', 'Siftei Kohen': 'Siftei Kohen',
    'ט״ז': 'Turei Zahav', 'ט"ז': 'Turei Zahav', 'הט״ז': 'Turei Zahav',
    'טורי זהב': 'Turei Zahav', 'Taz': 'Turei Zahav', 'Turei Zahav': 'Turei Zahav',
    'פת״ש': 'Pithei Teshuva', 'פת"ש': 'Pithei Teshuva', 'פ״ת': 'Pithei Teshuva',
    'פתחי תשובה': 'Pithei Teshuva', 'Pithei Techouva': 'Pithei Teshuva',
    "Pit'hei Techouva": 'Pithei Teshuva', 'Pitchei Teshuva': 'Pithei Teshuva',
    'Pithei Teshuva': 'Pithei Teshuva',
    'נקודות הכסף': 'Nekudot HaKesef', 'Nekoudot HaKessef': 'Nekudot HaKesef',
    'Nekudot HaKesef': 'Nekudot HaKesef',
    'כרתי': 'Kereti', 'Kereti': 'Kereti', 'פלתי': 'Peleti', 'Peleti': 'Peleti',
    # ---- Orah Haïm et Hilkhot Chabbat ----
    # Michna Beroura : l'ouvrage le plus cité du dépôt, et il manquait entièrement.
    'משנה ברורה': 'Mishnah Berurah', 'המשנה ברורה': 'Mishnah Berurah',
    'משנ״ב': 'Mishnah Berurah', 'משנ"ב': 'Mishnah Berurah',
    'המשנ״ב': 'Mishnah Berurah', 'המשנ"ב': 'Mishnah Berurah',
    'מ״ב': 'Mishnah Berurah', 'מ"ב': 'Mishnah Berurah',
    'המ״ב': 'Mishnah Berurah', 'המ"ב': 'Mishnah Berurah',
    'Michna Beroura': 'Mishnah Berurah', 'Mishna Beroura': 'Mishnah Berurah',
    'Mishnah Berurah': 'Mishnah Berurah', 'Mishna Berura': 'Mishnah Berurah',
    'MB': 'Mishnah Berurah',
    'מג״א': 'Magen Avraham', 'מג"א': 'Magen Avraham', 'המג״א': 'Magen Avraham',
    'מגן אברהם': 'Magen Avraham', 'Magen Avraham': 'Magen Avraham',
    'Maguen Avraham': 'Magen Avraham',
    'שע״ת': "Sha'arei Teshuvah", 'שע"ת': "Sha'arei Teshuvah",
    'שערי תשובה': "Sha'arei Teshuvah", 'Chaarei Techouva': "Sha'arei Teshuvah",
    "Sha'arei Teshuvah": "Sha'arei Teshuvah",
    'ביאור הגר״א': 'Beur HaGra', 'באור הגר״א': 'Beur HaGra',
    'הגר״א': 'Beur HaGra', 'Beour HaGra': 'Beur HaGra', 'Beur HaGra': 'Beur HaGra',
    'באר הגולה': "Be'er HaGolah", "Be'er HaGolah": "Be'er HaGolah",
    'Beer HaGola': "Be'er HaGolah",
    'עטרת זקנים': 'Ateret Zekenim', 'Ateret Zekenim': 'Ateret Zekenim',
    'אשל אברהם': 'Eshel Avraham', 'Eshel Avraham': 'Eshel Avraham',
    # « באר היטב » sert les deux compartiments.
    'באר היטב': "Ba'er Hetev", 'הבאר היטב': "Ba'er Hetev",
    'באה״ט': "Ba'er Hetev", 'באה"ט': "Ba'er Hetev",
    'Baer Hetev': "Ba'er Hetev", 'Beer Hetev': "Ba'er Hetev",
    "Ba'er Hetev": "Ba'er Hetev",
}
ALT = r"|".join(sorted((re.escape(k) for k in NOMS), key=len, reverse=True))

# Un numéral de prose, suivi d'une FRONTIÈRE. Sans elle, l'alternative « une lettre
# seule » happe la PREMIÈRE LETTRE D'UN MOT : « סעיף זה » — « ce séif » — se lisait
# « séif ז », c'est-à-dire séif 7, et le siman 122 rendait sur ce seul motif des
# écarts entièrement fabriqués. C'est la guématrie par un autre chemin.
NUM_PROSE = r"""(?:\d{1,3}|[א-ת]["״'׳][א-ת]|[א-ת]{1,2}["״'׳]|[א-ת])(?![א-ת])"""

def numero_prose(v):
    """Le nombre écrit dans une PAGE, ou None. Règle opposée à `numero_attribut`.

    Ici on lit de la prose, et en prose tout mot hébreu court est un nombre si on le
    lit en guématrie : « סעיף זה » — « ce séif » — vaut 12, « סעיף זו » 13. D'où
    l'exigence du dépôt, reprise ici : une lettre seule, ou le gershayim. Un
    `data-label`, lui, est un champ contrôlé et suit la règle inverse.
    """
    v = (v or '').strip()
    if v.isdigit():
        return int(v)
    if not re.search(r'["״\'׳]', v) and len(re.sub(r'["״\'׳]', '', v)) > 1:
        return None
    return gem(v)

# Le tiret de PLAGE n'a pas d'espaces — « סעיף ב-ח », « ס״ק ה-ו ». C'est le piège qui
# a produit 35 fausses anomalies sur 49 dans verifier-etiquettes.py : lu comme une
# borne unique, « séif 2-8 » devient « séif 2 » et tout ce qui vit aux séifim 3 à 8
# passe pour un écart. On lit la plage, et un rattachement qui tombe DEDANS est
# conforme.
PLAGE = r"""(?:\s*[-‑–]\s*(?P<%s2>\d{1,3}|[א-ת]["״'׳][א-ת]|[א-ת]{1,2}["״'׳]|[א-ת])(?![א-ת]))?"""

# Le sof-kof s'ecrit aussi EN LETTRES LATINES, et la porte n'acceptait que la forme
# hebraique : le francais du depot ecrit « MB s"k 5-6 », l'anglais « MB s.k. 5-6 ».
# Mesure : 5 722 formes latines portant un numero (yoreh-deah 5 584, shabbat 134,
# orah-haim 4), dont 34 avec le guillemet droit. La rangee temoin du siman 267 est
# dans ce cas dans DEUX de ses trois langues, et la porte ne voyait que l'hebreu.
#
# La forme SANS separateur — « sk1 » — est volontairement exclue : mesuree, elle
# n'est pas de la prose mais du BALISAGE, `id="cp-sk1"` et `data-copy-target="#cp-sk1"`,
# 349 fois pour le seul « sk1 ». La frontiere gauche `(?<![A-Za-z])` est indispensable :
# sans elle « task 1 » et « disk 2 » portent un « sk » suivi d'un nombre.
SK_LAT = r"""(?<![A-Za-z])s[.""״’']?k[.""״’']?\s*"""
SK_  = r"(?:ס[\"״]ק\s*|(?i:" + SK_LAT + r"))(?P<sk>" + NUM_PROSE + r")" + (PLAGE % 'sk')
QUI_ = r"(?P<qui>" + ALT + r")(?![.:׃])"
# `seif` s'ecrit avec une majuscule dans les tableaux — mesure : « Seif » 16 067,
# « Seif » accentue 3 454, « se'if » 1 490, 30 avec l'apostrophe typographique. Le
# motif etait SENSIBLE A LA CASSE et ne captait aucune des deux premieres formes.
# La casse est relachee sur le SEUL mot-cle, par un groupe `(?i:…)` : la relacher sur
# tout le motif la relacherait aussi sur la table des ouvrages, ou « MB » deviendrait
# « mb » et « Taz » « taz » dans n'importe quel mot.
#
# Frontiere GAUCHE, et c'est le piege des deux cotes que le depot a deja paye : sans
# elle le motif s'apparie A L'INTERIEUR d'un mot. `ה` colle devant `סעיף` est
# l'ARTICLE DEFINI — « הסעיף », « LE seif » — qui parle DU seif au lieu d'y renvoyer,
# et c'est ainsi que « למה מדבר הסעיף ב מעות » (« pourquoi le seif parle-t-il D'argent »)
# se lisait « seif 2 ». Mesure sur les 816 appariements : les prefixes qui renvoient
# reellement sont tous conserves — `ב` 49 (« בסעיף ד », dans le seif 4), `ו` 4, `ד` 3,
# `ל` 3, `מ` 2, `ש` 1 ; l'article `ה` n'apparait QU'UNE FOIS dans tout le depot, et
# c'est exactement le faux positif du siman 222. Le cout de la frontiere est donc
# d'un appariement, et il etait faux.
#
# Ce qui n'est PAS fait, et il faut le dire : l'arbitre proposait d'ecarter la lettre
# NUE quand elle peut etre une preposition (152 appariements, dont 36 sur ב/ו/ה). J'ai
# mesure cette piste et je l'ai REFUSEE : sur les 38 lettres nues suivies d'un mot
# hebreu, la quasi-totalite sont de vrais renvois — « סעיף ד נוקט חשבון », « seif 4
# tient un compte » —, et les ecarter aurait echange un faux positif contre 38 mutismes.
# La lettre nue est d'ailleurs la forme du cas temoin lui-meme (« סעיף ג », « ס״ק ה-ו »).
SF_  = r"(?:(?<![A-Za-z])(?i:s[eé][’\']?if)|(?<!ה)סעיף)\s*(?P<sf>" + NUM_PROSE + r")" + (PLAGE % 'sf')

# Deux ordres, et il faut les deux. Le motif d'origine n'en lisait qu'un — le ס״ק
# PUIS le séif — qui est la forme de Yoré Déa. Les pages d'Orah Haïm et de Chabbat
# écrivent aussi l'ordre inverse : « סעיף ג · מ״ב ס״ק ח », « seif 1, MB ס״ק ט »,
# « seif 2 du Mehaber, expliqué par la Michna Beroura au ס״ק ו ».
#
# La PARENTHÈSE FERMANTE est une frontière dans les deux sens. Sans elle le motif
# enjambe deux citations voisines et attribue à l'une le séif de l'AUTRE : au siman
# 122, « הש״ך (ס״ק ח) וערוך השולחן (סעיף כ׳ » donnait au ש״ך le séif de l'Aroukh
# HaChoul'han. C'est la même faute que la frontière de bloc corrige plus bas, à
# l'échelle de la phrase.
RX = re.compile(QUI_ + r"(?P<mid>[^.;<)]{0,60}?)" + SK_ +
                r"[^.;<)]{0,40}?[\(—–-]\s*" + SF_)
RX_INV = re.compile(SF_ + r"(?P<mid>[^.;<)]{0,60}?)" + QUI_ + r"[^.;<)]{0,40}?" + SK_)

# Un nom d'ouvrage DANS l'intervalle veut dire qu'on a changé de citation en route.
RX_AUTRE = re.compile(ALT)

# …mais l'ouvrage qui s'interpose n'est pas toujours l'un de ceux qui portent des
# ancres, et il ne se tient pas toujours DANS l'intervalle. Cas mesuré, et il était
# un faux positif de ce contrôle même : au siman 120 de Yoré Déa, la cellule
#   « ערוך השולחן יורה דעה סימן ק״כ סעיף מ״ה · ט״ז יו״ד ק״כ ס״ק י »
# porte DEUX références ; le séif מ״ה — quarante-cinq — est celui de l'AROUKH
# HACHOUL'HAN, et le Choul'han Aroukh n'a ici que seize séifim. Lu comme un séif du
# Choul'han Aroukh, il donnait un écart de 37 dans les trois langues, et c'était le
# plus gros du relevé. Un ouvrage nommé JUSTE AVANT le séif emporte ce séif avec lui.
OUVRAGES_TIERS = re.compile(
    r"ערוך השולחן|ערוה[\"״]ש|Aroukh HaShoulhan|Aroukh HaChoul'han|Arukh HaShulchan|"
    r"חכמת אדם|פרי מגדים|פמ[\"״]ג|דרכי תשובה|חוות דעת|יד אפרים|כף החיים|"
    r"שו[\"״]ע הרב|אליה רבה|לבוש|רמב[\"״]ם|בית יוסף|ב[\"״]י|טור\b|"
    r"Rambam|Beit Yossef|Tour\b|Levoush|Hokhmat Adam")

# Le seif peut appartenir a un AUTRE SIMAN du meme ouvrage, et c'est la conduite
# normale d'un renvoi. `OUVRAGES_TIERS` protege contre le seif d'un autre OUVRAGE ;
# rien ne protegeait contre un renvoi a un autre SIMAN du Choul'han Aroukh. Deux cas
# mesures, tous deux de faux ecarts : au siman 193 de Yore Dea,
#   « ועיין סי׳ קצ״ו סעיף י״א (ט״ז יו״ד קצ״ג ס״ק ד) »
# ou le seif 11 est celui du siman 196 — le 193 ne comptant qu'UN seif ; et au siman
# 96, « דבסי׳ ק״ג סעיף ו׳ … (ט״ז יו״ד צ״ו ס״ק י) », ou le seif 6 est celui du 103.
#
# Le marqueur doit TOUCHER le seif : on ne lit que les ~40 caracteres qui le precedent.
# Et l'appariement n'est ecarte que si le numero lu DIFFERE du siman de la page : une
# page qui ecrit « בסימן רמ״ז סעיף ב » chez elle se renvoie a elle-meme, et reste
# confrontable. Le `ס״ק` ne peut pas etre pris pour un marqueur de siman : `ס[׳']`
# n'accepte que le geresh, jamais le gershayim de `ס״ק`.
# Les pages hebraiques doublent le numeral de sa transcription en chiffres, separee
# par un point median — « בסימן צ״ט · 99 סעיף ז ». Exiger que le marqueur TOUCHE le
# seif fermait donc le faux positif en francais et en anglais et le LAISSAIT en
# hebreu : la garde aurait couvert deux lecteurs sur trois, ce qui est le defaut meme
# qu'on est venu reparer. On tolere la transcription, et on exige qu'elle CONFIRME la
# guematrie — si les deux ne disent pas le meme nombre, on ne comprend pas la forme
# et on ne conclut rien.
MARQ_SIMAN = re.compile(
    "(?:סימן|" + "סי[׳'\"״]" + "|" + "ס[׳']" + "|siman)" + r"\s*"
    r"(?P<sim>\d{1,3}|" + "[א-ת]{1,4}[\"״][א-ת]|[א-ת]{1,4}[\"״׳']" + r")"
    r"(?:\s*[·•]\s*(?P<tr>\d{1,3}))?\s*$", re.I)

def siman_etranger(txt, pos, n):
    """Le seif qui commence a `pos` est-il annonce comme celui d'un AUTRE siman ?"""
    m = MARQ_SIMAN.search(txt[max(0, pos - 44):pos])
    if not m:
        return False
    v = m.group('sim')
    autre = int(v) if v.isdigit() else gem(v)
    if not autre:
        return False
    if m.group('tr') and int(m.group('tr')) != autre:
        return False          # forme non comprise : on ne tranche pas
    return autre != n

# Troisième forme, et c'est la seule que pratique Orah Haïm : la CARTE D'ANCRAGE
# explicite, où la page énonce d'un bloc le rattachement qu'elle a suivi —
#   « séif א → ס״ק א-ה, ב → ו-ח, ג → ט-יג, ד → יד, ה → טו-טז, ו → יז-יט »  (siman 9)
#   « י:א → ס״ק א-ה; י:ד → ט-יא; י:ה-ו → יב-כג; י:ז → כד-כז »              (siman 10)
# C'est la promesse la plus explicite qu'une page puisse faire sur ce point, et elle
# échappait aux deux ordres précédents parce qu'elle n'écrit « ס״ק » qu'UNE FOIS, en
# tête, les maillons suivants étant nus.
#
# La flèche seule ne suffit pas à reconnaître la forme : les pages s'en servent aussi
# en prose — « רוב בגד → חייבת », « mostly cloth → חייבת ». Mesuré sur le dépôt :
# 561 flèches, dont une poignée seulement sont des cartes d'ancrage. Deux exigences
# la cernent : la TÊTE porte « ס״ק » à droite de la flèche, et les deux côtés de
# chaque maillon sont des numéraux à frontière — ce qui écarte « חייבת » (ח suivi de
# י) sans écarter « ה » ou « יז ».
# Une carte est une LISTE STRUCTURÉE, non de la prose : ses numéraux s'écrivent nus
# — « ג → ט-יג ». La règle du gershayim, qui protège la prose de la guématrie, n'a
# pas lieu ici et coupait la chaîne au troisième maillon ; ce qui la remplace est la
# forme même de la carte, une suite de flèches séparées par des virgules, où un mot
# ordinaire n'a pas sa place.
N_ = r"""(?:\d{1,3}|[א-ת]{1,3}["״'׳]?[א-ת]?)(?![א-ת])"""
# Le maillon peut porter son siman en tête — « י:ד → ט-יא » : le séif est ce qui
# suit le deux-points.
PFX_ = r"""(?:[\dא-ת]{1,4}["״'׳]?[א-ת]?:)?"""
# La gauche de la fleche est parfois une PLAGE, et elle n'etait pas lue : le siman 10
# ecrit « י:א → ס״ק א-ה; י:ד → ט-יא; י:ה-ו → יב-כג; י:ז → כד-כז; י:ח → כח-ל; י:ט-יב → לא-לז ».
# Un seul maillon non lu ROMPT LA CHAINE, la carte s'arretant au premier trou : la
# porte lisait 8 des 34 maillons du siman, et les 26 autres — verifies exacts a la main
# contre Sefaria — n'etaient confrontes a rien. Une plage a gauche est une promesse plus
# large, et un ס״ק qui tombe sur l'un de ses seifim la tient.
PLG_ = r"""(?:\s*[-‑–]\s*(?P<%s>""" + N_ + r"""))?"""
RX_TETE = re.compile(PFX_ + r"(?P<sf>" + N_ + r")" + (PLG_ % 'sfb') +
                     r"\s*→\s*ס[\"״]ק\s*(?P<a>" + N_ + r")" + (PLG_ % 'b'))
# Ancré en tête de la portion restante : une carte est une CHAÎNE, et dès
# qu'un maillon manque elle s'arrête — sans quoi on rapprocherait deux
# flèches éloignées l'une de l'autre.
RX_MAILLON = re.compile(r"^\s*[,;·]\s*" + PFX_ + r"(?P<sf>" + N_ + r")" + (PLG_ % 'sfb') +
                        r"\s*→\s*(?P<a>" + N_ + r")" + (PLG_ % 'b'))

def cartes_annoncees(segment):
    """(ouvrage, séif, dernier séif, premier ס״ק, dernier ס״ק, offset) par maillon.

    L'ouvrage est le DERNIER nommé AVANT la carte : « … la colonne de la Michna
    Beroura suit les ancres que Sefaria place dans le texte du Mehaber : séif א →
    ס״ק א-ה, ב → ו-ח … ». Compter les noms du bloc ne marche pas — le bloc est un
    paragraphe de méthode qui énumère dix ouvrages —, et il n'y a rien à deviner :
    la carte suit son ouvrage.
    """
    for tete in RX_TETE.finditer(segment):
        avant = [x for x in RX_AUTRE.finditer(segment) if x.end() <= tete.start()]
        if not avant:
            continue
        qui = NOMS[avant[-1].group(0)]
        yield (qui, tete.group('sf'), tete.group('sfb'),
               tete.group('a'), tete.group('b'), tete.start())
        pos = tete.end()
        while True:
            m = RX_MAILLON.match(segment[pos:])
            if not m:
                break
            yield (qui, m.group('sf'), m.group('sfb'),
                   m.group('a'), m.group('b'), pos + m.start())
            pos += m.end()

RX_FIN_BLOC = re.compile(
    r"</(?:div|p|li|td|tr|h[1-6]|blockquote|section)>|<br\s*/?>", re.I)
RX_TAG = re.compile(r"<[^>]+>")

def debaliser(brut):
    """Le texte sans ses balises, ET la carte qui ramène chaque position à sa source.

    Les numéros de ligne du relevé étaient faux, et un relevé dont les lignes sont
    fausses ne sert à rien au Rav : il annonçait siman-193/niveau-2-lamdan.html:700
    quand la citation vit ailleurs. La cause : `re.sub(r'<[^>]+>', ' ', txt)` SUPPRIME
    les retours à la ligne contenus DANS les balises, si bien que compter les sauts de
    ligne du texte débalisé ne compte plus les lignes du FICHIER.

    ⚠️ LA CORRECTION ÉVIDENTE EST UN PIÈGE, ET JE SUIS TOMBÉ DEDANS. Remplacer chaque
    balise par AUTANT D'ESPACES qu'elle occupait aligne bien les offsets — et allonge
    les intervalles du motif, qui sont bornés à 60 et 40 caractères. Un
    `<span class="src-ref">` de quarante caractères devenait quarante espaces au lieu
    d'un seul : au siman 114, l'écart entre « סעיף ה׳ » et « (ט״ז … ס״ק ד) » passait de
    27 à 74 caractères et L'APPARIEMENT DISPARAISSAIT. Quatre rattachements ont ainsi
    cessé d'être confrontés — sans qu'aucun compte ne baisse, les gains de la même
    version masquant la perte. C'est le mutisme que ce dépôt redoute, obtenu en
    voulant réparer un détail d'affichage.

    Donc on ne touche PAS au texte sur lequel on cherche : il est construit exactement
    comme avant, une balise valant un espace et une fin de bloc la frontière « . ».
    Le numéro de ligne vient d'une CARTE tenue à part — une liste de jalons
    (position dans le texte débalisé, position dans le fichier) — que `ligne_de`
    interroge. Les deux besoins sont découplés, et aucun ne dégrade l'autre.
    """
    out, jalons, pos, n = [], [], 0, 0
    for m in RX_TAG.finditer(brut):
        lit = brut[pos:m.start()]
        if lit:
            jalons.append((n, pos, True)); out.append(lit); n += len(lit)
        r = ' . ' if RX_FIN_BLOC.fullmatch(m.group(0)) else ' '
        jalons.append((n, m.start(), False)); out.append(r); n += len(r)
        pos = m.end()
    lit = brut[pos:]
    if lit:
        jalons.append((n, pos, True)); out.append(lit)
    return ''.join(out), jalons

def ligne_de(brut, jalons, i):
    """Le numéro de ligne DANS LE FICHIER de la position `i` du texte débalisé."""
    k = bisect.bisect_right([j[0] for j in jalons], i) - 1
    if k < 0:
        return 1
    dep, src, litteral = jalons[k]
    # Dans une balise remplacée, toute position renvoie au début de la balise : il n'y
    # a pas de caractère du fichier qui corresponde à l'espace qu'on a mis à sa place.
    return brut.count('\n', 0, src + (i - dep if litteral else 0)) + 1

SECTIONS = {'yoreh-deah': "Shulchan_Arukh,_Yoreh_De%27ah",
            'shabbat': "Shulchan_Arukh,_Orach_Chayim",
            'orah-haim': "Shulchan_Arukh,_Orach_Chayim"}

def _cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding='utf-8'))
        except Exception:
            return {}
    return {}

_C = _cache()

# Une ancre de Sefaria, attributs DANS UN ORDRE QUELCONQUE.
#
# Le motif d'origine était `data-commentator="…" data-order="(\d+)"` : il exigeait
# l'ADJACENCE des deux attributs. Mesuré sur Shulchan_Arukh,_Orach_Chayim.246 —
# 90 ancres, il en captait 37 et en ratait 53, soit 59 %. Deux causes :
#   · Sefaria intercale parfois un `data-label` ENTRE les deux (Be'er HaGolah,
#     Ateret Zekenim, Eshel Avraham) ;
#   · et la MICHNA BEROURA ne porte AUCUN `data-order` — seulement un `data-label`
#     qui est le numéro de ס״ק en lettres hébraïques.
# Mesuré sur treize simanim des trois compartiments : 2 632 ancres, 1 519 captées,
# 1 113 ratées, dont les 752 de la Michna Beroura — la totalité de l'ouvrage le plus
# cité du dépôt.
RX_ANCRE = re.compile(r'<i\b[^>]*\bdata-commentator="[^"]*"[^>]*>')
RX_ATTR  = re.compile(r'\b(data-commentator|data-order|data-label)="([^"]*)"')

def lire_ancre(tag):
    """(commentateur, numéro de ס״ק) — numéro None si l'ancre n'est pas confrontable."""
    a = dict(RX_ATTR.findall(tag))
    qui = a.get('data-commentator')
    ordre = a.get('data-order')
    if ordre and ordre.isdigit():
        return qui, int(ordre)
    # Pas de `data-order` : le `data-label` porte le numéro imprimé. C'est la forme
    # de la Michna Beroura, et elle a l'avantage d'échapper au piège de la פתיחה —
    # le label est le numéro TEL QU'IMPRIMÉ, il n'y a donc aucun décalage à mesurer.
    # Vérifié : Mishnah_Berurah.248 sert 37 entrées pour 36 ancres labellisées א…לו,
    # la première entrée étant la פתיחה non numérotée, qui ne porte pas d'ancre ;
    # aux simanim 250 et 251, 6 entrées pour 6 ancres et 9 pour 9.
    return qui, numero_attribut(a.get('data-label'))

# Les simanim que la source n'a PAS rendus, et pourquoi. Sans ce registre, les trois
# chemins d'échec de `carte()` — exception réseau, `he` vide, `ref` qui ne finit pas par
# le siman — rendaient tous `{}, 0, 0, 0`, c'est-à-dire exactement ce que rend un siman
# qui n'a rien à confronter. Éprouvé en coupant `urlopen` avec le cache écarté : la porte
# imprimait « Rattachements confrontés : 0 » et SORTAIT EN 0, sans une ligne pour le dire.
# C'est le défaut que le CLAUDE.md de ce dépôt nomme comme le pire.
NON_ATTEINTS = {}

def carte(section, n):
    """({commentateur: {numéro de ס״ק: séif}}, ancres, non lisibles, nb de séifim).

    Rend aussi ce qui a été LU et ce qui n'était pas lisible : une porte qui jette en
    silence ce qu'elle ne sait pas lire finit par ne plus rien comparer sans le dire.
    """
    cle = f"{section}.{n}"
    if cle in _C:
        d = _C[cle]
        return d['c'], d['ancres'], d['sans'], d['ns']
    url = (f"https://www.sefaria.org/api/texts/{SECTIONS[section]}.{n}"
           "?context=0&pad=0")
    try:
        d = json.loads(subprocess.run(["curl", "-s", url], capture_output=True,
                                      text=True, timeout=60).stdout)
        he = d.get('he') or []
    except Exception as e:
        NON_ATTEINTS[f"{section} {n}"] = f"réseau : {type(e).__name__}"
        return {}, 0, 0, 0
    # Un 503 de Sefaria rend un `he` vide. Le mettre en cache rendrait cette porte
    # verte POUR TOUJOURS sur ce siman, sans qu'aucune ligne ne le dise. On ne met
    # jamais en cache un résultat vide ; on refait l'appel au prochain passage.
    if not he:
        NON_ATTEINTS[f"{section} {n}"] = "source vide (503, ou siman non numérisé)"
        return {}, 0, 0, 0
    # Sefaria rend HTTP 200 ET LE LIVRE ENTIER sur un ref mal forme. Le signe qui ne
    # trompe pas est que le champ `ref` finit par le numero du siman demande ; sinon le
    # `len(he)` qu'on s'apprete a prendre pour un nombre de seifim est un nombre de
    # SIMANIM, et la borne du seif deviendrait une passoire.
    if not re.search(r"\b%d$" % n, str(d.get('ref') or '')):
        NON_ATTEINTS[f"{section} {n}"] = "ref servi ≠ siman demandé (le livre entier)"
        return {}, 0, 0, 0
    ns = len(he)
    c, ancres, sans = {}, 0, 0
    for i, s in enumerate(he, 1):
        t = s if isinstance(s, str) else " ".join(s)
        for tag in RX_ANCRE.findall(t):
            ancres += 1
            qui, num = lire_ancre(tag)
            if not qui or num is None:
                sans += 1          # ancre non confrontable — comptée, pas jetée
                continue
            # première ancre rencontrée = le séif de rattachement
            c.setdefault(qui, {}).setdefault(str(num), i)
    if not c:
        return {}, ancres, sans, ns
    _C[cle] = {'c': c, 'ancres': ancres, 'sans': sans, 'ns': ns}
    return c, ancres, sans, ns

def sauver_cache():
    try:
        json.dump(_C, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception:
        pass

def prechauffer(racines):
    """Remplit le cache en parallele. Le passage v2 → v3 le vide, et 512 simanim
    repris un par un font trois minutes et demie d'attente avant la premiere ligne."""
    from concurrent.futures import ThreadPoolExecutor
    aff = []
    for d in racines:
        mm = re.search(r'siman-(\d+)', d)
        sec = section_de(d)
        if mm and sec and f"{sec}.{int(mm.group(1))}" not in _C:
            aff.append((sec, int(mm.group(1))))
    if not aff:
        return
    print(f"Source : {len(aff)} siman(im) a relire sur Sefaria…", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda a: carte(*a), aff))
    sauver_cache()

def section_de(path):
    for s in SECTIONS:
        if f"/{s}/" in path.replace(os.sep, '/'):
            return s
    return None

# Ou commence le mot « seif » dans un appariement : il faut sa position ABSOLUE pour
# lire le marqueur de siman qui le precede.
RX_SF_TOK = re.compile(r"(?:(?<![A-Za-z])(?i:s[eé][’']?if)|סעיף)")

def examiner(dossier):
    n = int(re.search(r'siman-(\d+)', dossier).group(1))
    sec = section_de(dossier)
    if not sec:
        return [], 0, 0, 0, 0, {}
    c, ancres, sans, ns = carte(sec, n)
    if not c:
        return [], 0, 0, ancres, sans, {}
    justes = inconnus = 0
    ecarts = []
    par_ouvrage = {}
    for p in sorted(glob.glob(os.path.join(dossier, '*.html'))):
        brut = open(p, encoding='utf-8').read()
        vus_f = set()
        # Les balises doivent tomber AVANT la recherche. Yoré Déa écrit le séif dans un
        # <span class="src-ref">[seif N]</span> : lu sur le HTML brut, le motif — qui
        # interdit le chevron pour ne pas enjamber une phrase — ne pouvait jamais
        # apparier. Le contrôle sortait « 0 rattachement confronté » sur tout le
        # compartiment, et ce zéro passait pour un blanc-seing alors qu'il en existe
        # 140 dans le seul siman 234.
        # …mais les retirer toutes laisse le motif ENJAMBER les blocs : au siman 229,
        # « Le Taz ס״ק י״א » d'une carte s'appariait au « Verrou 2 — séif 5 » de la
        # carte suivante, et douze rattachements sur douze paraissaient décalés d'un
        # cran. Les fins de bloc restent donc une frontière, et `debaliser` le fait
        # SANS DEPLACER UN CARACTERE, pour que le numéro de ligne du relevé soit vrai.
        txt, jalons = debaliser(brut)

        # Les cartes d'ancrage annoncées, bloc par bloc. Le bloc doit nommer UN SEUL
        # ouvrage : s'il en nomme deux, rien ne dit auquel la carte se rapporte, et
        # deviner ici serait fabriquer un candidat.
        dep = 0
        for seg in txt.split(' . '):
            base, dep = dep, dep + len(seg) + 3
            if '→' not in seg or 'ס״ק' not in seg:
                continue
            for qui, b_sf, b_sfb, b_a, b_b, off in cartes_annoncees(seg):
                def _v(x):
                    return (int(x) if x.isdigit() else gem(x)) if x else None
                sf, sfb = _v(b_sf), _v(b_sfb)
                a, b = _v(b_a), _v(b_b) or _v(b_a)
                if not (sf and a and b) or b < a or b - a > 40:
                    continue
                # La gauche peut être une PLAGE de séifim ; sinon elle vaut pour elle seule.
                sfb = sfb if (sfb and sfb >= sf and sfb - sf <= 40) else sf
                # Un séif que le siman ne compte pas n'est pas un séif de ce siman.
                if sf > ns:
                    continue
                for sk in range(a, b + 1):
                    cle_c = (qui, sk, sf, sfb, 'carte')
                    if cle_c in vus_f:
                        continue
                    vus_f.add(cle_c)
                    vrai = c.get(qui, {}).get(str(sk))
                    if vrai is None:
                        inconnus += 1
                        continue
                    par_ouvrage[qui] = par_ouvrage.get(qui, 0) + 1
                    if sf <= vrai <= sfb:
                        justes += 1
                    else:
                        ligne = ligne_de(brut, jalons, base + off)
                        dit = str(sf) if sfb == sf else f"{sf}-{sfb}"
                        ecarts.append((p, ligne, qui, str(sk), dit, vrai,
                                       re.sub(r'\s+', ' ', seg)[:120]))
        vus = set()
        for m in list(RX.finditer(txt)) + list(RX_INV.finditer(txt)):
            # Le nom capté doit être le SEUL de l'intervalle : un second nom
            # d'ouvrage entre les deux bouts signale qu'on a changé de citation
            # en chemin, et le séif lu appartient alors à l'autre ouvrage.
            if RX_AUTRE.search(m.group(0).replace(m.group('qui'), ' ', 1)):
                continue
            if OUVRAGES_TIERS.search(m.group(0)):
                continue
            # Ce qui précède immédiatement le séif : dans l'ordre inverse, le séif
            # ouvre le motif, et l'ouvrage auquel il appartient est AVANT lui.
            if m.re is RX_INV and OUVRAGES_TIERS.search(txt[max(0, m.start() - 45):m.start()]):
                continue
            qui = NOMS.get(m.group('qui'))
            sk = numero_prose(m.group('sk'))
            sf = numero_prose(m.group('sf'))
            if not (qui and sk and sf):
                continue
            # Le séif annoncé peut être celui d'un AUTRE SIMAN du même ouvrage.
            o = RX_SF_TOK.search(m.group(0))
            if o and siman_etranger(txt, m.start() + o.start(), n):
                continue
            # Et il peut n'exister nulle part : Sefaria ne sert qu'un séif au siman 193
            # de Yoré Déa, et la page y annonce le 11.
            if sf > ns:
                continue
            # Une plage de séifim — « סעיף ב-ח » — est une promesse plus large, et
            # un ס״ק qui tombe dedans la tient.
            sf2 = numero_prose(m.group('sf2')) if m.group('sf2') else None
            # La SECONDE BORNE d'une plage de ס״ק était captée et jamais lue : `sk2`
            # existait dans le motif et ne paraissait nulle part dans le code. « MB
            # s"k 5-6 » promet DEUX rattachements, et un seul était confronté — au
            # siman 267, Sefaria ancre le ס״ק ה ET le ס״ק ו au séif 2 quand la page
            # annonce le séif 3 : deux promesses fausses, une seule signalée.
            sk2 = numero_prose(m.group('sk2')) if m.group('sk2') else None
            bornes = [sk]
            if sk2 and sk < sk2 <= sk + 40:
                bornes = list(range(sk, sk2 + 1))
            for skc in bornes:
                # Les deux ordres peuvent couvrir le même passage : on ne compte le
                # rattachement qu'une fois, sans quoi le nombre de confrontations est
                # gonflé — et un compte gonflé est le contraire de ce qu'on veut ici.
                cle_m = (qui, skc, sf, sf2)
                if cle_m in vus:
                    continue
                vus.add(cle_m)
                vrai = c.get(qui, {}).get(str(skc))
                if vrai is None:
                    inconnus += 1
                    continue
                par_ouvrage[qui] = par_ouvrage.get(qui, 0) + 1
                if vrai == sf or (sf2 and sf <= vrai <= sf2):
                    justes += 1
                else:
                    ligne = ligne_de(brut, jalons, m.start())
                    # Le ס״ק est rendu COMME LA PAGE L'ECRIT — « ס״ק כ״ז », non « ס״ק 27 » :
                    # le Rav doit retrouver la chaine dans son fichier. Seule une borne
                    # INTERMEDIAIRE de plage, que la page n'ecrit pas, sort en chiffres.
                    dit_sk = (m.group('sk') if skc == sk else
                              m.group('sk2') if sk2 and skc == sk2 else str(skc))
                    ecarts.append((p, ligne, m.group('qui'), dit_sk, sf, vrai,
                                   re.sub(r'\s+', ' ', m.group(0))[:120]))
    return ecarts, justes, inconnus, ancres, sans, par_ouvrage

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--path' in sys.argv:
        cible = sys.argv[sys.argv.index('--path') + 1]
        racines = ([cible] if os.path.basename(cible).startswith('siman-')
                   else sorted(glob.glob(os.path.join(cible, 'siman-*'))))
    elif args:
        # Un numéro nu se résout dans TOUS les compartiments. Dans sa forme d'origine
        # ce script ne cherchait que Yoré Déa : sur un siman de Chabbat ou d'Orah Haïm
        # il n'examinait rien et sortait vert, ce que CLAUDE.md tient pour pire qu'une
        # porte absente. Même correctif que verifier-fabrications.py et fix-lamdan-ltr.py.
        COMPARTIMENTS = ('yoreh-deah', 'shabbat', 'orah-haim', 'nida')
        racines, manquants = [], []
        for a in args:
            trouve = [os.path.join(ROOT, 'sources', c, f'siman-{a}') for c in COMPARTIMENTS
                      if os.path.isdir(os.path.join(ROOT, 'sources', c, f'siman-{a}'))]
            if not trouve:
                manquants.append(a)
            racines.extend(trouve)
        if manquants:
            print(f"Siman(im) introuvable(s) dans sources/ : {', '.join(manquants)}")
            return 2
    else:
        racines = sorted(glob.glob(os.path.join(ROOT, 'sources', '*', 'siman-*')))

    racines = [d for d in racines if os.path.isdir(d)]
    prechauffer(racines)
    tj = ti = 0
    ancres = sans = 0
    par_ouvrage = {}
    tous = []
    lignes = []
    for d in racines:
        if not os.path.isdir(d):
            continue
        ecarts, j, i, an, sa, po = examiner(d)
        tj += j; ti += i; ancres += an; sans += sa
        for k, v in po.items():
            par_ouvrage[k] = par_ouvrage.get(k, 0) + v
        tous.extend(ecarts)
        for e in ecarts:
            lignes.append(
                f"ÉCART  {os.path.relpath(e[0], ROOT)}:{e[1]} — {e[2]} ס״ק {e[3]} : "
                f"la page dit séif {e[4]}, l'ancre Sefaria le pose au séif {e[5]}")
    sauver_cache()
    for l in lignes:
        print(l)

    # Une porte qui ne compare rien et sort verte est pire qu'une porte absente : ces
    # trois comptes sont là pour qu'on puisse le voir. « ancres lues » dit ce que la
    # source offrait, « non confrontables » ce qu'on n'a pas su en lire, et
    # « rattachements confrontés » ce qui a réellement été comparé.
    resume = []
    resume.append(f"Ancres lues dans la source  : {ancres}")
    resume.append(f"  dont non confrontables    : {sans}  (label non numérique)")
    resume.append(f"Rattachements confrontés    : {tj + len(tous)}")
    resume.append(f"  conformes                 : {tj}")
    resume.append(f"  écarts (candidats)        : {len(tous)}")
    resume.append(f"  ס״ק hors carte            : {ti}")
    if par_ouvrage:
        resume.append("  par ouvrage               : " + ", ".join(
            f"{k} {v}" for k, v in sorted(par_ouvrage.items(), key=lambda x: -x[1])))
    # LE VERT N'EST PAS GRATUIT. Un siman que la source n'a pas rendu n'est pas un siman
    # sans rattachement : il est NON MESURÉ, et les deux se lisaient jusqu'ici « 0 ».
    if NON_ATTEINTS:
        resume.append(f"Simanim NON ATTEINTS        : {len(NON_ATTEINTS)}"
                      "  (rien n'y a été confronté)")
        for cle, pourquoi in sorted(NON_ATTEINTS.items())[:12]:
            resume.append(f"    ⚠ {cle} — {pourquoi}")
        if len(NON_ATTEINTS) > 12:
            resume.append(f"    … et {len(NON_ATTEINTS) - 12} autres")
    print()
    for l in resume:
        print(l)
    print()
    print("Un écart n'est pas une faute : une page peut citer le ס״ק d'un autre séif")
    print("quand il éclaire le sien. Ce qui se lit ici, c'est l'écart ISOLÉ — à ouvrir —")
    print("et l'écart SYSTÉMATIQUE, tout un siman décalé, qui est le piège 22-bis.")

    if '--ecrire' in sys.argv:
        dest = os.path.join(ROOT, 'audit', 'ancrage-candidats.txt')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write("\n".join(lignes) + "\n\n" + "\n".join(resume) + "\n")
        print(f"\n→ {os.path.relpath(dest, ROOT)}")

    # Une porte qui ne compare rien et sort verte est pire qu'une porte absente. Quand
    # AUCUN rattachement n'a été confronté alors que des simanim n'ont pas été atteints,
    # il n'y a pas de verdict à rendre — ni vert ni rouge — et le code de sortie doit le
    # dire, parce qu'un gate est lu par son code de sortie avant de l'être par son texte.
    # Un écart, lui, ne fait JAMAIS sortir en 1 : cette porte rend des candidats.
    if (tj + len(tous)) == 0 and NON_ATTEINTS:
        print()
        print(f"✗✗ MESURE NON FAITE : aucun rattachement confronté, et {len(NON_ATTEINTS)} "
              "siman(im) n'ont pas été atteints.")
        print("Aucun verdict n'est rendu ici. Vérifier l'accès à Sefaria, puis relancer.")
        return 3
    return 0

if __name__ == '__main__':
    sys.exit(main())
