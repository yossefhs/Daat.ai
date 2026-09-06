import { EditorialRegistry } from '../rav-content-engine/registry.js';
import { generateVisualMedia, MEDIA_STATE } from '../rav-content-engine/media.js';

if (!process.env.RAV_CONTENT_OUTPUT_PATH) throw new Error('RAV_CONTENT_OUTPUT_PATH is required');
const registry = new EditorialRegistry();
try {
  const approved = registry.candidates('APPROVED');
  console.log(`Visuels APPROVED à régénérer : ${approved.length}`);
  for (const row of approved) {
    const job = registry.createMediaJob(row.payload);
    try {
      const visuals = await generateVisualMedia(row.payload, process.env.RAV_CONTENT_OUTPUT_PATH);
      const previous = JSON.parse(job.outputs_json || '{}');
      registry.updateMediaJob(job.id, MEDIA_STATE.READY_TO_SCHEDULE, { ...previous, ...visuals, status: MEDIA_STATE.READY_TO_SCHEDULE });
      console.log(`Visuels prêts : ${row.payload.candidate_public_id}`);
    } catch (error) {
      const status = error?.code === MEDIA_STATE.MEDIA_FAILED_LAYOUT ? MEDIA_STATE.MEDIA_FAILED_LAYOUT : MEDIA_STATE.FAILED;
      registry.updateMediaJob(job.id, status, {}, String(error.message));
      console.error(`Échec visuel (${status}) : ${row.payload.candidate_public_id} — ${error.message}`);
    }
  }
} finally { registry.close(); }
