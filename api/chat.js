const URL_ = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
const KEY = 'chat:global';

async function redis(cmds) {
  const r = await fetch(`${URL_}/pipeline`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmds)
  });
  if (!r.ok) throw new Error('redis ' + r.status);
  return r.json();
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (!URL_ || !TOKEN) {
    return res.status(503).json({ message: 'Database chat belum dikonfigurasi.' });
  }
  try {
    if (req.method === 'GET') {
      const out = await redis([['LRANGE', KEY, 0, 49]]);
      const messages = (out[0].result || [])
        .map(s => { try { return JSON.parse(s); } catch { return null; } })
        .filter(Boolean)
        .reverse();
      return res.status(200).json({ messages });
    }
    if (req.method === 'POST') {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      const name = String(body.name || '').trim().slice(0, 20);
      const text = String(body.text || '').trim().slice(0, 300);
      if (!name || !text) return res.status(400).json({ message: 'Nama dan pesan wajib diisi.' });

      const ip = String(req.headers['x-forwarded-for'] || 'x').split(',')[0].trim();
      const rl = await redis([['SET', `chat:rl:${ip}`, '1', 'EX', 2, 'NX']]);
      if (rl[0].result !== 'OK') return res.status(429).json({ message: 'Pelan-pelan, tunggu sebentar.' });

      const msg = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), name, text, ts: Date.now() };
      await redis([['LPUSH', KEY, JSON.stringify(msg)], ['LTRIM', KEY, 0, 99]]);
      return res.status(200).json({ ok: true });
    }
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ message: 'Method tidak diizinkan.' });
  } catch (e) {
    console.error('chat error:', e);
    return res.status(500).json({ message: 'Chat error.' });
  }
};
