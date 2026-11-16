import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-settings-boot' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

NAV = r'''<button class="nav-btn" data-tab="tab-pengaturan"><span><svg viewBox="0 0 24 24" class="icon"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></span>Pengaturan</button>'''

SECTION = r'''<section class="tab" id="tab-pengaturan">
  <h2 class="title">Pengaturan</h2>
  <div class="profile-card">
    <h3 style="margin:0 0 4px">Tema Warna</h3>
    <p class="muted" style="margin:0 0 14px;font-size:.85rem">Pilih warna aksen untuk tombol dan penanda.</p>
    <div class="mz-sw-grid" id="mzSwatches"></div>
  </div>
  <div class="profile-card">
    <h3 style="margin:0 0 4px">Font</h3>
    <p class="muted" style="margin:0 0 14px;font-size:.85rem">Pilih gaya huruf yang nyaman dibaca.</p>
    <div class="mz-fo-list" id="mzFonts"></div>
  </div>
  <button class="btn" id="mzReset" type="button">Kembalikan ke Bawaan</button>
  <p class="muted" style="font-size:.8rem;margin-top:10px">Pengaturan disimpan di perangkat ini.</p>
</section>
'''

CSS = r'''
html body .mz-sw-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
html body .mz-sw{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:10px 4px;color:var(--text);font:inherit;font-size:.7rem;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:6px}
html body .mz-sw.sel,html body .mz-fo.sel{outline:2px solid var(--text);outline-offset:1px}
html body .mz-dot{width:30px;height:30px;border-radius:50%;border:1px solid var(--line)}
html body .mz-fo-list{display:flex;flex-direction:column;gap:8px}
html body .mz-fo{text-align:left;background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:12px 14px;color:var(--text);cursor:pointer;font:inherit}
html body .mz-fo b{display:block;font-size:1rem}
html body .mz-fo small{display:block;color:var(--muted);margin-top:2px}
'''

HEAD_JS = r'''
(function(){
  var KEY = 'mz_settings';
  var THEMES = [
    {id:'mono', n:'Hitam/Putih'},
    {id:'biru', n:'Biru', l:'#2563eb', d:'#3b82f6', ol:'#fff', od:'#fff'},
    {id:'hijau', n:'Hijau', l:'#16a34a', d:'#22c55e', ol:'#fff', od:'#0a0a0a'},
    {id:'kuning', n:'Kuning', l:'#eab308', d:'#facc15', ol:'#0a0a0a', od:'#0a0a0a'},
    {id:'pink', n:'Pink', l:'#ec4899', d:'#f472b6', ol:'#fff', od:'#0a0a0a'},
    {id:'ungu', n:'Ungu', l:'#7c3aed', d:'#a78bfa', ol:'#fff', od:'#0a0a0a'},
    {id:'oranye', n:'Oranye', l:'#ea580c', d:'#fb923c', ol:'#fff', od:'#0a0a0a'}
  ];
  var FONTS = [
    {id:'bawaan', n:'Bawaan', css:''},
    {id:'poppins', n:'Poppins', css:"'Poppins',sans-serif", gf:'Poppins:wght@400;600;800'},
    {id:'nunito', n:'Nunito', css:"'Nunito',sans-serif", gf:'Nunito:wght@400;700;900'},
    {id:'space', n:'Space Grotesk', css:"'Space Grotesk',sans-serif", gf:'Space+Grotesk:wght@400;600;700'},
    {id:'merri', n:'Merriweather', css:"'Merriweather',serif", gf:'Merriweather:wght@400;700;900'},
    {id:'kode', n:'JetBrains Mono', css:"'JetBrains Mono',monospace", gf:'JetBrains+Mono:wght@400;700;800'}
  ];

  function find(list, id){
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return list[0];
  }

  var state = {theme:'mono', font:'bawaan'};
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (saved.theme) state.theme = find(THEMES, saved.theme).id;
    if (saved.font) state.font = find(FONTS, saved.font).id;
  } catch (e) {}

  function build(st){
    var t = find(THEMES, st.theme), f = find(FONTS, st.font), out = '';
    if (t.l) {
      out += 'html[data-mz-accent] body:not(.light-mode){--accent:' + t.d + ';--purple:' + t.d + ';--gold:' + t.d + ';--on:' + t.od + '}';
      out += 'html[data-mz-accent] body.light-mode{--accent:' + t.l + ';--purple:' + t.l + ';--gold:' + t.l + ';--on:' + t.ol + '}';
    }
    if (f.css) {
      out += 'html[data-mz-font] body,html[data-mz-font] body button:not(.mz-fo),html[data-mz-font] body input,html[data-mz-font] body textarea{font-family:' + f.css + '!important}';
    }
    return out;
  }

  function apply(doc, st){
    if (!doc || !doc.documentElement) return;
    var h = doc.documentElement;
    var t = find(THEMES, st.theme), f = find(FONTS, st.font);
    if (t.l) h.setAttribute('data-mz-accent', t.id); else h.removeAttribute('data-mz-accent');
    if (f.css) h.setAttribute('data-mz-font', f.id); else h.removeAttribute('data-mz-font');
    var head = doc.head || h;
    var el = doc.getElementById('mz-user-css');
    if (!el) { el = doc.createElement('style'); el.id = 'mz-user-css'; head.appendChild(el); }
    el.textContent = build(st);
    var lk = doc.getElementById('mz-user-font');
    if (f.gf) {
      var href = 'https://fonts.googleapis.com/css2?family=' + f.gf + '&display=swap';
      if (!lk) { lk = doc.createElement('link'); lk.id = 'mz-user-font'; lk.rel = 'stylesheet'; head.appendChild(lk); }
      if (lk.getAttribute('href') !== href) lk.setAttribute('href', href);
    } else if (lk) {
      lk.remove();
    }
  }

  window.mzSettings = {
    THEMES: THEMES,
    FONTS: FONTS,
    get: function(){ return {theme: state.theme, font: state.font}; },
    set: function(p){
      if (p.theme) state.theme = find(THEMES, p.theme).id;
      if (p.font) state.font = find(FONTS, p.font).id;
      try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
      apply(document, state);
      try {
        var fr = document.getElementById('toolFrame');
        if (fr && fr.contentDocument) apply(fr.contentDocument, state);
      } catch (e) {}
    },
    applyTo: function(doc){ apply(doc, state); }
  };

  apply(document, state);
})();
'''

BODY_JS = r'''
(function(){
  var S = window.mzSettings;
  if (!S) return;
  var sw = document.getElementById('mzSwatches');
  var fo = document.getElementById('mzFonts');
  var rs = document.getElementById('mzReset');
  if (!sw || !fo) return;

  var previewLoaded = false;
  function loadPreview(){
    if (previewLoaded) return;
    previewLoaded = true;
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = 'https://fonts.googleapis.com/css2?family=Poppins:wght@600&family=Nunito:wght@700&family=Space+Grotesk:wght@600&family=Merriweather:wght@700&family=JetBrains+Mono:wght@700&display=swap';
    document.head.appendChild(l);
  }

  function render(){
    var st = S.get();
    sw.replaceChildren();
    S.THEMES.forEach(function(t){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'mz-sw' + (t.id === st.theme ? ' sel' : '');
      var dot = document.createElement('span');
      dot.className = 'mz-dot';
      dot.style.background = t.l ? t.l : 'linear-gradient(135deg,#0a0a0a 50%,#f5f5f5 50%)';
      var lb = document.createElement('span');
      lb.textContent = t.n;
      b.append(dot, lb);
      b.addEventListener('click', function(){ S.set({theme: t.id}); render(); });
      sw.appendChild(b);
    });

    fo.replaceChildren();
    S.FONTS.forEach(function(f){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'mz-fo' + (f.id === st.font ? ' sel' : '');
      var name = document.createElement('b');
      name.textContent = f.n;
      var sm = document.createElement('small');
      sm.textContent = 'Aa Bb Cc 123 - Santai dulu, main game.';
      if (f.css) { name.style.fontFamily = f.css; sm.style.fontFamily = f.css; }
      b.append(name, sm);
      b.addEventListener('click', function(){ S.set({font: f.id}); render(); });
      fo.appendChild(b);
    });
  }

  if (rs) rs.addEventListener('click', function(){ S.set({theme: 'mono', font: 'bawaan'}); render(); });

  document.querySelectorAll('[data-tab="tab-pengaturan"]').forEach(function(b){
    b.addEventListener('click', loadPreview);
  });

  var fr = document.getElementById('toolFrame');
  if (fr) fr.addEventListener('load', function(){
    try { S.applyTo(fr.contentDocument); } catch (e) {}
  });

  render();
})();
'''

m = re.search(r'<button class="nav-btn" data-tab="tab-alat">.*?</button>', s, re.S)
ok_main = '</main>' in s
ok_head = '</head>' in s
ok_body = s.rfind('</body>') != -1
print('Menu Alat ketemu :', 'OK' if m else 'GAGAL')
print('main/head/body   :', 'OK' if (ok_main and ok_head and ok_body) else 'GAGAL')
if not (m and ok_main and ok_head and ok_body):
    print('Dibatalkan, tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak18')
s = s[:m.end()] + '\n' + NAV + s[m.end():]
s = s.replace('</main>', SECTION + '</main>', 1)
s = s.replace('</head>', '<style id="mz-settings-css">' + CSS + '</style>\n<script id="mz-settings-boot">' + HEAD_JS + '</script>\n</head>', 1)
i = s.rfind('</body>')
s = s[:i] + '<script id="mz-settings-ui">' + BODY_JS + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Pengaturan       : OK')
