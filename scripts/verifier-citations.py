#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier-citations.py — confronte chaque citation hébraïque « verbatim » du site
à sa source réelle sur Sefaria.

Le gate structurel (audit-simanim.py) ne regarde que la forme des pages : il passe
à 174/174 sur une page truffée de citations inventées. Ce script est le gate de
*contenu* correspondant.

Principe
--------
1. Extraire de chaque page les fragments hébreux présentés comme des citations :
   <blockquote>, ou texte entre guillemets « … » / " … ". La classe `he-q` n'en
   fait pas partie — c'est une classe typographique (RTL + police hébraïque),
   appliquée aussi bien à une citation qu'à la thèse propre de l'auteur.
   Est « présenté comme une citation » ce que précède une formule d'annonce
   (תניא, וז״ל, כלשון…) **ou une référence nommée** — « רמב״ם (הלכות תפלה פי״ב
   הי״ג) — "…" ». Nommer sa source revendique le littéral au moins autant qu'une
   formule ; tant que ce second cas manquait, ces citations n'étaient pas
   seulement non résolues, elles n'étaient pas extraites.
2. Résoudre la référence qui les accompagne (daf talmudique — guemara, Rachi ou
   Tossefot —, séif du Choulhan Aroukh, ס״ק de la Michna Beroura, perek/halakha du
   Mishné Torah) en référence Sefaria canonique.
3. Récupérer le texte réel et comparer après normalisation (nikoud, ponctuation,
   guillemets, noms divins, orthographes pleine/défective).

Verdicts
--------
  OK           la citation figure telle quelle dans la source
  VARIANTE     très proche (≥ SEUIL_VARIANTE) — écart orthographique ou coupe
  REF_FAUSSE   le texte existe bien, mais pas là où la page le situe (la vraie
               référence est indiquée) — corriger le renvoi
  INTROUVABLE  absent de la source citée *et* du reste de Sefaria — citation
               vraisemblablement fabriquée, à réécrire
  NON_RESOLU   référence non reconnue ou source indisponible

Un fragment de moins de MIN_CITATION lettres n'est pas jugé : entre guillemets,
« תשמישי קדושה » ou « אמירה לנכרי שבות » sont des termes techniques, pas des
citations, et rien n'oblige à les retrouver mot pour mot dans la source voisine.

Usage
-----
  python3 scripts/verifier-citations.py                    # tout le site, FR
  python3 scripts/verifier-citations.py --langues fr,he,en
  python3 scripts/verifier-citations.py --path sources/shabbat/siman-297
  python3 scripts/verifier-citations.py --only-absent      # n'affiche que REF_FAUSSE / INTROUVABLE
  python3 scripts/verifier-citations.py --csv audit/citations-verifiees.csv

Sort non-zéro s'il reste des REF_FAUSSE ou des INTROUVABLE (utilisable comme gate CI).
Le cache disque (scripts/.cache-sefaria/) rend les passages suivants instantanés.
"""

import argparse
import difflib
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'scripts', '.cache-sefaria')

SEUIL_VARIANTE = 0.86   # ratio difflib au-dessus duquel on parle de variante et non d'absence
MIN_LETTRES = 12        # en deçà, un fragment est trop court pour conclure quoi que ce soit
# Une vraie citation est une phrase. En deçà de ce seuil on a affaire à un terme
# technique mis entre guillemets par l'auteur (« תשמישי קדושה », « אמירה לנכרי שבות »),
# que rien n'oblige à figurer mot pour mot dans la source voisine.
MIN_CITATION = 25
# La référence doit se trouver au voisinage de la citation, pas n'importe où sur la ligne.
FENETRE_REF = 200


# ─────────────────────────────── Sefaria ───────────────────────────────

def _get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == tries - 1:
                return {'error': str(e)}
            time.sleep(2 * (i + 1))


def _echec(data):
    """Une réponse d'erreur réseau, pas un verdict sur le texte."""
    return isinstance(data, dict) and set(data) == {'error'}


def _cached(key, produce):
    """Cache disque — mais JAMAIS une erreur réseau.

    Un 503/504 de Sefaria mis en cache se comporte ensuite comme un verdict :
    le daf devient introuvable pour toutes les exécutions suivantes, et des
    citations parfaitement exactes ressortent INTROUVABLE ou NON_RESOLU. C'est
    arrivé — 36 entrées d'erreur figées empoisonnaient Berakhot 59a pour tout
    le dépôt. On relit donc l'erreur à chaque fois plutôt que de la mémoriser,
    et une entrée d'erreur déjà présente est purgée à la lecture.
    """
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, hashlib.sha1(key.encode()).hexdigest()[:20] + '.json')
    if os.path.exists(path):
        try:
            data = json.load(open(path, encoding='utf-8'))
        except Exception:
            os.remove(path)
        else:
            if not _echec(data):
                return data
            os.remove(path)   # entrée empoisonnée héritée d'une exécution précédente
    data = produce()
    if not _echec(data):
        json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    return data


def hebrew_versions(book):
    """Titres de toutes les éditions hébraïques d'un ouvrage.

    Indispensable : Sefaria sert par défaut l'édition Davidson du Talmud, dont le
    texte diffère par endroits du Vilna imprimé auquel se réfèrent les pages du site
    (ברכות ג׳ ע״א : « אוי שהחרבתי » chez Davidson, « אוי לבנים שבעונותיהם החרבתי »
    dans le Vilna/Wikisource). Comparer à une seule édition fabrique des faux positifs.
    """
    data = _cached('versions::' + book, lambda: _get(
        'https://www.sefaria.org/api/texts/versions/' + urllib.parse.quote(book, safe=',._-')))
    if not isinstance(data, list):
        return []
    return [v['versionTitle'] for v in data
            if v.get('language') == 'he' and v.get('versionTitle')]


def locate(frag):
    """Où ce texte se trouve-t-il réellement dans Sefaria ? (recherche exacte)

    Permet de distinguer les deux cas que « absent de la source citée » recouvre :
    une citation *fabriquée* (introuvable nulle part) et une citation *exacte
    rattachée à la mauvaise référence* — qui appellent des corrections différentes.
    """
    q = re.sub(r'\s+', ' ', re.sub(r'[«»"„”\[\]]', '', frag)).strip()
    q = max((p.strip() for p in re.split(r'…|\.\.\.', q)), key=len)[:180]
    if n_letters(q) < MIN_CITATION:
        return []

    def ask():
        body = json.dumps({'query': q, 'type': 'text', 'field': 'exact', 'size': 4}).encode()
        req = urllib.request.Request('https://www.sefaria.org/api/search-wrapper',
                                     data=body, headers={'Content-Type': 'application/json'})
        for i in range(3):
            try:
                with urllib.request.urlopen(req, timeout=45) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                if i == 2:
                    return {'error': str(e)}
                time.sleep(2 * (i + 1))

    data = _cached('search::' + q, ask)
    if not isinstance(data, dict) or 'error' in data:
        return []
    out = []
    for h in data.get('hits', {}).get('hits', []):
        ref = re.sub(r'\s*\(.*$', '', h.get('_id', ''))
        if ref:
            out.append(ref)
    return out


def hebrew_title(book):
    """Titres hébreux d'un ouvrage Sefaria (« Job » → [« איוב »])."""
    data = _cached('index::' + book, lambda: _get(
        'https://www.sefaria.org/api/v2/index/' + urllib.parse.quote(book, safe=',._-')))
    if not isinstance(data, dict):
        return []
    return [x for x in ([data.get('heTitle')] + (data.get('heTitleVariants') or [])) if x]


def bien_attribuee(frag, window):
    """La page situe-t-elle correctement ce texte, dans un ouvrage que le
    résolveur de références ne sait pas lire ?

    Le résolveur couvre le Talmud, le Choulhan Aroukh et la Michna Beroura ; il
    ignore le Tanakh et les nossei kelim. Un verset correctement attribué — « ועליו
    נאמר \'לאחז בכנפות הארץ\' (איוב ל״ח) » — se retrouvait donc confronté au daf cité
    à côté. On demande à Sefaria où le texte se trouve réellement, et si le nom de
    cet ouvrage figure au voisinage de la citation, l'attribution de la page est juste.
    """
    for ref in locate(frag):
        book = re.split(r'\s+\d|:', ref)[0].strip()
        if any(he in window for he in hebrew_title(book)):
            return ref
        if book and book.lower() in window.lower():
            return ref
    return ''


def _flat(x, out):
    if isinstance(x, str):
        out.append(x)
    elif isinstance(x, list):
        for y in x:
            _flat(y, out)
    return out


def fetch(ref):
    """Segments hébreux d'une référence Sefaria, **toutes éditions hébraïques réunies**."""
    book = re.split(r'[.]\d|[.][א-ת]', ref)[0].replace('_', ' ')
    titles = hebrew_versions(book)
    qs = '?return_format=text_only&version=hebrew'
    for t in titles[:6]:
        qs += '&version=' + urllib.parse.quote('hebrew|' + t)
    data = _cached(ref + '::multi', lambda: _get(
        'https://www.sefaria.org/api/v3/texts/' + urllib.parse.quote(ref, safe=',._-') + qs))
    if not isinstance(data, dict) or 'error' in data:
        return None
    segs = []
    for v in data.get('versions') or []:
        if v.get('language') == 'he':
            segs += _flat(v.get('text'), [])
    return segs or None


# ─────────────────────────── Normalisation hébraïque ───────────────────────────

NIKUD = re.compile(r'[֑-ׇ]')
NONHEB = re.compile(r'[^א-ת]')

# Abréviations développées avant comparaison : les pages écrivent « הקב״ה » là
# où l'édition Sefaria imprime « הקדוש ברוך הוא ».
#
# Les trois graphies du gershayim doivent être couvertes : ״ (U+05F4) que le
# site emploie, " (ASCII) que Sefaria imprime, et ׳׳ (deux geresh). Elles
# étaient auparavant listées à la main, et plusieurs sigles n'existaient qu'en
# U+05F4 — une citation exacte contenant « כ"ש » ou « ר"ל » tel que Sefaria
# l'imprime ressortait alors en VARIANTE. On dérive donc les variantes.
_ABBREV_BASE = [
    ('הקב״ה', 'הקדוש ברוך הוא'),
    ('ת״ר', 'תנו רבנן'),
    ('ב״ש', 'בית שמאי'),
    ('ב״ה', 'בית הלל'),
    ('רשב״י', 'רבי שמעון בר יוחאי'),
    ('ריב״ל', 'רבי יהושע בן לוי'),
    ('רנב״י', 'רב נחמן בר יצחק'),
    ('ר״ל', 'ריש לקיש'),
    ('אעפ״י', 'אף על פי'),
    ('אע״פ', 'אף על פי'),
    ('כ״ש', 'כל שכן'),
    ('ק״ו', 'קל וחומר'),
    ('אא״כ', 'אלא אם כן'),
]


def _graphies(sigle):
    """Les trois écritures d'un sigle : ״ (U+05F4), " (ASCII), ׳׳ (deux geresh)."""
    return [sigle, sigle.replace('\u05f4', '"'), sigle.replace('\u05f4', '\u05f3\u05f3')]


_ABBREV = [(g, dev) for sig, dev in _ABBREV_BASE for g in dict.fromkeys(_graphies(sig))]
_ABBREV += [('ה\u05f3', 'ה'), ("ה'", 'ה')]

# Variantes graphiques qui ne changent pas le texte
_SUBS = [
    ('אלהים', 'אלקים'), ('אלוקים', 'אלקים'),
    ('ירושלים', 'ירושלם'),
]
# Le Tétragramme doit être borné par des non-lettres. Appliqué sans borne et APRÈS
# suppression des espaces, il mutilait des citations exactes : « …אָסוּר בַּהֲנָיָה.
# וְהַשּׁוֹתֶה… » se réduisait à `בהניהוהשותה`, où la suite `יהוה` naît de la seule
# soudure de deux mots — et la citation, amputée, était déclarée absente de sa
# source. N'importe quel « …יה ו… » produisait le même faux négatif : 98 citations
# du site sont dans ce cas.
_TETRA = re.compile(r'(?<![א-ת])יהוה(?![א-ת])')


def norm(s):
    """Réduit un texte hébreu à ses seules consonnes, pour comparaison."""
    s = html.unescape(s)
    for a, b in _ABBREV:
        s = s.replace(a, b)
    s = NIKUD.sub('', s)
    # tant que les espaces sont là, les frontières de mots ont encore un sens
    s = _TETRA.sub('ה', s)
    for a, b in _SUBS:
        s = s.replace(a, b)
    return NONHEB.sub('', s)


def n_letters(s):
    return len(NONHEB.sub('', NIKUD.sub('', s)))


# ─────────────────────────── Résolution des références ───────────────────────────

GEMATRIA = {'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
            'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200,
            'ש': 300, 'ת': 400}


def gem(s):
    """Valeur d'un nombre écrit en lettres hébraïques, ou None si ce n'en est pas un.

    Le contrôle de forme est indispensable : sans lui, « ספק ברכות להקל » se lit
    « Berakhot » + gematria(להקל)=165, et l'outil part chercher un folio 165 dans un
    traité qui en compte 64. Un numéral hébreu s'écrit par valeurs décroissantes
    (ק־י־ז), ce que « להקל » (30-5-100-30) ne respecte pas.
    """
    s = re.sub(r'["\'״׳]', '', s)
    if not s or len(s) > 3 or any(c not in GEMATRIA for c in s):
        return None
    vals = [GEMATRIA[c] for c in s]
    if vals in ([10, 6], [10, 7]):        # ט״ו / ט״ז s'écrivent ainsi par convention
        return sum(vals)
    if any(a < b for a, b in zip(vals, vals[1:])):
        return None
    return sum(vals)


MASSEKHTOT = {
    'שבת': 'Shabbat', 'ברכות': 'Berakhot', 'פסחים': 'Pesachim', 'עירובין': 'Eruvin',
    'ביצה': 'Beitzah', 'מנחות': 'Menachot', 'חולין': 'Chullin', 'יבמות': 'Yevamot',
    'נדה': 'Niddah', 'סוכה': 'Sukkah', 'מגילה': 'Megillah', 'תענית': 'Taanit',
    'יומא': 'Yoma', 'סנהדרין': 'Sanhedrin', 'כתובות': 'Ketubot', 'גיטין': 'Gittin',
    'קידושין': 'Kiddushin', 'קדושין': 'Kiddushin', 'בבא קמא': 'Bava Kamma',
    'בבא מציעא': 'Bava Metzia', 'בבא בתרא': 'Bava Batra', 'מועד קטן': 'Moed Katan',
    'ראש השנה': 'Rosh Hashanah', 'עבודה זרה': 'Avodah Zarah', 'סוטה': 'Sotah',
    'נדרים': 'Nedarim', 'שבועות': 'Shevuot', 'זבחים': 'Zevachim', 'בכורות': 'Bekhorot',
    'ערכין': 'Arakhin', 'תמורה': 'Temurah', 'כריתות': 'Keritot', 'מכות': 'Makkot',
    'הוריות': 'Horayot', 'חגיגה': 'Chagigah', 'פסחים ': 'Pesachim',
    # translittérations françaises / anglaises rencontrées dans les pages
    'chabbat': 'Shabbat', 'shabbat': 'Shabbat', 'berakhot': 'Berakhot',
    'berachot': 'Berakhot', 'pesachim': 'Pesachim', 'pessahim': 'Pesachim',
    'menachot': 'Menachot', 'menahot': 'Menachot', 'houlin': 'Chullin',
    'chullin': 'Chullin', 'yevamot': 'Yevamot', 'beitzah': 'Beitzah',
    'beitsa': 'Beitzah', 'eruvin': 'Eruvin', 'erouvin': 'Eruvin',
    'moed katan': 'Moed Katan', 'niddah': 'Niddah', 'nidda': 'Niddah',
}

TOURIM = {'או״ח': 'Orach Chayim', 'אורח חיים': 'Orach Chayim', 'oh': 'Orach Chayim',
          'oc': 'Orach Chayim', 'orah haim': 'Orach Chayim',
          'יו״ד': 'Yoreh Deah', 'יורה דעה': 'Yoreh Deah', 'yd': 'Yoreh Deah',
          'אה״ע': 'Even HaEzer', 'חו״מ': 'Choshen Mishpat'}

# daf : « קי״ז ע״ב », « מ״ג: », « לד ע״א », « 43b », « 117b »
RE_DAF_HE = re.compile(
    r'(?P<mass>' + '|'.join(sorted((k for k in MASSEKHTOT if re.search(r'[א-ת]', k)),
                                   key=len, reverse=True)) + r')'
    r'[\s‏]*\(?[\s]*'
    r'(?P<daf>[א-ת]{1,4}["״\'׳]?[א-ת]?)'
    # L'amoud ne doit pas etre suivi d'une lettre hebraique : sans cette garde, le
    # « עב » de « העבודה » se lisait comme « ע״ב ». Au siman 120, « בקשת השבת
    # העבודה » rendait Shabbat.5b — ה = 5, עב = amoud ב — et la page, qui citait le
    # texte de la tefila sans pretendre a aucune source, ressortait en REF_FAUSSE
    # contre un folio tire de sa propre prose.
    r'[\s]*(?:(?P<amud>ע["״]?[אב])(?![א-ת])|(?P<colon>[.:]))')
RE_DAF_LAT = re.compile(
    r'\b(?P<mass>' + '|'.join(sorted((k for k in MASSEKHTOT if not re.search(r'[א-ת]', k)),
                                     key=len, reverse=True)) + r')\b'
    r'[\s,]*\(?(?P<num>\d{1,3})\s*(?P<ab>[ab.:])', re.I)
# Choulhan Aroukh : « OH 131:1 », « או״ח קל״א:א », « שו״ע י:א », « YD 89:1 »
# « SAR OH 273:6 » est le Choulhan Aroukh HARAV, pas le Choulhan Aroukh. Sans ce
# garde, le siman 273 — qui donne la bonne reference — sortait en REF_FAUSSE
# contre le seif du Mehaber, qui porte tout autre chose.
RE_SA_LAT = re.compile(r'(?<![A-Za-z])(?<!SAR )(?<!SAH )(?<!Rav )(?P<tour>OH|OC|YD|EH|CM)\s*(?P<siman>\d{1,3})\s*:\s*(?P<seif>\d{1,3})', re.I)
# Le groupe `seif` doit accepter le gershayim : sans lui, « ק״כ:ט״ז » s'arrêtait à
# `ט` et le seif 16 était lu comme le seif 9. Une référence juste ressortait alors en
# REF_FAUSSE, contre un seif qui n'avait rien à voir. Même défaut pour י״ב lu 10,
# כ״ו lu 20, etc. — soit tous les seifim à deux lettres, c'est-à-dire la majorité.
RE_SA_HE = re.compile(r'(?P<tour>או["״]?ח|יו["״]?ד)\s*'
                      r'(?P<siman>[א-ת]{1,4}["״\'׳]?[א-ת]?)\s*[:׃]\s*'
                      r'(?P<seif>[א-ת]{1,3}["״\'׳]?[א-ת]?)')
# Michna Beroura : « MB 10:11 », « מ״ב י:יא », « ס״ק ג »
RE_MB = re.compile(r'(?:MB|מ["״]?ב)\s*(?P<siman>[\dא-ת"״\'׳]{1,5})\s*:\s*'
                   r'(?P<sk>[\dא-ת"״\'׳]{1,4})')


# ─────────────────────────────── Mishné Torah ───────────────────────────────
#
# Le résolveur savait lire un daf de guemara et un séif du Choulhan Aroukh, mais
# n'avait AUCUN motif pour le Rambam : une référence de la forme
# « (הלכות תפלה פי״ב הי״ג) » ne résolvait rien, et la citation qu'elle porte était
# rangée en « sans référence — non vérifiable automatiquement ». Le docstring
# promettait pourtant le Rambam depuis le début.
#
# C'est par ce trou qu'est passée, sur le siman 284, une clause entièrement
# fabriquée prêtée au Rambam — « וצריך שיהא הענין שמפטיר בו דומה למה שקרא בתורה »,
# absente de tout Sefaria — et sur laquelle la page appuyait sa remarque. Elle a
# été trouvée à la relecture, pas par ce script.
#
# La table est celle de Sefaria elle-même (api/index, 88 livres), pour qu'un
# titre ne soit jamais deviné.
HILKHOT_RAMBAM = {
    'ביכורים ושאר מתנות כהונה שבגבולין': 'First Fruits and other Gifts to Priests Outside the Sanctuary',
    'סנהדרין והעונשין המסורין להם': 'The Sanhedrin and the Penalties within Their Jurisdiction',
    'עבודה זרה וחוקות הגויים': 'Foreign Worship and Customs of the Nations',
    'תפילין ומזוזה וספר תורה': 'Tefillin, Mezuzah and the Torah Scroll',
    'כלי המקדש והעובדין בו': 'Vessels of the Sanctuary and Those Who Serve Therein',
    'מסירת תורה שבעל פה': 'Transmission of the Oral Law',
    'מעשר שני ונטע רבעי': "Second Tithes and Fourth Year's Fruit",
    'עבודת יום הכפורים': 'Service on the Day of Atonement',
    'תפילה וברכת כהנים': 'Prayer and the Priestly Blessing',
    'מטמאי משכב ומושב': 'Those Who Defile Bed or Seat',
    'שאר אבות הטומאות': 'Other Sources of Defilement',
    'שופר וסוכה ולולב': 'Shofar, Sukkah and Lulav',
    'רוצח ושמירת נפש': 'Murderer and the Preservation of Life',
    'פסולי המוקדשין': 'Sacrifices Rendered Unfit',
    'שלוחין ושותפין': 'Agents and Partners',
    'תמידים ומוספין': 'Daily Offerings and Additional Offerings',
    'מאכלות אסורות': 'Forbidden Foods',
    'מלכים ומלחמות': 'Kings and Wars',
    'מצוות לא תעשה': 'Negative Mitzvot',
    'שביתת יום טוב': 'Rest on a Holiday',
    'איסורי המזבח': 'Things Forbidden on the Altar',
    'גזילה ואבידה': 'Robbery and Lost Property',
    'טומאת אוכלים': 'Defilement of Foods',
    'מגילה וחנוכה': 'Scroll of Esther and Hanukkah',
    'מעשה הקרבנות': 'Sacrificial Procedure',
    'ערכים וחרמין': 'Appraisals and Devoted Property',
    'שאלה ופיקדון': 'Borrowing and Deposit',
    'איסורי ביאה': 'Forbidden Intercourse',
    'זכייה ומתנה': 'Ownerless Property and Gifts',
    'יבום וחליצה': 'Levirate Marriage and Release',
    'יסודי התורה': 'Foundations of the Torah',
    'מחוסרי כפרה': 'Offerings for Those with Incomplete Atonement',
    'מלווה ולווה': 'Creditor and Debtor',
    'מתנות עניים': 'Gifts to the Poor',
    'קידוש החודש': 'Sanctification of the New Month',
    'שמיטה ויובל': 'Sabbatical Year and the Jubilee',
    'תוכן החיבור': 'Overview of Mishneh Torah Contents',
    'בית הבחירה': 'The Chosen Temple',
    'חובל ומזיק': 'One Who Injures a Person or Property',
    'טומאת צרעת': 'Defilement by Leprosy',
    'טוען ונטען': 'Plaintiff and Defendant',
    'נערה בתולה': 'Virgin Maiden',
    'סדר התפילה': 'The Order of Prayer',
    'שביתת עשור': 'Rest on the Tenth of Tishrei',
    'תלמוד תורה': 'Torah Study',
    'ביאת מקדש': 'Admission into the Sanctuary',
    'מצוות עשה': 'Positive Mitzvot',
    'נזקי ממון': 'Damages to Property',
    'פרה אדומה': 'Red Heifer',
    'קריאת שמע': 'Reading the Shema',
    'חמץ ומצה': 'Leavened and Unleavened Bread',
    'טומאת מת': 'Defilement by a Corpse',
    'קרבן פסח': 'Paschal Offering',
    'גירושין': 'Divorce',
    'עירובין': 'Eruvin',
    'בכורות': 'Firstlings',
    'מעשרות': 'Tithes',
    'מקואות': 'Immersion Pools',
    'נזירות': 'Nazariteship',
    'שבועות': 'Oaths',
    'שכירות': 'Hiring',
    'תעניות': 'Fasts',
    'תרומות': 'Heave Offerings',
    'אישות': 'Marriage',
    'ברכות': 'Blessings',
    'גניבה': 'Theft',
    'חגיגה': 'Festival Offering',
    'כלאים': 'Diverse Species',
    'מכירה': 'Sales',
    'ממרים': 'Rebels',
    'מעילה': 'Trespass',
    'נדרים': 'Vows',
    'נחלות': 'Inheritances',
    'עבדים': 'Slaves',
    'ציצית': 'Fringes',
    'שגגות': 'Offerings for Unintentional Transgressions',
    'שחיטה': 'Ritual Slaughter',
    'שכנים': 'Neighbors',
    'שקלים': 'Sheqel Dues',
    'תמורה': 'Substitution',
    'תשובה': 'Repentance',
    'דעות': 'Human Dispositions',
    'כלים': 'Vessels',
    'מילה': 'Circumcision',
    'סוטה': 'Woman Suspected of Infidelity',
    'עדות': 'Testimony',
    'אבל': 'Mourning',
    'שבת': 'Sabbath',
}

# Le site n'écrit pas toujours le titre complet du livre : « הלכות תפלה » pour
# « הלכות תפילה וברכת כהנים », « הלכות תפילין » pour le livre qui couvre aussi la
# mezouza et le sefer Torah. Ces alias-là sont sûrs.
#
# Ce qui n'y figure PAS est délibéré : « הלכות נדה » n'est pas un livre du Mishné
# Torah (le Rambam traite la nidda dans הלכות איסורי ביאה) — sur ce site, c'est
# le Tour ou le Choulhan Aroukh ; « הלכות גדולות » et « הלכות קטנות » sont d'autres
# ouvrages entièrement ; « הלכות ברכות השחר », « הלכות קריאת התורה », « הלכות
# נטילת ידים » sont des intitulés du Tour / Choulhan Aroukh, pas du Rambam.
# Les faire pointer vers le Rambam produirait des REF_FAUSSE contre des pages
# justes — exactement le défaut que la seconde moitié de ce correctif répare.
ALIAS_RAMBAM = {
    'תפילה': 'תפילה וברכת כהנים', 'תפלה': 'תפילה וברכת כהנים',
    'תפילה ונשיאת כפים': 'תפילה וברכת כהנים',
    'תפלה ונשיאת כפים': 'תפילה וברכת כהנים',
    'תפילה וברכת כוהנים': 'תפילה וברכת כהנים',
    'תפילין': 'תפילין ומזוזה וספר תורה',
    'תפלין': 'תפילין ומזוזה וספר תורה',
    'מזוזה': 'תפילין ומזוזה וספר תורה',
    'ספר תורה': 'תפילין ומזוזה וספר תורה',
    'ציצית ועטיפתו': 'ציצית',
    'תמידין ומוספין': 'תמידים ומוספין',
    'מקוואות': 'מקואות',
    'שביתת יום טוב': 'שביתת יום טוב',
    'קריאת שמע': 'קריאת שמע', 'ק״ש': 'קריאת שמע',
}

# « הלכות תפלה פי״ב הי״ג », « הלכות שבת פרק ג׳ הלכה ה׳ », « הלכות ציצית פ״ג ».
# Le perek est obligatoire : sans lui, « הלכות ברכות » n'est pas une référence,
# c'est la locution courante « les lois des berakhot », qui revient 2745 fois sur
# le site et ne renvoie à rien de précis.
RE_RAMBAM = re.compile(
    r'הלכות\s+(?P<livre>[א-ת]+(?:\s+[א-ת]+){0,4}?)\s*'
    r'(?:פרק\s*(?P<perek1>[א-ת]{1,4}["״\'׳]?[א-ת]?)'
    r'|פ["״\'׳]?(?P<perek2>[א-ת]{1,3}["״\'׳]?[א-ת]?)'
    r'|(?P<perek3>[א-ת]{0,3}["״\'׳][א-ת]?)(?![א-ת]))'
    r'(?:\s*[,\s]\s*(?:הלכה\s*(?P<hal1>[א-ת]{1,4}["״\'׳]?[א-ת]?)'
    r'|ה["״\'׳]?(?P<hal2>[א-ת]{1,3}["״\'׳]?[א-ת]?)))?')

# Un titre de livre du Mishné Torah revendiqué comme tel : sans cette marque, une
# référence « הלכות שבת פרק ג הלכה ה » peut aussi bien viser le Tour. On n'exige la
# marque que lorsque la halakha manque — perek ET halakha ensemble sont la forme
# de citation propre au Mishné Torah.
RE_MARQUE_RAMBAM = re.compile(r'רמב["״]?ם|רמבם|Rambam|Ramba"m|Ma[ïi]monide|Mishneh\s+Torah', re.I)


# La table porte la graphie PLEINE de Sefaria (« הלכות מלווה ולווה »). Le Tour et
# le Beit Yossef écrivent la défective (« הלכות מלוה ולוה »), et une page qui les
# suit citait un livre que la table ne reconnaissait pas : la référence tombait
# alors en « sans référence », donc n'était jamais confrontée — silencieusement.
# Plutôt que d'énumérer les deux graphies de chaque titre, on compare sur un
# squelette où les doubles vav et yod sont réduits.
def _squelette_titre(nom):
    return nom.replace('וו', 'ו').replace('יי', 'י')


_RAMBAM_SQUELETTE = {_squelette_titre(k): v for k, v in HILKHOT_RAMBAM.items()}


def _livre_rambam(nom):
    """Le nom cité est-il un livre du Mishné Torah ? (titre exact ou alias sûr)"""
    nom = re.sub(r'\s+', ' ', nom.replace('״', '"').replace('׳', "'")).strip(' "\'')
    nom = ALIAS_RAMBAM.get(nom, nom)
    return HILKHOT_RAMBAM.get(nom) or _RAMBAM_SQUELETTE.get(_squelette_titre(nom))


# « משנה סוטה ז׳:א » n'est PAS le folio 7b. Le motif de daf lisait le geresh puis
# les deux-points comme un amoud, et rendait Sotah.7b : le siman 185 citait
# correctement « אלו נאמרין בכל לשון … וברכת המזון » de la Michna Sotah ז׳:א —
# verbatim, reference juste — et ressortait trois fois en INTROUVABLE contre un
# folio qui n'a rien a voir. C'est la pire espece de signalement : celui qui
# envoie corriger une page qui a raison.
RE_MISHNAH = re.compile(
    r'(?:משנה|מתני[\'׳])\s+(?P<mass>' +
    '|'.join(sorted((k for k in MASSEKHTOT if re.search(r'[א-ת]', k)), key=len, reverse=True)) +
    r')\s*(?P<perek>[א-ת]{1,4}["״\'׳]?[א-ת]?)\s*[:׃]\s*(?P<mish>[א-ת]{1,3}["״\'׳]?[א-ת]?)')
# Un daf precede de « משנה » / « מתני׳ » n'est pas un daf.
RE_AVANT_MISHNAH = re.compile(r'(?:משנה|מתני[\'׳])\s+[א-ת\s]{0,14}$')


def _num(tok):
    """Un jeton numérique, chiffres arabes ou lettres hébraïques."""
    tok = tok.strip()
    if re.fullmatch(r'\d+', tok):
        return int(tok)
    return gem(tok)


SENTINELLE = '\x00'


def fenetre_ref(plain, at, n):
    """Contexte d'une citation, borné par les citations voisines.

    La fenêtre symétrique de ``FENETRE_REF`` caractères était trop large : sur
    une ligne portant deux citations — « כל הטמאים קורין בתורה » … puis
    « דברי תורה אינן מקבלין טומאה » (ברכות כ״ב.) — le daf de la seconde était
    attribué à la première, qui n'en avait aucun, et la première ressortait en
    REF_FAUSSE. Un sondage sur cinq cas en a montré trois de cette espèce.

    Une référence appartient à la citation qu'elle jouxte : on arrête donc la
    fenêtre avant la citation suivante (``«``) et après la précédente (``»``).
    """
    fin = at + n
    apres = plain[fin:fin + FENETRE_REF]
    if apres.startswith('»'):
        apres = apres[1:]
    coupe = apres.find('«')
    if coupe >= 0:
        apres = apres[:coupe]

    avant = plain[max(0, at - FENETRE_REF):at]
    if avant.endswith('«'):
        avant = avant[:-1]
    coupe = avant.rfind('»')
    if coupe >= 0:
        avant = avant[coupe + 1:]
        # La citation précédente porte sa référence APRÈS son guillemet fermant :
        # « … » (מ״ב רכ״ז:יב). Couper au « » » la laissait dans notre fenêtre, et
        # une citation dont la référence suit — le cas ordinaire ici — se voyait
        # attribuer celle de sa voisine. Vu sur le siman 227 : le Taz, cité
        # « … » (ט״ז או״ח רכ״ז), héritait du מ״ב de la citation précédente et
        # sortait en REF_FAUSSE alors que la page était juste.
        avant = re.sub(r'^\s*\([^()]*\)', '', avant)

    # Le garde ci-dessus ne se déclenche que si la fenêtre COMMENCE par « ( ».
    # Quand la citation précédente est hors de portée des 200 caractères, la
    # fenêtre s'ouvre au MILIEU de sa parenthèse de référence, et celle-ci était
    # alors attribuée à notre citation. Une parenthèse fermante rencontrée avant
    # toute ouvrante appartient nécessairement à ce qui précède la fenêtre : on
    # coupe jusqu'à elle. Vu au siman 127, où une citation du Chakh, exacte et
    # correctement référencée, héritait du « (שו״ע יו״ד קכ״ז:א) » de sa voisine.
    ouvre, ferme = avant.find('('), avant.find(')')
    if ferme >= 0 and (ouvre < 0 or ferme < ouvre):
        avant = avant[ferme + 1:]

    # Le texte de la citation lui-même est EXCLU : une citation peut mentionner un
    # siman dans ses propres mots — le Chakh écrit « צ״ע … דמה שהוציא הב״י בסימן
    # קכ״ד מהרמב״ם » — et ce siman n'est pas la référence de la citation, c'est son
    # contenu. Résolue depuis l'intérieur du verbatim, la citation était confrontée
    # au Chakh du siman 124 au lieu du 125, et déclarée introuvable alors que la
    # page portait la bonne référence juste à côté.
    # Le séparateur est un sentinelle : la référence d'une citation suit la citation
    # (« … » (ש״ך … ס״ק ל)), et les consommateurs doivent pouvoir préférer ce qui la
    # suit à ce qui la précède quand une ligne porte plusieurs citations.
    return avant + SENTINELLE + apres


# Un commentaire du daf est un TEXTE DISTINCT de la guemara. « תוספות עבודה זרה
# ע״ה ע״ב ד״ה … » citait pourtant, jusqu'ici, le folio de guemara : le texte des
# Tossefot n'y figurant évidemment pas, toute citation de Tossefot correctement
# référencée ressortait en REF_FAUSSE. Quatre l'ont fait sur le seul siman 120, et
# deux agents successifs ont été renvoyés « corriger » du verbatim exact.
COMMENTATEURS = [
    # « תוספות על עבודה זרה » est aussi correct que « תוספות עבודה זרה » : le
    # « על » optionnel évite que la forme la plus naturelle en hébreu casse
    # silencieusement le résolveur et fasse ressortir du verbatim en VARIANTE.
    (re.compile(r'(?:תוספות|תוס[\'׳])\s*(?:על\s*)?$'), 'Tosafot_on_'),
    (re.compile(r'(?:רש["״]י)\s*(?:על\s*)?$'),          'Rashi_on_'),
    # Le Roch et le Mordekhi s'indexent en perek:siman, pas en daf : aucune
    # référence ne peut être construite depuis un folio. Ils reçoivent None —
    # la citation retombe en « sans référence », donc NON JUGÉE, au lieu d'être
    # confrontée au folio de guemara homonyme et déclarée fausse.
    # Ne rien dire vaut mieux que dire faux.
    (re.compile(r'(?:הרא["״]ש|רא["״]ש)\s*(?:על\s*)?$'), None),
    (re.compile(r'(?:המרדכי|מרדכי)\s*(?:על\s*)?$'),      None),
    # Les Richonim paginés comme leur support : le Rif et le Ran sur les pages du
    # Rif, le Rachba et le Ritva sur celles de la guemara. Sans eux, « רי״ף עבודה
    # זרה ל״ד ע״ב » était confronté au folio de guemara homonyme — même défaut que
    # pour les Tossefot. Les quatre slugs ont été vérifiés contre l'API.
    (re.compile(r'(?:רי["״]ף)\s*(?:על\s*)?$'),          'Rif_'),
    (re.compile(r'(?:הר["״]ן|ר["״]ן)\s*(?:על\s*)?$'),   'Ran_on_'),
    (re.compile(r'(?:הרשב["״]א|רשב["״]א)\s*(?:על\s*)?$'), 'Rashba_on_'),
    (re.compile(r'(?:הריטב["״]א|ריטב["״]א)\s*(?:על\s*)?$'), 'Ritva_on_'),
]


def _prefixe_commentateur(ctx, debut):
    """Le nom d'un commentateur précède-t-il immédiatement la référence de daf ?"""
    avant = ctx[max(0, debut - 24):debut]
    for rx, prefixe in COMMENTATEURS:
        if rx.search(avant):
            return prefixe          # peut valoir None : « ne pas construire de référence »
    return ''


# Le Roch, au niveau du PEREK. Son second niveau sur Sefaria ne coïncide pas
# toujours avec le numéro de siman imprimé (פ״ד de עבודה זרה : 7/12/20 là où les
# pages citent ט״ו/כ׳/ל״ג) — construire « Rosh_on_X.perek.siman » dirait donc
# parfois faux. Le perek entier, lui, est sûr : la citation y est cherchée parmi
# tous ses segments. Les 24 traités ci-dessous ont été vérifiés contre l'API ; les
# noms de perek ne sont tabulés que pour les traités que les pages citent ainsi.
ROSH_TRAITES = {'Avodah_Zarah', 'Gittin', 'Chullin', 'Pesachim', 'Shabbat', 'Berakhot',
                'Bava_Kamma', 'Bava_Metzia', 'Bava_Batra', 'Ketubot', 'Kiddushin',
                'Yevamot', 'Nedarim', 'Beitzah', 'Megillah', 'Rosh_Hashanah', 'Sukkah',
                'Taanit', 'Moed_Katan', 'Niddah', 'Bekhorot', 'Eruvin', 'Sanhedrin',
                'Makkot'}
ROSH_PERAKIM = {
    'Avodah_Zarah': {'לפני אידיהן': 1, 'אין מעמידין': 2, 'כל הצלמים': 3,
                     'רבי ישמעאל': 4, 'ר׳ ישמעאל': 4, 'השוכר את הפועל': 5, 'השוכר': 5},
    'Gittin': {'המביא גט': 1, 'המביא ראשון': 1, 'המביא שני': 2, 'כל הגט': 3, 'השולח': 4,
               'הניזקין': 5, 'האומר': 6, 'מי שאחזו': 7, 'הזורק': 8, 'המגרש': 9},
}
RE_ROSH = re.compile(
    r'(?:ה?רא["״]ש)\s*(?:על\s*)?(?:מסכת\s*)?(?P<mass>[א-ת ]{3,20}?)\s*,?\s*'
    r'פרק\s*(?P<perek>[א-ת]{1,3}["״׳\']?(?![א-ת])|[א-ת ׳]{3,24}?)\s*,?\s*(?=סימן|סי[׳\'])')


def refs_rosh(ctx):
    """« רא״ש על עבודה זרה פרק ד׳ סימן ט״ו » → Rosh_on_Avodah_Zarah.4 (perek entier)."""
    out = []
    for m in RE_ROSH.finditer(ctx):
        nom = m.group('mass').strip()
        livre = (MASSEKHTOT.get(nom) or '').replace(' ', '_')   # « Avodah Zarah » → slug
        if not livre or livre not in ROSH_TRAITES:
            continue
        pk = m.group('perek').strip()
        n = _num(pk) if re.fullmatch(r'[א-ת]{1,3}["״׳\']?', pk) else ROSH_PERAKIM.get(livre, {}).get(pk)
        if n:
            out.append(f"Rosh_on_{livre}.{n}")
    return out


def refs_in(ctx):
    """Toutes les références Sefaria détectées dans un contexte textuel."""
    out = []
    for m in RE_PASSOUK.finditer(ctx):
        ch, v = _num(m.group('ch')), _num(m.group('v'))
        if ch and v:
            out.append(f"{TANAKH[m.group('livre')]}.{ch}.{v}")
    out += refs_rosh(ctx)
    for m in RE_PEREK_MISHNAH.finditer(ctx):
        pe, mi = _num(m.group('p')), _num(m.group('m'))
        if pe and mi:
            livre = MISHNAYOT[m.group('mass')]
            out.append(f"{livre}.{pe}.{mi}" if livre.startswith('Pirkei')
                       else f"Mishnah_{livre.replace(' ', '_')}.{pe}.{mi}")
    for m in RE_MISHNAH.finditer(ctx):
        pe, mi = _num(m.group('perek')), _num(m.group('mish'))
        if pe and mi:
            out.append(f"Mishnah_{MASSEKHTOT[m.group('mass')].replace(' ', '_')}.{pe}.{mi}")
    for m in RE_DAF_HE.finditer(ctx):
        if RE_AVANT_MISHNAH.search(ctx[max(0, m.start() - 24):m.start()]):
            continue
        d = _num(m.group('daf'))
        if not d or d > 180:
            continue
        if m.group('amud'):
            ab = 'a' if m.group('amud').endswith('א') else 'b'
        else:
            ab = 'a' if m.group('colon') == '.' else 'b'
        pre = _prefixe_commentateur(ctx, m.start())
        if pre is None:      # commentateur non adressable par folio : on n'invente pas
            continue
        out.append(f"{pre}{MASSEKHTOT[m.group('mass')].replace(' ', '_')}.{d}{ab}")
    for m in RE_DAF_LAT.finditer(ctx):
        ab = {'a': 'a', 'b': 'b', '.': 'a', ':': 'b'}[m.group('ab').lower()]
        pre = _prefixe_commentateur(ctx, m.start())
        if pre is None:
            continue
        out.append(f"{pre}{MASSEKHTOT[m.group('mass').lower()].replace(' ', '_')}.{int(m.group('num'))}{ab}")
    for m in RE_SA_LAT.finditer(ctx):
        tour = {'oh': 'Orach Chayim', 'oc': 'Orach Chayim', 'yd': 'Yoreh Deah',
                'eh': 'Even HaEzer', 'cm': 'Choshen Mishpat'}[m.group('tour').lower()]
        out.append(f"Shulchan_Arukh,_{tour.replace(' ', '_')}.{m.group('siman')}.{m.group('seif')}")
    for m in RE_SA_HE.finditer(ctx):
        tour = 'Orach Chayim' if 'ח' in m.group('tour') else 'Yoreh Deah'
        si, se = _num(m.group('siman')), _num(m.group('seif'))
        if si and se:
            out.append(f"Shulchan_Arukh,_{tour.replace(' ', '_')}.{si}.{se}")
    for m in RE_MB.finditer(ctx):
        si, sk = _num(m.group('siman')), _num(m.group('sk'))
        if si and sk:
            out.append(f"Mishnah_Berurah.{si}.{sk}")
    marque = bool(RE_MARQUE_RAMBAM.search(ctx))
    for m in RE_RAMBAM.finditer(ctx):
        livre = _livre_rambam(m.group('livre'))
        if not livre:
            continue
        # « הלכות תפילין ד׳ » : le perek écrit sans « פרק » ni « פ ». La forme est
        # ambiguë — un nombre nu après un intitulé peut désigner un siman du Tour —
        # donc on ne l'accepte que sous la marque « רמב״ם », et seulement écrit avec
        # un geresh, comme le site l'écrit (117 fois pour les seuls tefillin).
        nu = m.group('perek3')
        if nu and not marque:
            continue
        perek = _num(m.group('perek1') or m.group('perek2') or nu or '')
        hal = _num(m.group('hal1') or m.group('hal2') or '')
        if not perek:
            continue
        # perek seul et aucune marque « רמב״ם » : la référence peut viser le Tour
        # aussi bien que le Mishné Torah. On s'abstient plutôt que de dénoncer une
        # page juste.
        if not hal and not marque:
            continue
        ref = f"Mishneh_Torah,_{livre.replace(' ', '_')}.{perek}"
        out.append(f"{ref}.{hal}" if hal else ref)
    # dédoublonne en gardant l'ordre
    seen, uniq = set(), []
    for r in out:
        if r not in seen:
            seen.add(r); uniq.append(r)
    return uniq


# ─────────────────────────── Extraction des citations ───────────────────────────

TAG = re.compile(r'<[^>]+>')
# Marqueurs de citation dans le balisage du site.
#
# `span.he-q` n'en est PAS un : la feuille de style du site ne lui donne que
# `direction: rtl` et la police Frank Ruhl Libre. C'est une classe typographique,
# appliquée aussi bien à une citation qu'à l'amorce d'un paragraphe où l'auteur
# énonce sa propre thèse (« סומא חייב בציצית — שהראייה גדר בכסות ולא תנאי בגברא »).
# La traiter comme un marqueur de citation confrontait ces thèses au daf cité à
# côté et les déclarait fabriquées. Seul <blockquote> encadre une citation.
# `blockquote.comment-source` en est un, en revanche : la classe a été créée pour
# distinguer la citation d'un commentateur du texte source, et c'est donc une
# revendication de littéralité. `blockquote.text-source` reste exclu : ce sont les
# seifim, que verify-yd-source.py confronte déjà à la source, mot pour mot.
#
# ⚠️ Portée réelle de ce marqueur : l'extraction est LIGNE À LIGNE, si bien qu'un
# blockquote réparti sur plusieurs lignes n'est jamais reconnu comme un tout. Sur
# les simanim 123-129, les 564 blocs `comment-source` sont tous multilignes et
# l'élargissement ci-dessus n'y change donc rien (mesuré : 3 446 citations extraites
# avant comme après). Ce qui protège réellement ces blocs, c'est la convention :
# tout hébreu verbatim y est encadré de « … ». Un bloc qui s'en dispense échappe au
# contrôle, quel que soit ce motif.
RE_MARK = re.compile(
    r'<blockquote(?:\s+class="comment-source"[^>]*)?>(.*?)</blockquote>()', re.S)
# Guillemets typographiques dans le texte rendu (pas dans les attributs : les balises
# sont supprimées avant extraction, ce qui écarte href="…", class="…", etc.)
RE_GUILL = re.compile(r'«([^«»]{5,900})»|„([^„”]{5,900})”')


def straight_pairs(s):
    """Contenus entre guillemets droits, appariés **séquentiellement**.

    Un appariement par expression régulière avec longueur minimale saute les paires
    trop courtes et décale toutes les suivantes : la « citation » extraite devient
    alors la prose située *entre* deux citations. On apparie donc 1er-2e, 3e-4e, …
    et on filtre sur la longueur seulement après coup.
    """
    pos = [m.start() for m in re.finditer(r'"', s)]
    # Un nombre IMPAIR décale TOUTES les paires, et ce qu'on extrait alors n'est
    # pas une citation mais la prose SITUÉE ENTRE deux citations. Au siman 10,
    # « ש״ארבע" ממעט פחות… » ouvre sur un gershayim et ferme sur un guillemet
    # droit : trois guillemets droits sur la ligne, et le garde-fou dénonçait
    # comme citation fabriquée une phrase que la page n'a jamais citée.
    # Mieux vaut ne rien extraire de cette ligne que d'y inventer une citation.
    if len(pos) % 2:
        return []
    return [s[a + 1:b] for a, b in zip(pos[0::2], pos[1::2]) if 0 < b - a - 1 <= 900]
# Préfixe de référence en tête de citation : « גמ' ברכות (נ״ג ע״א): », « OH 131:1 — », …
RE_PREFIX = re.compile(r'^[^"«„]{0,90}?[:—–-]\s*(?=["«„])')


# Le JSON-LD des pages porte un champ "description" qui résume le siman et cite
# souvent un fragment entre guillemets. C'est une métadonnée SEO, pas du contenu
# affiché : elle n'a pas à être jugée comme une citation.
SCRIPT_LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>.*?</script>', re.S | re.I)


def flatten_html(text):
    """Rend le texte visible en conservant les marqueurs de citation sous forme « … »."""
    def repl(m):
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return '«' + TAG.sub(' ', inner) + '»'
    out = RE_MARK.sub(repl, text)
    # on conserve <em>résumé</em> : c'est le marqueur de convention, il doit
    # rester visible après suppression des balises
    out = re.sub(r'<em>\s*(résumé|תמצית|summary)\s*</em>',
                 lambda m: f'<em>{m.group(1)}</em>', out)
    return html.unescape(re.sub(r'<(?!/?em\b)[^>]+>', ' ', out))


LATIN = re.compile(r'[A-Za-zÀ-ÿ]')

# Convention du site : les guillemets sont réservés au texte littéral. Une
# condensation d'un séif est annoncée par « résumé / תמצית / summary » et n'est
# donc pas jugée — c'est ce qui rend le verdict d'une citation guillemetée sans
# ambiguïté, et ce qui empêche une paraphrase de se faire passer pour la langue
# d'un auteur. Voir CLAUDE.md et scripts/README.md.
RESUME = re.compile(r'<em>\s*(?:résumé|תמצית|summary)\s*</em>\s*:?\s*$', re.I)

# Marqueurs qui présentent explicitement ce qui suit comme une citation. Sans l'un
# d'eux (ou sans référence collée juste avant), des guillemets encadrent tout aussi
# bien un résumé de l'auteur — « הברכה הולכת אחר השמחה » — qu'aucune source n'est
# censée contenir mot pour mot.
CUE = re.compile(
    'גמ[׳\']|תנן|תניא|תנו רבנן|ת[״"]ר|דתניא|דתנן|איתא|ברייתא|במשנה|משנת|'
    'וז[״"]ל|וזה לשון|לשון ה|כלשון|שנאמר|כתיב|דכתיב|אמרו|ואמר|אמר ר|'
    'מקור|לשון המחבר|לשון הרמ|ע[״"]פ|כדאיתא|וכלשון|הגמרא|הסוגיא|'
    r'[א-ת][״"][א-ת]\s*[:.]\s*$|\d\s*[:.]\s*$|[.:]\s*$')


def has_cue(before):
    """Le contexte immédiat annonce-t-il une citation ?

    Deux façons d'annoncer. La liste ``CUE`` couvre les formules — תניא, וז״ל,
    כלשון… Mais la façon la plus courante sur ce site n'y figurait pas : **nommer
    la source**. « רמב״ם (הלכות תפלה פי״ב הי״ג) — "…" » ne porte aucune formule
    d'annonce ; il porte une référence, ce qui revendique bien plus clairement une
    citation littérale qu'un « כלשון » ne le ferait.

    Faute de quoi ces citations n'étaient pas seulement non résolues : elles
    n'étaient **pas extraites du tout**, donc jamais comptées, pas même dans les
    « sans référence ». C'est le vrai verrou par lequel est passée la clause
    fabriquée du siman 284 — le défaut de résolution du Rambam n'en était que la
    seconde moitié.
    """
    tail = before[-90:]
    return bool(CUE.search(tail)) or bool(refs_in(tail))


def is_hebrew_quote(frag):
    """Écarte la prose française/anglaise : une citation doit être majoritairement hébraïque."""
    h, l = n_letters(frag), len(LATIN.findall(frag))
    return h >= MIN_LETTRES and h >= 2 * l


def quotes_in(text):
    """Chaque fragment hébreu présenté comme une citation, avec son numéro de ligne.

    L'extraction se fait **ligne par ligne** : le balisage du site place chaque
    citation sur sa propre ligne, et un guillemet non apparié ailleurs dans la page
    ne peut donc pas décaler l'appariement de toutes les suivantes.
    """
    text = SCRIPT_LD.sub(lambda m: '\n' * m.group(0).count('\n'), text)
    for lineno, line in enumerate(text.split('\n'), 1):
        plain = flatten_html(line)
        if not re.search(r'[א-ת]', plain):
            continue
        marked = [next(g for g in m.groups() if g is not None).strip()
                  for m in RE_GUILL.finditer(plain)]
        # les guillemets droits hors de tout bloc marqué sont eux aussi des citations
        outside = plain
        for b in marked:
            outside = outside.replace(b, ' ')
        blocks = [(b, True) for b in marked] + [(b, False) for b in straight_pairs(outside)]

        for block, from_marked in blocks:
            # Un bloc marqué (<blockquote>, span.he-q) contient souvent un préfixe de
            # référence, la citation entre guillemets droits, puis un commentaire de
            # l'auteur. Dans ce cas seule la portion entre guillemets est la citation.
            inner = [s for s in straight_pairs(block) if is_hebrew_quote(s)]
            for frag in (inner or [block]):
                frag = RE_PREFIX.sub('', frag).strip(' —–-:.«»')
                if not is_hebrew_quote(frag):
                    continue
                # écarte les identifiants d'ancre (mots collés par des tirets)
                if re.fullmatch(r'[\wא-ת֐-׿-]+', frag):
                    continue
                # un terme technique entre guillemets n'est pas une citation
                if n_letters(frag) < MIN_CITATION:
                    continue
                at = plain.find(frag)
                if at > 0 and RESUME.search(plain[:at]):
                    continue          # résumé assumé : pas une citation
                if at > 0 and not (from_marked or has_cue(plain[:at])):
                    continue
                yield frag, lineno, plain


# ─────────────────────────── Comparaison ───────────────────────────

def best_ratio(needle, haystack):
    """Meilleur ratio de similarité entre `needle` et une fenêtre de `haystack`."""
    if not needle or not haystack:
        return 0.0, ''
    n = len(needle)
    if n > len(haystack):
        return difflib.SequenceMatcher(None, needle, haystack).ratio(), haystack
    step = max(1, n // 6)
    # `quick_ratio` compare des multi-ensembles de caractères : il ignore
    # l'ordre. Sur de l'hébreu — vingt-deux lettres, distribution stable d'un
    # texte à l'autre — deux passages sans rapport y atteignent couramment 0,80.
    # S'en servir comme mesure finale faisait ressortir des « similarités » de
    # 0,79 à 0,85 entre une citation et un folio qui ne la contient pas, avec
    # pour « source » une suite de consonnes sans le moindre mot commun. Il ne
    # sert donc qu'à présélectionner des positions ; la valeur rendue est
    # toujours un ratio mesuré, qui tient compte de l'ordre.
    grossier = sorted(
        ((difflib.SequenceMatcher(None, needle, haystack[i:i + n]).quick_ratio(), i)
         for i in range(0, len(haystack) - n + 1, step)),
        reverse=True,
    )[:8]
    a_mesurer = set()
    for _, i in grossier:
        a_mesurer.update(range(max(0, i - step), min(len(haystack) - n, i + step) + 1))
    best, at = 0.0, (grossier[0][1] if grossier else 0)
    for i in sorted(a_mesurer):
        r = difflib.SequenceMatcher(None, needle, haystack[i:i + n]).ratio()
        if r > best:
            best, at = r, i
    return best, haystack[at:at + n]


# Plus longue suite de mots communs en deçà de laquelle deux textes hébreux
# n'ont rien à voir. Calibré sur les 123 signalements relus un à un par le Rav :
# les 46 variantes qu'il a reconnues partagent 7 mots suivis en médiane, les
# 68 faux positifs 1.
MIN_MOTS_SUIVIS = 3


def mots_he(s):
    return [w for w in re.sub(r'[^\wא-ת\s]', ' ', s).split() if re.search(r'[א-ת]', w)]


def suite_de_mots(frag, sources):
    """Plus longue suite de mots communs entre la citation et ses sources.

    Le ratio sur les consonnes ne peut pas, seul, décider : il garde un
    plancher de bruit élevé, et son seuil avait été calibré sur des valeurs
    surévaluées. Une suite de mots partagée, elle, ne se produit pas par
    hasard — c'est la trace d'un même texte, à la variante d'édition près.
    """
    q = mots_he(frag)
    s = mots_he(' '.join(sources))
    if not q or not s:
        return 0
    blocs = difflib.SequenceMatcher(None, q, s, autojunk=False).get_matching_blocks()
    return max((b.size for b in blocs), default=0)


def verdict(frag, sources):
    """Confronte un fragment (éventuellement coupé par des « … ») à ses sources."""
    hay = ''.join(norm(s) for s in sources)
    if not hay:
        return 'NON_RESOLU', 0.0, ''
    # « … », « וכו׳ », « כו׳ » marquent une coupe : chaque tronçon est vérifié séparément
    parts = [p for p in re.split(r'…|\.\.\.|וכו[׳\']|\bכו[׳\']', frag)
             if n_letters(p) >= MIN_LETTRES]
    parts = parts or [frag]
    ratios, worst_extract = [], ''
    for p in parts:
        np = norm(p)
        if np in hay:
            ratios.append(1.0)
            continue
        r, extract = best_ratio(np, hay)
        ratios.append(r)
        if not worst_extract or r == min(ratios):
            worst_extract = extract
    lo = min(ratios)
    if lo >= 0.999:
        return 'OK', lo, ''
    if lo >= SEUIL_VARIANTE:
        return 'VARIANTE', lo, worst_extract
    # Sous le seuil, le ratio ne suffit pas à conclure à une absence : une
    # citation abrégée, ou reprise d'une autre édition, fait chuter la
    # similarité sur les consonnes tout en gardant des phrases entières en
    # commun. « טעה בכל הברכות כולן אין מחזירין אותו » contre « …אין מעלין
    # אותו » partage neuf mots suivis pour un ratio de 0,83 : c'est une
    # variante d'édition, pas un texte introuvable.
    if suite_de_mots(frag, sources) >= MIN_MOTS_SUIVIS:
        return 'VARIANTE', lo, worst_extract
    return 'ABSENT', lo, worst_extract


# ─────────────────────────── Passage sur le site ───────────────────────────

def pages(base, langues):
    for dirpath, _dirs, files in os.walk(base):
        for f in sorted(files):
            if not f.endswith('.html'):
                continue
            lang = 'he' if f.endswith('-he.html') else 'en' if f.endswith('-en.html') else 'fr'
            if lang in langues:
                yield os.path.join(dirpath, f)


# Une référence talmudique collée à la citation : la page la revendique.
RE_REF_COLLEE = re.compile(
    r"^[»\"'\s):.]{0,6}\((?:[^)]{0,30})"
    r"(ברכות|שבת|מגילה|יבמות|פסחים|חולין|סוכה|ביצה|ר״ה|ראש השנה|בבא|יומא"
    r"|תענית|כתובות|עירובין|מנחות|סנהדרין|נדרים|גיטין|קידושין|מועד קטן)"
)


def ref_collee(plain, at, n):
    """La page place-t-elle une référence talmudique juste après la citation ?

    C'est ce qui distingue « la page se trompe de source » — auquel cas
    l'écart doit ressortir — de « la fenêtre a ramassé une référence voisine
    qui portait sur autre chose », auquel cas il n'y a rien à signaler.
    """
    if at < 0:
        return False
    return bool(RE_REF_COLLEE.match(plain[at + n: at + n + 60]))


# « המשנ״ב (ס״ק ג) » : sur une page de siman, un ס״ק sans numéro de siman en
# désigne un du siman de la page — c'est la façon naturelle d'écrire, et la seule
# que RE_MB ne savait pas lire (elle exige « מ״ב siman:ס״ק »). La citation était
# alors rapportée au folio de guemara qui traînait dans la même fenêtre : au
# siman 348, la page attribuait correctement « כדי שלא יתקיים מחשבתו… » au Michna
# Beroura ס״ק ג, et ressortait en REF_FAUSSE contre Chabbat ו ע״א.
# Les frontières de mot sont obligatoires : sans elles, « ס״ק » se retrouvait à
# l'intérieur de פוסקים, et le mot était lu comme une référence de sa′if katan.
RE_SK_NU = re.compile(r'(?<![א-ת])(?:ס["״]?ק|סעיף\s*קטן)(?![א-ת])\s*(?P<sk>[\dא-ת"״\'׳]{1,4})')


def ref_mb_du_siman(path, ctx):
    """Le ס״ק nu d'une page de siman, résolu sur le siman de cette page."""
    m = re.search(r'siman-(\d+)', path)
    if not m or '/yoreh-deah/' in path.replace(os.sep, '/'):
        return None            # la Michna Beroura ne couvre qu'Orah Haim
    k = RE_SK_NU.search(ctx)
    if not k:
        return None
    sk = _num(k.group('sk'))
    return f"Mishnah_Berurah.{int(m.group(1))}.{sk}" if sk else None


# ───────────────────── Beit Yosef, Tour et Aharonim ─────────────────────
#
# Deuxieme tranche de l'angle mort. Apres le Mishne Torah et les commentaires du
# daf, restaient sans motif les ouvrages que ces pages citent le plus : le Beit
# Yosef, le Tour, le Magen Avraham, le Taz, le Chakh, le Choulhan Aroukh HaRav,
# le Kaf HaHaim, le Aroukh HaChoulhan, le Peri Megadim, le Biour Halakha.
#
# Ces candidats ne sont essayes QU'EN REPLI, quand la citation est deja declaree
# absente de ses references resolues. C'est deliberé : un candidat en repli ne
# peut que RESOUDRE une citation reelle, jamais accuser une page juste — au pire
# il ne trouve rien et le verdict d'origine tient. Les mettre en references
# primaires ferait courir le risque inverse, et « ט״ז » est aussi la guematria de
# 16 : sur ce site, la sigle du Taz et le numero du seif seize s'ecrivent
# exactement pareil.
OUVRAGES = [
    # (sigle, gabarit Orah Haim, gabarit Yoreh Deah, second niveau requis)
    (r'מג["״]א|מגן אברהם', 'Magen_Avraham.{s}.{n}', None, True),
    (r'ט["״]ז|טורי זהב', 'Turei_Zahav_on_Shulchan_Arukh,_Orach_Chayim.{s}.{n}',
     "Turei_Zahav_on_Shulchan_Arukh,_Yoreh_De'ah.{s}.{n}", True),
    (r'ש["״]ך|שפתי כהן', None,
     "Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De'ah.{s}.{n}", True),
    (r'כה["״]ח|כף החיים', 'Kaf_HaChayim_on_Shulchan_Arukh,_Orach_Chayim.{s}.{n}', None, True),
    (r'שוע["״]ר|שו["״]ע הרב|שולחן ערוך הרב|אדמו["״]ר הזקן',
     'Shulchan_Arukh_HaRav,_Orach_Chayim.{s}.{n}', None, True),
    (r'ערוה["״]ש|ערוך השולחן', 'Arukh_HaShulchan,_Orach_Chaim.{s}.{n}',
     "Arukh_HaShulchan,_Yoreh_De'ah.{s}.{n}", True),
    (r'פמ["״]ג|פרי מגדים',
     'Peri_Megadim_on_Orach_Chayim,_Eshel_Avraham.{s}.{n}', None, True),
    (r'ב["״]י|בית יוסף', 'Beit_Yosef,_Orach_Chayim.{s}', 'Beit_Yosef,_Yoreh_Deah.{s}', False),
    (r'(?<![א-ת])טור(?![א-ת])', 'Tur,_Orach_Chayim.{s}', 'Tur,_Yoreh_Deah.{s}', False),
    (r'ביה["״]ל|ביאור הלכה', 'Biur_Halacha.{s}', None, False),
    # Le Pit'hei Techouva et le Baer Hetev sont les deux appareils les plus cités
    # des niveaux 4 de Yoré Déa, et ils manquaient à cette table : leurs citations
    # partaient toutes en « sans référence ». Les deux slugs n'existent que pour
    # Yoré Déa (l'endpoint Orah Haïm renvoie une erreur), d'où le gabarit OH à None.
    (r'פת["״]ש|פתחי תשובה', None,
     "Pitchei_Teshuva_on_Shulchan_Arukh,_Yoreh_De'ah.{s}.{n}", True),
    (r'באר היטב|ב["״]ה(?![א-ת])', None,
     "Beer_Hetev_on_Shulchan_Arukh,_Yoreh_De'ah.{s}.{n}", True),
    # Les Nekoudot HaKessef sont la reponse du Chakh au Taz : sur plusieurs simanim
    # ce sont elles qui tranchent, et deux agents de production ont du renoncer a
    # les citer mot a mot faute de reference resolvable — ils sont passes par le
    # report verbatim du Baer Hetev. Le gabarit s'arrete au SIMAN, sans second
    # niveau : l'index de Sefaria y est un simple numero d'ordre, pas le sk du Taz
    # ni le seif du Mehaber (chaque segment nomme lui-meme son ancrage). Un second
    # niveau produirait donc des references fausses.
    (r'נקודות הכסף|נקה["״]כ', None,
     "Nekudot_HaKesef_on_Shulchan_Arukh,_Yoreh_De'ah.{s}", False),
]
_OUVRAGES = [(re.compile(sig), oh, yd, n2) for sig, oh, yd, n2 in OUVRAGES]

# « או״ח רמ״ז », « סימן רמ״ז », « סי׳ ק״ל » — le siman explicitement nomme.
# « אבות פ״ב מי״ג » — perek et michna, la forme classique de renvoi a une michna.
# Le resolveur ne la lisait pas : le siman 1 ecrivait « מקורו במשנה (אבות פ״ב מי״ג) »,
# reference parfaitement exacte et collee a la citation, et se voyait tout de meme
# opposer le « (ברכות ה׳:) » d'une proposition suivante.
# MASSEKHTOT ne contient que les traités qui ont un Talmud Bavli. Une michna des
# ordres Zeraïm ou Tohorot n'y est donc pas, et une citation qui la nomme avec sa
# référence exacte — « משנה תרומות פ״ח מי״ב », que le Rama nomme au siman 157 —
# sortait en « sans référence », donc n'était jamais confrontée. On complète ici
# les traités mishnaïques manquants.
MISHNAYOT = dict(MASSEKHTOT, **{
    'אבות': 'Pirkei_Avot', 'אבות דרבי נתן': 'Pirkei_Avot',
    # Zeraïm
    'פאה': 'Peah', 'דמאי': 'Demai', 'כלאים': 'Kilayim', 'שביעית': 'Sheviit',
    'תרומות': 'Terumot', 'מעשרות': 'Maasrot', 'מעשר שני': 'Maaser Sheni',
    'חלה': 'Challah', 'ערלה': 'Orlah', 'ביכורים': 'Bikkurim', 'בכורים': 'Bikkurim',
    # Moed, Nezikin, Kodachim sans Bavli
    'שקלים': 'Shekalim', 'עדיות': 'Eduyot', 'עדויות': 'Eduyot',
    'מדות': 'Middot', 'מידות': 'Middot', 'קינים': 'Kinnim', 'תמיד': 'Tamid',
    # Tohorot
    'כלים': 'Kelim', 'אהלות': 'Oholot', 'נגעים': 'Negaim', 'פרה': 'Parah',
    'טהרות': 'Tahorot', 'מקואות': 'Mikvaot', 'מכשירין': 'Makhshirin',
    'זבים': 'Zavim', 'טבול יום': 'Tevul Yom', 'עוקצין': 'Oktzin',
    'ידים': 'Yadayim', 'ידיים': 'Yadayim',
})
RE_PEREK_MISHNAH = re.compile(
    r'(?P<mass>' + '|'.join(sorted((k for k in MISHNAYOT if re.search(r'[א-ת]', k)),
                                   key=len, reverse=True)) + r')\s*'
    r'פ["״\'׳]?(?P<p>[א-ת]{1,3}["״\'׳]?[א-ת]?)\s*,?\s*'
    r'מ["״\'׳]?(?P<m>[א-ת]{1,3}["״\'׳]?[א-ת]?)(?![א-ת])')


# Les livres du Tanakh, que le résolveur ne connaissait pas du tout : une citation
# de verset accompagnée de sa référence — « (שמות ל״ד:ט״ז) » — sortait en « sans
# référence », donc n'était jamais confrontée à la source. Les pages en citent
# beaucoup : c'est le socle des simanim d'idolâtrie.
TANAKH = {
    'בראשית': 'Genesis', 'שמות': 'Exodus', 'ויקרא': 'Leviticus',
    'במדבר': 'Numbers', 'דברים': 'Deuteronomy', 'יהושע': 'Joshua',
    'שופטים': 'Judges', 'שמואל א': 'I_Samuel', 'שמואל ב': 'II_Samuel',
    'מלכים א': 'I_Kings', 'מלכים ב': 'II_Kings', 'ישעיה': 'Isaiah',
    'ישעיהו': 'Isaiah', 'ירמיה': 'Jeremiah', 'ירמיהו': 'Jeremiah',
    'יחזקאל': 'Ezekiel', 'הושע': 'Hosea', 'יואל': 'Joel', 'עמוס': 'Amos',
    'עובדיה': 'Obadiah', 'יונה': 'Jonah', 'מיכה': 'Micah', 'נחום': 'Nahum',
    'חבקוק': 'Habakkuk', 'צפניה': 'Zephaniah', 'חגי': 'Haggai',
    'זכריה': 'Zechariah', 'מלאכי': 'Malachi', 'תהלים': 'Psalms',
    'משלי': 'Proverbs', 'איוב': 'Job', 'שיר השירים': 'Song_of_Songs',
    'רות': 'Ruth', 'איכה': 'Lamentations', 'קהלת': 'Ecclesiastes',
    'אסתר': 'Esther', 'דניאל': 'Daniel', 'עזרא': 'Ezra',
    'נחמיה': 'Nehemiah', 'דברי הימים א': 'I_Chronicles',
    'דברי הימים ב': 'II_Chronicles',
}
RE_PASSOUK = re.compile(
    r'(?<![א-ת])(?P<livre>' + '|'.join(sorted(TANAKH, key=len, reverse=True)) + r')'
    r'\s*(?P<ch>[\dא-ת"״\'׳]{1,6})\s*[:׃]\s*(?P<v>[\dא-ת"״\'׳]{1,5})(?![א-ת])')


RE_VERSET = re.compile(r'(?:שנאמר|ואומר|דכתיב|כדכתיב|וכתיב|כמו שנאמר)\s*[:"«„]?\s*$')
RE_SIMAN_SEIF = re.compile(r'(?P<s>[\dא-ת"״\'׳]{1,6})\s*[:׃]\s*(?P<n>[\dא-ת"״\'׳]{1,4})')
# Idem, et le cas est spectaculaire : sans frontière, « יו״ד » sans gershayim
# matchait les trois premières lettres de יוֹדֵעַ, et la lettre suivante — le ע de
# יודע — était lue comme le numéro du siman, soit 70. Une citation exacte du Chakh
# sur le siman 129 ressortait ainsi en REF_FAUSSE contre le Chakh du siman 70.
RE_SIMAN_NOMME = re.compile(r'(?<![א-ת])(?:או["״]?ח|יו["״]?ד|סימן|סי[\'׳])(?![א-ת])\s*'
                            r'(?P<s>[\dא-ת"״\'׳]{1,6})')
# La forme complète, qui nomme le recueil avec le siman.
RE_TOUR_SIMAN = re.compile(r'(?<![א-ת])(?:או["״]?ח|יו["״]?ד)(?![א-ת])\s*'
                           r'(?:סימן\s*|סי[\'׳]\s*)?(?P<s>[\dא-ת"״\'׳]{1,6})')


def _apres_deux_points(ctx, m):
    """La correspondance est-elle la seconde moitié d'un « chapitre:verset » ?"""
    return re.search(r'[:׃]\s*$', ctx[:m.start()]) is not None


def _plus_proche(rx, ctx, rejeter=None):
    """La correspondance la plus proche de la citation, avant ou après elle.

    Une ligne portant plusieurs citations donne plusieurs ס״ק dans la fenêtre, et
    la référence peut être écrite avant la citation (« Le Chakh (ס״ק נ׳) : “…” »)
    comme après (« “…” (ס״ק נ׳) »). Le dépôt emploie les deux tournures. Prendre la
    première correspondance de la fenêtre revenait donc à hériter du ס״ק de la
    citation voisine — trois fois sur le seul siman 124, contre des pages qui
    portaient pourtant la bonne référence juste à côté.

    On mesure la distance à la citation : pour ce qui la précède, ce qui reste
    après la correspondance ; pour ce qui la suit, ce qui la précède.

    La recherche porte sur la fenêtre ENTIÈRE, et non sur les deux moitiés
    découpées autour de la sentinelle : un appelant qui lit ce qui SUIT la
    correspondance (`ctx[m.end():…]`, pour y trouver le siman collé à la sigle)
    a besoin de positions valables dans la fenêtre. Découpée, la moitié d'après
    rendait des positions décalées de toute la longueur de la moitié d'avant, et
    « (ט״ז יו״ד קל״א ס״ק ג) » se voyait lire le siman ק״ל d'une phrase précédente.
    """
    pivot = ctx.find(SENTINELLE)
    if pivot < 0:
        pivot = len(ctx)
    meilleur, distance = None, None
    for m in rx.finditer(ctx):
        if rejeter is not None and rejeter(ctx, m):
            continue
        if m.start() > pivot:
            d = m.start() - (pivot + len(SENTINELLE))
        elif m.end() <= pivot:
            d = pivot - m.end()
        else:
            continue          # à cheval sur la citation : ce n'est pas une référence
        if distance is None or d < distance:
            meilleur, distance = m, d
    return meilleur


def candidats_ouvrages(path, ctx):
    """Références de repli pour les ouvrages nommés dans la fenêtre.

    Le siman vient de la fenêtre s'il y est nommé, sinon de la page — une page de
    siman qui écrit « הט״ז (ס״ק א) » parle du Taz de SON siman. Le second niveau
    (ס״ק, séif) vient du ס״ק de la fenêtre ou de la forme « siman:séif ».
    """
    p = path.replace(os.sep, '/')
    yd = '/yoreh-deah/' in p
    m = re.search(r'siman-(\d+)', p)
    siman_page = int(m.group(1)) if m else None

    # « ש״ך יו״ד קכ״ד ס״ק ע״א » nomme le recueil ET le siman : c'est une référence
    # complète. « תשובת מהרי״ל סימן ל״ח », cité au passage dans la prose, n'est
    # qu'un numéro. À proximité égale la seconde forme l'emportait, et la citation
    # partait chercher le Chakh du siman 38. La forme complète prime donc, où
    # qu'elle soit dans la fenêtre.
    m = _plus_proche(RE_TOUR_SIMAN, ctx) or _plus_proche(RE_SIMAN_NOMME, ctx)
    siman = (_num(m.group('s')) if m else None) or siman_page
    if not siman:
        return []

    # Une ligne portant plusieurs citations donne plusieurs ס״ק dans la fenêtre.
    # Celui de NOTRE citation est le premier de ce qui la SUIT ; prendre le premier
    # de toute la fenêtre revenait à hériter du ס״ק de la citation précédente. Vu au
    # siman 127, où « … דנשים עצלניות הן » (ש״ך ס״ק ל) était confronté au ס״ק כ״ט
    # de la clause voisine, et au siman 125 pour le ס״ק ב lu comme ס״ק א.
    k = _plus_proche(RE_SK_NU, ctx)
    n = _num(k.group('sk')) if k else None
    if n is None:
        m2 = RE_SIMAN_SEIF.search(ctx)
        n = _num(m2.group('n')) if m2 else None

    out = []
    for rx, oh, ydg, n2 in _OUVRAGES:
        # La sigle à retenir est celle qui accompagne LA citation, pas la première
        # de la fenêtre. « והש״ך מבאר … : “…” (ש״ך יו״ד קכ״ט ס״ק ל״ד) » nomme le
        # Chakh deux fois : dans la prose d'abord, dans la référence ensuite. La
        # première occurrence n'est suivie d'aucun numéro, et c'est pourtant elle
        # qui fixait la fenêtre où lire le siman.
        # Un numéral qui SUIT un deux-points n'est pas une sigle : c'est la
        # seconde moitié d'une référence « livre chapitre:verset ». Sans cette
        # garde, « (שמות ל״ד:ט״ז) » — Chemot 34:16 — était lu comme la sigle du
        # Taz, et une citation exacte du verset partait chercher un ס״ק ט״ז qui
        # n'existe pas. Tout verset dont le numéro s'écrit comme une sigle connue
        # était dans ce cas.
        m = _plus_proche(rx, ctx, rejeter=_apres_deux_points)
        if not m:
            continue
        gabarit = ydg if yd else oh
        if not gabarit:
            continue
        # Les chiffres qui SUIVENT la sigle priment sur ceux qui traînent ailleurs
        # dans la fenêtre : « (שו״ע הרב קי״ד:א) » désigne le séif א du siman קי״ד,
        # et non le premier « X:Y » rencontré soixante caractères plus tôt, qui
        # appartient à une autre proposition de la même ligne.
        # La coupure à 60 caractères ne doit pas tomber AU MILIEU d'un numéral
        # hébreu : « … יו״ד ק|כ״ט … » laissait lire ק seul, soit le siman 100, et
        # le Chakh du siman 129 était cherché sur le siman 100. On prolonge donc
        # jusqu'à la fin du mot commencé.
        fin = min(len(ctx), m.end() + 60)
        while fin < len(ctx) and re.match(r'[א-ת"״\'׳]', ctx[fin]):
            fin += 1
        proche = ctx[m.end():fin]
        # Le siman local ne peut être qu'une forme COMPLÈTE (« יו״ד קכ״ד »), jamais
        # un « סימן ל״ח » nu : la fenêtre au niveau supérieur a déjà donné priorité
        # à la forme complète, et un numéro nu cité au passage dans la prose la
        # renverserait. Vu au siman 124 : « (ש״ך יו״ד קכ״ד ס״ק ע״א) … תשובת מהרי״ל
        # סימן ל״ח … “citation” » envoyait le Chakh du siman 124 chercher sa
        # קבלה dans le siman 38.
        s_loc = RE_TOUR_SIMAN.search(proche)
        m_loc = RE_SIMAN_SEIF.search(proche)
        k_loc = RE_SK_NU.search(proche)
        si = (_num(s_loc.group('s')) if s_loc else None) \
             or (_num(m_loc.group('s')) if m_loc else None) or siman
        ni = (_num(k_loc.group('sk')) if k_loc else None) \
             or (_num(m_loc.group('n')) if m_loc else None) or n
        if not si:
            continue
        if n2:
            if ni:
                out.append(gabarit.format(s=si, n=ni))
        else:
            out.append(gabarit.format(s=si))
    return out


def ref_du_siman(path):
    """Référence Sefaria de l'ouvrage dont cette page est l'exposé.

    Le niveau 4 expose le Choul'han Aroukh HaRav ; les autres, le Mehaber.
    """
    m = re.search(r"siman-(\d+)", path)
    if not m:
        return None
    num = m.group(1)
    if "/yoreh-deah/" in path.replace(os.sep, "/"):
        section = "Yoreh_Deah"
    else:
        section = "Orach_Chayim"
    if "niveau-4-daat-harav" in path:
        return f"Shulchan_Arukh_HaRav,_{section}.{num}"
    return f"Shulchan_Arukh,_{section}.{num}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default='sources', help='répertoire à parcourir')
    ap.add_argument('--langues', default='fr', help='fr, he, en (séparés par des virgules)')
    ap.add_argument('--csv', default=None,
                    help='fichier de rapport ; par défaut audit/citations-verifiees.csv '
                         'pour un passage complet, audit/citations-<cible>.csv pour --path')
    ap.add_argument('--only-absent', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    # Un passage ciblé n'écrase plus le rapport du site entier. Deux fois, un
    # « --path sources/shabbat/siman-284 » a réduit audit/citations-verifiees.csv
    # à quatre lignes, et le rapport complet — le seul document qui dise ce qui
    # reste à corriger — a été perdu en silence jusqu'à ce qu'on le remarque.
    if args.csv is None:
        cible = os.path.normpath(args.path)
        # Un chemin ABSOLU — vu quand un agent vérifiait une copie de son scratchpad —
        # produisait un nom de rapport tiré du chemin entier :
        # « audit/citations-home-user-Daat.ai-scratchpad-yd-128-niveau4-check-siman-128.csv ».
        # Un CSV parasite dans audit/, aussitôt emporté par le prochain git add -A.
        # On ramène la cible au dépôt, et hors de sources/ on n'écrit aucun rapport.
        try:
            cible = os.path.relpath(os.path.abspath(cible), ROOT)
        except ValueError:
            cible = cible
        cible = cible.strip(os.sep)
        if cible in ('sources', '.', ''):
            args.csv = 'audit/citations-verifiees.csv'
        elif cible.startswith('sources' + os.sep):
            args.csv = 'audit/citations-%s.csv' % re.sub(r'[^\w.-]+', '-', cible).strip('-')
        else:
            args.csv = None      # hors du contenu du site : contrôle sans rapport

    langues = set(args.langues.split(','))
    base = args.path if os.path.isabs(args.path) else os.path.join(ROOT, args.path)

    rows, stats = [], {'OK': 0, 'VARIANTE': 0, 'REF_FAUSSE': 0, 'INTROUVABLE': 0,
                       'NON_RESOLU': 0, 'SANS_REF': 0}
    cache_src = {}

    for path in pages(base, langues):
        text = open(path, encoding='utf-8').read()

        for frag, lineno, plain in quotes_in(text):
            # la référence doit accompagner la citation, pas simplement figurer
            # quelque part sur la même ligne
            at = plain.find(frag)
            window = fenetre_ref(plain, at, len(frag)) if at >= 0 else plain
            refs = refs_in(window)
            if not refs:
                # `candidats_ouvrages` n'intervenait qu'en REPLI, après un verdict
                # ABSENT — donc jamais quand AUCUNE référence primaire n'avait été
                # résolue. Or la forme conventionnelle du dépôt pour les nossei
                # kelim, « (ש״ך יו״ד קכ״ח ס״ק ג) », n'en produit aucune : elle n'a
                # pas de deux-points, que RE_SA_HE exige. Ces citations partaient
                # donc en « sans référence » et n'étaient JAMAIS vérifiées — 85 des
                # 221 citations d'un seul siman, et la totalité du Chakh et du Taz
                # sur les 50 simanim de Yoré Déa déjà en ligne.
                # L'ouvrage nommé dans la fenêtre devient donc une résolution de
                # PREMIER rang quand il n'y en a pas d'autre.
                refs = [c for c in candidats_ouvrages(path, window) if c]
            if not refs:
                stats['SANS_REF'] += 1
                continue
            segs = []
            for r in refs[:3]:
                if r not in cache_src:
                    cache_src[r] = fetch(r) or []
                segs += cache_src[r]
            v, ratio, extract = verdict(frag, segs)

            # Repli sur l'ouvrage dont la page EST l'exposé. Une page de siman
            # cite d'abord son propre siman ; si la prose voisine mentionne au
            # passage un folio de Guemara, la fenêtre le ramasse et la citation
            # du Mehaber est déclarée absente d'un traité qu'elle n'a jamais
            # revendiqué. Trente-huit REF_FAUSSE sur cinquante-six venaient de
            # là, la référence talmudique portant sur une autre proposition de
            # la même ligne.
            #
            # Le repli n'est tenté QUE si aucune référence talmudique ne colle
            # à la citation : quand la page place elle-même « (ברכות כ״ב.) »
            # juste après les guillemets, elle revendique ce folio, et l'écart
            # doit ressortir — c'est le défaut relevé au siman 267.
            if v == 'ABSENT' and not ref_collee(plain, at, len(frag)):
                propre = ref_du_siman(path)
                if propre and propre not in refs:
                    if propre not in cache_src:
                        cache_src[propre] = fetch(propre) or []
                    if cache_src[propre]:
                        v2, ratio2, extract2 = verdict(frag, cache_src[propre])
                        if v2 in ('OK', 'VARIANTE'):
                            v, ratio, extract = v2, ratio2, extract2
                            refs = refs + [propre + ' (siman de la page)']
            # Repli sur les commentaires imprimés sur le daf. Un daf porte la
            # guemara ET Rachi ET les Tossefot ; le résolveur ne ramenait que la
            # guemara. Une page qui cite les Tossefot correctement — « פירש
            # בקונטרס… (עבודה זרה ע״ו ע״א) » — se voyait donc reprocher un texte
            # verbatim, en REF_FAUSSE, contre un daf où il figure réellement.
            #
            # Le mécanisme COMMENTATEURS existant ne couvre que le cas où le nom du
            # commentateur JOUXTE la référence ; le cas courant est que la page
            # nomme le commentateur dans sa prose et ne mette que le daf entre
            # parenthèses. Six signalements sur six, mesurés le 27/08, étaient de
            # cette espèce — quatre Tossefot sur Avoda Zara, un Rachi, une Michna
            # dont le chapitre ז׳ avait été lu comme le folio 7b.
            if v == 'ABSENT':
                for cand in ([ref_mb_du_siman(path, window)]
                             + candidats_ouvrages(path, window)):
                    if not cand or cand in refs:
                        continue
                    if cand not in cache_src:
                        cache_src[cand] = fetch(cand) or []
                    if not cache_src[cand]:
                        continue
                    v2, ratio2, extract2 = verdict(frag, cache_src[cand])
                    if v2 in ('OK', 'VARIANTE'):
                        v, ratio, extract = v2, ratio2, extract2
                        refs = refs + [cand + ' (ouvrage nommé dans la fenêtre)']
                        break

            if v == 'ABSENT':
                for r in refs[:3]:
                    if '_on_' in r or '.' not in r:
                        continue
                    for pre in ('Rashi_on_', 'Tosafot_on_'):
                        cand = pre + r
                        if cand not in cache_src:
                            cache_src[cand] = fetch(cand) or []
                        if not cache_src[cand]:
                            continue
                        v2, ratio2, extract2 = verdict(frag, cache_src[cand])
                        if v2 in ('OK', 'VARIANTE'):
                            v, ratio, extract = v2, ratio2, extract2
                            refs = refs + [cand + ' (commentaire du daf)']
                            break
                    if v != 'ABSENT':
                        break

            # LA PAGE A-T-ELLE SEULEMENT REVENDIQUÉ UNE SOURCE POUR CETTE CITATION ?
            #
            # La fenêtre de contexte est large : elle ramasse les références de
            # toute la ligne. Quand la citation n'en porte aucune à son contact,
            # ce qu'on lui oppose est la référence d'une proposition VOISINE — et
            # l'accusation vise une page qui n'a rien revendiqué du tout.
            #
            # Mesuré sur le tri du 27/08 : douze signalements sur vingt-six
            # étaient de cette espèce. Le siman 1 écrivait « מקורו במשנה (אבות פ״ב
            # מי״ג) », parfaitement exact, et se voyait opposer le « (ברכות ה׳:) »
            # d'une clause suivante. Le 52 et le 116 citaient un verset introduit
            # par « ואומר », sans renvoi ; le 120 citait le texte de la tefila.
            #
            # On exige donc qu'une référence jouxte la citation — trente caractères
            # avant l'ouverture, soixante après la fermeture. À défaut, la citation
            # rejoint les « sans référence » : non vérifiable, mais non accusée.
            # C'est le principe déjà appliqué par ref_collee(), étendu de la seule
            # guemara à toutes les références que le résolveur sait lire.
            if v == 'ABSENT' and at >= 0:
                avant30 = plain[max(0, at - 30):at]
                proche = avant30 + ' § ' + plain[at + len(frag):at + len(frag) + 60]
                # « שנאמר … », « ואומר … », « דכתיב … » annoncent un VERSET. La
                # référence qui traîne à portée est celle d'autre chose : au siman
                # 52, la page cite « פדה בשלום נפשי מקרב לי כי ברבים היו עמדי » —
                # Tehilim נ״ה:י״ט, verbatim — et se voyait opposer le renvoi au
                # Rambam de la proposition suivante. Le résolveur ne lit pas le
                # Tanakh ; tant qu'il ne le lira pas, il doit se taire ici.
                if RE_VERSET.search(avant30) or not refs_in(proche):
                    stats['SANS_REF'] += 1
                    continue

            ailleurs = ''
            if v == 'ABSENT':
                juste = bien_attribuee(frag, window)
                if juste:
                    v, ailleurs = 'OK', juste          # la page cite un ouvrage non résolu
                else:
                    found = [r for r in locate(frag) if r]
                    v = 'REF_FAUSSE' if found else 'INTROUVABLE'
                    ailleurs = ' · '.join(found[:3])
            stats[v] = stats.get(v, 0) + 1
            if v == 'OK' or (args.only_absent and v not in ('INTROUVABLE', 'REF_FAUSSE')):
                continue

            rows.append({
                'fichier': os.path.relpath(path, ROOT), 'ligne': lineno,
                'refs': ' | '.join(refs[:3]), 'verdict': v, 'ratio': f'{ratio:.2f}',
                'citation': re.sub(r'\s+', ' ', frag)[:400],
                'source_reelle': re.sub(r'\s+', ' ', extract)[:400],
                'texte_trouve_en': ailleurs,
            })

    if args.csv:
        import csv as _csv
        champs = ['fichier', 'ligne', 'refs', 'verdict', 'ratio', 'citation',
                  'source_reelle', 'texte_trouve_en']
        out = args.csv if os.path.isabs(args.csv) else os.path.join(ROOT, args.csv)
        os.makedirs(os.path.dirname(out), exist_ok=True)

        # Une exécution restreinte par --path FUSIONNE dans le CSV au lieu de l'écraser :
        # sans cela, vérifier un siman effaçait les constats de tous les autres. Plusieurs
        # agents travaillant en parallèle se sont ainsi effacé mutuellement leurs relevés.
        anciennes = []
        if args.path and os.path.exists(out):
            portee = os.path.relpath(os.path.abspath(args.path), ROOT).replace(os.sep, '/')
            with open(out, newline='', encoding='utf-8') as fh:
                for r in _csv.DictReader(fh):
                    f = (r.get('fichier') or '').replace(os.sep, '/')
                    if not (f == portee or f.startswith(portee.rstrip('/') + '/')):
                        anciennes.append({k: r.get(k, '') for k in champs})

        with open(out, 'w', newline='', encoding='utf-8') as fh:
            w = _csv.DictWriter(fh, fieldnames=champs)
            w.writeheader()
            w.writerows(sorted(anciennes + rows,
                               key=lambda r: (r['verdict'] != 'INTROUVABLE', r['fichier'], int(r['ligne']))))

    if not args.quiet:
        for r in sorted(rows, key=lambda r: (r['verdict'] != 'INTROUVABLE', r['fichier'])):
            print(f"[{r['verdict']:9}] {r['fichier']}:{r['ligne']}  ← {r['refs']}  (r={r['ratio']})")
            print(f"    page   : {r['citation'][:160]}")
            if r['source_reelle']:
                print(f"    source : {r['source_reelle'][:160]}")
        print()
    total = sum(stats.values())
    print('=== Vérification des citations (Sefaria) ===')
    print(f"  Citations examinées : {total}")
    print(f"  Sans référence      : {stats['SANS_REF']}  (non vérifiables automatiquement)")
    print(f"  Référence non résolue: {stats['NON_RESOLU']}")
    print(f"  Conformes           : {stats['OK']}")
    print(f"  Variantes           : {stats['VARIANTE']}")
    print(f"  Référence fausse    : {stats['REF_FAUSSE']}  (texte réel, mais pas là où la page le situe)")
    print(f"  INTROUVABLES        : {stats['INTROUVABLE']}  (absentes de tout Sefaria)")
    if args.csv:
        print(f"  Détail              : {args.csv}")
    return 1 if (stats['INTROUVABLE'] or stats['REF_FAUSSE']) else 0


if __name__ == '__main__':
    sys.exit(main())
