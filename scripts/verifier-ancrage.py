#!/usr/bin/env python3
"""L'entrée d'appareil est-elle rattachée au bon séif ?

Une page qui écrit « le psak du Taz ס״ק י״ח (seif 7) » promet au lecteur qu'en
ouvrant le séif 7 il y trouvera ce ס״ק. Aucune des dix autres portes ne vérifie
cette promesse : `verifier-citations.py` confronte le VERBATIM à la source et le
trouve exact — le ס״ק י״ח existe, il dit bien ce que la page lui fait dire — mais
il ne regarde pas où il est posé. Trouvé au siman 119 de Yoré Déa : le Taz ס״ק י״ח
est ancré au séif 19 (son lemme est `וכל זה אינו נוהג בחשוד`, et il traite du
ḥachoud envoyé acheter du fromage) ; la page le donne au séif 7.

La source de vérité est l'ancre que Sefaria pose DANS le texte du Choul'han Aroukh :
    <i data-commentator="Turei Zahav" data-order="18"></i>
`data-order` est le numéro du ס״ק dans le siman, et le séif où l'ancre se trouve est
le séif auquel il se rattache. Vérifié : les ordres croissent avec les séifim, et le
total par commentateur coïncide exactement avec le nombre d'entrées que Sefaria sert
pour ce commentateur (siman 234 : 93 ש״ך, 66 ט״ז, 62 באר היטב).

Ce contrôle rend des CANDIDATS, jamais des verdicts, et sort toujours en 0 : une page
peut légitimement citer un ס״ק d'un autre séif quand il éclaire le sien. Ce qu'il faut
lire dans sa sortie, c'est (a) un écart isolé — à vérifier à la main — et (b) un écart
SYSTÉMATIQUE, tout un siman décalé d'un cran, qui est le piège de la règle 22-bis :
le décompte aplati de Sefaria décale toute la numérotation.

Usage :
  python3 scripts/verifier-ancrage.py                       # tout Yoré Déa
  python3 scripts/verifier-ancrage.py --path sources/yoreh-deah/siman-119
  python3 scripts/verifier-ancrage.py 119 120 234
"""
import sys, os, re, json, glob, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache-ancrage.json")

GEM = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'כ':20,'ל':30,
       'מ':40,'נ':50,'ס':60,'ע':70,'פ':80,'צ':90,'ק':100,'ר':200,'ש':300,'ת':400}

def gem(s):
    s = re.sub(r'["״\'׳]', '', s or '')
    return sum(GEM[c] for c in s) if s and all(c in GEM for c in s) else None

NOMS = {
    'ש״ך': 'Siftei Kohen', 'ש"ך': 'Siftei Kohen', 'Chakh': 'Siftei Kohen',
    'Shakh': 'Siftei Kohen', 'Siftei Kohen': 'Siftei Kohen',
    'ט״ז': 'Turei Zahav', 'ט"ז': 'Turei Zahav', 'Taz': 'Turei Zahav',
    'Turei Zahav': 'Turei Zahav',
    'באר היטב': "Ba'er Hetev", 'Baer Hetev': "Ba'er Hetev",
    'פת״ש': "Pitchei Teshuva", 'פת"ש': "Pitchei Teshuva",
    'Pithei Techouva': "Pitchei Teshuva", "Pit'hei Techouva": "Pitchei Teshuva",
}
ALT = r"|".join(sorted((re.escape(k) for k in NOMS), key=len, reverse=True))

# « Taz ס״ק י״ח (seif 7) », « ש״ך ס״ק ג (séif 2) », « Chakh ס״ק ה — seif 4 »
RX = re.compile(
    r"(?P<qui>" + ALT + r")(?P<mid>[^.;<]{0,60}?)"
    r"ס[\"״]ק\s*(?P<sk>[א-ת]{1,4}[\"״'׳]?[א-ת]?)"
    r"[^.;<]{0,40}?[\(—–-]\s*(?:s[eé]if|סעיף)\s*(?P<sf>\d{1,3}|[א-ת]{1,3}[\"״'׳]?[א-ת]?)")

SECTIONS = {'yoreh-deah': "Shulchan_Arukh,_Yoreh_De%27ah",
            'shabbat': "Shulchan_Arukh,_Orach_Chayim",
            'orah-haim': "Shulchan_Arukh,_Orach_Chayim"}

def _cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding='utf-8'))
        except Exception:
            return {}
    return {}

_C = _cache()

def carte(section, n):
    """{commentateur: {numéro de ס״ק: séif}} d'après les ancres de Sefaria."""
    cle = f"{section}.{n}"
    if cle in _C:
        return _C[cle]
    url = (f"https://www.sefaria.org/api/texts/{SECTIONS[section]}.{n}"
           "?context=0&pad=0")
    try:
        d = json.loads(subprocess.run(["curl", "-s", url], capture_output=True,
                                      text=True, timeout=60).stdout)
        he = d.get('he') or []
    except Exception:
        return {}
    c = {}
    for i, s in enumerate(he, 1):
        t = s if isinstance(s, str) else " ".join(s)
        for m in re.finditer(r'data-commentator="([^"]+)" data-order="(\d+)"', t):
            # première ancre rencontrée = le séif de rattachement
            c.setdefault(m.group(1), {}).setdefault(m.group(2), i)
    _C[cle] = c
    try:
        json.dump(_C, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception:
        pass
    return c

def section_de(path):
    for s in SECTIONS:
        if f"/{s}/" in path.replace(os.sep, '/'):
            return s
    return None

def examiner(dossier):
    n = int(re.search(r'siman-(\d+)', dossier).group(1))
    sec = section_de(dossier)
    if not sec:
        return [], 0, 0
    c = carte(sec, n)
    if not c:
        return [], 0, 0
    justes = inconnus = 0
    ecarts = []
    for p in sorted(glob.glob(os.path.join(dossier, '*.html'))):
        brut = open(p, encoding='utf-8').read()
        # Les balises doivent tomber AVANT la recherche. Yoré Déa écrit le séif dans un
        # <span class="src-ref">[seif N]</span> : lu sur le HTML brut, le motif — qui
        # interdit le chevron pour ne pas enjamber une phrase — ne pouvait jamais
        # apparier. Le contrôle sortait « 0 rattachement confronté » sur tout le
        # compartiment, et ce zéro passait pour un blanc-seing alors qu'il en existe
        # 140 dans le seul siman 234. Un contrôle qui ne compare rien doit le dire ;
        # celui-ci le disait, et personne ne lisait la ligne.
        # …mais les retirer toutes laisse le motif ENJAMBER les blocs : au siman 229,
        # « Le Taz ס״ק י״א » d'une carte s'appariait au « Verrou 2 — séif 5 » de la
        # carte suivante, et douze rattachements sur douze paraissaient décalés d'un
        # cran — la signature même du piège 22-bis, ici entièrement fabriquée par le
        # contrôle. Les fins de bloc deviennent donc une frontière, pas un espace.
        txt = re.sub(r'</(?:div|p|li|td|tr|h[1-6]|blockquote|section)>|<br\s*/?>',
                     ' . ', brut)
        txt = re.sub(r'<[^>]+>', ' ', txt)
        for m in RX.finditer(txt):
            qui = NOMS.get(m.group('qui'))
            sk = gem(m.group('sk'))
            sf = m.group('sf')
            sf = int(sf) if sf.isdigit() else gem(sf)
            if not (qui and sk and sf):
                continue
            vrai = c.get(qui, {}).get(str(sk))
            if vrai is None:
                inconnus += 1
                continue
            if vrai == sf:
                justes += 1
            else:
                ligne = txt[:m.start()].count('\n') + 1
                ecarts.append((p, ligne, m.group('qui'), m.group('sk'), sf, vrai,
                               re.sub(r'\s+', ' ', m.group(0))[:120]))
    return ecarts, justes, inconnus

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--path' in sys.argv:
        cible = sys.argv[sys.argv.index('--path') + 1]
        racines = ([cible] if os.path.basename(cible).startswith('siman-')
                   else sorted(glob.glob(os.path.join(cible, 'siman-*'))))
    elif args:
        racines = [os.path.join(ROOT, 'sources', 'yoreh-deah', f'siman-{a}') for a in args]
    else:
        racines = sorted(glob.glob(os.path.join(ROOT, 'sources', '*', 'siman-*')))

    tj = ti = 0
    tous = []
    for d in racines:
        if not os.path.isdir(d):
            continue
        ecarts, j, i = examiner(d)
        tj += j; ti += i; tous.extend(ecarts)
        for p, ln, qui, sk, dit, vrai in ((e[0], e[1], e[2], e[3], e[4], e[5]) for e in ecarts):
            print(f"ÉCART  {os.path.relpath(p, ROOT)}:{ln} — {qui} ס״ק {sk} : "
                  f"la page dit séif {dit}, l'ancre Sefaria le pose au séif {vrai}")
    print()
    print(f"Rattachements confrontés : {tj + len(tous)}")
    print(f"  conformes              : {tj}")
    print(f"  écarts (candidats)     : {len(tous)}")
    print(f"  ס״ק hors carte         : {ti}")
    print()
    print("Un écart n'est pas une faute : une page peut citer le ס״ק d'un autre séif")
    print("quand il éclaire le sien. Ce qui se lit ici, c'est l'écart ISOLÉ — à ouvrir —")
    print("et l'écart SYSTÉMATIQUE, tout un siman décalé, qui est le piège 22-bis.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
