#!/usr/bin/env python3
"""L'étiquette d'une cellule de niveau 4 nomme-t-elle un séif qui porte ce qu'elle annonce ?

D'OÙ ELLE VIENT. Les tableaux comparatifs du niveau 4 rangent la source par colonne
— Mehaber, Rama, Michna Beroura — et posent au-dessus de chaque cellule une étiquette :
« OH 243:2 », « Hagaha sur OH 243:2 », « MB 242:3-4 ». Le contenu de la cellule est le
plus souvent une CONDENSATION, introduite par `<em>résumé</em> :`, que la convention du
dépôt exempte à bon droit de la porte du verbatim — une condensation n'est pas une
citation. Mais l'exemption laisse deux trous que rien ne surveillait :

  · une condensation peut être FAUSSE (le siman 247 en porte une qui inverse le psak :
    elle attache la condition du בי דואר au cas où l'on a fixé un prix, alors que le
    Mehaber ne l'ouvre qu'« ואם לא קצב ») ;
  · et l'ÉTIQUETTE elle-même peut mentir — au siman 243, une cellule annonce
    « Hagaha sur OH 243:2 » alors que le Rama n'a AUCUNE glose sur ce séif ; au 249,
    « OH 249:2-3 » pour un psak que le séif ב ne dit pas et que le séif ג contredit.

La première question ne se tranche pas mécaniquement, et cette porte ne la pose pas.
LA SECONDE, SI. Le séif annoncé existe-t-il ? Porte-t-il une glose du Rama quand la
cellule en promet une ? Le ס״ק annoncé existe-t-il dans la Michna Beroura de ce siman ?
Trois questions fermées, vérifiables, et qui ont déjà trouvé des défauts à la main.

Elle rend des ANOMALIES là où la réponse est non, et des CANDIDATS là où l'étiquette
nomme un siman autre que celui de la page — ce qui est licite mais rare, et mérite l'œil.

Usage :
  python3 scripts/verifier-etiquettes.py --section shabbat [--bref]
  python3 scripts/verifier-etiquettes.py 243 245 249
  python3 scripts/verifier-etiquettes.py --path sources/yoreh-deah/siman-202
Un numéro nu n'est accepté que s'il ne désigne qu'un seul compartiment ; les simanim
125, 128, 129 ou 202 existent en Orah Haïm ET en Yoré Déa, et il faut alors --path.
"""
import re, sys, os, io, json, glob, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache-etiquettes.json")

RXTD = re.compile(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', re.S | re.I)

# ⚠️ CE QUE LA PREMIÈRE VERSION NE LISAIT PAS, ET POURQUOI SON VERT MENTAIT.
# Elle n'acceptait que des chiffres ARABES. Or les tableaux des fichiers HÉBREUX écrivent
# leurs adresses en numération hébraïque — « או״ח רמ״ז:א », « מ״ב רמ״ט ס״ק יד » — et les
# fichiers français et anglais emploient aussi la forme MIXTE « MB 248 ס״ק ד ». Aucune n'a
# jamais été confrontée. Trois agents de contrôle l'ont établi indépendamment ; au siman 264,
# QUATRE des cinq adresses fausses réelles étaient hors de portée. Le premier chiffre publié —
# « 26 anomalies sur 7 simanim » — était donc un PLANCHER annoncé comme un compte.
# Et la colonne du Choulhan Aroukh HaRav n'était pas lue du tout, alors que c'est elle qui
# portait, au siman 249, une adresse (« רמ״ט:6-8 ») renvoyant à un sujet absent du siman.
# ⚠️ DEUX GARDE-FOUS CONTRE MA PROPRE MESURE, ET ILS ONT COÛTÉ UN FAUX BALAYAGE.
# Premier élargissement de cette porte : 49 « anomalies », dont 35 IMAGINAIRES, toutes de la
# même forme — « או״ח רמ״ב:א — אין » lu comme « siman 242, séif 1 À 61 ». Car le tiret de PROSE
# était pris pour un tiret de PLAGE, et le mot qui suit pour un nombre : en hébreu, tout mot
# court devient un nombre si on le lit en guématrie (אין = 61, כלל = 80, דן = 54). C'est
# exactement le piège que CLAUDE.md consigne pour verifier-denombrements.py, et j'y suis tombé
# le même jour. Deux règles, et il faut les deux :
#   · LE TIRET DE PLAGE N'A PAS D'ESPACES. Le dépôt écrit « נג-נד », « 3-4 », « 23–30 » ;
#     la prose écrit « — » entouré d'espaces. C'est le discriminant, et il est net.
#   · UN NUMÉRAL HÉBRAÏQUE FAIT UNE OU DEUX LETTRES, ou porte un gershayim au-delà.
#     « אין », « כלל », « המחב » n'en sont pas. heb-nums.py impose déjà cette convention.
# ⚠️ L'ORDRE DES ALTERNATIVES COMPTE, et il a coûté un faux chiffre. La forme au
# gershayim doit venir AVANT celle à une ou deux lettres : sur « ס״ק ע״א », rien ne suit
# le nombre, donc rien n'oblige le moteur à revenir en arrière — il prenait ע seul (70) au
# lieu de ע״א (71). La faute ne se voyait PAS sur « או״ח רמ״ב:א », où le deux-points
# qui suit force le backtracking et rattrape l'erreur : un motif peut être juste par accident
# dans un contexte et faux dans l'autre.
NB = (r'(?:\d{1,3}'
      r'|[\u05D0-\u05EA]+["\u05F4][\u05D0-\u05EA](?![\u05D0-\u05EA])'
      r'|[\u05D0-\u05EA]{1,2}(?![\u05D0-\u05EA]))')
TIRET = r'(?:[-\u2013])'
OH = r'(?:OH|OC|או["\u05F4]?ח|אורח חיים)'

RX_HAGAHA = re.compile(r'(?:Hagahah?|Gloss|הגהה|הגה(?![\u05D0-\u05EA]))\s*(?:sur|on|על)?\s*'
                       rf'{OH}\s*({NB})\s*[:\u05C3]\s*({NB})(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?', re.I)
RX_SEIF   = re.compile(rf'(?<![\w:\u05D0-\u05EA]){OH}\s*({NB})\s*[:\u05C3]\s*({NB})'
                       rf'(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?', re.I)
# « MB 242:3-4 », « מ״ב רמ״ט:יד », « MB 248 ס״ק ד », « משנ״ב רס״ד ס״ק כג »
MBW = r'(?:MB|מ["\u05F4]ב|משנ["\u05F4]ב|משנה ברורה)'
RX_MB     = re.compile(rf'(?<![\w:\u05D0-\u05EA]){MBW}\s*({NB})\s*'
                       rf'(?:[:\u05C3]|ס["\u05F4]?ק|סעיף\s*קטן)\s*({NB})(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?')
# La colonne du Choulhan Aroukh HaRav : « שו״ע הרב רמ״ט:יב », « רמ״ט:6-8 » dans sa cellule.
RAVW = r'(?:שו["\u05F4]ע הרב|שוע["\u05F4]ר|אדמו["\u05F4]ר הזקן|ש["\u05F4]ע אדה["\u05F4]ז|SA HaRav)'

# ⚠️ YORÉ DÉA N'EST PAS ORAH HAÏM, et la porte ne savait pas le dire. Elle résolvait TOUT
# « או״ח N » comme Shulchan_Arukh,_Orach_Chayim.N — ce qui est juste dans deux compartiments
# sur trois, et faux dans le troisième : une étiquette « יו״ד קכ״ח:ג » d'une page de Yoré Déa
# aurait été confrontée au siman 128 d'Orah Haïm, qui parle de la bénédiction des Cohanim.
# Et la Michna Beroura NE COUVRE PAS Yoré Déa : ses nossei kelim sont le Chakh et le Taz.
# Le compartiment se lit dans le CHEMIN du fichier ; une étiquette qui nomme l'autre tractat
# est un renvoi licite, et sort en candidat.
YD = r'(?:YD|יו["\u05F4]?ד|יורה דעה)'
RX_SEIF_YD = re.compile(rf'(?<![\w:\u05D0-\u05EA]){YD}\s*({NB})\s*[:\u05C3]\s*({NB})'
                        rf'(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?', re.I)
RX_HAGAHA_YD = re.compile(r'(?:Hagahah?|Gloss|הגהה|הגה(?![\u05D0-\u05EA]))\s*(?:sur|on|על)?\s*'
                          rf'{YD}\s*({NB})\s*[:\u05C3]\s*({NB})(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?', re.I)
# Le Chakh et le Taz, seifim ketanim, avec ou sans deux-points.
SHKW = r'(?:ש["\u05F4]ך|שפתי כהן|Shach)'
TAZW = r'(?:ט["\u05F4]ז|טורי זהב|Taz)'
# La forme réelle du dépôt intercale le tractat : « ש״ך יו״ד קכ״ד ס״ק ע״א ». Il est donc
# optionnel entre le sigle et le numéro de siman — sans lui, « ט״ז ק״ה ס״ק ג » se lit aussi.
RX_SHK = re.compile(rf'(?<![\w:\u05D0-\u05EA]){SHKW}\s*(?:{YD}\s*)?({NB})\s*'
                    rf'(?:[:\u05C3]|ס["\u05F4]?ק|סעיף\s*קטן)\s*({NB})(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?')
RX_TAZ = re.compile(rf'(?<![\w:\u05D0-\u05EA]){TAZW}\s*(?:{YD}\s*)?({NB})\s*'
                    rf'(?:[:\u05C3]|ס["\u05F4]?ק|סעיף\s*קטן)\s*({NB})(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?')
RX_RAV    = re.compile(rf'{RAVW}\s*(?:{OH}\s*)?({NB})\s*[:\u05C3]\s*({NB})(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?')

# ⚠️ UN NOM DE TRACTAT PRÉCÉDÉ D'UN NOM D'ŒUVRE NE DÉSIGNE PAS LE CHOUL'HAN AROUKH.
# C'est le piège consigné plus bas pour « או״ח » dans un recueil de responsa — et il ne se
# limite pas aux responsa : il se retrouve sur un CODE. L'AROUKH HACHOUL'HAN A SON PROPRE
# DÉCOUPAGE EN SÉIFIM, bien plus fin que celui du Choul'han Aroukh : « ערוך השולחן יורה דעה
# ר״ב:י״ב » est SON séif 12, quand le siman 202 de Yoré Déa n'en a que neuf, et son siman 201
# en compte 218 contre 75. La porte lisait « יורה דעה ר״ב:י״ב » dans cette étiquette, laissait
# tomber le nom de l'œuvre, et accusait la page de nommer un séif inexistant. SIX ANOMALIES
# IMAGINAIRES sur le siman 202 de Yoré Déa, dans les trois langues, sur six citations dont
# chacune est verbatim dans le séif qu'elle annonce (vérifié par squelette consonantique).
# Le siman 201 y échappait PAR CHANCE : son étiquette la plus haute est ר״א:ע״ה, soit 75, et
# le siman 201 du Choul'han Aroukh a précisément 75 séifim. Un motif peut être juste par
# accident dans un contexte et faux dans l'autre — c'est déjà la leçon du gershayim ci-dessus.
# On ne se contente donc pas de TAIRE l'étiquette comme pour les recueils : on la confronte à
# l'Aroukh HaChoul'han lui-même, qui est sur Sefaria et dont le tractat se lit DANS l'étiquette
# (l'œuvre couvre les quatre Tourim ; le chemin du fichier ne le dit pas).
# ⚠️ Et quand Sefaria rend `he: []` — Yoré Déa 123-182 et à partir de 203 — c'est une lacune
# de NUMÉRISATION et non de l'œuvre (règle 21 du brief) : on passe, on n'accuse pas.
AHSW = r'(?:ערוך השולחן|ערוה["\u05F4]ש|Arukh HaShulchan|Aroukh HaChoul[\'\u2019]han)'
RX_AHS = re.compile(rf'{AHSW}\s*(?:{OH}|{YD})\s*({NB})\s*[:\u05C3]\s*({NB})'
                    rf'(?:{TIRET}({NB})(?:\s*[:\u05C3]\s*({NB}))?)?', re.I)

GEM = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'כ':20,'ך':20,'ל':30,
       'מ':40,'ם':40,'נ':50,'ן':50,'ס':60,'ע':70,'פ':80,'ף':80,'צ':90,'ץ':90,'ק':100,
       'ר':200,'ש':300,'ת':400}
def _num(t):
    """Un numéro d'étiquette, arabe ou hébraïque. None si ce n'est ni l'un ni l'autre."""
    t = (t or '').strip()
    if re.fullmatch(r'\d{1,3}', t): return int(t)
    lettres = re.sub(r'[^\u05D0-\u05EA]', '', t)
    if not lettres: return None
    v = sum(GEM.get(c, 0) for c in lettres)
    return v or None

# ⚠️ LE CACHE EST VERSIONNÉ DEPUIS QU'IL A CHANGÉ DE CONTENU. La v1 stockait le texte
# tag pour tag effacé ; la v2 conserve les bornes de <small>, sans lesquelles les gloses
# du Rama en parenthèses sont indétectables (voir porte_glose_rama). Un cache v1 relu par
# la v2 rendrait un vert parfaitement faux, et silencieux.
CACHE_V = 2
_cache = {}
if os.path.exists(CACHE):
    try: _cache = json.load(open(CACHE, encoding='utf-8'))
    except Exception: _cache = {}
if _cache.get('__v') != CACHE_V:
    _cache = {'__v': CACHE_V}

PETIT_DEB, PETIT_FIN = '\u0001', '\u0002'

def _plat(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return ' '.join(_plat(y) for y in x)
    return ''

def _sans_balises(b):
    """Le texte d'un segment, les bornes de <small> remplacées par deux sentinelles.

    Sefaria imprime en petit corps tout ce que l'édition imprime en caractères Rachi :
    les gloses du Rama, et les notes explicatives du typographe. Effacer la balise
    confond les deux avec le Mehaber."""
    t = _plat(b)
    t = re.sub(r'<small>', PETIT_DEB, t, flags=re.I)
    t = re.sub(r'</small>', PETIT_FIN, t, flags=re.I)
    return re.sub(r'<[^>]+>', ' ', t)

def _get(slug, cle):
    """Les segments d'une œuvre, avec contrôle du champ ref — le piège du dépôt.

    ⚠️ UN RÉSULTAT VIDE N'EST PLUS MIS EN CACHE, et le défaut méritait d'être nommé : il
    rendait la porte SILENCIEUSEMENT VERTE POUR TOUJOURS. Un 503 de Sefaria, une coupure
    réseau, un slug momentanément absent inscrivaient `[]` dans le cache persisté ; la
    branche de contrôle fait `if not segs: continue`, donc l'œuvre entière cessait d'être
    confrontée — sans un mot, et à chaque relance suivante. C'est la forme la plus grave
    du défaut que ce dépôt traque : une porte qui ne compare rien et sort verte. Signalé
    par un agent de contrôle du siman 202 ; le cache courant n'en portait aucune, mais
    c'était la chance et non la conception.
    """
    if cle in _cache: return _cache[cle]
    out = []
    try:
        with urllib.request.urlopen(
                f'https://www.sefaria.org/api/texts/{slug}?context=0&pad=0', timeout=30) as r:
            d = json.load(r)
        ref = str(d.get('ref', ''))
        n = cle.split(':')[-1]
        if ref.rstrip().endswith(n):          # sinon : l'œuvre entière sans dire non
            he = d.get('he')
            out = [_sans_balises(b) for b in (he if isinstance(he, list) else [he])]
    except Exception:
        pass
    if out:                      # jamais de vide persisté : voir le docstring
        _cache[cle] = out
        try: json.dump(_cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
        except Exception: pass
    time.sleep(0.1)
    return out

# ⚠️ « LE RAMA N'A AUCUNE GLOSE SUR CE SÉIF » A ÉTÉ DIT DE TROIS SÉIFIM QUI EN PORTENT UNE.
# La porte cherchait le mot הגה dans le texte du séif, et rien d'autre. Or Sefaria ne l'écrit
# que lorsque la glose ouvre un bloc à la fin du séif ; la glose INSÉRÉE au fil du texte est
# rendue en petit corps entre parenthèses (Yoré Déa) ou entre crochets (Orah Haïm), sans
# aucun mot d'introduction — seule la source suit, entre parenthèses à son tour.
# Mesuré sur Yoré Déa 129:17 : la cellule annonce « הגה יו״ד קכ״ט:י״ז », le séif ne porte pas
# le mot הגה, et la porte criait. La glose y est pourtant, et deux nossei kelim la nomment :
#   Taz ס״ק כ״ו, sur ce lemme même — « ודוקא שהיא סתומה בפקק. זה למד רמ״א ממ״ש הר״ן… » ;
#   Baer Hetev ס״ק כ״ז — « כתב הט״ז מ״ש רמ״א דאם נסתם בפקק… ».
# Même cause aux séifim 125:1 et 128:1 de Yoré Déa : douze des dix-huit anomalies du
# compartiment étaient cette seule lacune. Relevé sur les 148 simanim de Yoré Déa servis par
# Sefaria : 454 blocs en petit corps ouverts par הגה, 469 ouverts par une parenthèse,
# 80 notes explicatives et 8 restes — la forme sans הגה est donc la MAJORITAIRE.
#
# Ce qui n'est PAS une glose du Rama, et qu'il faut écarter sous peine de rendre la porte
# muette pour de bon :
#   · la note du typographe, « (פירוש סתימה) », « [פירוש אריס הוא העובד…] », « (פי׳ בגדים גסים) » ;
#   · la note d'éditeur ou de censure, « [*עניני קהל וחרם בטלין כעת מדינא דמלכותא] ».
# ⚠️ ET CETTE PORTE NE S'ÉLARGIT QUE DANS UN SENS : elle accepte désormais plus d'étiquettes
# qu'avant. Ce qu'elle ne vérifie toujours pas — et c'est à écrire, pas à taire — c'est que le
# CONTENU de la cellule vienne bien de la zone du Rama et non du Mehaber du même séif.
RX_PETIT   = re.compile(PETIT_DEB + r'(.*?)(?:' + PETIT_FIN + r'|$)', re.S)
RX_EXPLIC  = re.compile(r"^[\(\[]?\s*(?:פירוש|פי[\u05F3'\u2019])")
RX_EDITEUR = re.compile(r"^[\(\[]\s*\*")

def porte_glose_rama(seg):
    """Le Rama a-t-il une glose sur ce séif ? Deux formes, et la seconde est la plus fréquente."""
    for m in RX_PETIT.finditer(seg):
        t = m.group(1).strip()
        if not t: continue
        if t.startswith('הגה'): return True
        if RX_EXPLIC.match(t) or RX_EDITEUR.match(t): continue
        return True
    return 'הגה' in seg          # filet, si Sefaria cessait d'employer <small>

def seifim(n):   return _get(f'Shulchan_Arukh,_Orach_Chayim.{n}', f'sa:{n}')
def seifim_yd(n):return _get(f"Shulchan_Arukh,_Yoreh_De'ah.{n}", f'yd:{n}')
def mb(n):       return _get(f'Mishnah_Berurah.{n}', f'mb:{n}')
def shk(n):      return _get(f"Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De'ah.{n}", f'shk:{n}')
def taz_yd(n):   return _get(f"Turei_Zahav_on_Shulchan_Arukh,_Yoreh_De'ah.{n}", f'tazyd:{n}')

def mb_decale(n):
    """Dans Mishnah_Berurah.N la première entrée est PARFOIS la פתיחה non numérotée.
    On ne le devine pas : on regarde si la première entrée porte un marqueur (א)."""
    s = mb(n)
    if not s: return None
    return 0 if re.search(r'\(\s*א\s*\)', s[0]) else 1

# ⚠️ « או״ח » NE DÉSIGNE PAS TOUJOURS LE CHOUL'HAN AROUKH. Dans un recueil de responsa il
# nomme une PARTIE : « אגרות משה או״ח ד:נג-נד » est le quatrième volume des Iggerot Moshe,
# responsa 53-54, et non le siman 4 du Choul'han Aroukh — qui n'a que 23 séifim. C'était la
# dernière anomalie du balayage, et c'était une fausse. Une étiquette précédée du nom d'un
# recueil de teshouvot n'est donc pas confrontée au Choul'han Aroukh.
RECUEILS = re.compile(r'אגרות משה|אג["״]מ|מהרש["״]ם|שו["״]ת|יביע אומר|'
                      r'מנחת שלמה|ציץ אליעזר|חתם סופר|חת["״]ס|אור לציון|'
                      r'שבט הלוי|משנה הלכות|Iggerot|Igrot')

def _dans_un_recueil(cell, deb):
    """Le nom d'un recueil de responsa precede-t-il l'etiquette de pres ?"""
    return bool(RECUEILS.search(cell[max(0, deb - 60):deb]))


def examiner(path, siman_page, anomalies, candidats, compte):
    s = io.open(path, encoding='utf-8').read()
    nom = os.path.basename(path)
    for cell in RXTD.findall(s):
        vus = set()
        # ⚠️ L'ÉTENDUE, ET NON LA PROXIMITÉ. « ערוך השולחן יורה דעה ר״ב:י״ב » CONTIENT
        # « יורה דעה ר״ב:י״ב » : c'est ce chevauchement-là, et lui seul, qu'il faut taire.
        # Le regard-en-arrière de 40 caractères employé pour les autres sigles taisait en
        # prime toute étiquette du Choul'han Aroukh VOISINE d'une étiquette de l'Aroukh
        # HaChoul'han dans la même cellule — mesuré : « שו״ע יו״ד ר״ב:כ » (le siman 202 de
        # Yoré Déa n'a que 9 séifim) est accusé quand il est seul, et MUET dès qu'une
        # étiquette de l'Aroukh HaChoul'han le précède de moins de 40 signes. Aucune page
        # du dépôt n'était dans ce cas — le trou était latent, et c'est la seule raison
        # pour laquelle il n'a rien coûté. Un garde-fou qu'on n'élargit que dans un sens
        # devient muet sans qu'on s'en aperçoive (leçon de verifier-troncatures.py).
        etendues_ahs = [(a.start(), a.end()) for a in RX_AHS.finditer(cell)]
        for rx, genre in ((RX_HAGAHA, 'hagaha'), (RX_HAGAHA_YD, 'hagaha_yd'),
                          (RX_MB, 'mb'), (RX_SHK, 'shk'), (RX_TAZ, 'taz'),
                          (RX_RAV, 'rav'), (RX_AHS, 'ahs'),
                          (RX_SEIF, 'seif'), (RX_SEIF_YD, 'seif_yd')):
            for m in rx.finditer(cell):
                if (m.start(), m.end()) in vus: continue
                # une étiquette de hagaha contient « OH n:m » : ne pas la compter deux fois
                if genre in ('seif', 'seif_yd'):
                    avant = cell[max(0, m.start() - 40):m.end()]
                    if (RX_HAGAHA.search(avant) or RX_HAGAHA_YD.search(avant)
                            or RX_RAV.search(avant) or RX_MB.search(avant)
                            or RX_SHK.search(avant) or RX_TAZ.search(avant)):
                        continue
                    if any(d <= m.start() and m.end() <= f for d, f in etendues_ahs):
                        continue
                if genre in ('seif', 'seif_yd', 'hagaha', 'hagaha_yd') \
                        and _dans_un_recueil(cell, m.start()):
                    continue
                vus.add((m.start(), m.end()))
                n = _num(m.group(1)); a = _num(m.group(2))
                # ⚠️ UNE PLAGE PEUT RÉPÉTER LE SIMAN : « יו״ד ק״ס:ד–ק״ס:י״ב » va du séif 4 au
                # séif 12 du siman 160, et non « du séif 4 au séif 160 ». La porte lisait la
                # seconde chose et rendait une anomalie imaginaire sur le siman 160 de Yoré
                # Déa, qui a bien 23 séifim. Quand la borne haute porte elle-même un
                # deux-points, c'est sa SECONDE moitié qui est le séif.
                b = _num(m.group(4)) if (m.lastindex or 0) >= 4 and m.group(4) else None
                b = b or _num(m.group(3)) or a
                if n is None or a is None: continue
                compte[genre] += 1
                if n != siman_page:
                    candidats.append(f"{nom} · « {m.group(0).strip()} » nomme le siman {n}, "
                                     f"la page est le siman {siman_page}")
                if genre in ('shk', 'taz'):
                    quoi = shk(n) if genre == 'shk' else taz_yd(n)
                    nom_o = 'Chakh' if genre == 'shk' else 'Taz'
                    if not quoi: continue
                    if b > len(quoi):
                        anomalies.append(f"{nom} · « {m.group(0).strip()} » — le {nom_o} du "
                                         f"siman {n} de Yoré Déa n'a que {len(quoi)} ס״ק")
                    continue
                if genre == 'rav':
                    segs = _get(f'Shulchan_Arukh_HaRav,_Orach_Chayim.{n}', f'rav:{n}')
                    if not segs: continue
                    if b > len(segs):
                        anomalies.append(f"{nom} · « {m.group(0).strip()} » — le Choul'han "
                                         f"Aroukh HaRav du siman {n} n'a que {len(segs)} séif(im)")
                    continue
                if genre == 'ahs':
                    yd = bool(re.search(YD, m.group(0)))
                    slug = (f"Arukh_HaShulchan,_Yoreh_De'ah.{n}" if yd
                            else f'Arukh_HaShulchan,_Orach_Chayim.{n}')
                    segs = _get(slug, f"ahs{'yd' if yd else 'oh'}:{n}")
                    # he: [] = lacune de numérisation Sefaria, jamais une absence d'œuvre
                    if not segs: continue
                    if b > len(segs):
                        anomalies.append(f"{nom} · « {m.group(0).strip()} » — l'Aroukh "
                                         f"HaChoul'han du siman {n} n'a que {len(segs)} séif(im)")
                    continue
                if genre == 'mb':
                    entrees = mb(n)
                    if not entrees: continue
                    d = mb_decale(n)
                    haut = len(entrees) - d
                    if b > haut:
                        anomalies.append(f"{nom} · « {m.group(0).strip()} » — la Michna Beroura "
                                         f"du siman {n} n'a que {haut} ס״ק")
                    continue
                segs = seifim_yd(n) if genre.endswith('_yd') else seifim(n)
                tract = 'Yoré Déa' if genre.endswith('_yd') else 'Orah Haïm'
                if not segs: continue
                if b > len(segs):
                    anomalies.append(f"{nom} · « {m.group(0).strip()} » — le siman {n} de "
                                     f"{tract} n'a que {len(segs)} séif(im)")
                    continue
                if genre in ('hagaha', 'hagaha_yd'):
                    sans = [k for k in range(a, b + 1) if not porte_glose_rama(segs[k - 1])]
                    if sans:
                        anomalies.append(
                            f"{nom} · « {m.group(0).strip()} » — le Rama n'a AUCUNE glose sur "
                            f"le séif {', '.join(map(str, sans))} du siman {n} de {tract}")

def main():
    argv = sys.argv[1:]
    bref = '--bref' in argv
    # ⚠️ DEUX DÉFAUTS DE LIGNE DE COMMANDE, ET LE SECOND RENDAIT UN VERT MENSONGER.
    # (1) --path n'était pas géré du tout, alors que toutes les autres portes du dépôt
    #     l'acceptent : la commande était silencieusement ignorée, dirs restait vide, et le
    #     script imprimait son mode d'emploi. J'ai cru mesurer onze simanim ainsi.
    # (2) UN NUMÉRO NU SE RÉSOLVAIT AU PREMIER COMPARTIMENT QUI LE PORTE. Les simanim 125,
    #     128, 129 et 202 existent en Orah Haïm ET en Yoré Déa : « verifier-etiquettes.py 202 »
    #     confrontait donc Orah Haïm 202 en croyant lire Yoré Déa 202, et sortait vert. Un
    #     numéro ambigu est désormais REFUSÉ, avec les chemins possibles nommés.
    if '--section' in argv:
        sec = argv[argv.index('--section') + 1]
        dirs = sorted(glob.glob(os.path.join(ROOT, 'sources', sec, 'siman-*')))
    elif '--path' in argv:
        cible = os.path.join(ROOT, argv[argv.index('--path') + 1])
        dirs = ([cible] if re.search(r'siman-\d+$', cible)
                else sorted(glob.glob(os.path.join(cible, 'siman-*'))))
        dirs = [d for d in dirs if os.path.isdir(d)]
    else:
        nums = [a for a in argv if a.isdigit()]
        dirs = []
        for n in nums:
            trouves = [os.path.join(ROOT, 'sources', s, f'siman-{n}')
                       for s in ('shabbat', 'orah-haim', 'yoreh-deah')
                       if os.path.isdir(os.path.join(ROOT, 'sources', s, f'siman-{n}'))]
            if len(trouves) > 1:
                print(f"✗ le siman {n} existe dans plusieurs compartiments — précisez :")
                for d in trouves:
                    print(f"    --path {os.path.relpath(d, ROOT)}")
                return 2
            dirs += trouves
    if not dirs:
        print(__doc__.strip().split('Usage :')[-1]); return 2

    anomalies, candidats = [], []
    compte = {'hagaha': 0, 'hagaha_yd': 0, 'seif': 0, 'seif_yd': 0,
              'mb': 0, 'shk': 0, 'taz': 0, 'rav': 0, 'ahs': 0}
    for d in dirs:
        m = re.search(r'siman-(\d+)$', d)
        if not m: continue
        n = int(m.group(1))
        for p in sorted(glob.glob(os.path.join(d, 'niveau-4-*.html'))):
            examiner(p, n, anomalies, candidats, compte)

    for a in anomalies: print(f'✗ {a}')
    if not bref:
        for c in candidats: print(f'?  {c}')
    print(f"\nÉtiquettes confrontées : {compte['seif']} séif d'Orah Haïm · "
          f"{compte['seif_yd']} séif de Yoré Déa · "
          f"{compte['hagaha'] + compte['hagaha_yd']} hagaha · "
          f"{compte['mb']} ס״ק de Michna Beroura · {compte['shk']} du Chakh · "
          f"{compte['taz']} du Taz · {compte['rav']} séif du Choul'han Aroukh HaRav · "
          f"{compte['ahs']} séif de l'Aroukh HaChoul'han")
    print(f'ANOMALIES  : {len(anomalies)}  (le séif ou le ס״ק annoncé n\'existe pas, '
          f'ou le Rama n\'a pas de glose là)')
    print(f'candidats  : {len(candidats)}  (l\'étiquette nomme un autre siman que la page — '
          f'licite, mais rare)')
    if not anomalies:
        print('\nAucune étiquette ne nomme un séif qui ne porte pas ce qu\'elle annonce.')
    else:
        print('\nUne étiquette fausse est invisible aux portes de citation : le contenu de la '
              'cellule\nest une condensation, que la convention du dépôt exempte du verbatim.')
    return 1 if anomalies else 0

if __name__ == '__main__':
    sys.exit(main())
