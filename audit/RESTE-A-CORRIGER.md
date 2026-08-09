# Ce qui reste à corriger

*Généré le 2026-08-09 par `scripts/reste-a-corriger.py` — ne pas éditer à la main.*

Chaque chiffre est relu depuis sa source à l'exécution : les pages du site, le classeur du Rav, les gates. Un inventaire tenu à la main devient faux dès la première correction appliquée, et un inventaire faux est pire que pas d'inventaire — il donne l'impression qu'on sait où l'on en est.

## Ce que ce fichier ne dit pas

Il inventorie ce que les instruments savent voir. Le siman 273 avait **quatre gates verts et neuf erreurs de fond** — « même maison = même lieu », la souka généralisée, le kazaït absent. Aucun compteur ci-dessous ne les aurait montrées. Cet inventaire borne le travail mécanique ; il ne borne pas l'état du contenu halakhique.

Quatre simanim sur 174 ont été relus au fond — 271, 272, 273, 274. Les autres ne l'ont jamais été.

## 1. Séifim non traduits — 167

L'hébreu est reproduit, et la traduction renvoie ailleurs (« Voir l'analyse pratique : ce seif traite de… ») au lieu de rendre le texte. Le lecteur francophone a le texte hébreu et rien d'autre.

| Siman | Séifim |
|---|---|
| 308 | 45 |
| 303 | 24 |
| 307 | 20 |
| 305 | 19 |
| 318 | 16 |
| 319 | 15 |
| 321 | 15 |
| 306 | 13 |

**Méthode établie** : vérifier l'alignement bloc↔séif avant d'écrire (`verifier-alignement.py`), traduire depuis l'hébreu de la page, recouper contre la traduction anglaise de Sefaria quand elle existe, vérifier qu'il ne reste aucun renvoi.

## 2. Classeur du Rav — 0 entrées non closes

Déjà confrontées à la page : **87** — dont 48 appliqué, 39 déjà-juste (registre : `audit/classeur-traite.txt`).

| Décision | Nombre |
|---|---|

⚠️ **Le classeur a été bâti sur la sortie du moteur d'audit, dont les artefacts s'y sont propagés.** Le moteur rattache une citation au daf le plus proche dans la page, même quand ce daf appartient à une autre proposition — et c'est ce daf que le classeur reproche. Sur les 50 premières entrées vérifiées, **10 décrivaient un défaut réel**. Ne jamais appliquer sans avoir lu la ligne de la page.

## 3. Points renvoyés à l'arbitrage du Rav

*Aucun point en attente.*

## 4. Non tranchés faute de localisation sûre

*Aucune entrée actuellement marquée `NON-TRANCHÉ` dans le registre.*

## 5. Traductions courtes à échantillonner — 238 blocs

Signalées par le décile inférieur de la distribution du site. **Ce ne sont pas des erreurs** : la dernière fois qu'une liste de ce type a été échantillonnée, les quatre blocs tirés étaient corrects et le défaut venait de l'instrument. À échantillonner avant d'en conclure quoi que ce soit.

## 6. Signalements de citations

`verifier-citations.py` continuera d'afficher les mêmes signalements : **ce sont des artefacts d'appariement**, pas des erreurs de page. Sur 58 triés un par un, **4 étaient réels** et sont corrigés. Trois pages accusées **disaient déjà juste** — dont une qui portait déjà une note signalant que la citation avait été faussement attribuée, note que le moteur a relue comme la citation elle-même.

## Gates

```
Hilkhot Shabbat     : 124/124 conformes
Yoreh De'ah         : 50/50 conformes
Simanim audités     : 174
Avec erreur(s)      : 0
Avec avertissement  : 0
Conformes           : 174
```

