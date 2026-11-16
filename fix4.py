import shutil, sys

f = sys.argv[1] if len(sys.argv) > 1 else 'games.html'
s = open(f, encoding='utf-8').read()
if 'mz-theme' in s:
    print('Sudah pernah dipasang.')
    sys.exit()
shutil.copy(f, f + '.bak4')

P = 'html body:is(.light-mode,:not(.light-mode))'

rules = [
 ('.card,.game-box,.ocean-tab',
  'background:var(--card)!important;border:1px solid var(--line)!important;box-shadow:0 4px 18px var(--shadow)!important;border-radius:14px!important'),
 ('.ocean-tab',
  'color:var(--muted)!important;border-radius:999px!important;box-shadow:none!important'),
 ('.ocean-tab.active',
  'background:var(--accent)!important;border-color:var(--accent)!important;color:#fff!important'),
 ('.ttt-cell,.wam-hole,.typing-text',
  'background:var(--bg)!important;border:1px solid var(--line)!important;box-shadow:none!important;border-radius:12px!important'),
 ('.rt-area',
  'border:1px solid var(--line)!important;box-shadow:none!important'),
 ('.ttt-cell,.ttt-cell:disabled',
  'color:var(--text)!important;-webkit-text-fill-color:var(--text)!important'),
 ('.wam-hole.up',
  'background:var(--accent)!important'),
 ('.game-controls button',
  'background:var(--card)!important;color:var(--text)!important;border:1px solid var(--line)!important;box-shadow:none!important;border-radius:10px!important'),
 ('.game-controls button.active',
  'background:var(--accent)!important;color:#fff!important;border-color:var(--accent)!important;outline:none!important'),
 ('.btn',
  'background:var(--accent)!important;color:#fff!important;border:1px solid var(--line)!important;box-shadow:0 4px 18px var(--shadow)!important;text-shadow:none!important;border-radius:10px!important'),
 ('.game-controls button:not(.active)',
  'background:var(--card)!important;color:var(--text)!important;box-shadow:none!important'),
 ('#typing-input,#wheel-options,textarea,input',
  'background:var(--bg)!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:9px!important;box-shadow:none!important'),
 ('.typing-stats b',
  'color:var(--accent)!important'),
 ('.wheel-pointer',
  'border-top-color:var(--accent)!important'),
 ('h1,h2,h3,.brand,#wheel-result,.ttt-status,.wam-top',
  'color:var(--text)!important;text-shadow:none!important'),
 ('.accent,.eyebrow',
  'color:var(--accent)!important;text-shadow:none!important'),
 ('.sub,.rt-stats,footer',
  'color:var(--muted)!important;text-shadow:none!important'),
 ('#theme-toggle',
  'background:var(--card)!important;border:1px solid var(--line)!important;color:var(--text)!important;border-radius:8px!important;box-shadow:none!important'),
]

css = ('html body:not(.light-mode){--bg:#0a0a0a;--card:#141414;--line:#2a2a2a;--text:#f5f5f5;--muted:#9ca3af;--shadow:rgba(0,0,0,.5);--gold:#2563eb;--purple:#2563eb;--accent:#2563eb}\n'
       'html body.light-mode{--bg:#ffffff;--card:#f7f7f8;--line:#e5e5e5;--text:#0a0a0a;--muted:#6b7280;--shadow:rgba(0,0,0,.12);--gold:#2563eb;--purple:#2563eb;--accent:#2563eb}\n')
css += P + '{background:var(--bg)!important;color:var(--text)!important}\n'
css += P + '::before,' + P + '::after{background:none!important}\n'
for sels, decl in rules:
    css += ','.join(P + ' ' + x for x in sels.split(',')) + '{' + decl + '}\n'

style = '<style id="mz-theme">\n' + css + '</style>\n'

script = '''<script>
(function(){
  function sync(){
    try{
      var pb = window.parent !== window ? window.parent.document.body : null;
      if(pb) document.body.classList.toggle('light-mode', pb.classList.contains('light-mode'));
    }catch(e){}
  }
  sync();
  window.addEventListener('load', sync);
  try{
    new MutationObserver(sync).observe(window.parent.document.body, {attributes:true, attributeFilter:['class']});
  }catch(e){}
})();
</script>
'''

ok1 = '</head>' in s
ok2 = '</body>' in s
s = s.replace('</head>', style + '</head>', 1)
s = s.replace('</body>', script + '</body>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Style  :', 'OK' if ok1 else 'GAGAL')
print('Script :', 'OK' if ok2 else 'GAGAL')
