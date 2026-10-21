# Cahier des charges — production d'Orah Haïm 366 et suivants (Hilkhot Érouvin 366-395, Hilkhot Te'houmin 396-407)

Ce fichier est le brief remis à chaque agent qui écrit un siman 366+ de A à Z, sur le modèle
de Hilkhot Chabbat : 15 fichiers par siman, niveau 4 sur le Choul'han Aroukh HaRav.
Il a été établi le 20 octobre 2026 à partir des 15 fichiers des simanim 360-365 (le dernier
lot de Chabbat), de 268 et 350 (deux pages corrigées), des portes de `scripts/`, des messages
de commit des lots Chabbat (`git log -- sources/shabbat`), de `audit/` (GUIDE-CORRECTIONS.md,
erreurs-recurrentes.md, relecture-rav.md, niv4-chabbat-urgent/decisions.md) et de
`docs/brief-yoreh-deah.md`. Chaque règle dit d'où elle vient : c'est ce qui permet de la
retrouver et de la défendre.

`CLAUDE.md` prime sur ce fichier. En cas de contradiction, suivre `CLAUDE.md` et le signaler.

## ⚠️ LA RÈGLE QUI COMMANDE TOUTES LES AUTRES — VÉRIFIER AVANT, NE PAS CORRIGER APRÈS

Décision de l'utilisateur, 20 octobre 2026 : *« Il faut absolument vérifier qu'il n'y ait pas d'erreur,
plus que retravailler avec des audits ensuite. »* Les simanim 242-365 ont été publiés puis audités, et
l'audit a trouvé, des mois après, des conduites contraires à la source sur des pages déjà lues (257, 261,
268, 278, 279 : `audit/niv4-chabbat-urgent/`). On ne refait pas ce chemin. Concrètement :

1. **Rien n'est écrit qui ne s'appuie sur un passage précis de la source.** Chaque affirmation
   halakhique — traduction, explication, encadré, synthèse, « למעשה » — nomme son séif (ou son ס״ק, sa
   page de guemara), et ce séif la porte. Sinon elle n'est pas écrite. Pas de « hidoush » que la
   comparaison du Rav et du Mehaber ne montre pas ; pas de formule absolue ; pas d'énumération fermée.
2. **Aucun mot d'hébreu n'est retapé** : `scripts/sefaria-extrait.py` rend la chaîne exacte de Sefaria
   (séif entier, ou extrait retrouvé au squelette consonantique), ou échoue (règle 29).
3. **Un siman ne sort que vérifié** : toutes les portes de la section 11, puis des vérificateurs adverses
   qui relisent la SOURCE (pas seulement les citations) niveau par niveau, puis un contrôle de cohérence
   entre l'index et les quatre niveaux — c'est dans la synthèse que sont nées toutes les erreurs
   trouvées jusqu'ici. Chaque objection est arbitrée contre la source ; après correction, on vérifie de
   nouveau, jusqu'à une passe qui ne trouve plus rien. **Un siman sur lequel un doute reste n'est pas
   publié** : il attend, avec sa question écrite pour le Rav.
4. **Des lots petits** (4 à 6 simanim), pour que chacun soit lu en entier.

## 0-bis. DÉCISIONS PRISES (20 octobre 2026)

- Emplacement `sources/shabbat/siman-N/`, URL `/oh/N/` (0.1 ci-dessous) — aucune règle `vercel.json` à ajouter.
- Libellés de section : FR « Hilkhot Érouvin » (366-395) et « Hilkhot Te'houmin » (396-407), HE « הלכות עירובין »
  et « הלכות תחומין », EN « Hilchos Eruvin » et « Hilchos Techumin » ; clés de catalogue `eruvin` et `techumin`.
  **Ne jamais écrire que le 366 « ouvre » Hilkhot Érouvin** : l'index de Sefaria fait commencer הלכות עירובין au
  siman 345. Un libellé de section n'est pas une affirmation sur la découpe du livre.
- Kountress Aharon : Sefaria n'en sert aucun sur 366-407 ; l'accordéon vide est retiré et la phrase
  « Sefaria ne donne aucune entrée de Kountress Aharon pour ce siman » le remplace (8.3).
- Tableau « כח הפסק / force du psak » : absent (8.1).
- Les citations de guemara se référencent en hébreu, `(עירובין צ״ח ע״ב)` : les formes latines accentuées
  (« Érouvin 20a ») ne sont pas encore rattachées à leur folio par `verifier-citations.py`.

## 0-ter. GABARIT ARRÊTÉ SUR LE PREMIER LOT (366-369, 21 octobre 2026)

Le premier lot a été écrit siman par siman, et ses choix de forme ont divergé ; il a fallu une passe
d'harmonisation, puis une nouvelle série de vérification. Les choix ci-dessous sont arrêtés : les
appliquer dès l'écriture. La charpente reste celle de 365 (CSS figé du niveau 4 compris) ; pour la
forme de ce qui suit, prendre modèle sur `sources/shabbat/siman-366/` (siman à plusieurs séifs) ou
`siman-369/` (séif unique).

- **Section 2 du niveau 4 — libellé neutre**, et non « חידוש » ni « תוספות » : `section-num`
  « 2 · לשון הרב ולשון המחבר » (FR et HE), EN « 2 · The Rav's text and the Mechaber's » ; h2 hébreu
  « לשון הרב מול סעיף המחבר » (« … והרמ״א » quand le siman a une glose du Rama) ; h2 de la langue
  de la page : FR « Où le texte du Rav diffère du séif du Mehaber [et du Rama] », HE « במה שונה לשון
  הרב מסעיף המחבר [והרמ״א] », EN « Where the Rav's text differs from the Mechaber's seif [and the
  Rema's] ». La meta description et la phrase d'introduction de la page disent « ce en quoi le texte
  du Rav diffère » / « במה שונה לשון הרב » / « where the Rav's text differs ». Raison : « תוספות » se
  lit comme les Tossafot (le 369 les cite dans cette section), et « ajoute » ne couvre pas un point où
  le Rav OMET ce que le Mehaber écrit (369, point א). L'introduction de la section dit qu'un point
  relevé n'est pas propre au Rav pour autant, et nomme où il se lit déjà (Tour, Rachi, Magen Avraham,
  Taz…) ; quand des commentateurs lisent déjà le point dans les mots du Mehaber, elle le dit.
- Blocs de la section 2 : « נקודה א/ב/ג — … » (HE), « Point א/ב/ג — … » (FR, EN), adresse du seul séif
  du Rav dans le titre : HE « (שו״ע הרב שס״ו:ג) », FR « (Choulhan Aroukh HaRav 366:3) », EN « (Shulchan
  Aruch HaRav 366:3) ». Étiquettes : « Ce qu'écrit le Mehaber : », « Ce qu'écrit le Rav : » (HE « דברי
  המחבר: », « דברי הרב: » ; EN « What the Mechaber writes: », « What the Rav writes: »).
- Nœud Organization du JSON-LD : logo `https://daattorah.com/assets/img/og/og-default.svg`, description,
  `jobTitle` et `educationalRole` dans la langue de la page.
- Renvoi au Rav : FR « consulte ton Rav », HE « היעזר ברב שלך », EN « consult your Rav ». Fin du
  récapitulatif du niveau 2 : « Pour la halakha lema'asseh, consulte ton Rav ; l'usage de la communauté
  compte aussi. » (HE « להלכה למעשה, היעזר ברב שלך; גם מנהג הקהילה קובע. » ; EN « For halachah
  lema'aseh, consult your Rav; the custom of the community also counts. »).
- h1 du niveau 1 qui nomme son ouvrage (« 15 séifim du Choulhan Aroukh ») ; ligne de couverture du
  niveau 3 « N séifim dans le Choulhan Aroukh, M dans le Choulhan Aroukh HaRav ».
- Section 4 du niveau 4 : un usage que le Rav rapporte « בִּזְמַן הַזֶּה » se rapporte à SON temps (« le
  Rav écrit que l'usage, de son temps, est… »), jamais au présent comme conduite Habad d'aujourd'hui.
- Ce que fait le coordinateur, pas l'agent (0.3) : carte du catalogue (section `#hilkhot-eruvin`),
  « suivant » du siman précédent, `siman-nav.js`, `data/simanim/siman-N.json`, image de partage,
  `index.md`, `llms.txt`.

**Les défauts que la vérification adverse a trouvés sur 366-369, toutes portes vertes** — près de
quatre cents corrections en trois séries (`audit/oh-366-369/decisions-N.md`). Aucun n'était une citation
fausse : tous étaient dans ce que la page DIT des citations. Les chercher soi-même avant de rendre :

1. **Le degré durci ou affaibli** : « צריך ליזהר » rendu « interdit » ; « וטוב לחוש » ou « לכתחלה טוב לחוש…
   היכא דאפשר » rendu « le Mehaber demande » ; « יש להקל », « יש לסמוך » rendus « on allège », « סומכים » ;
   une faculté (« יכול לערב ») devenue une conduite (« fait l'érouv ») ; « אסור » et un doute du Peri
   Megadim confondus dans un même degré.
2. **La condition perdue dans les résumés** : la mesure (« ובלבד שיהא בהם כשיעור ») absente de quatre
   résumés du même séif ; « מִשֶּׁלּוֹ » tombé d'une conduite ; « היכא דאפשר » omis. Une condition se
   cherche dans TOUS les endroits où le séif est résumé : index, encadrés, tableaux, arbres, pièges,
   commandements, למעשה.
3. **La raison proposée donnée pour établie** : « ונראה לי הטעם » du Rama rendu « il en donne la raison »,
   « parce que » ; « d'où », « hence », « ומכאן » qui fabriquent une causalité entre deux séifs.
4. **Le mauvais locuteur** : une hagaha sur le Smak attribuée au Beit Yossef, un Amora pour un autre, une
   parenthèse de Sefaria attribuée au Rama, l'avis du Ritva qui est celui de son maître.
5. **La liste fermée** : « gloses du Rama aux séifim ב, ג, ו… », « pain entier ou 'hala unique », « deux
   précisions », « ne convient que si » — et toujours fausses. Préférer « notamment ».
6. **Le rôle inversé** : מזכה rendu « acquires on behalf of » (confond le donneur et l'acquéreur), le fils
   qui « fait acquérir » au lieu d'acquérir.
7. **L'ordre** : concepts, tableaux, pièges et למעשה présentés dans un autre ordre que celui des séifs
   (règle du 243).
8. **La parité** : une citation présente en hébreu seulement, des ajouts explicatifs sans crochets en HE,
   des champs du JSON-LD ou un bouton restés en français sur les pages -he et -en, un menu qui renvoie à
   la page française.
9. **L'objet moderne** : « le quartier » pour ce que le Rama appelle la ville ou le mavoy.
10. **Le présent pour le passé** : « l'usage est… » quand le Rav écrit « בִּזְמַן הַזֶּה ».
11. **Une citation coupée avant ce qui la limite** : le Rama du shammash arrêté avant « ואדעתא דהכי נתנו
    קמחם מתחלה ».
12. **Le niveau 3 qui cite ce que les niveaux 1 et 4 ne portent pas** (des ס״ק de la Michna Beroura, le
    Biour Halakha) : la synthèse ne rapporte que ce qui est déjà dans la page.

---

## 0. AVANT DE COMMENCER — ce que le coordinateur doit avoir décidé et fait

Ces points ne relèvent pas de l'agent de production. S'ils ne sont pas faits, l'agent
s'arrête et le dit : sans eux ses pages ne sont confrontées par aucune porte, ou sont
servies sur une URL morte.

### 0.1 Emplacement et URL (décision recommandée)

- Répertoire : **`sources/shabbat/siman-N/`** (N = 366…407), à côté de 242-365.
- URL publiques : **`/oh/N/`**, `/oh/N/he`, `/oh/N/en`, `/oh/N/base|lamdan|synthese|daat-harav[/he|/en]`.
- Raison : `vercel.json` réécrit déjà `/oh/:n(\d+)…` vers `/sources/shabbat/siman-:n/…` pour
  tout nombre (règles `/oh/:n(\d+)`, `/oh/:n(\d+)/base`, etc.) — aucune règle à ajouter.
  `scripts/extract-corpus.js:30`, `scripts/verify-chabbat-source.py:337` (`SECTION =
  sources/shabbat`, `--tous` lit le disque, l.1610-1612) et `scripts/generate-simanim-index.js:24`
  trouvent les pages sans modification.
- Libellés de section (à valider par le coordinateur, puis à employer partout à l'identique) :
  FR « Hilkhot Érouvin » / « Hilkhot Te'houmin » · HE « הלכות עירובין » / « הלכות תחומין » ·
  EN « Hilchos Eruvin » / « Hilchos Techumin » (le site écrit « Hilchos Shabbos » en anglais).

### 0.2 Portes à étendre AVANT la production (sinon elles ne voient pas 366+)

> **Fait le 20 octobre 2026** (commit 834212272) : `verify-oh-source.py`, `verifier-apercus.py`, `audit-simanim.py`,
> `verifier-plan-limoud.py` lisent 366-407 ; le site connaît les sections `eruvin` et `techumin`. Reste au coordinateur,
> à la publication de chaque lot : `assets/js/siman-nav.js`, le « suivant » du siman précédent, `api/progress.js`
> (bornes 242-365), `scripts/extract-corpus.js` (clé de repli `dispoIds`), le catalogue statique `sources/shabbat/index*.html`,
> `data/simanim/siman-N.json`, l'image de partage, `data/seifim-count.json`, `llms.txt`, `sitemap.xml`. Le tableau ci-dessous
> est gardé pour mémoire.

| Fichier:ligne | Aujourd'hui | À écrire |
|---|---|---|
| `scripts/verify-oh-source.py:191` | `("shabbat", range(242, 366))` | `range(242, 408)` (ou la borne du lot) |
| `scripts/verify-oh-source.py:1541` | `nums = list(range(1, 366))` | `range(1, 408)` |
| `scripts/verify-oh-source.py:1598` et docstring l.6-7 | « (1-365) » | la nouvelle borne |
| `scripts/verifier-apercus.py` | lit `V.SECTIONS` (l.334, 339) | rien : suit `verify-oh-source.py` |
| `scripts/audit-simanim.py:27` et `:43` | `FIRST, LAST = 242, 365` / `range(242, 366)` | 407 / 408 |
| `assets/js/siman-nav.js:10` | `SIMANIM = [242, … 365]` | ajouter chaque siman publié |
| `scripts/fix-liens-morts.py:22` | `SHABBAT = set(range(242, 366))` | `range(242, 408)` |
| `scripts/add-niveau-nav.py:31`, `scripts/add-siman-suivant-button.py:19`, `scripts/add-internal-linking.py:289` | `LAST = 365` | seulement si on les emploie (on ne les emploie pas, voir 2.3) |

Sans le premier point, `verify-oh-source.py 366` imprime « hors des sections couvertes » et
le niveau 4 n'est confronté à rien ; `verifier-apercus.py` non plus.

### 0.3 À la charge du coordinateur après le lot (hors des 15 fichiers)

- Ajouter le lien « suivant » aux 15 fichiers du siman N-1 (pour 366 : les fichiers de 365,
  qui portent aujourd'hui `<span class="nav-spacer"></span>` à la place de `nav-next` dans les
  12 niveaux, et aucun `<a class="next">` dans `index*.html`, l.198-201). Forme exacte : celle
  de `sources/shabbat/siman-364/` (index l.198-201, `niveau-1-base-he.html:549-558`,
  `niveau-4-daat-harav-en.html:493-502`).
- `data/simanim/siman-N.json` (modèle `data/simanim/siman-365.json`, numberHe avec ״ et non `\"`) —
  `extract-corpus.js` (section `useMetaDir: true`) et `generate-og-image.js` le lisent.
- Images de partage : `node scripts/generate-og-image.js --siman N` puis `generate-og-image-png.js`
  (`assets/img/og/siman-N.svg|.png`, référencées par `og:image` et `twitter:image`).
- Catalogue `sources/shabbat/index*.html` (qui annonce « 242 à 365 », l.8, 21, 29, 48, 458),
  `data/simanim-disponibles*.json` (`npm run build`), `sitemap.xml` (`scripts/generate-sitemap.py`),
  `llms.txt`, `data/seifim-count.json` (`scripts/generer-seifim-count.py`), `index.md` du siman.
- Section du catalogue : `generate-simanim-index.js:24` range 366+ dans `shabbat` ; si l'on veut
  une section « eruvin » distincte, ajouter une fonction de section comme celle de `nida` (l.26-32)
  ET une entrée dans `generate-section-listings.js` (`ROUTE`, l.24 environ). Décision éditoriale.
- `CLAUDE.md` : les comptes « 124 simanim », « 242-365 » deviennent faux dès le premier siman publié.

---

## 1. LES SOURCES DE CE LOT, MESURÉES (Sefaria, 20 octobre 2026)

Re-mesurer avant d'écrire : ces chiffres sont un instantané, et Sefaria corrige son texte.

```
curl -s "https://www.sefaria.org/api/v3/texts/Shulchan_Arukh,_Orach_Chayim.N?version=hebrew%7Call"
curl -s "https://www.sefaria.org/api/v3/texts/Shulchan_Arukh_HaRav,_Orach_Chayim.N?version=hebrew%7Call"
curl -s "https://www.sefaria.org/api/texts/Kuntres_Acharon_on_Shulchan_Arukh_HaRav,_Orach_Chayim.N?context=0&pad=0"
curl -s "https://www.sefaria.org/api/texts/Mishnah_Berurah.N?context=0&pad=0"
```

Contrôler à chaque téléchargement que `ref` vaut exactement l'ouvrage ET le siman demandés
(brief Yoré Déa, « la forme d'URL qui rend l'œuvre entière » : `Mishnah_Berurah_on_Shulchan_Arukh,_Orach_Chayim.N`
rend le livre entier en HTTP 200 sans `error`).

| Siman | Mehaber (Maginei Eretz) | SA HaRav (Kehot vocalisée) | KA | MB ס״ק |
|---|---|---|---|---|
| 366 | 15 | 18 | 0 | 84 |
| 367 | 1 | 1 | 0 | |
| 368 | 5 | 4 | 0 | |
| 369 | 1 | 1 | 0 | |
| 370 | 8 | 10 | 0 | |
| 371 | 6 | 6 | 0 | |
| 372 | 19 | 22 | 0 | |
| 373 | 1 | 1 | 0 | |
| 374 | 4 | 4 | 0 | |
| 375 | 4 | 5 | 0 | |
| 376 | 4 | 4 | 0 | |
| 377 | 1 | 1 | 0 | |
| 378 | 5 | 5 | 0 | |
| 379 | 2 | 2 | 0 | |
| 380 | 4 | 7 | 0 | |
| 381 | 7 | 7 | 0 | |
| 382 | 20 | 23 | 0 | |
| 383 | 1 | 3 | 0 | |
| 384 | 2 | 1 | 0 | |
| 385 | 4 | 4 | 0 | |
| 386 | 9 | 9 | 0 | |
| 387 | 1 | 2 | 0 | |
| 388 | 1 | 1 | 0 | |
| 389 | 1 | 1 | 0 | |
| 390 | 2 | 2 | 0 | |
| 391 | 2 | 3 | 0 | |
| 392 | 8 | 9 | 0 | |
| 393 | 3 | 3 | 0 | |
| 394 | 3 | 3 | 0 | |
| 395 | 1 | 1 | 0 | |
| 396 | 2 | 4 | 0 | |
| 397 | 18 | 20 | 0 | |
| 398 | 11 | 14 | 0 | |
| 399 | 11 | 15 | 0 | |
| 400 | 1 | 1 | 0 | |
| 401 | 1 | 2 | 0 | |
| 402 | 1 | 2 | 0 | |
| 403 | 1 | 1 | 0 | |
| 404 | 1 | 4 | 0 | |
| 405 | 9 | 9 | 0 | |
| 406 | 1 | 3 | 0 | |
| 407 | 3 | 3 | 0 | |

(MB : la colonne n'est remplie que pour 366 ; le nombre se mesure par `len(d['he'])` — règle 22-bis.)

Ce que ce tableau impose :

1. **Aucune lacune du SA HaRav sur 366-407** : les 42 simanim sont servis (chapeau « ובו … סעיפים »
   concordant avec le nombre de segments). Pas de page-pont. Le vérifier quand même siman par
   siman (`CLAUDE.md`, « Lacune du Choul'han Aroukh HaRav ») ; si `he` est vide, s'arrêter.
2. **Deux comptes différents, presque partout.** Le Mehaber (niveaux 1-3) et le SA HaRav
   (niveau 4) n'ont pas le même nombre de séifim (366 : 15 et 18 ; 383 : 1 et 3 ; 384 : 2 et 1).
   C'est le « pattern #7 » de `audit/erreurs-recurrentes.md` : l'index du 365 lui-même écrit
   « 10 seifim » (SA HaRav) en tête de page (index.html:8, 147, 193) quand ses niveaux 1-3 en
   étudient 8. Sur toute page, **nommer l'ouvrage à côté du compte** (« 15 séifim du
   Choul'han Aroukh, 18 dans le Choul'han Aroukh HaRav »).
3. **Aucun Kountress Aharon servi par Sefaria sur 366-407** (`he: []` sans `error`). Ce n'est
   pas une preuve que l'Admour HaZaken n'en a pas écrit (règle 37 du brief Yoré Déa). Écrire
   « Sefaria ne donne aucune entrée de Kountress Aharon pour ce siman », jamais « il n'y en a
   pas ». Voir 7.6 pour l'accordéon.
4. **Mishna Beroura** : aucune פתיחה non numérotée sur 366-407 (première entrée « (א) » partout,
   mesuré) — l'index du segment est le ס״ק. Re-mesurer si un siman fait exception.
5. **Le texte de Kehot contient des appels de note** `<i data-commentator="Notes" data-label="…"></i>`
   (2 118 sur le lot) : les retirer **sans laisser d'espace** (c'est ce que fait
   `texte_source()` de `verify-oh-source.py`). Balises vues : `i`, `b`, `br`, et **une seule
   fois `<sup>*</sup><i class="footnote">…</i>`, au SA HaRav 398:4** — une note du Rav insérée
   dans le texte. Dans `.sa-he` ne sont admises que `br b small img` (`verify-oh-source.py:199`)
   et le caractère `*` n'est pas admis (l.198) : rendre la note dans `<small>…</small>` à sa
   place, sans l'astérisque, et faire valider ce premier cas par la porte ET par le coordinateur.
6. **Chapeaux du SA HaRav à recopier** (en tête du séif 1 du niveau 4) — exemple 366 :
   « דִּין עֵרוּב לְחָצֵר שֶׁהַרְבֵּה בְּנֵי אָדָם דָּרִים בְּתוֹכוֹ וּבוֹ י״ח סְעִיפִים: ». 393 porte un crochet
   d'édition « עֵרוּב [בְּ]יוֹם טוֹב » : se recopie tel quel (les crochets sont admis et retirés à la
   comparaison, `verify-oh-source.py:194`).

---

## 2. LES 15 FICHIERS ET LEURS GABARITS

### 2.1 Quels fichiers copier

Toujours copier le fichier **de la même langue et du même niveau**, puis remplacer le contenu.
Ne jamais dériver le HE ou l'EN du FR par édition : les CSS diffèrent (RTL, polices, bordures).

| Fichier à produire | Gabarit à copier | Pourquoi celui-là |
|---|---|---|
| `index.html`, `index-he.html`, `index-en.html` | `sources/shabbat/siman-365/index{,-he,-en}.html` | charpente actuelle (canonical `/oh/N/`, PWA, lang-switcher) |
| `niveau-1-base{,-he,-en}.html` | `sources/shabbat/siman-365/niveau-1-base{,-he,-en}.html` | conforme à toutes les portes ; encadrés « Ce que dit ce séif » en he-q |
| `niveau-2-lamdan.html`, `niveau-2-lamdan-en.html` | `sources/shabbat/siman-350/niveau-2-lamdan{,-en}.html` | **corps traduit** (français 85 % / anglais), `dir="ltr"`, citations «&nbsp;he-q&nbsp;» + `source-ref` |
| `niveau-2-lamdan-he.html` | `sources/shabbat/siman-350/niveau-2-lamdan-he.html` | même structure que FR/EN de 350 |
| `niveau-3-synthese{,-he,-en}.html` | `sources/shabbat/siman-365/niveau-3-synthese{,-he,-en}.html` | charpente et classes (`axiome`, `schema`, `mnemonic`, `warning`, `pesak-box`) |
| `niveau-4-daat-harav{,-he,-en}.html` | `sources/shabbat/siman-365/niveau-4-daat-harav{,-he,-en}.html` | CSS **figé** et admis (voir 7.1) |
| contenu des sections 2-4 du niveau 4 | `sources/shabbat/siman-268/niveau-4-daat-harav*.html` (section « 4 · למעשה ») | corrigé le 20 octobre 2026 sur décision du Rav : renvois de séif exacts, verbatim court vocalisé |

**Ne pas prendre le niveau 2 de 360-365 pour modèle.** Mesuré : le corps de
`siman-365/niveau-2-lamdan.html` est à 99 % hébreu sous `lang="fr" dir="rtl"`, c'est la page
hébraïque à quelques mots près (« מקורות talmudiques », « 40 entrées » au lieu de « 40 ס״ק »,
l.25 et 34) ; il en va de même pour 300, 345, 355, 358 et 360-364. `verifier-url-langue.py` ne
le voit pas, parce que les liens `intra-ref` injectés diffèrent d'un fichier à l'autre. Et ses
citations sont entre guillemets droits sans formule d'annonce reconnue : `verifier-citations.py
--path sources/shabbat/siman-365` en confronte **0** (une citation examinée sur cinq pages),
alors que la citation de la Michna Beroura ס״ק ב (niveau-2-lamdan.html, section 2, « שלא
אמרו שיעור אורך מבוי ד' אמות … ») n'est pas le texte du ס״ק ב (qui lit « שעדיין נשאר שיעור
חשוב במבוי … אבל כאן שכבר היה מבוי אלא שנסתר די בארבעה טפחים »). Le 350, lui, rend
10 citations confrontées, 10 conformes, dans les trois langues.

**Ne pas prendre les sections 2-4 du niveau 4 de 365 (ni de 301) pour modèle de contenu.**
365 FR l.518-531 et 561-567 : un « hidoush » générique (« lavoud répare partiellement »), des
renvois par plages (« שס״ה:1-5 », « 6-10 »), un item qui n'est pas une conduite (« ④ Hilkhot
Shabbat conclus »). 301 attribue au Rav « montre = OK, lunettes = OK ». C'est exactement le
« pattern #1 » de `audit/erreurs-recurrentes.md`. On garde la charpente, on réécrit le fond
sur le modèle de 268.

### 2.2 Méthode de copie

1. `cp` des 15 gabarits dans `sources/shabbat/siman-N/` (en lecture seule tant que le coordinateur
   n'a pas ouvert le chantier ; sinon dans le scratchpad).
2. Remplacer les points d'ancrage numériques **à la main ou par un script relu**, jamais par un
   `sed s/365/N/` aveugle : 365 apparaît 19 à 54 fois par fichier, dans des URL, des `@id`, des
   titres, du texte ; « 364 » (lien précédent) devient N-1 ; « שס״ה » devient le numéral de N ;
   les comptes « 8 » / « 10 » (seifim) apparaissent jusqu'à 9 fois par fichier
   (index.html : 9) et doivent tous être recalculés.
3. Supprimer tout ce qui est propre à 365 : « dernier siman de Hilkhot Shabbat », « le siman 366
   ouvrant déjà Hilkhot Érouvin » (niveau-1-base.html:467), les comptes de la Michna Beroura
   (« 40 entrées »), etc. Puis chercher les résidus (voir 9.2).

### 2.3 Ce qu'il ne faut PAS employer

- `scripts/generate-siman.js` : **périmé**. Il écrit `canonical`/`og:url` en
  `/sources/shabbat/siman-N/` (l.70, 147), un fil d'Ariane vers `/sources/shabbat/` (l.95, 202,
  212) — URL qui sont aujourd'hui des redirections 301 —, et ne produit ni les variantes HE/EN
  ni le lang-switcher. CLAUDE.md le présente encore comme le générateur d'index : ne pas le suivre.
- `scripts/generate-niveau-4.py` et `scripts/generate-niveaux-123.py` : ce sont eux qui ont laissé
  dans 242-365 les placeholders « Position classique : — » et le préfixe « outil : / כלי: / tool: »
  relevés dans presque chaque siman de `audit/relecture-rav.md` (340-361), et le boilerplate que
  `audit-simanim.py` refuse (`BP_N1 = "Traduction structurelle"`, l.64-68).
- `scripts/add-intra-links.py` : il injecte des `<a class="intra-ref">` au milieu des mots
  (`siman-365/niveau-2-lamdan-he.html` : « <a …>הוכשר</a>הּ », « <a …>בראש</a>ו »), sur des mots
  vides (« Hilkhot » renvoyant à « Place dans Hilkhot Shabbat », niveau-1-base.html:315 et 348) et
  jusque dans un texte source (`audit/relecture-rav.md`, siman 357 : « l'auto-linker injecte un
  hyperlien à l'intérieur du texte sacré reproduit »). Ne pas le lancer. Garder en revanche
  `<link rel="stylesheet" href="/assets/css/intra-links.css">` et
  `<script src="/assets/js/intra-links.js" defer></script>` (admis, inoffensifs).

---

## 3. LA CHARPENTE COMMUNE (les 15 fichiers)

### 3.1 Langue et direction

| Variante | `<html>` | Exemple |
|---|---|---|
| FR `X.html` | `<html lang="fr" dir="ltr">` (index : `<html lang="fr">`) | niveau-1-base.html:2 |
| HE `X-he.html` | `<html lang="he" dir="rtl">` | niveau-1-base-he.html:2 |
| EN `X-en.html` | `<html lang="en">` (N2 de 350 : `lang="en" dir="ltr"`) | niveau-1-base-en.html:2 |

Le niveau 2 FR est `dir="ltr"` (modèle 350), **pas** `dir="rtl"` comme 360-365.

### 3.2 URL — canonical, og:url, hreflang, JSON-LD

| Fichier | canonical = og:url = JSON-LD `url` |
|---|---|
| `index.html` / `-he` / `-en` | `https://daattorah.com/oh/N/` · `/oh/N/he` · `/oh/N/en` |
| `niveau-1-base*` | `/oh/N/base` · `/oh/N/base/he` · `/oh/N/base/en` |
| `niveau-2-lamdan*` | `/oh/N/lamdan` · `…/he` · `…/en` |
| `niveau-3-synthese*` | `/oh/N/synthese` · … |
| `niveau-4-daat-harav*` | `/oh/N/daat-harav` · … |

- Quatre `<link rel="alternate" hreflang>` par page : `fr`, `en`, `he`, `x-default` (= FR), sur
  le modèle de niveau-1-base.html:10-13.
- `canonical == og:url` (clause de vérification de `CLAUDE.md`) ; JSON-LD `@id` = URL + `#article`.
- `og:image` / `twitter:image` : `https://daattorah.com/assets/img/og/siman-N.png`.
- `og:locale` : `fr_FR` · `he_IL` · `en_US` ; JSON-LD `inLanguage` : `fr-FR` · `he-IL` · `en-US`.
- `datePublished` / `dateModified` : les vraies dates (le gabarit porte `2026-01-01` /
  `2026-06-10`, niveau-1-base.html:212-213 — ne pas les recopier).
- Liens internes **toujours sous la forme `/oh/…`** et **dans la langue de la page**
  (`/oh/N/base/he` depuis une page -he). Le niveau 2 de 365 emploie encore des liens relatifs
  `../siman-364/niveau-2-lamdan.html` dans sa `niveau-nav` : ne pas les recopier
  (`verifier-liens-langue.py`, 1 841 liens fautifs à l'origine).

### 3.3 Titres et métadonnées

- `<title>` : jamais de balise (pas de `<bdi>` : 784 titres de Chabbat affichaient leurs balises,
  commit 15a930fd7). Formes du gabarit :
  FR `Siman שס״ו · Niveau 1 — <sujet> | Hilkhot Érouvin` ·
  HE `סימן שס״ו · רמה 1 — <נושא> · הקדמה לימודית | דעת` ·
  EN `Siman שס״ו · Level 1 — <subject> | Hilchos Eruvin`.
- `<title>`, `<h1>`, `og:title`, `twitter:title`, `headline` dans la langue de la page
  (règle 34 Yoré Déa ; `verifier-langues.py` lit l'entête).
- `meta description`, `og:description`, `twitter:description`, JSON-LD : **aucun balisage**
  (règle 27-bis), **aucun `"` ASCII** (gershayim ״ : 1 093 fichiers cassés à l'origine,
  `audit/erreurs-recurrentes.md` pattern #4), **jamais tronqués en plein mot** (sous-titres de
  340, 345, 346, 352, 358 coupés « chev », « הוצ », « glissen », « purement u » : le sous-titre
  vient de `data/simanim/siman-N.json` et se propage au hero, aux meta, au JSON-LD).
- `meta author` : « Rav Yossef Haim Samama » (FR/EN), « רב יוסף חיים סממה » (HE).
- Le JSON-LD doit parser (`python3 -c "import json…"` sur chaque bloc) après conversion des gershayim.

### 3.4 Navigation

- Index : `<header class="daat-header">` + `<nav class="daat-nav">` + `<span class="lang-switcher">`
  (index.html:119-129), fil d'Ariane `daat-breadcrumb` (l.131-139), `daat-hero` (l.141-149),
  quatre `article.daat-level-card` (l.158-196), `nav.siman-neighbors` (l.198-201).
- Niveaux 1-3 : `div.lang-switcher-float` (niveau-1-base.html:293) et `nav.niveau-nav`
  (l.600-609) : `nav-prev` · `nav-niveaux` (N1-N4, la courante en `active`) · `nav-next`.
  Pour le dernier siman publié : `<span class="nav-spacer"></span>` à la place de `nav-next`.
- Niveau 4 : `header` + `nav` + `lang-switcher` (niveau-4-daat-harav.html:325-336), `breadcrumb`
  (l.338-348), `page-hero` (l.350-357), `niveau-nav` (l.575-584).
- **Flèches hébraïques** : copier exactement la forme de `siman-364/niveau-1-base-he.html:550,557`
  (« סימן שס״ג · 363 → » en tête, « ← סימן שס״ה · 365 » en fin) et de `siman-364/index-he.html:200-201`.
  C'est la convention d'Orah Haïm ; elle est l'inverse de celle de Yoré Déa (règle 35) — ne
  « corriger » ni l'une ni l'autre.
- Le libellé « Hilkhot Shabbat » du menu, du fil d'Ariane, du `daat-hero-meta` (index.html:125,
  135, 144), du JSON-LD BreadcrumbList (« Orah Haïm — Hilkhot Shabbat ») et des mots-clés devient
  le libellé de section décidé en 0.1. Le lien reste `/oh/` (`/oh/he`, `/oh/en`).

### 3.5 Pied de page et scripts (identiques au gabarit, ne rien ajouter)

Scripts admis par la porte du niveau 4 (`verify-oh-source.py`, `SCRIPTS_ADMIS`) et présents
dans tous les gabarits : `/assets/js/dedicace-banner.js`, `/assets/js/daat-copy.js`,
`/assets/js/share-text.js`, `/assets/js/pwa.js`, `/_vercel/insights/script.js`,
`../../../assets/js/chat-loader.js` (précédé de `window.DAAT_CHAT_API_URL = 'https://daatai.vercel.app/api/chat';`),
`../../../assets/js/daat-progress.js`, `/assets/js/siman-nav.js`, `/assets/js/intra-links.js`.
Bloc PWA (`manifest`, `theme-color #1A1F3A`, `apple-touch-icon`…) à l'identique.
Bouton `print-btn` avec son `<style>@media print {…}</style>` à l'identique.

---

## 4. INDEX (index.html, index-he.html, index-en.html)

Gabarit : `siman-365/index*.html` (213 lignes environ). Rien n'y est verbatim : pas de bloc
`seif-text-he` dans les index de Chabbat (celui d'Orah Haïm quotidien en a un, lu par
`verifier-index-source.py`, `verifier-polarite-index.py`, `verifier-etiquettes-index.py` — ne pas
en ajouter).

- `daat-hero-siman` : `<span class="daat-hero-siman-he">סימן שס״ו</span><span class="daat-hero-siman-num">Siman 366</span>`.
- `daat-hero-title-he` : **le chapeau réel** du Mehaber, sans « ובו … סעיפים » (365 :
  « דִּין מָבוֹי שֶׁנִּפְרַץ » ; 366 : « דין עירוב לחצר שהרבה בני אדם דרים בו »). Ne pas inventer
  de titre (règle 36).
- `h1.daat-hero-title-fr` : sujet dans la langue de la page (la classe garde le suffixe `-fr`
  même en HE et EN — c'est le gabarit).
- Les quatre cartes : textes du gabarit ; la carte N4 dit « Le Choulhan Aroukh de l'Admour HaZaken
  sur ce siman : 18 seifim. » — sans « et 0 KA » (voir 1.3).
- `description` / hero : les deux comptes nommés (1.2). Ne pas écrire « 10 seifim et 0 entrée(s) »
  (accord manqué, et compte du seul SA HaRav : `audit/relecture-rav.md`, 352, 356, 357, 360).
- HE : la page porte en plus `<style>body, .daat-body { font-family: 'Frank Ruhl Libre', serif; }</style>`
  (index-he.html:98) ; garder.

---

## 5. NIVEAU 1 — BASE (texte du Mehaber + Rama)

Gabarit : `siman-365/niveau-1-base{,-he,-en}.html`. Porte : `scripts/verify-chabbat-source.py N`
(texte, découpe, parité), `scripts/verifier-alignement.py`, `scripts/verifier-encadres.py`,
`scripts/verifier-couverture-encadres.py`.

### 5.1 Plan (titres exacts — l'indexeur du chat les reconnaît par leur libellé FR)

`extract-corpus.js:364` ignore le texte des sections dont le titre contient « Plan de l'étude »,
« Le texte du Choul'han Aroukh », « Mishnah Berurah — premières entrées », « Questions de
compréhension » (mais indexe leurs encadrés typés) ; `:386` découpe « Cas pratiques modernes »
ligne à ligne. Garder ces libellés au caractère près dans le FR.

| # | FR (niveau-1-base.html) | HE | EN |
|---|---|---|---|
| — | `📑 Plan de l'étude` (l.330) | `📑 תכנית הלימוד` | `📑 Study Plan` |
| 1 | `1. Le texte du Choul'han Aroukh` (l.346) | `1. טקסט השולחן ערוך` | `1. The Shulchan Aruch text` |
| 2 | `2. Le contexte général` (+ h3 « De quoi parle ce siman ? », « Place dans Hilkhot … ») | `2. הרקע הכללי` | `2. General context` |
| 3 | `3. Les concepts-clés halakhiques` | `3. מושגי היסוד ההלכתיים` | `3. Key halachic concepts` |
| 4 | `4. Le détail des seifim — un par un` | `4. פירוט הסעיפים — אחד אחד` | `4. Detail of the seifim — one by one` |
| 5 | `5. Le Mishnah Berurah — premières entrées` | `5. המשנה ברורה — ראשי פרקים` | `5. The Mishnah Berurah — first entries` |
| 6 | `6. La position du Rama` | `6. שיטת הרמ״א` | `6. Position of the Rema` |
| 7 | `7. Cas pratiques modernes` | `7. מקרים מעשיים מודרניים` | `7. Modern practical cases` |
| 8 | `8. Synthèse pratique du Siman` | `8. סיכום מעשי של הסימן` | `8. Practical synthesis of the Siman` |
| 9 | `9. Questions de compréhension` (+ h3 « Pour aller plus loin ») | `9. שאלות הבנה` | `9. Comprehension questions` |

Chaque `h2` a la classe `section-title` et un `id` (slug du titre).

### 5.2 Le bloc de chaque séif (section 1)

```html
<h4>Seif א</h4>                                   <!-- HE : <h4>סעיף א</h4> ; EN : <h4>Seif א</h4> -->
<blockquote class="text-source"><b>CHAPEAU. ובו טו סעיפים:</b><br>TEXTE DU SÉIF 1</blockquote>
<div class="translation"><strong>Traduction :</strong> …</div>   <!-- HE « ביאור: » · EN « Translation: » -->
<div class="key-point">
<strong>Ce que dit ce séif :</strong>                              <!-- HE « מה אומר הסעיף: » · EN « What this seif says: » -->
<ul class="compact">
  <li><strong>…</strong> — <span class="he-q">MOTS DU SÉIF, VERBATIM</span>.</li>
</ul>
</div>
```

- **Un `blockquote.text-source` par séif, ni plus ni moins** (découpe : `verify-chabbat-source.py`,
  invariant 2 ; règle absolue du 243 dans `CLAUDE.md`). Le séif d'un seul tenant, sur une ligne.
- **Le chapeau** se recopie en entier, en `<b>…</b><br>` en tête du séif 1, « ובו N סעיפים: »
  compris (niveau-1-base.html:351 ; règle 1-bis). Il est facultatif pour la porte mais c'est la
  forme du dépôt.
- **Le texte** : l'édition par défaut de Sefaria (Maginei Eretz), non vocalisée, consonnes
  identiques, ktiv de la source (règle 2), appels `<i data-commentator…></i>` retirés.
  `"` entre deux lettres hébraïques → ״ (`רה״ר`, `ג״ט`) ; l'apostrophe finale de Sefaria
  (`י'`, `אפי'`) reste telle quelle dans le blockquote, comme au 365 (l.351, 364).
  La Torat Emet 363 n'est admise que comme leçon alignée (R1-R4 de `CLAUDE.md`) : pour un bloc
  non vocalisé, recopier Maginei Eretz.
- **Le Rama** : sa glose reste à sa place dans le séif, dans le `<small>` que Sefaria lui donne,
  avec « הגה » et ses parenthèses de source (niveau-1-base.html:364 ; `<small>` est la forme
  majoritaire, `verifier-classes.py`). Une glose rendue à la taille du Mehaber est
  « indistinguable de la parole du Mehaber » (`CLAUDE.md`, verifier-classes).
- **HE et EN** portent le même texte source, octet pour octet (parité).
- **La traduction** suit l'ordre des propositions du séif ; tout ajout explicatif entre `[…]`.
  Pas de glose qui n'est ni dans l'hébreu ni signalée (343 : « comme le hamets à Pessah »
  inséré dans la traduction).
- **« Ce que dit ce séif »** : un encadré par séif, posé **après** le blockquote de son séif et
  avant le `h4` suivant (sa référence est sa place). Tout `he-q` et tout « … » qu'il contient doit
  se lire d'un seul tenant dans CE séif (`verifier-encadres.py`, TETES l.53, RE_HEQ l.63) :
  pas d'abréviation développée (`מרה״י` écrit « מרשות היחיד » : 18 fautes sur 351-360), pas de
  phrase de la Michna Beroura recousue aux mots du Mehaber (272). Une citation d'un autre
  ouvrage dans l'encadré se nomme expressément. Texte de plus de 40 caractères (sinon non indexé,
  `extract-corpus.js:369`).
- Ne pas recopier l'encadré « Texte intégral : ces 8 seifim constituent l'ensemble… »
  (niveau-1-base.html:443-445) posé **entre** le blockquote du séif ח et son « Ce que dit ce
  séif » : il s'interpose entre le séif et son encadré.

### 5.3 Les autres sections

- **2 et 3** : boîtes `definition` (indexées). Défaut du gabarit à ne pas recopier :
  niveau-1-base.html:462, `</p>` fermant sans `<p>` ouvrant dans la `div.definition`.
- **4** : tableau `<table><tr><th>Seif</th><th>Contenu</th></tr><tr><td><strong>א</strong></td><td>…</td></tr>…`
  — **une ligne par séif, dans l'ordre**, chaque ligne résumant CE séif (pattern #8 de
  `audit/erreurs-recurrentes.md` : 307, 310-317, tableaux qui attribuent à un séif le contenu
  d'un autre). Puis un `key-point` « Le cœur du siman ».
- **5** : `div.sacred-text he` avec les premières entrées de la Michna Beroura, **recopiées par
  programme depuis `Mishnah_Berurah.N`** (règle 29) : ces blocs ne sont confrontés par aucune
  porte (ni blockquote, ni guillemets). Le compte « compte N entrées » est un dénombrement :
  `len(d['he'])`, jamais de mémoire (283 annonçait 4 entrées pour 1 ; règle 22-bis).
- **6** : `div.remember` « Les gloses du Rama » — chaque glose avec son séif exact ; si le siman
  n'a aucune glose, le dire (349 promettait « ashkénaze vs séfarade » sur un siman sans הגה).
  Ligne Habad → renvoi au niveau 4.
- **7** : **le tableau des cas pratiques, au format exact que lit l'indexeur**
  (`extract-corpus.js:387`) :
  `<tr><td><strong>Situation</strong></td><td>Analyse (séif X)</td></tr>` — deux colonnes, la
  situation en `<strong>` seul dans la première cellule. Toute application moderne se dit
  « application du site » et se rattache à un séif nommé ; aucun objet moderne n'est attribué à
  la source (`audit/erreurs-recurrentes.md` 2b : RFID, LED, parapluie « sourcés » à des séifs ;
  décision du Rav sur 257 : l'aluminium « porte partout la mention application du site »).
- **8** : `key-point` « Les enseignements du Siman » (liste `ol`), terminée par « Pour la halakha
  lema'asseh, consulte ton Rav. »
- **9** : `question-box` — des questions **propres au siman**, pas les six questions génériques du
  gabarit (niveau-1-base.html:562-567).
- Fin : `div.yh-watermark` (l.584-590), styles et scripts du gabarit, `niveau-nav` (l.600-609).
- Optionnel (pilote, FR seul aujourd'hui) : ancres `<h4 id="seif-N">` et pastilles
  `seif-jump`/`seif-back` de `siman-358/niveau-1-base.html:185-191, 375` ; l'indexeur s'en sert
  (`nearestSeifAnchor`). Ne l'ajouter que si le coordinateur le demande, dans les trois langues.

---

## 6. NIVEAU 2 — LAMDAN

Gabarit : `siman-350/niveau-2-lamdan{,-en,-he}.html`. Corps rédigé dans la langue de la page,
hébreu cité en verbatim.

### 6.1 Charpente

- `div.cover` (badge « DAAT · NIVEAU 2 — LAMDAN » / « רמה 2 — למדן »), `credits` : sujet, nombre de
  séifim du Mehaber, nombre de ס״ק de la Michna Beroura **mesuré** et **écrit dans la langue de
  la page** (« 84 ס״ק », pas « 84 entrées » sur la page hébraïque).
- `h2.section-title` « 📑 Table des matières » + `div.index-box` : **la table doit reproduire les
  `h2` réels** (`audit-simanim.py` contrôle la désynchronisation ; `GENERIC_TOC = "המקור
  והברייתא הבסיסית"`, l.89, est refusée si la section 1 ne porte pas ce titre).
- `h2.section-title` « 📜 Le texte du Choulhan Aroukh — N seifim » : un
  `<div class="sacred-text he"><span class="he-q">סעיף א.</span> …</div>` par séif, même texte que
  le niveau 1, suivi en FR/EN d'un `<p><em>résumé</em> : …</p>` (350:356-363).
- Puis 8 à 10 sections numérotées : sougya, חקירה, Richonim, מחלוקת, נפקא מינה, יסוד, psak,
  « Récapitulatif des chitot et conclusion halakhique », h3 « Pour aller plus loin ».
  Boîtes : `pilpul-box`, `hakira-box`, `rishon-card`, `machloket-box`, `nafka-mina-box`,
  `yesod-box`, `teruts-box`, `kashya-box` (non indexées à part, c'est voulu — `CLAUDE.md`).
  Chaque classe employée doit être définie dans le `<style>` copié (`verifier-classes.py`).
- **L'ordre des sections suit l'ordre des séifim** (règle absolue du 243).

### 6.2 La citation, forme exacte (celle de 350, que les portes lisent)

```html
… la sougya de «&nbsp;<span class="he-q">TEXTE VERBATIM</span>&nbsp;» <span class="source-ref">(עירובין צ״ח ע״ב)</span>. …
```

- Guillemets **typographiques « »** : un bloc « … » est toujours extrait (`verifier-citations.py:1344`,
  `RE_GUILL`) ; des guillemets droits ne le sont que précédés d'une formule reconnue (`CUE`,
  l.1485) — « המשנ״ב (ס״ק ב) מדייק : "…" » au 365 n'est **pas** extrait.
- L'adresse **sur la même ligne**, juste après (règles 26, 30). Formes résolues :
  `(עירובין צ״ח ע״ב)` · `(שו״ע או״ח שס״ו:א)` · `(או״ח שס״ו:א)` · `(שו״ע הרב שס״ו:ב)` (sans או״ח —
  brief Yoré Déa, dernière section) · `(משנה ברורה שס״ו ס״ק ב)` ou `(מ״ב שס״ו ס״ק ב)` ·
  `(מגן אברהם שס״ו ס״ק ג)` · `(ט״ז …)` · `(ביאור הלכה שס״ו)` · `(בית יוסף …)` · `(טור …)` · Rambam
  `(הלכות עירובין פ״א ה״א)`. Table : `verifier-citations.py`, `OUVRAGES` (l.1922-1990).
- Une citation par ligne ; aucune citation coupée avant la clause qui la retourne
  (`verifier-troncatures.py` ; 247:ב « אלא אם כן יש שהות… », 348 « או לא התירו? »).
- Tout `he-q` de plus de 25 lettres est jugé comme une citation : il lui faut son adresse
  (règle 26-bis). Un terme technique court (« לָבוּד ») n'en a pas besoin.

---

## 7. NIVEAU 3 — SYNTHÈSE

Gabarit : `siman-365/niveau-3-synthese{,-he,-en}.html`. Sections (h2 nus, avec `id`) :
`1. L'Axiome central` (`div.axiome`) · `2. Les concepts-clés condensés` (table) ·
`3. Hiérarchie …` (`div.schema` > `span.schema-step` / `div.schema-arrow`) · `4. Arbre de décision …` ·
`5. …` (section propre au siman) · `6. Mnémonique …` (`div.mnemonic` > `span.letter`) ·
`7. Pièges à éviter` (`div.warning`) · `8. Cas pratiques` (table 3 colonnes) ·
`9. Tableau de synthèse finale` · `10. Les commandements pratiques du Siman` (`div.pesak-box`)
+ `div.remember` « Récapitulatif du parcours d'étude ». HE : `📑 תכנית הסיכום`, `1. האקסיומה
המרכזית` … ; EN : `📑 Synthesis plan`, `1. The central axiom` … (titres complets dans les gabarits).

Exigences de fond, toutes nées d'erreurs publiées :

- Le niveau 3 est **là où naissent les erreurs** (`CLAUDE.md` : les quatre erreurs de l'audit
  rabbinique d'août 2026 sont nées dans la synthèse ; 246 : « même le prêt gratuit est
  interdit » quand le Rama écrit l'inverse, commit 5d39ed711). Chaque ligne de psak renvoie à un
  séif nommé, et rien n'y est dit que le niveau 1 ou le niveau 4 ne porte.
- **Chaque séif du siman est mentionné au moins une fois** dans la synthèse (`scripts/veilleur.py`,
  critères A et C).
- Le compte de séifim nomme son ouvrage (365, tableau final : « 8 (Mehaber) — 10 dans le
  Choulhan Aroukh HaRav », le bon modèle).
- Les mesures se recopient sans glissement : טפחים n'est pas אמות (353 : « 4 amot » pour
  ד' על ד' טפחים) ; בית סאתים = 5 000 amot² (100×50), pas « deux בית סאתים » (358), pas
  « 70×50 » (359) ; ס' ריבוא = 600 000 (345 : « 60 000 »).
- Un piège ou un arbre ne transforme pas un permis en interdit ni l'inverse (365, Piège 1 :
  « jusqu'à 10 amot elle vaut comme une simple ouverture » vaut pour le séif ב, pas pour le séif א
  quand il ne reste pas de פס ד' — relire chaque phrase contre son séif).

---

## 8. NIVEAU 4 — DAAT HARAV (Choul'han Aroukh HaRav)

Gabarit : `siman-365/niveau-4-daat-harav{,-he,-en}.html` (605 lignes en FR). Porte :
`scripts/verify-oh-source.py N --rendu` (après l'extension de 0.2), `scripts/verifier-apercus.py N`.

### 8.1 Le CSS est FIGÉ — copier à l'octet près

`verify-oh-source.py` calcule l'empreinte de la suite des `<style>` de la page (espaces
normalisés, `_empreinte_css`, l.727-728) et refuse toute empreinte hors des 225 mesurées
(`CSS_ADMIS`, l.312) : « FEUILLE DE STYLE NON ADMISE ». Mesuré le 20 octobre 2026 :

| Gabarit | Empreinte | Remarque |
|---|---|---|
| `siman-365/niveau-4-daat-harav.html` | `2e669a21ccbdd11b` | 115 pages FR la partagent (362-365…) |
| `siman-365/niveau-4-daat-harav-he.html` | `968911cb178d015d` | vrai CSS RTL (bordures à droite, `◂`, Frank Ruhl) |
| `siman-365/niveau-4-daat-harav-en.html` | `1d2510c6af80c6bb` | |

Ne pas prendre `siman-363/niveau-4-daat-harav-he.html` (`d5a915d3a0a07006`) : c'est le CSS
français avec un `direction: rtl` ajouté. Pour vérifier une page produite :

```python
import importlib.util
s = importlib.util.spec_from_file_location("v", "scripts/verify-oh-source.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
_, fautes, lx = m.lire_page("sources/shabbat/siman-366/niveau-4-daat-harav.html"); print(lx.empreinte_css, fautes)
```

Sont figés de la même façon (l.196-272) : les `<link>` (`LIENS_ADMIS`, polices Google de la
l.28-29 du gabarit), les scripts (`SCRIPTS_ADMIS`), **chaque valeur `style=`** (264 empreintes,
`STYLES_EN_LIGNE_ADMIS`) — donc ne recopier que des `style=` présents dans le gabarit —, le
vocabulaire des balises (`TAGS_ADMIS`, 42) et des classes (`CLASSES_ADMISES`, 59, l.223-229).
Conséquences pratiques :
- **pas de `source-ref`** au niveau 4 (classe absente du vocabulaire) : l'adresse en texte nu
  entre parenthèses, comme au 268 ;
- **pas de `he-q`** au niveau 4 : la classe est admise mais **non définie** dans le CSS du
  niveau 4 (`verifier-classes.py`) ; le 268 cite l'hébreu nu, vocalisé, entre « » ;
- **pas de `<table class="compare-table">`** (tableau « כח הפסק / force du psak ») : retiré de
  Chabbat, c'était le lieu même des fausses adresses (commits 44e6c96ff, d85c88ae7 ; GUIDE-
  CORRECTIONS.md « Le problème n°1 »). La section 2 n'existe plus ; le commentaire
  `<!-- 2. LA FORCE DU PSAK -->` (l.505) peut rester ou partir.

### 8.2 Section 1 — le texte du Rav

```html
<section class="section-block">
  <span class="section-num">1 · טקסט אדמו״ר הזקן</span>                     <!-- EN « 1 · Text of the Alter Rebbe » -->
  <h2 class="section-title-he" id="…">שלחן ערוך הרב — סימן שס״ו</h2>
  <h2 class="section-title-fr" id="…">Le texte intégral du Choulhan Aroukh de l'Admour HaZaken (שולחן ערוך הרב)</h2>
  <div class="section-divider"></div>
  <p style="margin-bottom: 24px; color: var(--text-mid); font-size: 15px;">
    <strong>סימן שס״ו — <chapeau vocalisé> — וּבוֹ י״ח סְעִיפִים</strong><br>
    <em>Source : édition Kehot, telle que reproduite sur Sefaria. 18 seifim.</em>
  </p>
  <details class="seif-details" open>                                        <!-- open sur le séif 1 seulement -->
    <summary class="seif-summary">
      <span class="seif-num">סעיף א</span>
      <span class="seif-preview">PREMIERS MOTS DU SÉIF, VERBATIM…</span>
    </summary>
    <div class="sa-block">
      <p class="sa-he">CHAPEAU וּבוֹ י״ח סְעִיפִים:<br><br>TEXTE VOCALISÉ DU SÉIF 1</p>
      <p class="sa-fr">Traduction…</p>                                      <!-- EN : <p class="sa-en"> ; HE : rien -->
    </div>
  </details>
  …
```

(niveau-4-daat-harav.html:368-503 ; HE : un seul `p.sa-he` par bloc, sans traduction, comme
`siman-365/niveau-4-daat-harav-he.html:365` ; EN : `p.sa-en`.)

- **Nombre de `details.seif-details` = nombre de segments Kehot** (clause de `CLAUDE.md`).
- **`p.sa-he`** = Kehot vocalisé (« Vocalized Edition - Kehot Publication Society », `ED_REF`,
  l.190), mot pour mot, nikoud compris, appels de note retirés sans espace, `<br>` aux
  frontières de paragraphe. `"` → ״ (le 365 a 0 `"` ASCII dans ses `.sa-he`) ; l'apostrophe `'`
  de Kehot reste. Balises admises dans `.sa-he` : `br b small img` (l.199) ; caractères : lettres,
  nikoud, et la liste `ADMIS` (l.198) — rien d'autre. Chaîne obligatoire :
  `details.seif-details > div.sa-block > p.sa-he`. Le seul `style=` admis sur un `.sa-he` de bloc
  est `color:var(--text-muted);font-size:15px;margin-top:14px` (l.349).
- **Le texte est le même dans les trois langues** (parité ; à Chabbat, 17 simanim avaient des
  pages HE et EN abrégées quand la page FR était complète — 355, 356, 357, 358, 360 dans
  `audit/relecture-rav.md` — corrigés le 9 octobre 2026). Jamais d'abrégé présenté comme le texte.
- **`span.seif-preview`** : le début du séif, mots verbatim et dans l'ordre, coupé par « … »
  (ou une condensation marquée « תַּמְצִית: ») — `verifier-apercus.py` ; 3 955 aperçus non
  conformes au premier balayage du 13 octobre 2026. Mêmes mots d'aperçu dans les trois langues.
  Pour le séif 1, l'aperçu commence par le chapeau (365 l.382).
- **`p.sa-fr` / `p.sa-en`** : traduction complète, termes techniques en `<em>`, l'ordre des
  propositions du Rav. Pas de « Rebbe » pour l'Admour HaZaken en anglais : « the Alter Rebbe »
  (340 : « the Rebbe » désigne le Rabbi de Loubavitch).
- Après le dernier séif : le paragraphe « Source : <a href="https://www.sefaria.org/Shulchan_Arukh_HaRav%2C_Orach_Chayim.N" …> »
  (l.500-502) avec le numéral du siman.

### 8.3 Kountress Aharon

Sefaria n'en sert aucun sur 366-407 (1.3). L'accordéon vide « קונטרס אחרון — 0 entrée(s)
(cliquer pour déplier) » (365 l.489-498) est relevé comme « résidu de gabarit » à 352, 357,
360 (`audit/relecture-rav.md`). Recommandation : **retirer le `<details style="margin-top: 32px…">`**
et écrire une ligne dans le paragraphe « Source » : « Sefaria ne donne aucune entrée de Kountress
Aharon pour ce siman. » (HE : « בספריא לא מופיעים ערכי קונטרס אחרון לסימן זה. » ; EN : « Sefaria
gives no Kuntres Acharon entry for this siman. »). Retirer un élément ne change pas l'empreinte
CSS. Si un siman en a (re-mesurer), suivre la forme de `siman-345/niveau-4-daat-harav.html`
(« קונטרס אחרון, אות א », `div.sa-block` + `p.sa-he style="font-size: 17px;"` + `p.sa-fr`).

### 8.4 Section 2 — לשון הרב ולשון המחבר (libellé arrêté en 0-ter)

Charpente de 365 l.508-534 (deux `h2`, le `section-num` et les titres étant ceux de 0-ter, `div.sa-block`
avec `p.sa-he style="font-size: 19px; font-weight: 700; margin-bottom: 12px; color: var(--habad-deep);"`
pour le titre, `p.sa-fr` pour sa version française, `h3 style=…`, `p style="margin-bottom: 10px;"`).
Le fond, lui, se réécrit — règle née des simanim 340-361, où **chaque** bloc חידוש était fautif :

- Un hidoush n'est un hidoush que s'il **diffère du Mehaber** : citer côte à côte le séif du Rav
  « … » (שו״ע הרב שס״ו:ג) et le séif du Mehaber « … » (שו״ע או״ח שס״ו:ב), et nommer la
  différence. Un din mishnaïque que le Mehaber codifie déjà n'est pas un hidoush (344, 349, 351,
  352, 354, 359).
- **Adresse au séif près**, jamais une plage « 1-5 » sauf si le hidoush court réellement sur
  ces séifs ; vérifier chaque adresse contre la section 1 de la même page (pattern #1 : 268, 271,
  273, 274, 276, 277, 340-361).
- Jamais de champ vide (« Position classique : — »), jamais « outil : ». Si l'on n'a pas trouvé
  de hidoush vérifiable, n'en écrire qu'un, ou aucun, et le dire.
- Aucun objet moderne attribué au Rav (275 : LED ; 301 : montre ; 263 : Mivtsa Neshek attribué
  à l'Admour HaZaken mort en 1812).

### 8.5 Section 3 — דברי הרבי

Garder tel quel le bloc « Aucune référence vérifiée à ce jour » (365 l.536-548) tant qu'aucune
lettre, sikha ou psak du Rabbi rattaché au siman n'a été vérifié avec lien. Jamais une référence
non sourcée.

### 8.6 Section 4 — למעשה (modèle : 268)

`div.lemaaseh-block` > `h3` « Pour le Hassid (חסיד) Habad — Siman שס״ו » > `ul` de `li` :
`<strong>① Titre :</strong> conduite… (366:3). <em>Référence : Choulhan Aroukh de l'Admour HaZaken שס״ו:3, 5.</em>`
puis le paragraphe « ⚠ … consulter ton Rav » (365 l.569-571). Chaque point : un séif exact,
une conduite qui découle du texte reproduit en section 1, les réserves du Rav comprises
(345 : « וכל ירא שמים יחמיר לעצמו » omis ; 357 : le caveat du Rama « וכן עיקר » omis).
Un verbatim court y est permis, vocalisé, entre « », adresse collée (268 : « וּסְפֵק בְּרָכוֹת
לְהָקֵל » (268:3)).

---

## 9. CONVENTIONS D'ÉCRITURE

### 9.1 Citations et ordre

1. **Anti-fabrication (absolue)** : tout ce qui est entre « … » ou en `he-q` existe mot pour mot dans
   la source adressée. Une condensation commence par `<em>résumé</em> :` (HE `<em>תמצית</em> :`,
   EN `<em>summary</em> :`) et n'a pas de guillemets (`RESUME` de `verifier-citations.py`).
2. **Extraire, ne jamais retaper** (règle 29) : `python3 scripts/sefaria-extrait.py seif SAH N K` rend le
   séif K du Rav (Kehot vocalisée, appels de note retirés, ״ posés) ; `seif SA N K` celui du Mehaber
   (Maginei Eretz, glose du Rama dans son `<small>`) ; `extrait SAH N K "…"` (ou `--debut … --fin …`) rend la
   sous-chaîne exacte, ou sort en 2 (introuvable) / 3 (ambigu). Un extrait introuvable fait échouer la génération.
3. **L'ordre du Choul'han Aroukh** : numéros, découpe, ordre des propositions dans le séif, ordre
   de présentation (règle absolue du 243). Le niveau 4 suit l'ordre et la numérotation du SA
   HaRav, les niveaux 1-3 ceux du Mehaber : ne pas mêler les deux numérotations sans nommer
   l'ouvrage.
4. **Ktiv de la source**, coquilles comprises, signalées et non corrigées (règles 2, 13 ; 356 :
   « יותד » de Sefaria recopié et à signaler).
5. Une parenthèse de source au milieu d'une citation ne se saute pas (règle 31 ; 242 : le crochet
   « [סמך ממרדכי…] » retiré sans « … »).
6. Une double négation se traduit avec son sens (356 : « אם אין ביניהן פחות מג' טפחים »).

### 9.2 Résidus interdits (à chercher par `grep` avant de rendre)

`Position classique : —` · `outil :` · `כלי:` · `tool:` · `entrée(s)` · `0 KA` · `<!-- à vérifier` ·
`to verify` · `Traduction structurelle` · `מבית מדרשו של ר' יצחק הצרפתי` ·
`Action clairement permise selon le Mehaber` · `talmudiques` ou `entrées` dans une page -he ·
`ניוו` · `dernier siman` · `364` / `365` / `שס״ה` hors des liens « précédent » ·
`"` ASCII entre deux lettres hébraïques · `Hilkhot Shabbat` hors des renvois voulus.
Puis `python3 scripts/verifier-residus.py sources/shabbat/siman-N` après chaque correction.

### 9.3 Numérotation hébraïque (convention de `scripts/heb-nums.py`)

366 שס״ו · 367 שס״ז · 368 שס״ח · 369 שס״ט · 370 ש״ע · 371 שע״א · 372 שע״ב · 373 שע״ג · 374 שע״ד ·
375 שע״ה · 376 שע״ו · 377 שע״ז · 378 שע״ח · 379 שע״ט · 380 ש״פ · 381 שפ״א · 382 שפ״ב · 383 שפ״ג ·
384 שפ״ד · 385 שפ״ה · 386 שפ״ו · 387 שפ״ז · 388 שפ״ח · 389 שפ״ט · 390 ש״צ · 391 שצ״א · 392 שצ״ב ·
393 שצ״ג · 394 שצ״ד · 395 שצ״ה · 396 שצ״ו · 397 שצ״ז · 398 שצ״ח · 399 שצ״ט · 400 ת׳ · 401 ת״א ·
402 ת״ב · 403 ת״ג · 404 ת״ד · 405 ת״ה · 406 ת״ו · 407 ת״ז.

Pièges propres à ce lot, à faire passer par les portes : **ש״ע (370)** est aussi le sigle de
« שולחן ערוך », **ש״צ (390)** celui de « שליח ציבור », **ת״ב (402)** celui de « תשעה באב » ;
**ת׳ (400)** n'a qu'une lettre (geresh, pas gershayim). Dans la prose hébraïque, écrire
« סימן ש״ע · 370 » (forme de `heb-nums.py`) et jamais « ש״ע » seul pour le siman. Les numéros de
séif et de ס״ק prennent leur gershayim (« ס״ק י״ב », pas « ס״ק יב » : 1 476 corrigés, commit
5d39ed711) ; « טו » et « טז » pour 15 et 16.

### 9.4 Dénombrements

N'écrire « le seul », « l'un des trois », « le plus long » que mesuré, et préférer la forme
ouverte (« notamment aux séifim 3 et 7 ») — `verifier-denombrements.py` ; corollaire : une
énumération fermée fausse ne corrige pas un absolu faux (234 ; 247 « deux réserves seulement »).

### 9.5 Locuteurs et attributions

La famille de défauts dominante des niveaux 2 traduits (commit 8b3c6e63f) : une parole rendue au
mauvais locuteur — l'objectant pris pour celui qui tranche (263), la Mishna anonyme donnée à un
Amora (278), le rapporteur pris pour l'auteur (264, 348 : le Beit Yossef rapporte les Richonim),
Mehaber et Rama croisés (302 : « וטוב לחוש » est du Rama ; `verifier-citations.py` ne le voit
pas, il résout שו״ע et רמ״א vers le même segment). Vérifier chaque attribution sur la source.

---

## 10. LE BRIEF DE YORÉ DÉA : CE QUI VAUT, CE QUI CHANGE

| Règle (docs/brief-yoreh-deah.md) | Pour Orah Haïm 366+ |
|---|---|
| Contexte : `sources/yoreh-deah`, `niveau-4-halakha`, « ne jamais citer שולחן ערוך הרב » | **Change** : `sources/shabbat/siman-N`, `niveau-4-daat-harav`, le niveau 4 EST le SA HaRav |
| URL `/yd/N/…/halakha` | **Change** : `/oh/N/…/daat-harav` |
| 1 anti-fabrication · 1-bis chapeau tout ou rien · 2 ktiv · 13 coquilles · 16 signaler sans corriger · 17 guillemets = verbatim | Valent telles quelles |
| 21 pièges API (Yoreh_De%27ah, Kaf HaHaïm YD, Baer Hetev, Chakh, Aroukh HaChoul'han YD 123-182) | **Change** : sans objet pour la plupart ; à Orah Haïm, `Mishnah_Berurah.N` et `Magen_Avraham.N` (jamais `…_on_Shulchan_Arukh,_Orach_Chayim.N`) ; Baer Hetev et Pit'hei Techouva n'existent qu'en YD dans `OUVRAGES` ; la réponse « 503 Backend fetch failed » en HTML vaut partout |
| 22 compter les séifim soi-même · 22-bis compter `len(d['he'])` | Valent ; ici **deux** comptes, Mehaber et SA HaRav (1.2) |
| 23 le champ `text` n'est pas une traduction | Vaut (le texte anglais de Sefaria n'est pas la source) |
| 24 conversion des gershayim entre deux lettres · 25 tout verbatim en « » · 26 référence sur la ligne · 26-bis he-q > 25 lettres · 27-bis meta sans balisage · 29 extraire · 30 une citation par ligne · 31 parenthèse de source · 32 titres traduits · 33 classes définies · 34 titres dans la langue | Valent ; 33 se double au niveau 4 du **vocabulaire figé** (8.1) |
| 35 flèches hébraïques RTL (YD) | **Change** : Orah Haïm a la convention inverse — copier 364-he (3.4) |
| 36 un siman sans titre ne s'invente pas de titre | Vaut (chapeaux du Mehaber et du Rav) |
| 37 absence de commentaire ≠ absence d'ouvrage | Vaut, et s'applique au Kountress Aharon (1.3, 8.3) |
| « Ce que le vérificateur ne voit pas » 1-5 | Valent ; ajouter : les guillemets **droits** sans formule d'annonce ne sont pas extraits (6.2) ; les `sacred-text` de la Michna Beroura ne sont confrontés par rien (5.3) ; le contenu des cellules et des listes sans guillemets n'est jugé par rien (commit 44e6c96ff) |
| « `(שו״ע הרב רנ״ג:ט)` sans או״ח » | Vaut |
| Méthode (télécharger, outil 29, niveau 1 d'abord, fichier sur disque dès qu'il est prêt, s'arrêter si le contexte s'épuise) | Vaut ; ordre : niveau 1 (3 langues) → niveau 4 (3 langues) → index → niveaux 2, 3 |
| « Avant de rendre » : verify-yd-source | **Change** : voir 11 |
| Ce qui n'existe pas en YD | **Nouveau** : CSS figé du niveau 4, aperçus, rendu Chromium, encadrés « Ce que dit ce séif », tableau « Cas pratiques modernes » indexé |

---

## 11. AVANT DE RENDRE — les portes, dans cet ordre

Toutes sur `--path sources/shabbat/siman-N` ou le numéro, et toutes à zéro (ou à l'état
indiqué). Rapporter la sortie de chacune.

```bash
python3 scripts/verify-chabbat-source.py N                 # niveau 1 : texte, découpe, parité — IDENTIQUE ou ÉQUIVALENT
python3 scripts/verify-oh-source.py N --rendu              # niveau 4 : texte, CSS, vocabulaire, visibilité (sans --cache)
python3 scripts/verifier-apercus.py N                      # aperçus du niveau 4
python3 scripts/verifier-alignement.py --siman N           # étiquettes de séif et ordre
python3 scripts/verifier-encadres.py --siman N             # « Ce que dit ce séif » dans son séif
python3 scripts/verifier-couverture-encadres.py --section shabbat N
python3 scripts/verifier-citations.py --path sources/shabbat/siman-N --langues fr,he,en   # CONFRONTÉES > 0 ; 0 REF_FAUSSE, 0 INTROUVABLE
python3 scripts/verifier-troncatures.py --path sources/shabbat/siman-N
python3 scripts/verifier-etiquettes.py N
python3 scripts/verifier-ancrage.py N
python3 scripts/verifier-denombrements.py --path sources/shabbat/siman-N --a-verifier   # chaque « À VÉRIFIER » mesuré ou retiré
python3 scripts/verifier-langues.py --path sources/shabbat/siman-N --lignes
python3 scripts/verifier-url-langue.py --path sources/shabbat/siman-N --details
python3 scripts/verifier-balises.py --path sources/shabbat/siman-N --lignes
python3 scripts/verifier-classes.py --path sources/shabbat/siman-N --lignes
python3 scripts/verifier-liens.py
python3 scripts/verifier-liens-langue.py --path sources/shabbat/siman-N --lignes
python3 scripts/audit-simanim.py --quiet                   # après l'extension de 0.2
python3 scripts/verifier-residus.py sources/shabbat/siman-N
```

Puis `npm run build` et lire sa sortie : « fichier de niveau qui ne produit aucun chunk »,
« extraction qui capte moins de la moitié du texte » et « siman sans titre » visent votre siman.
Contrôle structurel de `CLAUDE.md` : 15 fichiers ; chaque fichier finit par `</html>` ;
`canonical == og:url` ; JSON-LD qui parse.

Remarques :
- Une porte qui sort verte **sans avoir rien comparé** n'a rien prouvé : lire le compte des
  confrontations (`verifier-citations.py` imprime « CONFRONTÉES à un texte »).
- Supprimer les CSV que les portes écrivent dans `audit/` (`citations-sources-*.csv`).
- **Aucun commit, aucun push.** Ne toucher à rien hors de `sources/shabbat/siman-N/` et du
  scratchpad, sauf mandat écrit du coordinateur (la section 0.3 est à lui).

## 12. DANS LE RAPPORT

Ce que chaque séif traite réellement (Mehaber et SA HaRav, chacun avec sa numérotation), les
ma'hlokot du niveau 2, chaque hidoush avec ses deux citations, la sortie de chaque porte, et
**tout point douteux, non tranché** : une adresse qui ne tombe pas juste, une traduction qui
repose sur une interprétation, la note 398:4, un séif dont le découpage diffère entre Mehaber et
SA HaRav, tout écart entre ce brief et la source — **suivre la source contre le brief** et le dire.
