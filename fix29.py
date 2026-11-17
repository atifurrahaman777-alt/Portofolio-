import re, shutil

g = 'games.html'
t = open(g, encoding='utf-8').read()
if 'mz-snake2' in t:
    print('Sudah pernah dipasang.')
    raise SystemExit
if '/* ===== SNAKE ===== */' not in t or '/* ===== TEBAK ANGKA ===== */' not in t:
    print('GAGAL: game Snake (fix27) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

NEW = r'''/* ===== SNAKE ===== */ /*mz-snake2*/
  (function(){
    var cv = document.getElementById('snake-canvas');
    var ctx = cv.getContext('2d');
    var scoreEl = document.getElementById('snake-score');
    var msg = document.getElementById('snake-msg');
    var view = document.getElementById('view-snake');
    var N = 15, S = cv.width / N, TICK = 150;
    var DIRS = [{x:-1,y:0},{x:0,y:-1},{x:1,y:0},{x:0,y:3-2}];
    var snake, prev, dir, queue, food, score, running = false, lastTick = 0, raf = 0;

    function cssv(n, f){
      var v = getComputedStyle(document.body).getPropertyValue(n).trim();
      return v || f;
    }
    function mod(v){ return ((v % N) + N) % N; }

    function placeFood(){
      for (var k = 0; k < 500; k++) {
        var p = {x: Math.floor(Math.random() * N), y: Math.floor(Math.random() * N)};
        var hit = snake.some(function(s){ return s.x === p.x && s.y === p.y; });
        if (!hit) { food = p; return; }
      }
    }

    function positions(t){
      var out = [], i;
      for (i = 0; i < snake.length; i++) {
        var a = prev[i] || snake[i], b = snake[i];
        var dx = b.x - a.x, dy = b.y - a.y;
        if (dx > N / 2) dx -= N; else if (dx < -N / 2) dx += N;
        if (dy > N / 2) dy -= N; else if (dy < -N / 2) dy += N;
        out.push({x: a.x + dx * t + 0.5, y: a.y + dy * t + 0.5});
      }
      for (i = 1; i < out.length; i++) {
        var p = out[i - 1], q = out[i];
        var ex = q.x - p.x, ey = q.y - p.y;
        ex -= Math.round(ex / N) * N;
        ey -= Math.round(ey / N) * N;
        out[i] = {x: p.x + ex, y: p.y + ey};
      }
      return out;
    }

    function draw(t){
      var bg = cssv('--bg', '#ffffff'), col = cssv('--text', '#111111');
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, cv.width, cv.height);

      var fx = (food.x + 0.5) * S, fy = (food.y + 0.5) * S;
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(fx, fy, S * 0.36, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,.75)';
      ctx.beginPath();
      ctx.arc(fx - S * 0.12, fy - S * 0.12, S * 0.08, 0, Math.PI * 2);
      ctx.fill();

      var pts = positions(t);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.strokeStyle = col;
      ctx.fillStyle = col;
      ctx.lineWidth = S * 0.72;
      var offs = [-N, 0, N], ox, oy;
      for (ox = 0; ox < 3; ox++) {
        for (oy = 0; oy < 3; oy++) {
          var dx = offs[ox], dy = offs[oy];
          ctx.beginPath();
          pts.forEach(function(p, i){
            var x = (p.x + dx) * S, y = (p.y + dy) * S;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
          });
          ctx.stroke();

          var hx = (pts[0].x + dx) * S, hy = (pts[0].y + dy) * S;
          ctx.fillStyle = col;
          ctx.beginPath();
          ctx.arc(hx, hy, S * 0.46, 0, Math.PI * 2);
          ctx.fill();

          var px = -dir.y, py = dir.x;
          ctx.fillStyle = bg;
          [-1, 1].forEach(function(sg){
            var ex = hx + dir.x * S * 0.14 + px * S * 0.19 * sg;
            var ey = hy + dir.y * S * 0.14 + py * S * 0.19 * sg;
            ctx.beginPath();
            ctx.arc(ex, ey, S * 0.1, 0, Math.PI * 2);
            ctx.fill();
          });
        }
      }
    }

    function reset(){
      cancelAnimationFrame(raf);
      snake = [{x:7,y:7},{x:6,y:7},{x:5,y:7}];
      prev = snake.slice();
      dir = DIRS[2]; queue = []; score = 0; running = false;
      scoreEl.textContent = 'Skor: 0';
      msg.textContent = 'Tekan Mulai. Tembus tembok boleh, tapi jangan makan badan sendiri.';
      placeFood();
      draw(1);
    }

    function stop(text){
      running = false;
      cancelAnimationFrame(raf);
      if (text) msg.textContent = text;
      draw(1);
    }

    function step(){
      if (queue.length) dir = queue.shift();
      var h = {x: mod(snake[0].x + dir.x), y: mod(snake[0].y + dir.y)};
      var eat = (h.x === food.x && h.y === food.y);
      var body = eat ? snake : snake.slice(0, -1);
      var hit = body.some(function(s){ return s.x === h.x && s.y === h.y; });
      if (hit) { stop('Game over! Kamu menabrak dirimu sendiri. Skor: ' + score); return false; }
      prev = snake.slice();
      snake.unshift(h);
      if (eat) {
        score++;
        scoreEl.textContent = 'Skor: ' + score;
        placeFood();
      } else {
        snake.pop();
      }
      return true;
    }

    function frame(now){
      if (!running) return;
      if (view.hidden) { stop(); return; }
      if (now - lastTick > TICK * 3) lastTick = now;
      while (running && now - lastTick >= TICK) {
        lastTick += TICK;
        if (!step()) return;
      }
      draw(Math.min((now - lastTick) / TICK, 1));
      raf = requestAnimationFrame(frame);
    }

    function start(){
      if (running) return;
      reset();
      running = true;
      msg.textContent = '';
      lastTick = performance.now();
      raf = requestAnimationFrame(frame);
    }

    function turn(i){
      var d = DIRS[i];
      var last = queue.length ? queue[queue.length - 1] : dir;
      if (d.x === -last.x && d.y === -last.y) return;
      if (d.x === last.x && d.y === last.y) return;
      if (queue.length < 2) queue.push(d);
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

  '''

t2, n = re.subn(r'/\* ===== SNAKE ===== \*/.*?(?=/\* ===== TEBAK ANGKA ===== \*/)', lambda m: NEW, t, count=1, flags=re.S)
if not n:
    print('GAGAL: blok Snake tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(g, g + '.bak29')
open(g, 'w', encoding='utf-8').write(t2)
print('Snake baru : OK')
