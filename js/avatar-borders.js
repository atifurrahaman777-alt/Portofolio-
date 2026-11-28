(function(){
  if (typeof auth === 'undefined' || typeof db === 'undefined') return;
  var LIST = [
    {id:'none', n:'Polos', cls:''},
    {id:'mono', n:'Hitam/Putih', cls:'bd-s-mono'},
    {id:'biru', n:'Biru', cls:'bd-s-biru'},
    {id:'hijau', n:'Hijau', cls:'bd-s-hijau'},
    {id:'pink', n:'Pink', cls:'bd-s-pink'},
    {id:'ungu', n:'Ungu', cls:'bd-s-ungu'},
    {id:'oranye', n:'Oranye', cls:'bd-s-oranye'},
    {id:'ganda', n:'Ganda', cls:'bd-s-ganda'},
    {id:'putus', n:'Putus', cls:'bd-s-putus'},
    {id:'kucing', n:'Kucing', cls:'bd-a-kucing'},
    {id:'tanduk', n:'Tanduk', cls:'bd-a-tanduk'},
    {id:'halo', n:'Halo', cls:'bd-a-halo'},
    {id:'bunga', n:'Bunga', cls:'bd-a-bunga'},
    {id:'bintang', n:'Bintang', cls:'bd-a-bintang'},
    {id:'hati', n:'Hati', cls:'bd-a-hati'},
    {id:'pita', n:'Pita', cls:'bd-a-pita'},
    {id:'denyut', n:'Denyut', cls:'bd-a-denyut'},
    {id:'senja', n:'Senja', cls:'bd-o-senja'},
    {id:'aurora', n:'Aurora', cls:'bd-o-aurora'},
    {id:'salju', n:'Salju', cls:'bd-a-salju'},
    {id:'daun', n:'Daun', cls:'bd-a-daun'},
    {id:'awan', n:'Awan', cls:'bd-a-awan'},
    {id:'topi', n:'Topi', cls:'bd-a-topi'},
    {id:'kelinci', n:'Kelinci', cls:'bd-a-kelinci'},
    {id:'kotak', n:'Kotak', cls:'bd-h-kotak'},
    {id:'heksa', n:'Heksagon', cls:'bd-h-heksa'},
    {id:'okta', n:'Oktagon', cls:'bd-h-okta'},
    {id:'perisai', n:'Perisai', cls:'bd-h-perisai'},
    {id:'lope', n:'Lope', cls:'bd-h-lope'},
    {id:'kelopak', n:'Kelopak', cls:'bd-h-kelopak'},
    {id:'wajik', n:'Wajik', cls:'bd-h-wajik'},
    {id:'emas', n:'Emas', cls:'bd-o-emas', owner:true},
    {id:'pelangi', n:'Pelangi', cls:'bd-o-pelangi', owner:true},
    {id:'neon', n:'Neon', cls:'bd-o-neon', owner:true},
    {id:'mahkota', n:'Mahkota', cls:'bd-o-emas bd-a-mahkota', owner:true},
    {id:'api', n:'Api', cls:'bd-a-api', owner:true},
    {id:'kilat', n:'Kilat', cls:'bd-a-kilat', owner:true},
    {id:'galaksi', n:'Galaksi', cls:'bd-o-galaksi', owner:true},
    {id:'holo', n:'Holo', cls:'bd-o-holo', owner:true},
    {id:'lava', n:'Lava', cls:'bd-o-lava', owner:true},
    {id:'listrik', n:'Listrik', cls:'bd-o-listrik', owner:true},
    {id:'sayap', n:'Sayap', cls:'bd-a-sayap', owner:true},
    {id:'berlian', n:'Berlian', cls:'bd-a-berlian', owner:true},
    {id:'bintang5', n:'Bintang Emas', cls:'bd-h-bintang5', owner:true},
    {id:'heksaneon', n:'Heksa Neon', cls:'bd-h-heksaneon', owner:true},
    {id:'perisaiemas', n:'Perisai Emas', cls:'bd-h-perisaiemas', owner:true},
    {id:'kelopakpelangi', n:'Kelopak Pelangi', cls:'bd-h-kelopakpelangi', owner:true}
  ];
  var MAIN = ['badgeAvatar','upAvatar','profileAvatarPreview'];
  var cur = 'none', admin = false;

  function find(id){ for (var i=0;i<LIST.length;i++) if (LIST[i].id===id) return LIST[i]; return LIST[0]; }
  function setCls(el, id){
    if (!el) return;
    Array.prototype.slice.call(el.classList).forEach(function(c){ if (c.indexOf('bd-')===0) el.classList.remove(c); });
    var b = find(id);
    if (b.cls) b.cls.split(' ').forEach(function(c){ el.classList.add(c); });
  }
  function applyAll(){ MAIN.forEach(function(id){ setCls(document.getElementById(id), cur); }); }

  /*mz-autosave*/
  async function saveBorder(){
    var user = auth.currentUser;
    if (!user) return;
    var b = find(cur);
    if (b.owner && !admin) return;
    applyAll();
    try {
      await db.collection('users').doc(user.uid).set({avatarBorder: cur}, {merge:true});
      hint('Bingkai disimpan.');
      setTimeout(function(){ hint(''); }, 1600);
    } catch (e) {
      hint('Gagal menyimpan bingkai, coba lagi.');
    }
  }

  function hint(m){
    var h = document.getElementById('bdHint');
    if (!h) return;
    h.textContent = m || '';
    h.style.display = m ? 'block' : 'none';
  }

  function build(){
    var grid = document.getElementById('bdGrid');
    if (!grid) return;
    var ini = ((document.getElementById('profileNameInput') || {}).value || '?').trim().charAt(0).toUpperCase() || '?';
    grid.replaceChildren();
    LIST.forEach(function(b){
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'bd-opt' + (b.id===cur ? ' sel' : '') + ((b.owner && !admin) ? ' lock' : '');
      var dot = document.createElement('span');
      dot.className = 'bd-dot' + (b.cls ? ' ' + b.cls : '');
      dot.textContent = ini;
      var lab = document.createElement('div');
      lab.textContent = b.n + (b.owner ? ' ★' : '');
      btn.append(dot, lab);
      btn.addEventListener('click', function(){
        if (b.owner && !admin) { hint('Bingkai bertanda ★ khusus Owner.'); return; }
        hint('');
        cur = b.id;
        setCls(document.getElementById('profileAvatarPreview'), cur);
        saveBorder();
        build();
      });
      grid.appendChild(btn);
    });
  }

  auth.onAuthStateChanged(async function(user){
    if (!user) { cur = 'none'; admin = false; applyAll(); build(); return; }
    try {
      var doc = await db.collection('users').doc(user.uid).get();
      var d = doc.exists ? doc.data() : {};
      admin = !!d.isAdmin;
      var b = find(d.avatarBorder || 'none');
      cur = (b.owner && !admin) ? 'none' : b.id;
    } catch (e) { cur = 'none'; }
    applyAll();
    build();
  });

  var save = document.getElementById('profileSaveBtn');
  if (save) save.addEventListener('click', async function(){
    var user = auth.currentUser;
    if (!user) return;
    var b = find(cur);
    if (b.owner && !admin) return;
    try {
      await db.collection('users').doc(user.uid).set({avatarBorder: cur}, {merge:true});
      applyAll();
    } catch (e) {}
  });

  var nm = document.getElementById('profileNameInput');
  if (nm) nm.addEventListener('input', build);
})();
