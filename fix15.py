import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

CSS = r"""
@property --ang{syntax:'<angle>';inherits:false;initial-value:0deg}
html body #badgeAvatar{--r:1.5px;--r2:2px}
html body [class*="bd-s-"]{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) var(--bc,var(--text))}
html body .bd-s-mono{--bc:var(--text)}
html body .bd-s-biru{--bc:#2563eb}
html body .bd-s-hijau{--bc:#22c55e}
html body .bd-s-pink{--bc:#ec4899}
html body .bd-s-ungu{--bc:#8b5cf6}
html body .bd-s-oranye{--bc:#f97316}
html body .bd-s-ganda{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) var(--text),0 0 0 calc(var(--r,3px)*3) var(--bg),0 0 0 calc(var(--r,3px)*4) var(--text)}
html body .bd-s-putus{box-shadow:none;outline:var(--r,3px) dashed var(--text);outline-offset:calc(var(--r,3px)*1.2)}
html body .bd-o-emas,html body .bd-o-pelangi{border:var(--r2,3px) solid transparent!important;animation:mzSpin 3s linear infinite}
html body .bd-o-emas{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#8a6500,#ffd700,#fff8dc,#ffd700,#8a6500) border-box!important}
html body .bd-o-pelangi{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#ef4444,#f59e0b,#22c55e,#06b6d4,#8b5cf6,#ec4899,#ef4444) border-box!important}
html body .bd-o-neon{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #22d3ee,0 0 14px 4px rgba(34,211,238,.6);animation:mzPulse 1.6s ease-in-out infinite alternate}
@keyframes mzSpin{to{--ang:360deg}}
@keyframes mzPulse{to{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #ec4899,0 0 16px 5px rgba(236,72,153,.6)}}
html body .bd-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
html body .bd-opt{background:none;border:none;color:var(--text);font:inherit;font-size:.68rem;cursor:pointer;padding:8px 2px;text-align:center;border-radius:10px}
html body .bd-opt.sel{background:var(--card);outline:1px solid var(--accent)}
html body .bd-opt.lock{opacity:.45}
html body .bd-dot{width:38px;height:38px;border-radius:50%;background:var(--accent);color:var(--on);display:flex;align-items:center;justify-content:center;font-weight:800;margin:0 auto 8px;--r:2px;--r2:3px}
html body .mz-rv{opacity:0;transform:translateY(26px) scale(.98);transition:opacity .6s ease,transform .6s cubic-bezier(.2,.7,.2,1)}
html body .mz-rv.mz-in{opacity:1;transform:none}
html body .tab.active{animation:mzTab .4s ease}
@keyframes mzTab{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
html body header{transition:box-shadow .3s ease}
html body.mz-scrolled header{box-shadow:0 6px 18px var(--shadow)}
@media(prefers-reduced-motion:reduce){html body .mz-rv{opacity:1!important;transform:none!important;transition:none!important}html body .tab.active,html body [class*="bd-o-"]{animation:none!important}}
"""

PICKER = r"""<div id="bdPicker" style="display:flex;flex-direction:column;gap:8px">
<p class="muted" style="margin:0;font-size:.85rem;font-weight:700">Bingkai Avatar</p>
<div class="bd-grid" id="bdGrid"></div>
<p class="muted" id="bdHint" style="margin:0;font-size:.78rem;display:none"></p>
</div>
"""

JS_BORDER = r"""
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
    {id:'emas', n:'Emas', cls:'bd-o-emas', owner:true},
    {id:'pelangi', n:'Pelangi', cls:'bd-o-pelangi', owner:true},
    {id:'neon', n:'Neon', cls:'bd-o-neon', owner:true}
  ];
  var MAIN = ['badgeAvatar','upAvatar','profileAvatarPreview'];
  var cur = 'none', admin = false;

  function find(id){ for (var i=0;i<LIST.length;i++) if (LIST[i].id===id) return LIST[i]; return LIST[0]; }
  function setCls(el, id){
    if (!el) return;
    Array.prototype.slice.call(el.classList).forEach(function(c){ if (c.indexOf('bd-')===0) el.classList.remove(c); });
    var b = find(id);
    if (b.cls) el.classList.add(b.cls);
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
      var id = d.avatarBorder || 'none';
      var b = find(id);
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

JS_ANIM = r"""
(function(){
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sel = '.profile-card,.banner,.about-block,.title,.project,.skill,.contact-block,.tool-card';
  var els = document.querySelectorAll(sel);
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting) { e.target.classList.add('mz-in'); io.unobserve(e.target); }
      });
    }, {threshold:.12, rootMargin:'0px 0px -6% 0px'});
    els.forEach(function(el){
      var idx = Array.prototype.indexOf.call(el.parentNode.children, el);
      el.style.transitionDelay = ((idx % 4) * 70) + 'ms';
      el.classList.add('mz-rv');
      io.observe(el);
    });
  }
  var ticking = false;
  window.addEventListener('scroll', function(){
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function(){
      document.body.classList.toggle('mz-scrolled', window.scrollY > 8);
      ticking = false;
    });
  }, {passive:true});
})();
"""

s, n = re.subn(r'(<button[^>]*id="profileSaveBtn")', lambda m: PICKER + m.group(1), s, count=1)
if not n:
    print('Picker : GAGAL (tombol Simpan Profil tidak ketemu). Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak15')
s = s.replace('</head>', '<style id="mz-border">' + CSS + '</style>\n</head>', 1)
i = s.rfind('</body>')
ok = i != -1
if ok:
    s = s[:i] + '<script id="mz-border-js">' + JS_BORDER + '</script>\n<script id="mz-anim-js">' + JS_ANIM + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Picker  : OK')
print('Style   : OK')
print('Script  :', 'OK' if ok else 'GAGAL')
