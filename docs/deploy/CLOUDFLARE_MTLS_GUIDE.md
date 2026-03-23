# Cloudflare mTLS Split-DNS Configuration Guide

**The Challenge:** Cloudflare's free and standard tiers do not support Mutual TLS (mTLS) "Bring Your Own CA" to validate LoTW certificates at the edge.
**The Solution:** Hams.com utilizes a "Split-DNS" architecture. It creates a seamless, stateless HMAC token bridge between a direct, unproxied authentication subdomain (`auth.hams.com`) and your Cloudflare-protected main domain (`hams.com`).
This allows you to use standard Cloudflare plans while still providing users with "Zero-Touch" LoTW authentication.

---

## Phase 1: DNS Configuration

In your Cloudflare Dashboard, configure your DNS records as follows:

1.  **`hams.com` (A/CNAME):** Point to your server IP. **Proxy status:** 🟧 Proxied (Orange Cloud).
2.  **`www.hams.com` (CNAME):** Point to `hams.com`. **Proxy status:** 🟧 Proxied (Orange Cloud).
3.  **`auth.hams.com` (A/CNAME):** Point to your server IP. **Proxy status:** ☁️ DNS Only (Grey Cloud).

---

## Phase 2: Nginx Infrastructure

The provided `deploy/nginx_hams.conf` is already pre-configured to handle this split architecture natively.

1.  It catches all traffic to `auth.hams.com` and strictly requires the `ssl_client_certificate` (`lotw_root.pem`).
2.  It catches all standard traffic on `hams.com` and passes it cleanly without prompting for a certificate.

---

## How the Transparent Hop Works

When a user clicks "Login with LoTW" on the main site:
1.  The UI dynamically routes them to `https://auth.hams.com/onboarding/lotw_verify`.
2.  Because `auth.` is Grey Clouded, the user's browser connects directly to your Nginx server, bypassing Cloudflare entirely.
3.  Nginx executes the mTLS handshake, validates the ARRL certificate, and passes the callsign to Odoo.
4.  Odoo (running behind `auth.hams.com`) generates a 30-second, stateless HMAC-SHA256 token containing the callsign.
5.  Odoo instantly redirects the user back to `https://hams.com/onboarding/lotw_consume?token=XYZ`.
6.  The main domain consumes the token, mathematically proves its authenticity, logs the user into the main Cloudflare-proxied session, and redirects them to their dashboard.

This entire process happens in roughly 300 milliseconds, completely transparent to the end-user.
