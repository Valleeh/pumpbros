// Define the cache name and assets to cache
const CACHE_NAME = 'my-site-cache-v1';
const urlsToCache = [
    '/',
    '/static/script.js',
    '/static/style.css',
    '/static/192_logo.jpg',
    '/static/512_logo.png',
];

// Install the service worker and cache the assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

// Activate the service worker and remove old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch and serve assets from cache if available, otherwise fetch from network
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }

                // Fetch from network
                return fetch(event.request);
            })
    );
});
