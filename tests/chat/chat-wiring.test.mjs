// Câblage des voies de réponse — contrôles STATIQUES sur les sources.
// api/chat.js instancie le client Anthropic à l'import et exige des variables
// d'environnement : on ne l'importe pas, on lit son texte. Ces tests garantissent
// que les correctifs sont câblés sur CHAQUE voie (normale, corpus-first, secours,
// synthèse forcée, quota épuisé), pas seulement dans le prompt.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { dateContextBlock } from '../../api/_date.js';

const chat = readFileSync(new URL('../../api/chat.js', import.meta.url), 'utf8');
const chatCorpus = readFileSync(new URL('../../api/chat-corpus.js', import.meta.url), 'utf8');
const mm = readFileSync(new URL('../../api/_mareh_mekomot.js', import.meta.url), 'utf8');

test('C — l\'urgence est détectée AVANT le routage et court-circuite corpus-first, pré-RAG et sauvetage à quota', () => {
  assert.ok(chat.indexOf('detecteUrgenceVitale(lastUserForUrgence') < chat.indexOf('await identifyUser(req)'));
  assert.ok(/!urgence\.urgent &&\s*\n\s*model\.id !== MODELS\.opus\.id/.test(chat), 'corpus-first non gardé');
  assert.ok(/skipPreRag = isOpus \|\| urgence\.urgent/.test(chat), 'pré-RAG non gardé');
  assert.equal((chat.match(/return serveUrgenceStatique\(\{ res/g) || []).length, 3, 'quota jour, quota mois, budget Anthropic');
});

test('C — la synthèse forcée a une variante sans renvoi au Rav en cas d\'urgence, et ne demande plus la rigueur par défaut', () => {
  assert.ok(/const synthText = urgence\.urgent/.test(chat));
  // Le source porte des apostrophes échappées (l\'avis d\'un) : on tolère le « \ ».
  assert.ok(/sans aucun renvoi à l\\?'avis d\\?'un Rav/.test(chat));
  assert.ok(/ni permission ni interdiction personnelle/.test(chat));
  assert.ok(!/tu ne dois donc formuler AUCUNE permission pratique/.test(chat));
});

test('C — la consigne de priorité est injectée dans le dernier message utilisateur, pas dans le bloc caché', () => {
  assert.ok(/CONSIGNE_URGENCE_MODELE \+ originalText/.test(chat));
});

test('réserve unique — le chemin corpus-first (Haiku) et chat-corpus.js emploient RESERVE, et renvoient HORS-SUJET sur un danger vital', () => {
  assert.ok(/\$\{RESERVE\.fr\}/.test(chat) && /\$\{RESERVE\.he\}/.test(chat) && /\$\{RESERVE\.en\}/.test(chat));
  assert.ok(/DANGER IMMÉDIAT pour une vie[\s\S]{0,120}HORS-SUJET/.test(chat));
  assert.ok(/\$\{RESERVE\.fr\}/.test(chatCorpus));
  assert.ok(/detecteUrgenceVitale\(question\)/.test(chatCorpus));
  assert.ok(/disclaimer: RESERVE\.fr/.test(mm));
});

test('réserve unique — l\'ancienne formulation a disparu de toutes les voies de génération', () => {
  const dir = new URL('../../api/', import.meta.url);
  const offenders = [];
  for (const f of readdirSync(dir)) {
    if (!f.endsWith('.js')) continue;
    const src = readFileSync(new URL(f, dir), 'utf8');
    if (/Ce n'est (?:pas|PAS) un psak halakha/.test(src)) offenders.push(f);
    if (/Pour ton cas précis, c'est à ton Rav de trancher/.test(src)) offenders.push(f);
  }
  assert.deepEqual(offenders, []);
});

test('date — un second bloc système non caché porte la date ; le bloc caché reste le prompt seul', () => {
  assert.ok(/text: dateContextBlock\(\)/.test(chat));
  const i = chat.indexOf("cache_control: { type: 'ephemeral', ttl: '1h' }");
  assert.ok(i > 0 && chat.indexOf('dateContextBlock()', i) > i);
  const b = dateContextBlock(new Date('2026-09-28T12:00:00Z'));
  assert.ok(b.includes('2026-09-28'));
  assert.ok(/Tishri/.test(b));
  assert.ok(/ne donne aucun horaire/.test(b));
});

test('compteurs — une réponse servie par le corpus renvoie la jauge mensuelle réelle', () => {
  assert.ok(/month_remaining: process\.env\.CORPUS_QUOTA_FREE === 'false'/.test(chat));
});

test('périmètre — chat.js ne recopie plus les plages du corpus comme des faits d\'index', () => {
  assert.ok(!/OH quotidien \(1-185\)/.test(chat));
  assert.ok(!/YD Issour ve-Heter \(87-118\)/.test(chat));
});

test('constat C — extract-corpus propage l\'ancre de séif dans sourceUrl quand la page en porte une', () => {
  const ex = readFileSync(new URL('../../scripts/extract-corpus.js', import.meta.url), 'utf8');
  assert.ok(/function nearestSeifAnchor/.test(ex));
  assert.ok(/\(c\.anchor \? `#\$\{c\.anchor\}` : ''\)/.test(ex));
});
