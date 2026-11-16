import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border2' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-border-js"' not in s:
    print('GAGAL: skrip bingkai lama (fix15) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

CSS = r"""
html body [class*="bd-a-"]{position:relative;overflow:visible!important;isolation:isolate;box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) var(--bc,var(--text))}
html body [class*="bd-a-"] img{border-radius:50%}
html body #badgeAvatar{--sz:28px}
html body #upAvatar{--sz:70px}
html body #profileAvatarPreview{--sz:64px}
html body .bd-dot{--sz:38px}
html body :is(.bd-a-bunga,.bd-a-bintang,.bd-a-hati,.bd-a-pita,.bd-a-mahkota,.bd-a-api,.bd-a-kilat)::before,html body :is(.bd-a-bintang,.bd-a-kilat)::after{position:absolute;line-height:1;font-size:calc(var(--sz,40px)*.42);z-index:2;pointer-events:none}
html body .bd-a-kucing{--bc:var(--accent)}
html body .bd-a-kucing::before,html body .bd-a-kucing::after{content:'';position:absolute;top:-14%;width:34%;height:34%;background:var(--bc);clip-path:polygon(0 100%,50% 0,100% 100%);z-index:-1}
html body .bd-a-kucing::before{left:6%;transform:rotate(-12deg)}
html body .bd-a-kucing::after{right:6%;transform:rotate(12deg)}
html body .bd-a-tanduk{--bc:#ef4444}
html body .bd-a-tanduk::before,html body .bd-a-tanduk::after{content:'';position:absolute;top:-18%;width:24%;height:32%;background:#ef4444;clip-path:polygon(0 100%,50% 0,100% 100%);z-index:-1}
html body .bd-a-tanduk::before{left:10%;transform:rotate(-28deg)}
html body .bd-a-tanduk::after{right:10%;transform:rotate(28deg)}
html body .bd-a-halo{--bc:#facc15}
html body .bd-a-halo::before{content:'';position:absolute;left:18%;right:18%;top:-28%;height:18%;border:calc(var(--sz,40px)*.06) solid #facc15;border-radius:50%;box-shadow:0 0 8px #facc15;z-index:2}
html body .bd-a-bunga{--bc:#ec4899}
html body .bd-a-bunga::before{content:'🌸';top:-14%;right:-14%}
html body .bd-a-bintang{--bc:#facc15}
html body .bd-a-bintang::before{content:'✨';top:-14%;right:-14%}
html body .bd-a-bintang::after{content:'✨';bottom:-8%;left:-12%;font-size:calc(var(--sz,40px)*.3)}
html body .bd-a-hati{--bc:#f43f5e}
html body .bd-a-hati::before{content:'💖';top:-14%;right:-14%}
html body .bd-a-pita{--bc:#ec4899}
html body .bd-a-pita::before{content:'🎀';top:-20%;left:-16%;transform:rotate(-20deg)}
html body .bd-a-mahkota{box-shadow:none!important}
html body .bd-a-mahkota::before{content:'👑';left:50%;top:-40%;transform:translateX(-50%);font-size:calc(var(--sz,40px)*.55)}
html body .bd-a-api{--bc:#f97316;animation:mzFlame 1.2s ease-in-out infinite alternate}
html body .bd-a-api::before{content:'🔥';left:50%;top:-36%;transform:translateX(-50%);font-size:calc(var(--sz,40px)*.5)}
html body .bd-a-kilat{--bc:#22d3ee;animation:mzZap 1.4s ease-in-out infinite alternate}
html body .bd-a-kilat::before{content:'⚡';top:-14%;right:-16%}
html body .bd-a-kilat::after{content:'⚡';bottom:-10%;left:-16%;font-size:calc(var(--sz,40px)*.4)}
@keyframes mzFlame{to{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #ef4444,0 0 14px 3px rgba(249,115,22,.7)}}
@keyframes mzZap{to{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #a78bfa,0 0 14px 3px rgba(34,211,238,.7)}}
html body .bd-grid{max-height:46vh;overflow-y:auto;padding:12px 4px 4px}
html body .bd-opt{padding-top:14px}
@media(prefers-reduced-motion:reduce){html body [class*="bd-a-"]{animation:none!important}}
"""

JS = r"""
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
    {id:'emas', n:'Emas', cls:'bd-o-emas', owner:true},
    {id:'pelangi', n:'Pelangi', cls:'bd-o-pelangi', owner:true},
    {id:'neon', n:'Neon', cls:'bd-o-neon', owner:true},
    {id:'mahkota', n:'Mahkota', cls:'bd-o-emas bd-a-mahkota', owner:true},
    {id:'api', n:'Api', cls:'bd-a-api', owner:true},
    {id:'kilat', n:'Kilat', cls:'bd-a-kilat', owner:true}
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
"""

s2, n = re.subn(r'<script id="mz-border-js">.*?</script>', lambda m: '<script id="mz-border-js">' + JS + '</script>', s, count=1, flags=re.S)
if not n:
    print('GAGAL: skrip bingkai tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak19')
s2 = s2.replace('</head>', '<style id="mz-border2">' + CSS + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s2)
print('Bingkai aksesoris : OK')
