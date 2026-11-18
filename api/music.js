const API = 'https://api.audius.co/v1';
const APP = 'MannzzMultifungsi';
const KEY = process.env.AUDIUS_API_KEY || '';
const ID_RE = /^[A-Za-z0-9]{1,24}$/;

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
    const r = text ? await get('/tracks/search', { query: text, limit: 20 }) : await get('/tracks/trending', { limit: 20 });
    if (r.status === 401 || r.status === 403) {
      return res.status(502).json({ message: 'Audius meminta API key. Isi AUDIUS_API_KEY di Vercel.' });
    }
    if (!r.ok) return res.status(502).json({ message: 'Layanan musik sedang tidak bisa dihubungi (' + r.status + ').' });
    const j = await r.json();
    const tracks = (j.data || [])
      .filter(t => t && t.id && t.title && t.is_streamable !== false)
      .map(t => ({
        id: String(t.id),
        title: String(t.title).slice(0, 100),
        artist: String((t.user && t.user.name) || '').slice(0, 60),
        art: (t.artwork && (t.artwork['150x150'] || t.artwork['480x480'])) || '',
        dur: parseInt(t.duration, 10) || 0
      }));
    res.setHeader('Cache-Control', 'public, s-maxage=120');
    return res.status(200).json({ success: true, tracks });
  } catch (e) {
    return res.status(502).json({ message: 'Gagal menghubungi layanan musik.' });
  }
};
