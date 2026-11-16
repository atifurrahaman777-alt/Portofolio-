import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border3' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-border2"' not in s:
    print('GAGAL: bingkai aksesoris (fix19) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

css = '''
html body .bd-grid{grid-template-columns:repeat(3,1fr)!important;gap:26px 10px!important;max-height:none!important;overflow:visible!important;padding:30px 4px 8px!important}
html body .bd-opt{padding:8px 2px!important;font-size:.8rem!important;border-radius:14px!important}
html body .bd-dot{width:56px!important;height:56px!important;--sz:56px;--r:3px;font-size:1.25rem!important;margin:0 auto 14px!important}
html body .bd-a-kucing::before,html body .bd-a-kucing::after{top:-24%!important;width:40%!important;height:42%!important}
html body .bd-a-kucing::before{left:4%!important}
html body .bd-a-kucing::after{right:4%!important}
html body .bd-a-tanduk::before,html body .bd-a-tanduk::after{top:-30%!important;width:30%!important;height:42%!important}
html body .bd-a-tanduk::before{left:8%!important}
html body .bd-a-tanduk::after{right:8%!important}
html body .bd-a-halo::before{top:-38%!important;left:14%!important;right:14%!important;height:24%!important}
html body .bd-a-bunga::before,html body .bd-a-hati::before,html body .bd-a-bintang::before,html body .bd-a-kilat::before{font-size:calc(var(--sz,40px)*.55)!important;top:-20%!important;right:-20%!important}
html body .bd-a-bintang::after,html body .bd-a-kilat::after{font-size:calc(var(--sz,40px)*.4)!important;bottom:-14%!important;left:-18%!important}
html body .bd-a-pita::before{font-size:calc(var(--sz,40px)*.58)!important;top:-24%!important;left:-20%!important}
html body .bd-a-mahkota::before{font-size:calc(var(--sz,40px)*.7)!important;top:-52%!important}
html body .bd-a-api::before{font-size:calc(var(--sz,40px)*.65)!important;top:-46%!important}
'''
shutil.copy(f, f + '.bak20')
s = s.replace('</head>', '<style id="mz-border3">' + css + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Perbaikan bingkai : OK')
