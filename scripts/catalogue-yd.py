#!/usr/bin/env python3
"""Complète les entrées Yoré Déa du catalogue avec numHe / titleHe / titleEn.

`npm run build` reconstruit data/simanim-disponibles.json depuis le disque, mais il
ne sait extraire que le titre français (le <title> des index YD porte le numéro en
chiffres arabes, pas en numéral hébreu). Les trois champs manquants sont donc
injectés ici, à partir d'un fichier de titres au format :

    119|קי״ט|נאמנות החשוד בדברים הנאכלים|The ḥashud — the trustworthiness of one suspected

Usage : python3 scripts/catalogue-yd.py /tmp/p/catalogue-119-122.txt
Idempotent : réécrit les trois champs, ne touche à rien d'autre.
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(path):
    titres = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        num, he, tHe, tEn = line.split("|")
        titres[int(num)] = (he.strip(), tHe.strip(), tEn.strip())

    p = os.path.join(ROOT, "data", "simanim-disponibles.json")
    d = json.load(open(p, encoding="utf-8"))
    touched = 0
    for s in d["simanim"]:
        if not str(s.get("path", "")).startswith("sources/yoreh-deah/"):
            continue
        t = titres.get(s["num"])
        if not t:
            continue
        s["numHe"], s["titleHe"], s["titleEn"] = t
        touched += 1
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(p, "a", encoding="utf-8").write("\n")
    print(f"catalogue : {touched} entrée(s) Yoré Déa complétée(s)")

if __name__ == "__main__":
    main(sys.argv[1])
