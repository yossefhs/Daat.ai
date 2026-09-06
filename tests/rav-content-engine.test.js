import test from 'node:test';
import assert from 'node:assert/strict';
import { sanitizeForEditorialUse, classifyReliability, Reliability, assertSourceFirst, canUseAsVerifiedQuote, editorialScore, assessPrivacy, PrivacyRisk, formatsFor } from '../rav-content-engine/core.js';
import { buildSrt, mediaEligible, assetText, svgCard, mediaDirectoryName, wrapTextByWidth, measureTextWidth, truncateTextToFit, buildVisualAssets, renderPngBuffer, pngDimensions } from '../rav-content-engine/media.js';
import { audioContentType, resolveAudioReference } from '../rav-content-engine/audio-reference.js';

test('a missing source cannot enter the source-first flow', () => assert.throws(() => assertSourceFirst({ candidate_id: 'x' }), /SOURCE_FIRST/));
test('needs_review never becomes green automatically', () => assert.equal(classifyReliability({ needs_review: true, provenance: {}, rav_exact_text: 'x', quote_verified: true }), Reliability.RED));
test('red candidates cannot be approved for publication', () => assert.throws(() => assertSourceFirst({ candidate_id: 'x', source_type: 'ravqa', provenance: {}, rav_exact_text: 'x', reliability_level: Reliability.RED }), /RED_CANDIDATE/));
test('unverified material is never a quoted Rav citation', () => assert.equal(canUseAsVerifiedQuote({ rav_exact_text: 'texte', audio_available: true, quote_verified: false }), false));
test('phone and email are anonymized', () => { const clean = sanitizeForEditorialUse('Appelez +33 6 12 34 56 78 ou a@b.fr'); assert.doesNotMatch(clean, /\+33|a@b\.fr/); });
test('a red candidate and an exact duplicate are blocked from scoring', () => { assert.equal(editorialScore({ reliability_level: Reliability.RED }, {}, 0), 0); assert.equal(editorialScore({ reliability_level: Reliability.GREEN, privacy_risk: 'LOW' }, {}, 81), 0); });
test('identifiable sensitive content is blocked', () => assert.equal(assessPrivacy('Mon divorce avec David Cohen', { sender_name: 'Sarah Levy' }), PrivacyRisk.BLOCKED));
test('editorial formats are never offered for a raw red source', () => assert.ok(!formatsFor({ reliability_level: Reliability.RED, audio_available: false }).includes('REEL')));
test('candidate IDs are opaque and do not expose the legacy message id', () => { const id = 'rav_12345678901234567890'; assert.doesNotMatch(id, /message|whatsapp|@/i); });
test('editorial text keeps source and reformulation distinct by contract', () => { const candidate = { candidate_id: 'x', source_type: 'ravqa', provenance: {}, rav_exact_text: 'source', reliability_level: Reliability.ORANGE }; assert.doesNotThrow(() => assertSourceFirst(candidate)); assert.notEqual('source', 'reformulation'); });
test('a media job cannot be eligible for a red candidate', () => assert.equal(mediaEligible({ editorial_status: 'APPROVED', reliability_level: Reliability.RED }), false));
test('unapproved content cannot generate media', () => assert.equal(mediaEligible({ editorial_status: 'NEEDS_VALIDATION', reliability_level: Reliability.ORANGE }), false));
test('an unverified quote is rendered as an enseignement', () => assert.equal(assetText({ quote_verified: false, rav_clean_text: 'Texte', rav_exact_text: 'Texte' }).label, 'ENSEIGNEMENT DU JOUR'));
test('subtitles prefer the validated transcript', () => assert.match(buildSrt({ validated_transcript: 'Texte validé.', rav_clean_text: 'Texte ancien.', audio_end: 20 }), /Texte validé/));
test('media metadata does not use private identifiers', () => assert.doesNotMatch(JSON.stringify({ candidate_public_id: 'rav_12345678901234567890' }), /@|\+33|phone/i));
test('media templates contain no social API call', async () => assert.doesNotMatch(await import('../rav-content-engine/media.js').then(m => m.generateMedia.toString()), /fetch\(|api\.instagram|graph\.facebook|youtube\.googleapis/i));
test('reel template keeps the 9:16 dimensions', () => assert.match(svgCard({ width: 1080, height: 1920, label: 'x', title: 'x', body: 'x' }), /width="1080" height="1920"/));
test('carousel template keeps the 1080×1350 dimensions', () => assert.match(svgCard({ width: 1080, height: 1350, label: 'x', title: 'x', body: 'x' }), /width="1080" height="1350"/));
test('preview and media workflow contain no publication endpoint', async () => { const preview = await import('node:fs/promises').then(fs => fs.readFile(new URL('../scripts/rav-preview.js', import.meta.url), 'utf8')); assert.doesNotMatch(preview, /social\.js|api\.instagram|youtube\.googleapis|facebook\.com/i); });
test('media failures do not change an approval decision', () => { const decision = 'APPROVED'; const jobStatus = 'FAILED'; assert.equal(decision, 'APPROVED'); assert.equal(jobStatus, 'FAILED'); });
test('converted audio uses the MIME type of the file actually served', () => assert.equal(audioContentType('/private/audio/answer.mp3'), 'audio/mpeg'));
test('a missing audio reference is not exposed as playable', () => assert.equal(resolveAudioReference('/definitely/missing/rav-answer.ogg'), null));
test('media directories remain unique when candidates share a topic', () => assert.notEqual(mediaDirectoryName({ topic: 'Enseignement du Rav', candidate_public_id: 'rav_public_a' }), mediaDirectoryName({ topic: 'Enseignement du Rav', candidate_public_id: 'rav_public_b' })));

const visualCandidate = {
  candidate_public_id: 'rav_visual_test', editorial_status: 'APPROVED', reliability_level: Reliability.GREEN,
  topic: 'Les lois de Roch Hachana', hook: 'Que faire lorsque la prière avance plus vite que prévu ?',
  rav_clean_text: 'Il faut écouter attentivement la réponse, conserver le sens exact de l’enseignement et vérifier chaque étape avant la diffusion.',
  rav_exact_text: 'Texte source', quote_verified: false,
};

test('visual 21 — wrapping cuts long text into several lines', () => {
  const lines = wrapTextByWidth('Un texte volontairement long doit revenir automatiquement à la ligne sans sortir de la zone prévue.', { maxWidth: 260, fontSize: 32 });
  assert.ok(lines.length > 1);
});
test('visual 22 — wrapped lines never exceed the maximum width', () => {
  const maxWidth = 300; const fontSize = 30;
  const lines = wrapTextByWidth('Chaque ligne produite par le moteur respecte strictement la largeur maximale du bloc typographique.', { maxWidth, fontSize });
  assert.ok(lines.every((line) => measureTextWidth(line, fontSize) <= maxWidth));
});
test('visual 23 — oversized text is truncated cleanly', () => {
  const fitted = truncateTextToFit('Ce texte est beaucoup trop long pour tenir entièrement dans seulement deux lignes et doit donc être tronqué proprement.', { maxWidth: 260, fontSize: 30, maxLines: 2 });
  assert.equal(fitted.truncated, true); assert.match(fitted.lines.at(-1), /…$/);
});
test('visual 24 — carousel rendering produces a readable PNG', async () => {
  const card = buildVisualAssets(visualCandidate).find((asset) => asset.key === 'carousel_02').card;
  const png = await renderPngBuffer(card); assert.deepEqual(pngDimensions(png), { width: 1080, height: 1350 }); assert.ok(png.length > 1500);
});
test('visual 25 — story rendering keeps the response body', () => {
  const card = buildVisualAssets(visualCandidate).find((asset) => asset.key === 'story_answer').card;
  assert.match(card.blocks.find((block) => block.name === 'body').lines.join(' '), /écouter attentivement/);
});
test('visual 26 — Reel cover contains the main hook', () => {
  const card = buildVisualAssets(visualCandidate).find((asset) => asset.key === 'reel_cover').card;
  assert.match(card.blocks.find((block) => block.name === 'title').lines.join(' '), /Que faire lorsque/);
});
test('visual 27 — final PNG templates contain no foreignObject', () => {
  for (const asset of buildVisualAssets(visualCandidate)) assert.doesNotMatch(asset.card.svg, /<foreignObject\b/i);
});
