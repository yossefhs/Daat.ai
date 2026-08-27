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
