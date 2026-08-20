# Scripts de build — DAAT

## generate-siman.js

Génère la page d'accueil d'un siman (`sources/shabbat/siman-XXX/index.html`) à partir d'un fichier JSON.

### Usage

```bash
# Générer le siman 247 depuis data/simanim/siman-247.json
node scripts/generate-siman.js --siman 247

# Ou pointer vers un fichier de données précis
node scripts/generate-siman.js --file data/simanim/siman-247.json

# Forcer l'écrasement d'un fichier existant
node scripts/generate-siman.js --siman 247 --force

# Sans mise à jour automatique du sitemap
node scripts/generate-siman.js --siman 247 --no-sitemap
```

### Workflow pour ajouter un nouveau siman

1. Créer `data/simanim/siman-XXX.json` (cf. `siman-247-exemple.json` pour la structure)
2. Lancer `node scripts/generate-siman.js --siman XXX` → produit `sources/shabbat/siman-XXX/index.html` + met à jour `sitemap.xml`
3. Rédiger manuellement les 3 niveaux d'étude :
   - `sources/shabbat/siman-XXX/niveau-1-base.html` (initiation)
   - `sources/shabbat/siman-XXX/niveau-2-lamdan.html` (pilpoul approfondi)
   - `sources/shabbat/siman-XXX/niveau-3-synthese.html` (synthèse magistrale)
4. Référencer le nouveau siman dans `sources/shabbat/index.html` (carte)
5. Mettre à jour `llms.txt` à la racine
6. Commit + push → Vercel/GitHub Pages redéploie automatiquement

### Structure d'un fichier JSON de siman

Tous les champs sont obligatoires sauf `seifText` et `subtitle`. Voir `data/simanim/siman-242.json` pour un exemple complet.

| Champ | Description |
|---|---|
| `number` | Numéro du siman (entier) |
| `numberHe` | Représentation hébraïque (ex : `רמ״ב`) |
| `titleHe` | Titre du siman en hébreu (issu du Choulhan Aroukh) |
| `titleFr` | Titre en français |
| `subtitle` | Sous-titre (optionnel) |
| `description` | Meta description SEO (~155 caractères) |
| `keywords` | Mots-clés SEO séparés par des virgules |
| `teaches` | Tableau des concepts halakhiques enseignés (pour Schema.org) |
| `citations` | Tableau des sources citées (Choulhan Aroukh, Mishna Brura, etc.) |
| `seifText` | Objet `{seif, he, fr}` (optionnel) — texte du seif principal |
| `levels` | Tableau de 3 objets `{num, bar, nameHe, nameFr, desc, href, pdf?}` |
| `faq` | Tableau d'objets `{q, a}` — alimente la FAQPage Schema + section visible |

### Pourquoi le générateur ne produit que la page index ?

Chaque siman a son propre pilpoul, ses propres tableaux de poskim, ses propres concepts. Tenter d'industrialiser les 3 niveaux d'étude ne ferait que produire des pages génériques sans valeur. Le générateur prend en charge ce qui est répétitif (head SEO, JSON-LD, breadcrumb, hero, navigation, FAQ) — la rédaction halakhique reste artisanale.

## audit-simanim.py

Audite l'état réel des niveaux 1-4 de tous les simanim de Hilkhot Shabbat (242-365) : fichiers manquants, contenu générique non réécrit (boilerplate laissé par `generate-niveaux-123.py`), tables des matières du Niveau 2 désynchronisées.

```bash
python3 scripts/audit-simanim.py                  # rapport complet
python3 scripts/audit-simanim.py --quiet          # résumé seul
python3 scripts/audit-simanim.py --write-progress # régénère PROGRESS.md
```

Le script renvoie un **code de sortie non nul** dès qu'une erreur est détectée (boilerplate, fichier absent, TOC désynchronisée). Il peut donc servir de garde-fou — par exemple en hook `SessionStart` ou en pre-commit — pour empêcher de considérer un siman comme « complété » alors qu'il contient encore du contenu générique.

`PROGRESS.md` (racine du dépôt) est le manifeste de progression : il est **généré** par ce script, ne pas l'éditer à la main.

## cout-question.js

Calcule le coût réel d'une question du chat Daat, et la marge de chaque plan payant. Le script **lit les constantes du code** (`api/chat.js` : tarifs des modèles, multiplicateurs de cache, budget d'outils, `MONTHLY_LIMITS` ; `api/_system-prompt.js` : taille du prompt système) — il ne peut donc pas diverger de ce qu'il mesure.

```bash
node scripts/cout-question.js             # tarifs et plafonds actuels
node scripts/cout-question.js --eur 1.08  # taux de change €→$ (défaut 1.08)
```

Il produit deux tableaux : le coût par scénario (corpus-first Haiku, Sonnet standard, Opus typique, Opus cache froid, Opus pire cas) et la marge par plan dans l'hypothèse la plus défavorable.

**À relancer après tout changement** de tarif Anthropic, de modèle dans `MODELS`, de plafond dans `MONTHLY_LIMITS`, ou de taille du prompt système. Les chiffres du commentaire de calibrage dans `api/chat.js` en sont issus — ne pas les recopier à la main.

Deux limites à connaître : la taille du prompt système est une **estimation** (3,5 caractères par token ; pour un compte exact, utiliser l'endpoint `count_tokens` d'Anthropic), et le pire cas suppose que 100 % des questions consomment le budget maximal en repartant d'un cache froid — ce qui n'arrive jamais. Le coût réellement observé est dans `/admin` (champ `cost_usd`).

⚠️ Les coûts sont en **dollars** (les tarifs Anthropic le sont, et le champ KV s'appelle `cost_usd`) ; les recettes des plans sont en **euros**. C'est le seul endroit du projet où les deux unités se rencontrent, d'où le taux de change explicite.

## verifier-citations.py

Confronte chaque citation hébraïque « verbatim » du site à sa source réelle sur Sefaria.

`audit-simanim.py` est un gate **structurel** : il vérifie que les pages existent, qu'elles ne contiennent plus de boilerplate, que les tables des matières sont synchronisées. Il passe à 174/174 sur une page truffée de citations inventées, parce qu'il ne regarde jamais le contenu. Ce script est le gate de **contenu** correspondant.

```bash
python3 scripts/verifier-citations.py                          # tout le site, FR
python3 scripts/verifier-citations.py --langues fr,he,en
python3 scripts/verifier-citations.py --path sources/shabbat/siman-297
python3 scripts/verifier-citations.py --only-absent            # ne liste que les ABSENT
python3 scripts/verifier-citations.py --csv audit/citations-verifiees.csv
```

Il extrait les fragments hébreux présentés comme des citations (`<blockquote>`, guillemets — **pas** `<span class="he-q">`, qui n'est qu'une classe typographique appliquée aussi bien à une citation qu'à la thèse propre de l'auteur), résout la référence qui les accompagne — daf talmudique en lettres (`ברכות מ״ג ע״ב`) ou en chiffres (`Berakhot 43b`), séif du Choulhan Aroukh (`OH 131:1`, `או״ח קל״א:א`), ס״ק de la Michna Beroura —, récupère le texte réel et compare après normalisation : nikoud, ponctuation, guillemets, noms divins, abréviations à gershayim (`הקב״ה` → `הקדוש ברוך הוא`), marqueurs de coupe (`…`, `וכו׳`).

Quatre verdicts : **OK** (la citation figure telle quelle), **VARIANTE** (≥ 0,86 de similarité — écart orthographique ou coupe), **ABSENT** (introuvable dans la source citée), **NON_RESOLU** (référence non reconnue). Seuls les ABSENT demandent une intervention ; le script sort en code non nul tant qu'il en reste, il peut donc servir de gate au même titre que `audit-simanim.py`.

Points de méthode :

- L'extraction se fait **ligne par ligne** — le balisage du site place chaque citation sur sa propre ligne, et un guillemet non apparié ailleurs dans la page ne peut donc pas décaler l'appariement de toutes les suivantes.
- Un bloc marqué contient souvent un préfixe de référence, la citation, puis un commentaire de l'auteur ; seule la portion entre guillemets droits est comparée.
- Les fragments majoritairement latins sont écartés : ce sont de la prose, pas des citations.
- Le cache disque (`scripts/.cache-sefaria/`, git-ignoré) rend les passages suivants instantanés. Le supprimer force un rafraîchissement depuis Sefaria.

### Convention de citation (tableaux du Niveau 4)

Les guillemets sont **réservés au texte littéral**. Une condensation d'un séif est annoncée par `<em>résumé</em> :` (`תמצית` en hébreu, `summary` en anglais) et n'est alors pas jugée par le script.

Cette convention n'est pas cosmétique. Avant elle, les cellules des tableaux comparatifs portaient toutes des guillemets, qu'elles citent ou qu'elles résument — et une citation fabriquée ressemblait exactement à ses quarante voisines légitimes. C'est ainsi que `« טוואן עכו״ם פסול »` (une מחלוקת donnée pour un psak) a survécu à toutes les relectures. En réservant les guillemets au verbatim, on rend le verdict sans ambiguïté : **ce qui est entre guillemets doit exister mot pour mot, sinon le gate échoue** ; le reste est un résumé assumé.

Une ellipse à l'intérieur de guillemets reste légitime — `« A… B »` signifie que A et B sont l'un et l'autre littéraux. Le script vérifie chaque tronçon séparément.

### La fenêtre de référence, et ce qu'elle a coûté

Une référence n'appartient pas à toute la ligne, mais à la citation qu'elle jouxte. Le script fenêtrait d'abord 200 caractères de part et d'autre, symétriquement — et sur une ligne portant deux citations, le daf de la seconde était attribué à la première :

> « כל הטמאים קורין בתורה וקורין ק״ש ומתפללין » — שאין הטומאה מעכבת בדברי תורה, ד« דברי תורה אינן מקבלין טומאה » (ברכות כ״ב.)

La première citation, qui n'a aucune référence, ressortait en `REF_FAUSSE` contre Berakhot 22a. Un sondage à la main sur cinq signalements en a montré **trois de cette espèce** — et une correction en masse aurait donc introduit des erreurs au lieu d'en retirer.

La fenêtre est désormais bornée par les citations voisines : elle s'arrête avant le `«` suivant et après le `»` précédent. Sur le site : **39 signalements disparus, 2 révélés** (des citations qui se lient maintenant à une référence plus proche, et fausse). `REF_FAUSSE` passe de 81 à 55, `INTROUVABLE` de 40 à 29.

La leçon vaut au-delà de ce script : un compteur de défauts n'est pas une liste de défauts tant qu'on n'a pas mesuré sa précision sur un échantillon.

⚠️ Un verdict **OK** signifie que le texte cité existe à la référence donnée — **pas** que le raisonnement halakhique qui l'entoure est juste, ni que l'attribution (« אמר רבא », « הגהת הרמ״א ») est la bonne. Le script attrape les citations fabriquées et les dafim faux ; il n'attrape pas une citation exacte mise au service d'une conclusion fausse. Cela reste du ressort de la relecture du Rav (`audit/relecture-rav.md`).

## verifier-langues.py

Vérifie que chaque page est écrite dans la **langue qu'elle annonce**.

Le site tient trois versions de chaque page — `X.html` en français, `X-he.html` en hébreu, `X-en.html` en anglais — et rien ne vérifiait que le corps correspondait au suffixe. Une page pouvait donc porter `lang="en"`, servir `/oh/304/base/en`, et afficher un corps **entièrement français** : c'était le cas de quatre pages complètes (simanim 304 et 322, niveaux 1 et 3) et de vingt-cinq blocs isolés dans huit pages hébraïques. Aucun autre gate ne pouvait le voir — `audit-simanim` juge la structure, `verifier-citations` les citations hébraïques, `verifier-traductions` la longueur des traductions par rapport à leur source ; tous trois passent au vert sur une page entière restée dans la mauvaise langue.

```bash
python3 scripts/verifier-langues.py              # tout le site
python3 scripts/verifier-langues.py --lignes     # + la liste de travail du traducteur
python3 scripts/verifier-langues.py --path sources/shabbat
```

Deux échelles, parce que le défaut se présente sous deux formes.

**La page entière** se voit à la domination : on compte des mots-témoins choisis pour ne jamais apparaître dans l'autre langue ni dans une translittération (`l'akum`, `d'oraisa`), et l'on ne conclut que sur une domination — une page anglaise cite légitimement du français, l'inverse aussi. Pour l'hébreu le test est plus sûr encore : une page `-he` dont le corps compte plus de lettres latines que de lettres hébraïques n'est pas une page hébraïque.

**Le bloc isolé** demande un second test, ligne à ligne — cinq à six paragraphes de séifim restés français au milieu d'une page anglaise complète ne déplacent pas la domination. Trois neutralisations ont été nécessaires pour que le seuil veuille dire quelque chose : les `<script>` (le dictionnaire i18n porte les trois langues dans *chaque* page), les commentaires HTML (`<!-- BANDEAU DE DÉDICACE… -->` est français partout), et le texte des liens sortants (le titre d'un article de Chabad.org reste dans sa langue). Sans elles, le contrôle sortait 464 signalements dont aucun n'était réel ; avec elles, **0 sur les 5 037 pages saines** — et les 32 défauts réels, tous confirmés à la main.

Le seuil a été calibré à l'envers sur les versions d'avant correction, conservées par git : le contrôle devait retrouver les sept pages fautives connues, et n'en inventer aucune sur les autres.

**L'entête** est la troisième échelle, et la plus discrète : le corps peut être irréprochable pendant que le `<title>`, l'`og:title` ou la `description` restent en français. Rien de cela ne se voit en lisant la page — c'est ce que lisent Google et les aperçus de partage. Le site en portait **212 pages** : 31 pages-pont dont la glose du sujet était restée française dans les trois langues (jusque dans le sous-titre visible du hero), 52 simanim de Yoreh De'ah dont le JSON-LD n'avait pas suivi la traduction des metas, 17 `og:title` « Siman כ״ג · Niveau 2 Lamdan », et une page hébraïque intitulée « Siman 178 · Niveau 4 — Daat HaRav (Admour HaZaken) ».

Le test ne porte que dans un sens — du français vers une page `-he`/`-en` — et sur une liste courte de jetons confrontés au site entier. Les mots communs aux trois langues en sont écartés : `Siman`, `Sougya`, `Lamdan`, `pilpoul`, `Base`, `gradation`, `structure`. `pour` n'y figure que sous ses formes composées (`pour la/le/les`), parce que le verbe anglais *to pour* apparaît dans les pages sur la netilat yadayim — un premier jet le retenait et sortait des pages saines. La description de l'éditeur (« Plateforme d'étude du Choulhan Aroukh… »), volontairement française dans les 5 397 pages, est ignorée. Validé des deux côtés comme les autres échelles : **212 pages avant correction, 0 après**.

Un premier prototype cherchait plus simplement « un `<title>` de page `-he` sans lettre hébraïque » : il sortait 300 pages, parce qu'une page française porte légitimement le nom hébreu du siman. Resserré au bon sens de lecture, il en sortait exactement une — le siman 178. La liste de jetons est ce que devient cette règle une fois généralisée.

## verifier-traductions.py

Repère les traductions **tronquées** — l'hébreu est intact, le français s'arrête en chemin.

Ni `audit-simanim.py` ni `verifier-citations.py` ne peuvent voir ce défaut : le premier ne regarde pas le contenu, le second conclut « conforme » précisément parce que l'hébreu est parfait. C'est arrivé au siman 271 séif ד, où les trois propositions portant la conclusion pratique sur la répétition de HaMotsi n'avaient aucun équivalent français.

```bash
python3 scripts/verifier-traductions.py              # tout le site
python3 scripts/verifier-traductions.py --siman 271
python3 scripts/verifier-traductions.py --quiet      # totaux seuls
```

Chaque bloc source est apparié à la traduction qui le suit, et trois choses sont signalées.

**Séif non traduit du tout.** L'hébreu est reproduit et la traduction renvoie ailleurs — « Voir l'analyse pratique : ce seif traite de… » — au lieu de rendre le texte. Cela se constate exactement, sans seuil ni statistique. Au siman 301, **2 séifim sur 51** ont une traduction ; les 49 autres portent ce renvoi.

**Traduction anormalement courte.** Le seuil n'est pas deviné : c'est le **décile inférieur de la distribution réelle du site**. On signale ce qui sort de l'usage constaté, et non ce qui s'écarte d'une idée a priori.

**Parenthèses de source non reprises** — `(ב״י)`, `(אורח חיים בשם תוס')`, où le Mehaber attribue ses sources.

### Un biais corrigé, et ce qu'il enseigne

La première version comptait les **lettres latines** de la traduction contre les lettres hébraïques de la source. Or l'usage du site est de garder en hébreu les termes techniques : « On dit ברוך שאמר avant les פסוקי דזמרה » traduit tout, mais ne marquait presque aucune lettre latine. Le ratio pénalisait donc exactement les pages les plus fidèles à cet usage.

Sur quatre blocs signalés pris au hasard, les quatre étaient des traductions **complètes et correctes**. Les lettres hébraïques de la traduction comptent désormais autant que les latines : 35 blocs ont été blanchis, 35 autres sont apparus — et c'est parmi ces derniers que se trouvaient les séifim purement non traduits.

⚠️ Un ratio normal ne veut pas dire que la traduction est fidèle — seulement qu'elle a la longueur attendue. Une traduction de la bonne longueur et du mauvais sens passe.

## verifier-syntheses.py

Cherche les **synthèses qui contredisent le corps de leur propre page**.

Au siman 271, les « règles à retenir » disaient « Mehaber avant — kiddush ; Rama après », alors que SA OH 271:12 porte l'inverse. Le corps de la page était juste ; seule la ligne de synthèse était fausse — celle que le lecteur emporte. Aucune citation n'était fautive, aucune traduction n'était courte : les trois autres gates étaient verts, et il a fallu qu'un lecteur tique.

```bash
python3 scripts/verifier-syntheses.py
python3 scripts/verifier-syntheses.py --siman 271
python3 scripts/verifier-syntheses.py --fichier CHEMIN   # p. ex. une version git antérieure
```

Le script ne comprend pas le sens. Il exploite une régularité : le Mehaber et le Rama sont souvent opposés sur un couple **ordonné** (avant/après, permis/interdit). Quand une ligne de synthèse attribue un terme à chacun, cette attribution peut être confrontée au corps de la page, où le texte du Mehaber précède la hagaha `הגה :` et où les marqueurs hébreux sont repérables.

Deux précautions, apprises de deux versions qui donnaient un résultat **inversé** :

- **Découpage par séif, jamais par page.** Un siman compte une hagaha par séif ou presque ; prendre la première de la page revient à confronter la synthèse au texte d'un séif sans rapport.
- **Deux termes contraires ne font pas une opposition.** Au séif 271:5 le Mehaber écrit `קודם שיקדשו` à propos de boire et le Rama `לאחר שבירך` à propos de HaMotsi : mots contraires, sujets différents, aucune divergence — et ce faux couple suffisait à faire taire le vrai. On exige donc un mot substantiel commun au voisinage des deux marqueurs (ici `ידיו`).

Aucun appariement par sujet n'est tenté : une ligne n'est signalée que si **un séif de sa page la contredit exactement** et qu'**aucun autre ne la soutient**. Le silence est le comportement par défaut.

### Sa portée, mesurée et non supposée

Sur 988 pages françaises et 2683 séifim, 281 lignes citent les deux autorités — dont **7** attribuent un terme à chacune, et **1** se trouve dans une page dont un séif oppose les mêmes termes sur le même acte. Le facteur limitant est structurel : **417 séifim seulement sur 2683 reproduisent une hagaha**, faute de quoi il n'y a pas de position du Rama à confronter.

C'est donc un **garde-fou de non-régression**, pas un gate de site — et le script imprime cette portée avec son résultat, pour qu'un « 0 contradiction » ne se lise jamais comme « les synthèses sont vérifiées ». Elles ne le sont pas.

Il a été validé **dans les deux sens** : silencieux sur le siman 271 corrigé, et signalant l'inversion sur la version antérieure du même fichier (`git show 95c9f2e:sources/shabbat/siman-271/niveau-1-base.html`). Les deux premières versions échouaient à ce test en donnant le résultat exactement inverse ; c'est ce qui a imposé les deux précautions ci-dessus.


## verifier-alignement.py

Confronte l'hébreu de chaque bloc d'une page au Choul'han Aroukh, pour répondre à une question qu'aucun autre gate ne pose : **ce bloc est-il bien le séif qu'on croit ?**

Une traduction peut être irréprochable et rester fausse si elle est posée sous le mauvais séif — le lecteur voit un texte hébreu et un texte français, tous deux justes, qui ne parlent pas de la même chose. `verifier-citations` juge les citations, `verifier-traductions` juge les longueurs ; ni l'un ni l'autre ne sait à quel séif un bloc correspond.

```bash
python3 scripts/verifier-alignement.py --siman 310
python3 scripts/verifier-alignement.py --section shabbat
```

### Trois formulations, dont deux fausses

Le chemin jusqu'à un contrôle utilisable mérite d'être noté, parce que chaque étape produisait un chiffre crédible et faux.

**Comparer le rang du bloc au numéro du séif** → 42 « décalages », aucun réel. Une page peut grouper trois séifim sous un seul bloc — le siman 263 le fait pour ז–ט — et le rang cesse alors de suivre la numérotation sans la moindre erreur.

**Se fier au titre que la page donne au bloc** → 320 faux signalements, pire encore : la plupart des séifim n'ont pas de titre propre, et les blocs héritaient d'un titre lointain.

**Ne rien supposer de la numérotation** — la seule qui tienne. Deux questions auxquelles on peut répondre sans hypothèse : l'hébreu du bloc existe-t-il dans ce siman, et les blocs se suivent-ils dans l'ordre de la source ? Un retour en arrière signale un bloc déplacé ou dupliqué.

Il a fallu en outre écarter ce qui n'est pas un séif mais partage son balisage : Michna Beroura (295 blocs), sugyot ouvrant par `תנו רבנן`, blocs citant leur propre massekhet. Et comparer **par mots et non par chaîne** — la page écrit `אַף עַל פִּי` en toutes lettres là où la source abrège `אע״פ`, et une comparaison littérale échouait dès la première abréviation.

Trajectoire : **436 → 158 → 42 → 320 → 12 → 8**. Chaque baisse est une correction de l'instrument, aucune n'est une amélioration du site.

### Sa portée

8 écarts subsistent dans 4 pages, et les quatre examinés sont légitimes — récapitulations reprenant le séif 1 en fin de page, citations de guemara non filtrées. C'est un **plancher de bruit**, pas une liste d'erreurs : un décalage nouvellement introduit ressortirait au-dessus.
