#!/usr/bin/env python3
"""Confronte le texte source (Mehaber + Rama) des simanim Yoré Déa aux sources
Sefaria — verbatim, consonnes identiques.

Usage : python3 scripts/verify-yd-source.py 119 120 121
Sort en code 1 si une divergence est détectée.

Invariant vérifié, pour chaque siman N :
  - la CONCATÉNATION des <blockquote class="text-source"> de niveau-1-base
    reproduit EXACTEMENT la concaténation des seifim du Choul'han Aroukh Yoré Déa
    sur Sefaria (comparaison sur les seules consonnes hébraïques : nikud,
    ponctuation, balises et espaces sont ignorés) ;
  - le titre-chapeau de Sefaria (« דין … ובו י״ג סעיפים ») est facultatif :
    il est retiré du texte de référence s'il n'est pas repris par la page ;
  - parité FR/HE/EN du texte source.

Rappel : le Choul'han Aroukh HaRav ne couvre pas Yoré Déa. Le niveau-4 des pages
Yoré Déa est `niveau-4-halakha` (psika pratique), pas `niveau-4-daat-harav` ;
c'est le niveau-1 qui porte le texte source, et c'est donc lui qu'on confronte.
"""
import sys, re, json, subprocess, unicodedata, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE_CONS = re.compile(r'[א-ת]')
CHAPEAU = re.compile(r'^\s*<b>.*?</b>\s*(<br\s*/?>)?', re.S)

def fetch_yd(n):
    url = ("https://www.sefaria.org/api/texts/"
           "Shulchan_Arukh,_Yoreh_De%27ah." + str(n) + "?context=0&pad=0")
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=60).stdout
    d = json.loads(out)
    he = d.get("he", [])
    return he if isinstance(he, list) else [he]

def consonants(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = unicodedata.normalize('NFC', s)
    return "".join(HE_CONS.findall(s))

def blocs(html):
    return re.findall(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>', html, re.S)

def page_source(path):
    html = open(path, encoding="utf-8").read()
    b = blocs(html)
    return len(b), consonants("".join(b))

def main(nums):
    ok = True
    for n in nums:
        sef = fetch_yd(n)
        if not sef:
            print(f"\n=== Siman {n} — ABSENT de Sefaria ==="); ok = False; continue
        avec = consonants("".join(sef))
        sans = consonants("".join([CHAPEAU.sub('', sef[0])] + sef[1:]))
        print(f"\n=== Siman {n} — Yoré Déa : {len(sef)} seifim sur Sefaria ===")
        pages = {lang: os.path.join(ROOT, f"sources/yoreh-deah/siman-{n}/niveau-1-base{suf}.html")
                 for lang, suf in [("FR", ""), ("HE", "-he"), ("EN", "-en")]}
        cons_by_lang = {}
        for lang, path in pages.items():
            if not os.path.exists(path):
                print(f"  {lang}: FICHIER ABSENT {path}"); ok = False; continue
            nb, cons = page_source(path)
            cons_by_lang[lang] = cons
            src_ok = cons in (avec, sans)
            print(f"  {lang}: {nb} blocs text-source | "
                  f"texte source vs Sefaria : {'✅ IDENTIQUE' if src_ok else '❌ DIVERGENCE'}")
            if not src_ok:
                ok = False
                ref = sans
                for i, (a, b) in enumerate(zip(cons, ref)):
                    if a != b:
                        print(f"      1re divergence @{i} : page…{cons[max(0,i-25):i+10]}")
                        print(f"                          sefaria…{ref[max(0,i-25):i+10]}")
                        break
                else:
                    print(f"      longueurs : page={len(cons)} sefaria={len(ref)} (l'un est préfixe de l'autre)")
        if len(set(cons_by_lang.values())) > 1:
            print("  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE"); ok = False
        elif cons_by_lang:
            print("  parité FR/HE/EN du texte source : ✅ identique")
    print("\n" + ("✅ VÉRIFICATION SOURCE : tout est conforme" if ok
                  else "❌ VÉRIFICATION SOURCE : divergence(s) détectée(s) — NE PAS PUBLIER"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main([int(a) for a in sys.argv[1:]]))
