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
// parle. Ce qu'il taperait tout de même en hébreu est confronté aux textes
// ouverts pendant la réponse et marqué s'il n'y est pas ; un décisionnaire nommé
// qu'aucun texte ouvert ne nomme est marqué « hors sources ». Un pied de réponse
// dit au lecteur ce qui a été vérifié.
//
// Ce que ça ne fait pas : juger un raisonnement. Une lecture de travers d'un
// texte pourtant ouvert (la structure du HaRav 253, le 18/10) passe. C'est au
// banc rejoué et aux signalements de la voir.
//
// Syntaxe acceptée du modèle :
//   [[cite:REF]]                → le texte entier de REF (plafonné)
//   [[cite:REF|début…fin]]      → l'extrait de REF qui va de « début » à « fin »
// REF est une référence Sefaria au format des outils (underscores, virgule, point).
//
// Deux bancs sur l'aperçu (12 réponses chacun) ont réglé ce fichier :
//  - les bornes sont comparées comme des SÉQUENCES DE MOTS (abréviations
//    développées, ו/י retirés, mots tronqués par apostrophe), un mauvais
//    paragraphe du Beit Yossef est rattrapé dans le siman entier ;
//  - l'hébreu libre n'est une « citation » que s'il en a la forme : entre
//    guillemets ou en bloc « > » toujours ; hors guillemets, une phrase assez
//    longue — pas une liste de termes ; dans une prose en hébreu, jamais hors
//    guillemets ;
//  - une citation retrouvée à un mot près (coquille de Sefaria « דעם ») passe.

import { fetchSefariaText, fetchSefariaSegments } from './_sefaria.js';

const MAX_CITATION = 1500;          // au-delà, un séif entier est coupé avec « […] »
const MARQUEUR_RE = /\[\[cite:([^\]|]+?)(?:\|([^\]]*?))?\]\]/g;
// Un passage hébreu : des mots hébreux séparés par des espaces, virgules, points-
// virgules, deux-points ou guillemets. Un point, une parenthèse ou un tiret long
// le terminent (fin de phrase, glose entre parenthèses).
const PASSAGE_RE = /(?:[֐-׿][֐-׿״׳"'’\-־]*[\s,;:«»"'’]*){2,}/g;
// Zones données comme citations : guillemets (pas ceux des abréviations, d'où
// les lookarounds) et lignes « > ».
const ZONES_CITATION_RE = /«[^»\n]{8,}»|(?<![֐-׿])"[^"\n]{8,}"(?![֐-׿])|(?<![֐-׿])״[^״\n]{8,}״(?![֐-׿])|“[^”\n]{8,}”|^>.+$/gm;
const MOTS_MIN_EN_CITATION = 4;     // entre guillemets : quatre mots suffisent
const MOTS_MIN_HORS_CITATION = 5;   // hors guillemets : une phrase d'au moins cinq mots d'un seul tenant…
const MOTS_MIN_TOTAL_HORS = 7;      // …ou sept mots en deux morceaux ; une liste de termes n'est jamais une citation

export function normaliser(t) {
  return String(t || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[֑-ׇ]/g, '')                    // nikoud et te'amim
    .replace(/[״׳"'“”‘’«»,.;:!?()\[\]{}־–—…\-/\\|*#_`]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
const squelette = (t) => t.replace(/[וי]/g, '');

// ── Comparer des mots ─────────────────────────────────────────────────────────
// Sefaria écrit le HaRav en haser (קדרה, עדין, מרבה), le modèle en malé ; les
// textes rabbiniques abrègent (וי"א, ע"ג, מות') ; le tout se compare donc sur des
// « clefs » : abréviation développée, ו/י retirés, mot tronqué marqué « ~ » pour
// accepter tout mot qui le prolonge.
const ABR = { 'ויא': 'ויש אומרים', 'יא': 'יש אומרים', 'עג': 'על גבי', 'אעפ': 'אף על פי', 'אעפכ': 'אף על פי כן', 'אכ': 'אם כן', 'אאכ': 'אלא אם כן', 'מבעי': 'מבעוד יום', 'בעש': 'בערב שבת', 'מש': 'מוצאי שבת', 'למש': 'למוצאי שבת', 'ממ': 'מכל מקום', 'וממ': 'ומכל מקום', 'כש': 'כל שכן', 'וכש': 'וכל שכן', 'הה': 'הוא הדין', 'והה': 'והוא הדין', 'והמ': 'והני מילי', 'וכ': 'וכתב', 'וככ': 'וכן כתב', 'ככ': 'כן כתב', 'פי': 'פירוש', 'אפי': 'אפילו', 'ואפי': 'ואפילו', 'סי': 'סימן', 'וכו': 'וכולי', 'זל': 'זכרונו לברכה', 'גה': 'גיד הנשה', 'סהת': 'ספר התרומה', 'שע': 'שולחן ערוך', 'בי': 'בית יוסף', 'רל': 'רוצה לומר', 'דה': 'דברי הכל', 'לדה': 'לדברי הכל', 'מב': 'משנה ברורה' };
const SEP_RE = /[\s֑-ׇ“”‘’«»,.;:!?()\[\]{}־–—…\-/\\|*#_`<>]/;   // ״ ׳ " ' restent dans le mot
function motsAvecPositions(texte) {
  const toks = []; let cur = null;
  for (let i = 0; i < texte.length; i++) {
    const c = texte[i];
    if (/[֑-ׇ]/.test(c)) { if (cur) cur.fin = i; continue; }       // nikoud : reste collé au mot
    if (SEP_RE.test(c)) { if (cur) { toks.push(cur); cur = null; } continue; }
    if (!cur) cur = { mot: '', debut: i, fin: i };
    cur.mot += c; cur.fin = i;
  }
  if (cur) toks.push(cur);
  return toks;
}
function clefs(mot) {
  const tronque = /[׳']$/.test(mot) && !ABR[mot.replace(/[״׳"'’]/g, '')];
  const nu = mot.replace(/[״׳"'’]/g, '');
  const pieces = squelette(ABR[nu] || nu).split(' ').filter(Boolean);
  if (tronque && pieces.length) pieces[pieces.length - 1] += '~';
  return pieces;
}
function clefEgale(a, b) {
  if (a === b) return true;
  if (a.endsWith('~')) return b.startsWith(a.slice(0, -1));
  if (b.endsWith('~')) return a.startsWith(b.slice(0, -1));
  return false;
}
function sequenceComparable(toks) {
  const cmp = [], proprio = [];
  toks.forEach((t, j) => { for (const k of clefs(t.mot)) { cmp.push(k); proprio.push(j); } });
  return { cmp, proprio };
}
function chercherSequence(cmp, motif, depuis = 0, tolerance = 0) {
  if (!motif.length) return -1;
  for (let i = depuis; i + motif.length <= cmp.length; i++) {
    if (!clefEgale(cmp[i], motif[0])) continue;
    let ecarts = 0;
    for (let k = 1; k < motif.length && ecarts <= tolerance; k++) if (!clefEgale(cmp[i + k], motif[k])) ecarts++;
    if (ecarts <= tolerance) return i;
  }
  return -1;
}

// L'extrait de `texte` qui va du premier `debut` au `fin` qui le suit ; rend le
// texte source intact (nikoud compris), ou null si une borne manque.
export function extraire(texte, debut, fin) {
  if (!debut) return null;
  const toks = motsAvecPositions(String(texte || ''));
  const { cmp, proprio } = sequenceComparable(toks);
  const mD = sequenceComparable(motsAvecPositions(debut)).cmp;
  const iD = chercherSequence(cmp, mD);
  if (iD === -1) return null;
  let iFinCmp = iD + mD.length - 1;
  if (fin) {
    const mF = sequenceComparable(motsAvecPositions(fin)).cmp;
    const iF = chercherSequence(cmp, mF, iD + mD.length);
    if (iF === -1) return null;
    iFinCmp = iF + mF.length - 1;
  }
  const t0 = toks[proprio[iD]], t1 = toks[proprio[iFinCmp]];
  return texte.slice(t0.debut, t1.fin + 1).trim();
}

// Décisionnaires que le modèle aime nommer, avec les formes sous lesquelles les
// sources les écrivent (sans guillemets ni nikoud). Un nom est « sourcé » si
// l'une de ses formes figure dans un texte ouvert — les références comprises :
// ouvrir le HaRav suffit à nommer l'Admour.
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
  ['Maguid Michné', /\bmaguid\s+michn[eé]\b|\bmaggid\s+mishneh\b|מגיד משנה/i,  ['מגיד משנה', 'המגיד', 'הה']],
  ['Tour',          /\btour\b|\btur\b|הטור/i,                                   ['הטור', 'רבינו']],
  ['Michna Beroura', /\bmichna\s+b[ée]roura\b|\bmishnah?\s+berurah?\b|מ[״"]ב\b|משנה ברורה/i, ['משנה ברורה', 'מב', 'Mishnah_Berurah']],
  ['Admour HaZaken', /\badmou?r\s+ha-?zaken\b|\balter\s+rebbe\b|אדמו[״"]ר הזקן|שו[״"]ע הרב|(?:choul['’]?han|shulchan)\s+arou?kh?\s+ha-?rav/i, ['Shulchan_Arukh_HaRav', 'שוע הרב', 'אדמור']],
];

function textesDuResultat(brut) {
  const out = [];
  const visite = (x) => {
    if (typeof x === 'string') { if (x.length >= 12) out.push(x); return; }
    if (Array.isArray(x)) { x.forEach(visite); return; }
    if (x && typeof x === 'object') Object.values(x).forEach(visite);
  };
  try { visite(JSON.parse(brut)); } catch { if (typeof brut === 'string') out.push(brut); }
  return out;
}

const nbMots = (t) => normaliser(t).split(' ').filter(Boolean).length;

export class FiltreLivraison {
  constructor({ sources = [], lang = 'fr', fetchTexte = fetchSefariaText, fetchSegments = fetchSefariaSegments } = {}) {
    this.lang = lang;
    this.fetchTexte = fetchTexte;
    this.fetchSegments = fetchSegments;
    this.pool = '';          // textes ouverts, normalisés
    this.poolCmp = [];       // les mêmes, en clefs comparables (pour la recherche tolérante)
    this.refs = '';          // références ouvertes (noms latins des œuvres)
    this.tampon = '';
    this.aRecu = false;
    this.stats = { collees: 0, introuvables: 0, refCorrigees: 0, retrouves: 0, nonRetrouves: 0, horsSources: [] };
    this.nomsSignales = new Set();
    for (const s of sources) this.ajouterSource(s.ref, s.texte);
  }

  ajouterSource(ref, texte) {
    const n = normaliser(texte);
    if (n) { this.pool += ' ' + n + ' '; this.poolCmp.push(...sequenceComparable(motsAvecPositions(String(texte))).cmp); }
    if (ref) this.refs += ' ' + String(ref) + ' ';
  }

  // À appeler après chaque ronde d'outils : tout ce que le modèle a ouvert
  // devient une source, pour l'hébreu libre et les noms.
  ajouterResultats(toolUses = [], toolResults = []) {
    toolResults.forEach((r, i) => {
      if (!r || r.is_error) return;
      const tu = toolUses[i] || {};
      const ref = tu.input && (tu.input.ref || tu.input.id || tu.input.query) || tu.name || '';
      for (const t of textesDuResultat(r.content)) this.ajouterSource(ref, t);
    });
  }

  // Le passage est-il dans les textes ouverts ? Exact d'abord ; sinon mot à mot,
  // en tolérant une différence sur huit (la coquille « דעם » de Sefaria).
  dansLesSources(passage) {
    const n = normaliser(passage);
    if (!n) return true;
    if (this.pool.includes(' ' + n + ' ') || this.pool.includes(n)) return true;
    const motif = sequenceComparable(motsAvecPositions(passage)).cmp;
    if (motif.length < 3) return false;
    return chercherSequence(this.poolCmp, motif, 0, Math.floor(motif.length / 8)) !== -1;
  }

  nomSource(formes) {
    const sansEspaces = this.pool.replace(/ /g, '');
    return formes.some((f) => /^[A-Za-z_]/.test(f) ? this.refs.includes(f) : this.pool.includes(' ' + normaliser(f) + ' ') || sansEspaces.includes(normaliser(f).replace(/ /g, '')));
  }

  // Colle les citations désignées. Rend le paragraphe transformé et les spans
  // collés (pour ne pas les re-vérifier comme hébreu libre).
  async collerCitations(paragraphe) {
    const marqueurs = [...paragraphe.matchAll(MARQUEUR_RE)];
    if (!marqueurs.length) return { texte: paragraphe, colles: [] };
    let texte = paragraphe;
    const colles = [];
    for (const m of marqueurs) {
      const ref = m[1].trim().replace(/\s+/g, '_');
      const plage = (m[2] || '').trim();
      const segs = plage.split(/…|\.\.\./).map((x) => x.trim()).filter(Boolean);
      const debut = segs[0] || '', fin = segs.length > 1 ? segs[segs.length - 1] : '';   // plusieurs « … » : les deux bouts
      let remplacement;
      try {
        const d = await this.fetchTexte(ref);
        if (!d || d.error || !d.hebrew) remplacement = `[citation introuvable : ${ref}]`;
        else {
          let he = String(d.hebrew).replace(/<[^>]+>/g, '').trim();
          if (plage) {
            let extrait = extraire(he, debut, fin);
            if (!extrait) {
              // Le modèle devine souvent le numéro de paragraphe du Beit Yossef
              // (il suit le Tour, pas les séifim) : on cherche dans le siman entier
              // et on dit où c'était vraiment.
              const parent = ref.match(/^(.+\.\d+)\.\d+$/);
              if (parent) {
                const sg = await this.fetchSegments(parent[1]).catch(() => null);
                const segments = sg && !sg.error && Array.isArray(sg.segments) ? sg.segments : [];
                for (let k = 0; k < segments.length && !extrait; k++) {
                  const e = extraire(segments[k], debut, fin);
                  if (e) { extrait = `${e} _[réf. exacte : ${parent[1]}.${k + 1}]_`; this.stats.refCorrigees += 1; }
                }
              }
            }
            // Les bornes sont de l'hébreu tapé par le modèle : si elles ne sont dans
            // aucun paragraphe, c'est précisément l'erreur qu'on veut voir.
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
      else {
        this.stats.collees += 1; colles.push(remplacement);
        this.ajouterSource(ref, remplacement);   // un texte collé est une source ouverte : les noms qu'il porte sont sourcés
      }
      texte = texte.replace(m[0], remplacement);
    }
    return { texte, colles };
  }

  // L'hébreu que le modèle a tapé lui-même, s'il a la forme d'une citation.
  verifierHebreuLibre(texte, colles) {
    let masque = texte;
    const sauvegarde = [];
    const cacher = (c) => { if (!c) return; sauvegarde.push(c); masque = masque.split(c).join(`\u0000${sauvegarde.length - 1}\u0000`); };
    for (const c of colles) cacher(c);                                                   // du Sefaria, pas du modèle
    for (const m of texte.match(/\[(?:extrait non trouvé|citation introuvable|citation interrompue)[^\]]*\]/g) || []) cacher(m);   // les messages du serveur
    const controler = (run, minMots) => {
      if (nbMots(run) < minMots) return run;
      if (this.dansLesSources(run)) { this.stats.retrouves += 1; return run; }
      this.stats.nonRetrouves += 1;
      return run.trimEnd() + ' ⚠️ [non retrouvé dans les sources ouvertes] ';
    };
    // Le paragraphe est-il une prose en hébreu ? Alors sa prose n'est pas une
    // citation : on ne regarde que les guillemets et les blocs « > ».
    const heb = (masque.match(/[א-ת]/g) || []).length, lat = (masque.match(/[A-Za-zÀ-ÿ]/g) || []).length;
    const proseHebraique = heb > lat * 1.5;
    const zones = [];
    masque = masque.replace(ZONES_CITATION_RE, (z) => { zones.push(z.replace(PASSAGE_RE, (run) => controler(run, MOTS_MIN_EN_CITATION))); return `\u0001${zones.length - 1}\u0001`; });
    if (!proseHebraique) {
      masque = masque.replace(PASSAGE_RE, (run) => {
        const morceaux = run.split(/[,;:«»"'’]+/).map(nbMots).filter((n) => n > 0);
        const total = morceaux.reduce((a, b) => a + b, 0), plusLong = Math.max(0, ...morceaux);
        // Une phrase d'un seul tenant, ou deux morceaux assez longs : à vérifier.
        // Une liste de termes (plusieurs morceaux courts) : non.
        if (plusLong >= MOTS_MIN_HORS_CITATION || (morceaux.length <= 2 && total >= MOTS_MIN_TOTAL_HORS)) return controler(run, 1);
        return run;
      });
    }
    masque = masque.replace(/\u0001(\d+)\u0001/g, (_, i) => zones[Number(i)]);
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
    this.aRecu = true;
    this.tampon += delta;
    const ouvert = this.tampon.lastIndexOf('[[cite:');
    if (ouvert !== -1 && this.tampon.indexOf(']]', ouvert) === -1) return '';   // marqueur ouvert : on attend sa fin
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
      // jamais atteindre le lecteur.
      const reste = this.tampon.replace(/\[\[cite:[^\]]*$/, (m) => { this.stats.introuvables += 1; return `[citation interrompue : ${m.slice(7).split('|')[0].trim()}]`; });
      sortie += await this.traiterParagraphe(reste);
      this.tampon = '';
    }
    if (!this.aRecu && !sortie.trim()) return '';   // rien reçu : pas de pied à zéro devant l'avis d'interruption
    return sortie + this.pied();
  }

  pied() {
    const s = this.stats;
    const pl = (n, mot, pluriel = mot + 's') => `${n} ${n > 1 ? pluriel : mot}`;
    const hors = s.horsSources.length ? s.horsSources.join(', ') : null;
    const L = {
      fr: `\n\n---\n_Vérification serveur : ${pl(s.collees, 'citation collée', 'citations collées')} depuis Sefaria${s.refCorrigees ? ` (${pl(s.refCorrigees, 'référence corrigée', 'références corrigées')})` : ''} · ${pl(s.retrouves, 'passage hébreu retrouvé', 'passages hébreux retrouvés')} dans les sources ouvertes · ${pl(s.nonRetrouves, 'non retrouvé')}${s.introuvables ? ` · ${pl(s.introuvables, 'référence introuvable', 'références introuvables')}` : ''}${hors ? ` · noms hors sources : ${hors}` : ''}._`,
      he: `\n\n---\n_אימות שרת: ${s.collees} ציטוטים הודבקו מספריא${s.refCorrigees ? ` (${s.refCorrigees} הפניות תוקנו)` : ''} · ${s.retrouves} קטעים עבריים נמצאו במקורות שנפתחו · ${s.nonRetrouves} לא נמצאו${s.introuvables ? ` · ${s.introuvables} הפניות לא נמצאו` : ''}${hors ? ` · שמות שאינם במקורות: ${hors}` : ''}._`,
      en: `\n\n---\n_Server check: ${pl(s.collees, 'quotation')} pasted from Sefaria${s.refCorrigees ? ` (${pl(s.refCorrigees, 'reference')} corrected)` : ''} · ${pl(s.retrouves, 'Hebrew passage')} found in the opened sources · ${s.nonRetrouves} not found${s.introuvables ? ` · ${pl(s.introuvables, 'reference')} not found` : ''}${hors ? ` · names outside the sources: ${hors}` : ''}._`,
    };
    return L[this.lang] || L.fr;
  }
}
