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

---

## Chabbat 290 — cinq points signalés par le Rav (9 septembre 2026)

Le texte hébreu des deux séifim était juste, et le **niveau 2 était déjà correct**
sur l'attribution — ce sont les niveaux 1 et 3 qui s'en écartaient. Le schéma
habituel du dépôt, une fois de plus : l'erreur naît dans la couche pédagogique.

**1. L'attribution des cent berakhot.** La page donnait « halakha de David
HaMelekh (Menahot 43b) ». Menahot מ״ג ע״ב l'énonce au nom de **Rabbi Meïr** :
`תניא, היה רבי מאיר אומר: חייב אדם לברך מאה ברכות בכל יום`. La takana de David
est ailleurs — le **Tour** או״ח מ״ו la rapporte au nom de **Rav Netronaï Gaon** :
`והשיב רב נטרונאי… דהע״ה תקן מאה ברכות`. Le niveau 2 renvoyait à « טור ושו״ע
סי׳ מ״ו » : le Choul'han Aroukh מ״ו:ג ne donne que l'obligation, sans
l'attribution — `חייב אדם לברך בכל יום מאה ברכות לפחות`.

**2. « Dire ou répondre Amen ».** La baraïta dit `חייב אדם לברך` — prononcer.
Que des berakhot entendues comptent dans des cas précis est un avis de
décisionnaires ; la page l'énonçait comme la définition de l'obligation. La
ligne pratique renvoie désormais la question au Rav.

**3. Le calcul.** La page annonçait « ≈ 18-22 » tout en posant 4 × 7 = 28 contre
3 × 19 = 57, ce qui fait **29**. Le niveau 2 du même siman écrivait déjà
`חיסור: כ-29 ברכות`. Aucun chiffre final n'est plus avancé : la Michna Beroura
(ר״צ ס״ק ב) dit seulement `שנחסר לו כמה ברכות שבתפלת שבת יש רק ז׳ ברכות וע״כ
ישתדל להשלימם`, sans cadrer de total.

**4. Le raisin.** « raisin (ha-gefen non-Kidoush) » était faux : un raisin frais
se bénit `בורא פרי העץ`. Michna Berakhot ו׳:א — `על פירות האילן אומר בורא פרי
העץ, חוץ מן היין, שעל היין אומר בורא פרי הגפן`. `בורא פרי הגפן` est pour le vin
et le jus de raisin.

**5. « Chaque odeur = une berakha ».** C'est chaque **catégorie**, non chaque
bouffée. או״ח רי״ז:א — `ישב שם כל היום אינו מברך אלא אחת`, et même en sortant
et rentrant, `היה דעתו לחזור לא יברך` ; et או״ח רט״ז:א — `אבל לאחריו אין צריך
לברך`.

**6. Trouvé en vérifiant** (le garde-fou de citations l'a signalé) : le derash
`אל תקרא מה אלא מאה` était placé À L'INTÉRIEUR de la citation de la guemara.
Il est de **Rachi** sur place : `מה ה׳ אלהיך וגו׳ — קרי ביה מאה`. Et Rachi, deux
mots plus loin, donne la raison même de ce siman : `בשבתות וימים טובים — דלא
מצלו י״ח`, puis `טרח וממלא להו — למאה ברכות`, `באספרמקי ומגדי — אספרמקי בשמים
ומגדי מיני מגדים שטעונים ברכה`. Le récit de Rav Hiya fils de Rav Avya —
`בשבתא וביומי טבי, טרח וממלי להו באיספרמקי ומגדי` — figure désormais au
niveau 2 et à la synthèse : c'est la source directe du siman, et elle manquait.

---

## Trois corrections trouvées par le garde-fou de cohérence (10 septembre 2026)

`scripts/verifier-coherence.py` est né de la signature commune aux simanim 288,
289 et 290 : **un niveau de la page portait déjà la bonne réponse pendant qu'un
autre en publiait une fausse**. Validé sur le 290 d'avant correction, il y voit
les deux défauts et sort à zéro une fois corrigés. Il a ensuite trouvé ceci :

**1. Siman 290 — deux chiffres résiduels.** La correction de la veille avait
retiré le « ≈ 18-22 » mais laissé « Souvent on arrive à 80 — manque ≈ 20 »
(niveau 1) et « déficit Shabbat ≈ 20 » (niveau 3). Ni 80 ni 20 ne viennent
d'une source. La méthode de comptage reste ; les totaux inventés s'en vont.

**2. Siman 344 — la mahloket de שבת ס״ט ע״ב.** Le niveau 1 annonçait « une
discussion célèbre entre Rav Houna et **Rava** ». La guemara oppose רב הונא à
`חייא בר רב` — `אמר רב הונא… מונה ששה ימים ומשמר יום אחד; חייא בר רב אומר:
משמר יום אחד ומונה ששה`. Rava figure bien sur la page, mais sur une tout autre
question. Les niveaux 2 et 3 portaient déjà la bonne paire.

**3. Siman 324 — « מחלוקת רב ושמואל » revenu deux fois.** La correction
précédente avait rectifié le titre de section mais laissé le sommaire et la
ligne d'introduction, où un lien intra-ref coupait le nom en deux et le
soustrayait à toute recherche. La guemara (שבת קנ״ה ע״ב) est sans ambiguïté :
`אין נותנין מים למורסן, דברי רבי. רבי יוסי בר יהודה אומר: נותנין מים למורסן` —
et שמואל ne figure ni dans קנ״ה ע״ב ni dans קנ״ו ע״א.

### Le tri, fait (10 septembre 2026)

Les quarante-quatre candidats ont été ouverts un par un, daf par daf. **Aucun
n'était une erreur.** Le détail vaut d'être gardé, parce qu'il dit ce que ce
genre de contrôle peut et ne peut pas :

  · Les dix « nom absent du daf » vérifiés à la main donnaient tous raison à la
    page — 287 (רבי מאיר est bien à שבת י״ב ע״א, comme la page l'écrit), 292
    (דוד המלך appartient au midrash que la page nomme), 305 (Tossafot sur
    עירובין מ״ו discute l'avis de רבי שמעון, qui n'a pas à figurer sur le daf),
    248 (la mahloket Rabbi/Rashbag est dans la braïta de שבת י״ט que la page
    cite en premier), et cinq d'Orah Haïm où le nom appartenait à la référence
    voisine, celle que la page lui donne.
  · Les seize divergences entre niveaux qui subsistent ont, des DEUX côtés, des
    noms réellement présents sur le daf cité : deux niveaux qui parlent de deux
    passages d'une même page ne se contredisent pas.

Ce tri a fait apparaître six fautes du contrôle lui-même, toutes corrigées et
commentées dans le script : « Rabban Gamliel » lu comme l'amora Rabba,
« הַרְבֵּה » lu de même, la référence entre parenthèses qui suit sa citation au
lieu de la précéder, le mot « דף » pris pour un nombre, un nom compté pour les
deux références qui l'encadrent, et une liste « 7-9-11-13 » lue comme une
soustraction. Le détecteur « le nom figure-t-il dans le daf » est désormais
**désactivé par défaut** : son idée est juste, sa précision sur ce corpus ne
l'est pas.

### Ce qui reste ouvert

Rien, de ce contrôle. Les seize divergences subsistantes sont légitimes et
consignées ci-dessus ; elles ne demandent pas de décision.

---

## Chabbat 291 — six points signalés par le Rav (10 septembre 2026)

**1. « Seouda Chelichit est une mitsva de la Torah ».** Le Mehaber n'écrit que
`יהא זהיר מאוד לקיים סעודה שלישית`. Le verset de שמות טז:כה n'est pas une
source biblique au sens propre : la Michna Beroura le dit en toutes lettres —
`ואסמכוהו אקרא` (רצ״א ס״ק א), ils l'ont *appuyé* sur un verset. Le niveau 2 de
la même page portait déjà la mahloket (R. Tam contre le Ran et la plupart) ;
c'est le niveau 1 qui écrivait « source biblique » sans la nuance.

**2. « après 'Hatsot ».** Le Mehaber donne une mesure halakhique :
`זמנה משיגיע זמן המנחה דהיינו משש שעות ומחצה ולמעלה`, et le Choul'han Aroukh
HaRav de même (רצ״א:ב). Les pages posaient « ≈ 12h30 » comme un seuil — une
heure de montre qui change tout au long de l'année. Tous les seuils horaires
sont remplacés par la mesure elle-même.

**3. Minha avant ou après.** Les niveaux 1 et 3 concluaient déjà juste. Seul le
titre du niveau 2 posait la question sans la trancher ; il porte désormais la
conclusion : Minha d'abord, comme le Rama (`וכן נוהגים לכתחלה בכל מדינות אלו`)
et le Choul'han Aroukh HaRav (רצ״א:ב et רצ״א:ד).

**4. Le lehem michné.** Le Mehaber demande DEUX pains — `אבל צריך לבצוע על שתי
ככרות`. Le Rama rapporte le minhag d'un seul et **conclut** :
`אבל יש להחמיר ליקח שנים`. Le Choul'han Aroukh HaRav tranche de même (רצ״א:ז) :
`אבל יש להחמיר לקחת שנים כסברא הראשונה שהוא עיקר`. Les traductions du séif
portaient déjà cette conclusion ; ce sont les RÉSUMÉS — quatorze lignes dans
les trois langues — qui inversaient l'accent, donnant le minhag d'un pain pour
la pratique et les deux pains pour une option.

**5. L'ordre des aliments.** Vérifié : les pages le donnaient déjà exactement
comme le séif ה — le pain d'abord, puis les cinq céréales, puis viande et
poisson, puis les fruits, et `וסברא ראשונה עיקר`. Rien à changer.

**6. Le Oneg.** La règle `ואם אי אפשר לו כלל לאכול אינו חייב לצער את עצמו`
figurait sans sa raison. La Michna Beroura la donne en cinq mots :
`דהסעודה לעונג ניתנה ולא לצער` (רצ״א ס״ק ג), désormais citée.

### Trouvé en vérifiant

Le niveau 2 attribuait à **רב חסדא**, entre guillemets et au nom de
ברכות כ״ו ע״ב, une phrase qui n'est pas de lui : `רב חסדא` ne figure nulle part
dans ce daf, et la définition y est donnée **anonymement**, dans la baraïta —
`ואיזו היא מנחה גדולה? משש שעות ומחצה ולמעלה`. C'est la deuxième attribution
fabriquée de la campagne après le « אמר רב » du siman 289.

Et le niveau 2 rattachait la conclusion « la plupart tiennent דרבנן » à
`מ״ב סק״ב`, qui traite du כביצה. Le passage utile est au `ס״ק א`.

### Ce qui reste ouvert

Le « ≈ 56 g » du כביצה est laissé tel quel : la mesure est bien dans le séif,
et sa conversion en grammes est déjà au registre comme question halakhique
(simanim 286 et 291).

---

## Charpente — seize simanim de Chabbat dont le niveau 1 ne reproduit pas le Choul'han Aroukh séif par séif (mesure du 11 septembre 2026)

Constaté en cherchant à y poser les encadrés « Ce que dit ce séif » : le moteur
n'y trouve pas où les ancrer. La mesure ci-dessous dit pourquoi, et elle ne
relève pas du même défaut que le siman 301, réparé le même jour.

Au 301, la page portait bien ses cinquante et un séifim, un par `<blockquote
class="text-source">`, chacun étiqueté « סעיף ח: » ; seuls les titres manquaient
en hébreu et en anglais, et les rendre n'a déplacé aucun texte. Ici, c'est la
reproduction du texte source elle-même qui ne suit pas la découpe de la source.

| Siman | Séifim au Choul'han Aroukh | Blocs source FR / HE / EN |
|---|---|---|
| 242 | 1 | 3 · 3 · 3 |
| 243 | 2 | 4 · 4 · 4 |
| 244 | 6 | 0 · 0 · 0 |
| 245 | 6 | 0 · 0 · 0 |
| 246 | 5 | 0 · 0 · 0 |
| 247 | 6 | 7 · 7 · **9** |
| 248 | 4 | 10 · 10 · 10 |
| 249 | 4 | **8** · 4 · 4 |
| 250 | 2 | 3 · 3 · 3 |
| 251 | 2 | 3 · 3 · 3 |
| 256 | 1 | 1 · 1 · 1 |
| 258 | 1 | 1 · 1 · 1 |
| 259 | 7 | 6 · 6 · 6 |
| 260 | 2 | 2 · 2 · 2 |
| 263 | 17 | 15 · 15 · 15 |
| 264 | 10 | 6 · 6 · 6 |

Trois choses distinctes s'y lisent :

1. **244, 245 et 246 ne reproduisent pas le texte du Choul'han Aroukh** — aucun
   bloc source, dans aucune des trois langues, pour dix-sept séifim au total.
2. **Deux divergences trilingues** : le 247 découpe en neuf blocs en anglais
   contre sept en français et en hébreu ; le 249 en huit en français contre
   quatre dans les deux autres. Une même source y est donc découpée
   différemment selon la langue du lecteur.
3. **Le reste est une découpe qui n'est pas celle de la source** — le 242
   fragmente son séif unique en trois, le 248 quatre séifim en dix, tandis que
   le 259, le 263 et le 264 en publient moins qu'il n'y en a (six blocs pour
   dix séifim au 264).

Le point 3 touche la règle absolue posée après le siman 243 : *« il faut toujours
que ce soit exactement comme dans le Choul'han Aroukh »* — la découpe entre
séifim en fait partie. Mais le réparer demande de reprendre le texte source de
seize pages publiées dans trois langues, ce qui n'est pas un correctif mécanique
et n'a pas été entrepris : **décision de l'utilisateur attendue**.

Rien n'a été modifié sur ces seize simanim.
