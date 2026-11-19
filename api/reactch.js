module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ message: 'Method tidak diizinkan.' });
  }

  const { link, emoji } = req.query || {};

  if (typeof link !== 'string' || !link.trim()) {
    return res.status(400).json({ message: 'Link channel wajib diisi.' });
  }

  let normalized;
  try {
    const u = new URL(link.trim());
    const host = u.hostname.replace(/^www\./i, '');
    if (host !== 'whatsapp.com') {
      throw new Error('Domain harus whatsapp.com');
    }
    const match = u.pathname.match(/^\/channel\/([^/]+)\/(\d+)\/?$/);
    if (!match) {
      throw new Error('Format link harus: https://whatsapp.com/channel/<channelId>/<postId>');
    }
    normalized = `https://whatsapp.com/channel/${match[1]}/${match[2]}`;
  } catch (e) {
    return res.status(400).json({ message: e.message || 'Link tidak valid.' });
  }

  const emojiValue = typeof emoji === 'string' && emoji.trim() ? emoji.trim() : '❤️';

  try {
    const endpoint = new URL('https://api.nexadev.my.id/api/rch');
    endpoint.searchParams.set('key', 'RS-YZS!9qjg');
    endpoint.searchParams.set('url', normalized);
    endpoint.searchParams.set('reaction', emojiValue);

    const response = await fetch(endpoint, {
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json'
      },
      signal: AbortSignal.timeout(20000)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.success) {
      return res.status(response.ok ? 422 : response.status).json({
        message: data.message || 'Gagal mengirim reaksi.'
      });
    }

    return res.status(200).json(data);
  } catch {
    return res.status(502).json({
      message: 'Server reaksi tidak merespons. Coba lagi nanti.'
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
