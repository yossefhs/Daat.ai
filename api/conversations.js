// Endpoint de synchronisation des conversations IA — par utilisateur.
//
// Auth : cookie daat_session (JWT signé) → getUserFromRequest → { email }
//
// Stockage : Vercel KV (Upstash Redis)
//   - Hash `convs:{email}` mappe `convId` → JSON.stringify(conversation)
//   - Une conversation = { id, title, messages, updatedAt, niveau, minhag, createdAt }
//
// Endpoints :
//   GET    /api/conversations        → { conversations: [...] } (triées par updatedAt desc)
//   POST   /api/conversations        → upsert ; body = conversation complète
//   DELETE /api/conversations?id=xxx → supprime une conversation
//   DELETE /api/conversations?all=1  → supprime tout (rare ; demande explicite)

import { kv } from './_kv.js';
import { getUserFromRequest, setCorsHeaders } from './_auth.js';

const MAX_CONVERSATIONS = 100;        // garde-fou — 100 conversations max par user
const MAX_MESSAGES_PER_CONV = 200;    // tronque les conversations très longues
const MAX_CONTENT_PER_MESSAGE = 60000; // 60k chars ≈ 15k tokens — large, mais évite les abus
const MAX_TITLE_LEN = 200;

function key(email) {
  // On lowercase pour éviter les doublons de casse (Outlook, etc.)
  return `convs:${email.toLowerCase().trim()}`;
}

function sanitizeConversation(c) {
  if (!c || typeof c !== 'object') return null;
  if (!c.id || typeof c.id !== 'string') return null;

  const messages = Array.isArray(c.messages) ? c.messages : [];
  const cleanMessages = messages
    .slice(-MAX_MESSAGES_PER_CONV) // garde les N derniers messages si dépassement
    .map(m => {
      if (!m || typeof m !== 'object') return null;
      const role = m.role === 'user' || m.role === 'assistant' ? m.role : null;
      if (!role) return null;
      let content = '';
      if (typeof m.content === 'string') content = m.content;
      else if (Array.isArray(m.content)) {
        content = m.content
          .filter(b => b && b.type === 'text' && typeof b.text === 'string')
          .map(b => b.text)
          .join('\n');
      }
      if (content.length > MAX_CONTENT_PER_MESSAGE) {
        content = content.slice(0, MAX_CONTENT_PER_MESSAGE) + '\n[…tronqué]';
      }
      return { role, content };
    })
    .filter(Boolean);

  const out = {
    id: c.id.slice(0, 80),
    title: typeof c.title === 'string' ? c.title.slice(0, MAX_TITLE_LEN) : 'Conversation',
    messages: cleanMessages,
    updatedAt: typeof c.updatedAt === 'number' ? c.updatedAt : Date.now(),
    createdAt: typeof c.createdAt === 'number' ? c.createdAt : (c.updatedAt || Date.now()),
  };
  if (typeof c.niveau === 'string') out.niveau = c.niveau.slice(0, 30);
  if (typeof c.minhag === 'string') out.minhag = c.minhag.slice(0, 30);
  return out;
}

function parseValue(raw) {
  // le client Redis déserialise déjà parfois ; on est défensif.
  if (typeof raw === 'string') {
    try { return JSON.parse(raw); } catch { return null; }
  }
  if (raw && typeof raw === 'object') return raw;
  return null;
}

async function listConversations(email) {
  const all = await kv.hgetall(key(email));
  if (!all || typeof all !== 'object') return [];
  const arr = Object.values(all)
    .map(parseValue)
    .filter(Boolean);
  arr.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
  return arr;
}

async function upsertConversation(email, conv) {
  const clean = sanitizeConversation(conv);
  if (!clean) throw new Error('Conversation invalide');

  // Garde-fou : si on dépasse MAX_CONVERSATIONS, on supprime les plus anciennes
  const existing = await kv.hgetall(key(email));
  const ids = existing ? Object.keys(existing) : [];
  if (ids.length >= MAX_CONVERSATIONS && !existing[clean.id]) {
    // Lister + trier par updatedAt asc → supprimer les plus vieilles
    const arr = ids
      .map(id => ({ id, conv: parseValue(existing[id]) }))
      .filter(x => x.conv)
      .sort((a, b) => (a.conv.updatedAt || 0) - (b.conv.updatedAt || 0));
    const toDelete = arr.slice(0, ids.length - MAX_CONVERSATIONS + 1).map(x => x.id);
    if (toDelete.length > 0) {
      await kv.hdel(key(email), ...toDelete);
    }
  }

  await kv.hset(key(email), { [clean.id]: JSON.stringify(clean) });
  return clean;
}

async function deleteOne(email, id) {
  if (!id) throw new Error('id requis');
  await kv.hdel(key(email), id);
}

async function deleteAll(email) {
  await kv.del(key(email));
}

export default async function handler(req, res) {
  setCorsHeaders(req, res);
  if (req.method === 'OPTIONS') return res.status(200).end();

  const user = getUserFromRequest(req);
  if (!user) return res.status(401).json({ error: 'Non authentifié' });

  try {
    if (req.method === 'GET') {
      const conversations = await listConversations(user.email);
      return res.status(200).json({ ok: true, conversations });
    }

    if (req.method === 'POST') {
      const conv = req.body;
      const saved = await upsertConversation(user.email, conv);
      return res.status(200).json({ ok: true, conversation: saved });
    }

    if (req.method === 'DELETE') {
      // ?all=1 → wipe complet (avec confirmation côté client)
      if (req.query?.all === '1') {
        await deleteAll(user.email);
        return res.status(200).json({ ok: true, deleted: 'all' });
      }
      const id = req.query?.id;
      if (!id) return res.status(400).json({ error: 'id ou all=1 requis' });
      await deleteOne(user.email, id);
      return res.status(200).json({ ok: true, deleted: id });
    }

    return res.status(405).json({ error: 'Méthode non supportée' });
  } catch (err) {
    console.error('[api/conversations] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}

export const config = {
  api: {
    bodyParser: { sizeLimit: '1mb' }, // une conversation longue ≈ 200k chars max
  },
};
