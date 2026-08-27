#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
veilleur.py — cherche en continu ce que les autres gates ne voient pas.

Les gates existants vérifient la FORME (audit-simanim), les CITATIONS hébraïques
(verifier-citations), la LANGUE (verifier-langues). Or les quatre erreurs de fond
trouvées lors de l'audit rabbinique d'août 2026 les ont TOUTES franchies sans
alerte, parce qu'aucune citation n'était fausse : c'est le raisonnement français
qui l'était.

  318 — machloket Mehaber/Rama inversée
  253 — « tout le siman découle d'une seule crainte »
  308 — « un objet n'est pas mouktsé en soi »
  320 — citron et orange confondus, le séif 320:6 jamais mentionné

Ces quatre erreurs partagent une signature exploitable :

  A. un séif entier du Choulhan Aroukh n'est jamais mentionné par les pages du
     siman — c'est exactement le cas du 320:6 (« מותר לסחוט לימוני״ש »), qui
     portait la permission décisive ;
  B. la page emploie une formulation ABSOLUE (« une seule », « tous s'accordent »,
     « n'est pas … en soi ») — les quatre l'avaient ;
  C. un concept présent dans le niveau 1 (texte primaire) ou le niveau 4 (Admour
     HaZaken) est ABSENT de la synthèse — le site contient alors son propre
     correctif sans le savoir (cas du 253 : מחזי כמבשל était dans le niveau 4).

Le script ne comprend pas le sens. Il produit des CANDIDATS à relecture, jamais
un verdict — et n'écrit jamais dans les pages. Sortie : rapport + option
--signalements pour déposer les candidats dans le registre existant, en
NEEDS_RABBINIC_VALIDATION, afin que le Rav les traite au même endroit que les
retours de lecteurs.
"""
import argparse, json, os, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / 'audit' / '.veilleur-cache.json'
SECTIONS = {'shabbat': 'Shulchan_Arukh,_Orach_Chayim', 'orah-haim': 'Shulchan_Arukh,_Orach_Chayim'}

HE_NUM = {1:'א',2:'ב',3:'ג',4:'ד',5:'ה',6:'ו',7:'ז',8:'ח',9:'ט',10:'י',11:'י״א',12:'י״ב',13:'י״ג',
          14:'י״ד',15:'ט״ו',16:'ט״ז',17:'י״ז',18:'י״ח',19:'י״ט',20:'כ',21:'כ״א',22:'כ״ב',23:'כ״ג',
          24:'כ״ד',25:'כ״ה',26:'כ״ו',27:'כ״ז',28:'כ״ח',29:'כ״ט',30:'ל'}

# B — formulations absolues : marqueurs relevés sur les 4 erreurs réelles
ABSOLUS = [
    # (motif, explication, priorité) — la priorité vient du rendement observé :
    # « une seule crainte » a donné 2 vraies erreurs sur 2 (253, 275) ; « toujours
    # interdit » est majoritairement légitime dans les tableaux pédagogiques.
    (r"une seule (?:crainte|peur|raison|règle)|tourne autour d'une seule", "affirme un principe unique pour tout un siman", "haute"),
    (r"n'est pas .{0,30}« ?en soi ? »", "nie un statut intrinsèque", "haute"),
    (r"(?:Mehaber|Mé'haber) (?:permet|interdit).{0,60}Rama (?:permet|interdit)", "attribution croisée Mehaber/Rama — à confronter au texte", "haute"),
    (r"tous s'accordent", "prête un consensus", "moyenne"),
    (r"\btous les (?:cas|scénarios|détails) (?:sont|so)", "prétend à l'exhaustivité", "moyenne"),
    (r"il suffit de", "réduit une condition à une seule", "basse"),
    (r"\btoujours permis\b|\btoujours interdit\b", "absolu sans exception", "basse"),
    (r"\bjamais\b.{0,40}\b(?:permis|interdit)\b", "absolu sans exception", "basse"),
]

def strip_nikud(s):
    return re.sub(r'[֑-ׇ]', '', s)

def text_of(html):
    html = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', html)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html))

def load_cache():
    if CACHE.exists():
        try: return json.loads(CACHE.read_text())
        except Exception: pass
    return {}

def save_cache(c):
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(c, ensure_ascii=False))

def sefaria_seifim(book, siman, cache):
    key = f'{book}.{siman}'
    if key in cache: return cache[key]
    url = f'https://www.sefaria.org/api/texts/{book}.{siman}?lang=he&context=0'
    try:
        d = json.load(urllib.request.urlopen(url, timeout=30))
        he = d.get('he') or []
        seifim = [strip_nikud(re.sub('<[^>]+>', '', str(x))) for x in he] if isinstance(he, list) else []
    except Exception:
        seifim = []
    cache[key] = seifim
    time.sleep(0.3)
    return seifim

def pages_of(sec, siman):
    d = ROOT / 'sources' / sec / f'siman-{siman}'
    if not d.is_dir(): return {}
    out = {}
    for stem in ('niveau-1-base', 'niveau-2-lamdan', 'niveau-3-synthese',
                 'niveau-4-daat-harav', 'niveau-4-halakha', 'index'):
        f = d / f'{stem}.html'
        if f.exists(): out[stem] = f.read_text(errors='ignore')
    return out

def detect_seifim_orphelins(siman, pages, seifim):
    """A — un séif du texte n'est mentionné nulle part dans les pages du siman."""
    if not seifim: return []
    blob = ' '.join(pages.values())
    blob_he = strip_nikud(blob)
    out = []
    for i, txt in enumerate(seifim, 1):
        if len(txt.strip()) < 25:   # séif vide/technique
            continue
        # mentionné par numéro (arabe ou hébreu) ou par un fragment de son texte
        hits = re.search(rf'(?:s[ée]if|séif|סעיף)\s*{i}\b', blob, re.I) \
            or (HE_NUM.get(i) and re.search(rf'{siman}\s*:\s*{re.escape(strip_nikud(HE_NUM[i]))}', blob_he)) \
            or (HE_NUM.get(i) and re.search(rf'(?:s[ée]if|séif)\s+{re.escape(strip_nikud(HE_NUM[i]))}\b', blob_he))
        if hits: continue
        frag = ' '.join(txt.split()[:4])
        if frag and strip_nikud(frag) in blob_he: continue
        out.append({'type': 'seif_non_couvert', 'siman': siman, 'seif': i,
                    'detail': f"Le séif {i} du Choulhan Aroukh n'est mentionné dans aucune page du siman.",
                    'extrait': txt[:160]})
    return out

def detect_absolus(siman, pages):
    """B — formulations absolues, marqueur commun aux 4 erreurs connues."""
    out = []
    for stem, html in pages.items():
        t = text_of(html)
        for pat, why, prio in ABSOLUS:
            for m in re.finditer(pat, t, re.I):
                ctx = t[max(0, m.start()-90):m.end()+90].strip()
                out.append({'type': 'formulation_absolue', 'siman': siman, 'page': stem,
                            'detail': why, 'extrait': ctx, 'priorite': prio})
                break   # un signalement par motif et par page
    return out

def detect_concept_orphelin(siman, pages):
    """C — concept hébreu présent dans le niveau 1 ou 4, absent de la synthèse."""
    syn = pages.get('niveau-3-synthese')
    if not syn: return []
    src = (pages.get('niveau-4-daat-harav') or '') + (pages.get('niveau-4-halakha') or '') + (pages.get('niveau-1-base') or '')
    if not src: return []
    syn_he = strip_nikud(text_of(syn))
    src_he = strip_nikud(text_of(src))
    # concepts halakhiques structurants : expressions hébraïques de 2-3 mots récurrentes
    cands = re.findall(r'(?:מחזי|נראה|משום|גזירה|איסור|מפני)\s+\S+(?:\s+\S+)?', src_he)
    seen, out = set(), []
    for c in cands:
        c = c.strip()
        if len(c) < 8 or c in seen: continue
        seen.add(c)
        if src_he.count(c) >= 2 and c not in syn_he:
            out.append({'type': 'concept_absent_synthese', 'siman': siman,
                        'detail': f"« {c} » apparaît {src_he.count(c)}× dans le texte primaire / niveau 4, jamais dans la synthèse.",
                        'extrait': c})
    return out[:3]

def pages_questions():
    """Les pages /questions/ sont dérivées des simanim : mêmes détecteurs."""
    d = ROOT / 'questions'
    return {f.stem: f.read_text(errors='ignore') for f in d.glob('*.html')} if d.is_dir() else {}

ENVOYES = ROOT / 'audit' / '.veilleur-envoyes.json'
API_DEFAUT = 'https://daatai.vercel.app/api/signalement'
# Le registre attend l'une de ses 5 catégories ; on y projette nos 3 détecteurs.
TYPE_API = {'seif_non_couvert': 'source', 'formulation_absolue': 'halakha',
            'concept_absent_synthese': 'pedagogie'}


def cle_finding(f):
    """Clé stable d'un candidat — pour qu'un passage hebdomadaire ne redépose pas
    chaque semaine les mêmes lignes dans le registre du Rav."""
    return f"{f['type']}|{f['siman']}|{f.get('seif','')}|{f.get('page','')}|{(f.get('extrait') or f['detail'])[:80]}"


def admin_password():
    """ADMIN_PASSWORD depuis l'environnement, sinon depuis .env (non versionné)."""
    pw = os.environ.get('ADMIN_PASSWORD')
    if pw:
        return pw.strip()
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text(encoding='utf-8', errors='replace').splitlines():
            if line.strip().startswith('ADMIN_PASSWORD='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    return ''


def deposer_signalements(findings, api, dry=False):
    """Verse les candidats dans le registre existant, en NEEDS_RABBINIC_VALIDATION.
    La machine repère ; le Rav tranche. Rien n'est jamais écrit dans les pages."""
    pw = admin_password()
    if not pw and not dry:
        print("✗ ADMIN_PASSWORD introuvable (environnement ni .env) — rien déposé.")
        return 1
    try:
        deja = set(json.loads(ENVOYES.read_text(encoding='utf-8')))
    except Exception:
        deja = set()

    envoyes = nouveaux = doublons = 0
    for f in findings:
        k = cle_finding(f)
        if k in deja:
            continue
        nouveaux += 1
        page, siman = f.get('page', ''), f['siman']
        url = (f"https://daattorah.com/oh/{siman}" if siman
               else f"https://daattorah.com/questions/{page.split('/')[-1]}")
        desc = (f"[veilleur · {f['type']}] {f['detail']}"
                + (f"\nSéif concerné : {f['seif']}" if f.get('seif') else '')
                + (f"\nPage : {page}" if page else '')
                + (f"\nExtrait : {f['extrait'][:400]}" if f.get('extrait') else '')
                + "\n\nCandidat repéré automatiquement — à confirmer ou écarter à la "
                  "source. Aucune page n'a été modifiée.")
        payload = json.dumps({
            'url': url, 'titre': f"Siman {siman}" if siman else page,
            'siman': str(siman) if siman else '', 'seif': str(f.get('seif', '')),
            'type': TYPE_API.get(f['type'], 'pedagogie'), 'description': desc,
            'origine': 'veilleur', 'cle': k[:120], 'lang': 'fr',
        }).encode('utf-8')
        if dry:
            print(f"  [essai] {url} — {f['detail'][:70]}")
            envoyes += 1
            deja.add(k)
            continue
        req = urllib.request.Request(api, data=payload, method='POST', headers={
            'Content-Type': 'application/json', 'Authorization': 'Bearer ' + pw})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                rep = json.loads(r.read().decode())
            if rep.get('ok'):
                deja.add(k)
                # Le registre tient lui-même la liste des clés déjà déposées :
                # il refuse le doublon même si le fichier local a été perdu (CI).
                if rep.get('doublon'):
                    doublons += 1
                else:
                    envoyes += 1
        except Exception as e:
            print(f"  ✗ dépôt échoué ({e}) — {f['detail'][:60]}")
        time.sleep(0.15)

    if not dry:
        ENVOYES.parent.mkdir(parents=True, exist_ok=True)
        ENVOYES.write_text(json.dumps(sorted(deja), ensure_ascii=False, indent=0), encoding='utf-8')
    print(f"\n→ {envoyes} candidat(s) déposé(s) en « Validation du Rav requise »"
          f"{' [essai — rien envoyé]' if dry else ''} · "
          f"{len(findings) - nouveaux} déjà connu(s) localement"
          f"{f', {doublons} refusé(s) en doublon par le registre' if doublons else ''}.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--section', default='shabbat')
    ap.add_argument('--siman', type=int, action='append', help='limiter (répétable)')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--detecteur', choices=['A','B','C','tous'], default='tous')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--priorite', choices=['haute','moyenne','basse'], help='ne garder que ce niveau')
    ap.add_argument('--signalements', action='store_true',
                    help='déposer les candidats dans le registre du Rav (NEEDS_RABBINIC_VALIDATION)')
    ap.add_argument('--essai', action='store_true', help="avec --signalements : montrer sans envoyer")
    ap.add_argument('--api', default=API_DEFAUT)
    args = ap.parse_args()

    sec = args.section
    book = SECTIONS.get(sec, 'Shulchan_Arukh,_Orach_Chayim')
    base = ROOT / 'sources' / sec
    simanim = sorted(int(p.name.split('-')[1]) for p in base.glob('siman-*') if p.name.split('-')[1].isdigit())
    if args.siman: simanim = [s for s in simanim if s in args.siman]
    if args.limit: simanim = simanim[:args.limit]

    cache = load_cache()
    findings = []
    if args.detecteur in ('B','tous') and not args.siman:
        for stem, html in pages_questions().items():
            findings += detect_absolus(0, {f'questions/{stem}': html})
    for s in simanim:
        pages = pages_of(sec, s)
        if not pages: continue
        if args.detecteur in ('A','tous'):
            findings += detect_seifim_orphelins(s, pages, sefaria_seifim(book, s, cache))
        if args.detecteur in ('B','tous'):
            findings += detect_absolus(s, pages)
        if args.detecteur in ('C','tous'):
            findings += detect_concept_orphelin(s, pages)
    save_cache(cache)

    if args.priorite:
        findings = [f for f in findings if f.get('priorite', 'haute') == args.priorite]

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=1)); return 0

    if args.signalements:
        return deposer_signalements(findings, args.api, dry=args.essai)

    print(f"=== Veilleur — {len(simanim)} siman(im) de {sec} ===\n")
    if not findings:
        print("Aucun candidat.  (Absence de candidat ≠ absence d'erreur.)"); return 0
    par_type = {}
    for f in findings: par_type.setdefault(f['type'], []).append(f)
    for typ, lst in par_type.items():
        print(f"── {typ} : {len(lst)} candidat(s)")
        for f in lst[:40]:
            loc = f"siman {f['siman']}" + (f" · séif {f['seif']}" if 'seif' in f else '') + (f" · {f['page']}" if 'page' in f else '')
            print(f"   [{loc}] {f['detail']}")
            if f.get('extrait'): print(f"      … {f['extrait'][:150]}")
        if len(lst) > 40: print(f"   (+{len(lst)-40} autres)")
        print()
    print("Ce sont des CANDIDATS à relecture humaine, pas des verdicts.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
