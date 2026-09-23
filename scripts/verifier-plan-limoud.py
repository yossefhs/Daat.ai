#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le plan d'étude couvre-t-il vraiment les simanim qu'il annonce ?

`verifier-limoud.py` compare deux CHEMINS — le tableau inscrit dans les pages et
le JSON que lit le courriel — et vérifie qu'ils disent la même chose. Il ne
compare ni l'un ni l'autre au **Choul'han Aroukh**. Les deux pouvaient donc
s'accorder parfaitement sur un plan tronqué, et c'est ce qui s'est produit.

Trouvé le 23 septembre 2026, à partir d'un signalement sur le siman 298 : le plan
annonçait **742 séifim pour 1 053 réels — 311 n'étaient programmés aucun jour**.
Quarante simanim étaient tronqués, sous deux formes :

- le plan s'arrête sous le compte réel — siman 298 au séif 10 quand le texte dit
  lui-même `ובו טו סעיפים`, siman 301 au séif 14 pour 51 séifim, siman 308 au
  séif 14 pour 52 ;
- ou il dépasse — siman 258, quatre séifim annoncés là où la source n'en a qu'un.

La racine était dans `generate-limoud-plan.cjs` : son tableau `SEIFIM_COUNT` était
écrit en dur et, comme son commentaire l'indiquait, « extrait des
niveau-1-base.html ». Le plan héritait donc de la troncature des PAGES — trente et
un simanim du site ne reproduisent qu'une partie de leur siman — au lieu de suivre
la source. Le compte vient désormais de `data/seifim-count.json`, que
`scripts/generer-seifim-count.py` tire de Sefaria.

Ce contrôle ferme l'écart restant : il confronte le plan À LA SOURCE, séif par
séif, et nomme ce qui n'est programmé aucun jour.

  python3 scripts/verifier-plan-limoud.py [--bref]
"""
import argparse, json, math, pathlib, sys

SITE = pathlib.Path(__file__).resolve().parent.parent
PLAN = SITE / "data/limoud-plan.json"
COMPTES = SITE / "data/seifim-count.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bref", action="store_true")
    a = ap.parse_args()

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    comptes = json.loads(COMPTES.read_text(encoding="utf-8"))["orach-chayim"]

    couvert = {}
    for e in plan["entries"]:
        n = e["siman"]["num"]
        deb, fin = e["seifRange"]
        couvert.setdefault(n, set()).update(range(deb, fin + 1))

    manquants, surnumeraires = [], []
    total_reel = total_prevu = 0
    for n in sorted(couvert):
        reel = comptes.get(str(n))
        if reel is None:
            print(f"  siman {n} : absent de {COMPTES.name} — compte inconnu")
            continue
        total_reel += reel
        total_prevu += len(couvert[n] & set(range(1, reel + 1)))
        absents = sorted(set(range(1, reel + 1)) - couvert[n])
        au_dela = sorted(s for s in couvert[n] if s > reel)
        if absents:
            manquants.append((n, reel, absents))
        if au_dela:
            surnumeraires.append((n, reel, au_dela))

    print(f"{len(couvert)} simanim au plan · {plan['meta']['totalDays']} journées")
    print(f"séifim du Choul'han Aroukh : {total_reel} · programmés : {total_prevu}"
          f" ({total_prevu/total_reel:.0%})" if total_reel else "")

    if manquants and not a.bref:
        print(f"\n→ {len(manquants)} siman(im) dont des séifim ne sont programmés aucun jour :")
        for n, reel, absents in manquants:
            apercu = absents if len(absents) <= 10 else f"{absents[:10]}… ({len(absents)})"
            print(f"   siman {n:3d} : {reel} séifim à la source · absents {apercu}")
    if surnumeraires and not a.bref:
        print(f"\n→ {len(surnumeraires)} siman(im) dont le plan annonce des séifim inexistants :")
        for n, reel, au_dela in surnumeraires:
            print(f"   siman {n:3d} : la source en compte {reel} · le plan va jusqu'à {max(au_dela)}")

    if manquants or surnumeraires:
        perdus = sum(len(x[2]) for x in manquants)
        jours = sum(max(1, math.ceil(comptes[str(n)] / plan["meta"]["seifimPerDay"]))
                    for n in couvert if str(n) in comptes)
        print(f"\n{perdus} séifim ne sont programmés aucun jour.")
        print(f"Un plan fidèle à la source demanderait {jours} journées, contre "
              f"{plan['meta']['totalDays']} aujourd'hui.")
        print("Régénérer déplace toutes les dates à venir : c'est une décision, pas un correctif.")
        return 1
    print("\n✅ Chaque séif de chaque siman du plan est programmé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
