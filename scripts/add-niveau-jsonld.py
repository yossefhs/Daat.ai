#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-niveau-jsonld.py — Injecte un JSON-LD (Article + LearningResource +
BreadcrumbList) dans les ~1488 pages de niveau qui n'en ont pas.

Le but : faire de chaque page niveau-X.html une entité structurée pour
Google et les AI Overviews, avec un author (@id) cohérent qui pointe vers
le Person défini dans about.html.

Idempotent : skip si la page contient déjà <script type="application/ld+json">.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

NIVEAU_INFO = {
    "niveau-1-base": {
        "name": "Niveau 1 — Base",
        "resourceType": "Cours d'étude halakhique — niveau initiation",
        "educationalLevel": "Débutant",
        "audience": "Débutant et intermédiaire",
        "shortKey": "base",
    },
    "niveau-2-lamdan": {
        "name": "Niveau 2 — Lamdan",
        "resourceType": "Étude approfondie — pilpoul Rishonim et Acharonim",
        "educationalLevel": "Avancé",
        "audience": "Étudiant avancé en halakha",
        "shortKey": "lamdan",
    },
    "niveau-3-synthese": {
        "name": "Niveau 3 — Synthèse",
        "resourceType": "Synthèse halakhique structurée pour révision",
        "educationalLevel": "Intermédiaire",
        "audience": "Étudiant intermédiaire",
        "shortKey": "synthese",
    },
    "niveau-4-daat-harav": {
        "name": "Niveau 4 — Daat HaRav",
        "resourceType": "Shitah de l'Admour HaZaken (Choulhan Aroukh HaRav)",
        "educationalLevel": "Avancé",
        "audience": "Étudiant avancé, lamdan",
        "shortKey": "daat-harav",
    },
}

LANG_INFO = {
    "fr": {"locale": "fr-FR", "ariane_oh": "Orah Haïm", "ariane_root": "Hilkhot Shabbat", "ariane_siman": "Siman"},
    "he": {"locale": "he-IL", "ariane_oh": "אורח חיים", "ariane_root": "הלכות שבת", "ariane_siman": "סימן"},
    "en": {"locale": "en-US", "ariane_oh": "Orach Chayim", "ariane_root": "Hilchos Shabbos", "ariane_siman": "Siman"},
}


def extract_meta(html: str) -> dict:
    """Extrait title, description, canonical, lang depuis le head."""
    def grab(pattern, group=1, default=""):
        m = re.search(pattern, html, re.I)
        return m.group(group).strip() if m else default

    # title peut contenir des balises inline (<bdi>, <em>, etc.) → on capture
    # tout le contenu, puis on strip les balises
    m_title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    title = ""
    if m_title:
        raw = m_title.group(1)
        title = re.sub(r"<[^>]+>", "", raw).strip()
        title = re.sub(r"\s+", " ", title)
    description = grab(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)')
    if not description:
        description = grab(r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']description')
    canonical = grab(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)')
    lang = grab(r'<html\s+lang=["\']([a-z]{2})')
    image = grab(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)')
    return {
        "title": title,
        "description": description,
        "canonical": canonical,
        "lang": lang or "fr",
        "image": image or "https://daattorah.com/assets/img/og/og-default.svg",
    }


def parse_filename(path: Path):
    """sources/shabbat/siman-248/niveau-1-base-he.html → (248, 'niveau-1-base', 'he')"""
    m = re.match(r"siman-(\d+)", path.parent.name)
    if not m:
        return None
    siman = int(m.group(1))
    stem = path.stem
    # gère les 2 cas : niveau-1-base[-he|-en].html
    m2 = re.match(r"(niveau-[1-4]-[a-z]+(?:-[a-z]+)*?)(?:-(he|en))?$", stem)
    if not m2:
        return None
    base_key = m2.group(1)
    # le base_key peut être p.ex. "niveau-4-daat-harav"
    # ou "niveau-1-base"
    # vérification dans NIVEAU_INFO
    if base_key not in NIVEAU_INFO:
        # tente de nettoyer le suffixe langue (-he ou -en)
        for k in NIVEAU_INFO:
            if base_key.startswith(k):
                base_key = k
                break
        else:
            return None
    lang_suffix = m2.group(2)
    lang = lang_suffix if lang_suffix else "fr"
    return siman, base_key, lang


def build_jsonld(siman: int, niveau_key: str, lang: str, meta: dict) -> str:
    info = NIVEAU_INFO[niveau_key]
    lang_info = LANG_INFO[lang]
    short = info["shortKey"]

    # URL canonique : /oh/N/{base|lamdan|synthese|daat-harav}[/he|/en]
    base_url = f"https://daattorah.com/oh/{siman}/{short}"
    canonical = meta["canonical"] or base_url
    if lang == "he":
        canonical = base_url + "/he"
    elif lang == "en":
        canonical = base_url + "/en"

    article_id = f"{canonical}#article"

    article = {
        "@type": ["Article", "LearningResource"],
        "@id": article_id,
        "headline": meta["title"][:110],
        "description": meta["description"][:300],
        "url": canonical,
        "image": meta["image"],
        "inLanguage": lang_info["locale"],
        "isAccessibleForFree": True,
        "learningResourceType": info["resourceType"],
        "educationalLevel": info["educationalLevel"],
        "audience": {"@type": "EducationalAudience", "educationalRole": info["audience"]},
        "isPartOf": {"@id": f"https://daattorah.com/oh/{siman}/#siman"},
        "author": {"@id": "https://daattorah.com/#rav-samama"},
        "publisher": {"@id": "https://daattorah.com/#organization"},
        "datePublished": "2026-01-01",
        "dateModified": "2026-06-10",
    }

    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "DAAT", "item": "https://daattorah.com/"},
            {"@type": "ListItem", "position": 2, "name": lang_info["ariane_oh"], "item": "https://daattorah.com/oh/"},
            {"@type": "ListItem", "position": 3, "name": f"{lang_info['ariane_siman']} {siman}", "item": f"https://daattorah.com/oh/{siman}/"},
            {"@type": "ListItem", "position": 4, "name": info["name"], "item": canonical},
        ],
    }

    # Embedded Organization + Person pour que les @id author/publisher
    # résolvent localement (sinon Google warning "name missing on Thing")
    organization = {
        "@type": ["Organization", "EducationalOrganization"],
        "@id": "https://daattorah.com/#organization",
        "name": "DAAT דעת",
        "alternateName": "Daat Torah",
        "url": "https://daattorah.com/",
        "logo": "https://daattorah.com/assets/img/og/og-default.svg",
        "description": "Plateforme d'étude du Choulhan Aroukh (Orah Haïm, Hilkhot Shabbat) en français, hébreu et anglais, 4 niveaux de profondeur, assistant IA Daat.",
        "founder": {"@id": "https://daattorah.com/#rav-samama"},
    }

    person = {
        "@type": "Person",
        "@id": "https://daattorah.com/#rav-samama",
        "name": "Rav Yossef Haim Samama",
        "alternateName": "רב יוסף חיים סממה",
        "jobTitle": "Rabbin, posek, fondateur de Daat Torah",
        "worksFor": {"@id": "https://daattorah.com/#organization"},
    }

    graph = {"@context": "https://schema.org", "@graph": [article, breadcrumb, organization, person]}
    return json.dumps(graph, ensure_ascii=False, indent=2)


MARKER = "niveau-jsonld"


def inject(html: str, jsonld_str: str) -> tuple:
    """Replace existing block (by marker) or insert before </head>.
    Returns (new_html, action) avec action ∈ {'inserted','updated','unchanged'}."""
    block = (
        f'<script type="application/ld+json" data-schema="{MARKER}">\n'
        f"{jsonld_str}\n"
        "</script>"
    )
    pattern = re.compile(
        r'<script type="application/ld\+json" data-schema="'
        + re.escape(MARKER)
        + r'">.*?</script>',
        re.S,
    )
    if pattern.search(html):
        new_html, _ = pattern.subn(block, html, count=1)
        return new_html, ("updated" if new_html != html else "unchanged")
    new_html = html.replace("</head>", "\n" + block + "\n</head>", 1)
    return new_html, "inserted"


def has_existing_jsonld(html: str) -> bool:
    """Vrai si la page a déjà un JSON-LD ANCIEN (sans marker, du premier run)
    ou un JSON-LD non-niveau (genre Article inline existant). On les laisse en place."""
    if f'data-schema="{MARKER}"' in html:
        return False  # géré par inject() qui fait un update
    # Cherche un JSON-LD sans notre marker
    pattern = re.compile(
        r'<script type="application/ld\+json"(?!\s+data-schema="' + re.escape(MARKER) + r'")',
    )
    return bool(pattern.search(html))


def process_file(path: Path, dry_run=False) -> tuple:
    """Retourne (status, reason)."""
    parsed = parse_filename(path)
    if not parsed:
        return ("skip", "filename non reconnu")
    siman, niveau_key, lang = parsed
    html = path.read_text(encoding="utf-8")

    # Migration v1 → v2 : si un ancien JSON-LD niveau (sans marker mais
    # avec notre signature "learningResourceType") est présent, le retirer
    # pour pouvoir injecter le @graph v2 enrichi (Person + Organization).
    pattern_v1 = re.compile(
        r'\s*<script type="application/ld\+json">\s*\{[^<]*?"learningResourceType"[^<]*?\}\s*</script>\s*',
        re.S,
    )
    html_after_migration = pattern_v1.sub("\n", html)
    if html_after_migration != html:
        html = html_after_migration  # on l'écrit après injection du nouveau bloc

    # has_existing_jsonld() ne flag QUE les JSON-LD étrangers (sans notre marker)
    if has_existing_jsonld(html):
        return ("skip", "JSON-LD étranger")
    meta = extract_meta(html)
    if not meta["title"]:
        return ("skip", "pas de title")
    jsonld_str = build_jsonld(siman, niveau_key, lang, meta)
    if dry_run:
        return ("would-inject", f"{niveau_key}/{lang}")
    new_html, action = inject(html, jsonld_str)
    if action != "unchanged":
        path.write_text(new_html, encoding="utf-8")
    return (action, f"{niveau_key}/{lang}")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    only_siman = None
    if "--siman" in args:
        only_siman = int(args[args.index("--siman") + 1])

    files = sorted(SHABBAT.glob("siman-*/niveau-*.html"))
    if only_siman:
        files = [f for f in files if f.parent.name == f"siman-{only_siman}"]

    stats = {"inject": 0, "skip": 0, "would-inject": 0}
    reasons = {}
    for f in files:
        status, reason = process_file(f, dry_run=dry_run)
        stats[status] = stats.get(status, 0) + 1
        if status == "skip":
            reasons[reason] = reasons.get(reason, 0) + 1

    print(f"Fichiers traités    : {len(files)}")
    print(f"  injectés          : {stats.get('inject', 0)}")
    print(f"  would-inject      : {stats.get('would-inject', 0)}")
    print(f"  skipped           : {stats.get('skip', 0)}")
    if reasons:
        print("  raisons skip      :")
        for r, n in sorted(reasons.items(), key=lambda x: -x[1]):
            print(f"    {r}: {n}")


if __name__ == "__main__":
    main()
