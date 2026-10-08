#!/usr/bin/env node
/**
 * Met à jour les meta tags og:image et twitter:image dans les fichiers HTML
 * pour pointer vers les images par niveau
 */

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(__dirname, '..');

const args = process.argv.slice(2);
const simanim = args.filter(arg => /^\d+$/.test(arg)).map(Number);

if (simanim.length === 0) {
  console.error('Usage: node update-og-meta.js 299 301');
  process.exit(1);
}

const levelMap = {
  'niveau-1-base': 'base',
  'niveau-2-lamdan': 'lamdan',
  'niveau-3-synthese': 'synthese',
  'niveau-4-daat-harav': 'daat-harav',
  'index': '',
};

function updateMetaTags(filepath, simanNum, level) {
  let content = readFileSync(filepath, 'utf8');
  
  const suffix = level ? `-${level}` : '';
  const newImage = `https://daattorah.com/assets/img/og/siman-${simanNum}${suffix}.png`;
  
  // Remplacer og:image
  content = content.replace(
    /(property="og:image" content=")https:\/\/daattorah\.com\/assets\/img\/og\/siman-\d+\.png(")/g,
    `$1${newImage}$2`
  );
  
  // Remplacer twitter:image (ou l'ajouter si absent)
  if (content.includes('name="twitter:image"')) {
    content = content.replace(
      /(name="twitter:image" content=")https:\/\/daattorah\.com\/assets\/img\/og\/siman-\d+\.png(")/g,
      `$1${newImage}$2`
    );
  } else {
    // Ajouter twitter:image après og:image
    content = content.replace(
      /(<meta property="og:image" content="[^"]+">)/,
      `$1\n<meta name="twitter:image" content="${newImage}">`
    );
  }
  
  writeFileSync(filepath, content, 'utf8');
  return newImage;
}

for (const siman of simanim) {
  const simanDir = resolve(ROOT, 'sources', 'shabbat', `siman-${siman}`);
  const files = readdirSync(simanDir).filter(f => f.endsWith('.html'));
  
  console.log(`\nSiman ${siman}:`);
  
  for (const file of files) {
    const filepath = join(simanDir, file);
    const stem = file.replace(/(-en|-he)?\.html$/, '');
    const level = levelMap[stem];
    
    if (level !== undefined) {
      const newImage = updateMetaTags(filepath, siman, level);
      console.log(`  ✓ ${file} → ${basename(newImage)}`);
    }
  }
}

console.log('\n✨ Mise à jour terminée');
