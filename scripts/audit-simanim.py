#!/usr/bin/env python3
"""
DAAT — Audit des simanim de Hilkhot Shabbat.

Vérifie, pour chaque siman (242-365), l'état réel des niveaux 1-4 :
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
FIRST, LAST = 242, 365
# Simanim que l'Admour HaZaken n'a pas rédigés : pas de niveaux 1-4 attendus.
NO_LEVELS = {304, 322}

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


def audit_siman(n):
    """Renvoie un dict {niveau: statut} + liste d'erreurs/avertissements."""
    d = os.path.join(ROOT, f"siman-{n}")
    res = {"siman": n, "errors": [], "warnings": [], "levels": {}}

    if n in NO_LEVELS:
        res["levels"] = {k: "n/a" for k in LEVELS}
        res["note"] = "non rédigé par l'Admour HaZaken"
        return res

    for lvl, fname in LEVELS.items():
        html = read(os.path.join(d, fname))
        if html is None:
            res["levels"][lvl] = "ABSENT"
            res["errors"].append(f"{lvl} : fichier absent")
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
    rows = [audit_siman(n) for n in range(FIRST, LAST + 1)]

    n_err = sum(1 for r in rows if r["errors"])
    n_warn = sum(1 for r in rows if r["warnings"] and not r["errors"])

    if not quiet:
        for r in rows:
            if r["errors"] or r["warnings"]:
                tag = "ERREUR " if r["errors"] else "avert. "
                for msg in r["errors"] + r["warnings"]:
                    print(f"  [{tag}] siman {r['siman']:>3} — {msg}")

    print()
    print(f"Simanim audités     : {len(rows)}")
    print(f"Avec erreur(s)      : {n_err}")
    print(f"Avec avertissement  : {n_warn}")
    print(f"Conformes           : {len(rows) - n_err - n_warn}")

    if "--write-progress" in args:
        write_progress(rows)
        print("\nPROGRESS.md régénéré.")

    return 1 if n_err else 0


def write_progress(rows):
    """Génère PROGRESS.md à la racine du dépôt."""
    out = os.path.join(os.path.dirname(__file__), "..", "PROGRESS.md")
    sym = {
        "ok": "✅", "bespoke": "✅", "boilerplate": "🔴",
        "toc-désync": "🟠", "structure-générique": "🟡",
        "ABSENT": "❌", "n/a": "—",
    }
    lines = [
        "# Progression — Hilkhot Shabbat (niveaux 1-4)",
        "",
        "Généré par `scripts/audit-simanim.py --write-progress`. Ne pas éditer à la main.",
        "",
        "✅ réécrit · 🟡 structure générique (à personnaliser) · "
        "🟠 TOC désynchronisée · 🔴 boilerplate · ❌ absent · — non concerné",
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
