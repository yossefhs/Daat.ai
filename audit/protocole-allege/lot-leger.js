export const meta = {
  name: 'oh398-production-legere',
  description: 'Lot 398-401 : production allegee (un redacteur par niveau, pas de passe de verification pendant l ecriture, niveau 2 court) puis verification allegee (2 verificateurs par passe, 3 passes au plus)',
  phases: [
    { title: 'Ecrire', detail: 'niveau 1 et niveau 4 en parallele, puis niveau 2, puis niveau 3 et index' },
    { title: 'Verifier', detail: 'deux lentilles par passe ; un arbitre sur les objections graves, sauf a la derniere passe' },
  ],
}

// Réécrit le 26 novembre 2026 : l'original (lot-leger-e8.js) a été perdu avec l'espace de travail de la session.
// Même structure que les lots 382-397 ; copie de référence dans audit/protocole-allege/ du dépôt.
const SP = '/tmp/claude-0/-home-user-Daat-ai/7d493fdf-7647-52e4-bf6b-12b6742d003b/scratchpad'
const WT = `${SP}/wt-e9`
const MEM = `${SP}/oh366/memoire-e9`
const SIMANIM = (args && args.simanim) || []
const TOURS = Math.min((args && args.tours) || 3, 3)
const HEB = { 397: 'שצ״ז', 398: 'שצ״ח', 399: 'שצ״ט', 400: 'ת׳', 401: 'ת״א', 402: 'ת״ב', 403: 'ת״ג', 404: 'ת״ד', 405: 'ת״ה' }
const SECTION = (n) => n <= 395 ? 'Hilkhot Erouvin' : `Hilkhot Te'houmin — le site range 396-407 sous la section « techumin » du
catalogue ; dans l'index de Sefaria, הלכות תחומין va de 396 a 407. Tes pages disent partout (meta, keywords, heros, fil d'Ariane, section
« place dans… ») « Hilkhot Te'houmin » / « הלכות תחומין » / « Hilchos Techumin »`

const GRAVITE = `GRAVITE, DEFINIE :
« bloquant » : la page enseigne quelque chose de faux — une halakha, un degre, une attribution, une traduction qui inverse, elargit ou
restreint, une citation qui n'est pas a l'adresse donnee.
« a_corriger » : une phrase de la page est inexacte ou trompeuse sur une source — mauvais locuteur, condition perdue qui rend la regle
plus large que la source, citation coupee avant ce qui la limite, cas dispute presente avec des avis differents selon l'endroit, liste ou
promesse presentee comme complete et qui ne l'est pas, renvoi qui mene a un endroit qui ne porte pas ce qu'il annonce, parite rompue
entre les langues sur le contenu.
« mineur » : tout le reste (une source de plus qu'on pourrait nommer quand rien ne devient faux ; une precision ; la typographie, le style).`

const COMMUN = (n) => `TU TRAVAILLES DANS LA COPIE DE TRAVAIL ${WT} (git worktree du depot /home/user/Daat.ai, tete detachee) — PAS dans
/home/user/Daat.ai : n'y ecris RIEN. Lance les scripts depuis ${WT} (cd ${WT} && python3 scripts/…). CLAUDE.md (injecte) : ses regles
absolues priment. NE COMMITTE PAS, NE POUSSE PAS, ne lance ni npm run build ni verify-oh-source.py --rendu. Ne touche a aucun fichier hors
de sources/shabbat/siman-${n}/ (catalogue, siman-nav.js, data/, pages des autres simanim, assets/ : c'est le coordinateur).
Ton siman : Orah Haim ${n} (${HEB[n]}), ${SECTION(n)}, sous sources/shabbat/siman-${n}/ (URL /oh/${n}/).
CAHIER DES CHARGES : docs/brief-orah-haim-366.md — lis les sections 0-ter (gabarit arrete et QUINZE DEFAUTS a eviter), 2-3 (fichiers,
charpente), et celle de ton niveau (4 index, 5 niveau 1, 6 niveau 2, 7 niveau 3, 8 niveau 4), puis 9 (conventions). Modele de FORME :
sources/shabbat/siman-397/ (publie, verifie, Hilkhot Te'houmin) ou siman-393/ ; siman-395/ ou siman-388/ pour un seif unique ; CSS du
niveau 4 copie a l'octet de siman-365 (verify-oh-source gele la feuille ; n'y ajoute AUCUNE classe : n'emploie que celles que la feuille
definit). Aucun mot d'hebreu retape : python3 scripts/sefaria-extrait.py (seif SAH ${n} K · seif SA ${n} K · seif MB ${n} K · extrait …
· compte …). Deux numerotations : niveaux 1-3 sur le Mehaber, niveau 4 sur le Choul'han Aroukh HaRav — nomme toujours l'ouvrage avec un
numero de seif ou un compte.
PRODUCTION ALLEGEE (decision de l'utilisateur, 29-30 octobre 2026, pour economiser) : ECRIS JUSTE ET COURT.
- Pas de passe de verification apres toi : relis ta page contre les quinze defauts avant de rendre.
- Chaque affirmation nomme son seif (ou ס״ק, ou folio) et ce passage la porte ; sinon elle n'est pas ecrite. Dans le doute, n'ecris pas.
- Un cas dispute s'expose EN DETAIL a un seul endroit (le niveau 2, et un tableau du niveau 3) ; ailleurs, une forme courte et sure (ce
  que dit le seif tel qu'imprime ; « les commentateurs divergent ») avec un renvoi. Jamais un sous-ensemble des voix.
- Pas de phrase qui rassemble ou compte des voix, pas de liste fermee, pas de promesse d'exhaustivite (« notamment »).
- Une citation ne s'arrete pas juste avant une clause qui la limite (« אלא אם כן… », « אבל… »).
- Pas de « hidoush » que la comparaison des deux textes ne montre pas ; aucun objet moderne attribue a la source.
- Un doute que la source ne tranche pas va dans « doutes », avec la question exacte a poser au Rav ; la page ne tranche pas.
LECONS DES LOTS 382-397 (objections relevees jusqu'a la derniere passe ; evite-les d'emblee) :
- La forme courte vaut AUSSI au niveau 4 (sections 2 a 4) et dans les tableaux du niveau 3 : n'y cite jamais la solution d'UN seul
  commentateur sur un cas que d'autres discutent ; ecris « les commentateurs divergent » + renvoi.
- Une reserve d'un commentateur se rapporte EXACTEMENT au cas qu'il vise ; un renvoi groupe doit etre exact pour chaque seif nomme.
- Une note, une precision ou un crochet ajoute dans une langue l'est dans les trois.
- Pages hebraiques : jamais « סימן 398 » en chiffres seuls ; ecris « סימן שצ״ח · 398 » (scripts/heb-nums.py).
- Le chapeau de la section 2 du niveau 4 ne PROMET RIEN d'exhaustif : « la page en nomme parfois la source ; elle ne releve ni toutes les
  sources ni toutes les divergences ».
- Une divergence s'attribue a CEUX QUI DIVERGENT, non a ceux qui la rapportent. Un cas que le niveau 2 ou 3 dit dispute est signale comme
  tel au niveau 4 aussi, et inversement.
- Une citation de guemara ne s'arrete pas sur une question sans sa reponse ; une citation coupee par « … » ne saute pas une clause qui
  retourne ou limite ce qui precede (« ואף על פי כן… », « אבל… »). Lance verifier-troncatures.py avant de rendre.
- Une condition de la source (« בכה״ג », « ודוקא », « אלא אם כן ») et une qualification qu'un auteur attache a un avis accompagnent la regle
  PARTOUT ou la page la reprend : resumes, tableaux, schemas, pieges, commandements, index.
- Quand un auteur ecrit lui-meme sa conclusion (« ויש לסמוך… », « וכן עיקר »), la page la rend partout ou elle cite cet auteur sur ce point.
- Un renvoi d'un commentateur (« ועיין לעיל … מש״כ שם ») se rend tel qu'il est ecrit ; une reference d'une glose du Rama (« (טור) ») cite le
  passage dont la glose reprend la formule, ou tous.
- Un cas que le niveau 2 laisse ouvert porte la reserve courte + renvoi PARTOUT ou la regle est enoncee, entete de l'index compris
  (description, og, twitter, JSON-LD), branches des arbres et mnemoniques compris.
- Chaque renvoi (« niveau 2, section 5 ») mene a une section qui porte ce qu'il annonce : relis tes renvois contre les titres de section.
- Un pronom ambigu se traduit sans en restreindre l'antecedent ; une parenthese en petits caracteres sans « הגה » n'est attribuee a
  personne ; les gloses du Rama se decrivent « introduite(s) par הגה au seif … ».
- Francais : pas de calque (« il y a qui interdit ») ni de double negation.
- Navigation : laisse le lien « suivant » en nav-spacer (le coordinateur le pose a la publication) ; le lien « precedent » mene au siman
  ${n - 1}.
${GRAVITE}
Machine partagee : lance une porte a la fois.`

const ECRIT = {
  type: 'object',
  properties: {
    fichiers: { type: 'array', items: { type: 'string' }, description: 'fichiers ecrits' },
    contenu: { type: 'string', description: 'ce que chaque seif traite, seif par seif, avec la numerotation de chaque ouvrage (court)' },
    portes: { type: 'string', description: 'sortie resumee de chaque porte lancee' },
    doutes: { type: 'array', items: { type: 'object', properties: { ou: { type: 'string' }, question: { type: 'string' } }, required: ['ou', 'question'] } },
  },
  required: ['fichiers', 'contenu', 'doutes'],
}
const VERDICT = {
  type: 'object',
  properties: {
    contenu: { type: 'string', description: 'ce que chaque seif traite, seif par seif, avec la numerotation de chaque ouvrage (court)' },
    portes: { type: 'string', description: 'sortie resumee de chaque porte lancee' },
    objections: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          gravite: { type: 'string', enum: ['bloquant', 'a_corriger', 'mineur'] },
          fichier: { type: 'string' }, ligne: { type: 'string', description: 'ligne ou passage exact de la page' },
          quoi: { type: 'string' }, preuve: { type: 'string', description: 'texte de la source avec sa ref' }, correction: { type: 'string' },
        },
        required: ['gravite', 'fichier', 'ligne', 'quoi', 'preuve'],
      },
    },
  },
  required: ['contenu', 'objections'],
}
const ARBITRAGE = {
  type: 'object',
  properties: {
    retenues: { type: 'array', items: { type: 'object', properties: { quoi: { type: 'string' }, correction_faite: { type: 'string' } }, required: ['quoi', 'correction_faite'] } },
    rejetees: { type: 'array', items: { type: 'object', properties: { quoi: { type: 'string' }, raison: { type: 'string' } }, required: ['quoi', 'raison'] } },
    doutes: { type: 'array', items: { type: 'object', properties: { ou: { type: 'string' }, question: { type: 'string' } }, required: ['ou', 'question'] } },
  },
  required: ['retenues', 'rejetees', 'doutes'],
}

const LENTILLES = [
  { cle: 'source', texte: `LENTILLE « SOURCE » : relis chaque niveau CONTRE LA SOURCE, seif par seif. Le texte du niveau 1 est-il celui du
Mehaber et du Rama, et celui du niveau 4 celui du Choul'han Aroukh HaRav ? Chaque traduction rend-elle la source sans l'elargir, la
restreindre ni l'inverser ? Chaque citation est-elle a son adresse, entiere jusqu'a ce qui la limite ? Chaque attribution nomme-t-elle le
bon locuteur ? Chaque renvoi mene-t-il ou il dit ? Lance au moins verifier-citations.py (--path sources/shabbat/siman-N --langues
fr,he,en) et verifier-troncatures.py (--path …) sur ton siman.` },
  { cle: 'halakha', texte: `LENTILLE « HALAKHA ET COHERENCE » : la page enseigne-t-elle quelque chose de faux, ou de plus large ou plus
etroit que la source ? Chaque cas dispute porte-t-il les memes avis partout (index et son entete, niveaux 1 a 4, tableaux, arbres,
pieges, commandements) ? Une conclusion qu'un auteur ecrit lui-meme est-elle rendue la ou la page le cite ? FR, HE et EN disent-ils la
meme chose ?` },
]

async function ecrire(n) {
  const c = COMMUN(n) + `\nMemoire du siman : ${MEM}/decisions-${n}.md (cree-la si elle n'existe pas ; note-y en une ligne chaque choix de
fond que tu fais et sa source).`
  const [n1, n4] = await parallel([
    () => agent(`${c}\n\nTA TACHE : le NIVEAU 1 (niveau-1-base.html, -he, -en), sur le gabarit de section 5 du cahier des charges et la
forme du modele. Texte du Mehaber et du Rama recopie de l'edition par defaut (sefaria-extrait), seif par seif, dans l'ordre ; traduction ;
« Ce que dit ce seif » ; concepts ; cas pratiques ; questions. Lance verify-chabbat-source.py ${n}, verifier-alignement.py --siman ${n},
verifier-citations.py et verifier-troncatures.py sur ton siman avant de rendre.`, { label: `ecrire:${n}:N1`, phase: 'Ecrire', schema: ECRIT }),
    () => agent(`${c}\n\nTA TACHE : le NIVEAU 4 (niveau-4-daat-harav.html, -he, -en), sur la section 8 du cahier des charges et la forme du
modele, CSS copie a l'octet. Section 1 : chaque seif du Choul'han Aroukh HaRav dans un <details class="seif-details">, texte vocalise de
Kehot (sefaria-extrait), aperçu = debut du seif verbatim ; sections 2 a 4 selon le cahier. Lance verify-oh-source.py ${n} (SANS --rendu),
verifier-apercus.py ${n}, verifier-classes.py --path sources/shabbat/siman-${n}, verifier-citations.py et verifier-troncatures.py avant
de rendre.`, { label: `ecrire:${n}:N4`, phase: 'Ecrire', schema: ECRIT }),
  ])
  const n2 = await agent(`${c}\n\nTA TACHE : le NIVEAU 2 (niveau-2-lamdan.html, -he, -en), COURT : la sougya (guemara d'Erouvin et ses
commentateurs), les Richonim et A'haronim que le Tour, le Beit Yossef, la Michna Beroura et le Biour Halakha font parler sur chaque cas
dispute — chacun cite par son texte (sefaria-extrait / API Sefaria), sans phrase qui rassemble des voix ; au plus une dizaine de sections,
recapitulatif compris (section 6 du cahier ; gabarit de forme : siman-397, en plus court). Ce que les niveaux 1 et 4 ont deja ecrit :
N1 ${JSON.stringify((n1 && n1.contenu) || '')} ; N4 ${JSON.stringify((n4 && n4.contenu) || '')}. Lance verifier-citations.py et
verifier-troncatures.py avant de rendre.`, { label: `ecrire:${n}:N2`, phase: 'Ecrire', schema: ECRIT })
  const n3 = await agent(`${c}\n\nTA TACHE : le NIVEAU 3 (niveau-3-synthese.html, -he, -en) et l'INDEX (index.html, -he, -en), sections 7
et 4 du cahier. Lis d'abord les niveaux 1, 2 et 4 du siman, deja ecrits : la synthese et l'index n'enseignent rien qu'ils ne portent, et
chaque cas que le niveau 2 dit dispute y porte la forme courte et le renvoi, entete de l'index compris. Verifie chaque renvoi vers une
section contre les titres de section. Lance verifier-alignement.py --siman ${n}, verifier-citations.py, verifier-troncatures.py,
verifier-denombrements.py --path …, verifier-langues.py --path … et verifier-balises.py --path … avant de rendre.`,
    { label: `ecrire:${n}:N3-index`, phase: 'Ecrire', schema: ECRIT })
  return [n1, n4, n2, n3].filter(Boolean).flatMap(r => r.doutes || [])
}

async function verifier(n, doutesEcriture) {
  const journal = []
  const doutes = [...doutesEcriture]
  for (let tour = 1; tour <= TOURS; tour++) {
    const c = COMMUN(n) + `\nMemoire du siman (decisions deja arbitrees : ne rouvre une decision que sur PREUVE NOUVELLE tiree de la source) :
${MEM}/decisions-${n}.md.\nLES CONTROLES DE STRUCTURE (balises, liens, langues, classes, apercus, alignement, rendu) SONT FAITS PAR LES PORTES
AUTOMATIQUES : lis la PAGE contre la SOURCE.`
    const verdicts = (await parallel(LENTILLES.map(l => () => agent(`${c}\n\nTU VERIFIES EN ADVERSAIRE les 15 fichiers du siman ${n}
(passe ${tour} sur ${TOURS} au plus). ${l.texte}\nOuvre la source pour chaque point que tu juges. Tu ne modifies RIEN. Chaque objection
porte la preuve tiree de la source.`, { label: `verifier:${n}:${l.cle}:l${tour}`, phase: 'Verifier', schema: VERDICT, effort: 'high' })))).filter(Boolean)
    const objections = verdicts.flatMap((v, i) => (v.objections || []).map(o => ({ ...o, lentille: LENTILLES[i].cle })))
    const graves = objections.filter(o => o.gravite !== 'mineur')
    log(`siman ${n}, passe ${tour} : ${graves.length} grave(s), ${objections.length - graves.length} mineure(s)`)
    if (verdicts.length === LENTILLES.length && !graves.length) {
      journal.push({ tour, graves: 0, objections: objections.length, mineures: objections })
      return { n, propre: true, tours: tour, journal, doutes }
    }
    if (tour === TOURS) {
      journal.push({ tour, graves_restantes: graves, mineures: objections.filter(o => o.gravite === 'mineur') })
      return { n, propre: false, plafond: true, tours: tour, journal, doutes }
    }
    const arb = await agent(`${c}\n\nTU ES L'ARBITRE de la passe ${tour} sur le siman ${n}. Voici les objections GRAVES des verificateurs
(les mineures ne s'appliquent pas) :\n${JSON.stringify(graves, null, 1)}\n\nPour CHACUNE : ouvre la source et juge-la. FONDEE → corrige
toi-meme, dans les trois langues et a TOUTES les occurrences du defaut dans les 15 fichiers (mesure-les par grep avant de corriger :
l'occurrence signalee n'est jamais la seule), par retrait ou par forme courte plutot que par un ajout long ; relis ta correction comme une
page neuve (elle ne doit introduire ni une voix unique, ni une promesse, ni une citation coupee). NON FONDEE → rejette-la avec la preuve.
Puis lance verifier-citations.py (--langues fr,he,en) et verifier-troncatures.py sur le siman, et ajoute a ${MEM}/decisions-${n}.md une
section « Verification allegee, passe ${tour} » : une ligne par objection (FONDEE/REJETEE, preuve, correction faite). Un point que la
source ne tranche pas va dans « doutes ».`, { label: `arbitrer:${n}:${tour}`, phase: 'Verifier', schema: ARBITRAGE, effort: 'high' })
    journal.push({ tour, graves: graves.length, objections: objections.length, arbitrage: arb })
    if (arb && arb.doutes) doutes.push(...arb.doutes)
  }
  return { n, propre: false, tours: TOURS, journal, doutes }
}

const res = await pipeline(SIMANIM, n => ecrire(n), (doutesEcriture, n) => verifier(n, doutesEcriture || []))
log(`lot ${SIMANIM.join(', ')} : ${res.filter(r => r && r.propre).length}/${SIMANIM.length} simanim propres`)
return { res }
