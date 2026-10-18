// Texte primaire obligatoire (lamdan + siman nommé) — fetch SIMULÉ, sauf le
// dernier test qui rejoue le cas réel du 18/10 contre Sefaria quand le réseau est là.
import { test, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { demandeLamdan, refMehaber, blocTextePrimaire, chargerTextePrimaire } from '../../api/_texte-primaire.js';

const PROFIL_LAMDAN = "[Profil de cette session]\n• Niveau : Lamdan / Talmid Hakham — pilpoul approfondi\n• Minhag : Habad / Loubavitch\n• Langue de réponse souhaitée : français\n• Contexte : je consulte actuellement le Siman 253 (Orah Haïm — Hilkhot Shabbat, page Niveau 1 — Base) sur daattorah.com — sauf indication contraire, mes questions portent sur ce siman.\n\n[Ma question]\nFait moi un résumé clair avec l idée des opinions";
const PROFIL_DEBUTANT = "[Profil de cette session]\n• Niveau : Débutant — peu ou pas de bagage\n• Minhag : Séfarade\n\nExplique le siman 253";

// Réponse Sefaria v3 simulée pour le Mehaber 253 : l'opinion STRICTE d'abord.
const MEHABER_253 = {
  title: 'Shulchan Arukh, Orach Chayim 253', indexTitle: 'Shulchan Arukh, Orach Chayim',
  ref: 'Shulchan Arukh, Orach Chayim 253', heRef: 'שולחן ערוך, אורח חיים רנ״ג',
  versions: [{ language: 'he', versionTitle: 'Wikisource', text: ['כירה שהיא עשויה כקדירה… אסור ליתן עליה תבשיל מבע"י להשהותו עליה אלא א"כ נתבשל כל צרכו והוא מצטמק ורע לו', 'שני סעיף'] }],
};

let realFetch;
beforeEach(() => { realFetch = globalThis.fetch; });
afterEach(() => { globalThis.fetch = realFetch; });
function mockFetch(map) {
  globalThis.fetch = async (url) => {
    const u = decodeURIComponent(String(url));
    for (const [key, val] of Object.entries(map)) {
      if (u.includes(key)) {
        if (val === 404) return { ok: false, status: 404, json: async () => ({ error: `We have no text for ${key}.` }) };
        return { ok: true, status: 200, json: async () => val };
      }
    }
    return { ok: false, status: 500, json: async () => ({}) };
  };
}

test('lamdan — le libellé réel du widget est reconnu, les autres niveaux non', () => {
  assert.equal(demandeLamdan(PROFIL_LAMDAN), true);
  assert.equal(demandeLamdan('Niveau : Talmid Hakham'), true);
  assert.equal(demandeLamdan(PROFIL_DEBUTANT), false);
  assert.equal(demandeLamdan('• Niveau : Élève de Yeshiva — étude régulière'), false);
  assert.equal(demandeLamdan('• Niveau : Intermédiaire — bagage moyen'), false);
  assert.equal(demandeLamdan('Explique-moi le siman 253'), false);
});

test('référence — le Mehaber de la bonne partie, au format sefaria_get_text', () => {
  assert.equal(refMehaber(253, 'orach-chaim'), 'Shulchan_Arukh,_Orach_Chayim.253');
  assert.equal(refMehaber(100, 'yoreh-deah'), "Shulchan_Arukh,_Yoreh_De'ah.100");
  assert.equal(refMehaber('abc', 'orach-chaim'), null);
});

test('cas du 18/10 — lamdan + « Siman 253 » dans le contexte : le Mehaber est chargé et placé en contexte', async () => {
  mockFetch({ 'Shulchan_Arukh,_Orach_Chayim.253': MEHABER_253 });
  const r = await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN], question: PROFIL_LAMDAN, section: 'orach-chaim' });
  assert.ok(r, 'un bloc doit être rendu');
  assert.equal(r.siman, 253);
  assert.equal(r.ref, 'Shulchan_Arukh,_Orach_Chayim.253');
  assert.match(r.texte, /chargé par le serveur/);
  assert.match(r.texte, /מצטמק ורע לו/, 'le texte hébreu du Mehaber est dans le bloc');
  assert.match(r.texte, /Shulchan_Arukh_HaRav,_Orach_Chayim\.253\.<séif>/, 'le HaRav est renvoyé à sefaria_get_text séif par séif');
  assert.doesNotMatch(r.texte, /One may/, 'pas d\'anglais : hébreu seul');
});

test('périmètre — pas de bloc sans lamdan, sans siman nommé, ou en urgence', async () => {
  mockFetch({ 'Shulchan_Arukh,_Orach_Chayim.253': MEHABER_253 });
  assert.equal(await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_DEBUTANT], question: PROFIL_DEBUTANT }), null, 'débutant');
  assert.equal(await chargerTextePrimaire({ messagesUtilisateur: ['• Niveau : Lamdan'], question: 'Explique-moi le borer' }), null, 'aucun siman nommé');
  assert.equal(await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN], question: PROFIL_LAMDAN, urgent: true }), null, 'urgence');
});

test('profil sur un tour antérieur — le niveau vient de l\'historique, le siman du dernier message', async () => {
  mockFetch({ "Shulchan_Arukh,_Yoreh_De'ah.100": { ...MEHABER_253, ref: "Shulchan Arukh, Yoreh De'ah 100", versions: [{ language: 'he', text: 'בריה אפילו באלף לא בטלה' }] } });
  const r = await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN, 'Et le siman 100 de Yoreh De\'ah ?'], question: "Et le siman 100 de Yoreh De'ah ?", section: 'yoreh-deah' });
  assert.ok(r); assert.equal(r.siman, 100); assert.match(r.texte, /בריה אפילו באלף/); assert.match(r.texte, /Chakh, Taz/);
});

test('page 253 ouverte mais question sur le 318 — c\'est le siman DE LA QUESTION qui est chargé', async () => {
  mockFetch({
    'Shulchan_Arukh,_Orach_Chayim.318': { ...MEHABER_253, ref: 'Shulchan Arukh, Orach Chayim 318', versions: [{ language: 'he', text: 'המבשל בשבת' }] },
    'Shulchan_Arukh,_Orach_Chayim.253': MEHABER_253,
  });
  const q = PROFIL_LAMDAN.replace(/\[Ma question\][\s\S]*$/, '[Ma question]\nEt dans le siman 318, la cuisson après cuisson ?');
  const r = await chargerTextePrimaire({ messagesUtilisateur: [q], question: q, section: 'orach-chaim' });
  assert.ok(r); assert.equal(r.siman, 318); assert.match(r.texte, /המבשל בשבת/); assert.doesNotMatch(r.texte, /מצטמק/);
});

test('robustesse — Sefaria en 404, réponse sans hébreu, ou réseau en panne : null, jamais d\'exception', async () => {
  mockFetch({ 'Shulchan_Arukh,_Orach_Chayim.253': 404 });
  assert.equal(await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN], question: PROFIL_LAMDAN }), null, '404');
  mockFetch({ 'Shulchan_Arukh,_Orach_Chayim.253': { ...MEHABER_253, versions: [] } });
  assert.equal(await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN], question: PROFIL_LAMDAN }), null, 'sans hébreu');
  globalThis.fetch = async () => { throw new Error('réseau'); };
  assert.equal(await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN], question: PROFIL_LAMDAN }), null, 'panne');
});

test('troncature — un siman de 20 000 caractères est plafonné à 12 000 et le modèle en est averti', async () => {
  mockFetch({ 'Shulchan_Arukh,_Orach_Chayim.301': { ...MEHABER_253, ref: 'Shulchan Arukh, Orach Chayim 301', versions: [{ language: 'he', text: 'ב'.repeat(20000) }] } });
  const q = PROFIL_LAMDAN.replace('Siman 253', 'Siman 301');
  const r = await chargerTextePrimaire({ messagesUtilisateur: [q], question: q, section: 'orach-chaim' });
  assert.ok(r); assert.equal((r.texte.match(/ב/g) || []).length, 12000, 'exactement 12 000 caractères d\'hébreu conservés');
  assert.match(r.texte, /tronqué à 12000/); assert.match(r.texte, /Shulchan_Arukh,_Orach_Chayim\.301\.<séif>/);
  const bloc = blocTextePrimaire('Shulchan_Arukh,_Orach_Chayim.318', { siman: 318, hebrew: 'א'.repeat(100), truncated: true, url: null }, 'orach-chaim');
  assert.match(bloc, /tronqué à 12000/);
  assert.match(bloc, /Shulchan_Arukh,_Orach_Chayim\.318\.<séif>/);
});

test('câblage — chat.js appelle le chargement APRÈS l\'injection d\'urgence et AVANT la boucle d\'outils, gardé par !urgence.urgent', () => {
  const chat = readFileSync(new URL('../../api/chat.js', import.meta.url), 'utf8');
  assert.match(chat, /import \{ chargerTextePrimaire \} from '\.\/_texte-primaire\.js'/);
  const iUrg = chat.indexOf('CONSIGNE_URGENCE_MODELE + originalText');
  const iTp = chat.indexOf('await chargerTextePrimaire(');
  const iLoop = chat.indexOf('while (iterations < maxIterations)');
  assert.ok(iUrg > 0 && iTp > iUrg && iTp < iLoop, 'ordre : urgence → texte primaire → boucle');
  const bloc = chat.slice(iTp - 600, iTp);
  assert.match(bloc, /!urgence\.urgent/, 'le chargement est conditionné à l\'absence d\'urgence');
  assert.match(chat.slice(iTp, iTp + 900), /originalText \+ textePrimaire\.texte/, 'le bloc est AJOUTÉ au dernier message, il ne le remplace pas');
});

// Contre Sefaria réel, uniquement si le réseau répond : le cas exact du 18/10.
test('réel — Mehaber 253:1 ouvre par l\'opinion stricte (Rif/Rambam), la lénienté vient en יש אומרים', async (t) => {
  globalThis.fetch = realFetch;
  let r;
  try { r = await chargerTextePrimaire({ messagesUtilisateur: [PROFIL_LAMDAN], question: PROFIL_LAMDAN, section: 'orach-chaim' }); }
  catch { r = null; }
  if (!r) { t.skip('Sefaria injoignable'); return; }
  const iStrict = r.texte.indexOf('מצטמק ורע לו');
  const iLenient = r.texte.indexOf('בן דרוסאי');
  assert.ok(iStrict > 0, 'la condition stricte du séif 1 est dans le texte chargé');
  assert.ok(iLenient === -1 || iStrict < iLenient, 'si « בן דרוסאי » apparaît, c\'est APRÈS la position stricte');
  assert.doesNotMatch(r.texte, /תישוי/, 'le mot inventé n\'existe pas dans le texte');
  assert.doesNotMatch(r.texte, /tronqué/, 'le 253 (5 451 caractères) est livré entier, pas coupé à 4 000 comme le ferait l\'outil');
});
