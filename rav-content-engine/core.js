import crypto from 'node:crypto';

export const Reliability = Object.freeze({ GREEN: 'GREEN', ORANGE: 'ORANGE', RED: 'RED' });
export const PrivacyRisk = Object.freeze({ LOW: 'LOW', MEDIUM: 'MEDIUM', HIGH: 'HIGH', BLOCKED: 'BLOCKED' });

const SENSITIVE = /\b(sant[ée]|m[ée]dical|maladie|cancer|couple|mariage|divorce|nidda|niddah|sexualit[ée]|conversion|deuil|enfant|grossesse|finance|dette|litige|adoption)\b/i;
const PHONE = /(?:\+?\d[\d .()\-]{7,}\d)/g;
const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi;
const WA_ID = /\b\d{5,}@(?:c\.us|g\.us)\b/gi;
const PRIVATE_URL = /https?:\/\/[^\s]*(?:chat\.whatsapp\.com|drive\.google\.com|dropbox\.com)[^\s]*/gi;
const ADDRESS = /\b(?:\d{1,4}\s+)?(?:rue|avenue|boulevard|all[ée]e|place)\s+[^,.\n]{3,}/gi;

export function opaqueId(value) {
  return `rav_${crypto.createHash('sha256').update(String(value)).digest('hex').slice(0, 20)}`;
}

export function sanitizeForEditorialUse(input = '') {
  let text = String(input).replace(PHONE, '[numéro masqué]').replace(EMAIL, '[e-mail masqué]')
    .replace(WA_ID, '[identifiant masqué]').replace(PRIVATE_URL, '[lien privé masqué]').replace(ADDRESS, '[adresse masquée]');
  // Salutations WhatsApp contenant un nom sont rarement utiles au contenu éditorial.
  text = text.replace(/^(?:bonjour|bonsoir|shalom)\s+(?:rav\s*,?\s*)?(?:je m['’]appelle\s+)?[A-ZÀ-Ý][\p{L}'’-]+(?:\s+[A-ZÀ-Ý][\p{L}'’-]+){0,3}[,.:;!]?\s*/uim, 'Une personne demande : ');
  text = text.replace(/\b(?:mon mari|ma femme|mon fils|ma fille|monsieur|madame)\s+[A-ZÀ-Ý][\p{L}'’-]+(?:\s+[A-ZÀ-Ý][\p{L}'’-]+){0,2}\b/gu, '$&'.replace(/[A-ZÀ-Ý][\p{L}'’-]+(?:\s+[A-ZÀ-Ý][\p{L}'’-]+){0,2}/u, 'une personne'));
  return text.replace(/\s{2,}/g, ' ').trim();
}

export function assessPrivacy(question, metadata = {}) {
  const combined = `${question || ''} ${metadata.sender_name || ''} ${metadata.group_name || ''}`;
  const identifiable = PHONE.test(combined) || EMAIL.test(combined) || WA_ID.test(combined) || /\b[A-ZÀ-Ý][\p{L}'’-]+\s+[A-ZÀ-Ý][\p{L}'’-]+/u.test(combined);
  if (SENSITIVE.test(combined) && identifiable) return PrivacyRisk.BLOCKED;
  if (SENSITIVE.test(combined)) return PrivacyRisk.HIGH;
  return identifiable ? PrivacyRisk.MEDIUM : PrivacyRisk.LOW;
}

export function classifyReliability(row) {
  if (!row || row.needs_review || !row.provenance || !row.rav_exact_text) return Reliability.RED;
  if (row.quote_verified || (row.audio_available && row.transcription_level === 'human_verified')) return Reliability.GREEN;
  if (row.transcription_level === 'torah_edited' || row.transcription_level === 'corrected') return Reliability.ORANGE;
  return Reliability.RED;
}

export function assertSourceFirst(candidate) {
  if (!candidate?.candidate_id || !candidate?.source_type || !candidate?.provenance || !candidate?.rav_exact_text || !candidate?.reliability_level) {
    throw new Error('SOURCE_FIRST_VIOLATION');
  }
  if (candidate.reliability_level === Reliability.RED) throw new Error('RED_CANDIDATE_BLOCKED');
}

export function canUseAsVerifiedQuote(candidate) {
  return Boolean(candidate?.quote_verified && candidate?.rav_exact_text && candidate?.audio_available);
}

export function presentationOfRavText(candidate) {
  return canUseAsVerifiedQuote(candidate) ? `« ${candidate.rav_exact_text} »` : `D’après l’enseignement du Rav : ${candidate.rav_clean_text}`;
}

export function editorialScore(candidate, calendar = {}, duplicateScore = 0) {
  if (candidate.reliability_level === Reliability.RED || candidate.privacy_risk === PrivacyRisk.BLOCKED || duplicateScore > 80) return 0;
  const calendarScore = Math.min(20, Number(calendar.relevance || 0));
  const practical = Math.min(20, Number(candidate.practical_score || 10));
  const hook = Math.min(15, Number(candidate.hook_score || 8));
  const audio = Math.min(15, candidate.audio_available ? Number(candidate.audio_score || 12) : 0);
  const reliability = candidate.reliability_level === Reliability.GREEN ? 20 : 12;
  const freshness = Math.max(0, 10 - Math.round(duplicateScore / 10));
  return calendarScore + practical + hook + audio + reliability + freshness;
}

export function formatsFor(candidate) {
  const formats = ['FACEBOOK'];
  if (candidate.audio_available) formats.push('REEL', 'SHORT', 'UNE_MINUTE_AVEC_LE_RAV');
  if (candidate.reliability_level !== Reliability.RED) formats.push('CAROUSEL', 'HALAKHA_DU_JOUR', 'STORY', 'WHATSAPP', 'ENSEIGNEMENT_DU_JOUR');
  return formats;
}
