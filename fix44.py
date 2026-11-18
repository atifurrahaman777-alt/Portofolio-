import re, shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()

tag = '<span>Saluran Tele</span>'
i = s.find(tag)
if i < 0:
    print('GAGAL: tombol Saluran Tele tidak ketemu (pastikan fix43 sudah jalan). Tidak ada yang diubah.')
    raise SystemExit
start = s.rfind('<div class="mz-sidelinks', 0, i)
end = s.find('</div>', i)
if start < 0 or end < 0:
    print('GAGAL: baris saluran tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit
end += len('</div>')

raw = input('Link saluran Telegram yang BENAR (contoh https://t.me/namasaluran atau @namasaluran): ').strip()
if raw.startswith('@'):
    raw = 'https://t.me/' + raw[1:]
elif raw.startswith('t.me/') or raw.startswith('telegram.me/'):
    raw = 'https://' + raw
if not re.fullmatch(r'https://(t\.me|telegram\.me)/[A-Za-z0-9_+/.-]{2,100}', raw):
    print('Link tidak valid. Harus berbentuk https://t.me/namasaluran. Tidak ada yang diubah.')
    raise SystemExit

block = s[start:end]
opener = '<a class="mz-sl" href="'
a = block.rfind(opener)
if a < 0:
    print('GAGAL: link Telegram di baris saluran tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit
h1 = a + len(opener)
h2 = block.find('"', h1)
block = block[:h1] + raw + block[h2:]
block = block.replace('<div class="mz-sidelinks">', '<div class="mz-sidelinks mz-ch">', 1)

css = '''
html body .mz-sidelinks.mz-ch .mz-sl{flex-direction:column;gap:5px;padding:10px 4px;font-size:.72rem;line-height:1.15;text-align:center;white-space:nowrap}
html body .mz-sidelinks.mz-ch .mz-sl svg{width:20px;height:20px}
html body .mz-sidelinks.mz-ch .mz-sl span{display:block;max-width:100%;overflow:hidden;text-overflow:ellipsis}
'''

shutil.copy(f, f + '.bak44')
s = s[:start] + block + s[end:]
s = re.sub(r'<style id="mz-ch">.*?</style>\n?', '', s, flags=re.S)
s = s.replace('</head>', '<style id="mz-ch">' + css + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Tombol saluran dirapikan : OK')
print('Link saluran Telegram    : ' + raw)
