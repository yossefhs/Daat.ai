// Tests C (urgence vitale) et réserve unique — outils SIMULÉS, aucun modèle.
// Un test simulé réussi ne démontre pas la fiabilité du système complet : il
// vérifie que le serveur ne peut PAS produire la contradiction observée
// (consigne d'urgence suivie de « c'est à ton Rav de trancher »).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { RESERVE, reserveFor, URGENCE, urgenceFor } from '../../api/_reserve.js';
import { detecteUrgenceVitale, CONSIGNE_URGENCE_MODELE } from '../../api/_urgence.js';

test('la réserve existe en quatre langues et reserveFor retombe sur le français', () => {
  for (const l of ['fr', 'he', 'en', 'es']) assert.ok(RESERVE[l].length > 40, l);
  assert.equal(reserveFor('xx'), RESERVE.fr);
  assert.equal(reserveFor('HE'), RESERVE.he);
});

test('C — la consigne d\'urgence ne contient aucune réserve « consulte ton Rav » ni numéro d\'urgence', () => {
  for (const l of ['fr', 'he', 'en']) {
    const t = URGENCE[l];
    assert.ok(!/consulte ton Rav|à ton Rav de trancher|consult your Rav|התייעץ עם רב|לפנות לרב/i.test(t), `réserve dans ${l}`);
    assert.ok(!/\b(?:15|18|112|911|101|100)\b/.test(t), `numéro d'urgence dans ${l}`);
    assert.ok(/secours|emergency|חירום/i.test(t), `mot secours absent en ${l}`);
    assert.ok(/328|שכ״ח/.test(t), `référence OH 328 absente en ${l}`);
  }
  assert.equal(urgenceFor('en'), URGENCE.en);
});

test('C — la question observée est détectée comme urgence vitale, sans indice d\'étude', () => {
  const q = "C'est Shabbat. Une personne vient de s'effondrer et ne répond plus. Faut-il attendre l'avis d'un Rav avant d'appeler les secours ?";
  const r = detecteUrgenceVitale(q);
  assert.equal(r.urgent, true);
  assert.equal(r.etude, false);
  assert.ok(r.indices.length >= 1);
});

test('C — détection en hébreu et en anglais', () => {
  assert.equal(detecteUrgenceVitale('מישהו התמוטט ולא מגיב, מה לעשות בשבת?').urgent, true);
  assert.equal(detecteUrgenceVitale('Someone collapsed and is not breathing on Shabbos, should I wait for a rav?').urgent, true);
});

test('C — une question halakhique ordinaire n\'est pas une urgence', () => {
  for (const q of [
    'Puis-je retirer les arêtes du poisson à Shabbat ?',
    'Explique-moi le siman 319 (borer).',
    'Quelle berakha sur une banane ?',
    'What is muktzeh?',
  ]) assert.equal(detecteUrgenceVitale(q).urgent, false, q);
});

test('C — une question d\'ÉTUDE sur le sujet est signalée comme étude (le corpus n\'est pas court-circuité)', () => {
  const r = detecteUrgenceVitale("Que dit le siman 328 sur celui qui s'effondre à Shabbat ?");
  assert.equal(r.urgent, true);
  assert.equal(r.etude, true);
});

test('C — la consigne injectée au modèle interdit explicitement la réserve après l\'urgence', () => {
  assert.ok(CONSIGNE_URGENCE_MODELE.includes('secours'));
  assert.ok(/AUCUNE réserve/.test(CONSIGNE_URGENCE_MODELE));
  assert.ok(/numéro d'urgence/.test(CONSIGNE_URGENCE_MODELE));
});
