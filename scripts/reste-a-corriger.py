#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère `audit/RESTE-A-CORRIGER.md` — l'inventaire de ce qui attend encore.

Ce fichier est **généré**, jamais écrit à la main. C'est le point : un
inventaire tenu à la main devient faux dès la première correction appliquée,
et un inventaire faux est pire que pas d'inventaire — il donne l'impression
qu'on sait où l'on en est. Ici, chaque chiffre est relu depuis sa source à
chaque exécution : les pages du site, le classeur du Rav, les gates.

    python3 scripts/reste-a-corriger.py

Ce qu'il ne sait pas dire
-------------------------
Il inventorie ce que les instruments savent voir. Or le siman 273 avait
**quatre gates verts et neuf erreurs de fond** — « même maison = même lieu »,
la souka généralisée, le kazaït absent. Aucun compteur de ce fichier ne les
aurait montrées. L'inventaire borne le travail mécanique ; il ne borne pas
l'état du contenu.
"""
from __future__ import annotations

import collections
import datetime
import importlib.util
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCES = RACINE / "sources"
SORTIE = RACINE / "audit" / "RESTE-A-CORRIGER.md"


def charger(nom: str):
    spec = importlib.util.spec_from_file_location(nom, RACINE / "scripts" / f"{nom}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def non_traduits() -> collections.Counter:
    """Séifim dont l'hébreu est reproduit et dont la traduction renvoie ailleurs."""
    v = charger("verifier-traductions")
    par_page: collections.Counter = collections.Counter()
    for f in sorted(SOURCES.rglob("niveau-*.html")):
        if f.stem.endswith(("-he", "-en")):
            continue
        for src, trad in v.paires(f):
            if len(re.findall(r"[֐-׿]", src)) >= 40 and v.NON_TRADUIT.search(trad):
                par_page[f.parent.name] += 1
    return par_page


def deja_traite() -> dict:
    """Registre des entrées déjà confrontées à la page.

    Le classeur xlsx n'est pas modifié — il reste la pièce rendue par le Rav.
    C'est ce registre qui avance, et lui seul empêche l'inventaire d'annoncer
    éternellement 66 entrées à corriger."""
    f = RACINE / "audit" / "classeur-traite.txt"
    if not f.exists():
        return {}
    out = {}
    for ligne in f.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("#") or not ligne.strip():
            continue
        parts = ligne.split(None, 2)
        if len(parts) >= 2:
            out[parts[0]] = parts[1]
    return out


def classeur() -> tuple[collections.Counter, list]:
    try:
        import openpyxl
    except ImportError:
        return collections.Counter(), []
    x = RACINE / "audit" / "audit-references-DAAT.xlsx"
    if not x.exists():
        return collections.Counter(), []
    ws = openpyxl.load_workbook(x, read_only=True)["Audit distinct"]
    rows = [r for r in ws.iter_rows(values_only=True)]
    data = [dict(zip(rows[0], r)) for r in rows[1:] if any(r)]
    fait = deja_traite()
    reste = [d for d in data
             if d["Décision finale"] != "CONFIRMÉ"
             and f'{d["Fichier normalisé"]}:{d["Ligne"]}' not in fait]
    return collections.Counter(d["Décision finale"] for d in reste), reste


def marques_rav() -> list[tuple[str, str]]:
    """Points explicitement renvoyés à l'arbitrage du Rav dans les pages."""
    motif = re.compile(r"vérifier par le Rav|לבירור אצל הרב|verified by the Rav", re.I)
    out = []
    for f in sorted(SOURCES.rglob("*.html")):
        if f.stem.endswith(("-he", "-en")):
            continue
        for m in motif.finditer(f.read_text(encoding="utf-8")):
            txt = f.read_text(encoding="utf-8")
            ctx = re.sub(r"<[^>]*>", "", txt[max(0, m.start() - 190):m.start()])
            out.append((f"{f.parent.parent.name}/{f.parent.name}",
                        re.sub(r"\s+", " ", ctx).strip()[-150:]))
    return out


def sortie_gate(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=RACINE)
        return (r.stdout or r.stderr).strip()
    except Exception as e:
        return f"(non exécuté : {e})"


def main() -> int:
    trad = non_traduits()
    dec, reste = classeur()
    rav = marques_rav()
    v_trad = sortie_gate([sys.executable, "scripts/verifier-traductions.py", "--quiet"])
    m = re.search(r"(\d+) bloc\(s\) à revoir", v_trad)
    courtes = int(m.group(1)) if m else 0

    d = datetime.date.today().isoformat()
    L = []
    a = L.append
    a("# Ce qui reste à corriger")
    a("")
    a(f"*Généré le {d} par `scripts/reste-a-corriger.py` — ne pas éditer à la main.*")
    a("")
    a("Chaque chiffre est relu depuis sa source à l'exécution : les pages du site, "
      "le classeur du Rav, les gates. Un inventaire tenu à la main devient faux dès "
      "la première correction appliquée, et un inventaire faux est pire que pas "
      "d'inventaire — il donne l'impression qu'on sait où l'on en est.")
    a("")
    a("## Ce que ce fichier ne dit pas")
    a("")
    a("Il inventorie ce que les instruments savent voir. Le siman 273 avait "
      "**quatre gates verts et neuf erreurs de fond** — « même maison = même lieu », "
      "la souka généralisée, le kazaït absent. Aucun compteur ci-dessous ne les "
      "aurait montrées. Cet inventaire borne le travail mécanique ; il ne borne pas "
      "l'état du contenu halakhique.")
    a("")
    a("Quatre simanim sur 174 ont été relus au fond — 271, 272, 273, 274. Les autres "
      "ne l'ont jamais été.")
    a("")

    a(f"## 1. Séifim non traduits — {sum(trad.values())}")
    a("")
    a("L'hébreu est reproduit, et la traduction renvoie ailleurs (« Voir l'analyse "
      "pratique : ce seif traite de… ») au lieu de rendre le texte. Le lecteur "
      "francophone a le texte hébreu et rien d'autre.")
    a("")
    if trad:
        a("| Siman | Séifim |")
        a("|---|---|")
        for k, n in sorted(trad.items(), key=lambda z: -z[1]):
            a(f"| {k.replace('siman-', '')} | {n} |")
    else:
        a("*Aucun — tous les séifim reproduits sont traduits.*")
    a("")
    a("**Méthode établie** : vérifier l'alignement bloc↔séif avant d'écrire "
      "(`verifier-alignement.py`), traduire depuis l'hébreu de la page, recouper "
      "contre la traduction anglaise de Sefaria quand elle existe, vérifier "
      "qu'il ne reste aucun renvoi.")
    a("")

    fait = deja_traite()
    bilan = collections.Counter(fait.values())
    a(f"## 2. Classeur du Rav — {sum(dec.values())} entrées non closes")
    a("")
    a(f"Déjà confrontées à la page : **{len(fait)}** — dont "
      + ", ".join(f"{n} {k.lower()}" for k, n in bilan.most_common())
      + " (registre : `audit/classeur-traite.txt`).")
    a("")
    a("| Décision | Nombre |")
    a("|---|---|")
    for k, n in dec.most_common():
        a(f"| {k} | {n} |")
    a("")
    a("⚠️ **Le classeur a été bâti sur la sortie du moteur d'audit, dont les "
      "artefacts s'y sont propagés.** Le moteur rattache une citation au daf le plus "
      "proche dans la page, même quand ce daf appartient à une autre proposition — "
      "et c'est ce daf que le classeur reproche. Sur les 50 premières entrées "
      "vérifiées, **10 décrivaient un défaut réel**. Ne jamais appliquer sans avoir "
      "lu la ligne de la page.")
    a("")
    if reste:
        par_siman = collections.Counter()
        for r in reste:
            p = str(r["Fichier normalisé"]).split("/")
            par_siman[p[2] if len(p) > 2 else "?"] += 1
        a("Simanim les plus concernés : "
          + ", ".join(f"{k.replace('siman-', '')} ({n})"
                      for k, n in par_siman.most_common(10)))
        a("")

    a("## 3. Points renvoyés à l'arbitrage du Rav")
    a("")
    if rav:
        a("Marqués « À vérifier par le Rav » directement dans les pages :")
        a("")
        for page, ctx in rav:
            a(f"- **{page}** — …{ctx}")
    else:
        a("*Aucun point en attente.*")
    a("")

    a("## 4. Non tranchés faute de localisation sûre")
    a("")
    a("La page y **paraphrase au lieu de citer**, de sorte que la comparaison "
      "littérale ne départage pas les dafim proposés. Deviner reviendrait à "
      "remplacer un daf incertain par un autre.")
    a("")
    a("| Endroit | Question |")
    a("|---|---|")
    a("| shabbat/252 | `נותנין חטין לתוך הריחים של מים` donné à או״ח רנ״ב:ה — "
      "n'y figure pas verbatim ; Sefaria le situe en שבת י״ח. |")
    a("| shabbat/284:354 | מגילה כ״ג. ou כ״ג: pour les 21 versets de la haftara |")
    a("| shabbat/287:413 | מועד קטן כ״ג: ou כ״ד. pour l'avelout à Chabbat |")
    a("| shabbat/288:456 | תענית י״ד. ou י״ט. pour « על אלו צרות מתריעין » |")
    a("| orah-haim/37 | `קרקפתא דלא מנח תפילין` absent du ראש השנה י״ז. de Sefaria, "
      "alors que les éditions courantes l'y portent — divergence de découpage probable |")
    a("| orah-haim/66 | `אינו ניזוק כל היום כולו` est la formulation du Yerushalmi ; "
      "citation composite portant des guillemets |")
    a("")

    a(f"## 5. Traductions courtes à échantillonner — {courtes} blocs")
    a("")
    a("Signalées par le décile inférieur de la distribution du site. **Ce ne sont "
      "pas des erreurs** : la dernière fois qu'une liste de ce type a été "
      "échantillonnée, les quatre blocs tirés étaient corrects et le défaut venait "
      "de l'instrument. À échantillonner avant d'en conclure quoi que ce soit.")
    a("")

    a("## 6. Signalements de citations")
    a("")
    a("`verifier-citations.py` continuera d'afficher les mêmes signalements : "
      "**ce sont des artefacts d'appariement**, pas des erreurs de page. Sur 58 "
      "triés un par un, **4 étaient réels** et sont corrigés. Trois pages accusées "
      "**disaient déjà juste** — dont une qui portait déjà une note signalant que la "
      "citation avait été faussement attribuée, note que le moteur a relue comme la "
      "citation elle-même.")
    a("")

    a("## Gates")
    a("")
    a("```")
    a(sortie_gate([sys.executable, "scripts/audit-simanim.py", "--quiet"]))
    a("```")
    a("")

    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"écrit : {SORTIE.relative_to(RACINE)}  ({len(L)} lignes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
