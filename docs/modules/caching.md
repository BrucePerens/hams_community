# ⚡ Caching Module (`caching`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Implements a global, root-scoped Service Worker (`/sw.js`) that proxies and caches frontend assets locally in the browser to provide near-instant load times.

## 2. Integration Rules
* Assets placed in your module's `static/` directory are cached automatically.
* **No Competing Workers:** DO NOT attempt to register another Service Worker.
* **WebSockets:** `ws://` protocols are hardcoded to bypass the proxy.
* **Dynamic Large File Prohibition:** The worker mathematically calculates an active quota limit (approx 35MB). Heavy media MUST route via `/web/image` to prevent the cache from ejecting critical UI bundles.

## 3. Semantic Anchors
* `[@ANCHOR: xpath_rendering_caching_layout]`.
