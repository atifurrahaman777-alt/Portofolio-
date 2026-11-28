/*mz-music2*/
(function(){
  var btn = document.getElementById('mzMusicBtn');
  if (!btn) return;
  var $ = function(id){ return document.getElementById(id); };
  var audio = new Audio();
  audio.preload = 'none';
  var S = { mode: '', src: 'audius', q: '', next: '', more: false, loading: false, results: [], queue: [], idx: -1, art: '', shuffle: false, repeat: '', yt: null, ytState: -1, lyricAbort: null, lyricLines: [], lyricIdx: -1, lyricRowCount: 0, lyricSong: '', lyricPlain: '', lyricMode: 'line', lyricWords: [], lyricWordTimes: [], lyricWeights: [], lyricColors: null, lyricEnd: 0, nowSong: '', nowArtist: '', built: false, loaded: false };
  var IP = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4l13 8-13 8z"/></svg>';
  var IQ = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>';
  var IN = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4l10 8-10 8zM18 4h2v16h-2z"/></svg>';
  var IPV = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4h2v16H7zM19 4l-10 8 10 8z"/></svg>';
  var ISH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5"/><path d="M4 20L21 3"/><path d="M21 16v5h-5"/><path d="M15 15l6 6"/><path d="M4 4l5 5"/></svg>';
  var IRP = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2l4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>';
  var IX = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  var HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
  var GEN = [
    { n: 'Populer', q: '' }, { n: 'Indonesia', q: 'lagu indonesia' }, { n: 'Pop', q: 'pop' }, { n: 'Hip-Hop', q: 'hip hop' },
    { n: 'Elektronik', q: 'electronic' }, { n: 'Lo-fi', q: 'lofi' }, { n: 'Rock', q: 'rock' }, { n: 'Chill', q: 'chill' },
    { n: 'R&B', q: 'r&b' }, { n: 'Jazz', q: 'jazz' }
  ];
  var mini, sheet;
  var lyricsOpen = false;

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
      + '<span class="mz-eq" id="mzEqMini" aria-hidden="true"><i></i><i></i><i></i><i></i></span>'
      + '<button type="button" class="mzm-b" id="mzFav" aria-label="Favorit"></button>'
      + '<button type="button" class="mzm-b" id="mzPlay" aria-label="Putar atau jeda"></button>'
      + '<button type="button" class="mzm-b" id="mzNext" aria-label="Berikutnya"></button>'
      + '<button type="button" class="mzm-b" id="mzClose" aria-label="Tutup pemutar"></button>';
    document.body.appendChild(mini);

    sheet = document.createElement('div');
    sheet.className = 'mzs mz-off';
    sheet.innerHTML = '<div class="mzs-panel">'
      + '<div class="mzs-head"><span class="mzs-head-title"><b>Musik</b><span class="mz-eq" id="mzEqSheet" aria-hidden="true"><i></i><i></i><i></i><i></i></span></span><button type="button" id="mzSheetX">Tutup</button></div>'
      + '<div class="mz-now">'
      + '<div class="mz-now-art"><img id="mzNowArt" alt="" hidden><span class="mz-now-ph" id="mzNowArtPh">&#9834;</span><div id="mzVid" class="mzs-yt" style="display:none"><div id="mzYtBox"></div></div></div>'
      + '<div class="mz-now-meta"><span class="mz-now-label" id="mzNowLabel">Sedang diputar</span><b id="mzNowTitle">Belum ada lirik</b><small id="mzNowSub">Cari lagu untuk mulai mendengarkan</small>'
      + '<span class="mz-eq" id="mzEqNow" aria-hidden="true"><i></i><i></i><i></i><i></i></span></div></div>'
      + '<div class="mz-progress"><span id="mzNowCur">0:00</span><input type="range" id="mzSeek" min="0" max="100" value="0" aria-label="Posisi lagu"><span id="mzNowDur">0:00</span></div>'
      + '<div class="mz-controls">'
      + '<button type="button" id="mzShuffle" aria-label="Acak" title="Acak">' + ISH + '</button>'
      + '<button type="button" id="mzPrev" aria-label="Sebelumnya" title="Lagu sebelumnya">' + IPV + '</button>'
      + '<button type="button" class="mz-playbig" id="mzPlayBig" aria-label="Putar atau jeda"></button>'
      + '<button type="button" id="mzNextBig" aria-label="Berikutnya" title="Lagu berikutnya">' + IN + '</button>'
      + '<button type="button" id="mzRepeat" aria-label="Ulangi" title="Ulangi">' + IRP + '</button>'
      + '</div>'
      + '<div class="mzs-tabs"><button type="button" class="on" data-mt="cari">Cari</button><button type="button" data-mt="yt">Tempel Link</button></div>'
      + '<div class="mz-scroll">'
      + '<div id="mz-cari">'
      + '<div class="mz-search-top"><div class="mzs-row"><input id="mzQ" type="search" placeholder="Cari lagu atau artis..." maxlength="80" autocomplete="off" enterkeyhint="search" aria-label="Cari lagu atau artis"><button type="button" class="mzs-btn" id="mzGo">Cari</button><button type="button" class="mz-lyrics-toggle" id="mLyricsToggle" aria-expanded="false" aria-controls="mLyrics" aria-label="Tampilkan lirik" title="Tampilkan lirik"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg></button></div></div>'
      + '<div class="mz-search-wrap"><div class="mz-search-body">'
      + '<div class="mzs-chips" id="mzSrc"><button type="button" class="on" data-src="audius">Audius</button><button type="button" data-src="yt" id="mzSrcYt" hidden>YouTube</button></div>'
      + '<div class="mzs-chips" id="mzGen"></div>'
      + '<p class="mzs-hint" id="mzStat"></p><div id="mzList"></div>'
      + '<button type="button" class="mzs-more" id="mzMore" hidden>Muat lebih banyak</button>'
      + '<p class="mzs-hint" id="mzCredit"></p>'
      + '</div></div>'
      + '<div class="mz-lyrics" id="mLyrics" hidden><div class="mz-lyrics-head"><span class="mz-lyrics-label">Lirik</span><b id="mLyricsTitle"></b></div><div class="mz-lyrics-body" id="mLyricsBody">Memuat lirik...</div></div></div>'
      + '<div id="mz-yt" class="mz-offp"><div class="mzs-row"><input id="mzYl" type="url" placeholder="Tempel link YouTube..." autocomplete="off" aria-label="Link YouTube"><button type="button" class="mzs-btn" id="mzYgo">Putar</button></div>'
      + '<p class="mzs-hint" id="mzYstat"></p></div>'
      + '</div></div>';
    document.body.appendChild(sheet);

    $('mzFav').innerHTML = HEART;
    $('mzPlay').innerHTML = IP;
    $('mzPlayBig').innerHTML = IP;
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
    $('mzPlayBig').addEventListener('click', toggle);
    $('mzPrev').addEventListener('click', prev);
    $('mzNext').addEventListener('click', function(){ next(false); });
    $('mzNextBig').addEventListener('click', function(){ next(false); });
    $('mzShuffle').addEventListener('click', function(){
      S.shuffle = !S.shuffle;
      this.classList.toggle('on', S.shuffle);
      this.title = S.shuffle ? 'Matikan acak' : 'Acak';
      if (S.shuffle && S.queue.length > 1 && S.idx >= 0) {
        var i = S.idx;
        while (i === S.idx) i = Math.floor(Math.random() * S.queue.length);
        S.idx = i;
        startItem();
        stat('Acak aktif');
      } else if (!S.shuffle) stat('Acak dimatikan');
    });
    $('mzRepeat').addEventListener('click', function(){
      var modes = ['', 'one', 'all'];
      var at = modes.indexOf(S.repeat || '');
      S.repeat = modes[(at + 1) % modes.length];
      this.classList.toggle('on', !!S.repeat);
      this.classList.toggle('one', S.repeat === 'one');
      this.title = S.repeat === 'one' ? 'Ulangi lagu ini' : (S.repeat === 'all' ? 'Ulangi semua lagu' : 'Ulangi');
      if (S.repeat === 'one') { restartCurrent(); stat('Ulangi lagu ini'); }
      else if (S.repeat === 'all') stat('Ulangi semua lagu');
      else stat('Ulangi dimatikan');
    });
    $('mzSeek').addEventListener('input', function(){
      var d = 0;
      if (S.mode === 'audius') d = audio.duration;
      else if (S.mode === 'yt' && S.yt && S.yt.getDuration) { try { d = S.yt.getDuration(); } catch (e) {} }
      if (!d || !isFinite(d)) return;
      var t = d * (Number(this.value) / 100);
      if (S.mode === 'audius') { try { audio.currentTime = t; } catch (e) {} }
      else if (S.yt && S.yt.seekTo) { try { S.yt.seekTo(t, true); } catch (e) {} }
      setProgress(t, d);
    });
    $('mzClose').addEventListener('click', stopAll);
    $('mzGo').addEventListener('click', function(){ search(true); });
    $('mLyricsToggle').addEventListener('click', function(){
      lyricsOpen = !lyricsOpen;
      syncLyrics();
    });
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
    var v = $('mzVid'), art = $('mzNowArt'), ph = $('mzNowArtPh');
    if (!v) return;
    if (S.mode === 'yt') {
      v.style.display = '';
      v.classList.toggle('mz-offp', !!(sheet && sheet.classList.contains('mz-off')));
      if (art) art.hidden = true;
      if (ph) ph.hidden = true;
      return;
    }
    v.style.display = 'none';
    v.classList.remove('mz-offp');
    var a = safeImg(S.art);
    if (art && ph) {
      if (a) { art.src = a; art.hidden = false; ph.hidden = true; }
      else { art.hidden = true; ph.hidden = false; }
    }
  }
  function openSheet(){
    build();
    if (typeof closeSidebar === 'function') closeSidebar();
    sheet.classList.remove('mz-off');
    document.documentElement.classList.add('mz-musiclock');
    layoutVid();
    if (!S.loaded) { S.loaded = true; init(); }
    if (window.matchMedia && !window.matchMedia('(pointer: coarse)').matches) {
      try { $('mzQ').focus(); } catch (e) {}
    }
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
  function setIcon(playing){
    var on = !!playing;
    if ($('mzPlay')) $('mzPlay').innerHTML = on ? IQ : IP;
    if ($('mzPlayBig')) $('mzPlayBig').innerHTML = on ? IQ : IP;
    document.querySelectorAll('.mz-eq').forEach(function(e){ e.classList.toggle('on', on); });
  }
  function setProgress(cur, dur){
    var pct = (dur > 0 && isFinite(dur)) ? Math.min(100, Math.max(0, cur / dur * 100)) : 0;
    if ($('mzBar')) $('mzBar').style.width = pct + '%';
    var seek = $('mzSeek');
    if (seek) { seek.value = pct; seek.style.setProperty('--mzp', pct + '%'); }
    if ($('mzNowCur')) $('mzNowCur').textContent = fmt(cur);
    if ($('mzNowDur')) $('mzNowDur').textContent = fmt(dur);
  }
  function setNowMeta(song, artist){
    S.nowSong = song || '';
    S.nowArtist = artist || '';
    if ($('mzNowLabel')) $('mzNowLabel').textContent = song || 'Sedang diputar';
    if ($('mzNowSub')) $('mzNowSub').textContent = artist || 'Artis tidak diketahui';
    if ($('mzNowTitle') && !S.lyricLines.length) $('mzNowTitle').textContent = 'Lirik belum tersedia';
  }
  function showMini(title, sub, art){
    mini.hidden = false;
    document.body.classList.add('mz-hasmini');
    S.art = art || '';
    $('mzTitle').textContent = title || '';
    $('mzSub').textContent = sub || '';
    setNowMeta(title || 'Tanpa judul', sub || 'Artis tidak diketahui');
    var a = safeImg(art), img = $('mzArt'), ph = $('mzArtPh');
    if (a) { img.src = a; img.hidden = false; ph.hidden = true; } else { img.hidden = true; ph.hidden = false; }
    var nimg = $('mzNowArt'), nph = $('mzNowArtPh');
    if (nimg && nph) {
      if (a) { nimg.src = a; nimg.hidden = false; nph.hidden = true; }
      else { nimg.hidden = true; nph.hidden = false; }
    }
    setProgress(0, 0);
    $('mzNext').style.display = S.queue.length > 1 ? '' : 'none';
    syncFavBtn();
  }

  /* ===== Lirik lagu ===== */
  function parseSynced(s){
    var out = [];
    String(s || '').split(/\r?\n/).forEach(function(line){
      var m = /^\s*((?:\[\d{1,2}:\d{2}(?:[.:]\d{1,3})?\])+)\s*(.*)$/.exec(line);
      if (!m) return;
      var txt = m[2].trim();
      if (!txt || /^(ar|ti|al|by|offset):/i.test(txt)) return;
      var re = /\[(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?\]/g, tm;
      while ((tm = re.exec(m[1]))) {
        out.push({ t: Number(tm[1]) * 60 + Number(tm[2]) + (tm[3] ? Number('0.' + tm[3]) : 0), text: txt });
      }
    });
    out.sort(function(a, b){ return a.t - b.t; });
    return out;
  }
  function yamlText(s){
    var v = String(s || '').trim();
    if ((v.charAt(0) === "'" && v.slice(-1) === "'") || (v.charAt(0) === '"' && v.slice(-1) === '"')) return v.slice(1, -1).replace(/\\n/g, '\n');
    return v.replace(/\s+#.*$/, '');
  }
  function parseLyricsfile(y){
    var rows = [], cur = null, base = null, last = 0;
    String(y || '').split(/\r?\n/).forEach(function(line){
      var m = /^(\s*)-\s*text:\s*(.*)$/.exec(line);
      if (m) {
        var ind = m[1].length, val = yamlText(m[2]);
        if (base === null) base = ind;
        if (ind <= base) {
          cur = { t: last, end: 0, text: val, words: [] };
          rows.push(cur);
        } else if (cur) {
          var prev = cur.words[cur.words.length - 1];
          if (prev && !prev.end && prev.start) prev.end = last || prev.start + 0.2;
          cur.words.push({ text: val, start: 0, end: 0 });
        }
        return;
      }
      var sm = /^(\s*)start_ms:\s*(\d+(?:\.\d+)?)/.exec(line);
      if (sm) {
        var ms = Number(sm[2]) / 1000, wordLine = base !== null && sm[1].length > base;
        if (wordLine && cur && cur.words.length) cur.words[cur.words.length - 1].start = ms;
        else if (cur) cur.t = ms;
        last = ms;
        return;
      }
      var em = /^(\s*)end_ms:\s*(\d+(?:\.\d+)?)/.exec(line);
      if (em) {
        var me = Number(em[2]) / 1000, wordEnd = base !== null && em[1].length > base;
        if (wordEnd && cur && cur.words.length) cur.words[cur.words.length - 1].end = me;
        else if (cur) cur.end = me;
        last = me;
      }
    });
    rows.forEach(function(r){
      if (!r.words.length) r.words = [{ text: r.text, start: r.t, end: r.end || r.t + 2 }];
      r.words.forEach(function(w, i){
        if (!w.start) w.start = i ? r.words[i - 1].end : r.t;
        if (!w.end || w.end <= w.start) w.end = i < r.words.length - 1 ? r.words[i + 1].start : (r.end || r.t + 3);
      });
    });
    return rows.filter(function(r){ return r.text && r.words.length; });
  }
  function currentTime(){
    if (S.mode === 'audius') return audio.currentTime || 0;
    if (S.mode === 'yt' && S.yt && S.yt.getCurrentTime) { try { return S.yt.getCurrentTime() || 0; } catch (e) {} }
    return 0;
  }
  function renderLyricRows(){
    var body = $('mLyricsBody');
    if (!body) return;
    body.replaceChildren();
    S.lyricLines.forEach(function(l, i){
      var d = document.createElement('div');
      d.className = 'mz-ly-row' + (i === S.lyricIdx ? ' on' : '');
      d.textContent = l.text;
      body.appendChild(d);
    });
    S.lyricRowCount = S.lyricLines.length;
  }
  function parsePlainToLines(text, dur){
    var arr = String(text || '').split(/\r?\n/).map(function(s){ return s.trim(); }).filter(Boolean);
    var total = Number(dur) || 0;
    if (!arr.length || total < 5) return [];
    var start = Math.min(12, total * 0.06);
    var end = Math.max(start + 2, total - 5);
    var step = (end - start) / arr.length;
    return arr.map(function(t, i){ return { t: start + i * step, text: t }; });
  }
  function cssVar(el, name, fallback){
    try { return getComputedStyle(el).getPropertyValue(name).trim() || fallback; } catch (e) { return fallback; }
  }
  function rgbOf(c){
    c = String(c || '').trim();
    if (c.charAt(0) === '#') {
      var h = c.slice(1);
      if (h.length === 3) h = h.split('').map(function(x){ return x + x; }).join('');
      if (h.length >= 6) return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
    }
    var m = /^rgba?\(([^)]+)\)/.exec(c);
    if (m) { var p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return [p[0] || 0, p[1] || 0, p[2] || 0]; }
    return [156, 163, 175];
  }
  function mixColor(a, b, t){
    var A = rgbOf(a), B = rgbOf(b), f = Math.max(0, Math.min(1, t));
    return 'rgb(' + Math.round(A[0] + (B[0] - A[0]) * f) + ',' + Math.round(A[1] + (B[1] - A[1]) * f) + ',' + Math.round(A[2] + (B[2] - A[2]) * f) + ')';
  }
  function renderNowLine(idx){
    var now = $('mzNowTitle');
    if (!now) return;
    var line = S.lyricLines[idx];
    var wordMode = S.lyricMode === 'word' && line.words && line.words.length;
    now.replaceChildren();
    S.lyricWords = [];
    S.lyricWordTimes = [];
    S.lyricWeights = [];
    S.lyricColors = { on: cssVar(now, '--sp', '#1ed760'), off: cssVar(now, '--muted', '#9ca3af') };
    var tokens = wordMode ? line.words.map(function(w){ return w.text; }) : String(line.text || '♪').split(/(\s+)/);
    tokens.forEach(function(w, i){
      if (!wordMode && /^\s+$/.test(w)) { now.appendChild(document.createTextNode(w)); return; }
      var sp = document.createElement('span');
      sp.className = 'mz-ly-w';
      sp.textContent = w;
      now.appendChild(sp);
      S.lyricWords.push(sp);
      if (wordMode) {
        S.lyricWordTimes.push({ start: line.words[i].start, end: line.words[i].end });
      } else {
        var core = String(w).replace(/[^A-Za-zÀ-ÿ]/g, '');
        var syl = (core.match(/[aeiouyà-ÿ]/gi) || []).length;
        S.lyricWeights.push(Math.max(0.7, Math.min(2.4, 0.6 + syl * 0.45 + String(w).length / 14)));
      }
    });
    now.classList.add('mz-ly-live');
    now.classList.remove('mz-ly-in');
    void now.offsetWidth;
    now.classList.add('mz-ly-in');
  }
  function setWordColor(sp, f){
    var col = mixColor(S.lyricColors.off, S.lyricColors.on, f);
    sp.style.setProperty('color', col);
    sp.style.setProperty('-webkit-text-fill-color', col);
  }
  function paintWords(v){
    if (!S.lyricWords.length || !S.lyricColors) return;
    if (S.lyricMode === 'word' && S.lyricWordTimes.length === S.lyricWords.length) {
      S.lyricWords.forEach(function(sp, i){
        var tm = S.lyricWordTimes[i];
        setWordColor(sp, (v - tm.start) / Math.max(0.01, tm.end - tm.start));
      });
      return;
    }
    var total = 0;
    S.lyricWeights.forEach(function(w){ total += w; });
    var pos = Math.max(0, Math.min(1, v)) * total, acc = 0;
    S.lyricWords.forEach(function(sp, i){
      var w = S.lyricWeights[i] || 1, start = acc;
      acc += w;
      setWordColor(sp, (pos - start) / Math.max(0.001, w));
    });
  }
  function updateKaraoke(t){
    if (!S.lyricLines.length) return;
    var at = t || 0, idx = 0;
    for (var i = 0; i < S.lyricLines.length; i++) {
      if (S.lyricLines[i].t <= at + 0.12) idx = i;
      else break;
    }
    var line = S.lyricLines[idx], next = S.lyricLines[idx + 1];
    var end = next ? next.t : (S.lyricEnd > line.t ? S.lyricEnd : line.t + 4);
    var frac = Math.max(0, Math.min(1, (at - line.t) / Math.max(0.5, end - line.t)));
    var rows = $('mLyricsBody') && $('mLyricsBody').querySelectorAll('.mz-ly-row');
    var stale = !rows || rows.length !== S.lyricRowCount;
    if (idx !== S.lyricIdx || stale) {
      S.lyricIdx = idx;
      renderNowLine(idx);
      if (rows && rows.length) {
        for (var j = 0; j < rows.length; j++) rows[j].classList.toggle('on', j === idx);
        var box = $('mLyrics'), on = rows[idx];
        if (on && box && !box.hidden && on.scrollIntoView && !stale) { try { on.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) {} }
      }
    }
    paintWords(S.lyricMode === 'word' ? at : frac);
  }
  function resetKaraoke(){
    S.lyricLines = [];
    S.lyricIdx = -1;
    S.lyricRowCount = 0;
    S.lyricSong = '';
    S.lyricPlain = '';
    S.lyricMode = 'line';
    S.lyricWords = [];
    S.lyricWordTimes = [];
    S.lyricWeights = [];
    S.lyricColors = null;
    S.lyricEnd = 0;
    var now = $('mzNowTitle');
    if (now) { now.replaceChildren(); now.textContent = 'Lirik belum tersedia'; now.classList.remove('mz-ly-live', 'mz-ly-in'); }
  }
  /* Lirik harus ngikutin bahasa lagunya (misal lagu Jawa → lirik Jawa). */
  function songLangHint(s){
    var x = String(s || '').toLowerCase();
    if (/\b(jawa|javanese|jawa timur|jawa tengah|campursari|keroncong|dangdut jawa|jogja|yogyakarta|surakarta|solo|semarang|surabaya|koplo)\b/.test(x)) return 'jv';
    if (/\b(indonesia|indo|pop indonesia|dangdut)\b/.test(x)) return 'id';
    return '';
  }
  function lyricLang(s){
    var x = ' ' + String(s || '').toLowerCase() + ' ';
    var jv = ['ora','sing','tak','suweng','gelenter','mambu','gudel','empong','sopo','ngguyu','ndele','godhong','telo','ojo','gelo','ngelak','ombeni','botole','njerone','seneng','asek','ngajar','kowe','kula','panjenengan','marang','saka','nanging','arep','wingi','mbesuk','ngunjuk','tedha','matur','nyuwun','sugeng','wilujeng','kuwi','mangka','dumugi','punika','menika','ageng','alit','wau','kesah','tindak','rawuh','wartos','mboten','boten','dados','tresna','sampun','dhateng','ngapusi','njaluk','nemu','teka','lunga','mangan','turu','tangi','saiki','kepriye','ngendi','kapan','napa','iya','engga','dhèwè','kanca','mangkat','gedhe','cilik','dawa','cendhak','manis','pait','panas','adhem','laris','kepengen','bunder','gepeng','legi'];
    var id = ['yang','dengan','untuk','karena','adalah','setelah','sebelum','hanya','juga','lebih','masih','dari','atau','saya','kamu','tidak','sudah','akan','dapat','seperti','ketika','sehingga','ini','itu','makan','minum','berdua','hati','sama','sangat','sekali','mereka','kita','belum','pernah','sedang'];
    function count(words){ var n = 0; words.forEach(function(w){ n += (x.split(w).length - 1); }); return n; }
    var j = count(jv), i = count(id);
    if (j >= 2 && j > i * 1.4) return 'jv';
    if (i >= 2 && i > j * 1.4) return 'id';
    return '';
  }
  /* Judul dari katalog seringkali "Judul - Playlist ...", jadi dibersihkan dulu. */
  function cleanLyricText(s){
    return String(s || '')
      .replace(/^\s*\d+[.)]\s*/, '')
      .replace(/\s*[\[(][^\])]*[\])]/g, ' ')
      .replace(/\b(official|video|audio|lyrics?|lirik|klip|full album|full|playlist|compilation|terpopuler|lagu|versi|cover|daerah|jawa tengah|jawa timur|jawa|indonesia|indo|koplo|asik|juga|di|hd|mp3|new|latest)\b/gi, ' ')
      .replace(/\s*\.\s+/g, ' ')
      .replace(/\s*[-–—|:_!?]+\s*/g, ' ')
      .replace(/\b\d{3,}k?\b/gi, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }
  function lyricQueries(title, artist){
    var raw = String(title || '').trim(), a = String(artist || '').trim();
    var clean = cleanLyricText(raw);
    var out = [];
    function add(t, ar){
      t = String(t || '').trim(); ar = String(ar || '').trim();
      if (!t) return;
      if (out.some(function(x){ return x.t.toLowerCase() === t.toLowerCase() && x.a.toLowerCase() === ar.toLowerCase(); })) return;
      out.push({ t: t, a: ar });
    }
    function variants(seed, max){
      var seen = {}, list = [];
      function put(v){ v = cleanLyricText(v); if (v && !seen[v]) { seen[v] = 1; list.push(v); } }
      put(seed);
      var w = String(seed || '').split(/\s+/).filter(Boolean);
      while (w.length > 2 && list.length < (max || 6)) { w.pop(); put(w.join(' ')); }
      return list;
    }
    var parts = raw.split(/\s+[-–—|:_]\s+/).map(cleanLyricText).filter(Boolean).slice(0, 3);
    var seeds = [];
    parts.concat(clean ? [clean] : []).forEach(function(s){
      var w = String(s || '').split(/\s+/).filter(Boolean);
      if (w.length <= 2) { seeds.push(s); return; }
      for (var n = Math.min(5, w.length); n >= 2; n--) seeds.push(cleanLyricText(w.slice(0, n).join(' ')));
    });
    var seenSeed = {};
    seeds = seeds.filter(function(s){ s = cleanLyricText(s); if (!s || seenSeed[s]) return false; seenSeed[s] = 1; return true; }).slice(0, 5);
    var terms = [];
    seeds.forEach(function(s){ variants(s, 5).forEach(function(v){ if (terms.indexOf(v) < 0) terms.push(v); }); });
    terms.forEach(function(t){ add(t, a); add(t, ''); });
    if (clean === raw) add(raw, '');
    return out.slice(0, 18);
  }
  async function loadLyrics(title, artist){
    var box = $('mLyrics'), body = $('mLyricsBody'), label = $('mLyricsTitle');
    if (!box || !body) return;
    if (S.lyricAbort) { try { S.lyricAbort.abort(); } catch (e) {} }
    var ctrl = ('AbortController' in window) ? new AbortController() : null;
    S.lyricAbort = ctrl;
    resetKaraoke();
    var nowLine = $('mzNowTitle');
    if (nowLine) nowLine.textContent = 'Memuat lirik...';
    label.textContent = title || '';
    box.hidden = !lyricsOpen;
    body.textContent = 'Memuat lirik...';
    var cur = S.queue[S.idx];
    var want = (cur && cur.dur) || (S.mode === 'audius' ? audio.duration : 0) || 0;
    var queries = lyricQueries(title, artist), pool = [];
    function fetchOpts(){
      var o = { cache: 'no-store', headers: { 'X-User-Agent': 'PortofolioMusik/1.0 (https://privat-project.vercel.app)' } };
      if (ctrl) o.signal = ctrl.signal;
      return o;
    }
    async function collect(url, q){
      var r = await fetch(url, fetchOpts());
      if (!r.ok) return false;
      var a = await r.json();
      if (ctrl && ctrl.signal.aborted) return false;
      var hasLyric = false;
      (a || []).forEach(function(x){
        if (!x) return;
        pool.push({ x: x, q: q });
        if (x.plainLyrics || x.syncedLyrics || x.lyricsfile) hasLyric = true;
      });
      return hasLyric;
    }
    var got = false;
    for (var i = 0; i < queries.length; i++) {
      if (ctrl && ctrl.signal.aborted) return;
      var q = queries[i];
      var url = 'https://lrclib.net/api/search?track_name=' + encodeURIComponent(q.t)
        + '&artist_name=' + encodeURIComponent(q.a);
      try { if (await collect(url, q)) got = true; }
      catch (e) { if (ctrl && ctrl.signal.aborted) return; }
    }
    if (!got) {
      var broad = cleanLyricText(title + ' ' + artist);
      if (broad) {
        try { await collect('https://lrclib.net/api/search?q=' + encodeURIComponent(broad), { t: broad, a: '' }); }
        catch (e) { if (ctrl && ctrl.signal.aborted) return; }
      }
    }
    if (ctrl && ctrl.signal.aborted) return;
    var found = null, best = -Infinity;
    var curTrack = S.queue[S.idx];
    var meta = title + ' ' + (curTrack && curTrack.title ? curTrack.title : '') + ' ' + artist;
    var langHint = songLangHint(meta) || lyricLang(meta);
    pool.forEach(function(item){
      var x = item.x, q = item.q, score = 0;
      var tn = String(x.trackName || x.name || '').toLowerCase();
      var an = String(x.artistName || '').toLowerCase();
      var qt = String(q.t || '').toLowerCase(), qa = String(q.a || '').toLowerCase();
      if (tn === qt) score += 5;
      else if (tn && (tn.indexOf(qt) >= 0 || qt.indexOf(tn) >= 0)) score += 2;
      if (qa) {
        if (an === qa) score += 4;
        else if (an.indexOf(qa) >= 0 || qa.indexOf(an) >= 0) score += 1;
      }
      if (want && x.duration) score += Math.max(0, 5 - Math.abs(x.duration - want) / 25);
      if (x.plainLyrics || x.syncedLyrics || x.lyricsfile) score += 3;
      if (x.hasWordSync && x.lyricsfile) score += 4;
      if (!(x.plainLyrics || x.syncedLyrics || x.lyricsfile)) score -= 3;
      var lx = lyricLang(x.plainLyrics || x.syncedLyrics || (x.lyricsfile || '').replace(/[^\n\rA-Za-zÀ-ÿ' ]/g, ' '));
      if (langHint && lx) score += (lx === langHint) ? 8 : -8;
      if (songLangHint(tn + ' ' + an) === langHint && langHint) score += 2;
      if (score > best) { best = score; found = x; }
    });
    var wordRows = (found && found.hasWordSync && found.lyricsfile) ? parseLyricsfile(found.lyricsfile) : [];
    var synced = !!(found && (wordRows.length || found.syncedLyrics));
    var text = wordRows.length ? wordRows.map(function(r){ return r.text; }).join('\n')
      : (synced ? found.syncedLyrics.replace(/^\[\d{2}:\d{2}(?:[.:]\d{1,3})?\]\s?/gm, '') : ((found && found.plainLyrics) || ''));
    label.textContent = (found && (found.trackName || found.name)) || title || '';
    S.lyricPlain = text || '';
    S.lyricMode = wordRows.length ? 'word' : 'line';
    S.lyricLines = wordRows.length ? wordRows : (synced ? parseSynced(found.syncedLyrics) : parsePlainToLines(S.lyricPlain, want));
    S.lyricEnd = want || (S.lyricLines.length ? S.lyricLines[S.lyricLines.length - 1].t + 4 : 0);
    if ((wordRows.length || (synced && found.syncedLyrics)) && found.duration && want) {
      var scale = want / found.duration;
      if (scale > 0.35 && scale < 3) {
        S.lyricLines.forEach(function(l){
          l.t *= scale;
          if (l.end) l.end *= scale;
          if (l.words) l.words.forEach(function(w){ w.start *= scale; w.end *= scale; });
        });
      }
    }
    if (S.lyricLines.length) {
      S.lyricSong = title || '';
      renderLyricRows();
      updateKaraoke(currentTime());
    } else {
      body.textContent = 'Lirik belum tersedia untuk lagu ini.';
      var nowPlain = $('mzNowTitle');
      if (nowPlain) nowPlain.textContent = 'Lirik belum tersedia';
    }
  }
  function syncLyrics(){
    var box = $('mLyrics'), cari = $('mz-cari'), b = $('mLyricsToggle');
    if (!box || !cari || !b) return;
    box.hidden = !lyricsOpen;
    cari.classList.toggle('mz-lyrics-open', lyricsOpen);
    b.setAttribute('aria-expanded', String(lyricsOpen));
    b.setAttribute('aria-label', lyricsOpen ? 'Tutup lirik' : 'Tampilkan lirik');
    b.title = lyricsOpen ? 'Tutup lirik' : 'Tampilkan lirik';
    if (!lyricsOpen) return;
    if (box.scrollIntoView) { try { box.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) {} }
    var t = S.queue[S.idx];
    if (!t) {
      resetKaraoke();
      $('mLyricsTitle').textContent = '';
      $('mLyricsBody').textContent = 'Putar lagu dulu untuk melihat lirik.';
    } else if (t.title === 'YouTube') {
      var waiting = $('mzNowTitle');
      if (waiting) waiting.textContent = 'Lirik muncul setelah judul terdeteksi';
      $('mLyricsTitle').textContent = '';
      $('mLyricsBody').textContent = 'Lirik muncul setelah judul lagu terdeteksi.';
    } else if (S.lyricSong === t.title && S.lyricLines.length) {
      updateKaraoke(currentTime());
    } else {
      loadLyrics(t.title, t.artist);
    }
  }
  function hideLyrics(){
    if (S.lyricAbort) { try { S.lyricAbort.abort(); } catch (e) {} S.lyricAbort = null; }
    var box = $('mLyrics');
    if (box) box.hidden = true;
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
      var num = document.createElement('span');
      num.className = 'mzs-num';
      num.textContent = String(i + 1);
      var d = document.createElement('span');
      d.className = 'mzs-d';
      d.textContent = t.dur ? fmt(t.dur) : '';
      var hs = document.createElement('span');
      hs.className = 'mzs-fav' + (isFav(t.id) ? ' on' : '');
      hs.setAttribute('role', 'button');
      hs.setAttribute('aria-label', 'Favorit');
      hs.innerHTML = HEART;
      hs.addEventListener('click', function(e){ e.stopPropagation(); toggleFav(t); });
      b.append(num, pic, info, d, hs);
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
    if (reset) {
      if (lyricsOpen) { lyricsOpen = false; syncLyrics(); }
      S.q = $('mzQ').value.trim(); S.next = ''; S.results = []; S.more = false;
    }
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
    stat(lyricsOpen ? '' : 'Ketuk ikon lirik di kolom cari untuk melihat lirik.');
    loadLyrics(t.title, t.artist);
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
  function restartCurrent(){
    if (S.mode === 'audius') {
      try { audio.currentTime = 0; } catch (e) {}
      var p = audio.play();
      if (p && p.catch) p.catch(function(){});
      setProgress(0, audio.duration || 0);
    } else if (S.mode === 'yt' && S.yt) {
      try { S.yt.seekTo(0, true); S.yt.playVideo(); } catch (e) {}
      var d = 0;
      try { d = S.yt.getDuration() || 0; } catch (e) {}
      setProgress(0, d);
    }
    updateKaraoke(0);
  }
  function next(auto){
    var n = S.queue.length;
    if (!n) return;
    if (auto && S.repeat === 'one') { restartCurrent(); return; }
    if (S.shuffle && n > 1) {
      var i = S.idx;
      while (i === S.idx) i = Math.floor(Math.random() * n);
      S.idx = i;
      startItem();
      return;
    }
    if (S.idx + 1 < n) { S.idx++; startItem(); return; }
    if (S.idx + 1 >= n && S.repeat === 'all') { S.idx = 0; startItem(); return; }
    if (S.mode === 'audius') audio.pause();
  }
  function prev(){
    if (S.mode === 'audius' && (audio.currentTime > 4 || S.idx === 0)) { audio.currentTime = 0; return; }
    if (S.idx > 0) { S.idx--; startItem(); }
  }
  audio.addEventListener('play', function(){ if (S.mode === 'audius') setIcon(true); });
  audio.addEventListener('pause', function(){ if (S.mode === 'audius') setIcon(false); });
  audio.addEventListener('ended', function(){ next(true); });
  audio.addEventListener('error', function(){
    if (S.mode === 'audius' && audio.getAttribute('src')) { stat('Lagu gagal diputar, coba lagu lain.'); setIcon(false); }
  });
  audio.addEventListener('timeupdate', function(){
    if (S.mode === 'audius') {
      setProgress(audio.currentTime, audio.duration);
      updateKaraoke(audio.currentTime);
    }
  });
  setInterval(function(){
    if (S.mode !== 'yt' || !S.yt || S.ytState !== 1 || !S.yt.getCurrentTime) return;
    try { setProgress(S.yt.getCurrentTime(), S.yt.getDuration()); updateKaraoke(S.yt.getCurrentTime()); } catch (e) {}
  }, 500);
  (function lyricLoop(){
    if (S.lyricLines.length && (S.mode === 'audius' ? !audio.paused : S.ytState === 1)) updateKaraoke(currentTime());
    if (window.requestAnimationFrame) window.requestAnimationFrame(lyricLoop);
  })();

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
        var label = cur.title === 'YouTube' ? d.title : cur.title;
        var sub = cur.artist || 'YouTube';
        $('mzTitle').textContent = label;
        $('mzSub').textContent = sub;
        setNowMeta(label, sub);
        if (cur.title === 'YouTube') cur.title = d.title;
        if (lyricsOpen) loadLyrics(label, sub);
        syncFavBtn();
      }
    } catch (err) {}
    if (e.data === 0) { setProgress(0, 0); next(true); }
  }
  function startYt(t){
    audio.pause();
    S.mode = 'yt';
    resetKaraoke();
    if (lyricsOpen) {
      $('mLyricsTitle').textContent = t.title === 'YouTube' ? '' : t.title;
      $('mLyricsBody').textContent = t.title === 'YouTube' ? 'Lirik muncul setelah judul lagu terdeteksi.' : 'Memuat lirik...';
      if (t.title !== 'YouTube') loadLyrics(t.title, t.artist || 'YouTube');
    } else hideLyrics();
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
    lyricsOpen = false;
    hideLyrics();
    resetKaraoke();
    syncLyrics();
    setIcon(false);
    S.mode = '';
    mini.hidden = true;
    document.body.classList.remove('mz-hasmini');
    setProgress(0, 0);
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
