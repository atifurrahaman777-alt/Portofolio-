(function(){
  var KEY = 'mz_settings';
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
    if (window.mzApplyTheme) window.mzApplyTheme();
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
