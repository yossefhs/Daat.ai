
## Verification allegee, passe 1

- Obj. 1 (a_corriger, N4 FR/EN, encadre « Aucune reference verifiee » tombe dans un commentaire HTML) : FONDEE — commentaire « <!-- 3. DIVREI HAREBBE --> » retabli avant la <section>, encadre remis visible apres le section-divider (forme du siman 385), FR et EN ; HE deja juste.
- Obj. 2 (a_corriger, N4 FR/EN, jeton « REBBE » affiche) : FONDEE, meme defaut que l'obj. 1 — ligne « REBBE » supprimee FR et EN par la meme correction ; parite avec la page HE retablie.
- Obj. 3 (a_corriger, N2 recapitulatif, Rachi garant de la condition pour la vallee) : FONDEE — Rachi Erouvin 67b (« אם היה לו פתח לקרפף בית סאתים… אבל אם יותר מבית סאתים נפיש אוירא ») ne parle que du karpef ; parenthese restreinte : FR « (séif א ; pour l'enclos, Rachi) », HE « (סעיף א; לענין קרפף, רש״י) », EN « (seif א; for the enclosure, Rashi) ». Aucune autre page du siman n'attribue la vallee a Rachi.
- Portes : verifier-citations.py (fr,he,en) 267/267 conformes, 0 grave ; verifier-troncatures.py 0 trou, 0 coupure.

## Vérification allégée, passe 2

- Objection 1 (a_corriger, enclos entouré pour l'habitation, voix d'un seul côté) — FONDÉE. Eliyah_Rabbah OC 389 ס״ק ד : « ואם כן נראה לי אפשר דמודה דאוסר כשאין אלא בית סאתים או פחות … וכן נראה לי דינא דעל כל פנים יש לסמוך בזה על יש מי שאומר » ; ס״ק ה : « ונקטינן כסברא ראשונה (בית יוסף) ». La page alignait MB ו, BY, BH d'un seul côté.
- N1 (FR/HE/EN), encadré, dernier point : la phrase MB/BY/BH est remplacée par la forme courte « Les commentateurs en discutent la portée : voir le niveau 2 (section 5). Consulte ton Rav. »
- N1 (FR/HE/EN), section 3, notion הוקף לדירה : citations MB ו, BY, BH retirées ; renvoi « chacun est cité par son texte au niveau 2 (section 5) ». Le bloc source « Michna Beroura (ו) » (recopie des entrées) est gardé.
- N3 (FR/HE/EN), section 5 : lignes Beit Yossef, Michna Beroura ו, Biour Halakha retirées du tableau ; une ligne « Les commentateurs — ils divergent sur la portée de cet avis : niveau 2, section 5 » ; résumé ajusté. Lignes Tour et SAH gardées.
- N4 (FR/HE/EN), point ג, « Chez les commentateurs » : la seule Michna Beroura (« הוא דעת התוספות לבד ») remplacée par « ils divergent sur la portée de cet avis : voir le niveau 2 (section 5) » — même cas disputé, corrigé partout où il paraît.
- N2 (FR/HE/EN), section 5 : ajout de l'Eliya Rabba par son texte (ס״ק ד, quatre segments extraits par sefaria-extrait.py, coupure « ומזה קשה נמי על תוס׳… » marquée « … » ; ס״ק ה), entre le Biour Halakha et le SAH.
- Objection 2 (a_corriger, récapitulatif du N2, « dans ce cas » rattaché à « plus de deux séa ») — FONDÉE (MB ס״ק ד porte sur « קטן הוא ולא ניחא », le cas de deux séa seulement). Corrigé dans les trois langues : « quand il n'y a que deux séa, la Michna Beroura (ס״ק ד) écrit que même une grande porte… » / « וכשאין בו אלא סאתים, המשנה ברורה (ס״ק ד) כותב שאפילו פתח גדול… » / « when it has only two se'ah, the Mishnah Berurah (ס״ק ד) writes that even a large door… ».
- Portes : verifier-citations.py --path sources/shabbat/siman-389 --langues fr,he,en → 261 citations, 261 conformes, 0 sans référence, 0 anomalie. verifier-troncatures.py → 0 trou, 0 coupure.
- Doutes devenus sans objet : ceux qui visaient la phrase BY « והכי נקטינן » au N1 section 3 / encadré et dans la ligne BY du tableau N3 (texte retiré de ces endroits) ; ils restent valables pour le N2, section 5.

## Après la passe 3 (coordinateur, 5 novembre 2026) — trois langues
- CORRIGÉ — la limite « אֲבָל כֵּלִים שֶׁשָּׁבְתוּ בַּבַּיִת — אָסוּר לְהוֹצִיאָם לְתוֹכוֹ » (שו״ע הרב שפ״ט:א) n'est plus rattachée au karpef entouré pour l'habitation : RETIRÉE de la ligne « Choulhan Aroukh HaRav » du tableau de la section 5 et du cas pratique 3 du N3 ; piège 4 du N3 : « Après la phrase entre crochets sur l'enclos de deux séa non entouré, le Choulhan Aroukh HaRav écrit… », puis « À quel enclos s'applique cette limite, la page ne le tranche pas : consulte ton Rav » ; commandement 4 : renvoi au piège 4 ; N4 point ב « Conséquence pratique » (« le Rav écrit ensuite… à quel karpef s'appliquent cette raison et cette limite, la page ne le tranche pas ») et section 4 point ② (« le séif écrit ensuite… à quel karpef, la page ne le tranche pas »). Les simanim 358 et 372 du Rav et le Magen Avraham ס״ק א posent la limite pour le karpef non entouré, et pour le karpef entouré d'un autre.
- DOUTE (au Rav) : la limite sur les objets de la maison vise-t-elle le seul beit sa'tayim non entouré (phrase entre crochets), ou aussi le karpef entouré pour l'habitation qui appartient au Juif lui-même ?
