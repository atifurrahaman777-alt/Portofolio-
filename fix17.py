import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-nofab' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

s2, n = re.subn(r'<a class="wa-fab".*?</a>\s*', '', s, count=1, flags=re.S)
if not n:
    print('GAGAL: tombol WhatsApp bulat tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

shutil.copy(f, f + '.bak17')
s2 = s2.replace('</head>', '<style id="mz-nofab">.wa-fab{display:none!important}</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s2)
print('Tombol WhatsApp bulat : dihapus (OK)')
