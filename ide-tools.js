(function () {
  'use strict';
  var I = window.IDE, cm = I.cm, S = I.S, E = window.mzEmmet;
  var $ = function (id) { return document.getElementById(id); };
  var UK = 'mz_ide_ui';
  var ui = { fs: 14, dark: true };
  try { var u = JSON.parse(localStorage.getItem(UK) || 'null'); if (u) ui = { fs: u.fs || 14, dark: u.dark !== false }; } catch (e) {}
  function saveUi() { try { localStorage.setItem(UK, JSON.stringify(ui)); } catch (e) {} }
  function ext() { return ((S.active || '').split('.').pop() || '').toLowerCase(); }

  /* ----- Status ----- */
  var note = '', nt = 0;
  function upd() {
    var c = cm.getCursor();
    var mi = S.active ? (CodeMirror.findModeByFileName(S.active.split('/').pop()) || { name: 'Teks' }) : { name: '-' };
    $('stPos').textContent = 'Ln ' + (c.line + 1) + ', Col ' + (c.ch + 1);
    $('stInfo').textContent = note || ('Spasi: 2 \u00B7 ' + mi.name + ' \u00B7 UTF-8');
  }
  I.say = function (t) {
    note = t;
    upd();
    clearTimeout(nt);
    nt = setTimeout(function () { note = ''; upd(); }, 2600);
  };
  I.upd = upd;
  cm.on('cursorActivity', upd);

  /* ----- Tema dan ukuran huruf ----- */
  function applyTheme() {
    var b = document.body;
    if (ui.dark) { b.classList.remove('light-mode'); return; }
    var light = false;
    try { var pb = window.parent !== window ? window.parent.document.body : null; light = !!pb && pb.classList.contains('light-mode'); } catch (e) {}
    b.classList.toggle('light-mode', light);
  }
  function setFs(n) {
    ui.fs = Math.max(11, Math.min(22, n));
    $('ed').style.setProperty('--fs', ui.fs + 'px');
    saveUi();
    cm.refresh();
  }
  $('fm').addEventListener('click', function () { setFs(ui.fs - 1); });
  $('fp').addEventListener('click', function () { setFs(ui.fs + 1); });
  $('thm').addEventListener('click', function () { ui.dark = !ui.dark; saveUi(); applyTheme(); });
  applyTheme();
  setFs(ui.fs);

  /* ----- Konteks ----- */
  function isHtml() { return ext() === 'html' || ext() === 'htm'; }
  function innerName() {
    try { var m = cm.getModeAt(cm.getCursor()); return (m && m.name) || ''; } catch (e) { return ''; }
  }
  function ctxHtml() { var n = innerName(); return isHtml() && n !== 'css' && n !== 'javascript'; }
  function inTag(before) { return before.lastIndexOf('<') > before.lastIndexOf('>'); }

  /* ----- Pengembangan singkatan ----- */
  function applyExp(from, to, res) {
    var line = cm.getLine(from.line);
    var ind = line.match(/^\s*/)[0];
    var text = res.text.split('\n').map(function (l, i) { return i ? ind + l : l; }).join('\n');
    var nl = res.text.slice(0, res.caret).split('\n').length - 1;
    var idx = res.caret + nl * ind.length;
    cm.replaceRange(text, from, to);
    var pre = text.slice(0, idx).split('\n');
    cm.setCursor({ line: from.line + pre.length - 1, ch: pre.length === 1 ? from.ch + pre[0].length : pre[pre.length - 1].length });
  }
  function tryExpand() {
    if (cm.somethingSelected() || !ctxHtml()) return false;
    var cur = cm.getCursor();
    var abbr = E.extract(cm.getLine(cur.line).slice(0, cur.ch));
    if (!abbr) return false;
    var r = E.expand(abbr);
    if (!r) return false;
    applyExp({ line: cur.line, ch: cur.ch - abbr.length }, cur, r);
    return true;
  }
  cm.addKeyMap({
    Tab: function () { if (tryExpand()) return; return CodeMirror.Pass; },
    Enter: function () {
      if (cm.somethingSelected() || !ctxHtml()) return CodeMirror.Pass;
      var cur = cm.getCursor(), line = cm.getLine(cur.line);
      if (line.charAt(cur.ch - 1) === '>' && line.slice(cur.ch, cur.ch + 2) === '</') {
        var ind = line.match(/^\s*/)[0];
        cm.replaceRange('\n' + ind + '  \n' + ind, cur);
        cm.setCursor({ line: cur.line + 1, ch: ind.length + 2 });
        return;
      }
      return CodeMirror.Pass;
    }
  });
  function autoClose() {
    if (!ctxHtml()) return;
    var cur = cm.getCursor(), line = cm.getLine(cur.line), before = line.slice(0, cur.ch);
    var m = before.match(/<([A-Za-z][\w:-]*)(?:\s[^<>]*)?>$/);
    if (!m || before.charAt(before.length - 2) === '/') return;
    if (E.VOID[m[1].toLowerCase()]) return;
    var close = '</' + m[1] + '>';
    if (line.slice(cur.ch, cur.ch + close.length) === close) return;
    cm.replaceRange(close, cur, cur);
    cm.setCursor(cur);
  }

  /* ----- Saran (popup) ----- */
  function emmetHint(c) {
    var cur = c.getCursor();
    var abbr = E.extract(c.getLine(cur.line).slice(0, cur.ch));
    if (!abbr) return null;
    var items = E.suggest(abbr);
    if (!items.length) return null;
    return {
      from: { line: cur.line, ch: cur.ch - abbr.length },
      to: cur,
      list: items.map(function (it) {
        return { text: it.abbr, displayText: it.label, hint: function (c2, data) { applyExp(data.from, data.to, it.res); } };
      })
    };
  }
  function show(fn, extra) {
    if (!fn || !cm.showHint) return;
    var o = { hint: fn, completeSingle: false };
    if (extra) for (var k in extra) o[k] = extra[k];
    cm.showHint(o);
  }
  function showHints(force) {
    if (!S.active) return;
    if (cm.state.completionActive) { if (!force) return; cm.state.completionActive.close(); }
    var cur = cm.getCursor(), e = ext();
    var before = cm.getLine(cur.line).slice(0, cur.ch);
    if (isHtml()) {
      var n = innerName();
      if (n === 'css') return show(CodeMirror.hint.css);
      if (n === 'javascript') return show(CodeMirror.hint.javascript);
      if (inTag(before)) return show(CodeMirror.hint.html);
      if (force && !E.extract(before)) { I.say('Ketik singkatan, misal: div.box atau html:5'); return; }
      return show(emmetHint, { closeCharacters: /\s/ });
    }
    if (/^(css|scss|less)$/.test(e)) return show(CodeMirror.hint.css);
    if (!force && !/[\w$]{2}$|\.\w?$/.test(before)) return;
    if (/^(js|mjs|jsx|ts|tsx|json)$/.test(e)) return show(CodeMirror.hint.javascript);
    show(CodeMirror.hint.anyword);
  }
  var ht = 0;
  cm.on('change', function (c, ch) {
    if (ch.origin !== '+input' && ch.origin !== undefined) return;
    if (ch.text.length !== 1 || ch.text[0].length !== 1) return;
    var t = ch.text[0];
    if (t === '>') setTimeout(autoClose, 0);
    if (!/[\w.#:<!\-\/>*+\[\]{}$^]/.test(t)) return;
    clearTimeout(ht);
    ht = setTimeout(function () { showHints(false); }, 150);
  });

  /* ----- Baris tombol ----- */
  var KEYS = [['Saran', 'hint'], ['\u2191', 'goLineUp'], ['\u2193', 'goLineDown'], ['\u2190', 'goCharLeft'], ['\u2192', 'goCharRight'], ['//', 'comment'], ['\u21B6', 'undo'], ['\u21B7', 'redo'], ['\u21E5', 'tab'],
    '<', '>', '/', '{', '}', '(', ')', '[', ']', '"', "'", '=', ';', ':', '.', '#', '!', '&', '|', '$', '_', '-', '+', '*'];
  KEYS.forEach(function (k) {
    var b = document.createElement('button');
    b.type = 'button';
    var sym = typeof k === 'string';
    b.textContent = sym ? k : k[0];
    if (!sym && k[1] === 'hint') b.className = 'sg';
    b.addEventListener('mousedown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function () {
      if (sym) {
        cm.replaceSelection(k);
        if (k === '>') setTimeout(autoClose, 0);
      } else if (k[1] === 'hint') showHints(true);
      else if (k[1] === 'comment') { if (cm.toggleComment) cm.toggleComment(); }
      else if (k[1] === 'undo') cm.undo();
      else if (k[1] === 'redo') cm.redo();
      else if (k[1] === 'tab') { if (!tryExpand()) cm.execCommand('insertSoftTab'); }
      else cm.execCommand(k[1]);
      cm.focus();
    });
    $('keys').appendChild(b);
  });
  upd();
})();
