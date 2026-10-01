# Orah Haïm — verdicts REF_FAUSSE, lot B (2ᵉ tiers)

Relevé : `audit/citations-sources-orah-haim.csv`.
Sélection déterministe : lignes dont `verdict == REF_FAUSSE`, triées par (fichier, ligne)
croissants, rangs **26 à 50** du tri. **74 REF_FAUSSE au total** dans le compartiment ;
ma tranche en contient **25**.

- Première de la tranche (rang 26) : `sources/orah-haim/siman-60/niveau-2-lamdan.html` ligne **546**
- Dernière de la tranche (rang 50) : `sources/orah-haim/siman-76/niveau-2-lamdan.html` ligne **563**

Méthode : aucune page de `sources/` n'a été modifiée ; `verifier-citations.py` n'a pas été
lancé ; le cache partagé `scripts/.cache-sefaria` n'a pas été touché. Toutes les affirmations
de source ci-dessous viennent de requêtes Sefaria faites pour ce lot
(`api/texts` et `api/search-wrapper`, cache privé dans mon scratchpad). Comparaisons sur
**squelettes consonantiques** (nikoud, ponctuation et balises neutralisés), avec un second
passage neutralisant les **matres lectionis** (yod/vav).

## Verdict d'ensemble

| Famille | Occurrences (lignes du CSV) |
|---|---|
| 1. Fabrication réelle | **0** |
| 2. Citation réelle mal adressée | **18** (9 défauts distincts) |
| 3. Faux positif de la porte | **7** |
| 4. Hors convention | 0 |
| Non tranchés | 0 |

**Aucune fabrication dans cette tranche.** Les 25 textes hébreux existent tous sur Sefaria,
localisés et cités ci-dessous. Les 18 défauts réels sont tous de la même nature : *le texte
est authentique, l'adresse entre parenthèses n'est pas la sienne.*

---

## Famille 3 — Faux positifs, et les mécanismes qui les produisent

C'est la partie la plus réutilisable du lot : **cinq mécanismes**, dont trois feront du bruit
sur toute la pile tant qu'ils ne seront pas corrigés dans la porte.

### M1. Récolte des références AU NIVEAU DE LA LIGNE (3 cas : 29, 32, 49)
La porte ramasse toutes les réfs présentes sur la ligne et confronte chaque citation à
**toutes**, sans regarder à laquelle la page l'attache. Une phrase est alors accusée d'une
adresse que la page ne lui a jamais donnée.

| # | Fichier : ligne | Citation | Réf que la porte lui oppose | Ce que la page écrit vraiment |
|---|---|---|---|---|
| 29 | `siman-62/niveau-2-lamdan.html:513` | `יכול לקרותה בכל לשון` | Berakhot 13a | la parenthèse `(ברכות י״ג.)` porte sur la citation VOISINE, `שמע — בכל לשון שאתה שומע`, **exacte à Berakhot 13a:27**. La phrase accusée est le **שו״ע או״ח ס״ב:ב** verbatim — le séif même du siman traité. |
| 32 | `siman-69/niveau-2-lamdan.html:542` | `ארי הוא יפרוס זבחא` | Mishneh Torah, Prayer 8 | la parenthèse `(הלכות תפלה פרק ח׳)` appartient à la proposition suivante, « וכן פסק הרמב״ם ». La phrase est le targoum de `כי הוא יברך הזבח`, **attestée au שו״ע הרב או״ח ס״ט:ב** (`ארי הוא יפרס זבחא`, écart de matres lectionis seul). |
| 49 | `siman-75/niveau-2-lamdan.html:513` | `מפני שמביא לידי הרהור` | Berakhot 24a | `(ברכות כ״ד.)` suit « ומקורו בגמרא » et introduit les trois étiquettes `טפח/קול/שער באשה ערוה`, **toutes trois exactes à Berakhot 24a:15 et 24a:17**. La phrase accusée est le **שו״ע הרב או״ח ע״ה:א et ע״ה:ד** verbatim. |

### M2. Une MICHNA confrontée au texte du DAF, que Sefaria y abrège (1 cas : 26)
`siman-60/niveau-2-lamdan.html:546` cite `אם כיוון לבו יצא ואם לאו לא יצא` (ברכות י״ג.).
- `Berakhot.13a:16` (William Davidson) ne donne que : **« מתני׳ היה קורא בתורה והגיע זמן המקרא, אם כוון לבו — יצא. »** puis enchaîne sur `בפרקים`.
- Mais `Mishnah_Berakhot.2.1` donne : **« …אם כון לבו, יצא. ואם לאו, לא יצא. »**

La citation de la page est donc **la Michna Berakhot 2:1 intégrale, et ברכות י״ג. est bien son
daf**. La porte échoue parce qu'elle confronte une michna au texte du Talmud, où le nossah
Vilna l'abrège. Mécanisme de classe : il se répétera sur **chaque michna citée par son daf**.
(S'y ajoute l'écart de matres lectionis `כיוון`/`כוון`, inoffensif.)

### M3. Une VARIANTE d'une lettre promue en REF_FAUSSE (1 cas : 27)
`siman-61/index.html:449` cite `עד כאן צריך כוונת הלב` (ברכות י״ג.-י״ג:).
`Berakhot.13b:13` porte : **« תנו רבנן … עד כאן צריכה כוונת הלב, דברי רבי מאיר. »**
L'écart est **un ה final** : `צריך` pour `צריכה`. C'est le nossah des Richonim, et il est
attesté tel quel chez **Rashba on Berakhot 13b:1**, Kessef Mishneh et Maaseh Rokeach, qui
renvoient tous eux-mêmes à Berakhot 13.
**L'adresse de la page est juste.** La porte, son ratio tombé sous le seuil, est allée
chercher le texte ailleurs par recherche plein-texte, et a rendu REF_FAUSSE — alors que cet
« ailleurs » est **un commentaire sur le daf cité**. Un repli plein-texte qui retombe sur
`<Richon> on <le daf même>` devrait rendre VARIANTE, jamais REF_FAUSSE.

### M4. GUILLEMETS IMBRIQUÉS : la porte compare une citation trouée (1 cas : 28)
`siman-61/niveau-2-lamdan.html:648` écrit : `"האומר «מודים מודים» — משתקין אותו"`.
Le CSV a enregistré comme citation : **`האומר « » — משתקין אותו`** — le segment interne a été
**vidé**. La porte a confronté une chaîne à trou. Le texte est réel :
`מודים מודים` est exact à **Berakhot 33b** (segments 16, 17, 26, 27) et à **Mishnah Berakhot 5:3**.
Second mécanisme sur la même ligne : la réf revendiquée vit dans un `<strong>`
(« שורש הדין — משנה ברכות ל״ג: ») et non dans une parenthèse ; la porte ne l'a **jamais
récoltée** et a opposé la citation à `Berakhot.60b | Pesachim.56a`, qui traînaient plus loin
sur la ligne.

### M5. Un VERSET coupé par la drasha au ref cité (1 cas : 37)
`siman-72/niveau-2-lamdan.html:654` cite `בשבתך בביתך ובלכתך בדרך` (ברכות י״א.; סוכה כ״ה.).
Le verset est **Deutéronome 6:7** verbatim. Aux deux dafim cités, la guemara le cite **en deux
morceaux séparés par sa propre drasha** :
> `Berakhot 11a:4` et `Sukkah 25a:5` — « ״בשבתך בביתך״ — פרט לעוסק במצוה, ״ובלכתך בדרך״ — פרט לחתן »

Les deux moitiés sont verbatim aux deux adresses ; seule la **contiguïté** manque. La convention
du dépôt admet l'ellipse dans les guillemets et contrôle chaque segment séparément — ce cas
devrait passer par ce chemin.

> **Réserve à verser au relecteur, pas à mon décompte** : sur cette même ligne, la glose de la
> page `«בלכת שלך»` est une hébraïsation de l'araméen `בלכת דידך` (Berakhot 11a:7, Sukkah 25a:7)
> et n'est **pas** verbatim à ces adresses. La porte ne l'a pas signalée. Ce n'est pas un des
> 25 verdicts de ma tranche et je ne le classe pas ; je le signale pour qu'il soit mesuré.

### Mécanisme secondaire, à surveiller : les ABRÉVIATIONS TYPOGRAPHIQUES du Choul'han Aroukh
Deux de mes cas (33, 48) n'ont été résolus qu'en lisant le texte servi : le Choul'han Aroukh
est imprimé avec des abréviations à geresh que la comparaison par squelette tronque —
`דהוי דברים שבקדוש׳` (או״ח ס״ט:א) pour `שבקדושה`, `דלבו רואה את הערוה אסו׳` (או״ח ע״ד:א)
pour `אסור`. Une recherche naïve conclut « absent du Choul'han Aroukh » alors que la phrase y
est. Le ktiv haser/malé fait le même effet au cas 50 (`דבכסוי` pour `בכיסוי`). Ce mécanisme ne
produit pas de REF_FAUSSE ici, mais il a failli me faire rendre deux faux verdicts.

---

## Famille 2 — Citations réelles, mal adressées (18 occurrences, 9 défauts distincts)

Toutes partagent la même signature : **la parenthèse nomme le daf de la sougya, et le texte
entre guillemets est celui du Choul'han Aroukh, du Taz, ou un verset** — c'est-à-dire pas ce
qui se trouve au daf. Le lecteur qui ouvre la référence ne trouve pas les mots promis.

### 2a — Les mots sont ceux du Choul'han Aroukh (ou du Taz) sur ce daf (7 occurrences)

| # | Fichier : ligne | Texte hébreu | Adresse revendiquée | Adresse VRAIE (vérifiée) |
|---|---|---|---|---|
| 31 | `siman-69/niveau-2-lamdan.html:533` | `לשון חתיכה פרוסה` | מגילה כ״ג: | **שו״ע או״ח ס״ט:א** — « וזה נקרא פורס על שמע לשון חתיכה פרוסה שאין אומרים אלא קצת ממנה » (exact) |
| 34 | `siman-69/niveau-3-synthese.html:623` | `לשון חתיכה פרוסה` | מגילה כ״ג: | idem — **שו״ע או״ח ס״ט:א** |
| 33 | `siman-69/niveau-2-lamdan.html:603` | `דהוי דברים שבקדושה` | מגילה כ״ג: | **שו״ע או״ח ס״ט:א** — « ואין עושין דברים אלו בפחות מי' משום **דהוי דברים שבקדוש'** ». Megillah 23b:6 porte un autre libellé : « כל דבר שבקדושה לא יהא פחות מעשרה » |
| 35 | `siman-71/niveau-2-lamdan.html:533` | `אינו רשאי להחמיר` | ברכות י״ז:-י״ח. | **ט״ז על או״ח ע״א ס״ק ג** (exact). Absent de Berakhot 17b (17 seg.) et de Berakhot 18a (14 seg.) |
| 36 | `siman-72/niveau-2-lamdan.html:533` | `מאחר שלמטה צורך בהם` | ברכות י״ז: | **שו״ע או״ח ע״ב:א** — « …בין אותם שהם לאחריה **מאחר שלמטה צורך בהם** פטורים ושאר המלוין… » (exact). Berakhot 17b:13 porte `שלאחר המטה צורך בהם` — presque l'anagramme, et un autre texte |
| 48 | `siman-74/niveau-2-lamdan.html:679` | `דלבו רואה את הערוה אסור` | ברכות כ״ה. | **שו״ע או״ח ע״ד:א** — « ואז יקרא משום **דלבו רואה את הערוה אסו'** » |
| 50 | `siman-76/niveau-2-lamdan.html:563` | `בכיסוי תלה רחמנא` | ברכות כ״ה. | **שו״ע או״ח ע״ו:א** — « משום **דבכסוי תלה רחמנא** דכתיב וכסית את צאתך והא מתכסיא » (aux matres lectionis près) ; aussi אליה רבה או״ח ע״ט:ג. La guemara dit autrement, et ailleurs : `דצואה בכיסוי תליא מילתא`, **Berakhot 25b:9** |

Deux précisions dues au cas 50 : la seconde moitié de sa parenthèse est **juste** —
`וכסית את צאתך` est exact à **Berakhot 25a:15**. C'est `בכיסוי תלה רחמנא` seul qui est mal placé.
Et dans les sept cas ci-dessus, le daf nommé est **le bon daf de la sougya** ; la réparation
est de changer la parenthèse de la citation, pas la section.

### 2b — La référence désigne simplement le mauvais endroit (11 occurrences)

| # | Fichier : ligne | Texte hébreu | Revendiqué | VRAI |
|---|---|---|---|---|
| 30 | `siman-64/index.html:450` | `והיו — בהוייתן יהו` | מגילה י״ז. | **Berakhot 13a:26** (« אמר קרא ״והיו״ בהוייתן יהו ») ; aussi Megillah 9a:5. **Megillah 17a ne contient pas la drasha** : son 17a:12 tire le למפרע d'ailleurs — « אמר קרא ״ככתבם וכזמנם״ — מה זמנם למפרע לא, אף כתבם למפרע לא ». Pour le ק״ש, c'est Berakhot 13a:30 / 13b:4 |
| 38 | `siman-73/niveau-1-base.html:622` | `ולא יראה בך ערות דבר` | ברכות כ״ד. | **דברים כ״ג:ט״ו** (Deut 23:15, exact) ; dans la guemara **Berakhot 25b:9**. Berakhot 24a (23 segments) **ne cite aucun verset** |
| 39-45 | `siman-73/niveau-2-lamdan.html:469, 483, 503, 513, 533, 563, 759` | idem | ברכות כ״ד. | idem |
| 46 | `siman-73/niveau-3-synthese.html:474` | idem | ברכות כ״ד. | idem |
| 47 | `siman-74/niveau-2-lamdan.html:563` | `שלבו רואה את הערוה אסור` | ברכות כ״ה. | **שו״ע הרב או״ח ע״ד:א** (exact) ; forme de la guemara `לבו רואה את הערוה` à **Berakhot 25b:4 et 25b:7** — amoud **ב**, pas א. Berakhot 25a ne la porte pas |

**Ce qui tranche le cas 38-46, et c'est le dépôt lui-même qui le tranche** : le
`siman-75/niveau-2-lamdan.html:513` écrit, pour exactement la même citation,
`«ולא יראה בך ערות דבר» (דברים כ״ג)` — l'adresse juste. Le siman 73 donne un daf là où le
siman 75 donne le verset. Ce n'est donc pas une convention du dépôt, c'est un écart.

Réserve honnête sur 38-46 : **Berakhot 24a est le bon daf pour la sougya du siman 73**
(`שנים שישנים במטה אחת`, segments 5 à 12, que j'ai lus). Le défaut est étroit et il est réel :
la parenthèse est juste pour la section et fausse pour le verset qu'elle suit.

---

## Étendue réelle, au-delà des 25 lignes du CSV

Le relevé ne couvre que les fichiers **français**. Les mêmes citations hébraïques vivent dans
les variantes `-he` et `-en`, et dans d'autres niveaux que ceux signalés. J'ai mesuré le
**couplage** (citation + référence fautive dans la même fenêtre de ligne) sur les 15 fichiers
de chaque siman :

| Siman | Citation | Réf fautive | Couplages | Fichiers |
|---|---|---|---|---|
| 64 | `בהוייתן יהו` | מגילה י״ז | 43 | 10 |
| 69 | `לשון חתיכה פרוסה` | מגילה כ״ג | 19 | 6 |
| 69 | `דהוי דברים שבקדושה` | מגילה כ״ג | 7 | 4 |
| 71 | `אינו רשאי להחמיר` | ברכות י״ז | 6 | 3 |
| 72 | `מאחר שלמטה צורך בהם` | ברכות י״ז | 18 | 3 |
| 73 | `ולא יראה בך ערות דבר` | ברכות כ״ד | 45 | 11 |
| 74 | `שלבו רואה את הערוה אסור` | ברכות כ״ה | 3 | 3 |
| 74 | `דלבו רואה את הערוה אסור` | ברכות כ״ה | 6 | 6 |
| 76 | `בכיסוי תלה רחמנא` | ברכות כ״ה | 12 | 3 |
| | | **total** | **159** | **42 fichiers distincts** |

**Ce 159 est un ordre de grandeur, pas un compte, et je le dis parce que je l'ai mesuré deux
fois** : une fenêtre de 140 caractères vers l'avant donnait 114 couplages dans 36 fichiers ;
une fenêtre symétrique de 160 en donne 159 dans 42. La mesure dépend de la fenêtre, donc elle
borne par le bas et ne tranche pas. Elle suffit à établir le seul point qui compte ici : les
**18 occurrences du CSV sont un plancher**, la réparation porte sur l'ordre de **150 passages
dans une quarantaine de fichiers**, et elle doit se faire avec la parité trilingue.

---

## Ce que je n'ai PAS fait

- **Aucune page de `sources/` n'a été modifiée.** Ce lot classe ; il ne corrige pas.
- `verifier-citations.py` n'a pas été lancé ; `scripts/.cache-sefaria` n'a pas été lu ni écrit.
- Aucun `git add`, aucun commit. Un seul fichier écrit : celui-ci.
- **La numérotation étrangère, que mon mandat me demandait de chercher spécialement, ne s'est
  pas présentée dans cette tranche** : mes 25 cas citent tous un daf du Talmud (Berakhot,
  Megillah, Rosh Hashanah, Pesachim, Soukka) ou un chapitre du Mishneh Torah. Aucun `או״ח`
  désignant une partie de recueil de responsa, aucune confrontation à la découpe de l'Aroukh
  HaChoul'han. Je ne peux donc ni confirmer ni infirmer ce mécanisme ici — **absence dans ma
  tranche, pas absence dans le compartiment** ; les deux autres tiers des 74 restent à voir.
- Je n'ai pas vérifié si les variantes `-he`/`-en` portent **la même** forme d'adresse fautive
  que le français (j'ai mesuré le couplage, pas la rédaction de chaque occurrence).
- Je n'ai pas classé la réserve du cas 37 (`בלכת שלך` pour `בלכת דידך`) : elle n'est pas dans
  mes 25 verdicts, elle n'est pas mesurée, et elle ne doit pas gonfler un décompte.
- Je n'ai pas cherché si la forme `אינו רשאי להחמיר` existe dans un nossah du Talmud absent de
  Sefaria. Ce que j'affirme est borné à ce que Sefaria m'a servi : absente de Berakhot 17b et 18a.
