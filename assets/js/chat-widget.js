// DAAT.AI Chat Widget — Vanilla JS, zéro dépendance
// Usage : inclure le CSS + ce script ; le widget s'initialise automatiquement.

(function () {
  'use strict';

  // === CONFIGURATION ===
  // L'URL de l'API Vercel — à mettre à jour après déploiement
  const API_URL = window.DAAT_CHAT_API_URL || 'https://daat-ai.vercel.app/api/chat';
  const FEEDBACK_URL = (window.DAAT_CHAT_API_URL || 'https://daatai.vercel.app/api/chat').replace(/\/api\/chat\/?$/, '/api/feedback');
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
    s = s.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

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
      const items = block.trim().split('\n').map(line => '<li>' + line.replace(/^[-*] /, '') + '</li>').join('');
      return '<ul>' + items + '</ul>';
    });
    s = s.replace(/(?:^\d+\. .+(?:\n|$))+/gm, function (block) {
      const items = block.trim().split('\n').map(line => '<li>' + line.replace(/^\d+\. /, '') + '</li>').join('');
      return '<ol>' + items + '</ol>';
    });

    // Hebrew text wrapping — isole les passages hébreux en RTL inline.
    // Inclut guillemets ASCII (") et typo + apostrophes pour ne pas casser
    // des abréviations comme אדה"ז, שו"ע, רמב"ם, מג"א, וכו׳, etc.
    s = s.replace(
      /([\u05D0-\u05EA\u05F0-\u05F2](?:[\u0591-\u05F4\u05D0-\u05EA\u05F0-\u05F2\s"'\u2019\u201C\u201D,.\-()]{0,80}[\u05D0-\u05EA\u05F0-\u05F2])?)/g,
      '<span lang="he" dir="rtl" style="unicode-bidi:isolate;">$1</span>'
    );

    // Paragraphs (double newline)
    const paragraphs = s.split(/\n\n+/);
    s = paragraphs.map(p => {
      const trimmed = p.trim();
      if (!trimmed) return '';
      // Skip if already a block-level element
      if (/^<(h[1-6]|ul|ol|pre|blockquote|table)/.test(trimmed)) return trimmed;
      return '<p>' + trimmed.replace(/\n/g, '<br>') + '</p>';
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
    return localStorage.getItem(LANG_KEY) || 'fr';
  }
  function setLang(lang) {
    if (!LANG_LABELS[lang]) lang = 'fr';
    localStorage.setItem(LANG_KEY, lang);
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
      `• Langue de réponse souhaitée : ${langTxt}\n\n` +
      `Je suis prêt à commencer. Adapte tes réponses à ce profil et réponds dans la langue indiquée.`
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
    if (conv.messages) conv.messages = conv.messages.slice(-MAX_MESSAGES_PER_CONV);
    if (idx >= 0) all[idx] = conv;
    else all.unshift(conv);
    saveConversations(all);
  }
  function deleteConversation(id) {
    saveConversations(loadConversations().filter(c => c.id !== id));
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
      this.build();
      this.attach();
      this.renderMessages();             // affiche l'écran d'accueil (vierge)
    }

    build() {
      // Floating button
      this.button = document.createElement('button');
      this.button.className = 'daat-chat-button';
      this.button.setAttribute('aria-label', 'Ouvrir le chat avec Daat');
      this.button.innerHTML =
        '<span class="daat-chat-button-icon">דעת</span>' +
        '<span class="daat-chat-button-pulse"></span>';

      // Panel
      this.panel = document.createElement('div');
      this.panel.className = 'daat-chat-panel';
      this.panel.setAttribute('role', 'dialog');
      this.panel.setAttribute('aria-label', 'Chat avec Daat — assistant Torah');
      this.panel.innerHTML = `
        <div class="daat-chat-header">
          <button class="daat-chat-history-btn" id="daat-chat-history-btn" title="Historique des conversations" aria-label="Historique des conversations">📋</button>
          <div class="daat-chat-header-logo">דעת</div>
          <div class="daat-chat-header-info">
            <div class="daat-chat-header-title">Daat</div>
            <div class="daat-chat-header-subtitle">Assistant d'étude</div>
          </div>
          <button class="daat-chat-reset" id="daat-chat-reset" title="Nouvelle conversation" aria-label="Nouvelle conversation">↺</button>
        </div>
        <div class="daat-chat-messages" id="daat-chat-messages" dir="ltr"></div>
        <div class="daat-chat-history-panel" id="daat-chat-history-panel">
          <div class="daat-chat-history-header">
            <span>Historique des conversations</span>
            <button class="daat-chat-history-close" id="daat-chat-history-close" aria-label="Fermer">✕</button>
          </div>
          <button class="daat-chat-history-new" id="daat-chat-history-new">＋ Nouvelle conversation</button>
          <div class="daat-chat-history-list" id="daat-chat-history-list"></div>
        </div>
        <button class="daat-chat-scroll-down" id="daat-chat-scroll-down" type="button" aria-label="Aller au dernier message">↓ Nouveau</button>
        <div class="daat-chat-input-area">
          <div class="daat-chat-input-wrapper">
            <textarea
              class="daat-chat-input"
              id="daat-chat-input"
              placeholder="Pose ta question..."
              rows="1"
              aria-label="Votre message"
            ></textarea>
            <button class="daat-chat-send" id="daat-chat-send" aria-label="Envoyer">→</button>
          </div>
          <div class="daat-chat-footer">Daat peut faire des erreurs. Vérifie auprès de ton Rav.</div>
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
      this.userScrolledUp = false;
    }

    attach() {
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

      // Track manual scrolling — si l'utilisateur remonte, on désactive l'auto-scroll
      this.messagesEl.addEventListener('scroll', () => {
        const el = this.messagesEl;
        const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
        const isAtBottom = distanceFromBottom < 30;
        this.userScrolledUp = !isAtBottom;
        if (this.scrollDownBtn) {
          this.scrollDownBtn.classList.toggle('is-visible', this.userScrolledUp && this.isStreaming);
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
            <h3>Bienvenue !</h3>
            <p>Je suis <strong>Daat</strong>, ton assistant d'étude pour la Torah et la Halakha.</p>

            <div class="daat-chat-step">
              <div class="daat-chat-step-label">① Quel est ton niveau d'étude ?</div>
              <div class="daat-chat-chips" data-group="niveau">
                <button class="daat-chat-chip" data-value="debutant">🌱 Débutant</button>
                <button class="daat-chat-chip" data-value="intermediaire">📚 Bagage moyen</button>
                <button class="daat-chat-chip" data-value="yeshiva">🕮 Élève de Yeshiva</button>
                <button class="daat-chat-chip" data-value="lamdan">🎓 Talmid Hakham</button>
              </div>
            </div>

            <div class="daat-chat-step">
              <div class="daat-chat-step-label">② Quel est ton minhag ?</div>
              <div class="daat-chat-chips" data-group="minhag">
                <button class="daat-chat-chip" data-value="sefarade">🕎 Séfarade</button>
                <button class="daat-chat-chip" data-value="ashkenaze">❄️ Ashkénaze</button>
                <button class="daat-chat-chip" data-value="habad">🔵 Habad / Loubavitch</button>
                <button class="daat-chat-chip" data-value="autre">🤷 Autre / pas sûr</button>
              </div>
            </div>

            <div class="daat-chat-step">
              <div class="daat-chat-step-label">③ Langue de réponse</div>
              <div class="daat-chat-chips" data-group="lang">
                <button class="daat-chat-chip" data-value="fr">🇫🇷 Français</button>
                <button class="daat-chat-chip" data-value="he" style="font-family:'Frank Ruhl Libre',serif;">עברית</button>
                <button class="daat-chat-chip" data-value="en">🇬🇧 English</button>
              </div>
            </div>

            <button class="daat-chat-start" id="daat-chat-start" disabled>✓ Commencer l'étude</button>
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
      // Force LTR for all messages — le français s'affiche de gauche à droite,
      // les passages hébreux sont wrappés en <span dir="rtl"> par renderMarkdown
      el.setAttribute('dir', 'ltr');
      el.style.textAlign = 'left';
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
      const bar = document.createElement('div');
      bar.className = 'daat-chat-feedback';
      bar.innerHTML = `
        <span class="daat-chat-feedback-label">Cette réponse :</span>
        <button class="daat-chat-fb-btn daat-chat-fb-up" title="Utile">👍</button>
        <button class="daat-chat-fb-btn daat-chat-fb-down" title="À corriger">👎</button>
        <span class="daat-chat-feedback-thanks" style="display:none;"></span>
      `;
      assistantEl.appendChild(bar);
      const widget = this;
      bar.querySelector('.daat-chat-fb-up').addEventListener('click', () => {
        widget.sendFeedback('👍', bar, lastUserContent, answerText);
      });
      bar.querySelector('.daat-chat-fb-down').addEventListener('click', () => {
        widget.askDownComment(assistantEl, bar, lastUserContent, answerText);
      });
    }

    askDownComment(assistantEl, bar, question, answer) {
      bar.querySelector('.daat-chat-fb-down').classList.add('is-selected');
      bar.querySelectorAll('.daat-chat-fb-btn').forEach(b => b.disabled = true);
      if (assistantEl.querySelector('.daat-chat-fb-comment')) return;
      const ta = document.createElement('textarea');
      ta.className = 'daat-chat-fb-comment';
      ta.placeholder = 'Optionnel : pourquoi ? (incorrect, source manquante…)';
      const actions = document.createElement('div');
      actions.className = 'daat-chat-fb-comment-actions';
      actions.innerHTML = `
        <button class="daat-chat-fb-send">Envoyer</button>
        <button class="daat-chat-fb-skip">Sans commentaire</button>
      `;
      assistantEl.appendChild(ta);
      assistantEl.appendChild(actions);
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
      // Respecte la position de l'utilisateur : si il a remonté le chat
      // pour lire pendant que le streaming continue, on NE le ramène PAS
      // automatiquement en bas. Il faut soit envoyer un nouveau message,
      // soit cliquer le bouton "↓" qui s'affiche, soit scroller manuellement.
      requestAnimationFrame(() => {
        const el = this.messagesEl;
        if (!el) return;
        const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
        if (force || distanceFromBottom < 80) {
          el.scrollTop = el.scrollHeight;
          this.userScrolledUp = false;
          if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');
        } else {
          // L'utilisateur lit en remontant — on signale juste qu'il y a du nouveau
          this.userScrolledUp = true;
          if (this.scrollDownBtn) this.scrollDownBtn.classList.add('is-visible');
        }
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
            `• Langue de réponse souhaitée : ${langTxt}\n\n` +
            `[Ma question]\n${text}`;
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
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: this.messages }),
        });

        if (!response.ok) {
          let errMsg = 'Erreur ' + response.status;
          try {
            const errJson = await response.json();
            errMsg = errJson.error || errMsg;
          } catch (_) {}
          throw new Error(errMsg);
        }

        // Remove typing indicator, prepare assistant message bubble
        typingEl.remove();
        const assistantEl = this.appendMessage('assistant', '');
        let assistantText = '';

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
              if (parsed.type === 'text' && parsed.delta) {
                assistantText += parsed.delta;
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
              } else if (parsed.type === 'notice') {
                this.appendToolNotice('⏳ ' + parsed.message);
              } else if (parsed.type === 'error') {
                throw new Error(parsed.error || 'Erreur de génération');
              } else if (parsed.type === 'done') {
                if (window.DAAT_CHAT_DEBUG) {
                  console.log('[Daat] Usage:', parsed.usage, 'Iterations:', parsed.iterations);
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
          // Attach feedback buttons to the assistant message
          this.attachFeedbackBar(assistantEl, assistantText);
        } else {
          assistantEl.remove();
          this.appendError('Pas de réponse reçue. Réessaie.');
        }
      } catch (error) {
        console.error('[Daat chat] error:', error);
        if (typingEl.parentNode) typingEl.remove();
        this.appendError(error.message || 'Erreur de connexion. Vérifie ta connexion internet.');
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
