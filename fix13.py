import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-side' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
shutil.copy(f, f + '.bak13')

css = '''
html body .sidebar{top:0!important;bottom:auto!important;height:100vh!important;height:100dvh!important;overflow:hidden!important;overscroll-behavior:contain}
html body .sidebar-head{margin-bottom:10px!important;flex-shrink:0}
html body .sidebar-nav{flex:0 1 auto!important;min-height:0;overflow-y:auto;overscroll-behavior:contain;gap:2px!important}
html body .sidebar-nav .nav-btn{flex:0 0 auto!important;padding:10px 12px!important;font-size:.9rem!important;margin-top:0!important}
html body .sidebar-nav .nav-btn span{width:22px!important;height:22px!important}
html body .sidebar-foot{margin-top:auto!important;flex-shrink:0}
html.mz-lock,html.mz-lock body{overflow:hidden!important}
'''
style = '<style id="mz-side">' + css + '</style>\n'

js = '''
(function(){
  var sb = document.getElementById('sidebar');
  var ov = document.getElementById('sidebarOverlay');
  if (!sb) return;
  function sync(){
    document.documentElement.classList.toggle('mz-lock', sb.classList.contains('active'));
  }
  new MutationObserver(sync).observe(sb, {attributes:true, attributeFilter:['class']});
  if (ov) ov.addEventListener('touchmove', function(e){ e.preventDefault(); }, {passive:false});
  sync();
})();
'''

i = s.rfind('</body>')
ok = i != -1
s = s.replace('</head>', style + '</head>', 1)
if ok:
    i = s.rfind('</body>')
    s = s[:i] + '<script id="mz-side-js">' + js + '</script>\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Style  : OK')
print('Script :', 'OK' if ok else 'GAGAL')
