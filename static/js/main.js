// ── SVG Gradient ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const svg = document.querySelector('.score-ring');
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  defs.innerHTML = `
    <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7c3aed"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>`;
  svg.prepend(defs);
});
const API_URL = "https://smart-resume-analyser-9vln.onrender.com";

// ── File Drop Zone ─────────────────────────────────
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileNameEl = document.getElementById('fileName');

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    showFileName(file.name);
  }
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showFileName(fileInput.files[0].name);
});
dropZone.addEventListener('click', (e) => {
  if (!e.target.classList.contains('browse-btn')) fileInput.click();
});

function showFileName(name) {
  fileNameEl.textContent = `✅ ${name}`;
}

// ── Form Submit ────────────────────────────────────
const form = document.getElementById('resumeForm');
const analyseBtn = document.getElementById('analyseBtn');
const btnText = analyseBtn.querySelector('.btn-text');
const btnLoader = analyseBtn.querySelector('.btn-loader');
const errorBox = document.getElementById('errorBox');
const errorMsg = document.getElementById('errorMsg');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!fileInput.files[0]) {
    showError('Please select a resume file first.');
    return;
  }
  errorBox.classList.add('hidden');
  setLoading(true);

  const formData = new FormData(form);
  try {
    const res = await fetch(`${API_URL}/analyse`, {
      method: 'POST',
      body: formData
    }); const data = await res.json();
    if (!res.ok || data.error) {
      showError(data.error || 'Analysis failed. Please try again.');
    } else {
      displayResults(data);
    }
  } catch (err) {
    showError('Network error. Please check your connection.');
  } finally {
    setLoading(false);
  }
});

function setLoading(state) {
  analyseBtn.disabled = state;
  btnText.hidden = state;
  btnLoader.hidden = !state;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorBox.classList.remove('hidden');
  window.scrollTo({ top: errorBox.offsetTop - 20, behavior: 'smooth' });
}

// ── Display Results ────────────────────────────────
function displayResults(d) {
  document.getElementById('results').classList.remove('hidden');
  document.getElementById('uploadCard').style.display = 'none';

  // Score ring
  const score = d.overall_score;
  const circumference = 314;
  const offset = circumference - (circumference * score / 100);
  setTimeout(() => {
    document.getElementById('ringFill').style.strokeDashoffset = offset;
  }, 100);

  // Animate score number
  animateNumber('scoreNum', 0, score, 1400);

  // Grade
  document.getElementById('gradeBadge').textContent = d.grade;
  document.getElementById('gradeLabel').textContent = d.grade_label;

  // Info
  document.getElementById('candidateName').textContent = d.name || 'Name not detected';
  document.getElementById('emailVal').textContent = `📧 ${d.email}`;
  document.getElementById('phoneVal').textContent = `📞 ${d.phone}`;

  // Stats
  document.getElementById('eduVal').textContent = d.education;
  document.getElementById('expVal').textContent = d.years_experience !== 'Not mentioned'
    ? `${d.years_experience} yrs` : '—';
  document.getElementById('cgpaVal').textContent = d.cgpa;
  document.getElementById('wordVal').textContent = d.word_count;

  // Score breakdown
  const breakdownLabels = {
    contact: 'Contact Info',
    sections: 'Sections',
    technical_skills: 'Tech Skills',
    soft_skills: 'Soft Skills',
    experience: 'Experience',
    education: 'Education',
    role_match: 'Role Match',
  };
  const maxPts = { contact: 10, sections: 20, technical_skills: 25, soft_skills: 10, experience: 15, education: 10, role_match: 10 };
  const barsEl = document.getElementById('breakdownBars');
  barsEl.innerHTML = '';
  for (const [key, pts] of Object.entries(d.score_breakdown)) {
    const max = maxPts[key] || 10;
    const pct = Math.round((pts / max) * 100);
    barsEl.innerHTML += `
      <div class="bar-row">
        <div class="bar-label">${breakdownLabels[key] || key}</div>
        <div class="bar-track"><div class="bar-fill" style="width:0%" data-pct="${pct}"></div></div>
        <div class="bar-pts">${pts}/${max}</div>
      </div>`;
  }
  setTimeout(() => {
    document.querySelectorAll('.bar-fill').forEach(el => {
      el.style.width = el.dataset.pct + '%';
    });
  }, 200);

  // Role match
  document.getElementById('detectedRole').textContent = d.detected_role;
  setTimeout(() => {
    document.getElementById('roleMatchFill').style.width = d.role_match_percent + '%';
  }, 300);
  document.getElementById('roleMatchPct').textContent = d.role_match_percent + '%';

  renderTags('matchedSkills', d.matched_role_skills, 'tag-match');
  renderTags('missingSkills', d.missing_role_skills, 'tag-miss');

  // Skills
  renderTags('techSkills', d.technical_skills, 'tag-tech');
  renderTags('softSkills', d.soft_skills, 'tag-soft');
  renderTags('sectionsFound', d.sections_found.map(s => s.charAt(0).toUpperCase() + s.slice(1)), 'tag-section');

  // Recommendations
  const recoList = document.getElementById('recoList');
  recoList.innerHTML = d.recommendations.map(r => `<li>${r}</li>`).join('');

  // Scroll to results
  setTimeout(() => {
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 150);
}

function renderTags(elId, items, tagClass) {
  const el = document.getElementById(elId);
  if (!items || items.length === 0) {
    el.innerHTML = `<span class="tag-empty">None detected</span>`;
    return;
  }
  el.innerHTML = items.map(item =>
    `<span class="tag ${tagClass}">${item}</span>`
  ).join('');
}

function animateNumber(elId, from, to, duration) {
  const el = document.getElementById(elId);
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── Reset Form ─────────────────────────────────────
function resetForm() {
  form.reset();
  fileNameEl.textContent = '';
  document.getElementById('results').classList.add('hidden');
  document.getElementById('uploadCard').style.display = 'block';
  errorBox.classList.add('hidden');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
