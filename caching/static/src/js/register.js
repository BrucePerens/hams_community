if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('[Caching] Worker registered with scope:', registration.scope);
            })
            .catch((err) => {
                console.error('[Caching] Registration failed:', err);
            });
    });
}
