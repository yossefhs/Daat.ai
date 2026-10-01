# Le trou de l'exemption « résumé » — étendue mesurée, hypothèses éprouvées, tri à la main

Relevé de mesure. **Aucune page de `sources/` n'a été modifiée, aucun commit, aucun `git add`.**
`verifier-citations.py` n'a pas été lancé (un balayage occupe `scripts/.cache-sefaria`) ; toutes les
confrontations ci-dessous viennent d'interrogations directes de `www.sefaria.org/api/texts`, mises en
cache dans le scratchpad de la séance.

Date : 1er octobre 2026.

---

## 0. Ce que ce relevé établit en une phrase

Le trou n'est pas théorique, il est peuplé, et il est **vingt fois plus large que l'estimation de 328**.
Sur **8 386 occurrences** du marqueur de condensation (6 357 textes distincts), un seul sous-ensemble
a été confronté séif par séif — les **165 cellules de tableau qui portent leur propre adresse** — et il
a rendu **11 condensations fausses sur 15 examinées à la main**, dont une inversion de chiffre
(`שליש בישול` contre `חצי בישולו` au séif cité), une attribution croisée Mehaber/Rama, et deux
formulations hébraïques **vocalisées** qui n'existent dans aucune des deux sources citées.

Les deux hypothèses demandées ne se valent pas : la **polarité** est inexploitable à l'échelle du site
et exploitable, faiblement, sur les cellules adressées ; la **condition** rend un peu plus. Une
troisième, trouvée en mesurant, les dépasse toutes les deux : **l'hébreu vocalisé dans une condensation
qui cite une source non vocalisée**.

---

## a) L'étendue réelle

### Le compte brut

Motif compté : `<em>résumé</em> :`, `<em>תמצית</em> :`, `<em>summary</em> :` (les deux espacements, avec
et sans espace avant le deux-points — l'un des deux seul en aurait manqué 1 127).

```
$ grep -c ... (script scratchpad/count.py, count2.py, extract2.py sur sources/)
TOTAL occurrences : 8 386   dans 860 fichiers
```

| | occurrences |
|---|---|
| **par compartiment** | orah-haim **6 563** · yoreh-deah **1 539** · shabbat **284** |
| **par niveau** | niveau-1-base **4 436** · niveau-2-lamdan **3 347** · niveau-4 **426** (daat-harav 379 + halakha 47) · niveau-3-synthese **123** · index **54** |
| **par langue de page** | fr **2 823** · en **2 805** · he **2 758** |
| **par forme du marqueur** | `תמצית` **4 796** · `résumé` **1 800** · `summary` **1 790** |

Croisement forme × langue, qui ne va pas de soi :

```
תמצית  dans un fichier he : 2 758   dans un fichier fr : 1 025   dans un fichier en : 1 013
résumé dans un fichier fr : 1 798   (2 égarés dans un fichier -en)
summary dans un fichier en: 1 790
```

Une page française porte donc **deux** marqueurs : son `résumé` français et un `תמצית` qui introduit
une condensation **en hébreu**. Ce n'est pas un défaut de langue — c'est la convention du dépôt — mais
cela explique pourquoi le compte par langue (2 823 / 2 805 / 2 758) est presque équilibré alors que
`תמצית` domine le compte par forme.

### Les deux unités, et pourquoi il faut les deux

- **Occurrences : 8 386.** C'est le nombre de lecteurs concernés : une même condensation vit dans trois
  fichiers, et un défaut y est trois lecteurs trompés.
- **Textes distincts (normalisés, balises et diacritiques retirés) : 6 357.** C'est le travail réel.
  Par langue du texte : hébreu **2 768**, français **1 799**, anglais **1 790**.
  **1 018** de ces textes se retrouvent dans plus d'un fichier-langue : ce sont les condensations
  hébraïques servies aussi au lecteur français et anglais.

Le rapport 8 386 / 6 357 n'est pas 3 : la parité n'est pas celle qu'on croit, parce que l'hébreu n'est
pas traduit mais recopié.

### Le marqueur fait **trois métiers différents**, et c'est le fait structurant

Le conteneur le plus serré a été relevé par pile de balises (un premier essai, qui prenait la dernière
balise ouvrante, attribuait 4 510 occurrences à des `<span>` et était faux) :

| famille de conteneur | occurrences | ce que le marqueur y introduit |
|---|---|---|
| encadré pédagogique (`key-point`, `remember`, `definition`) | **3 198** | le **ta'am**, la raison — pas une condensation de la source |
| appareil lamdan (`machloket-box`, `teruts-box`, `rishon-card`, `pilpul-box`, `hakira-box`, `nafka-mina-box`, `yesod-box`, `kashya-box`…) | **2 709** | la condensation d'une entrée de Taz / Chakh / Michna Beroura |
| **rendu du texte source** (`translation`, `sacred-text`, `sa-fr`) | **1 500** | la **suite du séif**, dans le flux même de la traduction |
| `<li>` | 357 | listes |
| `<p>` nu | 312 | prose |
| **cellule de tableau** (`<td>`/`<th>`) | **272** | la condensation d'une source **nommée par une adresse** |
| divers (`concept-desc`, `schema-step`, `blockquote`) | 38 | |

Trois conséquences :

1. **Les 3 198 encadrés pédagogiques ne sont pas des condensations au sens de la convention.**
   Au siman 180 niveau 1, séif 5 : « <em>תמצית</em> : la table est comparée à l'autel, et le fer, qui
   abrège la vie, n'a pas sa place découvert… ». Le séif ה du Mehaber ne dit **que**
   `נוהגים לכסות הסכין בשעת ברכת המזון ונהגו שלא לכסותו בשבת ויום טוב` — pas un mot de ce ta'am.
   Le ta'am est vrai : il est dans la **Michna Beroura ס״ק י״א**, d'après le Beit Yossef
   (`בב"י ב' טעמים האחד דברזל מקצר ימי האדם ואינו דין שיהיה מונח על השלחן שדומה למזבח`). Mais la page
   ne le dit pas, et le marqueur fait croire qu'elle condense le séif qu'elle vient de citer.
2. **La famille la plus dangereuse après les cellules est `div.translation` (1 500 occurrences)** : la
   condensation y est **dans le flux de la traduction du séif**, en `<strong>`, à la suite de
   « <strong>Séif 4 : … </strong> ». Le lecteur croit lire le séif. Cas mesuré en (c), item 3.
3. **Les cellules de tableau sont la seule famille mécaniquement confrontable**, parce qu'elle est la
   seule à porter une adresse.

### Le chiffre de 328 : à jeter

Aucune définition naturelle ne le reproduit. Mesures voisines :

| définition | mesuré |
|---|---|
| condensations en cellule de tableau (`<td>`/`<th>`), 3 langues | **272** occurrences · **268** textes distincts |
| condensations au niveau 4, toutes familles, 3 langues | **426** |
| condensations au niveau 4 **en cellule** | **200** |
| condensations au niveau 4, français seul | **118** |
| **toutes familles, tout le site** | **8 386** |

Donc : **328 surestime d'environ 20 % la famille des cellules de niveau 4** (272 mesurées) et
**sous-estime le phénomène d'un facteur 25** (8 386). Les 8 386 et les 6 357 **ne sont pas des
planchers** : le motif est exhaustif sur `sources/*/siman-*/*.html`, les deux espacements couverts.
Est en revanche **un plancher** tout dénombrement de *défauts* ci-dessous : seules 165 cellules sur
8 386 occurrences ont été confrontées à la source.

---

## b) Ce qui est mécaniquement confrontable — deux hypothèses éprouvées, une troisième trouvée

### Hypothèse 1 — LA POLARITÉ : **inexploitable au niveau 1, faible sur les cellules**

Marqueurs relevés de part et d'autre : source `מותר/מתר/שרי` contre `אסור` (frontières de mot
hébraïques des deux côtés, pour ne pas lire `מותר` dans un mot plus long) ; condensation, les mêmes
plus `permis/autorisé/licite` contre `interdit/défendu/prohibé`, et `permitted/allowed` contre
`forbidden/prohibited/may not`.

**Premier essai, sur le niveau 1 (3 873 condensations rattachées à un séif par l'ancre la plus proche) :**

```
total confrontable                      3873
condensation monopolaire                 667
  dont source AUSSI monopolaire          178     ← 4,6 % seulement
  dont source bipolaire ou muette        489
condensation bipolaire                   437
condensation sans polarité nette        2769
POLARITÉ DIVERGENTE                       80
```

**Dix des 80 tirés au sort et lus à la main : zéro défaut réel.** La cause est diagnostiquée et elle
condamne l'échelle, pas seulement le réglage : **le rattachement est faux**. En Yoré Déa, les
condensations du niveau 1 vivent dans des `div.translation` qui traduisent le **Taz et le Chakh**, dont
l'adresse est un ס״ק et non un séif ; l'ancre textuelle « Séif N » la plus proche les rattache à un séif
qui ne les porte pas. Exemple : Yoré Déa 159, une condensation qui expose la sougya du séif א est
rattachée au séif ג, dont le texte traite des Karaïtes.

Et le plafond est structurel : **un séif du Choul'han Aroukh statue presque toujours sur plusieurs cas,
donc porte `מותר` ET `אסור`**. 489 sources bipolaires ou muettes contre 178 monopolaires. La polarité ne
peut donc rien dire sur 95 % des couples.

**Second essai, sur les 165 cellules qui portent leur propre adresse** (plus d'erreur de rattachement) :

```
confrontable                            165
condensation monopolaire                 44
  dont source AUSSI monopolaire           30
POLARITÉ DIVERGENTE                        5
```

**Les 5 lus à la main : 1 défaut réel, 4 bruits.** Le réel est Chabbat 244 (item 7 ci-dessous) et c'est
une vraie inversion. Les bruits sont instructifs : « le négoce (פרקמטיא) **n'est pas compris dans
l'interdit** » contre `ופרקמטיא שרי` — même psak, polarité lexicale opposée, parce qu'une négation
d'interdit est un permis.

**Verdict : la polarité n'est pas une porte.** Rendement 1/5 sur le seul périmètre où elle a un sens,
et 0/10 ailleurs. Elle peut servir de **signal d'appoint sur les cellules adressées**, jamais de
contrôle bloquant.

### Hypothèse 2 — LA CONDITION : **exploitable, faiblement, sur les cellules seules**

Règle éprouvée : la condensation pose une condition (`si`, `s'il`, `à condition`, `seulement si`,
`dès lors que`, `if`, `only if`, `unless`, `אם`, `ובלבד`, `והוא ש`, `דוקא`, `אלא אם`) **et** le séif cité
contient une branche **négative** (`ואם לא`, `אם לא`, `ואי לא`, `אם אינו`, `אם אין`) **et** la
condensation ne porte aucune marque de négation. C'est la forme du défaut du siman 247.

Sur les 165 cellules adressées :

```
condensation conditionnelle               40
  dont source avec branche négative        15
CONDITION SANS BRANCHE NÉGATIVE            14
```

**Les 14 lus à la main : 4 occurrences réelles (2 cellules distinctes), 10 bruits.**
- Réel, Chabbat 243 (3 occurrences, 1 cellule) : item 6 ci-dessous.
- Réel, Chabbat 247, seconde cellule : item 9 — la citation s'arrête **juste avant**
  `והוא שיהא שהות ביום כדי שיוכל להגיע לבית`, qui est la condition restrictive de la branche qu'elle
  expose. C'est la « coupure avant la suite » de `verifier-troncatures.py`, mais dans une condensation,
  donc hors de sa portée.
- Bruit typique, Orah Haïm 12 (3 occurrences) : la condensation rend la branche `דקדק` de la glose du
  Rama, et la branche négative `אם לא דקדק` du Mehaber est un **autre cas**, non la même clause retournée.
  C'est exactement le faux positif que `ואם` produit déjà dans `verifier-troncatures.py`.

**Verdict : exploitable comme producteur de candidats, à 2 cellules réelles sur 7 distinctes
(≈ 29 %).** Ce rendement est du même ordre que celui qu'on accepte déjà de `verifier-ancrage.py`. À ne
jamais faire sortir en erreur.

### Hypothèse 3 — **L'HÉBREU VOCALISÉ DANS UNE CONDENSATION QUI CITE UNE SOURCE NON VOCALISÉE**

Trouvée en lisant les deux défauts réels, pas cherchée. Elle repose sur un fait de la source, non sur
une heuristique de langue : **Sefaria sert le Choul'han Aroukh du Mehaber, le Rama et la Michna Beroura
SANS nikoud, et le Choul'han Aroukh HaRav AVEC.** Donc une condensation **vocalisée** dans une colonne
« Mehaber » ou « Rama » n'a pu être recopiée de nulle part : elle a été **composée**. Elle n'est pas
pour autant fautive — la convention autorise une condensation en hébreu — mais elle a l'**apparence
d'une citation** sans en porter la charge, et le test est quasi gratuit.

Mesure sur les 165 cellules adressées :

```
condensation sans hébreu vocalisé                                   122
condensation AVEC hébreu vocalisé                                    43
  ...et la source citée est vocalisée (Choul'han Aroukh HaRav) : normal     3
  ...alors que la source citée est NON vocalisée                     40
     squelette consonantique RETROUVÉ dans le séif cité               0
     squelette ABSENT du séif cité  → CANDIDAT                       40
```

**40 occurrences, 15 cellules distinctes (comptées en français). Les 15 ont été ouvertes une par une
contre Sefaria : 11 fausses, 3 fidèles, 1 en réserve.** Rendement **73 %** — la meilleure des trois,
d'un ordre de grandeur.

| cellule | colonne | verdict | preuve |
|---|---|---|---|
| OH 1:2 | Mehaber | **FAUSSE** | `ראוי לכל ירא שמים שיהא מיצר ודואג על חורבן בית המקדש` **est le séif 1:3** mot pour mot ; 1:2 traite des veilles de la nuit |
| OH 243:2 | **Rama** | **FAUSSE** | contenu = Mehaber du séif **א** (`ותנור דינו כמרחץ ורחיים דינו כשדה`) ; la glose du Rama sur 243:2 dit tout autre chose (`ואפילו במקום האסור… רק שכרם מעכו״ם`) |
| OH 244:1 | Mehaber | **FAUSSE** | `אין אומרים` **absent du siman 244 entier**, et du Choul'han Aroukh HaRav 244 (22 séifim) ; 244:1 énonce une **permission** |
| OH 246:1 | Rama | FIDÈLE | la glose du Rama sur 246:1 porte bien `ומותר להשאיל לו בערב שבת` |
| OH 246:3 | Mehaber | FIDÈLE | même psak, même raison (`שאדם מצווה על שביתת בהמתו`) ; phrasé emprunté à la Michna |
| OH 252:1 | Mehaber | **FAUSSE** | `פותקין מים לגינה` et `מוגמר תחת הכלים` sont au séif **252:5** (`ומותר לפתוח מים לגנה… ולתת מוגמר תחת הכלים`) |
| OH 252:5 | Mehaber | **RÉSERVE** | `משתרף` absent du siman 252 entier ; adresse non établie, à ouvrir |
| OH 252:6 | Mehaber | **FAUSSE** | `דיו וסממנים` est au séif **252:1** (`לשרות דיו וסממנין`) ; 252:6 traite de `לא יצא אדם במחטו` |
| OH 253:1 | Mehaber | FIDÈLE | `קטומה`, `גרופה` et `באפר` sont tous trois au séif 1 |
| OH 254:1 | Mehaber | **FAUSSE** | `מצטמק ויפה לו` **absent du siman 254 entier** ; c'est le séif **253:1** |
| **OH 254:2** | Mehaber | **FAUSSE, et contraire au séif cité** | la condensation définit `כמאכל בן דרוסאי` par `כל שיש בו שליש בישול` ; **le séif 254:2 écrit `כמאכל בן דרוסאי שהוא חצי בישולו`** |
| OH 255:1 | Mehaber | **FAUSSE** | `אין נותנין שום דבר על גבי הגחלים` absent de 255 (qui traite de `מדורה מעצים`) ; la règle des גחלים est **254:2**, autre siman, et sa condition est `כמאכל בן דרוסאי`, non `שהות ביום` |
| OH 255:2 | Mehaber | **FAUSSE** | 255:2 traite des `פחמין` ; `חטין לתוך הריחים` absent du siman |
| OH 261:1 | Mehaber | **FAUSSE (durcissement)** | « וכל אסורי שבת נוהגים בו » absent du siman ; 261:1 **énumère des permissions** — `מעשרין את הדמאי`, `טומנין את החמין`, `ומותר לומר לעכו״ם… להדליק` |
| OH 263:1 | Mehaber | **FAUSSE** | `נשים מוזהרות` est au séif **263:3** ; `אחד אנשים ואחד נשים` absent du siman ; 263:1 traite de `נר יפה` |

Deux remarques qui comptent plus que le tableau :

- **Ces 15 cellules passent toutes les portes existantes.** `verifier-citations.py` ne les juge pas :
  la convention les exempte du verbatim, et elles ne portent pas de guillemets.
  `verifier-etiquettes.py` les laisse passer parce qu'elle pose trois questions fermées — le séif
  existe-t-il, porte-t-il une glose du Rama quand on en promet une, le ס״ק existe-t-il — et la réponse
  est oui aux trois pour 243:2, 254:2, 261:1 et 263:1.
- **Le défaut est groupé : 11 des 15 cellules sont dans Chabbat 243-263.** C'est la même plage que les
  26 étiquettes fausses et que les troncatures. Ce n'est probablement pas une coïncidence mais une
  campagne de production.

**Verdict : c'est la porte à écrire.** 73 % de rendement, trois questions purement mécaniques (y a-t-il
du nikoud · la source citée est-elle vocalisée · le squelette consonantique est-il dans le séif cité),
et un faux positif explicable (une condensation hébraïque légitime, cas 246:1 et 253:1).

---

## c) Le tri à la main — 14 condensations, trois compartiments

Chacune a été confrontée à la source Sefaria interrogée pour elle. Verdicts : **FIDÈLE** (la
condensation dit ce que dit la source citée) · **IMPRÉCISE** (vraie mais incomplète, affaiblie, ou sans
l'adresse qui la porte) · **FAUSSE** (la source citée ne dit pas cela).

| # | page | adresse annoncée | verdict | preuve |
|---|---|---|---|---|
| 1 | `sources/orah-haim/siman-1/niveau-4-daat-harav.html` | OH 1:2, colonne Mehaber | **FAUSSE** | le texte est le séif **1:3** verbatim ; `Shulchan_Arukh,_Orach_Chayim.1` séif 3 = `ראוי לכל ירא שמים שיהא מיצר ודואג על חורבן בית המקדש` |
| 2 | `sources/orah-haim/siman-12/niveau-4-daat-harav.html` | Hagaha sur OH 12:1 | **FIDÈLE** | la glose du Rama sur 12:1 : `וכל שכן אם דקדק שיהיו ניכרין הד' ראשים שבצד אחד ונפסקו ג' ראשים בצד אחר דפסול… ואם נפסקו בב' צדדין נמי פסול` |
| 3 | `sources/orah-haim/siman-162/niveau-1-base.html` | Séif 4, dans `div.translation` | **IMPRÉCISE** | la source dit `צריך שישפוך לו אחר עליהם` — **il faut** ; la page écrit « il vaut donc mieux qu'un autre lui verse ». Et deux clauses du séif sont omises sans « … » : `צריך לנגב ידיו ולחזור וליטלה כראוי`, et tout le passage `אם נגע בהם אחר שלא נטל ידיו בעודן לחות` |
| 4 | `sources/orah-haim/siman-180/niveau-1-base.html` | Séif 3, `key-point` | **FIDÈLE** | `ועכשיו אין אנו נוהגים כך מפני שאין אנו מסלקין השלחן ואנו נוטלים הידים חוץ לשלחן` — rendu exactement |
| 5 | `sources/orah-haim/siman-180/niveau-1-base.html` | Séif 5, `key-point` | **IMPRÉCISE** | le ta'am (`שלחן דומה למזבח`, `ברזל מקצר ימי האדם`) n'est pas dans le séif ה, qui ne dit que `נוהגים לכסות הסכין… ונהגו שלא לכסותו בשבת ויום טוב`. Il est vrai et il est dans **Michna Beroura 180 ס״ק י״א** — que la page ne cite pas |
| 6 | `sources/shabbat/siman-243/niveau-4-daat-harav.html` | *Hagaha sur OH 243:2* | **FAUSSE** | double erreur. `ותנור דינו כמרחץ ורחיים דינו כשדה` est au séif **א**, et c'est le **Mehaber**, non le Rama. La glose du Rama sur 243:1 est `ואע״פ שלא לקחה העכו״ם רק לשליש או לרביע…`, celle sur 243:2 `ואפילו במקום האסור…`. Attribution croisée Mehaber/Rama + décalage de séif — la signature même que cherche `veilleur.py` |
| 7 | `sources/shabbat/siman-244/niveau-4-daat-harav.html` | OH 244:1, colonne Mehaber | **FAUSSE** | `אין אומרים לעכו״ם לעשות לנו מלאכה בשבת`, donné en hébreu vocalisé, **n'existe ni dans SA OH 244 (6 séifim) ni dans SA HaRav OH 244 (22 séifim)**. Et la cellule écrit « énonce l'interdit » quand 244:1 énonce une **permission** : `פוסק אדם עם העכו״ם על המלאכה וקוצץ דמים והעכו״ם עושה לעצמו ואע״פ שהוא עושה בשבת מותר`, limitée par `בד״א בצנעא` |
| 8 | `sources/shabbat/siman-247/niveau-4-daat-harav.html` | OH 247:1, premier régime | **FIDÈLE** | 247:1 : `שולח אדם אגרת ביד עכו״ם ואפי' בע״ש עם חשיכה והוא שקוצץ לו דמים ובלבד שלא יאמר לו שילך בשבת` ; les conditions `בי דואר` et `שהות ביום` sont bien dans la branche `ואם לא קצב`. **Le défaut signalé dans le mandat n'est plus là : la cellule attache correctement le בי דואר au cas sans prix fixé.** |
| 9 | `sources/shabbat/siman-247/niveau-4-daat-harav.html` | OH 247:1, second régime | **IMPRÉCISE** | la citation s'arrête sur `ואי קביע בי דואר במתא משלחין אפי' בע״ש` — la source **poursuit** `והוא שיהא שהות ביום כדי שיוכל להגיע לבית` ; la condition qui restreint la permission exposée n'est pas donnée |
| 10 | `sources/shabbat/siman-254/niveau-4-daat-harav.html` | OH 254:2, colonne Mehaber | **FAUSSE** | la condensation : `כל שיש בו שליש בישול`. Le séif cité : `כמאכל בן דרוסאי שהוא **חצי** בישולו`. Un chiffre contre l'autre, au séif même qu'elle nomme — avec conséquence pratique sur le שיהוי |
| 11 | `sources/shabbat/siman-255/niveau-4-daat-harav.html` | OH 255:1, colonne Mehaber | **FAUSSE** | `אין נותנין שום דבר על גבי הגחלים… אא״כ יש שהות ביום שיוכלו להגחיל מבעוד יום` absent de 255, qui traite de `מדורה מעצים` et exige `שתהא השלהבת עולה מאליה`. La règle des braises est **OH 254:2**, et sa condition est `כמאכל בן דרוסאי` |
| 12 | `sources/shabbat/siman-261/niveau-4-daat-harav.html` | OH 261:1, colonne Mehaber | **FAUSSE** | « וכל אסורי שבת נוהגים בו » absent du siman ; 261:1 **énumère ce qui est permis** à בין השמשות : `מעשרין את הדמאי`, `טומנין את החמין`, `ומערבין עירובי חצרות`, `ומותר לומר לעכו״ם בין השמשות להדליק` |
| 13 | `sources/yoreh-deah/siman-131/niveau-1-base.html` | ט״ז יו״ד קל״א ס״ק א | **FIDÈLE** (réserve) | le Taz dit bien `ולא הבנתי זה דאדרבה בחצר מרתת טפי מבבית כיון שיש לו שייכות גם בבית` et `ויפה עשה רמ״א שלא זכר כאן בש״ע מחילוק זה`. Réserve : la condensation résume la distinction du Raavad sans sa clause opératoire `עד שיושיב שומר`, ce qui la rend inintelligible, et tait le `ובאמת צ״ע שם בר״ן` |
| 14 | `sources/yoreh-deah/siman-119/niveau-4-halakha.html` | ש״ך ס״ק כ״ד | **FIDÈLE** | `והדבר פשוט דלכל האיסורים אינו נאמן אלא דאינו עושה יין נסך כיון שהוא יהודי באמת` — rendu exactement |

**Bilan du tri : 6 FAUSSES · 3 IMPRÉCISES · 5 FIDÈLES.** Six sur quatorze.
Par compartiment : Orah Haïm 5 items (1 fausse, 2 imprécises, 2 fidèles) · Chabbat 7 (5 fausses,
1 imprécise, 1 fidèle) · Yoré Déa 2 (2 fidèles).

**Le trou est peuplé, et il est peuplé inégalement** : les six fausses sont toutes des cellules de
niveau 4, cinq des six dans Chabbat 243-263. Les deux condensations de Yoré Déa examinées sont fidèles,
et les deux familles de l'appareil lamdan (Taz, Chakh) tiennent. Ce n'est pas un échantillon
suffisant pour acquitter Yoré Déa : **2 items sur 1 539 occurrences**.

### Observation hors mandat, notée parce qu'elle était sous la main

`sources/yoreh-deah/siman-119/niveau-4-halakha.html` attribue au **Taz ס״ק י״א** la raison complète,
dont la clause « tandis que ce qu'il dit devant un Juif est plausiblement vrai ». Le Taz ס״ק י״א ne
porte pas cette clause ; elle est dans le **Chakh ס״ק כ״ד** (`וכשאומר לנו שהוא ישראל אומר בלב שלם`).
C'est en prose, hors condensation, donc hors de ce lot — mais c'est la même famille de défaut.

---

## d) Ce que je n'ai pas fait

- **Je n'ai modifié aucune page** de `sources/`, ni aucun autre fichier du dépôt que celui-ci.
  Aucun commit, aucun `git add`. Les scripts de mesure sont dans le scratchpad de la séance.
- **Je n'ai pas lancé `verifier-citations.py`** (balayage en cours sur son cache), ni aucune autre
  porte du dépôt. Toutes les confrontations sont des appels directs à l'API Sefaria, cache séparé.
- **Je n'ai confronté que 165 des 8 386 occurrences** — les cellules qui portent leur propre adresse.
  Les 8 221 autres ne sont pas acquittées : elles sont **non mesurées**. En particulier :
  - les **1 500 condensations de `div.translation`**, la famille la plus dangereuse après les cellules,
    n'ont été confrontées **qu'une fois** (item 3, et elle était imprécise) ;
  - les **2 709 condensations de l'appareil lamdan** n'ont été confrontées que deux fois (items 13-14,
    les deux fidèles) ;
  - les **3 198 encadrés pédagogiques** ne sont pas confrontables en l'état : ils ne nomment pas leur
    source. C'est le constat le plus lourd de ce lot et il n'a pas de remède mécanique.
- **Les 107 cellules sans adresse lisible** (272 − 165) n'ont pas été traitées : 42 en Yoré Déa
  niveau 3, 16 + 16 dans les fichiers hébreux de niveau 4, 12 en Orah Haïm niveau 3, le reste épars.
  Mon motif d'adresse ne lit pas toutes les formes hébraïques — c'est une **limite de ma mesure**,
  pas une absence d'adresse dans la page.
- **Je n'ai pas vérifié la parité trilingue des condensations** cellule par cellule. Les écarts par
  niveau sont visibles (niveau-2-lamdan : fr 1 159 · en 1 155 · he 1 033 ; niveau-4-daat-harav :
  fr 103 · en 102 · **he 174**) mais je n'ai pas établi si ce sont des condensations manquantes,
  des condensations supplémentaires, ou un découpage différent.
- **Je n'ai pas écrit la porte** de l'hypothèse 3, ni aucun script dans `scripts/`.
- La cellule **OH 252:5** reste en réserve : `משתרף` est absent du siman 252 entier, mais je n'ai pas
  établi où vit la règle, donc je ne la compte pas comme fausse.
- Les **trois « FIDÈLE » du tableau de l'hypothèse 3** (246:1, 246:3, 253:1) sont des acquittements de
  l'adresse et du psak, pas une relecture halakhique de la condensation.
