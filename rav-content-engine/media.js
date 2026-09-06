import fs from 'node:fs/promises';
import path from 'node:path';
import { presentationOfRavText } from './core.js';

export const MEDIA_STATE = Object.freeze({
  DRAFT: 'DRAFT',
  APPROVED: 'APPROVED',
  MEDIA_READY: 'MEDIA_READY',
  READY_TO_SCHEDULE: 'READY_TO_SCHEDULE',
  MEDIA_FAILED_LAYOUT: 'MEDIA_FAILED_LAYOUT',
  SCHEDULED: 'SCHEDULED',
  PUBLISHED: 'PUBLISHED',
  FAILED: 'FAILED',
});

const COLORS = Object.freeze({ navy: '#10182E', cream: '#FAF6EE', gold: '#B18B43', muted: '#596070' });
const SERIF = "Georgia, 'Times New Roman', serif";
const SANS = "Arial, Helvetica, sans-serif";
const DEFAULT_FOOTER = 'Dayan-Rav Mikhaël Chlomo Abichid';

export class MediaLayoutError extends Error {
  constructor(message) {
    super(message);
    this.name = 'MediaLayoutError';
    this.code = MEDIA_STATE.MEDIA_FAILED_LAYOUT;
  }
}

export function subtitleText(candidate) { return candidate.validated_transcript || candidate.rav_clean_text || ''; }
export function buildSrt(candidate) { const text = subtitleText(candidate).trim(); if (!text) throw new Error('VALIDATED_TRANSCRIPT_REQUIRED'); const end = Math.max(1, Number(candidate.audio_end || 60)); const chunks = text.match(/[^.!?]+[.!?]?/g) || [text]; return chunks.map((chunk, i) => `${i + 1}\n00:00:${String(Math.min(end - 1, i * 4)).padStart(2, '0')},000 --> 00:00:${String(Math.min(end, (i + 1) * 4)).padStart(2, '0')},000\n${chunk.trim()}\n`).join('\n'); }
export function mediaEligible(candidate) { return candidate?.editorial_status === 'APPROVED' && candidate?.reliability_level !== 'RED'; }
export function assetText(candidate) { return candidate.quote_verified ? { label: 'CITATION DU JOUR', body: `« ${candidate.rav_exact_text} »` } : { label: 'ENSEIGNEMENT DU JOUR', body: presentationOfRavText(candidate) }; }
export function mediaDirectoryName(candidate) {
  const topic = candidate.topic.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || 'enseignement';
  return `${topic}-${candidate.candidate_public_id}`;
}

const cleanText = (value) => String(value || '').replace(/\s+/g, ' ').trim();
const esc = (value) => String(value || '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[character]));

function glyphWidthEm(character) {
  if (/\s/.test(character)) return 0.34;
  if (/[ilI1|.,:;!'`]/.test(character)) return 0.31;
  if (/[mwMW@%&]/.test(character)) return 0.92;
  if (/[A-ZÀ-Ý]/.test(character)) return 0.72;
  if (/[0-9]/.test(character)) return 0.60;
  return 0.59;
}

export function measureTextWidth(text, fontSize) {
  return [...String(text || '')].reduce((width, character) => width + glyphWidthEm(character), 0) * Number(fontSize) * 1.035;
}

function breakWord(word, maxWidth, fontSize) {
  const parts = []; let current = '';
  for (const character of word) {
    const next = `${current}${character}`;
    if (current && measureTextWidth(next, fontSize) > maxWidth) { parts.push(current); current = character; } else current = next;
  }
  if (current) parts.push(current);
  return parts;
}

export function wrapTextByWidth(text, { maxWidth, fontSize }) {
  const paragraphs = String(text || '').split(/\n+/); const lines = [];
  for (const paragraph of paragraphs) {
    const words = cleanText(paragraph).split(' ').filter(Boolean); let line = '';
    for (const word of words) {
      const pieces = measureTextWidth(word, fontSize) > maxWidth ? breakWord(word, maxWidth, fontSize) : [word];
      for (const piece of pieces) {
        const next = line ? `${line} ${piece}` : piece;
        if (line && measureTextWidth(next, fontSize) > maxWidth) { lines.push(line); line = piece; } else line = next;
      }
    }
    if (line) lines.push(line);
  }
  return lines;
}

function ellipsize(line, maxWidth, fontSize) {
  const ellipsis = '…'; let result = cleanText(line);
  while (result && measureTextWidth(`${result}${ellipsis}`, fontSize) > maxWidth) result = result.slice(0, -1).trimEnd();
  return result ? `${result}${ellipsis}` : ellipsis;
}

export function truncateTextToFit(text, { maxWidth, fontSize, maxLines }) {
  const wrapped = wrapTextByWidth(text, { maxWidth, fontSize });
  if (wrapped.length <= maxLines) return { lines: wrapped, truncated: false };
  const lines = wrapped.slice(0, maxLines);
  lines[maxLines - 1] = ellipsize(lines[maxLines - 1], maxWidth, fontSize);
  return { lines, truncated: true };
}

export function measureTextBlock(lines, { fontSize, lineHeight = 1.2 }) {
  return { width: Math.max(0, ...lines.map((line) => measureTextWidth(line, fontSize))), height: lines.length * fontSize * lineHeight };
}

export function fitTextInBox(text, { width, height, maxFontSize, minFontSize, lineHeight = 1.2, maxLines = Infinity }) {
  const normalized = cleanText(text);
  if (!normalized) return { lines: [], fontSize: maxFontSize, lineHeight, truncated: false, width: 0, height: 0 };
  for (let fontSize = maxFontSize; fontSize >= minFontSize; fontSize -= 2) {
    const allowedLines = Math.max(1, Math.min(maxLines, Math.floor(height / (fontSize * lineHeight))));
    const wrapped = wrapTextByWidth(normalized, { maxWidth: width, fontSize });
    if (wrapped.length <= allowedLines) return { lines: wrapped, fontSize, lineHeight, truncated: false, ...measureTextBlock(wrapped, { fontSize, lineHeight }) };
  }
  const fontSize = minFontSize; const allowedLines = Math.max(1, Math.min(maxLines, Math.floor(height / (fontSize * lineHeight))));
  const fitted = truncateTextToFit(normalized, { maxWidth: width, fontSize, maxLines: allowedLines });
  return { ...fitted, fontSize, lineHeight, ...measureTextBlock(fitted.lines, { fontSize, lineHeight }) };
}

function textBlock(name, text, box, typography) {
  const fitted = fitTextInBox(text, { width: box.width, height: box.height, ...typography });
  return { name, text: cleanText(text), ...box, ...fitted, required: Boolean(cleanText(text)), fill: typography.fill || COLORS.navy, family: typography.family || SERIF, weight: typography.weight || 'normal' };
}

function layoutFor(kind, width, height) {
  const common = {
    label: { x: 90, y: 92, width: width - 180, height: 58 },
    footer: { x: 90, y: height - 132, width: width - 180, height: 45 },
  };
  const layouts = {
    'reel-cover': { ...common, title: { x: 90, y: 190, width: width - 180, height: 650 }, body: null, cta: { x: 90, y: 1180, width: width - 180, height: 160 } },
    'story-teaser': { ...common, title: { x: 90, y: 190, width: width - 180, height: 700 }, body: null, cta: { x: 90, y: 1210, width: width - 180, height: 160 } },
    'story-answer': { ...common, title: { x: 90, y: 190, width: width - 180, height: 230 }, body: { x: 90, y: 500, width: width - 180, height: 850 }, cta: { x: 90, y: 1430, width: width - 180, height: 130 } },
    'carousel-cover': { ...common, title: { x: 90, y: 190, width: width - 180, height: 500 }, body: null, cta: { x: 90, y: 850, width: width - 180, height: 130 } },
    'carousel-body': { ...common, title: { x: 90, y: 190, width: width - 180, height: 180 }, body: { x: 90, y: 420, width: width - 180, height: 650 }, cta: null },
    'carousel-cta': { ...common, title: { x: 90, y: 220, width: width - 180, height: 280 }, body: { x: 90, y: 590, width: width - 180, height: 320 }, cta: null },
    generic: { ...common, title: { x: 90, y: 190, width: width - 180, height: 240 }, body: { x: 90, y: 500, width: width - 180, height: height - 780 }, cta: null },
  };
  return layouts[kind] || layouts.generic;
}

function blockSvg(block) {
  if (!block?.lines.length) return '';
  const tspans = block.lines.map((line, index) => `<tspan x="${block.x}" y="${Math.round(block.y + block.fontSize + index * block.fontSize * block.lineHeight)}">${esc(line)}</tspan>`).join('');
  return `<text fill="${block.fill}" font-family="${esc(block.family)}" font-size="${block.fontSize}" font-weight="${block.weight}">${tspans}</text>`;
}

export function composeSvgCard({ width, height, label, title, body = '', cta = '', footer = DEFAULT_FOOTER, kind = 'generic' }) {
  const boxes = layoutFor(kind, width, height);
  const blocks = [
    textBlock('label', label, boxes.label, { maxFontSize: 32, minFontSize: 26, maxLines: 1, lineHeight: 1.1, fill: COLORS.gold }),
    textBlock('title', title, boxes.title, { maxFontSize: kind.startsWith('carousel') ? 52 : 58, minFontSize: 38, maxLines: kind === 'story-answer' || kind === 'carousel-body' ? 3 : 8, lineHeight: 1.12, weight: 'bold' }),
    boxes.body ? textBlock('body', body, boxes.body, { maxFontSize: kind === 'carousel-body' ? 36 : 38, minFontSize: 28, maxLines: kind === 'carousel-body' ? 13 : 18, lineHeight: 1.3 }) : null,
    boxes.cta ? textBlock('cta', cta, boxes.cta, { maxFontSize: 30, minFontSize: 24, maxLines: 3, lineHeight: 1.25, fill: COLORS.gold, family: SANS, weight: 'bold' }) : null,
    textBlock('footer', footer, boxes.footer, { maxFontSize: 25, minFontSize: 20, maxLines: 1, lineHeight: 1.1, family: SANS }),
  ].filter(Boolean);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><rect width="100%" height="100%" fill="${COLORS.navy}"/><rect x="48" y="48" width="${width - 96}" height="${height - 96}" rx="28" fill="${COLORS.cream}"/><rect x="90" y="158" width="120" height="4" rx="2" fill="${COLORS.gold}"/>${blocks.map(blockSvg).join('')}</svg>`;
  return { svg, width, height, kind, blocks };
}

export function svgCard(options) { return composeSvgCard(options).svg; }

export function validateVisualLayout(card) {
  if (/<foreignObject\b/i.test(card.svg)) throw new MediaLayoutError(`${card.kind}: foreignObject interdit`);
  if (!card.width || !card.height) throw new MediaLayoutError(`${card.kind}: dimensions absentes`);
  for (const block of card.blocks) {
    if (block.required && !block.lines.length) throw new MediaLayoutError(`${card.kind}/${block.name}: texte absent`);
    const measured = measureTextBlock(block.lines, { fontSize: block.fontSize, lineHeight: block.lineHeight });
    if (measured.width > block.width + 0.5) throw new MediaLayoutError(`${card.kind}/${block.name}: débordement horizontal ${Math.ceil(measured.width)}>${block.width}`);
    if (measured.height > block.height + 0.5) throw new MediaLayoutError(`${card.kind}/${block.name}: débordement vertical ${Math.ceil(measured.height)}>${block.height}`);
    if (block.x < 0 || block.y < 0 || block.x + block.width > card.width || block.y + block.height > card.height) throw new MediaLayoutError(`${card.kind}/${block.name}: boîte hors image`);
  }
  return true;
}

export function pngDimensions(buffer) {
  const signature = buffer.subarray(0, 8).toString('hex');
  if (signature !== '89504e470d0a1a0a' || buffer.subarray(12, 16).toString('ascii') !== 'IHDR') throw new MediaLayoutError('PNG invalide');
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

export async function renderPngBuffer(cardOrSvg) {
  const card = typeof cardOrSvg === 'string' ? { svg: cardOrSvg } : cardOrSvg;
  if (card.blocks) validateVisualLayout(card);
  const { Resvg } = await import('@resvg/resvg-js');
  const buffer = new Resvg(card.svg).render().asPng();
  if (card.width && card.height) {
    const dimensions = pngDimensions(buffer);
    if (dimensions.width !== card.width || dimensions.height !== card.height) throw new MediaLayoutError(`${card.kind}: dimensions PNG ${dimensions.width}×${dimensions.height}, attendu ${card.width}×${card.height}`);
    if (buffer.length < 1500) throw new MediaLayoutError(`${card.kind}: PNG anormalement vide`);
  }
  return buffer;
}

export async function renderPng(cardOrSvg, output) {
  const buffer = await renderPngBuffer(cardOrSvg);
  await fs.mkdir(path.dirname(output), { recursive: true });
  await fs.writeFile(output, buffer);
  return { output, bytes: buffer.length, ...(typeof cardOrSvg === 'string' ? {} : { width: cardOrSvg.width, height: cardOrSvg.height }) };
}

function splitTextAcrossSlides(text, count) {
  const words = cleanText(text).split(' ').filter(Boolean); const chunks = []; let cursor = 0;
  for (let index = 0; index < count; index++) {
    const remainingParts = count - index; const size = Math.ceil((words.length - cursor) / remainingParts);
    chunks.push(words.slice(cursor, cursor + size).join(' ')); cursor += size;
  }
  return chunks;
}

export function buildVisualAssets(candidate) {
  const words = assetText(candidate); const carouselBodies = splitTextAcrossSlides(words.body, 3);
  return [
    { key: 'reel_cover', relativePath: 'reel-cover.png', card: composeSvgCard({ width: 1080, height: 1920, kind: 'reel-cover', label: 'UNE MINUTE AVEC LE RAV', title: candidate.hook, cta: 'Écoutez la réponse validée du Rav.' }) },
    { key: 'story_teaser', relativePath: 'story-teaser.png', card: composeSvgCard({ width: 1080, height: 1920, kind: 'story-teaser', label: 'QUESTION', title: candidate.hook, cta: 'La réponse du Rav dans la story suivante.' }) },
    { key: 'story_answer', relativePath: 'story-answer.png', card: composeSvgCard({ width: 1080, height: 1920, kind: 'story-answer', label: words.label, title: candidate.topic, body: words.body, cta: 'Pour la pratique, consultez votre Rav.' }) },
    { key: 'carousel_01', relativePath: 'carousel/01.png', card: composeSvgCard({ width: 1080, height: 1350, kind: 'carousel-cover', label: 'HALAKHA DU JOUR', title: candidate.hook, cta: 'Faites défiler pour lire la réponse.' }) },
    ...carouselBodies.map((body, index) => ({ key: `carousel_0${index + 2}`, relativePath: `carousel/0${index + 2}.png`, card: composeSvgCard({ width: 1080, height: 1350, kind: 'carousel-body', label: `${words.label} · ${index + 1}/3`, title: candidate.topic, body }) })),
    { key: 'carousel_05', relativePath: 'carousel/05.png', card: composeSvgCard({ width: 1080, height: 1350, kind: 'carousel-cta', label: 'À RETENIR', title: 'Une réponse validée avant diffusion', body: 'Source audio et transcription conservées avec ce contenu.' }) },
  ];
}

export async function generateVisualMedia(candidate, outputRoot) {
  if (!mediaEligible(candidate)) throw new Error('MEDIA_REQUIRES_APPROVAL');
  const dir = path.join(outputRoot, new Date().toISOString().slice(0, 10), mediaDirectoryName(candidate));
  const visualAssets = buildVisualAssets(candidate); const outputs = {};
  for (const asset of visualAssets) {
    const output = path.join(dir, asset.relativePath); await renderPng(asset.card, output); outputs[asset.key] = output;
  }
  return { directory: dir, reel_cover: outputs.reel_cover, carousel: Array.from({ length: 5 }, (_, index) => outputs[`carousel_0${index + 1}`]), story_teaser: outputs.story_teaser, story_answer: outputs.story_answer };
}

export async function generateMedia(candidate, outputRoot) {
  if (!mediaEligible(candidate)) throw new Error('MEDIA_REQUIRES_APPROVAL');
  const visuals = await generateVisualMedia(candidate, outputRoot); const dir = visuals.directory;
  const srt = path.join(dir, 'reel.srt'); await fs.writeFile(srt, buildSrt(candidate));
  const source = { candidate_public_id: candidate.candidate_public_id, source_type: candidate.source_type, source_date: candidate.source_date, transcription_level: candidate.transcription_level };
  await fs.writeFile(path.join(dir, 'source.json'), JSON.stringify(source, null, 2)); await fs.writeFile(path.join(dir, 'proof.json'), JSON.stringify(candidate.proof, null, 2));
  await fs.writeFile(path.join(dir, 'captions.json'), JSON.stringify({ instagram: candidate.editorial_text, facebook: `${candidate.editorial_text}\n\nPour la pratique, consultez votre Rav.`, whatsapp: candidate.editorial_text, youtube: { title: candidate.hook, description: candidate.editorial_text } }, null, 2));
  await fs.writeFile(path.join(dir, 'schedule.json'), JSON.stringify({ status: MEDIA_STATE.READY_TO_SCHEDULE, recommended_time: { instagram: '18:30', facebook: '19:00', youtube: '17:00' }, scheduled_time: null }, null, 2));
  return { ...visuals, reel_srt: srt, status: MEDIA_STATE.READY_TO_SCHEDULE };
}
