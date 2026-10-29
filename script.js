(() => {
  const root = document.documentElement;
  const toggle = document.querySelector('.theme-toggle');
  const applyTheme = theme => {
    root.dataset.theme = theme;
    try {
      localStorage.setItem('quizflow-theme', theme);
    } catch(e) {}
    if (toggle) toggle.textContent = theme === 'purple' ? '☀' : '☾';
  };
  applyTheme(root.dataset.theme || 'light');
  if (toggle) {
    toggle.addEventListener('click', () =>
      applyTheme(root.dataset.theme === 'purple' ? 'light' : 'purple')
    );
  }
  const countInputs = document.querySelectorAll('input[name="count"]');
  const secondsInputs = document.querySelectorAll('input[name="seconds_per_question"]');
  const estimate = document.getElementById('estimated-time');
  function updateEstimate() {
    if (!estimate) return;
    const count = Number(
      document.querySelector('input[name="count"]:checked')?.value || 10
    );
    const secs = Number(
      document.querySelector('input[name="seconds_per_question"]:checked')?.value || 30
    );
    const total = count * secs;
    const m = Math.floor(total / 60), s = total % 60;
    estimate.textContent = `About ${m}m ${String(s).padStart(2,'0')}s at this pace`;
  }
  [...countInputs, ...secondsInputs].forEach(el =>
    el.addEventListener('change', updateEstimate)
  );
  updateEstimate();
})();
