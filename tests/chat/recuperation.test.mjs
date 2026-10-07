// Banc de régression de la RÉCUPÉRATION du chat (BM25 corpus-first).
//
// Les autres tests de tests/chat/ vérifient le câblage avec des chunks simulés ;
// aucun ne passait par le moteur de recherche. Celui-ci charge le VRAI corpus et
// rejoue tests/chat/bench-recuperation.json avec les réglages du routage
// (api/chat.js : minScore 8, strict, limit 3).
//
// Trois invariants :
//  1. un cas « attendu » non marqué défaillant doit rendre un des simanim
//     acceptables dans son top-3 ;
//  2. un cas « abstention » non marqué défaillant ne doit RIEN rendre ;
//  3. un cas marqué `connu_defaillant` doit toujours échouer — s'il réussit, le
//     test échoue et demande de retirer le drapeau : le banc ne se périme pas.
//
// data/corpus-shabbat.json est une sortie de build (non versionnée) : s'il est
// absent, tout est ignoré plutôt que rouge (clone frais → `npm run build`).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ici = dirname(fileURLToPath(import.meta.url));
const corpusPath = join(ici, '../../data/corpus-shabbat.json');
const bench = JSON.parse(readFileSync(join(ici, 'bench-recuperation.json'), 'utf8'));
const skip = existsSync(corpusPath) ? false : 'data/corpus-shabbat.json absent — lancer `npm run build`';

const { limit, minScore, strict } = bench.parametres;
const cas = bench.cas;

// Planchers à ne pas franchir vers le bas. Mesurés le 7 octobre 2026 sur 46 cas
// « attendu » (défaillants connus inclus) : rappel@3 = 40/46 (87,0 %), rang 1 =
// 30/46 (65,2 %). Ils ont reculé de 88/66 % à 87/65 % quand deux cas ont été
// ajoutés au banc (dont un défaillant connu), sans que le moteur ait changé sur
// les anciens. À relever quand le moteur progresse ; ne jamais les baisser pour
// faire passer un correctif.
const PLANCHER_RAPPEL_3 = 0.86;
const PLANCHER_RANG_1 = 0.65;

async function mesurer() {
  const { searchCorpus, getSimanChunks } = await import('../../api/_corpus-search.js');
  const lignes = cas.map((c) => {
    const r = searchCorpus(c.q, { limit, minScore, strict, section: c.section });
    const simanim = r.results.map((x) => +x.siman);
    const scores = r.results.map((x) => x.score);
    const ok = c.type === 'attendu'
      ? simanim.some((s) => c.siman.includes(s))
      : simanim.length === 0;
    const rang1 = c.type === 'attendu' && simanim.length > 0 && c.siman.includes(simanim[0]);
    return { c, simanim, scores, ok, rang1 };
  });
  return { lignes, getSimanChunks };
}

test('banc — les simanim attendus existent dans la section visée (garde contre une faute de frappe du banc)', { skip }, async () => {
  const { getSimanChunks } = await mesurer();
  for (const c of cas.filter((x) => x.type === 'attendu')) {
    assert.ok(Array.isArray(c.siman) && c.siman.length > 0, `${c.id} : liste de simanim vide`);
    const present = c.siman.some((s) => getSimanChunks(s, { section: c.section }).length > 0);
    assert.ok(present, `${c.id} : aucun des simanim ${c.siman} n’existe en ${c.section}`);
  }
});

test('banc — les cas non défaillants réussissent, les cas défaillants connus échouent encore', { skip }, async () => {
  const { lignes } = await mesurer();
  const regressions = lignes.filter((l) => !l.c.connu_defaillant && !l.ok);
  const gueris = lignes.filter((l) => l.c.connu_defaillant && l.ok);
  const fmt = (l) => `${l.c.id} [${l.c.type}] « ${l.c.q} » → ${l.simanim.map((s, i) => `${s}(${l.scores[i].toFixed(1)})`).join(' ') || '∅'}`;
  assert.deepEqual(regressions.map(fmt), [], 'RÉGRESSION : ces cas réussissaient ou devaient réussir');
  assert.deepEqual(gueris.map(fmt), [], 'GUÉRISON : retirer `connu_defaillant` de ces cas du banc, puis relever les planchers');
});

test('banc — rappel@3 et rang 1 sur les questions à réponse attendue ne passent pas sous leur plancher', { skip }, async (t) => {
  const { lignes } = await mesurer();
  const att = lignes.filter((l) => l.c.type === 'attendu');
  const rappel = att.filter((l) => l.ok).length / att.length;
  const rang1 = att.filter((l) => l.rang1).length / att.length;

  const abst = lignes.filter((l) => l.c.type === 'abstention');
  const fausses = abst.filter((l) => !l.ok);
  const bons = att.filter((l) => l.ok).flatMap((l) => l.scores.slice(0, 1));
  const faux = fausses.flatMap((l) => l.scores.slice(0, 1));
  t.diagnostic(`attendus : ${att.length} · rappel@3 ${(rappel * 100).toFixed(0)} % · rang 1 ${(rang1 * 100).toFixed(0)} %`);
  t.diagnostic(`abstentions : ${abst.length - fausses.length}/${abst.length} tenues · ${fausses.length} réponses servies à tort`);
  if (bons.length && faux.length) {
    const min = (a) => Math.min(...a).toFixed(1);
    const max = (a) => Math.max(...a).toFixed(1);
    t.diagnostic(`score du 1er résultat — bonnes réponses ${min(bons)}–${max(bons)} · réponses à tort ${min(faux)}–${max(faux)} (le seuil ${minScore} sépare-t-il ? ${Math.min(...faux) > Math.max(...bons) || Math.max(...faux) < Math.min(...bons) ? 'oui' : 'NON, plages qui se recouvrent'})`);
  }
  assert.ok(rappel >= PLANCHER_RAPPEL_3, `rappel@3 ${(rappel * 100).toFixed(0)} % < plancher ${PLANCHER_RAPPEL_3 * 100} %`);
  assert.ok(rang1 >= PLANCHER_RANG_1, `rang 1 ${(rang1 * 100).toFixed(0)} % < plancher ${PLANCHER_RANG_1 * 100} %`);
});
