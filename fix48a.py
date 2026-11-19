import glob, shutil

MARK = '/*mz-cors*/'
CORS = r"""
/*mz-cors*/
const __mzOrig = module.exports;
if (typeof __mzOrig === 'function') {
  module.exports = async function (req, res) {
    const o = String((req.headers && req.headers.origin) || '');
    if (o === 'https://localhost' || o === 'capacitor://localhost' || o === 'http://localhost') {
      res.setHeader('Access-Control-Allow-Origin', o);
      res.setHeader('Vary', 'Origin');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      res.setHeader('Access-Control-Max-Age', '86400');
    }
    if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }
    return __mzOrig(req, res);
  };
}
"""
done = 0
for p in sorted(glob.glob('api/*.js')):
    s = open(p, encoding='utf-8').read()
    if MARK in s:
        print(p, ': sudah')
        continue
    if 'module.exports' not in s:
        print(p, ': DILEWATI (bukan format module.exports)')
        continue
    shutil.copy(p, p + '.bak48')
    open(p, 'w', encoding='utf-8').write(s.rstrip() + '\n' + CORS)
    print(p, ': OK')
    done += 1
print('Selesai, file diubah:', done)
