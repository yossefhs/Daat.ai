# -*- coding: utf-8 -*-
"""Moteur de reconnaissance des références de Torah (§7).

Reconnaît les formes françaises, hébraïques et translittérées :

    Choul'han Aroukh OH 268:3        או״ח רס״ח:ג
    Michna Beroura 268 s.k. 12       מ״ב רס״ח ס״ק י״ב
    Berakhot 34a                     ברכות ל״ד ע״א        שבת קי״ז:
    Admour Hazaken 268:14            שו״ע הרב רס״ח:יד     SAR 268:14
    Rambam, Hilkhot Shabbat 24:5

Deux garde-fous appris du gate ``scripts/verifier-citations.py`` du dépôt :

1. **Validation des numéraux hébreux.** Un numéral s'écrit par valeurs
   décroissantes (ק־י־ז). Sans ce contrôle, « ספק ברכות להקל » se lit
   « Berakhot » + gematria(להקל) = 165, et l'on part chercher un folio 165
   dans un traité qui en compte 64.
2. **Confiance graduée** plutôt que binaire : une référence sans séif est
   moins sûre qu'une référence complète, et le champ ``confidence`` le dit.
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field

_DATA = pathlib.Path(__file__).parent / "data" / "works_aliases.json"

# ── Gematria ─────────────────────────────────────────────────────────────
GEMATRIA = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90, "ק": 100, "ר": 200,
    "ש": 300, "ת": 400,
}


def gematria(token: str) -> int | None:
    """Valeur d'un numéral hébreu, ou ``None`` si ce n'en est pas un.

    Contrôle de forme indispensable (voir docstring du module) : les valeurs
    doivent être non croissantes, avec l'exception conventionnelle ט״ו / ט״ז.
    """
    token = re.sub(r"[\"'״׳]", "", token).strip()
    if not token or len(token) > 4 or any(c not in GEMATRIA for c in token):
        return None
    values = [GEMATRIA[c] for c in token]
    if values in ([10, 6], [10, 7]):        # ט״ו = 15, ט״ז = 16
        return sum(values)
    if any(a < b for a, b in zip(values, values[1:])):
        return None
    return sum(values)


def _num(token: str) -> int | None:
    token = token.strip()
    if token.isdigit():
        return int(token)
    return gematria(token)


# ── Table d'alias ────────────────────────────────────────────────────────
def load_aliases(path: pathlib.Path | None = None) -> dict[str, str]:
    """{alias en minuscules → nom canonique}. Le plus long alias d'abord."""
    raw = json.loads((path or _DATA).read_text(encoding="utf-8"))
    table: dict[str, str] = {}
    for canonical, aliases in raw.items():
        if canonical.startswith("_"):
            continue
        table[canonical.lower()] = canonical
        for alias in aliases:
            table[alias.lower()] = canonical
    return table


ALIASES = load_aliases()
# Alternance triée par longueur décroissante : « Choulhan Aroukh HaRav » doit
# l'emporter sur « Choulhan Aroukh », qui en est un préfixe.
_ALIAS_PATTERN = "|".join(
    re.escape(a) for a in sorted(ALIASES, key=len, reverse=True) if len(a) >= 2
)

# Traités talmudiques (nom → nom canonique Sefaria), pour daf + amoud.
TRACTATES = {
    "שבת": "Shabbat", "ברכות": "Berakhot", "פסחים": "Pesachim", "עירובין": "Eruvin",
    "ביצה": "Beitzah", "מנחות": "Menachot", "חולין": "Chullin", "יבמות": "Yevamot",
    "נדה": "Niddah", "סוכה": "Sukkah", "מגילה": "Megillah", "תענית": "Taanit",
    "יומא": "Yoma", "סנהדרין": "Sanhedrin", "כתובות": "Ketubot", "גיטין": "Gittin",
    "קידושין": "Kiddushin", "מועד קטן": "Moed Katan", "בבא בתרא": "Bava Batra",
    "בבא קמא": "Bava Kamma", "בבא מציעא": "Bava Metzia", "נדרים": "Nedarim",
    "shabbat": "Shabbat", "chabbat": "Shabbat", "berakhot": "Berakhot",
    "berachot": "Berakhot", "pesachim": "Pesachim", "pessahim": "Pesachim",
    "menachot": "Menachot", "menahot": "Menachot", "houlin": "Chullin",
    "beitsa": "Beitzah", "beitzah": "Beitzah", "erouvin": "Eruvin",
    "yevamot": "Yevamot", "megillah": "Megillah", "meguila": "Megillah",
    "soucca": "Sukkah", "sukkah": "Sukkah", "kiddouchin": "Kiddushin",
}
_TRACTATE_PATTERN = "|".join(
    re.escape(t) for t in sorted(TRACTATES, key=len, reverse=True)
)

_HE_NUM = r"[א-ת]{1,4}[\"'״׳]?[א-ת]?"
_NUM = rf"(?:\d{{1,3}}|{_HE_NUM})"

# Daf + amoud : « ברכות ל״ד ע״א », « שבת קי״ז: », « Berakhot 34a »
RE_DAF = re.compile(
    rf"(?P<work>{_TRACTATE_PATTERN})\s*\(?\s*(?P<daf>{_NUM})\s*"
    rf"(?:(?P<amud_he>ע[\"'״׳]?[אב])|(?P<amud_lat>[ab])\b|(?P<colon>[.:]))",
    re.IGNORECASE,
)
# Forme **canonique du site** : « שולחן ערוך · אורח חיים · סימן רמ״ד · סעיף א ».
# C'est ainsi que les pages étiquettent le texte du Mehaber, et c'est la
# référence la plus autoritative qu'elles portent. La forme abrégée « X:Y » que
# reconnaît RE_SIMAN_SEIF n'y figure jamais : un premier audit du périmètre l'a
# montré sans appel — 213 citations extraites, 4 seulement rattachées, faute de
# savoir lire cet en-tête.
#
# « סעיף » au singulier est exigé : « סימן רמ״ט · 4 סעיפים » annonce un NOMBRE
# de séifim, pas un séif — le lire comme une référence serait un contresens.
RE_SIMAN_SEIF_LABEL = re.compile(
    rf"(?:(?P<work>שולחן ערוך|שו[\"'״׳]ע)\s*[·|,\-–—]?\s*)?"
    rf"(?:(?P<section>אורח חיים|או[\"'״׳]ח|יורה דעה|יו[\"'״׳]ד)\s*[·|,\-–—]?\s*)?"
    rf"סימן\s*(?P<siman>{_NUM})"
    rf"\s*[·|,\-–—]?\s*סעיף\s*(?P<seif>{_NUM})"
)

_SECTION_HE = {
    "אורח חיים": "Orach Chayim", "או״ח": "Orach Chayim", 'או"ח': "Orach Chayim",
    "יורה דעה": "Yoreh Deah", "יו״ד": "Yoreh Deah", 'יו"ד': "Yoreh Deah",
}

# Séif katan : « ס״ק י״ב », « s.k. 12 »
RE_SEIF_KATAN = re.compile(rf"(?:ס[\"'״׳]?ק|s\.?k\.?)\s*(?P<sk>{_NUM})", re.IGNORECASE)

# Ouvrages désignés par un sigle court, non couverts par la table d'alias.
# Les sigles de *section* (או״ח, יו״ד…) désignent le Choulhan Aroukh : ce sont
# les quatre parties de l'ouvrage, pas des ouvrages distincts. Chaque forme est
# donnée avec ses deux gershayim (״ typographique et " droit), les deux ayant
# cours dans les sources.
_SHORT = {
    "oh": "Choulhan Aroukh", "oc": "Choulhan Aroukh", "yd": "Choulhan Aroukh",
    "sar": "Choulhan Aroukh HaRav", "sah": "Choulhan Aroukh HaRav",
    "mb": "Michna Beroura",
    "או״ח": "Choulhan Aroukh", 'או"ח': "Choulhan Aroukh",
    "יו״ד": "Choulhan Aroukh", 'יו"ד': "Choulhan Aroukh",
    "אה״ע": "Choulhan Aroukh", 'אה"ע': "Choulhan Aroukh",
    "חו״מ": "Choulhan Aroukh", 'חו"מ': "Choulhan Aroukh",
}
_SECTION_OF_SHORT = {
    "oh": "Orach Chayim", "oc": "Orach Chayim", "yd": "Yoreh Deah",
    "או״ח": "Orach Chayim", 'או"ח': "Orach Chayim",
    "יו״ד": "Yoreh Deah", 'יו"ד': "Yoreh Deah",
    "אה״ע": "Even HaEzer", 'אה"ע': "Even HaEzer",
    "חו״מ": "Choshen Mishpat", 'חו"מ': "Choshen Mishpat",
}
# Alternance construite depuis la table : ajouter un sigle ci-dessus suffit.
_SHORT_PATTERN = "|".join(
    re.escape(s) for s in sorted(_SHORT, key=len, reverse=True)
)

# Ouvrage + siman:séif — « OH 268:3 », « או״ח רס״ח:ג », « SAR 268:14 »
RE_SIMAN_SEIF = re.compile(
    rf"(?P<work>{_SHORT_PATTERN}|{_ALIAS_PATTERN})\s*"
    rf"(?P<siman>{_NUM})\s*[:׃]\s*(?P<seif>{_NUM})",
    re.IGNORECASE,
)


@dataclass
class ParsedRef:
    raw_text: str
    work: str | None = None
    section: str | None = None
    siman: str | None = None
    seif: str | None = None
    seif_katan: str | None = None
    daf: str | None = None
    amud: str | None = None
    confidence: float = 0.0
    span: tuple[int, int] = (0, 0)
    notes: list[str] = field(default_factory=list)

    def sefaria_ref(self) -> str | None:
        """Référence Sefaria canonique, quand elle est déductible."""
        if self.daf and self.work in TRACTATES.values():
            return f"{self.work.replace(' ', '_')}.{self.daf}{self.amud or 'a'}"
        if self.work == "Choulhan Aroukh" and self.siman and self.seif:
            section = (self.section or "Orach Chayim").replace(" ", "_")
            return f"Shulchan_Arukh,_{section}.{self.siman}.{self.seif}"
        if self.work == "Choulhan Aroukh HaRav" and self.siman and self.seif:
            return f"Shulchan_Arukh_HaRav,_Orach_Chayim.{self.siman}.{self.seif}"
        if self.work == "Michna Beroura" and self.siman and self.seif_katan:
            return f"Mishnah_Berurah.{self.siman}.{self.seif_katan}"
        return None


def _canonical_work(token: str) -> tuple[str | None, str | None]:
    """(ouvrage canonique, section) à partir d'un jeton reconnu."""
    low = token.lower().strip()
    if low in _SHORT:
        return _SHORT[low], _SECTION_OF_SHORT.get(low)
    return ALIASES.get(low), None


def extract_references(text: str) -> list[ParsedRef]:
    """Toutes les références détectées dans un texte, sans doublon de span."""
    refs: list[ParsedRef] = []

    for m in RE_DAF.finditer(text):
        daf = _num(m.group("daf"))
        if daf is None or not (1 <= daf <= 180):
            continue      # numéral invalide ou folio impossible : on s'abstient
        tractate = TRACTATES[m.group("work").lower()] if m.group("work").lower() in TRACTATES \
            else TRACTATES.get(m.group("work"))
        if not tractate:
            continue
        if m.group("amud_he"):
            amud = "a" if m.group("amud_he").endswith("א") else "b"
        elif m.group("amud_lat"):
            amud = m.group("amud_lat").lower()
        else:
            amud = "a" if m.group("colon") == "." else "b"
        refs.append(ParsedRef(
            raw_text=m.group(0), work=tractate, daf=str(daf), amud=amud,
            confidence=0.9, span=m.span(),
        ))

    for m in RE_SIMAN_SEIF.finditer(text):
        work, section = _canonical_work(m.group("work"))
        siman, seif = _num(m.group("siman")), _num(m.group("seif"))
        if not work or siman is None or seif is None:
            continue
        # Un ס״ק dans les 40 caractères suivants appartient à cette référence.
        tail = text[m.end(): m.end() + 40]
        sk_match = RE_SEIF_KATAN.search(tail)
        seif_katan = _num(sk_match.group("sk")) if sk_match else None
        refs.append(ParsedRef(
            raw_text=m.group(0), work=work, section=section,
            siman=str(siman), seif=str(seif),
            seif_katan=str(seif_katan) if seif_katan is not None else None,
            confidence=0.85, span=m.span(),
        ))

    for m in RE_SIMAN_SEIF_LABEL.finditer(text):
        siman, seif = _num(m.group("siman")), _num(m.group("seif"))
        if siman is None or seif is None:
            continue
        section = _SECTION_HE.get((m.group("section") or "").strip())
        refs.append(ParsedRef(
            raw_text=m.group(0), work="Choulhan Aroukh",
            section=section or "Orach Chayim",
            siman=str(siman), seif=str(seif),
            # Forme explicite et étiquetée : plus sûre que l'abrégé « X:Y ».
            confidence=0.92, span=m.span(),
        ))

    # Michna Beroura « 268:12 » = siman:séif katan, pas siman:séif.
    for ref in refs:
        if ref.work == "Michna Beroura" and ref.seif and not ref.seif_katan:
            ref.seif_katan, ref.seif = ref.seif, None
            ref.notes.append("« siman:n » lu comme siman:séif katan pour la Michna Beroura")

    refs.sort(key=lambda r: r.span)
    return _dedupe(refs)


def _dedupe(refs: list[ParsedRef]) -> list[ParsedRef]:
    """Écarte les références dont le span est inclus dans un autre."""
    out: list[ParsedRef] = []
    for ref in refs:
        if any(o.span[0] <= ref.span[0] and ref.span[1] <= o.span[1] and o is not ref
               for o in refs):
            continue
        out.append(ref)
    return out
