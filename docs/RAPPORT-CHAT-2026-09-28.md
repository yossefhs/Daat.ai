# Chat Daat — compte rendu du chantier du 28 septembre 2026

Branche : `claude/aat-torah-prompt-improvement-d8w9ks`. Rien n'est déployé : le résultat est
préparé pour relecture. Pour chaque point : problème, cause établie, correction, preuve, limites.

## 1. État réel du projet (ce qui a été lu, pas supposé)

Le point d'entrée est `api/chat.js` (1 950 lignes). Il n'y a pas une voie de réponse mais
**huit**, et les défauts observés ne venaient pas toutes du même endroit :

| Voie | Modèle | Prompt | Réserve ajoutée par |
|---|---|---|---|
| Cache méta (KV) | aucun | — | — |
| Méta DeepSeek | deepseek-chat | prompt propre (`_deepseek.js`) | — |
| Corpus-first : cache KV | aucun | — | texte mis en cache |
| Corpus-first : Haiku | Haiku | `corpusSystem` (chat.js) | prompt corpus (« c'est à ton Rav de trancher ») |
| Corpus brut (0 modèle) | aucun | — | `RAW_CORPUS_I18N.foot` |
| Agentique | Haiku / Sonnet / Opus | `buildSystemPrompt()` | prompt (3 formulations) + message de synthèse forcée |
| Secours à quota épuisé | Haiku ou brut | idem corpus-first | idem |
| `api/chat-corpus.js` (endpoint séparé) | Haiku | prompt propre | prompt propre |

Plus deux sources de réserve hors chat : le champ `disclaimer` de `_mareh_mekomot.js` (recopié
par le modèle) et `api/admin/generate-siman.js`. **Six formulations** de la même réserve.

Le commit `3b35fdf39` n'est pas la version courante : `main` a 15 commits de plus. La branche
`origin/feat/prompt-v2` (session du 27 septembre, non fusionnée) a servi de base au prompt.

## 2. Les trois constats

### A. Confusion entre ouvrages (317:4)

- **Problème** : interrogé sur « Choul'han Aroukh HaRav 317:4 », le modèle a appelé
  `Shulchan_Arukh,_Orach_Chayim.317.4` (Karo) et attribué le passage à l'Admour HaZaken.
- **Cause établie** : `sefaria_get_text` rendait `{ ref, title, hebrew, english }`. Rien n'y
  nommait l'auteur ; `title` (« Shulchan Arukh, Orach Chayim 317 ») se lit comme le titre
  demandé. La réussite de l'appel valait vérification. Vérifié sur Sefaria : les deux ouvrages
  existent à 317:4 — Karo : קושרין דלי במשיחה… (seaux) ; HaRav : קֶשֶׁר שֶׁאֵינוֹ נִקְרָא שֶׁל קַיָּמָא…
  (nœud pour une mitsva). Aucun ne traite du salaire de Shabbat : l'exemple « OH 317:4 » de
  l'ancien prompt (l. 462) était lui-même faux (le 317 traite des nœuds, confirmé sur
  Chabad.org, chapitre 317 « Tying Knots »).
- **Correction** : `api/_sefaria.js` — table d'identité des ouvrages ; chaque résultat porte
  `work`, `work_he`, `author`, `nature`, `url` (formée depuis la ref servie), `versions` (la
  traduction anglaise est identifiée comme traduction), et une `attribution_note` explicite
  pour la paire Karo / HaRav (et Kitsour). En erreur, le résultat nomme l'ouvrage DEMANDÉ et
  interdit la substitution silencieuse. Description de l'outil : identifiants distincts. Prompt :
  section « Identité des ouvrages », rang 2 de la hiérarchie, règle de relance (reconnaître,
  retirer, corriger).
- **Preuve** : `tests/chat/sefaria-identite.test.mjs` (7 tests, fetch simulé avec les réponses
  Sefaria réelles du jour) ; smoke test réel de `describeWork` sur 317:4 dans les deux ouvrages.
- **Limites** : la table couvre les ouvrages confusables et les plus cités ; un ouvrage inconnu
  reçoit une note « identifie l'auteur avant d'attribuer ». Le comportement du modèle face à la
  note n'a pas été testé en conversation réelle (pas de clé API dans cet environnement).

### B. Conclusion contradictoire dans une urgence

- **Problème** : « appelle immédiatement les secours » puis « c'est à ton Rav de trancher ».
- **Cause établie** : trois mécanismes indépendants, aucun dans le seul modèle :
  1. le chemin corpus-first (Haiku) impose la réserve « dès que la question porte sur un cas
     concret » — une urgence est un cas concret ;
  2. le message de synthèse forcée dit « renvoie la conclusion pratique au Rav » sans condition ;
  3. le prompt imposait une « formulation imposée » de renvoi au Rav.
- **Correction** : `api/_urgence.js` (détecteur FR/HE/EN, avec indice « étude ») ; dans
  `chat.js`, détection AVANT tout routage ; corpus-first, pré-RAG et sauvetage à quota
  court-circuités ; consigne de priorité injectée devant la question (bloc caché intact) ;
  variante de synthèse forcée sans renvoi au Rav ; consigne statique (0 modèle, sans numéro
  d'urgence, sans réserve) servie à quota épuisé et à budget IA épuisé ; `chat-corpus.js` et le
  prompt corpus-first répondent HORS-SUJET sur un danger vital ; prompt : section
  `<urgence_vitale>` placée avant le profil, réserve interdite après une consigne d'urgence.
  Source de contrôle : Chabad.org 328:2 (« one who asks … as if he sheds blood »).
- **Preuve** : `tests/chat/reserve-urgence.test.mjs` et `chat-wiring.test.mjs` (la question
  observée est détectée ; la consigne statique ne contient ni réserve ni numéro ; les trois
  points de court-circuit sont câblés).
- **Limites** : le détecteur est lexical ; un faux négatif laisse le prompt seul en ligne ; un
  faux positif coûte une réponse par le chemin complet, sans réserve automatique. Non testé en
  conversation réelle.

### C. Synthèse ambiguë dans le corpus (319, daat-harav)

- **Problème** : « déchet du bon ? outil ? différé ? Si les 3 oui = interdit » et « 3 critères
  du borer interdit », présentés comme test de décision.
- **Cause établie** : confrontation au texte (Sefaria, SA HaRav 319:1-10, Kehot) — séif א :
  le déchet hors de l'aliment est passible **même à la main et même pour aussitôt** ; séif ב :
  trier pour plus tard est passible ; séif י : נפה וכברה passible, קנון ותמחוי interdit. Les trois
  conditions sont cumulatives pour la **permission** ; la formule inverse n'est pas fausse mais
  omet les cas où une seule marque suffit à interdire. Le contre-exemple demandé (retirer le
  déchet à la main pour consommation immédiate) est exactement le séif א.
- **Correction** : les deux blocs réécrits en FR / HE / EN, avec commentaire HTML de provenance
  et renvoi à la validation ; description et sous-titre des index FR / EN / `index.md` alignés
  (le triplet FR d'origine « mélange + intention + outil » ne correspondait même pas au triplet
  du niveau 4). Côté chat : chaque résultat du corpus porte sa `nature` ; le prompt dit qu'une
  synthèse du site ne prouve pas l'original et qu'une formule pédagogique n'est pas la règle.
- **Formulations analogues** : une seule trouvée hors 319 (`siman-247` niveau 4, « Si les 3 oui
  = OK »), dans le sens de la permission, non modifiée — listée pour examen. Les niveaux 1 et 3
  du 319 étaient corrects (« une seule manque → interdit »).
- **Preuve** : `verifier-balises.py`, `verifier-langues.py`, `verifier-citations.py` verts sur
  le siman 319 ; `verifier-integrite.py` : 0 ; corpus reconstruit (`npm run build`, 43 362
  chunks, 513 simanim).
- **Limites** : la reformulation est halakhiquement engageante — elle est **soumise à
  validation** (`audit/validation-rabbinique-chat-2026-09-28.md`). Les caches de réponses
  corpus (KV, 30 jours) sont invalidés d'eux-mêmes : la clé porte l'id de chunk et le contrat de
  génération, tous deux changés.

## 3. Prompt principal V3

`api/_system-prompt.js`, 34 251 caractères (V1 : 60 404). Hiérarchie unique en cinq rangs ;
états documentaires (texte primaire consulté et pertinent / synthèse consultée, original non
vérifié / attribution non vérifiée / sources contradictoires / informations du cas
insuffisantes) à la place des pourcentages ; identification des ouvrages ; urgence ; périmètre
injecté ; une seule réserve (`api/_reserve.js`) ; liens uniquement depuis le champ `url` des
outils ; glose de l'hébreu dans le contrôle final ; date du jour dans un second bloc système non
caché (`api/_date.js`). Le prompt Orah Haïm reste un préfixe exact du prompt Yoreh De'ah.

## 4. Périmètre

`corpusPerimeter()` calcule le périmètre depuis le corpus chargé : « Orah Haïm 1-365 (365) ·
Yoreh De'ah 87-234 (148) — 513 simanim », égal au catalogue `data/simanim-disponibles.json`
(513). Les plages recopiées ont été retirées des descriptions d'outils, du prompt et des
commentaires de `chat.js` ; les bornes 242-365 et 183-200 qui subsistent dans le code sont
celles du **livre** (Hilkhot Shabbat, Niddah), pas du périmètre, et sont commentées comme
telles. Le prompt distingue « absent du périmètre / existant mais non retrouvé / récupéré mais
insuffisant ».

## 5. Accueil et rendu

- La question saisie pendant le choix du profil n'est plus écrasée par le message
  d'introduction.
- « Commencer » ne déclenche plus d'appel au modèle : l'accueil est statique et local. Mesuré
  dans le code : l'ancien « Bonjour Daat ! Voici mon profil… » dépassait le seuil méta (80
  caractères) et partait donc en Sonnet/Opus — **un Aperçu Opus sur trois consommé pour un
  accueil**.
- Le profil n'est plus obligatoire pour envoyer (une définition n'exige pas un minhag) ; ce qui
  manque est transmis « non précisé ».
- Compteurs : `rate_info` annonçait « count + 1 » avant de savoir que le corpus servirait sans
  consommer ; `done` renvoie désormais la jauge mensuelle réelle et le widget la reprend.
- Rendu : tableaux, citations « > » en RTL, liens, hébreu inline testés
  (`widget-render.test.mjs`).
- Lien vers le séif cité : `extract-corpus.js` propage `#seif-N` dans `sourceUrl` quand la page
  porte l'ancre (pilote 358 : 14 ancres dans le corpus reconstruit). Ailleurs, l'URL reste celle
  de la page — les ancres sont à généraliser côté contenu.

## 6. Tests et validation

| Type | Exécuté | Résultat |
|---|---|---|
| Automatisés, outils simulés (`npm test`) | oui | **53 / 53** |
| Portes de contenu sur 319 (balises, langues, citations, intégrité) | oui | vertes |
| Build complet (`npm run build`) | oui | 43 362 chunks, 513 simanim, avertissements préexistants inchangés |
| Intégration avec les outils réels (Sefaria) | partiel | `describeWork` et `dateContextBlock` exécutés ; Sefaria interrogé à la main pour 317:4 (×2), 319:1-12 |
| Essais conversationnels avec un modèle réel | **non** | pas de clé API dans cet environnement |

Correspondance des cas demandés : A (identité 317:4), B (relance), C (urgence), D (319:4-5,
règle de lecture), E (synthèse vs original), F (source indisponible), G (réserve éditoriale),
H (sans profil), I (traditions), J (Rebbe non retrouvé), K (Tanya), L (liens, tableaux, RTL) —
chacun a au moins un test de spécification ou de câblage ; **aucun n'a été joué contre le
modèle**. Un test simulé réussi ne démontre pas la fiabilité du système complet.

## 7. Ce qui reste

- Les trois pages de chat plein écran (`chat.html`, `chat-he.html`, `chat-en.html`) ont leur
  propre accueil : « Commencer » y envoie encore le message d'introduction au modèle, et l'envoi
  y exige encore le profil. Même correctif à porter (trois fichiers).
- `api/_query-rewrite.js` réduit la question à des mots-clés : une négation peut disparaître
  (limite architecturale ; le prompt demande de relire la question avant de conclure).
- Les Igrot Kodesh, Likoutei Si'hot, Sefer HaMinhagim et responsa du Tsema'h Tsedek ne sont
  dans aucun outil : le prompt le dit et interdit de prétendre les avoir consultés.
- Les ancres de séif n'existent que sur le pilote 358.
- Le détecteur d'urgence est lexical ; à élargir à partir des journaux (`[chat.js] URGENCE`).
- Une passe conversationnelle réelle sur les douze cas, avec clé API, avant tout déploiement.
