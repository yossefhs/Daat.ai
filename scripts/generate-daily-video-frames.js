#!/usr/bin/env node
/**
 * generate-daily-video-frames.js — frames verticales (1080×1920) du Daat Yomi du jour.
 *
 * Cœur créatif du contenu vidéo quotidien : produit des slides de marque (Navy/Or/
 * crème, דעת) à partir de l'entrée du jour (api/_daily-limoud.js). Ces frames sont
 * ensuite assemblées en MP4 par l'API de rendu (cf. api/_daily-video.js).
 *
 * Dépendance : @resvg/resvg-js (déjà devDependency, comme generate-og-image.js).
 *
 *   node scripts/generate-daily-video-frames.js [YYYY-MM-DD] [outDir]
 */
import { Resvg } from '@resvg/resvg-js';
import { writeFileSync, mkdirSync } from 'node:fs';
import { loadPlan, getEntryForDate } from '../api/_daily-limoud.js';

const NAVY = '#1A1F3A', GOLD = '#C5A55A', CREME = '#FAF6EE', NAVY2 = '#0E1230';
const W = 1080, H = 1920;

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Découpe un texte en lignes d'au plus maxChars caractères (sur les espaces). */
function wrap(text, maxChars) {
  const words = String(text).split(/\s+/);
  const lines = [];
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length > maxChars && cur) { lines.push(cur); cur = w; }
    else cur = (cur + ' ' + w).trim();
  }
  if (cur) lines.push(cur);
  return lines;
}

function tspans(lines, x, y, lh) {
  return lines.map((l, i) => `<tspan x="${x}" y="${y + i * lh}">${esc(l)}</tspan>`).join('');
}

const FONT = "'Frank Ruhl Libre','Arial Hebrew',serif";

function frame({ kicker, he, title, lines, cta }) {
  const titleLines = title ? wrap(title, 22) : [];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}">
  <defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="${NAVY}"/><stop offset="1" stop-color="${NAVY2}"/>
  </linearGradient></defs>
  <rect width="${W}" height="${H}" fill="url(#bg)"/>
  <rect x="40" y="40" width="${W - 80}" height="${H - 80}" rx="32" fill="none" stroke="${GOLD}" stroke-width="3" opacity="0.55"/>
  <text x="${W / 2}" y="200" text-anchor="middle" font-family="${FONT}" font-size="120" font-weight="700" fill="${GOLD}">דעת</text>
  <text x="${W / 2}" y="270" text-anchor="middle" font-family="Inter,sans-serif" font-size="34" letter-spacing="6" fill="${CREME}" opacity="0.85">DAAT · DAAT YOMI</text>
  ${kicker ? `<text x="${W / 2}" y="560" text-anchor="middle" font-family="Inter,sans-serif" font-size="42" letter-spacing="3" fill="${GOLD}">${esc(kicker)}</text>` : ''}
  ${he ? `<text x="${W / 2}" y="760" text-anchor="middle" font-family="${FONT}" font-size="150" font-weight="700" fill="${CREME}">${esc(he)}</text>` : ''}
  ${titleLines.length ? `<text text-anchor="middle" font-family="Cormorant Garamond,serif" font-size="64" fill="${CREME}">${tspans(titleLines, W / 2, 980, 84)}</text>` : ''}
  ${lines && lines.length ? `<text text-anchor="middle" font-family="Inter,sans-serif" font-size="46" fill="${GOLD}">${tspans(lines, W / 2, 1480, 70)}</text>` : ''}
  ${cta ? `<text x="${W / 2}" y="${H - 130}" text-anchor="middle" font-family="Inter,sans-serif" font-size="40" font-weight="600" fill="${CREME}">${esc(cta)}</text>` : ''}
</svg>`;
}

/** Construit le storyboard (liste de frames) pour une entrée Daat Yomi (FR). */
export function buildFrames(entry) {
  const s = entry.siman;
  const seif = `Séifim ${entry.seifRange[0]}–${entry.seifRange[1]}`;
  const lot = entry.lotTotal > 1 ? ` (partie ${entry.lotIndex}/${entry.lotTotal})` : '';
  return [
    { kicker: `JOUR ${entry.dayNumber} · ${entry.date}`, he: 'דעת יומי',
      lines: ['Le limoud du jour', 'Hilkhot Shabbat'] },
    { kicker: `SIMAN ${s.num}`, he: s.numHe, title: s.title },
    { kicker: seif + lot, title: s.title, lines: ['5 séifim/jour · dim → jeu'] },
    { kicker: 'À étudier maintenant', he: 'דעת',
      title: `Choulhan Aroukh · Siman ${s.num}`, cta: `daattorah.com/oh/${s.num}` },
  ];
}

function svgToPng(svg) {
  return new Resvg(svg, { fitTo: { mode: 'width', value: W } }).render().asPng();
}

function main() {
  const date = process.argv[2] || new Date().toISOString().slice(0, 10);
  const outDir = process.argv[3] || `/tmp/daat-yomi-${date}`;
  loadPlan();
  const entry = getEntryForDate(date);
  if (!entry) { console.error(`Aucune entrée Daat Yomi pour ${date} (dim–jeu uniquement).`); process.exit(1); }
  mkdirSync(outDir, { recursive: true });
  const frames = buildFrames(entry);
  frames.forEach((f, i) => {
    writeFileSync(`${outDir}/frame-${i + 1}.png`, svgToPng(frame(f)));
  });
  console.log(`✓ ${frames.length} frames → ${outDir} (Jour ${entry.dayNumber}, Siman ${entry.siman.num})`);
}

if (import.meta.url === `file://${process.argv[1]}`) main();
