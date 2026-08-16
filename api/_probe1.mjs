import { tokenize } from './_probe_after.mjs';
import * as A from './_probe_after.mjs';
const SYN = A.__SYN, CANON = A.__CANON, norm = A.__norm, expand = A.__expand;
console.log('tokenize("kidouch") =', tokenize('kidouch'));
console.log('tokenize("kiddoush") =', tokenize('kiddoush'));
console.log('SYNONYMS has kidouch?', Object.prototype.hasOwnProperty.call(SYN,'kidouch'));
console.log('SYNONYMS has kiddoush?', Object.prototype.hasOwnProperty.call(SYN,'kiddoush'));
console.log('expandQuery(["kidouch"]) =', [...expand(['kidouch'])]);
console.log('expandQuery(tokenize("kidouch")) =', [...expand(tokenize('kidouch'))]);
console.log('---- all SYNONYMS keys that normalizeToken rewrites ----');
let n=0;
for (const k of Object.keys(SYN)) { const nk = norm(k); if (nk !== k) { n++; console.log('  KEY', JSON.stringify(k), '->', JSON.stringify(nk), '| target key exists in SYNONYMS?', Object.prototype.hasOwnProperty.call(SYN,nk)); } }
console.log('  total rewritten SYNONYMS keys:', n);
console.log('---- other tables ----');
for (const [name, set] of [['DOMAIN_ANCHORS',A.__ANCH],['SHABBAT_MARKERS',A.__MARK],['NON_TOPICAL',A.__NONTOP],['STOPWORDS',A.__STOP]]) {
  const bad=[...set].filter(k=>norm(k)!==k);
  console.log(' ', name, 'entries rewritten by normalizeToken:', bad.length, bad.slice(0,10));
}
let cr=0; const crbad=[];
for (const r of A.__CR) for (const f of ['any','ctx','add']) for (const w of r[f]) if (norm(w)!==w) { cr++; crbad.push(f+':'+w+'->'+norm(w)); }
console.log('  CONCEPT_RULES rewritten:', cr, crbad.slice(0,10));
let sv=0; const svbad=[];
for (const k of Object.keys(SYN)) for (const v of SYN[k]) if (norm(v)!==v) { sv++; svbad.push(k+':'+v+'->'+norm(v)); }
console.log('  SYNONYMS VALUES rewritten:', sv, svbad.slice(0,20));
