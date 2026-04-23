/** @odoo-module **/

const originalConsoleError = console.error;

console.error = function (...args) {
    originalConsoleError.apply(console, args);

    const msg = args.map(a => {
        if (typeof a === 'string') return a;
        if (a && a.message) return a.message;
        return '';
    }).join(' ');

    // Intercept standard Odoo Legacy and HOOT test failures
    if (!window._domDumped && (msg.includes('TIMEOUT') || msg.includes('FAILED:') || msg.includes('AssertionError'))) {
        window._domDumped = true; // Prevent spamming the log with multiple dumps from a single failure
        try {
            const clone = document.body.cloneNode(true);

            // Strip out noise: non-visible structural tags, SVGs, and framework-hidden elements
            const elementsToRemove = clone.querySelectorAll('script, style, link, meta, noscript, svg, path, iframe, .d-none, .o_hidden');
            elementsToRemove.forEach(el => el.remove());

            originalConsoleError.call(console, "\n========== VISIBLE DOM DUMP ==========\n" + clone.innerHTML + "\n======================================\n");
        } catch (e) {
            originalConsoleError.call(console, "Failed to dump DOM: " + e.toString());
        }
    }
};
