import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'id="mz-favui-js"' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-music-js"' not in s or 'id="mz-profile2-js"' not in s:
    print('GAGAL: fitur musik (fix43) atau profil baru (fix33) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

A_BUILD = "  function build(){\n    if (S.built) return;\n"
A_MINI = "+ '<button type=\"button\" class=\"mzm-b\" id=\"mzClose\" aria-label=\"Tutup pemutar\"></button>';"
A_CLOSE = "$('mzClose').innerHTML = IX;"
A_SHOW = "$('mzNext').style.display = S.mode === 'audius' ? '' : 'none';"
A_LIST = "b.append(pic, info, d);"
A_YT = "if (e.data === 0) { $('mzBar').style.width = '0'; }"
A_END = "    renderList();\n  }\n})();"

for a in (A_BUILD, A_MINI, A_CLOSE, A_SHOW, A_LIST, A_YT, A_END):
    if s.count(a) != 1:
        print('GAGAL: bagian pemutar tidak cocok dengan versi yang gw tahu (' + a[:40].strip() + '...). Tidak ada yang diubah.')
        raise SystemExit

FAV = r"""  var HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 21s-7.5-4.6-10-9.3C.5 8 2.4 4.5 6 4.5c2 0 3.6 1.1 4.5 2.8C11.4 5.6 13 4.5 15 4.5c3.6 0 5.5 3.5 4 7.2C19.5 16.4 12 21 12 21z"/></svg>';
  var favs = [];
  var favUnsub = null;
  function isFav(id){ return favs.some(function(f){ return f.id === id; }); }
  function cleanFav(t){
    var id = String((t && t.id) || '');
    if (!/^[A-Za-z0-9_-]{1,24}$/.test(id)) return null;
    return {
      src: t.src === 'yt' ? 'yt' : 'audius',
      id: id,
      title: String(t.title || 'Tanpa judul').slice(0, 100),
      artist: String(t.artist || '').slice(0, 60),
      art: safeImg(t.art) ? String(t.art).slice(0, 300) : '',
      dur: parseInt(t.dur, 10) || 0
    };
  }
  function fireFavs(){
    window.mzFavs = favs;
    if (S.built) { try { renderList(); syncFavBtn(); } catch (e) {} }
    window.dispatchEvent(new Event('mzfavs'));
  }
  async function toggleFav(t){
    var u = (typeof auth !== 'undefined') ? auth.currentUser : null;
    if (!u) { if (window.mzNeedLogin) window.mzNeedLogin('Masuk dulu untuk menyimpan lagu favorit.'); return; }
    var c = cleanFav(t);
    if (!c) return;
    var prev = favs;
    var list = favs.filter(function(f){ return f.id !== c.id; });
    if (list.length === favs.length) {
      if (list.length >= 50) { if (S.built) stat('Favorit penuh (maks 50).'); return; }
      list.unshift(c);
    }
    favs = list;
    fireFavs();
    try {
      await db.collection('users').doc(u.uid).set({ favorites: list }, { merge: true });
    } catch (e) {
      favs = prev;
      fireFavs();
      if (S.built) stat('Gagal menyimpan favorit.');
    }
  }
  function curItem(){
    if (S.mode === 'audius' && S.queue[S.idx]) {
      var t = S.queue[S.idx];
      return { src: 'audius', id: t.id, title: t.title, artist: t.artist, art: t.art, dur: t.dur };
    }
    if (S.mode === 'yt' && S.yt && S.yt.getVideoData) {
      try {
        var d = S.yt.getVideoData();
        if (d && d.video_id) return { src: 'yt', id: d.video_id, title: d.title || 'YouTube', artist: d.author || 'YouTube', art: 'https://i.ytimg.com/vi/' + d.video_id + '/mqdefault.jpg', dur: 0 };
      } catch (e) {}
    }
    return null;
  }
  function favCurrent(){ var t = curItem(); if (t) toggleFav(t); }
  function syncFavBtn(){
    var b = $('mzFav');
    if (!b) return;
    var t = curItem();
    b.classList.toggle('on', !!(t && isFav(t.id)));
    b.style.display = t ? '' : 'none';
  }
  function watchFavs(){
    if (typeof auth === 'undefined' || typeof db === 'undefined') return;
    auth.onAuthStateChanged(function(u){
      if (favUnsub) { favUnsub(); favUnsub = null; }
      favs = [];
      fireFavs();
      if (!u) return;
      favUnsub = db.collection('users').doc(u.uid).onSnapshot(function(snap){
        var arr = snap.exists ? (snap.data().favorites || []) : [];
        favs = arr.map(cleanFav).filter(Boolean);
        fireFavs();
      }, function(){});
    });
  }

"""

LISTBTN = r"""var hs = document.createElement('span');
      hs.className = 'mzs-fav' + (isFav(t.id) ? ' on' : '');
      hs.setAttribute('role', 'button');
      hs.setAttribute('aria-label', 'Favorit');
      hs.innerHTML = HEART;
      hs.addEventListener('click', function(e){
        e.stopPropagation();
        toggleFav({ src: 'audius', id: t.id, title: t.title, artist: t.artist, art: t.art, dur: t.dur });
      });
      b.append(pic, info, d, hs);"""

EXPOSE = r"""    renderList();
  }
  window.mzMusic = {
    play: function(list, i){
      build();
      var it = list[i];
      if (!it) return;
      if (it.src === 'yt') { playYt(it.id); return; }
      S.queue = list.filter(function(x){ return x.src !== 'yt'; });
      S.idx = S.queue.findIndex(function(x){ return x.id === it.id; });
      if (S.idx < 0) return;
      startAudius();
    },
    toggleFav: toggleFav,
    isFav: isFav
  };
  watchFavs();
})();"""

CSS = r"""
html body .mzs-fav{flex-shrink:0;width:34px;height:34px;display:flex;align-items:center;justify-content:center;color:var(--muted);cursor:pointer;border-radius:50%}
html body .mzs-fav svg{width:20px;height:20px}
html body #mzFav{color:var(--muted)}
html body .mzs-fav.on,html body #mzFav.on,html body .pf-fav-rm{color:#ef4444}
html body .mzs-fav.on svg,html body #mzFav.on svg,html body .pf-fav-rm svg{fill:currentColor}
html body .pf-fav-note{margin:0 0 10px;font-size:.82rem;color:var(--muted)}
html body .pf-fav-row{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:14px;background:var(--card);padding:8px;margin-bottom:8px}
html body .pf-fav-main{flex:1;min-width:0;display:flex;align-items:center;gap:10px;background:none;border:none;color:var(--text);font:inherit;text-align:left;cursor:pointer;padding:0}
html body .pf-fav-main img,html body .pf-fav-main .ph{width:46px;height:46px;border-radius:10px;object-fit:cover;flex-shrink:0;background:var(--line)}
html body .pf-fav-it{min-width:0;display:flex;flex-direction:column}
html body .pf-fav-it b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.92rem}
html body .pf-fav-it small{color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
html body .pf-fav-rm{width:38px;height:38px;border-radius:50%;border:none;background:none;display:flex;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0;padding:0}
html body .pf-fav-rm svg{width:22px;height:22px}
"""

UI = r"""
(function(){
  var tabs = document.querySelector('.pf-tabs');
  var lenc = document.getElementById('pf-lencana');
  var tent = document.getElementById('pf-tentang');
  if (!tabs || !lenc || !tent) return;
  var HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M12 21s-7.5-4.6-10-9.3C.5 8 2.4 4.5 6 4.5c2 0 3.6 1.1 4.5 2.8C11.4 5.6 13 4.5 15 4.5c3.6 0 5.5 3.5 4 7.2C19.5 16.4 12 21 12 21z"/></svg>';
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
        panel.hidden = true;
      }
    });
  });
  window.addEventListener('mzfavs', function(){ if (!panel.hidden) render(); });
})();
"""

shutil.copy(f, f + '.bak45b')
s = s.replace(A_BUILD, FAV + A_BUILD, 1)
s = s.replace(A_MINI, "+ '<button type=\"button\" class=\"mzm-b\" id=\"mzFav\" aria-label=\"Favorit\"></button>'\n      " + A_MINI, 1)
s = s.replace(A_CLOSE, A_CLOSE + "\n    $('mzFav').innerHTML = HEART;\n    $('mzFav').addEventListener('click', favCurrent);", 1)
s = s.replace(A_SHOW, A_SHOW + "\n    syncFavBtn();", 1)
s = s.replace(A_LIST, LISTBTN, 1)
s = s.replace(A_YT, A_YT + "\n    syncFavBtn();", 1)
s = s.replace(A_END, EXPOSE, 1)
s = s.replace('</head>', '<style id="mz-fav-css">' + CSS + '</style>\n</head>', 1)
j = s.rfind('</body>')
s = s[:j] + '<script id="mz-favui-js">' + UI + '</script>\n' + s[j:]
open(f, 'w', encoding='utf-8').write(s)
print('Favorit di pemutar musik : OK')
print('Tab Favorit di profil    : OK')
