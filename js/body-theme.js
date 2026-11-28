// Terapkan tema tersimpan sebelum halaman tampil.
try {
  if (localStorage.getItem('mz-theme') !== 'dark') document.body.classList.add('light-mode');
} catch (e) {
  document.body.classList.add('light-mode');
}
