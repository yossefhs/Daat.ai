import fs from 'node:fs/promises';
import path from 'node:path';
import { presentationOfRavText } from './core.js';

export const MEDIA_STATE = Object.freeze({ DRAFT: 'DRAFT', APPROVED: 'APPROVED', MEDIA_READY: 'MEDIA_READY', READY_TO_SCHEDULE: 'READY_TO_SCHEDULE', SCHEDULED: 'SCHEDULED', PUBLISHED: 'PUBLISHED', FAILED: 'FAILED' });
export function subtitleText(candidate) { return candidate.validated_transcript || candidate.rav_clean_text || ''; }
export function buildSrt(candidate) { const text = subtitleText(candidate).trim(); if (!text) throw new Error('VALIDATED_TRANSCRIPT_REQUIRED'); const end = Math.max(1, Number(candidate.audio_end || 60)); const chunks = text.match(/[^.!?]+[.!?]?/g) || [text]; return chunks.map((chunk, i) => `${i + 1}\n00:00:${String(Math.min(end - 1, i * 4)).padStart(2, '0')},000 --> 00:00:${String(Math.min(end, (i + 1) * 4)).padStart(2, '0')},000\n${chunk.trim()}\n`).join('\n'); }
export function mediaEligible(candidate) { return candidate?.editorial_status === 'APPROVED' && candidate?.reliability_level !== 'RED'; }
export function assetText(candidate) { return candidate.quote_verified ? { label: 'CITATION DU JOUR', body: `« ${candidate.rav_exact_text} »` } : { label: 'ENSEIGNEMENT DU JOUR', body: presentationOfRavText(candidate) }; }
const esc = (s) => String(s || '').replace(/[&<>]/g, (x) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[x]));
export function svgCard({ width, height, label, title, body, footer = 'Dayan-Rav Mikhaël Chlomo Abichid' }) { return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}"><rect width="100%" height="100%" fill="#10182E"/><rect x="48" y="48" width="${width - 96}" height="${height - 96}" rx="28" fill="#FAF6EE"/><text x="90" y="130" fill="#B18B43" font-family="Georgia" font-size="32">${esc(label)}</text><text x="90" y="230" fill="#10182E" font-family="Georgia" font-size="54" font-weight="bold">${esc(title).slice(0, 72)}</text><foreignObject x="90" y="300" width="${width - 180}" height="${height - 470}"><div xmlns="http://www.w3.org/1999/xhtml" style="font:34px Georgia;color:#10182E;line-height:1.35">${esc(body).slice(0, 500)}</div></foreignObject><text x="90" y="${height - 105}" fill="#10182E" font-family="Arial" font-size="25">${esc(footer)}</text></svg>`; }
export async function renderPng(svg, output) { const { Resvg } = await import('@resvg/resvg-js'); await fs.mkdir(path.dirname(output), { recursive: true }); await fs.writeFile(output, new Resvg(svg).render().asPng()); }
export async function generateMedia(candidate, outputRoot) {
  if (!mediaEligible(candidate)) throw new Error('MEDIA_REQUIRES_APPROVAL');
  const slug = candidate.topic.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || candidate.candidate_public_id;
  const dir = path.join(outputRoot, new Date().toISOString().slice(0, 10), slug); const words = assetText(candidate);
  const cover = path.join(dir, 'reel-cover.png'); const story = path.join(dir, 'story-teaser.png'); const answer = path.join(dir, 'story-answer.png'); const carousel = Array.from({ length: 5 }, (_, i) => path.join(dir, 'carousel', `${String(i + 1).padStart(2, '0')}.png`));
  await renderPng(svgCard({ width: 1080, height: 1920, label: 'UNE MINUTE AVEC LE RAV', title: candidate.hook, body: words.body }), cover);
  await renderPng(svgCard({ width: 1080, height: 1920, label: 'QUESTION', title: candidate.hook, body: 'Écoutez la réponse du Rav.' }), story);
  await renderPng(svgCard({ width: 1080, height: 1920, label: words.label, title: candidate.topic, body: words.body }), answer);
  for (let i = 0; i < carousel.length; i++) await renderPng(svgCard({ width: 1080, height: 1350, label: i === 0 ? 'HALAKHA DU JOUR' : words.label, title: i === 0 ? candidate.hook : candidate.topic, body: i === 4 ? 'Source et validation avant diffusion.' : words.body }), carousel[i]);
  const srt = path.join(dir, 'reel.srt'); await fs.writeFile(srt, buildSrt(candidate));
  const source = { candidate_public_id: candidate.candidate_public_id, source_type: candidate.source_type, source_date: candidate.source_date, transcription_level: candidate.transcription_level };
  await fs.writeFile(path.join(dir, 'source.json'), JSON.stringify(source, null, 2)); await fs.writeFile(path.join(dir, 'proof.json'), JSON.stringify(candidate.proof, null, 2));
  await fs.writeFile(path.join(dir, 'captions.json'), JSON.stringify({ instagram: candidate.editorial_text, facebook: `${candidate.editorial_text}\n\nPour la pratique, consultez votre Rav.`, whatsapp: candidate.editorial_text, youtube: { title: candidate.hook, description: candidate.editorial_text } }, null, 2));
  await fs.writeFile(path.join(dir, 'schedule.json'), JSON.stringify({ status: MEDIA_STATE.READY_TO_SCHEDULE, recommended_time: { instagram: '18:30', facebook: '19:00', youtube: '17:00' }, scheduled_time: null }, null, 2));
  return { directory: dir, reel_cover: cover, reel_srt: srt, carousel, story_teaser: story, story_answer: answer, status: MEDIA_STATE.READY_TO_SCHEDULE };
}
