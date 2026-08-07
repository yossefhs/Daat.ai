# Ce qui reste à corriger

*Généré le 2026-08-07 par `scripts/reste-a-corriger.py` — ne pas éditer à la main.*

Chaque chiffre est relu depuis sa source à l'exécution : les pages du site, le classeur du Rav, les gates. Un inventaire tenu à la main devient faux dès la première correction appliquée, et un inventaire faux est pire que pas d'inventaire — il donne l'impression qu'on sait où l'on en est.

## Ce que ce fichier ne dit pas

Il inventorie ce que les instruments savent voir. Le siman 273 avait **quatre gates verts et neuf erreurs de fond** — « même maison = même lieu », la souka généralisée, le kazaït absent. Aucun compteur ci-dessous ne les aurait montrées. Cet inventaire borne le travail mécanique ; il ne borne pas l'état du contenu halakhique.

Quatre simanim sur 174 ont été relus au fond — 271, 272, 273, 274. Les autres ne l'ont jamais été.

## 1. Séifim non traduits — 226

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
| 320 | 12 |
| 315 | 11 |
| 314 | 10 |
| 316 | 10 |
| 312 | 8 |
| 313 | 8 |

**Méthode établie** : vérifier l'alignement bloc↔séif avant d'écrire (`verifier-alignement.py`), traduire depuis l'hébreu de la page, recouper contre la traduction anglaise de Sefaria quand elle existe, vérifier qu'il ne reste aucun renvoi.

## 2. Classeur du Rav — 40 entrées non closes

Déjà confrontées à la page : **47** — dont 26 déjà-juste, 16 appliqué, 5 non-tranché (registre : `audit/classeur-traite.txt`).

| Décision | Nombre |
|---|---|
| À CORRIGER | 17 |
| À PRÉCISER | 14 |
| PARAPHRASE VALABLE | 8 |
| À CORRIGER IMMÉDIATEMENT | 1 |

⚠️ **Le classeur a été bâti sur la sortie du moteur d'audit, dont les artefacts s'y sont propagés.** Le moteur rattache une citation au daf le plus proche dans la page, même quand ce daf appartient à une autre proposition — et c'est ce daf que le classeur reproche. Sur les 50 premières entrées vérifiées, **10 décrivaient un défaut réel**. Ne jamais appliquer sans avoir lu la ligne de la page.

Simanim les plus concernés : 296 (4), 295 (3), 6 (2), 246 (2), 280 (2), 286 (2), 338 (2), 198 (2), 22 (1), 61 (1)

## 3. Points renvoyés à l'arbitrage du Rav

Marqués « À vérifier par le Rav » directement dans les pages :

- **shabbat/siman-273** — … s'ils ne savent pas faire le kiddush eux-mêmes — « אין לו לקדש לאחרים לכתחלה אלא אם כן הם אינם יודעים » (SAR 273:6). La marge en cas de nécessité : à
- **shabbat/siman-274** — …elle du dessus — jour de Shabbat et nuit de Yom Tov — et, le vendredi soir, de disposer les pains de sorte que celle du dessous soit la plus proche. À
- **shabbat/siman-274** — …ajouté ne fait pas un lehem michné — lehem michné veut dire deux pains entiers ; et l'on ne coupera pas le pain entier en deux pour en simuler deux. À
- **shabbat/siman-274** — …ins entiers prêts à être consommés pour chaque repas. En cas d'oubli ou de nécessité, il existe des avis permettant d'y associer une halla congelée. À

## 4. Non tranchés faute de localisation sûre

La page y **paraphrase au lieu de citer**, de sorte que la comparaison littérale ne départage pas les dafim proposés. Deviner reviendrait à remplacer un daf incertain par un autre.

| Endroit | Question |
|---|---|
| shabbat/252 | `נותנין חטין לתוך הריחים של מים` donné à או״ח רנ״ב:ה — n'y figure pas verbatim ; Sefaria le situe en שבת י״ח. |
| shabbat/284:354 | מגילה כ״ג. ou כ״ג: pour les 21 versets de la haftara |
| shabbat/287:413 | מועד קטן כ״ג: ou כ״ד. pour l'avelout à Chabbat |
| shabbat/288:456 | תענית י״ד. ou י״ט. pour « על אלו צרות מתריעין » |
| orah-haim/37 | `קרקפתא דלא מנח תפילין` absent du ראש השנה י״ז. de Sefaria, alors que les éditions courantes l'y portent — divergence de découpage probable |
| orah-haim/66 | `אינו ניזוק כל היום כולו` est la formulation du Yerushalmi ; citation composite portant des guillemets |

## 5. Traductions courtes à échantillonner — 169 blocs

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

