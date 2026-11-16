import shutil

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'mz-border7' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit
if 'id="mz-border6"' not in s:
    print('GAGAL: bingkai baru (fix23) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

CSS = r"""
@keyframes mzXGlow{0%,100%{filter:drop-shadow(0 0 0 transparent)}50%{filter:drop-shadow(0 0 5px var(--bc,currentColor))}}
@keyframes mzXFlick{from{filter:drop-shadow(0 0 0 transparent)}to{filter:drop-shadow(0 0 7px #ef4444)}}
@keyframes mzXDouble{
 0%{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) var(--text),0 0 0 calc(var(--r,3px)*3) var(--bg),0 0 0 calc(var(--r,3px)*4) var(--text)}
 100%{box-shadow:0 0 0 var(--r,3px) var(--bg),0 0 0 calc(var(--r,3px)*2) var(--text),0 0 0 calc(var(--r,3px)*4) var(--bg),0 0 0 calc(var(--r,3px)*5) var(--text)}}
@keyframes mzXTurn{to{transform:rotate(360deg)}}
@keyframes mzXSpin{to{rotate:360deg}}
@keyframes mzXEarL{0%,70%,100%{rotate:0deg}80%{rotate:-14deg}90%{rotate:4deg}}
@keyframes mzXEarR{0%,70%,100%{rotate:0deg}80%{rotate:14deg}90%{rotate:-4deg}}
@keyframes mzXHorn{from{scale:1}to{scale:1.18}}
@keyframes mzXHalo{from{translate:0 0;opacity:.85}to{translate:0 -14%;opacity:1}}
@keyframes mzXTwk{0%,100%{scale:1;opacity:1}50%{scale:1.3;opacity:.65}}
@keyframes mzXBeat2{0%,100%{scale:1}15%{scale:1.3}30%{scale:1}45%{scale:1.2}}
@keyframes mzXWig{0%,100%{rotate:-6deg}50%{rotate:8deg}}
@keyframes mzXSway{0%,100%{rotate:-8deg}50%{rotate:10deg}}
@keyframes mzXHop{0%,100%{translate:0 0}50%{translate:0 -10%}}
@keyframes mzXBunL{0%,100%{rotate:0deg}50%{rotate:-9deg}}
@keyframes mzXBunR{0%,100%{rotate:0deg}50%{rotate:9deg}}
@keyframes mzXZap{0%,60%,100%{opacity:1;scale:1}65%{opacity:.25}70%{opacity:1;scale:1.25}75%{opacity:.35}80%{opacity:1;scale:1}}
@keyframes mzXBob{from{translate:0 0}to{translate:0 -8%}}
@keyframes mzXFire{0%,100%{scale:1 1}25%{scale:.9 1.1}50%{scale:1.08 .92}75%{scale:.95 1.07}}

html body :is(.bd-s-mono,.bd-s-biru,.bd-s-hijau,.bd-s-pink,.bd-s-ungu,.bd-s-oranye,.bd-a-kucing,.bd-a-halo,.bd-a-bunga,.bd-a-bintang,.bd-a-hati,.bd-a-pita,.bd-a-daun,.bd-a-topi,.bd-a-kelinci){animation:mzXGlow 2.2s ease-in-out infinite}
html body .bd-s-biru,html body .bd-a-hati{animation-duration:1.8s}
html body .bd-s-hijau,html body .bd-a-daun{animation-duration:2.6s}
html body .bd-s-pink,html body .bd-a-pita{animation-duration:2s}
html body .bd-s-ganda{animation:mzXDouble 2s ease-in-out infinite alternate}
html body .bd-s-putus{box-shadow:none!important;outline:none!important;position:relative}
html body .bd-s-putus::after{content:"";position:absolute;inset:calc(var(--r,3px)*-2);border:var(--r,3px) dashed var(--text);border-radius:50%;pointer-events:none;animation:mzXTurn 7s linear infinite}
html body .bd-o-senja{background:linear-gradient(var(--accent),var(--accent)) padding-box,conic-gradient(from var(--ang),#f97316,#ec4899,#8b5cf6,#f97316) border-box!important;animation:mzSpin 5s linear infinite}
html body .bd-a-kucing::before{transform-origin:50% 100%;animation:mzXEarL 2.4s ease-in-out infinite}
html body .bd-a-kucing::after{transform-origin:50% 100%;animation:mzXEarR 2.4s ease-in-out .3s infinite}
html body .bd-a-tanduk{animation:mzXFlick 1.2s ease-in-out infinite alternate}
html body .bd-a-tanduk::before,html body .bd-a-tanduk::after{transform-origin:50% 100%;animation:mzXHorn 1.2s ease-in-out infinite alternate}
html body .bd-a-halo::before{animation:mzXHalo 2s ease-in-out infinite alternate}
html body .bd-a-bunga::before{animation:mzXSpin 6s linear infinite}
html body .bd-a-bintang::before{animation:mzXTwk 1.4s ease-in-out infinite}
html body .bd-a-bintang::after{animation:mzXTwk 1.4s ease-in-out .7s infinite}
html body .bd-a-hati::before{animation:mzXBeat2 1.5s ease-in-out infinite}
html body .bd-a-pita::before{animation:mzXWig 1.3s ease-in-out infinite}
html body .bd-a-daun::before{transform-origin:0% 100%;animation:mzXSway 2.2s ease-in-out infinite}
html body .bd-a-topi::before{animation:mzXHop 1s ease-in-out infinite}
html body .bd-a-kelinci::before{transform-origin:50% 100%;animation:mzXBunL 1.8s ease-in-out infinite}
html body .bd-a-kelinci::after{transform-origin:50% 100%;animation:mzXBunR 1.8s ease-in-out .25s infinite}
html body .bd-a-kilat::before,html body .bd-a-kilat::after{animation:mzXZap 1.6s ease-in-out infinite}
html body .bd-a-kilat::after{animation-delay:.5s}
html body .bd-a-mahkota::before{animation:mzXBob 1.6s ease-in-out infinite alternate}
html body .bd-a-api::before{transform-origin:50% 100%;animation:mzXFire .9s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){html body [class*="bd-s-"],html body [class*="bd-s-"]::after,html body [class*="bd-a-"],html body [class*="bd-a-"]::before,html body [class*="bd-a-"]::after{animation:none!important}}
"""

shutil.copy(f, f + '.bak24')
s = s.replace('</head>', '<style id="mz-border7">' + CSS + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Animasi bingkai : OK')
