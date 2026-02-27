# ☁️ Cloudflare Edge Orchestration (`cloudflare`)

**Context:** Technical documentation strictly for LLMs and Integrators developing proprietary (`hams_private`) modules.
This generalized module acts as the control plane for the CDN edge.
It automatically applies aggressive caching headers, manages WAF bans, handles Turnstile CAPTCHA verification, orchestrates Zero Trust Tunnels, and provides context on edge requests.

---

**1. 🛡️ Advanced API Interfaces**

Proprietary modules MUST utilize the following AbstractModel APIs to interact with the edge layer securely:

### A. WAF IP Banning API
Instantly block or challenge malicious traffic at the Cloudflare Edge before it reaches Nginx.
* **Signature:** `env['cloudflare.waf'].ban_ip(ip_address, mode='block', duration=3600)`
* **Modes:** `'block'`, `'challenge'`, `'managed_challenge'`.
* **Use Case:** To be used by silent honeypots (e.g., `ham_events` issue reporting) to drop scrapers.

### B. Cache-Tag Purging API
Purge relational models globally across all paginated views without calculating exact URLs.
* **Signature:** `env['cloudflare.purge.queue'].enqueue_tags(tags_list)`
* **Example:** `env['cloudflare.purge.queue'].enqueue_tags(['user_k6bp', 'classifieds_index'])`
* **Use Case:** Called by `ham_logbook` or `ham_classifieds` when a user's global profile state changes.

### C. Turnstile Verification API
Validate modern, invisible CAPTCHA tokens for unauthenticated public forms.
* **Signature:** `env['cloudflare.turnstile'].verify_token(token, remote_ip=None)`
* **Returns:** `True` if the token is valid, `False` otherwise.
* **Use Case:** Used by custom `POST` controllers to replace Google reCAPTCHA dependencies.

### D. Edge Context Parsing API
Retrieve geographic and threat data injected by the Cloudflare edge proxy.
* **Signature:** `env['cloudflare.utils'].get_request_context()`
* **Returns:** A dictionary containing: `{'ip': str, 'country': str, 'city': str, 'longitude': str, 'latitude': str, 'threat_score': str}`.
* **Use Case:** Used by `ham_propagation` and `ham_satellite` to instantly default unauthenticated map viewers to their physical region.

### E. Zero Trust Tunnels (cloudflared)
The module allows administrators to provision a new Cloudflare Tunnel directly from the settings UI.
It requires the `cloudflare_account_id` (tunnels are account-level, not zone-level). When triggered, it generates a random secret, creates the tunnel on the edge, and returns the `cloudflared service install <TOKEN>` command via a pop-up wizard.

---

**2. 📡 Automated Edge Caching (The Middleware)**
The module intercepts all outgoing HTTP responses via `ir.http._post_dispatch` to apply caching rules based on the user's authentication state:
* **Static Assets:** `max-age=31536000` (1 Year).
Also seamlessly injects `Cache-Tag: odoo-static-assets`.
* **Private / Authenticated:** `no-cache, no-store` (If `request.env.user._is_public()` is False).
* **Public Content:** `max-age=86400` (24 Hours).

**3. 🧹 Cache Invalidation**

**Automated Static Asset Purging:**
The module automatically hooks into the Odoo boot sequence (`_register_hook`).
It scans the `static/` folders of all installed modules. If a file modification is detected, it automatically enqueues the `odoo-static-assets` Cache-Tag to the Cloudflare API, perfectly synchronizing the CDN edge with the local filesystem without manual intervention.

**Manual URL Purging:**
For standard URLs, push updates to the asynchronous queue using the generic Service Account:
```python
queue_env = self.env['cloudflare.purge.queue']
svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
queue_env.with_user(svc_uid).enqueue_urls(['/my-custom-url'])
```

---

## 4. 🔗 Semantic Anchors
* `[%ANCHOR: cf_execute_ban]` / `[%ANCHOR: test_cf_execute_ban]`: WAF IP Ban execution.
* `[%ANCHOR: cf_action_lift_ban]` / `[%ANCHOR: test_cf_action_lift_ban]`: Lifting WAF IP Bans.
* `[%ANCHOR: cf_tunnel_setup]`: Generating Tunnel Commands.
* `[%ANCHOR: enqueue_urls_base_url]` / `[%ANCHOR: test_purge_queue_base_url_sudo]`: URL queueing validation.
* `[%ANCHOR: ir_cron_process_cf_purge_queue]` / `[%ANCHOR: test_queue_batching_and_rate_limiting]`: Queue batching limits.
* `[%ANCHOR: xpath_rendering_cf_settings]` / `[%ANCHOR: test_xpath_rendering_cf_settings]`: UI Configuration settings rendering.
* `[%ANCHOR: cf_ip_ban_ui]` / `[%ANCHOR: test_tour_cf_ip_ban]`: IP Ban User Interface tour.
* `[%ANCHOR: cf_waf_rule_ui]` / `[%ANCHOR: test_tour_cf_waf_rule]`: WAF Rule User Interface tour.
