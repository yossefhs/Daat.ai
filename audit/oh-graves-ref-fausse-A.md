# Orah Haïm — tri du lot A : premier tiers des 74 REF_FAUSSE

Relevé d'origine : `audit/citations-sources-orah-haim.csv`.
Sélection : lignes dont `verdict == REF_FAUSSE`, triées par `(fichier, ligne)` croissants
(ligne lue comme un **entier** ; vérifié : le tri lexicographique donne ici le même ordre,
donc aucune ligne ne peut tomber entre deux lots à cause de ce choix), puis les **25 premières**.

**Ma tranche : 25 verdicts sur 74.**
- première : `sources/orah-haim/siman-107/niveau-2-lamdan.html` ligne **542**
- dernière : `sources/orah-haim/siman-59/niveau-2-lamdan.html` ligne **513**

Méthode : interrogation **directe** de Sefaria par `urllib` (cache privé dans mon scratchpad,
`scripts/.cache-sefaria` jamais touché), comparaison sur **squelettes consonantiques**
(nikoud, ponctuation, ancres `<i data-…>` et balises neutralisés). `verifier-citations.py`
n'a **pas** été lancé. **Aucun fichier de `sources/` n'a été modifié.**

## Résultat

| famille | n |
|---|---|
| 1 — fabrication réelle | **0** |
| 2 — citation réelle mal adressée | **9** |
| 3 — faux positif de la porte | **15** |
| 4 — hors convention | **1** |
| non tranchés | **0** |
| **total** | **25** |

Les 25 textes hébreux de ma tranche **existent tous** dans Sefaria. **Aucune fabrication.**

---

## Famille 2 — citations réelles MAL ADRESSÉES (9)

Gradation, parce que les neuf ne se valent pas et qu'annoncer neuf défauts égaux serait faux :

- **lourd (3 cas)** — le folio nommé ne porte *rien* du texte, et le texte est ailleurs,
  dans un autre traité ou un autre folio : #19, #16, #18.
- **mineur (6 cas)** — un **verset en exergue** dont la page ne donne pas la référence
  biblique ; la sugya nommée est la bonne, c'est l'adresse *du verset* qui manque : #25, #10,
  #20, #22, #23, #24.

### 2.1 — LOURD · siman 157 : « כזורק אבן לחמת » donné à בבא מציעא ק״ז:, il est à שבת י׳.

- `sources/orah-haim/siman-157/niveau-1-base.html` **ligne 604** (teaser « approfondir »)
- adresse revendiquée : **בבא מציעא ק״ז:**
- adresse VRAIE : **שבת י׳.** — Sefaria `Bava_Metzia.107b` : `כזורק` ABSENT.
  `Shabbat.10a` (servi `Shabbat 10a`) :
  `…רביעית זמן סעודה לכל אדם … ששית מאכל תלמידי חכמים מכאן ואילך כזורק אבן לחמת אמר אביי לא אמרן אלא דלא טעים מידי בצפרא…`
  C'est **mot pour mot la sugya du siman 157** (heure de la סעודה, le ת״ח qui attend la 6ᵉ heure),
  et le Mehaber lui-même l'a : `Shulchan_Arukh,_Orach_Chayim.157.1` → `…ימתין עד שעה ששית ולא יאחר יותר דהוי כזורק אבן לחמת אם לא טעם מידי בצפרא`.
- ce que בבא מציעא ק״ז: porte réellement : `…וברך את לחמך ואת מימיך זו פת במלח וקיתון של מים…` —
  c'est la source de la **פת שחרית**, l'autre membre de la même phrase du teaser. Les deux sources
  ont été fusionnées et la mauvaise est restée collée à la citation.
- **preuve interne qui tranche** : le niveau 2 du même siman donne la bonne adresse —
  `sources/orah-haim/siman-157/niveau-2-lamdan.html` lignes **469** et **737** :
  `<a class="intra-ref" href="#2-שעה-רביעית">שבת י׳.</a>`. La page contredit sa propre page de pilpoul.
- étendue mesurée : le teaser existe dans les trois langues —
  `niveau-1-base.html:604`, `niveau-1-base-he.html:606`, `niveau-1-base-en.html:604`.

### 2.2 — LOURD · simanim 153 et 154 : « מעלין בקודש ואין מורידין » donné à מגילה כ״ו., il est à מגילה ט׳:

- `sources/orah-haim/siman-153/niveau-2-lamdan.html` **ligne 513** — « ומדין «מעלין בקודש ואין מורידין» (מגילה כ״ו.-כ״ז.) »
- `sources/orah-haim/siman-154/niveau-2-lamdan.html` **ligne 577** — « יסוד זה נלמד במגילה (כ״ו.-כ״ו:) ובכמה מקומות »
- adresse VRAIE : **מגילה ט׳:** — `Megillah.9b` :
  `…כהן גדול משום איבה כהן הדיוט משום מעלין בקודש ולא מורידין…`
  et **מנחות ל״ט.** — `Menachot.39a` : `…וכשהוא מסיים מסיים בלבן מעלין בקודש ולא מורידין…`
- j'ai balayé tout le voisinage, et c'est un trou net : dans `Megillah` **25b, 26a, 26b, 27a,
  28a, 28b, 29a**, les mots `מעלין`, `מורידין` et `בקדושה` sont **tous absents**. Le seul folio
  voisin qui dise quelque chose est **מגילה כ״ז:** :
  `אין מוכרין את של רבים ליחיד מפני שמורידין אותו מקדושתו` — c'est bien la sugya de l'הורדה
  מקדושתו, mais ce n'est pas le maxime, et **27b est hors des deux plages annoncées**
  (« כ״ו.-כ״ז. » s'arrête à 27a, « כ״ו.-כ״ו: » à 26b).
- noter aussi la forme : les deux pages écrivent `ואין מורידין`, la guemara `ולא מורידין`.
- étendue mesurée (citation + une adresse de מגילה **sur la même ligne**, les trois langues) :
  siman 153 `niveau-2-lamdan` **5 lignes × 3** ; siman 154 **8 lignes × 3** dans `niveau-2-lamdan`,
  plus 1 × 3 dans `index` et 1 × 3 dans `niveau-1-base`. Le relevé CSV n'en voyait que **2**
  (il ne balaye que le français, une ligne par extraction) : le travail réel est d'un autre ordre.
- le même siman 153 porte par ailleurs un **faux positif** sur le même sujet (#17, §3.1).

### 2.3 — MINEUR · versets en exergue sans leur référence biblique (6)

Dans les six, la sugya nommée est **la bonne** ; ce qui manque est l'adresse du **verset**.
Le lecteur qui ouvre le folio y trouve le sujet, pas les mots entre guillemets.

| # | fichier · ligne | citation | revendiqué | VRAI | preuve Sefaria |
|---|---|---|---|---|---|
| 25 | `siman-59/niveau-2-lamdan.html` **513** | שבע ביום הללתיך | ברכות י״א: | **תהלים קי״ט:קס״ד** ; l'asmakhta est au **ירושלמי ברכות א׳:ה׳** | `Berakhot.11b` : `הללתיך` **absent**. `Jerusalem_Talmud_Berakhot.1.5` : `…על שם שבע ביום הללתיך על משפטי צדקך…` |
| 10 | `siman-118/niveau-2-lamdan.html` **533** | מלך במשפט יעמיד ארץ | ברכות י״ב: | **משלי כ״ט:ד** | `Berakhot.12b` porte `…שמתפלל המלך הקדוש והמלך המשפט…` mais **pas le verset** ; `Proverbs.29.4` le porte |
| 20 | `siman-29/niveau-2-lamdan.html` **585** | אות היא ביני וביניכם | מנחות ל״ו: | **שמות ל״א:י״ג** | `Menachot.36b` porte `והיה לאות על ידך … שהן גופן אות`, **pas** la clause citée. `Exodus.31.13` : `…כי אות הוא ביני וביניכם…` — **ktiv `הוא`**, la page écrit `היא` (qeré) |
| 22 | `siman-47/index.html` **454** | על מה אבדה הארץ | נדרים פא. | **ירמיה ט׳:י״א** | `Nedarim.81a` cite le verset **par son incipit seul** : `…מאי דכתיב מי האיש החכם ויבן את זאת … ויאמר ה׳ על עזבם את תורתי…` — la clause `על מה אבדה הארץ` **n'y est pas**. `Jeremiah.9.11` : `מי האיש החכם ויבן את זאת ואשר דבר פי ה׳ אליו ויגדה על מה אבדה הארץ נצתה כמדבר` |
| 23 | `siman-47/index.html` **512** | id. | id. | id. | id. |
| 24 | `siman-47/niveau-3-synthese.html` **539** | id. | id. | id. | id. |

Pour #22-24 la sugya de נדרים פ״א. est **exactement** celle du siman 47 (le châtiment pour
avoir délaissé ברכת התורה) : la correction est d'ajouter `(ירמיה ט׳:י״א)` au verset, non de
changer la sugya. Étendue trilingue mesurée : siman 59 **1 ligne × 3** ; siman 118 **3 × 3** ;
siman 29 **2 × 3** ; siman 47 **2 × 3** dans `index` + **1 × 3** dans `niveau-3-synthese`.

---

## Famille 3 — FAUX POSITIFS, par mécanisme (15)

C'est la partie la plus utile du lot : **six mécanismes**, dont le premier explique à lui
seul 7 des 25 verdicts de ma tranche.

### 3.1 — M1 · « mots du Mehaber, adresse de la sugya » — 7 cas

La citation est **le texte du Choul'han Aroukh du siman que la page expose** ; la parenthèse
qui suit nomme le **locus talmudique / le Rambam d'où le din est tiré**, et ferme un item de
sommaire ou un titre de section entier.

**Mécanisme exact, dans le code** : `verifier-citations.py` possède déjà le repli qu'il faut —
`ref_du_siman(path)`, « Repli sur l'ouvrage dont la page EST l'exposé » (≈ l. 1830). Mais il est
gardé par `if v == 'ABSENT' and not ref_collee(plain, at, len(frag))`. Or la forme conventionnelle
du dépôt pour un item de sommaire et un `h2.section-title` met précisément la parenthèse de
sources **collée après les guillemets**. Le repli est donc **désactivé exactement dans la mise en
page où il serait nécessaire**. Les deux replis suivants (`ref_mb_du_siman`, `candidats_ouvrages`,
`Rashi_on_`/`Tosafot_on_`) ne rattrapent pas : aucun ne propose le siman de la page.

| # | fichier · ligne | citation | revendiqué | où elle est RÉELLEMENT |
|---|---|---|---|---|
| 2 | `siman-108/niveau-2-lamdan.html` **484** | ואם היפך לא יצא | ברכות כ״ו., רמב״ם תפלה ג׳ | `Shulchan_Arukh,_Orach_Chayim.108.1` : `…הראשונה מנחה והשני לתשלומין ואם היפך לא יצא ידי תפלה…` |
| 5 | `siman-111/niveau-2-lamdan.html` **534** | ולא יפסיק ביניהם אפי׳ באמן | ברכות ד׳: | `…111.1` : `צריך לסמוך גאולה לתפלה ולא יפסיק ביניהם אפי׳ באמן אחר גאל ישראל…` |
| 11 | `siman-124/niveau-2-lamdan.html` **674** | שאינו יודע להתפלל | ראש השנה ל״ד: | `…124.1` : `…יחזיר ש״צ התפלה שאם יש מי שאינו יודע להתפלל יכוין למה שהוא אומר…` — ר״ה ל״ד: **est** la bonne sugya, mais sa langue est `כדי להוציא את שאינו בקי` |
| 12 | `siman-126/niveau-2-lamdan.html` **608** | שהרי תפלת המוספין לפניו | ברכות ל׳: | `…126.3` : `…אין מחזירין אותו מפני טורח הצבור שהרי תפלת המוספין לפניו…` |
| 13 | `siman-128/niveau-2-lamdan.html` **484** | יצאו ידי חובתן מן התורה | כתובות כ״ד:, תוספות | `Shulchan_Arukh_HaRav,_Orach_Chayim.128.1` : `…ומשנשאו כפיהם וברכו פעם אחת ביום יצאו ידי חובתן מן התורה…` |
| 14 | `siman-128/niveau-2-lamdan.html` **533** | יצאו ידי חובתן | כתובות כ״ד: | id. (forme courte du même) |
| 17 | `siman-153/niveau-2-lamdan.html` **572** | איפכא להורידן מקדושתן אסור | מגילה כ״ו., רמב״ם תפילה י״א | `…153.2` : `…מכרו ספרים לוקחים בדמיהם ס״ת אבל איפכא להורידן מקדושתן אסור…` |

Conséquence pour la porte : **la pile entière des items de sommaire et des `h2.section-title`
d'Orah Haïm** est exposée à ce mécanisme. C'est un bruit de classe, pas sept accidents.

### 3.2 — M2 · élision d'un mot sans « … », plus ktiv — 2 cas (#3, #4)

`siman-110/niveau-2-lamdan.html` **486** et **569**, « צרכי עמך מרובים » (ברכות כ״ט:).
Le texte **est** au folio cité : `Berakhot.29b` → `…אחרים אומרים צרכי עמך ישראל מרובין ודעתם קצרה…`.
Deux écarts, aucun d'adresse : le mot `ישראל` est **élidé au milieu sans « … »**, et `מרובין`
devient `מרובים`. La forme exacte que la page imprime est celle du Mehaber de son propre siman —
`Shulchan_Arukh,_Orach_Chayim.110.3` : `…מתפלל צרכי עמך מרובים וכו׳…` — ce qui est précisément ce
que `locate()` a trouvé « ailleurs » et qui a fait basculer le verdict en REF_FAUSSE.

**Et c'est là le mécanisme le plus traître du dispositif** : `REF_FAUSSE` est émis dès que
`locate()` trouve une occurrence exacte **n'importe où**, sans jamais revenir mesurer ce que le
folio revendiqué contient. Ici il contient le texte à **un mot et une lettre près** — ce qui,
confronté au bon segment, serait un `VARIANTE`. **La porte sait étiqueter « très proche », et
elle ne s'en sert pas à cet endroit : trouver mieux ailleurs la fait monter d'un cran de
gravité au lieu de la faire descendre.** C'est une escalade de sévérité, pas une détection.

### 3.3 — M3 · la référence annoncée en TÊTE de ligne est hors fenêtre — 1 cas (#1)

`siman-107/niveau-2-lamdan.html` **542**. La ligne ouvre par
`<strong>שורש הדין — ברכות כ״א.:</strong>` puis cite « ולואי שיתפלל אדם כל היום כולו », puis
écrit `ופסקו הראשונים (רי״ף, רמב״ם הלכות תפילה פרק י׳, רא״ש)`.
La citation est **verbatim à ברכות כ״א.** — `Berakhot.21a` :
`…ספק התפלל ספק לא התפלל אינו חוזר ומתפלל ורבי יוחנן אמר ולואי שיתפלל אדם כל היום כולו…`
La porte lui a opposé `Mishneh_Torah,_Prayer_and_the_Priestly_Blessing.10`, la seule référence
que sa fenêtre (30 caractères avant / 60 après) ait vue — celle des **Rishonim qui tranchent
comme** cette parole, pas celle de la parole. La référence revendiquée était à gauche, hors fenêtre.

### 3.4 — M4 · la page nomme deux adresses, la porte n'en résout qu'une — 3 cas (#6, #7, #8)

Toutes trois dans `siman-115/niveau-2-lamdan.html`.

- **#7, ligne 533** — titre : `« מותר האדם מן הבהמה » (קהלת ג׳; ברכות ל״ג.)`. La page donne
  **deux** adresses ; la bonne est la première, que la porte ne lit pas (pas de Tanakh, et
  `קהלת ג׳` est un chapitre sans verset). `Ecclesiastes.3.19` :
  `…ורוח אחד לכל ומותר האדם מן הבהמה אין כי הכל הבל`.
- **#6, ligne 486** — sommaire : `« אם אין דעה הבדלה מנין » (ברכות ל״ג., ירושלמי)`. La page
  **nomme le Yerushalmi**, et c'est lui : `Jerusalem_Talmud_Berakhot.5.2` →
  `…היאך ביטלו חונן הדעת בשבת אם אין דיעה תפילה מניין וכה אם אין דיעה הבדלה מניין אמר רבי יצחק בר אלעזר…`
  (ktiv `דיעה`/`מניין` contre `דעה`/`מנין`). Un « ירושלמי » nu, sans traité ni perek, n'est pas
  résoluble : la porte juge alors contre le Bavli de la même ligne.
- **#8, ligne 608** — `h2.section-title` : `« אם אין דעה הבדלה מנין » (ברכות ל״ג.)`. Ici le titre
  ne nomme que le Bavli — mais **l'attribution juste est dans le corps de la même section, dix
  lignes plus bas** : `ובירושלמי (ברכות פרק ה׳) נתנו טעם` (l. 617), et le `yesod-box` de la même
  page écrit `« אם אין דעה הבדלה מנין » (ירושלמי)` (l. 638). Le lecteur a la bonne source **sous
  les yeux, dans la page qu'il lit** — le critère même que CLAUDE.md pose pour les troncatures.
  La porte, qui ne regarde qu'une ligne, ne peut pas le voir.
  *Réserve honnête* : le titre, lu seul, promet ברכות ל״ג. pour des mots qui n'y sont pas. Si
  l'on veut resserrer, ajouter `ירושלמי` au titre coûte quatre caractères. Je ne le compte pas
  en famille 2 parce que la page attribue correctement là où elle développe.

### 3.5 — M5 · seule la borne basse d'une plage de dafim est résolue — 1 cas (#15)

`siman-151/niveau-2-lamdan.html` **469** : la page écrit **מגילה כ״ח.-כ״ט.** et cite
« ואהי להם למקדש מעט ». La porte n'a résolu que `Megillah.28a`. Le texte est à la **borne
haute** : `Megillah.29a` → `…שבקוהו ואהי להם למקדש מעט אמר רבי יצחק אלו בתי כנסיות ובתי מדרשות
שבבבל…` — et c'est, de surcroît, la sugya même du siman 151 (la קדושה des בתי כנסיות).
Le verset est יחזקאל י״א:ט״ז (`Ezekiel.11.16`, vérifié).
C'est le piège du **tiret de plage** déjà consigné dans CLAUDE.md pour `verifier-etiquettes.py`
et `verifier-denombrements.py` ; il est ici dans la porte des citations.

### 3.6 — M6 · `<em>Fondement : …</em>` lu comme l'adresse d'un verset — 1 cas (#21)

`siman-3/niveau-4-daat-harav.html` **913**. Prose française :
« La conduite « privée » reste ordonnée par le « מלא כל הארץ כבודו ». *Fondement : Mehaber +
Rama OH 3:2 (Or Zaroua), lu par la voie du Rav comme qedoucha du corps.* »
`Shulchan_Arukh,_Orach_Chayim.3.2` fait **95 consonnes** et ne porte pas ces mots ; c'est
ישעיה ו׳:ג — `Isaiah.6.3` : `…קדוש קדוש קדוש ה׳ צבאות מלא כל הארץ כבודו`.
La ligne `Fondement :` nomme la source **du psak du paragraphe**, pas celle d'un verset cité en
exergue. Deux garde-fous existants manquent la cible : la porte ne lit pas le Tanakh, et le
garde `RE_VERSET` (`שנאמר`, `דכתיב`, `ואומר`) ne déclenche pas dans une phrase **française**.

---

## Famille 4 — HORS CONVENTION (1)

### 4.1 — #9 · formule liturgique à l'intérieur d'un `<em>résumé</em> :`

`sources/orah-haim/siman-116/niveau-3-synthese.html` **487** :
« on y insère une prière pour un malade (*résumé* : עד שלא תתחתם — avant de sceller
« רופא חולי עמו ישראל »), car c'est `דרך תפלה ובקשה` (cf. סי׳ קי״ט ; ברכות ל״ד. ; עבודה זרה ח׳.). »

« רופא חולי עמו ישראל » est la **ח ת י מ ה de ברכת רפאנו** — le nom de la clause de clôture de
la berakha, un désignateur liturgique, et non la citation d'un ouvrage. Elle ne figure ni à
`Berakhot.34a` ni à `Avodah_Zarah.8a` ni à `Shulchan_Arukh,_Orach_Chayim.116.1`/`.2` ;
`locate()` la retrouve dans les siddourim, ce qui est exactement ce qu'elle est.
Deux motifs cumulés d'exemption : elle est **dans la portée d'un `<em>résumé</em> :`**, et les
deux folios que la porte lui oppose sont donnés **en fin de phrase pour le din**
(`דרך תפלה ובקשה`), pas pour elle.

---

## Ce que je n'ai PAS fait

1. **Aucune page de `sources/` n'a été modifiée** — ce lot classe, il ne corrige pas. Les neuf
   cas de famille 2 restent entiers, dans les trois langues.
2. **`verifier-citations.py` n'a pas été lancé** et `scripts/.cache-sefaria` n'a pas été touché
   (cache privé dans mon scratchpad).
3. **Je n'ai pas corrigé la porte.** Les six mécanismes sont décrits ; `M1` et `M2` sont
   localisés dans le code (`ref_du_siman` gardé par `ref_collee` ; `locate()` qui promeut en
   `REF_FAUSSE` sans re-mesurer le folio revendiqué). Aucune ligne de `scripts/` n'a été écrite.
4. **Je n'ai pas chiffré l'étendue trilingue de façon exhaustive.** Les comptes donnés sont des
   `grep` « citation + adresse sur la même ligne », donc **approchés** : pour le siman 154 le
   motif d'adresse employé était le simple `מגילה`, plus large que `מגילה כ״ו`. À reprendre
   avant correction. Ce que je tiens pour établi : le CSV ne voit que le français et sous-compte
   le travail réel d'un facteur voisin de trois.
5. **Je n'ai pas examiné les 49 autres REF_FAUSSE** (lots B et C), ni les 16 INTROUVABLE,
   ni les 16 NON_RESOLU, ni les 295 VARIANTE.
6. **La petiha n'est en cause dans aucun de mes 25 cas** : ma tranche ne contient **pas une
   seule** adresse de Michna Beroura — les 25 adresses revendiquées sont des folios de Talmud
   (19), le Rambam הלכות תפילה (4, dont 2 en second), et le Choul'han Aroukh lui-même (1). Le
   recalage des 28 adresses MB d'Orah Haïm ne peut donc pas être testé sur ce lot ; les simanim
   à petiha 178 et 211 n'y figurent pas. **C'est une absence constatée, pas un contrôle réussi.**
7. **Je n'ai pas tranché si le ktiv `הוא` de שמות ל״א:י״ג** (#20) doit être écrit `הוא` ou laissé
   `היא` dans la page : citer le ktiv ou le qeré est une décision éditoriale, pas un fait de source.

---

# ARBITRAGE DU LOT A — 2026-10-01

Relecture adversariale du classement ci-dessus. **Toutes les affirmations de source de cette
section viennent de requêtes Sefaria faites par moi** (`api/texts`, cache privé dans mon
scratchpad). `verifier-citations.py` **n'a pas été lancé**, `scripts/.cache-sefaria` **n'a pas
été touché**, **aucune page de `sources/` n'a été modifiée**, aucun `git add`, aucun commit.

## Ce que je confirme

**Famille 1 = 0 : je l'établis moi-même.** J'ai retrouvé les **25** textes dans les segments
Sefaria, un par un. **Aucune fabrication dans cette tranche.**

**La tranche est complète et exacte.** Reproduite depuis le CSV : 74 `REF_FAUSSE`, tri par
`(fichier, int(ligne))`, 25 premiers. Première et dernière identiques à l'annonce, et les
25 cas du relevé sont les 25 lignes du tri. La claim « le tri lexicographique donne ici le
même ordre » **est vraie** : toutes les valeurs de `ligne` du fichier font 3 chiffres
(min 446, max 913). La frontière 25→26 ne porte pas d'égalité, et le lot B annonce
rang 26 = `siman-60/niveau-2-lamdan.html:546`, rang 50 = `siman-76:563` — **aucune ligne n'est
tombée entre les deux lots.**

**Les deux cas lourds de famille 2 sont confirmés par mesure indépendante.**
- #19, siman 157 : `Bava_Metzia.107b` ne porte ni `כזורק` ni `אבן` ni `לחמת` (0 occurrence) ;
  `Shabbat.10a` porte `…ששית מאכל תלמידי חכמים מכאן ואילך כזורק אבן לחמת אמר אביי…`, et
  `Shulchan_Arukh,_Orach_Chayim.157.1` `…דהוי כזורק אבן לחמת אם לא טעם מידי בצפרא`.
- #16/#18, simanim 153-154 : balayage refait folio par folio — `מעלין בקודש` est **absent** de
  `Megillah` 25b, 26a, 26b, **27a, 27b**, 28a et 29a ; il est verbatim à `Megillah.9b`
  (`…כהן הדיוט משום מעלין בקודש ולא מורידין…`) et `Menachot.39a`.

**Quatre mécanismes de faux positif sont réels et expliquent vraiment leurs cas** (vérifiés,
pas seulement nommés) : **M4** sur #7 (`Ecclesiastes.3.19` porte `ומותר האדם מן הבהמה`,
`Berakhot.33a` non, et la page écrit `קהלת ג׳` **en premier**) et sur #6 (verbatim à
`Jerusalem_Talmud_Berakhot.5.2`, ktiv `אם אין דיעה הבדלה מניין` — j'ai vérifié avec ce ktiv ;
absent de `Berakhot.33a`) ; **M5** sur #15 (absent de `Megillah.28a`, verbatim à `Megillah.29a`,
et la page annonce bien la **plage** `מגילה כ״ח.-כ״ט.` qui **contient** le bon folio — c'est le
faux positif le plus propre du lot) ; **M6** sur #21 (`Isaiah.6.3` porte la clause,
`Shulchan_Arukh,_Orach_Chayim.3.2` non, et `RE_VERSET` ne peut pas déclencher dans une phrase
française).

**La famille 4 (#9) est fondée.** Vérifié dans la page : la citation est bien **à l'intérieur**
de la parenthèse ouverte par `<em>résumé</em> :`, et les trois renvois ferment la phrase sur
`דרך תפלה ובקשה`. Vérifié contre les sources : la clause est absente de `Berakhot.34a`,
`Avodah_Zarah.8a` et `Shulchan_Arukh,_Orach_Chayim.116` ; la colonne `texte_trouve_en` du CSV
ne la trouve que dans des **siddourim** (Weekday Siddur Sefard Linear, Shemoneh Esrei) — c'est
une חתימה liturgique, pas une citation d'ouvrage.

## RECLASSEMENTS

### R1 — #13 et #14 (siman 128, l. 484 et 533) : famille 3 → **FAMILLE 2**

**Le mécanisme M1 ne peut pas produire ces deux cas, et le relevé le dit pourtant.** Le remède
que M1 invoque est `ref_du_siman(path)` ; pour un `niveau-2-lamdan.html` cette fonction rend
`Shulchan_Arukh,_Orach_Chayim.128` — **le Mehaber**, jamais le Choul'han Aroukh HaRav (seul
`niveau-4-daat-harav` y est mappé, cf. `scripts/verifier-citations.py:1731-1748`).

Mesuré : `יצאו ידי חובתן מן התורה` est **ABSENT du Mehaber du siman 128** — 0 consonne sur 19
dans `…128.1`, et absent des **45 segments** de `Shulchan_Arukh,_Orach_Chayim.128`. Il est
verbatim dans `Shulchan_Arukh_HaRav,_Orach_Chayim.128.1` :
`…ומשנשאו כפיהם וברכו פעם אחת ביום יצאו ידי חובתן מן התורה…`

Donc **lever le garde `ref_collee` ne rattraperait pas ces deux cas** : la porte a raison, et
l'adresse de la page est fausse. Elle l'est de façon notable : une page de **niveau 2** attribue
la formulation propre de l'**Admour HaZaken** (≈ 1800) à `כתובות כ״ד:, תוספות`. Vérifié absent
de `Ketubot.24b`, de `Tosafot_on_Ketubot.24b` **et** de `Rashi_on_Ketubot.24b`. La sugya de
`Ketubot.24b` est bien celle de la נשיאות כפים comme preuve de כהונה (`…מהו להעלות מנשיאות
כפים ליוחסין … נשיאות כפים דאיסור עשה…`) : la sugya est juste, les mots n'y sont pas.

→ **famille 3 : 15 → 13 · famille 2 : 9 → 11.**

### R2 — #20 (siman 29, l. 585) et #25 (siman 59, l. 513) : famille 2 → **famille 3**

Famille 2 veut dire « le texte existe, à une autre adresse ; donne l'adresse vraie ». Dans ces
deux cas **la page ne donne aucune adresse au verset** : la référence que la porte a retenue
ferme une clause voisine.
- siman 29 l. 585 : `<strong>שורש הדין — שבת אינה זמן תפילין (מנחות ל״ו:):</strong> … והשבת
  עצמה אות היא ("אות היא ביני וביניכם"). ודרשו חז״ל (מנחות ל״ו:): "יצאו שבתות…"`. Le premier
  `(מנחות ל״ו:)` est sur le **titre du din**, le second introduit une **autre** citation. Le
  verset n'a pas de référence propre.
- siman 59 l. 513 : `…ובערב שתים לפניה ושתים לאחריה (ברכות י״א:), וסמכום על "שבע ביום הללתיך"`.
  `(ברכות י״א:)` ferme le **dénombrement des sept berakhot** ; le verset suit comme אסמכתא.

C'est exactement la classe de **M6** du relevé (verset sans référence, la porte emprunte celle
du voisin, `RE_VERSET` muet). Les ranger en famille 2 affirme que la page a situé le texte
quelque part où il n'est pas : elle ne l'a pas situé du tout.

**Contre-épreuve, et elle tient dans l'autre sens :** #10 (siman 118) et #22-24 (siman 47) sont
**à bon droit** en famille 2, parce que le verset y est **à l'intérieur** de la parenthèse
ouverte par le daf — `(ברכות י״ב:, «מלך במשפט יעמיד ארץ»)`, `(נדרים פא. « על מה אבדה הארץ »)`.
Là, la page situe. Mesuré : `Proverbs.29.4` et `Jeremiah.9.11` portent les clauses ;
`Berakhot.12b` (3/16) et `Nedarim.81a` (0/12) non.

## ERREURS DU LOT (sans reclassement, mais à ne pas transmettre telles quelles)

### E1 — BLOQUANT POUR L'USAGE · M1 présente comme un oubli un garde **documenté comme voulu**

Le relevé écrit que « le repli est désactivé **exactement dans la mise en page où il serait
nécessaire** », et conclut à « un bruit de classe, pas sept accidents ». Il ne dit pas que les
quatre lignes de commentaire **juste au-dessus du garde** donnent la raison de l'auteur :

> « Le repli n'est tenté QUE si aucune référence talmudique ne colle à la citation : quand la
> page place elle-même « (ברכות כ״ב.) » juste après les guillemets, elle revendique ce folio,
> et l'écart doit ressortir — c'est le défaut relevé au siman 267. »

Le garde n'est donc pas une interaction malheureuse : c'est la **sémantique voulue**, motivée
par un défaut réel et nommé. Et la convention du dépôt lui donne raison : CLAUDE.md écrit
« Anything inside quotes must exist word-for-word in the cited source or the gate fails ».
La question posée par les 7 cas — *une parenthèse collée après des guillemets revendique-t-elle
ce folio pour les mots cités ?* — est une **question de convention à arbitrer par un humain**,
pas un défaut de porte. Ces 7 verdicts appartiennent aux **non tranchés**, pas à la colonne des
faux positifs. (Les **faits** de la table M1 sont justes : j'ai confirmé #2 `SA 108:1`,
#5 `SA 111:1`, #11 `SA 124:1`, #12 `SA 126:3`, #17 `SA 153:2` verbatim, et chacun absent du daf
revendiqué.)

### E2 — M2 nomme dans le code un mécanisme qui n'est pas celui qui agit

Le relevé écrit : « `REF_FAUSSE` est émis dès que `locate()` trouve une occurrence exacte
n'importe où, **SANS jamais revenir mesurer** ce que le folio revendiqué contient ». **La porte
mesure d'abord le folio revendiqué** : `v, ratio, extract = verdict(frag, segs)` où `segs` sont
les segments des refs revendiquées, et la ligne 1926 `v = 'REF_FAUSSE' if found else
'INTROUVABLE'` n'est atteinte **que si** ce `verdict` a rendu `ABSENT`. Le CSV imprime même le
ratio contre le folio revendiqué : **0,62** pour #3/#4.

Le vrai mécanisme est ailleurs, et il est plus instructif : les deux portes de `VARIANTE` de
`verdict()` n'ont pas déclenché. `SEUIL_VARIANTE = 0.86` (0,62 est loin dessous) et
`MIN_MOTS_SUIVIS = 3`, alors que `צרכי עמך מרובים` ne partage que **deux** mots consécutifs avec
`צרכי עמך ישראל מרובין`. **Une citation de trois mots dont un est élidé au milieu passe sous les
deux seuils** — c'est une sensibilité aux citations courtes, pas une escalade sans mesure. De
même, « la porte sait étiqueter très proche et ne s'en sert pas » : elle s'en sert, elle n'a pas
déclenché.

Et sur le fond, #3/#4 ne sont pas des faux positifs propres : la page imprime
`«צרכי עמך מרובים»` avec `(ברכות כ״ט:)` **collé après**, et `Berakhot.29b` dit
`צרכי עמך ישראל מרובין`. Le corps du relevé nomme lui-même l'élision sans « … » ; l'étiquette
famille 3 (« la citation est bonne et la porte se trompe ») contredit son propre corps. Le
verdict juste est **« gravité trop haute »**, pas « citation bonne ».

### E3 — M3 : chiffres faux, et le garde est là aussi délibéré

Le relevé parle d'une fenêtre « 30 caractères avant / 60 après ». `FENETRE_REF = 200`
(l. 126). La cause opérante est autre : `fenetre_ref()` **coupe la fenêtre arrière au `»`
précédent** (l. 931-936, avec son commentaire motivant). Sur siman 107 l. 542, la citation
`«ולואי שיתפלל…»` est précédée d'une **autre citation fermée** (`«ספק התפלל ספק לא התפלל»`) :
la fenêtre est tronquée juste après elle, et `ברכות כ״א.`, qui est **avant** cette première
citation, devient inatteignable. Les chiffres 30/60 existent bien dans le fichier, mais dans un
autre bloc (l. 1907-1908, le garde `RE_VERSET`), qui n'a pas produit ce verdict. Le mécanisme
est réel ; **l'explication donnée n'est pas la bonne** — et le mandat dit qu'un mécanisme nommé
sans être montré ne compte pas.

### E4 — #8 (siman 115 l. 608) rangé en faux positif alors que le corps du relevé concède le défaut

Le `h2` ne porte que `«אם אין דעה הבדלה מנין» (ברכות ל״ג.)`. Mesuré : absent de `Berakhot.33a`
(0/17) ; verbatim au `Jerusalem_Talmud_Berakhot.5.2`. La défense du relevé — l'attribution juste
est au corps (l. 617 `ובירושלמי (ברכות פרק ה׳)`) et au `yesod-box` (l. 638 `(ירושלמי)`), que
j'ai tous deux vérifiés — est une atténuation **réelle**, mais c'est le critère
« le lecteur l'a sous les yeux » que CLAUDE.md pose pour les **troncatures**, transposé à une
autre porte. Un titre de section qui ne nomme qu'un folio revendique ce folio. À mettre en
**non tranché**, non en famille 3 avec une note de bas de page.

## Ce qu'il a tu

1. **Les commentaires du code qui rendent les gardes de M1 et M3 délibérés** (E1, E3). Six
   mécanismes sont présentés comme six défaillances ; au moins deux sont des **décisions
   documentées**, dont une nomme le défaut qu'elle protège (siman 267).
2. **Que le mécanisme de M2 n'est pas celui qui agit** (E2) — et le ratio 0,62, présent dans le
   CSV qu'il a lu, suffisait à le voir.
3. **Que son bucket « famille 2 mineur » mélange deux choses** : des versets que la page situe
   réellement à un daf (#10, #22-24) et des versets auxquels la page ne donne **aucune** adresse
   (#20, #25). Deux défauts sur-déclarés d'un côté (R2), deux sous-déclarés de l'autre (R1,
   #13/#14) : le total de famille 2 bouge à peine — **9 annoncés, 11 réels** — et cette
   quasi-compensation est précisément ce qui cache les deux erreurs.
4. **« 15 faux positifs » est un PLAFOND annoncé comme un compte.** C'est l'erreur de ce dépôt
   retournée : non pas un plancher pris pour un total, mais un total gonflé. Après arbitrage :
   **4 faux positifs de classe établis** (#7, #6, #15, #21) + 2 de gravité (#3, #4) + 1 de
   fenêtre (#1) ; **7 cas (M1) qui relèvent d'une question de convention non tranchée**, et
   **2 qui sont des défauts de page** (#13, #14).

## Compte final après arbitrage

| famille | annoncé | après arbitrage |
|---|---|---|
| 1 — fabrication réelle | 0 | **0** (vérifié indépendamment) |
| 2 — citation réelle mal adressée | 9 | **11** (+#13, +#14 · −#20, −#25) |
| 3 — faux positif de la porte | 15 | **7** (4 de classe, 2 de gravité, 1 de fenêtre) + #20, #25 = **9** |
| 4 — hors convention | 1 | **1** (fondé) |
| non tranchés | 0 | **8** (les 7 de M1 + #8) |

## Ce que je n'ai PAS fait

1. **Aucune page de `sources/` modifiée**, aucun `git add`, aucun commit, aucun fichier écrit
   hors de ce relevé et de mon scratchpad. `git status` le montre : `sources/` intact.
2. **`verifier-citations.py` non lancé.** Vérification du périmètre du lot A sur le cache
   partagé : les entrées de `scripts/.cache-sefaria` écrites **après** le CSV (14:53) le sont
   à 15:36-15:51 et sont **toutes de Yoré Déa / Nidda** — aucune de la tranche A. Et aucune des
   références que seule l'enquête de A exigeait (`Megillah 9b`, `Jerusalem Talmud Berakhot 1:5`
   et `5:2`, `Psalms 119:164`, `Jeremiah 9:11`, `Isaiah 6:3`, `Ecclesiastes 3:19`,
   `Proverbs 29:4`, `Exodus 31:13`, `Shulchan Arukh HaRav OH 128:1`) n'y figure. **Son cache
   privé est corroboré.** Le commit `265b778a` de 16:27 appartient au lot INTROUVABLE et n'a
   pas emporté ce fichier.
3. **Je n'ai pas tranché la question de convention de M1.** Elle n'est pas mécanique : elle
   demande une décision éditoriale sur ce qu'une parenthèse collée après des guillemets
   revendique, dans un item de sommaire et un `h2.section-title`. Je l'ai sortie de la colonne
   des faux positifs ; je ne l'ai pas résolue.
4. **Je n'ai pas rouvert les 6 cas de M1 un par un côté « est-ce la bonne sugya ? »** — j'ai
   seulement vérifié que le texte est au siman de la page et absent du daf.
5. **Je n'ai pas corrigé la porte**, ni touché à `scripts/`.
6. **Je n'ai pas examiné les lots B et C**, ni les INTROUVABLE, NON_RESOLU ou VARIANTE. J'ai
   seulement lu l'entête de B pour éprouver la frontière des tranches.
7. **L'étendue trilingue n'est pas chiffrée par moi non plus.** La réserve du lot (§4 de son
   « non fait ») reste entière, et elle est juste : le CSV ne voit que le français.
