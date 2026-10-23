# Matrice arbitrée du tertre — SA 375:2 (Choul'han Aroukh HaRav 375:2)

Arbitrée le 22 octobre 2026, à partir de deux matrices établies chacune de leur côté (A et B), puis révisée le même jour après quatorze objections, chacune arbitrée contre la source (section finale). Cette matrice est la référence : l'arbre, le tableau, le N1, le N2, le N3 et le N4 s'alignent sur elle, et une page ne s'en écarte que sur une preuve nouvelle tirée de la source.

**Le cas.** Un tertre (תל) ou une colonne (עמוד) est commun à la cour et à la galerie (מרפסת), et leurs habitants n'ont pas fait l'érouv ensemble. Il y a trois variables :
- **H** : la hauteur au-dessus de la cour, moins de dix téfahim ou dix et plus ;
- **G** : de combien le tertre est plus bas que la galerie, moins de dix (« תוך עשרה למרפסת ») ou dix et plus ;
- **E** : l'écart de devant la galerie, moins de quatre téfahim (סמוך) ou quatre et plus (מופלג).

**Sources ouvertes.** Toutes ont été ouvertes par `scripts/sefaria-extrait.py`, et aucune page du site n'a été modifiée :
- SA 375:2 et 375:4 (Maginei Eretz) ;
- Taz 375 ס״ק ב, en entier ;
- MB 375 ס״ק ה à י״א, et ס״ק יד, טו ;
- SAH 375:2 et 375:3 ;
- Tour 375, Beit Yossef 375 (avec la guemara Érouvin 84a et Rachi qu'il recopie) et Magen Avraham 375, en entier ;
- Rambam, Érouvin 4:16, 4:17 et 4:18 (ajoutés à la révision).

Chaque citation a été vérifiée segment par segment avec `extrait`, code 0 sur tous les segments, y compris les citations données dans les colonnes « Réf. » et dans « Ce que la source laisse ouvert ». Le script est `oh366/memoire-e3/matrice375/arbitre.py --verifier` (sortie : `VERIF OK`). La version d'avant les objections est dans `oh366/memoire-e3/bak-matrice-obj/`.

**Conventions d'écriture.**
- « … » sépare deux segments d'une même source, dans l'ordre de la source.
- « ‖ » sépare deux sources. Pour la voix « Rambam selon le Taz », on cite d'abord les mots du séif hors parenthèses, puis le Taz.
- Les balises `<small>` sont recopiées telles que les imprime Maginei Eretz.

**Critère des modes, fixé par l'arbitrage et précisé à la révision.**
- **Explicite** : la voix écrit l'issue dans une clause dont ce cas relève *sous toute lecture* de ce qu'elle ne précise pas, ou elle écarte expressément la variable manquante (« אפילו », « בין … בין », « בכל ענין », « ולהרמב״ם אינו כן »). Une clause disjonctive dont le cas remplit les deux branches est explicite.
- **Règle générale** : le cas ne relève de la clause que par une lecture d'une variable que la voix tait, ou par sa règle « בנחת / בקשה ». Une autre lecture écrite peut la limiter : la colonne « Réf. » le dit. Pour la voix « SA 375:ד », la règle est écrite pour la saillie, non pour le tertre : elle n'est jamais explicite pour le tertre.
- **Non écrit** : la voix ne porte pas d'issue pour ce cas. C'est aussi le cas quand ses propres règles donnent pour ce cas des issues contraires, ou quand les seules voix qui lisent sa clause n'y mettent pas ce cas : l'issue serait alors notre choix.

## Arbitrage des six cellules où A et B divergeaient

(Arbitrage d'origine, conservé. Les cellules qu'il fixe et que la révision a changées sont signalées dans « Objections arbitrées ».)
## Arbitrage des six cellules où A et B divergeaient

1. **Cas 1, séif imprimé : explicite** (A ; B disait règle générale). La première phrase ne nomme que la hauteur. Le cas « tout bas, tout proche » en relève pourtant sous les deux lectures écrites :
   - BY et Taz pour le Rambam : « מדלא זכר ברישא מחילוק מופלג או סמוך », la phrase vaut sans distinction ;
   - MB ס״ק ו-ז : la phrase est limitée à ce cas ; Magen Avraham « וגם למרפסת אין גבוהים י' » : limitée au tertre à moins de dix sous la galerie, ce qui comprend ce cas (sur l'écart, il rapporte deux avis : cas 2).

   Les cas 2 à 4 n'en relèvent que par la première lecture : ils restent en règle générale.
2. **Cas 4, Rambam selon le Taz : explicite** (B ; A disait règle générale). Le Taz écarte chaque variable expressément dans la רישא :
   - l'écart : « אסור לשניהם אפילו במופלג ד' ממרפסת » ;
   - la hauteur sous la galerie : « אבל בנמוך י' ממרפסת בני החצר מותרים כדעת הטור ולהרמב״ם אינו כן ».

   Le cas 3 est traité de même.
3. **Cas 4, Magen Avraham : à la cour, règle générale** (A ; B disait deux avis rapportés). Le Magen Avraham rapporte le BY (« אף ע״פ שרחוק ד' … שניהם אסורים ») sous sa propre glose « וגם למרפסת אין גבוהים י' ». Ce rapport ne porte donc que sur l'écart, dans le cadre du tertre à moins de dix sous la galerie. Pour le tertre plus bas de dix, le Magen Avraham n'écrit que « בטור ובפוסקים … או נמוך ממנו י' ». Le cas 3 a la même issue chez A et chez B, et c'est la même lecture.
4. **Cas 6, Rambam selon le Taz : explicite** (A ; B disait règle générale). Les mots du séif hors parenthèses écrivent ce cas : « ואם היו רחוקים … אע״פ שגבוהים עשרה … שניהם אסורים ». Il en relève, que le Rambam suppose le tertre au niveau de la galerie (doute 42) ou qu'il ne tienne pas compte de G (Taz). En revanche, les cas 7 et 8 (G ≥ 10) ne relèvent de la règle que par la lecture du silence (« ולא זכר הרמב״ם כלל ») : ils restent en règle générale, ce sur quoi A et B s'accordaient.
5. **Cas 6, Tour : explicite** (A ; B disait règle générale). La clause « או שהוא גבוה י' לבני החצר ורחוק ד' מן המרפסת … שניהם אסורין » ne nomme pas G. Ce cas en relève pourtant sous toute lecture : le séif prête au Tour « (מן החצר לתוך עשרה למרפסת) », et le Taz lit ainsi le Tour (« ולגביה אין ריעותא מכח שלשול כיון שהוא תוך י' שלו »). Le cas 8 reste en règle générale.
6. **Cas 7, Taz (shita du Tour) : explicite** (A ; B disait règle générale). Chez le Taz, l'écart est une ריעותא distincte, traitée à part sous « תרתי לריעות' … למעלה מי' ומופלג ». « לא' בזריקה ולא' בשלשול » désigne donc exactement ce cas, et le Taz écrit « שלשול וזריקה שוין הם ואסור והכי קי״ל … ונ״ל דכיון דכבר כ' הטור דין שלשול וזריקה דאסור ».

**Les autres cellules.** A et B s'accordaient sur l'issue et sur le mode de toutes les autres cellules. Les citations retenues sont celles des deux matrices, parfois complétées, et toutes ont été revérifiées. Aucune issue n'a changé par l'arbitrage, sauf celle du Magen Avraham au cas 4, où A et B divergeaient.

## Vue d'ensemble

Légende des cellules :
- **I** : interdit aux deux ;
- **G** : à la galerie ;
- **C** : à la cour ;
- **2** : deux avis rapportés ;
- **·** : non écrit ;
- **h** : hors du cadre de la voix (colonne « guemara selon Rachi, cadre בני עלייה », cas 1, 2, 5 et 6 : la cellule du cas donne ce qu'écrit la guemara dans la lecture où elle conclut) ;
- **(r)** : règle générale. L'issue tient à une lecture de ce que la voix tait ; une autre lecture écrite peut la limiter, et la colonne « Réf. » du cas le dit. Une issue (r) n'est donc jamais à donner comme « ce qu'écrit » la voix.

Une cellule sans (r) est explicite.

Deux voix ont été ajoutées à la révision :
- **Guemara selon Rachi (cadre בני עלייה)** : la guemara d'Érouvin 84a et le Rachi que le BY recopie, là où Rachi explique le tertre sous les chambres hautes. Elle ne porte que les cas 7 et 8. Les cas 1, 2, 5 et 6 sont hors de ce cadre ; dans la lecture où la guemara conclut (Rav Houna, les gens qui habitent la galerie), elle écrit le cas 1 (interdit aux deux), le cas 5 (à la galerie) et le cas 6 (interdit aux deux), et le cas 2 s'y lit de deux façons : interdit aux deux selon le sens simple que le BY lit dans la michna (« אבל במופלגת בין גבוה י' טפחים בין פחות מי' לחצר כלומר אף לחצר כדמוקי בגמרא »), à la cour selon la lecture « לצדדין » que le BY prête au Tour (« צריך לדחוק ») [ajouté à la vérification stricte du nœud, passe 4 ; cas 2 corrigé à la passe 5, où la matrice disait que la phrase « ne distingue pas l'écart »].
- **SA 375:ד, saillies (analogue)** : le séif ד du même siman (= Rambam, Érouvin 4:17), qui écrit la saillie (זיז) collée au mur entre la cour et la chambre haute. C'est une règle pour un autre objet, que le BY dit « נלמד » de celle du tertre. Elle ne donne jamais qu'une issue en (r).

| Cas | Séif imprimé | Rambam selon le Taz | Taz, shita du Tour | Tour | Beit Yossef | Michna Beroura | SA HaRav | Magen Avraham | Guemara selon Rachi (cadre בני עלייה) | SA 375:ד, saillies (analogue) |
|---|---|---|---|---|---|---|---|---|---|---|
| `H<10 G<10 E<4` | I | I | I (r) | I | I | I | I | I | h | · |
| `H<10 G<10 E>=4` | I (r) | I | C (r) | C | I | C | C | 2 | h | · |
| `H<10 G>=10 E<4` | I (r) | I | C | C (r) | · | C | C | C | · | C (r) |
| `H<10 G>=10 E>=4` | I (r) | I | C | C | I (r) | C | C | C | · | · |
| `H>=10 G<10 E<4` | G | G | G (r) | G | G | G | G | G (r) | h | G (r) |
| `H>=10 G<10 E>=4` | I | I | I | I | I | I | I | · | h | · |
| `H>=10 G>=10 E<4` | · | · | I | I | I | I | I | I | 2 | I (r) |
| `H>=10 G>=10 E>=4` | · | I (r) | C | · | I | 2 | C | · | I | · |

## La matrice, cas par cas

### Cas 1 — `H<10 G<10 E<4`

Tertre ou colonne commun : moins de dix au-dessus de la cour ; à moins de dix sous la galerie (תוך עשרה למרפסת) ; à moins de quatre téfahim de devant la galerie (סמוך).

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **interdit aux deux** | explicite | אם אינם גבוהים י״ט הרי אלו נחשבי' בין החצר ובין המרפסת ושניהם אסורים להוציא שם כלים שבבתים | SA OH 375:2 (Maginei Eretz) — la clause ne nomme que la hauteur ; ce cas est dans sa portée sous toutes les lectures (BY et Taz : sans distinction ; MB et MA : limitée à ce cas) |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **interdit aux deux** | explicite | כל שיש מעלה לתרווייהו דהיינו לחצר תוך י' ולמרפסת בסמוך פחות מד' טפחים פשיטא שאוסרין זה על זה | ט״ז שע״ה ס״ק ב |
| Taz (shita du Tour) | **interdit aux deux** | règle générale | אבל אם שניהם שוים הן בנחת כגון ששניהם משתמשים ע״י פתח הן בקשה שייך לשניהם ואוסרין זה על זה … גם נמוכים ממרפסת פחות מי' דאז דוקא שוה לשניהם | ט״ז שע״ה ס״ק ב |
| Tour | **interdit aux deux** | explicite | ואם הוא לשניהן שוה תוך י' או יותר מי' והוא בתוך ד' למרפסת … שניהם אסורין | Tour OH 375 |
| Beit Yossef | **interdit aux deux** | explicite | הא פחות מגובה י' אפילו הם סמוכים או מופלגים אע״ג שגבוהים י' הוי אף לחצר ושניהם אסורים | BY OH 375 (sa lecture du Rambam, appuyée sur la michna) |
| Michna Beroura | **interdit aux deux** | explicite | מן הארץ וגם מן המרפסת שלמעלה מהם אין נמוך ממנה עשרה טפחים דאז נוח לשניהם להשתמש שם ולכן אוסרים זה על זה … ודוקא כשהיה התל והעמוד סמוך להמרפסת בתוך ד״ט | MB 375 ס״ק ו ; ס״ק ז |
| Choul'han Aroukh HaRav | **interdit aux deux** | explicite | וְאִם הוּא תּוֹךְ עֲשָׂרָה לִשְׁנֵיהֶם … וְאִם אֵינוֹ מֻפְלָג ד', שְׁנֵיהֶם אֲסוּרִים | SAH OH 375:2 |
| autre : Magen Avraham | **interdit aux deux** | explicite | וגם למרפסת אין גבוהים י' דהוי לשניהם בנחת | מג״א שע״ה (un seul segment sur Sefaria, sur « אינם גבוהים ») |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **hors de ce cadre** | — | — | hors de ce cadre : Rachi y suppose les chambres hautes bien plus hautes que le tertre (« דגביהי ממרפסת טובא »), et ce cas, à moins de dix sous la galerie, n'y entre pas [corrigé à la vérification stricte du nœud, passe 4 : « non écrit », avec « Rachi n'y explique que le tertre sous les chambres hautes » — Rachi explique aussi, sur la même page, la lecture où la guemara conclut]. Dans la lecture où la guemara conclut (Rav Houna, « כִּדְאָמַר רַב הוּנָא: לְאוֹתָן הַדָּרִים בַּמִּרְפֶּסֶת », puis « שמע מינה »), elle écrit ce cas : interdit aux deux — « לָזֶה בְּפֶתַח וְלָזֶה בְּפֶתַח הוּא! מַאי ״לֶחָצֵר״? אַף לֶחָצֵר. וּשְׁנֵיהֶן אֲסוּרִין » ‖ Rachi « לזה בפתח ולזה בפתח הוא - ותרוייהו בעי איתסורי ביה דהא סתם מרפסת לא גביהה טובא » (עירובין פ״ד ע״א et Rachi) |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **non écrit** | — | — | le séif ד ne distingue pas (« כל שהוא למטה מעשרה … מהחצר ») ; c'est la MB ס״ק טו qui interdit aux deux la saillie à moins de dix de l'une et de l'autre (« וה״ה כשהיה פחות מעשרים טפחים … לא לזה ולא לזה ») |

### Cas 2 — `H<10 G<10 E>=4`

Moins de dix au-dessus de la cour ; à moins de dix sous la galerie ; écarté de quatre téfahim ou plus de devant la galerie (מופלג).

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **interdit aux deux** | règle générale | אם אינם גבוהים י״ט הרי אלו נחשבי' בין החצר ובין המרפסת ושניהם אסורים להוציא שם כלים שבבתים | SA OH 375:2 (Maginei Eretz) — deux lectures écrites de la première phrase : sans distinction, interdit aux deux (BY sur le Rambam, Taz) ; limitée au tertre proche, ce cas étant hors de sa portée (MB ס״ק ז), qui le donne à la cour. Le MA rapporte les deux lectures (BY ; Tour et posekim) et ne tranche pas [corrigé à la vérification stricte, passe 1 : la référence nommait le MA avec la MB, contre sa propre cellule] |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **interdit aux deux** | explicite | מבואר דברישא באין גבוהין י' אסור לשניהם אפילו במופלג ד' ממרפסת מדלא זכר ברישא מחילוק מופלג או סמוך … ואפי' יש לחצר מעלה ולמרפסת ריעותא | ט״ז שע״ה ס״ק ב |
| Taz (shita du Tour) | **à la cour** | règle générale | הכלל מסעי' זה דכל שלזה תשמישו בנחת ולזה בקשה לא מקרי רק רשות לאותו שתשמישו בנחת … ועוד קרוי קשה אפי' אם הוא פחות מי' טפחים כגון אם הוא מופלג בריחוק המשך ממנו ד״ט | ט״ז שע״ה ס״ק ב |
| Tour | **à la cour** | explicite | או אם הוא תוך י' לשניהן ורחוק מן המרפסת ד' טפחים בני החצר מותרין בו שהוא נוח להם יותר | Tour OH 375 |
| Beit Yossef | **interdit aux deux** | explicite | ולא חילק בין אם מופלגים ארבעה לאם אינם מופלגין משמע נמי דאע״פ שהן מופלגין מן המרפסת ד' ואינם גבוהין י' טפחים רשות מרפסת שולטת בהם ג״כ | BY OH 375 (lecture du Rambam, qu'il dit prouvée par le sens simple de la michna telle que la guemara la conclut : « ופשטא דמתני' כוותיה מוכחא … הרי בהדיא לא משכחת לה צד היתרא אלא בשני תנאים » ; selon lui, le Tour doit forcer le texte, « צריך לדחוק » — voir la voix « guemara selon Rachi ») [précisé à la passe 5] |
| Michna Beroura | **à la cour** | explicite | ודוקא כשהיה התל והעמוד סמוך להמרפסת בתוך ד״ט דאם היו רחוקים ממנו ד״ט א״כ תשמיש המרפסת עליו בקשה והחצר בנחת ונותנים אותו לבני החצר | MB 375 ס״ק ז (cadre G<10 : ס״ק ו) |
| Choul'han Aroukh HaRav | **à la cour** | explicite | וְאִם הוּא תּוֹךְ עֲשָׂרָה לִשְׁנֵיהֶם … אִם הוּא מֻפְלָג מִכְּנֶגֶד הַמִּרְפֶּסֶת ד', נוֹתְנִים אוֹתוֹ לֶחָצֵר, שֶׁתַּשְׁמִישׁוֹ לָהּ בְּנַחַת יוֹתֵר מִלַּמִּרְפֶּסֶת | SAH OH 375:2 |
| autre : Magen Avraham | **deux avis rapportés** | explicite | וכתב הב״י דאף ע״פ שרחוק ד' מן המרפסת שניהם אסורים דבני המרפסת יכולים להשתמש עליו בזריקה אבל בטור ובפוסקים משמע דכל פחות מי' לאו כלום הוא ונותנין אותו לבני החצר אם הוא רחוק ד' מן המרפסת … ואפשר שגם דעת הרמב״ם כן אלא שדרכו לסתום | מג״א שע״ה — il rapporte le BY, puis ce qu'il lit « בטור ובפוסקים », et ajoute que le Rambam pense peut-être comme eux (« ואפשר שגם דעת הרמב״ם כן ») : il ne tranche pas |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **hors de ce cadre** | — | — | hors de ce cadre : Rachi y suppose les chambres hautes bien plus hautes que le tertre (« דגביהי ממרפסת טובא »), et ce cas, à moins de dix sous la galerie, n'y entre pas [corrigé à la vérification stricte du nœud, passe 4 : « non écrit », avec « Rachi n'y explique que le tertre sous les chambres hautes » — Rachi explique aussi, sur la même page, la lecture où la guemara conclut]. Dans la lecture où la guemara conclut (Rav Houna), ce cas se lit de deux façons, toutes deux écrites par le BY. (1) Interdit aux deux : le BY lit dans la michna, telle que la guemara la conclut, que la clause « אֲבָל בְּמוּפְלֶגֶת, אֲפִילּוּ גָּבוֹהַּ עֲשָׂרָה טְפָחִים — לֶחָצֵר … אַף לֶחָצֵר, וּשְׁנֵיהֶן אֲסוּרִין » couvre, par son « אפילו », le tertre de moins de dix écarté, et il dit que c'est explicite et le sens simple : « ופשטא דמתני' כוותיה מוכחא … אבל במופלגת בין גבוה י' טפחים בין פחות מי' לחצר כלומר אף לחצר כדמוקי בגמרא הרי בהדיא לא משכחת לה צד היתרא אלא בשני תנאים ». (2) À la cour : la lecture qu'il prête au Tour, en disant qu'elle force le texte : « ולדעת רבינו צריך לדחוק … לצדדין קתני דבגבוה מי' הוי אף לחצר ושניהם אסורים ובפחות מי' הוי דוקא לחצר ושרי ». [Corrigé à la vérification stricte du nœud, passe 5 : la référence disait que la phrase « ne distingue pas l'écart » et que la guemara « n'écrit pas ce cas en tant que tel ».] |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **non écrit** | — | — | la saillie part du mur : le séif ד n'a pas de cas écarté |

### Cas 3 — `H<10 G>=10 E<4`

Moins de dix au-dessus de la cour ; plus bas que la galerie de dix ou plus ; à moins de quatre téfahim de devant la galerie.

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **interdit aux deux** | règle générale | אם אינם גבוהים י״ט הרי אלו נחשבי' בין החצר ובין המרפסת ושניהם אסורים להוציא שם כלים שבבתים | SA OH 375:2 (Maginei Eretz) — aucune parenthèse dans la première phrase ; deux lectures écrites : sans distinction, interdit aux deux (Taz selon le Rambam) ; limitée au tertre à moins de dix sous la galerie, ce cas étant hors de sa portée (MB ס״ק ו, MA), qui le donnent à la cour. Le séif ד du même siman donne à la cour la saillie dans la position analogue (voir la voix « SA 375:ד ») |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **interdit aux deux** | explicite | וא״כ גם ברישא באין גבוהים י' ה״ל להגיה גם נמוכים ממרפסת פחות מי' דאז דוקא שוה לשניהם אבל בנמוך י' ממרפסת בני החצר מותרים כדעת הטור ולהרמב״ם אינו כן | ט״ז שע״ה ס״ק ב — c'est la thèse écrite du Taz ; le Rambam (4:17) et le Mehaber (375:ד) donnent pourtant à la cour la saillie à moins de dix de la cour et à plus de dix sous la chambre haute, et le Taz ne dit pas comment il les concilie (« ce que la source laisse ouvert », 1) |
| Taz (shita du Tour) | **à la cour** | explicite | ובטור כתוב ואם אינו גבוה י' לבני החצר וממנו למרפסת ד' צ״ל יו״ד במקום דל״ת … אבל בנמוך י' ממרפסת בני החצר מותרים כדעת הטור | ט״ז שע״ה ס״ק ב |
| Tour | **à la cour** | règle générale | ואם אינו גבוה י' לבני החצר וממנו למרפסת ארבעה … אבל כל שתשמישו בנחת יותר מלחבירו נותנין אותו למי שהוא בנחת בין אם הוא עליון או תחתון | Tour OH 375 (texte imprimé « ארבעה », que le Taz corrige en י׳ ; sans la correction, le cas relève de la règle finale) |
| Beit Yossef | **non écrit** | — | — | BY OH 375 — il ne parle jamais de la hauteur sous la galerie dans sa lecture du Rambam, et ses deux règles tirent en sens contraires : « והלכך כל היכא דאפשר לבני חצר להשתמש עליהם שניהם אסורין ולא משכחת לה צד היתר אלא בגבוהים י' ואינם מופלגים ד' דהשתא הוי לבני מרפסת בנחת ולבני חצר בזריקה ונותנין אותה לזה שבנחת » (tirée de l'écart : « מהטעם שכתבתי דבכה״ג בני מרפסת יכול להשתמש בהם ע״י זריקה ») ; et, pour Rav, « לרב שניהם אסורים עד שיהא לזה בנחת לגמרי דומיא דפתח ולזה בקשה וגם זה סעד לדברי הרמב״ם » ; il ajoute que le Rambam écrit la saillie « ביני וביני » (« וג״ז כתב הרמב״ם »). Voir « ce que la source laisse ouvert », 6 |
| Michna Beroura | **à la cour** | explicite | דאם היה נמוך מן המרפסת עשרה טפחים אז היו נותנים אותו לבני החצר דלהם תשמישו בנחת | MB 375 ס״ק ו |
| Choul'han Aroukh HaRav | **à la cour** | explicite | וְאִם הוּא תּוֹךְ עֲשָׂרָה לֶחָצֵר, וְיוֹתֵר מֵעֲשָׂרָה לַמִּרְפֶּסֶת — נוֹתְנִים אוֹתוֹ לֶחָצֵר בְּכָל עִנְיָן, אַף עַל פִּי שֶׁאֵינוֹ מֻפְלָג ד' מִכְּנֶגֶד הַמִּרְפֶּסֶת | SAH OH 375:2 |
| autre : Magen Avraham | **à la cour** | explicite | אבל בטור ובפוסקים משמע דכל פחות מי' לאו כלום הוא ונותנין אותו לבני החצר אם הוא רחוק ד' מן המרפסת או נמוך ממנו י' דאין אדם אוסר על חבירו דרך אויר | מג״א שע״ה (attribué « בטור ובפוסקים » ; le rapport du BY, juste avant, ne porte que sur l'écart) |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **non écrit** | — | — | hors de ce passage : Rachi n'y explique que le tertre sous les chambres hautes (נמוך מן העלייה י') ; ce cas n'y est pas expliqué |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **à la cour** | règle générale | זיזים היוצאים מהכתלים כל שהוא למטה מעשרה טפחים הרי זה נחשב מהחצר ובני החצר משתמשין בו ‖ מיירי בשהיו יותר מעשרים טפחים מן העליה לקרקע החצר | SA OH 375:4 (= Rambam Érouvin 4:17) ‖ MB 375 ס״ק טו — règle écrite pour la saillie, non pour le tertre : la saillie à moins de dix de la cour, la chambre haute à plus de vingt (MB), donc à plus de dix au-dessus d'elle, collée au mur sous la chambre haute ; mêmes parties (MB ס״ק ו : « ולבני המרפסת [היינו אנשי העליה …] ») |

### Cas 4 — `H<10 G>=10 E>=4`

Moins de dix au-dessus de la cour ; plus bas que la galerie de dix ou plus ; écarté de quatre téfahim ou plus de devant la galerie.

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **interdit aux deux** | règle générale | אם אינם גבוהים י״ט הרי אלו נחשבי' בין החצר ובין המרפסת ושניהם אסורים להוציא שם כלים שבבתים | SA OH 375:2 (Maginei Eretz) — deux lectures écrites : sans distinction, interdit aux deux (Taz ; BY sur le Rambam pour l'écart, sans nommer la hauteur sous la galerie) ; hors de sa portée selon la MB (ס״ק ו, ז) et le MA (par la hauteur sous la galerie), qui donnent ce cas à la cour |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **interdit aux deux** | explicite | מבואר דברישא באין גבוהין י' אסור לשניהם אפילו במופלג ד' ממרפסת … אבל בנמוך י' ממרפסת בני החצר מותרים כדעת הטור ולהרמב״ם אינו כן | ט״ז שע״ה ס״ק ב (deux phrases, chacune écarte expressément une variable dans la רישא) |
| Taz (shita du Tour) | **à la cour** | explicite | אבל בנמוך י' ממרפסת בני החצר מותרים כדעת הטור | ט״ז שע״ה ס״ק ב (l'écart n'y est pas distingué : la clause couvre ce cas sous toute lecture, comme au cas 3) |
| Tour | **à la cour** | explicite | ואם אינו גבוה י' לבני החצר וממנו למרפסת ארבעה … בני החצר מותרין בו שהוא נוח להם יותר | Tour OH 375 (lu « י׳ » par le Taz, « מתרי טעמי » — loin de dix et écarté de quatre — par le BY : les deux lectures couvrent ce cas) |
| Beit Yossef | **interdit aux deux** | règle générale | משמע דכל שמופלגין מן המרפסת ד' בין גבוהין י' בין אינם גבוהין י' שניהם אסורין … והלכך כל היכא דאפשר לבני חצר להשתמש עליהם שניהם אסורין | BY OH 375 (lecture du Rambam, après « אבל הרמב״ם כתב ») — la hauteur sous la galerie n'y est pas nommée ; sa règle pour Rav (« עד שיהא לזה בנחת לגמרי דומיא דפתח ולזה בקשה ») ne tranche pas ce cas, puisqu'il interdit déjà le tertre écarté de quatre où la cour est בנחת (cas 2) ; voir « ce que la source laisse ouvert », 6 |
| Michna Beroura | **à la cour** | explicite | דאם היה נמוך מן המרפסת עשרה טפחים אז היו נותנים אותו לבני החצר … דאם היו רחוקים ממנו ד״ט א״כ תשמיש המרפסת עליו בקשה והחצר בנחת ונותנים אותו לבני החצר | MB 375 ס״ק ו ; ס״ק ז |
| Choul'han Aroukh HaRav | **à la cour** | explicite | וְאִם הוּא תּוֹךְ עֲשָׂרָה לֶחָצֵר, וְיוֹתֵר מֵעֲשָׂרָה לַמִּרְפֶּסֶת — נוֹתְנִים אוֹתוֹ לֶחָצֵר בְּכָל עִנְיָן | SAH OH 375:2 |
| autre : Magen Avraham | **à la cour** | explicite | אבל בטור ובפוסקים משמע דכל פחות מי' לאו כלום הוא ונותנין אותו לבני החצר אם הוא רחוק ד' מן המרפסת או נמוך ממנו י' | מג״א שע״ה (disjonction : ce cas remplit les deux branches ; le rapport du BY est posé sous « וגם למרפסת אין גבוהים י' » : il ne porte pas sur ce cas) |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **non écrit** | — | — | hors de ce passage : Rachi n'y explique que le tertre sous les chambres hautes (נמוך מן העלייה י') ; ce cas n'y est pas expliqué |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **non écrit** | — | — | la saillie part du mur : le séif ד n'a pas de cas écarté |

### Cas 5 — `H>=10 G<10 E<4`

Haut de dix ou plus au-dessus de la cour ; à moins de dix sous la galerie ; à moins de quatre téfahim de devant la galerie.

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **à la galerie** | explicite | ואם הם גבוהים מקרקעית החצר י״ט <small>(ובתוך עשרה למרפסת (טור)</small> והם בתוך ד' טפחים למרפסת בני מרפסת מותרים לפי שתשמישו (להם) בנחת מלבני החצר | SA OH 375:2 (Maginei Eretz ; la parenthèse est en <small>, non refermée) |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **à la galerie** | explicite | ואם הם גבוהים מקרקעית החצר י״ט … והם בתוך ד' טפחים למרפסת בני מרפסת מותרים ‖ אלא שאם יש למרפסת מעלה ולחצר ריעותא אז יש היתר למרפסת היינו בגובה י' ואינם רחוקים ד' טפחים | SA OH 375:2 hors parenthèse ‖ ט״ז שע״ה ס״ק ב |
| Taz (shita du Tour) | **à la galerie** | règle générale | הכלל מסעי' זה דכל שלזה תשמישו בנחת ולזה בקשה לא מקרי רק רשות לאותו שתשמישו בנחת ואין השני יכול למחות בידו כלל | ט״ז שע״ה ס״ק ב |
| Tour | **à la galerie** | explicite | אם הוא גבוה מקרקעית החצר י' טפחים ואין מראשו למרפסת י' טפחים והוא בתוך ד״ט למרפסת בני מרפסת מותרין בו לפי שתשמישו להם בנחת מלבני החצר | Tour OH 375 |
| Beit Yossef | **à la galerie** | explicite | לא משכחת לה צד היתרא אלא בשני תנאים גבוהים י' טפחים וסמוכים דאז בני מרפסת מותרין | BY OH 375 |
| Michna Beroura | **à la galerie** | explicite | שתשמישו להם בנחת - שהם לה בתוך י״ט וגם אינם מופלגים ממנה | MB 375 ס״ק ט |
| Choul'han Aroukh HaRav | **à la galerie** | explicite | אִם הוּא גָבוֹהַּ עֲשָׂרָה מִקַּרְקָעִית הֶחָצֵר וְאֵינוֹ נָמוּךְ עֲשָׂרָה מִמִּרְפֶּסֶת, נוֹתְנִים אוֹתוֹ לִבְנֵי הַמִּרְפֶּסֶת … בַּמֶּה דְּבָרִים אֲמוּרִים? כְּשֶׁהוּא סָמוּךְ לַמִּרְפֶּסֶת | SAH OH 375:2 (repris en 375:3) |
| autre : Magen Avraham | **à la galerie** | règle générale | בור שבחצר אם היה מלא פירות טבלים שאסור לטלטלם בשבת הרי הוא וחליתו כסלע ומחשב למרפסת כמש״ל | מג״א שע״ה — par renvoi (« כמש״ל »), en recopiant le Rambam (4:18) sur la citerne ; la hauteur sous la galerie n'y est pas nommée |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **hors de ce cadre** | — | — | hors de ce cadre : Rachi y suppose les chambres hautes bien plus hautes que le tertre (« דגביהי ממרפסת טובא »), et ce cas, à moins de dix sous la galerie, n'y entre pas [corrigé à la vérification stricte du nœud, passe 4 : « non écrit », avec « Rachi n'y explique que le tertre sous les chambres hautes » — Rachi explique aussi, sur la même page, la lecture où la guemara conclut]. Dans la lecture où la guemara conclut (Rav Houna, « לְאוֹתָן הַדָּרִים בַּמִּרְפֶּסֶת »), elle écrit ce cas : à la galerie — la michna « לַמִּרְפֶּסֶת … בַּמֶּה דְּבָרִים אֲמוּרִים בִּסְמוּכָה » ‖ Rachi « הדרין במרפסת - כגון שיש בה דיורין דלדידהו הוי האי תל שבחצר שוה להן בתוך עשרה » ; le BY tire de cette réponse la condition du Tour (« מדאוקימנא מאי מרפסת לאותם הדרין במרפסת ») |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **à la galerie** | règle générale | וכל שהוא בתוך י״ט העליונים הסמוכים לעלייה אנשי עלייה משתמשין בו ‖ מיירי בשהיו יותר מעשרים טפחים מן העליה לקרקע החצר | SA OH 375:4 (= Rambam Érouvin 4:17) ‖ MB 375 ס״ק טו — règle écrite pour la saillie, non pour le tertre |

### Cas 6 — `H>=10 G<10 E>=4`

Haut de dix ou plus au-dessus de la cour ; à moins de dix sous la galerie ; écarté de quatre téfahim ou plus de devant la galerie.

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **interdit aux deux** | explicite | ואם היו רחוקים מהמרפס' ד״ט או יותר אע״פ שגבוהים עשרה <small>(מן החצר לתוך עשרה למרפסת) (טור)</small> הרי אלו בכלל החצר והמרפס' לפי ששניהם אפשר להשתמש בהם על ידי זריקה לפיכך שניהם אסורים להוציא שם כלים ששבתו בבתים עד שיערבו | SA OH 375:2 (Maginei Eretz) |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **interdit aux deux** | explicite | ואם היו רחוקים מהמרפס' ד״ט או יותר אע״פ שגבוהים עשרה … הרי אלו בכלל החצר והמרפס' לפי ששניהם אפשר להשתמש בהם על ידי זריקה לפיכך שניהם אסורים ‖ וכן אם לשניהם ריעותא ג״כ אוסרים זה על זה | SA OH 375:2 hors parenthèse ‖ ט״ז שע״ה ס״ק ב — ce cas est dans la portée de la phrase sous toute lecture de la hauteur sous la galerie |
| Taz (shita du Tour) | **interdit aux deux** | explicite | ומ״ש כאן ואם היו רחוקים מהמרפסת ד' טפחים או יותר אע״ג שגבוהי' י' מן החצר לתוך י' למרפסת היינו שלכל א' יש לבעל החצר ריעות' מכח זריקה ולבעל מרפסת מכח הפלגה ד״ט ולגביה אין ריעותא מכח שלשול כיון שהוא תוך י' שלו וע״כ אסור ששניהם שולטים בו | ט״ז שע״ה ס״ק ב |
| Tour | **interdit aux deux** | explicite | או שהוא גבוה י' לבני החצר ורחוק ד' מן המרפסת … שניהם אסורין | Tour OH 375 — la clause ne nomme pas la hauteur sous la galerie ; ce cas est dans sa portée sous toute lecture (le séif lui prête « (מן החצר לתוך עשרה למרפסת) (טור) ») |
| Beit Yossef | **interdit aux deux** | explicite | משמע דכל שמופלגין מן המרפסת ד' בין גבוהין י' בין אינם גבוהין י' שניהם אסורין | BY OH 375 |
| Michna Beroura | **interdit aux deux** | explicite | אפ״ה כיון שמופלגין ממנה ד״ט וכשרוצים בני מרפסת להשתמש שם הוא רק ע״י זריקה מקרי תשמישו ג״כ בקשה זה מחמת גובהו וזה מחמת רחקו | MB 375 ס״ק י |
| Choul'han Aroukh HaRav | **interdit aux deux** | explicite | אִם הוּא גָבוֹהַּ עֲשָׂרָה מִקַּרְקָעִית הֶחָצֵר וְאֵינוֹ נָמוּךְ עֲשָׂרָה מִמִּרְפֶּסֶת … אֲבָל אִם הוּא מֻפְלָג מִכְּנֶגְדָּהּ ד' טְפָחִים … וְלָכֵן אוֹסְרִים זֶה עַל זֶה, וּשְׁנֵיהֶם אֲסוּרִים בּוֹ בְּכֵלִים שֶׁשָּׁבְתוּ בַּבַּיִת עַד שֶׁיְּעָרְבוּ | SAH OH 375:2 |
| autre : Magen Avraham | **non écrit** | — | — | מג״א שע״ה — n'en parle pas |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **hors de ce cadre** | — | — | hors de ce cadre : Rachi y suppose les chambres hautes bien plus hautes que le tertre (« דגביהי ממרפסת טובא »), et ce cas, à moins de dix sous la galerie, n'y entre pas [corrigé à la vérification stricte du nœud, passe 4 : « non écrit », avec « Rachi n'y explique que le tertre sous les chambres hautes » — Rachi explique aussi, sur la même page, la lecture où la guemara conclut]. Dans la lecture où la guemara conclut (Rav Houna), elle écrit ce cas : interdit aux deux — « אֲבָל בְּמוּפְלֶגֶת, אֲפִילּוּ גָּבוֹהַּ עֲשָׂרָה טְפָחִים — לֶחָצֵר … אֶלָּא מַאי ״לֶחָצֵר״ — אַף לֶחָצֵר, וּשְׁנֵיהֶן אֲסוּרִין » ‖ Rachi « אלא - על כרחך אף לחצר ואסורין לרב נמי דמתרץ לה בדיורי מרפסת » |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **non écrit** | — | — | la saillie part du mur : le séif ד n'a pas de cas écarté |

### Cas 7 — `H>=10 G>=10 E<4`

Haut de dix ou plus au-dessus de la cour ; plus bas que la galerie de dix ou plus ; à moins de quatre téfahim de devant la galerie (pour la cour par jet, pour la galerie par descente : לזה בזריקה ולזה בשלשול).

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **non écrit** | — | — | SA OH 375:2 — la parenthèse « (ובתוך עשרה למרפסת (טור) » retire ce cas de la permission à la galerie ; le séif imprimé n'en écrit pas l'issue. Le séif ד du même siman écrit le cas analogue de la saillie entre les deux dizaines : interdit aux deux (voir la voix « SA 375:ד ») |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **non écrit** | — | — | ט״ז שע״ה ס״ק ב — le Taz n'écrit pas ce cas. Ses deux règles pour le Rambam tirent en sens contraires : « אז יש היתר למרפסת היינו בגובה י' ואינם רחוקים ד' טפחים ולא זכר הרמב״ם כלל מענין נמוך התל ממרפסת י' או יותר » d'un côté ; « וכן אם לשניהם ריעותא ג״כ אוסרים זה על זה » de l'autre, avec, plus haut, la descente de dix comptée comme malaisée (« וכן בשלשול דהיינו שהמקום נמוך ממנו י״ט וצריך לשלשל שם ») ; et son « ולהרמב״ם אינו כן » ne vise que la רישא. En face : Rambam 4:17 et SA 375:ד, la saillie entre les deux dizaines interdite aux deux ; BY, le Rambam tranche comme Rav. Voir « ce que la source laisse ouvert », 1 |
| Taz (shita du Tour) | **interdit aux deux** | explicite | אלא דאם לא' בזריקה ולא' בשלשול ס״ל לשמואל … ורב סבירא ליה דלא מיקרי נחת אלא במשתמש דרך פתח אבל כאן לא אכפת לן בנחת קצת ושלשול וזריקה שוין הם ואסור והכי קי״ל … ונ״ל דכיון דכבר כ' הטור דין שלשול וזריקה דאסור | ט״ז שע״ה ס״ק ב (l'écart est chez lui une ריעותא distincte, traitée à part sous « תרתי לריעות׳ » : « לא׳ בשלשול » est ce cas) |
| Tour | **interdit aux deux** | explicite | ואם הוא לשניהן שוה תוך י' או יותר מי' והוא בתוך ד' למרפסת … שניהם אסורין | Tour OH 375 |
| Beit Yossef | **interdit aux deux** | explicite | לזה בשלשול ולזה בזריקה מאי אמר רב שתיהן אסורים … ותל שבחצר שהוא גבוה י' הוי נמוך מן העלייה י' דהוי לזה בשלשול ולזה בזריקה … וידוע דהלכה כרב באיסורי וכן פסק הרא״ש שם והרמב״ם בפ״ד מה״ע | BY OH 375 (la guemara, Rachi qui y nomme ce cas, puis la décision ; il ajoute plus bas que le Rambam écrit la saillie « ביני וביני », interdite aux deux) |
| Michna Beroura | **interdit aux deux** | explicite | דאם היה מרוחק עשרה גם ממרפסת היה לשניהם בקשה ויד שניהן שוין בו לאסור זה על זה | MB 375 ס״ק ח |
| Choul'han Aroukh HaRav | **interdit aux deux** | explicite | אוֹ יוֹתֵר מֵעֲשָׂרָה לִשְׁנֵיהֶם … וְאִם אֵינוֹ מֻפְלָג ד', שְׁנֵיהֶם אֲסוּרִים | SAH OH 375:2 |
| autre : Magen Avraham | **interdit aux deux** | explicite | ועסס״י שנ״ה דאם לא' בשלשול ולא' בזריקה גובה י' ובשלשול שניהם אסורים וכ״ה בגמ' ובהג״א וצ״ע שהרא״ש סכ״א ד״ה לא כ' כן | מג״א שע״ה (« לא' בשלשול ולא' בזריקה » désigne ce cas, comme chez le Taz ; renvoi au siman 355, avec un צ״ע sur le Roch) |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **deux avis rapportés** | explicite | לזה בשלשול ולזה בזריקה מאי אמר רב שתיהן אסורים ושמואל אמר נותנין אותו לזה שבשלשול … ותל שבחצר שהוא גבוה י' הוי נמוך מן העלייה י' דהוי לזה בשלשול ולזה בזריקה וקתני דבני עלייה מותרין בו | guemara Érouvin 84a et Rachi, cités par le BY — Rav : interdit aux deux ; Chmouel : à la galerie (lecture de la michna que la guemara écarte ensuite par « לאותם הדרים במרפסת ») ; le BY tranche : « וידוע דהלכה כרב באיסורי » |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **interdit aux deux** | règle générale | והנשאר בין י' התחתונים עד התחלת י' העליונים מן הזיזין היוצאים שניהם אסורים בו ‖ מיירי בשהיו יותר מעשרים טפחים מן העליה לקרקע החצר ‖ ודייק אליבא דרב דקי״ל כוותיה הא דביני וביני אסור וג״ז כתב הרמב״ם בפרק הנזכר ולא כתבו רבינו לפי שממה שכתב הוא נלמד | SA OH 375:4 (= Rambam Érouvin 4:17, « שְׁנֵיהֶן אֲסוּרִין בּוֹ ») ‖ MB 375 ס״ק טו ‖ BY OH 375 — règle écrite pour la saillie, non pour le tertre : plus de dix au-dessus de la cour, plus de dix sous la chambre haute, collée au mur ; le BY la dit selon Rav et « נלמד » de la loi du tertre |

### Cas 8 — `H>=10 G>=10 E>=4`

Haut de dix ou plus au-dessus de la cour ; plus bas que la galerie de dix ou plus ; écarté de quatre téfahim ou plus (« תרתי לריעות' » pour la galerie, dans les mots du Taz).

| Voix | Issue | Mode | Citation (extraite) | Réf. |
|---|---|---|---|---|
| séif imprimé (SA 375:2, Maginei Eretz) | **non écrit** | — | — | SA OH 375:2 — la parenthèse « (מן החצר לתוך עשרה למרפסת) (טור) » limite la dernière phrase au tertre à moins de dix sous la galerie ; le séif imprimé n'écrit pas l'issue de ce cas |
| Rambam selon le Taz (mots du séif hors parenthèses, lus par le Taz ס״ק ב) | **interdit aux deux** | règle générale | ואם היו רחוקים מהמרפס' ד״ט או יותר אע״פ שגבוהים עשרה … הרי אלו בכלל החצר והמרפס' ‖ כל זה שיטת הטור אבל הרמב״ם לא ס״ל כך … וכן אם לשניהם ריעותא ג״כ אוסרים זה על זה … ולא זכר הרמב״ם כלל מענין נמוך התל ממרפסת י' או יותר | SA OH 375:2 hors parenthèse ‖ ט״ז שע״ה ס״ק ב |
| Taz (shita du Tour) | **à la cour** | explicite | ואם היו תרתי לריעות' לבעל המרפסת דהיינו למעלה מי' ומופלג נ״ל שמותר בעל החצר בהתל ואין בעל המרפסת יוכל לאסור עליו מפני שאין אדם אוסר דרך אויר | ט״ז שע״ה ס״ק ב (« נ״ל » : sa conclusion, que le Tour n'écrit pas ; puis « כל זה שיטת הטור ») |
| Tour | **non écrit** | — | — | Tour OH 375 — « או שהוא גבוה י' לבני החצר ורחוק ד' מן המרפסת … שניהם אסורין » ne fixe pas la hauteur sous la galerie. Les deux voix qui lisent cette clause n'y mettent pas ce cas : le séif lui prête « (מן החצר לתוך עשרה למרפסת) (טור) », et le Taz, dans la shita du Tour, tranche ce cas par son propre « נ״ל ». Lue sans condition, elle l'interdirait. Voir « ce que la source laisse ouvert », 2 |
| Beit Yossef | **interdit aux deux** | explicite | דלשניהם תשמישו בקשה לחצר בזריקת גובה ולעלייה בזריקה את משך ההפלגה ובשלשול את הנמוכות ונהי דלשמואל שלשול לגבי זריקת גובה נוח היא הכא דאיכא שלשול וזריקת משך שוים הם לזריקת גובה ואמאי לחצר … משמע דכל שמופלגין מן המרפסת ד' בין גבוהין י' בין אינם גבוהין י' שניהם אסורין | BY OH 375 — explicite par Rachi, qu'il recopie sur la guemara ; puis sa propre lecture du Rambam |
| Michna Beroura | **deux avis rapportés** | explicite | ואם היו נמוכים עשרה טפחים גם מהמרפסת יש דעות בפוסקים יש אומרים דכיון שלבעל המרפסת יש שתי ריעותות שנמוכים מעשרה וגם מופלגים ד״ט א״כ תשמיש של אנשי החצר נוח יותר שם ונותנין אותו להם ויש אומרים דכיון שלהחצר נמי גבוה י״ט מקרי לשניהם תשמישו בקשה ואוסרין זה ע״ז | MB 375 ס״ק י״א |
| Choul'han Aroukh HaRav | **à la cour** | explicite | אוֹ יוֹתֵר מֵעֲשָׂרָה לִשְׁנֵיהֶם — אִם הוּא מֻפְלָג מִכְּנֶגֶד הַמִּרְפֶּסֶת ד', נוֹתְנִים אוֹתוֹ לֶחָצֵר, שֶׁתַּשְׁמִישׁוֹ לָהּ בְּנַחַת יוֹתֵר מִלַּמִּרְפֶּסֶת | SAH OH 375:2 |
| autre : Magen Avraham | **non écrit** | — | — | מג״א שע״ה — son « אין אדם אוסר על חבירו דרך אויר » est écrit sous « כל פחות מי' », pas pour le tertre haut de dix |
| autre : guemara Érouvin 84a selon Rachi, cadre « בני עלייה » (cité par le BY) | **interdit aux deux** | explicite | מאי לחצר אילימא לחצר ושרי אמאי רשותא דתרווייהו הוא אלא מאי לחצר אף לחצר ושניהם אסורין … דלשניהם תשמישו בקשה לחצר בזריקת גובה ולעלייה בזריקה את משך ההפלגה ובשלשול את הנמוכות ונהי דלשמואל שלשול לגבי זריקת גובה נוח היא הכא דאיכא שלשול וזריקת משך שוים הם לזריקת גובה ואמאי לחצר | guemara Érouvin 84a et Rachi, cités par le BY — même selon Chmouel ; contre le « נ״ל » du Taz et contre le SAH (à la cour) |
| autre : SA 375:ד = Rambam Érouvin 4:17 (saillies, cas analogue) | **non écrit** | — | — | la saillie part du mur : le séif ד n'a pas de cas écarté |

## Ce que la source laisse ouvert

1. **Rambam selon le Taz, cas 7 (`H>=10 G>=10 E<4`) : non écrit.** Cette cellule reprenait les décisions 158 et 161 de la mémoire (« à la galerie » par règle générale). Elle est rouverte sur des pièces nouvelles, qu'aucune passe n'avait ouvertes.
   - Le Taz n'écrit pas ce cas. Il écrit « אז יש היתר למרפסת היינו בגובה י' ואינם רחוקים ד' טפחים ולא זכר הרמב״ם כלל מענין נמוך התל ממרפסת י' או יותר ». Il ne convertit expressément le silence du Rambam en indifférence (« ולהרמב״ם אינו כן ») que pour la רישא.
   - Ses propres règles tirent en sens contraires. D'un côté, la permission à la galerie sans condition de hauteur. De l'autre, « וכן אם לשניהם ריעותא ג״כ אוסרים זה על זה », alors qu'il compte plus haut la descente de dix comme malaisée (« וכן בשלשול דהיינו שהמקום נמוך ממנו י״ט וצריך לשלשל שם »).
   - Le Rambam écrit, au paragraphe suivant, la saillie entre les deux dizaines : « וְהַנִּשְׁאָר בֵּין עֲשָׂרָה הַתַּחְתּוֹנִים עַד תְּחִלַּת עֲשָׂרָה הָעֶלְיוֹנִים מִן הַזִּיזִין הַיּוֹצְאִין שָׁם שְׁנֵיהֶן אֲסוּרִין בּוֹ » (4:17), et le Mehaber le recopie au séif ד du même siman. La MB (ס״ק טו) place la chambre haute à plus de vingt téfahim, et (ס״ק ו) les gens de la galerie sont ceux de la chambre haute : même géométrie, mêmes parties.
   - Le BY rattache cette loi à Rav et au Rambam (« ודייק אליבא דרב דקי״ל כוותיה הא דביני וביני אסור וג״ז כתב הרמב״ם בפרק הנזכר ולא כתבו רבינו לפי שממה שכתב הוא נלמד »). Il écrit aussi que le Rambam tranche comme Rav sur la descente contre le jet (« וידוע דהלכה כרב באיסורי וכן פסק הרא״ש שם והרמב״ם בפ״ד מה״ע »).
   - Le Rambam interdit la citerne pleine d'eau (4:18 « אֲבָל אִם הָיָה מָלֵא מַיִם אֵין בְּנֵי חָצֵר וְלֹא בְּנֵי מִרְפֶּסֶת מַכְנִיסִין מִמֶּנּוּ לַבָּתִּים עַד שֶׁיְּעָרְבוּ »), et la guemara que recopie le BY en donne la raison : « בבור מלא מים כיון דכי חסרה אסור משום דהוי תשמישו לזה בשלשול ולזה בזריקה כי מליא נמי אסור ». Le Magen Avraham : « אבל מלא מים אסור שמא ימלא ממנה ותחסר מי' (רמב״ם) ».
   - Rachi, que recopie le BY, dit pourquoi la michna ne parle pas de la hauteur sous la galerie : « דהא סתם מרפסת לאו גביהא טובא ». Le Rambam motive par « שֶׁהֲרֵי הֵן שָׁוִין לָהּ » (4:16).
   - **Pièces à verser au doute 42.** Le Taz ne dit nulle part comment il concilie sa lecture avec ces passages.
   - **Même tension au cas 3.** Le Taz écrit, pour le Rambam, le tertre de moins de dix, plus bas de dix que la galerie : interdit aux deux (« ולהרמב״ם אינו כן »). Sa cellule le rapporte, puisque c'est sa thèse écrite. Mais le Rambam (4:17, « כָּל שֶׁהוּא לְמַטָּה מֵעֲשָׂרָה טְפָחִים הֲרֵי זֶה נֶחְשָׁב מִן הֶחָצֵר ») et le Mehaber (375:ד) donnent à la cour la saillie dans la position analogue. Le Taz ne dit pas comment il les concilie. Une page qui donne « le Taz, selon le Rambam, même plus bas de dix que la galerie » doit le donner comme la lecture du Taz, et dire que le Rambam et le Mehaber donnent à la cour la saillie dans la même position.
   - **À aligner, hors de cet arbitrage.** La phrase qui donne ce tertre à la galerie « selon la règle que le Taz tire des mots du Rambam » est en ligne : N3 l.379 (arbre Q4) et l.401 (tableau de la section 5), N4 l.468 (point ב, « ce tertre est à la galerie »), et leurs équivalents HE et EN. Le N2 l.582 se borne à traduire le Taz (« le Rambam ne parle pas du tertre plus bas que la galerie de dix ») et ne conclut pas. Ces phrases sont à retirer, ou à remplacer par le constat de source ci-dessus, puis les portes à repasser.
2. **Tour, cas 8 (`H>=10 G>=10 E>=4`) : non écrit.** La clause « או שהוא גבוה י' לבני החצר ורחוק ד' מן המרפסת … שניהם אסורין » ne fixe pas G, et les deux voix qui la lisent n'y mettent pas ce cas :
   - le séif lui prête la condition « (מן החצר לתוך עשרה למרפסת) (טור) » ;
   - le Taz, dans la shita du Tour, tranche ce cas par son propre « נ״ל » (à la cour), ce qu'il n'aurait pas à faire si le Tour l'écrivait.

   Lue sans condition, la clause l'interdirait. La règle finale du Tour, « אבל כל שתשמישו בנחת יותר מלחבירו נותנין אותו למי שהוא בנחת », ne le tranche pas. En face, la guemara selon Rachi, que recopie le BY, écrit ce cas : interdit aux deux, même selon Chmouel (« ונהי דלשמואל שלשול לגבי זריקת גובה נוח היא הכא דאיכא שלשול וזריקת משך שוים הם לזריקת גובה ואמאי לחצר »). Cette pièce s'oppose directement au « נ״ל » du Taz et au SAH, qui donnent le tertre à la cour. La MB ס״ק י״א rapporte les deux avis sans les nommer.
3. **Tour, « ואם אינו גבוה י' לבני החצר וממנו למרפסת ארבעה ».** C'est le texte imprimé, et il se lit de deux façons :
   - le Taz corrige : « צ״ל יו״ד במקום דל״ת וכן הגיה מו״ח ז״ל » ;
   - le BY garde « ארבעה » et lit « מתרי טעמי דרחוק ממנו י' ומופלג ממנו ד' או אפילו … מיפלג ממנו ד' ».

   Les deux lectures couvrent le cas 4, qui est donc explicite chez le Tour. Seule la correction du Taz couvre le cas 3 par la clause elle-même. Sans elle, le cas 3 relève de la règle finale du Tour, d'où le mode « règle générale » au cas 3.
4. **Séif imprimé, cas 7 et 8.** Chacune des deux parenthèses retire de sa clause le tertre plus bas de dix que la galerie :
   - la première, de la permission à la galerie ;
   - la seconde, de l'interdit aux deux.

   Le séif imprimé ne porte donc pas d'issue pour ces cas, et la cellule est « non écrit ». Ce sont la MB (ס״ק ח, ס״ק י״א) et le SAH qui les comblent. Le séif ד du même siman écrit le cas analogue du cas 7, la saillie entre les deux dizaines : interdit aux deux.
5. **Auteur des parenthèses.** Le Taz attribue la première au Rama (« ורמ״א הכניס לתוך דברי הרמב״ם מן שיטת הטור דהיינו ובתוך י' למרפסת »). Il parle de « זולת הגהות רמ״א » au pluriel, mais il ne nomme pas l'auteur de la seconde, qu'il commente pourtant comme du texte du séif (« ומ״ש כאן … מן החצר לתוך י' למרפסת »).
   - Maginei Eretz ouvre une parenthèse sans la refermer : « (ובתוך עשרה למרפסת (טור) ».
   - Torat Emet 363 imprime les deux additions en `<small>`.
   - « להם » se lit dans la phrase du Tour.

   Doutes 1, 13, 37 et 38 : la source ne les tranche pas.
6. **Beit Yossef, cas 3 et 4 (`H<10 G>=10`).** Dans sa lecture du Rambam, le BY ne nomme jamais la hauteur sous la galerie.
   - Sa règle « והלכך כל היכא דאפשר לבני חצר להשתמש עליהם שניהם אסורין ולא משכחת לה צד היתר אלא בגבוהים י' ואינם מופלגים ד' דהשתא הוי לבני מרפסת בנחת ולבני חצר בזריקה ונותנין אותה לזה שבנחת » est tirée de l'écart (« מהטעם שכתבתי דבכה״ג בני מרפסת יכול להשתמש בהם ע״י זריקה »).
   - Pour Rav, il écrit « לרב שניהם אסורים עד שיהא לזה בנחת לגמרי דומיא דפתח ולזה בקשה וגם זה סעד לדברי הרמב״ם ».
   - Il ajoute que le Rambam écrit la saillie « ביני וביני », et la saillie au-dessous de dix est à la cour (Rambam 4:17, SA 375:ד).

   **Cas 3 : non écrit.** La cour y est בנחת et la galerie descend de dix : sa seconde règle et la saillie donneraient la cour, sa première l'interdit. Aucune page ne doit présenter « interdit selon le BY » pour ce cas.

   **Cas 4 : interdit (r).** Il relève de « כל שמופלגין … בין גבוהין י' בין אינם גבוהין י' שניהם אסורין » par le silence sur G. Sa règle pour Rav ne le tranche pas, puisqu'il interdit déjà le cas 2, où la cour est aussi בנחת. Une page ne le donne que comme sa lecture, non comme son écrit.
7. **Taz (shita du Tour), cas 1 et 2.** Le כלל du Taz donne le cas 2 à la cour (« ועוד קרוי קשה … מופלג … ד״ט »). Mais sa phrase sur la glose que la רישא aurait demandée, « גם נמוכים ממרפסת פחות מי' דאז דוקא שוה לשניהם », ne nomme pas E. Lue seule, elle rangerait aussi le cas 2 dans le « שוה ». Le Tour, lui, est explicite pour la cour (« או אם הוא תוך י' לשניהן ורחוק מן המרפסת ד' »).
8. **Séif imprimé, cas 2 à 4 : deux lectures écrites.** La première phrase, « אם אינם גבוהים י״ט … ושניהם אסורים », ne porte aucune condition.
   - Le Taz la lit sans distinction (cas 2 à 4), ce qui donne l'interdit. Le BY (sur le Rambam) la lit sans distinguer l'écart (cas 2 et 4) ; il ne nomme jamais la hauteur sous la galerie (cas 3 : non écrit ; cas 4 : I (r), point 6).
   - La MB (ס״ק ו, ז) la limite au cas 1 et donne ces cas à la cour.
   - Le Magen Avraham (« וגם למרפסת אין גבוהים י' ») la limite au tertre à moins de dix sous la galerie : il donne à la cour, avec le Tour et les posekim, le tertre plus bas de dix (cas 3 et 4) ; pour l'écart (cas 2), il rapporte le BY puis le Tour et les posekim, et ne tranche pas.
   - [Corrigé à la vérification stricte, passe 1 : ce point rangeait le MA avec la MB pour les cas 2 à 4 et le BY avec le Taz pour le cas 3, contre les cellules MA cas 2 (« 2 ») et BY cas 3 (« · ») de cette même matrice.]

   L'issue « I (r) » est celle du texte lu à la lettre. Ce n'est pas « l'issue du séif » : une page qui la donne nomme la lecture.
9. **Cadre, valable pour les huit cas, hors matrice.**
   - La MB ס״ק ד et le BY exigent que le tertre soit commun : s'il est à l'un seul, il n'interdit pas.
   - Le Biour Halakha exige qu'il soit large : « מיירי שהוא רחב דע״ד דאל״ה הוי מקום פטור ובטל להכא ולהכא ».
   - Le SAH ajoute « וּשְׁנֵיהֶם מִשְׁתַּמְּשִׁים בּוֹ בְּחֹל » et pose le cadre « אִם עֵרְבוּ בְּנֵי הַמִּרְפֶּסֶת לְעַצְמָן ».
   - La matseva devant la galerie lève tout : SA 375:ג, et SAH 375:4, « אֲפִלּוּ תֵּל וְעַמּוּד הַסְּמוּכָה לָהּ ».

   C'est une quatrième variable, que la matrice ne traite pas.
10. **Conduite.** Pour les cas 2, 3, 4 et 8, des voix de la matrice s'opposent, et aucune ne tranche entre les autres. Au cas 7, aucune voix ne s'oppose : toutes celles qui en portent une issue interdisent aux deux (Taz, Tour, BY, MB, SAH, MA ; séif ד en règle générale) ; le séif imprimé et le Rambam selon le Taz n'en écrivent pas l'issue ; la guemara rapporte aussi Chmouel (à la galerie), que le BY écarte (« וידוע דהלכה כרב באיסורי ») et que le Taz écarte (« והכי קי״ל »). Une page range donc le cas 7 avec les cas d'accord, en nommant Chmouel et sa mise à l'écart. [Corrigé à la vérification stricte, passe 1 : ce point rangeait le cas 7 parmi les cas où « aucune ne tranche », puis se contredisait à la phrase suivante.] Une page qui donne une conduite pour ces cas la donne sous le nom d'une voix : SAH, MB ou BY. Elle ne la donne jamais comme « le séif ». Doutes 20, 26 et 27.

## Objections arbitrées

1. **[bloquant] Cas 7, Rambam selon le Taz « à la galerie (r) » — FONDÉE.** Pièces nouvelles (grep « זיז », « ביני », « גביהא » dans decisions-375 et doutes-375 : 0) : Rambam 4:17-18, SA 375:4, BY « ביני וביני » et « הרמב״ם בפ״ד », Rachi « סתם מרפסת לאו גביהא טובא ». La règle du Taz lui-même (« וכן אם לשניהם ריעותא ») tire contre la galerie. Cellule mise à non écrit ; point 1 réécrit ; pièces pour le doute 42 ; pages à aligner (N3 l.379 et 401, N4 l.468, trois langues), non touchées ici.
2. **[à corriger] Cas 2, BY, segment coupé sur « או מופלגים » — FONDÉE.** Dans la source, « או מופלגים » ouvre « אע״ג שגבוהים י' » (BY : « … סמוכים או מופלגים אע״ג שגבוהים י' הוי אף לחצר ושניהם אסורים »). Second segment retiré ; la cellule cite « ולא חילק בין אם מופלגים ארבעה לאם אינם מופלגין משמע נמי … ג״כ ». L'issue est inchangée.
3. **[à corriger] Cas 4, Tour, mode — FONDÉE.** Les deux lectures écrites (י׳ du Taz, « מתרי טעמי » du BY) couvrent ce cas : explicite, dans la cellule et dans la vue d'ensemble.
4. **[à corriger] Cas 8, BY sous-évalué ; guemara selon Rachi — FONDÉE EN PARTIE.**
   - BY au cas 8 : explicite, par le Rachi qu'il recopie (« דלשניהם תשמישו בקשה … ואמאי לחצר »).
   - Voix « guemara selon Rachi » ajoutée : cas 8, interdit aux deux, explicite (« אילימא לחצר ושרי אמאי רשותא דתרווייהו הוא … אף לחצר ושניהם אסורין »).
   - Au cas 7, NON « interdit » : Rachi y explique la lecture de Chmouel (« וקתני דבני עלייה מותרין בו »), et la guemara rapporte Rav et Chmouel. Issue « deux avis rapportés », avec la décision du BY dans la référence.
   - Point 2 : la pièce s'oppose au « נ״ל » du Taz et au SAH.
5. **[mineur] Modes inégaux pour une même clause — FONDÉE.** Au cas 4, le Taz (shita du Tour), la MB et le MA passent en explicite ; au cas 7, le BY et le MA aussi (le MA avec son « וצ״ע » dans la référence).
6. **[mineur] Séif imprimé, cas 2 à 4, deux lectures — FONDÉE EN PARTIE.** L'issue « I (r) » est gardée : c'est le texte lu à la lettre, et le BY et le Taz le lisent ainsi. Les références de ces trois cellules disent les deux lectures. La légende de (r) et le point 8 disent qu'une issue (r) n'est pas « l'issue du séif ».
7. **[mineur] Cas 5, Magen Avraham « n'en parle pas » — FONDÉE.** Sa ligne sur la citerne renvoie au tertre (« ומחשב למרפסת כמש״ל ») : à la galerie, règle générale, par renvoi, sans G nommé. Le renvoi n'est pas étendu au cas 7, où le MA écrit l'interdit.
8. **[bloquant] Cas 7, Rambam selon le Taz (doublon de 1) — FONDÉE.** Même correction. S'y ajoute que la référence du séif imprimé, au cas 7, note la saillie du séif ד : interdit aux deux. La contradiction de méthode est corrigée : le BY n'était pas étendu à G>=10, le Taz l'était.
9. **[à corriger] Voix manquante, SA 375:ד = Rambam 4:17 — FONDÉE.** Voix ajoutée : cas 3 à la cour, cas 5 à la galerie, cas 7 interdit aux deux, partout en règle générale et non en explicite (règle écrite pour la saillie ; lien posé par le BY, « נלמד »). Les autres cas sont non écrits. La tension avec le Taz au cas 3 est notée dans sa référence et au point 1.
10. **[à corriger] Cas 3, BY « interdit (r) » — FONDÉE.** Ses deux règles tirent en sens contraires, et la saillie (« ביני וביני », Rambam) va vers la cour. Cellule mise à non écrit, avec la citation prolongée jusqu'à « ונותנין אותה לזה שבנחת » dans la référence ; point 6 réécrit. Le cas 4 reste « interdit (r) », avec la limite dite.
11. **[mineur] Cas 8, guemara selon Rachi et Tour — FONDÉE.** La voix est ajoutée (voir 4). Le Tour au cas 8 passe en non écrit : les deux voix qui lisent sa clause (la parenthèse du séif, et le Taz qui tranche par son propre נ״ל) n'y mettent pas ce cas. Point 2 réécrit.
12. **[mineur] Cas 2, BY, coupe (doublon de 2) — FONDÉE.** Même correction.
13. **[mineur] Modes du Tour et du MA au cas 4, et du MA au cas 7 — FONDÉE.** Le MA au cas 4 est une disjonction dont le cas remplit les deux branches. Le Tour au cas 4 relève des deux lectures. « לא' בשלשול ולא' בזריקה » désigne le cas 7 chez le MA comme chez le Taz. Les trois cellules passent en explicite. Le critère précise désormais le cas de la disjonction.
14. **[mineur] Magen Avraham, cas 2 et 5 — FONDÉE EN PARTIE.**
   - Cas 5 : voir 7.
   - Cas 2 : l'issue « deux avis rapportés » est gardée. « ואפשר שגם דעת הרמב״ם כן » est un « peut-être » ; « le MA penche » serait notre lecture. La référence cite la phrase et dit qu'il ne tranche pas.

## Vérification stricte, passe 1 (23 octobre 2026) — corrections de la matrice

Sauvegarde d'avant : `oh366/memoire-e3/bak-375-tertre-v1/matrice-tertre-375.md`. Sources rouvertes par `sefaria-extrait.py` : MA 375 (segment unique), MB 375 ס״ק ה-ח, י״א, BY 375 (« משמע דכל שמופלגין … שניהם אסורין », code 0).

1. **Point 8 et références du séif imprimé aux cas 2 et 4 — la matrice était fausse.** Le Magen Avraham ne limite la première phrase que par la hauteur sous la galerie (« וגם למרפסת אין גבוהים י' ») ; sur l'écart, il rapporte « וכתב הב״י דאף ע״פ שרחוק ד' … שניהם אסורים » puis « אבל בטור ובפוסקים משמע … אם הוא רחוק ד' מן המרפסת או נמוך ממנו י' », et « ואפשר שגם דעת הרמב״ם כן » : il ne tranche pas (sa propre cellule au cas 2 : « 2 »). Le Beit Yossef ne distingue que sur l'écart (« ולא חילק בין אם מופלגים ארבעה לאם אינם מופלגין ») et ne nomme jamais la hauteur sous la galerie (sa propre cellule au cas 3 : « · »). Point 8, arbitrage 1 et références des cas 2 et 4 réécrits ; aucune cellule ne change.
2. **Point 10, cas 7 — la matrice était fausse.** Aucune voix de la ligne du cas 7 ne porte d'autre issue que l'interdit (Taz, Tour, BY, MB, SAH, MA explicites ; séif ד en règle générale) ; le séif imprimé et le Rambam selon le Taz sont « non écrit », ce qui n'est pas une opposition ; Chmouel, rapporté par la guemara, est écarté par le BY (« וידוע דהלכה כרב באיסורי וכן פסק הרא״ש שם והרמב״ם בפ״ד מה״ע ») et par le Taz (« ושלשול וזריקה שוין הם ואסור והכי קי״ל »). Le cas 7 sort de la liste des cas où « aucune ne tranche » ; les pages le rangent avec les cas d'accord en nommant Chmouel et sa mise à l'écart.

## Vérification stricte du nœud, passe 4 (23 octobre 2026) — correction de la matrice

Sauvegarde d'avant : `oh366/memoire-e3/bak-375-tertre-v4/matrice-tertre-375.md`. Sources rouvertes par `sefaria-extrait.py` : Érouvin 84a (guemara) et Rachi sur Érouvin 84a, en entier (`noeud375-v4/rashi84a.txt`) ; chaque fragment cité ci-dessus, code 0.

1. **Voix « guemara selon Rachi », cas 1, 2, 5 et 6 — la matrice était fausse dans sa référence.** Elle disait « hors de ce passage : Rachi n'y explique que le tertre sous les chambres hautes ». Or Rachi, sur la même page, explique aussi la lecture où la guemara conclut : « הדרין במרפסת - כגון שיש בה דיורין דלדידהו הוי האי תל שבחצר שוה להן בתוך עשרה » ; « לזה בפתח ולזה בפתח הוא - ותרוייהו בעי איתסורי ביה דהא סתם מרפסת לא גביהה טובא » ; « אלא - על כרחך אף לחצר ואסורין לרב נמי דמתרץ לה בדיורי מרפסת ». Dans cette lecture, la guemara écrit le cas 1 (interdit aux deux), le cas 5 (à la galerie, « בִּסְמוּכָה ») et le cas 6 (interdit aux deux, « בְּמוּפְלֶגֶת אֲפִילּוּ גָּבוֹהַּ עֲשָׂרָה … אַף לֶחָצֵר, וּשְׁנֵיהֶן אֲסוּרִין »). Le cadre בני עלייה, lui, suppose les chambres hautes bien plus hautes que le tertre (« דגביהי ממרפסת טובא ») : les quatre cas où le tertre est à moins de dix sous la galerie (1, 2, 5, 6) n'y entrent pas. Cellules passées de « non écrit » à « hors de ce cadre », avec, dans la référence, ce qu'écrit la lecture où la guemara conclut ; le cas 2 reste sans issue écrite (la phrase « פחות מכאן … אף לחצר ושניהן אסורין » ne distingue pas l'écart). Les cas 3 et 4, où le tertre est plus bas de dix que la galerie, sont dans le cadre, et Rachi n'en écrit pas l'issue : « non écrit » maintenu (l'objection proposait « hors de ce cadre » pour les cas 1 à 6 : non retenu pour 3 et 4). Aucune issue d'accord ne change : la guemara rejoint toutes les voix aux cas 1, 5 et 6.

## Vérification stricte du nœud, passe 5 (23 octobre 2026) — correction de la matrice

Sauvegarde d'avant : `oh366/memoire-e3/bak-375-tertre-v5/matrice-tertre-375.md`. Sources rouvertes par `sefaria-extrait.py` : Beit Yossef 375 en entier (`noeud375-v4/by375-p5.txt`) ; Érouvin 84a, guemara, en entier (`noeud375-v4/eruvin84a-p5.txt`) ; Rachi sur Érouvin 84a (`noeud375-v4/rashi84a.txt`). Chaque fragment cité ci-dessous, code 0.

1. **Voix « guemara selon Rachi », cas 2 — la matrice était fausse dans sa référence.** Elle disait que, dans la lecture où la guemara conclut, la phrase sur le tertre de moins de dix « ne distingue pas l'écart » et que la guemara « n'écrit pas ce cas en tant que tel ». Or la guemara elle-même prouve sa conclusion par la clause du tertre écarté (« הָכִי נָמֵי מִסְתַּבְּרָא, מִדְּקָתָנֵי סֵיפָא: בַּמֶּה דְּבָרִים אֲמוּרִים בִּסְמוּכָה. אֲבָל בְּמוּפְלֶגֶת, אֲפִילּוּ גָּבוֹהַּ עֲשָׂרָה טְפָחִים — לֶחָצֵר … אֶלָּא מַאי ״לֶחָצֵר״ — אַף לֶחָצֵר, וּשְׁנֵיהֶן אֲסוּרִין »), et le Beit Yossef lit dans cette clause, par son « אפילו », le tertre de moins de dix écarté, interdit aux deux, « בהדיא » : « ופשטא דמתני' כוותיה מוכחא דקתני בד״א בסמוכה אבל במופלגת אפילו גבוה י' טפחים לחצר ומשמע דה״ק בד״א דגבוה י' טפחים למרפסת בסמוכה אבל במופלגת בין גבוה י' טפחים בין פחות מי' לחצר כלומר אף לחצר כדמוקי בגמרא הרי בהדיא לא משכחת לה צד היתרא אלא בשני תנאים ». Il écrit aussi la lecture contraire, qu'il prête au Tour en disant qu'elle force le texte : « ולדעת רבינו צריך לדחוק … לצדדין קתני דבגבוה מי' הוי אף לחצר ושניהם אסורים ובפחות מי' הוי דוקא לחצר ושרי ». La référence de la cellule dit désormais les deux lectures (critère de la matrice : séif imprimé, cas 2, « deux lectures écrites »). La cellule reste « h » dans la vue d'ensemble (le cadre בני עלייה ne contient pas ce cas) ; aucune issue d'une autre voix ne change.
2. **Beit Yossef, cas 2 — référence précisée.** « lecture du Rambam » seule rabaissait le degré : le BY la dit prouvée par le sens simple de la michna. L'issue (interdit aux deux, explicite) ne change pas. Le cas 4 reste « interdit (r) » : la phrase « בין גבוה י' טפחים בין פחות מי' » ne nomme pas non plus la hauteur sous la galerie.

