import glob, shutil

OLD = {
    'apiKey': 'AIzaSyC_iYADCUCDN1pCl3j4-jeZT3pU2XcIydU',
    'appId': '1:431533009387:web:72a9855b0bd596f37911ae',
    'authDomain': 'manz-4d272.firebaseapp.com',
    'storageBucket': 'manz-4d272.firebasestorage.app',
    'projectId': 'manz-4d272',
    'messagingSenderId': '431533009387',
}
NEW = {
    'apiKey': 'AIzaSyArfUhdOVfyIsjKjfD_9BkbixxNa6XRvsM',
    'appId': '1:178479215158:web:265819c21836b2116f5e97',
    'authDomain': 'manz-web.firebaseapp.com',
    'storageBucket': 'manz-web.firebasestorage.app',
    'projectId': 'manz-web',
    'messagingSenderId': '178479215158',
}
files = [p for p in glob.glob('*.html') + glob.glob('*.js') + glob.glob('api/*.js') if '.bak' not in p]
changed = 0
for p in sorted(files):
    s = open(p, encoding='utf-8', errors='surrogateescape').read()
    t = s
    for k in OLD:
        t = t.replace(OLD[k], NEW[k])
    if t != s:
        shutil.copy(p, p + '.bak50')
        open(p, 'w', encoding='utf-8', errors='surrogateescape').write(t)
        print('diubah:', p)
        changed += 1
print('Selesai, file diubah:', changed)

sisa = [p for p in files if any(v in open(p, encoding='utf-8', errors='surrogateescape').read() for v in OLD.values())]
print('Masih ada nilai lama di:', sisa if sisa else 'tidak ada')
