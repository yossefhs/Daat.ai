#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le nombre de séifim de chaque siman, pris À LA SOURCE.

`generate-limoud-plan.cjs` portait ce nombre dans une table écrite en dur, et
son propre commentaire disait d'où elle venait : « extrait des niveau-1-base.html ».
C'est la racine du défaut. Une page ne reproduit pas toujours tout le siman —
trente et un simanim du site sont dans ce cas — et le plan d'étude héritait donc
de la troncature des pages au lieu de suivre le Choul'han Aroukh.

Mesuré le 23 septembre 2026 : le plan annonçait **742 séifim pour 1 053 réels**.
**311 séifim n'étaient programmés aucun jour** — dont les séifim 11 à 15 du
siman 298, dont le texte dit pourtant lui-même `ובו טו סעיפים`. Quarante simanim
étaient tronqués, et deux formes de défaut coexistaient : le plan s'arrêtait au
séif 10 quand le siman en comptait 51 (siman 301), et il annonçait quatre séifim
là où la source n'en a qu'un (siman 258).

Le nombre vient désormais de Sefaria, et d'un fichier que le générateur lit.

  python3 scripts/generer-seifim-count.py [--write]
"""
import argparse, importlib.util, json, pathlib, sys

SITE = pathlib.Path(__file__).resolve().parent.parent
_s = importlib.util.spec_from_file_location("va", SITE / "scripts/verifier-alignement.py")
va = importlib.util.module_from_spec(_s)
_s.loader.exec_module(va)

SORTIE = SITE / "data/seifim-count.json"
OUVRAGES = {"shabbat": "Shulchan Arukh, Orach Chayim",
            "orah-haim": "Shulchan Arukh, Orach Chayim",
            "yoreh-deah": "Shulchan Arukh, Yoreh De'ah"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--sections", nargs="*", default=["shabbat", "orah-haim"],
                    choices=sorted(OUVRAGES))
    a = ap.parse_args()

    # Le fichier est STRUCTURÉ PAR OUVRAGE, et non par numéro seul. Les numéros
    # se recouvrent d'un ouvrage à l'autre — Yoré Déa 87 et Orah Haïm 87 sont deux
    # simanim différents — et `generate-limoud-plan.cjs` les indexe aujourd'hui par
    # numéro seul, tous compartiments confondus. Ce défaut est latent tant que le
    # plan ne couvre que l'Orah Haïm ; il ne doit pas être entretenu ici.
    compte, absents = {}, []
    for section in a.sections:
        base = SITE / f"sources/{section}"
        cle = "orach-chayim" if OUVRAGES[section].endswith("Orach Chayim") else "yoreh-deah"
        d = compte.setdefault(cle, {})
        for p in sorted(base.glob("siman-*"), key=lambda q: int(q.name.split("-")[1])):
            if not (p / "niveau-1-base.html").exists():
                continue
            n = int(p.name.split("-")[1])
            src = va.seifim(OUVRAGES[section], n)
            if not src:
                absents.append(f"{section}/{n}")
                continue
            d[str(n)] = len(src)

    total = sum(len(v) for v in compte.values())
    seifim = sum(sum(v.values()) for v in compte.values())
    print(f"{total} simanim lus à la source · {seifim} séifim")
    for k, v in compte.items():
        print(f"   {k:<14} {len(v)} simanim · {sum(v.values())} séifim")
    if absents:
        print(f"source indisponible : {absents}")
        return 1

    ancien = json.loads(SORTIE.read_text(encoding="utf-8")) if SORTIE.exists() else {}
    for cle, d in compte.items():
        av = ancien.get(cle, {})
        ecarts = {k: (av.get(k), v) for k, v in d.items() if av.get(k) != v}
        if av and ecarts:
            print(f"\n{cle} — {len(ecarts)} écart(s) avec le fichier existant :")
            for k, (a1, a2) in sorted(ecarts.items(), key=lambda x: int(x[0]))[:20]:
                print(f"   siman {k} : {a1} → {a2}")
    if a.write:
        SORTIE.write_text(json.dumps(compte, indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"\nécrit : {SORTIE.relative_to(SITE)}")
    else:
        print("\n(essai à blanc — relancer avec --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
