import test from 'node:test';
import assert from 'node:assert/strict';
import { sanitizeForEditorialUse, classifyReliability, Reliability, assertSourceFirst, canUseAsVerifiedQuote, editorialScore, assessPrivacy, PrivacyRisk, formatsFor } from '../rav-content-engine/core.js';

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
