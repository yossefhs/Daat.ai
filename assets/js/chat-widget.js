// DAAT.AI Chat Widget — Vanilla JS, zéro dépendance
// Usage : inclure le CSS + ce script ; le widget s'initialise automatiquement.

(function () {
  'use strict';

  // === ANALYTICS — events custom Vercel Web Analytics ===
  // File d'attente sûre : les appels sont mis en queue même si le script
  // /_vercel/insights n'est pas (encore) chargé ou est bloqué.
  function vaTrack(name, data) {
    try {
      window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
      window.va('event', data ? { name: name, data: data } : { name: name });
    } catch (_) {}
  }

  // === CONFIGURATION ===
  // Résolution de l'URL API :
  //  1. window.DAAT_CHAT_API_URL si défini (embed daattorah.com par exemple)
  //  2. Si on est sur un domaine *.vercel.app (preview ou prod du projet) → API du même domaine
  //     Ça permet de tester un preview branch sans que le widget tape la prod par erreur.
  //  3. Sinon (script chargé depuis un autre site sans config) → PROD par défaut.
  function resolveApiUrl() {
    if (window.DAAT_CHAT_API_URL) return window.DAAT_CHAT_API_URL;
    const host = window.location.host || '';
    if (/\.vercel\.app$/.test(host)) {
      return window.location.origin + '/api/chat';
    }
    return 'https://daatai.vercel.app/api/chat';
  }
  const API_URL = resolveApiUrl();
  const FEEDBACK_URL = API_URL.replace(/\/api\/chat\/?$/, '/api/feedback');
  const HISTORY_KEY = 'daat-conversations-v1'; // partagé avec chat.html
  const MAX_HISTORY = 50; // conversations max gardées
  const MAX_MESSAGES_PER_CONV = 60;

  // === MARKDOWN MINIMAL (sécurisé : échappe HTML d'abord) ===
  function escapeHtml(s) {
    return s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Détecte si un texte est majoritairement en hébreu (≥ ~50% des lettres).
  // → utilisé pour passer la bulle entière en RTL quand l'IA répond en hébreu pur.
  function detectMessageDir(text) {
    if (!text) return 'ltr';
    const heb = (text.match(/[א-תװ-ײ]/g) || []).length;
    const lat = (text.match(/[A-Za-zÀ-ÿ]/g) || []).length;
    if (heb === 0) return 'ltr';
    return heb >= lat ? 'rtl' : 'ltr';
  }

  // Texte nu d'un fragment HTML — pour décider la direction d'un BLOC sans que
  // les noms de balises/attributs (latins) faussent le comptage.
  function stripTags(html) {
    return String(html || '').replace(/<[^>]*>/g, '');
  }
  // Attribut dir à poser sur un bloc si son contenu est majoritairement hébreu.
  function blockDir(html) {
    return detectMessageDir(stripTags(html)) === 'rtl' ? ' dir="rtl"' : '';
  }

  function renderMarkdown(text) {
    if (!text) return '';
    let s = escapeHtml(text);

    // Code blocks (```...```)
    s = s.replace(/```([\s\S]*?)```/g, function (_, code) {
      return '<pre><code>' + code.trim() + '</code></pre>';
    });

    // Inline code
    s = s.replace(/`([^`\n]+)`/g, '<code>$1</code>');

    // Headings
    s = s.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    s = s.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    s = s.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    s = s.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Blockquote
    // Le bloc porte SA PROPRE direction : une citation hébraïque dans une réponse
    // française doit être RTL (barre de citation à droite, alignement à droite).
    s = s.replace(/^&gt; (.+)$/gm, function (_, c) {
      return '<blockquote' + blockDir(c) + '>' + c + '</blockquote>';
    });

    // Bold then italic (order matters)
    s = s.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g, '<em>$1</em>');

    // Links — détecte aussi les caractères encodés (Sefaria utilise %2C)
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (_, label, url) {
      // Heuristique : si l'URL contient des caractères hébreux ou %, c'est sûrement une URL Sefaria
      const isHebrew = /[֐-׿]/.test(label);
      const heb = isHebrew ? ' lang="he" dir="rtl"' : '';
      return '<a href="' + url + '" target="_blank" rel="noopener noreferrer"' + heb + '>' + label + '</a>';
    });

    // Tables (très simple — assume bien formé)
    s = s.replace(/\|(.+)\|\n\|[-:|\s]+\|\n((?:\|.+\|\n?)+)/g, function (_, headerLine, bodyLines) {
      const headers = headerLine.split('|').map(h => h.trim()).filter(Boolean);
      const rows = bodyLines.trim().split('\n').map(line =>
        line.split('|').map(c => c.trim()).filter((_, i, arr) => i > 0 && i < arr.length)
      );
      let html = '<table><thead><tr>';
      headers.forEach(h => html += '<th>' + h + '</th>');
      html += '</tr></thead><tbody>';
      rows.forEach(row => {
        html += '<tr>';
        row.forEach(c => html += '<td>' + c + '</td>');
        html += '</tr>';
      });
      html += '</tbody></table>';
      return html;
    });

    // Lists (ul/ol)
    s = s.replace(/(?:^[-*] .+(?:\n|$))+/gm, function (block) {
      const items = block.trim().split('\n').map(function (line) {
        const c = line.replace(/^[-*] /, '');
        return '<li' + blockDir(c) + '>' + c + '</li>';
      }).join('');
      return '<ul>' + items + '</ul>';
    });
    s = s.replace(/(?:^\d+\. .+(?:\n|$))+/gm, function (block) {
      const items = block.trim().split('\n').map(function (line) {
        const c = line.replace(/^\d+\. /, '');
        return '<li' + blockDir(c) + '>' + c + '</li>';
      }).join('');
      return '<ol>' + items + '</ol>';
    });

    // Hebrew text wrapping — isole les passages hébreux en RTL inline.
    // Inclut guillemets ASCII (") et typo + apostrophes pour ne pas casser
    // des abréviations comme אדה"ז, שו"ע, רמב"ם, מג"א, וכו׳, etc.
    s = s.replace(
      /([\u05D0-\u05EA\u05F0-\u05F2](?:[\u0591-\u05F4\u05D0-\u05EA\u05F0-\u05F2\s"'\u2019\u201C\u201D,.\-()?!:;\u2014\u2013\u2026\u00AB\u00BB]{0,2000}[\u05D0-\u05EA\u05F0-\u05F2])?)/g,
      '<span lang="he" dir="rtl" style="unicode-bidi:isolate;">$1</span>'
    );

    // Paragraphs (double newline)
    const paragraphs = s.split(/\n\n+/);
    s = paragraphs.map(p => {
      const trimmed = p.trim();
      if (!trimmed) return '';
      // Skip if already a block-level element
      if (/^<(h[1-6]|ul|ol|pre|blockquote|table)/.test(trimmed)) return trimmed;
      return '<p' + blockDir(trimmed) + '>' + trimmed.replace(/\n/g, '<br>') + '</p>';
    }).join('');

    return s;
  }

  // === LABELS NIVEAU + MINHAG ===
  const NIVEAU_LABELS = {
    debutant: 'Débutant — peu ou pas de bagage',
    intermediaire: 'Intermédiaire — bagage moyen',
    yeshiva: 'Élève de Yeshiva — étude régulière',
    lamdan: 'Lamdan / Talmid Hakham — pilpoul approfondi',
  };
  const MINHAG_LABELS = {
    sefarade: 'Séfarade (général — Choulchan Aroukh sans Rama)',
    marocain: 'Séfarade marocain',
    yemenite: 'Yéménite (Téimani — Baladi ou Shami selon le cas)',
    'edot-hamizrah': 'Edot HaMizrah (Iraqi / Bagdadi / Halabi)',
    ashkenaze: 'Ashkénaze (général — Choulchan Aroukh + Rama)',
    habad: 'Habad / Loubavitch',
    litvak: 'Litvak (yeshivot lituaniennes)',
    autre: 'Autre ou non spécifié — demander si pertinent',
  };

  // === LANGUAGE PREFERENCE ===
  const LANG_KEY = 'daat-lang-v1';
  const LANG_LABELS = {
    fr: 'français',
    he: 'hébreu (עברית)',
    en: 'English',
  };
  function getLang() {
    return localStorage.getItem(LANG_KEY) || pageUiLang();
  }
  function setLang(lang) {
    if (!LANG_LABELS[lang]) lang = 'fr';
    localStorage.setItem(LANG_KEY, lang);
  }


  // === I18N DE L'INTERFACE (fr / he / en, selon la langue de la page hôte) ===
  function pageUiLang() {
    const l = (document.documentElement.lang || 'fr').slice(0, 2);
    return (l === 'he' || l === 'en') ? l : 'fr';
  }
  const UI_STRINGS = {
    fr: {
      welcomeTitle: 'Bienvenue !', welcomeIntro: 'Je suis <strong>Daat</strong>, ton assistant d\'étude pour la Torah et la Halakha.',
      step1: '\u2460 Quel est ton niveau d\'étude ?', step2: '\u2461 Quel est ton minhag ?', step3: '\u2462 Langue de réponse',
      nivDebutant: '\ud83c\udf31 Débutant', nivInter: '\ud83d\udcda Bagage moyen', nivYeshiva: '\ud83d\udd6e Élève de Yeshiva', nivLamdan: '\ud83c\udf93 Talmid Hakham',
      minSef: '\ud83d\udd4e Séfarade', minAshk: '\u2744\ufe0f Ashkénaze', minHabad: '\ud83d\udd35 Habad / Loubavitch', minAutre: '\ud83e\udd37 Autre / pas sûr',
      start: '\u2713 Commencer l\'étude', placeholder: 'Pose ta question...', sendAria: 'Envoyer', msgAria: 'Votre message',
      headerSubtitle: 'Assistant d\'étude', historyTitle: 'Historique des conversations', newConv: '\uff0b Nouvelle conversation', newConvTitle: 'Nouvelle conversation',
      close: 'Fermer', scrollNew: '\u2193 Nouveau', footer: 'Daat peut faire des erreurs. Vérifie auprès de ton Rav.',
      ctxBadge: function (n, sec, niv) { return 'Tu étudies le <strong>Siman ' + n + '</strong> (' + sec + (niv ? ' · ' + niv : '') + ') — mes réponses en tiendront compte.'; },
      fabSiman: function (n) { return 'Poser une question sur le Siman ' + n; }, fabDefault: 'Poser une question de Halakha',
    },
    he: {
      welcomeTitle: '\u05d1\u05e8\u05d5\u05da \u05d4\u05d1\u05d0 !', welcomeIntro: '\u05d0\u05e0\u05d9 <strong>\u05d3\u05e2\u05ea</strong>, \u05e2\u05d5\u05d6\u05e8 \u05d4\u05dc\u05d9\u05de\u05d5\u05d3 \u05e9\u05dc\u05da \u05dc\u05ea\u05d5\u05e8\u05d4 \u05d5\u05dc\u05d4\u05dc\u05db\u05d4.',
      step1: '\u2460 \u05de\u05d4 \u05e8\u05de\u05ea \u05d4\u05dc\u05d9\u05de\u05d5\u05d3 \u05e9\u05dc\u05da ?', step2: '\u2461 \u05de\u05d4 \u05d4\u05de\u05e0\u05d4\u05d2 \u05e9\u05dc\u05da ?', step3: '\u2462 \u05e9\u05e4\u05ea \u05d4\u05ea\u05e9\u05d5\u05d1\u05d4',
      nivDebutant: '\ud83c\udf31 \u05de\u05ea\u05d7\u05d9\u05dc', nivInter: '\ud83d\udcda \u05e8\u05e7\u05e2 \u05d1\u05d9\u05e0\u05d5\u05e0\u05d9', nivYeshiva: '\ud83d\udd6e \u05d1\u05df \u05d9\u05e9\u05d9\u05d1\u05d4', nivLamdan: '\ud83c\udf93 \u05ea\u05dc\u05de\u05d9\u05d3 \u05d7\u05db\u05dd',
      minSef: '\ud83d\udd4e \u05e1\u05e4\u05e8\u05d3\u05d9', minAshk: '\u2744\ufe0f \u05d0\u05e9\u05db\u05e0\u05d6\u05d9', minHabad: '\ud83d\udd35 \u05d7\u05d1"\u05d3', minAutre: '\ud83e\udd37 \u05d0\u05d7\u05e8 / \u05dc\u05d0 \u05d1\u05d8\u05d5\u05d7',
      start: '\u2713 \u05dc\u05d4\u05ea\u05d7\u05d9\u05dc \u05dc\u05dc\u05de\u05d5\u05d3', placeholder: '\u05e9\u05d0\u05dc \u05d0\u05ea \u05e9\u05d0\u05dc\u05ea\u05da...', sendAria: '\u05e9\u05dc\u05d7', msgAria: '\u05d4\u05d4\u05d5\u05d3\u05e2\u05d4 \u05e9\u05dc\u05da',
      headerSubtitle: '\u05e2\u05d5\u05d6\u05e8 \u05dc\u05d9\u05de\u05d5\u05d3', historyTitle: '\u05d4\u05d9\u05e1\u05d8\u05d5\u05e8\u05d9\u05d9\u05ea \u05e9\u05d9\u05d7\u05d5\u05ea', newConv: '\uff0b \u05e9\u05d9\u05d7\u05d4 \u05d7\u05d3\u05e9\u05d4', newConvTitle: '\u05e9\u05d9\u05d7\u05d4 \u05d7\u05d3\u05e9\u05d4',
      close: '\u05e1\u05d2\u05d5\u05e8', scrollNew: '\u2193 \u05d7\u05d3\u05e9', footer: '\u05d3\u05e2\u05ea \u05e2\u05dc\u05d5\u05dc \u05dc\u05d8\u05e2\u05d5\u05ea. \u05d1\u05d3\u05d5\u05e7 \u05d0\u05e6\u05dc \u05d4\u05e8\u05d1 \u05e9\u05dc\u05da.',
      ctxBadge: function (n, sec, niv) { return '\u05d0\u05ea\u05d4 \u05dc\u05d5\u05de\u05d3 \u05db\u05e2\u05ea \u05d0\u05ea <strong>\u05e1\u05d9\u05de\u05df ' + n + '</strong> — \u05d4\u05ea\u05e9\u05d5\u05d1\u05d5\u05ea \u05d9\u05ea\u05d7\u05e9\u05d1\u05d5 \u05d1\u05db\u05da.'; },
      fabSiman: function (n) { return '\u05dc\u05e9\u05d0\u05d5\u05dc \u05e2\u05dc \u05e1\u05d9\u05de\u05df ' + n; }, fabDefault: '\u05dc\u05e9\u05d0\u05d5\u05dc \u05e9\u05d0\u05dc\u05d4 \u05d1\u05d4\u05dc\u05db\u05d4',
    },
    en: {
      welcomeTitle: 'Welcome!', welcomeIntro: 'I\'m <strong>Daat</strong>, your study assistant for Torah and Halacha.',
      step1: '\u2460 What is your study level?', step2: '\u2461 What is your minhag?', step3: '\u2462 Answer language',
      nivDebutant: '\ud83c\udf31 Beginner', nivInter: '\ud83d\udcda Some background', nivYeshiva: '\ud83d\udd6e Yeshiva student', nivLamdan: '\ud83c\udf93 Talmid Chacham',
      minSef: '\ud83d\udd4e Sephardic', minAshk: '\u2744\ufe0f Ashkenazi', minHabad: '\ud83d\udd35 Chabad', minAutre: '\ud83e\udd37 Other / not sure',
      start: '\u2713 Start learning', placeholder: 'Ask your question...', sendAria: 'Send', msgAria: 'Your message',
      headerSubtitle: 'Study assistant', historyTitle: 'Conversation history', newConv: '\uff0b New conversation', newConvTitle: 'New conversation',
      close: 'Close', scrollNew: '\u2193 New', footer: 'Daat can make mistakes. Check with your Rav.',
      ctxBadge: function (n, sec, niv) { return 'You are studying <strong>Siman ' + n + '</strong> (' + sec + (niv ? ' \u00b7 ' + niv : '') + ') — my answers will take it into account.'; },
      fabSiman: function (n) { return 'Ask a question about Siman ' + n; }, fabDefault: 'Ask a Halacha question',
    },
  };
  function uiT() { return UI_STRINGS[pageUiLang()]; }

  // === CONTEXTE DE NAVIGATION (siman consulté) ===
  // Détecte depuis l'URL le siman que l'utilisateur étudie, pour que Daat
  // ancre ses réponses dedans sans que l'utilisateur ait à le préciser.
  // Injecté dans le PREMIER MESSAGE (pattern niveau/minhag) — jamais dans le
  // system prompt, qui est caché 1h côté API et doit rester identique.
  const PAGE_LEVEL_LABELS = {
    'base': 'Niveau 1 — Base', 'lamdan': 'Niveau 2 — Lamdan',
    'synthese': 'Niveau 3 — Synthèse', 'daat-harav': 'Niveau 4 — Daat HaRav',
    'halakha': 'Niveau 4 — Halakha lemaassé',
  };
  const SECTION_NAMES = {
    'oh': 'Orah Haïm — Hilkhot Shabbat', 'yd': "Yoreh De'ah",
    'oh-quotidien': 'Orah Haïm — étude quotidienne',
    'shabbat': 'Orah Haïm — Hilkhot Shabbat', 'yoreh-deah': "Yoreh De'ah", 'orah-haim': 'Orah Haïm — étude quotidienne',
  };
  function detectSimanContext() {
    try {
      const path = window.location.pathname;
      let m = path.match(/^\/(oh|yd|oh-quotidien)\/(\d+)(?:\/(base|lamdan|synthese|daat-harav|halakha))?/);
      if (m) return { siman: Number(m[2]), sectionName: SECTION_NAMES[m[1]] || m[1], niveauPage: m[3] ? PAGE_LEVEL_LABELS[m[3]] : null };
      m = path.match(/\/sources\/(shabbat|yoreh-deah|orah-haim)\/siman-(\d+)(?:\/niveau-\d-([a-z-]+?))?(?:-he|-en)?\.html/)
        || path.match(/\/sources\/(shabbat|yoreh-deah|orah-haim)\/siman-(\d+)/);
      if (m) return { siman: Number(m[2]), sectionName: SECTION_NAMES[m[1]] || m[1], niveauPage: m[3] ? (PAGE_LEVEL_LABELS[m[3]] || null) : null };
      return null;
    } catch (_) { return null; }
  }
  function simanContextLine() {
    const ctx = detectSimanContext();
    if (!ctx) return '';
    const niveau = ctx.niveauPage ? `, page ${ctx.niveauPage}` : '';
    return `• Contexte : je consulte actuellement le Siman ${ctx.siman} (${ctx.sectionName}${niveau}) sur daattorah.com — sauf indication contraire, mes questions portent sur ce siman.\n`;
  }

  function buildIntroMessage(niveau, minhag) {
    const niveauTxt = NIVEAU_LABELS[niveau] || niveau;
    const minhagTxt = MINHAG_LABELS[minhag] || minhag;
    const lang = getLang();
    const langTxt = LANG_LABELS[lang] || 'français';
    return (
      `Bonjour Daat ! Voici mon profil pour cette session :\n` +
      `• Niveau : ${niveauTxt}\n` +
      `• Minhag : ${minhagTxt}\n` +
      `• Langue de réponse souhaitée : ${langTxt}\n` +
      simanContextLine() +
      `\nJe suis prêt à commencer. Adapte tes réponses à ce profil et réponds dans la langue indiquée.`
    );
  }

  // === CONVERSATION STORAGE (localStorage — persistent across sessions) ===
  function loadConversations() {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      if (!raw) return [];
      const arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr : [];
    } catch (e) { return []; }
  }
  function saveConversations(convs) {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(convs.slice(0, MAX_HISTORY))); } catch (e) {}
  }
  function upsertConversation(conv) {
    const all = loadConversations();
    const idx = all.findIndex(c => c.id === conv.id);
    conv.updatedAt = Date.now();
    if (!conv.createdAt) conv.createdAt = conv.updatedAt;
    if (conv.messages) conv.messages = conv.messages.slice(-MAX_MESSAGES_PER_CONV);
    if (idx >= 0) all[idx] = conv;
    else all.unshift(conv);
    saveConversations(all);
    syncConvUpsert(conv);
  }
  function deleteConversation(id) {
    saveConversations(loadConversations().filter(c => c.id !== id));
    syncConvDelete(id);
  }

  // === SERVER SYNC — par utilisateur connecté (cookie daat_session) ===
  // Mêmes principes que dans chat.html : no-op si pas connecté, push
  // debounce 1.5s, pull-and-merge au login. Stockage localStorage partagé
  // avec chat.html (clé HISTORY_KEY) — donc une conv créée par le widget
  // remonte dans chat.html et inversement, et la sync server est unifiée.
  const SYNC_BASE = 'https://daatai.vercel.app/api/conversations';
  const SYNC_DEBOUNCE_MS = 1500;
  const _syncUpsertQueue = new Map();
  let _syncUpsertTimer = null;

  function isLoggedIn() {
    return !!(window.daatAuth && window.daatAuth.getUser && window.daatAuth.getUser());
  }

  function _syncFetch(method, opts) {
    opts = opts || {};
    return fetch(SYNC_BASE + (opts.qs || ''), {
      method,
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
  }

  function _flushSyncUpserts() {
    _syncUpsertTimer = null;
    if (!isLoggedIn()) return;
    const items = Array.from(_syncUpsertQueue.values());
    _syncUpsertQueue.clear();
    for (const conv of items) {
      _syncFetch('POST', { body: conv }).catch(err => {
        console.warn('[widget-sync] upsert failed', conv.id, err);
      });
    }
  }

  function syncConvUpsert(conv) {
    if (!isLoggedIn()) return;
    _syncUpsertQueue.set(conv.id, conv);
    if (_syncUpsertTimer) clearTimeout(_syncUpsertTimer);
    _syncUpsertTimer = setTimeout(_flushSyncUpserts, SYNC_DEBOUNCE_MS);
  }

  function syncConvDelete(id) {
    if (!isLoggedIn()) return;
    _syncUpsertQueue.delete(id);
    _syncFetch('DELETE', { qs: '?id=' + encodeURIComponent(id) })
      .catch(err => console.warn('[widget-sync] delete failed', id, err));
  }

  async function syncPullAndMerge() {
    if (!isLoggedIn()) return;
    try {
      const res = await _syncFetch('GET');
      if (!res.ok) return;
      const data = await res.json();
      const serverConvs = Array.isArray(data.conversations) ? data.conversations : [];

      const local = loadConversations();
      const localMap = new Map(local.map(c => [c.id, c]));
      const merged = [];
      const serverIds = new Set();

      for (const sc of serverConvs) {
        const lc = localMap.get(sc.id);
        if (!lc || (sc.updatedAt || 0) >= (lc.updatedAt || 0)) {
          merged.push(sc);
        } else {
          merged.push(lc);
          _syncUpsertQueue.set(lc.id, lc);
        }
        serverIds.add(sc.id);
      }
      for (const lc of local) {
        if (!serverIds.has(lc.id)) {
          merged.push(lc);
          _syncUpsertQueue.set(lc.id, lc);
        }
      }

      merged.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
      saveConversations(merged);
      if (_syncUpsertQueue.size > 0) _flushSyncUpserts();

      // Re-render le panneau historique du widget si l'instance existe
      if (window.daatChatWidget && typeof window.daatChatWidget.renderHistoryList === 'function') {
        window.daatChatWidget.renderHistoryList();
      }
    } catch (err) {
      console.warn('[widget-sync] pull failed', err);
    }
  }

  function _bindAuthSyncHook() {
    if (window.daatAuth && typeof window.daatAuth.onChange === 'function') {
      window.daatAuth.onChange(user => {
        if (user) syncPullAndMerge();
      });
      if (window.daatAuth.getUser && window.daatAuth.getUser()) {
        syncPullAndMerge();
      }
    } else {
      setTimeout(_bindAuthSyncHook, 100);
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _bindAuthSyncHook);
  } else {
    _bindAuthSyncHook();
  }
  function getConversation(id) {
    return loadConversations().find(c => c.id === id) || null;
  }
  function newConversationId() {
    return 'c-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7);
  }
  function autoTitleFromMessage(text) {
    let t = text;
    if (t.startsWith('[Profil de cette session]')) {
      const lines = t.split('\n');
      const blankIdx = lines.findIndex((l, i) => i > 0 && l.trim() === '');
      if (blankIdx > 0) t = lines.slice(blankIdx + 1).join('\n');
    }
    // Strip leading "[Ma question]" marker too
    t = t.replace(/^\[Ma question\]\s*/i, '');
    t = t.trim().replace(/\s+/g, ' ');
    if (!t) return 'Nouvelle conversation';
    return t.length > 50 ? t.slice(0, 50) + '…' : t;
  }
  function relativeDate(ts) {
    if (!ts) return '';
    const d = new Date(ts), now = new Date();
    const sameDay = d.toDateString() === now.toDateString();
    const yest = new Date(now); yest.setDate(yest.getDate() - 1);
    const isYest = d.toDateString() === yest.toDateString();
    if (sameDay) return 'Aujourd\'hui ' + d.toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit'});
    if (isYest) return 'Hier ' + d.toLocaleTimeString('fr-FR', {hour:'2-digit',minute:'2-digit'});
    return d.toLocaleDateString('fr-FR', {day:'2-digit', month:'short'});
  }

  // === WIDGET ===
  class DaatChatWidget {
    constructor() {
      this.messages = [];                // conversation courante (vide à l'ouverture)
      this.currentConvId = null;         // id de la conversation en cours, null = aucune
      this.selectedNiveau = null;
      this.selectedMinhag = null;
      this.isOpen = false;
      this.isStreaming = false;
      this.isHistoryOpen = false;
      this.rateInfo = null;              // dernier rate_info reçu (plan, Aperçu, etc.)
      this.previousAperçuRemaining = null; // pour détecter Q3→Q4 (transition Aperçu→Standard)
      this.build();
      this.attach();
      this.renderMessages();             // affiche l'écran d'accueil (vierge)
    }

    build() {
      // Floating button
      this.button = document.createElement('button');
      this.button.className = 'daat-chat-button';
      const fabCtx = detectSimanContext();
      this.button.setAttribute('aria-label', fabCtx ? uiT().fabSiman(fabCtx.siman) : uiT().fabDefault);
      this.button.title = fabCtx ? uiT().fabSiman(fabCtx.siman) : uiT().fabDefault;
      this.button.innerHTML =
        '<span class="daat-chat-button-icon">דעת</span>' +
        '<span class="daat-chat-button-pulse"></span>';

      // Panel
      this.panel = document.createElement('div');
      this.panel.className = 'daat-chat-panel';
      this.panel.setAttribute('role', 'dialog');
      this.panel.setAttribute('aria-label', 'Chat avec Daat — assistant Torah');
      if (pageUiLang() === 'he') this.panel.setAttribute('dir', 'rtl');
      this.panel.innerHTML = `
        <div class="daat-chat-header">
          <button class="daat-chat-history-btn" id="daat-chat-history-btn" title="${uiT().historyTitle}" aria-label="${uiT().historyTitle}">📋</button>
          <div class="daat-chat-header-logo">דעת</div>
          <div class="daat-chat-header-info">
            <div class="daat-chat-header-title">Daat</div>
            <div class="daat-chat-header-subtitle">${uiT().headerSubtitle}</div>
          </div>
          <button class="daat-chat-reset" id="daat-chat-reset" title="${uiT().newConvTitle}" aria-label="${uiT().newConvTitle}">↺</button>
        </div>
        <div class="daat-chat-messages" id="daat-chat-messages" dir="ltr"></div>
        <div class="daat-chat-history-panel" id="daat-chat-history-panel">
          <div class="daat-chat-history-header">
            <span>${uiT().historyTitle}</span>
            <button class="daat-chat-history-close" id="daat-chat-history-close" aria-label="${uiT().close}">✕</button>
          </div>
          <button class="daat-chat-history-new" id="daat-chat-history-new">${uiT().newConv}</button>
          <div class="daat-chat-history-list" id="daat-chat-history-list"></div>
        </div>
        <button class="daat-chat-scroll-down" id="daat-chat-scroll-down" type="button" aria-label="${uiT().scrollNew}">${uiT().scrollNew}</button>
        <div class="daat-status-banner" id="daat-status-banner" data-status="hidden"></div>
        <div class="daat-chat-input-area">
          <div class="daat-chat-input-wrapper">
            <textarea
              class="daat-chat-input"
              id="daat-chat-input"
              placeholder="${uiT().placeholder}"
              rows="1"
              dir="auto"
              aria-label="${uiT().msgAria}"
            ></textarea>
            <button class="daat-chat-send" id="daat-chat-send" aria-label="${uiT().sendAria}">→</button>
          </div>
          <div class="daat-chat-footer">${uiT().footer}</div>
        </div>
      `;

      document.body.appendChild(this.button);
      document.body.appendChild(this.panel);

      this.messagesEl = this.panel.querySelector('#daat-chat-messages');
      this.inputEl = this.panel.querySelector('#daat-chat-input');
      this.sendBtn = this.panel.querySelector('#daat-chat-send');
      this.scrollDownBtn = this.panel.querySelector('#daat-chat-scroll-down');
      this.resetBtn = this.panel.querySelector('#daat-chat-reset');
      this.historyBtn = this.panel.querySelector('#daat-chat-history-btn');
      this.historyPanel = this.panel.querySelector('#daat-chat-history-panel');
      this.historyCloseBtn = this.panel.querySelector('#daat-chat-history-close');
      this.historyNewBtn = this.panel.querySelector('#daat-chat-history-new');
      this.historyListEl = this.panel.querySelector('#daat-chat-history-list');
      this.bannerEl = this.panel.querySelector('#daat-status-banner');
      this.userScrolledUp = false;
    }

    attachDrag() {
      const header = this.panel.querySelector('.daat-chat-header');
      const panel = this.panel;
      if (!header) return;

      // Restaurer la position sauvegardée
      try {
        const saved = JSON.parse(localStorage.getItem('daat-chat-pos') || 'null');
        if (saved && window.innerWidth > 760) {
          // Clamp dans le viewport au cas où la taille a changé
          const maxLeft = window.innerWidth - 100;
          const maxTop = window.innerHeight - 100;
          const left = Math.max(0, Math.min(saved.left, maxLeft));
          const top = Math.max(0, Math.min(saved.top, maxTop));
          panel.style.left = left + 'px';
          panel.style.top = top + 'px';
          panel.style.right = 'auto';
          panel.style.bottom = 'auto';
        }
      } catch (_) {}

      let dragging = false;
      let startX = 0, startY = 0, startLeft = 0, startTop = 0;

      const onDown = (e) => {
        // Pas de drag sur mobile (panel plein écran)
        if (window.innerWidth <= 760) return;
        // Pas de drag si on a cliqué sur un bouton/lien à l'intérieur du header
        if (e.target.closest('button, a, input')) return;

        const point = e.touches ? e.touches[0] : e;
        dragging = true;
        panel.classList.add('is-dragging');

        // Position courante du panel (gère le cas initial où c'est bottom/right)
        const rect = panel.getBoundingClientRect();
        startLeft = rect.left;
        startTop = rect.top;
        startX = point.clientX;
        startY = point.clientY;

        // Bascule en left/top pour le drag
        panel.style.left = startLeft + 'px';
        panel.style.top = startTop + 'px';
        panel.style.right = 'auto';
        panel.style.bottom = 'auto';

        if (e.cancelable) e.preventDefault();
      };

      const onMove = (e) => {
        if (!dragging) return;
        const point = e.touches ? e.touches[0] : e;
        const dx = point.clientX - startX;
        const dy = point.clientY - startY;
        // Clamp dans le viewport (laisse au moins le header visible)
        const maxLeft = window.innerWidth - 80;
        const maxTop = window.innerHeight - 60;
        const newLeft = Math.max(0, Math.min(startLeft + dx, maxLeft));
        const newTop = Math.max(0, Math.min(startTop + dy, maxTop));
        panel.style.left = newLeft + 'px';
        panel.style.top = newTop + 'px';
      };

      const onUp = () => {
        if (!dragging) return;
        dragging = false;
        panel.classList.remove('is-dragging');
        try {
          localStorage.setItem('daat-chat-pos', JSON.stringify({
            left: parseFloat(panel.style.left) || 0,
            top: parseFloat(panel.style.top) || 0,
          }));
        } catch (_) {}
      };

      header.addEventListener('mousedown', onDown);
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
      header.addEventListener('touchstart', onDown, { passive: false });
      window.addEventListener('touchmove', onMove, { passive: false });
      window.addEventListener('touchend', onUp);

      // Double-clic sur le header → reset à la position par défaut
      header.addEventListener('dblclick', (e) => {
        if (e.target.closest('button, a, input')) return;
        panel.style.left = '';
        panel.style.top = '';
        panel.style.right = '';
        panel.style.bottom = '';
        try { localStorage.removeItem('daat-chat-pos'); } catch (_) {}
      });
    }

    attach() {
      this.attachDrag();
      this.button.addEventListener('click', () => this.toggle());

      // Bouton reset — remet à zéro la conversation (ne supprime pas l'historique)
      if (this.resetBtn) {
        this.resetBtn.addEventListener('click', () => this.startFreshState());
      }

      // Bouton historique — ouvre/ferme le panneau d'historique
      if (this.historyBtn) {
        this.historyBtn.addEventListener('click', () => this.toggleHistory());
      }
      if (this.historyCloseBtn) {
        this.historyCloseBtn.addEventListener('click', () => this.closeHistory());
      }
      if (this.historyNewBtn) {
        this.historyNewBtn.addEventListener('click', () => {
          this.startFreshState();
          this.closeHistory();
        });
      }

      this.sendBtn.addEventListener('click', () => this.send());

      this.inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.send();
        }
      });

      // Track manual scrolling — seulement via wheel/touch (pas les scrolls programmatiques)
      // pour éviter que le scroll auto pendant le streaming soit détecté comme "user scroll"
      const markScrolledUp = () => {
        const el = this.messagesEl;
        const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
        if (distanceFromBottom > 60) {
          this.userScrolledUp = true;
          if (this.scrollDownBtn) this.scrollDownBtn.classList.toggle('is-visible', this.isStreaming);
        }
      };
      this.messagesEl.addEventListener('wheel', markScrolledUp, { passive: true });
      this.messagesEl.addEventListener('touchstart', () => { this._touchScrolling = true; }, { passive: true });
      this.messagesEl.addEventListener('touchend', () => { this._touchScrolling = false; }, { passive: true });
      this.messagesEl.addEventListener('scroll', () => {
        const el = this.messagesEl;
        const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
        const isAtBottom = distanceFromBottom < 30;
        // Quand l'utilisateur revient en bas, on réactive l'auto-scroll
        if (isAtBottom) {
          this.userScrolledUp = false;
          if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');
        } else if (this._touchScrolling) {
          this.userScrolledUp = true;
          if (this.scrollDownBtn) this.scrollDownBtn.classList.toggle('is-visible', this.isStreaming);
        }
      });

      // Bouton "↓ Nouveau" — ramène en bas et reprend l'auto-scroll
      if (this.scrollDownBtn) {
        this.scrollDownBtn.addEventListener('click', () => {
          this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
          this.userScrolledUp = false;
          this.scrollDownBtn.classList.remove('is-visible');
        });
      }

      // Auto-resize textarea
      this.inputEl.addEventListener('input', () => {
        this.inputEl.style.height = 'auto';
        this.inputEl.style.height = Math.min(this.inputEl.scrollHeight, 120) + 'px';
      });
    }

    toggle() {
      this.isOpen = !this.isOpen;
      this.panel.classList.toggle('is-open', this.isOpen);
      this.button.classList.toggle('is-open', this.isOpen);
      if (this.isOpen) {
        vaTrack('chat_open');
        // À chaque ouverture, on revient sur l'écran d'accueil vierge
        // (l'historique des conversations reste accessible via le bouton 📋)
        if (!this.isStreaming) this.startFreshState();
        setTimeout(() => this.inputEl.focus(), 250);
      }
    }

    toggleHistory() {
      if (this.isHistoryOpen) this.closeHistory();
      else this.openHistory();
    }
    openHistory() {
      this.isHistoryOpen = true;
      this.historyPanel.classList.add('is-open');
      this.renderHistoryList();
    }
    closeHistory() {
      this.isHistoryOpen = false;
      this.historyPanel.classList.remove('is-open');
    }

    renderHistoryList() {
      const convs = loadConversations();
      if (convs.length === 0) {
        this.historyListEl.innerHTML = '<div class="daat-chat-history-empty">Aucune conversation pour l\'instant. Choisis ton niveau et ton minhag, puis pose ta première question.</div>';
        return;
      }
      this.historyListEl.innerHTML = '';
      const widget = this;
      convs.forEach(c => {
        const item = document.createElement('div');
        item.className = 'daat-chat-history-item' + (c.id === widget.currentConvId ? ' is-active' : '');
        item.innerHTML = `
          <div class="daat-chat-history-item-content">
            <div class="daat-chat-history-item-title"></div>
            <div class="daat-chat-history-item-meta"></div>
          </div>
          <button class="daat-chat-history-item-del" title="Supprimer" aria-label="Supprimer cette conversation">🗑</button>
        `;
        item.querySelector('.daat-chat-history-item-title').textContent = c.title || 'Nouvelle conversation';
        const niveau = c.niveau || '?', minhag = c.minhag || '?';
        item.querySelector('.daat-chat-history-item-meta').textContent =
          `${niveau} · ${minhag} · ${relativeDate(c.updatedAt || c.createdAt)}`;
        item.addEventListener('click', e => {
          if (e.target.closest('.daat-chat-history-item-del')) {
            e.stopPropagation();
            if (confirm('Supprimer cette conversation ?')) {
              deleteConversation(c.id);
              if (widget.currentConvId === c.id) widget.startFreshState();
              widget.renderHistoryList();
            }
            return;
          }
          widget.loadConvIntoView(c.id);
          widget.closeHistory();
        });
        this.historyListEl.appendChild(item);
      });
    }

    loadConvIntoView(id) {
      const conv = getConversation(id);
      if (!conv) return;
      this.currentConvId = conv.id;
      this.messages = conv.messages || [];
      this.selectedNiveau = conv.niveau;
      this.selectedMinhag = conv.minhag;
      this.messagesEl.innerHTML = '';
      // Bandeau méta
      const meta = document.createElement('div');
      meta.className = 'daat-chat-conv-meta';
      meta.textContent = `📋 ${conv.title || ''} · ${conv.niveau || '?'} · ${conv.minhag || '?'}`;
      this.messagesEl.appendChild(meta);
      this.messages.forEach(m => {
        const el = this.appendMessage(m.role, m.content);
        if (m.role === 'assistant') this.attachFeedbackBar(el, m.content);
      });
      this.scrollToBottom(true);
      setTimeout(() => this.inputEl.focus(), 100);
    }

    startFreshState() {
      if (this.isStreaming) return;
      this.currentConvId = null;
      this.messages = [];
      this.selectedNiveau = null;
      this.selectedMinhag = null;
      this.userScrolledUp = false;
      if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');
      this.renderMessages(); // affiche l'écran d'accueil avec chips
    }

    persistConversation() {
      if (!this.currentConvId) return;
      const existing = getConversation(this.currentConvId);
      const firstUserMsg = this.messages.find(m => m.role === 'user');
      const niveauLabel = NIVEAU_LABELS[this.selectedNiveau] || this.selectedNiveau || existing?.niveau;
      const minhagLabel = MINHAG_LABELS[this.selectedMinhag] || this.selectedMinhag || existing?.minhag;
      const title = existing?.title || (firstUserMsg ? autoTitleFromMessage(firstUserMsg.content) : 'Nouvelle conversation');
      upsertConversation({
        id: this.currentConvId,
        title,
        niveau: niveauLabel,
        minhag: minhagLabel,
        createdAt: existing?.createdAt || Date.now(),
        updatedAt: Date.now(),
        messages: this.messages,
      });
    }

    renderMessages() {
      if (this.messages.length === 0) {
        // À chaque ouverture, écran vierge — pas de pré-sélection
        // (l'utilisateur doit toujours re-choisir niveau et minhag)
        this.messagesEl.innerHTML = `
          <div class="daat-chat-welcome">
            <span class="heb">דעת</span>
            <h3>${uiT().welcomeTitle}</h3>
            <p>${uiT().welcomeIntro}</p>
            ${(() => {
              const ctx = detectSimanContext();
              if (!ctx) return '';
              const niveau = ctx.niveauPage ? ' · ' + ctx.niveauPage : '';
              return '<div class="daat-chat-context-badge" style="display:inline-flex;align-items:center;gap:7px;margin:2px 0 10px;padding:7px 14px;background:rgba(197,165,90,0.12);border:1px solid rgba(197,165,90,0.45);border-radius:3px;font-size:13px;color:#5a4a1a;">' +
                '<span>📖</span><span>' + uiT().ctxBadge(ctx.siman, ctx.sectionName, ctx.niveauPage) + '</span></div>';
            })()}

            <div class="daat-chat-step">
              <div class="daat-chat-step-label">${uiT().step1}</div>
              <div class="daat-chat-chips" data-group="niveau">
                <button class="daat-chat-chip" data-value="debutant">${uiT().nivDebutant}</button>
                <button class="daat-chat-chip" data-value="intermediaire">${uiT().nivInter}</button>
                <button class="daat-chat-chip" data-value="yeshiva">${uiT().nivYeshiva}</button>
                <button class="daat-chat-chip" data-value="lamdan">${uiT().nivLamdan}</button>
              </div>
            </div>

            <div class="daat-chat-step">
              <div class="daat-chat-step-label">${uiT().step2}</div>
              <div class="daat-chat-chips" data-group="minhag">
                <button class="daat-chat-chip" data-value="sefarade">${uiT().minSef}</button>
                <button class="daat-chat-chip" data-value="ashkenaze">${uiT().minAshk}</button>
                <button class="daat-chat-chip" data-value="habad">${uiT().minHabad}</button>
                <button class="daat-chat-chip" data-value="autre">${uiT().minAutre}</button>
              </div>
            </div>

            <div class="daat-chat-step">
              <div class="daat-chat-step-label">${uiT().step3}</div>
              <div class="daat-chat-chips" data-group="lang">
                <button class="daat-chat-chip" data-value="fr">🇫🇷 Français</button>
                <button class="daat-chat-chip" data-value="he" style="font-family:'Frank Ruhl Libre',serif;">עברית</button>
                <button class="daat-chat-chip" data-value="en">🇬🇧 English</button>
              </div>
            </div>

            <button class="daat-chat-start" id="daat-chat-start" disabled>${uiT().start}</button>
            <div class="signature">דעת התורה לעומקה</div>
          </div>
        `;

        const updateStartBtn = () => {
          const btn = this.messagesEl.querySelector('#daat-chat-start');
          if (btn) btn.disabled = !(this.selectedNiveau && this.selectedMinhag);
        };
        updateStartBtn();

        // Pré-sélectionne la langue précédemment choisie
        const currentLang = getLang();
        const langChip = this.messagesEl.querySelector(`.daat-chat-chips[data-group="lang"] .daat-chat-chip[data-value="${currentLang}"]`);
        if (langChip) langChip.classList.add('is-selected');

        // Toggle des chips (sélection unique par groupe)
        this.messagesEl.querySelectorAll('.daat-chat-chips').forEach(group => {
          const groupName = group.dataset.group;
          group.querySelectorAll('.daat-chat-chip').forEach(chip => {
            chip.addEventListener('click', () => {
              group.querySelectorAll('.daat-chat-chip').forEach(c => c.classList.remove('is-selected'));
              chip.classList.add('is-selected');
              const val = chip.dataset.value;
              if (groupName === 'niveau') this.selectedNiveau = val;
              if (groupName === 'minhag') this.selectedMinhag = val;
              if (groupName === 'lang') setLang(val);
              updateStartBtn();
            });
          });
        });

        // Bouton "Commencer"
        const startBtn = this.messagesEl.querySelector('#daat-chat-start');
        if (startBtn) {
          startBtn.addEventListener('click', () => {
            if (!this.selectedNiveau || !this.selectedMinhag) return;
            this.inputEl.value = buildIntroMessage(this.selectedNiveau, this.selectedMinhag);
            this.send();
          });
        }
        return;
      }

      this.messagesEl.innerHTML = '';
      this.messages.forEach(m => this.appendMessage(m.role, m.content));
    }

    appendMessage(role, content) {
      const el = document.createElement('div');
      el.className = 'daat-chat-message is-' + role;
      // Direction adaptative : LTR par défaut, RTL si le message est
      // majoritairement en hébreu (ex: l'IA répond en hébreu pur).
      // Cas LTR → les passages hébreux restent wrappés en <span dir="rtl">.
      el.setAttribute('dir', detectMessageDir(content));
      if (role === 'assistant') {
        el.innerHTML = renderMarkdown(content);
      } else {
        el.textContent = content;
      }
      this.messagesEl.appendChild(el);
      this.scrollToBottom();
      return el;
    }

    attachFeedbackBar(assistantEl, answerText) {
      if (!answerText || answerText.length < 20) return;
      if (assistantEl.dataset.fbAttached) return;
      assistantEl.dataset.fbAttached = '1';
      // Find the last user message to associate
      let lastUserContent = '';
      for (let i = this.messages.length - 1; i >= 0; i--) {
        if (this.messages[i].role === 'user') { lastUserContent = this.messages[i].content; break; }
        if (this.messages[i].role === 'assistant' && this.messages[i].content === answerText) continue;
      }
      // i18n minimal selon la lang de la page hôte
      const pageLang = (document.documentElement.lang || 'fr').slice(0, 2);
      const i18n = {
        fr: { label: 'Cette réponse :', up: 'Utile', down: 'À corriger', share: '📤 Partager', shareTitle: 'Partager cette réponse' },
        he: { label: 'תשובה זו:', up: 'מועילה', down: 'טעונה תיקון', share: '📤 שתף', shareTitle: 'שתף תשובה זו' },
        en: { label: 'This answer:', up: 'Helpful', down: 'Needs correction', share: '📤 Share', shareTitle: 'Share this answer' },
      }[pageLang] || { label: 'Cette réponse :', up: 'Utile', down: 'À corriger', share: '📤 Partager', shareTitle: 'Partager cette réponse' };

      const bar = document.createElement('div');
      bar.className = 'daat-chat-feedback';
      bar.innerHTML = `
        <span class="daat-chat-feedback-label">${i18n.label}</span>
        <button class="daat-chat-fb-btn daat-chat-fb-up" title="${i18n.up}">👍</button>
        <button class="daat-chat-fb-btn daat-chat-fb-down" title="${i18n.down}">👎</button>
        <button class="daat-chat-fb-btn daat-chat-fb-share" title="${i18n.shareTitle}">${i18n.share}</button>
        <span class="daat-chat-feedback-thanks" style="display:none;"></span>
      `;
      // Insérer la barre APRÈS la bulle (pas dedans) — en dessous du texte
      assistantEl.insertAdjacentElement('afterend', bar);
      const widget = this;
      bar.querySelector('.daat-chat-fb-up').addEventListener('click', () => {
        widget.sendFeedback('👍', bar, lastUserContent, answerText);
      });
      bar.querySelector('.daat-chat-fb-down').addEventListener('click', () => {
        widget.askDownComment(assistantEl, bar, lastUserContent, answerText);
      });
      bar.querySelector('.daat-chat-fb-share').addEventListener('click', () => {
        widget.shareResponse(bar, lastUserContent, answerText, pageLang);
      });
    }

    // Partage une réponse Daat — Web Share API natif si dispo (mobile),
    // sinon copie presse-papier. Inclut TOUJOURS l'URL daattorah.com en bas
    // pour la promotion du site auprès du destinataire.
    async shareResponse(bar, question, answer, pageLang = 'fr') {
      const SITE_URL = 'https://daattorah.com';
      const lang = (pageLang || 'fr').slice(0, 2);
      const footers = {
        fr: `— Daat Torah · ${SITE_URL}\nÉtude halakhique en français · Choulhan Aroukh trilingue + assistant IA`,
        he: `— דעת תורה · ${SITE_URL}\nלימוד הלכה רב-לשוני · שולחן ערוך עם עוזר בינה מלאכותית`,
        en: `— Daat Torah · ${SITE_URL}\nMultilingual halacha study · Shulchan Aruch with AI assistant`,
      };
      const titles = { fr: 'Réponse de Daat Torah', he: 'תשובה מדעת תורה', en: 'Answer from Daat Torah' };
      const statusMsgs = {
        fr: { shared: 'Partagé ✓', copied: 'Copié ✓', fail: 'Copie échouée — sélectionne le texte manuellement' },
        he: { shared: 'שותף ✓', copied: 'הועתק ✓', fail: 'העתקה נכשלה — בחר את הטקסט ידנית' },
        en: { shared: 'Shared ✓', copied: 'Copied ✓', fail: 'Copy failed — select text manually' },
      };
      const msg = statusMsgs[lang] || statusMsgs.fr;

      const q = (question || '').trim();
      const a = (answer || '').trim();
      const text = (q ? `❓ ${q}\n\n` : '') + `${a}\n\n` + (footers[lang] || footers.fr);

      const thanks = bar.querySelector('.daat-chat-feedback-thanks');
      const showStatus = (m, ms = 2500) => {
        thanks.style.display = '';
        thanks.textContent = m;
        setTimeout(() => {
          if (thanks.textContent === m) thanks.style.display = 'none';
        }, ms);
      };

      if (navigator.share) {
        try {
          await navigator.share({ title: titles[lang] || titles.fr, text, url: SITE_URL });
          showStatus(msg.shared);
          return;
        } catch (err) {
          if (err && err.name === 'AbortError') return;
        }
      }

      try {
        await navigator.clipboard.writeText(text);
        showStatus(msg.copied);
      } catch (err) {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed'; ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); showStatus(msg.copied); }
        catch { showStatus(msg.fail, 4000); }
        ta.remove();
      }
    }

    askDownComment(assistantEl, bar, question, answer) {
      bar.querySelector('.daat-chat-fb-down').classList.add('is-selected');
      bar.querySelectorAll('.daat-chat-fb-btn').forEach(b => b.disabled = true);
      if (bar.nextElementSibling && bar.nextElementSibling.classList.contains('daat-chat-fb-comment')) return;
      const ta = document.createElement('textarea');
      ta.className = 'daat-chat-fb-comment';
      ta.placeholder = 'Optionnel : pourquoi ? (incorrect, source manquante…)';
      const actions = document.createElement('div');
      actions.className = 'daat-chat-fb-comment-actions';
      actions.innerHTML = `
        <button class="daat-chat-fb-send">Envoyer</button>
        <button class="daat-chat-fb-skip">Sans commentaire</button>
      `;
      bar.insertAdjacentElement('afterend', ta);
      ta.insertAdjacentElement('afterend', actions);
      ta.focus();
      const widget = this;
      actions.querySelector('.daat-chat-fb-send').addEventListener('click', () => {
        widget.sendFeedback('👎', bar, question, answer, ta.value.trim());
        ta.remove(); actions.remove();
      });
      actions.querySelector('.daat-chat-fb-skip').addEventListener('click', () => {
        widget.sendFeedback('👎', bar, question, answer, '');
        ta.remove(); actions.remove();
      });
    }

    async sendFeedback(rating, bar, question, answer, comment) {
      const upBtn = bar.querySelector('.daat-chat-fb-up');
      const downBtn = bar.querySelector('.daat-chat-fb-down');
      const thanks = bar.querySelector('.daat-chat-feedback-thanks');
      upBtn.disabled = true; downBtn.disabled = true;
      if (rating === '👍') upBtn.classList.add('is-selected');
      else downBtn.classList.add('is-selected');
      thanks.style.display = '';
      thanks.textContent = 'Envoi…';
      try {
        const res = await fetch(FEEDBACK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rating,
            question: question || '',
            answer: answer || '',
            niveau: NIVEAU_LABELS[this.selectedNiveau] || this.selectedNiveau,
            minhag: MINHAG_LABELS[this.selectedMinhag] || this.selectedMinhag,
            comment: comment || '',
            conversationId: this.currentConvId,
            page: window.location.pathname,
          }),
        });
        if (!res.ok) {
          const j = await res.json().catch(() => ({}));
          throw new Error(j.error || 'HTTP ' + res.status);
        }
        thanks.textContent = rating === '👍' ? 'Merci !' : 'Reçu — merci.';
      } catch (err) {
        thanks.textContent = 'Erreur : ' + err.message;
        thanks.style.color = '#C0392B';
      }
    }

    // ─── Bannière d'état au-dessus de l'input (Aperçu/Standard/Premium) ───
    updateStatusBanner() {
      const r = this.rateInfo;
      const el = this.bannerEl;
      if (!el || !r) return;
      if (r.ux_status === 'meta' || r.is_subscriber === false && r.plan === 'anonymous' && r.preview_used === 0 && !r.is_aperçu) {
        // Premier contact, méta-question : pas de bannière (zéro friction)
        el.setAttribute('data-status', 'hidden');
        return;
      }
      const soutenirUrl = r.soutenir_url || '/soutenir.html';
      if (r.ux_status === 'aperçu') {
        const remaining = r.preview_remaining ?? 0;
        const remainTxt = remaining === 0
          ? 'Dernière réponse en qualité Opus'
          : remaining === 1
            ? '<strong>1 question</strong> Opus offerte restante'
            : `<strong>${remaining} questions</strong> Opus offertes restantes`;
        el.setAttribute('data-status', 'aperçu');
        el.innerHTML = `
          <span class="daat-status-banner-icon">✨</span>
          <span class="daat-status-banner-text">Aperçu Premium · ${remainTxt}</span>
          <button class="daat-status-banner-cta" data-action="open-soutenir">Soutenir →</button>
        `;
      } else if (r.ux_status === 'premium') {
        const planLabels = {
          khavroutha: '📚 Khavroutha',
          beit_midrash: '🕯️ Beit Midrash',
          beit_midrash_plus: '🕯️ Beit Midrash+',
          yeshiva: '🎓 Yeshiva',
          lifetime: '✨ Lifetime',
          premium: '💎 Premium',
        };
        const label = planLabels[r.plan] || r.plan;
        const mr = r.month_remaining;
        const remain = (r.month_limit && r.month_limit < 9999 && typeof mr === 'number')
          ? `${mr} question${mr > 1 ? 's' : ''} ce mois-ci` : 'qualité Opus active';
        el.setAttribute('data-status', 'premium');
        el.innerHTML = `
          <span class="daat-status-banner-icon">${label.split(' ')[0]}</span>
          <span class="daat-status-banner-text">${label.split(' ').slice(1).join(' ')} · ${remain}</span>
        `;
      } else {
        // Standard : free/anonyme après Aperçu épuisé — jauge MENSUELLE
        const remain = r.month_remaining ?? 0;
        el.setAttribute('data-status', 'standard');
        el.innerHTML = `
          <span class="daat-status-banner-icon">📜</span>
          <span class="daat-status-banner-text"><strong>${remain}</strong> question${remain > 1 ? 's' : ''} IA ce mois-ci · le corpus reste illimité</span>
          <button class="daat-status-banner-cta" data-action="open-soutenir">Soutenir DAAT →</button>
        `;
      }
      // Bind CTA(s)
      el.querySelectorAll('[data-action="open-soutenir"]').forEach(btn => {
        btn.addEventListener('click', () => window.open(soutenirUrl, '_blank', 'noopener'));
      });
    }

    // ─── Badge modèle en haut de la bulle assistant ───
    addModelBadge(assistantEl, provider) {
      const r = this.rateInfo;
      if (!r || !assistantEl) return;
      // Pas de badge sur les méta (Haiku/DeepSeek)
      if (r.ux_status === 'meta') return;
      let badge = null;
      // ⚠️ Tester le PRÉFIXE, pas l'égalité : le serveur émet 'corpus-haiku'
      // (reformulée), 'corpus-cache' (déjà reformulée, resservie) et 'corpus-raw'
      // (extrait brut, aucun modèle appelé). Ne reconnaître que 'corpus-haiku'
      // faisait retomber les deux autres sur la branche suivante — une réponse
      // du corpus s'affichait alors « ✨ APERÇU OPUS ». C'est exactement le
      // mauvais étiquetage déjà corrigé une fois (PR #161).
      if (typeof provider === 'string' && provider.startsWith('corpus')) {
        badge = document.createElement('span');
        badge.className = 'daat-msg-badge is-corpus';
        if (provider === 'corpus-raw') {
          badge.textContent = '📜 TEXTE DU RAV';
          badge.title = "Extrait du corpus servi tel quel — aucune reformulation par l'IA";
        } else {
          badge.textContent = '📚 CORPUS DU RAV';
          badge.title = 'Réponse tirée directement du corpus écrit par le Rav';
        }
      } else if (r.is_aperçu) {
        badge = document.createElement('span');
        badge.className = 'daat-msg-badge is-aperçu';
        badge.textContent = '✨ APERÇU OPUS';
        badge.title = `Réponse en qualité Opus (offerte) — il te reste ${r.preview_remaining} question(s) Opus offerte(s)`;
      } else if (r.is_subscriber && r.model_tier === 'opus') {
        badge = document.createElement('span');
        badge.className = 'daat-msg-badge is-opus';
        badge.textContent = '🕯️ OPUS';
        badge.title = 'Réponse en qualité Opus (grâce à ton soutien)';
      } else if (r.would_use_opus) {
        badge = document.createElement('span');
        badge.className = 'daat-msg-badge is-sonnet-hint';
        badge.textContent = '→ AURAIT ÉTÉ OPUS EN SOUTIEN';
        badge.title = 'Cette réponse aurait été en qualité Opus si tu soutenais DAAT — clique pour découvrir';
        badge.addEventListener('click', () => {
          window.open(r.soutenir_url || '/soutenir.html', '_blank', 'noopener');
        });
      }
      if (badge) {
        assistantEl.insertBefore(badge, assistantEl.firstChild);
        // saut de ligne après le badge pour que le markdown commence à la ligne
        const br = document.createElement('br');
        assistantEl.insertBefore(br, badge.nextSibling);
      }
    }

    // ─── Paywall modal (limite atteinte OU transition Aperçu→Standard) ───
    showPaywallModal({ reason, info }) {
      const r = this.rateInfo || {};
      const soutenirUrl = (info && info.soutenir_url) || r.soutenir_url || '/soutenir.html';
      const overlay = document.createElement('div');
      overlay.className = 'daat-paywall-overlay';
      let title, eyebrow, body, primaryLabel, secondaryLabel, ghostLabel;
      if (reason === 'transition') {
        // Q3 → Q4 : on vient de servir la dernière Aperçu Opus.
        eyebrow = '✨ APERÇU PREMIUM TERMINÉ';
        title = 'Tu as goûté à la qualité Opus.';
        body = `
          <p>Tu viens d'utiliser tes <strong>3 questions Opus offertes</strong>. À partir de maintenant, tes réponses seront en qualité Sonnet — toujours sérieuses, mais sans la profondeur analytique de l'Opus.</p>
          <p>DAAT est gratuit et le restera. Si tu veux garder l'Opus en continu et soutenir l'accès gratuit pour d'autres talmidim, tu peux rejoindre une Khavroutha.</p>
        `;
        primaryLabel = 'Découvrir les soutiens';
        secondaryLabel = null;
        ghostLabel = 'Continuer en Sonnet';
      } else if (reason === 'anthropic_exhausted') {
        // QUOTA ANTHROPIC ÉPUISÉ — le budget mensuel global est terminé,
        // le chat est en pause pour TOUS les utilisateurs jusqu'au prochain soutien.
        eyebrow = '🛑 LE CHAT EST EN PAUSE';
        title = "DAAT n'a plus de tokens pour répondre.";
        body = `
          <p style="font-size:15px;line-height:1.65;margin-bottom:12px;">
            <strong>L'IA Daat fonctionne grâce aux dons de la communauté.</strong>
            Notre budget mensuel est épuisé — le chat est donc <strong>temporairement à l'arrêt</strong>.
          </p>
          <p style="font-size:15px;line-height:1.65;margin-bottom:12px;">
            Sans nouveaux soutiens, le projet ne peut pas continuer.
            <strong>Ta participation, même modeste, permet de réactiver le chat</strong>
            et de poursuivre la diffusion de la Torah pour tous.
          </p>
          <p style="font-size:13.5px;line-height:1.55;color:#5a4e3d;background:rgba(184,151,42,0.10);border-left:3px solid #B8972A;padding:10px 12px;margin:14px 0 8px;">
            ⏱️ Un léger délai peut s'écouler entre ta participation et la réactivation du chat.
          </p>
          <p style="font-size:13px;color:#8a847b;font-style:italic;margin-top:14px;">
            Reçu fiscal 66 % déductible · Association loi 1901
          </p>
        `;
        primaryLabel = '❤️ Soutenir pour réactiver le chat';
        secondaryLabel = null;
        ghostLabel = null; // Pas d'échappatoire facile — l'utilisateur doit comprendre
      } else if (reason === 'limit') {
        // 429 — limite quotidienne ou mensuelle atteinte
        // 'monthly_ip' (plafond par adresse) est aussi une limite MENSUELLE : sans
        // cette reconnaissance, l'interface retombait sur le message QUOTIDIEN
        // (« reviens demain ») et le message serveur n'était jamais affiché.
        const isMonthly = info && (info.scope === 'monthly' || info.scope === 'monthly_ip');
        const limit = info?.limit ?? '?';
        const plan = info?.plan || r.plan || 'free';
        const isGuest = info?.is_guest;
        eyebrow = isMonthly ? 'QUOTA MENSUEL ATTEINT' : 'LIMITE QUOTIDIENNE ATTEINTE';
        title = isMonthly
          ? `Tu as utilisé tes ${limit} questions ce mois.`
          : isGuest
            ? `Tu as utilisé tes ${limit} questions du jour.`
            : `Tu as posé ${limit} questions aujourd'hui.`;
        body = `
          <p>${isGuest
            ? 'Connecte-toi avec ton email pour <strong>10 questions IA/mois</strong> et 3 questions Opus offertes en bienvenue.'
            : 'Reviens demain pour de nouvelles questions, ou soutiens DAAT pour débloquer immédiatement l\'<strong>accès Opus</strong> — l\'analyse halakhique approfondie.'}</p>
          <p style="font-size:12.5px;color:#8a847b;">Les questions couvertes par le corpus du Rav restent <strong>gratuites et illimitées</strong>.</p>
          ${isMonthly ? '<p style="font-size:12px;color:#8a847b;">Le quota mensuel protège l\'asso contre les usages excessifs et garantit que DAAT reste accessible à tous.</p>' : ''}
        `;
        primaryLabel = 'Soutenir DAAT';
        secondaryLabel = isGuest ? 'Créer un compte gratuit' : null;
        ghostLabel = 'Fermer';
      }
      overlay.innerHTML = `
        <div class="daat-paywall" role="dialog" aria-modal="true">
          <div class="daat-paywall-eyebrow">${eyebrow}</div>
          <h3 class="daat-paywall-title">${title}</h3>
          <div class="daat-paywall-body">${body}</div>
          <div class="daat-paywall-actions">
            <button class="daat-paywall-btn is-primary" data-act="primary">${primaryLabel}</button>
            ${secondaryLabel ? `<button class="daat-paywall-btn" data-act="secondary">${secondaryLabel}</button>` : ''}
            ${ghostLabel ? `<button class="daat-paywall-btn is-ghost" data-act="ghost">${ghostLabel}</button>` : ''}
          </div>
        </div>
      `;
      this.panel.appendChild(overlay);
      const close = () => overlay.remove();
      overlay.querySelector('[data-act="primary"]').addEventListener('click', () => {
        window.open(soutenirUrl, '_blank', 'noopener');
        close();
      });
      const sec = overlay.querySelector('[data-act="secondary"]');
      if (sec) sec.addEventListener('click', () => { close(); /* Le bouton login est ailleurs */ });
      const ghost = overlay.querySelector('[data-act="ghost"]');
      if (ghost) ghost.addEventListener('click', close);
      overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    }

    appendError(text) {
      const el = document.createElement('div');
      el.className = 'daat-chat-message is-error';
      el.textContent = text;
      this.messagesEl.appendChild(el);
      this.scrollToBottom();
    }

    appendToolNotice(text) {
      const el = document.createElement('div');
      el.className = 'daat-chat-tool-notice';
      el.textContent = text;
      this.messagesEl.appendChild(el);
      this.scrollToBottom();
    }

    showTyping() {
      const el = document.createElement('div');
      el.className = 'daat-chat-typing';
      el.innerHTML = '<span></span><span></span><span></span>';
      this.messagesEl.appendChild(el);
      this.scrollToBottom();
      return el;
    }

    scrollToBottom(force) {
      // Si l'utilisateur a scrollé vers le haut manuellement, on ne touche pas à sa position
      // sauf si force=true (nouveau message envoyé, ouverture du panel)
      if (!force && this.userScrolledUp) {
        if (this.scrollDownBtn) this.scrollDownBtn.classList.add('is-visible');
        return;
      }
      requestAnimationFrame(() => {
        const el = this.messagesEl;
        if (!el) return;
        el.scrollTop = el.scrollHeight;
        this.userScrolledUp = false;
        if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');
      });
    }

    setStreaming(streaming) {
      this.isStreaming = streaming;
      this.inputEl.disabled = streaming;
      this.sendBtn.disabled = streaming;
    }

    async send() {
      let text = this.inputEl.value.trim();
      if (!text || this.isStreaming) return;

      // Nouveau message → on reset le tracking de scroll et on revient en bas
      this.userScrolledUp = false;
      if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');

      // Welcome screen → first message
      if (this.messages.length === 0) {
        // L'utilisateur doit avoir choisi niveau + minhag avant d'envoyer
        if (!this.selectedNiveau || !this.selectedMinhag) {
          alert('Choisis d\'abord ton niveau et ton minhag.');
          return;
        }
        this.messagesEl.innerHTML = '';
        // Génère un nouvel id de conversation
        if (!this.currentConvId) this.currentConvId = newConversationId();

        const niveauTxt = NIVEAU_LABELS[this.selectedNiveau] || this.selectedNiveau;
        const minhagTxt = MINHAG_LABELS[this.selectedMinhag] || this.selectedMinhag;
        const langTxt = LANG_LABELS[getLang()] || 'français';
        if (!/•\s*Niveau/i.test(text)) {
          text =
            `[Profil de cette session]\n` +
            `• Niveau : ${niveauTxt}\n` +
            `• Minhag : ${minhagTxt}\n` +
            `• Langue de réponse souhaitée : ${langTxt}\n` +
            simanContextLine() +
            `\n[Ma question]\n${text}`;
        }
      }

      // Add user message
      this.messages.push({ role: 'user', content: text });
      this.appendMessage('user', text);
      this.scrollToBottom(true);
      this.inputEl.value = '';
      this.inputEl.style.height = 'auto';
      this.persistConversation();

      // Show typing indicator
      const typingEl = this.showTyping();
      this.setStreaming(true);

      try {
        const chatSection = (document.querySelector('meta[name="daat-section"]') || {}).content || 'orach-chaim';
        const vaCtx = detectSimanContext();
        vaTrack('chat_question_sent', vaCtx ? { section: chatSection, siman: vaCtx.siman } : { section: chatSection });
        const response = await fetch(API_URL, {
          method: 'POST',
          // credentials:'include' est INDISPENSABLE : le widget est embarqué sur
          // daattorah.com mais l'API est sur daatai.vercel.app (cross-site). Sans ça
          // le cookie daat_session (JWT) n'est jamais envoyé → l'utilisateur connecté
          // (et payant) est vu comme anonyme et ne reçoit pas Opus.
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: this.messages, section: chatSection }),
        });

        if (!response.ok) {
          let errMsg = 'Erreur ' + response.status;
          let errJson = null;
          try {
            errJson = await response.json();
            errMsg = errJson.error || errMsg;
          } catch (_) {}
          // 429 = limite quotidienne/mensuelle atteinte → paywall plutôt qu'erreur
          if (response.status === 429 && errJson && errJson.type === 'limit_reached') {
            const limitErr = new Error(errJson.message || errMsg);
            limitErr._isLimitReached = true;
            limitErr._info = errJson;
            throw limitErr;
          }
          throw new Error(errMsg);
        }

        // On GARDE l'indicateur « ... » (3 points animés) tant que le premier mot
        // n'est pas arrivé : pendant que l'IA réfléchit / consulte les sources
        // (Opus + outils = parfois plusieurs dizaines de secondes), les points
        // continuent de bouger pour montrer qu'une réponse arrive. La bulle de
        // réponse n'est créée qu'au tout premier token de texte.
        let assistantEl = null;
        let assistantText = '';
        let responseProvider = null; // renseigné par l'event 'done' (ex: 'corpus-haiku')
        const ensureBubble = () => {
          if (!assistantEl) {
            if (typingEl.parentNode) typingEl.remove();
            assistantEl = this.appendMessage('assistant', '');
          }
          return assistantEl;
        };
        // Garde les 3 points TOUJOURS en bas (après un notice d'outil) = « je continue ».
        const keepTypingLast = () => {
          if (typingEl.parentNode) { this.messagesEl.appendChild(typingEl); this.scrollToBottom(); }
        };

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events
          const events = buffer.split('\n\n');
          buffer = events.pop() || ''; // keep incomplete last chunk

          for (const evt of events) {
            const line = evt.trim();
            if (!line.startsWith('data:')) continue;
            const data = line.slice(5).trim();
            if (!data) continue;

            try {
              const parsed = JSON.parse(data);
              if (parsed.type === 'rate_info') {
                // Détection Q3 → Q4 : avant ce message, l'user avait 1 Aperçu restant
                // (so it was his Q3 Aperçu). Après → 0 restant. On affichera la modale
                // de transition à la fin du streaming pour ne pas casser l'expérience.
                if (
                  this.previousAperçuRemaining === 1 &&
                  parsed.preview_remaining === 0 &&
                  parsed.is_aperçu === true
                ) {
                  this.pendingTransitionModal = true;
                }
                this.previousAperçuRemaining = parsed.preview_remaining;
                this.rateInfo = parsed;
                this.updateStatusBanner();
              } else if (parsed.type === 'text' && parsed.delta) {
                ensureBubble(); // 1er token : retire les points, crée la bulle
                assistantText += parsed.delta;
                assistantEl.setAttribute('dir', detectMessageDir(assistantText));
                assistantEl.innerHTML = renderMarkdown(assistantText);
                this.scrollToBottom();
              } else if (parsed.type === 'tool_use') {
                // Afficher discrètement la consultation (corpus DAAT ou Sefaria)
                const toolLabels = {
                  daat_search_corpus: `📚 Recherche dans le corpus DAAT : « ${parsed.input?.query || ''} »`,
                  daat_get_content: `📖 Lecture du corpus DAAT : ${parsed.input?.id || ''}`,
                  sefaria_get_text: `📜 Vérification dans Sefaria : ${parsed.input?.ref || ''}`,
                  sefaria_search: `🔍 Recherche dans Sefaria : « ${parsed.input?.query || ''} »`,
                };
                const toolLabel = toolLabels[parsed.tool] || `🔧 ${parsed.tool}`;
                this.appendToolNotice(toolLabel);
                keepTypingLast(); // les points restent sous le notice = « je travaille »
              } else if (parsed.type === 'notice') {
                this.appendToolNotice('⏳ ' + parsed.message);
                keepTypingLast();
              } else if (parsed.type === 'limit_reached') {
                // Quota Anthropic épuisé (envoyé via SSE après début du stream)
                if (assistantEl) assistantEl.remove();
                const isAnthropic = parsed.scope === 'anthropic_quota';
                this.showPaywallModal({
                  reason: isAnthropic ? 'anthropic_exhausted' : 'limit',
                  info: parsed,
                });
                if (typingEl.parentNode) typingEl.remove();
                this.setStreaming(false);
                return;
              } else if (parsed.type === 'error') {
                // Filet de sécurité : si erreur contient pattern Anthropic, paywall
                const errStr = String(parsed.error || '');
                if (/API usage limits|credit balance is too low|invalid_request_error/i.test(errStr)) {
                  if (assistantEl) assistantEl.remove();
                  this.showPaywallModal({
                    reason: 'anthropic_exhausted',
                    info: { scope: 'anthropic_quota', soutenir_url: '/soutenir.html?from=chat' },
                  });
                  if (typingEl.parentNode) typingEl.remove();
                  this.setStreaming(false);
                  return;
                }
                throw new Error(parsed.error || 'Erreur de génération');
              } else if (parsed.type === 'done') {
                responseProvider = parsed.provider || null;
                // Corpus-first ayant intercepté un Aperçu : aucune consommation
                // côté serveur → on annule la fausse modale de transition et on
                // restaure le compteur d'Aperçu client (sinon il « saute » à 0).
                if (typeof parsed.provider === 'string' && parsed.provider.startsWith('corpus') && parsed.aperçu_intercepted) {
                  this.pendingTransitionModal = false;
                  if (typeof parsed.preview_remaining === 'number' && this.rateInfo) {
                    this.rateInfo.preview_remaining = parsed.preview_remaining;
                    this.rateInfo.is_aperçu = false;
                    this.previousAperçuRemaining = parsed.preview_remaining;
                    this.updateStatusBanner();
                  }
                }
                if (window.DAAT_CHAT_DEBUG) {
                  console.log('[Daat] Usage:', parsed.usage, 'Iterations:', parsed.iterations, 'Provider:', parsed.provider);
                }
              }
            } catch (e) {
              // JSON parse failure — likely partial chunk, ignore unless real error
              if (e.message && !e.message.includes('JSON')) throw e;
            }
          }
        }

        // Save final assistant message to history
        if (assistantText) {
          this.messages.push({ role: 'assistant', content: assistantText });
          this.persistConversation();
          // Badge modèle (Aperçu / Opus / "aurait été Opus")
          this.addModelBadge(assistantEl, responseProvider);
          // Attach feedback buttons to the assistant message
          this.attachFeedbackBar(assistantEl, assistantText);
          // Modale de transition Aperçu → Standard après Q3 (semer la conversion)
          if (this.pendingTransitionModal) {
            this.pendingTransitionModal = false;
            setTimeout(() => this.showPaywallModal({ reason: 'transition' }), 400);
          }
        } else {
          if (typingEl.parentNode) typingEl.remove();
          if (assistantEl) assistantEl.remove();
          this.appendError('Pas de réponse reçue. Réessaie.');
        }
      } catch (error) {
        console.error('[Daat chat] error:', error);
        if (typingEl.parentNode) typingEl.remove();
        const msg = String(error?.message || error || '');
        // 429 limite quotidienne/mensuelle (notre cap par utilisateur) → paywall limit
        if (error._isLimitReached) {
          this.showPaywallModal({ reason: 'limit', info: error._info });
        }
        // Quota Anthropic global épuisé (pattern dans le message d'erreur) → paywall fort
        else if (/API usage limits|credit balance is too low|invalid_request_error/i.test(msg)) {
          this.showPaywallModal({
            reason: 'anthropic_exhausted',
            info: { scope: 'anthropic_quota', soutenir_url: '/soutenir.html?from=chat' },
          });
        } else {
          this.appendError(error.message || 'Erreur de connexion. Vérifie ta connexion internet.');
        }
        // Remove the user message that failed (so they can retry without duplicates)
        // Actually keep it — let them edit and retry
      } finally {
        this.setStreaming(false);
        this.inputEl.focus();
      }
    }
  }

  // === AUTO-INIT ===
  function init() {
    if (window.daatChatWidget) return; // already initialized
    window.daatChatWidget = new DaatChatWidget();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
