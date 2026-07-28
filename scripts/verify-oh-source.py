#!/usr/bin/env python3
"""Confronte le texte niveau-4 (Choul'han Aroukh HaRav) des simanim oh-quotidien
aux sources Sefaria — verbatim, consonnes identiques.

Usage : python3 scripts/verify-oh-source.py 71 72 73
Sort en code 1 si une divergence est détectée.

Vérifie, pour chaque siman N :
  - le nombre de blocs <details class="seif-details"> = nombre de seifim SA HaRav sur Sefaria ;
  - le texte hébreu source (.sa-he dans les blocs seif-details) reproduit EXACTEMENT
    le texte Sefaria (comparaison sur les consonnes hébraïques, nikud/ponctuation ignorés) ;
  - parité FR/HE/EN du texte source.
"""
import sys, re, json, subprocess, unicodedata, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE_CONS = re.compile(r'[א-ת]')  # lettres hébraïques (sans nikud)

def fetch_saharav(n):
    url = f"https://www.sefaria.org/api/texts/Shulchan_Arukh_HaRav,_Orach_Chayim.{n}?context=0&pad=0"
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=60).stdout
    d = json.loads(out)
    he = d.get("he", [])
    return he if isinstance(he, list) else [he]

def consonants(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = unicodedata.normalize('NFC', s)
    return "".join(HE_CONS.findall(s))

def seif_details_blocks(html):
    return re.findall(r'<details class="seif-details"[^>]*>(.*?)</details>', html, re.S)

def sahe_in(block):
    return re.findall(r'class="[^"]*\bsa-he\b[^"]*"[^>]*>(.*?)</', block, re.S)

def page_source_consonants(path):
    html = open(path, encoding="utf-8").read()
    blocks = seif_details_blocks(html)
    txt = "".join("".join(sahe_in(b)) for b in blocks)
    return len(blocks), consonants(txt)

def main(nums):
    ok = True
    for n in nums:
        sef = fetch_saharav(n)
        sef_cons = consonants("".join(sef))
        print(f"\n=== Siman {n} — SA HaRav : {len(sef)} seifim sur Sefaria ===")
        pages = {lang: os.path.join(ROOT, f"sources/orah-haim/siman-{n}/niveau-4-daat-harav{suf}.html")
                 for lang, suf in [("FR", ""), ("HE", "-he"), ("EN", "-en")]}
        cons_by_lang = {}
        for lang, path in pages.items():
            if not os.path.exists(path):
                print(f"  {lang}: FICHIER ABSENT {path}"); ok = False; continue
            nblocks, cons = page_source_consonants(path)
            cons_by_lang[lang] = cons
            cnt_ok = (nblocks == len(sef))
            src_ok = (cons == sef_cons)
            print(f"  {lang}: {nblocks} blocs seif-details "
                  f"[{'OK' if cnt_ok else f'≠ {len(sef)} ATTENDUS'}] | "
                  f"texte source vs Sefaria : {'✅ IDENTIQUE' if src_ok else '❌ DIVERGENCE'}")
            if not (cnt_ok and src_ok):
                ok = False
                if not src_ok:
                    # localiser la 1re divergence
                    for i, (a, b) in enumerate(zip(cons, sef_cons)):
                        if a != b:
                            print(f"      1re divergence @{i} : page…{cons[max(0,i-25):i+10]}")
                            print(f"                          sefaria…{sef_cons[max(0,i-25):i+10]}")
                            break
                    else:
                        print(f"      longueurs : page={len(cons)} sefaria={len(sef_cons)} (l'un est préfixe de l'autre)")
        if len(set(cons_by_lang.values())) > 1:
            print("  ⚠️  PARITÉ FR/HE/EN du texte source : DIVERGENTE"); ok = False
        else:
            print("  parité FR/HE/EN du texte source : ✅ identique")
    print("\n" + ("✅ VÉRIFICATION SOURCE : tout est conforme" if ok
                  else "❌ VÉRIFICATION SOURCE : divergence(s) détectée(s) — NE PAS PUBLIER"))
    return 0 if ok else 1

if __name__ == "__main__":
    nums = [int(x) for x in sys.argv[1:]]
    if not nums:
        print("usage: python3 scripts/verify-oh-source.py N [N...]"); sys.exit(2)
    sys.exit(main(nums))
