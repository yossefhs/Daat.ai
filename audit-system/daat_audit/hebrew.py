# -*- coding: utf-8 -*-
"""Normalisation et comparaison de l'hébreu (§9).

Deux modes, et le texte original TOUJOURS conservé :

- **stricte** : comparaison caractère par caractère, telle quelle ;
- **normalisée** : on ignore, *pour la comparaison seulement*, le nikoud,
  les te'amim, les espaces multiples, les variantes de guillemets, le maqaf,
  les équivalents Unicode et la ponctuation non significative.

Le résultat n'est jamais binaire : la fonction ``compare`` rend un verdict
gradué (identique, différence de nikoud, mot ajouté, citation tronquée…),
parce qu'une variante d'édition n'est pas une erreur (§8).

Cette logique reprend celle éprouvée par ``scripts/verifier-citations.py``
à la racine du dépôt — notamment le développement des abréviations à
gershayim, sans lequel « הקב״ה » et « הקדוש ברוך הוא » sont vus comme
différents.
"""
from __future__ import annotations

import difflib
import enum
import re
import unicodedata

# ── Plages Unicode hébraïques ────────────────────────────────────────────
NIKUD = re.compile(r"[֑-ׇ]")          # nikoud + te'amim + meteg…
HEBREW_LETTER = re.compile(r"[א-ת]")
_GERSHAYIM = "״""                      # ״ et "
_GERESH = "׳'"                         # ׳ et '
_MAQAF = "־"                                # ־

# Guillemets et tirets équivalents, ramenés à une forme unique.
_EQUIV = {
    "«": '"', "»": '"', "„": '"', "”": '"', "“": '"', "‟": '"',
    "‹": "'", "›": "'", "’": "'", "‘": "'",
    "–": "-", "—": "-", "‒": "-", _MAQAF: "-",
    " ": " ", " ": " ", "‎": "", "‏": "",  # espaces/marques bidi
}

# Abréviations à gershayim développées avant comparaison.
ABBREVIATIONS: dict[str, str] = {
    "הקב״ה": "הקדוש ברוך הוא",
    "ת״ר": "תנו רבנן",
    "ב״ש": "בית שמאי",
    "ב״ה": "בית הלל",
    "רשב״י": "רבי שמעון בר יוחאי",
    "ריב״ל": "רבי יהושע בן לוי",
    "רנב״י": "רב נחמן בר יצחק",
    "ר״ל": "ריש לקיש",
    "אע״פ": "אף על פי",
    "אעפ״י": "אף על פי",
    "כ״ש": "כל שכן",
    "ק״ו": "קל וחומר",
    "אא״כ": "אלא אם כן",
    "וכו׳": "",   # marqueur de troncature
    "וגו׳": "",
}

# Marqueurs de coupe : « A… B » signifie que A et B sont chacun littéraux.
ELLIPSIS = re.compile(r"…|\.\.\.|וכו[׳']|\bכו[׳']")


class Verdict(str, enum.Enum):
    """Résultats gradués de la comparaison (§9)."""

    IDENTIQUE = "identique"
    DIFF_PONCTUATION = "difference_ponctuation"
    DIFF_NIKOUD = "difference_nikoud"
    DIFF_ORTHOGRAPHE = "difference_orthographe"
    MOT_AJOUTE = "mot_ajoute"
    MOT_SUPPRIME = "mot_supprime"
    MOT_REMPLACE = "mot_remplace"
    ORDRE_DIFFERENT = "ordre_different"
    CITATION_TRONQUEE = "citation_tronquee"
    VARIANTE_POSSIBLE = "variante_possible"
    DIFFERENCE_SUBSTANTIELLE = "difference_substantielle"


# Gravité relative des verdicts. Sert à choisir le PIRE tronçon d'une citation
# coupée : à ratio égal, c'est le verdict le plus grave qui doit l'emporter,
# sinon un tronçon littéral masque un tronçon douteux.
SEVERITY: dict[Verdict, int] = {
    Verdict.IDENTIQUE: 0,
    Verdict.DIFF_PONCTUATION: 1,
    Verdict.DIFF_NIKOUD: 1,
    Verdict.DIFF_ORTHOGRAPHE: 2,
    Verdict.CITATION_TRONQUEE: 2,
    Verdict.ORDRE_DIFFERENT: 3,
    Verdict.MOT_AJOUTE: 4,
    Verdict.MOT_SUPPRIME: 4,
    Verdict.MOT_REMPLACE: 5,
    Verdict.VARIANTE_POSSIBLE: 5,
    Verdict.DIFFERENCE_SUBSTANTIELLE: 6,
}


def _apply_equivalents(text: str) -> str:
    for src, dst in _EQUIV.items():
        text = text.replace(src, dst)
    return text


def expand_abbreviations(text: str) -> str:
    """Développe les abréviations à gershayim (avant retrait du nikoud)."""
    for abbrev, full in ABBREVIATIONS.items():
        text = text.replace(abbrev, full)
        text = text.replace(abbrev.replace("״", '"'), full)
    return text


def strip_nikud(text: str) -> str:
    return NIKUD.sub("", text)


def normalize(text: str, *, drop_nikud: bool = True, drop_punct: bool = True) -> str:
    """Forme normalisée pour comparaison. N'altère jamais l'original."""
    text = unicodedata.normalize("NFC", text)
    text = _apply_equivalents(text)
    text = expand_abbreviations(text)
    if drop_nikud:
        text = strip_nikud(text)
    if drop_punct:
        text = re.sub(r"[^א-ת\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def letters_only(text: str) -> str:
    """Consonnes hébraïques uniquement — la forme la plus tolérante."""
    return "".join(HEBREW_LETTER.findall(normalize(text)))


def n_letters(text: str) -> int:
    return len(letters_only(text))


def _words(text: str) -> list[str]:
    return normalize(text).split()


def defective_letters(text: str) -> str:
    """Squelette consonantique avec les *mères de lecture* vav neutralisées.

    Sefaria sert un texte vocalisé en graphie **défective** (עֹנֶג, מְכֻבָּד) ;
    le site écrit la même citation en graphie **pleine**, sans nikoud
    (עונג, מכובד). Sans cette forme, le verset d'Isaïe 58:13 cité mot pour mot
    ressort en « mot remplacé » — un faux positif de pure orthographe.

    Seul le **vav médian** est retiré, et c'est délibéré :

    - le vav *initial* est presque toujours la conjonction « et » — le retirer
      ferait disparaître une vraie différence de sens (ובא / בא) ;
    - le vav *final* porte un suffixe possessif (לו, בו) ;
    - le **yod** n'est pas touché : le neutraliser confondrait בית et בת,
      אין et אן — on préfère un faux positif à une erreur non détectée.

    Deux mots que cette forme rapproche restent donc *signalés* comme variante
    orthographique (jamais « identique ») : sans nikoud, שלום et שלם ont bel et
    bien le même squelette, et l'outil ne peut pas honnêtement trancher.
    """
    out = []
    for word in _words(text):
        if len(word) > 2:
            word = word[0] + word[1:-1].replace("ו", "") + word[-1]
        out.append(word)
    return "".join(out)


def compare(quote: str, source: str) -> tuple[Verdict, float, str]:
    """Compare une citation à un texte source.

    Retourne ``(verdict, ratio, détail)``. ``ratio`` est la similarité
    difflib sur les consonnes (0–1). La comparaison est faite tronçon par
    tronçon quand la citation contient une coupe (« A… B »).
    """
    parts = [p for p in ELLIPSIS.split(quote) if n_letters(p) >= 3]
    truncated = len(parts) > 1
    parts = parts or [quote]

    haystack = letters_only(source)
    verdicts: list[tuple[Verdict, float, str]] = []

    for part in parts:
        needle = letters_only(part)
        if not needle:
            continue
        if needle in haystack:
            verdicts.append((Verdict.IDENTIQUE, 1.0, ""))
            continue
        # Présent en ignorant seulement la ponctuation ? le nikoud ?
        if letters_only(strip_nikud(part)) in letters_only(strip_nikud(source)):
            verdicts.append((Verdict.DIFF_NIKOUD, 1.0, "nikoud uniquement"))
            continue
        # Présent à la graphie pleine/défective près ? (עונג / עֹנֶג)
        if defective_letters(part) in defective_letters(source):
            verdicts.append((
                Verdict.DIFF_ORTHOGRAPHE, 1.0,
                "graphie pleine ou défective (vav mère de lecture) — à confirmer",
            ))
            continue
        verdicts.append(_diff_words(part, source, needle, haystack))

    if not verdicts:
        return Verdict.DIFFERENCE_SUBSTANTIELLE, 0.0, "citation trop courte"

    # À ratio égal, le verdict le plus grave l'emporte : un tronçon littéral ne
    # doit jamais masquer un tronçon douteux.
    worst = min(verdicts, key=lambda v: (v[1], -SEVERITY[v[0]]))
    if not truncated:
        return worst
    if SEVERITY[worst[0]] <= SEVERITY[Verdict.DIFF_NIKOUD]:
        return Verdict.CITATION_TRONQUEE, worst[1], "tronçons tous littéraux (coupe signalée)"
    return worst[0], worst[1], f"{worst[2]} (citation tronçonnée)"


def _diff_words(part: str, source: str, needle: str, haystack: str
                ) -> tuple[Verdict, float, str]:
    """Qualifie l'écart quand la citation n'est pas retrouvée telle quelle."""
    ratio, window = _best_window(needle, haystack)

    q_words = _words(part)
    # Diff contre la FENÊTRE correspondante, pas contre la source entière : un
    # folio du Talmud fait quelques milliers de mots, et comparer une citation
    # de dix mots à tout le folio produit un écart illisible
    # (« הבורא » → toute la sougya suivante) au lieu du mot réellement changé.
    s_words = _best_word_window(q_words, _words(source))
    matcher = difflib.SequenceMatcher(None, q_words, s_words, autojunk=False)
    ops = [op for op in matcher.get_opcodes() if op[0] != "equal"]

    if ratio >= 0.995:
        return Verdict.DIFF_PONCTUATION, ratio, "ponctuation ou espaces"

    if ops and all(op[0] == "insert" for op in ops):
        return Verdict.MOT_SUPPRIME, ratio, "la citation omet des mots de la source"
    if ops and all(op[0] == "delete" for op in ops):
        return Verdict.MOT_AJOUTE, ratio, "la citation ajoute des mots absents de la source"

    if ratio >= 0.90:
        replaced = []
        for tag, i1, i2, j1, j2 in ops:
            if tag != "replace":
                continue
            avant, apres = " ".join(q_words[i1:i2]), " ".join(s_words[j1:j2])
            # Un couple qui ne diffère que par une mère de lecture n'est pas un
            # mot remplacé : l'annoncer comme tel ferait lire un second défaut
            # là où il n'y en a qu'un (« קדשת » → « קדושת »).
            if defective_letters(avant) == defective_letters(apres):
                continue
            replaced.append(f"« {avant} » → « {apres} »")
        return (Verdict.MOT_REMPLACE, ratio,
                " ; ".join(replaced[:2]) or "mots différents")

    if ratio >= 0.75:
        if sorted(q_words) and set(q_words) <= set(s_words):
            return Verdict.ORDRE_DIFFERENT, ratio, "mêmes mots, ordre différent"
        return Verdict.VARIANTE_POSSIBLE, ratio, f"proche : « {window[:60]} »"

    return Verdict.DIFFERENCE_SUBSTANTIELLE, ratio, "aucune correspondance nette"


def _best_word_window(quote_words: list[str], source_words: list[str]) -> list[str]:
    """Passage de la source qui correspond le mieux à la citation, en mots.

    Sert uniquement à rendre le diff lisible : le verdict, lui, s'appuie sur
    ``_best_window`` (consonnes). Une marge est laissée de part et d'autre
    pour qu'un mot ajouté en bordure reste visible.
    """
    if not quote_words or not source_words:
        return source_words
    taille = len(quote_words)
    if len(source_words) <= taille:
        return source_words

    marge = max(2, taille // 4)
    aiguille = "".join(quote_words)
    meilleur, debut = -1.0, 0
    for i in range(0, len(source_words) - taille + 1):
        fenetre = "".join(source_words[i: i + taille])
        ratio = difflib.SequenceMatcher(None, aiguille, fenetre).quick_ratio()
        if ratio > meilleur:
            meilleur, debut = ratio, i
    return source_words[max(0, debut - marge): debut + taille + marge]


def _best_window(needle: str, haystack: str) -> tuple[float, str]:
    """Meilleure similarité entre ``needle`` et une fenêtre de ``haystack``."""
    if not needle or not haystack:
        return 0.0, ""
    n = len(needle)
    if n >= len(haystack):
        return difflib.SequenceMatcher(None, needle, haystack).ratio(), haystack
    best, at = 0.0, 0
    step = max(1, n // 6)
    for i in range(0, len(haystack) - n + 1, step):
        r = difflib.SequenceMatcher(None, needle, haystack[i:i + n]).quick_ratio()
        if r > best:
            best, at = r, i
    lo, hi = max(0, at - step), min(len(haystack) - n, at + step)
    for i in range(lo, hi + 1):
        r = difflib.SequenceMatcher(None, needle, haystack[i:i + n]).ratio()
        if r > best:
            best, at = r, i
    return best, haystack[at:at + n]
