import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if '/*mz-music2*/' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-music-js"' not in s:
    print('GAGAL: fitur musik (fix43) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

OLD_HEART = 'M12 21s-7.5-4.6-10-9.3C.5 8 2.4 4.5 6 4.5c2 0 3.6 1.1 4.5 2.8C11.4 5.6 13 4.5 15 4.5c3.6 0 5.5 3.5 4 7.2C19.5 16.4 12 21 12 21z'
NEW_HEART = 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z'

JS = r"""/*mz-music2*/
(function(){
  var btn = document.getElementById('mzMusicBtn');
  if (!btn) return;
  var $ = function(id){ return document.getElementById(id); };
  var audio = new Audio();
  audio.preload = 'none';
  var S = { mode: '', src: 'audius', q: '', next: '', more: false, loading: false, results: [], queue: [], idx: -1, yt: null, ytState: -1, built: false, loaded: false };
  var IP = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4l13 8-13 8z"/></svg>';
  var IQ = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>';
  var IN = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4l10 8-10 8zM18 4h2v16h-2z"/></svg>';
  var IX = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  var HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
  var GEN = [
    { n: 'Populer', q: '' }, { n: 'Indonesia', q: 'lagu indonesia' }, { n: 'Pop', q: 'pop' }, { n: 'Hip-Hop', q: 'hip hop' },
    { n: 'Elektronik', q: 'electronic' }, { n: 'Lo-fi', q: 'lofi' }, { n: 'Rock', q: 'rock' }, { n: 'Chill', q: 'chill' },
    { n: 'R&B', q: 'r&b' }, { n: 'Jazz', q: 'jazz' }
  ];
  var mini, sheet;

  function fmt(n){ n = Math.max(0, Math.round(n || 0)); return Math.floor(n / 60) + ':' + String(n % 60).padStart(2, '0'); }
  function safeImg(u){ return (typeof u === 'string' && /^https:\/\//.test(u)) ? u : ''; }

  /* ===== Favorit ===== */
  var favs = [], favUnsub = null;
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
    if (S.built) { renderList(); syncFavBtn(); }
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
    var t = S.queue[S.idx];
    if (!t || !S.mode) return null;
    return { src: t.src, id: t.id, title: t.title, artist: t.artist, art: t.art, dur: t.dur };
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

  /* ===== Tampilan ===== */
  function build(){
    if (S.built) return;
    S.built = true;
    mini = document.createElement('div');
    mini.className = 'mzm';
    mini.hidden = true;
    mini.innerHTML = '<div class="mzm-bar"><i id="mzBar"></i></div>'
      + '<button type="button" class="mzm-main" id="mzMiniOpen"><img id="mzArt" alt="" hidden><span class="mzm-ph" id="mzArtPh">&#9834;</span>'
      + '<span class="mzm-t"><b id="mzTitle"></b><small id="mzSub"></small></span></button>'
      + '<button type="button" class="mzm-b" id="mzFav" aria-label="Favorit"></button>'
      + '<button type="button" class="mzm-b" id="mzPlay" aria-label="Putar atau jeda"></button>'
      + '<button type="button" class="mzm-b" id="mzNext" aria-label="Berikutnya"></button>'
      + '<button type="button" class="mzm-b" id="mzClose" aria-label="Tutup pemutar"></button>';
    document.body.appendChild(mini);

    sheet = document.createElement('div');
    sheet.className = 'mzs mz-off';
    sheet.innerHTML = '<div class="mzs-panel">'
      + '<div class="mzs-head"><b>Musik</b><button type="button" id="mzSheetX">Tutup</button></div>'
      + '<div id="mzVid" class="mzs-yt" style="display:none"><div id="mzYtBox"></div></div>'
      + '<div class="mzs-tabs"><button type="button" class="on" data-mt="cari">Cari</button><button type="button" data-mt="yt">Tempel Link</button></div>'
      + '<div id="mz-cari">'
      + '<div class="mzs-chips" id="mzSrc"><button type="button" class="on" data-src="audius">Audius</button><button type="button" data-src="yt" id="mzSrcYt" hidden>YouTube</button></div>'
      + '<div class="mzs-row"><input id="mzQ" type="search" placeholder="Cari lagu atau artis..." maxlength="80" autocomplete="off"><button type="button" class="mzs-btn" id="mzGo">Cari</button></div>'
      + '<div class="mzs-chips" id="mzGen" style="margin-top:10px"></div>'
      + '<p class="mzs-hint" id="mzStat"></p><div id="mzList"></div>'
      + '<button type="button" class="mzs-more" id="mzMore" hidden>Muat lebih banyak</button>'
      + '<p class="mzs-hint" id="mzCredit"></p></div>'
      + '<div id="mz-yt" class="mz-offp"><div class="mzs-row"><input id="mzYl" type="url" placeholder="Tempel link YouTube..." autocomplete="off"><button type="button" class="mzs-btn" id="mzYgo">Putar</button></div>'
      + '<p class="mzs-hint" id="mzYstat"></p></div>'
      + '</div>';
    document.body.appendChild(sheet);

    $('mzFav').innerHTML = HEART;
    $('mzPlay').innerHTML = IP;
    $('mzNext').innerHTML = IN;
    $('mzClose').innerHTML = IX;

    GEN.forEach(function(g){
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = g.n;
      b.dataset.q = g.q;
      b.addEventListener('click', function(){ $('mzQ').value = g.q; search(true); });
      $('mzGen').appendChild(b);
    });

    sheet.addEventListener('click', function(e){ if (e.target === sheet) closeSheet(); });
    $('mzSheetX').addEventListener('click', closeSheet);
    $('mzMiniOpen').addEventListener('click', openSheet);
    $('mzFav').addEventListener('click', favCurrent);
    $('mzPlay').addEventListener('click', toggle);
    $('mzNext').addEventListener('click', next);
    $('mzClose').addEventListener('click', stopAll);
    $('mzGo').addEventListener('click', function(){ search(true); });
    $('mzMore').addEventListener('click', function(){ search(false); });
    $('mzQ').addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); search(true); } });
    $('mzYgo').addEventListener('click', goYt);
    $('mzYl').addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); goYt(); } });
    sheet.querySelectorAll('[data-mt]').forEach(function(b){
      b.addEventListener('click', function(){ setTab(b.dataset.mt); });
    });
    sheet.querySelectorAll('[data-src]').forEach(function(b){
      b.addEventListener('click', function(){ setSrc(b.dataset.src); });
    });
  }

  function setTab(t){
    sheet.querySelectorAll('[data-mt]').forEach(function(b){ b.classList.toggle('on', b.dataset.mt === t); });
    $('mz-cari').classList.toggle('mz-offp', t !== 'cari');
    $('mz-yt').classList.toggle('mz-offp', t !== 'yt');
  }
  function layoutVid(){
    var v = $('mzVid');
    if (!v) return;
    if (S.mode !== 'yt') { v.style.display = 'none'; v.classList.remove('mz-offp'); return; }
    v.style.display = '';
    v.classList.toggle('mz-offp', !!(sheet && sheet.classList.contains('mz-off')));
  }
  function openSheet(){
    build();
    if (typeof closeSidebar === 'function') closeSidebar();
    sheet.classList.remove('mz-off');
    document.documentElement.classList.add('mz-musiclock');
    layoutVid();
    if (!S.loaded) { S.loaded = true; init(); }
  }
  function closeSheet(){
    if (!sheet) return;
    sheet.classList.add('mz-off');
    document.documentElement.classList.remove('mz-musiclock');
    layoutVid();
  }
  btn.addEventListener('click', openSheet);

  function stat(m){ var e = $('mzStat'); if (e) e.textContent = m || ''; }
  function ystat(m){ var e = $('mzYstat'); if (e) e.textContent = m || ''; }
  function setIcon(playing){ if ($('mzPlay')) $('mzPlay').innerHTML = playing ? IQ : IP; }
  function showMini(title, sub, art){
    mini.hidden = false;
    document.body.classList.add('mz-hasmini');
    $('mzTitle').textContent = title || '';
    $('mzSub').textContent = sub || '';
    var img = $('mzArt'), ph = $('mzArtPh'), a = safeImg(art);
    if (a) { img.src = a; img.hidden = false; ph.hidden = true; } else { img.hidden = true; ph.hidden = false; }
    $('mzNext').style.display = S.queue.length > 1 ? '' : 'none';
    syncFavBtn();
  }

  /* ===== Daftar & pencarian ===== */
  function renderList(){
    var box = $('mzList');
    if (!box) return;
    box.replaceChildren();
    var cur = (S.mode && S.queue[S.idx]) ? S.queue[S.idx].id : '';
    S.results.forEach(function(t, i){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'mzs-item' + (t.id === cur ? ' on' : '');
      var a = safeImg(t.art), pic;
      if (a) { pic = document.createElement('img'); pic.alt = ''; pic.src = a; pic.loading = 'lazy'; }
      else { pic = document.createElement('span'); pic.className = 'ph'; }
      var info = document.createElement('span');
      info.className = 'mzs-it';
      var tt = document.createElement('b'); tt.textContent = t.title;
      var ar = document.createElement('small'); ar.textContent = t.artist || '-';
      info.append(tt, ar);
      var d = document.createElement('span');
      d.className = 'mzs-d';
      d.textContent = t.dur ? fmt(t.dur) : '';
      var hs = document.createElement('span');
      hs.className = 'mzs-fav' + (isFav(t.id) ? ' on' : '');
      hs.setAttribute('role', 'button');
      hs.setAttribute('aria-label', 'Favorit');
      hs.innerHTML = HEART;
      hs.addEventListener('click', function(e){ e.stopPropagation(); toggleFav(t); });
      b.append(pic, info, d, hs);
      b.addEventListener('click', function(){ S.queue = S.results.slice(); S.idx = i; startItem(); });
      box.appendChild(b);
    });
    $('mzMore').hidden = !S.more;
    $('mzMore').disabled = S.loading;
    $('mzGen').querySelectorAll('button').forEach(function(x){ x.classList.toggle('on', x.dataset.q === S.q); });
  }
  function setSrc(src){
    S.src = src;
    sheet.querySelectorAll('[data-src]').forEach(function(b){ b.classList.toggle('on', b.dataset.src === src); });
    $('mzCredit').textContent = src === 'yt'
      ? 'Hasil dari YouTube, diputar lewat pemutar resmi YouTube.'
      : 'Katalog dari Audius (musik artis independen). Hargai karya artisnya.';
    search(true);
  }
  async function init(){
    try {
      var r = await fetch('/api/music?info=1', { cache: 'no-store' });
      var d = await r.json();
      if (d && d.yt) { $('mzSrcYt').hidden = false; S.src = 'yt'; }
    } catch (e) {}
    setSrc(S.src);
  }
  async function search(reset){
    if (S.loading) return;
    if (reset) { S.q = $('mzQ').value.trim(); S.next = ''; S.results = []; S.more = false; }
    S.loading = true;
    stat(reset ? (S.q ? 'Mencari...' : 'Memuat lagu populer...') : 'Memuat...');
    renderList();
    try {
      var p = new URLSearchParams({ q: S.q, src: S.src });
      if (S.next) p.set('page', S.next);
      var r = await fetch('/api/music?' + p.toString(), { cache: 'no-store' });
      var d = await r.json().catch(function(){ return {}; });
      if (!r.ok || !d.success) { stat(d.message || 'Gagal memuat lagu.'); S.more = false; return; }
      var seen = {};
      S.results.forEach(function(t){ seen[t.id] = 1; });
      (d.tracks || []).forEach(function(t){ if (!seen[t.id]) { seen[t.id] = 1; S.results.push(t); } });
      S.next = d.next || '';
      S.more = !!S.next;
      stat(S.results.length ? '' : 'Tidak ada hasil.');
    } catch (e) { stat('Koneksi bermasalah.'); S.more = false; }
    finally { S.loading = false; renderList(); }
  }

  /* ===== Pemutaran ===== */
  function startItem(){
    var t = S.queue[S.idx];
    if (!t) return;
    if (t.src === 'yt') startYt(t); else startAudius(t);
    renderList();
  }
  function startAudius(t){
    stopYt();
    S.mode = 'audius';
    layoutVid();
    audio.src = '/api/music?stream=' + encodeURIComponent(t.id);
    var p = audio.play();
    if (p && p.catch) p.catch(function(){ stat('Lagu gagal diputar, coba lagu lain.'); });
    showMini(t.title, t.artist, t.art);
    if ('mediaSession' in navigator) {
      try {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: t.title, artist: t.artist,
          artwork: safeImg(t.art) ? [{ src: t.art, sizes: '150x150', type: 'image/jpeg' }] : []
        });
        navigator.mediaSession.setActionHandler('play', function(){ audio.play(); });
        navigator.mediaSession.setActionHandler('pause', function(){ audio.pause(); });
        navigator.mediaSession.setActionHandler('nexttrack', next);
        navigator.mediaSession.setActionHandler('previoustrack', prev);
      } catch (e) {}
    }
  }
  function next(){
    if (S.idx + 1 < S.queue.length) { S.idx++; startItem(); }
    else if (S.mode === 'audius') audio.pause();
  }
  function prev(){
    if (S.mode === 'audius' && (audio.currentTime > 4 || S.idx === 0)) { audio.currentTime = 0; return; }
    if (S.idx > 0) { S.idx--; startItem(); }
  }
  audio.addEventListener('play', function(){ if (S.mode === 'audius') setIcon(true); });
  audio.addEventListener('pause', function(){ if (S.mode === 'audius') setIcon(false); });
  audio.addEventListener('ended', next);
  audio.addEventListener('error', function(){
    if (S.mode === 'audius' && audio.getAttribute('src')) { stat('Lagu gagal diputar, coba lagu lain.'); setIcon(false); }
  });
  audio.addEventListener('timeupdate', function(){
    var bar = $('mzBar');
    if (bar && S.mode === 'audius' && audio.duration && isFinite(audio.duration)) bar.style.width = Math.min(100, audio.currentTime / audio.duration * 100) + '%';
  });

  var YT_RE = /(?:youtu\.be\/|youtube\.com\/(?:watch\?(?:[^#]*&)?v=|embed\/|shorts\/|live\/)|music\.youtube\.com\/watch\?(?:[^#]*&)?v=)([A-Za-z0-9_-]{11})/;
  function ytApi(cb){
    if (window.YT && window.YT.Player) { cb(); return; }
    window.__mzYtq = window.__mzYtq || [];
    window.__mzYtq.push(cb);
    if (!document.getElementById('mz-ytapi')) {
      var sc = document.createElement('script');
      sc.id = 'mz-ytapi';
      sc.src = 'https://www.youtube.com/iframe_api';
      document.head.appendChild(sc);
      var prevCb = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function(){
        if (prevCb) { try { prevCb(); } catch (e) {} }
        (window.__mzYtq || []).splice(0).forEach(function(f){ f(); });
      };
    }
  }
  function onYt(e){
    S.ytState = e.data;
    if (S.mode !== 'yt') return;
    setIcon(e.data === 1);
    try {
      var d = S.yt.getVideoData();
      var cur = S.queue[S.idx];
      if (d && d.title && cur && d.video_id === cur.id) {
        if (!cur.artist) cur.artist = d.author || '';
        $('mzTitle').textContent = cur.title === 'YouTube' ? d.title : cur.title;
        $('mzSub').textContent = cur.artist || 'YouTube';
        if (cur.title === 'YouTube') cur.title = d.title;
        syncFavBtn();
      }
    } catch (err) {}
    if (e.data === 0) { if ($('mzBar')) $('mzBar').style.width = '0'; next(); }
  }
  function startYt(t){
    audio.pause();
    S.mode = 'yt';
    showMini(t.title, t.artist || 'YouTube', t.art || ('https://i.ytimg.com/vi/' + t.id + '/mqdefault.jpg'));
    setIcon(true);
    layoutVid();
    ytApi(function(){
      if (S.mode !== 'yt') return;
      var cur = S.queue[S.idx];
      if (!cur) return;
      if (S.yt && S.yt.loadVideoById) { S.yt.loadVideoById(cur.id); return; }
      S.yt = new YT.Player('mzYtBox', {
        videoId: cur.id, width: '100%', height: '100%',
        playerVars: { playsinline: 1, rel: 0, autoplay: 1 },
        events: { onReady: function(e){ e.target.playVideo(); }, onStateChange: onYt }
      });
    });
  }
  function stopYt(){ try { if (S.yt && S.yt.stopVideo) S.yt.stopVideo(); } catch (e) {} S.ytState = -1; }
  function goYt(){
    var m = YT_RE.exec($('mzYl').value.trim());
    if (!m) { ystat('Link YouTube tidak dikenali.'); return; }
    ystat('Memutar... pemutar tampil di bagian atas panel.');
    S.queue = [{ src: 'yt', id: m[1], title: 'YouTube', artist: '', art: 'https://i.ytimg.com/vi/' + m[1] + '/mqdefault.jpg', dur: 0 }];
    S.idx = 0;
    startItem();
  }

  function toggle(){
    if (S.mode === 'audius') {
      if (audio.paused) { var p = audio.play(); if (p && p.catch) p.catch(function(){}); } else audio.pause();
    } else if (S.mode === 'yt' && S.yt) {
      if (S.ytState === 1) S.yt.pauseVideo(); else S.yt.playVideo();
    }
  }
  function stopAll(){
    audio.pause();
    stopYt();
    S.mode = '';
    mini.hidden = true;
    document.body.classList.remove('mz-hasmini');
    if ($('mzBar')) $('mzBar').style.width = '0';
    layoutVid();
    renderList();
  }

  window.mzMusic = {
    play: function(list, i){
      build();
      if (!list[i]) return;
      S.queue = list.slice();
      S.idx = i;
      startItem();
    },
    toggleFav: toggleFav,
    isFav: isFav
  };
  watchFavs();
})();
"""

CSS = r"""
html body .mzs-chips{display:flex;gap:8px;overflow-x:auto;padding:2px 0 10px;margin:0;-webkit-overflow-scrolling:touch;scrollbar-width:none}
html body .mzs-chips::-webkit-scrollbar{display:none}
html body .mzs-chips button{flex-shrink:0;padding:8px 14px;border-radius:999px;border:1px solid var(--line);background:var(--bg);color:var(--text);font:inherit;font-size:.82rem;font-weight:700;cursor:pointer;white-space:nowrap}
html body .mzs-chips button.on{background:var(--accent);color:var(--on,#fff);border-color:var(--accent)}
html body .mzs-chips button[hidden]{display:none}
html body .mzs-more{width:100%;margin:8px 0 4px;padding:13px;border-radius:12px;border:1px solid var(--line);background:var(--bg);color:var(--text);font:inherit;font-weight:800;cursor:pointer}
html body .mzs-more[hidden]{display:none}
html body .mzs-yt{margin:0 0 12px}
"""

s, n = re.subn(r'<script id="mz-music-js">.*?</script>', lambda m: '<script id="mz-music-js">' + JS + '</script>', s, count=1, flags=re.S)
if not n:
    print('GAGAL: skrip musik tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak46')
s = s.replace(OLD_HEART, NEW_HEART)
s = s.replace('</head>', '<style id="mz-music2-css">' + CSS + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Pemutar musik baru + hati yang benar : OK')
