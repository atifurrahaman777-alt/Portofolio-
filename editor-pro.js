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
  var NAMES = TAGS.concat(Object.keys(ALIAS).filter(function (k) { return !KNOWN[k]; })).concat(['html:5']);

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
  function extract(before) {
    var lt = before.lastIndexOf('<'), gt = before.lastIndexOf('>');
    var depth = 0, i = before.length;
    while (i > 0) {
      var c = before[i - 1];
      if (c === ']' || c === '}') depth++;
      else if (c === '[' || c === '{') depth = Math.max(0, depth - 1);
      else if (/\s/.test(c) && depth === 0) break;
      i--;
    }
    var chunk = before.slice(i);
    if (chunk.indexOf('<') >= 0) {
      var l = chunk.lastIndexOf('<'), gg = chunk.indexOf('>', l);
      if (gg < 0) return null;
      chunk = chunk.slice(gg + 1);
    } else if (lt > gt && before.slice(lt).indexOf(' ') >= 0) {
      return null;
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
      if (r2) out.push({ abbr: n, label: n + '  \u2192  ' + (n === 'html:5' || n === '!' ? 'kerangka HTML5' : preview(r2)), res: r2 });
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
  function lsGet() { try { return localStorage.getItem(LSK); } catch (e) { return null; } }
  function lsSet(v) { try { localStorage.setItem(LSK, v); } catch (e) {} }

  var css = document.createElement('style');
  css.textContent =
    'body.edark{--bg:#1a1b26;--card:#16161e;--line:#2a2b3d;--text:#c0caf5;--muted:#7a82a8;--accent:#7aa2f7;--on:#10131f;--k:#bb9af7;--s:#9ece6a;--n:#ff9e64;--c:#565f89;--t:#7aa2f7;--a:#7dcfff;--d:#e0af68}' +
    '.stat{display:flex;justify-content:space-between;gap:12px;padding:5px 12px;font-size:.74rem;color:var(--muted);border-top:1px solid var(--line);background:var(--card);white-space:nowrap;overflow-x:auto}' +
    '.CodeMirror-hints{background:var(--card)!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:12px!important;font:14px ui-monospace,Menlo,monospace!important;max-height:34vh!important;padding:4px!important;box-shadow:0 8px 24px rgba(0,0,0,.45)!important;z-index:100!important}' +
    '.CodeMirror-hint{color:var(--text)!important;padding:9px 10px!important;border-radius:8px!important;max-width:92vw;white-space:pre!important;overflow:hidden;text-overflow:ellipsis}' +
    'li.CodeMirror-hint-active{background:var(--accent)!important;color:var(--on)!important}';
  document.head.appendChild(css);

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
  ['addon/hint/show-hint.min.js', 'addon/hint/xml-hint.min.js', 'addon/hint/html-hint.min.js', 'addon/hint/css-hint.min.js', 'addon/hint/javascript-hint.min.js', 'addon/comment/comment.min.js']
    .reduce(function (p, f) { return p.then(function () { return loadJs(f); }); }, Promise.resolve())
    .then(function () { ready = true; });

  /* ----- Tema ----- */
  var forceDark = lsGet() !== 'web';
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
    lsSet(forceDark ? 'dark' : 'web');
    applyTheme();
  });
  $('ftabs').appendChild(tb);
  applyTheme();

  /* ----- Status bar ----- */
  var stat = document.createElement('div');
  stat.className = 'stat';
  stat.innerHTML = '<span id="stPos"></span><span id="stInfo"></span>';
  $('keys').parentNode.insertBefore(stat, $('keys'));
  function modeLabel() { var n = cm.getMode().name; return n === 'htmlmixed' ? 'HTML' : n === 'css' ? 'CSS' : 'JavaScript'; }
  function updStat() {
    var c = cm.getCursor();
    $('stPos').textContent = 'Ln ' + (c.line + 1) + ', Col ' + (c.ch + 1);
    $('stInfo').textContent = 'Spasi: 2 \u00B7 ' + modeLabel() + ' \u00B7 UTF-8';
  }
  cm.on('cursorActivity', updStat);
  cm.on('swapDoc', updStat);
  updStat();

  /* ----- Tombol tambahan ----- */
  var frag = document.createDocumentFragment();
  [['\u2191', 'goLineUp'], ['\u2193', 'goLineDown'], ['\u2190', 'goCharLeft'], ['\u2192', 'goCharRight'], ['//', 'comment']].forEach(function (k) {
    var b = document.createElement('button');
    b.type = 'button';
    b.textContent = k[0];
    b.addEventListener('mousedown', function (e) { e.preventDefault(); });
    b.addEventListener('click', function () {
      if (k[1] === 'comment') { if (cm.toggleComment) cm.toggleComment(); }
      else cm.execCommand(k[1]);
      cm.focus();
    });
    frag.appendChild(b);
  });
  $('keys').insertBefore(frag, $('keys').firstChild);

  /* ----- Konteks ----- */
  function ctxHtml() {
    var m = cm.getMode();
    if (m.name !== 'htmlmixed') return false;
    var inner = CodeMirror.innerMode(m, cm.getTokenAt(cm.getCursor()).state);
    return inner.mode.name === 'xml';
  }
  function innerName() {
    var m = cm.getMode();
    return CodeMirror.innerMode(m, cm.getTokenAt(cm.getCursor()).state).mode.name;
  }
  function inTag(before) { return before.lastIndexOf('<') > before.lastIndexOf('>'); }

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
  var kb = Array.prototype.filter.call($('keys').querySelectorAll('button'), function (b) { return b.textContent === '>'; })[0];
  if (kb) kb.addEventListener('click', function () { setTimeout(autoClose, 0); });

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
    if (!fn) return;
    var o = { hint: fn, completeSingle: false };
    if (extra) for (var k in extra) o[k] = extra[k];
    cm.showHint(o);
  }
  function showHints() {
    if (!ready || cm.state.completionActive || !cm.showHint) return;
    var cur = cm.getCursor(), m = cm.getMode().name;
    if (m === 'htmlmixed') {
      if (!ctxHtml()) {
        var inner = innerName();
        if (inner === 'css') show(CodeMirror.hint.css);
        else if (inner === 'javascript') show(CodeMirror.hint.javascript);
        return;
      }
      var before = cm.getLine(cur.line).slice(0, cur.ch);
      if (inTag(before)) show(CodeMirror.hint.html);
      else show(emmetHint, { closeCharacters: /\s/ });
    } else if (m === 'css') {
      show(CodeMirror.hint.css);
    } else {
      var w = cm.getRange({ line: cur.line, ch: Math.max(0, cur.ch - 2) }, cur);
      if (/[\w$]{2}$|\.\w?$/.test(w)) show(CodeMirror.hint.javascript);
    }
  }
  var ht = 0;
  cm.on('inputRead', function (c, ch) {
    var t = ch.text.length === 1 ? ch.text[0] : '';
    if (t === '>') autoClose();
    if (!/[\w.#:<!\-\/>*+\[\]{}$^]/.test(t)) return;
    clearTimeout(ht);
    ht = setTimeout(showHints, 150);
  });
})();
