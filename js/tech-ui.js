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
