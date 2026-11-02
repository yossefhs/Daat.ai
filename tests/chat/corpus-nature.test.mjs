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

// Point 3 (18/10/2026) — le texte hébreu du séif du HaRav parvient au modèle, étiqueté.
const harav = { ...base, id: 'oh-daat-harav-siman-253-daatharav-14', siman: 253, level: 'daat-harav', levelLabel: 'Niveau 4 — Daat HaRav',
  text: 'Rendu français du séif 14 … ' + 'x'.repeat(900) + '\n\nכירה שהסיקוה בקש וגבבא ונטל הקדרה מעליה',
  he: 'כירה שהסיקוה בקש וגבבא, או אפלו בגפת ועצים אלא שהיא גרופה וקטומה, ונטל הקדרה מעליה' };

test('point 3 — un extrait Daat HaRav porte source_he (le séif en hébreu, entier) avec sa nature, hors du summary tronqué', () => {
  const h = formatChunkHit(harav);
  assert.equal(h.source_he, harav.he);
  assert.match(h.source_he_nature, /Choul'han Aroukh HaRav/);
  assert.match(h.source_he_nature, /fait autorité/);
  assert.ok(!h.summary.includes('כירה שהסיקוה'), 'le summary (700 car.) ne contenait pas l\'hébreu : c\'est bien pour cela que source_he existe');
});

test('point 3 — seul le niveau Daat HaRav porte source_he ; au-delà du 3e résultat, on l\'omet', () => {
  assert.equal(formatChunkHit({ ...harav, level: 'base' }).source_he, undefined, 'niveau 1 : le Mehaber est déjà le texte');
  assert.equal(formatChunkHit({ ...harav, level: 'synthese' }).source_he, undefined);
  assert.equal(formatChunkHit({ ...harav, he: null }).source_he, undefined, 'page sans bloc sa-he');
  assert.equal(formatChunkHit(harav, { avecHebreu: false }).source_he, undefined);
  assert.equal(formatChunkHit(harav, { avecHebreu: true }).source_he, harav.he);
});

test('point 3 — la description de daat_search_corpus annonce source_he', () => {
  const search = CORPUS_TOOLS.find(t => t.name === 'daat_search_corpus');
  assert.match(JSON.stringify(search), /source_he/);
});
