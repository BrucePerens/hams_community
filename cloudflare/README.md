# Cloudflare Edge Orchestration (`cloudflare`)

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This module acts as the command center for your Cloudflare CDN and Web Application Firewall (WAF). It sits quietly in the background and automatically manages edge caching, security, and IP bans so you don't have to constantly log into the Cloudflare dashboard.

## 🌟 What It Does

* **Automated Static Caching & Purging:** It forces Cloudflare to aggressively cache static assets (like images, CSS, and JS) for a full year. If you update a file and restart the server, the module detects the new file timestamp during boot and automatically tells Cloudflare to purge the stale assets globally.
* **WAF Management:** You can build, backup, and deploy Cloudflare Firewall rules directly from the Odoo backend.
* **Honeypot IP Banning:** If a malicious bot triggers a silent honeypot trap on your site, this module instantly talks to Cloudflare%2s API and bans their IP address at the network edge.
* **Zero Trust Tunnels:** You can provision a new `cloudflared` tunnel directly from the settings menu. The module generates the tunnel via API and gives you the exact copy-paste command to run on your server.
* **Turnstile Integration:** It provides a backend validator for Cloudflare's invisible Turnstile CAPTCHA to protect your public forms.

## 🛠️ How to Set It Up

1. Drop the `cloudflare` folder into your Odoo `addons` directory.
2. Add your credentials to your server's `.env` file (or set them in the Odoo UI under **Settings > Cloudflare Edge**):
   * `CLOUDFLARE_API_TOKEN` (Requires `Zone.Cache Purge`, `Zone.Firewall Services`, and `Account.Cloudflare Tunnel` permissions)
   * `CLOUDFLARE_ZONE_ID`
   * `CLOUDFLARE_ACCOUNT_ID` (Only needed if using Zero Trust Tunnels)
3. Install the module. It will automatically apply the baseline security rules.
