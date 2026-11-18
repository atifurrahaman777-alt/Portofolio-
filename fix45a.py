import re, os, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'id="mz-gate-js"' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

i = s.find('<span>Saluran Tele</span>')
start = s.rfind('<div class="mz-sidelinks', 0, i) if i >= 0 else -1
if start < 0 or s.rfind('</body>') == -1 or '</head>' not in s or 'function showTab' not in s:
    print('GAGAL: struktur index.html tidak cocok (pastikan fix43 sudah jalan). Tidak ada yang diubah.')
    raise SystemExit

CSS = r"""
html body .mz-sidelinks.mz-ch{flex-direction:column;gap:8px}
html body .mz-sidelinks.mz-ch .mz-sl{flex:none;width:100%;flex-direction:row;justify-content:center;gap:10px;padding:13px 14px;font-size:.95rem;line-height:1.2;white-space:nowrap;border-radius:10px;background:var(--card);border:1px solid var(--line)}
html body .mz-sidelinks.mz-ch .mz-sl svg{width:20px;height:20px}
html body .mz-sidelinks.mz-ch .mz-sl span{display:inline;overflow:visible}
"""

GATE = r"""
(function(){
  if (typeof auth === 'undefined') return;
  var LOCK = { 'tab-sosial': 1, 'tab-feed': 1, 'tab-alat': 1 };
  var known = false, user = null;
  auth.onAuthStateChanged(function(u){ known = true; user = u; });

  function ask(msg){
    setTimeout(function(){
      if (typeof closeSidebar === 'function') closeSidebar();
      var panel = document.getElementById('authPanel'), tog = document.getElementById('auth-toggle');
      if (panel && panel.style.display === 'none' && tog) tog.click();
      var er = document.getElementById('authError');
      if (er) { er.textContent = msg; er.style.display = 'block'; }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 0);
  }
  window.mzNeedLogin = ask;

  var orig = window.showTab;
  if (typeof orig !== 'function') return;
  window.showTab = function(id){
    if (LOCK[id] && !user) {
      ask(known ? 'Masuk dulu untuk memakai fitur ini. Tamu hanya bisa Game dan Musik.' : 'Memeriksa login... coba lagi sebentar.');
      return;
    }
    return orig.apply(this, arguments);
  };
  auth.onAuthStateChanged(function(u){
    if (!u) {
      var act = document.querySelector('.tab.active');
      if (act && LOCK[act.id]) orig('tab-beranda');
    }
  });
})();
"""

GUARD = r"""<script id="mz-guard">
(function(){
  var root = document.documentElement;
  root.style.visibility = 'hidden';
  var CFG = {apiKey:"AIzaSyC_iYADCUCDN1pCl3j4-jeZT3pU2XcIydU",authDomain:"manz-4d272.firebaseapp.com",projectId:"manz-4d272",appId:"1:431533009387:web:72a9855b0bd596f37911ae"};
  function lock(msg){
    document.body.innerHTML = '<div style="max-width:420px;margin:18vh auto;padding:24px;text-align:center;font-family:system-ui,sans-serif"><h2>Masuk dulu</h2><p>' + msg + '</p><a href="/" style="display:inline-block;margin-top:12px;padding:12px 20px;border-radius:10px;background:#111;color:#fff;text-decoration:none;font-weight:700">Ke beranda</a></div>';
    root.style.visibility = 'visible';
  }
  function load(src, cb){
    var sc = document.createElement('script');
    sc.src = src; sc.onload = cb;
    sc.onerror = function(){ lock('Gagal memeriksa login. Muat ulang halaman.'); };
    document.head.appendChild(sc);
  }
  function run(){
    try { if (!firebase.apps.length) firebase.initializeApp(CFG); } catch (e) {}
    firebase.auth().onAuthStateChanged(function(u){
      if (u) root.style.visibility = 'visible';
      else lock('Fitur ini hanya untuk pengguna yang sudah login. Tamu hanya bisa memakai Game dan Musik.');
    });
  }
  function go(){
    if (window.firebase && firebase.auth) { run(); return; }
    load('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js', function(){
      load('https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js', run);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  setTimeout(function(){ if (root.style.visibility === 'hidden') lock('Pemeriksaan login terlalu lama. Muat ulang halaman.'); }, 12000);
})();
</script>
"""

shutil.copy(f, f + '.bak45')
tag_end = s.find('>', start)
s = s[:start] + '<div class="mz-sidelinks mz-ch">' + s[tag_end + 1:]
s = re.sub(r'<style id="mz-ch">.*?</style>\n?', '', s, flags=re.S)
s = s.replace('</head>', '<style id="mz-ch2">' + CSS + '</style>\n</head>', 1)
j = s.rfind('</body>')
s = s[:j] + '<script id="mz-gate-js">' + GATE + '</script>\n' + s[j:]
open(f, 'w', encoding='utf-8').write(s)
print('Tombol saluran disusun ke bawah : OK')
print('Wajib login (Sosial/Feed/Alat)   : OK')

for p in ['amprem.html', 'downloader.html', 'reactch.html', 'tempmail.html', 'chat.html']:
    if not os.path.exists(p):
        print('Penjaga ' + p + ' : dilewati (file tidak ada)')
        continue
    t = open(p, encoding='utf-8').read()
    if 'id="mz-guard"' in t:
        print('Penjaga ' + p + ' : sudah ada')
        continue
    if '<head>' not in t:
        print('Penjaga ' + p + ' : GAGAL (tag head tidak ketemu)')
        continue
    shutil.copy(p, p + '.bak45')
    t = t.replace('<head>', '<head>\n' + GUARD, 1)
    open(p, 'w', encoding='utf-8').write(t)
    print('Penjaga ' + p + ' : OK')
