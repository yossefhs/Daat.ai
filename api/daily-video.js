/**
 * daily-video.js — cron quotidien : génère et publie la vidéo Daat Yomi du jour.
 *
 * Déclenché par Vercel cron (auth Bearer ${CRON_SECRET}). Activé seulement si
 * DAILY_VIDEO_ENABLED=1. Sans clés (JSON2VIDEO_API_KEY / AYRSHARE_API_KEY), les
 * étapes correspondantes sont des no-op : l'endpoint reste sûr et idempotent.
 *
 * Le plan Daat Yomi n'a d'entrée que du dimanche au jeudi → les autres jours,
 * l'endpoint ne fait rien (skip).
 */
import { getEntryForDate } from './_daily-limoud.js';
import { buildStoryboard, buildCaption, toJson2Video, renderVideo, postVideo } from './_daily-video.js';

export default async function handler(req, res) {
  const expected = process.env.CRON_SECRET;
  const auth = req.headers.authorization || '';
  if (!expected || auth !== `Bearer ${expected}`) {
    return res.status(401).json({ error: 'unauthorized' });
  }
  if (process.env.DAILY_VIDEO_ENABLED !== '1') {
    return res.status(200).json({ skipped: 'DAILY_VIDEO_ENABLED != 1' });
  }

  // ?date=YYYY-MM-DD pour tester un jour précis, sinon aujourd'hui.
  const date = (req.query?.date) || new Date().toISOString().slice(0, 10);
  const entry = getEntryForDate(date);
  if (!entry) {
    return res.status(200).json({ skipped: `pas d'entrée Daat Yomi pour ${date}` });
  }

  try {
    const movie = toJson2Video(buildStoryboard(entry));
    const render = await renderVideo(movie);
    if (!render.url) {
      return res.status(200).json({ date, day: entry.dayNumber, render });
    }
    const post = await postVideo(render.url, buildCaption(entry));
    return res.status(200).json({ date, day: entry.dayNumber, video: render.url, post });
  } catch (e) {
    return res.status(500).json({ error: String(e?.message || e), date });
  }
}
