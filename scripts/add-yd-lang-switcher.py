#!/usr/bin/env python3
"""Injecte le sélecteur de langue flottant FR/HE/EN + les liens hreflang dans
les pages françaises d'un siman Yoreh De'ah (modèle identique à Hilkhot Shabbat).

Pages traitées : index.html, niveau-1-base.html, niveau-3-synthese.html,
niveau-4-halakha.html.  Le niveau-2-lamdan.html est EXCLU (hébreu uniquement).

Usage : python3 scripts/add-yd-lang-switcher.py 87
        python3 scripts/add-yd-lang-switcher.py 87 88 89 90 91
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://daattorah.com"

# page -> slug de route (index = "" ; base/synthese/halakha)
PAGES = {
    "index.html": "",
    "niveau-1-base.html": "base",
    "niveau-3-synthese.html": "synthese",
    "niveau-4-halakha.html": "halakha",
}

CSS = """<style id="daat-langsw-css">
  .lang-switcher-float {
    position: fixed; top: 12px; right: 12px; z-index: 9999;
    display: flex; gap: 4px; background: rgba(255,255,255,0.95);
    border: 1px solid #C5A55A; padding: 4px 6px; border-radius: 3px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1); font-family: 'Inter', sans-serif;
  }
  .lang-switcher-float a {
    font-size: 11px; letter-spacing: 1px; padding: 3px 7px; border-radius: 2px;
    color: #5a4a1a; text-decoration: none; border: 1px solid transparent;
  }
  .lang-switcher-float a.active { color: #1A1F3A; background: #FFF8E5; border-color: #1A1F3A; font-weight: 600; }
  .lang-switcher-float a:hover { color: #1A1F3A; border-color: #C5A55A; }
  @media print { .lang-switcher-float { display: none; } }
</style>"""

def base_url(n, slug):
    return f"{SITE}/yd/{n}/" if slug == "" else f"{SITE}/yd/{n}/{slug}"

def hreflang_block(n, slug):
    fr = base_url(n, slug)
    he = fr.rstrip("/") + "/he" if slug == "" else fr + "/he"
    en = fr.rstrip("/") + "/en" if slug == "" else fr + "/en"
    # index : /yd/N/he ; pages : /yd/N/<slug>/he
    if slug == "":
        he, en = f"{SITE}/yd/{n}/he", f"{SITE}/yd/{n}/en"
    return (
        f'  <link rel="alternate" hreflang="fr" href="{fr}">\n'
        f'  <link rel="alternate" hreflang="he" href="{he}">\n'
        f'  <link rel="alternate" hreflang="en" href="{en}">\n'
        f'  <link rel="alternate" hreflang="x-default" href="{fr}">\n'
    )

def switcher_div(n, slug, active="fr"):
    fr = base_url(n, slug)
    he = f"{SITE}/yd/{n}/he" if slug == "" else f"{base_url(n, slug)}/he"
    en = f"{SITE}/yd/{n}/en" if slug == "" else f"{base_url(n, slug)}/en"
    # liens relatifs au domaine (chemins absolus comme Shabbat)
    fr_p = f"/yd/{n}/" if slug == "" else f"/yd/{n}/{slug}"
    he_p = f"/yd/{n}/he" if slug == "" else f"/yd/{n}/{slug}/he"
    en_p = f"/yd/{n}/en" if slug == "" else f"/yd/{n}/{slug}/en"
    cls = ' class="active"'
    def a(href, lab, lng):
        return '<a href="' + href + '"' + (cls if lng == active else '') + '>' + lab + '</a>'
    return ('<div class="lang-switcher-float" role="navigation" aria-label="Language">'
            + a(fr_p, "FR", "fr") + a(he_p, "HE", "he") + a(en_p, "EN", "en") + "</div>")

def inject(path, n, slug):
    html = path.read_text(encoding="utf-8")
    changed = False
    # 1) hreflang après le canonical (si pas déjà présent)
    if "hreflang=" not in html:
        m = re.search(r'(<link\s+rel="canonical"[^>]*>)', html)
        if m:
            html = html.replace(m.group(1), m.group(1) + "\n" + hreflang_block(n, slug), 1)
            changed = True
    # 2) CSS du sélecteur (avant </head>)
    if 'id="daat-langsw-css"' not in html:
        html = html.replace("</head>", CSS + "\n</head>", 1)
        changed = True
    # 3) div flottant juste après <body...>
    if "lang-switcher-float" not in html:
        m = re.search(r'(<body[^>]*>)', html)
        if m:
            html = html.replace(m.group(1), m.group(1) + "\n" + switcher_div(n, slug, "fr"), 1)
            changed = True
    if changed:
        path.write_text(html, encoding="utf-8")
    return changed

def main(simanim):
    for n in simanim:
        d = ROOT / "sources" / "yoreh-deah" / f"siman-{n}"
        if not d.exists():
            print(f"  ⚠ {d} absent"); continue
        for page, slug in PAGES.items():
            f = d / page
            if f.exists():
                ok = inject(f, n, slug)
                print(f"  {'✓' if ok else '·'} siman {n}/{page}")
            else:
                print(f"  ⚠ {f} absent")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.isdigit()]
    if not args:
        print("Usage: python3 scripts/add-yd-lang-switcher.py 87 [88 ...]"); sys.exit(1)
    main(args)
