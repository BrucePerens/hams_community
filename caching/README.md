# Caching PWA & Service Worker (`caching`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This module speeds up the Odoo frontend by acting as a client-side CDN. It installs a global Service Worker that runs in the background of the user's browser.

When a user loads a page, the Service Worker intercepts the requests for Odoo's JavaScript, CSS, and static module files. If the browser already has a copy of the file, it loads it instantly from the hard drive (0ms latency) without ever talking to the network.

## 🪄 How It Works (Zero-Config)

You do not need to do anything special to make your custom modules work with this cache. 

The Service Worker automatically looks for requests matching these patterns:
* `/web/assets/...` (Odoo's compiled JS/CSS bundles)
* `/web/static/...` (Core Odoo static files)
* `/<your_module_name>/static/...` (Your custom module's frontend assets)

As long as you place your Javascript, CSS, and UI icons inside your module's standard `static/` directory, they will be cached automatically.

## 🔄 Automated Cache Invalidation

You do not need to manually bump version numbers or write complex QWeb query parameters to bust the cache when you update your static files (like logos, CSS, or JS). 

When the Odoo server boots up, this module automatically scans the `static/` directories of all installed modules to find the most recent file modification timestamp (`mtime`). 

It dynamically injects this timestamp into the `/sw.js` payload. If you modify a file and restart the Odoo server, the Service Worker's script signature changes. The next time a user visits the site, their browser will instantly detect the new Service Worker, install it, and purge the entire stale cache automatically.

## 🚨 The File-Size Caveat & Safety Valve

Browsers give Service Workers a strict storage limit. If a Service Worker tries to cache massive files, it will max out the quota and the browser will panic and delete the entire cache—destroying the performance benefits of this module.

**The Dynamic Safety Valve:** To protect against this, our Service Worker runs a mathematical calculation on the server during boot. It sums up the sizes of all static files across all installed modules. If the total size exceeds the safe limits of the browser's cache quota (~35MB), it automatically calculates a dynamic max file size limit. It instructs the browser to cache as many small files as possible while intentionally rejecting the largest, heaviest files, keeping the total cache footprint safely underneath the browser's panic threshold.

**The Golden Rule:** 

Keep your `static/` folders strictly reserved for lightweight UI code (JS, CSS) and small layout graphics. If you need to serve heavy media, user uploads, or large datasets, use Odoo's standard attachment routes (`/web/image` or `/web/content`). The Service Worker explicitly ignores those routes, allowing Cloudflare to handle the heavy lifting safely.
