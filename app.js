const ICON_STYLE = 'width:1em;height:1em;display:inline-block;vertical-align:-0.15em;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round';
const SUN_ICON = '<svg viewBox="0 0 24 24" style="' + ICON_STYLE + '"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="22"/><line x1="4" y1="12" x2="2" y2="12"/><line x1="22" y1="12" x2="20" y2="12"/><line x1="5" y1="5" x2="6.4" y2="6.4"/><line x1="17.6" y1="17.6" x2="19" y2="19"/><line x1="5" y1="19" x2="6.4" y2="17.6"/><line x1="17.6" y1="6.4" x2="19" y2="5"/></svg>';
const MOON_ICON = '<svg viewBox="0 0 24 24" style="' + ICON_STYLE + '"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z"/></svg>';

document.addEventListener('DOMContentLoaded', () => {
  // Halaman tool mengikuti tema induk saat di-embed; tema tersimpan dipakai saat dibuka sendiri.
  try {
    if (window.parent === window) {
      const saved = localStorage.getItem('mz-theme');
      if (saved) document.body.classList.toggle('light-mode', saved === 'light');
    }
  } catch (e) {}

  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;

  function paint() {
    const light = document.body.classList.contains('light-mode');
    themeToggle.innerHTML = light ? MOON_ICON : SUN_ICON;
    themeToggle.setAttribute('aria-label', light ? 'Ganti mode gelap' : 'Ganti mode terang');
  }

  paint();
  themeToggle.addEventListener('click', () => {
    const light = document.body.classList.toggle('light-mode');
    try { localStorage.setItem('mz-theme', light ? 'light' : 'dark'); } catch (e) {}
    paint();
  });
});
