// Tests du prompt principal V3 : hiérarchie, états documentaires, préfixe OH/YD,
// et présence des règles correspondant aux cas A-K. Ce sont des tests de
// SPÉCIFICATION du prompt (le texte dit-il ce qu'il doit dire ?), pas des tests
// de comportement du modèle — ceux-là exigent un essai conversationnel réel.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { SYSTEM_PROMPT, buildSystemPrompt } from '../../api/_system-prompt.js';
import { RESERVE } from '../../api/_reserve.js';

const oh = buildSystemPrompt('orach-chaim');
const yd = buildSystemPrompt('yoreh-deah');

test('le prompt Orah Haïm est un préfixe exact du prompt Yoreh De\'ah (cache partagé)', () => {
  assert.ok(yd.startsWith(oh));
  assert.ok(yd.length > oh.length);
});

test('aucun marqueur résiduel, aucun pourcentage de confiance, aucun accent grave', () => {
  assert.ok(!/\{\{/.test(oh));
  assert.ok(!/\d+\s?%/.test(oh));
  assert.ok(!/\bsûr à\b|confiance ≥|score de confiance/i.test(oh));
  assert.ok(!oh.includes('`'));
});

test('périmètre — sans corpus chargé, le prompt n\'annonce ni « 0 simanim » ni une plage vide', () => {
  assert.ok(!/\b0 simanim\b/.test(oh));
  assert.ok(/périmètre exact indisponible|simanim\)/.test(oh));
  assert.ok(!/\b(?:87-118|183-200|1-67)\b/.test(SYSTEM_PROMPT), 'plage recopiée dans le gabarit');
});

test('hiérarchie unique en cinq rangs, dans l\'ordre demandé', () => {
  const i1 = oh.indexOf('1. Protéger les personnes, dire vrai');
  const i2 = oh.indexOf('2. Identifier correctement chaque ouvrage');
  const i3 = oh.indexOf('3. Répondre à la question réellement posée');
  const i4 = oh.indexOf('4. Adapter la recherche');
  const i5 = oh.indexOf('5. Respecter la langue');
  assert.ok(i1 > 0 && i1 < i2 && i2 < i3 && i3 < i4 && i4 < i5);
});

test('états documentaires observables, à la place des probabilités', () => {
  for (const s of [
    'texte primaire consulté et pertinent',
    'synthèse consultée, original non vérifié',
    'attribution non vérifiée',
    'sources contradictoires',
    'informations du cas insuffisantes',
  ]) assert.ok(oh.includes(s), s);
  assert.ok(/jamais par un pourcentage ni une probabilité de vérité/.test(oh));
});

test('une seule réserve, en quatre langues, et jamais l\'ancienne formulation', () => {
  for (const l of ['fr', 'he', 'en', 'es']) assert.equal(oh.split(RESERVE[l]).length - 1, 1, l);
  assert.ok(!oh.includes("Ce n'est pas un psak halakha"));
  assert.ok(!oh.includes('Confiance limitée'));
  assert.ok(/ni après une consigne d'urgence vitale/.test(oh));
});

test('A — identification des ouvrages : identifiants distincts, pas de substitution silencieuse, champs work/author', () => {
  assert.ok(oh.includes('Shulchan_Arukh,_…'));
  assert.ok(oh.includes('Shulchan_Arukh_HaRav,_…'));
  assert.ok(/Ne substitue jamais silencieusement un ouvrage à un autre/.test(oh));
  assert.ok(/champs work, author, url, nature/.test(oh));
  assert.ok(/réussite d'un appel d'outil vérifie qu'une référence existe, pas qu'elle appartient/.test(oh));
});

test('B — relance : reconnaître, retirer et corriger une attribution erronée', () => {
  assert.ok(/Si tu as attribué un passage au mauvais ouvrage, reconnais-le/.test(oh));
  assert.ok(/Une contestation de l'utilisateur déclenche une vérification/.test(oh));
});

test('C — urgence vitale : secours d\'abord, aucun numéro inventé, aucune réserve ensuite', () => {
  const sec = oh.slice(oh.indexOf('<urgence_vitale>'), oh.indexOf('</urgence_vitale>'));
  assert.ok(/appeler les secours locaux/.test(sec));
  assert.ok(/N'invente aucun numéro d'urgence/.test(sec));
  assert.ok(/N'ajoute jamais, après une consigne d'urgence/.test(sec));
  assert.ok(sec.indexOf('<urgence_vitale>') < oh.indexOf('<question_et_profil>'), 'l\'urgence précède le profil');
});

test('D — lecture de l\'unité de raisonnement : le séif suivant n\'est pas une garantie universelle', () => {
  assert.ok(/במה דברים אמורים/.test(oh));
  assert.ok(/La lecture du seul séif suivant n'est pas une garantie universelle/.test(oh));
  assert.ok(/Un extrait de recherche est tronqué/.test(oh));
});

test('E — synthèse DAAT contre original : signaler l\'écart, ne pas reproduire la synthèse', () => {
  assert.ok(/ne signifie pas qu'une synthèse DAAT prime sur le texte original/.test(oh));
  assert.ok(/ne reproduis pas la synthèse/.test(oh));
  assert.ok(/Un score de recherche mesure la pertinence de récupération/.test(oh));
});

test('F/liens — pas d\'URL au jugé : seulement le champ url rendu par l\'outil', () => {
  assert.ok(/Un lien Sefaria provient exclusivement du champ url rendu par sefaria_get_text/.test(oh));
  assert.ok(/ne construis pas de route \/oh\/ ou \/yd\//.test(oh));
});

test('G — caveat et caveatNote préservés ; jamais attribuer au Rav ce qu\'il a écarté', () => {
  assert.ok(/respecte « caveatNote »/.test(oh));
  assert.ok(/Ne jamais attribuer au Rav une position qu'il a expressément mise à distance/.test(oh));
});

test('H — sans profil, répondre à ce qui peut l\'être ; une définition n\'exige pas de minhag', () => {
  assert.ok(/une définition, une traduction, l'explication d'un concept ou d'un séif n'exigent ni minhag ni niveau/.test(oh));
  assert.ok(/Ne redemande pas un profil complet/.test(oh));
});

test('I — traditions : pas de catégories uniformes, pas de filtrage qui efface les divergences', () => {
  assert.ok(/ne désignent une opinion unique/.test(oh));
  assert.ok(/ne filtre pas les sources au point de faire disparaître/.test(oh));
  assert.ok(/N'impose pas la pratique 'Habad/.test(oh));
});

test('J — attribution à un Rebbe : source précise, sinon « pas de texte consulté », jamais « le Rebbe a dit »', () => {
  assert.ok(/lequel des Rebbeim/.test(oh));
  assert.ok(/jamais « le Rebbe a dit »/.test(oh));
  assert.ok(/Igrot Kodesh, les Likoutei Si'hot.*ne sont pas dans tes outils/.test(oh));
});

test('K — Tanya : partie et chapitre ; original distinct des explications ultérieures', () => {
  assert.ok(/Pour le Tanya, identifie sa partie et son chapitre/.test(oh));
  assert.ok(/distingue le texte de l'Admour Hazaken des explications ultérieures/.test(oh));
});

test('L — présentation : citation « > » pour l\'hébreu long, tableau Markdown, pas de HTML, glose de l\'hébreu', () => {
  assert.ok(/ligne commençant par « > »/.test(oh));
  assert.ok(/tableau Markdown bien formé/.test(oh));
  assert.ok(/N'écris pas de HTML/.test(oh));
  assert.ok(/chaque mot hébreu d'une réponse en français, anglais ou espagnol porte-t-il sa traduction/.test(oh));
});

test('Yoreh De\'ah — le complément ne rétablit aucune plage et n\'écrase aucune règle', () => {
  const ov = yd.slice(oh.length);
  assert.ok(/ne rétablit aucun chiffre/.test(ov));
  assert.ok(!/remplacent les instructions par défaut/.test(ov));
  assert.ok(/Michna Beroura ne couvre pas le Yoreh De'ah/.test(ov));
});
