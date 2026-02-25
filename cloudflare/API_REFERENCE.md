# Cloudflare Edge Orchestration (`cloudflare`) - API Reference

## Purpose
Acts as the control plane for the Cloudflare CDN edge. It automatically applies caching headers to outgoing HTTP responses, manages Web Application Firewall (WAF) rules, verifies invisible CAPTCHA tokens, and provides asynchronous cache invalidation.

## Python API

### `cloudflare.purge.queue`
Manages the asynchronous queue for invalidating edge cache.

#### `enqueue_urls(urls)`
Adds specific relative URLs to the purge queue.
* **Arguments:** `urls` (list of str): e.g., `['/my-page/home', '/about']`
* **Usage:**
  ```python
  svc_uid = self.env['zero_sudo.security.utils']._get_service_uid('cloudflare.user_cloudflare_service')
  self.env['cloudflare.purge.queue'].with_user(svc_uid).enqueue_urls(['/route'])
  ```

#### `enqueue_tags(tags)`
Adds Cloudflare Cache-Tags to the purge queue for global relational purging.
* **Arguments:** `tags` (list of str): e.g., `['user_profile_123']`

### `cloudflare.waf`

#### `ban_ip(ip_address, mode='block', duration=3600, notes="Honeypot Triggered")`
Instantly instructs the Cloudflare WAF to block or challenge an IP address, AND logs the ban locally in the `cloudflare.ip.ban` model where administrators can review or lift it via the Odoo UI.
* **Arguments:**
  * `ip_address` (str): The target IP.
  * `mode` (str): `'block'`, `'challenge'`, or `'managed_challenge'`.
  * `notes` (str): Explain exactly why this was triggered (e.g., `'Classifieds Contact Honeypot'`).
* **Usage:** (Note: You do not need to use `sudo` or Service Accounts manually. The module escalates internally to allow unauthenticated public guests to trigger the honeypot safely).
  ```python
  self.env['cloudflare.waf'].ban_ip(request.httprequest.remote_addr, notes="Spam form submitted.")
  ```

### `cloudflare.turnstile`

#### `verify_token(token, remote_ip=None)`
Verifies a Cloudflare Turnstile CAPTCHA response token against the Cloudflare verification API.
* **Returns:** `True` if valid, `False` otherwise.

### `cloudflare.utils`

#### `get_request_context()`
Parses edge-injected headers (like IP, Country, City, Lat/Lon) from the current HTTP request.
* **Returns:** `dict` containing geographic and threat data.
