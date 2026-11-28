(function(){
  var MEDIA = {cloud: 'knhk74y4', preset: 'Web_multifungsi'};
  var $ = function(id){ return document.getElementById(id); };

  function fail(e){
    var h = $('pfHint');
    if (h) {
      h.textContent = 'Error profil: ' + (e && e.message ? e.message : e);
      h.style.display = 'block';
      h.style.color = '#ef4444';
    }
    if (window.console) console.error(e);
  }

  function main(){
    if (typeof auth === 'undefined' || typeof db === 'undefined' || typeof firebase === 'undefined') {
      throw new Error('Firebase belum siap.');
    }
    var banner = $('pfBanner');
    if (!banner) throw new Error('Elemen banner tidak ditemukan.');
    var camBtn = $('pfBannerBtn'), bodyEl = $('pfBody');
    var S = {user: null, data: {}};
    var unsub = null, sheet = null, shownBanner = null, busy = false;
    var reduce = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
    var cloudOn = !!(MEDIA.cloud && MEDIA.preset);

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
      {id:'sunset', n:'Senja', l:'#a63a10', d:'#a63a10', ol:'#ffffff', od:'#ffffff'}, {id:'ocean', n:'Laut', l:'#1d4ed8', d:'#1d4ed8', ol:'#ffffff', od:'#ffffff'}, {id:'forest', n:'Hutan', l:'#166534', d:'#166534', ol:'#ffffff', od:'#ffffff'}, {id:'candy', n:'Permen', l:'#a81959', d:'#a81959', ol:'#ffffff', od:'#ffffff'},
      {id:'mono', n:'Mono', l:'#8a5a2b', d:'#8a5a2b', ol:'#ffffff', od:'#ffffff'}, {id:'peach', n:'Peach', l:'#bf8b5e', d:'#bf8b5e', ol:'#ffffff', od:'#ffffff'}, {id:'night', n:'Malam', l:'#1d4ed8', d:'#1d4ed8', ol:'#ffffff', od:'#ffffff'}, {id:'lilac', n:'Lilac', l:'#166534', d:'#166534', ol:'#ffffff', od:'#ffffff'},
      {id:'aurora', n:'Aurora', owner:true}, {id:'galaksi', n:'Galaksi', owner:true},
      {id:'lava', n:'Lava', owner:true}, {id:'holo', n:'Holo', owner:true}, {id:'hacker', n:'Hacker', owner:true}
    ];

    function say(m){
      var h = $('pfHint');
      h.textContent = m || '';
      h.style.color = '';
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

    function okUrl(u){
      u = String(u || '');
      return u.indexOf('data:image/') === 0 || u.indexOf('https://res.cloudinary.com/') === 0;
    }

    function applyBanner(el, id, url, type){
      var key = id + '|' + type + '|' + url;
      if (shownBanner === key) return;
      shownBanner = key;
      Array.prototype.slice.call(el.classList).forEach(function(c){ if (c.indexOf('pfb-') === 0) el.classList.remove(c); });
      el.style.backgroundImage = '';
      var old = el.querySelector('.pf-media');
      if (old) old.remove();
      if (id === 'custom' && okUrl(url)) {
        var m;
        if (type === 'video') {
          m = document.createElement('video');
          m.muted = true;
          m.loop = true;
          m.playsInline = true;
          m.setAttribute('playsinline', '');
          m.setAttribute('muted', '');
          m.preload = 'auto';
          m.src = url;
          if (!reduce) {
            m.autoplay = true;
            var p = m.play();
            if (p && p.catch) p.catch(function(){});
          }
        } else {
          m = document.createElement('img');
          m.alt = '';
          m.src = url;
        }
        m.className = 'pf-media';
        el.insertBefore(m, el.firstChild);
      } else if (PRESETS.some(function(p){ return p.id === id; })) {
        el.classList.add('pfb-' + id);
      }
    }

    function render(){
      var u = S.user, d = S.data || {}, guest = !u, admin = !!d.isAdmin;
      camBtn.style.display = guest ? 'none' : 'flex';
      bodyEl.hidden = guest;
      applyBanner(banner, guest ? '' : d.banner, d.bannerURL, d.bannerType);
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

    document.querySelectorAll('[data-pt]').forEach(function(b){
      b.addEventListener('click', function(){
        document.querySelectorAll('[data-pt]').forEach(function(x){ x.classList.toggle('on', x === b); });
        $('pf-tentang').hidden = b.dataset.pt !== 'tentang';
        $('pf-lencana').hidden = b.dataset.pt !== 'lencana';
      });
    });

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
    var DEL = function(){ return firebase.firestore.FieldValue.delete(); };

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

    function setProgress(p){
      var w = $('pfUp'), b = $('pfUpBar');
      if (!w) return;
      w.hidden = false;
      b.style.width = p + '%';
      shint('Mengunggah... ' + p + '%');
    }
    function endProgress(){
      var w = $('pfUp');
      if (w) w.hidden = true;
      busy = false;
    }

    function uploadCloud(file, cb){
      var fd = new FormData();
      fd.append('file', file);
      fd.append('upload_preset', MEDIA.preset);
      var x = new XMLHttpRequest();
      x.open('POST', 'https://api.cloudinary.com/v1_1/' + MEDIA.cloud + '/auto/upload');
      x.upload.onprogress = function(e){
        if (e.lengthComputable) setProgress(Math.round(e.loaded / e.total * 100));
      };
      x.onload = function(){
        var r;
        try { r = JSON.parse(x.responseText); } catch (e) { cb(null, 'Respons upload tidak valid.'); return; }
        if (x.status >= 200 && x.status < 300 && r.secure_url) {
          cb({url: r.secure_url, type: r.resource_type === 'video' ? 'video' : 'image'});
        } else {
          cb(null, (r.error && r.error.message) || 'Upload gagal.');
        }
      };
      x.onerror = function(){ cb(null, 'Koneksi bermasalah saat upload.'); };
      x.send(fd);
    }

    function onFile(f){
      if (!f || busy) return;
      var isVid = f.type.indexOf('video/') === 0, isImg = f.type.indexOf('image/') === 0;
      if (!isVid && !isImg) { shint('File harus berupa foto, GIF, atau video.'); return; }
      if (cloudOn) {
        var cap = isVid ? 25 : 10;
        if (f.size > cap * 1048576) { shint('File terlalu besar (maks ' + cap + ' MB).'); return; }
        busy = true;
        setProgress(0);
        uploadCloud(f, function(res, err){
          endProgress();
          if (!res) { shint(err || 'Upload gagal.'); return; }
          saveBanner({banner: 'custom', bannerURL: res.url, bannerType: res.type});
        });
        return;
      }
      if (isVid) { shint('Video butuh Cloudinary. Jalankan ulang fix34.py dan isi cloud name + preset.'); return; }
      if (f.type === 'image/gif') {
        if (f.size > 600 * 1024) { shint('GIF maksimal 600 KB (atau aktifkan Cloudinary untuk yang lebih besar).'); return; }
        var rd = new FileReader();
        rd.onload = function(){ saveBanner({banner: 'custom', bannerURL: rd.result, bannerType: 'image'}); };
        rd.onerror = function(){ shint('GIF tidak bisa dibaca.'); };
        rd.readAsDataURL(f);
        return;
      }
      shint('Memproses gambar...');
      toBanner(f, function(data){
        if (!data) { shint('Gambar tidak bisa dipakai. Coba foto lain (JPG atau PNG).'); return; }
        saveBanner({banner: 'custom', bannerURL: data, bannerType: 'image'});
      });
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
          if (p.owner && !admin) { shint('Banner bertanda ★ khusus Owner.'); return; }
          shint('');
          saveBanner({banner: p.id, bannerURL: DEL(), bannerType: DEL()});
        });
        grid.appendChild(b);
      });
    }

    function buildSheet(){
      sheet = document.createElement('div');
      sheet.className = 'pf-sheet';
      sheet.hidden = true;
      sheet.innerHTML = '<div class="pf-sheet-panel"><div class="pf-sheet-head"><b>Banner Profil</b><button type="button" id="pfSheetClose">Tutup</button></div><div class="pf-sw-grid" id="pfSwGrid"></div><p class="pf-shint" id="pfSheetHint"></p><div class="pf-up" id="pfUp" hidden><i id="pfUpBar"></i></div><div class="pf-sheet-row"><button class="btn" id="pfGal" type="button">Foto / GIF / Video</button><button class="btn" id="pfRm" type="button">Hapus Banner</button></div><input type="file" id="pfFile" accept="image/*,video/*" hidden aria-label="Kolom input"></div>';
      document.body.appendChild(sheet);
      sheet.addEventListener('click', function(e){ if (e.target === sheet) sheet.hidden = true; });
      $('pfSheetClose').addEventListener('click', function(){ sheet.hidden = true; });
      $('pfGal').addEventListener('click', function(){ if (!busy) $('pfFile').click(); });
      $('pfRm').addEventListener('click', function(){
        if (busy) return;
        shint('');
        saveBanner({banner: DEL(), bannerURL: DEL(), bannerType: DEL()});
      });
      $('pfFile').addEventListener('change', function(){
        var f = this.files && this.files[0];
        this.value = '';
        onFile(f);
      });
    }

    camBtn.addEventListener('click', function(){
      if (!sheet) buildSheet();
      fillGrid();
      shint(cloudOn ? 'Foto atau GIF maks 10 MB, video maks 25 MB.' : 'Foto dan GIF kecil (maks 600 KB). Video butuh Cloudinary.');
      sheet.hidden = false;
    });

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
  }

  try { main(); } catch (e) { fail(e); }
})();
