# Passages à soumettre à la validation rabbinique — chantier chat du 28 septembre 2026

Ce relevé liste ce que le chantier a **modifié ou constaté dans le contenu halakhique**
et qui appelle la relecture du Rav avant publication. Les modifications de code
(prompt, outils, widget) ne sont pas des affirmations halakhiques et ne figurent pas ici.

## 1. Modifié — à valider

### Siman 319, niveau 4 (Daat HaRav), FR / HE / EN — « les trois conditions du borer »

- Fichiers : `sources/shabbat/siman-319/niveau-4-daat-harav.html` (l. ~727-745 et ~776),
  `-he.html` (l. ~641-655 et ~685), `-en.html` (l. ~670-685 et ~715).
- Avant : « test pour chaque action : déchet du bon ? outil ? différé ? **Si les 3 oui = interdit** »
  et « 3 critères du borer interdit : déchet du bon + outil + différé ».
- Défaut : présentée comme test de décision, la formule laissait croire que les trois marques
  doivent être réunies pour interdire. Or le texte pose trois conditions **cumulatives de
  permission** : une seule manque et le tri est interdit.
- Source confrontée (Sefaria, `Shulchan_Arukh_HaRav,_Orach_Chayim.319.1-10`, édition Kehot) :
  - séif א : כָּל הַבּוֹרֵר פְּסֹלֶת מִתּוֹךְ הָאֹכֶל, אֲפִלּוּ בְּיָדוֹ אַחַת, וַאֲפִלּוּ כְּדֵי לֶאֱכוֹל לְאַלְתַּר — חַיָּב ;
  - séif ב : הַבּוֹרֵר אֹכֶל מִתּוֹךְ הַפְּסֹלֶת שֶׁלֹּא לֶאֱכוֹל לְאַלְתַּר … נַעֲשֶׂה כְּבוֹרֵר לְאוֹצָר, וְחַיָּב ;
  - séif ג : וְאֵינוֹ קָרוּי לְאַלְתַּר אֶלָּא סָמוּךְ לַסְּעֻדָּה מַמָּשׁ ;
  - séifim ד-ה : אֵין אִסּוּר מִשּׁוּם בּוֹרֵר אֶלָּא בְּבוֹרֵר פְּסֹלֶת מֵאֹכֶל אוֹ לְהֵפֶךְ … בַּמֶּה דְּבָרִים אֲמוּרִים … כְּשֶׁהַכֹּל מִין אֶחָד ;
  - séif י : לֹא יְנַפֶּה בְּקָנוֹן אוֹ תַּמְחוּי, גְּזֵרָה שֶׁמָּא יְנַפֶּה בְּנָפָה וּכְבָרָה שֶׁהוּא חַיָּב.
- Après : « Le tri n'est permis que si les trois conditions sont réunies : l'aliment hors du
  déchet (séif א) ; à la main, sans tamis ni crible (séif י) ; pour consommer aussitôt (séifim
  ב-ג). Les trois oui = permis. Un seul non = interdit. » La formule inverse est présentée comme
  « pas fausse en soi, mais incomplète ».
- **Points à trancher par le Rav** :
  1. le rattachement de la condition « à la main » au séif י (קנון ותמחוי / נפה וכברה) est-il le
     bon renvoi dans l'édition suivie par le site ?
  2. la mention « passible » (חייב) pour le déchet hors de l'aliment et pour le tri différé est
     celle du texte ; la page ne distingue pas ici חייב de אסור מדרבנן (קנון ותמחוי) — est-ce
     assez clair pour le lecteur du niveau 4 ?
  3. le titre du hidoush (« שלושת תנאי הבורר המותר ») remplace « 3 critères structurés » : le
     Rav souhaite-t-il conserver l'idée de « hidoush » de l'Admour HaZaken sur ce point, alors
     que les trois conditions sont celles du Mehaber (319:1) ?
- Provenance des corrections : commentaires HTML datés en tête de chaque bloc modifié.

### Siman 319, index (FR / EN / index.md) — description et sous-titre

- Avant (FR) : « Cadre : 3 critères pour interdire (mélange + intention + outil) » ; (EN) :
  « the 3 conditions for an issur (taaroves, pesoles from ochel, and a keli) ».
- Après : « les trois conditions cumulatives du tri permis (l'aliment hors du déchet, à la
  main, pour consommer aussitôt — une seule manque et le tri est interdit) ».
- À valider : même question que ci-dessus. Le triplet FR d'origine (« mélange + intention +
  outil ») ne correspondait pas au triplet du niveau 4 (« déchet + outil + différé ») : deux
  formulations différentes pour le même cadre sur le même siman.

## 2. Constaté, NON modifié — à examiner

- `sources/shabbat/siman-247/niveau-4-daat-harav.html` l. 677 (et `-en` l. 585) : « Si les 3
  oui = OK. Si un seul non = à vérifier ou différer. » — même forme de test à trois critères,
  mais dans le sens de la **permission**, ce qui est logiquement correct ; la page dit elle-même
  que la transposition aux services modernes « est le fait de cette page et non du Rav ». Laissé
  tel quel ; le Rav peut souhaiter en revoir la portée.
- Niveau 3 du siman 319 (FR/EN, l. 332 et 452) : « Une seule manque → interdit » — formulation
  correcte, cohérente avec la correction du niveau 4.
- Niveau 1 du siman 319 : « 3 conditions cumulatives du tri PERMIS » — correct.

## 4. Réponses du banc conversationnel réel — points à relire

Relevé complet : `audit/conversationnel-2026-09-28.md` (douze cas, modèle réel, déploiement de
prévisualisation). Deux points méritent l'œil du Rav :

- **Cas D (poulet et bœuf mélangés)** : la réponse est juste sur le fond (prendre l'espèce qu'on
  mange, à la main, tout de suite ; l'autre a le statut de déchet, 319:5 HaRav) mais elle écrit,
  sous « Application à ton cas », « ✅ Autorisé : prendre à la main les morceaux de poulet… ».
  C'est la permission du texte, suivie de la réserve unique ; le Rav souhaite-t-il que le chat
  s'interdise cette forme (coche verte sur le cas personnel), même quand le texte est clair ?
- **Cas D, citations des séifim ה et ו du HaRav** : confrontées le 29/09 au texte Kehot servi par
  Sefaria (consonnes comparées). Séif ה : « אם היו לפניו שני מיני אוכלים מעורבים … דהיינו אוכל
  מתוך הפסולת, ולא להפך » — **verbatim**. Séif ו : « אין להקל, כי ספק חיוב חטאת הוא » — **verbatim**
  (le séif ו le dit à propos de morceaux gros et distincts de deux espèces : « ואפשר שלא שייך
  כאן ברירה כלל — אף על פי כן אין להקל »). Point clos ; rien à trancher.
- **Cas I (attente viande / fromage, trois traditions)** et **cas K (Tanya ch. 1)** : réponses
  longues avec sources ; exactitude à relire, aucun contrôle mécanique ne la juge.

## 3. Formulations du chat qui touchent à la halakha — à valider

- La consigne d'urgence statique (`api/_reserve.js`, `URGENCE`, FR/HE/EN) cite Orah Haïm 328:2
  (« celui qui agit vite est loué, celui qui s'attarde à demander est blâmé ») — vérifié sur
  Chabad.org (Shulchan Aruch HaRav 328:2 : « One who does so eagerly is praiseworthy, while one
  who asks [whether it is permitted] is considered as if he sheds blood »). Le Rav souhaite-t-il
  cette formulation, ou une formulation sans référence ?
- La phrase de réserve unique (`RESERVE`, FR/HE/EN/ES) remplace six formulations antérieures.
  Elle est reprise de la V2 (audit du 27 septembre). À valider dans les quatre langues.
