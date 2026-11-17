import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-camfix' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-profile2"' not in s:
    print('GAGAL: profil baru (fix33) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

css = '''
html body .pf-head{pointer-events:none}
html body .pf-head>*{pointer-events:auto}
html body .pf-banner .pf-cam{z-index:6;bottom:14px;right:12px;width:42px;height:42px}
html body .pf-banner{z-index:1}
'''
shutil.copy(f, f + '.bak35')
s = s.replace('</head>', '<style id="mz-camfix">' + css + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Perbaikan tombol kamera : OK')
