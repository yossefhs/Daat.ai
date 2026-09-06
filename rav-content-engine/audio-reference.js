import fs from 'node:fs';
import path from 'node:path';

const AUDIO_EXTENSIONS = ['.mp3', '.m4a', '.ogg', '.opus', '.wav', '.webm'];

export function resolveAudioReference(reference, baseDirectory) {
  if (!reference) return null;
  const original = baseDirectory && !path.isAbsolute(reference) ? path.resolve(baseDirectory, reference) : reference;
  const extension = path.extname(original);
  const stem = extension ? original.slice(0, -extension.length) : original;
  const candidates = [original, ...AUDIO_EXTENSIONS.map((candidateExtension) => `${stem}${candidateExtension}`)];
  return candidates.find((candidate) => fs.existsSync(candidate)) || null;
}

export function audioContentType(reference) {
  return ({ '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4', '.ogg': 'audio/ogg', '.opus': 'audio/ogg', '.wav': 'audio/wav', '.webm': 'audio/webm' })[path.extname(reference).toLowerCase()] || 'application/octet-stream';
}
