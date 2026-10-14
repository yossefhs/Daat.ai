#!/usr/bin/env python3
"""Confronte l'APERÇU de chaque séif du niveau 4 — le texte hébreu du titre du bloc, que le lecteur lit d'abord
quand le séif est fermé — au texte source de son bloc.

Usage :
  python3 scripts/verifier-apercus.py                 # Orah Haïm (1-241) et Chabbat (242-365), les trois langues
  python3 scripts/verifier-apercus.py 76 186 301      # simanim nommés
  python3 scripts/verifier-apercus.py --section shabbat
  options : --bref (le décompte seul) · --lignes (chaque aperçu non conforme, avec le début de son séif) ·
            --json FICHIER (un enregistrement par bloc, conformes compris)

Codes de sortie : 0 tout aperçu conforme · 1 au moins un aperçu non conforme · 3 une page illisible, ou AUCUN
aperçu confronté (une porte qui ne compare rien ne sort pas verte).

POURQUOI. Chaque séif vit dans un <details class="seif-details"> dont le titre porte « סעיף X » et un aperçu
VOCALISÉ (<summary> > span.seif-preview), dans la police du texte source, juste au-dessus de lui. 90 % des blocs
sont fermés au chargement : le lecteur lit l'aperçu comme le début du séif. verify-oh-source.py confronte le
.sa-he à Sefaria mot pour mot et déclarait l'aperçu hors champ ; verifier-citations.py ne juge que ce qui est entre
guillemets. Rien ne le lisait. Un aperçu « כָּשֵׁר » pour un séif « פָּסוּל » sortait conforme partout.

LA RÈGLE. Un aperçu est conforme s'il est fait de MOTS DU SÉIF, VERBATIM, DANS L'ORDRE, ET QUE TOUTE COUPE Y EST
DÉCLARÉE PAR « … » — la convention des citations du dépôt (CLAUDE.md : « A… B » signifie que A et B sont chacun
verbatim) appliquée au titre :
  1. chaque segment entre deux « … » est une suite de mots consécutifs du .sa-he de son bloc, et les segments se
     suivent dans l'ordre du séif ;
  2. un aperçu qui ne commence pas au premier mot du séif s'ouvre sur « … » ; un aperçu qui s'arrête avant la fin
     du séif se ferme sur « … », et c'est seulement là qu'un mot peut être coupé (« בְּסִמ… ») ; une « … » ne se
     pose que là où quelque chose est omis ;
  3. seul le CHAPEAU du siman (« … וּבוֹ N סְעִיפִים: », reconnu par chapeau() de verify-oh-source.py) peut être
     omis sans « … » en tête du séif 1 : c'est le titre du siman, non le texte du séif.
  Sont ADMIS sans être confrontés, et comptés à part : un titre sans aucune lettre hébraïque (il ne se donne pas
  pour la source : 70 titres anglais, Chabbat 305, 321-324, 355-357), une note éditoriale entièrement entre
  crochets SUR UN SÉIF VIDE (« [סעיף ל״ג חסר במהדורת קה״ת.] », 305:33, que Sefaria sert vide ; ailleurs, les mots
  entre crochets sont jugés comme les autres), un bloc sans aperçu, et une CONDENSATION MARQUÉE — un aperçu qui commence par
  « תַּמְצִית: » (aucun au 13 octobre 2026). Une condensation marquée n'est pas jugée verbatim, comme les cellules
  « résumé : » des tableaux ; ses mots de décision absents du séif sont imprimés à part (⚑), sans rien bloquer.

  L'APERÇU, c'est tout le texte du <summary> hors de span.seif-num : un texte posé hors de span.seif-preview y est
  jugé comme lui. Un <summary> nu (« סעיף א » : 41 blocs, Chabbat 321-324 en hébreu et 305:33) n'a pas d'aperçu.

LES NORMALISATIONS sont celles de verify-oh-source.py, importées et non recopiées : la page est lue par son Lecteur
(premier attribut, frontières de mots, <br>…), les mots par mots() — NFC, nikoud et te'amim retirés, maqaf =
frontière, ZWJ et crochets éditoriaux de Kehot retirés (« יַחֲזִ[י]ר » = « יחזיר »), « … », « ... » reconnus.
La ponctuation, les guillemets et le nikoud ne sont donc pas confrontés : « חָלָב » et « חֵלֶב » y sont le même mot,
comme dans la porte du .sa-he.

CE QUE LA CONFORMITÉ GARANTIT, ET À QUELLE CONDITION. La porte confronte l'aperçu au .sa-he DE LA PAGE, non à
Sefaria : hors réseau, ~6 s pour les 1 095 pages. « L'aperçu est la source » ne vaut donc que si verify-oh-source.py
certifie le .sa-he de la même page — les deux portes se lancent ensemble.

CE QU'ELLE NE COUVRE PAS :
  - la JUSTESSE d'une coupe déclarée : « A… B » verbatim peut sauter la condition qui retourne A — c'est la
    famille de verifier-troncatures.py, qui ne lit pas les aperçus ;
  - le sens d'une condensation marquée (relecture) ;
  - l'étiquette « סעיף X » (verifier-alignement.py) ; la visibilité (le CSS est figé par verify-oh-source.py) ;
  - la parité FR/HE/EN de l'aperçu : chaque page est jugée seule ; l'écart entre langues est compté, non refusé.

LES CLASSES NON CONFORMES, imprimées avec leur famille :
  COUPE NON DÉCLARÉE    — mots du séif verbatim, mais un début ou une fin omis sans « … » ;
  « … » SANS COUPE      — une « … » là où rien n'est omis ;
  ABRÉGÉ                — mots du séif dans l'ordre, des mots sautés sans « … » ;
  REFORMULÉ             — mots du séif, mais l'ordre (ou le nombre) n'est pas le sien ;
  MOT ABSENT            — au moins un mot qui n'est pas dans le séif. Chaque mot absent porte sa nature : variante
                          d'un mot du séif (yod/vav ; préfixe ו ה ב ל כ ש מ ד ; frontière de mot ; sigle « ק״ש »,
                          « ד׳ »), ou mot ÉTRANGER au séif. Que tous soient des variantes ne dit rien de l'aperçu :
                          une condensation recomposée de mots du séif est la règle, non l'exception (31:2).
  ⚑ marque un aperçu dont un MOT DE DÉCISION (מֻתָּר, אָסוּר, חַיָּב, פָּטוּר, כָּשֵׁר, פָּסוּל, צָרִיךְ, חוֹזֵר, מְבָרֵךְ…)
  n'est pas dans le séif : un candidat à ouvrir d'abord, non un verdict (« מוֹתַר הָאָדָם », 115:1, en est un faux).

PREMIER BALAYAGE, 13 octobre 2026 (relevé et échantillon jugé : audit/apercus-niveau4.md ; liste complète :
audit/apercus-niveau4.txt). 9 942 blocs, 9 830 aperçus confrontés : 5 875 conformes, 3 955 NON CONFORMES (1 432
aperçus distincts, 181 simanim) — 3 922 à Orah Haïm (83 % de la section : des condensations en hébreu vocalisé,
dans la langue de l'Admour HaZaken, que rien ne distingue du texte), 33 seulement à Chabbat, dont les aperçus sont
des débuts de séif coupés à longueur fixe. L'arbitre du septième tour comptait 2 694 aperçus portant un mot absent ; la porte en
retrouve 2 695 au sens strict, dont 104 ne s'écartent que par leur dernier mot coupé avant « … » (conformes).
Un échantillon de 117 aperçus non conformes, lu contre le séif, en a trouvé 12 qui changent le sens — 75:7 donne
pour règle l'avis que l'Admour HaZaken écarte (« וְכֵן עִקָּר ») ; 186:4 fait d'un « אֵינוֹ רַשַּׁאי » un « אֵינוֹ
יוֹצֵא » ; 76:11, 192:6, 167:10 omettent la condition qui renverse la règle —, dont 5 sur un tirage au hasard
de 60.
CORRIGÉ LE MÊME JOUR par scripts/fix-apercus.py (537 pages, 4 029 aperçus réécrits) : la porte sort verte, et le
doit rester.
"""
import sys, os, re, json, importlib.util, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("verify_oh_source", os.path.join(ROOT, "scripts", "verify-oh-source.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)

ETIQUETTE = re.compile(r"^\s*סעיף\s+[א-ת]{1,4}[\"'״׳]?[א-ת]?\s*[.:]?")
MARQUE = re.compile(r"^\s*תמצית\s*:")
MATRES = str.maketrans("", "", "וי")
PREFIXES = set("ושהבלכמד")
DECISIONS = {"מתר", "מותר", "מתרים", "מותרים", "מתרין", "מותרין", "מתרת", "מותרת", "אסור", "אסורים", "אסורין", "אסורה",
             "חיב", "חייב", "חיבים", "חייבים", "חיבין", "חייבין", "פטור", "פטורים", "פטורין", "כשר", "כשרים", "כשרין",
             "כשרה", "פסול", "פסולים", "פסולין", "פסולה", "צריך", "צריכים", "צריכין", "חוזר", "חוזרים", "חוזרין",
             "מברך", "מברכין", "מברכים", "יברך", "יצא", "יוצא", "יוצאין", "מתירין", "אוסרין", "רשאי"}
CONFORMES = ("INCIPIT — séif entier", "INCIPIT — coupe finale déclarée", "COUPES DÉCLARÉES")
ADMIS = ("SANS APERÇU", "TITRE SANS HÉBREU", "NOTE ENTRE CROCHETS", "CONDENSATION MARQUÉE")
NON_CONFORMES = ("COUPE NON DÉCLARÉE", "« … » SANS COUPE", "ABRÉGÉ", "REFORMULÉ", "MOT ABSENT")


ONES, TENS, HUNS = " אבגדהוזחט", " יכלמנסעפצ", " קרשת"


def gematria(n):
    """242 → « רמ״ב », 1 → « א׳ » (la convention de heb-nums.py)."""
    r = n % 100
    s = (HUNS[n // 100] + ("טו" if r == 15 else "טז" if r == 16 else TENS[r // 10] + ONES[r % 10])).replace(" ", "")
    return s + "׳" if len(s) == 1 else s[:-1] + "״" + s[-1]


class LecteurApercus(V.Lecteur):
    """Le Lecteur de verify-oh-source.py, qui relève en plus, pour chaque bloc, le texte de son <summary> :
    celui de span.seif-num (« num ») et tout le reste (« titre »)."""

    def __init__(self):
        super().__init__()
        self._sm = self._num = self._pv = None   # profondeur de pile du <summary>, du span.seif-num, du span.seif-preview

    def _ouvre(self, tag, attrs, auto):
        n0 = len(self.pile)
        super()._ouvre(tag, attrs, auto)
        if len(self.pile) != n0 + 1 or not self.bloc or not self.blocs:
            return
        classes = next((v or "" for k, v in attrs if k.lower() == "class"), "").split()   # le premier, comme le navigateur
        if tag == "summary" and self._sm is None:
            self._sm = len(self.pile)
            self.blocs[-1].update({"num": None, "titre": "", "hors": ""})
        elif self._sm and tag == "span" and "seif-num" in classes and self._num is None:
            self._num = len(self.pile)
            self.blocs[-1]["num"] = ""
        elif self._sm and tag == "span" and "seif-preview" in classes and self._pv is None:
            self._pv = len(self.pile)

    def _frontiere(self):
        super()._frontiere()
        if self._sm and not self._num and self.blocs:
            self.blocs[-1]["titre"] += " "

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if self._num and len(self.pile) < self._num:
            self._num = None
        if self._pv and len(self.pile) < self._pv:
            self._pv = None
        if self._sm and len(self.pile) < self._sm:
            self._sm = self._num = self._pv = None

    def handle_data(self, data):
        super().handle_data(data)
        if self._sm and self.blocs and self._script is None and self._style is None:
            b = self.blocs[-1]
            if self._num:
                b["num"] += data
            else:
                b["titre"] += data
                if not self._pv:
                    b["hors"] += data


def lire(path):
    """Les blocs de la page, chacun avec son étiquette et son aperçu. Lève sur une page que la porte ne lit pas."""
    html = re.sub(r"<!---?>", "<!---->", open(path, encoding="utf-8").read())
    lx = LecteurApercus()
    lx.feed(html)
    lx.close()
    for b in lx.blocs:
        titre = re.sub(r"\s+", " ", unicodedata.normalize("NFC", b.get("titre", ""))).strip()
        num = (b.get("num") or "").strip()
        hors = re.sub(r"\s+", " ", b.get("hors", "")).strip()
        if b.get("num") is None:                 # <summary> nu : l'étiquette est en tête du texte
            m = ETIQUETTE.match(titre)
            if m:
                num, titre = m.group(0).strip(), titre[m.end():].strip()
                hors = ETIQUETTE.sub("", hors).strip()
        else:                                    # span.seif-num : l'étiquette seule ; tout le reste est jugé
            num = re.sub(r"\s+", " ", unicodedata.normalize("NFC", num))
            m = ETIQUETTE.match(num)
            reste = num[m.end():].strip() if m else num
            if reste:
                num, titre, hors = (m.group(0).strip() if m else ""), (reste + " " + titre).strip(), reste
        b["etiquette"], b["apercu"], b["hors_span"] = num, titre, bool(hors)
    return lx.blocs


# ---------------------------------------------------------------- confrontation

def segments(pt):
    """Les mots de l'aperçu coupés aux « … » : (segments, « … » en tête, « … » en fin, nombre de « … » vides)."""
    segs, cur, vides, prec = [], [], 0, None
    for w in pt:
        if w == "…":
            if cur:
                segs.append(cur)
            elif prec == "…":
                vides += 1
            cur = []
        else:
            cur.append(w)
        prec = w
    if cur:
        segs.append(cur)
    return segs, bool(pt) and pt[0] == "…", bool(pt) and pt[-1] == "…", vides


def placer(st, seg, depuis, coupe_permise):
    """Premier rang ≥ depuis où le segment est une suite de mots du séif ; son dernier mot peut n'en être que le début
    si une « … » le suit. Rend (rang, mot coupé ?) ou (-1, False)."""
    n = len(seg)
    for i in range(depuis, len(st) - n + 1):
        if st[i:i + n - 1] == seg[:-1]:
            if st[i + n - 1] == seg[-1]:
                return i, False
            if coupe_permise and st[i + n - 1].startswith(seg[-1]):
                return i, True
    return -1, False


def sous_suite(seq, sub):
    i = 0
    for w in sub:
        while i < len(seq) and seq[i] != w:
            i += 1
        if i == len(seq):
            return False
        i += 1
    return True


def nature(w, st, brut):
    """Pourquoi un mot de l'aperçu n'est pas dans le séif : la variante d'un de ses mots, ou un mot étranger.
    `brut` : l'aperçu sans nikoud, où se lisent les sigles."""
    if len(w) <= 3 and re.search(rf"(?<![א-ת]){w}[״׳\"']|[״\"]{w}(?![א-ת])", brut):
        return "sigle"
    sq = w.translate(MATRES)
    if any(x.translate(MATRES) == sq for x in st):
        return "yod/vav"
    for x in st:
        a, b = (w, x) if len(w) > len(x) else (x, w)
        if len(b) >= 2 and a.endswith(b) and set(a[:len(a) - len(b)]) <= PREFIXES:
            return "préfixe"
    if len(w) >= 3 and w in "".join(st):
        return "frontière de mot"
    return "étranger"


def decisions_absentes(pm, st):
    return sorted({w for w in pm if w in DECISIONS} - set(st))


def classer(apercu, txt, rang):
    """(classe, détails) de l'aperçu d'un bloc de rang `rang` (0 pour le séif 1) dont le .sa-he est `txt`."""
    if not apercu:
        return "SANS APERÇU", {}
    if not re.search(r"[א-ת]", apercu):
        return "TITRE SANS HÉBREU", {}
    st = V.sans_points(V.mots(txt))
    if re.fullmatch(r"\[[^\[\]]*\]", apercu) and not st:   # la note qui dit qu'un séif manque, et elle seule
        return "NOTE ENTRE CROCHETS", {}
    if MARQUE.match(V.NIKUD.sub("", apercu)):
        pm = V.sans_points(V.mots(MARQUE.sub("", V.NIKUD.sub("", apercu))))
        return "CONDENSATION MARQUÉE", {"decisions": decisions_absentes(pm, st)}
    pt = V.mots(apercu)
    pm = V.sans_points(pt)
    if not pm:
        return "TITRE SANS HÉBREU", {}
    segs, tete, fin, vides = segments(pt)
    chap = V.chapeau(txt) if rang == 0 else 0
    pos, places, coupe = 0, [], False
    for k, s in enumerate(segs):
        dernier = k == len(segs) - 1
        p, c = placer(st, s, pos, coupe_permise=not dernier or fin)
        if p < 0:
            break
        coupe |= c
        places.append((p, p + len(s)))
        pos = p + len(s) - (1 if c else 0)
    if len(places) == len(segs):
        manques = []
        debut, fin_ = places[0][0], places[-1][1]
        if debut not in (0, chap) and not tete:
            manques.append(f"début omis sans « … » ({debut} mots)")
        if fin_ < len(st) and not fin:
            manques.append(f"fin omise sans « … » ({len(st) - fin_} mots)")
        if manques:
            return "COUPE NON DÉCLARÉE", {"detail": " ; ".join(manques)}
        src = set(V._rangs_points(V.mots(txt)))  # une « … » de l'aperçu là où la source en porte une est recopiée
        sans = [k for k in range(1, len(places)) if places[k][0] == places[k - 1][1] and places[k][0] not in src]
        if (tete and debut == 0 and 0 not in src) or (fin and fin_ == len(st) and not coupe and fin_ not in src) \
                or sans or vides:
            return "« … » SANS COUPE", {}
        if len(segs) == 1 and debut in (0, chap):
            return ("INCIPIT — séif entier" if fin_ == len(st) else "INCIPIT — coupe finale déclarée"), \
                {"chapeau_omis": bool(chap) and debut == chap}
        return "COUPES DÉCLARÉES", {"segments": len(segs)}
    d = {"decisions": decisions_absentes(pm, st)}
    if sous_suite(st, pm):
        return "ABRÉGÉ", d
    presents = collections.Counter(st)
    absents = [w for w in pm if w not in presents]
    if not absents:
        return "REFORMULÉ", d
    brut = V.NIKUD.sub("", apercu)
    natures = [nature(w, st, brut) for w in absents]
    d.update({"absents": absents, "natures": natures, "etranger": "étranger" in natures})
    return "MOT ABSENT", d


# ---------------------------------------------------------------- balayage

def pages(simanim):
    for n in simanim:
        sec = V.section_de(n)
        for lang, suf in V.LANGS:
            p = os.path.join(ROOT, "sources", sec, f"siman-{n}", f"niveau-4-daat-harav{suf}.html")
            if os.path.exists(p):
                yield n, lang, p


def main(argv):
    opts = {a for a in argv if a.startswith("--")}
    json_out = None
    if "--json" in argv:
        k = argv.index("--json")
        if k + 1 >= len(argv):
            print("--json demande un fichier")
            return 3
        json_out = argv[k + 1]
    nums = [int(a) for a in argv if a.isdigit() and a != json_out]
    if "--section" in argv:
        k = argv.index("--section")
        sec = argv[k + 1] if k + 1 < len(argv) else ""
        rng = dict(V.SECTIONS).get(sec)
        if rng is None:
            print(f"section inconnue : {sec} (orah-haim, shabbat)")
            return 3
        nums = list(rng)
    simanim = nums or [n for _s, r in V.SECTIONS for n in r]

    recs, illisibles = [], []
    for n, lang, p in pages(simanim):
        try:
            blocs = lire(p)
        except Exception as e:                  # une page illisible n'est jamais une page conforme
            illisibles.append((n, lang, f"{type(e).__name__}: {e}"))
            continue
        for i, b in enumerate(blocs):
            classe, d = classer(b["apercu"], b["txt"], i)
            recs.append({"siman": n, "langue": lang, "seif": i + 1, "etiquette": b["etiquette"],
                         "apercu": b["apercu"], "hors_span": b["hors_span"],
                         "classe": classe, **d,
                         "debut_seif": " ".join(b["txt"].split()[:min(30, max(15, len(b["apercu"].split()) + 6))])})

    if json_out:
        json.dump(recs, open(json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    confrontes = [r for r in recs if r["classe"] not in ADMIS]
    fautifs = [r for r in recs if r["classe"] in NON_CONFORMES]
    cpt = collections.Counter(r["classe"] for r in recs)
    print(f"Aperçus du niveau 4 — {len({(r['siman'], r['langue']) for r in recs})} pages lues, {len(recs)} blocs, "
          f"{len(confrontes)} aperçus confrontés à leur .sa-he")
    for titre, classes in (("conformes", CONFORMES), ("admis sans confrontation", ADMIS), ("NON CONFORMES", NON_CONFORMES)):
        tot = sum(cpt[c] for c in classes)
        print(f"  {titre} : {tot}")
        for c in classes:
            if cpt[c]:
                par = collections.Counter(r["langue"] for r in recs if r["classe"] == c)
                print(f"    {cpt[c]:6d}  {c}  (FR {par['FR']} · HE {par['HE']} · EN {par['EN']})")
    ma = [r for r in recs if r["classe"] == "MOT ABSENT"]
    if ma:
        print(f"    dont {sum(r['etranger'] for r in ma)} avec au moins un mot ÉTRANGER au séif, "
              f"{sum(not r['etranger'] for r in ma)} dont chaque mot absent est la variante d'un mot du séif")
    drap = [r for r in recs if r.get("decisions")]
    if drap:
        print(f"  ⚑ mot de décision absent du séif : {len(drap)} aperçus — à ouvrir en premier (--lignes)")
    if any(r["hors_span"] for r in recs):
        print(f"  texte hors de span.seif-preview dans le titre : {sum(r['hors_span'] for r in recs)} blocs (jugé comme l'aperçu)")
    trios = collections.defaultdict(set)
    for r in recs:
        if r["classe"] not in ("SANS APERÇU", "TITRE SANS HÉBREU"):
            trios[(r["siman"], r["seif"])].add(tuple(V.mots(r["apercu"])))
    print(f"  parité : {sum(len(v) > 1 for v in trios.values())} séifs sur {len(trios)} n'ont pas les mêmes mots d'aperçu "
          "dans les trois langues (« … » comprises ; compté, non refusé)")

    if fautifs and "--bref" not in opts:
        par_siman = collections.defaultdict(collections.Counter)
        for r in fautifs:
            par_siman[r["siman"]][r["langue"]] += 1
        print(f"\nSimanim portant au moins un aperçu non conforme : {len(par_siman)}")
        for n in sorted(par_siman):
            c = par_siman[n]
            print(f"  siman {n} ({gematria(n)}) : {sum(c.values())} — FR {c['FR']} · HE {c['HE']} · EN {c['EN']}")
    if fautifs and "--lignes" in opts:
        print("\nAPERÇUS NON CONFORMES (un par séif ; les langues qui le portent à l'identique entre crochets)")
        groupes = collections.OrderedDict()
        for r in fautifs:
            groupes.setdefault((r["siman"], r["seif"], r["apercu"]), []).append(r)
        for (n, s, ap), rs in groupes.items():
            r = rs[0]
            info = r.get("detail") or (" ; ".join(f"{w} ({x})" for w, x in zip(r["absents"], r["natures"]))
                                       if r.get("absents") else "")
            print(f"\n{n} ({gematria(n)}):{s} [{' '.join(x['langue'] for x in rs)}] {r['classe']}"
                  + (f" ⚑ {' '.join(r['decisions'])}" if r.get("decisions") else "") + (f" — {info}" if info else ""))
            print(f"   aperçu : {ap}")
            print(f"   séif   : {r['debut_seif']} …")
    for n, lang, e in illisibles:
        print(f"⛔ siman {n} ({gematria(n)}) {lang} : page illisible — {e}")

    if illisibles or not confrontes:
        print("\n⛔ APERÇUS : " + ("pages illisibles — rien n'est conclu pour elles" if illisibles
                                  else "aucun aperçu confronté — rien n'est conclu"))
        return 3
    if fautifs:
        print(f"\n❌ APERÇUS : {len(fautifs)} non conformes sur {len(confrontes)} confrontés")
        return 1
    print(f"\n✅ APERÇUS : les {len(confrontes)} aperçus confrontés sont des mots du séif, verbatim, coupes déclarées")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
