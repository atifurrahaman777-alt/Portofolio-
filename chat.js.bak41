(() => {
  const $ = id => document.getElementById(id);
  const root = $('gc'), list = $('gc-list'), input = $('gc-input'), act = $('gc-action'), status = $('gc-status');
  const palette = ['#ff7b7b', '#c792ea', '#4dd0e1', '#ffd166', '#7bd88f', '#ff9f68', '#6fa8ff'];
  const bgs = ['#7c3aed', '#0f766e', '#be185d', '#b45309', '#1d4ed8', '#15803d'];
  const IC = {
    users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    back: '<path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/>',
    bell: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    moon: '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    sun: '<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/>',
    eye: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    eraser: '<path d="M7 21h13"/><path d="M5.5 13.5l8-8a2 2 0 0 1 2.8 0l2.2 2.2a2 2 0 0 1 0 2.8L11 18H8l-2.5-2.5a2 2 0 0 1 0-2z"/>',
    smile: '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    mic: '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v4"/>',
    send: '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    bars: '<path d="M6 20V10M12 20V4M18 20v-6"/>'
  };
  const ic = (k, s = 22) => '<svg viewBox="0 0 24 24" width="' + s + '" height="' + s + '" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + IC[k] + '</svg>';
  const ls = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
    del(k) { try { localStorage.removeItem(k); } catch {} }
  };

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function colorFor(name) {
    let h = 0;
    for (const c of String(name)) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    return palette[h % palette.length];
  }
  const ini = name => (String(name).trim()[0] || '?').toUpperCase();
  function ago(ts) {
    const m = Math.floor((Date.now() - ts) / 60000);
    if (m < 1) return 'baru saja';
    if (m < 60) return m + ' mnt lalu';
    return Math.floor(m / 60) + ' jam lalu';
  }
  function avatarEl(name, avatar, size) {
    const av = el('div', 'gc-av');
    av.style.cssText = 'width:' + size + 'px;height:' + size + 'px;font-size:' + Math.round(size * 0.42) + 'px;background:' + colorFor(name);
    if (avatar) {
      const img = new Image();
      img.alt = ''; img.referrerPolicy = 'no-referrer'; img.src = avatar;
      img.onerror = () => { img.remove(); av.textContent = ini(name); };
      av.appendChild(img);
    } else av.textContent = ini(name);
    return av;
  }

  let cid = ls.get('chat_cid') || '';
  if (!cid) { cid = Math.random().toString(36).slice(2, 12) + Date.now().toString(36); ls.set('chat_cid', cid); }

  function profile() {
    let name = ls.get('chat_name'), avatar = ls.get('chat_avatar') || '';
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const v = localStorage.getItem(localStorage.key(i));
        if (!v || v[0] !== '{') continue;
        try {
          const o = JSON.parse(v);
          const n = o.displayName || o.name || o.username || o.nama;
          const a = o.avatar || o.photo || o.foto || o.photoURL || o.image || o.pfp || o.avatarUrl;
          if (!name && typeof n === 'string' && n.trim()) name = n.trim().slice(0, 20);
          if (!avatar && typeof a === 'string' && /^https:\/\//.test(a)) avatar = a;
        } catch {}
      }
    } catch {}
    return { name, avatar };
  }
  function ensureProfile() {
    const p = profile();
    if (!p.name) {
      const n = (prompt('Nama buat chat:') || '').trim().slice(0, 20);
      if (!n) return null;
      ls.set('chat_name', n);
      p.name = n;
    }
    return p;
  }

  let data = { messages: [], stories: [], notes: [], online: 1 };
  let msgSig = null, storySig = null, noteSig = null;
  let replyTo = null, loadedOnce = false, force = true, storyTimer = null;
  let bellOn = ls.get('chat_bell') !== '0';
  let clearTs = parseInt(ls.get('chat_clear'), 10) || 0;
  let ac = null, rec = null, recording = false;

  $('gc-users').innerHTML = ic('users');
  $('gc-back').innerHTML = ic('back');
  $('gc-eye').innerHTML = ic('eye');
  $('gc-eraser').innerHTML = ic('eraser');
  $('gc-sticker').innerHTML = ic('smile');
  function syncBell() { $('gc-bell').innerHTML = ic('bell') + (bellOn ? '<i class="gc-bdot"></i>' : ''); }
  function syncTheme() { $('gc-theme').innerHTML = ic(root.classList.contains('light') ? 'sun' : 'moon'); }
  function renderMe() {
    const p = profile();
    const box = $('gc-me');
    box.textContent = '';
    box.appendChild(avatarEl(p.name || '?', p.avatar, 38));
  }
  function syncAct() {
    if (recording) { act.classList.add('rec'); act.innerHTML = ic('send'); return; }
    act.classList.remove('rec');
    act.innerHTML = input.value.trim() ? ic('send') : ic('mic');
  }
  if (ls.get('chat_light') === '1') root.classList.add('light');
  if (ls.get('chat_hidetop') === '1') $('gc-top').style.display = 'none';
  syncBell(); syncTheme(); renderMe(); syncAct();

  function beep() {
    try {
      const A = window.AudioContext || window.webkitAudioContext;
      ac = ac || new A();
      const o = ac.createOscillator(), g = ac.createGain();
      o.connect(g); g.connect(ac.destination);
      o.frequency.value = 880;
      g.gain.setValueAtTime(0.08, ac.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ac.currentTime + 0.25);
      o.start(); o.stop(ac.currentTime + 0.25);
    } catch {}
  }

  async function post(body) {
    try {
      const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) { status.textContent = d.message || 'Gagal.'; return false; }
      status.textContent = '';
      return true;
    } catch { status.textContent = 'Koneksi bermasalah.'; return false; }
  }
  // === akhir bagian 2 ===

  function openStory(s) {
    const ov = $('gc-overlay');
    ov.textContent = '';
    ov.style.background = bgs[s.bg % bgs.length];
    const bar = el('div', 'gc-ov-bar'); bar.appendChild(document.createElement('i'));
    const top = el('div', 'gc-ov-top');
    const who = el('div');
    who.append(el('b', '', s.name), el('small', '', ago(s.ts)));
    top.append(avatarEl(s.name, s.avatar, 40), who);
    ov.append(bar, top, el('div', 'gc-ov-body', s.text));
    ov.hidden = false;
    clearTimeout(storyTimer);
    storyTimer = setTimeout(closeStory, 6000);
  }
  function closeStory() { clearTimeout(storyTimer); $('gc-overlay').hidden = true; }
  $('gc-overlay').addEventListener('click', closeStory);

  function openComposer(o) {
    const old = $('gc-sheet');
    if (old) old.remove();
    if (!$('gc-sheet-css')) {
      const st = document.createElement('style');
      st.id = 'gc-sheet-css';
      st.textContent = '#gc-sheet textarea::placeholder{color:rgba(255,255,255,.7)}#gc-sheet button{font:inherit;cursor:pointer}';
      document.head.appendChild(st);
    }
    const p0 = profile();
    const light = root.classList.contains('light');
    const C = light
      ? { bg: '#ffffff', fg: '#111b21', mu: '#667781', ln: '#d9dee1', fi: '#f0f2f5' }
      : { bg: '#1f2c33', fg: '#e9edef', mu: '#8696a0', ln: '#2f3f47', fi: '#2a3942' };
    let bg = Math.floor(Math.random() * bgs.length);

    const wrap = el('div');
    wrap.id = 'gc-sheet';
    wrap.style.cssText = 'position:fixed;left:0;right:0;top:0;bottom:0;z-index:60;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.55);overscroll-behavior:contain';
    const panel = el('div');
    panel.style.cssText = 'width:100%;max-width:520px;box-sizing:border-box;background:' + C.bg + ';color:' + C.fg + ';border-radius:18px 18px 0 0;padding:16px;max-height:90vh;overflow-y:auto;display:flex;flex-direction:column;gap:12px';

    const head = el('div');
    head.style.cssText = 'display:flex;justify-content:space-between;align-items:center';
    const title = el('b', '', o.title);
    title.style.fontSize = '1.05rem';
    const x = el('button', '', 'Tutup');
    x.type = 'button';
    x.style.cssText = 'background:none;border:none;color:' + C.mu + ';font-weight:700';
    head.append(title, x);
    panel.appendChild(head);

    let nameIn = null;
    if (!p0.name) {
      nameIn = el('input');
      nameIn.type = 'text';
      nameIn.maxLength = 20;
      nameIn.placeholder = 'Nama kamu (maks 20 huruf)';
      nameIn.style.cssText = 'padding:12px;border-radius:12px;border:1px solid ' + C.ln + ';background:' + C.fi + ';color:' + C.fg + ';font:inherit';
      panel.appendChild(nameIn);
    }

    const ta = el('textarea');
    ta.maxLength = o.max;
    ta.rows = o.colors ? 4 : 3;
    ta.placeholder = o.placeholder;
    ta.value = o.initial || '';
    let box = ta;
    if (o.colors) {
      box = el('div');
      box.style.cssText = 'border-radius:16px;padding:18px;min-height:130px;display:flex;align-items:center;justify-content:center;transition:background .2s';
      ta.style.cssText = 'width:100%;box-sizing:border-box;background:transparent;border:none;outline:none;resize:none;color:#fff;text-align:center;font:inherit;font-size:1.25rem;font-weight:700;text-shadow:0 1px 3px rgba(0,0,0,.35)';
      box.appendChild(ta);
      box.style.background = bgs[bg];
    } else {
      ta.style.cssText = 'width:100%;box-sizing:border-box;padding:12px;border-radius:12px;border:1px solid ' + C.ln + ';background:' + C.fi + ';color:' + C.fg + ';font:inherit;resize:none;outline:none';
    }
    panel.appendChild(box);

    const cnt = el('div', '', ta.value.length + '/' + o.max);
    cnt.style.cssText = 'text-align:right;font-size:.78rem;color:' + C.mu;
    ta.addEventListener('input', () => { cnt.textContent = ta.value.length + '/' + o.max; });
    panel.appendChild(cnt);

    if (o.colors) {
      const row = el('div');
      row.style.cssText = 'display:flex;gap:10px;justify-content:center;flex-wrap:wrap';
      const dots = [];
      const mark = () => dots.forEach((d, i) => { d.style.borderColor = i === bg ? C.fg : 'transparent'; });
      bgs.forEach((c, i) => {
        const d = el('button');
        d.type = 'button';
        d.setAttribute('aria-label', 'Warna ' + (i + 1));
        d.style.cssText = 'width:32px;height:32px;border-radius:50%;border:3px solid transparent;background:' + c;
        d.addEventListener('click', () => { bg = i; box.style.background = c; mark(); });
        row.appendChild(d);
        dots.push(d);
      });
      mark();
      panel.appendChild(row);
    }

    const hint = el('div');
    hint.style.cssText = 'min-height:1.2em;font-size:.82rem;color:#ef4444';
    panel.appendChild(hint);

    const acts = el('div');
    acts.style.cssText = 'display:flex;gap:10px';
    const go = el('button', '', o.cta);
    go.type = 'button';
    go.style.cssText = 'flex:1;padding:13px;border-radius:12px;border:none;background:#25d366;color:#052e16;font-weight:800';

    let busy = false;
    const close = () => { wrap.remove(); };
    const submit = async remove => {
      if (busy) return;
      const t = remove ? '' : ta.value.trim();
      let name = p0.name;
      if (!name) {
        name = ((nameIn && nameIn.value) || '').trim().slice(0, 20);
        if (!name) { hint.textContent = 'Isi namamu dulu.'; return; }
      }
      if (!t && !o.allowEmpty) { hint.textContent = 'Tulisannya masih kosong.'; return; }
      busy = true;
      go.disabled = true;
      hint.textContent = '';
      if (!p0.name) ls.set('chat_name', name);
      const ok = await o.send(name, p0.avatar, t, bg);
      busy = false;
      go.disabled = false;
      if (ok) { close(); renderMe(); }
      else hint.textContent = status.textContent || 'Gagal, coba lagi.';
    };

    if (o.removable) {
      const rm = el('button', '', 'Hapus');
      rm.type = 'button';
      rm.style.cssText = 'padding:13px 18px;border-radius:12px;border:1px solid ' + C.ln + ';background:none;color:#ef4444;font-weight:800';
      rm.addEventListener('click', () => submit(true));
      acts.appendChild(rm);
    }
    go.addEventListener('click', () => submit(false));
    acts.appendChild(go);
    panel.appendChild(acts);

    x.addEventListener('click', close);
    wrap.addEventListener('click', e => { if (e.target === wrap) close(); });
    wrap.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    ta.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(false); }
    });
    wrap.appendChild(panel);
    document.body.appendChild(wrap);
    ta.focus();
  }

  function addStory() {
    openComposer({
      title: 'Story baru', cta: 'Kirim story', max: 140, colors: true,
      placeholder: 'Apa yang lagi kamu pikirin?',
      send: async (name, avatar, text, bg) => {
        const ok = await post({ type: 'story', name, avatar, text, bg });
        if (ok) { storySig = null; load(); }
        return ok;
      }
    });
  }
  function addNote(current) {
    openComposer({
      title: 'Catatan', cta: 'Simpan', max: 60, initial: current || '',
      allowEmpty: true, removable: !!current, placeholder: 'Tulis catatan singkat...',
      send: async (name, avatar, text) => {
        const ok = await post({ type: 'note', name, avatar, text });
        if (ok) { noteSig = null; load(); }
        return ok;
      }
    });
  }

  function storyItem(name, avatar, story, own) {
    const it = el('div', 'gc-item');
    const ring = el('div', 'gc-ring ' + (story ? 'on' : 'dashed'));
    ring.appendChild(avatarEl(name, avatar, 60));
    if (own) {
      const plus = el('button', 'gc-plus');
      plus.type = 'button';
      plus.innerHTML = ic('plus', 14);
      plus.addEventListener('click', e => { e.stopPropagation(); addStory(); });
      ring.appendChild(plus);
    }
    it.append(ring, el('div', 'gc-lbl', own ? 'Story-mu' : name), el('div', 'gc-sub', story ? ago(story.ts) : (own ? 'Tambah' : '')));
    it.addEventListener('click', () => { if (story) openStory(story); else if (own) addStory(); });
    return it;
  }
  function renderStories() {
    const me = profile();
    const box = $('gc-stories');
    box.textContent = '';
    const byUser = new Map();
    data.stories.forEach(s => { if (!byUser.has(s.name)) byUser.set(s.name, s); });
    box.appendChild(storyItem(me.name || 'Kamu', me.avatar, me.name ? byUser.get(me.name) : null, true));
    byUser.forEach((s, name) => { if (name !== me.name) box.appendChild(storyItem(name, s.avatar, s, false)); });
  }

  function noteItem(name, avatar, note, own) {
    const it = el('div', 'gc-item');
    const b = el('div', 'gc-nb' + (note ? '' : ' new'));
    if (note) {
      const h = el('div', 'gc-nh');
      h.innerHTML = ic('bars', 12);
      h.appendChild(el('span', '', own ? 'Catatanmu' : name));
      b.append(h, el('div', 'gc-nt', note.text));
    } else b.textContent = 'Catatan baru';
    it.append(b, el('div', 'gc-dots'), avatarEl(name, avatar, 56), el('div', 'gc-lbl', own ? 'Catatanmu' : name));
    if (own) it.addEventListener('click', () => addNote(note ? note.text : ''));
    return it;
  }
  function renderNotes() {
    const me = profile();
    const box = $('gc-notes');
    box.textContent = '';
    const mine = me.name ? data.notes.find(n => n.name === me.name) : null;
    box.appendChild(noteItem(me.name || 'Kamu', me.avatar, mine, true));
    data.notes.filter(n => n.name !== me.name).forEach(n => box.appendChild(noteItem(n.name, n.avatar, n, false)));
  }
  // === akhir bagian 3 ===

  function setReply(m) {
    replyTo = { id: m.id, name: m.name, text: (m.text || '🎤 Pesan suara').slice(0, 80) };
    $('gc-rname').textContent = m.name;
    $('gc-rtext').textContent = m.text || '🎤 Pesan suara';
    $('gc-replybar').classList.add('on');
    input.focus();
  }
  function clearReply() { replyTo = null; $('gc-replybar').classList.remove('on'); }
  $('gc-rx').addEventListener('click', clearReply);

  function renderMessages() {
    const me = profile().name;
    const msgs = data.messages.filter(m => m.ts > clearTs);
    const near = list.scrollHeight - list.scrollTop - list.clientHeight < 100;
    list.textContent = '';
    if (!msgs.length) { list.appendChild(el('div', 'gc-day', 'Belum ada pesan. Mulai obrolan!')); return; }
    let day = '', prev = null;
    msgs.forEach(m => {
      const d = new Date(m.ts), key = d.toDateString();
      if (key !== day) {
        day = key; prev = null;
        list.appendChild(el('div', 'gc-day', key === new Date().toDateString() ? 'Hari ini'
          : d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })));
      }
      const mine = m.name === me;
      const first = !prev || prev.name !== m.name;
      const row = el('div', 'gc-row' + (mine ? ' me' : '') + (first ? ' first' : ''));
      if (!mine) row.appendChild(first ? avatarEl(m.name, m.avatar, 36) : el('div', 'gc-sp'));
      const bub = el('div', 'gc-bub');
      if (!mine && first) {
        const n = el('span', 'gc-name', m.name);
        n.style.color = colorFor(m.name);
        bub.appendChild(n);
      }
      if (m.reply && m.reply.name) {
        const q = el('div', 'gc-quote');
        q.append(el('b', '', m.reply.name), el('span', '', m.reply.text));
        bub.appendChild(q);
      }
      bub.append((m.aud ? voiceEl(m) : el('span', 'gc-text', m.text)),
        el('span', 'gc-time', d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })));
      bub.addEventListener('click', () => setReply(m));
      row.appendChild(bub);
      list.appendChild(row);
      prev = m;
    });
    if (near || force) { list.scrollTop = list.scrollHeight; force = false; }
  }

  async function load() {
    try {
      const r = await fetch('/api/chat?cid=' + encodeURIComponent(cid), { cache: 'no-store' });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) { status.textContent = d.message || 'Gagal memuat chat.'; return; }
      status.textContent = '';
      data = { messages: d.messages || [], stories: d.stories || [], notes: d.notes || [], online: d.online || 1 };
      $('gc-online').textContent = data.online + ' online';

      const last = data.messages[data.messages.length - 1];
      const sig = data.messages.length + ':' + (last ? last.id : '');
      if (sig !== msgSig) {
        const me = profile().name;
        if (loadedOnce && bellOn && last && last.name !== me) beep();
        msgSig = sig;
        renderMessages();
      }
      const ss = data.stories.map(s => s.id).join(',');
      if (ss !== storySig) { storySig = ss; renderStories(); }
      const ns = JSON.stringify(data.notes);
      if (ns !== noteSig) { noteSig = ns; renderNotes(); }
      loadedOnce = true;
    } catch { status.textContent = 'Koneksi bermasalah.'; }
  }

  async function sendMsg() {
    const text = input.value.trim();
    if (!text) return;
    const p = ensureProfile();
    if (!p) return;
    act.disabled = true;
    if (await post({ name: p.name, text, avatar: p.avatar, reply: replyTo })) {
      input.value = ''; clearReply(); force = true; msgSig = null;
      $('gc-emoji').classList.remove('on');
      renderMe(); await load();
    }
    act.disabled = false;
    syncAct();
  }

  let mr = null, chunks = [], recStart = 0, recTick = null, recCancel = false, recStream = null;
  const fmt = n => Math.floor(n / 60) + ':' + String(n % 60).padStart(2, '0');
  function stopTracks() { if (recStream) recStream.getTracks().forEach(t => t.stop()); recStream = null; }
  function endRec() {
    clearInterval(recTick); recording = false;
    input.readOnly = false; input.placeholder = 'Tulis pesan';
    stopTracks(); syncAct();
  }
  async function toggleVoice() {
    if (recording) { if (mr && mr.state === 'recording') mr.stop(); return; }
    if (!navigator.mediaDevices || !window.MediaRecorder) { status.textContent = 'Browser ini belum mendukung rekam suara.'; return; }
    const p = ensureProfile();
    if (!p) return;
    try {
      recStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch { status.textContent = 'Izin mikrofon ditolak. Izinkan lewat setelan situs Chrome.'; return; }
    const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];
    const mime = types.find(t => MediaRecorder.isTypeSupported(t)) || '';
    chunks = []; recCancel = false;
    try { mr = new MediaRecorder(recStream, mime ? { mimeType: mime, audioBitsPerSecond: 24000 } : { audioBitsPerSecond: 24000 }); }
    catch { stopTracks(); status.textContent = 'Gagal memulai rekaman.'; return; }
    mr.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };
    mr.onstop = async () => {
      const dur = Math.max(1, Math.round((Date.now() - recStart) / 1000));
      const type = mr.mimeType || mime || 'audio/webm';
      endRec();
      if (recCancel || !chunks.length) return;
      const blob = new Blob(chunks, { type });
      if (blob.size > 280000) { status.textContent = 'Rekaman terlalu besar, coba lebih pendek.'; return; }
      const dataUrl = await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = () => res(''); r.readAsDataURL(blob); });
      if (!dataUrl) { status.textContent = 'Gagal membaca rekaman.'; return; }
      act.disabled = true;
      if (await post({ name: p.name, text: '', avatar: p.avatar, reply: replyTo, audio: dataUrl, dur })) {
        clearReply(); force = true; msgSig = null; await load();
      }
      act.disabled = false; syncAct();
    };
    recStart = Date.now(); recording = true;
    input.readOnly = true; syncAct();
    recTick = setInterval(() => {
      const t = Math.round((Date.now() - recStart) / 1000);
      input.placeholder = '🔴 Merekam ' + fmt(t) + ' · ketuk di sini untuk batal';
      if (t >= 40 && mr.state === 'recording') mr.stop();
    }, 250);
    mr.start();
  }
  input.addEventListener('click', () => {
    if (recording && mr && mr.state === 'recording') { recCancel = true; mr.stop(); }
  });
  const audCache = new Map();
  let curAudio = null, curReset = null, curBtn = null;
  const PLAY = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M7 4l13 8-13 8z"/></svg>';
  const PAUSE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>';
  function voiceEl(m) {
    const box = el('div', 'gc-voice');
    const btn = el('button', 'gc-play');
    btn.type = 'button'; btn.innerHTML = PLAY;
    const track = el('div', 'gc-track'), fill = document.createElement('i');
    track.appendChild(fill);
    box.append(btn, track, el('span', 'gc-vdur', fmt(m.dur || 1)));
    btn.addEventListener('click', async e => {
      e.stopPropagation();
      if (curAudio && curBtn === btn) { if (curAudio.paused) curAudio.play(); else curAudio.pause(); return; }
      if (curAudio) curAudio.pause();
      if (curReset) curReset();
      btn.disabled = true;
      let url = audCache.get(m.id);
      if (!url) {
        try {
          const r = await fetch('/api/chat?audio=' + encodeURIComponent(m.id), { cache: 'no-store' });
          const d = await r.json().catch(() => ({}));
          if (!r.ok || !d.audio) { status.textContent = d.message || 'Audio tidak tersedia.'; btn.disabled = false; return; }
          url = d.audio; audCache.set(m.id, url);
        } catch { status.textContent = 'Koneksi bermasalah.'; btn.disabled = false; return; }
      }
      btn.disabled = false;
      const a = new Audio(url);
      const reset = () => { btn.innerHTML = PLAY; fill.style.width = '0'; if (curBtn === btn) { curAudio = null; curBtn = null; curReset = null; } };
      curAudio = a; curBtn = btn; curReset = reset;
      a.addEventListener('timeupdate', () => {
        const d = a.duration && isFinite(a.duration) ? a.duration : (m.dur || 1);
        fill.style.width = Math.min(100, a.currentTime / d * 100) + '%';
      });
      a.addEventListener('play', () => { btn.innerHTML = PAUSE; });
      a.addEventListener('pause', () => { if (!a.ended) btn.innerHTML = PLAY; });
      a.addEventListener('ended', reset);
      a.play().catch(() => { status.textContent = 'Gagal memutar audio.'; reset(); });
    });
    return box;
  }
  // === akhir bagian 4 ===

  act.addEventListener('click', () => { if (input.value.trim()) sendMsg(); else toggleVoice(); });
  input.addEventListener('input', syncAct);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); sendMsg(); } });

  $('gc-back').addEventListener('click', () => { if (history.length > 1) history.back(); else location.href = '/'; });
  $('gc-theme').addEventListener('click', () => {
    root.classList.toggle('light');
    ls.set('chat_light', root.classList.contains('light') ? '1' : '0');
    syncTheme();
  });
  $('gc-bell').addEventListener('click', () => {
    bellOn = !bellOn;
    ls.set('chat_bell', bellOn ? '1' : '0');
    syncBell();
    if (bellOn) beep();
  });
  $('gc-eye').addEventListener('click', () => {
    const top = $('gc-top');
    const hide = top.style.display !== 'none';
    top.style.display = hide ? 'none' : '';
    ls.set('chat_hidetop', hide ? '1' : '0');
  });
  // === akhir bagian 5a ===

  $('gc-eraser').addEventListener('click', () => {
    if (clearTs) {
      if (!confirm('Tampilkan lagi semua pesan?')) return;
      clearTs = 0; ls.del('chat_clear');
    } else {
      if (!confirm('Bersihkan tampilan chat? (hanya di perangkatmu, pesan tidak dihapus)')) return;
      clearTs = Date.now(); ls.set('chat_clear', String(clearTs));
    }
    msgSig = null; force = true; load();
  });
  $('gc-users').addEventListener('click', () => {
    const names = [...new Set(data.messages.map(m => m.name).concat(data.stories.map(s => s.name), data.notes.map(n => n.name)))];
    alert('Anggota aktif (' + names.length + '):\n' + (names.join('\n') || '-'));
  });

  const emo = '😀 😃 😄 😁 😆 😅 🤣 😂 🙂 🙃 😉 😊 😇 🥰 😍 🤩 😘 😗 😋 😛 😜 🤪 😝 🤑 🤗 🤭 🤫 🤔 🤐 😐 😑 😶 😏 😒 🙄 😬 😌 😔 😪 😴 😷 🤒 🤕 🤢 🤮 🥵 🥶 🥴 😵 🤯 🤠 🥳 😎 🤓 🧐 😕 😟 🙁 😮 😲 😳 🥺 😦 😨 😰 😥 😢 😭 😱 😖 😣 😞 😓 😩 😫 🥱 😤 😡 😠 🤬 😈 👿 💀 👻 👽 🤖 💩 🙈 🙉 🙊 👍 👎 👌 ✌️ 🤞 🤟 🤘 👈 👉 👆 👇 👋 🤝 👏 🙌 🙏 💪 ❤️ 🧡 💛 💚 💙 💜 🖤 🤍 💔 💯 💢 💥 💫 💦 🔥 ✨ ⭐ 🎉 🎊 🎁 🏆 ⚽ 🎮 🎧 🎵 📱 💻 💬 👀 ✅ ❌ ⚠️ 🍕 🍔 🍟 🍜 🍗 ☕ 🍺 🐶 🐱 🐹 🐸 🐵 🌹 🌈 ☀️ 🌙'.split(' ');
  const ep = $('gc-emoji');
  emo.forEach(e => {
    const b = el('button', '', e);
    b.type = 'button';
    b.addEventListener('click', () => { input.value += e; syncAct(); input.focus(); });
    ep.appendChild(b);
  });
  $('gc-sticker').addEventListener('click', () => ep.classList.toggle('on'));

  $('gc-me').style.cursor = 'pointer';
  $('gc-me').addEventListener('click', () => {
    const p = profile();
    const n = prompt('Nama (maks 20 huruf):', p.name || '');
    if (n === null) return;
    if (n.trim()) ls.set('chat_name', n.trim().slice(0, 20));
    const a = prompt('Link foto profil (harus https://). Kosongkan untuk hapus:', p.avatar || '');
    if (a !== null) {
      const u = a.trim();
      if (!u) ls.del('chat_avatar');
      else if (/^https:\/\/[^\s"'<>]{1,280}$/.test(u)) ls.set('chat_avatar', u);
      else { status.textContent = 'Link harus diawali https://'; return; }
    }
    status.textContent = '';
    renderMe(); msgSig = null; load();
  });
  setInterval(() => { if (!document.hidden) load(); }, 8000);
  load();
})();
