import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-profile2' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-profile"' not in s:
    print('GAGAL: skrip profil user (fix7) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

SECTION = r'''<section class="tab" id="tab-profil">
<div class="pf">
<div class="pf-banner" id="pfBanner"><button class="pf-cam" id="pfBannerBtn" type="button" aria-label="Ganti banner" style="display:none"><svg viewBox="0 0 24 24" class="icon"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg></button></div>
<div class="pf-head">
<div class="avatar pf-av" id="upAvatar">?</div>
<div class="pf-actions"><button class="btn primary" id="upEdit" type="button">Masuk / Daftar</button><button class="btn" id="upLogout" type="button" style="display:none">Keluar</button></div>
</div>
<div class="pf-id">
<div class="pf-name"><span id="upName">Tamu</span><span id="upBadge"></span></div>
<div class="pf-handle" id="pfHandle"></div>
<div class="pf-email" id="upEmail">Masuk untuk melihat dan mengatur profilmu.</div>
</div>
<p class="pf-bio" id="pfBioText"></p>
<a class="pf-chip" id="pfLinkChip" hidden target="_blank" rel="noopener noreferrer"></a>
<p class="pf-hint" id="pfHint" style="display:none"></p>
<div id="pfBody" hidden>
<div class="pf-stats">
<div><b id="pfDays">0</b><span>Hari</span></div>
<div><b id="pfBadgeCount">0</b><span>Lencana</span></div>
<div><b id="pfPct">0%</b><span>Profil</span></div>
</div>
<div class="pf-prog">
<div class="pf-prog-top"><span>Kelengkapan profil</span><b id="pfPct2">0%</b></div>
<div class="pf-bar"><i id="pfBarFill"></i></div>
<p id="pfMissing"></p>
</div>
<div class="pf-tabs">
<button type="button" class="on" data-pt="tentang">Tentang</button>
<button type="button" data-pt="lencana">Lencana</button>
</div>
<div id="pf-tentang">
<div class="pf-info">
<div class="pf-row"><span>Status</span><b id="upRole">Tamu</b></div>
<div class="pf-row"><span>Bergabung</span><b id="upJoined">-</b></div>
</div>
<button class="btn" id="pfEditBio" type="button" style="margin-top:12px">Edit Bio &amp; Link</button>
<div class="pf-form" id="pfBioForm" hidden>
<textarea id="pfBioInput" maxlength="120" rows="3" placeholder="Tulis bio singkat..."></textarea>
<div class="pf-count" id="pfBioCount">0/120</div>
<input id="pfLinkInput" type="text" inputmode="url" maxlength="200" placeholder="Link (contoh: instagram.com/namamu)">
<div class="pf-form-row"><button class="btn primary" id="pfBioSave" type="button">Simpan</button><button class="btn" id="pfBioCancel" type="button">Batal</button></div>
</div>
</div>
<div id="pf-lencana" hidden><div class="pf-bd-grid" id="pfBadges"></div></div>
</div>
</div>
</section>'''

CSS = r'''
@keyframes pfShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pfTw{from{opacity:.2}to{opacity:1}}
html body .pf [hidden],html body .pf-sheet[hidden]{display:none!important}
html body .pf-banner{height:150px;border-radius:16px;position:relative;overflow:hidden;background:linear-gradient(135deg,var(--line),var(--card)) center/cover no-repeat;border:1px solid var(--line)}
html body .pf-cam{position:absolute;right:10px;bottom:10px;width:38px;height:38px;border-radius:50%;border:1px solid rgba(255,255,255,.35);background:rgba(0,0,0,.5);color:#fff;align-items:center;justify-content:center;cursor:pointer;padding:0;z-index:2}
html body .pf-cam svg{width:20px;height:20px}
html body .pf-head{display:flex;justify-content:space-between;align-items:flex-end;padding:0 6px;margin-top:-46px;position:relative;z-index:2;gap:10px}
html body #upAvatar{width:96px;height:96px;font-size:2.2rem;--sz:96px;flex-shrink:0}
html body .pf-av:not([class*="bd-"]){box-shadow:0 0 0 4px var(--bg)}
html body .pf-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;padding-bottom:4px}
html body .pf-actions .btn{padding:9px 14px;font-size:.85rem}
html body .pf-id{padding:12px 6px 0}
html body .pf-name{font-size:1.3rem;font-weight:900;display:flex;align-items:center;gap:4px;flex-wrap:wrap}
html body .pf-handle{color:var(--muted);font-weight:700;font-size:.9rem}
html body .pf-email{color:var(--muted);font-size:.8rem;margin-top:2px;overflow-wrap:anywhere}
html body .pf-bio{margin:12px 6px 0;line-height:1.6;overflow-wrap:anywhere}
html body .pf-chip{display:inline-flex;align-items:center;margin:10px 6px 0;padding:6px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card);font-weight:700;font-size:.82rem;color:var(--text);text-decoration:none;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
html body .pf-hint{margin:8px 6px 0;font-size:.82rem;color:var(--muted);font-weight:700}
html body .pf-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:16px 0 12px}
html body .pf-stats div{text-align:center;border:1px solid var(--line);border-radius:14px;padding:12px 4px;background:var(--card)}
html body .pf-stats b{display:block;font-size:1.35rem}
html body .pf-stats span{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
html body .pf-prog{border:1px solid var(--line);border-radius:14px;padding:14px;background:var(--card)}
html body .pf-prog-top{display:flex;justify-content:space-between;font-weight:700;font-size:.88rem;margin-bottom:8px}
html body .pf-bar{height:8px;border-radius:99px;background:var(--line);overflow:hidden}
html body .pf-bar i{display:block;height:100%;width:0;background:var(--accent);border-radius:99px;transition:width .6s ease}
html body .pf-prog p{margin:8px 0 0;font-size:.78rem;color:var(--muted)}
html body .pf-tabs{display:flex;margin:16px 0 12px;border-bottom:1px solid var(--line)}
html body .pf-tabs button{flex:1;background:none;border:none;border-bottom:2px solid transparent;padding:11px;font:inherit;font-weight:800;color:var(--muted);cursor:pointer}
html body .pf-tabs button.on{color:var(--text);border-bottom-color:var(--accent)}
html body .pf-info{border:1px solid var(--line);border-radius:14px;background:var(--card);overflow:hidden}
html body .pf-row{display:flex;justify-content:space-between;padding:13px 14px;border-top:1px solid var(--line)}
html body .pf-row:first-child{border-top:none}
html body .pf-row span{color:var(--muted)}
html body .pf-form{margin-top:12px;display:flex;flex-direction:column;gap:8px}
html body .pf-form textarea,html body .pf-form input{width:100%;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--text);font:inherit}
html body .pf-count{text-align:right;font-size:.75rem;color:var(--muted)}
html body .pf-form-row{display:flex;gap:8px}
html body .pf-bd-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
html body .pf-bd{border:1px solid var(--line);border-radius:14px;padding:14px 10px;background:var(--card);text-align:center}
html body .pf-bd.lock{opacity:.4;filter:grayscale(1)}
html body .pf-bi{width:44px;height:44px;border-radius:50%;margin:0 auto 8px;display:flex;align-items:center;justify-content:center;background:var(--accent);color:var(--on,#fff)}
html body .pf-bi svg{width:22px;height:22px}
html body .pf-bd b{display:block;font-size:.9rem}
html body .pf-bd small{display:block;margin-top:2px;font-size:.72rem;color:var(--muted)}
html body .pf-sheet{position:fixed;inset:0;z-index:90;background:rgba(0,0,0,.55);display:flex;align-items:flex-end;justify-content:center}
html body .pf-sheet-panel{width:min(520px,100%);background:var(--card);color:var(--text);border-radius:18px 18px 0 0;padding:16px;max-height:85vh;overflow-y:auto;border:1px solid var(--line)}
html body .pf-sheet-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;font-size:1.05rem}
html body .pf-sheet-head button{background:none;border:none;color:var(--text);font:inherit;font-weight:700;cursor:pointer}
html body .pf-sw-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
html body .pf-sw{background:none;border:none;color:var(--text);font:inherit;font-size:.68rem;cursor:pointer;padding:4px;border-radius:10px;text-align:center}
html body .pf-sw.sel{outline:2px solid var(--text)}
html body .pf-sw.lock{opacity:.45}
html body .pfs{display:block;height:54px;border-radius:10px;margin-bottom:6px;position:relative;overflow:hidden;border:1px solid var(--line)}
html body .pf-sheet-row{display:flex;gap:8px;margin-top:14px}
html body .pf-sheet-row .btn{flex:1;text-align:center}
html body .pf-shint{margin:10px 0 0;font-size:.8rem;color:var(--muted);min-height:1.2em}
html body .pfb-sunset{background-image:linear-gradient(135deg,#f97316,#ec4899,#8b5cf6)}
html body .pfb-ocean{background-image:linear-gradient(135deg,#0ea5e9,#2563eb,#1e3a8a)}
html body .pfb-forest{background-image:linear-gradient(135deg,#22c55e,#15803d,#064e3b)}
html body .pfb-candy{background-image:linear-gradient(135deg,#f9a8d4,#c4b5fd,#93c5fd)}
html body .pfb-mono{background-image:linear-gradient(135deg,#111,#555,#ddd)}
html body .pfb-peach{background-image:linear-gradient(135deg,#fde68a,#fdba74,#fca5a5)}
html body .pfb-night{background-image:linear-gradient(135deg,#0f172a,#1e1b4b,#312e81)}
html body .pfb-lilac{background-image:linear-gradient(135deg,#a78bfa,#f0abfc,#fbcfe8)}
html body .pfb-aurora{background-image:linear-gradient(120deg,#22c55e,#06b6d4,#8b5cf6,#22c55e);background-size:300% 300%;animation:pfShift 8s ease infinite}
html body .pfb-lava{background-image:linear-gradient(120deg,#7f1d1d,#ef4444,#f97316,#fde047,#ef4444);background-size:300% 300%;animation:pfShift 6s ease infinite}
html body .pfb-holo{background-image:linear-gradient(120deg,#f0abfc,#67e8f9,#fde68a,#86efac,#f0abfc);background-size:300% 300%;animation:pfShift 5s ease infinite}
html body .pfb-galaksi{background-image:radial-gradient(1.6px 1.6px at 18% 28%,#fff,transparent),radial-gradient(1.4px 1.4px at 62% 18%,#fff,transparent),radial-gradient(1.6px 1.6px at 42% 78%,#fff,transparent),linear-gradient(135deg,#0b0b2b,#3b0764,#9d174d)}
html body :is(.pf-banner,.pfs).pfb-galaksi::after{content:"";position:absolute;inset:0;background:radial-gradient(1.4px 1.4px at 30% 60%,#fff,transparent),radial-gradient(1.4px 1.4px at 80% 40%,#fff,transparent),radial-gradient(1.6px 1.6px at 55% 22%,#fff,transparent),radial-gradient(1.2px 1.2px at 90% 78%,#fff,transparent);animation:pfTw 2.2s ease-in-out infinite alternate}
@media(prefers-reduced-motion:reduce){html body :is(.pf-banner,.pfs),html body :is(.pf-banner,.pfs)::after{animation:none!important}}
'''

JS = r'''
(function(){
  if (typeof auth === 'undefined' || typeof db === 'undefined' || typeof firebase === 'undefined') return;
  var $ = function(id){ return document.getElementById(id); };
  var banner = $('pfBanner');
  if (!banner) return;
  var camBtn = $('pfBannerBtn'), bodyEl = $('pfBody');
  var S = {user: null, data: {}};
  var unsub = null, sheet = null;

  var I = {
    crown: '<path d="M3 18h18l-1.5-9-4.5 4-3-6-3 6-4.5-4L3 18z"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>',
    cal: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/>',
    star: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    cam: '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    spark: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>',
    pen: '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
    img: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M21 16l-5-5-8 9"/>',
    link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    ok: '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>'
  };
  function ico(n){ return '<svg viewBox="0 0 24 24" class="icon">' + I[n] + '</svg>'; }

  var PRESETS = [
    {id:'sunset', n:'Senja'}, {id:'ocean', n:'Laut'}, {id:'forest', n:'Hutan'}, {id:'candy', n:'Permen'},
    {id:'mono', n:'Mono'}, {id:'peach', n:'Peach'}, {id:'night', n:'Malam'}, {id:'lilac', n:'Lilac'},
    {id:'aurora', n:'Aurora', owner:true}, {id:'galaksi', n:'Galaksi', owner:true},
    {id:'lava', n:'Lava', owner:true}, {id:'holo', n:'Holo', owner:true}
  ];

  function say(m){
    var h = $('pfHint');
    h.textContent = m || '';
    h.style.display = m ? 'block' : 'none';
    clearTimeout(say.t);
    if (m) say.t = setTimeout(function(){ h.style.display = 'none'; }, 2400);
  }
  function shint(m){ var h = $('pfSheetHint'); if (h) h.textContent = m || ''; }

  function normLink(v){
    v = String(v || '').trim();
    if (!v || v.length > 200) return '';
    if (!/^https?:\/\//i.test(v)) v = 'https://' + v;
    try {
      var u = new URL(v);
      if (u.protocol !== 'http:' && u.protocol !== 'https:') return '';
      if (!u.hostname || u.hostname.indexOf('.') < 0) return '';
      return u.href;
    } catch (e) { return ''; }
  }

  function applyBanner(el, id, url){
    Array.prototype.slice.call(el.classList).forEach(function(c){ if (c.indexOf('pfb-') === 0) el.classList.remove(c); });
    el.style.backgroundImage = '';
    if (id === 'custom' && url && String(url).indexOf('data:image/') === 0) {
      el.style.backgroundImage = 'url("' + url + '")';
    } else if (PRESETS.some(function(p){ return p.id === id; })) {
      el.classList.add('pfb-' + id);
    }
  }

  function render(){
    var u = S.user, d = S.data || {}, guest = !u, admin = !!d.isAdmin;
    camBtn.style.display = guest ? 'none' : 'flex';
    bodyEl.hidden = guest;
    applyBanner(banner, guest ? '' : d.banner, d.bannerURL);
    var bio = String(d.bio || '').trim();
    var link = normLink(d.link || '');
    $('pfHandle').textContent = u ? '@' + String(u.email || d.name || 'user').split('@')[0].toLowerCase().replace(/[^a-z0-9._]/g, '') : '';
    $('pfBioText').textContent = guest ? 'Masuk untuk membuat profilmu sendiri.' : (bio || 'Belum ada bio. Ketuk "Edit Bio & Link" untuk menulis.');
    var chip = $('pfLinkChip');
    if (link) {
      chip.hidden = false;
      chip.href = link;
      chip.textContent = new URL(link).hostname.replace(/^www\./, '');
    } else {
      chip.hidden = true;
    }
    if (sheet && !sheet.hidden) fillGrid();
    if (guest) return;

    var jd = null;
    if (d.createdAt && d.createdAt.toDate) jd = d.createdAt.toDate();
    else if (u.metadata && u.metadata.creationTime) jd = new Date(u.metadata.creationTime);
    var days = jd ? Math.max(1, Math.floor((Date.now() - jd.getTime()) / 864e5) + 1) : 1;

    var has = {foto: !!d.photoURL, banner: !!d.banner, bio: !!bio, frame: !!d.avatarBorder && d.avatarBorder !== 'none', link: !!link};
    var names = {foto: 'foto profil', banner: 'banner', bio: 'bio', frame: 'bingkai avatar', link: 'link'};
    var keys = Object.keys(has);
    var done = keys.filter(function(k){ return has[k]; }).length;
    var pct = Math.round(done / keys.length * 100);

    var BADGES = [
      {n:'Anggota', d:'Bergabung di Multifungsi', ok:true, i:'user'},
      {n:'Owner', d:'Pemilik web ini', ok:admin, i:'crown'},
      {n:'7 Hari', d:'Bergabung 7 hari', ok:days >= 7, i:'cal'},
      {n:'30 Hari', d:'Bergabung 30 hari', ok:days >= 30, i:'star'},
      {n:'Berfoto', d:'Memasang foto profil', ok:has.foto, i:'cam'},
      {n:'Bergaya', d:'Memakai bingkai avatar', ok:has.frame, i:'spark'},
      {n:'Bercerita', d:'Menulis bio', ok:has.bio, i:'pen'},
      {n:'Berbanner', d:'Memasang banner', ok:has.banner, i:'img'},
      {n:'Terhubung', d:'Menambahkan link', ok:has.link, i:'link'},
      {n:'Lengkap', d:'Profil 100%', ok:pct === 100, i:'ok'}
    ];
    var unlocked = BADGES.filter(function(b){ return b.ok; }).length;

    $('pfDays').textContent = days;
    $('pfBadgeCount').textContent = unlocked + '/' + BADGES.length;
    $('pfPct').textContent = pct + '%';
    $('pfPct2').textContent = pct + '%';
    $('pfBarFill').style.width = pct + '%';
    var miss = keys.filter(function(k){ return !has[k]; }).map(function(k){ return names[k]; });
    $('pfMissing').textContent = miss.length ? 'Lengkapi: ' + miss.join(', ') + '.' : 'Profilmu sudah lengkap!';

    var grid = $('pfBadges');
    grid.replaceChildren();
    BADGES.forEach(function(b){
      var el = document.createElement('div');
      el.className = 'pf-bd' + (b.ok ? '' : ' lock');
      var ic = document.createElement('span');
      ic.className = 'pf-bi';
      ic.innerHTML = ico(b.i);
      var nm = document.createElement('b');
      nm.textContent = b.n;
      var ds = document.createElement('small');
      ds.textContent = b.d;
      el.append(ic, nm, ds);
      grid.appendChild(el);
    });
  }

  /* ----- Tab Tentang / Lencana ----- */
  document.querySelectorAll('[data-pt]').forEach(function(b){
    b.addEventListener('click', function(){
      document.querySelectorAll('[data-pt]').forEach(function(x){ x.classList.toggle('on', x === b); });
      $('pf-tentang').hidden = b.dataset.pt !== 'tentang';
      $('pf-lencana').hidden = b.dataset.pt !== 'lencana';
    });
  });

  /* ----- Edit bio & link ----- */
  var bioIn = $('pfBioInput'), linkIn = $('pfLinkInput'), form = $('pfBioForm'), editBtn = $('pfEditBio');
  function count(){ $('pfBioCount').textContent = bioIn.value.length + '/120'; }
  bioIn.addEventListener('input', count);
  editBtn.addEventListener('click', function(){
    var d = S.data || {};
    bioIn.value = d.bio || '';
    linkIn.value = d.link || '';
    count();
    form.hidden = false;
    editBtn.hidden = true;
  });
  $('pfBioCancel').addEventListener('click', function(){ form.hidden = true; editBtn.hidden = false; });
  $('pfBioSave').addEventListener('click', async function(){
    var u = auth.currentUser;
    if (!u) return;
    var bio = bioIn.value.trim().slice(0, 120);
    var raw = linkIn.value.trim();
    var link = normLink(raw);
    if (raw && !link) { say('Link tidak valid.'); return; }
    try {
      await db.collection('users').doc(u.uid).set({bio: bio, link: link}, {merge: true});
      form.hidden = true;
      editBtn.hidden = false;
      say('Tersimpan.');
    } catch (e) {
      say('Gagal menyimpan, coba lagi.');
    }
  });

  /* ----- Pemilih banner ----- */
  async function saveBanner(payload){
    var u = auth.currentUser;
    if (!u) return;
    try {
      await db.collection('users').doc(u.uid).set(payload, {merge: true});
      shint('Banner disimpan.');
    } catch (e) {
      shint('Gagal menyimpan, coba lagi.');
    }
  }

  function toBanner(file, cb){
    var r = new FileReader();
    r.onload = function(){
      var img = new Image();
      img.onload = function(){
        var W = 900, H = 300, c = document.createElement('canvas');
        c.width = W; c.height = H;
        var ratio = Math.max(W / img.width, H / img.height);
        var w = img.width * ratio, h = img.height * ratio;
        c.getContext('2d').drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
        var q = 0.82, out = c.toDataURL('image/jpeg', q);
        while (out.length > 700000 && q > 0.4) { q -= 0.1; out = c.toDataURL('image/jpeg', q); }
        cb(out.length > 900000 ? null : out);
      };
      img.onerror = function(){ cb(null); };
      img.src = r.result;
    };
    r.onerror = function(){ cb(null); };
    r.readAsDataURL(file);
  }

  function fillGrid(){
    var grid = $('pfSwGrid');
    if (!grid) return;
    var d = S.data || {}, admin = !!d.isAdmin, cur = d.banner || '';
    grid.replaceChildren();
    PRESETS.forEach(function(p){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'pf-sw' + (p.id === cur ? ' sel' : '') + ((p.owner && !admin) ? ' lock' : '');
      var sw = document.createElement('span');
      sw.className = 'pfs pfb-' + p.id;
      var lb = document.createElement('span');
      lb.textContent = p.n + (p.owner ? ' ★' : '');
      b.append(sw, lb);
      b.addEventListener('click', function(){
        if (p.owner && !admin) { shint('Banner
bertanda ★ khusus Owner.'); return; }
        shint('');
        saveBanner({banner: p.id, bannerURL: firebase.firestore.FieldValue.delete()});
      });
      grid.appendChild(b);
    });
  }

  function buildSheet(){
    sheet = document.createElement('div');
    sheet.className = 'pf-sheet';
    sheet.hidden = true;
    sheet.innerHTML = '<div class="pf-sheet-panel"><div class="pf-sheet-head"><b>Banner Profil</b><button type="button" id="pfSheetClose">Tutup</button></div><div class="pf-sw-grid" id="pfSwGrid"></div><p class="pf-shint" id="pfSheetHint"></p><div class="pf-sheet-row"><button class="btn" id="pfGal" type="button">Pilih dari Galeri</button><button class="btn" id="pfRm" type="button">Hapus Banner</button></div><input type="file" id="pfFile" accept="image/*" hidden></div>';
    document.body.appendChild(sheet);
    sheet.addEventListener('click', function(e){ if (e.target === sheet) sheet.hidden = true; });
    $('pfSheetClose').addEventListener('click', function(){ sheet.hidden = true; });
    $('pfGal').addEventListener('click', function(){ $('pfFile').click(); });
    $('pfRm').addEventListener('click', function(){
      shint('');
      saveBanner({banner: firebase.firestore.FieldValue.delete(), bannerURL: firebase.firestore.FieldValue.delete()});
    });
    $('pfFile').addEventListener('change', function(){
      var f = this.files && this.files[0];
      this.value = '';
      if (!f) return;
      if (f.type && f.type.indexOf('image/') !== 0) { shint('File harus berupa gambar.'); return; }
      shint('Memproses gambar...');
      toBanner(f, function(data){
        if (!data) { shint('Gambar tidak bisa dipakai. Coba foto lain (JPG atau PNG).'); return; }
        saveBanner({banner: 'custom', bannerURL: data});
      });
    });
  }

  camBtn.addEventListener('click', function(){
    if (!sheet) buildSheet();
    shint('');
    fillGrid();
    sheet.hidden = false;
  });

  /* ----- Data real-time dari Firestore ----- */
  auth.onAuthStateChanged(function(user){
    S.user = user;
    S.data = {};
    if (unsub) { unsub(); unsub = null; }
    if (!user) { render(); return; }
    unsub = db.collection('users').doc(user.uid).onSnapshot(function(snap){
      S.data = snap.exists ? snap.data({serverTimestamps: 'estimate'}) : {};
      render();
    }, function(){ render(); });
    render();
  });

  render();
})();
'''

m = re.search(r'<section class="tab" id="tab-profil">.*?</section>', s, re.S)
if not m or '</head>' not in s or s.rfind('</body>') == -1:
    print('GAGAL: struktur index.html tidak cocok. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak33')
s = s[:m.start()] + SECTION + s[m.end():]
s = s.replace('</head>', '<style id="mz-profile2">' + CSS + '</style>\n</head>', 1)
i = s.rfind('</body>')
s = s[:i] + '<script id="mz-profile2-js">' + JS + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Profil baru : OK')
