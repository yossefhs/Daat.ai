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
reproduit le séif visé : au titre suivant de rang égal ou supérieur à celui
qui introduit le bloc.

Le rang compte. Il fut d'abord fixé à ``<h3>`` pour toutes les pages ; mais
beaucoup ouvrent une seule section « Le texte du Choul'han Aroukh » en ``<h3>``
et titrent chaque séif en ``<h4>`` dessous. Le ``<h3>`` suivant valait alors
pour tous les séifim, et les encadrés — justes, dans le bon ordre — s'empilaient
tous à la fin de la section au lieu de suivre chacun son séif. Vingt-deux
simanim ont été publiés ainsi avant que ce soit vu.

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
# Valeur d'une lettre-numéro de séif. La table s'arrêtait à כ = 20 : le siman 303
# en compte vingt-sept, et les séifim כ״א à כ״ז faisaient echouer le lot entier
# avec « séif hors du siman » — alors qu'ils existent bel et bien. Calculée
# désormais, jusqu'à quarante, plutôt qu'énumérée.
_UNITES = {c: i + 1 for i, c in enumerate("אבגדהוזחט")}
_DIZAINES = {"י": 10, "כ": 20, "ל": 30, "מ": 40}


def _val(lettres):
    """« כ״ז » → 27. Les lettres sont écrites sans geresh dans les clés du lot."""
    s = lettres.replace("״", "").replace('"', "").replace("׳", "").replace("'", "")
    if s in ("טו", "טז"):                      # convention : 15 et 16
        return 9 + _UNITES[s[1]]
    n = 0
    for c in s:
        if c in _DIZAINES:
            n += _DIZAINES[c]
        elif c in _UNITES:
            n += _UNITES[c]
        else:
            return None
    return n or None


class _Val(dict):
    def get(self, k, defaut=None):
        v = _val(k)
        return v if v is not None else defaut


VAL = _Val()
RE_TS = re.compile(r'<blockquote class="text-source"[^>]*>(.*?)</blockquote>', re.S)
RE_TITRE = re.compile(r'<h(?P<rang>[1-6])[^>]*>')
SEUIL = 0.55


def fin_de_section(html, apres, depuis):
    """Où se referme la section du bloc source qui commence à ``depuis``.

    Le terminateur n'est pas toujours le ``<h3>`` suivant. Beaucoup de pages
    ouvrent une seule section « Le texte du Choul'han Aroukh » en ``<h3>`` et
    titrent chaque séif en ``<h4>`` dessous : le ``<h3>`` suivant est alors le
    même pour les dix-neuf séifim, et les dix-neuf encadrés s'empilent à la fin
    de la section au lieu de suivre chacun son séif — c'est ce qui est arrivé à
    vingt-deux simanim publiés. On lit donc le rang du titre qui introduit le
    bloc, et la section se referme au titre suivant de rang égal ou supérieur.
    """
    rang = 3
    for m in RE_TITRE.finditer(html, 0, depuis):
        rang = int(m.group("rang"))
    fin = re.compile(r'\n<h[1-%d][^>]*>' % rang)
    suivant = fin.search(html, apres)
    return suivant


def encadre(etiquette, puces):
    lis = "\n".join(f"  <li>{p}</li>" for p in puces)
    return (f'<div class="key-point">\n<strong>{etiquette}</strong>\n'
            f'<ul class="compact">\n{lis}\n</ul>\n</div>\n\n')


def mots_utiles(texte):
    """Les mots d'un texte, réduits à leur squelette, tels que l'ancrage les lit.

    Un même texte doit donner la même liste des deux côtés de la comparaison —
    dans le bloc de la page comme dans le séif de Sefaria. La liste était
    construite avec ce filtre pour le bloc et sans lui pour le séif : le séif יב
    du siman 320, « יש ליזהר שלא ישפשף ידיו במלח », gardait un ד que le bloc
    avait laissé tomber, et le lot entier était refusé pour ce seul mot.
    """
    mots = [va.squelette(w) for w in re.findall(r"[א-ת]{3,}", va.lettres_mots(texte))]
    return [w for w in mots if len(w) >= 2]


def ancrage(html, sq, n, courts=None):
    """Fin de la section du PREMIER bloc qui reproduit le séif n, et son score.

    Le premier, car plusieurs pages reprennent le texte du séif dans une
    section d'analyse plus bas ; c'est la section de tête qui porte le texte,
    la traduction et l'explication, et donc celle que l'encadré doit refermer.
    """
    for m in RE_TS.finditer(html):
        txt = re.sub(r"\s+", " ", va.RE_TAG.sub(" ", m.group(1))).strip()
        tem = mots_utiles(txt)[:14]
        if len(tem) < 6:
            # Bloc trop court pour le test de recouvrement — mais un séif peut
            # l'être aussi : « סומא אינו מברך » (רצ״ח:יג) ne fait que trois mots,
            # et le lot entier était refusé pour lui. Sur un bloc si court, le
            # recouvrement n'apporte rien de plus qu'une inclusion exacte, et
            # l'inclusion est plus sûre : on exige que le squelette du bloc soit
            # contenu dans CE séif et dans aucun autre. Sans unicité, on s'abstient.
            court = " ".join(tem)
            if not court or courts is None:
                continue
            dedans = [j + 1 for j, s in enumerate(courts) if court in s]
            if dedans != [n]:
                continue
            suivant = fin_de_section(html, m.end(), m.start())
            if not suivant:
                return None, 1.0
            return suivant.start() + 1, 1.0
        sc = [(sum(1 for w in tem if w in s) / len(tem), j + 1) for j, s in enumerate(sq)]
        best, place = max(sc)
        if place != n or best < SEUIL:
            continue
        suivant = fin_de_section(html, m.end(), m.start())
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
    courts = [" ".join(mots_utiles(s)) for s in src]
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
            at, score = ancrage(t, sq, num, courts)
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
