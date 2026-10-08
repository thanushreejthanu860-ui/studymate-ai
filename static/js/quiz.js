// Quiz run: one question at a time with progress bar
let current = 0;
let total = 0;

function initQuiz(n) {
  total = n;
  showSlide(0);
}

function showSlide(index) {
  document.querySelectorAll('.question-slide').forEach((el, i) => {
    el.classList.toggle('hidden', i !== index);
  });
  // Update progress bar
  document.getElementById('progress-bar').style.width = ((index + 1) / total * 100) + '%';
  document.getElementById('q-current').textContent = index + 1;
  // Show/hide buttons
  document.getElementById('prev-btn').style.display = index === 0 ? 'none' : '';
  document.getElementById('next-btn').style.display = index === total - 1 ? 'none' : '';
  document.getElementById('submit-btn').style.display = index === total - 1 ? '' : 'none';
}

function nextQ() {
  // Require an answer before advancing
  const slide = document.querySelectorAll('.question-slide')[current];
  const chosen = slide.querySelector('input[type=radio]:checked');
  if (!chosen) { alert('Please select an answer.'); return; }
  if (current < total - 1) { current++; showSlide(current); }
}

function prevQ() {
  if (current > 0) { current--; showSlide(current); }
}
