// Endpoint admin pour extraire le texte d'un PDF.
// Le PDF est envoyé en base64 dans le body JSON (limite Vercel ~4.5 Mo
// → ~3 Mo de PDF en base64). Le texte extrait est renvoyé au front,
// qui pré-remplit le formulaire "Ajouter au corpus" pour relecture/édition
// avant sauvegarde dans Vercel KV.
//
// Auth : header Authorization: Bearer <ADMIN_PASSWORD>
//
// POST /api/admin/upload-pdf
//   body : { filename, pdfBase64, meta?: { siman, seif, level, title } }
//   response : { ok, text, pages, info, suggested: { title, summary, tags } }

import { extractText, getDocumentProxy } from 'unpdf';

export const config = {
  api: {
    bodyParser: { sizeLimit: '6mb' },
  },
};

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

function suggestMetadata(text, filename, meta) {
  // Extrait quelques heuristiques utiles depuis le texte + le nom de fichier
  const cleanFilename = (filename || '').replace(/\.pdf$/i, '').replace(/[_-]+/g, ' ');

  // Première ligne non-vide de >5 caractères → titre suggéré
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  const firstReal = lines.find(l => l.length > 8 && l.length < 200) || cleanFilename || 'Document PDF';

  // Résumé : 1-2 premières phrases (max 250 caractères)
  const flat = text.replace(/\s+/g, ' ').trim();
  const sentences = flat.split(/(?<=[.!?])\s+/);
  let summary = '';
  for (const s of sentences) {
    if ((summary + ' ' + s).length > 250) break;
    summary = (summary + ' ' + s).trim();
  }

  // Tags suggérés via mots-clés fréquents
  const keywords = ['shabbat', 'siman', 'halakha', 'rama', 'choulchan', 'rambam',
                    'mishna', 'talmud', 'pesak', 'ashkenaze', 'sefarade', 'habad',
                    'mikvé', 'cacherout', 'tefilin', 'bénédiction', 'prière'];
  const lower = text.toLowerCase();
  const tags = keywords.filter(k => lower.includes(k));
  if (meta?.siman) tags.unshift(`siman-${meta.siman}`);

  return {
    title: meta?.title || firstReal,
    summary: summary || `Document importé depuis ${filename}`,
    tags: [...new Set(tags)].slice(0, 8),
  };
}

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST uniquement' });

  // Auth
  const auth = checkAuth(req);
  if (!auth.ok) return res.status(auth.status).json({ error: auth.error });

  try {
    const { pdfBase64, filename, meta } = req.body || {};
    if (!pdfBase64 || typeof pdfBase64 !== 'string') {
      return res.status(400).json({ error: 'pdfBase64 manquant ou invalide' });
    }

    // Strip data URL prefix si présent
    const base64Clean = pdfBase64.replace(/^data:application\/pdf;base64,/, '');
    let buffer;
    try {
      buffer = Buffer.from(base64Clean, 'base64');
    } catch {
      return res.status(400).json({ error: 'Base64 invalide' });
    }

    if (buffer.length < 100) {
      return res.status(400).json({ error: 'Fichier trop petit ou vide' });
    }
    if (buffer.length > 5 * 1024 * 1024) {
      return res.status(400).json({ error: 'PDF trop lourd (max 5 Mo). Compresse ou découpe le fichier.' });
    }

    // Extraction via unpdf (pdfjs sous le capot, ESM-native, friendly serverless)
    const uint8 = new Uint8Array(buffer);
    const pdf = await getDocumentProxy(uint8);
    const { totalPages, text: pages } = await extractText(pdf, { mergePages: false });

    // text est un array de pages — on les joint en gardant des séparateurs
    const text = (Array.isArray(pages) ? pages : [pages])
      .map((p, i) => `\n\n--- Page ${i + 1} ---\n\n${p}`)
      .join('')
      .trim();

    if (!text || text.length < 20) {
      return res.status(422).json({
        error: 'Aucun texte extractible — PDF scanné (image) ou protégé. Utilise un OCR avant import.',
      });
    }

    const suggested = suggestMetadata(text, filename, meta);
    const info = (await pdf.getMetadata?.().catch(() => null))?.info || {};

    return res.status(200).json({
      ok: true,
      filename: filename || 'document.pdf',
      pages: totalPages,
      text,
      info,
      suggested,
    });
  } catch (err) {
    console.error('[admin/upload-pdf] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur extraction PDF' });
  }
}
