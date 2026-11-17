import re, shutil, random
from urllib.parse import quote

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'id="mz-fx"' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-profile2-js"' not in s:
    print('GAGAL: profil baru (fix33/fix34) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

HOLO = "{id:'holo', n:'Holo', owner:true}"
m = re.search(r"\{id:'holo', n:'Holo', owner:true\}", s)
if not m:
    print('GAGAL: daftar banner tidak ketemu. Tidak ada yang diubah.')
    raise SystemExit

def uri(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

def esc(c):
    return c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def wave(op):
    return uri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 20" preserveAspectRatio="none"><path d="M0 10Q25 0 50 10T100 10V20H0Z" fill="#fff" fill-opacity="%s"/></svg>' % op)

def rain():
    rnd = random.Random(7)
    chars = list('01$#<>/{}=+*;:%&?')
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><g font-family="monospace" font-size="11" font-weight="700">']
    for cx in range(8, 160, 14):
        n = rnd.randint(5, 9)
        y0 = rnd.randint(6, 160 - n * 12 - 6)
        for i in range(n):
            ch = esc(rnd.choice(chars))
            y = y0 + (i + 1) * 12
            if i == n - 1:
                fill, op = '#d9ffe4', 1
            else:
                fill, op = '#22c55e', round(0.15 + 0.7 * i / n, 2)
            out.append('<text x="%d" y="%d" fill="%s" fill-opacity="%s">%s</text>' % (cx, y, fill, op, ch))
    out.append('</g></svg>')
    return uri(''.join(out))

MASK = uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 150"><defs><radialGradient id="f" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d9d9d2"/></radialGradient></defs><path d="M70 4C34 4 18 36 20 70C22 100 10 128 0 150H140C130 128 118 100 120 70C122 36 106 4 70 4Z" fill="#070b08" stroke="#1c2b21" stroke-width="2"/><ellipse cx="70" cy="68" rx="41" ry="52" fill="#020403"/><g transform="translate(25 14) scale(.9)"><path d="M50 4C20 4 10 30 12 58C14 86 30 112 50 116C70 112 86 86 88 58C90 30 80 4 50 4Z" fill="url(#f)" stroke="#bdbdb4" stroke-width="1.5"/><circle cx="27" cy="64" r="9" fill="#f08a8a" fill-opacity=".7"/><circle cx="73" cy="64" r="9" fill="#f08a8a" fill-opacity=".7"/><path d="M19 37Q31 24 45 34M81 37Q69 24 55 34" fill="none" stroke="#111" stroke-width="2.8" stroke-linecap="round"/><path d="M22 45Q32 38 43 46Q32 51 22 45ZM78 45Q68 38 57 46Q68 51 78 45Z" fill="#111"/><circle cx="32" cy="45" r="1.6" fill="#4ade80"/><circle cx="68" cy="45" r="1.6" fill="#4ade80"/><path d="M24 53Q32 56 41 53M76 53Q68 56 59 53" fill="none" stroke="#9a9a92" stroke-width="1.2" stroke-linecap="round"/><path d="M50 50L47 70Q50 73 53 70" fill="none" stroke="#b5b5ac" stroke-width="1.4" stroke-linecap="round"/><path d="M25 76Q31 86 44 82Q50 80 56 82Q69 86 75 76Q67 91 50 88Q33 91 25 76Z" fill="#111"/><path d="M35 95Q50 106 65 95" fill="none" stroke="#111" stroke-width="2.4" stroke-linecap="round"/><path d="M50 102V111" stroke="#111" stroke-width="3" stroke-linecap="round"/></g></svg>''')

def S(c, p=''):
    return 'html body .pf-banner.pfb-%s%s,html body .pfs.pfb-%s%s' % (c, p, c, p)

R = []
def add(c, p, decl):
    R.append(S(c, p) + '{' + decl + '}')

def dot(x, y, a='#fff7a8', b='rgba(253,224,71,.45)'):
    return 'radial-gradient(circle at %s%% %s%%,%s 1.5px,%s 3.5px,transparent 7px)' % (x, y, a, b)
def star(x, y, r):
    return 'radial-gradient(%spx %spx at %s%% %s%%,#fff,transparent)' % (r, r, x, y)
def ring(x, y):
    return 'radial-gradient(circle at %s%% %s%%,transparent 3px,rgba(255,255,255,.75) 3.5px,rgba(255,255,255,.15) 6px,transparent 6.5px)' % (x, y)
def bigring(x, y):
    return 'radial-gradient(circle at %s%% %s%%,transparent 7px,rgba(255,255,255,.7) 7.5px,rgba(255,255,255,.12) 12px,transparent 12.5px)' % (x, y)
def ember(x, y):
    return 'radial-gradient(circle at %s%% %s%%,#fff3b0 1px,#ffb347 2.5px,transparent 4.5px)' % (x, y)

SHIFT = lambda sec: 'background-size:300%% 300%%;animation:fxShift %ss ease infinite' % sec
WIDE = 'top:0;left:0;width:200%;height:100%;'
SHEEN = lambda a: 'inset:0;background:linear-gradient(105deg,transparent 40%%,rgba(255,255,255,%s) 50%%,transparent 60%%) 160%% 0/250%% 100%% no-repeat;animation:fxSheen 5s ease-in-out infinite' % a

# Senja
add('sunset', '', SHIFT(9))
add('sunset', '::before', 'left:50%;bottom:-42%;width:62%;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,rgba(255,238,160,.9),rgba(255,160,60,.35) 45%,transparent 70%);transform:translateX(-50%);animation:fxSun 5s ease-in-out infinite alternate')
add('sunset', '::after', SHEEN('.3'))
# Laut
add('ocean', '', SHIFT(10))
add('ocean', '::before', 'left:0;bottom:0;width:200%;height:46%;background:%WAVEB% 0 100%/25% 100% repeat-x;animation:fxWave 8s linear infinite')
add('ocean', '::after', 'left:0;bottom:0;width:200%;height:34%;background:%WAVEF% 0 100%/25% 100% repeat-x;animation:fxWave 5s linear infinite')
# Hutan
add('forest', '', SHIFT(11))
add('forest', '::before', WIDE + 'background:' + ','.join([dot(12, 30), dot(42, 72), dot(70, 22), dot(90, 60)]) + ';background-size:25% 100%;animation:fxDrift 16s linear infinite')
add('forest', '::after', WIDE + 'background:' + ','.join([dot(25, 55, '#e8ffb0', 'rgba(163,230,53,.45)'), dot(58, 35, '#e8ffb0', 'rgba(163,230,53,.45)'), dot(80, 82, '#e8ffb0', 'rgba(163,230,53,.45)')]) + ';background-size:25% 100%;animation:fxDriftR 24s linear infinite,fxBlink 2.6s ease-in-out infinite alternate')
# Permen
add('candy', '', SHIFT(9))
add('candy', '::before', 'top:0;left:0;width:100%;height:200%;background:' + ','.join([ring(14, 20), ring(46, 62), ring(78, 36), ring(92, 84)]) + ';background-size:100% 25%;animation:fxRise 9s linear infinite')
add('candy', '::after', 'top:0;left:0;width:100%;height:200%;background:' + ','.join([bigring(30, 45), bigring(72, 78)]) + ';background-size:100% 50%;animation:fxRise 14s linear infinite')
# Mono
add('mono', '', SHIFT(12))
add('mono', '::before', 'inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.08) 0,rgba(255,255,255,.08) 1px,transparent 1px,transparent 3px);animation:fxBreath 3s ease-in-out infinite alternate')
add('mono', '::after', 'left:0;right:0;top:0;height:35%;background:linear-gradient(transparent,rgba(255,255,255,.22),transparent);transform:translateY(-110%);animation:fxRoll 4s linear infinite')
# Peach
add('peach', '', SHIFT(9))
add('peach', '::before', WIDE + 'background:radial-gradient(circle at 22% 40%,rgba(255,255,255,.5),transparent 20%),radial-gradient(circle at 72% 62%,rgba(255,255,255,.35),transparent 18%);background-size:25% 100%;animation:fxDrift 18s linear infinite')
add('peach', '::after', SHEEN('.5'))
# Malam
add('night', '', SHIFT(14))
add('night', '::before', 'inset:0;background:' + ','.join([star(8, 24, 1.3), star(22, 70, 1.1), star(38, 18, 1.5), star(55, 55, 1.2), star(70, 28, 1.4), star(84, 72, 1.1), star(94, 20, 1.3)]) + ';animation:fxTwk 2.6s ease-in-out infinite alternate')
add('night', '::after', 'top:14%;left:96%;width:30%;height:2px;border-radius:2px;background:linear-gradient(90deg,#fff,transparent);transform:rotate(-18deg);opacity:0;animation:fxShoot 6s linear infinite')
# Lilac
add('lilac', '', SHIFT(10))
add('lilac', '::before', WIDE + 'background:radial-gradient(circle at 25% 40%,rgba(255,255,255,.5),transparent 18%),radial-gradient(circle at 75% 65%,rgba(251,207,232,.6),transparent 22%);background-size:25% 100%;animation:fxDrift 18s linear infinite')
add('lilac', '::after', 'inset:0;background:' + ','.join([star(15, 30, 1.4), star(34, 75, 1.2), star(52, 22, 1.5), star(68, 60, 1.3), star(86, 35, 1.4), star(92, 80, 1.2)]) + ';animation:fxTwk 2s ease-in-out infinite alternate')
# Aurora
add('aurora', '::before', WIDE + 'background:linear-gradient(100deg,transparent 15%,rgba(255,255,255,.2) 45%,transparent 75%);background-size:25% 100%;animation:fxDrift 10s linear infinite')
add('aurora', '::after', 'inset:0;background:radial-gradient(ellipse at 50% 120%,rgba(255,255,255,.3),transparent 60%);animation:fxBreath 3s ease-in-out infinite alternate')
# Lava
add('lava', '::before', 'top:0;left:0;width:100%;height:200%;background:' + ','.join([ember(15, 35), ember(40, 80), ember(66, 20), ember(88, 60)]) + ';background-size:100% 25%;animation:fxRise 5s linear infinite')
add('lava', '::after', 'left:0;right:0;bottom:0;height:50%;background:linear-gradient(0deg,rgba(255,200,40,.45),transparent);animation:fxBreath 2.2s ease-in-out infinite alternate')
# Holo
add('holo', '::before', SHEEN('.55').replace('5s', '3.5s'))
add('holo', '::after', 'inset:0;background:' + ','.join([star(14, 28, 1.6), star(36, 72, 1.5), star(58, 24, 1.7), star(76, 62, 1.5), star(92, 30, 1.6)]) + ';animation:fxTwk 1.8s ease-in-out infinite alternate')
# Galaksi
add('galaksi', '::before', WIDE + 'background:radial-gradient(circle at 30% 50%,rgba(168,85,247,.35),transparent 28%),radial-gradient(circle at 75% 40%,rgba(236,72,153,.28),transparent 26%);background-size:25% 100%;animation:fxDrift 22s linear infinite')
# Hacker
add('hacker', '', 'background-image:repeating-linear-gradient(0deg,rgba(0,255,100,.05) 0,rgba(0,255,100,.05) 1px,transparent 1px,transparent 3px),radial-gradient(ellipse at 64% 50%,#0b2d17 0%,#020a05 72%)')
add('hacker', '::before', 'top:-160px;bottom:-160px;left:0;right:0;background:%RAIN% 0 0/160px 160px repeat;opacity:.85;animation:fxMx 5s linear infinite')
add('hacker', '::after', 'inset:0;background:%MASK% 64% 50%/auto 96% no-repeat;filter:drop-shadow(0 0 8px rgba(34,197,94,.55));animation:fxGlitch 5s steps(1,end) infinite')

KEYS = '''
@keyframes fxShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes fxDrift{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes fxDriftR{from{transform:translateX(-50%)}to{transform:translateX(0)}}
@keyframes fxRise{from{transform:translateY(0)}to{transform:translateY(-50%)}}
@keyframes fxWave{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes fxSheen{0%{background-position:160% 0}60%,100%{background-position:-60% 0}}
@keyframes fxTwk{from{opacity:.25}to{opacity:1}}
@keyframes fxBlink{from{opacity:.35}to{opacity:1}}
@keyframes fxBreath{from{opacity:.45}to{opacity:1}}
@keyframes fxSun{from{transform:translateX(-50%) translateY(8%) scale(.95);opacity:.8}to{transform:translateX(-50%) translateY(-8%) scale(1.08);opacity:1}}
@keyframes fxRoll{from{transform:translateY(-110%)}to{transform:translateY(300%)}}
@keyframes fxShoot{0%{opacity:0;transform:translate(0,0) rotate(-18deg)}4%{opacity:1}16%{opacity:0;transform:translate(-360%,120%) rotate(-18deg)}100%{opacity:0;transform:translate(-360%,120%) rotate(-18deg)}}
@keyframes fxMx{from{transform:translateY(0)}to{transform:translateY(160px)}}
@keyframes fxGlitch{0%,88%,100%{transform:none;filter:drop-shadow(0 0 8px rgba(34,197,94,.55))}90%{transform:translate(2px,-1px)}92%{transform:translate(-3px,1px);filter:drop-shadow(-3px 0 #f0f) drop-shadow(3px 0 #0ff)}94%{transform:translate(1px,0)}96%{transform:none}}
'''
GEN = 'html body :is(.pf-banner,.pfs)[class*="pfb-"]::before,html body :is(.pf-banner,.pfs)[class*="pfb-"]::after{content:"";position:absolute;pointer-events:none}\n'
RM = '@media(prefers-reduced-motion:reduce){html body :is(.pf-banner,.pfs)[class*="pfb-"],html body :is(.pf-banner,.pfs)[class*="pfb-"]::before,html body :is(.pf-banner,.pfs)[class*="pfb-"]::after{animation:none!important}}\n'

CSS = KEYS + GEN + '\n'.join(R) + '\n' + RM
CSS = CSS.replace('%WAVEB%', wave('.18')).replace('%WAVEF%', wave('.32')).replace('%RAIN%', rain()).replace('%MASK%', MASK)

shutil.copy(f, f + '.bak37')
s = s[:m.start()] + HOLO + ", {id:'hacker', n:'Hacker', owner:true}" + s[m.end():]
s = s.replace('</head>', '<style id="mz-fx">\n' + CSS + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Efek semua banner : OK')
print('Banner Hacker     : OK')
