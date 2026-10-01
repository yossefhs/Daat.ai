# Orah Haïm — les 16 verdicts INTROUVABLE, ouverts un par un

Lot : les lignes de `audit/citations-sources-orah-haim.csv` dont le verdict vaut exactement
`INTROUVABLE`. **Compte vérifié : 16** — conforme au mandat.

Méthode : aucun lancement de `verifier-citations.py` (cache partagé). Chaque référence a été
interrogée **en direct par curl** sur `https://www.sefaria.org/api/texts/…`, et chaque phrase
cherchée *dans le segment servi* (squelettes consonantiques, nikoud et ponctuation neutralisés)
avant tout recours à l'index plein-texte `api/search-wrapper`. Aucun fichier de `sources/` n'a
été modifié.

## Verdict d'ensemble

| Famille | Verdicts |
|---|---|
| 1. FABRICATION RÉELLE | **7** |
| 2. CITATION RÉELLE MAL ADRESSÉE | **5** |
| 3. FAUX POSITIF DE LA PORTE | **4** |
| 4. HORS CONVENTION | **0** |
| Non tranchés | **0** |

**Les 16 sont tranchés.** Aucun n'est une condensation : les quatorze premiers portent des
guillemets français `«…»` ou droits, aucun n'est introduit par `<em>résumé</em>` / `תמצית`.
La famille 4 est donc vide — ce qui est en soi une information : sur ce verdict-là, l'exemption
de condensation n'absout personne.

**Signature commune aux 16.** Toutes citent le **Talmud** (plus un dibour hamathil de Tossafot),
jamais le Choul'han Aroukh ni la Michna Beroura ; **15 sur 16 vivent dans `niveau-2-lamdan`**, une
dans `niveau-3-synthese`. Le lieu est toujours le même : une ligne `הבסיס התלמודי`, un titre de
section, ou l'en-tête d'un `rishon-card`. C'est une habitude de rédaction — on **étiquette** une
sougya par un mot d'ordre mnémonique, puis on l'habille de guillemets.

## ⚠️ L'étendue réelle est 8 fois le relevé

Les 16 verdicts ne sont que les occurrences que la porte a vues. Les **9 phrases distinctes**
réellement fautives (7 fabrications + 5 mal adressées = 12 verdicts) sont présentes
**134 fois dans 35 fichiers**, les trois langues comprises, et **25 de ces occurrences sont dans
`<meta name="description">`, `og:description` ou le JSON-LD** — invisibles à la lecture, lues par
Google et par les aperçus de partage.

| Phrase | occurrences | fichiers | dont meta/JSON-LD | lignes au CSV |
|---|---:|---:|---:|---:|
| `הא קא מתהני ממאור` | 57 | 6 | 15 | 1 |
| `חל עליו שם בית הכסא` | 27 | 3 | 9 | 2 |
| `מודים רבנן מאי אמרי` | 12 | 6 | 0 | 3 |
| `כל המינים מדאורייתא` | 11 | 5 | 1 | 1 |
| `עקבו רואה מותר` | 9 | 3 | 0 | 1 |
| `כמה חוטין ניתקין` | 6 | 3 | 0 | 1 |
| `בגובה שביד` | 6 | 3 | 0 | 1 |
| `בעשרה בני ישראל` | 3 | 3 | 0 | 1 |
| `המזלזל... בא לידי עניות` | 3 | 3 | 0 | 1 |

C'est exactement la leçon inscrite au CLAUDE.md : *un correctif appliqué à la main sur les cas
qu'on a vus n'est pas un correctif.* Corriger les 12 lignes du CSV laisserait 122 occurrences en
ligne. **Et la porte ne lit pas les `<meta>` : 25 occurrences d'un verbatim fabriqué ne sont
confrontées à rien, dont les 15 de `הא קא מתהני ממאור` au siman 69.**

---

# Famille 1 — FABRICATION RÉELLE (7 verdicts, 5 phrases)

## F1.1 · siman 127, trois verdicts — `מודים רבנן מאי אמרי`

- `sources/orah-haim/siman-127/niveau-2-lamdan.html` **L469** et **L577**
- `sources/orah-haim/siman-127/niveau-3-synthese.html` **L474**
- Revendique : `סוטה מ׳.` (Sotah 40a)

**Ce que Sefaria sert à Sotah 40a:11** (William Davidson, vocalisé) :

> בִּזְמַן שֶׁשְּׁלִיחַ צִבּוּר אוֹמֵר מוֹדִים, הָעָם מָה הֵם אוֹמְרִים? אָמַר רַב: ״מוֹדִים אֲנַחְנוּ לָךְ ה׳ אֱלֹהֵינוּ עַל שֶׁאָנוּ מוֹדִים לָךְ״. וּשְׁמוּאֵל אָמַר: ״אֱלֹהֵי כׇּל בָּשָׂר…״ רַבִּי סִימַאי אוֹמֵר: ״יוֹצְרֵנוּ יוֹצֵר בְּרֵאשִׁית…״ נְהַרְדָּעֵי אָמְרִי מִשְּׁמֵיהּ דְּרַבִּי סִימַאי: ״בְּרָכוֹת וְהוֹדָאוֹת לְשִׁמְךָ הַגָּדוֹל עַל שֶׁהֶחֱיִיתָנוּ וְקִיַּימְתָּנוּ…״

**Preuve d'absence.** Recherche exacte sur `מודים רבנן מאי אמרי` → **0 résultat**.
Variantes essayées, toutes à 0 : `מודים דרבנן מאי אמרי`, `מודים רבנן מאי`, `מודים מאי אמרי`.
`מודים רבנן` seul existe (Rachi Chabbat 123a, Bartenoura Bekhorot 6:9, Mahatsit haChékel OH 318…)
mais **jamais à Sotah 40a** et jamais suivi de `מאי אמרי`. La formule interrogative réelle est
`העם מה הם אומרים?` — qui, elle, sort bien à Sotah 40a:11.

**Ce qui tient quand même.** Le sens est fidèle et le reste du bloc est exact : les cinq noussa'ot
d'amoraïm sont bien ceux du texte, et `הלכך נימרינהו לכולהו` est **verbatim** à Sotah 40a:12
(`אָמַר רַב פָּפָּא: הִילְכָּךְ נֵימְרִינְהוּ לְכוּלְּהוּ`). Le raisonnement de la page survit
intégralement : seule l'étiquette entre guillemets est à remplacer par la vraie question du
Talmud. Étendue : **12 occurrences, 6 fichiers** (`niveau-2` L469/L577/L737 et `niveau-3`, ×3 langues).

## F1.2 · siman 12 — `כמה חוטין ניתקין`

- `sources/orah-haim/siman-12/niveau-2-lamdan.html` **L520** (+ L802)
- Revendique : `מנחות (ל״ח:–ל״ט.)`

**Preuve d'absence.** Recherche exacte : `כמה חוטין ניתקין` → 0 ; `חוטין ניתקין` → **0**.
Absent aussi des segments servis à Menachot 38b (14 segments) et 39a (12 segments) : meilleur
ratio 0,50.

**Ce que la source dit à la place** — c'est la même sougya, avec d'autres mots :

- Menachot 38b:10 — `וְכַמָּה שִׁיעוּר גַּרְדּוּמִּין? אָמַר בַּר הַמְדּוּרֵי אָמַר שְׁמוּאֵל: כְּדֵי לְעׇנְבָן`
- Menachot 38b:11 — `אִיבַּעְיָא לְהוּ: כְּדֵי לְעׇנְבָן – לְעׇנְבָן כּוּלְּהוּ בַּהֲדָדֵי, אוֹ דִלְמָא כֹּל חַד וְחַד לְחוֹדֵיהּ? תֵּיקוּ`
- Menachot 39a:3 — `אִם נִפְסַק הַחוּט מֵעִיקָּרוֹ – פְּסוּלָה … אֲבָל סוֹפוֹ – שְׁיָרָיו וְגַרְדּוּמָּיו כׇּל שֶׁהוּא`

Le second terme de la même phrase, `כדי עניבה`, est en revanche **verbatim** — mais au
**Choul'han Aroukh OH 12:1-3** (`ונשתייר בהם כדי עניבת כל החוטים הפסוקים`, `ואם לא נשאר כדי עניבה`),
non au Talmud, qui dit `כדי לענבן`. La page attribue les deux au Talmud.

## F1.3 · siman 55 — `בעשרה בני ישראל`

- `sources/orah-haim/siman-55/niveau-2-lamdan.html` **L542**
- Revendique : `ובסנהדרין (ע״ד:) … לענין קידוש השם`

**Preuve d'absence.** Recherche exacte `בעשרה בני ישראל` → **0 résultat**.

**Ce que Sanhedrin 74b sert réellement** :

- 74b:2 — `וכמה פרהסיא? אמר רבי יעקב אמר רבי יוחנן: אין פרהסיא פחותה מֵעשרה בני אדם. פשיטא, ישראלים בעינן, דכתיב: ״ונקדשתי בתוך בני ישראל״`
- 74b:3 — `מה להלן עשרה וכולהו ישראל, אף כאן עשרה וכולהו ישראל`

La phrase de la page **fusionne** `עשרה` avec les mots du verset `בני ישראל`. Les formes réelles
disponibles pour dire la même chose, verbatim : `מעשרה בני אדם` et `עשרה וכולהו ישראל`
(Sanhedrin 74b), `בעשרה מישראל` (Rambam, Yessodei haTorah **5:2** et **5:4** — vérifié),
`כל עשרה מישראל` (Rambam, Tefila 8:5). Le contenu halakhique de la page est juste et abondamment
sourcé ; c'est le mot d'ordre entre guillemets qui n'existe pas.

## F1.4 · siman 69 — `הא קא מתהני ממאור`

- `sources/orah-haim/siman-69/niveau-2-lamdan.html` **L678**
- Revendique : `(מגילה כ״ד.)`

**Preuve d'absence.** `הא קא מתהני` existe (Ritva Erouvin 31a, Ritva Nedarim 31a, Nimoukei Yossef
Nedarim 15a, Maharcham I 62) — **nulle part à Meguila**, et jamais suivi de `ממאור` ;
`מתהני מנהורא` → 0. Ni `מתהני` ni `מאור` dans aucun segment de Meguila 24b ; Meguila 24a ne porte
que la michna (24a:13).

**Ce que la source dit à la place — et elle est sur l'autre face du folio, Meguila 24b** :

- 24b:5 — `וְרַבִּי יְהוּדָה, הָתָם בְּאֹבַנְתָּא דְלִיבָּא תַּלְיָא מִילְּתָא… הָכָא מִשּׁוּם הֲנָאָה הוּא, וְהָא לֵית לֵיהּ הֲנָאָה`
- 24b:6 — `וְרַבָּנַן — אִית לֵיהּ הֲנָאָה, כְּרַבִּי יוֹסֵי`
- 24b:7 — le maassé de R. Yossi et l'aveugle à la torche : `כׇּל זְמַן שֶׁאֲבוּקָה בְּיָדִי, בְּנֵי אָדָם רוֹאִין אוֹתִי וּמַצִּילִין אוֹתִי מִן הַפְּחָתִין וּמִן הַקּוֹצִין וּמִן הַבַּרְקָנִין`

L'explication française de la page (« שהוא נהנה במאורות שרואין אחרים שיורוהו הדרך ») **est** une
restitution fidèle de ce maassé : le raisonnement tient, le verbatim et la face du folio sont faux.
Le mot juste de la guemara est `הנאה`, non `מתהני`. **C'est le cas le plus étendu du lot :
57 occurrences, 6 fichiers, dont 15 dans les `<meta>` et le JSON-LD** des niveaux 2 et 3.

## F1.5 · siman 9 — `כל המינים מדאורייתא`, dibour hamathil de Tossafot

- `sources/orah-haim/siman-9/niveau-2-lamdan.html` **L833** : `תוספות (מנחות ל״ט:, "כל המינים מדאורייתא")`

**Preuve d'absence.** Recherche exacte → **0 résultat** ; `המינים מדאורייתא` → un seul hit,
Pnei Yehochoua sur Chabbat 27b, sans rapport. Et **les neuf Tossafot que Sefaria sert à
`Tosafot_on_Menachot.39b`** portent ces dibourim, aucun n'est celui-là :

1. `או גדיל או פתיל` · 2. `וההוא גדילים למניינא` · 3. `ופותליהו מתוכו` · 4. `לבן נמי פטר` ·
5. `ופליגא דרב נחמן` · 6. `ורב נחמן דאמר כתנא דבי רבי ישמעאל` · 7. `אף כל צמר ופשתים` ·
8. `אמר אביי האי תנא דבי רבי ישמעאל` · 9. `בגד אין לי אלא בגד צמר`

**Ce qui est fabriqué ici est un localisateur**, non un énoncé halakhique : le lecteur à qui l'on
promet ce dibour ouvrira Menachot 39b et ne le trouvera pas. Les Tossafot qui traitent réellement
du sujet (שאר מינין חייבין מדאורייתא ou לא) sont les n° 6 et 7 ci-dessus ; et le texte de la
guemara correspondant est Menachot 39b:12 : `צמר ופשתים פוטרין בין במינן בין שלא במינן, שאר מינין – במינן פוטרין, שלא במינן אין פוטרין`.
Étendue : **11 occurrences, 5 fichiers**, dont une dans le `<meta description>` de
`niveau-1-base-he.html`.

---

# Famille 2 — CITATION RÉELLE MAL ADRESSÉE (5 verdicts, 4 phrases)

## F2.1 · siman 83, deux verdicts — `חל עליו שם בית הכסא`

- `sources/orah-haim/siman-83/niveau-2-lamdan.html` **L484** et **L533**
- Revendique : `(ברכות כ״ו.; רמב״ם הלכות קריאת שמע פרק ג׳)`

**Adresse vraie, trouvée : `Shulchan Arukh HaRav, Orach Chayim 83:1`** — verbatim :

> …כך אסור לקרות כנגד בית הכסא ישן, דהינו שנשתמש בו כבר פעם אחד בעשית צרכיו, ואפלו אם פנה ממנו הצואה אחר כך, **שכיון שחל עליו שם בית הכסא** פעם אחד — מאוס הוא ואין זה מחנה קדוש, ואסור מן התורה.

Le même Choul'han Aroukh HaRav redit `נקרא עליו שם בית הכסא` (83:2) et `אין שם בית הכסא כלל חוץ לגמא` (83:4).
Formulation voisine, non identique, chez l'Aroukh haChoul'han OH 83:3 : `אין על זה שם "בית הכסא"`.

**Ce que Berakhot 26a sert à la place** — les mots n'y sont pas, la notion y est, autrement dite :
26a:4 `בית הכסא שאמרו אף על פי שאין בו צואה` · 26a:5 `הזמינו לבית הכסא, מהו? יש זימון, או אין זימון?`

La correction est donc légère : il suffit de rendre à la phrase son auteur, l'**Admour haZaken**,
au lieu de la Guemara et du Rambam. Étendue : **27 occurrences, 3 fichiers, dont 9 dans les
`<meta>` et le JSON-LD** du niveau 2.

## F2.2 · siman 27 — `על ידכה — בגובה שביד`

- `sources/orah-haim/siman-27/niveau-2-lamdan.html` **L598** (+ L835)
- Revendique : `(מנחות ל״ז.)`, répété en gras dans la phrase

**Adresse vraie : `Menachot 37b:2`** — verbatim :

> אמר מר: ״ידך״ זו קיבורת, מנלן? דתנו רבנן: **״על ידך״ – זו גובה שביד**. אתה אומר: זו גובה שביד, או אינו אלא על ידך ממש? אמרה תורה: הנח תפילין ביד והנח תפילין בראש, מה להלן בגובה שבראש – אף כאן **בגובה שביד**.

Même expression aux Sifrei Devarim 35:5 et 35:7.

**Deux écarts, pas un.** (a) La braïta est sur **37b**, non 37a. (b) Le lemme qu'elle expose est
**`על ידך`**, non `על ידכה` : `ידכה` בה״י est la dracha **voisine et distincte**, et elle conclut
autre chose — Menachot 37a:3 `מִ״יָּדְכָה״ כְּתִיב, בְּהֵ״י כֵּהָה` et 37a:4 `״יָדְכָה״ בְּהֵ״י – זוֹ שְׂמֹאל`
(c'est-à-dire : la **main gauche**, non la hauteur du bras). La page a soudé le lemme d'une dracha
au résultat de l'autre. Le `קיבורת` qu'elle nomme ensuite est, lui, exact : Menachot 37a:6
`תָּנָא דְּבֵי מְנַשֶּׁה: ״עַל יָדְךָ״ – זוֹ קִיבּוֹרֶת`.

## F2.3 · siman 74 — `עקבו רואה מותר, נוגע אסור`

- `sources/orah-haim/siman-74/niveau-2-lamdan.html` **L604** (titre de section ; + L486, L732)
- Revendique : `(ברכות כ״ד.)`

**Adresse vraie : `Berakhot 25b:7-8`** :

> 25b:7 — והרי **עקבו רואה את הערוה**! קסבר עקבו רואה את הערוה מותר.
> 25b:8 — אתמר: **עקבו רואה את הערוה מותר, נוגע** — אביי אמר: אסור, ורבא אמר: מותר… **והלכתא נוגע — אסור, רואה — מותר**.

**Ce que Berakhot 24a sert à la place** : la sougya de `טפח באשה ערוה` / `שוק באשה ערוה` /
`קול באשה ערוה` (24a:15, 24a:17) — ce qui explique au passage la fenêtre `קולךערבומראךנאוה`
imprimée par la porte dans la colonne `source_reelle`. Le psak cité est réel et son **contenu
est juste** (נוגע אסור, רואה מותר) ; il est à **ברכות כ״ה:**. La forme citée abrège par ailleurs
`את הערוה` — à rétablir en même temps que le folio.

## F2.4 · siman 158 — `המזלזל... בא לידי עניות`

- `sources/orah-haim/siman-158/niveau-2-lamdan.html` **L635** (bloc `teruts-box`)
- Revendique : `(סוטה ד:)`

**Ce que Sotah 4b:6 sert réellement** :

> אָמַר רַבִּי זְרִיקָא אָמַר רַבִּי אֶלְעָזָר: כׇּל **הַמְּזַלְזֵל בִּנְטִילַת יָדַיִם נֶעֱקָר מִן הָעוֹלָם**.

Sotah 4b dit `נעקר מן העולם`, **pas** `בא לידי עניות` — vérifié sur les 18 segments.

**Adresses vraies de la clause d'עניות :**
- `Shabbat 62b:16-17` — dans la liste de ce qui amène la pauvreté : `וּמְזַלְזֵל בִּנְטִילַת יָדַיִם, אָמַר רָבָא: לָא אֲמַרַן אֶלָּא דְּלָא מְשָׁא יְדֵיהּ כְּלָל` … suivi de `אֲנָא מְשַׁאי מְלֵא חָפְנַי מַיָּא וִיהַבוּ לִי מְלֵא חָפְנַי טֵיבוּתָא` — **le daf que la même phrase de la page cite déjà, deux clauses plus haut.**
- `Shulchan Arukh, Orach Chayim 158:9` — et là, l'ellipse de la page est **verbatim** :
  `צריך ליזהר בנטילת ידים שכל **המזלזל** בנטילת ידים חייב נידוי ו**בא לידי עניות** ונעקר מן העולם`.

**Le siman 158 porte sa propre correction**, et c'est le cas le plus instructif du lot : la **même
page** cite ailleurs, correctement, `«כל המזלזל בנטילת ידים... נעקר מן העולם» (סוטה ד:)` — aux
lignes 8, 337, 618, 639, 644, 695 — et la ligne 618 prend soin de laisser `ובא לידי עניות`
**hors** des guillemets. La ligne 635 est le seul endroit où la clause d'עניות entre dans les
guillemets sous l'adresse de Sotah. Un unique glissement, pas une habitude.

---

# Famille 3 — FAUX POSITIF DE LA PORTE (4 verdicts)

**À lire avec la réserve suivante, qui compte** : sur ces quatre, **deux sont des faux positifs
purs** (la citation est verbatim) et **deux sont des faux positifs de l'accusation de fabrication**
— le texte est bien à l'adresse donnée, mais le mot n'est pas exactement le bon. Ces deux-là sont
des `VARIANTE` mal classées en `INTROUVABLE`, et ils **demandent une remise au verbatim**.
Les compter comme « rien à faire » serait un plancher annoncé comme un compte.

## F3.1 (pur) · siman 106 — `נשים ועבדים… חייבין בתפלה`

`sources/orah-haim/siman-106/niveau-2-lamdan.html` **L469**. La page annonce `ברכות כ׳.-כ׳:`
— les deux faces, et c'est exactement là que la michna est coupée :

- `Berakhot 20a:10` — `מַתְנִי׳ **נָשִׁים וַעֲבָדִים** וּקְטַנִּים פְּטוּרִין מִקְּרִיאַת שְׁמַע` (sous-chaîne exacte vérifiée)
- `Berakhot 20b:5` — `וְ**חַיָּיבִין בִּתְפִלָּה**. דְּרַחֲמֵי נִינְהוּ` (sous-chaîne exacte vérifiée)

Les deux côtés de l'ellipse sont verbatim, de part et d'autre du changement de folio. **Rien à
corriger.** La page a même raison sur le fond : le `דרחמי נינהו` qu'elle cite à côté
(`«תפלה רחמי נינהו»`) est bien la raison donnée par 20b:5.

## F3.2 (pur) · siman 25 — `וקשרתם … ודברת בם`

`sources/orah-haim/siman-25/niveau-2-lamdan.html` **L488**. Ce sont **deux versets**, verbatim :

- `Deuteronomy 6:8` — `וּקְשַׁרְתָּ֥ם לְא֖וֹת עַל־יָדֶ֑ךָ` (sous-chaîne exacte vérifiée)
- `Deuteronomy 6:7` — `וְשִׁנַּנְתָּ֣ם לְבָנֶ֔יךָ **וְדִבַּרְתָּ֖ בָּ֑ם** בְּשִׁבְתְּךָ֤ בְּבֵיתֶ֙ךָ֙…` (idem)

La porte les a confrontés au daf cité à côté (`ברכות ו׳.`) parce que le garde-fou `bien_attribuee()`
n'absout un verset que si le nom de son livre figure au voisinage — et ici le voisinage nomme
Berakhot, non Devarim. **Rien à corriger sur la citation.** Une réserve à passer au contenu, sans
rapport avec la fabrication : Berakhot 6a traite des tefilin du Saint béni soit-Il (6a:17-20), non
de la דרשה de `וקשרתם`/`ודברת בם` ; le lieu classique du lien tefilin/ק״ש est ברכות י״ד:-ט״ו. —
à faire voir à un relecteur de contenu, pas à cette porte.

## F3.3 (variante réelle) · siman 120 — `כיון שבאה עבודה באה הודאה`

`sources/orah-haim/siman-120/niveau-2-lamdan.html` **L627**. **Bonne adresse**, Meguila 18a:2 :

> וְכֵיוָן שֶׁבָּאת תְּפִלָּה — בָּאת עֲבוֹדָה… וְכֵיוָן **שֶׁבָּאת עֲבוֹדָה — בָּאתָה תּוֹדָה**, שֶׁנֶּאֱמַר: ״זוֹבֵחַ תּוֹדָה יְכַבְּדָנְנִי״.

Trois écarts : `שבאה`/`שבאת`, `באה`/`באתה`, et surtout **`הודאה` pour `תודה`**. Le dernier n'est
pas une orthographe : c'est un autre mot — que la guemara emploie bien, mais **à la ligne
suivante** (18a:3 : `וּמָה רָאוּ לוֹמַר בִּרְכַּת כֹּהֲנִים אַחַר **הוֹדָאָה**`). La page a mêlé
deux lignes voisines. **Pas une fabrication ; une variante à remettre au verbatim.**

## F3.4 (variante réelle) · siman 88 — `טובלין בעלי קריין`

`sources/orah-haim/siman-88/niveau-2-lamdan.html` **L577**. **Bonne adresse**, Bava Kamma 82a:3 :

> עשרה תקנות תיקן עזרא: … ושתהא אשה חופפת וטובלת; ושיהו רוכלין מחזירין בעיירות; ו**תיקן טבילה לבעלי קריין**.

Le texte réel est **`טבילה לבעלי קריין`** (substantif) ; la page écrit `טובלין בעלי קריין`
(verbe). **Pas une fabrication ; une variante à remettre au verbatim.** Le reste du bloc est juste :
`כדי שלא יהיו תלמידי חכמים מצויין אצל נשותיהן כתרנגולין` est bien le טעם donné à Berakhot 22a,
et la porte ne l'a pas contesté.

---

# Les mécanismes de faux positifs — la partie la plus réutilisable du lot

## Mécanisme A — l'ellipse dont les deux côtés font moins de 12 lettres (2 cas : F3.1, F3.2)

`verdict()` découpe le fragment sur `…`, puis **jette toute part de moins de
`MIN_LETTRES = 12` lettres**. Quand il ne reste rien, la ligne

```python
parts = parts or [frag]
```

**recolle la citation entière, ellipse comprise**, et la compare d'un bloc à la source : le
milieu élidé manquant, le ratio s'effondre mécaniquement. En parallèle `locate()` ne prend que
**la plus longue** part et refuse de chercher sous `MIN_CITATION_REFERENCEE = 12`. Les deux
conditions de `INTROUVABLE` — absent de la source **et** absent du reste de Sefaria — sont donc
remplies sans qu'aucune comparaison utile n'ait eu lieu.

Mesuré : `נשים ועבדים` = **10** lettres, `חייבין בתפלה` = **11** ; `וקשרתם` = **6**,
`ודברת בם` = **7**. Les quatre sont verbatim dans Sefaria. **Une citation à ellipse courte des
deux côtés ne peut pas être acquittée par cette porte**, quelle que soit sa justesse.

## Mécanisme B — la citation de trois à quatre mots n'a pas de bande « VARIANTE » (2 cas : F3.3, F3.4)

Sous le seuil, il n'existe que deux voies vers `VARIANTE` : `ratio ≥ SEUIL_VARIANTE = 0.86`, ou
`suite_de_mots ≥ MIN_MOTS_SUIVIS = 3`. Sur une citation de 3 ou 4 mots, **un seul mot changé
ferme les deux** — il reste au mieux 2 mots suivis, et le ratio tombe sous 0,86. Et le même mot
changé fait rendre **0 résultat** à `locate()`, qui interroge le champ `exact`. Résultat : une
citation quasi verbatim, à la bonne adresse, atterrit dans le verdict **le plus grave du
dispositif**.

Mesuré : `טובלין בעלי קריין` (3 mots) → ratio 0,80 ; `כיון שבאה עבודה באה הודאה` (5 mots, 3 écarts)
→ 0,86 à la frontière. La résolution de la porte est le plancher : **plus la citation est courte,
plus `ABSENT` est inévitable** — et `ABSENT` + `locate()` muet = accusation de fabrication.

## Mécanisme C — le préfixe attaché (ש/ו/ד/ב/כ/ל) : il ne crée pas le faux positif, il aggrave le verdict (2 cas : F2.1)

Celui-ci n'a innocenté personne, mais il a **transformé une « mal adressée » en « fabriquée »**,
et c'est le plus coûteux des trois. `locate()` interroge `api/search-wrapper` en `field: exact`,
qui **apparie des jetons entiers**. Mesuré en direct :

| requête | résultat |
|---|---|
| `חל עליו שם בית הכסא` | **0 résultat** |
| `שחל עליו שם בית הכסא` | `Shulchan Arukh HaRav, Orach Chayim 83:1` (deux versions) |

La source porte `שכיון **ש**חל עליו…` : la citation de la page commence **au milieu d'un mot** du
texte source. L'index ne la voit pas, `locate()` rend `[]`, et le verdict passe de `REF_FAUSSE`
(« le texte existe, ailleurs ») à `INTROUVABLE` (« fabrication »). Deux des 16 verdicts de ce lot
sont dans ce cas. **Remède simple et testé ici : relancer la recherche en préfixant la citation
des cinq lettres serviles, ou en retirant la première lettre du premier mot** — c'est ainsi que
j'ai trouvé l'adresse vraie.

## Ce qui n'était PAS le mécanisme — et qu'il faut dire

Le mandate signalait la classe de faux positifs déjà observée dans ce dépôt : **les blocs
parenthésés et les `<small>` que Sefaria insère à l'intérieur des seifim, et les ajouts
parenthétiques du Choul'han Aroukh HaRav**, que l'index plein-texte ignore. **Elle n'explique
aucun des 16.** J'ai systématiquement cherché dans le **segment servi** avant de conclure, et non
par l'index seul : les cinq fabrications sont absentes des segments eux-mêmes, pas seulement de
l'index. Le seul cas où l'index a menti alors que le segment contenait le texte est le
mécanisme C — et la cause y est le préfixe, pas la parenthèse.

Corollaire utile : sur ce lot, **l'index plein-texte et le texte des segments se sont accordés
15 fois sur 16**. La défiance à avoir envers `locate()` porte sur le **jeton**, pas sur la
couverture.

---

# Ce que je n'ai pas fait

1. **Aucune page de `sources/` n'a été modifiée**, aucun `git add`, aucun commit. Ce lot classe.
2. **`verifier-citations.py` n'a pas été lancé** (cache `scripts/.cache-sefaria` partagé entre
   quatre agents). Tout vient de requêtes curl directes que j'ai faites moi-même.
3. **Je n'ai pas corrigé les mécanismes A, B et C** dans `verifier-citations.py` : ce sont des
   modifications de garde-fou, à faire sous un mandat qui les mesure avant/après sur tout le site.
   Rappel du CLAUDE.md, qui s'applique mot pour mot ici : *un garde-fou qu'on ne règle que dans un
   sens devient muet sans qu'on s'en aperçoive* — les mécanismes A et B sont des resserrements
   contre les faux positifs qui ont fini par produire de faux **graves**.
4. **Je n'ai pas vérifié les 74 `REF_FAUSSE`, les 16 `NON_RESOLU` ni les 295 `VARIANTE`** d'Orah
   Haïm : hors lot. Mais le mécanisme C dit qu'une partie des `INTROUVABLE` du site entier sont
   des `REF_FAUSSE` déguisées, et les mécanismes A et B qu'une partie sont des `VARIANTE` —
   le relevé des verdicts graves est donc **surévalué en gravité**, et c'est à vérifier avant de
   l'annoncer.
5. **Je n'ai pas tranché si les niveaux 1 et 3 raisonnent encore juste** sans les cinq phrases
   fabriquées. J'ai vérifié que le **contenu halakhique** porté par chacune est exact et sourçable
   (c'est dit cas par cas), mais la relecture du raisonnement français est un travail de contenu.
6. **Je n'ai pas mesuré l'étendue hors d'Orah Haïm.** Les 140 occurrences comptées le sont sur
   `sources/orah-haim/` seulement ; je n'ai pas cherché ces mêmes phrases dans Hilkhot Chabbat ni
   dans Yoré Déa, et au vu de l'historique du dépôt il serait imprudent de supposer qu'elles n'y
   sont pas.
7. **Je n'ai pas vérifié si la Michna Beroura ou les nossei kelim reprennent quelque part l'une
   des cinq phrases fabriquées** sous une forme que l'index n'atteint pas. Pour chacune j'ai
   éprouvé la recherche exacte, les variantes de formulation que je pouvais former, **et** le
   texte des segments de la référence revendiquée ; je n'ai pas balayé tout le corpus des
   commentateurs. Les cinq verdicts de fabrication sont solides sur ce que j'ai mesuré, mais
   « absent de tout Sefaria » reste, chez moi comme chez la porte, une conclusion tirée d'un
   nombre fini de requêtes.
