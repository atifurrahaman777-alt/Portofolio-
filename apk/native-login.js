(function () {
  var C = window.Capacitor;
  if (!C || !C.isNativePlatform || !C.isNativePlatform()) return;

  function showErr(m) {
    var e = document.getElementById('authError');
    if (e) { e.textContent = m; e.style.display = 'block'; }
  }
  function hideGithub() {
    document.querySelectorAll('[data-provider="github"]').forEach(function (b) { b.style.display = 'none'; });
  }
  hideGithub();
  document.addEventListener('DOMContentLoaded', hideGithub);

  document.addEventListener('click', async function (e) {
    var b = e.target.closest && e.target.closest('[data-provider]');
    if (!b) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    if (b.dataset.provider !== 'google') { showErr('Metode ini belum tersedia di aplikasi.'); return; }
    var p = C.Plugins && C.Plugins.FirebaseAuthentication;
    if (!p) { showErr('Login Google belum siap di aplikasi ini.'); return; }
    b.disabled = true;
    try {
      var r = await p.signInWithGoogle();
      var idToken = r && r.credential && r.credential.idToken;
      if (!idToken) throw new Error('Token Google tidak diterima.');
      await firebase.auth().signInWithCredential(firebase.auth.GoogleAuthProvider.credential(idToken));
    } catch (err) {
      var msg = String((err && (err.message || err.code)) || err);
      if (!/cancel|dismiss|12501/i.test(msg)) showErr('Login Google gagal: ' + msg);
    } finally {
      b.disabled = false;
    }
  }, true);
})();
