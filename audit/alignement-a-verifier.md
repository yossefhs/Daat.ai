# Alignement des blocs sur le Choul'han Aroukh — ce qui reste à trancher

Établi le 17 août 2026 par `scripts/verifier-alignement.py`, après ajustement du
garde-fou (voir sa docstring). 2359 blocs confrontés dans les 359 pages des trois
compartiments.

## Ce qui a été corrigé

**Orah Haïm 79, niveau 1** — deux blocs étaient numérotés d'après leur rang dans
la page et non d'après le Choul'han Aroukh. Leur hébreu est verbatim ; seul le
numéro était faux, et la traduction placée juste au-dessous portait déjà le bon
numéro, ce qui rendait la page contradictoire avec elle-même.

| Titre affiché | Séif réel | Vérification |
|---|---|---|
| « Séif 3 — la fiente des animaux » | **séif 4** | recouvrement 93 % au séif 4, 14 % au séif 3 |
| « Séif 4 — le ריח רע » | **séif 9** | recouvrement 93 % au séif 9, 36 % au séif 4 |

Corrigé dans les trois langues (titre + ancre `id`). Aucun mot du texte hébreu,
de la traduction ou de l'explication n'a été touché.

## Ce qui doit être tranché par le Rav — ne rien modifier sans son avis

**Yoreh De'ah 101, niveau 1, séifim 8 et 9.** Les deux blocs sont présentés en
`<blockquote class="text-source">`, avec bouton « Copier », donc comme le texte
du Choul'han Aroukh. Or leur hébreu ne se retrouve **nulle part dans le siman**
(recouvrement 15 % et 23 %, meilleur score tous séifim confondus), ni dans le
Tour Yoreh De'ah 101, ni dans le Chakh ou le Taz sur place — recherche faite sur
Sefaria le 17 août 2026.

La halakha énoncée est proche de celle de la source, mais **le cas n'est pas le
même**, et c'est ce qui interdit de corriger d'office :

| | Ce qu'affiche la page | Ce que dit le Choul'han Aroukh |
|---|---|---|
| **séif 8** | des **gésiers** se sont mélangés, l'un est טריפה ; on identifie l'interdit par la graisse qui le recouvrait | un **gésier trouvé percé**, et la **poule** dont il provient s'est mélangée à d'autres ; on compare la graisse du gésier à celle de la poule pour **permettre les autres** |
| **séif 9** | des **têtes d'agneaux** se sont mélangées, l'une est טריפה ; on identifie l'interdit par la coupe | une **tête trouvée טריפה** dont on ignore de quel agneau elle vient ; on ajuste la tête au cou de l'un d'eux, et si les coupes correspondent **יש לסמוך** |

Dans les deux cas la page pose la question « lequel est interdit ? » là où la
source pose « peut-on permettre les autres ? ». Remplacer l'hébreu par celui de
la source rendrait fausses les traductions et les explications placées
au-dessous, dans les trois langues : ce n'est pas une substitution mécanique.

Texte source, pour la confrontation :

- **YD 101:8** — קורקבן שנמצא נקוב ונתערבה אותה תרנגולת עם אחרות מדמין שומן שבקורקבן
  לשומן התרנגולת של מקום חיבור הקורקבן ואם דומים לגמרי מכשירים האחרות (וכן כל כיוצא בזה)
- **YD 101:9** — ראש כבש שנמצא טריפה ולא נודע מאיזה כבש הוא והקיפו הראש לצוארו של אחד
  מהכבשים ונמצאו החתיכות דומות ומכוונות יפה יש לסמוך

**Statut : `needs_rav_review`. Aucune modification faite.**

## Le plancher de bruit qui subsiste

14 autres signalements, tous sur des blocs **sans titre de séif** : baraïtot,
récapitulations de fin de page, citations de guemara que les filtres de contenu
n'attrapent pas. Ils ne sont pas des erreurs ; ils fixent le niveau au-dessus
duquel un décalage nouvellement introduit ressortirait.

    orah-haim  8   · shabbat 242 (×5), 243 · yoreh-deah 89, 90, 183, 187, 190 (×2), 200

## Ce qui a été écarté après vérification, et pourquoi

Le garde-fou rapportait 143 écarts avant ajustement. Trois mécanismes en
produisaient la quasi-totalité, chacun vérifié sur échantillon avant d'être
neutralisé :

1. **Le ktiv haser** (≈ 90 écarts). Les pages vocalisées écrivent אֲפִלּוּ,
   l'imprimé de Sefaria אפילו ; la comparaison littérale déclarait « introuvable »
   un séif recopié mot pour mot. Yoreh De'ah, entièrement vocalisé, en portait
   l'essentiel.
2. **Les blocs de commentateurs** (≈ 30). Un bloc sous « Taz s.k. 1 » n'a pas à
   figurer dans le Choul'han Aroukh ; il y était pourtant cherché, et son absence
   comptée comme écart — puis le bloc suivant comptait un « retour en arrière ».
3. **Les plages déclarées** (≈ 15). Une page qui titre « séifim 6-8, 16-21,
   23-24 » est explicite ; le contrôle n'en lisait que le premier nombre.

Trois sondages indépendants ont confirmé que la bande 55–69 % de recouvrement
est du **développement d'abréviations** et non une altération : Chabbat 269:1
(בבהכ״נ → בית הכנסת), Orah Haïm 154:2 (ב״ה → בית הכנסת), Yoreh De'ah 108:2
(בד״א → במה דברים אמורים). Dans les trois cas le texte est verbatim.

## Siman 250 (Chabbat) — attribution au Rambam non confirmée · `needs_rav_review`

`sources/shabbat/siman-250/niveau-2-lamdan.html`, ligne 395 (et les deux autres langues).

La page écrit :

> הרמב״ם (הלכות שבת פ״ל ה״ו) : "כיצד מכבדו ? כדי שיהא לו בגדים נקיים והיתה ערוכה
> לו השלחן ומסודרים מטה ומסבה והכלים הצריכים, וירבה בבשר וביין ומגדנות ככל יכלתו".

**Ce texte n'a pas été retrouvé** dans le Mishné Torah, Hilkhot Chabbat פרק ל׳ —
ni en ה״ו, ni ailleurs dans le chapitre (les trente segments ont été parcourus).
Ce que le Rambam écrit sur le sujet, en פ״ל ה״ה, est :

> וצריך לתקן ביתו מבעוד יום מפני כבוד השבת. ויהיה נר דלוק ושולחן ערוך לאכול
> ומטה מוצעת שכל אלו לכבוד שבת הן.

Le fond est le même ; la langue ne l'est pas. Il se peut que la page cite un autre
ouvrage — le Tour ou le Choul'han Aroukh sur רמ״ב, ou le Rambam sur les jours de
fête — mais **je n'ai pas pu l'établir**, et la règle anti-fabrication interdit de
proposer un remplacement au jugé.

**Aucune modification n'a été faite.** À trancher par le Rav : soit la référence
exacte, soit le passage en `<em>résumé</em> :` si c'est une condensation.

---

## Siman 320 — le séif ו (le citron) et la glose du Rama au séif א

`needs_rav_review` — signalé par le veilleur en août 2026, re-constaté en septembre.

Le Choul'han Aroukh écrit au séif ו, sans condition ni réserve :

> מותר לסחוט לימוני״ש

La synthèse (niveau 3) consacre au citron sa section 5, la plus développée du
niveau — « un seul et même fruit peut être permis ou interdit à presser, non selon
sa nature, mais selon là où le jus aboutit » — mais **ne cite nulle part le séif ו**,
c'est-à-dire la permission que le Choul'han Aroukh donne en propre.

En regard, la glose du Rama au séif א pose :

> ובמקום שנהגו לסחוט איזה פירות לשתות מימיו מחמת צמא או תענוג דינו כתותים ורמונים

Le citron d'aujourd'hui est pressé couramment pour en boire le jus. Savoir si cette
glose l'atteint, et comment elle se compose avec le séif ו, **est une question de
psak** : elle n'est pas tranchée ici.

**Ce qui a été fait :** l'encadré « Ce que dit ce séif » du séif ו rend la permission
verbatim et renvoie à la glose du Rama en la donnant à vérifier au Rav.
**Ce qui n'a pas été fait :** la synthèse n'a pas été touchée — ni son raisonnement,
ni sa conclusion.

---

## Siman 288 — le ta'anit halom : deux affirmations retirées

Signalé par l'utilisateur en septembre 2026, confronté aux sources et corrigé.

**1. « Permis Chabbat — car il sauve une vie ».** Le Choul'han Aroukh HaRav dit
l'inverse. En רפ״ח:ג il donne deux raisons, et aucune n'est le péril :

> אבל מותר להתענות תענית חלום בשבת כשחלם בו ביום, שיפה תענית לחלום לבטל הגזר דין
> כאש לנעורת אם מתענה בו ביום, **והתירו לו חכמים בשביל שיקרע גזר דינו**. **ועוד,
> לפי שאין כאן ביטול עונג שבת לגמרי, כיון שנפשו עגומה עליו בשביל חלומו אם לא
> יתענה** … אם כן **הרי התענית הזה תענוג הוא לו**.

Et en רפ״ח:ט il écarte le péril nommément :

> שהרי התירו אפילו להתענות על חלום **אף על פי שאין שם סכנת היום**

La page était donc contredite par sa propre source. Les trois langues disent
maintenant les deux raisons du Choul'han Aroukh HaRav, et non le péril.

**2. « La plupart des poskim contemporains ».** Aucune source du dossier ne
l'affirme. Le Choul'han Aroukh (רפ״ח:ה) et le Choul'han Aroukh HaRav (רפ״ח:ז)
donnent tous deux « בזמן הזה אין להתענות » comme **un** יש אומרים parmi plusieurs
qu'ils énumèrent. Le seul רוב du dossier est dans la Michna Beroura ס״ק ט״ו, et
il porte sur la pratique du של״ה — *« היה רגיל על הרוב לפסוק שלא להתענות בשבת »*,
ce que **lui** avait coutume de trancher — non sur le compte des décisionnaires.

Les dix occurrences (trois langues, niveaux 1 et 3) disent maintenant : un avis
rapporté, avec sa référence, plus la condition que la Michna Beroura pose —
`אין להתענות בשבת אלא אם כן התענית עונג לו` — et la conduite renvoyée au Rav.

**Ce qui reste à trancher par le Rav :** quelle est, en fait, la conduite reçue
aujourd'hui. La page ne le dit plus, et ne doit pas le redire sans qu'il l'ait
établi.

---

## Chabbat 289 — quatre points signalés par le Rav (septembre 2026)

Le texte hébreu des deux séifim était juste ; les quatre erreurs étaient dans
l'exposé pédagogique posé dessus. Toutes corrigées, dans les trois langues.

**1. Le jus de raisin n'est pas du hamar medina.** La page le rangeait avec la
bière, le whisky et le cognac. Or le séif ב ne parle que de
`שכר ושאר משקין חוץ מהמים` ; le jus de raisin, lui, est du **vin** — berakha
`בורא פרי הגפן`, apte au Kidoush comme le vin : או״ח רע״ב:ב,
`וסוחט אדם אשכול של ענבים ואומר עליו קידוש היום`, que notre propre page du
siman 272 enseigne déjà. Le contresens était pratique : on aurait fait `שהכל`
sur ce qui appelle `בורא פרי הגפן`. Le défaut vivait aussi au **siman 296**
(Havdala), où une ligne allait jusqu'à écrire que la berakha du jus de raisin
« n'est pas boré peri ha-gefen ». 36 remplacements, 15 fichiers.

**2. La quantité du « Kidoush bimkom seuda ».** La page donnait
« pat ka-beitsa de mezonot, ≈ 56 g de gâteau » comme une règle. Aucune source
ne parle ainsi ici : le Choul'han Aroukh écrit `אפילו אכל דבר מועט או שתה כוס
של יין שחייב עליו ברכה`, et `ודוקא אכל לחם או שתה יין אבל אכל פירות לא`
(רע״ג:ה) ; la Michna Beroura parle d'un `כזית` (רע״ג ס״ק ט). Le `כביצה` avait
été importé d'une autre halakha — il est bien dans les sources aux simanim 286
(Rama רפ״ו:ג) et 291, mais pas ici. Tout chiffre fixe est retiré du siman 289.

**3. L'étymologie de `קידושא רבה`.** La page l'attribuait à Pessahim ק״ו ע״א.
La guemara y emploie bien le nom — `ליקדיש לן מר קידושא רבה` — et y établit que
le Kidoush du jour n'est que `בורא פרי הגפן`, **mais elle n'explique pas le
nom**. L'explication est des Rishonim : le Méiri en donne deux,
`והוא הנקרא קדושא רבה דרך כנוי או שמא על שם שכל הברכות מתעטרות בו`, et le
Rashbam retient la seconde, `וקרי ליה קידושא רבא דאכולהו קידושי קאמרי ליה`.

**4. L'eau avant la tefila.** La page écrivait que « l'eau ne déclenche pas
l'obligation ». La raison du Mehaber est nommée dans le séif lui-même :
`מפני שעדיין לא חל עליו חובת קידוש` — l'obligation ne s'est **pas encore**
appliquée à lui. Le Choul'han Aroukh HaRav dit de même (רפ״ט:ב).

### Ce qui reste à trancher par le Rav

L'équivalence **`כביצה` ≈ 56 grammes**, employée aux simanim **286** et **291**
(21 et 6 occurrences). La mesure `כביצה` y est bien dans les sources ; c'est sa
conversion en grammes qui est donnée sans attribution, alors que les shiourim
retenus varient d'un décisionnaire à l'autre. Rien n'a été changé là-bas : la
question est halakhique, pas rédactionnelle.
