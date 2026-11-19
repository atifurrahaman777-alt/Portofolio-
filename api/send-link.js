const vinzcloud = require('../lib/vinzcloud');

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({
      success: false,
      message: 'Gunakan metode POST.'
    });
  }

  const email = String(req.body?.email || '').trim();

  if (email.length > 254 ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({
      success: false,
      message: 'Format email tidak valid.'
    });
  }

  try {
    const data = await vinzcloud('/api/send-link', { email });
    return res.status(200).json(data);
  } catch (err) {
    console.error('send-link:', err.message);
    return res.status(err.status || 502).json({
      success: false,
      message: err.status === 503
        ? err.message
        : 'Permintaan kirim link gagal. Periksa konfigurasi API.'
    });
  }
};

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
