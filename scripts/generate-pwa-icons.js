#!/usr/bin/env node
/**
 * generate-pwa-icons.js — génère les icônes de l'application installable (PWA).
 *
 * Sortie :
 *   icons/icon-192.png · icons/icon-512.png            (purpose "any")
 *   icons/icon-maskable-192.png · icons/icon-maskable-512.png  (purpose "maskable", marge de sécurité)
 *   apple-touch-icon.png (180×180, fond plein pour iOS)
 *
 * Dépendance : sharp (non listé dans package.json — `npm install sharp --no-save`).
 * Les PNG produits sont committés comme assets statiques ; ce script n'est pas
 * dans le pipeline de build Vercel (cf. convert-og-png.js / generate-og-image.js).
 *
 * Identité visuelle : Navy #1A1F3A · Or #C5A55A · Crème #EEE6D6 — דעת en hébreu.
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const ICONS_DIR = path.join(ROOT, 'icons');

// Icône "any" : contenu large, fond plein navy (coins arrondis par l'OS).
const SVG_ANY = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#1A1F3A"/>
  <circle cx="256" cy="256" r="228" fill="none" stroke="#EEE6D6" stroke-width="18"/>
  <text x="256" y="324" font-family="'Arial Hebrew','David','Frank Ruhl Libre',serif" font-size="184" font-weight="700" text-anchor="middle" fill="#C5A55A">דעת</text>
</svg>`;

// Icône "maskable" : contenu dans la zone de sécurité (~62 %), plein navy en débord.
const SVG_MASKABLE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#1A1F3A"/>
  <circle cx="256" cy="256" r="150" fill="none" stroke="#EEE6D6" stroke-width="13"/>
  <text x="256" y="301" font-family="'Arial Hebrew','David','Frank Ruhl Libre',serif" font-size="122" font-weight="700" text-anchor="middle" fill="#C5A55A">דעת</text>
</svg>`;

async function render(svg, size, outFile) {
  await sharp(Buffer.from(svg), { density: 600 })
    .resize(size, size)
    .png()
    .toFile(outFile);
  console.log('✓', path.relative(ROOT, outFile));
}

(async () => {
  fs.mkdirSync(ICONS_DIR, { recursive: true });
  await render(SVG_ANY, 192, path.join(ICONS_DIR, 'icon-192.png'));
  await render(SVG_ANY, 512, path.join(ICONS_DIR, 'icon-512.png'));
  await render(SVG_MASKABLE, 192, path.join(ICONS_DIR, 'icon-maskable-192.png'));
  await render(SVG_MASKABLE, 512, path.join(ICONS_DIR, 'icon-maskable-512.png'));
  await render(SVG_ANY, 180, path.join(ROOT, 'apple-touch-icon.png'));
  console.log('PWA icons générées.');
})().catch((e) => { console.error(e); process.exit(1); });
