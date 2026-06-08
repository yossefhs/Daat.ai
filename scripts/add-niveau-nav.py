#!/usr/bin/env python3
"""
DAAT — Ajoute la navigation "Niveau précédent / suivant" et le sélecteur N1/N2/N3/N4
à la fin de chaque page niveau d'un siman (toutes langues : FR, EN, HE).

Pour chaque fichier sources/shabbat/siman-NNN/niveau-{1,2,3,4}-*.html :
  - détecte le siman, le niveau, la langue ;
  - calcule le siman précédent/suivant (en sautant les NO_LEVELS) ;
  - construit le bloc <nav class="niveau-nav"> avec :
      * lien vers le même niveau du siman précédent (si existant) ;
      * 4 onglets N1/N2/N3/N4 (l'onglet courant marqué .active) ;
      * lien vers le même niveau du siman suivant (si existant) ;
  - insère le bloc juste avant </main> (ou </body> si pas de </main>) ;
  - n'insère rien si la nav existe déjà (idempotent).

Les simanim 304 et 322 (non rédigés par l'Admour HaZaken) sont sautés
dans le calcul prev/next ET ne reçoivent pas la nav.

Usage:
    python3 scripts/add-niveau-nav.py [--dry-run]
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "sources", "shabbat")
FIRST, LAST = 242, 365
NO_LEVELS = {304, 322}  # Pas de niveaux rédigés.

# Mappings de noms de fichier par niveau.
LEVEL_FILES = {
    1: "niveau-1-base",
    2: "niveau-2-lamdan",
    3: "niveau-3-synthese",
    4: "niveau-4-daat-harav",
}

# Labels par langue (FR par défaut sur fichiers sans suffixe).
LABELS = {
    "fr": {
        "aria": "Navigation entre niveaux",
        "prev_prefix": "← Siman",
        "next_suffix": "Siman {} →",
    },
    "en": {
        "aria": "Navigation between levels",
        "prev_prefix": "← Siman",
        "next_suffix": "Siman {} →",
    },
    "he": {
        "aria": "ניווט בין רמות",
        "prev_prefix": "סימן",   # affiché avec flèche → en RTL = inversée
        "next_suffix": "סימן {}",
    },
}

# CSS — injecté dans la <style> existante (pas de variables CSS supposées présentes).
CSS_BLOCK = """
  /* Niveau navigation (prev/next siman + onglets N1-N4) */
  .niveau-nav {
    display: flex; justify-content: space-between; align-items: center;
    gap: 1rem; padding: 1.5rem 0; border-top: 1px solid #d4c89a;
    margin: 3rem 0 1.5rem; flex-wrap: wrap;
    font-family: 'Inter', 'Helvetica', sans-serif; font-size: 11pt;
  }
  .niveau-nav a {
    color: #1A1F3A; text-decoration: none;
    padding: 0.5rem 1rem; border-radius: 4px;
    transition: background 0.2s, color 0.2s;
  }
  .niveau-nav a:hover { background: #FAF6EE; color: #1A1F3A; }
  .niveau-nav .nav-niveaux { display: flex; gap: 0.5rem; }
  .niveau-nav .nav-level { border: 1px solid #d4c89a; font-weight: 600; letter-spacing: 1px; }
  .niveau-nav .nav-level.active { background: #1A1F3A; color: #fff; border-color: #1A1F3A; }
  .niveau-nav .nav-level.active:hover { background: #1A1F3A; color: #fff; }
  .niveau-nav .nav-spacer { flex: 1; }
  @media (max-width: 640px) {
    .niveau-nav { flex-direction: column; gap: 0.75rem; }
  }
  @media print { .niveau-nav { display: none; } }
"""

NAV_MARKER = 'class="niveau-nav"'  # classe sur le <nav> = marqueur d'idempotence
CSS_MARKER = "/* Niveau navigation (prev/next siman + onglets N1-N4) */"


def lang_suffix(lang):
    """Retourne le suffixe de nom de fichier pour une langue."""
    return "" if lang == "fr" else f"-{lang}"


def find_existing_siman(n):
    """Retourne True si le siman n est dans la plage et n'est pas exclu."""
    return FIRST <= n <= LAST and n not in NO_LEVELS


def prev_siman(n):
    """Numéro du siman précédent disponible, ou None."""
    k = n - 1
    while k >= FIRST:
        if k not in NO_LEVELS:
            return k
        k -= 1
    return None


def next_siman(n):
    """Numéro du siman suivant disponible, ou None."""
    k = n + 1
    while k <= LAST:
        if k not in NO_LEVELS:
            return k
        k += 1
    return None


def build_nav(siman, level, lang):
    """Construit le bloc <nav class="niveau-nav"> pour cette page."""
    L = LABELS[lang]
    suf = lang_suffix(lang)

    p = prev_siman(siman)
    n = next_siman(siman)

    parts = []
    parts.append(
        f'<nav class="niveau-nav" aria-label="{L["aria"]}">'
    )

    # Lien prev (ou spacer).
    if p is not None:
        prev_file = f"../siman-{p}/{LEVEL_FILES[level]}{suf}.html"
        if lang == "he":
            # En RTL, la flèche "précédent" pointe vers la droite.
            label = f'{L["prev_prefix"]} {p} →'
        else:
            label = f'{L["prev_prefix"]} {p}'
        parts.append(f'  <a href="{prev_file}" class="nav-prev">{label}</a>')
    else:
        parts.append('  <span class="nav-spacer"></span>')

    # Onglets niveaux.
    parts.append('  <div class="nav-niveaux">')
    for lvl in (1, 2, 3, 4):
        active = " active" if lvl == level else ""
        href = f"{LEVEL_FILES[lvl]}{suf}.html"
        parts.append(
            f'    <a href="{href}" class="nav-level{active}">N{lvl}</a>'
        )
    parts.append('  </div>')

    # Lien next (ou spacer).
    if n is not None:
        next_file = f"../siman-{n}/{LEVEL_FILES[level]}{suf}.html"
        if lang == "he":
            label = f'← {L["next_suffix"].format(n)}'
        else:
            label = L["next_suffix"].format(n)
        parts.append(f'  <a href="{next_file}" class="nav-next">{label}</a>')
    else:
        parts.append('  <span class="nav-spacer"></span>')

    parts.append('</nav>')
    return "\n".join(parts) + "\n"


def inject_css(html):
    """Injecte le bloc CSS dans la première balise <style> du fichier.
    Si pas de <style>, en crée une dans <head>."""
    if CSS_MARKER in html:
        return html, False
    # Cherche la première </style>.
    m = re.search(r'</style>', html)
    if m:
        idx = m.start()
        return html[:idx] + CSS_BLOCK + html[idx:], True
    # Pas de style — créer une dans <head>.
    m = re.search(r'</head>', html, re.I)
    if m:
        idx = m.start()
        block = f"<style>{CSS_BLOCK}</style>\n"
        return html[:idx] + block + html[idx:], True
    return html, False


def inject_nav(html, nav_block):
    """Insère le bloc nav avant </main> (ou </body> en fallback)."""
    if NAV_MARKER in html:
        return html, False
    # Préférence : juste avant </main>.
    m = re.search(r'</main>', html, re.I)
    if m:
        idx = m.start()
        return html[:idx] + nav_block + html[idx:], True
    # Fallback : avant </body>.
    m = re.search(r'</body>', html, re.I)
    if m:
        idx = m.start()
        return html[:idx] + nav_block + html[idx:], True
    return html, False


# Détecte (siman, level, lang) à partir d'un chemin de fichier.
PATH_RE = re.compile(
    r"siman-(?P<siman>\d{3})/"
    r"niveau-(?P<level>[1-4])-[a-z0-9-]+?"
    r"(?P<lang>-en|-he)?\.html$"
)


def detect(path):
    m = PATH_RE.search(path.replace(os.sep, "/"))
    if not m:
        return None
    siman = int(m.group("siman"))
    level = int(m.group("level"))
    lang_tag = m.group("lang")
    lang = "fr"
    if lang_tag == "-en":
        lang = "en"
    elif lang_tag == "-he":
        lang = "he"
    return siman, level, lang


def main():
    dry = "--dry-run" in sys.argv[1:]
    files_processed = 0
    files_updated = 0
    files_skipped = 0
    files_no_anchor = []
    by_lang = {"fr": 0, "en": 0, "he": 0}

    for n in range(FIRST, LAST + 1):
        if n in NO_LEVELS:
            continue
        d = os.path.join(ROOT, f"siman-{n}")
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.startswith("niveau-") or not fname.endswith(".html"):
                continue
            full = os.path.join(d, fname)
            info = detect(full)
            if info is None:
                continue
            siman, level, lang = info
            files_processed += 1

            with open(full, encoding="utf-8") as f:
                html = f.read()

            if NAV_MARKER in html:
                files_skipped += 1
                continue

            nav_block = build_nav(siman, level, lang)
            new_html, css_added = inject_css(html)
            new_html, nav_added = inject_nav(new_html, nav_block)

            if not nav_added:
                files_no_anchor.append(full)
                continue

            if new_html != html and not dry:
                with open(full, "w", encoding="utf-8") as f:
                    f.write(new_html)
            files_updated += 1
            by_lang[lang] += 1

    print(f"Niveau-nav — fichiers parcourus : {files_processed}")
    print(f"  mis à jour                    : {files_updated}")
    print(f"    dont FR : {by_lang['fr']}, EN : {by_lang['en']}, HE : {by_lang['he']}")
    print(f"  déjà à jour (sautés)          : {files_skipped}")
    if files_no_anchor:
        print(f"  SANS </main> ni </body> : {len(files_no_anchor)}")
        for p in files_no_anchor[:10]:
            print(f"    - {p}")
    if dry:
        print("  (dry-run : aucun fichier écrit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
