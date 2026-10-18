#!/usr/bin/env node
/**
 * DAAT — Mise à jour des balises og:image et twitter:image dans les pages HTML
 *
 * Pour chaque niveau de simanim spécifiés :
 * - Met à jour ou ajoute og:image avec l'URL de l'image PNG par niveau
 * - Met à jour ou ajoute twitter:image avec la même URL
 * - Ajoute twitter:card summary_large_image si absente
 *
 * Usage :
 *   node scripts/update-og-meta.js 299 301
 */

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const SOURCES = resolve(ROOT, 'sources', 'shabbat');

const args = process.argv.slice(2);
const simanim = args.filter(a => /^\d+$/.test(a)).map(Number);

if (simanim.length === 0) {
  console.error('Usage: node scripts/update-og-meta.js 299 301');
  process.exit(1);
}

// Map suffixes to level pages
const LEVELS = [
  { file: 'index', suffix: '' },
  { file: 'niveau-1-base', suffix: '-base' },
  { file: 'niveau-2-lamdan', suffix: '-lamdan' },
  { file: 'niveau-3-synthese', suffix: '-synthese' },
  { file: 'niveau-4-daat-harav', suffix: '-daat-harav' },
];

const LANGS = ['', '-he', '-en'];

function updateMeta(html, simanNum, level) {
  const imageUrl = `https://daattorah.com/assets/img/og/siman-${simanNum}${level.suffix}.png`;
  
  // Ajouter ou remplacer og:image
  if (html.includes('property="og:image"')) {
    html = html.replace(
      /<meta\s+property="og:image"\s+content="[^"]*"\s*\/?>/gi,
      `<meta property="og:image" content="${imageUrl}">`
    );
  } else {
    // Insérer après og:url
    html = html.replace(
      /(<meta\s+property="og:url"[^>]*>)/i,
      `$1\n  <meta property="og:image" content="${imageUrl}">`
    );
  }
  
  // Ajouter ou remplacer twitter:image
  if (html.includes('name="twitter:image"')) {
    html = html.replace(
      /<meta\s+name="twitter:image"\s+content="[^"]*"\s*\/?>/gi,
      `<meta name="twitter:image" content="${imageUrl}">`
    );
  } else {
    // Insérer après og:image
    html = html.replace(
      /(<meta\s+property="og:image"[^>]*>)/i,
      `$1\n  <meta name="twitter:image" content="${imageUrl}">`
    );
  }
  
  // Ajouter twitter:card si absent
  if (!html.includes('name="twitter:card"')) {
    html = html.replace(
      /(<meta\s+name="twitter:image"[^>]*>)/i,
      `<meta name="twitter:card" content="summary_large_image">\n  $1`
    );
  }
  
  return html;
}

let totalUpdated = 0;

for (const simanNum of simanim) {
  const simanDir = join(SOURCES, `siman-${simanNum}`);
  
  for (const level of LEVELS) {
    for (const lang of LANGS) {
      const filepath = join(simanDir, `${level.file}${lang}.html`);
      try {
        let html = readFileSync(filepath, 'utf8');
        html = updateMeta(html, simanNum, level);
        writeFileSync(filepath, html, 'utf8');
        console.log(`✓ ${level.file}${lang}.html (siman ${simanNum})`);
        totalUpdated++;
      } catch (err) {
        // Fichier absent, on continue
      }
    }
  }
}

console.log(`\n✅ ${totalUpdated} fichiers mis à jour`);
