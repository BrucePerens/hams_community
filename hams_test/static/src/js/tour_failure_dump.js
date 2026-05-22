/** @odoo-module **/

const originalConsoleError = console.error;

// Intercept network drop completely independent of pending requests
window.addEventListener('offline', () => {
    console.error("FATAL: Browser detected network OFFLINE state! Backend connection lost.");
});

// 1. Maintain a ledger of unresolved network requests to diagnose backend hangs
window._pendingRPCs = new Set();
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const url = typeof args[0] === 'string' ? args[0] : (args[0] ? args[0].url : 'unknown');
    window._pendingRPCs.add(url);
    try {
        return await originalFetch.apply(this, args);
    } catch (e) {
        if (e && e.name === 'TypeError' && e.message === 'Failed to fetch') {
            console.error("FATAL: Fetch API network error. The backend server crashed or dropped the connection. URL: " + url);
        }
        throw e;
    } finally {
        window._pendingRPCs.delete(url);
    }
};

const originalXHR = window.XMLHttpRequest.prototype.open;
window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.addEventListener('loadend', () => window._pendingRPCs.delete(url));
    this.addEventListener('error', () => {
        window._pendingRPCs.delete(url);
        console.error("FATAL: XHR network error. The backend server crashed or dropped the connection. URL: " + url);
    });
    this.addEventListener('abort', () => window._pendingRPCs.delete(url));
    window._pendingRPCs.add(url);
    return originalXHR.call(this, method, url, ...rest);
};

// 2. Condense the DOM into an "Interactable Skeleton" to protect LLM token limits
function buildInteractableSkeleton(node) {
    if (node.nodeType === Node.TEXT_NODE) return node.textContent.trim();
    if (node.nodeType !== Node.ELEMENT_NODE) return "";

    // Mathematically prune structurally invisible trees
    if (node.classList && (node.classList.contains('d-none') || node.classList.contains('o_hidden'))) return "";

    // Identify semantic components critical for tour triggers
    let isImportant = ['BUTTON', 'INPUT', 'A', 'SELECT', 'TEXTAREA'].includes(node.tagName) ||
        node.hasAttribute('name') || node.hasAttribute('id') || node.hasAttribute('data-menu-xmlid') ||
        (node.classList && Array.from(node.classList).some(c => c.startsWith('o_tour_') || c === 'o_notification' || c === 'modal'));

    let childrenText = Array.from(node.childNodes).map(buildInteractableSkeleton).filter(Boolean).join(' ');

    if (isImportant) {
        let attrs = [];
        ['name', 'id', 'data-menu-xmlid', 'type', 'placeholder', 'value'].forEach(a => {
            if (node.hasAttribute(a)) attrs.push(`${a}="${node.getAttribute(a)}"`);
        });
        if (node.classList) {
            // Strip layout/utility classes, keep semantic identifiers
            let cls = Array.from(node.classList).filter(c => c.startsWith('o_') || c === 'btn' || c.startsWith('btn-')).join(' ');
            if (cls) attrs.push(`class="${cls}"`);
        }
        let tag = node.tagName.toLowerCase();
        let content = childrenText.length > 80 ? childrenText.substring(0, 80) + '...' : childrenText;
        return `\n<${tag} ${attrs.join(' ')}>${content}</${tag}>`;
    }
    return childrenText;
}

console.error = function (...args) {
    originalConsoleError.apply(console, args);

    const msg = args.map(a => {
        if (typeof a === 'string') return a;
        if (a && a.message) return a.message;
        return '';
    }).join(' ');

    if (!window._domDumped && (msg.includes('TIMEOUT') || msg.includes('FAILED:') || msg.includes('FATAL:') || msg.includes('AssertionError'))) {
        window._domDumped = true;
        try {
            let rpcList = Array.from(window._pendingRPCs).join(', ') || 'None';
            let currentHash = document.location.hash || document.location.pathname;

            let stateHeader = `\n========== UI STATE SUMMARY ==========\nURL/Hash: ${currentHash}\nPending RPCs: ${rpcList}\n======================================\n`;
            let skeleton = buildInteractableSkeleton(document.body).replace(/\s{2,}/g, ' ');

            originalConsoleError.call(console, stateHeader + "\n========== INTERACTABLE DOM SKELETON ==========\n" + skeleton + "\n===============================================\n");
        } catch (e) {
            originalConsoleError.call(console, "Failed to dump DOM skeleton: " + e.toString());
        }
    }
};

// 3. Catch Unhandled Promise Rejections to prevent silent headless browser deadlocks
window.addEventListener('unhandledrejection', function(event) {
    let reason = event.reason ? (event.reason.stack || event.reason) : "Unknown Error";
    originalConsoleError.call(console, `\n========== UNHANDLED PROMISE REJECTION ==========\n${reason}\n=================================================\n`);
});

// 4. Detect illegal redirects to Discuss app (Odoo 19 fallback mechanism)
window._discussAlarmInterval = setInterval(() => {
    const url = document.location.pathname + document.location.hash + document.location.search;
    if (url.includes('/discuss')) {
        if (!window._discussAlarmTriggered) {
            window._discussAlarmTriggered = true;
            console.error("AssertionError: Tour illegally redirected to /odoo/discuss! This usually means the query parameter routing was malformed, hash routing was illegally used, or cids/menu_id were missing, causing Odoo to fallback to the default app.");
        }
    }
}, 1000);

// 5. Global Tour Watchdog (Hang Detector)
window._hamsTourWatchdog = {
    lastActivity: Date.now(),
    lastLog: "Initialized",
    hanging: false
};

const ogLog = console.log;
console.log = function(...args) {
    ogLog.apply(console, args);
    const msg = args.map(a => typeof a === 'string' ? a : (a && a.message ? a.message : '')).join(' ');
    // Intercept native Odoo tour progression logs
    if (msg.toLowerCase().includes('tour') || msg.toLowerCase().includes('step') || msg.toLowerCase().includes('trigger')) {
        window._hamsTourWatchdog.lastActivity = Date.now();
        window._hamsTourWatchdog.lastLog = msg;
        window._hamsTourWatchdog.hanging = false;

        let hangOverlay = document.getElementById('tour_hang_overlay');
        if (hangOverlay) hangOverlay.remove();
    }
};

window._hamsTourWatchdogInterval = setInterval(() => {
    const idleTime = Date.now() - window._hamsTourWatchdog.lastActivity;
    // Trigger alarm if the tour pipeline goes completely silent for 6 seconds
    if (idleTime > 6000 && !window._hamsTourWatchdog.hanging) {
        window._hamsTourWatchdog.hanging = true;
        clearInterval(window._hamsTourWatchdogInterval);
        if (window._discussAlarmInterval) clearInterval(window._discussAlarmInterval);

        const alarmMsg = `[WATCHDOG ALARM] Tour idle for ${Math.floor(idleTime/1000)}s! Last activity: ${window._hamsTourWatchdog.lastLog}`;

        originalConsoleError.call(console, alarmMsg);
        ogLog.call(console, alarmMsg);

        let overlay = document.getElementById('tour_hang_overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'tour_hang_overlay';
            overlay.style = 'position:fixed; top:10px; left:50%; transform:translateX(-50%); z-index:999999; background:rgba(255,165,0,0.9); color:black; padding:15px; font-weight:bold; font-size:16px; border:2px solid red; pointer-events:none; font-family:sans-serif; text-align:center;';
            document.body.appendChild(overlay);
        }
        overlay.textContent = alarmMsg;

        // Force the DOM skeleton dump so Python test runner captures the frozen state
        if (!window._domDumped) {
            let currentHash = document.location.hash || document.location.pathname;
            let rpcList = Array.from(window._pendingRPCs).join(', ') || 'None';
            let stateHeader = `\n========== UI STATE SUMMARY (HANG DETECTED) ==========\nURL/Hash: ${currentHash}\nPending RPCs: ${rpcList}\n======================================================\n`;
            let skeleton = buildInteractableSkeleton(document.body).replace(/\s{2,}/g, ' ');
            originalConsoleError.call(console, stateHeader + "\n========== INTERACTABLE DOM SKELETON ==========\n" + skeleton + "\n===============================================\n");
        }
    }
}, 2000);
