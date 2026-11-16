import re, shutil, sys

f = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = open(f, encoding='utf-8').read()
shutil.copy(f, f + '.bak2')

icons = {
    'HTML': 'devicon-html5-plain colored',
    'CSS': 'devicon-css3-plain colored',
    'JavaScript': 'devicon-javascript-plain colored',
    'Node.js': 'devicon-nodejs-plain colored',
    'Git': 'devicon-git-plain colored',
    'Linux': 'devicon-linux-plain',
}
for name, cls in icons.items():
    pat = r'<span class="skill-badge"[^>]*>[^<]*</span>' + re.escape(name) + r'(?=</div>)'
    extra = ' style="color:var(--text)"' if name == 'Linux' else ''
    s, n = re.subn(pat, '<i class="%s"%s></i>%s' % (cls, extra, name), s)
    print(name, 'OK' if n else 'GAGAL')

open(f, 'w', encoding='utf-8').write(s)
