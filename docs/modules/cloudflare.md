# ☁️ Cloudflare Edge Orchestration (`cloudflare`)

**Context:** Technical documentation strictly for LLMs and Integrators developing proprietary (`hams_private`) modules.

This generalized module acts as the control plane for the CDN edge. It automatically applies aggressive caching headers to public routes and manages an asynchronous queue for targeted cache invalidation.

---

## 1. 📡 Edge Caching Rules (The Middleware)
The module intercepts all outgoing HTTP responses via `ir.http._post_dispatch`. Private modules do **not** need to manually define caching headers. The middleware applies the following generalized ruleset:

* **Static Assets:** Paths containing `/static/` receive `max-age=31536000` (1 Year).
* **Private / API Routes:** Paths starting with `/my/`, `/web/`, or `/api/` receive `no-cache, no-store`.
* **Authenticated Users:** If `request.env.user._is_public()` evaluates to `False`, the response receives `no-cache, no-store` to prevent caching personal dashboards or PII.
* **Public Content:** All other responses (e.g., standard website pages, blogs, custom public CMS routes) receive `max-age=86400` (24 Hours).

---

## 2. 🧹 Cache Invalidation (Purging)
When an internal user edits a cached record (like a blog post or a proprietary `ham.private.article`), the old version will remain cached at the edge for 24 hours. You MUST invalidate the URL. 

Because Cloudflare API limits are strict, **direct API calls are forbidden**. You must push the URLs into the `cloudflare.purge.queue`.

### Integrating Proprietary Models (`hams_private`)
To invalidate cache when your private module's data changes, override `write` and `unlink`. You **MUST** use the Service Account to securely interact with the queue, ensuring unprivileged users don't trigger AccessErrors.

```python
class ProprietaryArticle(models.Model):
    _name = 'ham.private.article'
    _inherit = ['mail.thread']
    
    website_url = fields.Char(string="URL")

    def write(self, vals):
        # 1. Capture the URLs BEFORE the change if needed, or mapped current URLs
        urls_to_purge = self.mapped('website_url')
        
        # 2. Execute standard write
        res = super().write(vals)
        
        # 3. Enqueue URLs safely using the generic Cloudflare Service Account
        if urls_to_purge and 'cloudflare.purge.queue' in self.env:
            queue_env = self.env['cloudflare.purge.queue']
            svc_uid = queue_env._get_cf_service_uid()
            queue_env.with_user(svc_uid).enqueue_urls(urls_to_purge)
            
        return res
```

---

## 3. 🛡️ WAF (Web Application Firewall) Management
The module utilizes the `deploy_waf_rules()` utility to push Bot Management rules to Cloudflare. This is executed automatically on installation, but can be manually triggered by system administrators via the Odoo General Settings interface. Private modules generating new API endpoints are automatically protected if they reside under `/api/v1/`.
