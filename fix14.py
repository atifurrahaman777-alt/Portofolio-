import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-owner' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
shutil.copy(f, f + '.bak14')

css = '''
html body .owner-badge.owner-role{background:var(--card)!important;background-image:none!important;color:var(--text)!important;border:1px solid var(--line)!important;animation:none!important;text-shadow:none!important;box-shadow:none!important}
html body .owner-badge.owner-role *{animation:none!important;text-shadow:none!important}
'''
style = '<style id="mz-owner">' + css + '</style>\n'

ok = '</head>' in s
s = s.replace('</head>', style + '</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Style :', 'OK' if ok else 'GAGAL')
