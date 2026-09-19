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
RX_SEIF = re.compile(r'Seif\s+(\d+)(?:\s*[-–]\s*(\d+))?', re.I)

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
        t = titre_avant(s, m.start())
        mm = RX_SEIF.match(t)
        if not mm:
            out.append(None); continue
        a = int(mm.group(1)); b = int(mm.group(2) or a)
        out.append((a, b) if 1 <= a <= len(S) and 1 <= b <= len(S) else None)
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
            a, b = cible
            neuf = ' '.join(S[i - 1] for i in range(a, b + 1))
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


if __name__ == '__main__':
    sys.exit(main())
