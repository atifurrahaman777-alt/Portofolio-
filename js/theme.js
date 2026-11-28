(function(){
  var KEY='mz_settings';
  var TECH_KEY='mz_tech';
  var THEMES = [
    {id:'mono', n:'Hitam/Putih', l:'#374151', d:'#cbd5e1', ol:'#ffffff', od:'#0b0d14'},
    {id:'biru', n:'Biru', l:'#1d4ed8', d:'#9dc0ff', ol:'#ffffff', od:'#0b0d14'},
    {id:'hijau', n:'Hijau', l:'#18794e', d:'#85d2a7', ol:'#ffffff', od:'#0b0d14'},
    {id:'kuning', n:'Kuning', l:'#8a5a06', d:'#e6c26b', ol:'#ffffff', od:'#0b0d14'},
    {id:'pink', n:'Pink', l:'#a51856', d:'#efa0c4', ol:'#ffffff', od:'#0b0d14'},
    {id:'oranye', n:'Oranye', l:'#b54708', d:'#f0ad7d', ol:'#ffffff', od:'#0b0d14'}
  ];
  var FONTS = [
    {id:'bawaan', n:'Bawaan', css:''},
    {id:'poppins', n:'Poppins', css:"'Poppins',sans-serif", gf:'Poppins:wght@400;600;800'},
    {id:'nunito', n:'Nunito', css:"'Nunito',sans-serif", gf:'Nunito:wght@400;700;900'},
    {id:'space', n:'Space Grotesk', css:"'Space Grotesk',sans-serif", gf:'Space+Grotesk:wght@400;600;700'},
    {id:'merri', n:'Merriweather', css:"'Merriweather',sans-serif", gf:'Merriweather:wght@400;700;900'},
    {id:'kode', n:'JetBrains Mono', css:"'JetBrains Mono',monospace", gf:'JetBrains+Mono:wght@400;700;800'}
  ];
  var TECH_FONTS = {
    orbitron: { n: 'Orbitron', css: "'Orbitron',sans-serif", gf: 'Orbitron:wght@500;700;900' },
    michroma: { n: 'Michroma', css: "'Michroma',sans-serif", gf: 'Michroma' },
    audiowide: { n: 'Audiowide', css: "'Audiowide',sans-serif", gf: 'Audiowide' },
    oxanium: { n: 'Oxanium', css: "'Oxanium',sans-serif", gf: 'Oxanium:wght@500;700;800' }
  };

  function find(list, id){ for (var i=0;i<list.length;i++) if (list[i].id===id) return list[i]; return list[0]; }

  var state = {theme:'mono', font:'bawaan', techFont:'', techUpper:1};
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (saved.theme) state.theme = find(THEMES, saved.theme).id;
    if (saved.font) state.font = find(FONTS, saved.font).id;
    state.techFont = (saved.techFont && TECH_FONTS[saved.techFont]) ? saved.techFont : '';
    state.techUpper = saved.techUp === undefined ? 1 : !!saved.techUp;
  } catch (e) {}
  try {
    var tv = JSON.parse(localStorage.getItem(TECH_KEY) || '{}');
    if (tv.f && TECH_FONTS[tv.f]) state.techFont = tv.f;
    if (tv.up === 0) state.techUpper = 0;
  } catch (e) {}

  function buildThemeCSS(st){
    var t = find(THEMES, st.theme), f = find(FONTS, st.font), out = '';
    if (f.css) out += 'html[data-mz-font] body,html[data-mz-font] body button:not(.mz-fo),html[data-mz-font] body input,html[data-mz-font] body textarea{font-family:' + f.css + '!important}';
    return out;
  }
  function buildTechCSS(s){
    var f = TECH_FONTS[s.f];
    if (!f) return '';
    var SEL = 'h1,h2,h3,.brand,.logo,.title,.eyebrow,.banner-title,.pf-name,.profile-name,.nav-btn,.btn,.mz-sl,.stat span,.pf-stats span,.pf-tabs button,.mzs-tabs button,.mzs-head b,.pf-sheet-head b';
    var UPS = 'h1,h2,h3,.brand,.logo,.title,.eyebrow,.banner-title,.nav-btn,.btn,.mz-sl,.stat span,.pf-stats span,.pf-tabs button,.mzs-tabs button,.mzs-head b,.pf-sheet-head b';
    var P = 'html[data-mz-tech] body:not(#mz_) ';
    var out = pre(SEL) + '{font-family:' + f.css + '!important;letter-spacing:.06em}';
    if (s.up) out += pre(UPS) + '{text-transform:uppercase}';
    return out;
  }
  function pre(list){ return list.split(',').map(function(x){ return 'html[data-mz-tech] body:not(#mz_) ' + x; }).join(','); }

  function applyDoc(doc, full){
    if (!doc || !doc.documentElement) return;
    var h = doc.documentElement;
    var t = find(THEMES, full.theme), f = find(FONTS, full.font);
    if (t.l) h.setAttribute('data-mz-accent', t.id); else h.removeAttribute('data-mz-accent');
    if (f.css) h.setAttribute('data-mz-font', f.id); else h.removeAttribute('data-mz-font');
    var head = doc.head || h;
    var el = doc.getElementById('mz-user-css');
    if (!el) { el = doc.createElement('style'); el.id = 'mz-user-css'; head.appendChild(el); }
    el.textContent = buildThemeCSS(full);
    if (window.mzApplyTheme) window.mzApplyTheme();
    var lk = doc.getElementById('mz-user-font');
    if (f.gf) {
      var href = 'https://fonts.googleapis.com/css2?family=' + f.gf + '&display=swap';
      if (!lk) { lk = doc.createElement('link'); lk.id = 'mz-user-font'; lk.rel = 'stylesheet'; head.appendChild(lk); }
      if (lk.getAttribute('href') !== href) lk.setAttribute('href', href);
    } else if (lk) { lk.remove(); }
    var th = doc.getElementById('mz-tech-css');
    if (!th) { th = doc.createElement('style'); th.id = 'mz-tech-css'; head.appendChild(th); }
    th.textContent = buildTechCSS({f: full.techFont, up: full.techUpper});
    var tlk = doc.getElementById('mz-tech-font');
    var tf = TECH_FONTS[full.techFont];
    if (tf) {
      var href2 = 'https://fonts.googleapis.com/css2?family=' + tf.gf + '&display=swap';
      if (!tlk) { tlk = doc.createElement('link'); tlk.id = 'mz-tech-font'; tlk.rel = 'stylesheet'; head.appendChild(tlk); }
      if (tlk.getAttribute('href') !== href2) tlk.setAttribute('href', href2);
    } else if (tlk) { tlk.remove(); }
  }

  function applyFull(doc){
    if (!doc || !doc.documentElement) return;
    applyDoc(doc, {theme: state.theme, font: state.font, techFont: state.techFont, techUpper: state.techUpper});
    if (window.mzApplyTheme) window.mzApplyTheme();
  }

  window.mzSettings = {
    THEMES: THEMES,
    FONTS: FONTS,
    get: function(){ return {theme: state.theme, font: state.font}; },
    set: function(p){
      if (p.theme) state.theme = find(THEMES, p.theme).id;
      if (p.font) state.font = find(FONTS, p.font).id;
      try { localStorage.setItem(KEY, JSON.stringify({theme: state.theme, font: state.font})); } catch (e) {}
      applyFull(document);
      try {
        var fr = document.getElementById('toolFrame');
        if (fr && fr.contentDocument) applyFull(fr.contentDocument);
      } catch (e) {}
    },
    applyTo: function(doc){ applyFull(doc); }
  };

  window.mzTech = {
    FONTS: TECH_FONTS,
    get: function(){ return { f: state.techFont, up: !!state.techUpper }; },
    set: function(p){
      if (p.f !== undefined) state.techFont = TECH_FONTS[p.f] ? p.f : '';
      if (p.up !== undefined) state.techUpper = !!p.up;
      try { localStorage.setItem(TECH_KEY, JSON.stringify({f: state.techFont, up: state.techUpper})); } catch (e) {}
      applyFull(document);
      try {
        var fr = document.getElementById('toolFrame');
        if (fr && fr.contentDocument) applyFull(fr.contentDocument);
      } catch (e) {}
    },
    applyTo: function(doc){ applyFull(doc); }
  };

  function mzApplyTheme(){
    var t = state.theme, h=document.documentElement, b=document.body, mode;
    h.setAttribute('data-mz-accent',t);
    if(b){
      try{mode=localStorage.getItem('mz-theme');}catch(e){}
      b.classList.toggle('light-mode',mode!=='dark');
    }
    return t;
  }
  window.mzApplyTheme = mzApplyTheme;
  window.mzSettings.applyTo = applyFull;

  try { applyFull(document); } catch (e) {}
  document.addEventListener('DOMContentLoaded', function(){ try { applyFull(document); } catch(e){} });
})();
