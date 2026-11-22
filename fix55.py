import shutil

f = 'api/chat.js'
s = open(f, encoding='utf-8').read()
if 'MZ-SEC' in s:
    print('Sudah pernah dipasang.')
    raise SystemExit

A1 = r"""      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
"""
B1 = r"""      const clen = parseInt(req.headers['content-length'], 10) || 0; /* MZ-SEC */
      if (clen > 460000) return res.status(413).json({ message: 'Data terlalu besar.' });
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      if (!body.audio && clen > 8000) return res.status(413).json({ message: 'Data terlalu besar.' });
"""

A2 = r"""      if (!owner) {
        const ip = String(req.headers['x-forwarded-for'] || 'x').split(',')[0].trim();
        const rl = await redis([['SET', `chat:rl:${ip}`, '1', 'EX', 2, 'NX']]);
        if (rl[0].result !== 'OK') return res.status(429).json({ message: 'Pelan-pelan, tunggu sebentar.' });
      }
"""
B2 = r"""      if (!action && !me) return res.status(401).json({ message: 'Masuk dulu untuk ikut ngobrol (login Google di halaman utama).' });
      if (!owner) {
        const ip = String(req.headers['x-forwarded-for'] || 'x').split(',')[0].trim();
        const minute = Math.floor(Date.now() / 60000);
        const who_ = me ? 'u:' + me.uid : 'i:' + ip;
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
"""

A3 = r"""      const name = String(body.name || '').trim().slice(0, 20);
      const text = String(body.text || '').trim().slice(0, type === 'note' ? 60 : type === 'story' ? 140 : 300);
"""
B3 = r"""      const strip = (v, hard) => String(v || '').replace(hard ? /[\u0000-\u001F\u007F\u200B-\u200F\u202A-\u202E\u2028\u2029\uFEFF]/g : /[\u0000-\u001F\u007F\u200B\u200E\u200F\u202A-\u202E\u2028\u2029\uFEFF]/g, ' ').replace(/\s+/g, ' ').trim();
      const name = strip(String(body.name || '').normalize('NFKC'), true).slice(0, 20);
      const text = strip(body.text, false).slice(0, type === 'note' ? 60 : type === 'story' ? 140 : 300);
"""

A4 = r"""      if (isBanned(bans, { oh, name, uid: me && me.uid })) {
        return res.status(403).json({ banned: true, message: 'Akunmu diblokir dari chat.' });
      }
"""
B4 = A4 + r"""      {
        const key = name.normalize('NFKC').toLowerCase();
        const reserved = String(process.env.RESERVED_NAMES || 'owner,admin,administrator,mod,moderator,system').split(',').map(x => x.trim().toLowerCase()).filter(Boolean);
        if (!owner && reserved.includes(key)) return res.status(403).json({ message: 'Nama itu khusus Owner.' });
        const got = await redis([['HGET', 'chat:names', key], ['HGET', 'chat:unames', me.uid]]);
        const holder = got[0].result, prev = got[1].result;
        if (holder && holder !== me.uid && !owner) {
          return res.status(403).json({ message: 'Nama "' + name + '" sudah dipakai orang lain. Ganti nama di profil chat.' });
        }
        if (holder !== me.uid) {
          const cmds = [['HSET', 'chat:names', key, me.uid], ['HSET', 'chat:unames', me.uid, key]];
          if (prev && prev !== key) cmds.push(['HDEL', 'chat:names', prev]);
          await redis(cmds);
        }
      }
"""

for a in (A1, A2, A3, A4):
    if s.count(a) != 1:
        print('GAGAL: bagian api/chat.js tidak cocok dengan versi yang gw tahu: ' + a.strip()[:60] + ' ... Tidak ada yang diubah.')
        raise SystemExit

shutil.copy(f, f + '.bak55')
s = s.replace(A1, B1, 1).replace(A2, B2, 1).replace(A3, B3, 1).replace(A4, B4, 1)
open(f, 'w', encoding='utf-8').write(s)
print('api/chat.js diperketat : OK')
