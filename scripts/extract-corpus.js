#!/usr/bin/env node
// Extracteur du corpus DAAT — scanne tous les simanim Shabbat disponibles
// et génère data/corpus-shabbat.json (index BM25-ready pour /api/chat-corpus).
//
// Chunking par siman :
// - 1 chunk par <div class="definition|remember|key-point">
// - 1 chunk par ligne du tableau "Cas pratiques modernes"
// - 1 chunk par bloc <h3> + paragraphes narratifs
// Métadonnées : siman, sectionTitle, subsection, type, simanTitle, sourceUrl

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const SOURCES_DIR = path.join(ROOT, 'sources', 'shabbat');
const META_DIR = path.join(ROOT, 'data', 'simanim');
const OUTPUT_PATH = path.join(ROOT, 'data', 'corpus-shabbat.json');

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

  const sectionRegex = /<h2 class="section-title">([\s\S]*?)<\/h2>([\s\S]*?)(?=<h2 class="section-title">|$)/g;
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
    const h3Re = /<h3>([\s\S]*?)<\/h3>([\s\S]*?)(?=<h3|<h2|$)/g;
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

// ── Scan de tous les simanim ───────────────────────────────────────────────
const simanDirs = fs.readdirSync(SOURCES_DIR)
  .filter((d) => /^siman-\d+$/.test(d))
  .sort((a, b) => parseInt(a.slice(6)) - parseInt(b.slice(6)));

const allChunks = [];
const stats = { totalSimanim: 0, withChunks: 0, skipped: [], chunksPerSiman: {} };

for (const dir of simanDirs) {
  const simanNum = parseInt(dir.slice(6));
  const htmlPath = path.join(SOURCES_DIR, dir, 'niveau-1-base.html');
  const metaPath = path.join(META_DIR, `${dir}.json`);

  if (!fs.existsSync(htmlPath)) { stats.skipped.push({ num: simanNum, reason: 'pas de niveau-1-base.html' }); continue; }

  stats.totalSimanim++;

  let meta = { titleFr: `Siman ${simanNum}`, titleHe: '' };
  if (fs.existsSync(metaPath)) {
    try {
      const m = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
      meta = { titleFr: m.titleFr || meta.titleFr, titleHe: m.titleHe || '', subtitle: m.subtitle || '' };
    } catch (e) { /* ignore */ }
  }

  const html = fs.readFileSync(htmlPath, 'utf8');
  const chunks = extractChunks({ num: simanNum }, html);

  if (chunks.length === 0) { stats.skipped.push({ num: simanNum, reason: 'aucun chunk extrait' }); continue; }

  chunks.forEach((c) => {
    c.simanTitle = meta.titleFr;
    c.simanTitleHe = meta.titleHe;
    c.simanSubtitle = meta.subtitle || '';
    c.sourceUrl = `/oh/${simanNum}/base`;
  });

  stats.withChunks++;
  stats.chunksPerSiman[simanNum] = chunks.length;
  allChunks.push(...chunks);
}

const output = {
  meta: {
    generated: new Date().toISOString(),
    totalSimanim: stats.withChunks,
    totalChunks: allChunks.length,
    skipped: stats.skipped,
    source: 'sources/shabbat/siman-*/niveau-1-base.html (canonical /oh/N/base)',
  },
  chunks: allChunks,
};

fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output), 'utf8');
const sizeKb = (fs.statSync(OUTPUT_PATH).size / 1024).toFixed(1);

console.log(`\n✓ Corpus généré : ${OUTPUT_PATH}`);
console.log(`  Simanim avec chunks : ${stats.withChunks}/${stats.totalSimanim}`);
console.log(`  Chunks totaux       : ${allChunks.length}`);
console.log(`  Taille JSON         : ${sizeKb} KB`);
console.log(`  Skipped (${stats.skipped.length})  : ${stats.skipped.map((s) => s.num).slice(0, 5).join(',')}${stats.skipped.length > 5 ? '...' : ''}`);

// Distribution chunks/siman
const counts = Object.values(stats.chunksPerSiman);
counts.sort((a, b) => a - b);
console.log(`  Chunks/siman p50    : ${counts[Math.floor(counts.length / 2)]}`);
console.log(`  Chunks/siman max    : ${counts[counts.length - 1]} (siman ${Object.keys(stats.chunksPerSiman).find((k) => stats.chunksPerSiman[k] === counts[counts.length - 1])})`);
