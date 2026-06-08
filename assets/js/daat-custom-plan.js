// DAAT — Plan personnel
// Module client (vanilla) qui gère :
//   - le stockage localStorage du plan perso (clé 'daat:custom-plan:v1')
//   - la génération de la timeline à partir de data/limoud-simanim-catalog.json
//   - le calcul du jour courant, l'aperçu, le suivi de progression
//   - l'encodage/décodage des liens partagés (?p=base64)
//
// Tous les exports sont accessibles via window.DaatCustomPlan.
//
// Hypothèses :
//   - Corpus couvert : simanim 242 → 365 (Hilkhot Shabbat).
//   - Granularité minimale : 1 séif/jour, maximale 50/jour (garde-fou UI).
//   - Tous les calculs de dates sont en UTC pour éviter les drifts DST.

(function () {
  'use strict';

  // ============================================================
  // CONSTANTES & LANG
  // ============================================================

  var STORAGE_KEY = 'daat:custom-plan:v1';
  var AUTH_KEY = 'daat-auth-user-v1';
  var CATALOG_URL = '/data/limoud-simanim-catalog.json';

  var SIMAN_MIN = 242;
  var SIMAN_MAX = 365;
  var RATE_MIN = 1;
  var RATE_MAX = 50;

  var LANG = (function () {
    var l = (document.documentElement.lang || 'fr').toLowerCase();
    if (l.startsWith('he')) return 'he';
    if (l.startsWith('en')) return 'en';
    return 'fr';
  })();

  var DAYS_FR = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
  var DAYS_EN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  var DAYS_HE = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'];

  var MONTHS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
  var MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];

  // ============================================================
  // UTILITAIRES DATES (tout en UTC)
  // ============================================================

  function parseISO(s) {
    if (!s) return null;
    var p = String(s).split('-');
    if (p.length !== 3) return null;
    var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
    if (isNaN(d.getTime())) return null;
    return d;
  }

  function isoDate(d) {
    var y = d.getUTCFullYear();
    var m = ('0' + (d.getUTCMonth() + 1)).slice(-2);
    var day = ('0' + d.getUTCDate()).slice(-2);
    return y + '-' + m + '-' + day;
  }

  function todayUTC() {
    var n = new Date();
    return new Date(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate()));
  }

  function addDays(d, n) {
    var r = new Date(d.getTime());
    r.setUTCDate(r.getUTCDate() + n);
    return r;
  }

  function fmtDateLong(d) {
    if (!d) return '';
    var dow = d.getUTCDay();
    var day = d.getUTCDate();
    var month = d.getUTCMonth();
    var year = d.getUTCFullYear();
    if (LANG === 'en') return DAYS_EN[dow] + ', ' + MONTHS_EN[month] + ' ' + day + ', ' + year;
    if (LANG === 'he') return 'יום ' + DAYS_HE[dow] + ' · ' + day + '/' + (month + 1) + '/' + year;
    return DAYS_FR[dow] + ' ' + day + ' ' + MONTHS_FR[month] + ' ' + year;
  }

  function fmtDateShort(d) {
    if (!d) return '';
    var dow = d.getUTCDay();
    var day = d.getUTCDate();
    var month = d.getUTCMonth() + 1;
    if (LANG === 'en') return DAYS_EN[dow].slice(0, 3) + ' ' + month + '/' + day;
    if (LANG === 'he') return DAYS_HE[dow] + ' ' + day + '/' + month;
    return DAYS_FR[dow] + ' ' + day + '/' + month;
  }

  function dayName(dow) {
    if (LANG === 'en') return DAYS_EN[dow];
    if (LANG === 'he') return DAYS_HE[dow];
    return DAYS_FR[dow];
  }

  // ============================================================
  // STOCKAGE
  // ============================================================

  function defaultPlan() {
    var today = todayUTC();
    return {
      rate: 5,
      rateUnit: 'seifim_per_day',
      studyDays: [0, 1, 2, 3, 4],
      startDate: isoDate(today),
      startSiman: 242,
      email: '',
      emailNotif: false,
      completedDays: [],
      createdAt: new Date().toISOString(),
    };
  }

  function readPlan() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var p = JSON.parse(raw);
      return normalizePlan(p);
    } catch (_) {
      return null;
    }
  }

  function writePlan(plan) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(plan));
      return true;
    } catch (_) {
      return false;
    }
  }

  function clearPlan() {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (_) {
      return false;
    }
  }

  function hasPlan() {
    try {
      return !!localStorage.getItem(STORAGE_KEY);
    } catch (_) {
      return false;
    }
  }

  function readAuthEmail() {
    try {
      var raw = localStorage.getItem(AUTH_KEY);
      if (!raw) return '';
      var u = JSON.parse(raw);
      return (u && u.email) ? String(u.email) : '';
    } catch (_) {
      return '';
    }
  }

  // Garantit qu'un plan a tous les champs et des valeurs raisonnables.
  function normalizePlan(p) {
    var d = defaultPlan();
    if (!p || typeof p !== 'object') return d;
    var rate = parseInt(p.rate, 10);
    if (!isFinite(rate) || rate < RATE_MIN) rate = d.rate;
    if (rate > RATE_MAX) rate = RATE_MAX;

    var rateUnit = (p.rateUnit === 'siman_per_day') ? 'siman_per_day' : 'seifim_per_day';

    var studyDays = Array.isArray(p.studyDays)
      ? p.studyDays.map(function (x) { return parseInt(x, 10); }).filter(function (x) { return x >= 0 && x <= 6; })
      : d.studyDays;
    studyDays = studyDays.filter(function (v, i, a) { return a.indexOf(v) === i; });
    studyDays.sort(function (a, b) { return a - b; });
    if (!studyDays.length) studyDays = d.studyDays.slice();

    var startDate = parseISO(p.startDate) ? p.startDate : d.startDate;
    var startSiman = parseInt(p.startSiman, 10);
    if (!isFinite(startSiman) || startSiman < SIMAN_MIN || startSiman > SIMAN_MAX) {
      startSiman = SIMAN_MIN;
    }

    var email = typeof p.email === 'string' ? p.email.trim().slice(0, 254) : '';
    var emailNotif = !!p.emailNotif;
    var completedDays = Array.isArray(p.completedDays)
      ? p.completedDays.map(function (x) { return parseInt(x, 10); }).filter(function (x) { return x > 0; })
      : [];
    completedDays = completedDays.filter(function (v, i, a) { return a.indexOf(v) === i; });
    completedDays.sort(function (a, b) { return a - b; });

    return {
      rate: rate,
      rateUnit: rateUnit,
      studyDays: studyDays,
      startDate: startDate,
      startSiman: startSiman,
      email: email,
      emailNotif: emailNotif,
      completedDays: completedDays,
      createdAt: typeof p.createdAt === 'string' ? p.createdAt : d.createdAt,
    };
  }

  // ============================================================
  // CATALOGUE DES SIMANIM (cache module)
  // ============================================================

  var _catalogPromise = null;
  function loadCatalog() {
    if (_catalogPromise) return _catalogPromise;
    _catalogPromise = fetch(CATALOG_URL, { cache: 'force-cache' })
      .then(function (r) {
        if (!r.ok) throw new Error('Catalog HTTP ' + r.status);
        return r.json();
      })
      .then(function (j) {
        if (!j || !Array.isArray(j.simanim)) throw new Error('Catalog malformé');
        // Index par num
        var byNum = {};
        for (var i = 0; i < j.simanim.length; i++) {
          byNum[j.simanim[i].num] = j.simanim[i];
        }
        return {
          simanim: j.simanim,
          byNum: byNum,
          meta: j.meta || {},
        };
      })
      .catch(function (err) {
        _catalogPromise = null;
        throw err;
      });
    return _catalogPromise;
  }

  function simanTitle(siman) {
    if (!siman) return '';
    if (LANG === 'en' && siman.titleEn) return siman.titleEn;
    if (LANG === 'he' && siman.titleHe) return siman.titleHe;
    return siman.title || '';
  }

  // ============================================================
  // CALCULATEUR DE TIMELINE
  // ============================================================

  // Construit le découpage par séifim sans tenir compte des dates.
  // Renvoie un tableau d'entrées : { lotKey, simanNum, numHe, title, seifStart, seifEnd, lotIndex, lotTotal }
  function buildLots(plan, catalog) {
    var lots = [];
    var rate = plan.rate;
    var siman, lotsForSiman, lotIdx, totalSeifim, seif;
    var startNum = plan.startSiman;

    for (var num = startNum; num <= SIMAN_MAX; num++) {
      siman = catalog.byNum[num];
      if (!siman) continue;
      totalSeifim = siman.totalSeifim;
      if (plan.rateUnit === 'siman_per_day') {
        lots.push({
          simanNum: num,
          numHe: siman.numHe,
          title: simanTitle(siman),
          seifStart: 1,
          seifEnd: totalSeifim,
          lotIndex: 1,
          lotTotal: 1,
        });
        continue;
      }
      // seifim_per_day : on coupe en lots de "rate" séifim, jamais à cheval entre simanim.
      lotsForSiman = Math.max(1, Math.ceil(totalSeifim / rate));
      seif = 1;
      lotIdx = 1;
      while (seif <= totalSeifim) {
        var end = Math.min(totalSeifim, seif + rate - 1);
        lots.push({
          simanNum: num,
          numHe: siman.numHe,
          title: simanTitle(siman),
          seifStart: seif,
          seifEnd: end,
          lotIndex: lotIdx,
          lotTotal: lotsForSiman,
        });
        seif = end + 1;
        lotIdx++;
      }
    }
    return lots;
  }

  // Assigne une date à chaque lot, en sautant les jours non-étudiés.
  function assignDates(lots, plan) {
    var start = parseISO(plan.startDate);
    if (!start) start = todayUTC();
    var cur = new Date(start.getTime());
    var studySet = {};
    plan.studyDays.forEach(function (d) { studySet[d] = true; });

    // Garde-fou : si aucun jour n'est coché, on prend tous les jours pour
    // éviter une boucle infinie (mais c'est une erreur de validation côté UI).
    var anyStudyDay = plan.studyDays.length > 0;

    var out = new Array(lots.length);
    for (var i = 0; i < lots.length; i++) {
      // Avance jusqu'au prochain jour d'étude
      if (anyStudyDay) {
        var guard = 0;
        while (!studySet[cur.getUTCDay()]) {
          cur = addDays(cur, 1);
          guard++;
          if (guard > 14) break; // safety
        }
      }
      var entry = {
        dayNumber: i + 1,
        date: isoDate(cur),
        dow: cur.getUTCDay(),
        simanNum: lots[i].simanNum,
        numHe: lots[i].numHe,
        title: lots[i].title,
        seifStart: lots[i].seifStart,
        seifEnd: lots[i].seifEnd,
        lotIndex: lots[i].lotIndex,
        lotTotal: lots[i].lotTotal,
      };
      out[i] = entry;
      cur = addDays(cur, 1);
    }
    return out;
  }

  function buildTimeline(plan, catalog) {
    var p = normalizePlan(plan);
    var lots = buildLots(p, catalog);
    var entries = assignDates(lots, p);
    var endDate = entries.length ? parseISO(entries[entries.length - 1].date) : null;
    return {
      plan: p,
      entries: entries,
      totalDays: entries.length,
      startDate: parseISO(p.startDate),
      endDate: endDate,
    };
  }

  // ============================================================
  // ÉTAT COURANT (jour N de TON plan)
  // ============================================================

  // Renvoie l'index 1-based du dayNumber correspondant à "aujourd'hui",
  // ou null si le plan n'a pas encore commencé.
  // Si on est entre 2 jours d'étude (ex: vendredi pour un plan dim-jeu),
  // on renvoie le prochain jour à venir.
  function currentDayNumber(timeline, today) {
    if (!timeline.entries.length) return null;
    today = today || todayUTC();
    var todayISO = isoDate(today);
    // Si avant le premier jour
    if (todayISO < timeline.entries[0].date) return null;
    // Si après le dernier
    if (todayISO > timeline.entries[timeline.entries.length - 1].date) {
      return { state: 'finished', dayNumber: timeline.totalDays };
    }
    // Cherche le dayNumber dont la date == aujourd'hui, ou le prochain
    for (var i = 0; i < timeline.entries.length; i++) {
      if (timeline.entries[i].date === todayISO) {
        return { state: 'today', dayNumber: i + 1 };
      }
      if (timeline.entries[i].date > todayISO) {
        return { state: 'next', dayNumber: i + 1 };
      }
    }
    return null;
  }

  // ============================================================
  // PARTAGE — encodage/décodage URL
  // ============================================================

  function encodeShareablePlan(plan) {
    var p = normalizePlan(plan);
    // Champs non partagés : email, emailNotif, completedDays, createdAt
    var minimal = {
      r: p.rate,
      u: p.rateUnit === 'siman_per_day' ? 's' : 'd', // 's' = siman/day, 'd' = default seifim
      w: p.studyDays.join(''),
      d: p.startDate,
      n: p.startSiman,
    };
    try {
      var json = JSON.stringify(minimal);
      // base64url
      return btoa(unescape(encodeURIComponent(json)))
        .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    } catch (_) {
      return '';
    }
  }

  function decodeShareablePlan(s) {
    if (!s) return null;
    try {
      var b64 = String(s).replace(/-/g, '+').replace(/_/g, '/');
      while (b64.length % 4) b64 += '=';
      var json = decodeURIComponent(escape(atob(b64)));
      var m = JSON.parse(json);
      if (!m) return null;
      return normalizePlan({
        rate: m.r,
        rateUnit: m.u === 's' ? 'siman_per_day' : 'seifim_per_day',
        studyDays: String(m.w || '').split('').map(function (c) { return parseInt(c, 10); }),
        startDate: m.d,
        startSiman: m.n,
      });
    } catch (_) {
      return null;
    }
  }

  // ============================================================
  // PROGRESSION
  // ============================================================

  function markDayComplete(dayNumber) {
    var p = readPlan();
    if (!p) return false;
    if (!p.completedDays.includes(dayNumber)) {
      p.completedDays.push(dayNumber);
      p.completedDays.sort(function (a, b) { return a - b; });
      writePlan(p);
    }
    return true;
  }

  function unmarkDayComplete(dayNumber) {
    var p = readPlan();
    if (!p) return false;
    p.completedDays = p.completedDays.filter(function (d) { return d !== dayNumber; });
    writePlan(p);
    return true;
  }

  // ============================================================
  // EXPORTS
  // ============================================================

  window.DaatCustomPlan = {
    // Constantes
    STORAGE_KEY: STORAGE_KEY,
    SIMAN_MIN: SIMAN_MIN,
    SIMAN_MAX: SIMAN_MAX,
    RATE_MIN: RATE_MIN,
    RATE_MAX: RATE_MAX,
    LANG: LANG,

    // Stockage
    readPlan: readPlan,
    writePlan: writePlan,
    clearPlan: clearPlan,
    hasPlan: hasPlan,
    defaultPlan: defaultPlan,
    normalizePlan: normalizePlan,
    readAuthEmail: readAuthEmail,

    // Catalogue
    loadCatalog: loadCatalog,
    simanTitle: simanTitle,

    // Timeline
    buildTimeline: buildTimeline,
    currentDayNumber: currentDayNumber,

    // Partage
    encodeShareablePlan: encodeShareablePlan,
    decodeShareablePlan: decodeShareablePlan,

    // Progression
    markDayComplete: markDayComplete,
    unmarkDayComplete: unmarkDayComplete,

    // Dates
    parseISO: parseISO,
    isoDate: isoDate,
    todayUTC: todayUTC,
    addDays: addDays,
    fmtDateLong: fmtDateLong,
    fmtDateShort: fmtDateShort,
    dayName: dayName,
  };
})();
