// Naikkan versi cache setiap deploy supaya aset lama ikut terhapus.
const C = 'mannzz-v6';
const SHELL = '/index.html';

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(C)
      .then((c) => c.add(SHELL))
      .catch(() => {})
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => e.waitUntil(
  caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== C).map((k) => caches.delete(k))))
    .then(() => self.clients.claim())
));

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const u = new URL(req.url);
  if (req.method !== 'GET' || u.origin !== location.origin || u.pathname.startsWith('/api/') || u.pathname === '/sw.js') return;

  // Halaman selalu diambil dari jaringan; cache hanya dipakai saat offline.
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).catch(() => caches.match(req).then((hit) => hit || caches.match(SHELL)))
    );
    return;
  }

  // Aset statis: cache lebih dulu, tapi hanya simpan respons sukses.
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((r) => {
      if (r.ok && r.type === 'basic') {
        const copy = r.clone();
        caches.open(C).then((c) => c.put(req, copy));
      }
      return r;
    }))
  );
});
