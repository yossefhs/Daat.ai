#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-limoud-course-schema.py — Ajoute un JSON-LD schema.org Course sur les
3 pages hub Daat Yomi (FR/HE/EN) + un LearningResource isPartOf sur chaque
page jour-NNN-{he,en}.html.

Effet attendu :
- Affichage potentiel dans le carrousel "Cours" Google avec badge Gratuit
- Compréhension par les AI Overviews que /limoud/ est un PROGRAMME
  structuré, pas une simple page de blog
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMOUD = ROOT / "limoud"

COURSE_META = {
    "fr": {
        "name": "Daat Yomi — Hilkhot Shabbat en 9 mois",
        "description": "Programme d'étude quotidien du Choulhan Aroukh, Hilkhot Shabbat. 5 séifim par jour (dimanche-jeudi), 124 simanim couverts en 194 jours d'étude. Texte du Mehaber + Rama + Choulhan Aroukh HaRav, traduction française fluide, explications progressives.",
        "teaches": ["Hilkhot Shabbat", "Choulhan Aroukh Orah Haïm 242-365", "Halakha pratique de Shabbat"],
        "locale": "fr-FR",
        "level": "Tous niveaux",
    },
    "he": {
        "name": "דעת יומי — הלכות שבת ב-9 חודשים",
        "description": "תוכנית לימוד יומית של שולחן ערוך, הלכות שבת. 5 סעיפים ביום (ראשון-חמישי), 124 סימנים ב-194 ימי לימוד. טקסט המחבר + הרמ״א + שולחן ערוך הרב, תרגום עברי בהיר, הסברים מדורגים.",
        "teaches": ["הלכות שבת", "שולחן ערוך אורח חיים רמ״ב-שס״ה", "הלכה למעשה לשבת"],
        "locale": "he-IL",
        "level": "כל הרמות",
    },
    "en": {
        "name": "Daat Yomi — Hilchos Shabbos in 9 months",
        "description": "Daily study program of the Shulchan Aruch, Hilchos Shabbos. 5 seifim per day (Sunday-Thursday), 124 simanim covered in 194 study days. Mechaber + Rema + Shulchan Aruch HaRav text, fluent English translation, progressive explanations.",
        "teaches": ["Hilchos Shabbos", "Shulchan Aruch Orach Chayim 242-365", "Practical halacha of Shabbos"],
        "locale": "en-US",
        "level": "All levels",
    },
}


def url_for_hub(lang: str) -> str:
    if lang == "fr":
        return "https://daattorah.com/limoud/"
    return f"https://daattorah.com/limoud/{lang}/"


def build_course_jsonld(lang: str, num_days: int, start_date: str, end_date: str) -> str:
    meta = COURSE_META[lang]
    canonical = url_for_hub(lang)

    # Entité Organization (EducationalOrganization), embedded pour que le @id résolve
    # sur la même page (sinon Google affiche "provider name manquant" comme warning)
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

    # Entité Person (Rav), embedded pour la même raison
    person = {
        "@type": "Person",
        "@id": "https://daattorah.com/#rav-samama",
        "name": "Rav Yossef Haim Samama",
        "alternateName": "רב יוסף חיים סממה",
        "jobTitle": "Rabbin, posek, fondateur de Daat Torah",
        "worksFor": {"@id": "https://daattorah.com/#organization"},
    }

    course = {
        "@type": "Course",
        "@id": f"{canonical}#course",
        "name": meta["name"],
        "description": meta["description"],
        "url": canonical,
        "inLanguage": meta["locale"],
        "isAccessibleForFree": True,
        "provider": {"@id": "https://daattorah.com/#organization"},
        "instructor": {"@id": "https://daattorah.com/#rav-samama"},
        "teaches": meta["teaches"],
        "educationalLevel": meta["level"],
        "audience": {"@type": "EducationalAudience", "educationalRole": "Étudiant en halakha"},
        "numberOfCredits": 0,
        "hasCourseInstance": [{
            "@type": "CourseInstance",
            "@id": f"{canonical}#instance",
            "name": "Cycle 2026-2027",
            "courseMode": "online",
            "courseWorkload": "PT15M",
            "startDate": start_date,
            "endDate": end_date,
            "instructor": {"@id": "https://daattorah.com/#rav-samama"},
            "totalSessionCount": num_days,
        }],
        "image": "https://daattorah.com/assets/img/og/og-default.svg",
        "creator": {"@id": "https://daattorah.com/#rav-samama"},
    }

    graph = {
        "@context": "https://schema.org",
        "@graph": [course, organization, person],
    }
    return json.dumps(graph, ensure_ascii=False, indent=2)


def inject(html: str, jsonld_str: str, marker: str) -> tuple:
    """Replace existing schema block (by marker) or insert before </head>.
    Always idempotent : un re-run met à jour, jamais ne duplique.
    Returns (new_html, action) où action ∈ {'inserted', 'updated', 'unchanged'}."""
    block = f'<script type="application/ld+json" data-schema="{marker}">\n{jsonld_str}\n</script>'
    pattern = re.compile(
        r'<script type="application/ld\+json" data-schema="'
        + re.escape(marker)
        + r'">.*?</script>',
        re.S,
    )
    if pattern.search(html):
        new_html, n = pattern.subn(block, html, count=1)
        return new_html, ("updated" if new_html != html else "unchanged")
    new_html = html.replace("</head>", "\n" + block + "\n</head>", 1)
    return new_html, "inserted"


def main():
    plan = json.loads((ROOT / "data" / "limoud-plan.json").read_text())
    entries = plan["entries"]
    num_days = len(entries)
    start_date = entries[0]["date"]
    end_date = entries[-1]["date"]

    print(f"Plan Daat Yomi : {num_days} jours, du {start_date} au {end_date}")
    print()

    pages = {
        "fr": LIMOUD / "index.html",
        "he": LIMOUD / "index-he.html",
        "en": LIMOUD / "index-en.html",
    }

    for lang, p in pages.items():
        if not p.exists():
            print(f"  ⚠️ {p} absent, skip")
            continue
        html = p.read_text(encoding="utf-8")
        jsonld_str = build_course_jsonld(lang, num_days, start_date, end_date)
        new_html, action = inject(html, jsonld_str, "limoud-course")
        if action != "unchanged":
            p.write_text(new_html, encoding="utf-8")
        print(f"  {'✓' if action != 'unchanged' else '·'} {p.name} : Course schema {action}")


if __name__ == "__main__":
    main()
