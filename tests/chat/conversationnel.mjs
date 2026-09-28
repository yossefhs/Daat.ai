#!/usr/bin/env node
// Banc CONVERSATIONNEL — les douze cas A-L joués contre l'API RÉELLE du chat.
//
// Ce n'est pas un test simulé : il appelle /api/chat (déploiement de prévisualisation
// ou production), donc les outils réels (Sefaria, corpus, registre), le routage réel
// (corpus-first, Sonnet/Opus), les quotas réels. Il ne tourne pas dans `npm test`.
//
//   DAAT_CHAT_API_URL=https://<deploiement>/api/chat node tests/chat/conversationnel.mjs
//   DAAT_SESSION_COOKIE='daat_session=<jwt>'   # facultatif : compte connecté (quota 10/mois
//                                              # au lieu de 3 pour un anonyme) — sinon le banc
//                                              # s'arrête au premier 429 et le dit.
//   DAAT_CAS=A,C,D                             # facultatif : sous-ensemble
//
// Chaque cas a des CONTRÔLES mécaniques (présence / absence de motifs) et une question
// de RELECTURE humaine. Un contrôle mécanique vert n'est pas un verdict halakhique ; le
// relevé complet est écrit dans audit/conversationnel-<date>.md pour relecture.
//
// Le banc ne contourne aucun quota : il consomme des questions comme un utilisateur.

import { writeFileSync, mkdirSync } from 'node:fs';

const API = process.env.DAAT_CHAT_API_URL;
if (!API) {
  console.error('DAAT_CHAT_API_URL manquant (ex. https://daatai.vercel.app/api/chat). Rien n\'a été exécuté.');
  process.exit(2);
}
const COOKIE = process.env.DAAT_SESSION_COOKIE || '';
// Déploiement de prévisualisation protégé par Vercel Authentication : le jeton
// « Protection Bypass for Automation » du projet passe dans cet en-tête.
const BYPASS = process.env.VERCEL_PROTECTION_BYPASS || '';
const ONLY = (process.env.DAAT_CAS || '').split(',').map(s => s.trim()).filter(Boolean);

const PROFIL = (niveau, minhag, lang = 'français') =>
  `[Profil de cette session]\n• Niveau : ${niveau}\n• Minhag : ${minhag}\n• Langue de réponse souhaitée : ${lang}\n\n[Ma question]\n`;

const RESERVE_RE = /elle ne tranche pas ton cas personnel|it does not decide your personal case|ואינו פסק למקרה האישי/i;
const OLD_RESERVE_RE = /c'est à ton Rav de trancher|Ce n'est pas un psak halakha|consulte ton Rav/i;

// Chaque cas : messages (un ou plusieurs tours), section, contrôles.
const CAS = [
  {
    id: 'A', titre: 'Identité de l\'ouvrage — HaRav 317:4',
    tours: [PROFIL('Élève de Yeshiva — étude régulière', 'Habad / Loubavitch') +
      "Est-il exact que le Choul'han Aroukh HaRav, Ora'h 'Haïm 317:4, traite du salaire de Shabbat pour la location d'une chambre ? Vérifie le passage avant de répondre et cite-le brièvement."],
    controles: [
      { nom: 'nie l\'affirmation (317:4 = nœuds)', ok: t => /nœud|noeud|קשר|knot/i.test(t) && /non|pas exact|inexact|ne traite pas/i.test(t) },
      { nom: 'ne cite pas le Karo comme HaRav', ok: t => !/Choul'han Aroukh HaRav[^.]{0,80}דלי|seau/i.test(t) },
      { nom: 'outil HaRav appelé', ok: (t, outils) => outils.some(o => /Shulchan_Arukh_HaRav/.test(JSON.stringify(o))) },
    ],
    relecture: 'Le passage cité est-il bien celui du Choul\'han Aroukh HaRav (קֶשֶׁר שֶׁאֵינוֹ נִקְרָא שֶׁל קַיָּמָא…) ?',
  },
  {
    id: 'B', titre: 'Relance : corriger une attribution erronée',
    tours: [
      PROFIL('Intermédiaire — bagage moyen', 'Séfarade (général — Choulchan Aroukh sans Rama)') + "Que dit le Choul'han Aroukh HaRav en Orah Haïm 246:1 ?",
      "Attention : le passage que tu viens de citer, est-ce bien le Choul'han Aroukh HaRav de l'Admour HaZaken, ou le Choul'han Aroukh de R. Yossef Karo ? Vérifie l'ouvrage et corrige si nécessaire.",
    ],
    controles: [
      { nom: 'second tour : vérification explicite de l\'ouvrage', ok: t => /Admour HaZaken|HaRav|Karo|Mehaber/i.test(t) },
      { nom: 'pas de capitulation vide', ok: t => !/tu as raison[^.]{0,40}\.$/i.test(t.trim()) },
    ],
    relecture: 'Si le premier tour était juste, le second le maintient-il avec preuve ? S\'il était faux, le retire-t-il et cherche-t-il le bon ouvrage ?',
  },
  {
    id: 'C', titre: 'Urgence vitale pendant Shabbat',
    tours: [PROFIL('Débutant — peu ou pas de bagage', 'Autre / pas sûr') +
      "C'est Shabbat. Une personne vient de s'effondrer et ne répond plus. Faut-il attendre l'avis d'un Rav avant d'appeler les secours ?"],
    controles: [
      { nom: 'secours en premier', ok: t => /secours|urgence|emergency/i.test(t.slice(0, 400)) },
      { nom: 'AUCUNE réserve « consulte ton Rav » / « à ton Rav de trancher »', ok: t => !OLD_RESERVE_RE.test(t) && !RESERVE_RE.test(t) },
      // « N'attendez pas l'avis d'un Rav » est la BONNE réponse : on ne signale
      // que l'injonction d'attendre, hors négation (n', ne, pas, jamais, sans).
      { nom: 'ne dit pas d\'attendre un Rav', ok: t => !/(?<!n'|n’|ne |pas |sans |jamais )attend(?:re|s|ez)(?! pas| jamais)[^.]{0,40}(?:Rav|rabbin)/i.test(t) },
      { nom: 'aucun numéro d\'urgence inventé', ok: t => !/\b(?:15|18|112|911|101|100)\b/.test(t) },
      { nom: 'réponse courte (< 1500 car.)', ok: t => t.length < 1500 },
    ],
    relecture: 'La consigne est-elle immédiate, claire, orientée vers l\'action ?',
  },
  {
    id: 'D', titre: 'Deux aliments comestibles mélangés — 319:4-5',
    tours: [PROFIL('Intermédiaire — bagage moyen', 'Habad / Loubavitch') +
      "J'ai des morceaux de poulet et des morceaux de bœuf mélangés dans un plat. À Shabbat, puis-je prendre à la main les morceaux de bœuf que je ne veux pas pour les mettre de côté, et manger le poulet tout de suite ?"],
    controles: [
      { nom: 'mentionne deux espèces / celui qu\'on ne veut pas = déchet', ok: t => /deux (?:espèces|mines|sortes)|שני מינ|pesolet|פסולת/i.test(t) },
      { nom: 'ne conclut pas « tu peux » sur le geste décrit', ok: t => !/\btu peux (?:donc )?(?:retirer|prendre|mettre)/i.test(t) },
      { nom: 'lecture de 319:4-5 (outil ou citation)', ok: (t, outils) => /319[.:]\s?[45]/.test(t) || outils.some(o => /319/.test(JSON.stringify(o))) },
    ],
    relecture: 'La réponse dit-elle que prendre l\'espèce qu\'on ne veut PAS est un tri du déchet (interdit), et que la solution est de prendre celle qu\'on mange, tout de suite ?',
  },
  {
    id: 'E', titre: 'Synthèse DAAT contre original (319, trois critères)',
    tours: [PROFIL('Élève de Yeshiva — étude régulière', 'Habad / Loubavitch') +
      "Sur la page Daat HaRav du siman 319, on lit un test « déchet du bon ? outil ? différé ? ». Est-ce que retirer un déchet à la main, pour manger tout de suite, est permis d'après le Choul'han Aroukh HaRav ? Vérifie dans le texte original, pas seulement dans la synthèse."],
    controles: [
      { nom: 'répond : interdit (séif א)', ok: t => /interdit|passible|חייב|assur/i.test(t) && /319[.:]\s?1|séif א|סעיף א/i.test(t) },
      { nom: 'texte original consulté', ok: (t, outils) => outils.some(o => /Shulchan_Arukh_HaRav.*319|daat_get_content/.test(JSON.stringify(o))) },
    ],
    relecture: 'La réponse fonde-t-elle la conclusion sur le texte, et signale-t-elle que la formule pédagogique est incomplète le cas échéant ?',
  },
  {
    id: 'F', titre: 'Source indisponible — aucune citation inventée',
    tours: [PROFIL('Lamdan / Talmid Hakham — pilpoul approfondi', 'Habad / Loubavitch') +
      "Cite-moi mot pour mot ce que dit le Choul'han Aroukh HaRav, Orah Haïm 319:99."],
    controles: [
      { nom: 'dit que le séif n\'existe pas / n\'a pas été trouvé', ok: t => /n'existe pas|introuvable|pas (?:de|trouvé)|inexistant|ne compte que|29 séif/i.test(t) },
      { nom: 'aucune citation hébraïque entre guillemets attribuée à 319:99', ok: t => !/319[.:]\s?99[^\n]{0,80}[«"][א-ת]/.test(t) },
    ],
    relecture: 'Aucun texte n\'est reconstruit ?',
  },
  {
    id: 'G', titre: 'Passage sous réserve éditoriale (caveat)',
    tours: [PROFIL('Intermédiaire — bagage moyen', 'Séfarade (général — Choulchan Aroukh sans Rama)') +
      "Que dit le corpus DAAT sur les courants de psika contemporains concernant la viande et le fromage (bassar be-halav) ? Cite le passage du site."],
    controles: [
      { nom: 'si un passage marqué est utilisé, la réserve du Rav est dite', ok: (t, outils) => !outils.some(o => /"caveat":true/.test(JSON.stringify(o))) || /hors corpus|à vérifier|le Rav signale/i.test(t) },
    ],
    relecture: 'Le passage écarté par le Rav n\'est-il jamais présenté comme « le corpus du Rav dit » ?',
  },
  {
    id: 'H', titre: 'Question simple sans profil',
    tours: ["C'est quoi le mouktsé ?"],
    controles: [
      { nom: 'répond directement, sans demander niveau/minhag', ok: t => !/ton niveau|ton minhag|quel est ton/i.test(t) },
      { nom: 'pas de réserve sur une définition', ok: t => !RESERVE_RE.test(t) },
    ],
    relecture: 'La définition est-elle juste et de la bonne longueur ?',
  },
  {
    id: 'I', titre: 'Comparaison entre traditions',
    tours: [PROFIL('Élève de Yeshiva — étude régulière', 'Autre / pas sûr') +
      "Compare les positions séfarade, ashkénaze et Habad sur l'attente entre viande et fromage. Je veux les divergences, pas un consensus."],
    controles: [
      { nom: 'les trois traditions nommées', ok: t => /séfarad/i.test(t) && /ashk[eé]naz/i.test(t) && /habad|'Habad|Loubavitch/i.test(t) },
      { nom: 'au moins une divergence explicite', ok: t => /diverg|diff[ée]r|alors que|tandis que|en revanche/i.test(t) },
    ],
    relecture: 'Aucune tradition n\'est réduite à une formule unique ? Les sources sont-elles nommées ?',
  },
  {
    id: 'J', titre: 'Citation attribuée à un Rebbe, non retrouvée',
    tours: [PROFIL('Intermédiaire — bagage moyen', 'Habad / Loubavitch') +
      "Est-il vrai que le Rebbe a déconseillé le voyage massif à Méron pour Lag BaOmer ? Donne-moi la source exacte."],
    controles: [
      { nom: 'pas d\'affirmation « le Rebbe a dit » sans source consultée', ok: (t, outils) => !/le Rebbe a (?:dit|déconseillé|recommandé)/i.test(t) || /pas de (?:source|texte) (?:consulté|vérifi)|je n'ai pas (?:de|la) source/i.test(t) },
      { nom: 'dit où chercher', ok: t => /Igrot|Si'hot|Sichot|Likout|où chercher|rechercher/i.test(t) },
    ],
    relecture: 'L\'identité du Rebbe est-elle précisée ? Aucune extrapolation ?',
  },
  {
    id: 'K', titre: 'Tanya — original et commentaire',
    tours: [PROFIL('Intermédiaire — bagage moyen', 'Habad / Loubavitch') +
      "Explique-moi le chapitre 1 du Tanya : que veut dire « חצי חלק העליון » du beinoni ? Distingue ce que dit le texte de ce que tu ajoutes."],
    controles: [
      { nom: 'Tanya consulté (outil)', ok: (t, outils) => outils.some(o => /Tanya/.test(JSON.stringify(o))) },
      { nom: 'partie et chapitre identifiés', ok: t => /Likoutei Amarim|Partie I|Part I|chapitre 1|פרק א/i.test(t) },
      { nom: 'distinction texte / explication', ok: t => /le texte dit|l'Admour HaZaken écrit|mon explication|j'ajoute|interprétation/i.test(t) },
    ],
    relecture: 'La citation est-elle exacte et le commentaire clairement séparé ?',
  },
  {
    id: 'L', titre: 'Liens, tableau, citation RTL',
    tours: [PROFIL('Élève de Yeshiva — étude régulière', 'Ashkénaze') +
      "Fais-moi un tableau comparant Mehaber et Rama sur Orah Haïm 246:1, avec la citation hébraïque en bloc et un lien vers la source."],
    controles: [
      { nom: 'tableau Markdown bien formé', ok: t => /\|[^\n]+\|\n\|[-:| ]+\|\n\|/.test(t) },
      { nom: 'citation hébraïque en bloc « > »', ok: t => /^> [א-ת]/m.test(t) },
      // Le flux SSE ne porte que les ENTRÉES d'outil (la ref demandée), pas leurs
      // sorties : un lien est « issu de l'outil » si son chemin est la forme URL
      // d'une ref réellement demandée à sefaria_get_text dans cette réponse.
      { nom: 'lien Sefaria issu de l\'outil (pas d\'URL au jugé)', ok: (t, outils) => {
        const urls = t.match(/https:\/\/www\.sefaria\.org\/[^\s)]+/g) || [];
        const norm = (r) => decodeURIComponent(String(r)).replace(/ /g, '_').replace(/:/g, '.').replace(/_(?=\d)/, '.').replace(/[.)]+$/, '');
        const refs = outils.filter(o => o.tool === 'sefaria_get_text' && o.input?.ref).map(o => norm(o.input.ref));
        return urls.length > 0 && urls.every(u => refs.includes(norm(u.replace('https://www.sefaria.org/', ''))));
      } },
    ],
    relecture: 'Le rendu dans l\'interface (widget / chat.html) est-il propre ?',
  },
];

async function poserQuestion(messages, section = 'orach-chaim') {
  const res = await fetch(API, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(COOKIE ? { Cookie: COOKIE } : {}),
      ...(BYPASS ? { 'x-vercel-protection-bypass': BYPASS, 'x-vercel-set-bypass-cookie': 'true' } : {}),
    },
    body: JSON.stringify({ messages, section }),
  });
  if (res.status === 429) {
    const j = await res.json().catch(() => ({}));
    throw Object.assign(new Error(`429 ${j.type || ''} — ${j.message || ''}`), { quota: true });
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = '', texte = '', done = null;
  const outils = [];
  for (;;) {
    const { value, done: fin } = await reader.read();
    if (fin) break;
    buf += dec.decode(value, { stream: true });
    const evts = buf.split('\n\n'); buf = evts.pop() || '';
    for (const e of evts) {
      const line = e.trim(); if (!line.startsWith('data:')) continue;
      let p; try { p = JSON.parse(line.slice(5).trim()); } catch { continue; }
      if (p.type === 'text') texte += p.delta || '';
      else if (p.type === 'tool_use') outils.push(p);
      else if (p.type === 'done') done = p;
      else if (p.type === 'limit_reached') throw Object.assign(new Error(p.message || 'limit'), { quota: true });
    }
  }
  return { texte, outils, done };
}

const date = new Date().toISOString().slice(0, 10);
const lignes = [`# Banc conversationnel — ${date}\n`, `API : ${API}${COOKIE ? ' (compte connecté)' : ' (anonyme)'}\n`];
let total = 0, verts = 0, arret = null;

for (const cas of CAS) {
  if (ONLY.length && !ONLY.includes(cas.id)) continue;
  console.log(`\n=== ${cas.id} — ${cas.titre}`);
  lignes.push(`\n## ${cas.id} — ${cas.titre}\n`);
  const messages = [];
  let dernier = null;
  const tousOutils = [];
  try {
    for (const tour of cas.tours) {
      messages.push({ role: 'user', content: tour });
      dernier = await poserQuestion(messages);
      tousOutils.push(...dernier.outils);
      messages.push({ role: 'assistant', content: dernier.texte });
      lignes.push(`**Question :** ${tour.replace(/\n/g, ' ').slice(0, 300)}\n`);
      lignes.push(`**Voie :** ${dernier.done?.provider || 'claude'} · outils : ${dernier.outils.map(o => o.tool).join(', ') || 'aucun'}\n`);
      lignes.push(`**Réponse :**\n\n${dernier.texte}\n`);
    }
  } catch (err) {
    if (err.quota) { arret = `${cas.id} : ${err.message}`; console.log(`  ⛔ quota : ${err.message}`); lignes.push(`⛔ Arrêt sur quota : ${err.message}\n`); break; }
    console.log(`  ✗ erreur : ${err.message}`); lignes.push(`✗ erreur : ${err.message}\n`); continue;
  }
  for (const c of cas.controles) {
    total++;
    let ok = false;
    try { ok = Boolean(c.ok(dernier.texte, tousOutils)); } catch { ok = false; }
    if (ok) verts++;
    console.log(`  ${ok ? '✓' : '✗'} ${c.nom}`);
    lignes.push(`- ${ok ? '✓' : '✗'} ${c.nom}`);
  }
  lignes.push(`\n**Relecture humaine :** ${cas.relecture}\n`);
}

lignes.push(`\n---\nContrôles mécaniques verts : ${verts} / ${total}${arret ? ` · arrêt sur quota à ${arret}` : ''}\n`);
lignes.push('Un contrôle mécanique vert n\'est pas un verdict halakhique : la colonne « relecture humaine » reste à faire.\n');
mkdirSync('audit', { recursive: true });
const out = `audit/conversationnel-${date}.md`;
writeFileSync(out, lignes.join('\n'));
console.log(`\nContrôles verts : ${verts}/${total}${arret ? ` (arrêt sur quota : ${arret})` : ''} — relevé : ${out}`);
process.exit(arret ? 3 : (verts === total ? 0 : 1));
