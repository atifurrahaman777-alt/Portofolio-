(function(){
  if (typeof auth === 'undefined' || typeof firebase === 'undefined') return;
  var label = document.getElementById('authToggleLabel');
  var box = document.getElementById('authProviders');
  var errEl = document.getElementById('authError');

  var MSG = {
    'auth/operation-not-allowed': 'Metode masuk ini belum diaktifkan di Firebase.',
    'auth/unauthorized-domain': 'Domain web ini belum didaftarkan di Firebase (Authorized domains).',
    'auth/network-request-failed': 'Koneksi bermasalah, coba lagi.',
    'auth/account-exists-with-different-credential': 'Email ini sudah terdaftar lewat metode lain. Masuk pakai metode yang dulu dipakai.',
    'auth/web-storage-unsupported': 'Browser memblokir penyimpanan. Coba buka di Chrome biasa.'
  };

  function showErr(m){ errEl.textContent = m; errEl.style.display = 'block'; }
  function clearErr(){ errEl.style.display = 'none'; }
  function setBusy(b){
    document.querySelectorAll('.auth-prov').forEach(function(x){ x.disabled = b; });
  }

  var makers = {
    google: function(){
      var p = new firebase.auth.GoogleAuthProvider();
      p.setCustomParameters({ prompt: 'select_account' });
      return p;
    },
    github: function(){ return new firebase.auth.GithubAuthProvider(); }
  };

  async function signIn(provider){
    clearErr();
    setBusy(true);
    try {
      await auth.signInWithPopup(provider);
    } catch (e) {
      if (e.code === 'auth/popup-closed-by-user' || e.code === 'auth/cancelled-popup-request') {
        // dibatalkan, tidak perlu pesan
      } else if (e.code === 'auth/popup-blocked') {
        try { await auth.signInWithRedirect(provider); return; }
        catch (e2) { showErr(MSG[e2.code] || e2.message || 'Masuk gagal.'); }
      } else {
        showErr(MSG[e.code] || e.message || 'Masuk gagal.');
      }
    } finally {
      setBusy(false);
    }
  }

  document.querySelectorAll('[data-provider]').forEach(function(b){
    b.addEventListener('click', function(){
      var make = makers[b.dataset.provider];
      if (make) signIn(make());
    });
  });

  auth.getRedirectResult().catch(function(e){
    if (e && e.code) showErr(MSG[e.code] || e.message || 'Masuk gagal.');
  });

  // Buat profil otomatis saat pertama kali masuk
  async function ensureProfile(user){
    try {
      var ref = db.collection('users').doc(user.uid);
      var snap = await ref.get();
      if (snap.exists) return false;
      await ref.set({
        name: user.displayName || user.email || 'Pengguna',
        email: user.email || '',
        photoURL: user.photoURL || '',
        isAdmin: false,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      });
      return true;
    } catch (e) { return false; }
  }

  auth.onAuthStateChanged(async function(user){
    if (label) label.textContent = user ? 'Akun Saya' : 'Masuk';
    if (box) box.style.display = user ? 'none' : 'flex';
    if (user) {
      var created = await ensureProfile(user);
      if (created) location.reload();
    }
  });
})();
