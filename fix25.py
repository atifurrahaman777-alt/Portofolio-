import shutil
from urllib.parse import quote

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border8' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

K1 = "{id:'kelinci', n:'Kelinci', cls:'bd-a-kelinci'},"
K2 = "{id:'berlian', n:'Berlian', cls:'bd-a-berlian', owner:true}"
if 'id="mz-border6"' not in s or K1 not in s or K2 not in s:
    print('GAGAL: bingkai sebelumnya (fix23) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

def uri(inner, vb='0 0 24 24', par=''):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s"%s>%s</svg>' % (vb, par, inner)
    return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

def shape(inner, stroke=6):
    g = '<g fill="#000" stroke="#000" stroke-width="%d" stroke-linejoin="round">%s</g>' % (stroke, inner)
    return uri(g, '0 0 100 100', ' preserveAspectRatio="none"')

# ---------- Aksesoris realistis ----------
CROWN = uri('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2a8"/><stop offset=".45" stop-color="#ffc928"/><stop offset="1" stop-color="#b07400"/></linearGradient><radialGradient id="r"><stop offset="0" stop-color="#ff8a8a"/><stop offset="1" stop-color="#b30000"/></radialGradient><radialGradient id="b"><stop offset="0" stop-color="#9fd0ff"/><stop offset="1" stop-color="#0b4fb3"/></radialGradient></defs><path d="M4 34L8 10L22 22L32 5L42 22L56 10L60 34Z" fill="url(#g)" stroke="#8a5a00" stroke-width="1.4" stroke-linejoin="round"/><rect x="4" y="33" width="56" height="6" rx="2" fill="url(#g)" stroke="#8a5a00" stroke-width="1.2"/><path d="M8 12L22 24L32 8" fill="none" stroke="#fff6c8" stroke-width="1" opacity=".7"/><circle cx="32" cy="27" r="3.4" fill="url(#r)" stroke="#7a0000" stroke-width=".8"/><circle cx="17" cy="29" r="2.4" fill="url(#b)" stroke="#06316f" stroke-width=".7"/><circle cx="47" cy="29" r="2.4" fill="url(#b)" stroke="#06316f" stroke-width=".7"/><circle cx="8" cy="9" r="2.4" fill="#fff6c8" stroke="#8a5a00" stroke-width=".8"/><circle cx="32" cy="4.5" r="2.6" fill="#fff6c8" stroke="#8a5a00" stroke-width=".8"/><circle cx="56" cy="9" r="2.4" fill="#fff6c8" stroke="#8a5a00" stroke-width=".8"/>', '0 0 64 40')

FLAME = uri('<defs><radialGradient id="o" cx=".5" cy=".85" r=".8"><stop offset="0" stop-color="#fff7a0"/><stop offset=".35" stop-color="#ffb11f"/><stop offset=".7" stop-color="#f2541b"/><stop offset="1" stop-color="#b3120f"/></radialGradient><radialGradient id="i" cx=".5" cy=".9" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#ffe066"/><stop offset="1" stop-color="#ff9d1a"/></radialGradient></defs><path d="M20 2C22 14 36 20 34 36C33 47 27 54 20 54C12 54 6 47 6 37C6 29 11 25 13 18C16 22 17 26 18 27C19 20 17 10 20 2Z" fill="url(#o)"/><path d="M20 26C22 32 28 35 27 42C26.5 48 23.5 51 20 51C16.5 51 13.5 48 13.5 43C13.5 38 18 35 20 26Z" fill="url(#i)"/>', '0 0 40 56')

WING = uri('<defs><linearGradient id="w" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#c9d6e8"/></linearGradient></defs><path d="M2 20C14 4 38 2 58 8C48 10 42 13 38 16C46 15 52 16 58 19C48 21 42 24 38 27C44 27 50 29 55 32C45 33 38 35 30 37C20 38 8 32 2 20Z" fill="url(#w)" stroke="#aebdd6" stroke-width=".7" stroke-linejoin="round"/><g fill="none" stroke="#aebdd6" stroke-width=".8" stroke-linecap="round"><path d="M6 20C18 14 34 12 54 10"/><path d="M8 24C20 21 34 20 52 20"/><path d="M12 28C22 27 34 27 48 30"/></g>', '0 0 60 40')

GEM = uri('<defs><linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8fbff"/><stop offset=".5" stop-color="#5fd6f2"/><stop offset="1" stop-color="#0a7fa6"/></linearGradient></defs><path d="M12 2H36L46 14L24 38L2 14Z" fill="url(#a)" stroke="#0a6a8c" stroke-width="1.2" stroke-linejoin="round"/><path d="M2 14H46M12 2L17 14L24 38L31 14L36 2M17 14L24 2L31 14" fill="none" stroke="#e6fbff" stroke-width=".9" opacity=".85" stroke-linejoin="round"/><path d="M12 2L17 14L2 14Z" fill="#ffffff" opacity=".45"/>', '0 0 48 40')

EAR = uri('<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9a9aa8"/><stop offset="1" stop-color="#55555f"/></linearGradient></defs><path d="M2 32C2 18 6 8 14 2C22 8 28 20 28 32Z" fill="url(#f)" stroke="#3a3a42" stroke-width="1.2" stroke-linejoin="round"/><path d="M8 30C8 21 10 15 14 10C19 15 22 22 22 30Z" fill="#f4a9bd"/><path d="M10 26C10 21 12 17 14 14" stroke="#fbd0dc" stroke-width="1" fill="none" stroke-linecap="round"/>', '0 0 30 34')

BUN = uri('<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e9e3ee"/></linearGradient></defs><path d="M10 2C16 4 18 16 17 28C16.5 35 13 38 10 38C7 38 3.5 35 3 28C2 16 4 4 10 2Z" fill="url(#f)" stroke="#d8cde0" stroke-width="1"/><path d="M10 8C13 10 14 18 13.5 27C13 32 11.5 34 10 34C8.5 34 7 32 6.5 27C6 18 7 10 10 8Z" fill="#f9b4c8"/>', '0 0 20 40')

HORN = uri('<defs><linearGradient id="h" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#5a0a0a"/><stop offset=".6" stop-color="#d62828"/><stop offset="1" stop-color="#ff8a7a"/></linearGradient></defs><path d="M3 32C3 22 6 12 14 3C13 12 17 20 21 32C16 28 8 28 3 32Z" fill="url(#h)" stroke="#4a0808" stroke-width="1" stroke-linejoin="round"/><path d="M6 27C10 25 15 25 19 27M7 21C10 19.5 14 19.5 17 21M9 15C11 14 13 14 14.5 14.5" stroke="#7a1010" stroke-width=".9" fill="none" stroke-linecap="round" opacity=".8"/>', '0 0 24 34')

def pos(top=None, right=None, bottom=None, left=None, tf='none'):
    out = ''
    for k, v in (('top', top), ('right', right), ('bottom', bottom), ('left', left)):
        out += k + ':' + (v if v else 'auto') + '!important;'
    return out + 'transform:' + tf + '!important;'

def acc2(sel, img, w, h, p):
    return ('html body ' + sel + '{content:""!important;background:' + img + ' center/contain no-repeat!important;'
            'width:calc(var(--sz,40px)*' + w + ')!important;height:calc(var(--sz,40px)*' + h + ')!important;'
            'font-size:0!important;border:none!important;border-radius:0!important;clip-path:none!important;' + p + '}\n')

# ---------- Bentuk bingkai ----------
GOLD = 'conic-gradient(from var(--ang),#6b4a00,#ffd34e,#fff6c2,#ffc21c,#8a5a00,#ffd34e,#6b4a00)'
HEX = '<polygon points="50,5 91,28 91,72 50,95 9,72 9,28"/>'
OKTA = '<polygon points="32,5 68,5 95,32 95,68 68,95 32,95 5,68 5,32"/>'
WAJIK = '<polygon points="50,5 95,50 50,95 5,50"/>'
KOTAK = '<rect x="6" y="6" width="88" height="88" rx="26"/>'
SHIELD = '<path d="M50 5L92 18V50C92 74 74 90 50 96C26 90 8 74 8 50V18Z"/>'
HEART = '<path d="M50 90C22 70 7 52 7 34C7 20 17 10 30 10C39 10 46 15 50 22C54 15 61 10 70 10C83 10 93 20 93 34C93 52 78 70 50 90Z"/>'
STAR = '<polygon points="50,8 64.1,32.6 91.8,38.4 72.8,59.4 75.9,87.6 50,76 24.1,87.6 27.2,59.4 8.2,38.4 35.9,32.6"/>'
PETAL = '<circle cx="50" cy="50" r="35"/><circle cx="82" cy="50" r="17"/><circle cx="72.6" cy="72.6" r="17"/><circle cx="50" cy="82" r="17"/><circle cx="27.4" cy="72.6" r="17"/><circle cx="18" cy="50" r="17"/><circle cx="27.4" cy="27.4" r="17"/><circle cx="50" cy="18" r="17"/><circle cx="72.6" cy="27.4" r="17"/>'

def ring(a, b, c):
    return 'conic-gradient(from var(--ang),' + a + ',' + b + ',' + c + ',' + b + ',' + a + ')'

SH = [
 ('kotak', 'Kotak', KOTAK, 6, '86%', ring('#1d4ed8', '#38bdf8', '#a5f3fc'), '9', False),
 ('heksa', 'Heksagon', HEX, 6, '86%', ring('#14532d', '#22c55e', '#bbf7d0'), '9', False),
 ('okta', 'Oktagon', OKTA, 6, '86%', ring('#4c1d95', '#8b5cf6', '#e9d5ff'), '9', False),
 ('perisai', 'Perisai', SHIELD, 6, '82%', ring('#7f1d1d', '#ef4444', '#fdba74'), '9', False),
 ('lope', 'Lope', HEART, 6, '80%', ring('#9d174d', '#ec4899', '#fbcfe8'), '9', False),
 ('kelopak', 'Kelopak', PETAL, 0, '84%', ring('#f9a8d4', '#ffffff', '#fde68a'), '9', False),
 ('wajik', 'Wajik', WAJIK, 6, '72%', ring('#134e4a', '#14b8a6', '#99f6e4'), '9', False),
 ('bintang5', 'Bintang Emas', STAR, 6, '74%', GOLD, '3', True),
 ('heksaneon', 'Heksa Neon', HEX, 6, '86%', 'conic-gradient(from var(--ang),#0ea5e9,#a855f7,#ec4899,#22d3ee,#0ea5e9)', '2.5', True),
 ('perisaiemas', 'Perisai Emas', SHIELD, 6, '82%', GOLD, '3.5', True),
 ('kelopakpelangi', 'Kelopak Pelangi', PETAL, 0, '84%', 'conic-gradient(from var(--ang),#ef4444,#f59e0b,#22c55e,#06b6d4,#8b5cf6,#ec4899,#ef4444)', '4', True),
]

CSS = r"""
@keyframes mzHSpin{to{--ang:360deg}}
@keyframes mzHSheen{0%{background-position:160% 0}55%,100%{background-position:-60% 0}}
html body [class*="bd-h-"]{position:relative!important;overflow:visible!important;border-radius:0!important;border:none!important;box-shadow:none!important;outline:none!important;isolation:isolate;-webkit-mask:var(--m) center/100% 100% no-repeat;mask:var(--m) center/100% 100% no-repeat}
html body [class*="bd-h-"]::before{content:"";position:absolute;inset:0;z-index:-1;background:var(--accent);-webkit-mask:var(--m) center/var(--k,86%) var(--k,86%) no-repeat;mask:var(--m) center/var(--k,86%) var(--k,86%) no-repeat;transform:none;animation:none}
html body [class*="bd-h-"]::after{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;background:linear-gradient(115deg,transparent 40%,rgba(255,255,255,.5) 50%,transparent 60%) 160% 0/250% 100% no-repeat;animation:mzHSheen 3.6s ease-in-out infinite}
html body [class*="bd-h-"] img{border-radius:0!important;-webkit-mask:var(--m) center/var(--k,86%) var(--k,86%) no-repeat;mask:var(--m) center/var(--k,86%) var(--k,86%) no-repeat}
html body .bd-o-emas{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#6b4a00,#ffd34e,#fff6c2,#ffc21c,#8a5a00,#ffd34e,#6b4a00) border-box!important;box-shadow:0 0 6px rgba(255,200,40,.45)}
html body .bd-a-halo::before{border-color:#ffe27a!important;box-shadow:0 0 6px 1px #fff6b8,0 0 14px 4px rgba(255,208,64,.6),inset 0 0 5px 1px #fffbe6!important}
@media(prefers-reduced-motion:reduce){html body [class*="bd-h-"],html body [class*="bd-h-"]::after{animation:none!important}}
"""

for sid, name, inner, stroke, k, rg, spd, owner in SH:
    CSS += 'html body .bd-h-%s{--m:%s;--k:%s;background:%s!important;animation:mzHSpin %ss linear infinite}\n' % (sid, shape(inner, stroke), k, rg, spd)

CSS += acc2('.bd-a-mahkota::before', CROWN, '.92', '.58', pos(top='-47%', left='50%', tf='translateX(-50%)'))
CSS += acc2('.bd-a-api::before', FLAME, '.56', '.78', pos(top='-58%', left='50%', tf='translateX(-50%)'))
CSS += acc2('.bd-a-berlian::before', GEM, '.62', '.52', pos(top='-46%', left='50%', tf='translateX(-50%)'))
CSS += acc2('.bd-a-sayap::before', WING, '.9', '.6', pos(top='0%', left='-84%', tf='scaleX(-1)'))
CSS += acc2('.bd-a-sayap::after', WING, '.9', '.6', pos(top='0%', right='-84%'))
CSS += ('html body .bd-a-kucing::before,html body .bd-a-kucing::after{content:""!important;background:' + EAR + ' center/contain no-repeat!important;clip-path:none!important;width:38%!important;height:42%!important}\n')
CSS += ('html body .bd-a-tanduk::before,html body .bd-a-tanduk::after{content:""!important;background:' + HORN + ' center/contain no-repeat!important;clip-path:none!important}\n')
CSS += ('html body .bd-a-kelinci::before,html body .bd-a-kelinci::after{content:""!important;background:' + BUN + ' center/contain no-repeat!important;border:none!important;border-radius:0!important;width:24%!important;height:60%!important}\n')

member = ''
owner_ = ''
for sid, name, inner, stroke, k, rg, spd, owner in SH:
    if owner:
        owner_ += ",\n    {id:'%s', n:'%s', cls:'bd-h-%s', owner:true}" % (sid, name, sid)
    else:
        member += "\n    {id:'%s', n:'%s', cls:'bd-h-%s'}," % (sid, name, sid)

shutil.copy(f, f + '.bak25')
s = s.replace(K1, K1 + member, 1)
s = s.replace(K2, K2 + owner_, 1)
s = s.replace('</head>', '<style id="mz-border8">\n' + CSS + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Bentuk bingkai baru : OK (11 bentuk)')
print('Aksesoris realistis : OK')
