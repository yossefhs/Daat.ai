# Rapport signal / bruit des piles de candidats

Lot de **mesure et de tri** — aucune page de `sources/` n'a été modifiée, aucun commit.
Date de la mesure : 2026-10-01. Chaque verdict ci-dessous vient de Sefaria interrogé
pendant ce lot (cache privé hors `scripts/.cache-sefaria`, le balayage en cours n'a pas
été touché ; `verifier-citations.py` n'a pas été lancé).

**Ce que ce relevé mesure :** la proportion de lignes, dans chaque pile, qui vaut la
lecture du Rav. Une pile dont neuf lignes sur dix sont du bruit ne sera pas lue, et c'est
aussi grave qu'une porte muette.

---

## 0. Les tailles réelles des piles, avant tout taux

`audit/ancrage-candidats.txt` annonce **152 écarts**. Ce 152 compte les **pages
atteintes**, pas les défauts :

| unité | nombre | commande |
|---|---|---|
| occurrences `ÉCART` (= pages atteintes) | **152** | `grep -c '^ÉCART' audit/ancrage-candidats.txt` |
| couples distincts (siman × ס״ק × séif annoncé × séif ancré) | **63** | dédoublonnage des 152 lignes |
| dont Hilkhot Chabbat | 9 occurrences · **6 couples** | idem |
| dont Yoré Déa | 143 occurrences · **57 couples** | idem |
| dont Orah Haïm | **0** | la porte mesure 159 confrontations, 0 écart |

Les deux unités sont utiles et il faut les deux : les occurrences disent combien de
lecteurs sont trompés (un défaut dans les trois langues = trois lecteurs), les couples
disent le **travail réel**. **Le mandat demandait des écarts « répartis sur les
compartiments » : c'est impossible à trois compartiments.** Orah Haïm n'en dépose aucun,
et Chabbat n'en a que 6 couples, sur 3 simanim (244, 264, 267). L'échantillon est donc
réparti sur les deux compartiments qui déposent.

---

## 1. Pile `audit/ancrage-candidats.txt` — 14 sites ouverts

**Taille de l'échantillon, dite dans l'unité où elle a été tranchée :** 14 **sites**
(un site = un siman × un ouvrage × une revendication de la page), couvrant
**26 des 63 couples distincts** et **61 des 152 occurrences**, soit 41 % du travail réel
de la pile.

### 1.0 Calibrage — le défaut témoin (Chabbat 267) : DÉFAUT RÉEL, confirmé

`sources/shabbat/siman-267/niveau-3-synthese.html:446` (et les variantes `-he`, `-en`:435).
Ligne de tableau : « Hashkivenou — j'ai dit "Shomer Ammo" puis je me suis rendu compte »
→ **« Seif 3 + MB s"k 5-6 »**.

Mesuré sur `Shulchan_Arukh,_Orach_Chayim.267` : Michna Beroura ס״ק א→séif 1 · **ס״ק ב à ו
→ séif 2** · ס״ק ז, ח, ט→séif 3.

Lu dans `Mishnah_Berurah.267` :
- ס״ק ה = `(ה) ולאכול` — manger après avoir accepté le Chabbat tôt ;
- ס״ק ו = `(ו) מיד` — attendre une demi-heure, et le ק״ש de nuit ;
- **ס״ק ט = `(ט) הפורס סוכת וכו' — ואם שכח ואמר שומר עמו ישראל תחת הפורס סוכת שלום אם נזכר
  תכ״ד יאמר מיד…`** — c'est EXACTEMENT le cas de la ligne, et c'est le seul ;
- ס״ק ז = `(ז) אינו חותם — דבשבת א״צ שמירה` — la raison.

**Le séif 3 est juste** (les ancres ז-ט y sont) ; **ce sont les numéros de ס״ק qui sont
faux**. Le lecteur qui ouvre le ס״ק ה tombe sur les lois du repas avant la nuit. Les
bonnes adresses sont ס״ק ט (le cas) et ס״ק ז (la raison).

> Ce que le calibrage enseigne et qui sert pour les 13 suivants : la porte annonce
> « la page dit séif X, l'ancre le pose au séif Y » ; cet énoncé est un **symptôme**, pas
> le défaut. Ici le séif était bon et le ס״ק faux. Il faut donc, à chaque ligne, lire ce
> que le ס״ק cité **dit**, et pas seulement où il est posé.

### 1.1 Les 13 autres sites

| # | site | ce que la page écrit | verdict |
|---|---|---|---|
| 1 | chabbat 244 `niveau-2-lamdan.html:572` | « le séif א exclut expressément … MB ס״ק כ״ז » | **DÉFAUT RÉEL** |
| 2 | chabbat 264 `niveau-2-lamdan-en.html:599` | « as in seif 7, or … as in seif 3 ? … his ס״ק כ״ד » | FAUX POSITIF |
| 3 | yd 101 `niveau-2-lamdan-he.html:428` | « (סעיף ה׳, ט״ז ס״ק ט–יא) » | ÉCLAIRANTE LÉGITIME |
| 4 | yd 103 `niveau-2-lamdan.html:417` | « (seif 3, Chakh ס״ק ב et י״ב) » | ÉCLAIRANTE LÉGITIME |
| 5 | yd 105 `niveau-2-lamdan.html:716` | « le seif 7 contre le seif 9 (Taz ס״ק כ״ב) » | FAUX POSITIF |
| 6 | yd 112 `niveau-4-halakha.html:575` | « seif 11, Shach s.k. 6-9 » | **DÉFAUT RÉEL** |
| 7 | yd 119 `niveau-2-lamdan.html:463` | « le psak du Taz ס״ק י״ח (seif 7) » | ÉCLAIRANTE LÉGITIME *(réserve)* |
| 8 | yd 124 `niveau-4-halakha.html:610` | « comme il ressortira du seif 24 (ט״ז … ס״ק י) » | FAUX POSITIF |
| 9 | yd 148 `index.html:168` | « מה שנזכר בסעיף ט׳ … (ש״ך … ס״ק י״ב) » | FAUX POSITIF |
| 10 | yd 168 `niveau-1-base.html:666` | « seif 16 · ש״ך ס״ק ס״ח » | **DÉFAUT RÉEL** *(systématique)* |
| 11 | yd 201 `niveau-1-base.html:1897` | « Seif 40 et Chakh ס״ק נ״ז » | **DÉFAUT RÉEL** |
| 12 | yd 234 `niveau-4-halakha.html:487` | « seif 55 · Baer Hetev ס״ק א » | FAUX POSITIF |
| 13 | yd 92 `niveau-1-base.html:1059` | « … du seif 1 ? Et le Shach (s.k. 3) … ? » | FAUX POSITIF |

### 1.2 Les quatre défauts réels, avec leur preuve

**Chabbat 244 — `niveau-2-lamdan.html:572` (+ `-he`, `-en`). ס״ק כ״ז donné au séif א.**
`Mishnah_Berurah.244` ס״ק כ״ז = `(כז) בבית ישראל - דבזה אפילו קבלנות גמורה אסור כדלקמן
בסימן רנ״ב:`. Le **contenu** est exactement ce que la page lui fait dire. Mais la clause
`בבית ישראל` qu'il glose a été cherchée dans les six séifim de
`Shulchan_Arukh,_Orach_Chayim.244` : elle est **présente au séif 5 et nulle part ailleurs**
(séifim 1, 2, 3, 4, 6 : absente), et l'ancre y pose ס״ק כ״ז. La page écrit « ce que le
séif א exclut expressément » : le séif א ne porte pas cette clause, et le lecteur qui l'y
cherche, ou qui y cherche le ס״ק כ״ז, ne trouve ni l'un ni l'autre (le MB du séif א est
ס״ק א–י״ג).

**Yoré Déa 112 — `niveau-4-halakha.html:575` (+ `-en`:581). « seif 11, Shach s.k. 6-9 ».**
Ancres de `Shulchan_Arukh,_Yoreh_De'ah.112` : Siftei Kohen **ס״ק ו, ז, ח, ט → tous au séif
2** ; et **le séif 11 ne porte AUCUNE ancre du Chakh** (ס״ק י״ט→séif 9, ס״ק כ→séif 10,
ס״ק כ״א→séif 13). Des quatre ס״ק annoncés, **un seul traite le sujet** : ס״ק ז
(`דוקא פת עובד כוכבים אבל פת ישראל שאפאו עובד כוכבים … שהרי הוא כבישולי עובד כוכבים`),
et c'est bien la thèse que la page soutient. Les trois autres sont ailleurs : ס״ק ו
compare aux שלקות, ס״ק ח donne la raison du Mordekhi, ס״ק ט le minhag et les dix jours de
תשובה. La plage « s.k. 6-9 » promet quatre rattachements dont trois sont hors sujet, à un
séif qui n'en porte aucun. *(À décharge : le « Shach (s.k. 1) » de la même ligne est
exact — ס״ק א dit bien `כל שעשה בו ישראל מעשה באפייה מותר` au nom du Rambam et du Rachba.)*

**Yoré Déa 168 — `niveau-1-base.html:666` (+ `-he`, `-en`). Écart SYSTÉMATIQUE de +5.**
C'est le cas le plus net des quatorze, et c'est la signature que la docstring de la porte
dit de chercher. `Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De'ah.168` ס״ק ס״ח commence par le
lemme **`באחריות העובד כוכבים כו׳`** — ces mots sont dans le **séif 21**
(`מעותיו של ישראל מופקדים ביד עובד כוכבים והלוה אותם לישראל ברבית אם היו באחריות העובד
כוכבים מותר…`). Et le **contenu rédigé de la page décrit le séif 21**, pas le 16 : « Un
Juif emprunte à un Juif, mais l'argent transite par un établissement non juif … qui perd
si l'emprunteur ne rend rien ? ». Le séif 16, lui, est un **autre cas** : un Juif confie
de l'argent à un messager pour le prêter à un **non-Juif** (`טול מעות הללו והלוה אותם
לעובד כוכבים ברבית`). La page étiquette « seif 16 » deux fois sur la même ligne.
**Et la ligne suivante (668) répète le décalage :** « seif 17 · ש״ך ס״ק ס״ט », quand
ס״ק ס״ט est ancré au séif 22. Deux étiquettes consécutives décalées de **+5** : ce n'est
pas un écart isolé, c'est un bloc à reprendre.

**Yoré Déa 201 — `niveau-1-base.html:1897` (+ `-he`, `-en`). ס״ק נ״ז au lieu de ס״ק פ״ז.**
La page : « Seif 40 et Chakh ס״ק נ״ז : on perce le seau au fond, si peu que ce soit… ».
Le **séif 40 est juste** — c'est lui qui dit `יקוב הכלי בשוליו כל שהוא`. Mais
`Siftei_Kohen_on_Shulchan_Arukh,_Yoreh_De'ah.201` ס״ק נ״ז est
`והאמה נכנסת כו׳. פי׳ הר״ש דהיינו אמה של מי גשמים…` — une אמה d'eau de pluie entrant dans
un bassin, **rien sur le percement d'un récipient** ; son ancre est au séif 22. Le Chakh
du séif 40 est ס״ק פ״ג–פ״ח. **Et la source donne elle-même la bonne adresse :** la glose
du Rama du séif 40 porte le renvoi `(עיין ס״ק פ״ז)`. נ״ז / פ״ז diffèrent d'une lettre
(נ=50, פ=80) : c'est un lapsus d'une lettre, et il envoie le lecteur à **dix-huit** séifim
de là (séif 22 au lieu du séif 40).

> **Correction d'un arbitre, 2026-10-01.** Ce relevé écrivait « cinquante-huit séifim de
> là ». L'écart réel est de **18 séifim** : l'ancre de ס״ק נ״ז est au séif 22, la page
> annonce le séif 40. Le « 58 » paraît venir de 80 − 22, soit la guématrie du ס״ק
> (פ=80) retranchée d'un numéro de SÉIF — deux unités différentes soustraites l'une de
> l'autre, qui est le défaut de méthode que ce dépôt documente partout ailleurs. Le
> défaut d'ancrage lui-même est confirmé par mesure indépendante (ס״ק נ״ז → séif 22 ;
> ס״ק פ״ז → séif 40 ; le renvoi `(עיין ס״ק פ״ז)` est bien dans la glose du Rama du
> séif 40 ; le siman compte 75 séifim).

### 1.3 Les trois citations éclairantes légitimes

- **yd 101** — la page cite une **plage** `ט״ז ס״ק ט–יא` au séif ה. La **borne haute est
  exacte** (ס״ק י״א → séif 5) et c'est elle qui porte le sujet annoncé : ס״ק י״א est tout
  entier sur le `קורקבן אווז` et le `הכל תלוי לפי הזמן` que la page résume. ס״ק ט
  (`שומן הכנתא`, séif 4) traite les `בני מעיים` — l'autre moitié de la même phrase. La
  porte signale la borne basse d'une plage dont la borne haute est juste : c'est son
  fonctionnement normal, et elle sort en 0 pour cela.
- **yd 103** — même forme, en paire et non en plage : `Chakh ס״ק ב et י״ב`. ס״ק י״ב
  (`ואלמלא המלח והתבלין כו׳`, séif 3) est le sel et les épices ; ס״ק ב (séif 2) est
  précisément là où est établi `לא לשבח ולא לפגם אסור`, l'autre moitié de la phrase. Les
  deux moitiés de l'énoncé sont chacune à leur place.
- **yd 119 — avec une réserve, et elle corrige une affirmation antérieure du dépôt.**
  `CLAUDE.md` donne ce cas comme un défaut réel : « le Taz ס״ק י״ח du siman 119, donné au
  séif 7 dans les trois langues quand son ancre le pose au séif 19 ». Mesuré : l'ancre est
  bien au séif 19, et le lemme de ס״ק י״ח est la glose finale du séif 19
  (`וכל זה אינו נוהג בחשוד וכו׳`). **Mais ce que la page lui attribue s'y trouve, et ne se
  trouve que là :** la page écrit « R. Méir contre Rabban Chimon ben Gamliel, et le psak du
  Taz ס״ק י״ח », et ס״ק י״ח finit par
  `והראב״ד סבירא ליה דלא פסקו כרשב״ג … כר״מ וכך יש לפסוק למעשה כנלע״ד`. Le ס״ק ט, qui est
  le Taz du séif 7, ne contient pas ce psak. Le sujet (`נאמן בשל אחרים`) est bien celui du
  séif 7. **Ce n'est donc pas un ס״ק faux ni une fabrication** : le Taz statue, depuis le
  séif 19, sur le din du séif 7, et la page le dit. *Réserve de forme :* la parenthèse
  « (seif 7) » se lit comme une localisation ; « (sur le din du séif 7) » lèverait
  l'ambiguïté. **Je signale explicitement que je contredis ici le relevé antérieur.**

### 1.4 Les six faux positifs, et le piège qui produit chacun

| site | piège |
|---|---|
| chabbat 264 | **plusieurs étiquettes de séif dans une même phrase.** « as in seif 7, or … as in seif 3 ? » puis le ס״ק. La porte retient la **dernière** (3) ; l'ancre donne 7, que la page nomme aussi. |
| yd 105 | **le même**, en français et de façon encore plus nette : « le seif 7 contre le seif 9 (Taz ס״ק כ״ב) ». L'ancre pose ס״ק כ״ב au séif 9 — l'une des deux que la phrase oppose. La page a raison sur les deux. |
| yd 124 | **l'étiquette la plus proche est un RENVOI, pas une localisation.** Le paragraphe entier porte sur le séif 12 (« Le seif 12 met en scène… ») et l'ancre pose ט״ז ס״ק י **au séif 12**. Le « seif 24 » que la porte a retenu est la fin de la phrase « comme il ressortira du seif 24 » — un renvoi en aval. |
| yd 148 | **l'étiquette est DANS la citation : la source parle, pas la page.** Le ש״ך ס״ק י״ב est, mot pour mot, `אבל בזמן הזה כו׳. ומ״מ מה שנזכר בסעיף ט׳ אסור גם האידנא. ב״ח` — c'est **le Chakh** qui dit « séif 9 ». La page, elle, écrit « (ש״ך יו״ד קמ״ח ס״ק י״ב) » et n'annonce **aucun** séif. C'est la leçon de `verifier-denombrements.py` : *une citation n'affirme pas, elle rapporte.* |
| yd 234 | **le ס״ק renvoie lui-même au séif que la page annonce.** `Ba'er Hetev … 234` ס״ק א = `האב והבעל מפירין דוקא דברים שיש בהם עינוי נפש או בינו לבינה **כדלקמן סנ״ה** ונ״ח`. La page écrit « deux catégories seulement / seif 55 · Baer Hetev ס״ק א » : le séif 55 codifie bien les deux catégories, et le ס״ק א est bien celui qui les énonce — **en nommant le séif 55**. Les deux moitiés sont exactes. |
| yd 92 | **l'étiquette ne gouverne que le PREMIER ס״ק.** « Que dit le Taz (s.k. 1) sur les deux interdits du seif 1 ? **Et** le Shach (s.k. 3) au nom du Ran ? » — deux questions de compréhension ; « seif 1 » porte sur le Taz ס״ק א, qui **est** au séif 1. La seconde question n'annonce aucun séif. Et le ס״ק ג du Chakh **cite bien le Ran** (`כמ״ש הר״ן ס״פ כ״ה וז״ל…`). |

### 1.5 Taux pour la pile `ancrage`

| verdict | sur 14 sites ouverts | lu sur |
|---|---|---|
| **DÉFAUT RÉEL** | **5** (267, 244, 112, 168, 201) | **36 %** |
| éclairante légitime | 3 (101, 103, 119) | 21 % |
| **FAUX POSITIF** | **6** (264, 105, 124, 148, 234, 92) | **43 %** |

**Le taux, dit sans l'arrondir en « environ » : 5 défauts réels sur 14 sites ouverts, sur
une pile de 63 couples distincts (152 occurrences) ; l'échantillon couvre 26 de ces 63
couples.** Si le taux se tenait, la pile porterait de l'ordre de 22 défauts réels sur 63 —
**c'est une extrapolation, pas une mesure**, et je ne la donne que comme ordre de grandeur.

**Ce qui est mesuré, et non extrapolé :** la pile est **lisible**. Plus d'une ligne sur
trois est un vrai défaut, et les faux positifs ne sont pas aléatoires — **ils se ramènent
à quatre familles** (plusieurs étiquettes dans la phrase · l'étiquette est un renvoi ·
l'étiquette est dans la citation · l'étiquette ne gouverne que le premier ס״ק). Ces quatre
familles font **6 des 6 faux positifs** de l'échantillon. Elles sont mécanisables, et les
traiter rendrait la pile beaucoup plus dense.

---

## 2. Les onze verdicts les plus graves — `audit/citations-sources-shabbat.csv`

**Échantillon : 11 sur 11. La pile entière. Aucune extrapolation.**
(CSV lu, script non lancé.) **Les onze sont dans des fichiers `niveau-2-lamdan` français,
et quatre d'entre eux dans un seul fichier : `sources/shabbat/siman-307/niveau-2-lamdan.html`.**

### 2.1 La seule absence réelle : `אגרות הדיוטות`

`sources/shabbat/siman-307/niveau-2-lamdan.html:363`
```
<li><strong>שבת קמ״ט:</strong> — סוגיא של "<em>אגרות הדיוטות</em>" — אסור
<a class="intra-ref" href="#4-סוגיית-שטרי-הדיוטות-מה-אסור-לקרוא-בשבת">לקרוא</a> בשבת.</li>
```
Recherche plein texte Sefaria sur `אגרות הדיוטות` : **total 0**. Zéro occurrence dans tout
Sefaria. Le terme réel est **`שטרי הדיוטות`**, et il est **présent** — vérifié
verbatim dans `Shabbat.116b`.

**Et la page se contredit sur la même ligne :** son propre lien interne pointe vers
`#4-סוגיית-שטרי-הדיוטות-…` — le titre de sa section dit `שטרי`, le terme entre guillemets
dit `אגרות`. C'est une **erreur de terme**, non une halakha inventée, mais c'est le seul
des onze dont le texte entre guillemets n'existe nulle part. *(Le daf est aussi à revoir :
`שטרי הדיוטות` est en 116b, la page annonce קמ״ט = 149b.)*

### 2.2 Quatre citations réelles mal adressées

| fichier:ligne | texte entre guillemets | mesuré |
|---|---|---|
| 307:362 | `אומר לעכו״ם ועושה` | **26** occurrences dans Sefaria (Piskei Tosafot, Sefer HaMakhria, Kaf HaChayim…) — **aucune dans `Shabbat.120b`**, que la page annonce. |
| 307:538 | `שלא תהא שבת קלה בעיניהם` | **25** occurrences (Maggid Michné & Késsef Michné sur Rambam *Chabbat* 2:3, Kaf HaChayim) — **absent de `Shabbat.120b`**. |
| 307:368 | `אמירה לעכו״ם שבות` | Le dictum est réel et il est **au `Shabbat.150a:4`** : `מַתְקֵיף לַהּ רַב אָשֵׁי: אֲמִירָה לְגוֹי שְׁבוּת!` (aussi `Eruvin.68a`, Rachi sur *Bava Metzia* 90a). La page annonce `שבת ק״כ:` et écrit `עכו״ם` là où Sefaria sert `גוי` — la variante de censure, pas une fabrication. **Le daf, lui, est faux.** |
| 286:490 | `תדיר ושאינו תדיר — תדיר קודם` | Dans un `<blockquote>` attribué à `גמ' זבחים (פ״ט ע״א)`. `Zevachim.89a` dit `כל התדיר מחבירו קודם את חבירו` (**présent**, vérifié) ; la **formulation citée est celle de la michna de `Sukkah.54b`** (108 occurrences dans Sefaria, dont `Sukkah 54b:12`). Revendication de verbatim sur le mauvais traité. |

Ces quatre-là demandent une correction d'adresse (et, pour 307, une reprise d'ensemble :
trois des quatre y pointent le même daf 120b, qui ne porte aucun des trois).

### 2.3 Six faux positifs de la porte

| fichier:ligne | pourquoi c'en est un |
|---|---|
| **273:348** | **Double faux positif.** (i) La référence confrontée était `Isaiah.58.13`, prise du `(ישעיהו נ״ח:יג)` du début de la ligne, alors que la page étiquette explicitement le second segment `הדרשה (במ״ב)`. (ii) Contre la bonne source, la citation est **réelle** : `Mishnah_Berurah.273` ס״ק א = `במקום סעודה - דכתיב וקראת לשבת ענג במקום ענג שהוא הסעודה שם תהא הקריאה של קידוש`. Seul écart : la page écrit `עונג`, le MB `ענג` — **ktiv malé contre ktiv haser**, le faux positif dominant que `verify-chabbat-source.py` isole déjà. |
| **320:358** | **La citation est réelle, verbatim, et elle ENJAMBE la frontière du daf.** `Shabbat.144a` finit par `…דתניא סוחטין` et `Shabbat.144b` commence par `בפגעין ובפרישין ובעוזרדין, אבל לא ברימונים`. Mesuré : `סוחטין בפגעין ובפרישין` est **absent de 143b, de 144a et de 144b pris séparément**, et **présent dans la concaténation 144a+144b**. La page annonce la plage `שבת קמ״ג:-קמ״ה.`, qui la contient ; la porte n'a confronté que la borne basse, `Shabbat.143b`. Aucune citation à cheval sur deux dafim ne peut être trouvée en testant un daf. |
| **262:433** | La page **dit elle-même** que `לכה דודי לקראת כלה` est le piyyout d'Alkabetz, « מבוסס ישירות על » *Chabbat* 119a, et composé « מ"לכה דודי" של שיר השירים + "לקראת כלה" של ר' ינאי ». Le `Shabbat.119a` confronté vient de la clause voisine de la même ligne. Le texte existe (`Lekha Dodi 1:1`) et la page est explicite sur son statut. |
| **269:339** | `"קידוש במקום סעודה"` est un **nom de sougya** (`סוגיא ב"…"`), pas une citation — et le daf annoncé est **juste** : `אין קידוש אלא במקום סעודה` est **présent** dans `Pesachim.101a` (vérifié). |
| **310:349** | `"מחלוקת ר' יהודה ור' שמעון"` est une **description** en français d'une controverse (« la dispute de R. Yehouda et R. Chimon »), entre guillemets dans une liste de sougyot. Rien à confronter : la juger sur le verbatim est une erreur de catégorie. |
| **296:416** | `גמ' פסחים (ק״ה ע״א): "אסור לטעום קודם הבדלה"`. Le **daf est juste** et la doctrine y est : `Pesachim.105a` porte `כׇּל הַטּוֹעֵם כְּלוּם קוֹדֶם שֶׁיַּבְדִּיל — מִיתָתוֹ בְּאַסְכָּרָה` (vérifié). La chaîne citée est une **condensation fidèle** mise entre guillemets. |

**Réserve à donner avec ce classement, et elle compte :** quatre de ces six faux positifs
(269, 310, 296, et 307:362/538 côté « mal adressé ») sont des **manquements à la convention
de citation du dépôt** — les guillemets y sont posés sur un nom de sougya, une description
ou une condensation, alors que les guillemets sont réservés au verbatim et qu'une
condensation s'introduit par `<em>résumé</em> :`. Ce n'est **pas** une fabrication, et la
porte a tort de les compter en « absente de tout Sefaria » ; mais ce sont de vraies lignes
à reprendre. Les classer « bruit » serait injuste à la porte : elle a vu quelque chose, elle
l'a mal nommé.

### 2.4 Taux pour la pile des onze verdicts graves

| verdict | sur 11 ouverts (= toute la pile) | lu sur |
|---|---|---|
| **fabrication réelle** (texte absent de tout Sefaria) | **1** (307:363 `אגרות הדיוטות`) | **9 %** |
| citation réelle mal adressée | 4 (307:362, 307:538, 307:368, 286:490) | 36 % |
| faux positif de la porte | 6 (273:348, 320:358, 262:433, 269:339, 310:349, 296:416) | 55 % |
| *dont faux positifs qui sont néanmoins un manquement de convention* | *3 (269, 310, 296)* | *27 %* |

**Lecture.** L'accusation la plus grave du dispositif — « absente de tout Sefaria », qui est
l'accusation de fabrication — **tient une fois sur onze**, et même cette fois-là est une
erreur de terme (`אגרות` pour `שטרי`) que la page contredit dans son propre lien, non une
halakha inventée. **Il n'y a aucune fabrication halakhique dans ces onze lignes.** C'est un
résultat rassurant sur le contenu et sévère sur la porte : **sur les onze verdicts qu'elle
présente comme les plus graves, six sont du bruit**, et deux de ces six (273, 320) tiennent
à des défauts de mesure identifiables et réparables — la référence prise sur la mauvaise
clause de la ligne, et la citation à cheval sur deux dafim.

---

## 3. `MB 359 ס״ק ו` et `MB 359 ס״ק ח` — les deux « ס״ק inexistants »

**Échantillon : 2 sur 2. Verdict : FAUX POSITIFS tous les deux — et PAS pour la raison
annoncée.**

La porte les a rendus `NON_RESOLU` en précisant que « ce siman s'arrête à 5 » et en
annonçant des candidats faibles, « faux positifs de guématrie attendus ». Les deux points
sont à corriger : **le siman 359 s'arrête bien à 5** (`Mishnah_Berurah.359` : 5 segments
servis, vérifié), **mais la guématrie n'a rien à voir ici.**

Lu dans `sources/shabbat/siman-359/niveau-2-lamdan.html` (lignes 404 et 412) :
```
«ובית סאתים הוא ה׳ אלפים אמה באמה רוחב» (משנה ברורה שנ״ח סק״ו)
«וסמכו חכמים בשיעור זה אשיעורא של חצר המשכן שהיה ב״ס בכולו» (משנה ברורה שנ״ח סק״ח)
```
**La page écrit `שנ״ח` — siman 358 — et non 359.** Confrontation faite :
`Mishnah_Berurah.358` sert **101 entrées**, et

| ס״ק | texte servi par Sefaria | la citation de la page y est-elle verbatim ? |
|---|---|---|
| 358 ס״ק ו | `(ו) שהוא שיעור ע׳ וכו׳ - … ובית סאתים הוא ה׳ אלפים אמה באמה רוחב…` | **OUI** |
| 358 ס״ק ח | `(ח) מותר לטלטל בכולו - וסמכו חכמים בשיעור זה אשיעורא של חצר המשכן שהיה ב״ס בכולו והיו מטלטלים בו:` | **OUI** |
| 358 ס״ק י״א | `… שמצינו בחצר המשכן שארכו מאה ורחבו חמשים:` | **OUI** |

(squelettes consonantiques comparés, nikoud et ponctuation neutralisés)

**Les deux adresses de la page sont justes.** Ce ne sont pas de vraies adresses fausses.

### 3.1 La cause, lue dans le script et non supposée

`scripts/verifier-citations.py:1594-1598` :
```python
RE_SIMAN_NOMME = re.compile(r'(?<![א-ת])(?:או["״]?ח|יו["״]?ד|סימן|סי[\'׳])(?![א-ת])\s*'
                            r'(?P<s>[\dא-ת"״\'׳]{1,6})')
RE_TOUR_SIMAN  = re.compile(r'(?<![א-ת])(?:או["״]?ח|יו["״]?ד)(?![א-ת])\s*'
                            r'(?:סימן\s*|סי[\'׳]\s*)?(?P<s>[\dא-ת"״\'׳]{1,6})')
```
et `candidats_ouvrages` (même fichier, ~l. 1654-1662) :
```python
siman_page = int(m.group(1)) if m else None
...
siman = (_num(m.group('s')) if m else None) or siman_page
```
Les deux motifs **exigent un mot-clé** (`או״ח`, `יו״ד`, `סימן`, `סי׳`) devant le numéro. La
page écrit le siman **collé au nom de l'ouvrage en toutes lettres** — « משנה ברורה שנ״ח
סק״ו » — sans aucun de ces mots-clés. Aucun des deux motifs ne mord, `siman` retombe sur
`siman_page`, et `siman_page` vaut **359** parce que le fichier est dans `siman-359/`.
La porte est allée chercher le ס״ק ו du siman **de la page** au lieu du siman **de la
référence**.

C'est le symétrique exact du piège nommé dans `CLAUDE.md` à propos de
`verifier-etiquettes.py` — « או״ח ne désigne pas toujours le Choul'han Aroukh » : ici c'est
**le repli sur le siman de la page qui écrase un siman explicitement écrit**. Le repli est
légitime (« une page de siman qui écrit הט״ז (ס״ק א) parle du Taz de SON siman », dit la
docstring) ; ce qui manque, c'est qu'il **ne s'applique que faute de siman nommé**, et la
forme « <nom d'ouvrage en toutes lettres> <numéral> » n'est pas reconnue comme un siman
nommé.

### 3.2 Une asymétrie observée, non diagnostiquée

Les **trois** citations de ce bloc emploient la même forme de référence
(`משנה ברורה שנ״ח סק״…`), et **deux seulement** sont sorties en `NON_RESOLU` : le
« סקי״א » de la ligne 411 n'apparaît pas dans le CSV. Je **n'ai pas** établi pourquoi
— l'hypothèse la plus simple est que la forme du numéral diffère (`סק״ו` / `סק״ח`, une
lettre avec gershayim interne, contre `סקי״א`, deux lettres), mais **je ne l'ai pas
éprouvée** et je ne peux pas la relancer dans ce lot (règle 3). À reprendre.

> **Éprouvée par un arbitre, 2026-10-01 — l'hypothèse est juste, et la cause est plus
> large que l'asymétrie qu'elle explique.** Il n'était pas nécessaire de relancer le
> script : il suffit de lire `RE_SK_NU` (`scripts/verifier-citations.py:1452`) et de
> l'essayer sur les trois chaînes réelles, ce qui n'écrit rien dans le cache partagé.
>
> `RE_SK_NU = (?<![א-ת])(?:ס["״]?ק|סעיף\s*קטן)(?![א-ת])\s*(?P<sk>…)`. Résultat mesuré :
> `(משנה ברורה שנ״ח סק״ו)` → capture `״ו` · `(משנה ברורה שנ״ח סק״ח)` → capture `״ח` ·
> **`(משנה ברורה שנ״ח סקי״א)` → AUCUN MATCH.** La cause n'est pas « deux lettres » : c'est
> que le garde-fou de frontière de mot `(?![א-ת])` — écrit pour empêcher `סק` de mordre à
> l'intérieur de `סקירה` ou `סקילה`, ce qu'il fait très bien — **rejette aussi toute forme
> compacte où le numéral commence par une LETTRE collée à `סק`.** `סק״ו` passe (le
> caractère suivant est un gershayim) ; `סקי״א` est rejeté (le caractère suivant est `י`).
>
> **Deux corrections de localisation :** la citation `סקי״א` est à la ligne **411**, non
> 409 (la ligne 409 est de la prose française et ne porte aucune citation) ; les trois
> références du bloc sont donc aux lignes 404, 411 et 412.
>
> **Étendue mesurée dans `sources/` : 89 occurrences, 58 fichiers, 17 formes distinctes**
> (Chabbat 80 · Yoré Déa 6 · Orah Haïm 3) — `סקי״ד` ×20, `סקי״א` ×16, `סקי״ח` ×12,
> `סקי״ג` ×6, puis `סקכ״א`, `סקכ״ד`, `סקכ״ו`, `סקכ״ח`, `סקל״ב`, `סקל״ג`, `סקל״ח`,
> `סקמ״א`, `סקמ״ג`. Le compte exige un gershayim ou un geresh dans le numéral, faute de
> quoi `סקירה` (×43), `סקילה` (×36) et `סקירת` (×30) entrent dans le chiffre : un premier
> comptage sans ce filtre annonçait 225 et était faux. **Ce qui est établi est la cécité
> du DÉTECTEUR de ס״ק sur ces 89 occurrences ; la conséquence en aval sur le verdict rendu
> à chacune n'a pas été tracée.**

---

## 4. Synthèse chiffrée des trois piles

| pile | taille | échantillon | signal (à corriger) | bruit (faux positif) |
|---|---|---|---|---|
| `ancrage-candidats.txt` | 152 occurrences / **63 couples** / 0 en Orah Haïm | **14 sites** (26 couples, 61 occurrences) | **5 / 14 défauts réels** · + 3 éclairantes légitimes | **6 / 14** |
| 11 verdicts graves (Chabbat) | 11 — **pile entière** | **11 / 11** | **1 fabrication** + **4 mal adressées** | **6 / 11** *(dont 3 manquements de convention)* |
| « ס״ק 359 inexistants » | 2 — **pile entière** | **2 / 2** | **0** | **2 / 2** |

**Les trois piles méritent d'être lues.** Aucune n'est à neuf dixièmes du bruit. La plus
dense est celle de l'ancrage (36 % de défauts réels, et les défauts qu'elle trouve sont
sérieux — un bloc entier du siman 168 décalé de cinq séifim, un ס״ק à dix-huit
séifim de son séif au 201 — chiffre corrigé par un arbitre, le relevé écrivait 58). La plus trompeuse est celle des « verdicts les plus graves » :
elle porte le nom le plus alarmant du dispositif et **une seule de ses onze lignes est une
absence réelle**, laquelle est une erreur de terme et non une halakha inventée.

**Deux réparations de porte ressortent de ce tri et rendraient le plus :**
1. `verifier-ancrage.py` — les quatre familles de faux positifs de §1.4 sont mécanisables
   (plusieurs étiquettes dans la phrase · étiquette-renvoi · étiquette **dans** la citation ·
   étiquette gouvernant le seul premier ס״ק). Elles font 6 faux positifs sur 6.
2. `verifier-citations.py` — (a) reconnaître « <ouvrage en toutes lettres> <numéral> » comme
   un siman nommé, pour que le repli sur `siman_page` cesse d'écraser une adresse écrite
   (§3.1) ; (b) confronter une plage de dafim sur **toutes** ses bornes et sur leur
   concaténation, faute de quoi aucune citation à cheval sur deux dafim n'est trouvable
   (§2.3, cas 320).

---

## 5. Ce que je n'ai PAS fait

- **Aucune page de `sources/` n'a été modifiée.** Aucun `git add`, aucun commit. Ce fichier
  est le seul écrit dans le dépôt.
- **`verifier-citations.py` n'a pas été lancé** (règle 3) : le CSV a été lu. Mon cache
  Sefaria est privé (scratchpad) ; `scripts/.cache-sefaria` n'a pas été touché.
- **Je n'ai pas ouvert les 138 autres occurrences** (37 des 63 couples) de la pile
  d'ancrage. Le taux de 36 % est **lu sur 14 sites**, et toute projection à 63 est une
  extrapolation que j'ai signalée comme telle.
- **Je n'ai pas tranché les 93 candidats de `verifier-etiquettes.py` ni les 12 candidats
  de son balayage Chabbat** — hors mandat de ce lot.
- **Je n'ai pas tranché les TROUS et COUPURES** de `verifier-troncatures.py` (5+91 Chabbat,
  22+1 354 Yoré Déa) : la mesure de leur rapport signal/bruit reste entièrement à faire, et
  c'est de loin la plus grosse pile du dispositif.
- **Je n'ai pas vérifié si les écarts d'ancrage de Yoré Déa 168 vont au-delà des ס״ק ס״ח et
  ס״ט** (le décalage de +5 pourrait courir sur tout un bloc du siman) ; j'ai constaté deux
  étiquettes consécutives décalées, pas l'étendue du bloc.
- **Je n'ai pas diagnostiqué** pourquoi « משנה ברורה שנ״ח סקי״א » a échappé au défaut qui a
  frappé « סק״ו » et « סק״ח » sur la même page (§3.2) — hypothèse formulée, non éprouvée.
- **Je n'ai pas évalué** si les condensations mises entre guillemets (§2.3 : simanim 269,
  296, 310) sont halakhiquement justes ; j'ai seulement établi qu'elles ne sont pas des
  fabrications. La convention du dépôt exempte la condensation du verbatim, **pas de la
  vérité** : ce tri reste au lecteur rabbinique.
