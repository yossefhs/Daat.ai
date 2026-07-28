// Réécriture de requête halakhique (query rewrite) avant la recherche corpus.
//
// La recherche BM25 (_corpus-search.js) est LEXICALE : elle compare des mots, pas
// du sens. Un utilisateur écrit « j'ai un plat de petits pois avec des pommes de
// terre, je veux retirer la pomme de terre » ; le corpus, lui, parle de « borer,
// okhel, pesolet ». Le lexique de synonymes écrit à la main plafonne (~40 % de
// bons résultats sur des questions inédites) et ne peut pas couvrir toute la langue.
//
// Ce module fait reformuler la question par Haiku (rapide, ~0,5-1 s) en QUELQUES
// mots-clés halakhiques (la mélakha / le concept / la racine hébraïque). Ces
// mots-clés sont AJOUTÉS à la question originale avant la recherche — jamais
// substitués : même si la reformulation se trompe, les tokens d'origine comptent
// toujours, et un bon mot-clé (« borer ») domine par son IDF élevé.
//
// C'est le correctif de la cause racine de l'incident borer : le corpus contenait
// la réponse, mais la recherche ne la retrouvait pas.

const REWRITE_MODEL = 'claude-haiku-4-5';

function systemPrompt(section) {
  const domain = section === 'yoreh-deah'
    ? "le Yoreh De'ah (cacheroute : bassar be-halav, taarovot, ben yomo, nat bar nat ; ou Nidah / Taharat haMishpacha : ketamim, harchakot, hefsek tahara, vesatot, tevila)"
    : "les hilkhot Shabbat (borer, bishoul, hazara, hatmana, mouktsé, tohen, sekhita, tolesh, kotev, koshér, hotsaa, tsida, refoua, hadlaka…)";
  const examples = section === 'yoreh-deah'
    ? `- « puis-je manger du fromage juste après de la viande ? » → bassar be-halav attente viande lait המתנה בשר בחלב
- « une goutte de lait est tombée dans la casserole de viande » → taarovet bassar be-halav bitoul בשר בחלב תערובת`
    : `- « j'ai un plat de petits pois avec des pommes de terre, je veux retirer la pomme de terre » → borer trier okhel pesolet mélange deux espèces בורר
- « puis-je remettre le plat sur la plaque le samedi ? » → hazara plata bishoul kira חזרה
- « ma femme peut-elle sortir avec ses bijoux dehors ? » → hotsaa bijoux ornement takhchit רשות הרבים`;

  return `Tu es un assistant de recherche halakhique. On te donne UNE question d'utilisateur, en langage courant, sur ${domain}.

TA SEULE TÂCHE : identifier la mélakha (ou le principe halakhique) et le concept en jeu, puis produire 4 à 8 MOTS-CLÉS de recherche — le nom de la mélakha/du principe, les concepts halakhiques associés, et la racine hébraïque si elle est évidente.

RÈGLES ABSOLUES :
- Tu ne réponds PAS à la question. Tu n'écris AUCUNE phrase, aucune explication.
- Tu n'inventes AUCUNE halakha et ne tranches rien.
- Sortie : UNIQUEMENT les mots-clés séparés par des espaces, sur une seule ligne. Rien d'autre.
- Les noms d'aliments, d'objets ou de marques ne sont PAS de bons mots-clés (le corpus parle de la mélakha, pas du légume) — ne les répète pas, traduis-les en concept.
- Si tu n'identifies aucun concept halakhique clair, renvoie une ligne vide.

EXEMPLES :
${examples}`;
}

/**
 * Reformule une question en mots-clés halakhiques via Haiku.
 * @returns {Promise<{keywords: string, latencyMs: number} | null>} null si échec/vide.
 */
export async function expandHalakhicQuery(client, question, { section = 'orach-chaim', signal } = {}) {
  if (!client || !question) return null;
  const t0 = Date.now();
  try {
    const resp = await client.messages.create({
      model: REWRITE_MODEL,
      max_tokens: 48,
      system: systemPrompt(section),
      messages: [{ role: 'user', content: question.slice(0, 800) }],
    }, signal ? { signal } : undefined);

    const raw = (resp.content || [])
      .filter((b) => b.type === 'text')
      .map((b) => b.text)
      .join(' ')
      .trim();

    // Garde-fou : on ne garde qu'une seule ligne courte de mots-clés. Si Haiku
    // dérape en phrase (malgré la consigne), on tronque au premier saut de ligne
    // et on refuse si ça ressemble à une phrase (ponctuation de fin, « . »).
    const firstLine = raw.split('\n')[0].trim();
    if (!firstLine) return null;
    if (firstLine.length > 160) return null;               // trop long = probablement une phrase
    const keywords = firstLine.replace(/[«»"“”]/g, '').trim();
    if (!keywords) return null;

    return { keywords, latencyMs: Date.now() - t0 };
  } catch (err) {
    console.warn('[query-rewrite] échec (on continue sans):', err?.message || err);
    return null;
  }
}
