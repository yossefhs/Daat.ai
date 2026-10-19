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
const MIN_MOTS_HEBREU = 5;          // en dessous, un libellé (« על גבה ולא לתוכה »), pas une citation — banc du 19/10
const MARQUEUR_RE = /\[\[cite:([^\]|]+?)(?:\|([^\]]*?))?\]\]/g;
// Quatre mots hébreux ou plus, la ponctuation ordinaire entre eux comprise
// (« אחד, שנים : שלש. ארבע » est un seul passage — relecture Codex #284).
const HEBREU_RE = /(?:[\u0590-\u05FF][\u0590-\u05FF״׳"'’\-־]*[\s,.;:!?()«»"'’]*){5,}/g;

export function normaliser(t) {
  return String(t || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[֑-ׇ]/g, '')                    // nikoud et te'amim
    .replace(/[״׳"'“”‘’«»,.;:!?()\[\]{}־–—…\-/\\|*#_`]/g, ' ')
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
            const segs = plage.split(/…|\.\.\./).map((x) => x.trim()).filter(Boolean);
            const debut = segs[0] || '', fin = segs.length > 1 ? segs[segs.length - 1] : '';   // plusieurs « … » : on garde les deux bouts
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
    // Masquer ce que le serveur vient de coller (c'est du Sefaria, pas du modèle)
    // et ses propres messages (ils citent les bornes du modèle).
    let masque = texte;
    const sauvegarde = [];
    const cacher = (c) => { if (!c) return; sauvegarde.push(c); masque = masque.split(c).join(`\u0000${sauvegarde.length - 1}\u0000`); };
    for (const c of colles) cacher(c);
    for (const m of texte.match(/\[(?:extrait non trouvé|citation introuvable|citation interrompue)[^\]]*\]/g) || []) cacher(m);
    const controler = (run) => {
      if (normaliser(run).split(' ').length < MIN_MOTS_HEBREU) return run;
      if (this.dansLesSources(run)) { this.stats.retrouves += 1; return run; }
      this.stats.nonRetrouves += 1;
      return run.trimEnd() + ' ⚠️ [non retrouvé dans les sources ouvertes] ';
    };
    if (this.lang === 'he') {
      // Réponse en hébreu : la prose EST en hébreu. Seuls les passages donnés
      // comme citations (guillemets, blocs « > ») sont des citations.
      masque = masque.replace(/«[^»\n]{8,}»|"[^"\n]{8,}"|״[^״\n]{8,}״|“[^”\n]{8,}”|^>.+$/gm, (zone) => zone.replace(HEBREU_RE, controler));
    } else {
      masque = masque.replace(HEBREU_RE, controler);
    }
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
    // Rien reçu (génération interrompue avant le premier mot) : pas de pied à zéro
    // devant l'avis d'interruption que chat.js écrit ensuite.
    if (!this.aRecu && !sortie.trim()) return '';
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

// ── Localiser un extrait par ses bornes ─────────────────────────────────────
// Le banc du 19/10 : sur 32 bornes « non trouvées », 15 étaient présentes mot
// pour mot (l'ancien extracteur traitait les guillemets d'abréviation autrement
// que normaliser()), 14 ne différaient que par l'orthographe pleine/défective
// (Sefaria écrit le HaRav en haser : קדרה, עדין, מרבה), 4 portaient plusieurs
// « … », 3 seulement visaient un mauvais séif. On compare donc des SÉQUENCES DE
// MOTS : abréviations développées (וי"א → ויש אומרים), ו/י retirés, et l'on rend
// le texte source intact (nikoud compris) entre le premier et le dernier mot.
const ABR_BORNES = { 'ויא': 'ויש אומרים', 'יא': 'יש אומרים', 'עג': 'על גבי', 'אעפ': 'אף על פי', 'אעפכ': 'אף על פי כן', 'אכ': 'אם כן', 'אאכ': 'אלא אם כן', 'מבעי': 'מבעוד יום', 'בעש': 'בערב שבת', 'מש': 'מוצאי שבת', 'למש': 'למוצאי שבת', 'ממ': 'מכל מקום', 'וממ': 'ומכל מקום', 'כש': 'כל שכן', 'וכש': 'וכל שכן', 'הה': 'הוא הדין', 'והה': 'והוא הדין', 'והמ': 'והני מילי', 'וכ': 'וכתב', 'וככ': 'וכן כתב', 'ככ': 'כן כתב', 'פי': 'פירוש', 'אפי': 'אפילו', 'ואפי': 'ואפילו', 'סי': 'סימן', 'וכו': 'וכולי', 'זל': 'זכרונו לברכה', 'גה': 'גיד הנשה', 'סהת': 'ספר התרומה', 'שע': 'שולחן ערוך', 'בי': 'בית יוסף', 'רל': 'רוצה לומר', 'דה': 'דברי הכל', 'לדה': 'לדברי הכל' };
const SEP_RE = /[\s֑-ׇ“”‘’«»,.;:!?()\[\]{}־–—…\-/\\|*#_`<>]/;   // ״ ׳ " ' restent dans le mot (abréviations)
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
  const nu = mot.replace(/[״׳"'’]/g, '');
  return squelette(ABR_BORNES[nu] || nu).split(' ').filter(Boolean);
}
function sequenceComparable(toks) {
  const cmp = [], proprio = [];
  toks.forEach((t, j) => { for (const k of clefs(t.mot)) { cmp.push(k); proprio.push(j); } });
  return { cmp, proprio };
}
function chercherSequence(cmp, motif, depuis = 0) {
  if (!motif.length) return -1;
  for (let i = depuis; i + motif.length <= cmp.length; i++) {
    let ok = true;
    for (let k = 0; k < motif.length; k++) if (cmp[i + k] !== motif[k]) { ok = false; break; }
    if (ok) return i;
  }
  return -1;
}
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
