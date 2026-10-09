// Garde-fous du chemin court (corpus-first) — siman 89 de Yoré Déa (פ״ט).
// Mesuré en production le 30 septembre 2026 : à une question sur le fromage après
// la viande, le chemin court a servi un extrait de contexte SANS règle
// (yd-base-siman-89-s3-b2) et Haiku a répondu « tu peux recommencer aussitôt » —
// l'inverse du séif 1 (six heures). Réponse mise en cache trente jours.
// Ces tests rejouent le cas : fonctions pures, câblage statique de api/chat.js
// (qui ne s'importe pas sans variables d'environnement), et — si le corpus est
// construit (`npm run build`) — la recherche réelle.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { questionDePermission, autorisationPersonnelle } from '../../api/_garde-corpus.js';
import { RESERVE } from '../../api/_reserve.js';

const chat = readFileSync(new URL('../../api/chat.js', import.meta.url), 'utf8');
const recherche = readFileSync(new URL('../../api/_corpus-search.js', import.meta.url), 'utf8');

const QUESTIONS_SIMAN_89 = [
  'Combien de temps attendre entre la viande et le fromage ?',
  'Après avoir mangé de la viande, je peux manger du fromage tout de suite ?',
  "J'ai mangé de la viande, est-ce que je peux recommencer aussitôt avec du fromage si je me nettoie bien ?",
  'fromage aussitôt après la viande',
  'Can I eat cheese right after meat?',
  'כמה זמן צריך להמתין בין בשר לחלב?',
  'האם מותר לאכול גבינה אחרי בשר?',
];

test('89 — les questions de permission ou de délai sont reconnues, dans les trois langues', () => {
  for (const q of QUESTIONS_SIMAN_89) assert.ok(questionDePermission(q), q);
});

test('89 — une question d\'étude n\'est pas prise pour une question de permission', () => {
  for (const q of ['Explique le siman 89', 'Quelle est la raison des six heures ?', "Qu'est-ce que la viande entre les dents ?"]) {
    assert.ok(!questionDePermission(q), q);
  }
});

test('89 — la réponse servie en production est reconnue comme une autorisation personnelle', () => {
  assert.equal(autorisationPersonnelle('Tu peux recommencer aussitôt, à condition de bien te nettoyer. Source : Siman 89'), 'tu peux');
  assert.ok(autorisationPersonnelle('Vous pouvez manger du fromage après vous être rincé la bouche.'));
  assert.ok(autorisationPersonnelle('You can eat cheese right away.'));
  assert.ok(autorisationPersonnelle('מותר לך לאכול גבינה מיד.'));
});

test('89 — rapporter une source, orienter vers le Rav ou la réserve du site ne sont pas des autorisations', () => {
  for (const t of [
    "Le Rav écrit que c'est permis lorsque l'on a attendu six heures. Source : Siman 89",
    'Tu peux consulter ton Rav pour ton cas.',
    'Tu peux reposer la question en mode étendu.',
    'Tu peux aussi relire le séif 1.',
    'You can ask your Rav.',
    RESERVE.fr, RESERVE.en, RESERVE.he,
  ]) assert.equal(autorisationPersonnelle(t), null, t);
});

// Le corps de serveCorpusAnswer, pour les contrôles de câblage.
const debut = chat.indexOf('async function serveCorpusAnswer(');
const corps = chat.slice(debut, chat.indexOf('\nfunction serveUrgenceStatique', debut));

test('89 — Yoré Déa : une question de permission décline le chemin court AVANT toute écriture', () => {
  const declin = corps.indexOf("=== 'yoreh-deah' && questionDePermission(lastUserText)");
  assert.ok(declin > 0, 'déclin absent');
  const premiereEcriture = Math.min(...['res.write(', 'ensureSse()'].map((m) => corps.indexOf(m)).filter((i) => i > 0));
  assert.ok(declin < premiereEcriture, 'le déclin doit précéder toute écriture au lecteur');
  assert.ok(declin < corps.indexOf('await kv.get(corpusKvKey)'), 'le déclin doit précéder la lecture du cache');
});

test('89 — la réponse générée est lue ENTIÈRE et vérifiée avant d\'être servie', () => {
  const tampon = corps.slice(corps.indexOf('Tampon COMPLET'), corps.indexOf('await stream.finalMessage()'));
  assert.ok(tampon.length > 0);
  assert.ok(!/res\.write\(/.test(tampon), 'plus aucune écriture pendant la génération');
  assert.ok(/autorisationPersonnelle\(buffer\)/.test(tampon), 'vérification absente');
  assert.ok(/refuse = true;[\s\S]*?return false;/.test(tampon), 'un refus doit rendre la main');
});

test('89 — un refus ne retombe pas sur le corpus brut, et le cache ne ressert jamais un feu vert', () => {
  assert.ok(/allowRawFallback && !offTopic && !refuse\)/.test(corps));
  assert.ok(/&& !autorisationPersonnelle\(raw\.text\)\) \{\s*cachedCorpus = raw;/.test(corps));
});

test('89 — le cache des réponses corpus est purgé (v5)', () => {
  assert.match(recherche, /export const CORPUS_CACHE_VERSION = 'v5';/);
});

// Recherche réelle — seulement si le corpus a été construit localement.
const CORPUS = new URL('../../data/corpus-shabbat.json', import.meta.url);
test('89 — la recherche réelle tombe bien sur le siman 89, et la question est déclinée', { skip: !existsSync(CORPUS) && 'corpus non construit (npm run build)' }, async () => {
  const { searchCorpus } = await import('../../api/_corpus-search.js');
  for (const q of QUESTIONS_SIMAN_89.slice(0, 4)) {
    const r = searchCorpus(q, { limit: 3, minScore: 8, strict: true, section: 'yoreh-deah' });
    const top = (r.results || [])[0];
    assert.ok(top, `aucun extrait pour « ${q} »`);
    assert.equal(String(top.siman), '89', q);
    assert.ok(questionDePermission(q), `« ${q} » doit décliner le chemin court`);
  }
});
