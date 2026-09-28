// Tests E (synthèse ≠ original) et G (réserve éditoriale) au niveau de l'outil
// corpus — chunks SIMULÉS. Le corpus réel (data/corpus-shabbat.json) n'est pas
// requis : formatChunkHit est pur.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { formatChunkHit, CORPUS_TOOLS } from '../../api/_corpus.js';

const base = { id: 'oh-base-siman-319-s1-b1', siman: 319, section: 'orach-chaim', level: 'base', levelLabel: 'Niveau 1 — Base', text: 'x'.repeat(900), sourceUrl: '/oh/319/base#seif-1' };

test('E — chaque résultat porte une nature qui distingue texte source et synthèse du site', () => {
  assert.match(formatChunkHit(base).nature, /texte source/);
  assert.match(formatChunkHit({ ...base, level: 'synthese' }).nature, /synthèse.*ne prouve pas l'original/);
  assert.match(formatChunkHit({ ...base, level: 'lamdan' }).nature, /synthèse.*ne prouve pas l'original/);
  assert.match(formatChunkHit({ ...base, level: 'daat-harav' }).nature, /Choul'han Aroukh HaRav/);
  assert.match(formatChunkHit({ ...base, level: 'daat-harav', section: 'yoreh-deah' }).nature, /autres décisionnaires/);
});

test('E — l\'extrait est tronqué et le dit (hasMore), avec l\'URL de la page (ancre de séif comprise)', () => {
  const h = formatChunkHit(base);
  assert.equal(h.hasMore, true);
  assert.ok(h.summary.length < 900);
  assert.equal(h.url, '/oh/319/base#seif-1');
});

test('G — un chunk sous réserve de l\'auteur porte caveat ET caveatNote, jamais le drapeau seul', () => {
  const h = formatChunkHit({ ...base, caveat: true });
  assert.equal(h.caveat, true);
  assert.match(h.caveatNote, /hors corpus, à vérifier/);
  assert.match(h.caveatNote, /renvoie explicitement au Rav/);
  assert.equal(formatChunkHit(base).caveat, undefined);
});

test('périmètre — les descriptions d\'outils ne portent plus aucune plage de simanim en dur', () => {
  for (const t of CORPUS_TOOLS) {
    const blob = JSON.stringify(t);
    assert.ok(!/\b(?:87-118|183-200|242-365|1-67)\b/.test(blob), `${t.name} recopie une plage`);
    assert.ok(!/124 simanim|241 simanim|513 simanim/.test(blob), `${t.name} recopie un total`);
  }
  const search = CORPUS_TOOLS.find(t => t.name === 'daat_search_corpus');
  assert.match(search.description, /nature/);
  assert.match(search.input_schema.properties.section.description, /prompt système/);
});
