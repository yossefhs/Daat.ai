#!/usr/bin/env node
/**
 * DAAT — SSG des listings de sections
 *
 * Injecte des tuiles <a class="simanim-tile"> STATIQUES dans le HTML des index
 * de section (yoreh-deah, orah-haim, nida ×3 langues + teaser oh-quotidien de
 * sources/shabbat/index*.html), à partir de data/simanim-disponibles.json.
 *
 * Motivation SEO : sans cela le HTML initial ne contient que « Chargement… »
 * et les crawlers (Google, moteurs IA) ne voient aucun lien vers les simanim.
 * Le JS client existant re-rend les mêmes tuiles (même source JSON, mêmes URLs
 * routes) — il reste en place comme rafraîchisseur, le contenu est identique.
 *
 * Idempotent : remplace tout le contenu du conteneur à chaque exécution.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'simanim-disponibles.json'), 'utf8'));

const ROUTE = { 'yoreh-deah': '/yd/', 'nida': '/yd/', 'oh-quotidien': '/oh-quotidien/', 'shabbat': '/oh/' };

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function tilesHTML(sectionKeys, lang) {
  const items = DATA.simanim.filter((s) => sectionKeys.includes(s.section));
  const suffix = lang === 'he' ? 'he' : lang === 'en' ? 'en' : '';
  return items
    .map((s) => {
      const href = (ROUTE[s.section] || '/oh/') + s.num + '/' + suffix;
      const title = lang === 'he' ? (s.titleHe || s.title) : lang === 'en' ? (s.titleEn || s.title) : s.title;
      return [
        `<a class="simanim-tile" href="${href}" title="Siman ${s.num} — ${esc(title)}">`,
        `<span class="simanim-tile-num">${esc(s.numHe)}<span class="siman-num-fr">· ${s.num}</span></span>`,
        `<span class="simanim-tile-title">${esc(title)}</span>`,
        `</a>`,
      ].join('');
    })
    .join('\n      ');
}

function countText(sectionKeys, lang) {
  const total = DATA.simanim.filter((s) => sectionKeys.includes(s.section)).length;
  const d = DATA.meta.lastUpdated;
  if (lang === 'he') return `${total} סימנים זמינים · עודכן ${d}`;
  if (lang === 'en') return `${total} simanim available · updated ${d}`;
  return total > 1 ? `${total} simanim disponibles · mis à jour le ${d}` : `1 siman disponible · mis à jour le ${d}`;
}

/** Remplace le contenu d'un <div id="..."> (non imbriqué de div internes autres que les tuiles/loading). */
function replaceContainer(html, id, inner) {
  const re = new RegExp(`(<div id="${id}"[^>]*>)[\\s\\S]*?(</div>)(\\s*(?:</div>|<script|<p|<h|<!--|<div class="section-header"|$))`);
  // Le conteneur ne contient que des <a> plats ou le loading <div> simple :
  // on matche jusqu'au premier </div> suivi d'un début de bloc frère plausible.
  const simple = new RegExp(`(<div id="${id}"[^>]*>)([\\s\\S]*?)(</div>)`);
  const m = html.match(simple);
  if (!m) return null;
  // Si le contenu actuel contient un <div> interne (loading), il faut avaler son </div> aussi.
  let content = m[2];
  let closing = m[3];
  let full = m[0];
  const openDivs = (content.match(/<div/g) || []).length;
  const closeDivs = (content.match(/<\/div>/g) || []).length;
  if (openDivs > closeDivs) {
    // le </div> matché fermait le div interne — étendre jusqu'au suivant
    const start = html.indexOf(m[0]);
    const rest = html.slice(start + m[0].length);
    const nextClose = rest.indexOf('</div>');
    if (nextClose === -1) return null;
    full = html.slice(start, start + m[0].length + nextClose + '</div>'.length);
  }
  const openTag = m[1].replace(/\s*aria-busy="true"/, '');
  return html.replace(full, `${openTag}\n      ${inner}\n  </div>`);
}

function replaceCounts(html, id, text) {
  const re = new RegExp(`(<p id="${id}"[^>]*>)[^<]*(</p>)`);
  if (!re.test(html)) return null;
  return html.replace(re, `$1${text}$2`);
}

let filesChanged = 0;

// ── 1. Index de sections : yoreh-deah (yd+…), orah-haim (oh-quotidien), nida ──
const SECTION_PAGES = [
  { file: 'sources/yoreh-deah/index{L}.html', sections: ['yoreh-deah'] },
  { file: 'sources/orah-haim/index{L}.html', sections: ['oh-quotidien'] },
  { file: 'sources/nida/index{L}.html', sections: ['nida'] },
];

for (const page of SECTION_PAGES) {
  for (const [suffixFile, lang] of [['', 'fr'], ['-he', 'he'], ['-en', 'en']]) {
    const rel = page.file.replace('{L}', suffixFile);
    const p = path.join(ROOT, rel);
    if (!fs.existsSync(p)) continue;
    let html = fs.readFileSync(p, 'utf8');
    const withTiles = replaceContainer(html, 'yd-section-grid', tilesHTML(page.sections, lang));
    if (!withTiles) { console.warn(`⚠ conteneur yd-section-grid introuvable : ${rel}`); continue; }
    html = withTiles;
    const withCounts = replaceCounts(html, 'yd-section-counts', countText(page.sections, lang));
    if (withCounts) html = withCounts;
    fs.writeFileSync(p, html, 'utf8');
    filesChanged++;
    console.log(`SSG ${rel} : ${DATA.simanim.filter((s) => page.sections.includes(s.section)).length} tuiles (${lang})`);
  }
}

// ── 2. Teaser oh-quotidien dans sources/shabbat/index*.html (#ohq-grid) ──────
const OHQ = DATA.simanim.filter((s) => s.section === 'oh-quotidien');
const ohqMax = OHQ.length ? Math.max(...OHQ.map((s) => s.num)) : 0;
for (const [suffixFile, lang] of [['', 'fr'], ['-he', 'he'], ['-en', 'en']]) {
  const rel = `sources/shabbat/index${suffixFile}.html`;
  const p = path.join(ROOT, rel);
  if (!fs.existsSync(p)) continue;
  let html = fs.readFileSync(p, 'utf8');
  if (!html.includes('id="ohq-grid"')) continue;
  const withTiles = replaceContainer(html, 'ohq-grid', tilesHTML(['oh-quotidien'], lang));
  if (!withTiles) { console.warn(`⚠ conteneur ohq-grid introuvable : ${rel}`); continue; }
  html = withTiles;
  // Compteur + libellé de plage hardcodés
  html = html.replace(/(<div class="section-count" id="ohq-count">)[^<]*(<\/div>)/, `$1${OHQ.length} simanim$2`);
  html = html.replace(/simanim 1 à \d+/, `simanim 1 à ${ohqMax}`);
  html = html.replace(/\(simanim 1-\d+\)/, `(simanim 1-${ohqMax})`);
  fs.writeFileSync(p, html, 'utf8');
  filesChanged++;
  console.log(`SSG ${rel} : teaser oh-quotidien ${OHQ.length} tuiles (${lang})`);
}

console.log(`\n${filesChanged} fichiers mis à jour.`);
