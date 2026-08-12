import { EditorialRegistry } from '../rav-content-engine/registry.js';
import { generateMedia } from '../rav-content-engine/media.js';
if (!process.env.RAV_CONTENT_OUTPUT_PATH) throw new Error('RAV_CONTENT_OUTPUT_PATH is required');
const registry = new EditorialRegistry();
try { const approved = registry.candidates('APPROVED'); console.log(`Candidats APPROVED : ${approved.length}`); for (const row of approved) { const job = registry.createMediaJob(row.payload); try { const outputs = await generateMedia(row.payload, process.env.RAV_CONTENT_OUTPUT_PATH); registry.updateMediaJob(job.id, outputs.status, outputs); console.log(`Média prêt : ${row.payload.candidate_public_id}`); } catch (error) { registry.updateMediaJob(job.id, 'FAILED', {}, String(error.message)); console.error(`Échec média : ${row.payload.candidate_public_id}`); } } } finally { registry.close(); }
