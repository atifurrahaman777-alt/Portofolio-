import glob, re, shutil

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print('Pillow belum terpasang (pakai python3, bukan python).')
    raise SystemExit

POLY = [(4,58),(8,6),(24,26),(32,16),(40,26),(56,6),(60,58),(49,58),(47,30),(36,44),(28,44),(17,30),(15,58)]
TOP, MID, BOT = (255, 255, 255), (200, 205, 215), (84, 88, 100)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make(out):
    S = 512
    k = S / 64.0
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.2), fill=(8, 8, 8, 255))

    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).polygon([(x * k, y * k) for x, y in POLY], fill=255)
    big = mask.filter(ImageFilter.MaxFilter(25))
    red = Image.new('RGBA', (S, S), (225, 29, 29, 255))
    img.paste(red, (0, 0), big)

    grad = Image.new('RGBA', (S, S))
    gd = ImageDraw.Draw(grad)
    y0, y1 = int(6 * k), int(58 * k)
    for y in range(S):
        t = min(max((y - y0) / float(y1 - y0), 0), 1)
        c = mix(TOP, MID, t / 0.45) if t < 0.45 else mix(MID, BOT, (t - 0.45) / 0.55)
        gd.line([(0, y), (S, y)], fill=c + (255,))
    img.paste(grad, (0, 0), mask)
    img.resize((out, out), Image.LANCZOS).save('tab-icon.png')

make(256)
print('tab-icon.png : OK')

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".45" stop-color="#c8cdd7"/><stop offset="1" stop-color="#545864"/></linearGradient></defs>
<rect width="64" height="64" rx="13" fill="#080808"/>
<polygon points="4,58 8,6 24,26 32,16 40,26 56,6 60,58 49,58 47,30 36,44 28,44 17,30 15,58" fill="#e11d1d" stroke="#e11d1d" stroke-width="5" stroke-linejoin="miter"/>
<polygon points="4,58 8,6 24,26 32,16 40,26 56,6 60,58 49,58 47,30 36,44 28,44 17,30 15,58" fill="url(#g)"/>
</svg>"""
open('tab-icon.svg', 'w', encoding='utf-8').write(SVG)
print('tab-icon.svg : OK')

n = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'tab-icon\.(svg|png)\?v=\d+', lambda m: 'tab-icon.' + m.group(1) + '?v=3', s)
    if s2 != s:
        shutil.copy(f, f + '.bak31')
        open(f, 'w', encoding='utf-8').write(s2)
        n += 1
print('Halaman diperbarui :', n)
