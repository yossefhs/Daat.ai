// Cadrage du domaine dans les prompts de reformulation (corpus-first de api/chat.js,
// api/chat-corpus.js) — contrôle sur le TEXTE des sources, comme chat-wiring.test.mjs :
// les deux fichiers instancient le client Anthropic à l'import.
//
// Ce que ce test verrouille : le prompt nomme un DOMAINE (Shabbat, Érouvin, Te'houmin,
// quotidien, Issour ve-Heter, Nidah), jamais une plage de simanim — les bornes restent
// dans le code. corpus-nature.test.mjs ne contrôle que les descriptions d'outils.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { RESERVE } from '../../api/_reserve.js';

const chat = readFileSync(new URL('../../api/chat.js', import.meta.url), 'utf8');
const chatCorpus = readFileSync(new URL('../../api/chat-corpus.js', import.meta.url), 'utf8');

const PLAGE = /\d{2,3}\s*[-–]\s*\d{2,3}/;
const SECTIONS = ['orach-chaim', 'yoreh-deah', undefined];

function extraire(source, debut, fin) {
  const i = source.indexOf(debut);
  assert.ok(i >= 0, `introuvable : ${debut}`);
  const j = source.indexOf(fin, i);
  assert.ok(j > i, `fin introuvable après : ${debut}`);
  return source.slice(i, j + fin.length);
}

// buildSystemPrompt(lang, section, topSiman) — fonction pure, n'utilise que RESERVE.
const buildSystemPrompt = new Function('RESERVE',
  extraire(chatCorpus, 'function buildSystemPrompt(', '\n}\n') + '\nreturn buildSystemPrompt;')(RESERVE);

// L'expression `const corpusDom = … ;` de serveCorpusAnswer, évaluée pour (section, topNum).
const corpusDomSrc = extraire(chat, 'const corpusDom = ', "p: 'le principe halakhique' });");
const corpusDom = new Function('section', 'topNum', corpusDomSrc + '\nreturn corpusDom;');

test('chat-corpus — le prompt ne recopie aucune plage de simanim, pour tout n de 1 à 697', () => {
  for (const section of SECTIONS) {
    for (const lang of ['fr', 'he', 'en']) {
      for (let n = 1; n <= 697; n++) {
        const p = buildSystemPrompt(lang, section, n);
        assert.ok(!PLAGE.test(p), `plage dans le prompt (section ${section}, n ${n}) : ${p.match(PLAGE)}`);
      }
    }
  }
});

test('chat-corpus — Érouvin et Te\'houmin sont cadrés à part, Chabbat et le quotidien inchangés', () => {
  assert.match(buildSystemPrompt('fr', 'orach-chaim', 366), /les hilkhot Érouvin/);
  assert.match(buildSystemPrompt('fr', 'orach-chaim', 395), /les hilkhot Érouvin/);
  assert.match(buildSystemPrompt('fr', 'orach-chaim', 396), /les hilkhot Te'houmin/);
  assert.match(buildSystemPrompt('fr', 'orach-chaim', 407), /les hilkhot Te'houmin/);
  assert.match(buildSystemPrompt('fr', 'orach-chaim', 365), /sur les hilkhot Shabbat et UN EXTRAIT/);
  assert.match(buildSystemPrompt('fr', 'orach-chaim', 408), /journée du juif/);
  assert.match(buildSystemPrompt('fr', 'yoreh-deah', 397), /Nidah/);
});

test('chat.js corpus-first — le cadrage ne recopie aucune plage, pour tout n de 1 à 697', () => {
  for (const section of SECTIONS) {
    for (let n = 1; n <= 697; n++) {
      const { d, t, p } = corpusDom(section, n);
      for (const s of [d, t, p]) assert.ok(!PLAGE.test(s), `plage (section ${section}, n ${n}) : ${s}`);
    }
  }
  assert.match(corpusDom('orach-chaim', 380).d, /Érouvin/);
  assert.match(corpusDom('orach-chaim', 400).d, /Te'houmin/);
  assert.equal(corpusDom('orach-chaim', 300).d, 'les hilkhot Shabbat');
  assert.match(corpusDom('orach-chaim', 408).d, /journée du juif/);
});
