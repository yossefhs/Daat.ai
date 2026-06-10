#!/usr/bin/env python3
"""
DAAT — Liens d'ancrage intra-page.

Ce script ajoute automatiquement des liens internes <a class="intra-ref"
href="#anchor-id"> aux pages siman (4 niveaux × 3 langues × 124 simanim).
Un terme important dans un texte pédagogique (translation / key-point /
definition / remember / paragraphe) devient cliquable et le clic scrolle
vers la section qui l'explique plus bas dans la page.

Pipeline (par fichier HTML) :

  1. Parse léger, basé regex, scopé aux balises identifiées : on n'altère
     que les attributs id sur <h2>/<h3> et on n'insère des <a> qu'à
     l'intérieur de conteneurs pédagogiques.
  2. Détection des ancres : <h2>, <h3>, <summary>, <details> et tout
     élément avec un id="" explicite. Slug stable construit depuis le
     texte du titre (FR/HE/EN).
  3. Extraction des termes ancrables : mots significatifs du titre + le
     titre entier. Blacklist par langue (depuis data/internal-links.json).
  4. Wrap d'une occurrence par paragraphe de texte AVANT l'ancre.
     Heuristiques anti-pollution intégrées (cf. ci-dessous).
  5. Idempotent : ne double pas les <a class="intra-ref"> existants.
  6. Injection de <link> CSS et <script> JS dans <head>/avant </body>.

Cibles HTML :
  - sources/shabbat/siman-{n}/index{,-en,-he}.html
  - sources/shabbat/siman-{n}/niveau-{1..4}-*.html

Convention trilingue (CLAUDE.md) :
  - X.html       = français (lang="fr")
  - X-he.html    = hébreu (lang="he", dir="rtl")
  - X-en.html    = anglais (lang="en")
Un terme FR pointe vers une ancre FR ; pareil HE/EN. Pas de cross-langue.

CRITIQUE — ne JAMAIS modifier le texte halakhique source :
  - blockquote.text-source (Mehaber / Rama / HaRav / Mishna Beroura)
  - blockquote.sacred-text
  - .he-q (citations hébraïques inline)
  - <bdi> (numérotation hébraïque)
Le wrapping s'applique uniquement aux conteneurs « pédagogiques »
allowlistés (voir ALLOWED_CONTAINERS).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCES_ROOT = os.path.join(REPO_ROOT, "sources", "shabbat")
DATA_FILE = os.path.join(REPO_ROOT, "data", "internal-links.json")

FIRST_SIMAN, LAST_SIMAN = 242, 365

CSS_HREF = "/assets/css/intra-links.css"
JS_SRC = "/assets/js/intra-links.js"

LEVEL_STEMS = {
    1: "niveau-1-base",
    2: "niveau-2-lamdan",
    3: "niveau-3-synthese",
    4: "niveau-4-daat-harav",
}

LANG_SUFFIX = {"fr": "", "he": "-he", "en": "-en"}

# Niveau 4 absent (l'Admour HaZaken n'a pas écrit la Choulhan Aroukh HaRav
# pour ces simanim).
NO_LEVEL_4 = {304, 322}

# Conteneurs pédagogiques où l'on peut wrapper des liens. On exclut
# délibérément blockquote.text-source / blockquote.sacred-text, les
# spans .he-q, les <bdi> et les <p class="sa-..."> (texte source de la
# Choulhan Aroukh HaRav).
ALLOWED_CONTAINERS = {
    "div.translation",
    "div.key-point",
    "div.definition",
    "div.remember",
    "div.question-box",
    "p",
    "li",
}

# Tags qu'il faut sauter purement et simplement (jamais de wrap dedans)
SKIP_TAGS_RE = re.compile(
    r"<(?:script|style|head|code|pre|blockquote|bdi|summary)\b[^>]*>.*?</(?:script|style|head|code|pre|blockquote|bdi|summary)>",
    re.IGNORECASE | re.DOTALL,
)

# Classes / contextes interdits (texte halakhique source). Tout conteneur
# qui matche l'une de ces classes — ou qui en est un descendant direct —
# est exclu du wrapping.
FORBIDDEN_CLASS_RE = re.compile(
    r'class="[^"]*\b(?:'
    r"sa-he|sa-fr|sa-en|sa-block|text-source|sacred-text|"
    r"seif-summary|seif-preview|seif-num|seif-details|"
    r"he-q|hero-title-he|sefaria-source"
    r')\b[^"]*"',
    re.IGNORECASE,
)

# Min taille DOM (en chars) entre source-de-lien et ancre pour qu'un lien
# soit pertinent (sinon il est inutile).
MIN_DOM_DISTANCE = 300

# Longueurs minimales d'un terme pour qu'il soit ancrable
MIN_TERM_LEN_LATIN = 5
MIN_TERM_LEN_HE = 4

# Plafonds anti-pollution
MAX_LINKS_PER_FILE = 40
MAX_LINKS_PER_CONTAINER = 2

# Stopwords additionnels (en plus de la blacklist user) — termes trop
# génériques qui pollueraient les pages si on les liait.
BUILTIN_STOPWORDS = {
    "fr": {
        "jours", "jour", "vendredi", "samedi", "dimanche", "lundi", "mardi",
        "mercredi", "jeudi", "matin", "soir", "nuit", "semaine",
        "avant", "après", "pendant", "durant", "selon", "pour", "dans",
        "avec", "sans", "vers", "chez", "depuis", "alors", "ainsi",
        "cette", "cette-ci", "celui", "celle", "ceux", "celles", "leur",
        "leurs", "notre", "votre", "nos", "vos",
        "moderne", "modernes", "pratique", "pratiques",
        "exemple", "exemples", "question", "questions", "réponse",
        "réponses", "concept", "concepts", "notion", "notions",
        "première", "deuxième", "troisième", "premier", "second",
        "trois", "quatre", "cinq", "quel", "quelle",
        "central", "centrale", "général", "générale", "axiome",
        "synthèse", "résumé", "récap", "récapitulatif",
        "comprendre", "comprend", "voir", "regarder", "lire",
        "siman", "seif", "seifim", "séif", "shabbat", "mehaber",
        "rama", "harav", "daat", "niveau", "base", "lamdan",
        "halakha", "halakhique", "choulhan", "aroukh",
        "trois", "même", "tout", "tous", "toute", "toutes",
        "long", "courrier", "into", "bateau", "ship",
        # Termes qui sortent en tête lors du test corpus mais qui sont
        # peu signifiants en tant que liens.
        "hazaken", "admour", "intégral", "ensemble", "tableau",
        "synthèse", "finale", "cases", "habad", "chabad", "shitah",
        "place", "place-clé", "commandements", "rebbe",
        "berurah", "berura", "berurah", "mishna", "mishnah",
        "chaque", "ainsi", "encore", "donc", "puis", "même", "aussi",
        "fait", "faits", "très", "bien", "déjà", "souvent",
        "raison", "raisons", "cause", "causes", "loin", "près",
        "souvent", "parfois", "rarement", "toujours", "jamais",
        "lorsque", "quand", "comme", "puisque", "parce", "parce-que",
        "mais", "or", "donc", "ainsi", "etc",
        "permis", "interdit", "permise", "interdite",
        "axiome", "axiomes", "axiom",
        "chitah", "shitah", "schita", "psak", "pesak",
        "condensé", "condensés", "condensed",
        "pièges", "pitfalls", "piège",
        "arbre", "arbres", "tree", "trees",
        "décision", "décisions", "decision", "decisions",
        "hierarchie", "hierarchy", "hiérarchie",
        "mnémonique", "mnemonic", "mnemonics",
        "overview", "vue", "vue-d-ensemble",
        "halakhiques", "halakhique",
        "éviter", "éviter,", "à-éviter",
        "kiddush", "kiddoush", "kidoush",
        "mélakha", "melakha", "mélachot", "melachot",
        "matrice", "matrices",
        "approche", "approches",
        "commandement", "commandements",
    },
    "he": {
        "ימים", "יום", "ערב", "בוקר", "לילה",
        "סעיף", "סעיפים", "סימן", "שבת", "מחבר", "הלכה",
        "ראשון", "שני", "שלישי", "רביעי",
        "כללי", "פרטי", "מעשי", "תיאורטי",
        "פירוש", "פירושים", "מושג", "מושגים",
        "תוכן", "תוכנית", "סיכום", "מבוא",
        "אדמו", "הזקן", "הרב",
        "השבת", "קודם", "כדבר", "הימים", "בשבת",
        # Termes qui sortent en tête lors du test corpus.
        "מקור", "ברורה", "הרבי", "האחרון", "האחרונים",
        "המקור", "השיטה", "השיטות", "השיטתי",
        "טבלה", "סופית", "טבלת", "סיכומי",
        "אסור", "מותר", "מתירין", "אוסרין",
        "וכן", "וכל", "כל", "כאשר", "כיון", "מכל",
        "במקרה", "מקרים", "במקרים", "במקום",
        "לפי", "לכן", "כלומר", "אם", "אבל", "או",
        "וגם", "וגם", "אף", "אפילו", "רק", "גם",
        "ערוך", "שולחן", "שלחן",
        "מחלוקת", "הכרעת", "ההלכה",
        "פסק", "פסיקה",
        "שיטה", "שיטת",
        "סופית", "סיכומית",
        "אדמו", "אדמו״ר",
        "הסעיפים",
    },
    "en": {
        "days", "day", "friday", "saturday", "sunday", "monday",
        "tuesday", "wednesday", "thursday", "morning", "evening", "night",
        "before", "after", "during", "according", "into", "with",
        "without", "toward", "since", "then", "this", "these", "those",
        "their", "theirs", "modern", "moderns", "practical",
        "example", "examples", "question", "questions", "answer",
        "answers", "concept", "concepts", "notion", "notions",
        "first", "second", "third", "central", "general",
        "synthesis", "summary", "recap", "understand", "understands",
        "see", "look", "read", "level", "base", "lamdan",
        "siman", "seif", "seifim", "shabbat", "shabbos", "mechaber",
        "rema", "shulchan", "aruch", "halacha", "halachic",
        "three", "every", "every-time", "long", "haul", "ship",
        "rebbe", "alter",
        # Termes qui sortent en tête lors du test corpus.
        "hazaken", "admour", "complete", "full", "text", "texts",
        "table", "summary", "synthesis", "final", "cases",
        "shitah", "chabad", "habad", "place",
        "berurah", "berura", "mishnah", "mishna",
        "case", "rule", "example", "always", "never", "often",
        "sometimes", "when", "where", "what", "which", "while",
        "because", "since", "therefore", "thus", "also",
        "permitted", "forbidden", "allowed", "prohibited",
        "axiom", "axioms",
        "hierarchy", "hierarchies",
        "pitfall", "pitfalls", "avoid",
        "condensed", "condense",
        "decision", "decisions",
        "tree", "trees", "branch", "branches",
        "mnemonic", "mnemonics",
        "overview", "view",
        "matrix", "matrices",
        "approach", "approaches",
        "commandment", "commandments",
        "melakha", "melachah", "melachot",
    },
}

# Caractères de découpe pour la tokenisation d'un titre
SPLIT_RE = re.compile(r"[\s,;:.()\[\]/—–\-•·*\"'’`«»]+")
# Caractères qu'on retire en début/fin d'un terme
STRIP_CHARS = " ,;:.()[]/—–\"'’`«»*•·\t\n\r"

# Pour le matching insensible aux nikud (HE)
NIKUD_RE = re.compile(r"[֑-ֽֿׁ-ׂׄ-ׇ]")

# Numérotation TOC (1. 2.3 §7 ס״ק) à retirer de l'extraction de termes
NUM_RE = re.compile(r"^[\d\s.§א-ת\"׳״ʼ׳·]+")

# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------


def load_overrides():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"blacklist": {}, "force": {}, "skip": {}}
    # Merge built-in stopwords into the user-supplied blacklist
    bl = data.setdefault("blacklist", {})
    for lang, words in BUILTIN_STOPWORDS.items():
        merged = set(w.casefold() for w in bl.get(lang, []))
        merged.update(w.casefold() for w in words)
        bl[lang] = sorted(merged)
    return data


HEBREW_CHAR_RE = re.compile(r"[֐-׿]")


def is_mostly_hebrew(text: str) -> bool:
    """Vrai si plus de 50% des caractères alpha sont hébreux."""
    he = 0
    alpha = 0
    for ch in text:
        if ch.isalpha():
            alpha += 1
            if HEBREW_CHAR_RE.match(ch):
                he += 1
    return alpha > 0 and he * 2 > alpha


def combined_blacklist(overrides: dict, primary_lang: str) -> set[str]:
    """Construit la blacklist effective : la langue primaire + l'hébreu.

    Permet de filtrer les tokens hébreux qui apparaissent dans les pages
    FR/EN (titres avec citations הלכתיות).
    """
    bl_dict = overrides.get("blacklist", {})
    out = set(bl_dict.get(primary_lang, []))
    if primary_lang != "he":
        out.update(bl_dict.get("he", []))
    return {w.casefold() for w in out}


def normalize_for_match(text: str, lang: str) -> str:
    """Texte normalisé pour comparaison (lowercase, sans nikud HE)."""
    t = text
    if lang == "he":
        t = NIKUD_RE.sub("", t)
    return t.casefold()


def strip_html_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def decode_entities(s: str) -> str:
    # Décode les entités les plus courantes pour avoir un titre lisible
    repl = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&apos;": "'",
        "&laquo;": "«", "&raquo;": "»",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    # entités numériques
    s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s)
    return s


def slugify(text: str, lang: str) -> str:
    """Produit un slug stable à partir du texte d'un titre."""
    s = decode_entities(strip_html_tags(text))
    s = NIKUD_RE.sub("", s)
    # Latin: normalisation NFKD pour retirer les accents
    if lang != "he":
        s = unicodedata.normalize("NFKD", s)
        s = "".join(c for c in s if not unicodedata.combining(c))
    # Garde lettres / chiffres / espaces / tirets ; conserve l'hébreu
    out = []
    for ch in s:
        if ch.isalnum() or ch in (" ", "-", "_"):
            out.append(ch)
        elif "֐" <= ch <= "׿":
            out.append(ch)
        else:
            out.append("-")
    s = "".join(out)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    s = s.lower() if lang != "he" else s
    if not s:
        s = "section"
    # Borne la longueur pour éviter des slugs interminables
    if len(s) > 80:
        s = s[:80].rstrip("-")
    return s


# ---------------------------------------------------------------------------
# Détection des ancres (H2/H3/SUMMARY + id="" explicites)
# ---------------------------------------------------------------------------


class AnchorScanner(HTMLParser):
    """Scanne <body> et collecte les ancres potentielles."""

    def __init__(self, lang: str):
        super().__init__(convert_charrefs=True)
        self.lang = lang
        self.in_body = False
        self.in_head = False
        self.depth = 0
        self.anchors = []  # liste de (tag, id_or_None, title, start, end)
        self._stack = []   # stack of (tag, attrs_dict, title_buf, start_pos)
        self.body_start = None
        self.body_end = None

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        if tag == "body":
            self.in_body = True
            self.body_start = self.getpos()
        if not self.in_body or self.in_head:
            return
        # On EXCLUT <summary> de la détection d'ancres : ses titres
        # contiennent souvent du texte halakhique source (citations de la
        # Choulhan Aroukh HaRav dans niveau-4) ou de simples libellés
        # d'UI ("cliquer pour déplier"). Garder un id si présent —
        # mais ne pas en faire une cible.
        if tag in ("h2", "h3"):
            self._stack.append({
                "tag": tag,
                "attrs": dict(attrs),
                "title": [],
                "line": self.getpos(),
            })

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag == "body":
            self.body_end = self.getpos()
            self.in_body = False
        if not self.in_body:
            return
        if tag in ("h2", "h3") and self._stack:
            top = self._stack.pop()
            if top["tag"] != tag:
                return
            title = "".join(top["title"]).strip()
            if not title:
                return
            existing_id = top["attrs"].get("id")
            self.anchors.append({
                "tag": tag,
                "id": existing_id,
                "title": title,
                "line": top["line"],
            })

    def handle_data(self, data):
        if self._stack:
            self._stack[-1]["title"].append(data)


# ---------------------------------------------------------------------------
# Modification du HTML : ajout d'ids sur les balises d'ancre
# ---------------------------------------------------------------------------


def find_tag_open_positions(html: str, tag: str):
    """Itère sur les ouvertures de <tag ...>. Renvoie (start, end_of_open_tag).

    end_of_open_tag = position juste avant le '>' final, pour pouvoir insérer
    un attribut.
    """
    pattern = re.compile(rf"<{tag}\b([^>]*)>", re.IGNORECASE)
    for m in pattern.finditer(html):
        yield m.start(), m.end() - 1, m.group(1)


def has_id_attr(attrs: str) -> str | None:
    m = re.search(r'\bid\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', attrs)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else m.group(2)


def inject_id_attr(html: str, end_of_open_tag: int, new_id: str) -> str:
    """Insère ` id="..."` juste avant le `>` final d'une balise ouvrante."""
    return html[:end_of_open_tag] + f' id="{new_id}"' + html[end_of_open_tag:]


# ---------------------------------------------------------------------------
# Extraction des termes ancrables depuis un titre
# ---------------------------------------------------------------------------


def extract_terms(title: str, lang: str, blacklist: set[str]) -> list[str]:
    """Liste de termes candidats à matcher pour cette ancre.

    Stratégie :
      - retire numérotation (1. , 2.3 , §7 ...).
      - garde le titre entier (utile pour matcher la phrase exacte).
      - tokenise et garde les mots significatifs.

    Filtres :
      - on rejette les titres entiers de type "Siman XXX" / "סימן XXX"
        qui ne sont que des références (et qui matchent partout) ;
      - on rejette un titre entier si plus de 50% de ses tokens sont
        blacklistés ;
      - on rejette un titre entier si son premier ou son dernier token
        est blacklisté (signe d'une référence générique).
    """
    clean = decode_entities(strip_html_tags(title))
    clean = NUM_RE.sub("", clean).strip(STRIP_CHARS)
    if not clean:
        return []
    terms: list[str] = []

    min_len = MIN_TERM_LEN_HE if lang == "he" else MIN_TERM_LEN_LATIN

    # Tokenise une fois pour les filtres / extraction
    raw_tokens = [t.strip(STRIP_CHARS)
                  for t in SPLIT_RE.split(clean) if t.strip(STRIP_CHARS)]
    significant = []
    for tok in raw_tokens:
        tok_is_he = is_mostly_hebrew(tok)
        # Détermine longueur min et règle de normalisation selon le
        # caractère effectif du token, pas seulement la langue de la page.
        tok_len = (len(NIKUD_RE.sub("", tok))
                   if tok_is_he or lang == "he" else len(tok))
        tok_min = MIN_TERM_LEN_HE if tok_is_he else min_len
        if tok_len < tok_min:
            continue
        # Normalisation : si le token est hébreu, on retire les nikud.
        if tok_is_he:
            norm = NIKUD_RE.sub("", tok).casefold()
        else:
            norm = normalize_for_match(tok, lang)
        if norm in blacklist:
            continue
        significant.append(tok)

    # Filtre : rejette "Siman XXX" / "סימן XXX" purs (que des refs)
    low = clean.lower()
    if (re.match(r"^siman\s+\S+$", low)
            or re.match(r"^seif\s+\S+$", low)
            or clean.startswith("סימן ")
            or clean.startswith("סעיף ")):
        # Pas de titre entier, mais on peut garder les sous-tokens significatifs
        pass
    elif 8 <= len(clean) <= 60 and significant:
        # On ne garde le titre entier que si au moins la moitié de ses
        # tokens sont significatifs (filtre les titres-références).
        ratio = len(significant) / max(1, len(raw_tokens))
        if ratio >= 0.5:
            terms.append(clean)

    seen = {normalize_for_match(t, lang) for t in terms}
    for tok in significant:
        norm = normalize_for_match(tok, lang)
        if norm in seen:
            continue
        seen.add(norm)
        terms.append(tok)

    return terms


# ---------------------------------------------------------------------------
# Wrapping des occurrences dans un fragment HTML "sûr" (zone autorisée)
# ---------------------------------------------------------------------------

# Découpe un fragment en alternance (texte, balise). On wrappe uniquement
# dans les nœuds texte (entre balises), et on saute les zones blockquote /
# script / style / bdi qui pourraient contenir du texte halakhique cité.

TAG_RE = re.compile(r"<[^>]+>")


def wrap_in_fragment(fragment: str, term: str, anchor_id: str,
                     lang: str) -> tuple[str, bool]:
    """Wrappe la 1re occurrence de `term` dans le fragment hors balises.

    - Évite les zones blockquote/script/style/bdi/code/pre via mask.
    - Évite les <a> existants.
    - Évite les attributs (on ne wrappe que dans les data, jamais dedans
      un attribut).

    Retourne (new_fragment, ok).
    """
    # 1) Calcule un masque des zones interdites (1 = zone interdite)
    forbidden = bytearray(len(fragment))

    def mark(start, end):
        for i in range(start, min(end, len(fragment))):
            forbidden[i] = 1

    # blockquote / script / style / code / pre / bdi / summary
    for m in re.finditer(
        r"<(blockquote|script|style|code|pre|bdi|summary)\b[^>]*>.*?</\1>",
        fragment, re.IGNORECASE | re.DOTALL,
    ):
        mark(m.start(), m.end())

    # he-q (citations hébraïques inline)
    for m in re.finditer(
        r'<span[^>]*class="[^"]*\bhe-q\b[^"]*"[^>]*>.*?</span>',
        fragment, re.IGNORECASE | re.DOTALL,
    ):
        mark(m.start(), m.end())

    # p.sa-he / p.sa-fr / p.sa-en (source halakhique)
    for m in re.finditer(
        r'<p\s+class="[^"]*\bsa-(?:he|fr|en)\b[^"]*"[^>]*>.*?</p>',
        fragment, re.IGNORECASE | re.DOTALL,
    ):
        mark(m.start(), m.end())

    # <a> existants — ne pas wrapper à l'intérieur (double-lien)
    for m in re.finditer(r"<a\b[^>]*>.*?</a>", fragment,
                         re.IGNORECASE | re.DOTALL):
        mark(m.start(), m.end())

    # Toutes les balises (pour ne pas wrapper dans les attributs)
    for m in TAG_RE.finditer(fragment):
        mark(m.start(), m.end())

    # 2) Construit une représentation "texte plat" + mapping vers positions
    #    réelles pour pouvoir chercher en case-insensible / sans nikud.
    plain_chars: list[str] = []
    plain_to_real: list[int] = []
    for i, ch in enumerate(fragment):
        if forbidden[i]:
            continue
        if lang == "he":
            if NIKUD_RE.match(ch):
                continue
        plain_chars.append(ch.casefold())
        plain_to_real.append(i)
    plain = "".join(plain_chars)

    # 3) Cherche le terme (lui aussi normalisé)
    needle = NIKUD_RE.sub("", term) if lang == "he" else term
    needle_cf = needle.casefold()
    if not needle_cf:
        return fragment, False

    # On veut respecter les frontières de mots pour le latin (évite
    # "halakha" qui matcherait dans "halakhique").
    pos = 0
    while True:
        idx = plain.find(needle_cf, pos)
        if idx == -1:
            return fragment, False
        # Word boundary check (Latin seulement)
        if lang != "he":
            before_ok = idx == 0 or not plain[idx - 1].isalpha()
            after_idx = idx + len(needle_cf)
            after_ok = (after_idx == len(plain)
                        or not plain[after_idx].isalpha())
            if not (before_ok and after_ok):
                pos = idx + 1
                continue
        # OK on a un match — convertit en positions réelles
        real_start = plain_to_real[idx]
        real_end_inclusive = plain_to_real[idx + len(needle_cf) - 1]
        real_end = real_end_inclusive + 1

        # Récupère le texte source réel (avec nikud / casse d'origine)
        original = fragment[real_start:real_end]

        # Vérifie qu'on ne casse pas l'HTML : entre real_start et real_end,
        # il ne doit y avoir aucune balise (déjà garanti par le masque)
        if any(forbidden[i] for i in range(real_start, real_end)):
            pos = idx + 1
            continue

        replacement = (
            f'<a class="intra-ref" href="#{anchor_id}">{original}</a>'
        )
        new_fragment = fragment[:real_start] + replacement + fragment[real_end:]
        return new_fragment, True


# ---------------------------------------------------------------------------
# Pipeline principal par fichier
# ---------------------------------------------------------------------------


CONTAINER_BLOCK_PATTERNS = [
    # (regex, sélecteur lisible)
    (re.compile(r'<div\s+class="translation"[^>]*>(.*?)</div>',
                re.IGNORECASE | re.DOTALL), "div.translation"),
    (re.compile(r'<div\s+class="key-point"[^>]*>(.*?)</div>',
                re.IGNORECASE | re.DOTALL), "div.key-point"),
    (re.compile(r'<div\s+class="definition"[^>]*>(.*?)</div>',
                re.IGNORECASE | re.DOTALL), "div.definition"),
    (re.compile(r'<div\s+class="remember"[^>]*>(.*?)</div>',
                re.IGNORECASE | re.DOTALL), "div.remember"),
    (re.compile(r'<div\s+class="question-box"[^>]*>(.*?)</div>',
                re.IGNORECASE | re.DOTALL), "div.question-box"),
    (re.compile(r"<p\b([^>]*)>(.*?)</p>",
                re.IGNORECASE | re.DOTALL), "p"),
    (re.compile(r"<li\b([^>]*)>(.*?)</li>",
                re.IGNORECASE | re.DOTALL), "li"),
]


def find_safe_containers(html: str, body_start: int, body_end: int):
    """Itère sur les conteneurs pédagogiques 'sûrs' dans le body.

    Yields tuples (start, end, content_start, content_end, selector).

    On ne renvoie PAS les conteneurs imbriqués dans un <blockquote>,
    un <a>, ou dans un conteneur source halakhique (sa-block, details,
    sa-he/fr/en).
    """
    # Pré-calcule les zones interdites (blockquote, script, style, code,
    # pre, sa-block, details.seif-details, p.sa-*, summary)
    forbidden_zones = []
    for m in re.finditer(
        r"<(blockquote|script|style|code|pre|summary)\b[^>]*>.*?</\1>",
        html, re.IGNORECASE | re.DOTALL,
    ):
        forbidden_zones.append((m.start(), m.end()))
    # div.sa-block (englobe les p.sa-he / p.sa-fr)
    for m in re.finditer(
        r'<div\s+class="[^"]*\bsa-block\b[^"]*"[^>]*>.*?</div>',
        html, re.IGNORECASE | re.DOTALL,
    ):
        forbidden_zones.append((m.start(), m.end()))
    # details (seif-details) — toute la balise details (inclut sa-block)
    for m in re.finditer(
        r"<details\b[^>]*>.*?</details>",
        html, re.IGNORECASE | re.DOTALL,
    ):
        forbidden_zones.append((m.start(), m.end()))
    # p.sa-he / p.sa-fr / p.sa-en (sécurité supplémentaire)
    for m in re.finditer(
        r'<p\s+class="[^"]*\bsa-(?:he|fr|en)\b[^"]*"[^>]*>.*?</p>',
        html, re.IGNORECASE | re.DOTALL,
    ):
        forbidden_zones.append((m.start(), m.end()))

    def in_forbidden(s, e):
        for fs, fe in forbidden_zones:
            if s >= fs and e <= fe:
                return True
        return False

    for pat, sel in CONTAINER_BLOCK_PATTERNS:
        for m in pat.finditer(html):
            s, e = m.start(), m.end()
            if s < body_start or e > body_end:
                continue
            if in_forbidden(s, e):
                continue
            # Pour <p> et <li> on a un groupe 1 = attrs, groupe 2 = content
            if sel in ("p", "li"):
                attrs = m.group(1) or ""
                content_start = m.start(2)
                content_end = m.end(2)
                # Skip si la balise elle-même a une classe interdite
                if FORBIDDEN_CLASS_RE.search("<x" + attrs + ">"):
                    continue
            else:
                content_start = m.start(1)
                content_end = m.end(1)
            yield s, e, content_start, content_end, sel


def detect_lang_from_filename(path: str) -> str:
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    if name.endswith("-he"):
        return "he"
    if name.endswith("-en"):
        return "en"
    return "fr"


def already_injected_css(html: str) -> bool:
    return CSS_HREF in html


def already_injected_js(html: str) -> bool:
    return JS_SRC in html


def inject_assets(html: str) -> tuple[str, bool, bool]:
    """Insère le <link> CSS dans <head> et le <script> JS avant </body>."""
    css_added = False
    js_added = False
    if not already_injected_css(html):
        # Insère juste avant </head>
        end_head = re.search(r"</head>", html, re.IGNORECASE)
        if end_head:
            link = f'<link rel="stylesheet" href="{CSS_HREF}">\n'
            html = (html[: end_head.start()] + link
                    + html[end_head.start():])
            css_added = True
    if not already_injected_js(html):
        end_body = re.search(r"</body>", html, re.IGNORECASE)
        if end_body:
            script = f'<script src="{JS_SRC}" defer></script>\n'
            html = (html[: end_body.start()] + script
                    + html[end_body.start():])
            js_added = True
    return html, css_added, js_added


def get_body_bounds(html: str) -> tuple[int, int]:
    bs = re.search(r"<body\b[^>]*>", html, re.IGNORECASE)
    be = re.search(r"</body>", html, re.IGNORECASE)
    if not bs or not be:
        return 0, len(html)
    return bs.end(), be.start()


def remove_intra_links(html: str) -> tuple[str, int]:
    """Retire tous les <a class="intra-ref" ...>...</a> en gardant le texte.
    Retire aussi les injections <link>/<script>.
    """
    pattern = re.compile(
        r'<a\s+class="intra-ref"\s+href="[^"]*">(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    n = 0

    def sub(m):
        nonlocal n
        n += 1
        return m.group(1)

    html = pattern.sub(sub, html)
    html = re.sub(
        rf'\s*<link rel="stylesheet" href="{re.escape(CSS_HREF)}">\s*\n?',
        "\n", html,
    )
    html = re.sub(
        rf'\s*<script src="{re.escape(JS_SRC)}" defer></script>\s*\n?',
        "\n", html,
    )
    return html, n


# ---------------------------------------------------------------------------
# Processus complet d'un fichier
# ---------------------------------------------------------------------------


def process_file(path: str, overrides: dict, *, siman: int | None,
                 dry_run: bool, stats_only: bool):
    """Renvoie un dict de stats pour ce fichier."""
    with open(path, encoding="utf-8") as f:
        html = f.read()

    lang = detect_lang_from_filename(path)
    # On combine la blacklist de la langue primaire avec celle de l'HE
    # (les pages FR/EN contiennent des citations hébraïques qu'il ne
    # faut pas transformer en liens).
    blacklist = combined_blacklist(overrides, lang)

    skip_anchors = set()
    if siman is not None:
        skip_anchors = set(
            overrides.get("skip", {}).get(str(siman), [])
        )

    # --- 1. Scan des ancres
    scanner = AnchorScanner(lang)
    scanner.feed(html)
    body_start, body_end = get_body_bounds(html)

    # Pour chaque ancre, on va devoir lui assigner un id stable. On
    # parcourt le HTML balise par balise dans l'ordre (h2/h3/summary) et
    # on injecte l'id manquant. On garde un mapping (ordre_apparition →
    # anchor_id final).

    # Recompute des positions des balises h2/h3/summary dans le HTML pour
    # injecter les ids dans le bon ordre. On opère sur une *liste*
    # d'éditions à appliquer en fin.

    inserts: list[tuple[int, str]] = []  # (position, attribut à insérer)
    used_slugs: dict[str, int] = {}
    anchor_records: list[dict] = []  # ordered

    # On extrait tous les h2/h3 dans l'ordre — leur ordre correspond
    # à l'ordre de AnchorScanner. (summary est exclu : voir AnchorScanner.)
    tag_positions = []
    for tag in ("h2", "h3"):
        for s, eo, attrs in find_tag_open_positions(html, tag):
            tag_positions.append((s, eo, attrs, tag))
    tag_positions.sort()

    # Joint AnchorScanner.anchors avec tag_positions par ordre
    if len(scanner.anchors) != len(tag_positions):
        # Cas pathologique (CDATA / commentaires) : on prend le min
        pass
    anchors_ordered = scanner.anchors[: len(tag_positions)]

    for (s, eo, attrs, tag), anc in zip(tag_positions, anchors_ordered):
        if s < body_start:
            # Skip ce qui est dans <head> ou avant body
            continue
        title = anc["title"].strip()
        if not title:
            continue
        existing_id = has_id_attr(attrs)
        if existing_id:
            anchor_id = existing_id
        else:
            base_slug = slugify(title, lang)
            if not base_slug:
                continue
            slug = base_slug
            i = 2
            # Évite la collision avec slugs déjà attribués dans cette
            # passe ET avec des ids existants dans le HTML
            existing_ids_in_doc = set(
                re.findall(r'\bid\s*=\s*"([^"]+)"', html)
            )
            while (slug in used_slugs
                   or slug in existing_ids_in_doc):
                slug = f"{base_slug}-{i}"
                i += 1
            used_slugs[slug] = s
            anchor_id = slug
            inserts.append((eo, f' id="{anchor_id}"'))

        if anchor_id in skip_anchors:
            continue
        anchor_records.append({
            "tag": tag,
            "id": anchor_id,
            "title": title,
            "start_in_orig": s,
        })

    # Applique les insertions d'id (en ordre inverse pour préserver les
    # offsets)
    for pos, payload in sorted(inserts, key=lambda x: -x[0]):
        html = html[:pos] + payload + html[pos:]

    # Recalcule body_bounds après insertion d'ids
    body_start, body_end = get_body_bounds(html)

    # --- 2. Pour chaque ancre, calcule sa position FINALE dans html
    # (les insertions d'ids ont décalé les positions).
    # On retrouve les ancres par id="..." en repassant.
    final_positions: dict[str, int] = {}
    for ar in anchor_records:
        tag = ar["tag"]
        pat = re.compile(
            rf'<{tag}\b[^>]*\bid="{re.escape(ar["id"])}"[^>]*>',
            re.IGNORECASE,
        )
        m = pat.search(html)
        if m:
            final_positions[ar["id"]] = m.start()

    # --- 3. Construit la table des termes : ordonnée par position d'ancre
    #        croissante, pour qu'un terme renvoie vers la 1re ancre
    #        pertinente.
    anchor_terms: list[tuple[str, int, list[str], str]] = []
    # (anchor_id, final_position, terms, original_title)
    for ar in anchor_records:
        if ar["id"] not in final_positions:
            continue
        fp = final_positions[ar["id"]]
        terms = extract_terms(ar["title"], lang, blacklist)
        if not terms:
            continue
        anchor_terms.append((ar["id"], fp, terms, ar["title"]))

    # Index par terme normalisé : term_norm → liste de (anchor_id, position)
    term_index: dict[str, list[tuple[str, int]]] = defaultdict(list)
    term_originals: dict[str, str] = {}
    for aid, fp, terms, _title in anchor_terms:
        for t in terms:
            tn = normalize_for_match(t, lang)
            if tn in blacklist:
                continue
            term_index[tn].append((aid, fp, t))
            term_originals.setdefault(tn, t)
    # Sort par position croissante pour chaque terme
    for tn in term_index:
        term_index[tn].sort(key=lambda x: x[1])

    # --- 4. Force-links éventuels
    force_links = []
    if siman is not None:
        for rule in overrides.get("force", {}).get(str(siman), []):
            if rule.get("lang") and rule["lang"] != lang:
                continue
            term = rule.get("term", "").strip()
            target = rule.get("target", "").strip().lstrip("#")
            if term and target:
                force_links.append((term, target))

    # --- 5. Parcourt les conteneurs pédagogiques dans l'ordre et wrappe
    #        une occurrence par paragraphe pour chaque terme dont l'ancre
    #        est plus loin dans le DOM.

    containers = list(find_safe_containers(html, body_start, body_end))
    # Tri par position de début puis end décroissant pour pouvoir
    # déduper les conteneurs imbriqués (on garde le plus extérieur).
    containers.sort(key=lambda c: (c[0], -c[1]))
    deduped: list[tuple] = []
    for c in containers:
        s, e = c[0], c[1]
        if deduped and s < deduped[-1][1]:
            # Imbriqué dans le précédent — on garde l'extérieur seulement
            continue
        deduped.append(c)
    containers = deduped

    # On va éditer le HTML en place — pour simplifier on travaille
    # backwards (de la fin au début) afin de conserver les offsets.
    edits: list[tuple[int, int, str]] = []
    # (content_start, content_end, new_content)
    links_created = 0
    top_terms: Counter = Counter()
    examples: list[tuple[str, str]] = []  # (terme matché, anchor_id)

    # Ordre des termes : on préfère matcher les termes longs / multi-mots
    # AVANT les tokens isolés (sinon un terme courant attire le lien).
    term_keys_sorted = sorted(
        term_index.keys(),
        key=lambda t: (-len(t), t),
    )

    # Compte les liens intra-ref déjà présents dans le HTML (idempotence)
    existing_links_total = len(re.findall(
        r'<a\s+class="intra-ref"', html, re.IGNORECASE,
    ))

    for c_start, c_end, cs, ce, sel in containers:
        if links_created + existing_links_total >= MAX_LINKS_PER_FILE:
            break
        # contenu textuel courant
        fragment = html[cs:ce]
        new_fragment = fragment
        # Wraps déjà appliqués dans CE conteneur (pour pas répéter le même
        # terme dans le même paragraphe)
        used_in_container: set[str] = set()
        # Ancres déjà ciblées depuis CE conteneur (1 seul lien par ancre)
        anchors_used_in_container: set[str] = set()
        # Pré-charge les liens et ancres déjà présents dans le fragment
        # pour préserver l'idempotence d'un re-run.
        for prev_a in re.finditer(
            r'<a\s+class="intra-ref"\s+href="#([^"]*)">([^<]*)</a>',
            fragment, re.IGNORECASE,
        ):
            anchors_used_in_container.add(prev_a.group(1))
            used_in_container.add(normalize_for_match(prev_a.group(2), lang))
        in_container = len(anchors_used_in_container)
        modified = False

        # 5a. force links d'abord
        for term, target in force_links:
            tn = normalize_for_match(term, lang)
            if tn in used_in_container:
                continue
            if target in anchors_used_in_container:
                continue
            updated, ok = wrap_in_fragment(new_fragment, term, target, lang)
            if ok:
                used_in_container.add(tn)
                anchors_used_in_container.add(target)
                new_fragment = updated
                modified = True
                in_container += 1
                links_created += 1
                top_terms[tn] += 1
                if len(examples) < 5:
                    examples.append((term, target))
                if in_container >= MAX_LINKS_PER_CONTAINER:
                    break

        # 5b. termes auto : termes longs d'abord, puis tokens isolés
        for tn in term_keys_sorted:
            if in_container >= MAX_LINKS_PER_CONTAINER:
                break
            if links_created >= MAX_LINKS_PER_FILE:
                break
            if tn in used_in_container:
                continue
            # Cherche la 1re ancre située APRÈS le conteneur, avec une
            # distance minimum (sinon le lien ne sert à rien)
            target_id = None
            for aid, ap, _orig in term_index[tn]:
                if ap >= c_end + MIN_DOM_DISTANCE:
                    target_id = aid
                    break
            if not target_id:
                continue
            if target_id in anchors_used_in_container:
                # Déjà un lien vers cette ancre depuis ce conteneur
                continue
            # Récupère un original de référence (casse / nikud)
            term_text = term_originals[tn]
            updated, ok = wrap_in_fragment(new_fragment, term_text,
                                           target_id, lang)
            if ok:
                used_in_container.add(tn)
                anchors_used_in_container.add(target_id)
                new_fragment = updated
                modified = True
                in_container += 1
                links_created += 1
                top_terms[tn] += 1
                if len(examples) < 5:
                    examples.append((term_text, target_id))

        if modified:
            edits.append((cs, ce, new_fragment))

    # Applique les éditions en ordre inverse
    for cs, ce, new_content in sorted(edits, key=lambda x: -x[0]):
        html = html[:cs] + new_content + html[ce:]

    # --- 6. Injecte les assets CSS/JS (si on a au moins une ancre utile)
    css_added = js_added = False
    if anchor_records:
        html, css_added, js_added = inject_assets(html)

    if not dry_run and (links_created > 0 or css_added or js_added or inserts):
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    return {
        "path": path,
        "lang": lang,
        "anchors_total": len(anchor_records),
        "anchors_with_ids_added": len(inserts),
        "links_created": links_created,
        "css_added": css_added,
        "js_added": js_added,
        "examples": examples,
        "top_terms": top_terms,
    }


# ---------------------------------------------------------------------------
# Découverte des fichiers à traiter
# ---------------------------------------------------------------------------


def files_for_siman(siman: int, niveau: int | None = None,
                    lang: str | None = None) -> list[str]:
    d = os.path.join(SOURCES_ROOT, f"siman-{siman}")
    if not os.path.isdir(d):
        return []
    out = []
    langs = [lang] if lang else ["fr", "he", "en"]
    if niveau is None:
        # Index pages + tous les niveaux disponibles
        for lg in langs:
            suf = LANG_SUFFIX[lg]
            p = os.path.join(d, f"index{suf}.html")
            if os.path.exists(p):
                out.append(p)
        for lv in (1, 2, 3, 4):
            if lv == 4 and siman in NO_LEVEL_4:
                continue
            stem = LEVEL_STEMS[lv]
            for lg in langs:
                suf = LANG_SUFFIX[lg]
                p = os.path.join(d, f"{stem}{suf}.html")
                if os.path.exists(p):
                    out.append(p)
    else:
        if niveau == 4 and siman in NO_LEVEL_4:
            return []
        stem = LEVEL_STEMS[niveau]
        for lg in langs:
            suf = LANG_SUFFIX[lg]
            p = os.path.join(d, f"{stem}{suf}.html")
            if os.path.exists(p):
                out.append(p)
    return out


def all_files() -> list[tuple[int, str]]:
    out = []
    for n in range(FIRST_SIMAN, LAST_SIMAN + 1):
        for p in files_for_siman(n):
            out.append((n, p))
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(
        description="Ajoute des liens d'ancrage intra-page DAAT.",
    )
    ap.add_argument("--siman", type=int, default=None,
                    help="Limite à un siman précis (242-365).")
    ap.add_argument("--niveau", type=int, choices=[1, 2, 3, 4], default=None)
    ap.add_argument("--lang", choices=["fr", "he", "en"], default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Affiche ce qui serait fait, n'écrit rien.")
    ap.add_argument("--stats", action="store_true",
                    help="Affiche un résumé des liens créés par fichier.")
    ap.add_argument("--remove", action="store_true",
                    help="Retire tous les <a.intra-ref> (rollback).")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    overrides = load_overrides()

    if args.siman is not None:
        targets = [(args.siman, p)
                   for p in files_for_siman(args.siman,
                                            niveau=args.niveau,
                                            lang=args.lang)]
    else:
        targets = all_files()

    if not targets:
        print("Aucun fichier ciblé.", file=sys.stderr)
        return 1

    if args.remove:
        total = 0
        files_touched = 0
        for siman, path in targets:
            with open(path, encoding="utf-8") as f:
                html = f.read()
            new_html, n = remove_intra_links(html)
            if n or new_html != html:
                files_touched += 1
                total += n
                if not args.dry_run:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_html)
        print(f"[remove] {total} liens retirés sur {files_touched} fichiers"
              + (" (dry-run)" if args.dry_run else ""))
        return 0

    grand_total_links = 0
    grand_total_anchors = 0
    grand_total_files = 0
    grand_top_terms: Counter = Counter()
    per_file: list[dict] = []

    for siman, path in targets:
        res = process_file(path, overrides,
                           siman=siman,
                           dry_run=args.dry_run,
                           stats_only=args.stats)
        per_file.append(res)
        grand_total_links += res["links_created"]
        grand_total_anchors += res["anchors_total"]
        grand_total_files += 1
        grand_top_terms.update(res["top_terms"])
        if not args.quiet:
            rel = os.path.relpath(path, REPO_ROOT)
            print(f"  {rel}  "
                  f"anchors={res['anchors_total']:>3}  "
                  f"links={res['links_created']:>3}  "
                  f"+css={int(res['css_added'])}  "
                  f"+js={int(res['js_added'])}")
            if args.stats and res["examples"]:
                for term, aid in res["examples"]:
                    short = term if len(term) < 40 else term[:40] + "…"
                    print(f"      • {short!r:42s} → #{aid}")

    print()
    print("=== Résumé ===")
    print(f"Fichiers traités   : {grand_total_files}")
    print(f"Ancres détectées   : {grand_total_anchors}")
    print(f"Liens créés        : {grand_total_links}"
          + (" (dry-run)" if args.dry_run else ""))
    if args.stats:
        print("Top 10 termes les plus liés :")
        for term, n in grand_top_terms.most_common(10):
            print(f"  {n:>4}  {term}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
