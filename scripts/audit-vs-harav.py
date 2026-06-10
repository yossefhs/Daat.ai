#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit-vs-harav.py — Compare le texte des pages Niveau 4 (Daat HaRav) avec la
référence du Choulhan Aroukh HaRav (data/reference/choulhan-aroukh-harav-242-365.json,
édition Kehot vocalisée, extraite de Sefaria).

ATTENTION — le Niveau 4 n'est PAS une retranscription mot-à-mot du HaRav (à
la différence du Niveau 1 vs Choulhan Aroukh). C'est une étude analytique de
la Shitah de l'Admour HaZaken : la page peut citer le HaRav en extraits, le
résumer, ou discuter sa Shitah sans tout citer. Un faible % de couverture
n'est PAS forcément une erreur. Le script cherche surtout :
  - les séifim entièrement absents (couverture < 5% : HaRav non cité du tout)
  - les séifim avec une longue citation présentée comme du HaRav mais
    tronquée massivement (un long sa-he avec couverture < 30% ⇒ suspect)
  - les passages d'au moins 5 mots consécutifs du HaRav absents de la page,
    pour repérer les troncatures de blockquote (à la N1).

Heuristique : pour chaque seif on extrait TOUS les <p class="sa-he"> du
container <details class="seif-details"> correspondant. On classe le seif :
  OK              : couverture ≥ 30%  (ou citation très courte ≤ 20 mots et OK partiel)
  HARAV-PARTIAL   : 5% ≤ couverture < 30% ET on présente une vraie citation longue
  HARAV-MISSING   : couverture < 5%   ET sa-he non vide (paraphrase ?)
  HARAV-ABSENT    : aucun sa-he du tout pour ce seif (seif absent de la page)
  HARAV-NOPAGE    : page Niveau 4 manquante (304, 322 ou autre)

Usage :
  python3 scripts/audit-vs-harav.py                 # rapport global FR
  python3 scripts/audit-vs-harav.py --detail 248    # détail d'un siman
  python3 scripts/audit-vs-harav.py --csv           # export CSV
  python3 scripts/audit-vs-harav.py --lang he       # autre langue (défaut fr)
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_PATH = ROOT / 'data' / 'reference' / 'choulhan-aroukh-harav-242-365.json'
SOURCES = ROOT / 'sources' / 'shabbat'

NIKUD = re.compile(r'[֑-ׇ]')
TAGS = re.compile(r'<[^>]+>')

# Mots dont l'orthographe varie entre la référence (abrégée) et le site (développée)
# Réutilisé d'audit-vs-sefaria.py + complété pour les particularités du HaRav.
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
    "ת\"ח": 'תלמידחכם',
    "ב\"ד": 'ביתדין',
    "כ\"כ": 'כךכך',
    "ר\"ה": 'ראשהשנה',
    "וכו'": '',
    "ז\"ל": '',
    "וכיוצא": 'וכיוצא',
    'שלש': 'שלוש', 'שלשה': 'שלושה',
    "ג'": 'שלושה', "ג": 'שלושה',
    "י'": 'עשרה',
    "ד'": 'ארבעה',
    "ה'": 'חמישה',
    "ו'": 'ששה',
    "ז'": 'שבעה',
    "ח'": 'שמונה',
    "ט'": 'תשעה',
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
    return w


def tokenize(text: str) -> list:
    text = strip_nikud(text)
    text = TAGS.sub(' ', text)
    words = re.split(r'[\s ]+', text)
    out = []
    for w in words:
        w = re.sub(r'[^א-ת\'"׳״]', '', w)
        w = norm_word(w)
        if w and re.search(r'[א-ת]', w):
            out.append(w)
    return out


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
    return SOURCES / f'siman-{siman}' / f'niveau-4-daat-harav{suffix}.html'


# Découpe le HTML en blocs <details class="seif-details">…</details>
# tolérant aux imbrications (on s'appuie sur la structure plate observée).
DETAILS_OPEN = re.compile(r'<details class="seif-details"[^>]*>')
SAHE_RE = re.compile(r'<p class="sa-he"[^>]*>(.*?)</p>', flags=re.S)


def split_seif_blocks(html: str) -> list:
    """Retourne la liste des contenus HTML de chaque <details class="seif-details">.

    Les blocs ne sont pas imbriqués dans les pages auditées (structure plate
    confirmée sur un échantillon : siman-248, 280, 310, 340…). On extrait par
    balayage simple jusqu'au </details> de profondeur 0.
    """
    blocks = []
    pos = 0
    while True:
        m = DETAILS_OPEN.search(html, pos)
        if not m:
            break
        start = m.end()
        depth = 1
        i = start
        # Balayage caractère par caractère via regex pour les ouvertures/fermetures
        token_re = re.compile(r'<details[^>]*>|</details>')
        while depth > 0:
            tm = token_re.search(html, i)
            if not tm:
                # Pas de </details> de fermeture → on coupe au bout
                blocks.append(html[start:])
                pos = len(html)
                break
            if tm.group().startswith('</'):
                depth -= 1
                if depth == 0:
                    blocks.append(html[start:tm.start()])
                    pos = tm.end()
                    break
                i = tm.end()
            else:
                depth += 1
                i = tm.end()
        else:
            continue
    return blocks


def extract_seif_tokens(html: str) -> list:
    """Retourne, pour chaque seif-details, la liste des tokens hébreux de ses sa-he."""
    blocks = split_seif_blocks(html)
    seifim = []
    for b in blocks:
        sa_he_chunks = SAHE_RE.findall(b)
        tokens = []
        for chunk in sa_he_chunks:
            tokens.extend(tokenize(chunk))
        seifim.append({'tokens': tokens, 'n_blocks': len(sa_he_chunks)})
    return seifim


def audit_siman(siman: int, ref: dict, lang: str) -> dict:
    seifim_ref = ref['simanim'].get(str(siman))
    if seifim_ref is None or len(seifim_ref) == 0:
        return None  # 304/322 vides ou hors corpus
    p = page_path(siman, lang)
    if not p.exists():
        return {'siman': siman, 'error': 'page absente'}
    html = p.read_text(encoding='utf-8')
    page_seifim = extract_seif_tokens(html)

    rows = []
    for idx, ref_text in enumerate(seifim_ref, 1):
        r_tokens = tokenize(ref_text)
        if idx - 1 < len(page_seifim):
            page_block = page_seifim[idx - 1]
            p_tokens = page_block['tokens']
            n_blocks = page_block['n_blocks']
        else:
            p_tokens = []
            n_blocks = 0
        p_set = set(p_tokens)
        p_bigrams = set((p_tokens[i], p_tokens[i + 1]) for i in range(len(p_tokens) - 1))
        cov = coverage(r_tokens, p_set, p_bigrams) if p_tokens else 0.0
        missing = missing_segments(r_tokens, p_bigrams, min_len=5) if cov < 0.7 else []
        rows.append({
            'seif': idx,
            'cov': cov,
            'ref_len': len(r_tokens),
            'page_len': len(p_tokens),
            'n_sa_he_blocks': n_blocks,
            'missing': missing,
        })
    # On note aussi les seifim "en trop" sur la page (n_seif-details > référence)
    extra = max(0, len(page_seifim) - len(seifim_ref))
    return {'siman': siman, 'seifim': rows, 'extra_blocks': extra,
            'n_page_seifim': len(page_seifim), 'n_ref_seifim': len(seifim_ref)}


def verdict(row: dict) -> str:
    """Verdict adapté au N4 :
      - HARAV-NOPAGE    : géré au niveau du siman
      - HARAV-ABSENT    : aucun sa-he pour ce seif (séif absent de la page)
      - HARAV-MISSING   : sa-he présent mais couverture < 5% (paraphrase ?)
      - HARAV-PARTIAL   : 5% ≤ couverture < 30% ET citation longue (>40 mots du HaRav présentés)
      - OK              : sinon
    Note : pour des séifim de référence très courts (<6 mots), on tolère tout.
    """
    if row['ref_len'] < 6:
        return 'OK'
    if row['n_sa_he_blocks'] == 0:
        return 'HARAV-ABSENT'
    if row['cov'] < 0.05:
        return 'HARAV-MISSING'
    # Citation longue ET couverture faible ⇒ suspect (vraisemblablement
    # un blockquote tronqué ou paraphrasé).
    if row['cov'] < 0.30 and row['page_len'] >= 40:
        return 'HARAV-PARTIAL'
    return 'OK'


SEVERITY = {'HARAV-ABSENT': 4, 'HARAV-MISSING': 3, 'HARAV-PARTIAL': 2, 'OK': 0}


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
        if r is None:
            print(f"Siman {detail}: vide chez HaRav (pas de N4 attendu)")
            return
        if r.get('error'):
            print(f"Siman {detail}: {r['error']}")
            return
        print(f"=== Siman {detail} — couverture vs Choulhan Aroukh HaRav ({lang.upper()}) ===")
        print(f"Référence : {r['n_ref_seifim']} séifim · Page : {r['n_page_seifim']} blocs seif-details"
              + (f" (+{r['extra_blocks']} blocs en trop)" if r['extra_blocks'] else "") + "\n")
        for row in r['seifim']:
            v = verdict(row)
            print(f"Seif {row['seif']:>2} [{v:<14}] cov {row['cov']*100:5.1f}% · ref {row['ref_len']:>3} mots · page {row['page_len']:>3} mots · {row['n_sa_he_blocks']} bloc(s) sa-he")
            for seg in row['missing'][:3]:
                print(f"     ✗ Absent ({len(seg.split())} mots) : {seg[:120]}")
        return

    results = []
    no_page = []
    for siman_str, seifim_ref in ref['simanim'].items():
        siman = int(siman_str)
        if not seifim_ref:
            continue  # 304/322
        r = audit_siman(siman, ref, lang)
        if r is None:
            continue
        if r.get('error'):
            no_page.append(siman)
            continue
        results.append(r)

    if as_csv:
        print("siman,seif,verdict,cov,ref_len,page_len,n_sa_he_blocks,extra_blocks")
        for r in results:
            for row in r['seifim']:
                print(f"{r['siman']},{row['seif']},{verdict(row)},{row['cov']:.3f},{row['ref_len']},{row['page_len']},{row['n_sa_he_blocks']},{r['extra_blocks']}")
        return

    # Rapport global
    counts = {}
    siman_sev = []
    total_seifim = 0
    cov_sum = 0.0
    cov_n = 0
    for r in results:
        sev = 0
        flags = []
        for row in r['seifim']:
            v = verdict(row)
            counts[v] = counts.get(v, 0) + 1
            total_seifim += 1
            sev += SEVERITY[v]
            cov_sum += row['cov']
            cov_n += 1
            if v != 'OK':
                flags.append(f"s{row['seif']}:{v.split('-')[-1]}")
        siman_sev.append((sev, r['siman'], flags, r['extra_blocks']))

    print(f"=== Audit vs Choulhan Aroukh HaRav — Niveau 4 ({lang.upper()}) ===\n")
    print(f"Simanim audités : {len(results)} / 122 (304 et 322 exclus = pas de HaRav)")
    if no_page:
        print(f"Pages manquantes  : {len(no_page)} ({', '.join(str(s) for s in no_page[:10])}{'…' if len(no_page) > 10 else ''})")
    print(f"Séifim audités  : {total_seifim}")
    print(f"Couverture moy. : {cov_sum / max(1, cov_n) * 100:.1f}%  (médiocre attendue : le N4 est analytique, pas mot-à-mot)\n")
    for v in ['OK', 'HARAV-PARTIAL', 'HARAV-MISSING', 'HARAV-ABSENT']:
        n = counts.get(v, 0)
        pct = n * 100 / max(1, total_seifim)
        print(f"  {v:<16}: {n:>4}  ({pct:5.1f}%)")
    nb_clean = sum(1 for s, _, f, _ in siman_sev if s == 0)
    print(f"\nSimanim 100% conformes : {nb_clean} / {len(results)}")
    print(f"\n=== Top 30 simanim suspects (par gravité) ===")
    for sev, siman, flags, extra in sorted(siman_sev, reverse=True)[:30]:
        if sev == 0:
            break
        extra_str = f" [+{extra} blocs en trop]" if extra else ""
        print(f"  {siman} (sev {sev:>3}){extra_str} : {', '.join(flags[:10])}{'…' if len(flags) > 10 else ''}")


if __name__ == '__main__':
    main()
