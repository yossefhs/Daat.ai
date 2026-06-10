#!/usr/bin/env python3
"""
DAAT — Générateur de représentations Markdown des simanim, pour indexation LLM.

Pour chaque siman 242-365, produit :
  sources/shabbat/siman-N/index.md

Ce fichier est une représentation Markdown compacte de la page index du siman :
- Titres trilingues (FR / HE / EN)
- Path canonique vers /oh/N/
- Texte hébreu officiel du séif 1 (Mehaber + hagahot Rama) issu du Sefaria-Export
- Liens vers les 4 niveaux d'étude (Base / Lamdan / Synthèse / Daat HaRav)
- Référence Sefaria

Conçu pour être idempotent : peut être ré-exécuté à volonté ; produit toujours
le même contenu pour les mêmes données d'entrée.

Sources :
- data/simanim/siman-N.json (titres FR/HE, description, sous-titre)
- data/limoud-simanim-catalog.json (titres EN, numHe)
- data/simanim-disponibles.json / -he.json / -en.json (présence par niveau)
- data/reference/choulhan-aroukh-oh-242-365.json (texte hébreu officiel)

Particularités :
- Simanim 304 et 322 : pas de Niveau 4 (bridge — l'Admour HaZaken ne les
  a pas écrits). Le .md mentionne explicitement cette absence.

Usage :
    python3 scripts/generate-siman-markdown.py            # tous les simanim
    python3 scripts/generate-siman-markdown.py --siman 248 # un seul
    python3 scripts/generate-siman-markdown.py --check     # sans écriture
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SHABBAT = ROOT / "sources" / "shabbat"

BASE_URL = "https://daattorah.com"
SEFARIA_BASE = "https://www.sefaria.org/Shulchan_Arukh,_Orach_Chayim"

BRIDGE_SIMANIM = {304, 322}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_index() -> dict[int, dict[str, Any]]:
    """Build a dict keyed by siman number with merged metadata."""
    catalog = load_json(DATA / "limoud-simanim-catalog.json")
    disp_fr = load_json(DATA / "simanim-disponibles.json")
    disp_he = load_json(DATA / "simanim-disponibles-he.json")
    disp_en = load_json(DATA / "simanim-disponibles-en.json")
    reference = load_json(DATA / "reference" / "choulhan-aroukh-oh-242-365.json")

    index: dict[int, dict[str, Any]] = {}

    for s in catalog["simanim"]:
        n = s["num"]
        index[n] = {
            "num": n,
            "numHe": s.get("numHe", ""),
            "titleFr": s.get("title", ""),
            "titleEn": s.get("titleEn", ""),
            "titleHe": s.get("titleHe", ""),
            "totalSeifim": s.get("totalSeifim", 0),
            "levels": {"n1": False, "n2": False, "n3": False, "n4": False},
            "description": "",
            "subtitle": "",
            "seif1Raw": "",
            "titleFrAlt": s.get("title", ""),
            "titleEnAlt": s.get("titleEn", ""),
            "titleHeAlt": s.get("titleHe", ""),
        }

    # Levels from FR disponibles file
    for s in disp_fr["simanim"]:
        n = s["num"]
        if n in index:
            index[n]["levels"] = dict(s.get("levels", {}))

    # Reference text (séif 1)
    simanim_ref = reference.get("simanim", {})
    for n, entry in index.items():
        ref = simanim_ref.get(str(n))
        if isinstance(ref, list) and ref:
            entry["seif1Raw"] = ref[0]
            entry["seifimCount"] = len(ref)
        else:
            entry["seifimCount"] = 0

    # Per-siman JSON (description, subtitle, sometimes better titles)
    for n in index:
        p = DATA / "simanim" / f"siman-{n}.json"
        if not p.exists():
            continue
        try:
            data = load_json(p)
        except Exception:
            continue
        if data.get("titleFr"):
            index[n]["titleFr"] = data["titleFr"]
        if data.get("titleHe"):
            index[n]["titleHe"] = data["titleHe"]
        # Per-siman JSON is authoritative for Hebrew numbering (the catalog has
        # historic glitches where some numHe values were left as decimals).
        if data.get("numberHe"):
            num_he_val = data["numberHe"].strip()
            looks_decimal = num_he_val.isdigit()
            if num_he_val and not looks_decimal:
                index[n]["numHe"] = num_he_val
            elif not index[n]["numHe"]:
                index[n]["numHe"] = num_he_val
        index[n]["description"] = data.get("description", "")
        index[n]["subtitle"] = data.get("subtitle", "")

    return index


# ---------------------------------------------------------------------------
# Hebrew text cleaning
# ---------------------------------------------------------------------------

# Strip Sefaria commentator anchor markers (<i data-commentator="...">...</i>)
RE_COMMENTATOR = re.compile(
    r'<i[^>]*data-commentator=[^>]*>.*?</i>', re.IGNORECASE | re.DOTALL
)
RE_OPEN_BOLD = re.compile(r'<b[^>]*>', re.IGNORECASE)
RE_CLOSE_BOLD = re.compile(r'</b>', re.IGNORECASE)
RE_OPEN_I = re.compile(r'<i[^>]*>', re.IGNORECASE)
RE_CLOSE_I = re.compile(r'</i>', re.IGNORECASE)
RE_BR = re.compile(r'<br\s*/?>', re.IGNORECASE)
RE_OPEN_SMALL = re.compile(r'<small[^>]*>', re.IGNORECASE)
RE_CLOSE_SMALL = re.compile(r'</small>', re.IGNORECASE)
RE_WHITESPACE = re.compile(r'[ \t]+')


def clean_hebrew(raw: str) -> tuple[str, str | None, str | None]:
    """Return (header, mehaber_text, rama_text) cleaned of HTML markup.

    The raw Sefaria entry follows this structure:
        <b>HEADER</b><br>... MEHABER text ...<small>הגה ... RAMA gloss ...</small>
    There can be multiple <small> blocks but for séif 1 we keep the first as Rama.
    """
    if not raw:
        return "", None, None

    text = raw.replace("\r", "")
    text = RE_COMMENTATOR.sub("", text)

    # Extract header from first <b>...</b>
    header = ""
    bopen = RE_OPEN_BOLD.search(text)
    bclose = RE_CLOSE_BOLD.search(text, bopen.end() if bopen else 0)
    if bopen and bclose:
        header = text[bopen.end():bclose.start()].strip()
        text = text[bclose.end():]
    # remove any further <b></b>
    text = RE_OPEN_BOLD.sub("", text)
    text = RE_CLOSE_BOLD.sub("", text)

    # Initial <br> after header
    text = RE_BR.sub("\n", text, count=10)

    # Extract first <small>...</small> as Rama gloss
    rama = None
    sopen = RE_OPEN_SMALL.search(text)
    if sopen:
        sclose = RE_CLOSE_SMALL.search(text, sopen.end())
        if sclose:
            rama = text[sopen.end():sclose.start()].strip()
            text = (text[:sopen.start()] + " " + text[sclose.end():]).strip()
    # Remove any remaining <small>...</small> blocks (merge content)
    text = RE_OPEN_SMALL.sub("", text)
    text = RE_CLOSE_SMALL.sub("", text)

    # Drop any leftover <i> tags
    text = RE_OPEN_I.sub("", text)
    text = RE_CLOSE_I.sub("", text)

    mehaber = normalize_ws(text)
    if rama:
        rama = normalize_ws(rama)
        # If the rama text starts with "הגה" (the standard Rama marker), keep it.
        if not rama.startswith("הגה"):
            rama = "הגה " + rama
    return header, mehaber or None, rama or None


def normalize_ws(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = RE_WHITESPACE.sub(" ", text)
    text = re.sub(r" *\n+ *", "\n", text)
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text.strip()


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

LEVEL_DEFINITIONS = [
    ("n1", "Niveau 1 — Base", "base",
     "Texte hébreu du Mehaber + traduction française fluide + explications pédagogiques."),
    ("n2", "Niveau 2 — Lamdan", "lamdan",
     "Pilpoul approfondi : Rishonim, Acharonim, hakirot, mahlokot, nafka minot pratiques."),
    ("n3", "Niveau 3 — Synthèse", "synthese",
     "Récapitulatif structuré pour révision : axiomes, arbres de décision, mnémoniques."),
    ("n4", "Niveau 4 — Daat HaRav", "daat-harav",
     "Chitah de l'Admour HaZaken (Choulhan Aroukh HaRav + Kountress Aharon) — psak Habad."),
]


def render_md(entry: dict[str, Any]) -> str:
    n = entry["num"]
    num_he = entry["numHe"] or ""
    title_fr = entry["titleFr"]
    title_he = entry["titleHe"]
    title_en = entry["titleEn"]
    description = entry.get("description", "")
    subtitle = entry.get("subtitle", "")
    seifim_count = entry.get("seifimCount", 0)
    levels = entry["levels"]

    header, mehaber, rama = clean_hebrew(entry.get("seif1Raw", ""))

    out: list[str] = []
    out.append(f"# Siman {n} — {title_fr}")
    out.append("")
    out.append(f"> Choulhan Aroukh, Orah Haïm, Hilkhot Shabbat — Siman {n} ({num_he})")
    out.append("")
    out.append(f"- **Français :** {title_fr}")
    if title_he:
        out.append(f"- **עברית :** {title_he}")
    if title_en:
        out.append(f"- **English :** {title_en}")
    out.append(f"- **Path canonique :** {BASE_URL}/oh/{n}/")
    out.append(f"- **Versions linguistiques :** "
               f"[FR]({BASE_URL}/oh/{n}/) · "
               f"[HE]({BASE_URL}/oh/{n}/he) · "
               f"[EN]({BASE_URL}/oh/{n}/en)")
    if seifim_count:
        out.append(f"- **Nombre de seifim (Mehaber + Rama) :** {seifim_count}")
    out.append("")

    if subtitle:
        out.append("## Présentation")
        out.append("")
        out.append(subtitle.strip())
        out.append("")
    elif description:
        out.append("## Présentation")
        out.append("")
        out.append(description.strip())
        out.append("")

    # Hebrew Mehaber séif 1
    if mehaber:
        out.append("## Texte du Mehaber — Séif 1 (hébreu)")
        out.append("")
        if header:
            out.append(f"**Titre du siman :** {header}")
            out.append("")
        out.append("> " + mehaber.replace("\n", "\n> "))
        out.append("")

    if rama:
        out.append("## Hagahot du Rama — Séif 1")
        out.append("")
        out.append("> " + rama.replace("\n", "\n> "))
        out.append("")

    # Bridge note for 304/322
    if n in BRIDGE_SIMANIM:
        out.append("## Note — Siman bridge (Niveau 4 absent)")
        out.append("")
        if n == 304:
            out.append(
                "Le Niveau 4 « Daat HaRav » n'existe pas pour ce siman : "
                "l'Admour HaZaken n'a pas développé ce sujet dans son "
                "Choulhan Aroukh HaRav (sujet devenu inapplicable historiquement). "
                "Une page « bridge » documente cette absence."
            )
        else:  # 322
            out.append(
                "Le Niveau 4 « Daat HaRav » n'existe pas pour ce siman : "
                "l'Admour HaZaken n'a pas traité ce sujet séparément dans son "
                "Choulhan Aroukh HaRav. Le contenu équivalent est intégré "
                "aux simanim 308 et 310 chez l'Admour HaZaken."
            )
        out.append("")

    # Levels
    out.append("## 4 niveaux d'étude")
    out.append("")
    for key, label, slug, desc in LEVEL_DEFINITIONS:
        present = bool(levels.get(key))
        if key == "n4" and n in BRIDGE_SIMANIM:
            out.append(f"- **{label}** : absent (siman bridge — voir note ci-dessus)")
            continue
        status = "" if present else " *(non disponible)*"
        out.append(f"- **{label}**{status} : {desc}")
        out.append(f"  - {BASE_URL}/oh/{n}/{slug}")
        out.append(f"  - HE : {BASE_URL}/oh/{n}/{slug}/he")
        out.append(f"  - EN : {BASE_URL}/oh/{n}/{slug}/en")
    out.append("")

    # Sefaria
    out.append("## Référence externe")
    out.append("")
    out.append(f"- **Sefaria — Shulchan Arukh, Orach Chayim {n} :** "
               f"{SEFARIA_BASE}.{n}")
    out.append("")

    out.append("---")
    out.append("")
    out.append("DAAT — daattorah.com · Auteur : Rav Yossef Haim Samama · "
               "Étude du Choulhan Aroukh en français · Édition 2026.")
    out.append(
        "Représentation Markdown générée automatiquement à des fins "
        "d'indexation par les moteurs et les LLM. La version HTML complète "
        f"se trouve à {BASE_URL}/oh/{n}/."
    )
    out.append("")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Génère les .md de chaque siman.")
    ap.add_argument("--siman", type=int, help="Un seul siman (ex: 248).")
    ap.add_argument("--check", action="store_true",
                    help="Génère mais n'écrit rien (dry-run).")
    args = ap.parse_args()

    index = build_index()

    if args.siman:
        targets = [args.siman]
    else:
        targets = sorted(index.keys())

    written = 0
    skipped = 0
    for n in targets:
        entry = index.get(n)
        if not entry:
            print(f"  ! Siman {n}: pas de données", file=sys.stderr)
            skipped += 1
            continue
        out_dir = SHABBAT / f"siman-{n}"
        if not out_dir.exists():
            print(f"  ! Siman {n}: dossier {out_dir} absent", file=sys.stderr)
            skipped += 1
            continue
        target = out_dir / "index.md"
        md = render_md(entry)
        if args.check:
            print(f"  - Siman {n}: {len(md)} chars (dry-run)")
        else:
            existing = target.read_text(encoding="utf-8") if target.exists() else None
            if existing == md:
                # idempotent: nothing to do
                pass
            else:
                target.write_text(md, encoding="utf-8")
        written += 1

    mode = "(dry-run)" if args.check else ""
    print(f"OK — {written} simanim traités, {skipped} ignorés {mode}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
