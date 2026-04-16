# ☁️ Cloudflare Edge Orchestration (`cloudflare`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

## 1. Overview
Control plane for the CDN edge. Manages Cache-Tags, WAF bans, and Turnstile CAPTCHA verification to offload CPU from the Python WSGI workers.

## 2. API Interfaces
* **WAF IP Banning:** `env['cloudflare.waf'].ban_ip(...)` dynamically injects firewall rules `[@ANCHOR: cf_execute_ban]`. Automatically lifts expired bans via `[@ANCHOR: cf_action_lift_ban]`.
* **Cache Purging:** `env['cloudflare.purge.queue'].enqueue_tags(...)`. Processes asynchronous cache invalidation queues via cron `[@ANCHOR: ir_cron_process_cf_purge_queue]`. Base URLs are accurately resolved and injected via `[@ANCHOR: enqueue_urls_base_url]`.
* **Turnstile API:** `env['cloudflare.turnstile'].verify_token(...)` securely evaluates CAPTCHA handshakes against the API.
* **Edge Context:** `env['cloudflare.utils'].get_request_context()` (Extracts trusted IP/Geodata).
* **Tunnel Setup:** Wizard dynamically generates the `cloudflared` execution token command for edge network bridging `[@ANCHOR: cf_tunnel_setup]`.

## 3. Automated Subsystems
* Injects `Cloudflare-CDN-Cache-Control` headers natively via `ir.http._post_dispatch`.
* Scans module `static/` folders on boot and automatically invalidates the CDN edge via cache tags if file modifications are detected.
* **Settings View Injection:** Extends standard Odoo config settings to securely accept Cloudflare API tokens `[@ANCHOR: xpath_rendering_cf_settings]`.
