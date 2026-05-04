// Endpoint admin : transcription de photos du Choulchan Aroukh via Claude Vision.
//
// Reçoit N photos (JPG / PNG en base64), les envoie à Claude Opus 4.7 avec un
// prompt halakhique précis qui demande une transcription FIDÈLE de l'hébreu
// (avec nikoud si présent, ponctuation, abréviations classiques préservées).
// Retourne pour chaque photo le texte transcrit + un texte fusionné prêt à
// être édité dans l'admin.
//
// Auth : header Authorization: Bearer <ADMIN_PASSWORD>
//
// POST /api/admin/transcribe-photos
//   body : {
//     images: [{ data: <base64 sans prefix>, mimeType: "image/jpeg" | "image/png" }],
//     siman?: string,    // optionnel — si fourni, ajouté au prompt pour aider l'OCR
//     hint?: string      // optionnel — ex: "Choulchan Aroukh OH 247, seif 1 + Hagahot Rama"
//   }
//
//   réponse : {
//     ok: true,
//     pages: [{ index, hebrew, hagahot?, notes? }],
//     merged: "<texte hébreu fusionné>",
//     model: "claude-opus-4-7",
//     usage: { input_tokens, output_tokens }
//   }

import Anthropic from '@anthropic-ai/sdk';

export const config = {
  api: {
    // Vercel impose une limite dure ~4.5 Mo sur le body des fonctions Node.
    // → le client envoie UNE photo à la fois (en parallèle), pas un batch.
    bodyParser: { sizeLimit: '4mb' },
  },
};

const MODEL = 'claude-opus-4-7'; // Vision-capable. Aligné avec api/chat.js du projet.
const MAX_IMAGES = 8; // garde-fou si quelqu'un envoie quand même un batch
const MAX_IMAGE_BYTES = 3 * 1024 * 1024; // 3 Mo par image (raw bytes après b64 decode)

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

function buildSystemPrompt() {
  return `Tu es un expert en transcription de textes halakhiques imprimés en hébreu (Choulchan Aroukh, Hagahot du Rama, Mishna Beroura, Beour Halakha, Beit Yossef, etc.).

RÈGLES DE TRANSCRIPTION :
1. Transcris MOT À MOT l'hébreu visible sur la photo, sans paraphraser.
2. Préserve le nikoud / les téamim s'ils sont visibles.
3. Préserve EXACTEMENT les abréviations classiques (ע״כ, וכו׳, ז״ל, רמ״א, מהרי״ק, וכיו״ב, etc.) avec les guillemets-rabbiniques (״ pour double, ׳ pour simple).
4. Sépare les seifim avec une ligne vide entre chaque, et indique le numéro de seif quand il est visible.
5. Si la page contient à la fois le **Mehaber** et les **Hagahot du Rama**, distingue-les clairement :
   - le texte du Mehaber dans le champ "hebrew"
   - les hagahot du Rama dans le champ "hagahot"
6. Si tu vois un commentaire (Mishna Beroura, Beour Halakha, Choulchan Aroukh haRav, etc.), mets-le dans "notes" avec son nom.
7. N'INVENTE RIEN. Si une lettre est illisible, mets [?]. Si un mot entier est illisible, mets [...].
8. Pas de traduction — uniquement l'hébreu original.

FORMAT DE RÉPONSE — réponds UNIQUEMENT avec un JSON valide, sans texte avant/après, sans \`\`\`json :

{
  "hebrew": "le texte du Mehaber, en hébreu",
  "hagahot": "les hagahot du Rama si visibles, sinon chaîne vide",
  "notes": "commentaires identifiés (Mishna Beroura, etc.) avec leur nom, ou chaîne vide",
  "confidence": "high|medium|low",
  "warnings": ["liste de problèmes si applicable, ex: 'page coupée à droite', 'photo floue en bas'"]
}`;
}

function buildUserPromptForImage(meta) {
  const ctx = [];
  if (meta?.siman) ctx.push(`Siman : ${meta.siman}`);
  if (meta?.hint) ctx.push(`Indication : ${meta.hint}`);
  const ctxStr = ctx.length ? `\n\nContexte fourni par l'admin :\n${ctx.join('\n')}` : '';
  return `Transcris fidèlement le texte hébreu visible sur cette photo.${ctxStr}

Rappel : réponds UNIQUEMENT avec le JSON spécifié, rien d'autre.`;
}

function safeJsonParse(text) {
  // Claude répond parfois avec du texte autour ou un bloc markdown — on extrait.
  if (!text) return null;
  // Bloc \`\`\`json ... \`\`\`
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fence) {
    try { return JSON.parse(fence[1].trim()); } catch {}
  }
  // Première accolade jusqu'à la dernière
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start >= 0 && end > start) {
    try { return JSON.parse(text.slice(start, end + 1)); } catch {}
  }
  // Tentative directe
  try { return JSON.parse(text); } catch {}
  return null;
}

async function transcribeOne(client, image, meta, index) {
  const message = await client.messages.create({
    model: MODEL,
    max_tokens: 4096,
    system: buildSystemPrompt(),
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: image.mimeType || 'image/jpeg',
              data: image.data,
            },
          },
          { type: 'text', text: buildUserPromptForImage(meta) },
        ],
      },
    ],
  });

  const text = message.content
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('\n');

  const parsed = safeJsonParse(text) || {};
  return {
    index,
    hebrew: (parsed.hebrew || '').trim(),
    hagahot: (parsed.hagahot || '').trim(),
    notes: (parsed.notes || '').trim(),
    confidence: parsed.confidence || 'unknown',
    warnings: Array.isArray(parsed.warnings) ? parsed.warnings : [],
    raw_preview: text.slice(0, 200),
    usage: message.usage,
  };
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
    const { images, siman, hint } = req.body || {};
    if (!Array.isArray(images) || images.length === 0) {
      return res.status(400).json({ error: 'Champ "images" manquant ou vide' });
    }
    if (images.length > MAX_IMAGES) {
      return res.status(400).json({ error: `Maximum ${MAX_IMAGES} photos par requête` });
    }

    // Validation rapide de chaque image
    for (const [i, img] of images.entries()) {
      if (!img?.data || typeof img.data !== 'string') {
        return res.status(400).json({ error: `Image ${i + 1} : champ "data" (base64) manquant` });
      }
      // Strip data-URL prefix au cas où
      img.data = img.data.replace(/^data:image\/[a-zA-Z]+;base64,/, '');
      // Estimation taille (b64 → bytes ≈ length × 3/4)
      const estBytes = Math.floor(img.data.length * 0.75);
      if (estBytes > MAX_IMAGE_BYTES) {
        return res.status(400).json({
          error: `Image ${i + 1} trop lourde (~${(estBytes / 1024 / 1024).toFixed(1)} Mo). Max ${MAX_IMAGE_BYTES / 1024 / 1024} Mo. Compresse côté client.`,
        });
      }
      if (!img.mimeType) img.mimeType = 'image/jpeg';
    }

    const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
    const meta = { siman, hint };

    // On traite en parallèle (max 8 photos donc safe). Chaque photo = un appel.
    const pages = await Promise.all(
      images.map((img, i) => transcribeOne(client, img, meta, i + 1))
    );

    // Texte fusionné : on concatène hebrew + hagahot de chaque page,
    // séparés par des marqueurs lisibles que l'admin pourra ajuster.
    const merged = pages
      .map(p => {
        const parts = [];
        parts.push(`=== Page ${p.index} ===`);
        if (p.hebrew) parts.push(p.hebrew);
        if (p.hagahot) parts.push(`\n[הגהות הרמ״א]\n${p.hagahot}`);
        if (p.notes) parts.push(`\n[הערות / מ״ב]\n${p.notes}`);
        return parts.join('\n');
      })
      .join('\n\n');

    const totalUsage = pages.reduce(
      (acc, p) => ({
        input_tokens: acc.input_tokens + (p.usage?.input_tokens || 0),
        output_tokens: acc.output_tokens + (p.usage?.output_tokens || 0),
      }),
      { input_tokens: 0, output_tokens: 0 }
    );

    return res.status(200).json({
      ok: true,
      model: MODEL,
      pages: pages.map(p => ({
        index: p.index,
        hebrew: p.hebrew,
        hagahot: p.hagahot,
        notes: p.notes,
        confidence: p.confidence,
        warnings: p.warnings,
      })),
      merged,
      usage: totalUsage,
    });
  } catch (err) {
    console.error('[admin/transcribe-photos] error:', err);
    const msg = err.message || 'Erreur transcription';
    const status = err.status || 500;
    return res.status(status).json({ error: msg });
  }
}
