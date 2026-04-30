// DAAT.AI Chat Widget — Vanilla JS, zéro dépendance
// Usage : inclure le CSS + ce script ; le widget s'initialise automatiquement.

(function () {
  'use strict';

  // === CONFIGURATION ===
  // L'URL de l'API Vercel — à mettre à jour après déploiement
  const API_URL = window.DAAT_CHAT_API_URL || 'https://daat-ai.vercel.app/api/chat';
  const STORAGE_KEY = 'daat-chat-history-v1';
  const MAX_HISTORY = 24; // tours max gardés en mémoire

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

  function buildIntroMessage(niveau, minhag) {
    const niveauTxt = NIVEAU_LABELS[niveau] || niveau;
    const minhagTxt = MINHAG_LABELS[minhag] || minhag;
    return (
      `Bonjour Daat ! Voici mon profil pour cette session :\n` +
      `• Niveau : ${niveauTxt}\n` +
      `• Minhag : ${minhagTxt}\n\n` +
      `Je suis prêt à commencer. Adapte tes réponses à ce profil.`
    );
  }

  // === STATE MANAGEMENT ===
  function loadHistory() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed.slice(-MAX_HISTORY) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(messages) {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_HISTORY)));
    } catch (e) {
      // Ignore (sessionStorage full or unavailable)
    }
  }

  // === WIDGET ===
  class DaatChatWidget {
    constructor() {
      this.messages = loadHistory();
      this.isOpen = false;
      this.isStreaming = false;
      this.build();
      this.attach();
      this.renderMessages();
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
          <div class="daat-chat-header-logo">דעת</div>
          <div class="daat-chat-header-info">
            <div class="daat-chat-header-title">Daat</div>
            <div class="daat-chat-header-subtitle">Assistant d'étude · Rav Yossef Haim Samama</div>
          </div>
          <button class="daat-chat-reset" id="daat-chat-reset" title="Nouvelle conversation" aria-label="Nouvelle conversation">↺</button>
        </div>
        <div class="daat-chat-messages" id="daat-chat-messages" dir="ltr"></div>
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
      this.userScrolledUp = false;
    }

    attach() {
      this.button.addEventListener('click', () => this.toggle());

      // Bouton reset — remet à zéro la conversation
      if (this.resetBtn) {
        this.resetBtn.addEventListener('click', () => this.resetChat());
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
        setTimeout(() => this.inputEl.focus(), 250);
        this.scrollToBottom();
      }
    }

    renderMessages() {
      if (this.messages.length === 0) {
        // Restaurer choix précédents si l'utilisateur revient
        const savedNiveau = sessionStorage.getItem('daat-niveau');
        const savedMinhag = sessionStorage.getItem('daat-minhag');
        this.selectedNiveau = savedNiveau || null;
        this.selectedMinhag = savedMinhag || null;

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
                <button class="daat-chat-chip" data-value="marocain">🇲🇦 Marocain</button>
                <button class="daat-chat-chip" data-value="yemenite">🌴 Yéménite (Téimani)</button>
                <button class="daat-chat-chip" data-value="edot-hamizrah">🌅 Edot HaMizrah</button>
                <button class="daat-chat-chip" data-value="ashkenaze">❄️ Ashkénaze</button>
                <button class="daat-chat-chip" data-value="habad">🔵 Habad / Loubavitch</button>
                <button class="daat-chat-chip" data-value="litvak">📖 Litvak</button>
                <button class="daat-chat-chip" data-value="autre">🤷 Autre / pas sûr</button>
              </div>
            </div>

            <button class="daat-chat-start" id="daat-chat-start" disabled>✓ Commencer l'étude</button>

            <p style="font-size: 0.85em; color: var(--daat-text-muted); margin-top: 16px;">
              💡 Tu peux me parler en <strong>français</strong>, <strong>hébreu</strong>, <strong>anglais</strong> ou <strong>espagnol</strong>.
            </p>
            <div class="signature">דעת התורה לעומקה</div>
          </div>
        `;

        // Hydrater les chips déjà sélectionnés
        if (this.selectedNiveau) {
          const b = this.messagesEl.querySelector(`.daat-chat-chip[data-value="${this.selectedNiveau}"]`);
          if (b) b.classList.add('is-selected');
        }
        if (this.selectedMinhag) {
          const b = this.messagesEl.querySelector(`.daat-chat-chip[data-value="${this.selectedMinhag}"]`);
          if (b) b.classList.add('is-selected');
        }

        const updateStartBtn = () => {
          const btn = this.messagesEl.querySelector('#daat-chat-start');
          if (btn) btn.disabled = !(this.selectedNiveau && this.selectedMinhag);
        };
        updateStartBtn();

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
              sessionStorage.setItem('daat-' + groupName, val);
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

    resetChat() {
      if (this.isStreaming) return; // Ne pas couper en plein stream
      // Effacer l'historique et les préférences
      sessionStorage.removeItem(STORAGE_KEY);
      sessionStorage.removeItem('daat-niveau');
      sessionStorage.removeItem('daat-minhag');
      this.messages = [];
      this.selectedNiveau = null;
      this.selectedMinhag = null;
      this.userScrolledUp = false;
      if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');
      // Revenir à l'écran de bienvenue
      this.renderMessages();
    }

    async send() {
      let text = this.inputEl.value.trim();
      if (!text || this.isStreaming) return;

      // Nouveau message → on reset le tracking de scroll et on revient en bas
      this.userScrolledUp = false;
      if (this.scrollDownBtn) this.scrollDownBtn.classList.remove('is-visible');

      // Welcome screen → first message
      if (this.messages.length === 0) {
        this.messagesEl.innerHTML = '';

        // Si l'utilisateur a sélectionné niveau + minhag dans les chips
        // mais a tapé directement sa question (sans cliquer "Commencer"),
        // on préfixe le profil pour que Daat le reçoive.
        const niveau = this.selectedNiveau || sessionStorage.getItem('daat-niveau');
        const minhag = this.selectedMinhag || sessionStorage.getItem('daat-minhag');
        if (niveau && minhag) {
          const niveauTxt = NIVEAU_LABELS[niveau] || niveau;
          const minhagTxt = MINHAG_LABELS[minhag] || minhag;
          // Détection : si le message ne contient pas déjà le profil, on l'ajoute
          if (!/•\s*Niveau/i.test(text)) {
            text =
              `[Profil de cette session]\n` +
              `• Niveau : ${niveauTxt}\n` +
              `• Minhag : ${minhagTxt}\n\n` +
              `[Ma question]\n${text}`;
          }
        }
      }

      // Add user message
      this.messages.push({ role: 'user', content: text });
      this.appendMessage('user', text);
      this.scrollToBottom(true); // force le scroll au moment d'envoyer
      this.inputEl.value = '';
      this.inputEl.style.height = 'auto';
      saveHistory(this.messages);

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
          saveHistory(this.messages);
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
