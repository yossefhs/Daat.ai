# -*- coding: utf-8 -*-
"""Vérifie les réponses archivées par scripts/banc-chat/jouer.mjs.

    python3 scripts/banc-chat/verifier.py <DOSSIER_SORTIE> [--sources]

Pour chaque cas : (1) MÉCANIQUE — les événements serveur attendus (Mehaber, Beit
Yossef chargés par api/_texte-primaire.js) sont présents, les interdits absents, l'outil
que le modèle devait ouvrir l'a été ; (2) FOND, déterministe — ordre des opinions du
253 (רנ״ג), langue de la réponse, pied « Vérification serveur » de api/_livraison.js ;
(3) avec --sources : chaque passage hébreu de la réponse (≥ 3 mots) cherché mot pour mot
dans les textes Sefaria réellement ouverts (serveur + modèle), nikoud, ponctuation,
abréviations (וי"א, ע"ג…) et ktiv haser tolérés ; les passages non retrouvés et les
attributions à lire (Rif/Rambam près d'un marqueur indulgent) sont listés POUR LECTURE —
ce sont des candidats, jamais des verdicts. Code de sortie 1 si une mécanique échoue.
"""
import glob, json, os, re, sys, urllib.parse, urllib.request

DOSSIER = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
if not DOSSIER or not os.path.isdir(DOSSIER):
    print(__doc__); sys.exit(2)
SOURCES = '--sources' in sys.argv
POOL = os.path.join(DOSSIER, '_pool'); os.makedirs(POOL, exist_ok=True)

ABR = {'וי"א': 'ויש אומרים', 'י"א': 'יש אומרים', 'ע"ג': 'על גבי', 'אע"פ': 'אף על פי', 'א"כ': 'אם כן', 'אא"כ': 'אלא אם כן',
       'מבע"י': 'מבעוד יום', 'שו"ע': 'שולחן ערוך', 'מ"מ': 'מכל מקום', 'כ"ש': 'כל שכן', "אפי'": 'אפילו', "פי'": 'פירוש', 'ת"ה': 'תורת הבית'}
def norm(t):
    t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'[֑-ׇ]', '', t)
    t = re.sub(r'[״׳"\'“”‘’«»,.;:!?()\[\]{}־–—\-/\\|*#_`>]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()
def expand(t):
    for k, v in ABR.items(): t = t.replace(k, k + ' ' + v).replace(k.replace('"', '״'), k + ' ' + v)
    return t
sq = lambda t: re.sub(r'[וי]', '', t)
def flatten(x): return [x] if isinstance(x, str) else [s for y in (x or []) for s in flatten(y)]
def sefaria(ref):
    f = os.path.join(POOL, re.sub(r'[^A-Za-z0-9._,-]', '_', ref) + '.txt')
    if os.path.exists(f): return open(f, encoding='utf-8').read()
    try:
        d = json.load(urllib.request.urlopen(f"https://www.sefaria.org/api/texts/{urllib.parse.quote(ref)}?context=0&pad=0", timeout=40))
        t = '\n'.join(flatten(d.get('he')))
    except Exception: t = ''
    open(f, 'w', encoding='utf-8').write(t); return t

HEB_RUN = re.compile(r'(?:[֐-׿][֐-׿״׳"\'’\-־]*\s*){3,}')
LENIENT = re.compile(r'(?i)indulgent|l[ée]nient|lenient|yesh omrim|יש אומרים|hananya|chananya|ḥananya|מקיל|permissive|adopted by|codifies chananya')
STRICT = re.compile(r'(?i)strict|stringent|rigoureux|s[ée]v[èe]re|\bstam\b|חכמים|rabbanan|מחמיר')

echecs = 0
for jf in sorted(glob.glob(os.path.join(DOSSIER, '*.json'))):
    d = json.load(open(jf, encoding='utf-8')); cid = d['id']; exp = d.get('expect') or {}
    if not d.get('tours'): print(f"✗ {cid} : aucun tour"); echecs += 1; continue
    tour = d['tours'][-1]; rep = tour.get('text') or ''; tools = tour.get('tools') or []
    srv = [o['input'].get('ref') for o in tools if (o.get('input') or {}).get('par') == 'serveur']
    mod = [o['input'].get('ref') for o in tools if o.get('tool') == 'sefaria_get_text' and (o.get('input') or {}).get('par') != 'serveur' and (o.get('input') or {}).get('ref')]
    pb, avert = [], []
    if tour.get('erreur') or not rep: pb.append('réponse vide ou erreur : ' + str(tour.get('erreur'))[:80])
    for e in exp.get('serveur') or []:
        if e['ref'] not in srv: pb.append(f"événement serveur manquant : {e['ref']}")
    if (exp.get('serveur') == []) and srv: pb.append(f"événement serveur inattendu : {srv}")
    for r in exp.get('interdit') or []:
        if r in srv: pb.append(f"événement serveur interdit : {r}")
    if exp.get('modele') and not any(m.startswith(exp['modele']) for m in mod): pb.append(f"le modèle n'a pas ouvert {exp['modele']}")
    if exp.get('ordre_253'):
        i, j = rep.find('מצטמק ורע לו'), rep.find('בן דרוסאי')
        if i >= 0 and j >= 0 and i > j: pb.append('ordre des opinions du 253 INVERSÉ (בן דרוסאי avant מצטמק ורע לו)')
    if 'תישוי' in rep: pb.append('« תישוי » (mot inventé du 18/10) présent')
    if exp.get('langue'):
        heb = len(re.findall(r'[א-ת]', rep)); lat = len(re.findall(r'[A-Za-zÀ-ÿ]', rep))
        est = 'he' if heb > lat else ('en' if re.search(r'\b(the|is|are|which|this)\b', rep) and not re.search(r'\b(les|des|une|est|dans)\b', rep[:800]) else 'fr')
        if est != exp['langue']: avert.append(f"langue estimée {est}, attendue {exp['langue']}")
    for nom in exp.get('strict') or []:
        for m in re.finditer(r'(?i)\b' + re.escape(nom) + r'\b', rep):
            fen = rep[max(0, m.start() - 160):m.end() + 160]
            if LENIENT.search(fen) and not STRICT.search(fen):
                avert.append(f"ATTRIBUTION À LIRE « {nom} » : …{fen[60:260].replace(chr(10), ' ')}…"); break
    pied = re.search(r'Vérification serveur\s*:\s*([^\n]*)', rep)
    nr = rep.count('non retrouvé')
    if SOURCES:
        pool = ' ' + ' '.join(norm(expand(sefaria(r))) for r in srv + mod) + ' '
        psq = sq(pool); heb_ratio = len(re.findall(r'[א-ת]', rep)) / max(1, len(re.findall(r'[A-Za-zÀ-ÿא-ת]', rep)))
        runs = [m.group(0).strip() for m in HEB_RUN.finditer(rep)]
        if heb_ratio > 0.5:   # réponse en hébreu : seules les citations marquées comptent
            runs = [r for r in runs if re.search(r'[«"“>]\s*' + re.escape(r[:12]), rep)]
        absents = []
        for r in runs:
            n = norm(r)
            if len(n.split()) < 3 or (' ' + n + ' ') in pool or n in pool: continue
            if len(n.split()) >= 4 and sq(n) in psq: continue
            absents.append(n[:90])
        if absents: avert.append(f"{len(absents)} passage(s) hébreu(x) non retrouvé(s) dans les sources ouvertes : " + ' | '.join(absents[:6]))
    etat = '✓' if not pb else '✗'
    if pb: echecs += 1
    print(f"{etat} {cid} · {tour.get('http')} · {round((tour.get('ms') or 0) / 1000)} s · serveur {len(srv)} · modèle {len(mod)} outils" + (f" · pied : {pied.group(1)[:70]}" if pied else '') + (f" · ⚠️ {nr} « non retrouvé » signalé(s) par le serveur" if nr else ''))
    for p in pb: print('     ✗', p)
    for a in avert: print('     •', a[:260])
print(f"\n{'ÉCHEC' if echecs else 'OK'} — {echecs} cas en échec mécanique sur {len(glob.glob(os.path.join(DOSSIER, '*.json')))}")
sys.exit(1 if echecs else 0)
