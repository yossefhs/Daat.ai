import { sanitizeForEditorialUse, assessPrivacy, classifyReliability, opaqueId, editorialScore, formatsFor, presentationOfRavText, Reliability } from './core.js';

const THEMES = ['chofar', 'eloul', 'teshouva', 'roch hachana', 'selihot', 'repentance'];

function parse(value) { try { return value ? JSON.parse(value) : []; } catch { return []; } }
function textOf(row) { return row.transcript_torah_edited || row.transcript_torah || row.transcript_raw || ''; }
function topicOf(row) { return row.title || parse(row.topics_json)[0] || 'Enseignement du Rav'; }

export function toCandidate(row, registry) {
  const ravText = textOf(row).trim();
  const provisional = { provenance: { source: 'ravqa', internal_id: row.id }, rav_exact_text: ravText, needs_review: false, audio_available: Boolean(row.audio_path || row.audio_m4a_path), transcription_level: row.transcript_torah_edited ? 'torah_edited' : row.transcript_torah ? 'corrected' : 'raw_machine', quote_verified: false };
  const reliability = classifyReliability(provisional);
  const topic = topicOf(row); const candidateId = opaqueId(`candidate:ravqa:${row.id}`);
  const candidate = {
    candidate_id: candidateId, candidate_public_id: row.candidate_public_id, source_type: 'ravqa', source_internal_id: row.id,
    provenance: { system: 'ravqa', source_public_id: row.candidate_public_id, audio_reference_present: provisional.audio_available },
    source_date: row.ts ? new Date(row.ts * 1000).toISOString() : null, topic, subtopic: null, category: parse(row.categories_json), tags: parse(row.topics_json),
    question_anonymized: sanitizeForEditorialUse(row.question_text), rav_exact_text: ravText, rav_clean_text: ravText,
    audio_available: provisional.audio_available, audio_reference: row.audio_m4a_path || row.audio_path || null, audio_start: 0, audio_end: row.audio_seconds || null,
    youtube_url: null, youtube_video_id: null, halakhic_sources: parse(row.references_json), transcription_level: provisional.transcription_level,
    confidence: Number(row.relevance_score || 0), privacy_status: 'SANITIZED', privacy_risk: assessPrivacy(row.question_text, row), reliability_level: reliability,
    editorial_status: reliability === Reliability.GREEN ? 'READY_FOR_REVIEW' : reliability === Reliability.ORANGE ? 'NEEDS_VALIDATION' : 'BLOCKED',
    quote_verified: false, calendar_tags: [], created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
  };
  candidate.duplicate_score = registry.duplicateScore(candidate); candidate.editorial_score = editorialScore(candidate, { relevance: 16 }, candidate.duplicate_score);
  candidate.formats = formatsFor(candidate); candidate.angle = `Réponse pratique : ${topic}`;
  candidate.hook = candidate.question_anonymized || `Que dit le Rav sur ${topic} ?`;
  candidate.editorial_text = `${presentationOfRavText(candidate)}\n\nÀ VALIDER PAR LE RAV.`;
  candidate.proof = { source: `ravqa / message privé ${candidate.candidate_public_id}`, audio: candidate.audio_available ? 'présent' : 'absent', excerpt: candidate.rav_exact_text.slice(0, 420), confidence: candidate.confidence, validation: candidate.editorial_status };
  return candidate;
}

export function generateWeeklyPack(repository, registry, { themes = THEMES, limit = 40 } = {}) {
  const rows = themes.flatMap((keyword) => repository.search({ keyword, audioOnly: true, limit })).filter((row, index, all) => all.findIndex((x) => x.id === row.id) === index);
  const candidates = rows.map((row) => toCandidate(row, registry)).sort((a, b) => b.editorial_score - a.editorial_score);
  candidates.forEach((candidate) => registry.saveCandidate(candidate));
  const publishable = candidates.filter((c) => c.editorial_status !== 'BLOCKED');
  return { generated_at: new Date().toISOString(), themes, analyzed: candidates.length, counts: Object.fromEntries(['GREEN', 'ORANGE', 'RED'].map((r) => [r, candidates.filter((c) => c.reliability_level === r).length])), reels: publishable.filter((c) => c.formats.includes('REEL')).slice(0, 3), halakha: publishable.filter((c) => c.formats.includes('HALAKHA_DU_JOUR')).slice(0, 2), stories: publishable.filter((c) => c.formats.includes('STORY')).slice(0, 7), whatsapp: publishable.filter((c) => c.formats.includes('WHATSAPP')).slice(0, 2), candidates };
}

export function formatPack(pack) {
  const line = (c) => `${c.reliability_level === 'GREEN' ? '🟢' : '🟠'} ${c.editorial_score}/100 — ${c.topic}\n   PREUVE: ${c.proof.source}; audio ${c.proof.audio}; ${c.proof.validation}`;
  return ['RAV ABICHID — PACK ÉDITORIAL', `Candidats analysés : ${pack.analyzed} | GREEN ${pack.counts.GREEN} / ORANGE ${pack.counts.ORANGE} / RED ${pack.counts.RED}`, '', 'REELS', ...(pack.reels.map(line) || ['Aucun candidat suffisamment sûr']), '', 'HALAKHA', ...(pack.halakha.map(line) || ['Aucun candidat suffisamment sûr']), '', 'STORIES', ...(pack.stories.map(line) || ['Aucun candidat suffisamment sûr'])].join('\n');
}
