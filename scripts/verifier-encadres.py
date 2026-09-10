#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garde-fou des encadrés « Ce que dit ce séif » — la citation est-elle dans SON séif ?

`verifier-citations.py` juge une citation sur la référence qu'elle porte. Les
encadrés n'en portent pas : leur référence est leur PLACE — le séif sous lequel
ils sont posés. Le garde-fou les classait donc « sans référence » et ne les
regardait pas. Ils étaient 261 dans les seuls simanim 351-360, et dix-huit
d'entre eux étaient fautifs : à l'intérieur des guillemets, les abréviations du
Choul'han Aroukh avaient été développées — `מרה״י` écrit « מרשות היחיד »,
`אפי׳` écrit « אפילו », `אא״כ` écrit « אלא אם כן ». Les guillemets sont réservés
au verbatim ; développer une abréviation à l'intérieur, c'est déjà réécrire.

Deux marqueurs de verbatim sont lus, comme ailleurs dans le dépôt : les
guillemets, et le ``<span class="he-q">``. N'en lire qu'un revient à ne pas
contrôler l'autre — les vingt-sept séifim du lot 361-365 sont écrits en he-q.

Le contrôle est simple et n'admet aucune interprétation : le squelette des mots
de la citation doit se retrouver, dans l'ordre et d'un seul tenant, dans le
séif que l'encadré referme. Le nikoud, la ponctuation et le ktiv haser/male
sont libres — c'est ce que `squelette()` efface déjà pour l'alignement. Une
ellipse « … » sépare des segments jugés chacun pour soi.

Le plancher de bruit, mesuré en septembre 2026, est de CINQ cas — quinze
signalements, trois langues chacun — et tous les cinq ont été lus et gardés :

  272:1  אלא אם כן נמר ריחו וטעמו   — Choul'han Aroukh HaRav רע״ב:א, que
                                      l'encadré nomme lui-même.
  272:2  מצוה מן המובחר ביין ישן    — SA HaRav רע״ב:ב et Michna Beroura ס״ק ה,
                                      attribution ajoutée en septembre 2026.
  278:1  חולה שיש בו סכנה           — un terme que la page nomme, pas une
                                      citation du séif.
  279:6  מוקצה מחמת מיאוס מותר      — de même : un principe énoncé, non cité.
  320:6  ובמקום שנהגו לסחוט…        — la glose du Rama au séif א, que l'encadré
                                      désigne explicitement comme telle.

Ce que le contrôle ne voit pas, et qu'il faut savoir : une citation attribuée
explicitement à un AUTRE ouvrage (« Choul'han Aroukh HaRav רע״ב:ב », « la glose
du Rama au séif א ») n'est pas dans le séif et sort donc en signalement. Ce sont
des faux positifs légitimes, à lire un par un — c'est ainsi qu'a été trouvée, au
siman 272, une phrase de la Michna Beroura reprise nue à la suite des mots du
Mehaber.

    python3 scripts/verifier-encadres.py [--section shabbat] [--siman N …]
"""
import argparse, importlib.util, pathlib, re, sys

SITE = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("va", SITE / "scripts/verifier-alignement.py")
va = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(va)

TETES = {"": "Ce que dit ce séif :", "-he": "מה אומר הסעיף:", "-en": "What this seif says:"}
SECTIONS = {"shabbat": "Shulchan Arukh, Orach Chayim",
            "orah-haim": "Shulchan Arukh, Orach Chayim",
            "yoreh-deah": "Shulchan Arukh, Yoreh De'ah"}
RE_TAG = re.compile(r"<[^>]+>")
RE_CIT = re.compile(r'[«"“]([^«»"”“]{8,})[»"”]')
# Le dépôt a DEUX marqueurs de verbatim, et il faut lire les deux : les
# guillemets, et le <span class="he-q"> — que verifier-citations.py traite déjà
# comme du verbatim. Ne lire que les guillemets laissait passer les encadrés
# rédigés en he-q, soit 27 séifim du lot 361-365 non confrontés à leur source.
RE_HEQ = re.compile(r'<span class="he-q">(.*?)</span>', re.S)


def mots(texte):
    """Les mots hébreux du texte, réduits à leur squelette."""
    return [va.squelette(w) for w in re.findall(r"[א-ת]+", va.lettres_mots(texte))]


def dedans(segment, seif):
    """Le segment se lit-il d'un seul tenant dans le séif ?"""
    if not segment:
        return False
    n = len(segment)
    return any(seif[i:i + n] == segment for i in range(len(seif) - n + 1))


def verifier(section, numeros=None):
    base = SITE / "sources" / section
    ouvrage = SECTIONS[section]
    total = fautes = pages = 0
    for d in sorted(base.glob("siman-*")):
        n = int(d.name.split("-")[1])
        if numeros and n not in numeros:
            continue
        if not (d / "niveau-1-base.html").exists():
            continue
        if TETES[""] not in (d / "niveau-1-base.html").read_text(encoding="utf-8"):
            continue
        seifim = [mots(s) for s in va.seifim(ouvrage, n)]
        for suf, tete in TETES.items():
            p = d / f"niveau-1-base{suf}.html"
            if not p.exists():
                continue
            pages += 1
            enc = re.compile(r'<div class="key-point">\s*<strong>'
                             + re.escape(tete) + r"</strong>(.*?)</div>", re.S)
            for i, m in enumerate(enc.finditer(p.read_text(encoding="utf-8"))):
                if i >= len(seifim):
                    print(f"{p} : encadré {i + 1} au-delà des {len(seifim)} séifim")
                    fautes += 1
                    continue
                brut = m.group(1)
                # Un he-q court n'est pas une citation mais un TERME que la page
                # nomme — « לחם משנה », « גרף של רעי », « מוקצה מחמת מיאוס ». Le
                # confronter au séif n'a pas de sens : il vient du vocabulaire de
                # la sougya, pas de la phrase du Mehaber. Quatre mots et plus,
                # c'est une phrase, et elle doit être dans son séif. Les
                # guillemets, eux, sont jugés dès huit caractères : ils
                # n'annoncent jamais autre chose qu'un verbatim.
                heq = [c for c in RE_HEQ.findall(brut) if len(mots(RE_TAG.sub(" ", c))) >= 4]
                citations = heq + RE_CIT.findall(RE_TAG.sub(" ", brut))
                for cit in (RE_TAG.sub(" ", c) for c in citations):
                    if not re.search(r"[א-ת]", cit):
                        continue
                    total += 1
                    segs = [mots(x) for x in re.split(r"…|\.\.\.", cit)
                            if re.search(r"[א-ת]", x)]
                    if not all(dedans(s, seifim[i]) for s in segs):
                        fautes += 1
                        print(f"{p}\n  séif {i + 1} ← {cit.strip()[:120]}")
    print(f"\n{total} citation(s) hébraïque(s) d'encadré dans {pages} page(s)")
    print(f"→ {fautes} hors du séif qu'elles referment")
    return 1 if fautes else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--section", default="shabbat", choices=sorted(SECTIONS))
    ap.add_argument("--siman", type=int, nargs="*")
    a = ap.parse_args()
    sys.exit(verifier(a.section, set(a.siman) if a.siman else None))
