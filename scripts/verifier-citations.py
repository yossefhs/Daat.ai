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
1. Extraire de chaque page les fragments hébreux présentés comme des citations
   (<span class="he-q">, <blockquote>, ou entre guillemets « … » / " … ").
2. Résoudre la référence qui les accompagne (daf talmudique, séif du Choulhan
   Aroukh, ס״ק de la Michna Beroura, Rambam…) en référence Sefaria canonique.
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


def _cached(key, produce):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, hashlib.sha1(key.encode()).hexdigest()[:20] + '.json')
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    data = produce()
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

# Abréviations à gershayim développées avant comparaison : les pages écrivent
# « הקב״ה » là où l'édition Sefaria imprime « הקדוש ברוך הוא ».
_ABBREV = [
    ('הקב״ה', 'הקדוש ברוך הוא'), ('הקב"ה', 'הקדוש ברוך הוא'),
    ('הקב׳׳ה', 'הקדוש ברוך הוא'),
    ('ת״ר', 'תנו רבנן'), ('ת"ר', 'תנו רבנן'),
    ('ב״ש', 'בית שמאי'), ('ב"ש', 'בית שמאי'),
    ('ב״ה', 'בית הלל'), ('ב"ה', 'בית הלל'),
    ('רשב״י', 'רבי שמעון בר יוחאי'), ('ריב״ל', 'רבי יהושע בן לוי'),
    ('רנב״י', 'רב נחמן בר יצחק'), ('ר״ל', 'ריש לקיש'),
    ('אעפ״י', 'אף על פי'), ('אע״פ', 'אף על פי'), ('אע"פ', 'אף על פי'),
    ('כ״ש', 'כל שכן'), ('ק״ו', 'קל וחומר'), ('אא״כ', 'אלא אם כן'),
    ('ה׳', 'ה'), ("ה'", 'ה'),
]

# Variantes graphiques qui ne changent pas le texte
_SUBS = [
    ('יהוה', 'ה'), ('אלהים', 'אלקים'), ('אלוקים', 'אלקים'),
    ('ירושלים', 'ירושלם'),
]


def norm(s):
    """Réduit un texte hébreu à ses seules consonnes, pour comparaison."""
    s = html.unescape(s)
    for a, b in _ABBREV:
        s = s.replace(a, b)
    s = NIKUD.sub('', s)
    s = NONHEB.sub('', s)
    for a, b in _SUBS:
        s = s.replace(a, b)
    return s


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
    r'[\s]*(?:(?P<amud>ע["״]?[אב])|(?P<colon>[.:]))')
RE_DAF_LAT = re.compile(
    r'\b(?P<mass>' + '|'.join(sorted((k for k in MASSEKHTOT if not re.search(r'[א-ת]', k)),
                                     key=len, reverse=True)) + r')\b'
    r'[\s,]*\(?(?P<num>\d{1,3})\s*(?P<ab>[ab.:])', re.I)
# Choulhan Aroukh : « OH 131:1 », « או״ח קל״א:א », « שו״ע י:א », « YD 89:1 »
RE_SA_LAT = re.compile(r'\b(?P<tour>OH|OC|YD|EH|CM)\s*(?P<siman>\d{1,3})\s*:\s*(?P<seif>\d{1,3})', re.I)
RE_SA_HE = re.compile(r'(?P<tour>או["״]?ח|יו["״]?ד)\s*'
                      r'(?P<siman>[א-ת]{1,4}["״\'׳]?[א-ת]?)\s*[:׃]\s*'
                      r'(?P<seif>[א-ת]{1,3})')
# Michna Beroura : « MB 10:11 », « מ״ב י:יא », « ס״ק ג »
RE_MB = re.compile(r'(?:MB|מ["״]?ב)\s*(?P<siman>[\dא-ת"״\'׳]{1,5})\s*:\s*'
                   r'(?P<sk>[\dא-ת"״\'׳]{1,4})')


def _num(tok):
    """Un jeton numérique, chiffres arabes ou lettres hébraïques."""
    tok = tok.strip()
    if re.fullmatch(r'\d+', tok):
        return int(tok)
    return gem(tok)


def refs_in(ctx):
    """Toutes les références Sefaria détectées dans un contexte textuel."""
    out = []
    for m in RE_DAF_HE.finditer(ctx):
        d = _num(m.group('daf'))
        if not d or d > 180:
            continue
        if m.group('amud'):
            ab = 'a' if m.group('amud').endswith('א') else 'b'
        else:
            ab = 'a' if m.group('colon') == '.' else 'b'
        out.append(f"{MASSEKHTOT[m.group('mass')].replace(' ', '_')}.{d}{ab}")
    for m in RE_DAF_LAT.finditer(ctx):
        ab = {'a': 'a', 'b': 'b', '.': 'a', ':': 'b'}[m.group('ab').lower()]
        out.append(f"{MASSEKHTOT[m.group('mass').lower()].replace(' ', '_')}.{int(m.group('num'))}{ab}")
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
    # dédoublonne en gardant l'ordre
    seen, uniq = set(), []
    for r in out:
        if r not in seen:
            seen.add(r); uniq.append(r)
    return uniq


# ─────────────────────────── Extraction des citations ───────────────────────────

TAG = re.compile(r'<[^>]+>')
# Marqueurs de citation dans le balisage du site
RE_MARK = re.compile(r'<span class="he-q">(.*?)</span>|<blockquote>(.*?)</blockquote>', re.S)
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
    return [s[a + 1:b] for a, b in zip(pos[0::2], pos[1::2]) if 0 < b - a - 1 <= 900]
# Préfixe de référence en tête de citation : « גמ' ברכות (נ״ג ע״א): », « OH 131:1 — », …
RE_PREFIX = re.compile(r'^[^"«„]{0,90}?[:—–-]\s*(?=["«„])')


def flatten_html(text):
    """Rend le texte visible en conservant les marqueurs de citation sous forme « … »."""
    def repl(m):
        inner = m.group(1) if m.group(1) is not None else m.group(2)
        return '«' + TAG.sub(' ', inner) + '»'
    out = RE_MARK.sub(repl, text)
    return html.unescape(TAG.sub(' ', out))


LATIN = re.compile(r'[A-Za-zÀ-ÿ]')

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
    """Le contexte immédiat annonce-t-il une citation ?"""
    return bool(CUE.search(before[-90:]))


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
    best, at = 0.0, 0
    step = max(1, n // 6)
    for i in range(0, len(haystack) - n + 1, step):
        r = difflib.SequenceMatcher(None, needle, haystack[i:i + n]).quick_ratio()
        if r > best:
            best, at = r, i
    # affine autour du meilleur point
    lo, hi = max(0, at - step), min(len(haystack) - n, at + step)
    for i in range(lo, hi + 1):
        r = difflib.SequenceMatcher(None, needle, haystack[i:i + n]).ratio()
        if r > best:
            best, at = r, i
    return best, haystack[at:at + n]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default='sources', help='répertoire à parcourir')
    ap.add_argument('--langues', default='fr', help='fr, he, en (séparés par des virgules)')
    ap.add_argument('--csv', default='audit/citations-verifiees.csv')
    ap.add_argument('--only-absent', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

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
            window = (plain[max(0, at - FENETRE_REF):at + len(frag) + FENETRE_REF]
                      if at >= 0 else plain)
            refs = refs_in(window)
            if not refs:
                stats['SANS_REF'] += 1
                continue
            segs = []
            for r in refs[:3]:
                if r not in cache_src:
                    cache_src[r] = fetch(r) or []
                segs += cache_src[r]
            v, ratio, extract = verdict(frag, segs)
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
        out = args.csv if os.path.isabs(args.csv) else os.path.join(ROOT, args.csv)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', newline='', encoding='utf-8') as fh:
            w = _csv.DictWriter(fh, fieldnames=['fichier', 'ligne', 'refs', 'verdict',
                                                'ratio', 'citation', 'source_reelle',
                                                'texte_trouve_en'])
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r['verdict'] != 'INTROUVABLE', r['fichier'], r['ligne'])))

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
