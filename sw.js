const VERSION = 'scs-v4';
const SHELL = [
  './', 'index.html', 'docs.json', 'manifest.json',
  'assets/icon-192.png', 'assets/header-mark.png', 'assets/icon-512.png', 'assets/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Network-first, cache fallback: documents are always fresh when online,
// and everything already seen keeps working with no connection at all.
self.addEventListener('fetch', e => {
  if(e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if(url.origin !== location.origin) return;
  // range requests (PDF streaming) bypass the cache layer entirely
  if(e.request.headers.has('range')) return;

  e.respondWith(
    fetch(e.request).then(res => {
      if(res.ok){
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(stripBust(e.request), copy));
      }
      return res;
    }).catch(() =>
      caches.match(stripBust(e.request)).then(hit => hit || Response.error())
    )
  );
});

// docs.json is fetched with a ?v= cache-buster; normalize so offline lookup hits
function stripBust(req){
  const u = new URL(req.url);
  if(u.pathname.endsWith('docs.json')){ u.search = ''; return new Request(u.href); }
  return req;
}
