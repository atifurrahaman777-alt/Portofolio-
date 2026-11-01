const BASE = 'https://vinzcloud.vercel.app';

module.exports = async function vinzcloud(path, body) {
  if (!['/api/send-link', '/api/verify-link'].includes(path)) {
    throw new Error('Endpoint tidak diizinkan.');
  }

  const response = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Origin': BASE,
      'Referer': `${BASE}/`
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15000)
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = new Error(data.message || `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }

  return data;
};
