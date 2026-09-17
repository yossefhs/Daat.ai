#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le résumé d'un séif dit-il PERMIS là où la source dit INTERDIT ?

Le bloc d'index d'Orah Haïm résume le siman séif par séif, chacun étiqueté
« (סעיף N) », et le fait dans les mots de la page. Aucune comparaison de texte ne
peut donc en juger : c'est ce qui a laissé passer, des mois durant, le siman 246,
dont le résumé disait « אסור להשכיר… ואסור אפילו להשאיל » là où le Mehaber écrit
« מותר להשאיל ולהשכיר » — une interdiction publiée à la place d'une permission.

Ce contrôle ne compare pas les mots mais la POLARITÉ. Pour chaque séif, il relève
de part et d'autre ce que la halakha y met de tranchant — אסור, מותר, חייב, פטור,
כשר, פסול, אין, יש — et signale les séifim où le résumé penche d'un côté que la
source ne connaît pas du tout.

Il produit des CANDIDATS, jamais des verdicts : un séif peut dire « מותר » dans
une clause et « אסור » dans une autre, et un résumé fidèle peut n'en garder
qu'une. Ce qu'il donne, c'est une liste courte à lire — au lieu de 54 simanim.
"""
import argparse, json, re, subprocess, sys, unicodedata, pathlib

RACINE = pathlib.Path(__file__).resolve().parent.parent
RE_BLOC = re.compile(r'<div class="seif-text-he">(.*?)</div>', re.S)
RE_SEIF = re.compile(r'\(\s*(?:סעיף|סעיפים)\s*([^)]{1,12})\)')
LETTRES = {c: i + 1 for i, c in enumerate("אבגדהוזחט")}
DIZ = {"י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60, "ע": 70, "פ": 80, "צ": 90}
# TROIS AXES, et non un seul. La première version les confondait — elle rangeait
# « חייב » avec « אסור » et « פטור » avec « מותר » — et signalait donc le siman 9,
# qui ne parle que de ce qui est OBLIGÉ en tsitsit et jamais de ce qui est permis.
# Obligation, permission et validité sont trois questions séparées ; comparer un
# pôle de l'une au pôle d'une autre ne veut rien dire.
AXES = {
    "permission": {"interdit": ("אסור", "אסורים", "אסורה", "אסורות"),
                   "permis":   ("מותר", "מותרים", "מותרת", "מותרות", "שרי")},
    "obligation": {"obligé":   ("חייב", "חייבים", "חייבת", "חיבים", "צריך"),
                   "exempt":   ("פטור", "פטורים", "פטורה", "אינו חייב", "אין חייב",
                                "א״צ", "אינו צריך")},
    "validité":   {"invalide": ("פסול", "פסולים", "פסולה"),
                   "valide":   ("כשר", "כשרים", "כשרה")},
}


def sansnik(s):
    return "".join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def plat(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', sansnik(s))).strip()


def val(lettres):
    s = re.sub(r'[^א-ת]', '', lettres)
    if s in ("טו", "טז"): return 9 + LETTRES[s[1]]
    n = 0
    for c in s:
        if c in DIZ: n += DIZ[c]
        elif c in LETTRES: n += LETTRES[c]
        else: return None
    return n or None


def _sq(s): return re.sub(r'[יו]', '', s)


def premier_pole(txt, axe):
    """Le pôle par lequel le texte OUVRE sur CET axe, s'il l'aborde.

    La comparaison se fait sur les SQUELETTES. Les blocs d'index sont vocalisés et
    écrits en ktiv haser — « מתר » sans vav — que la table, écrite en ktiv malé,
    ne reconnaissait pas : le siman 14, qui ouvre par « מתר לטל טלית חברו », était
    donc lu comme ouvrant par le « אסור » qui vient plus loin, et signalé à tort.
    """
    z = _sq(txt)
    trouve = []
    for k, mots in AXES[axe].items():
        for m in mots:
            i = z.find(_sq(m))
            if i != -1: trouve.append((i, k))
    return min(trouve)[1] if trouve else None


def _inutilise(txt):
    """Le pôle par lequel le texte OUVRE, et la position où il le fait.

    C'est là qu'est le défaut, et non dans l'ajout d'un pôle. Le résumé fautif du
    siman 246 ne disait rien que le séif ne dise : il disait « אסור להשכיר » en
    tête là où le Mehaber ouvre par « מותר להשאיל ולהשכיר », et reléguait la
    permission à une subordonnée. Une première règle, qui cherchait un pôle absent
    de la source, ne voyait donc PAS le cas connu — c'est en la rejouant sur lui
    qu'on s'en est aperçu.
    """
    trouve = []
    for k, mots in POLES.items():
        for m in mots:
            i = txt.find(m)
            if i != -1: trouve.append((i, k))
    return min(trouve)[1] if trouve else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--siman", nargs="*", type=int)
    a = ap.parse_args()
    nums = a.siman or [int(d.name.split("-")[1])
                       for d in sorted((RACINE / "sources/orah-haim").glob("siman-*"),
                                       key=lambda p: int(p.name.split("-")[1]))]
    examines, candidats = 0, []
    for n in nums:
        p = RACINE / f"sources/orah-haim/siman-{n}/index.html"
        if not p.exists(): continue
        t = p.read_text(encoding="utf-8")
        m = RE_BLOC.search(t)
        if not m: continue
        bloc = plat(m.group(1))
        etiq = list(RE_SEIF.finditer(bloc))
        if not etiq: continue
        u = f"https://www.sefaria.org/api/texts/Shulchan_Arukh,_Orach_Chayim.{n}?context=0&pad=0"
        o = subprocess.run(["curl", "-s", u], capture_output=True, text=True, timeout=60).stdout
        try: sef = json.loads(o).get("he", [])
        except Exception: continue
        if not isinstance(sef, list) or not sef: continue
        debut = 0
        for e in etiq:
            k = val(e.group(1))
            resume = bloc[debut:e.start()].strip()
            debut = e.end()
            if k is None or k > len(sef) or len(resume) < 12: continue
            examines += 1
            src_txt = plat(sef[k - 1])
            for axe in AXES:
                pr, ps = premier_pole(resume, axe), premier_pole(src_txt, axe)
                if pr and ps and pr != ps:
                    candidats.append((n, k, [f"{axe} : le résumé ouvre par {pr}, la source par {ps}"],
                                      resume[:78]))
    print(f"\n{examines} résumé(s) de séif confronté(s) à la polarité de leur source")
    print(f"→ {len(candidats)} candidat(s) : le résumé OUVRE par un pôle, la source par l'autre")
    for n, k, pol, ex in candidats:
        print(f"   siman {n:3d} séif {k:2d} · {pol[0]} · {ex}")
    print("\n   Candidats, non verdicts : à lire un par un.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
