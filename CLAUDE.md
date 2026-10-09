# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

DAAT (דעת / daattorah.com) is a trilingual halakhic study platform: hand-authored static HTML pages for the Choulhan Aroukh (Orah Haïm, Hilkhot Shabbat) plus Vercel serverless functions powering an AI study assistant. No front-end framework — pages are standalone HTML with inline `<style>`; the API is ESM Node functions under `api/`.

## ⚠️ Clause de vérification obligatoire avant publication (RÈGLE ABSOLUE)

**Avant toute mise en ligne en production (`main`), et à la fin du travail de chaque lot / chaque semaine, il faut RE-VÉRIFIER la totalité du contenu produit et le confronter aux sources originales pour être certain qu'il n'y a aucune erreur.** Cette vérification n'est pas optionnelle : c'est la dernière porte avant publication.

Elle comporte, au minimum :
1. **Contrôle structurel** de tous les fichiers produits : 15 fichiers/siman ; parité trilingue (FR/HE/EN) ; 0 jeton interdit ; `canonical == og:url` ; geresh/gershayim corrects (jamais d'apostrophe/guillemet ASCII à l'intérieur d'un mot hébreu) ; chaque fichier finit par `</html>` ; nombre de `<details class="seif-details">` = nombre réel de seifim du Choul'han Aroukh HaRav.
2. **Confrontation aux sources (Sefaria)** : re-télécharger le Mehaber (`Shulchan_Arukh,_Orach_Chayim.N`) et le Choul'han Aroukh HaRav (`Shulchan_Arukh_HaRav,_Orach_Chayim.N`) et **comparer le texte hébreu source du niveau-4** (`.sa-he` dans les blocs `seif-details`) au texte réel — verbatim, consonnes identiques — pour garantir qu'aucun seif n'a été inventé, tronqué, ni altéré, et que le nombre de seifim est exact. En cas de doute halakhique sur un contenu (traduction, explication, psak), **retourner voir la source** avant de publier.
3. **Ne publier qu'une fois cette vérification entièrement verte**, et n'annoncer « c'est en ligne » qu'après confirmation. Toute divergence détectée doit être corrigée (et re-vérifiée) avant le déploiement.

Le script `scripts/verify-oh-source.py N [N...]` automatise la confrontation aux sources pour le compartiment `oh-quotidien` ; le lancer sur chaque lot avant de proposer la mise en ligne. Il ne contrôle que le **niveau 4** (Choul'han Aroukh HaRav). Le **niveau 1** (Mehaber + Rama) a sa propre porte depuis le 8 octobre 2026, `scripts/verify-oh-niveau1-source.py N [N...]` : la lancer aussi, et elle ne doit pas devenir **plus** rouge sur les simanim du lot — 133 des 241 simanim y divergent encore au 9 octobre 2026, aucun par un séif absent sans le dire (voir plus bas). ⚠️ Sefaria sert **plusieurs éditions hébraïques** du Choul'han Aroukh, dont deux de référence pour chaque livre (l'édition par défaut et la Torat Emet numérotée), et les pages en recopient tantôt l'une, tantôt l'autre : les trois portes de source du Choul'han Aroukh (niveau 1 d'Orah Haïm, Chabbat, Yoré Déa) confrontent ces deux-là depuis le 9 octobre 2026, sous une règle unique — voir « Les éditions de Sefaria » plus bas. `verify-oh-source.py` (niveau 4) ne lit toujours qu'une édition du Choul'han Aroukh HaRav, dont Sefaria sert aussi deux éditions hébraïques.

### ⚠️ Lacune du Choul'han Aroukh HaRav dans `oh-quotidien` (niveau-4 = page-pont 🌉)

Le Choul'han Aroukh HaRav (Admour HaZaken) **ne couvre pas tout Orah Haïm** : il y a des blocs entiers qu'il n'a pas rédigés. Dans le compartiment `oh-quotidien`, les lacunes, **mesurées sur Sefaria pour les simanim 1 à 365** le 8 octobre 2026 (302 servis, 63 vides — les simanim au-delà de 365 n'ont pas été mesurés), sont **132-154, 157, 169-173, 175-176, 208-211, 216-241** en Orah Haïm quotidien, et **304, 322** en Hilkhot Chabbat. Cette liste a été fausse deux fois, et c'est la raison de la donner mesurée : ce fichier écrivait « 132 à 154 … ex. 157, 170-179, 210, 220, 240, 420… », puis un message de commit de la session elle-même (800f886e), repris par un arbitre (b9845687), l'a « corrigée » en « 132-154, 157, 170-173, 175-176, 208-241, 304, 322 » — soixante-six simanim pour un total annoncé de soixante-trois. La liste juste n'est entrée dans le code que le 7 octobre 2026 (`scripts/verifier-alignement.py`, `LACUNES_MESUREES`, commit b9845687) ; jusque-là la porte détectait la lacune à la volée, et sa docstring portait l'ancienne liste fausse. **AVANT de produire un niveau-4, toujours vérifier le nombre de seifim SA HaRav** : `curl -s "https://www.sefaria.org/api/texts/Shulchan_Arukh_HaRav,_Orach_Chayim.N?context=0&pad=0"` → si `he` est vide (0 seif), l'Admour HaZaken **n'a pas écrit ce siman**.

Dans ce cas, **NE JAMAIS fabriquer de texte SA HaRav** (règle anti-fabrication ABSOLUE). Le niveau-4 devient une **page-passerelle sobre** (🌉), générée par `scripts/gen-bridge.py` (ou `/tmp/gen-bridge.py`) : elle explique honnêtement l'absence, renvoie aux niveaux 1-3 (Mehaber/Rama) et au **Siddour de l'Admour HaZaken** (où sa pratique sur la tefila est consignée), **sans aucune citation reconstruite ni le mot « n'existe pas sur Sefaria »**. Les niveaux 1-3 + index restent des pages normales (contenu Mehaber/Rama). `verify-oh-source.py` passe alors avec 0 seif attendu = 0 bloc `seif-details`. Décision utilisateur (2026) : **page-pont sobre**, pas de reconstruction façon 304/322.

## ⚠️ Le Choul'han Aroukh est le repère — ordre compris (RÈGLE ABSOLUE)

**Toute référence doit être exactement celle du Choul'han Aroukh** : le numéro du séif,
la découpe entre séifim, l'ordre des propositions à l'intérieur d'un séif, et l'ordre dans
lequel la page les présente. Une page ne réarrange pas la source pour les besoins de son
exposé ; si un enchaînement pédagogique semble l'exiger, c'est l'exposé qui plie.

Décision de l'utilisateur, août 2026, après le siman 243 : *« Il faut toujours que ce soit
exactement comme dans le Choul'han Aroukh. Le Choul'han Aroukh est le repère pour toute
référence. »*

Ce que le 243 a montré, et qu'aucun des garde-fous de contenu ne pouvait voir — les
citations y étaient réelles, la langue juste, la structure conforme :

- le champ, le four, le moulin et la glose du Rama, tous dans le **séif א**, étaient publiés
  sous « סעיף ב », et le vrai séif ב n'était cité nulle part ;
- une clause déplacée d'un raisonnement à l'autre donnait comme raison de **permettre** le
  champ ce que le Choul'han Aroukh donne comme raison d'**interdire** le bain ;
- et la page présentait la fin du séif א **après** le séif ב.

`scripts/verifier-alignement.py` est le contrôle qui répond de cette règle. Il lit
l'étiquette de séif dans le titre **et dans le paragraphe** (`<p><strong>סעיף א.</strong> …`,
`<strong>א.</strong>` entre `<br>`), sur `niveau-1-base.html` en entier et sur `index.html`,
`niveau-2-lamdan.html`, `niveau-3-synthese.html` pour les seules étiquettes inline. Il pose
deux questions : *le bloc annoncé séif N est-il le séif N ?* et *les blocs se suivent-ils
dans l'ordre de la source ?* Le lancer avant de publier une page de séif.

⚠️ **La porte écrite pour le siman 243 ne lisait ni le niveau 4 ni deux langues sur trois.**
Sa liste de fichiers s'arrêtait à `niveau-1-base.html` et trois pages françaises : 2 052 pages
lues sur 7 695. Et sur les 1 095 pages `niveau-4-daat-harav`, son motif captait **zéro bloc** —
le texte source y vit dans un `<p class="sa-he">` d'un `<details class="seif-details">`. Ce texte
n'est pas le Choul'han Aroukh mais le **Choul'han Aroukh HaRav**, un autre livre à numérotation
propre : le confronter au Mehaber aurait produit un bruit massif et faux. Réparée (octobre 2026),
mesure du 8 octobre : 7 695 fichiers, 23 701 blocs, 22 887 étiquettes de séif, les trois langues,
le niveau 4 confronté au Choul'han Aroukh HaRav ; plages chaînées « ז-ח-ט-י » lues en entier dans
les deux écritures ; « סעיף אחד » n'est plus lu comme le séif 13. Le niveau 4 rend **0 anomalie**
(9 926 blocs au commit 800f886e) : l'élargissement le plus rentable en couverture n'est pas celui
qui trouve le plus.

## ⚠️ Avant tout push sur `main` : fusionner puis vérifier (RÈGLE ABSOLUE)

Plusieurs sessions travaillent sur ce dépôt depuis des copies distinctes. **Par deux fois**, une
session a poussé sur `main` un commit construit sur une copie périmée : les commits `7ed67012`
(« journal S3 ») et `a1311630` (« journal S5 ») ont chacun **supprimé silencieusement des dizaines
de simanim déjà publiés** et annulé des correctifs appliqués à plus de 1 300 fichiers, sans que le
message de commit n'en dise un mot. Le site a perdu douze simanim en ligne, deux fois.

Donc, **avant tout push sur `main`, sans exception** :

```bash
git fetch origin main && git merge origin/main   # jamais publier sur une base périmée
python3 scripts/verifier-integrite.py            # doit sortir 0
```

`scripts/verifier-integrite.py` compare l'état local à `origin/main` et **refuse** un état qui
supprimerait un siman publié, désynchroniserait le catalogue du disque, ou annulerait l'un des deux
correctifs mécaniques (`scripts/fix-jsonld-lang.py`, `scripts/heb-nums.py` — tous deux idempotents et
rejouables). Si une suppression est réellement voulue, `--autoriser-suppressions` et **le dire dans le
message de commit**. Le workflow `.github/workflows/anti-regression.yml` fait le même contrôle après
coup sur `main` et échoue en rouge si des simanim disparaissent.

Ce contrôle est structurel et ne remplace pas la clause de vérification de contenu ci-dessous.

## Commands

```bash
# Full build (run by Vercel as vercel-build, and locally before commit if you touched content or chat-widget.js)
npm run build
#   → generate-simanim-index.js : régénère data/simanim-disponibles.json (titres) — FUSION,
#                                 ne supprime jamais une entrée, couvre les 4 sections
#   → extract-corpus.js         : régénère data/corpus-shabbat.json (le corpus BM25 du chat)
#   → build:js                  : terser sur assets/js/chat-widget.js → chat-widget.min.js

# Content state guard — MUST stay green. The reference count is whatever the script prints,
# never a value hard-coded here. It covers **Hilkhot Shabbat and Yoreh De'ah only** — Orah Haïm
# has its own checks. Exits non-zero on boilerplate / missing files / desynced TOC.
python3 scripts/audit-simanim.py            # full report
python3 scripts/audit-simanim.py --quiet    # summary only (what the SessionStart hook prints)
python3 scripts/audit-simanim.py --write-progress   # regenerates PROGRESS.md (never hand-edit PROGRESS.md)

# Content-truth guard — checks every Hebrew "verbatim" quote against its real source on Sefaria.
# audit-simanim.py is structural only and passes on pages full of invented citations; this is the
# complementary gate. Exits non-zero while any quote is ABSENT from the source it cites.
python3 scripts/verifier-citations.py                       # whole site, FR (Hebrew quotes are shared across the 3 languages)
python3 scripts/verifier-citations.py --only-absent          # just the list to fix
python3 scripts/verifier-citations.py --path sources/shabbat/siman-297
# ⚠️ LA MICHNA BEROURA MANQUAIT À SA TABLE D'OUVRAGES, et c'est l'ouvrage le plus cité du
# compartiment. RE_MB ne lit que la forme à deux-points (« מ״ב רמ״ו:ב ») ; la forme
# conventionnelle du dépôt — « (משנה ברורה רמ״ו ס״ק ב) » ou « (מ״ב רמ״ו ס״ק ב) » — ne
# produisait AUCUNE référence, ni par RE_MB qui exige le deux-points, ni par OUVRAGES où elle
# ne figurait pas. Ces citations partaient en « sans référence » et n'étaient confrontées à
# RIEN. 648 références sont dans ce cas — 642 en Hilkhot Chabbat, 6 en Orah Haïm.
# Le motif exige le nom en toutes lettres, OU le sigle avec ses frontières de mot et non suivi
# d'une marque de folio : « מ״ב » est aussi la guématria 42, et « (מנחות מ״ב.) » est un DAF.
# Mon premier comptage, qui l'ignorait, annonçait 1 934 au lieu de 648.
# EFFET MESURÉ, avant → après :
#   siman 246 : sans réf 12 → 4  · conformes 24 → 32 · variantes 2 → 2
#   siman 248 : sans réf 29 → 27 · conformes 55 → 55 · variantes 1 → 3
#   siman 253 : sans réf  9 → 8  · conformes 50 → 50 · variantes 3 → 5
# Référence fausse et INTROUVABLES restent à 0 partout. Mais les VARIANTES augmentent sur deux
# des trois simanim : des citations qui n'étaient confrontées à rien reviennent « texte réel,
# mais pas mot pour mot ». C'est la porte qui fait enfin son travail, et il faut le dire —
# j'avais d'abord annoncé « elle n'accuse rien de neuf » sur la foi du seul siman 246.
#
# ⚠️ OCTOBRE 2026 — CE QU'ELLE NE LISAIT PAS, ET CE QU'ON Y A TROUVÉ.
#   · Les <meta name="description">, og:, twitter: et le JSON-LD : 7 432 citations d'entête, dans
#     les trois langues, n'étaient pas LUES — invisibles à la lecture, lues par Google. Elles sont
#     désormais examinées ; comme dans le corps, une partie reste sans référence.
#   · L'Eliya Rabba manquait à OUVRAGES — un lot l'avait déclarée « non numérisée » ; elle est
#     sur Sefaria (Eliyah_Rabbah_on_Shulchan_Arukh,_Orach_Chayim).
#   · Le code 3 sort désormais dès qu'une citation part en NON_RESOLU parce qu'un ouvrage est
#     injoignable, QUEL QUE SOIT l'ouvrage — il ne couvrait que la Michna Beroura. Une panne
#     PARTIELLE d'un ouvrage (une référence sur deux) reste, elle, non signalée. Mesure qui l'a
#     motivé, faite par sabotage par un arbitre (commit b9845687) : quand seule la recherche
#     plein-texte tombait, l'ancienne porte rendait 8 INTROUVABLE FICTIVES — des accusations de
#     fabrication nées d'une panne d'index.
#   · Elle tourne en FRANÇAIS par défaut : son CSV ne couvre qu'UNE langue sur trois. Sur les onze
#     verdicts graves de Chabbat, dix existaient à l'identique en -he et -en. --langues fr,he,en.
#   · La פתיחה non numérotée décale la Michna Beroura aux simanim 69, 178, 211 (Orah Haïm) et
#     243, 248, 253, 308, 317, 319, 337 (Chabbat) parmi les simanim du dépôt — le recensement
#     exhaustif écrit dans le script en compte onze, le 645 compris, et un vérificateur l'a refait
#     sur Sefaria pour 1-365 ; elle ne le fait pas aux simanim 250 et 251.
# PREMIER BALAYAGE D'ORAH HAÏM — 1er octobre, porte d'AVANT la lecture des entêtes et l'ajout de
# l'Eliya Rabba, français seul : 106 verdicts graves, soit 74 REF_FAUSSE, 16 INTROUVABLE et
# 16 NON_RESOLU (le total des citations examinées ce jour-là n'est consigné nulle part ; un rejeu
# de cette porte le 8 octobre rend 14 238 citations, 74 REF_FAUSSE, 16 INTROUVABLE, 15 NON_RESOLU).
# Ces 106 verdicts ont été ouverts un par un contre Sefaria par quatre lots et quatre arbitres
# (audit/oh-graves-*.md) : 7 verdicts de FABRICATION (5 phrases distinctes ; six en
# niveau-2-lamdan, un en niveau-3-synthese) — des mots d'ordre talmudiques mis entre guillemets
# (« מודים רבנן מאי אמרי » pour « העם מה הם אומרים », Sotah 40a, siman 127) et un dibour de
# Tossafot inventé (siman 9) — et des dizaines de citations réelles MAL ADRESSÉES (un verset
# donné sous l'adresse d'un daf, les mots du Choul'han Aroukh sous celle de la guemara).
# Corrigées siman par siman en octobre 2026, chaque lot arbitré avant commit ; ce que les
# arbitres ont laissé est dans audit/oh-corrections-restes.md. LEÇON : les 9 phrases fautives du
# lot INTROUVABLE apparaissaient 134 fois dans 35 fichiers, dont une seule 57 fois — des chaînes
# comptées, dont une partie étaient des paraphrases licites ou des citations à la bonne adresse.
# Chaque occurrence se juge à part, et corriger la ligne du CSV n'est pas corriger.

# Garde-fou de langue — chaque page est-elle écrite dans la langue qu'elle annonce ?
# Trois échelles : la page entière, le bloc isolé, et l'entête (title/og/twitter/JSON-LD),
# cette dernière étant invisible à la lecture mais lue par Google et les aperçus de partage.
# Complémentaire des deux autres : une page peut être 174/174 conforme, sans citation
# fausse, et avoir un corps entièrement français sous un lang="en".
python3 scripts/verifier-langues.py            # tout le site
python3 scripts/verifier-langues.py --lignes   # + la liste des blocs à traduire

# ⚠️ LES ÉDITIONS DE SEFARIA — à lire avant toute porte de source, et avant de recopier un séif.
# Sefaria sert PLUSIEURS éditions hébraïques du même livre ; api/texts ne sert que le TEXTE de
# l'édition par défaut (qu'il nomme dans heVersionTitle ; les autres n'y figurent que par leur titre) :
#   https://www.sefaria.org/api/v3/texts/REF?version=hebrew%7Call  → « versions », chacune avec
#   « versionTitle » et « text » (un segment par séif).
#   · Orah Haïm (1-241) et Hilkhot Chabbat (242-365), même livre : « Maginei Eretz: Shulchan Aruch
#     Orach Chaim, Lemberg, 1893 » (PAR DÉFAUT, non vocalisée, porte le chapeau « ובו יז סעיפים ») et
#     « Torat Emet 363 » (vocalisée, DÉVELOPPE des abréviations — « לבה״כ » → « לבית הכסא » —, sans
#     chapeau, leçons propres : « יאמר » / « יאמרו »). Sur 105 simanim de Chabbat, aussi « Torat Emet
#     Freeware », et sur un siman « שלחן ערוך מטור ארוח חיים » ; R1 les écarte.
#   · Yoré Déa : « Ashlei Ravrevei » (par défaut, Lemberg 1888), « Torat Emet 357 » (vocalisée, texte
#     censuré : « עבודת כוכבים » pour « אלילים »), « Torat Emet Freeware » (113 simanim, entre 113 et
#     234), « Wikisource » (51 simanim).
# Les pages d'Orah Haïm recopient tantôt Maginei Eretz, tantôt Torat Emet (vocalisée), et beaucoup de
# pages non vocalisées sont du Maginei Eretz aux abréviations développées comme le fait Torat Emet ;
# 142 séifs mêlent les deux éditions. Chabbat et les simanim conformes de Yoré Déa recopient l'édition
# par défaut ; les simanim 87-118 de Yoré Déa suivent souvent Torat Emet 357. Jusqu'au 9 octobre 2026,
# les trois portes de source du Choul'han Aroukh ne lisaient que l'édition par défaut : une page fidèle
# à Torat Emet y sortait « altérée » — plus de 140 séifs d'Orah Haïm comptés comme altérés ne l'étaient
# que par l'édition (141 au premier tour du 8 octobre, et 49 de plus quand la porte a admis les leçons
# mêlées dans un séif), et 28 séifs français de l'état de Chabbat du 14 septembre (31 avant la garde
# ktiv).
# Une première réparation retenait, séif par séif, l'édition la plus proche : ses arbitres l'ont fait
# certifier conforme, code 0, sur des pages qui recopiaient une édition DÉSALIGNÉE (Freeware sert sous
# Orah Haïm 344:1 le texte du 343:1, et la porte de Chabbat l'acceptait ; sous Yoré Déa 139 elle sert
# celui du 138, que la garde de siman de la porte de Yoré Déa écartait déjà) ou LACUNAIRE (Freeware
# 252:2 saute « מלאכתו בשבת אם היה עושה », 316:7 omet « ועקרבים » ; Freeware Yoré Déa 190:35 n'a pas
# « הגה: וכן עיקר », la décision du Rama). D'où la RÈGLE COMMUNE aux trois portes de source :
#   R1  éditions de référence : l'édition par défaut et la Torat Emet numérotée (363, 357), et ELLES
#       SEULES ; Freeware et Wikisource sont ignorées, et la sortie le dit ;
#   R2  la Torat Emet n'est admise pour un séif que si elle est ALIGNÉE sur le séif de même numéro de
#       l'édition par défaut ;
#   R3  UNE AUTRE ÉDITION EXPLIQUE UNE LEÇON, JAMAIS UNE OMISSION : tout passage de l'édition par défaut
#       absent de la page reste signalé, « absent aussi de Torat Emet » le cas échéant — y compris une
#       DITTOGRAPHIE de Torat Emet 357 (234:37 « או שרוי לך או שרוי לך » pour « או מותר ליך או שרוי ליך ») ;
#   R4  chaque séif retenu hors de l'édition par défaut est imprimé avec son édition.
# Et la GARDE KTIV : les portes d'Orah Haïm et de Chabbat ôtaient yod et vav pour comparer — à l'intérieur
# du mot pour Orah Haïm, partout pour Chabbat, vav de conjonction compris —, si bien que « כוס » (coupe)
# et « כיס » (poche), « מים » et « מום », « הוא » et « היא » avaient la même clé : une page qui changeait
# l'un en l'autre sortait ÉQUIVALENT. La porte de Yoré Déa n'a jamais excusé le ktiv. Deux mots ne sont égaux au ktiv que si l'un s'obtient de
# l'autre en AJOUTANT des yod/vav ; un échange est un mot changé, imprimé. Sous ÉQUIVALENT, la porte
# LISTE les mots égaux au ktiv près, pour qu'on les contrôle.
# POUR RECOPIER UN SÉIF : bloc vocalisé → Torat Emet, nikoud compris ; bloc non vocalisé → l'édition par
# défaut, gershayim ״ et geresh ׳ ; un passage que Torat Emet omet se recopie de l'édition par défaut.

# Garde-fou de source pour Yoré Déa — la concaténation des <blockquote class="text-source">
# du niveau 1 reproduit-elle VERBATIM, et dans l'ordre, la totalité des seifim que
# Sefaria donne pour ce siman ? Consonnes comparées, nikoud et ponctuation libres.
# Contrôle aussi la parité FR/HE/EN du texte source. L'équivalent d'Orah Haïm est
# verify-oh-source.py, et pour Hilkhot Shabbat verify-chabbat-source.py.
python3 scripts/verify-yd-source.py 129 130 131

# Garde-fou de source pour Hilkhot Chabbat — le même invariant que ci-dessus, plus
# la DÉCOUPE : le nombre de blocs source est-il le nombre de séifim ? Rend deux
# verdicts distincts, IDENTIQUE et ÉQUIVALENT (égal aux matres lectionis près),
# parce que le ktiv haser/malé est le faux positif dominant et ne dit rien de la
# fidélité à la source. Premier balayage, 14 septembre 2026 : 44 des 124 simanim
# divergent au-delà du ktiv, et c'est un bloc — 242-283 et 309-314 ; tout ce qui
# a été produit à partir du 284 est conforme, le 309-314 excepté. Corrigés depuis :
# au 9 octobre 2026, les 124 sont conformes (366 pages IDENTIQUES, 6 ÉQUIVALENTES ;
# découpe de 242 et 243 en avertissement). Rejoué sous R1-R4 sur l'état du 14 septembre,
# le compte reste 44, mais 28 séifs français n'y sont fidèles qu'à Torat Emet 363 (31
# avant la garde ktiv) : une partie de ces « divergences » était du bruit d'édition.
python3 scripts/verify-chabbat-source.py 292 301 308
python3 scripts/verify-chabbat-source.py --tous --bref

# Garde-fou de source pour le NIVEAU 1 d'Orah Haïm — la porte qui manquait. verify-oh-source.py
# ne regarde que le niveau 4 ; rien ne vérifiait que le niveau 1 des 241 simanim recopie le
# Mehaber et le Rama, et la troncature du séif 10 d'Orah Haïm 8 (17 mots, trois langues)
# n'était PLUS signalée par aucune porte (verifier-alignement la signalait jusque-là, en FR et EN,
# par un faux motif). Nomme la famille de chaque écart : absent déclaré ou non,
# TRONCATURE (début, fin, intérieure ; Rama ou Mehaber ; déclarée par « … » ou non), DÉPLACÉ,
# ALTÉRATION (abréviation développée, parenthèse omise, mots changés), REPRISE.
# Premier balayage, 8 octobre 2026, contre la SEULE Maginei Eretz — 241 simanim, 1 453 séifim : IDENTIQUE 73 · ÉQUIVALENT 7 ·
# TRONCATURE 56 · ALTÉRATION 90 · ABSENT NON DÉCLARÉ 14 · ABSENT DÉCLARÉ 1. 219 séifim tronqués,
# dont 141 touchés dans la glose du RAMA ; sur 276 coupures (séif × position), 158 portent sur le
# Rama et 26 seulement sont déclarées par « … ». 655 séifim altérés, dont 504 « par une abréviation
# développée » — chiffre FAUX par construction : une bonne part de ces séifs recopiaient fidèlement
# Torat Emet 363 (voir « Les éditions de Sefaria » plus haut).
# ÉTAT AU 9 OCTOBRE 2026, porte sous R1-R4 et garde ktiv : IDENTIQUE 88 · ÉQUIVALENT 20 · TRONCATURE 59 ·
# ALTÉRATION 73 · ABSENT DÉCLARÉ 1 (le 32) · ABSENT NON DÉCLARÉ 0 — 133 divergents ; séifs, chacun sous
# son pire défaut : 1 005 conformes, 136 tronqués, 264 altérés, 8 déplacés, 40 absents déclarés (par
# famille, l'unité des 219 et 655 ci-dessus : 136 tronqués, 338 altérés, 12 déplacés ; coupures, en
# séif × position : 123 sur la glose du Rama, 17 seulement déclarées par « … »). Entre les deux : les 14 simanim qui omettaient des séifs sans le dire (3 8 53 55 66 79 90 94
# 113 128 153 158 159 160) ont été restaurés — 176 séifs, en tout ou en partie, dans au moins une
# langue (commits 39d7d567 à 42140f53) —, puis texte rendu conforme et ORDRE du Choul'han Aroukh
# rétabli (commits 368bb709 à b433e894), et ce que le Rav doit relire (traductions
# nouvelles, 25 points d'encadrés que le texte restauré contredit ou nuance) est dans audit/oh-niveau1-a-relire-rav.md.
# Le faux positif du chapeau (67:1, 97:1) a disparu avec la réparation. Relevé : une PILE, pas une
# liste de corrections, dans audit/orah-haim-recopie-niveau1.txt.
# Elle a redressé la LECTURE de verifier-couverture-encadres.py (non modifié), dont la mesure est
# « séifim moins blocs » : il imprimait « 264 séifim absents » pour Orah Haïm le 8 octobre, et en
# imprime 209 le 9 (24 simanim : au 32, des séifs réellement absents, et déclarés ; dans les 23
# autres, dont 12 des 14 restaurés, des séifs regroupés dans un bloc passent pour absents). 133 séifim étaient
# réellement absents de la page française (139 dans l'union des trois langues) ; les autres, 131 par
# différence, étaient présents — regroupés à plusieurs dans un bloc, ou réordonnés — et non absents.
# Depuis la restauration du 9 octobre 2026, il n'en reste que 40, tous au siman 32, et déclarés.
python3 scripts/verify-oh-niveau1-source.py 8 9 10
python3 scripts/verify-oh-niveau1-source.py --tous --bref

# Garde-fou d'URL et de langue — le nom du FICHIER promet une langue, le lang= en
# annonce une, et le corps en parle une troisième. verifier-langues.py compare la
# page à ce qu'elle DÉCLARE ; celui-ci la compare à ce que son URL PROMET, et
# compare les trois corps entre eux pour repérer une variante jamais traduite.
python3 scripts/verifier-url-langue.py --path sources/yoreh-deah [--details]

# Garde-fou de liens — rejoue les rewrites et redirects de vercel.json pour savoir
# si chaque lien interne mène à un fichier réel. Un lien vers /yd/133/ pendant que
# le siman 133 n'existe pas est un 404 en production que rien d'autre ne voit.
python3 scripts/verifier-liens.py

# Garde-fou de charpente — la page est-elle un document HTML bien formé ? Un « < »
# à l'intérieur d'une balise, une balise unique en double, un <style> jamais refermé,
# un fichier qui ne finit pas par </html>, un <html> sans lang. Le navigateur
# s'accommode de tout cela en silence : trois index du siman 132 ont été publiés
# portant <body<body class="…"> sans qu'aucun autre contrôle ne bronche.
python3 scripts/verifier-balises.py [--path …] [--lignes]

# Garde-fou de mise en page — la classe employée par la page est-elle définie
# quelque part d'atteignable, son <style> inline ou une feuille qu'elle charge ?
# Sinon le bloc n'est pas mal mis en page : il ne l'est PAS DU TOUT. 87 pages
# étaient dans ce cas, dont des tableaux de psak où « Interdit » et « Permis »
# s'affichaient en noir, et des gloses <small> de Sefaria indistinguables du
# texte du Mehaber. `fix-classes.py` pose la forme MAJORITAIRE du dépôt.
python3 scripts/verifier-classes.py [--path …] [--lignes]

# Garde-fou de langue des liens — un lien interne mène-t-il à la page de la MÊME
# LANGUE ? verifier-liens.py ne juge que l'existence du fichier, et depuis une
# page -he un lien vers niveau-2-lamdan.html mène à un fichier qui existe très
# bien : le fichier FRANÇAIS. Deux formes, toutes deux contrôlées — relative
# (niveau-2-lamdan.html) et absolue (/yd/160/ au lieu de /yd/160/he), la seconde
# étant la pire puisqu'elle vise une URL publique. 1841 liens étaient fautifs.
python3 scripts/verifier-liens-langue.py [--path …] [--lignes]
python3 scripts/fix-liens-langue.py [--dry-run]   # ne réécrit jamais vers une variante absente

# Garde-fou de couverture — chaque séif a-t-il son encadré, et la page a-t-elle le séif ?
# Mesure la PLACE et non l'intitulé : il reprend l'ancrage du moteur d'encadrés et
# regarde si un encadré se trouve dans l'étendue du séif, quel que soit le mot qui
# l'introduit. Né d'un chiffre faux — compter « Ce que dit ce séif : » donnait
# « 38 simanim faits sur 241 » pour Orah Haïm, qui est en réalité servi partout ;
# un lot entier était prêt pour six simanim qui les avaient déjà. Il a trouvé
# davantage : 31 simanim dont le niveau 1 ne reproduit qu'une PARTIE du siman
# (264 séifim absents en Orah Haïm, 104 en Yoré Déa), dont 28 sans le déclarer.
# ⚠️ CES 264 COMPTENT DES BLOCS, PAS DES SÉIFIM (mesure « séifim moins blocs ») :
# verify-oh-niveau1-source.py, séif par séif, trouvait le 8 octobre 2026 133 séifim
# réellement absents de la page française d'Orah Haïm, dans 15 simanim ; les autres
# étaient présents, regroupés ou réordonnés. Lire ce chiffre-ci comme un plafond. Depuis
# la restauration du 9 octobre, il n'en reste que 40, au seul siman 32, déclarés ; la
# porte de couverture, elle, imprime 209 (voir le bloc de verify-oh-niveau1-source).
python3 scripts/verifier-couverture-encadres.py --section orah-haim [--bref] [N …]

# Garde-fou de dénombrement — la page COMPTE-t-elle juste ? « c'est le seul séif
# où… », « l'un des trois plus longs », « son plus long ס״ק ». Cinq de ces phrases
# étaient fausses sur le seul siman 234, les neuf autres portes vertes : aucune
# citation n'était fausse, c'est la phrase qui les compte qui l'était. Trois
# verdicts qui ne se valent pas — FAUX (le nombre annoncé n'est pas celui de la
# source) et DÉSACCORD (les trois langues ne disent pas le même nombre) sortent
# en 1 ; À VÉRIFIER liste ce qu'aucune machine ne tranche, et ne bloque jamais.
python3 scripts/verifier-denombrements.py [--path …] [--a-verifier] [--bref]

# Garde-fou d'ancrage — l'entrée d'appareil est-elle rattachée au BON séif ?
# « le psak du Taz ס״ק י״ח (seif 7) » promet au lecteur de l'y trouver ; au siman 119
# ce ס״ק est ancré au séif 19. verifier-citations.py ne le voit pas : il confronte le
# verbatim, qui est exact, et ne regarde pas où le ס״ק est posé. La vérité est l'ancre
# <i data-commentator="…" data-order="N"> que Sefaria place DANS le texte du Choul'han
# Aroukh. Rend des CANDIDATS et sort toujours en 0 — une page peut citer le ס״ק d'un
# autre séif quand il éclaire le sien. Ce qui compte : l'écart isolé, à ouvrir, et
# l'écart SYSTÉMATIQUE, tout un siman décalé, qui est le piège de la règle 22-bis.
#
# ⚠️ ELLE N'AVAIT JAMAIS CONFRONTÉ UN SEUL ס״ק DE LA MICHNA BEROURA — l'ouvrage le plus
# cité du dépôt — et elle sortait verte. Son motif exigeait l'ADJACENCE de
# `data-commentator="…"` et `data-order="…"`, or Sefaria intercale parfois un `data-label`,
# et la Michna Beroura ne porte AUCUN `data-order` : son numéro de ס״ק est un NUMÉRAL
# HÉBREU dans `data-label`. Mesuré sur `Shulchan_Arukh,_Orach_Chayim.246` : 90 ancres,
# 37 captées, 53 RATÉES — les 34 de la Michna Beroura, 15 Be'er HaGolah, 3 Ateret
# Zekenim, 1 Eshel Avraham. Soit 59 % des ancres.
# ET ELLE NE COUVRAIT QU'UN LECTEUR SUR TROIS : `SF_` était sensible à la casse et ne
# lisait pas « Seif » (16 070 occurrences dans sources/), `SK_` n'acceptait que le ס״ק
# hébreu (5 722 formes latines). Le cas témoin du siman 267 existe dans les trois langues
# et seul l'HÉBREU était lu — le français, langue par défaut du site, était muet. C'est
# mot pour mot la leçon de verifier-troncatures.py : UNE CLAUSE NE COUVRE LE LECTEUR QUE
# DANS LA PAGE QU'IL A SOUS LES YEUX. Et le groupe `sk2` était capté sans jamais être lu :
# « MB ס״ק ה-ו » promet DEUX rattachements et un seul était confronté (54 cas).
# ÉTAT MESURÉ, avant → après, site entier :
#   Orah Haïm    0 →   159 confrontations ·   0 écart
#   Chabbat      0 →    32 confrontations ·   9 écarts
#   Yoré Déa   107 →   982 confrontations · 143 écarts
#   TOTAL      107 → 1 173 confrontations · 152 écarts — ×11 · 40 714 ancres lues
#   par ouvrage : Siftei Kohen 573 · Turei Zahav 352 · MICHNA BEROURA 189 ·
#                 Pithei Teshuva 46 · Ba'er Hetev 11 · Magen Avraham 2
# Le défaut du siman 267 est réel : Sefaria ancre MB ס״ק ה ET ו au séif 2 d'OH 267 quand
# la page annonce le séif 3 ; ce qui traite de שומר עמו est le ס״ק ז. Le lecteur qui ouvre
# le ס״ק ה tombe sur les lois du repas avant la nuit.
# ⚠️ ELLE SORTAIT AUSSI VERTE SANS AVOIR RIEN COMPARÉ. `carte()` rendait `{}, 0, 0, 0` sur
# ses TROIS chemins d'échec — exception réseau, `he` vide, `ref` servi ≠ siman demandé —
# c'est-à-dire exactement ce que rend un siman sans rattachement, et `examiner()` rendait
# la main sans même ouvrir les pages. Éprouvé en coupant `urlopen` avec le cache écarté :
# « Rattachements confrontés : 0 », CODE DE SORTIE 0, pas une ligne pour le dire. Les
# trois chemins se déclarent désormais dans `NON_ATTEINTS` AVEC LEUR RAISON, et la porte
# sort en 3 quand rien n'a été confronté. Une lacune de la source et un échec de mesure
# n'y sont PAS confondus : un siman que Sefaria ne numérise pas rend le BON `ref`, `error`
# nul et `he` vide (vérifié sur `Shulchan_Arukh,_Yoreh_De'ah.169`, le seul du dépôt).
python3 scripts/verifier-ancrage.py [N N …] [--path …]

# Garde-fou de troncature — la citation SAUTE-t-elle un passage de sa source sans le dire ?
# Deux familles, et la seconde est invisible à toutes les autres portes. LE TROU : la page
# saute un passage du milieu et recolle les bords — « ונוהגין ללוש כדי שעור חלה… » (242,
# niveau 4) est le Rama mot pour mot, sauf qu'elle retire le crochet [סמך ממרדכי ריש מסכת
# ר״ה] que Sefaria place DANS le texte, sans « … ». LA COUPURE AVANT LA SUITE : la citation
# s'arrête juste avant la clause qui la retourne, et comme elle EST alors une sous-chaîne
# exacte, aucune porte de citation ne peut la voir — elle est verbatim. Deux arbitres l'ont
# trouvée le même jour sur deux simanim : מג״א רמ״ו ס״ק ו coupé sur שרי quand la suite est
# « אבל … וצ״ע … ויש להקל בעת הצורך », et שו״ע הרב רמ״ז:ב coupé sur אסור quand la source
# poursuit « אלא אם כן יש שהות… ». Sur Chabbat : 9 trous et 35 coupures pour 3 554 citations.
# Deux filtres ont fait la différence entre une porte et un bruit : « ואם » retiré de la liste
# des mots qui retournent (83 des 201 premiers candidats, aucun n'était un défaut — « ואם »
# introduit un AUTRE CAS), et la clause qui retourne cherchée AILLEURS DANS LA PAGE avant
# d'être signalée (citer une clause et traiter la suivante à la section voisine est la conduite
# normale d'une page d'étude). Rend des CANDIDATS ; sort en 1 s'il en reste.
#
# ⚠️ ELLE A ÉTÉ MUETTE, ET LA LEÇON VAUT PLUS QUE LA PORTE. Trois défauts la faisaient rater
# SON PROPRE CAS TÉMOIN — שו״ע הרב רמ״ז:ב, celui qu'un arbitre avait trouvé à la main :
#   1. la PONCTUATION DÉTACHÉE — « …בְּיוֹם רִאשׁוֹן , אֶלָּא » : mots[0].strip(',;') rendait la
#      chaîne vide et le test ne passait jamais ;
#   2. le NIKOUD — le Choul'han Aroukh HaRav est servi VOCALISÉ, la source écrit אֶלָּא, la
#      liste porte אלא, et « אֶלָּא ».startswith(« אלא ») est FAUX. On compare les SQUELETTES ;
#   3. le FILTRE TROP LARGE — il balayait les quinze fichiers du siman, les trois langues
#      confondues. La clause venait d'être rétablie dans le fichier HÉBREU : le filtre l'y
#      trouvait et taisait le défaut pour le FRANÇAIS et l'ANGLAIS, qui le portaient intact.
#      Restreindre à la langue ne suffisait pas non plus — la clause vit aussi dans le niveau 4
#      français. UNE CLAUSE NE COUVRE LE LECTEUR QUE DANS LA PAGE QU'IL A SOUS LES YEUX.
# J'avais resserré cette porte QUATRE fois contre des faux positifs, et il a fallu un agent
# extérieur pour trouver qu'elle ratait des vrais. Un garde-fou qu'on ne règle que dans un sens
# devient muet sans qu'on s'en aperçoive.
#
# CHIFFRES RÉELS — et ils ont changé trois fois, dont une fois par une RÉGRESSION :
#   24 septembre 2026 : Chabbat 20 trous · 113 coupures ; Yoré Déa 256 · 1 005 ; Orah Haïm NON MESURÉ
#     (le cache portait UN siman sur 241 — 47 % des répertoires du dépôt jamais passés par la porte).
#   8 octobre 2026, contre le cache rempli entre fin septembre et le 1er octobre (Orah Haïm le
#   1er octobre) — avant les corrections de Sefaria, voir plus bas : Chabbat 11 trous · 91 coupures ; Yoré Déa 37 · 1 369 ; Orah Haïm 292 · 958.
# Ce qui a fait bouger ces chiffres, et chaque point est une façon de se tromper :
#   · le RABATTEMENT : une citation de guemara exacte était accusée d'un TROU contre un Richon
#     qui paraphrase la même guemara (siman 263, Tour). Les TROUS s'effondrent, à appareil
#     identique : 244 → 22 en Yoré Déa, 13 → 5 en Chabbat (29 septembre).
#   · presente() évaluée sur TOUT l'appareil : une citation tronquée de son œuvre, retrouvée
#     telle quelle dans une œuvre voisine qui cite le même passage autrement, était déclarée
#     confrontée — mutisme silencieux, sans aucun compteur. Témoin : Chabbat 353, où la page ne
#     nomme aucune œuvre, où le trou contre le Mehaber est réel, et où l'Aroukh HaChoul'han, qui
#     cite le séif en INVERSANT l'ordre, le masquait. La restriction à l'œuvre visée a rendu
#     +58 TROUS — une population à trier, pas 58 défauts…
#   · …et a ouvert une RÉGRESSION, poussée avant son arbitrage : le nom de l'œuvre était cherché
#     dans une fenêtre qui ENJAMBAIT LES BLOCS — 39 des 58 TROUS gagnés venaient de là : 20 dans le
#     bloc suivant, 12 dans un titre qui précède, 7 dans un bloc précédent. Le nom n'attribue plus la
#     citation que s'il est dans le MÊME élément qu'elle, sa rangée de tableau, ou le src-ref qui
#     la suit.
#   · une cible dont le nom n'est pas un PRÉFIXE du ref servi n'atteint jamais son œuvre
#     (« Beer Hetev » contre « Ba'er Hetev ») ; un préfixe en contient un autre (« Tur » dans
#     « Turei Zahav ») ; et un motif de nom qui ignore la pleine graphie laisse ses citations à
#     une voisine (« שולחן ערוך הרב » en toutes lettres était attribué au Mehaber).
#   · une réponse Sefaria `error` (HTTP 200) était gravée dans le cache comme un appareil complet.
#   · Défaut OUVERT, déclaré dans le script : une attribution juste portée par un TITRE au-dessus
#     du bloc (<h4>ט״ז ס״ק א</h4>) n'est plus lue ; coût mesuré sur le corpus actuel : 0.
# ⚠️ UN CACHE COMPLET COMPARE À UN INSTANTANÉ, ET L'INSTANTANÉ VIEILLIT. Balayage à froid du
# 8 octobre 2026 (audit/troncatures-cache-froid-2026-10-08.txt), 513 simanim retéléchargés :
# aucune œuvre manquante, mais 23 simanim divergeaient du cache rempli entre fin septembre et le
# 1er octobre. Sefaria corrige son texte : surtout des coquilles d'OCR du Beit Yosef OC 342-365
# (« אכילו » → « אפילו », « כטור » → « פטור »), plus un redécoupage de segments au siman 357 et une
# correction de contenu au Biour Halakha 314. Une page qui cite juste était confrontée à la coquille.
# Deux unités, et il faut les deux : les occurrences comptent chaque PAGE atteinte (un défaut
# dans les trois langues est trois lecteurs trompés), les couples comptent le TRAVAIL réel.
# Relevés dans audit/{chabbat,yoreh-deah,orah-haim}-troncatures.txt.
# RÉSERVE À DONNER AVEC LES CHIFFRES : le mot אלא produit des candidats faibles — au siman 100
# de Yoré Déa la suite non citée est « אלא חתיכת גיד וחתיכת אבר מיקרו », une précision de fin
# de ס״ק et non un renversement. Le tri revient au lecteur.
python3 scripts/verifier-troncatures.py --path sources/shabbat/siman-246
python3 scripts/verifier-troncatures.py --section shabbat [--bref]

# Garde-fou d'étiquette — la cellule de niveau 4 nomme-t-elle un séif qui porte ce qu'elle
# annonce ? Les tableaux comparatifs rangent la source par colonne et posent au-dessus de
# chaque cellule une adresse : « OH 243:2 », « Hagaha sur OH 243:2 », « MB 242:3-4 ». Le
# contenu, lui, est le plus souvent une CONDENSATION introduite par `<em>résumé</em> :`, que
# la convention exempte à bon droit du verbatim — une condensation n'est pas une citation.
# L'exemption laissait DEUX trous. Le premier — une condensation peut être FAUSSE (au siman
# 247, une qui inverse le psak : elle attache la condition du בי דואר au cas où l'on a fixé
# un prix, quand le Mehaber ne l'ouvre qu'« ואם לא קצב ») — ne se tranche pas mécaniquement,
# et cette porte ne le prétend pas. LE SECOND, SI : l'ADRESSE elle-même peut mentir.
# Trois questions fermées : le séif existe-t-il · porte-t-il une glose du Rama quand la
# cellule en promet une · le ס״ק existe-t-il dans la Michna Beroura de ce siman.
# Premier balayage de Hilkhot Chabbat : 308 étiquettes confrontées, 26 ANOMALIES sur
# 7 simanim (242, 247-251, 264) — et toutes dans la plage 242-264, comme les troncatures.
# Les 26 ont été corrigées. État des pages au 8 octobre 2026, confronté au cache du 1er octobre
# (la porte ne retélécharge rien quand son cache est complet), trois compartiments : 3 992 étiquettes
# (805 Chabbat · 709 Orah Haïm · 2 478 Yoré Déa), 397 plages déployées sur toute leur étendue
# (la porte ne testait que la borne HAUTE), 5 264 points de source, 0 anomalie, 93 candidats.
#
# ⚠️ CE « 26 » ÉTAIT UN PLANCHER ANNONCÉ COMME UN COMPTE, et trois agents de contrôle l'ont
# établi indépendamment. La porte ne lisait que les chiffres ARABES : les colonnes des fichiers
# HÉBREUX (« או״ח רמ״ז:א », « מ״ב רמ״ט ס״ק יד »), la forme mixte « MB 248 ס״ק ד » employée aussi
# en FR et EN, et la colonne entière du Choul'han Aroukh HaRav n'avaient JAMAIS été confrontées.
# Au siman 264, QUATRE des cinq adresses fausses réelles étaient hors de portée.
# Élargie, elle lit 803 étiquettes au lieu de 308 — dont 148 séifim du Choul'han Aroukh HaRav.
#
# ⚠️ ET L'ÉLARGISSEMENT A EXIGÉ TROIS GARDE-FOUS, chacun trouvé en LISANT la sortie :
#   1. le TIRET DE PLAGE n'a pas d'espaces. « או״ח רמ״ב:א — אין » se lisait « séif 1 à 61 »,
#      car אין vaut 61 en guématrie : 35 des 49 premières « anomalies » étaient ce seul défaut.
#      C'est le piège de verifier-denombrements.py, retrouvé le même jour.
#   2. un NUMÉRAL HÉBRAÏQUE fait une ou deux lettres, ou porte un gershayim au-delà — כלל (80)
#      et דן (54) n'en sont pas.
#   3. « או״ח » NE DÉSIGNE PAS TOUJOURS LE CHOUL'HAN AROUKH : dans un recueil de responsa il
#      nomme une PARTIE — « אגרות משה או״ח ד:נג-נד » est le volume 4, responsa 53-54, non le
#      siman 4. C'était la dernière anomalie du balayage, et elle était fausse.
# Vérifiées à la main contre Sefaria : le siman 249 a QUATRE séifim (son chapeau l'écrit,
# « ובו ד סעיפים ») et la page annonce « OH 249:5 » ; ses gloses du Rama sont aux séifim ב
# et ד, la page en annonce trois, aux séifim 1, 3 et 5. Le siman 250 a SIX ס״ק de Michna
# Beroura, la page annonce « MB 250:14-17 ».
# ⚠️ Le décalage de la פתיחה se MESURE, jamais ne se suppose : dans Mishnah_Berurah.N la
# première entrée est la פתיחה non numérotée aux simanim 69, 178, 211 (Orah Haïm) et 243, 248,
# 253, 308, 317, 319, 337 (Chabbat) — recensement exhaustif dans verifier-citations.py —, et ne
# l'est PAS aux simanim 250 et 251. La porte regarde si la première entrée porte le marqueur « (א) ».
python3 scripts/verifier-etiquettes.py --section shabbat [--bref]
python3 scripts/verifier-etiquettes.py 249

# Garde-fou du plan d'étude — le Daat Yomi couvre-t-il les simanim qu'il annonce ?
# verifier-limoud.py compare deux CHEMINS (le tableau des pages et le JSON du
# courriel) et vérifie qu'ils s'accordent ; il ne compare ni l'un ni l'autre au
# Choul'han Aroukh, et tous deux s'accordaient sur un plan tronqué. Mesuré le
# 23 septembre 2026 : 739 séifim programmés pour 1 053 réels — 314 ne l'étaient
# AUCUN jour, sur quarante simanim. Deux formes : le plan s'arrête sous le compte
# (siman 298 au séif 10 quand le texte dit « ובו טו סעיפים », siman 301 au 14 pour
# 51), ou il le dépasse (siman 258, quatre séifim annoncés pour un seul réel).
# RACINE : le tableau SEIFIM_COUNT de generate-limoud-plan.cjs était écrit en dur
# et, son commentaire le disait, « extrait des niveau-1-base.html » — le plan
# héritait donc de la troncature des PAGES au lieu de suivre la source. Le compte
# vient désormais de data/seifim-count.json, tiré de Sefaria.
python3 scripts/generer-seifim-count.py --sections shabbat orah-haim [--write]
python3 scripts/verifier-plan-limoud.py [--bref]
# ⚠️ generate-limoud-plan.cjs S'EXÉCUTE AU require() : ne jamais l'importer pour
# le tester — il réécrit le plan, 1 959 pages limoud/ et les bandeaux d'accueil.
# Régénérer déplace toutes les dates à venir pour des abonnés en cours de plan :
# c'est une décision éditoriale, pas un correctif.

# Generate a siman's index page from data/simanim/siman-XXX.json (does NOT generate study levels — those are written by hand)
node scripts/generate-siman.js --siman XXX [--force] [--no-sitemap]
```

There is no linter, and no test suite for CONTENT: `npm test` (tests/chat/, see « Le chat » below) checks only the chat's server wiring. For content, three complementary gates stand in for one: `scripts/audit-simanim.py` checks **structure** (boilerplate, missing files, desynced TOC), `scripts/verifier-citations.py` checks **content** (does each Hebrew quote actually exist at the reference it claims?), and `scripts/verifier-langues.py` checks **language** (is the body of `X-en.html` actually English — and is its `<title>`/`og:title`/`description`?). None subsumes the others — a page can be 174/174 conforme, carry no false citation, and still be a French page served under `lang="en"`, which is what four pages of simanim 304 and 322 were; 212 further pages had a correct body under a French head, which only the third scale of `verifier-langues.py` can see. Run all three before declaring content work done; the SessionStart hook (`.claude/hooks/session-start.sh`, remote-only) runs `npm install` then this audit at the start of every web session.

A fourth gate watches what those three structurally cannot see. The four halakhic errors found in the rabbinic audit of August 2026 (simanim 318, 253, 308, 320) passed all three without a single alert, because **no citation was false** — the Hebrew was verbatim, the structure was sound, the language was right; it was the French reasoning built on top that was wrong. Proof: `verifier-citations.py --path sources/shabbat/siman-320` returned 0 anomalies on a page whose séif 320:6 (ש״כ:ו — `מותר לסחוט לימוני״ש`, the decisive permission on lemon) was never mentioned at all. `scripts/veilleur.py` looks for the shared signature of those four: **A** a séif of the Choulhan Aroukh that no page of the siman ever mentions; **B** an absolute formulation (« une seule crainte », « n'est pas … en soi », a crossed Mehaber/Rama attribution), weighted by observed yield; **C** a concept present in level 1 or level 4 but absent from the level-3 synthesis — the site then holds its own correction without knowing it.

**Quatre contrôles de plus sont nés en produisant Yoré Déa 119-145, chacun d'un défaut qu'aucun des autres ne pouvait voir.** Ils ne sont pas facultatifs : chacun a trouvé, sur des pages déjà publiées, quelque chose que les trois portes historiques laissaient passer.

- `verify-yd-source.py` — le texte source lui-même. Les 50 simanim de Yoré Déa antérieurs échouaient tous ; au 9 octobre 2026 il en reste 32, les simanim 87 à 118 (183-200 ont été refaits), et ils divergent de TOUTES les éditions de Sefaria, pas de la seule édition par défaut — ce n'est pas un artefact d'édition. Leur niveau 1 change et omet des mots bien plus qu'il ne développe des abréviations (mesure ponctuelle du 8 octobre, contre l'édition la plus proche de chaque siman, Wikisource comprise, script non conservé : de l'ordre de 700 mots changés et 200 omis, pour 164 abréviations développées). `verifier-citations.py` ne le voyait pas, parce qu'il juge les citations, pas la recopie du texte de base.
- `verifier-url-langue.py` — l'URL contre le contenu. A trouvé 49 pages dont le `lang=` contredit le nom du fichier et 100 variantes jamais traduites, toutes dans les 50 simanim antérieurs.
- `verifier-liens.py` — 27 liens morts en production, dont des renvois vers `/oh-quotidien/` pour des simanim qui vivent sous `/oh/`.
- `verifier-balises.py` — 11 défauts de charpente sur 6 528 pages : `<body<body class="…">` dans trois index du siman 132, un `<li` sans chevron fermant dans un niveau 1 hébreu de Chabbat, des `<em>` à l'intérieur d'un `content=` de meta description.

**Deux autres sont nés en produisant Yoré Déa 146-166**, et ils ne regardent ni le texte ni la langue de la page mais ce qu'elle PROMET au lecteur :

- `verifier-classes.py` — la classe employée est-elle définie quelque part d'atteignable ? 87 pages ne l'avaient pas, dans les trois compartiments. Le bloc n'y était pas mal mis en page, il ne l'était pas du tout : deux colonnes nues avec l'hébreu dans le sens du français, des tableaux de psak où « Interdit » et « Permis » s'affichaient en noir, et — le plus grave — des gloses `<small>` que Sefaria insère À L'INTÉRIEUR des seifim, rendues à la taille du texte principal et donc indistinguables de la parole du Mehaber.
- `verifier-liens-langue.py` — le lien mène-t-il à la page de la même langue ? **1 841 liens** ne le faisaient pas. `verifier-liens.py` sortait vert : le fichier visé existe parfaitement, c'est le fichier français. Le défaut a deux formes, relative et absolue, et j'ai corrigé trois cas de la seconde à la main sur un lot avant de découvrir qu'il y en avait 224.

**Un dixième est né en produisant Yoré Déa 229-234**, du premier lot jamais soumis à une
relecture adversariale — laquelle a trouvé **26 défauts les neuf autres portes vertes** :

- `verifier-denombrements.py` — **la page compte-t-elle juste ?** Le siman 234 affirmait
  cinq dénombrements dont aucun n'était exact : « l'un des trois plus longs de tout Yoré Déa »
  (il est quatrième, derrière les simanim 331, 267 et 201), « le plus long ס״ק du Taz »
  (il est troisième), « le seif le plus long après le 5 » (le 5 est quatrième), « l'un des
  deux endroits où les Nekoudot HaKessef défendent le Rama » (une seule des cinq entrées le
  fait), « LES deux endroits où l'appareil s'arrête sur un צריך עיון » (il y en a quatorze).
  Aucune citation n'était fausse ; le verbatim était exact, la langue juste, la structure
  saine. **Corollaire appris au premier tour de correction : remplacer une affirmation
  absolue fausse par une énumération fermée également fausse n'est pas une correction.**
  D'où le choix de signaler aussi les énumérations fermées, et de préférer partout une
  forme ouverte (« notamment aux seifim 22, 49, 51 et 57 ») — ou de ne rien écrire.
- `verifier-ancrage.py` — **le ס״ק cité est-il sur le séif annoncé ?** J'ai d'abord décrit
  sa portée comme « volontairement étroite : 101 rattachements confrontables sur les 424
  simanim, 91 conformes, 10 non ». **Cette étroitesse n'était pas un choix, c'était une
  cécité** — et c'est la leçon à garder de cette porte. Elle ne lisait pas les ancres de la
  Michna Beroura, ni « Seif » avec une majuscule, ni la forme latine du ס״ק, ni la seconde
  borne d'une plage ; et sur trois chemins d'échec elle rendait un zéro impossible à
  distinguer d'un compartiment sans rattachement. Réparée, elle confronte **1 173
  rattachements dont 189 de Michna Beroura** (×11), en rend **152 candidats**, et **refuse
  de conclure** (code 3) quand la source n'a pas répondu. Le Taz ס״ק י״ח du siman 119, donné
  au séif 7 dans les trois langues quand son ancre le pose au séif 19, reste dans le relevé.
  Candidats dans `audit/ancrage-candidats.txt` ; aucune page n'a été modifiée.
  **Un chiffre bas n'est pas une portée modeste : c'est d'abord une hypothèse à éprouver.**

Ce contrôle a été **beaucoup plus difficile à rendre juste qu'à écrire**, et la leçon vaut
d'être gardée : son premier essai rendait **118 « FAUX » sur le seul siman 228, tous
imaginaires**. Quatre causes, toutes instructives :
1. en hébreu, tout mot court devient un nombre si on le lit en guématrie — `בכל` valait 52,
   `אלו` 37 ; d'où l'exigence du gershayim ;
2. `ושמונה` contient `מונה` : sans frontière de mot hébraïque, « deux cent dix-huit séifim
   de l'Aroukh HaChoul'han » passait pour un dénombrement du Choul'han Aroukh ;
3. **la proximité du mot « siman » ne prouve pas qu'on compte le siman** — « The two seifim
   say one thing in two ways » était confronté aux six séifim du siman 182 parce que le mot
   traînait dans la phrase suivante ; seuls un verbe de dénombrement ou un possessif comptent ;
4. et surtout : **une citation n'affirme pas, elle rapporte**. Le chapeau du siman 234 annonce
   `ובו ע״ב סעיפים` — soixante-douze — quand l'édition suivie en découpe soixante-quatorze,
   et la page le dit noir sur blanc. Lui reprocher ce nombre, c'était lui reprocher la source.
   Sont donc exempts : le contenu entre « … », les `div.translation` et `.comment-source`,
   la formule `ובו … סעיפים` partout où elle paraît (c'est la formule du livre), et tout
   nombre attribué au chapeau (« Titre du siman : … et il comporte cinq seifim », siman 164).

Après resserrement : **204 dénombrements réellement confrontés à la source sur les 148
simanim de Yoré Déa, zéro faux, zéro désaccord entre langues** — et 6 104 formulations
rendues au relecteur. Le compte des confrontations est imprimé exprès : une porte qui ne
compare rien et sort verte est pire qu'une porte absente.


La leçon commune à ces deux-là, et elle vaut d'être retenue : **un correctif appliqué à la main sur les cas qu'on a vus n'est pas un correctif**. `fix-two-col.py` a réparé 27 pages ; le même défaut est revenu la semaine suivante sous une autre classe, puis sous la forme d'un lien. Chaque fois qu'un agent signale un défaut « local », mesurer d'abord son étendue réelle — elle a été plus grande que le signalement dans tous les cas sans exception.

Deux défauts trouvés à la main pendant ces lots n'ont **toujours pas** de garde-fou, et méritent l'œil du relecteur : (a) une citation dont la référence vit dans un `<p class="src-ref">` à la ligne SUIVANTE échappe entièrement au contrôle, l'extraction étant ligne à ligne — `scripts/plier-citations.py` replie ces blocs, 600 citations des simanim 123-130 n'avaient jamais été confrontées à leur source ; (b) un titre de section en hébreu dans une page française, noyé dans un corps par ailleurs traduit, passe sous le seuil de `verifier-langues.py` — vu sur le niveau 4 du siman 144, dont les huit titres et le sommaire étaient hébreux en FR et en EN. Même chose pour `scripts/fix-two-col.py` : 27 pages employaient les classes `daat-two-col` sans charger la feuille qui les définit, et leur bloc n'était pas mis en page du tout.

The recurring pattern is worth stating plainly, because it dictates where to look: in every case **levels 1 and 4 were correct** (they translate the primary text) and the error was born in the **pedagogical synthesis**, from where it spread to the derived `/questions/` pages and to the index metadata. The veilleur produces **candidates, never verdicts**, and never writes into a page: `--signalements` files them in the reader-report registry as `NEEDS_RABBINIC_VALIDATION`, deduplicated server-side, so the Rav triages machine findings and reader reports in one place. `.github/workflows/veilleur.yml` runs it every Sunday (needs the `ADMIN_PASSWORD` repo secret to file; without it, it reports only).

## Le chat : ce qui est câblé côté serveur, et pourquoi (28 septembre 2026)

Trois constats de l'interface publique ont montré que la qualité du chat ne tient pas au seul
prompt. Chaque correctif vit dans un module partagé par TOUTES les voies de réponse (chemin
agentique, corpus-first Haiku, corpus brut, secours à quota épuisé, `chat-corpus.js`) :

- **`api/_reserve.js`** — la phrase de réserve UNIQUE (`RESERVE`, quatre langues) et la consigne
  d'urgence statique (`URGENCE`). Six formulations différentes coexistaient ; le modèle en
  recopiait deux dans une même réponse. Aucun fichier de `api/` ne doit réécrire cette phrase.
- **`api/_urgence.js`** — détection d'un danger vital dans la question. Mesuré : « appelle les
  secours… c'est à ton Rav de trancher ». La détection court-circuite corpus-first, pré-RAG et
  sauvetage à quota, injecte une consigne de priorité devant la question, et sert une consigne
  statique (0 modèle) si aucun modèle n'est disponible. La synthèse forcée a une variante sans
  renvoi au Rav.
- **`api/_sefaria.js`** — chaque résultat porte l'identité de l'ouvrage RÉELLEMENT servi
  (`work`, `author`, `url`, `attribution_note`). Mesuré : `Shulchan_Arukh,_Orach_Chayim.317.4`
  (Karo) attribué au Choul'han Aroukh HaRav. L'URL vient de la ref servie, jamais du jugé.
- **`api/_corpus.js`** — chaque résultat porte sa `nature` (texte source / synthèse du site /
  rubrique de décision) : une synthèse ne prouve pas l'original (borer 319).
- **`api/_date.js`** — la date du jour dans un second bloc système NON caché.
- **`api/_system-prompt.js`** — V3 : hiérarchie unique, états documentaires à la place des
  pourcentages, identification des ouvrages, urgence, périmètre injecté. Le prompt Orah Haïm
  reste un préfixe exact du prompt Yoreh De'ah (cache partagé).

```bash
npm test          # tests/chat/*.test.mjs — outils SIMULÉS, aucun modèle appelé
# Les douze cas A-L contre l'API RÉELLE d'un déploiement (outils, routage, quotas réels) :
DAAT_CHAT_API_URL=https://<deploiement>/api/chat node tests/chat/conversationnel.mjs
```

`npm test` vérifie le câblage et la spécification ; il ne démontre pas le comportement du
modèle. Le banc conversationnel le fait, sur un déploiement de prévisualisation, et dépose son
relevé dans `audit/conversationnel-<date>.md` avec une question de relecture humaine par cas.
Un constat n'est clos qu'après cette passe.

## Ce que le corpus indexe — à lire avant d'écrire du contenu

Deux chantiers avancent en parallèle sur ce dépôt : l'un **écrit le contenu**
(encadrés « Ce que dit ce séif », vérification des citations, audit), l'autre
**maintient la chaîne d'indexation** (extraction, recherche, API du chat). Ce qui
suit est le contrat entre les deux : où écrire pour que le chat vous voie.

**Un encadré n'est indexé que s'il est d'un type connu ET dans une section lue.**
- Types indexés : `definition`, `remember`, `key-point`, plus les tableaux
  « Cas pratiques modernes » (une ligne = un chunk).
- Les encadrés du niveau Lamdan (`hakira-box`, `rishon-card`, `pilpul-box`,
  `machloket-box`, `nafka-mina-box`, `yesod-box`, `teruts-box`, `kashya-box`)
  ne sont **volontairement pas** indexés à part : mesuré sur un banc de 47
  questions de niveau lamdan, les indexer n'apporte **aucun gain** et coûte
  2 à 4 points sur les questions pratiques — leur texte est déjà présent, capté
  par les chunks narratifs de la même page. Les indexer le fragmenterait en deux
  chunks concurrents.
- Les sections « Le texte du Choul'han Aroukh », « Mishnah Berurah — premières
  entrées », « Plan de l'étude » et « Questions de compréhension » ne sont pas
  indexées **en tant que texte** — c'est du source recopié. Mais les encadrés
  RÉDIGÉS qu'on y place le sont : c'est là que vivent les « Ce que dit ce séif ».
  (Ils ne l'étaient pas avant août 2026 : 158 encadrés des lots 7 à 9 étaient
  écrits, publiés, et invisibles au chat.)

**Le build vous avertit — lisez sa sortie.** `npm run build` signale désormais :
un siman indexé sans titre, un fichier de niveau qui ne produit aucun chunk, un
fichier dont l'extraction capte moins de la moitié du texte, et un répertoire de
`sources/` non déclaré dans `SECTIONS` (dont le contenu n'entre dans rien).

**`data/corpus-shabbat.json` n'est plus versionné** — c'est une sortie de build de
34 Mio que GitHub refuserait au-delà de 100 Mio. Il est régénéré par
`vercel-build` et déclaré dans `vercel.json` (`includeFiles`). Après un clone
frais : `npm run build`. Cela supprime aussi le conflit récurrent entre branches
sur ce fichier.

**Le périmètre du corpus n'est plus écrit en dur** dans le prompt système : il est
calculé depuis le corpus (`corpusPerimeter()`). Inutile de le mettre à jour à la
main en ajoutant des simanim.

## Content model — the core of the repo

`sources/` holds **513 simanim** in three compartments — **Orah Haïm quotidien** (`sources/orah-haim/`, 241), **Hilkhot Shabbat** (`sources/shabbat/siman-242/` … `siman-365/`, 124) and **Yoreh De'ah** (`sources/yoreh-deah/`, 148) — counted on disk on 8 October 2026; this line said 424 and 59 for weeks. The catalogue of record is `data/simanim-disponibles.json` — a build output, never hand-edited; count from it or from disk, never from memory. Each siman directory holds an `index.html` plus up to **4 study levels**, and **every page exists in 3 languages**:

| Level | File stem | Audience |
|-------|-----------|----------|
| 1 — Base | `niveau-1-base` | Hebrew text + fluent French translation + explanation |
| 2 — Lamdan | `niveau-2-lamdan` | In-depth pilpoul (Rishonim/Acharonim, hakira, machloket) — body is largely Hebrew |
| 3 — Synthèse | `niveau-3-synthese` | Structured recap for revision |
| 4 — Daat HaRav *(Orah Haïm, Shabbat)* | `niveau-4-daat-harav` | Shitah of the Admour HaZaken (Choulhan Aroukh HaRav + Kountress Aharon) |
| 4 — Halakha lema'asse *(Yoreh De'ah)* | `niveau-4-halakha` | Psak — the ruling as it is practised |

Language convention (applies site-wide, not just simanim): **`X.html` = French (default, `lang="fr"`)**, **`X-he.html` = Hebrew (`dir`/RTL)**, **`X-en.html` = English**. When you change content in one language you must keep the other two in sync — this is the single most common source of inconsistency. Many `scripts/*.py` exist to propagate edits across the trilingual set (translate, add buttons, fix canonicals, audit Rama gloses); prefer adapting one of those to mass-edits by hand.

**Level 4 carries two file stems**, one per compartment: `niveau-4-daat-harav` for Orah Haïm and Hilkhot Shabbat, `niveau-4-halakha` for Yoreh De'ah. A glob on one stem alone silently misses a whole compartment.

Within Hilkhot Shabbat, levels 1–3 exist for all 124 simanim; Level 4 exists for **122** of them. **Simanim 304 and 322 have no Level 4** — the Admour HaZaken did not write them in the Choulhan Aroukh HaRav, so they carry a "bridge page" (🌉 in `PROGRESS.md`) instead. Treat "124 simanim" (corpus / Mehaber) and "122 simanim" (Level 4 / Daat HaRav) as distinct counts; do not collapse them.

Study-level pages are **artisanal**: `generate-siman.js` only builds the repetitive `index.html` (SEO head, JSON-LD, breadcrumb, hero, FAQ). Do not try to industrialize the level pages — generic generated pilpoul has no value, and the audit flags boilerplate as an error.

`PROGRESS.md` is the generated manifest of per-siman/per-level state (✅ written · 🔴 boilerplate · ❌ absent · 🌉 bridge). Other top-level HTML (homepage `index.html`, `chat.html`, `soutenir.html`, `about/faq/communaute`, `blog/`) follows the same trilingual triple.

## URL scheme (vercel.json)

Public URLs are short and canonical; the physical paths are rewritten:
- `/oh/` → catalogue · `/oh/:n` → siman index · `/oh/:n/base|lamdan|synthese|daat-harav` → the 4 levels
- `/oh/:n/he` · `/oh/:n/en` → language variants
- Old `/sources/shabbat/...` paths **301-redirect** to `/oh/...`, so always link via `/oh/`.

When adding pages/levels, add matching `rewrites` in `vercel.json`. The repo deploys as a static site (`outputDirectory: "."`) on Vercel; `main` → daattorah.com (auto-deploy on merge). Security headers and `/api/*` CORS are also set here; `crons` triggers `/api/newsletter` daily.

## API architecture (`api/`, ESM serverless on Vercel, Node 22)

Shared modules are prefixed `_` (e.g. `_kv.js`, `_auth.js`, `_corpus.js`, `_system-prompt.js`, `_sefaria.js`, `_deepseek.js`). State lives in **Upstash Redis** (`_kv.js`) — there is no SQL database. Everything (rate limits, usage/cost tracking, plans, dedications, meta-response cache) is KV keys.

**`api/chat.js`** is the heart and the most complex file — the AI study assistant ("Daat"):
- Agentic loop with **tool use** (Sefaria API, the DAAT corpus, mareh mekomot), **SSE streaming**, and **1h prompt caching** on the long system prompt.
- **Cost-optimized model routing** (`pickModel`): meta/greeting questions → DeepSeek or Haiku (or a KV-cached canned answer, $0); halakhic-depth questions → Opus; otherwise Sonnet. New users get a lifetime "Aperçu Premium" of 3 Opus answers (with per-IP and global daily anti-abuse caps).
- **Corpus-first**: a strong BM25 match in the Rav's own corpus (`data/corpus-shabbat.json`, built by `extract-corpus.js`) is reformulated by Haiku instead of calling Opus/Sonnet. Several behaviors are env-gated (`CORPUS_FIRST_ENABLED`, `CORPUS_MIN_SCORE`, `CORPUS_QUOTA_FREE`).
- Time-budget aware: forces a final synthesis (`tool_choice: none`) past ~50s and hard-aborts at 80s, because Vercel kills the lambda ~90s. Usage/cost **must be written to KV before `res.end()`** (no fire-and-forget in serverless Node).
- Note model IDs are pinned in-file (`claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5`) — update here when bumping models.

**Auth** (`_auth.js`, `auth.js`): passwordless **email OTP** (6-digit code via Resend) → **JWT** session in the `daat_session` cookie. Cookies are `SameSite=None; Secure` on purpose: the chat API is served from `daatai.vercel.app` but consumed from `daattorah.com` (cross-site), so `Lax` would drop them. Pages set `window.DAAT_CHAT_API_URL` to the API origin. Anonymous users get a `daat_guest_id` cookie.

**Monetization / plans**: HelloAsso donations hit `helloasso-webhook.js` (verified via `HELLOASSO_WEBHOOK_SECRET`), which sets the user's plan in KV. Plans: `anonymous`, `free`, `khavroutha`, `beit_midrash`, `beit_midrash_plus`, `yeshiva`, `lifetime` — each with daily + monthly question caps defined in `chat.js`. `dedicaces.js` / `dedicace/[siman].js` drive the dedication banners.

**Admin** (`api/admin/*`, pages under `admin/`): gated by `ADMIN_PASSWORD` / `SOUTIEN_ADMIN_SECRET` via the `X-Admin-Secret` header — **never in the query string**. `api/_admin-gate.js` is the shared door: a **server-side origin refusal** (`origineRefusee` → 403, allowlist extendable with `ADMIN_ALLOWED_ORIGINS`) backed by a matching CORS allowlist (`corsAdmin`) and a **failure counter** in KV (`freinage` / `echecAdmin` / `reussiteAdmin`, 5 per IP and 200 global per 15 min, `logs:admin`). Both exist because of what was measured in production on 22 September 2026: ten wrong secrets in a row returned ten plain `401`s with no throttling, and `Access-Control-Allow-Origin: *` was set **before** the auth check — so the `401` itself was readable cross-origin, and any web page could have the secret brute-forced by ordinary visitors' browsers. The origin check is **server-side on purpose**: the CORS allowlist alone did NOT hold — measured in production on 23 September 2026, **ten of fourteen** requests from a foreign origin still got `Access-Control-Allow-Origin: *`, because `vercel.json` sets that header on `/api/` at the platform level and the `/api/((?!admin/).*)` exclusion is not applied reliably. The deeper lesson is not syntax: **CORS is a browser control**. It asks the browser not to let a page READ the response; it never stops the request arriving, and it protects nothing that is not a browser. A page hosted elsewhere now gets `403` before the password is ever compared. The gate **fails open** when KV is unavailable: it still demands the password, and closing there would lock the real admin out on every Upstash hiccup. **The JWT path is now in place, and it is purely additive**: `adminParJeton` accepts the site's own session cookie when its email is listed in `ADMIN_EMAILS` (falling back to `ADMIN_EMAIL`), and falls back to the shared password otherwise. With the variable unset **nothing changes at all** — the password keeps working exactly as before, so configuring it can never lock the real admin out. What it buys that a shared password cannot: an **identity** (who changed a plan), an **expiry**, individual **revocation**, and no secret to pass around. ⚠️ The session cookie is `SameSite=None` by necessity (API on daatai.vercel.app, site on daattorah.com), so it rides along on requests a third-party page triggers: the **origin refusal is what stops CSRF**, and it becomes *more* important once a cookie can authenticate, not less. **Les pages `/admin` (`middleware.js`, octobre 2026)** : la session par courriel d'une adresse de `ADMIN_EMAILS` y entre sans mot de passe (le JWT HS256 est vérifié par `crypto.subtle`, l'Edge Runtime n'ayant pas `jsonwebtoken`) ; une visite sans identifiants est renvoyée vers `/connexion-admin.html` (code par courriel, ou lien `?motdepasse` qui rouvre la fenêtre Basic Auth habituelle) ; un mot de passe faux reçoit toujours le 401. Tests : `tests/admin/middleware.test.mjs` (dans `npm test`). `api/soutenir.js` passes its **admin** actions (`recent`, `admin-all`, POST, DELETE) through the same door since 1 October 2026 (origin refusal → throttle → constant-time check, no `?secret=`); its **public** GETs (the wall and the month's stats, read by `soutenir.html` from daattorah.com) keep an open CORS on purpose. One thing still open: the password comparison is not constant-time in `/api/admin/*`. `api/daily-pack.js` and `api/social.js` still accept `?secret=` **on purpose**: they use `CRON_SECRET` and serve a browser login page that puts it in the URL; closing that needs a cookie-based login, not a one-line change.

### Environment variables

Set in Vercel (never committed; `.env` is git-ignored). Core: `ANTHROPIC_API_KEY`, `UPSTASH_REDIS_REST_URL`/`_TOKEN` (and `KV_REST_API_*`), `JWT_SECRET`, `RESEND_API_KEY` (+ `RESEND_FROM_EMAIL`), `DEEPSEEK_API_KEY`, `HELLOASSO_WEBHOOK_SECRET` (+ `HELLOASSO_FORM_*` URLs), `ADMIN_PASSWORD`/`ADMIN_EMAIL`/`SOUTIEN_ADMIN_SECRET`, `CRON_SECRET`. Behavior flags: `CORPUS_FIRST_ENABLED`, `CORPUS_MIN_SCORE`, `CORPUS_QUOTA_FREE`, `SOUTIEN_MONTHLY_TARGET`.

## Conventions & gotchas

- **Citation convention**: quotation marks are reserved for **verbatim** text. A condensation of a seif is introduced by `<em>résumé</em> :` (`תמצית` / `summary`) and is not judged by `verifier-citations.py`. Anything inside quotes must exist word-for-word in the cited source or the gate fails. This is what makes the gate meaningful — before it, every Level 4 table cell wore quotation marks whether it quoted or paraphrased, and a fabricated citation looked exactly like its forty legitimate neighbours. An ellipsis inside quotes is still fine (`« A… B »` means A and B are each verbatim); each segment is checked separately.
- **Trilingual parity**: a change is not done until FR, HE, and EN are updated consistently.
- **Corpus is derived**: after editing siman HTML that should be searchable by the chat, rerun `npm run build` so `data/corpus-shabbat.json` and `data/simanim-disponibles.json` reflect it.
- **`data/corpus-shabbat.json` n'est plus versionné** (34 Mio réécrits à chaque build, et GitHub refuse un fichier >100 Mio). Il est régénéré par `vercel-build` avant le bundling des fonctions et déclaré dans `vercel.json` (`includeFiles`). **Après un clone frais : lancer `npm run build` avant tout script local qui lit le corpus.**
- **Don't hand-edit generated files**: `PROGRESS.md`, `data/simanim-disponibles*.json`, `data/corpus-shabbat.json`, `assets/js/chat-widget.min.js`, `sitemap.xml` are build outputs.
- **Visual identity** (used throughout the inline CSS): Navy `#1A1F3A`, Or `#C5A55A`, Crème `#FAF6EE`; fonts Frank Ruhl Libre (Hebrew) + Cormorant Garamond.
- **README.md is stale** (describes an old single-siman layout with different level names) — trust this file, `vercel.json`, and `scripts/README.md` instead.
