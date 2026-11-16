import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-badge' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
shutil.copy(f, f + '.bak9')

css = '''
html body .owner-badge{display:inline-flex!important;align-items:center!important;gap:8px!important;padding:4px 14px 4px 4px!important;font-size:.78rem!important;font-weight:700!important;line-height:1!important;white-space:nowrap!important;border-radius:999px!important}
html body .owner-badge .badge-avatar{width:28px!important;height:28px!important;margin:0!important;vertical-align:baseline!important;font-size:.8rem!important;flex-shrink:0!important}
html body #badgeText{display:inline-flex!important;align-items:center!important;gap:4px!important;line-height:1!important}
html body .owner-badge .badge-avatar svg,html body #upAvatar svg{width:58%;height:58%;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
'''
style = '<style id="mz-badge">' + css + '</style>\n'

js = '''
(function(){
  var PERSON = '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></svg>';
  ['badgeAvatar','upAvatar'].forEach(function(id){
    var el = document.getElementById(id);
    if (!el) return;
    function fix(){ if (el.textContent.trim() === '?') el.innerHTML = PERSON; }
    fix();
    new MutationObserver(fix).observe(el, {childList:true, characterData:true, subtree:true});
  });
})();
'''

s = s.replace('</head>', style + '</head>', 1)
i = s.rfind('</body>')
ok = i != -1
if ok:
    s = s[:i] + '<script id="mz-badge-js">' + js + '</script>\\n' + s[i:]
open(f, 'w', encoding='utf-8').write(s)
print('Style  : OK')
print('Script :', 'OK' if ok else 'GAGAL')
