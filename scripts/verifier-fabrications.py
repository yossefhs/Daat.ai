#!/usr/bin/env python3
"""Une citation qui n'existe NULLE PART — la porte que quatre fabrications ont exigée.

Le 19 septembre 2026, en réparant le bloc נדה, quatre citations hébraïques se sont
révélées inventées, sur des pages en ligne et vertes à toutes les portes :

  · siman 187 — « אין אנו נוהגין להוציאה », attribuée au Rama, 136 occurrences, dont une
    LIGNE DE PSAK du niveau 4 référencée « Choul'han Aroukh YD 187:1 ». Elle renversait
    le siman : la glose réelle du Rama au séif 1 est une rigueur — ונאסרה על בעלה — et la
    page en faisait un allègement.
  · siman 187 — « אין כל האצבעות שוות », attribuée au Taz ס״ק ב-ג, 15 occurrences. Le Taz
    écrit לפי שאין כל אצבעו׳ שוו׳.
  · siman 196 — « תספור לה שבעה ימים מהיום שתפסוק בטהרה », attribuée au Mehaber. Le séif 1
    ouvre en réalité שבעת ימים שהזבה סופרת מתחילין ממחרת יום שפסקה בו.
  · siman 192 — « אבל אין לטבול הרבה ימים קודם », attribuée au Rama. Il écrit
    אבל אין להרחיק הטבילה מן הבעילה יותר מזה.

POURQUOI LES AUTRES PORTES NE LES VOIENT PAS. `verifier-citations.py` ne juge que les
citations de 25 lettres ou plus — seuil posé pour ne pas accuser les termes techniques
entre guillemets — et il lui faut une référence sur la ligne. La première fabrication
compte 22 lettres, la dernière 23. Le seuil les a couvertes, et le psak inversé avec.

CE QUE CELLE-CI FAIT, ET QUI NE DÉPEND D'AUCUN SEUIL. Elle prend chaque citation hébraïque
— quelle que soit sa longueur — et demande à la recherche plein-texte de Sefaria si cette
suite de mots existe QUELQUE PART dans le corpus. Pas « à la référence citée » : nulle
part. Une citation qui ne s'y trouve pas est soit inventée, soit altérée au point de ne
plus être la source — et les deux sont des défauts.

ELLE REND DES CANDIDATS, jamais des verdicts sur le fond : une orthographe défective, un
nikoud, un mot recollé suffisent à rendre zéro. C'est précisément l'intérêt — « אין כל
האצבעות שוות » est introuvable parce que le Taz écrit אצבעו׳ שוו׳, et c'est bien un
défaut. Mais le tri revient au lecteur, et le script ne réécrit jamais rien.

Usage :
  python3 scripts/verifier-fabrications.py --path sources/yoreh-deah/siman-187
  python3 scripts/verifier-fabrications.py 183 184 185
  python3 scripts/verifier-fabrications.py --path sources/yoreh-deah --bref
"""
import re, sys, os, io, json, glob, subprocess, unicodedata, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache-fabrications.json")

# Plage ÉTROITE, et la raison mérite d'être écrite parce que je l'ai apprise deux fois.
# La plage large 0591-05C7 contient le MAQAF (U+05BE), le paseq (U+05C0) et le sof pasuq
# (U+05C3), qui ne sont pas du nikoud mais de la PONCTUATION. Les supprimer soude les
# mots : לֹא־תַשִּׁיךְ devenait לאתשיך et כָּל־דָּבָר devenait כלדבר, si bien que des versets
# parfaitement recopiés sortaient « introuvables dans tout Sefaria ». Le maqaf devient
# une espace, il ne disparaît pas.
NIKOUD = re.compile('[\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7]')
SEPARATEURS = re.compile('[\u05BE\u05C0\u05C3]')
HEB = re.compile(r'[א-ת]')

# Les citations hébraïques d'une page : le span he-q, et l'hébreu entre guillemets.
RX_HEQ = re.compile(r'<span class="he-q"[^>]*>(.*?)</span>', re.S)
RX_GUIL = re.compile(r'«\s*(?:&nbsp;)?\s*([^»]{4,400}?)\s*(?:&nbsp;)?\s*»')

def nettoyer(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = (s.replace('&nbsp;', ' ').replace('&amp;', '&')
          .replace('&quot;', '"').replace('&#39;', "'"))
    s = unicodedata.normalize('NFC', s)
    s = SEPARATEURS.sub(' ', s)
    s = NIKOUD.sub('', s)
    return re.sub(r'\s+', ' ', s).strip()

def mots_he(s):
    return [w for w in s.split() if HEB.search(w)]

def segments(citation):
    """Une ellipse sépare deux verbatims : chacun se vérifie seul (règle du dépôt)."""
    return [p.strip() for p in re.split(r'…|\.\.\.', citation) if p.strip()]

_C = {}
if os.path.exists(CACHE):
    try:
        _C = json.load(open(CACHE, encoding='utf-8'))
    except Exception:
        _C = {}

def _ecrire():
    try:
        json.dump(_C, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception:
        pass

def hits(phrase):
    """Combien de fois cette suite de mots paraît-elle dans TOUT Sefaria ?"""
    if phrase in _C:
        return _C[phrase]
    # `field: "exact"` est la forme employée par `locate()` dans
    # verifier-citations.py, sur ce même point de terminaison. Mesuré le
    # 22 septembre 2026, il ne change RIEN au résultat : cinq essais — un
    # verbatim contigu, les mêmes mots dans l'ordre inverse, des mots du même
    # séif non contigus, un verbatim court et sa permutation — rendent le même
    # compte avec et sans lui, la recherche se comportant déjà comme une
    # recherche de séquence. Il est donc posé pour ne pas faire reposer une
    # porte anti-fabrication sur un comportement par défaut non documenté, et
    # non pour réparer un défaut observé.
    corps = json.dumps({"query": phrase, "type": "text", "field": "exact", "size": 3},
                       ensure_ascii=False)
    for essai in range(3):
        try:
            out = subprocess.run(
                ["curl", "-s", "-X", "POST",
                 "https://www.sefaria.org/api/search-wrapper",
                 "-H", "Content-Type: application/json",
                 "--data-binary", "@-"],
                input=corps, capture_output=True, text=True, timeout=60).stdout
            n = json.loads(out)['hits']['total']
            if isinstance(n, dict):
                n = n.get('value', 0)
            _C[phrase] = n
            _ecrire()
            return n
        except Exception:
            time.sleep(1 + essai)
    return None

# Sous ce nombre de mots, une « citation » est un terme technique, pas une phrase :
# la chercher n'apprend rien et la recherche rendrait des milliers de résultats.
MIN_MOTS = 3

def citations(path):
    s = io.open(path, encoding='utf-8').read()
    vues = set()
    for m in RX_HEQ.finditer(s):
        for seg in segments(nettoyer(m.group(1))):
            if len(mots_he(seg)) >= MIN_MOTS:
                vues.add(seg)
    for m in RX_GUIL.finditer(s):
        brut = m.group(1)
        if not HEB.search(brut):
            continue
        for seg in segments(nettoyer(brut)):
            w = mots_he(seg)
            # entre guillemets, seul l'hébreu franc est jugé : une phrase française
            # qui cite deux mots hébreux n'est pas une citation hébraïque.
            if len(w) >= MIN_MOTS and len(w) >= len(seg.split()) * 0.7:
                vues.add(seg)
    return vues

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    bref = '--bref' in sys.argv
    if '--path' in sys.argv:
        cible = sys.argv[sys.argv.index('--path') + 1]
        racines = ([cible] if os.path.basename(cible).startswith('siman-')
                   else sorted(glob.glob(os.path.join(cible, 'siman-*'))))
    elif args:
        racines = [os.path.join(ROOT, 'sources', 'yoreh-deah', f'siman-{a}') for a in args]
    else:
        print(__doc__); return 2

    tot = absent = 0
    for d in racines:
        vues = {}
        for p in sorted(glob.glob(os.path.join(d, '*.html'))):
            for c in citations(p):
                vues.setdefault(c, []).append(os.path.relpath(p, ROOT))
        for c, ou in sorted(vues.items()):
            tot += 1
            n = hits(c)
            if n is None:
                print(f"?  {os.path.relpath(d, ROOT)} — recherche impossible : « {c[:70]} »")
                continue
            if n == 0:
                absent += 1
                print(f"INTROUVABLE DANS TOUT SEFARIA — {os.path.relpath(d, ROOT)}")
                print(f"   « {c} »")
                print(f"   {len(ou)} fichier(s) : {', '.join(os.path.basename(x) for x in ou[:4])}"
                      + (" …" if len(ou) > 4 else ""))
                if not bref:
                    print()
    print()
    print(f"Citations hébraïques examinées : {tot}")
    print(f"INTROUVABLES dans tout Sefaria : {absent}")
    print()
    print("« Introuvable » ne veut pas dire « inventée » à coup sûr : un ktiv défectif,")
    print("un mot recollé, une abréviation développée suffisent. Mais chacun de ces trois")
    print("cas est lui-même un défaut, et les quatre fabrications du bloc נדה sont sorties")
    print("exactement par là. Le tri revient au lecteur ; le script ne réécrit rien.")
    return 1 if absent else 0

if __name__ == '__main__':
    sys.exit(main())
