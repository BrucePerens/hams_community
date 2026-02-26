# Caching Module (caching)

## Overview
This module implements a global, root-scoped Service Worker (`/sw.js`) that proxies and caches frontend assets across the entire Odoo instance. It acts as a client-side CDN, resulting in near-instant load times for returning visitors.

## Agent Integration Instructions (Zero-Config)
If you are an AI agent or developer building another module, **you do not need to write any integration code for this module.**

To ensure your module's assets are cached, you must strictly follow these rules:

1.  **Path Compliance:** The Service Worker automatically intercepts and caches HTTP GET requests matching the following paths:
    * `/web/assets/...`: Odoo's compiled and hashed asset bundles.
    * `/web/static/...`: Odoo's core static files and generic media.
    * `/<your_module_name>/static/...`: Any static file served directly from your custom module's directory (e.g., `/user_websites/static/src/js/widget.js`).
    As long as you place your frontend assets inside your module's standard `static/` directory, they will be cached automatically.
2.  **No Competing Workers:** DO NOT attempt to register another Service Worker in your module. A domain can only be cleanly controlled by one root Service Worker.
3.  **WebSocket Safety:** The Service Worker is hardcoded to ignore `ws://` and `wss://` protocols. You may safely open WebSockets (e.g., for the DX Cluster) without fear of proxy interception or caching failures.
4.  **Dynamic Data:** Do not put dynamic, user-specific data into static JS files. Static files are aggressively cached. Pass dynamic data to your static JS via HTML `data-*` attributes or standard Odoo RPC calls.
