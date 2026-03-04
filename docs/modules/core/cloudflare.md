# ☁️ Cloudflare Edge Orchestration (`cloudflare`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Control plane for the CDN edge. Manages Cache-Tags, WAF bans, and Turnstile CAPTCHA verification to offload CPU from the Python WSGI workers.

## 2. API Interfaces
* **WAF IP Banning:** `env['cloudflare.waf'].ban_ip(...)`
* **Cache Purging:** `env['cloudflare.purge.queue'].enqueue_tags(...)`
* **Turnstile API:** `env['cloudflare.turnstile'].verify_token(...)`
* **Edge Context:** `env['cloudflare.utils'].get_request_context()` (Extracts IP/Geodata).

## 3. Automated Subsystems
* Injects `Cloudflare-CDN-Cache-Control` headers natively via `ir.http._post_dispatch`.
* Scans module `static/` folders on boot and automatically invalidates the CDN edge via cache tags if file modifications are detected.
