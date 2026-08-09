# Passation — application des corrections du classeur d'audit

Ce document existe pour qu'une session neuve reprenne ce travail sans refaire
les erreurs déjà commises. Il est écrit à l'intention de quelqu'un qui n'a pas
assisté à ce qui précède.

## Le point de départ

`audit/audit-references-DAAT.xlsx` — relecture rendue par le Rav, 480 lignes
regroupées en **197 signalements distincts** (les autres sont les duplications
entre versions FR/HE/EN d'une même page).

| Feuille | Contenu |
|---|---|
| `Synthèse` | vue d'ensemble |
| `Priorités P0-P1` | les 50 anomalies prioritaires |
| `Audit distinct` | les 197 signalements, une ligne chacun |
| `Toutes les lignes` | les 480 lignes d'origine, annotées |

Colonnes utiles de `Audit distinct` : `Citation`, `Références initiales`,
**`Décision finale`**, **`Référence corrigée`**, `Gravité`, `Type`,
`Explication`, `Source URL`, `Versions concernées`.

Répartition annoncée par le Rav :

- 107 confirmés — **aucune correction**
- 8 paraphrases valables — ne pas les présenter comme citations littérales
- 14 références à préciser
- **66 références ou textes à corriger**
- 1 citation à supprimer
- 1 erreur halakhique à corriger

## Déjà fait — ne pas refaire

Corrections appliquées dans **les trois langues**, gates verts (174/174) :

| Siman | Correction |
|---|---|
| 331 | opinion des Sages inversée : `אין מכשירי מילה דוחין את השבת` ; perek ramené à ק״ל ע״א |
| 293 | tossefet Chabbat formulée à l'envers, remplacée par l'énoncé correct |
| 293 | citation `אלמלא דחים נקטינן` non retrouvée — retirée, substance en `résumé` |
| 261 | statut de *bein hachmachot* inversé ; phrase incohérente retirée ; daf → 34b |
| 261 | citation non établie de Yoma 81b retirée (niveaux 1 et 2) |
| 242 | `הבורא` → `הקדוש ברוך הוא` (Beitsa 15b) |
| 254 | `אין צולין בשר, בצל וביצה` (Michna Chabbat 1:10) |
| 263 | `גרבי יין` au lieu de `חביות` (Chabbat 23b) |
| — | `חלל עליו שבת אחת` → Yoma **85b** ; `משום הנכנסין ומשום היוצאין` → Meguila **21b** |

Deux points **volontairement non appliqués**, vérification faite :

- `כל המשנה ממטבע שטבעו חכמים` porte déjà `ברכות מ׳:` = Berakhot 40b. Correct.
- `מקום שאמרו להאריך` : aucun daf fautif attaché à proximité dans les pages.
  Ne pas corriger à l'aveugle — localiser d'abord.

## Ce qui reste

Les ~66 corrections de références/textes du classeur, plus le lot **siman 268**
détaillé par le Rav dans la conversation (IDs 586-595) : les séifim corrects
sont 268:7, 268:8, 268:12, 268:15, 268:16, 268:17, 268:18 pour le **Choul'han
Aroukh HaRav**, et 268:6 et 268:8 pour le **Choul'han Aroukh ordinaire**.

Le cas **588 est le plus délicat et n'est pas un simple numéro** : la page
mélange le Choul'han Aroukh ordinaire et celui de l'Admour Hazaken sans
l'indiquer. Dans un cadre 'Habad cette distinction compte. Forme demandée :

> **Choul'han Aroukh, Ora'h 'Haïm 268:6** : `הטועה בתפילת שבת...`
> **Voir cependant Choul'han Aroukh HaRav 268:10-11**, qui précise la halakha
> concernant Moussaf.

Restent aussi : **563** (deux michnayot à séparer — Chabbat 47b et 49a),
**570** (Chabbat 34b), **578** (Kountress A'haron 263, séif 11, note 2),
**583** (Michna Beroura 266:2).

## Méthode — ce qui a été appris à ses dépens

**1. Vérifier que la page revendique vraiment la référence avant de la
corriger.** Sur six « références erronées » d'un premier lot, les six étaient
des inventions de l'outil : la page n'avait jamais écrit ce qu'on lui
reprochait. Corriger aurait introduit une erreur là où il n'y en avait pas.

**2. Trois langues, toujours.** Toute correction s'applique à `X.html`,
`X-he.html`, `X-en.html`. Vérifier après coup qu'aucune n'a été oubliée.

**3. Les deux gates après chaque lot :**

```bash
npm run build                              # corpus et index dérivés
python3 scripts/audit-simanim.py --quiet   # doit rester 174/174
cd audit-system && .venv/bin/python -m pytest tests/ -q
```

**4. Ne jamais inventer une source.** Quand la source exacte n'est pas établie,
retirer la citation et marquer `résumé`, en disant que la source primaire reste
à établir. C'est ce qui a été fait pour Yoma 81b et pour `אלמלא דחים נקטינן`.

**5. La convention typographique du dépôt fait tout le travail.** Les
guillemets sont réservés au **littéral** ; une condensation s'annonce par
`<em>résumé</em> :` (`תמצית` / `summary`) et n'est pas jugée. Une paraphrase
correcte n'a pas à être supprimée — il suffit qu'elle cesse de se présenter
comme une citation. C'est la réponse aux 8 « paraphrases valables ».

## Outillage disponible

```bash
cd audit-system
.venv/bin/python -m pytest tests/ -q                    # 233 tests
AUDIT_DATABASE_URL="sqlite:///$PWD/var/audit-4niveaux.db" \
  .venv/bin/python scripts/export-triage.py --out /tmp/triage.html
cat decisions.txt | .venv/bin/python scripts/import-triage.py
```

Base d'audit : `audit-system/var/audit-4niveaux.db` (git-ignorée) — 112 pages,
4 niveaux, simanim 242-269. Les décisions déjà rendues par le Rav y sont
tracées et **ne doivent pas être écrasées** : `run_analyse` ne supprime que les
signalements encore à l'état `NEW`.

Réponses du tri : `contenu`, `reference`, `variante`, `pas_citation`,
`aucune_erreur`, `rav`.

## Un garde-fou qui ne se contourne pas

Un signalement à risque **halakhique** ne peut pas être approuvé par un
éditeur : la transition d'état elle-même le refuse et impose l'escalade au Rav.
Cela vaut aussi dans le tri rapide. Ne pas contourner ce mécanisme pour aller
plus vite — c'est la garantie centrale du système.
