const URL_ = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
const KEY = 'chat:global', ONLINE = 'chat:online', STORIES = 'chat:stories', NOTES = 'chat:notes';
const DAY = 86400000;

async function redis(cmds) {
  const r = await fetch(`${URL_}/pipeline`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(cmds)
  });
  if (!r.ok) throw new Error('redis ' + r.status);
  return r.json();
}
const parse = arr => (arr || []).map(s => { try { return JSON.parse(s); } catch { return null; } }).filter(Boolean);
const cleanAvatar = av => /^https:\/\/[^\s"'<>]{1,280}$/.test(String(av || '')) ? String(av) : '';

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (!URL_ || !TOKEN) return res.status(503).json({ message: 'Database chat belum dikonfigurasi.' });
  try {
    if (req.method === 'GET' && req.query?.audio) {
      const aid = String(req.query.audio).replace(/[^a-z0-9]/gi, '').slice(0, 20);
      const o = await redis([['GET', 'chat:a:' + aid]]);
      if (!o[0].result) return res.status(404).json({ message: 'Audio sudah kedaluwarsa.' });
      return res.status(200).json({ audio: o[0].result });
    }
    if (req.method === 'GET') {
      const cid = String(req.query?.cid || '').replace(/[^a-z0-9]/gi, '').slice(0, 40);
      const now = Date.now();
      const cmds = [['LRANGE', KEY, 0, 59]];
      if (cid) cmds.push(['ZADD', ONLINE, now, cid]);
      cmds.push(
        ['ZREMRANGEBYSCORE', ONLINE, 0, now - 30000],
        ['ZCARD', ONLINE],
        ['EXPIRE', ONLINE, 120],
        ['LRANGE', STORIES, 0, 39],
        ['HGETALL', NOTES]
      );
      const out = await redis(cmds);
      const n = out.length;
      const messages = parse(out[0].result).reverse();
      const stories = parse(out[n - 2].result).filter(s => now - s.ts < DAY);
      const raw = out[n - 1].result;
      let pairs = [];
      if (Array.isArray(raw)) { for (let i = 0; i < raw.length; i += 2) pairs.push([raw[i], raw[i + 1]]); }
      else if (raw && typeof raw === 'object') pairs = Object.entries(raw);
      const notes = pairs.map(([, v]) => { try { return JSON.parse(v); } catch { return null; } })
        .filter(x => x && now - x.ts < DAY);
      return res.status(200).json({ messages, stories, notes, online: out[n - 4].result || 1 });
    }
    if (req.method === 'POST') {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      const type = ['story', 'note'].includes(body.type) ? body.type : 'msg';
      const name = String(body.name || '').trim().slice(0, 20);
      const text = String(body.text || '').trim().slice(0, type === 'note' ? 60 : type === 'story' ? 140 : 300);
      const audio = type === 'msg' && typeof body.audio === 'string' && body.audio.length < 400000 && /^data:audio\/(webm|ogg|mp4|mpeg|aac)[a-z0-9;=.,+-]*;base64,[A-Za-z0-9+\/=]+$/.test(body.audio) ? body.audio : '';
      const dur = Math.max(1, Math.min(60, parseInt(body.dur, 10) || 1));
      if (!name || (type !== 'note' && !text && !audio)) return res.status(400).json({ message: 'Nama dan isi wajib diisi.' });

      const ip = String(req.headers['x-forwarded-for'] || 'x').split(',')[0].trim();
      const rl = await redis([['SET', `chat:rl:${ip}`, '1', 'EX', 2, 'NX']]);
      if (rl[0].result !== 'OK') return res.status(429).json({ message: 'Pelan-pelan, tunggu sebentar.' });

      const avatar = cleanAvatar(body.avatar);
      const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

      if (type === 'story') {
        const bg = Math.max(0, Math.min(5, parseInt(body.bg, 10) || 0));
        await redis([['LPUSH', STORIES, JSON.stringify({ id, name, avatar, text, bg, ts: Date.now() })], ['LTRIM', STORIES, 0, 49]]);
        return res.status(200).json({ ok: true });
      }
      if (type === 'note') {
        if (!text) await redis([['HDEL', NOTES, name]]);
        else await redis([['HSET', NOTES, name, JSON.stringify({ name, avatar, text, ts: Date.now() })]]);
        return res.status(200).json({ ok: true });
      }
      let reply = null;
      if (body.reply && typeof body.reply === 'object') {
        reply = {
          id: String(body.reply.id || '').slice(0, 20),
          name: String(body.reply.name || '').slice(0, 20),
          text: String(body.reply.text || '').slice(0, 80)
        };
      }
      if (audio) await redis([['SET', 'chat:a:' + id, audio, 'EX', 172800]]);
      await redis([['LPUSH', KEY, JSON.stringify({ id, name, text, avatar, reply, ts: Date.now(), ...(audio ? { aud: 1, dur } : {}) })], ['LTRIM', KEY, 0, 99]]);
      return res.status(200).json({ ok: true });
    }
    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ message: 'Method tidak diizinkan.' });
  } catch (e) {
    console.error('chat error:', e);
    return res.status(500).json({ message: 'Chat error.' });
  }
};
