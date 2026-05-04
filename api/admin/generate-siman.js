// Endpoint admin : génération automatique des 4 fichiers HTML d'un nouveau siman.
//
// Stratégie : Claude Opus 4.7 reçoit en CONTEXTE les 4 fichiers complets de
// siman-242 (notre référence canonique de style/structure). Grâce au prompt
// caching d'Anthropic (cache_control: ephemeral), le gabarit n'est facturé
// qu'une fois pour les 4 appels successifs. Pour chaque fichier de sortie,
// Claude reçoit le nouveau contenu (texte hébreu + traduction + métadonnées
// + mareh mekomot résolus via Sefaria) et produit un HTML structurellement
// identique à siman-242 mais adapté au nouveau siman.
//
// Auth : header Authorization: Bearer <ADMIN_PASSWORD>
//
// POST /api/admin/generate-siman
//   body : {
//     siman: "247",                 // numéro arabe du siman
//     num_he: "רמ״ז",               // numéro hébreu (gimatria)
//     title_he: "...",              // titre hébreu officiel du siman
//     title_fr: "...",              // titre français
//     subtitle: "...",              // sous-titre court (ex: "un seul Seif :")
//     hebrew_text: "...",           // texte hébreu original (Mehaber)
//     hagahot?: "...",              // Hagahot du Rama si applicable
//     translation_fr?: "...",       // traduction française (générée si absente)
//     chapter?: "hilkhot-shabbat",  // chapitre (défaut: hilkhot-shabbat)
//     section?: "orah-haim",        // section (défaut: orah-haim)
//     refs?: ["Shulchan_Arukh,_Orach_Chayim.247.1", ...]  // refs Sefaria à résoudre auto
//   }
//
//   réponse : {
//     ok: true,
//     siman: "247",
//     files: {
//       "index.html": "<!DOCTYPE html>...",
//       "niveau-1-base.html": "...",
//       "niveau-2-lamdan.html": "...",
//       "niveau-3-synthese.html": "..."
//     },
//     mareh_mekomot: [{ ref, hebrew, english, title }],
//     translation_fr: "...",  // remontée si on l'a générée
//     usage: { input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens }
//   }

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { fetchSefariaText } from '../_sefaria.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TEMPLATE_DIR = join(__dirname, '..', '..', 'sources', 'shabbat', 'siman-242');

export const config = {
  api: {
    bodyParser: { sizeLimit: '4mb' },
  },
};

const MODEL = 'claude-opus-4-7';
const MAX_OUTPUT_TOKENS = 16384; // nos templates font ~700-900 lignes — il faut de la marge.

const TARGETS = [
  { file: 'index.html',           role: 'page d\'entrée du siman (présentation, 3 niveaux, poskim, concepts)' },
  { file: 'niveau-1-base.html',   role: 'niveau 1 BASE — pédagogique, format A4/PDF, plan + 10 sections + texte original + traduction + 3 catégories pratiques + dilemme + questions de compréhension' },
  { file: 'niveau-2-lamdan.html', role: 'niveau 2 LAMDAN — pilpoul approfondi, חקירת היסוד, plusieurs פרשנויות, מאמרי חז״ל, sougya complète, tikkunim modernes' },
  { file: 'niveau-3-synthese.html', role: 'niveau 3 SYNTHÈSE — récap révision, axiomes, arbres décision, mnémoniques, pièges, cas pratiques, 5 commandements' },
];

function checkAuth(req) {
  const expected = process.env.ADMIN_PASSWORD;
  if (!expected) {
    return { ok: false, status: 500, error: 'ADMIN_PASSWORD non configuré côté serveur' };
  }
  const auth = req.headers['authorization'] || '';
  const provided = auth.startsWith('Bearer ') ? auth.slice(7) : '';
  if (provided !== expected) {
    return { ok: false, status: 401, error: 'Non autorisé' };
  }
  return { ok: true };
}

let _templateCache = null;
function loadTemplate() {
  if (_templateCache) return _templateCache;
  const files = {};
  for (const t of TARGETS) {
    files[t.file] = readFileSync(join(TEMPLATE_DIR, t.file), 'utf-8');
  }
  _templateCache = files;
  return files;
}

function buildSystemPrompt(template, meta) {
  return `Tu es l'auteur expert de daattorah.com — plateforme d'étude halakhique en français.

Ta mission : générer le HTML d'un nouveau siman EN COPIANT FIDÈLEMENT la structure, le style CSS, le ton et la profondeur pédagogique du siman 242 (Hilkhot Shabbat — להזהר בכבוד שבת) qui est la référence canonique de la plateforme. Tu ne dois RIEN inventer halakhiquement : tu pars du texte hébreu fourni par l'admin, tu cites scrupuleusement les sources fournies, tu présentes les positions sans trancher.

PRINCIPES NON-NÉGOCIABLES :
1. **Structure HTML 1:1** : tu reprends le squelette HTML de la référence (header, breadcrumb, hero, sections, footer), les classes CSS (.section-title, .sacred-text, .translation, .key-point, .definition, .question-box, .poskim-table, .concept-box, etc.), les tags rabbiniques (Frank Ruhl Libre, Cormorant Garamond, Inter), les couleurs (var(--navy), var(--gold), var(--cream), var(--green)).
2. **Pas de simplification** : si le siman 242 a 10 sections au niveau 1, le nouveau siman doit avoir un nombre comparable de sections. Si le niveau 2 a 3 פרשנויות + 5 מאמרי חז״ל, tu fais pareil — adapté au nouveau contenu.
3. **Hébreu fidèle** : tout hébreu que tu insères doit être copié du texte fourni ou des sources Sefaria fournies. Pas de paraphrase de l'hébreu.
4. **Traduction française rigoureuse** : précise, halakhique, sans glose. Jamais de psak — toujours "selon X, Y. Selon Z, W."
5. **Mareh mekomot** : tu intègres les sources Sefaria fournies (Guemara, Rambam, Tour, Mishna Beroura, etc.) dans la section appropriée du niveau 2 et tu les cites en bas du niveau 1. Pour chaque source, tu donnes la ref + un lien vers Sefaria.
6. **Liens internes** : entre les 3 niveaux (level-1 ↔ level-2 ↔ level-3) et vers le chat IA (chat.html), tels qu'ils existent dans le siman 242.
7. **PDF** : les liens vers les PDFs (href="pdfs/Siman_XXX_*.pdf") sont à inclure même si le PDF n'existe pas encore — l'admin les générera plus tard. Utilise le pattern de nommage du siman 242.
8. **Aucun lien factice** : si tu ne sais pas, tu omets, tu n'inventes pas d'URL.
9. **Disclaimer** : à la fin de chaque niveau, le disclaimer "Cette analyse présente ce que disent les sources. Ce n'est pas un psak halakha. Pour ton cas concret, consulte ton Rav."

FORMAT DE SORTIE : tu réponds UNIQUEMENT avec le code HTML complet du fichier demandé, depuis <!DOCTYPE html> jusqu'à </html>. Pas de bloc markdown, pas de commentaire avant ou après, juste le HTML brut.

==================================================================
GABARIT DE RÉFÉRENCE — SIMAN 242 (à reproduire fidèlement en l'adaptant)
==================================================================

--- index.html (siman-242) ---
${template['index.html']}

--- niveau-1-base.html (siman-242) ---
${template['niveau-1-base.html']}

--- niveau-2-lamdan.html (siman-242) ---
${template['niveau-2-lamdan.html']}

--- niveau-3-synthese.html (siman-242) ---
${template['niveau-3-synthese.html']}

==================================================================
NOUVEAU SIMAN À GÉNÉRER — MÉTADONNÉES
==================================================================

Numéro arabe : ${meta.siman}
Numéro hébreu : ${meta.num_he}
Titre hébreu : ${meta.title_he}
Titre français : ${meta.title_fr}
Sous-titre : ${meta.subtitle || ''}
Section : ${meta.section || 'orah-haim'} / ${meta.chapter || 'hilkhot-shabbat'}

Texte hébreu original (Mehaber) :
${meta.hebrew_text}

${meta.hagahot ? `Hagahot du Rama :\n${meta.hagahot}` : ''}

${meta.translation_fr ? `Traduction française fournie :\n${meta.translation_fr}` : ''}

${meta.mareh_mekomot_text ? `\n==================================================================\nMARAH MEKOMOT — sources Sefaria résolues automatiquement (à intégrer)\n==================================================================\n${meta.mareh_mekomot_text}` : ''}`;
}

function buildUserPromptForFile(target, meta) {
  return `Génère maintenant le fichier **${target.file}** du siman ${meta.siman}.

Rôle de ce fichier : ${target.role}

Reprends EXACTEMENT la même structure que le \`${target.file}\` de référence (siman 242), avec les mêmes sections, mêmes classes CSS, même profondeur pédagogique. Adapte le contenu au nouveau siman ${meta.siman} (${meta.title_he} / ${meta.title_fr}) en t'appuyant sur :
- le texte hébreu fourni
- la traduction (à générer ou à utiliser si fournie)
- les sources mareh mekomot fournies (à citer dans les sections adéquates)

Liens internes attendus dans ce fichier :
- Vers les autres niveaux : ./niveau-1-base.html, ./niveau-2-lamdan.html, ./niveau-3-synthese.html, ./index.html
- Vers la home : ../../../index.html
- Vers le chat : ../../../chat.html
- Vers la liste des simanim de shabbat : ../index.html
- PDF : pdfs/Siman_${meta.siman}_Seif_Alef_Niveau1_Base.pdf (et équivalents par niveau, comme dans siman 242)

Réponds UNIQUEMENT avec le HTML complet — depuis <!DOCTYPE html> jusqu'à </html>. Pas de markdown, pas d'explication.`;
}

async function generateOneFile(client, target, meta, template) {
  const message = await client.messages.create({
    model: MODEL,
    max_tokens: MAX_OUTPUT_TOKENS,
    system: [
      {
        type: 'text',
        text: buildSystemPrompt(template, meta),
        cache_control: { type: 'ephemeral' },
      },
    ],
    messages: [
      { role: 'user', content: buildUserPromptForFile(target, meta) },
    ],
  });

  let html = message.content
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('\n')
    .trim();

  // Strip éventuel bloc markdown au cas où Claude désobéit
  const fence = html.match(/```(?:html)?\s*([\s\S]*?)```/);
  if (fence) html = fence[1].trim();

  // Sanity check : doit commencer par <!DOCTYPE
  if (!/^<!DOCTYPE/i.test(html)) {
    // Trouver le premier <!DOCTYPE et tronquer
    const idx = html.search(/<!DOCTYPE/i);
    if (idx >= 0) html = html.slice(idx);
  }

  return { html, usage: message.usage };
}

async function resolveMarehMekomot(refs) {
  if (!Array.isArray(refs) || refs.length === 0) return [];
  // On limite à 12 refs pour ne pas exploser la latence
  const limited = refs.slice(0, 12);
  const results = await Promise.all(limited.map(ref => fetchSefariaText(ref)));
  return results.filter(r => r && (r.hebrew || r.english));
}

function formatMarehMekomot(resolved) {
  if (resolved.length === 0) return '';
  return resolved
    .map(r => {
      const url = `https://www.sefaria.org/${r.ref.replace(/ /g, '_')}`;
      return `[${r.ref}] ${r.title || ''}\nLien : ${url}\nHébreu : ${r.hebrew.slice(0, 1500)}\nAnglais : ${(r.english || '').slice(0, 800)}`;
    })
    .join('\n\n');
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  const auth = checkAuth(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY non configuré côté serveur' });
  }

  try {
    const meta = req.body || {};
    const required = ['siman', 'num_he', 'title_he', 'title_fr', 'hebrew_text'];
    for (const k of required) {
      if (!meta[k] || typeof meta[k] !== 'string') {
        return res.status(400).json({ error: `Champ requis manquant : ${k}` });
      }
    }

    // 1. Mareh mekomot — résolution Sefaria si refs fournies
    const resolved = await resolveMarehMekomot(meta.refs || []);
    meta.mareh_mekomot_text = formatMarehMekomot(resolved);

    // 2. Charger le gabarit (siman-242)
    const template = loadTemplate();

    // 3. Générer chaque fichier (en série pour bénéficier au max du cache prompt)
    const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    const files = {};
    let totalUsage = { input_tokens: 0, output_tokens: 0, cache_read_tokens: 0, cache_creation_tokens: 0 };

    for (const target of TARGETS) {
      const { html, usage } = await generateOneFile(client, target, meta, template);
      files[target.file] = html;
      totalUsage.input_tokens += usage.input_tokens || 0;
      totalUsage.output_tokens += usage.output_tokens || 0;
      totalUsage.cache_read_tokens += usage.cache_read_input_tokens || 0;
      totalUsage.cache_creation_tokens += usage.cache_creation_input_tokens || 0;
    }

    return res.status(200).json({
      ok: true,
      model: MODEL,
      siman: meta.siman,
      files,
      mareh_mekomot: resolved.map(r => ({
        ref: r.ref,
        title: r.title || r.ref,
        hebrew_preview: (r.hebrew || '').slice(0, 200),
        url: `https://www.sefaria.org/${r.ref.replace(/ /g, '_')}`,
      })),
      usage: totalUsage,
    });
  } catch (err) {
    console.error('[admin/generate-siman] error:', err);
    const msg = err.message || 'Erreur génération siman';
    const status = err.status || 500;
    return res.status(status).json({ error: msg });
  }
}
