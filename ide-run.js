(function () {
  'use strict';
  var I = window.IDE, S = I.S;
  var $ = function (i) { return document.getElementById(i); };
  var out = $('out'), con = $('con'), frame = $('frame');
  var stampN = 0;
  function stamp() { return '<!--' + Date.now() + '-' + (++stampN) + '-->'; }

  function show(tab) {
    out.classList.remove('off');
    $('tCon').classList.toggle('on', tab === 'con');
    $('tPre').classList.toggle('on', tab === 'pre');
    con.style.display = tab === 'con' ? 'block' : 'none';
    frame.style.display = tab === 'pre' ? 'block' : 'none';
    I.cm.refresh();
  }
  function log(t, m) {
    var l = document.createElement('div');
    l.className = 'ln ' + t;
    l.textContent = m;
    con.appendChild(l);
    while (con.children.length > 300) con.removeChild(con.firstChild);
    con.scrollTop = con.scrollHeight;
  }
  $('tCon').addEventListener('click', function () { show('con'); });
  $('tPre').addEventListener('click', function () { show('pre'); });
  $('oClr').addEventListener('click', function () { con.textContent = ''; });
  $('oBig').addEventListener('click', function () { out.classList.toggle('big'); I.cm.refresh(); });
  $('oX').addEventListener('click', function () { out.classList.add('off'); I.cm.refresh(); });

  var BRIDGE = '<script>(function(){function s(t,a){try{parent.postMessage({mzc:1,t:t,m:a.map(function(x){try{return typeof x==="object"?JSON.stringify(x):String(x)}catch(e){return String(x)}}).join(" ")},"*")}catch(e){}}["log","info","warn","error"].forEach(function(k){var o=console[k];console[k]=function(){s(k,[].slice.call(arguments));try{o.apply(console,arguments)}catch(e){}}});window.addEventListener("error",function(e){s("error",[e.message+(e.lineno?" (baris "+e.lineno+")":"")])});window.addEventListener("unhandledrejection",function(e){s("error",["Promise ditolak: "+(e.reason&&e.reason.message||e.reason)])})})();<\/script>';
  window.addEventListener('message', function (e) {
    if (e.source !== frame.contentWindow) return;
    var d = e.data;
    if (!d || d.mzc !== 1) return;
    log(String(d.t), String(d.m).slice(0, 2000));
  });

  function norm(base, ref) {
    if (/^(https?:)?\/\//i.test(ref) || ref.indexOf('data:') === 0) return null;
    var parts = (base ? base.split('/') : []).concat(ref.split('?')[0].split('#')[0].split('/')), res = [];
    parts.forEach(function (x) { if (x === '.' || x === '') return; if (x === '..') res.pop(); else res.push(x); });
    return res.join('/');
  }
  function buildHtml(path) {
    var src = S.files[path] || '';
    var dir = path.indexOf('/') >= 0 ? path.slice(0, path.lastIndexOf('/')) : '';
    src = src.replace(/<link\b((?:"[^"]*"|'[^']*'|[^'">])*)>/gi, function (all, attrs) {
      var rm = /(?:^|\s)rel\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrs);
      var rel = rm ? (rm[1] !== undefined ? rm[1] : (rm[2] !== undefined ? rm[2] : rm[3])) : '';
      if (!/stylesheet/i.test(rel)) return all;
      var hm = /(?:^|\s)href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrs);
      if (!hm) return all;
      var ref = hm[1] !== undefined ? hm[1] : (hm[2] !== undefined ? hm[2] : hm[3]);
      var p = norm(dir, ref);
      return p && S.files[p] !== undefined ? '<style>' + S.files[p] + '</style>' : all;
    });
    src = src.replace(/<script\b((?:"[^"]*"|'[^']*'|[^'">])*)>\s*<\/script\s*>/gi, function (all, attrs) {
      var m = /(?:^|\s)src\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i.exec(attrs);
      if (!m) return all;
      var ref = m[1] !== undefined ? m[1] : (m[2] !== undefined ? m[2] : m[3]);
      var p = norm(dir, ref);
      if (!p || S.files[p] === undefined) return all;
      var rest = attrs.replace(/(?:^|\s)src\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/i, '');
      return '<script' + rest + '>' + S.files[p].replace(/<\/script/gi, '<\\/script') + '<\/script>';
    });
    var mark = stamp();
    if (/<head[^>]*>/i.test(src)) src = src.replace(/<head[^>]*>/i, function (m) { return m + mark + BRIDGE; });
    else if (/<!doctype[^>]*>/i.test(src)) src = src.replace(/<!doctype[^>]*>/i, function (m) { return m + mark + BRIDGE; });
    else src = mark + BRIDGE + src;
    return src;
  }
  function runHtml(path) {
    con.textContent = '';
    frame.srcdoc = buildHtml(path);
    show('pre');
  }
  function runJs(path) {
    con.textContent = '';
    var code = (S.files[path] || '').replace(/<\/script/gi, '<\\/script');
    frame.srcdoc = '<!doctype html><html><head>' + stamp() + '<meta charset="utf-8">' + BRIDGE + '</head><body><script>' + code + '<\/script></body></html>';
    show('con');
    log('info', '\u25B6 ' + path);
  }

  var py = null, pyP = null;
  function loadPy() {
    if (py) return Promise.resolve(py);
    if (pyP) return pyP;
    log('info', 'Memuat Python... (pertama kali sekitar 10 MB, tunggu sebentar)');
    pyP = new Promise(function (res, rej) {
      var s = document.createElement('script');
      s.src = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';
      s.onload = function () {
        window.loadPyodide().then(function (p) {
          py = p;
          p.setStdout({ batched: function (t) { log('log', t); } });
          p.setStderr({ batched: function (t) { log('error', t); } });
          p.setStdin({ stdin: function () { var v = window.prompt('Input untuk Python:'); return v === null ? '' : v; } });
          res(p);
        }, rej);
      };
      s.onerror = function () { rej(new Error('Gagal memuat Python (cek internet).')); };
      document.head.appendChild(s);
    });
    pyP.catch(function () { pyP = null; });
    return pyP;
  }
  function runPy(path) {
    con.textContent = '';
    show('con');
    log('info', '\u25B6 ' + path);
    loadPy().then(async function (p) {
      try {
        Object.keys(S.files).forEach(function (f) {
          var d = f.indexOf('/') >= 0 ? f.slice(0, f.lastIndexOf('/')) : '';
          if (d) p.FS.mkdirTree('/home/pyodide/' + d);
          p.FS.writeFile('/home/pyodide/' + f, S.files[f]);
        });
        p.runPython("import os, sys\nos.chdir('/home/pyodide')\nif '/home/pyodide' not in sys.path: sys.path.insert(0, '/home/pyodide')");
        var code = S.files[path] || '';
        await p.loadPackagesFromImports(code);
        var g = p.globals.get('dict')();
        try { await p.runPythonAsync(code, { globals: g }); log('info', '\u2713 selesai'); }
        finally { g.destroy(); }
      } catch (e) {
        log('error', String((e && e.message) || e).split('\n').slice(-12).join('\n'));
      }
    }, function (e) { log('error', String((e && e.message) || e)); });
  }

  function runActive() {
    var p = S.active;
    if (!p) { I.say('Buka sebuah file dulu.'); return; }
    var ext = (p.split('.').pop() || '').toLowerCase();
    if (ext === 'html' || ext === 'htm') return runHtml(p);
    if (ext === 'js' || ext === 'mjs') return runJs(p);
    if (ext === 'py') return runPy(p);
    if (S.files['index.html'] !== undefined && /^(css|json|md|txt|svg)$/.test(ext)) return runHtml('index.html');
    con.textContent = '';
    show('con');
    log('warn', 'File .' + ext + ' belum bisa dijalankan di browser (yang didukung: HTML, JavaScript, Python). Kode tetap bisa disunting dan diunduh.');
  }
  I.run = runActive;
  $('run').addEventListener('click', runActive);
})();
