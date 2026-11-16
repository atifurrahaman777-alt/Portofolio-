import re, shutil, sys

f = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = open(f, encoding='utf-8').read()
shutil.copy(f, f + '.bak')

# Fix 1: footer nimpa halaman game/alat
old_css = '.container{position:relative;z-index:1}'
found_css = old_css in s
s = s.replace(old_css, '.container{position:relative}')

# Fix 2: kartu Chat Global jadi sama kayak tool-card di beranda
new_card = '''<section id="gchat">
<a class="tool-card" href="chat.html"><span class="tool-icon"><svg viewBox="0 0 24 24" class="icon"><path d="M21 12a8 8 0 10-3.3 6.4L21 20l-1.2-3.4A8 8 0 0021 12z"/></svg></span><div><h3>Buka Chat Global</h3><p>Ngobrol, story, dan catatan bareng.</p></div></a>
</section>'''
s, n = re.subn(r'<section id="gchat">.*?</section>', lambda m: new_card, s, count=1, flags=re.S)

open(f, 'w', encoding='utf-8').write(s)
print('Fix footer :', 'OK' if found_css else 'GAGAL (baris CSS tidak ketemu)')
print('Fix chat   :', 'OK' if n else 'GAGAL (section gchat tidak ketemu)')
