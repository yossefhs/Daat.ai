# Cahier des charges — production de Yoré Déa

Ce fichier est le brief transmis à chaque agent chargé de produire un ou plusieurs
simanim de Yoré Déa. **Il a vécu dix-sept lots dans `/tmp`, et un redémarrage de
conteneur l'a effacé** — trente-trois règles nées chacune d'un défaut réel,
perdues d'un coup. Il est donc versionné ici, où il survivra.

Reconstruit le 16 septembre 2026 depuis l'histoire du dépôt : chaque règle avait
été consignée dans le message de commit du lot qui l'a fait naître, ce qui est la
seule raison pour laquelle cette reconstruction est possible. **Écrire d'où vient
une règle n'est pas de l'ornement : c'est ce qui permet de la retrouver.**

---

## CONTEXTE

Dépôt `/home/user/Daat.ai`. Compartiment **Yoré Déa** : `sources/yoreh-deah/siman-N/`
(et non `orah-haim`). Site trilingue : `X.html` = FR (`lang="fr" dir="ltr"`),
`X-he.html` = HE (`lang="he" dir="rtl"`), `X-en.html` = EN.

### Les 5 pages × 3 langues = 15 fichiers par siman

```
index{,-he,-en}.html
niveau-1-base{,-he,-en}.html        → texte source + traduction fluide + explication
niveau-2-lamdan{,-he,-en}.html      → pilpoul (Richonim/Aharonim, hakira, ma'hloket)
niveau-3-synthese{,-he,-en}.html    → récapitulatif structuré pour la révision
niveau-4-halakha{,-he,-en}.html     → HALAKHA LEMA'ASSÉ (psika pratique)
```

⚠️ En Yoré Déa le niveau 4 s'appelle `niveau-4-halakha`, **pas** `niveau-4-daat-harav` :
l'Admour HaZaken n'a pas écrit de Choul'han Aroukh sur Yoré Déa. **Ne cite jamais
« שולחן ערוך הרב » sur un siman de Yoré Déa.** Le niveau 4 s'appuie sur le Chakh, le
Taz, le Baer Hetev, le Pit'hei Techouva, les Nekoudot HaKessef, le Rambam et les
poskim — chacun avec sa référence réelle.

### URLs canoniques

```
/yd/N/  · /yd/N/he  · /yd/N/en
/yd/N/base      · /yd/N/base/he      · /yd/N/base/en
/yd/N/lamdan    · /yd/N/lamdan/he    · /yd/N/lamdan/en
/yd/N/synthese  · /yd/N/synthese/he  · /yd/N/synthese/en
/yd/N/halakha   · /yd/N/halakha/he   · /yd/N/halakha/en
```

---

## LES RÈGLES

### 1 — Anti-fabrication (ABSOLUE)
Tout ce qui est entre « … » doit exister **mot pour mot** dans la source citée.
Aucune exception, aucun « à peu près ». Une condensation s'introduit par
`<em>résumé</em> :` (`תמצית` / `summary`) et n'est pas jugée par le vérificateur.

### 1-bis — Le chapeau se recopie en entier
Le chapeau d'un siman (`titre. ובו N סעיפים:`) fait partie du texte source et se
recopie **tout ou rien**, y compris quand il annonce ce que le siman ne traite pas
(voir règle 27, cas du 216) ou un nombre de seifim faux (cas du 234).

### 2 — Le ktiv de la source ne se « corrige » pas
`מתר` et non `מותר`, `חיב` et non `חייב`, `אסר` et non `איסור`. Le Rambam et le
Choul'han Aroukh emploient des graphies défectives : les recopier est la règle,
les « corriger » est une faute.

### 13 — Les coquilles de numérisation se recopient telles quelles
`סעודת צמוה` pour `מצוה`, `דו` pour `ידו`, `נוונא` pour `גוונא`, une parenthèse
jamais refermée. On recopie, on signale dans la page, on ne restaure jamais.

### 16 — Signale ce que tu vois ailleurs
Un défaut aperçu dans un siman voisin se signale dans le rapport. **Ne le corrige
pas toi-même** : le coordinateur mesure son étendue réelle avant d'agir — elle a
été plus grande que le signalement dans tous les cas sans exception.

### 17 — Les guillemets sont réservés au verbatim
Une paraphrase entre guillemets est une faute, même si le contenu est juste.

### 21 — Les pièges de l'API Sefaria
- L'apostrophe de `Yoreh_De'ah` doit être **`%27`**.
- `Kaf_HaChaim,_Yoreh_De%27ah.N` retombe **silencieusement** sur le Kaf HaHaïm
  d'Orah Haïm. Ne le cite pas.
- `Peri_Chadash_on_…`, `Biur_HaGra_on_…`, `Beer_HaGolah_on_…` renvoient **HTTP 200
  avec un champ `error`**. Un script qui ne teste que le code HTTP les croirait
  disponibles.
- **Baer Hetev** : quatre graphies circulent, une seule échoue — celle avec un *i*.
  `Be%27er_Heitev_…` renvoie HTTP 200 + `error`. Résolvent : `Be%27er_Hetev_…`,
  `Baer_Hetev_…`, `Beer_Hetev_…` — cette dernière étant celle qu'emploie
  `verifier-citations.py`, donc la préférable.
- `Siftei_Kohen_on_…` déclare `sectionNames = [Siman, Seif, Paragraph]`, mais le
  deuxième niveau est en réalité le **ס״ק**, pas le seif.
- `Arukh_HaShulchan,_Yoreh_De%27ah.N` renvoie `he: []` pour les simanim **123-182**
  et **à partir de 203**. ⚠️ **C'est une lacune de NUMÉRISATION, pas de l'œuvre.**
  Il est disponible sur 87-122 et sur 201-202. Ne l'écris jamais « absent ».
- **L'Aroukh HaChoul'han se cite avec son nom** : `(ערוך השולחן יורה דעה ר״ב:ג)` ou
  `(ערוך השולחן יו״ד ר״ב:ג)`. Les deux formes résolvent depuis le lot 201-208 ;
  avant, aucune ne marchait. N'invente pas de contournement.
- Sefaria peut servir **une page HTML « 503 Backend fetch failed »** avec un
  `<!DOCTYPE html>` que `json.load()` fait planter. Réessaie jusqu'à obtenir du
  JSON ; sans cela, un script conclut à tort qu'un ouvrage est absent.

### 22 — Vérifie le nombre de seifim toi-même
Le chapeau et le nombre réel de segments ne concordent pas toujours. **C'est le
nombre de segments qui fait foi** pour `verify-yd-source.py`. Signale tout écart.

### 22-bis — Compte les entrées d'appareil SANS LES APLATIR
Le nombre de ס״ק est `len(d['he'])`, **jamais** le nombre de paragraphes aplatis.
Certains groupes portent deux paragraphes (une note à lemme en gras suivie d'un
ajout qui n'en a pas) ; les aplatir décale toute la numérotation d'un cran.

Sur le siman 208, ce décalage a produit **54 VARIANTE, 3 NON_RESOLU et 84
sans-référence**. Il s'est présenté depuis sur les simanim 201 (151 groupes pour
155 paragraphes), 214, 215, 217 (46 pour 50), 218 et 228 (113 pour 115), et n'a
été évité que parce que les agents l'ont cherché.

Deux garde-fous à écrire avant de générer :

```python
n_sk = len(d['he'])          # jamais sum(len(x) for x in d['he'])
ordres = {int(m.group(1)) for seif in sa_he
          for m in re.finditer(r'data-commentator="Siftei Kohen" data-order="(\d+)"', seif)}
assert sorted(ordres) == list(range(1, n_sk + 1))
```

Puis la **confirmation croisée ancre ↔ lemme** : pour chaque ancre que Sefaria
insère dans le texte du Mehaber, le texte qui la suit doit reprendre le ד״ה du
segment. Mesure le taux de concordance à décalage −1 / 0 / +1. Si 0 ne domine pas
très nettement, la numérotation est fausse. Relevé d'une numérotation juste
(siman 201) : Chakh 0,8 % | 88,8 % | 0,8 % — l'effondrement de part et d'autre est
ce qui compte, pas la valeur centrale.

**Quand un groupe porte deux paragraphes : deux blocs sous LA MÊME référence de
ס״ק, jamais deux numéros.** L'écart existe aussi en sens inverse — le Taz du 201 a
89 ancres pour 88 groupes, deux entrées fondues en un segment. Ne reconstruis rien.

### 23 — Le champ `text` de Sefaria n'est pas une traduction
Pour Yoré Déa c'est une paraphrase française de 1898 (Jean de Pavly), matériellement
fausse par endroits. **Le champ `he` est la seule source.**

### 24 — La conversion des gershayim ne sort pas du texte
Ne convertis `"` en ״ qu'**entre deux lettres hébraïques** (nikoud toléré au
milieu), et `'` en ׳ qu'après une lettre. Sinon tu casses les `content="…"` et le
JSON-LD. Vérifie ensuite que le JSON-LD des trois fichiers parse.

### 25 — Tout hébreu verbatim est encadré de « … », y compris dans un blockquote
Le vérificateur extrait **ligne à ligne** : un blockquote réparti sur plusieurs
lignes n'est jamais reconnu comme un tout.

### 26 — La référence DANS le bloc
Une citation dont la référence vit à la ligne suivante échappe entièrement au
contrôle.

### 26-bis — Un `he-q` de plus de 25 lettres est une citation, même en pleine prose
`verifier-citations.py` traite **tout** `<span class="he-q">` de plus de 25 lettres
comme une citation à vérifier, qu'il soit dans un blockquote ou au milieu d'une
phrase française. Citer un mot fort d'un posek dans ta prose sans lui donner sa
référence le fait sortir en « sans référence ». Donne sa référence à tout hébreu
cité, où qu'il soit.

### 27-bis — La meta description ne prend pas de balisage
Si tu reprends un générateur d'un lot précédent, il insère `desc` dans
`<meta name="description">`, `og:description` et `twitter:description` **sans
retirer les balises**. Une description contenant un `<span class="he-q">` produit
un `content="…<span…"`. Pose un `clean()` et applique-le **aussi** au `headline` et
au `description` du JSON-LD.

### 29 — NE RETAPE JAMAIS UN MOT D'HÉBREU — EXTRAIS-LE
**La règle la plus rentable du chantier.** Écris-toi un outil qui, pour chaque
extrait, le RETROUVE dans le JSON Sefaria téléchargé **par squelette consonantique**
(ne garder que `[א-ת]` des deux côtés) et renvoie la **sous-chaîne réelle** de la
source, jamais ta frappe. **Un extrait introuvable doit FAIRE ÉCHOUER ta
génération.**

Deux raisons, la seconde non évidente :
- le nikoud et la ponctuation de Sefaria ne se retapent pas de mémoire ;
- les segments vocalisés peuvent voir leurs **marques combinantes réordonnées** au
  passage par un terminal : la comparaison littérale échoue alors sur un texte
  identique à l'œil.

Ce filet a attrapé, lot après lot, des dizaines de fautes qu'aucune relecture
n'aurait vues — toutes du ktiv (règle 2). **Le seul endroit où il ne protège pas
est la glose française qui accompagne la citation.**

### 30 — Une citation par ligne, au sens strict
Deux citations sur la même ligne partagent la fenêtre de résolution du vérificateur
et chacune se fait juger contre la référence de l'autre. Vu au siman 142 : r=0,34
sur deux citations exactes.

### 31 — Une parenthèse de source au milieu d'une citation ne se saute pas
Inclus-la, ou coupe avec `…`.

### 32 — Les titres de section se traduisent
`verifier-langues.py` ne les voit pas : les huit titres et le sommaire du niveau 4
du siman 144 étaient hébreux en FR **et** en EN.

### 33 — Une classe reprise d'un gabarit doit être définie
Dans le `<style>` de la page ou une feuille qu'elle charge. Sinon le bloc n'est pas
mal mis en page : il ne l'est **pas du tout**.

### 34 — Les titres sont dans la langue de la page
`<title>`, `<h1>`, `og:title`, `twitter:title` et le `headline` du JSON-LD.
L'hébreu va **entre parenthèses, après** le titre vernaculaire. Aucun vérificateur
ne voit un titre anglais commençant par de l'hébreu, et c'est ce que lisent Google
et les aperçus de partage.

### 35 — Les flèches hébraïques suivent le sens de lecture
En RTL : « précédent » pointe à **droite et se met au début** (`→ סימן …`),
« suivant » pointe à **gauche et se met à la fin** (`… ←`). Le défaut est revenu à
chaque lot (20 liens, puis 3, puis 6, puis 43) — c'est celui qui revient le plus.
⚠️ **Orah Haïm a la convention inverse** (1 443 liens contre 8) : ne « corrige »
jamais un autre compartiment.

### 36 — Un siman sans titre ne s'invente pas un titre
Les simanim **225** et **230** commencent directement par `ובו סעיף אחד:`, sans
intitulé. Le chapeau recopié est exactement ce que Sefaria donne. Le `<h1>` de la
page décrit le contenu, de ta rédaction, et **n'est jamais présenté comme le titre
du Choul'han Aroukh**. Dis-le honnêtement dans la page.

### 37 — Une absence de commentaire n'est pas une absence d'ouvrage
Quand un commentateur ne commente pas un siman (`he: []` **sans** champ `error`) :
une ligne honnête au niveau 1 **et** au niveau 4, renvoyant aux simanim voisins où
on le trouve. **Jamais « n'existe pas », jamais une entrée fabriquée pour remplir
une colonne de tableau.**

---

## CE QUE LE VÉRIFICATEUR NE VOIT PAS

À savoir, parce que c'est là que les vraies erreurs se logent :

1. **Les citations de moins de 25 lettres ne sont jamais confrontées à leur
   source.** Mesuré : 1 204 citations de Yoré Déa sont dans ce cas, dont 319
   portent pourtant une référence précise sur leur propre ligne. Le seuil existe
   pour ne pas accuser les termes techniques mis entre guillemets, et il laisse
   passer les ס״ק complets qui sont simplement courts.
2. **Une attribution croisée Mehaber / Rama est invisible** : le vérificateur
   résout `רמ״א` et `שו״ע` vers le même segment Sefaria.
3. **Les références à חושן משפט ne se résolvent pas du tout** : `RE_SA_HE`
   n'accepte que `או״ח` et `יו״ד`. Une citation verbatim de CM sort en « sans
   référence », donc non vérifiée.
4. **Le raisonnement français bâti par-dessus des citations vraies.** C'est le
   défaut qui a produit les quatre erreurs de l'audit rabbinique d'août 2026 :
   les citations étaient exactes, la structure saine, la langue juste. C'est
   pourquoi **aucune ligne de psak ne doit être écrite sans une entrée d'appareil
   citée à côté d'elle.**

---

## MÉTHODE DE TRAVAIL IMPOSÉE

1. Télécharge **toutes** tes sources dans `scratchpad/yd-NNN/` (gitignoré) avant
   d'écrire une ligne.
2. Écris l'outil de la règle 29.
3. Écris le **niveau 1 dans les trois langues d'abord**, puis l'index, puis les
   niveaux 2, 3 et 4.
4. **Chaque fichier sur le disque dès qu'il est prêt.**
5. **Si ton contexte s'épuise, ARRÊTE-TOI et dis exactement où tu en es.** Un
   siman partiellement écrit se reprend ; un siman bâclé pour « terminer » se
   refait entièrement, et on ne s'en aperçoit qu'après publication.

## AVANT DE RENDRE

Lance et rapporte la sortie de : `verify-yd-source.py N` · `verifier-citations.py
--path … --langues fr,he,en` · `verifier-langues.py` · `verifier-balises.py` ·
`verifier-classes.py` · `verifier-liens-langue.py` · `verifier-url-langue.py`.
Tous doivent sortir à zéro. Supprime les CSV produits dans `audit/`.

**NE FAIS AUCUN COMMIT GIT.** Ne touche à rien hors de tes répertoires et de ton
scratchpad.

## DANS TON RAPPORT

Ce que chaque siman traite **réellement** seif par seif (pas un résumé générique),
les ma'hlokot du niveau 2, la ligne de psika du niveau 4, la sortie de chaque
vérificateur, et surtout **tout point douteux** — une référence qui ne tombe pas
juste, une parenthèse mal placée, une traduction qui repose sur une interprétation
plutôt que sur une correspondance. **Ne les tranche pas : signale-les.**

Et si le relevé que le coordinateur t'a transmis est faux, **suis la source contre
lui** et dis-le. C'est arrivé trois fois (chapitre du Rambam au siman 180, matière
du siman 216, comptage du Chakh au 201) et c'est chaque fois la bonne conduite.
