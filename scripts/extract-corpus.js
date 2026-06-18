#!/usr/bin/env node
// Extracteur du corpus DAAT — scanne tous les simanim disponibles (Hilkhot
// Shabbat / Orah Haïm ET Yoreh De'ah) et génère data/corpus-shabbat.json
// (index BM25-ready pour /api/chat-corpus et le corpus-first de /api/chat).
//
// Chaque chunk porte un champ `section` ('orach-chaim' | 'yoreh-deah') pour que
// la recherche puisse se restreindre à la section de la conversation, et un
// `sourceUrl` pointant vers la bonne route (/oh/N/base ou /yd/N/base).
//
// Chunking par siman :
// - 1 chunk par <div class="definition|remember|key-point">
// - 1 chunk par ligne du tableau "Cas pratiques modernes"
// - 1 chunk par bloc <h3> + paragraphes narratifs
// Métadonnées : siman, section, sectionTitle, subsection, type, simanTitle, sourceUrl

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const META_DIR = path.join(ROOT, 'data', 'simanim');
const OUTPUT_PATH = path.join(ROOT, 'data', 'corpus-shabbat.json');

// Sections scannées. `section` correspond exactement à la valeur utilisée par
// /api/chat (req.body.section) afin que le filtrage soit direct.
const SECTIONS = [
  { id: 'orach-chaim', dir: path.join(ROOT, 'sources', 'shabbat'), urlPrefix: '/oh', useMetaDir: true },
  { id: 'yoreh-deah', dir: path.join(ROOT, 'sources', 'yoreh-deah'), urlPrefix: '/yd', useMetaDir: false },
];

// Cartes de titres pour les sections sans data/simanim/*.json (ex. Yoreh De'ah),
// construites depuis les manifestes simanim-disponibles{,-he}.json déjà maintenus.
function loadDispoMap(file) {
  try {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', file), 'utf8'));
    const m = {};
    for (const s of d.simanim || []) m[`${s.section || 'shabbat'}:${s.num}`] = s;
    return m;
  } catch { return {}; }
}
const DISPO_FR = loadDispoMap('simanim-disponibles.json');
const DISPO_HE = loadDispoMap('simanim-disponibles-he.json');

// Résout titreFr / titreHe / sous-titre d'un siman selon sa section.
function resolveMeta(section, num) {
  if (section.useMetaDir) {
    const metaPath = path.join(META_DIR, `siman-${num}.json`);
    if (fs.existsSync(metaPath)) {
      try {
        const m = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
        return { titleFr: m.titleFr || `Siman ${num}`, titleHe: m.titleHe || '', subtitle: m.subtitle || '' };
      } catch { /* ignore */ }
    }
  }
  const fr = DISPO_FR[`${section.id}:${num}`];
  const he = DISPO_HE[`${section.id}:${num}`];
  return {
    titleFr: (fr && fr.title) || `Siman ${num}`,
    titleHe: (he && he.title) || (fr && fr.numHe) || '',
    subtitle: '',
  };
}

// ── Helpers HTML → texte ───────────────────────────────────────────────────
function decodeEntities(s) {
  return s
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
    .replace(/&laquo;/g, '«').replace(/&raquo;/g, '»').replace(/&hellip;/g, '…')
    .replace(/&mdash;/g, '—').replace(/&ndash;/g, '–');
}

function htmlToText(html) {
  let s = html;
  s = s.replace(/<style[\s\S]*?<\/style>/gi, '');
  s = s.replace(/<script[\s\S]*?<\/script>/gi, '');
  s = s.replace(/<div class="page-break"[^>]*><\/div>/gi, '');
  s = s.replace(/<br\s*\/?>/gi, '\n');
  s = s.replace(/<\/(p|div|li|tr|h[1-6])>/gi, '\n');
  s = s.replace(/<\/td>/gi, ' · ');
  s = s.replace(/<li[^>]*>/gi, '• ');
  s = s.replace(/<[^>]+>/g, '');
  s = decodeEntities(s);
  s = s.replace(/[ \t]+/g, ' ');
  s = s.replace(/\n[ \t]+/g, '\n');
  s = s.replace(/\n{3,}/g, '\n\n');
  return s.trim();
}

// ── Extraction des chunks d'un fichier ─────────────────────────────────────
function extractChunks(siman, html) {
  const chunks = [];
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  const body = bodyMatch ? bodyMatch[1] : html;

  // Tolérant aux attributs supplémentaires (ex. id="…" ajouté pour les ancres).
  const sectionRegex = /<h2 class="section-title"[^>]*>([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2 class="section-title"[^>]*>|$)/g;
  let match;
  let sectionIndex = 0;
  while ((match = sectionRegex.exec(body)) !== null) {
    sectionIndex++;
    const sectionTitle = htmlToText(match[1]);
    const sectionContent = match[2];

    // Skip les sections bruyantes
    if (/Plan de l'étude|Le texte du Choul'han Aroukh|Mishnah Berurah — premières entrées|Questions de compréhension/.test(sectionTitle)) {
      continue;
    }

    // Cas pratiques modernes → 1 chunk par ligne du tableau
    if (/Cas pratiques modernes/i.test(sectionTitle)) {
      const rowRe = /<tr>\s*<td[^>]*><strong>([^<]+)<\/strong><\/td>\s*<td[^>]*>([\s\S]*?)<\/td>\s*<\/tr>/g;
      let row;
      while ((row = rowRe.exec(sectionContent)) !== null) {
        const situation = htmlToText(row[1]);
        const analysis = htmlToText(row[2]);
        const text = situation + ' — ' + analysis;
        if (text.length < 30) continue;
        chunks.push({
          id: `siman-${siman.num}-cas-${chunks.length + 1}`,
          siman: siman.num,
          sectionNum: sectionIndex,
          sectionTitle, subsection: 'Cas pratique : ' + situation,
          text, type: 'cas-pratique',
        });
      }
      continue;
    }

    // Blocs définition/remember/key-point
    const blockRe = /<div class="(definition|remember|key-point)"[^>]*>([\s\S]*?)<\/div>(?=\s*<(?:div class="(?:definition|remember|key-point|page-break)"|h\d|p\b|table\b|hr\b|\/section|\/body))/g;
    let block;
    let blockIdx = 0;
    while ((block = blockRe.exec(sectionContent)) !== null) {
      const text = htmlToText(block[2]);
      if (text.length < 40) continue;
      blockIdx++;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-b${blockIdx}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle, subsection: null,
        text, type: block[1],
      });
    }

    // Paragraphes narratifs (h3 + p)
    const h3Re = /<h3[^>]*>([\s\S]*?)<\/h3>([\s\S]*?)(?=<h3|<h2|$)/g;
    let h3m;
    while ((h3m = h3Re.exec(sectionContent)) !== null) {
      const h3Title = htmlToText(h3m[1]);
      const subClean = h3m[2].replace(/<div class="(definition|remember|key-point)"[^>]*>[\s\S]*?<\/div>/g, '');
      const text = htmlToText(subClean);
      if (text.length < 60) continue;
      chunks.push({
        id: `siman-${siman.num}-s${sectionIndex}-h3-${chunks.length}`,
        siman: siman.num,
        sectionNum: sectionIndex,
        sectionTitle, subsection: h3Title,
        text, type: 'narratif',
      });
    }
  }
  return chunks;
}

// ── Scan de tous les simanim, section par section ──────────────────────────
const allChunks = [];
const stats = { totalSimanim: 0, withChunks: 0, skipped: [], chunksPerSiman: {}, perSection: {} };

for (const section of SECTIONS) {
  if (!fs.existsSync(section.dir)) continue;
  stats.perSection[section.id] = 0;
  const simanDirs = fs.readdirSync(section.dir)
    .filter((d) => /^siman-\d+$/.test(d))
    .sort((a, b) => parseInt(a.slice(6)) - parseInt(b.slice(6)));

  for (const dir of simanDirs) {
    const simanNum = parseInt(dir.slice(6));
    const htmlPath = path.join(section.dir, dir, 'niveau-1-base.html');

    if (!fs.existsSync(htmlPath)) { stats.skipped.push({ section: section.id, num: simanNum, reason: 'pas de niveau-1-base.html' }); continue; }

    stats.totalSimanim++;

    const meta = resolveMeta(section, simanNum);
    const html = fs.readFileSync(htmlPath, 'utf8');
    const chunks = extractChunks({ num: simanNum }, html);

    if (chunks.length === 0) { stats.skipped.push({ section: section.id, num: simanNum, reason: 'aucun chunk extrait' }); continue; }

    chunks.forEach((c) => {
      c.section = section.id;
      c.simanTitle = meta.titleFr;
      c.simanTitleHe = meta.titleHe;
      c.simanSubtitle = meta.subtitle || '';
      c.sourceUrl = `${section.urlPrefix}/${simanNum}/base`;
    });

    stats.withChunks++;
    stats.chunksPerSiman[`${section.id}:${simanNum}`] = chunks.length;
    stats.perSection[section.id] += chunks.length;
    allChunks.push(...chunks);
  }
}

const output = {
  meta: {
    generated: new Date().toISOString(),
    totalSimanim: stats.withChunks,
    totalChunks: allChunks.length,
    skipped: stats.skipped,
    perSection: stats.perSection,
    source: 'sources/{shabbat,yoreh-deah}/siman-*/niveau-1-base.html (routes /oh/N/base et /yd/N/base, champ section par chunk)',
  },
  chunks: allChunks,
};

fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output), 'utf8');
const sizeKb = (fs.statSync(OUTPUT_PATH).size / 1024).toFixed(1);

console.log(`\n✓ Corpus généré : ${OUTPUT_PATH}`);
console.log(`  Simanim avec chunks : ${stats.withChunks}/${stats.totalSimanim}`);
console.log(`  Chunks totaux       : ${allChunks.length}`);
console.log(`  Taille JSON         : ${sizeKb} KB`);
console.log(`  Par section         : ${Object.entries(stats.perSection).map(([k, v]) => `${k}=${v}`).join(', ')}`);
console.log(`  Skipped (${stats.skipped.length})  : ${stats.skipped.map((s) => `${s.section || ''}#${s.num}`).slice(0, 5).join(',')}${stats.skipped.length > 5 ? '...' : ''}`);

// Distribution chunks/siman
const counts = Object.values(stats.chunksPerSiman);
counts.sort((a, b) => a - b);
console.log(`  Chunks/siman p50    : ${counts[Math.floor(counts.length / 2)]}`);
console.log(`  Chunks/siman max    : ${counts[counts.length - 1]} (siman ${Object.keys(stats.chunksPerSiman).find((k) => stats.chunksPerSiman[k] === counts[counts.length - 1])})`);
