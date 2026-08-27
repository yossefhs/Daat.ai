#!/usr/bin/env python3
"""Corrige le learningResourceType des niveaux 4 de Yoré Déa.

Les pages `niveau-4-halakha*` de Yoré Déa déclaraient dans leur JSON-LD :
    "Shitah of the Admour HaZaken (Shulchan Aruch HaRav)"   (50 fichiers -en)
    "שיטת אדמו״ר הזקן (שולחן ערוך הרב)"                        (45 fichiers -he)
    "… (niveau 4 — Daat HaRav et Halakha lema'asse)"        (18 fichiers FR)

C'est faux : l'Admour HaZaken n'a jamais écrit de Choul'han Aroukh sur Yoré Déa.
Ces pages présentent une psika pratique appuyée sur le Chakh, le Taz et les poskim.
Le JSON-LD n'est lu par personne à l'écran — il est lu par Google et par les aperçus
de partage, qui annonçaient donc un contenu que la page elle-même dément dans son
propre avertissement. Aucun garde-fou ne regardait ce champ.

Idempotent. Usage : python3 scripts/fix-yd-jsonld-niveau4.py [--dry-run]
"""
import re, glob, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIBLE = {
    "":    "Cours d'étude halakhique (niveau 4 — Halakha lema'asse)",
    "-he": "שיעור הלכה (רמה 4 — הלכה למעשה)",
    "-en": "Halakhic study course (level 4 — Halakha lema'asse)",
}
CHAMP = re.compile(r'("learningResourceType"\s*:\s*")([^"]*)(")')

def main(dry=False):
    total = 0
    for suf, bon in CIBLE.items():
        for p in sorted(glob.glob(os.path.join(ROOT, f"sources/yoreh-deah/siman-*/niveau-4-halakha{suf}.html"))):
            html = open(p, encoding="utf-8").read()
            new, n = CHAMP.subn(lambda m: m.group(1) + bon + m.group(3), html)
            if n and new != html:
                total += 1
                if not dry:
                    open(p, "w", encoding="utf-8").write(new)
                print(f"  {os.path.relpath(p, ROOT)}")
    print(f"{'(à blanc) ' if dry else ''}{total} fichier(s) corrigé(s)")

if __name__ == "__main__":
    main("--dry-run" in sys.argv)
