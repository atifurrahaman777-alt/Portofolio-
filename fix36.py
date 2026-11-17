import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-sheetfix' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-profile2"' not in s:
    print('GAGAL: profil baru (fix33) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

css = '''
html body .pf-sheet{top:0!important;bottom:auto!important;height:100vh!important;height:100dvh!important;overscroll-behavior:contain;touch-action:none}
html body .pf-sheet-panel{max-height:85vh!important;max-height:85dvh!important;overflow-y:auto;overscroll-behavior:contain;touch-action:pan-y;-webkit-overflow-scrolling:touch}
html.mz-sheetlock,html.mz-sheetlock body{overflow:hidden!important}
'''

js = '''
(function(){
  var root = document.documentElement;
  function sync(){
    var open = !!document.querySelector('.pf-sheet:not([hidden])');
    root.classList.toggle('mz-sheetlock', open);
  }
  new MutationObserver(sync).observe(document.body, {childList:true, subtree:true, attributes:true, attributeFilter:['hidden']});
  document.addEventListener('touchmove', function(e){
    var t = e.target;
    if (t && t.classList && t.classList.contains('pf-sheet')) e.preventDefault();
  }, {passive:false});
  sync();
})();
'''

i = s.rfind('</body>')
if i == -1 or '</head>' not in s:
    print('GAGAL: struktur index.html tidak cocok. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak36')
s = s.replace('</head>', '<style id="mz-sheetfix">' + css + '</style>\n</head>', 1)
i = s.rfind('</body>')
s = s[:i] + '<script id="mz-sheetfix-js">' + js + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Perbaikan panel banner : OK')
