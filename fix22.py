import shutil
from urllib.parse import quote

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border5' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-border2"' not in s:
    print('GAGAL: bingkai aksesoris (fix19) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

def uri(inner):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">' + inner + '</svg>'
    return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

HEART = uri('<path fill="#f43f5e" stroke="#9f1239" stroke-width="1" stroke-linejoin="round" d="M12 21s-7.5-4.6-10-9.3C.5 8 2.4 4.5 6 4.5c2 0 3.6 1.1 4.5 2.8C11.4 5.6 13 4.5 15 4.5c3.6 0 5.5 3.5 4 7.2C19.5 16.4 12 21 12 21z"/>')
SPARK = uri('<path fill="#facc15" stroke="#a16207" stroke-width="1" stroke-linejoin="round" d="M12 1l2.6 8.4L23 12l-8.4 2.6L12 23l-2.6-8.4L1 12l8.4-2.6z"/>')
BOLT = uri('<path fill="#22d3ee" stroke="#0e7490" stroke-width="1.2" stroke-linejoin="round" d="M13 2L4 14h6l-1 8 9-12h-6l1-8z"/>')
CROWN = uri('<path fill="#facc15" stroke="#a16207" stroke-width="1" stroke-linejoin="round" d="M2 18l1.5-10 5 4.5L12 4l3.5 8.5 5-4.5L22 18z"/><rect x="2" y="19" width="20" height="3" rx="1" fill="#facc15" stroke="#a16207" stroke-width="1"/><circle cx="12" cy="14" r="1.4" fill="#ef4444"/><circle cx="7" cy="14.5" r="1" fill="#3b82f6"/><circle cx="17" cy="14.5" r="1" fill="#22c55e"/>')
FLAME = uri('<path fill="#f97316" stroke="#c2410c" stroke-width="1" stroke-linejoin="round" d="M12 1c1 4.5 6 6.5 6 12a6 6 0 0 1-12 0c0-2.5 1.2-4 2.4-5.2.2 1.7 1 2.7 2.1 2.9C10 8 10.8 4.5 12 1z"/><path fill="#fde047" d="M12 22a3.4 3.4 0 0 1-3.4-3.4c0-2.2 2.2-3.4 3.4-5.6 1.2 2.2 3.4 3.4 3.4 5.6A3.4 3.4 0 0 1 12 22z"/>')
FLOWER = uri('<g fill="#f9a8d4" stroke="#ec4899" stroke-width=".9"><circle cx="12" cy="6.3" r="3.4"/><circle cx="17.4" cy="10.2" r="3.4"/><circle cx="15.3" cy="16.6" r="3.4"/><circle cx="8.7" cy="16.6" r="3.4"/><circle cx="6.6" cy="10.2" r="3.4"/></g><circle cx="12" cy="12" r="2.8" fill="#facc15" stroke="#a16207" stroke-width=".8"/>')
BOW = uri('<path fill="#ec4899" stroke="#9d174d" stroke-width="1" stroke-linejoin="round" d="M12 12L2.5 6v12z"/><path fill="#ec4899" stroke="#9d174d" stroke-width="1" stroke-linejoin="round" d="M12 12l9.5-6v12z"/><circle cx="12" cy="12" r="2.6" fill="#be185d" stroke="#9d174d" stroke-width="1"/>')

def pos(top=None, right=None, bottom=None, left=None, tf='none'):
    out = ''
    for k, v in (('top', top), ('right', right), ('bottom', bottom), ('left', left)):
        out += k + ':' + (v if v else 'auto') + '!important;'
    return out + 'transform:' + tf + '!important;'

def rule(sel, img, w, h, p):
    return ('html body ' + sel + '{content:""!important;background:' + img + ' center/contain no-repeat!important;'
            'width:calc(var(--sz,40px)*' + w + ')!important;height:calc(var(--sz,40px)*' + h + ')!important;'
            'font-size:0!important;border:none!important;clip-path:none!important;' + p + '}\n')

css = ''
css += rule('.bd-a-bunga::before', FLOWER, '.55', '.55', pos(top='-20%', right='-20%'))
css += rule('.bd-a-hati::before', HEART, '.52', '.52', pos(top='-20%', right='-20%'))
css += rule('.bd-a-bintang::before', SPARK, '.5', '.5', pos(top='-20%', right='-20%'))
css += rule('.bd-a-bintang::after', SPARK, '.32', '.32', pos(bottom='-12%', left='-16%'))
css += rule('.bd-a-kilat::before', BOLT, '.5', '.58', pos(top='-22%', right='-18%'))
css += rule('.bd-a-kilat::after', BOLT, '.36', '.42', pos(bottom='-14%', left='-18%'))
css += rule('.bd-a-pita::before', BOW, '.6', '.5', pos(top='-18%', left='-20%', tf='rotate(-18deg)'))
css += rule('.bd-a-mahkota::before', CROWN, '.8', '.6', pos(top='-50%', left='50%', tf='translateX(-50%)'))
css += rule('.bd-a-api::before', FLAME, '.6', '.72', pos(top='-52%', left='50%', tf='translateX(-50%)'))

shutil.copy(f, f + '.bak22')
s = s.replace('</head>', '<style id="mz-border5">\n' + css + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Aksesoris gambar : OK')
