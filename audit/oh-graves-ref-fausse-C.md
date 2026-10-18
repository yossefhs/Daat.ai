# Orah Haïm — verdicts graves, lot C
## Le dernier tiers des REF_FAUSSE (lignes 51→74 du tri) + les 16 NON_RESOLU

Relevé source : `audit/citations-sources-orah-haim.csv`.
Sélection déterministe : lignes dont `verdict == REF_FAUSSE`, triées par (fichier, ligne),
rangs **51 à 74 inclus** — soit **24 verdicts**, le tri en comptant 74.

- Première ligne du lot : `sources/orah-haim/siman-81/index.html:449` — « בני מעים מסריחים » (סוכה מ״ב.)
- Dernière ligne du lot : `sources/orah-haim/siman-99/niveau-3-synthese.html:467` — « אל תתן את אמתך לפני בת בליעל » (ברכות ל״א.)

Puis les **16 NON_RESOLU**, seconde moitié du mandat.
**Total ouvert et tranché : 40 cas.**

Méthode : Sefaria interrogé **en direct par `urllib`/curl**, cache privé dans mon scratchpad.
`verifier-citations.py` n'a **jamais** été lancé (cache partagé). **Aucun fichier de `sources/`
n'a été modifié.** Aucun `git add`, aucun commit.

---

## 1. Compte par famille

| Famille | REF_FAUSSE (24) | NON_RESOLU (16) | Total |
|---|---|---|---|
| 1 — Fabrication réelle | **0** | 0 | **0** |
| 2 — Citation réelle mal adressée | 16 | 0 | **16** |
| 3 — Faux positif de la porte | 6 | 15 | **21** |
| 4 — Hors convention | 2 | 0 | **2** |
| Non tranché | 0 | 1 | **1** |

**Aucune fabrication dans ce lot.** Les 40 textes hébreux examinés existent tous, mot pour
mot, dans une source que j'ai obtenue moi-même de Sefaria. Ce qui est en cause est **l'adresse**,
jamais le texte.

### Le ktiv haser/malé — la cause que le mandat demandait de chercher spécialement

Mesure décisive, faite sur les 24 REF_FAUSSE : j'ai recomparé chaque citation au texte du
`ref` cité **en neutralisant les matres lectionis des deux côtés** (tous les ו et י retirés).
**Résultat : 0 cas sur 24 change de verdict.** Le ktiv n'explique AUCUN REF_FAUSSE de ma
tranche, et il faut le dire aussi nettement que l'inverse aurait été dit.

Deux choses vraies à côté de ce zéro, et qui comptent :

1. **`norm()` ne neutralise PAS le ktiv**, contrairement à ce qu'annonce sa propre docstring
   (« orthographes pleine/défective »). `_SUBS` ne contient que `אלהים/אלקים`,
   `אלוקים/אלקים` et `ירושלים/ירושלם`. Donc la porte EST exposée au faux positif dominant
   du dépôt ; ma tranche n'en porte simplement pas d'exemple causal. Cas témoin que j'ai
   mesuré : « ברב עם הדרת מלך » (ktiv haser, celui du verset) contre Megillah 27b, qui écrit
   « ברוב » (malé) → sous-chaîne absente, ratio 0,92 → **VARIANTE**, pas REF_FAUSSE. Un seul
   vav suffit à faire chuter un verbatim sous le seuil quand la citation est plus courte.
2. **Le ktiv a frappé à l'INTÉRIEUR de la porte**, et c'est la trouvaille la plus rentable du
   lot : la table `OUVRAGES` n'écrit l'Aroukh HaChoul'han qu'en **malé** —
   `ערוה["״]ש|ערוך השולחן`. Or le dépôt écrit massivement **haser** :
   **5 567 occurrences de « ערוך השלחן » contre 1 095 de « ערוך השולחן »** dans
   `sources/orah-haim/` (plus 857 sigles `ערוה״ש`, qui eux matchent). Toute citation de
   l'Aroukh HaChoul'han écrite dans la forme majoritaire du dépôt est donc invisible à la
   table — et son numéro de séif est annexé par l'ouvrage voisin. C'est exactement le
   NON_RESOLU n° 7 ci-dessous.

---

## 2. Les 24 REF_FAUSSE, un par un

### 2.1 Famille 2 — citation réelle, MAUVAISE ADRESSE (16 cas)

#### [51] `sources/orah-haim/siman-81/index.html:449` et [52] `…/siman-81/niveau-1-base.html:608`
Citation : **« בני מעים מסריחים »** · adresse de la page : **(סוכה מ״ב.)**

Ce n'est pas une phrase talmudique. Sefaria ne la connaît qu'en **un** endroit :
**שולחן ערוך הרב, אורח חיים פ״א:ב** — verbatim. Le ט״ז או״ח פ״א ס״ק א en porte la variante
« מעיו מסריחים ». J'ai lu Sukkah 42a et 42b en entier : ni la phrase, ni même le mot
« מסריחים » n'y figurent (0 occurrence), ni dans Berakhot 25a.
Gravité : un **טעם des Aharonim** (l'Admour HaZaken) est donné au lecteur comme la parole de
la guemara. Adresse vraie à écrire : **שו״ע הרב או״ח פ״א:ב**.
Note : la même parenthèse (סוכה מ״ב.) est de toute façon fausse d'un amoud pour le passage
voisin — la clause « יכול לאכול כזית דגן » est sur **Sukkah 42b**, pas 42a.

#### [53] `sources/orah-haim/siman-81/niveau-3-synthese.html:593`
Citation : **« כזית דגן בכדי אכילת פרס »** · adresse de la page : **(ברכות כ״ה.)**

Adresse vraie : **Sukkah 42b** — « יָכוֹל לֶאֱכוֹל כְּזַיִת דָּגָן — מַרְחִיקִין מִצּוֹאָתוֹ…
אָמַר רַב חִסְדָּא: וְהוּא שֶׁיָּכוֹל לְאוֹכְלוֹ בִּכְדֵי אֲכִילַת פְּרָס ». Berakhot 25a ne
contient ni « כזית דגן » ni « בכדי אכילת פרס » (0 occurrence chacune).
Aggravant : **la page se contredit d'un niveau à l'autre** — l'index et le niveau 1 du même
siman donnent, pour la phrase sœur, le bon traité (סוכה), et c'est le niveau 3 qui écrit ברכות.
Secondaire : la chaîne citée **soude deux clauses distinctes** (la baraïta, puis Rav Hisda) sans
« … », ce que la convention exige.

#### [54] `sources/orah-haim/siman-82/niveau-1-base.html:608`
Citation : **« נפרכת על ידי גלילה »** · adresse de la page : **(ברכות כ״ה.)**

Adresse vraie : **la glose du Rama sur שו״ע או״ח פ״ב:א** — « הגה וי״א דלא הוי כעפר רק אם
**נפרכת על ידי גלילה** בלא זריקה וכן עיקר » — c'est-à-dire **le siman même de la page**.
La guemara Berakhot 25a dit « כל זמן שזורקה ואינה נפרכת. ואיכא דאמרי: כל זמן שגוללה ואינה
נפרכת » : même idée, autres mots (ratio tolérant au ktiv : 0,80 — ce n'est pas une affaire
d'orthographe). Adresse vraie à écrire : **רמ״א או״ח פ״ב:א**.
Non signalé par la porte mais du même défaut, sur la même ligne : « שאם יזרקנה תתפרך » est le
Mehaber de או״ח פ״ב:א, pas Berakhot 25a non plus.

#### [56] `sources/orah-haim/siman-83/niveau-2-lamdan.html:542` et [58] `…:577`
Citation : **« הזמנה מילתא היא (או לאו מילתא) »** · adresse : **(ברכות כ״ו.)**

La **sougya** est bien là : Berakhot 26a, segment 5 — « וְהָא מִיבְּעֵי לֵיהּ לְרָבִינָא:
הִזְמִינוֹ לְבֵית הַכִּסֵּא, מַהוּ? **יֵשׁ זִימּוּן, אוֹ אֵין זִימּוּן?** ». **Les mots, non** :
« הזמנה » ne paraît pas une seule fois sur ce daf. La formule est verbatim dans
**מנחות ל״ד:** (« וּלְמַאן דְּאָמַר הַזְמָנָה מִילְּתָא הִיא ») et chez **רש״י סנהדרין מ״ח. ס״ז
וס״י** (« אלמא הזמנה מילתא היא »).
Pourquoi ces deux lignes-là sont mal adressées et non « hors convention » : elles mettent
explicitement les mots dans la bouche de la guemara — « **ובגמרא נחלקו** … «הזמנה מילתא היא או
לאו מילתא» » (542) et « **בגמרא ברכות כ״ו. נחלקו אם** «הזמנה מילתא היא» » (577).
Réparation honnête : citer « יש זימון או אין זימון » pour la guemara, et garder « הזמנה
מילתא » comme la *nomination* de la mahloket par les Richonim.

> **Candidat de contenu, hors mandat, à vérifier par un lecteur** : la ligne 542 attribue la
> mahloket à « (פליגי בה **רב אחא ורבינא**) ». Berakhot 26a:5 la donne comme une בעיא de
> **Ravina seul** ; je n'ai trouvé aucun רב אחא sur ce daf. Aucune porte ne regarde cela.

#### [63] `sources/orah-haim/siman-87/niveau-2-lamdan.html:469` et [64] `…:483`
Citation : **« והיה מחניך קדוש »** · adresse : **(ברכות כ״ה:)**

Le verset est **דברים כ״ג:ט״ו**, et la guemara le cite à **Berakhot 25a:11** (« הָכָא,
״וְהָיָה מַחֲנֶיךָ קָדוֹשׁ״ אָמַר רַחֲמָנָא, וְהָא לֵיכָּא ») — **verbatim, ratio 1,00**.
Sur Berakhot **25b**, le mot « מחניך » ne paraît pas (0 occurrence).
Nuance due à la page : la sougya qu'elle expose — גרף של רעי ועביט של מי רגלים — est bien sur
25b. Le daf est donc juste pour la *halakha* et faux d'un amoud pour le *verset cité*.
Réparation : **(דברים כ״ג:ט״ו, וברכות כ״ה.)**.

#### [66] `sources/orah-haim/siman-90/niveau-2-lamdan.html:469`
Citation : **« ברב עם הדרת מלך »** · adresse : **(ברכות ו׳.-ח׳. · מגילה כ״ט.)**

C'est **משלי י״ד:כ״ח** verbatim (« בְּרׇב־עָם הַדְרַת־מֶלֶךְ »), que le Talmud cite en ktiv
haser à **יומא ע׳.** (seg. 10) et **פסחים ס״ד:** (seg. 15), et en ktiv malé (« ברוב ») à
**מגילה כ״ז:** (seg. 4) et **ראש השנה ל״ב:** (seg. 19).
J'ai lu **tout l'intervalle annoncé** — Berakhot 6a, 6b, 7a, 7b, 8a : **0 occurrence** de
« עם הדרת מלך ». Megillah 29a : **0** également.
**Réserve à donner avec ce verdict** : la ligne est une LISTE — « ברכות ו׳.-ח׳. · מגילה כ״ט. ·
«ברב עם הדרת מלך» · «אין הקב״ה מואס בתפלתן של רבים» · «אין גבהות לפני המקום» » — où les
références et les phrases-clefs sont juxtaposées sans appariement un à un. Mais l'appariement
est bien ce que la forme invite à lire, et **deux des trois phrases ne sont pas où la liste les
met** : la deuxième EST à **Berakhot 8a:4** (donc dans l'intervalle, correcte), la troisième est
à **Berakhot 10b:27** (hors de l'intervalle).

#### [67] `sources/orah-haim/siman-93/niveau-2-lamdan.html:533`
Citation : **« כדי שיכוין לבו למקום »** · adresse : **(ברכות ל׳:)**

Verbatim dans **שולחן ערוך או״ח צ״ג:א** : « ישהא שעה א׳ קודם שיקום להתפלל **כדי שיכוין לבו
למקום** » — **le siman même de la page**. La michna de Berakhot 30b dit « חֲסִידִים הָרִאשׁוֹנִים
הָיוּ שׁוֹהִין שָׁעָה אַחַת, וּמִתְפַּלְּלִין… » et ne porte pas « שיכוין » (0 occurrence).
Le titre de section mélange les deux registres : il nomme « חסידים הראשונים » — la michna — et
cite les mots du Mehaber sous la référence de la michna. Adresse vraie : **שו״ע או״ח צ״ג:א**.

#### [69] `sources/orah-haim/siman-96/niveau-2-lamdan.html:539`
Citation : **« מפני שלבו עליהם שלא יפלו »** · adresse : **(ברכות כ״ג:)**

Verbatim dans **שו״ע או״ח צ״ו:א** (et טור או״ח צ״ו) : « …וככר **מפני שלבו עליהם שלא יפלו**
ויטרד ותתבטל כוונתו ». Berakhot 23b porte bien la baraïta « תָּנוּ רַבָּנַן: לֹא יֹאחַז אָדָם
תְּפִילִּין בְּיָדוֹ וְסֵפֶר תּוֹרָה בִּזְרוֹעוֹ וְיִתְפַּלֵּל… אָמַר שְׁמוּאֵל: סַכִּין וּמָעוֹת
וּקְעָרָה וְכִכָּר, הֲרֵי אֵלּוּ כַּיּוֹצֵא בָּהֶן » — **mais ne donne aucune raison** : le mot
« לבו » n'y paraît pas (0 occurrence). La raison est celle de Rachi, reprise par le Tour et le
Mehaber. Réparation : **(שו״ע או״ח צ״ו:א, ומקור הדין בברכות כ״ג:)**.

#### [70] `sources/orah-haim/siman-98/niveau-2-lamdan.html:503`
Citation : **« חסידים ואנשי מעשה »** · adresse : **(ברכות ל׳:)**

Verbatim dans **שו״ע או״ח צ״ח:א** : « וכך היו עושים **חסידים ואנשי מעשה** שהיו מתבודדים
ומכוונין בתפלתם… ». Berakhot 30b dit « חֲסִידִים **הָרִאשׁוֹנִים** » — autre expression ;
« חסידים ואנשי מעשה » est la michna de **סוכה פ״ה מ״ד**. Adresse vraie : **שו״ע או״ח צ״ח:א**.
Non signalé par la porte, même ligne, même défaut : « כאלו שכינה כנגדו » (ברכות ל״א.) est aussi
le Mehaber de או״ח צ״ח:א, et n'est pas sur Berakhot 31a.

#### [71] `…/siman-99/niveau-2-lamdan.html:503` · [72] `…:513` · [73] `…:598` · [74] `…/niveau-3-synthese.html:467`
Citation : **« אל תתן את אמתך לפני בת בליעל »** · adresse : **(ברכות ל״א.)**

C'est **שמואל א׳ א׳:ט״ז** verbatim, et la guemara le cite avec la derachah de Rabbi Elazar à
**Berakhot 31b:4** : « ״אַל תִּתֵּן אֶת אֲמָתְךָ לִפְנֵי בַּת בְּלִיָּעַל״. אָמַר רַבִּי
אֶלְעָזָר: מִכָּאן לְשִׁכּוֹר שֶׁמִּתְפַּלֵּל, כְּאִילּוּ עוֹבֵד עֲבוֹדָה זָרָה » (ratio 1,00).
Sur **31a** : 0 occurrence.
**À la décharge de la page** : Berakhot 31a porte bien les derachot de Rav Hamnuna sur Hanna,
dont « ״וַיַּחְשְׁבֶהָ עֵלִי לְשִׁכֹּרָה״ — מִכָּאן שֶׁשִּׁכּוֹר אָסוּר לְהִתְפַּלֵּל ». La
*halakha* du siman est donc bien sourcée sur 31a ; c'est le *verset cité* qui est sur 31b.
Erreur d'un amoud, réelle : le lecteur qui ouvre ל״א. ne trouve pas le verset promis.
Réparation : **(שמואל א׳ א׳:ט״ז, ברכות ל״א:)**. **Quatre pages** — et comme l'hébreu est
partagé entre les trois langues, **douze fichiers**.

### 2.2 Famille 3 — FAUX POSITIFS DE LA PORTE (6 cas), et les deux mécanismes qui les produisent

#### Mécanisme A — **le résolveur ne lit pas le Tanakh, et la citation hérite du daf voisin**
4 cas : [59] `siman-84/niveau-2-lamdan.html:469`, [60] `…:741`, [65] `siman-87/niveau-2-lamdan.html:733`,
[68] `siman-94/niveau-2-lamdan.html:542`.

- [59][60] « ויקרא לו ה׳ שלום » — **la page donne elle-même sa source, collée à la citation :
  « (שופטים ו׳ כ״ד) »**. Juges 6:24 : « וַיִּבֶן שָׁם גִּדְעוֹן מִזְבֵּחַ לַיהוָה
  **וַיִּקְרָא־לוֹ יְהוָה שָׁלוֹם** » — verbatim **sous la normalisation de la porte elle-même**,
  qui réduit le Tétragramme à ה. La porte a opposé « שבת י׳. · שבת מ׳: », les deux dafim listés
  plus tôt sur la même ligne. **La page est juste.**
- [65] « והיה מחניך קדוש » — la page écrit « (דברים כ״ג) ». Deut. 23:15, verbatim. **La page est juste.**
- [68] « והתפללו אליך דרך ארצם » — le paragraphe est intitulé « שורש הדין — ברכות ל׳.
  **ומלכים א׳ ח׳** » et introduit la citation par « ומקרא מלא דיבר בו שלמה בתפילתו ».
  **מלכים א׳ ח׳:מ״ח** : « …**וְהִתְפַּלְלוּ אֵלֶיךָ דֶּרֶךְ אַרְצָם** אֲשֶׁר נָתַתָּה
  לַאֲבוֹתָם… » — verbatim. La porte a opposé le Rambam nommé dans la clause SUIVANTE.
  **La page est juste.**

Le script connaît son angle mort — son commentaire dit « Le résolveur ne lit pas le Tanakh ;
tant qu'il ne le lira pas, il doit se taire ici » — mais le garde-fou (`RE_VERSET`) ne se
déclenche que si la citation est **annoncée** par שנאמר / ואומר / דכתיב. Ici le verset n'est
annoncé par rien et **suivi de sa référence exacte** : le garde-fou passe à côté.
**Classe générale** : tout verset dont la page donne la référence sous la forme
« (livre chapitre verset) » sur une ligne qui nomme par ailleurs un daf.
**Réparation possible** : `TANAKH` existe déjà dans le script (introduit pour « (שמות ל״ד:ט״ז) »)
et `RE_PASSOUK` sait lire cette forme — il suffit que la référence de Tanakh **collée** à la
citation l'emporte sur un daf plus lointain, comme `ref_collee()` le fait déjà pour la guemara.

#### Mécanisme B — **le résolveur ne lit que la PREMIÈRE borne d'une plage de dafim**
2 cas : [61] `siman-85/niveau-2-lamdan.html:483`, [62] `…:542`.

La page écrit **« (ברכות כ״ד:-כ״ה.) »**, une plage. Le verset « והיה מחניך קדוש » est
**verbatim, ratio 1,00, à Berakhot 25a:11** — c'est-à-dire **à la seconde borne**.
`RE_DAF_HE` exige le nom du traité immédiatement avant le numéral : il capte « ברכות כ״ד: » et
s'arrête ; « כ״ה. » n'a pas de traité à lui, donc n'est jamais résolu. La porte a confronté la
citation au seul 24b, où elle n'est pas, et l'a déclarée mal adressée. **La page est juste.**

C'est **mot pour mot le défaut du tiret de plage déjà documenté pour
`verifier-etiquettes.py`** (« או״ח רמ״ב:א — אין » lu « séif 1 à 61 »), retrouvé dans un second
script. Une plage de dafim, de ס״ק ou de séifim doit être **développée en ses deux bornes** avant
toute confrontation, partout.

### 2.3 Famille 4 — HORS CONVENTION (2 cas)

[55] `sources/orah-haim/siman-83/niveau-2-lamdan.html:485` · [57] `…:568`

**« הזמנה מילתא היא »** y figure en position de **titre** : un `<li>` de sommaire
(« הזמנה ועשייה — «הזמנה מילתא היא», כנגדו מותר בתוכו אסור ») et un `<h2 class="section-title">`.
Dans les deux cas la formule **nomme la mahloket**, elle ne la cite pas — c'est exactement
l'espèce que la porte exempte explicitement par ailleurs (« entre guillemets, « תשמישי קדושה »
ou « אמירה לנכרי שבות » sont des termes techniques, pas des citations »), à ceci près qu'elle
dépasse `MIN_LETTRES` (13 lettres) et n'est donc pas exemptée.
Un terme d'art lamdanique de plus de douze lettres est le trou de ce seuil. Reprocher à un titre
de ne pas être verbatim serait une fausse trouvaille ; mais puisque les guillemets sont réservés
au verbatim dans ce dépôt, **la forme juste serait sans guillemets** (ou en italique), et c'est
tout ce qu'il y a à corriger ici.

---

## 3. Les 16 NON_RESOLU — pourquoi la porte n'a rien confronté

Rappel de ce que vaut ce verdict : ce n'est **pas** une accusation contre une page, c'est un aveu
de la porte. Mais une citation non confrontée n'est confrontée **à rien**.

**Résultat d'ensemble, à dire d'abord : sur les 16, j'ai pu retrouver 15 citations, VERBATIM, à
l'adresse que la page donne elle-même.** Aucune n'est un défaut de contenu. La seizième ne peut
pas être tranchée parce que l'ouvrage n'est pas sur Sefaria.

| # | Fichier:ligne | `refs` fabriqué par la porte | Adresse VRAIE (vérifiée) | Motif |
|---|---|---|---|---|
| 1 | siman-138/niveau-2:630 | `Biur_Halacha.138` | **רמ״א על שו״ע או״ח קל״ח:א** — « ויכוין שיתחיל תמיד לקרא בדבר טוב **ויסיים בדבר טוב** » | source vide |
| 2 | siman-159/niveau-2:623 | `Turei_Zahav_on_…OH.159.40` | **שו״ע או״ח קנ״ט:י״ד** | ט״ז = 16 lu comme le Taz |
| 3 | siman-159/niveau-2:623 | idem | **שו״ע או״ח קנ״ט:ט״ז** | idem |
| 4 | siman-174/niveau-2:658 | `Berakhot.174b` | **שו״ע או״ח קע״ד:ד** | ברכות nom commun + « : » lu amoud ב |
| 5 | siman-217/niveau-2:582 | `Turei_Zahav_on_…OH.217.360` | **ט״ז על או״ח רי״ז** (seg. 2) | mot שני lu 360 |
| 6 | siman-218/niveau-2:681 | `Magen_Avraham.218.445` | **מגן אברהם רי״ח** (« ויש חולק. ») | mot תמה lu 445 |
| 7 | siman-221/niveau-2:665 | `Magen_Avraham.221.5` | **ערוך השלחן או״ח רכ״א:ה** | ktiv de la TABLE |
| 8 | siman-224/niveau-2:527 | `Magen_Avraham.224.90` | **מגן אברהם רכ״ד** (« חזר וראה. ») | mot מלך lu 90 |
| 9 | siman-237/niveau-2:636 | `Mishnah_Berurah.237.3` | אליה רבה רל״ז:ג — **absent de Sefaria** | ouvrage non numérisé |
| 10–15 | siman-239 ×6 | `Shulchan_Arukh,_OH.239.3` / `.239.6` | **מחצית השקל על או״ח רל״ט:ג** et **רל״ט:ו** | « X על או״ח N:M » donné au Mehaber |
| 16 | siman-96/niveau-2:623 | `Mishnah_Berakhot.300.10` | **שו״ע או״ח צ״ו:ב** | le mot פרק lu « פ » + « רק » = 300 |

### Les six mécanismes, et leur portée mesurée

**M1 — La source citée est VIDE sur Sefaria (cas 1). Particulier dans sa cause, général dans sa forme.**
`Biur_Halacha.138` répond HTTP 200, `ref = "Biur Halacha 138"`, `error = null`, et **0 segment**.
Vérifié que l'endpoint fonctionne : siman 1 → 4 segments, 139 → 2, 140 → 4, 242 → 6, 253 → 29.
Le Beour Halakha **ne commente pas tout** : un siman sans commentaire rend un corps vide, exactement
comme un siman que Sefaria ne numérise pas. Une lacune de l'ouvrage et un échec de mesure sont
alors indiscernables — c'est la même confusion que `verifier-ancrage.py` a dû apprendre à défaire.
La citation, elle, est réelle et **à son siman** : « ויסיים בדבר טוב » est verbatim dans la glose
du Rama sur או״ח קל״ח:א. La porte est allée chercher le Beour Halakha parce que la fenêtre
énumère les Aharonim (« מגן אברהם, ט״ז, פרי מגדים, משנה ברורה, **ביאור הלכה**, … »).
Secondairement : la phrase est dans un `<strong>` de titre, et le bloc est introduit par
`<em>תמצית:</em>` — donc **condensation**, hors convention de toute façon.

**M2 — « ט״ז » est à la fois le numéral 16 et le sigle du Taz (cas 2, 3). GÉNÉRAL.**
La page numérote ses séifim : « **י״ד:** הטביל ידיו במי מעיין… » puis « **ט״ז:** מ׳ סאה מים
שאובים… ». Ses deux étiquettes sont **exactes** (או״ח קנ״ט:י״ד et קנ״ט:ט״ז, vérifiés verbatim).
La porte a lu « ט״ז » comme le **טורי זהב**, puis a pris le premier nombre venu pour un ס״ק :
« מ׳ » — les **quarante seah du miqvé** — d'où `…159.40`, hors borne (le Taz sur 159 compte 21
segments). Double faute, et toutes deux générales : `ט״ז` étiquette de séif se présente partout
où une page découpe un siman de plus de quinze séifim, et `י״ד` collisionne de même avec יו״ד.
Le garde `_apres_deux_points` ne protège pas ici : il rejette un sigle **après** un deux-points,
et celui-ci est **avant**.

**M3 — « ברכות » nom commun lu comme le traité, et le « : » du dépôt lu comme amoud ב (cas 4). GÉNÉRAL, et mesuré.**
La page écrit « (קע״ד:ד) » — siman 174, séif 4 — et c'est **exact** (שו״ע או״ח קע״ד:ד contient
« וכן יין של קידוש **פוטר יין שבתוך המזון** », verbatim). Mais la même ligne finit par
« ובדיעבד פטור מספק **ברכות** (קע״ד:ד) » : `RE_DAF_HE` n'a **pas de frontière de mot à gauche**,
`ברכות` est dans `MASSEKHTOT`, `קע״ד` est un numéral hébreu valide et décroissant, le seul garde
est `d > 180` — et 174 passe. Le « : » du couple siman:séif devient l'amoud ב → **`Berakhot.174b`**.
Sefaria répond alors **HTTP 200, ref = "Berakhot", 2 749 segments : le traité entier** — le même
piège de livre entier que `Mishnah_Berurah_on_Shulchan_Arukh,_Orach_Chayim.N`. Le garde de queue
de `ref` l'a intercepté, d'où NON_RESOLU et non une comparaison contre tout Berakhot.
**Mesure** : 4 lignes d'Orah Haïm mettent « ברכות » immédiatement devant **le numéro de leur
propre siman** suivi de « : » ou « . » — `siman-174/niveau-2-lamdan{,-he,-en}.html:658` et
`siman-177/niveau-2-lamdan-he.html:514` (« שתי הברכות (קע״ז:ב) »). Une seule est dans ce CSV,
le balayage ayant porté sur le FR.
C'est la trappe de la guématrie que CLAUDE.md documente déjà (« ספק ברכות להקל » → Berakhot 165),
sous une forme neuve où le numéral est **légitime** et passe donc `gem()`.

**M4 — UN MOT HÉBREU ORDINAIRE LU COMME UN ס״ק (cas 5, 6, 8). GÉNÉRAL — c'est le mécanisme le plus rentable de mon lot.**
`RE_SIMAN_SEIF = (?P<s>[\dא-ת"״'׳]{1,6})\s*[:׃]\s*(?P<n>[\dא-ת"״'׳]{1,4})` n'exige **ni gershayim,
ni frontière de mot**. Elle lit donc n'importe quel **intitulé suivi de deux-points** comme
« siman:séif », et `gem()` ne rejette que les suites **croissantes** de plus de trois lettres —
si bien que tout mot de deux ou trois lettres à valeurs décroissantes devient un nombre :

| Page | Texte réel | Lu comme | Valeur |
|---|---|---|---|
| siman-217:582 | « **תירוץ:** שני דרכים בדבר » | תירוץ : **שני** | ש300+נ50+י10 = **360** |
| siman-218:681 | « …ומי הוא: **תמה** המגן אברהם » | הוא : **תמה** | ת400+מ40+ה5 = **445** |
| siman-224:527 | « …שלישית: **מלך** שני בתוך שלושים » | שלישית : **מלך** | מ40+ל30+ך20 = **90** |

Les trois valeurs correspondent **exactement** aux trois `refs` fabriqués. Les trois citations
sont verbatim chez l'ouvrage et au siman que la page nomme : la porte avait l'ouvrage **et** le
siman justes, et c'est le ס״ק inventé qui a tout annulé.
**Mesure de l'exposition dans Orah Haïm** : **446 lignes** portent à la fois un sigle de la table
`OUVRAGES`, **aucun** « ס״ק », et une étiquette-mot suivie de deux-points dont le mot suivant a une
guématrie valide. C'est un plafond d'exposition, pas un compte de défauts — le pseudo-ס״ק ne nuit
que s'il tombe dans la fenêtre de la citation. Je le donne comme tel.
**Réparation** : exiger un **gershayim** (ou des chiffres arabes) dans le groupe `n` de
`RE_SIMAN_SEIF`, comme `gem()` l'exige déjà ailleurs dans ce même script — et refuser un `s`
qui est un mot, c'est-à-dire qui n'est pas lui-même un numéral valide.

**M5 — Un ouvrage absent, ou mal orthographié, dans la table `OUVRAGES` (cas 7, 9, 10–15). GÉNÉRAL.**
Quand l'ouvrage réellement cité n'est pas lisible par la table, son **numéro** est annexé par
l'ouvrage voisin qui, lui, y figure. Trois espèces distinctes :

- **(a) ktiv de la table — cas 7.** La page écrit « (ערוך השלחן רכ״א:ה) », et la citation est
  verbatim dans **Arukh HaShulchan OH 221:5**. La table n'écrit l'ouvrage qu'en **malé**
  (`ערוה["״]ש|ערוך השולחן`) ; la page l'écrit en **haser**. L'Aroukh HaChoul'han est donc
  invisible, et le « ה » (5) de sa référence est annexé par le מגן אברהם, sujet du paragraphe
  → `Magen_Avraham.221.5` (MA 221 n'a que 2 segments).
  **Mesure : 5 567 « ערוך השלחן » haser contre 1 095 « ערוך השולחן » malé dans `sources/orah-haim/`.**
  La table manque la forme **majoritaire** du dépôt. Réparation d'une ligne : `ערוך הש[ו]?לחן`.
- **(b) ouvrage non numérisé — cas 9.** « (אליה רבה רל״ז:ג) ». Sefaria n'a **pas** l'Eliya Rabba
  sur le Choul'han Aroukh : la seule « Eliyahu Rabbah » qu'il serve est le commentaire sur les
  michnayot de Taharot. Rien ne peut confronter cette citation, et ce n'est pas un défaut de la
  table. Conséquence mesurable : **1 219 lignes d'Orah Haïm nomment אליה רבה ou א״ר**, et chacune
  de leurs citations est soit non confrontée, soit — comme ici — **annexée** par l'ouvrage voisin :
  « המשנה ברורה », nommée dans la clause SUIVANTE, a hérité du « רל״ז:ג », et MB 237 n'a que
  2 ס״ק. **C'est le seul des 40 cas que je ne tranche pas** : je ne peux pas dire si la citation
  est exacte.
- **(c) ouvrage absent mais DISPONIBLE — cas 10 à 15, et c'est la classe dangereuse.**
  Les pages écrivent « (מחצית השקל על אורח חיים רל״ט:ג) » et « (… רל״ט:ו) ». מחצית השקל ne figure
  pas dans la table ; en revanche `RE_SA_HE` reconnaît « **אורח חיים** רל״ט:ג » et donne la
  citation **au Mehaber lui-même** → `Shulchan_Arukh,_Orach_Chayim.239.3`. Le siman 239 n'ayant
  que **2 séifim**, le corps est vide et le verdict est NON_RESOLU — un échec **bruyant**, donc
  bénin. **Mais là où N:M existe dans le Choul'han Aroukh, le même mécanisme ne fait pas de bruit :
  il compare les mots d'un commentateur au texte du Mehaber et rend INTROUVABLE ou REF_FAUSSE
  contre une page qui a raison.**
  **Mesure : 138 endroits d'Orah Haïm écrivent une référence sous la forme « … על או״ח N:M » / « … על אורח חיים N:M ».**
  Les six citations sont verbatim à l'adresse annoncée, et Sefaria la sert :
  `Machatzit_HaShekel_on_Orach_Chayim.239.3` → « …דהברכה היא על טבע הבריאה ואפי׳ לא יישן אין
  ברכתו לבטלה » ; `…239.6` → « …ולענ״ד לק״מ דמי גרע מה שכבר קרא ק״ש… ».
  Réparation double : ajouter `מחצית השקל → Machatzit_HaShekel_on_Orach_Chayim.{s}.{n}` à
  `OUVRAGES`, **et** faire refuser à `RE_SA_HE` une correspondance précédée de « על » quand un
  ouvrage est nommé devant.

**M6 — Le mot « פרק » lu comme « פ » + le numéral « רק » (cas 16). GÉNÉRAL dans sa forme.**
La page écrit « **שורש הדין — רבינו יונה (ברכות פרק מי שמתו)** » — un chapitre nommé par son
incipit, qui est la façon normale de citer un Richon sur une sougya.
`RE_PEREK_MISHNAH` vaut `(mass)\s*פ["״'׳]?(?P<p>…)\s*,?\s*מ["״'׳]?(?P<m>…)`. Appliquée à
« ברכות **פרק מי** שמתו » : `mass` = ברכות ; le `פ` du motif mange le **פ de פרק** ; `p` = « רק »
= ר200+ק100 = **300**, décroissant donc accepté ; le `מ` du motif mange le **מ de מי** ; `m` = « י »
= **10**. D'où **`Mishnah_Berakhot.300.10`**, et Sefaria répond « Mishnah Berakhot ends at
Chapter 9 ». La citation, elle, est réelle : « הואיל ותופס לצורך תפלה עצמה » est verbatim dans
**שו״ע או״ח צ״ו:ב** (recherche Sefaria : deux témoins, tous deux או״ח צ״ו:ב), le Mehaber reprenant
Rabbenou Yona via le Beit Yossef — et Talmidei Rabbenou Yona n'est pas un ouvrage que Sefaria serve.
**Mesure : 18 occurrences dans Orah Haïm** d'un « massekhet פרק <nom> » produisant un perek > 9,
donc impossible. Réparation : un perek de michna ne dépasse pas la dizaine — borner `p`, et refuser
que le `פ` du motif consomme le `פ` du mot `פרק` (exiger une frontière, ou le gershayim de `פ״ג`).

---

## 4. Ce que je n'ai PAS fait

- **Aucune page de `sources/` n'a été modifiée.** Ce lot classe ; il ne corrige pas.
- **`verifier-citations.py` n'a pas été lancé** (cache partagé `scripts/.cache-sefaria` :
  quatre agents en parallèle). Je n'ai pas non plus **importé** le module, qui lit/écrit ce cache :
  j'ai **recopié** ses expressions régulières et sa fonction `gem()` dans un script de scratchpad
  pour reproduire ses lectures. Les trois valeurs 360 / 445 / 90 et le 300/10 sont donc des
  reproductions exactes de son comportement, non des conjectures.
- **Aucun texte hébreu n'a été reconstruit.** Chaque adresse affirmée ci-dessus vient d'une réponse
  de Sefaria obtenue par moi.
- **Je n'ai pas vérifié l'exactitude du cas 9** (אליה רבה רל״ז:ג) : l'ouvrage n'est pas sur Sefaria.
  Il reste **non tranché**, et ne compte dans aucune des quatre familles.
- **Je n'ai pas mesuré l'étendue hors d'Orah Haïm.** Tous les comptes de ce relevé
  (446 · 4 · 138 · 1 219 · 18 · 5 567/1 095) portent sur `sources/orah-haim/` seul. Les mêmes
  mécanismes doivent exister dans Hilkhot Chabbat et Yoré Déa ; je ne les ai pas comptés.
- **Les chiffres 446, 138, 1 219 et 5 567 sont des PLAFONDS D'EXPOSITION, pas des comptes de défauts.**
  Ils disent combien de lignes offrent le mécanisme, non combien de citations en souffrent — ce
  second nombre ne s'obtient qu'en rejouant la porte, ce que je n'avais pas le droit de faire.
  Je ne les annonce pas autrement.
- **Je n'ai pas réparé les 295 VARIANTE ni les 16 INTROUVABLE** d'Orah Haïm : ils ne sont pas de
  mon lot. Mais la mesure du ktiv ci-dessus (`norm()` ne neutralise pas les matres lectionis)
  prédit qu'une part des 295 VARIANTE n'est que du ktiv haser/malé, et cela se vérifie en une
  passe — hors de ce lot.
- **Candidat de contenu laissé ouvert, non tranché faute de mandat** : `siman-83/niveau-2-lamdan.html:542`
  attribue la mahloket de l'הזמנה à « רב אחא ורבינא » quand Berakhot 26a:5 la donne comme une
  בעיא de Ravina seul. Aucun garde-fou ne regarde cela.
