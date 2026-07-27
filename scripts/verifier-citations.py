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
  OK        la citation figure telle quelle dans la source
  VARIANTE  très proche (≥ SEUIL_VARIANTE) — écart orthographique ou coupe
  ABSENT    introuvable dans la source citée  ← c'est la liste à traiter
  NON_RESOLU  référence non reconnue ou source indisponible

Usage
-----
  python3 scripts/verifier-citations.py                    # tout le site, FR
  python3 scripts/verifier-citations.py --langues fr,he,en
  python3 scripts/verifier-citations.py --path sources/shabbat/siman-297
  python3 scripts/verifier-citations.py --only-absent      # n'affiche que les ABSENT
  python3 scripts/verifier-citations.py --csv audit/citations-verifiees.csv

Sort non-zéro s'il reste des ABSENT (utilisable comme gate CI).
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


def fetch(ref):
    """Texte hébreu d'une référence Sefaria canonique, sous forme de liste de segments."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, hashlib.sha1(ref.encode()).hexdigest()[:20] + '.json')
    if os.path.exists(path):
        data = json.load(open(path, encoding='utf-8'))
    else:
        url = ('https://www.sefaria.org/api/v3/texts/'
               + urllib.parse.quote(ref, safe=',._-') + '?return_format=text_only')
        data = _get(url)
        json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    if 'error' in data:
        return None
    versions = data.get('versions') or []
    if not versions:
        return None
    heb = [v for v in versions if v.get('language') == 'he'] or versions

    def flat(x, out):
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, list):
            for y in x:
                flat(y, out)
        return out

    segs = flat(heb[0].get('text'), [])
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
    """Valeur numérique d'un nombre écrit en lettres hébraïques (ignore ״ et ׳)."""
    s = re.sub(r'["\'״׳]', '', s)
    if not s or any(c not in GEMATRIA for c in s):
        return None
    return sum(GEMATRIA[c] for c in s)


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
RE_INNER = re.compile(r'«([^«»]{15,700})»|"([^"]{15,700})"|„([^„”]{15,700})”')
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
        for m in RE_INNER.finditer(plain):
            block = next(g for g in m.groups() if g is not None).strip()
            # Un bloc marqué (<blockquote>, span.he-q) contient souvent un préfixe de
            # référence, la citation entre guillemets droits, puis un commentaire de
            # l'auteur. Dans ce cas seule la portion entre guillemets est la citation.
            inner = [s for s in re.findall(r'"([^"]{15,700})"', block) if is_hebrew_quote(s)]
            for frag in (inner or [block]):
                frag = RE_PREFIX.sub('', frag).strip(' —–-:.«»')
                if not is_hebrew_quote(frag):
                    continue
                # écarte les identifiants d'ancre (mots collés par des tirets)
                if re.fullmatch(r'[\wא-ת֐-׿-]+', frag):
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

    rows, stats = [], {'OK': 0, 'VARIANTE': 0, 'ABSENT': 0, 'NON_RESOLU': 0, 'SANS_REF': 0}
    cache_src = {}

    for path in pages(base, langues):
        text = open(path, encoding='utf-8').read()

        for frag, lineno, plain in quotes_in(text):
            # la référence accompagne presque toujours la citation sur la même ligne
            refs = refs_in(plain)
            if not refs:
                stats['SANS_REF'] += 1
                continue
            segs = []
            for r in refs[:3]:
                if r not in cache_src:
                    cache_src[r] = fetch(r) or []
                segs += cache_src[r]
            v, ratio, extract = verdict(frag, segs)
            stats[v] += 1
            if v == 'OK' or (args.only_absent and v != 'ABSENT'):
                continue

            rows.append({
                'fichier': os.path.relpath(path, ROOT), 'ligne': lineno,
                'refs': ' | '.join(refs[:3]), 'verdict': v, 'ratio': f'{ratio:.2f}',
                'citation': re.sub(r'\s+', ' ', frag)[:400],
                'source_reelle': re.sub(r'\s+', ' ', extract)[:400],
            })

    if args.csv:
        import csv as _csv
        out = args.csv if os.path.isabs(args.csv) else os.path.join(ROOT, args.csv)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', newline='', encoding='utf-8') as fh:
            w = _csv.DictWriter(fh, fieldnames=['fichier', 'ligne', 'refs', 'verdict',
                                                'ratio', 'citation', 'source_reelle'])
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r['verdict'] != 'ABSENT', r['fichier'], r['ligne'])))

    if not args.quiet:
        for r in sorted(rows, key=lambda r: (r['verdict'] != 'ABSENT', r['fichier'])):
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
    print(f"  ABSENTES de la source: {stats['ABSENT']}")
    if args.csv:
        print(f"  Détail              : {args.csv}")
    return 1 if stats['ABSENT'] else 0


if __name__ == '__main__':
    sys.exit(main())
