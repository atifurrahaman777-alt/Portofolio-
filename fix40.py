import shutil, os

f = 'api/chat.js'
if not os.path.exists(f):
    print('GAGAL: api/chat.js tidak ada.')
    raise SystemExit
old = open(f, encoding='utf-8').read()
if 'chat:bans' in old:
    print('Sudah pernah dipasang.')
    raise SystemExit

JS = r'''const crypto = require('crypto');

const URL_ = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
const KEY = 'chat:global', ONLINE = 'chat:online', STORIES = 'chat:stories', NOTES = 'chat:notes', BANS = 'chat:bans';
const DAY = 86400000;
const API_KEY = process.env.FIREBASE_API_KEY || 'AIzaSyC_iYADCUCDN1pCl3j4-jeZT3pU2XcIydU';
const OWNERS = String(process.env.OWNER_EMAILS || '').split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
const SALT = process.env.CHAT_SALT || TOKEN || 'chat';
const ID_RE = /^[a-z0-9]{1,20}$/i;

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
const cleanCid = v => String(v || '').replace(/[^a-z0-9]/gi, '').slice(0, 40);
const ownerHash = cid => cid ? crypto.createHash('sha256').update(SALT + ':' + cid).digest('hex').slice(0, 20) : '';

const tokCache = new Map();
async function who(req) {
  const h = String(req.headers.authorization || '');
  const t = h.startsWith('Bearer ') ? h.slice(7).trim() : '';
  if (!t || t.length > 4000) return null;
  const c = tokCache.get(t);
  if (c && c.exp > Date.now()) return c.v;
  let v = null;
  try {
    const r = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idToken: t }),
      signal: AbortSignal.timeout(6000)
    });
    if (r.ok) {
      const d = await r.json();
      const u = d.users && d.users[0];
      if (u && u.localId && !u.disabled) {
        const email = String(u.email || '').toLowerCase();
        v = { uid: u.localId, email, isOwner: !!(u.emailVerified && email && OWNERS.includes(email)) };
      }
    }
  } catch {}
  if (tokCache.size > 200) tokCache.clear();
  tokCache.set(t, { v, exp: Date.now() + (v ? 60000 : 8000) });
  return v;
}

function isBanned(bans, who_) {
  const n = String(who_.name || '').trim().toLowerCase();
  return bans.some(b => (b.o && who_.oh && b.o === who_.oh) || (b.u && who_.uid && b.u === who_.uid) || (b.n && n && b.n === n));
}

async function findMsg(id) {
  const out = await redis([['LRANGE', KEY, 0, 99]]);
  for (const raw of out[0].result || []) {
    try { const m = JSON.parse(raw); if (m && m.id === id) return { raw, m }; } catch {}
  }
  return null;
}

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
      const cid = cleanCid(req.query?.cid);
      const name = String(req.query?.name || '').trim().slice(0, 20);
      const now = Date.now();
      const me = await who(req);
      const oh = ownerHash(cid);
      const cmds = [], ix = {};
      ix.msgs = cmds.push(['LRANGE', KEY, 0, 59]) - 1;
      if (cid) cmds.push(['ZADD', ONLINE, now, cid]);
      cmds.push(['ZREMRANGEBYSCORE', ONLINE, 0, now - 30000]);
      ix.online = cmds.push(['ZCARD', ONLINE]) - 1;
      cmds.push(['EXPIRE', ONLINE, 120]);
      ix.stories = cmds.push(['LRANGE', STORIES, 0, 39]) - 1;
      ix.notes = cmds.push(['HGETALL', NOTES]) - 1;
      ix.bans = cmds.push(['HVALS', BANS]) - 1;
      const out = await redis(cmds);

      const messages = parse(out[ix.msgs].result).reverse().map(m => {
        const mine = !!((m.o && oh && m.o === oh) || (me && m.u && m.u === me.uid));
        const { o, u, ...rest } = m;
        return { ...rest, mine };
      });
      const stories = parse(out[ix.stories].result).filter(s => now - s.ts < DAY);
      const raw = out[ix.notes].result;
      let pairs = [];
      if (Array.isArray(raw)) { for (let i = 0; i < raw.length; i += 2) pairs.push([raw[i], raw[i + 1]]); }
      else if (raw && typeof raw === 'object') pairs = Object.entries(raw);
      const notes = pairs.map(([, v]) => { try { return JSON.parse(v); } catch { return null; } })
        .filter(x => x && now - x.ts < DAY);

      const bans = parse(out[ix.bans].result);
      const owner = !!(me && me.isOwner);
      const banned = isBanned(bans, { oh, name, uid: me && me.uid });
      return res.status(200).json({
        messages, stories, notes,
        online: out[ix.online].result || 1,
        isOwner: owner,
        banned,
        ...(owner ? { bans: bans.map(b => ({ id: b.id, name: b.name, ts: b.ts })) } : {})
      });
    }

    if (req.method === 'POST') {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      const cid = cleanCid(body.cid);
      const oh = ownerHash(cid);
      const me = await who(req);
      const owner = !!(me && me.isOwner);
      const action = ['delete', 'ban', 'unban'].includes(body.type) ? body.type : '';

      if (!owner) {
        const ip = String(req.headers['x-forwarded-for'] || 'x').split(',')[0].trim();
        const rl = await redis([['SET', `chat:rl:${ip}`, '1', 'EX', 2, 'NX']]);
        if (rl[0].result !== 'OK') return res.status(429).json({ message: 'Pelan-pelan, tunggu sebentar.' });
      }
      const bans = parse((await redis([['HVALS', BANS]]))[0].result);

      if (action === 'delete') {
        const id = String(body.id || '');
        if (!ID_RE.test(id)) return res.status(400).json({ message: 'ID pesan tidak valid.' });
        const f = await findMsg(id);
        if (!f) return res.status(404).json({ message: 'Pesan tidak ditemukan (mungkin sudah terhapus).' });
        const own = (f.m.o && oh && f.m.o === oh) || (me && f.m.u && f.m.u === me.uid);
        if (!own && !owner) return res.status(403).json({ message: 'Kamu tidak boleh menghapus pesan ini.' });
        const cmds = [['LREM', KEY, 1, f.raw]];
        if (f.m.aud) cmds.push(['DEL', 'chat:a:' + id]);
        await redis(cmds);
        return res.status(200).json({ ok: true });
      }

      if (action === 'ban') {
        if (!owner) return res.status(403).json({ message: 'Khusus Owner.' });
        const id = String(body.id || '');
        if (!ID_RE.test(id)) return res.status(400).json({ message: 'ID pesan tidak valid.' });
        const f = await findMsg(id);
        if (!f) return res.status(404).json({ message: 'Pesan tidak ditemukan.' });
        if ((f.m.o && f.m.o === oh) || (f.m.u && f.m.u === me.uid)) {
          return res.status(400).json({ message: 'Kamu tidak bisa mem-ban dirimu sendiri.' });
        }
        const nl = String(f.m.name || '').trim().toLowerCase();
        const dup = bans.some(b => (f.m.o && b.o === f.m.o) || (f.m.u && b.u === f.m.u) || (b.n && b.n === nl));
        if (!dup) {
          const banId = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
          await redis([['HSET', BANS, banId, JSON.stringify({
            id: banId, name: String(f.m.name || '').slice(0, 20), n: nl,
            o: f.m.o || '', u: f.m.u || '', ts: Date.now()
          })]]);
        }
        return res.status(200).json({ ok: true });
      }

      if (action === 'unban') {
        if (!owner) return res.status(403).json({ message: 'Khusus Owner.' });
        const banId = String(body.banId || '');
        if (!ID_RE.test(banId)) return res.status(400).json({ message: 'ID ban tidak valid.' });
        await redis([['HDEL', BANS, banId]]);
        return res.status(200).json({ ok: true });
      }

      const type = ['story', 'note'].includes(body.type) ? body.type : 'msg';
      const name = String(body.name || '').trim().slice(0, 20);
      const text = String(body.text || '').trim().slice(0, type === 'note' ? 60 : type === 'story' ? 140 : 300);
      const audio = type === 'msg' && typeof body.audio === 'string' && body.audio.length < 400000 && /^data:audio\/(webm|ogg|mp4|mpeg|aac)[a-z0-9;=.,+-]*;base64,[A-Za-z0-9+\/=]+$/.test(body.audio) ? body.audio : '';
      const dur = Math.max(1, Math.min(60, parseInt(body.dur, 10) || 1));
      if (!name || (type !== 'note' && !text && !audio)) return res.status(400).json({ message: 'Nama dan isi wajib diisi.' });
      if (isBanned(bans, { oh, name, uid: me && me.uid })) {
        return res.status(403).json({ banned: true, message: 'Akunmu diblokir dari chat.' });
      }

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
      await redis([['LPUSH', KEY, JSON.stringify({
        id, name, text, avatar, reply, ts: Date.now(),
        ...(oh ? { o: oh } : {}),
        ...(me ? { u: me.uid } : {}),
        ...(audio ? { aud: 1, dur } : {})
      })], ['LTRIM', KEY, 0, 99]]);
      return res.status(200).json({ ok: true });
    }

    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ message: 'Method tidak diizinkan.' });
  } catch (e) {
    console.error('chat error:', e);
    return res.status(500).json({ message: 'Chat error.' });
  }
};
'''

shutil.copy(f, f + '.bak40')
open(f, 'w', encoding='utf-8').write(JS)
print('api/chat.js baru : OK')
