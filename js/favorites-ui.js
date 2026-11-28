(function(){
  var tabs = document.querySelector('.pf-tabs');
  var lenc = document.getElementById('pf-lencana');
  var tent = document.getElementById('pf-tentang');
  if (!tabs || !lenc || !tent) return;
  var HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.dataset.pt = 'fav';
  btn.textContent = 'Favorit';
  tabs.appendChild(btn);
  var panel = document.createElement('div');
  panel.id = 'pf-fav';
  panel.hidden = true;
  panel.innerHTML = '<p class="pf-fav-note" id="pfFavNote"></p><div id="pfFavList"></div>';
  lenc.parentNode.insertBefore(panel, lenc.nextSibling);

  function render(){
    var list = window.mzFavs || [];
    var box = document.getElementById('pfFavList');
    document.getElementById('pfFavNote').textContent = list.length
      ? list.length + ' lagu favorit. Ketuk lagu untuk memutar.'
      : 'Belum ada favorit. Ketuk ikon hati di pemutar Musik untuk menyimpan lagu di sini.';
    box.replaceChildren();
    list.forEach(function(t, i){
      var row = document.createElement('div');
      row.className = 'pf-fav-row';
      var main = document.createElement('button');
      main.type = 'button';
      main.className = 'pf-fav-main';
      var pic;
      if (/^https:\/\//.test(t.art || '')) { pic = document.createElement('img'); pic.alt = ''; pic.src = t.art; pic.loading = 'lazy'; }
      else { pic = document.createElement('span'); pic.className = 'ph'; }
      var info = document.createElement('span');
      info.className = 'pf-fav-it';
      var tt = document.createElement('b'); tt.textContent = t.title;
      var ar = document.createElement('small'); ar.textContent = (t.artist || '-') + ' \u00b7 ' + (t.src === 'yt' ? 'YouTube' : 'Audius');
      info.append(tt, ar);
      main.append(pic, info);
      main.addEventListener('click', function(){ if (window.mzMusic) window.mzMusic.play(list, i); });
      var rm = document.createElement('button');
      rm.type = 'button';
      rm.className = 'pf-fav-rm';
      rm.setAttribute('aria-label', 'Hapus dari favorit');
      rm.innerHTML = HEART;
      rm.addEventListener('click', function(){ if (window.mzMusic) window.mzMusic.toggleFav(t); });
      row.append(main, rm);
      box.appendChild(row);
    });
  }

  document.querySelectorAll('[data-pt]').forEach(function(b){
    b.addEventListener('click', function(){
      if (b.dataset.pt === 'fav') {
        document.querySelectorAll('[data-pt]').forEach(function(x){ x.classList.toggle('on', x === b); });
        tent.hidden = true;
        lenc.hidden = true;
        panel.hidden = false;
        render();
      } else {
        document.querySelectorAll('[data-pt]').forEach(function(x){ x.classList.toggle('on', x === b); });
        tent.hidden = b.dataset.pt !== 'tentang';
        lenc.hidden = b.dataset.pt !== 'lencana';
        panel.hidden = true;
        render();
      }
    });
  });
  window.addEventListener('mzfavs', function(){ if (!panel.hidden) render(); });
})();
