// app.js — dark mode toggle with persistence
(function(){
  const KEY = 'symptomx-theme';
  const apply = (t) => {
    if (!t || t === 'system') document.body.removeAttribute('data-theme');
    else document.body.setAttribute('data-theme', t);
  };
  const btn = document.getElementById('theme-toggle');
  const saved = localStorage.getItem(KEY) || 'system';
  apply(saved);
  function label(){
    const t = document.body.getAttribute('data-theme') || 'system';
    btn.textContent = (t === 'dark') ? 'Light Mode' : 'Dark Mode';
  }
  if (btn){
    btn.addEventListener('click', () => {
      const cur = document.body.getAttribute('data-theme') || 'system';
      const next = cur === 'dark' ? 'light' : 'dark';
      localStorage.setItem(KEY, next);
      apply(next);
      label();
    });
    label();
  }
})();
