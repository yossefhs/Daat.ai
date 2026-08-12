import { RavSourceRepository } from '../rav-content-engine/rav-source-repository.js';
import { EditorialRegistry } from '../rav-content-engine/registry.js';
import { generateWeeklyPack, formatPack } from '../rav-content-engine/weekly-pack.js';

const repository = new RavSourceRepository();
const registry = new EditorialRegistry();
try { console.log(formatPack(generateWeeklyPack(repository, registry))); } finally { repository.close(); registry.close(); }
