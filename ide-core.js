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
  function flushSave() {
    clearTimeout(st);
    st = 0;
    if (!ls.set(KEY, JSON.stringify(S))) say('Penyimpanan penuh atau diblokir.');
  }
  function save() {
    clearTimeout(st);
    st = setTimeout(flushSave, 400);
  }
  window.addEventListener('pagehide', flushSave);
  window.addEventListener('beforeunload', flushSave);

  CodeMirror.modeURL = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/%N/%N.min.js';
  var cm = CodeMirror($('ed'), {
    value: '', lineNumbers: true, lineWrapping: true, tabSize: 2, indentUnit: 2, indentWithTabs: false,
    autoCloseBrackets: true, matchBrackets: true, styleActiveLine: true,
    extraKeys: { Tab: function (c) { c.execCommand('insertSoftTab'); } }
  });
  var docs = {};
  var activePath = '';   // path dokumen yang benar-benar ada di editor
  var openToken = 0;     // menolak callback lama saat klik tab cepat
  cm.on('change', function () {
    if (!activePath || S.files[activePath] === undefined) return;
    S.files[activePath] = cm.getValue();
    save();
  });

  function modeInfo(p) {
    return CodeMirror.findModeByFileName(p.split('/').pop()) || { name: 'Teks', mode: 'null', mime: 'text/plain' };
  }
  function ensureDoc(p, cb) {
    if (docs[p]) return cb(docs[p]);
    var mi = modeInfo(p), spec = mi.mime || mi.mode;
    var called = false, ready = false, timer = 0;
    function fin(spec2, fallback) {
      if (S.files[p] === undefined || S.open.indexOf(p) < 0) return;
      var d = docs[p];
      if (!d) { d = CodeMirror.Doc(S.files[p] || '', spec2); docs[p] = d; }
      else if (!fallback) d.setMode(spec2); // mode asli boleh tiba setelah fallback
      if (!fallback) { ready = true; clearTimeout(timer); }
      if (!called) { called = true; cb(d); }
    }
    timer = setTimeout(function () { fin('text/plain', true); }, 4000);
    CodeMirror.requireMode(mi.mode, function () { if (!ready) fin(spec, false); });
  }
  function openFile(p) {
    if (S.files[p] === undefined) return;
    if (S.open.indexOf(p) < 0) S.open.push(p);
    var token = ++openToken;
    S.active = p; // sinkron, agar tab yang ditutup tidak menerima ketikan
    renderTabs();
    ensureDoc(p, function (d) {
      if (token !== openToken || S.files[p] === undefined || S.open.indexOf(p) < 0) return;
      S.active = p;
      activePath = p;
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
      openToken++; // batalkan callback ensureDoc dari tab yang ditutup
      S.active = n || '';
      if (n) { openFile(n); return; }
      activePath = '';
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
      var im = document.createElement('img');
      im.src = fileIcon(p);
      im.alt = '';
      var s = document.createElement('span');
      s.textContent = p.split('/').pop();
      var x = document.createElement('i');
      x.textContent = '\u00D7';
      x.addEventListener('click', function (e) { e.stopPropagation(); closeTab(p); });
      b.append(im, s, x);
      b.addEventListener('click', function () { openFile(p); });
      t.appendChild(b);
      if (p === S.active) setTimeout(function () { b.scrollIntoView({ inline: 'nearest', block: 'nearest' }); }, 0);
    });
    updateFavicon();
  }

  /* ----- Favicon mengikuti jenis berkas aktif ----- */
  var favicon = $('favicon');
  function svgIcon(inner) {
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">' + inner + '</svg>';
    return 'data:image/svg+xml,' + encodeURIComponent(svg);
  }
  function fileIcon(p) {
    var e = (p.split('/').pop().split('.').pop() || '').toLowerCase();
    var t = 'font-family="Arial,sans-serif" font-weight="800" text-anchor="middle"';
    if (e === 'html' || e === 'htm' || e === 'xml') return svgIcon(
      '<svg x="0" y="0" width="64" height="64" viewBox="74 100 364 412">'
      + '<path fill="#e44d26" d="M107.6 471l-33-370.4h362.8l-33 370.2L255.7 512"/>'
      + '<path fill="#f16529" d="M256 480.5V131H404.3L376 447"/>'
      + '<path fill="#ebebeb" d="M142 176.3h114v45.4h-64.2l4.2 46.5h60v45.3H154.4M156.4 336.3H202l3.2 36.3 50.8 13.6v47.4l-93.2-26"/>'
      + '<path fill="#fff" d="M369.6 176.3H255.8v45.4h109.6M361.3 268.2H255.8v45.4h56l-5.3 59-50.7 13.6v47.2l93-25.8"/>'
      + '</svg>');
    if (e === 'css') return svgIcon(
      '<svg x="0" y="0" width="64" height="64" viewBox="74 100 364 412">'
      + '<polygon points="437.367,100.62 404.321,470.819 255.778,512 107.644,470.877 74.633,100.62" fill="#264de4"/>'
      + '<polygon points="376.03,447.246 404.27,130.894 256,130.894 256,480.523" fill="#2965f1"/>'
      + '<polygon points="150.31,268.217 154.38,313.627 256,313.627 256,268.217" fill="#ebebeb"/>'
      + '<polygon points="256,176.305 255.843,176.305 142.132,176.305 146.26,221.716 256,221.716" fill="#ebebeb"/>'
      + '<polygon points="256,433.399 256,386.153 255.801,386.206 205.227,372.55 201.994,336.333 177.419,336.333 156.409,336.333 162.771,407.634 255.791,433.457" fill="#ebebeb"/>'
      + '<polygon points="311.761,313.627 306.49,372.521 255.843,386.191 255.843,433.435 348.937,407.634 349.62,399.962 360.291,280.411 361.399,268.217 369.597,176.305 255.843,176.305 255.843,221.716 319.831,221.716 315.699,268.217 255.843,268.217 255.843,313.627" fill="#fff"/>'
      + '</svg>');
    if (e === 'js' || e === 'mjs') return svgIcon(
      '<svg x="0" y="0" width="64" height="64" viewBox="0 0 630 630">'
      + '<rect width="630" height="630" fill="#f7df1e"/>'
      + '<path d="m423.2 492.19c12.69 20.72 29.2 35.95 58.4 35.95 24.53 0 40.2-12.26 40.2-29.2 0-20.3-16.1-27.49-43.1-39.3l-14.8-6.35c-42.72-18.2-71.1-41-71.1-89.2 0-44.4 33.83-78.2 86.7-78.2 37.64 0 64.7 13.1 84.2 47.4l-46.1 29.6c-10.15-18.2-21.1-25.37-38.1-25.37-17.34 0-28.33 11-28.33 25.37 0 17.76 11 24.95 36.4 35.95l14.8 6.34c50.3 21.57 78.7 43.56 78.7 93 0 53.3-41.87 82.5-98.1 82.5-54.98 0-90.5-26.2-107.88-60.54zm-209.13 5.13c9.3 16.5 17.76 30.45 38.1 30.45 19.45 0 31.72-7.61 31.72-37.2v-201.3h59.2v202.1c0 61.3-35.94 89.2-88.4 89.2-47.4 0-74.85-24.53-88.81-54.075z"/>'
      + '</svg>');
    if (e === 'ts') return svgIcon(
      '<svg x="0" y="0" width="64" height="64" viewBox="0 0 512 512">'
      + '<rect width="512" height="512" rx="50" fill="#3178c6"/>'
      + '<path fill="#fff" fill-rule="evenodd" d="m316.939 407.424v50.061c8.138 4.172 17.763 7.3 28.875 9.386s22.823 3.129 35.135 3.129c11.999 0 23.397-1.147 34.196-3.442 10.799-2.294 20.268-6.075 28.406-11.342 8.138-5.266 14.581-12.15 19.328-20.65s7.121-19.007 7.121-31.522c0-9.074-1.356-17.026-4.069-23.857s-6.625-12.906-11.738-18.225c-5.112-5.319-11.242-10.091-18.389-14.315s-15.207-8.213-24.18-11.967c-6.573-2.712-12.468-5.345-17.685-7.9-5.217-2.556-9.651-5.163-13.303-7.822-3.652-2.66-6.469-5.476-8.451-8.448-1.982-2.973-2.974-6.336-2.974-10.091 0-3.441.887-6.544 2.661-9.308s4.278-5.136 7.512-7.118c3.235-1.981 7.199-3.52 11.894-4.615 4.696-1.095 9.912-1.642 15.651-1.642 4.173 0 8.581.313 13.224.938 4.643.626 9.312 1.591 14.008 2.894 4.695 1.304 9.259 2.947 13.694 4.928 4.434 1.982 8.529 4.276 12.285 6.884v-46.776c-7.616-2.92-15.937-5.084-24.962-6.492s-19.381-2.112-31.066-2.112c-11.895 0-23.163 1.278-33.805 3.833s-20.006 6.544-28.093 11.967c-8.086 5.424-14.476 12.333-19.171 20.729-4.695 8.395-7.043 18.433-7.043 30.114 0 14.914 4.304 27.638 12.912 38.172 8.607 10.533 21.675 19.45 39.204 26.751 6.886 2.816 13.303 5.579 19.25 8.291s11.086 5.528 15.415 8.448c4.33 2.92 7.747 6.101 10.252 9.543 2.504 3.441 3.756 7.352 3.756 11.733 0 3.233-.783 6.231-2.348 8.995s-3.939 5.162-7.121 7.196-7.147 3.624-11.894 4.771c-4.748 1.148-10.303 1.721-16.668 1.721-10.851 0-21.597-1.903-32.24-5.71-10.642-3.806-20.502-9.516-29.579-17.13zm-84.159-123.342h64.22v-41.082h-179v41.082h63.906v182.918h50.874z"/>'
      + '</svg>');
    if (e === 'py') return svgIcon(
      '<svg x="3" y="3" width="58" height="58" viewBox="0.21 -0.077 110 110">'
      + '<path fill="#3776ab" d="M55.023-0.077c-25.971,0-26.25,10.081-26.25,12.156c0,3.148,0,12.594,0,12.594h26.75v3.781 c0,0-27.852,0-37.375,0c-7.949,0-17.938,4.833-17.938,26.25c0,19.673,7.792,27.281,15.656,27.281c2.335,0,9.344,0,9.344,0 s0-9.765,0-13.125c0-5.491,2.721-15.656,15.406-15.656c15.91,0,19.971,0,26.531,0c3.902,0,14.906-1.696,14.906-14.406 c0-13.452,0-17.89,0-24.219C82.054,11.426,81.515-0.077,55.023-0.077z M40.273,8.392c2.662,0,4.813,2.15,4.813,4.813 c0,2.661-2.151,4.813-4.813,4.813s-4.813-2.151-4.813-4.813C35.46,10.542,37.611,8.392,40.273,8.392z"/>'
      + '<path fill="#ffd43b" d="M55.397,109.923c25.959,0,26.282-10.271,26.282-12.156c0-3.148,0-12.594,0-12.594H54.897v-3.781 c0,0,28.032,0,37.375,0c8.009,0,17.938-4.954,17.938-26.25c0-23.322-10.538-27.281-15.656-27.281c-2.336,0-9.344,0-9.344,0 s0,10.216,0,13.125c0,5.491-2.631,15.656-15.406,15.656c-15.91,0-19.476,0-26.532,0c-3.892,0-14.906,1.896-14.906,14.406 c0,14.475,0,18.265,0,24.219C28.366,100.497,31.562,109.923,55.397,109.923z M70.148,101.454c-2.662,0-4.813-2.151-4.813-4.813 s2.15-4.813,4.813-4.813c2.661,0,4.813,2.151,4.813,4.813S72.809,101.454,70.148,101.454z"/>'
      + '</svg>');
    if (e === 'svg') return svgIcon(
      '<circle cx="23" cy="22" r="5" fill="#ffd43b"/>'
      + '<path d="M8 50l15-17 10 11 8-9 15 15z" fill="#0891b2"/>');
    if (e === 'json') return svgIcon(
      '<text x="32" y="44" ' + t + ' font-size="30" fill="#16a34a">{}</text>');
    if (e === 'md') return svgIcon(
      '<text x="32" y="43" ' + t + ' font-size="26" fill="#0891b2">M</text>');
    return svgIcon(
      '<text x="32" y="43" ' + t + ' font-size="25" fill="#0891b2">&lt;/&gt;</text>');
  }
  function updateFavicon() {
    if (favicon) favicon.href = fileIcon(S.active || '');
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
      openToken++;
      S.active = S.open[0] || '';
      if (!S.active) { activePath = ''; cm.swapDoc(CodeMirror.Doc('', 'text/plain')); }
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
    else { ic = document.createElement('img'); ic.className = 'ic'; ic.src = fileIcon(path); ic.alt = ''; }
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
