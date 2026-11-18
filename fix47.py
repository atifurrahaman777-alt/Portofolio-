import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'id="mz-tech-boot"' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-settings-boot"' not in s:
    print('GAGAL: menu Pengaturan (fix18) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit
MARK = '<button class="btn" id="mzReset"'
if s.count(MARK) != 1 or '</head>' not in s or s.rfind('</body>') == -1:
    print('GAGAL: struktur Pengaturan tidak cocok. Tidak ada yang diubah.')
    raise SystemExit

CARD = """<div class="profile-card" id="mzTechCard">
    <h3 style="margin:0 0 4px">Gaya Judul (Tech)</h3>
    <p class="muted" style="margin:0 0 14px;font-size:.85rem">Font futuristik untuk judul, menu, dan tombol, seperti tampilan dashboard gelap.</p>
    <div class="mz-fo-list" id="mzTechList"></div>
    <label class="mz-tech-up"><input type="checkbox" id="mzTechUp"> Judul huruf kapital</label>
  </div>
  """

CSS = """
html body .mz-tech-up{display:flex;align-items:center;gap:10px;margin-top:14px;font-size:.9rem;cursor:pointer}
html body .mz-tech-up input{width:20px;height:20px;accent-color:var(--accent)}
"""

HEAD_JS = r"""
(function(){
  var KEY = 'mz_tech';
  var FONTS = {
    orbitron: { n: 'Orbitron', css: "'Orbitron',sans-serif", gf: 'Orbitron:wght@500;700;900' },
    michroma: { n: 'Michroma', css: "'Michroma',sans-serif", gf: 'Michroma' },
    audiowide: { n: 'Audiowide', css: "'Audiowide',sans-serif", gf: 'Audiowide' },
    oxanium: { n: 'Oxanium', css: "'Oxanium',sans-serif", gf: 'Oxanium:wght@500;700;800' }
  };
  var SEL = 'h1,h2,h3,.brand,.logo,.title,.eyebrow,.banner-title,.pf-name,.profile-name,.nav-btn,.btn,.mz-sl,.stat span,.pf-stats span,.pf-tabs button,.mzs-tabs button,.mzs-head b,.pf-sheet-head b';
  var UPS = 'h1,h2,h3,.brand,.logo,.title,.eyebrow,.banner-title,.nav-btn,.btn,.mz-sl,.stat span,.pf-stats span,.pf-tabs button,.mzs-tabs button';
  var P = 'html[data-mz-tech] body:not(#mz_) ';
  var st = { f: '', up: 1 };
  try {
    var v = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (v.f && FONTS[v.f]) st.f = v.f;
    if (v.up === 0) st.up = 0;
  } catch (e) {}

  function pre(list){ return list.split(',').map(function(x){ return P + x; }).join(','); }
  function build(s){
    var f = FONTS[s.f];
    if (!f) return '';
    var out = pre(SEL) + '{font-family:' + f.css + '!important;letter-spacing:.06em}';
    if (s.up) out += pre(UPS) + '{text-transform:uppercase}';
    return out;
  }
  function apply(doc, s){
    if (!doc || !doc.documentElement) return;
    var h = doc.documentElement, f = FONTS[s.f], head = doc.head || h;
    if (f) h.setAttribute('data-mz-tech', s.f); else h.removeAttribute('data-mz-tech');
    var el = doc.getElementById('mz-tech-css');
    if (!el) { el = doc.createElement('style'); el.id = 'mz-tech-css'; head.appendChild(el); }
    el.textContent = build(s);
    var lk = doc.getElementById('mz-tech-font');
    if (f) {
      var href = 'https://fonts.googleapis.com/css2?family=' + f.gf + '&display=swap';
      if (!lk) { lk = doc.createElement('link'); lk.id = 'mz-tech-font'; lk.rel = 'stylesheet'; head.appendChild(lk); }
      if (lk.getAttribute('href') !== href) lk.setAttribute('href', href);
    } else if (lk) {
      lk.remove();
    }
  }
  window.mzTech = {
    FONTS: FONTS,
    get: function(){ return { f: st.f, up: st.up }; },
    set: function(p){
      if (p.f !== undefined) st.f = FONTS[p.f] ? p.f : '';
      if (p.up !== undefined) st.up = p.up ? 1 : 0;
      try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
      apply(document, st);
      try {
        var fr = document.getElementById('toolFrame');
        if (fr && fr.contentDocument) apply(fr.contentDocument, st);
      } catch (e) {}
    },
    applyTo: function(doc){ apply(doc, st); }
  };
  apply(document, st);
})();
"""

BODY_JS = r"""
(function(){
  var T = window.mzTech;
  if (!T) return;
  var list = document.getElementById('mzTechList');
  var up = document.getElementById('mzTechUp');
  if (!list || !up) return;
  var loaded = false;
  function preload(){
    if (loaded) return;
    loaded = true;
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Michroma&family=Audiowide&family=Oxanium:wght@700&display=swap';
    document.head.appendChild(l);
  }
  function render(){
    var st = T.get();
    list.replaceChildren();
    var opts = [{ id: '', n: 'Mati (bawaan)', css: '' }].concat(Object.keys(T.FONTS).map(function(k){
      return { id: k, n: T.FONTS[k].n, css: T.FONTS[k].css };
    }));
    opts.forEach(function(o){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'mz-fo' + (o.id === st.f ? ' sel' : '');
      var nm = document.createElement('b');
      nm.textContent = o.n;
      var sm = document.createElement('small');
      sm.textContent = 'MULTIFUNGSI \u00b7 05:30 \u00b7 Good Morning';
      if (o.css) { nm.style.fontFamily = o.css; sm.style.fontFamily = o.css; }
      b.append(nm, sm);
      b.addEventListener('click', function(){ T.set({ f: o.id }); render(); });
      list.appendChild(b);
    });
    up.checked = !!st.up;
  }
  up.addEventListener('change', function(){ T.set({ up: up.checked }); });
  document.querySelectorAll('[data-tab="tab-pengaturan"]').forEach(function(b){ b.addEventListener('click', preload); });
  var rs = document.getElementById('mzReset');
  if (rs) rs.addEventListener('click', function(){ T.set({ f: '', up: 1 }); render(); });
  var fr = document.getElementById('toolFrame');
  if (fr) fr.addEventListener('load', function(){ try { T.applyTo(fr.contentDocument); } catch (e) {} });
  render();
})();
"""

shutil.copy(f, f + '.bak47')
s = s.replace(MARK, CARD + MARK, 1)
s = s.replace('</head>', '<style id="mz-tech-ui-css">' + CSS + '</style>\n<script id="mz-tech-boot">' + HEAD_JS + '</script>\n</head>', 1)
j = s.rfind('</body>')
s = s[:j] + '<script id="mz-tech-ui">' + BODY_JS + '</script>\n' + s[j:]
open(f, 'w', encoding='utf-8').write(s)
print('Gaya Judul (Tech) : OK')
