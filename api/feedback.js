// POST /api/feedback — Stocke un retour utilisateur sur une réponse de Daat
//
// Body JSON :
//   {
//     rating: '👍' | '👎',                        (obligatoire)
//     question: string,                            (la question utilisateur)
//     answer: string,                              (la réponse de Daat évaluée)
//     niveau?: string, minhag?: string,            (profil de session)
//     comment?: string,                            (commentaire libre, surtout si 👎)
//     conversationId?: string,                     (id de la conversation côté client)
//     messageIndex?: number,                       (index du message dans la conv)
//     page?: string                                (URL de la page d'origine)
//   }
//
// Réponse : { ok: true, id: 'fb-...' }
//
// Stockage Vercel KV :
//   - feedback:{id}    → l'objet complet
//   - feedback:list    → liste des ids (les 1000 plus récents)

import { kv } from '@vercel/kv';

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST uniquement' });
  }

  try {
    const body = req.body || {};
    const { rating, question, answer, niveau, minhag, comment, conversationId, messageIndex, page } = body;

    if (!rating || !['👍', '👎'].includes(rating)) {
      return res.status(400).json({ error: 'rating doit être "👍" ou "👎"' });
    }
    if (!question && !answer) {
      return res.status(400).json({ error: 'question ou answer requis' });
    }

    const id = `fb-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const entry = {
      id,
      rating,
      question: typeof question === 'string' ? question.slice(0, 2000) : '',
      answer: typeof answer === 'string' ? answer.slice(0, 6000) : '',
      niveau: niveau || null,
      minhag: minhag || null,
      comment: typeof comment === 'string' ? comment.slice(0, 1000) : '',
      conversationId: conversationId || null,
      messageIndex: typeof messageIndex === 'number' ? messageIndex : null,
      page: typeof page === 'string' ? page.slice(0, 200) : '',
      createdAt: Date.now(),
      userAgent: (req.headers['user-agent'] || '').slice(0, 200),
      ip: (req.headers['x-forwarded-for'] || req.connection?.remoteAddress || '').toString().slice(0, 50),
    };

    // Sauvegarde dans KV
    await kv.set(`feedback:${id}`, entry);
    // Index list (LIFO)
    await kv.lpush('feedback:list', id);
    await kv.ltrim('feedback:list', 0, 999);

    return res.status(200).json({ ok: true, id });
  } catch (err) {
    console.error('[feedback] error:', err);
    return res.status(500).json({ error: err.message || 'Erreur serveur' });
  }
}
