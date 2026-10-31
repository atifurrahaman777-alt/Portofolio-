module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ message: 'Method tidak diizinkan.' });
  }

  const url = req.query?.url;
  const base = process.env.DOWNLOADER_API_URL;

  if (!base) {
    return res.status(503).json({
      message: 'Backend downloader belum dikonfigurasi.'
    });
  }

  if (typeof url !== 'string' || !url.trim() || url.length > 2048) {
    return res.status(400).json({ message: 'Link tidak valid.' });
  }

  try {
    const endpoint = new URL('/api/download', base);
    endpoint.searchParams.set('url', url);

    const response = await fetch(endpoint, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(20000)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      return res.status(response.status).json({
        message: data.detail || data.message || 'Gagal memproses link.'
      });
    }

    if (data.downloadUrl && data.downloadUrl.startsWith('/')) {
      data.downloadUrl = new URL(data.downloadUrl, base).toString();
    }

    return res.status(200).json(data);
  } catch {
    return res.status(502).json({
      message: 'Backend downloader tidak merespons. Coba lagi nanti.'
    });
  }
};
