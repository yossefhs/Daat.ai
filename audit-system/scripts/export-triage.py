#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère un fichier de tri rapide, autonome et hors ligne.

Pourquoi un fichier plutôt que l'interface `/admin`
----------------------------------------------------
L'API d'audit tourne sur ``127.0.0.1`` dans un conteneur : personne d'autre ne
peut l'atteindre. Le tri doit donc voyager. Ce script produit **une page HTML
sans aucune ressource externe** : elle s'ouvre d'un double-clic, fonctionne
sans réseau, et rend à la fin une ligne compacte de décisions à recoller.

Ce que la page montre, et ce qu'elle se garde de dire
------------------------------------------------------
Elle affiche **la citation et la source côte à côte**, pour que le lecteur
tranche sur le texte et non sur le verdict de l'outil. Le verdict est indiqué
en petit, comme une indication. Rien n'est pré-coché : un tri rapide ne doit
pas devenir un tri automatique.

Ordre de présentation : gravité, puis confiance décroissante. Les signalements
les plus susceptibles d'être réels viennent en premier, de sorte qu'on puisse
s'arrêter à tout moment sans avoir perdu son temps.

    python3 scripts/export-triage.py --out /tmp/triage.html [--limit 40]
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy import select                                    # noqa: E402

from daat_audit.config import get_settings                       # noqa: E402
from daat_audit.db import make_engine, make_session_factory      # noqa: E402
from daat_audit.models import AuditFinding, FindingStatus, Page  # noqa: E402

# Réponses proposées. Le libellé dit ce que le lecteur constate, pas ce que
# l'outil doit faire : la traduction en transition du workflow se fait à
# l'import (scripts/import-triage.py).
# Les cinq catégories distinguent ce que l'outil confondait : une erreur dans
# le texte, une référence mal rattachée, une variante d'édition, et ce qui
# n'était pas une citation. Les mélanger — comme le faisait la première
# version — revenait à présenter 123 artefacts comme 123 erreurs de Torah.
REPONSES = [
    ("1", "contenu",   "Erreur dans le contenu — le texte est fautif",   "#9B2C2C"),
    ("2", "reference", "Référence erronée ou mal rattachée",             "#B7791F"),
    ("3", "variante",  "Variante d'édition ou d'orthographe",            "#2C5282"),
    ("4", "pas_citation", "Paraphrase ou titre — ce n'est pas une citation", "#276749"),
    ("5", "rav",       "À soumettre au Rav",                             "#1A1F3A"),
]

_GRAVITE = {"P0_CRITICAL": 0, "P1_MAJOR": 1, "P2_SIGNIFICANT": 2,
            "P3_MINOR": 3, "P4_SUGGESTION": 4}


def collecter(session, limit: int | None, rule: str) -> list[dict]:
    lignes = session.execute(
        select(AuditFinding, Page)
        .join(Page, AuditFinding.page_id == Page.id)
        .where(AuditFinding.rule_code == rule,
               AuditFinding.status == FindingStatus.NEW)
    ).all()

    items = [
        {
            "id": f.id,
            "siman": p.siman,
            "niveau": p.niveau,
            "url": p.url,
            "regle": f.rule_code,
            "verdict": f.subcategory or "",
            "gravite": f.severity.value,
            "confiance": round(f.confidence or 0, 2),
            "citation": f.current_text or "",
            "source": (f.source_text or "")[:1200],
            "ref": f.sources or "",
            "explication": f.explanation or "",
        }
        for f, p in lignes
    ]
    items.sort(key=lambda i: (_GRAVITE.get(i["gravite"], 9), -i["confiance"]))
    return items[:limit] if limit else items


GABARIT = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DAAT — Tri rapide des signalements</title>
<style>
:root{--navy:#1A1F3A;--or:#C5A55A;--creme:#FAF6EE;--gris:#6B7280}
*{box-sizing:border-box}
body{margin:0;background:var(--creme);color:var(--navy);
 font:16px/1.6 "Cormorant Garamond",Georgia,serif;padding:0 0 90px}
header{background:var(--navy);color:var(--creme);padding:12px 20px;
 position:sticky;top:0;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
header b{color:var(--or)}
#barre{height:4px;background:var(--or);width:0;transition:width .2s}
main{max-width:1000px;margin:0 auto;padding:20px}
.meta{color:var(--gris);font-size:13.5px;margin-bottom:10px}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0}
@media(max-width:760px){.cmp{grid-template-columns:1fr}}
.pan{background:#fff;border:1px solid #e3dcc9;border-radius:6px;padding:12px 14px;
 max-height:46vh;overflow-y:auto}
.pan h3{margin:0 0 8px;font:600 11.5px/1 system-ui,sans-serif;letter-spacing:.09em;
 text-transform:uppercase;color:var(--gris)}
.he{direction:rtl;text-align:right;font-family:"Frank Ruhl Libre","Times New Roman",serif;
 font-size:19px;line-height:2}
.expl{background:#fdf8ec;border:1px solid #e8d9ae;border-radius:5px;padding:11px 15px;
 font-size:15px;color:#7a5c1e;margin:4px 0 14px}
.cit{unicode-bidi:isolate;direction:ltr;white-space:nowrap}
#reps{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #e3dcc9;
 display:flex;gap:8px;padding:10px 14px;flex-wrap:wrap;justify-content:center}
#reps button{font:15px/1.2 inherit;padding:9px 14px;border-radius:6px;border:1px solid;
 background:#fff;cursor:pointer;display:flex;gap:8px;align-items:center}
#reps kbd{background:var(--navy);color:#fff;border-radius:4px;padding:1px 7px;font:600 12px system-ui}
#fin{display:none;padding:26px;max-width:1000px;margin:0 auto}
textarea{width:100%;height:150px;font:13px ui-monospace,Menlo,monospace;padding:10px}
button.sec{background:var(--navy);color:#fff;border:none;padding:10px 16px;border-radius:6px;
 cursor:pointer;font:15px inherit}
a{color:var(--navy)}
</style></head><body>
<header>
  <b>DAAT</b> · Tri rapide
  <span id="pos"></span>
  <span style="flex:1"></span>
  <label style="font-size:13.5px">Je réponds en tant que
    <select id="role" style="font:inherit"><option value="rav">Rav</option>
    <option value="editor">éditeur</option></select></label>
  <button class="sec" onclick="retour()" style="padding:5px 11px;font-size:13.5px">↩ Annuler (Retour arrière)</button>
</header>
<div id="barre"></div>

<main id="carte"></main>
<div id="reps"></div>

<div id="fin">
  <h2>Terminé — <span id="compte"></span></h2>
  <p>Copiez ce bloc et collez-le-moi dans la conversation. Je l'applique au
     workflow : chaque décision sera tracée, et réversible.</p>
  <textarea id="sortie" readonly></textarea>
  <p><button class="sec" onclick="copier()">Copier</button>
     <span id="copie" style="color:#276749"></span></p>
</div>

<script>
const ITEMS = __DONNEES__;
const REPS  = __REPONSES__;
let i = 0; const choix = {};

const esc = s => (s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const HEB = "\\u0590-\\u05FF";
const mixte = s => esc(s)
  .replace(new RegExp(`«\\\\s*([^«»]*[${HEB}][^«»]*?)\\\\s*»`,"g"),
    (_,x)=>`<span class="cit">«&nbsp;<bdi dir="rtl">${x}</bdi>&nbsp;»</span>`)
  .replace(new RegExp(`(?![^<]*>)[${HEB}][${HEB}\\\\s'׳״-]*`,"g"),m=>`<bdi dir="rtl">${m}</bdi>`);

document.getElementById("reps").innerHTML = REPS.map(([k,code,txt,col])=>
  `<button style="border-color:${col};color:${col}" onclick="repondre('${code}')">
     <kbd>${k}</kbd> ${esc(txt)}</button>`).join("");

function afficher(){
  if(i>=ITEMS.length) return terminer();
  const it = ITEMS[i];
  document.getElementById("pos").textContent = `${i+1} / ${ITEMS.length}`;
  document.getElementById("barre").style.width = (100*i/ITEMS.length)+"%";
  document.getElementById("carte").innerHTML = `
    <div class="meta">Siman <b>${it.siman}</b> · niveau ${esc(it.niveau)} ·
      <a href="${esc(it.url)}" target="_blank">voir la page</a>
      · ${esc(it.gravite)} · confiance ${Math.round(it.confiance*100)} %</div>
    <div class="expl">${mixte(it.explication)}</div>
    <div class="cmp">
      <div class="pan"><h3>Texte de la page</h3><div class="he">${esc(it.citation)}</div></div>
      <div class="pan"><h3>Source — ${esc(it.ref)}</h3>
        <div class="he">${esc(it.source) || "<em>non consultée</em>"}</div></div>
    </div>
    <p class="meta">Comparez les deux colonnes vous-même : ce que dit l'outil
       est une indication, pas une preuve.</p>`;
  window.scrollTo(0,0);
}
function repondre(code){ choix[ITEMS[i].id]=code; i++; afficher(); }
function retour(){ if(i>0){ i--; delete choix[ITEMS[i].id]; afficher(); } }
function terminer(){
  document.getElementById("carte").style.display="none";
  document.getElementById("reps").style.display="none";
  document.getElementById("barre").style.width="100%";
  document.getElementById("fin").style.display="block";
  const n=Object.keys(choix).length;
  document.getElementById("compte").textContent = `${n} décision(s)`;
  const role=document.getElementById("role").value;
  document.getElementById("sortie").value =
    "DAAT-TRIAGE v1 role="+role+"\\n"+
    Object.entries(choix).map(([id,c])=>`${id} ${c}`).join("\\n");
}
function copier(){
  const t=document.getElementById("sortie"); t.select();
  document.execCommand("copy");
  document.getElementById("copie").textContent="✓ copié";
}
document.addEventListener("keydown", e=>{
  if(e.key==="Backspace"){ e.preventDefault(); return retour(); }
  const r=REPS.find(x=>x[0]===e.key);
  if(r) repondre(r[1]);
});
afficher();
</script></body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--rule", default="CIT-001")
    args = ap.parse_args()

    settings = get_settings()
    with make_session_factory(make_engine(settings))() as session:
        items = collecter(session, args.limit, args.rule)

    if not items:
        print("Aucun signalement en attente.", file=sys.stderr)
        return 1

    page = (GABARIT
            .replace("__DONNEES__", json.dumps(items, ensure_ascii=False))
            .replace("__REPONSES__", json.dumps(REPONSES, ensure_ascii=False)))
    args.out.write_text(page, encoding="utf-8")
    print(f"{len(items)} signalement(s) → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
