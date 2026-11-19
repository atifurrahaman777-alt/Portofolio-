const API = 'https://api.audius.co/v1';
const APP = 'MannzzMultifungsi';
const KEY = process.env.AUDIUS_API_KEY || '';
const YT_KEY = process.env.YOUTUBE_API_KEY || '';
const ID_RE = /^[A-Za-z0-9]{1,24}$/;
const PAGE = 25;
const ENT = { '&amp;': '&', '&quot;': '"', '&#39;': "'", '&lt;': '<', '&gt;': '>' };
const decode = s => String(s || '').replace(/&(amp|quot|#39|lt|gt);/g, m => ENT[m]);

function get(path, params, manual) {
  const u = new URL(API + path);
  Object.entries(params || {}).forEach(([k, v]) => u.searchParams.set(k, String(v)));
  u.searchParams.set('app_name', APP);
  return fetch(u, {
    headers: KEY ? { 'x-api-key': KEY } : {},
    redirect: manual ? 'manual' : 'follow',
    signal: AbortSignal.timeout(8000)
  });
}

module.exports = async (req, res) => {
  const q = req.query || {};
  try {
    if (q.info) {
      res.setHeader('Cache-Control', 'public, s-maxage=300');
      return res.status(200).json({ success: true, yt: !!YT_KEY });
    }

    if (q.stream) {
      const id = String(q.stream);
      if (!ID_RE.test(id)) return res.status(400).json({ message: 'ID tidak valid.' });
      const r = await get('/tracks/' + id + '/stream', {}, true);
      const loc = r.headers.get('location');
      if (loc && /^https:\/\//i.test(loc)) {
        res.setHeader('Cache-Control', 'no-store');
        res.statusCode = 302;
        res.setHeader('Location', loc);
        return res.end();
      }
      return res.status(502).json({ message: 'Lagu tidak bisa diputar.' });
    }

    const text = String(q.q || '').trim().slice(0, 80);
    const page = String(q.page || '').slice(0, 60);

    if (String(q.src) === 'yt') {
      if (!YT_KEY) return res.status(503).json({ message: 'Pencarian YouTube belum aktif (isi YOUTUBE_API_KEY di Vercel).' });
      const u = new URL('https://www.googleapis.com/youtube/v3/' + (text ? 'search' : 'videos'));
      u.searchParams.set('part', 'snippet');
      u.searchParams.set('videoCategoryId', '10');
      u.searchParams.set('regionCode', 'ID');
      if (text) {
        u.searchParams.set('type', 'video');
        u.searchParams.set('videoEmbeddable', 'true');
        u.searchParams.set('q', text);
      } else {
        u.searchParams.set('chart', 'mostPopular');
      }
      u.searchParams.set('maxResults', String(PAGE));
      if (/^[A-Za-z0-9_-]{1,60}$/.test(page)) u.searchParams.set('pageToken', page);
      u.searchParams.set('key', YT_KEY);
      const r = await fetch(u, { signal: AbortSignal.timeout(8000) });
      if (r.status === 403 || r.status === 400) {
        return res.status(502).json({ message: 'Kuota YouTube hari ini habis atau API key tidak valid.' });
      }
      if (!r.ok) return res.status(502).json({ message: 'YouTube sedang tidak bisa dihubungi (' + r.status + ').' });
      const j = await r.json();
      const tracks = (j.items || []).map(it => {
        const id = typeof it.id === 'string' ? it.id : (it.id && it.id.videoId);
        const sn = it.snippet || {};
        const th = sn.thumbnails || {};
        return {
          id: id,
          title: decode(sn.title).slice(0, 100),
          artist: decode(sn.channelTitle).slice(0, 60),
          art: (th.medium && th.medium.url) || (th.default && th.default.url) || '',
          dur: 0,
          src: 'yt'
        };
      }).filter(t => t.id && /^[A-Za-z0-9_-]{11}$/.test(t.id));
      res.setHeader('Cache-Control', 'public, s-maxage=300');
      return res.status(200).json({ success: true, tracks, next: j.nextPageToken || '' });
    }

    const offset = Math.max(0, Math.min(500, parseInt(page, 10) || 0));
    const r = text
      ? await get('/tracks/search', { query: text, limit: PAGE, offset })
      : await get('/tracks/trending', { limit: PAGE, offset });
    if (r.status === 401 || r.status === 403) {
      return res.status(502).json({ message: 'Audius meminta API key. Isi AUDIUS_API_KEY di Vercel.' });
    }
    if (!r.ok) return res.status(502).json({ message: 'Layanan musik sedang tidak bisa dihubungi (' + r.status + ').' });
    const j = await r.json();
    const raw = j.data || [];
    const tracks = raw
      .filter(t => t && t.id && t.title && t.is_streamable !== false)
      .map(t => ({
        id: String(t.id),
        title: String(t.title).slice(0, 100),
        artist: String((t.user && t.user.name) || '').slice(0, 60),
        art: (t.artwork && (t.artwork['150x150'] || t.artwork['480x480'])) || '',
        dur: parseInt(t.duration, 10) || 0,
        src: 'audius'
      }));
    res.setHeader('Cache-Control', 'public, s-maxage=120');
    return res.status(200).json({ success: true, tracks, next: raw.length >= PAGE ? String(offset + PAGE) : '' });
  } catch (e) {
    return res.status(502).json({ message: 'Gagal menghubungi layanan musik.' });
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
