#!/usr/bin/env node
/**
 * DAAT — Générateur d'images Open Graph (SVG 1200×630)
 *
 * Génère une image OG par siman à partir des données JSON dans
 * data/simanim/. Génère aussi og-default.svg pour les pages génériques.
 *
 * Usage :
 *   node scripts/generate-og-image.js          # tous les simanim
 *   node scripts/generate-og-image.js --siman 242
 *   node scripts/generate-og-image.js --default
 *
 * Output : assets/img/og/siman-{N}.svg + assets/img/og/og-default.svg
 *
 * Format : SVG vectoriel (~4 KB). Twitter, LinkedIn, WhatsApp, Slack,
 * Discord acceptent SVG. Facebook préfère PNG/JPG ; pour Facebook on
 * pourra brancher @vercel/og plus tard via une route /api/og?siman=N
 * (rendu serverless à la demande, sans binaire natif).
 *
 * Pure Node — aucune dépendance native, déploiement Vercel safe.
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = resolve(__dirname, '..');
const DATA_DIR = resolve(ROOT, 'data', 'simanim');
const OUT_DIR  = resolve(ROOT, 'assets', 'img', 'og');

if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });

// -- Helpers --
const args = process.argv.slice(2);
const flag = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const has  = (n) => args.includes(n);

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

// -- Couleurs DAAT --
const COLORS = {
  parchment: '#F5F0E8',
  parchmentSoft: '#FBF7EF',
  parchmentDark: '#EDE3CE',
  gold: '#B8972A',
  goldLight: '#D4B255',
  navy: '#1A1F3A',
  text: '#1A1F3A',
  textMid: '#3D4266',
};

// -- Wrap text by character length (rough) --
function wrap(text, maxLen) {
  if (!text) return [''];
  const words = text.split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > maxLen) {
      lines.push(cur.trim());
      cur = w;
    } else {
      cur = (cur + ' ' + w).trim();
    }
  }
  if (cur) lines.push(cur);
  return lines;
}

// -- Render a single OG image --
function renderOG({ titleFr, titleHe, numberLabel, subtitle }) {
  const titleLines = wrap(titleFr, 28).slice(0, 3);
  const subtitleLines = wrap(subtitle || '', 60).slice(0, 2);

  // Le @import des Google Fonts contient des & qui cassent le parsing XML
  // → on l'enveloppe dans CDATA. Les bots OG (Facebook, Twitter, LinkedIn)
  // qui rendent SVG vont l'utiliser. resvg-js n'exécute pas le @import
  // mais sait au moins parser le SVG (et utilise les polices système).
  const fontImport = `<![CDATA[
    @import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&family=Frank+Ruhl+Libre:wght@500;700;900&family=Inter:wght@400;500;600&display=swap");
  ]]>`;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <style>${fontImport}
      .bg          { fill: ${COLORS.parchment}; }
      .border-frame{ fill: none; stroke: ${COLORS.gold}; stroke-width: 4; }
      .border-inner{ fill: none; stroke: ${COLORS.gold}; stroke-width: 1.5; opacity: 0.4; }
      .label       { font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600;
                     letter-spacing: 6px; fill: ${COLORS.gold}; text-transform: uppercase; }
      .title-fr    { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 60px;
                     font-weight: 600; fill: ${COLORS.navy}; }
      .title-he    { font-family: 'Frank Ruhl Libre', serif; font-size: 78px; font-weight: 900;
                     fill: ${COLORS.gold}; direction: rtl; }
      .subtitle    { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 22px;
                     font-style: italic; fill: ${COLORS.textMid}; }
      .number      { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 30px;
                     font-weight: 500; fill: ${COLORS.gold}; letter-spacing: 2px; }
      .brand-he    { font-family: 'Frank Ruhl Libre', serif; font-size: 32px; font-weight: 700;
                     fill: ${COLORS.gold}; }
      .brand-en    { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600;
                     letter-spacing: 4px; fill: ${COLORS.textMid}; text-transform: uppercase; }
      .brand-tag   { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 16px;
                     font-style: italic; fill: ${COLORS.textMid}; }
    </style>

    <!-- Subtle paper grain -->
    <pattern id="grain" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <rect width="40" height="40" fill="${COLORS.parchment}"/>
      <circle cx="3" cy="7"  r="0.6" fill="${COLORS.parchmentDark}" opacity="0.3"/>
      <circle cx="22" cy="18" r="0.4" fill="${COLORS.parchmentDark}" opacity="0.25"/>
      <circle cx="35" cy="32" r="0.5" fill="${COLORS.parchmentDark}" opacity="0.3"/>
      <circle cx="11" cy="28" r="0.3" fill="${COLORS.parchmentDark}" opacity="0.2"/>
    </pattern>

    <!-- Manuscript margin (left) -->
    <linearGradient id="margin" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="${COLORS.parchmentDark}" stop-opacity="0.55"/>
      <stop offset="80%" stop-color="${COLORS.parchmentDark}" stop-opacity="0.0"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect class="bg" x="0" y="0" width="1200" height="630"/>
  <rect x="0" y="0" width="1200" height="630" fill="url(#grain)"/>

  <!-- Manuscript margin -->
  <rect x="0" y="0" width="80" height="630" fill="url(#margin)"/>
  <line x1="80" y1="0" x2="80" y2="630" stroke="${COLORS.gold}" stroke-width="2" opacity="0.6"/>

  <!-- Outer frame -->
  <rect class="border-frame" x="32" y="32" width="1136" height="566" rx="6"/>
  <rect class="border-inner" x="48" y="48" width="1104" height="534" rx="3"/>

  <!-- Top label -->
  <text class="label" x="120" y="110">CHOULHAN AROUKH · ÉTUDE EN FRANÇAIS</text>

  <!-- Hebrew title (sa propre ligne, à droite) -->
  <text class="title-he" x="1140" y="200" text-anchor="end">${esc(titleHe || '')}</text>

  <!-- Number en français + hébreu (sa propre ligne, sous le label, plus discret) -->
  ${numberLabel ? `<text class="number" x="120" y="160">${esc(numberLabel)}</text>` : ''}

  <!-- Title FR (multi-line) — décalé vers le bas pour aérer -->
  ${titleLines.map((line, i) => `<text class="title-fr" x="120" y="${290 + i * 74}">${esc(line)}</text>`).join('\n  ')}

  <!-- Subtitle (multi-line) -->
  ${subtitleLines.map((line, i) => `<text class="subtitle" x="120" y="${475 + i * 30}">${esc(line)}</text>`).join('\n  ')}

  <!-- Footer brand -->
  <line x1="120" y1="535" x2="1080" y2="535" stroke="${COLORS.gold}" stroke-width="1" opacity="0.4"/>
  <text class="brand-he" x="120" y="575">דעת</text>
  <text class="brand-en" x="180" y="572">DAAT</text>
  <text class="brand-tag" x="1080" y="575" text-anchor="end">daattorah.com</text>
</svg>
`;
}

// -- Render a default OG (no specific siman) --
function renderDefault() {
  return renderOG({
    numberLabel: 'דעת התורה לעומקה',
    titleFr: "L'étude halakhique en français",
    titleHe: 'דעת',
    subtitle: 'Choulhan Aroukh par siman, en 3 niveaux — Base, Lamdan, Synthèse',
  });
}

// -- Process simanim --
function getSimanFiles() {
  return readdirSync(DATA_DIR)
    .filter(f => /^siman-\d+\.json$/.test(f))
    .map(f => resolve(DATA_DIR, f));
}

function generateForSiman(filepath) {
  const data = JSON.parse(readFileSync(filepath, 'utf8'));
  const svg = renderOG({
    numberLabel: `Siman ${data.number} · ${data.numberHe}`,
    titleFr: data.titleFr,
    titleHe: data.titleHe,
    subtitle: data.subtitle || data.description?.slice(0, 100),
  });
  const svgPath = join(OUT_DIR, `siman-${data.number}.svg`);
  writeFileSync(svgPath, svg, 'utf8');
  console.log(`✓ ${svgPath} (${(svg.length / 1024).toFixed(1)} KB)`);
}

// -- Main --
const onlySiman = flag('--siman');
const onlyDefault = has('--default');

function writeDefault() {
  const svg = renderDefault();
  const svgPath = join(OUT_DIR, 'og-default.svg');
  writeFileSync(svgPath, svg, 'utf8');
  console.log(`✓ ${svgPath}`);
}

if (onlyDefault) {
  writeDefault();
} else if (onlySiman) {
  generateForSiman(join(DATA_DIR, `siman-${onlySiman}.json`));
} else {
  // All simanim + default
  const files = getSimanFiles();
  for (const f of files) generateForSiman(f);
  writeDefault();
  console.log(`\n🎨 ${files.length + 1} images OG SVG générées dans ${OUT_DIR}`);
}
