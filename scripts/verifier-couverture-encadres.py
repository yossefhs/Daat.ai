#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garde-fou de couverture — chaque séif a-t-il son encadré, et la page a-t-elle le séif ?

Ce contrôle est né d'un chiffre faux que j'utilisais moi-même. Pour savoir où
la campagne d'encadrés en était, je comptais dans le niveau 1 la chaîne exacte
« Ce que dit ce séif : » — et j'obtenais 204 simanim d'Orah Haïm « sans
encadré ». Le compte était faux de bout en bout : les pages plus anciennes
écrivent la même chose autrement — « Trois idées dans ce séif », « Ce que dit
le séif — pas à pas », « מה אומר הסעיף — צעד אחר צעד », « What this séif
says: » avec l'accent français. Le siman 17 était compté vide dans les trois
langues alors qu'il est servi dans les trois. Un lot entier d'encadrés était
écrit et prêt à être posé sur six simanim qui les avaient déjà : il aurait
donné au lecteur DEUX encadrés par séif.

La leçon est celle que le dépôt a déjà apprise deux fois : on ne mesure pas un
contenu par la chaîne qui l'annonce, on le mesure par sa PLACE. Le contrôle
reprend donc l'ancrage du moteur — le bloc ``<blockquote class="text-source">``
qui reproduit le séif n — et pose deux questions dans cet ordre :

  1. La page REPRODUIT-ELLE le séif ? Combien de blocs source pour combien de
     séifim au Choul'han Aroukh.
  2. Le séif reproduit PORTE-T-IL un encadré ? Y a-t-il un ``key-point`` entre
     le début de son bloc et la fin de sa section, quel que soit son intitulé.

La seconde question est celle de la campagne. La PREMIÈRE a trouvé autre chose,
et de plus grave : vingt-six simanim d'Orah Haïm dont le niveau 1 ne reproduit
qu'une partie du siman — 264 séifim du Choul'han Aroukh absents — et un seul,
le 32, qui le dit au lecteur (« Plan de l'étude — les 8 familles des נ״ב
סעיפים », chaque bloc intitulé « Texte représentatif »). Les vingt-cinq autres
présentent sous « Le texte du Choul'han Aroukh » un texte partiel sans l'annoncer.
C'est la même famille de défaut que les blocs d'index : une matière donnée au
lecteur pour davantage que ce qu'elle est.

Le script ne répare rien et n'écrit dans aucune page : il compte, et il nomme.
Combler ces séifim est un travail de contenu, qui revient au Rav.

  python3 scripts/verifier-couverture-encadres.py [--section orah-haim] [N …] [--bref]
"""
import argparse, importlib.util, pathlib, re, sys

SITE = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("enc", SITE / "scripts/encadres-par-source.py")
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)
va = enc.va

RE_TS = re.compile(r'<blockquote class="text-source"')
RE_KP = re.compile(r'<div class="(?:key-point|remember|definition)"')
# Le siman 32 annonce sa sélection ; le contrôle cherche cette annonce pour
# distinguer une page partielle ASSUMÉE d'une page partielle muette.
RE_DECL = re.compile(r'repr[ée]sentatif|s[ée]lection|extraits choisis|נציג|representative')


def examiner(section, n):
    d = SITE / f"sources/{enc.REPERTOIRES[section]}/siman-{n}"
    f = d / "niveau-1-base.html"
    if not f.exists():
        return None
    src = va.seifim(enc.OUVRAGES[section], n)
    if not src:
        return {"siman": n, "erreur": "source Sefaria indisponible"}
    sq = [va.squelette(x) for x in src]
    courts = [" ".join(enc.mots_utiles(x)) for x in src]
    t = f.read_text(encoding="utf-8", errors="replace")
    blocs = len(RE_TS.findall(t))
    couverts, ancres = 0, 0
    nus = []
    # L'étendue d'un séif sur la page n'est pas sa « section » au sens de
    # l'ancrage : beaucoup de pages titrent « Traduction française » en <h3>
    # sous le texte hébreu, et la section du bloc se referme donc AVANT
    # l'encadré, qui suit la traduction. Mesuré ainsi, le séif א des simanim
    # 1 à 5 passait pour nu alors qu'il porte son encadré quelques lignes
    # plus bas. L'étendue retenue va donc du bloc source au bloc source
    # SUIVANT — ce qui est sur la page la part du séif, et rien de plus.
    debuts = [m.start() for m in RE_TS.finditer(t)]
    for j in range(1, len(src) + 1):
        at, _ = enc.ancrage(t, sq, j, courts, src)
        if at is None:
            continue
        ancres += 1
        deb = max([d for d in debuts if d < at], default=-1)
        if deb == -1:
            continue
        suivants = [d for d in debuts if d > deb]
        fin = suivants[0] if suivants else max(at, len(t))
        if RE_KP.search(t[deb:max(fin, at)]):
            couverts += 1
        else:
            nus.append(j)
    # Un séif peut être servi par un encadré qui ne tient pas dans SON étendue :
    # les simanim 238 et 239 rassemblent les leurs dans la section d'analyse qui
    # suit les deux blocs source. On ne signale donc un siman que si la page
    # compte MOINS d'encadrés que de séifim — là, il en manque vraiment un.
    boites = len(RE_KP.findall(t))
    return {"siman": n, "seifim": len(src), "blocs": blocs, "ancres": ancres,
            "couverts": couverts, "nus": nus, "boites": boites,
            "declare": bool(RE_DECL.search(t))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("simanim", nargs="*", type=int)
    ap.add_argument("--section", default="orah-haim", choices=sorted(enc.REPERTOIRES))
    ap.add_argument("--bref", action="store_true")
    a = ap.parse_args()

    base = SITE / f"sources/{enc.REPERTOIRES[a.section]}"
    cibles = a.simanim or sorted(int(p.name.split("-")[1]) for p in base.glob("siman-*")
                                 if (p / "niveau-1-base.html").exists())
    partielles, incompletes, erreurs = [], [], []
    ts = tc = 0
    for n in cibles:
        r = examiner(a.section, n)
        if r is None:
            continue
        if r.get("erreur"):
            erreurs.append(r)
            continue
        ts += r["seifim"]
        tc += r["couverts"]
        if r["blocs"] < r["seifim"]:
            partielles.append(r)
        if r["nus"] and r["boites"] < r["seifim"]:
            incompletes.append(r)
        if not a.bref:
            drapeau = ""
            if r["blocs"] < r["seifim"]:
                drapeau = f" · PAGE PARTIELLE {r['blocs']}/{r['seifim']} blocs" \
                          + ("" if r["declare"] else " — NON DÉCLARÉE")
            print(f"  siman {n:3d} : {r['couverts']}/{r['seifim']} séifim portent un encadré{drapeau}")

    print(f"\n{ts} séifim du Choul'han Aroukh dans « {a.section} » · "
          f"{tc} portent un encadré ({tc/ts:.0%})" if ts else "\naucun siman lu")
    if incompletes:
        print(f"\n→ {len(incompletes)} siman(im) qui comptent moins d'encadrés que de séifim :")
        for r in incompletes:
            print(f"   siman {r['siman']:3d} : {r['boites']} encadrés pour {r['seifim']} séifim"
                  f" · séifim sans encadré dans leur étendue : {r['nus']}")
    if partielles:
        manque = sum(r["seifim"] - r["blocs"] for r in partielles)
        muettes = [r for r in partielles if not r["declare"]]
        print(f"\n→ {len(partielles)} siman(im) dont le niveau 1 ne reproduit "
              f"qu'une partie du siman — {manque} séifim absents :")
        for r in partielles:
            print(f"   siman {r['siman']:3d} : {r['blocs']}/{r['seifim']} blocs"
                  f"{'' if r['declare'] else '  ← sélection NON DÉCLARÉE'}")
        if muettes:
            print(f"\n   {len(muettes)} présentent ce texte partiel sans l'annoncer au lecteur.")
            print("   Constat, non verdict : combler un séif est un travail de contenu.")
    if erreurs:
        print("\n→ source indisponible : " + ", ".join(str(r["siman"]) for r in erreurs))
    return 1 if partielles or incompletes else 0


if __name__ == "__main__":
    sys.exit(main())
