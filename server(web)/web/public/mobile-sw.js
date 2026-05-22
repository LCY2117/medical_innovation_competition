const CACHE_NAME = 'lifereflex-mobile-shell-v6';
const APP_SHELL = ['/mobile', '/manifest.webmanifest', '/pwa-icon.svg', '/offline.html'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.registration.navigationPreload?.enable())
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }

  if (url.pathname.startsWith('/api') || url.pathname.startsWith('/ws')) {
    return;
  }

  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  if (url.pathname === '/manifest.webmanifest' || url.pathname === '/pwa-icon.svg' || url.pathname === '/offline.html') {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  if (isMobileNavigation(request, url)) {
    event.respondWith(networkFirstMobileShell(request, event.preloadResponse));
  }
});

function isMobileNavigation(request, url) {
  return request.mode === 'navigate' && (url.pathname === '/mobile' || url.pathname.startsWith('/mobile/'));
}

async function networkFirstMobileShell(request, preloadResponsePromise) {
  const cachedShell = await caches.match('/mobile');
  try {
    const preloadResponse = await preloadResponsePromise;
    if (preloadResponse) {
      await cacheResponse('/mobile', preloadResponse.clone());
      return preloadResponse;
    }
    const response = await fetch(request);
    if (response.ok) {
      await cacheResponse('/mobile', response.clone());
    }
    return response;
  } catch (error) {
    return cachedShell || caches.match('/offline.html');
  }
}

async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);
  const network = fetch(request)
    .then(async (response) => {
      if (response.ok) {
        await cacheResponse(request, response.clone());
      }
      return response;
    })
    .catch(() => cached);
  return cached || network;
}

async function cacheResponse(request, response) {
  const cache = await caches.open(CACHE_NAME);
  await cache.put(request, response);
}
