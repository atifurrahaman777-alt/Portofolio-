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
