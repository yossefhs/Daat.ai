# Le trou de l'exemption « résumé » — étendue mesurée, hypothèses éprouvées, tri à la main

Relevé de mesure. **Aucune page de `sources/` n'a été modifiée, aucun commit, aucun `git add`.**
`verifier-citations.py` n'a pas été lancé (un balayage occupe `scripts/.cache-sefaria`) ; toutes les
confrontations ci-dessous viennent d'interrogations directes de `www.sefaria.org/api/texts`, mises en
cache dans le scratchpad de la séance.

Date : 1er octobre 2026.

---

## 0. Ce que ce relevé établit en une phrase

Le trou n'est pas théorique, il est peuplé, et il est **vingt-cinq fois plus large que l'estimation de 328** [corrigé par l'arbitre : 8 386 / 328 = 25,6 ; « vingt fois » était le rapport des textes distincts, 6 357 / 328 = 19,4 — le paragraphe mélangeait les deux unités, et §a dit déjà « facteur 25 »].
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
contre Sefaria : ~~11 fausses, 3 fidèles, 1 en réserve~~ → après arbitrage, **10 fausses, 5 fidèles,
0 réserve**.** Rendement ~~73 %~~ → **67 %** — toujours la meilleure des trois, d'un ordre de grandeur.

| cellule | colonne | verdict | preuve |
|---|---|---|---|
| OH 1:2 | Mehaber | ~~FAUSSE~~ → **FIDÈLE (réfutée par l'arbitre)** | l'étiquette réelle est **`OH 1:2-3`**, non `OH 1:2` : la cellule cite le séif **2** verbatim (`המשכים להתחנן… יכוין לשעות שמשתנות המשמרות`, vérifié au séif 2) **et** condense le séif **3**. Les deux séifim sont dans la plage annoncée. Motif d'adresse tronqué sur le tiret de plage — le piège même que le mandat signalait |
| OH 243:2 | **Rama** | **FAUSSE** | contenu = Mehaber du séif **א** (`ותנור דינו כמרחץ ורחיים דינו כשדה`) ; la glose du Rama sur 243:2 dit tout autre chose (`ואפילו במקום האסור… רק שכרם מעכו״ם`) |
| OH 244:1 | Mehaber | **FAUSSE** | `אין אומרים` **absent du siman 244 entier**, et du Choul'han Aroukh HaRav 244 (22 séifim) ; 244:1 énonce une **permission** |
| OH 246:1 | Rama | FIDÈLE | la glose du Rama sur 246:1 porte bien `ומותר להשאיל לו בערב שבת` |
| OH 246:3 | Mehaber | FIDÈLE | même psak, même raison (`שאדם מצווה על שביתת בהמתו`) ; phrasé emprunté à la Michna |
| OH 252:1 | Mehaber | **FAUSSE** | `פותקין מים לגינה` et `מוגמר תחת הכלים` sont au séif **252:5** (`ומותר לפתוח מים לגנה… ולתת מוגמר תחת הכלים`) |
| OH 252:5 | Mehaber | ~~RÉSERVE~~ → **FIDÈLE sur l'adresse et le psak (résolu par l'arbitre)** | `משתרף` est bien absent de SA OH 252 (7 séifim) **et** de SA HaRav 252 (20 séifim) — formulation composée. Mais le psak est **au séif 252:5** qu'elle nomme : `וטוענין בקורות בית הבד והגת מבעוד יום על זיתים וענבים והשמן והיין היוצא מהן מותר`. Adresse juste, psak juste, hébreu composé : même classe de faux positif que 246:1 et 253:1 |
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
- **Le défaut est groupé : ~~11 des 15 cellules~~ → les 10 cellules fausses sont dans Chabbat 243-263, sans exception** (l'arbitrage a retiré la seule fausse hors Chabbat, OH 1:2-3 ; le groupement en ressort **plus** net, non moins). C'est la même plage que les
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

**Bilan du tri : ~~6 FAUSSES · 3 IMPRÉCISES · 5 FIDÈLES~~ → après arbitrage 5 FAUSSES · 3 IMPRÉCISES · 6 FIDÈLES.** Cinq sur quatorze (item 1, OH 1:2-3, réfuté).
Par compartiment : Orah Haïm 5 items (~~1 fausse~~ **0 fausse**, 2 imprécises, ~~2~~ **3** fidèles) ·
Chabbat 7 (5 fausses, 1 imprécise, 1 fidèle) · Yoré Déa 2 (2 fidèles).

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

---

## e) Note d'arbitrage — 1er octobre 2026

Relevé contradictoire, par un second agent. Aucune page de `sources/` touchée, aucun commit.
Toutes les confrontations ci-dessous sont des interrogations directes de Sefaria faites pour cet
arbitrage, cache séparé ; `verifier-citations.py` n'a pas été lancé.

**Chiffres reproduits sans le script de l'auteur** (grep seul, puis une pile de balises réécrite) :
8 386 occurrences · 860 fichiers · orah-haim 6 563 / yoreh-deah 1 539 / shabbat 284 ·
niveau-1 4 436 / niveau-2 3 347 / niveau-3 123 / n4-daat-harav 379 / n4-halakha 47 / index 54 ·
fr 2 823 / en 2 805 / he 2 758 · `תמצית` 4 796 / `résumé` 1 800 / `summary` 1 790 ·
**272 cellules** · **3 198 encadrés pédagogiques**. Tous exacts au chiffre près.
Donc « 328 surestime de 20 % la famille des cellules » **tient**.

**Chiffres qui ne tombent pas**, et il faut le dire :
- **6 357 textes distincts** → 6 305 avec ma normalisation (−0,8 %). Dépend du normaliseur ; ce n'est
  pas un compte au même titre que 8 386, contrairement à ce qu'écrit §a.
- **165 cellules adressées** → non reproductible : un motif `OH <n>:<n>` en chiffres arabes n'en lit
  que **56 sur 272**. Non réfuté, mais non vérifiable depuis la description donnée.
- **`<li>` 357 · `<p>` 312 · lamdan 2 709** → j'obtiens 9 · 282 · 3 084. L'écart est l'**ordre de
  priorité** du classement (`<li>` testé avant ou après les familles de classe), pas le comptage :
  le total et les familles décisives sont identiques. La table n'est pas reproductible sans cette règle.

**Ce que l'arbitrage ajoute :**

1. **`scripts/verifier-alignement.py` ne lit pas le niveau 4** — et c'est la porte écrite POUR ce
   défaut. Son commentaire dit qu'elle est née du siman 243. Sa liste de fichiers est
   `ENTIER = ("niveau-1-base.html",)` et `INLINE = ("index.html", "niveau-2-lamdan.html",
   "niveau-3-synthese.html")` : **`niveau-4-daat-harav.html` n'y est pas, ni aucune variante `-he`
   / `-en`.** Sept des dix cellules fausses sont des décalages de séif ou des attributions croisées
   — sa question exacte — et toutes vivent au niveau 4, dans trois langues. Le relevé impute le
   silence à l'exemption de verbatim ; la cause immédiate est une **liste de fichiers**.
2. **Les 1 539 occurrences de Yoré Déa ne sont pas « non mesurables ».** `1 237 des 1 256`
   condensations de niveau 1 de Yoré Déa (98,5 %) suivent immédiatement un `blockquote` qui porte
   **sa propre référence** (`(ט״ז יו״ד קמ״ט ס״ק א)`). L'ancre juste était une balise au-dessus.
   `non_fait` n° 9 diagnostique correctement que l'ancre « Séif N » est fausse en Yoré Déa, puis
   s'arrête là.
3. **Échantillon indépendant, 13 items, 0 fausse.** 7 condensations de niveau 1 de Yoré Déa
   (simanim 136, 137, 141, 149, 153, 158, 160) et 6 cellules de niveau 4 d'Orah Haïm **hors** de la
   plage chaude (OH 6:3, 11:14, 12:3, 13:1, 13:2, 14:3) : **13 fidèles**. Avec les 2 items Yoré Déa
   de l'auteur, 9 sur 9 en Yoré Déa. Le groupement en Chabbat 243-263 est **corroboré**, et le 67 %
   est un taux de plage chaude, non un taux de site.
   *Mise en garde méthodique : mon premier passage rattachait la condensation au DERNIER blockquote
   et rendait 5 discordances sur 7 ; les 5 se sont dissoutes à la lecture du HTML brut — une
   condensation couvre le GROUPE de blockquotes qui la précède. Trois d'entre elles auraient été
   publiées comme défauts.*
4. **La troisième question de l'hypothèse 3 n'est pas une porte à elle seule.** Sur mes 6 cellules
   fidèles d'Orah Haïm, le squelette consonantique est **absent du séif cité dans 4 cas** (OH 13:1,
   13:2, 14:3, 11:14) : une condensation écrit `ד׳` pour `ארבע`, `מעכבות` pour `מעכבין`, et déplace
   les clauses. Le « squelette RETROUVÉ 0 / ABSENT 40 » n'est exact que parce que le filtre du
   nikoud passe d'abord. Qui écrira la porte ne doit pas retirer la première question.
5. **L'étiquette composée, un piège non nommé.** Au-delà du tiret de plage (11 étiquettes sur les 56
   que lit mon motif), des cellules portent **deux adresses** : `OH 11:4, 12` · `OH 8:7, 8:9` ·
   `OH 8:10, 8:15-16`. Un test à un seul séif y produit le même faux positif que sur `OH 1:2-3`.
6. **Deux marqueurs `résumé` français dans un fichier anglais**, relevés par l'auteur comme
   « 2 égarés » et laissés là : `sources/shabbat/siman-293/niveau-2-lamdan-en.html`, page
   `<html lang="en" dir="rtl">`, dont les deux condensations sont **intégralement en français** — et
   l'une porte un reste de chantier éditorial, « source primaire à établir (citation retirée faute de
   source vérifiée) », dans une page publiée.
