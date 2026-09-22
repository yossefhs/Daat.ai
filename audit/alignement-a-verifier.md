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

---

## Siman 292 — Tsidkatekha n'est pas un psaume, et Ezra n'a pas Rabbi Yohanan (14 septembre 2026)

**1. « Un seul psaume ».** L'encadré du niveau 1 présentait צדקתך צדק comme
« 3 courts versets formant un seul psaume » — en hébreu
`שלושה פסוקים קצרים המהווים מזמור אחד`, en anglais « 3 short pesukim forming
one mizmor ». C'est inexact : les trois versets viennent de **trois Tehilim
différents**, vérifiés un par un à la source —

- תהלים לו:ז — `צדקתך כהררי־אל משפטיך תהום רבה`
- תהלים עא:יט — `וצדקתך אלהים עד־מרום אשר־עשית גדלות`
- תהלים קיט:קמב — `צדקתך צדק לעולם ותורתך אמת`

Les trois encadrés portent désormais la formulation retenue par l'utilisateur :
trois versets tirés de trois Tehilim différents, avec leurs références. Le verset
cité comme « Contenu » est celui de קיט:קמב, et il est désormais nommé comme tel
— il était donné auparavant comme s'il résumait les trois.

La traduction du séif, juste en dessous, donnait déjà les trois références
correctes (`תהלים לו:ז, עא:יט, קיט:קמב`), et le niveau 2 les attribue une par
une à Moïse, Yossef et David. C'est encore la synthèse pédagogique seule qui
portait l'erreur, au-dessus de deux niveaux qui savaient juste — le même motif
que les simanim 288, 289, 290, 324 et 344.

**2. Trouvé en vérifiant — une attribution fabriquée.** Le niveau 2 citait, entre
guillemets et au nom de בבא קמא פ״ב ע״א :
`"עזרא תיקן... שיהו קורין במנחה בשבת. מאי טעמא? אמר ר' יוחנן: משום יושבי קרנות"`.

Le `מאי טעמא? אמר ר' יוחנן` n'existe pas à cet endroit. La guemara y donne la
takana **sans attribution** : `עשרה תקנות תיקן עזרא: שקורין במנחה בשבת` … puis
`שיהו קוראין במנחה בשבת – משום יושבי קרנות`. Le `אמר רבי יוחנן` du même daf
appartient à une tout autre sougya — `כי אתא רבי אבין אמר רבי יוחנן`, sur l'arbre
penché dans le champ du voisin et les bikourim. Une attribution a donc été prise
ailleurs sur le daf et soudée à celle-ci.

La citation est remplacée par ses deux segments réellement verbatim. C'est la
troisième attribution fabriquée de la campagne, après le « אמר רב » du siman 289
et le « רב חסדא » du siman 291.

---

## Orah Haïm 56 — une citation à 0,39 de sa source annoncée (14 septembre 2026)

Trouvée en publiant les encadrés du lot 54-58, **antérieure à ce lot** et non
corrigée : le niveau 1 du siman 56 cite, au nom de שבת קי״ט ע״ב,

> `יְהִי שְׁמוֹ הַגָּדוֹל מְבֹרָךְ לְעוֹלָם וּלְעוֹלְמֵי עוֹלָמִים`

`verifier-citations.py` la mesure à **0,39** de ce que donne ce daf — l'écart le
plus bas rencontré sur le compartiment. La guemara y porte l'araméen
`אמן יהא שמיה רבא מברך` ; la forme hébraïque citée est une traduction, qui vit
ailleurs (Rashi, le Tour, le Zohar selon les éditions). Où exactement, je ne l'ai
pas établi, et **je ne l'ai pas deviné** : la référence n'est pas remplacée.

Deux corrections possibles, et c'est au Rav de trancher laquelle : rendre la
citation à sa forme araméenne réelle en שבת קי״ט ע״ב, ou garder la forme
hébraïque en lui donnant sa vraie source.

Les huit autres variantes du lot (simanim 56 et 58, niveaux 1 à 3) sont toutes
entre 0,85 et 0,98 et toutes antérieures elles aussi — de l'ordre de la variante
d'édition. Elles sont laissées telles quelles.

---

## Siman 293 — l'Arvit anticipée présentée comme une solution pratique (15 septembre 2026)

Six points repris par l'utilisateur dans le Choul'han Aroukh et la Michna Beroura,
tous confrontés aux sources avant d'être écrits. Le fond des pages était bon ;
c'est le §3 qui posait un vrai problème.

**1. Les trois petites étoiles — il manquait le POURQUOI.** La page donnait le
critère sans la raison. La Michna Beroura la donne : en droit trois étoiles
*moyennes* suffiraient, mais nous ne savons plus les distinguer des grandes, qui
se voient de jour — `ומדינא סגי בג׳ כוכבים בינונים אלא שאין אנו בקיאין בזה` (ס״ק ג).
Et le caractère *rapproché* sert la Tossefet Shabbat — `אלא רצופים — משום תוספת שבת`
(ס״ק ה). Ajouté aux trois langues.

**2. Le jour couvert.** `ימתין עד שיצא הספק מלבו` était juste. La Michna Beroura
ajoute qu'on peut se fier à une horloge sûre quand on sait avec certitude qu'à
cette heure, la veille, il faisait nuit selon la loi (ס״ק ז). Ajouté.

**3. Le cas du אנוס — la correction de fond.** La page écrivait « Critère : ones +
devar mitzva (force majeure pour une mitzva) », ce qui en faisait une règle
générale. Le cas de la Michna Beroura est étroit : il part de chez lui avant la
nuit jusqu'à la limite du tehoum, s'y assied jusqu'au soir, **et il n'y trouvera
pas de coupe** (ס״ק ח). Et surtout, les A'haronim écrivent qu'on n'agit pas ainsi
— la chose étonne le public, on risque de s'alléger sur la mélakha — et à notre
époque, où l'on suit toujours l'avis permettant Min'ha jusqu'au soir,
`בודאי מדינא אסור להקדים מעריב במו״ש` (ס״ק ט). Le niveau 3 allait plus loin encore
et **inventait des applications** que ni le Choul'han Aroukh ni la Michna Beroura
ne donnent : son tableau de cas pratiques portait « Brit Mila ou voyage urgent ».
Remplacé par le cas réel, avec la restriction.

**4. Mélakha interdite jusqu'à tslet** — était juste, et porte désormais sa
citation.

**5. Kriat Chema — manquait entièrement.** `ומ״מ ימתין מלקרות ק״ש עד צה״כ` (ס״ק י).
Les « 2 restrictions » deviennent trois, dans les trois langues et au niveau 3.

**6. Le Rama sur והוא רחום וברכו** — juste, inchangé.

### Un défaut d'indexation trouvé en corrigeant

La restriction des A'haronim, posée d'abord dans un bloc `warning`, était publiée
et **invisible au chat** : le corpus ne lit que `definition`, `remember`,
`key-point` et les tableaux de cas pratiques. Le chat aurait donc continué de
répondre selon l'ancienne présentation. Les trois blocs sont passés en `remember`
et sont désormais indexés — vérifié dans `data/corpus-shabbat.json`.

### Ce qui reste ouvert

`verifier-citations.py` ne sait pas résoudre une référence Michna Beroura de la
forme `מ״ב רצ״ג ס״ק ג` : les onze citations posées ici ne sont donc pas couvertes
par la porte. Elles ont été confrontées à Sefaria une par une par programme avant
publication, et le sont toutes. Mais **aucun garde-fou ne les surveillera
ensuite**, et c'est une lacune réelle du dépôt.

---

## Hilkhot Chabbat — le texte source rendu à 26 simanim (15 septembre 2026)

Suite de la mesure du 14 septembre. Le premier balayage de
`verify-chabbat-source.py` donnait **44 simanim sur 124** dont le niveau 1
s'écartait du Choul'han Aroukh au-delà du ktiv haser/malé. Vingt-six sont
désormais rendus à leur source, **sans jugement** : uniquement ceux dont la
découpe était déjà juste — autant de blocs que de séifim, dans les trois langues
— où le bloc n° i est sans ambiguïté le séif n° i.

Trois preuves ont été exigées par fichier avant écriture : autant de blocs que de
séifim ; la concaténation reposée redonne la source consonne pour consonne ; et
le fichier privé de ses blocs source est identique à l'original privé des siens,
donc rien d'autre que le texte source n'a bougé.

**Deux choses apprises en le faisant.** Sefaria insère dans son texte des ancres
de commentateurs — `<i data-commentator=…></i>`, toutes vides, 787 sur six
simanim échantillonnés. C'est son appareil critique, pas le Choul'han Aroukh :
les reposer laissait des éléments invisibles dans la page et polluait le corpus.
Elles sont retirées. Les `<small>`, eux, sont gardés : c'est par eux que Sefaria
marque les gloses du Rama **à l'intérieur** des séifim, et les perdre rendrait la
parole du Rama indistinguable de celle du Mehaber.

**État après ce lot : 18 simanim restent** — 242, 243, 245, 246, 247, 248, 249,
250, 251, 259, 263, 264, 309-314. Et les deux listes du garde-fou sont désormais
**identiques** : tout ce qui reste est un problème de DÉCOUPE, plus de texte.

Ces dix-huit ne se réparent pas mécaniquement, et je ne les ai pas touchés :

- **245 et 246 n'ont aucun titre de séif.** Leurs sections sont thématiques
  (« Le cas type : boutique, atelier, fonds commun », « De quoi parle ce séif ? »
  sans dire lequel). Y placer la source demanderait de décider quel séif va où :
  c'est exactement le jugement qui a produit l'erreur du siman 243.
- **242, 248, 250, 251** fragmentent : trois blocs pour le séif unique du 242,
  dix pour les quatre séifim du 248.
- **259, 263, 264** en publient moins qu'il n'y en a — six blocs pour les dix
  séifim du 264.
- **309-314** : les pages hébraïque et anglaise portent plus de blocs que la
  française et que la source (huit pour cinq séifim au 309).

**Décision de l'utilisateur attendue** sur ces dix-huit.

### Trouvé en vérifiant, non corrigé

Siman 273, niveau 2 — une phrase entre guillemets au nom d'ישעיהו נ״ח:י״ג :
`במקום עונג שהוא הסעודה, שם תהא הקריאה של קידוש`. Elle est **absente de tout
Sefaria** : c'est l'explication du limoud, pas le verset, et le verset de ce
passage est `וקראת לשבת עונג`. Antérieure à ce lot, et dans un niveau 2 que ce
travail n'a pas touché. À trancher : rendre la citation au verset réel, ou
retirer les guillemets puisqu'il s'agit d'une glose.

Quinze variantes subsistent par ailleurs dans neuf de ces simanim (252, 253, 257,
260, 262, 265, 271, 282), toutes antérieures et toutes de l'ordre de la variante
d'édition. Laissées telles quelles.

---

## Simanim 309-314 — la Michna Beroura déguisée en Choul'han Aroukh (15 septembre 2026)

Ces six simanim figuraient parmi les dix-huit « problèmes de découpe » restants.
Ce n'en était pas un. Leurs séifim sont tous présents, justes et dans l'ordre :
ce que le garde-fou comptait en trop, ce sont **trois entrées de Michna Beroura
par siman, en hébreu et en anglais, portant `blockquote class="text-source"`** —
la classe réservée au texte du Choul'han Aroukh.

Deux conséquences, et la première est la plus grave : **pour le lecteur hébreu et
anglais, la Michna Beroura était rendue exactement comme le Mehaber**, dans le
même cadre, sans rien qui la distingue. C'est le défaut dont `verifier-classes.py`
était né en juillet, sous une autre forme — les gloses `<small>` indistinguables
du texte principal — et il est ici plus net encore, puisqu'il ne s'agit pas d'une
glose de quelques mots mais d'entrées entières du Hafets Haïm.

La seconde : six simanim déclarés divergents à tort par `verify-chabbat-source.py`.

**Aucun jugement n'a été nécessaire.** La forme juste existait déjà dans le dépôt :
la page FRANÇAISE des six mêmes simanim porte les mêmes trois entrées dans
`<div class="sacred-text he">`. L'hébreu et l'anglais sont alignés sur elle, le
contenu ne bouge pas d'un caractère, et la règle CSS `.sacred-text` — absente de
ces douze pages — est reprise telle quelle de la page française.

Les six sont désormais IDENTIQUES à la source, découpe et parité comprises.
Il reste douze simanim sur les quarante-quatre du premier balayage.

### Ce que l'analyse des douze restants a montré, et qui n'est pas encore traité

Une cartographie bloc par bloc, tolérante au ktiv, donne trois familles :

- **248 et 249 répètent leurs séifim** : la suite des correspondances est
  1-2-3-4 puis 1-2-3-4 à nouveau. Le texte du séif est vraisemblablement repris
  dans une section d'analyse plus bas, la seconde reprise portant elle aussi
  `text-source`.
- **Des blocs qui ne correspondent à aucun séif** (3 à 6 % de recouvrement) aux
  simanim 242, 243, 247, 248, 259 — probablement le même défaut qu'au 309-314,
  du commentaire ou des titres portant la classe du texte de base.
- **Des séifim réellement absents** : le 264 ne couvre que les séifim 1, 2, 3, 5,
  6 et 9 sur dix ; le 259 saute le 1 et le 4 ; le 263 saute le 7 et le 9.

Les deux premières familles se réparent probablement sans jugement, comme le
309-314. La troisième demande d'ajouter du texte source là où la page n'en a
jamais eu, ce qui est additif mais demande de choisir l'emplacement.

---

## ⚠️ Le nikoud contre le verbatim — une décision que j'ai prise sans la voir (15 septembre 2026)

**À signaler d'abord : en rendant leur texte source à 26 simanim, j'ai supprimé le
nikoud de 22 d'entre eux.** Leur texte était vocalisé ; Sefaria ne l'est pas ; le
remplacement l'a donc dévocalisé. Je ne l'avais pas vu avant de publier, et je ne
l'ai donc pas soumis. Les simanim concernés : 252, 253, 254, 255, 256, 257, 260,
261, 262, 265, 267, 268, 269, 270, 274, 275, 276, 277, 279, 281, 282, 283. Le
texte d'avant est intact dans l'historique (commit `b891a92~1`) et le retour
arrière est possible siman par siman.

**Et voici pourquoi les douze simanim restants ne peuvent pas être traités sans
trancher cette question.** Tous les douze sont vocalisés. Or les deux exigences
sont incompatibles par nature :

> **On ne peut pas vocaliser une abréviation.** `בע״ש` ne se vocalise qu'en
> devenant `בְּעֶרֶב שַׁבָּת`. Une page vocalisée DOIT développer les
> abréviations du Choul'han Aroukh — c'est-à-dire commettre exactement la faute
> que `verify-yd-source.py` a été écrit pour détecter.

Vérifié : Sefaria ne propose aucune version hébraïque vocalisée de l'ouvrage. Les
trois disponibles — Maginei Eretz (Lemberg, 1893), Torat Emet, Wikisource — sont
toutes sans nikoud. Le texte vocalisé du site a donc été produit à la main.

Deux voies, et c'est à l'utilisateur de choisir :

1. **Le verbatim.** Le texte de Sefaria, avec ses abréviations, sans nikoud. C'est
   ce que demandent la règle absolue (« le Choul'han Aroukh est le repère pour
   toute référence ») et les trois garde-fous de source. C'est l'état actuel des
   22.
2. **Le nikoud.** Le texte vocalisé, plus lisible pour l'étudiant, mais qui
   développe nécessairement les abréviations et ne peut donc pas passer les
   garde-fous de source. Il faudrait alors que ces pages **disent** qu'elles
   donnent une vocalisation et non une recopie — par exemple une classe distincte
   de `text-source`, que le garde-fou saurait ne pas juger au verbatim.

La seconde voie me paraît la meilleure des deux, parce qu'elle ne sacrifie rien :
elle garde le service rendu au lecteur ET rend le garde-fou honnête, au prix d'une
distinction explicite. Mais c'est une décision éditoriale, pas technique, et je ne
l'ai pas prise.

**Rien n'a été fait sur les douze restants** — 242, 243, 245, 246, 247, 248, 249,
250, 251, 259, 263, 264 — en attendant cette décision.

---
## Yoré Déa 183-200 (bloc נדה) : le niveau 1 ne reproduit pas le texte source

Mesuré le 15 septembre 2026, en produisant le lot 201-208, après qu'un agent de
production eut signalé que le siman 200 échouait au garde-fou de source. Aucune
de ces dix-huit pages n'a été modifiée : c'est un constat, pas une correction.

**Les dix-huit simanim du bloc échouent à `scripts/verify-yd-source.py`.**
C'est le seul bloc de Yoré Déa dans ce cas ; les simanim 87 à 182 et 201 à 208
passent tous. Le garde-fou n'avait jamais été lancé sur 183-200, produits par une
autre chaîne de travail, et `audit-simanim.py` ne pouvait pas le voir : il juge la
structure, pas la fidélité du texte.

### Ce que porte la classe `text-source` — 161 blocs, niveau 1 français

| état | blocs | ce que c'est |
|---|---|---|
| verbatim | 102 | le texte du Choul'han Aroukh, tel quel |
| **réécrit** | **41** | la matière du siman, mais les mots changés — vocalisation ajoutée, ponctuation refaite, formulation retouchée |
| **sans correspondance** | **18** | rien qui réponde au siman cité |

Les trois langues portent les mêmes blocs : l'ordre de grandeur réel est le triple.

### Le cas le plus net, et le plus grave — siman 200

Son niveau 1 porte **trois** blocs `text-source` pour **un** seul seif. Le
troisième n'est pas une citation du tout :

> שֹׁרֶשׁ הַמַּחֲלֹקֶת: מִצַּד אֶחָד, כָּל הַבְּרָכוֹת מְבָרֵךְ עֲלֵיהֶן עוֹבֵר לַעֲשִׂיָּתָן ; וּמִצַּד שֵׁנִי,
> אֵין לְבָרֵךְ כְּשֶׁגּוּפָהּ מְגֻלֶּה…

C'est une explication pédagogique — « la racine de la controverse : d'un côté…
de l'autre… » — composée en hébreu vocalisé et servie sous la classe réservée au
texte du Mehaber, dans les trois langues. Elle n'est nulle part dans le
Choul'han Aroukh. Le premier bloc du même siman « corrige » par ailleurs
l'orthographe de la source (`ותפשט` pour `ותפשוט`).

### Pourquoi cela compte plus qu'un défaut de mise en page

La classe `text-source` est la promesse faite au lecteur que ce qu'il lit est la
parole de la source. Un encadré pédagogique rendu dans cette classe ne se
distingue pas d'un seif : le lecteur prend l'exposé de la page pour le texte du
Choul'han Aroukh. C'est la même famille que le défaut des gloses `<small>` de
Sefaria rendues à la taille du texte principal — sauf qu'ici le contenu n'est pas
seulement mal présenté, il n'est pas de la source.

⚠️ **Le siman 200 sert de gabarit.** C'est un siman à seif unique, donc le
premier que consulte un agent chargé d'un siman court — l'agent du siman 207
(un seif) s'y est reporté et a signalé le défaut plutôt que de le recopier. Un
agent moins attentif l'aurait reproduit.

### Ce qui reste à décider

Reprendre ces dix-huit simanim, c'est réécrire le niveau 1 de 270 pages contre
les sources. Ce n'est pas une correction mécanique : les 41 blocs réécrits
demandent d'être remplacés par le texte réel, les 18 sans correspondance
demandent un arbitrage cas par cas (déplacer le contenu hors de la classe
`text-source`, ou le retirer). **Décision de l'utilisateur attendue.**

En attendant, deux choses sont vraies et doivent être dites ensemble : ces pages
sont en ligne, et leurs citations d'appareil n'ont jamais été mises en cause —
c'est la reproduction du texte de base qui est en défaut, pas l'honnêteté des
références.


## Voie 1 retenue — le verbatim. Six simanim de plus, six restants (16 septembre 2026)

Décision de l'utilisateur : le verbatim plutôt que le nikoud. Les 22 simanim
dévocalisés restent en l'état, et les douze qui attendaient sont portés au même
régime. **Six y sont passés : 243, 247, 248, 249, 250, 251.**

Presque aucun n'était le « problème de découpe » que le premier balayage
annonçait. C'était, trois fois sur quatre, le défaut déjà vu aux simanim 309-314 :
des blocs qui n'étaient pas du Choul'han Aroukh portaient sa classe.

- **250 et 251** : une citation de guemara — « L'origine talmudique — Shabbat
  119a », « — Pesahim 50b » — rendue dans le cadre du texte de base.
- **247 et 248** : les séifim recopiés une seconde fois dans une section
  d'analyse plus bas, la reprise portant elle aussi `text-source`. Le 248 y
  ajoutait une braïta, `תנו רבנן: אין מפליגין בספינה`.
- **249** : la même reprise, quatre séifim publiés deux fois.
- **243** : rien d'étranger, seulement le texte à rendre verbatim. Sa découpe en
  quatre blocs pour deux séifim est délibérée et juste — « texte du Mehaber »
  puis « texte du Rama » — et l'avertissement du garde-fou est ici sans objet.

**Trois pièges rencontrés en construisant l'outil, et chacun aurait produit une
page fausse s'il n'avait pas été vu :**

1. La première mesure de correspondance prenait la plus longue suite commune.
   Elle s'effondre sur une page vocalisée, où chaque abréviation développée hache
   le texte : le séif א du siman 247 tombait à 6 % alors que c'est mot pour mot
   le même séif. Remplacée par un recouvrement de mots.
2. Ce recouvrement est unidirectionnel : un bloc qui ne porte que la part du
   Mehaber marque 1,0 sur le séif entier, tous ses mots y étant. L'outil lui
   aurait donné le séif complet — donc **ajouté la glose du Rama que le bloc
   suivant porte déjà**, et publié la glose deux fois. Remplacé par une moyenne
   harmonique des deux sens.
3. Une braïta que le séif recopie partage presque tous ses mots. Aucune mesure de
   similarité ne l'en distingue ; c'est le titre de la page qui le dit
   (« origine talmudique ») ou l'ouverture du bloc (`תנו רבנן`, `תניא`).

### Les six qui restent, et pourquoi

- **242** : sa page découpe son unique séif — très long — en parts thématiques
  que le partage Mehaber/Rama ne capture pas. L'outil a refusé : le texte reposé
  ne redonnait pas la source.
- **245 et 246** : aucun titre de séif, sections thématiques. Inchangé depuis le
  14 septembre.
- **259, 263, 264** : des séifim **réellement absents** de la page. Le 259 n'a pas
  le 4, le 263 n'a ni le 7 ni le 9, le 264 ne couvre que 1, 2, 3, 5, 6 et 9 sur
  dix. Les ajouter est additif, mais demande de choisir où — donc un jugement.

Le compte : **44 → 6**.

---
## Yoré Déa 228:21 — une frontière Mehaber / Rama que le balisage ne marque pas (16 septembre 2026)

Trouvé en produisant le siman 228 (התרת נדרים, 51 seifim). L'agent a dû trancher,
l'a fait, et l'a signalé comme le premier point à soumettre au Rav — ce qui est la
conduite attendue. Vérification faite ici ; la page n'est pas modifiée.

**Le fait.** Le seif 21 porte quatre marques `הגה` dans le texte de Sefaria. Les
deux clauses `ואין נקראים רבים בפחות מג׳…` et `ויש אומרים שאם נדר בפני ג׳…`
tombent, selon ce balisage, à l'intérieur d'une région de glose. Mais :

- elles sont les **seules de tout le segment** à ne porter **aucune parenthèse de
  source** — signature constante des gloses dans ce siman (les 46 autres clauses
  attribuées au Rama en portent toutes une) ;
- la clause qui précède se ferme sur sa source, `(ב"י בשם תשובת רשב"א)` ;
- et la seconde se termine par un **deux-points**, qui est dans cette édition la
  marque de fin du texte du Mehaber — immédiatement suivi d'un nouveau `הגה`.

**Ce qui a été fait.** Les deux clauses sont rendues au Mehaber
(`שו״ע יו״ד רכ״ח:כא`), et la page dit au lecteur, dans les trois langues, que la
frontière n'est pas marquée et que la lecture mérite d'être vérifiée sur une
édition imprimée.

**Pourquoi aucun garde-fou ne peut le voir.** `verifier-citations.py` résout
`רמ״א` et `שו״ע` vers le même segment Sefaria : une attribution croisée y est
invisible. C'est la même famille que les quatre erreurs de l'audit rabbinique
d'août 2026, où les citations étaient vraies et l'attribution fausse.

**Ce qui reste à décider.** Ce siman compte en outre **27 attributions au Rama
inférées et non marquées** : sur 48 clauses de glose, 21 seulement s'ouvrent par
un `הגה` explicite ; les 27 autres sont des propositions parenthésées portant une
source, ou des suites de gloses déjà ouvertes. C'est la convention imprimée, mais
Sefaria ne la marque pas, et la décision revient au producteur de la page. Les
seifim concernés : 15, 16, 17, 20, 21, 31, 33, 43, 45, 50.

⚠️ **Et le siman 43 porte une parenthèse jamais refermée** (3 « ( » pour 2 « ) ») :
la glose lexicale sur `משודכים` s'ouvre et ne se clôt pas, de sorte que les mots
du Mehaber `מעשיו פטור הלה משבועתו` tombent à l'intérieur de la parenthèse. C'est
un défaut de numérisation, recopié tel quel (règle 13) et signalé dans la page —
il fausserait la lecture de quiconque lirait la parenthèse comme une glose close.


## Hilkhot Chabbat — les 124 simanim reproduisent le Choul'han Aroukh (16 septembre 2026)

Le premier balayage du 14 septembre donnait **44 simanim sur 124** dont le niveau 1
s'écartait de sa source au-delà du ktiv haser/malé. Le compte est **zéro**.

Les six derniers, traités ce jour :

- **259, 263, 264** — des séifim n'avaient jamais été publiés : le ד du 259, le ז
  et le ט du 263, et quatre des dix du 264. Leur place n'était pas un jugement :
  elle est fixée par la source, entre le bloc du précédent et celui du suivant.
  *Un piège au passage* : deux séifim absents qui se posent au même endroit — le ז
  et le ח du 264 — étaient départagés par leur TEXTE, et le ח passait devant le ז.
  Le rang du séif départage désormais les ex æquo.
- **242** — son unique séif, très long, est présenté en trois parts : le début, la
  takana d'Ezra, la glose du Rama. Les trois sont contiguës et dans l'ordre de la
  source ; il a suffi de couper le séif aux deux mêmes frontières et de rendre à
  chaque bloc SA part.
- **245 et 246** — aucun titre de séif, sections purement thématiques : rien où
  accrocher chaque séif, et les répartir entre les thèmes aurait été le jugement
  qui a produit l'erreur du 243. Une section entière, « Le texte du Choul'han
  Aroukh », est posée AVANT la première section thématique — le lecteur rencontre
  la source avant l'exposé — avec les séifim dans l'ordre, étiquetés comme au
  siman 301. Purement additif.

*Un second piège, trouvé par le garde-fou lui-même* : j'avais étiqueté les blocs
français « Séif א », avec accent. `verify-chabbat-source.py` ne reconnaît comme
étiquette que `סעיף`, `Seif` et leurs pluriels — le `א` du label comptait donc
pour du texte, et les pages françaises du 245 et du 246 sortaient divergentes
quand l'hébreu et l'anglais passaient. Les pages françaises du dépôt écrivent
« Seif ».

### Ce qui reste, et qui est juste

Deux simanim gardent un **avertissement de découpe**, et il est sans objet dans
les deux cas : le 242 (trois blocs pour un séif) et le 243 (quatre blocs pour
deux). Leur découpe est délibérée — « texte du Mehaber » puis « texte du Rama »,
et pour le 242 les trois parts d'un séif très long — elle suit l'ordre de la
source, et leur texte est verbatim. L'avertissement signale une découpe qui
diffère du compte des séifim, ce qui est vrai ; il ne dit pas qu'elle est fautive.

### Bilan des trois compartiments

Hilkhot Chabbat a désormais son garde-fou de source ET le passe entièrement. Yoré
Déa et Orah Haïm ont les leurs ; l'état de Yoré Déa est suivi par la session qui
l'écrit (voir l'entrée sur le bloc נדה 183-200).

---

## Les comptes de mots — « en N mots / בN תיבות / in N words » (17 septembre 2026)

Seconde forme des affirmations de dénombrement, trouvée par l'arbitre du siman 234
alors que trois tours de correction avaient nettoyé les superlatifs jusqu'au bout.
Sur les dix-sept comptes de mots du siman 234, **cinq étaient faux**, mesurés contre
la source un par un.

Deux exemples, parce qu'ils disent la nature du défaut :

- « le dernier séif, qui tient en **sept mots** » — le séif 74 est
  `אשה שנדרה לשתות סם להתעבר אין הבעל יכול להפר`, **neuf** mots, et la page le cite
  elle-même verbatim à deux autres endroits.
- « **quatre mots**, et aucun commentateur n'y ajoute rien » — le séif 26 est
  `השוטה אינו מפר`, **trois** mots, cités deux lignes plus bas ; et l'hébreu dit lui
  aussi `ארבע תיבות`, donc aucune lecture ne sauve la phrase. (La seconde moitié est
  exacte : aucun des cinq appareils ne commente ce séif.)

**Étendue mesurée sur les 148 simanim de Yoré Déa publiés : 710 comptes de mots.**
`scripts/verifier-denombrements.py` les relève tous et tranche mécaniquement le seul
cas qui se tranche sans lecture — la **divergence entre les trois langues**, les
variantes d'un niveau étant parallèles à la ligne près dans ce dépôt. Neuf
divergences dures :

| siman | fichier | ligne | fr | he | en |
|------:|---|---:|---:|---:|---:|
| 127 | niveau-3-synthese | 494 | 3 | — | 4 |
| 133 | niveau-1-base | 669 | 5 | — | 3 |
| 160 | niveau-1-base | 665 | 3 | — | 2 |
| 179 | niveau-1-base | 719 | 5 | — | 4 |
| 220 | niveau-2-lamdan | 618 | — | 3 | 6 |
| 231 | niveau-1-base | 563 | 5 | 4 | 4 |
| 234 | niveau-1-base | 578 | 5 | 4 | 4 |
| 234 | niveau-1-base | 931 | 4 | 3 | 3 |
| 234 | niveau-1-base | 967 | 4 | 3 | 3 |

Les trois du 234 ont été mesurées contre la source : elle donne **trois** dans les
trois cas, si bien qu'au l.578 les trois langues se trompent et de trois manières.
Aux l.931 et 967, l'hébreu et l'anglais sont justes et le français seul est faux.

Les six divergences **hors du lot 229-234** (simanim 127, 133, 160, 179, 220) ne sont
pas corrigées : aucune page n'a été modifiée. Elles attendent une décision, comme le
bloc נדה 183-200. Et les 701 autres comptes de mots n'ont **jamais été mesurés** —
si la proportion du siman 234 valait ailleurs, il y en aurait beaucoup de faux ; mais
un siman ne fait pas une mesure, et c'est précisément ce qu'il faudrait établir.

---

## Le bloc hébreu des pages d'index — un trou de garde, et son étendue réelle (16 septembre 2026)

La session ravabichid.org signale avoir corrigé le siman 246, dont le bloc
`seif-text-he` de l'index disait **l'inverse** du Choul'han Aroukh : une
interdiction, « אסור להשכיר… ואסור אפילו להשאיל », là où le Mehaber écrit
« מותר להשאיל ולהשכיר ». Vérifié ici à la source : leur correction est juste, le
bloc porte désormais le verbatim.

Elle signale aussi, et c'est le point important, que **ce bloc n'est lu par aucun
garde-fou**. C'est exact : `verifier-citations.py` juge ce que la page met entre
guillemets, `verifier-alignement.py` juge les blocs `text-source` des niveaux
d'étude, et les trois portes de source jugent le niveau 1. La page d'index
n'était lue par personne — alors que ce bloc est souvent le premier hébreu que le
lecteur rencontre, et celui que Google indexe.

**Étendue réelle mesurée : 738 pages d'index en portent un.** Le signalement en
nommait cinq. C'est la leçon que ce fichier tire déjà deux fois — « un correctif
appliqué à la main sur les cas qu'on a vus n'est pas un correctif » — et elle
vaut une troisième.

`scripts/verifier-index-source.py` comble le trou. Il lit l'intertitre qui NOMME
l'ouvrage — « שולחן ערוך, אורח חיים » ou « שולחן ערוך הרב (אדמו״ר הזקן) » — et
exige que le bloc se retrouve mot pour mot dans cet ouvrage-là, d'un seul tenant.
Deux verdicts, comme les autres portes de source : IDENTIQUE et ÉQUIVALENT aux
matres lectionis près.

**Un défaut de mon propre garde-fou, trouvé en le lançant.** Il ne cherchait le
nom de l'ouvrage qu'en hébreu. Les pages ANGLAISES des simanim 244 et 245
écrivent « Shulchan Aruch HaRav (the Alter Rebbe), not the Shulchan Aruch » en
lettres latines : il les lisait donc comme citant le Choul'han Aroukh, et les
déclarait fautives **à tort**. C'est exactement le défaut du « Séif » accentué de
la veille — un détecteur qui ne connaît qu'une langue sur trois. Corrigé.

**Hilkhot Chabbat : 15 pages d'index, 0 divergence.** Les simanim 242, 243 et 246
développaient les abréviations de la source parce que leur bloc est vocalisé —
on ne peut pas vocaliser « ואע״פ ». C'est la question déjà tranchée le 16
septembre, voie 1 : le verbatim. La frontière où chaque bloc s'arrête n'a pas été
devinée mais retrouvée DANS la source, par ses derniers mots.

### À décider avec le Rav

Les simanim 244 et 245 portent en tête, sous un intertitre qui le dit
explicitement, le texte du **Choul'han Aroukh HaRav** et non celui du Mehaber. La
session ravabichid.org a corrigé l'étiquette, qui annonçait « שולחן ערוך », et
laisse ouverte la question de fond : faut-il y mettre le Mehaber ? Le garde-fou
accepte les deux, puisqu'il juge la fidélité à l'ouvrage nommé, pas le choix de
l'ouvrage.

### Le balayage d'Orah Haïm — ce qu'il dit, et ce qu'il ne dit pas

723 pages d'index portent un bloc hébreu. Le garde-fou les répartit ainsi :

- **460 digests fidèles** — ils abrègent le siman, séif par séif, chacun étiqueté
  `(סעיף N)` et séparé par « · ». Ils sautent des passages ; ils n'inventent rien.
- **15 conformes** aux matres lectionis près.
- **156 pages (54 simanim)** dont le bloc s'éloigne assez des mots de la source
  pour que la porte ne puisse plus en répondre.

**Ce dernier compte n'est PAS une liste de 54 simanim fautifs, et il ne faut pas
le lire ainsi.** Vérification faite sur les plus gros écarts : le siman 216, qui
présente 728 caractères d'affilée introuvables dans sa source, est une
**réécriture fidèle** — il écrit « ולאחריו אינו מברך » là où le Mehaber écrit
« אבל לאחריו א״צ לברך », et ajoute « וכיצד מברך » en tête d'énumération. Le sens
est le même ; les mots ne le sont pas.

C'est le fait central de ce balayage, et il est plus grave que n'importe quel
chiffre : **le bloc d'index d'Orah Haïm n'est pas une citation, c'est le siman
rendu dans les mots de la page** — sous un intertitre qui annonce « שולחן ערוך,
אורח חיים סימן רט״ז ». Et c'est précisément pour cela que l'inversion du siman 246
avait pu s'y loger sans que rien ne la voie : quand le bloc est dans les mots de
la page, rien ne distingue une réécriture juste d'une réécriture inversée.

La porte mesure donc, sur Orah Haïm, une DISTANCE et non une vérité. Les 54
simanim sont une liste à lire, pas un verdict — et je ne les ai pas touchés :

8 9 11 27 45 55 58 61 63 65 66 70 71 75 79 83 90 108 109 110 112 114 117 124 126
128 135 137 143 149 150 153 154 155 156 168 174 177 178 182 188 190 191 192 193
201 202 205 208 211 214 216 224 240

### Ce qui rendrait la porte capable de juger

Deux voies, et c'est une décision éditoriale :

1. **Le verbatim** — le bloc porte le texte de la source, comme il le fait
   désormais sur les quinze pages de Hilkhot Chabbat. La porte devient alors un
   vrai contrôle de vérité sur les 738 pages.
2. **Le résumé assumé** — le bloc reste une réécriture, mais la page le DIT, selon
   la convention du dépôt : un abrégé s'introduit par `<em>résumé</em> :` et n'est
   pas jugé au verbatim. L'intertitre cesse alors d'annoncer le Choul'han Aroukh
   comme si le texte suivait.

Aujourd'hui les blocs d'Orah Haïm sont dans le premier régime pour l'apparence et
dans le second pour le contenu, ce qui est le seul cas où une erreur ne peut être
vue par personne.

---

## Les blocs d'index d'Orah Haïm — décision prise, et deux références fausses trouvées (17 septembre 2026)

### La décision : le résumé assumé

Des deux voies posées au registre, c'est la seconde qui est retenue, et voici
pourquoi. À Hilkhot Chabbat, les quinze blocs d'index sont courts et peuvent
porter le verbatim — ils le portent désormais. À Orah Haïm, le bloc résume **tout
le siman**, séif par séif, avec ses étiquettes « (סעיף N) » : c'est un vrai
service au lecteur, qu'un préfixe verbatim détruirait. Le défaut n'était donc pas
le contenu mais **l'étiquette qui le présentait comme le texte** — « Le Siman —
שולחן ערוך, אורח חיים סימן רט״ז », au-dessus d'une réécriture.

`scripts/etiqueter-resumes-index.py` pose donc la convention du dépôt —
« <em>résumé séif par séif</em> » / « תמצית סעיף אחר סעיף » / « summary, seif by
seif » — et **uniquement là où elle est vraie** : 615 pages la reçoivent, 108 dont
le bloc est une citation réelle gardent leur étiquette telle quelle.

### Ce que la relecture des 54 simanim a donné

Plutôt que de parcourir 54 digests à la main, deux contrôles ciblés ont été écrits
sur ce qui avait fait le défaut du siman 246.

**`verifier-polarite-index.py`** — le résumé dit-il PERMIS là où la source dit
INTERDIT ? Il compare non les mots mais le pôle par lequel chacun OUVRE.
Résultat sur tout Orah Haïm : **aucune inversion**. Il n'y a pas d'autre siman 246.

Trois corrections ont été nécessaires avant d'y arriver, et chacune a été trouvée
en rejouant le contrôle sur le cas connu plutôt qu'en le croyant sur parole :

1. La première règle cherchait un pôle ABSENT de la source. Elle ne voyait pas le
   246, dont le résumé ne disait rien que le séif ne dise — il ouvrait par
   l'inverse et reléguait la permission à une subordonnée.
2. La table confondait trois axes : elle rangeait « חייב » avec « אסור » et
   « פטור » avec « מותר ». Obligation, permission et validité sont trois
   questions distinctes ; le siman 9, qui ne parle que d'obligation, était
   signalé à tort.
3. La table était écrite en ktiv malé et les blocs sont en ktiv haser : « מתר »
   n'était pas reconnu comme « מותר », et le siman 14 — qui ouvre pourtant par
   « מתר לטל טלית חברו » — était lu comme ouvrant par le « אסור » qui vient plus
   loin.

**`verifier-etiquettes-index.py`** — le résumé étiqueté « (סעיף ט) » est-il celui
du séif ט ? C'est la règle absolue appliquée aux pages d'index, qu'aucun contrôle
ne couvrait. **Deux simanim fautifs, le 25 et le 28**, et la cause est la même :
le CHAPEAU du siman — « דיני תפלין בפרטות, ובו י״ג סעיפים » — avait reçu
l'étiquette « (סעיף א) », décalant tout d'un cran. Ce qui était donné comme le
séif ט était le séif ח, jusqu'au bout du siman. Corrigé : le chapeau perd une
étiquette qui ne lui revenait pas, les autres reculent d'un rang, aucun texte
n'est touché.

C'est la faute du siman 243 — une référence qui désigne le mauvais séif — trouvée
dans un endroit que personne ne regardait.

### Siman 65 d'Orah Haïm — deux séifim que le moteur ne sait pas départager

Écarté du lot 59-67, et non forcé. Ses séifim ב et ג commencent tous deux par
« קרא קריאת שמע ונכנס לבית הכנסת ומצא ציבור שקורין קריאת שמע » et ne divergent
qu'ensuite — l'un sur l'obligation du premier verset, l'autre sur le mérite de
lire tout le Chema avec eux. Les deux blocs de la page sont aussi proches que les
deux séifim, et l'ancrage par recouvrement de mots ne peut pas les séparer : le
moteur a refusé le siman entier plutôt que d'attribuer un encadré au hasard.

C'est le bon comportement. À traiter à la main, en nommant chaque bloc.

---

## Une citation FABRIQUÉE, en ligne, sur une ligne de psak — siman 187 (19 septembre 2026)

**NEEDS_RABBINIC_VALIDATION.** Le siman 187 de Yoré Déa attribue au Rama, entre
guillemets, une phrase qui n'existe pas :

> « אין אנו נוהגין להוציאה »

**Vérifié deux fois, par squelette consonantique, sur le texte retéléchargé depuis
Sefaria : cette phrase n'est nulle part dans le siman 187.** Ni elle, ni même les mots
`נוהגין` ou `להוציאה` pris isolément — zéro occurrence dans les quatorze séifim.

**113 occurrences** dans les quinze fichiers du siman, dont des meta descriptions, des
JSON-LD, des sommaires, et une **ligne de psak du niveau 4** qui la référence
explicitement « Choul'han Aroukh YD 187:1 ».

**Et elle renverse le sens du siman.** La page en fait « l'allègement du Rama » : on ne
fait plus divorcer. Or le Mehaber au séif 1 écrit
`אסורה לשמש עם בעל זה אלא תתגרש ותנשא לאחר`, et la glose **réelle** du Rama au même séif
est une **rigueur** :

> הגה וי״א שאין אנו בקיאין איזה מיקרי מחמת תשמיש כי אין בקיאין בשיעור הנזכר ולכן כל
> שרואה ג״פ סמוך לתשמיש מקרי לדידן מחמת תשמיש **ונאסרה על בעלה** (ב״י בשם הראב״ד…)

Le Rama **élargit** l'interdit ; le site lui fait dire le contraire.

**Pourquoi aucune porte ne l'a vu.** Le `span.he-q` de la phrase compte **22 lettres
hébraïques**, sous le seuil de 25 de `verifier-citations.py`. C'est le point aveugle n°1
du brief — « les citations de moins de 25 lettres ne sont jamais confrontées à leur
source », 1 204 mesurées dans Yoré Déa dont 319 portant une référence précise — et le
voici qui coûte un psak inversé, en ligne.

Le seuil existe pour ne pas accuser les termes techniques mis entre guillemets. Ce cas
montre ce qu'il laisse passer. **À rouvrir comme question d'outil**, indépendamment de la
réparation du siman 187 : une citation courte MUNIE D'UNE RÉFÉRENCE PRÉCISE devrait être
jugée quel que soit son nombre de lettres.

L'idée qu'on ne contraindrait plus au divorce de nos jours est une position réelle chez
des Aharonim. Elle n'est pas dans ce siman, et ce n'est pas au site de décider ce qu'il
enseigne à la place : la réparation RETIRE la fabrication et rétablit la glose réelle,
sans substituer un psak à un autre. Ce qui doit être dit de la pratique contemporaine
revient au Rav.

---

## Les sujets d'entête restés en hébreu sur des pages traduites (22 septembre 2026)

Mesuré sur les 263 pages de niveau 2 déjà traduites du compartiment Yoré Déa : **47 titres
français et 33 titres anglais** portent encore un sujet **entièrement hébreu**, là où le
reste de l'entête est bien dans la langue de la page. Exemple :

> `<title>Siman צ״ה · Niveau 2 Lamdan — Pilpoul approfondi · דגים וביצה שנתבשלו בקדרה של בשר…`

Le défaut touche le `<title>`, l'`og:title`, le `twitter:title` et la `meta description`.
Il est invisible à la lecture de la page — c'est l'entête — mais c'est ce que Google
indexe et ce que montre un aperçu de partage.

Les huit simanim du lot 95-102 sont corrigés : le sujet est repris de la page `index` du
même siman, qui l'écrit déjà dans la bonne langue. **Les autres ne le sont pas** et
attendent un balayage dédié — la correction n'est pas mécanique partout, certains simanim
n'ayant pas de sujet français disponible ailleurs.
