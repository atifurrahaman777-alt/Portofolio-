import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-sidelinks' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

marker = '<button id="auth-toggle"'
if marker not in s:
    print('GAGAL: tombol Akun/Masuk tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak16')

row = ('<div class="mz-sidelinks">'
       '<a class="mz-sl" href="https://whatsapp.com/channel/0029VbDsbXE1noz0Tpjb5K1O" target="_blank" rel="noopener">'
       '<svg viewBox="0 0 24 24" class="icon"><path d="M3 11v2a1 1 0 001 1h2l5 4V6L6 10H4a1 1 0 00-1 1z"/><path d="M15.5 8.5a5 5 0 010 7"/><path d="M18.5 6a9 9 0 010 12"/></svg>'
       '<span>Saluran</span></a>'
       '<a class="mz-sl" href="https://wa.me/6282339899845" target="_blank" rel="noopener">'
       '<svg viewBox="0 0 24 24" class="icon"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></svg>'
       '<span>Owner</span></a>'
       '</div>')
s = s.replace(marker, row + marker, 1)

css = '''
html body .mz-sidelinks{display:flex;gap:10px;margin-bottom:10px}
html body .mz-sl{flex:1 1 0;min-width:0;display:flex;align-items:center;justify-content:center;gap:8px;padding:11px 8px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--text);font:inherit;font-weight:700;font-size:.85rem;text-decoration:none;cursor:pointer}
html body .mz-sl svg{width:18px;height:18px;flex-shrink:0}
html body .mz-sl:active{transform:scale(.96)}
'''
s = s.replace('</head>', '<style id="mz-sidelinks">' + css + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Tombol : OK')
print('Style  : OK')
