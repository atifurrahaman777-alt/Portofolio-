import glob, json, os, re, shutil

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print('Pillow belum terpasang (pakai python3, bukan python).')
    raise SystemExit

POLY = [(4,58),(8,6),(24,26),(32,16),(40,26),(56,6),(60,58),(49,58),(47,30),(36,44),(28,44),(17,30),(15,58)]
TOP, MID, BOT = (255, 255, 255), (200, 205, 215), (84, 88, 100)

def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def render(size, maskable):
    S = 1024
    k = S / 64.0
    sc = 0.62 if maskable else 1.0
    off = (64 - 64 * sc) / 2.0
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        d.rectangle([0, 0, S, S], fill=(8, 8, 8, 255))
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.2), fill=(8, 8, 8, 255))
    pts = [((x * sc + off) * k, (y * sc + off) * k) for x, y in POLY]
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    big = mask.filter(ImageFilter.MaxFilter(25 if not maskable else 17))
    red = Image.new('RGBA', (S, S), (225, 29, 29, 255))
    img.paste(red, (0, 0), big)
    grad = Image.new('RGBA', (S, S))
    gd = ImageDraw.Draw(grad)
    y0 = int((6 * sc + off) * k)
    y1 = int((58 * sc + off) * k)
    for y in range(S):
        t = min(max((y - y0) / float(y1 - y0), 0), 1)
        c = mix(TOP, MID, t / 0.45) if t < 0.45 else mix(MID, BOT, (t - 0.45) / 0.55)
        gd.line([(0, y), (S, y)], fill=c + (255,))
    img.paste(grad, (0, 0), mask)
    return img.resize((size, size), Image.LANCZOS)

made = []
for name, size, mk in [('icon-192.png', 192, False), ('icon-512.png', 512, False), ('icon-maskable-512.png', 512, True)]:
    if os.path.exists(name):
        shutil.copy(name, name + '.bak51')
    render(size, mk).save(name)
    made.append(name)
print('Ikon dibuat:', ', '.join(made))

V = '?v=5'
if os.path.exists('manifest.json'):
    shutil.copy('manifest.json', 'manifest.json.bak51')
    m = json.load(open('manifest.json', encoding='utf-8'))
    m['icons'] = [
        {'src': '/icon-192.png' + V, 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
        {'src': '/icon-512.png' + V, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
        {'src': '/icon-maskable-512.png' + V, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ]
    json.dump(m, open('manifest.json', 'w', encoding='utf-8'), indent=2)
    print('manifest.json : OK')
else:
    print('manifest.json : tidak ada (dilewati)')

n = 0
for p in sorted(glob.glob('*.html')):
    s = open(p, encoding='utf-8', errors='surrogateescape').read()
    t = re.sub(r'(/icon-(?:192|512)\.png)(\?v=\d+)?', lambda mm: mm.group(1) + V, s)
    t = re.sub(r'(/manifest\.json)(\?v=\d+)?', lambda mm: mm.group(1) + V, t)
    if t != s:
        shutil.copy(p, p + '.bak51')
        open(p, 'w', encoding='utf-8', errors='surrogateescape').write(t)
        print('diubah:', p)
        n += 1
print('Halaman diperbarui :', n)
