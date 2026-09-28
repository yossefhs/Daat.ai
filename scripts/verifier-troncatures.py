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

DEUX FAMILLES, ET LA SECONDE EST LA PLUS DANGEREUSE.
· LE TROU — la citation saute un passage du milieu et recolle les deux bords. C'est le cas
  témoin ci-dessus.
· LA COUPURE AVANT LA SUITE — la citation s'arrête juste avant la clause qui la retourne, et
  comme elle EST alors une sous-chaîne exacte de la source, aucune porte de citation ne peut
  la voir : elle est verbatim. Deux arbitres l'ont trouvée à la main, le même jour, sur deux
  simanim différents — le מגן אברהם רמ״ו ס״ק ו coupé sur שרי quand le mot suivant est אבל, et
  ce qui suit est le צריך עיון qui empêche d'en faire un היתר plat ; et שו״ע הרב רמ״ז:ב coupé
  sur אסור quand la source poursuit אלא אם כן יש שהות…, c'est-à-dire la condition qui le lève.
  Un correctif appliqué aux seuls cas vus n'est pas un correctif : d'où cette seconde mesure.
  Le signal est étroit à dessein — la suite doit commencer par un mot qui RETOURNE (אבל, אלא,
  ומיהו, וצ״ע, ודלא…) et la phrase ne doit pas s'être close entre-temps.

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
COUVERTURE_MAX = 1.10   # …sans la couvrir DEUX FOIS : voir ci-dessous
TROU_MIN = 4            # en deçà, c'est une variante d'orthographe, pas un passage sauté
CITATION_MIN = 25       # le seuil du dépôt : sous 25 consonnes, une coïncidence est probable

# ⚠️ COUVERTURE_MAX, et la mesure qui l'a imposé. Au siman 101 de Yoré Déa, la citation
# « הראויה להתכבד בה לפני האורחים » (24 consonnes) sortait avec un préfixe de 12 ET un
# suffixe de 24 — soit 36 ancrages pour 24 consonnes. Les deux ancres se recouvraient donc
# largement dans la CITATION, tout en tombant loin l'une de l'autre dans la SOURCE : ce
# n'est pas un passage sauté, c'est une locution courante qui paraît deux fois. Exiger que
# les ancres soient à peu près disjointes, et relever le seuil de longueur à celui que le
# dépôt emploie partout ailleurs, suffit à l'écarter.

def rogner_aux_mots(saute, brut, deb, fin):
    """Ramener les bords du trou sur des frontières de mot.

    La neutralisation des matres lectionis décale l'index d'une lettre ou deux, si bien
    que le trou imprimé commençait ou finissait au milieu d'un mot — « ו הכי », « יפר ב ».
    Ce n'était pas seulement laid : un trou de quatre consonnes dont deux appartiennent aux
    mots voisins n'est pas un passage sauté, c'est un artefact d'alignement. On rogne donc
    jusqu'à la première espace de chaque côté, puis le seuil TROU_MIN est appliqué à ce
    qui reste — ce qui écarte l'artefact sans écarter le mot réellement retiré.
    """
    def lettre(c): return '\u05D0' <= c <= '\u05EA'
    i, j = deb, fin
    # une espace, une virgule, un crochet ou une parenthèse sont des frontières ;
    # seule une LETTRE collée au bord prouve qu'on coupe un mot en deux.
    while i < j and i > 0 and lettre(brut[i - 1]):
        i += 1
    while j > i and j < len(brut) and lettre(brut[j]):
        j -= 1
    return brut[i:j].strip()

def juger(cit, segs):
    """None si rien à dire ; sinon (ref, sauté, pref, suff).

    L'ancrage se fait DEUX FOIS, sur le squelette strict et sur le squelette sans matres
    lectionis. Le premier cas témoin de cette porte l'exigeait : la page écrit וְנוֹהֲגִין
    là où le Rama écrit נוהגין, si bien que le préfixe strict tombe au premier caractère
    et que le trou du milieu — le crochet [סמך ממרדכי ריש מסכת ר״ה] — reste invisible.
    """
    s0, _ = sk(cit)
    if len(s0) < CITATION_MIN: return None
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
            if p + q > len(chaine) * COUVERTURE_MAX: continue   # ancres qui se recouvrent
            i = cible.find(chaine[:p]) + p
            j = cible.rfind(chaine[-q:])
            if j - i < TROU_MIN: continue     # chevauchement ou variante d'orthographe
            # ramener les bornes sur le squelette strict, puis sur le texte brut
            bi = i if vers_b0 is None else vers_b0[i]
            bj = j if vers_b0 is None else vers_b0[j]
            if bj >= len(b0idx): continue
            saute = brut[b0idx[bi]:b0idx[bj]]
            saute = rogner_aux_mots(saute, brut, b0idx[bi], b0idx[bj])
            if len(sk(saute)[0]) < TROU_MIN: continue
            if meilleur is None or p + q > meilleur[2] + meilleur[3]:
                meilleur = (ref, saute, p, q)
    return meilleur

# Les mots par lesquels une source RETOURNE ce qu'elle vient de dire. La liste est courte
# à dessein : elle ne cherche pas toutes les continuations, seulement celles dont l'omission
# change le sens. Une citation qui s'arrête avant un simple ו־ narratif n'est pas un défaut.
# ⚠️ « ואם » EN A ÉTÉ RETIRÉ, et la mesure qui l'a exigé mérite d'être gardée. Au premier
# balayage il rendait 83 des 201 candidats — et aucun n'était un défaut. « ואם » introduit
# presque toujours un AUTRE CAS, non un renversement : la page cite « והוא שקוצץ לו דמים
# ובלבד שלא יאמר לו שילך בשבת », le Mehaber enchaîne « ואם לא קצב… », et c'est le cas suivant,
# que la page traite ailleurs. Même chose pour ואסור, ומותר, ואינו. Une porte qui compte mal
# est pire qu'une porte absente : ne garder que ce qui RETOURNE.
RETOURNEMENT = ('אבל', 'אלא', 'ומיהו', 'מיהו', 'ואך', 'אך', 'ודלא', 'וצ״ע', 'וצ"ע', 'וצריך עיון',
                'ולפיכך', 'ולכן', 'והלכך', 'הילכך', 'ומכל מקום', 'ומ״מ', 'ומ"מ', 'ויש מתירין',
                'ויש מקילין', 'ויש חולקין', 'ויש חולקים')
# Une phrase close : la source a fini de parler, s'arrêter là n'omet rien.
CLOTURE = (':', '.', '׃')

def couper_avant_la_suite(cit, segs, page_entiere=''):
    """None, ou (ref, suite, premier_mot) — la citation s'arrête avant ce qui la retourne.

    `page_entiere` est le squelette de LA PAGE EXAMINÉE, elle seule.
    Si la clause qui retourne s'y trouve ailleurs, la page la dit à SON lecteur et il n'y a
    rien à signaler : citer une clause et traiter la suivante dans la section voisine est
    la conduite NORMALE d'une page d'étude. Sans ce filtre, la porte reprocherait à une page
    bien faite d'avoir découpé son exposé.

    ⚠️ LA PAGE, ET RIEN QU'ELLE — deux mesures l'ont imposé, l'une après l'autre.
    La première version réunissait TOUT le siman, les trois langues et les quinze fichiers.
    Au siman 247, la clause qui lève l'interdit de שו״ע הרב רמ״ז:ב venait d'être rétablie
    dans le fichier HÉBREU du niveau 2 : le filtre l'y trouvait et taisait le défaut pour
    le FRANÇAIS et pour l'ANGLAIS, qui le portaient intact. Restreindre à la langue ne
    suffisait pas : la clause vit AUSSI dans le niveau 4 français, et le filtre taisait
    encore le défaut du niveau 2. Or un lecteur du niveau 2 n'ouvre pas forcément le
    niveau 4, et jamais la page hébraïque s'il lit le français. Une clause ne couvre le
    lecteur que là où il la lit : dans la page qu'il a sous les yeux.
    """
    s0, _ = sk(cit)
    if len(s0) < 20: return None
    for ref, brut in segs:
        b0, b0idx = sk(brut)
        i = b0.find(s0)
        if i < 0: continue
        fin = b0idx[i + len(s0) - 1]
        reste = brut[fin + 1:]
        # la source s'est-elle close juste après ?
        tete = reste[:6]
        if any(c in tete for c in CLOTURE): return None
        # ⚠️ LA PONCTUATION DÉTACHÉE. La source sépare souvent la clause qui retourne par une
        # virgule, et le texte vocalisé la détache par une espace : « …בְּיוֹם רִאשׁוֹן , אֶלָּא
        # אִם כֵּן ». Prendre mots[0] puis le dépouiller rendait alors la chaîne VIDE, et le test
        # ne passait jamais — la porte ratait SON PROPRE CAS TÉMOIN, שו״ע הרב רמ״ז:ב, celui-là
        # même qu'un arbitre avait trouvé à la main. Un « 0 coupure » ne valait rien tant que
        # ce défaut vivait. On dépouille donc la TÊTE du reste avant de découper.
        mots = [m for m in reste.strip(' ,;\u05C3\u00A0\t\n-–—').split() if m.strip(',;')]
        if not mots: return None
        premier = mots[0].strip(',;')
        # ⚠️ COMPARER LES SQUELETTES, JAMAIS LES FORMES. Le Choulhan Aroukh HaRav est servi
        # VOCALISÉ : la source écrit אֶלָּא, la liste porte אלא, et « אֶלָּא ».startswith(« אלא »)
        # est FAUX — le nikoud s'intercale entre les lettres. La porte ratait ainsi son propre
        # cas témoin, שו״ע הרב רמ״ז:ב, celui-là même qu'un arbitre avait trouvé à la main et
        # que deux langues portaient intact. Un « 0 coupure » ne vaut rien tant qu'on compare
        # une forme vocalisée à une forme qui ne l'est pas.
        sp = sk(premier)[0]
        if not any(sp.startswith(sk(r)[0]) or sp == sk(r)[0] for r in RETOURNEMENT if sk(r)[0]):
            return None
        sq = sk(reste)[0]
        if len(sq) < 12: return None
        # la clause qui retourne est-elle dite ailleurs dans le siman ?
        if page_entiere and sq[:25] in page_entiere: return None
        return (ref, reste.strip(), premier)
    return None

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

    total = trouve = coupe = 0
    for n, d in cibles:
        sec = 'yoreh-deah' if 'yoreh-deah' in d else ('shabbat' if 'shabbat' in d else 'orah-haim')
        segs = None
        vues = set()
        fichiers = sorted(glob.glob(os.path.join(d, '*.html')))
        def langue(x):
            b = os.path.basename(x)
            return 'he' if b.endswith('-he.html') else ('en' if b.endswith('-en.html') else 'fr')
        for f in fichiers:
            page_entiere = sk(re.sub(r'<[^>]+>', ' ',
                                     open(f, encoding='utf-8').read()))[0]
            for c in citations(f):
                # dédoublonner PAR FICHIER : la même citation dans deux pages est deux
                # fois la même question, mais posée à deux lecteurs différents, et le
                # filtre « la clause est-elle dite ailleurs » ne leur répond pas pareil.
                if (f, c) in vues: continue
                vues.add((f, c))
                if segs is None: segs = appareil(n, sec)
                total += 1
                r = juger(c, segs)
                if r:
                    trouve += 1
                    ref, saute, p, q = r
                    print(f"✗ TROU · siman {n} · {os.path.basename(f)}")
                    print(f"   « {c[:150]} »")
                    print(f"   {ref} : {p} consonnes au début + {q} à la fin, et entre les deux")
                    print(f"   la source porte — SAUTÉ SANS ELLIPSE ({len(sk(saute)[0])} consonnes) : [{saute[:160]}]")
                    if not bref: print()
                    continue
                r2 = couper_avant_la_suite(c, segs, page_entiere)
                if r2:
                    coupe += 1
                    ref, suite, premier = r2
                    print(f"✗ COUPÉE AVANT LA SUITE · siman {n} · {os.path.basename(f)}")
                    print(f"   « {c[:150] } »")
                    print(f"   {ref} — la source enchaîne sur « {premier} » sans que la phrase soit close :")
                    print(f"   [{suite[:200]}]")
                    if not bref: print()
    print(f"\nCitations confrontées : {total}")
    print(f"TROUS non marqués (un passage sauté au milieu)       : {trouve}")
    print(f"COUPURES avant la suite (la clause qui retourne)      : {coupe}")
    if not trouve and not coupe:
        print("\nAucune citation ne saute un passage de sa source sans le dire.")
    else:
        print("\nUne ellipse marque la coupure : « A… B » dit que A et B sont chacun verbatim.")
        print("Le remède est l'un des deux — rétablir le passage, ou écrire « … ».")
    return 1 if (trouve or coupe) else 0

if __name__ == '__main__':
    sys.exit(main())
