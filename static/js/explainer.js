// Explainer modal: fetch slides, use speechSynthesis, auto-advance
let slides = [];
let slideIndex = 0;
let paused = false;
let utterance = null;

function speakSlide(slide) {
  // Cancel any ongoing speech
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  if (!slide || !slide.text) return;

  const voiceOn = localStorage.getItem('voiceNarration') !== 'false';
  if (!voiceOn || !window.speechSynthesis) {
    // No speech: auto-advance after 7 seconds
    setTimeout(() => {
      if (!paused && slideIndex < slides.length - 1) {
        slideIndex++;
        renderSlide();
      }
    }, 7000);
    return;
  }

  utterance = new SpeechSynthesisUtterance(slide.text);
  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  utterance.onend = () => {
    if (!paused && slideIndex < slides.length - 1) {
      slideIndex++;
      renderSlide();
    }
  };
  utterance.onerror = () => {
    // Fallback timer on error
    setTimeout(() => {
      if (!paused && slideIndex < slides.length - 1) {
        slideIndex++;
        renderSlide();
      }
    }, 7000);
  };

  window.speechSynthesis.speak(utterance);
}

function openExplainer(qid, chosen) {
  const modal = document.getElementById('explainer-modal');
  const errorEl = document.getElementById('explainer-error');
  if (errorEl) errorEl.textContent = '';

  fetch(`/explainer/${qid}/${chosen}`)
    .then(r => {
      if (!r.ok) throw new Error('Server error: ' + r.status);
      return r.json();
    })
    .then(data => {
      if (data.error) {
        showErrorInModal(data.error);
        return;
      }
      slides = data.slides || data; // handle both {slides: [...]} and direct array
      if (!slides.length) {
        showErrorInModal('No slides returned.');
        return;
      }
      slideIndex = 0;
      modal.style.display = 'flex';
      renderSlide();
    })
    .catch(err => {
      console.error('Explainer fetch error:', err);
      showErrorInModal('Could not load the explainer, please try again');
    });
}

function showErrorInModal(msg) {
  const modal = document.getElementById('explainer-modal');
  const errorEl = document.getElementById('explainer-error');
  if (errorEl) errorEl.textContent = msg;
  slides = [{ icon: '⚠️', title: 'Error', text: msg }];
  slideIndex = 0;
  modal.style.display = 'flex';
  renderSlide();
}

function renderSlide() {
  if (!slides.length) return;
  const s = slides[slideIndex];
  document.getElementById('slide-icon').textContent = s.icon || '💡';
  document.getElementById('slide-title').textContent = s.title || '';
  document.getElementById('slide-text').textContent = s.text || '';

  // Dots
  const dots = document.getElementById('slide-dots');
  dots.innerHTML = '';
  slides.forEach((_, i) => {
    const dot = document.createElement('span');
    if (i === slideIndex) dot.classList.add('active');
    dots.appendChild(dot);
  });

  // Speak this slide
  speakSlide(s);
}

function closeModal() {
  const modal = document.getElementById('explainer-modal');
  modal.style.display = 'none';
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  paused = false;
  const pauseBtn = document.getElementById('pause-slide');
  if (pauseBtn) pauseBtn.textContent = '⏸ Pause';
}

document.addEventListener('DOMContentLoaded', () => {
  // Prev button
  document.getElementById('prev-slide')?.addEventListener('click', () => {
    if (slideIndex > 0) { slideIndex--; renderSlide(); }
  });

  // Next button
  document.getElementById('next-slide')?.addEventListener('click', () => {
    if (slideIndex < slides.length - 1) { slideIndex++; renderSlide(); }
  });

  // Pause/Play button
  document.getElementById('pause-slide')?.addEventListener('click', () => {
    const btn = document.getElementById('pause-slide');
    if (paused) {
      paused = false;
      btn.textContent = '⏸ Pause';
      if (slideIndex < slides.length) speakSlide(slides[slideIndex]);
    } else {
      paused = true;
      btn.textContent = '▶ Play';
      if (window.speechSynthesis) window.speechSynthesis.pause();
    }
  });

  // Close button
  document.getElementById('close-modal')?.addEventListener('click', closeModal);

  // ESC key closes modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // Wire up all explain buttons
  document.querySelectorAll('.explain-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const qid = btn.dataset.qid;
      const chosen = btn.dataset.chosen;
      if (!qid) {
        showErrorInModal('No question available for this topic yet.');
        return;
      }
      openExplainer(qid, chosen);
    });
  });
});