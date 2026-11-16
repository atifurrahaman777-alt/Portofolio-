f = 'index.html'
s = open(f, encoding='utf-8').read()
bad = '</script>' + chr(92) + 'n</body>'
good = '</script>\n</body>'
n = s.count(bad)
s = s.replace(bad, good)
open(f, 'w', encoding='utf-8').write(s)
print('Teks \\n dihapus:', 'OK' if n else 'Tidak ketemu (sudah bersih)')
