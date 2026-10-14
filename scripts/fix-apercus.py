#!/usr/bin/env python3
"""Remplace chaque aperçu NON CONFORME du niveau 4 (verifier-apercus.py) par l'INCIPIT de son séif — l'option A
de audit/apercus-niveau4.md.

Usage :
  python3 scripts/fix-apercus.py                    # SIMULATION : rien n'est écrit dans sources/
  python3 scripts/fix-apercus.py --releve FICHIER   # + la liste avant/après, un séif par entrée
  python3 scripts/fix-apercus.py --appliquer        # écrit les pages
  python3 scripts/fix-apercus.py 75 186 [--appliquer]

⚠️ La simulation est le défaut, à l'inverse de fix-classes.py et fix-liens-langue.py : la correction réécrit le
titre de plus de 1 300 séifs dans plusieurs centaines de pages.

L'INCIPIT est celui que pose scripts/generate-niveau-4.py (_seif_preview), la forme des 5 007 aperçus conformes de
Chabbat : le texte du séif, coupé à 110 caractères au plus sur une frontière de mot, suivi de « … » quand le séif
continue. Trois écarts, voulus :
  - le texte est le .sa-he DE LA PAGE, lu par le Lecteur de verify-oh-source.py (celui que verifier-apercus.py
    confronte), et non Sefaria : l'aperçu ne peut pas diverger du texte qu'il annonce ;
  - au séif 1, le CHAPEAU du siman (« … וּבוֹ N סְעִיפִים: ») est sauté : c'est le titre du siman, déjà affiché ;
  - la coupe ne laisse ni ponctuation ni tiret avant « … », et s'arrête avant une « … » de la source ou un dessin
    de lettre (32:36, 36:2), qu'un aperçu de texte enjamberait sans le dire.

CE QUI EST RÉÉCRIT : pour chaque séif dont UNE langue au moins porte un aperçu non conforme, l'aperçu des trois
langues — sauf un titre sans hébreu ou un <summary> nu, admis et laissés tels quels —, pour que FR, HE et EN
portent le même (CLAUDE.md, parité trilingue). Rien d'autre : seul le texte de span.seif-preview change, ni CSS,
ni style=, ni classe, ni balise — aucune empreinte de verify-oh-source.py n'est touchée.

CE QUI EST VÉRIFIÉ AVANT D'ÉCRIRE, page par page, sur la page réécrite (en mémoire) :
  - chaque aperçu réécrit est conforme pour verifier-apercus.py, et aucun aperçu ne change de classe ailleurs ;
  - la lecture de verify-oh-source.py est inchangée : mêmes blocs, même texte .sa-he (empreinte), même CSS
    (empreinte), mêmes fautes de forme ;
  - le fichier ne diffère qu'à l'intérieur des span.seif-preview visés.
Une page qui échoue à l'une de ces vérifications n'est pas écrite, et la sortie le dit (code 1).

Codes de sortie : 0 tout est prêt (ou écrit) · 1 au moins une page refusée par les vérifications.
"""
import sys, os, re, html, importlib.util, collections, tempfile, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("verifier_apercus", os.path.join(ROOT, "scripts", "verifier-apercus.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
V = A.V

MAX = 110                                       # generate-niveau-4.py, _seif_preview(max_chars=110)
QUEUE = " ,;:.—–-"
SPAN = re.compile(r'(<span class="seif-preview">)([^<]*)(</span>)')
BLOC = re.compile(r'<details class="seif-details"[^>]*>')


def incipit(bloc, rang):
    """L'aperçu d'un bloc lu par le Lecteur ({"txt", "img"}), de rang `rang` (0 pour le séif 1)."""
    t = re.sub(r"\s+", " ", bloc["txt"]).strip()
    avant = 0                                   # mots du chapeau sauté, pour situer les dessins
    if rang == 0 and V.chapeau(t):
        avant = len(V.sans_points(V.mots(t[:t.find(":")])))
        t = t[t.find(":") + 1:].strip()
    dessins = [r for r, _src, _alt in bloc["img"] if r > avant]
    mots, coupe, compte = [], False, avant
    for w in t.split(" "):
        if "…" in w or "..." in w:              # une « … » de la source : on s'arrête avant elle
            coupe = True
            break
        if mots and dessins and compte >= dessins[0]:   # un dessin de lettre (32:36, 36:2) : de même
            coupe = True
            break
        if mots and len(" ".join(mots + [w])) > MAX:
            coupe = True
            break
        mots.append(w)
        compte += len(V.sans_points(V.mots(w)))
    while mots and coupe:                       # ni ponctuation ni tiret avant « … »
        mots[-1] = mots[-1].rstrip(QUEUE)
        if re.search(r"[א-ת]", mots[-1]):
            break
        mots.pop()
    return " ".join(mots) + ("…" if coupe else "")


def langues(n):
    return {lang: p for n_, lang, p in A.pages([n])}


def lecture_voh(texte, chemin_tmp):
    open(chemin_tmp, "w", encoding="utf-8").write(texte)
    blocs, fautes, lx = V.lire_page(chemin_tmp)
    return [b["txt"] for b in blocs], fautes, lx.empreinte, lx.empreinte_css


def main(argv):
    appliquer = "--appliquer" in argv
    releve = argv[argv.index("--releve") + 1] if "--releve" in argv and argv.index("--releve") + 1 < len(argv) else None
    nums = [int(a) for a in argv if a.isdigit()]
    simanim = nums or [n for _s, r in V.SECTIONS for n in r]
    fd, tmp = tempfile.mkstemp(suffix=".html")
    os.close(fd)

    stats = collections.Counter()
    entrees, refus = [], []
    for n in simanim:
        pages = langues(n)
        if not pages:
            continue
        lus = {lang: A.lire(p) for lang, p in pages.items()}
        classes = {lang: [A.classer(b["apercu"], b["txt"], i)[0] for i, b in enumerate(bs)] for lang, bs in lus.items()}
        nb = {len(bs) for bs in lus.values()}
        if len(nb) != 1:
            refus.append((n, "*", f"nombre de blocs différent selon la langue ({sorted(nb)}) : parité impossible"))
            continue
        a_refaire = {i for lang in lus for i, c in enumerate(classes[lang]) if c in A.NON_CONFORMES}
        if not a_refaire:
            continue
        for lang, p in pages.items():
            bs = lus[lang]
            nouveaux = {}
            for i in sorted(a_refaire):
                if classes[lang][i] not in A.NON_CONFORMES + A.CONFORMES:
                    continue                    # titre sans hébreu, <summary> nu : admis, laissé tel quel
                neuf = incipit(bs[i], i)
                if unicodedata.normalize("NFC", neuf) != bs[i]["apercu"]:
                    nouveaux[i] = neuf
            if not nouveaux:
                continue
            brut = open(p, encoding="utf-8").read()
            debuts = [m.start() for m in BLOC.finditer(brut)]
            if len(debuts) != len(bs):
                refus.append((n, lang, f"{len(debuts)} <details> lus par motif, {len(bs)} blocs par le Lecteur"))
                continue
            morceaux, curseur, ok = [], 0, True
            for i, neuf in sorted(nouveaux.items()):
                fin_bloc = debuts[i + 1] if i + 1 < len(debuts) else len(brut)
                fin_titre = brut.find("</summary>", debuts[i], fin_bloc)
                m = SPAN.search(brut, debuts[i], fin_titre if fin_titre >= 0 else fin_bloc)
                vu = re.sub(r"\s+", " ", unicodedata.normalize("NFC", html.unescape(m.group(2)))).strip() if m else None
                if not m or vu != bs[i]["apercu"]:
                    refus.append((n, lang, f"séif {i + 1} : span.seif-preview introuvable ou autre que l'aperçu lu"))
                    ok = False
                    break
                morceaux += [brut[curseur:m.start(2)], html.escape(neuf, quote=False)]
                curseur = m.end(2)
            if not ok:
                continue
            nouveau = "".join(morceaux) + brut[curseur:]
            # les vérifications, sur la page réécrite
            avant, apres = lecture_voh(brut, tmp), lecture_voh(nouveau, tmp)
            if avant != apres:
                refus.append((n, lang, "la lecture de verify-oh-source.py change (texte, CSS ou forme)"))
                continue
            relus = A.lire(tmp)
            for i, b in enumerate(relus):
                c = A.classer(b["apercu"], b["txt"], i)[0]
                attendu = classes[lang][i] if i not in nouveaux else None
                if (attendu is None and c not in A.CONFORMES) or (attendu is not None and c != attendu):
                    refus.append((n, lang, f"séif {i + 1} : « {b['apercu'][:60]} » sort {c}"))
                    ok = False
            if not ok:
                continue
            for i, neuf in nouveaux.items():
                stats["non conformes" if classes[lang][i] in A.NON_CONFORMES else "conformes, pour la parité"] += 1
                entrees.append((n, i + 1, lang, bs[i]["apercu"], classes[lang][i], neuf))
            stats["pages"] += 1
            if appliquer:
                open(p, "w", encoding="utf-8").write(nouveau)
    if os.path.exists(tmp):
        os.remove(tmp)

    groupes = collections.OrderedDict()
    for n, s, lang, vieux, classe, neuf in entrees:
        groupes.setdefault((n, s), []).append((lang, vieux, classe, neuf))
    neufs_par_seif = [{unicodedata.normalize("NFC", neuf) for _l, _v, _c, neuf in g} for g in groupes.values()]
    print(("ÉCRIT" if appliquer else "SIMULATION — rien n'est écrit") +
          f" : {stats['pages']} pages, {len(groupes)} séifs, {stats['non conformes'] + stats['conformes, pour la parité']} aperçus "
          f"({stats['non conformes']} non conformes, {stats['conformes, pour la parité']} conformes réécrits pour la parité)")
    print(f"  séifs dont les langues réécrites reçoivent le même aperçu (forme NFC : l'ordre des signes de nikoud varie d'une "
          f"page à l'autre, l'écran non) : {sum(len(x) == 1 for x in neufs_par_seif)} sur {len(groupes)}")
    longueurs = sorted(len(neuf.split()) for *_x, neuf in entrees)
    if longueurs:
        print(f"  longueur des nouveaux aperçus : {longueurs[len(longueurs) // 2]} mots (médiane), "
              f"de {longueurs[0]} à {longueurs[-1]}")
    for n, lang, e in refus:
        print(f"  ⛔ siman {n} ({A.gematria(n)}) {lang} : {e} — page NON réécrite")

    if releve:
        with open(releve, "w", encoding="utf-8") as f:
            f.write("Correction A des aperçus du niveau 4 (scripts/fix-apercus.py) — avant / après, un séif par entrée.\n"
                    "Les aperçus remplacés y sont conservés : les condensations écrites à la main pour Orah Haïm\n"
                    "(voir audit/apercus-niveau4.md) ne vivent plus que dans ce relevé.\n")
            for (n, s), g in groupes.items():
                f.write(f"\n{n} ({A.gematria(n)}):{s}\n")
                vieux = collections.OrderedDict()
                for lang, v, c, _neuf in g:
                    vieux.setdefault((v, c), []).append(lang)
                for (v, c), ls in vieux.items():
                    f.write(f"   avant [{' '.join(ls)}] {c} : {v}\n")
                for neuf in sorted({neuf for *_x, neuf in g}):
                    f.write(f"   après [{' '.join(lang for lang, *_r, nf in g if nf == neuf)}] : {neuf}\n")
        print(f"  relevé avant/après : {releve}")
    return 1 if refus else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
