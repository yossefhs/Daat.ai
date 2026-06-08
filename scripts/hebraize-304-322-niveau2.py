#!/usr/bin/env python3
"""Hébraïse les résidus visibles (chrome + intro) du niveau-2 des simanim 304 et 322.

Ces 2 simanim-passerelles (sans niveau 4) n'avaient pas été hébraïsés comme les
122 autres : sous-titre, h2, phrase d'introduction, renvoi niveau 3, note
« pas de niveau 4 », filigrane, bouton soutien et FAB khavroutha étaient restés
en français/anglais. Le corps pilpoul lui-même est déjà en hébreu.

Idempotent. Cible les 3 variantes (FR/HE/EN).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COMMON = [
    ("הלכות שבת — Études approfondies", "הלכות שבת — עיון מעמיק"),
    ("הלכות שבת — In-depth studies", "הלכות שבת — עיון מעמיק"),
    (">Pilpoul approfondi<", ">פלפול מעמיק<"),
    (">In-depth pilpul<", ">פלפול מעמיק<"),
    ("Sources talmudiques,", "מקורות התלמוד,"),
    ("<strong>Niveau 3 — Synthèse :</strong>", "<strong>רמה 3 — סיכום:</strong>"),
    ("<strong>Level 3 — Synthèse :</strong>", "<strong>רמה 3 — סיכום:</strong>"),
    ("récapitulation structurée avec axiome central, arbres de décision, mnémoniques et règles d'or.",
     "ריכוז מובנה עם עיקרון מרכזי, עצי החלטה, סימני זיכרון וכללי אצבע."),
    ("Ce siman n'a pas de Niveau 4 (Daat HaRav) : l'Admour HaZaken ne l'a pas rédigé dans le Choulhan Aroukh HaRav.",
     "סימן זה אינו כולל רמה 4 (דעת הרב): אדמו״ר הזקן לא כתבו בשולחן ערוך הרב."),
    ("Ce siman n'a pas de Level 4 (Daat HaRav) : l'Admour HaZaken ne l'a pas rédigé dans le Choulhan Aroukh HaRav.",
     "סימן זה אינו כולל רמה 4 (דעת הרב): אדמו״ר הזקן לא כתבו בשולחן ערוך הרב."),
    ("· Niveau 2 — Lamdan", "· רמה 2 — למדן"),
    ("· Level 2 — Lamdan", "· רמה 2 — למדן"),
    ("NIVEAU 2 — LAMDAN", "רמה 2 — למדן"),
    ("LEVEL 2 — LAMDAN", "רמה 2 — למדן"),
    ("♥ Soutenir DAAT", "♥ תמיכה DAAT"),
    ("♥ Support DAAT", "♥ תמיכה DAAT"),
    ('title="Trouver une khavroutha pour ce siman"', 'title="מציאת חברותא לסימן זה"'),
    ('title="Find a khavroutha for this siman"', 'title="מציאת חברותא לסימן זה"'),
    (">Rejoindre la khavroutha<", ">להצטרף לחברותא<"),
    (">Join the khavroutha<", ">להצטרף לחברותא<"),
]
PER = {
    "304": [("שיטות הראשונים בעניין le repos du serviteur et de l'esclave le chabbat",
             "שיטות הראשונים בעניין שביתת העבד והאמה בשבת")],
    "322": [("שיטות הראשונים בעניין l'œuf pondu le chabbat (nolad)",
             "שיטות הראשונים בעניין ביצה שנולדה בשבת (נולד)")],
}


def main() -> int:
    total = 0
    for n in ("304", "322"):
        for variant in ("", "-he", "-en"):
            p = ROOT / f"sources/shabbat/siman-{n}/niveau-2-lamdan{variant}.html"
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            orig = t
            for a, b in COMMON + PER[n]:
                t = t.replace(a, b)
            if t != orig:
                p.write_text(t, encoding="utf-8")
                total += 1
                print(f"  modifié : {p.relative_to(ROOT)}")
    print(f"Fichiers modifiés : {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
