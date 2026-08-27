#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garde-fou anti-régression — à lancer AVANT tout push sur `main`.

Deux sessions Claude écrivent sur ce dépôt depuis des copies distinctes. Par deux
fois, une session a poussé sur `main` un commit construit sur une copie périmée,
qui a silencieusement supprimé des dizaines de simanim publiés et annulé des
correctifs appliqués à plus d'un millier de fichiers. Le message de commit ne
mentionnait rien de tel dans les deux cas.

Ce script compare l'état local à `origin/main` et refuse de laisser passer une
régression. Il ne juge pas le contenu (c'est le rôle de verifier-citations.py,
verifier-langues.py et verify-oh-source.py) : il vérifie qu'on ne DÉTRUIT rien.

    python3 scripts/verifier-integrite.py            # compare à origin/main
    python3 scripts/verifier-integrite.py --ref REF  # compare à une autre référence

Sortie non nulle = ne pas pousser. Si la suppression est intentionnelle,
relancer avec --autoriser-suppressions et le dire dans le message de commit.
"""
import json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SECTIONS = ("shabbat", "orah-haim", "yoreh-deah", "nida")


def git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def simanim_dans(ref):
    """{section: {numéro, …}} tels qu'ils existent dans une référence git."""
    out = {}
    for line in git("ls-tree", "-d", "-r", "--name-only", ref, "sources/").splitlines():
        m = re.fullmatch(r"sources/([a-z-]+)/siman-(\d+)", line.strip())
        if m:
            out.setdefault(m.group(1), set()).add(int(m.group(2)))
    return out


def simanim_sur_disque():
    out = {}
    for sec in SECTIONS:
        d = ROOT / "sources" / sec
        if not d.is_dir():
            continue
        for p in d.iterdir():
            m = re.fullmatch(r"siman-(\d+)", p.name)
            if m and p.is_dir():
                out.setdefault(sec, set()).add(int(m.group(1)))
    return out


def catalogue():
    """{répertoire: {numéro, …}} — indexé par le CHEMIN réel, car la clé
    « section » du catalogue (oh-quotidien, nida) ne correspond pas au nom du
    répertoire (orah-haim, yoreh-deah)."""
    p = ROOT / "data" / "simanim-disponibles.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for s in d["simanim"]:
        m = re.match(r"sources/([a-z-]+)/siman-(\d+)/", str(s.get("path", "")))
        if m:
            out.setdefault(m.group(1), set()).add(int(m.group(2)))
    return out


def main():
    ref = "origin/main"
    if "--ref" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1]
    autoriser = "--autoriser-suppressions" in sys.argv

    erreurs, avertissements = [], []
    publie, disque, cat = simanim_dans(ref), simanim_sur_disque(), catalogue()

    if not publie:
        avertissements.append(
            f"référence « {ref} » introuvable ou vide — comparaison impossible "
            "(git fetch origin main ?)")

    print(f"=== Intégrité — état local vs {ref} ===\n")
    for sec in SECTIONS:
        pub, dis, ca = publie.get(sec, set()), disque.get(sec, set()), cat.get(sec, set())
        perdus = sorted(pub - dis)
        hors_cat = sorted(dis - ca)
        fantomes = sorted(ca - dis)
        etat = "OK" if not (perdus or hors_cat or fantomes) else "✗"
        print(f"  {etat}  {sec:<12} disque {len(dis):>3} · catalogue {len(ca):>3} · {ref} {len(pub):>3}")
        if perdus:
            (avertissements if autoriser else erreurs).append(
                f"{sec} : {len(perdus)} siman(im) présents dans {ref} et ABSENTS du disque "
                f"→ {perdus[:12]}{' …' if len(perdus) > 12 else ''}")
        if hors_cat:
            erreurs.append(f"{sec} : {len(hors_cat)} siman(im) sur disque mais absents du "
                           f"catalogue → {hors_cat[:12]}")
        if fantomes:
            erreurs.append(f"{sec} : {len(fantomes)} entrée(s) de catalogue sans répertoire "
                           f"→ {fantomes[:12]}")

    # correctifs mécaniques : doivent rester appliqués
    for nom, script in (("JSON-LD des pages -he/-en", "fix-jsonld-lang.py"),
                        ("numéraux hébreux des renvois", "heb-nums.py")):
        p = ROOT / "scripts" / script
        if not p.exists():
            continue
        r = subprocess.run([sys.executable, str(p)], capture_output=True,
                           text=True, cwd=str(ROOT))
        m = re.search(r"(\d+) fichiers", r.stdout)
        if m and int(m.group(1)) > 0:
            erreurs.append(f"{nom} : {m.group(1)} fichiers à recorriger — "
                           f"le correctif a été annulé (relancer {script} --apply)")

    print()
    for a in avertissements:
        print(f"  ⚠  {a}")
    for e in erreurs:
        print(f"  ✗  {e}")
    if erreurs:
        print(f"\n❌ NE PAS POUSSER. {len(erreurs)} régression(s) détectée(s).")
        print("   Fusionner origin/main puis restaurer ce qui manque, ou relancer")
        print("   avec --autoriser-suppressions si la suppression est voulue.")
        return 1
    print("\n✅ Aucune régression : l'état local ne détruit rien de ce qui est publié.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
