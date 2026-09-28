// Tests L (rendu Markdown : tableaux, citations, hébreu RTL, liens) et H (accueil
// sans profil obligatoire) sur le widget. renderMarkdown vit dans une IIFE qui
// touche `document` au chargement : on extrait la fonction du source et on
// l'évalue avec des stubs, sans navigateur.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const src = readFileSync(new URL('../../assets/js/chat-widget.js', import.meta.url), 'utf8');

function extractFunction(name) {
  const start = src.indexOf(`function ${name}(`);
  assert.ok(start > 0, `${name} introuvable`);
  let i = src.indexOf('{', start), depth = 0;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  return src.slice(start, i + 1);
}

const stubs = `
  function escapeHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function stripTags(h){return String(h||'').replace(/<[^>]*>/g,'');}
  function detectMessageDir(t){const he=(t.match(/[\\u05d0-\\u05ea]/g)||[]).length;const lat=(t.match(/[a-zA-Z]/g)||[]).length;return he>lat?'rtl':'ltr';}
  function blockDir(html){return detectMessageDir(stripTags(html))==='rtl'?' dir="rtl"':'';}
`;
const renderMarkdown = new Function(stubs + extractFunction('renderMarkdown') + '; return renderMarkdown;')();

test('L — un tableau Markdown devient une <table>, pas du texte brut', () => {
  const md = '| Source | Position |\n|---|---|\n| Mehaber | permis |\n| Rama | interdit |\n';
  const html = renderMarkdown(md);
  assert.ok(html.includes('<table>') && html.includes('<th>Source</th>') && html.includes('<td>Rama</td>'));
  assert.ok(!html.includes('|---|'));
});

test('L — une citation « > » en hébreu devient un <blockquote dir="rtl">', () => {
  const html = renderMarkdown('Le Choulhan Aroukh écrit :\n\n> אסור להשכיר כליו לגוי כשהוא יודע שיעשה בהם מלאכה בשבת\n\nTraduction : …');
  assert.ok(/<blockquote dir="rtl">/.test(html));
  assert.ok(!html.includes('&gt; אסור'));
});

test('L — un lien Markdown Sefaria devient un <a target="_blank">', () => {
  const html = renderMarkdown('[Choulhan Aroukh HaRav 317:4](https://www.sefaria.org/Shulchan_Arukh_HaRav,_Orach_Chayim.317.4)');
  assert.ok(/<a href="https:\/\/www\.sefaria\.org\/Shulchan_Arukh_HaRav,_Orach_Chayim\.317\.4" target="_blank"/.test(html));
});

test('L — l\'hébreu inline est isolé en RTL, abréviations avec gershayim comprises', () => {
  const html = renderMarkdown('Le terme מוקצה (mouktsé) et l\'abréviation שו״ע.');
  assert.ok(/<span lang="he" dir="rtl"[^>]*>מוקצה<\/span>/.test(html));
  assert.ok(/<span lang="he" dir="rtl"[^>]*>שו״ע<\/span>/.test(html));
});

test('H — le profil n\'est plus obligatoire pour envoyer, et l\'accueil est statique', () => {
  assert.ok(!src.includes("alert('Choisis d\\'abord ton niveau et ton minhag.')"), 'l\'alerte bloquante subsiste');
  assert.ok(/renderLocalWelcome\(\)/.test(src));
  assert.ok(/\|\| 'non précisé'/.test(src));
});

test('UX — la question saisie pendant le choix du profil n\'est plus écrasée par le message d\'introduction', () => {
  assert.ok(!/this\.inputEl\.value = buildIntroMessage\(/.test(src));
  assert.ok(/const draft = this\.inputEl\.value\.trim\(\);\s*\n\s*if \(draft\) \{ this\.send\(\); return; \}/.test(src));
});

test('compteurs — le widget corrige la jauge mensuelle quand `done` la renvoie', () => {
  assert.ok(/typeof parsed\.month_remaining === 'number' && this\.rateInfo/.test(src));
});
