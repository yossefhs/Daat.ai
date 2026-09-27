#!/usr/bin/env python3
"""L'étiquette d'une cellule de niveau 4 nomme-t-elle un séif qui porte ce qu'elle annonce ?

D'OÙ ELLE VIENT. Les tableaux comparatifs du niveau 4 rangent la source par colonne
— Mehaber, Rama, Michna Beroura — et posent au-dessus de chaque cellule une étiquette :
« OH 243:2 », « Hagaha sur OH 243:2 », « MB 242:3-4 ». Le contenu de la cellule est le
plus souvent une CONDENSATION, introduite par `<em>résumé</em> :`, que la convention du
dépôt exempte à bon droit de la porte du verbatim — une condensation n'est pas une
citation. Mais l'exemption laisse deux trous que rien ne surveillait :

  · une condensation peut être FAUSSE (le siman 247 en porte une qui inverse le psak :
    elle attache la condition du בי דואר au cas où l'on a fixé un prix, alors que le
    Mehaber ne l'ouvre qu'« ואם לא קצב ») ;
  · et l'ÉTIQUETTE elle-même peut mentir — au siman 243, une cellule annonce
    « Hagaha sur OH 243:2 » alors que le Rama n'a AUCUNE glose sur ce séif ; au 249,
    « OH 249:2-3 » pour un psak que le séif ב ne dit pas et que le séif ג contredit.

La première question ne se tranche pas mécaniquement, et cette porte ne la pose pas.
LA SECONDE, SI. Le séif annoncé existe-t-il ? Porte-t-il une glose du Rama quand la
cellule en promet une ? Le ס״ק annoncé existe-t-il dans la Michna Beroura de ce siman ?
Trois questions fermées, vérifiables, et qui ont déjà trouvé des défauts à la main.

Elle rend des ANOMALIES là où la réponse est non, et des CANDIDATS là où l'étiquette
nomme un siman autre que celui de la page — ce qui est licite mais rare, et mérite l'œil.

Usage :
  python3 scripts/verifier-etiquettes.py --section shabbat [--bref]
  python3 scripts/verifier-etiquettes.py 243 245 249
"""
import re, sys, os, io, json, glob, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache-etiquettes.json")

RXTD = re.compile(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', re.S | re.I)

# ⚠️ CE QUE LA PREMIÈRE VERSION NE LISAIT PAS, ET POURQUOI SON VERT MENTAIT.
# Elle n'acceptait que des chiffres ARABES. Or les tableaux des fichiers HÉBREUX écrivent
# leurs adresses en numération hébraïque — « או״ח רמ״ז:א », « מ״ב רמ״ט ס״ק יד » — et les
# fichiers français et anglais emploient aussi la forme MIXTE « MB 248 ס״ק ד ». Aucune n'a
# jamais été confrontée. Trois agents de contrôle l'ont établi indépendamment ; au siman 264,
# QUATRE des cinq adresses fausses réelles étaient hors de portée. Le premier chiffre publié —
# « 26 anomalies sur 7 simanim » — était donc un PLANCHER annoncé comme un compte.
# Et la colonne du Choulhan Aroukh HaRav n'était pas lue du tout, alors que c'est elle qui
# portait, au siman 249, une adresse (« רמ״ט:6-8 ») renvoyant à un sujet absent du siman.
NB = r'(?:\d{1,3}|[\u05D0-\u05EA]{1,4}(?:["\u05F4][\u05D0-\u05EA])?)'
TIRET = r'(?:\s*[-–—]\s*)'
OH = r'(?:OH|OC|או["\u05F4]?ח|אורח חיים)'

RX_HAGAHA = re.compile(r'(?:Hagahah?|Gloss|הגהה|הגה(?![\u05D0-\u05EA]))\s*(?:sur|on|על)?\s*'
                       rf'{OH}\s*({NB})\s*[:\u05C3]\s*({NB})(?:{TIRET}({NB}))?', re.I)
RX_SEIF   = re.compile(rf'(?<![\w:\u05D0-\u05EA]){OH}\s*({NB})\s*[:\u05C3]\s*({NB})'
                       rf'(?:{TIRET}({NB}))?', re.I)
# « MB 242:3-4 », « מ״ב רמ״ט:יד », « MB 248 ס״ק ד », « משנ״ב רס״ד ס״ק כג »
MBW = r'(?:MB|מ["\u05F4]ב|משנ["\u05F4]ב|משנה ברורה)'
RX_MB     = re.compile(rf'(?<![\w:\u05D0-\u05EA]){MBW}\s*({NB})\s*'
                       rf'(?:[:\u05C3]|ס["\u05F4]?ק|סעיף\s*קטן)\s*({NB})(?:{TIRET}({NB}))?')
# La colonne du Choulhan Aroukh HaRav : « שו״ע הרב רמ״ט:יב », « רמ״ט:6-8 » dans sa cellule.
RAVW = r'(?:שו["\u05F4]ע הרב|שוע["\u05F4]ר|אדמו["\u05F4]ר הזקן|ש["\u05F4]ע אדה["\u05F4]ז|SA HaRav)'
RX_RAV    = re.compile(rf'{RAVW}\s*(?:{OH}\s*)?({NB})\s*[:\u05C3]\s*({NB})(?:{TIRET}({NB}))?')

GEM = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'כ':20,'ך':20,'ל':30,
       'מ':40,'ם':40,'נ':50,'ן':50,'ס':60,'ע':70,'פ':80,'ף':80,'צ':90,'ץ':90,'ק':100,
       'ר':200,'ש':300,'ת':400}
def _num(t):
    """Un numéro d'étiquette, arabe ou hébraïque. None si ce n'est ni l'un ni l'autre."""
    t = (t or '').strip()
    if re.fullmatch(r'\d{1,3}', t): return int(t)
    lettres = re.sub(r'[^\u05D0-\u05EA]', '', t)
    if not lettres: return None
    v = sum(GEM.get(c, 0) for c in lettres)
    return v or None

_cache = {}
if os.path.exists(CACHE):
    try: _cache = json.load(open(CACHE, encoding='utf-8'))
    except Exception: _cache = {}

def _plat(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return ' '.join(_plat(y) for y in x)
    return ''

def _get(slug, cle):
    """Les segments d'une œuvre, avec contrôle du champ ref — le piège du dépôt."""
    if cle in _cache: return _cache[cle]
    out = []
    try:
        with urllib.request.urlopen(
                f'https://www.sefaria.org/api/texts/{slug}?context=0&pad=0', timeout=30) as r:
            d = json.load(r)
        ref = str(d.get('ref', ''))
        n = cle.split(':')[-1]
        if ref.rstrip().endswith(n):          # sinon : l'œuvre entière sans dire non
            he = d.get('he')
            out = [re.sub(r'<[^>]+>', ' ', _plat(b)) for b in (he if isinstance(he, list) else [he])]
    except Exception:
        pass
    _cache[cle] = out
    try: json.dump(_cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception: pass
    time.sleep(0.1)
    return out

def seifim(n):   return _get(f'Shulchan_Arukh,_Orach_Chayim.{n}', f'sa:{n}')
def mb(n):       return _get(f'Mishnah_Berurah.{n}', f'mb:{n}')

def mb_decale(n):
    """Dans Mishnah_Berurah.N la première entrée est PARFOIS la פתיחה non numérotée.
    On ne le devine pas : on regarde si la première entrée porte un marqueur (א)."""
    s = mb(n)
    if not s: return None
    return 0 if re.search(r'\(\s*א\s*\)', s[0]) else 1

def examiner(path, siman_page, anomalies, candidats, compte):
    s = io.open(path, encoding='utf-8').read()
    nom = os.path.basename(path)
    for cell in RXTD.findall(s):
        vus = set()
        for rx, genre in ((RX_HAGAHA, 'hagaha'), (RX_MB, 'mb'), (RX_RAV, 'rav'),
                          (RX_SEIF, 'seif')):
            for m in rx.finditer(cell):
                if (m.start(), m.end()) in vus: continue
                # une étiquette de hagaha contient « OH n:m » : ne pas la compter deux fois
                if genre == 'seif':
                    avant = cell[max(0, m.start() - 40):m.end()]
                    if (RX_HAGAHA.search(avant) or RX_RAV.search(avant)
                            or RX_MB.search(avant)):
                        continue
                vus.add((m.start(), m.end()))
                n = _num(m.group(1)); a = _num(m.group(2))
                b = _num(m.group(3)) or a
                if n is None or a is None: continue
                compte[genre] += 1
                if n != siman_page:
                    candidats.append(f"{nom} · « {m.group(0).strip()} » nomme le siman {n}, "
                                     f"la page est le siman {siman_page}")
                if genre == 'rav':
                    segs = _get(f'Shulchan_Arukh_HaRav,_Orach_Chayim.{n}', f'rav:{n}')
                    if not segs: continue
                    if b > len(segs):
                        anomalies.append(f"{nom} · « {m.group(0).strip()} » — le Choul'han "
                                         f"Aroukh HaRav du siman {n} n'a que {len(segs)} séif(im)")
                    continue
                if genre == 'mb':
                    entrees = mb(n)
                    if not entrees: continue
                    d = mb_decale(n)
                    haut = len(entrees) - d
                    if b > haut:
                        anomalies.append(f"{nom} · « {m.group(0).strip()} » — la Michna Beroura "
                                         f"du siman {n} n'a que {haut} ס״ק")
                    continue
                segs = seifim(n)
                if not segs: continue
                if b > len(segs):
                    anomalies.append(f"{nom} · « {m.group(0).strip()} » — le siman {n} n'a que "
                                     f"{len(segs)} séif(im)")
                    continue
                if genre == 'hagaha':
                    sans = [k for k in range(a, b + 1) if 'הגה' not in segs[k - 1]]
                    if sans:
                        anomalies.append(
                            f"{nom} · « {m.group(0).strip()} » — le Rama n'a AUCUNE glose sur "
                            f"le séif {', '.join(map(str, sans))} du siman {n}")

def main():
    argv = sys.argv[1:]
    bref = '--bref' in argv
    if '--section' in argv:
        sec = argv[argv.index('--section') + 1]
        dirs = sorted(glob.glob(os.path.join(ROOT, 'sources', sec, 'siman-*')))
    else:
        nums = [a for a in argv if a.isdigit()]
        dirs = []
        for n in nums:
            for s in ('shabbat', 'orah-haim'):
                d = os.path.join(ROOT, 'sources', s, f'siman-{n}')
                if os.path.isdir(d): dirs.append(d); break
    if not dirs:
        print(__doc__.strip().split('Usage :')[-1]); return 2

    anomalies, candidats = [], []
    compte = {'hagaha': 0, 'seif': 0, 'mb': 0, 'rav': 0}
    for d in dirs:
        m = re.search(r'siman-(\d+)$', d)
        if not m: continue
        n = int(m.group(1))
        for p in sorted(glob.glob(os.path.join(d, 'niveau-4-*.html'))):
            examiner(p, n, anomalies, candidats, compte)

    for a in anomalies: print(f'✗ {a}')
    if not bref:
        for c in candidats: print(f'?  {c}')
    print(f"\nÉtiquettes confrontées : {compte['seif']} séif · {compte['hagaha']} hagaha · "
          f"{compte['mb']} ס״ק de Michna Beroura · {compte['rav']} séif du Choul'han Aroukh HaRav")
    print(f'ANOMALIES  : {len(anomalies)}  (le séif ou le ס״ק annoncé n\'existe pas, '
          f'ou le Rama n\'a pas de glose là)')
    print(f'candidats  : {len(candidats)}  (l\'étiquette nomme un autre siman que la page — '
          f'licite, mais rare)')
    if not anomalies:
        print('\nAucune étiquette ne nomme un séif qui ne porte pas ce qu\'elle annonce.')
    else:
        print('\nUne étiquette fausse est invisible aux portes de citation : le contenu de la '
              'cellule\nest une condensation, que la convention du dépôt exempte du verbatim.')
    return 1 if anomalies else 0

if __name__ == '__main__':
    sys.exit(main())
