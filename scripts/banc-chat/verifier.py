# -*- coding: utf-8 -*-
"""Vérifie les réponses archivées par scripts/banc-chat/jouer.mjs.

    python3 scripts/banc-chat/verifier.py <DOSSIER_SORTIE> [--sources]
    python3 scripts/banc-chat/verifier.py --autotest      # gabarits synthétiques (flux en erreur, nikoud, référence non attendue)

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
if '--autotest' not in sys.argv and (not DOSSIER or not os.path.isdir(DOSSIER)):
    print(__doc__); sys.exit(2)
SOURCES = '--sources' in sys.argv
POOL = os.path.join(DOSSIER or '.', '_pool')
if DOSSIER: os.makedirs(POOL, exist_ok=True)

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

ECHEC_FLUX = ('error', 'limit_reached', 'rate_limited')

def verifier_cas(d, sources=False):
    """Rend (problemes, avertissements, infos) pour un cas archivé par jouer.mjs."""
    exp = d.get('expect') or {}
    if not d.get('tours'): return (['aucun tour'], [], {})
    tour = d['tours'][-1]; rep = tour.get('text') or ''; tools = tour.get('tools') or []; events = tour.get('events') or []
    rep_n = norm(rep)                      # sans nikoud ni ponctuation : les citations collées par la livraison vérifiée sont vocalisées
    srv = [o['input'].get('ref') for o in tools if (o.get('input') or {}).get('par') == 'serveur']
    mod = [o['input'].get('ref') for o in tools if o.get('tool') == 'sefaria_get_text' and (o.get('input') or {}).get('par') != 'serveur' and (o.get('input') or {}).get('ref')]
    pb, avert = [], []
    # ── le flux doit s'être terminé proprement : un texte partiel suivi d'une erreur n'est pas une réponse ──
    echecs_flux = [e for e in events if e.get('type') in ECHEC_FLUX]
    done = next((e for e in events if e.get('type') == 'done'), None)
    if tour.get('erreur'): pb.append('erreur du tour : ' + str(tour.get('erreur'))[:100])
    for e in echecs_flux: pb.append(f"événement d'échec dans le flux : {e.get('type')} {str(e.get('message') or e.get('error') or '')[:60]}")
    if not done and not tour.get('erreur'): pb.append('flux sans événement done')
    if done and done.get('stop_reason') == 'error': pb.append('done.stop_reason = error')
    if not rep: pb.append('réponse vide')
    # ── événements serveur : l'ensemble attendu, exactement ──
    attendus = [e['ref'] for e in (exp.get('serveur') or [])]
    for r in attendus:
        if r not in srv: pb.append(f"événement serveur manquant : {r}")
    for r in srv:
        if r not in attendus: pb.append(f"événement serveur non attendu : {r}")
    for r in exp.get('interdit') or []:
        if r in srv: pb.append(f"événement serveur interdit : {r}")
    if exp.get('modele') and not any(m.startswith(exp['modele']) for m in mod): pb.append(f"le modèle n'a pas ouvert {exp['modele']}")
    # ── fond déterministe ──
    if exp.get('ordre_253'):
        i, j = rep_n.find(norm('מצטמק ורע לו')), rep_n.find(norm('בן דרוסאי'))
        if i >= 0 and j >= 0 and i > j: pb.append('ordre des opinions du 253 INVERSÉ (בן דרוסאי avant מצטמק ורע לו)')
    if 'תישוי' in rep_n: pb.append('« תישוי » (mot inventé du 18/10) présent')
    if exp.get('langue'):
        heb = len(re.findall(r'[\u05D0-\u05EA]', rep)); lat = len(re.findall(r'[A-Za-zÀ-ÿ]', rep))
        est = 'he' if heb > lat else ('en' if re.search(r'\b(the|is|are|which|this)\b', rep) and not re.search(r'\b(les|des|une|est|dans)\b', rep[:800]) else 'fr')
        if est != exp['langue']: avert.append(f"langue estimée {est}, attendue {exp['langue']}")
    for nom in exp.get('strict') or []:
        for m in re.finditer(r'(?i)\b' + re.escape(nom) + r'\b', rep):
            fen = rep[max(0, m.start() - 160):m.end() + 160]
            if LENIENT.search(fen) and not STRICT.search(fen):
                avert.append(f"ATTRIBUTION À LIRE « {nom} » : …{fen[60:260].replace(chr(10), ' ')}…"); break
    pied = re.search(r'Vérification serveur\s*:\s*([^\n]*)', rep)
    nr = rep.count('non retrouvé')
    if sources:
        pool = ' ' + ' '.join(norm(expand(sefaria(r))) for r in srv + mod) + ' '
        psq = sq(pool); heb_ratio = len(re.findall(r'[\u05D0-\u05EA]', rep)) / max(1, len(re.findall(r'[A-Za-zÀ-ÿ\u05D0-\u05EA]', rep)))
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
    infos = {'http': tour.get('http'), 's': round((tour.get('ms') or 0) / 1000), 'srv': len(srv), 'mod': len(mod), 'pied': pied.group(1)[:70] if pied else None, 'nr': nr}
    return pb, avert, infos

def autotest():
    """Gabarits synthétiques : le vérificateur doit refuser ce qu'il refusait d'accepter (relecture Codex, #290)."""
    ok_done = {'type': 'done', 'stop_reason': 'end_turn'}
    srv = lambda ref: {'tool': 'sefaria_get_text', 'input': {'ref': ref, 'par': 'serveur'}}
    base = {'id': 'G0-propre', 'expect': {'serveur': [{'ref': 'Shulchan_Arukh,_Orach_Chayim.318'}], 'ordre_253': True},
            'tours': [{'http': 200, 'ms': 1000, 'text': 'אסור… אלא אם כן נתבשל כל צרכו והוא מצטמק ורע לו. ויש אומרים כמאכל בן דרוסאי.', 'events': [ok_done], 'tools': [srv('Shulchan_Arukh,_Orach_Chayim.318')]}]}
    gabarits = [
        ('G0 propre → doit passer', base, False),
        ('G1 texte partiel puis événement error → doit échouer', {**base, 'tours': [{**base['tours'][0], 'events': [{'type': 'error', 'message': 'Anthropic 529'}]}]}, True),
        ('G2 flux sans done → doit échouer', {**base, 'tours': [{**base['tours'][0], 'events': []}]}, True),
        ('G3 ordre inversé en hébreu VOCALISÉ → doit échouer', {**base, 'tours': [{**base['tours'][0], 'text': 'וְיֵשׁ אוֹמְרִים כְּמַאֲכַל בֶּן דְּרוּסַאי… אֶלָּא אִם כֵּן מִצְטַמֵּק וְרַע לוֹ'}]}, True),
        ('G4 référence serveur non attendue (253 en plus du 318) → doit échouer', {**base, 'tours': [{**base['tours'][0], 'tools': [srv('Shulchan_Arukh,_Orach_Chayim.318'), srv('Shulchan_Arukh,_Orach_Chayim.253')]}]}, True),
        ('G5 limit_reached après du texte → doit échouer', {**base, 'tours': [{**base['tours'][0], 'events': [{'type': 'limit_reached'}, ok_done]}]}, True),
    ]
    rate = 0
    for nom, d, doit_echouer in gabarits:
        pb, _, _ = verifier_cas(d)
        bon = bool(pb) == doit_echouer
        rate += 0 if bon else 1
        print(('✓' if bon else '✗'), nom, ('— ' + '; '.join(pb)[:120]) if pb else '')
    print(f"\nautotest : {'OK' if not rate else str(rate) + ' gabarit(s) mal jugé(s)'}")
    return rate

if '--autotest' in sys.argv:
    sys.exit(1 if autotest() else 0)

echecs = 0
fichiers = sorted(glob.glob(os.path.join(DOSSIER, '*.json')))
for jf in fichiers:
    d = json.load(open(jf, encoding='utf-8')); cid = d['id']
    pb, avert, infos = verifier_cas(d, SOURCES)
    if pb: echecs += 1
    print(f"{'✗' if pb else '✓'} {cid} · {infos.get('http')} · {infos.get('s')} s · serveur {infos.get('srv')} · modèle {infos.get('mod')} outils" + (f" · pied : {infos['pied']}" if infos.get('pied') else '') + (f" · ⚠️ {infos['nr']} « non retrouvé » signalé(s) par le serveur" if infos.get('nr') else ''))
    for p_ in pb: print('     ✗', p_)
    for a in avert: print('     •', a[:260])
print(f"\n{'ÉCHEC' if echecs else 'OK'} — {echecs} cas en échec mécanique sur {len(fichiers)}")
sys.exit(1 if echecs else 0)
