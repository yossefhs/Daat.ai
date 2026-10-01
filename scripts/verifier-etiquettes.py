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

UNE PLAGE EST CONFRONTÉE SUR TOUTE SON ÉTENDUE. « MB 250:14-17 » annonce quatre ס״ק et
n'en faisait regarder qu'un — le dernier. Sur une liste contiguë cela suffit à l'existence,
et c'est ce qui rendait le trou invisible : le vert était juste par accident de structure,
non par vérification. Chaque point est désormais regardé pour lui-même, ce qui ferme trois
portes que la borne haute seule laissait ouvertes — la plage inversée (dans le même siman
ET d'un siman à l'autre : « MB 250:2-249:3 » descend, et se lit sur le couple, non sur le
point seul), la plage qui change de siman en chemin, et le segment vide servi par Sefaria
au milieu d'une œuvre. Le compte imprimé distingue les ÉTIQUETTES LUES des POINTS DE SOURCE
CONFRONTÉS : 3 992 étiquettes, dont 397 portent une plage, valent 5 264 points — c'étaient
3 992 regards pour 5 264 points annoncés. La largeur d'une plage se compte en POINTS, borne
haute comprise, et le compte des points confrontés est un PLANCHER : un tronçon qui casse
n'ajoute que le parcouru.

UNE LACUNE DE LA SOURCE ET UNE ADRESSE QUI DÉPASSE L'ŒUVRE NE SONT PAS LA MÊME CHOSE, et la
porte les confondait — au profit du silence. Sefaria rend `ref` juste, `error` nul et `he` VIDE
dans les deux cas : pour le siman 169 de Yoré Déa, qu'elle ne numérise pas et qui existe, comme
pour « Mishnah Berurah 999 », qui n'existe pas. Tout `he` vide passait donc « sans accuser ». Le
discriminant se DEMANDE (`api/shape/<œuvre>` : combien de simanim sont servis), il ne se devine
pas : dans l'étendue de l'œuvre, c'est une lacune de la source et on passe ; au-delà, c'est une
ADRESSE FAUSSE, et c'est ce que cette porte existe pour dire. Étendue inconnue = on ne certifie
pas. Et le refus motivé de Sefaria — « ends at Siman 697 » — est autoritatif : il valait jusqu'ici
une œuvre « non chargée », donc le diagnostic le moins grave, alors que la source a répondu.

CE QU'ELLE ANNONCE ET CE QU'ELLE PEUT CONFRONTER SONT DEUX CHOSES, et le compte doit dire
laquelle il compte. Les points de source ANNONCÉS par les étiquettes sont imprimés en face des
points RÉELLEMENT CONFRONTÉS : l'écart est le plancher, mesuré au lieu d'être nommé. Et la
ventilation du thème dit ce que la porte ne peut pas faire : 603 des 3 992 étiquettes vivent
dans une cellule qui, toutes adresses retirées, ne porte pas un mot (toutes en Yoré Déa, 24,3 %
du compartiment) — leur contenu est dans les cellules VOISINES de la rangée, que la porte ne lit
pas. L'annonce antérieure, « 3 987 sur 3 992 portent un thème confrontable, seules 5 n'en portent
aucun », était fausse d'un facteur cent vingt.

ET ELLE REFUSE DE CERTIFIER CE QU'ELLE N'A PAS COMPARÉ. Sefaria injoignable, la porte lisait
ses étiquettes, sautait chaque point, et sortait en 0 sur « ANOMALIES : 0 ». Trois registres
de charge le disent désormais, et la sortie 3 les traduit : œuvres chargées · non numérisées
par Sefaria (autoritatif, on passe) · NON CHARGÉES (la mesure n'a pas eu lieu).

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

# Les trois registres de charge. Une œuvre absente du cache et injoignable rend `[]` comme
# une œuvre que Sefaria ne numérise pas : sans ces registres, la porte ne peut pas dire si
# elle a comparé quoi que ce soit. Voir le docstring de _get et le refus de vert de main().
_chargees, _lacunes, _echecs = set(), set(), {}
# Deux registres de plus. _fausses sépare du silence légitime ce qui est une adresse hors de
# l'œuvre ; _du_cache / _du_reseau disent si la porte a parlé à Sefaria ou relu un instantané.
_fausses = {}
# ⚠️ « RELUE DANS LE CACHE » SE MESURE À L'ÉTAT DU FICHIER AU DÉMARRAGE, non au dictionnaire en
# mémoire — et ma première version de cette ligne a menti pour cette exact raison : une œuvre est
# redemandée à chaque point d'une plage, si bien que le deuxième appel trouvait dans `_cache` ce
# que le PREMIER venait de télécharger, et la porte créditait le cache d'une lecture qu'elle
# venait de faire à Sefaria. Éprouvé en écartant le cache : « 3 RELUES DANS LE CACHE et 0
# obtenues de Sefaria » pour trois œuvres toutes téléchargées. C'est le défaut que cette ligne
# existe pour empêcher, commis dans la ligne elle-même.
_INITIAL = {k for k in _cache if not k.startswith(('__', 'shape:'))}
_du_reseau = set()

def _ecrire_cache():
    try: json.dump(_cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception: pass

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

    ⚠️ NE PAS PERSISTER LE VIDE NE SUFFISAIT PAS, et le trou restant était le pire de tous.
    Un agent de contrôle l'a mesuré en trois gestes : racine fantôme, cache réduit à
    {"__v": 2}, HTTPS_PROXY dirigé sur 127.0.0.1:9. Toutes les œuvres échouent au chargement,
    `if not segs: continue` saute chaque point, et la porte imprime « points de source
    réellement confrontés : 0 pour 47 étiquettes lues », « ANOMALIES : 0 », « Aucune étiquette
    ne nomme un séif qui ne porte pas ce qu'elle annonce » — et SORT EN 0. Le nouveau compte
    de points était le seul témoin, et rien n'agissait sur lui : ni le code de sortie, ni la
    phrase de conclusion, ni la ligne historique « Étiquettes confrontées », qui affiche le
    même 47 réseau coupé ou non. C'est mot pour mot ce que CLAUDE.md nomme le pire : une porte
    qui ne compare rien et sort verte.

    D'où trois registres, et la distinction qu'ils portent est tout l'enjeu :
      · _chargees — l'œuvre a répondu et porte du texte : ses points sont confrontables ;
      · _lacunes  — Sefaria a RÉPONDU et ne numérise pas ce siman (`he: []`, Yoré Déa 123-182
        et à partir de 203). C'est une lacune de numérisation, elle est AUTORITATIVE, on passe
        sans accuser (règle 21 du brief) — et sans que la mesure en soit invalidée ;
      · _echecs   — l'œuvre n'a PAS été chargée : exception réseau, timeout, ou champ « ref »
        qui ne finit pas par le numéro demandé. Rien n'est confronté, et la porte ne peut plus
        prétendre au vert : main() refuse alors de certifier (voir la sortie 3).
    Un échec et une lacune rendent tous deux `[]` à l'appelant ; seul le registre les sépare,
    et c'est pour cela qu'il fallait le tenir ici et non au point d'appel.
    """
    if cle in _cache:
        _chargees.add(cle)
        return _cache[cle]
    titre = slug.rpartition('.')[0]
    n = cle.split(':')[-1]
    out, raison, fausse = [], None, None
    try:
        with urllib.request.urlopen(
                f'https://www.sefaria.org/api/texts/{slug}?context=0&pad=0', timeout=30) as r:
            d = json.load(r)
        _du_reseau.add(cle)
        ref = str(d.get('ref') or '')
        err = str(d.get('error') or '')
        if not ref.rstrip().endswith(n):      # sinon : l'œuvre entière sans dire non
            # ⚠️ UN REFUS MOTIVÉ N'EST PAS UN ÉCHEC DE MESURE. « Shulchan Arukh, Orach Chayim
            # ends at Siman 697 » est la source qui dit jusqu'où elle va : c'est autoritatif,
            # et c'est une adresse fausse. La porte en faisait une œuvre NON CHARGÉE, donc une
            # « mesure incomplète » — le lecteur recevait le diagnostic le moins grave, et la
            # ligne du relevé disait « Sefaria rend «  » », ce qui est faux : elle a répondu.
            f = RX_FIN.search(err)
            if f: fausse = int(f.group(1))
            else:
                raison = f"Sefaria rend « {ref[:60]} » et non {slug}"
                if err: raison += f" (error : {err[:80]})"
        else:
            he = d.get('he')
            segs = [_sans_balises(b) for b in (he if isinstance(he, list) else [he])]
            out = segs if any(_plein(x) for x in segs) else []
            if not out:
                # `he` vide : lacune de la source, ou siman qui dépasse l'œuvre ? On DEMANDE.
                ext = etendue(titre)
                if ext is None:
                    raison = ("he vide ET étendue de l'œuvre inconnue (api/shape ne nomme pas "
                              f"« {titre.replace('_', ' ')} ») : impossible de dire si c'est "
                              "une lacune de la source ou une adresse hors de l'œuvre")
                elif n.isdigit() and int(n) > ext:
                    fausse = ext
    except Exception as e:
        raison = f'{type(e).__name__}: {e}'
    if out:                      # jamais de vide persisté : voir le docstring
        _chargees.add(cle)
        _cache[cle] = out
        _ecrire_cache()
    elif fausse is not None:
        _fausses[cle] = fausse   # ADRESSE HORS DE L'ŒUVRE : accusée, jamais passée en silence
    elif raison is None:
        _lacunes.add(cle)        # lacune de numérisation, autoritative
    else:
        _echecs[cle] = raison    # œuvre NON CHARGÉE : la mesure est incomplète
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

# ⚠️ « he VIDE » N'EST PAS UNE RÉPONSE : C'EST DEUX RÉPONSES, ET LA PORTE LES CONFONDAIT.
# Sefaria rend une réponse D'APPARENCE VALIDE — `ref` juste, `error` nul, `he` vide — pour un
# siman qu'elle ne numérise pas ET pour un siman QUI N'EXISTE PAS. Sondes vérifiées une par une :
#   Mishnah_Berurah.999                              → ref juste · error nul · he VIDE
#   Mishnah_Berurah.700                              → idem (la Michna Beroura s'arrête au 697)
#   Siftei_Kohen_…,_Yoreh_De'ah.550                  → idem (le Chakh s'arrête au 403)
#   Shulchan_Arukh,_Yoreh_De'ah.169                  → idem, et c'est une LACUNE RÉELLE
#   Shulchan_Arukh_HaRav,_Orach_Chayim.140           → idem, lacune réelle (l'Admour HaZaken
#                                                      n'a pas écrit 132-154 ; api/shape en
#                                                      compte 140 sur 651, dont 132-154 et 157)
#   Shulchan_Arukh,_Orach_Chayim.700                 → ref=None + « ends at Siman 697 »
# La porte traitait TOUT `he` vide comme « lacune de numérisation, autoritative, on passe sans
# accuser ». C'est juste pour le Choul'han Aroukh, dont la lacune du siman 169 de Yoré Déa est
# réelle. Mais le chemin était atteignable pour TOUTE œuvre : une étiquette « MB 999 ס״ק ב »
# sortait au vert, comptée parmi les « non numérisées », c'est-à-dire rangée du côté des silences
# légitimes. Or un siman qui dépasse l'œuvre n'est pas une lacune : c'est une ADRESSE FAUSSE, et
# c'est exactement ce que cette porte existe pour dire.
#
# LE DISCRIMINANT NE SE DEVINE PAS, IL SE DEMANDE : `api/shape/<œuvre>` rend `length`, le nombre
# de simanim que Sefaria sert, et `chapters`, leur taille un par un. Mesuré : la Michna Beroura
# 697 simanim et AUCUN vide ; le Choul'han Aroukh de Yoré Déa 403 dont le SEUL vide est le 169 ;
# le Choul'han Aroukh HaRav d'Orah Haïm 651 dont 140 vides, à commencer par 132-154 et 157 —
# ce que CLAUDE.md consigne de mémoire, et que la source confirme ici d'elle-même.
# Donc : siman ≤ length et vide = lacune de la source, on passe. siman > length = adresse fausse.
# ⚠️ ET L'ÉTENDUE INCONNUE NE RETOMBE PAS DANS LE SILENCE. Si `api/shape` ne répond pas, ou ne
# rend pas une entrée dont le titre est CELUI QU'ON A DEMANDÉ (même piège que le champ `ref` :
# elle rend 200 et autre chose — « Arukh_HaShulchan,_Orach_Chayim » rend
# {'error': 'No index or category found'}), alors on ne SAIT pas, et une porte qui ne sait pas
# ne certifie pas : le cas part en œuvre NON CHARGÉE, et la mesure est déclarée incomplète.
SHAPE_V = 1
if _cache.get('__shape_v') != SHAPE_V:
    _cache = {k: v for k, v in _cache.items() if not k.startswith('shape:')}
    _cache['__shape_v'] = SHAPE_V
_etendues = {}
RX_FIN = re.compile(r'ends at\s+\w+\s+(\d+)', re.I)

def etendue(titre):
    """Combien de simanim Sefaria SERT-ELLE de cette œuvre ? None si elle ne le dit pas.

    Le cache de ce chiffre est versionné à part (`__shape_v`) : les segments déjà en cache
    gardent exactement le sens qu'ils avaient, rien dans leur lecture ne change, et il n'y a
    donc pas à les jeter — mais un chiffre d'étendue lu d'une version antérieure, lui, serait
    muet et faux de la même façon qu'un segment vide persisté. Un vide n'est JAMAIS persisté
    ici non plus : une étendue inconnue est redemandée à chaque exécution."""
    if titre in _etendues: return _etendues[titre]
    cle = f'shape:{titre}'
    if cle in _cache:
        _etendues[titre] = _cache[cle]
        return _cache[cle]
    val = None
    try:
        with urllib.request.urlopen(
                f'https://www.sefaria.org/api/shape/{titre}', timeout=30) as r:
            d = json.load(r)
        attendu = titre.replace('_', ' ').strip()
        for e in (d if isinstance(d, list) else []):
            if str(e.get('title', '')).strip() == attendu and isinstance(e.get('length'), int):
                val = e['length']; break
    except Exception:
        val = None
    _etendues[titre] = val
    if val is not None:
        _cache[cle] = val
        _ecrire_cache()
    time.sleep(0.1)
    return val

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

# ⚠️ UNE PLAGE N'ÉTAIT CONFRONTÉE QUE PAR SA BORNE HAUTE, ET LA PORTE L'AVOUAIT.
# « MB 250:14-17 » passait au vert dès lors que le ס״ק 17 existait : ni le 14, ni le 15,
# ni le 16 n'étaient jamais regardés. Sur une liste contiguë 1..N cela SUFFIT pour
# l'existence — et c'est précisément ce qui rendait le trou invisible : le vert était
# juste par accident de structure, non par vérification. Il cessait de l'être dans trois
# cas, dont deux qu'aucune autre porte ne voit :
#   · la PLAGE INVERSÉE — « או״ח רמ״ט:ה-ב » : la borne haute lue (2) existe, la borne
#     basse (5) n'existe pas, et le siman 249 n'a que quatre séifim ;
#   · la PLAGE QUI CHANGE DE SIMAN — « MB 249:3-250:14 » : la porte prenait 14 pour un
#     ס״ק du siman 249 (qui en a 23) et sortait verte, quand le ס״ק annoncé est celui du
#     siman 250, qui n'en a que SIX. C'est la forme « N:a–M:b », déjà employée par le
#     dépôt (« יו״ד ק״ס:ד–ק״ס:י״ב »), où M se trouve être le même siman ;
#   · le POINT VIDE — Sefaria sert parfois un segment blanc au milieu d'une œuvre ; il
#     compte dans len() et fait passer la borne haute sans que rien ne soit écrit là.
# MESURE (les trois compartiments, cache du 29 septembre 2026) : 3 992 étiquettes lues, dont
# 397 portent une plage ; ces 397 plages annoncent 1 669 POINTS et ne faisaient regarder que
# 397 bornes hautes. La largeur d'une plage se compte donc en POINTS, borne haute comprise —
# « MB 250:3-6 » vaut QUATRE points et non trois ; l'histogramme des largeurs est en points,
# et sa somme est 1 669. La somme des écarts b−a vaut 1 272, qui est le nombre de regards
# AJOUTÉS : c'est le même chiffre vu de l'autre bord, et confondre les deux décale
# l'histogramme d'un cran.
#
# ⚠️ CE QUE CE 1 272 N'EST PAS, et l'énoncé précédent le disait faux. Il ne vaut PAS
# « +31,9 % de vérification » : sur une liste contiguë servie par Sefaria, a ≤ b ≤ len entraîne
# l'existence de tout point intermédiaire, si bien que les regards ajoutés sont logiquement
# REDONDANTS avec la borne haute déjà contrôlée. Mesuré sur le cache : 199 œuvres, 0 segment
# vide, 34 cartes de marqueurs de Michna Beroura, 0 carte à trou, 0 carte illisible. Sur cet
# état, l'élargissement ne peut rendre AUCUN verdict que la borne haute ne rendait déjà.
# L'énoncé honnête n'est pas un pourcentage de couverture, c'est : TROIS MODES DE DÉFAILLANCE
# NOUVEAUX (plage inversée, plage qui change de siman, borne basse hors d'atteinte) plus un
# TEST DE VACUITÉ PAR POINT, aucun d'eux constaté aujourd'hui, tous couverts le jour où l'un
# paraît. Le gain immédiat est un compte de confrontations qui cesse de mentir — rien de plus.
# ⚠️ LE TIRET DE PLAGE N'A TOUJOURS PAS D'ESPACES, et RIEN ici n'y touche : TIRET et NB
# sont inchangés, le nombre d'étiquettes lues reste 3 992 au signe près. « או״ח רמ״ב:א — אין »
# n'est pas plus une plage après qu'avant ; c'est le faux positif qui avait coûté 35
# anomalies imaginaires sur 49, et on ne le rouvre pas pour élargir la borne basse.

RX_MARQ = re.compile(r'^\s*\(\s*([\u05D0-\u05EA]{1,4})\s*\)')
_cartes_mb = {}

def mb_carte(n):
    """ס״ק → index, lue sur les marqueurs « (א) » que Sefaria imprime DANS l'entrée.

    Plus vraie que le compte : elle dit quels ס״ק existent, et non combien il y en a.
    On ne devine rien — dès qu'une entrée (hors פתיחה de tête) ne porte pas de marqueur
    lisible, ou qu'un marqueur se répète, la numérotation est illisible et on retombe sur
    le compte et le décalage mesuré. Relevé sur les 34 simanim de Michna Beroura servis au
    dépôt : tous alignés, la seule entrée sans marqueur étant la פתיחה des simanim 243,
    248 et 253. La carte ne change donc AUCUN verdict aujourd'hui ; elle tiendra le jour
    où une entrée non numérotée paraîtra au milieu."""
    if n in _cartes_mb: return _cartes_mb[n]   # relue à chaque point d'une plage, sinon
    segs = mb(n)
    if not segs: return None
    carte = {}
    for i, seg in enumerate(segs):
        m = RX_MARQ.match(seg)
        if m is None:
            if i == 0: continue          # la פתיחה non numérotée
            _cartes_mb[n] = None; return None
        v = _num(m.group(1))
        if v is None or v in carte:
            _cartes_mb[n] = None; return None
        carte[v] = i
    _cartes_mb[n] = carte or None
    return _cartes_mb[n]

def _plein(seg):
    """Sefaria écrit-il quelque chose à cet endroit ?"""
    return bool(re.sub(r'[\s\u00a0]', '', seg or ''))

def _bornes(m, n):
    """(borne basse, borne haute, siman de la borne haute, est-ce une plage).

    ⚠️ UNE PLAGE PEUT RÉPÉTER LE SIMAN : « יו״ד ק״ס:ד–ק״ס:י״ב » va du séif 4 au séif 12
    du siman 160, et non « du séif 4 au séif 160 ». Quand la borne haute porte elle-même
    un deux-points, sa PREMIÈRE moitié est un siman et la seconde le point — et ce siman
    n'est pas forcément celui de la borne basse."""
    a = _num(m.group(2))
    dernier = m.lastindex or 0
    g3 = m.group(3) if dernier >= 3 else None
    g4 = m.group(4) if dernier >= 4 else None
    if not g3: return a, a, n, False
    if g4: return a, _num(g4), (_num(g3) or n), True
    return a, (_num(g3) or a), n, True

# ⚠️ ET UNE CIBLE QUE SEFARIA N'A JAMAIS SERVIE : « Arukh_HaShulchan,_Orach_Chayim » rend
# « Unable to find text for that ref » (HTTP 400) — le titre servi s'écrit « Orach CHAIM »,
# sans le yod, alors que le Choul'han Aroukh s'écrit « Orach Chayim ». C'est mot pour mot la
# leçon du commit b92a48dc : LE NOM D'UNE CIBLE EST UN PRÉFIXE DU « ref » SERVI, non une
# étiquette qu'on écrit de mémoire. Mesuré : « Arukh_HaShulchan,_Orach_Chaim.246 » rend
# 24 séifim, « …_Orach_Chayim.246 » rend une erreur. Aucune étiquette du dépôt ne passe
# aujourd'hui par cette branche (les 6 de l'Aroukh HaChoul'han sont toutes de Yoré Déa) :
# le défaut était DORMANT, et c'est la seule raison pour laquelle il n'a rien coûté.
def _oeuvre(genre, m):
    """(chargeur, unité, nom de l'œuvre du siman k, clé de cache du siman k). Un seul endroit
    où le genre se traduit en œuvre, pour que la plage se déploie de la même façon pour toutes
    — et pour que le diagnostic d'absence puisse retrouver la clé qui porte la raison."""
    if genre == 'shk':
        return (shk, 'ס״ק', (lambda k: f"le Chakh du siman {k} de Yoré Déa"),
                (lambda k: f'shk:{k}'))
    if genre == 'taz':
        return (taz_yd, 'ס״ק', (lambda k: f"le Taz du siman {k} de Yoré Déa"),
                (lambda k: f'tazyd:{k}'))
    if genre == 'rav':
        return ((lambda k: _get(f'Shulchan_Arukh_HaRav,_Orach_Chayim.{k}', f'rav:{k}')),
                'séif', (lambda k: f"le Choul'han Aroukh HaRav du siman {k}"),
                (lambda k: f'rav:{k}'))
    if genre == 'ahs':
        yd = bool(re.search(YD, m.group(0)))
        pre = 'ahsyd' if yd else 'ahsoh'
        slug = ((lambda k: f"Arukh_HaShulchan,_Yoreh_De'ah.{k}") if yd
                else (lambda k: f'Arukh_HaShulchan,_Orach_Chaim.{k}'))
        return ((lambda k: _get(slug(k), f'{pre}:{k}')),
                'séif', (lambda k: f"l'Aroukh HaChoul'han du siman {k}"),
                (lambda k: f'{pre}:{k}'))
    if genre == 'mb':
        return (mb, 'ס״ק', (lambda k: f"la Michna Beroura du siman {k}"),
                (lambda k: f'mb:{k}'))
    if genre.endswith('_yd'):
        return (seifim_yd, 'séif', (lambda k: f"le siman {k} de Yoré Déa"),
                (lambda k: f'yd:{k}'))
    return (seifim, 'séif', (lambda k: f"le siman {k} d'Orah Haïm"), (lambda k: f'sa:{k}'))

def _place(genre, n, segs, x):
    """L'index du point x dans les segments, et le nombre de points numérotés de l'œuvre.
    Pour la Michna Beroura, la carte des marqueurs prime sur le compte ; ailleurs, Sefaria
    sert un segment par séif et l'index est le rang."""
    if genre == 'mb':
        carte = mb_carte(n)
        if carte is not None:
            return carte.get(x), max(carte)
        d = mb_decale(n) or 0
        return (x - 1 + d), (len(segs) - d)
    return (x - 1), len(segs)

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


# ⚠️ « 3 987 ÉTIQUETTES SUR 3 992 ANNONCENT UN THÈME CONFRONTABLE, SEULES 5 N'EN PORTENT
# AUCUN » : C'ÉTAIT FAUX D'UN FACTEUR CENT VINGT, et le chiffre venait de ce que l'on ne
# retirait de la cellule QUE l'adresse appariée, en laissant passer pour un « thème » les
# autres adresses de la même cellule. Recompté ici, non sur un relevé mais sur les pages :
#   603 étiquettes (15,1 %) dont la cellule, toutes adresses retirées, ne porte PAS UN MOT —
#       et les 603 sont en Yoré Déa, soit 24,3 % de ce compartiment ;
#   1 850 (46,3 %) à un à cinq mots · 1 539 (38,6 %) à six mots ou plus.
# ⚠️ ET LA SUITE CORRIGE AUSSI CE RECOMPTAGE-LÀ, car « aucun thème » n'est pas « rien n'est
# annoncé » : ces 603 étiquettes vivent dans une COLONNE D'ANCRAGE (« Cas | Berakha | Ancrage »),
# et le contenu qu'elles adressent est dans les cellules VOISINES de leur rangée. Mesuré :
# 572 des 603 sont dans une rangée dont les autres cellules portent six mots ou plus, 31 dans
# une rangée qui en porte un à cinq, et AUCUNE n'est orpheline (mesuré par un arbitre, en
# instrumentant ce compteur-ci ; le « 563 / 40 » qui figurait ici venait d'un appariement
# cellule↔rangée par égalité de chaîne, quand la porte apparie par POSITION — et ses deux
# nombres contredisaient la sortie que ce même fichier imprime, « dont 572 »). Ce que la porte
# ne peut donc pas
# faire, et qu'il faut écrire au lieu de le taire : confronter l'adresse au contenu de SA cellule.
# Le mot « mot » est ici un jeton de deux lettres au moins ; en comptant aussi les jetons d'une
# seule lettre (un numéral hébraïque nu, « א »), la classe sans thème tombe à 540 et non 603.
# La frontière des classes dépend de cette convention, et c'est pour cela qu'elle est écrite.
MOT_THEME = re.compile(r'[A-Za-z\u00C0-\u024F\u05D0-\u05EA]{2,}')
RXTR = re.compile(r'<tr\b.*?</tr>', re.S | re.I)
TOUTES_ADRESSES = (RX_HAGAHA, RX_HAGAHA_YD, RX_MB, RX_SHK, RX_TAZ,
                   RX_RAV, RX_AHS, RX_SEIF, RX_SEIF_YD)

def mots_du_theme(cell):
    """Les mots de la cellule, TOUTES les adresses retirées — pas seulement l'appariée."""
    t = list(cell)
    for rx in TOUTES_ADRESSES:
        for m in rx.finditer(cell):
            t[m.start():m.end()] = [' '] * (m.end() - m.start())
    txt = re.sub(r'<[^>]*>', ' ', ''.join(t))
    txt = re.sub(r'&[#0-9A-Za-z]+;', ' ', txt)
    return MOT_THEME.findall(txt)

def _voisinage(s):
    """Pour chaque cellule (par son début), les mots des AUTRES cellules de sa rangée."""
    rangees = [(m.start(), m.end()) for m in RXTR.finditer(s)]
    cells = [(m.start(), m.end(), m.group(1)) for m in RXTD.finditer(s)]
    out = {}
    for i, (d, f, c) in enumerate(cells):
        r = next(((a, b) for a, b in rangees if a <= d and f <= b), None)
        if r is None: continue
        soeurs = [cc for j, (dd, ff, cc) in enumerate(cells)
                  if j != i and r[0] <= dd and ff <= r[1]]
        out[d] = len(mots_du_theme(' '.join(soeurs)))
    return out

def examiner(path, siman_page, anomalies, candidats, compte):
    s = io.open(path, encoding='utf-8').read()
    nom = os.path.basename(path)
    voisinage = _voisinage(s)
    for _mcell in RXTD.finditer(s):
        cell = _mcell.group(1)
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
                if n is None or a is None: continue
                a, b, n_haut, plage = _bornes(m, n)
                if b is None: b = a
                txt = m.group(0).strip()
                compte[genre] += 1
                compte['_plages'] += 1 if plage else 0
                # la ventilation du thème : ce que la cellule annonce, hors adresses
                k_mots = len(mots_du_theme(cell))
                compte['_th0' if k_mots == 0 else ('_th15' if k_mots <= 5 else '_th6')] += 1
                if k_mots == 0 and voisinage.get(_mcell.start(), 0) >= 6:
                    compte['_th0_rangee'] += 1
                # les POINTS ANNONCÉS, face aux points confrontés : sans eux, « plancher »
                # est un mot et non une mesure.
                if n_haut == n and b >= a: compte['_annonces'] += b - a + 1
                else: compte['_annonces_flou'] += 1
                if n != siman_page:
                    candidats.append(f"{nom} · « {txt} » nomme le siman {n}, "
                                     f"la page est le siman {siman_page}")

                charge, unite, libelle, cle_de = _oeuvre(genre, m)
                sans, casse, prive, dits = [], False, [], set()

                def _absence(k):
                    """Rien n'a été servi pour le siman k de cette œuvre — faut-il accuser ?

                    Trois raisons possibles, et elles ne se valent pas : l'œuvre n'a pas été
                    chargée (la mesure n'a pas eu lieu, main() refuse de certifier) ; Sefaria
                    a répondu et ne numérise pas ce siman (lacune de la source, autoritative,
                    on passe) ; ou LE SIMAN DÉPASSE L'ŒUVRE, et c'est une adresse fausse — le
                    cas que cette porte existe pour dire, et qu'elle rangeait avec les silences
                    légitimes. _get a déjà tranché et inscrit sa raison : on la relit ici."""
                    ext = _fausses.get(cle_de(k))
                    if ext is None or k in dits: return
                    dits.add(k)
                    compte['_hors_oeuvre'] += 1
                    # ⚠️ LA SEULE CLASSE DE FAUX POSITIFS DE CE VERDICT, ET ELLE SE MESURE :
                    # le siman JUSTE au-delà de ce que Sefaria sert peut être une lacune de
                    # numérisation en FIN d'ouvrage et non une adresse fausse. Mesuré sur le
                    # Taz de Yoré Déa : api/shape en sert 402, et api/v2/raw/index en déclare
                    # 403 (« lengths: [403, 3421] ») ; Turei_Zahav…403 rend un `ref` juste et
                    # un `he` vide. Aucune étiquette du dépôt n'est dans ce cas aujourd'hui —
                    # le siman le plus haut cité du Taz est le 203 — mais la réserve se dit.
                    queue = ("" if k > ext + 1 else
                             " — ATTENTION : c'est le siman JUSTE au-delà ; vérifier à la main "
                             "qu'il ne s'agit pas d'une lacune de numérisation en fin "
                             "d'ouvrage (l'index déclare parfois un siman de plus que le "
                             "texte servi : le Taz de Yoré Déa, 403 déclarés, 402 servis)")
                    anomalies.append(
                        f"{nom} · « {txt} » — {libelle(k)} n'existe pas : Sefaria ne sert que "
                        f"{ext} simanim de cette œuvre (adresse HORS DE L'ŒUVRE, "
                        f"et non une lacune de la source){queue}")

                def _regarder(k, x):
                    """Le point x de l'œuvre du siman k : existe-t-il, porte-t-il du texte ?

                    Rend le segment, ou None. Un seul endroit où un point est confronté, pour
                    que la plage inversée reçoive le MÊME examen que la plage licite — c'est
                    le défaut (c) : « MB 249:26-23 » sortait « plage inversée » et ne disait
                    JAMAIS que la Michna Beroura du siman 249 n'a pas de ס״ק 26 (elle en a 23),
                    parce que le `continue` de l'inversion coupait l'examen. Le diagnostic
                    rendu n'était pas le plus grave."""
                    segs = charge(k)
                    if not segs:
                        # œuvre non chargée, lacune de la source, ou adresse hors de l'œuvre :
                        # rien n'est confronté ici, il faut que cela se COMPTE, et le troisième
                        # cas doit s'ACCUSER.
                        _absence(k)
                        prive.append(k)
                        compte['_sans_source'] += 1
                        return None, None
                    i, haut = _place(genre, k, segs, x)
                    compte['_points'] += 1
                    if i is None or not (0 <= i < len(segs)):
                        anomalies.append(f"{nom} · « {txt} » — {libelle(k)} n'a pas de "
                                         f"{unite} {x} (il en a {haut})")
                        return None, haut
                    if not _plein(segs[i]):
                        anomalies.append(f"{nom} · « {txt} » — {libelle(k)} ne porte "
                                         f"RIEN au {unite} {x} : le segment est vide")
                        return None, haut
                    return segs[i], haut

                # ⚠️ L'INVERSION SE LIT SUR LE COUPLE (siman, point), ET NON SUR LE POINT SEUL.
                # C'était le défaut (b), et c'est le croisement exact des deux témoins que
                # l'élargissement aux plages revendique : le test « n_haut == n and b < a » ne
                # voyait pas « MB 250:2-249:3 », que la porte traitait comme un parcours licite
                # en deux tronçons — elle confrontait 250:2..6 puis 249:1..3, huit points, et
                # sortait verte. Mesuré : 0 plage changeant de siman dans l'état courant du
                # dépôt, donc le défaut est DORMANT — mais c'est le chemin que l'élargissement
                # vient d'ouvrir, et une comparaison de tuples le ferme.
                if (n_haut, b) < (n, a):
                    ou = (f"du {unite} {a} au {unite} {b}" if n_haut == n else
                          f"du {unite} {a} du siman {n} au {unite} {b} du siman {n_haut}")
                    anomalies.append(f"{nom} · « {txt} » — plage inversée : elle va {ou}")
                    # et l'examen ne s'arrête PAS là : les deux bornes nommées sont confrontées,
                    # sinon le lecteur reçoit le diagnostic le moins grave (défaut c).
                    for k, x in ((n, a), (n_haut, b)):
                        if x is not None and x >= 1: _regarder(k, x)
                    if prive: compte['_etiq_sans_source'] += 1
                    continue
                if a < 1:
                    anomalies.append(f"{nom} · « {txt} » — borne basse {a} : "
                                     f"il n'y a pas de {unite} {a}")
                    continue
                # ⚠️ TOUTE SON ÉTENDUE, ET NON SA SEULE BORNE HAUTE. Un tronçon par siman
                # traversé : une plage ordinaire en a un, une plage qui change de siman en
                # a deux, et dans chacun CHAQUE point annoncé est regardé pour lui-même.
                troncons = ([(n, a, b)] if n_haut == n
                            else [(n, a, None), (n_haut, 1, b)])
                for k, bas, haut_dit in troncons:
                    segs = charge(k)
                    # he: [] = lacune de la source SI le siman est dans l'étendue de l'œuvre ;
                    # au-delà, c'est une adresse fausse, et _absence l'accuse.
                    if not segs:
                        _absence(k)
                        prive.append(k); compte['_sans_source'] += 1
                        continue
                    _, haut = _place(genre, k, segs, bas)
                    fin_t = haut if haut_dit is None else haut_dit
                    # sinon range(bas, fin_t+1) est VIDE et la borne basse hors d'atteinte
                    # sortirait en silence — le défaut même que cette réparation ferme.
                    if bas > fin_t:
                        anomalies.append(f"{nom} · « {txt} » — {libelle(k)} n'a pas de "
                                         f"{unite} {bas} (il en a {haut})")
                        casse = True; break
                    for x in range(bas, fin_t + 1):
                        seg, _h = _regarder(k, x)
                        if seg is None:
                            casse = True; break
                        if genre in ('hagaha', 'hagaha_yd') and not porte_glose_rama(seg):
                            sans.append(x)
                    if casse: break
                if prive: compte['_etiq_sans_source'] += 1
                if sans and not casse:
                    tract = 'Yoré Déa' if genre.endswith('_yd') else 'Orah Haïm'
                    anomalies.append(
                        f"{nom} · « {txt} » — le Rama n'a AUCUNE glose sur "
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
              'mb': 0, 'shk': 0, 'taz': 0, 'rav': 0, 'ahs': 0,
              '_plages': 0, '_points': 0, '_sans_source': 0, '_etiq_sans_source': 0,
              '_hors_oeuvre': 0, '_annonces': 0, '_annonces_flou': 0,
              '_th0': 0, '_th15': 0, '_th6': 0, '_th0_rangee': 0}
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
    # ⚠️ UNE PORTE QUI NE COMPARE RIEN ET SORT VERTE EST PIRE QU'UNE PORTE ABSENTE : le
    # compte des étiquettes n'est PAS le compte des confrontations. Une étiquette simple
    # vaut un point de source ; « MB 250:3-6 » en vaut quatre, et n'en valait qu'un.
    # ⚠️ ET CE COMPTE EST UN PLANCHER, non un total, dès qu'une anomalie paraît : un tronçon
    # qui casse en chemin n'ajoute que le parcouru, et un point dont l'œuvre n'a pas été
    # chargée n'ajoute rien du tout. Il faut le NOMMER ainsi. Un plancher annoncé comme un
    # compte est l'erreur la plus coûteuse de ce dépôt.
    lues = sum(v for k, v in compte.items() if not k.startswith('_'))
    print(f"dont {compte['_plages']} portent une plage (largeur comptée en POINTS, "
          f"borne haute comprise : « MB 250:3-6 » vaut QUATRE points, pas trois)")
    # ⚠️ « PLANCHER » ÉTAIT UN MOT ; LE VOICI MESURÉ. Le compte des points confrontés ne peut
    # pas être relu seul : un tronçon qui casse n'ajoute que le parcouru, un point dont l'œuvre
    # n'a pas été chargée n'ajoute rien, et une plage inversée ne fait regarder que ses deux
    # bornes nommées au lieu de sa largeur. Face à lui, les POINTS ANNONCÉS par les étiquettes
    # elles-mêmes : l'écart des deux EST le plancher, et il se lit au lieu de se croire.
    manque = compte['_annonces'] - compte['_points']
    print(f"points de source : {compte['_annonces']} ANNONCÉS par les étiquettes · "
          f"{compte['_points']} RÉELLEMENT CONFRONTÉS"
          + ("" if manque <= 0 else f" · {manque} jamais regardés"))
    if compte['_annonces_flou']:
        print(f"    + {compte['_annonces_flou']} étiquette(s) dont la largeur annoncée n'est pas "
              f"calculable avant chargement (plage inversée, ou qui change de siman)")
    if manque > 0:
        print("    le compte des confrontés est donc un PLANCHER : un tronçon qui casse "
              "n'ajoute que le parcouru, un point dont l'œuvre n'a pas été chargée n'ajoute "
              "rien, et une plage inversée ne fait regarder que ses deux bornes nommées.")
    # La ventilation du THÈME : une étiquette dont la cellule ne porte, toutes adresses retirées,
    # aucun mot n'est pas confrontable au contenu de cette cellule — le dire est le seul moyen de
    # ne pas prendre un plafond pour un compte. Voir le commentaire de mots_du_theme.
    th = compte['_th0'] + compte['_th15'] + compte['_th6']
    if th:
        print(f"thème annoncé dans la cellule (toutes adresses retirées, un mot = deux lettres "
              f"au moins) : {compte['_th6']} étiquettes à six mots ou plus "
              f"({100 * compte['_th6'] / th:.1f} %) · {compte['_th15']} à un à cinq mots "
              f"({100 * compte['_th15'] / th:.1f} %) · {compte['_th0']} SANS AUCUN MOT "
              f"({100 * compte['_th0'] / th:.1f} %)")
        if compte['_th0']:
            print(f"    dont {compte['_th0_rangee']} dans une rangée dont les AUTRES cellules "
                  f"portent six mots ou plus (colonne d'ancrage : le contenu adressé est là, "
                  f"et cette porte ne le lit pas)")
    # Les trois registres de charge, imprimés sans condition : c'est le seul témoin qui dise
    # si la porte a comparé quelque chose, et le seul sur lequel le code de sortie agisse.
    print(f"œuvres chargées : {len(_chargees)} — dont {len(_chargees & _INITIAL)} RELUES DANS "
          f"LE CACHE ({os.path.basename(CACHE)}) et {len(_chargees - _INITIAL)} obtenues de Sefaria "
          f"sur cette exécution ({len(_du_reseau)} appels de texte, "
          f"{len(_etendues)} d'étendue) · "
          f"lacunes de la source (he vide DANS l'étendue de l'œuvre, on passe sans accuser) : "
          f"{len(_lacunes)} · HORS DE L'ŒUVRE (siman au-delà de ce que Sefaria sert — accusé) : "
          f"{len(_fausses)} · NON CHARGÉES (rien n'y a été confronté) : {len(_echecs)}")
    # ⚠️ RÉSERVE À LIRE AVEC LA LIGNE CI-DESSUS. « œuvres chargées : 199 · … · 0 · 0 » décrit
    # LE CACHE, pas Sefaria : un lecteur y voit « la source a répondu 199 fois » quand elle n'a
    # pas été appelée une seule fois. Le cache est un instantané ; il ne vieillit pas tout seul.
    if _chargees and not _du_reseau:
        print(f"    ⚠ AUCUNE œuvre n'a été demandée à Sefaria sur cette exécution : tout vient "
              f"du cache, et ce verdict confronte les pages à un INSTANTANÉ, non à la source "
              f"d'aujourd'hui. Supprimer {os.path.basename(CACHE)} pour re-confronter.")
    elif _etendues:
        print(f"    étendues d'œuvre demandées à api/shape : "
              f"{sum(1 for v in _etendues.values() if v is not None)} connues, "
              f"{sum(1 for v in _etendues.values() if v is None)} inconnues")
    if _fausses:
        for cle, ext in list(_fausses.items())[:8]:
            print(f"    ✗ {cle} — l'œuvre s'arrête au siman {ext}")
        if len(_fausses) > 8: print(f"    … et {len(_fausses) - 8} autres")
    if _echecs:
        for cle, raison in list(_echecs.items())[:8]:
            print(f"    ⚠ {cle} — {raison}")
        if len(_echecs) > 8: print(f"    … et {len(_echecs) - 8} autres")
        print(f"    étiquettes dont au moins un point n'a pu être confronté : "
              f"{compte['_etiq_sans_source']} · points hors d'atteinte : "
              f"{compte['_sans_source']}")
    print(f'ANOMALIES  : {len(anomalies)}  (le séif ou le ס״ק annoncé n\'existe pas — '
          f'hors de l\'œuvre : {compte["_hors_oeuvre"]} —, ou le Rama n\'a pas de glose là)')
    print(f'candidats  : {len(candidats)}  (l\'étiquette nomme un autre siman que la page — '
          f'licite, mais rare)')

    # ⚠️ LE REFUS DE CERTIFIER. C'était le défaut le plus grave, et il tenait à ceci : rien
    # n'agissait sur le compte de points. Racine fantôme, cache vidé, HTTPS_PROXY sur
    # 127.0.0.1:9 — la porte imprimait « 0 pour 47 étiquettes lues », « ANOMALIES : 0 »,
    # « Aucune étiquette ne nomme un séif qui ne porte pas ce qu'elle annonce », et SORTAIT
    # EN 0. Deux verrous, et la sortie 3 se distingue de la sortie 1 (des anomalies) parce
    # que ce n'est pas la même nouvelle : l'une dit que le contenu est fautif, l'autre que la
    # MESURE n'a pas eu lieu. Une lacune de numérisation ne déclenche NI l'un ni l'autre :
    # Sefaria a répondu, et son silence sur ce siman est autoritatif.
    incomplete = (lues > 0 and compte['_points'] == 0) or bool(_echecs)
    if lues > 0 and compte['_points'] == 0:
        print(f"\n✗✗ MESURE NON FAITE : {lues} étiquettes lues et AUCUN point de source "
              f"confronté.\nAucun verdict n'est rendu ici — ni vert ni rouge. Vérifier "
              f"l'accès à Sefaria, puis relancer.")
    elif _echecs:
        print(f"\n✗✗ MESURE INCOMPLÈTE : {len(_echecs)} œuvre(s) n'ont pas été chargées, "
              f"{compte['_etiq_sans_source']} étiquette(s) sur {lues} n'ont donc pas été "
              f"entièrement confrontées.\nAucune anomalie sur ce qui a pu être comparé : ce "
              f"n'est pas un vert, c'est une mesure partielle. Relancer Sefaria joignable.")
    if anomalies:
        print('\nUne étiquette fausse est invisible aux portes de citation : le contenu de la '
              'cellule\nest une condensation, que la convention du dépôt exempte du verbatim.')
    elif not incomplete:
        print('\nAucune étiquette ne nomme un séif qui ne porte pas ce qu\'elle annonce.')
    if anomalies: return 1
    return 3 if incomplete else 0

if __name__ == '__main__':
    sys.exit(main())
