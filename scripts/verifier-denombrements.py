#!/usr/bin/env python3
"""Les affirmations de dénombrement — « c'est le seul », « les trois », « le plus long ».

Cinquième point aveugle, trouvé le 17 septembre 2026 en relisant le siman 234 de
Yoré Déa alors que les neuf portes étaient vertes. La page y affirmait cinq
dénombrements dont aucun n'était exact, et l'un d'eux était contredit QUATRE FOIS
par la page elle-même. Aucune citation n'était fausse : le défaut ne vit pas dans
le verbatim mais dans la phrase française qui le compte.

Corollaire appris au premier tour de correction : remplacer une affirmation
absolue fausse par une énumération fermée également fausse n'est pas une
correction. D'où le choix de signaler AUSSI les énumérations fermées.

Trois verdicts, et ils ne se valent pas :

  FAUX       — réfuté mécaniquement. Le nombre annoncé n'est pas celui de la
               source (séifim du siman, ס״ק du Chakh ou du Taz). Sort en code 1.
  DÉSACCORD  — les trois langues d'un même niveau ne disent pas le même nombre.
               L'une des trois est fausse, la machine ne sait pas laquelle.
               Sort en code 1.
  À VÉRIFIER — une affirmation absolue ou une énumération fermée, qu'aucune
               machine ne peut trancher (« le seul séif où le Rama tranche
               contre le Mehaber »). Listée, jamais bloquante : ces phrases sont
               légitimes quand elles sont vraies. C'est au relecteur d'y aller.

Usage :
  python3 scripts/verifier-denombrements.py                      # tout le site
  python3 scripts/verifier-denombrements.py --path sources/yoreh-deah/siman-234
  python3 scripts/verifier-denombrements.py --a-verifier         # + la liste des candidats
  python3 scripts/verifier-denombrements.py --bref
"""
import sys, os, re, json, glob, subprocess, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache-denombrements.json")

# ---------------------------------------------------------------- numéraux

ONES = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9}
TENS = {'י':10,'כ':20,'ל':30,'מ':40,'נ':50,'ס':60,'ע':70,'פ':80,'צ':90}
HUNS = {'ק':100,'ר':200,'ש':300,'ת':400}
GEM = {**ONES, **TENS, **HUNS}

def gematria(s):
    """Numéral hébreu → entier. None si ce n'en est pas un."""
    s = re.sub(r'["״\'׳]', '', s)
    if not s or any(c not in GEM for c in s):
        return None
    return sum(GEM[c] for c in s)

MOTS_FR = {}
for _i, _u in enumerate(['zéro','un','deux','trois','quatre','cinq','six','sept','huit',
                         'neuf','dix','onze','douze','treize','quatorze','quinze','seize']):
    MOTS_FR[_u] = _i
MOTS_FR['une'] = 1
for _d, _n in (('vingt',20),('trente',30),('quarante',40),('cinquante',50),
               ('soixante',60),('quatre-vingt',80)):
    MOTS_FR[_d] = _n
    MOTS_FR[_d + 's'] = _n
    MOTS_FR[_d + '-et-un'] = _n + 1
    for _j in range(1, 10):
        MOTS_FR[f"{_d}-{['','un','deux','trois','quatre','cinq','six','sept','huit','neuf'][_j]}"] = _n + _j
for _j, _u in enumerate(['dix','onze','douze','treize','quatorze','quinze','seize',
                         'dix-sept','dix-huit','dix-neuf']):
    MOTS_FR['soixante-' + _u] = 70 + _j          # soixante-dix … soixante-dix-neuf
    MOTS_FR['quatre-vingt-' + _u] = 90 + _j
MOTS_FR['dix-sept'], MOTS_FR['dix-huit'], MOTS_FR['dix-neuf'] = 17, 18, 19
MOTS_FR['cent'] = 100

MOTS_EN = {}
for _i, _u in enumerate(['zero','one','two','three','four','five','six','seven','eight',
                         'nine','ten','eleven','twelve','thirteen','fourteen','fifteen',
                         'sixteen','seventeen','eighteen','nineteen']):
    MOTS_EN[_u] = _i
for _d, _n in (('twenty',20),('thirty',30),('forty',40),('fifty',50),('sixty',60),
               ('seventy',70),('eighty',80),('ninety',90)):
    MOTS_EN[_d] = _n
    for _j, _u in enumerate(['','one','two','three','four','five','six','seven','eight','nine']):
        if _u:
            MOTS_EN[f"{_d}-{_u}"] = _n + _j
MOTS_EN['hundred'] = 100

MOTS_HE = {'אחד':1,'אחת':1,'שנים':2,'שניים':2,'שתי':2,'שני':2,'שלושה':3,'שלוש':3,
           'שלשה':3,'ארבעה':4,'ארבע':4,'חמישה':5,'חמש':5,'שישה':6,'שש':6,
           'שבעה':7,'שבע':7,'שמונה':8,'תשעה':9,'תשע':9,'עשרה':10,'עשר':10}

def nombre(jeton):
    """Un jeton (chiffre, mot, numéral hébreu) → entier, ou None."""
    j = jeton.strip()
    if re.fullmatch(r'\d{1,3}', j):
        return int(j)
    low = j.lower()
    for table in (MOTS_FR, MOTS_EN):
        if low in table:
            return table[low]
    if j in MOTS_HE:
        return MOTS_HE[j]
    # numéral hébreu : seulement s'il porte son gershayim — sans quoi tout mot
    # hébreu court serait un nombre.
    if re.search(r'["\u05f4\'\u05f3]', j):
        return gematria(j)
    return None

# Un nombre ÉCRIT COMME TEL. En français et en anglais : chiffres ou mots-nombres,
# jamais un mot quelconque. En hébreu : un mot-nombre, ou un numéral PORTANT SON
# gershayim (כ״ה) — sans quoi « בכל » vaudrait 52 et « אלו » 37, et le contrôle
# transformerait chaque mot court en dénombrement. C'est exactement ce qu'il a fait
# à son premier essai : 118 « FAUX » sur le seul siman 228, tous imaginaires.
N_LATIN = r"(?:\d{1,3}|" + "|".join(sorted(set(list(MOTS_FR) + list(MOTS_EN)),
                                          key=len, reverse=True)) + r")"
N_HEB = r"(?:\d{1,3}|[א-ת]{1,3}[\"״][א-ת]|[א-ת]{1,2}[\'׳]|" + \
        "|".join(sorted(MOTS_HE, key=len, reverse=True)) + r")"

# ------------------------------------------- famille A : dénombrements vérifiables
#
# Un dénombrement n'est pas un nombre posé à côté d'un mot : c'est une phrase qui
# COMPTE. « voir séifim 20 et 21 » n'affirme rien ; « ses 51 séifim » si. D'où
# l'amorce obligatoire — déterminant possessif/défini ou verbe de dénombrement.
# L'amorce fait tout. « LES deux séifim suivants » et « ses 74 séifim » ont la même
# forme et ne disent pas la même chose : le déterminant défini désigne, le verbe de
# dénombrement et le possessif COMPTENT. Trois des cinq derniers faux positifs
# tenaient à cela seul — « The two seifim say one thing in two ways » comparé aux six
# séifim du siman 182, parce que le mot « siman » traînait dans la phrase suivante.
AMORCE_FR = r"(?:ses|compte|comporte|contient|totalise|réunit)"
AMORCE_EN = r"(?:its|has|counts|comprises|contains|totals)"
# Les amorces FAIBLES ne fondent aucun verdict — « les deux séifim », « sur douze
# séifim » désignent aussi souvent un sous-ensemble qu'un total. Mais les rendre
# invisibles serait pire que les signaler : elles partent en « À VÉRIFIER ».
AMORCE_FAIBLE_FR = r"(?:les|des|ces|sur|de|en|parmi)"
AMORCE_FAIBLE_EN = r"(?:the|of|over|across|among|all)"
# « ובו … סעיפים » est la formule du Choul'han Aroukh lui-même, imprimée dans son
# chapeau. Partout où une page la porte, elle REPRODUIT la source — dans un
# blockquote, dans une traduction, ou dans la troisième colonne du tableau des
# séifim qui la résume. Elle n'affirme donc jamais le décompte de la page, et le
# siman 234 en est la démonstration : son chapeau dit ע״ב (72), l'édition suivie
# en découpe 74, et la page le dit noir sur blanc. Le total revendiqué par la page
# s'écrit autrement — מונה, יש בו, בן.
AMORCE_HE = r"(?:מונה|בן|בת|יש בו|כולל)"

MOT_SEIF = r"(?:séifim|sé\'ifim|seifim|se\'ifim)"
MOT_SK = r"(?:ס[\"״]?ק|séifim qetanim|seifim ketanim|se\'ifim qetanim)"

RE_SEIFIM = re.compile(
    r"\b" + AMORCE_FR + r"\s+(?P<n>" + N_LATIN + r")\s+" + MOT_SEIF + r"\b", re.I)
RE_SEIFIM_EN = re.compile(
    r"\b" + AMORCE_EN + r"\s+(?P<n>" + N_LATIN + r")\s+" + MOT_SEIF + r"\b", re.I)
RE_SEIFIM_HE = re.compile(
    r"(?<![א-ת])" + AMORCE_HE + r"\s+(?P<n>" + N_HEB + r")\s+סעיפים")

RE_FAIBLE_FR = re.compile(
    r"\b" + AMORCE_FAIBLE_FR + r"\s+(?P<n>" + N_LATIN + r")\s+" + MOT_SEIF + r"\b", re.I)
RE_FAIBLE_EN = re.compile(
    r"\b" + AMORCE_FAIBLE_EN + r"\s+(?P<n>" + N_LATIN + r")\s+" + MOT_SEIF + r"\b", re.I)

RE_SK = re.compile(
    r"\b(?:" + AMORCE_FR + r"|" + AMORCE_EN + r")\s+(?P<n>" + N_LATIN + r")\s+"
    + MOT_SK, re.I)
RE_SK_HE = re.compile(r"(?<![א-ת])" + AMORCE_HE + r"\s+(?P<n>" + N_HEB + r")\s+ס[\"״]?ק")

# « le Chakh compte 23 ס״ק sur ce siman » — le nom, puis un verbe de dénombrement.
RE_SK_NOMME = re.compile(
    r"(?P<qui>Chakh|Shakh|ש[\"״]?ך|Taz|ט[\"״]?ז|Turei Zahav|Siftei Kohen)\s+"
    r"(?:y\s+)?(?:compte|comporte|contient|totalise|donne|counts|has|comprises|gives)\s+"
    r"(?P<n>\d{1,3}|" + "|".join(sorted(set(list(MOTS_FR) + list(MOTS_EN)),
                                        key=len, reverse=True)) + r")\s+"
    r"(?:" + MOT_SK + r"|remarques|entrées|entries)", re.I)

# ------------------------------------------ famille B : ce qu'aucune machine ne tranche

ABSOLUS = [
    # français
    (r"\bl[ae']?\s*(?:seul|seule|unique)\b", 'fr'),
    (r"\bles\s+(?:deux|trois|quatre)\s+seuls?\b", 'fr'),
    (r"\bl'un des\s+(?:deux|trois|quatre|cinq)\b", 'fr'),
    (r"\ble plus (?:long|court|bref|ancien|récent|développé)\b", 'fr'),
    (r"\bnulle part ailleurs\b", 'fr'),
    (r"\bn[e']\w*\s+qu'une\s+(?:seule\s+)?fois\b", 'fr'),
    (r"\bjamais ailleurs\b", 'fr'),
    (r"\bsans équivalent\b", 'fr'),
    (r"\bà lui seul\b", 'fr'),
    # anglais
    (r"\bthe (?:only|sole|single) \b", 'en'),
    (r"\bone of the (?:two|three|four|five)\b", 'en'),
    (r"\bthe (?:longest|shortest|oldest)\b", 'en'),
    (r"\bnowhere else\b", 'en'),
    (r"\bappears only once\b", 'en'),
    (r"\bthe only place\b", 'en'),
    # hébreu
    (r"היחיד(?:ה|י|ים)?\b", 'he'),
    (r"\bהארוך ביותר\b", 'he'),
    (r"\bהקצר ביותר\b", 'he'),
    (r"\bרק כאן\b", 'he'),
    (r"\bאין דוגמתו\b", 'he'),
]
ABSOLUS = [(re.compile(p, re.I), lg) for p, lg in ABSOLUS]

# énumérations fermées : « les trois cas », « les quatre conditions »
FERMEES = re.compile(
    r"\bles\s+(?P<n>deux|trois|quatre|cinq|six)\s+"
    r"(?P<quoi>cas|conditions|situations|exceptions|opinions|avis|raisons|critères|"
    r"hypothèses|séifim|motifs|réponses|niveaux)\b", re.I)
FERMEES_EN = re.compile(
    r"\bthe\s+(?P<n>two|three|four|five|six)\s+"
    r"(?P<quoi>cases|conditions|situations|exceptions|opinions|reasons|criteria|"
    r"grounds|answers|levels)\b", re.I)

# Un dénombrement n'est comparable au total de la source que s'il PRÉTEND être ce
# total. « les neuf séifim qui suivent » compte un sous-ensemble ; le confronter aux
# 75 séifim du siman 201 produirait un faux « FAUX ». Et « מאתיים ושמונה עשר סעיפים »
# dénombre le Aroukh HaChoulhan, pas le Choul'han Aroukh.
TOTALITE = re.compile(r"\bsiman\b|סימן|\bau total\b|\ben tout\b|\bובו\b|\bin all\b", re.I)
SOUS_ENSEMBLE = re.compile(
    r"qui suivent|qui précèdent|that follow|preceding|premiers?|derniers?|"
    r"suivants?|précédents?|\bfollowing\b|\bnext\b|"
    r"\bfirst\b|\blast\b|\bparmi\b|\bamong\b|du doute|of doubt|"
    r"ערוך השולחן|ערוה[\"״]ש|\bBeit Yosef\b|\bTour\b|\bRambam\b|רמב[\"״]ם|הטור",
    re.I)

# Une autre œuvre nommée dans la fenêtre : le nombre ne compte plus les séifim du
# Choul'han Aroukh mais les siens. Le siman 202 annonce « ses treize seifim » —
# ceux de l'Aroukh HaChoul'han.
AUTRE_OEUVRE = re.compile(
    r"Aroukh HaChoul|Arukh HaShul|ערוך השולחן|ערוה[\"״]ש|Beit Yos|Beth Yos|בית יוסף"
    r"|\bTour\b|הטור|Rambam|רמב[\"״]ם|Michné|Mishneh|Ba[\"״]h|ב[\"״]ח"
    r"|Mishnah Berurah|משנה ברורה|HaRav\b", re.I)

# Un dénombrement porté sur UN séif (« le Chakh y compte dix ס״ק » sur le séif le
# plus commenté) n'est pas le total du siman. Le singulier le trahit.
PORTEE_SEIF = re.compile(r"\bs[ée]\'?if\b|\bseif\b|(?<![א-ת])סעיף(?![א-ת])", re.I)

# Une relative restreint : « les deux séifim du siman 228 AUXQUELS le siman renvoie ».
RESTRICTION = re.compile(r"auxquels|auquel|à laquelle|to which|which|qui renvoie|dont\b", re.I)

RE_SIMAN_NOMME = re.compile(r"(?:siman|סימן)\s*(?P<n>\d{1,3})", re.I)

# Le nombre attribué au CHAPEAU n'est pas celui que la page revendique : la page
# rapporte ce que la source annonce, et — siman 164, siman 234 — c'est souvent pour
# dire dans la phrase suivante que l'édition suivie en donne un autre.
ATTRIBUE_CHAPEAU = re.compile(
    r"chapeau|כותרת|\bheading\b|\b(?:titre|title)\b|annonce|announces|proclaims|déclare", re.I)

def est_total(txt, m, exiger_totalite=True):
    fen = txt[max(0, m.start() - 70):m.end() + 70]
    # L'attribution se cherche sur la LIGNE ENTIÈRE, pas dans la fenêtre : « Titre du
    # siman : … et il comporte cinq seifim » place son attribution cent caractères plus
    # tôt. Cherchée en fenêtre, elle échappait en français et non en anglais — et le
    # contrôle rendait deux verdicts opposés sur la même phrase traduite.
    if ATTRIBUE_CHAPEAU.search(txt):
        return None
    if AUTRE_OEUVRE.search(fen) or PORTEE_SEIF.search(fen) or RESTRICTION.search(fen):
        return None
    if SOUS_ENSEMBLE.search(fen):
        return None
    # Nommer le commentateur SUFFIT à dire de quoi on parle : « le Chakh y compte
    # quarante ס״ק » n'a pas besoin du mot « siman » pour être un total. Le garde-fou
    # qui reste est PORTEE_SEIF, qui distingue le total du siman du compte d'un séif.
    if exiger_totalite and not TOTALITE.search(fen):
        return None
    # « le siman 216 va développer sur douze seifim » ne parle pas du siman de la
    # page : le nombre est celui du 216, et c'est à lui qu'il faut le confronter.
    autre = RE_SIMAN_NOMME.search(fen)
    return int(autre.group('n')) if autre else 0   # 0 = le siman de la page

# Les guillemets sont réservés au verbatim (règle du dépôt). Une citation n'affirme
# pas : elle rapporte. Le chapeau du siman 234 annonce « ובו ע״ב סעיפים » — soixante-
# douze — quand l'édition suivie en découpe soixante-quatorze ; la page le cite tel
# quel ET explique l'écart. Juger la citation, c'est reprocher à la page la source.
# Même protection, même raison qu'au siman 169 pour heb-nums.py.
CITATION = re.compile(r"«[^»]{0,600}»|\u201c[^\u201d]{0,600}\u201d")

def hors_citation(txt):
    """Rend une copie du texte où le contenu entre guillemets est blanchi."""
    return CITATION.sub(lambda m: " " * len(m.group(0)), txt)

# ---------------------------------------------------------------- source

def _cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding='utf-8'))
        except Exception:
            return {}
    return {}

def _ecrire_cache(c):
    try:
        json.dump(c, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception:
        pass

_C = _cache()

def _api(titre, n):
    cle = f"{titre}.{n}"
    if cle in _C:
        return _C[cle]
    url = f"https://www.sefaria.org/api/texts/{titre}.{n}?context=0&pad=0"
    try:
        out = subprocess.run(["curl", "-s", url], capture_output=True,
                             text=True, timeout=60).stdout
        d = json.loads(out)
    except Exception:
        return None
    he = d.get('he')
    if not isinstance(he, list):
        _C[cle] = 0
    else:
        # règle 22-bis : le décompte est la liste NON APLATIE.
        _C[cle] = len(he)
    _ecrire_cache(_C)
    return _C[cle]

TITRES = {
    'yoreh-deah': "Shulchan_Arukh,_Yoreh_De%27ah",
    'shabbat':    "Shulchan_Arukh,_Orach_Chayim",
    'orah-haim':  "Shulchan_Arukh,_Orach_Chayim",
}
APPAREIL = {
    'yoreh-deah': {'chakh': "Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De%27ah",
                   'taz':   "Turei_Zahav_on_Shulchan_Arukh,_Yoreh_De%27ah"},
}

def compartiment(path):
    for c in TITRES:
        if f"/{c}/" in path.replace(os.sep, '/'):
            return c
    return None

def numero(path):
    m = re.search(r'siman-(\d+)', path)
    return int(m.group(1)) if m else None

# ---------------------------------------------------------------- lecture

BALISE = re.compile(r'<[^>]+>')
SCRIPTS = re.compile(r'<(script|style)\b.*?</\1>', re.S | re.I)
# le texte source n'est pas jugé : il n'affirme pas, il est.
SOURCE = re.compile(r'<blockquote class="text-source".*?</blockquote>'
                    r'|<[^>]*class="[^"]*\bsa-he\b[^"]*".*?</[a-z]+>', re.S | re.I)

def lignes_visibles(path):
    brut = open(path, encoding='utf-8').read()
    brut = SCRIPTS.sub(lambda m: '\n' * m.group(0).count('\n'), brut)
    brut = SOURCE.sub(lambda m: '\n' * m.group(0).count('\n'), brut)
    for i, ligne in enumerate(brut.split('\n'), 1):
        txt = BALISE.sub(' ', ligne)
        txt = (txt.replace('&nbsp;', ' ').replace('&amp;', '&')
                  .replace('&quot;', '"').replace('&#39;', "'"))
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt:
            yield i, txt, ligne

def langue(path):
    b = os.path.basename(path)
    if b.endswith('-he.html'):
        return 'he'
    if b.endswith('-en.html'):
        return 'en'
    return 'fr'

# ---------------------------------------------------------------- analyse

def claims(path):
    """Rend la liste des affirmations de dénombrement d'une page."""
    lg = langue(path)
    out = []
    for no, txt, brut in lignes_visibles(path):
        # Famille A : ce que la page AFFIRME. Ni le verbatim entre guillemets, ni une
        # traduction — une traduction rapporte le nombre de la source, elle ne le
        # revendique pas. Le siman 234 rend son chapeau (« ע״ב », soixante-douze) dans
        # un div.translation, puis explique à la ligne suivante que l'édition suivie en
        # découpe soixante-quatorze. Le lui reprocher serait lui reprocher la source.
        nu = hors_citation(txt)
        if re.search(r'class="(?:translation|comment-source|src-ref)"', brut):
            nu = " " * len(nu)
        # Un « N ס״ק » sans nom d'auteur n'est pas vérifiable : la machine ne sait
        # pas de qui on parle. Seul le dénombrement NOMMÉ (RE_SK_NOMME) l'est.
        rxs = {'fr': [(RE_SEIFIM, 'seifim')],
               'en': [(RE_SEIFIM_EN, 'seifim')],
               'he': [(RE_SEIFIM_HE, 'seifim')]}[lg]
        for rx, quoi in rxs:
            for m in rx.finditer(nu):
                v = nombre(m.group('n'))
                if v is None or not (1 <= v <= 200):
                    continue
                cible = est_total(nu, m)
                if cible is not None:
                    out.append(dict(kind='A', quoi=quoi, valeur=v, ligne=no, siman=cible,
                                    txt=txt[max(0, m.start()-60):m.end()+60], lg=lg))
                else:
                    # dénombrement partiel : la machine ne peut pas le trancher,
                    # mais c'est exactement la forme qui était fausse au siman 234.
                    out.append(dict(kind='B', motif=m.group(0), ligne=no,
                                    txt=txt[max(0, m.start()-60):m.end()+90], lg=lg))
        for m in RE_SK_NOMME.finditer(nu):
            v = nombre(m.group('n'))
            qui = m.group('qui')
            cible = 'taz' if re.search(r'Taz|ט["״]?ז|Turei', qui) else 'chakh'
            if v is not None and 1 <= v <= 200 and est_total(nu, m, False) is not None:
                out.append(dict(kind='A', quoi=cible, valeur=v, ligne=no, siman=0,
                                txt=txt[max(0, m.start()-40):m.end()+60], lg=lg))
        for rx, lgp in ABSOLUS:
            if lgp != lg:
                continue
            for m in rx.finditer(txt):
                out.append(dict(kind='B', motif=m.group(0), ligne=no,
                                txt=txt[max(0, m.start()-80):m.end()+120], lg=lg))
        for rx in ({'fr': RE_FAIBLE_FR, 'en': RE_FAIBLE_EN}.get(lg) or RE_FAIBLE_FR,) \
                  if lg in ('fr', 'en') else ():
            for m in rx.finditer(nu):
                if nombre(m.group('n')) is not None:
                    out.append(dict(kind='B', motif=m.group(0), ligne=no,
                                    txt=txt[max(0, m.start()-60):m.end()+90], lg=lg))
        for rx in (FERMEES, FERMEES_EN):
            for m in rx.finditer(txt):
                out.append(dict(kind='B', motif=m.group(0), ligne=no,
                                txt=txt[max(0, m.start()-60):m.end()+140], lg=lg))
    return out

def verifier(dossier, bref=False):
    comp = compartiment(dossier)
    n = numero(dossier)
    faux, desaccords, candidats = [], [], []
    confrontes = 0
    vrais = {}
    if comp and n:
        vrais['seifim'] = _api(TITRES[comp], n)
        if comp in APPAREIL:
            for k, t in APPAREIL[comp].items():
                vrais[k] = _api(t, n)

    par_niveau = {}
    for path in sorted(glob.glob(os.path.join(dossier, '*.html'))):
        base = re.sub(r'(-he|-en)?\.html$', '', os.path.basename(path))
        cs = claims(path)
        par_niveau.setdefault(base, []).append((path, cs))
        for c in cs:
            if c['kind'] == 'B':
                candidats.append((path, c))
                continue
            if c.get('siman'):
                if not comp:
                    continue
                attendu = (_api(TITRES[comp], c['siman']) if c['quoi'] == 'seifim'
                           else _api(APPAREIL.get(comp, {}).get(c['quoi'], ''), c['siman']))
            else:
                attendu = vrais.get(c['quoi'])
            if attendu in (None, 0):
                continue
            confrontes += 1
            if c['valeur'] != attendu:
                faux.append((path, c, attendu))

    # désaccord trilingue sur un même niveau
    for base, entrees in par_niveau.items():
        vus = {}
        for path, cs in entrees:
            for c in cs:
                if c['kind'] != 'A':
                    continue
                vus.setdefault(c['quoi'], {}).setdefault(c['lg'], set()).add(c['valeur'])
        for quoi, parlangue in vus.items():
            valeurs = {lg: sorted(v) for lg, v in parlangue.items()}
            distinctes = {tuple(v) for v in valeurs.values()}
            if len(valeurs) > 1 and len(distinctes) > 1:
                desaccords.append((os.path.join(dossier, base), quoi, valeurs))
    return faux, desaccords, candidats, confrontes

# ---------------------------------------------------------------- main

def main():
    args = sys.argv[1:]
    bref = '--bref' in args
    montrer = '--a-verifier' in args
    args = [a for a in args if not a.startswith('--') or a == '--path']
    cible = None
    if '--path' in sys.argv:
        cible = sys.argv[sys.argv.index('--path') + 1]

    if cible:
        racines = ([cible] if os.path.basename(cible).startswith('siman-')
                   else sorted(glob.glob(os.path.join(cible, 'siman-*'))))
    else:
        racines = sorted(glob.glob(os.path.join(ROOT, 'sources', '*', 'siman-*')))

    tot_faux = tot_des = tot_cand = tot_conf = 0
    for d in racines:
        faux, des, cand, conf = verifier(d)
        tot_faux += len(faux); tot_des += len(des); tot_cand += len(cand)
        tot_conf += conf
        nom = os.path.relpath(d, ROOT)
        for path, c, attendu in faux:
            print(f"FAUX       {os.path.relpath(path, ROOT)}:{c['ligne']} — "
                  f"annonce {c['valeur']} {c['quoi']}, la source en donne {attendu}")
            print(f"           … {c['txt']}")
        for base, quoi, valeurs in des:
            print(f"DÉSACCORD  {os.path.relpath(base, ROOT)} — {quoi} : "
                  + " / ".join(f"{lg}={v}" for lg, v in sorted(valeurs.items())))
        if montrer:
            for path, c in cand:
                print(f"À VÉRIFIER {os.path.relpath(path, ROOT)}:{c['ligne']} "
                      f"[{c['lg']}] « {c['motif']} »")
                if not bref:
                    print(f"           … {c['txt']}")

    print()
    print(f"Simanim examinés   : {len(racines)}")
    print(f"Confrontés         : {tot_conf}   (dénombrements réellement comparés "
          f"à la source)")
    print(f"FAUX               : {tot_faux}")
    print(f"DÉSACCORD          : {tot_des}")
    print(f"À VÉRIFIER         : {tot_cand}"
          + ("" if montrer else "   (--a-verifier pour les lister)"))
    print()
    print("Rappel : « À VÉRIFIER » n'est pas un défaut — c'est une phrase que seule")
    print("une lecture peut trancher. Les deux autres verdicts, si, et font sortir en 1.")
    return 1 if (tot_faux or tot_des) else 0

if __name__ == '__main__':
    sys.exit(main())
