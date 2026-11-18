import shutil

def rep(s, old, new, label):
    n = s.count(old)
    if n != 1:
        print('GAGAL: ' + label + ' (ditemukan ' + str(n) + ' kali). Tidak ada yang diubah.')
        raise SystemExit
    return s.replace(old, new, 1)

f = 'chat.js'
s = open(f, encoding='utf-8', errors='surrogateescape').read()
h = open('chat.html', encoding='utf-8').read()
if 'function openMsgMenu' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

s = rep(s, 'let ac = null, rec = null, recording = false;',
        'let ac = null, rec = null, recording = false;\n  let isOwner = false, banned = false, bans = [], lastTs = 0;', 'variabel awal')
s = rep(s, "const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });",
        "const r = await fetch('/api/chat', { method: 'POST', headers: Object.assign({ 'Content-Type': 'application/json' }, await authHeaders()), body: JSON.stringify(Object.assign({ cid }, body)) });", 'fungsi post')
s = rep(s, "if (!r.ok) { status.textContent = d.message || 'Gagal.'; return false; }",
        "if (!r.ok) { if (d.banned) setBanned(true); status.textContent = d.message || 'Gagal.'; return false; }", 'error post')
s = rep(s, "const r = await fetch('/api/chat?cid=' + encodeURIComponent(cid), { cache: 'no-store' });",
        "const r = await fetch('/api/chat?cid=' + encodeURIComponent(cid) + '&name=' + encodeURIComponent(profile().name || ''), { cache: 'no-store', headers: await authHeaders() });", 'fungsi load')
s = rep(s, "data = { messages: d.messages || [], stories: d.stories || [], notes: d.notes || [], online: d.online || 1 };",
        "data = { messages: d.messages || [], stories: d.stories || [], notes: d.notes || [], online: d.online || 1 };\n      isOwner = !!d.isOwner; bans = d.bans || [];\n      setBanned(!!d.banned);\n      if (banned) status.textContent = 'Akunmu diblokir dari chat oleh admin.';", 'data load')
s = rep(s, "const sig = data.messages.length + ':' + (last ? last.id : '');",
        "const sig = data.messages.map(m => m.id).join(',') + '|' + isOwner;", 'signature pesan')
s = rep(s, "if (loadedOnce && bellOn && last && last.name !== me) beep();",
        "if (loadedOnce && bellOn && last && last.name !== me && last.ts > lastTs) beep();\n        if (last) lastTs = Math.max(lastTs, last.ts);", 'bunyi notifikasi')
s = rep(s, "bub.addEventListener('click', () => setReply(m));",
        "bub.addEventListener('click', () => openMsgMenu(m));", 'klik pesan')
s = rep(s, 'async function sendMsg() {', 'async function sendMsg() {\n    if (banned) return;', 'sendMsg')

a = s.find("$('gc-users').addEventListener('click', () => {")
k = s.find("alert('Anggota aktif", a)
b = s.find("  });", k)
if a < 0 or k < 0 or b < 0:
    print('GAGAL: tombol anggota tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit
s = s[:a] + "$('gc-users').addEventListener('click', openMembers);" + s[b + len("  });"):]

NEW = r"""  async function authHeaders() {
    try {
      if (window.firebase && firebase.apps && firebase.apps.length) {
        const u = firebase.auth().currentUser;
        if (u) return { Authorization: 'Bearer ' + await u.getIdToken() };
      }
    } catch {}
    return {};
  }
  function setBanned(v) {
    if (banned === v) return;
    banned = v;
    input.disabled = v;
    input.placeholder = v ? 'Akunmu diblokir dari chat' : 'Tulis pesan';
    act.disabled = v;
    status.textContent = v ? 'Akunmu diblokir dari chat oleh admin.' : '';
  }
  function sheetColors() {
    return root.classList.contains('light')
      ? { bg: '#ffffff', fg: '#111b21', mu: '#667781', ln: '#d9dee1', fi: '#f0f2f5' }
      : { bg: '#1f2c33', fg: '#e9edef', mu: '#8696a0', ln: '#2f3f47', fi: '#2a3942' };
  }
  function openSheet(title) {
    const old = $('gc-sheet2');
    if (old) old.remove();
    const C = sheetColors();
    const wrap = el('div');
    wrap.id = 'gc-sheet2';
    wrap.style.cssText = 'position:fixed;left:0;right:0;top:0;bottom:0;z-index:60;display:flex;align-items:flex-end;justify-content:center;background:rgba(0,0,0,.55);overscroll-behavior:contain';
    const panel = el('div');
    panel.style.cssText = 'width:100%;max-width:520px;box-sizing:border-box;background:' + C.bg + ';color:' + C.fg + ';border-radius:18px 18px 0 0;padding:16px;max-height:85vh;overflow-y:auto;display:flex;flex-direction:column;gap:10px';
    const head = el('div');
    head.style.cssText = 'display:flex;justify-content:space-between;align-items:center';
    const t = el('b', '', title);
    t.style.fontSize = '1.05rem';
    const x = el('button', '', 'Tutup');
    x.type = 'button';
    x.style.cssText = 'background:none;border:none;color:' + C.mu + ';font:inherit;font-weight:700;cursor:pointer';
    head.append(t, x);
    panel.appendChild(head);
    const close = () => wrap.remove();
    x.addEventListener('click', close);
    wrap.addEventListener('click', e => { if (e.target === wrap) close(); });
    wrap.appendChild(panel);
    document.body.appendChild(wrap);
    return { panel, close, C };
  }
  function menuBtn(C, label, color, fn, armedLabel) {
    const b = el('button', '', label);
    b.type = 'button';
    b.style.cssText = 'padding:13px;border-radius:12px;border:1px solid ' + C.ln + ';background:' + C.fi + ';color:' + color + ';font:inherit;font-weight:800;text-align:center;cursor:pointer';
    let armed = false;
    b.addEventListener('click', () => {
      if (armedLabel && !armed) { armed = true; b.textContent = armedLabel; b.style.borderColor = color; return; }
      fn();
    });
    return b;
  }
  function openMsgMenu(m) {
    const mine = !!m.mine;
    const canDel = mine || isOwner;
    const canBan = isOwner && !mine && m.name !== (profile().name || '');
    const sh = openSheet(m.name);
    const prev = el('div', '', (m.text || '🎤 Pesan suara').slice(0, 100));
    prev.style.cssText = 'color:' + sh.C.mu + ';font-size:.9rem;overflow-wrap:anywhere';
    sh.panel.appendChild(prev);
    sh.panel.appendChild(menuBtn(sh.C, 'Balas', sh.C.fg, () => { sh.close(); setReply(m); }));
    if (canDel) {
      sh.panel.appendChild(menuBtn(sh.C, 'Hapus untuk semua', '#ef4444', async () => {
        sh.close();
        if (await post({ type: 'delete', id: m.id })) { msgSig = null; await load(); }
      }, 'Ketuk lagi untuk menghapus'));
    }
    if (canBan) {
      sh.panel.appendChild(menuBtn(sh.C, 'Ban pengguna', '#ef4444', async () => {
        sh.close();
        if (await post({ type: 'ban', id: m.id })) {
          await load();
          status.textContent = m.name + ' diblokir dari chat.';
        }
      }, 'Ketuk lagi untuk mem-ban ' + m.name));
    }
  }
  function openMembers() {
    const sh = openSheet('Anggota');
    const names = [...new Set(data.messages.map(m => m.name).concat(data.stories.map(s => s.name), data.notes.map(n => n.name)))];
    const lab = text => {
      const d = el('div', '', text);
      d.style.cssText = 'color:' + sh.C.mu + ';font-size:.8rem;font-weight:700;margin-top:4px';
      return d;
    };
    const row = text => {
      const r = el('div', '', text);
      r.style.cssText = 'padding:10px 12px;border-radius:10px;background:' + sh.C.fi + ';overflow-wrap:anywhere';
      return r;
    };
    sh.panel.appendChild(lab('Aktif (' + names.length + ')'));
    if (!names.length) sh.panel.appendChild(row('-'));
    names.forEach(n => sh.panel.appendChild(row(n)));
    if (isOwner) {
      sh.panel.appendChild(lab('Diblokir (' + bans.length + ')'));
      if (!bans.length) sh.panel.appendChild(row('Tidak ada.'));
      bans.forEach(bn => {
        const r = el('div');
        r.style.cssText = 'display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 12px;border-radius:10px;background:' + sh.C.fi;
        const nm = el('span', '', bn.name || '(tanpa nama)');
        nm.style.overflowWrap = 'anywhere';
        const un = el('button', '', 'Cabut');
        un.type = 'button';
        un.style.cssText = 'padding:8px 14px;border-radius:10px;border:1px solid ' + sh.C.ln + ';background:none;color:#22c55e;font:inherit;font-weight:800;cursor:pointer';
        un.addEventListener('click', async () => {
          un.disabled = true;
          if (await post({ type: 'unban', banId: bn.id })) { await load(); sh.close(); openMembers(); }
          else un.disabled = false;
        });
        r.append(nm, un);
        sh.panel.appendChild(r);
      });
    }
  }
  try {
    if (window.firebase && firebase.apps && firebase.apps.length) {
      firebase.auth().onAuthStateChanged(() => { msgSig = null; load(); });
    }
  } catch {}

"""
s = rep(s, '  function setReply(m) {', NEW + '  function setReply(m) {', 'sisipan fungsi')

if 'firebase-app-compat' not in h:
    SCR = ('<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js"></script>\n'
           '<script src="https://www.gstatic.com/firebasejs/10.7.1/firebase-auth-compat.js"></script>\n'
           '<script>if(!firebase.apps.length)firebase.initializeApp({apiKey:"AIzaSyC_iYADCUCDN1pCl3j4-jeZT3pU2XcIydU",authDomain:"manz-4d272.firebaseapp.com",projectId:"manz-4d272",appId:"1:431533009387:web:72a9855b0bd596f37911ae"});</script>\n')
    h = rep(h, '<script src="chat.js"></script>', SCR + '<script src="chat.js"></script>', 'chat.html')
    shutil.copy('chat.html', 'chat.html.bak41')
    open('chat.html', 'w', encoding='utf-8').write(h)

shutil.copy(f, f + '.bak41')
open(f, 'w', encoding='utf-8', errors='surrogateescape').write(s)
print('Chat: hapus pesan, ban, panel anggota : OK')
