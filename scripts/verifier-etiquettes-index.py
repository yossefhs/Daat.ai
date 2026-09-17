#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le résumé étiqueté « (סעיף ט) » est-il bien celui du séif ט ?

Le bloc d'index d'Orah Haïm résume le siman séif par séif et étiquette chaque
résumé de son numéro. Ce numéro est une affirmation, et la règle absolue du dépôt
la vise directement : « toute référence doit être exactement celle du Choul'han
Aroukh — le numéro du séif, la découpe, l'ordre ». C'est ce que le siman 243 avait
montré au niveau 1 ; rien ne le contrôlait sur les pages d'index.

Trouvé au siman 25 : le CHAPEAU du siman — « דיני תפלין בפרטות, ובו י״ג סעיפים » —
avait reçu l'étiquette « (סעיף א) », et tous les séifim s'en trouvaient décalés
d'un cran. Ce qui est donné comme le séif ט y est le séif ח ; ce qui est donné
comme le séif י est le séif ט, et ainsi jusqu'au bout.

Le contrôle compare chaque résumé au séif qu'il revendique, par recouvrement de
mots, et dit lequel il reproduit réellement. Quand tous les écarts sont du même
sens, il le nomme : « décalage de +1 », qui se corrige d'un seul geste.
"""
import argparse, json, re, subprocess, sys, unicodedata, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
RE_BLOC = re.compile(r'<div class="seif-text-he">(.*?)</div>', re.S)
RE_SEIF = re.compile(r'\(\s*(?:סעיף|סעיפים)\s*([^)]{1,12})\)')
UNI = {c: i + 1 for i, c in enumerate("אבגדהוזחט")}
DIZ = {"י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60, "ע": 70, "פ": 80, "צ": 90}


def plat(s):
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()


def mots(s):
    return [re.sub(r'[יו]', '', w) for w in re.findall(r'[א-ת]{3,}', plat(s))]


def val(l):
    s = re.sub(r'[^א-ת]', '', l)
    if s in ("טו", "טז"): return 9 + UNI[s[1]]
    n = 0
    for c in s:
        if c in DIZ: n += DIZ[c]
        elif c in UNI: n += UNI[c]
        else: return None
    return n or None


def recouvre(a, b):
    ma = mots(a)
    if not ma: return 0.0
    mb = set(mots(b))
    return sum(1 for w in ma if w in mb) / len(ma)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--siman", nargs="*", type=int)
    ap.add_argument("--details", action="store_true")
    a = ap.parse_args()
    nums = a.siman or [int(d.name.split("-")[1])
                       for d in sorted((RACINE / "sources/orah-haim").glob("siman-*"),
                                       key=lambda p: int(p.name.split("-")[1]))]
    pages, fautifs = 0, []
    for n in nums:
        p = RACINE / f"sources/orah-haim/siman-{n}/index.html"
        if not p.exists(): continue
        t = p.read_text(encoding="utf-8")
        m = RE_BLOC.search(t)
        if not m: continue
        bloc = plat(m.group(1))
        etiq = list(RE_SEIF.finditer(bloc))
        if len(etiq) < 3: continue
        u = f"https://www.sefaria.org/api/texts/Shulchan_Arukh,_Orach_Chayim.{n}?context=0&pad=0"
        o = subprocess.run(["curl", "-s", u], capture_output=True, text=True, timeout=60).stdout
        try: sef = json.loads(o).get("he", [])
        except Exception: continue
        if not isinstance(sef, list) or len(sef) < 2: continue
        pages += 1
        ecarts, debut = [], 0
        for e in etiq:
            k = val(e.group(1))
            resume = bloc[debut:e.start()].strip()
            debut = e.end()
            if k is None or len(mots(resume)) < 4: continue
            scores = [(recouvre(resume, sef[j]), j + 1) for j in range(len(sef))]
            best, vrai = max(scores)
            if best >= 0.5 and vrai != k:
                ecarts.append((k, vrai, resume[:60]))
        if ecarts:
            decalages = {v - k for k, v, _ in ecarts}
            uniforme = decalages.pop() if len(decalages) == 1 else None
            fautifs.append((n, len(ecarts), uniforme, ecarts))
            print(f"  ❌ siman {n:3d} : {len(ecarts)} étiquette(s) fausse(s)"
                  + (f" — décalage uniforme de {uniforme:+d}" if uniforme else " — écarts non uniformes"))
            if a.details:
                for k, vrai, ex in ecarts[:4]:
                    print(f"        donné (סעיף {k}) · est en fait le séif {vrai} · {ex}")
    print(f"\n{pages} page(s) d'index dont les résumés sont étiquetés séif par séif")
    print(f"→ {len(fautifs)} portant au moins une étiquette qui ne désigne pas le bon séif")
    if fautifs:
        print("   " + " ".join(str(x[0]) for x in fautifs))
    return 1 if fautifs else 0


if __name__ == "__main__":
    sys.exit(main())
