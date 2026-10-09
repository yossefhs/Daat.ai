#!/usr/bin/env node
/**
 * Ajoute og:image et twitter:card aux pages /limoud/
 */

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = fileURLToPath(new URL('.', import.meta.url));
const ROOT = resolve(__dirname, '..');
const LIMOUD_DIR = join(ROOT, 'limoud');

const defaultImage = 'https://daattorah.com/assets/img/og/og-default.png';

function updateLimoudPage(filepath) {
  let content = readFileSync(filepath, 'utf8');
  let modified = false;
  
  // Ajouter og:image si absent
  if (!content.includes('property="og:image"')) {
    // Trouver og:url et insérer juste après
    if (content.includes('property="og:url"')) {
      content = content.replace(
        /(<meta property="og:url" content="[^"]+">)/,
        `$1\n  <meta property="og:image" content="${defaultImage}">`
      );
      modified = true;
    } else {
      // Sinon, ajouter après og:description
      content = content.replace(
        /(<meta property="og:description" content="[^"]+">)/,
        `$1\n  <meta property="og:image" content="${defaultImage}">`
      );
      modified = true;
    }
  }
  
  // Ajouter twitter:card si absent
  if (!content.includes('name="twitter:card"')) {
    // Ajouter après og:image
    content = content.replace(
      /(<meta property="og:image" content="[^"]+">)/,
      `$1\n  <meta name="twitter:card" content="summary_large_image">`
    );
    modified = true;
  }
  
  // Ajouter twitter:image si absent
  if (!content.includes('name="twitter:image"')) {
    // Ajouter après twitter:card
    content = content.replace(
      /(<meta name="twitter:card" content="[^"]+">)/,
      `$1\n  <meta name="twitter:image" content="${defaultImage}">`
    );
    modified = true;
  }
  
  if (modified) {
    writeFileSync(filepath, content, 'utf8');
  }
  
  return modified;
}

// Traiter index
const indexFiles = ['index.html', 'index-en.html', 'index-he.html'];
console.log('Pages index /limoud/ :');
for (const file of indexFiles) {
  const filepath = join(LIMOUD_DIR, file);
  const modified = updateLimoudPage(filepath);
  console.log(`  ${modified ? '✓' : '·'} ${file}`);
}

// Traiter toutes les pages jour-XXX.html
console.log('\nPages jour-XXX.html :');
const jourFiles = readdirSync(LIMOUD_DIR).filter(f => /^jour-\d+\.html$/.test(f));
let updated = 0;
for (const file of jourFiles) {
  const filepath = join(LIMOUD_DIR, file);
  const modified = updateLimoudPage(filepath);
  if (modified) updated++;
}
console.log(`  ✓ ${updated} pages mises à jour`);

// Traiter toutes les pages jour-XXX-en.html et jour-XXX-he.html
console.log('\nPages jour-XXX-{en,he}.html :');
const jourTransFiles = readdirSync(LIMOUD_DIR).filter(f => /^jour-\d+-(en|he)\.html$/.test(f));
updated = 0;
for (const file of jourTransFiles) {
  const filepath = join(LIMOUD_DIR, file);
  const modified = updateLimoudPage(filepath);
  if (modified) updated++;
}
console.log(`  ✓ ${updated} pages mises à jour`);

console.log('\n✨ Mise à jour terminée');
