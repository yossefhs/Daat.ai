#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garde-fou de cohérence interne — les niveaux d'un siman se contredisent-ils ?

Trois simanim corrigés en septembre 2026 — 288, 289, 290 — partagent une même
signature, et aucune des portes existantes ne pouvait la voir : **un niveau de
la page portait déjà la bonne réponse pendant qu'un autre en publiait une
fausse**. Aucune citation n'était inventée, la langue était juste, la structure
conforme ; c'est la couche pédagogique qui s'écartait de ce que la page
elle-même savait ailleurs.

Au siman 290, le niveau 2 attribuait la baraïta des cent berakhot à רבי מאיר —
ce qui est exact — pendant que les niveaux 1 et 3 l'attribuaient à David
HaMelekh, avec la MÊME référence, מנחות מ״ג ע״ב. Et le niveau 2 calculait
« חיסור: כ-29 ברכות » pendant que les niveaux 1 et 3 annonçaient « ≈ 18-22 »,
à partir des mêmes opérandes.

D'où deux détecteurs, tous deux sans interprétation :

**1. Attributions divergentes.** Pour chaque référence talmudique citée dans un
siman — le daf, en hébreu comme en translittération —, on relève les noms
propres qui l'accompagnent, niveau par niveau. Deux niveaux qui attachent à la
même référence des noms DISJOINTS se contredisent, et l'un des deux se trompe.

**2. Le nom figure-t-il dans le daf ?** — DÉSACTIVÉ par défaut, `--noms-dans-daf`
pour l'appeler. L'idée est juste : quand deux niveaux portent la même erreur ils
s'accordent, le premier détecteur se tait, et confronter le nom au texte réel de
la guemara reste le seul recours. Mais sur ce corpus il crie au loup. Les pages
tissent plusieurs références et plusieurs noms dans un même paragraphe, tantôt
« référence : "citation" », tantôt « "citation" (référence) », et rattacher
chaque nom à la bonne référence relève de la lecture, pas de la mesure. Dix
candidats ont été vérifiés un par un, en ouvrant chaque daf : **la page avait
raison dans les dix cas**. On le garde parce qu'il vaut pour un nom rare et une
page sobre ; on ne l'impose pas.

**3. Arithmétique fausse.** Toute opération écrite en toutes lettres — « 4 × 7
= 28 » — est vérifiée. Et lorsqu'un passage pose deux résultats puis annonce un
écart, l'écart est confronté à la différence des deux.

**Ce qu'il a trouvé, et ce qu'il ne voit pas.** Validé sur le siman 290 tel
qu'il était avant sa correction : deux contradictions d'attribution et deux
calculs démentis, zéro une fois corrigé. Il a ensuite trouvé, sur des pages
publiées, deux « ≈ 20 » résiduels au siman 290 qu'une correction manuelle avait
manqués, la mahloket de שבת ס״ט ע״ב attribuée à Rava au lieu de חייא בר רב au
siman 344, et deux mentions de « מחלוקת רב ושמואל » au siman 324 que le lien
intra-ref coupait en deux et qui échappaient à toute recherche.

Ses angles morts sont connus et il vaut mieux les avoir en tête :
  · un nom court comme דוד figure dans les versets cités par le daf, si bien
    que le test « ce nom est-il sur cette page » ne peut rien conclure de lui ;
  · un nom placé entre deux références va à la plus proche, ce qui est le bon
    choix la plupart du temps et le mauvais quand la page cite longuement ;
  · la soustraction n'est pas contrôlée du tout, le tiret servant ici de
    séparateur de liste ;
  · et quand DEUX niveaux portent la même erreur, ils s'accordent : le premier
    détecteur se tait, et seul le troisième peut encore parler.

Le contrôle produit des CANDIDATS, jamais des verdicts : il dit que deux pages
ne disent pas la même chose, pas laquelle a raison. C'est au relecteur, et pour
la substance halakhique au Rav, de trancher.

    python3 scripts/verifier-coherence.py [--section shabbat] [--siman N …]
"""
import argparse, collections, pathlib, re, sys

SITE = pathlib.Path(__file__).resolve().parent.parent
RE_TAG = re.compile(r"<[^>]+>")

# ── Les massekhtot, dans les deux écritures ────────────────────────────────
MASSEKHET_HE = {
    "ברכות": "Berakhot", "שבת": "Shabbat", "עירובין": "Eruvin", "פסחים": "Pesachim",
    "יומא": "Yoma", "סוכה": "Sukkah", "ביצה": "Beitzah", "ראש השנה": "RoshHashanah",
    "תענית": "Taanit", "מגילה": "Megillah", "מועד קטן": "MoedKatan", "חגיגה": "Chagigah",
    "יבמות": "Yevamot", "כתובות": "Ketubot", "נדרים": "Nedarim", "נזיר": "Nazir",
    "סוטה": "Sotah", "גיטין": "Gittin", "קידושין": "Kiddushin", "בבא קמא": "BavaKamma",
    "בבא מציעא": "BavaMetzia", "בבא בתרא": "BavaBatra", "סנהדרין": "Sanhedrin",
    "מכות": "Makkot", "שבועות": "Shevuot", "עבודה זרה": "AvodahZarah",
    "הוריות": "Horayot", "זבחים": "Zevachim", "מנחות": "Menachot", "חולין": "Chullin",
    "בכורות": "Bekhorot", "ערכין": "Arakhin", "תמורה": "Temurah", "כריתות": "Keritot",
    "מעילה": "Meilah", "נדה": "Niddah",
}
MASSEKHET_LAT = {
    "berakhot": "Berakhot", "berachos": "Berakhot", "berachot": "Berakhot",
    "shabbat": "Shabbat", "shabbos": "Shabbat", "chabbat": "Shabbat",
    "eruvin": "Eruvin", "erouvin": "Eruvin", "eiruvin": "Eruvin",
    "pesahim": "Pesachim", "pesachim": "Pesachim", "pessahim": "Pesachim",
    "menahot": "Menachot", "menachot": "Menachot", "menachos": "Menachot",
    "sukkah": "Sukkah", "souka": "Sukkah", "beitzah": "Beitzah", "yoma": "Yoma",
    "megillah": "Megillah", "meguila": "Megillah", "taanit": "Taanit",
    "hagigah": "Chagigah", "chagigah": "Chagigah", "ketubot": "Ketubot",
    "guittin": "Gittin", "gittin": "Gittin", "kiddushin": "Kiddushin",
    "sanhedrin": "Sanhedrin", "houlin": "Chullin", "chullin": "Chullin",
    "avodah zarah": "AvodahZarah", "nidda": "Niddah", "niddah": "Niddah",
    "yevamot": "Yevamot", "sotah": "Sotah", "nedarim": "Nedarim",
    "bava kamma": "BavaKamma", "bava metzia": "BavaMetzia", "bava batra": "BavaBatra",
}

_UNITES = {c: i + 1 for i, c in enumerate("אבגדהוזחט")}
_DIZAINES = {"י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60, "ע": 70, "פ": 80, "צ": 90}
_CENTAINES = {"ק": 100, "ר": 200, "ש": 300, "ת": 400}


def gematria(s):
    """« מ״ג » → 43. Rend None si ce n'est pas un nombre-lettres."""
    s = re.sub(r"[״\"׳']", "", s)
    n = 0
    for c in s:
        if c in _CENTAINES: n += _CENTAINES[c]
        elif c in _DIZAINES: n += _DIZAINES[c]
        elif c in _UNITES: n += _UNITES[c]
        else: return None
    return n or None


RE_DAF_HE = re.compile(
    r"(?P<mas>" + "|".join(sorted(MASSEKHET_HE, key=len, reverse=True)) + r")\s*"
    # « עירובין דף מ״ו ע״א » : sans cette option, « דף » était lu comme le
    # nombre-lettres et donnait le daf 84, une référence qui n'existe pas.
    r"(?:דף\s*)?"
    r"\(?(?P<daf>[א-ת]{1,4}[״\"׳']?[א-ת]?)\s*ע[״\"׳']?(?P<amud>[אב])")
RE_DAF_LAT = re.compile(
    r"\b(?P<mas>" + "|".join(sorted(MASSEKHET_LAT, key=len, reverse=True)) + r")\s+"
    r"(?P<daf>\d{1,3})(?P<amud>[ab])\b", re.I)

# ── Les noms qui portent une attribution ───────────────────────────────────
NOMS = [
    "רבי מאיר", "רבי עקיבא", "רבי יהודה", "רבי יוסי", "רבי יוחנן", "רבי אליעזר",
    "רבי שמעון", "רבן גמליאל", "רבי חייא", "רב חייא", "רב הונא", "רב חסדא",
    "רב נחמן", "רב יהודה", "רב אשי", "רב ששת", "רב פפא", "רב כהנא", "רב זירא",
    "שמואל", "רבא", "אביי", "רבה", "דוד המלך", "רש״י", "רשב״ם", "המאירי",
    "מאירי", "תוספות", "הרמב״ם", "רמב״ם", "הרא״ש", "הרי״ף", "רב נטרונאי",
    "Rabbi Meïr", "Rabbi Meir", "Rabbi Akiva", "Rabbi Yehouda", "Rabbi Yohanan",
    "David Hamélékh", "David HaMelekh", "Dovid HaMelech", "Chmouel", "Shmuel",
    "Rava", "Abaye", "Rabba", "Rashi", "Rachi", "Rashbam", "Meiri", "Méiri",
    "Rambam", "Rosh", "Rif", "Rav Netronaï", "Rav Netronai",
    "Shemuel", "Chemouel", "Rachbam", "Rabbi Chimon", "רבי שמעון",
    "רב הונא", "Rav Houna", "Rav Huna", "חייא בר רב", "Chiya bar Rav",
    "רבן שמעון בן גמליאל", "רשב״ג",
]
# « רב » seul est trop court pour être cherché tel quel : il est dans « רבא »,
# « רבה », « רבי »… On le prend seulement en tête de citation, « אמר רב ».
# « Rabba » et « רבה » sont le même homme. Sans cette table, toute page qui
# nomme un amora en français d'un côté et en hébreu de l'autre se dénoncerait
# elle-même : c'était le cas de neuf des douze premiers signalements.
CANON = {
    "רבי מאיר": "R. Meir", "Rabbi Meïr": "R. Meir", "Rabbi Meir": "R. Meir",
    "רבי עקיבא": "R. Akiva", "Rabbi Akiva": "R. Akiva",
    "רבי יהודה": "R. Yehuda", "Rabbi Yehouda": "R. Yehuda",
    "רבי יוחנן": "R. Yohanan", "Rabbi Yohanan": "R. Yohanan",
    "דוד המלך": "David", "David Hamélékh": "David", "David HaMelekh": "David",
    "Dovid HaMelech": "David",
    "שמואל": "Shmuel", "Chmouel": "Shmuel", "Shmuel": "Shmuel",
    "רבא": "Rava", "Rava": "Rava", "רבה": "Rabba", "Rabba": "Rabba",
    "אביי": "Abaye", "Abaye": "Abaye",
    "רש״י": "Rashi", "Rashi": "Rashi", "Rachi": "Rashi",
    "רשב״ם": "Rashbam", "Rashbam": "Rashbam",
    "המאירי": "Meiri", "מאירי": "Meiri", "Meiri": "Meiri", "Méiri": "Meiri",
    "הרמב״ם": "Rambam", "רמב״ם": "Rambam", "Rambam": "Rambam",
    "הרא״ש": "Rosh", "Rosh": "Rosh", "הרי״ף": "Rif", "Rif": "Rif",
    "רב נטרונאי": "Netronai", "Rav Netronaï": "Netronai", "Rav Netronai": "Netronai",
    "תוספות": "Tosafot",
    "Shemuel": "Shmuel", "Chemouel": "Shmuel", "Rachbam": "Rashbam",
    "רבי שמעון": "R. Shimon", "Rabbi Chimon": "R. Shimon",
    "רב הונא": "Rav Huna", "Rav Houna": "Rav Huna", "Rav Huna": "Rav Huna",
    "חייא בר רב": "Chiya b. Rav", "Chiya bar Rav": "Chiya b. Rav",
    "רבן שמעון בן גמליאל": "Rashbag", "רשב״ג": "Rashbag",
}


def canon(n):
    return CANON.get(n, n)


RE_NOMS = re.compile("|".join(re.escape(n) for n in sorted(NOMS, key=len, reverse=True)))
RE_RAV_SEUL = re.compile(r"אמר רב(?![א-ת])")
# « רבה » vit aussi dans « קידושא רבה », « הגדה רבה », « ברכה רבה » — où il ne
# nomme personne. Ces deux-là ne sont retenus que si un verbe d'attribution les
# accompagne. Sans cette garde, le siman 273 se dénonçait pour un « קידושא רבה »
# cité en passant.
AMBIGUS = {"רבה", "רבא"}
# « רבה » vit aussi dans « הַרְבֵּה » — beaucoup —, mot on ne peut plus courant :
# « שהצבור מקדימים הרבה לפני הלילה » a fait dénoncer le siman רל״ה. Ces noms-là
# doivent donc COMMENCER un mot, préfixe hébreu compris.
RE_LETTRE = re.compile(r"[א-ת]")
def attribue(fen, nom):
    return bool(re.search(
        r"(?:אמר|סבר|אומר|שיטת|דעת|מחלוקת|לדעת)\s+ה?" + nom + r"(?![א-ת])"
        r"|" + nom + r"\s+(?:אמר|סבר|אומר)"
        r"|[כדו]" + nom + r"(?![א-ת])", fen))

# ── Le troisième détecteur : le nom figure-t-il dans le daf ? ──────────────
# Comparer les niveaux entre eux ne suffit pas : quand DEUX niveaux portent la
# même erreur, ils s'accordent et le contrôle se tait. On confronte donc chaque
# nom talmudique au texte réel du daf. Les commentateurs en sont exclus : Rachi
# commente légitimement une page où il ne figure pas.
# On cherche le nom DISTINCTIF, non la formule complète : le daf écrit tantôt
# « רבי עקיבא », tantôt « ר׳ עקיבא », tantôt l'abrège, et exiger la formule
# entière faisait dire « absent » d'un homme présent — c'est arrivé au siman 331,
# où « עקיבא » figure bel et bien dans שבת קל״ב.
TALMUDIQUES = {
    "R. Meir": ["מאיר"], "R. Akiva": ["עקיבא"], "R. Yehuda": ["יהודה"],
    "R. Yohanan": ["יוחנן"], "R. Shimon": ["שמעון"], "David": ["דוד"],
    "Shmuel": ["שמואל"], "Rava": ["רבא"], "Rabba": ["רבה"], "Abaye": ["אביי"],
    "Rav Huna": ["הונא"], "Chiya b. Rav": ["חייא"],
    "Rashbag": ["רבן שמעון בן גמליאל", "רשב״ג"],
}
_DAPIM = {}


RE_DIT = "|".join(("אמר", "אומר", "אומרים", "סבר", "דאמר", "תני", "תניא"))


def parlant(par_niveau, cle, nom):
    """La page fait-elle PARLER ce nom, ou se contente-t-elle de le nommer ?"""
    formes = TALMUDIQUES.get(nom, [nom])
    for t in par_niveau.values():
        for f in formes:
            for m in re.finditer(re.escape(f), t):
                fen = t[max(0, m.start() - 30):m.end() + 30]
                if re.search(r"(?:" + RE_DIT + r")\s+\S{0,12}" + re.escape(f), fen) \
                   or re.search(re.escape(f) + r"\s+(?:" + RE_DIT + r")", fen):
                    return True
    return False


def texte_du_daf(cle):
    """Le texte hébreu du daf, via Sefaria, mémorisé pour la durée du contrôle."""
    if cle in _DAPIM:
        return _DAPIM[cle]
    mas, daf = cle.rsplit(" ", 1)
    try:
        import json, urllib.request, unicodedata
        u = f"https://www.sefaria.org/api/texts/{mas}.{daf}?context=0&pad=0"
        d = json.load(urllib.request.urlopen(u, timeout=30))
        def plat(x):
            if isinstance(x, str):
                return [x]
            out = []
            for y in (x or []):
                out += plat(y)
            return out
        s = " ".join(plat(d.get("he")))
        s = unicodedata.normalize("NFKD", RE_TAG.sub(" ", s))
        s = "".join(c for c in s if not unicodedata.combining(c))
        _DAPIM[cle] = re.sub(r"\s+", " ", s)
    except Exception:
        _DAPIM[cle] = None          # daf injoignable : on s'abstient
    return _DAPIM[cle]


NIVEAUX = {"niveau-1-base": "niveau 1", "niveau-2-lamdan": "niveau 2",
           "niveau-3-synthese": "niveau 3", "niveau-4-daat-harav": "niveau 4",
           "niveau-4-halakha": "niveau 4"}
FENETRE = 220


RE_CITATION = re.compile(r"«[^«»]{10,600}»|\"[^\"]{10,600}\"|״[^״]{10,600}״")
RE_ABREV = re.compile(r"ר[״\"׳']\s*(?=[א-ת])")


def normaliser(t):
    """« ר׳ מאיר » et « ר' מאיר » sont le même nom que « רבי מאיר ».

    Le dépôt écrit l'abréviation aussi souvent que le nom plein — c'est elle
    qui figure dans le niveau 2 du siman 290, et sans cette normalisation le
    contrôle n'y voyait aucun nom, donc aucune contradiction.
    """
    return RE_ABREV.sub("רבי ", t)


def texte(p):
    return normaliser(re.sub(r"\s+", " ", RE_TAG.sub(" ", p.read_text(encoding="utf-8"))))


def refs_et_noms(t):
    """{référence canonique : ensemble des noms qui l'entourent}.

    Chaque nom est attribué à la référence la PLUS PROCHE, et à elle seule.
    Le partager entre les deux références qui l'encadrent faisait dire au
    contrôle que « רבי מאיר » est attribué à שבת י״ב ע״ב, alors que la page
    l'attribue à שבת י״ב ע״א deux lignes plus haut, et cite le ע״ב pour
    רבי יהודה. C'est la même mécanique qui rattachait « שמואל », dit d'une
    guemara de ביצה, à la référence de שבת qui suivait.
    """
    reperes = []
    for m in RE_DAF_HE.finditer(t):
        d = gematria(m.group("daf"))
        if not d or d > 180:
            continue
        reperes.append((m.start(), m.end(),
                        f"{MASSEKHET_HE[m.group('mas')]} {d}{'a' if m.group('amud') == 'א' else 'b'}"))
    for m in RE_DAF_LAT.finditer(t):
        reperes.append((m.start(), m.end(),
                        f"{MASSEKHET_LAT[m.group('mas').lower()]} {int(m.group('daf'))}{m.group('amud').lower()}"))
    reperes.sort()
    out = collections.defaultdict(set)
    for cle in {c for _, _, c in reperes}:
        out[cle] = set()
    if not reperes:
        return out

    occurrences = [(m.start(), m.group(0)) for m in RE_NOMS.finditer(t)]
    occurrences += [(m.start() + 4, "רב") for m in RE_RAV_SEUL.finditer(t)]
    # Le dépôt écrit tantôt « référence : "citation" », tantôt « "citation"
    # (référence) ». La règle qui vaut dans les deux cas : le nom appartient à
    # la référence qui BORDE SA CITATION. On repère donc le passage entre
    # guillemets qui contient le nom, et on regarde ce qui le jouxte — après
    # d'abord, avant ensuite. Hors de toute citation, on retombe sur la plus
    # proche. Prendre bêtement la plus proche rattachait « ואמר רבא … (ברכות
    # נ׳ ע״א) » à la référence citée deux lignes plus haut.
    guillemets = [(m.start(), m.end()) for m in RE_CITATION.finditer(t)]

    def citation_de(pos):
        for a, b in guillemets:
            if a <= pos < b:
                return a, b
        return None

    for pos, nom in occurrences:
        borne = citation_de(pos)
        choisi = None
        if borne:
            a, b = borne
            apres = [r for r in reperes if r[0] >= b and r[0] - b <= 60]
            avant = [r for r in reperes if r[1] <= a and a - r[1] <= 60]
            choisi = apres[0] if apres else (avant[-1] if avant else None)
        if choisi is None:
            proches = [r for r in reperes
                       if min(abs(pos - r[0]), abs(pos - r[1])) <= FENETRE]
            if not proches:
                continue
            choisi = min(proches, key=lambda r: min(abs(pos - r[0]), abs(pos - r[1])))
        i, j, cle = choisi
        # Frontière de mot, des deux côtés et dans les deux écritures :
        # « Rabban Gamliel » contient « Rabba », et « הַרְבֵּה » contient « רבה ».
        # Les deux ont fait dénoncer le siman רל״ה, où la page ne nomme aucun
        # amora de ce nom.
        suivant = t[pos + len(nom):pos + len(nom) + 1]
        if pos and RE_LETTRE.match(t[pos - 1]) or (pos and t[pos - 1].isalpha()):
            continue
        if suivant.isalpha() and not RE_LETTRE.match(suivant):
            continue
        fen = t[max(0, pos - 40):pos + len(nom) + 40]
        if nom in AMBIGUS and not attribue(fen, nom):
            continue
        out[cle].add(nom)

    # On ne garde que les noms maximaux : « רבי מאיר » absorbe « רבי ».
    for cle, noms in out.items():
        maximaux = {n for n in noms if not any(n != a and n in a for a in noms)}
        out[cle] = {canon(n) for n in maximaux}
    return out


# Les pages écrivent leurs calculs en toutes lettres — « 7 brakhot × 4 tefillot
# = 28 » — et non en algèbre. On tolère donc des mots entre les opérandes, mais
# jamais un autre chiffre ni un autre « = », ce qui garde la lecture locale.
_MOTS = r"[^\d=×✕*+]{0,25}?"
RE_MUL = re.compile(r"(\d{1,4})\s*" + _MOTS + r"[×✕*]\s*(\d{1,4})\s*" + _MOTS + r"=\s*(\d{1,5})")
# Les sommes se lisent en entier : « 2+1+12 = 15 » a trois termes, et n'en lire
# que deux faisait dénoncer un calcul juste.
RE_SOMME = re.compile(r"(\d{1,4}(?:\s*\+\s*\d{1,4}){1,8})\s*" + _MOTS + r"=\s*(\d{1,5})")
# La soustraction n'est PAS contrôlée : le tiret sert ici de séparateur de liste
# — « כריכות 7-9-11-13 = 40 » énumère quatre nombres dont la somme fait bien 40 —
# et le distinguer d'un vrai signe moins demanderait de deviner l'intention.
RE_ECART = re.compile(
    # La fenêtre ne franchit ni ponctuation forte ni tiret : « manque-t-il ?
    # Quels sont les 3 » n'est pas un écart annoncé de 3.
    r"\b(?:déficit|manque|écart|shortfall|חסרון|חיסור)\b[^.;:?!—-]{0,40}?"
    r"(?:≈|environ|about|around|כ-)?\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?", re.I)


def arithmetique(t, ou):
    """Les opérations écrites, et les écarts annoncés qui ne suivent pas."""
    signalements = []
    for m in RE_MUL.finditer(t):
        a, b, c = (int(x) for x in m.groups())
        if a * b != c:
            signalements.append(f"{ou} : {a} × {b} = {c} — or {a} × {b} = {a * b}")
    for m in RE_SOMME.finditer(t):
        termes = [int(x) for x in re.findall(r"\d{1,4}", m.group(1))]
        c = int(m.group(2))
        if sum(termes) != c:
            ecrit = " + ".join(str(x) for x in termes)
            signalements.append(f"{ou} : {ecrit} = {c} — or la somme fait {sum(termes)}")
    # Un passage qui pose deux résultats puis annonce un écart.
    resultats = [int(m.group(3)) for m in RE_MUL.finditer(t)]
    if len(resultats) >= 2:
        vrai = abs(resultats[0] - resultats[1])
        for m in RE_ECART.finditer(t):
            bornes = [int(x) for x in m.groups() if x]
            # Un écart ne peut pas excéder la plus grande des deux quantités
            # qu'il sépare : « déficit des 100 berakhot » nomme la cible, pas
            # le manque, et n'est donc pas un calcul à vérifier.
            if bornes and max(bornes) > max(resultats):
                continue
            if bornes and not (min(bornes) <= vrai <= max(bornes)):
                annonce = "-".join(str(b) for b in bornes)
                signalements.append(
                    f"{ou} : écart annoncé {annonce}, mais les opérandes de la page"
                    f" donnent |{resultats[0]} − {resultats[1]}| = {vrai}")
    # Le même écart réapparaît souvent d'un paragraphe à l'autre ; on ne le dit
    # qu'une fois, sans quoi le lot se compte en doublons.
    return list(dict.fromkeys(signalements))


def verifier(section, numeros=None, noms_dans_daf=False):
    base = SITE / "sources" / section
    contradictions = fautes = absents = simanim = 0
    for d in sorted(base.glob("siman-*"), key=lambda p: int(p.name.split("-")[1])):
        n = int(d.name.split("-")[1])
        if numeros and n not in numeros:
            continue
        simanim += 1
        par_niveau = {}
        for stem, nom in NIVEAUX.items():
            p = d / f"{stem}.html"
            if p.exists():
                par_niveau[nom] = texte(p)

        # 1 — attributions divergentes
        vus = collections.defaultdict(dict)
        for nom, t in par_niveau.items():
            for cle, noms in refs_et_noms(t).items():
                if noms:
                    vus[cle][nom] = noms
        for cle, parlants in sorted(vus.items()):
            # On ne confronte que des noms de MÊME NATURE. Un niveau qui nomme
            # l'amora et un autre qui nomme le Richon qui le commente ne se
            # contredisent pas — ils parlent de deux choses. Sans ce filtre,
            # Yoré Déa sortait 62 candidats, presque tous de cette forme.
            parlants = {k: v & set(TALMUDIQUES) for k, v in parlants.items()}
            parlants = {k: v for k, v in parlants.items() if v}
            for a, b in ((x, y) for x in parlants for y in parlants if x < y):
                if not (parlants[a] & parlants[b]):
                    contradictions += 1
                    print(f"siman {n} · {cle}")
                    print(f"    {a} : {', '.join(sorted(parlants[a]))}")
                    print(f"    {b} : {', '.join(sorted(parlants[b]))}")

        # 1 bis — le nom figure-t-il dans le daf qu'on lui attribue ?
        for cle, parlants in (sorted(vus.items()) if noms_dans_daf else ()):
            # On ne retient que les noms que la page fait PARLER dans ce daf :
            # « אמר X », « X אומר », « דאמר X ». Nommer quelqu'un près d'une
            # référence n'est pas la lui attribuer — la page peut citer Tossafot
            # qui discute son avis, ou un midrash qui le met en scène. Sans ce
            # resserrement le détecteur sortait vingt-cinq candidats dont aucun
            # n'était une erreur : la page avait raison à chaque fois.
            noms = {n for n, d in parlants.items() for n in d} if False else set().union(*parlants.values())
            cherchables = {n for n in noms if n in TALMUDIQUES and parlant(par_niveau, cle, n)}
            if not cherchables:
                continue
            daf = texte_du_daf(cle)
            if not daf:
                continue
            for nom in sorted(cherchables):
                if not any(f in daf for f in TALMUDIQUES[nom]):
                    ou = ", ".join(sorted(k for k, v in parlants.items() if nom in v))
                    absents += 1
                    print(f"siman {n} · {cle} — « {nom} » ne figure pas dans ce daf ({ou})")

        # 2 — arithmétique
        for nom, t in par_niveau.items():
            for s in arithmetique(t, f"siman {n} · {nom}"):
                fautes += 1
                print(s)

    print(f"\n{simanim} siman(im) examiné(s) dans {section}")
    print(f"→ {contradictions} référence(s) attribuée(s) différemment d'un niveau à l'autre")
    if noms_dans_daf:
        print(f"→ {absents} nom(s) attribué(s) à un daf où il ne figure pas")
    print(f"→ {fautes} calcul(s) que la page dément elle-même")
    return 1 if (contradictions or absents or fautes) else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--section", default="shabbat")
    ap.add_argument("--siman", type=int, nargs="*")
    ap.add_argument("--noms-dans-daf", action="store_true",
                    help="ajouter le détecteur 2 — peu précis, voir l'en-tête")
    a = ap.parse_args()
    sys.exit(verifier(a.section, set(a.siman) if a.siman else None, a.noms_dans_daf))
