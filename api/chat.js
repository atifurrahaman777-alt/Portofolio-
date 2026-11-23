const crypto = require('crypto');

const URL_ = process.env.UPSTASH_REDIS_REST_URL || process.env.KV_REST_API_URL;
const TOKEN = process.env.UPSTASH_REDIS_REST_TOKEN || process.env.KV_REST_API_TOKEN;
const KEY = 'chat:global', ONLINE = 'chat:online', STORIES = 'chat:stories', NOTES = 'chat:notes', BANS = 'chat:bans';
const DAY = 86400000;
const API_KEY = process.env.FIREBASE_API_KEY || 'AIzaSyArfUhdOVfyIsjKjfD_9BkbixxNa6XRvsM';
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
// kepemilikan baru berdasarkan uid yang disimpan server; o (hash cid) hanya untuk pesan tamu lawas
const mineOf = (x, me, oh) => !!((x.o && oh && x.o === oh) || (me && x.u && x.u === me.uid));
const mineLegacy = (x, authName) => !!(authName && !x.u && !x.o && String(x.name || '').toLowerCase() === authName);

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
      if (me) ix.uname = cmds.push(['HGET', 'chat:unames', me.uid]) - 1;
      const out = await redis(cmds);

      // nama resmi diambil dari server, bukan dari query klien yang bisa diganti lokal
      const authName = me && ix.uname !== undefined ? out[ix.uname].result || '' : '';
      const messages = parse(out[ix.msgs].result).reverse().map(m => {
        const mine = mineOf(m, me, oh);
        const { o, u, ...rest } = m;
        return { ...rest, mine };
      });
      const stories = parse(out[ix.stories].result).filter(s => now - s.ts < DAY)
        .map(s => ({ ...s, mine: mineOf(s, me, oh) || mineLegacy(s, authName) }));
      const raw = out[ix.notes].result;
      let pairs = [];
      if (Array.isArray(raw)) { for (let i = 0; i < raw.length; i += 2) pairs.push([raw[i], raw[i + 1]]); }
      else if (raw && typeof raw === 'object') pairs = Object.entries(raw);
      const notes = pairs.map(([, v]) => { try { return JSON.parse(v); } catch { return null; } })
        .filter(x => x && now - x.ts < DAY)
        .map(n => ({ ...n, mine: mineOf(n, me, oh) || mineLegacy(n, authName) }));

      const bans = parse(out[ix.bans].result);
      const owner = !!(me && me.isOwner);
      const banned = isBanned(bans, { oh, name: authName || name, uid: me && me.uid });
      return res.status(200).json({
        messages, stories, notes,
        online: out[ix.online].result || 1,
        isOwner: owner,
        banned,
        ...(owner ? { bans: bans.map(b => ({ id: b.id, name: b.name, ts: b.ts })) } : {})
      });
    }

    if (req.method === 'POST') {
      const clen = parseInt(req.headers['content-length'], 10) || 0; /* MZ-SEC */
      if (clen > 460000) return res.status(413).json({ message: 'Data terlalu besar.' });
      let body;
      try { body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {}); }
      catch { return res.status(400).json({ message: 'Data tidak valid.' }); }
      if (!body || typeof body !== 'object' || Array.isArray(body)) return res.status(400).json({ message: 'Data tidak valid.' });
      if (!body.audio && clen > 8000) return res.status(413).json({ message: 'Data terlalu besar.' });
      const cid = cleanCid(body.cid);
      const oh = ownerHash(cid);
      const me = await who(req);
      // semua aksi yang mengubah data wajib login (termasuk delete/ban/unban)
      if (!me) return res.status(401).json({ message: 'Sesi berakhir. Masuk lagi untuk ikut ngobrol.' });
      const owner = !!(me && me.isOwner);
      const action = ['delete', 'ban', 'unban'].includes(body.type) ? body.type : '';
      const type = ['story', 'note'].includes(body.type) ? body.type : 'msg';
      const strip = (v, hard) => String(v || '').replace(hard ? /[\u0000-\u001F\u007F\u200B-\u200F\u202A-\u202E\u2028\u2029\uFEFF]/g : /[\u0000-\u001F\u007F\u200B\u200E\u200F\u202A-\u202E\u2028\u2029\uFEFF]/g, ' ').replace(/\s+/g, ' ').trim();
      const name = strip(String(body.name || '').normalize('NFKC'), true).slice(0, 20);
      const text = strip(body.text, false).slice(0, type === 'note' ? 60 : type === 'story' ? 140 : 300);
      const audio = type === 'msg' && typeof body.audio === 'string' && body.audio.length < 400000 && /^data:audio\/(webm|ogg|mp4|mpeg|aac)[a-z0-9;=.,+-]*;base64,[A-Za-z0-9+\/=]+$/.test(body.audio) ? body.audio : '';
      const dur = Math.max(1, Math.min(60, parseInt(body.dur, 10) || 1));

      // ban dicek lebih dulu, dengan nama resmi dari chat:unames (bukan nama bebas dari klien)
      const pre = await redis([['HVALS', BANS], ['HGET', 'chat:unames', me.uid]]);
      const bans = parse(pre[0].result);
      const authName = pre[1].result || '';
      if (isBanned(bans, { oh, name: authName || name, uid: me.uid })) {
        return res.status(403).json({ banned: true, message: 'Akunmu diblokir dari chat.' });
      }

      if (!action) {
        if (!name || (type !== 'note' && !text && !audio)) return res.status(400).json({ message: 'Nama dan isi wajib diisi.' });
        if (!owner) {
          const ip = String(req.headers['x-forwarded-for'] || 'x').split(',')[0].trim();
          const minute = Math.floor(Date.now() / 60000);
          const who_ = 'u:' + me.uid;
          const rl = await redis([
            ['SET', `chat:rl:${who_}`, '1', 'EX', 2, 'NX'],
            ['INCR', `chat:rw:${who_}:${minute}`],
            ['EXPIRE', `chat:rw:${who_}:${minute}`, 90],
            ['INCR', `chat:ri:${ip}:${minute}`],
            ['EXPIRE', `chat:ri:${ip}:${minute}`, 90]
          ]);
          if (rl[0].result !== 'OK') return res.status(429).json({ message: 'Pelan-pelan, tunggu sebentar.' });
          if ((rl[1].result || 0) > 20 || (rl[3].result || 0) > 60) return res.status(429).json({ message: 'Terlalu banyak pesan, tunggu semenit.' });
        }
      }

      if (action === 'delete') {
        const id = String(body.id || '');
        if (!ID_RE.test(id)) return res.status(400).json({ message: 'ID pesan tidak valid.' });
        const f = await findMsg(id);
        if (!f) return res.status(404).json({ message: 'Pesan tidak ditemukan (mungkin sudah terhapus).' });
        // hak utama dari uid; fallback hanya untuk pesan tamu lawas tanpa 'u' (cid pemilik + login)
        const own = !!(me && f.m.u && f.m.u === me.uid) || !!(!f.m.u && oh && f.m.o && f.m.o === oh);
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
        const targetUid = f.m.u || '';
        const self = targetUid ? targetUid === me.uid : !!(oh && f.m.o && f.m.o === oh);
        if (self) return res.status(400).json({ message: 'Kamu tidak bisa mem-ban dirimu sendiri.' });
        const targetOh = targetUid ? '' : (f.m.o || '');
        let targetName = String(f.m.name || '').slice(0, 20);
        if (targetUid) {
          const got = await redis([['HGET', 'chat:unames', targetUid]]);
          if (got[0].result) targetName = String(got[0].result).slice(0, 20);
        }
        const nl = targetName.toLowerCase();
        const dup = bans.some(b => (targetUid && b.u === targetUid) || (targetOh && b.o === targetOh) || (b.n && b.n === nl));
        if (!dup) {
          const banId = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
          await redis([['HSET', BANS, banId, JSON.stringify({
            id: banId, name: targetName, n: nl,
            o: targetOh, u: targetUid, ts: Date.now()
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

      {
        const key = name.normalize('NFKC').toLowerCase();
        const reserved = String(process.env.RESERVED_NAMES || 'owner,admin,administrator,mod,moderator,system').split(',').map(x => x.trim().toLowerCase()).filter(Boolean);
        if (!owner && reserved.includes(key)) return res.status(403).json({ message: 'Nama itu khusus Owner.' });
        const got = await redis([['HGET', 'chat:names', key], ['HGET', 'chat:unames', me.uid]]);
        const holder = got[0].result, prev = got[1].result;
        if (holder && holder !== me.uid) {
          return res.status(403).json({ message: 'Nama "' + name + '" sudah dipakai orang lain. Ganti nama di profil chat.' });
        }
        if (holder === me.uid) {
          if (prev !== key) await redis([['HSET', 'chat:unames', me.uid, key]]);
        } else {
          // HSETNX membuat klaim nama atomik untuk dua request bersamaan
          const claim = await redis([['HSETNX', 'chat:names', key, me.uid]]);
          if (claim[0].result !== 1 && claim[0].result !== '1') {
            return res.status(403).json({ message: 'Nama "' + name + '" sudah dipakai orang lain. Ganti nama di profil chat.' });
          }
          const cmds = [['HSET', 'chat:unames', me.uid, key]];
          if (prev && prev !== key) cmds.push(['HDEL', 'chat:names', prev]);
          await redis(cmds);
        }
      }

      const avatar = cleanAvatar(body.avatar);
      const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

      if (type === 'story') {
        const bg = Math.max(0, Math.min(5, parseInt(body.bg, 10) || 0));
        await redis([['LPUSH', STORIES, JSON.stringify({ id, name, avatar, text, bg, ts: Date.now(), u: me.uid, o: oh })], ['LTRIM', STORIES, 0, 49]]);
        return res.status(200).json({ ok: true, name });
      }
      if (type === 'note') {
        // catatan kini dikunci per uid agar tidak hilang saat nama ditampilkan ulang
        const noteKey = 'u:' + me.uid;
        if (!text) await redis([['HDEL', NOTES, noteKey]]);
        else await redis([['HSET', NOTES, noteKey, JSON.stringify({ name, avatar, text, ts: Date.now(), u: me.uid, o: oh })]]);
        return res.status(200).json({ ok: true, name });
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
      return res.status(200).json({ ok: true, name });
    }

    res.setHeader('Allow', 'GET, POST');
    return res.status(405).json({ message: 'Method tidak diizinkan.' });
  } catch (e) {
    console.error('chat error:', e);
    return res.status(500).json({ message: 'Chat error.' });
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
