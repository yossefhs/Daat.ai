#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le bloc hébreu de la page d'index dit-il ce que sa source dit ?

Chaque page d'index de siman porte, sous un intertitre qui NOMME son ouvrage
— « שולחן ערוך, אורח חיים סימן ה׳ » ou « שולחן ערוך הרב (אדמו״ר הזקן) » —, un
`<div class="seif-text-he">` qui donne le début du siman en hébreu. C'est
souvent le premier hébreu que le lecteur rencontre, et c'est lui que Google
indexe.

**Aucun garde-fou ne le lisait.** `verifier-citations.py` juge ce que la page met
entre guillemets ; `verifier-alignement.py` juge les blocs `text-source` des
niveaux d'étude ; `verify-chabbat-source.py`, `verify-yd-source.py` et
`verify-oh-source.py` jugent le niveau 1. La page d'index n'était lue par aucun.

Ce que cela laissait passer, trouvé le 16 septembre 2026 par la session
ravabichid.org sur le siman 246 : le bloc disait **l'inverse** du Choul'han
Aroukh — « אסור להשכיר… ואסור אפילו להשאיל » là où le Mehaber écrit
« מותר להשאיל ולהשכיר ». Une interdiction publiée à la place d'une permission,
en tête de page, dans les trois langues.

Ce contrôle demande une seule chose, et elle est vérifiable : **le bloc doit se
retrouver mot pour mot dans l'ouvrage qu'il nomme**, d'un seul tenant. Deux
verdicts, comme pour les autres portes de source : IDENTIQUE (consonnes égales)
et ÉQUIVALENT (égal aux matres lectionis près), parce que le ktiv haser/malé est
le faux positif dominant du dépôt et ne dit rien de la fidélité.

Usage :
    python3 scripts/verifier-index-source.py                 # tout le site
    python3 scripts/verifier-index-source.py --section orah-haim
    python3 scripts/verifier-index-source.py --siman 246 244
    python3 scripts/verifier-index-source.py --details       # + l'écart trouvé
"""
import argparse, json, re, subprocess, sys, unicodedata, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
SECTIONS = {"shabbat": "sources/shabbat", "orah-haim": "sources/orah-haim",
            "yoreh-deah": "sources/yoreh-deah"}
OUVRAGES = {
    "sa":    ("Shulchan_Arukh,_Orach_Chayim",   "שולחן ערוך, אורח חיים"),
    "harav": ("Shulchan_Arukh_HaRav,_Orach_Chayim", "שולחן ערוך הרב"),
    "yd":    ("Shulchan_Arukh,_Yoreh_De%27ah",  "שולחן ערוך, יורה דעה"),
}
RE_BLOC = re.compile(r'<div class="seif-text-he">(.*?)</div>', re.S)
RE_HARAV = re.compile(r'שולחן ערוך הרב|ערוך הרב|'
                      r'(?:Shulchan|Shulḥan|Choul\'han|Shulhan)\s+(?:Aruch|Arukh|Aroukh)\s*HaRav',
                      re.I)
_cache = {}


def consonnes(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return "".join(re.findall(r'[א-ת]', s))


def squelette(s):
    return re.sub(r'[יו]', '', s)


# Un bloc d'index n'est pas toujours une citation d'un seul tenant : beaucoup sont
# des DIGESTS, qui sautent des passages et recousent des fragments de séifim
# différents (le siman 7 les sépare même par « · » et les étiquette « (סעיף ב) »).
# Un digest fidèle et un texte faux sont deux choses opposées, et la porte doit les
# séparer — sans quoi elle noie le siman 246, dont le bloc disait l'INVERSE du
# Mehaber, dans six cents pages qui ne font qu'abréger.
SEUIL_FRAGMENT = 8          # en deçà, un morceau n'est pas une citation
SEUIL_ETRANGER = 25         # au-delà, du texte qui n'est pas dans la source


def fragments_absents(bloc, src):
    """Les morceaux du bloc qu'on ne retrouve pas dans la source, dans l'ordre.

    Renvoie (nb_caracteres_absents, plus_long_absent, exemple). Un bloc dont tout
    se retrouve, fragment après fragment et sans revenir en arrière, est un digest
    fidèle : il abrège, il n'invente pas.
    """
    b, s = squelette(bloc), squelette(src)
    i, pos, absents, courant = 0, 0, [], []
    while i < len(b):
        lo, hi, ou = 0, len(b) - i, -1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            j = s.find(b[i:i + mid], pos)
            if j != -1:
                lo, ou = mid, j
            else:
                hi = mid - 1
        if lo >= SEUIL_FRAGMENT:
            if courant:
                absents.append("".join(courant)); courant = []
            pos = ou + lo
            i += lo
        else:
            courant.append(b[i]); i += 1
    if courant:
        absents.append("".join(courant))
    if not absents:
        return 0, 0, ""
    pire = max(absents, key=len)
    return sum(len(x) for x in absents), len(pire), pire


def source(cle, n):
    """Le siman entier, consonnes seules. Mis en cache : les trois langues d'une
    même page interrogeraient sinon Sefaria trois fois."""
    if (cle, n) in _cache:
        return _cache[(cle, n)]
    ref = OUVRAGES[cle][0]
    url = f"https://www.sefaria.org/api/texts/{ref}.{n}?context=0&pad=0"
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=60).stdout
    try:
        he = json.loads(out).get("he", [])
    except Exception:
        he = []
    he = he if isinstance(he, list) else [he]
    _cache[(cle, n)] = consonnes(" ".join(he))
    return _cache[(cle, n)]


def ouvrage_declare(avant, section):
    """Ce que la page dit citer, lu dans les 400 caractères qui précèdent le bloc."""
    z = re.sub(r'<[^>]+>', ' ', avant[-400:])
    # L'ouvrage se nomme dans la langue de la page : l'hébreu écrit
    # « שולחן ערוך הרב », le français « Choul'han Aroukh HaRav », l'anglais
    # « Shulchan Aruch HaRav ». Ne chercher que la forme hébraïque faisait lire
    # les pages ANGLAISES des simanim 244 et 245 comme citant le Choul'han Aroukh
    # alors qu'elles annoncent l'Admour HaZaken — et les déclarait fautives à tort.
    if RE_HARAV.search(z):
        return "harav"
    if section == "yoreh-deah":
        return "yd"
    return "sa"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", choices=list(SECTIONS))
    ap.add_argument("--siman", nargs="*", type=int)
    ap.add_argument("--details", action="store_true")
    a = ap.parse_args()

    pages, fautes, equivalents, sans_source, digests = 0, [], [], [], []
    sections = [a.section] if a.section else list(SECTIONS)
    for sec in sections:
        for d in sorted((RACINE / SECTIONS[sec]).glob("siman-*"),
                        key=lambda p: int(p.name.split("-")[1])):
            n = int(d.name.split("-")[1])
            if a.siman and n not in a.siman:
                continue
            for suf in ("", "-he", "-en"):
                p = d / f"index{suf}.html"
                if not p.exists():
                    continue
                t = p.read_text(encoding="utf-8")
                m = RE_BLOC.search(t)
                if not m:
                    continue
                pages += 1
                cle = ouvrage_declare(t[:m.start()], sec)
                src = source(cle, n)
                bloc = consonnes(m.group(1))
                if not bloc:
                    continue
                if not src:
                    sans_source.append((sec, n, suf, cle)); continue
                if bloc in src:
                    continue
                if squelette(bloc) in squelette(src):
                    equivalents.append((sec, n, suf, cle)); continue
                total, pire, exemple = fragments_absents(bloc, src)
                if pire < SEUIL_ETRANGER:
                    digests.append((sec, n, suf, total)); continue
                fautes.append((sec, n, suf, cle, pire, exemple))
                if a.details:
                    print(f"  ❌ {sec} {n}{suf} (dit citer {OUVRAGES[cle][1]})")
                    print(f"       {pire} caractères d'affilée absents de la source :")
                    print(f"       …{exemple[:70]}")

    print(f"\n{pages} page(s) d'index portant un bloc hébreu")
    print(f"→ {len(fautes)} portant du texte ABSENT de l'ouvrage qu'elles nomment "
          f"(plus de {SEUIL_ETRANGER} caractères d'affilée)")
    if fautes:
        print("   " + " ".join(sorted({f"{x[1]}" for x in fautes}, key=int)))
    print(f"→ {len(equivalents)} conformes aux matres lectionis près")
    print(f"→ {len(digests)} digests fidèles : ils abrègent la source, ils n'inventent rien")
    if sans_source:
        print(f"→ {len(sans_source)} dont l'ouvrage nommé ne donne rien pour ce siman "
              f"(à regarder : {sorted({x[1] for x in sans_source})[:12]})")
    return 1 if fautes else 0


if __name__ == "__main__":
    sys.exit(main())
