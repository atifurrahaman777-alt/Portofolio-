import glob, re, shutil

try:
    from PIL import Image, ImageDraw
except ImportError:
    print('Pillow belum terpasang. Jalankan dulu: pkg install python-pillow -y')
    raise SystemExit

POLY = [(8,54),(8,10),(21,10),(32,32),(43,10),(56,10),(56,54),(46,54),(46,27),(34,47),(30,47),(18,27),(18,54)]
TOP, MID, BOT = (255,228,77), (255,138,0), (225,29,29)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make(size):
    S = 1024
    k = S / 64.0
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=(10, 10, 10, 255))
    d.rounded_rectangle([int(S*.02), int(S*.02), S - int(S*.02) - 1, S - int(S*.02) - 1],
                        radius=int(S * 0.2), outline=(255, 138, 0, 255), width=int(S * 0.03))
    for (x1, y1, x2, y2) in [(46, 6, 22, 58), (56, 14, 34, 58)]:
        d.line([(x1*k, y1*k), (x2*k, y2*k)], fill=(239, 68, 68, 150), width=int(3.2*k))
    grad = Image.new('RGBA', (S, S))
    gp = grad.load()
    y0, y1 = int(8*k), int(56*k)
    for y in range(S):
        t = min(max((y - y0) / float(y1 - y0), 0), 1)
        c = mix(TOP, MID, t / 0.5) if t < 0.5 else mix(MID, BOT, (t - 0.5) / 0.5)
        for x in range(S):
            gp[x, y] = c + (255,)
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).polygon([(x*k, y*k) for x, y in POLY], fill=255)
    outline = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(outline).polygon([(x*k, y*k) for x, y in POLY], outline=(0, 0, 0, 255), width=int(1.6*k))
    img.alpha_composite(outline)
    img.paste(grad, (0, 0), mask)
    return img.resize((size, size), Image.LANCZOS)

make(256).save('tab-icon.png')
print('tab-icon.png : OK')

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe44d"/><stop offset=".5" stop-color="#ff8a00"/><stop offset="1" stop-color="#e11d1d"/></linearGradient></defs>
<rect width="64" height="64" rx="14" fill="#0a0a0a"/>
<rect x="1.3" y="1.3" width="61.4" height="61.4" rx="12.8" fill="none" stroke="#ff8a00" stroke-width="1.9"/>
<path d="M46 6L22 58M56 14L34 58" stroke="#ef4444" stroke-opacity=".6" stroke-width="3.2" stroke-linecap="round"/>
<polygon points="8,54 8,10 21,10 32,32 43,10 56,10 56,54 46,54 46,27 34,47 30,47 18,27 18,54" fill="url(#g)" stroke="#000" stroke-width="1.6" stroke-linejoin="round"/>
</svg>"""
open('tab-icon.svg', 'w', encoding='utf-8').write(SVG)
print('tab-icon.svg : OK')

LINKS = '<link rel="icon" type="image/svg+xml" href="tab-icon.svg?v=2"><link rel="icon" type="image/png" href="tab-icon.png?v=2">'
done = 0
for f in sorted(glob.glob('*.html')):
    s = open(f, encoding='utf-8').read()
    if 'tab-icon' in s:
        continue
    if re.search(r'<link rel="icon"[^>]*>', s):
        s2 = re.sub(r'<link rel="icon"[^>]*>', lambda m: LINKS, s, count=1)
    elif '</head>' in s:
        s2 = s.replace('</head>', LINKS + '\n</head>', 1)
    else:
        continue
    shutil.copy(f, f + '.bak30')
    open(f, 'w', encoding='utf-8').write(s2)
    done += 1
    print(f, ': OK')
print('Halaman diperbarui :', done)
