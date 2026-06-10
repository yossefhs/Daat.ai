#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit-vs-sefaria.py — Compare le texte des pages Niveau 1 (Base) avec le
texte de référence du Choulhan Aroukh (data/reference/choulhan-aroukh-oh-242-365.json,
extrait de Sefaria : Mehaber + hagahot du Rama, non vocalisé).

Pour chaque siman 242-365 :
  1. Extrait les blockquotes <blockquote class="text-source"> de la page FR
  2. Strip le nikud + normalise (abréviations, ponctuation, matres lectionis)
  3. Calcule la COUVERTURE : quelle proportion des mots de la référence
     se retrouve sur la page (matching par fenêtres de n-grammes)
  4. Détecte spécifiquement les hagahot du Rama absentes

Usage :
  python3 scripts/audit-vs-sefaria.py                 # rapport global
  python3 scripts/audit-vs-sefaria.py --detail 248    # détail d'un siman
  python3 scripts/audit-vs-sefaria.py --csv           # export CSV
  python3 scripts/audit-vs-sefaria.py --lang he       # autre langue (défaut fr)
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_PATH = ROOT / 'data' / 'reference' / 'choulhan-aroukh-oh-242-365.json'
SOURCES = ROOT / 'sources' / 'shabbat'

NIKUD = re.compile(r'[֑-ׇ]')
TAGS = re.compile(r'<[^>]+>')

# Mots dont l'orthographe varie entre la référence (abrégée) et le site (développée)
CANON = {
    'אפי': 'אפילו', "אפי'": 'אפילו',
    'מות': 'מותר', "מות'": 'מותר',
    'אסו': 'אסור',
    "אח\"כ": 'אחרכך', 'אחכ': 'אחרכך',
    "ע\"י": 'עלידי', 'עי': 'עלידי',
    "ע\"ש": 'ערבשבת', "בע\"ש": 'בערבשבת',
    "מע\"ש": 'מערבשבת',
    "וי\"א": 'וישאומרים', "י\"א": 'ישאומרים',
    "א\"י": 'ארץישראל',
    'שלש': 'שלוש', 'שלשה': 'שלושה',
    "ג'": 'שלושה', "ג": 'שלושה',
    "י'": 'עשרה',
    'מג': 'משלושה',
}


def strip_nikud(s: str) -> str:
    return NIKUD.sub('', s)


def norm_word(w: str) -> str:
    w = w.strip('.,:;()[]"\'׳״“”—–-')
    w = w.replace('״', '').replace('׳', '').replace('"', '').replace("'", '')
    if not w:
        return ''
    w = CANON.get(w, w)
    # Normalise lettres finales pour le matching (pas linguistique, juste robustesse)
    return w


def tokenize(text: str) -> list:
    text = strip_nikud(text)
    text = TAGS.sub(' ', text)
    # Garde seulement les lettres hébraïques et la ponctuation de séparation
    words = re.split(r'[\s ]+', text)
    out = []
    for w in words:
        # Vire tout ce qui n'est pas hébreu
        w = re.sub(r'[^א-ת\'"׳״]', '', w)
        w = norm_word(w)
        if w and re.search(r'[א-ת]', w):
            out.append(w)
    return out


def split_mehaber_rama(seif_text: str) -> tuple:
    """Sépare un séif de la référence en (mehaber, [hagahot])."""
    clean = TAGS.sub(' ', seif_text)
    parts = re.split(r'(הגה)', clean)
    mehaber = parts[0]
    hagahot = []
    i = 1
    while i < len(parts):
        if parts[i] == 'הגה' and i + 1 < len(parts):
            hagahot.append(parts[i + 1])
            i += 2
        else:
            i += 1
    return mehaber, hagahot


def coverage(ref_tokens: list, page_tokens_set: set, page_bigrams: set) -> float:
    """% des bigrammes de la référence présents sur la page."""
    if len(ref_tokens) < 2:
        return 1.0 if all(t in page_tokens_set for t in ref_tokens) else 0.0
    ref_bigrams = [(ref_tokens[i], ref_tokens[i + 1]) for i in range(len(ref_tokens) - 1)]
    hit = sum(1 for b in ref_bigrams if b in page_bigrams)
    return hit / len(ref_bigrams)


def missing_segments(ref_tokens: list, page_bigrams: set, min_len: int = 5) -> list:
    """Retourne les segments consécutifs de la référence absents de la page."""
    segs = []
    cur = []
    for i in range(len(ref_tokens) - 1):
        big = (ref_tokens[i], ref_tokens[i + 1])
        if big not in page_bigrams:
            if not cur:
                cur = [ref_tokens[i]]
            cur.append(ref_tokens[i + 1])
        else:
            if len(cur) >= min_len:
                segs.append(' '.join(cur))
            cur = []
    if len(cur) >= min_len:
        segs.append(' '.join(cur))
    return segs


def page_path(siman: int, lang: str) -> Path:
    suffix = {'fr': '', 'he': '-he', 'en': '-en'}[lang]
    return SOURCES / f'siman-{siman}' / f'niveau-1-base{suffix}.html'


def extract_page_tokens(siman: int, lang: str) -> list:
    p = page_path(siman, lang)
    if not p.exists():
        return None
    html = p.read_text(encoding='utf-8')
    # Tous les blockquotes text-source + sacred-text (texte hébreu cité)
    bqs = re.findall(r'<blockquote[^>]*>(.*?)</blockquote>', html, flags=re.S)
    divs = re.findall(r'<div class="(?:sacred-text|he)"[^>]*>(.*?)</div>', html, flags=re.S)
    tokens = []
    for b in bqs + divs:
        tokens.extend(tokenize(b))
    return tokens


def audit_siman(siman: int, ref: dict, lang: str) -> dict:
    seifim = ref['simanim'].get(str(siman))
    if not seifim:
        return None
    page_tokens = extract_page_tokens(siman, lang)
    if page_tokens is None:
        return {'siman': siman, 'error': 'page absente'}
    page_set = set(page_tokens)
    page_bigrams = set((page_tokens[i], page_tokens[i + 1]) for i in range(len(page_tokens) - 1))

    rows = []
    for idx, seif_text in enumerate(seifim, 1):
        mehaber, hagahot = split_mehaber_rama(seif_text)
        m_tokens = tokenize(mehaber)
        m_cov = coverage(m_tokens, page_set, page_bigrams)
        h_results = []
        for h in hagahot:
            h_tokens = tokenize(h)
            h_cov = coverage(h_tokens, page_set, page_bigrams)
            h_results.append({'cov': h_cov, 'len': len(h_tokens),
                              'missing': missing_segments(h_tokens, page_bigrams) if h_cov < 0.7 else []})
        rows.append({
            'seif': idx,
            'mehaber_cov': m_cov,
            'mehaber_len': len(m_tokens),
            'mehaber_missing': missing_segments(m_tokens, page_bigrams) if m_cov < 0.7 else [],
            'hagahot': h_results,
        })
    return {'siman': siman, 'seifim': rows}


def verdict(row: dict) -> str:
    """Verdict pour un séif."""
    bad_h = [h for h in row['hagahot'] if h['cov'] < 0.5 and h['len'] >= 4]
    weak_h = [h for h in row['hagahot'] if 0.5 <= h['cov'] < 0.8 and h['len'] >= 4]
    if row['mehaber_cov'] < 0.5 and row['mehaber_len'] >= 8:
        return 'MEHABER-MISSING'
    if bad_h:
        return 'RAMA-MISSING'
    if row['mehaber_cov'] < 0.8 and row['mehaber_len'] >= 8:
        return 'MEHABER-PARTIAL'
    if weak_h:
        return 'RAMA-PARTIAL'
    return 'OK'


SEVERITY = {'MEHABER-MISSING': 3, 'RAMA-MISSING': 3, 'MEHABER-PARTIAL': 2, 'RAMA-PARTIAL': 1, 'OK': 0}


def main():
    args = sys.argv[1:]
    lang = 'fr'
    if '--lang' in args:
        lang = args[args.index('--lang') + 1]
    detail = None
    if '--detail' in args:
        detail = int(args[args.index('--detail') + 1])
    as_csv = '--csv' in args

    ref = json.loads(REF_PATH.read_text(encoding='utf-8'))

    if detail:
        r = audit_siman(detail, ref, lang)
        if not r or r.get('error'):
            print(f"Siman {detail}: {r.get('error') if r else 'pas dans la référence'}")
            return
        print(f"=== Siman {detail} — couverture vs référence Choulhan Aroukh ({lang.upper()}) ===\n")
        for row in r['seifim']:
            v = verdict(row)
            print(f"Seif {row['seif']:>2} [{v}] Mehaber {row['mehaber_cov']*100:5.1f}% ({row['mehaber_len']} mots)"
                  + (f" | {len(row['hagahot'])} hagah(ot): " + ', '.join(f"{h['cov']*100:.0f}%" for h in row['hagahot'])
                     if row['hagahot'] else " | pas de hagah"))
            for seg in row['mehaber_missing'][:3]:
                print(f"     ✗ Mehaber absent : {seg[:90]}")
            for h in row['hagahot']:
                for seg in h['missing'][:3]:
                    print(f"     ✗ Rama absent    : {seg[:90]}")
        return

    results = []
    for siman in range(242, 366):
        r = audit_siman(siman, ref, lang)
        if r and not r.get('error'):
            results.append(r)

    if as_csv:
        print("siman,seif,verdict,mehaber_cov,n_hagahot,hagahot_cov")
        for r in results:
            for row in r['seifim']:
                hcov = ';'.join(f"{h['cov']:.2f}" for h in row['hagahot'])
                print(f"{r['siman']},{row['seif']},{verdict(row)},{row['mehaber_cov']:.2f},{len(row['hagahot'])},{hcov}")
        return

    # Rapport global
    counts = {}
    siman_sev = []
    total_seifim = 0
    for r in results:
        sev = 0
        flags = []
        for row in r['seifim']:
            v = verdict(row)
            counts[v] = counts.get(v, 0) + 1
            total_seifim += 1
            sev += SEVERITY[v]
            if v != 'OK':
                flags.append(f"s{row['seif']}:{v}")
        siman_sev.append((sev, r['siman'], flags))

    print(f"=== Audit vs référence Choulhan Aroukh — Niveau 1 ({lang.upper()}) ===\n")
    print(f"Simanim audités : {len(results)} / 124")
    print(f"Séifim audités  : {total_seifim}\n")
    for v in ['OK', 'RAMA-PARTIAL', 'MEHABER-PARTIAL', 'RAMA-MISSING', 'MEHABER-MISSING']:
        print(f"  {v:<16}: {counts.get(v, 0)}")
    nb_clean = sum(1 for s, _, f in siman_sev if s == 0)
    print(f"\nSimanim 100% conformes : {nb_clean} / {len(results)}")
    print(f"\n=== Top 30 simanim à corriger (par gravité) ===")
    for sev, siman, flags in sorted(siman_sev, reverse=True)[:30]:
        if sev == 0:
            break
        print(f"  {siman} (sev {sev:>2}) : {', '.join(flags[:8])}{'…' if len(flags) > 8 else ''}")


if __name__ == '__main__':
    main()
