# Les 267 citations « introuvables » de Hilkhot Chabbat — triées

*Relevé mécanique, 24 septembre 2026. **Ce sont des candidats, jamais des verdicts.**
Aucune page n'a été modifiée pour produire ce document.*

## Pourquoi ce tri existe

`scripts/verifier-fabrications.py` demande à la recherche plein texte de Sefaria si une
citation existe **quelque part**. Sur les 3 484 citations hébraïques de Hilkhot Chabbat, il
en rend **265 introuvables** (267 après dédoublonnage par siman). C'est une bonne première
passe, mais sa question est trop grossière : un ktiv défectif, deux mots recollés, une œuvre
mal indexée suffisent à faire sortir « introuvable » une citation parfaitement réelle.

Premier resserrement — **la citation est-elle dans l'appareil du siman ?** On retélécharge,
une fois par siman, le Choul'han Aroukh, la Michna Beroura, le Maguen Avraham, le Taz, le
Biour Halakha, le Beit Yossef et le Choul'han Aroukh HaRav, et l'on cherche le squelette
consonantique. **39 se retrouvent** : faux positifs de la recherche. Restent 228.
En neutralisant en plus les matres lectionis (le ktiv haser/malé est le faux positif
dominant), **20 de plus** se retrouvent. Restent **208**.

## Le cas témoin, et ce qu'il a imposé

J'allais rendre ces 208 comme une liste unique. Un cas témoin l'a interdit.

`ונוהגין ללוש כדי שעור חלה בבית…` (siman 242, niveau 4, FR et EN) sortait « absente ».
Or c'est **le Rama, mot pour mot, sur Orah Haïm 242**. Le diagnostic, au caractère 45 du
squelette :

| | la source | la page |
|---|---|---|
| ouverture | `נוהגין ללוש` | `וְנוֹהֲגִין` — un vav ajouté |
| ktiv | `שיעור` | `שִׁעוּר` |
| **au milieu** | `…בשבת ויום טוב [סמך ממרדכי ריש מסכת ר״ה] והוא מכבוד…` | `…בשבת ויום טוב, והוא מכבוד…` |
| nikoud | aucun chez Sefaria | vocalisation entière ajoutée |

La page **saute le crochet de source que Sefaria place à l'intérieur du texte du Rama** et
recolle les deux morceaux sans points de suspension, le tout entre guillemets. La citation
n'est pas inventée : elle est **recollée**. Le test « le squelette est-il une sous-chaîne ? »
ne peut pas distinguer cette famille d'une fabrication — il rend le même verdict pour une
phrase inventée et pour une phrase réelle dont on a retiré cinq mots au milieu.

D'où le tri par **ancrage des deux bouts** : plus long préfixe et plus long suffixe, cherchés
**dans le même segment source** (jamais dans une concaténation — un préfixe chez le Michna
Beroura et un suffixe chez le Beit Yossef ne font pas un recollage, ils font deux
coïncidences), avec et sans matres lectionis.

**Ce cas témoin a donné une porte**, `scripts/verifier-troncatures.py`, qui pose la question
sur TOUTES les citations et non plus sur les seules « introuvables ».

## Ce que le tri rend

| pile | nombre | ce que cela veut dire |
|---|---|---|
| **RECOLLÉE** | 14 | le texte existe des deux côtés du trou : omission non marquée |
| **PARTIELLE** | 40 | un long fragment retrouvé, le reste nulle part |
| **ABSENTE** | 154 | rien de substantiel — dont 40 seulement revendiquent une source |

Et dans les 154 « absentes », la question qui décide n'est pas la même selon que la page
**promet une source** ou non :

| | nombre |
|---|---|
| **avec une source revendiquée à ±2 lignes** — elle promet, la source ne porte pas | **40** |
| sans source, 25 consonnes ou plus — confrontable à rien (règle 26-bis) | 45 |
| sans source, moins de 25 consonnes — sans doute pas une citation du tout | 69 |

Neuf entrées ne se retrouvent plus dans leur page : elles ont été corrigées depuis le relevé.

## Un défaut de forme qui traverse les trois piles

**68 des 208 portent un guillemet ASCII (`"`) à l'intérieur de l'hébreu** — `עכו"ם` au lieu
de `עכו״ם`. Mesuré ensuite sur tout le dépôt : **5 131 occurrences dans 187 fichiers** pour le
gershayim d'abréviation, et **1 926 occurrences dans 560 fichiers** pour le guillemet ASCII
employé comme guillemet autour d'une phrase hébraïque — deux défauts distincts qu'il ne faut
pas confondre.

⚠️ **Et il ne faut pas corriger sans regarder d'où vient l'ASCII** : Sefaria l'emploie
elle-même dans ses propres textes (le crochet du cas témoin s'écrit `[סמך ממרדכי ריש מסכת ר"ה]`
CHEZ SEFARIA). Un `blockquote class="text-source"` qui recopie fidèlement Sefaria porte donc
légitimement de l'ASCII, et l'y « corriger » ferait diverger la recopie de sa source. C'est la
raison pour laquelle `heb-nums.py` exempte `blockquote.text-source` et `.sa-he`, et tout
correctif de ce défaut doit faire de même.

## Ce que ce document ne dit pas

« Absente » ne veut **jamais** dire « inventée ». La recherche porte sur l'appareil du siman ;
une citation du Talmud, d'un Richon ou d'un siman voisin en sort légitimement absente. Le
tri réduit la pile à ce qui demande une lecture — il ne la remplace pas.

## RECOLLÉES — 14

Le texte de la source existe **des deux côtés du trou**. Ce ne sont pas des fabrications :
ce sont des omissions non marquées à l'intérieur de guillemets. Le remède est mécanique —
rétablir le passage sauté, ou marquer la coupure par « … ».

- **242** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « ונוהגין ללוש כדי שעור חלה בבית לעשות מהם לחמים לבצוע עליהם בשבת ויום טוב, והוא מכבוד שבת ויום טוב, ואין לשנות »
  - ancrage : 44 consonnes au début + 18 à la fin dans **Shulchan Arukh, Orach Chayim 242**, préfixe et suffixe se chevauchent — l'écart est une variante d'orthographe, non un passage sauté
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « אלא הביאו בהבלעה עם שאר הימים, כגון שהביא לו בבת אחת שכר ארבעה וחמשה ויום השבת ביניהם, שאין בזה איסור משום שכר שבת »
  - ancrage : 46 consonnes au début + 27 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 243**, préfixe et suffixe se chevauchent — l'écart est une variante d'orthographe, non un passage sauté
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « כל מי שאינו רוחץ באותו מרחץ כל ימות החל אינו יודע שמרחץ זה הוא של ישראל »
  - ancrage : 24 consonnes au début + 32 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 243**, préfixe et suffixe se chevauchent — l'écart est une variante d'orthographe, non un passage sauté
- **243** · niveau 4 · niveau-4-daat-harav.html
  - « שגם הרחיים דרך רוב העולם ליתן באריסות כמו שדות ; אבל התנור דינו כמרחץ במקום שאסור להשכירו לנכרי »
  - ancrage : 43 consonnes au début + 13 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 243**, trou de 4 consonnes au milieu
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html
  - « שגם הרחיים דרך רוב העולם ליתן באריסות כמו שדות; אבל התנור דינו כמרחץ במקום שאסור להשכירו לנכרי »
  - ancrage : 43 consonnes au début + 13 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 243**, trou de 4 consonnes au milieu
- **246** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html · **guillemet ASCII à l'intérieur**
  - « אבל להשאיל לו כלים שעושים בהם מלאכה מתר אפלו בערב שבת סמוך לחשכה, דכיון שאין ריוח לישראל במה שהעכו"ם רשאי לעשות בהם בשבת — אין נראה כאלו עושה בשליחותו »
  - ancrage : 62 consonnes au début + 39 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 246**, trou de 18 consonnes au milieu
- **260** · niveau 4 · niveau-4-daat-harav.html
  - « מצוה לרחוץ כל גופו בחמין בערב שבת, ואם אי אפשר לו — ירחץ פניו ידיו ורגליו »
  - ancrage : 15 consonnes au début + 32 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 260**, trou de 9 consonnes au milieu
- **268** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « אינו חוזר אלא לתחלת ברכה של שבת ; אבל אם כבר סים תחנונים — צריך לחזור לראש אף על פי שעדין לא עקר רגליו" »
  - ancrage : 25 consonnes au début + 53 à la fin dans **Shulchan Arukh HaRav, Orach Chayim 268**, préfixe et suffixe se chevauchent — l'écart est une variante d'orthographe, non un passage sauté
- **270** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « ואין נוהגין כן בחנוכה, ובשבת של חול המועד אין אומרים אותו (מנהגים), וכן ביו״ט שחל להיות בשבת אין אומרים אותו (מהרי״ל הלכות סוכה) »
  - ancrage : 20 consonnes au début + 46 à la fin dans **Shulchan Arukh, Orach Chayim 270**, trou de 5 consonnes au milieu
- **288** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « אין להתענות בשבת אלא אם כן התענית עונג לו »
  - ancrage : 15 consonnes au début + 12 à la fin dans **Mishnah Berurah 288**, trou de 6 consonnes au milieu
- **316** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "כל המחוסר צידה — פטור ; שאינו מחוסר צידה — חייב" »
  - ancrage : 19 consonnes au début + 13 à la fin dans **Turei Zahav on Shulchan Arukh, Orach Chayim 316**, trou de 2 consonnes au milieu
- **318** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "כלי ראשון מבשל; כלי שני אינו מבשל" »
  - ancrage : 12 consonnes au début + 14 à la fin dans **Beit Yosef, Orach Chayim 318**, préfixe et suffixe se chevauchent — l'écart est une variante d'orthographe, non un passage sauté
- **337** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "יש מחמירין אפילו במרוצף, וכן נוהגין ואין לשנות" »
  - ancrage : 12 consonnes au début + 18 à la fin dans **Shulchan Arukh, Orach Chayim 337**, trou de 8 consonnes au milieu
- **353** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אין נותנין עליו אלא כלי חרס וזכוכית" »
  - ancrage : 13 consonnes au début + 17 à la fin dans **Shulchan Arukh, Orach Chayim 353**, préfixe et suffixe se chevauchent — l'écart est une variante d'orthographe, non un passage sauté
## PARTIELLES — 40

Un long fragment se retrouve dans l'appareil du siman, le reste nulle part. Soit la citation
déborde sur une source que ce balayage n'interroge pas, soit une clause a été ajoutée à un
verbatim réel — et ce second cas est grave, puisqu'il met sous guillemets ce que la source
ne dit pas.

- **242** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan.html
  - « והא דאמר ר״ע (שבת קיח.) עשה שבתך חול ואל תצטרך לבריות היינו בדלא אפשר ליה אבל אפשר ליה צריך לכבדו כפי יכולתו »
  - ancrage : 33 consonnes sur 83 dans **Turei Zahav on Shulchan Arukh, Orach Chayim 242**
- **242** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « תבשיל של תרדין ודגים גדולים וראשי שומין »
  - ancrage : 13 consonnes sur 33 dans **Mishnah Berurah 242**
- **243** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « "קבלנות בזה והבלעה — חד מילתא היא" »
  - ancrage : 18 consonnes sur 25 dans **Turei Zahav on Shulchan Arukh, Orach Chayim 243**
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « אם יש שם אדם שהשכירם או נתנם באריסות שנה אחר שנה עד שנתפרסם לרבים שאין דרכו לשכור פועלים אלא להשכירם או לתתן באריסות »
  - ancrage : 85 consonnes sur 94 dans **Shulchan Arukh HaRav, Orach Chayim 243**
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « אם יש שם אדם שהשכירם או נתנם באריסות שנה אחר שנה עד שנתפרסם לרבים שאין דרכו לשכור פועלים אלא להשכירם — מותר »
  - ancrage : 81 consonnes sur 85 dans **Shulchan Arukh HaRav, Orach Chayim 243**
- **243** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « תנור דינו כמרחץ, רחיים דינם כשדה »
  - ancrage : 13 consonnes sur 26 dans **Shulchan Arukh HaRav, Orach Chayim 243**
- **244** · niveau 1 · niveau-1-base.html
  - « אין הישראל מקפיד עליו »
  - ancrage : 15 consonnes sur 18 dans **Shulchan Arukh HaRav, Orach Chayim 244**
- **246** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « אין אנו מצוים על שביתת הכלים שלנו »
  - ancrage : 16 consonnes sur 27 dans **Shulchan Arukh HaRav, Orach Chayim 246**
- **246** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « יש רוח לישראל / אין רוח לישראל »
  - ancrage : 12 consonnes sur 23 dans **Shulchan Arukh HaRav, Orach Chayim 246**
- **249** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « אין הולכין בערב שבת יותר משלש פרסאות »
  - ancrage : 21 consonnes sur 30 dans **Beit Yosef, Orach Chayim 249**
- **250** · niveau 4 · niveau-4-daat-harav.html
  - « מאי ויום הששי? — לעולם ישכים אדם »
  - ancrage : 13 consonnes sur 24 dans **Beit Yosef, Orach Chayim 250**
- **262** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « לקראת המלך / לקראת חתן וכלה »
  - ancrage : 12 consonnes sur 21 dans **Shulchan Arukh, Orach Chayim 262**
- **263** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « להדליק נר של שבת [קדש] »
  - ancrage : 13 consonnes sur 16 dans **Shulchan Arukh, Orach Chayim 263**
- **263** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « להדליק נר של שבת קדש »
  - ancrage : 13 consonnes sur 16 dans **Shulchan Arukh, Orach Chayim 263**
- **266** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « ודוקא כשנותן להם משחשיכה, אבל כשנותן להם מבעוד יום מותר בכל ענין »
  - ancrage : 36 consonnes sur 52 dans **Shulchan Arukh, Orach Chayim 266**
- **268** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « "לפי שברכה זו לא נתקנה בשבת בגלל חובת היום אלא מפני המזיקין" »
  - ancrage : 45 consonnes sur 47 dans **Shulchan Arukh HaRav, Orach Chayim 268**
- **274** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « ודוקא בליל שבת. אבל ביום השבת או בליל יו״ט בוצעין על העליונה »
  - ancrage : 25 consonnes sur 47 dans **Shulchan Arukh, Orach Chayim 274**
- **274** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « ועל כולן צריך לבצוע על שתי ככרות »
  - ancrage : 19 consonnes sur 26 dans **Mishnah Berurah 274**
- **279** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "נר שהדליקו בו באותו שבת — אסור לטלטלו. שלא הדליקו בו — מותר לטלטלו." »
  - ancrage : 29 consonnes sur 50 dans **Shulchan Arukh, Orach Chayim 279**
- **282** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « משה רבנו תיקן להם לישראל שיהיו קוראין בתורה ברבים »
  - ancrage : 21 consonnes sur 41 dans **Shulchan Arukh HaRav, Orach Chayim 282**
- **303** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שמא תשלפם ותראה אותם לחבירתה" »
  - ancrage : 13 consonnes sur 24 dans **Shulchan Arukh HaRav, Orach Chayim 303**
- **303** · niveau 1,2 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-2-lamdan-en.html …
  - « שמא תשלפם להראותם לחבירתה »
  - ancrage : 14 consonnes sur 22 dans **Shulchan Arukh HaRav, Orach Chayim 303**
- **310** · niveau 3 · niveau-3-synthese.html
  - « הוקצה למקצת השבת = הוקצה לכל השבת »
  - ancrage : 12 consonnes sur 26 dans **Shulchan Arukh HaRav, Orach Chayim 310**
- **310** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « הוקצה למקצת השבת — הוקצה לכל השבת »
  - ancrage : 12 consonnes sur 26 dans **Shulchan Arukh HaRav, Orach Chayim 310**
- **330** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « יולדת כחולה שיש בו סכנה »
  - ancrage : 14 consonnes sur 19 dans **Shulchan Arukh, Orach Chayim 330**
- **333** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « מפני אורחים או ביטול בית המדרש »
  - ancrage : 13 consonnes sur 25 dans **Beit Yosef, Orach Chayim 333**
- **334** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « יש בה חשש סכנת נפשות »
  - ancrage : 12 consonnes sur 16 dans **Shulchan Arukh, Orach Chayim 334**
- **337** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « דבר שאין מתכוון מותר — ובלבד שלא יהא פסיק רישיה »
  - ancrage : 20 consonnes sur 37 dans **Beit Yosef, Orach Chayim 337**
- **346** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "כל רשויות שלנו כרמלית" »
  - ancrage : 12 consonnes sur 18 dans **Shulchan Arukh, Orach Chayim 346**
- **347** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "העושה את כולה ולא העושה את מקצתה; יחיד ועשה אותה — חייב, שניים ועשו אותה — פטורים" »
  - ancrage : 43 consonnes sur 61 dans **Shulchan Arukh HaRav, Orach Chayim 347**
- **349** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אף על פי שהחפץ הולך כמה מילין ברה״ר" »
  - ancrage : 25 consonnes sur 27 dans **Shulchan Arukh, Orach Chayim 349**
- **351** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אמרינן לבוד ושם גג עליה" »
  - ancrage : 16 consonnes sur 19 dans **Mishnah Berurah 351**
- **352** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "גוללו אצלו אפילו נתגלגל חוץ לד' אמות, ואפילו ברה״ר והאסקופה ברה״י" »
  - ancrage : 23 consonnes sur 51 dans **Shulchan Arukh HaRav, Orach Chayim 352**
- **354** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « לא דרסי בה רבים כלל, והוי מקום פטור" »
  - ancrage : 16 consonnes sur 27 dans **Mishnah Berurah 354**
- **357** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "תקנו לו זכר לשבת שלא ישכח וישפכם ברשות הרבים הוא בעצמו" »
  - ancrage : 38 consonnes sur 44 dans **Shulchan Arukh HaRav, Orach Chayim 357**
- **358** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שכן דרך הקרפפות להיות בהן אילנות" »
  - ancrage : 20 consonnes sur 27 dans **Shulchan Arukh HaRav, Orach Chayim 358**
- **360** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "דהוי ליה אינך כחצר לאמצעי" »
  - ancrage : 20 consonnes sur 21 dans **Shulchan Arukh, Orach Chayim 360**
- **362** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « למלא האויר שבין הענפים »
  - ancrage : 18 consonnes sur 19 dans **Shulchan Arukh, Orach Chayim 362**
- **363** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "כיון דלשריפה קיימא — כתותי מכתת שיעורא" »
  - ancrage : 30 consonnes sur 31 dans **Shulchan Arukh, Orach Chayim 363**
- **365** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אבל אי בקעי בה רבים אפילו לא נפרץ רק ד' טפחים צריך לתקנו שם" »
  - ancrage : 30 consonnes sur 45 dans **Shulchan Arukh, Orach Chayim 365**
## ABSENTES — avec une source revendiquée — 40

**C'est la pile à lire en premier.** Chacune de ces citations **nomme** sa source ; cette
source, telle que Sefaria la rend, ne la porte pas là où l'appareil du siman la cherche.
Attention : plusieurs de ces « références » sont en réalité de la prose de rédaction posée
dans la case d'une source (« אין הגהה על העיקר… », « no הגהה on the timing… »), ce qui est
un défaut de forme distinct et qui mérite d'être mesuré à part.

- **242** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « בשר ויין ופירות וכל מטעמים »
  - 22 consonnes · source revendiquée : רש״י
- **242** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « יחליף בגדיו לכבוד שבת »
  - 18 consonnes · source revendiquée : no הגהה on the timing of laundry in 242; cf. Rama 250 on erev Shabbos preparations
- **242** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « לוו עלי ואני פורע. והא דאמר (פסחים דף ק.) עשה שבתך חול ואל תצטרך לבריות ה״מ כשאין. לו [א] לפרוע »
  - 68 consonnes · source revendiquée : פסחים דף ק. ; תוספות ביצה ט״ו ע״ב ד״ה לוו עלי
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html · **guillemet ASCII à l'intérieur**
  - « אבל שדה — מתר להשכירו לעכו"ם שיעבוד בו העכו"ם, ויטול השכר לעצמו »
  - 48 consonnes · source revendiquée : אין הגהה על בסיס העיקרון; ראה פרטים על תנור / רחיים בסעיף הבא
- **243** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html · **guillemet ASCII à l'intérieur**
  - « מרחץ ותנור של ישראל אסור להשכירן לעכו"ם, שהם דברים שעושין בהם מלאכה בפרהסיא, והכל יודעים שהם של ישראל, ויאמרו שהעכו"ם שכיר יום של הישראל »
  - 108 consonnes · source revendiquée : on this central seif, the Rama does not add a hagaha; see his hagaha on 243:2 for תנור / רחיים
- **245** · niveau 4 · niveau-4-daat-harav-he.html
  - « חלוקת רווחי שבת »
  - 13 consonnes · source revendiquée : אין הגהה על העיקר; ראה הגהות על תנאי הרטרואקטיביות בסעיף הבא
- **245** · niveau 4 · niveau-4-daat-harav-he.html, niveau-4-daat-harav.html · **guillemet ASCII à l'intérieur**
  - « ישראל ועכו"ם שהם שתפים במלאכה, אם התנו מתחלה שיהיה ריוח השבת לעכו"ם לבדו וריוח יום אחד מימות החל לישראל לבדו — מתר »
  - 89 consonnes · source revendiquée : אין הגהה על העיקר; ראה הגהות על תנאי הרטרואקטיביות בסעיף הבא ; פסחים נ ע״ב, עבודה זרה כב ע״א
- **247** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « קלות שבת בעיניו »
  - 13 consonnes · source revendiquée : Hil. Shabbat 6:1
- **248** · niveau 4 · niveau-4-daat-harav.html
  - « על מנת שישבת »
  - 10 consonnes · source revendiquée : שבת י״ט ע״א, citée au ס״ק א
- **248** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan.html
  - « רב אלפס פי׳ הטעם משום עונג שבת שכל ג׳ ימים הראשונים גופו משתבר ואין רוחו חוזרת עד אחר ג׳ ימים ולכן מתירין בנהרות הנובעים שאינו מצטער »
  - 104 consonnes · source revendiquée : טור אורח חיים רמ״ח
- **250** · niveau 4 · niveau-4-daat-harav.html
  - « יהא שלחנו ערוך ומטתו מצעת »
  - 21 consonnes · source revendiquée : rituel de l'arrivée de Shabbat avec les anges ; לחם משנה ou substitut symbolique ; סעודה שלישית — Shabbat 117b
- **250** · niveau 4 · niveau-4-daat-harav.html
  - « כל המענג את השבת על ידי דגים »
  - 22 consonnes · source revendiquée : le minhag aschkenaze sur les plats spécifiques est documenté dans les Aharonim plutôt que dans une הגהה du Rama
- **252** · niveau 4 · niveau-4-daat-harav-he.html
  - « נותנין חטין לתוך הריחים של מים רק סמוך לחשכה »
  - 36 consonnes · source revendiquée : בית שמאי בשבת יז ע״ב טוען לאיסור; בית הלל לבסוף מתיר ; הרמ״א דן בקול בהגהה שלו על רנ״ב:ה — ראה בסוף הסעיף
- **253** · niveau 4 · niveau-4-daat-harav.html
  - « תבשיל שבשל כמאכל בן דרוסאי, אפלו אינו קטומה — שרי להשהותו »
  - 45 consonnes · source revendiquée : le seuil minimum de cuisson — équivalent du tiers cuit selon Rashi, ou de la moitié selon Rambam
- **254** · niveau 4 · niveau-4-daat-harav.html
  - « והאדנא נוהגין להשהותן »
  - 19 consonnes · source revendiquée : Shabbat 119a
- **258** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan.html
  - « ובהא אתי שפיר מה שנוהגין להטמין מבעוד יום מיני עיסה בקדרה קטנה תוך גדולה אע״ג דהוה ליה הטמנה ממש עיין סי׳ שכ״ו »
  - 86 consonnes · source revendiquée : קונטרס אחרון לשו״ע הרב רנ״ח
- **260** · niveau 4 · niveau-4-daat-harav.html
  - « יהא לו בגדים נאים מיחדים לשבת »
  - 24 consonnes · source revendiquée : pas de הגהה sur ce seif — le Rama suit le Mehaber et la pratique aschkenaze
- **263** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « יברך קדם שידליק »
  - 13 consonnes · source revendiquée : the Rama has no explicit הגהה on the order, but the Ashkenazi minhag reverses it — see MB for the justification
- **263** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « נר של שבת קדש »
  - 10 consonnes · source revendiquée : the Rama has no explicit הגהה on the order, but the Ashkenazi minhag reverses it — see MB for the justification
- **263** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « נשים מזהרות בה יותר »
  - 16 consonnes · source revendiquée : שָׁמוֹר וְזָכוֹר → 2 dimensions of Shabbat
- **266** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "לא התירו לטלטל ד' אמות אלא לפיקוח נפש" »
  - 29 consonnes · source revendiquée : קנ״ג ע״ב
- **266** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "מי שהחשיך בדרך נותן כיסו לנכרי, ואם אין עמו נכרי מניחו על החמור. הגיע לחצר החיצונה נוטל את הכלים הנטלין בשבת, ושאינן נטלין מתיר את החבלים והשקין נופלין מאליהן." »
  - 127 consonnes · source revendiquée : קנ״ג ע״א
- **266** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « הילדות היא תהליך — שמירה הוא בניית מצוות »
  - 32 consonnes · source revendiquée : סוף פרק כ״ד ; קנ״ג ע״ב
- **266** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « עקירה היא רק במצב מנוחה »
  - 19 consonnes · source revendiquée : שבת קנ״ג ע״א ד״ה מניחו על החמור
- **268** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « חשיבנא ליה כטעה »
  - 13 consonnes · source revendiquée : considéré comme s'étant trompé entre Amidot de Shabbat
- **268** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « להוציא שאינו יודע »
  - 15 consonnes · source revendiquée : סעיף ג ; סעיף ז ; סעיף יג
- **268** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « להזכיר שבחו של המקום »
  - 17 consonnes · source revendiquée : ברכות כ״א ע״א ד״ה לא יצא
- **270** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « קריאת משנה בפרהסיא »
  - 16 consonnes · source revendiquée : Mishnah, Aggadah ; Public recital of Mishnah
- **276** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « מצוה (סעודת חתנה / מילה) »
  - 17 consonnes · source revendiquée : בשם בעל העיטור
- **290** · niveau 3 · niveau-3-synthese-he.html
  - « פועלים מול ת״ח »
  - 11 consonnes · source revendiquée : רמ״א
- **303** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « תפור / קלוע / קבוע »
  - 12 consonnes · source revendiquée : סעיף כה
- **320** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « אין סוחטין אותן. ואם יצאו מעצמן — אסורין. ר' יהודה אומר אם לאוכלין — היוצא מהן מותר, ואם למשקין — היוצא מהן אסור" »
  - 83 consonnes · source revendiquée : במפרק
- **320** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « משקין הבאין לאוכל — כאוכל הם »
  - 22 consonnes · source revendiquée : תוס׳ שבת קמ״ה. ; ר״ן
- **322** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « תיקון כלי / מחתך »
  - 12 consonnes · source revendiquée : ס״ק ב
- **323** · niveau 3 · niveau-3-synthese-he.html
  - « האם דומה לתיקון כלי? »
  - 16 consonnes · source revendiquée : סעיף 6 ; סעיף 7
- **343** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אמר רבי יוחנן : ב עושה על דעת אביו , דכוותיה גבי גוי דעושה על דעת ישראל — מי שרי? גוי אדעתא דנפשיה עביד" »
  - 76 consonnes · source revendiquée : ובהמשך הסוגיא :  "רבי יוחנן ספוקי מספקא ליה"  — ואין בדף מחלוקת רב הונא ור' יוחנן. ; ס״ק א
- **343** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "קטן הבא לכבות — אומרים לו 'אל תכבה', ששביתתו עליהם" »
  - 37 consonnes · source revendiquée : ובהמשך הסוגיא :  "רבי יוחנן ספוקי מספקא ליה"  — ואין בדף מחלוקת רב הונא ור' יוחנן. ; ס״ק א
- **351** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "ויחבר ידו — והוא הדין פיו או כלי" »
  - 24 consonnes · source revendiquée : ס״ק א ; ס״ק ב
- **361** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "לאו כרה״ר ממש, דאי הכי לא היה מהני סולם, אלא ר״ל כעין רה״ר" »
  - 41 consonnes · source revendiquée : ס״ק ג
- **365** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שלא אמרו שיעור אורך מבוי ד' אמות אלא הבא לעשות הכשר מבוי בתחלה, אבל מבוי שהיה כשר מתחלתו אינו נפסל עד שלא נשתייר בו ד' טפחים" »
  - 96 consonnes · source revendiquée : ס״ק ב
## ABSENTES — sans source, 25 consonnes ou plus — 45

Ces citations ne sont confrontables à rien : elles portent des guillemets sans dire d'où
elles viennent. C'est la règle 26-bis, et c'est un défaut en soi, indépendamment de ce que
la lecture révélera.

- **242** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « אף שכבוד ועונג שבת מדרבנן, מכל מקום צריך להיזהר בהם מאד, שדברי סופרים חמורים יותר מדברי תורה »
  - 74 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **246** · niveau 4 · niveau-4-daat-harav-he.html
  - « האם יש רווח גלוי לי ממלאכת השבת? »
  - 25 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **247** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « "ואפלו קצץ, אם לא קבוע בי דואר באותה העיר אסור" »
  - 35 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **247** · niveau 2 · niveau-2-lamdan-he.html
  - « (2) ראיית הציבור שהגוי עושה את הפעולה בשבילו של ישראל »
  - 41 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **248** · niveau 2 · niveau-2-lamdan-he.html
  - « להמנע מלהיכנס בכוונה למצבים שיביאו לחילול שבת »
  - 39 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **249** · niveau 2 · niveau-2-lamdan-he.html · **guillemet ASCII à l'intérieur**
  - « "לא ילך אדם בערב שבת יותר מג' פרסאות, כדי שיוכל להגיע לביתו ולעשות צרכי שבת" »
  - 58 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **257** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav-he.html, niveau-4-daat-harav.html
  - « אין טומנין בדבר המוסיף הבל אפלו מבעוד יום, אבל בדבר שאינו מוסיף הבל — מתר להטמין מבעוד יום »
  - 71 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **266** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « בהמתו של אדם — שביתתה עליו מן התורה »
  - 27 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **268** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « בלילי שבתות, אומר אחר תפלת הציבור — שליח צבור ברכה אחת מעין שבע: 'מגן אבות' »
  - 56 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **268** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « טעה והתחיל בשל חול: גומר אותה ברכה ופותח של שבת »
  - 37 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **272** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אמר רב זוטרא בר טוביה אמר רב: אין אומרים קידוש היום אלא על היין הראוי לנסך על גבי המזבח." »
  - 68 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **273** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « אם קידש בבית זה ונמלך לאכול בבית אחר — צריך לקדש בבית האחר »
  - 45 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **274** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אמר רבי אבא: בשבת חייב אדם לבצוע על שתי ככרות. דכתיב 'לקטו לחם משנה' (שמות טז:כב)." »
  - 59 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **274** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « חייב אדם לאכול שלוש סעודות בשבת »
  - 26 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **275** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "לא יקרא לאור הנר. באמת אמרו: החזן רואה היכן תינוקות קוראים, אבל הוא לא יקרא." »
  - 58 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **276** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « אסרו חכמים לומר לעכו״ם לעשות לנו מלאכה בשבת — אף על פי שאינו מצווה על השביתה »
  - 59 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **277** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "גרם כיבוי מותר" — רבי יוסי. וחכמים אוסרים. »
  - 31 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **278** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אמר רב יהודה: מכבין את הנר מפני חולה כדי שיישן." »
  - 36 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **278** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « פיקוח נפש דוחה שבת — מי שיש בו סכנה ומלאכה צריכה לרפואתו, אסור לאחר. אלא לעשות מיד. ולא יאמר 'אתאמת אצל פלוני אם אעשה' — אלא מי שהוא מהיר ויודע הוא קודם »
  - 114 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **278** · niveau 3 · niveau-3-synthese.html
  - « פשוט הוא דלא רק מותר אלא חובה לכבות »
  - 28 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **279** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « כל הכלים — בין מותר לטלטלן בין אסור — שיש בהם מוקצה — אסור לטלטלן »
  - 48 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **281** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "ולא יוסיף — כדי שלא יזחיח דעתו עליו" (= שלא יחזיק טובה לעצמו). »
  - 44 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **281** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « לא ישחה ולא יעצור עצמו מלשחות במקומות שתיקנו חכמים »
  - 42 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **282** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "בשבת בשחרית — שבעה עולים. בשני וחמישי ובשבת במנחה — שלושה. אין פוחתין מהם ואין מוסיפין עליהם." »
  - 72 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **283** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "אין קוראין בתורה פחות משלושה פסוקים." »
  - 30 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **283** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « אין קוראים בתורה פחות משלושה פסוקים »
  - 30 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **289** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "רבי ינאי לביש מאני מעליי, ואמר: בואי כלה, בואי כלה" »
  - 38 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **301** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שמא יפול ויביאנו ארבע אמות ברה״ר" »
  - 26 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **301** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « שמא יפול ויבוא להביא ארבע אמות ברשות הרבים »
  - 35 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **302** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "מקפלין את הכלים מארבעה וחמשה פעמים" »
  - 29 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **303** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "דחיישינן דלמא מטבילי וקא מטו ד׳ אמות ברה״ר" »
  - 33 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **303** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « "שמא תשלפם להראותם לחבירתה ותעבירם ד׳ אמות ברה״ר" »
  - 38 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **305** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "במה בהמה יוצאה ובמה אינה יוצאה — יוצאה הגמל באפסר, והנאקה בחטם, ולובדקים בפרומביא, והסוס בשיר, וכל בעלי השיר יוצאין בשיר ונמשכין בשיר, ומזין עליהן וטובלן במקומן" »
  - 128 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **307** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « "כל מה שאסור לישראל לעשות בעצמו אסור לומר לנכרי לעשותו" »
  - 44 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **307** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "כל שאסור לישראל לעשות אסור לומר לנכרי" »
  - 31 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **309** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שכח אבן על פי החבית — מטה על צידה והיא נופלת ; הניחה ע״ד שתישאר שם — בסיס לדבר האסור היא והכלי כולו אסור" »
  - 77 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **309** · niveau 3 · niveau-3-synthese.html
  - « הוקצה למקצת השבת — הוקצה לכל השבת »
  - 26 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **311** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "רבי יהודה בן לקיש אומר מטלטלין את המת מטה למטה — ולא ע״י ככר ותינוק" »
  - 51 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **315** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "כל אהל שאינו עשוי לדור בו אינו חייב עליו" »
  - 32 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **317** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "ואלו קשרים שחייבין עליהן — קשר הגמלין וקשר הספנין ; וכשם שהוא חייב על קשורן כך הוא חייב על היתרן" »
  - 75 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **323** · niveau 3 · niveau-3-synthese-he.html
  - « האם הכלי הזה ישרת אותי היום , לפני צאת השבת? »
  - 33 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **324** · niveau 3 · niveau-3-synthese-he.html
  - « בלעדי, האם הבהמה יכולה לאכול את זה? »
  - 27 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **324** · niveau 1 · niveau-1-base-he.html
  - « האם המאכל היה כבר אכיל כפי שהוא? »
  - 25 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **340** · niveau 3 · niveau-3-synthese-he.html
  - « מאיזו אב נגזר המעשה, ו מתי הוא עובר את הסף? »
  - 32 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **350** · niveau 2 · niveau-2-lamdan-he.html · **guillemet ASCII à l'intérieur**
  - « "לא יעמוד ברה״י ויוציא ראשו לרה״ר וישתה" »
  - 30 consonnes · source revendiquée : AUCUNE sur ±2 lignes
## ABSENTES — sans source, moins de 25 consonnes — 69

Le plus souvent, ce ne sont pas des citations : le sujet d'une hakira, un intitulé de
colonne, un terme technique. Les guillemets y sont de trop — la convention du dépôt les
réserve au verbatim. À reformuler sans guillemets plutôt qu'à confronter.

- **244** · niveau 4 · niveau-4-daat-harav-he.html
  - « האם נראה שהוא פועל בשבילי? »
  - 21 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **245** · niveau 1 · niveau-1-base.html
  - « וצריך לזהר בזה ממראית העין »
  - 22 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **245** · niveau 4 · niveau-4-daat-harav-he.html
  - « חלק הנכרי שמעולם לא היה לי »
  - 21 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **246** · niveau 1 · niveau-1-base.html
  - « אין ראוי לו להשכירה כלל »
  - 19 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **247** · niveau 2 · niveau-2-lamdan-he.html
  - « (1) פעולה בשבת על ידי הגוי »
  - 18 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **247** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « קביעות בי דואר »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **248** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « דבר מצוה / דבר רשות »
  - 14 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **248** · niveau 1 · niveau-1-base-en.html
  - « משום סכנה (פיקוח נפש) »
  - 16 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **248** · niveau 1 · niveau-1-base.html
  - « עליה לארץ ישראל = דבר מצוה »
  - 20 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **248** · niveau 1 · niveau-1-base-he.html
  - « עלייה לארץ ישראל = דבר מצוה »
  - 21 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **249** · niveau 2 · niveau-2-lamdan-he.html
  - « (3) תענית אנשי מעשה »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **249** · niveau 4 · niveau-4-daat-harav-en.html, niveau-4-daat-harav.html
  - « אין הולכין לסעדה בערב שבת »
  - 21 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **249** · niveau 2 · niveau-2-lamdan-he.html
  - « דורות שלאחר ירושלים »
  - 17 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **249** · niveau 2 · niveau-2-lamdan-he.html
  - « תכלית הכבוד שבת »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **251** · niveau 2 · niveau-2-lamdan-he.html
  - « תיקון לכבוד שבת »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **264** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « האור נאחז / נתלה »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **265** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « להגן על האדם מתקלה »
  - 15 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **265** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « להגן על הנר מהפרעה »
  - 15 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **267** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "עבד כמר עבד, ועבד כמר עבד" »
  - 19 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **267** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שינוי קבלת שבת" »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **269** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "תקנה שבטל טעמה" »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **269** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « להוציא אורחים ידי חובה »
  - 19 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **269** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « תקנה שבטל טעמה »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **270** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "קריאת תורה שבעל פה בציבור" »
  - 21 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **270** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « ערוב, מעשר, נר »
  - 10 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **275** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « שמא ישכח וייטה את הנר »
  - 17 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **278** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « בספק פקוח נפש מקילין »
  - 17 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **283** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « שלשה פסוקים לכל עולה »
  - 17 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **289** · niveau 1 · niveau-1-base-he.html
  - « לשתות מים לפני התפילה »
  - 18 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **289** · niveau 1 · niveau-1-base-en.html, niveau-1-base.html
  - « לשתות מים לפני התפלה »
  - 17 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **301** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "שדרך בני אדם להוציאו כן" »
  - 19 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **301** · niveau 1 · niveau-1-base-he.html · **guillemet ASCII à l'intérieur**
  - « שמא יפול ויביאנו ד' אמות ברה״ר »
  - 23 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **301** · niveau 1 · niveau-1-base-en.html, niveau-1-base.html
  - « שמא יפול ויביאנו ד׳ אמות ברה״ר »
  - 23 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **301** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « תכשיט שאינו נוי »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **303** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « תפור / קלוע / מעשה אריגה »
  - 17 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **304** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « מדין בעלות הרב »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **307** · niveau 1 · niveau-1-base.html
  - « דבר אמירה לנכרי »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **309** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « הוקצה למקצת השבת »
  - 14 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **309** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « הקצה למקצת השבת — הקצה לכל השבת »
  - 24 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **309** · niveau 1 · niveau-1-base-en.html, niveau-1-base.html
  - « צריך לגופו / למקומו »
  - 15 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **309** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « שכח / הניח מדעת »
  - 11 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **310** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « הוקצה למקצת השבת »
  - 14 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **313** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « מחשבה מערב שבת »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **315** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « אהל קבע / עראי »
  - 10 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **316** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "הצד צבי לבית ולביבר — חייב" »
  - 20 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **317** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « קשר על גבי עניבה »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **320** · niveau 1,3 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html, niveau-3-synthese-en.html …
  - « משקין הבאין לאוכל »
  - 15 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **323** · niveau 1 · niveau-1-base-he.html
  - « אחזיר לך משקל מדויק »
  - 16 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **323** · niveau 3 · niveau-3-synthese-he.html
  - « תן לי בסכום זה »
  - 11 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **323** · niveau 3 · niveau-3-synthese-he.html
  - « תן לי ליטר / קילו »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **323** · niveau 3 · niveau-3-synthese-he.html
  - « תן לי מידה / מחיר »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **326** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « שמא יחם מים בשבת »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **330** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html · **guillemet ASCII à l'intérieur**
  - « "יולדת — חיה היא" »
  - 11 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **333** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « טרחה ועובדין דחול »
  - 15 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **333** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « טרחה יתרה / עובדין דחול »
  - 18 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **334** · niveau 3 · niveau-3-synthese-he.html · **guillemet ASCII à l'intérieur**
  - « "שמא מתוך טרדה יבוא לכבות" »
  - 20 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **335** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « נסדקה ועביד טיף טיף »
  - 16 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **338** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « השמעת קול דרך שיר »
  - 14 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **340** · niveau 3 · niveau-3-synthese-he.html
  - « זה אינו האב עצמו »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **340** · niveau 1 · niveau-1-base-he.html
  - « מאיזו אב מלאכה הוא נגזר מעשי? »
  - 23 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **341** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « מוגבלת ליום שמעו »
  - 14 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **342** · niveau 2 · niveau-2-lamdan-he.html · **guillemet ASCII à l'intérieur**
  - « "ועיין לעיל סי' רס״א וסוף סי' ש״ז" »
  - 22 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **351** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html · **guillemet ASCII à l'intérieur**
  - « ד' על ד' / למעלה מעשרה »
  - 14 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **352** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « הנחה / נח על הארץ »
  - 12 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **354** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « אשפה של רבים / של יחיד »
  - 16 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **356** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « בטל לגבי רשות היחיד »
  - 16 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **358** · niveau 1 · niveau-1-base-en.html, niveau-1-base-he.html, niveau-1-base.html
  - « מעוט / בטול הדירה »
  - 13 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **359** · niveau 3 · niveau-3-synthese-en.html, niveau-3-synthese-he.html, niveau-3-synthese.html
  - « פתח קדם להקף »
  - 10 consonnes · source revendiquée : AUCUNE sur ±2 lignes
- **362** · niveau 2 · niveau-2-lamdan-en.html, niveau-2-lamdan-he.html, niveau-2-lamdan.html
  - « היתה והוסרה וחזרה »
  - 15 consonnes · source revendiquée : AUCUNE sur ±2 lignes