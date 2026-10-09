# Niveau 1 d'Orah Haïm — ce que le Rav doit relire (chantier 3, octobre 2026)

Le niveau 1 de quatorze simanim d'Orah Haïm (3, 8, 53, 55, 66, 79, 90, 94, 113, 128, 153, 158,
159, 160) omettait des séifs entiers ou en coupait la fin sans le dire au lecteur : 157 séifs restaurés
(commits 39d7d567 à 42140f53), puis le texte source rendu conforme, séif par séif, à une édition de
Sefaria — Maginei Eretz (Lemberg 1893) ou Torat Emet 363 — avec l'ordre du Choul'han Aroukh rétabli
(commits 368bb709 à b433e894). Chaque lot a été confronté à Sefaria par un arbitre avant commit.

Ce qu'aucune machine ne tranche, et qui revient au Rav, est ici :

1. **Les encadrés que le texte restauré contredit ou nuance.** C'est le motif que le veilleur appelle
   « signature C » : la page porte désormais sa propre correction, dans le bloc source, sans que
   l'encadré pédagogique écrit à côté le sache. AUCUN de ces encadrés n'a été réécrit. Certains
   reflètent peut-être la pratique retenue par les décisionnaires postérieurs (la Michna Beroura,
   notamment) plutôt qu'une erreur : c'est précisément ce qui demande un jugement.
2. **Les traductions ajoutées ou changées.** Elles ont été lues côte à côte avec l'hébreu par un
   arbitre, mais elles sont nouvelles.
3. **Les lectures à trancher.**

Ces listes sont reprises des rapports des agents et de leurs arbitres, sans réécriture ; les numéros de
ligne qu'elles citent sont ceux du jour.


## 1. Encadrés que le texte restauré contredit ou nuance


### Simanim 3, 8, 53

- Siman 53, Cas 3, encadré remember « Conduite », trois langues : « S il n avait pas de טלית, qu il s en revête avant ישתבח (et non entre פסוקי דזמרה et ישתבח) » (HE « (ולא בין פסוקי דזמרה לישתבח) », EN « (and not between פסוקי דזמרה and ישתבח) »). Le séif 3, maintenant entier, interdit au Mehaber de bénir sur le tsitsit entre פסוקי דזמרה et ישתבח. Le Rama, lui (« הש״ץ … יתעטף בציצית קודם שיתחיל ישתבח … [כל בו סי׳ ה׳] »), fait s'envelopper le ש״ץ avant ישתבח, c'est-à-dire précisément entre les deux. La parenthèse de l'encadré contredit ce rapport, ou le rend mal. Non corrigé.
- Siman 8, séif 14 : l'encadré key-point de la section E (« Talit ôté (séif 14) : … il rebénit en le remettant — selon l'avis principal. (D'autres avis distinguent…) », HE « לדעה העיקרית », EN de même) et le remember du Cas 4 (« Un talit ôté demande, selon l'avis principal, de rebénir… mais certains avis distinguent… »), trois langues, font de la position du Mehaber l'avis principal. Or la glose du Rama, rétablie entière, conclut « וְיֵשׁ אוֹמְרִים דַּוְקָא כְּשֶׁנִּשְׁאַר עָלָיו טַלִּית קָטָן וְהָכֵי נוֹהֲגִין » : l'usage ashkénaze est de ne pas rebénir quand on avait l'intention de revenir et qu'un talit katan reste sur soi. Non corrigé.
- Siman 3, contradiction éditoriale et non halakhique : la note d'introduction et l'encadré remember de la section 14-16 (« Nous en exposons ici uniquement le principe, avec la pudeur qui convient ») annoncent un exposé de principe. Le texte et la traduction des séifs 14-16 sont maintenant donnés en entier. Non corrigé : c'est au Rav de dire s'il garde la traduction littérale ou s'il veut un autre registre.

### Simanim 55, 66, 79

- 55, Famille E (séifim 13-22), key-point dans les trois langues : « ce qui sépare (מחיצה, seuil, toit) exclut, sauf si l on montre son visage ». Le séif 19 joint au minyan le ש״ץ placé sur une תיבה dont les parois font dix טפחים, parce qu'elle est « בטלה לגבי ב״ה ». Non modifié.
- 66, Séif 7-9, key-point FR : « on colle la fin de la Gueoula au début de la Amida sans rien intercaler ». Le séif 8 permet de mettre les תפילין entre גאולה et תפלה en cas d'אונס, et le Rama fait réciter la berakha avant « גאל ישראל ». Non modifié.
- 79, séif 2, key-point FR : « dès qu il y a un ריח רע, ni séparation ni changement de domaine n aident ». Elle tait le « וי״א » du séif 2, selon lequel la séparation sert aussi pour l'odeur, et la restriction du Rachba (« דוקא כשאינו רואה אותה »). Non modifié.
- 79, séif 4, key-point : « la fiente des poules rouges » en FR, « the excrement of red roosters » en EN. La source du séif 6 dit « צואת תרנגולים אדומה » : אדומה qualifie la צואה. La traduction du séif 6 le rend bien (« la fiente rouge des poules », « red chicken excrement ») ; la key-point HE recopie l'hébreu et n'est pas en cause. C'est une erreur de traduction de l'encadré, non corrigée.

### Simanim 90, 94, 113

- Siman 90, « Cas 1 — Prier sur un lieu élevé », encadré key-point « Conduite » (FR, et sa version EN/HE). « Situation : peut-on prier debout sur une chaise, un banc ou une estrade élevée ? — Conduite : non … On prie au niveau du sol, dans l humilité. » Or 90:2, restauré au tour 2, dit : « היה גבוה ג׳ ויש בו ד׳ אמות על ד׳ אמות הרי הוא כעלייה ומותר להתפלל בו וכן אם היה מוקף מחיצות אע״פ שאין בו ד׳ על ד׳ מותר להתפלל בו ». Le « non » sans réserve sur l'estrade élevée contredit cette permission, même si l'encadré renvoie au Rav pour « l estrade de la synagogue ». NON corrigé.
- Siman 94, « Cas 1 — S orienter à la synagogue », encadré key-point « Conduite » : « Les synagogues placent donc l ארון au mur est. » La glose du Rama 94:2, restaurée au tour 2, dit : « אין עושים מקום הארון וצד התפלה נגד זריחת השמש ממש כי זהו דרך המינים רק מכוונים נגד אמצע היום ». La page le reprend d'ailleurs dans la key-point du séif 1-2. C'est une tension, ou une nuance que l'encadré efface, plutôt qu'une contradiction franche. NON corrigé : à trancher par le Rav.

### Simanim 128

- HE, niveau-1-base-he.html l.723, key-point « אבֵל ופנוי. » : « ונהגו בקצת מקומות שאין נושאין כפים אלא ביום טוב… ». Le Rama, au 128:44 (ME et TE), écrit « נהגו בכל מדינות אלו שאין נושאין כפים אלא בי״ט ». Les traductions FR (« dans toutes ces contrées ») et EN (« in all these lands ») suivent le Rama. L'encadré réduit l'usage à « quelques endroits ». NON corrigé : au Rav de trancher.

### Simanim 153, 158

- 153, key-point du bloc « Séifim 2–6 » (FR « Le résidu (מותר הדמים) suit la même règle (séif 5) », HE « וכן מותר הדמים נוהג בזה (סעיף ה׳) », EN pareil) et Cas 2 (« Le résidu suit la même règle ») : le séif 5 permet de changer le reste « לכל מה שירצו » une fois faite la chose pour laquelle on a collecté. Il permet aussi de le faire descendre si on l'a stipulé en collectant (« התנו … מותר להוריד המותר »).
- 153, key-point du bloc « Séifim 7–9 » (« elle est vendable » pour le village ; « La synagogue de grande ville n est pas vendable »), Cas 1 (« peut être vendue … n est pas vendable ») et le remember « Le siman en une phrase » (« celle de ville non ») : le séif 7 excepte la synagogue de ville que l'on a fait dépendre d'un particulier (« אא״כ תלו אותו בדעת היחיד »), et la glose du Rama interdit de vendre la synagogue de village quand c'est la seule (« אם אין להם רק ב״ה אחת אסור למכרו »).
- 153, Cas 3 (« Sans cette présence, l argent garde sa sainteté ») : le séif 7 donne une autre voie, « ואם קבלו עליהם בני העיר בפירוש במכר זה כל מה שיעשו אפילו יחיד מה שעשה עשה ».
- 153, key-point du bloc « Séifim 10–12 » (« Un bien privé non voué au public garde une latitude que le bien communautaire n a pas ») : le séif 10 n'est qu'un « יש אומרים », suivi de « ויש מי שאוסר אלא אם כן ללמוד תורה או לישא אשה ».
- 153, key-point du bloc « Séifim 13 & 14 » (« Le don d un terrain (séif 14) dépend de l intention initiale du donateur ») : le séif 14 dit « לא מצי ראובן הדר ביה » malgré la protestation d'intention de Reuven. La suite dépend de sa résidence et du חבר עיר.
- 153, key-point du bloc « Séifim 15–17 » (« Même celui qui a prêté sa propre maison ne peut en punir un seul membre par ressentiment ») : la glose du Rama au séif 16 lui donne « הרשות בידו למחות כמו שירצה » s'il l'a stipulé au départ, ou s'il ne l'a pas prêtée expressément.
- 153, key-point du bloc « Séifim 18–21 » : « Un usage régulier fixe la sainteté » et « La consécration prend même par un simple écrit retrouvé » sont présentés comme acquis, alors que les séifs 18 et 19 ne les rapportent qu'au nom de « יש מי שאומר ».

### Simanim 159, 160

- 159:20, Rama « [ויש אומרים דמברכין על טבילת ידים וכן עיקר] » : trois encadrés donnent « al netilat yadaïm » comme conduite, sans mentionner le Rama, dans les trois langues (FR, EN « he still recites the blessing "al netilat yadaïm" », HE « ומברך על נטילת ידים ») : la key-point des séifs 14-20 (« il récite tout de même la bénédiction « al netilat yadaïm » »), le remember « Le siman en une phrase » et la Conduite du Cas 3. Même chose dans niveau-3-synthese et index du 159, hors de mon périmètre. Non corrigé.
- 159:13, Rama « [וכוונת נותן נמי מועיל אפי׳ לכתחלה אפי׳ שלא כוון הנוטל כלל] » : la key-point des séifs 11-13 (« C est celui qui se lave qui doit, a priori, avoir l intention ») et le Cas 3 (« pourvu que celui qui se lave ait l intention voulue ») taisent que l'intention de celui qui verse suffit, même a priori. Trois langues. Non corrigé.
- 159:11-12, Rama « [ואיכא מאן דאמר דקטן פחות מבן ו׳ דינו כקוף] » et « (ומ״מ יש להחמיר) » : le Cas 3 (« même un enfant ») ne fait aucune réserve sur l'enfant de moins de six ans. Trois langues. Non corrigé.
- 159:6, Rama « אבל הסברא הראשונה היא עיקר לכן יש להחמיר לכתחלה » : la key-point du séif 6 cite « l usage qui suit son avis » (celui de Rabbénou Tam) et s'arrête là, sans la suite du Rama. Incomplet, trois langues. Non corrigé.
- 159:14, Rama « [ויש להחמיר לכתחלה] » (quarante séa pour le mikvé) : la key-point des séifs 14-20, le remember et le Cas 3 parlent d'immerger « dans une source ou un mikvé » sans cette réserve. Trois langues. Non corrigé.
- 160:9, passage restauré au tour 2 : « ואם הם עכורים מחמת טיט שנתערב בהם אם הכלב יכול לשתות מהם כשרים ». La key-point du séif 1 (« sa couleur ou sa limpidité » rend l'eau invalide) et le Cas 1 (« une couleur trouble » donne « non ») le contredisent pour une eau troublée par la boue qu'un chien peut boire. Trois langues. Non corrigé.
- 160:10, Mehaber « בכל דבר שתחלתו מן המים » et Rama « (ונראה דוקא אם רסקן …) » : la key-point des séifs 9-12 écrit, en FR et en EN, « tout liquide dont l origine est l eau », sans la condition du Rama ; la version HE dit justement « כל דבר ». Les trois langues divergent donc entre elles. Non corrigé.
- 160:12 : la key-point des séifs 9-12 (« Pour les מי פירות et le vin, יש מי שאומר qu ils conviennent à la rigueur (בשעת הדחק) ») est approximative. La source donne une première opinion, eau seulement ; pour le vin, « וי״א » valable mais interdit a priori, et selon le Rama vin blanc seulement ; pour les jus de fruits seulement, « יש מי שאומר … בשעת הדחק ». Trois langues. Non corrigé.
- 160:13, restauré au tour 2 (« אבל לב׳ שבאו ליטול כאחד האחרון א״צ … מפני שהם באים משיורי טהרה ») : la key-point des séifs 13-15 et le Cas 3 posent « un revi'it par lavage » comme minimum absolu, ce que ce séif nuance. Trois langues. Non corrigé.

## 2. Traductions ajoutées ou changées, à valider


### Simanim 3, 8, 53 — restauration (tour 2)

- Toutes les traductions ajoutées ou remplacées, en FR, EN et HE (div.translation), pour les 26 restaurations listées : 3:6 et 3:7 ; 8:12 à 8:17 ; 53:3, 6, 8 (Rama), 9, 10, 11, 14, 16, 17, 18, 19, 20, 21, 22 (Rama), 23, 25 (Rama), 26. La traduction HE est le texte rendu en hébreu courant, abréviations développées.
- 3:6 : l'ancienne traduction adoucissait le אסור, dans les trois langues (« on évite de dormir orienté est-ouest [lorsque l'épouse est présente] »). Elle est remplacée par « il est interdit … si son épouse est avec lui ; et il convient d'y prendre garde même lorsqu'elle n'est pas avec lui ». À valider.
- 3:7 : à valider, la traduction de « או יסלק הקודש לצדדין » par « ou bien qu'il écarte le lieu saint sur le côté ».
- 8:12 : « אֶחָד וְאֶחָד » (FR) et « אֶחָד » (HE/EN) sont remplacés par « אַחַת וְאַחַת », la leçon des deux éditions. La traduction HE passe de « על כל אחד » à « על כל אחת ואחת ».
- 8:14 : la paraphrase entre crochets (« certains disent : pas s'il avait l'intention de revenir, ou si le talit katan lui reste ») est remplacée par la traduction du Rama rétabli. Le Rama dit « והכי נוהגין » : l'usage est de ne pas rebénir quand il lui reste un talit katan. L'encadré key-point (séif 14) et le Cas 4 du niveau 1, dans les trois langues, présentent la position du Mehaber comme « l'avis principal » et réduisent celle du Rama à « d'autres avis ». Je l'ai signalé, pas réécrit.
- 8:14 : TE donne la source « אגור סימן ל״ד », ME « [אגור סימן ל"ה] ». J'ai suivi TE puisque le bloc est vocalisé.
- 8:17 : TE lit « בִּטֵּל מִצְוַת עֲשֵׂה », ME « ביטל מצות ציצית ». Le bloc vocalisé suit TE, alors que l'encadré « remember » du même bloc cite la leçon de ME vocalisée (« בִּטֵּל מִצְוַת צִיצִית »). La page porte donc deux leçons. Non réécrit.
- 8:16 : la glose du Rama (« וכן יעשה מי שלובש טליתו קודם שיאור היום ») n'a pas le mot « הגה » dans ME ni dans TE. Elle n'est marquée comme glose que dans les traductions.
- Siman 53, Cas 3 (FR/EN/HE) : « qu il s en revête avant ישתבח (et non entre פסוקי דזמרה et ישתבח) ». Le séif 3 du Mehaber, maintenant rétabli, interdit de bénir sur le tsitsit entre פסוקי דזמרה et ישתבח. Le Rama (« מיהו » dans TE) dit que le ש״ץ s'enveloppe avant de commencer ישתבח, c'est-à-dire précisément entre les deux. La parenthèse du Cas 3 paraît contredire ce rapport, ou le rendre mal. Signalé, pas réécrit.
- Siman 53, références de source qui divergent entre éditions (j'ai copié ME, puisque le bloc n'est pas vocalisé) : 19, Maharam de Padoue סי׳ ק״ד (ME) contre ס״ד (TE), et Maharik שורש מ״ד (ME) contre [ל׳] (correction de TE) ; 23, Maharam de Padoue סי׳ מ״ד (ME) contre [מ״ב] (TE) ; 25, Rashba סי׳ ט׳ (ME) contre ש׳ (TE). Leçon aussi en 25 : « בשירי הנכרים » (ME) contre « בשירי הגוים עובדי עבודה זרה » (TE).
- Siman 53, points de traduction à valider : 20, « dire la prière pour son père » (je n'ai ajouté aucune précision de contexte) ; 26, « סתמן כפירושן » et « נכתב לשמו » ; 10, la glose du Rama sur le ערבית de Chabbat ; 25, « שמסר אדם » rendu par « qu il a livré quelqu un ».
- La page du siman 53 en FR et en EN n'emploie aucune apostrophe (« qu il », « l arche »). Les ajouts suivent cette convention.

### Simanim 55, 66, 79 — restauration (tour 2)

- Chaque traduction ajoutée, en FR, EN et HE, est listée séif par séif dans « restaurations ». Les séifs traduits sont 55:3, 5, 7, 9, 10, 12, 13, 16-19, 21, 22 ; 66:3, 5, 6, 8, 10 ; 79:1, 2, 3, 5-8. Le div.translation de la page hébraïque reprend le texte de ME mot pour mot, sans les renvois bibliographiques entre crochets, comme le fait déjà ce div sur ces pages.
- 55:3, glose du Rama : la page rendait « שהרי אומר תתקבל צלותהון ; אבל אין קורין בתורה » comme parole du Mehaber. La traduction de ce membre de phrase l'attribue désormais au Rama, avec le reste de la glose. À trancher aussi : « לאחר שהתחיל בקול רם וקדושה » est rendu littéralement par « après qu il a commencé à voix haute, et la קדושה ».
- 66:10, Rama : « ואין לו פנאי להתפלל מיד אחר קריאת שמע » est lu « n'a pas le loisir de prier aussitôt après la ק״ש ». TE ponctue autrement (« להתפלל, מיד אחר… »). Lecture à confirmer.
- Encadré à revoir, non modifié (55, Famille E) : la key-point dit « ce qui sépare (מחיצה, seuil, toit) exclut ». Or le séif 19 restauré joint le ש״ץ sur une תיבה entourée de parois de dix tefa'him, parce qu'elle est « בטלה לגבי ב״ה ». Il y a une tension dans les trois langues.
- Encadré à revoir, non modifié (66, Séif 7-9) : la key-point dit que l'on joint la Gueoula à la Amida « sans rien intercaler ». Or le séif 8 restauré permet de mettre les תפילין entre גאולה et תפלה en cas d'אונס, et le Rama fait réciter la berakha avant « גאל ישראל ».
- Encadré à revoir, non modifié (79, séif 2) : la key-point dit « dès qu il y a un ריח רע, ni séparation ni changement de domaine n aident ». Or le séif 2 restauré rapporte un « וי״א » selon lequel la séparation sert aussi pour l'odeur, et la position du Rachba, qui exige qu'il ne la voie pas. La key-point n'en dit rien.
- Encadré à revoir, non modifié (79, séif 4) : la key-point FR parle de « la fiente des poules rouges », l'EN de « the excrement of red roosters ». Or dans « צואת תרנגולים אדומה » (79:6, rétabli), אדומה qualifie la צואה et non les volailles. C'est probablement une erreur de traduction de l'encadré.
- 55:13 : le remplissage « — הרי הוא », que la page avait mis à la place du passage omis, a été retiré au profit du texte restauré. C'est la seule modification d'un texte existant qui ne soit pas un ajout.
- 55, retouches de titres et de marqueurs : le titre h3 « (séifim 6, 8, 11-12) » devient « (séifim 6-12) » dans les trois langues, et le marqueur de traduction « Séifim 21-22 » devient « Séif 21 … Séif 22 ».
- Les séifs entièrement absents ont été restaurés en entier depuis ME : 55:10, 55:22 et la glose de 55:21, entre crochets chez ME. Ils gardent donc leurs renvois de source entre crochets et le renvoi « וע״ל ריש סי׳ ק״ן », alors que les blocs voisins n'en montrent pas. Décision éditoriale à confirmer.
- Nouveaux titres h3 composés pour les nouveaux blocs, en FR, EN et HE : 66:6 (« אם פסק אחר שאמר אמת ») et 79:3, 5, 6, 7, 8. Ils sont faits des mots mêmes du séif, et aucun encadré n'a été ajouté.
- FR 55 et 79 : les ajouts suivent la convention de ces deux pages, qui écrivent sans apostrophe (« l un », « s il »). Le défaut préexistait, il n'est pas corrigé.
- verifier-denombrements 55 : un « À VÉRIFIER » de plus, 13 → 14. C'est « היחיד » dans le div.translation hébreu, mot pour mot le séif 17 (« שאין הרוב נגרר אחר היחיד »). C'est un faux positif, et ce verdict ne bloque pas.

### Simanim 90, 94, 113 — restauration (tour 2)

- 90:23, glose du Rama, RETRADUITE au tour 2 : « בגדים שמצוייר עליהם דברי תפלות ». FR : « des vêtements sur lesquels sont représentées des choses indécentes (דברי תפלות) » ; EN : « garments on which indecent things (דברי תפלות) are depicted ». Fichiers : /home/user/Daat.ai/sources/orah-haim/siman-90/niveau-1-base.html et niveau-1-base-en.html.
- 94:9, glose du Rama, RETRADUITE au tour 2 en FR : « ומי שבא בדרך » rendu par « celui qui est en route » ; l'EN « one who is travelling » est inchangé. Fichier : /home/user/Daat.ai/sources/orah-haim/siman-94/niveau-1-base.html.
- 113:2 (séif entier et glose du Rama, dont « (ד״ע לפי הטור) » rendu par « paroles propres du Rama, selon le Tour ») : traductions FR et EN ajoutées.
- 94:1 fin ; 94:2 (séif et glose du Rama : מזרח, דרך המינים, אמצע היום, יצפין/ידרים) ; 94:4, intérieur et fin ; 94:5 (séif et glose du Rama) ; 94:6 (glose du Rama) ; 94:7 ; 94:9 (glose du Rama) : traductions FR et EN ajoutées.
- 90:2-3 ; 90:7-8 (glose du Rama « או שרוכב על הבהמה ») ; 90:9 fin (glose du Rama, Semag) ; 90:10 (glose du Rama) ; 90:12-13 ; 90:15 (deux gloses du Rama) ; 90:16 « ורוצה ללון בה » ; 90:17 ; 90:18 (glose du Rama) ; 90:19 fin ; 90:20 ; 90:21 (gloses du Rama, dont « ולי נראה דבעלי חיים חוצצים ») ; 90:22 ; 90:23 ; 90:24 (gloses du Rama) ; 90:25 ; 90:26 ; 90:27 (glose du Rama) : traductions FR et EN ajoutées.
- Les gloses courtes que ME place entre ( ) ou [ ] et que TE place en <small> sont marquées « glose (Rama) » dans la traduction : 90:8, 9, 10, 15, 21, 24 et 94:6. À confirmer.

### Simanim 128 — restauration (tour 2)

- FR séif 36 (bloquant, tour 2) : « celui qui a circoncis un enfant, et l enfant est mort, lève les mains ; et même si le peuple murmure contre lui qu il verse le sang, puisque la chose n est pas établie, il lève les mains. » (ME : מל תינוק ומת…)
- FR et EN séif 1 (tour 2) : glose du Rama étiquetée et complétée. FR « (Rama : un non-Cohen (זר) ne lève pas les mains, même avec d autres Cohanim — au chapitre 2 de Ketoubot, [daf] 24 : le זר transgresse un עשה ; Tossafot, chapitre כל כתבי : le ר״י ne savait pas quelle interdiction frappe le זר qui monte, et il se peut qu avec d autres Cohanim [ce soit permis] ; cela demande examen.) » ; EN, même contenu. « [ce soit permis] / [it is permitted] » est un supplément du traducteur, entre crochets : TE 363 porte « שרי », ME ne l'a pas.
- Étiquette « Rama » ajoutée en FR et EN (tour 2) aux séifim 5, 6, 16, 20, 34, 37 et 39. Attribution vérifiée sur trois sources : ME (<small>), TE 363 (petits caractères), traduction communautaire de Sefaria (<small>). Pour 34 et 37, ME met la glose entre parenthèses sans <small>, TE en petits caractères.
- Séif 41 (tour 2) : la glose « (י״א דמי שיש לו בת…) » est désormais étiquetée « Rama » en FR et EN. Même vérification qu'aux autres séifim.
- EN séif 30 (tour 2), nouvelle traduction du crochet restauré : « [בוהקניות : a kind of white skin-affliction (נגע), and Rashi explained it with the vernacular word לינטלי״ש ; עקומות : curved ; עקושות : bent to their sides ; and the Ran explained עקומות as one whose hand has become bent backward, and עקושות as one who cannot separate his fingers] ».
- EN séif 10 (tour 2) : « then, if they are two, he calls them « כהנים » ». EN séif 33 (tour 2) : « …ayin for alef, and the like — ».
- Séif 20 (tour 2) : raison ajoutée retirée en EN, « (lest he lose his place in the prayer) », et dans le div HE, « (שלא לטרוף דעתו מן התפילה) ».
- div.translation HE, séif 1 (tour 2) : la paraphrase « וזר (ישראל) שנשא את כפיו, אפילו עם כהנים אחרים — עובר בעשה » est remplacée par le texte de ME, « ואין לזר (ישראל) לישא כפיו אפילו עם כהנים אחרים (בפ׳ ב׳ דכתובות דכ״ד דזר עובר בעשה) (ותו׳ פ׳ כל כתבי … וצ״ע) ». Pas de « הגה » ajouté : ME n'en porte pas ici.
- div.translation HE, séif 5 (tour 2) : « [ויש מחמירין אם הם של עור] » quitte « במנעליו » pour suivre « בבתי שוקיים מותר ». La rigueur porte sur les בתי שוקים de cuir.
- Titres HE (tour 2) : le sommaire et le h3 de la section ד passent à « (סעיפים כ׳–כ״ב) » ; le sommaire de la section ה passe à « (סעיפים כ״ג–כ״ט) », comme son h3 déjà corrigé par le premier agent.
- Traductions FR ajoutées par le premier agent (état final, toutes à relire). Nouvelles aux séifim 2-4, 7-10, 13-14, 16-21, 23-26, 28-29, 31-34, 36-39 et 41-44 ; complétées aux séifim 1, 5, 6, 12, 15, 30, 35 et 45. Je les ai relues une à une contre ME, sans autre écart que ceux corrigés ici.
- Traductions EN complétées ou modifiées par le premier agent : séifim 1, 5, 6, 9, 10, 13, 15-18, 20, 22-26, 30-41, 43-45. Relues contre ME, sans autre écart que ceux corrigés ici.
- div.translation HE étendu par le premier agent dans toutes les sections : il recopie ME pour les séifim restaurés et garde ailleurs les paraphrases d'origine.

### Simanim 159, 160 — restauration (tour 2)

- Toutes les traductions FR et EN ajoutées (liste des restaurations ci-dessus) et, dans la page HE, le div.translation, où les passages restaurés sont le texte de ME ponctué, avec l'étiquette « הגה (רמ״א): » devant chaque glose.
- À NUANCER — 159:11, Rama (un enfant de moins de six ans est comme un singe, selon certains), et 159:12, Rama « ומ״מ יש להחמיר » : le Cas 3 dit « même un enfant » sans réserve.
- INCOMPLET — 159:6 : le key-point écrit « l'usage qui suit son avis » (celui de Rabbénou Tam). Il omet la suite du Rama : « הסברא הראשונה היא עיקר, לכן יש להחמיר לכתחלה ».
- INCOMPLET — 159:14, Rama « ויש להחמיר לכתחלה » (40 séa pour le mikvé) : le key-point des séifim 14-20 et le Cas 3 parlent de l'immersion « dans une source ou un mikvé » sans cette réserve.
- APPROXIMATIF — 160, key-point des séifim 9-12 : « pour les מי פירות et le vin, יש מי שאומר qu'ils conviennent à la rigueur ». La source donne trois choses : une première opinion, eau seulement ; pour le vin, « וי״א » valable mais interdit a priori, et selon le Rama vin blanc seulement ; pour les jus de fruits, « יש מי שאומר בשעת הדחק ».
- Retrait de « (fondue) » en FR et de « (melted) » en EN, dans la traduction du séif 160:10. Ce mot prêtait au Mehaber la condition du Rama « ונראה דוקא אם רסקן », désormais restaurée et traduite comme glose. C'est le seul texte existant que j'ai retiré : à valider.
- 160:13 « (והוא הדין) » : ME l'imprime entre parenthèses, TE 363 en petits caractères (Rama). Je l'ai traduit « (et de même) », sans étiquette Rama, à trancher.
- 160:12 : j'ai recopié avec le passage le renvoi du Rama « (עיין בי״ד סי׳ ר״א ס״ל) », parce qu'il est interne à la troncature. Je l'ai traduit « voir Yoré Déa, siman 201, séif 30 ».
- Choix d'édition, 159:11 : j'ai recopié ME « פחות מבן ו׳ » (six ans), alors que TE 363 lit « ז׳ » (sept).

### Simanim 153, 158 — restauration (tour 2)

- Toutes les traductions ajoutées ou réécrites, FR et EN, du siman 153 : séifs 2 (fin et deux « c est-à-dire »), 3, 4, 5 (avec la glose), 6 (« et de même les autres choses saintes »), 7 (entier, deux gloses), 8 (fin), 9 (début), 10 (fin), 11 (entier, avec la glose), 13 (passage intérieur), 14 (entier, remplace le résumé), 16 (glose, remplace la parenthèse), 18 (« certains disent que », fin), 19 et 20 (« certains disent que »), 21 (glose, remplace le résumé).
- Toutes les traductions ajoutées, FR et EN, du siman 158 : séifs 4 (crochet), 5 (glose et suite), 7 (entier, avec la glose), 10 (fin), 11 (suite et glose), 13 (fin).
- Les div.translation HÉBREUX des deux simanim : j'y ai ajouté le texte ME restauré lui-même, avec le marqueur « הגה (רמ״א): » pris du siman 156, et non une reformulation. Aux séifs 2 (153), 14 (153), 16 (153) et 21 (153), il remplace une parenthèse ou un résumé hébreu de la page.
- 153 séif 8 — DÉCISION À VALIDER : le séif 8 est remis à sa place dans l'ordre du Choul'han Aroukh (bloc « Séifim 7–9 »), avec sa traduction, au lieu du bloc 1. Les titres sont corrigés : « Séif 1 — Synagogue et beit hamidrash » / « סעיף א׳ — בית הכנסת ובית המדרש » / « Séif 1 — Synagogue and beit hamidrash » ; « Séifim 7–9 » / « סעיפים ז׳–ט׳ ». Fait parce que, restauré au bloc 1, le séif 8 sortait ABSENT dans les deux portes, et en vertu de la règle « ordre compris » du CLAUDE.md. C'est au-delà du mandat strict, qui excluait les DÉPLACÉS.
- 153 — trois résumés ou paraphrases hébreux de la page sont REMPLACÉS par le texte : le résumé du séif 7 (« בית הכנסת של כפרים — נמכר, ושל כרכים — אינו נמכר »), la paraphrase entière du séif 11 et le début reformulé du séif 10 (« יחיד בשלו — אפילו ספר תורה — יש מתירים »). Ont aussi été remplacés les mots que la porte disait mis à la place du passage manquant : séif 9 « ומכרו … הלוקח עושה », séif 13 « ואם », séif 18 « כלי », séif 22 « לחזור ».
- Leçons où ME, recopiée, diffère de Torat Emet 363 : 153:13 « וגדרום » (TE « וגררום », que j'ai traduit « taillées ») ; 153:16 Rama « כמו שירצה » (TE « במי שירצה ») ; 153:7 « כל מה שיעשו » (TE « שיעשה »), « בנו אותם » (TE « אותה ») et la source du Rachba « סי׳ תתר״ד » (TE « תרי״ז ») ; 153:21 « נ״ג ח״א » (TE « נכ״ג ») ; 153:5 « בשבילם » (TE « בשבילו ») ; 153:14 « מאי » (TE « מאן ») ; 153:4 « הותר » (TE « מותר ») ; 158:7 Rama « סימן צ״ב וקצ״ג » (TE « קצ״ב », probable coquille de ME).
- Attribution de passages entre crochets ou parenthèses que ME imprime sans « הגה » et que TE met en petits caractères, comme les gloses du Rama : 158:4 « [ואפילו … בלא ברכה] [ב״י] », 153:7 « (ואפי׳ בנו אותם משל אחרים) », 153:14 « (ושבעה טובי עיר דינם כחבר עיר) ». Je les ai traduits entre crochets ou parenthèses, sans les marquer « Rama ».
- Choix de traduction à vérifier : « הפנויות הקדשות » → « femmes non mariées qui se prostituent » ; « [ד״ע] » → « avis propre du Rama » (TE : « דברי עצמו ») ; « מחטים » → « littéralement : aiguilles » ; « דכל מאי דאתי אדעתא דידיה אתי » → « car tout ce qui vient [en don] vient en se fiant à son avis » ; « אפילו יחיד מה שעשה עשה » → « alors même un particulier — ce qu il a fait est fait » ; « במקומות המטונפים בגופו » → « les endroits malpropres de son corps » ; « לוח שמעמידין עליו ס״ת » → « le pupitre (לוח) ».
- Les encadrés de 153 signalés dans non_traites (résidu, synagogue de village ou de ville, don de terrain, « יש מי שאומר » présenté comme absolu) : à trancher par le Rav, je ne les ai pas réécrits.

### Simanim 3, 8, 53 — finitions

- 3:1 : la leçon de TE « יֹאמְרוּ » remplace « יֹאמַר » (consonnes de ME dans un séif par ailleurs TE). Traductions : FR « on dit » (au lieu de « il disait »), HE « יאמרו », EN « one says ».
- 3:5 : « הגה » est retiré du texte, parce que ni ME ni TE ne le portent ; la glose n'est plus marquée comme celle du Rama que dans les traductions. FR « mais entre est et ouest, c'est interdit » (au lieu de « à éviter », qui adoucissait אסור), EN « is forbidden ».
- 3:7 : nouvelle traduction FR, EN et HE. Le « (לא) » entre parenthèses de la source est rendu « ne s'assiéra (pas) ». « יסלק הקודש לצדדין » est rendu « il se placera de sorte que le lieu saint soit sur le côté ». Rachi est traduit « explication : le lieu d'où l'on peut voir le Mont du Temple… ».
- 3:8 : nouvelle traduction (« s'il est derrière une clôture, il se soulage aussitôt ; et en plaine… sa nudité »).
- 3:11 : nouvelle traduction complète. « תחתוניות » est rendu « hémorroïdes » ; « דבר שהאור שולט בו » est rendu « une chose sur laquelle le feu a prise » ; la parenthèse de la glose « (avec un tesson ; et de même l'usage est de s'essuyer) » est rendue telle quelle.
- 3:13 : traduction ajoutée pour la parenthèse « פירוש קרקע שאינה בתולה… » (« un sol qui n'est pas vierge, comme par exemple une terre labourée »).
- 3:14-16 : traduction littérale sobre en FR, EN et HE, à la place du résumé « au niveau du principe ». Termes : « le membre », « à partir de la couronne et en dessous », « de s'aider [en soutenant] les testicules », « se gratter ». À valider pour la forme comme pour le fond.
- 8:2 : « Il dispose son enveloppement » (TE « יְסַדֵּר »), au lieu de « L'ordre de l'enveloppement se fait » (« סֵדֶר », la leçon que lisait la page).
- 8:5 : « ensemble (explication : en une seule fois) » pour « כאחת (פירוש בפעם אחת) ».
- 8:6 : la source du Rama est développée en « Nimmoukei Yossef sur les Hilkhot Ketanot, folio 86b » (FR), « Nimukei Yosef on Hilkhot Ketanot » (EN), « נמוקי יוסף בהלכות קטנות דף פ״ו ע״ב » (HE), pour « נ״י בה״ק דף פ״ו ע״ב ». Ce développement est une lecture de l'abréviation, à confirmer. ME imprime « ט״ב », TE « ע״ב ».
- 8:13 : « Celui qui revêt un talit katan et bénit sur lui, puis, lorsqu'il va à la synagogue et s'enveloppe d'un talit gadol — doit bénir sur celui-ci » (les crochets de suppléance ont disparu).
- 8:14 : « même s'il avait l'intention de s'en envelopper de nouveau aussitôt ».
- 8 : nouvel ordre des sections, A (1-3), B (4-6), C kavana (7-10), D talit katan (11), E. L'encadré key-point du talit katan, qui commente les séifs 3, 6 et 11, est maintenant placé après le séif 11, et les séifs 3 et 6 sont donnés plus haut, en A et B. Sommaire réécrit en conséquence, trois langues.
- 53:3 Rama : « au départ » (תחלה), « à la synagogue » (בב״ה), « puis il dit ישתבח et le קדיש », et les sources [Kol Bo, siman 5] et [Maharil], en FR, EN et HE.
- 53:5 Rama : sources ajoutées. « ספ״ק דחולין » est rendu « fin du premier chapitre de Houlin » ; « תשובת א״ז במס׳ ברכו׳ » est rendu « Responsa du Or Zaroua, traité Berakhot ».
- 53:7 : « S il n y a là personne qui sache être חזן sinon un jeune de י״ג ans et un jour, mieux vaut qu il soit חזן plutôt qu ils soient privés d entendre la קדושה et le קדיש » (EN et HE alignés).
- 53:8 : « Celui qui n a pas de barbe : dès lors qu on voit en lui qu il est arrivé à l âge où sa barbe devrait être pleine, on lui applique « נתמלא זקנו » » (la traduction omettait « מי שאינו בעל זקן »). Rama : « s il a de la barbe, même un peu ».
- 53:13 : traduction du crochet : « [« mon serviteur Isaïe, nu » (עבדי ישעיה ערום) : le Targoum traduit « mon serviteur Isaïe, פחח »] — c est-à-dire celui dont… ».
- 53:16 : « celui qui n est pas שליח ציבור fixe doit refuser un peu (סירוב) avant de descendre devant l arche ».
- 53 : le siman suit ME partout, abréviations comprises (2, 4 et 12 sont passés de la forme développée de TE aux abréviations de ME), pour que le bloc non vocalisé ne mêle pas deux éditions. Les leçons divergentes signalées par l'arbitre du tour 2 restent celles de ME : 19 « סי׳ ק״ד » et « שורש מ״ד » ; 23 « סי׳ מ״ד » ; 25 « סי׳ ט׳ » et « בשירי הנכרים ».

### Simanim 55, 66, 79 — finitions

- 55:3, glose du Rama : « etc. » (FR, EN) et « וכו׳ » (div HE) ajoutés après תתקבל צלותהון.
- 55:8 : « comme un חרש שוטה וקטן » devient « comme un שוטה et un קטן » / « like a שוטה and a קטן ». La source dit « הרי הוא כשוטה וקטן ».
- 55:11-12 : la traduction commune est coupée en « Séif 11 : … » et « Séif 12 : … ». Pour le מנודה, le texte omis est ajouté : « on ne l adjoint à rien de ce qui requiert dix » / « is not adjoined for anything that requires ten » / « אין מצרפין אותו לכל דבר שצריך עשרה ». Le « mais » qui liait les deux séifs est retiré.
- 55:14, traduction entièrement refaite (FR, EN, div HE). FR : « celui qui se tient derrière la synagogue, une fenêtre entre eux — même haute de plusieurs étages, même si elle n a pas quatre [טפחים] de large — et qui leur montre son visage de là, se joint à eux pour les dix. Rama : les toits et les étages ne sont pas compris dans la « maison », et celui qui s y tient ne se joint pas. » « [טפחים] » est une addition entre crochets.
- 55:20, traduction refaite : « si dix étaient en un même lieu et disaient קדיש et קדושה … et certains disent qu il faut qu aucune saleté (טינוף) ni עכו״ם (idolâtrie ou idolâtre) ne fasse écran » (EN pareil). Les deux éditions portent עכו״ם, que la page avait développé en « עבודה זרה ». La Michna Beroura 55 ס״ק סה glose « ר״ל עבודת כוכבים או עובד כוכבים » ; la traduction garde donc les deux lectures, là où l'ancienne disait « idole » seulement. À trancher.
- 55:4 : la source de la glose du Rama diffère selon l'édition : « פ״ט מהלכות תפלה » dans ME, « פרק ח׳ » dans TE. J'ai retenu ME, l'édition par défaut, et le séif est unifié sur ME (הפוסקי׳, וה״ה).
- 55:6, 55:20, 66:1 : séifs unifiés sur ME (עמה׳, אפ״ה ; אפי׳, וי״א ; וכ״ש, ואפי׳, ובשכמל״ו). L'hébreu montre désormais les sigles du livre. Le sens et les traductions ne changent pas.
- 66:6, titre FR : « inutile de redire « אמת » » au lieu de « ne pas redire ». La source dit « אינו צריך לחזור ».
- 66:7, glose du Rama : traductions « comme [il est dit] plus loin, au siman 215 » / « as [stated] below in siman 215 » ; div HE « …אחר הש״ץ אמן … כדלקמן סימן רט״ו ». La traduction FR dit toujours « après le חזן » pour « אחר הש״ץ ».
- 66:9 : « — on attend plutôt » (qui rendait le « אלא » de la page) devient « Comment fait-on ? On attend à « שירה חדשה » pour répondre ». EN : « How does one do it? One waits… ». Div HE : « אין לענות … וכיצד עושין? ממתין… ».
- 66, sommaire « Plan de l'étude » : « אם פסק אחר שאמר אמת (séif 6 / סעיף ו׳) » ajouté dans les trois langues. Ancres renommées seif-4-5, seif-6, seif-7-9, seif-10 ; elles disaient seif-5 au-dessus des séifim 7-9 et seif-6 au-dessus du séif 10.
- 66, marqueurs ajoutés dans le bloc source : [ה], [ח] et [ט]. Les traductions portaient déjà « Séif 5/8/9 ».
- 79:1 : « או שהוא סומא » est entre crochets dans ME (dans un <small>) et en petits caractères dans TE : c'est une glose insérée dans le texte du Mehaber, sans « הגה ». Le bloc et les traductions la mettent maintenant entre crochets : « [ou s il est aveugle (סומא)] », « [or if he is blind (סומא)] », « [או שהוא סומא] ». Faut-il l'attribuer explicitement au Rama ?
- 79:1, fin de la glose du Rama : « Et voir plus loin, à la fin du siman 90 [et voir plus loin, au siman 87, la règle de la צואה dans une maison]. » EN : « And see below, at the end of siman 90 [and see below, siman 87, on the law of excrement in a house]. » Div HE : « ועיין לקמן ס״ס צ׳ [ועיין לקמן סי׳ פ״ז בדין צואה בבית] ».
- Toujours ouvert depuis le tour 2 : 55:3, « לאחר שהתחיל בקול רם וקדושה » est rendu littéralement (« après qu il a commencé à voix haute, et la קדושה ») ; 66:10, lecture de « ואין לו פנאי להתפלל מיד אחר קריאת שמע ».

### Simanim 90, 94, 113 — finitions

- 90:1, glose du Rama « ואפי׳ אינן גבוהין ג׳ [ב״י בשם מהרי״א] » (ME et TE en <small>), désormais marquée comme glose. FR : « [glose (Rama) : et même s ils n ont pas trois טפחים de haut — Beit Yossef au nom du מהרי״א] ». EN : « [gloss (Rama): and even if they are not three טפחים tall — Beit Yosef in the name of the מהרי״א] ». Div HE : « [הגה: ואפילו אינם גבוהים ג׳ טפחים (בית יוסף בשם מהרי״א)] ». L'unité « טפחים » n'est pas dans le texte (ג׳ seul) : elle vient de 90:2. Fichiers : /home/user/Daat.ai/sources/orah-haim/siman-90/niveau-1-base{,-en,-he}.html.
- 90:11, traductions sans le « et » qui rendait un vav absent du texte : FR « Séif 11 : celui qui a une synagogue », EN « Séif 11: one who has a synagogue », HE « סעיף י״א: מי שיש לו ».
- 94:1, traduction complétée en FR, EN et HE. FR : « Celui qui se tient en ארץ ישראל tourne son visage vers ירושלים et dirige aussi son cœur vers le מקדש et le בית קדשי הקדשים. Celui qui se tient à ירושלים tourne son visage vers le מקדש et dirige aussi son cœur vers le בית קדשי הקדשים. » EN : « … and directs his heart also toward … ». HE : « … ומכוין גם למקדש ולבית קדשי הקדשים … ומכוין גם לבית קדשי הקדשים ». Fichiers : /home/user/Daat.ai/sources/orah-haim/siman-94/niveau-1-base{,-en,-he}.html.
- 113:3, glose « (פי׳ שאין לכרוע אלא במקום שתקנו חכמים) » : FR « (c est-à-dire : on ne doit s incliner qu à l endroit institué par les Sages) », qui remplace « — car on ne doit … » ; EN « (that is: one may bow only in the place instituted by the Sages) » ; HE « (פירוש: שאין לכרוע אלא במקום שתקנו חכמים) ». Attribution non tranchée, Rama ou glose d'imprimeur. Fichiers : /home/user/Daat.ai/sources/orah-haim/siman-113/niveau-1-base{,-en,-he}.html.
- 113:5, glose « (פי׳ שהשפיל) » : FR « dès lors qu il a incliné (הרכין) (c est-à-dire : abaissé) sa tête », EN « once he has inclined (הרכין) (that is: lowered) his head », HE « כיון שהרכין (פירוש: שהשפיל) ראשו ». Même question d'attribution.

### Simanim 128 — finitions

- FR séif 30 (traduction réécrite) : « celui qui a un défaut au visage ou aux mains — par exemple si elles sont בוהקניות, עקומות ou עקושות [בוהקניות signifie : une sorte de plaie blanche (נגע), et Rachi l a expliqué par le mot vernaculaire לינטלי״ש ; עקומות : recourbées ; עקושות : tordues sur leurs côtés ; et le Ran a expliqué עקומות : celui dont la main s est recourbée vers l arrière, et עקושות : celui qui ne peut écarter ses doigts] — ne lève pas les mains, parce que le peuple le regarde ; il en va de même de celui qui a des défauts aux pieds, là où l on monte à la doukhan sans chaussettes (בתי שוקיים) ; de même celui dont la salive coule sur sa barbe, ou dont les yeux coulent de larmes ; et de même l aveugle d un œil ne lève pas les mains. Mais s il est דש בעירו — c est-à-dire qu on est habitué à lui et que tous savent qu il a ce défaut —, il lève les mains, même s il est aveugle des deux yeux ; et quiconque a séjourné trente jours dans la ville est appelé דש בעירו. » (la suite est inchangée)
- FR séif 40 : « …il reste פסול jusqu à ce qu il fasse vœu, על דעת רבים (selon l intention de la multitude), de ne tirer aucun profit (הנאה) des femmes qui lui sont interdites. » (ME : שידור הנאה על דעת רבים מהנשים שהוא אסור בהם)
- EN séif 3 : « if he went up once in the day, he no longer transgresses, even if he was told « go up ». » (« but » retiré)
- EN séif 12 : « …aiming to make five spaces (ה׳ אוירים) — between two fingers and two fingers one space, and between finger and thumb, and between thumb and thumb — and they spread out their palms so that the inside of their palms faces the ground and the backs of their hands face the sky. »
- EN séif 13 : « then the שליח צבור prompts them word by word, and they answer after him on each word until they finish the first verse, and then the congregation answers « אמן » ; and likewise after the second verse, and likewise after the third. » (avant : « the מקריא feeds them each verse » — le texte dit « מקרא אותם ש״ץ »)
- EN séif 21 : « the kohanim may not sing the blessing in two or three melodies, for there is reason to fear confusion (טירוף הדעת) ; one sings only one melody, from start to end. » (ordre de la source rétabli)
- EN séif 30 : ajout de « the same applies to one who has blemishes on his feet, in a place where they go up to the dukhan without socks (בתי שוקיים) ; likewise one whose spittle runs down onto his beard, or whose eyes drip tears ; and likewise one who is blind in one eye does not raise his hands. »
- div.translation HE séifim 23-24 : la paraphrase est remplacée par le texte de ME, « סעיף כ״ג: … ולא יסתכלו בהם. הגה: וגם הכהנים לא יסתכלו בידיהם … (ב״י). סעיף כ״ד: עם שאחורי הכהנים… הם בכלל הברכה. ». La glose du Rama est désormais marquée « הגה » et placée après la fin du Mehaber.
- div.translation HE séif 30 : le début est remplacé par le texte de ME (crochet בוהקניות ajouté). La raison ajoutée « ומתבטלת כוונתם » est retirée.
- Encadrés FR, attribution corrigée : l.595 « Le Rama note que les Lévites ont pris l usage de ne pas se relaver d abord » et l.765 « Le Rama clôt le siman par un principe de dignité sacerdotale : אסור להשתמש בכהן ». Dans ME comme dans TE 363, ces deux passages sont dans la glose (<small>).
- Encadré HE déplacé tel quel : la תמצית des séifim 27-29 (« וכן — אין להוסיף על שלושת הפסוקים… (סעיף כ״ט) ») passe de la key-point de la section ד (20-22) à la fin de la key-point de la section ה (23-29). Elle y suit « ובשעת הברכה אין לומר פסוקים… (סעיף כ״ו) ».

### Simanim 153, 158 — finitions

- 158:1, FR/EN : traduction des deux parenthèses restaurées. « (פירוש סטורט״י בלע״ז) » → « explication : סטורט״י en langue vernaculaire » (le mot étranger est laissé en lettres hébraïques). « (פי׳ פת עשוי׳ עם צוקארו ושקדים ואגוזים) » → « explication : un pain fait avec du sucre [צוקארו], des amandes et des noix ». Dans ME, la première glose est posée entre « לחמניות » et « דקות » ; la traduction la met après « לחמניות דקות ».
- 158:5, FR/EN/HE : j'ai retiré « — la netila n est requise que pour le pain » (EN « for the netila is only for bread », HE « שאין הנטילה אלא לפת »), raison que le texte ne donne pas. J'ai ajouté le marqueur « Suite du Mehaber : » (EN « The Mehaber continues: », HE « המשך דברי המחבר: ») devant « ובשר צלי », qui est du Mehaber, même séif, après la glose du Rama.
- 158:6 : « [וע״ל סי׳ ק״ע] » est traduit sans direction, « [et voir siman ק״ע] » / « [and see siman ק״ע] ». ע״ל se lit d'ordinaire « voir plus haut », mais le siman 170 vient APRÈS le 158 : à trancher.
- 158:10 : le crochet restauré est traduit « [explication : le quart d un log, c est-à-dire la mesure d un œuf et demi] » ; l'ancienne glose « (un quart de log) » est supprimée.
- 158:11 : j'ai remplacé « à la rigueur on bénit avant la netila » (qui en français veut dire « au besoin ») par « on bénit avant la netila ». J'ai retiré pour la parité « by the letter of the law » (EN) et « מן הדין » (div HE). Les key-points, qui disent « en principe », sont inchangés.
- 158, div.translation HE des séifs 1, 4, 6, 9 et 10 : le texte ME restauré y est recopié, comme dans le bloc source.
- 153:2, FR/EN : traduction du séif entier rétabli (« s ils ont vendu la תיבה, ils peuvent acquérir avec son produit un מטפחת (housse) du ספר תורה ; s ils ont vendu le מטפחת, ils achètent avec son produit des ספרים … ; s ils ont vendu des ספרים, ils achètent avec leur produit un ספר תורה »).
- 153:6 : « avec le produit » ajouté pour rendre « בדמיו » (FR) ; « and » retiré en EN.
- 153:7 : marqueur « Suite du Mehaber : » / « The Mehaber continues: » / « המשך דברי המחבר: » devant « אבל של כרכים », qui est du Mehaber après la glose du Rama « (מרדכי) ».
- 153:9 : « quatre usages avilissants » remplacé par « sauf [pour en faire] un bain, une tannerie, un bain rituel ou des latrines » ; la fin devient « l acheteur pourra faire même ces quatre choses ». La phrase EN, cassée, est corrigée.
- 153:10 : « certains disent qu un particulier … a le droit de le vendre et de faire de son produit tout ce qu il veut » (EN « some say that … do with its proceeds whatever he wishes »).
- 153:13 : « qu une chose de mitsva se présente à eux … on ne les vendra pas pour une chose de mitsva, mais seulement pour פדיון שבויים … ils ne vendront pas la synagogue, mais collecteront … ». ME « לא ימכרם » est au singulier, TE « לֹא יִמְכְּרוּם » au pluriel : j'ai traduit par un impersonnel. « וגדרום » (TE « וּגְרָרוּם ») reste traduit « taillées », un choix du tour 2 jamais tranché.
- 153:16 : « ne peut la [lui] interdire, à moins de l interdire à toute la communauté ensemble » (EN « [to him] ») remplace « à lui seul », qui n'est pas dans le texte.
- 153:18 : « toujours » / « always » ajouté (« שנהגו להביאם תמיד »). « יש מי שאומר » reste rendu « certains disent » aux séifs 18-20, tandis qu'au séif 10 « יש מי שאוסר » est « il en est un qui l interdit ». À harmoniser ?
- 153:21 : « il ne faut pas acheter » / « one should not buy » pour « אין לקנות ».
- 153:22, FR/EN : traduction refaite sur le texte rétabli (« le premier avait les moyens de donner ce qu il donnait chaque année … quand on l a donnée au second, le premier n avait pas les moyens … il veut acquérir sa mitsva et redonner ce qu il donnait auparavant »).
- 153, div.translation HE des séifs 2, 6, 8, 9, 10, 13, 15, 16, 18, 21 et 22 : les paraphrases hébraïques (« יש מתירים », « חוץ מארבעה דברים של ביזיון », « אינו יכול לאוסרו עליו לבדו », etc.) sont remplacées par le texte ME lui-même.
- 153, key-point du séif 8 : la phrase « Et la sainteté d un lieu ne prend qu à l usage… » est détachée du key-point du séif 1 et posée, sans changement, sous le bloc « Séifim 7–9 », FR/HE/EN. Elle commence par « Et » parce qu'elle est recopiée telle quelle.
- Leçons de ME désormais recopiées en 153, là où TE 363 diffère (sans changement de sens, à mon avis) : 8 « והקדישו אח״כ » (TE « וְהִקְדִּישׁוּהוּ אַחַר כָּךְ ») ; 9 « שבעה טובי העיר » (TE « ז׳ ») ; 13 « לא ימכרם » (TE « לֹא יִמְכְּרוּם »), « וגדרום » (TE « וּגְרָרוּם ») ; 18 « להביאם תמיד … להוציא » (TE « לְהָבִיא תָּמִיד … לְהוֹצִיאָם ») ; 22 « סיפק » deux fois (TE « סִפּוּק » puis « סִפֵּק »). Celles du tour 2 restent valables : 7 « כל מה שיעשו », « בנו אותם », « סי׳ תתר״ד » (TE « תרי״ז ») ; 16 Rama « כמו שירצה » (TE « במי שירצה ») ; 21 « נ״ג ח״א » ; 158:7 « סימן צ״ב וקצ״ג » (TE « קצ״ב »).
- Attribution toujours ouverte (tour 2) : des passages que ME imprime en petits caractères sans « הגה » sont traduits entre parenthèses ou crochets, sans être marqués Rama. Ce sont 153:7 « (ואפי׳ בנו אותם משל אחרים) », 153:14 « (ושבעה טובי עיר דינם כחבר עיר) » et 158:4 « [ואפילו … בלא ברכה] [ב״י] ».

### Simanim 159, 160 — finitions

- 159:1, traduction ajoutée de la glose « [פירוש כלים עשוים מרפת בקר ועפר] ». FR : « (כלי גללים — explication : des récipients faits de [ce qui vient de] l étable des bovins et de terre) ». EN : « (כלי גללים — that is, vessels made from [the matter of] a cattle stall and earth) ». ME lit « מרפת » (étable) là où TE 363 lit « מרפש » (fange). La traduction suit ME à la lettre, avec les mots suppléés entre crochets.
- 159:12, traduction ajoutée de « [פי׳ מין חיה סימי״א בלע״ז] ». FR : « si un singe (קוף — explication : une espèce de bête sauvage, סימי״א en langue vernaculaire) ». EN : « if a monkey (קוף — that is, a species of wild animal, סימי״א in the vernacular) ».
- 159:9, traduction FR changée : « un tonneau (חבית) rempli d eau » devient « un tonneau (חבית) qui contient de l eau », pour « חבית שיש בה מים ».
- 160:4, traduction ajoutée de « (פי׳ שתיית הכלב נקרא לקיקה) ». FR : « (שלקק — explication : quand le chien boit, cela s appelle לקיקה) ». EN : « (שלקק — that is, a dog's drinking is called לקיקה) ».
- 160:6, traduction ajoutée de « [פי׳ כל שכריסו של תינוק נכוה הימנו] ». FR : « (שהיד סולדת — explication : toute [chaleur] dont le ventre d un nourrisson est brûlé) ». EN : « (שהיד סולדת — that is, any [heat] by which a baby's belly is scalded) ».
- 160:10, traduction ajoutée de « (פי׳ תולעים) ». FR : « comme les vermisseaux (יבחושים — explication : des vers) rouges ». EN : « such as red midges (יבחושים — that is, worms) ».
- 160:11, traduction FR/EN réécrite en entier à la place de la condensation. FR : « de l eau dont on doute si l on y a fait un travail ou non, ou dont on doute si elle contient la mesure ou non, ou si elle est impure ou pure, ou si l on doute de s être lavé les mains ou non — on est pur. Glose (Rama) : [et tout doute de pureté portant sur les mains est pur] [Tour]. Et il en est un qui dit que, malgré tout cela, si l on a d autres eaux, on se lave les mains et l on se dégage du doute. » EN : réécriture parallèle. Le div HE porte désormais le texte complet de ME ponctué.
- 160:12, traduction ajoutée de « (פי׳ המים הנקפי׳ מרוב הקור) ». FR : « la glace (הגליד — explication : l eau qui se fige sous l effet d un grand froid) ». EN : « ice (הגליד — that is, water that congeals from the intensity of the cold) ».
- Div.translation HE (159:1, 159:12, 160:4, 6, 10, 12) : les gloses ajoutées sont le texte de ME tel quel, sans étiquette « הגה (רמ״א) », comme les autres פירוש de la page. ME les imprime en <small> et TE 363 en double <small>, c'est-à-dire comme des notes et non comme le Rama.
- En attente depuis le tour 2, non touchés par moi : (a) retrait de « (fondue) » / « (melted) » dans la traduction de 160:10 ; (b) 160:13 « (והוא הדין) », que ME imprime entre parenthèses sans <small> et TE 363 en petits caractères simples, comme le Rama ; il est traduit « (et de même) » sans étiquette Rama ; (c) le renvoi du 160:12 « (עיין בי״ד סי׳ ר״א ס״ל) », traduit « voir Yoré Déa, siman 201, séif 30 » ; (d) au 159:11, la page suit ME « פחות מבן ו׳ » (six ans), alors que TE 363 lit « ז׳ » (sept).

### Contradictions déjà signalées au tour 2 (reprises au § 1 quand elles subsistent)

- [c-159-160] CONTRADICTION — 159:20, Rama « ויש אומרים דמברכין על טבילת ידים וכן עיקר » : la page dit le contraire, sans réserve, dans l'encadré key-point des séifim 14-20 (« il récite tout de même la bénédiction al netilat yadaïm »), le remember « Le siman en une phrase » et le Cas 3 (« en bénissant al netilat yadaïm »), dans les trois langues. Le niveau 3 (niveau-3-synthese*) dit la même chose. Rien n'a été réécrit.
- [c-159-160] CONTRADICTION — 159:13, Rama « וכוונת נותן נמי מועיל אפי׳ לכתחלה » : le key-point des séifim 11-13 (« c'est celui qui se lave qui doit, a priori, avoir l'intention ») et le Cas 3 (« pourvu que celui qui se lave ait l'intention voulue ») ne mentionnent pas que l'intention de celui qui verse suffit.

## 3. Lectures à trancher

- 66:10, glose du Rama : « ואין לו פנאי להתפלל מיד אחר קריאת שמע » est lu « n'a pas le loisir de prier aussitôt après la ק״ש » ; Torat Emet 363 ponctue autrement (« להתפלל, מיד אחר… »).
- 79:1 : « [או שהוא סומא] » — Maginei Eretz l'imprime entre crochets ; la traduction le met entre crochets sans l'attribuer au Rama. Faut-il écrire « Rama : ou s'il est aveugle » ?
- 3:7 : « או יסלק הקודש לצדדין » est rendu « ou bien qu'il écarte le lieu saint sur le côté », calque littéral ; le sens est de se placer de sorte que le lieu saint soit sur le côté.
- 3:13-16 : la note d'introduction annonce un exposé « de principe, avec la pudeur qui convient » ; le texte et la traduction des séifs 14-16 sont désormais donnés en entier. Garder la traduction littérale, ou un autre registre ?
- 8:17 : l'encadré remember cite « בִּטֵּל מִצְוַת צִיצִית » (leçon de Maginei Eretz) alors que le bloc suit Torat Emet 363, « בִּטֵּל מִצְוַת עֲשֵׂה ».
