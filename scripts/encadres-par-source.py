#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Encadrés « Ce que dit ce séif » — moteur ancré sur le texte source.

``enc.py`` cherche le titre du séif — « Seif ג — … » — pour savoir où poser
l'encadré. Les simanim 242-265 sont plus anciens et n'ont pas de convention
commune : les uns titrent « Seif Guimel » en <h3>, d'autres « Texte original »,
d'autres n'annoncent rien. Chercher le titre y échoue.

Mais chaque page affiche l'hébreu du séif, et cet hébreu identifie le séif sans
ambiguïté — c'est le critère du garde-fou d'alignement, appliqué ici à
l'ancrage. On confronte donc chaque bloc ``<blockquote class="text-source">``
au Choul'han Aroukh, et l'encadré se pose à la fin de la section du bloc qui
reproduit le séif visé : juste avant le ``<h3>`` suivant, ou avant le
``<h2 class="section-title">`` qui ouvre la partie suivante de la page.

C'est un ancrage plus sûr que le titre, pas seulement un ancrage de repli :
un encadré posé sous un titre mal numéroté serait faux ; posé sous le texte
qu'il résume, il ne peut pas l'être.

Rien n'est écrit si un seul ancrage manque, ou si le bloc trouvé ne correspond
pas au séif attendu : le lot entier est refusé.
"""
import importlib.util, pathlib, re, sys

SITE = pathlib.Path("/home/user/Daat.ai")
_spec = importlib.util.spec_from_file_location("va", SITE / "scripts/verifier-alignement.py")
va = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(va)

TETES = {"": "Ce que dit ce séif :", "-he": "מה אומר הסעיף:", "-en": "What this seif says:"}
IDX = {"": 0, "-he": 1, "-en": 2}
VAL = {c: i + 1 for i, c in enumerate("אבגדהוזחטי")}
VAL.update({"יא": 11, "יב": 12, "יג": 13, "יד": 14, "טו": 15, "טז": 16, "יז": 17,
            "יח": 18, "יט": 19, "כ": 20})
RE_TS = re.compile(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>', re.S)
RE_FIN = re.compile(r'\n<h3[^>]*>|\n<h2 class="section-title"')
SEUIL = 0.55


def encadre(etiquette, puces):
    lis = "\n".join(f"  <li>{p}</li>" for p in puces)
    return (f'<div class="key-point">\n<strong>{etiquette}</strong>\n'
            f'<ul class="compact">\n{lis}\n</ul>\n</div>\n\n')


def ancrage(html, sq, n):
    """Fin de la section du PREMIER bloc qui reproduit le séif n, et son score.

    Le premier, car plusieurs pages reprennent le texte du séif dans une
    section d'analyse plus bas ; c'est la section de tête qui porte le texte,
    la traduction et l'explication, et donc celle que l'encadré doit refermer.
    """
    for m in RE_TS.finditer(html):
        txt = re.sub(r"\s+", " ", va.RE_TAG.sub(" ", m.group(1))).strip()
        tem = [va.squelette(w) for w in re.findall(r"[א-ת]{3,}", va.lettres_mots(txt))][:14]
        tem = [w for w in tem if len(w) >= 2]
        if len(tem) < 6:
            # Bloc trop court pour le test de recouvrement — mais un séif peut
            # l'être aussi : « סומא אינו מברך » (רצ״ח:יג) ne fait que trois mots,
            # et le lot entier était refusé pour lui. Sur un bloc si court, le
            # recouvrement n'apporte rien de plus qu'une inclusion exacte, et
            # l'inclusion est plus sûre : on exige que le squelette du bloc soit
            # contenu dans CE séif et dans aucun autre. Sans unicité, on s'abstient.
            court = " ".join(tem)
            if not court:
                continue
            dedans = [j + 1 for j, s in enumerate(sq) if court in s]
            if dedans != [n]:
                continue
            suivant = RE_FIN.search(html, m.end())
            if not suivant:
                return None, 1.0
            return suivant.start() + 1, 1.0
        sc = [(sum(1 for w in tem if w in s) / len(tem), j + 1) for j, s in enumerate(sq)]
        best, place = max(sc)
        if place != n or best < SEUIL:
            continue
        suivant = RE_FIN.search(html, m.end())
        if not suivant:
            return None, best
        return suivant.start() + 1, best
    return None, 0.0


def appliquer(siman, T, ecrire):
    src = va.seifim("Shulchan Arukh, Orach Chayim", siman)
    if not src:
        print(f"siman {siman} : source Sefaria indisponible")
        return 1
    sq = [va.squelette(s) for s in src]
    plan, erreurs, n = {}, [], 0
    for suf in ("", "-he", "-en"):
        p = SITE / f"sources/shabbat/siman-{siman}/niveau-1-base{suf}.html"
        t = p.read_text(encoding="utf-8")
        etiquette = TETES[suf]
        if etiquette in t:
            erreurs.append(f"{p.name} : encadrés déjà présents")
            continue
        points = []
        for lettre in T:
            num = VAL.get(lettre)
            if num is None or num > len(src):
                erreurs.append(f"{p.name} {lettre} : séif hors du siman ({len(src)} séifim)")
                continue
            at, score = ancrage(t, sq, num)
            if at is None:
                erreurs.append(f"{p.name} {lettre} : aucun bloc ne reproduit le séif {num}"
                               f" (meilleur {score:.0%})")
                continue
            points.append((at, lettre, score))
        # On insère de la fin vers le début pour que les positions restent valides.
        for at, lettre, _ in sorted(points, reverse=True):
            t = t[:at] + encadre(etiquette, T[lettre][IDX[suf]]) + t[at:]
            n += 1
        plan[p] = t
    if erreurs:
        print("\n".join(erreurs))
        return 1
    print(f"siman {siman} — {len(plan)} fichier(s) · {n} encadré(s) ({len(T)} × 3).")
    if ecrire:
        for p, t in plan.items():
            p.write_text(t, encoding="utf-8")
        print("écrit.")
    return 0


def lancer(siman, T):
    raise SystemExit(appliquer(siman, T, "--write" in sys.argv))
