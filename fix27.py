import re, shutil, os

# ===================== games.html =====================
g = 'games.html'
t = open(g, encoding='utf-8').read()

TABS = '''
<button type="button" class="ocean-tab" data-game-tab="mem">Memory</button>
<button type="button" class="ocean-tab" data-game-tab="g2048">2048</button>
<button type="button" class="ocean-tab" data-game-tab="snake">Snake</button>
<button type="button" class="ocean-tab" data-game-tab="guess">Tebak Angka</button>
<button type="button" class="ocean-tab" data-game-tab="rps">Suit</button>
'''

SECTIONS = r'''
<!-- MEMORY -->
<section class="card game-box ocean-view" id="view-mem" data-view="mem" hidden>
<h2 style="text-align:center;margin-top:0">Memory Match</h2>
<div class="gm-top"><span id="mem-moves">Langkah: 0</span><button type="button" class="btn" id="mem-reset">Ulang</button></div>
<div class="mem-grid" id="mem-grid"></div>
<p class="gm-msg" id="mem-msg"></p>
</section>

<!-- 2048 -->
<section class="card game-box ocean-view" id="view-g2048" data-view="g2048" hidden>
<h2 style="text-align:center;margin-top:0">2048</h2>
<div class="gm-top"><span id="g2048-score">Skor: 0</span><button type="button" class="btn" id="g2048-reset">Ulang</button></div>
<div class="g2048-board" id="g2048-board"></div>
<p class="gm-msg" id="g2048-msg">Geser di papan atau pakai tombol arah.</p>
<div class="dpad" id="g2048-pad">
<button type="button" class="up" data-d="1">&#8593;</button>
<button type="button" class="lf" data-d="0">&#8592;</button>
<button type="button" class="dn" data-d="3">&#8595;</button>
<button type="button" class="rt" data-d="2">&#8594;</button>
</div>
</section>

<!-- SNAKE -->
<section class="card game-box ocean-view" id="view-snake" data-view="snake" hidden>
<h2 style="text-align:center;margin-top:0">Snake</h2>
<div class="gm-top"><span id="snake-score">Skor: 0</span><button type="button" class="btn" id="snake-start">Mulai</button></div>
<canvas id="snake-canvas" width="300" height="300"></canvas>
<p class="gm-msg" id="snake-msg">Tekan Mulai, lalu geser di papan atau pakai tombol arah.</p>
<div class="dpad" id="snake-pad">
<button type="button" class="up" data-d="1">&#8593;</button>
<button type="button" class="lf" data-d="0">&#8592;</button>
<button type="button" class="dn" data-d="3">&#8595;</button>
<button type="button" class="rt" data-d="2">&#8594;</button>
</div>
</section>

<!-- TEBAK ANGKA -->
<section class="card game-box ocean-view" id="view-guess" data-view="guess" hidden>
<h2 style="text-align:center;margin-top:0">Tebak Angka</h2>
<p class="gm-msg" style="margin-top:0">Aku memikirkan angka 1 sampai 100. Coba tebak!</p>
<div class="gm-row">
<input id="guess-input" type="number" inputmode="numeric" min="1" max="100" placeholder="1 - 100">
<button type="button" class="btn" id="guess-btn">Tebak</button>
</div>
<p class="gm-msg" id="guess-msg"></p>
<p class="gm-msg" id="guess-tries">Percobaan: 0</p>
<div style="text-align:center"><button type="button" class="btn" id="guess-reset">Main Lagi</button></div>
</section>

<!-- SUIT -->
<section class="card game-box ocean-view" id="view-rps" data-view="rps" hidden>
<h2 style="text-align:center;margin-top:0">Suit vs Bot</h2>
<div class="gm-row">
<button type="button" class="btn" data-pick="batu">Batu</button>
<button type="button" class="btn" data-pick="gunting">Gunting</button>
<button type="button" class="btn" data-pick="kertas">Kertas</button>
</div>
<p class="gm-msg" id="rps-msg">Pilih salah satu.</p>
<p class="gm-msg" id="rps-score">Menang 0 | Kalah 0 | Seri 0</p>
<div style="text-align:center"><button type="button" class="btn" id="rps-reset">Reset Skor</button></div>
</section>
'''

CSS = r'''
html body .gm-top{display:flex;justify-content:space-between;align-items:center;gap:10px;max-width:320px;margin:0 auto 12px;font-weight:700}
html body .gm-msg{text-align:center;margin:12px 0;font-weight:700;min-height:1.4em}
html body .gm-row{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:12px 0}
html body .gm-row input{width:150px;text-align:center}
html body .mem-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;max-width:320px;margin:0 auto}
html body .mem-card{aspect-ratio:1;font-size:1.7rem;font-weight:900;border-radius:12px!important;border:1px solid var(--line)!important;background:var(--card)!important;color:var(--text)!important;box-shadow:none!important;cursor:pointer;display:flex;align-items:center;justify-content:center;touch-action:manipulation;padding:0}
html body .mem-card.open{background:var(--accent)!important;color:var(--on,#fff)!important}
html body .mem-card.done{background:var(--bg)!important;opacity:.5}
html body .g2048-board{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;max-width:320px;margin:0 auto;padding:8px;border-radius:14px;background:var(--line);touch-action:none;user-select:none;-webkit-user-select:none}
html body .t2048{aspect-ratio:1;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1.4rem;background:var(--bg);color:#776e65}
html body .t2048.v2{background:#eee4da}
html body .t2048.v4{background:#ede0c8}
html body .t2048.v8{background:#f2b179;color:#fff}
html body .t2048.v16{background:#f59563;color:#fff}
html body .t2048.v32{background:#f67c5f;color:#fff}
html body .t2048.v64{background:#f65e3b;color:#fff}
html body .t2048.v128,html body .t2048.v256,html body .t2048.v512{background:#edcf72;color:#fff;font-size:1.15rem}
html body .t2048.v1024,html body .t2048.v2048,html body .t2048.vbig{background:#edc22e;color:#fff;font-size:1rem}
html body #snake-canvas{display:block;margin:0 auto;max-width:100%;border:1px solid var(--line);border-radius:12px;touch-action:none}
html body .dpad{display:grid;grid-template-columns:repeat(3,58px);grid-template-rows:repeat(2,48px);gap:8px;justify-content:center;margin:14px auto 0}
html body .dpad button{font-size:1.3rem;font-weight:800;border-radius:12px!important;border:1px solid var(--line)!important;background:var(--card)!important;color:var(--text)!important;box-shadow:none!important;cursor:pointer;touch-action:manipulation;padding:0}
html body .dpad button:active{background:var(--accent)!important;color:var(--on,#fff)!important}
html body .dpad .up{grid-column:2;grid-row:1}
html body .dpad .lf{grid-column:1;grid-row:2}
html body .dpad .dn{grid-column:2;grid-row:2}
html body .dpad .rt{grid-column:3;grid-row:2}
'''

JS = r'''<script id="mz-games2-js">
(function(){
  window.mzSwipe = function(el, cb){
    var sx = 0, sy = 0;
    el.addEventListener('touchstart', function(e){ sx = e.touches[0].clientX; sy = e.touches[0].clientY; }, {passive:true});
    el.addEventListener('touchmove', function(e){ e.preventDefault(); }, {passive:false});
    el.addEventListener('touchend', function(e){
      var t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
      if (Math.max(Math.abs(dx), Math.abs(dy)) < 24) return;
      if (Math.abs(dx) > Math.abs(dy)) cb(dx < 0 ? 0 : 2); else cb(dy < 0 ? 1 : 3);
    }, {passive:true});
  };

  /* ===== MEMORY MATCH ===== */
  (function(){
    var grid = document.getElementById('mem-grid');
    var movesEl = document.getElementById('mem-moves');
    var msg = document.getElementById('mem-msg');
    var symbols = ['\u25CF','\u25B2','\u25A0','\u25C6','\u2605','\u2665','\u2663','\u2660'];
    var cards = [], first = null, lock = false, moves = 0, matched = 0;
    function shuffle(a){
      for (var i = a.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
      }
      return a;
    }
    function start(){
      cards = shuffle(symbols.concat(symbols));
      first = null; lock = false; moves = 0; matched = 0;
      movesEl.textContent = 'Langkah: 0';
      msg.textContent = '';
      grid.replaceChildren();
      cards.forEach(function(sym, i){
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'mem-card';
        b.addEventListener('click', function(){ flip(b, i); });
        grid.appendChild(b);
      });
    }
    function flip(b, i){
      if (lock || b.classList.contains('open') || b.classList.contains('done')) return;
      b.classList.add('open');
      b.textContent = cards[i];
      if (first === null) { first = i; return; }
      moves++;
      movesEl.textContent = 'Langkah: ' + moves;
      var a = grid.children[first];
      if (cards[first] === cards[i]) {
        a.classList.add('done'); b.classList.add('done');
        first = null; matched++;
        if (matched === symbols.length) msg.textContent = 'Selesai dalam ' + moves + ' langkah!';
      } else {
        lock = true;
        setTimeout(function(){
          a.classList.remove('open'); b.classList.remove('open');
          a.textContent = ''; b.textContent = '';
          first = null; lock = false;
        }, 700);
      }
    }
    document.getElementById('mem-reset').addEventListener('click', start);
    start();
  })();

  /* ===== 2048 ===== */
  (function(){
    var boardEl = document.getElementById('g2048-board');
    var scoreEl = document.getElementById('g2048-score');
    var msg = document.getElementById('g2048-msg');
    var view = document.getElementById('view-g2048');
    var g, score, over;
    function empty(){ var r = []; for (var i = 0; i < 4; i++) r.push([0,0,0,0]); return r; }
    function addTile(){
      var e = [];
      for (var r = 0; r < 4; r++) for (var c = 0; c < 4; c++) if (!g[r][c]) e.push([r, c]);
      if (!e.length) return;
      var p = e[Math.floor(Math.random() * e.length)];
      g[p[0]][p[1]] = Math.random() < 0.9 ? 2 : 4;
    }
    function slide(line){
      var a = line.filter(Boolean), gained = 0;
      for (var i = 0; i < a.length - 1; i++) {
        if (a[i] === a[i + 1]) { a[i] *= 2; gained += a[i]; a.splice(i + 1, 1); }
      }
      while (a.length < 4) a.push(0);
      return {row: a, gained: gained};
    }
    function move(dir){
      if (over) return;
      var ng = empty(), gain = 0, moved = false, i, j;
      for (i = 0; i < 4; i++) {
        var line = [];
        for (j = 0; j < 4; j++) {
          line.push(dir === 0 ? g[i][j] : dir === 2 ? g[i][3 - j] : dir === 1 ? g[j][i] : g[3 - j][i]);
        }
        var res = slide(line);
        gain += res.gained;
        for (j = 0; j < 4; j++) {
          var v = res.row[j];
          if (dir === 0) ng[i][j] = v;
          else if (dir === 2) ng[i][3 - j] = v;
          else if (dir === 1) ng[j][i] = v;
          else ng[3 - j][i] = v;
        }
      }
      for (i = 0; i < 4; i++) for (j = 0; j < 4; j++) if (ng[i][j] !== g[i][j]) moved = true;
      if (!moved) return;
      g = ng; score += gain;
      addTile(); render(); check();
    }
    function canMove(){
      for (var r = 0; r < 4; r++) for (var c = 0; c < 4; c++) {
        if (!g[r][c]) return true;
        if (c < 3 && g[r][c] === g[r][c + 1]) return true;
        if (r < 3 && g[r][c] === g[r + 1][c]) return true;
      }
      return false;
    }
    function check(){
      if (!canMove()) { over = true; msg.textContent = 'Game over! Skor: ' + score; return; }
      for (var r = 0; r < 4; r++) for (var c = 0; c < 4; c++) if (g[r][c] === 2048) { msg.textContent = 'Kamu dapat 2048! Lanjut terus.'; return; }
    }
    function render(){
      scoreEl.textContent = 'Skor: ' + score;
      boardEl.replaceChildren();
      g.forEach(function(row){
        row.forEach(function(v){
          var d = document.createElement('div');
          d.className = 't2048 v' + (v > 2048 ? 'big' : v);
          d.textContent = v || '';
          boardEl.appendChild(d);
        });
      });
    }
    function reset(){
      g = empty(); score = 0; over = false;
      msg.textContent = 'Geser di papan atau pakai tombol arah.';
      addTile(); addTile(); render();
    }
    document.getElementById('g2048-reset').addEventListener('click', reset);
    document.querySelectorAll('#g2048-pad [data-d]').forEach(function(b){
      b.addEventListener('click', function(){ move(parseInt(b.dataset.d, 10)); });
    });
    window.mzSwipe(boardEl, move);
    document.addEventListener('keydown', function(e){
      var map = {ArrowLeft:0, ArrowUp:1, ArrowRight:2, ArrowDown:3};
      if (!(e.key in map) || view.hidden) return;
      e.preventDefault();
      move(map[e.key]);
    });
    reset();
  })();

  /* ===== SNAKE ===== */
  (function(){
    var cv = document.getElementById('snake-canvas');
    var ctx = cv.getContext('2d');
    var scoreEl = document.getElementById('snake-score');
    var msg = document.getElementById('snake-msg');
    var view = document.getElementById('view-snake');
    var N = 15, S = cv.width / N;
    var DIRS = [{x:-1,y:0},{x:0,y:-1},{x:1,y:0},{x:0,y:1}];
    var snake, dir, nextDir, food, score, timer, running = false;
    function cssv(n, f){
      var v = getComputedStyle(document.body).getPropertyValue(n).trim();
      return v || f;
    }
    function placeFood(){
      for (var k = 0; k < 500; k++) {
        var p = {x: Math.floor(Math.random() * N), y: Math.floor(Math.random() * N)};
        var hit = snake.some(function(s){ return s.x === p.x && s.y === p.y; });
        if (!hit) { food = p; return; }
      }
    }
    function draw(){
      ctx.fillStyle = cssv('--bg', '#ffffff');
      ctx.fillRect(0, 0, cv.width, cv.height);
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(food.x * S + S / 2, food.y * S + S / 2, S / 2 - 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = cssv('--text', '#111111');
      snake.forEach(function(s, i){
        ctx.globalAlpha = i === 0 ? 1 : 0.75;
        ctx.fillRect(s.x * S + 1, s.y * S + 1, S - 2, S - 2);
      });
      ctx.globalAlpha = 1;
    }
    function reset(){
      clearInterval(timer);
      snake = [{x:7,y:7},{x:6,y:7},{x:5,y:7}];
      dir = DIRS[2]; nextDir = dir; score = 0; running = false;
      scoreEl.textContent = 'Skor: 0';
      msg.textContent = 'Tekan Mulai, lalu geser di papan atau pakai tombol arah.';
      placeFood(); draw();
    }
    function stop(text){
      clearInterval(timer); running = false;
      if (text) msg.textContent = text;
    }
    function tick(){
      if (view.hidden) { stop(); return; }
      dir = nextDir;
      var h = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
      var self = snake.some(function(s){ return s.x === h.x && s.y === h.y; });
      if (h.x < 0 || h.y < 0 || h.x >= N || h.y >= N || self) { stop('Game over! Skor: ' + score); return; }
      snake.unshift(h);
      if (h.x === food.x && h.y === food.y) {
        score++; scoreEl.textContent = 'Skor: ' + score; placeFood();
      } else {
        snake.pop();
      }
      draw();
    }
    function start(){
      if (running) return;
      reset(); running = true; msg.textContent = '';
      timer = setInterval(tick, 140);
    }
    function turn(i){
      var d = DIRS[i];
      if (d.x === -dir.x && d.y === -dir.y) return;
      nextDir = d;
    }
    document.getElementById('snake-start').addEventListener('click', start);
    document.querySelectorAll('#snake-pad [data-d]').forEach(function(b){
      b.addEventListener('click', function(){ turn(parseInt(b.dataset.d, 10)); });
    });
    window.mzSwipe(cv, turn);
    document.addEventListener('keydown', function(e){
      var map = {ArrowLeft:0, ArrowUp:1, ArrowRight:2, ArrowDown:3};
      if (!(e.key in map) || view.hidden) return;
      e.preventDefault();
      turn(map[e.key]);
    });
    reset();
  })();

  /* ===== TEBAK ANGKA ===== */
  (function(){
    var input = document.getElementById('guess-input');
    var btn = document.getElementById('guess-btn');
    var msg = document.getElementById('guess-msg');
    var triesEl = document.getElementById('guess-tries');
    var target, tries, done;
    function reset(){
      target = 1 + Math.floor(Math.random() * 100);
      tries = 0; done = false;
      msg.textContent = '';
      triesEl.textContent = 'Percobaan: 0';
      input.value = '';
    }
    function guess(){
      if (done) return;
      var v = parseInt(input.value, 10);
      if (isNaN(v) || v < 1 || v > 100) { msg.textContent = 'Masukkan angka 1 sampai 100.'; return; }
      tries++;
      triesEl.textContent = 'Percobaan: ' + tries;
      if (v === target) { done = true; msg.textContent = 'Benar! Angkanya ' + target + '.'; }
      else if (v > target) msg.textContent = v + ' terlalu besar.';
      else msg.textContent = v + ' terlalu kecil.';
      input.value = '';
    }
    btn.addEventListener('click', guess);
    input.addEventListener('keydown', function(e){ if (e.key === 'Enter') guess(); });
    document.getElementById('guess-reset').addEventListener('click', reset);
    reset();
  })();

  /* ===== SUIT ===== */
  (function(){
    var msg = document.getElementById('rps-msg');
    var scoreEl = document.getElementById('rps-score');
    var names = {batu:'Batu', gunting:'Gunting', kertas:'Kertas'};
    var beats = {batu:'gunting', gunting:'kertas', kertas:'batu'};
    var keys = ['batu', 'gunting', 'kertas'];
    var w = 0, l = 0, d = 0;
    function show(){ scoreEl.textContent = 'Menang ' + w + ' | Kalah ' + l + ' | Seri ' + d; }
    document.querySelectorAll('[data-pick]').forEach(function(b){
      b.addEventListener('click', function(){
        var me = b.dataset.pick;
        var bot = keys[Math.floor(Math.random() * 3)];
        var out;
        if (me === bot) { d++; out = 'Seri!'; }
        else if (beats[me] === bot) { w++; out = 'Kamu menang!'; }
        else { l++; out = 'Kamu kalah.'; }
        msg.textContent = 'Kamu: ' + names[me] + ' | Bot: ' + names[bot] + '. ' + out;
        show();
      });
    });
    document.getElementById('rps-reset').addEventListener('click', function(){
      w = 0; l = 0; d = 0; msg.textContent = 'Pilih salah satu.'; show();
    });
    show();
  })();
})();
</script>
'''

if not os.path.exists(g):
    print('games.html : GAGAL (file tidak ada)')
elif 'mz-games2' in t:
    print('games.html : sudah pernah')
else:
    nav_m = re.search(r'(<nav class="ocean-nav" id="games-nav"[^>]*>.*?)(</nav>)', t, re.S)
    ok = bool(nav_m) and ('</main>' in t) and ('</head>' in t) and (t.rfind('</body>') != -1)
    if not ok:
        print('games.html : GAGAL (struktur tidak cocok). Tidak ada yang diubah.')
    else:
        shutil.copy(g, g + '.bak27')
        t = t[:nav_m.end(1)] + TABS + t[nav_m.end(1):]
        t = t.replace('</main>', SECTIONS + '</main>', 1)
        t = t.replace('</head>', '<style id="mz-games2">' + CSS + '</style>\n</head>', 1)
        old = "var valid = ['ttt','wam','rt','typing','wheel'];"
        if old in t:
            t = t.replace(old, "var valid = ['ttt','wam','rt','typing','wheel','mem','g2048','snake','guess','rps'];", 1)
            solo = 'OK'
        else:
            solo = 'PERINGATAN: skrip pemisah game (fix26) belum terpasang, kartu game baru belum langsung membuka game-nya'
        i = t.rfind('</body>')
        t = t[:i] + JS + t[i:]
        open(g, 'w', encoding='utf-8').write(t)
        print('games.html : OK (5 game baru)')
        print('Daftar hash : ' + solo)

# ===================== index.html =====================
f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'data-tool="games.html#mem"' in s:
    print('index.html : sudah pernah')
else:
    def card(tool, title, desc, icon):
        return ('<div class="tool-card" data-tool="games.html#%s" role="button" tabindex="0"><span class="tool-icon">'
                '<svg viewBox="0 0 24 24" class="icon">%s</svg></span><div><h3>%s</h3><p>%s</p></div></div>'
                % (tool, icon, title, desc))
    cards = '\n  '.join([
        card('mem', 'Memory Match', 'Cari pasangan kartu yang sama.',
             '<rect x="3" y="4" width="8" height="10" rx="1.5"/><rect x="13" y="10" width="8" height="10" rx="1.5"/>'),
        card('g2048', '2048', 'Gabungkan angka sampai 2048.',
             '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 8h3v3H8zM13 13h3v3h-3z"/>'),
        card('snake', 'Snake', 'Makan titik, jangan sampai nabrak.',
             '<path d="M4 18h6a3 3 0 0 0 0-6H8a3 3 0 0 1 0-6h10"/><circle cx="19" cy="6" r="1.4"/>'),
        card('guess', 'Tebak Angka', 'Tebak angka rahasia 1 sampai 100.',
             '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7"/><path d="M12 17h.01"/>'),
        card('rps', 'Suit vs Bot', 'Batu, gunting, kertas lawan bot.',
             '<path d="M8 11V6a1.5 1.5 0 0 1 3 0v4M11 10V5a1.5 1.5 0 0 1 3 0v5M14 10V7a1.5 1.5 0 0 1 3 0v6c0 4-2 7-6 7s-5-3-6-5l-1-3a1.5 1.5 0 0 1 3-.5L8 13"/>'),
    ])
    m = re.search(r'<div class="tool-card" data-tool="games\.html#wheel".*?</p></div></div>', s, re.S)
    if m:
        shutil.copy(f, f + '.bak27')
        s = s[:m.end()] + '\n  ' + cards + s[m.end():]
        open(f, 'w', encoding='utf-8').write(s)
        print('index.html : OK (5 kartu baru)')
    else:
        print('index.html : GAGAL (kartu Spin Wheel tidak ketemu). Jalankan fix26 dulu.')
