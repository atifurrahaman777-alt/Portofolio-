module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({
      success: false,
      message: 'Gunakan GET.'
    });
  }

  try {
    const link = String(req.query?.url || '').trim();

    if (!link || link.length > 3000) {
      return res.status(400).json({
        success: false,
        message: 'Masukkan link terlebih dahulu.'
      });
    }

    let url;

    try {
      url = new URL(link);
    } catch {
      return res.status(400).json({
        success: false,
        message: 'Link tidak valid.'
      });
    }

    if (!['https:', 'http:'].includes(url.protocol)) {
      return res.status(400).json({
        success: false,
        message: 'Protokol tidak didukung.'
      });
    }

    const { resolve, detect } = await import('../lib/omdown.mjs');

    const platform = detect(url.href);

    if (!platform) {
      return res.status(400).json({
        success: false,
        message: 'Platform tidak didukung.'
      });
    }

    const data = await resolve(url.href, {
      platform,
      locale: 'en',
      size: false
    });

    const formats = Array.isArray(data.formats)
      ? data.formats
      : [];

    const available = formats.filter(f =>
      f && typeof f.downloadUrl === 'string' &&
      /^https?:\/\//i.test(f.downloadUrl)
    );

    return res.status(200).json({
      success: true,
      title: data.title || data.name || platform,
      thumbnail: data.thumbnailUrl || data.thumbnail || '',
      meta: data.platform || platform,
      downloadUrl: available[0]?.downloadUrl || '',
      formats: available,
      data
    });

  } catch (err) {
    console.error('OMDown:', err);

    return res.status(502).json({
      success: false,
      message: err.message || 'Gagal mengambil media.'
    });
  }
};
