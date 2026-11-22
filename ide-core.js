(function () {
  'use strict';
  var $ = function (i) { return document.getElementById(i); };
  var KEY = 'mz_ide_v1';
  var ls = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
  };
  function say(t) { if (window.IDE && window.IDE.say) window.IDE.say(t); }
  var DEF = {
    'index.html': '<!doctype html>\n<html lang="id">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <title>Proyekku</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>Halo, Dunia!</h1>\n  <button id="btn">Klik aku</button>\n  <script src="script.js"><\/script>\n</body>\n</html>\n',
    'style.css': 'body{font-family:system-ui,sans-serif;text-align:center;padding:40px;background:#0f172a;color:#e2e8f0}\nbutton{padding:12px 20px;border:0;border-radius:10px;background:#38bdf8;font-weight:700}\n',
    'script.js': 'document.getElementById("btn").addEventListener("click", function(){\n  console.log("Tombol diklik!");\n  document.querySelector("h1").textContent = "Berhasil!";\n});\n',
    'main.py': 'nama = "Dunia"\nprint(f"Halo, {nama}!")\nfor i in range(3):\n    print("Baris", i + 1)\n'
  };
  var S = null;
  try { S = JSON.parse(ls.get(KEY) || 'null'); } catch (e) {}
  if (!S || typeof S.files !== 'object' || !S.files) S = { files: DEF, dirs: [], open: ['index.html'], active: 'index.html', exp: {} };
  S.dirs = S.dirs || [];
  S.exp = S.exp || {};
  S.open = (S.open || []).filter(function (p) { return S.files[p] !== undefined; });
  if (!S.open.length) S.open = Object.keys(S.files).slice(0, 1);
  if (S.files[S.active] === undefined) S.active = S.open[0] || '';

  var st = 0;
  function save() {
    clearTimeout(st);
    st = setTimeout(function () { if (!ls.set(KEY, JSON.stringify(S))) say('Penyimpanan penuh atau diblokir.'); }, 400);
  }

  CodeMirror.modeURL = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/%N/%N.min.js';
  var cm = CodeMirror($('ed'), {
    value: '', lineNumbers: true, lineWrapping: true, tabSize: 2, indentUnit: 2, indentWithTabs: false,
    autoCloseBrackets: true, matchBrackets: true, styleActiveLine: true,
    extraKeys: { Tab: function (c) { c.execCommand('insertSoftTab'); } }
  });
  var docs = {};
  cm.on('change', function () { if (S.active) { S.files[S.active] = cm.getValue(); save(); } });

  function modeInfo(p) {
    return CodeMirror.findModeByFileName(p.split('/').pop()) || { name: 'Teks', mode: 'null', mime: 'text/plain' };
  }
  function ensureDoc(p, cb) {
    if (docs[p]) return cb(docs[p]);
    var mi = modeInfo(p), done = false;
    function fin(spec) {
      if (done) return;
      done = true;
      docs[p] = CodeMirror.Doc(S.files[p] || '', spec);
      cb(docs[p]);
    }
    CodeMirror.requireMode(mi.mode, function () { fin(mi.mime || mi.mode); });
    setTimeout(function () { fin('text/plain'); }, 4000);
  }
  function openFile(p) {
    if (S.files[p] === undefined) return;
    if (S.open.indexOf(p) < 0) S.open.push(p);
    ensureDoc(p, function (d) {
      S.active = p;
      cm.swapDoc(d);
      cm.refresh();
      renderTabs();
      renderTree();
      if (window.IDE && window.IDE.upd) window.IDE.upd();
      save();
    });
  }
  function closeTab(p) {
    var i = S.open.indexOf(p);
    if (i < 0) return;
    S.open.splice(i, 1);
    if (S.active === p) {
      var n = S.open[Math.max(0, i - 1)];
      if (n) { openFile(n); return; }
      S.active = '';
      cm.swapDoc(CodeMirror.Doc('', 'text/plain'));
    }
    renderTabs();
    renderTree();
    save();
  }
  function renderTabs() {
    var t = $('tabs');
    t.textContent = '';
    S.open.forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'tab' + (p === S.active ? ' on' : '');
      var s = document.createElement('span');
      s.textContent = p.split('/').pop();
      var x = document.createElement('i');
      x.textContent = '\u00D7';
      x.addEventListener('click', function (e) { e.stopPropagation(); closeTab(p); });
      b.append(s, x);
      b.addEventListener('click', function () { openFile(p); });
      t.appendChild(b);
      if (p === S.active) setTimeout(function () { b.scrollIntoView({ inline: 'nearest', block: 'nearest' }); }, 0);
    });
  }

  /* ----- Panel bawah dan tombol bantu ----- */
  function closeSheet() { $('sheet').classList.add('off'); }
  $('sheet').addEventListener('click', function (e) { if (e.target === this) closeSheet(); });
  function sheet(title, fill) {
    var p = $('panel');
    p.textContent = '';
    var h = document.createElement('div');
    h.className = 'ph';
    var b = document.createElement('b');
    b.textContent = title;
    var x = document.createElement('button');
    x.type = 'button';
    x.textContent = 'Tutup';
    x.addEventListener('click', closeSheet);
    h.append(b, x);
    p.appendChild(h);
    fill(p);
    $('sheet').classList.remove('off');
  }
  function btn(label, cls, fn) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'btn ' + (cls || '');
    b.textContent = label;
    if (fn) b.addEventListener('click', fn);
    return b;
  }
  function armed(b, hint, fn) {
    var orig = b.textContent, on = false, t = 0;
    function off() { on = false; b.textContent = orig; b.classList.remove('warn'); }
    b.addEventListener('click', function () {
      if (!on) { on = true; b.textContent = hint; b.classList.add('warn'); t = setTimeout(off, 3000); return; }
      clearTimeout(t);
      off();
      fn();
    });
  }
  function clean(n) {
    n = String(n || '').trim().replace(/\\/g, '/').replace(/^\/+|\/+$/g, '');
    if (!n || n.length > 100 || /(^|\/)\.\.?(\/|$)/.test(n) || /[^\w.\-\/ ]/.test(n)) return '';
    return n;
  }
  function askName(title, ph, init, ok) {
    sheet(title, function (p) {
      var i = document.createElement('input');
      i.className = 'in';
      i.placeholder = ph;
      i.value = init || '';
      i.maxLength = 100;
      var go = btn('Simpan', 'pri', function () {
        var n = clean(i.value);
        if (!n) { say('Nama tidak valid.'); return; }
        if (ok(n) !== false) closeSheet();
      });
      i.addEventListener('keydown', function (e) { if (e.key === 'Enter') go.click(); });
      p.append(i, go);
      setTimeout(function () { i.focus(); i.select(); }, 60);
    });
  }

  /* ----- Berkas dan folder ----- */
  function addDirChain(d) {
    var parts = d.split('/'), acc = '';
    parts.forEach(function (x) {
      acc = acc ? acc + '/' + x : x;
      if (S.dirs.indexOf(acc) < 0) S.dirs.push(acc);
    });
  }
  function newFile(dir) {
    askName('File baru' + (dir ? ' di ' + dir : ''), 'contoh: app.py', '', function (n) {
      var p = dir ? dir + '/' + n : n;
      if (S.files[p] !== undefined) { say('Sudah ada.'); return false; }
      var d = p.indexOf('/') >= 0 ? p.slice(0, p.lastIndexOf('/')) : '';
      if (d) addDirChain(d);
      S.files[p] = '';
      openFile(p);
    });
  }
  function newDir(dir) {
    askName('Folder baru' + (dir ? ' di ' + dir : ''), 'contoh: src', '', function (n) {
      var p = dir ? dir + '/' + n : n;
      if (S.dirs.indexOf(p) >= 0) { say('Sudah ada.'); return false; }
      addDirChain(p);
      renderTree();
      save();
    });
  }
  function rekey(o, n, isDir) {
    if (!isDir) {
      if (S.files[n] !== undefined) { say('Nama sudah dipakai.'); return false; }
      S.files[n] = S.files[o];
      delete S.files[o];
      delete docs[o];
      delete docs[n];
      S.open = S.open.map(function (x) { return x === o ? n : x; });
      if (S.active === o) S.active = n;
    } else {
      var pre = o + '/', npre = n + '/';
      if (S.dirs.indexOf(n) >= 0 || Object.keys(S.files).some(function (f) { return f.indexOf(npre) === 0; })) { say('Nama sudah dipakai.'); return false; }
      Object.keys(S.files).forEach(function (f) {
        if (f.indexOf(pre) !== 0) return;
        var nf = npre + f.slice(pre.length);
        S.files[nf] = S.files[f];
        delete S.files[f];
        delete docs[f];
        S.open = S.open.map(function (x) { return x === f ? nf : x; });
        if (S.active === f) S.active = nf;
      });
      S.dirs = S.dirs.map(function (d) { return d === o ? n : (d.indexOf(pre) === 0 ? npre + d.slice(pre.length) : d); });
    }
    save();
    return true;
  }
  function removeEntry(p, isDir) {
    var pre = p + '/';
    Object.keys(S.files).forEach(function (f) {
      if (f === p || (isDir && f.indexOf(pre) === 0)) { delete S.files[f]; delete docs[f]; }
    });
    S.dirs = S.dirs.filter(function (d) { return !(isDir && (d === p || d.indexOf(pre) === 0)); });
    S.open = S.open.filter(function (x) { return S.files[x] !== undefined; });
    if (S.files[S.active] === undefined) {
      S.active = S.open[0] || '';
      if (!S.active) cm.swapDoc(CodeMirror.Doc('', 'text/plain'));
    }
    refreshAll();
    save();
  }
  function refreshAll() {
    renderTabs();
    renderTree();
    if (S.active) openFile(S.active);
  }
  function menu(p, isDir) {
    sheet(p, function (panel) {
      if (isDir) {
        panel.append(btn('File baru di sini', '', function () { closeSheet(); newFile(p); }), btn('Folder baru di sini', '', function () { closeSheet(); newDir(p); }));
      }
      panel.appendChild(btn('Ganti nama', '', function () {
        closeSheet();
        askName('Ganti nama', 'nama baru', p.split('/').pop(), function (n) {
          var par = p.indexOf('/') >= 0 ? p.slice(0, p.lastIndexOf('/')) + '/' : '';
          if (!rekey(p, par + n, isDir)) return false;
          refreshAll();
        });
      }));
      var d = btn('Hapus', '', null);
      armed(d, 'Ketuk lagi untuk menghapus', function () { closeSheet(); removeEntry(p, isDir); });
      panel.appendChild(d);
    });
  }

  /* ----- Pohon berkas ----- */
  var COL = { html: '#e44d26', htm: '#e44d26', css: '#2d8cf0', js: '#f7df1e', mjs: '#f7df1e', ts: '#3178c6', py: '#3776ab', json: '#9ece6a', md: '#7dcfff', php: '#8892bf', java: '#e76f00', c: '#659ad2', cpp: '#659ad2', go: '#00add8', rs: '#dea584' };
  function buildTree() {
    var root = { d: {}, f: [] };
    function node(parts) {
      var n = root;
      parts.forEach(function (x) { n = n.d[x] = n.d[x] || { d: {}, f: [] }; });
      return n;
    }
    S.dirs.forEach(function (d) { node(d.split('/')); });
    Object.keys(S.files).sort().forEach(function (p) {
      var a = p.split('/'), f = a.pop();
      node(a).f.push({ n: f, p: p });
    });
    return root;
  }
  function row(lvl, name, path, isDir, on, open) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'row' + (on ? ' on' : '');
    b.style.paddingLeft = (10 + lvl * 16) + 'px';
    var ic = document.createElement('span');
    if (isDir) { ic.className = 'ic'; ic.textContent = open ? '\u25BE' : '\u25B8'; }
    else { ic.className = 'dot'; ic.style.background = COL[name.split('.').pop().toLowerCase()] || '#7a82a8'; }
    var nm = document.createElement('span');
    nm.className = 'nm';
    nm.textContent = name;
    var mo = document.createElement('span');
    mo.className = 'mo';
    mo.textContent = '\u22EF';
    mo.addEventListener('click', function (e) { e.stopPropagation(); menu(path, isDir); });
    b.append(ic, nm, mo);
    b.addEventListener('click', function () {
      if (isDir) { S.exp[path] = !open; renderTree(); save(); }
      else { openFile(path); closeSide(); }
    });
    return b;
  }
  function renderTree() {
    var box = $('tree');
    box.textContent = '';
    function draw(n, path, lvl) {
      Object.keys(n.d).sort().forEach(function (k) {
        var dp = path ? path + '/' + k : k, open = S.exp[dp] !== false;
        box.appendChild(row(lvl, k, dp, true, false, open));
        if (open) draw(n.d[k], dp, lvl + 1);
      });
      n.f.forEach(function (f) { box.appendChild(row(lvl, f.n, f.p, false, f.p === S.active, false)); });
    }
    draw(buildTree(), '', 0);
  }
  function openSide() { $('side').classList.add('on'); $('scrim').classList.add('on'); }
  function closeSide() { $('side').classList.remove('on'); $('scrim').classList.remove('on'); }
  $('menu').addEventListener('click', openSide);
  $('sx').addEventListener('click', closeSide);
  $('scrim').addEventListener('click', closeSide);
  $('nf').addEventListener('click', function () { newFile(''); });
  $('nd').addEventListener('click', function () { newDir(''); });

  /* ----- Unggah dan ZIP ----- */
  $('up').addEventListener('click', function () { $('upin').click(); });
  $('upin').addEventListener('change', function () {
    var list = Array.prototype.slice.call(this.files || []);
    this.value = '';
    list.forEach(function (f) {
      if (f.size > 1500000) { say(f.name + ' terlalu besar (maks 1,5 MB).'); return; }
      var r = new FileReader();
      r.onload = function () {
        var t = String(r.result || '');
        var n = clean(f.name);
        if (!n || t.indexOf('\u0000') >= 0) { say(f.name + ' bukan file teks.'); return; }
        if (S.files[n] !== undefined) { say(n + ' sudah ada, dilewati.'); return; }
        S.files[n] = t;
        renderTree();
        save();
        say(n + ' ditambahkan.');
      };
      r.onerror = function () { say('Gagal membaca ' + f.name); };
      r.readAsText(f);
    });
  });
  $('zip').addEventListener('click', function () {
    function go() {
      var z = new window.JSZip();
      Object.keys(S.files).forEach(function (p) { z.file(p, S.files[p]); });
      S.dirs.forEach(function (d) { z.folder(d); });
      z.generateAsync({ type: 'blob' }).then(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'proyek.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 3000);
        say('Mengunduh proyek.zip...');
      });
    }
    if (window.JSZip) return go();
    say('Menyiapkan ZIP...');
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
    s.onload = go;
    s.onerror = function () { say('Gagal memuat ZIP. Cek internet.'); };
    document.head.appendChild(s);
  });

  window.IDE = { S: S, cm: cm, openFile: openFile, save: save, say: null, upd: null, run: null, closeSide: closeSide };
  renderTabs();
  renderTree();
  if (S.active) openFile(S.active);
})();
