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
