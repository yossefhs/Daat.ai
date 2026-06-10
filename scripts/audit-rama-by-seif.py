#!/usr/bin/env python3
"""Audit de la presence du Rama (הגה) seif par seif.

Contrairement a audit-rama-presence.py qui audite au niveau du siman entier,
ce script descend au niveau du SEIF : pour chaque seif d'un niveau-1-base.html,
il verifie si l'hagaha du Rama y est presente (blockquote dedie, class "rama",
mention en prose), et croise avec ce que le niveau-2-lamdan affirme
("seif X hagah", "hagah du Rama sur seif Y"...).

Verdicts par seif :
  - OK              : au moins un block hagaa ou class rama
  - SUSPECT-LAMDAN  : Lamdan dit qu'il y a une hagah ici, Base est silencieux
  - SUSPECT-PROSE   : mention "Rama" en prose mais aucun block dedie
  - LIKELY-MISSING  : silence total (Base + Lamdan) - peut-etre OK
  - NEUTRAL         : cas non couvert

Usage :
  python3 scripts/audit-rama-by-seif.py
  python3 scripts/audit-rama-by-seif.py --detail 248
  python3 scripts/audit-rama-by-seif.py --csv
  python3 scripts/audit-rama-by-seif.py --lang fr|he|en

NB : audit en lecture seule. Aucun HTML n'est modifie.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHABBAT = ROOT / "sources" / "shabbat"

# -------------------------------------------------------------------------
# Noms des seifim (translitteration <-> chiffre <-> lettre hebraique)
# -------------------------------------------------------------------------
SEIF_NAMES_FR = [
    "Alef", "Beit", "Beis", "Guimel", "Gimel", "Daled", "Dalet",
    "Heh", "He", "Vav", "Zayin", "Zain", "Het", "Heth", "Chet",
    "Tet", "Yod", "Youd",
    # composes 11-19 : Yod-Alef, Yod-Beit, ...
]

# nombre par nom FR (sans tirets) -> int
NAME_TO_NUM_FR = {
    "alef": 1, "beit": 2, "beis": 2,
    "guimel": 3, "gimel": 3,
    "daled": 4, "dalet": 4,
    "heh": 5, "he": 5,
    "vav": 6,
    "zayin": 7, "zain": 7,
    "het": 8, "heth": 8, "chet": 8,
    "tet": 9,
    "yod": 10, "youd": 10,
}

# lettres hebraiques 1..10
HEB_NUM = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5,
    "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10,
}
# lettres composees 11..19 : י + א/ב/...
# (on gere via post-traitement)

NUM_TO_FR = {
    1: "Alef", 2: "Beit", 3: "Guimel", 4: "Daled",
    5: "Heh", 6: "Vav", 7: "Zayin", 8: "Het",
    9: "Tet", 10: "Yod",
    11: "Yod-Alef", 12: "Yod-Beit", 13: "Yod-Guimel",
    14: "Yod-Daled", 15: "Tet-Vav", 16: "Tet-Zayin",
    17: "Yod-Zayin", 18: "Yod-Het", 19: "Yod-Tet",
    20: "Khaf",
}

# -------------------------------------------------------------------------
# Regex
# -------------------------------------------------------------------------

# Marqueurs hagaa dans le texte hebreu :
#  - הגה  (la forme courte, peut etre suivie d'un signe de ponctuation)
#  - הג"ה / הג״ה
#  - הגהה / הַגָּהּ
# On reste plus strict que audit-rama-presence : on veut que le marqueur soit
# visiblement balise (donc dans un block) ou clairement utilise comme libelle.
RE_HAGAA_MARKER = re.compile(
    r'הַגָּ?הּ|הַגָּהָה|הגה(?=[<\s:,.\-ְ-ׇ׃])|הג["״]ה'
)

# Mentions du Rama (en hebreu) : "Rama", "ha-Rama"
RE_RAMA_HE = re.compile(r'הרמ["״]א|רמ["״]א')

# Mentions "Rama" en prose (FR / EN)
RE_RAMA_FR = re.compile(r'\bRama\b', re.IGNORECASE)
RE_RAMA_EN = re.compile(r'\bRema\b', re.IGNORECASE)

# Patterns pour decouper en seifim - h3 ou h2 contenant "Seif X" / "סעיף X"
# On capture le nom du seif. On va segmenter sur les <h3> ou <h2> de meme
# niveau, plus les <div class="seif-block" id="...">.

# Regex pour decouper le texte en sections seif :
# variantes acceptees :
#   <h3 ...>Seif Alef ...</h3>
#   <h3 ...>Séif א ...</h3>
#   <h3 ...>סעיף א'/ב'...</h3>
#   <h2 ... id="seif-N">...
#   <div class="seif-block" id="...seif-N">
RE_SEIF_HEADING_FR = re.compile(
    r'<h[2-4][^>]*>\s*(?:Section\s+\d+\s*[-—:]\s*)?'
    r'(?:Le\s+)?[Ss][ée]if\s+([A-Za-z][A-Za-z\-]*|[א-ת][א-ת\'׳]*)'
    r'\b[^<]*</h[2-4]>',
)
RE_SEIF_HEADING_HE = re.compile(
    r'<h[2-4][^>]*>\s*(?:\d+\.\s*)?'
    r'(?:ה?)?סעיף\s*([א-ת]+)\s*[\'׳]?[^<]*</h[2-4]>',
)
# Fallback : <div class="seif-block" id="etude-seif-N"> ou similaire
RE_SEIF_BLOCK_ID = re.compile(
    r'<div[^>]*class="[^"]*seif-block[^"]*"[^>]*id="[^"]*seif-(\d+)[^"]*"',
)
# Marquage par id sur h2/h3 : id="seif-N"
RE_SEIF_H_ID = re.compile(
    r'<h[2-4][^>]*id="seif-(\d+)"[^>]*>',
)


def normalize_seif_name(raw: str) -> int | None:
    """Convertit un nom de seif (Alef/Beit/.../א/ב/...) en numero 1..n."""
    if not raw:
        return None
    raw = raw.strip().strip("'׳״”“")  # apostrophes
    # cas hebreu
    if raw and raw[0] in HEB_NUM:
        if len(raw) == 1:
            return HEB_NUM[raw]
        # composes : "י" + "א"/"ב"/... = 11+
        if raw[0] == "י" and len(raw) == 2 and raw[1] in HEB_NUM:
            return 10 + HEB_NUM[raw[1]]
        # "כ" pour 20 etc. (rare ici)
        return HEB_NUM.get(raw[0])
    # cas FR
    key = raw.lower().replace("-", "").replace("é", "e").replace("è", "e")
    # composes type "yodalef" / "yod-alef"
    if key.startswith("yod") and len(key) > 3:
        rest = key[3:]
        if rest in NAME_TO_NUM_FR:
            return 10 + NAME_TO_NUM_FR[rest]
    if key.startswith("tet") and len(key) > 3:
        rest = key[3:]
        if rest == "vav":
            return 15
        if rest == "zayin":
            return 16
    return NAME_TO_NUM_FR.get(key)


# -------------------------------------------------------------------------
# Decoupage HTML en seifim
# -------------------------------------------------------------------------

@dataclass
class SeifSection:
    num: int           # 1..n
    name: str          # libelle d'origine (Alef, ב', ...)
    text: str          # contenu HTML de la section


def split_into_seifim(html: str, lang: str) -> list[SeifSection]:
    """Trouve les sections seif et retourne une liste ordonnee.

    Strategie en deux passes :
      1. cherche tous les <h2|h3> "Seif X" / "סעיף X" et utilise leurs
         positions pour decouper.
      2. fallback : <div class="seif-block" id="etude-seif-N">.

    Pour ne pas confondre une mention en prose dans un <h3> de cas pratique
    ("Practical cases of Seif Alef"), on filtre les en-tetes contenant des
    mots-cle de cas/synthese.
    """
    # 1) headings "Seif X" / "סעיף X"
    candidates: list[tuple[int, int, str]] = []
    # offset, seif_num, raw_name

    # Skip si l'en-tete contient des mots indiquant un sous-titre
    SKIP_TOKENS = re.compile(
        r'(?:Practical|cases|Cas pratiques|Pesak|Synth[èe]se|Question|conditions|'
        r'מקרים|פסיקה|סיכום|שאלה|practical|cases\.)',
        re.IGNORECASE,
    )

    for m in RE_SEIF_HEADING_FR.finditer(html):
        heading = html[m.start():m.end()]
        if SKIP_TOKENS.search(heading):
            continue
        n = normalize_seif_name(m.group(1))
        if n is not None:
            candidates.append((m.start(), n, m.group(1)))

    for m in RE_SEIF_HEADING_HE.finditer(html):
        heading = html[m.start():m.end()]
        if SKIP_TOKENS.search(heading):
            continue
        n = normalize_seif_name(m.group(1))
        if n is not None:
            candidates.append((m.start(), n, m.group(1)))

    # 2) Fallback / complement : marqueurs id="...seif-N" sur des <div>
    for m in RE_SEIF_BLOCK_ID.finditer(html):
        n = int(m.group(1))
        candidates.append((m.start(), n, str(n)))
    for m in RE_SEIF_H_ID.finditer(html):
        n = int(m.group(1))
        candidates.append((m.start(), n, str(n)))

    if not candidates:
        return []

    # Tri par offset
    candidates.sort(key=lambda t: t[0])

    # Deduplication : un seif numero peut apparaitre plusieurs fois
    # (en-tete, etude detaillee, cas pratiques). On veut garder pour chaque
    # seif l'OFFSET LE PLUS PRECOCE (qui inclura les blockquotes de la
    # citation initiale) jusqu'a l'offset du seif SUIVANT.
    seen: dict[int, tuple[int, str]] = {}
    for off, n, raw in candidates:
        if n not in seen or off < seen[n][0]:
            seen[n] = (off, raw)

    ordered = sorted(seen.items(), key=lambda kv: kv[1][0])
    # Construire les sections : chaque section va de son offset au offset du
    # suivant.
    sections: list[SeifSection] = []
    for i, (n, (off, raw)) in enumerate(ordered):
        end = ordered[i + 1][1][0] if i + 1 < len(ordered) else len(html)
        sections.append(SeifSection(num=n, name=raw, text=html[off:end]))
    # tri final par num croissant (au cas ou)
    sections.sort(key=lambda s: s.num)
    return sections


# -------------------------------------------------------------------------
# Analyse d'un seif
# -------------------------------------------------------------------------

@dataclass
class SeifMetrics:
    num: int
    name: str
    blocks_hagaa: int = 0
    blocks_rama_class: int = 0
    prose_rama: int = 0
    total_blocks: int = 0
    text_length: int = 0

    @property
    def verdict(self) -> str:
        if self.blocks_hagaa >= 1 or self.blocks_rama_class >= 1:
            return "OK"
        # le verdict SUSPECT-LAMDAN est applique apres cross-reference
        if self.prose_rama >= 1:
            return "SUSPECT-PROSE"
        return "LIKELY-MISSING"


def strip_tags(html: str) -> str:
    """Supprime les balises HTML pour obtenir un texte brut."""
    return re.sub(r"<[^>]+>", " ", html)


def extract_blockquotes(text: str) -> list[str]:
    """Extrait le contenu des blockquotes (avec ou sans class)."""
    return re.findall(r"<blockquote[^>]*>(.*?)</blockquote>", text, re.DOTALL)


def extract_rama_class_elements(text: str) -> list[str]:
    """Extrait les elements dont la class contient 'rama'."""
    # cherche <X class="...rama...">...</X> sur 1+ lignes
    out: list[str] = []
    for m in re.finditer(
        r'<(\w+)[^>]*class="[^"]*\brama[\w\-]*\b[^"]*"[^>]*>',
        text,
    ):
        out.append(m.group(0))
    return out


def measure_seif(seif: SeifSection, lang: str) -> SeifMetrics:
    text = seif.text
    blocks = extract_blockquotes(text)
    blocks_hagaa = sum(1 for b in blocks if RE_HAGAA_MARKER.search(b))
    rama_class_els = extract_rama_class_elements(text)

    # prose = texte hors blockquotes
    prose = re.sub(
        r"<blockquote[^>]*>.*?</blockquote>", " ", text, flags=re.DOTALL
    )
    # supprime aussi le <h3> de la section "Hagaha du Rama" qui mentionne Rama
    # mais ne compte pas comme prose halakhique
    prose_text = strip_tags(prose)

    if lang == "fr":
        prose_rama = len(RE_RAMA_FR.findall(prose_text))
    elif lang == "en":
        prose_rama = len(RE_RAMA_EN.findall(prose_text))
    else:
        prose_rama = len(RE_RAMA_HE.findall(prose_text))

    return SeifMetrics(
        num=seif.num,
        name=seif.name,
        blocks_hagaa=blocks_hagaa,
        blocks_rama_class=len(rama_class_els),
        prose_rama=prose_rama,
        total_blocks=len(blocks),
        text_length=len(text),
    )


# -------------------------------------------------------------------------
# Analyse du niveau-2-lamdan : quels seifim sont annonces comme hagah ?
# -------------------------------------------------------------------------

# Patterns hebrais : on cherche un contexte ou "seif X" et "hagah/Rama"
# apparaissent dans une fenetre commune.
RE_LAMDAN_SEIF_THEN_HAGAA = re.compile(
    r"סעיף\s*([א-ת]+)\s*[\'׳]?[^.<\n]{0,120}?(?:הגה|רמ[\"״]א)",
)
RE_LAMDAN_HAGAA_THEN_SEIF = re.compile(
    r"(?:הגה(?:ת|ה)?|הרמ[\"״]א|רמ[\"״]א)[^.<\n]{0,120}?סעיף\s*([א-ת]+)",
)
# pattern explicite "seif X hagah" (forme directe utilisee dans 248 : "סעיף א הגה")
RE_LAMDAN_SEIF_HAGAA_DIRECT = re.compile(
    r"סעיף\s*([א-ת]+)\s*[\'׳]?\s*הגה",
)


def find_lamdan_hagaa_on_seifim(html: str) -> set[int]:
    """Renvoie l'ensemble des numeros de seif explicitement signales comme
    portant une hagah du Rama selon le niveau-2-lamdan.
    """
    seifim: set[int] = set()
    text = strip_tags(html)
    for rx in (
        RE_LAMDAN_SEIF_HAGAA_DIRECT,
        RE_LAMDAN_SEIF_THEN_HAGAA,
        RE_LAMDAN_HAGAA_THEN_SEIF,
    ):
        for m in rx.finditer(text):
            n = normalize_seif_name(m.group(1))
            if n is not None and 1 <= n <= 30:
                seifim.add(n)
    return seifim


# -------------------------------------------------------------------------
# Cross-reference et verdict final
# -------------------------------------------------------------------------

VERDICT_ICON = {
    "OK": "[v] OK              ",
    "SUSPECT-LAMDAN": "[!] SUSPECT-LAMDAN  ",
    "SUSPECT-PROSE": "[~] SUSPECT-PROSE   ",
    "SUSPECT-CONTEXT": "[*] SUSPECT-CONTEXT ",
    "LIKELY-MISSING": "[?] LIKELY-MISSING  ",
    "NEUTRAL": "[ ] NEUTRAL         ",
}
VERDICT_SEVERITY = {
    "SUSPECT-LAMDAN": 3,
    "SUSPECT-PROSE": 2,
    "SUSPECT-CONTEXT": 2,
    "LIKELY-MISSING": 1,
    "OK": 0,
    "NEUTRAL": 0,
}


def cross_reference(
    metrics: SeifMetrics,
    lamdan_hagaa_set: set[int],
    siman_has_rama_elsewhere: bool,
) -> str:
    if metrics.blocks_hagaa >= 1 or metrics.blocks_rama_class >= 1:
        return "OK"
    # silence des blocs
    if metrics.num in lamdan_hagaa_set and metrics.prose_rama == 0:
        return "SUSPECT-LAMDAN"
    if metrics.num in lamdan_hagaa_set and metrics.prose_rama >= 1:
        # Le Lamdan signale + le Base en parle en prose mais sans block
        # = on prefere SUSPECT-LAMDAN (plus grave : pas de citation visuelle)
        return "SUSPECT-LAMDAN"
    if metrics.prose_rama >= 1:
        return "SUSPECT-PROSE"
    # Heuristique contextuelle : siman "rama-rich" mais ce seif est muet.
    # Le silence dans un environnement bavard sur le Rama merite enquete.
    if siman_has_rama_elsewhere:
        return "SUSPECT-CONTEXT"
    return "LIKELY-MISSING"


# -------------------------------------------------------------------------
# Iteration sur les simanim
# -------------------------------------------------------------------------

def iter_simanim() -> list[int]:
    nums: list[int] = []
    for p in SHABBAT.iterdir():
        m = re.match(r"^siman-(\d+)$", p.name)
        if m:
            nums.append(int(m.group(1)))
    return sorted(nums)


def file_for_lang(folder: Path, base: str, lang: str) -> Path:
    if lang == "fr":
        return folder / f"{base}.html"
    return folder / f"{base}-{lang}.html"


@dataclass
class SimanReport:
    num: int
    seifim: list[tuple[SeifMetrics, str]] = field(default_factory=list)
    lamdan_set: set[int] = field(default_factory=set)
    skipped_reason: str | None = None

    def suspect_seifim(self) -> list[tuple[SeifMetrics, str]]:
        return [
            (m, v) for (m, v) in self.seifim
            if v in ("SUSPECT-LAMDAN", "SUSPECT-PROSE", "SUSPECT-CONTEXT")
        ]

    def severity(self) -> int:
        # cumul du nombre de seifim suspects, ponderes
        s = 0
        for _, v in self.seifim:
            s += VERDICT_SEVERITY.get(v, 0)
        return s


def audit_siman(num: int, lang: str) -> SimanReport:
    rep = SimanReport(num=num)
    folder = SHABBAT / f"siman-{num}"
    base = file_for_lang(folder, "niveau-1-base", lang)
    lamdan = folder / "niveau-2-lamdan-he.html"

    if not base.exists():
        rep.skipped_reason = f"missing {base.name}"
        return rep

    html = base.read_text(encoding="utf-8")
    sections = split_into_seifim(html, lang)
    if not sections:
        rep.skipped_reason = "no seif sections detected"
        return rep

    if lamdan.exists():
        lamdan_html = lamdan.read_text(encoding="utf-8")
        rep.lamdan_set = find_lamdan_hagaa_on_seifim(lamdan_html)

    # Pre-mesure : on a besoin de savoir si le siman est globalement
    # "rama-rich" (au moins un seif avec un block hagaa). Si oui, un seif
    # silencieux devient SUSPECT-CONTEXT.
    metrics_list = [measure_seif(sec, lang) for sec in sections]
    siman_has_rama_elsewhere = any(
        m.blocks_hagaa >= 1 or m.blocks_rama_class >= 1 for m in metrics_list
    )
    # Si le Lamdan signale au moins un seif comme ayant une hagah, on
    # considere aussi le siman comme "rama-rich".
    if rep.lamdan_set:
        siman_has_rama_elsewhere = True

    for m in metrics_list:
        v = cross_reference(m, rep.lamdan_set, siman_has_rama_elsewhere)
        rep.seifim.append((m, v))
    return rep


# -------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------

def cmd_summary(lang: str) -> None:
    reports = [audit_siman(n, lang) for n in iter_simanim()]
    total_seifim = 0
    counts = {"OK": 0, "SUSPECT-LAMDAN": 0, "SUSPECT-PROSE": 0,
              "SUSPECT-CONTEXT": 0, "LIKELY-MISSING": 0, "NEUTRAL": 0}
    skipped = 0
    for r in reports:
        if r.skipped_reason:
            skipped += 1
            continue
        for _, v in r.seifim:
            counts[v] = counts.get(v, 0) + 1
            total_seifim += 1

    print("=== Audit Rama par seif - daattorah.com ===\n")
    print(f"Langue auditee      : {lang.upper()}")
    print(f"Simanim audites     : {len(reports) - skipped} / {len(reports)}")
    if skipped:
        print(f"Simanim skipped     : {skipped} (fichier manquant / pas de seif detecte)")
    print(f"Seifim audites      : {total_seifim}")
    print("Verdicts par seif   :")
    print(f"  [v] OK              : {counts['OK']}")
    print(f"  [!] SUSPECT-LAMDAN  : {counts['SUSPECT-LAMDAN']:>3}  "
          "(Lamdan dit qu'il y a une hagah, Base ne l'a pas)")
    print(f"  [~] SUSPECT-PROSE   : {counts['SUSPECT-PROSE']:>3}  "
          "(mention en prose, pas de block visuel)")
    print(f"  [*] SUSPECT-CONTEXT : {counts['SUSPECT-CONTEXT']:>3}  "
          "(siman rama-rich, mais ce seif est muet)")
    print(f"  [?] LIKELY-MISSING  : {counts['LIKELY-MISSING']:>3}  "
          "(silence total - probablement pas de hagah)")

    # Top 20 simanim suspects
    ranked = [r for r in reports if r.suspect_seifim()]
    ranked.sort(
        key=lambda r: (-r.severity(), -len(r.suspect_seifim()), r.num),
    )
    print("\n=== Top 20 simanim suspects ===")
    print(f"{'Siman':6}  {'Sev':>3}  Seifim suspects")
    print("-" * 90)
    for r in ranked[:20]:
        label = ", ".join(
            f"{NUM_TO_FR.get(m.num, str(m.num))} ({short_verdict(v)})"
            for m, v in r.suspect_seifim()
        )
        print(f"{r.num:<6}  {r.severity():>3}  {label}")
    if not ranked:
        print("(aucun siman suspect dans cette langue)")


def short_verdict(v: str) -> str:
    return {
        "SUSPECT-LAMDAN": "[!] lamdan",
        "SUSPECT-PROSE": "[~] prose",
        "SUSPECT-CONTEXT": "[*] context",
        "LIKELY-MISSING": "[?] missing",
    }.get(v, v)


def cmd_detail(num: int, lang: str) -> None:
    rep = audit_siman(num, lang)
    if rep.skipped_reason:
        print(f"Siman {num} skipped : {rep.skipped_reason}")
        return
    print(f"=== Siman {num} - Niveau 1 Base ({lang.upper()}) ===")
    if rep.lamdan_set:
        ordered = sorted(rep.lamdan_set)
        named = ", ".join(NUM_TO_FR.get(n, str(n)) for n in ordered)
        print(f"Lamdan signale hagah sur seif(im) : {named}")
    else:
        print("Lamdan signale hagah sur seif(im) : (aucun seif identifie)")
    print()
    print(f"{'Seif':14}  {'Verdict':22}  Details")
    print("-" * 90)
    for m, v in rep.seifim:
        name = NUM_TO_FR.get(m.num, m.name)
        details = (
            f"({m.blocks_hagaa} block hagaa, "
            f"{m.blocks_rama_class} class=rama, "
            f"{m.prose_rama} mention(s) prose, "
            f"{m.total_blocks} blocks total)"
        )
        print(f"{'Seif ' + name:14}  {VERDICT_ICON[v]:22}  {details}")


def cmd_csv(lang: str) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow([
        "siman", "seif_num", "seif_name", "verdict",
        "blocks_hagaa", "blocks_rama_class", "prose_rama",
        "total_blocks", "text_length", "in_lamdan_hagaa_set",
    ])
    for n in iter_simanim():
        rep = audit_siman(n, lang)
        if rep.skipped_reason:
            continue
        for m, v in rep.seifim:
            writer.writerow([
                n, m.num, NUM_TO_FR.get(m.num, m.name), v,
                m.blocks_hagaa, m.blocks_rama_class, m.prose_rama,
                m.total_blocks, m.text_length,
                "1" if m.num in rep.lamdan_set else "0",
            ])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--detail", type=int, default=None,
        help="affiche le detail d'un siman donne (ex : --detail 248)",
    )
    p.add_argument(
        "--lang", choices=["fr", "he", "en"], default="fr",
        help="langue a auditer (defaut : fr)",
    )
    p.add_argument(
        "--csv", action="store_true",
        help="sortie CSV (tous les seifim de tous les simanim)",
    )
    args = p.parse_args()

    if args.csv:
        cmd_csv(args.lang)
        return
    if args.detail is not None:
        cmd_detail(args.detail, args.lang)
        return
    cmd_summary(args.lang)


if __name__ == "__main__":
    main()
