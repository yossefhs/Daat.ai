#!/usr/bin/env python3
"""
DAAT — Audit des simanim de Hilkhot Shabbat et suivants (sources/shabbat), et de Yoreh De'ah.

Vérifie, pour chaque siman (sources/shabbat : la base publiée 242-365, plus tout siman-N présent
sur le disque — Orah Haïm 366 et suivants y vivront, sous /oh/N), l'état réel des niveaux 1-4 :
  - présence des fichiers ;
  - boilerplate non réécrit (texte générique laissé par generate-niveaux-123.py) ;
  - désynchronisation de la table des matières du Niveau 2
    (l'index-box doit refléter les en-têtes de sections réels).

Sortie : un rapport lisible + un code de sortie non nul si au moins
une ERREUR est détectée — utilisable en hook SessionStart ou en pre-commit
pour empêcher de « marquer complété » un siman encore générique.

Usage :
    python3 scripts/audit-simanim.py                # rapport
    python3 scripts/audit-simanim.py --write-progress# régénère PROGRESS.md
    python3 scripts/audit-simanim.py --quiet         # résumé seul

Aucune dépendance externe.
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "sources", "shabbat")
# Simanim que l'Admour HaZaken n'a pas rédigés : pas de niveaux 1-4 attendus.
NO_LEVELS = {304, 322}

# ── SECTIONS AUDITÉES ────────────────────────────────────────────────────────
# L'audit ne couvrait QUE Hilkhot Shabbat : les 750 pages du Yoreh De'ah
# n'étaient contrôlées par rien. C'est ce qui a permis au niveau 2 YD de rester
# monolingue sans que rien ne le signale.
# Le niveau 4 porte un NOM DIFFÉRENT selon la section : le Choulhan Aroukh HaRav
# ne couvre pas les simanim de cacheroute, le niveau 4 y est donc la halakha
# lema'asse (niveau-4-halakha) et non « Daat HaRav ».
# La base 242-365 est ÉCRITE et n'est jamais abaissée : un siman publié qui
# disparaît du disque reste audité, et sort en « fichier absent ». Tout siman-N
# présent sur le disque s'y ajoute (Orah Haïm 366 et suivants vivent sous
# sources/shabbat) : jusqu'au 20 octobre 2026 la liste était range(242, 366), et
# un siman 366 déposé là n'aurait été audité par rien, le hook restant vert.
_DIR_SHABBAT = os.path.join(os.path.dirname(__file__), "..", "sources", "shabbat")
_BASE_SHABBAT = range(242, 366)


def _simanim_du_disque(d):
    try:
        noms = os.listdir(d)
    except FileNotFoundError:
        return set()
    return {int(m.group(1)) for m in (re.fullmatch(r"siman-([1-9][0-9]*)", e) for e in noms)
            if m and os.path.isdir(os.path.join(d, m.group(0)))}


def _hors_forme(d):
    """Les entrées siman-* qui ne sont pas un répertoire siman-N (siman-366-ancien, siman-0366, fichier) : elles ne
    sont pas auditées, et jamais passées sous silence — main() les déclare en erreur, comme verify-oh-source.py
    --tous les refuse en PAGE HORS PORTE."""
    try:
        noms = sorted(os.listdir(d))
    except FileNotFoundError:
        return []
    return [e for e in noms if e.startswith("siman-") and not (
        re.fullmatch(r"siman-([1-9][0-9]*)", e) and os.path.isdir(os.path.join(d, e)))]


_SIMANIM_SHABBAT = sorted(set(_BASE_SHABBAT) | _simanim_du_disque(_DIR_SHABBAT))
_HORS_FORME_SHABBAT = _hors_forme(_DIR_SHABBAT)
# Le libellé ne s'élargit que lorsqu'un siman au-delà de la base existe : le
# rapport (et le hook SessionStart) reste mot pour mot celui d'avant tant qu'il n'y en a pas.
_LABEL_SHABBAT = ("Hilkhot Shabbat" if _SIMANIM_SHABBAT[-1] <= _BASE_SHABBAT[-1]
                  else f"Hilkhot Shabbat et suivants ({_BASE_SHABBAT[0]}-{_SIMANIM_SHABBAT[-1]})")

SECTIONS = [
    {
        "id": "shabbat",
        "label": _LABEL_SHABBAT,
        "dir": _DIR_SHABBAT,
        "simanim": _SIMANIM_SHABBAT,
        "no_levels": {304, 322},
        "n4_file": "niveau-4-daat-harav.html",
    },
    {
        "id": "yoreh-deah",
        "label": "Yoreh De'ah",
        "dir": os.path.join(os.path.dirname(__file__), "..", "sources", "yoreh-deah"),
        # Continu du 87 au 208. La brèche entre le bloc de l'intérêt et celui
        # de נדה (183-200) a été fermée par le lot 178-182 ; le lot 201-208 a
        # ajouté le mikvé (201-202) puis l'ouverture des נדרים (203-208).
        "simanim": list(range(87, 235)),
        "no_levels": set(),
        "n4_file": "niveau-4-halakha.html",
    },
]

# Variantes de langue attendues pour CHAQUE page (règle de parité trilingue).
LANG_SUFFIXES = {"HE": "-he", "EN": "-en"}

# Marqueurs NON ambigus de contenu générique laissé par le générateur.
BP_N1 = "Traduction structurelle"
BP_N2 = "מבית מדרשו של ר' יצחק הצרפתי"          # carte Rashi générique
BP_N3 = "Action clairement permise selon le Mehaber"  # schéma générique récent
# Section de synthèse générique (gabarit ancien, mnémonique parfois personnalisé).
SOFT_N3 = "Différence Mehaber vs Rama"

LEVELS = {
    "N1": "niveau-1-base.html",
    "N2": "niveau-2-lamdan.html",
    "N3": "niveau-3-synthese.html",
    "N4": "niveau-4-daat-harav.html",
}


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


# Entrée de TOC générique laissée par le générateur (Niveau 2).
# Si elle figure dans l'index-box d'un siman dont le corps est réécrit,
# c'est que la table des matières n'a pas été régénérée.
GENERIC_TOC = "המקור והברייתא הבסיסית"


def toc_desynced(n2_html):
    """Vrai si la table des matières du N2 est restée générique."""
    m = re.search(
        r'<div class="index-box" dir="rtl">\s*<ol>(.*?)</ol>',
        n2_html, re.S,
    )
    if not m:
        return False
    toc = m.group(1)
    if GENERIC_TOC not in toc:
        return False
    # La TOC est légitime si la section 1 réelle porte bien ce titre.
    sec1 = re.search(
        r'<h2 class="section-title">1\.\s*(.*?)</h2>', n2_html
    )
    return not (sec1 and GENERIC_TOC in sec1.group(1))


def audit_siman(n, section=None):
    """Renvoie un dict {niveau: statut} + liste d'erreurs/avertissements."""
    section = section or SECTIONS[0]
    d = os.path.join(section["dir"], f"siman-{n}")
    res = {"siman": n, "section": section["id"], "errors": [], "warnings": [], "levels": {}}

    levels = dict(LEVELS)
    levels["N4"] = section["n4_file"]

    # Simanim non rédigés par l'Admour HaZaken (304, 322) : les niveaux 1-3
    # existent bel et bien et DOIVENT être audités — seul le niveau 4 est une
    # page-passerelle. L'ancien court-circuit les sortait entièrement de l'audit :
    # il annonçait « 124/124 conformes » en n'en contrôlant réellement que 122,
    # et les 24 pages de ces deux simanim (4 niveaux × 3 langues) passaient sous
    # le radar.
    is_bridge = n in section["no_levels"]
    if is_bridge:
        res["note"] = "niveau 4 : page-passerelle (siman non rédigé par l'Admour HaZaken)"

    # Parité trilingue : chaque page doit exister en -he ET en -en.
    for lvl, fname in list(levels.items()) + [("IDX", "index.html")]:
        if not os.path.exists(os.path.join(d, fname)):
            continue  # l'absence du FR est déjà signalée plus bas
        for lang, suffix in LANG_SUFFIXES.items():
            variant = fname.replace(".html", f"{suffix}.html")
            if not os.path.exists(os.path.join(d, variant)):
                res["errors"].append(f"{lvl} : variante {lang} absente ({variant})")

    for lvl, fname in levels.items():
        html = read(os.path.join(d, fname))
        if html is None:
            res["levels"][lvl] = "ABSENT"
            res["errors"].append(f"{lvl} : fichier absent")
            continue
        if is_bridge and lvl == "N4":
            # La page doit se déclarer explicitement comme passerelle.
            if "passerelle" in html or "n'a pas rédigé" in html:
                res["levels"][lvl] = "bridge"
            else:
                res["levels"][lvl] = "ABSENT"
                res["errors"].append("N4 : page-passerelle attendue mais non déclarée")
            continue
        if lvl == "N1" and BP_N1 in html:
            res["levels"][lvl] = "boilerplate"
            res["errors"].append("N1 : traduction générique non réécrite")
        elif lvl == "N2" and BP_N2 in html:
            res["levels"][lvl] = "boilerplate"
            res["errors"].append("N2 : pilpoul générique non réécrit")
        elif lvl == "N3" and BP_N3 in html:
            res["levels"][lvl] = "boilerplate"
            res["errors"].append("N3 : synthèse générique non réécrite")
        elif lvl == "N3" and SOFT_N3 in html:
            res["levels"][lvl] = "structure-générique"
            res["warnings"].append(
                "N3 : structure générique (à personnaliser)"
            )
        else:
            res["levels"][lvl] = "ok"

        # Désynchronisation de la TOC du Niveau 2.
        if lvl == "N2" and res["levels"]["N2"] == "ok" and toc_desynced(html):
            res["levels"]["N2"] = "toc-désync"
            res["errors"].append("N2 : table des matières désynchronisée")
    return res


def main():
    args = set(sys.argv[1:])
    quiet = "--quiet" in args
    only = next((a.split("=", 1)[1] for a in args if a.startswith("--section=")), None)
    rows = []
    for sec in SECTIONS:
        if only and sec["id"] != only:
            continue
        rows += [audit_siman(n, sec) for n in sec["simanim"]]

    n_err = sum(1 for r in rows if r["errors"])
    n_warn = sum(1 for r in rows if r["warnings"] and not r["errors"])

    if not quiet:
        for r in rows:
            if r["errors"] or r["warnings"]:
                tag = "ERREUR " if r["errors"] else "avert. "
                for msg in r["errors"] + r["warnings"]:
                    print(f"  [{tag}] {r.get('section','shabbat'):<10} siman {r['siman']:>3} — {msg}")

    print()
    for sec in SECTIONS:
        sub = [r for r in rows if r.get("section") == sec["id"]]
        if sub:
            e = sum(1 for r in sub if r["errors"])
            print(f"{sec['label']:<20}: {len(sub) - e}/{len(sub)} conformes")
    print(f"Simanim audités     : {len(rows)}")
    print(f"Avec erreur(s)      : {n_err}")
    print(f"Avec avertissement  : {n_warn}")
    print(f"Conformes           : {len(rows) - n_err - n_warn}")
    hors_forme = _HORS_FORME_SHABBAT if (not only or only == "shabbat") else []
    for e in hors_forme:
        print(f"  [ERREUR ] shabbat    {e} — entrée qui n'est pas un répertoire siman-N : NON AUDITÉE")

    if "--write-progress" in args:
        write_progress([r for r in rows if r.get("section") == "shabbat"])
        print("\nPROGRESS.md régénéré.")

    return 1 if n_err or hors_forme else 0


def write_progress(rows):
    """Génère PROGRESS.md à la racine du dépôt."""
    out = os.path.join(os.path.dirname(__file__), "..", "PROGRESS.md")
    sym = {
        "ok": "✅", "bespoke": "✅", "boilerplate": "🔴",
        "toc-désync": "🟠", "structure-générique": "🟡",
        "ABSENT": "❌", "n/a": "—", "bridge": "🌉",
    }
    lines = [
        f"# Progression — {_LABEL_SHABBAT} (niveaux 1-4)",
        "",
        "Généré par `scripts/audit-simanim.py --write-progress`. Ne pas éditer à la main.",
        "",
        "✅ réécrit · 🟡 structure générique (à personnaliser) · "
        "🟠 TOC désynchronisée · 🔴 boilerplate · ❌ absent · — non concerné · "
        "🌉 page-passerelle (siman non rédigé par l'Admour HaZaken, traité par analogie)",
        "",
        "| Siman | N1 | N2 | N3 | N4 |",
        "|-------|----|----|----|----|",
    ]
    for r in rows:
        lv = r["levels"]
        cells = " | ".join(sym.get(lv.get(k, "?"), "?") for k in
                            ("N1", "N2", "N3", "N4"))
        lines.append(f"| {r['siman']} | {cells} |")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
