// Livraison vérifiée — point 2 (19 octobre 2026).
//
// Le modèle ne recopie plus l'hébreu : il le DÉSIGNE, le serveur colle le texte
// exact. Et chaque paragraphe est contrôlé au passage avant d'atteindre le
// lecteur, sans renoncer à l'affichage progressif : on retient un paragraphe à
// la fois, pas la réponse entière.
//
// Pourquoi. Les bancs des 18 et 19 octobre (19 réponses réelles) ont montré que
// charger les sources avant la réponse (points 1 et 1b) fixe l'ordre, les mots
// et les attributions — tant que le modèle ne retape pas l'hébreu de mémoire.
// Or il le fait encore : « תישוי », un mot inventé dans une citation, est né
// comme ça. Ici une citation fausse devient impossible par construction : le
// modèle écrit [[cite:Shulchan_Arukh,_Orach_Chayim.253.1]] et c'est Sefaria qui
// parle. Ce qu'il taperait tout de même en hébreu (quatre mots et plus) est
// confronté aux textes ouverts pendant la réponse et marqué s'il n'y est pas ;
// un décisionnaire nommé qu'aucun texte ouvert ne nomme est marqué « hors
// sources ». Un pied de réponse dit au lecteur ce qui a été vérifié.
//
// Ce que ça ne fait pas : juger un raisonnement. Une lecture de travers d'un
// texte pourtant ouvert (la structure du HaRav 253, le 18/10) passe. C'est au
// banc rejoué et aux signalements de la voir.
//
// Syntaxe acceptée du modèle :
//   [[cite:REF]]                → le texte entier de REF (plafonné)
//   [[cite:REF|début…fin]]      → l'extrait de REF qui va de « début » à « fin »
// REF est une référence Sefaria au format des outils (underscores, virgule, point).

import { fetchSefariaText } from './_sefaria.js';

const MAX_CITATION = 1500;          // au-delà, un séif entier est coupé avec « […] »
const MIN_MOTS_HEBREU = 4;          // un passage hébreu plus court est un terme, pas une citation
const MARQUEUR_RE = /\[\[cite:([^\]|]+?)(?:\|([^\]]*?))?\]\]/g;
// Quatre mots hébreux ou plus, la ponctuation ordinaire entre eux comprise
// (« אחד, שנים : שלש. ארבע » est un seul passage — relecture Codex #284).
const HEBREU_RE = /(?:[\u0590-\u05FF][\u0590-\u05FF״׳"'’\-־]*[\s,.;:!?()«»"'’]*){4,}/g;

export function normaliser(t) {
  return String(t || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[֑-ׇ]/g, '')                    // nikoud et te'amim
    .replace(/[״׳"'“”‘’«»,.;:!?()\[\]{}־–—\-/\\|*#_`]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
const squelette = (t) => t.replace(/[וי]/g, '');

// Décisionnaires que le modèle aime nommer, avec les formes sous lesquelles les
// sources les écrivent. Un nom est « sourcé » si l'une de ses formes figure dans
// un texte ouvert (références comprises : ouvrir le HaRav suffit à le nommer).
const DECISIONNAIRES = [
  ['Rambam',        /\b(?:rambam|maimonide)\b|רמב[״"]ם/i,                     ['רמבם']],
  ['Rif',           /\brif\b|רי[״"]ף/i,                                        ['ריף']],
  ['Roch',          /\bro[sc]h\b|רא[״"]ש/i,                                    ['ראש']],
  ['Ran',           /\bran\b|ר[״"]ן/i,                                         ['רן']],
  ['Rachi',         /\bra[cs]hi\b|רש[״"]י/i,                                   ['רשי', 'פירשי']],
  ['Tossafot',      /\btoss?afot\b|תוספות|תוס['׳]/i,                           ['תוספות', 'תוס']],
  ['Rabbénou Tam',  /\brabb?[ée]i?nou\s+tam\b|rabbeinu\s+tam|ר[״"]ת/i,          ['רת', 'רבינו תם']],
  ['Rachba',        /\bra[cs]hba\b|רשב[״"]א/i,                                  ['רשבא']],
  ['Ramban',        /\bramban\b|רמב[״"]ן/i,                                     ['רמבן']],
  ['Mordekhi',      /\bmordekh?[ai]i?\b|\bmordechai\b|מרדכי/i,                 ['מרדכי']],
  ['Smag / Smak',   /\bs[e]?ma[gk]\b|סמ[״"][גק]/i,                             ['סמג', 'סמק']],
  ['Terouma',       /\b(?:sefer ha-?)?t[eé]rouma(?:h)?\b|\bterumah?\b|התרומה/i, ['התרומה', 'תרומה']],
  ['Hagahot',       /\bhagahot\b|הגהות/i,                                       ['הגהות']],
  ['Rabbénou Hananel', /\brabb?[ée]i?nou\s+[hḥc]h?anan?el\b|ר[״"]ח\b/i,         ['רח', 'רבינו חננאל']],
  ['Baal HaMaor',   /\bba['’]?al\s+ha-?ma['’]?or\b|\braza[h]?\b|רז[״"]ה|המאור/i, ['רזה', 'המאור']],
  ['Rav Haï',       /\brav\s+hai\b|רב האי/i,                                    ['רב האי']],
  ['Maguid Michné', /\bmaguid\s+michn[eé]\b|\bmaggid\s+mishneh\b|מגיד משנה/i,  ['מגיד משנה']],
  ['Tour',          /\btour\b|\btur\b|הטור/i,                                   ['הטור', 'רבינו']],
  ['Michna Beroura', /\bmichna\s+b[ée]roura\b|\bmishnah?\s+berurah?\b|מ[״"]ב\b|משנה ברורה/i, ['משנה ברורה', 'מב', 'Mishnah_Berurah']],
  ['Admour HaZaken', /\badmou?r\s+ha-?zaken\b|\balter\s+rebbe\b|אדמו[״"]ר הזקן|שו[״"]ע הרב|(?:choul['’]?han|shulchan)\s+arou?kh?\s+ha-?rav/i, ['Shulchan_Arukh_HaRav', 'שוע הרב', 'אדמור']],
];

function textesDuResultat(brut) {
  // Un résultat d'outil est une chaîne JSON ; on en extrait toutes les chaînes
  // substantielles (hébreu d'un séif, extrait du site, référence…).
  const out = [];
  const visite = (x) => {
    if (typeof x === 'string') { if (x.length >= 12) out.push(x); return; }
    if (Array.isArray(x)) { x.forEach(visite); return; }
    if (x && typeof x === 'object') Object.values(x).forEach(visite);
  };
  try { visite(JSON.parse(brut)); } catch { if (typeof brut === 'string') out.push(brut); }
  return out;
}

export class FiltreLivraison {
  constructor({ sources = [], lang = 'fr', fetchTexte = fetchSefariaText } = {}) {
    this.lang = lang;
    this.fetchTexte = fetchTexte;
    this.pool = '';          // textes ouverts, normalisés, pour la recherche
    this.poolSq = '';        // idem, sans ו/י (ktiv malé / haser)
    this.refs = '';          // références ouvertes (noms latins des œuvres)
    this.tampon = '';
    this.stats = { collees: 0, introuvables: 0, retrouves: 0, nonRetrouves: 0, horsSources: [] };
    this.nomsSignales = new Set();
    for (const s of sources) this.ajouterSource(s.ref, s.texte);
  }

  ajouterSource(ref, texte) {
    const n = normaliser(texte);
    if (n) { this.pool += ' ' + n + ' '; this.poolSq += ' ' + squelette(n) + ' '; }
    if (ref) this.refs += ' ' + String(ref) + ' ';
  }

  // À appeler après chaque ronde d'outils : tout ce que le modèle a ouvert
  // devient une source, pour les citations libres et les noms.
  ajouterResultats(toolUses = [], toolResults = []) {
    toolResults.forEach((r, i) => {
      if (!r || r.is_error) return;
      const tu = toolUses[i] || {};
      const ref = tu.input && (tu.input.ref || tu.input.id || tu.input.query) || tu.name || '';
      for (const t of textesDuResultat(r.content)) this.ajouterSource(ref, t);
    });
  }

  dansLesSources(passage) {
    const n = normaliser(passage);
    if (!n) return true;
    if (this.pool.includes(' ' + n + ' ') || this.pool.includes(n)) return true;
    return this.poolSq.includes(squelette(n));
  }

  nomSource(formes) {
    const poolSansGuillemets = this.pool.replace(/\s/g, ' ');
    return formes.some((f) => /^[A-Za-z_]/.test(f) ? this.refs.includes(f) : poolSansGuillemets.includes(normaliser(f)) || poolSansGuillemets.replace(/ /g, '').includes(normaliser(f).replace(/ /g, '')));
  }

  // Colle les citations désignées. Rend le paragraphe transformé et la liste
  // des spans collés (pour ne pas les re-vérifier comme hébreu libre).
  async collerCitations(paragraphe) {
    const marqueurs = [...paragraphe.matchAll(MARQUEUR_RE)];
    if (!marqueurs.length) return { texte: paragraphe, colles: [] };
    let texte = paragraphe;
    const colles = [];
    for (const m of marqueurs) {
      const ref = m[1].trim().replace(/\s+/g, '_');
      const plage = (m[2] || '').trim();
      let remplacement;
      try {
        const d = await this.fetchTexte(ref);
        if (!d || d.error || !d.hebrew) remplacement = `[citation introuvable : ${ref}]`;
        else {
          let he = String(d.hebrew).replace(/<[^>]+>/g, '').trim();
          if (plage) {
            const [debut, fin] = plage.split(/…|\.\.\./).map((x) => (x || '').trim());
            const extrait = extraire(he, debut, fin);
            // Les bornes sont de l'hébreu tapé par le modèle : si elles ne sont pas
            // dans le texte, c'est précisément l'erreur qu'on veut voir — pas un
            // séif entier collé à la place de l'extrait annoncé (relecture Codex).
            if (!extrait) remplacement = `[extrait non trouvé dans ${ref} : « ${plage} »]`;
            else he = extrait;
          }
          if (remplacement === undefined) {
            if (he.length > MAX_CITATION) he = he.slice(0, MAX_CITATION) + ' […]';
            remplacement = he;
          }
        }
      } catch {
        remplacement = `[citation introuvable : ${ref}]`;
      }
      if (remplacement.startsWith('[citation introuvable') || remplacement.startsWith('[extrait non trouvé')) this.stats.introuvables += 1;
      else { this.stats.collees += 1; colles.push(remplacement); }
      texte = texte.replace(m[0], remplacement);
    }
    return { texte, colles };
  }

  verifierHebreuLibre(texte, colles) {
    // Masquer ce que le serveur vient de coller : c'est du Sefaria, pas du modèle.
    let masque = texte;
    const sauvegarde = [];
    for (const c of colles) { sauvegarde.push(c); masque = masque.split(c).join(`\u0000${sauvegarde.length - 1}\u0000`); }
    masque = masque.replace(HEBREU_RE, (run) => {
      if (normaliser(run).split(' ').length < MIN_MOTS_HEBREU) return run;
      if (this.dansLesSources(run)) { this.stats.retrouves += 1; return run; }
      this.stats.nonRetrouves += 1;
      return run.trimEnd() + ' ⚠️ [non retrouvé dans les sources ouvertes] ' ;
    });
    return masque.replace(/\u0000(\d+)\u0000/g, (_, i) => sauvegarde[Number(i)]);
  }

  verifierNoms(texte) {
    let out = texte;
    for (const [nom, re, formes] of DECISIONNAIRES) {
      if (this.nomsSignales.has(nom) || !re.test(out)) continue;
      if (this.nomSource(formes)) continue;
      this.nomsSignales.add(nom);
      this.stats.horsSources.push(nom);
      out = out.replace(re, (m) => `${m} ⚠️ [nom absent des sources ouvertes]`);
    }
    return out;
  }

  async traiterParagraphe(p) {
    if (!p.trim()) return p;
    const { texte, colles } = await this.collerCitations(p);
    return this.verifierNoms(this.verifierHebreuLibre(texte, colles));
  }

  // Reçoit un delta du modèle ; rend le texte prêt à livrer (paragraphes
  // complets), ou '' s'il faut encore attendre.
  async pousser(delta) {
    this.tampon += delta;
    // Un marqueur ouvert et non fermé : on attend sa fin avant de couper.
    const ouvert = this.tampon.lastIndexOf('[[cite:');
    if (ouvert !== -1 && this.tampon.indexOf(']]', ouvert) === -1) return '';
    let sortie = '';
    let i;
    while ((i = this.tampon.indexOf('\n\n')) !== -1) {
      const par = this.tampon.slice(0, i + 2);
      this.tampon = this.tampon.slice(i + 2);
      sortie += await this.traiterParagraphe(par);
    }
    return sortie;
  }

  async terminer() {
    let sortie = '';
    if (this.tampon) {
      // Génération coupée au milieu d'un marqueur : la syntaxe interne ne doit
      // jamais atteindre le lecteur (relecture Codex #284).
      const reste = this.tampon.replace(/\[\[cite:[^\]]*$/, (m) => { this.stats.introuvables += 1; return `[citation interrompue : ${m.slice(7).split('|')[0].trim()}]`; });
      sortie += await this.traiterParagraphe(reste);
      this.tampon = '';
    }
    return sortie + this.pied();
  }

  pied() {
    const s = this.stats;
    const hors = s.horsSources.length ? s.horsSources.join(', ') : null;
    const L = {
      fr: `\n\n---\n_Vérification serveur : ${s.collees} citation${s.collees > 1 ? 's' : ''} collée${s.collees > 1 ? 's' : ''} depuis Sefaria · ${s.retrouves} passage${s.retrouves > 1 ? 's' : ''} hébreu${s.retrouves > 1 ? 's' : ''} retrouvé${s.retrouves > 1 ? 's' : ''} dans les sources ouvertes · ${s.nonRetrouves} non retrouvé${s.nonRetrouves > 1 ? 's' : ''}${s.introuvables ? ` · ${s.introuvables} référence${s.introuvables > 1 ? 's' : ''} introuvable${s.introuvables > 1 ? 's' : ''}` : ''}${hors ? ` · noms hors sources : ${hors}` : ''}._`,
      he: `\n\n---\n_אימות שרת: ${s.collees} ציטוטים הודבקו מספריא · ${s.retrouves} קטעים עבריים נמצאו במקורות שנפתחו · ${s.nonRetrouves} לא נמצאו${s.introuvables ? ` · ${s.introuvables} הפניות לא נמצאו` : ''}${hors ? ` · שמות שאינם במקורות: ${hors}` : ''}._`,
      en: `\n\n---\n_Server check: ${s.collees} quotation${s.collees > 1 ? 's' : ''} pasted from Sefaria · ${s.retrouves} Hebrew passage${s.retrouves > 1 ? 's' : ''} found in the opened sources · ${s.nonRetrouves} not found${s.introuvables ? ` · ${s.introuvables} reference${s.introuvables > 1 ? 's' : ''} not found` : ''}${hors ? ` · names outside the sources: ${hors}` : ''}._`,
    };
    return L[this.lang] || L.fr;
  }
}

// L'extrait de `texte` qui va du premier `debut` au `fin` qui le suit, en
// ignorant nikoud et ponctuation pour trouver les bornes ; rend le texte source
// (avec son nikoud) entre ces bornes, ou null si une borne manque.
export function extraire(texte, debut, fin) {
  if (!debut) return null;
  const carte = [];           // position dans le texte nu → position dans le texte source
  let nu = '';
  for (let i = 0; i < texte.length; i++) {
    const c = texte[i];
    if (/[֑-ׇ״׳"'“”‘’«»,.;:!?()\[\]{}־–—\-/\\|*#_`]/.test(c)) continue;
    const cc = /\s/.test(c) ? ' ' : c;
    if (cc === ' ' && nu.endsWith(' ')) continue;
    nu += cc; carte.push(i);
  }
  const d = normaliser(debut), f = normaliser(fin || '');
  const i0 = nu.indexOf(d);
  if (i0 === -1) return null;
  let i1;
  if (f) { const k = nu.indexOf(f, i0 + d.length); if (k === -1) return null; i1 = k + f.length - 1; }
  else i1 = i0 + d.length - 1;
  // La dernière lettre emporte le nikoud qui la suit (« לוֹ », pas « לו »).
  let fin2 = carte[i1];
  while (fin2 + 1 < texte.length && /[\u0591-\u05C7]/.test(texte[fin2 + 1])) fin2++;
  return texte.slice(carte[i0], fin2 + 1).trim();
}
