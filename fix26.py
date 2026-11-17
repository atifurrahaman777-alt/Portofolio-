import re, shutil, os

# ===== 1. index.html =====
f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'data-tool="games.html#ttt"' in s:
    print('index.html : sudah pernah')
else:
    s, n1 = re.subn(r'<div class="project-links">.*?</div>\s*', '', s, count=1, flags=re.S)

    def card(tool, title, desc, icon):
        return ('<div class="tool-card" data-tool="games.html#%s" role="button" tabindex="0"><span class="tool-icon">'
                '<svg viewBox="0 0 24 24" class="icon">%s</svg></span><div><h3>%s</h3><p>%s</p></div></div>'
                % (tool, icon, title, desc))

    cards = '\n  '.join([
        card('ttt', 'Tic Tac Toe', 'Lawan bot, pilih tingkat kesulitan.',
             '<path d="M9 3v18M15 3v18M3 9h18M3 15h18"/>'),
        card('wam', 'Whack-a-Mole', 'Pukul tikus secepat mungkin dalam 30 detik.',
             '<path d="M3 21l7-7"/><path d="M14 4l6 6-3 3-6-6 3-3z"/><path d="M12.5 8.5l-7 7"/>'),
        card('rt', 'Reaction Test', 'Ukur kecepatan reaksimu.',
             '<path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z"/>'),
        card('typing', 'Typing Test', 'Cek kecepatan dan akurasi mengetikmu.',
             '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/>'),
        card('wheel', 'Spin Wheel', 'Putar roda dengan pilihanmu sendiri.',
             '<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4"/>'),
    ])

    s, n2 = re.subn(r'<div class="tool-card" data-tool="games\.html".*?</p></div></div>',
                    lambda m: cards, s, count=1, flags=re.S)
    print('Tombol Channel dihapus :', 'OK' if n1 else 'GAGAL (tidak ketemu, mungkin sudah hilang)')
    print('Kartu game dipisah     :', 'OK' if n2 else 'GAGAL (kartu Games tidak ketemu)')
    if n2:
        shutil.copy(f, f + '.bak26')
        open(f, 'w', encoding='utf-8').write(s)
    else:
        print('index.html tidak diubah.')

# ===== 2. games.html: buka langsung game yang dipilih =====
g = 'games.html'
if not os.path.exists(g):
    print('games.html : GAGAL (file tidak ada)')
else:
    t = open(g, encoding='utf-8').read()
    if 'mz-solo' in t:
        print('games.html : sudah pernah')
    else:
        js = '''<script id="mz-solo">
(function(){
  var valid = ['ttt','wam','rt','typing','wheel'];
  function go(){
    var h = (location.hash || '').replace('#','');
    if (valid.indexOf(h) === -1) return;
    if (typeof showGame === 'function') showGame(h);
    var nav = document.getElementById('games-nav');
    if (nav) nav.style.display = 'none';
    var hero = document.querySelector('.hero');
    if (hero) hero.style.display = 'none';
  }
  go();
  window.addEventListener('hashchange', go);
})();
</script>
'''
        i = t.rfind('</body>')
        if i == -1:
            print('games.html : GAGAL (</body> tidak ketemu)')
        else:
            shutil.copy(g, g + '.bak26')
            t = t[:i] + js + t[i:]
            open(g, 'w', encoding='utf-8').write(t)
            print('games.html : OK')
