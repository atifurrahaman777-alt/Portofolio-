(function (g) {
  'use strict';
  var CARET = '\u0001';
  var VOID = { area: 1, base: 1, br: 1, col: 1, embed: 1, hr: 1, img: 1, input: 1, link: 1, meta: 1, source: 1, track: 1, wbr: 1 };
  var INLINE = { a: 1, abbr: 1, b: 1, i: 1, em: 1, strong: 1, span: 1, small: 1, code: 1, label: 1, button: 1, img: 1, input: 1, br: 1, sub: 1, sup: 1, kbd: 1, mark: 1, q: 1, s: 1, u: 1, select: 1, textarea: 1, cite: 1, time: 1 };
  var TAGS = 'a abbr address article aside audio b blockquote body br button canvas caption code col div dl dt dd em fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 head header hr html i iframe img input label legend li link main mark meta nav ol optgroup option p pre script section select small source span strong style sub summary sup svg table tbody td textarea tfoot th thead time title tr u ul video'.split(' ');
  var KNOWN = {};
  TAGS.forEach(function (t) { KNOWN[t] = 1; });
  var ALIAS = {
    'a': ['a', [['href', '']]],
    'a:link': ['a', [['href', 'http://']]],
    'a:mail': ['a', [['href', 'mailto:']]],
    'img': ['img', [['src', ''], ['alt', '']]],
    'link': ['link', [['rel', 'stylesheet'], ['href', '']]],
    'link:css': ['link', [['rel', 'stylesheet'], ['href', 'style.css']]],
    'script:src': ['script', [['src', '']]],
    'input:text': ['input', [['type', 'text'], ['name', '']]],
    'input:email': ['input', [['type', 'email'], ['name', '']]],
    'input:password': ['input', [['type', 'password'], ['name', '']]],
    'input:checkbox': ['input', [['type', 'checkbox'], ['name', '']]],
    'input:radio': ['input', [['type', 'radio'], ['name', '']]],
    'input:submit': ['input', [['type', 'submit'], ['value', '']]],
    'input:button': ['input', [['type', 'button'], ['value', '']]],
    'btn': ['button', []],
    'btn:s': ['button', [['type', 'submit']]],
    'form:post': ['form', [['action', ''], ['method', 'post']]],
    'form:get': ['form', [['action', ''], ['method', 'get']]],
    'meta:vp': ['meta', [['name', 'viewport'], ['content', 'width=device-width, initial-scale=1.0']]],
    'meta:utf': ['meta', [['charset', 'UTF-8']]],
    'bq': ['blockquote', []],
    'fig': ['figure', []],
    'figc': ['figcaption', []]
  };
  var NAMES = TAGS.concat(Object.keys(ALIAS).filter(function (k) { return !KNOWN[k]; })).concat(['html:5', 'doc']);

  function parseAttrs(s) {
    var out = [], re = /([\w:@-]+)(?:=(?:"([^"]*)"|'([^']*)'|([^\s"']+)))?/g, m;
    while ((m = re.exec(s))) {
      var v = m[2] !== undefined ? m[2] : (m[3] !== undefined ? m[3] : (m[4] !== undefined ? m[4] : null));
      out.push([m[1], v]);
    }
    return out;
  }

  function parse(abbr) {
    var i = 0, n = abbr.length;
    function ident() {
      var s = i;
      while (i < n && /[A-Za-z0-9_:$@\-]/.test(abbr[i])) i++;
      return abbr.slice(s, i);
    }
    function element() {
      var nd = { name: '', id: '', cls: [], attrs: [], text: '', count: 1, kids: [], group: false };
      if (abbr[i] === '(') {
        i++;
        nd.kids = sequence();
        if (abbr[i] !== ')') throw new Error('x');
        i++;
        nd.group = true;
      } else {
        nd.name = ident();
      }
      while (i < n) {
        var c = abbr[i];
        if (c === '.') { i++; nd.cls.push(ident()); }
        else if (c === '#') { i++; nd.id = ident(); }
        else if (c === '[') { var e = abbr.indexOf(']', i); if (e < 0) throw new Error('x'); nd.attrs = nd.attrs.concat(parseAttrs(abbr.slice(i + 1, e))); i = e + 1; }
        else if (c === '{') { var e2 = abbr.indexOf('}', i); if (e2 < 0) throw new Error('x'); nd.text = abbr.slice(i + 1, e2); i = e2 + 1; }
        else if (c === '*') { i++; var s = i; while (i < n && /\d/.test(abbr[i])) i++; nd.count = Math.max(1, Math.min(parseInt(abbr.slice(s, i), 10) || 1, 50)); }
        else break;
      }
      if (!nd.group && !nd.name && !nd.cls.length && !nd.id && !nd.text && !nd.attrs.length) throw new Error('x');
      return nd;
    }
    function sequence() {
      var roots = [], last = element();
      roots.push(last);
      var stack = [roots];
      while (i < n && abbr[i] !== ')') {
        var c = abbr[i], nx;
        if (c === '>') { i++; nx = element(); last.kids.push(nx); stack.push(last.kids); last = nx; }
        else if (c === '+') { i++; nx = element(); stack[stack.length - 1].push(nx); last = nx; }
        else if (c === '^') {
          while (abbr[i] === '^') { i++; if (stack.length > 1) stack.pop(); }
          if (i < n && abbr[i] !== ')' && abbr[i] !== '+' && abbr[i] !== '>') { nx = element(); stack[stack.length - 1].push(nx); last = nx; }
        }
        else throw new Error('x');
      }
      return roots;
    }
    var tree = sequence();
    if (i !== n) throw new Error('x');
    return tree;
  }

  function valid(nodes) {
    return nodes.every(function (nd) {
      if (nd.group) return valid(nd.kids);
      if (nd.name && !KNOWN[nd.name] && !ALIAS[nd.name]) return false;
      return valid(nd.kids);
    });
  }

  function num(str, ix) {
    return str.replace(/\$+/g, function (m) {
      var s = String(ix + 1);
      while (s.length < m.length) s = '0' + s;
      return s;
    });
  }
  function implicit(parent) {
    if (parent === 'ul' || parent === 'ol') return 'li';
    if (parent === 'table' || parent === 'tbody' || parent === 'thead' || parent === 'tfoot') return 'tr';
    if (parent === 'tr') return 'td';
    if (parent === 'select' || parent === 'optgroup') return 'option';
    if (INLINE[parent] || parent === 'p') return 'span';
    return 'div';
  }
  function indent(t) { return t.split('\n').map(function (l) { return '  ' + l; }).join('\n'); }

  function renderNode(nd, parent, st, k, inh) {
    var ix = nd.count > 1 ? k : (inh || 0);
    var name = nd.name, attrs = [];
    var al = ALIAS[name];
    if (al) { name = al[0]; al[1].forEach(function (p) { attrs.push([p[0], p[1]]); }); }
    if (!name) name = implicit(parent);
    var list = [];
    if (nd.id) list.push(['id', num(nd.id, ix)]);
    if (nd.cls.length) list.push(['class', nd.cls.map(function (c) { return num(c, ix); }).join(' ')]);
    attrs.concat(nd.attrs).forEach(function (p) {
      var key = num(p[0], ix), val = p[1] === null ? null : num(p[1], ix), done = false;
      list.forEach(function (q) { if (q[0] === key) { q[1] = val; done = true; } });
      if (!done) list.push([key, val]);
    });
    var as = list.map(function (p) {
      if (p[1] === null) return p[0];
      if (p[1] === '' && !st.placed) { st.placed = true; return p[0] + '="' + CARET + '"'; }
      return p[0] + '="' + p[1] + '"';
    }).join(' ');
    var open = '<' + name + (as ? ' ' + as : '') + '>';
    if (VOID[name]) return { text: open, inline: true };
    var text = num(nd.text, ix);
    var kids = renderList(nd.kids, name, st, ix);
    var inl = !!INLINE[name];
    if (!kids.length) {
      if (!text && !st.placed) { st.placed = true; text = CARET; }
      return { text: open + text + '</' + name + '>', inline: inl };
    }
    var allInline = kids.every(function (x) { return x.inline && x.text.indexOf('\n') < 0; });
    if (allInline) return { text: open + text + kids.map(function (x) { return x.text; }).join('') + '</' + name + '>', inline: inl };
    var body = (text ? [text] : []).concat(kids.map(function (x) { return x.text; })).map(indent).join('\n');
    return { text: open + '\n' + body + '\n</' + name + '>', inline: false };
  }
  function renderList(nodes, parent, st, inh) {
    var res = [];
    nodes.forEach(function (nd) {
      for (var k = 0; k < nd.count; k++) {
        if (nd.group) res = res.concat(renderList(nd.kids, parent, st, nd.count > 1 ? k : inh));
        else res.push(renderNode(nd, parent, st, k, inh));
      }
    });
    return res;
  }
  function finish(text) {
    var idx = text.indexOf(CARET);
    if (idx < 0) return { text: text, caret: text.length };
    return { text: text.replace(CARET, ''), caret: idx };
  }

  function boiler() {
    return finish('<!DOCTYPE html>\n<html lang="id">\n<head>\n  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <title>Dokumen</title>\n</head>\n<body>\n  ' + CARET + '\n</body>\n</html>');
  }
  function expand(abbr) {
    if (!abbr || abbr.length > 200) return null;
    if (abbr === '!' || abbr === 'html:5' || abbr === 'doc') return boiler();
    var tree;
    try { tree = parse(abbr); } catch (e) { return null; }
    if (!tree.length || !valid(tree)) return null;
    var st = { placed: false };
    var out = renderList(tree, '', st, 0);
    if (!out.length) return null;
    var all = out.every(function (x) { return x.inline && x.text.indexOf('\n') < 0; });
    return finish(out.map(function (x) { return x.text; }).join(all ? '' : '\n'));
  }
  function firstOpen(s, ch, from) {
    var q = '';
    for (var i = from || 0; i < s.length; i++) {
      var c = s.charAt(i);
      if (q) { if (c === q) q = ''; }
      else if (c === '"' || c === "'") q = c;
      else if (c === ch) return i;
    }
    return -1;
  }
  function extract(before) {
    var depth = 0, i = before.length, quote = '';
    // spasi di dalam nilai atribut berkutip bukan pemisah singkatan
    // contoh: <div class="foo">ul>li  ->  ul>li
    while (i > 0) {
      var c = before[i - 1];
      if (quote) {
        if (c === quote) quote = '';
      } else if (c === '"' || c === "'") quote = c;
      else if (c === ']' || c === '}') depth++;
      else if (c === '[' || c === '{') depth = Math.max(0, depth - 1);
      else if (/\s/.test(c) && depth === 0) break;
      i--;
    }
    var chunk = before.slice(i);
    var lt = i > 0 ? before.lastIndexOf('<', i - 1) : -1;
    if (chunk.indexOf('<') >= 0) {
      var gg = firstOpen(chunk, '>', chunk.lastIndexOf('<') + 1);
      if (gg < 0) return null;
      chunk = chunk.slice(gg + 1);
    } else if (lt >= 0 && firstOpen(before.slice(lt, i), '>', 0) < 0) {
      var g = firstOpen(chunk, '>', 0); // '>' pertama menutup tag yang belum selesai
      if (g < 0) return null;
      chunk = chunk.slice(g + 1);
    }
    return chunk;
  }
  function preview(r) {
    var l = r.text.split('\n');
    var s = l[0];
    if (s.length > 44) s = s.slice(0, 44) + '\u2026';
    return l.length > 1 ? s + ' \u2026' : s;
  }
  function suggest(abbr) {
    if (!abbr || (abbr.length < 2 && abbr !== '!')) return [];
    var out = [];
    if (/[.#>+*\[\]{}()^$]/.test(abbr)) {
      var r = expand(abbr);
      if (r) out.push({ abbr: abbr, label: abbr + '  \u2192  ' + preview(r), res: r });
      return out;
    }
    var cands = abbr === '!' ? ['!'] : NAMES.filter(function (n) { return n.indexOf(abbr) === 0; });
    cands.sort(function (a, b) { return (a === abbr ? -1 : b === abbr ? 1 : a < b ? -1 : 1); });
    cands.slice(0, 10).forEach(function (n) {
      var r2 = expand(n);
      if (r2) out.push({ abbr: n, label: n + '  \u2192  ' + (n === 'html:5' || n === 'doc' || n === '!' ? 'kerangka HTML5' : preview(r2)), res: r2 });
    });
    return out;
  }
  g.mzEmmet = { expand: expand, extract: extract, suggest: suggest, VOID: VOID };
})(typeof window !== 'undefined' ? window : globalThis);
(function () {
  'use strict';
  var E = window.mzEmmet;
  var el = document.querySelector('.CodeMirror');
  var cm = el && el.CodeMirror;
  if (!cm || !E) return;
  var $ = function (id) { return document.getElementById(id); };
  var LSK = 'mz_editor_theme';
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  /* ----- Tampilan ----- */
  var P = 'html body:not(#e1):not(#e2) ';
  function R(sel, decl) { return sel.split(',').map(function (s) { return P + s.trim(); }).join(',') + '{' + decl + '}'; }
  var rules = [
    'body.edark{--bg:#1a1b26;--card:#16161e;--line:#2a2b3d;--text:#c0caf5;--muted:#7a82a8;--accent:#7aa2f7;--on:#10131f;--k:#bb9af7;--s:#9ece6a;--n:#ff9e64;--c:#565f89;--t:#7aa2f7;--a:#7dcfff;--d:#e0af68}',
    R('.top', 'padding:0 8px 0 4px;gap:6px;min-height:46px'),
    R('.seg', 'border:0;border-radius:0;gap:0;overflow:visible;flex:1'),
    R('.seg button', 'flex:0 0 auto;padding:13px 16px;background:none;color:var(--muted);border-bottom:2px solid transparent;border-radius:0;font:600 14px system-ui,sans-serif;text-transform:none;letter-spacing:0'),
    R('.seg button.on', 'background:none;color:var(--text);border-bottom-color:var(--accent)'),
    R('#run', 'width:40px;height:40px;padding:0;border-radius:50%;background:#22c55e;border:0;color:#052e16;display:flex;align-items:center;justify-content:center;font-size:0'),
    R('#run svg', 'width:20px;height:20px'),
    R('.ftabs', 'padding:0 6px;gap:0;background:var(--card)'),
    R('.ftabs button[data-f]', 'border:0;border-radius:0;padding:11px 14px;background:none;color:var(--muted);font:600 13px system-ui,sans-serif;text-transform:none;letter-spacing:0;border-bottom:2px solid transparent;display:flex;align-items:center;gap:7px'),
    R('.ftabs button[data-f]::before', 'content:"";width:9px;height:9px;border-radius:2px;background:var(--lc)'),
    R('.ftabs button[data-f="html"]', '--lc:#e44d26'),
    R('.ftabs button[data-f="css"]', '--lc:#2d8cf0'),
    R('.ftabs button[data-f="js"]', '--lc:#f7df1e'),
    R('.ftabs button[data-f].on', 'background:rgba(127,127,127,.12);color:var(--text);border-bottom-color:var(--lc)'),
    R('.ftabs #fm,.ftabs #fp,.ftabs #thm', 'border:0;background:none;width:36px;padding:9px 0;border-radius:8px;color:var(--muted);font:600 13px system-ui,sans-serif;text-transform:none;letter-spacing:0'),
    R('.keys', 'padding:6px 8px;gap:6px'),
    R('.keys button', 'min-width:40px;height:36px;padding:0 10px;border-radius:8px;font:500 15px ui-monospace,Menlo,monospace;text-transform:none;letter-spacing:0'),
    R('.keys button.sg', 'font:700 12px system-ui,sans-serif;background:var(--accent);color:var(--on);border-color:var(--accent)'),
    R('.tools', 'gap:0;padding:0'),
    R('.tools button', 'flex:1;border:0;border-radius:0;border-right:1px solid var(--line);background:none;padding:13px 4px;font:600 12px system-ui,sans-serif;color:var(--muted);text-transform:none;letter-spacing:0'),
    R('.tools button:last-child', 'border-right:0'),
    R('.tools button.warn', 'color:var(--err)'),
    R('.stat', 'font:12px system-ui,sans-serif;text-transform:none;letter-spacing:0'),
    '.stat{display:flex;justify-content:space-between;gap:12px;padding:5px 12px;color:var(--muted);border-top:1px solid var(--line);background:var(--card);white-space:nowrap;overflow-x:auto}',
    '.CodeMirror{line-height:1.65!important}',
    '.CodeMirror-lines{padding:8px 0!important}',
    '.CodeMirror-activeline-background{background:rgba(127,127,127,.12)!important}',
    '.CodeMirror-hints{background:var(--card)!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:12px!important;font:14px ui-monospace,Menlo,monospace!important;max-height:34vh!important;padding:4px!important;box-shadow:0 8px 24px rgba(0,0,0,.45)!important;z-index:100!important}',
    '.CodeMirror-hint{color:var(--text)!important;padding:9px 10px!important;border-radius:8px!important;max-width:92vw;white-space:pre!important;overflow:hidden;text-overflow:ellipsis}',
    'li.CodeMirror-hint-active{background:var(--accent)!important;color:var(--on)!important}'
  ];
  var css = document.createElement('style');
  css.textContent = rules.join('\n');
  document.head.appendChild(css);
  $('run').setAttribute('aria-label', 'Jalankan');
  $('run').innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
  if (!lsGet('mz_editor_fs')) $('ed').style.setProperty('--fs', '14px');

  /* ----- Muat pustaka saran ----- */
  var BASE = 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/';
  var ready = false;
  var lk = document.createElement('link');
  lk.rel = 'stylesheet';
  lk.href = BASE + 'addon/hint/show-hint.min.css';
  document.head.appendChild(lk);
  function loadJs(p) {
    return new Promise(function (res) {
      var s = document.createElement('script');
      s.src = BASE + p;
      s.onload = res;
      s.onerror = res;
      document.head.appendChild(s);
    });
  }
  ['addon/hint/show-hint.min.js', 'addon/hint/xml-hint.min.js', 'addon/hint/html-hint.min.js', 'addon/hint/css-hint.min.js', 'addon/hint/javascript-hint.min.js', 'addon/comment/comment.min.js', 'addon/selection/active-line.min.js']
    .reduce(function (p, f) { return p.then(function () { return loadJs(f); }); }, Promise.resolve())
    .then(function () {
      ready = !!cm.showHint;
      try { cm.setOption('styleActiveLine', true); } catch (e) {}
      updStat();
    });

  /* ----- Tema ----- */
  var forceDark = lsGet(LSK) !== 'web';
  function parentLight() {
    try { var pb = window.parent !== window ? window.parent.document.body : null; return pb ? pb.classList.contains('light-mode') : false; } catch (e) { return false; }
  }
  function applyTheme() {
    var b = document.body;
    if (forceDark) { b.classList.add('edark'); b.classList.remove('light-mode'); }
    else { b.classList.remove('edark'); b.classList.toggle('light-mode', parentLight()); }
  }
  new MutationObserver(function () {
    if (forceDark && document.body.classList.contains('light-mode')) document.body.classList.remove('light-mode');
  }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
  var tb = document.createElement('button');
  tb.type = 'button';
  tb.id = 'thm';
  tb.setAttribute('aria-label', 'Tema editor');
  tb.textContent = '\u25D0';
  tb.addEventListener('click', function () {
    forceDark = !forceDark;
    lsSet(LSK, forceDark ? 'dark' : 'web');
    applyTheme();
  });
  $('ftabs').appendChild(tb);
  applyTheme();

  /* ----- Jenis file dan konteks ----- */
  function curFile() {
    var b = $('ftabs').querySelector('[data-f].on');
    return b ? b.dataset.f : 'html';
  }
  function innerName() {
    try { var m = cm.getModeAt(cm.getCursor()); return (m && m.name) || ''; } catch (e) { return ''; }
  }
  function ctxHtml() {
    if (curFile() !== 'html') return false;
    var n = innerName();
    return n !== 'css' && n !== 'javascript';
  }
  function inTag(before) { return before.lastIndexOf('<') > before.lastIndexOf('>'); }

  /* ----- Status bar ----- */
  var stat = document.createElement('div');
  stat.className = 'stat';
  stat.innerHTML = '<span id="stPos"></span><span id="stInfo"></span>';
  $('keys').parentNode.insertBefore(stat, $('keys'));
  var LABEL = { html: 'HTML', css: 'CSS', js: 'JavaScript' };
  var note = '', noteT = 0;
  function updStat() {
    var c = cm.getCursor();
    $('stPos').textContent = 'Ln ' + (c.line + 1) + ', Col ' + (c.ch + 1);
    $('stInfo').textContent = note || ('Spasi: 2 \u00B7 ' + LABEL[curFile()] + ' \u00B7 ' + (ready ? 'Saran aktif' : 'Saran memuat...'));
  }
  function say(t) {
    note = t;
    updStat();
    clearTimeout(noteT);
    noteT = setTimeout(function () { note = ''; updStat(); }, 2200);
  }
  cm.on('cursorActivity', updStat);
  cm.on('swapDoc', updStat);
  $('ftabs').addEventListener('click', function () { setTimeout(updStat, 0); });
  updStat();

  /* ----- Tombol tambahan ----- */
  var frag = document.createDocumentFragment();
  [['Saran', 'hint'], ['\u2191', 'goLineUp'], ['\u2193', 'goLineDown'], ['\u2190', 'goCharLeft'], ['\u2192', 'goCharRight'], ['//', 'comment']].forEach(function (k) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = k[0];
    if (k[1] === 'hint') b.className = 'sg';
    b.addEventListener('mousedown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function () {
      if (k[1] === 'hint') showHints(true);
      else if (k[1] === 'comment') { if (cm.toggleComment) cm.toggleComment(); }
      else cm.execCommand(k[1]);
      cm.focus();
    });
    frag.appendChild(b);
  });
  $('keys').insertBefore(frag, $('keys').firstChild);

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

  /* ----- Tutup tag otomatis ----- */
  function autoClose() {
    if (!ctxHtml()) return;
    var cur = cm.getCursor(), line = cm.getLine(cur.line), before = line.slice(0, cur.ch);
    var m = before.match(/<([A-Za-z][\w:-]*)(?:\s[^<>]*)?>$/);
    if (!m || before.charAt(before.length - 2) === '/') return;
    var tag = m[1];
    if (E.VOID[tag.toLowerCase()]) return;
    var close = '</' + tag + '>';
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
    if (!cm.showHint) { say(force ? 'Saran belum termuat. Cek internet.' : ''); return; }
    if (cm.state.completionActive) { if (!force) return; cm.state.completionActive.close(); }
    var cur = cm.getCursor(), f = curFile();
    if (f === 'css') { show(CodeMirror.hint.css); return; }
    if (f === 'js') {
      var w = cm.getRange({ line: cur.line, ch: Math.max(0, cur.ch - 2) }, cur);
      if (force || /[\w$]{2}$|\.\w?$/.test(w)) show(CodeMirror.hint.javascript);
      return;
    }
    var n = innerName();
    if (n === 'css') { show(CodeMirror.hint.css); return; }
    if (n === 'javascript') { show(CodeMirror.hint.javascript); return; }
    var before = cm.getLine(cur.line).slice(0, cur.ch);
    if (inTag(before)) { show(CodeMirror.hint.html); return; }
    if (force && !E.extract(before)) { say('Ketik singkatan, misal: div.box atau html:5'); return; }
    show(emmetHint, { closeCharacters: /\s/ });
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
})();
