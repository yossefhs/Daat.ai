#!/usr/bin/env python3
"""
DAAT — Ajoute le CSS responsive mobile (<=768px / <=480px) aux pages
des niveaux 1, 2 et 3 (le N4 est déjà responsive).

Pour chaque fichier `niveau-{1,2,3}-*.html` sous `sources/shabbat/siman-*/` :
  - on cherche le PREMIER `<style>` … `</style>` (le bloc inline du <head>) ;
  - si ce bloc contient déjà `@media (max-width:` → on saute (déjà fait) ;
  - sinon on insère, juste avant la balise `</style>` fermante, un bloc
    `@media` adapté aux classes spécifiques du niveau.

Usage :
    python3 scripts/add-responsive-niveaux-123.py            # applique
    python3 scripts/add-responsive-niveaux-123.py --dry-run  # log seul
    python3 scripts/add-responsive-niveaux-123.py --only=1   # un niveau
"""
import argparse
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "sources", "shabbat")

# Marqueur unique pour reconnaître nos blocs et éviter les doubles insertions.
MARKER = "/* DAAT responsive mobile (auto-injected) */"

# --------- CSS responsive par niveau --------------------------------------
# Adapté aux classes réellement présentes dans chaque niveau (voir
# siman-244 comme référence). Les sélecteurs absents dans un fichier
# donné sont simplement ignorés par le navigateur — sans effet de bord.

RESP_N1 = """
""" + MARKER + """
@media (max-width: 768px) {
  header { padding: 0 16px; height: auto; min-height: 60px; flex-wrap: wrap; gap: 8px; padding-top: 8px; padding-bottom: 8px; }
  .logo-he { font-size: 22px; }
  .logo-en { font-size: 13px; letter-spacing: 2px; }
  .breadcrumb { padding: 8px 16px; }
  .page-hero { padding: 28px 16px; }
  .hero-title { font-size: 26px; }
  .hero-subtitle { font-size: 15px; }
  .main { max-width: 100%; padding: 28px 16px 36px; }
  .doc-section { margin-bottom: 36px; }
  .section-title { font-size: 22px; }
  .hebrew-box { padding: 20px 18px; }
  .hebrew-text { font-size: 18px; line-height: 1.85; }
  .rama-text { font-size: 15px; }
  .translation-box { padding: 18px 18px; }
  .translation-text { font-size: 16px; line-height: 1.75; }
  .explanation-box { padding: 18px 18px; }
  .explanation-box h3 { font-size: 19px; }
  .explanation-box p { font-size: 15px; line-height: 1.7; }
  .concept-grid, .practical-grid { grid-template-columns: 1fr; gap: 12px; }
  .concept-card { padding: 16px; }
  .pesak-box { padding: 22px 20px; }
  .pesak-he { font-size: 19px; line-height: 1.7; }
  .pesak-fr { font-size: 15px; line-height: 1.7; }
  .ped-box { grid-template-columns: 32px 1fr; }
  .ped-content { padding: 12px 14px; }
  .ped-text { font-size: 15px; }
  .seif-block { margin: 22px 0; }
  .seif-block h3 { font-size: 16px; }
  .seif-block p, .seif-block li { font-size: 15px; line-height: 1.65; }
  .seif-block table, blockquote.text-source { font-size: 14px; }
  .seif-block table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; white-space: nowrap; }
  blockquote.text-source { padding: 12px 14px; font-size: 17px; line-height: 1.85; }
  .translation, .definition, .key-point, .remember, .question-box, .case-card { padding: 12px 14px; }
  .bottom-nav { flex-direction: column; gap: 12px; align-items: stretch; text-align: center; }
  footer { padding: 20px 16px; }
}
@media (max-width: 480px) {
  .logo-en { display: none; }
  .hero-title { font-size: 22px; }
  .section-title { font-size: 20px; }
  .hebrew-text { font-size: 17px; }
  .translation-text { font-size: 15px; }
  .main { padding: 22px 12px 28px; }
}
"""

RESP_N2 = """
""" + MARKER + """
@media (max-width: 768px) {
  body { font-size: 15px; line-height: 1.65; }
  main { padding: 16px; max-width: 100%; box-sizing: border-box; overflow-wrap: break-word; }
  .cover { margin-top: 1.2cm; margin-bottom: 1.2cm; }
  .cover h1 { font-size: 22pt; }
  .cover .he-title { font-size: 26pt; }
  .cover .he-sub { font-size: 14pt; }
  .cover .he-subject { font-size: 12pt; }
  .cover .level-badge { font-size: 11pt; padding: 10px 22px; }
  .cover .subtitle { font-size: 12pt; }
  h2.section-title { font-size: 14pt; padding: 8px 12px; margin-top: 22px; }
  h3 { font-size: 12pt; margin-top: 18px; }
  .he { font-size: 12pt; line-height: 1.85; }
  .sacred-text { padding: 12px 14px; font-size: 12pt; line-height: 1.85; }
  .pilpul-box, .kashya-box, .teruts-box, .hakira-box, .nafka-mina-box,
  .yesod-box, .machloket-box, .rishon-card, .index-box { padding: 10px 14px; margin: 12px 0; }
  blockquote { margin: 10px 0; padding: 8px 12px; font-size: 12pt; }
  table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; white-space: nowrap; font-size: 10pt; }
  th, td { padding: 8px; }
  .index-box ol { padding-right: 18px; }
  .index-box[dir="rtl"] ol { padding-right: 18px; }
}
@media (max-width: 480px) {
  body { font-size: 14px; }
  main { padding: 12px; }
  .cover h1 { font-size: 19pt; }
  .cover .he-title { font-size: 22pt; }
  h2.section-title { font-size: 13pt; }
  h3 { font-size: 11.5pt; }
  .sacred-text, .he { font-size: 11.5pt; }
}
"""

RESP_N3 = """
""" + MARKER + """
@media (max-width: 768px) {
  body { font-size: 15px; line-height: 1.65; }
  .container { max-width: 100%; padding: 16px; box-sizing: border-box; overflow-wrap: break-word; }
  .cover { margin: 1.2cm 0; }
  .cover h1 { font-size: 24pt; }
  .cover .he-title { font-size: 22pt; }
  .cover .subtitle { font-size: 12pt; }
  h2 { font-size: 15pt; margin: 22pt 0 10pt; }
  h3 { font-size: 12.5pt; margin: 16pt 0 6pt; }
  h4 { font-size: 12pt; margin: 12pt 0 6pt; }
  .he { font-size: 12pt; line-height: 1.85; }
  .axiome { padding: 12pt 14pt; font-size: 11.5pt; line-height: 1.7; }
  .axiome strong { font-size: 12.5pt; }
  .remember, .warning, .mnemonic, .pesak-box, .toc, .schema { padding: 10pt 14pt; margin: 12pt 0; }
  .schema-step { padding: 6pt 10pt; }
  table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; white-space: nowrap; font-size: 10pt; }
  th, td { padding: 8pt; }
  .toc ol { margin-left: 16pt; }
}
@media (max-width: 480px) {
  body { font-size: 14px; }
  .container { padding: 12px; }
  .cover h1 { font-size: 20pt; }
  .cover .he-title { font-size: 19pt; }
  h2 { font-size: 14pt; }
  h3 { font-size: 12pt; }
  .axiome { font-size: 11pt; }
  .he { font-size: 11.5pt; }
}
"""

LEVELS = {
    1: ("niveau-1-base", RESP_N1),
    2: ("niveau-2-lamdan", RESP_N2),
    3: ("niveau-3-synthese", RESP_N3),
}


def has_responsive_media(style_block: str) -> bool:
    """Vrai si le bloc <style> contient déjà une media query mobile."""
    return bool(re.search(r"@media\s*\([^)]*max-width\s*:", style_block))


def patch_html(html: str, css_block: str):
    """Insère le bloc CSS responsive juste avant le 1er `</style>`.

    Renvoie (nouveau_html, statut) où statut ∈ {"inserted", "skip-existing",
    "skip-no-style", "skip-marker"}.
    """
    if MARKER in html:
        return html, "skip-marker"

    # Trouver le 1er <style>...</style> dans le <head>.
    m = re.search(r"<style\b[^>]*>(.*?)</style>", html, flags=re.S)
    if not m:
        return html, "skip-no-style"

    style_body = m.group(1)
    if has_responsive_media(style_body):
        return html, "skip-existing"

    close_at = m.end() - len("</style>")
    new_html = html[:close_at] + css_block + html[close_at:]
    return new_html, "inserted"


def find_files(only_levels):
    """Renvoie [(level, path), ...] trié."""
    out = []
    for n in sorted(os.listdir(ROOT)):
        if not n.startswith("siman-"):
            continue
        d = os.path.join(ROOT, n)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            for lvl, (prefix, _css) in LEVELS.items():
                if lvl not in only_levels:
                    continue
                if fname.startswith(prefix) and fname.endswith(".html"):
                    out.append((lvl, os.path.join(d, fname)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="N'écrit rien, log seulement.")
    ap.add_argument("--only", default="1,2,3",
                    help="Niveaux à traiter, ex: --only=1,2")
    args = ap.parse_args()

    only_levels = {int(x) for x in args.only.split(",") if x.strip()}

    stats = {lvl: {"inserted": 0, "skip-existing": 0,
                    "skip-no-style": 0, "skip-marker": 0}
                for lvl in LEVELS}

    files = find_files(only_levels)
    print(f"Fichiers candidats : {len(files)}\n")

    for lvl, path in files:
        with open(path, encoding="utf-8") as f:
            html = f.read()
        new_html, status = patch_html(html, LEVELS[lvl][1])
        stats[lvl][status] += 1
        if status == "inserted" and not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_html)

    print("Résumé par niveau :")
    print(f"{'niveau':<8}{'insérés':<10}{'déjà':<10}"
            f"{'no-style':<12}{'marker':<10}")
    for lvl in (1, 2, 3):
        if lvl not in only_levels:
            continue
        s = stats[lvl]
        print(f"N{lvl}      {s['inserted']:<10}{s['skip-existing']:<10}"
                f"{s['skip-no-style']:<12}{s['skip-marker']:<10}")

    if args.dry_run:
        print("\n(dry-run : aucun fichier modifié)")


if __name__ == "__main__":
    main()
