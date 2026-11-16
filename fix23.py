import shutil
from urllib.parse import quote

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border6' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

A = "{id:'pita', n:'Pita', cls:'bd-a-pita'},"
B = "{id:'kilat', n:'Kilat', cls:'bd-a-kilat', owner:true}"
if 'id="mz-border-js"' not in s or A not in s or B not in s:
    print('GAGAL: skrip bingkai sebelumnya (fix19) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

def uri(inner):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">' + inner + '</svg>'
    return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

SNOW = uri('<g stroke="#38bdf8" stroke-width="2" stroke-linecap="round" fill="none"><path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7"/><path d="M9 4l3 2 3-2M9 20l3-2 3 2"/></g>')
LEAF = uri('<path fill="#22c55e" stroke="#15803d" stroke-width="1" stroke-linejoin="round" d="M4 20C4 9 10 3 21 3c0 11-6 17-17 17z"/><path d="M4 20L15 9" stroke="#15803d" stroke-width="1.2" fill="none"/>')
CLOUD = uri('<path fill="#fff" stroke="#93c5fd" stroke-width="1.2" stroke-linejoin="round" d="M7 18a4 4 0 0 1-.6-7.96A5.5 5.5 0 0 1 17 9.5 4.3 4.3 0 0 1 17.5 18z"/>')
HAT = uri('<path fill="#a855f7" stroke="#6b21a8" stroke-width="1" stroke-linejoin="round" d="M12 2l8 20H4z"/><path d="M8.5 13h7M6.8 18h10.4" stroke="#fde047" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="2.5" r="2" fill="#fde047"/>')
GEM = uri('<path fill="#67e8f9" stroke="#0e7490" stroke-width="1" stroke-linejoin="round" d="M6 3h12l4 6-10 13L2 9z"/><path d="M2 9h20M9 3l-2 6 5 13M15 3l2 6-5 13" fill="none" stroke="#0e7490" stroke-width=".8"/>')
WING = uri('<g fill="#fff" stroke="#cbd5e1" stroke-width=".8"><ellipse cx="14" cy="7" rx="9" ry="3.2" transform="rotate(-25 14 7)"/><ellipse cx="14" cy="12.5" rx="9.5" ry="3.2" transform="rotate(-5 14 12.5)"/><ellipse cx="14" cy="18" rx="8.5" ry="3" transform="rotate(15 14 18)"/></g>')

def acc(sel, img, w, h, p):
    return ('html body ' + sel + '{content:"";position:absolute;z-index:2;pointer-events:none;'
            'background:' + img + ' center/contain no-repeat;'
            'width:calc(var(--sz,40px)*' + w + ');height:calc(var(--sz,40px)*' + h + ');' + p + '}\n')

CSS = r"""
html body :is(.bd-o-senja,.bd-o-aurora,.bd-o-galaksi,.bd-o-holo,.bd-o-lava,.bd-o-listrik){border:var(--r2,3px) solid transparent!important}
html body .bd-o-senja{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(#f97316,#ec4899,#8b5cf6,#f97316) border-box!important}
html body .bd-o-aurora{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#22c55e,#06b6d4,#8b5cf6,#22c55e) border-box!important;animation:mzSpin 6s linear infinite}
html body .bd-o-galaksi{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#1e1b4b,#7c3aed,#ec4899,#22d3ee,#1e1b4b) border-box!important;box-shadow:0 0 8px 1px rgba(124,58,237,.5);animation:mzSpin 4s linear infinite,mzGlowV 2s ease-in-out infinite alternate}
html body .bd-o-holo{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#f0abfc,#67e8f9,#fde68a,#86efac,#f0abfc) border-box!important;animation:mzSpin 2.5s linear infinite}
html body .bd-o-lava{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#7f1d1d,#ef4444,#f97316,#fde047,#f97316,#7f1d1d) border-box!important;box-shadow:0 0 8px 1px rgba(249,115,22,.5);animation:mzSpin 3s linear infinite,mzFlick .8s ease-in-out infinite alternate}
html body .bd-o-listrik{border-color:#22d3ee!important;animation:mzElec .9s steps(1) infinite}
html body .bd-a-denyut{--bc:#ef4444;animation:mzBeat 1.2s ease-out infinite}
html body .bd-a-salju{--bc:#7dd3fc;box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #7dd3fc,0 0 12px 2px rgba(125,211,252,.6)}
html body .bd-a-daun{--bc:#22c55e}
html body .bd-a-awan{--bc:#93c5fd}
html body .bd-a-topi{--bc:#a855f7}
html body .bd-a-kelinci{--bc:#f9a8d4}
html body .bd-a-kelinci::before,html body .bd-a-kelinci::after{content:"";position:absolute;top:-46%;width:22%;height:56%;background:#fff;border:2px solid #f9a8d4;border-radius:50% 50% 45% 45%;z-index:-1}
html body .bd-a-kelinci::before{left:22%;transform:rotate(-10deg)}
html body .bd-a-kelinci::after{right:22%;transform:rotate(10deg)}
html body .bd-a-sayap{--bc:#facc15;box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #facc15,0 0 12px 2px rgba(250,204,21,.55)}
html body .bd-a-berlian{--bc:#22d3ee;box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #22d3ee,0 0 12px 2px rgba(34,211,238,.55)}
html body .bd-a-salju::before{animation:mzTurn 6s linear infinite}
html body .bd-a-awan::before{animation:mzFloat 2.4s ease-in-out infinite alternate}
html body .bd-a-berlian::before{animation:mzTwinkle 1.4s ease-in-out infinite}
html body .bd-a-sayap::before{animation:mzFlapL 1.1s ease-in-out infinite}
html body .bd-a-sayap::after{animation:mzFlapR 1.1s ease-in-out infinite}
@keyframes mzGlowV{to{box-shadow:0 0 16px 4px rgba(236,72,153,.6)}}
@keyframes mzFlick{to{box-shadow:0 0 16px 4px rgba(239,68,68,.65)}}
@keyframes mzElec{0%{box-shadow:0 0 6px #22d3ee}20%{box-shadow:0 0 14px 4px #fff}40%{box-shadow:0 0 4px #22d3ee}60%{box-shadow:0 0 16px 5px #a5f3fc}80%{box-shadow:0 0 8px #22d3ee}}
@keyframes mzBeat{0%{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #ef4444,0 0 0 calc(var(--r,3px)*2) rgba(239,68,68,.55)}100%{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) #ef4444,0 0 0 calc(var(--r,3px)*2 + 10px) rgba(239,68,68,0)}}
@keyframes mzTurn{to{transform:rotate(360deg)}}
@keyframes mzFloat{from{transform:translateY(0)}to{transform:translateY(-12%)}}
@keyframes mzTwinkle{0%,100%{opacity:1;transform:translateX(-50%) scale(1)}50%{opacity:.65;transform:translateX(-50%) scale(1.18)}}
@keyframes mzFlapL{0%,100%{transform:scaleX(-1) rotate(-8deg)}50%{transform:scaleX(-1) rotate(10deg)}}
@keyframes mzFlapR{0%,100%{transform:rotate(-8deg)}50%{transform:rotate(10deg)}}
@media(prefers-reduced-motion:reduce){html body [class*="bd-a-"]::before,html body [class*="bd-a-"]::after,html body [class*="bd-o-"]{animation:none!important}}
"""
CSS += acc('.bd-a-salju::before', SNOW, '.5', '.5', 'top:-20%;right:-20%;')
CSS += acc('.bd-a-daun::before', LEAF, '.5', '.5', 'top:-20%;right:-18%;transform:rotate(15deg);')
CSS += acc('.bd-a-awan::before', CLOUD, '.62', '.5', 'top:-26%;left:-20%;')
CSS += acc('.bd-a-topi::before', HAT, '.5', '.6', 'top:-42%;left:50%;transform:translateX(-30%) rotate(18deg);')
CSS += acc('.bd-a-berlian::before', GEM, '.5', '.5', 'top:-42%;left:50%;transform:translateX(-50%);')
CSS += acc('.bd-a-sayap::before', WING, '.7', '.7', 'left:-64%;top:6%;z-index:-1;transform:scaleX(-1);')
CSS += acc('.bd-a-sayap::after', WING, '.7', '.7', 'right:-64%;top:6%;z-index:-1;')

MEMBER = ("\n    {id:'denyut', n:'Denyut', cls:'bd-a-denyut'},"
          "\n    {id:'senja', n:'Senja', cls:'bd-o-senja'},"
          "\n    {id:'aurora', n:'Aurora', cls:'bd-o-aurora'},"
          "\n    {id:'salju', n:'Salju', cls:'bd-a-salju'},"
          "\n    {id:'daun', n:'Daun', cls:'bd-a-daun'},"
          "\n    {id:'awan', n:'Awan', cls:'bd-a-awan'},"
          "\n    {id:'topi', n:'Topi', cls:'bd-a-topi'},"
          "\n    {id:'kelinci', n:'Kelinci', cls:'bd-a-kelinci'},")
OWNER = (",\n    {id:'galaksi', n:'Galaksi', cls:'bd-o-galaksi', owner:true},"
         "\n    {id:'holo', n:'Holo', cls:'bd-o-holo', owner:true},"
         "\n    {id:'lava', n:'Lava', cls:'bd-o-lava', owner:true},"
         "\n    {id:'listrik', n:'Listrik', cls:'bd-o-listrik', owner:true},"
         "\n    {id:'sayap', n:'Sayap', cls:'bd-a-sayap', owner:true},"
         "\n    {id:'berlian', n:'Berlian', cls:'bd-a-berlian', owner:true}")

shutil.copy(f, f + '.bak23')
s = s.replace(A, A + MEMBER, 1)
s = s.replace(B, B + OWNER, 1)
s = s.replace('</head>', '<style id="mz-border6">' + CSS + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Bingkai baru : OK (14 bingkai)')
