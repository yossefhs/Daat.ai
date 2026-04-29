// Endpoint admin pour gérer le corpus dynamique DAAT.AI
//
// Auth : header Authorization: Bearer <ADMIN_PASSWORD>
//   où ADMIN_PASSWORD est défini comme variable d'environnement Vercel.
//
// Endpoints (selon la méthode HTTP) :
//   GET  /api/admin/corpus            → liste les entrées dynamiques
//   POST /api/admin/corpus            → ajoute une entrée (body JSON)
//   DELETE /api/admin/corpus?id=xxx   → supprime une entrée

import {
  addDynamicEntry,
  deleteDynamicEntry,
  listDynamicEntries,
} from '../_corpus.js';

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

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Auth obligatoire pour toutes les méthodes
  const auth = checkAuth(req);
  if (!auth.ok) {
    return res.status(auth.status).json({ error: auth.error });
  }

  try {
    if (req.method === 'GET') {
      const entries = await listDynamicEntries();
      return res.status(200).json({ entries, count: entries.length });
    }

    if (req.method === 'POST') {
      const body = req.body || {};

      // Validation minimale
      const required = ['title', 'content'];
      for (const k of required) {
        if (!body[k] || typeof body[k] !== 'string' || body[k].trim().length === 0) {
          return res.status(400).json({ error: `Le champ "${k}" est requis (string non vide)` });
        }
      }

      // Limites pour éviter les abus
      if (body.title.length > 300) {
        return res.status(400).json({ error: 'Titre trop long (max 300 caractères)' });
      }
      if (body.content.length > 50000) {
        return res.status(400).json({ error: 'Contenu trop long (max 50000 caractères)' });
      }

      const entry = {
        id: body.id || undefined, // sinon généré auto
        title: body.title.trim(),
        section: body.section || 'orah-haim',
        chapter: body.chapter || '',
        siman: body.siman || '',
        seif: body.seif || '',
        level: body.level || 'all',
        tags: Array.isArray(body.tags) ? body.tags : (typeof body.tags === 'string' ? body.tags.split(',').map(t => t.trim()).filter(Boolean) : []),
        sources: Array.isArray(body.sources) ? body.sources : [],
        internalLinks: Array.isArray(body.internalLinks) ? body.internalLinks : [],
        summary: body.summary || '',
        content: body.content,
      };

      const saved = await addDynamicEntry(entry);
      return res.status(201).json({ ok: true, entry: saved });
    }

    if (req.method === 'DELETE') {
      const id = req.query?.id || (req.url.match(/[?&]id=([^&]+)/) || [])[1];
      if (!id) {
        return res.status(400).json({ error: 'Paramètre "id" requis' });
      }
      await deleteDynamicEntry(decodeURIComponent(id));
      return res.status(200).json({ ok: true });
    }

    return res.status(405).json({ error: 'Méthode non autorisée' });
  } catch (err) {
    console.error('[admin/corpus] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur interne' });
  }
}
