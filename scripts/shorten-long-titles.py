#!/usr/bin/env python3
"""DAAT — Raccourcit les <title> trop longs (>70 chars).

Cible :
  - sources/shabbat/siman-*/index.html       (FR)
  - sources/shabbat/siman-*/index-en.html    (EN)
  - sources/shabbat/siman-*/index-he.html    (HE)
  - sources/shabbat/siman-*/niveau-1-base*.html
  - sources/shabbat/siman-*/niveau-2-lamdan*.html
  - sources/shabbat/siman-*/niveau-3-synthese*.html
  - sources/shabbat/siman-*/niveau-4-daat-harav*.html

Stratégie :
  1) simplifier les suffixes verbeux ;
  2) si encore > 70 chars, tronquer la description à un séparateur naturel.

Préservés : numéro de siman, sujet principal (1-3 mots), suffixe DAAT/Hilkhot Shabbat.
"""
import os, re, glob, sys

ROOT = "/home/user/Daat.ai/sources/shabbat"

title_re = re.compile(r'(<title>)(.*?)(</title>)', re.S)

def visible_len(s):
    return len(re.sub(r'<[^>]+>', '', s))

# =====================================================================
# Étape 1 : remplacements de suffixes
# =====================================================================

# Pour les index (siman-N/index.html, etc.)
INDEX_SUFFIX_RULES = [
    # FR
    (re.compile(r' · Choulhan Aroukh(?:, Orah Haïm)? · Étude en français \| DAAT$'),
     " | Hilkhot Shabbat"),
    # EN — plusieurs variantes du suffixe
    (re.compile(r' · (?:Choulhan Aroukh|Shulchan Aru[ck]h)(?:, Orach Chaim)? · '
                r'(?:Learning in English|Study in English|English [Ss]tudy|Limud in English) \| DAAT$'),
     " | Hilkhot Shabbat"),
    # HE
    (re.compile(r' · שולחן ערוך(?: אורח חיים)? · לימוד(?: בעברית)? \| (?:DAAT|דעת)$'),
     " | הלכות שבת"),
    # Anomalies repérées dans 304/322 (suffixes malformés mélangeant langues)
    (re.compile(r' · Choulhan Aroukh · Study en français \| DAAT$'),
     " | Hilkhot Shabbat"),
    (re.compile(r' · Choulhan Aroukh · לימוד en français \| DAAT$'),
     " | הלכות שבת"),
]

# Pour les pages niveau-1/2/3/4
NIVEAU_RULES = [
    # ----- Niveau 1 : retirer sous-titres verbeux -----
    (re.compile(r' · Initiation pédagogique \| DAAT$'),                " | Hilkhot Shabbat"),
    (re.compile(r' · (?:Introductory|Pedagogical|Foundational|Beginner\'s|Educational)\s+'
                r'(?:Study|Introduction|study|introduction) \| DAAT$'), " | Hilkhot Shabbat"),
    (re.compile(r' · Introduction \| DAAT$'),                          " | Hilkhot Shabbat"),
    (re.compile(r' · Introductory \| DAAT$'),                          " | Hilkhot Shabbat"),
    (re.compile(r' · התחלה לימודית \| (?:DAAT|דעת)$'),                 " | הלכות שבת"),
    # ----- Niveau 1 : préfixe "Base"/"Foundation" -> garder seulement "Niveau 1" -----
    (re.compile(r'Niveau 1 Base — '),         "Niveau 1 — "),
    (re.compile(r'Niveau 1 Foundation — '),   "Niveau 1 — "),
    (re.compile(r'Level 1 Base — '),          "Level 1 — "),
    (re.compile(r'Level 1 Foundation — '),    "Level 1 — "),
    (re.compile(r'רמה 1 Base — '),            "רמה 1 — "),
    (re.compile(r'רמה 1 בסיסית — '),          "רמה 1 — "),
    (re.compile(r'רמה 1 בסיס — '),            "רמה 1 — "),
    (re.compile(r'רמה 1 התחלה — '),           "רמה 1 — "),
    # ----- Niveau 2 : retirer "Lamdan — Pilpoul approfondi" -----
    (re.compile(r'Niveau 2 Lamdan — Pilpoul approfondi · '), "Niveau 2 — "),
    (re.compile(r'Niveau 2 Lamdan — '),                      "Niveau 2 — "),
    (re.compile(r'Level 2 Lamdan — (?:In-depth|Advanced) Pilpul · '), "Level 2 — "),
    (re.compile(r'Level 2 Lamdan — Pilpoul approfondi · '),  "Level 2 — "),
    (re.compile(r'Level 2 Lamdan — '),                       "Level 2 — "),
    (re.compile(r'רמה 2 Lamdan — Pilpoul approfondi · '),    "רמה 2 — "),
    (re.compile(r'רמה 2 Lamdan — '),                         "רמה 2 — "),
    # ----- Niveau 3 : simplifier "Synthèse Magistrale" -----
    (re.compile(r'Niveau 3 Synthèse Magistrale — Récapitulatif & '), "Niveau 3 — "),
    (re.compile(r'Niveau 3 Synthèse Magistrale — '),                 "Niveau 3 — "),
    (re.compile(r'Niveau 3 Synthèse Magistrale\b'),                  "Niveau 3 Synthèse"),
    (re.compile(r'Level 3 (?:Magisterial Synthesis|Master Synthesis|Comprehensive Synthesis) — Summary & '),
     "Level 3 — "),
    (re.compile(r'Level 3 (?:Magisterial Synthesis|Master Synthesis|Comprehensive Synthesis) — '), "Level 3 — "),
    (re.compile(r'Level 3 (?:Magisterial|Master|Comprehensive) Synthesis\b'), "Level 3 Synthesis"),
    (re.compile(r'רמה 3 סיכום (?:מאסטרלי|מגיסטרלי|מסכם|מקיף) — '),    "רמה 3 — "),
    (re.compile(r'רמה 3 סיכום (?:מאסטרלי|מגיסטרלי|מסכם|מקיף)\b'),     "רמה 3 סיכום"),
    # ----- Niveau 4 -----
    (re.compile(r'Siman \(סימן\) '), "Siman "),
    (re.compile(r'סימן \(סימן\) '),  "סימן "),
    (re.compile(r'Niveau 4 Daat HaRav — Chitah \(שיטה\) de l\'Admour HaZaken'),
     "Niveau 4 — Chitah de l'Admour HaZaken"),
    (re.compile(r'Niveau 4 Daat HaRav — Chitah de l\'Admour HaZaken'),
     "Niveau 4 — Chitah de l'Admour HaZaken"),
    (re.compile(r'Level 4 Daa[st] HaRav — Shitah \(שיטה\) of the Alter Rebbe'),
     "Level 4 — Shitah of the Alter Rebbe"),
    (re.compile(r'Level 4 Daa[st] HaRav — Shitah of the Alter Rebbe'),
     "Level 4 — Shitah of the Alter Rebbe"),
    (re.compile(r'רמה 4 דעת הרב — שיטת אדמו["״]ר הזקן'),
     "רמה 4 — שיטת אדמו״ר הזקן"),
]

# Normalisation finale du suffixe selon la langue du fichier (appliquée après tout)
SUFFIX_BY_LANG = {
    "fr": " | Hilkhot Shabbat",
    "en": " | Hilkhot Shabbat",
    "he": " | הלכות שבת",
}

def smart_truncate(desc, max_chars):
    """Tronque à un séparateur naturel.

    Préférence : séparateurs forts (—, ·, +) > virgule > ouverture de parenthèse > espace.
    """
    if len(desc) <= max_chars: return desc
    # Essai par ordre de priorité ; on prend le plus long candidat qui rentre.
    for sep in [" — ", " · ", " + "]:
        idx = desc.rfind(sep, 0, max_chars + 1)
        if idx > 15:
            return desc[:idx].rstrip().rstrip(",")
    # Virgule (souvent dans des listes : "Tolesh, Tohen, Me'abed")
    idx = desc.rfind(", ", 0, max_chars + 1)
    if idx > 15:
        return desc[:idx].rstrip().rstrip(",")
    # Parenthèse ouvrante (couper avant)
    idx = desc.rfind(" (", 0, max_chars + 1)
    if idx > 15:
        return desc[:idx].rstrip().rstrip(",")
    # Espace simple
    idx = desc.rfind(" ", 0, max_chars)
    if idx > 15:
        return desc[:idx].rstrip().rstrip(",")
    return desc[:max_chars].rstrip().rstrip(",")

def shorten(title, kind, lang):
    """Raccourcit un titre. kind ∈ {'index','niveau'}, lang ∈ {'fr','en','he'}."""
    new = title
    rules = INDEX_SUFFIX_RULES if kind == "index" else NIVEAU_RULES
    for pat, repl in rules:
        new = pat.sub(repl, new)

    # Normaliser le suffixe selon la langue du fichier
    new_suffix = SUFFIX_BY_LANG[lang]
    # Remplacer tout suffixe " | <quelque chose>" final par le bon
    new = re.sub(r' \| (?:DAAT|דעת|Hilkhot Shabbat|הלכות שבת)$', new_suffix, new)
    if visible_len(new) <= 70:
        return new
    
    # Trouver le suffix (" | Hilkhot Shabbat" ou " | הלכות שבת" ou " | DAAT").
    suffix_match = re.search(r' \| (?:Hilkhot Shabbat|הלכות שבת|DAAT|דעת)$', new)
    if not suffix_match:
        return new
    suffix = suffix_match.group(0)
    body = new[:suffix_match.start()]
    target_body = 70 - len(suffix)
    if visible_len(body) <= target_body:
        return new
    # Trouver le préfixe "Siman X · Niveau N — " ou "Siman X — " ou "סימן X — "
    # On garde tout jusqu'au DERNIER " — " ; ce qui suit est la description.
    # Pour les index : "Siman X — desc"
    # Pour les niveaux : "Siman X · Niveau N — desc" ou "Siman X · Niveau N — sub · desc"
    m = re.match(r'^(.+? — )(.+)$', body)
    if not m:
        return new
    prefix, desc = m.group(1), m.group(2)
    prefix_vlen = visible_len(prefix)
    desc_max = target_body - prefix_vlen
    if desc_max < 8:
        return new
    new_desc = smart_truncate(desc, desc_max)
    return prefix + new_desc + suffix

def kind_of(fp):
    """Renvoie 'index' ou 'niveau'."""
    name = os.path.basename(fp)
    return "index" if name.startswith("index") else "niveau"

def lang_of(fp):
    """Renvoie 'fr','en','he'."""
    name = os.path.basename(fp)
    if name.endswith("-en.html"): return "en"
    if name.endswith("-he.html"): return "he"
    return "fr"

def main(write=False):
    patterns = [
        "siman-*/index.html", "siman-*/index-en.html", "siman-*/index-he.html",
        "siman-*/niveau-1-base.html", "siman-*/niveau-1-base-en.html", "siman-*/niveau-1-base-he.html",
        "siman-*/niveau-2-lamdan.html", "siman-*/niveau-2-lamdan-en.html", "siman-*/niveau-2-lamdan-he.html",
        "siman-*/niveau-3-synthese.html", "siman-*/niveau-3-synthese-en.html", "siman-*/niveau-3-synthese-he.html",
        "siman-*/niveau-4-daat-harav.html", "siman-*/niveau-4-daat-harav-en.html", "siman-*/niveau-4-daat-harav-he.html",
    ]
    total = 0; touched = 0; still_long = 0
    for pat in patterns:
        for fp in sorted(glob.glob(os.path.join(ROOT, pat))):
            with open(fp, encoding="utf-8") as f:
                html = f.read()
            m = title_re.search(html)
            if not m: continue
            total += 1
            old_title = m.group(2).strip()
            kind = kind_of(fp)
            lang = lang_of(fp)
            # Ne toucher qu'aux titres trop longs (> 70 chars).
            if visible_len(old_title) <= 70:
                continue
            new_title = shorten(old_title, kind, lang)
            if new_title != old_title:
                touched += 1
                if write:
                    new_html = title_re.sub(
                        lambda mm: f"{mm.group(1)}{new_title}{mm.group(3)}",
                        html, count=1)
                    with open(fp, "w", encoding="utf-8") as f:
                        f.write(new_html)
            if visible_len(new_title) > 70:
                still_long += 1
    print(f"Files checked     : {total}")
    print(f"Titles modified   : {touched}" + (" (WRITTEN)" if write else " (dry run)"))
    print(f"Still > 70 chars  : {still_long}")

if __name__ == "__main__":
    write = "--write" in sys.argv
    main(write=write)
