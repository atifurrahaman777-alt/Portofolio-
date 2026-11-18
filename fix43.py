import os, re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-music-js' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

m = re.search(r'<div class="mz-sidelinks">.*?</div>', s, re.S)
nav = (re.search(r'<button class="nav-btn" data-tab="tab-pengaturan">.*?</button>', s, re.S)
       or re.search(r'<button class="nav-btn" data-tab="tab-alat">.*?</button>', s, re.S))
if not m or not nav or '</head>' not in s or s.rfind('</body>') == -1:
    print('GAGAL: sidebar atau menu tidak ketemu (pastikan fix42 sudah jalan). Tidak ada yang diubah.')
    raise SystemExit

raw = input('Link saluran Telegram lu (contoh https://t.me/namasaluran atau @namasaluran): ').strip()
if raw.startswith('@'):
    raw = 'https://t.me/' + raw[1:]
elif raw.startswith('t.me/') or raw.startswith('telegram.me/'):
    raw = 'https://' + raw
if not re.fullmatch(r'https://(t\.me|telegram\.me)/[A-Za-z0-9_+/.-]{2,100}', raw):
    print('Link tidak valid. Harus berbentuk https://t.me/namasaluran. Tidak ada yang diubah.')
    raise SystemExit

WA_PATH = 'M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z'

ROW2 = ('<div class="mz-sidelinks">'
        '<a class="mz-sl" href="https://whatsapp.com/channel/0029VbDsbXE1noz0Tpjb5K1O" target="_blank" rel="noopener noreferrer">'
        '<svg viewBox="0 0 448 512" fill="currentColor" stroke="none"><path d="' + WA_PATH + '"/></svg>'
        '<span>Saluran WA</span></a>'
        '<a class="mz-sl" href="' + raw + '" target="_blank" rel="noopener noreferrer">'
        '<svg viewBox="0 0 24 24" class="icon"><path d="M21 3L3 10.5l6 2.5 2.5 6L21 3z"/><path d="M9 13l5-4"/></svg>'
        '<span>Saluran Tele</span></a>'
        '</div>')

NAVBTN = ('<button class="nav-btn" id="mzMusicBtn" type="button"><span>'
          '<svg viewBox="0 0 24 24" class="icon"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>'
          '</span>Musik</button>')

API = r"""const API = 'https://api.audius.co/v1';
const APP = 'MannzzMultifungsi';
const KEY = process.env.AUDIUS_API_KEY || '';
const ID_RE = /^[A-Za-z0-9]{1,24}$/;

function get(path, params, manual) {
  const u = new URL(API + path);
  Object.entries(params || {}).forEach(([k, v]) => u.searchParams.set(k, String(v)));
  u.searchParams.set('app_name', APP);
  return fetch(u, {
    headers: KEY ? { 'x-api-key': KEY } : {},
    redirect: manual ? 'manual' : 'follow',
    signal: AbortSignal.timeout(8000)
  });
}

module.exports = async (req, res) => {
  const q = req.query || {};
  try {
    if (q.stream) {
      const id = String(q.stream);
      if (!ID_RE.test(id)) return res.status(400).json({ message: 'ID tidak valid.' });
      const r = await get('/tracks/' + id + '/stream', {}, true);
      const loc = r.headers.get('location');
      if (loc && /^https:\/\//i.test(loc)) {
        res.setHeader('Cache-Control', 'no-store');
        res.statusCode = 302;
        res.setHeader('Location', loc);
        return res.end();
      }
      return res.status(502).json({ message: 'Lagu tidak bisa diputar.' });
    }

    const text = String(q.q || '').trim().slice(0, 80);
    const r = text ? await get('/tracks/search', { query: text, limit: 20 }) : await get('/tracks/trending', { limit: 20 });
    if (r.status === 401 || r.status === 403) {
      return res.status(502).json({ message: 'Audius meminta API key. Isi AUDIUS_API_KEY di Vercel.' });
    }
    if (!r.ok) return res.status(502).json({ message: 'Layanan musik sedang tidak bisa dihubungi (' + r.status + ').' });
    const j = await r.json();
    const tracks = (j.data || [])
      .filter(t => t && t.id && t.title && t.is_streamable !== false)
      .map(t => ({
        id: String(t.id),
        title: String(t.title).slice(0, 100),
        artist: String((t.user && t.user.name) || '').slice(0, 60),
        art: (t.artwork && (t.artwork['150x150'] || t.artwork['480x480'])) || '',
        dur: parseInt(t.duration, 10) || 0
      }));
    res.setHeader('Cache-Control', 'public, s-maxage=120');
    return res.status(200).json({ success: true, tracks });
  } catch (e) {
    return res.status(502).json({ message: 'Gagal menghubungi layanan musik.' });
  }
};
"""

CSS = r"""
html body .mzm{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));max-width:520px;margin:0 auto;z-index:70;display:flex;align-items:center;gap:6px;padding:10px 8px 8px 10px;border-radius:16px;background:var(--card);color:var(--text);border:1px solid var(--line);box-shadow:0 10px 30px var(--shadow);overflow:hidden}
html body .mzm[hidden]{display:none}
html body .mzm-bar{position:absolute;left:0;right:0;top:0;height:3px;background:var(--line)}
html body .mzm-bar i{display:block;height:100%;width:0;background:var(--accent)}
html body .mzm-main{flex:1;min-width:0;display:flex;align-items:center;gap:10px;background:none;border:none;color:inherit;font:inherit;text-align:left;cursor:pointer;padding:0}
html body .mzm-main img,html body .mzm-ph{width:40px;height:40px;border-radius:10px;object-fit:cover;flex-shrink:0;background:var(--line);display:flex;align-items:center;justify-content:center}
html body .mzm-t{min-width:0;display:flex;flex-direction:column}
html body .mzm-t b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.9rem}
html body .mzm-t small{color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
html body .mzm-b{width:38px;height:38px;border-radius:50%;border:none;background:none;color:var(--text);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;flex-shrink:0}
html body .mzm-b svg{width:20px;height:20px}
html body #mzPlay{background:var(--accent);color:var(--on,#fff)}
html body.mz-hasmini{padding-bottom:84px}
html body .mzs{position:fixed;left:0;right:0;top:0;bottom:0;z-index:95;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.55);overscroll-behavior:contain}
html body .mzs.mz-off{visibility:hidden;pointer-events:none;opacity:0}
html body .mzs-panel{width:min(520px,100%);max-height:88vh;max-height:88dvh;overflow-y:auto;background:var(--card);color:var(--text);border-radius:18px 18px 0 0;padding:16px;border:1px solid var(--line);overscroll-behavior:contain}
html body .mzs-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;font-size:1.05rem}
html body .mzs-head button{background:none;border:none;color:var(--muted);font:inherit;font-weight:700;cursor:pointer}
html body .mzs-tabs{display:flex;border-bottom:1px solid var(--line);margin-bottom:12px}
html body .mzs-tabs button{flex:1;background:none;border:none;border-bottom:2px solid transparent;padding:10px;font:inherit;font-weight:800;color:var(--muted);cursor:pointer}
html body .mzs-tabs button.on{color:var(--text);border-bottom-color:var(--accent)}
html body .mzs-row{display:flex;gap:8px}
html body .mzs-row input{flex:1;min-width:0;padding:12px;border-radius:12px;border:1px solid var(--line);background:var(--bg);color:var(--text);font:inherit}
html body .mzs-btn{padding:0 16px;border-radius:12px;border:none;background:var(--accent);color:var(--on,#fff);font:inherit;font-weight:800;cursor:pointer}
html body .mzs-hint{margin:10px 0;font-size:.8rem;color:var(--muted);min-height:1.2em}
html body .mzs-item{display:flex;align-items:center;gap:10px;width:100%;padding:8px;border-radius:12px;background:none;border:none;color:var(--text);font:inherit;text-align:left;cursor:pointer}
html body .mzs-item.on{background:var(--bg)}
html body .mzs-item img,html body .mzs-item .ph{width:46px;height:46px;border-radius:10px;object-fit:cover;flex-shrink:0;background:var(--line)}
html body .mzs-it{flex:1;min-width:0;display:flex;flex-direction:column}
html body .mzs-it b{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.92rem}
html body .mzs-it small{color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
html body .mzs-d{color:var(--muted);font-size:.78rem;flex-shrink:0}
html body .mzs-yt{position:relative;width:100%;aspect-ratio:16/9;background:#000;border-radius:12px;overflow:hidden;margin-top:10px}
html body .mzs-yt iframe{position:absolute;left:0;top:0;width:100%;height:100%;border:0}
html body .mz-offp{position:fixed!important;left:-9999px;top:0;width:320px;pointer-events:none}
html.mz-musiclock,html.mz-musiclock body{overflow:hidden!important}
"""

JS = r"""
(function(){
  var btn = document.getElementById('mzMusicBtn');
  if (!btn) return;
  var $ = function(id){ return document.getElementById(id); };
  var audio = new Audio();
  audio.preload = 'none';
  var S = { mode: '', results: [], queue: [], idx: -1, yt: null, ytState: -1, built: false, loaded: false };
  var IP = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4l13 8-13 8z"/></svg>';
  var IQ = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>';
  var IN = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 4l10 8-10 8zM18 4h2v16h-2z"/></svg>';
  var IX = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  var mini, sheet;

  function fmt(n){ n = Math.max(0, Math.round(n || 0)); return Math.floor(n / 60) + ':' + String(n % 60).padStart(2, '0'); }
  function safeImg(u){ return (typeof u === 'string' && /^https:\/\//.test(u)) ? u : ''; }

  function build(){
    if (S.built) return;
    S.built = true;
    mini = document.createElement('div');
    mini.className = 'mzm';
    mini.hidden = true;
    mini.innerHTML = '<div class="mzm-bar"><i id="mzBar"></i></div>'
      + '<button type="button" class="mzm-main" id="mzMiniOpen"><img id="mzArt" alt="" hidden><span class="mzm-ph" id="mzArtPh">&#9834;</span>'
      + '<span class="mzm-t"><b id="mzTitle"></b><small id="mzSub"></small></span></button>'
      + '<button type="button" class="mzm-b" id="mzPlay" aria-label="Putar atau jeda"></button>'
      + '<button type="button" class="mzm-b" id="mzNext" aria-label="Berikutnya"></button>'
      + '<button type="button" class="mzm-b" id="mzClose" aria-label="Tutup pemutar"></button>';
    document.body.appendChild(mini);

    sheet = document.createElement('div');
    sheet.className = 'mzs mz-off';
    sheet.innerHTML = '<div class="mzs-panel">'
      + '<div class="mzs-head"><b>Musik</b><button type="button" id="mzSheetX">Tutup</button></div>'
      + '<div class="mzs-tabs"><button type="button" class="on" data-mt="cari">Cari</button><button type="button" data-mt="yt">YouTube</button></div>'
      + '<div id="mz-cari"><div class="mzs-row"><input id="mzQ" type="search" placeholder="Cari lagu atau artis..." maxlength="80" autocomplete="off"><button type="button" class="mzs-btn" id="mzGo">Cari</button></div>'
      + '<p class="mzs-hint" id="mzStat"></p><div id="mzList"></div>'
      + '<p class="mzs-hint">Katalog dari Audius (musik artis independen). Hargai karya artisnya.</p></div>'
      + '<div id="mz-yt" class="mz-offp"><div class="mzs-row"><input id="mzYl" type="url" placeholder="Tempel link YouTube..." autocomplete="off"><button type="button" class="mzs-btn" id="mzYgo">Putar</button></div>'
      + '<p class="mzs-hint" id="mzYstat"></p><div class="mzs-yt"><div id="mzYtBox"></div></div></div>'
      + '</div>';
    document.body.appendChild(sheet);

    $('mzPlay').innerHTML = IP;
    $('mzNext').innerHTML = IN;
    $('mzClose').innerHTML = IX;

    sheet.addEventListener('click', function(e){ if (e.target === sheet) closeSheet(); });
    $('mzSheetX').addEventListener('click', closeSheet);
    $('mzMiniOpen').addEventListener('click', openSheet);
    $('mzPlay').addEventListener('click', toggle);
    $('mzNext').addEventListener('click', next);
    $('mzClose').addEventListener('click', stopAll);
    $('mzGo').addEventListener('click', search);
    $('mzQ').addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); search(); } });
    $('mzYgo').addEventListener('click', goYt);
    $('mzYl').addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); goYt(); } });
    sheet.querySelectorAll('[data-mt]').forEach(function(b){
      b.addEventListener('click', function(){ setTab(b.dataset.mt); });
    });
  }

  function setTab(t){
    sheet.querySelectorAll('[data-mt]').forEach(function(b){ b.classList.toggle('on', b.dataset.mt === t); });
    $('mz-cari').classList.toggle('mz-offp', t !== 'cari');
    $('mz-yt').classList.toggle('mz-offp', t !== 'yt');
  }
  function openSheet(){
    build();
    if (typeof closeSidebar === 'function') closeSidebar();
    sheet.classList.remove('mz-off');
    document.documentElement.classList.add('mz-musiclock');
    if (!S.loaded) { S.loaded = true; search(); }
  }
  function closeSheet(){
    if (!sheet) return;
    sheet.classList.add('mz-off');
    document.documentElement.classList.remove('mz-musiclock');
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
    $('mzNext').style.display = S.mode === 'audius' ? '' : 'none';
  }

  /* ----- Audius ----- */
  function renderList(){
    var box = $('mzList');
    box.replaceChildren();
    var cur = (S.mode === 'audius' && S.queue[S.idx]) ? S.queue[S.idx].id : '';
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
      b.append(pic, info, d);
      b.addEventListener('click', function(){ S.queue = S.results.slice(); S.idx = i; startAudius(); });
      box.appendChild(b);
    });
  }
  async function search(){
    var q = $('mzQ').value.trim();
    stat(q ? 'Mencari...' : 'Memuat lagu populer...');
    try {
      var r = await fetch('/api/music?q=' + encodeURIComponent(q), { cache: 'no-store' });
      var d = await r.json().catch(function(){ return {}; });
      if (!r.ok || !d.success) { stat(d.message || 'Gagal memuat lagu.'); return; }
      S.results = d.tracks || [];
      stat(S.results.length ? '' : 'Tidak ada hasil.');
      renderList();
    } catch (e) { stat('Koneksi bermasalah.'); }
  }
  function startAudius(){
    var t = S.queue[S.idx];
    if (!t) return;
    stopYt();
    S.mode = 'audius';
    audio.src = '/api/music?stream=' + encodeURIComponent(t.id);
    var p = audio.play();
    if (p && p.catch) p.catch(function(){ stat('Lagu gagal diputar, coba lagu lain.'); });
    showMini(t.title, t.artist, t.art);
    renderList();
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
    if (S.mode !== 'audius') return;
    if (S.idx + 1 < S.queue.length) { S.idx++; startAudius(); } else { audio.pause(); }
  }
  function prev(){
    if (S.mode !== 'audius') return;
    if (audio.currentTime > 4 || S.idx === 0) { audio.currentTime = 0; return; }
    S.idx--; startAudius();
  }
  audio.addEventListener('play', function(){ if (S.mode === 'audius') setIcon(true); });
  audio.addEventListener('pause', function(){ if (S.mode === 'audius') setIcon(false); });
  audio.addEventListener('ended', next);
  audio.addEventListener('error', function(){
    if (S.mode === 'audius' && audio.getAttribute('src')) { stat('Lagu gagal diputar, coba lagu lain.'); setIcon(false); }
  });
  audio.addEventListener('timeupdate', function(){
    var bar = $('mzBar');
    if (bar && audio.duration && isFinite(audio.duration)) bar.style.width = Math.min(100, audio.currentTime / audio.duration * 100) + '%';
  });

  /* ----- YouTube ----- */
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
      if (d && d.title) { $('mzTitle').textContent = d.title; $('mzSub').textContent = d.author || 'YouTube'; }
    } catch (err) {}
    if (e.data === 0) { $('mzBar').style.width = '0'; }
  }
  function playYt(id){
    audio.pause();
    S.mode = 'yt';
    showMini('YouTube', 'Memuat...', 'https://i.ytimg.com/vi/' + id + '/mqdefault.jpg');
    setIcon(true);
    ytApi(function(){
      if (S.yt && S.yt.loadVideoById) { S.yt.loadVideoById(id); return; }
      S.yt = new YT.Player('mzYtBox', {
        videoId: id, width: '100%', height: '100%',
        playerVars: { playsinline: 1, rel: 0, autoplay: 1 },
        events: { onReady: function(e){ e.target.playVideo(); }, onStateChange: onYt }
      });
    });
  }
  function stopYt(){ try { if (S.yt && S.yt.stopVideo) S.yt.stopVideo(); } catch (e) {} S.ytState = -1; }
  function goYt(){
    var v = $('mzYl').value.trim();
    var m = YT_RE.exec(v);
    if (!m) { ystat('Link YouTube tidak dikenali.'); return; }
    ystat('');
    playYt(m[1]);
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
    renderList();
  }
})();
"""

shutil.copy(f, f + '.bak43')
s = s[:m.end()] + '\n' + ROW2 + s[m.end():]
nav = (re.search(r'<button class="nav-btn" data-tab="tab-pengaturan">.*?</button>', s, re.S)
       or re.search(r'<button class="nav-btn" data-tab="tab-alat">.*?</button>', s, re.S))
s = s[:nav.end()] + '\n' + NAVBTN + s[nav.end():]
s = s.replace('</head>', '<style id="mz-music-css">' + CSS + '</style>\n</head>', 1)
i = s.rfind('</body>')
s = s[:i] + '<script id="mz-music-js">' + JS + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)

os.makedirs('api', exist_ok=True)
if os.path.exists('api/music.js'):
    shutil.copy('api/music.js', 'api/music.js.bak43')
open('api/music.js', 'w', encoding='utf-8').write(API)
print('Saluran WA + Tele di sidebar : OK')
print('Fitur Musik (index.html)     : OK')
print('api/music.js                 : OK')
