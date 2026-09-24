#!/usr/bin/env python3
"""Une citation qui SAUTE un passage de sa source sans le dire — la porte née d'un cas témoin.

LE CAS TÉMOIN, 24 septembre 2026. En triant les 267 citations que
`verifier-fabrications.py` rend « introuvables » dans Hilkhot Chabbat, une d'elles
résistait à toutes les explications : « ונוהגין ללוש כדי שעור חלה בבית… »
(siman 242, niveau 4, FR et EN). C'est pourtant le Rama, mot pour mot, sur
Orah Haïm 242. Le diagnostic est tombé au caractère 45 du squelette consonantique :

    la source  …בשבת ויום טוב [סמך ממרדכי ריש מסכת ר״ה] והוא מכבוד שבת…
    la page    …בשבת ויום טוב, והוא מכבוד שבת…

La page saute le crochet de source que Sefaria place À L'INTÉRIEUR du texte du Rama,
et recolle les deux morceaux **sans points de suspension**, le tout entre guillemets.

POURQUOI AUCUNE AUTRE PORTE NE LE VOIT.
· `verifier-citations.py` cherche la citation dans la source : elle n'y est pas telle
  quelle, donc il la rend ABSENTE — le même verdict que pour une phrase inventée. Le
  lecteur du rapport ne peut pas distinguer les deux, et la pile devient inexploitable.
· `verifier-fabrications.py` demande à la recherche plein texte si la suite de mots
  existe : elle n'existe pas sous cette forme, donc « introuvable ». Même confusion.
· `verify-chabbat-source.py` et `verify-yd-source.py` jugent la RECOPIE du texte de base
  (les blockquote du niveau 1), pas les citations que les niveaux 2, 3 et 4 en tirent.

CE QUE CELLE-CI FAIT. Elle ancre la citation PAR LES DEUX BOUTS dans un même segment de
source : plus long préfixe, plus long suffixe. Quand les deux sont substantiels et que
leur somme couvre la citation, le texte existe des deux côtés d'un trou — et le trou est
imprimable. La porte dit alors ce qui a été sauté.

Une ellipse MARQUE la coupure, et la convention du dépôt le prévoit : « A… B » signifie
que A et B sont chacun verbatim. Une citation qui porte une ellipse est donc découpée à
l'ellipse et chaque morceau jugé seul, exactement comme le fait `verifier-fabrications.py`.
Ce que cette porte cherche, c'est la coupure NON MARQUÉE.

ELLE REND DES CANDIDATS. Un trou peut être une variante d'édition — Sefaria n'est pas
l'édition que la page suit. Mais un crochet de source sauté, une clause retirée du milieu
d'un verbatim, une parenthèse d'attribution perdue sont chacun un défaut, et tous se
réparent de la même manière : rétablir le passage, ou écrire « … ».

Usage :
  python3 scripts/verifier-troncatures.py --path sources/shabbat/siman-242
  python3 scripts/verifier-troncatures.py --section shabbat [--bref]
  python3 scripts/verifier-troncatures.py 242 243 244
"""
import re, sys, os, json, glob, time, urllib.request, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache-troncatures.json")

# On réutilise l'extracteur de citations de la porte anti-fabrication : une porte qui
# n'extrait pas les MÊMES citations qu'une autre est une porte qui compare autre chose.
_spec = importlib.util.spec_from_file_location(
    "vf", os.path.join(ROOT, "scripts", "verifier-fabrications.py"))
_vf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vf)
citations = _vf.citations

NIK = re.compile('[֑-ׇ]')
def sk(s):
    """Squelette consonantique, avec l'index de chaque consonne dans la chaîne d'origine."""
    out, idx = [], []
    for i, c in enumerate(NIK.sub(lambda m: '\u0000' * len(m.group()), s)):
        if 'א' <= c <= 'ת':
            out.append(c); idx.append(i)
    return ''.join(out), idx

def nomat_idx(chaine, idx):
    """La même chaîne sans matres lectionis, et l'index d'origine de chaque consonne.

    Le ktiv haser/malé est le faux positif dominant de tout ce dépôt : la MÊME phrase
    s'écrit מתר ou מותר, שעור ou שיעור. On neutralise donc le yod et le vav — mais en
    gardant la trace de l'index d'origine, faute de quoi le trou ne serait plus
    imprimable et la porte ne dirait pas ce qui a été sauté.
    """
    o, oi = [], []
    for c, i in zip(chaine, idx):
        if c in 'יו': continue
        o.append(c); oi.append(i)
    return ''.join(o), oi

def nomat(s): return re.sub(r'[יו]', '', s)

# L'appareil d'un siman. Le champ `ref` est contrôlé à chaque téléchargement : les formes
# X_on_Shulchan_Arukh,_Orach_Chayim.N rendent l'ŒUVRE ENTIÈRE avec un HTTP 200 et un `ref`
# sans numéro, et qui lit he[4] y lit le cinquième siman.
OEUVRES = {
    'or': 'Shulchan_Arukh,_Orach_Chayim.{n}',
    'yd': "Shulchan_Arukh,_Yoreh_De'ah.{n}",
}
APPAREIL_OR = ['Mishnah_Berurah.{n}', 'Magen_Avraham.{n}',
               'Turei_Zahav_on_Shulchan_Arukh,_Orach_Chayim.{n}', 'Biur_Halacha.{n}',
               'Beit_Yosef,_Orach_Chaim.{n}', 'Shulchan_Arukh_HaRav,_Orach_Chayim.{n}']
APPAREIL_YD = ["Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Turei_Zahav_on_Shulchan_Arukh,_Yoreh_De'ah.{n}",
               "Beit_Yosef,_Yoreh_Deah.{n}"]

def plat(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return ' '.join(plat(y) for y in x)
    return ''

_cache = {}
if os.path.exists(CACHE):
    try: _cache = json.load(open(CACHE, encoding='utf-8'))
    except Exception: _cache = {}

def appareil(n, section):
    """[(ref, texte brut)] — le texte est gardé BRUT pour pouvoir imprimer le trou."""
    cle = f'{section}:{n}'
    if cle in _cache: return _cache[cle]
    modeles = ([OEUVRES['yd']] + APPAREIL_YD) if section == 'yoreh-deah' \
              else ([OEUVRES['or']] + APPAREIL_OR)
    out = []
    for m in modeles:
        url = f'https://www.sefaria.org/api/texts/{m.format(n=n)}?context=0&pad=0'
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = json.load(r)
            ref = str(d.get('ref', ''))
            if not ref.rstrip().endswith(str(n)):
                continue                      # le piège : l'œuvre entière sans dire non
            he = d.get('he')
            for b in (he if isinstance(he, list) else [he]):
                t = re.sub(r'<[^>]+>', ' ', plat(b))
                t = re.sub(r'\s+', ' ', t).strip()
                if t: out.append((ref, t))
        except Exception:
            pass
        time.sleep(0.12)
    _cache[cle] = out
    try: json.dump(_cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception: pass
    return out

def _prefixe(s, cible):
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if s[:mid] in cible: lo = mid
        else: hi = mid - 1
    return lo

def _suffixe(s, cible):
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if s[-mid:] in cible: lo = mid
        else: hi = mid - 1
    return lo

ANCRE_MIN = 12          # sous douze consonnes, un ancrage ne prouve rien
COUVERTURE_MIN = 0.85   # préfixe + suffixe doivent couvrir presque toute la citation

ANCRE_MIN = 12          # sous douze consonnes, un ancrage ne prouve rien
COUVERTURE_MIN = 0.85   # préfixe + suffixe doivent couvrir presque toute la citation
TROU_MIN = 4            # en deçà, c'est une variante d'orthographe, pas un passage sauté

def juger(cit, segs):
    """None si rien à dire ; sinon (ref, sauté, pref, suff).

    L'ancrage se fait DEUX FOIS, sur le squelette strict et sur le squelette sans matres
    lectionis. Le premier cas témoin de cette porte l'exigeait : la page écrit וְנוֹהֲגִין
    là où le Rama écrit נוהגין, si bien que le préfixe strict tombe au premier caractère
    et que le trou du milieu — le crochet [סמך ממרדכי ריש מסכת ר״ה] — reste invisible.
    """
    s0, _ = sk(cit)
    if len(s0) < 20: return None
    meilleur = None
    for ref, brut in segs:
        b0, b0idx = sk(brut)
        s1, _ = nomat_idx(s0, list(range(len(s0))))
        b1, b1idx_ = nomat_idx(b0, list(range(len(b0))))
        if s0 in b0 or s1 in b1:
            return None                       # présente : rien à signaler
        for chaine, cible, vers_b0 in ((s0, b0, None), (s1, b1, b1idx_)):
            p, q = _prefixe(chaine, cible), _suffixe(chaine, cible)
            if p < ANCRE_MIN or q < ANCRE_MIN: continue
            if p + q < len(chaine) * COUVERTURE_MIN: continue
            i = cible.find(chaine[:p]) + p
            j = cible.rfind(chaine[-q:])
            if j - i < TROU_MIN: continue     # chevauchement ou variante d'orthographe
            # ramener les bornes sur le squelette strict, puis sur le texte brut
            bi = i if vers_b0 is None else vers_b0[i]
            bj = j if vers_b0 is None else vers_b0[j]
            if bj >= len(b0idx): continue
            saute = brut[b0idx[bi]:b0idx[bj]].strip()
            if len(sk(saute)[0]) < TROU_MIN: continue
            if meilleur is None or p + q > meilleur[2] + meilleur[3]:
                meilleur = (ref, saute, p, q)
    return meilleur

def simanim(path):
    for d in sorted(glob.glob(os.path.join(path, 'siman-*'))):
        m = re.search(r'siman-(\d+)$', d)
        if m: yield int(m.group(1)), d

def main():
    argv = sys.argv[1:]
    bref = '--bref' in argv
    section = None
    cibles = []
    if '--path' in argv:
        p = os.path.join(ROOT, argv[argv.index('--path') + 1])
        section = 'yoreh-deah' if 'yoreh-deah' in p else ('shabbat' if 'shabbat' in p else 'orah-haim')
        if re.search(r'siman-\d+$', p):
            m = re.search(r'siman-(\d+)$', p); cibles = [(int(m.group(1)), p)]
        else:
            cibles = list(simanim(p))
    elif '--section' in argv:
        section = argv[argv.index('--section') + 1]
        cibles = list(simanim(os.path.join(ROOT, 'sources', section)))
    else:
        nums = [int(a) for a in argv if a.isdigit()]
        for n in nums:
            for sec in ('shabbat', 'orah-haim', 'yoreh-deah'):
                d = os.path.join(ROOT, 'sources', sec, f'siman-{n}')
                if os.path.isdir(d): cibles.append((n, d)); section = sec; break
    if not cibles:
        print(__doc__.strip().split('Usage :')[-1]); return 2

    total = trouve = 0
    for n, d in cibles:
        sec = 'yoreh-deah' if 'yoreh-deah' in d else ('shabbat' if 'shabbat' in d else 'orah-haim')
        segs = None
        vues = set()
        for f in sorted(glob.glob(os.path.join(d, '*.html'))):
            for c in citations(f):
                if c in vues: continue
                vues.add(c)
                if segs is None: segs = appareil(n, sec)
                total += 1
                r = juger(c, segs)
                if r:
                    trouve += 1
                    ref, saute, p, q = r
                    print(f"✗ siman {n} · {os.path.basename(f)}")
                    print(f"   « {c[:150]} »")
                    print(f"   {ref} : {p} consonnes au début + {q} à la fin, et entre les deux")
                    print(f"   la source porte — SAUTÉ SANS ELLIPSE : [{saute[:160]}]")
                    if not bref: print()
    print(f"\nCitations confrontées : {total}")
    print(f"Coupures NON MARQUÉES : {trouve}")
    if not trouve:
        print("\nAucune citation ne saute un passage de sa source sans le dire.")
    else:
        print("\nUne ellipse marque la coupure : « A… B » dit que A et B sont chacun verbatim.")
        print("Le remède est l'un des deux — rétablir le passage, ou écrire « … ».")
    return 1 if trouve else 0

if __name__ == '__main__':
    sys.exit(main())
