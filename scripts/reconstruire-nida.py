#!/usr/bin/env python3
"""Bloc נדה : reposer le texte du Choul'han Aroukh VERBATIM, là où la page le retapait.

Dix des dix-huit simanim du bloc נדה (184-188, 192, 194-197) ont la bonne CHARPENTE —
un bloc par séif, dans l'ordre du livre — et un texte FAUX : hébreu retapé, vocalisé et
plus ou moins abrégé (de 101 % du texte au siman 184 à 40 % au siman 196). Ce script ne
réécrit rien : il va chercher dans le JSON de Sefaria le séif annoncé par le titre du
bloc et le repose tel quel.

C'est la règle 29 du cahier des charges, appliquée à la réparation : **on ne retape
jamais l'hébreu**. Un bloc dont le séif ne se retrouve pas dans la source n'est pas
réparé au jugé — il est signalé et laissé intact.

Le bloc redevient `blockquote.text-source` et perd sa marque « résumé » : il redit ce
qu'il est. Les trois langues portent le même hébreu, donc la substitution est identique
dans les trois fichiers — c'est la parité trilingue.

⚠️ CE QUE CE SCRIPT NE FAIT PAS. Il ne touche pas aux TRADUCTIONS. Là où l'ancien bloc
était abrégé, la traduction l'est aussi, et elle ne couvre plus tout le texte reposé :
le script le dit siman par siman, en pourcentage. C'est le travail qui reste, et il
demande une lecture.

Usage :
  python3 scripts/reconstruire-nida.py 185              # un siman
  python3 scripts/reconstruire-nida.py --tier1          # les dix qui s'y prêtent
  python3 scripts/reconstruire-nida.py 185 --dry-run
"""
import re, sys, os, io, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIER1 = [184, 185, 186, 187, 188, 192, 194, 195, 196, 197]

GEM = {'א':1,'ב':2,'ג':3,'ד':4,'ה':5,'ו':6,'ז':7,'ח':8,'ט':9,'י':10,'כ':20,'ל':30,
       'מ':40,'נ':50,'ס':60,'ע':70,'פ':80,'צ':90,'ק':100,'ר':200,'ש':300,'ת':400}

def cons(x):
    return ''.join(re.findall(r'[א-ת]', re.sub(r'<[^>]+>', '', x)))

_cache = {}
def source(n):
    if n in _cache:
        return _cache[n]
    u = (f"https://www.sefaria.org/api/texts/Shulchan_Arukh,_Yoreh_De%27ah.{n}"
         "?context=0&pad=0")
    he = json.loads(subprocess.run(["curl", "-s", u], capture_output=True,
                                   text=True, timeout=60).stdout)['he']
    _cache[n] = [x if isinstance(x, str) else ' '.join(x) for x in he]
    return _cache[n]

RX_BLOC = re.compile(r'<blockquote class="text-resume"([^>]*)>(.*?)</blockquote>', re.S)
RX_SEIF = re.compile(r'Seif\s+(?P<spec>\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*)',
                     re.I)

def seifim_de(titre):
    """Les séifim qu'un titre de bloc annonce : « Seif 3 », « Seif 2-4 », « Seif 9, 11 »."""
    m = RX_SEIF.match(titre)
    if not m:
        return []
    out = []
    for part in m.group('spec').split(','):
        part = part.strip()
        mr = re.match(r'(\d+)\s*[-–]\s*(\d+)$', part)
        if mr:
            out += list(range(int(mr.group(1)), int(mr.group(2)) + 1))
        elif part.isdigit():
            out.append(int(part))
    return out

def titre_avant(s, pos):
    h = re.findall(r'<h[34][^>]*>(.*?)(?:<button|</h)', s[:pos], re.S)
    return re.sub(r'<[^>]+>', '', h[-1]).strip() if h else ''

def plan(n, S):
    """Correspondance bloc → séif, calculée UNE FOIS sur la page française.

    Les pages hébraïque et anglaise titrent leurs blocs dans leur langue (« סעיף א »,
    « Seif 1 »), si bien qu'un motif français n'y voit rien : à son premier essai le
    script ne traitait que deux blocs sur quatre et croyait avoir fini. Mais les trois
    variantes sont parallèles bloc à bloc — c'est la parité trilingue du dépôt — donc la
    correspondance se calcule sur le français et s'applique PAR POSITION aux trois.
    """
    p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base.html')
    s = io.open(p, encoding='utf-8').read()
    out = []
    for m in RX_BLOC.finditer(s):
        nums = [x for x in seifim_de(titre_avant(s, m.start())) if 1 <= x <= len(S)]
        out.append(nums or None)
    return out

def traiter(n, dry=False):
    S = source(n)
    carte = plan(n, S)
    faits = ignores = 0
    couv_avant = couv_apres = 0
    for suf in ('', '-he', '-en'):
        p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base{suf}.html')
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        blocs = list(RX_BLOC.finditer(s))
        if len(blocs) != len(carte):
            print(f"  ⚠️ siman {n}{suf} : {len(blocs)} blocs contre {len(carte)} en "
                  f"français — parité rompue, fichier laissé intact")
            continue
        sortie = []
        for m, cible in zip(blocs, carte):
            if cible is None:
                ignores += 1
                continue
            neuf = ' '.join(S[i - 1] for i in cible)
            neuf = re.sub(r'<i data-commentator[^>]*></i>', '', neuf)
            if suf == '':
                couv_avant += len(cons(m.group(2)))
                couv_apres += len(cons(neuf))
            sortie.append((m.start(), m.end(), m.group(1), neuf))
        if not sortie:
            continue
        out, pos = [], 0
        for deb, fin, attrs, neuf in sortie:
            out.append(s[pos:deb])
            out.append(f'<blockquote class="text-source"{attrs}>\n{neuf}\n</blockquote>')
            pos = fin
        out.append(s[pos:])
        s2 = ''.join(out)
        if not dry:
            io.open(p, 'w', encoding='utf-8').write(s2)
        faits += len(sortie)
    tot = sum(len(cons(x)) for x in S)
    return faits // 3, ignores // 3, couv_avant, couv_apres, tot

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    if '--refondre' in sys.argv:
        for a in args:
            refondre(int(a), dry)
        if dry:
            print("\n(essai à blanc — rien n'a été écrit)")
        return 0
    if '--monoseif' in sys.argv:
        for a in (args or ['183', '191', '193', '200']):
            traiter_monoseif(int(a), dry)
        if dry:
            print("\n(essai à blanc — rien n'a été écrit)")
        return 0
    nums = TIER1 if '--tier1' in sys.argv else [int(a) for a in args]
    if not nums:
        print(__doc__); return 2
    print(f"{'sim':>4} {'blocs':>6} {'ignorés':>8}  couverture avant → après")
    for n in nums:
        f, i, av, ap, tot = traiter(n, dry)
        print(f"{n:>4} {f:>6} {i:>8}  {100*av//max(tot,1):>3} % → {100*ap//max(tot,1):>3} %"
              + ("   ⚠️ traduction à étendre" if ap > av * 1.15 else ""))
    if dry:
        print("\n(essai à blanc — rien n'a été écrit)")
    return 0



# ─────────────────────── simanim d'un seul séif ───────────────────────
#
# Les simanim 183, 191, 193 et 200 n'ont qu'UN séif, long, que la page débite en
# plusieurs blocs pour le rendre lisible — deux, sept, un, trois. Le découpage est
# légitime : `verify-yd-source.py` compare la CONCATÉNATION des blocs au séif, et ne
# juge pas où l'on coupe. Ce qui ne l'est pas, c'est que le texte y soit retapé.
#
# On ne peut donc pas remplacer « le séif annoncé par le titre » : il n'y en a qu'un.
# On recoupe le vrai séif aux endroits où la page coupe déjà, en cherchant dans la
# source le début consonantique de chaque bloc. Un bloc dont le début ne se retrouve
# pas dans la source laisse le siman intact et le dit : mieux vaut ne rien faire que
# couper au jugé.

def _skelette(x):
    return ''.join(re.findall(r'[א-ת]', re.sub(r'<[^>]+>', '', x)))

def decouper(seif, blocs):
    """Découpe `seif` aux points où les `blocs` de la page commencent."""
    sq = _skelette(seif)
    # position, dans le squelette, du début de chaque bloc
    # L'ancre ne peut pas être le seul début du bloc : la page développe parfois une
    # abréviation de la source dès le premier mot — au siman 191, le bloc du Rama ouvre
    # « הגה: ויש אומרים » là où le Choul'han Aroukh porte « הגה וי״א ». On essaie donc
    # plusieurs ancres prises à l'intérieur du bloc, et l'on retranche le décalage.
    coupes, curseur = [], 0
    for b in blocs:
        sk = _skelette(b)
        if len(sk) < 12:
            return None
        trouve = None
        for saut in (0, 8, 16, 24, 32, 48, 64):
            if saut + 12 > len(sk):
                break
            i = sq.find(sk[saut:saut + 12], curseur)
            if i >= 0:
                trouve = max(curseur, i - saut)
                break
        if trouve is None:
            return None
        coupes.append(trouve)
        curseur = trouve + 1
    # Le premier bloc de la page commence APRÈS le chapeau (« דין דם בתולים. ובו סעיף
    # אחד: ») : exiger qu'il parte de zéro faisait échouer les quatre simanim. Le chapeau
    # appartient à la source et rejoint donc le premier bloc, comme aux simanim 185 et
    # 234 déjà publiés.
    coupes[0] = 0
    if coupes != sorted(coupes) or len(set(coupes)) != len(coupes):
        return None
    # reporter ces positions sur le texte réel, lettre à lettre
    pos, rendu, morceaux = 0, [], []
    for ch in seif:
        if re.match(r'[א-ת]', ch):
            if pos in coupes[1:]:
                morceaux.append(''.join(rendu)); rendu = []
            pos += 1
        rendu.append(ch)
    morceaux.append(''.join(rendu))
    return morceaux if len(morceaux) == len(blocs) else None

def traiter_monoseif(n, dry=False):
    S = source(n)
    if len(S) != 1:
        print(f"siman {n} : {len(S)} séifim — ce mode ne vaut que pour un séif unique")
        return 0
    seif = re.sub(r'<i data-commentator[^>]*></i>', '', S[0])
    p0 = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base.html')
    s0 = io.open(p0, encoding='utf-8').read()
    blocs0 = [m.group(2) for m in RX_BLOC.finditer(s0)]
    if not blocs0:
        print(f"siman {n} : aucun bloc text-resume")
        return 0
    morceaux = decouper(seif, blocs0)
    if morceaux is None:
        print(f"siman {n} : ⚠️ le début d'au moins un bloc ne se retrouve pas dans la "
              f"source — rien n'a été touché, à reprendre à la main")
        return 0
    for suf in ('', '-he', '-en'):
        p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base{suf}.html')
        s = io.open(p, encoding='utf-8').read()
        blocs = list(RX_BLOC.finditer(s))
        if len(blocs) != len(morceaux):
            print(f"  ⚠️ {os.path.basename(p)} : parité rompue, laissé intact")
            continue
        out, pos = [], 0
        for m, txt in zip(blocs, morceaux):
            out.append(s[pos:m.start()])
            out.append(f'<blockquote class="text-source"{m.group(1)}>\n{txt}\n</blockquote>')
            pos = m.end()
        out.append(s[pos:])
        if not dry:
            io.open(p, 'w', encoding='utf-8').write(''.join(out))
    avant = sum(len(_skelette(b)) for b in blocs0)
    apres = len(_skelette(seif))
    print(f"siman {n} : {len(morceaux)} blocs recoupés sur le séif unique — "
          f"{100*avant//apres} % → 100 %")
    return len(morceaux)




# ─────────────────── refonte d'une section de texte ───────────────────
#
# Les simanim 189, 190 et 198 ne se réparent pas bloc à bloc : leurs pages ne portent
# qu'un cinquième du Choul'han Aroukh (13 blocs pour 34 séifim, 15 pour 54, 10 pour 48),
# et deux d'entre elles présentent en outre les séifim dans le désordre. Il n'y a pas de
# texte à remplacer — il y a un texte à POSER.
#
# La refonte reconstruit la section entière : un bloc par séif, verbatim, dans l'ordre du
# livre. Les traductions existantes ne sont pas jetées : chacune est reportée sur le
# premier séif que son bloc d'origine annonçait, avec une marque disant à quels séifim
# elle se rapportait — c'est au rédacteur de les répartir, la machine ne sait pas le
# faire. Les séifim qui n'étaient nulle part reçoivent un bloc verbatim et une traduction
# vide, marquée.
#
# L'hébreu vient toujours du JSON de Sefaria et n'est jamais retapé (règle 29).

RX_H2 = re.compile(r'<h2[ >]')

def _section(s):
    m = re.search(r'<h2 id="exp-seifim"', s)
    if not m:
        return None
    suite = RX_H2.search(s[m.end():])
    return m.start(), (m.end() + suite.start() if suite else len(s))

def _unites(s, a, b):
    deb = [m.start() for m in re.finditer(r'<h4[ >]', s) if a <= m.start() < b]
    out = []
    for d in deb:
        suite = re.search(r'<h[234][ >]', s[d + 4:b])
        out.append((d, d + 4 + suite.start() if suite else b))
    return out

A_TRADUIRE = {
    'fr': ('<div class="translation"><em>traduction à écrire</em> — ce séif n’était '
           'pas dans la page ; son texte vient d’être posé verbatim.</div>'),
    'he': ('<div class="translation"><em>תרגום לכתוב</em> — סעיף זה לא היה בדף; לשונו '
           'הונחה עתה כמות שהיא.</div>'),
    'en': ('<div class="translation"><em>translation to be written</em> — this seif was '
           'not in the page; its text has just been laid down verbatim.</div>'),
}
REPORTEE = {
    'fr': 'traduction reportée — elle portait sur les séifim {}, à répartir',
    'he': 'תרגום שהועבר — הוא נסב על סעיפים {}, יש לחלקו',
    'en': 'translation carried over — it covered seifim {}, to be redistributed',
}

def refondre(n, dry=False):
    S = source(n)
    p0 = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base.html')
    s0 = io.open(p0, encoding='utf-8').read()
    bornes0 = _section(s0)
    if not bornes0:
        print(f"siman {n} : section du texte introuvable"); return 0
    u0 = _unites(s0, *bornes0)
    # ce que chaque unité annonce, lu sur le français
    annonce = []
    for d, f in u0:
        t = re.sub(r'<[^>]+>', '', s0[d:d + 260])
        annonce.append([x for x in seifim_de(t.strip()) if 1 <= x <= len(S)])
    par_seif = {}
    for i, nums in enumerate(annonce):
        for x in nums:
            par_seif.setdefault(x, i)

    neufs = 0
    for suf in ('', '-he', '-en'):
        p = os.path.join(ROOT, f'sources/yoreh-deah/siman-{n}/niveau-1-base{suf}.html')
        s = io.open(p, encoding='utf-8').read()
        bornes = _section(s)
        u = _unites(s, *bornes)
        if len(u) != len(u0):
            print(f"  ⚠️ {os.path.basename(p)} : {len(u)} unités contre {len(u0)} en "
                  f"français — parité rompue, fichier laissé intact")
            continue
        lg = 'he' if suf == '-he' else 'en' if suf == '-en' else 'fr'
        # la traduction et les encadrés d'une unité, sans son titre ni ses blocs
        garde = []
        for d, f in u:
            corps = s[d:f]
            corps = re.sub(r'<h4[^>]*>.*?</h4>', '', corps, flags=re.S)
            corps = re.sub(r'<blockquote class="text-(?:resume|source|compose)"[^>]*>'
                           r'.*?</blockquote>', '', corps, flags=re.S)
            garde.append(corps.strip())
        titres = [re.sub(r'(?s)<button.*?</button>', '',
                         re.search(r'<h4[^>]*>(.*?)</h4>', s[d:f], re.S).group(1)).strip()
                  if re.search(r'<h4[^>]*>(.*?)</h4>', s[d:f], re.S) else ''
                  for d, f in u]
        morceaux = []
        for x in range(1, len(S) + 1):
            txt = re.sub(r'<i data-commentator[^>]*></i>', '', S[x - 1])
            i = par_seif.get(x)
            premier = i is not None and min(annonce[i]) == x
            titre = titres[i] if premier else f"Seif {x}"
            bloc = (f'\n<h4>{titre}</h4>\n'
                    f'<blockquote class="text-source" data-copy-block id="cp-s{x}">\n'
                    f'{txt}\n</blockquote>\n')
            if premier:
                marque = REPORTEE[lg].format(', '.join(str(y) for y in annonce[i]))
                bloc += f'<p class="src-ref"><em>{marque}</em></p>\n{garde[i]}\n'
            else:
                bloc += A_TRADUIRE[lg] + '\n'
                if suf == '':
                    neufs += 1
            morceaux.append(bloc)
        neuf = s[:u[0][0]] + ''.join(morceaux) + s[u[-1][1]:]
        if not dry:
            io.open(p, 'w', encoding='utf-8').write(neuf)
    print(f"siman {n} : {len(S)} blocs posés dans l'ordre du livre, "
          f"{neufs} séifim qui n'étaient pas dans la page")
    return neufs


if __name__ == '__main__':
    sys.exit(main())
