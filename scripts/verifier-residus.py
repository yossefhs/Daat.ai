#!/usr/bin/env python3
"""Ce qu'on a corrigé ici, l'a-t-on laissé vivre ailleurs ?

CINQ FOIS de suite, sur le lot 229-234 de Yoré Déa, un correcteur a réparé la phrase
qu'on lui montrait et laissé la même affirmation debout ailleurs dans le même siman :

  · « les quatre verrous des séifim 4 à 8 », corrigé au sommaire du niveau 2, survivant
    dans les QUATRE descriptions de la page — meta, og, twitter, JSON-LD — des trois
    langues, et dans la carte visible de l'index : quinze survivances ;
  · « une seule échoue entièrement », corrigé dans la FAQ et sa copie JSON-LD, survivant
    au sous-titre héros et dans le tableau « teaches » du JSON-LD : six survivances, et
    le fichier index.html se contredisant à 78 lignes d'intervalle ;
  · « qui tient en sept mots », laissé trente mots après un superlatif ouvert dans LA
    MÊME PHRASE.

Le CLAUDE.md le dit déjà — « un correctif appliqué à la main sur les cas qu'on a vus
n'est pas un correctif » — et le répéter aux agents n'a pas suffi. Ce script le vérifie
au lieu de le demander : il prend ce que l'édition a RETIRÉ, et cherche si ça vit encore.

MÉTHODE. `git diff` donne les lignes supprimées et ajoutées. On en retire les balises,
on en extrait les n-grammes (cinq mots en caractères latins, trois en hébreu), on écarte
ceux que le texte AJOUTÉ reprend — ceux-là n'étaient pas censés disparaître — et on
cherche les autres dans les quinze fichiers du siman, métadonnées, JSON-LD et sommaires
compris. Tout ce qui répond est un résidu.

Usage :
  python3 scripts/verifier-residus.py sources/yoreh-deah/siman-229
  python3 scripts/verifier-residus.py --depuis HEAD~1 sources/yoreh-deah/siman-234
  python3 scripts/verifier-residus.py --tous            # tout ce que l'arbre modifie

Sort en 1 s'il reste un résidu.
"""
import sys, os, re, subprocess, unicodedata, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BALISE = re.compile(r'<[^>]+>')
NIKOUD = re.compile(r'[֑-ׇ]')
HEB = re.compile(r'[א-ת]')

# Une citation verbatim n'est pas une affirmation : elle vit légitimement dans plusieurs
# fichiers, et l'y retrouver ne prouve rien. Même raison qu'ailleurs dans ce dépôt — les
# guillemets sont réservés au verbatim, et les blocs de source le sont par construction.
CITATION = re.compile(r'«[^»]{0,800}»|\u201c[^\u201d]{0,800}\u201d')
BLOC_SOURCE = re.compile(r'class="(?:text-source|comment-source|src-ref|he-q|sa-he|translation)"')

def sans_citation(s):
    return CITATION.sub(lambda m: ' ' * len(m.group(0)), s)

def nettoyer(s):
    s = BALISE.sub(' ', s)
    s = (s.replace('&nbsp;', ' ').replace('&amp;', '&')
          .replace('&quot;', '"').replace('&#39;', "'"))
    s = NIKOUD.sub('', s)
    return re.sub(r'\s+', ' ', s).strip()

def mots(s, hebreu):
    if hebreu:
        return [w for w in re.findall(r'[א-ת״׳"\']+', s) if len(w) > 1]
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return [w for w in re.findall(r"[a-z0-9]+", s) if len(w) > 2]

def ngrammes(texte):
    """Rend l'ensemble des n-grammes d'un texte — 5 mots en latin, 3 en hébreu."""
    out = set()
    for hebreu, n in ((False, 5), (True, 3)):
        w = mots(texte, hebreu)
        for i in range(len(w) - n + 1):
            out.add((hebreu, ' '.join(w[i:i + n])))
    return out

def diff(ref, cible):
    cmd = ["git", "-C", ROOT, "diff", "-U0"]
    if ref:
        cmd.append(ref)
    cmd += ["--", cible]
    return subprocess.run(cmd, capture_output=True, text=True).stdout

def analyser(dossier, ref):
    rel = os.path.relpath(dossier, ROOT)
    d = diff(ref, rel)
    if not d.strip():
        return [], 0
    retires, ajoutes = [], []
    # Les lignes que l'édition a elle-même touchées ne sont pas des résidus : ce qui y
    # subsiste y subsiste volontairement. On relève donc les plages « + » de chaque
    # fichier pour les écarter — sans quoi toute phrase dont on change UN mot serait
    # signalée comme survivant… à sa propre ligne.
    touchees = defaultdict(set)
    fichier = None
    for ligne in d.split('\n'):
        if ligne.startswith('+++ b/'):
            fichier = os.path.join(ROOT, ligne[6:].strip())
        elif ligne.startswith('@@') and fichier:
            m = re.search(r'\+(\d+)(?:,(\d+))?', ligne)
            if m:
                deb = int(m.group(1)); n = int(m.group(2) or 1)
                touchees[fichier] |= set(range(deb - 1, deb + n + 1))
    for ligne in d.split('\n'):
        if ligne.startswith('-') and not ligne.startswith('---'):
            brut = ligne[1:]
            retires.append('' if BLOC_SOURCE.search(brut)
                           else nettoyer(sans_citation(brut)))
        elif ligne.startswith('+') and not ligne.startswith('+++'):
            ajoutes.append(nettoyer(sans_citation(ligne[1:])))
    if not retires:
        return [], 0

    n_ajoutes = set()
    for a in ajoutes:
        n_ajoutes |= ngrammes(a)
    # ce qui était censé disparaître : présent dans le retiré, absent de l'ajouté
    candidats = set()
    for r in retires:
        candidats |= ngrammes(r)
    candidats -= n_ajoutes
    if not candidats:
        return [], 0

    # index du siman tel qu'il est MAINTENANT
    index = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(dossier, '*.html'))):
        for no, ligne in enumerate(open(p, encoding='utf-8'), 1):
            if BLOC_SOURCE.search(ligne):
                continue
            txt = nettoyer(sans_citation(ligne))
            if not txt:
                continue
            for cle in ngrammes(txt):
                index[cle].append((p, no, txt))

    residus = []
    for cle in candidats:
        for p, no, txt in index.get(cle, []):
            if no in touchees.get(p, ()):
                continue
            residus.append((cle[1], p, no, txt))
    # dédoublonner par (fichier, ligne) en gardant le n-gramme le plus long
    par_lieu = {}
    for ng, p, no, txt in residus:
        k = (p, no)
        if k not in par_lieu or len(ng) > len(par_lieu[k][0]):
            par_lieu[k] = (ng, txt)
    return [(ng, p, no, txt) for (p, no), (ng, txt) in sorted(par_lieu.items())], len(candidats)

def main():
    args = sys.argv[1:]
    ref = None
    if '--depuis' in args:
        i = args.index('--depuis')
        ref = args[i + 1]
        args = args[:i] + args[i + 2:]
    if '--tous' in args:
        args.remove('--tous')
        modifs = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"],
                                capture_output=True, text=True).stdout
        dossiers = sorted({os.path.join(ROOT, os.path.dirname(l[3:].strip()))
                           for l in modifs.split('\n')
                           if '/siman-' in l and l.strip().endswith('.html')})
    else:
        dossiers = [a if os.path.isabs(a) else os.path.join(ROOT, a) for a in args]
    if not dossiers:
        print("Rien à examiner. Donne un dossier de siman, ou --tous.")
        return 0

    total = 0
    for d in dossiers:
        residus, nb = analyser(d, ref)
        nom = os.path.relpath(d, ROOT)
        if not residus:
            print(f"✅ {nom} — {nb} formulations retirées, aucune ne survit ailleurs")
            continue
        print(f"❌ {nom} — {len(residus)} RÉSIDUS "
              f"(formulations retirées quelque part, vivantes ailleurs)")
        for ng, p, no, txt in residus:
            print(f"   {os.path.relpath(p, ROOT)}:{no}")
            print(f"     n-gramme retiré ailleurs : « {ng} »")
            print(f"     la ligne dit            : {txt[:150]}")
        total += len(residus)
    print()
    print(f"Résidus : {total}")
    if total:
        print("Chacun est une phrase corrigée à un endroit et laissée debout à un autre —")
        print("souvent une meta description, un sous-titre héros ou un JSON-LD, que le")
        print("lecteur voit et que le correcteur n'avait pas ouvert.")
    return 1 if total else 0

if __name__ == '__main__':
    sys.exit(main())
