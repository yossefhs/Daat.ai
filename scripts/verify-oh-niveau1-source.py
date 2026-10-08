#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garde-fou de recopie du NIVEAU 1 d'Orah Haïm — le texte source donné au
lecteur est-il le Choul'han Aroukh, tout le Choul'han Aroukh, et rien d'autre ?

  python3 scripts/verify-oh-niveau1-source.py 8 32 128
  python3 scripts/verify-oh-niveau1-source.py --tous            # les 241
  python3 scripts/verify-oh-niveau1-source.py --tous --bref     # une ligne par siman
  python3 scripts/verify-oh-niveau1-source.py --tous --rafraichir   # ignore le cache

Codes de sortie : 0 conforme · 1 divergence au-delà du ktiv · 3 RIEN n'a pu être
confronté, ou une partie des simanim demandés n'a pas été atteinte alors que le
reste est conforme (la porte ne conclut pas sur ce qu'elle n'a pas lu) · 2 usage.

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
concaténation des séifim de ``Shulchan_Arukh,_Orach_Chayim.N`` (api/texts, la
version ``he`` par défaut — Maginei Eretz, Lemberg 1893), sur les CONSONNES :
nikoud, ponctuation, balises et ancres ``<i data-commentator>`` retirés ; le
chapeau du siman (« דין … ובו ט סעיפים ») facultatif ; deux verdicts, IDENTIQUE et
ÉQUIVALENT (égal aux matres lectionis près, le ktiv haser/malé étant le faux
positif dominant) ; la parité FR/HE/EN du texte source.

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
  ALTÉRATION          des mots changés : abréviation de l'imprimé développée
                      (וי״א → ויש אומרים, הקב״ה → הקדוש ברוך הוא — c'est ce qui a
                      fait échouer les 50 premiers simanim de Yoré Déa, et c'est un
                      vrai défaut de recopie, pas un faux positif), parenthèse de
                      source omise (« (טור) »), mot omis, mot remplacé.

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
                      confrontée à son tour, et ses mots étrangers à la source
                      sont une ALTÉRATION.

COMMENT : un alignement au MOT, non au caractère. Les deux textes sont découpés en
mots ; chaque mot est comparé par son squelette (consonnes sans yod ni vav, SAUF
l'initiale : le ktiv ne touche jamais la première lettre, le vav de conjonction
si) ; un alignement monotone (difflib) apparie la page à la source ; puis une
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
- un renvoi de source entre parenthèses n'est jamais une TRONCATURE du din.

MESURE DU 8 OCTOBRE 2026 — les 241 simanim, 1 453 séifim, 723 pages
------------------------------------------------------------------
73 simanim IDENTIQUES, 7 ÉQUIVALENTS, 161 divergents (le pire des trois pages :
14 ABSENT NON DÉCLARÉ, 1 ABSENT DÉCLARÉ, 56 TRONCATURE, 90 ALTÉRATION). Par séif,
chacun compté une fois sous son pire défaut : 609 conformes au ktiv près, 98
absents non déclarés (dont 66 ANNONCÉS par le titre de leur bloc), 41 absents
déclarés (le seul siman 32), 201 tronqués, 13 déplacés, 491 altérés. Parité
FR/HE/EN rompue dans 5 simanim (8, 10, 98, 128, 162) ; au siman 10, la page
FRANÇAISE seule omet la condition du séif ו, « אא״כ תפרה כולה ואפי׳ מרוח
אחת ». Les simanim 185 à 241 sont tous identiques ou équivalents.

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
139 au lieu de 133.

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
  sort en 3, elle ne passe pas pour verte.
"""
import argparse, difflib, html, importlib.util, json, os, re, sys, unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION = os.path.join(ROOT, "sources", "orah-haim")
CACHE = os.path.join(ROOT, "scripts", ".cache-sefaria", "recopie-oh-niveau1")
LIVRE = "Shulchan_Arukh,_Orach_Chayim"
LANGS = [("FR", ""), ("HE", "-he"), ("EN", "-en")]

TRONC_MIN = 4          # mots consécutifs absents au-delà desquels on parle de troncature
DEPLACE_SEUIL = 0.5    # part du séif retrouvée hors de sa place pour le dire DÉPLACÉ
ILOT_MAX = 2           # un îlot de 1-2 mots appariés au milieu d'un trou est du bruit

# Une page qui dit au lecteur qu'elle ne donne qu'une partie du siman. Même motif
# que verifier-couverture-encadres.py, pour que les deux comptes se comparent.
RE_DECL = re.compile(r'repr[ée]sentatif|s[ée]lection|extraits choisis|נציג|representative', re.I)
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


class Mot:
    __slots__ = ("lettres", "cle", "abrev", "rama", "chapeau", "ref", "seif",
                 "bloc", "deb", "fin", "brut")

    def __init__(self, brut, **kw):
        self.brut = brut
        self.lettres = re.sub(r"[^א-ת]", "", brut)
        # La clé de comparaison : le squelette, SAUF la première lettre. Le ktiv
        # haser/malé ne touche jamais l'initiale d'un mot ; le vav de conjonction,
        # si. Sans cette réserve « ואם » valait « אם », et l'alignement
        # appariait le « וְאִם » du séif יד du siman 8 à un « אם » du séif יג.
        self.cle = (self.lettres[:1] + squelette(self.lettres[1:])) if self.lettres else "·"
        self.abrev = any(q in brut for q in QUOTES)
        self.rama = kw.get("rama", False)
        self.chapeau = kw.get("chapeau", False)
        self.ref = kw.get("ref", False)
        self.seif = kw.get("seif", 0)
        self.bloc = kw.get("bloc", 0)
        self.deb = kw.get("deb", 0)
        self.fin = kw.get("fin", 0)


def mots_source(seifim):
    """Les mots de Sefaria, chacun avec son séif, et ce qu'il est : chapeau, Rama,
    renvoi de source entre parenthèses ou crochets."""
    out = []
    for i, raw in enumerate(seifim, 1):
        raw = RE_NOTE.sub(" ", RE_ANCRE.sub("", raw))
        chap = i == 1 and raw.lstrip().startswith("<b>")
        small, prof, en_b, vu_b = 0, 0, False, False
        for piece in re.split(r"(<[^>]+>)", raw):
            if piece.startswith("<"):
                p = piece.lower()
                if p.startswith("<small"):
                    small += 1
                elif p.startswith("</small"):
                    small = max(0, small - 1)
                elif p.startswith("<b>") or p.startswith("<b "):
                    en_b = chap and not vu_b
                elif p.startswith("</b"):
                    if en_b:
                        vu_b = True
                    en_b = False
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
                out.append(Mot(g, rama=small > 0, chapeau=en_b, ref=prof > 0, seif=i))
    return out


def texte_bloc(raw):
    """Le texte lisible d'un bloc de la page, marqueurs de séif blanchis."""
    raw = RE_ETIQ.sub("", raw)
    raw = RE_NOTE.sub(" ", RE_ANCRE.sub("", raw))
    raw = RE_BLOC_HTML.sub(" ", raw)
    raw = RE_BALISE.sub("", raw)
    t = sans_nikoud(html.unescape(raw))
    marqueurs = []

    def blanchir(m):
        lettres = re.sub(r"[^א-ת]", "", m.group(1))
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


def fetch(n, rafraichir=False):
    """Les séifim du Mehaber (bruts, avec balises), ou None — et alors RAISONS[n]
    dit pourquoi. Jamais de liste vide confondue avec un succès."""
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, f"OH-{n}.json")
    if not rafraichir and os.path.exists(f):
        try:
            d = json.load(open(f, encoding="utf-8"))
            if d.get("he") and str(d.get("ref", "")).endswith(f" {n}"):
                return d
        except Exception:
            pass
    u = f"https://www.sefaria.org/api/texts/{LIVRE}.{n}?context=0&pad=0"
    try:
        d = json.load(urllib.request.urlopen(u, timeout=60))
    except Exception as e:
        RAISONS[n] = f"api/texts injoignable : {type(e).__name__} {e}"[:160]
        return None
    ref = str(d.get("ref") or "")
    if d.get("error") or not ref.rstrip().endswith(f" {n}"):
        RAISONS[n] = f"ref servi {d.get('ref')!r} ≠ siman {n} demandé, error {d.get('error')!r}"
        return None
    he = d.get("he")
    he = he if isinstance(he, list) else ([he] if he else [])
    he = [x if isinstance(x, str) else " ".join(map(str, x)) for x in he]
    if not any(re.sub(r"<[^>]+>", "", x).strip() for x in he):
        RAISONS[n] = "ref juste mais he VIDE — le Mehaber n'a pas de lacune connue en Orah Haïm"
        return None
    out = {"ref": ref, "heVersionTitle": d.get("heVersionTitle"), "he": he}
    with open(f, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
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
            "marqueurs": marqueurs, "declare": RE_DECL.search(page)}


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

        def score(c):
            x, y = c
            return ((x == 0 or src[x - 1].seif != src[x].seif)
                    + (y == n or src[y].seif != src[y - 1].seif), c == (i, j))

        a, b = max(cands, key=score)
        if (a, b) != (i, j):
            u0, u1 = min(c[0] for c in cands), max(c[1] for c in cands)
            partenaires = [part[x] for x in range(u0, u1) if not (i <= x < j)]
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
        elif tag == "replace" and (lambda a, b: a == b or a[:1] + squelette(a[1:]) == b[:1] + squelette(b[1:]))(
                "".join(w.lettres for w in src[i1:i2]), "".join(w.lettres for w in pm[j1:j2])):
            # même texte, coupé autrement en mots : « דוראיתם » / « ד וראיתם »
            same = "".join(w.lettres for w in src[i1:i2]) == "".join(w.lettres for w in pm[j1:j2])
            for i in range(i1, i2):
                st[i] = "eq" if same else "ktiv"
                part[i] = j1
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
        if not en_place(s, premier, dernier):
            deplace[s] = (pm[premier].bloc, pg["titres"][pm[premier].bloc])

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


def analyser(src, pg, nseifs):
    st, op_de, part, rep_page, deplace, ajouts, par_seif = aligner(src, pg, nseifs)
    pm = pg["mots"]
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
    taille_op = {}
    for o in op_de:
        if o is not None:
            taille_op[o] = taille_op.get(o, 0) + 1
    res = {}
    for s in range(1, nseifs + 1):
        idx = par_seif.get(s, [])
        d = {"familles": [], "lignes": [], "ktiv": False}
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
                d["familles"].append("TRONCATURE")
                d["lignes"].append(
                    f"TRONCATURE — séif réduit à {len(propres)} mot(s) sur {len(idx)}, "
                    f"réécrit autour : « {extrait(restes)} » ; source : « {extrait([src[x] for x in idx])} »")
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
            d["familles"].append(quoi)
            d["lignes"].append(f"{quoi} — {len(idx)} mots, {decl} : « {extrait([src[x] for x in idx])} »")
            res[s] = d
            continue
        if s in deplace:
            b, t = deplace[s]
            d["familles"].append("DÉPLACÉ")
            d["lignes"].append(f"DÉPLACÉ — reproduit hors de l'ordre de la source, au bloc {b + 1}"
                               + (f" (« {t[:60]} »)" if t else ""))
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
            tout_rama = all(w.rama for w in run)
            tout_ref = all(w.ref for w in run)
            n = len(run)
            dans_par = " (entre parenthèses)" if tout_ref else ""
            if tout_ref and (not page_rep or len(page_rep) * 2 < n):
                # un renvoi de source entre parenthèses n'est pas une troncature
                # du DIN, quelle que soit sa longueur
                d["familles"].append("ALTÉRATION")
                d["lignes"].append(f"ALTÉRATION — passage entre parenthèses omis : « {extrait(run)} »"
                                   + (f" (à sa place : « {extrait(page_rep)} »)" if page_rep else ""))
            elif page_rep and not (n >= TRONC_MIN and len(page_rep) * 2 < n):
                d["familles"].append("ALTÉRATION")
                if any(w.abrev for w in run) or any(w.abrev for w in page_rep):
                    d["lignes"].append(f"ALTÉRATION — abréviation de l'imprimé développée ou changée{dans_par} : "
                                       f"« {extrait(run)} » → « {extrait(page_rep)} »")
                elif len(run) == 1 and len(page_rep) == 1 and une_lettre(run[0].lettres, page_rep[0].lettres):
                    d["lignes"].append(f"ALTÉRATION — une lettre{dans_par} : « {run[0].brut} » → « {page_rep[0].brut} »")
                else:
                    d["lignes"].append(f"ALTÉRATION — mots changés{dans_par} : « {extrait(run)} » → « {extrait(page_rep)} »")
            elif n >= TRONC_MIN:
                d["familles"].append("TRONCATURE")
                d["lignes"].append(_ligne_tronc(pg, part[idx[x]], pos, run, tout_rama, page_rep))
            else:
                d["familles"].append("ALTÉRATION")
                k = part[idx[x]]
                decl = " (déclaré par « … »)" if (not page_rep and k is not None and ellipse_a(pg, k)) else ""
                quoi = ("mot « הגה » omis (l'étiquette de la glose)"
                        if [w.lettres for w in run] == ["הגה"] and not page_rep else "mot(s) omis")
                d["lignes"].append(f"ALTÉRATION — {quoi}{decl} : « {extrait(run)} »"
                                   + (f" → « {extrait(page_rep)} »" if page_rep else ""))
            x = y
        res[s] = d

    # Ajouts : rattachés au séif qui précède le point d'insertion.
    src_de_page = {}
    for x, k in enumerate(part):
        if k is not None and st[x] in ("eq", "ktiv"):
            src_de_page.setdefault(k, x)
    toutes = [w.cle for w in src]
    ajouts_lignes = []
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
                vus = {b.b + d for b in blocs for d in range(b.size)}
                seifs = sorted({src[b.a + d].seif for b in blocs for d in range(b.size)})
                ecarts = [mots[k] for k in range(len(mots)) if k not in vus]
                cible = seifs[0]
                fam = "REPRISE"
                ligne = (f"REPRISE — {len(mots)} mots du séif "
                         f"{', '.join(f'{q} ({numeral(q)})' for q in seifs)} cités une seconde fois"
                         + (", fidèlement (au ktiv près)" if not ecarts else
                            f", dont {len(ecarts)} mot(s) qui ne sont pas ceux de la source : "
                            f"« {extrait(ecarts)} »"))
                res.setdefault(cible, {"familles": [], "lignes": [], "ktiv": False})
                res[cible]["familles"].append(fam)
                if ecarts:
                    res[cible]["familles"].append("ALTÉRATION")
                res[cible]["lignes"].append(ligne)
                continue
            fam = "AJOUT"
            ligne = f"AJOUT — {len(mots)} mots qui ne sont pas du siman : « {extrait(mots)} »"
        else:
            fam = "ALTÉRATION"
            quoi = ("mot « הגה » ajouté (l'étiquette de la glose)"
                    if [w.lettres for w in mots] == ["הגה"] else "mot(s) ajouté(s)")
            ligne = f"ALTÉRATION — {quoi} : « {extrait(mots)} »"
        res.setdefault(s, {"familles": [], "lignes": [], "ktiv": False})
        res[s]["familles"].append(fam)
        res[s]["lignes"].append(ligne)
    return res


def _ligne_tronc(pg, k, pos, run, rama, page_rep=()):
    decl = "déclarée par « … »" if (k is not None and ellipse_a(pg, k)) else "NON déclarée"
    quoi = "la glose du Rama" if rama else ("dont la glose du Rama" if any(w.rama for w in run) else "")
    rep = f", remplacés par « {extrait(list(page_rep), 4)} »" if page_rep else ""
    return (f"TRONCATURE {pos} — {len(run)} mots consécutifs non reproduits"
            f"{' (' + quoi + ')' if quoi else ''}{rep}, {decl} : « {extrait(run)} »")


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


# -------------------------------------------------------------------- verdicts

ORDRE = ["ABSENT NON DÉCLARÉ", "ABSENT DÉCLARÉ", "TRONCATURE", "DÉPLACÉ", "ALTÉRATION", "AJOUT"]


def principal(fams):
    for f in ORDRE:
        if f in fams:
            return f
    return None


def un_siman(n, args, stats):
    d = fetch(n, args.rafraichir)
    if d is None:
        stats["non_atteints"].append((n, RAISONS.get(n, "?")))
        print(f"\n=== Siman {n} — NON ATTEINT : {RAISONS.get(n)}")
        return
    seifs = d["he"]
    src = mots_source(seifs)
    avec = "".join(w.lettres for w in src)
    sans = "".join(w.lettres for w in src if not w.chapeau)
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
    stats["seifim"] += len(seifs)
    stats["mots_src"] += len(src)
    stats["pages"] += len(pages)
    resultats, verdict_lang, memo = {}, {}, {}
    for lang, pg in pages.items():
        stats["mots_page"] += len(pg["mots"])
        cle = tuple(w.lettres for w in pg["mots"])
        lettres = "".join(cle)
        if lettres in (avec, sans):
            verdict_lang[lang] = "IDENTIQUE"
            resultats[lang] = {}
            continue
        if cle not in memo:
            memo[cle] = analyser(src, pg, len(seifs))
        resultats[lang] = memo[cle]
        fams = {f for r in memo[cle].values() for f in r["familles"]}
        verdict_lang[lang] = principal(fams) or "ÉQUIVALENT"
    parite = len({tuple(w.lettres for w in pg["mots"]) for pg in pages.values()}) == 1 and not absentes

    # comptes : un séif compte dans une famille si l'une des trois pages l'y met
    fam_seif = {}
    for lang, r in resultats.items():
        for s, x in r.items():
            for f in x["familles"]:
                fam_seif.setdefault((s, f), set()).add(lang)
    for (s, f), ls in fam_seif.items():
        stats["seifs_fam"].setdefault(f, set()).add((n, s))
    for s in range(1, len(seifs) + 1):
        p = principal({f for (q, f) in fam_seif if q == s})
        stats["seifs_principal"][p or "CONFORME (au ktiv près)"] = \
            stats["seifs_principal"].get(p or "CONFORME (au ktiv près)", 0) + 1
    for lang, r in resultats.items():
        for s, x in r.items():
            for ligne in x["lignes"]:
                if ligne.startswith("TRONCATURE"):
                    stats["tronc"].add((n, s, ligne.split(" — ")[0], "Rama" in ligne, "déclarée par" in ligne))
                if "abréviation" in ligne:
                    stats["abrev"].add((n, s))
                if "entre parenthèses" in ligne:
                    stats["paren"].add((n, s))
                if ligne.startswith("ALTÉRATION") and "abréviation" not in ligne \
                        and "entre parenthèses" not in ligne:
                    stats["autres_alt"].add((n, s))
                if ligne.startswith("TRONCATURE — séif réduit"):
                    stats["reduits"].add((n, s))
                if "ANNONCÉ par le titre" in ligne:
                    stats["annonce"].add((n, s))
    pires = [verdict_lang[l] for l in verdict_lang]
    pire = (principal(set(pires)) or ("ÉQUIVALENT" if "ÉQUIVALENT" in pires else "IDENTIQUE"))
    if absentes:
        pire = principal(set(pires)) or "PAGE ABSENTE"
        stats["pages_absentes"].append((n, absentes))
    stats["verdict"].setdefault(pire, []).append(n)
    if not parite:
        stats["parite"].append(n)
    if pire not in ("IDENTIQUE", "ÉQUIVALENT"):
        stats["divergents"].append(n)
    blocs = "/".join(str(len(pages[l]["textes"])) if l in pages else "—" for l, _ in LANGS)

    if args.bref:
        fams = sorted({f for (s, f) in fam_seif}, key=(ORDRE + ["REPRISE"]).index)
        detail = ", ".join(f"{f.lower()} {len({s for (s, g) in fam_seif if g == f})}" for f in fams)
        print(f"  siman {n:3d} : {len(seifs):2d} séifim · blocs {blocs:>8s} · {pire}"
              f"{' — ' + detail if detail else ''}{'' if parite else ' · ⚠️ parité'}")
        return

    print(f"\n=== Siman {n} — {len(seifs)} séifim sur Sefaria · {len(src)} mots · "
          f"blocs FR/HE/EN {blocs} ===")
    for lang, _ in LANGS:
        if lang in absentes:
            print(f"  {lang}: FICHIER ABSENT {chemin(n, dict(LANGS)[lang])}")
        else:
            print(f"  {lang}: {len(pages[lang]['mots'])} mots confrontés · {verdict_lang[lang]}")
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
    # Les lignes de défaut : une fois si les pages concordent, sinon langue par langue.
    groupes = {}
    for lang in [l for l, _ in LANGS if l in resultats]:
        cle = tuple(w.lettres for w in pages[lang]["mots"])
        groupes.setdefault(cle, []).append(lang)
    for cle, ls in groupes.items():
        r = resultats[ls[0]]
        lignes = [(s, l) for s in sorted(r) for l in r[s]["lignes"]]
        if not lignes:
            continue
        if len(groupes) > 1:
            print(f"  — {'/'.join(ls)} :")
        for s, l in lignes:
            print(f"    séif {s:2d} ({numeral(s)}) : {l}")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("simanim", nargs="*", type=int)
    ap.add_argument("--tous", action="store_true")
    ap.add_argument("--bref", action="store_true")
    ap.add_argument("--rafraichir", action="store_true", help="ignore le cache Sefaria")
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
             "seifs_principal": {}}
    print(f"=== Recopie du niveau 1 d'Orah Haïm vs Shulchan_Arukh,_Orach_Chayim (Sefaria) — "
          f"{len(nums)} siman(im) demandé(s) · ROOT {ROOT} ===")
    for n in nums:
        un_siman(n, args, stats)

    print("\n" + "=" * 78)
    print(f"CONFRONTÉ : {stats['simanim']} simanim · {stats['seifim']} séifim · "
          f"{stats['mots_src']} mots de source · {stats['pages']} pages · "
          f"{stats['mots_page']} mots de page")
    if stats["simanim"] == 0:
        print("❌ RIEN N'A ÉTÉ CONFRONTÉ — la porte ne conclut pas (code 3).")
        if not nums:
            print(f"   aucune page sous {SECTION} : copie lancée hors du dépôt ?")
    print("\nSimanim par verdict (le pire des trois pages) :")
    for v in ["IDENTIQUE", "ÉQUIVALENT"] + ORDRE + ["PAGE ABSENTE"]:
        if v in stats["verdict"]:
            l = stats["verdict"][v]
            print(f"  {v:20s} {len(l):4d}" + ("" if v in ("IDENTIQUE", "ÉQUIVALENT") else
                                               "   " + " ".join(map(str, l))))
    print("\nSéifim par verdict principal (chacun compté UNE fois, sous son pire défaut, "
          "les trois pages réunies) :")
    for v in ["CONFORME (au ktiv près)"] + ORDRE:
        if v in stats["seifs_principal"]:
            print(f"  {v:24s} {stats['seifs_principal'][v]:5d}")
    print("\nSéifim par famille (un séif compte dans chaque famille où l'une des trois pages le met) :")
    for f in ORDRE + ["REPRISE"]:
        e = stats["seifs_fam"].get(f, set())
        print(f"  {f:20s} {len(e):4d} séifim dans {len({n for n, _ in e}):3d} simanim"
              + ("   (information : un passage déjà donné, cité une seconde fois — "
                 "ne fait pas à lui seul diverger le siman)" if f == "REPRISE" else ""))
    tr = stats["tronc"]
    if tr:
        print(f"  dont troncatures : fin {sum(1 for t in tr if t[2].endswith('fin'))} · "
              f"début {sum(1 for t in tr if t[2].endswith('début'))} · "
              f"intérieure {sum(1 for t in tr if t[2].endswith('intérieure'))} · "
              f"portant sur le Rama {sum(1 for t in tr if t[3])} · "
              f"déclarées par « … » {sum(1 for t in tr if t[4])} (occurrences séif × position)")
    if stats["annonce"]:
        print(f"  dont absents ANNONCÉS par le titre de leur bloc : {len(stats['annonce'])} séifim")
    if stats["abrev"]:
        print(f"  dont altérations par abréviation : {len(stats['abrev'])} séifim")
    if stats["paren"]:
        print(f"  dont passages entre parenthèses omis (renvois de source, gloses) : {len(stats['paren'])} séifim")
    if stats["autres_alt"]:
        print(f"  dont autres altérations (mots changés, omis, ajoutés, une lettre) : "
              f"{len(stats['autres_alt'])} séifim")
    if stats["reduits"]:
        print(f"  dont séifim réduits à quelques mots réécrits (comptés en TRONCATURE) : "
              f"{len(stats['reduits'])}")
    if stats["parite"]:
        print(f"\nParité FR/HE/EN du texte source DIVERGENTE : {len(stats['parite'])} simanim — "
              + " ".join(map(str, stats["parite"])))
    if stats["pages_absentes"]:
        print("Pages absentes : " + "; ".join(f"{n} {'/'.join(l)}" for n, l in stats["pages_absentes"]))
    if stats["non_atteints"]:
        print(f"\nNON ATTEINTS ({len(stats['non_atteints'])}) — rien n'est conclu sur eux :")
        for n, r in stats["non_atteints"]:
            print(f"  siman {n} : {r}")
    if stats["simanim"] == 0:
        return 3
    if stats["divergents"]:
        print(f"\n❌ {len(stats['divergents'])} siman(im) dont le texte source diverge de Sefaria "
              "au-delà du ktiv haser/malé — NE PAS PUBLIER sans relecture")
        return 1
    if stats["non_atteints"]:
        print("\n⚠️  conforme sur ce qui a été lu, mais des simanim n'ont pas été atteints (code 3)")
        return 3
    print("\n✅ RECOPIE DU NIVEAU 1 : conforme à Sefaria (au ktiv près)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
