import { DatabaseSync } from 'node:sqlite';
import path from 'node:path';
import { opaqueId } from './core.js';
import { resolveAudioReference } from './audio-reference.js';

export class RavSourceRepository {
  constructor(dbPath = process.env.RAVQA_DB_PATH) {
    if (!dbPath) throw new Error('RAVQA_DB_PATH is required');
    this.dbPath = dbPath;
    this.db = new DatabaseSync(`file:${dbPath}?mode=ro`, { open: true, readOnly: true });
  }
  close() { this.db.close(); }
  search({ keyword = '', category, from, to, audioOnly = false, limit = 100 } = {}) {
    const where = ['deleted_at IS NULL', 'COALESCE(needs_review, 0) = 0']; const values = [];
    if (keyword) { where.push('(question_text LIKE ? OR transcript_torah_edited LIKE ? OR transcript_torah LIKE ? OR title LIKE ?)'); values.push(...Array(4).fill(`%${keyword}%`)); }
    if (category) { where.push('categories_json LIKE ?'); values.push(`%${category}%`); }
    if (from) { where.push('datetime(ts, \'unixepoch\') >= ?'); values.push(from); }
    if (to) { where.push('datetime(ts, \'unixepoch\') <= ?'); values.push(to); }
    if (audioOnly) where.push('COALESCE(audio_path, audio_m4a_path) IS NOT NULL');
    values.push(Math.min(Math.max(Number(limit) || 100, 1), 250));
    const sql = `SELECT id, ts, question_text, transcript_raw, transcript_torah, transcript_torah_edited, audio_path, audio_m4a_path, audio_seconds, sources_json, references_json, topics_json, categories_json, title, summary, relevance_score, enrichment_status FROM messages WHERE ${where.join(' AND ')} ORDER BY relevance_score DESC, ts DESC LIMIT ?`;
    return this.db.prepare(sql).all(...values).map((row) => {
      const audioReference = resolveAudioReference(row.audio_m4a_path || row.audio_path, path.dirname(this.dbPath));
      return { ...row, audio_path: audioReference, audio_m4a_path: null, source_type: 'ravqa', source_internal_id: row.id, candidate_public_id: opaqueId(`ravqa:${row.id}`) };
    }).filter((row) => !audioOnly || row.audio_path);
  }
  getById(id) { return this.search({ limit: 1, keyword: '' }).find((r) => r.id === Number(id)) || null; }
}
