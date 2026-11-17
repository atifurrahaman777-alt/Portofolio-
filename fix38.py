import re, shutil, random
from urllib.parse import quote

f = 'index.html'
s = open(f, encoding='utf-8').read()
if 'id="mz-fx"' not in s:
    print('GAGAL: banner hacker (fix37) belum terpasang. Tidak ada yang diubah.')
    raise SystemExit

def uri(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe='') + '")'

def esc(c):
    return c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def rain():
    rnd = random.Random(11)
    chars = list('01$#<>/{}=+*;:%&?')
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160"><g font-family="monospace" font-size="11" font-weight="700">']
    for cx in range(8, 160, 14):
        n = rnd.randint(5, 9)
        y0 = rnd.randint(6, 160 - n * 12 - 6)
        for i in range(n):
            ch = esc(rnd.choice(chars))
            y = y0 + (i + 1) * 12
            if i == n - 1:
                fill, op = '#ccfbf1', 1
            else:
                fill, op = '#2dd4bf', round(0.15 + 0.7 * i / n, 2)
            out.append('<text x="' + str(cx) + '" y="' + str(y) + '" fill="' + fill + '" fill-opacity="' + str(op) + '">' + ch + '</text>')
    out.append('</g></svg>')
    return uri(''.join(out))

FIG = uri('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220">
<defs>
<linearGradient id="m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b9f1e8"/></linearGradient>
<linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14414f"/><stop offset="1" stop-color="#07191f"/></linearGradient>
<radialGradient id="l" cx=".3" cy=".3" r=".9"><stop offset="0" stop-color="#7ffcf0"/><stop offset=".5" stop-color="#0f766e"/><stop offset="1" stop-color="#03181a"/></radialGradient>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#a7e8de"/></linearGradient>
</defs>
<path d="M0 220L6 176Q28 152 66 142L100 196L134 142Q172 152 194 176L200 220Z" fill="url(#c)" stroke="#5eead4" stroke-width="1.4" stroke-linejoin="round"/>
<path d="M84 128L116 128L118 150L100 160L82 150Z" fill="#06151b"/>
<path d="M84 148L100 198L116 148Z" fill="#bfeee8" fill-opacity=".85"/>
<path d="M94 160L106 160L110 206L100 216L90 206Z" fill="#06151b" stroke="#5eead4" stroke-width="1"/>
<path d="M66 142L100 196L82 206L48 164Z" fill="#0f3441" stroke="#5eead4" stroke-width="1" stroke-linejoin="round"/>
<path d="M134 142L100 196L118 206L152 164Z" fill="#0f3441" stroke="#5eead4" stroke-width="1" stroke-linejoin="round"/>
<path d="M66 74C66 58 80 52 100 52C120 52 134 58 134 74C136 98 126 124 100 140C74 124 64 98 66 74Z" fill="url(#m)" stroke="#5eead4" stroke-width="1.2"/>
<ellipse cx="100" cy="77" rx="34" ry="5" fill="#000" fill-opacity=".25"/>
<circle cx="76" cy="106" r="6" fill="#f87171" fill-opacity=".3"/>
<circle cx="124" cy="106" r="6" fill="#f87171" fill-opacity=".3"/>
<path d="M100 92L96 104Q100 107 104 104" fill="none" stroke="#8fb8b3" stroke-width="1.3" stroke-linecap="round"/>
<path d="M78 108Q89 101 100 107Q111 101 122 108Q112 116 100 112Q88 116 78 108Z" fill="#06151b"/>
<path d="M74 108Q76 120 90 124M126 108Q124 120 110 124" fill="none" stroke="#06151b" stroke-width="1.8" stroke-linecap="round"/>
<rect x="67" y="77" width="30" height="17" rx="7" fill="url(#l)" stroke="#99f6e4" stroke-width="1.8"/>
<rect x="103" y="77" width="30" height="17" rx="7" fill="url(#l)" stroke="#99f6e4" stroke-width="1.8"/>
<path d="M97 82H103M67 82L62 80M133 82L138 80" stroke="#99f6e4" stroke-width="2" stroke-linecap="round"/>
<path d="M72 81H80M108 81H116" stroke="#ffffff" stroke-opacity=".85" stroke-width="1.6" stroke-linecap="round"/>
<path d="M72 87H92M72 90H88M108 87H128M108 90H124" stroke="#5eead4" stroke-opacity=".5" stroke-width=".8"/>
<path d="M62 56C60 30 72 8 90 8L100 18L110 8C128 8 140 30 138 56Z" fill="url(#c)" stroke="#5eead4" stroke-width="1.4" stroke-linejoin="round"/>
<path d="M74 16V40M82 12V40M90 14V40M110 14V40M118 12V40M126 18V40" stroke="#5eead4" stroke-opacity=".45" stroke-width="1"/>
<path d="M61.5 44H138.5L138 56H62Z" fill="#06151b" stroke="#5eead4" stroke-width="1"/>
<path d="M28 60C28 50 60 46 100 46C140 46 172 50 172 60C172 70 140 74 100 74C60 74 28 70 28 60Z" fill="#0a2430" stroke="#5eead4" stroke-width="1.4"/>
<path d="M76 190L126 190L136 220L66 220Z" fill="url(#c)" stroke="#5eead4" stroke-width="1.2" stroke-linejoin="round"/>
<path d="M78 190H124" stroke="#d6f5f1" stroke-width="5" stroke-linecap="round"/>
<rect x="94.5" y="102" width="11" height="58" rx="5.5" fill="url(#g)" stroke="#06151b" stroke-width="1.5"/>
<path d="M97.5 109Q100 106 102.5 109" fill="none" stroke="#6bb8ae" stroke-width="1" stroke-linecap="round"/>
<path d="M96 126H104M96 142H104" stroke="#6bb8ae" stroke-width="1.1" stroke-linecap="round"/>
<path d="M78 170C78 156 88 150 100 152C112 150 122 156 122 170L123 182C123 190 112 194 100 194C88 194 77 190 77 182Z" fill="url(#g)" stroke="#06151b" stroke-width="1.5" stroke-linejoin="round"/>
<path d="M80 160Q100 164 120 160M79 169Q100 173 121 169M79 178Q100 182 121 178" fill="none" stroke="#6bb8ae" stroke-width="1.2" stroke-linecap="round"/>
<path d="M80 168C70 166 66 176 72 184C78 190 88 186 90 178Z" fill="url(#g)" stroke="#06151b" stroke-width="1.4" stroke-linejoin="round"/>
</svg>''')

P = 'html body .pf-banner.pfb-hacker'
Q = 'html body .pfs.pfb-hacker'

def both(suffix, decl):
    return P + suffix + ',' + Q + suffix + '{' + decl + '}\n'

css = '''@keyframes fxHack{
0%{transform:none;filter:drop-shadow(0 0 6px rgba(45,212,191,.45))}
40%{filter:drop-shadow(0 0 14px rgba(45,212,191,.9))}
80%{transform:none;filter:drop-shadow(0 0 6px rgba(45,212,191,.45))}
90%{transform:translate(2px,-1px)}
92%{transform:translate(-3px,1px);filter:drop-shadow(-3px 0 #f0f) drop-shadow(3px 0 #0ff)}
94%{transform:translate(1px,0);filter:drop-shadow(0 0 6px rgba(45,212,191,.45))}
96%,100%{transform:none;filter:drop-shadow(0 0 6px rgba(45,212,191,.45))}
}
'''
css += both('', 'background-color:#06151c!important;background-image:repeating-linear-gradient(90deg,transparent 0,transparent 13px,rgba(94,234,212,.13) 13px,rgba(94,234,212,.13) 14px),radial-gradient(ellipse at 66% 46%,#1f6b7b 0%,#0e3946 46%,#06151c 100%)!important')
css += both('::before', 'background:RAIN 0 0/160px 160px repeat!important;opacity:.8')
css += both('::after', 'background:FIG 66% 50%/auto 98% no-repeat!important;animation:fxHack 6s linear infinite!important;filter:drop-shadow(0 0 6px rgba(45,212,191,.45))')
css = css.replace('RAIN', rain()).replace('FIG', FIG)

had = '<style id="mz-fx2">' in s
s = re.sub(r'<style id="mz-fx2">.*?</style>\n?', '', s, flags=re.S)
if not had:
    shutil.copy(f, f + '.bak38')
s = s.replace('</head>', '<style id="mz-fx2">\n' + css + '</style>\n</head>', 1)
open(f, 'w', encoding='utf-8').write(s)
print('Banner Hacker baru : OK')
