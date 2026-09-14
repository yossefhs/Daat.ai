#!/usr/bin/env python3
"""Confronte le texte source (Mehaber + Rama) des simanim de Hilkhot Chabbat aux
sources Sefaria — verbatim, consonnes identiques.

Usage : python3 scripts/verify-chabbat-source.py 292 301 308
        python3 scripts/verify-chabbat-source.py --tous          # les 124
        python3 scripts/verify-chabbat-source.py --tous --bref   # une ligne par siman

Sort en code 1 si une divergence est détectée.

C'est l'équivalent, pour Hilkhot Chabbat, de `verify-yd-source.py` (Yoré Déa) et
de `verify-oh-source.py` (Orah Haïm quotidien). Il manquait : `CLAUDE.md` le
notait — « Hilkhot Shabbat n'en a pas encore » — et c'est le plus gros
compartiment du site, 124 simanim.

Ce qu'aucune des trois portes historiques ne voit et que celle-ci voit :
`verifier-citations.py` juge les CITATIONS (ce que la page met entre guillemets),
pas la RECOPIE du texte de base ; `verifier-alignement.py` juge la correspondance
entre l'étiquette de séif annoncée et le contenu du bloc, mais ne confronte pas
ce contenu à Sefaria ; `audit-simanim.py` est structurel. Une page peut donc
passer les trois en développant les abréviations du Choul'han Aroukh, en laissant
tomber une parenthèse de source, en fondant deux séifim en un bloc ou en n'en
publiant que six sur dix.

Deux invariants, pour chaque siman N :

  1. **Le texte.** La CONCATÉNATION des `<blockquote class="text-source">` de
     `niveau-1-base` reproduit exactement la concaténation des séifim que Sefaria
     donne pour `Shulchan_Arukh, Orach_Chayim N` — consonnes hébraïques seules,
     nikoud, ponctuation, balises et espaces ignorés. Le titre-chapeau de Sefaria
     (« דין … ובו נ״א סעיפים ») est facultatif : il est retiré du texte de
     référence si la page ne le reprend pas.

  2. **La découpe.** Le NOMBRE de blocs source est comparé au nombre de séifim.
     C'est la règle absolue posée après le siman 243 : la découpe entre séifim
     fait partie de ce qui doit être exactement comme dans le Choul'han Aroukh.
     Une page qui fragmente un séif en trois, ou qui n'en publie que six sur dix,
     reproduit peut-être un texte juste mais ne donne pas la source telle qu'elle
     est. L'écart est signalé comme AVERTISSEMENT et non comme erreur, parce que
     le texte peut être intégralement exact malgré une découpe différente — les
     deux faits sont distincts et se lisent séparément.

Plus la parité FR/HE/EN du texte source : une même source doit être donnée au
lecteur français, hébreu et anglais sous la même forme.

Une étiquette que le bloc se donne lui-même — « <strong>סעיף ח:</strong> » en
hébreu, « <strong>Seif ח:</strong> » en anglais — n'est pas du texte du Choul'han
Aroukh et est retirée avant comparaison ; sans quoi toute page qui numérote ses
blocs serait déclarée divergente, et toute page qui les numérote en hébreu le
serait sans que l'anglaise le soit.
"""
import sys, re, json, subprocess, unicodedata, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE_CONS = re.compile(r'[א-ת]')
CHAPEAU = re.compile(r'^\s*<b>.*?</b>\s*(<br\s*/?>)?', re.S)
ETIQ = re.compile(r'^\s*<strong>\s*(?:סעיפים|סעיף|Seifim|Seif)\b[^<]*</strong>\s*')
LANGS = [("FR", ""), ("HE", "-he"), ("EN", "-en")]


def fetch(n):
    url = ("https://www.sefaria.org/api/texts/"
           "Shulchan_Arukh,_Orach_Chayim." + str(n) + "?context=0&pad=0")
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True,
                         timeout=60).stdout
    he = json.loads(out).get("he", [])
    return he if isinstance(he, list) else [he]


def consonants(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = unicodedata.normalize('NFC', s)
    return "".join(HE_CONS.findall(s))


def squelette(s):
    """Le texte privé de ses matres lectionis — même normalisation que
    `verifier-alignement.py`.

    Sans elle, ce garde-fou serait illisible : le siman 271 écrit « כשיבוא »
    là où Sefaria écrit « כשיבא », le 252 « המתרים » pour « המותרים ». C'est du
    ktiv haser/malé, le faux positif dominant du dépôt, et il ne dit rien de la
    fidélité au Choul'han Aroukh. Deux verdicts sont donc rendus, et ils ne se
    valent pas : IDENTIQUE (consonnes strictement égales) et ÉQUIVALENT (égal
    aux matres lectionis près). Seul un écart qui SURVIT au squelette est un
    écart de texte — un mot remplacé, une abréviation développée, une
    parenthèse de source perdue, un séif tronqué.
    """
    return re.sub(r"[יו]", "", s)


def page_source(path):
    html = open(path, encoding="utf-8").read()
    b = re.findall(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>',
                   html, re.S)
    return len(b), consonants("".join(ETIQ.sub("", x) for x in b))


def chemin(n, suf):
    return os.path.join(ROOT, f"sources/shabbat/siman-{n}/niveau-1-base{suf}.html")


def un_siman(n, bref):
    """Renvoie (texte_ok, decoupe_ok) et imprime le détail."""
    sef = fetch(n)
    if not sef:
        print(f"\n=== Siman {n} — aucun séif sur Sefaria (page-passerelle attendue) ===")
        ok = True
        for lang, suf in LANGS:
            p = chemin(n, suf)
            if not os.path.exists(p):
                print(f"  {lang}: FICHIER ABSENT {p}"); ok = False; continue
            nb, _ = page_source(p)
            bon = (nb == 0)
            print(f"  {lang}: {nb} blocs | "
                  f"{'✅ aucun séif prétendu' if bon else '❌ la page cite un séif que la source ne donne pas'}")
            ok = ok and bon
        return ok, True

    avec = consonants("".join(sef))
    sans = consonants("".join([CHAPEAU.sub('', sef[0])] + sef[1:]))
    texte_ok, decoupe_ok, cons_par_langue, nb_par_langue = True, True, {}, {}
    equivalents = []

    for lang, suf in LANGS:
        p = chemin(n, suf)
        if not os.path.exists(p):
            if not bref:
                print(f"  {lang}: FICHIER ABSENT {p}")
            texte_ok = False
            continue
        nb, cons = page_source(p)
        cons_par_langue[lang] = cons
        nb_par_langue[lang] = nb
        if cons not in (avec, sans):
            if squelette(cons) in (squelette(avec), squelette(sans)):
                equivalents.append(lang)
            else:
                texte_ok = False
        if nb != len(sef):
            decoupe_ok = False

    if bref:
        blocs = "/".join(str(nb_par_langue.get(l, "—")) for l, _ in LANGS)
        parite = "" if len(set(cons_par_langue.values())) <= 1 else " ⚠️ parité"
        etat = "❌" if not texte_ok else ("≈ " if equivalents else "✅")
        print(f"  siman {n:3d} : {len(sef):2d} séifim · blocs {blocs:>8s} · "
              f"texte {etat} · découpe {'✅' if decoupe_ok else '⚠️ '}{parite}")
        return texte_ok, decoupe_ok and len(set(cons_par_langue.values())) <= 1

    print(f"\n=== Siman {n} — Hilkhot Chabbat : {len(sef)} séifim sur Sefaria ===")
    for lang, suf in LANGS:
        p = chemin(n, suf)
        if not os.path.exists(p):
            print(f"  {lang}: FICHIER ABSENT {p}"); continue
        nb, cons = nb_par_langue[lang], cons_par_langue[lang]
        src_ok = cons in (avec, sans)
        equiv = (not src_ok) and squelette(cons) in (squelette(avec), squelette(sans))
        dec = "✅" if nb == len(sef) else f"⚠️  {nb} blocs pour {len(sef)} séifim"
        verdict = ("✅ IDENTIQUE" if src_ok else
                   "≈ ÉQUIVALENT (ktiv haser/malé seulement)" if equiv else "❌ DIVERGENCE")
        print(f"  {lang}: {nb} blocs | texte vs Sefaria : {verdict} | découpe : {dec}")
        if not src_ok and not equiv:
            # Comparer au plus proche des deux textes de référence, et non
            # toujours à « sans chapeau » : une page qui reprend le chapeau du
            # siman (« דיני קידוש על היין ובו י״ז סעיפים ») divergeait alors dès
            # le caractère 0, ce qui masquait la vraie divergence, plus loin.
            ref = max((avec, sans), key=lambda r: len(os.path.commonprefix([cons, r])))
            # La divergence rapportée est celle qui SURVIT au squelette : la
            # première divergence brute est presque toujours un ktiv haser/malé,
            # et la montrer envoyait le lecteur sur une fausse piste. Les indices
            # sont donc ceux du texte squelettisé, et l'extrait en est tiré.
            sc, sr = squelette(cons), squelette(ref)
            for i, (a, b) in enumerate(zip(sc, sr)):
                if a != b:
                    print(f"      1re divergence réelle @{i} (hors ktiv) :")
                    print(f"          page   …{sc[max(0,i-30):i+12]}")
                    print(f"          sefaria…{sr[max(0,i-30):i+12]}")
                    break
            else:
                print(f"      longueurs (squelette) : page={len(sc)} sefaria={len(sr)} "
                      f"— l'un est préfixe de l'autre : la page tronque ou ajoute")

    if len(set(cons_par_langue.values())) > 1:
        print("  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE")
        decoupe_ok = False
    elif cons_par_langue:
        print("  parité FR/HE/EN du texte source : ✅ identique")
    return texte_ok, decoupe_ok


def main(argv):
    bref = "--bref" in argv
    nums = [int(a) for a in argv if a.isdigit()]
    if "--tous" in argv:
        nums = sorted(int(d.split("-")[1]) for d in os.listdir(os.path.join(ROOT, "sources/shabbat"))
                      if d.startswith("siman-"))
    if not nums:
        print(__doc__); return 2
    if bref:
        print(f"=== Texte source de Hilkhot Chabbat vs Sefaria — {len(nums)} siman(im) ===")
    faux_texte, faux_decoupe = [], []
    for n in nums:
        t, d = un_siman(n, bref)
        if not t: faux_texte.append(n)
        if not d: faux_decoupe.append(n)
    print(f"\n{len(nums)} siman(im) confronté(s) au Choul'han Aroukh")
    print(f"→ {len(faux_texte)} dont le texte source diverge de Sefaria "
          f"au-delà du ktiv haser/malé")
    if faux_texte: print("   " + " ".join(map(str, faux_texte)))
    print(f"→ {len(faux_decoupe)} dont la découpe ou la parité s'écarte de la source")
    if faux_decoupe: print("   " + " ".join(map(str, faux_decoupe)))
    return 0 if not faux_texte else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
