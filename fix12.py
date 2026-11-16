import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-login' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

# 1. Hapus tombol login lama dari atas sidebar
s, n1 = re.subn(r'<button class="nav-btn" id="auth-toggle".*?</button>\s*<div style="height:1px;background:var\(--line\);margin:4px 0 8px"></div>\s*', '', s, count=1, flags=re.S)

# 2. Tombol login baru di bawah sidebar
foot = ('<div class="sidebar-foot"><button id="auth-toggle" type="button" style="width:100%;display:flex;align-items:center;justify-content:center;gap:10px;padding:13px 14px;border-radius:10px;background:var(--accent);color:var(--on);border:1px solid var(--line);font:inherit;font-weight:800;font-size:.95rem;cursor:pointer">'
        '<svg viewBox="0 0 24 24" class="icon"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></svg>'
        '<span id="authToggleLabel">Masuk</span></button></div>')
s, n2 = re.subn(r'(</nav>)(\s*</aside>)', lambda m: m.group(1) + '\n' + foot + m.group(2), s, count=1)

# 3. Pilihan akun di panel login
providers = '''<div id="authProviders" style="display:flex;flex-direction:column;gap:10px">
<p class="muted" style="margin:0;font-size:.85rem;text-align:center">Pilih akun untuk masuk</p>
<button type="button" class="auth-prov" data-provider="google"><svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>Lanjutkan dengan Google</button>
<button type="button" class="auth-prov" data-provider="github"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2c-3.2.7-3.87-1.37-3.87-1.37-.52-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.78 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.69 5.39-5.25 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 23.5 12C23.5 5.73 18.27.5 12 .5z"/></svg>Lanjutkan dengan GitHub</button>
</div>
'''
marker = '<p class="gate-error" id="authError"'
n3 = 1 if marker in s else 0
s = s.replace(marker, providers + marker, 1)

if not (n1 and n2 and n3):
    print('Tombol lama dihapus  :', 'OK' if n1 else 'GAGAL')
    print('Tombol bawah sidebar :', 'OK' if n2 else 'GAGAL')
    print('Pilihan akun         :', 'OK' if n3 else 'GAGAL')
    print('Dibatalkan, tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak12')

css = '''
html body .auth-tabs,html body #authLoginForm,html body #authRegisterForm{display:none!important}
html body .sidebar{overflow:hidden!important}
html body .sidebar-nav{flex:1 1 auto;min-height:0;overflow-y:auto}
html body .sidebar-foot{flex-shrink:0;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
html body .sidebar-foot svg{width:20px;height:20px}
html body .auth-prov{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:12px 14px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--text);font:inherit;font-weight:700;cursor:pointer}
html body .auth-prov svg{width:20px;height:20px;flex-shrink:0}
html body .auth-prov:active{transform:scale(.97)}
html body .auth-prov:disabled{opacity:.6}
'''
style = '<style id="mz-login">' + css + '</style>\n'

js = r'''
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
'''

i = s.rfind('</body>')
ok = i != -1
s = s.replace('</head>', style + '</head>', 1)
if ok:
    i = s.rfind('</body>')
    s = s[:i] + '<script id="mz-login">' + js + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Tombol lama dihapus  : OK')
print('Tombol bawah sidebar : OK')
print('Pilihan akun         : OK')
print('Script               :', 'OK' if ok else 'GAGAL')
