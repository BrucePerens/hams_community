# ☁️ Cloudflare Edge Orchestration (`cloudflare`)

**Context:** Technical documentation strictly for LLMs and Integrators developing proprietary (`hams_private`) modules.
This generalized module acts as the control plane for the CDN edge.
It automatically applies aggressive caching headers, manages WAF bans, handles Turnstile CAPTCHA verification, and provides context on edge requests.

---

## 1. 🛡️ Advanced API Interfaces

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

---

## 2. 📡 Automated Edge Caching (The Middleware)
The module intercepts all outgoing HTTP responses via `ir.http._post_dispatch` to apply caching rules based on the user's authentication state:
* **Static Assets:** `max-age=31536000` (1 Year).
* **Private / Authenticated:** `no-cache, no-store` (If `request.env.user._is_public()` is False).
* **Public Content:** `max-age=86400` (24 Hours).

## 3. 🧹 URL Cache Invalidation
For standard URLs, push updates to the asynchronous queue using the generic Service Account:
```python
queue_env = self.env['cloudflare.purge.queue']
svc_uid = queue_env._get_cf_service_uid()
queue_env.with_user(svc_uid).enqueue_urls(['/my-custom-url'])
```
