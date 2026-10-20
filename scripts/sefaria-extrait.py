#!/usr/bin/env python3
"""sefaria-extrait.py — extraire le texte source de Sefaria, sans jamais le retaper.

Règle 29 des cahiers des charges (docs/brief-yoreh-deah.md, docs/brief-orah-haim-366.md) : un mot
d'hébreu ne se retape pas, il s'EXTRAIT de la source. Cet outil rend la chaîne réelle de Sefaria —
nikoud, ktiv et ponctuation compris — ou échoue. Un extrait introuvable, ou trouvé à plusieurs
endroits, est une ERREUR (code 2 ou 3), jamais un « à peu près ».

Usages :
  python3 scripts/sefaria-extrait.py seif SAH 366 3          # texte du séif 3 du Choul'han Aroukh HaRav (Kehot vocalisée)
  python3 scripts/sefaria-extrait.py seif SA 366 3           # séif 3 du Mehaber, édition par défaut (Maginei Eretz)
  python3 scripts/sefaria-extrait.py seif SA 366 3 --edition "Torat Emet 363"
  python3 scripts/sefaria-extrait.py seif MB 366 12          # ס״ק 12 de la Michna Beroura
  python3 scripts/sefaria-extrait.py compte SAH 366          # nombre de segments (séifim, ס״ק) et chapeau
  python3 scripts/sefaria-extrait.py extrait SAH 366 3 "מותר לטלטל"            # sous-chaîne exacte du séif 3
  python3 scripts/sefaria-extrait.py extrait SAH 366 3 --debut "אם" --fin "מותר"  # de la 1re occurrence de « אם » à « מותר »
  python3 scripts/sefaria-extrait.py extrait REF "Eruvin.49a" 0 "אמר רב"       # toute ref Sefaria (0 = tout le texte)
  python3 scripts/sefaria-extrait.py editions SA 366          # éditions hébraïques servies par l'API v3

Ouvrages : SA (Shulchan_Arukh,_Orach_Chayim), SAH (Shulchan_Arukh_HaRav,_Orach_Chayim), KA (Kuntres_Acharon
on SA HaRav), MB (Mishnah_Berurah), BH (Biur_Halacha), MA (Magen_Avraham), TAZ (Turei_Zahav on OC), BY
(Beit_Yosef, Orach Chayim), TUR (Tur, Orach Chayim), REF (une ref Sefaria quelconque, donnée à la place du
siman ; le séif vaut alors 0 pour tout le texte, ou l'indice du segment, à partir de 1).

Ce que fait le nettoyage (option --brut pour ne rien nettoyer) :
  · retire les appels de note et d'appareil (<i data-commentator=… ></i>, <i class="footnote">…</i> SIGNALÉ) ;
  · garde <b>, <br>, <small> (la glose du Rama vit dans un <small>), retire les autres balises ;
  · convertit le guillemet droit ENTRE deux lettres hébraïques en gershayim ״ (convention du site) ;
  · laisse l'apostrophe telle quelle (le site recopie « י' », « אפי' » comme la source).
La comparaison d'un extrait se fait sur le SQUELETTE consonantique ([א-ת] seulement, finales comprises) :
on retrouve la place, puis on rend la sous-chaîne RÉELLE de la source, marques combinantes comprises.

Le cache (--cache, par défaut scripts/.cache-sefaria/extrait/) garde chaque réponse JSON VALIDE ; une
réponse « error » ou une page HTML (« 503 Backend fetch failed ») n'est jamais gravée.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DEFAUT = os.path.join(ROOT, 'scripts', '.cache-sefaria', 'extrait')

OUVRAGES = {
    'SA':  ('Shulchan_Arukh,_Orach_Chayim', 'Maginei Eretz: Shulchan Aruch Orach Chaim, Lemberg, 1893'),
    'SAH': ('Shulchan_Arukh_HaRav,_Orach_Chayim', 'Vocalized Edition - Kehot Publication Society'),
    'KA':  ('Kuntres_Acharon_on_Shulchan_Arukh_HaRav,_Orach_Chayim', None),
    'MB':  ('Mishnah_Berurah', None),
    'BH':  ('Biur_Halacha', None),
    'MA':  ('Magen_Avraham', None),
    'TAZ': ('Turei_Zahav_on_Shulchan_Arukh,_Orach_Chayim', None),
    'BY':  ('Beit_Yosef,_Orach_Chayim', None),
    'TUR': ('Tur,_Orach_Chayim', None),
}

HEB = re.compile(r'[א-ת]')


def _get(url, cache, essais=5):
    os.makedirs(cache, exist_ok=True)
    nom = re.sub(r'[^A-Za-z0-9_.,-]+', '_', url.split('/api/', 1)[-1])[:180] + '.json'
    chemin = os.path.join(cache, nom)
    if os.path.exists(chemin):
        with open(chemin, encoding='utf-8') as f:
            return json.load(f)
    derniere = None
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'daat-extrait/1.0'})
            with urllib.request.urlopen(req, timeout=60) as r:
                corps = r.read().decode('utf-8')
            d = json.loads(corps)          # une page HTML « 503 » lève ici
            if isinstance(d, dict) and d.get('error'):
                raise ValueError('Sefaria error : %s' % d['error'])
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False)
            return d
        except Exception as e:                # noqa: BLE001 — on réessaie, puis on échoue en clair
            derniere = e
            time.sleep(2 * (i + 1))
    raise SystemExit('ÉCHEC du téléchargement après %d essais : %s\n  %s' % (essais, url, derniere))


def _aplatir(x):
    if isinstance(x, str):
        return [x]
    out = []
    for y in x or []:
        out.extend(_aplatir(y))
    return out


def segments(ouvrage, siman, edition=None, cache=CACHE_DEFAUT):
    """Rend (ref servie, édition servie, liste des segments bruts) — un segment par séif / ס״ק."""
    if ouvrage == 'REF':
        ref = str(siman)
        livre_attendu = None
    else:
        livre, ed_defaut = OUVRAGES[ouvrage]
        ref = '%s.%s' % (livre, siman)
        livre_attendu = livre
        edition = edition or ed_defaut
    q = urllib.parse.quote(ref, safe='_,.:')
    if edition:
        url = 'https://www.sefaria.org/api/v3/texts/%s?version=%s' % (q, urllib.parse.quote('hebrew|' + edition))
        d = _get(url, cache)
        vs = [v for v in d.get('versions', []) if v.get('versionTitle') == edition]
        if not vs:
            raise SystemExit('Édition « %s » absente pour %s (servies : %s)' % (
                edition, ref, ', '.join(v.get('versionTitle', '?') for v in d.get('versions', []))))
        texte = vs[0].get('text')
        servie = d.get('ref', ref)
    else:
        url = 'https://www.sefaria.org/api/texts/%s?context=0&pad=0' % q
        d = _get(url, cache)
        texte = d.get('he')
        servie = d.get('ref', ref)
        edition = d.get('heVersionTitle')
    # garde : la ref servie doit être celle demandée (Sefaria retombe parfois sur une autre œuvre)
    if livre_attendu:
        attendu = livre_attendu.replace('_', ' ').replace(',', ',')
        if not servie.replace('_', ' ').startswith(attendu.split(',')[0]) or not servie.rstrip().endswith(' %s' % siman):
            raise SystemExit('REF SERVIE INATTENDUE : demandé %s, servi %s' % (ref, servie))
    segs = texte if isinstance(texte, list) else [texte]
    if segs and isinstance(segs[0], list):      # Talmud : segments par amoud ; on aplatit
        segs = _aplatir(segs)
    return servie, edition, [s or '' for s in segs]


NOTE_FOOTNOTE = re.compile(r'<sup[^>]*>\s*\*?\s*</sup>\s*<i class="footnote">(.*?)</i>', re.S)


def nettoyer(s, signaler=None):
    s = re.sub(r'<i\s+data-commentator="[^"]*"[^>]*>\s*</i>', '', s)
    s = re.sub(r'<i\s+data-[^>]*>\s*</i>', '', s)
    if NOTE_FOOTNOTE.search(s):
        if signaler is not None:
            signaler.append('NOTE du texte (<i class="footnote">) : gardée en ligne, sans astérisque, dans un <small>')
        s = NOTE_FOOTNOTE.sub(lambda m: ' <small>' + m.group(1).strip() + '</small>', s)
    s = re.sub(r'<(?!/?(?:b|br|small)\b)[^>]+>', '', s)
    s = re.sub(r'<br\s*/?>', '<br>', s)
    s = html.unescape(s)
    s = re.sub(r'(?<=[א-ת])"(?=[א-ת])', '״', s)
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s


def squelette(s):
    """Lettres hébraïques seulement, avec la position de chacune dans s."""
    lettres, pos = [], []
    for i, c in enumerate(s):
        if HEB.match(c):
            lettres.append(c)
            pos.append(i)
    return ''.join(lettres), pos


def _fin_lettre(s, i):
    """Étend la fin d'une lettre à ses marques combinantes (nikoud, te'amim) et geresh/gershayim collés."""
    j = i + 1
    while j < len(s) and ('֑' <= s[j] <= 'ׇ' or s[j] in '׳״'):
        j += 1
    return j


def trouver(source, fragment):
    """Toutes les occurrences (début, fin) du fragment dans la source, au squelette consonantique."""
    sq, pos = squelette(source)
    f, _ = squelette(fragment)
    if not f:
        raise SystemExit('Fragment sans lettre hébraïque : %r' % fragment)
    occ, k = [], sq.find(f)
    while k != -1:
        occ.append((pos[k], _fin_lettre(source, pos[k + len(f) - 1])))
        k = sq.find(f, k + 1)
    return occ


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('action', choices=['seif', 'compte', 'extrait', 'editions'])
    ap.add_argument('ouvrage', choices=sorted(OUVRAGES) + ['REF'])
    ap.add_argument('siman', help='numéro du siman (ou la ref Sefaria avec REF)')
    ap.add_argument('seif', nargs='?', type=int, default=0, help='séif / ס״ק, à partir de 1 ; 0 = tout')
    ap.add_argument('fragment', nargs='?', help='extrait cherché (action extrait)')
    ap.add_argument('--debut'); ap.add_argument('--fin')
    ap.add_argument('--edition', help='versionTitle exact (sinon : Maginei Eretz pour SA, Kehot vocalisée pour SAH)')
    ap.add_argument('--brut', action='store_true', help='ne pas nettoyer le texte')
    ap.add_argument('--premier', action='store_true', help='accepter la première de plusieurs occurrences (déconseillé)')
    ap.add_argument('--cache', default=CACHE_DEFAUT)
    a = ap.parse_args()

    if a.action == 'editions':
        livre = OUVRAGES[a.ouvrage][0] if a.ouvrage != 'REF' else a.siman
        ref = livre if a.ouvrage == 'REF' else '%s.%s' % (livre, a.siman)
        d = _get('https://www.sefaria.org/api/v3/texts/%s?version=hebrew%%7Call' % urllib.parse.quote(ref, safe='_,.:'), a.cache)
        for v in d.get('versions', []):
            t = v.get('text')
            n = len(t) if isinstance(t, list) else 1
            print('%-70s %4d segment(s)' % (v.get('versionTitle'), n))
        return 0

    servie, edition, segs = segments(a.ouvrage, a.siman, a.edition, a.cache)
    notes = []
    if a.action == 'compte':
        print('%s · %s · %d segment(s)' % (servie, edition, len(segs)))
        if segs:
            m = re.search(r'ובו\s+([^\s:]+(?:\s+[^\s:]+)?)\s+סעיפים|ובו\s+סעיף\s+אחד', re.sub(r'[֑-ׇ]', '', nettoyer(segs[0])))
            print('chapeau : %s' % (m.group(0) if m else '(aucun « ובו … סעיפים » dans le segment 1)'))
        vides = [i + 1 for i, s in enumerate(segs) if not squelette(s)[0]]
        if vides:
            print('⚠ segments vides : %s' % vides)
        return 0

    if a.seif:
        if not 1 <= a.seif <= len(segs):
            raise SystemExit('Segment %d hors limites : %s en a %d' % (a.seif, servie, len(segs)))
        texte = segs[a.seif - 1]
    else:
        texte = ' '.join(segs)
    texte = texte if a.brut else nettoyer(texte, notes)

    if a.action == 'seif':
        print(texte)
        for n in notes:
            print('⚠ ' + n, file=sys.stderr)
        return 0

    # extrait
    if a.debut or a.fin:
        if not (a.debut and a.fin):
            raise SystemExit('--debut et --fin vont ensemble')
        o1, o2 = trouver(texte, a.debut), trouver(texte, a.fin)
        if not o1 or not o2:
            print('INTROUVABLE : %s' % ('début' if not o1 else 'fin'), file=sys.stderr)
            return 2
        d0 = o1[0][0]
        fins = [f for (s, f) in o2 if s >= d0]
        if not fins:
            print('INTROUVABLE : aucune fin après le début', file=sys.stderr)
            return 2
        if (len(o1) > 1 or len(fins) > 1) and not a.premier:
            print('AMBIGU : début ×%d, fin ×%d — préciser (ou --premier)' % (len(o1), len(fins)), file=sys.stderr)
            return 3
        print(texte[d0:fins[0]])
        return 0
    if not a.fragment:
        raise SystemExit('extrait : donner le fragment, ou --debut et --fin')
    occ = trouver(texte, a.fragment)
    if not occ:
        print('INTROUVABLE dans %s%s' % (servie, (':%d' % a.seif) if a.seif else ''), file=sys.stderr)
        return 2
    if len(occ) > 1 and not a.premier:
        print('AMBIGU : %d occurrences dans %s — allonger le fragment (ou --premier)' % (len(occ), servie), file=sys.stderr)
        for s, f in occ:
            print('  … %s …' % texte[max(0, s - 30):f + 30], file=sys.stderr)
        return 3
    s, f = occ[0]
    print(texte[s:f])
    return 0


if __name__ == '__main__':
    sys.exit(main())
