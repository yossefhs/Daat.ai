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

    // Hebrew text wrapping (sequences of Hebrew chars)
    s = s.replace(/([֐-׿\s֑-ׇ]{2,})/g, '<span lang="he" dir="rtl">$1</span>');

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
        </div>
        <div class="daat-chat-messages" id="daat-chat-messages"></div>
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
    }

    attach() {
      this.button.addEventListener('click', () => this.toggle());

      this.sendBtn.addEventListener('click', () => this.send());

      this.inputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.send();
        }
      });

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
        this.messagesEl.innerHTML = `
          <div class="daat-chat-welcome">
            <span class="heb">דעת</span>
            <h3>Bienvenue !</h3>
            <p>Je suis <strong>Daat</strong>, ton assistant d'étude pour la Torah et la Halakha.</p>
            <p>Pose-moi une question — sur le Choulchan Aroukh, le Talmud, un concept halakhique...</p>
            <div class="daat-chat-suggestions">
              <button class="daat-chat-suggestion" data-q="Explique-moi le Siman 246 Seif Alef">
                📖 Explique-moi le Siman 246 Seif Alef
              </button>
              <button class="daat-chat-suggestion" data-q="C'est quoi שביתת כלים ?">
                🤔 C'est quoi שביתת כלים ?
               </button>
              <button class="daat-chat-suggestion" data-q="Quelle est la différence entre prêter et louer un objet à un non-juif pour Shabbat ?">
                ⚖️ Prêter vs louer à un non-juif pour Shabbat ?
              </button>
            </div>
            <div class="signature">דעת התורה לעומקה</div>
          </div>
        `;
        // Suggestion buttons
        this.messagesEl.querySelectorAll('.daat-chat-suggestion').forEach(btn => {
          btn.addEventListener('click', () => {
            this.inputEl.value = btn.dataset.q;
            this.send();
          });
        });
        return;
      }

      this.messagesEl.innerHTML = '';
      this.messages.forEach(m => this.appendMessage(m.role, m.content));
    }

    appendMessage(role, content) {
      const el = document.createElement('div');
      el.className = 'daat-chat-message is-' + role;
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

    showTyping() {
      const el = document.createElement('div');
      el.className = 'daat-chat-typing';
      el.innerHTML = '<span></span><span></span><span></span>';
      this.messagesEl.appendChild(el);
      this.scrollToBottom();
      return el;
    }

    scrollToBottom() {
      requestAnimationFrame(() => {
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
      });
    }

    setStreaming(streaming) {
      this.isStreaming = streaming;
      this.inputEl.disabled = streaming;
      this.sendBtn.disabled = streaming;
    }

    async send() {
      const text = this.inputEl.value.trim();
      if (!text || this.isStreaming) return;

      // Welcome screen → first message
      if (this.messages.length === 0) {
        this.messagesEl.innerHTML = '';
      }

      // Add user message
      this.messages.push({ role: 'user', content: text });
      this.appendMessage('user', text);
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
              } else if (parsed.type === 'error') {
                throw new Error(parsed.error || 'Erreur de génération');
              } else if (parsed.type === 'done') {
                // Optional: log usage info
                if (window.DAAT_CHAT_DEBUG) {
                  console.log('[Daat] Usage:', parsed.usage);
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
