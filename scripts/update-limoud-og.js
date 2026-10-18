#!/usr/bin/env node
/**
 * DAAT — Mise à jour des balises og:image et twitter:image dans les pages /limoud/
 *
 * Met à jour toutes les pages limoud/ (index et jour-*.html) en FR, EN, HE :
 * - og:image et twitter:image vers og-default.png
 * - Ajoute twitter:card summary_large_image si absent
 *
 * Usage :
 *   node scripts/update-limoud-og.js
 */

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const LIMOUD_DIR = resolve(ROOT, 'limoud');

const IMAGE_URL = 'https://daattorah.com/assets/img/og/og-default.png';

function updateMeta(html) {
  // Ajouter ou remplacer og:image
  if (html.includes('property="og:image"')) {
    html = html.replace(
      /<meta\s+property="og:image"\s+content="[^"]*"\s*\/?>/gi,
      `<meta property="og:image" content="${IMAGE_URL}">`
    );
  } else {
    // Insérer après og:url
    html = html.replace(
      /(<meta\s+property="og:url"[^>]*>)/i,
      `$1\n  <meta property="og:image" content="${IMAGE_URL}">`
    );
  }
  
  // Ajouter ou remplacer twitter:image
  if (html.includes('name="twitter:image"')) {
    html = html.replace(
      /<meta\s+name="twitter:image"\s+content="[^"]*"\s*\/?>/gi,
      `<meta name="twitter:image" content="${IMAGE_URL}">`
    );
  } else {
    // Insérer après og:image
    html = html.replace(
      /(<meta\s+property="og:image"[^>]*>)/i,
      `$1\n  <meta name="twitter:image" content="${IMAGE_URL}">`
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

// Patterns: index.html, index-he.html, index-en.html, jour-*.html
const files = readdirSync(LIMOUD_DIR).filter(f => 
  f === 'index.html' || 
  f === 'index-he.html' || 
  f === 'index-en.html' || 
  /^jour-\d+(-he|-en)?\.html$/.test(f)
);

for (const file of files) {
  const filepath = join(LIMOUD_DIR, file);
  try {
    let html = readFileSync(filepath, 'utf8');
    html = updateMeta(html);
    writeFileSync(filepath, html, 'utf8');
    console.log(`✓ ${file}`);
    totalUpdated++;
  } catch (err) {
    console.error(`✗ ${file}: ${err.message}`);
  }
}

console.log(`\n✅ ${totalUpdated} fichiers limoud/ mis à jour`);
