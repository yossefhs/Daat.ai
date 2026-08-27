// Recherche BM25 dans le corpus Shabbat (1500+ chunks).
// Utilisé par /api/chat-corpus (endpoint dédié) et — à terme — par /api/chat
// comme premier filtre avant routage Opus/Sonnet.
//
// Tokenisation FR + hébreu, stopwords, synonymes halakhiques, garde-fou keyToken.

import { readFileSync } from 'node:fs';
import { brotliDecompressSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CORPUS_PATH = join(__dirname, '..', 'data', 'corpus-shabbat.json');
// Tokenisation précalculée par scripts/extract-corpus.js — sortie de build.
const INDEX_PATH = join(__dirname, '..', 'data', 'corpus-index.br');

// ── Empreinte du tokeniseur ─────────────────────────────────────────────────
// L'index précalculé dérive de DEUX choses : le corpus ET tokenize(). L'empreinte
// du corpus ne dit rien du second. Or SPELLING_CANON, SYNONYMS, MULTIWORD,
// STOPWORDS, NON_TOPICAL et preNormalize sont retouchés sans arrêt dans ce
// fichier. Si l'un change sans que le build soit relancé, le corpus reste indexé
// avec l'ANCIEN tokeniseur pendant que la question de l'utilisateur passe par le
// NOUVEAU : les deux côtés du BM25 ne parlent plus la même langue, et rien ne le
// signale. Mesuré : ajouter la graphie « mouktse » sans régénérer fait entrer les
// simanim 259 (רנ״ט) et 279 (רע״ט) dans les cinq premiers et en chasse le 343
// (שמ״ג) et le 310 (ש״י).
//
// Un TEXTE TÉMOIN passé au tokeniseur ne suffit pas — essayé, et mis en défaut
// par ce cas même : il ne détecte que les règles qu'il exerce par hasard, et une
// graphie ajoutée pour un mot absent du témoin reste invisible. On prend donc
// l'empreinte du FICHIER SOURCE : toute retouche, fût-elle d'un commentaire,
// invalide l'index. C'est délibérément trop sensible. Le déséquilibre le
// commande : un faux repli coûte 2 secondes en local et rien en production (où
// chaque déploiement rebâtit), tandis qu'une fausse acceptation coûte une
// réponse halakhique fausse servie avec aplomb.
const SELF_PATH = fileURLToPath(import.meta.url);
let _tokSig = null;
export function tokenizerSignature() {
  if (!_tokSig) {
    try {
      _tokSig = createHash('sha1').update(readFileSync(SELF_PATH, 'utf-8')).digest('hex').slice(0, 16);
    } catch { _tokSig = 'illisible'; }
  }
  return _tokSig;
}

let _corpus = null;
let _idf = null;
let _df = null;   // fréquence documentaire brute — sert au plancher du portail
let _avgdl = 0;
let _N = 0;

const STOPWORDS = new Set([
  'le','la','les','de','des','du','et','ou','un','une','en','a','au','aux',
  'que','qu','qui','quoi','ce','cette','ces','est','sont','etre','avoir','pas','ne',
  'on','je','tu','il','elle','nous','vous','ils','elles','se','sa','son','ses',
  'mon','ma','mes','ton','ta','tes','dans','sur','par','pour','avec','sans',
  'mais','donc','car','si','plus','moins','tres','peu','tout','tous','toute',
  'comment','pourquoi','quand','ou','y','d','l','s','c','j','m','n','t',
  'ca','oui','non','apres','avant','ici','meme','aussi',
  'fait','faire','faut','peut','peuvent','dire','dit','quel','quelle',
  'the','an','of','to','in','is','are','was','were','be','been','this','that',
  // Mots vides ajoutés après l'incident borer : sans eux, « ai-je le droit de
  // faire cuire » retenait « ai » et « droit » comme tokens-clés (les mots de plus
  // haute IDF servent de portail) et le mot porteur « cuire » était ignoré.
  'ai','as','ont','avons','avez','avait','avais','etait','etais','suis','es','sommes','etes',
  'me','te','lui','leur','eux','moi','toi','soi','en','y',
  'chez','vers','depuis','pendant','entre','sous','hors','contre','selon',
  'quelque','quelques','chose','choses','truc','trucs','maniere','facon',
  'veux','veut','veulent','voulais','vouloir','voudrais',
  'dois','doit','doivent','devoir','devrais',
  'puis','peux','pouvez','pouvons','pourrais','pouvoir','pourra',
  'droit','besoin','envie','possible','permission',
  'autre','autres','tel','telle','tels','telles','certains','certaines',
  'falloir','faudrait','faisant','faites','fais',
  'maintenant','aujourd','hui','hier','demain','alors','ensuite','puisque',
  'merci','bonjour','shalom','svp','question','savoir','explique','expliquer',
  // Conjugaisons manquantes : la liste ne couvrait que le présent. « pouvait »,
  // « disait », « fallait » sont rares dans le corpus donc à FORT IDF — ils
  // devenaient le portail à la place du vrai mot de sujet.
  'pouvait','pouvaient','pouvais','devait','devaient','devais','fallait','faudra',
  'avait','avaient','avais','etait','etaient','etais','voulait','voulaient',
  'faisait','faisaient','mettait','allait','venait','savait','sait','saurait',
  'aurait','serait','ferait','pourrait','devrait','disait','disaient','disais',
  'vraiment','juste','simplement','peut-etre','environ','sorte',
]);

// Expressions multi-mots, normalisées AVANT la tokenisation. Sans cela « pommes
// de terre » matche « pommes » (le fruit, siman 290 berakhot) — c'est exactement
// ce qui a fait manquer le siman 319 sur une question de borer.
const MULTIWORD = [
  [/pommes?\s+de\s+terre/g, 'pommedeterre'],
  [/petits?\s+pois/g, 'petitspois'],
  [/papier\s+(?:hygienique|toilette)/g, 'papiertoilette'],
  [/eau\s+chaude/g, 'eauchaude'],
  [/mal\s+(?:a\s+la\s+|de\s+)?tete/g, 'maltete'],
  [/mal\s+au\s+ventre/g, 'malventre'],
  [/lait\s+maternel/g, 'laitmaternel'],
  [/machine\s+a\s+laver/g, 'machinelaver'],
  [/salle\s+de\s+bain/g, 'sallebain'],
  [/eau\s+bouillante/g, 'eaubouillante'],
];

const SYNONYMS = {
  'cuisson': ['bishoul'],
  'chauffer': ['bishoul','rechauffer'], 'rechauffer': ['bishoul','ein'],
  'cholent': ['bishoul','hatmana'], 'chamin': ['bishoul','hatmana'],
  'theboisson': ['iroui','liquide','eaubouillante'], 'cafe': ['iroui','liquide'],
  'eau': ['liquide','mayim'], 'temperature': ['yad','soledet','chaud'],
  'trier': ['borer','tri'], 'separer': ['borer','separation'],
  'salade': ['aliments','okhel'], 'passoire': ['tamis','crible','instrument'],
  'eplucher': ['epluchage','derekh','akhila'],
  'mouktse': ['muqtse','mouqtse','deplacement'], 'deplacer': ['mouktse','tiltoul','porter'],
  'porter': ['mouktse','tiltoul'], 'objet': ['mouktse','kli'],
  'casser': ['nolad','brise'], 'argent': ['kis','hisaron'],
  'shabbat': ['chabbat','sabbat','shabbos'], 'chabbat': ['shabbat','sabbat','shabbos'],
  'shabbos': ['shabbat','chabbat'],
  'permis': ['mutar'], 'interdit': ['assour','isour'],
  'vaisselle': ['kelim','plat','ustensile'],
  'cuir': ['bishoul'], 'rotir': ['bishoul','tsoli'],
  'mehaber': ['choulhan','aroukh','maran'], 'rama': ['rama','ashkenaze'],
  'nouer': ['qosher','noeud'], 'noeud': ['qosher'],
  'ecrire': ['kotev','ecriture'], 'effacer': ['mohek'],
  'allumer': ['mavir','feu'], 'eteindre': ['mekhabe','feu'],
  'electricite': ['hashmal','electrique'],
  // ── Vocabulaire réel des utilisateurs (ajouté après l'incident borer 2026-07) ──
  // Le corpus est écrit en langue halakhique ; les gens écrivent en langue courante.
  // ⚠️ 'retirer' / 'enlever' / 'oter' N'ONT PLUS de synonyme inconditionnel vers
  // « borer » : ce sont les verbes les plus banals du français, et ils envoyaient
  // n'importe quelle question vers le siman 319 (« enlever ses chaussures »,
  // « retirer les tefilin »). Le borer reste couvert — mais par la RÈGLE de
  // co-occurrence ci-dessous, qui exige en plus un contexte alimentaire.
  'melange': ['melanges','tri','תערובת'], 'melanges': ['tri','תערובת'], 'melangee': ['tri','תערובת'],
  'pesolet': ['psolet','dechet'], 'psolet': ['pesolet','dechet'],
  'raper': ['tohen','moudre','broyer'], 'moudre': ['tohen'], 'ecraser': ['tohen','lash','broyer'],
  'hacher': ['tohen','couper'], 'broyer': ['tohen'], 'mixer': ['tohen'],
  'medicament': ['malade','refoua','remede','soin'], 'cachet': ['malade','refoua','remede'],
  'comprime': ['malade','refoua','remede'], 'fievre': ['malade','soin','refoua'],
  'malade': ['refoua','soin','maladie'], 'douleur': ['malade','soin','refoua'],
  'maltete': ['malade','refoua','soin'], 'malventre': ['malade','refoua','soin'],
  'soigner': ['malade','refoua','soin'], 'medecin': ['malade','refoua'],
  'doucher': ['laver','rehitsa','bain'], 'douche': ['laver','rehitsa','bain'],
  'laver': ['rehitsa','bain','ablution'], 'bain': ['rehitsa','laver'], 'sallebain': ['rehitsa','laver'],
  'baigner': ['rehitsa','laver','bain'],
  'creme': ['sikha','oindre','huile','pommade','חלב'], 'pommade': ['sikha','oindre'],
  'parfum': ['sikha','besamim'], 'oindre': ['sikha'],
  // ⚠️ 'femme' retiré : c'est un mot de CONTEXTE omniprésent (nidah, tsitsit,
  // tefila…), pas un indice de bijou.
  'bijou': ['bijoux','ornement','takhchit'], 'bijoux': ['ornement','takhchit'],
  'bague': ['bijoux','ornement','takhchit'], 'collier': ['bijoux','ornement','takhchit'],
  'boucle': ['bijoux','ornement','takhchit'], 'montre': ['bijoux','ornement','takhchit'],
  'incendie': ['feu','dlika','sauvetage'], 'brule': ['feu','incendie'], 'flamme': ['feu'],
  'pain': ['lehem','pat','michne','hamotsi','pains'], 'pains': ['lehem','michne'],
  'bougies': ['bougie','hadlaka','allumage','nerot'], 'bougie': ['hadlaka','allumage','nerot'],
  'bougeoir': ['bougie','chandelier','mouktse','deplacement'], 'chandelier': ['bougie','bougeoir'],
  'heure': ['moment','zman','horaire'], 'moment': ['zman','heure'],
  'cuire': ['bishoul','mevashel','cuisson'], 'cuisiner': ['bishoul','mevashel','cuisson'],
  'plata': ['kira','plaque','hatmana'], 'plaque': ['kira','plata','hatmana'],
  'casserole': ['kira','kedera','marmite'],
  'ongles': ['ongle','preparatifs'],
  'mouche': ['tsida','capturer','insecte'], 'attraper': ['tsida','capturer'],
  'lacets': ['qosher','noeud','nouer'], 'balayer': ['balai','maison','nettoyer'],
  'circoncision': ['mila','brit'], 'sauver': ['pikouah','nefesh','sauvetage'],
  'voyage': ['voyageur','chemin','route'],
  'havdala': ['avdala','besamim'], 'epices': ['besamim','avdala'],

  // ══ ORAH HAÏM QUOTIDIEN (simanim 1-185) ══════════════════════════════════
  // Le lexique ci-dessus a été écrit quand le corpus ne couvrait QUE Hilkhot
  // Shabbat. Le corpus couvre désormais 359 simanim, dont toute la journée du
  // juif : sans ces entrées, deux tiers du corpus n'étaient atteignables que par
  // hasard, et les questions correspondantes partaient sur un siman de Shabbat.
  'reveil': ['lever','matin','hashkamat'], 'lever': ['hashkamat','matin'],
  'mains': ['yadayim','netilat','netila'], 'main': ['yadayim','netilat'],
  'ongle': ['yadayim','netilat'],
  'toilettes': ['bethakisse','asher','yatsar'], 'besoin': ['asher','yatsar'],
  'chaussure': ['naalayim','habillement'], 'chaussures': ['naalayim','habillement'],
  'habiller': ['levicha','vetement','tsniout'], 'kippa': ['couvrir','tete','yirat'],
  'chale': ['talit','tsitsit'], 'franges': ['tsitsit','fils','tsitsiyot'],
  'fils': ['tsitsit','houtim'], 'coins': ['kanfot','talit','tsitsit'],
  'phylacteres': ['tefilin','batim','retsouot'], 'boitier': ['tefilin','batim'],
  'lanieres': ['retsouot','tefilin'], 'bras': ['tefilin','yad'], 'tete': ['tefilin','roch'],
  'parchemin': ['klaf','parachiot','ecriture'],
  'priere': ['tefila','amida','chemone'], 'prier': ['tefila','amida'],
  'office': ['tefila','minyan','tsibbour'], 'offices': ['tefila','minyan'],
  'matinale': ['chaharit','matin'], 'apresmidi': ['minha'],
  'benir': ['berakha','bendire'], 'benedicite': ['berakha','hamotsi'],
  'amen': ['berakha','repondre','ania'],
  'quorum': ['minyan','tsibbour','dix'], 'assemblee': ['tsibbour','minyan'],
  'officiant': ['chatz','cheliah','tsibbour'], 'hazan': ['chatz','cheliah'],
  'lecture': ['keriat','torah','sefer'], 'rouleau': ['sefer','torah','keria'],
  'monter': ['alia','torah','keria'], 'appele': ['alia','torah'],
  'silencieuse': ['amida','lahach'], 'repetition': ['hazarat','chatz','amida'],
  'erreur': ['taout','tromper','hozer'], 'trompe': ['taout','hozer'],
  'oublie': ['chakhah','taout','hozer'], 'recommencer': ['hozer','taout'],
  'intention': ['kavana','kaven'], 'concentration': ['kavana'],
  'interrompre': ['hefsek','hafsaka'], 'parler': ['hefsek','dibbour'],
  'repas': ['seouda','akhila','pat'],
  'manger': ['akhila','seouda','okhel'], 'boire': ['chetiya','mayim'],
  'vin': ['yayin','kos','guefen'], 'fruits': ['peirot','haets'],
  'legumes': ['yerakot','haadama'], 'gateau': ['mezonot','pat'],
  'mezouza': ['mezouzot','porte','klaf'], 'porte': ['mezouza','petah'],

  // ══ YOREH DE'AH — CACHEROUTE (87-118) ════════════════════════════════════
  // Les pages de cette section sont largement rédigées en HÉBREU : le lexique
  // doit traduire le français de l'utilisateur vers les mots réellement indexés
  // (mesuré : בששים df=115, נבילה df=101, חריף df=87 ; « taarovet » df=2).
  'viande': ['בשר','bassar','carne'], 'lait': ['חלב','halav','laitage'],
  'laitage': ['חלב','halav'], 'fromage': ['גבינה','חלב','halav'],
  'beurre': ['חמאה','חלב'],
  'melanger': ['תערובת','taarovet','bitoul'], 'melangeant': ['תערובת'],
  'annuler': ['בטל','bitoul','בששים'], 'annulation': ['בטל','bitoul','בששים'],
  'soixante': ['בששים','bitoul','chichim'], 'proportion': ['בששים','hechbon'],
  'tombe': ['נפל','תערובת'], 'gout': ['טעם','נותן','taam'],
  'attendre': ['שעות','המתנה','attente'], 'attente': ['שעות','המתנה'],
  'heures': ['שעות','המתנה'], 'ustensile': ['כלי','kli','kelim'],
  'marmite': ['kira','kedera','plata','קדרה'], 'couteau': ['סכין','sakin','חריף'],
  'piquant': ['חריף','davar','sakin'], 'oignon': ['חריף','bassal'],
  'sale': ['מליחה','melicha','salage'], 'saler': ['מליחה','melicha'],
  'cachere': ['כשר','casher','heter'], 'casher': ['כשר','heter','cacheroute'],
  'cacheroute': ['כשר','איסור','היתר'], 'traife': ['טרפה','נבילה','איסור'],
  'interdiction': ['איסור','issour'], 'permission': ['היתר','heter'],
  'four': ['תנור','tanour','ריחא'], 'odeur': ['ריחא','reiha'],
  'insecte': ['tsida','capturer','animal','תולעים'],


  // ══ YOREH DE'AH — NIDAH / TAHARAT HA-MISHPAHA (183-200) ══════════════════
  // Section rédigée à ~80 % en hébreu, sans aucune translittération française
  // (mesuré : « ketamim » df=0, « harhakot » df=0, mais כתמים df=35, הרחקות df=52).
  // Sans ces traductions, la section était littéralement inatteignable.
  'regles': ['וסת','וסתות','נדה','veset'], 'periode': ['וסת','וסתות'],
  'cycle': ['וסת','וסתות','vesatot'], 'menstruation': ['נדה','וסת','דם'],
  'sang': ['דם','נדה','ראתה'], 'saignement': ['דם','ראתה','נדה'],
  'tache': ['כתם','כתמים','ketem'], 'taches': ['כתמים','כתם'],
  'impure': ['טמאה','נדה','touma'], 'pure': ['טהורה','טהרה','tahara'],
  'purete': ['טהרה','טהורה','tahara'], 'purification': ['טהרה','טבילה'],
  'separation': ['הרחקות','harhakot','perisha'], 'eloignement': ['הרחקות','perisha'],
  'toucher': ['הרחקות','נגיעה'],
  'immersion': ['טבילה','מקוה','tevila'], 'tremper': ['טבילה','מקוה'],
  // Familles des ANCRES dont le corpus est rédigé en hébreu : sans elles, l'ancre
  // ne désigne que les rares chunks où le mot est translittéré.
  'tevila': ['טבילה','מקוה'], 'mikve': ['מקוה','טבילה'], 'nidda': ['נדה','וסת','דם'],
  'taarovet': ['תערובת','בששים'], 'cacheroute': ['כשר','איסור','היתר'],
  'bassin': ['מקוה','טבילה'], 'sept': ['שבעה','נקיים','chiva'],
  'propres': ['נקיים','שבעה'], 'comptage': ['ספירה','נקיים','שבעה'],
  'examen': ['בדיקה','בדיקות','bedika'], 'verifier': ['בדיקה','בדיקות'],
  'linge': ['בדיקה','edim','כתם'], 'sousvetement': ['כתם','בדיקה'],
  'mari': ['בעל','הרחקות','ichto'], 'epouse': ['אשה','הרחקות'],
  'grossesse': ['מעוברת','וסת'], 'allaitement': ['מניקה','וסת'],
  'accouchement': ['יולדת','נדה'],

  // ══ PONT HÉBREU → FRANÇAIS ═══════════════════════════════════════════════
  // Le corpus est bilingue, mais chunk par chunk : un même siman a des chunks
  // français ET des chunks hébreux, rarement les deux dans le même. Une question
  // posée en hébreu n'atteignait donc que la fraction hébraïque du siman.
  // Mesuré sur « האם מותר לישון עם תפילין ? » : le siman 44 a 44 chunks, dont
  // 9 seulement contiennent תפילין et UN SEUL contient לישון — la question
  // tombait sur le siman 80. Ce pont traduit les mots de question les plus
  // courants vers leur équivalent français indexé, dans les deux sens.
  'לישון': ['dormir','sommeil','שינה'], 'לישן': ['dormir','sommeil','שינה'],
  'שינה': ['dormir','sommeil'], 'ישן': ['dormir','sommeil'],
  'מותר': ['permis','mutar'], 'אסור': ['interdit','assour'],
  'זמן': ['heure','moment','temps'], 'מתי': ['heure','moment','quand'],
  'לאכול': ['manger','akhila'], 'אכילה': ['manger','akhila'],
  'לשתות': ['boire','chetiya'], 'שתיה': ['boire'],
  'להדליק': ['allumer','hadlaka'], 'הדלקה': ['allumer','bougies','nerot'],
  'לכבות': ['eteindre'], 'לרחוץ': ['laver','rehitsa'], 'רחיצה': ['laver','rehitsa','bain'],
  'לבשל': ['cuire','bishoul'], 'בישול': ['cuire','cuisson'],
  'לטלטל': ['deplacer','tiltoul'], 'טלטול': ['deplacer','tiltoul'],
  'להוציא': ['sortir','hotsaa'], 'לשאת': ['porter'],
  'לברך': ['berakha','benir'], 'ברכה': ['berakha'], 'ברכות': ['berakha'],
  'להתפלל': ['tefila','prier','priere'], 'תפלה': ['tefila','priere'], 'תפילה': ['tefila','priere'],
  'לקרוא': ['lire','keriat'], 'קריאה': ['lire','keriat'],
  'לכתוב': ['ecrire','kotev'], 'כתיבה': ['ecrire','kotev'],
  'אשה': ['femme'], 'איש': ['homme'], 'ילד': ['enfant'], 'תינוק': ['bebe','enfant'],
  'חולה': ['malade','refoua'], 'רפואה': ['refoua','medicament','soin'],
  'בשר': ['viande','bassar'], 'חלב': ['lait','halav'], 'גבינה': ['fromage'],
  'נר': ['bougie','nerot'], 'נרות': ['bougies','bougie'],
  'שבת': ['shabbat','chabbat'], 'בשבת': ['shabbat','chabbat'],

  // ══ PONT ANGLAIS → FRANÇAIS ══════════════════════════════════════════════
  // Les pages -en.html existent mais NE SONT PAS indexées : le corpus est
  // français + hébreu (mesuré : 38 chunks sur 17 239 contiennent de l'anglais).
  // Les indexer doublerait le corpus et déplacerait toutes les fréquences, donc
  // tous les classements. Un pont lexical coûte zéro et suffit au vocabulaire —
  // borné et prévisible — des questions posées en anglais.
  'sleep': ['dormir','sommeil'], 'sleeping': ['dormir','sommeil'],
  'eat': ['manger','akhila'], 'eating': ['manger','akhila'], 'food': ['nourriture','aliments','okhel'],
  'drink': ['boire'], 'cook': ['cuire','bishoul'], 'cooking': ['cuire','bishoul'],
  'light': ['allumer','hadlaka'], 'lighting': ['allumer','hadlaka','bougies'],
  'candles': ['bougies','nerot','hadlaka'], 'candle': ['bougie','nerot'],
  'wash': ['laver','netilat','rehitsa'], 'washing': ['laver','netilat','rehitsa'],
  'hands': ['mains','yadayim','netilat'], 'hand': ['mains','yadayim'],
  'wear': ['porter'], 'wearing': ['porter'], 'carry': ['porter','tiltoul'],
  'move': ['deplacer','tiltoul'], 'moving': ['deplacer','tiltoul'],
  'allowed': ['permis','mutar'], 'permitted': ['permis','mutar'],
  'forbidden': ['interdit','assour'], 'prohibited': ['interdit','assour'],
  'morning': ['matin'], 'evening': ['soir'], 'night': ['nuit'],
  'time': ['heure','moment','zman'], 'when': ['heure','moment'],
  'prayer': ['tefila','priere'], 'pray': ['tefila','prier'],
  'blessing': ['berakha'], 'bless': ['berakha','benir'],
  'read': ['lire','keriat'], 'reading': ['lire','keriat'],
  'write': ['ecrire','kotev'], 'writing': ['ecrire','kotev'],
  'meat': ['viande','bassar'], 'milk': ['lait','halav'], 'dairy': ['lait','halav'],
  'cheese': ['fromage'], 'kosher': ['casher','cacheroute'],
  'sick': ['malade','refoua'], 'medicine': ['medicament','refoua'],
  'woman': ['femme'], 'wife': ['femme','epouse'], 'child': ['enfant'], 'baby': ['bebe'],
  'sort': ['trier','borer'], 'sorting': ['trier','borer'], 'separate': ['separer','borer'],
  'immersion': ['tevila','mikve'], 'stain': ['tache','ketem'],
};

// ── Règles de CO-OCCURRENCE ──
// Un mot isolé est ambigu ; la COMBINAISON ne l'est pas. « retirer » seul ne dit
// rien ; « retirer » + « mélange / plat / parmi » désigne sans ambiguïté le borer.
// C'est le levier principal : les questions réelles décrivent une SITUATION, pas
// une mélakha. Chaque règle n'ajoute des termes que si les deux familles sont là.
const CONCEPT_RULES = [
  { any: ['retirer','enlever','oter','sortir','separer','trier','choisir','prendre','isoler','ecarter'],
    ctx: ['melange','plat','assiette','salade','parmi','milieu','bol','morceaux','aliments','nourriture','petitspois','pommedeterre','legumes','fruits','poisson','arretes'],
    add: ['borer','berira','okhel','pesolet','tri'], w: 2.4 },
  { any: ['chaud','rechauffer','remettre','reposer','poser','mettre','met','mets',
          'placer','place','deposer','pose','remet','laisser','laisse'],
    ctx: ['plata','plaque','kira','marmite','casserole','four','feu','blech','rechaud'],
    add: ['hazara','kira','plata','hatmana','bishoul'], w: 2.0 },
  // 'prendre' RESTE dans le ctx : la règle exige déjà un mot médical dans `any`,
  // elle ne peut donc pas se déclencher sur « prendre » seul. Sans lui, « prendre
  // un médicament à Shabbat » — la formulation dominante — tombait sur le siman 308
  // (mouktsé) au lieu du 328 (le malade à Shabbat) : un faux issour sous une source.
  { any: ['mal','douleur','malade','fievre','soigner','medicament','cachet','comprime'],
    ctx: ['tete','ventre','gorge','dent','enfant','bebe','maltete','malventre','sirop','antibiotique','prendre'],
    add: ['malade','refoua','soin','maladie'], w: 2.2 },
  // ⚠️ ctx resserré : 'objet', 'argent', 'toucher', 'ranger' sont du vocabulaire
  // générique qui captait des questions de prière et de synagogue.
  { any: ['deplacer','bouger','ranger'],
    ctx: ['mouktse','bougie','bougeoir','chandelier','telephone','outil','casse','inutile'],
    add: ['mouktse','tiltoul','deplacement'], w: 1.8 },
  // ⚠️ 'femme' retiré du ctx : toute question contenant « femme » + « porter /
  // mettre / sortir » injectait bijoux/takhchit au poids 2.0 et faisait gagner le
  // siman 303, quel que soit le domaine réel de la question.
  { any: ['sortir','porter','mettre'],
    ctx: ['bijoux','bijou','bague','collier','boucle','ornement','montre','broche'],
    add: ['bijoux','ornement','takhchit'], w: 2.0 },
  { any: ['allumer','allumage','heure','moment','avant'],
    ctx: ['bougies','bougie','nerot','hadlaka'],
    add: ['hadlaka','bougies','zman','moment'], w: 1.8 },
  // דבר חריף — l'aliment piquant coupé au couteau (Yoreh De'ah 96). Une ancre
  // n'aide pas ici : elle est un OU, donc elle ÉLARGIT (mesuré : aucun effet).
  // « j'ai coupé un oignon avec le couteau à viande » était happée par le siman
  // 89 (l'attente entre viande et fromage), qui ne répond pas à la question.
  { any: ['couteau','coupe','couper','trancher','emince','rape'],
    ctx: ['oignon','ail','citron','radis','navet','piquant','harif','חריף','sakin','poireau','echalote'],
    add: ['חריף','סכין','sakin','harif'], w: 2.4 },
];

// Mots à FORT IDF mais SANS contenu de sujet. Ils décrivent la PROVENANCE d'un
// avis (minhag, nom de posek) ou la FAÇON dont l'utilisateur rapporte sa question
// (« dans le livre que j'ai lu il disait que… ») — jamais le sujet lui-même.
// Ils peuvent contribuer au SCORE, mais ne doivent JAMAIS servir de « portail »
// keyToken. Sinon une question sur le poisson sur la plata est gatée par
// « sefarades » + « disait » et ramène le siman 244 (travaux du non-juif).
const NON_TOPICAL = new Set([
  // minhag / provenance
  'sefarade','sefarades','sefarad','sfarade','sfarades','ashkenaze','ashkenazes',
  'askenaz','askenaze','askina','habad','chabad','loubavitch','lubavitch','litvak',
  'marocain','marocaine','yemenite','teimani','mizrah','edot','minhag','minhagim',
  'communaute','tradition',
  // noms de poskim : provenance d'un avis, pas le sujet
  'rama','rema','mehaber','maran','rambam','ramdam','ramban','rachi','rashi',
  'tossafot','tosafot','chakh','shakh','taz','beroura','berura','michna','mishna',
  'choulhan','shulchan','aroukh','arouh','admour','hazaken','rav','rabbi','gaon',
  'posek','poskim','rishonim','acharonim',
  // façon de RAPPORTER la question (pas son sujet)
  'livres','lu','entendu','entendre',
  'appris','disait','disent','disais','disaient','raconte','explique','expliquait',
  'parait','semble','pense','pensais','crois','croyais','vu','vois','accepte',
  'acceptait','tranche','tranchait','base','basent','selon',
  // ⚠️ 'ecrire', 'ecrit', 'lire', 'livre' et 'michna' ONT été retirés de cette
  // liste : écrits pour Hilkhot Shabbat, ils y étaient effectivement des mots de
  // rapport (« dans le livre que j'ai lu »). Depuis l'entrée d'Orah Haïm 1-185
  // dans le corpus, ce sont des mots de SUJET : écrire les tefilin (32, 36),
  // lire la Torah (135-145), lire le Chema (58-88), la michna « éézehou mekoman »
  // (50). Les bloquer rendait ces simanim inatteignables.
  // repères de TEMPS et verbes passe-partout : ils SITUENT la question, ils n'en
  // sont jamais le SUJET. Sans eux dans cette liste, « soir », « mettre » ou
  // « quelles » suffisait à ouvrir le portail keyToken — la soupape de sécurité
  // ne s'est donc jamais déclenchée sur une question mal formée.
  'soir','soiree','matin','matinee','midi','nuit','jour','journee','semaine',
  'hier','demain','aujourdhui','maintenant','tard','tot','apres','avant','pendant',
  'quelles','quels','quelle','quel','combien','pourquoi','comment','faut','faudrait',
  'peut','peux','puis','dois','doit','devrait','veux','veut','voulais',
  'fais','fait','faire','mettre','met','mets','mis','prendre','pris','donner',
  'passer','arriver','arrive',
]);

// ── ANCRES DE DOMAINE ───────────────────────────────────────────────
// Noms de SUJET sans ambiguïté : quand l'utilisateur en écrit un, il dit de quoi
// il parle. Le chunk servi DOIT alors en parler aussi (restriction ET, pas un
// bonus). C'est l'inverse de l'IDF : depuis que le corpus couvre 359 simanim, ces
// mots sont devenus les PLUS fréquents (tefilin df=1321, chema df=1351), donc les
// plus faibles — le garde-fou keyToken les écartait au profit du mot incident, et
// une question sur les tefilin partait sur un siman de Shabbat.
// L'ancre est satisfaite par le mot LUI-MÊME ou par l'un de ses synonymes indexés
// (le corpus Yoreh De'ah est rédigé en hébreu : « viande » doit pouvoir être
// satisfait par בשר).
// Équivalents HÉBREUX des ancres. Le corpus est rédigé en grande partie en hébreu :
// sans cette table, l'ancre « kohanim » ne désigne que les chunks qui écrivent la
// translittération française et met à ZÉRO les simanim qui écrivent כהנים —
// c'est-à-dire ceux qui traitent réellement le sujet.
// ── FAMILLES D'ANCRES TRILINGUES ────────────────────────────────────────────
// Une ancre est un nom de SUJET sans ambiguïté : quand l'utilisateur l'écrit, il
// dit de quoi il parle, et le chunk servi DOIT en parler (restriction ET). C'est
// le seul garde-fou qui ne dépend pas de la fréquence, donc le seul qui ne se
// dégrade pas quand le corpus grandit.
//
// ⚠️ CHAQUE FAMILLE REGROUPE LES TROIS LANGUES. Une première version ne listait
// que le français : un visiteur écrivant « תפילין » n'activait aucune ancre, la
// recherche retombait sur le mot le plus rare, et « האם מותר לישון עם תפילין ? »
// était servie par le siman 266 (« le voyageur en chemin ») au lieu du 44 —
// une source fausse sur une réponse halakhique. chat-he.html et chat-en.html
// postent sur le même /api/chat : la parité trilingue est une règle du dépôt.
//
// `daily: true` marque les sujets qui appartiennent à la journée du juif
// (Orah Haïm 1-185). Ils servent de PREUVE POSITIVE qu'une question ne porte pas
// sur Shabbat, et déclenchent alors le déclassement des simanim 242-365.
const ANCHOR_FAMILIES = [
  // ── Orah Haïm quotidien ──
  { daily: true,  forms: ['tefilin', 'תפילין', 'תפלין', 'phylacteres', 'phylacteries'] },
  { daily: true,  forms: ['tsitsit', 'ציצית', 'fringes'] },
  { daily: true,  forms: ['talit', 'טלית'] },
  { daily: true,  forms: ['chema', 'שמע'] },
  { daily: true,  forms: ['tefila', 'תפלה', 'תפילה', 'prayer'] },
  { daily: true,  forms: ['amida', 'עמידה', 'שמונה'] },
  { daily: true,  forms: ['berakha', 'ברכה', 'ברכות', 'blessing', 'blessings'] },
  { daily: true,  forms: ['birkat', 'ברכת'] },
  { daily: true,  forms: ['netilat', 'netila', 'נטילת', 'נטילה'] },
  { daily: true,  forms: ['yadayim', 'ידים', 'ידיים'] },
  { daily: true,  forms: ['minha', 'מנחה'] },
  { daily: true,  forms: ['chaharit', 'שחרית'] },
  { daily: true,  forms: ['maariv', 'ערבית', 'מעריב'] },
  { daily: true,  forms: ['moussaf', 'מוסף'] },
  { daily: true,  forms: ['kaddich', 'קדיש'] },
  { daily: true,  forms: ['kedoucha', 'קדושה'] },
  { daily: true,  forms: ['tahanoun', 'תחנון'] },
  { daily: true,  forms: ['minyan', 'מנין', 'מניין'] },
  { daily: true,  forms: ['kohanim', 'כהנים', 'כפים', 'doukhan'] },
  { daily: true,  forms: ['synagogue', 'כנסת'] },
  { daily: true,  forms: ['sefer', 'ספר'] },
  { daily: true,  forms: ['torah', 'תורה'] },
  { daily: true,  forms: ['mezouza', 'מזוזה', 'mezuzah'] },
  { daily: true,  forms: ['hamotsi', 'המוציא'] },
  { daily: true,  forms: ['mazon', 'מזון'] },
  { daily: true,  forms: ['zimoun', 'זימון'] },
  { daily: true,  forms: ['tsedaka', 'צדקה'] },
  // ── Hilkhot Shabbat ── (jamais `daily`)
  { daily: false, forms: ['borer', 'בורר'] },
  { daily: false, forms: ['bishoul', 'בישול'] },
  { daily: false, forms: ['mouktse', 'מוקצה'] },
  { daily: false, forms: ['hazara', 'חזרה'] },
  { daily: false, forms: ['tohen', 'טוחן'] },
  { daily: false, forms: ['hatmana', 'הטמנה'] },
  { daily: false, forms: ['kiddoush', 'קידוש'] },
  { daily: false, forms: ['havdala', 'הבדלה'] },
  { daily: false, forms: ['bougies', 'nerot', 'נרות', 'הדלקה', 'candles', 'candle'] },
  { daily: false, forms: ['erouv', 'עירוב'] },
  { daily: false, forms: ['plata', 'פלטה'] },
  { daily: false, forms: ['kira', 'כירה'] },
  // ── Yoreh De'ah — cacheroute ──
  { daily: false, forms: ['viande', 'בשר', 'meat'] },
  { daily: false, forms: ['lait', 'חלב', 'milk', 'dairy'] },
  { daily: false, forms: ['fromage', 'גבינה', 'cheese'] },
  { daily: false, forms: ['casher', 'cacheroute', 'כשר', 'kosher'] },
  { daily: false, forms: ['taarovet', 'תערובת'] },
  // ── Yoreh De'ah — nidah ──
  { daily: false, forms: ['nidda', 'נדה', 'נידה'] },
  { daily: false, forms: ['mikve', 'מקוה', 'מקווה'] },
  { daily: false, forms: ['tevila', 'טבילה'] },
  { daily: false, forms: ['וסת', 'וסתות'] },
  { daily: false, forms: ['כתם', 'כתמים'] },
  { daily: false, forms: ['הרחקות'] },
  { daily: false, forms: ['נקיים'] },
];

// ── Graphies concurrentes de la translittération française ──────────────────
// Le français n'a pas de translittération unique de l'hébreu : « tefilin » et
// « tefillin » désignent le MÊME objet. Le corpus n'emploie qu'une graphie ; la
// variante n'y survit que dans de rares mentions INCIDENTES, à qui BM25 attribue
// donc une IDF énorme (mesuré sur le corpus réel : tefilin df=1295, tefillin
// df=12 — soit idf 2,5 contre 7,2). La variante devenait donc le « portail »
// keyToken et dirigeait la question vers le siman qui la mentionne au passage,
// jamais vers celui qui l'enseigne. Le filtre `known` ne protège que des mots
// ABSENTS (df=0) ; le trou est la bande « df petit mais non nul », qui est
// exactement celle des mentions incidentes.
// On fusionne les graphies DANS normalizeToken, donc avant l'indexation ET avant
// la requête (même fonction pour les deux) : l'asymétrie d'IDF disparaît à la
// racine, ce qu'un synonyme ne saurait faire (un synonyme ne corrige pas l'IDF).
const SPELLING_CANON = new Map(Object.entries({
  // tefilin
  tefillin: 'tefilin', teffilin: 'tefilin', tephilin: 'tefilin', tephillin: 'tefilin',
  tefiline: 'tefilin', tefilines: 'tefilin', tephilines: 'tefilin', tfilin: 'tefilin',
  tefilim: 'tefilin', tefillim: 'tefilin', tefillines: 'tefilin', tefilins: 'tefilin',
  // tsitsit
  tzitzit: 'tsitsit', tzitzis: 'tsitsit', tsitsis: 'tsitsit', zizith: 'tsitsit',
  tsitsite: 'tsitsit', tsitsits: 'tsitsit', tzitzith: 'tsitsit', sitsit: 'tsitsit',
  tsitsith: 'tsitsit',
  // talit
  tallit: 'talit', talith: 'talit', tallith: 'talit', taleth: 'talit', talits: 'talit',
  tallits: 'talit', talleth: 'talit',
  // chema
  // 'schema' VOLONTAIREMENT absent : « schéma » est un mot français (et anglais)
  // courant de tout autre sens, et 'chema' est une ANCRE — la fusion ne bruitait
  // pas seulement le score, elle RESTREIGNAIT la recherche au Chema.
  shema: 'chema', shma: 'chema', sema: 'chema', chma: 'chema',
  // berakha (le mot français aussi : le corpus dit « berakha »)
  brakha: 'berakha', beracha: 'berakha', bracha: 'berakha', berakhah: 'berakha',
  berachot: 'berakha', brachot: 'berakha', brakhot: 'berakha', berakhot: 'berakha',
  berakhote: 'berakha', bendiction: 'berakha',
  // tefila
  tefilla: 'tefila', tefillah: 'tefila', tefilah: 'tefila', tfila: 'tefila',
  tefillot: 'tefila', tefilot: 'tefila', tefillas: 'tefila',
  // offices
  mincha: 'minha', minhah: 'minha', minah: 'minha', mincah: 'minha',
  shaharit: 'chaharit', shacharit: 'chaharit', chacharit: 'chaharit',
  arvit: 'maariv', arvith: 'maariv', maarive: 'maariv', arbit: 'maariv',
  // kidouch
  kidoush: 'kiddoush', kiddush: 'kiddoush', kidouch: 'kiddoush', kiddouch: 'kiddoush',
  kiddousch: 'kiddoush',
  // nidah / taharat ha-mishpaha
  nidah: 'nidda', nida: 'nidda', niddah: 'nidda', niddha: 'nidda',
  mikve: 'mikve', mikveh: 'mikve', mikva: 'mikve', mikvah: 'mikve', mikwe: 'mikve',
}));

// Une clé de SPELLING_CANON qui est AUSSI une clé de SYNONYMS ou de NON_TOPICAL
// NON_TOPICAL rend cette entrée INATTEIGNABLE : normalizeToken réécrit le token
// avant toute consultation de ces tables. L'erreur est silencieuse et se
// reproduira à chaque graphie ajoutée — on la signale donc au chargement.
for (const [variant, canon] of SPELLING_CANON) {
  if (variant === canon) continue;
  for (const [nom, table] of [['SYNONYMS', SYNONYMS], ['NON_TOPICAL', NON_TOPICAL]]) {
    const present = table instanceof Set
      ? table.has(variant)
      : Object.prototype.hasOwnProperty.call(table, variant);
    if (present) console.warn(`[corpus-search] entrée inatteignable : '${variant}' est dans ${nom} mais SPELLING_CANON le réécrit en '${canon}'`);
  }
}

// Index token → famille d'ancre. Construit paresseusement car il dépend de
// normalizeToken, définie juste en dessous.
// L'hébreu colle ses préfixes au mot : « הפלטה » est UN token, distinct de
// « פלטה ». Sans dépréfixation, une question hébraïque n'active aucune ancre et
// la recherche retombe sur le mot le plus rare de la phrase — mesuré :
// « האם מותר להחזיר סיר על הפלטה בשבת ? » partait sur le siman 318 (bishoul)
// au lieu du 253 (hazara), le portail étant « סיר » (présent dans UN chunk).
const HE_PREFIXES = ['ה', 'ב', 'ל', 'מ', 'ו', 'כ', 'ש', 'שה', 'וה', 'כש', 'לכ', 'מה', 'ובה'];
function heVariants(t) {
  if (!/^[\u05d0-\u05ea]/.test(t)) return [t];
  const out = [t];
  for (const p of HE_PREFIXES) {
    if (t.length > p.length + 1 && t.startsWith(p)) out.push(t.slice(p.length));
  }
  return out;
}

let _anchorIndex = null;
function anchorIndex() {
  if (_anchorIndex) return _anchorIndex;
  _anchorIndex = new Map();
  ANCHOR_FAMILIES.forEach((fam, i) => {
    for (const w of fam.forms) {
      const n = normalizeToken(w);
      if (n.length >= 2) _anchorIndex.set(n, i);
    }
  });
  return _anchorIndex;
}

function normalizeToken(s) {
  const t = s.toLowerCase().normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')      // diacritiques latins
    .replace(/[\u0591-\u05C7]/g, '')      // NIKUD + te'amim hébreux : « בַּמֶּה » ≡ « במה »
    .replace(/['’‘\u05F3\u05F4"״]/g, '')  // apostrophes, geresh, gershayim
    .replace(/[^a-z\u05d0-\u05ea\u05f0-\u05f20-9]/g, '');
  return SPELLING_CANON.get(t) || t;
}

// Pré-normalise la chaîne ENTIÈRE (minuscules, sans accents) puis remplace les
// expressions multi-mots, avant tout découpage en tokens.
function preNormalize(text) {
  let t = String(text || '').toLowerCase().normalize('NFC');
  // « thé » AVANT le retrait des accents : sans cela il devient « the », avalé par
  // le stopword ANGLAIS — une question sur le thé perdait son seul mot porteur.
  t = t.replace(/(^|[^\p{L}])th[éè]s?(?![\p{L}])/gu, '$1 theboisson ');
  t = t.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  // Variante sans accent, seulement après un déterminant français (« un the »),
  // pour ne jamais toucher au « the » anglais des questions EN.
  t = t.replace(/(^|[^\p{L}])(un|une|le|du|de|mon|ma|ce|cette|votre|son|au|mets|verse)\s+thes?(?![\p{L}])/gu, '$1$2 theboisson ');
  // Élisions FRANÇAISES uniquement (l', d', qu', j'…) : on les efface pour ne pas
  // coller le déterminant au mot. Les AUTRES apostrophes sont des
  // translittérations de l'hébreu (Min'ha, Bera'ha, Ta'hanoun, Hala'ha) : le
  // séparateur les coupait en deux — « min » + « ha », deux débris sans rapport
  // avec le sujet (mesuré : min df=233, ha df=566 dans le corpus). L'apostrophe a
  // donc été retirée du séparateur de tokenize(), et normalizeToken la supprime.
  t = t.replace(/(^|[^\p{L}])(?:[ldjnmtsc]|qu|jusqu|lorsqu|puisqu|quelqu|aujourd)['’‘]/gu, '$1 ');
  // Possessif ANGLAIS (« Shabbat's », « the Rambam's ») : l'apostrophe est en FIN
  // de mot, la règle d'élision française ne la voit pas. Sans cela « Shabbat's »
  // donnait le token `shabbats` (df=0) : le mot de sujet était détruit. La
  // lookahead protège les translittérations hébraïques (Ro'sh, Bera'ha).
  t = t.replace(/(\p{L})['’‘]s(?![\p{L}])/gu, '$1 ');
  for (const [re, rep] of MULTIWORD) t = t.replace(re, rep);
  return t;
}

export function tokenize(text) {
  return preNormalize(text)
    .split(/[\s,.;:!?()«»""\-—–_/]+/)
    .map(normalizeToken)
    .filter((t) => t.length >= 2 && !STOPWORDS.has(t));
}

// Termes de CONCEPT déduits des règles de co-occurrence. Ils servent aussi de
// clés d'accès au garde-fou keyToken : si l'on a reconnu que la question porte
// sur le borer, les chunks qui parlent de borer doivent pouvoir passer, même
// s'ils ne nomment jamais « pomme de terre ».
function conceptTerms(tokens) {
  const set = new Set(tokens);
  const out = new Set();
  CONCEPT_RULES.forEach((rule) => {
    if (rule.any.some((w) => set.has(w)) && rule.ctx.some((w) => set.has(w))) {
      rule.add.forEach((t) => { const n = normalizeToken(t); if (n.length >= 2) out.add(n); });
    }
  });
  return out;
}

function expandQuery(tokens) {
  const expanded = new Map();
  tokens.forEach((t) => {
    expanded.set(t, (expanded.get(t) || 0) + 1.0);
    if (SYNONYMS[t]) {
      SYNONYMS[t].forEach((syn) => {
        const n = normalizeToken(syn);
        if (n.length >= 2) expanded.set(n, Math.max(expanded.get(n) || 0, 0.6));
      });
    }
  });
  // Co-occurrence : n'ajoute les termes de concept que si les DEUX familles de
  // mots sont présentes — évite d'injecter « borer » dès qu'on lit « prendre ».
  const set = new Set(tokens);
  CONCEPT_RULES.forEach((rule) => {
    if (rule.any.some((w) => set.has(w)) && rule.ctx.some((w) => set.has(w))) {
      rule.add.forEach((term) => {
        const n = normalizeToken(term);
        if (n.length >= 2) expanded.set(n, Math.max(expanded.get(n) || 0, rule.w));
      });
    }
  });
  return expanded;
}

function loadAndIndex() {
  if (_corpus) return;
  let _srcSig = null;
  try {
    const raw = readFileSync(CORPUS_PATH, 'utf-8');
    // Empreinte du corpus TEL QU'IL EST SUR LE DISQUE — 54 ms mesurées sur
    // 45 Mo. C'est ce qui autorise à faire confiance à l'index précalculé.
    _srcSig = createHash('sha1').update(raw).digest('hex');
    _corpus = JSON.parse(raw);
  } catch (err) {
    console.error('[corpus-search] Failed to load corpus-shabbat.json:', err.message);
    _corpus = { meta: {}, chunks: [] };
    _idf = new Map();
    _avgdl = 1;
    _N = 0;
    return;
  }
  _N = _corpus.chunks.length;

  // ── Tokenisation PRÉCALCULÉE ────────────────────────────────────────────
  // La tokenisation représente 94 % du démarrage à froid, et elle est refaite
  // à chaque réveil de la lambda. Mesuré : 2,0 s à 20 741 chunks, 2,7 s à
  // 28 333 — et le corpus a grandi de 37 % en huit jours. Ce temps est payé
  // par l'utilisateur GRATUIT, sur sa question. Or les journaux de production
  // montrent ~13 appels à /api/chat par jour : la fonction est presque
  // toujours froide, donc PRESQUE CHAQUE visiteur le paie.
  // Le build produit donc data/corpus-index.br (mêmes chunks, même ordre) et
  // on ne s'en sert QUE si son empreinte est celle du corpus effectivement lu.
  // Une empreinte portant seulement sur les identifiants de chunks ne suffit
  // PAS : le 2026-08-27, la correction du siman 320 (ש״כ) a changé le texte de
  // plusieurs chunks sans changer ni leur nombre (28 333) ni leurs
  // identifiants. Un index périmé aurait donc passé un tel contrôle et servi
  // des tokens faux — donc de mauvaises réponses halakhiques, sans alarme.
  // Le repli sur la tokenisation à chaud est conservé : si le fichier manque
  // ou ne concorde pas, rien ne casse.
  let pre = null;
  try {
    const parsed = JSON.parse(brotliDecompressSync(readFileSync(INDEX_PATH)).toString('utf-8'));
    const tokSig = tokenizerSignature();
    if (parsed && Array.isArray(parsed.tokens) && parsed.tokens.length === _N
        && parsed.src === _srcSig && parsed.tok === tokSig) pre = parsed.tokens;
    else console.warn(`[corpus-search] corpus-index.br ignoré (longueur ${parsed?.tokens?.length} vs ${_N}, corpus ${parsed?.src === _srcSig}, tokeniseur ${parsed?.tok === tokSig}) — tokenisation à chaud`);
  } catch { /* absent : tokenisation à chaud */ }

  // Le chemin rapide est PROTÉGÉ. Une seule entrée mal formée dans l'index (un
  // nombre au lieu d'une chaîne) ferait lever .split hors du try de lecture, et
  // comme _corpus est déjà posé, le `if (_corpus) return` du haut renverrait
  // ensuite un module à moitié construit : la lambda servirait des erreurs
  // jusqu'à sa mort, pour TOUTES les questions. On retombe donc sur la
  // tokenisation à chaud plutôt que d'empoisonner le processus.
  const buildIndex = (src) => {
    const df = new Map();
    let totalLen = 0;
    for (let i = 0; i < _corpus.chunks.length; i++) {
      const c = _corpus.chunks[i];
      const tokens = src
        ? (src[i] ? src[i].split(' ') : [])
        : tokenize(
          c.text + ' ' + (c.subsection || '') + ' ' + c.sectionTitle + ' ' +
          (c.simanTitle || '') + ' ' + (c.simanTitleHe || '')
        );
      c._tokens = tokens;
      c._tokenCount = tokens.length;
      c._tfMap = new Map();
      for (const t of tokens) c._tfMap.set(t, (c._tfMap.get(t) || 0) + 1);
      totalLen += tokens.length;
      new Set(tokens).forEach((t) => df.set(t, (df.get(t) || 0) + 1));
    }
    return { df, totalLen };
  };

  let built;
  try {
    built = buildIndex(pre);
  } catch (err) {
    console.error(`[corpus-search] index précalculé illisible (${err.message}) — tokenisation à chaud`);
    pre = null;
    built = buildIndex(null);
  }

  _idf = new Map();
  _df = built.df;
  built.df.forEach((freq, term) => _idf.set(term, Math.log(1 + (_N - freq + 0.5) / (freq + 0.5))));
  _avgdl = built.totalLen / Math.max(1, _N);
  console.log(`[corpus-search] Indexed ${_N} chunks from ${(_corpus.meta?.totalSimanim) || '?'} simanim${pre ? ' (index précalculé)' : ' (tokenisation à chaud)'}`);
}

function getIdf(term) {
  if (_idf.has(term)) return _idf.get(term);
  return Math.log(1 + (_N + 0.5) / 0.5);
}

function scoreChunk(chunk, queryTerms, keyTokens, originalTokens, strict, conceptKeys = [], anchorTerms = []) {
  const k1 = 1.5, b = 0.75;
  const tf = chunk._tfMap;
  // ⛓️ ANCRE DE DOMAINE (restriction ET). Si la question NOMME son sujet, le
  // chunk doit en parler. C'est le seul garde-fou qui résiste à la croissance du
  // corpus : il ne dépend pas de l'IDF, donc il ne se dégrade pas quand un mot
  // de sujet devient fréquent. Sans lui, « à quelle heure mettre les tefilin ? »
  // était servie par un siman de Shabbat qui mentionne les tefilin en passant.
  if (anchorTerms.length && !anchorTerms.some((t) => tf.get(t))) return 0;
  // Garde-fou keyToken : au moins un token original à haute IDF doit matcher —
  // OU un terme de concept reconnu par les règles de co-occurrence. Sans cette
  // seconde porte, une question dont le mot le plus rare est un ALIMENT (« pomme
  // de terre ») n'atteint jamais les chunks de la mélakha concernée (borer).
  if (keyTokens.length
      && !keyTokens.some((t) => tf.get(t))
      && !conceptKeys.some((t) => tf.get(t))) return 0;
  // Mode strict (prod) : au moins 2 tokens distincts doivent matcher (les termes
  // de concept comptent, sinon le strict annule le bénéfice des règles).
  if (strict) {
    // Exigence PROPORTIONNELLE à la longueur de la question. Exiger 2 tokens
    // correspondants sur une question de 2 mots utiles (« le feu », « médicament
    // tête ») élimine presque tout : en production cela rendait 6 questions sur
    // 32 totalement vides. On exige 2 matchs seulement à partir de 4 tokens.
    const need = originalTokens.length >= 4 ? 2 : 1;
    let matched = 0;
    for (const t of originalTokens) { if (tf.get(t)) matched++; if (matched >= need) break; }
    if (matched < need) for (const t of conceptKeys) { if (tf.get(t)) matched++; if (matched >= need) break; }
    if (matched < need) return 0;
  }

  const dl = chunk._tokenCount;
  let score = 0;
  queryTerms.forEach((boost, term) => {
    const f = tf.get(term);
    if (!f) return;
    const idf = getIdf(term);
    const num = f * (k1 + 1);
    const den = f + k1 * (1 - b + b * dl / _avgdl);
    score += boost * idf * (num / den);
  });
  // Bonus titre de section / subsection
  const titleStr = chunk.sectionTitle + ' ' + (chunk.subsection || '');
  const titleSet = new Set(tokenize(titleStr));
  let titleBonus = 0;
  queryTerms.forEach((boost, term) => {
    if (titleSet.has(term)) titleBonus += boost * getIdf(term) * 0.8;
  });
  // Boost de type
  if (chunk.type === 'cas-pratique') score *= 1.15;
  if (chunk.type === 'definition') score *= 1.1;
  return score + titleBonus;
}

// Mots de MOMENT qui situent la question dans la journée sans être un sujet à
// part entière. Ils complètent les familles marquées `daily`.
const DAILY_EXTRA = new Set(['matin', 'reveil', 'lever', 'prier', 'priere', 'benediction', 'benedictions']);

// Réglages du portail, pilotables par variable d'environnement pour pouvoir les
// ajuster sans redéploiement (le corpus grandit toutes les semaines).
const ANCHOR_MODE = process.env.CORPUS_ANCHOR_MODE || 'and';
// Un mot doit apparaître dans au moins GATE_MIN_DF chunks pour pouvoir servir de
// portail. Réglable sans redéploiement.
const GATE_MIN_DF = parseInt(process.env.GATE_MIN_DF || '3', 10);
// Facteur appliqué au score d'un siman de Hilkhot Shabbat quand la question ne
// porte aucun marqueur de Shabbat. 1 = garde-fou désactivé, 0 = exclusion pure.
const SHABBAT_PENALTY = parseFloat(process.env.CORPUS_SHABBAT_PENALTY || '0.35');

// Mots qui situent une question à Shabbat. Volontairement LARGE (mieux vaut
// laisser passer une question du quotidien vers Shabbat que l'inverse).
const SHABBAT_MARKERS = new Set([
  'shabbat','chabbat','chabat','shabat','sabbat','shabbos','chabbath','chabbatot',
  'vendredi','samedi','motsae','motsaei','motsash','melakha','melakhot','melacha',
  'mouktse','muktse','mouqtse','borer','bishoul','hatmana','hazara','tohen','lash',
  'plata','blech','kira','rechaud','eirouv','erouv','havdala','avdala','kiddoush',
  'nerot','hadlaka','bougies','bougie','tsomet','yomtov','fete','fetes','pessah',
  'kippour','soucca','chalom',
  // graphies latines concurrentes : sans elles, « trier les couverts a Shabbath »
  // tombait sur le siman 45 au lieu du 319.
  'shabbath','shabbes','chabbes','shabath','chabos','shabbatot','chabbatoth',
  'shabes','sabbath',
]);

// Graphies HÉBRAÏQUES. Un Set de tokens ne peut pas suffire : le tokeniseur garde
// les préfixes attachés (ב/ל/מ/ה/ו/כ/ש), « בשבת » est UN token. On teste donc le
// RADICAL sur la chaîne. chat-he.html poste sur le même /api/chat : sans cela,
// toute question de Shabbat posée en hébreu était traitée comme hors-Shabbat.
const SHABBAT_MARKERS_HE =
  /[בלמהוכש]{0,2}(?:שבת|מלאכ|מוקצ|בורר|בישול|הטמנ|הבדל|קידוש|עירוב|פלטה|מוצאי)/;

// ── Nettoyage du bloc de profil injecté par les interfaces ──────────────────
// Le widget ET les trois pages de chat plein écran préfixent la 1re question
// d'une conversation par un bloc de profil (niveau, minhag, langue). Ces mots
// (« débutant », « souhaitée », « profil ») sont des hapax du corpus : ils ont
// l'IDF MAXIMALE et confisquaient les deux keyTokens du portail, rendant la
// recherche aveugle à la vraie question. Le nettoyage est fait ici, côté SERVEUR,
// pour couvrir aussi les widgets déjà en cache chez les visiteurs — le texte
// COMPLET continue d'être envoyé au modèle, qui a besoin du profil.
// Quatre formats existent (widget avec « [Ma question] », chat.html sans
// marqueur, chat-he.html, chat-en.html) : ils sont tous traités.
const PROFILE_HEADER_RE = /^\s*(?:\[Profil de cette session\]|\[Session profile\]|\[\u05e4\u05e8\u05d5\u05e4\u05d9\u05dc \u05e1\u05e9\u05df \u05d6\u05d4\]|Bonjour Daat\s*!\s*Voici mon profil)/i;

export function stripProfileBlock(text) {
  const s = String(text || '');
  // Variante widget : marqueur explicite de la question.
  const m = s.match(/\[(?:Ma question|My question)\]\s*([\s\S]*)$/i);
  if (m) return m[1].trim();
  if (!PROFILE_HEADER_RE.test(s)) return s;
  const lines = s.split('\n');
  let i = PROFILE_HEADER_RE.test(lines[0]) ? 1 : 0;
  // Puces du profil (« • Niveau : … », « - \u05e8\u05de\u05d4: … ») et lignes vides. Borné à
  // 6 lignes : au-delà, c'est la question de l'utilisateur, on n'y touche pas.
  // La ligne VIDE qui suit les puces CLÔT le bloc : tout ce qui vient après est la
  // question, même si elle commence elle aussi par un tiret (sinon « - Puis-je
  // trier les couverts ? » était avalé et la recherche partait à vide).
  let eaten = 0;
  while (i < lines.length && eaten < 6) {
    if (/^\s*$/.test(lines[i])) {
      if (eaten > 0) break;
      i++; continue;
    }
    if (!/^\s*[\u2022\-\u2013*]\s/.test(lines[i])) break;
    eaten++; i++;
  }
  const rest = lines.slice(i).join('\n').trim();
  // Message d'introduction (bouton « Commencer l'étude ») : aucune question réelle
  // → requête vide, la recherche ne renverra rien plutôt qu'un extrait au hasard.
  // On matche la PHRASE COMPLÈTE émise par buildIntroMessage, jamais son préfixe :
  // « Je suis prêt à allumer les bougies, à quelle heure ? » est une VRAIE question.
  // Relevés dans les producteurs eux-mêmes : chat-widget.js et chat.html disent
  // « Je suis prêt à commencer. », chat-en.html « I am ready to begin. » et
  // chat-he.html « הנני מוכן להתחיל. » — et non « אני מוכן ». On matche la phrase
  // entière, pas un préfixe : « Je suis prêt à allumer les bougies, à quelle
  // heure ? » est une VRAIE question. NB : \b ne fonctionne pas sur l'hébreu en
  // JS (les lettres ne sont pas des \w) — d'où l'absence de borne sur la 3e.
  const INTRO_SENTINELS = [
    /^je suis pr[\u00ea\u00e9]te? [\u00e0a] commencer/i,
    /^i(?:['\u2019]?m| am) ready to begin/i,
    /^(?:\u05d0\u05e0\u05d9|\u05d4\u05e0\u05e0\u05d9)\s+\u05de\u05d5\u05db\u05e0?[\u05d4\u05df]?\s+\u05dc\u05d4\u05ea\u05d7\u05d9\u05dc/,
  ];
  if (INTRO_SENTINELS.some((re) => re.test(rest))) return '';
  return rest;
}

// Le bloc de profil est retiré de la RECHERCHE (il l'empoisonnait) mais il reste
// dans le PROMPT envoyé au reformulateur. Il doit donc rester dans la CLÉ de
// cache, sinon deux prompts différents (anglais/ashkénaze vs français/séfarade)
// partagent une entrée pendant 30 jours. On n'y remet pas le bloc brut — qui
// empêchait tout partage — mais seulement ses trois champs.
export function profileSignature(text) {
  const s = String(text || '');
  const grab = (re) => (s.match(re)?.[1] || '').toLowerCase().trim().replace(/\s+/g, '-');
  const niveau = grab(/(?:Niveau(?:\s+d'\u00e9tude)?|(?:Study )?Level|\u05e8\u05de\u05ea \u05dc\u05d9\u05de\u05d5\u05d3|\u05e8\u05de\u05d4)\s*:\s*(.+)/i);
  const minhag = grab(/(?:Minhag|\u05de\u05e0\u05d4\u05d2)\s*:\s*(.+)/i);
  const langue = grab(/(?:Langue de r\u00e9ponse souhait\u00e9e|Desired response language|\u05e9\u05e4\u05ea \u05d4\u05de\u05e2\u05e0\u05d4 \u05d4\u05de\u05d1\u05d5\u05e7\u05e9\u05ea)\s*:\s*(.+)/i);
  return (niveau || minhag || langue) ? `${niveau}|${minhag}|${langue}` : '';
}

export function searchCorpus(question, opts = {}) {
  loadAndIndex();
  const limit = opts.limit || 3;
  const minScore = opts.minScore ?? 1.5;
  const strict = opts.strict === true;
  // Filtre de section optionnel ('orach-chaim' | 'yoreh-deah'). Absent → tout le
  // corpus (rétro-compatible). Les anciens chunks sans champ `section` ne sont
  // jamais exclus, pour éviter toute régression silencieuse.
  const section = opts.section || null;
  const tokens = tokenize(stripProfileBlock(question));
  if (tokens.length === 0) return { results: [], keyTokens: [], totalChunks: _N };

  // Key tokens = les 2 tokens originaux de plus haute IDF, choisis UNIQUEMENT
  // parmi ceux qui EXISTENT dans le corpus. getIdf() attribue l'IDF maximale à
  // tout mot inconnu : une faute de frappe, une marque ou une expression absente
  // devenait donc le « portail » du garde-fou keyToken et mettait TOUS les chunks
  // à zéro — la recherche ne renvoyait alors plus rien (ex. « râper des carottes »).
  const known = tokens.filter((t) => _idf.has(t));
  // Repli : si le plancher ne laisse rien, on reprend les tokens connus — mieux
  // vaut un portail imparfait qu'une abstention systématique sur les questions
  // dont tout le vocabulaire est rare.

  // Le « portail » ne peut être ouvert que par un mot de SUJET : on écarte les
  // mots de provenance (minhag, nom de posek) et de rapport (« il disait que »).
  // Plancher de FRÉQUENCE DOCUMENTAIRE. Un mot présent dans un ou deux chunks sur
  // 20 000 n'est pas un sujet, c'est un accident de rédaction — et l'IDF en fait
  // pourtant le mot le plus « discriminant », donc le portail. C'est la fragilité
  // récurrente de ce moteur : à chaque enrichissement du corpus, un mot passe de
  // df=0 (ignoré) à df=1 (portail exclusif) et détourne une question entière.
  const gateCandidates = known.filter((t) => !NON_TOPICAL.has(t) && _df.get(t) >= GATE_MIN_DF);
  const gatePool = gateCandidates.length ? gateCandidates : known.filter((t) => !NON_TOPICAL.has(t));
  const byIdf = [...new Set(gatePool)].map((t) => ({ t, idf: getIdf(t) })).sort((a, b) => b.idf - a.idf);
  // Ancres présentes dans la question, avec leur famille de synonymes indexés
  // (le corpus Yoreh De'ah est rédigé en hébreu : « tevila » doit être satisfait
  // par טבילה, sans quoi l'ancre ne désigne que les 32 chunks translittérés).
  // Une forme écrite dans N'IMPORTE QUELLE des trois langues active la famille
  // ENTIÈRE : le chunk peut donc satisfaire l'ancre en hébreu même si la question
  // est en français, et réciproquement.
  const anchorTerms = [];
  const activeFamilies = new Set();
  if (ANCHOR_MODE !== 'off') {
    const idx = anchorIndex();
    for (const t of new Set(gateCandidates)) {
      for (const v of heVariants(t)) {
        const fi = idx.get(v);
        if (fi !== undefined) { activeFamilies.add(fi); break; }
      }
    }
    for (const fi of activeFamilies) {
      for (const w of ANCHOR_FAMILIES[fi].forms) {
        const n = normalizeToken(w);
        if (n.length >= 2 && _idf.has(n)) anchorTerms.push(n);
        for (const syn of SYNONYMS[n] || []) {
          const sn = normalizeToken(syn);
          if (sn.length >= 2 && _idf.has(sn)) anchorTerms.push(sn);
        }
      }
    }
  }

  // QUAND L'UTILISATEUR NOMME SON SUJET, C'EST LE SUJET QUI EST LE PORTAIL.
  // Sélectionner le portail sur la seule IDF donne le mot le plus RARE, qui est
  // presque toujours un mot de décor (« au ras du coin », « vernis », « un rêve
  // horrible ») : sur « un des fils de mes tsitsit s'est coupé au ras du coin »,
  // le portail devenait `ras` (df=3) et il fallait un chunk contenant à la fois
  // « ras » et « tsitsit » — il n'en existe aucun, la recherche rendait le vide.
  // Une ancre n'est jamais un mot de décor : elle passe donc devant l'IDF.
  const keyTokens = anchorTerms.length
    ? [...new Set(anchorTerms)]
    : byIdf.slice(0, 2).map((x) => x.t);

  // Synonymes de SECOURS : un synonyme ne pouvait JAMAIS ouvrir le portail (seuls
  // les tokens écrits par l'utilisateur et présents dans l'index le pouvaient),
  // si bien qu'ajouter des synonymes ne rattrapait PAS un mot absent du corpus —
  // or c'est précisément à cela qu'ils servent (les pages de nidah sont en
  // hébreu : וסת / כתם / הרחקות). On n'élargit le portail que pour un mot
  // que l'index NE CONNAÎT PAS : le garde-fou reste strictement intact dès que le
  // vocabulaire de la question est déjà couvert.
  const rescueKeys = [];
  for (const t of new Set(tokens)) {
    if (_idf.has(t) || !SYNONYMS[t]) continue;
    for (const syn of SYNONYMS[t]) {
      const n = normalizeToken(syn);
      if (n.length >= 2 && _idf.has(n) && !NON_TOPICAL.has(n)) rescueKeys.push(n);
    }
  }
  const conceptKeys = [...conceptTerms(tokens), ...rescueKeys];


  // 🛡️ SÉCURITÉ : aucun mot de sujet exploitable ET aucun concept halakhique
  // reconnu → la question n'a rien d'identifiable dans le corpus. Ne RIEN
  // renvoyer (le chat bascule alors sur le chemin complet) est infiniment plus
  // sûr que renvoyer un extrait au hasard : c'est exactement ce qui a produit
  // une réponse sur la kablanout pour une question sur le poisson sur la plata.
  if (keyTokens.length === 0 && conceptKeys.length === 0) {
    return { results: [], keyTokens: [], totalChunks: _N };
  }
  // Idem pour le mode strict : n'exiger que des tokens réellement indexables.
  const originalSet = [...new Set(known.length ? known : tokens)];

  // 🛡️ GARDE-FOU SHABBAT. `section` ne sépare PAS le quotidien de Shabbat : les
  // simanim 1-185 et 242-365 portent TOUS section 'orach-chaim'. Une question sans
  // le moindre marqueur de Shabbat ne peut donc pas être servie par un siman de
  // Hilkhot Shabbat — c'est ainsi que « faut-il se laver les mains le matin ? »
  // recevait le siman 326 (« Se laver à Shabbat ») avec la mention « Source :
  // Siman 326 » : le mécanisme exact du faux heter borer, une réponse assurée sous
  // une référence fausse. L'inverse n'est PAS filtré : « le tsitsit à Shabbat »
  // doit rester servi par le siman 13 comme par le 301.
  const shabbatQ = tokens.some((t) => SHABBAT_MARKERS.has(t))
    || SHABBAT_MARKERS_HE.test(preNormalize(question));
  // ⚠️ La pénalité exige une PREUVE POSITIVE que la question porte sur un AUTRE
  // domaine — pas seulement l'absence du mot « Shabbat ». Une première version
  // pénalisait dès que le mot manquait : elle cassait TOUTES les questions
  // hébraïques (aucun marqueur latin) et déclassait les vraies questions de
  // Shabbat formulées sans le mot (« peut-on trier les couverts ? », relance dans
  // une conversation, page /oh/319) — jusqu'à servir un siman du quotidien sous
  // une source affirmée, c'est-à-dire le mécanisme même du faux heter borer.
  const otherDomainQ = [...activeFamilies].some((fi) => ANCHOR_FAMILIES[fi].daily)
    || tokens.some((t) => DAILY_EXTRA.has(t));

  const expanded = expandQuery(tokens);
  const scored = [];
  for (const c of _corpus.chunks) {
    if (section && c.section && c.section !== section) continue;
    let s = scoreChunk(c, expanded, keyTokens, originalSet, strict, conceptKeys, anchorTerms);
    // PÉNALITÉ, pas exclusion. Une première version excluait purement les simanim
    // de Shabbat : mesuré sur banc indépendant, elle supprimait bien les fuites
    // (14 → 1) mais faisait passer les réponses vides de 7 à 24 sur 75. Or une
    // réponse vide renvoie l'utilisateur gratuit au paywall : on échangeait une
    // mauvaise réponse contre une non-réponse. Le déclassement garde le siman de
    // Shabbat atteignable quand RIEN d'autre ne répond, tout en le faisant perdre
    // systématiquement face à un vrai match du domaine de la question.
    if (s > 0 && !shabbatQ && otherDomainQ && c.section === 'orach-chaim' && +c.siman >= 242 && +c.siman <= 365) {
      s *= SHABBAT_PENALTY;
    }
    if (s >= minScore) scored.push({ chunk: c, score: s });
  }
  scored.sort((a, b) => b.score - a.score);
  return {
    results: scored.slice(0, limit).map((r) => ({
      id: r.chunk.id,
      siman: r.chunk.siman,
      section: r.chunk.section || null,
      level: r.chunk.level || null,
      levelLabel: r.chunk.levelLabel || null,
      simanTitle: r.chunk.simanTitle,
      simanTitleHe: r.chunk.simanTitleHe,
      sectionNum: r.chunk.sectionNum,
      sectionTitle: r.chunk.sectionTitle,
      subsection: r.chunk.subsection,
      type: r.chunk.type,
      // Réserve écrite par le Rav (« hors corpus, à vérifier ») : elle doit
      // parvenir à TOUS les chemins d'affichage, jamais dépendre de l'un d'eux.
      caveat: r.chunk.caveat === true,
      text: r.chunk.text,
      score: r.score,
      sourceUrl: r.chunk.sourceUrl,
    })),
    keyTokens,
    totalChunks: _N,
  };
}

// ── Accès direct (utilisé par les OUTILS daat_search_corpus / daat_get_content) ──
// La recherche BM25 ci-dessus sert au ROUTAGE (décider si Haiku peut répondre
// seul). Les deux helpers ci-dessous servent au mode APPROFONDI, où le modèle
// interroge lui-même le corpus : il lui faut alors récupérer un chunk précis
// par son id, ou tous les chunks d'un siman nommé explicitement.

/**
 * Récupère un chunk par son id (ex. "siman-318-daatharav-12").
 * NB : 10 ids du corpus sont dupliqués (niveau synthèse) — on renvoie le premier.
 */
export function getChunkById(id) {
  loadAndIndex();
  if (!id) return null;
  // Les ids sont désormais préfixés par section et niveau (oh-base-…, yd-halakha-…)
  // et donc globalement uniques : mesuré 1 186 collisions avant, 0 après. On
  // accepte encore les anciens ids nus pour les liens et caches déjà émis, mais
  // on signale l'ambiguïté au lieu de servir silencieusement le premier venu —
  // c'est ainsi que daat_get_content rendait le texte d'un AUTRE siman sous la
  // référence issue de la recherche.
  const exact = _corpus.chunks.filter((c) => c.id === id);
  if (exact.length === 1) return exact[0];
  if (exact.length > 1) {
    console.warn(`[corpus-search] id ambigu « ${id} » : ${exact.length} chunks — le premier est servi`);
    return exact[0];
  }
  const legacy = _corpus.chunks.filter((c) => c.id.endsWith(`-${id}`));
  if (legacy.length === 1) return legacy[0];
  if (legacy.length > 1) {
    console.warn(`[corpus-search] id hérité ambigu « ${id} » : ${legacy.length} chunks dans ${[...new Set(legacy.map((c) => c.section + '/' + c.level))].join(', ')} — non servi`);
    return null;
  }
  return null;
}

/**
 * Tous les chunks d'un siman donné, optionnellement filtrés par section/niveau.
 * Si `question` est fourni, les chunks sont classés par pertinence BM25 ; sinon
 * ils gardent l'ordre du corpus (niveau puis ordre de lecture de la page).
 */
export function getSimanChunks(siman, opts = {}) {
  loadAndIndex();
  const num = parseInt(siman, 10);
  if (!Number.isFinite(num)) return [];
  const section = opts.section || null;
  const level = opts.level || null;
  let chunks = _corpus.chunks.filter((c) => {
    if (c.siman !== num) return false;
    if (section && c.section && c.section !== section) return false;
    if (level && c.level !== level) return false;
    return true;
  });
  const question = String(opts.question || '').trim();
  if (question) {
    const tokens = tokenize(question);
    if (tokens.length) {
      const expanded = expandQuery(tokens);
      // Pas de garde-fou keyToken ni de mode strict : le siman est déjà imposé
      // par l'appelant, le risque de hors-sujet est nul et un filtre supprimerait
      // des seifim pertinents dont le vocabulaire diffère de la question.
      chunks = chunks
        .map((c) => ({ c, s: scoreWithinSiman(c, expanded) }))
        .sort((a, b) => b.s - a.s)
        .map((x) => x.c);
    }
  }
  return chunks;
}

// Pondération par niveau, appliquée UNIQUEMENT à l'intérieur d'un siman imposé.
// À pertinence comparable, on remonte le texte SOURCE (Daat HaRav = Choulhan
// Aroukh HaRav seif par seif ; Base = texte du Mehaber) avant les fiches de
// révision — c'est le texte source qui empêche le modèle de citer de mémoire.
// Pondération EXPLICITE par niveau. Le bonus 1.2 du Daat HaRav se justifie par
// le fait qu'il remonte le texte SOURCE (Choulhan Aroukh HaRav, séif par séif).
// Le niveau 4 du Yoreh De'ah ('halakha') n'est PAS ce texte — l'Admour HaZaken
// n'a pas rédigé de Choulhan Aroukh sur le Yoreh De'ah — il reste donc à 1.0.
// Mesuré : 1.0, 1.1 et 1.2 donnent le même résultat sur les 75 questions du banc ;
// la valeur est donc posée sur la raison, pas sur un réglage. Le repli ?? 1.0
// est conservé mais aucun niveau ne doit s'y appuyer sans intention.
const LEVEL_WEIGHT = { 'daat-harav': 1.2, base: 1.1, halakha: 1.0, lamdan: 1.0, synthese: 0.9 };

// Score SANS normalisation par la longueur. Dans un siman déjà imposé, la
// longueur n'est pas un signal de pertinence mais un artefact du niveau : le
// facteur `b` de BM25 classait systématiquement les seifim du Daat HaRav
// (3 000 caractères et plus) derrière les fiches courtes du niveau Synthèse.
function scoreWithinSiman(chunk, queryTerms) {
  const tf = chunk._tfMap;
  let s = 0;
  queryTerms.forEach((boost, term) => {
    const f = tf.get(term);
    if (f) s += boost * getIdf(term) * (1 + Math.log(f));
  });
  const titleSet = new Set(tokenize(chunk.sectionTitle + ' ' + (chunk.subsection || '')));
  queryTerms.forEach((boost, term) => {
    if (titleSet.has(term)) s += boost * getIdf(term) * 0.8;
  });
  return s * (LEVEL_WEIGHT[chunk.level] ?? 1.0);
}

// ── Cache KV des réponses corpus reformulées ───────────────────────────────
// La même question revient souvent ("c'est quoi le borer ?"). On cache la
// reformulation Haiku : 1re personne → ~0.005 €, toutes les suivantes → 0 €.
// Clé versionnée : bumper CORPUS_CACHE_VERSION invalide tout le cache d'un coup
// (à faire si on change le system prompt de reformulation).
// La clé inclut la section pour ne jamais servir une réponse Shabbat sur une
// conversation Yoreh De'ah (et inversement).
// v2 : la clé ne se limite plus aux 120 premiers caractères de la question.
// Deux questions différentes partageant leur début recevaient la MÊME réponse
// en cache pendant 30 jours — or c'est très souvent la FIN d'une question qui
// porte le détail décisif (« …en tournant » vs « …en tournant sans rien
// casser »). Le préfixe reste dans la clé pour rester lisible en debug, mais
// c'est l'empreinte du texte ENTIER qui identifie la question.
// v3 : le prompt de reformulation cadre désormais le domaine sur le siman servi
// (et non sur la seule section). Les entrées v2 ont été écrites avec l'ancien
// cadrage (« les hilkhot Shabbat » annoncé pour une question de tefila) : les
// resservir 30 jours durant reproduirait exactement le défaut corrigé.
// v4 : le contrat de GÉNÉRATION a changé — le prompt impose désormais la réserve
// du Rav (« hors corpus, à vérifier ») sur les extraits concernés. Les entrées v3
// portent le bon extrait mais pas l'avertissement ; les resservir 30 jours durant
// reproduirait exactement le défaut corrigé. Bumper la version les rend
// inatteignables d'un coup.
export const CORPUS_CACHE_VERSION = 'v4';
export const CORPUS_CACHE_TTL = 30 * 24 * 60 * 60; // 30 jours
// ⚠️ `contract` : empreinte du PROMPT de reformulation. Trois fois de suite, un
// changement de comportement a été masqué par le cache — la réserve « à
// vérifier », puis le cadrage du domaine, puis le refus HORS-SUJET : l'entrée
// portait le bon extrait et un texte produit sous les ANCIENNES règles. Bumper
// CORPUS_CACHE_VERSION à la main marche, mais suppose de ne jamais l'oublier.
// En dérivant la clé du prompt lui-même, toute modification du contrat invalide
// exactement ce qu'elle doit invalider, sans intervention — et deux cadrages
// différents (Shabbat / nidah) ne partagent plus jamais une entrée.
export function corpusCacheKey(text, { section = 'orach-chaim', lang = 'fr', contract = '' } = {}) {
  const norm = String(text || '')
    .toLowerCase()
    .normalize('NFD').replace(/[̀-ͯ]/g, '') // sans accents → meilleur hit rate
    .replace(/[!?.,;:'"«»()\[\]{}]/g, '')
    .replace(/\s+/g, ' ')
    .trim(); // en DERNIER : la ponctuation retirée peut laisser un espace final
  const fingerprint = createHash('sha1').update(norm).digest('hex').slice(0, 16);
  const c = contract ? createHash('sha1').update(String(contract)).digest('hex').slice(0, 8) : 'x';
  return `corpus-cache:${CORPUS_CACHE_VERSION}:${c}:${section}:${lang}:${norm.slice(0, 80)}:${fingerprint}`;
}

// ── PÉRIMÈTRE RÉEL DU CORPUS ────────────────────────────────────────────────
// Calculé depuis le corpus lui-même, jamais écrit en dur. Le prompt système
// annonçait « 241 simanim » et « Hilkhot Shabbat 242-365 + Yoreh De'ah » alors
// que le corpus en contient 359 et couvre aussi tout Orah Haïm 1-185 : le modèle
// croyait hors corpus 57 % de ce qu'il a sous la main, et y plafonnait sa
// confiance à 75 %. Une valeur écrite en dur se périme à chaque siman ajouté —
// c'est la même pathologie que le garde-fou fondé sur la fréquence des mots.
const SECTION_LABELS = {
  'orach-chaim': 'Orah Haïm',
  'yoreh-deah': "Yoreh De'ah",
};
let _perimeter = null;
export function corpusPerimeter() {
  loadAndIndex();
  if (_perimeter) return _perimeter;
  // Plages contiguës de simanim, par section.
  const bySection = new Map();
  for (const c of _corpus.chunks) {
    const sec = c.section || 'orach-chaim';
    const n = Number(c.siman);
    if (!Number.isFinite(n)) continue;
    if (!bySection.has(sec)) bySection.set(sec, new Set());
    bySection.get(sec).add(n);
  }
  const parts = [];
  let totalSimanim = 0;
  for (const [sec, set] of [...bySection.entries()].sort()) {
    const nums = [...set].sort((a, b) => a - b);
    totalSimanim += nums.length;
    const ranges = [];
    let start = nums[0];
    let prev = nums[0];
    for (const n of nums.slice(1)) {
      if (n !== prev + 1) { ranges.push([start, prev]); start = n; }
      prev = n;
    }
    ranges.push([start, prev]);
    parts.push({
      section: sec,
      label: SECTION_LABELS[sec] || sec,
      ranges,
      text: ranges.map(([a, b]) => (a === b ? `${a}` : `${a}-${b}`)).join(', '),
      count: nums.length,
    });
  }
  _perimeter = {
    totalSimanim,
    totalChunks: _N,
    sections: parts,
    // Phrase prête à insérer dans le prompt système.
    summary: parts.map((p) => `${p.label} ${p.text} (${p.count} simanim)`).join(' · '),
  };
  return _perimeter;
}

export function getCorpusStats() {
  loadAndIndex();
  return { totalChunks: _N, totalSimanim: _corpus?.meta?.totalSimanim || 0, avgdl: _avgdl };
}
