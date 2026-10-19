// Livraison vérifiée (api/_livraison.js) : citations désignées et collées par le
// serveur, hébreu libre et décisionnaires contrôlés paragraphe par paragraphe,
// pied de vérification. Sefaria est SIMULÉ (fetchTexte injecté) ; le câblage de
// chat.js est vérifié sur le texte du fichier.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { FiltreLivraison, extraire, normaliser } from '../../api/_livraison.js';

const MEHABER_253_1 = 'כִּירָה שֶׁהִיא עֲשׂוּיָה כְּקְדֵרָה וְשׁוֹפְתִין עַל פִּיהָ קְדֵרָה לְמַעְלָה… אָסוּר לִתֵּן עָלֶיהָ תַּבְשִׁיל מִבְּעוֹד יוֹם לְהַשְׁהוֹתוֹ עָלֶיהָ אֶלָּא אִם כֵּן נִתְבַּשֵּׁל כָּל צָרְכוֹ וְהוּא מִצְטַמֵּק וְרַע לוֹ. וְיֵשׁ אוֹמְרִים שֶׁכָּל שֶׁנִּתְבַּשֵּׁל כְּמַאֲכַל בֶּן דְּרוֹסַאי מֻתָּר לְהַשְׁהוֹתוֹ.';
const BY_253 = 'כירה שהיא עשויה כקדרה וכו\' משנה רפ"ג דמסכת שבת… וכתב הרי"ף מסתברא… וכך הם דברי הרמב"ם בפ"ג וכ"כ הר"ן… ופירש"י… וכתב הרא"ש ובשביל שרבו הדעות';
const HARAV_253_14 = 'כִּירָה שֶׁהִסִּיקוּהָ בְּקַשׁ וּגְבָבָא, וְנָטַל הַקְּדֵרָה מֵעָלֶיהָ, אִם עוֹדָהּ בְּיָדוֹ — מֻתָּר לוֹ לְהַחֲזִירוֹ.';

const SEFARIA = {
  'Shulchan_Arukh,_Orach_Chayim.253.1': { hebrew: MEHABER_253_1 },
  'Shulchan_Arukh_HaRav,_Orach_Chayim.253.14': { hebrew: HARAV_253_14 },
  'Shulchan_Arukh,_Orach_Chayim.253.99': { error: 'Référence inexistante', hebrew: '' },
};
const fetchTexte = async (ref) => SEFARIA[ref] || { error: 'inconnu', hebrew: '' };
const filtre = (opts = {}) => new FiltreLivraison({ fetchTexte, sources: [{ ref: 'Shulchan_Arukh,_Orach_Chayim.253', texte: MEHABER_253_1 }, { ref: 'Beit_Yosef,_Orach_Chayim.253', texte: BY_253 }], ...opts });
async function livrer(f, deltas) { let out = ''; for (const d of deltas) out += await f.pousser(d); return out + await f.terminer(); }

test('normaliser / extraire — nikoud et ponctuation ignorés pour trouver les bornes, texte source rendu', () => {
  assert.equal(normaliser('אָסוּר, לִתֵּן!'), 'אסור לתן');
  const ex = extraire(MEHABER_253_1, 'אסור לתן', 'ורע לו');
  assert.ok(ex.startsWith('אָסוּר לִתֵּן') && ex.endsWith('וְרַע לוֹ'), ex);
  assert.equal(extraire(MEHABER_253_1, 'מילה שאינה שם', 'ורע לו'), null);
  assert.equal(extraire(MEHABER_253_1, 'אסור לתן'), 'אָסוּר לִתֵּן');
});

test('citation désignée — séif entier collé depuis Sefaria, extrait par bornes, référence introuvable marquée', async () => {
  const f = filtre();
  const out = await livrer(f, ['> [[cite:Shulchan_Arukh,_Orach_Chayim.253.1|אסור לתן…ורע לו]]\n\nLe Mehaber ouvre par l\'opinion stricte.\n\n']);
  assert.match(out, /> אָסוּר לִתֵּן[\s\S]*וְרַע לוֹ\n\n/, 'l\'extrait source, avec son nikoud, remplace le marqueur');
  assert.doesNotMatch(out, /\[\[cite:/, 'aucun marqueur ne fuit vers le lecteur');
  assert.equal(f.stats.collees, 1);
  const g = filtre();
  const out2 = await livrer(g, ['[[cite:Shulchan_Arukh,_Orach_Chayim.253.99]] et [[cite:Shulchan_Arukh_HaRav,_Orach_Chayim.253.14]]\n\n']);
  assert.match(out2, /\[citation introuvable : Shulchan_Arukh,_Orach_Chayim\.253\.99\]/);
  assert.match(out2, /כִּירָה שֶׁהִסִּיקוּהָ בְּקַשׁ/);
  assert.equal(g.stats.introuvables, 1); assert.equal(g.stats.collees, 1);
});

test('flux — un marqueur coupé entre deux deltas et un paragraphe coupé en trois arrivent entiers, dans l\'ordre', async () => {
  const f = filtre();
  let out = '';
  out += await f.pousser('Texte : [[ci'); assert.equal(out, '', 'marqueur ouvert : on attend');
  out += await f.pousser('te:Shulchan_Arukh_HaRav,_Orach_'); assert.equal(out, '');
  out += await f.pousser('Chayim.253.14]] — voilà.\n\nSuite du');
  assert.match(out, /Texte : כִּירָה שֶׁהִסִּיקוּהָ[\s\S]*— voilà\.\n\n$/, 'le premier paragraphe part dès qu\'il est complet');
  out += await f.pousser(' raisonnement.');
  assert.doesNotMatch(out, /Suite du raisonnement/, 'le paragraphe inachevé reste en tampon');
  out += await f.terminer();
  assert.match(out, /Suite du raisonnement\.\n\n---\n_Vérification serveur/);
});

test('hébreu libre — retrouvé (nikoud, graphie ו/י) ou marqué « non retrouvé »', async () => {
  const f = filtre();
  const out = await livrer(f, [
    'Le Mehaber : אסור ליתן עליה תבשיל מבעוד יום — formulation stricte.\n\n',       // dans la source (sans nikoud, יתן→ליתן toléré)
    'Le HaRav écrit : שלא בטלה שהייה הראשונה שהשהה אותה — mais ce texte n\'est pas ouvert.\n\n',
    'Terme court : שמא יחתה בגחלים.\n\n',                                                 // 3 mots : terme, pas citation
  ]);
  assert.doesNotMatch(out.split('\n\n')[0], /non retrouvé/, 'retrouvé dans le Mehaber chargé');
  assert.match(out.split('\n\n')[1], /שהשהה אותה ⚠️ \[non retrouvé dans les sources ouvertes\]/, 'marqué juste après le passage');
  assert.doesNotMatch(out.split('\n\n')[2], /non retrouvé/, 'trois mots : pas une citation');
  assert.equal(f.stats.retrouves, 1); assert.equal(f.stats.nonRetrouves, 1);
  assert.match(out, /1 passage hébreu retrouvé dans les sources ouvertes · 1 non retrouvé/);
});

test('décisionnaires — nommés dans le Beit Yossef chargé : rien ; absents : marqués une fois ; HaRav ouvert = Admour sourcé', async () => {
  const f = filtre();
  const out = await livrer(f, ['Le Rif et le Rambam sont stricts, le Ran indulgent ; le Smak aussi, dit-on, et le Smak encore.\n\n', 'Selon l\'Admour HaZaken…\n\n']);
  assert.doesNotMatch(out, /Rambam ⚠️|Rif ⚠️|Ran ⚠️/, 'présents dans le Beit Yossef chargé');
  assert.equal((out.match(/Smak ⚠️ \[nom absent des sources ouvertes\]/g) || []).length, 1, 'marqué une seule fois');
  assert.match(out, /Admour HaZaken ⚠️/, 'le HaRav n\'a pas été ouvert');
  assert.deepEqual(f.stats.horsSources, ['Smag / Smak', 'Admour HaZaken']);
  assert.match(out, /noms hors sources : Smag \/ Smak, Admour HaZaken/);
  // le modèle ouvre le HaRav : l'Admour devient sourcé
  const g = filtre();
  g.ajouterResultats([{ name: 'sefaria_get_text', input: { ref: 'Shulchan_Arukh_HaRav,_Orach_Chayim.253.14' } }], [{ type: 'tool_result', content: JSON.stringify({ ref: 'Shulchan_Arukh_HaRav,_Orach_Chayim.253.14', hebrew: HARAV_253_14 }) }]);
  const out2 = await livrer(g, ['L\'Admour HaZaken écrit : אם עודה בידו מותר לו להחזירו.\n\n']);
  assert.doesNotMatch(out2, /⚠️/, 'ni le nom ni la citation (texte ouvert par le modèle) ne sont marqués');
  assert.equal(g.stats.retrouves, 1);
});

test('résultats d\'outils — un résultat en erreur n\'alimente pas les sources', () => {
  const f = filtre();
  const avant = f.pool.length;
  f.ajouterResultats([{ name: 'sefaria_get_text', input: { ref: 'X' } }], [{ type: 'tool_result', is_error: true, content: JSON.stringify({ error: 'nope', hebrew: 'טקסט שאינו קיים בשום מקום' }) }]);
  assert.equal(f.pool.length, avant);
});

test('pied — langue de la réponse ; aucun passage : compteurs à zéro', async () => {
  const en = await livrer(filtre({ lang: 'en' }), ['Plain English answer.\n\n']);
  assert.match(en, /Server check: 0 quotations? pasted from Sefaria · 0 Hebrew passages? found/);
  const he = await livrer(filtre({ lang: 'he' }), ['תשובה.\n\n']);
  assert.match(he, /אימות שרת/);
});

// ── Banc du 19/10 sur l'aperçu : ce que les 12 réponses réelles ont appris ────
const HARAV_253_4 = 'וְתַנּוּר שֶׁהוּא עָשׂוּי כְּעֵין קְדֵרָה גְּדוֹלָה… אָסוּר אֲפִלּוּ לִסְמֹךְ לוֹ אִם הַיָּד סוֹלֶדֶת שָׁם, אֲפִלּוּ הוּא גָּרוּף וְקָטוּם, שֶׁמָּא יַחְתֶּה בְּזוֹ הָאֵשׁ הַמְּעוּטָה.';
const MEHABER_318_4 = 'תבשיל שנתבשל כל צרכו יש בו משום בישול אם נצטנן: הגה וי"א דוקא אם מצטמק ויפה לו [רבי ירוחם] ואם לא נתבשל כל צרכו אפילו הוא רותח יש בו משום בישול: וה"מ שיש בו בישול אחר בישול בתבשיל שיש בו מרק אבל דבר שנתבשל כבר והוא יבש מותר לשרותו בחמין בשבת';

test('banc — bornes avec abréviation (וי"א), orthographe pleine (קדירה/אפילו/עדיין) et plusieurs « … » : l\'extrait est localisé', () => {
  assert.equal(extraire(MEHABER_318_4, 'וי"א דוקא אם מצטמק ויפה לו'), 'וי"א דוקא אם מצטמק ויפה לו', 'borne = texte entier avec abréviation (15 cas du banc)');
  assert.equal(extraire(MEHABER_318_4, 'ויש אומרים דוקא', 'ויפה לו'), 'וי"א דוקא אם מצטמק ויפה לו', 'abréviation développée par le modèle');
  const ex = extraire(HARAV_253_4, 'ותנור שהוא עשוי כעין קדירה גדולה', 'שמא יחתה בזו האש המעוטה');
  assert.ok(ex && ex.startsWith('וְתַנּוּר') && ex.endsWith('הַמְּעוּטָה'), 'קדירה (malé) retrouve קְדֵרָה (haser) — 14 cas du banc : ' + ex);
  assert.equal(extraire(HARAV_253_4, 'אסור אפילו לסמוך לו אם היד סולדת שם, אפילו הוא גרוף וקטום'), 'אָסוּר אֲפִלּוּ לִסְמֹךְ לוֹ אִם הַיָּד סוֹלֶדֶת שָׁם, אֲפִלּוּ הוּא גָּרוּף וְקָטוּם', 'אפילו ↔ אפלו, virgule dans la borne');
  assert.equal(extraire(MEHABER_318_4, 'והתנורים שלנו שפתחם מן הצד', 'דינם שוה'), null, 'un mauvais séif reste non trouvé (3 cas du banc)');
});

test('banc — plusieurs « … » dans la plage : on garde le premier et le dernier bout', async () => {
  const f = new FiltreLivraison({ fetchTexte: async () => ({ hebrew: MEHABER_318_4 }), sources: [] });
  const out = await livrer(f, ['[[cite:Shulchan_Arukh,_Orach_Chayim.318.4|תבשיל שנתבשל…הגה וי"א…אם נצטנן]]\n\n']);
  assert.match(out, /^תבשיל שנתבשל כל צרכו יש בו משום בישול אם נצטנן\n\n/); assert.equal(f.stats.collees, 1);
});

test('banc — réponse en hébreu : seule la prose entre guillemets ou en bloc « > » est contrôlée', async () => {
  const f = filtre({ lang: 'he' });
  const out = await livrer(f, ['להלן סיכום הדעות העיקריות בסוגיית שהייה על גבי כירה מערב שבת, לפי המחבר והרמ"א.\n\n', 'המחבר כותב: «אסור ליתן עליה תבשיל מבעוד יום להשהותו עליה אלא אם כן נתבשל» — וזה לשון הסתם.\n\n', '> מילים שאינן במקור ואינן בשום טקסט שנפתח כאן בכלל\n\n']);
  assert.doesNotMatch(out.split('\n\n')[0], /⚠️/, 'la prose du modèle n\'est pas une citation');
  assert.doesNotMatch(out.split('\n\n')[1], /⚠️/, 'la citation entre guillemets est retrouvée');
  assert.match(out.split('\n\n')[2], /⚠️ \[non retrouvé/, 'un bloc « > » inventé est marqué');
  assert.equal(f.stats.nonRetrouves, 1); assert.equal(f.stats.retrouves, 1);
});

test('banc — le message « extrait non trouvé » n\'est pas lui-même marqué ; un libellé de quatre mots n\'est pas une citation', async () => {
  const f = filtre();
  const out = await livrer(f, ['[[cite:Shulchan_Arukh,_Orach_Chayim.253.1|מילים שאינן בטקסט הזה כלל…ועוד מילים שאינן שם]] puis le libellé על גבה ולא לתוכה.\n\n']);
  assert.equal((out.match(/⚠️/g) || []).length, 0, out);
  assert.equal(f.stats.introuvables, 1); assert.equal(f.stats.nonRetrouves, 0);
});

test('banc — rien reçu du modèle : pas de pied à zéro', async () => {
  const f = filtre();
  assert.equal(await f.terminer(), '');
});

// ── Second passage du banc (19/10, 12 réponses) ─────────────────────────────
test('banc 2 — une prose en hébreu est reconnue au paragraphe, même si la question était en français', async () => {
  const f = filtre({ lang: 'fr' });   // profil français, réponse en hébreu (cas L08)
  const out = await livrer(f, ['## מה שהטקסט אומר\n\n', '**המחבר — דעה ראשונה (סתם):** כירה שהוסקה בגפת או בעצים אסור להשהות עליה תבשיל מבעוד יום אלא אם כן נתבשל כל צרכו.\n\n', 'Le Mehaber écrit en français : שלא בטלה שהייה הראשונה שהשהה אותה שם — paragraphe français.\n\n']);
  assert.doesNotMatch(out.split('\n\n')[1], /⚠️/, 'prose hébraïque : pas de contrôle hors guillemets');
  assert.match(out.split('\n\n')[2], /⚠️ \[non retrouvé/, 'paragraphe français : l\'hébreu libre est contrôlé');
});

test('banc 2 — une liste de termes hébreux séparés par des virgules ou des parenthèses n\'est pas une citation', async () => {
  const f = filtre();
  const out = await livrer(f, ['les cinq conditions (רותחת, בידו, דעתו להחזיר, מבושל כל צרכו, על גבה ולא לתוכה) selon le HaRav.\n\n', 'même pour un plat מבושל כל צרכו (אין בישול אחר בישול).\n\n', 'les cas : דבר שיש לו מתירין, חתיכה הראויה להתכבד, בעלי חיים, בריה.\n\n']);
  assert.equal((out.match(/⚠️/g) || []).length, 0, out);
  assert.equal(f.stats.nonRetrouves, 0);
});

test('banc 2 — une citation entre guillemets qui diffère d\'un mot sur huit est retrouvée (coquille « דעם » de Sefaria)', async () => {
  const BY = 'ולענין הלכה כיון שהתוספות והרא"ש והר"ן מסכימים לאסור וגם דעם הרי"ף והרמב"ם נראה כן מדלא הזכירו דבר זה הכי נקטינן';
  const f = new FiltreLivraison({ fetchTexte, sources: [{ ref: "Beit_Yosef,_Yoreh_De'ah.100", texte: BY }] });
  const out = await livrer(f, ['Le Beit Yossef conclut : « כיון שהתוספות והרא"ש והר"ן מסכימים לאסור, וגם דעת הרי"ף והרמב"ם נראה כן מדלא הזכירו דבר זה, הכי נקטינן ».\n\n', 'Mais « אם לקחו משם משחשיכה אפילו הניחו על גבי קרקע מותר » n\'est pas la lettre du texte.\n\n']);
  assert.doesNotMatch(out.split('\n\n')[0], /⚠️/, 'un mot sur seize : retrouvé'); 
  assert.match(out.split('\n\n')[1], /⚠️ \[non retrouvé/, 'une paraphrase entre guillemets reste marquée');
  assert.equal(f.stats.retrouves, 1); assert.equal(f.stats.nonRetrouves, 1);
});

test('banc 2 — bornes : mot tronqué par apostrophe (מות\' ↔ מותר) et abréviation ע"ג', () => {
  const src = 'וי"א שכל שנתבשל כמאכל בן דרוסאי או שנתבשל כל צרכו ומצטמק ויפה לו מות\' להשהותו ע"ג כירה';
  assert.equal(extraire(src, 'ויש אומרים שכל שנתבשל', 'מותר להשהותו על גבי כירה'), src);
  assert.equal(extraire(src, 'וי"א שכל', 'מות\' להשהותו ע"ג כירה'), src);
});

test('banc 2 — mauvais paragraphe du Beit Yossef : l\'extrait est cherché dans le siman entier et collé avec la référence exacte', async () => {
  const segs = ['כירה שהיא עשויה כקדרה וכו\' משנה… וכתב הרא"ש ובשביל שרבו הדעות בהאי פיסקא וישראל אדוקים במצות עונג שבת הנח להם במנהג שנהגו על פי הפוסקים כחנניה', 'ומ"ש רבינו שכמאכל ב"ד הוא שליש בישולו', 'ומ"ש אא"כ גרף או קטם'];
  const f = new FiltreLivraison({ fetchTexte: async (ref) => ({ hebrew: ref.endsWith('.7') ? segs[2] : segs.join(' ') }), fetchSegments: async () => ({ segments: segs }), sources: [] });
  const out = await livrer(f, ['Le Roch : [[cite:Beit_Yosef,_Orach_Chayim.253.7|וכתב הרא"ש ובשביל שרבו הדעות…הפוסקים כחנניה]]\n\n']);
  assert.match(out, /^Le Roch : וכתב הרא"ש ובשביל שרבו הדעות[\s\S]*כחנניה _\[réf\. exacte : Beit_Yosef,_Orach_Chayim\.253\.1\]_\n\n/);
  assert.equal(f.stats.collees, 1); assert.equal(f.stats.refCorrigees, 1); assert.match(out, /1 référence corrigée/);
});

test('banc 2 — « ה"ה » du Beit Yossef suffit à sourcer le Maguid Michné', async () => {
  const f = new FiltreLivraison({ fetchTexte, sources: [{ ref: 'Beit_Yosef,_Orach_Chayim.253', texte: 'וכן דעת הרמב"ם בפרק קמא וכתב ה"ה שכן דעת הרמב"ן' }] });
  const out = await livrer(f, ['Le Maguid Michné rapporte que le Ramban suit le Rambam.\n\n']);
  assert.doesNotMatch(out, /Maguid Michné ⚠️|Ramban ⚠️|Rambam ⚠️/);
});

// ── Relecture Codex (#284) : quatre constats, chacun reproduit ──────────────
test('Codex 1 — textePrimaire est déclaré HORS du bloc if : le filtre peut le lire sur tous les chemins', () => {
  const chat = readFileSync(new URL('../../api/chat.js', import.meta.url), 'utf8');
  assert.match(chat, /let textePrimaire = null;\s*\n\s*if \(!urgence\.urgent && !model\._meta\) \{\s*\n\s*textePrimaire = await chargerTextePrimaire\(/, 'déclaration avant le if, affectation dedans');
  assert.doesNotMatch(chat, /const textePrimaire = await chargerTextePrimaire/, 'plus de const dans le bloc');
  const iDecl = chat.indexOf('let textePrimaire = null;'), iUse = chat.indexOf('new FiltreLivraison({ sources: textePrimaire.sources');
  assert.ok(iDecl > 0 && iDecl < iUse);
});

test('Codex 2 — la ponctuation ordinaire ne coupe pas un passage hébreu en deux', async () => {
  const f = filtre();
  const out = await livrer(f, ['Il écrit : אחד שנים שלש, ארבע חמש שש שבע — sept mots que personne n\'a ouverts.\n\n']);
  assert.match(out, /⚠️ \[non retrouvé dans les sources ouvertes\]/, 'six mots coupés par une virgule restent UN passage à vérifier');
  assert.equal(f.stats.nonRetrouves, 1);
  const g = filtre();
  const out2 = await livrer(g, ['Mehaber : אסור ליתן עליה תבשיל מבעוד יום, להשהותו עליה — ponctuation ajoutée par le modèle.\n\n']);
  assert.doesNotMatch(out2, /⚠️/, 'retrouvé malgré la virgule insérée'); assert.equal(g.stats.retrouves, 1);
});

test('Codex 3 — des bornes d\'extrait introuvables donnent une citation invalide, pas un séif entier', async () => {
  const f = filtre();
  const out = await livrer(f, ['[[cite:Shulchan_Arukh,_Orach_Chayim.253.1|מילים שאינן…בטקסט]]\n\n']);
  assert.match(out, /\[extrait non trouvé dans Shulchan_Arukh,_Orach_Chayim\.253\.1 : « מילים שאינן…בטקסט »\]/);
  assert.doesNotMatch(out, /כִּירָה שֶׁהִיא/, 'le séif entier n\'est pas collé à la place');
  assert.equal(f.stats.collees, 0); assert.equal(f.stats.introuvables, 1);
});

test('Codex 4 — un marqueur inachevé à la fermeture ne fuit pas vers le lecteur', async () => {
  const f = filtre();
  let out = await f.pousser('Le texte dit [[cite:Shulchan_Arukh,_Orach_Chayim.253.1|אסור');
  assert.equal(out, '');
  out += await f.terminer();
  assert.doesNotMatch(out, /\[\[cite:/);
  assert.match(out, /\[citation interrompue : Shulchan_Arukh,_Orach_Chayim\.253\.1\]/);
  assert.equal(f.stats.introuvables, 1); assert.match(out, /1 référence introuvable/);
});

test('câblage — chat.js : filtre créé sur le chemin lamdan, deltas filtrés, outils ajoutés, fin et abort vidés une fois, plafond lamdan', () => {
  const chat = readFileSync(new URL('../../api/chat.js', import.meta.url), 'utf8');
  assert.match(chat, /import \{ FiltreLivraison \} from '\.\/_livraison\.js'/);
  const iNew = chat.indexOf('new FiltreLivraison({ sources: textePrimaire.sources');
  const iLoop = chat.indexOf('while (iterations < maxIterations)');
  const iPousser = chat.indexOf('await livraison.pousser(event.delta.text)');
  const iAjout = chat.indexOf('livraison.ajouterResultats(toolUses, toolResults)');
  const iFin = chat.indexOf("if (livraison && !livraison.clos) {\n      livraison.clos = true;\n      const fin = await livraison.terminer()");
  const iMax = chat.indexOf("if (stopReason === 'max_tokens') {");
  assert.ok(iNew > 0 && iNew < iLoop, 'créé avant la boucle');
  assert.ok(iPousser > iLoop && iAjout > iPousser, 'deltas puis outils dans la boucle');
  assert.ok(iFin > iAjout && iFin < iMax, 'vidé et pied AVANT l\'avis de troncature');
  assert.equal((chat.match(/livraison\.clos = true/g) || []).length, 2, 'fin normale + abort, une seule fois chacun');
  assert.match(chat, /max_tokens: forceSynthesis \? FORCED_SYNTHESIS_MAX_TOKENS : \(livraison \? MAX_TOKENS_LAMDAN : MAX_TOKENS_OUTPUT\)/);
  assert.match(chat, /const MAX_TOKENS_LAMDAN = parseInt\(process\.env\.MAX_TOKENS_LAMDAN \|\| String\(MAX_TOKENS_OUTPUT\), 10\)/, 'pas de plafond réduit par défaut (banc du 19/10 : réponses vides)');
});

test('texte primaire — le bloc porte les règles de rédaction et chargerTextePrimaire rend les sources brutes', async () => {
  const tp = readFileSync(new URL('../../api/_texte-primaire.js', import.meta.url), 'utf8');
  assert.match(tp, /RÈGLES DE RÉDACTION — appliquées par le serveur/);
  assert.match(tp, /\[\[cite:\$\{ref\}\.1\]\]/);
  assert.match(tp, /const sources = \[\{ ref, texte: hebrew \}\];/);
  assert.match(tp, /return \{ siman, partie, ref, texte, complements, sources \};/);
});
