import re, shutil, os

P = 'html body:is(.light-mode,:not(.light-mode))'

# ===== 1. Tema hitam-putih buat 4 halaman Game/Alat =====
sub_css = ('html body:not(.light-mode){--gold:#f5f5f5;--purple:#f5f5f5;--accent:#f5f5f5;--on:#0a0a0a}\n'
           'html body.light-mode{--gold:#0a0a0a;--purple:#0a0a0a;--accent:#0a0a0a;--on:#fff}\n')
sels = ['.btn', '.ocean-tab.active', '.email-step.active', '.game-controls button.active', '.status']
sub_css += ','.join(P + ' ' + x for x in sels) + '{color:var(--on)!important}\n'
sub_block = '<style id="mz-bw">\n' + sub_css + '</style>\n'

for f in ['amprem.html', 'games.html', 'downloader.html', 'reactch.html']:
    if not os.path.exists(f):
        print(f, ': GAGAL (file tidak ada)')
        continue
    s = open(f, encoding='utf-8').read()
    if 'mz-bw' in s:
        print(f, ': sudah pernah')
        continue
    if 'mz-theme' not in s:
        print(f, ': GAGAL (tema sebelumnya belum terpasang)')
        continue
    shutil.copy(f, f + '.bak7')
    s = s.replace('</head>', sub_block + '</head>', 1)
    open(f, 'w', encoding='utf-8').write(s)
    print(f, ': OK')

# ===== 2. index.html: hitam-putih + profil user =====
f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-bw' in s:
    print(f, ': sudah pernah')
    raise SystemExit
shutil.copy(f, f + '.bak7')

css = r'''
html body:not(.light-mode){--accent:#f5f5f5;--purple:#f5f5f5;--on:#0a0a0a}
html body.light-mode{--accent:#0a0a0a;--purple:#0a0a0a;--on:#fff}
html body .btn.primary,html body .banner-tag,html body .avatar,html body .contact-block button,html body .badge-avatar,html body .avatar-preview-large{color:var(--on)!important}
html body .bottom-nav .nav-btn.home span .icon{stroke:var(--on)!important}
html body .bottom-nav .nav-btn.home span{box-shadow:0 6px 16px rgba(0,0,0,.35)!important}
html body .tag{background:rgba(128,128,128,.14)!important;border-color:var(--line)!important;color:var(--text)!important}
html body::before{background:radial-gradient(circle at 20% 0%,rgba(128,128,128,.12),transparent 60%)!important}
'''
style = '<style id="mz-bw">' + css + '</style>\n'

section = r'''<section class="tab" id="tab-profil">
  <div class="profile-card" id="userProfileCard">
    <div class="profile-top">
      <div class="avatar" id="upAvatar" style="width:70px;height:70px;font-size:1.6rem">?</div>
      <div style="min-width:0">
        <div class="profile-name"><span id="upName">Tamu</span><span id="upBadge"></span></div>
        <div class="profile-bio" id="upEmail" style="overflow-wrap:anywhere">Masuk untuk melihat dan mengatur profilmu.</div>
      </div>
    </div>
    <div class="stat-row" style="grid-template-columns:repeat(2,1fr)">
      <div class="stat"><b id="upRole" style="font-size:1.05rem">Tamu</b><span>Status</span></div>
      <div class="stat"><b id="upJoined" style="font-size:1.05rem">-</b><span>Bergabung</span></div>
    </div>
    <div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap">
      <button class="btn primary" id="upEdit" type="button">Masuk / Daftar</button>
      <button class="btn" id="upLogout" type="button" style="display:none">Keluar</button>
    </div>
  </div>
</section>'''

js = r'''
(function(){
  var els = {
    avatar: document.getElementById('upAvatar'),
    name: document.getElementById('upName'),
    badge: document.getElementById('upBadge'),
    email: document.getElementById('upEmail'),
    role: document.getElementById('upRole'),
    joined: document.getElementById('upJoined'),
    edit: document.getElementById('upEdit'),
    logout: document.getElementById('upLogout')
  };
  if (!els.avatar || typeof auth === 'undefined') return;

  var BADGE = '<svg viewBox="0 0 24 24" class="badge-icon"><path fill="currentColor" d="M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z"/><path fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" d="m9 12 2 2 4-4"/></svg>';

  function render(user, data) {
    if (!user) {
      renderAvatar(els.avatar, '?', '');
      els.name.textContent = 'Tamu';
      els.badge.innerHTML = '';
      els.email.textContent = 'Masuk untuk melihat dan mengatur profilmu.';
      els.role.textContent = 'Tamu';
      els.joined.textContent = '-';
      els.edit.textContent = 'Masuk / Daftar';
      els.logout.style.display = 'none';
      return;
    }
    var name = (data && data.name) || user.displayName || user.email || 'Pengguna';
    var photo = (data && data.photoURL) || '';
    var isAdmin = !!(data && data.isAdmin);
    renderAvatar(els.avatar, name, photo);
    els.name.textContent = name;
    els.badge.innerHTML = '<span class="verified-badge2' + (isAdmin ? ' owner-role' : '') + '">' + BADGE + '</span>';
    els.email.textContent = user.email || '';
    els.role.textContent = isAdmin ? 'Owner' : 'Member';
    var d = null;
    if (data && data.createdAt && data.createdAt.toDate) d = data.createdAt.toDate();
    else if (user.metadata && user.metadata.creationTime) d = new Date(user.metadata.creationTime);
    els.joined.textContent = d ? d.toLocaleDateString('id-ID', {day:'numeric', month:'short', year:'numeric'}) : '-';
    els.edit.textContent = 'Edit Profil';
    els.logout.style.display = 'inline-block';
  }

  async function load(user) {
    if (!user) { render(null, null); return; }
    var data = null;
    try {
      var doc = await db.collection('users').doc(user.uid).get();
      if (doc.exists) data = doc.data();
    } catch (e) {}
    render(user, data);
  }

  auth.onAuthStateChanged(load);

  var saved = document.getElementById('profileSavedMsg');
  if (saved) {
    new MutationObserver(function(){
      if (saved.style.display === 'block') load(auth.currentUser);
    }).observe(saved, {attributes:true, attributeFilter:['style']});
  }

  els.edit.addEventListener('click', function(){
    setTimeout(function(){
      window.scrollTo({top:0});
      var panel = document.getElementById('authPanel');
      if (panel && panel.style.display === 'none') document.getElementById('auth-toggle').click();
    }, 0);
  });
  els.logout.addEventListener('click', function(){ auth.signOut(); });
})();
'''

s, n = re.subn(r'<section class="tab" id="tab-profil">.*?</section>', lambda m: section, s, count=1, flags=re.S)
s = s.replace('</head>', style + '</head>', 1)
i = s.rfind('</body>')
ok_body = i != -1
if ok_body:
    s = s[:i] + '<script id="mz-profile">' + js + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('index Profil :', 'OK' if n else 'GAGAL (section profil tidak ketemu)')
print('index Script :', 'OK' if ok_body else 'GAGAL')
print('index Warna  : OK')
