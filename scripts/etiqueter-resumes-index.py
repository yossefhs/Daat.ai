#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dire au lecteur, dans l'étiquette du bloc d'index, quand ce qu'il lit est un
résumé et non le texte du Choul'han Aroukh.

Le balayage du 16 septembre a établi que le bloc `seif-text-he` des pages d'index
d'Orah Haïm n'est presque jamais une citation : c'est le siman résumé séif par
séif, chacun étiqueté « (סעיף N) », et souvent réécrit dans les mots de la page —
le siman 216 donne « ולאחריו אינו מברך » là où le Mehaber écrit
« אבל לאחריו א״צ לברך ». Or l'étiquette au-dessus annonce « Le Siman — שולחן ערוך,
אורח חיים סימן רט״ז », c'est-à-dire le texte.

C'est le seul endroit du site où une erreur ne peut être vue par personne, et le
siman 246 l'a prouvé : son bloc disait l'INVERSE du Mehaber — une interdiction à
la place d'une permission — et rien ne l'a signalé pendant des mois, parce qu'un
bloc écrit dans les mots de la page ne se confronte à rien.

La convention du dépôt existe déjà pour cela : un abrégé s'introduit par
« <em>résumé</em> : » (תמצית / summary) et n'est pas jugé au verbatim. On la pose
ici, et uniquement là où elle est vraie : une page dont le bloc EST une citation
d'un seul tenant garde son étiquette telle quelle.
"""
import argparse, json, re, subprocess, sys, unicodedata, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
RE_BLOC = re.compile(r'<div class="seif-text-he">(.*?)</div>', re.S)
RE_ETIQ = re.compile(r'(<div class="seif-info-label">)(.*?)(</div>)', re.S)
MARQUE = {"": " · <em>résumé séif par séif</em>",
          "-he": " · <em>תמצית סעיף אחר סעיף</em>",
          "-en": " · <em>summary, seif by seif</em>"}
DEJA = ("résumé séif par séif", "תמצית סעיף אחר סעיף", "summary, seif by seif")
_cache = {}


def consonnes(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    return "".join(re.findall(r'[א-ת]', s))


def squelette(s): return re.sub(r'[יו]', '', s)


def source(n):
    if n in _cache: return _cache[n]
    u = f"https://www.sefaria.org/api/texts/Shulchan_Arukh,_Orach_Chayim.{n}?context=0&pad=0"
    o = subprocess.run(["curl", "-s", u], capture_output=True, text=True, timeout=60).stdout
    try: he = json.loads(o).get("he", [])
    except Exception: he = []
    _cache[n] = consonnes(" ".join(he if isinstance(he, list) else [he]))
    return _cache[n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--siman", nargs="*", type=int)
    a = ap.parse_args()
    pose, verbatim, deja, sans = 0, 0, 0, 0
    for d in sorted((RACINE / "sources/orah-haim").glob("siman-*"),
                    key=lambda p: int(p.name.split("-")[1])):
        n = int(d.name.split("-")[1])
        if a.siman and n not in a.siman: continue
        src = source(n)
        for suf in ("", "-he", "-en"):
            p = d / f"index{suf}.html"
            if not p.exists(): continue
            t = p.read_text(encoding="utf-8")
            mb = RE_BLOC.search(t)
            me = RE_ETIQ.search(t)
            if not mb or not me: sans += 1; continue
            if any(x in me.group(2) for x in DEJA): deja += 1; continue
            bloc = consonnes(mb.group(1))
            if not bloc or not src: sans += 1; continue
            # une vraie citation garde son étiquette
            if bloc in src or squelette(bloc) in squelette(src):
                verbatim += 1; continue
            t2 = t[:me.start()] + me.group(1) + me.group(2) + MARQUE[suf] + me.group(3) + t[me.end():]
            assert t2.replace(MARQUE[suf], "", 1) == t, f"{p} : autre chose a bougé"
            pose += 1
            if a.write: p.write_text(t2, encoding="utf-8")
    print(f"\n→ {pose} page(s) reçoivent l'étiquette « résumé »")
    print(f"→ {verbatim} page(s) portent une vraie citation et gardent la leur")
    if deja: print(f"→ {deja} page(s) l'avaient déjà")
    if sans: print(f"→ {sans} page(s) sans bloc ou sans source")
    print("écrit." if a.write else "essai — rien n'est écrit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
