#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère les CSV squelettes + pages-non-verifiees.csv à partir de l'inventaire. Lecture seule (écrit dans audit/)."""
import csv
from pathlib import Path
from collections import Counter
AUDIT=Path(__file__).resolve().parents[1]

inv=list(csv.DictReader(open(AUDIT/'inventaire-pages.csv',encoding='utf-8')))

# Pages ayant reçu une revue sémantique approfondie (agents) :
DEEP={'261','263','293'}
non_verif=[]
for r in inv:
    sec=r['Section']; sim=r['Siman']
    if sec in ('shabbat','orah-haim','yoreh-deah','nida','limoud','blog'):
        deep = (sec=='shabbat' and sim in DEEP)
        if not deep:
            non_verif.append({
                'URL':r['URL'],'Fichier':r['Fichier_source'],'Section':sec,'Siman':sim,
                'Niveau':r['Niveau'],'Langue':r['Langue'],
                'Controles_faits':'automatiques (inventaire, SEO, liens, hreflang, numerotation-titre, chronologie-regex)',
                'Revue_semantique':'NON — halakha/traduction/niveaux non vérifiés en profondeur',
                'Raison':'Volume : revue sémantique manuelle/rabbinique requise'})

with open(AUDIT/'pages-non-verifiees.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['URL','Fichier','Section','Siman','Niveau','Langue','Controles_faits','Revue_semantique','Raison'])
    w.writeheader()
    for r in non_verif: w.writerow(r)

# CSV halakha / traduction / divergences : en-têtes (remplis par la revue sémantique)
hal_cols=['ID','URL','Fichier','Ligne','Langue','Siman','Seif','Niveau','Texte_actuel','Probleme','Source_primaire','Correction_proposee','Certitude','Validation_Rav']
trad_cols=['ID','URL','Fichier','Langue','Siman','Seif','Niveau','Element','Texte_actuel','Probleme','Correction_proposee','Certitude','Validation_Rav']
div_cols=['URL_FR','URL_HE','URL_EN','Siman','Seif','Element','Texte_FR','Texte_HE','Texte_EN','Type_divergence','Gravite','Correction_proposee','A_valider_par_le_Rav']
for name,cols in [('erreurs-halakha.csv',hal_cols),('erreurs-traduction.csv',trad_cols),('divergences-langues.csv',div_cols)]:
    p=AUDIT/name
    if not p.exists():
        with open(p,'w',newline='',encoding='utf-8') as f:
            csv.writer(f).writerow(cols)

print("pages-non-verifiees.csv :",len(non_verif),"lignes")
print("Répartition sections non vérifiées sémantiquement :",dict(Counter(r['Section'] for r in non_verif)))
