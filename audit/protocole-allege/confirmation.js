export const meta = {
  name: 'oh394-confirmation-unique',
  description: 'Lot 394-397 : une seule passe de confirmation (2 verificateurs par siman, aucun arbitre) apres les corrections du coordinateur',
  phases: [{ title: 'Verifier', detail: 'deux lentilles par siman : la source, la halakha et la coherence' }],
}

const SP = '/tmp/claude-0/-home-user-Daat-ai/7d493fdf-7647-52e4-bf6b-12b6742d003b/scratchpad'
const WT = `${SP}/wt-e8`
const MEM = `${SP}/oh366/memoire-e8`
const SIMANIM = (args && args.simanim) || []
const HEB = { 393: 'שצ״ג', 394: 'שצ״ד', 395: 'שצ״ה', 396: 'שצ״ו', 397: 'שצ״ז', 398: 'שצ״ח' }
const SECTION = (n) => n <= 395 ? 'Hilkhot Erouvin' : `Hilkhot Te'houmin (le site range 396-407 sous la section « techumin » du
catalogue ; dans l'index de Sefaria, הלכות תחומין va de 396 a 407 ; le siman 396 ouvre הלכות תחומין, le 395 clot הלכות עירובין)`

const GRAVITE = `GRAVITE, DEFINIE :
« bloquant » : la page enseigne quelque chose de faux — une halakha, un degre, une attribution, une traduction qui inverse, elargit ou
restreint, une citation qui n'est pas a l'adresse donnee.
« a_corriger » : une phrase de la page est inexacte ou trompeuse sur une source — mauvais locuteur, condition perdue qui rend la regle
plus large que la source, citation coupee avant ce qui la limite, cas dispute presente avec des avis differents selon l'endroit, liste ou
promesse presentee comme complete et qui ne l'est pas, renvoi qui mene a un endroit qui ne porte pas ce qu'il annonce, parite rompue
entre les langues sur le contenu.
« mineur » : tout le reste (une source de plus qu'on pourrait nommer quand rien ne devient faux ; une precision ; la typographie, le style).`

const COMMUN = (n) => `TU TRAVAILLES DANS LA COPIE DE TRAVAIL ${WT} (git worktree du depot /home/user/Daat.ai, tete detachee) — PAS dans
/home/user/Daat.ai. Lance les scripts depuis ${WT} (cd ${WT} && python3 scripts/…). CLAUDE.md (injecte) : ses regles absolues priment.
NE MODIFIE AUCUN FICHIER, NE COMMITTE PAS, NE POUSSE PAS, ne lance ni npm run build ni verify-oh-source.py --rendu.
Ton siman : Orah Haim ${n} (${HEB[n]}), ${SECTION(n)}, sous sources/shabbat/siman-${n}/ (URL /oh/${n}/) : quinze fichiers (index et
quatre niveaux, en francais, hebreu et anglais). Deux numerotations : niveaux 1-3 sur le Mehaber, niveau 4 sur le Choul'han Aroukh HaRav.
CAHIER DES CHARGES : docs/brief-orah-haim-366.md (sections 0-ter et 2 a 9). Pour lire la source sans la retaper :
python3 scripts/sefaria-extrait.py (seif SAH ${n} K · seif SA ${n} K · seif MB ${n} K · extrait … · compte …) ; pour un autre ouvrage,
l'API de Sefaria (https://www.sefaria.org/api/texts/REF?context=0&pad=0).
REGLES QUE LA PAGE DOIT TENIR (protocole allege, lecons des lots 382-393) :
- Chaque affirmation nomme son seif (ou ס״ק, ou folio) et ce passage la porte.
- Un cas dispute s'expose en detail a un seul endroit (niveau 2, et un tableau du niveau 3) ; ailleurs, une forme courte et sure
  (« les commentateurs divergent ») avec un renvoi — jamais un sous-ensemble des voix, ni la solution d'un seul commentateur.
- La reserve courte d'un cas ouvert va PARTOUT ou la regle est enoncee : niveaux 1, 3, 4, index, entete de l'index (description, og,
  twitter, JSON-LD), branches des arbres, mnemoniques, commandements.
- Une condition de la source (« בכה״ג », « ודוקא », « אלא אם כן ») accompagne la regle partout ou la page la reprend.
- Une citation ne s'arrete pas juste avant une clause qui la limite ou la retourne (« אבל… », « ואף על פי כן… ») ; un « … » ne saute pas
  une telle clause.
- Une divergence s'attribue a ceux qui divergent, non a ceux qui la rapportent ; un renvoi d'un commentateur (« ועיין לעיל … מש״כ שם »)
  se rend tel qu'il est ecrit ; une reference d'une glose du Rama (« (טור) ») cite le passage dont la glose reprend la formule, ou tous.
- Pas de liste fermee ni de promesse d'exhaustivite ; le chapeau de la section 2 du niveau 4 ne promet rien d'exhaustif.
- Un renvoi (« niveau 2, section 5 ») mene a une section qui porte ce qu'il annonce.
- Une precision ajoutee dans une langue l'est dans les trois. Pages hebraiques : « סימן שצ״ד · 394 », jamais le chiffre seul.
${GRAVITE}
Machine partagee : lance une porte a la fois.`

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
          fichier: { type: 'string' },
          ligne: { type: 'string', description: 'ligne ou passage exact de la page' },
          quoi: { type: 'string' },
          preuve: { type: 'string', description: 'texte de la source avec sa ref' },
          correction: { type: 'string' },
        },
        required: ['gravite', 'fichier', 'ligne', 'quoi', 'preuve'],
      },
    },
  },
  required: ['contenu', 'objections'],
}

const LENTILLES = [
  { cle: 'source', texte: `LENTILLE « SOURCE » : relis chaque niveau CONTRE LA SOURCE, seif par seif. Le texte du niveau 1 est-il celui du
Mehaber et du Rama, et celui du niveau 4 celui du Choul'han Aroukh HaRav ? Chaque traduction rend-elle la source sans l'elargir, la
restreindre ni l'inverser ? Chaque citation est-elle a son adresse, entiere jusqu'a ce qui la limite ? Chaque attribution nomme-t-elle le
bon locuteur ? Chaque renvoi mene-t-il ou il dit ? Lance au moins verifier-citations.py (--path sources/shabbat/siman-N --langues
fr,he,en) et verifier-troncatures.py (--path …) sur ton siman.` },
  { cle: 'halakha', texte: `LENTILLE « HALAKHA ET COHERENCE » : la page enseigne-t-elle quelque chose de faux, ou de plus large ou plus
etroit que la source ? Chaque cas dispute porte-t-il les memes avis partout (index et son entete, niveaux 1 a 4, tableaux, arbres,
pieges, commandements) ? Une conclusion qu'un auteur ecrit lui-meme (« ויש לסמוך… ») est-elle rendue la ou la page le cite ? FR, HE et EN
disent-ils la meme chose ?` },
]

const CONTEXTE = (args && args.contexte) || ''
async function confirmer(n) {
  const c = COMMUN(n) + `\nLES CONTROLES DE STRUCTURE (balises, liens, langues, classes, apercus, alignement, rendu) SONT FAITS PAR LES
PORTES AUTOMATIQUES AILLEURS : ne les relance pas ; lis la PAGE contre la SOURCE. Lis ce dont tu as besoin, pas tout le depot.
Memoire du siman (decisions deja arbitrees : ne rouvre une decision que sur PREUVE NOUVELLE tiree de la source) : ${MEM}/decisions-${n}.md.
${CONTEXTE}`
  const verdicts = (await parallel(LENTILLES.map(l => () => agent(`${c}\n\nTU VERIFIES EN ADVERSAIRE les 15 fichiers du siman ${n} : c'est la
PASSE DE CONFIRMATION, apres trois passes et les corrections du coordinateur (fin de decisions-${n}.md). ${l.texte}\nOuvre la source pour
chaque point que tu juges. Tu ne modifies RIEN. Chaque objection porte la preuve tiree de la source.`,
    { label: `verifier:${n}:${l.cle}:${(args && args.passe) || 'c1'}`, phase: 'Verifier', schema: VERDICT, effort: 'high' })))).filter(Boolean)
  const objections = verdicts.flatMap((v, i) => (v.objections || []).map(o => ({ ...o, lentille: LENTILLES[i].cle })))
  const graves = objections.filter(o => o.gravite !== 'mineur')
  log(`siman ${n}, confirmation : ${graves.length} grave(s), ${objections.length - graves.length} mineure(s)`)
  return { n, propre: verdicts.length === LENTILLES.length && !graves.length, verdicts: verdicts.length, graves, mineures: objections.filter(o => o.gravite === 'mineur') }
}
const res = await pipeline(SIMANIM, n => confirmer(n))
return { res }
