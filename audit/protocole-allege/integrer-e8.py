#!/usr/bin/env python3
"""Intègre 394-397 au catalogue et aux données (dépôt principal) ; ouvre la section « Hilkhot Te'houmin » (396-407).

Chaque remplacement est compté ; arrêt avant toute écriture si un compte diffère.
  1. data/simanim/siman-N.json sur le gabarit du 393, niveaux lus sur l'index du siman ;
  2. cartes 394-395 après la carte du 393 (section Érouvin) ; section Te'houmin nouvelle (396-397) avant la section 304/322 ;
  3. entêtes et compteurs du catalogue ; texte d'introduction (paragraphe visible + trois entrées i18n par fichier) ;
  4. bouton « Hilkhot Te'houmin » après le bouton « Hilkhot Érouvin » dans la barre des 12 catalogues.
"""
import json, re, pathlib, os
R = pathlib.Path(os.environ.get('RACINE', '/home/user/Daat.ai'))
NUM_HE = {394: 'שצ״ד', 395: 'שצ״ה', 396: 'שצ״ו', 397: 'שצ״ז'}
ERUVIN, TECHUMIN = (394, 395), (396, 397)


def lire(p): return (R / p).read_text()


def hero(n, suf):
    return re.search(r'<p class="daat-hero-subtitle">(.*?)</p>', lire(f'sources/shabbat/siman-{n}/index{suf}.html')).group(1)


def phrases(n, suf):
    h = hero(n, suf); k = h.index('. ')
    comptes, reste = h[:k], h[k + 2:]
    return comptes, re.search(r'^(.*?[?.])(\s|$)', reste).group(1)


def titre(n, suf):
    x = re.search(r'<title>(.*?) \| ', lire(f'sources/shabbat/siman-{n}/index{suf}.html')).group(1)
    return x.split(' — ', 1)[1]


DESC = {n: {lang: phrases(n, suf)[1] for suf, lang in (('', 'fr'), ('-he', 'he'), ('-en', 'en'))} for n in NUM_HE}
SUBTITLE = {n: phrases(n, '')[1].rstrip('.') + ' — ' + phrases(n, '')[0] for n in NUM_HE}
ecrits = {}

# 1. données
gabarit = json.loads(lire('data/simanim/siman-393.json'))
for n in NUM_HE:
    idx = lire(f'sources/shabbat/siman-{n}/index.html')
    d = json.loads(json.dumps(gabarit))
    d['number'] = n; d['numberHe'] = NUM_HE[n]
    d['titleHe'] = titre(n, '-he'); d['titleFr'] = titre(n, '')
    d['subtitle'] = SUBTITLE[n]
    d['description'] = re.search(r'<meta name="description" content="([^"]*)"', idx).group(1).replace('&#39;', "'")
    d['keywords'] = re.search(r'<meta name="keywords" content="([^"]*)"', idx).group(1)
    descs = re.findall(r'<p style="color: var\(--daat-text-mid\); margin-bottom: 16px;">(.*?)</p>', idx)
    assert len(descs) == 4, (n, len(descs))
    for lv, ds in zip(d['levels'], descs):
        lv['desc'] = ds
    ecrits[f'data/simanim/siman-{n}.json'] = json.dumps(d, ensure_ascii=False, indent=2) + '\n'

# 2-3. catalogue
CARTE = {
    '': ('/oh/{n}/', 'Siman {n}', 'Complet', '4 niveaux : Base · Lamdan · Synthèse · ', 'Étudier →', 'fr'),
    '-he': ('/oh/{n}/he', 'סימן {n}', 'שלם', '4 רמות: בסיס · למדן · סיכום · ', 'ללמוד ←', 'he'),
    '-en': ('/oh/{n}/en', 'Siman {n}', 'Complete', '4 levels: Base · Lamdan · Synthesis · ', 'Study →', 'en'),
}
SECTION_TECHUMIN = {
    '': ("  <!-- SECTION 2 ter : Hilkhot Te'houmin (396+) — 4 niveaux ; publiée lot par lot, dans l'ordre du Mehaber -->",
         "Hilkhot Te'houmin · simanim 396 à 397 — 4 niveaux d'étude", "2 simanim · la suite paraît dans l'ordre du Mehaber"),
    '-he': ("  <!-- SECTION 2 ter : Hilkhot Te'houmin (396+) — 4 niveaux ; publiée lot par lot, dans l'ordre du Mehaber -->",
            'הלכות תחומין · סימנים שצ״ו–שצ״ז — ארבע רמות לימוד', '2 סימנים · ההמשך יתפרסם לפי סדר המחבר'),
    '-en': ("  <!-- SECTION 2 ter: Hilchos Techumin (396+) — 4 levels; published lot by lot, in the order of the Mechaber -->",
            'Hilchos Techumin · simanim 396 to 397 — 4 levels of study', '2 simanim · more to follow in the order of the Mechaber'),
}
REMPL = {
    '': [('Hilkhot Érouvin · simanim 366 à 393', 'Hilkhot Érouvin · simanim 366 à 395'),
         ('<div class="section-count">28 simanim · la suite paraît dans l\'ordre du Mehaber</div>', '<div class="section-count">30 simanim</div>'),
         ('disponible sur 150 des 152 simanim', 'disponible sur 154 des 156 simanim')],
    '-he': [('הלכות עירובין · סימנים שס״ו–שצ״ג', 'הלכות עירובין · סימנים שס״ו–שצ״ה'),
            ('<div class="section-count">28 סימנים · ההמשך יתפרסם לפי סדר המחבר</div>', '<div class="section-count">30 סימנים</div>'),
            ('זמינה ב־150 מתוך 152 הסימנים', 'זמינה ב־154 מתוך 156 הסימנים')],
    '-en': [('Hilchos Eruvin · simanim 366 to 393', 'Hilchos Eruvin · simanim 366 to 395'),
            ('<div class="section-count">28 simanim · more to follow in the order of the Mechaber</div>', '<div class="section-count">30 simanim</div>'),
            ('available on 150 of the 152 simanim', 'available on 154 of the 156 simanim')],
}
# introduction : (ancien, nouveau) ; dans les entrées i18n (chaînes JS entre apostrophes), l'apostrophe est échappée
INTRO = [
    ("puis, à partir du siman 366, les Hilkhot Érouvin.",
     "puis, à partir du siman 366, les Hilkhot Érouvin, et, à partir du siman 396, les Hilkhot Te'houmin (dans l'index de Sefaria, la section הלכות תחומין couvre les simanim 396 à 407)."),
    ("ומסימן שס״ו ואילך את הלכות עירובין.",
     "ומסימן שס״ו ואילך את הלכות עירובין, ומסימן שצ״ו ואילך את הלכות תחומין (במפתח של ספריא, חלק הלכות תחומין מכסה את סימנים שצ״ו עד ת״ז)."),
    ("then, from siman 366, Hilchos Eruvin.",
     "then, from siman 366, Hilchos Eruvin, and, from siman 396, Hilchos Techumin (in Sefaria's index, the section הלכות תחומין covers simanim 396 to 407)."),
]
INTRO_ATTENDU = {'': (2, 1, 1), '-he': (1, 2, 1), '-en': (1, 1, 2)}


def carte(n, suf):
    href, numfr, statut, niv, btn, lang = CARTE[suf]
    nom = titre(n, '-he') if lang == 'he' else titre(n, suf)
    return f'''
    <a href="{href.format(n=n)}" class="siman-card available full-4" style="text-decoration:none; color:inherit;">
      <div class="siman-card-top">
        <div class="siman-num"><span class="siman-num-fr">{numfr.format(n=n)}</span><span class="siman-num-he">סימן {NUM_HE[n]}</span></div>
        <span class="siman-status status-ready">{statut}</span>
      </div>
      <div class="siman-name-he">{titre(n, '-he')}</div>
      <div class="siman-name-fr">{nom}</div>
      <div class="siman-desc">{DESC[n][lang]}</div>
      <div class="siman-card-bottom">
        <span class="siman-levels-info">{niv}<strong style="color:#3851A3;">{'דעת הרב' if lang == 'he' else 'Daat HaRav'}</strong></span>
        <span class="btn-study">{btn}</span>
      </div>
    </a>
'''


for suf, (href, *_rest) in CARTE.items():
    p = f'sources/shabbat/index{suf}.html'
    s = lire(p)
    assert 'href="' + href.format(n=394) + '"' not in s, ('déjà intégré', p)
    ancre = re.compile(r'(<a href="' + re.escape(href.format(n=393)) + r'" class="siman-card[^"]*".*?</a>\n)', re.S)
    s, k = ancre.subn(lambda m: m.group(1) + ''.join(carte(n, suf) for n in ERUVIN), s); assert k == 1, (p, k)
    com, titre_s, compte = SECTION_TECHUMIN[suf]
    bloc = (f'{com}\n  <div class="section-header" id="hilkhot-techumin" style="scroll-margin-top:90px;">\n'
            f'    <div class="section-title">{titre_s}</div>\n    <div class="section-count">{compte}</div>\n  </div>\n\n'
            f'  <div class="simanim-grid">' + ''.join(carte(n, suf) for n in TECHUMIN) + '\n  </div>\n\n')
    m = re.search(r'  <!-- SECTION 3[ :]', s); assert m and s.count('<!-- SECTION 3') == 1, p
    s = s[:m.start()] + bloc + s[m.start():]
    for a, b in REMPL[suf]:
        assert s.count(a) == 1, (p, a, s.count(a)); s = s.replace(a, b)
    L = s.split('\n')
    for (a, b), att in zip(INTRO, INTRO_ATTENDU[suf]):
        idx = [i for i, l in enumerate(L) if a in l]
        assert len(idx) == att, (p, a, len(idx))
        for i in idx:
            js = "'shabbat.intro1':" in L[i]
            L[i] = L[i].replace(a, b.replace("'", "\\'") if js else b)
    ecrits[p] = '\n'.join(L)

# 4. bouton de la barre, dans les 12 catalogues
LIB = {'': ("Orah Haïm — Hilkhot Érouvin", "Orah Haïm — Hilkhot Te'houmin"),
       '-he': ('אורח חיים — הלכות עירובין', 'אורח חיים — הלכות תחומין'),
       '-en': ('Orah Haim — Hilchos Eruvin', 'Orah Haim — Hilchos Techumin')}
for d in ('shabbat', 'orah-haim', 'yoreh-deah', 'nida'):
    for suf in ('', '-he', '-en'):
        p = f'sources/{d}/index{suf}.html'
        s = ecrits.get(p) or lire(p)
        assert '#hilkhot-techumin"' not in s, p
        L = s.split('\n')
        idx = [i for i, l in enumerate(L) if '#hilkhot-eruvin"' in l and LIB[suf][0] in l]
        assert len(idx) == 1, (p, len(idx))
        i = idx[0]
        L.insert(i + 1, L[i].replace('#hilkhot-eruvin"', '#hilkhot-techumin"').replace(LIB[suf][0], LIB[suf][1]))
        ecrits[p] = '\n'.join(L)

for p, s in ecrits.items():
    (R / p).write_text(s)
print(len(ecrits), 'fichiers écrits')
