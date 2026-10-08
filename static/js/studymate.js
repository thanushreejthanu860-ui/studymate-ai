/**
 * studymate.js — StudyMate AI chat panel
 *
 * Reads quiz context (wrong answers, weak topics) from a hidden
 * #chat-context-data element injected by the Flask home route,
 * then sends them along with every message so the AI can give
 * personalised answers about the student's quiz mistakes.
 */
(function () {
  'use strict';

  // ── DOM refs ──────────────────────────────────────────────────────────────
  const fab      = document.getElementById('chat-fab');
  const panel    = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const clearBtn = document.getElementById('chat-clear');
  const msgBox   = document.getElementById('chat-messages');
  const input    = document.getElementById('chat-input');
  const sendBtn  = document.getElementById('chat-send');
  const typing   = document.getElementById('chat-typing');
  const suggsBox = document.getElementById('chat-suggestions');

  // Guard: if the chatbot HTML isn't on this page, do nothing
  if (!fab || !panel) return;

  // ── Read quiz context injected by Flask ───────────────────────────────────
  const ctxEl       = document.getElementById('chat-context-data');
  const wrongAnswers = ctxEl ? JSON.parse(ctxEl.dataset.wrong || '[]') : [];
  const weakTopics   = ctxEl ? JSON.parse(ctxEl.dataset.weak  || '[]') : [];

  // ── Conversation history (kept in memory, cleared on page reload) ─────────
  let history = [];

  // ── Open / close panel ────────────────────────────────────────────────────
  fab.addEventListener('click', () => {
    const isOpen = panel.classList.toggle('open');
    fab.classList.toggle('active', isOpen);
    if (isOpen) {
      input.focus();
      scrollBottom();
    }
  });

  closeBtn.addEventListener('click', closePanelFn);

  // Close when clicking outside the panel
  document.addEventListener('click', e => {
    if (panel.classList.contains('open') &&
        !panel.contains(e.target) &&
        !fab.contains(e.target)) {
      closePanelFn();
    }
  });

  // ── Clear chat ────────────────────────────────────────────────────────────
  clearBtn.addEventListener('click', () => {
    msgBox.querySelectorAll('.chat-msg:not(#chat-welcome)').forEach(el => el.remove());
    if (suggsBox) suggsBox.style.display = 'flex';
    history = [];
    input.focus();
  });

  // ── Suggestion chips ──────────────────────────────────────────────────────
  document.querySelectorAll('.chat-suggestion').forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.dataset.msg || btn.textContent.trim();
      sendMessage(msg);
    });
  });

  // ── Send on button click ──────────────────────────────────────────────────
  sendBtn.addEventListener('click', () => sendMessage(input.value));

  // Send on Enter (Shift+Enter inserts a newline)
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input.value);
    }
  });

  // Auto-grow textarea up to 120 px
  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });

  // ── Core send function ────────────────────────────────────────────────────
  function sendMessage(text) {
    text = text.trim();
    if (!text) return;
    if (suggsBox) suggsBox.style.display = 'none';
    appendBubble('user', text);
    history.push({ role: 'user', text });
    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;
    showTyping(true);
    scrollBottom();

    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        history: history.slice(0, -1),
        wrong_answers: wrongAnswers,
        weak_topics:   weakTopics
      })
    })
      .then(r => r.json())
      .then(data => {
        showTyping(false);
        sendBtn.disabled = false;
        if (data.error) {
          appendBubble('bot', '⚠️ ' + data.error);
        } else {
          appendBubble('bot', data.reply);
          history.push({ role: 'assistant', text: data.reply });
        }
        scrollBottom();
      })
      .catch(() => {
        showTyping(false);
        sendBtn.disabled = false;
        appendBubble('bot', '⚠️ Could not reach StudyMate AI. Please check your connection and try again.');
        scrollBottom();
      });
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  /** Create and append a chat bubble row */
  function appendBubble(role, text) {
    const row    = document.createElement('div');
    row.className = 'chat-msg ' + role;
    const bubble = document.createElement('span');
    bubble.className = 'chat-bubble';
    bubble.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
    row.appendChild(bubble);
    msgBox.appendChild(row);
  }

  /** Show or hide the typing animation */
  function showTyping(show) {
    typing.style.display = show ? 'flex' : 'none';
    if (show) scrollBottom();
  }

  /** Scroll the message box to the bottom */
  function scrollBottom() {
    msgBox.scrollTop = msgBox.scrollHeight;
  }

  /** Escape HTML special characters to prevent XSS */
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

})();