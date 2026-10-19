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
  const out = await livrer(f, ['Il écrit : אחד שנים שלש, ארבע חמש שש — six mots que personne n\'a ouverts.\n\n']);
  assert.match(out, /⚠️ \[non retrouvé dans les sources ouvertes\]/, 'six mots coupés par une virgule restent UN passage à vérifier');
  assert.equal(f.stats.nonRetrouves, 1);
  const g = filtre();
  const out2 = await livrer(g, ['Mehaber : אסור ליתן עליה תבשיל, מבעוד יום — ponctuation ajoutée par le modèle.\n\n']);
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
  assert.match(chat, /const MAX_TOKENS_LAMDAN = parseInt\(process\.env\.MAX_TOKENS_LAMDAN \|\| '3000', 10\)/);
});

test('texte primaire — le bloc porte les règles de rédaction et chargerTextePrimaire rend les sources brutes', async () => {
  const tp = readFileSync(new URL('../../api/_texte-primaire.js', import.meta.url), 'utf8');
  assert.match(tp, /RÈGLES DE RÉDACTION — appliquées par le serveur/);
  assert.match(tp, /\[\[cite:\$\{ref\}\.1\]\]/);
  assert.match(tp, /const sources = \[\{ ref, texte: hebrew \}\];/);
  assert.match(tp, /return \{ siman, partie, ref, texte, complements, sources \};/);
});
